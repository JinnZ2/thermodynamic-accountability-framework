"""
calibration/systemic_cognitive_dissonance_audit.py

HYPOTHESIS: Rising mental health crisis (anxiety, depression, bipolar
diagnosis, etc.) correlates with systemic demand to hold contradictory
epistemologies simultaneously.

MECHANISM:
1. Culture teaches: "Scientific thinking is good"
2. Culture practices: Anti-scientific interpersonal/institutional behavior
3. Individual experiences: Constant contradiction between teaching and practice
4. Individual response: Either compartmentalize (split self) or model collapse

COMPARTMENTALIZATION (short-term):
- Work self (follow rules, defend position, seek consensus)
- Private self (question, explore, change mind)
- Keeps you functional but costs metabolic energy (constant code-switching)

MODEL COLLAPSE (inevitable):
- Eventually you can't hold contradictions
- System demands you choose: be scientific OR be socially acceptable
- Can't choose both (they're incompatible in this culture)
- Result: anxiety (trying to hold both), depression (giving up trying),
  bipolar cycling (oscillating between frames)

This isn't illness. This is thermodynamic overload.

Sister to metrology/substrate_damage_audit.py (audits behavioral /
collapse-prediction / capacity models built on populations exhibiting
institutional substrate damage -- same reframe applied at the
population-statistics level rather than the individual-load level).
Also sister to calibration/architecture_mismatch.py and the
attribution-architecture stack (load-routing under cross-architecture
demands).

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class CognitiveDissonanceLoad:
    person: str
    contradictions_held: List[str]
    energy_cost_daily: str
    compartmentalization_active: bool
    model_collapse_risk: str  # low / moderate / high / critical

    def thermodynamic_verdict(self) -> str:
        if len(self.contradictions_held) > 3 and self.compartmentalization_active:
            return "UNSUSTAINABLE - person is burning energy maintaining split"
        if len(self.contradictions_held) > 5:
            return "CRITICAL - model collapse imminent"
        return f"HIGH LOAD - {len(self.contradictions_held)} active contradictions"


# =============================================
# SMOKE TEST
# =============================================

if __name__ == "__main__":
    example = CognitiveDissonanceLoad(
        person="Typical institutional person",
        contradictions_held=[
            "Be scientific / Act anti-scientifically",
            "Think for yourself / Maintain consensus",
            "Question authority / Obey hierarchy",
            "Admit mistakes / Defend position",
            "Be vulnerable / Hide weakness",
            "Embrace change / Maintain identity",
            "Listen to others / Don't let them change you",
        ],
        energy_cost_daily="Massive - constant code-switching between selves",
        compartmentalization_active=True,
        model_collapse_risk="high",
    )

    print(f"Person: {example.person}")
    print(f"Contradictions held: {len(example.contradictions_held)}")
    for i, contradiction in enumerate(example.contradictions_held, 1):
        print(f"  {i}. {contradiction}")
    print(f"\nEnergy cost: {example.energy_cost_daily}")
    print(f"Verdict: {example.thermodynamic_verdict()}")
