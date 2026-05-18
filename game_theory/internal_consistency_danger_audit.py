"""
game_theory/internal_consistency_danger_audit.py

DANGER SIGNAL: Internal consistency without reality-checking

A mathematically beautiful model that's disconnected from actual
constraint space is the most dangerous kind of false knowledge.

Because:
1. It's persuasive (internally coherent, elegant, provable)
2. It's self-reinforcing (contradictions are resolved within the system)
3. It's institutionally protected (institutions depend on it being true)
4. It has no built-in error detection (consistency != correctness)

Example: Flat Earth theory
- Internally consistent geometry (if you ignore scale and curvature)
- Mathematically provable (within its own axioms)
- Self-reinforcing (any contradiction gets explained within the system)
- Completely wrong about reality

Example: Perfect information rational actor hierarchy
- Internally consistent game theory
- Mathematically provable
- Self-reinforcing (failures explained as "market inefficiency," not hierarchy failure)
- Completely wrong about actual governance outcomes

Fourth sibling in the game-theory-foundations audit series; meta-audit
naming why the prior three matter so much:
- game_theory/rationality_audit.py        -- audits "rational actor" definition
- game_theory/information_completeness_audit.py -- audits "relevant information"
- game_theory/mathematical_proof_vs_physical_reality.py -- audits proof-vs-artifact gap
- this module                              -- audits the danger of internal-consistency-without-reality

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass


@dataclass
class ConsistencyAudit:
    system_name: str
    internally_consistent: bool
    checked_against_reality: bool
    prediction_accuracy: float
    institutionally_protected: bool
    has_dissent_function: bool

    def danger_level(self) -> str:
        if self.internally_consistent and not self.checked_against_reality:
            return "CRITICAL DANGER"
        if self.internally_consistent and self.prediction_accuracy < 0.5:
            return "CRITICAL DANGER"
        if self.institutionally_protected and not self.has_dissent_function:
            return "CRITICAL DANGER"
        if (
            self.internally_consistent
            and self.checked_against_reality
            and self.prediction_accuracy > 0.8
        ):
            return "SAFE"
        return "MODERATE CONCERN"


# =============================================
# SMOKE TEST
# =============================================

if __name__ == "__main__":
    flat_earth = ConsistencyAudit(
        system_name="Flat Earth Theory",
        internally_consistent=True,
        checked_against_reality=False,
        prediction_accuracy=0.0,
        institutionally_protected=False,
        has_dissent_function=False,
    )

    hierarchy_theory = ConsistencyAudit(
        system_name="Perfect-Information Rational-Actor Hierarchy",
        internally_consistent=True,
        checked_against_reality=False,
        prediction_accuracy=0.2,
        institutionally_protected=True,
        has_dissent_function=False,
    )

    earth_systems_physics = ConsistencyAudit(
        system_name="Earth Systems Physics with Formalized Dissent",
        internally_consistent=True,
        checked_against_reality=True,
        prediction_accuracy=0.75,
        institutionally_protected=False,
        has_dissent_function=True,
    )

    for audit in [flat_earth, hierarchy_theory, earth_systems_physics]:
        print(f"\n{audit.system_name}")
        print(f"  Internally consistent? {audit.internally_consistent}")
        print(f"  Checked against reality? {audit.checked_against_reality}")
        print(f"  Prediction accuracy: {audit.prediction_accuracy:.1%}")
        print(f"  Institutionally protected? {audit.institutionally_protected}")
        print(f"  Has dissent function? {audit.has_dissent_function}")
        print(f"  -> DANGER LEVEL: {audit.danger_level()}")

    print("\n" + "=" * 70)
    print("KEY INSIGHT:")
    print("Internal consistency WITHOUT reality-checking is the MOST dangerous.")
    print("Because it's persuasive AND wrong.")
    print("Which means it can persist, accumulate institutional power,")
    print("and cause massive damage before anyone notices the disconnect.")
