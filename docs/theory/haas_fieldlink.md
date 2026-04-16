# HAAS-Q ↔ TAF Field Link

## What This Is

A formal bidirectional coupling between the **Thermodynamic Accountability Framework** (TAF) and the **Human-Automation-AI Safety & Quality Framework** ([HAAS-Q](https://github.com/JinnZ2/HAAS)).

TAF models the **energy physics of organisms** under institutional load.
HAAS-Q models the **control environment** where humans, machines, and AI operate together.

Neither framework is complete without the other:
- A "safe" environment with a collapsing operator is not safe.
- A healthy operator in an unsafe environment will not stay healthy.

The fieldlink makes this coupling explicit and computable.

## Architecture

```
┌─────────────────────┐         ┌─────────────────────┐
│       TAF           │         │      HAAS-Q          │
│                     │         │                      │
│  fatigue_score ─────┼────→────┼─ risk amplifier      │
│  collapse_distance ─┼────→────┼─ zone level          │
│  parasitic_debt ────┼────→────┼─ drift index         │
│                     │         │                      │
│  cognitive_load ←───┼────←────┼─ spatial risk        │
│  metabolic_load ←───┼────←────┼─ alerts              │
│  override_cost  ←───┼────←────┼─ control overrides   │
│                     │         │                      │
│  ghost_friction ←───┼──↔──→──┼─ AI-tax              │
└─────────────────────┘         └─────────────────────┘
```

## Coupling Direction

### HAAS-Q → TAF (Environment → Organism)

| HAAS-Q Signal | TAF Variable | Function |
|---|---|---|
| `compute_risk()` output | cognitive_load addition | `risk_field_cognitive_load()` |
| `check_alerts()` output | metabolic + cognitive load | `alert_metabolic_cost()` |
| Human-AI override count | cognitive load addition | `control_override_load()` |
| Sensor noise levels | hidden_count | Direct mapping |
| Brake efficiency | automation_reliability | Direct mapping |

### TAF → HAAS-Q (Organism → Environment)

| TAF Signal | HAAS-Q Variable | Function |
|---|---|---|
| fatigue_score (0-10) | Risk multiplier (≥1.0) | `fatigue_risk_amplifier()` |
| collapse_distance (0-1) | Zone level (GREEN/YELLOW/RED) | `collapse_distance_to_zone()` |
| parasitic_debt | Drift index (0-1) | `energy_debt_to_drift()` |

## Shared Equations

### Risk Field Cognitive Load
```
vigilance = haas_risk / confidence
latency_factor = 1 + latency_ms / 1000
cognitive_load = vigilance * latency_factor * 25.0
```

High risk with low confidence creates high vigilance demand, which drains cognitive energy.

### Fatigue → Risk Amplification
```
if fatigue ≤ 7:
    amplifier = 1 + fatigue * 0.05        # linear, matches HAAS-Q
if fatigue > 7:
    amplifier = 1 + 0.35 + 0.05*(f-7) + 0.02*(f-7)²  # nonlinear tail
```

Compatible with HAAS-Q's `risk.py` which applies `1 + fatigue_score * 0.05`.

### Collapse Distance → Zone
```
collapse_distance > 0.6  → GREEN   (sustainable)
0.2 < collapse_distance ≤ 0.6  → YELLOW  (degrading)
collapse_distance ≤ 0.2  → RED     (unsafe)
```

### Parasitic Debt → Drift
```
drift = 1 - exp(-0.5 * debt / threshold)
```

Accumulated institutional friction erodes operator calibration.

## The Feedback Loop

The `FieldLink` class runs the coupled loop:

1. **HAAS-Q signals arrive** — risk score, confidence, alerts, overrides
2. **Convert to TAF load** — cognitive, metabolic, and friction costs
3. **Run TAF computation** — fatigue, collapse distance, energy deficit
4. **Export to HAAS-Q** — risk amplifier, zone level, drift index
5. **HAAS-Q uses these** to adjust control decisions next step

This creates a **positive feedback loop** that matches reality: degrading operators increase risk, increased risk degrades operators further. The loop stabilizes only when either:
- The environment improves (lower risk, better automation)
- The operator is replenished (rest, energy input)
- The system collapses (flags trigger shutdown)

## Usage

```python
from core.haas_fieldlink import FieldLink

link = FieldLink(energy_input=100.0)

# Each simulation step couples both frameworks
result = link.step(
    haas_risk=0.5,
    haas_confidence=0.7,
    haas_alerts=["LOW_CONFIDENCE"],
    override_count=2,
    friction_events=1,
    hidden_count=4,
    automation_count=2,
    automation_reliability=0.85,
    temp_celsius=10,
    wind_mps=5,
    latency_ms=100,
)

# Result contains both TAF and HAAS-Q state
print(result["fatigue_score"])      # TAF output
print(result["risk_amplifier"])     # For HAAS-Q consumption
print(result["zone_level"])         # For HAAS-Q consumption
print(result["drift_index"])        # For HAAS-Q consumption
```

## Variable Map

See `FIELD_MAP` in `core/integrations/haas_fieldlink.py` for the complete shared namespace.

## Relationship to HAAS-Q energy.py

HAAS-Q's `energy.py` module already ports TAF equations **into** HAAS-Q (the `HumanEnergyState` dataclass). This fieldlink provides the **reverse path** plus the formal coupled loop. Together they form the complete bidirectional bridge.
