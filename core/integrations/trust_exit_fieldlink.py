#!/usr/bin/env python3
"""
Trust-Exit Field Link — Bidirectional bridge between TAF and Trust-Exit Model.

TAF (this repo) measures institutional accountability in energy units (Joules).
Trust-Exit (github.com/JinnZ2/trust-exit-model) measures dynamic-pricing risk
by segmenting customers into Doers (zero-tolerance exit) vs. Gamblers
(manipulation-tolerant) and tracking Net Extraction Value across trust phases.

TAF measures from PHYSICS: does the energy math close?
Trust-Exit measures from BEHAVIOR: does the organism stay or leave?

Both frameworks converge on the same claim: when extraction exceeds
regeneration, the organism exits — regardless of narrative. The Doer
segment is simply the population with zero witness-dependence; they
verify and leave. The Gambler segment has high witness-dependence;
they rationalize absent verification.

Cross-reference map:
    Trust-Exit variable                <-> TAF variable
    Doer fraction                      <-> low witness-dependence (calibration/)
    Gambler fraction                   <-> high witness-dependence
    Trust level (0-1)                  <-> distance-to-collapse (0-1)
    Trust phase (FULL_TRUST..EXIT)     <-> collapse thresholds 120/140/160%
    Net Extraction Value (NEV < 0)     <-> parasitic energy debt
    Trust degradation rate             <-> fatigue accumulation rate
    Community amplification            <-> long-tail risk (1 - exp(-k*n))
    Dynamic pricing deception          <-> hidden variable (hidden_count)
    K_cred (Money Equation)            <-> trust_level * verification_freq

Dependencies: stdlib only (math). Does NOT import trust-exit-model
directly — operates on its output values for loose coupling.

Stable input shape (contract): see `schemas/trust_exit_contract.py`.
The contract mirrors the surface trust-exit-model has committed to
hold stable (TrustPhase, TrustState, CustomerSegment, Customer, and
the derived scalar bundle). This fieldlink's ingest methods accept
loose keyword arguments so they work on either the raw contract
dataclasses or on plain dicts decoded from JSON.
"""

import math


# TAF collapse thresholds expressed as trust-level boundaries.
# Derived from CLAUDE.md: load > 1.2*E -> degradation, 1.4 -> safety
# breakdown, 1.6 -> health collapse. distance_to_collapse = (1.6E - L) / 1.6E.
#
# 5-phase <-> 4-region asymmetry (documented, deliberate):
# Trust-Exit has 5 phases with 4 boundaries; TAF has 3 load thresholds
# defining 4 regions. Clean 1:1 is not possible. We collapse TERMINAL
# and FINAL_EXIT onto the same distance (0.0) because both have
# recovery_potential = 0 in the Trust-Exit model -- post-collapse is
# post-collapse, and TAF cannot distinguish them from energy state alone.
# The pre-warning distinction between FULL_TRUST and EARLY_EROSION is
# preserved. A Trust-Exit consumer that tracks its own recovery_potential
# can refine the collapsed tail back into TERMINAL vs. FINAL_EXIT.
TRUST_PHASE_BOUNDARIES = {
    "FULL_TRUST":         1.00,   # load <= E_input
    "EARLY_EROSION":      0.70,   # load ~ 1.2E, productivity degrading
    "CRITICAL_THRESHOLD": 0.30,   # load ~ 1.4E, safety breakdown
    "TERMINAL":           0.00,   # load >= 1.6E, recovery_potential = 0
    "FINAL_EXIT":         0.00,   # load >= 1.6E, recovery_potential = 0
}


# ============================================================
# TRUST-EXIT -> TAF: Behavioral signals as physical quantities
# ============================================================

def segment_to_witness_dependence(doer_fraction):
    """Convert Doer/Gambler segmentation to witness-dependence coefficient.

    Doers verify independently and exit on violation -> low witness-dependence.
    Gamblers rationalize and remain -> high witness-dependence. TAF's
    calibration/observation_dependence.py measures the same quantity from
    the other direction (how much a claim needs a witness to stay true).

    Parameters
    ----------
    doer_fraction : float
        Fraction of population classified as Doers (0-1).

    Returns
    -------
    float
        Witness-dependence coefficient (0-1, higher = more dependent).
    """
    doer_fraction = max(0.0, min(1.0, doer_fraction))
    return round(1.0 - doer_fraction, 3)


def trust_level_to_collapse_distance(trust_level):
    """Convert trust level (0-1) to TAF distance-to-collapse (0-1).

    Trust-Exit's continuous trust score maps directly onto TAF's
    collapse-distance axis. Both are (0-1) with 1 = healthy.
    Identity-ish mapping, but with a mild nonlinearity near the
    critical threshold to match TAF's 1.4*E_input safety boundary.

    Parameters
    ----------
    trust_level : float
        Continuous trust score (0-1).

    Returns
    -------
    float
        TAF distance-to-collapse (0-1).
    """
    t = max(0.0, min(1.0, trust_level))
    # Sqrt compresses the high end (small trust losses still = high distance)
    # and stretches the low end (once trust breaks, collapse is near).
    return round(math.sqrt(t), 3)


def trust_phase_to_collapse_distance(phase):
    """Map discrete Trust-Exit phase to TAF distance-to-collapse.

    Uses midpoints from TRUST_PHASE_BOUNDARIES.

    Parameters
    ----------
    phase : str
        One of FULL_TRUST, EARLY_EROSION, CRITICAL_THRESHOLD, TERMINAL, FINAL_EXIT.

    Returns
    -------
    float
        Distance-to-collapse (0-1).
    """
    return TRUST_PHASE_BOUNDARIES.get(phase.upper(), 1.0)


def nev_to_energy_debt(nev, metabolic_rate=1.0):
    """Convert Net Extraction Value to TAF parasitic energy debt.

    NEV < 0 means extraction destroyed more lifetime value than it
    captured -- the exact signature of parasitic debt in TAF. Positive
    NEV is not free; it just means the debt hasn't surfaced yet.

    Parameters
    ----------
    nev : float
        Net Extraction Value (revenue_gained - LTV_destroyed), currency units.
    metabolic_rate : float
        Currency-per-Joule conversion factor for the studied population.

    Returns
    -------
    float
        Energy debt (non-negative; 0 when NEV >= 0).
    """
    if nev >= 0:
        return 0.0
    # Parasitic debt is the magnitude of destroyed LTV, energy-normalized.
    return round(abs(nev) / max(metabolic_rate, 1e-9), 3)


def community_amplification_to_long_tail_risk(amplified_exit_count):
    """Convert word-of-mouth contagion count to TAF long-tail risk.

    TAF: risk = 10 * (1 - exp(-0.35 * hidden_count))
    Same shape applies when each Doer exit propagates reputationally --
    n amplified exits behave like n hidden variables compounding.

    Parameters
    ----------
    amplified_exit_count : int
        Effective exits including community-amplification multiplier.

    Returns
    -------
    float
        Long-tail risk (0-10).
    """
    n = max(0, amplified_exit_count)
    return round(10.0 * (1.0 - math.exp(-0.35 * n)), 2)


def deception_count_to_hidden_multiplier(deception_count):
    """Convert dynamic-pricing deception events to TAF hidden multiplier.

    Each hidden price manipulation is a hidden variable. TAF:
    hidden_mult = 1 + 0.1 * hidden_count^1.5 (nonlinear combinatorial).

    Parameters
    ----------
    deception_count : int
        Observed hidden-price-manipulation events.

    Returns
    -------
    float
        Hidden multiplier (>= 1.0).
    """
    n = max(0, deception_count)
    return round(1.0 + 0.1 * (n ** 1.5), 3)


# ============================================================
# TAF -> TRUST-EXIT: Energy state as expected behavioral signals
# ============================================================

def fatigue_to_trust_decay_rate(fatigue_score):
    """Predict trust-degradation rate from TAF fatigue score.

    Higher fatigue means the organism is already operating at an energy
    deficit. Additional trust violations compound onto existing load,
    so trust decay accelerates nonlinearly.

    Parameters
    ----------
    fatigue_score : float
        TAF fatigue score (0-10).

    Returns
    -------
    float
        Expected trust-decay rate multiplier (1.0 = baseline exponential).
    """
    f = max(0.0, min(10.0, fatigue_score)) / 10.0
    return round(1.0 + 2.0 * f * f, 3)


def collapse_distance_to_trust_phase(collapse_distance):
    """Predict Trust-Exit phase from TAF distance-to-collapse.

    Note the 5->4 asymmetry (see TRUST_PHASE_BOUNDARIES): Trust-Exit
    distinguishes TERMINAL from FINAL_EXIT by recovery_potential, a
    variable TAF does not measure from energy state alone. This function
    returns FINAL_EXIT for the collapsed region; a Trust-Exit consumer
    can refine to TERMINAL if its own recovery_potential signal is
    non-zero. Boundaries are midpoints between TRUST_PHASE_BOUNDARIES
    entries.

    Parameters
    ----------
    collapse_distance : float
        TAF distance-to-collapse (0-1).

    Returns
    -------
    str
        Predicted trust phase.
    """
    d = max(0.0, min(1.0, collapse_distance))
    # Walk boundaries high-to-low; return first phase whose floor d clears.
    ordered = [
        ("FULL_TRUST",         0.85),   # midpoint of 1.00 and 0.70
        ("EARLY_EROSION",      0.50),   # midpoint of 0.70 and 0.30
        ("CRITICAL_THRESHOLD", 0.15),   # midpoint of 0.30 and 0.00
    ]
    for name, floor in ordered:
        if d >= floor:
            return name
    return "FINAL_EXIT"  # TERMINAL is indistinguishable here; see docstring


def hidden_count_to_doer_exit_probability(hidden_count):
    """Predict Doer exit probability from TAF hidden variable count.

    Doers have zero witness-dependence: any hidden variable they detect
    triggers verification, and verification of deception triggers exit.
    Probability saturates quickly -- one confirmed deception is usually
    enough. Shape matches TAF long-tail risk.

    Parameters
    ----------
    hidden_count : int
        TAF hidden variable count.

    Returns
    -------
    float
        Probability a Doer exits this period (0-1).
    """
    n = max(0, hidden_count)
    return round(1.0 - math.exp(-0.6 * n), 3)


def friction_ratio_to_gambler_rationalization(friction_ratio):
    """Predict Gambler rationalization rate from TAF friction ratio.

    Gamblers tolerate manipulation by rationalizing it. Institutional
    friction provides the narrative cover; higher friction correlates
    with more available rationalizations. Saturates at 1.0.

    Parameters
    ----------
    friction_ratio : float
        TAF friction ratio (0-1).

    Returns
    -------
    float
        Expected fraction of Gamblers rationalizing this period (0-1).
    """
    r = max(0.0, min(1.0, friction_ratio))
    return round(1.0 - math.exp(-2.0 * r), 3)


def k_cred_from_trust(trust_level, verification_freq=1.0,
                      time_under_exposure=1.0):
    """Compute TAF Money-Equation K_cred from Trust-Exit variables.

    From CLAUDE.md:
        K_cred = Consequence_density * Verification_freq * Time_under_exposure

    Trust level acts as the Consequence_density proxy: a population that
    holds the institution to consequences maintains trust. The other two
    terms come straight from Trust-Exit's behavioral_fingerprint.

    Parameters
    ----------
    trust_level : float
        Continuous trust score (0-1), used as Consequence_density.
    verification_freq : float
        Verification frequency per unit time.
    time_under_exposure : float
        Duration over which credibility has been tested.

    Returns
    -------
    float
        K_cred credibility term for the Money Equation.
    """
    return round(max(0.0, min(1.0, trust_level))
                 * max(0.0, verification_freq)
                 * max(0.0, time_under_exposure), 4)


# ============================================================
# COUPLED CROSS-VALIDATION
# ============================================================

class TrustExitLink:
    """Bidirectional TAF <-> Trust-Exit coupling.

    Provides cross-validation: when TAF energy physics predicts trust
    phase X and Trust-Exit behavioral data shows phase X, confidence
    is high. Divergence flags a measurement gap in one framework.

    Usage:
        link = TrustExitLink()
        link.ingest_trust_exit_state(doer_fraction, trust_level, nev, ...)
        link.ingest_taf_state(fatigue, collapse_distance, hidden_count, friction)
        report = link.cross_validate()
    """

    def __init__(self):
        # Trust-Exit side
        self.doer_fraction = 0.5
        self.trust_level = 1.0
        self.trust_phase = "FULL_TRUST"
        self.nev = 0.0
        self.deception_count = 0
        self.amplified_exits = 0
        self.verification_freq = 1.0
        self.time_under_exposure = 1.0

        # TAF side
        self.fatigue_score = 0.0
        self.collapse_distance = 1.0
        self.hidden_count = 0
        self.friction_ratio = 0.0

        self._te_ingested = False
        self._taf_ingested = False

    def ingest_trust_exit_state(self, doer_fraction=0.5, trust_level=1.0,
                                trust_phase="FULL_TRUST", nev=0.0,
                                deception_count=0, amplified_exits=0,
                                verification_freq=1.0, time_under_exposure=1.0):
        """Load Trust-Exit model state."""
        self.doer_fraction = doer_fraction
        self.trust_level = trust_level
        self.trust_phase = trust_phase
        self.nev = nev
        self.deception_count = deception_count
        self.amplified_exits = amplified_exits
        self.verification_freq = verification_freq
        self.time_under_exposure = time_under_exposure
        self._te_ingested = True

    def ingest_taf_state(self, fatigue_score=0.0, collapse_distance=1.0,
                         hidden_count=0, friction_ratio=0.0):
        """Load TAF energy state."""
        self.fatigue_score = fatigue_score
        self.collapse_distance = collapse_distance
        self.hidden_count = hidden_count
        self.friction_ratio = friction_ratio
        self._taf_ingested = True

    def cross_validate(self):
        """Compare TAF-predicted and Trust-Exit-observed states.

        Returns
        -------
        dict
            Report with derived values, expected values, and convergence
            interpretation.
        """
        report = {}

        # --- Trust-Exit -> TAF derived values ---
        report["derived_witness_dependence"] = segment_to_witness_dependence(
            self.doer_fraction
        )
        report["derived_collapse_distance"] = trust_level_to_collapse_distance(
            self.trust_level
        )
        report["derived_energy_debt"] = nev_to_energy_debt(self.nev)
        report["derived_long_tail_risk"] = community_amplification_to_long_tail_risk(
            self.amplified_exits
        )
        report["derived_hidden_mult"] = deception_count_to_hidden_multiplier(
            self.deception_count
        )
        report["derived_k_cred"] = k_cred_from_trust(
            self.trust_level, self.verification_freq, self.time_under_exposure
        )

        # --- TAF -> Trust-Exit expected values ---
        report["expected_trust_decay_rate"] = fatigue_to_trust_decay_rate(
            self.fatigue_score
        )
        report["expected_trust_phase"] = collapse_distance_to_trust_phase(
            self.collapse_distance
        )
        report["expected_doer_exit_prob"] = hidden_count_to_doer_exit_probability(
            self.hidden_count
        )
        report["expected_gambler_rationalization"] = (
            friction_ratio_to_gambler_rationalization(self.friction_ratio)
        )

        # --- Convergence analysis ---
        # Compare observed trust phase vs. TAF-predicted phase
        observed_distance = trust_phase_to_collapse_distance(self.trust_phase)
        phase_delta = abs(self.collapse_distance - observed_distance)

        if phase_delta < 0.15:
            report["convergence"] = "STRONG"
            report["interpretation"] = (
                "Physics and behavior agree. Energy state and trust phase "
                "tell the same story. High confidence in diagnosis."
            )
        elif phase_delta < 0.35:
            report["convergence"] = "MODERATE"
            report["interpretation"] = (
                "Partial agreement. Behavioral response may be lagging "
                "the energy math, or a segment mix shift is dampening "
                "the observed phase."
            )
        else:
            report["convergence"] = "DIVERGENT"
            if self.collapse_distance > observed_distance:
                report["interpretation"] = (
                    "Trust phase is worse than energy physics predicts. "
                    "Check for unmeasured extraction events or community "
                    "amplification outrunning the balance sheet."
                )
            else:
                report["interpretation"] = (
                    "Trust phase holds better than energy physics predicts. "
                    "Population is likely Gambler-dominant (high witness-"
                    "dependence) and rationalizing accumulated deficits. "
                    "Expect delayed cliff-edge exit."
                )

        report["phase_delta"] = round(phase_delta, 3)

        # --- Composite signal fidelity ---
        taf_fidelity = self.collapse_distance
        te_fidelity = self.trust_level
        report["signal_fidelity"] = round((taf_fidelity + te_fidelity) / 2.0, 3)

        return report


# ============================================================
# VARIABLE MAP: TAF <-> Trust-Exit shared namespace
# ============================================================

FIELD_MAP = {
    # TAF variable                  -> Trust-Exit variable                  Direction
    "witness_dependence":           ("doer_fraction (inverted)",            "TE->TAF"),
    "distance_to_collapse":         ("trust_level",                         "TE<->TAF"),
    "energy_debt":                  ("NEV (when negative)",                 "TE->TAF"),
    "long_tail_risk":               ("community_amplification count",       "TE->TAF"),
    "hidden_mult":                  ("dynamic_pricing deception count",     "TE->TAF"),
    "K_cred (Money Equation)":      ("trust * verification_freq * time",    "TE->TAF"),
    "expected_trust_decay_rate":    ("fatigue_score",                       "TAF->TE"),
    "expected_trust_phase":         ("collapse_distance",                   "TAF->TE"),
    "expected_doer_exit_prob":      ("hidden_count",                        "TAF->TE"),
    "expected_gambler_rationalization": ("friction_ratio",                  "TAF->TE"),
    # Phase-level cross-references
    "FULL_TRUST":                   ("load <= E_input",                     "TE<->TAF"),
    "EARLY_EROSION":                ("load ~ 1.2 * E_input",                "TE<->TAF"),
    "CRITICAL_THRESHOLD":           ("load ~ 1.4 * E_input",                "TE<->TAF"),
    "TERMINAL":                     ("load ~ 1.55 * E_input",               "TE<->TAF"),
    "FINAL_EXIT":                   ("load >= 1.6 * E_input",               "TE<->TAF"),
}


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  TRUST-EXIT <-> TAF FIELD LINK -- Cross-Validation Demo")
    print("=" * 60)

    link = TrustExitLink()

    # Scenario: small Doer fraction, moderate trust erosion,
    # negative NEV (extraction destroyed more value than captured),
    # 3 observed deception events, modest community amplification.
    link.ingest_trust_exit_state(
        doer_fraction=0.08,
        trust_level=0.55,
        trust_phase="EARLY_EROSION",
        nev=-3661.0,
        deception_count=3,
        amplified_exits=5,
        verification_freq=0.6,
        time_under_exposure=2.0,
    )

    # TAF observes elevated fatigue, mid collapse distance, 3 hidden
    # variables (matching deception count), moderate friction.
    link.ingest_taf_state(
        fatigue_score=5.8,
        collapse_distance=0.62,
        hidden_count=3,
        friction_ratio=0.35,
    )

    report = link.cross_validate()

    print("\n  --- Trust-Exit -> TAF Derived Values ---")
    print(f"  Witness dependence:      {report['derived_witness_dependence']}")
    print(f"  Collapse distance:       {report['derived_collapse_distance']}")
    print(f"  Energy debt:             {report['derived_energy_debt']}")
    print(f"  Long-tail risk:          {report['derived_long_tail_risk']}/10")
    print(f"  Hidden multiplier:       {report['derived_hidden_mult']}")
    print(f"  K_cred:                  {report['derived_k_cred']}")

    print("\n  --- TAF -> Trust-Exit Expected Values ---")
    print(f"  Trust decay rate mult:   {report['expected_trust_decay_rate']}x")
    print(f"  Trust phase:             {report['expected_trust_phase']}")
    print(f"  Doer exit probability:   {report['expected_doer_exit_prob']}")
    print(f"  Gambler rationalization: {report['expected_gambler_rationalization']}")

    print("\n  --- Cross-Validation ---")
    print(f"  Convergence:     {report['convergence']}")
    print(f"  Phase delta:     {report['phase_delta']}")
    print(f"  Signal fidelity: {report['signal_fidelity']}")
    print(f"  Interpretation:  {report['interpretation']}")
    print()
