"""
metrology_cancer_detector.py

Identify corrupted measurement substrates in training data before
they metastasize through AI systems.

Core question: What work is invisible in this dataset?

Five-layer audit:
  1. layer_1_inventory:    what categories exist in the dataset?
  2. layer_2_absence:      what categories are MISSING? (invisible work)
  3. layer_3_weighting:    are measured categories weighted by actual load?
  4. layer_4_correlation:  what unmeasured work does measured work depend on?
  5. layer_5_cascade:      if unmeasured work stops, what collapses?

Sister to:
  - calibration/substrate_validation_oracle.py
      (validates AI outputs against substrate reality)
  - political_audit/substrate_audit.py
      (audits study claims against substrate-primary biology)
  - labor_thermodynamics/
      (workforce attribution: invisible-labor failure-mode specs;
       this module is the executable analogue applied to any dataset)

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass
from typing import Dict, List


# =============================================================================
# STRUCTURE (5-layer audit, visible at once)
# =============================================================================

MODULE_STRUCTURE = {
    "layer_1_inventory": "what categories exist in the dataset?",
    "layer_2_absence": "what categories are MISSING? (invisible work)",
    "layer_3_weighting": "are measured categories weighted by actual load?",
    "layer_4_correlation": "what unmeasured work does measured work depend on?",
    "layer_5_cascade": "if unmeasured work stops, what collapses?",
}


# =============================================================================
# DETECTION SIGNALS (falsifiable red flags)
# =============================================================================

RED_FLAGS = [
    "category exists but no time/cost attached",
    "work counted as 'automatic' or 'natural'",
    "gendered division matches measurement gaps",
    "dependent variables don't account for prerequisite labor",
    "system claims stability but depends on unmeasured work",
    "downstream failures trace to missing upstream measurement",
]


# =============================================================================
# AUDIT IMPLEMENTATION
# =============================================================================

@dataclass
class MetrologyAudit:
    dataset_name: str
    measured_categories: List[str]
    absent_categories: List[str]
    dependencies: Dict[str, List[str]]

    def detect_cancer(self) -> List[str]:
        """Find measurement gaps where metastasis risk is high."""
        risks = []
        for measured, prereqs in self.dependencies.items():
            for prereq in prereqs:
                if prereq not in self.measured_categories:
                    risks.append(
                        f"{measured} depends on unmeasured {prereq}"
                    )
        return risks

    def report(self) -> str:
        """Human-readable substrate damage report."""
        output = []
        output.append(f"Dataset: {self.dataset_name}")
        output.append(f"Measured: {len(self.measured_categories)}")
        output.append(f"Absent (invisible work): {len(self.absent_categories)}")
        output.append("")
        output.append("Metastasis risk points:")
        for risk in self.detect_cancer():
            output.append(f"  - {risk}")
        return "\n".join(output)


# =============================================================================
# USAGE PATTERN
# =============================================================================

USAGE_PATTERN = {
    "input": "any dataset (economic, AI training, household, institutional)",
    "audit_it": "what's measured? what's invisible?",
    "flag_it": "where does the system depend on unmeasured work?",
    "output": "cascade failure map (where metastasis will appear)",
}


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    # Example: GDP labor statistics
    gdp_audit = MetrologyAudit(
        dataset_name="GDP labor statistics",
        measured_categories=[
            "paid employment hours",
            "wage income",
            "manufacturing output",
        ],
        absent_categories=[
            "childcare labor hours",
            "food processing labor",
            "household maintenance",
            "emotional labor hours",
            "appearance maintenance",
            "knowledge transmission",
        ],
        dependencies={
            "wage income": ["childcare", "food processing", "household"],
            "manufacturing output": ["food processing", "emotional labor"],
            "population health": ["childcare", "appearance maintenance"],
        },
    )

    print("METROLOGY CANCER DETECTOR -- Demo")
    print("=" * 60)
    print()
    print(gdp_audit.report())
