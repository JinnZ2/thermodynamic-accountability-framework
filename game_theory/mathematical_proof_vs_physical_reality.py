"""
game_theory/mathematical_proof_vs_physical_reality.py

CORE PROBLEM:

Mathematics operates in a space where:
- Assumptions can be perfect (infinite precision, no friction, no time)
- Operations are reversible (divide by zero doesn't exist, entropy can go backward)
- Objects are eternal (circles don't wear out, hierarchies don't degrade)

Reality operates in a space where:
- Every assumption breaks under actual conditions
- Every operation has friction and entropy
- Every system decays, requires maintenance, fails

So a mathematical "proof" that hierarchy is optimal tells you NOTHING
about whether hierarchies actually work in constraint space.

It tells you: "IF these impossible conditions were true, THEN hierarchy
would work."

But the conditions are never true.

The perfect circle has never existed. We can describe it mathematically.
We cannot make it. The gap between the proof and the artifact is infinite.

Same with "rational actor hierarchies."

Third sibling in the game-theory-foundations audit series:
- game_theory/rationality_audit.py        -- audits the "rational actor" definition
- game_theory/information_completeness_audit.py -- audits the "relevant information" assumption
- this module                              -- audits the "mathematical proof of optimality" assumption

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class MathematicalModel:
    """What the proof assumes."""
    name: str
    perfect_conditions: List[str] = field(default_factory=list)
    reversibility: bool = False
    friction: bool = True
    time: bool = True
    feedback: bool = True

    def gap_to_reality(self) -> List[str]:
        """What has to be true in math that's false in reality?"""
        gaps = []
        if not self.friction:
            gaps.append("Math assumes no friction; reality: friction everywhere")
        if not self.time:
            gaps.append("Math assumes timeless; reality: everything decays")
        if self.reversibility:
            gaps.append("Math assumes reversible; reality: entropy is irreversible")
        if not self.feedback:
            gaps.append("Math assumes errors don't compound; reality: they do exponentially")
        return gaps


# =============================================
# SMOKE TEST
# =============================================

if __name__ == "__main__":
    math_hierarchy = MathematicalModel(
        name="Game theory hierarchy proof",
        perfect_conditions=[
            "Perfect information",
            "Rational actors",
            "No time cost to communication",
            "No information loss through layers",
            "No enforcement cost",
            "Decisions are reversible",
            "No fatigue, burnout, or degradation",
            "Utility is objective and measurable",
        ],
        reversibility=True,
        friction=False,
        time=False,
        feedback=False,
    )

    real_hierarchy = MathematicalModel(
        name="Hierarchy under field conditions",
        perfect_conditions=[],
        reversibility=False,
        friction=True,
        time=True,
        feedback=True,
    )

    print("MATHEMATICAL MODEL (hierarchy proof):")
    print(f"  Perfect conditions required: {len(math_hierarchy.perfect_conditions)}")
    for condition in math_hierarchy.perfect_conditions:
        print(f"    - {condition}")

    print(f"\n  Gap to reality:")
    for gap in math_hierarchy.gap_to_reality():
        print(f"    - {gap}")

    print("\n\nREAL HIERARCHY (field conditions):")
    print(f"  Perfect conditions required: {len(real_hierarchy.perfect_conditions)}")
    print(f"  Reversible? {real_hierarchy.reversibility}")
    print(f"  Frictionless? {not real_hierarchy.friction}")
    print(f"  Timeless? {not real_hierarchy.time}")
    print(f"  Error-feedback-free? {not real_hierarchy.feedback}")

    print("\n\nVERDICT:")
    print("Mathematical proof tells you hierarchy is optimal IF conditions are perfect.")
    print("Field conditions are never perfect.")
    print("Therefore, the proof tells you nothing about whether hierarchy actually works.")
    print("")
    print("This is like proving the perfect circle exists mathematically,")
    print("then claiming you can therefore make one with a compass.")
    print("You can't. The proof doesn't transfer to reality.")
