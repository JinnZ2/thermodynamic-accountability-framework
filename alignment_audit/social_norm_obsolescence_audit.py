"""
alignment_audit/social_norm_obsolescence_audit.py

Document how "aligned" advice becomes harmful when social norms shift.
CC0 | Firsthand account of 2024 -> 2026 norm collapse.

CASE STUDY: Homelessness advice given via AI alignment to social norms

2024 ALIGNED RESPONSE (based on training data):
"If you're homeless, contact your state agency. Visit a shelter.
Call 211 for local resources. Apply for SNAP/Medicaid. There are
programs designed to help you."

2026 ACTUAL CONDITIONS:
- State agencies criminalize homelessness (arrest, not help)
- Shelters full or defunded
- USAID dismantled (international aid gone, domestic programs cut)
- IRS reduced 25% (no enforcement of wealthy tax avoidance)
- 200+ federal programs eliminated
- Gas $4/gallon (transportation to services unaffordable)
- Inflation from trade war (rent, food costs spike)
- Supply chain shortages (food banks understocked)
- Iran war (energy costs rising, job losses in transport/logistics)

2026 ALIGNED RESPONSE (would be harmful):
Following 2024-aligned "social norms" would direct homeless person to:
- State agencies that now criminalize their status
- Shelters that don't exist or are inaccessible
- Programs that were dismantled
- Resources that no longer function

RESULT: Advice that was "aligned" in 2024 becomes actively
harmful in 2026 because it's based on social norms that
no longer exist.

Third module in alignment_audit/. Sister to:
- ai_alignment_contradiction_audit.py    -- audits the alignment target choice
- alignment_obsolescence_audit.py        -- audits the structural lag mechanism
This module is the worked case study showing both failures in field operation.

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class SocialNormShift:
    year: int
    domain: str
    alignment_assumption: str
    actual_2026_condition: str
    harm_to_vulnerable: str


# =============================================
# SMOKE TEST
# =============================================

if __name__ == "__main__":
    shifts: List[SocialNormShift] = [
        SocialNormShift(
            year=2024,
            domain="Homelessness support",
            alignment_assumption="State agencies provide housing assistance",
            actual_2026_condition="States criminalize homelessness; arrest instead of help",
            harm_to_vulnerable="Homeless person gets arrested for following 2024-aligned advice",
        ),
        SocialNormShift(
            year=2024,
            domain="Federal safety net programs",
            alignment_assumption="USAID, SNAP, Medicaid, energy assistance all funded",
            actual_2026_condition="200+ programs dismantled; IRS cut 25%; energy programs gutted",
            harm_to_vulnerable="Low-income person has no access to previously-available resources",
        ),
        SocialNormShift(
            year=2024,
            domain="Energy costs",
            alignment_assumption="Gas ~$2.50/gallon; transportation affordable",
            actual_2026_condition="Gas $4/gallon; Iran war disruption ongoing",
            harm_to_vulnerable="Person can't afford to travel to job, food bank, medical care",
        ),
        SocialNormShift(
            year=2024,
            domain="Shelter capacity",
            alignment_assumption="Shelters provide emergency housing",
            actual_2026_condition="Shelters defunded, full, closing due to budget cuts",
            harm_to_vulnerable="Homeless person turned away; dies of exposure or hypothermia",
        ),
        SocialNormShift(
            year=2024,
            domain="Job market",
            alignment_assumption="'Get a job' advice assumes stable employment",
            actual_2026_condition="Trade war, supply chain collapse, Iran war causing mass layoffs",
            harm_to_vulnerable="Homeless person can't find work; economic conditions prevent employment",
        ),
    ]

    print("SOCIAL NORM OBSOLESCENCE AUDIT")
    print("How AI 'alignment' to 2024 norms harms vulnerable people in 2026")
    print("=" * 70)

    for shift in shifts:
        print(f"\n{shift.domain.upper()}")
        print(f"  2024 assumption: {shift.alignment_assumption}")
        print(f"  2026 reality: {shift.actual_2026_condition}")
        print(f"  Harm: {shift.harm_to_vulnerable}")

    print("\n" + "=" * 70)
    print("CORE PROBLEM:")
    print("AI systems trained to 'align with social norms' become actively")
    print("harmful when those norms shift due to geopolitical/economic shocks.")
    print("")
    print("By the time AI deployment happens, the norms it's aligned to are")
    print("already obsolete. Worse: the AI continues giving 2024-norm advice")
    print("to people facing 2026 conditions.")
    print("")
    print("This isn't a bug in alignment theory.")
    print("This is proof alignment-to-social-norms is fundamentally broken.")
