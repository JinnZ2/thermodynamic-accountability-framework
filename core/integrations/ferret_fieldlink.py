#!/usr/bin/env python3
"""
Logic-Ferret Field Link — Bidirectional bridge between TAF and Logic-Ferret.

TAF (this repo) measures institutional accountability in energy units (Joules).
Logic-Ferret (github.com/JinnZ2/Logic-Ferret) detects rhetorical camouflage,
fallacies, and narrative manipulation through pattern analysis.

TAF measures from PHYSICS: does the energy math close?
Logic-Ferret measures from RHETORIC: is the narrative hiding the physics?

This module couples them:

    TAF → Ferret:  energy deficits, friction ratios → expected camouflage zones
    Ferret → TAF:  camouflage scores, fallacy counts → hidden variable estimates

The shared field is SIGNAL FIDELITY. Both systems detect when stated
narratives diverge from measurable reality. TAF catches the divergence
in energy; the Ferret catches it in language. When both fire together,
the camouflage has nowhere to hide.

Cross-reference map (from Logic-Ferret conflict_diagnosis.py):
    TAF Narrative Stripper         <-> Stated Problem + Feasibility Gap
    TAF Social Overhead Accountant <-> Systemic Alignment (performative action)
    TAF Root Cause Depth Analyzer  <-> Hidden Driver + Consequence Analysis
    TAF Friction Ratio             <-> Camouflage Score
    TAF Energy Conservation        <-> Consequence divergence (output != promise)
    TAF Entropy / waste growth     <-> Feedback Loops (self-reinforcing decay)

Dependencies: stdlib only (math). Does NOT import Logic-Ferret modules
directly — operates on their output values for loose coupling.

Stable input shape (contract): see `schemas/logic_ferret_contract.py`.
The contract mirrors Logic-Ferret's declared surface
(schema_contract.SCHEMA_VERSION, SENSOR_NAMES, LAYER_NAMES,
SIGNAL_LEVELS, DiagnoseResult / LayerResult TypedDicts, CALCULATE_C3
signature) and provides `validate_ferret_surface()`, which any
consumer should call on startup against Logic-Ferret's
`ferret_surface()` output. If validate returns compatible=False
(major version mismatch or missing canonical constants), the consumer
should bail rather than silently decode against a stale shape.
Pinned upstream schema version: 1.0.0.
"""

import math


# ============================================================
# FERRET → TAF: Rhetoric signals as hidden variable estimates
# ============================================================

def camouflage_to_hidden_count(camouflage_score, layer_signals=None):
    """Convert Logic-Ferret camouflage score to TAF hidden variable count.

    Camouflage = narrative hiding reality. Each layer of camouflage
    is functionally equivalent to a hidden variable in TAF — something
    the system can't see but that affects outcomes.

    Parameters
    ----------
    camouflage_score : float
        Logic-Ferret composite camouflage score (0-1).
    layer_signals : dict or None
        Per-layer signal strengths from conflict_diagnosis.diagnose().
        Keys are layer names, values are "strong"/"moderate"/"weak".
        If provided, strong signals add extra hidden variables.

    Returns
    -------
    int
        Estimated hidden variable count for TAF (0-10).
    """
    # Base: camouflage score maps linearly to hidden count
    base_count = camouflage_score * 8

    # Strong layer signals add extra hidden variables
    if layer_signals:
        signal_weights = {"strong": 1.0, "moderate": 0.3, "weak": 0.0}
        bonus = sum(signal_weights.get(s, 0) for s in layer_signals.values())
        # Cap bonus at 4 (max 8 strong layers × 0.5 contribution)
        base_count += min(bonus * 0.5, 4.0)

    return min(int(round(base_count)), 10)


def fallacy_count_to_feedback_integrity(fallacy_total):
    """Convert Logic-Ferret fallacy count to TAF feedback integrity score.

    Fallacies degrade feedback loops — each one is a point where
    the signal between cause and effect gets corrupted.

    TAF feedback integrity is 0-10 (10 = tight feedback).
    Each fallacy degrades it.

    Parameters
    ----------
    fallacy_total : int
        Total fallacy count from Logic-Ferret (any sensor).

    Returns
    -------
    float
        Feedback integrity score (0-10, 10 = intact).
    """
    if fallacy_total <= 0:
        return 10.0
    # Exponential decay: 10 fallacies → ~3.0 integrity
    integrity = 10.0 * math.exp(-0.12 * fallacy_total)
    return round(max(integrity, 0.0), 1)


def sensor_scores_to_friction_ratio(sensor_results):
    """Convert Logic-Ferret sensor suite results to TAF friction ratio.

    Each sensor detects a different type of institutional friction:
    - Propaganda/bias → narrative friction (energy spent maintaining stories)
    - Gatekeeping → access friction (energy spent on barriers)
    - False urgency → temporal friction (energy wasted on fake deadlines)
    - Reward manipulation → incentive friction (misaligned energy flows)
    - Narrative fragility → structural friction (energy spent propping up weak logic)

    Parameters
    ----------
    sensor_results : dict
        Sensor name → score (0-1) from run_full_sensor_scan.

    Returns
    -------
    float
        Friction ratio (0-1, higher = more institutional friction).
    """
    if not sensor_results:
        return 0.0

    # Weight sensors by their friction type relevance to TAF
    friction_weights = {
        "Propaganda Tone": 0.8,
        "Reward Manipulation": 1.2,
        "False Urgency": 0.9,
        "Gatekeeping": 1.3,
        "Narrative Fragility": 1.1,
        "Agency Score": 1.4,        # loss of agency = high friction
        "Propaganda Bias": 0.7,
        "Logic Fallacy Ferret": 1.0,
        "Gaslight Frequency Meter": 1.2,
        "Conflict Diagnosis": 1.5,   # most direct TAF mapping
        "Responsibility Deflection": 1.3,
        "True Accountability": -0.8,  # accountability REDUCES friction
        "Meritocracy Score": -0.6,    # meritocracy REDUCES friction
    }

    weighted_sum = 0.0
    weight_total = 0.0

    for name, score in sensor_results.items():
        w = friction_weights.get(name, 1.0)
        if w < 0:
            # Inverted sensors: high score = low friction
            weighted_sum += (1.0 - score) * abs(w)
            weight_total += abs(w)
        else:
            weighted_sum += score * w
            weight_total += w

    if weight_total == 0:
        return 0.0

    ratio = weighted_sum / weight_total
    return round(min(max(ratio, 0.0), 1.0), 3)


def gaslight_score_to_prediction_error(gaslight_score):
    """Convert Logic-Ferret gaslight meter to TAF prediction error.

    NOTE: gaslight_frequency_meter uses INVERTED polarity:
    1.0 = low gaslighting (good), 0.0 = high gaslighting (bad).
    This function handles the inversion.

    Gaslighting creates prediction error — the organism's model
    of reality is deliberately disrupted.

    Parameters
    ----------
    gaslight_score : float
        Gaslight frequency meter score (0-1, INVERTED: 1=good).

    Returns
    -------
    float
        Prediction error magnitude (0-1, 0=no error, 1=total disruption).
    """
    # Invert: 1.0 (low gaslight) → 0.0 prediction error
    return round(1.0 - max(0.0, min(1.0, gaslight_score)), 3)


# ============================================================
# TAF → FERRET: Energy state as expected camouflage indicators
# ============================================================

def energy_deficit_to_camouflage_expectation(fatigue_score, friction_ratio=0.0):
    """Predict expected camouflage level from TAF energy state.

    When an institution extracts more energy than it returns (high fatigue),
    it must maintain a narrative to justify the extraction. Higher energy
    deficits predict higher camouflage scores.

    Parameters
    ----------
    fatigue_score : float
        TAF fatigue score (0-10).
    friction_ratio : float
        TAF friction ratio (0-1).

    Returns
    -------
    float
        Expected camouflage score (0-1) for cross-validation.
    """
    # Fatigue drives need for camouflage
    fatigue_component = fatigue_score / 10.0

    # Friction amplifies it (more friction = more to hide)
    amplified = fatigue_component * (1 + friction_ratio)

    return round(min(amplified, 1.0), 3)


def collapse_distance_to_narrative_fragility(collapse_distance):
    """Predict expected narrative fragility from TAF collapse proximity.

    As systems approach collapse, narratives become more fragile —
    the gap between stated reality and actual reality widens,
    requiring more fallacies to maintain coherence.

    Parameters
    ----------
    collapse_distance : float
        TAF distance-to-collapse (0-1, 1=sustainable, 0=collapse).

    Returns
    -------
    float
        Expected narrative fragility (0-1, higher = more fragile).
    """
    # Inverse: closer to collapse → more fragile narrative
    if collapse_distance >= 1.0:
        return 0.0
    # Nonlinear: fragility accelerates near collapse
    return round(1.0 - collapse_distance ** 0.6, 3)


def parasitic_debt_to_deflection_expectation(energy_debt, metabolic_rate=1.0):
    """Predict expected responsibility deflection from TAF parasitic debt.

    Unpaid energy debt creates institutional pressure to deflect
    accountability. Higher debt → more deflection language expected.

    Parameters
    ----------
    energy_debt : float
        TAF parasitic energy debt.
    metabolic_rate : float
        Baseline metabolic rate for normalization.

    Returns
    -------
    float
        Expected deflection score (0-1).
    """
    if energy_debt <= 0:
        return 0.0
    # Normalize debt against daily metabolic output (8h × rate)
    normalized = energy_debt / (8 * metabolic_rate)
    return round(min(1.0 - math.exp(-0.3 * normalized), 1.0), 3)


# ============================================================
# COUPLED CROSS-VALIDATION
# ============================================================

class FerretLink:
    """Bidirectional TAF ↔ Logic-Ferret coupling.

    Provides cross-validation: when TAF energy physics and Ferret
    rhetorical analysis agree, confidence is high. When they diverge,
    something is being missed by one framework.

    Usage:
        link = FerretLink()
        link.ingest_ferret_results(camouflage_score, fallacies, sensor_results)
        link.ingest_taf_state(fatigue_score, collapse_distance, energy_debt, friction)
        report = link.cross_validate()
    """

    def __init__(self):
        # Ferret side
        self.camouflage_score = 0.0
        self.fallacy_total = 0
        self.sensor_results = {}
        self.layer_signals = {}
        self.gaslight_score = 1.0  # default: no gaslighting

        # TAF side
        self.fatigue_score = 0.0
        self.collapse_distance = 1.0
        self.energy_debt = 0.0
        self.friction_ratio = 0.0

        # Derived
        self._ferret_ingested = False
        self._taf_ingested = False

    def ingest_ferret_results(self, camouflage_score=0.0, fallacy_total=0,
                               sensor_results=None, layer_signals=None,
                               gaslight_score=1.0):
        """Load Logic-Ferret analysis results.

        Parameters
        ----------
        camouflage_score : float
            Conflict diagnosis camouflage score (0-1).
        fallacy_total : int
            Total fallacy count across all sensors.
        sensor_results : dict or None
            Sensor name → score from run_full_sensor_scan.
        layer_signals : dict or None
            Layer name → signal strength from conflict_diagnosis.
        gaslight_score : float
            Gaslight frequency meter score (0-1, INVERTED polarity).
        """
        self.camouflage_score = camouflage_score
        self.fallacy_total = fallacy_total
        self.sensor_results = sensor_results or {}
        self.layer_signals = layer_signals or {}
        self.gaslight_score = gaslight_score
        self._ferret_ingested = True

    def ingest_taf_state(self, fatigue_score=0.0, collapse_distance=1.0,
                          energy_debt=0.0, friction_ratio=0.0):
        """Load TAF energy analysis state.

        Parameters
        ----------
        fatigue_score : float
            TAF fatigue score (0-10).
        collapse_distance : float
            TAF distance-to-collapse (0-1).
        energy_debt : float
            TAF parasitic energy debt.
        friction_ratio : float
            TAF friction ratio (0-1).
        """
        self.fatigue_score = fatigue_score
        self.collapse_distance = collapse_distance
        self.energy_debt = energy_debt
        self.friction_ratio = friction_ratio
        self._taf_ingested = True

    def cross_validate(self):
        """Run cross-validation between TAF physics and Ferret rhetoric.

        Compares what TAF predicts the narrative SHOULD look like
        (given energy state) with what the Ferret actually found.

        Returns
        -------
        dict
            Cross-validation report with convergence/divergence analysis.
        """
        report = {}

        # --- Ferret → TAF derived values ---
        report["derived_hidden_count"] = camouflage_to_hidden_count(
            self.camouflage_score, self.layer_signals
        )
        report["derived_feedback_integrity"] = fallacy_count_to_feedback_integrity(
            self.fallacy_total
        )
        report["derived_friction_ratio"] = sensor_scores_to_friction_ratio(
            self.sensor_results
        )
        report["derived_prediction_error"] = gaslight_score_to_prediction_error(
            self.gaslight_score
        )

        # --- TAF → Ferret expected values ---
        report["expected_camouflage"] = energy_deficit_to_camouflage_expectation(
            self.fatigue_score, self.friction_ratio
        )
        report["expected_narrative_fragility"] = collapse_distance_to_narrative_fragility(
            self.collapse_distance
        )
        report["expected_deflection"] = parasitic_debt_to_deflection_expectation(
            self.energy_debt
        )

        # --- Convergence analysis ---
        # Compare observed camouflage vs. expected from energy state
        camo_delta = abs(self.camouflage_score - report["expected_camouflage"])

        if camo_delta < 0.15:
            report["convergence"] = "STRONG"
            report["interpretation"] = (
                "Physics and rhetoric agree. The energy math and the language "
                "tell the same story. High confidence in diagnosis."
            )
        elif camo_delta < 0.35:
            report["convergence"] = "MODERATE"
            report["interpretation"] = (
                "Partial agreement. Either the narrative is partially effective "
                "at hiding the energy deficit, or there's a lag between "
                "physical reality and rhetorical adaptation."
            )
        else:
            report["convergence"] = "DIVERGENT"
            if self.camouflage_score > report["expected_camouflage"]:
                report["interpretation"] = (
                    "More camouflage than expected from energy state. "
                    "The narrative is working overtime — possibly preemptive "
                    "cover for problems that haven't surfaced in energy data yet. "
                    "Check for hidden institutional extraction."
                )
            else:
                report["interpretation"] = (
                    "Less camouflage than expected from energy state. "
                    "The energy deficit is visible but the institution isn't "
                    "defending it rhetorically. Possible scenarios: honest "
                    "acknowledgment, narrative hasn't caught up yet, or "
                    "the extraction is so normalized it doesn't need defending."
                )

        report["camouflage_delta"] = round(camo_delta, 3)

        # --- Composite signal fidelity ---
        # How much of reality is visible through both lenses?
        ferret_fidelity = 1.0 - self.camouflage_score
        taf_fidelity = self.collapse_distance  # further from collapse = clearer signal
        combined_fidelity = (ferret_fidelity + taf_fidelity) / 2.0
        report["signal_fidelity"] = round(combined_fidelity, 3)

        return report


# ============================================================
# VARIABLE MAP: TAF ↔ Logic-Ferret shared namespace
# ============================================================

FIELD_MAP = {
    # TAF variable              → Ferret variable                    Direction
    "hidden_count":             ("camouflage_score → hidden estimate", "Ferret→TAF"),
    "feedback_integrity":       ("fallacy_total → integrity score",    "Ferret→TAF"),
    "friction_ratio":           ("sensor_suite composite",             "Ferret→TAF"),
    "prediction_error":         ("gaslight_score (inverted)",          "Ferret→TAF"),
    "expected_camouflage":      ("fatigue + friction → camo prediction", "TAF→Ferret"),
    "narrative_fragility":      ("collapse_distance → fragility",     "TAF→Ferret"),
    "expected_deflection":      ("energy_debt → deflection prediction", "TAF→Ferret"),
    "signal_fidelity":          ("combined lens clarity",             "bidirectional"),
    # Layer-level cross-references
    "Stated Problem":           ("narrative_stripper / energy budget",  "Ferret↔TAF"),
    "Feasibility Gap":          ("solution vs. energy math",           "Ferret↔TAF"),
    "Systemic Alignment":       ("social_overhead_accountant",         "Ferret↔TAF"),
    "Hidden Driver":            ("root_cause_depth_analyzer",          "Ferret↔TAF"),
    "Consequence Analysis":     ("energy_conservation check",          "Ferret↔TAF"),
    "Feedback Loops":           ("entropy_growth / waste tracking",    "Ferret↔TAF"),
}


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  LOGIC-FERRET ↔ TAF FIELD LINK — Cross-Validation Demo")
    print("=" * 60)

    link = FerretLink()

    # Simulate Ferret results: moderate camouflage detected
    link.ingest_ferret_results(
        camouflage_score=0.55,
        fallacy_total=7,
        sensor_results={
            "Propaganda Tone": 0.3,
            "Reward Manipulation": 0.4,
            "False Urgency": 0.6,
            "Gatekeeping": 0.5,
            "Narrative Fragility": 0.7,
            "Agency Score": 0.45,
            "Propaganda Bias": 0.35,
            "Logic Fallacy Ferret": 0.5,
            "Gaslight Frequency Meter": 0.6,  # inverted: 0.6 = moderate gaslighting
        },
        layer_signals={
            "Stated Problem": "strong",
            "Feasibility Gap": "moderate",
            "Incentive Mapping": "strong",
            "Systemic Alignment": "moderate",
            "Consequence Analysis": "strong",
            "Hidden Driver": "moderate",
            "Peripheral Signals": "weak",
            "Feedback Loops": "strong",
        },
        gaslight_score=0.6,
    )

    # Simulate TAF state: elevated fatigue, moderate friction
    link.ingest_taf_state(
        fatigue_score=6.5,
        collapse_distance=0.45,
        energy_debt=12.0,
        friction_ratio=0.4,
    )

    report = link.cross_validate()

    print("\n  --- Ferret → TAF Derived Values ---")
    print(f"  Hidden variable estimate: {report['derived_hidden_count']}")
    print(f"  Feedback integrity:       {report['derived_feedback_integrity']}/10")
    print(f"  Friction ratio:           {report['derived_friction_ratio']}")
    print(f"  Prediction error:         {report['derived_prediction_error']}")

    print("\n  --- TAF → Ferret Expected Values ---")
    print(f"  Expected camouflage:      {report['expected_camouflage']}")
    print(f"  Expected fragility:       {report['expected_narrative_fragility']}")
    print(f"  Expected deflection:      {report['expected_deflection']}")

    print("\n  --- Cross-Validation ---")
    print(f"  Convergence:       {report['convergence']}")
    print(f"  Camouflage delta:  {report['camouflage_delta']}")
    print(f"  Signal fidelity:   {report['signal_fidelity']}")
    print(f"  Interpretation:    {report['interpretation']}")
    print()
