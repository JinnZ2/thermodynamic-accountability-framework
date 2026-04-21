#!/usr/bin/env python3
"""
Metabolic-Accounting Field Link -- Bidirectional bridge between TAF
and metabolic-accounting.

TAF (this repo) measures institutional accountability in energy units.
Metabolic-accounting (github.com/JinnZ2/metabolic-accounting) measures
the same physics from the firm-P&L angle: basins (soil/air/water/bio/
community) as balance-sheet line items, metabolic_profit vs
reported_profit as the two-line split that makes parasitic extraction
visible.

The concept overlap is the strongest of any upstream TAF mirrors:
metabolic_profit vs reported_profit IS the Money Equation's physics-
vs-narrative split, and cumulative_environment_loss IS parasitic
energy debt in xdu units.

Cross-reference map:
    metabolic-accounting              <-> TAF concept
    Verdict.time_to_red               <-> distance_to_collapse (inverse)
    Verdict.profit_gap                <-> hidden_count proxy
    Verdict.sustainable_yield_signal  <-> status vocabulary
    Verdict.basin_trajectory          <-> fatigue direction
    GlucoseFlow.cumulative_env_loss   <-> parasitic_energy_debt (xdu)
    GlucoseFlow.reserve_drawdown_cost <-> short-term extraction load
    GlucoseFlow.regeneration_debt     <-> unpaid metabolic cost
    GlucoseFlow.irreversible_metrics  <-> hidden_count (permanent)
    ExergyFlow.destroyed              <-> entropy / waste growth
    BLACK signal                      <-> distance_to_collapse = 0
                                          (irreversibility)

Stable input shape (contract): see schemas/metabolic_accounting_contract.py
which mirrors the 4 canonical dataclasses (ExergyFlow, GlucoseFlow,
BasinState, Verdict) and the 7 numbered invariants. This fieldlink
accepts loose keyword arguments so it works on either the contract
dataclasses or plain dicts decoded from JSON.

Dependencies: stdlib only (math). Does NOT import metabolic-accounting
at runtime; coupling via output values keeps both repos independently
runnable.

License: CC0 1.0 Universal.
"""

from __future__ import annotations

import math


# ============================================================
# MA -> TAF: Firm-layer measurements as substrate quantities
# ============================================================

def time_to_red_to_collapse_distance(time_to_red, horizon_periods=20.0):
    """Convert Verdict.time_to_red to TAF distance_to_collapse.

    time_to_red is in "periods" (upstream-defined, typically quarters
    or years). distance_to_collapse is a TAF 0-1 metric with 1 = safe.
    A larger time_to_red within the horizon maps to a larger distance.
    None means no RED is projected -> distance_to_collapse = 1.0.

    Parameters
    ----------
    time_to_red : float or None
        From Verdict.time_to_red.
    horizon_periods : float
        Periods considered "fully safe" if time_to_red exceeds it.

    Returns
    -------
    float
        distance_to_collapse in [0, 1].
    """
    if time_to_red is None:
        return 1.0
    t = float(time_to_red)
    if t <= 0.0:
        return 0.0
    if t >= horizon_periods:
        return 1.0
    return round(t / horizon_periods, 3)


def cumulative_loss_to_energy_debt(cumulative_environment_loss,
                                    xdu_to_joule=1.0):
    """Convert GlucoseFlow.cumulative_environment_loss to TAF energy debt.

    cumulative_environment_loss is in xdu (exergy-destruction units)
    per invariant 7. TAF's parasitic_energy_debt is in joules. The
    conversion factor is caller-supplied because xdu is defined
    relative to the upstream's XduConverter, which is declarative,
    not physical.

    Parameters
    ----------
    cumulative_environment_loss : float
        From GlucoseFlow.
    xdu_to_joule : float
        Conversion factor. Default 1.0 leaves values in xdu; callers
        with a calibrated converter should pass their own.

    Returns
    -------
    float
        Energy debt (non-negative).
    """
    c = max(0.0, float(cumulative_environment_loss))
    return round(c * max(0.0, float(xdu_to_joule)), 3)


def profit_gap_to_hidden_count(profit_gap, revenue):
    """Convert Verdict.profit_gap to TAF hidden_count estimate.

    profit_gap = reported_profit - metabolic_profit. A positive gap
    indicates hidden costs not visible in conventional accounting.
    TAF's hidden_count is an integer in [0, 10]. Map the gap as a
    fraction of revenue to a saturating count.

    Parameters
    ----------
    profit_gap : float
        May be math.inf (irreversibility).
    revenue : float
        Divisor for normalization.

    Returns
    -------
    int
        hidden_count in [0, 10].
    """
    if profit_gap == math.inf:
        return 10
    if profit_gap <= 0 or revenue <= 0:
        return 0
    ratio = profit_gap / revenue
    # Saturating: ratio=0.1 -> ~3; ratio=0.3 -> ~7; ratio=1.0 -> ~10
    count = 10.0 * (1.0 - math.exp(-3.0 * ratio))
    return int(round(min(10.0, count)))


def sustainable_yield_signal_to_status(signal):
    """Convert Verdict.sustainable_yield_signal to TAF status.

    Metabolic-accounting uses a 4-level vocabulary (GREEN/AMBER/RED/
    BLACK); TAF uses 3 (GREEN/YELLOW/RED). BLACK is reserved for
    irreversibility per invariant 4 and does NOT collapse into RED --
    this function returns a distinct "BLACK" string so consumers can
    handle it specially; map to RED only with explicit loss of
    information.

    Parameters
    ----------
    signal : str or SustainableYieldSignal
        From Verdict.

    Returns
    -------
    str
        One of GREEN / YELLOW / RED / BLACK.
    """
    s = getattr(signal, "value", signal)
    return {
        "GREEN": "GREEN",
        "AMBER": "YELLOW",
        "RED": "RED",
        "BLACK": "BLACK",
    }.get(s, "YELLOW")


def basin_trajectory_to_fatigue_direction(trajectory):
    """Convert Verdict.basin_trajectory to a TAF fatigue trend.

    Returns -1 (improving), 0 (stable), or +1 (degrading). Scales
    into downstream fatigue-accumulation terms.
    """
    s = getattr(trajectory, "value", trajectory)
    return {"IMPROVING": -1, "STABLE": 0, "DEGRADING": 1}.get(s, 0)


def irreversibility_to_distance_clamp(verdict_signal, irreversible_metrics):
    """Apply invariant 4: if BLACK or any irreversible_metrics, clamp
    TAF distance_to_collapse to 0 regardless of other signals.

    Returns
    -------
    (clamp_required, reason)
        clamp_required : bool
        reason         : human-readable if clamped, else empty
    """
    s = getattr(verdict_signal, "value", verdict_signal)
    if s == "BLACK":
        return (True, "Verdict.sustainable_yield_signal == BLACK: "
                      "irreversibility already breached.")
    if irreversible_metrics:
        return (True,
                f"Verdict.irreversible_metrics non-empty: "
                f"{list(irreversible_metrics)}")
    return (False, "")


# ============================================================
# TAF -> MA: Energy state as expected firm-layer readings
# ============================================================

def distance_to_collapse_to_expected_time_to_red(distance_to_collapse,
                                                  horizon_periods=20.0):
    """Predict expected Verdict.time_to_red from TAF distance.

    Inverse of time_to_red_to_collapse_distance.
    """
    if distance_to_collapse is None:
        return None
    d = max(0.0, min(1.0, float(distance_to_collapse)))
    if d >= 1.0:
        return None   # no RED projected
    return round(d * horizon_periods, 3)


def fatigue_to_expected_signal(fatigue_score):
    """Predict expected sustainable_yield_signal from TAF fatigue.

    Bands from the TAF fatigue thresholds (0-10):
        < 4 -> GREEN
        4-6 -> AMBER
        6-8 -> RED
        > 8 -> likely BLACK if damage is confirmed irreversible
               (we cannot know from fatigue alone, so return RED
               and flag the ambiguity in notes)
    """
    if fatigue_score is None:
        return ("GREEN", "")
    f = max(0.0, min(10.0, float(fatigue_score)))
    if f < 4.0:
        return ("GREEN", "")
    if f < 6.0:
        return ("AMBER", "")
    if f < 8.0:
        return ("RED", "")
    return ("RED",
            "Fatigue above 8.0 typically co-occurs with "
            "irreversibility; check Verdict.irreversible_metrics "
            "to determine if BLACK is warranted.")


def hidden_count_to_expected_profit_gap(hidden_count, revenue):
    """Invert profit_gap_to_hidden_count for a TAF -> MA prediction.

    Returns
    -------
    float
        Expected profit_gap in the same currency as `revenue`.
    """
    if hidden_count is None or revenue <= 0:
        return 0.0
    n = max(0, min(10, int(hidden_count)))
    if n >= 10:
        return math.inf
    ratio = -math.log(1.0 - n / 10.0) / 3.0
    return round(ratio * revenue, 3)


# ============================================================
# COUPLED CROSS-VALIDATION
# ============================================================

class MetabolicLink:
    """Bidirectional TAF <-> metabolic-accounting coupling.

    Usage:
        link = MetabolicLink()
        link.ingest_metabolic(time_to_red=14.0, profit_gap=28.6,
                              revenue=1000.0,
                              sustainable_yield_signal="AMBER",
                              basin_trajectory="DEGRADING",
                              cumulative_environment_loss=1.2,
                              irreversible_metrics=[])
        link.ingest_taf(fatigue_score=5.5, distance_to_collapse=0.70,
                        hidden_count=3)
        report = link.cross_validate()
    """

    def __init__(self):
        # MA side
        self.time_to_red = None
        self.profit_gap = 0.0
        self.revenue = 0.0
        self.sustainable_yield_signal = None
        self.basin_trajectory = None
        self.cumulative_environment_loss = 0.0
        self.irreversible_metrics = ()

        # TAF side
        self.fatigue_score = None
        self.distance_to_collapse = None
        self.hidden_count = None

    def ingest_metabolic(self, *, time_to_red=None, profit_gap=0.0,
                         revenue=0.0, sustainable_yield_signal=None,
                         basin_trajectory=None,
                         cumulative_environment_loss=0.0,
                         irreversible_metrics=()):
        self.time_to_red = time_to_red
        self.profit_gap = profit_gap
        self.revenue = revenue
        self.sustainable_yield_signal = sustainable_yield_signal
        self.basin_trajectory = basin_trajectory
        self.cumulative_environment_loss = cumulative_environment_loss
        self.irreversible_metrics = tuple(irreversible_metrics)

    def ingest_taf(self, *, fatigue_score=None, distance_to_collapse=None,
                   hidden_count=None):
        self.fatigue_score = fatigue_score
        self.distance_to_collapse = distance_to_collapse
        self.hidden_count = hidden_count

    def cross_validate(self) -> dict:
        report = {}

        # MA -> TAF derived
        report["derived_collapse_distance"] = time_to_red_to_collapse_distance(
            self.time_to_red)
        report["derived_energy_debt"] = cumulative_loss_to_energy_debt(
            self.cumulative_environment_loss)
        report["derived_hidden_count"] = profit_gap_to_hidden_count(
            self.profit_gap, self.revenue)
        report["derived_status"] = sustainable_yield_signal_to_status(
            self.sustainable_yield_signal)
        report["derived_fatigue_direction"] = (
            basin_trajectory_to_fatigue_direction(self.basin_trajectory))

        clamp, reason = irreversibility_to_distance_clamp(
            self.sustainable_yield_signal, self.irreversible_metrics)
        if clamp:
            report["derived_collapse_distance"] = 0.0
            report["irreversibility_clamp"] = reason

        # TAF -> MA expected
        report["expected_time_to_red"] = (
            distance_to_collapse_to_expected_time_to_red(
                self.distance_to_collapse))
        signal, note = fatigue_to_expected_signal(self.fatigue_score)
        report["expected_signal"] = signal
        if note:
            report["expected_signal_note"] = note
        report["expected_profit_gap"] = hidden_count_to_expected_profit_gap(
            self.hidden_count, self.revenue)

        # Convergence check on the strongest pairing:
        # observed sustainable_yield_signal vs expected from fatigue
        observed = report["derived_status"]
        expected = report["expected_signal"]
        if observed in ("GREEN", "YELLOW", "RED", "BLACK") and expected:
            # Map both to a severity rank 0-3 (BLACK = 3 in both sides)
            rank = {"GREEN": 0, "YELLOW": 1, "AMBER": 1,
                    "RED": 2, "BLACK": 3}
            delta = abs(rank.get(observed, 1) - rank.get(expected, 1))
            if delta == 0:
                report["convergence"] = "STRONG"
                report["interpretation"] = (
                    "Firm-layer signal and energy-layer prediction "
                    "agree. High confidence in joint diagnosis.")
            elif delta == 1:
                report["convergence"] = "MODERATE"
                report["interpretation"] = (
                    "Adjacent-level disagreement. One framework is "
                    "lagging the other; monitor for convergence.")
            else:
                report["convergence"] = "DIVERGENT"
                report["interpretation"] = (
                    "Signals disagree by more than one severity step. "
                    "Check for: (a) BLACK masking as RED elsewhere, "
                    "(b) reporting lag on one side, (c) missing "
                    "irreversible_metrics on the MA side.")
        else:
            report["convergence"] = "INSUFFICIENT_DATA"
            report["interpretation"] = (
                "Need both sustainable_yield_signal (from MA) and "
                "fatigue_score (from TAF) for primary convergence.")

        return report


# ============================================================
# VARIABLE MAP: TAF <-> metabolic-accounting shared namespace
# ============================================================

FIELD_MAP = {
    # TAF concept                  -> MA source                          Direction
    "distance_to_collapse":        ("Verdict.time_to_red",               "MA->TAF"),
    "parasitic_energy_debt":       ("GlucoseFlow.cumulative_env_loss",   "MA->TAF"),
    "hidden_count":                ("Verdict.profit_gap / revenue",      "MA->TAF"),
    "status (GREEN/YELLOW/RED/BLACK)": ("Verdict.sustainable_yield_signal",
                                        "MA->TAF (BLACK preserved)"),
    "fatigue_direction":           ("Verdict.basin_trajectory",          "MA->TAF"),
    "expected_time_to_red":        ("distance_to_collapse",              "TAF->MA"),
    "expected_signal":             ("fatigue_score",                     "TAF->MA"),
    "expected_profit_gap":         ("hidden_count",                      "TAF->MA"),
    # Irreversibility override
    "collapse_distance=0 clamp":   ("BLACK signal OR irreversible_metrics "
                                    "non-empty",                         "MA->TAF"),
}


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  METABOLIC <-> TAF FIELD LINK -- Cross-Validation Demo")
    print("=" * 60)

    link = MetabolicLink()

    # MA readings from the sample in the repo README:
    # reported 399.33, metabolic 370.73, gap 28.60, environment_loss 0.0307
    link.ingest_metabolic(
        time_to_red=14.0,
        profit_gap=28.60,
        revenue=1000.0,
        sustainable_yield_signal="AMBER",
        basin_trajectory="DEGRADING",
        cumulative_environment_loss=0.0307,
        irreversible_metrics=(),
    )

    # TAF state consistent with the AMBER reading:
    link.ingest_taf(
        fatigue_score=5.0,
        distance_to_collapse=0.70,
        hidden_count=3,
    )

    report = link.cross_validate()

    print("\n  --- MA -> TAF Derived ---")
    print(f"  Collapse distance:     {report['derived_collapse_distance']}")
    print(f"  Energy debt (xdu):     {report['derived_energy_debt']}")
    print(f"  Hidden count:          {report['derived_hidden_count']}")
    print(f"  Status:                {report['derived_status']}")
    print(f"  Fatigue direction:     {report['derived_fatigue_direction']}")

    print("\n  --- TAF -> MA Expected ---")
    print(f"  time_to_red:           {report['expected_time_to_red']}")
    print(f"  sustainable_yield:     {report['expected_signal']}")
    print(f"  profit_gap:            {report['expected_profit_gap']}")

    print("\n  --- Cross-Validation ---")
    print(f"  Convergence:    {report['convergence']}")
    print(f"  Interpretation: {report['interpretation']}")
    print()

    # Irreversibility demo
    print("  --- Irreversibility clamp demo ---")
    link2 = MetabolicLink()
    link2.ingest_metabolic(
        time_to_red=None,
        profit_gap=math.inf,
        revenue=1000.0,
        sustainable_yield_signal="BLACK",
        basin_trajectory="DEGRADING",
        cumulative_environment_loss=12.5,
        irreversible_metrics=("soil.organic_carbon",),
    )
    link2.ingest_taf(fatigue_score=9.0, distance_to_collapse=0.3,
                     hidden_count=8)
    r2 = link2.cross_validate()
    print(f"  BLACK scenario:")
    print(f"    derived_collapse_distance: {r2['derived_collapse_distance']} "
          f"({r2.get('irreversibility_clamp', 'no clamp')})")
    print(f"    status:                    {r2['derived_status']}")
    print(f"    hidden_count:              {r2['derived_hidden_count']}")
    print()
