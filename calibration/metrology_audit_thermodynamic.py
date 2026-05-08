"""
metrology_audit_thermodynamic.py

Detect measurement system corruption by testing against thermodynamic
reality.

Core principle: any measurement system used as basis for prediction,
policy, or AI training must be auditable against physical /
thermodynamic constraints. If it is not, downstream predictions will
fail and corruption will cascade.

Catches:
  - measurement gaps (what's not being counted)
  - thermodynamic violations (impossible energy budgets)
  - prediction failures (model doesn't match reality)
  - rational actor hypocrisy (model applied selectively)
  - cascade risk (where corruption will spread)

Sister to:
  - calibration/metrology_cancer_detector.py
      (the upstream "what's invisible in this dataset?" detector;
       this module adds thermodynamic-budget checking and the
       rational-actor-hypocrisy gate)
  - calibration/substrate_validation_oracle.py
      (validates AI outputs against substrate reality)
  - political_audit/substrate_audit.py
      (audits study claims against substrate biology)

CC0 -- stdlib only -- falsifiable.
Part of the metrology cancer detection toolkit.
"""

from dataclasses import dataclass, field
from typing import Dict, List


# =============================================================================
# THERMODYNAMIC BUDGET
# =============================================================================

@dataclass
class ThermodynamicBudget:
    """Energy / time / resource accounting at the substrate level."""
    name: str
    total_available: float       # hours, joules, dollars, etc.
    measured_allocation: float   # what the system counts
    unmeasured_allocation: float # what the system ignores but is happening
    unit: str = "hours/week"

    def total_actual(self) -> float:
        return self.measured_allocation + self.unmeasured_allocation

    def deficit(self) -> float:
        """Negative = sustainable. Positive = thermodynamic violation."""
        return self.total_actual() - self.total_available

    def is_physically_possible(self) -> bool:
        return self.deficit() <= 0

    def visibility_ratio(self) -> float:
        """Fraction of actual load that is visible to the measurement system."""
        if self.total_actual() == 0:
            return 1.0
        return self.measured_allocation / self.total_actual()

    def report(self) -> str:
        lines = [
            f"Budget: {self.name} ({self.unit})",
            f"  Available:    {self.total_available:.1f}",
            f"  Measured:     {self.measured_allocation:.1f}",
            f"  Unmeasured:   {self.unmeasured_allocation:.1f}",
            f"  Total actual: {self.total_actual():.1f}",
            f"  Deficit:      {self.deficit():+.1f}",
            f"  Visibility:   {self.visibility_ratio()*100:.0f}%",
            f"  Physically possible: {self.is_physically_possible()}",
        ]
        return "\n".join(lines)


# =============================================================================
# MEASUREMENT SYSTEM AUDIT
# =============================================================================

@dataclass
class MeasurementSystemAudit:
    """Audit a measurement system against thermodynamic reality."""
    system_name: str
    what_is_measured: List[str]
    what_is_ignored: List[str]
    predicted_outcome: str
    actual_outcome: str
    energy_budget: ThermodynamicBudget
    applies_universally: bool = True   # does the model claim universal scope?
    applied_to_modelers: bool = False  # do the modelers apply it to themselves?

    # ---------- core checks ----------

    def measurement_completeness(self) -> float:
        total = len(self.what_is_measured) + len(self.what_is_ignored)
        if total == 0:
            return 0.0
        return len(self.what_is_measured) / total

    def prediction_matches_reality(self) -> bool:
        """Crude string match -- caller can override with their own comparator."""
        return (
            self.predicted_outcome.strip().lower()
            == self.actual_outcome.strip().lower()
        )

    def thermodynamic_validity(self) -> bool:
        return self.energy_budget.is_physically_possible()

    def rational_actor_consistency(self) -> str:
        """The hypocrisy check: is the model applied to its own users?"""
        if not self.applies_universally:
            return (
                "SCOPED: model is explicitly limited, no universal claim "
                "-- coherent"
            )
        if self.applies_universally and self.applied_to_modelers:
            return "CONSISTENT: universal claim, modelers apply it to themselves"
        if self.applies_universally and not self.applied_to_modelers:
            return (
                "SELF_REFUTING: model claims universality but modelers "
                "exempt themselves. Either model is false, or modelers "
                "admit they are non-rational actors."
            )
        return "UNCLEAR"

    # ---------- diagnosis ----------

    def corruption_severity(self) -> str:
        score = 0
        if self.measurement_completeness() < 0.7:
            score += 1
        if not self.prediction_matches_reality():
            score += 1
        if not self.thermodynamic_validity():
            score += 2  # physical impossibility weighs double
        if "SELF_REFUTING" in self.rational_actor_consistency():
            score += 1

        if score == 0:
            return "CLEAN"
        if score == 1:
            return "DEGRADED"
        if score == 2:
            return "CORRUPTED"
        return "POISONED"  # cascade-spreading

    def cascade_risk(self) -> List[str]:
        """Where will this corruption spread if used as substrate?"""
        risks = []
        if self.corruption_severity() in ("CORRUPTED", "POISONED"):
            risks.append("AI trained on this data will inherit the gap")
            risks.append(
                "Policy built on this measurement will fail predictably"
            )
            risks.append(
                "Downstream models (rational actor, market, family) "
                "will collapse"
            )
            risks.append(
                "Failures will be blamed on agents, not the measurement system"
            )
        if not self.thermodynamic_validity():
            risks.append(
                "System is running an impossible load -- failure is "
                "inevitable, not random"
            )
        if "SELF_REFUTING" in self.rational_actor_consistency():
            risks.append(
                "Logical contradiction -- institutional credibility cannot "
                "survive disclosure"
            )
        return risks

    def diagnosis(self) -> List[str]:
        issues = []

        if self.measurement_completeness() < 0.7:
            missing = (
                ", ".join(self.what_is_ignored)
                if self.what_is_ignored else "unknown"
            )
            issues.append(
                f"INCOMPLETE: only {self.measurement_completeness()*100:.0f}% "
                f"of categories counted. Ignored: {missing}"
            )

        if not self.prediction_matches_reality():
            issues.append(
                f"INACCURATE: predicted '{self.predicted_outcome}' "
                f"but observed '{self.actual_outcome}'"
            )

        if not self.thermodynamic_validity():
            issues.append(
                f"PHYSICALLY_IMPOSSIBLE: deficit of "
                f"{self.energy_budget.deficit():+.1f} "
                f"{self.energy_budget.unit} -- system cannot sustain"
            )

        consistency = self.rational_actor_consistency()
        if "SELF_REFUTING" in consistency:
            issues.append(f"LOGICAL_CONTRADICTION: {consistency}")

        return issues if issues else ["No corruption detected"]

    def recommendations(self) -> List[str]:
        recs = []
        if not self.thermodynamic_validity():
            recs.append(
                "STOP using this measurement for prediction -- "
                "it violates physical law"
            )
        if self.measurement_completeness() < 0.7:
            recs.append(
                "ADD missing categories to the measurement system "
                "before any further use"
            )
            for cat in self.what_is_ignored:
                recs.append(f"  - measure: {cat}")
        if not self.prediction_matches_reality():
            recs.append(
                "DO NOT train AI on this substrate -- "
                "predictions will be garbage"
            )
        if "SELF_REFUTING" in self.rational_actor_consistency():
            recs.append("RESOLVE the rational actor contradiction:")
            recs.append("  (a) admit model is false and stop using it, or")
            recs.append("  (b) apply it to the modelers themselves, or")
            recs.append(
                "  (c) explicitly disclose modelers are exempt "
                "(loss of credibility)"
            )
        return recs

    # ---------- output ----------

    def audit_report(self) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append(f"METROLOGY AUDIT: {self.system_name}")
        lines.append("=" * 60)
        lines.append("")
        lines.append(self.energy_budget.report())
        lines.append("")
        lines.append(
            f"Measurement completeness: "
            f"{self.measurement_completeness()*100:.0f}%"
        )
        lines.append(
            f"Prediction matches reality: {self.prediction_matches_reality()}"
        )
        lines.append(f"Thermodynamic validity: {self.thermodynamic_validity()}")
        lines.append(
            f"Rational actor consistency: {self.rational_actor_consistency()}"
        )
        lines.append("")
        lines.append(f"CORRUPTION SEVERITY: {self.corruption_severity()}")
        lines.append("")
        lines.append("Diagnosis:")
        for issue in self.diagnosis():
            lines.append(f"  - {issue}")
        lines.append("")
        risks = self.cascade_risk()
        if risks:
            lines.append("Cascade risk if used as substrate:")
            for risk in risks:
                lines.append(f"  - {risk}")
            lines.append("")
        lines.append("Recommendations:")
        for rec in self.recommendations():
            lines.append(f"  - {rec}")
        lines.append("=" * 60)
        return "\n".join(lines)


# =============================================================================
# EXAMPLE AUDITS
# =============================================================================

def audit_gdp() -> MeasurementSystemAudit:
    """GDP measured against household labor thermodynamic reality."""
    budget = ThermodynamicBudget(
        name="adult woman, weekly time budget",
        total_available=112,         # 168 - 56 sleep
        measured_allocation=45,      # paid work GDP counts
        unmeasured_allocation=85,    # household + care + appearance + emotional
        unit="hours/week",
    )
    return MeasurementSystemAudit(
        system_name="GDP (economic measurement)",
        what_is_measured=[
            "paid labor hours",
            "market transactions",
            "industrial output",
            "financial flows",
        ],
        what_is_ignored=[
            "household labor (60-100 hrs/week)",
            "care work (emotional labor, health coordination)",
            "appearance labor (40+ hrs/week)",
            "environmental services (water, pollination, soil)",
            "knowledge transmission (education, mentoring)",
            "social capital (community bonds)",
        ],
        predicted_outcome=(
            "economic stability, rising productivity, stable demographics"
        ),
        actual_outcome=(
            "birth rates collapse, marriages fail, women withdraw, "
            "male health declines"
        ),
        energy_budget=budget,
        applies_universally=True,
        applied_to_modelers=False,   # modelers don't measure their own household labor
    )


def audit_ai_training_data() -> MeasurementSystemAudit:
    """AI training data inheriting GDP-level corruption."""
    budget = ThermodynamicBudget(
        name="AI training data coverage",
        total_available=100,
        measured_allocation=55,     # paid work + market data captured
        unmeasured_allocation=45,   # invisible labor + care work absent
        unit="% of actual economic substrate",
    )
    return MeasurementSystemAudit(
        system_name="AI training data (economic + social)",
        what_is_measured=[
            "documented transactions",
            "recorded paid labor",
            "market valuations",
            "institutional records",
        ],
        what_is_ignored=[
            "invisible household labor",
            "care work (unmeasured)",
            "appearance labor (unmeasured)",
            "actual energy flows in households",
            "load-bearing constraints (not visible)",
            "gender dynamics encoded as bias rather than structural variable",
        ],
        predicted_outcome=(
            "accurate predictions of consumer behavior, market dynamics, "
            "demographics"
        ),
        actual_outcome=(
            "prediction failures across consumer, marriage, birth rate, "
            "health metrics 2022-2026"
        ),
        energy_budget=budget,
        applies_universally=True,
        applied_to_modelers=False,
    )


def audit_rational_actor_model() -> MeasurementSystemAudit:
    """Hypocrisy trap: rational actor model applied to everyone except modelers."""
    budget = ThermodynamicBudget(
        name="rational actor decision-information budget",
        total_available=100,
        measured_allocation=60,     # info actors actually have
        unmeasured_allocation=40,   # info hidden by measurement gaps
        unit="% of relevant decision information",
    )
    return MeasurementSystemAudit(
        system_name="Rational Actor Model (as deployed by institutions)",
        what_is_measured=[
            "price signals",
            "stated preferences",
            "market behavior",
            "documented transactions",
        ],
        what_is_ignored=[
            "invisible labor inputs to decisions",
            "thermodynamic constraints on actors",
            "information asymmetries created by measurement gaps",
            "non-market value flows",
        ],
        predicted_outcome=(
            "actors make rational decisions, markets self-correct"
        ),
        actual_outcome=(
            "actors respond rationally to corrupted information, "
            "systems break"
        ),
        energy_budget=budget,
        applies_universally=True,    # claimed universal
        applied_to_modelers=False,   # but institutions exempt themselves
    )


# =============================================================================
# CASCADE TRACE: connect multiple audits to see metastasis path
# =============================================================================

@dataclass
class CascadeTrace:
    """Trace metrology corruption from origin through dependent systems."""
    origin: MeasurementSystemAudit
    dependents: List[MeasurementSystemAudit] = field(default_factory=list)

    def trace_report(self) -> str:
        lines = []
        lines.append("#" * 60)
        lines.append("METROLOGY CASCADE TRACE")
        lines.append("#" * 60)
        lines.append("")
        lines.append(f"ORIGIN: {self.origin.system_name}")
        lines.append(f"  Severity: {self.origin.corruption_severity()}")
        for issue in self.origin.diagnosis():
            lines.append(f"  - {issue}")
        lines.append("")
        for i, dep in enumerate(self.dependents, 1):
            lines.append(f"LAYER {i}: {dep.system_name}")
            lines.append(f"  Inherits from: {self.origin.system_name}")
            lines.append(f"  Severity: {dep.corruption_severity()}")
            for issue in dep.diagnosis():
                lines.append(f"  - {issue}")
            lines.append("")
        lines.append("CASCADE CONCLUSION:")
        lines.append(
            "  Fix the origin -> all dependent systems can be corrected."
        )
        lines.append(
            "  Treat only symptoms -> corruption keeps re-emerging downstream."
        )
        lines.append("#" * 60)
        return "\n".join(lines)


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    gdp = audit_gdp()
    ai = audit_ai_training_data()
    rational_actor = audit_rational_actor_model()

    print(gdp.audit_report())
    print()
    print(ai.audit_report())
    print()
    print(rational_actor.audit_report())
    print()

    cascade = CascadeTrace(origin=gdp, dependents=[ai, rational_actor])
    print(cascade.trace_report())
