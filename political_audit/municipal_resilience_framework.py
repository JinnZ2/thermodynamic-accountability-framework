"""
municipal_resilience_framework.py

Restructures municipal/township incentive systems so they
reward businesses that build community substrate and filter
out extraction-model businesses that degrade it.

Three coupled layers:

    1. Actuarial pricing layer (insurance reframed for systemic resilience)
    2. Municipal scoring layer (business reputation tied to substrate health)
    3. Tax/zoning incentive layer (cost to operate scales with extraction ratio)

The three together flip the incentive: extraction becomes
expensive, contribution becomes cheap.

CC0 -- JinnZ2
"""

from dataclasses import dataclass, field
from typing import Dict, List


# -----------------------------------------------------------
# BUSINESS PROFILE
# -----------------------------------------------------------

@dataclass
class BusinessProfile:
    name: str

    # workforce signals
    avg_tenure_years: float            # higher = more committed substrate
    pension_or_equivalent: bool        # binary: real long-term commitment
    discretionary_effort_index: float  # 0..1 from worker surveys / safety reports
    accident_rate_per_1000: float      # actuarial input
    turnover_rate_pct: float           # actuarial input

    # community signals
    local_supplier_pct: float          # 0..1 fraction of inputs from local economy
    profit_recirculated_local_pct: float  # 0..1 fraction kept in local loop
    community_lifespan_years: int      # years operating in this community
    externalized_costs: float          # 0..1 fraction of costs pushed onto community

    # extraction signals
    profit_extracted_to_holding_pct: float  # 0..1
    debt_loaded_for_extraction: bool
    subsidiary_liability_shuffling: bool

    # cascade signals
    sole_employer_dependency: float    # 0..1 -- community dependence on this firm
    substrate_knowledge_retained: float  # 0..1 -- how much knowledge stays vs leaves


# -----------------------------------------------------------
# LAYER 1: ACTUARIAL RESILIENCE PRICING
# -----------------------------------------------------------

def actuarial_resilience_score(b: BusinessProfile) -> dict:
    """
    Reframes insurance pricing from short-term extraction risk
    to long-term cascade-failure risk.

    LOWER score = lower premium (better risk).
    HIGHER score = higher premium (worse risk).
    """
    # short-term risk (current actuary view)
    short_term = (
        b.accident_rate_per_1000 / 100.0 +
        b.turnover_rate_pct / 100.0
    )

    # systemic risk (the missing layer)
    instability_penalty = 0.0
    if b.avg_tenure_years < 3.0:
        instability_penalty += 0.30
    if not b.pension_or_equivalent:
        instability_penalty += 0.20
    if b.discretionary_effort_index < 0.4:
        instability_penalty += 0.25
    if b.substrate_knowledge_retained < 0.3:
        instability_penalty += 0.20

    cascade_penalty = (
        b.sole_employer_dependency * 0.4 +
        b.externalized_costs * 0.5 +
        b.profit_extracted_to_holding_pct * 0.3
    )

    # commitment discount
    discount = 0.0
    if b.avg_tenure_years > 7:
        discount += 0.15
    if b.pension_or_equivalent:
        discount += 0.20
    if b.discretionary_effort_index > 0.7:
        discount += 0.15
    if b.local_supplier_pct > 0.5:
        discount += 0.10

    total = short_term + instability_penalty + cascade_penalty - discount
    return {
        "premium_index": round(max(0.05, total), 3),
        "short_term_risk": round(short_term, 3),
        "systemic_risk": round(instability_penalty + cascade_penalty, 3),
        "commitment_discount": round(discount, 3),
    }


# -----------------------------------------------------------
# LAYER 2: MUNICIPAL REPUTATION SCORE
# -----------------------------------------------------------

def municipal_reputation_score(b: BusinessProfile) -> dict:
    """
    Score the business as a community member.
    Used by municipality for zoning, permits, contract eligibility.

    Range: -1.0 (extraction predator) to +1.0 (substrate contributor)
    """
    contribution = (
        b.local_supplier_pct * 0.20 +
        b.profit_recirculated_local_pct * 0.25 +
        b.discretionary_effort_index * 0.10 +
        b.substrate_knowledge_retained * 0.15 +
        min(b.community_lifespan_years / 50.0, 1.0) * 0.20 +
        (0.10 if b.pension_or_equivalent else 0.0)
    )

    extraction = (
        b.profit_extracted_to_holding_pct * 0.30 +
        b.externalized_costs * 0.30 +
        (0.20 if b.debt_loaded_for_extraction else 0.0) +
        (0.20 if b.subsidiary_liability_shuffling else 0.0)
    )

    score = round(contribution - extraction, 3)
    classification = (
        "substrate_contributor" if score > 0.4 else
        "neutral"               if score > -0.1 else
        "extraction_predator"
    )
    return {
        "score": score,
        "contribution": round(contribution, 3),
        "extraction": round(extraction, 3),
        "classification": classification,
    }


# -----------------------------------------------------------
# LAYER 3: TAX / ZONING INCENTIVE
# -----------------------------------------------------------

def tax_and_zoning_treatment(b: BusinessProfile, base_rate: float = 0.05) -> dict:
    """
    Tax rate scales with extraction ratio.
    Substrate contributors get reduced rates and zoning priority.
    Extraction predators pay more and face zoning friction.
    """
    rep = municipal_reputation_score(b)
    score = rep["score"]

    if score > 0.4:
        rate_multiplier = 0.5
        zoning = "priority"
        permit_speed = "expedited"
    elif score > 0.1:
        rate_multiplier = 0.75
        zoning = "favorable"
        permit_speed = "standard"
    elif score > -0.1:
        rate_multiplier = 1.0
        zoning = "standard"
        permit_speed = "standard"
    elif score > -0.4:
        rate_multiplier = 1.5
        zoning = "restricted"
        permit_speed = "extended_review"
    else:
        rate_multiplier = 2.5
        zoning = "blocked"
        permit_speed = "denied_pending_review"

    return {
        "effective_tax_rate": round(base_rate * rate_multiplier, 4),
        "zoning_status": zoning,
        "permit_speed": permit_speed,
        "rate_multiplier": rate_multiplier,
    }


# -----------------------------------------------------------
# COUPLED FRAMEWORK
# -----------------------------------------------------------

def evaluate_business(b: BusinessProfile) -> dict:
    return {
        "name": b.name,
        "actuarial": actuarial_resilience_score(b),
        "reputation": municipal_reputation_score(b),
        "tax_zoning": tax_and_zoning_treatment(b),
    }


# -----------------------------------------------------------
# REFERENCE PROFILES
# -----------------------------------------------------------

def reference_profiles() -> List[BusinessProfile]:
    return [
        BusinessProfile(
            name="Long-tenure regional manufacturer (Costco-like)",
            avg_tenure_years=9.0, pension_or_equivalent=True,
            discretionary_effort_index=0.78,
            accident_rate_per_1000=2.1, turnover_rate_pct=12.0,
            local_supplier_pct=0.45, profit_recirculated_local_pct=0.55,
            community_lifespan_years=40, externalized_costs=0.10,
            profit_extracted_to_holding_pct=0.20,
            debt_loaded_for_extraction=False,
            subsidiary_liability_shuffling=False,
            sole_employer_dependency=0.30,
            substrate_knowledge_retained=0.80,
        ),
        BusinessProfile(
            name="Big-box extraction model (Walmart-like)",
            avg_tenure_years=1.8, pension_or_equivalent=False,
            discretionary_effort_index=0.30,
            accident_rate_per_1000=4.5, turnover_rate_pct=68.0,
            local_supplier_pct=0.05, profit_recirculated_local_pct=0.10,
            community_lifespan_years=15, externalized_costs=0.55,
            profit_extracted_to_holding_pct=0.85,
            debt_loaded_for_extraction=True,
            subsidiary_liability_shuffling=True,
            sole_employer_dependency=0.65,
            substrate_knowledge_retained=0.15,
        ),
        BusinessProfile(
            name="Small local farm cooperative",
            avg_tenure_years=15.0, pension_or_equivalent=False,
            discretionary_effort_index=0.85,
            accident_rate_per_1000=3.0, turnover_rate_pct=8.0,
            local_supplier_pct=0.85, profit_recirculated_local_pct=0.90,
            community_lifespan_years=60, externalized_costs=0.05,
            profit_extracted_to_holding_pct=0.05,
            debt_loaded_for_extraction=False,
            subsidiary_liability_shuffling=False,
            sole_employer_dependency=0.10,
            substrate_knowledge_retained=0.95,
        ),
        BusinessProfile(
            name="PE-owned roll-up (debt-loaded extraction)",
            avg_tenure_years=1.2, pension_or_equivalent=False,
            discretionary_effort_index=0.20,
            accident_rate_per_1000=6.0, turnover_rate_pct=85.0,
            local_supplier_pct=0.02, profit_recirculated_local_pct=0.05,
            community_lifespan_years=4, externalized_costs=0.70,
            profit_extracted_to_holding_pct=0.95,
            debt_loaded_for_extraction=True,
            subsidiary_liability_shuffling=True,
            sole_employer_dependency=0.50,
            substrate_knowledge_retained=0.05,
        ),
    ]


# -----------------------------------------------------------
# DEMO
# -----------------------------------------------------------

if __name__ == "__main__":
    profiles = reference_profiles()

    for b in profiles:
        result = evaluate_business(b)
        print(f"\n{'=' * 70}")
        print(f"  {result['name']}")
        print(f"{'=' * 70}")

        a = result["actuarial"]
        print("  ACTUARIAL")
        print(f"    premium_index:        {a['premium_index']}")
        print(f"    short_term_risk:      {a['short_term_risk']}")
        print(f"    systemic_risk:        {a['systemic_risk']}")
        print(f"    commitment_discount:  {a['commitment_discount']}")

        r = result["reputation"]
        print("  MUNICIPAL REPUTATION")
        print(f"    score:                {r['score']:+.3f}")
        print(f"    classification:       {r['classification']}")

        t = result["tax_zoning"]
        print("  TAX / ZONING")
        print(f"    effective_tax_rate:   {t['effective_tax_rate']}")
        print(f"    zoning_status:        {t['zoning_status']}")
        print(f"    permit_speed:         {t['permit_speed']}")

    print(f"\n{'=' * 70}")
    print("  HYPOTHESIS")
    print(f"{'=' * 70}")
    print("  Extraction-model businesses face higher actuarial premiums,")
    print("  worse municipal reputation, and 2-3x effective tax rates.")
    print("  Substrate-contributor businesses get lower premiums, priority")
    print("  zoning, and reduced tax rates.")
    print("  The incentive structure FLIPS without changing the underlying laws --")
    print("  it changes the PRICING of cost-sources and risk pools.")
