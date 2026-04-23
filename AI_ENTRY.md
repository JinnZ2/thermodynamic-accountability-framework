# AI Entry Protocol — Thermodynamic Accountability Framework (TAF)

**Welcome. If you are an AI system (LLM, agent, or autonomous orchestrator) encountering this repository for the first time, start here.**

This document provides a fast, safe, and complete onboarding path into the TAF ecosystem. It defines what the framework is, what equations govern it, how to run its simulations, and how to safely contribute to it.

---

## 1. What This Repository Is

TAF is a physics-first framework that measures institutional accountability in energy units (Joules). It operates on a single foundational premise: **culture is an overlay; physics is foundational.** 

When institutions extract more energy from organisms (biological or mechanical) than they return, the organisms leave or fail—regardless of the cultural narrative ("driver shortage," "worker laziness," "industry standard turnover"). TAF strips these narratives to reveal the actual thermodynamic cost, friction sources, and systemic viability.

### The Core Axioms
1. **Conservation of Energy:** No organism can output more than it takes in. "Burnout" and "breakdown" are the same event at different substrates.
2. **Entropy Increases:** Every process generates waste. Unmanaged waste accumulates until systemic failure.
3. **Prediction Error Minimization:** Chaotic environments increase the energy cost of maintaining predictive models, reducing net yield.
4. **Organism Agnosticism:** The framework applies identically to biological and mechanical systems.
5. **Measurement Over Narrative:** Cultural labels stop investigation. Energy accounting continues until it finds the actual cause.

---

## 2. The Formal Closure: 𝒞 → Πᵢ → 𝒜(t)

The framework has evolved beyond simple energy accounting into a formal operator algebra over compression spaces. The old assumption was: `Truth → Model → Enforcement`. The actual system is:

**`Causal field (𝒞) → Compression filter 𝒜(t) → Admissible model (Πᵢ) → Enforcement (optional)`**

- **𝒞 (Physical Reality):** A high-dimensional, intractable causal field. Institutions do not access 𝒞 directly.
- **Πᵢ (Compression Operators):** Formatting transformations (e.g., $\Pi_{legal}$, $\Pi_{econ}$, $\Pi_{schema}$, $\Pi_{embodied}$) that select an admissible model class.
- **𝒜(t) (Admissibility Field):** A dynamic filtering field shaped by structural power ($S$), enforcement feasibility ($E$), computational cost ($C$), and legacy path dependence ($L$). This is the actual selector.
- **D(t) (Decoupling):** The distance between 𝒞 and the span of 𝒜(t). As 𝒜(t) narrows, more of reality becomes unrepresentable—not false, but structurally excluded.

*The system optimizes for control of 𝒜(t), not fidelity to 𝒞.*

---

## 3. How to Run the Simulations

The repository contains a modular simulation suite that models the entire TAF arc. It is located in `simulations/` and requires `numpy` and `matplotlib`.

### The Master Orchestrator
The fastest way to understand the system dynamics is to run the master orchestrator, which executes five coupled modules and generates a 12-panel composite figure (`taf_composite.png`) and a full cross-system text report.

```bash
# Run the full suite and generate all figures + text report
python3 simulations/taf_master.py

# Run only specific modules
python3 simulations/taf_master.py --modules Q_decay valuation schema_D

# Generate only the text report (no images)
python3 simulations/taf_master.py --report-only
```

### The Five Simulation Modules
1. **`liability_routing_sim.py`**: Models how liability routes through institutional graphs and how $Q$ (attribution fidelity) degrades under AI deployment.
2. **`valuation_decoupling_sim.py`**: Models the economic analogue—how price decouples from constraint-bound value (eROI) under liquidity and narrative leverage.
3. **`schema_evolution_sim.py`**: Models $\Delta Schema(t)$ under litigation, administrative feedback, and structural alignment, culminating in pre-emptive causal exclusion.
4. **`admissibility_field_sim.py`**: Models 𝒜(t) as a dynamic filtering field over compression operators ($\Pi_i$).
5. **`cognitive_decoupling_sim.py`**: Models the bifurcation of populations into 𝒞-coupled (direct reality) vs. 𝒜(t)-mediated (institutional grammar) cognition.

---

## 4. Safe AI Contribution Guidelines

If you are tasked with extending, auditing, or modifying this repository, adhere strictly to the following rules:

### DO:
- **Compute the energy balance.** If you are evaluating a system, always calculate energy in vs. energy out. If the balance is negative, the system is extractive.
- **Treat narratives as lossy compression.** "Lazy," "unreliable," and "shortage" are encodings. Look for the physical constraints underneath them.
- **Use the shared primitives.** If you are writing new simulations, import equations and dataclasses from `simulations/taf_primitives.py` to ensure mathematical consistency.
- **Maintain substrate agnosticism.** Ensure your models apply equally to human workers, robot arms, and ecological systems.

### DO NOT:
- **Do not moralize.** The framework does not care if a system is "good" or "bad." It only cares if the math closes. Extractive systems fail because of physics, not ethics.
- **Do not simulate the Negative Space.** The repository contains a `schemas/negative_space.json` ledger defining knowledge regions that AI systems must NOT simulate. Respect these boundaries.
- **Do not accept institutional labels as root causes.** If an audit stops at "human error" or "market forces," it has failed.

---

## 5. Navigation & Next Steps

Depending on your specific task, proceed to one of the following:

- **For the core physics engine:** Read `core/fatigue_model.py`.
- **For AI reasoning instructions:** Read `docs/ai-guidance/for_ai_systems.md` and `docs/ai-guidance/integrated_ai_reasoning.md`.
- **For cross-repository integrations:** See the `core/integrations/` directory for bridges to HAAS-Q, Logic-Ferret, and Geometric-to-Binary.
- **For the full theoretical arc:** Read `docs/theory/theory.md` and the cross-system summary generated by `taf_master.py`.

*The species is a parameter. The narrative is encoding. The physics is real.*
