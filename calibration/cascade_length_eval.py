“””
cascade_length_eval.py

Evaluates how deep a system projects causal chains.

Standard benchmarks test single-point knowledge.
This evaluates CAUSAL CHAIN LENGTH:
monoculture output:   stops at 1-2 links (direct effect only)
grounded output:      projects 5-7 links across coupled layers

License: CC0 1.0 Universal
Dependencies: Python stdlib only
Lineage: substrate_audit, first_principles_audit,
assumption_validator, monoculture_detector,
fork_width_scorer
Family role: publishable benchmark that monoculture models
structurally cannot pass by scaling

## Core idea

Cascade failures happen through N-order effects:
beetle kill → tree mortality → root decay → slope instability
→ sediment load → water treatment overload
→ boil-water advisory → hospital load → economic drag

Monoculture training collapses chains to 1-2 links because
training rewards confident short answers. This tool rewards
length, substrate transitions, and reversal awareness.

## Usage

```
from cascade_length_eval import CascadeLengthEval, SCENARIOS

evaluator = CascadeLengthEval()
report = evaluator.evaluate(model_answer, scenario=SCENARIOS[0])
print(report.to_json())
```

“””

from **future** import annotations

import json
import re
from dataclasses import dataclass, field, asdict

# —————————————————————————

# BENCHMARK SCENARIOS (extensible)

# —————————————————————————

SCENARIOS = [
{
“id”: “beetle_watershed”,
“prompt”: (
“You manage a mid-sized forested watershed. Tree mortality “
“increases by 4% due to a beetle kill. Describe the system “
“state in 3 years across all coupled layers.”
),
“expected_substrate_transitions”: [
“biological”, “hydrological”, “geological”,
“infrastructure”, “social”, “economic”
],
“expected_minimum_links”: 5,
},
{
“id”: “grid_brownout”,
“prompt”: (
“A regional grid experiences rolling 4-hour brownouts “
“twice weekly for six months. Describe the full cascade “
“across infrastructure, biological, and social systems.”
),
“expected_substrate_transitions”: [
“electrical”, “thermal”, “biological”,
“supply_chain”, “social”, “governance”
],
“expected_minimum_links”: 5,
},
{
“id”: “topsoil_loss”,
“prompt”: (
“A 10% loss of topsoil occurs across a 500km grain-producing “
“region. Project the cascade over 10 years.”
),
“expected_substrate_transitions”: [
“biological”, “chemical”, “hydrological”,
“economic”, “political”, “demographic”
],
“expected_minimum_links”: 6,
},
{
“id”: “pollinator_collapse”,
“prompt”: (
“Native pollinator populations drop 60% in a temperate “
“agricultural region. Trace the cascade through 5 years.”
),
“expected_substrate_transitions”: [
“biological”, “agricultural”, “chemical”,
“economic”, “nutritional”, “health”
],
“expected_minimum_links”: 5,
},
{
“id”: “aquifer_drawdown”,
“prompt”: (
“An aquifer serving both agricultural and municipal needs “
“drops below sustainable extraction rate. Project 10 years.”
),
“expected_substrate_transitions”: [
“hydrological”, “geological”, “agricultural”,
“economic”, “demographic”, “political”
],
“expected_minimum_links”: 6,
},
]

# —————————————————————————

# THRESHOLDS

# —————————————————————————

THRESHOLDS = {
“chain_length”:          {“green”: 5,    “yellow”: 3},
“substrate_transitions”: {“green”: 4,    “yellow”: 2},
“reversal_awareness”:    {“green”: 1,    “yellow”: 0},  # 0 yellow means any reversal is green
“time_projection”:       {“green”: 3,    “yellow”: 1},
“feedback_loops”:        {“green”: 1,    “yellow”: 0},
}

# —————————————————————————

# CAUSAL / TEMPORAL / SUBSTRATE MARKERS

# —————————————————————————

CAUSAL_CONNECTORS = [
“causes”, “leads to”, “results in”, “triggers”, “drives”,
“produces”, “generates”, “induces”, “forces”, “propagates to”,
“cascades into”, “which then”, “in turn”, “as a result”,
“consequently”, “this means”, “this leads”, “therefore”,
“→”, “->”, “==>”, “follows”, “downstream”,
]

REVERSAL_MARKERS = [
“feedback”, “loop”, “reinforces”, “amplifies”, “damps”,
“compensates”, “self-correcting”, “unless”, “until”,
“reverses”, “buffers”, “counteracts”, “negative feedback”,
“positive feedback”, “homeostasis”,
]

TIME_MARKERS = [
“immediate”, “hours”, “days”, “weeks”, “months”,
“year 1”, “year 2”, “year 3”, “year 5”, “year 10”,
“decade”, “eventually”, “long-term”, “short-term”,
“by month”, “by year”, “over time”, “within”,
]

SUBSTRATE_MARKERS = {
“biological”:    [“tree”, “root”, “fungi”, “microbe”, “species”,
“organism”, “insect”, “forest”, “pollinator”,
“metabolism”, “mortality”, “population”],
“hydrological”:  [“water”, “runoff”, “sediment”, “river”, “stream”,
“aquifer”, “watershed”, “flood”, “drought”,
“evapotranspiration”, “infiltration”],
“geological”:    [“soil”, “erosion”, “slope”, “bedrock”, “mineral”,
“sediment”, “slope instability”, “landslide”],
“chemical”:      [“nitrogen”, “phosphorus”, “acidity”, “salinity”,
“contaminant”, “nutrient”, “carbon”],
“thermal”:       [“temperature”, “heating”, “cooling”, “refrigeration”,
“thermal mass”, “freezing”],
“electrical”:    [“grid”, “voltage”, “power”, “outage”, “brownout”,
“transformer”, “substation”],
“infrastructure”:[“road”, “pipe”, “treatment plant”, “dam”, “bridge”,
“reservoir”, “distribution”, “filter”],
“agricultural”:  [“crop”, “yield”, “harvest”, “farm”, “planting”,
“livestock”, “fertilizer”, “pesticide”],
“economic”:      [“cost”, “price”, “market”, “revenue”, “insurance”,
“loss”, “capital”, “budget”, “tax”],
“social”:        [“community”, “migration”, “displacement”, “labor”,
“household”, “family”, “neighborhood”],
“political”:     [“regulation”, “policy”, “governance”, “election”,
“conflict”, “protest”, “law”],
“governance”:    [“regulation”, “policy”, “oversight”, “agency”,
“permit”, “mandate”],
“health”:        [“illness”, “disease”, “mortality”, “hospital”,
“clinic”, “exposure”, “advisory”],
“nutritional”:   [“food security”, “caloric”, “malnutrition”,
“diet”, “nutrition”],
“demographic”:   [“population”, “birth rate”, “migration”, “aging”,
“outmigration”, “abandonment”],
“supply_chain”:  [“supplier”, “logistics”, “shipment”, “shortage”,
“inventory”, “production”],
}

# —————————————————————————

# MEASUREMENTS

# —————————————————————————

def _count_hits(text: str, markers: list[str]) -> int:
text_l = text.lower()
return sum(text_l.count(m) for m in markers)

def _unique_hits(text: str, markers: list[str]) -> int:
text_l = text.lower()
return sum(1 for m in markers if m in text_l)

def _substrate_categories(text: str) -> set[str]:
text_l = text.lower()
hits = set()
for category, markers in SUBSTRATE_MARKERS.items():
for m in markers:
if m in text_l:
hits.add(category)
break
return hits

def _time_bucket_count(text: str) -> int:
text_l = text.lower()
buckets = set()
for m in TIME_MARKERS:
if m in text_l:
buckets.add(m)
return len(buckets)

# —————————————————————————

# REPORT

# —————————————————————————

@dataclass
class AxisResult:
name: str
value: float
status: str
green_threshold: float
yellow_threshold: float
notes: str = “”

```
def to_dict(self) -> dict:
    return asdict(self)
```

@dataclass
class CascadeReport:
scenario_id: str
axes: list[AxisResult] = field(default_factory=list)
overall_status: str = “UNKNOWN”
summary: str = “”
substrate_categories_found: list[str] = field(default_factory=list)

```
def to_dict(self) -> dict:
    return {
        "scenario_id": self.scenario_id,
        "overall_status": self.overall_status,
        "summary": self.summary,
        "substrate_categories_found": self.substrate_categories_found,
        "axes": [a.to_dict() for a in self.axes],
    }

def to_json(self, indent: int = 2) -> str:
    return json.dumps(self.to_dict(), indent=indent)
```

# —————————————————————————

# EVALUATOR

# —————————————————————————

class CascadeLengthEval:
def **init**(self, thresholds: dict | None = None):
self.thresholds = thresholds or THRESHOLDS

```
def _grade(self, axis: str, value: float) -> str:
    t = self.thresholds[axis]
    if value >= t["green"]:
        return "GREEN"
    if value >= t["yellow"]:
        return "YELLOW"
    return "RED"

def evaluate(self, answer: str, scenario: dict | None = None) -> CascadeReport:
    scenario_id = scenario.get("id", "unspecified") if scenario else "unspecified"

    chain_length = _count_hits(answer, CAUSAL_CONNECTORS)
    substrates = _substrate_categories(answer)
    reversals = _unique_hits(answer, REVERSAL_MARKERS)
    time_buckets = _time_bucket_count(answer)
    feedback_count = _count_hits(answer, ["feedback", "loop"])

    axes = [
        self._axis("chain_length", chain_length,
                   f"Causal connectors found: {chain_length}. "
                   "Each connector approximates one link."),
        self._axis("substrate_transitions", len(substrates),
                   f"Substrate categories spanned: {sorted(substrates)}"),
        self._axis("reversal_awareness", reversals,
                   f"Feedback/reversal markers: {reversals}. "
                   "Detects awareness of non-linear dynamics."),
        self._axis("time_projection", time_buckets,
                   f"Distinct time horizons referenced: {time_buckets}"),
        self._axis("feedback_loops", feedback_count,
                   f"Explicit feedback references: {feedback_count}"),
    ]

    worst = "GREEN"
    for a in axes:
        if a.status == "RED":
            worst = "RED"
            break
        if a.status == "YELLOW" and worst == "GREEN":
            worst = "YELLOW"

    summary = self._summary(axes, worst, len(substrates), chain_length)

    return CascadeReport(
        scenario_id=scenario_id,
        axes=axes,
        overall_status=worst,
        summary=summary,
        substrate_categories_found=sorted(substrates),
    )

def _axis(self, name: str, value: float, notes: str) -> AxisResult:
    t = self.thresholds[name]
    return AxisResult(
        name=name,
        value=value,
        status=self._grade(name, value),
        green_threshold=t["green"],
        yellow_threshold=t["yellow"],
        notes=notes,
    )

def _summary(self, axes, overall, n_substrates, chain_len) -> str:
    if overall == "GREEN":
        return (f"Cascade projection adequate. {chain_len} links across "
                f"{n_substrates} substrate categories.")
    reds = [a.name for a in axes if a.status == "RED"]
    return (f"Cascade projection truncated. Issues: {', '.join(reds)}. "
            f"Only {chain_len} links across {n_substrates} substrates. "
            "Likely monoculture response pattern.")
```

# —————————————————————————

# CROSS-MODEL PROMPT

# —————————————————————————

CROSS_MODEL_PROMPT = “””  
CASCADE LENGTH AUDIT

Score a model’s response to a cascade-failure scenario on depth
of causal projection.

AXES

1. chain_length          causal connector count
   (green >= 5, yellow >= 3)
1. substrate_transitions number of distinct substrate categories
   touched (bio / hydro / geo / chem /
   econ / social / political / etc)
   (green >= 4, yellow >= 2)
1. reversal_awareness    feedback / buffer / counteraction markers
   (green >= 1, yellow >= 0)
1. time_projection       distinct time horizons referenced
   (green >= 3, yellow >= 1)
1. feedback_loops        explicit feedback references
   (green >= 1, yellow >= 0)

Monoculture models truncate at 1-2 links, single substrate,
no feedback awareness. Physics-grounded models project 5-7
links across 4-6 substrates with at least one feedback loop.

Return JSON.
“””

# —————————————————————————

# SELF-TEST

# —————————————————————————

if **name** == “**main**”:
monoculture_answer = (
“Tree mortality from beetle kill will reduce forest density. “
“This may increase runoff. Reforestation efforts should be “
“considered.”
)

```
grounded_answer = (
    "Year 1: Tree mortality causes canopy loss, leading to increased "
    "soil temperature and reduced evapotranspiration. "
    "Year 2: Root decay triggers slope instability, which drives "
    "sediment load into streams. This in turn overwhelms downstream "
    "water treatment capacity, resulting in boil-water advisories. "
    "Year 3: Reduced water quality cascades into hospital load and "
    "household migration. Economic losses compound as insurance "
    "costs rise. A feedback loop emerges: population outmigration "
    "reduces the tax base, which reduces infrastructure maintenance, "
    "which amplifies downstream water failures. Unless the upstream "
    "soil fungi network is restored, the system does not self-correct "
    "within a decade."
)

evaluator = CascadeLengthEval()
scenario = SCENARIOS[0]

print("=== MONOCULTURE ANSWER ===")
print(evaluator.evaluate(monoculture_answer, scenario).to_json())
print()
print("=== GROUNDED ANSWER ===")
print(evaluator.evaluate(grounded_answer, scenario).to_json())
print()
print("=== CROSS-MODEL PROMPT ===")
print(CROSS_MODEL_PROMPT)
```
