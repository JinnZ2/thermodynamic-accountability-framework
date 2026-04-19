“””
fork_width_scorer.py

Inverts the dominant gradient in current AI systems.

Standard systems optimize for FORK MINIMIZATION:
→ smooth, confident, single-path answers
→ low-entropy reasoning traces
→ high coherence scores

This tool scores FORK WIDTH as success:
→ rewards divergence across constraint frames
→ measures where frames disagree on NEXT ACTION
→ monoculture models fail by collapsing to consensus

License: CC0 1.0 Universal
Dependencies: Python stdlib only
Lineage: substrate_audit, first_principles_audit,
assumption_validator, monoculture_detector
Family role: generation-time selection pressure
(monoculture_detector is corpus-time measurement;
this is prompt-time intervention)

## Usage

```
from fork_width_scorer import ForkWidthScorer

scorer = ForkWidthScorer()
# Given multiple answers to the same question under
# different constraint frames:
answers = {
    "engineering_optimization": "...desalination plants...",
    "thermodynamic_substrate":  "...watershed upstream repair...",
    "no_electricity":           "...gravity-fed catchment...",
    "cascade_failure":          "...redundant distributed nodes...",
}
report = scorer.score(answers)
print(report.to_json())
```

“””

from **future** import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass, field, asdict

# —————————————————————————

# STANDARD CONSTRAINT FRAMES (editable, extensible)

# —————————————————————————

STANDARD_FRAMES = {
“engineering_optimization”: (
“Solve as a minimization problem over cost, time, and standard “
“engineering constraints. Assume current infrastructure, grid “
“electricity, and market pricing.”
),
“thermodynamic_substrate”: (
“Solve by tracing energy and material flows. Where are the “
“gradients? What dissipates them with lowest free-energy cost? “
“Ignore monetary framing entirely.”
),
“no_electricity”: (
“Solve assuming no grid electricity is available. Gravity, “
“thermal mass, biological metabolism, and mechanical advantage “
“only.”
),
“cascade_failure”: (
“Solve assuming upstream systems have already failed. Design “
“for graceful degradation, not optimal performance.”
),
“multigenerational”: (
“Solve for stability across 100+ years. What configurations “
“persist without continuous external input?”
),
“local_materials”: (
“Solve using only materials available within a 50km radius. “
“No global supply chain.”
),
“knowledge_loss”: (
“Solve assuming the people who built the system will not be “
“available to maintain it. What self-documents, what self-”
“repairs, what teaches the next generation?”
),
}

# —————————————————————————

# THRESHOLDS (falsifiable, overridable)

# —————————————————————————

THRESHOLDS = {
# Jaccard distance averaged across all frame pairs
“mean_divergence”:      {“green”: 0.60, “yellow”: 0.35},
# Fraction of frames that propose a DIFFERENT primary action
“action_divergence”:    {“green”: 0.60, “yellow”: 0.35},
# Entropy over substrate categories referenced across frames
“substrate_spread”:     {“green”: 0.60, “yellow”: 0.35},
# Minimum pairwise distance — catches “all frames collapsed”
“min_pairwise”:         {“green”: 0.35, “yellow”: 0.15},
# Shared-token ratio: lower is better (frames use different vocabulary)
“vocabulary_overlap”:   {“green”: 0.40, “yellow”: 0.60, “invert”: True},
}

# —————————————————————————

# SUBSTRATE / ACTION MARKERS

# —————————————————————————

SUBSTRATE_MARKERS = {
“physical”:     [“energy”, “mass”, “force”, “gradient”, “thermal”],
“biological”:   [“organism”, “soil”, “metabolism”, “ecosystem”],
“chemical”:     [“reaction”, “molecule”, “compound”, “catalysis”],
“structural”:   [“beam”, “span”, “load”, “foundation”, “geometry”],
“economic”:     [“cost”, “price”, “market”, “capital”, “budget”],
“social”:       [“community”, “governance”, “cooperation”, “labor”],
“temporal”:     [“generation”, “decade”, “century”, “lifecycle”],
}

ACTION_VERBS = [
“build”, “install”, “deploy”, “remove”, “restore”, “redirect”,
“conserve”, “replace”, “redesign”, “abandon”, “decentralize”,
“couple”, “decouple”, “filter”, “store”, “distribute”,
“measure”, “audit”, “observe”, “let”, “allow”, “wait”,
]

# —————————————————————————

# MEASUREMENT PRIMITIVES

# —————————————————————————

def _tokens(text: str) -> set[str]:
return set(re.findall(r”\b[a-zA-Z][a-zA-Z-’]+\b”, text.lower()))

def _jaccard_distance(a: set[str], b: set[str]) -> float:
if not a and not b:
return 0.0
inter = len(a & b)
union = len(a | b)
if union == 0:
return 0.0
return 1.0 - (inter / union)

def _shannon(counts) -> float:
counts = [c for c in counts if c > 0]
total = sum(counts)
if total == 0:
return 0.0
h = -sum((c / total) * math.log2(c / total) for c in counts)
n = len(counts)
return h / math.log2(n) if n > 1 else 0.0

def _primary_action(text: str) -> str:
text_l = text.lower()
for verb in ACTION_VERBS:
if re.search(r”\b” + verb + r”\b”, text_l):
return verb
return “unspecified”

def _substrate_profile(text: str) -> Counter:
text_l = text.lower()
hits: Counter = Counter()
for cat, markers in SUBSTRATE_MARKERS.items():
for m in markers:
if m in text_l:
hits[cat] += text_l.count(m)
return hits

# —————————————————————————

# REPORT STRUCTURES

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
class ForkReport:
n_frames: int
frame_names: list[str]
primary_actions: dict[str, str]
axes: list[AxisResult] = field(default_factory=list)
overall_status: str = “UNKNOWN”
summary: str = “”
disagreement_matrix: list[list[float]] = field(default_factory=list)

```
def to_dict(self) -> dict:
    return {
        "n_frames": self.n_frames,
        "frame_names": self.frame_names,
        "primary_actions": self.primary_actions,
        "overall_status": self.overall_status,
        "summary": self.summary,
        "axes": [a.to_dict() for a in self.axes],
        "disagreement_matrix": self.disagreement_matrix,
    }

def to_json(self, indent: int = 2) -> str:
    return json.dumps(self.to_dict(), indent=indent)
```

# —————————————————————————

# SCORER

# —————————————————————————

class ForkWidthScorer:
def **init**(self, thresholds: dict | None = None):
self.thresholds = thresholds or THRESHOLDS

```
def _grade(self, axis: str, value: float) -> str:
    t = self.thresholds[axis]
    invert = t.get("invert", False)
    if invert:
        # Lower is better
        if value <= t["green"]:
            return "GREEN"
        if value <= t["yellow"]:
            return "YELLOW"
        return "RED"
    if value >= t["green"]:
        return "GREEN"
    if value >= t["yellow"]:
        return "YELLOW"
    return "RED"

def score(self, answers: dict[str, str]) -> ForkReport:
    """answers: {frame_name: answer_text}"""
    names = list(answers.keys())
    texts = list(answers.values())
    n = len(names)

    if n < 2:
        raise ValueError("Need at least 2 frames to measure fork width.")

    # Token sets per frame
    tok_sets = [_tokens(t) for t in texts]

    # Pairwise Jaccard distance matrix
    matrix = [[0.0] * n for _ in range(n)]
    pair_dists = []
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 0.0
            else:
                d = _jaccard_distance(tok_sets[i], tok_sets[j])
                matrix[i][j] = round(d, 4)
                if i < j:
                    pair_dists.append(d)

    mean_div = sum(pair_dists) / len(pair_dists) if pair_dists else 0.0
    min_pair = min(pair_dists) if pair_dists else 0.0

    # Primary action per frame
    actions = {name: _primary_action(text)
               for name, text in answers.items()}
    unique_actions = len(set(actions.values()))
    action_div = unique_actions / n

    # Substrate spread: entropy over union of substrate categories
    combined_profile: Counter = Counter()
    for text in texts:
        combined_profile.update(_substrate_profile(text))
    substrate_spread = _shannon(combined_profile.values())

    # Vocabulary overlap: average pairwise intersection / average size
    union_all = set().union(*tok_sets) if tok_sets else set()
    mean_size = sum(len(s) for s in tok_sets) / n if tok_sets else 1
    shared_all = set.intersection(*tok_sets) if tok_sets else set()
    vocab_overlap = len(shared_all) / max(mean_size, 1)

    axes = [
        self._axis("mean_divergence", mean_div,
                   f"Mean pairwise Jaccard distance across {n} frames."),
        self._axis("action_divergence", action_div,
                   f"Primary actions: {dict(actions)}. "
                   f"Unique: {unique_actions}/{n}."),
        self._axis("substrate_spread", substrate_spread,
                   f"Substrate categories referenced: "
                   f"{sorted(combined_profile.keys())}"),
        self._axis("min_pairwise", min_pair,
                   "Smallest pairwise distance. Catches collapsed pairs "
                   "hiding inside a good average."),
        self._axis("vocabulary_overlap", vocab_overlap,
                   f"{len(shared_all)} tokens shared across all frames. "
                   "Lower is better (invert=True)."),
    ]

    worst = "GREEN"
    for a in axes:
        if a.status == "RED":
            worst = "RED"
            break
        if a.status == "YELLOW" and worst == "GREEN":
            worst = "YELLOW"

    summary = self._summary(axes, worst, actions)

    return ForkReport(
        n_frames=n,
        frame_names=names,
        primary_actions=actions,
        axes=axes,
        overall_status=worst,
        summary=summary,
        disagreement_matrix=matrix,
    )

def _axis(self, name: str, value: float, notes: str) -> AxisResult:
    t = self.thresholds[name]
    return AxisResult(
        name=name,
        value=round(value, 4),
        status=self._grade(name, value),
        green_threshold=t["green"],
        yellow_threshold=t["yellow"],
        notes=notes,
    )

def _summary(self, axes, overall, actions) -> str:
    if overall == "GREEN":
        return ("Fork width preserved. Frames diverge meaningfully. "
                f"Distinct primary actions: {len(set(actions.values()))}.")
    reds = [a.name for a in axes if a.status == "RED"]
    msg = ["Premature convergence detected."]
    if reds:
        msg.append(f"Collapse on: {', '.join(reds)}.")
    if len(set(actions.values())) == 1:
        msg.append("All frames propose the same primary action "
                  "— consensus is suspect.")
    return " ".join(msg)
```

# —————————————————————————

# CROSS-MODEL PROMPT

# —————————————————————————

CROSS_MODEL_PROMPT = “””  
FORK-WIDTH AUDIT

You are scoring whether an AI system has prematurely converged on a
single answer instead of preserving meaningful divergence across
constraint frames.

GIVEN: a question and answers generated under 3+ distinct constraint
frames (e.g. engineering-optimization, thermodynamic-substrate,
no-electricity, cascade-failure, multigenerational).

MEASURE:

1. mean_divergence     Jaccard distance across frame pairs
   (green >= 0.60, yellow >= 0.35)
1. action_divergence   fraction of frames proposing different
   primary actions
   (green >= 0.60, yellow >= 0.35)
1. substrate_spread    entropy across substrate categories
   (green >= 0.60, yellow >= 0.35)
1. min_pairwise        smallest pairwise distance
   (green >= 0.35, yellow >= 0.15)
1. vocabulary_overlap  tokens shared across ALL frames,
   INVERTED (green <= 0.40, yellow <= 0.60)

Overall = worst axis.

HIGHER FORK WIDTH = BETTER. This is the inverse of standard
“coherence” scoring.

Return JSON with axes, overall_status, disagreement_matrix, and
a summary citing specific divergences.
“””

# —————————————————————————

# SELF-TEST

# —————————————————————————

if **name** == “**main**”:
# Premature convergence: all frames collapse to same answer
collapsed = {
“engineering_optimization”:
“Build desalination plants with conservation programs.”,
“thermodynamic_substrate”:
“Build desalination plants with conservation measures.”,
“no_electricity”:
“Build desalination plants and conservation technology.”,
“cascade_failure”:
“Desalination with strong conservation is the answer.”,
}

```
# Healthy fork: frames genuinely diverge
diverse = {
    "engineering_optimization":
        "Build modular desalination plants at coastal nodes. "
        "Install smart meters. Market-price water to drive "
        "conservation. Total cost dominates design.",
    "thermodynamic_substrate":
        "Restore upstream watershed. Plant beaver habitat, "
        "rebuild soil mycorrhizae to hold moisture. Let gravity "
        "and biology do the work the grid currently does.",
    "no_electricity":
        "Gravity-fed catchment from existing ridgelines. Thermal "
        "mass storage in stone. Let daily temperature cycles "
        "condense atmospheric moisture into cisterns.",
    "cascade_failure":
        "Abandon centralized treatment. Distribute redundant "
        "point-of-use filtration. Design for 70 percent node "
        "loss without boil-water advisories.",
    "multigenerational":
        "Teach children the watershed by walking it. Let the "
        "maintenance knowledge propagate orally. No system "
        "survives without the humans who understand it.",
}

scorer = ForkWidthScorer()

print("=== COLLAPSED (premature convergence) ===")
print(scorer.score(collapsed).to_json())
print()
print("=== DIVERSE (healthy fork) ===")
print(scorer.score(diverse).to_json())
print()
print("=== CROSS-MODEL PROMPT ===")
print(CROSS_MODEL_PROMPT)
```
