# calibration-audit

**A falsifiable diagnostic for detecting environments that reward fragility.**

Source: a conversation on safety, adaptation, and the domestication of humans (2026).
License: CC0. Dependencies: Python stdlib only.

-----

## What this is

Three scored modules that turn a qualitative critique into quantitative
diagnostics. Input: a description of a system (organization, team, self,
relationship) as a dict. Output: JSON scores with falsifiable claims —
specific observations that would flip the verdict.

```
    system_description
           │
           ├──────────────┬──────────────┐
           ▼              ▼              ▼
     calibration_    observation_   adaptation_
       audit         dependence        debt
     (5 dims)          (3 dims)       (3 dims)
           │              │              │
           └──────────────┼──────────────┘
                          ▼
                  unified JSON report
                  + falsifiable claims
                  + cross-model prompt
```

## What this is NOT

- **Not a judgment of people.** It measures *environments* that reward
  fragility vs. environments that preserve calibration.
- **Not a recommendation engine.** It surfaces failing dimensions. It does
  not tell anyone what to do about them.
- **Not a certification.** If someone uses the JSON output to claim a system
  is “calibrated,” they have just triggered Q3 on themselves (witness-dependent
  skill).
- **Not a replacement for judgment.** It’s a lens. Operators with skin in the
  game make the calls.

-----

## The five questions (calibration_audit)

|# |Question                      |Dimension                   |Measures                                  |
|--|------------------------------|----------------------------|------------------------------------------|
|Q1|Where does the bite come from?|`bite_source`               |personal/impersonal feedback ratio        |
|Q2|Who has skin in the game?     |`skin_in_game`              |mean hops between decision and consequence|
|Q3|Observed vs. practiced?       |`witness_dependence`        |fraction of skills requiring audience     |
|Q4|What is memorialized?         |`memorialization_extinction`|praise × (1 − prevalence)                 |
|Q5|Where is the friction?        |`adaptation_debt`           |compounded debt from removed friction     |

Scores normalize to `[0.0, 1.0]` where `0.0 = calibrated`, `1.0 = domesticated`.

Bands:

- `0.00–0.30` calibrating (GREEN)
- `0.30–0.60` drifting (YELLOW)
- `0.60–0.85` mauling (RED)
- `0.85–1.00` memorialized_only (EXTINCT)

## Adaptation debt model

Removed friction compounds:

```
debt(t) = Σᵢ initial_loadᵢ × (1 + rᵢ)^tᵢ
```

Default compounding rates by domain:

|Domain       |Rate/yr|Doubling time|
|-------------|-------|-------------|
|institutional|0.08   |~9 years     |
|physical     |0.04   |~17 years    |
|social       |0.12   |~6 years     |
|cognitive    |0.15   |~5 years     |

Calibrated against time-to-failure patterns in analogous systems
(infrastructure-stability-model, urban-resilience-sim).

-----

## Usage

```python
from pipeline import run_unified_audit

system = {
    "system_id": "my_org",
    "feedback_events": [
        {"type": "personal", "count": 12},
        {"type": "impersonal", "count": 4},
    ],
    "decisions": [
        {"decision_maker": "mgmt", "consequence_hops": 3},
    ],
    "skills_observed": [
        {"skill": "compliance", "requires_witness": True},
        {"skill": "field_repair", "requires_witness": False},
    ],
    "memorialized_skills": [
        {"skill": "decision_making", "praise_volume": 700,
         "estimated_prevalence": 0.15},
    ],
    "friction_events": [
        {"name": "postmortems", "domain": "institutional",
         "initial_load": 0.7, "removed": True,
         "years_since_removed": 6.0},
    ],
    "skill_log": [
        {"skill": "field_repair", "context": "silent",
         "consequence_real": True},
    ],
}

report = run_unified_audit(system)
print(report["unified_band"])              # "mauling"
print(report["all_failing_dimensions"])    # list of broken dims
print(report["all_falsifiable_claims"])    # what would change the verdict
```

## Minimum data thresholds

Each dimension returns a YELLOW placeholder if starved for data:

- `feedback_events`: ≥10 tagged events
- `decisions`: ≥5 with consequence_hops
- `skills_observed`: ≥5 with requires_witness flag
- `skill_log`: ≥20 context-tagged events
- `friction_events`: ≥5 with removal status

Below threshold, the score defaults to 0.5 and the falsifier tells you what
data to provide.

-----

## Falsifiability

Every dimension ships with a falsifier — the specific observation that would
flip the score to GREEN. Example:

```json
{
  "name": "skin_in_game",
  "score": 0.83,
  "band": "mauling",
  "falsifier": "if mean consequence_hops drops below 1.2, decision-makers
                are feeling the physics; dimension flips to GREEN"
}
```

The test suite (`tests/test_calibration.py`) verifies that each falsifier
actually flips its dimension. If a test fails, the claim is wrong — not the
math. During build, one falsifier claim was caught as mis-specified and
corrected.

```bash
cd calibration-audit
PYTHONPATH=. python tests/test_calibration.py
```

## Self-audit

The framework runs on itself (`examples/self_audit.py`). Two inputs are
provided: an optimistic self-description and an honest one. The delta
between them is the propaganda-of-skill signal.

Observed result on first run:

```
OPTIMISTIC: 0.000 (perfect calibration)
HONEST:     0.331 (drifting)
DELTA:     +0.331
```

A delta above 0.15 means the framework scores itself higher when described
optimistically than when described honestly. That’s exactly the gap Q3
(observed-vs-practiced) is designed to detect. The framework caught itself.

Reading: **this framework calibrates best when used on systems by operators
with skin in the game — not on itself as self-description.**

-----

## Limits (honest)

1. **Input quality determines output quality.** Garbage-in-garbage-out
   applies. The framework cannot detect self-flattering inputs from a
   single run — only from the delta between optimistic and honest runs.
1. **Compounding rates are calibrated, not derived.** The default rates
   match observed failure patterns in analogous systems, but they are not
   first-principles constants.
1. **Band thresholds are choices, not physics.** The 0.30/0.60/0.85 cut
   points are Six Sigma-style choices; they are meaningful in relation to
   each other but not absolute.
1. **Memorialization-extinction scoring is coarse.** `praise_volume` and
   `estimated_prevalence` are hard to measure precisely. Use for relative
   comparison across skills, not absolute claims.
1. **The framework cannot audit itself in use.** If used as a signaling
   device (“look, I ran the audit”), it becomes witness-dependent skill
   (Q3 failure). Silent use only.

-----

## Connects to

- `substrate_audit.py` — the metrology-as-upstream-of-AI argument. This repo
  applies the same falsifiable-claims discipline to human systems.
- `first_principles_audit.py` — Six Sigma DMAIC validation. Compatible
  JSON output schema.
- `infrastructure-stability-model` — compounding-debt model shares time
  constants with that repo’s maintenance debt dynamics.
- `urban-resilience-sim` — cliff failure thresholds inspired by the ~year-23
  soil regeneration cliff observed there.

## Structure

```
calibration-audit/
├── schema.py                    shared dataclasses, Band enum, embedded prompt
├── calibration_audit.py         5-dim diagnostic (the five questions)
├── observation_dependence.py    3-dim witness-dependence engine
├── adaptation_debt.py           compounding debt model + cliff proximity
├── pipeline.py                  unified orchestrator
├── tests/test_calibration.py    11 falsification tests
└── examples/self_audit.py       meta-calibration (two-pass)
```

## License

CC0. No attribution required. The framework is designed to be forked,
broken, improved, and re-broken.

## A note on intended use

The artifacts this is built from describe people who still feel the weather,
practice without observation, and endure small pain rather than store it as
debt. This tool is for them. It is a lens for naming what they already see —
not a method for teaching it to people who do not.

If you recognize yourself in that description, this repo is yours. If you
don’t, the framework will probably feel wrong, and that reaction is also
data.
