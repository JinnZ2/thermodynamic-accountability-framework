"""
business_resilience_framework.py

Self-audit framework for individual businesses to measure their own
resilience, extraction ratio, and substrate health honestly -- and to
find a falsifiable transition pathway forward.

Sits between the municipal scoring layer and labor thermodynamics.
A business can run this on itself, see the actual math, and get a
phased transition path that satisfies all stakeholders without
requiring all-at-once disruption.

Five coupled diagnostics:
    1. Substrate health audit (the labor + knowledge + community base)
    2. Extraction ratio measurement (where value flows)
    3. Cascade vulnerability scan (single points of failure)
    4. Discretionary effort indicator (the leading signal of decay)
    5. Transition pathway generator (phased, falsifiable, costed)

Couples to political_audit/municipal_resilience_framework.py via
business_state_to_business_profile(): the inside-view self-audit can
be projected to the outside-view municipal scoring vocabulary, so a
business can see how its self-assessed substrate health translates to
the actuarial premium / reputation score / tax-zoning treatment a
municipality would assign.

CC0 -- JinnZ2
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


# -----------------------------------------------------------
# BUSINESS STATE
# -----------------------------------------------------------

@dataclass
class BusinessState:
    name: str

    # --- workforce substrate ---
    headcount: int
    avg_tenure_years: float
    pension_or_equivalent: bool
    health_coverage_quality: float        # 0..1
    apprenticeship_pipeline: bool
    voluntary_turnover_pct: float         # leading indicator
    safety_reports_per_employee: float    # higher = healthier reporting culture
    discretionary_effort_index: float     # 0..1

    # --- knowledge substrate ---
    documented_processes_pct: float        # 0..1
    cross_trained_pct: float               # 0..1
    knowledge_holders_within_5yr_retire: float  # 0..1 (risk fraction)
    succession_plan_coverage: float        # 0..1

    # --- community substrate ---
    local_supplier_pct: float              # 0..1
    local_payroll_pct: float               # 0..1
    profit_recirculated_local_pct: float   # 0..1
    community_contracts_honored_pct: float # 0..1

    # --- extraction signals ---
    profit_extracted_to_holding_pct: float # 0..1
    debt_loaded_for_extraction: bool
    quarterly_pressure_index: float        # 0..1 (1 = pure quarterly extraction)
    executive_to_median_pay_ratio: float

    # --- physical / operational ---
    single_supplier_dependencies: int      # count of SPOFs
    deferred_maintenance_pct: float        # 0..1
    energy_dependency: float               # 0..1
    regulatory_compliance_only: bool       # vs. exceeds compliance

    # --- financial reality ---
    cash_runway_months: float
    revenue_concentration_top_3_clients: float  # 0..1
    capex_reinvestment_pct: float          # 0..1 of profit


# -----------------------------------------------------------
# DIAGNOSTIC 1: SUBSTRATE HEALTH
# -----------------------------------------------------------

def substrate_health_audit(b: BusinessState) -> dict:
    workforce = (
        min(b.avg_tenure_years / 7.0, 1.0) * 0.20 +
        (0.15 if b.pension_or_equivalent else 0.0) +
        b.health_coverage_quality * 0.10 +
        (0.10 if b.apprenticeship_pipeline else 0.0) +
        max(0.0, 1.0 - b.voluntary_turnover_pct / 30.0) * 0.15 +
        min(b.safety_reports_per_employee / 2.0, 1.0) * 0.10 +
        b.discretionary_effort_index * 0.20
    )

    knowledge = (
        b.documented_processes_pct * 0.25 +
        b.cross_trained_pct * 0.25 +
        (1.0 - b.knowledge_holders_within_5yr_retire) * 0.25 +
        b.succession_plan_coverage * 0.25
    )

    community = (
        b.local_supplier_pct * 0.25 +
        b.local_payroll_pct * 0.25 +
        b.profit_recirculated_local_pct * 0.25 +
        b.community_contracts_honored_pct * 0.25
    )

    composite = workforce * 0.45 + knowledge * 0.30 + community * 0.25

    return {
        "workforce": round(workforce, 3),
        "knowledge": round(knowledge, 3),
        "community": round(community, 3),
        "composite": round(composite, 3),
        "rating": (
            "healthy"   if composite > 0.65 else
            "at_risk"   if composite > 0.40 else
            "degrading" if composite > 0.20 else
            "collapsing"
        ),
    }


# -----------------------------------------------------------
# DIAGNOSTIC 2: EXTRACTION RATIO
# -----------------------------------------------------------

def extraction_ratio_measurement(b: BusinessState) -> dict:
    extraction = (
        b.profit_extracted_to_holding_pct * 0.35 +
        (0.20 if b.debt_loaded_for_extraction else 0.0) +
        b.quarterly_pressure_index * 0.25 +
        min(b.executive_to_median_pay_ratio / 100.0, 1.0) * 0.20
    )

    contribution = (
        b.capex_reinvestment_pct * 0.40 +
        b.local_payroll_pct * 0.20 +
        b.profit_recirculated_local_pct * 0.20 +
        b.community_contracts_honored_pct * 0.20
    )

    net = round(contribution - extraction, 3)
    return {
        "extraction_index": round(extraction, 3),
        "contribution_index": round(contribution, 3),
        "net_flow": net,
        "direction": (
            "value_returning_to_substrate" if net > 0.15 else
            "balanced"                     if net > -0.15 else
            "value_leaving_substrate"
        ),
    }


# -----------------------------------------------------------
# DIAGNOSTIC 3: CASCADE VULNERABILITY
# -----------------------------------------------------------

def cascade_vulnerability_scan(b: BusinessState) -> dict:
    spofs = []
    if b.single_supplier_dependencies > 0:
        spofs.append({
            "type": "supplier",
            "count": b.single_supplier_dependencies,
            "weight": min(b.single_supplier_dependencies * 0.10, 0.40),
        })
    if b.knowledge_holders_within_5yr_retire > 0.30:
        spofs.append({
            "type": "knowledge_loss",
            "fraction": b.knowledge_holders_within_5yr_retire,
            "weight": b.knowledge_holders_within_5yr_retire * 0.50,
        })
    if b.deferred_maintenance_pct > 0.20:
        spofs.append({
            "type": "deferred_maintenance",
            "fraction": b.deferred_maintenance_pct,
            "weight": b.deferred_maintenance_pct * 0.40,
        })
    if b.revenue_concentration_top_3_clients > 0.50:
        spofs.append({
            "type": "revenue_concentration",
            "fraction": b.revenue_concentration_top_3_clients,
            "weight": b.revenue_concentration_top_3_clients * 0.45,
        })
    if b.energy_dependency > 0.70:
        spofs.append({
            "type": "energy_dependency",
            "fraction": b.energy_dependency,
            "weight": b.energy_dependency * 0.30,
        })
    if b.cash_runway_months < 3:
        spofs.append({
            "type": "cash_fragility",
            "months": b.cash_runway_months,
            "weight": 0.40,
        })

    total_weight = sum(s["weight"] for s in spofs)
    return {
        "single_points_of_failure": spofs,
        "vulnerability_index": round(min(total_weight, 1.0), 3),
        "rating": (
            "robust"   if total_weight < 0.30 else
            "fragile"  if total_weight < 0.60 else
            "critical" if total_weight < 0.90 else
            "imminent_failure_risk"
        ),
    }


# -----------------------------------------------------------
# DIAGNOSTIC 4: DISCRETIONARY EFFORT (LEADING INDICATOR)
# -----------------------------------------------------------

def discretionary_effort_signal(b: BusinessState) -> dict:
    """
    Discretionary effort is the EARLIEST signal of substrate decay.
    Workers withdraw effort before they withdraw labor.
    Falling discretionary effort = 6-18 months ahead of turnover spike.
    """
    signals = {
        "current_effort": b.discretionary_effort_index,
        "safety_reporting_health": min(b.safety_reports_per_employee / 2.0, 1.0),
        "voluntary_turnover_pressure": b.voluntary_turnover_pct / 30.0,
    }

    leading = (
        b.discretionary_effort_index * 0.5 +
        signals["safety_reporting_health"] * 0.3 +
        max(0.0, 1.0 - signals["voluntary_turnover_pressure"]) * 0.2
    )

    return {
        "signals": {k: round(v, 3) for k, v in signals.items()},
        "leading_indicator": round(leading, 3),
        "forecast": (
            "stable_or_improving" if leading > 0.65 else
            "early_decay_warning" if leading > 0.45 else
            "decay_in_progress"   if leading > 0.25 else
            "advanced_decay_imminent_failure"
        ),
    }


# -----------------------------------------------------------
# DIAGNOSTIC 5: TRANSITION PATHWAY
# -----------------------------------------------------------

def transition_pathway(b: BusinessState) -> dict:
    """
    Builds a phased, falsifiable transition path from current state
    toward substrate-contributor status. Each phase has measurable
    targets and estimated payback windows.
    """
    sub = substrate_health_audit(b)
    ext = extraction_ratio_measurement(b)
    cas = cascade_vulnerability_scan(b)
    eff = discretionary_effort_signal(b)

    phases = []

    # Phase 1: Stop the bleeding (0-6 months)
    p1 = {"phase": 1, "window_months": 6, "actions": [], "cost_signal": "low"}
    if eff["leading_indicator"] < 0.50:
        p1["actions"].append(
            "Immediate worker safety/voice channel -- Lean Six Sigma "
            "style empowerment without retaliation. Restores discretionary effort."
        )
    if cas["vulnerability_index"] > 0.60:
        p1["actions"].append(
            "Identify top 3 SPOFs; allocate emergency redundancy budget."
        )
    if b.deferred_maintenance_pct > 0.30:
        p1["actions"].append(
            "Catch up on critical deferred maintenance before cascade triggers."
        )
    if not p1["actions"]:
        p1["actions"].append(
            "Maintain current floor; document baseline for transition tracking."
        )
    phases.append(p1)

    # Phase 2: Substrate rebuild (6-24 months)
    p2 = {"phase": 2, "window_months": 24, "actions": [], "cost_signal": "medium"}
    if not b.pension_or_equivalent:
        p2["actions"].append(
            "Worker-controlled retirement vehicle, vested. "
            "Long-tenure incentive structure."
        )
    if sub["knowledge"] < 0.50:
        p2["actions"].append(
            "Cross-training program + process documentation. "
            "Apprenticeship pipeline if absent."
        )
    if b.local_supplier_pct < 0.30:
        p2["actions"].append(
            "Local supplier development program -- "
            "phased substitution where viable."
        )
    if b.capex_reinvestment_pct < 0.30:
        p2["actions"].append(
            "Increase reinvestment ratio; reduce dividend extraction."
        )
    phases.append(p2)

    # Phase 3: Structural realignment (24-60 months)
    p3 = {"phase": 3, "window_months": 60, "actions": [],
          "cost_signal": "high_but_payback_positive"}
    if ext["extraction_index"] > 0.40:
        p3["actions"].append(
            "Restructure ownership/financing to remove debt-loaded "
            "extraction. Consider employee ownership or stewardship trust."
        )
    if b.executive_to_median_pay_ratio > 50:
        p3["actions"].append(
            "Compensation realignment -- ratio target under 25:1, "
            "ties leadership to substrate health."
        )
    if b.quarterly_pressure_index > 0.5:
        p3["actions"].append(
            "Renegotiate investor expectations or transition off "
            "quarterly-extraction capital. Long-cycle financing alignment."
        )
    phases.append(p3)

    estimated_resilience_gain = round(
        (1.0 - sub["composite"]) * 0.6 +
        max(0.0, -ext["net_flow"]) * 0.5 +
        cas["vulnerability_index"] * 0.4,
        3,
    )

    return {
        "current_state_summary": {
            "substrate": sub["rating"],
            "extraction": ext["direction"],
            "cascade_risk": cas["rating"],
            "effort_forecast": eff["forecast"],
        },
        "phases": phases,
        "estimated_resilience_gain": estimated_resilience_gain,
        "falsifiable_targets": {
            "phase_1": "discretionary_effort_index > 0.55, top_spofs_redundant",
            "phase_2": "substrate_composite > 0.55, local_supplier_pct > 0.30",
            "phase_3": "extraction_index < 0.30, exec_pay_ratio < 25",
        },
    }


# -----------------------------------------------------------
# UNIFIED REPORT
# -----------------------------------------------------------

def full_audit(b: BusinessState) -> dict:
    return {
        "name": b.name,
        "substrate_health": substrate_health_audit(b),
        "extraction_ratio": extraction_ratio_measurement(b),
        "cascade_vulnerability": cascade_vulnerability_scan(b),
        "discretionary_effort": discretionary_effort_signal(b),
        "transition_pathway": transition_pathway(b),
    }


# -----------------------------------------------------------
# COUPLING TO MUNICIPAL RESILIENCE FRAMEWORK
# -----------------------------------------------------------

def business_state_to_business_profile(b: BusinessState):
    """
    Project an inside-view BusinessState into the outside-view
    BusinessProfile used by political_audit.municipal_resilience_
    framework. Lets a self-audit check how its substrate health
    translates to the actuarial premium / municipal reputation /
    tax-zoning treatment a municipality would assign.

    Field mapping (inside -> outside):
        avg_tenure_years              -> avg_tenure_years (direct)
        pension_or_equivalent         -> pension_or_equivalent (direct)
        discretionary_effort_index    -> discretionary_effort_index (direct)
        voluntary_turnover_pct        -> turnover_rate_pct (direct)
        safety_reports_per_employee   -> accident_rate_per_1000
                                          (inverse proxy: low reporting
                                           often correlates with hidden-
                                           accident regimes; this maps
                                           the reporting-health signal
                                           into the accident-rate axis)
        local_supplier_pct            -> local_supplier_pct (direct)
        profit_recirculated_local_pct -> profit_recirculated_local_pct
        knowledge_holders_within_5yr  -> sole_employer_dependency proxy
                                          (high knowledge concentration
                                           = high single-employer
                                           dependency on those holders)
        documented_processes_pct      -> substrate_knowledge_retained
        profit_extracted_to_holding   -> profit_extracted_to_holding_pct
        debt_loaded_for_extraction    -> debt_loaded_for_extraction
        quarterly_pressure_index +    -> subsidiary_liability_shuffling
          revenue_concentration         (proxy for short-term financial
                                         engineering pressure)
        deferred_maintenance_pct      -> externalized_costs (proxy:
                                          deferred maintenance pushes
                                          cost onto whoever inherits
                                          the asset / community)
    """
    # Lazy import keeps this module standalone.
    try:
        from political_audit.municipal_resilience_framework import (
            BusinessProfile,
        )
    except ImportError:
        from municipal_resilience_framework import BusinessProfile  # type: ignore

    # safety_reports_per_employee (good signal, 0..high) -> accident_rate
    # Healthy reporting culture (high) corresponds to LOWER hidden-
    # accident risk. Floor at 0.5 / ceiling at ~6.0 to stay in the
    # actuarial-input range expected by the outside view.
    if b.safety_reports_per_employee >= 1.5:
        accident_rate = 2.0
    elif b.safety_reports_per_employee >= 0.5:
        accident_rate = 4.0
    else:
        accident_rate = 6.0

    # Externalized cost proxy: deferred maintenance + inverse community
    # contracts honored fraction. Capped at 1.0.
    externalized = min(
        1.0,
        b.deferred_maintenance_pct +
        max(0.0, 1.0 - b.community_contracts_honored_pct) * 0.3,
    )

    # Subsidiary-shuffling signal: hard to detect from inside-view,
    # so use quarterly pressure + extraction as a proxy heuristic.
    shuffling_proxy = (
        b.quarterly_pressure_index > 0.7
        and b.profit_extracted_to_holding_pct > 0.7
    )

    return BusinessProfile(
        name=b.name,
        avg_tenure_years=b.avg_tenure_years,
        pension_or_equivalent=b.pension_or_equivalent,
        discretionary_effort_index=b.discretionary_effort_index,
        accident_rate_per_1000=accident_rate,
        turnover_rate_pct=b.voluntary_turnover_pct,
        local_supplier_pct=b.local_supplier_pct,
        profit_recirculated_local_pct=b.profit_recirculated_local_pct,
        community_lifespan_years=max(1, int(b.avg_tenure_years * 4)),
        externalized_costs=round(externalized, 3),
        profit_extracted_to_holding_pct=b.profit_extracted_to_holding_pct,
        debt_loaded_for_extraction=b.debt_loaded_for_extraction,
        subsidiary_liability_shuffling=shuffling_proxy,
        sole_employer_dependency=b.knowledge_holders_within_5yr_retire,
        substrate_knowledge_retained=b.documented_processes_pct,
    )


# -----------------------------------------------------------
# REFERENCE PROFILES
# -----------------------------------------------------------

def reference_profiles() -> List[BusinessState]:
    return [
        BusinessState(
            name="Mid-size manufacturer (legacy committed model)",
            headcount=420, avg_tenure_years=11.0, pension_or_equivalent=True,
            health_coverage_quality=0.80, apprenticeship_pipeline=True,
            voluntary_turnover_pct=8.0, safety_reports_per_employee=1.8,
            discretionary_effort_index=0.78,
            documented_processes_pct=0.65, cross_trained_pct=0.55,
            knowledge_holders_within_5yr_retire=0.25,
            succession_plan_coverage=0.50,
            local_supplier_pct=0.45, local_payroll_pct=0.85,
            profit_recirculated_local_pct=0.55,
            community_contracts_honored_pct=0.90,
            profit_extracted_to_holding_pct=0.20,
            debt_loaded_for_extraction=False,
            quarterly_pressure_index=0.30,
            executive_to_median_pay_ratio=18,
            single_supplier_dependencies=2,
            deferred_maintenance_pct=0.10,
            energy_dependency=0.60,
            regulatory_compliance_only=False,
            cash_runway_months=8,
            revenue_concentration_top_3_clients=0.30,
            capex_reinvestment_pct=0.40,
        ),
        BusinessState(
            name="PE-acquired roll-up under quarterly extraction",
            headcount=1100, avg_tenure_years=1.4, pension_or_equivalent=False,
            health_coverage_quality=0.30, apprenticeship_pipeline=False,
            voluntary_turnover_pct=72.0, safety_reports_per_employee=0.2,
            discretionary_effort_index=0.20,
            documented_processes_pct=0.30, cross_trained_pct=0.15,
            knowledge_holders_within_5yr_retire=0.55,
            succession_plan_coverage=0.10,
            local_supplier_pct=0.05, local_payroll_pct=0.40,
            profit_recirculated_local_pct=0.05,
            community_contracts_honored_pct=0.40,
            profit_extracted_to_holding_pct=0.92,
            debt_loaded_for_extraction=True,
            quarterly_pressure_index=0.95,
            executive_to_median_pay_ratio=180,
            single_supplier_dependencies=6,
            deferred_maintenance_pct=0.55,
            energy_dependency=0.85,
            regulatory_compliance_only=True,
            cash_runway_months=2,
            revenue_concentration_top_3_clients=0.65,
            capex_reinvestment_pct=0.05,
        ),
    ]


# -----------------------------------------------------------
# DEMO
# -----------------------------------------------------------

if __name__ == "__main__":
    for b in reference_profiles():
        r = full_audit(b)
        print(f"\n{'=' * 72}")
        print(f"  {r['name']}")
        print(f"{'=' * 72}")

        s = r["substrate_health"]
        print(f"  SUBSTRATE HEALTH:    composite={s['composite']:.3f}  "
              f"rating={s['rating']}")

        e = r["extraction_ratio"]
        print(f"  EXTRACTION RATIO:    net_flow={e['net_flow']:+.3f}  "
              f"direction={e['direction']}")

        c = r["cascade_vulnerability"]
        print(f"  CASCADE RISK:        index={c['vulnerability_index']:.3f}  "
              f"rating={c['rating']}")

        d = r["discretionary_effort"]
        print(f"  DISCRETIONARY EFFORT: lead={d['leading_indicator']:.3f}  "
              f"forecast={d['forecast']}")

        t = r["transition_pathway"]
        print(f"  TRANSITION PATHWAY (estimated resilience gain: "
              f"{t['estimated_resilience_gain']}):")
        for p in t["phases"]:
            print(f"    Phase {p['phase']} ({p['window_months']} months, "
                  f"cost={p['cost_signal']}):")
            for a in p["actions"]:
                print(f"       - {a}")
        print("  FALSIFIABLE TARGETS:")
        for k, v in t["falsifiable_targets"].items():
            print(f"    {k}: {v}")

    # ---- COUPLING DEMO: project to municipal_resilience_framework ----
    try:
        import sys
        import pathlib
        repo_root = pathlib.Path(__file__).resolve().parent.parent
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from political_audit.municipal_resilience_framework import (
            evaluate_business,
        )

        print(f"\n{'=' * 72}")
        print("  PROJECTION: BusinessState (inside-view self-audit)")
        print("              -> BusinessProfile -> municipal scoring")
        print(f"{'=' * 72}")
        for b in reference_profiles():
            profile = business_state_to_business_profile(b)
            outside = evaluate_business(profile)
            r = outside["reputation"]
            t = outside["tax_zoning"]
            a = outside["actuarial"]
            print(f"\n  {b.name}")
            print(f"    municipal classification: {r['classification']:25s}  "
                  f"reputation={r['score']:+.3f}")
            print(f"    actuarial premium_index:  {a['premium_index']:.3f}")
            print(f"    tax/zoning:               {t['zoning_status']:12s} "
                  f"effective_rate={t['effective_tax_rate']}")
    except ImportError as e:
        print(f"\n  (municipal coupling skipped: {e})")
