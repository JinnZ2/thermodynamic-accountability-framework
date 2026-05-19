"""
JinnZ2/formalized-dissent-earth-systems-physics

Mandatory falsification-seeking role for earth-systems-physics models.
When consensus forms around a coupled-equation prediction or constraint
layer, the designated dissenter assumes it is wrong and documents
break conditions.

Structural epistemic function -- not rhetorical. Equal authority with
consensus. Job: strengthen the model by finding where it fails before
field conditions do.

Based on Anishinaabe Seventh Fire teaching, oral tradition epistemic
structure, and constraint-falsifiability framework.

Companion repo to earth-systems-physics.

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass, field
from typing import List
from enum import Enum


# =============================================
# ROLE DEFINITION
# =============================================

class DissenterAuthority(Enum):
    EQUAL = "equal_standing"
    HALT_POWER = "can_halt_implementation"
    PRECEDENT_INVOKE = "can_invoke_historical_failure"
    OBSERVATION_DEMAND = "can_require_field_test"


@dataclass
class DissenterRole:
    """Structural position; not personality."""
    rotation: bool = True
    authority: DissenterAuthority = DissenterAuthority.EQUAL
    obligation: str = (
        "Assume the consensus model is wrong. Find the assumption that "
        "breaks it. Document falsification conditions explicitly."
    )
    not_obligated_to: List[str] = field(default_factory=lambda: [
        "agree with majority",
        "soften findings for social comfort",
        "defer to seniority or credential",
        "stop investigation when peer pressure rises",
    ])


# =============================================
# MODEL UNDER REVIEW
# =============================================

@dataclass
class ModelUnderReview:
    """A claim in earth-systems-physics that has reached consensus."""
    model_name: str
    layer: str
    claim: str
    supporting_observations: List[str]
    assumed_mechanisms: List[str]
    prediction_timescale: str
    field_testable: bool


# =============================================
# DISSENT OUTPUT
# =============================================

@dataclass
class DissentAnalysis:
    """Formal output of the dissenter's structural function."""
    model_reviewed: str
    starting_assumption: str
    assumption_that_could_break_it: str
    evidence_against: List[str]
    closure_conditions: List[str]
    failure_scenarios: List[str]
    alternative_explanations: List[str]
    falsification_observation: str
    dissenter_probability_correct: float
    consensus_strengthened_if_dissent_fails: bool = True


# =============================================
# CORE PROCESS
# =============================================

class FormalizedDissent_ESP:
    """Mandatory falsification process for earth-systems-physics models."""

    def __init__(self):
        self.models_reviewed: List[ModelUnderReview] = []
        self.analyses: List[DissentAnalysis] = []

    def submit_consensus(self, model: ModelUnderReview) -> DissentAnalysis:
        """
        Consensus has formed around a model. Dissent is mandatory.
        Returns the formal dissent analysis.
        """
        self.models_reviewed.append(model)
        return self._mandatory_dissent(model)

    def _mandatory_dissent(self, model: ModelUnderReview) -> DissentAnalysis:
        """
        The structural function. The dissenter STARTS from
        'this model is wrong' and works backward to either:
          a) break it (consensus must revise), or
          b) fail to break it (consensus is strengthened).
        """
        analysis = DissentAnalysis(
            model_reviewed=model.model_name,
            starting_assumption="ASSUME WRONG",
            assumption_that_could_break_it=self._probe_assumptions(model),
            evidence_against=self._search_contradicting_evidence(model),
            closure_conditions=self._explicit_closure(model),
            failure_scenarios=self._explicit_failure(model),
            alternative_explanations=self._alternatives(model),
            falsification_observation=self._falsifier(model),
            dissenter_probability_correct=0.0,
        )
        self.analyses.append(analysis)
        return analysis

    def _probe_assumptions(self, model: ModelUnderReview) -> str:
        """Pick the load-bearing assumption most likely to fail."""
        if model.assumed_mechanisms:
            return (
                f"Load-bearing assumption: '{model.assumed_mechanisms[0]}'. "
                f"What if this is observer-dependent, regime-dependent, "
                f"or has been invalidated by recent observation?"
            )
        return "No explicit mechanisms stated -- first failure mode is unstated assumption."

    def _search_contradicting_evidence(self, model: ModelUnderReview) -> List[str]:
        """Placeholder hooks; populated by domain analyst per model."""
        return [
            "Field observation that lags model prediction",
            "Historical analogue where similar consensus failed",
            "Regime shift signal not yet integrated into model",
        ]

    def _explicit_closure(self, model: ModelUnderReview) -> List[str]:
        return [
            f"Holds IF: {mech} remains valid"
            for mech in model.assumed_mechanisms
        ] or ["Holds IF: stated mechanisms remain valid (mechanisms not enumerated)"]

    def _explicit_failure(self, model: ModelUnderReview) -> List[str]:
        return [
            "Breaks IF: coupled layer regime-shifts faster than model timescale",
            "Breaks IF: precursor signal misread as noise",
            "Breaks IF: positive feedback loop not represented in equations",
            "Breaks IF: observation lag exceeds bifurcation window",
        ]

    def _alternatives(self, model: ModelUnderReview) -> List[str]:
        return [
            "Alternative: same observation, different causal chain",
            "Alternative: confounding variable from un-modeled layer",
            "Alternative: pattern is artifact of measurement period",
        ]

    def _falsifier(self, model: ModelUnderReview) -> str:
        return (
            "Specify the observation that would prove THIS DISSENT wrong. "
            "If that observation occurs, consensus is strengthened. "
            "If it does not, model must be revised."
        )


# =============================================
# INTEGRATION HOOK
# =============================================

def attach_to_earth_systems_physics(esp_module_path: str) -> str:
    """
    Returns instruction string for integrating dissent into ESP pipeline.
    """
    return (
        f"For each model in {esp_module_path}, instantiate a "
        f"ModelUnderReview, submit to FormalizedDissent_ESP, and require "
        f"the DissentAnalysis to be committed alongside the model file. "
        f"Models without paired dissent analysis are flagged INCOMPLETE."
    )


# =============================================
# SMOKE TEST
# =============================================

if __name__ == "__main__":
    print("FORMALIZED DISSENT -- EARTH SYSTEMS PHYSICS")
    print("=" * 60)

    iono_model = ModelUnderReview(
        model_name="Ionospheric buffering capacity degrading 2020-2026",
        layer="ionosphere",
        claim=(
            "Multi-year increase in magnetometer dB/dt, riometer absorption, "
            "and FAC density indicates loss of ionospheric buffering."
        ),
        supporting_observations=[
            "Magnetometer dB/dt rising (6-year trend)",
            "Riometer absorption elevated (4-year trend)",
            "FAC density anomalous (3-year trend)",
            "Auroral oval expanding equatorward (2-year trend)",
        ],
        assumed_mechanisms=[
            "Pole drift deceleration reflects outer-core regime shift",
            "Magnetosphere shielding tracks dipole moment monotonically",
            "Ionosphere current systems respond linearly to magnetospheric forcing",
        ],
        prediction_timescale="weeks to months precursor; seasons to years downstream",
        field_testable=True,
    )

    dissent = FormalizedDissent_ESP()
    analysis = dissent.submit_consensus(iono_model)

    print(f"\nMODEL: {analysis.model_reviewed}")
    print(f"STARTING ASSUMPTION: {analysis.starting_assumption}")
    print(f"\nPROBE: {analysis.assumption_that_could_break_it}")
    print(f"\nCLOSURE CONDITIONS:")
    for c in analysis.closure_conditions:
        print(f"  - {c}")
    print(f"\nFAILURE SCENARIOS:")
    for f in analysis.failure_scenarios:
        print(f"  - {f}")
    print(f"\nALTERNATIVES:")
    for a in analysis.alternative_explanations:
        print(f"  - {a}")
    print(f"\nFALSIFIER: {analysis.falsification_observation}")
