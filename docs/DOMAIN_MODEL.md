# Domain Model

## Terminology

This document defines core concepts and their relationships. Implementation details, formulas, and thresholds are intentionally deferred.

## Impulse

A directional price move that may qualify as the basis for zone creation. Not every move is a validated impulse — qualification is a separate concern.

**Candidate qualification factors (not yet specified):**

- Normalized displacement relative to ATR
- Duration of the move
- Directional efficiency

## Validated Impulse

An impulse that passes qualification rules (to be defined). Only validated impulses trigger zone detection.

## Zone

The price range defined by the **last candle immediately preceding** a validated impulse. This is a single-candle zone boundary, not a generic multi-candle supply/demand zone.

A zone has:

- Price bounds (high/low of the preceding candle)
- Directional bias (implied by impulse direction)
- Temporal context (timeframe, timestamp)
- Lifecycle state (active, weakened, invalidated — exact states TBD)

## Concern Separation

### Zone Detection

**What:** Given a validated impulse, identify the preceding candle and derive the zone bounds.

**Inputs:** Validated impulse, OHLCV series  
**Outputs:** Zone geometry and metadata  
**Does not:** Score strength, evaluate confluence, or make trade decisions

### Impulse Qualification

**What:** Determine whether a price move qualifies as a validated impulse.

**Inputs:** OHLCV series, market context  
**Outputs:** Qualification result and impulse metadata  
**Does not:** Define the zone or assign strength

### Initial Zone Strength

**What:** Score a newly detected zone based on characteristics of the originating impulse.

**Inputs:** Validated impulse metrics, zone metadata  
**Outputs:** Initial strength score or tier  
**Does not:** Incorporate lifecycle events or multi-timeframe context (those are separate)

### Zone Lifecycle

**What:** Reevaluate zone strength and validity as time passes and market events occur.

**Inputs:** Zone, subsequent price action, confluence updates  
**Outputs:** Updated strength, state transitions  
**Does not:** Redefine zone geometry (bounds are fixed at detection)

### Multi-Timeframe Confluence

**What:** Assess alignment and context across timeframes (e.g. 4H, 1H, 15M).

**Candidate factors (not yet weighted):**

- Timeframe alignment
- Market structure
- Liquidity
- Freshness
- Retests
- Reaction behavior
- Strategy-specific factors

**Does not:** Replace impulse qualification or zone detection

### Historical Outcomes

**What:** Record what happened after a zone formed (touches, breaks, reactions, etc.) for retrospective analysis.

**Purpose:** Feed statistical validation and research; not real-time trading logic.

### Statistical Validation

**What:** Rigorous hypothesis testing of qualification rules, strength models, and confluence factors using historical outcomes.

**Purpose:** Evidence-based refinement before production use.

### Future ML Research

**What:** Exploratory supervised or unsupervised modeling using features from impulses, zones, confluence, and labeled outcomes.

**Purpose:** Research track separate from rule-based core logic. Models must be validated statistically before adoption.

## Entity Relationships (Conceptual)

```
OHLCV Series
    │
    ▼
Impulse (candidate) ──qualification──► Validated Impulse
                                            │
                                            ▼
                                       Zone (detected)
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    ▼                       ▼                       ▼
           Initial Strength          Lifecycle Updates      Confluence Context
                    │                       │                       │
                    └───────────────────────┴───────────────────────┘
                                            │
                                            ▼
                                   Historical Outcome
                                            │
                                            ▼
                              Statistical Validation / ML Research
```

## Related Documents

- [ADR-001](decisions/ADR-001-impulse-based-zone-definition.md)
- [DATA_MODEL.md](DATA_MODEL.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
