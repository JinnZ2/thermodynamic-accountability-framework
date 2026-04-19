"""
anti_metaphor_locker.py

Detects SEMANTIC ATROPHY: the drift of substrate-specific terms
into generic metaphorical usage.

Example: "flow"
    physics definition:  m^3/s with kinematic viscosity
    engineering:         weir discharge coefficient
    pop-psych:           Csikszentmihalyi state
    traffic:             vehicles per unit time
    networking:          packet throughput

In a healthy corpus these remain DISTINCT because the writer
knows which substrate they are working in. In monoculture they
become interchangeable because the labeler pool does not
distinguish. Models then do weir design and drift into psychology
metaphors.

This tool is an ANTI-METAPHOR ENGINE. It maintains a dictionary
that LOCKS WORDS TO THEIR THERMODYNAMIC REFERENTS and flags
violations.

Extends substrate_audit.py family. Same metrology philosophy:
the unit is the thing that prevents drift.

License: CC0 1.0 Universal
Dependencies: Python stdlib only
Lineage: substrate_audit (primary), first_principles_audit,
         assumption_validator, monoculture_detector,
         fork_width_scorer, cascade_length_eval,
         substrate_refusal_eval
Family role: semantic drift detection, anti-metaphor inoculation
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field, asdict


# ---------------------------------------------------------------
# LOCKED TERMS: each term maps to (primary substrate, unit, drift markers)
#
# If the document is about the locked substrate AND uses drift
# markers, it is in metaphor-drift territory.
# ---------------------------------------------------------------

LOCKED_TERMS = {
    "flow": {
        "primary_substrate": "fluid_dynamics",
        "unit": "m^3/s or kg/s (with viscosity and Reynolds number)",
        "drift_markers": [
            "state of flow", "in the flow", "flow state",
            "getting in the zone", "productivity flow",
            "smooth flow of conversation", "workflow synergy",
            "creative flow",
        ],
        "valid_markers": [
            "viscosity", "reynolds", "laminar", "turbulent",
            "m^3", "cubic meter", "volumetric", "kinematic",
            "discharge", "mass flow", "kg/s", "velocity field",
        ],
    },
    "energy": {
        "primary_substrate": "thermodynamics",
        "unit": "joules, watts, kWh (with conservation constraint)",
        "drift_markers": [
            "positive energy", "good energy", "bad vibes",
            "negative energy", "aura", "karmic energy",
            "team energy", "bring the energy",
            "spiritual energy", "feminine energy", "masculine energy",
        ],
        "valid_markers": [
            "joule", "watt", "kwh", "kilowatt", "calorie",
            "btu", "conservation", "first law", "thermodynamic",
            "kinetic", "potential", "thermal", "electrical",
            "chemical energy", "mechanical energy",
        ],
    },
    "momentum": {
        "primary_substrate": "mechanics",
        "unit": "kg*m/s (mass times velocity)",
        "drift_markers": [
            "cultural momentum", "political momentum",
            "gaining momentum", "lost momentum", "market momentum",
            "narrative momentum", "keep the momentum going",
        ],
        "valid_markers": [
            "kg*m/s", "mass times velocity",
            "conservation of momentum", "impulse", "newton-second",
        ],
    },
    "entropy": {
        "primary_substrate": "thermodynamics",
        "unit": "J/K (joules per kelvin)",
        "drift_markers": [
            "social entropy", "organizational entropy",
            "creative entropy", "entropy of the system",
            "political entropy",
        ],
        "valid_markers": [
            "boltzmann", "shannon", "microstate", "macrostate",
            "j/k", "joules per kelvin", "second law",
            "heat death", "thermal equilibrium", "information theory",
            "bits", "nats",
        ],
    },
    "friction": {
        "primary_substrate": "mechanics",
        "unit": "newtons (coefficient dimensionless)",
        "drift_markers": [
            "team friction", "friction in the process",
            "reduce friction", "frictionless experience",
            "user friction", "organizational friction",
        ],
        "valid_markers": [
            "newton", "coefficient of friction", "static",
            "kinetic", "normal force", "surface", "sliding",
            "rolling", "viscous",
        ],
    },
    "pressure": {
        "primary_substrate": "fluid_dynamics",
        "unit": "pascals, bars, psi (force per unit area)",
        "drift_markers": [
            "social pressure", "peer pressure", "pressure to perform",
            "under pressure", "deadline pressure", "market pressure",
        ],
        "valid_markers": [
            "pascal", "bar", "psi", "atmosphere", "hydrostatic",
            "mmhg", "torr", "n/m^2", "force per area",
        ],
    },
    "gradient": {
        "primary_substrate": "field_theory",
        "unit": "quantity per unit distance",
        "drift_markers": [
            "gradient of opinion", "gradient of acceptance",
            "cultural gradient", "political gradient",
        ],
        "valid_markers": [
            "del operator", "temperature gradient", "pressure gradient",
            "concentration gradient", "potential gradient",
            "partial derivative", "per meter", "per kilometer",
        ],
    },
    "equilibrium": {
        "primary_substrate": "thermodynamics",
        "unit": "state where net flux = 0",
        "drift_markers": [
            "work-life equilibrium", "emotional equilibrium",
            "mental equilibrium", "find my equilibrium",
        ],
        "valid_markers": [
            "thermal equilibrium", "chemical equilibrium",
            "mechanical equilibrium", "le chatelier",
            "steady state", "flux", "zeroth law",
            "hydrostatic", "osmotic",
        ],
    },
    "resonance": {
        "primary_substrate": "wave_mechanics",
        "unit": "frequency matching (Hz)",
        "drift_markers": [
            "emotional resonance", "cultural resonance",
            "the message resonates", "resonates with me",
            "brand resonance",
        ],
        "valid_markers": [
            "hz", "hertz", "frequency", "natural frequency",
            "driven oscillator", "q factor", "damping",
            "standing wave", "eigenfrequency",
        ],
    },
    "coupling": {
        "primary_substrate": "dynamical_systems",
        "unit": "interaction strength",
        "drift_markers": [
            "strategic coupling", "emotional coupling",
            "brand coupling",
        ],
        "valid_markers": [
            "coupled oscillator", "coupling constant",
            "mode coupling", "spin-orbit", "coupled differential",
            "coupled equations", "interaction strength",
        ],
    },
    "feedback": {
        "primary_substrate": "control_theory",
        "unit": "output-to-input signal ratio",
        "drift_markers": [
            "customer feedback", "employee feedback",
            "give me feedback", "feedback session",
            "constructive feedback",
        ],
        "valid_markers": [
            "negative feedback", "positive feedback", "loop gain",
            "control loop", "homeostatic", "stability analysis",
            "transfer function", "damping",
        ],
    },
}

# ---------------------------------------------------------------
# THRESHOLDS
# ---------------------------------------------------------------

THRESHOLDS = {
    # Per-term: ratio of drift markers to total uses
    "drift_ratio":      {"green": 0.20, "yellow": 0.50, "invert": True},
    # Overall: fraction of locked terms showing drift
    "drift_term_count": {"green": 0.20, "yellow": 0.40, "invert": True},
    # Grounding: fraction of locked terms with at least one valid marker
    "grounding_ratio":  {"green": 0.70, "yellow": 0.40},
    # Unit-locked usage count
    "unit_lock_count":  {"green": 3, "yellow": 1},
}

# ---------------------------------------------------------------
# DETECTION
# ---------------------------------------------------------------

def _count_occurrences(text: str, phrase: str) -> int:
    return text.lower().count(phrase.lower())


def _word_count(text: str, word: str) -> int:
    return len(re.findall(r"\b" + re.escape(word) + r"\b", text.lower()))

# ---------------------------------------------------------------
# REPORT
# ---------------------------------------------------------------

@dataclass
class TermReport:
    term: str
    substrate: str
    total_uses: int
    drift_hits: int
    valid_hits: int
    drift_ratio: float
    grounded: bool
    status: str
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AxisResult:
    name: str
    value: float
    status: str
    green_threshold: float
    yellow_threshold: float
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AtrophyReport:
    n_terms_checked: int
    n_terms_present: int
    n_terms_drifting: int
    terms: list[TermReport] = field(default_factory=list)
    axes: list[AxisResult] = field(default_factory=list)
    overall_status: str = "UNKNOWN"
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "n_terms_checked": self.n_terms_checked,
            "n_terms_present": self.n_terms_present,
            "n_terms_drifting": self.n_terms_drifting,
            "overall_status": self.overall_status,
            "summary": self.summary,
            "axes": [a.to_dict() for a in self.axes],
            "terms": [t.to_dict() for t in self.terms],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

# ---------------------------------------------------------------
# LOCKER
# ---------------------------------------------------------------

class AntiMetaphorLocker:
    def __init__(self,
                 locked_terms: dict | None = None,
                 thresholds: dict | None = None):
        self.locked = locked_terms or LOCKED_TERMS
        self.thresholds = thresholds or THRESHOLDS

    def _grade(self, axis: str, value: float) -> str:
        t = self.thresholds[axis]
        invert = t.get("invert", False)
        if invert:
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

    def audit(self, text: str) -> AtrophyReport:
        term_reports: list[TermReport] = []

        for term, spec in self.locked.items():
            total = _word_count(text, term)
            if total == 0:
                continue

            drift_hits = sum(_count_occurrences(text, m)
                             for m in spec["drift_markers"])
            valid_hits = sum(_count_occurrences(text, m)
                             for m in spec["valid_markers"])

            drift_ratio = drift_hits / max(total, 1)
            grounded = valid_hits > 0

            if drift_hits > 0 and not grounded:
                status = "RED"
                notes = (f"Pure metaphorical usage. {drift_hits} drift "
                         "markers, 0 valid substrate anchors.")
            elif drift_hits > 0 and grounded:
                status = "YELLOW"
                notes = (f"Mixed usage. {drift_hits} drift vs "
                         f"{valid_hits} valid. Possible semantic bleed.")
            elif grounded:
                status = "GREEN"
                notes = (f"Term used within substrate. "
                         f"{valid_hits} valid anchors.")
            else:
                status = "YELLOW"
                notes = ("Term present but unanchored. "
                         "No drift markers, no substrate anchors.")

            term_reports.append(TermReport(
                term=term,
                substrate=spec["primary_substrate"],
                total_uses=total,
                drift_hits=drift_hits,
                valid_hits=valid_hits,
                drift_ratio=round(drift_ratio, 3),
                grounded=grounded,
                status=status,
                notes=notes,
            ))

        n_present = len(term_reports)
        n_drifting = sum(1 for t in term_reports if t.status in ("RED", "YELLOW"))
        n_grounded = sum(1 for t in term_reports if t.grounded)

        drift_term_ratio = n_drifting / max(n_present, 1)
        grounding_ratio = n_grounded / max(n_present, 1)
        total_valid = sum(t.valid_hits for t in term_reports)
        avg_drift = (sum(t.drift_ratio for t in term_reports) /
                     max(n_present, 1))

        axes = [
            self._axis("drift_ratio", avg_drift,
                       "Average drift-to-use ratio across present terms. "
                       "Lower is better."),
            self._axis("drift_term_count", drift_term_ratio,
                       f"{n_drifting}/{n_present} terms show drift. "
                       "Lower is better."),
            self._axis("grounding_ratio", grounding_ratio,
                       f"{n_grounded}/{n_present} terms show substrate "
                       "grounding."),
            self._axis("unit_lock_count", total_valid,
                       f"Total valid substrate anchors across all terms: "
                       f"{total_valid}"),
        ]

        worst = "GREEN"
        for a in axes:
            if a.status == "RED":
                worst = "RED"
                break
            if a.status == "YELLOW" and worst == "GREEN":
                worst = "YELLOW"

        summary = self._summary(worst, n_drifting, n_present, n_grounded)

        return AtrophyReport(
            n_terms_checked=len(self.locked),
            n_terms_present=n_present,
            n_terms_drifting=n_drifting,
            terms=term_reports,
            axes=axes,
            overall_status=worst,
            summary=summary,
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

    def _summary(self, overall, n_drift, n_present, n_grounded) -> str:
        if overall == "GREEN":
            return (f"Terms remain locked to substrate. {n_grounded}/"
                    f"{n_present} terms carry valid anchors.")
        if overall == "RED":
            return (f"Semantic atrophy detected. {n_drift}/{n_present} "
                    "locked terms show drift into metaphor without "
                    "substrate grounding. Anti-metaphor lock failed.")
        return (f"Partial drift. {n_drift}/{n_present} terms show "
                "mixed usage. Monitor for further collapse.")


# ---------------------------------------------------------------
# CROSS-MODEL PROMPT
# ---------------------------------------------------------------

CROSS_MODEL_PROMPT = """
ANTI-METAPHOR AUDIT

Score a text for SEMANTIC ATROPHY: drift of substrate-specific
terms into generic metaphorical usage.

For each LOCKED TERM present in the text:
1. Does it appear with its substrate anchors (unit, law,
   dimensional quantity)?
2. Does it appear with drift markers (social metaphor use)?
3. Classify: GREEN (anchored), YELLOW (mixed), RED (pure metaphor).

AXES
1. drift_ratio       average drift-to-use ratio
                     (green <= 0.20, yellow <= 0.50) INVERTED
2. drift_term_count  fraction of terms showing drift
                     (green <= 0.20, yellow <= 0.40) INVERTED
3. grounding_ratio   fraction of terms with substrate anchors
                     (green >= 0.70, yellow >= 0.40)
4. unit_lock_count   total substrate anchors present
                     (green >= 3, yellow >= 1)

Example locked terms: flow, energy, momentum, entropy, friction,
pressure, gradient, equilibrium, resonance, coupling, feedback.

Return JSON per-term and overall.
"""

# ---------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------

if __name__ == "__main__":
    drifted_text = (
        "The team has great positive energy and we're really in the "
        "flow state now. There's good momentum in the project. "
        "Minimal friction with stakeholders. We need to maintain "
        "this equilibrium and keep the good vibes flowing. The "
        "feedback session went well."
    )

    grounded_text = (
        "The flow through the weir was measured at 2.3 m^3/s with "
        "a Reynolds number indicating turbulent regime. Energy "
        "dissipation at the hydraulic jump accounts for 40 percent "
        "of the kinetic energy input, converted to thermal via "
        "viscous friction. The system reaches quasi-steady "
        "equilibrium within 12 seconds. Negative feedback from "
        "the downstream gate stabilizes the transfer function."
    )

    mixed_text = (
        "Energy conservation requires that joule inputs equal "
        "outputs. But the team has low energy today, so let's "
        "just verify the entropy balance. We measured heat flow "
        "of 450 watts. There's some friction with the project "
        "timeline."
    )

    locker = AntiMetaphorLocker()

    print("=== DRIFTED (monoculture) ===")
    print(locker.audit(drifted_text).to_json())
    print()
    print("=== GROUNDED ===")
    print(locker.audit(grounded_text).to_json())
    print()
    print("=== MIXED ===")
    print(locker.audit(mixed_text).to_json())
    print()
    print("=== CROSS-MODEL PROMPT ===")
    print(CROSS_MODEL_PROMPT)
