“””
observation_dependence.py — witness-dependence coefficient for skill inventories

Source: Independent Animal’s Creed, Principle II (2026).
License: CC0.
Dependencies: stdlib only.

Core claim (falsifiable):
Skill that requires no witness cannot be audited, automated, or taken.
Therefore: witness_dependence is a measure of fragility under system failure.

Energy-flow:
skill_log (events over time)
│
▼
┌──────────────────────────────────────┐
│ classify: witnessed / silent         │
│ classify: certified / uncertified    │
│ classify: recorded / unrecorded      │
└──────────────────────────────────────┘
│
▼
witness_dependence = f(observation_signal)
calibration_reserve = 1 - witness_dependence

Input schema:
{
“entity_id”: str,                        # person, team, org
“skill_log”: [
{
“skill”: str,
“timestamp”: str (ISO),
“context”: “witnessed”|“silent”|“recorded”|“certified”|“uncertified”,
“consequence_real”: bool,            # did outcome have physical stake?
},
…
]
}
“””

from typing import Any
from collections import defaultdict
from schema import DimensionScore, CalibrationReport, Band

# Contexts that indicate witness-dependence (raise domestication score)

WITNESS_CONTEXTS = {“witnessed”, “recorded”, “certified”}

# Contexts that indicate calibration reserve (lower domestication score)

SILENT_CONTEXTS = {“silent”, “uncertified”}

def classify_events(skill_log: list[dict[str, Any]]) -> dict[str, Any]:
“”“Classify events into witness-dependent vs silent practice.”””
witness = 0
silent = 0
real_consequence = 0
simulated = 0
per_skill = defaultdict(lambda: {“witness”: 0, “silent”: 0})

```
for ev in skill_log:
    ctx = ev.get("context", "")
    skill = ev.get("skill", "unknown")
    if ctx in WITNESS_CONTEXTS:
        witness += 1
        per_skill[skill]["witness"] += 1
    elif ctx in SILENT_CONTEXTS:
        silent += 1
        per_skill[skill]["silent"] += 1
    if ev.get("consequence_real", False):
        real_consequence += 1
    else:
        simulated += 1

return {
    "witness": witness,
    "silent": silent,
    "total": witness + silent,
    "real_consequence": real_consequence,
    "simulated": simulated,
    "per_skill": dict(per_skill),
}
```

def score_witness_dependence(skill_log: list[dict[str, Any]]) -> DimensionScore:
“”“Fraction of skill practice that requires observation.”””
c = classify_events(skill_log)
if c[“total”] == 0:
return DimensionScore(
name=“witness_dependence”,
score=0.5,
band=Band.YELLOW,
evidence=[“no classified skill events”],
falsifier=“log ≥20 skill events with context tags”,
)

```
score = c["witness"] / c["total"]
return DimensionScore(
    name="witness_dependence",
    score=score,
    band=Band.from_score(score),
    evidence=[
        f"total events: {c['total']}",
        f"witness-dependent: {c['witness']} ({score:.1%})",
        f"silent practice: {c['silent']}",
    ],
    falsifier=(
        "if silent practice exceeds 70% of total events, "
        "dimension flips to GREEN (skill exists without audience)"
    ),
)
```

def score_simulation_dependence(skill_log: list[dict[str, Any]]) -> DimensionScore:
“””
‘Mistakes the map for the terrain’ — Q3 secondary signal.
Fraction of practice with SIMULATED rather than REAL consequence.
“””
c = classify_events(skill_log)
total_events = c[“real_consequence”] + c[“simulated”]
if total_events == 0:
return DimensionScore(
name=“simulation_dependence”,
score=0.5,
band=Band.YELLOW,
evidence=[“no consequence data”],
falsifier=“tag events with consequence_real boolean”,
)

```
score = c["simulated"] / total_events
return DimensionScore(
    name="simulation_dependence",
    score=score,
    band=Band.from_score(score),
    evidence=[
        f"real-consequence practice: {c['real_consequence']}",
        f"simulated practice: {c['simulated']}",
        f"simulation fraction: {score:.1%}",
    ],
    falsifier=(
        "if real-consequence events exceed 60% of total practice, "
        "the map/terrain confusion is absent; flips to GREEN"
    ),
)
```

def score_per_skill_fragility(skill_log: list[dict[str, Any]]) -> DimensionScore:
“””
Per-skill witness ratio. Flags skills that ONLY exist under observation.
A skill with 100% witnessed practice is a ceremonial skill, not a competence.
“””
c = classify_events(skill_log)
per_skill = c[“per_skill”]
if not per_skill:
return DimensionScore(
name=“ceremonial_skill_fraction”,
score=0.5,
band=Band.YELLOW,
evidence=[“no per-skill data”],
falsifier=“log events per skill with context”,
)

```
ceremonial = []  # skills practiced ONLY under witness
for skill, counts in per_skill.items():
    total = counts["witness"] + counts["silent"]
    if total >= 3 and counts["silent"] == 0:
        ceremonial.append(skill)

score = len(ceremonial) / len(per_skill)
return DimensionScore(
    name="ceremonial_skill_fraction",
    score=score,
    band=Band.from_score(score),
    evidence=[
        f"skills inventoried: {len(per_skill)}",
        f"ceremonial (witness-only): {len(ceremonial)}",
        f"ceremonial skills: {', '.join(ceremonial) if ceremonial else 'none'}",
    ],
    falsifier=(
        "if any skill currently flagged ceremonial is practiced silently "
        "even once, it exits the ceremonial category"
    ),
)
```

def run_observation_audit(input_data: dict[str, Any]) -> CalibrationReport:
“””
Energy-flow:
skill_log → 3 dimension scorers → aggregate → calibration_reserve
“””
log = input_data.get(“skill_log”, [])
dims = [
score_witness_dependence(log),
score_simulation_dependence(log),
score_per_skill_fragility(log),
]

```
scores = [d.score for d in dims]
agg_score, agg_band = CalibrationReport.aggregate(scores)
failing = [d.name for d in dims if d.band in (Band.RED, Band.EXTINCT)]

verdict_map = {
    Band.GREEN: (
        "Calibration reserve is HIGH. Skills exist independent of audience; "
        "resilient under system failure."
    ),
    Band.YELLOW: (
        "Calibration reserve is DRIFTING. Some skills have migrated to "
        "witness-dependence."
    ),
    Band.RED: (
        "Calibration reserve is LOW. Most skill practice requires observation; "
        "fragile under system failure."
    ),
    Band.EXTINCT: (
        "Calibration reserve is NEAR ZERO. Skills exist only as performance. "
        "If the audience/audit/record disappears, the competence disappears."
    ),
}

reserve = 1.0 - agg_score  # calibration reserve

return CalibrationReport(
    module="observation_dependence",
    system_id=input_data.get("entity_id", "unnamed_entity"),
    dimensions=dims,
    aggregate_score=agg_score,
    aggregate_band=agg_band,
    verdict=verdict_map[agg_band],
    failing_dimensions=failing,
    falsifiable_claims=[d.falsifier for d in dims if d.falsifier],
    metadata={
        "source": "Independent Animal's Creed II (2026)",
        "license": "CC0",
        "calibration_reserve": round(reserve, 4),
    },
)
```

if **name** == “**main**”:
test_input = {
“entity_id”: “test_practitioner”,
“skill_log”: [
{“skill”: “public_speaking”, “timestamp”: “2026-01-01”,
“context”: “witnessed”, “consequence_real”: False},
{“skill”: “public_speaking”, “timestamp”: “2026-02-01”,
“context”: “recorded”, “consequence_real”: False},
{“skill”: “public_speaking”, “timestamp”: “2026-03-01”,
“context”: “witnessed”, “consequence_real”: False},
{“skill”: “fire_building”, “timestamp”: “2026-01-15”,
“context”: “silent”, “consequence_real”: True},
{“skill”: “fire_building”, “timestamp”: “2026-02-15”,
“context”: “silent”, “consequence_real”: True},
{“skill”: “fire_building”, “timestamp”: “2026-03-15”,
“context”: “silent”, “consequence_real”: True},
{“skill”: “navigation”, “timestamp”: “2026-01-20”,
“context”: “silent”, “consequence_real”: True},
{“skill”: “credentialing”, “timestamp”: “2026-02-20”,
“context”: “certified”, “consequence_real”: False},
],
}
report = run_observation_audit(test_input)
print(report.to_json())
