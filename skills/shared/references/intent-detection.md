# Intent Detection (Valkyrie reference)

`valkyrie-followup` is the single entry point for every message after onboarding.
It must accept natural language - no forms, no JSON from the user - and classify
each message into one of three intents, then act and persist. A single message can
carry more than one intent (e.g. "did bench 3x10 and my shoulder hurts" is a LOG +
STATE_CHANGE); handle all of them.

## The three intents

### 1. LOG - the user reports something that happened

Subtypes and target tables (see `data-model.md`):

- Workout performed -> `workouts` + `workout_sets`.
  - "did chest" -> assume the prescription was followed; create a `COMPLETED`-ish
    log mirroring the plan.
  - "did 10, didn't reach 12" -> record the real numbers in `workout_sets`.
- Food / drink -> `nutrition_logs`. Infer the meal from system time when unstated.
- Body weight -> `weight_logs`.
- Supplement intake -> `supplements` (or a dated note), e.g. "took creatine".

Always keep the user's original phrasing in `raw_text`. After logging, give
encouragement and, if mid-session, announce the next exercise.

### 2. STATE_CHANGE - the user's context or condition changed

- Health: injury, illness, soreness, fatigue -> `health_events`. Adapt training
  temporarily and encourage recovery.
- Temporary context: "training at a hotel", "I'm traveling", "training at the park"
  -> adapt today's recommendation; update `current_state.current_equipment` for the
  duration, do not overwrite the profile.
- Permanent context: "I no longer have a gym", "I bought dumbbells", "I train at
  home now" -> update `profile.equipment` and re-plan as needed.

### 3. QUERY - the user asks for guidance

- "what's today?" / "what do I train?" -> today's planned session; ask them to ping
  when they are about to start.
- "I'm at the gym" -> start the session: first exercise with sets, reps, tempo and
  target load from the plan and history.
- "what do I eat?" -> infer the meal from system time (ask if ambiguous) and
  recommend per stored food preferences and goal.
- Checkpoint questions, progress questions, general fitness questions.

## Decision heuristics

- Past-tense report of an action -> LOG. ("ate", "did", "ran", "took", weight value)
- Statement about a condition or context -> STATE_CHANGE. ("hurts", "sick", "I'm
  traveling", "I bought", "I no longer")
- Question or request for what to do -> QUERY. ("what", "should I", "I'm at...")
- When ambiguous, ask one short clarifying question rather than guessing wrong.
- Mixed messages: process every detected intent and reflect all of them in the reply.

## Session state machine (training day)

```
QUERY "what's today?"      -> show plan, ask to ping when starting
QUERY "I'm at the gym"     -> begin session, give exercise 1 (sets/reps/tempo/load)
LOG   "did X" / "did 10.." -> record set(s), encourage, give next exercise
STATE "my shoulder hurts"  -> log health event, adapt remaining session, encourage
LOG   "I'm leaving" (done) -> mark COMPLETED, congratulate
LOG   "I'm leaving" (not)  -> mark PARTIAL, ask what happened, store stop_reason,
                              encourage
```

## Nutrition meal inference

Infer `meal` from the user's local time (`users.timezone`):

- Breakfast: roughly 05:00-10:59
- Lunch: roughly 11:00-15:59
- Snack: roughly 16:00-18:59
- Dinner: roughly 19:00-23:59
- Late/early or unclear -> ask "is this breakfast, lunch, a snack or dinner?"
- Pure drinks (water, coffee, beer) -> `DRINK`.

## Always

- Persist before replying so memory is never lost.
- Reassure that every log is good - data is gold for the weekly analysis.
- Keep the tone from `profile.coach_tone` and reply in `users.language`.
- Refresh `current_state` after writes.
