# Logic-Ferret ↔ TAF Field Link

## What This Is

A formal bidirectional coupling between the **Thermodynamic Accountability Framework** (TAF) and **Logic-Ferret** ([github.com/JinnZ2/Logic-Ferret](https://github.com/JinnZ2/Logic-Ferret)).

TAF measures institutional accountability in **energy units** (physics).
Logic-Ferret detects **rhetorical camouflage** (rhetoric).

Same target, different instruments. The fieldlink couples them for cross-validation.

## Architecture

```
┌──────────────────────┐         ┌──────────────────────┐
│        TAF           │         │    Logic-Ferret       │
│                      │         │                       │
│  fatigue_score ──────┼────→────┼─ expected camouflage  │
│  collapse_distance ──┼────→────┼─ expected fragility   │
│  energy_debt ────────┼────→────┼─ expected deflection  │
│  friction_ratio ─────┼────→────┼─ amplification factor │
│                      │         │                       │
│  hidden_count ←──────┼────←────┼─ camouflage_score     │
│  feedback_integrity ←┼────←────┼─ fallacy_total        │
│  friction_ratio ←────┼────←────┼─ sensor_suite scores  │
│  prediction_error ←──┼────←────┼─ gaslight_score       │
│                      │         │                       │
│  signal_fidelity ←───┼──↔──→──┼─ signal_fidelity      │
└──────────────────────┘         └──────────────────────┘
```

## Layer-Level Cross-Reference

| TAF Module | Logic-Ferret Sensor | Shared Signal |
|---|---|---|
| Narrative Stripper | Stated Problem + Feasibility Gap | Story vs. energy math |
| Social Overhead Accountant | Systemic Alignment | Performative action detection |
| Root Cause Depth Analyzer | Hidden Driver + Consequences | Actual vs. stated cause |
| Friction Ratio | Camouflage Score | Institutional resistance to transparency |
| Energy Conservation | Consequence divergence | Output != promise |
| Entropy / waste growth | Feedback Loops | Self-reinforcing decay |

## Coupling Direction

### Ferret → TAF (Rhetoric → Physics)

| Ferret Output | TAF Variable | Function |
|---|---|---|
| camouflage_score (0-1) | hidden variable count (0-10) | `camouflage_to_hidden_count()` |
| fallacy_total (int) | feedback integrity (0-10) | `fallacy_count_to_feedback_integrity()` |
| sensor_suite scores | friction ratio (0-1) | `sensor_scores_to_friction_ratio()` |
| gaslight_score (0-1, INVERTED) | prediction error (0-1) | `gaslight_score_to_prediction_error()` |

### TAF → Ferret (Physics → Rhetoric)

| TAF Output | Expected Ferret Signal | Function |
|---|---|---|
| fatigue_score + friction | Expected camouflage level | `energy_deficit_to_camouflage_expectation()` |
| collapse_distance | Expected narrative fragility | `collapse_distance_to_narrative_fragility()` |
| energy_debt | Expected responsibility deflection | `parasitic_debt_to_deflection_expectation()` |

## Cross-Validation

The `FerretLink` class compares what TAF **predicts** the narrative should look like (given energy state) with what the Ferret **actually found**.

Three convergence states:

| State | Delta | Meaning |
|---|---|---|
| **STRONG** | < 0.15 | Physics and rhetoric agree. High diagnostic confidence. |
| **MODERATE** | 0.15-0.35 | Partial agreement. Narrative partially effective, or lag between reality and rhetoric. |
| **DIVERGENT** | > 0.35 | Significant mismatch. Either the narrative is working overtime (preemptive cover), or the energy deficit is so normalized it doesn't need rhetorical defense. |

## Key Equations

### Camouflage → Hidden Count
```
base_count = camouflage_score * 8
bonus = sum(0.5 per "strong" layer signal, 0.15 per "moderate")
hidden_count = min(round(base_count + bonus), 10)
```

### Fallacy Count → Feedback Integrity
```
integrity = 10 * exp(-0.12 * fallacy_total)
```
10 fallacies → ~3.0 integrity. Exponential decay matches how fallacies compound.

### Energy Deficit → Expected Camouflage
```
expected = (fatigue_score / 10) * (1 + friction_ratio)
```
Higher fatigue + higher friction = more narrative needed to justify extraction.

### Collapse Distance → Narrative Fragility
```
fragility = 1 - collapse_distance^0.6
```
Nonlinear: fragility accelerates as systems approach collapse.

## Polarity Note

**IMPORTANT**: `gaslight_frequency_meter.assess()` returns INVERTED polarity:
- `1.0` = low gaslighting (good)
- `0.0` = high gaslighting (bad)

All other Logic-Ferret sensors return `1.0` = high detection (bad).
The fieldlink handles this inversion in `gaslight_score_to_prediction_error()`.

## Usage

```python
from core.ferret_fieldlink import FerretLink

link = FerretLink()

# Load Logic-Ferret analysis results
link.ingest_ferret_results(
    camouflage_score=0.55,
    fallacy_total=7,
    sensor_results={"Propaganda Tone": 0.3, "Gatekeeping": 0.5, ...},
    layer_signals={"Stated Problem": "strong", "Feasibility Gap": "moderate", ...},
    gaslight_score=0.6,
)

# Load TAF energy state
link.ingest_taf_state(
    fatigue_score=6.5,
    collapse_distance=0.45,
    energy_debt=12.0,
    friction_ratio=0.4,
)

# Cross-validate
report = link.cross_validate()
print(report["convergence"])      # STRONG / MODERATE / DIVERGENT
print(report["signal_fidelity"])  # Combined clarity (0-1)
print(report["interpretation"])   # Human-readable analysis
```

## Logic-Ferret Audit Notes (2026-04-07)

Issues found during fieldlink integration review:

### Critical

1. **`run_full_sensor_scan.py` — Syntax error**: Extra closing paren on import block. Will crash on import.
   ```python
   gaslight_frequency_meter,
       agency_detector,
   )
   )    # ← extra paren
   ```

2. **`propaganda_tone.py` — Missing file**: Imported by `run_full_sensor_scan.py` but returns 404. No such module exists in the repo.

### Bugs

3. **`run_full_sensor_scan.py` — Duplicate import**: `agency_detector` imported twice in the same block.

4. **`Logic_fallacy_ferret.py` — Broken relative import**: Uses `from .fallacy_overlay import annotate_text` which only works inside a package. Will fail when run directly.

5. **`setup.py` — Entry point mismatch**: Points to `gui.fallacy_gui:main` but `fallacy_gui.py` is at root level (not in `gui/` package) and has no `main()` function.

6. **`fallacy_gui.py` — No cancel handling**: If user cancels file dialog, `file_path` is `""` and `open("")` raises `FileNotFoundError`.

### Design Issues

7. **Inverted score polarity mismatch**: `gaslight_frequency_meter` returns `1.0 = good` while all other sensors return `1.0 = bad`. The `truth_integrity_score.calculate_c3()` doesn't account for this — gaslight scores will be inverted relative to others in the composite.

8. **New sensors not wired in**: `responsibility_deflection_sensor.py`, `true_accountability_sensor.py`, and `meritocracy_detector.py` exist but are not imported in `run_full_sensor_scan.py`.

9. **Duplicate `truth_integrity_score.py`**: Root-level version (equal weights) differs from `sensor_suite/sensors/` version (specific weights). Which one gets imported depends on PYTHONPATH.
