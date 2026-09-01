# ADR-001: Impulse-Based Zone Definition

## Status

Accepted

## Date

2026-09-01

## Context

Supply and demand zone methodologies vary widely. Many approaches use multi-candle bases, swing structures, or discretionary drawing rules. This project needs a precise, reproducible zone definition that:

- Ties zone creation to observable price behavior (an impulse move)
- Avoids ambiguous multi-candle base definitions
- Separates zone geometry from strength, lifecycle, and confluence
- Leaves room for empirical validation before fixing formulas and thresholds

## Decision

We adopt an **impulse-based zone definition** with the following rules:

1. **A validated impulse move is detected.** Not every price move qualifies; impulse qualification is a separate step with its own rules (to be defined).

2. **The last candle immediately preceding that impulse becomes the zone.** The zone bounds are the high and low of that single preceding candle. This is intentionally **not** a generic multi-candle supply/demand definition.

3. **Initial zone strength will eventually be derived from characteristics of the impulse.** Strength at creation reflects the originating move, not subsequent market behavior.

4. **Candidate impulse factors** for qualification and strength (exact formulas deferred):
   - Normalized displacement relative to ATR
   - Duration of the move
   - Directional efficiency

5. **Exact formulas, thresholds, and weights are intentionally NOT decided yet.** They will be specified in future ADRs or specs after research and statistical validation.

6. **A zone is a living object** whose strength can be reevaluated as time passes and additional confluences or events occur (retests, breaks, reaction behavior, etc.).

7. **Future confluence** may include 4H, 1H, and 15M alignment, structure, liquidity, freshness, retests, reaction behavior, and other strategy-specific factors. Confluence is separate from zone detection and initial strength.

## Concern Separation

The following concerns MUST remain distinct in design and implementation:

| Concern | Responsibility |
|---------|----------------|
| **Zone detection** | Given a validated impulse, derive zone bounds from the preceding candle |
| **Impulse qualification** | Decide whether a move is a validated impulse |
| **Initial zone strength** | Score at zone creation from impulse characteristics |
| **Zone lifecycle** | Ongoing reevaluation of strength and validity over time |
| **Multi-timeframe confluence** | Cross-TF alignment and contextual factors |
| **Historical outcomes** | Record post-formation market behavior for analysis |
| **Statistical validation** | Test hypotheses and models against historical outcomes |
| **Future ML research** | Exploratory modeling; not a substitute for rule specification |

No single module should combine zone detection with trading logic, execution, or backtesting.

## Consequences

### Positive

- Clear, testable zone boundary rule (single preceding candle)
- Impulse metrics provide a natural basis for initial strength
- Separation of concerns enables independent research and implementation
- Deferred formulas avoid premature optimization

### Negative / Risks

- Single-candle zones may differ from trader intuition used to wider bases
- Qualification rules require careful research to avoid overfitting
- Lifecycle and confluence add complexity; must not blur zone geometry

### Follow-Up

- Phase 2: Impulse qualification spec and implementation
- Phase 3: Zone detection implementation
- Future ADRs for strength formulas, lifecycle states, and confluence weights when evidence supports them

## References

- [DOMAIN_MODEL.md](../DOMAIN_MODEL.md)
- [PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md)
- [ROADMAP.md](../ROADMAP.md)
