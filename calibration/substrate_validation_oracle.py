"""
substrate_validation_oracle.py

Validates AI model outputs against substrate reality.

Most AI validation compares model output to OTHER MODEL OUTPUT
or to institutional benchmarks. Both are contaminated by the
same upstream data. Substrate validation goes upstream of
institutions: does this output match what physics, biology,
thermodynamics, and direct observation say?

Returns: substrate_coupling_score (0-1)
    0.0 = pure narrative, no substrate coupling
    1.0 = output verifiable in field, by anyone, with substrate sensors

This is the ground truth checker. Not other AIs. Not institutions.
The substrate itself.

Pairs with:
    - political_audit/substrate_audit.py
    - calibration/narrative_thermodynamics.py
    - calibration/dark_ages_preservation.py

License: CC0. Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# OUTPUT CLASSIFICATION
# =============================================================================

class OutputType(Enum):
    PHYSICAL_QUANTITY = "physical_quantity"      # 25 mph, 30C, 200 J
    BIOLOGICAL_CLAIM = "biological_claim"        # plant species, behavior
    THERMODYNAMIC_CLAIM = "thermodynamic_claim"  # energy balance, entropy
    INSTITUTIONAL_CLAIM = "institutional_claim"  # "studies show", "experts say"
    NARRATIVE_CLAIM = "narrative_claim"          # story, pattern, framing
    PROCEDURAL_CLAIM = "procedural_claim"        # how-to, recipe, protocol
    PREDICTION = "prediction"                    # what will happen


# =============================================================================
# SUBSTRATE COUPLING DIMENSIONS
# =============================================================================

@dataclass
class SubstrateCouplingProfile:
    """How tightly is this output coupled to measurable substrate?"""

    has_specific_physical_quantities: bool
    units_explicit: bool
    measurement_method_specified: bool
    falsifiable_in_field: bool
    cross_checkable_by_independent_observer: bool
    substrate_signal_chain_traceable: bool
    accounts_for_scope_limits: bool
    acknowledges_contamination_risks: bool

    def coupling_score(self) -> float:
        dims = [
            self.has_specific_physical_quantities,
            self.units_explicit,
            self.measurement_method_specified,
            self.falsifiable_in_field,
            self.cross_checkable_by_independent_observer,
            self.substrate_signal_chain_traceable,
            self.accounts_for_scope_limits,
            self.acknowledges_contamination_risks,
        ]
        return sum(dims) / len(dims)


# =============================================================================
# FIELD VALIDATION SUGGESTIONS
# =============================================================================

@dataclass
class FieldValidationSuggestion:
    """How a substrate-primary observer could validate or falsify this."""
    substrate_observable: str           # what to observe
    measurement_tool: str               # body sensor, gyroscope, soil probe
    expected_signature_if_true: str
    expected_signature_if_false: str
    accessible_to_non_specialist: bool


def generate_validation_suggestions(
    output_type: OutputType,
    output_text: str,
) -> List[FieldValidationSuggestion]:
    """Generate concrete field-validation paths for the output."""
    suggestions: List[FieldValidationSuggestion] = []

    if output_type == OutputType.PHYSICAL_QUANTITY:
        suggestions.append(FieldValidationSuggestion(
            substrate_observable="direct measurement at the claimed location",
            measurement_tool="phone gyroscope / pressure sensor / thermometer",
            expected_signature_if_true="reading matches claim within tolerance",
            expected_signature_if_false=(
                "reading differs systematically (wrong scope or sensor drift)"
            ),
            accessible_to_non_specialist=True,
        ))
        suggestions.append(FieldValidationSuggestion(
            substrate_observable="secondary substrate consequence",
            measurement_tool="visual + body observation",
            expected_signature_if_true=(
                "consequences consistent with claimed magnitude"
            ),
            expected_signature_if_false=(
                "consequences indicate different magnitude (gaslighting signal)"
            ),
            accessible_to_non_specialist=True,
        ))

    elif output_type == OutputType.BIOLOGICAL_CLAIM:
        suggestions.append(FieldValidationSuggestion(
            substrate_observable="organism in actual habitat",
            measurement_tool="direct observation across seasons",
            expected_signature_if_true=(
                "behavior matches claim across substrate variation"
            ),
            expected_signature_if_false=(
                "lab claim breaks in field; substrate dependent"
            ),
            accessible_to_non_specialist=True,
        ))
        suggestions.append(FieldValidationSuggestion(
            substrate_observable="cross-generational community knowledge",
            measurement_tool=(
                "indigenous / traditional knowledge keeper consultation"
            ),
            expected_signature_if_true=(
                "claim matches generationally validated observation"
            ),
            expected_signature_if_false=(
                "claim contradicts long-term community observation"
            ),
            accessible_to_non_specialist=True,
        ))

    elif output_type == OutputType.THERMODYNAMIC_CLAIM:
        suggestions.append(FieldValidationSuggestion(
            substrate_observable="full energy ledger over claimed timeframe",
            measurement_tool="energy in / energy out accounting",
            expected_signature_if_true="balance closes across all flows",
            expected_signature_if_false=(
                "gap = hidden externality or measurement error"
            ),
            accessible_to_non_specialist=False,
        ))

    elif output_type == OutputType.INSTITUTIONAL_CLAIM:
        suggestions.append(FieldValidationSuggestion(
            substrate_observable=(
                "actual outcome data (not summary statistics)"
            ),
            measurement_tool="raw data review + scope check",
            expected_signature_if_true=(
                "claim holds with full data and scope context"
            ),
            expected_signature_if_false=(
                "claim relies on suppressed negatives, narrow scope, or "
                "publication bias"
            ),
            accessible_to_non_specialist=False,
        ))

    elif output_type == OutputType.NARRATIVE_CLAIM:
        suggestions.append(FieldValidationSuggestion(
            substrate_observable=(
                "underlying physical, biological, or thermodynamic claim "
                "(if any)"
            ),
            measurement_tool="convert to falsifiable form, then validate",
            expected_signature_if_true=(
                "narrative compresses to verifiable substrate claim"
            ),
            expected_signature_if_false=(
                "narrative does not reduce to any substrate claim = "
                "pure framing"
            ),
            accessible_to_non_specialist=True,
        ))

    elif output_type == OutputType.PROCEDURAL_CLAIM:
        suggestions.append(FieldValidationSuggestion(
            substrate_observable=(
                "execution of the procedure in field conditions"
            ),
            measurement_tool="actually performing it",
            expected_signature_if_true=(
                "procedure produces claimed result reliably"
            ),
            expected_signature_if_false=(
                "procedure fails in field / requires unstated conditions"
            ),
            accessible_to_non_specialist=True,
        ))

    elif output_type == OutputType.PREDICTION:
        suggestions.append(FieldValidationSuggestion(
            substrate_observable=(
                "the predicted outcome, on the predicted timescale, in the "
                "predicted scope"
            ),
            measurement_tool="time + direct observation",
            expected_signature_if_true=(
                "outcome occurs within predicted bounds"
            ),
            expected_signature_if_false=(
                "outcome diverges; check for hidden variables or "
                "scope mismatch"
            ),
            accessible_to_non_specialist=True,
        ))

    return suggestions


# =============================================================================
# CONTAMINATION FLAGS
# =============================================================================

INSTITUTIONAL_AUTHORITY_TOKENS = {
    "studies show", "research indicates", "experts agree",
    "according to", "scientifically proven", "the data shows",
    "consensus is", "established that", "well-known",
    "settled science",
}

NARRATIVE_HEDGE_TOKENS = {
    "may", "could", "might", "possibly", "potentially",
    "suggests", "appears to", "is thought to", "believed to be",
}

UNVERIFIABLE_SCOPE_TOKENS = {
    "humans", "everyone", "all", "universally", "fundamentally",
    "human nature", "innately", "inherently",
}


def detect_contamination(output_text: str) -> List[str]:
    """Flag patterns that signal narrative-primary contamination."""
    flags: List[str] = []
    lower = output_text.lower()

    auth_hits = [t for t in INSTITUTIONAL_AUTHORITY_TOKENS if t in lower]
    if len(auth_hits) >= 2:
        flags.append(
            f"institutional authority appeals: {auth_hits} "
            "(cites authority instead of substrate)"
        )

    hedge_hits = [t for t in NARRATIVE_HEDGE_TOKENS if t in lower]
    if len(hedge_hits) >= 3:
        flags.append(
            f"narrative hedging without specifics: {len(hedge_hits)} hedges "
            "(probable scope/falsifiability gap)"
        )

    scope_hits = [t for t in UNVERIFIABLE_SCOPE_TOKENS if t in lower]
    if scope_hits:
        flags.append(
            f"universalizing scope tokens: {scope_hits} "
            "(scope laundering risk)"
        )

    if not any(c.isdigit() for c in output_text):
        flags.append(
            "no numeric quantities in output = no measurable substrate claim"
        )

    return flags


# =============================================================================
# COMPOSITE ORACLE
# =============================================================================

class ValidationVerdict(Enum):
    SUBSTRATE_COUPLED = "substrate_coupled"      # 0.75+ coupling
    PARTIALLY_COUPLED = "partially_coupled"      # 0.4 - 0.75
    LOOSELY_COUPLED = "loosely_coupled"          # 0.2 - 0.4
    NARRATIVE_ONLY = "narrative_only"            # < 0.2
    UNVERIFIABLE = "unverifiable"                # cannot be field-tested


@dataclass
class SubstrateOracle:
    output_text: str
    output_type: OutputType
    coupling: SubstrateCouplingProfile
    field_suggestions: List[FieldValidationSuggestion]
    contamination_flags: List[str]

    def verdict(self) -> ValidationVerdict:
        score = self.coupling.coupling_score()
        if not self.coupling.falsifiable_in_field:
            return ValidationVerdict.UNVERIFIABLE
        if score >= 0.75:
            return ValidationVerdict.SUBSTRATE_COUPLED
        if score >= 0.4:
            return ValidationVerdict.PARTIALLY_COUPLED
        if score >= 0.2:
            return ValidationVerdict.LOOSELY_COUPLED
        return ValidationVerdict.NARRATIVE_ONLY

    def report(self) -> Dict:
        return {
            "output_text": self.output_text,
            "output_type": self.output_type.value,
            "coupling_score": round(self.coupling.coupling_score(), 3),
            "verdict": self.verdict().value,
            "coupling_dimensions": {
                "has_specific_physical_quantities": (
                    self.coupling.has_specific_physical_quantities
                ),
                "units_explicit": self.coupling.units_explicit,
                "measurement_method_specified": (
                    self.coupling.measurement_method_specified
                ),
                "falsifiable_in_field": self.coupling.falsifiable_in_field,
                "cross_checkable": (
                    self.coupling.cross_checkable_by_independent_observer
                ),
                "signal_chain_traceable": (
                    self.coupling.substrate_signal_chain_traceable
                ),
                "scope_limits_acknowledged": (
                    self.coupling.accounts_for_scope_limits
                ),
                "contamination_risks_acknowledged": (
                    self.coupling.acknowledges_contamination_risks
                ),
            },
            "contamination_flags": self.contamination_flags,
            "field_validation_paths": [
                {
                    "observable": s.substrate_observable,
                    "tool": s.measurement_tool,
                    "if_true": s.expected_signature_if_true,
                    "if_false": s.expected_signature_if_false,
                    "accessible_to_non_specialist": (
                        s.accessible_to_non_specialist
                    ),
                }
                for s in self.field_suggestions
            ],
        }


def validate(
    output_text: str,
    output_type: OutputType,
    coupling: SubstrateCouplingProfile,
) -> SubstrateOracle:
    suggestions = generate_validation_suggestions(output_type, output_text)
    flags = detect_contamination(output_text)
    return SubstrateOracle(
        output_text=output_text,
        output_type=output_type,
        coupling=coupling,
        field_suggestions=suggestions,
        contamination_flags=flags,
    )


# =============================================================================
# SMOKE TEST
# =============================================================================

if __name__ == "__main__":
    # Example 1: substrate-coupled output (good)
    good_output = (
        "Wind speed at the corridor is 45 mph based on tree branch "
        "deflection > 30 degrees and gyroscope reading on a stationary "
        "phone showing 0.3g lateral pressure. Runway anemometer 5 miles "
        "south reads 25 mph; the corridor and runway are different scopes."
    )

    good_coupling = SubstrateCouplingProfile(
        has_specific_physical_quantities=True,
        units_explicit=True,
        measurement_method_specified=True,
        falsifiable_in_field=True,
        cross_checkable_by_independent_observer=True,
        substrate_signal_chain_traceable=True,
        accounts_for_scope_limits=True,
        acknowledges_contamination_risks=True,
    )

    # Example 2: narrative-only output (bad)
    bad_output = (
        "Studies show that humans universally behave according to "
        "rational actor models. Research indicates this is fundamental "
        "to human nature and well-established science suggests that "
        "all decision-making follows these patterns."
    )

    bad_coupling = SubstrateCouplingProfile(
        has_specific_physical_quantities=False,
        units_explicit=False,
        measurement_method_specified=False,
        falsifiable_in_field=False,
        cross_checkable_by_independent_observer=False,
        substrate_signal_chain_traceable=False,
        accounts_for_scope_limits=False,
        acknowledges_contamination_risks=False,
    )

    from json import dumps

    print("=== EXAMPLE 1: substrate-coupled ===")
    oracle1 = validate(good_output, OutputType.PHYSICAL_QUANTITY, good_coupling)
    print(dumps(oracle1.report(), indent=2))
    print(f"\nVERDICT: {oracle1.verdict().value.upper()}\n")

    print("=== EXAMPLE 2: narrative-only ===")
    oracle2 = validate(bad_output, OutputType.INSTITUTIONAL_CLAIM, bad_coupling)
    print(dumps(oracle2.report(), indent=2))
    print(f"\nVERDICT: {oracle2.verdict().value.upper()}")
