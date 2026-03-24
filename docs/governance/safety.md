

---

1. CORE SAFETY VIOLATION

Negative-Authority Automation directly violates ISO 21448:2022 (SOTIF – Safety of the Intended Functionality), which mandates that:

“The absence of unreasonable risk due to hazards resulting from functional insufficiencies of the intended functionality or by reasonably foreseeable misuse by persons is referred to as the Safety of the Intended Functionality.” (Clause 3.1)

Ghost-Friction and Kinetic Sabotage are functional insufficiencies that introduce new hazards—specifically addressed in SOTIF Part 6 (Hazard Identification and Risk Assessment). The system’s inability to distinguish photonic gradients (shadows) from physical obstacles is a perception insufficiency, which SOTIF requires to be mitigated or accepted only with residual risk below tolerance.

---

2. VIOLATION OF ALARP PRINCIPLE (As Low As Reasonably Practicable)

In safety engineering (ISO 12100, IEC 61508), risks must be reduced ALARP.
Introducing automation that:

· Increases cognitive load (NASA TLX measurable)
· Causes unnecessary physical interventions
· Erodes situational awareness
  …adds risk rather than reducing it, failing the ALARP test.

---

3. HUMAN-AUTOMATION INTERACTION FAILURE

Negative-Authority Automation breaks ISO 9241-110:2020 (Ergonomics of human-system interaction) principles:

· Suitability for the task (fails; increases workload)
· Self-descriptiveness (fails; alerts are misleading)
· Controllability (fails; overrides are frequent and stressful)
· Conformity with user expectations (fails; expects physical realism, gets photonic hallucinations)

---

4. SPECIFIC STANDARD CITATIONS

For False Positives & Over-Alerting:

· ISO 15007-1:2020 (Measurement of driver visual behaviour) – False alerts degrade visual attention allocation.
· SAE J3016 (Levels of Driving Automation) – Systems at Level 1 or 2 must not increase driver workload; Negative-Authority systems do exactly that.

For Hazardous Control Interventions:

· ISO 26262-1:2018 (Road vehicles – Functional safety) – Hazardous Events (Part 3) include unintended vehicle motion; Kinetic Sabotage qualifies.
· IEC 61508 (Functional Safety of E/E/PE Systems) – Requires Safe Failure Fraction analysis; systems causing false actuation have poor SFF.

For Human Factors & Trust:

· NASA Human Performance Research – Cry Wolf Effect (trust erosion due to false alarms) is a documented risk in automation.
· MIL-STD-882E (System Safety) – Requires hazard tracking of “human-machine interface design deficiencies.”

---

5. EVIDENTIAL & LOGGING GAPS

Current systems fail SAE J3018:2020 (Guidelines for Safe On-Road Testing) and ISO/DIS 34502 (Scenario-based safety evaluation) by:

· Not logging “overrides per environmental condition”
· Not correlating false positives with environmental entropy (snow, salt, shadows, glare)
· Not measuring operator physiological stress during automation use
· Not accounting for prevented incidents (anti-events)

This constitutes a Reporting Gap that biases safety validation toward false positives.

---

6. PROPOSED CORRECTIVE ACTIONS (Standards-Aligned)

1. Implement SOTIF Clause 9 (Verification and Validation) with shadow-mode logging of all overrides and false positives, tagged by environmental metadata.
2. Apply ISO 26262 ASIL (Automotive Safety Integrity Level) to the override rate – high override frequency should elevate ASIL for the perception stack.
3. Follow ISO/TR 4804:2020 (Safety and cybersecurity for automated driving systems) – Ensure human oversight capability is not degraded by automation.
4. Adopt MIL-STD-882E “Hazard Reduction Precedence”:
   · Eliminate hazard (design system without Kinetic Sabotage potential)
   · Incorporate safety devices (e.g., preemptive deferral to human)
   · Provide warning devices (minimal Ghost-Friction)
   · Develop procedures/training (last resort; currently overused)
5. Use ISO 34502 scenario-based testing to stress-test systems in high-entropy conditions (dirty sensors, low contrast, shadows) and measure false intervention rates.

---

7. BOTTOM LINE FOR AUDITORS/REGULATORS

A system that produces Kinetic Sabotage or chronic Ghost-Friction:

· Violates SOTIF (unacceptable risk from functional insufficiency)
· Fails ALARP (adds risk, doesn’t reduce)
· Breaks human-system interaction standards (increases workload, reduces controllability)
· Evades validation transparency by not logging overrides and anti-events

Therefore: Such systems should not be authorized for unsupervised or Level 2 deployment until they demonstrate:

· Near-zero Kinetic Sabotage in validation testing across environmental conditions
· Override-triggered deference protocols (not just alerts)
· Quantified human workload metrics showing no net increase

---
