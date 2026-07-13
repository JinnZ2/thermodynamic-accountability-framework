# seeam_unified.py
"""
SEEAM Unified Audit Module
Systemic Energy-Extraction Audit – Falsifies the "Human Capital" Hypothesis
Thermodynamic & Resource-Economics Foundation
"""

import json
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

# ----------------------------------------------------------------------
# 1. OIL BENCHMARK DATA (reference values for resource-industry comparison)
# ----------------------------------------------------------------------

DEFAULT_OIL_BENCHMARK = {
    "upstream_capex_billion_usd": 500,
    "midstream_capex_billion_usd": 150,
    "refining_capex_billion_usd": 80,
    "total_capex_billion_usd": 730,
    "global_production_million_bbl_per_day": 100,
    "average_oil_price_per_bbl": 80,
}

def load_oil_benchmark(source: str = "default") -> Dict:
    """Return oil-industry capex and revenue benchmark."""
    if source == "default":
        b = DEFAULT_OIL_BENCHMARK
        total_capex = b["total_capex_billion_usd"] * 1e9
        total_bbl = b["global_production_million_bbl_per_day"] * 1e6 * 365
        revenue = b["average_oil_price_per_bbl"] * total_bbl
        return {
            "dependency_investment_per_barrel": total_capex / total_bbl,
            "oil_investment_ratio": total_capex / revenue,
        }
    # else load from file
    with open(source) as f:
        data = json.load(f)
    return data

# ----------------------------------------------------------------------
# 2. INDIVIDUAL VIABILITY EVALUATOR (micro-level)
# ----------------------------------------------------------------------

class HumanCapitalEvaluator:
    """Tests if a single worker can sustain themselves.
    Negative net surplus = the 'human capital' label is falsified for this node.
    """
    def __init__(self, income: float, location_expenses: float,
                 commute_costs: float, health_wellness: float,
                 daycare: float, other_deps: Optional[Dict[str, float]] = None):
        self.income = income
        self.dependencies = {
            "location_premium": location_expenses,
            "commute": commute_costs,
            "health_maintenance": health_wellness,
            "childcare": daycare
        }
        if other_deps:
            self.dependencies.update(other_deps)

    def calculate_net_surplus(self) -> float:
        return self.income - sum(self.dependencies.values())

    def production_gap(self) -> float:
        """Gap when income cannot meet basic consumption needs (simplified)."""
        # Here we treat the minimum adequate consumption as the dependency floor.
        return max(0, sum(self.dependencies.values()) - self.income)

    def consumption_gap(self) -> float:
        """Unrealised consumption due to low surplus."""
        surplus = self.calculate_net_surplus()
        return max(0, 0 - surplus)  # if surplus negative, that's consumption deficit

    def self_financing_ratio(self) -> float:
        total_deps = sum(self.dependencies.values())
        return total_deps / self.income if self.income else float('inf')

    def audit_report(self) -> dict:
        surplus = self.calculate_net_surplus()
        return {
            "income": self.income,
            "dependencies": self.dependencies,
            "net_surplus": surplus,
            "production_gap": self.production_gap(),
            "consumption_gap": self.consumption_gap(),
            "self_financing_ratio": self.self_financing_ratio(),
            "viable": surplus > 0,
            "verdict": "ASSET MAINTAINED" if surplus > 0 else "EXTRACTION"
        }

# ----------------------------------------------------------------------
# 3. COHORT-LEVEL INFRASTRUCTURE & RESERVE MODEL
# ----------------------------------------------------------------------

@dataclass
class HumanCapitalInfrastructure:
    cohort_id: str
    population_count: int
    early_childhood_dev_cost_per_child: float
    k12_education_cost_per_student_year: float
    higher_education_cost_per_student_year: float
    vocational_training_cost_per_trainee: float
    digital_infrastructure_cost_per_capita: float
    transportation_access_cost_per_capita: float
    upskilling_reskilling_cost_per_worker_year: float
    job_matching_services_cost_per_capita: float
    credentialing_licensing_cost_per_capita: float
    healthcare_cost_per_capita_year: float
    social_safety_net_cost_per_capita: float
    retirement_pension_cost_per_retiree_year: float
    actual_spending: Dict[str, float] = field(default_factory=dict)

    def optimal_annual_investment_per_capita(self) -> float:
        # simplified amortisation
        return (self.early_childhood_dev_cost_per_child / 18 +
                self.k12_education_cost_per_student_year * 0.15 +
                self.higher_education_cost_per_student_year * 0.05 +
                self.vocational_training_cost_per_trainee * 0.02 +
                self.digital_infrastructure_cost_per_capita / 10 +
                self.transportation_access_cost_per_capita / 10 +
                self.upskilling_reskilling_cost_per_worker_year * 0.6 +
                self.job_matching_services_cost_per_capita +
                self.credentialing_licensing_cost_per_capita +
                self.healthcare_cost_per_capita_year +
                self.social_safety_net_cost_per_capita +
                self.retirement_pension_cost_per_retiree_year * 0.2)

    def actual_annual_investment_per_capita(self) -> float:
        return sum(self.actual_spending.values())

    def system_efficiency_ratio(self) -> float:
        opt = self.optimal_annual_investment_per_capita()
        return self.actual_annual_investment_per_capita() / opt if opt else 0.0

@dataclass
class ResourceSelfFinancing:
    cohort_id: str
    individual_share_higher_ed: float = 0.0
    individual_share_healthcare: float = 0.0
    individual_share_retraining: float = 0.0
    total_optimal_investment_per_capita: float = 0.0

    def individual_contribution_per_capita(self) -> float:
        # rough weighting; real implementation should use actual component costs
        return (self.individual_share_higher_ed * 0.15 +
                self.individual_share_healthcare * 0.10 +
                self.individual_share_retraining * 0.05) * self.total_optimal_investment_per_capita

    def resource_self_financing_ratio(self) -> float:
        if self.total_optimal_investment_per_capita == 0:
            return 0.0
        return self.individual_contribution_per_capita() / self.total_optimal_investment_per_capita


@dataclass
class HumanReserveAsset:
    cohort_id: str
    description: str
    age_range: tuple
    population_count: int
    proved_reserves_count: int
    probable_reserves_count: int
    possible_reserves_count: int
    contingent_resources_count: int
    proved_production_curve: List[float]
    probable_production_curve: List[float]
    possible_production_curve: List[float]
    price_per_unit: float
    extraction_cost_per_unit: float
    development_capex_per_capita: float
    infrastructure: Optional[HumanCapitalInfrastructure] = None
    self_financing: Optional[ResourceSelfFinancing] = None
    discount_rate: float = 0.10

    def _npv(self, production: List[float]) -> float:
        cashflows = [v * (self.price_per_unit - self.extraction_cost_per_unit) for v in production]
        return sum(c / (1 + self.discount_rate) ** (i + 1) for i, c in enumerate(cashflows))

    def standardized_measure(self) -> Dict[str, float]:
        return {
            'proved_npv10': self._npv(self.proved_production_curve),
            'probable_npv10': self._npv(self.probable_production_curve),
            'possible_npv10': self._npv(self.possible_production_curve),
            'total_3p_npv10': (self._npv(self.proved_production_curve) +
                               self._npv(self.probable_production_curve) +
                               self._npv(self.possible_production_curve))
        }

    def fair_npv(self, category='proved') -> float:
        sf_per_fte = 0
        if self.self_financing and self.infrastructure:
            sf_per_fte = self.self_financing.individual_contribution_per_capita()
        full_cost = self.extraction_cost_per_unit + sf_per_fte
        orig = self.extraction_cost_per_unit
        self.extraction_cost_per_unit = full_cost
        npv_val = self._npv(getattr(self, f'{category}_production_curve'))
        self.extraction_cost_per_unit = orig
        return npv_val

    def systemic_drag(self, siblings_expected_output: List[float],
                      siblings_actual_output: List[float]) -> float:
        """Total output deficit of siblings relative to expected (parity)."""
        return sum(max(0, exp - act) for exp, act in zip(siblings_expected_output, siblings_actual_output))


# ----------------------------------------------------------------------
# 4. POTENTIAL EVALUATOR (aggregates individual gaps and cohort drag)
# ----------------------------------------------------------------------

class PotentialEvaluator:
    def __init__(self, individuals: List[HumanCapitalEvaluator],
                 cohort_asset: HumanReserveAsset,
                 siblings_expected: Optional[List[float]] = None,
                 siblings_actual: Optional[List[float]] = None):
        self.individuals = individuals
        self.asset = cohort_asset
        self.siblings_expected = siblings_expected or []
        self.siblings_actual = siblings_actual or []

    def calculate_optimization_gap(self) -> dict:
        production_gap = sum(ind.production_gap() for ind in self.individuals)
        consumption_gap = sum(ind.consumption_gap() for ind in self.individuals)
        drag = 0.0
        if self.siblings_expected and self.siblings_actual:
            drag = self.asset.systemic_drag(self.siblings_expected, self.siblings_actual)
        return {
            "production_gap": production_gap,
            "consumption_gap": consumption_gap,
            "systemic_drag": drag,
            "total_optimization_failure": production_gap + consumption_gap + drag
        }

# ----------------------------------------------------------------------
# 5. UNIFIED AUDIT ENGINE (Rule Registry + Gap + Drift + Verdict)
# ----------------------------------------------------------------------

class SEEAMUnifiedAudit:
    def __init__(self, cohort_asset: HumanReserveAsset,
                 individuals: List[HumanCapitalEvaluator],
                 siblings_expected: Optional[List[float]] = None,
                 siblings_actual: Optional[List[float]] = None,
                 previous_report: Optional[dict] = None):
        self.asset = cohort_asset
        self.individuals = individuals
        self.evaluator = PotentialEvaluator(individuals, cohort_asset,
                                            siblings_expected, siblings_actual)
        self.previous = previous_report
        self.oil_data = load_oil_benchmark()

    def check_rules(self) -> dict:
        failures = []
        sm = self.asset.standardized_measure()
        infra = self.asset.infrastructure
        sf = self.asset.self_financing

        sys_eff = infra.system_efficiency_ratio() if infra else 0.0
        rs_fin = sf.resource_self_financing_ratio() if sf else 0.0
        dep_parity = 0.0
        if infra and sm['total_3p_npv10']:
            actual_inv = infra.actual_annual_investment_per_capita()
            human_value_per_capita = sm['total_3p_npv10'] / self.asset.population_count
            oil_ratio = self.oil_data['oil_investment_ratio']
            if human_value_per_capita:
                dep_parity = (actual_inv / human_value_per_capita) / oil_ratio

        if sys_eff < 0.6:
            failures.append(f"System efficiency ratio {sys_eff:.2f} < 0.6")
        if rs_fin > 0.05:
            failures.append(f"RSFR {rs_fin:.2f} > 0.05")
        if dep_parity < 0.8:
            failures.append(f"Dependency parity {dep_parity:.2f} < 0.8")
        
        fair_npv_proved = self.asset.fair_npv('proved')
        fairness_gap = sm['proved_npv10'] - fair_npv_proved
        if sm['proved_npv10'] and abs(fairness_gap) / sm['proved_npv10'] > 0.2:
            failures.append(f"Fairness gap too large: {fairness_gap:.0f}")

        return {
            "metrics": {
                "proved_npv10": sm['proved_npv10'],
                "total_3p_npv10": sm['total_3p_npv10'],
                "system_efficiency_ratio": sys_eff,
                "cohort_rsfr": rs_fin,
                "dependency_parity_index": dep_parity,
                "fair_npv_proved": fair_npv_proved,
                "fairness_gap": fairness_gap
            },
            "failures": failures
        }

    def run(self) -> dict:
        rule_results = self.check_rules()
        gaps = self.evaluator.calculate_optimization_gap()

        drift_alerts = []
        if self.previous:
            prev_gaps = self.previous.get("gaps", {})
            for k in gaps:
                prev_val = prev_gaps.get(k, 0)
                change = gaps[k] - prev_val
                threshold = 0.05 * (abs(prev_val) + 1e-6)
                if abs(change) > threshold:
                    drift_alerts.append(f"{k} changed by {change:.2f} (threshold {threshold:.2f})")

        hypothesis_falsified = len(rule_results['failures']) > 0 or gaps['total_optimization_failure'] > 0

        return {
            "cohort_id": self.asset.cohort_id,
            "rule_registry": rule_results,
            "optimization_gaps": gaps,
            "drift_alerts": drift_alerts,
            "hypothesis_falsified": hypothesis_falsified,
            "verdict": "HUMAN CAPITAL HYPOTHESIS CONSISTENT" if not hypothesis_falsified
                       else "FALSIFIED: extraction or underinvestment detected."
        }

# ----------------------------------------------------------------------
# 6. DEMONSTRATION WITH FAMILY #001 DATA
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Cohort: 4 siblings, one received $80k loan and defaulted
    # Production curves (annual output, e.g. income)
    years = 30
    # C1 (proved) income $50k, declining 2%
    proved_curve = [50000 * 0.98**t for t in range(years)]
    # Siblings (possible) – we'll use their actual incomes for now
    # In a real run, possible reserves would have their own production curve.
    # We'll set them to zero for simplicity; they are considered "unproven" in traditional accounting.
    probable_curve = []
    possible_curve = [0]*years

    # Infrastructure (simplified: actual public spending values are estimates)
    infra = HumanCapitalInfrastructure(
        cohort_id="Family_001",
        population_count=4,
        early_childhood_dev_cost_per_child=3000,  # per child
        k12_education_cost_per_student_year=8000,
        higher_education_cost_per_student_year=20000,  # partly covered by parents/loans
        vocational_training_cost_per_trainee=5000,
        digital_infrastructure_cost_per_capita=600,
        transportation_access_cost_per_capita=1000,
        upskilling_reskilling_cost_per_worker_year=0,
        job_matching_services_cost_per_capita=100,
        credentialing_licensing_cost_per_capita=200,
        healthcare_cost_per_capita_year=5000,
        social_safety_net_cost_per_capita=2000,
        retirement_pension_cost_per_retiree_year=15000,
        actual_spending={  # what was actually provided by family / public
            "early_childhood": 1000,
            "k12": 7000,  # public school
            "higher_ed": 60000,  # total for C1 (loan) – others only $5k each → huge concentration
            "vocational": 0,
            "digital": 300,
            "transport": 500,
            "upskilling": 0,
            "job_match": 0,
            "credential": 50,
            "healthcare": 4000,
            "safety_net": 1000,
            "pension": 0
        }
    )
    sf = ResourceSelfFinancing(
        cohort_id="Family_001",
        individual_share_higher_ed=0.9,  # student loans covered most
        individual_share_healthcare=0.5,  # out-of-pocket
        individual_share_retraining=0.0,
        total_optimal_investment_per_capita=infra.optimal_annual_investment_per_capita()
    )

    asset = HumanReserveAsset(
        cohort_id="Family_001",
        description="Sibling group with concentrated loan and default",
        age_range=(25, 64),
        population_count=4,
        proved_reserves_count=1,
        probable_reserves_count=0,
        possible_reserves_count=3,
        contingent_resources_count=0,
        proved_production_curve=proved_curve,
        probable_production_curve=probable_curve,
        possible_production_curve=possible_curve,
        price_per_unit=1,          # treat output directly as income
        extraction_cost_per_unit=0, # dependency costs handled separately
        development_capex_per_capita=0,
        infrastructure=infra,
        self_financing=sf
    )

    # Individual evaluators – net monthly converted to annual, but we use annual here
    c1 = HumanCapitalEvaluator(income=50000, location_expenses=12000, commute_costs=2400,
                               health_wellness=3000, daycare=0)
    c2 = HumanCapitalEvaluator(income=22000, location_expenses=9000, commute_costs=1500,
                               health_wellness=2000, daycare=0)
    c3 = HumanCapitalEvaluator(income=18000, location_expenses=8000, commute_costs=1200,
                               health_wellness=1500, daycare=0)
    c4 = HumanCapitalEvaluator(income=30000, location_expenses=10000, commute_costs=2000,
                               health_wellness=2500, daycare=5000)
    individuals = [c1, c2, c3, c4]

    # Sibling expected output for drag calculation (if all had equal resources ~$40k)
    expected = [40000, 40000, 40000]
    actual_sib = [22000, 18000, 30000]

    audit = SEEAMUnifiedAudit(asset, individuals, expected, actual_sib)
    result = audit.run()
    print(json.dumps(result, indent=2))
