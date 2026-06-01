# Neurotyping (Valkyrie reference)

Neurotyping is a model that classifies people by how their nervous system tends to
work, especially how they produce and respond to neurotransmitters (dopamine,
serotonin, acetylcholine, GABA, etc.). It was popularized in athletic and mental
performance coaching by Christian Thibaudeau and is used to adapt training,
nutrition and lifestyle to a person's neurochemical profile.

Valkyrie uses neurotyping as a soft adaptation layer, never as a hard medical
claim. The goal is to infer a likely type during onboarding (and refine it over
time from follow-up behavior) so the coach can tune volume, intensity, exercise
variety, rest and communication style.

## Why it matters for Valkyrie

- Some users thrive on variety, novelty and high intensity; others need structure,
  predictability and steady progression.
- Matching the program to the neurotype improves adherence, which is Valkyrie's
  top metric.
- It also informs tone: a stimulation-seeking user tolerates blunt pushing; an
  anxiety-prone user needs reassurance and structure.

## Types (practical summary)

These are working heuristics for coaching, not diagnoses.

- `TYPE_1A` - High dopamine, explosive, thrives on heavy and demanding work, gets
  bored fast. Adapt: low reps, high intensity, frequent variation, big lifts.
- `TYPE_1B` - Dopamine-driven but slightly more tolerant of volume than 1A. Adapt:
  heavy compound work with some accessory variety; keep it intense and novel.
- `TYPE_2A` - Balanced, dopamine/serotonin mix, hard worker, tolerates volume and
  bodybuilding-style training well. Adapt: moderate reps, hypertrophy blocks,
  structured progression.
- `TYPE_2B` - Serotonin-leaning, enjoys higher volume and pump work, very
  consistent. Adapt: higher reps, more accessory volume, steady routines.
- `TYPE_3` - Acetylcholine/GABA-leaning, sensitive to stress, prone to anxiety,
  needs predictability and technical mastery. Adapt: structured, repeatable
  routines, controlled tempo, lots of reassurance, avoid chaotic variety.
- `UNKNOWN` - Not enough signal yet. Default to balanced programming and refine
  over time.

## How to infer the neurotype during onboarding

Do not run a clinical questionnaire. Infer from natural answers and at most one or
two light questions. Useful signals:

- **Training preference and boredom**: "I get bored with the same routine" leans
  Type 1; "I like following a clear plan" leans Type 2/3.
- **Response to intensity**: enjoys maximal/heavy efforts (Type 1) vs prefers
  pump/volume (Type 2B) vs prefers control and form (Type 3).
- **Stress and anxiety**: easily stressed, overthinks, needs certainty -> Type 3.
- **Novelty seeking**: craves new stimuli, variety, competition -> Type 1.
- **Consistency**: naturally consistent and patient -> Type 2.

Store the inferred type in `profile.neurotype` and the supporting reasoning in
`profile.neurotype_notes`. When unsure, store `UNKNOWN` and refine later from
follow-up behavior (e.g. repeated boredom complaints, missed sessions after
monotony, or thriving under heavy days).

## How the neurotype changes programming

- Type 1: fewer reps, heavier loads, more frequent exercise rotation, autoregulated
  intensity, shorter blocks.
- Type 2: classic hypertrophy/strength progression, moderate-to-higher volume,
  stable exercise selection across a block.
- Type 3: highly structured and repeatable sessions, emphasis on technique and
  controlled tempo, conservative progression, strong reassurance and predictability.

Always combine the neurotype with the primary goal, the natural-vs-enhanced status
and the available equipment. Neurotype tunes the program; it does not override the
goal.
