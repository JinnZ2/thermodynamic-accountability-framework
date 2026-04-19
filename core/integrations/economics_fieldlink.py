#!/usr/bin/env python3
"""
Mathematic-Economics Field Link -- Bidirectional bridge between TAF and
the 13 canonical equations from github.com/JinnZ2/Mathematic-economics.

TAF (this repo) measures institutional accountability in energy units.
Mathematic-Economics (ME) measures economic systems through quantifiable
metrics that explicitly avoid monetary proxies, with thermodynamic
grounding and falsifiable counter-tests for each equation.

Both frameworks share the same physics-first methodology. ME is the
empirical-economics surface; TAF is the substrate-physics surface.
Where they overlap, this fieldlink translates between the two.

Cross-reference map:
    ME equation                <-> TAF concept
    ER  (Extraction Rate)      <-> parasitic_energy_debt
    UFR (Upward Flow Rate)     <-> distance_to_collapse trajectory
    MSI / MM / BSC             <-> K_cred (Money Equation credibility)
    SID / ISR                  <-> hidden_count multiplier
    RI  (Risk Inequality)      <-> fatigue_score asymmetry
    SD  (Semantic Drift)       <-> anti_metaphor_locker drift_ratio
    HHI (concentration)        <-> governance.power_concentration
    DI  (Democracy Index)      <-> governance composite
    OSDI (composite)           <-> derivable from the above

Stable input shape (contract): see schemas/mathematic_economics_contract.py
which mirrors ME's 13 canonical equation IDs and their formulas as text.
This fieldlink accepts loose keyword arguments so it works on either
the contract dataclasses or plain dicts decoded from ME output.

Dependencies: stdlib only (math). Does NOT import Mathematic-Economics
at runtime -- ME has no requirements.txt and is research-stage; coupling
via output values keeps both repos independently runnable.

License: CC0 1.0 Universal.
"""

from __future__ import annotations

import math


# ============================================================
# ME -> TAF: Economic measurements as physical quantities
# ============================================================

def er_to_parasitic_debt(extraction_rate, daily_revenue_J=1e7):
    """Convert Extraction Rate to TAF parasitic energy debt per day.

    ER = (revenue - labor_costs) / revenue. The retained-after-labor
    fraction maps to the surplus extracted from the productive
    organism. In TAF terms that surplus, when not returned, accumulates
    as parasitic debt against the metabolic substrate.

    Parameters
    ----------
    extraction_rate : float
        ME's ER (0-1).
    daily_revenue_J : float
        Daily throughput in joule-equivalent units. Default 1e7 J ~
        one full metabolic day for a single worker.

    Returns
    -------
    float
        Parasitic energy debt per day (J).
    """
    er = max(0.0, min(1.0, extraction_rate))
    return round(er * daily_revenue_J, 3)


def ufr_to_collapse_trajectory(upward_flow_rate):
    """Convert Upward Flow Rate to a TAF distance-to-collapse trend.

    UFR = d(top_1pct)/dt / d(bottom_50pct)/dt. UFR > 1 means the top
    is accumulating faster than the broad base, which TAF reads as
    redistribution-toward-extraction and therefore an erosion of
    distance-to-collapse over time.

    Returns
    -------
    float
        Trajectory multiplier in [0, 2]. 1.0 = no trend. > 1 = collapse
        distance shrinking. < 1 = recovering.
    """
    if upward_flow_rate is None:
        return 1.0
    # Saturating: UFR=1 -> 1.0; UFR=3 -> ~1.6; UFR=10 -> ~1.95
    excess = max(0.0, float(upward_flow_rate) - 1.0)
    trend = 1.0 + (1.0 - math.exp(-0.5 * excess))
    return round(trend, 3)


def money_origin_to_k_cred(msi=None, mm=None, bsc=None):
    """Combine ME's money-origin metrics into TAF's K_cred term.

    From CLAUDE.md (TAF Money Equation):
        K_cred = Consequence_density * Verification_freq * Time_under_exposure

    ME measures three orthogonal money-origin properties:
        MSI = government_created_money / total_money_supply
        MM  = 1 / reserve_requirement (leverage in private credit creation)
        BSC = government_rescue_funds / private_losses

    K_cred is the Money Equation's discount on credibility. Money that
    is collectively created (high MSI), highly leveraged (high MM),
    and routinely bailed out (high BSC) all reduce the credibility
    of the unit -- because each property weakens the link between the
    monetary claim and the underlying physical value it claims to
    represent.

    Returns
    -------
    float
        K_cred in [0, 1]. 1.0 = full credibility. 0.0 = pure narrative.
    """
    components = []
    if msi is not None:
        # High MSI = high collective dependency = lower private-money
        # autonomy claim. Inverted: cred drops as MSI rises.
        components.append(1.0 - max(0.0, min(1.0, msi)))
    if mm is not None:
        # Money multiplier > 10 indicates extreme leverage. Saturating.
        leverage_penalty = 1.0 - math.exp(-max(0.0, mm) / 10.0)
        components.append(1.0 - leverage_penalty)
    if bsc is not None:
        # BSC > 1 means rescue funds exceed private losses (full
        # socialization of loss while privatizing gain). Saturating.
        bsc_penalty = 1.0 - math.exp(-max(0.0, bsc))
        components.append(1.0 - bsc_penalty)

    if not components:
        return 1.0
    # Multiplicative combination -- each property erodes credibility
    # independently.
    k_cred = 1.0
    for c in components:
        k_cred *= max(0.0, min(1.0, c))
    return round(k_cred, 4)


def hidden_subsidies_to_hidden_count(sid=None, isr=None):
    """Convert SID and ISR to TAF's hidden_count.

    SID = C / (C + P): collective infrastructure share. High SID means
    the private system is structurally dependent on collective inputs
    that don't appear on its own books.

    ISR = market_value_of_public_infrastructure_used / cost_paid:
    direct measurement of hidden subsidy magnitude.

    Each unit of unaccounted dependency is functionally equivalent to
    one TAF hidden variable -- something the system pretends doesn't
    exist but that affects outcomes. The combined estimate is mapped
    to TAF's hidden_count integer (0-10) and the hidden_mult formula
    1 + 0.1 * n^1.5 captures the nonlinear amplification.

    Returns
    -------
    int
        Estimated hidden variable count for TAF (0-10).
    """
    contributions = []
    if sid is not None:
        # SID > 0.5 means majority-collective infrastructure -- map to
        # 0..6 hidden variables.
        contributions.append(min(6.0, max(0.0, float(sid)) * 6.0))
    if isr is not None:
        # ISR ~ 1 means the entity pays full freight (no hidden subsidy).
        # ISR > 1 means subsidy is positive; ISR very large = pure
        # extraction of public value. Saturating mapping to 0..6.
        excess = max(0.0, float(isr) - 1.0)
        contributions.append(6.0 * (1.0 - math.exp(-0.4 * excess)))

    if not contributions:
        return 0
    avg = sum(contributions) / len(contributions)
    return int(round(min(10.0, avg)))


def risk_inequality_to_fatigue_asymmetry(ri):
    """Convert Risk Inequality to TAF fatigue asymmetry.

    RI = (Risk_workers / N_workers) / (Risk_investors / N_investors).
    Per-capita risk burden ratio. RI = 1 means symmetric; RI > 1 means
    workers carry more per-capita risk than investors. TAF's fatigue
    score does not directly encode asymmetry, but the asymmetry term
    multiplies the fatigue contribution attributable to systemic risk.

    Returns
    -------
    float
        Fatigue-asymmetry multiplier in [1.0, 3.0]. 1.0 = symmetric.
    """
    if ri is None:
        return 1.0
    r = max(0.0, float(ri))
    if r <= 1.0:
        return 1.0
    # Saturating: RI=2 -> ~1.4; RI=5 -> ~2.3; RI=20 -> ~2.95
    mult = 1.0 + 2.0 * (1.0 - math.exp(-0.2 * (r - 1.0)))
    return round(mult, 3)


def semantic_drift_to_anti_metaphor_score(sd_per_year):
    """Convert Semantic Drift Rate to anti_metaphor_locker drift_ratio.

    ME's SD measures how fast a term's empirical referent diverges
    from its earlier referent (diachronic word-embedding distance per
    unit time). TAF's anti_metaphor_locker tracks per-term drift_ratio
    on the same axis.

    A common conversion: if a single term drifts at SD = 0.05/year
    sustained for 5 years, its accumulated divergence approaches
    drift_ratio ~ 0.25 in the locker's normalized space.

    Returns
    -------
    float
        Drift ratio in [0, 1]. Higher = more drift.
    """
    if sd_per_year is None:
        return 0.0
    sd = max(0.0, float(sd_per_year))
    # Saturating over a 5-year window: 0.05/yr -> ~0.22; 0.2/yr -> ~0.63
    drift = 1.0 - math.exp(-5.0 * sd)
    return round(min(1.0, drift), 3)


def hhi_to_power_concentration(hhi):
    """Convert Herfindahl-Hirschman Index to TAF power_concentration.

    HHI ranges 0-10000 (squared percent of market shares). The DOJ
    treats HHI > 2500 as "highly concentrated" and HHI < 1500 as
    "unconcentrated." TAF's power_concentration is a 0-1 INVERTED
    variable (high = bad).

    Returns
    -------
    float
        power_concentration in [0, 1].
    """
    if hhi is None:
        return 0.0
    h = max(0.0, min(10000.0, float(hhi)))
    # Linear in the concentration band, saturating above 5000:
    if h <= 1500:
        return round(0.2 * (h / 1500.0), 3)
    if h <= 2500:
        return round(0.2 + 0.4 * ((h - 1500) / 1000.0), 3)
    return round(0.6 + 0.4 * (1.0 - math.exp(-(h - 2500) / 2000.0)), 3)


def democracy_index_to_governance_health(di_variance, baseline_variance=1.0):
    """Convert Democracy Index variance to a TAF governance health score.

    DI = Var(P_1, ..., P_n) where P_i = W_i * I_i (wealth * leverage).
    Higher variance = more concentrated effective political power =
    less democratic. TAF's governance term is a 0-1 health score
    (higher = better) computed as:
        gov = (rotation * dissent * (1-power_conc) * succession)^0.25

    This converter contributes to the (1 - power_conc) factor by
    converting DI variance into a power-concentration estimate.

    Parameters
    ----------
    di_variance : float
        ME's DI value (variance, units depend on P_i normalization).
    baseline_variance : float
        Variance of an idealized democratic distribution. Default 1.0
        (caller should pass the actual baseline if known).

    Returns
    -------
    float
        governance_health in [0, 1]. 1.0 = perfectly democratic.
    """
    if di_variance is None:
        return 1.0
    ratio = max(0.0, float(di_variance)) / max(1e-9, baseline_variance)
    # Saturating: ratio=1 -> 0.5; ratio=10 -> ~0.05
    health = math.exp(-0.7 * (ratio - 1.0)) if ratio >= 1.0 else 1.0
    return round(max(0.0, min(1.0, health)), 3)


# ============================================================
# TAF -> ME: Energy state as expected economic measurements
# ============================================================

def fatigue_to_expected_er(fatigue_score):
    """Predict expected Extraction Rate from TAF fatigue.

    Higher organism fatigue indicates a longer-running extraction
    regime. Predicts ER will be elevated above any healthy baseline.
    Saturating mapping.
    """
    if fatigue_score is None:
        return None
    f = max(0.0, min(10.0, float(fatigue_score))) / 10.0
    return round(0.3 + 0.5 * f, 3)


def collapse_distance_to_expected_ufr(collapse_distance):
    """Predict UFR from TAF distance-to-collapse.

    Closer to collapse implies the upward redistribution machinery
    is running harder. UFR rises nonlinearly as distance shrinks.
    """
    if collapse_distance is None:
        return None
    d = max(0.0, min(1.0, float(collapse_distance)))
    if d >= 0.9:
        return 1.0
    return round(1.0 + 4.0 * (1.0 - d) ** 2, 3)


def hidden_count_to_expected_isr(hidden_count):
    """Predict ISR from TAF hidden_count.

    Each hidden variable in TAF corresponds to an unaccounted
    dependency in ME's framing. Higher hidden_count predicts higher
    ISR (more public infrastructure value consumed without paying for
    it).
    """
    if hidden_count is None:
        return None
    n = max(0, int(hidden_count))
    return round(1.0 + 0.5 * n, 3)


def k_cred_to_expected_msi(k_cred):
    """Predict MSI from TAF K_cred.

    Low credibility is the symptom of high collective dependency that
    the private narrative refuses to acknowledge. As K_cred drops,
    expected MSI rises (more of the money base is collectively
    created even if rhetorically denied).
    """
    if k_cred is None:
        return None
    k = max(0.0, min(1.0, float(k_cred)))
    return round(1.0 - k, 3)


# ============================================================
# COUPLED CROSS-VALIDATION
# ============================================================

class EconomicsLink:
    """Bidirectional TAF <-> Mathematic-Economics coupling.

    Cross-validates: when TAF energy physics and ME equation values
    agree, confidence is high. When they diverge, one framework is
    missing something the other catches.

    Usage:
        link = EconomicsLink()
        link.ingest_economics(er=0.62, ufr=1.45, msi=0.18, hhi=3500, sd=0.022)
        link.ingest_taf(fatigue_score=6.5, collapse_distance=0.45,
                        hidden_count=4, k_cred=0.30)
        report = link.cross_validate()
    """

    def __init__(self):
        # ME side
        self.er = None
        self.ufr = None
        self.msi = None
        self.mm = None
        self.bsc = None
        self.sid = None
        self.isr = None
        self.ri = None
        self.sd = None
        self.hhi = None
        self.di = None

        # TAF side
        self.fatigue_score = None
        self.collapse_distance = None
        self.hidden_count = None
        self.k_cred = None

    def ingest_economics(self, er=None, ufr=None, msi=None, mm=None,
                          bsc=None, sid=None, isr=None, ri=None,
                          sd=None, hhi=None, di=None):
        """Load Mathematic-Economics measurements (any subset)."""
        self.er, self.ufr = er, ufr
        self.msi, self.mm, self.bsc = msi, mm, bsc
        self.sid, self.isr = sid, isr
        self.ri = ri
        self.sd = sd
        self.hhi = hhi
        self.di = di

    def ingest_taf(self, fatigue_score=None, collapse_distance=None,
                    hidden_count=None, k_cred=None):
        """Load TAF state (any subset)."""
        self.fatigue_score = fatigue_score
        self.collapse_distance = collapse_distance
        self.hidden_count = hidden_count
        self.k_cred = k_cred

    def cross_validate(self) -> dict:
        """Run cross-validation between TAF physics and ME measurements."""
        report = {}

        # ME -> TAF derived
        report["derived_parasitic_debt"] = (
            er_to_parasitic_debt(self.er) if self.er is not None else None
        )
        report["derived_collapse_trajectory"] = ufr_to_collapse_trajectory(self.ufr)
        report["derived_k_cred"] = money_origin_to_k_cred(
            msi=self.msi, mm=self.mm, bsc=self.bsc
        )
        report["derived_hidden_count"] = hidden_subsidies_to_hidden_count(
            sid=self.sid, isr=self.isr
        )
        report["derived_fatigue_asymmetry"] = risk_inequality_to_fatigue_asymmetry(self.ri)
        report["derived_drift_ratio"] = semantic_drift_to_anti_metaphor_score(self.sd)
        report["derived_power_concentration"] = hhi_to_power_concentration(self.hhi)
        report["derived_governance_health"] = democracy_index_to_governance_health(self.di)

        # TAF -> ME expected
        report["expected_er"] = fatigue_to_expected_er(self.fatigue_score)
        report["expected_ufr"] = collapse_distance_to_expected_ufr(self.collapse_distance)
        report["expected_isr"] = hidden_count_to_expected_isr(self.hidden_count)
        report["expected_msi"] = k_cred_to_expected_msi(self.k_cred)

        # Convergence on the strongest pairing: ER <-> fatigue
        delta = None
        if self.er is not None and report["expected_er"] is not None:
            delta = abs(self.er - report["expected_er"])
            if delta < 0.10:
                report["convergence"] = "STRONG"
                report["interpretation"] = (
                    "Energy physics and economic measurement agree on "
                    "extraction. High confidence in joint diagnosis."
                )
            elif delta < 0.25:
                report["convergence"] = "MODERATE"
                report["interpretation"] = (
                    "Partial agreement. Either fatigue is lagging the "
                    "extraction signal, or the ER measurement window is "
                    "shorter than the fatigue accumulation timescale."
                )
            else:
                report["convergence"] = "DIVERGENT"
                if self.er > report["expected_er"]:
                    report["interpretation"] = (
                        "Extraction rate is higher than fatigue predicts. "
                        "Either the burden is masked (sycophantic compliance) "
                        "or the productive base is being externalized to "
                        "other organisms not measured here."
                    )
                else:
                    report["interpretation"] = (
                        "Fatigue is higher than extraction rate predicts. "
                        "Look for non-extraction stressors: friction, "
                        "hidden variables, environmental load."
                    )
            report["er_delta"] = round(delta, 3)
        else:
            report["convergence"] = "INSUFFICIENT_DATA"
            report["interpretation"] = (
                "Need both ER (from ME) and fatigue_score (from TAF) "
                "for the primary convergence check."
            )

        return report


# ============================================================
# VARIABLE MAP: TAF <-> Mathematic-Economics shared namespace
# ============================================================

FIELD_MAP = {
    # TAF concept                  -> ME equation                   Direction
    "parasitic_energy_debt":       ("ER (Extraction Rate)",          "ME->TAF"),
    "distance_to_collapse_trend":  ("UFR (Upward Flow Rate)",        "ME->TAF"),
    "K_cred":                      ("MSI + MM + BSC composite",      "ME->TAF"),
    "hidden_count":                ("SID + ISR composite",           "ME->TAF"),
    "fatigue_asymmetry":           ("RI (Risk Inequality)",          "ME->TAF"),
    "drift_ratio":                 ("SD (Semantic Drift Rate)",      "ME->TAF"),
    "power_concentration":         ("HHI (Herfindahl-Hirschman)",    "ME->TAF"),
    "governance_health":           ("DI (Democracy Index)",          "ME->TAF"),
    "expected_ER":                 ("fatigue_score",                 "TAF->ME"),
    "expected_UFR":                ("distance_to_collapse",          "TAF->ME"),
    "expected_ISR":                ("hidden_count",                  "TAF->ME"),
    "expected_MSI":                ("K_cred",                        "TAF->ME"),
}


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  ECONOMICS <-> TAF FIELD LINK -- Cross-Validation Demo")
    print("=" * 60)

    link = EconomicsLink()

    # ME measurements (illustrative -- numbers in the right ballpark)
    link.ingest_economics(
        er=0.62,        # 62% extraction rate
        ufr=1.45,       # top 1% accumulating 45% faster than bottom 50%
        msi=0.18,       # 18% of money supply is government-created
        mm=10.0,        # money multiplier (10x leverage)
        bsc=0.85,       # bailout-to-loss ratio
        sid=0.55,       # 55% collective infrastructure share
        isr=2.3,        # entities use $2.30 of public infra per $1 paid
        ri=4.5,         # workers carry 4.5x per-capita risk vs investors
        sd=0.022,       # 2.2%/year semantic drift on key terms
        hhi=3500,       # highly concentrated markets
        di=8.0,         # high political power variance
    )

    # TAF state at the same time
    link.ingest_taf(
        fatigue_score=6.5,
        collapse_distance=0.45,
        hidden_count=4,
        k_cred=0.30,
    )

    report = link.cross_validate()

    print("\n  --- ME -> TAF Derived Values ---")
    print(f"  Parasitic debt (J/day):  {report['derived_parasitic_debt']}")
    print(f"  Collapse trajectory:     {report['derived_collapse_trajectory']}x")
    print(f"  K_cred:                  {report['derived_k_cred']}")
    print(f"  Hidden count:            {report['derived_hidden_count']}")
    print(f"  Fatigue asymmetry:       {report['derived_fatigue_asymmetry']}x")
    print(f"  Drift ratio:             {report['derived_drift_ratio']}")
    print(f"  Power concentration:     {report['derived_power_concentration']}")
    print(f"  Governance health:       {report['derived_governance_health']}")

    print("\n  --- TAF -> ME Expected Values ---")
    print(f"  Expected ER:             {report['expected_er']}")
    print(f"  Expected UFR:            {report['expected_ufr']}")
    print(f"  Expected ISR:            {report['expected_isr']}")
    print(f"  Expected MSI:            {report['expected_msi']}")

    print("\n  --- Cross-Validation ---")
    print(f"  Convergence:    {report['convergence']}")
    if "er_delta" in report:
        print(f"  ER delta:       {report['er_delta']}")
    print(f"  Interpretation: {report['interpretation']}")
    print()

