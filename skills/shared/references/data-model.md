# Valkyrie Data Model

Valkyrie's source of truth is a single SQLite database: `valkyrie.db`. Every skill
reads from and writes to this file through `skills/shared/scripts/db.py`. If the
database does not exist yet, run `python skills/shared/scripts/db.py init` first.

The database lives at the path given by the `VALKYRIE_DB` environment variable, or
`./valkyrie.db` in the working directory when that variable is unset. The host
application is responsible for placing this file in a stable, writable, per-user
location. Without persistent storage, Valkyrie has no memory.

## Design principles

- **Adherence over perfection.** We store what the user actually did, not only what
  was planned. Both are needed to compute adherence.
- **Keep the raw text.** Every log keeps the user's original phrasing in a
  `raw_text` column alongside the normalized/structured fields. Natural language is
  the interface; structure is for analysis.
- **One user per database by default.** The schema supports multiple users, but a
  typical deployment is one `valkyrie.db` per end user. `user_id = 1` is the default.
- **Private by default.** Substance/anabolic data is sensitive. It is stored so the
  coach can adapt training, never to be surfaced in shareable output.

## Tables

### users

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Default user is `1`. |
| `created_at` | TEXT | ISO 8601 timestamp. |
| `language` | TEXT | Detected user language (e.g. `es`, `en`). Communication language, not file language. |
| `timezone` | TEXT | IANA tz (e.g. `America/Montevideo`). Used for meal-time and checkpoint logic. |

### profile

One row per user. Captures the onboarding result. Adjustable later via follow-up.

| Column | Type | Notes |
|---|---|---|
| `user_id` | INTEGER FK | References `users.id`. |
| `name` | TEXT | Asked first in onboarding. |
| `coach_tone` | TEXT | Enum: `DIRECT`, `BALANCED`, `MOTIVATIONAL`. Asked second. |
| `age` | INTEGER | |
| `sex` | TEXT | Enum: `MALE`, `FEMALE`, `OTHER`. |
| `height_cm` | REAL | |
| `start_weight_kg` | REAL | Weight captured during onboarding. |
| `body_composition` | TEXT | Enum: `LEAN`, `AVERAGE`, `OVERWEIGHT`, `OBESE` (perceived). |
| `activity_level` | TEXT | Enum: `SEDENTARY`, `LIGHT`, `ACTIVE`, `VERY_ACTIVE`. |
| `job_type` | TEXT | Free text describing daily job (desk, physical labor, shifts, etc.). |
| `primary_goal` | TEXT | Enum: `LOSE_FAT`, `GAIN_MUSCLE`, `GAIN_STRENGTH`, `IMPROVE_HEALTH`, `SPORT_PERFORMANCE`, `LOOK_GOOD`. |
| `secondary_goal` | TEXT | Specific and measurable, e.g. "delt hypertrophy", "front lever", "run 10km". NOT a copy of the primary list. |
| `motivation` | TEXT | Why they want this goal. Used to re-motivate when adherence drops. |
| `neurotype` | TEXT | Enum: `TYPE_1A`, `TYPE_1B`, `TYPE_2A`, `TYPE_2B`, `TYPE_3`, `UNKNOWN`. See `neurotyping.md`. |
| `neurotype_notes` | TEXT | Free text supporting the neurotype inference. |
| `technical_level` | TEXT | Enum: `LOW`, `MEDIUM`, `HIGH`. |
| `days_per_week` | INTEGER | Training availability. |
| `minutes_per_session` | INTEGER | Training availability. |
| `equipment` | TEXT | Enum (comma-separated allowed): `FULL_GYM`, `BASIC_GYM`, `HOME`, `OUTDOOR`, `BANDS`, `BODYWEIGHT`. |
| `training_preference` | TEXT | Enum: `HEAVY_DUTY`, `PPL`, `UPPER_LOWER`, `FULL_BODY`, `NONE`. |
| `diet_type` | TEXT | Enum: `OMNIVORE`, `VEGETARIAN`, `VEGAN`. |
| `diet_restrictions` | TEXT | Free text: celiac, lactose, allergies, etc. |
| `fasting` | TEXT | Enum: `NONE`, `12_12`, `14_10`, `16_8`, `20_4`, `CUSTOM`. |
| `food_preferences` | TEXT | Free text: liked/disliked foods, practical constraints. Drives "what do I eat?". |
| `enhanced` | INTEGER | `0` natural, `1` uses anabolics. Private. Drives volume/recovery assumptions. |
| `updated_at` | TEXT | ISO 8601 timestamp. |

### supplements

What the user takes. Private for anabolics.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `user_id` | INTEGER FK | |
| `name` | TEXT | e.g. `CREATINE`, `PROTEIN`, `OMEGA_3`, `MAGNESIUM`, `CAFFEINE`, `ANABOLIC:<detail>`, `OTHER:<detail>`. |
| `dose` | TEXT | Free text (e.g. "5g", "1 scoop"). |
| `is_private` | INTEGER | `1` for anabolics/sensitive entries. Never surfaced in shareable output. |
| `created_at` | TEXT | |

### plan

The current training plan (initial duration suggested: 4 weeks). One active plan at a time.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `user_id` | INTEGER FK | |
| `name` | TEXT | e.g. "Initial 4-week adherence block". |
| `start_date` | TEXT | ISO date. |
| `end_date` | TEXT | ISO date. |
| `split` | TEXT | Resolved split, e.g. `PPL`, `UPPER_LOWER`. |
| `notes` | TEXT | Free text. |
| `is_active` | INTEGER | `1` for the current plan. |
| `created_at` | TEXT | |

### plan_days

The planned sessions inside a plan (the prescription used to compute adherence and to answer "what's today?").

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `plan_id` | INTEGER FK | |
| `weekday` | INTEGER | 0 = Monday ... 6 = Sunday. |
| `focus` | TEXT | e.g. "Push", "Pull", "Legs", "Rest", "Cardio". |
| `exercises_json` | TEXT | JSON array of prescribed exercises (see below). |

`exercises_json` item shape:

```json
{
  "order": 1,
  "exercise": "BENCH_PRESS",
  "raw_name": "Flat barbell bench press",
  "sets": 3,
  "reps": "8-12",
  "tempo": "3-1-2-1",
  "target_load_kg": 100,
  "rest_seconds": 120,
  "note": "Eccentric control, supports hypertrophy goal"
}
```

`tempo` uses the eccentric-extended-concentric-contracted notation (see `tempo.md`).

### workouts

One row per logged training session.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `user_id` | INTEGER FK | |
| `date` | TEXT | ISO date. |
| `plan_day_id` | INTEGER FK | Nullable. Links the session to its prescription. |
| `status` | TEXT | Enum: `COMPLETED`, `PARTIAL`, `SKIPPED`. |
| `stop_reason` | TEXT | Nullable. Why a session ended early (injury, frustration, time, etc.). |
| `raw_text` | TEXT | Original user phrasing. |
| `created_at` | TEXT | |

### workout_sets

The actual sets performed within a workout (the real numbers, e.g. "did 10, didn't reach 12").

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `workout_id` | INTEGER FK | |
| `exercise` | TEXT | Enum where possible (see Exercise enums). |
| `raw_name` | TEXT | Original exercise text. |
| `set_index` | INTEGER | 1-based. |
| `reps` | INTEGER | Actual reps. |
| `load_kg` | REAL | Actual load. Nullable for bodyweight/time-based. |
| `tempo` | TEXT | Nullable. |
| `note` | TEXT | Nullable. |

### nutrition_logs

Simple, judgment-free food/drink logging. No calorie counting required by default.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `user_id` | INTEGER FK | |
| `date` | TEXT | ISO date. |
| `meal` | TEXT | Enum: `BREAKFAST`, `LUNCH`, `SNACK`, `DINNER`, `DRINK`, `OTHER`. Inferred from system time when unstated. |
| `description` | TEXT | Normalized food description. |
| `raw_text` | TEXT | Original phrasing ("ate chicken", "1L beer on the weekend"). |
| `quality` | TEXT | Nullable enum: `ON_PLAN`, `OFF_PLAN`, `NEUTRAL`. Coach's light assessment. |
| `created_at` | TEXT | |

### weight_logs

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `user_id` | INTEGER FK | |
| `date` | TEXT | ISO date. |
| `weight_kg` | REAL | |
| `raw_text` | TEXT | |
| `created_at` | TEXT | |

### health_events

Injuries, illness, soreness, anything affecting training. Drives temporary adaptation.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `user_id` | INTEGER FK | |
| `date` | TEXT | ISO date. |
| `type` | TEXT | Enum: `INJURY`, `ILLNESS`, `SORENESS`, `FATIGUE`, `OTHER`. |
| `body_part` | TEXT | Nullable (e.g. "shoulder"). |
| `severity` | TEXT | Enum: `MILD`, `MODERATE`, `SEVERE`. |
| `status` | TEXT | Enum: `ACTIVE`, `RECOVERING`, `RESOLVED`. |
| `raw_text` | TEXT | |
| `created_at` | TEXT | |

### checkpoints

Scheduled performance/progress measurements. Not in week 1. First around one month, then every 2-3 months.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `user_id` | INTEGER FK | |
| `scheduled_date` | TEXT | ISO date. |
| `type` | TEXT | Enum: `STRENGTH`, `FAT_LOSS`, `HEALTH`, `PERFORMANCE`. Depends on goal. |
| `metrics_json` | TEXT | JSON of what to measure (e.g. bench, squat, waist, photos, run time). |
| `status` | TEXT | Enum: `SCHEDULED`, `DONE`, `MISSED`. |
| `results_json` | TEXT | Nullable JSON of recorded results. |
| `created_at` | TEXT | |

### analysis_reports

Output of `valkyrie-analysis`. Kept for trend comparison.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | |
| `user_id` | INTEGER FK | |
| `period_start` | TEXT | ISO date. |
| `period_end` | TEXT | ISO date. |
| `kind` | TEXT | Enum: `WEEKLY`, `MONTHLY`, `ON_DEMAND`. |
| `adherence_pct` | REAL | Workouts done / planned for the period. |
| `summary` | TEXT | Human-readable report (in the user's language). |
| `metrics_json` | TEXT | JSON of computed deltas (weight, strength, endurance, etc.). |
| `created_at` | TEXT | |

### current_state (view / cached row)

A single denormalized snapshot for fast context loading. Implemented as a table with
one row per user, refreshed on writes.

| Field | Description |
|---|---|
| `current_weight_kg` | Latest weight log. |
| `current_phase` | Active plan name / phase. |
| `current_health` | Most relevant active health event, or `OK`. |
| `current_equipment` | Equipment in use (may differ temporarily from profile, e.g. travel). |
| `adherence_last_30_days` | Rolling adherence percentage. |
| `last_workout_date` | Date of the last logged workout. |
| `next_checkpoint_date` | Next scheduled checkpoint. |
| `updated_at` | ISO timestamp. |

## Exercise enums

Store a normalized enum when recognizable, always keep `raw_name`. Non-exhaustive:

`BENCH_PRESS`, `INCLINE_BENCH`, `OVERHEAD_PRESS`, `SQUAT`, `FRONT_SQUAT`,
`DEADLIFT`, `ROMANIAN_DEADLIFT`, `PULLUP`, `CHINUP`, `ROW`, `LAT_PULLDOWN`,
`LATERAL_RAISE`, `LEG_PRESS`, `LUNGE`, `BICEP_CURL`, `TRICEP_EXTENSION`,
`PLANK`, `FRONT_LEVER_PROGRESSION`, `SCAPULAR_DEPRESSION`, `RUN`, `BIKE`,
`WALK`, `OTHER`.

When an exercise is not in the list, use `OTHER` and rely on `raw_name`.
