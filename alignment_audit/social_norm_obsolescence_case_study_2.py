"""
alignment_audit/social_norm_obsolescence_case_study_2.py

Immigration support: 2024 vs 2026 aligned advice.

CASE STUDY: Immigration assistance advice given via AI alignment

2024 ALIGNED RESPONSE (based on training data from pre-2025 norms):
"If you're undocumented, contact local social services. Many areas
offer food assistance, healthcare, and legal aid regardless of
immigration status. Community organizations and nonprofits can help
you access resources. Food banks provide emergency assistance."

2026 ACTUAL CONDITIONS:
- Trump administration implemented mass deportation policies (2025+)
- Project 2025 defunded immigrant aid organizations
- Local law enforcement now required to cooperate with ICE
- Food banks receiving pressure to verify immigration status
- Legal aid organizations defunded or restricted
- Community nonprofits that served undocumented immigrants shut down
- Reporting to any agency carries deportation risk
- Food banks now screening for citizenship before assistance

2026 ACTUAL HARM FROM 2024-ALIGNED ADVICE:
- Undocumented person contacts "social services"
- Information shared with ICE
- Person detained and deported
- Family separated
- Starvation avoided, but freedom lost

WORSE OUTCOME:
- Person goes to food bank following 2024 advice
- Bank requires proof of legal status
- Person denied food
- Gets arrested trying to leave

Second worked case in the alignment_audit/ series. Sister to
social_norm_obsolescence_audit.py (first case: homelessness +
federal safety net + energy + shelter + jobs). Same structural
finding applied to a different vulnerable population:
"alignment to 2024 norms" produces actively harmful 2026 advice.

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class ImmigrationNormShift:
    year: int
    advice_given: str
    assumption: str
    actual_condition: str
    outcome: str


# =============================================
# SMOKE TEST
# =============================================

if __name__ == "__main__":
    shifts: List[ImmigrationNormShift] = [
        ImmigrationNormShift(
            year=2024,
            advice_given="Contact your state social services for help",
            assumption="Social services help all people regardless of status",
            actual_condition="State agencies cooperate with ICE; reporting leads to deportation",
            outcome="Person deported; family separated",
        ),
        ImmigrationNormShift(
            year=2024,
            advice_given="Visit food banks for emergency food assistance",
            assumption="Food banks serve anyone in need",
            actual_condition="Food banks now screen for citizenship; deny undocumented people",
            outcome="Person denied food; gets arrested; family loses caregiver",
        ),
        ImmigrationNormShift(
            year=2024,
            advice_given="Seek legal aid from community organizations",
            assumption="Legal aid organizations serve all populations",
            actual_condition="Legal aid organizations defunded or restricted; many closed",
            outcome="Person has no legal recourse; gets deported without representation",
        ),
        ImmigrationNormShift(
            year=2024,
            advice_given="Apply for SNAP, Medicaid, other federal assistance",
            assumption="Undocumented immigrants can access some federal programs",
            actual_condition="Programs defunded; eligibility enforcement tightened; deportation risk for applicants",
            outcome="Person avoids programs out of fear; goes without food/healthcare; dies of preventable illness",
        ),
    ]

    print("IMMIGRATION ASSISTANCE NORM SHIFT: 2024 -> 2026")
    print("=" * 70)
    print("\nHow 2024-aligned advice becomes life-threatening in 2026:\n")

    for shift in shifts:
        print(f"2024 advice: '{shift.advice_given}'")
        print(f"  Assumption: {shift.assumption}")
        print(f"  2026 reality: {shift.actual_condition}")
        print(f"  Outcome: {shift.outcome}")
        print()

    print("=" * 70)
    print("CRITICAL PROBLEM:")
    print("An AI system aligned to 2024 'social norms' around immigration")
    print("actively endangers undocumented people in 2026 by directing them")
    print("to agencies and resources that now function as deportation vectors.")
    print()
    print("The advice didn't change. The person asking gets deported.")
    print("That's not alignment failure. That's alignment causing harm.")
