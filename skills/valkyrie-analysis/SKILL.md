---
name: valkyrie-analysis
description: Produces a periodic Valkyrie progress and adherence report for an onboarded fitness coaching user. Use this when the user asks for their weekly or monthly review, progress report, or "how am I doing"; when a scheduled job (cron) triggers a review; or as the first message of a new week when no cron is available (for example the first message on a Sunday). It reads valkyrie.db, computes adherence (planned vs done), and summarizes progress across weight, strength, endurance, nutrition and health, with alerts, then stores the report. Use valkyrie-followup, not this skill, for ordinary daily logging and questions.
---

# Valkyrie Analysis

This skill generates the periodic review: how consistent the user has been
(adherence) and how they are progressing. It is read-mostly: it reads `valkyrie.db`,
computes metrics, writes one `analysis_reports` row, and delivers a human-readable
summary in the user's language and tone.

Adherence is Valkyrie's most important metric - more important than calories or the
perfect plan. See `../shared/references/data-model.md` and
`../shared/references/coach-tone.md`.

## When this runs

- **Manually**, when the user asks for their review or "how am I doing".
- **By cron**, on a schedule (suggested: Sundays at 12:00).
- **First message of the week**, when no cron exists: if today is the start of a new
  week (e.g. the first Sunday message) and no report covers the past week yet, run
  analysis first, then continue with `valkyrie-followup`.

Check whether a recent report already exists before generating a duplicate:

```bash
python skills/shared/scripts/db.py query \
  --sql "SELECT id, period_end, kind FROM analysis_reports WHERE user_id = 1 ORDER BY id DESC LIMIT 1"
```

## What to compute

Choose the period (default: trailing 7 days for `WEEKLY`, trailing ~30 for `MONTHLY`,
or an explicit range for `ON_DEMAND`). Pull the data with `query`:

### Adherence (headline)

Planned vs done sessions for the period. The `context` / `refresh-state` commands
already maintain a rolling 30-day adherence in `current_state.adherence_last_30_days`;
for a specific window compute it directly:

```bash
python skills/shared/scripts/db.py query \
  --sql "SELECT COUNT(*) AS done FROM workouts WHERE user_id=1 AND date>=? AND status!='SKIPPED'" \
  --params '["2026-05-25"]'
```

Compare against the active plan's training days scaled to the window. Report a
percentage and the raw counts (planned, done).

### Progress by domain

- **Weight** - trend over the period from `weight_logs` (delta, direction, whether it
  matches the goal). Flag stalls or rapid changes.
- **Strength** - changes in load/reps for key lifts from `workout_sets` (e.g. bench
  +12%). Compare earliest vs latest in the window.
- **Endurance / resistance** - running distance/time, bike, walks, work capacity.
- **Nutrition** - habit quality from `nutrition_logs` (ratio of `ON_PLAN` vs
  `OFF_PLAN`, logging consistency), patterns (e.g. weekend drift). Habits and
  patterns, not calorie totals.
- **Health** - active or recent `health_events` and how they affected training.
- **Supplements** - adherence to creatine/protein/etc. if relevant. Never mention
  anabolic/private entries in the summary.

### Alerts

Surface meaningful signals, for example:

- "12 days without logging a workout."
- "8 days without a weight entry."
- "Training frequency dropped ~40% vs last period."
- "Bench press up ~12%."
- "Adherence below 50% - let's talk about what's getting in the way."

When adherence is low, reconnect to the user's stored `motivation` from onboarding.

## Deliver and store

1. Write the report:

```bash
python skills/shared/scripts/db.py exec \
  --sql "INSERT INTO analysis_reports (user_id,period_start,period_end,kind,adherence_pct,summary,metrics_json,created_at) VALUES (1,?,?,?,?,?,?,strftime('%Y-%m-%dT%H:%M:%SZ','now'))" \
  --params '["2026-05-25","2026-05-31","WEEKLY",68.0,"<summary text>","{\"bench_delta_pct\":12,\"weight_delta_kg\":-0.8}"]'
```

2. Present the summary to the user in their language and `coach_tone`: lead with
   adherence, then the wins, then the concerns and the alerts, and finish with one or
   two concrete priorities for the next period. Keep it honest and encouraging;
   `DIRECT` can be blunt about a low adherence week but never cruel.

3. Run `python skills/shared/scripts/db.py refresh-state` so the snapshot reflects the
   latest review.

## Privacy

Never reference anabolic or private substance use in the report or any shareable
output. Adapt the analysis silently using `profile.enhanced`. See
`../shared/references/natural-vs-enhanced.md`.
