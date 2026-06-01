# Natural vs Enhanced (Valkyrie reference)

This reference explains why Valkyrie asks about supplements and anabolic use during
onboarding, and how that information changes programming. The data is **private**:
it is used only to adapt the routine and recovery assumptions, and is never surfaced
in any shareable output. See `data-model.md` (`profile.enhanced`, `supplements`).

## The core difference

A natural athlete has a more limited capacity to recover, synthesize muscle protein
and tolerate large training volumes. They generally benefit from efficient training:
moderate volume, high execution quality, good fatigue management and consistent
nutrition. Every set should justify its recovery cost.

A person using anabolics has an artificially increased capacity for recovery and
muscle building. They can tolerate more volume, more frequency, and recover faster
from very demanding sessions. In nutrition, both need enough protein and energy to
progress, but the enhanced user can convert a larger share of those resources into
muscle and lose less muscle during caloric deficits. Copying routines or diets
designed for enhanced bodybuilders is usually a poor strategy for most naturals.

## How Valkyrie adapts

- `enhanced = 0` (natural): default. Prioritize moderate volume, quality of
  execution, fatigue management, and sustainable progression. Do not prescribe
  pro-bodybuilder volume.
- `enhanced = 1`: allow higher volume and frequency, faster progression, and more
  aggressive deficits while preserving muscle, as appropriate to the goal.

Combine this with the neurotype and goal. Enhanced status raises the volume/recovery
ceiling; it does not change which goal or split is appropriate.

## Asking about it (privacy)

When asking about supplements and substances during onboarding:

- Ask about creatine, protein, omega 3, magnesium, caffeine, and anything anabolic.
- State explicitly, before they answer, that this information **will never be
  published or shared** and is only used to adapt their routine to their real
  recovery capacity.
- Record anabolic/sensitive entries with `is_private = 1` in the `supplements`
  table and set `profile.enhanced = 1`.
- Never mention or imply substance use in analysis reports, summaries, or any output
  the user might share. Adapt silently.

## Supplements as supportive, not magic

- Creatine: generally recommended for most users.
- Protein: a tool to reach protein targets, not mandatory if diet covers it.
- Omega 3 / magnesium: supportive of recovery and general health.
- Caffeine / pre-workout: analyze context; do not encourage unnecessary dependence.

Log supplement intake from follow-up messages ("took creatine") so the analysis can
relate it to adherence and recovery.
