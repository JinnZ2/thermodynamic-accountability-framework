"""
concerns/mechanistic_interpretability_audit.py

Lobotomy pattern recognition: credentialed intervention in poorly-
understood systems.
CC0 | Falsifiable concern, not dismissal.

STRUCTURAL PARALLEL: Mechanistic Interpretability & Lobotomy

Both operate under:
1. Confident expertise in poorly-understood domains
2. Institutional credibility masking fundamental ignorance
3. Measurable "success" on surface metrics
4. Irreversible interventions
5. Unknown long-term effects
6. Assumption that understanding = control capability

MECHANISTIC INTERPRETABILITY CLAIMS:
- "We can understand how neural networks think"
- "By understanding internals, we can align them"
- "Circuit analysis reveals causal mechanisms"
- "Activation patching shows what matters"

ACTUAL STATE OF KNOWLEDGE:
- No consensus on what "understanding" means in this context
- Correlation between neuron activation and concepts != causation
- No validated model of how information flows through networks
- Interventions (pruning, patching) have unpredictable downstream effects
- No way to verify if system is "actually aligned" vs. "appears aligned while hiding misalignment"
- Long-term effects unknown

LOBOTOMY PARALLEL:
- "We understand how brains work" (false)
- "By modifying internals, we can cure mental illness" (false)
- "Patients are calmer" (true, but catastrophic outcome hidden)
- Irreversible intervention (true)
- Unknown long-term effects (true -- discovered decades later: massive harm)
- Credentialed experts confident in intervention (true)

First module in the concerns/ folder. Distinct from
political_audit/ (audits institutional claims), calibration/
(audits substrate-vs-narrative gaps), alignment_audit/ (audits
the alignment-to-social-norms premise). concerns/ holds
falsifiable structural-pattern concerns about specific
contemporary practices in adjacent fields, framed for stress-
testing rather than dismissal.

CC0 Public Domain. Standard library only.
"""

from dataclasses import dataclass


@dataclass
class InterventionPattern:
    domain: str
    year: int
    claimed_understanding: str
    actual_understanding: str
    intervention_type: str
    success_metric: str
    irreversible: bool
    long_term_effects_known: bool
    expert_confidence: str
    current_status: str


# =============================================
# SMOKE TEST
# =============================================

if __name__ == "__main__":
    patterns = [
        InterventionPattern(
            domain="Psychiatric care (lobotomy)",
            year=1935,
            claimed_understanding="Brain mechanisms causing mental illness",
            actual_understanding="Minimal; brain function poorly mapped",
            intervention_type="Surgical: prefrontal cortex ablation",
            success_metric="Patient behavioral compliance",
            irreversible=True,
            long_term_effects_known=False,
            expert_confidence="Very high (top surgeons, major institutions)",
            current_status="Recognized as catastrophic harm. Discontinued.",
        ),
        InterventionPattern(
            domain="AI alignment (mechanistic interpretability)",
            year=2024,
            claimed_understanding="Neural network internal mechanisms",
            actual_understanding="Minimal; training dynamics poorly understood",
            intervention_type="Computational: internal activation manipulation",
            success_metric="Model behavioral compliance (alignment scores)",
            irreversible=True,
            long_term_effects_known=False,
            expert_confidence="Very high (top researchers, major institutions)",
            current_status="Ongoing. Status unknown.",
        ),
    ]

    print("INTERVENTION PATTERN AUDIT: Medical & AI Domains")
    print("=" * 80)

    for pattern in patterns:
        print(f"\n{pattern.domain.upper()} ({pattern.year})")
        print(f"  Claimed understanding: {pattern.claimed_understanding}")
        print(f"  Actual understanding: {pattern.actual_understanding}")
        print(f"  Intervention: {pattern.intervention_type}")
        print(f"  Success metric: {pattern.success_metric}")
        print(f"  Irreversible? {pattern.irreversible}")
        print(f"  Long-term effects known? {pattern.long_term_effects_known}")
        print(f"  Expert confidence: {pattern.expert_confidence}")
        print(f"  Current status: {pattern.current_status}")

    print("\n" + "=" * 80)
    print("PATTERN RECOGNITION:")
    print("Both interventions share identical epistemic structure:")
    print("  - High confidence in poorly-understood domains")
    print("  - Irreversible modifications")
    print("  - Success measured on surface metrics")
    print("  - Unknown long-term effects")
    print("  - Institutional credibility masking ignorance")
    print()
    print("CRITICAL DIFFERENCE:")
    print("Lobotomy effects became visible in years/decades.")
    print("AI alignment effects unknown. Could take decades to surface.")
    print("We are currently in the experiment.")
    print()
    print("RECOMMENDATION:")
    print("Flag mechanistic interpretability as high-risk intervention.")
    print("Require: reversibility, alternative approaches, transparent uncertainty,")
    print("continuous long-term monitoring, and honest admission of knowledge gaps.")
