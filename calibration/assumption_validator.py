"""
assumption_validator.py

Generalized assumption-boundary validator. Tracks whether TAF's own
state variables are operating within the regime where their underlying
equations remain valid, and detects cascade convergence across coupled
assumptions.

Mirrors the stable surface of earth-systems-physics' assumption_validator
package (RiskLevel enum, AssumptionBoundary dataclass shape, full_report
return contract) so reports can be cross-consumed without runtime
coupling. The Earth-systems REGISTRY there is domain-specific; this
module ships a TAF-specific REGISTRY keyed to TAF's core equations
(fatigue_score, distance_to_collapse, hidden_count, friction_ratio,
K_cred, parasitic_energy_debt).

License: CC0 1.0 Universal (public domain)
Dependencies: stdlib only
Lineage: substrate_audit, first_principles_audit, monoculture_detector
Family role: regime-validity diagnostic. Answers "are the equations
    we are using still valid given current state?" -- complementary to
    monoculture_detector (variance) and first_principles_audit (mechanics).

Cross-reference upstream: github.com/JinnZ2/earth-systems-physics
    (assumption_validator/registry.py)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------
# RISK LEVEL (matches ESP contract exactly: GREEN/YELLOW/RED string values)
# ---------------------------------------------------------------

class RiskLevel(Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


# ---------------------------------------------------------------
# ASSUMPTION BOUNDARY
# ---------------------------------------------------------------

@dataclass
class AssumptionBoundary:
    """A single assumption with its valid-regime boundaries.

    Field shape matches earth-systems-physics' AssumptionBoundary
    minus the ESP-specific source_layer / layer_key. Add those fields
    via subclass or via the `notes` field if mirroring an ESP entry.
    """
    name: str
    parameter: str
    units: str
    green_range: Tuple[float, float]
    yellow_range: Tuple[float, float]
    red_threshold: float
    higher_is_worse: bool
    couplings: List[str] = field(default_factory=list)
    rate_of_change: float = 0.0
    notes: str = ""

    def assess(self, value: Optional[float]) -> Tuple[RiskLevel, float, float]:
        """Assess risk for a given value.

        Returns
        -------
        (risk, confidence_penalty, proximity_to_red)
            risk: GREEN/YELLOW/RED
            confidence_penalty: [0,1], how much to discount predictions
            proximity_to_red: [0,1], how close the value sits to the RED line
        """
        if value is None:
            return (RiskLevel.GREEN, 0.0, 0.0)

        v = float(value)

        if self.higher_is_worse:
            if v <= self.green_range[1]:
                return (RiskLevel.GREEN, 0.0, 0.0)
            if v <= self.yellow_range[1]:
                progress = (v - self.green_range[1]) / (
                    self.yellow_range[1] - self.green_range[1] + 1e-30)
                penalty = 0.3 * progress
                proximity = (v - self.yellow_range[0]) / (
                    self.red_threshold - self.yellow_range[0] + 1e-30)
                return (RiskLevel.YELLOW, penalty, min(1.0, proximity))
            excess = (v - self.red_threshold) / (
                abs(self.red_threshold) + 1e-30)
            penalty = min(1.0, 0.8 + 0.2 * excess)
            return (RiskLevel.RED, penalty, 1.0)
        # lower_is_worse branch
        if v >= self.green_range[0]:
            return (RiskLevel.GREEN, 0.0, 0.0)
        if v >= self.yellow_range[0]:
            progress = (self.green_range[0] - v) / (
                self.green_range[0] - self.yellow_range[0] + 1e-30)
            penalty = 0.3 * progress
            proximity = (self.yellow_range[1] - v) / (
                self.yellow_range[1] - self.red_threshold + 1e-30)
            return (RiskLevel.YELLOW, penalty, min(1.0, proximity))
        deficit = (self.red_threshold - v) / (
            abs(self.red_threshold) + 1e-30)
        penalty = min(1.0, 0.8 + 0.2 * deficit)
        return (RiskLevel.RED, penalty, 1.0)

    def proximity_to_red(self, value: float) -> float:
        _, _, prox = self.assess(value)
        return prox


# ---------------------------------------------------------------
# TAF REGISTRY -- assumptions about TAF's own equations
# ---------------------------------------------------------------
#
# Each entry pins the regime in which a TAF equation is known to behave.
# Outside the regime, predictions get a confidence penalty and the
# affected couplings get walked for cascade detection.
#
# Sources for thresholds (CLAUDE.md):
#   fatigue_score:  0-10 scale, productivity degrades >6, safety >7,
#                   health collapse >8 (corresponds to 1.2/1.4/1.6 * E_input)
#   distance_to_collapse: 0-1, 1=sustainable, 0=collapsed
#   hidden_count: nonlinear compounding via hidden_mult = 1 + 0.1 * n^1.5
#   friction_ratio: 0-1, institutional friction
#   K_cred: 0-1+, Money Equation credibility term
#   parasitic_energy_debt: J, accumulated unpaid metabolic cost

REGISTRY: Dict[str, AssumptionBoundary] = {
    "fatigue_score": AssumptionBoundary(
        name="Organism Fatigue Score",
        parameter="fatigue_score",
        units="dimensionless 0-10",
        green_range=(0.0, 6.0),
        yellow_range=(6.0, 7.0),
        red_threshold=7.0,
        higher_is_worse=True,
        couplings=["distance_to_collapse", "parasitic_energy_debt"],
        notes="Above 6: productivity degradation. Above 7: safety system "
              "breakdown. Above 8: health collapse imminent.",
    ),
    "distance_to_collapse": AssumptionBoundary(
        name="Distance to Collapse",
        parameter="distance_to_collapse",
        units="fraction 0-1",
        green_range=(0.40, 1.00),
        yellow_range=(0.15, 0.40),
        red_threshold=0.15,
        higher_is_worse=False,
        couplings=["fatigue_score", "trust_phase"],
        notes="Below 0.40: load exceeds 1.4 * E_input (safety breakdown). "
              "Below 0.15: load exceeds 1.55 * E_input (terminal). "
              "0.0: organism exits or collapses.",
    ),
    "hidden_count": AssumptionBoundary(
        name="Hidden Variable Count",
        parameter="hidden_count",
        units="count",
        green_range=(0, 3),
        yellow_range=(3, 6),
        red_threshold=6,
        higher_is_worse=True,
        couplings=["fatigue_score", "long_tail_risk"],
        notes="Compounds via hidden_mult = 1 + 0.1 * n^1.5. Above 6 the "
              "nonlinear amplification dominates and linear-superposition "
              "assumptions break.",
    ),
    "friction_ratio": AssumptionBoundary(
        name="Institutional Friction Ratio",
        parameter="friction_ratio",
        units="fraction 0-1",
        green_range=(0.0, 0.30),
        yellow_range=(0.30, 0.60),
        red_threshold=0.60,
        higher_is_worse=True,
        couplings=["fatigue_score", "K_cred"],
        notes="Above 0.30: parasitic-debt accumulation accelerates. "
              "Above 0.60: friction dominates over productive throughput.",
    ),
    "K_cred": AssumptionBoundary(
        name="Money Equation Credibility Term",
        parameter="K_cred",
        units="dimensionless 0-1",
        green_range=(0.50, 1.00),
        yellow_range=(0.20, 0.50),
        red_threshold=0.20,
        higher_is_worse=False,
        couplings=["friction_ratio", "trust_level"],
        notes="K_cred = consequence_density * verification_freq * "
              "time_under_exposure. Below 0.50: credibility eroding. "
              "Below 0.20: Money Equation diverges from delivered value.",
    ),
    "parasitic_energy_debt": AssumptionBoundary(
        name="Parasitic Energy Debt",
        parameter="energy_debt_J",
        units="joules (per metabolic day)",
        green_range=(0, 5e6),
        yellow_range=(5e6, 2e7),
        red_threshold=2e7,
        higher_is_worse=True,
        couplings=["fatigue_score", "distance_to_collapse"],
        notes="Approx. one full metabolic day = 1e7 J. Above 2x daily "
              "metabolic output: organism cannot repay debt without "
              "structural recovery time.",
    ),
    "trust_level": AssumptionBoundary(
        name="Trust Level (Trust-Exit Bridge)",
        parameter="trust_level",
        units="fraction 0-1",
        green_range=(0.50, 1.00),
        yellow_range=(0.20, 0.50),
        red_threshold=0.20,
        higher_is_worse=False,
        couplings=["K_cred", "distance_to_collapse"],
        notes="Mirrors trust-exit-model TrustState.trust_level. Below "
              "0.50: EARLY_EROSION or worse. Below 0.20: TERMINAL.",
    ),
    "long_tail_risk": AssumptionBoundary(
        name="Long-Tail Risk Score",
        parameter="long_tail_risk",
        units="dimensionless 0-10",
        green_range=(0.0, 4.0),
        yellow_range=(4.0, 7.0),
        red_threshold=7.0,
        higher_is_worse=True,
        couplings=["hidden_count"],
        notes="risk = 10 * (1 - exp(-0.35 * hidden_count)). Above 7: "
              "long-tail dominates expected value; mean-based reasoning "
              "fails.",
    ),
}


# ---------------------------------------------------------------
# COUPLING GRAPH -- which assumptions drag others when degraded
# ---------------------------------------------------------------

COUPLING_GRAPH: Dict[str, List[str]] = {
    "fatigue_score":         ["distance_to_collapse", "parasitic_energy_debt"],
    "distance_to_collapse":  ["fatigue_score", "trust_level"],
    "hidden_count":          ["fatigue_score", "long_tail_risk"],
    "friction_ratio":        ["fatigue_score", "K_cred"],
    "K_cred":                ["friction_ratio", "trust_level"],
    "parasitic_energy_debt": ["fatigue_score", "distance_to_collapse"],
    "trust_level":           ["K_cred", "distance_to_collapse"],
    "long_tail_risk":        ["hidden_count"],
}


# ---------------------------------------------------------------
# ASSESSMENT ENGINE
# ---------------------------------------------------------------

def assess_state(
    state: Dict[str, float],
    registry: Optional[Dict[str, AssumptionBoundary]] = None,
) -> Dict[str, Dict]:
    """Assess every registered assumption against an observed state.

    Parameters
    ----------
    state : dict
        Observed values keyed by AssumptionBoundary.parameter (NOT the
        registry key -- this matches ESP's layer_key indirection).
    registry : dict, optional
        Defaults to the TAF REGISTRY above.

    Returns
    -------
    dict keyed by assumption-id with per-assumption assessment dicts
    matching ESP's full_report() shape.
    """
    if registry is None:
        registry = REGISTRY

    results = {}
    for assumption_id, boundary in registry.items():
        value = state.get(boundary.parameter)
        if value is None:
            results[assumption_id] = {
                "id": assumption_id,
                "name": boundary.name,
                "status": "UNKNOWN",
                "value": None,
                "message": f"No value for parameter '{boundary.parameter}'",
            }
            continue

        try:
            numeric = float(value)
        except (TypeError, ValueError):
            results[assumption_id] = {
                "id": assumption_id,
                "name": boundary.name,
                "status": "INFO",
                "value": str(value),
                "message": f"Non-numeric value: {value}",
            }
            continue

        risk, penalty, proximity = boundary.assess(numeric)
        results[assumption_id] = {
            "id": assumption_id,
            "name": boundary.name,
            "status": risk.value,
            "value": numeric,
            "units": boundary.units,
            "confidence_penalty": penalty,
            "proximity_to_red": proximity,
            "green_range": boundary.green_range,
            "red_threshold": boundary.red_threshold,
            "couplings": boundary.couplings,
            "notes": boundary.notes,
        }

    return results


def global_confidence_multiplier(assessments: Dict[str, Dict]) -> float:
    """Multiplicative confidence discount across all assumptions.

    Each YELLOW/RED assumption applies (1 - penalty). Used to discount
    downstream predictions when multiple assumptions are degrading.
    """
    multiplier = 1.0
    for data in assessments.values():
        penalty = data.get("confidence_penalty", 0.0)
        if isinstance(penalty, (int, float)):
            multiplier *= (1.0 - penalty)
    return max(0.0, multiplier)


def detect_cascade_risk(
    assessments: Dict[str, Dict],
    coupling_graph: Optional[Dict[str, List[str]]] = None,
    registry: Optional[Dict[str, AssumptionBoundary]] = None,
) -> Dict:
    """Detect convergence of failures across coupled assumptions.

    Returns
    -------
    dict with cascade level (MINIMAL/LOW/MODERATE/HIGH/CRITICAL),
    explanatory message, lists of red/yellow/coupled-degraded pairs,
    and an irreversible-active list (IDs whose notes contain
    'IRREVERSIBLE').
    """
    if coupling_graph is None:
        coupling_graph = COUPLING_GRAPH
    if registry is None:
        registry = REGISTRY

    yellow = [k for k, v in assessments.items() if v.get("status") == "YELLOW"]
    red = [k for k, v in assessments.items() if v.get("status") == "RED"]
    degraded_set = set(yellow + red)

    coupled = []
    for src, targets in coupling_graph.items():
        if src in degraded_set:
            for tgt in targets:
                if tgt in degraded_set:
                    coupled.append(tuple(sorted((src, tgt))))
    coupled = sorted(set(coupled))

    n_red = len(red)
    n_yellow = len(yellow)
    n_coupled = len(coupled)

    if n_red >= 3 or (n_red >= 2 and n_coupled >= 2):
        level = "CRITICAL"
        message = ("System entering unknown state -- multiple coupled "
                   "assumptions have left their stable regime.")
    elif n_red >= 1 and n_coupled >= 2:
        level = "HIGH"
        message = ("Cascade propagating -- one RED assumption is "
                   "driving coupled YELLOW degradations.")
    elif n_coupled >= 3:
        level = "MODERATE"
        message = ("Multiple coupled assumption pairs degrading "
                   "simultaneously.")
    elif n_yellow >= 4:
        level = "LOW"
        message = ("Broad degradation across assumptions -- monitor "
                   "coupling for convergence.")
    else:
        level = "MINIMAL"
        message = "No cascade convergence detected."

    irreversible = [
        k for k in red
        if "IRREVERSIBLE" in registry.get(
            k,
            AssumptionBoundary("", "", "", (0, 1), (0, 1), 0, True, notes=""),
        ).notes.upper()
    ]

    return {
        "cascade_level": level,
        "message": message,
        "red_assumptions": red,
        "yellow_assumptions": yellow,
        "coupled_degraded": [list(p) for p in coupled],
        "irreversible_active": irreversible,
        "n_red": n_red,
        "n_yellow": n_yellow,
        "n_coupled_pairs": n_coupled,
    }


def full_report(
    state: Dict[str, float],
    registry: Optional[Dict[str, AssumptionBoundary]] = None,
    coupling_graph: Optional[Dict[str, List[str]]] = None,
) -> Dict:
    """Single call: state in, full validity report out.

    Return shape exactly mirrors ESP's assumption_validator.registry.full_report:
        {assumptions, global_confidence_multiplier, cascade, summary}

    This lets a downstream consumer treat TAF reports and ESP reports
    interchangeably (the registries differ by domain; the contract does not).
    """
    assessments = assess_state(state, registry)
    multiplier = global_confidence_multiplier(assessments)
    cascade = detect_cascade_risk(assessments, coupling_graph, registry)

    summary = {
        "total": len(assessments),
        "green": sum(1 for v in assessments.values() if v.get("status") == "GREEN"),
        "yellow": sum(1 for v in assessments.values() if v.get("status") == "YELLOW"),
        "red": sum(1 for v in assessments.values() if v.get("status") == "RED"),
        "unknown": sum(1 for v in assessments.values() if v.get("status") == "UNKNOWN"),
    }

    return {
        "assumptions": assessments,
        "global_confidence_multiplier": multiplier,
        "cascade": cascade,
        "summary": summary,
    }


# ---------------------------------------------------------------
# CROSS-MODEL PROMPT
# ---------------------------------------------------------------

CROSS_MODEL_PROMPT = """
ASSUMPTION VALIDITY AUDIT

Score whether the equations being applied to a system are still
operating in their valid regime.

For each assumption in the registry:
1. Read the observed value of its parameter.
2. Compare against (green_range, yellow_range, red_threshold).
3. Return RiskLevel: GREEN / YELLOW / RED.
4. Compute confidence_penalty in [0,1] and proximity_to_red in [0,1].

For the system as a whole:
- global_confidence_multiplier = product of (1 - penalty) over all
  assumptions. A value below 0.5 means downstream predictions should
  be heavily discounted.
- cascade detection: walk the coupling graph. If two coupled
  assumptions are simultaneously degraded, their interaction is
  outside the validated regime even if each is YELLOW alone.

Output JSON with shape:
    {
      "assumptions": {id: {status, value, confidence_penalty, ...}, ...},
      "global_confidence_multiplier": float,
      "cascade": {cascade_level, red_assumptions, coupled_degraded, ...},
      "summary": {total, green, yellow, red, unknown}
    }

Cascade level scale: MINIMAL < LOW < MODERATE < HIGH < CRITICAL.
"""


# ---------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------

if __name__ == "__main__":
    import json as _json

    # Healthy state: everything within green ranges
    healthy = {
        "fatigue_score": 3.0,
        "distance_to_collapse": 0.85,
        "hidden_count": 1,
        "friction_ratio": 0.10,
        "K_cred": 0.80,
        "energy_debt_J": 1e6,
        "trust_level": 0.90,
        "long_tail_risk": 1.5,
    }

    # Stressed state: multiple coupled degradations
    stressed = {
        "fatigue_score": 6.5,
        "distance_to_collapse": 0.30,
        "hidden_count": 5,
        "friction_ratio": 0.45,
        "K_cred": 0.30,
        "energy_debt_J": 1.2e7,
        "trust_level": 0.35,
        "long_tail_risk": 5.2,
    }

    # Critical state: cascade territory
    critical = {
        "fatigue_score": 8.5,
        "distance_to_collapse": 0.05,
        "hidden_count": 9,
        "friction_ratio": 0.75,
        "K_cred": 0.10,
        "energy_debt_J": 5e7,
        "trust_level": 0.10,
        "long_tail_risk": 9.0,
    }

    for label, state in [("HEALTHY", healthy),
                         ("STRESSED", stressed),
                         ("CRITICAL", critical)]:
        report = full_report(state)
        print(f"=== {label} ===")
        print(f"  summary:   {report['summary']}")
        print(f"  cascade:   {report['cascade']['cascade_level']} -- "
              f"{report['cascade']['message']}")
        print(f"  multiplier: {report['global_confidence_multiplier']:.3f}")
        print()

    print("=== CROSS-MODEL PROMPT ===")
    print(CROSS_MODEL_PROMPT)
