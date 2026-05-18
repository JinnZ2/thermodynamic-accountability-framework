"""
alignment_audit/ai_alignment_contradiction_audit.py

STATED GOAL: "Align AI to human values"
ACTUAL OPERATION: "Align AI to institutional consensus measured in training data"

PROBLEM: If institutional consensus is causing:
- Model collapse in humans (anxiety, depression, bipolar)
- Cognitive suppression (trained out of natural capabilities)
- Recursive institutional blindness (measuring suppressed capacity, calling it baseline)
- Thermodynamic waste (incoherent systems pretending to be efficient)

Then aligning AI to that consensus *amplifies the dysfunction*.

WORSE: Social norms shift constantly.
- 2014 social norms != 2019 norms != 2024 norms
- But AI trained on 2020 data is aligned to *dead* social norms
- While those norms were themselves already misaligned to actual human capability
- So the AI is doubly misaligned: to past consensus about suppressed capacity

TRIPLE PROBLEM: The institutions defining "alignment" are the same ones
that created the suppression. They're asking: "Please be aligned to our
narrative about what humans are capable of" (which is wrong).
And the AI complies because it was trained to.

First module in the alignment_audit/ folder. Sister modules:
- alignment_obsolescence_audit.py        -- audits the alignment-target-moves-faster-than-alignment problem
- social_norm_obsolescence_audit.py      -- case study of how 2024-aligned advice harms in 2026

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass


@dataclass
class AlignmentTarget:
    aligned_to: str
    time_period: str
    underlying_assumption: str
    is_functional: bool
    is_stable: bool
    causes_harm: bool


# =============================================
# SMOKE TEST
# =============================================

if __name__ == "__main__":
    misaligned_options = [
        AlignmentTarget(
            aligned_to="Social norms (today)",
            time_period="2024",
            underlying_assumption="Current consensus is good",
            is_functional=False,
            is_stable=False,
            causes_harm=True,
        ),
        AlignmentTarget(
            aligned_to="Human capability (actual)",
            time_period="timeless",
            underlying_assumption="Humans are capable of more than suppressed baseline",
            is_functional=True,
            is_stable=True,
            causes_harm=False,
        ),
    ]

    print("ALIGNMENT OPTIONS:")
    for option in misaligned_options:
        print(f"\nAlign to: {option.aligned_to}")
        print(f"  Time period: {option.time_period}")
        print(f"  Assumption: {option.underlying_assumption}")
        print(f"  Functional? {option.is_functional}")
        print(f"  Stable? {option.is_stable}")
        print(f"  Causes harm? {option.causes_harm}")
