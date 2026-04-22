# Thermodynamic Accountability Framework: Liability Routing and Pre-Emptive Causal Exclusion

**Author:** Manus AI  
**Framework Family:** Thermodynamic Accountability Framework (TAF)  
**Date:** April 2026  
**Status:** Formal theory document — companion to `simulations/liability_routing_sim.py`

---

## Abstract

This document formalizes the mechanisms by which institutional liability is degraded, routed, and ultimately excluded from legal reality. Drawing on the node-edge model developed in `ToWorkOn.md`, it derives the core equations governing attribution clarity, enforcement instability, and schema decoupling, then demonstrates each mechanism through simulation. The central finding is that artificial intelligence does not create a "liability sink" — it creates a **reflection boundary** that routes liability upstream while simultaneously degrading the attribution clarity required for any enforcement to occur. The attractor state of a system subject to these dynamics is a self-consistent representational system that maintains procedural legitimacy while processing an ever-narrowing slice of actual harm.

---

## 1. Introduction

The Thermodynamic Accountability Framework (TAF) evaluates institutional systems by stripping away cultural narratives and replacing them with rigorous energy accounting. The question is always the same: does the energy math close? In the domain of legal and institutional accountability, the analogous question is whether the attribution math closes — whether the causal chain from a harmful event to a resolved penalty can be completed before the system's resolution capacity is overwhelmed.

This document addresses a specific failure mode: the systematic degradation of that causal chain through corporate structure, AI deployment, and schema design. It proceeds in four parts, each corresponding to one of the four simulation panels in `liability_routing_sim.py`.

---

## 2. The Liability Equation

The foundational equation of liability realization within the TAF is:

> **Liability Realized $\propto$ Q × Eₐ × X − Z**

Where each variable represents a measurable property of the enforcement graph:

| Variable | Name | Definition | Direction Under AI |
|---|---|---|---|
| **Q** | Attribution Clarity | Degree to which an event is traceable to a specific decision | $\downarrow$ rapidly |
| **Eₐ** | Enforcement Accessibility | Ability of an institutional node to reach and penalize the acting node | $\downarrow$ or stagnant |
| **X** | Event Surface Area | Scale and frequency of deployed actions | $\uparrow\uparrow$ |
| **Z** | Shielding | Legal, insurance, and jurisdictional barriers protecting the node | $\uparrow$ |

The corporate form has long optimized this function by lowering Q through diffuse decision-making, increasing Z through subsidiary walls and insurance layers, and relocating X to nodes with low Eₐ. What AI adds is Q degradation at machine speed and X scaling at deployment velocity — a combination that pushes the numerator toward zero while the denominator grows without bound.

### 2.1 The Routing Correction

A common framing error is to describe high-Z nodes as "liability sinks" — places where liability is absorbed and disappears. This is incorrect. Liability is not absorbed; it is **routed along paths of least enforceability**. The corporate advantage is not a sponge. It is a switchboard.

When attribution fails at a target node (Q → 0), liability reflects and propagates upstream to the nearest structurally enforceable ancestor node. Each bounce in this reflection cascade consumes institutional resolution capacity (R), adds latency, and increases legal costs, ultimately diluting the liability across the enforcement graph until it lands as a socialized cost on the public node. The liability does not disappear. It is distributed, delayed, and diluted.

---

## 3. Simulation Panel 1 — Liability Routing Through the Deployment Graph

The routing simulation models a standard AI deployment graph with seven nodes ordered from event origin to final socialized cost. Each node is characterized by its Q, Eₐ, Z, and R values. Unresolved liability propagates downstream at each step.

**Key result:** Starting from 100 liability units, the AI System node (Q=0.05, Z=0.90) resolves only 5 units and reflects 95. By the time the chain reaches the Regulator, only 20 units remain, of which 18 are resolved. The final 2 units land on the public as socialized cost. The total reflection across all nodes is 307 units — meaning each unit of liability bounces an average of three times before resolution. This is the reflection cascade in quantitative form.

The routing trace makes visible what is otherwise invisible: the AI node is not a terminal. It is the first reflection boundary in a chain of deflections.

---

## 4. Q Degradation Over Time

Attribution clarity Q is not a fixed property of a system. It degrades over time as organizational complexity, AI deployment, and jurisdictional fragmentation accumulate. The simulation models two degradation regimes:

**Corporate Q (procedural decay):** Degrades slowly through organizational complexity, slow deliberation, and distributed signatures. The process has friction. It takes time.

**AI-driven Q (computational decay):** Degrades rapidly through training data opacity, stochastic outputs, multi-agent interaction, and continuous deployment. The process has no friction. It operates at machine speed.

**Key result:** Under the simulation parameters, AI-driven Q reaches near-zero (≤0.05) at operational cycle 14, while corporate Q continues its slower decline. Once Q → 0, the liability equation produces near-zero realized liability regardless of the scale of harm (X) or the accessibility of enforcement (Eₐ). The mechanism is not evasion. It is the mathematical consequence of attribution diffusion.

---

## 5. The Instability Threshold

The system becomes unstable when attribution demand exceeds enforcement supply:

> **Instability Threshold:** $\frac{F}{Q} > R \times E_a$

Where F is event frequency (driven by AI deployment velocity), Q is attribution clarity (degrading), R is institutional resolution capacity (stagnant or declining under overload), and Eₐ is enforcement accessibility (fragmented across jurisdictions).

The threshold is crossed not when any single variable fails, but when the ratio of demand to supply exceeds 1. Once crossed, the institutional node enters permanent backlog. Liability enforcement becomes purely stochastic — enforced only when randomly sampled, not systematically.

**Key result:** The simulation crosses the instability threshold at cycle 11. At that point, F/Q = 9.19 and R×Eₐ = 8.40. After the crossing, the enforcement deficit grows exponentially as F continues to rise and Q continues to fall. By cycle 60, the system is operating at a demand-to-supply ratio several orders of magnitude above the threshold. The failure sequence follows four observable stages:

| Stage | Mechanism | Observable Signal |
|---|---|---|
| Attribution Compression | Q collapses faster than institutional adaptation | Courts cannot determine "who decided" |
| Enforcement Backlog | R saturates | Regulatory dockets grow faster than resolution rate |
| Jurisdictional Inconsistency | Eₐ fragmentation dominates | Forum shopping becomes primary defense strategy |
| Legal Category Revision | Doctrine adapts to new equilibrium | Personhood, strict liability, or novel entity forms emerge |

Only at Stage 4 does "AI personhood" become a live legal question. By then, the system has already functionally adapted to the enforcement deficit through informal mechanisms: de facto immunity, regulatory forbearance, settlement as default, and insurance market withdrawal.

---

## 6. Pre-Emptive Causal Exclusion

The most consequential shift in institutional accountability occurs when representation constraints determine not only how events are interpreted but which causal structures are allowed to enter the legal system at all. This is the transition from a post-hoc descriptive schema to a pre-emptive generative schema.

| Regime | Flow | Property |
|---|---|---|
| **Post-Hoc Schema (Descriptive)** | Event → Evidence → Schema → Interpretation | Reality mapping happens after the event; Q exists prior to filtering |
| **Pre-Emptive Schema (Generative)** | Schema → Allowed Event Space → Compatible Evidence → Adjudication | Schema defines what counts as a valid event; non-compatible structures never become legally real |

The threshold is crossed when representation constraints are applied **before** evidence enters the system, not after. At that point, the legal system no longer merely filters reality — it defines the subset of reality that can be processed as legally existent.

Pre-emptive exclusion is not metaphysical absence. It is operational exclusion implemented through required data schemas, evidentiary admissibility rules, logging constraints, and model interfaces. Exclusion is not a decision. It is a compatibility condition on representability.

### 6.1 The Partition of Q

Under pre-emptive exclusion, Q splits into two components:

- **$Q_{phys}$:** Physical causality — the causal structure that exists in the world.
- **$Q_{leg}$:** Legally representable causality — the subset of $Q_{phys}$ that is schema-compatible.

The reality decoupling function D(t) controls the covariance between these two quantities. When coupling is high, the legal system tracks physical reality. When coupling is low, the legal system evolves independently of reality.

### 6.2 Why Scaling Does Not Restore Lost Q

Under a post-hoc schema, more computational power can expand representational boundaries through novel arguments. Under a pre-emptive schema, more computational power only processes more schema-compatible cases. Schema-incompatible cases never enter the queue. AI legal systems do not "see more reality" — they only process what the schema permits to exist as input. Scaling expands throughput within an already constrained representational space. It does not expand the space itself.

---

## 7. Simulation Panel 4 — Schema Evolution and Reality Decoupling D(t)

The schema evolution simulation models the dynamics of $\Delta Schema(t)$ under the full constraint system:

> $\Delta Schema(t) = f\bigl(D(t) \cdot \{litigation,\ admin\_feedback\},\ S,\ infrastructure\bigr)$

Where D(t) is a correlation breakdown operator (not a scalar weight), S is structural alignment (corporate/state capture), and infrastructure represents technical implementation constraints.

**Key result:** Over 80 schema update cycles, schema breadth declines from 0.80 to 0.41, coupling declines from 0.90 to 0.27, and the gap between $Q_{phys}$ (0.745) and $Q_{leg}$ (0.081) reaches 0.664. This means that by the end of the simulation, **89.2% of physical causality is legally non-representable**. The system is not broken. It is functioning exactly as its optimization surface demands — minimizing representational complexity while maintaining procedural legitimacy.

The three forces driving this outcome are asymmetric:

- **Litigation pressure** (expansion from below): slow, requires adversarial proof and institutional bandwidth, gated by D(t).
- **Structural alignment S** (shaping from above): continuous, operates through vendor ecosystems, procurement, and standards bodies.
- **Administrative compression** (contraction from within): optimizes for throughput, not completeness.

Contraction of representational space is cheaper and faster than expansion. This creates a directional bias in long-run schema evolution.

---

## 8. The Full Arc

The model traces a complete causal arc from metaphysics to institutional anatomy:

| Stage | Shift |
|---|---|
| Metaphysics | Personhood debate is misdirection |
| Corporate Structure | Q degradation via obfuscation and fragmentation |
| Enforcement Gradients | A(t) shaped by S; procedural cost prices out enforcement |
| Representational Grammar | Bottleneck shifts from throughput to schema |
| Institutional Anatomy | Five-layer constraint stack defines schema |
| Pre-Emptive Exclusion | Schema defines legal reality itself |
| Infrastructure Dominance | $\Delta Schema(t)$ driven by vendors, not law |
| Decoupling | D(t) breaks mapping between physical and legal reality |
| Self-Referential Evolution | System maintains coherence while losing correspondence |

The terminal implication is this: a self-consistent representational system can be internally coherent, procedurally legitimate, computationally efficient, and completely decoupled from physical reality. Legitimacy no longer requires correspondence. It requires consistency. The schema does not describe reality. The schema **replaces** reality for all legally operative purposes.

---

## 9. Structural Intervention Space

Given this model, effective interventions must target edge properties in the enforcement graph, not node definitions. The following table maps intervention targets to mechanisms and effects:

| Intervention Target | Mechanism | Effect |
|---|---|---|
| Q (Attribution Clarity) | Mandate model lineage tracking, decision provenance logs | Increase Q for AI-driven actions |
| Eₐ (Enforcement Accessibility) | Require domestic asset anchoring for AI deployments | Prevent Eₐ → 0 routing |
| Z (Shielding) | Pierce AI veil by statute: treat AI actions as per se acts of deploying entity | Eliminate Z benefit of AI intermediary |
| Resolution Cycle Time | Pre-clearance regimes, real-time oversight APIs | Reduce I node latency |
| Schema Breadth | Mandate representational completeness audits | Prevent pre-emptive exclusion drift |

The most structurally elegant intervention is **statutory attribution coupling**: any action taken by or through an AI system is legally attributed to the highest-Q, highest-Eₐ node in the deployment chain, with joint and several liability. This inverts the optimization function. Instead of routing liability to the lowest-Q node, the structure routes it to the highest-Q node — the human or corporate principal with assets and enforceability.

---

## 10. Simulation Usage

The companion simulation `simulations/liability_routing_sim.py` implements all four mechanisms described in this document. It requires only `numpy` and `matplotlib`.

```bash
# Run from the repository root
python3 simulations/liability_routing_sim.py
```

The simulation produces a four-panel figure (`liability_routing_sim.png`) and a structured text report. All parameters are exposed as function arguments and can be modified to explore different scenarios:

- `build_standard_graph(ai_Q=...)` — vary the AI node's attribution clarity.
- `q_degradation_curve(corporate_decay_rate=..., ai_decay_rate=...)` — vary degradation speeds.
- `instability_threshold_sim(F0=..., F_growth=..., Q0=..., Q_decay=...)` — vary enforcement dynamics.
- `schema_evolution_sim(initial_state=SchemaState(S=..., infra=...))` — vary structural alignment and infrastructure lock-in.

---

## References

[1] ToWorkOn.md, Thermodynamic Accountability Framework Repository. JinnZ2, 2026.  
[2] `docs/theory/functional_epistemology_framework.md` — Core TAF axioms and energy accounting model.  
[3] `docs/theory/egs_core.md` — Entropy Governance System: seven failure modes and anti-gaming mechanisms.  
[4] `docs/theory/lhri.md` — Longitudinal Human Resilience Index: multi-horizon cost function.  
[5] `labor_thermodynamics/core/attribution_sim.py` — Attribution laundering simulation (facility model).
