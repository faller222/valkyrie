#!/usr/bin/env python3
"""Valkyrie persistence helper.

Single source of truth for the Valkyrie skill set: a SQLite database that lets the
coach remember the user across conversations. All three skills (valkyrie-onboard,
valkyrie-followup, valkyrie-analysis) read and write through this script.

The database path comes from the VALKYRIE_DB environment variable, falling back to
./valkyrie.db in the current working directory. The host application is responsible
for placing this file in a stable, writable, per-user location.

Usage (run from a shell, parse the JSON it prints to stdout):

  python db.py init
      Create the database and schema if they do not exist (idempotent).

  python db.py profile-exists [--user 1]
      Print {"exists": true|false}. Use this to route a new message to
      valkyrie-onboard (false) or valkyrie-followup (true).

  python db.py context [--user 1]
      Print a compact JSON snapshot the coach needs before replying: profile,
      current_state, today's planned session, active health events, next checkpoint,
      and recent logs.

  python db.py query --sql "SELECT ..." [--params '["a", 1]']
      Run a read-only SELECT and print rows as a JSON array of objects.

  python db.py exec --sql "INSERT ..." [--params '["a", 1]']
      Run a write statement. Prints {"rowcount": N, "lastrowid": M}. After any write
      to a stateful table, call refresh-state to keep current_state accurate.

  python db.py refresh-state [--user 1]
      Recompute and store the current_state snapshot for the user.

Design notes:
- Original user phrasing is always stored in raw_text columns; normalized/enum
  fields are for analysis. Natural language is the interface.
- One database per end user is the typical deployment; user_id defaults to 1.
- Substance/anabolic data lives in `supplements` with is_private=1 and must never be
  surfaced in shareable output.
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

DEFAULT_USER_ID = 1


def db_path() -> str:
    return os.environ.get("VALKYRIE_DB", os.path.join(os.getcwd(), "valkyrie.db"))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,
    created_at  TEXT NOT NULL,
    language    TEXT,
    timezone    TEXT
);

CREATE TABLE IF NOT EXISTS profile (
    user_id             INTEGER PRIMARY KEY REFERENCES users(id),
    name                TEXT,
    coach_tone          TEXT,
    age                 INTEGER,
    sex                 TEXT,
    height_cm           REAL,
    start_weight_kg     REAL,
    body_composition    TEXT,
    activity_level      TEXT,
    job_type            TEXT,
    primary_goal        TEXT,
    secondary_goal      TEXT,
    motivation          TEXT,
    neurotype           TEXT,
    neurotype_notes     TEXT,
    technical_level     TEXT,
    days_per_week       INTEGER,
    minutes_per_session INTEGER,
    equipment           TEXT,
    training_preference TEXT,
    diet_type           TEXT,
    diet_restrictions   TEXT,
    fasting             TEXT,
    food_preferences    TEXT,
    enhanced            INTEGER DEFAULT 0,
    updated_at          TEXT
);

CREATE TABLE IF NOT EXISTS supplements (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    name       TEXT NOT NULL,
    dose       TEXT,
    is_private INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plan (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    name       TEXT,
    start_date TEXT,
    end_date   TEXT,
    split      TEXT,
    notes      TEXT,
    is_active  INTEGER DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plan_days (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id        INTEGER NOT NULL REFERENCES plan(id),
    weekday        INTEGER NOT NULL,
    focus          TEXT,
    exercises_json TEXT
);

CREATE TABLE IF NOT EXISTS workouts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    date        TEXT NOT NULL,
    plan_day_id INTEGER REFERENCES plan_days(id),
    status      TEXT,
    stop_reason TEXT,
    raw_text    TEXT,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS workout_sets (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL REFERENCES workouts(id),
    exercise   TEXT,
    raw_name   TEXT,
    set_index  INTEGER,
    reps       INTEGER,
    load_kg    REAL,
    tempo      TEXT,
    note       TEXT
);

CREATE TABLE IF NOT EXISTS nutrition_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    date        TEXT NOT NULL,
    meal        TEXT,
    description TEXT,
    raw_text    TEXT,
    quality     TEXT,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weight_logs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    date       TEXT NOT NULL,
    weight_kg  REAL NOT NULL,
    raw_text   TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS health_events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id),
    date       TEXT NOT NULL,
    type       TEXT,
    body_part  TEXT,
    severity   TEXT,
    status     TEXT,
    raw_text   TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS checkpoints (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL REFERENCES users(id),
    scheduled_date TEXT,
    type           TEXT,
    metrics_json   TEXT,
    status         TEXT DEFAULT 'SCHEDULED',
    results_json   TEXT,
    created_at     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS analysis_reports (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id),
    period_start  TEXT,
    period_end    TEXT,
    kind          TEXT,
    adherence_pct REAL,
    summary       TEXT,
    metrics_json  TEXT,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS current_state (
    user_id                 INTEGER PRIMARY KEY REFERENCES users(id),
    current_weight_kg       REAL,
    current_phase           TEXT,
    current_health          TEXT,
    current_equipment       TEXT,
    adherence_last_30_days  REAL,
    last_workout_date       TEXT,
    next_checkpoint_date    TEXT,
    updated_at              TEXT
);

CREATE INDEX IF NOT EXISTS idx_workouts_user_date ON workouts(user_id, date);
CREATE INDEX IF NOT EXISTS idx_nutrition_user_date ON nutrition_logs(user_id, date);
CREATE INDEX IF NOT EXISTS idx_weight_user_date ON weight_logs(user_id, date);
CREATE INDEX IF NOT EXISTS idx_health_user_date ON health_events(user_id, date);
"""


def cmd_init(args) -> dict:
    conn = connect()
    try:
        conn.executescript(SCHEMA)
        cur = conn.execute("SELECT id FROM users WHERE id = ?", (DEFAULT_USER_ID,))
        if cur.fetchone() is None:
            conn.execute(
                "INSERT INTO users (id, created_at) VALUES (?, ?)",
                (DEFAULT_USER_ID, now_iso()),
            )
        conn.commit()
        return {"ok": True, "db": db_path()}
    finally:
        conn.close()


def cmd_profile_exists(args) -> dict:
    conn = connect()
    try:
        cur = conn.execute(
            "SELECT name FROM profile WHERE user_id = ? AND name IS NOT NULL",
            (args.user,),
        )
        row = cur.fetchone()
        return {"exists": row is not None}
    finally:
        conn.close()


def _params(args):
    if not args.params:
        return []
    return json.loads(args.params)


def cmd_query(args) -> object:
    conn = connect()
    try:
        cur = conn.execute(args.sql, _params(args))
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def cmd_exec(args) -> dict:
    conn = connect()
    try:
        cur = conn.execute(args.sql, _params(args))
        conn.commit()
        return {"rowcount": cur.rowcount, "lastrowid": cur.lastrowid}
    finally:
        conn.close()


def _scalar(conn, sql, params=()):
    cur = conn.execute(sql, params)
    row = cur.fetchone()
    if row is None:
        return None
    return row[0]


def _compute_adherence(conn, user_id, days=30) -> float | None:
    """Done vs planned workouts over the trailing window.

    Planned count is approximated from the active plan's training days per week
    scaled to the window; done count is logged non-skipped workouts in the window.
    """
    since = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    done = _scalar(
        conn,
        "SELECT COUNT(*) FROM workouts WHERE user_id = ? AND date >= ? "
        "AND status != 'SKIPPED'",
        (user_id, since),
    ) or 0
    training_days = _scalar(
        conn,
        "SELECT COUNT(*) FROM plan_days pd JOIN plan p ON p.id = pd.plan_id "
        "WHERE p.user_id = ? AND p.is_active = 1 AND pd.focus IS NOT NULL "
        "AND UPPER(pd.focus) != 'REST'",
        (user_id,),
    ) or 0
    if training_days == 0:
        return None
    planned = training_days * (days / 7.0)
    if planned <= 0:
        return None
    return round(min(done / planned, 1.0) * 100.0, 1)


def cmd_refresh_state(args) -> dict:
    user_id = args.user
    conn = connect()
    try:
        weight = _scalar(
            conn,
            "SELECT weight_kg FROM weight_logs WHERE user_id = ? "
            "ORDER BY date DESC, id DESC LIMIT 1",
            (user_id,),
        )
        phase = _scalar(
            conn,
            "SELECT name FROM plan WHERE user_id = ? AND is_active = 1 "
            "ORDER BY id DESC LIMIT 1",
            (user_id,),
        )
        health_row = conn.execute(
            "SELECT type, body_part, severity FROM health_events "
            "WHERE user_id = ? AND status = 'ACTIVE' ORDER BY date DESC, id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        if health_row is None:
            health = "OK"
        else:
            parts = [health_row["type"]]
            if health_row["body_part"]:
                parts.append(health_row["body_part"])
            if health_row["severity"]:
                parts.append(health_row["severity"])
            health = " ".join(p for p in parts if p)
        equipment = _scalar(
            conn, "SELECT equipment FROM profile WHERE user_id = ?", (user_id,)
        )
        last_workout = _scalar(
            conn,
            "SELECT date FROM workouts WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 1",
            (user_id,),
        )
        next_checkpoint = _scalar(
            conn,
            "SELECT scheduled_date FROM checkpoints WHERE user_id = ? "
            "AND status = 'SCHEDULED' AND scheduled_date >= ? "
            "ORDER BY scheduled_date ASC LIMIT 1",
            (user_id, datetime.now(timezone.utc).date().isoformat()),
        )
        adherence = _compute_adherence(conn, user_id)

        conn.execute(
            """
            INSERT INTO current_state (
                user_id, current_weight_kg, current_phase, current_health,
                current_equipment, adherence_last_30_days, last_workout_date,
                next_checkpoint_date, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                current_weight_kg = excluded.current_weight_kg,
                current_phase = excluded.current_phase,
                current_health = excluded.current_health,
                current_equipment = excluded.current_equipment,
                adherence_last_30_days = excluded.adherence_last_30_days,
                last_workout_date = excluded.last_workout_date,
                next_checkpoint_date = excluded.next_checkpoint_date,
                updated_at = excluded.updated_at
            """,
            (
                user_id, weight, phase, health, equipment, adherence,
                last_workout, next_checkpoint, now_iso(),
            ),
        )
        conn.commit()
        return {
            "user_id": user_id,
            "current_weight_kg": weight,
            "current_phase": phase,
            "current_health": health,
            "current_equipment": equipment,
            "adherence_last_30_days": adherence,
            "last_workout_date": last_workout,
            "next_checkpoint_date": next_checkpoint,
        }
    finally:
        conn.close()


def cmd_context(args) -> dict:
    user_id = args.user
    conn = connect()
    try:
        def rows(sql, params):
            return [dict(r) for r in conn.execute(sql, params).fetchall()]

        def one(sql, params):
            r = conn.execute(sql, params).fetchone()
            return dict(r) if r else None

        today = datetime.now(timezone.utc).date()
        weekday = today.weekday()  # 0 = Monday

        profile = one("SELECT * FROM profile WHERE user_id = ?", (user_id,))
        user = one("SELECT * FROM users WHERE id = ?", (user_id,))
        state = one("SELECT * FROM current_state WHERE user_id = ?", (user_id,))

        todays_session = one(
            "SELECT pd.* FROM plan_days pd JOIN plan p ON p.id = pd.plan_id "
            "WHERE p.user_id = ? AND p.is_active = 1 AND pd.weekday = ? LIMIT 1",
            (user_id, weekday),
        )
        active_health = rows(
            "SELECT * FROM health_events WHERE user_id = ? AND status IN ('ACTIVE','RECOVERING') "
            "ORDER BY date DESC",
            (user_id,),
        )
        next_checkpoint = one(
            "SELECT * FROM checkpoints WHERE user_id = ? AND status = 'SCHEDULED' "
            "AND scheduled_date >= ? ORDER BY scheduled_date ASC LIMIT 1",
            (user_id, today.isoformat()),
        )
        recent_workouts = rows(
            "SELECT * FROM workouts WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 5",
            (user_id,),
        )
        recent_nutrition = rows(
            "SELECT * FROM nutrition_logs WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 5",
            (user_id,),
        )
        recent_weight = rows(
            "SELECT * FROM weight_logs WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 5",
            (user_id,),
        )

        return {
            "today": today.isoformat(),
            "weekday": weekday,
            "user": user,
            "profile": profile,
            "current_state": state,
            "todays_session": todays_session,
            "active_health": active_health,
            "next_checkpoint": next_checkpoint,
            "recent_workouts": recent_workouts,
            "recent_nutrition": recent_nutrition,
            "recent_weight": recent_weight,
        }
    finally:
        conn.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Valkyrie SQLite persistence helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create database and schema (idempotent)")
    p_init.set_defaults(func=cmd_init)

    p_exists = sub.add_parser("profile-exists", help="Whether an onboarded profile exists")
    p_exists.add_argument("--user", type=int, default=DEFAULT_USER_ID)
    p_exists.set_defaults(func=cmd_profile_exists)

    p_ctx = sub.add_parser("context", help="Compact JSON snapshot for the coach")
    p_ctx.add_argument("--user", type=int, default=DEFAULT_USER_ID)
    p_ctx.set_defaults(func=cmd_context)

    p_query = sub.add_parser("query", help="Run a read-only SELECT, print JSON rows")
    p_query.add_argument("--sql", required=True)
    p_query.add_argument("--params", default=None, help="JSON array of bound params")
    p_query.set_defaults(func=cmd_query)

    p_exec = sub.add_parser("exec", help="Run a write statement")
    p_exec.add_argument("--sql", required=True)
    p_exec.add_argument("--params", default=None, help="JSON array of bound params")
    p_exec.set_defaults(func=cmd_exec)

    p_state = sub.add_parser("refresh-state", help="Recompute current_state snapshot")
    p_state.add_argument("--user", type=int, default=DEFAULT_USER_ID)
    p_state.set_defaults(func=cmd_refresh_state)

    args = parser.parse_args(argv)
    result = args.func(args)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, default=str)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
