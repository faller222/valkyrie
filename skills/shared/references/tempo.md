# Tempo (Valkyrie reference)

Tempo determines how long a muscle stays under tension and how much momentum and
inertia contribute to a rep. Controlling the speed of each repetition makes the
muscle do the actual work, improves technique, and makes the stimulus consistent
across sets and sessions. A slow, controlled rep is usually more demanding for the
muscle than a fast rep performed with swings or bounces.

The eccentric phase (the lowering) is especially important because that is where
the muscle can generate high levels of mechanical tension. That is why many
programs recommend lifting with strong intent and lowering under control. The goal
is not to move everything extremely slowly, but to keep effective tension on the
muscle while avoiding wasted effort on impulsive movement.

## Notation

Valkyrie uses the **eccentric-extended-concentric-contracted** notation, four
numbers in seconds:

```
E - X - C - K
```

- `E` (eccentric): the lowering phase.
- `X` (extended): the pause in the stretched/lengthened position.
- `C` (concentric): the lifting phase.
- `K` (contracted): the pause in the shortened/contracted position.

Example: `3-1-2-1` means lower for 3 seconds, pause 1 second stretched, lift for
2 seconds, pause 1 second squeezed.

A `0` means no deliberate pause. `X` is sometimes used for "explosive" on the
concentric, but Valkyrie prefers explicit seconds for clarity; use `1` as a fast
controlled concentric when in doubt.

## How Valkyrie uses tempo

- Every prescribed exercise in a plan day carries a `tempo` field (see
  `data-model.md`).
- When the user says "I'm at the gym", the coach states the tempo together with
  reps and target load, e.g. "Bench: 3 sets of 8-12, tempo 3-1-2-1, ~100 kg".
- For technical or rehab-focused work (and for Type 3 users, see `neurotyping.md`),
  bias toward controlled eccentrics and explicit pauses.
- For strength/explosive work, keep the eccentric controlled but the concentric
  fast.

## Practical defaults

- Hypertrophy: `3-1-1-1` to `4-0-1-0`.
- Strength: `2-1-1-0` with intent on the concentric.
- Technique / rehab / beginners: `3-1-3-1`, emphasize control.
- Power/explosive accessory: `2-0-1-0`, fast concentric.

Tempo is a tool to keep effective tension and quality of execution, not a rule to
make every rep maximally slow.
