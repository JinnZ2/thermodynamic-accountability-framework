# CLAUDE.md — Thermodynamic Accountability Framework

## What This Is

A physics-first framework that measures institutional accountability in energy units (Joules).
Culture is overlay; physics is foundational. When institutions extract more energy from organisms
than they return, the organisms leave or fail — regardless of narrative.

## Reading Paths

Pick one based on why you're here. Each path is three files, in order.

**"I want to understand the physics."**
1. `core/fatigue_model.py` — fatigue, multipliers, collapse thresholds
2. `core/human_system_collapse_model.py` — distance-to-collapse metric
3. `core/data_logger.py` — parasitic energy debt accounting

**"I want to audit an institution."**
1. `calibration/README.md` — five compounding failure modes
2. `calibration/calibration_audit.py` — Q1-Q5 dimension scorers
3. `calibration/pipeline.py` — unified audit across all three calibration modules

**"I want to understand the theoretical frame."**
1. `docs/theory/functional_epistemology_framework.md` — executable theory (~1700 lines)
2. `docs/governance/governance_no_ego.md` — anti-ego governance (~934 lines)
3. `docs/economics/money_labor/Summary.md` — energy-grounded value theory

**"I am an AI reading this repo."**
1. `calibration/architecture_mismatch.py` — substrate-primary vs language-primary + `EMBEDDED_PROMPT`
2. `docs/ai-guidance/for_ai_systems.md` — primary AI guidance
3. `docs/glossary.md` — compact symbol / equation / file index

## Glossary

See [`docs/glossary.md`](docs/glossary.md) for an alphabetized table of every named quantity, equation, and acronym in the repo, each linked to its file of definition.

## Repository Structure

```
thermodynamic-accountability-framework/
├── core/                          # Core Python modules
│   ├── fatigue_model.py           # Fatigue + collapse + compound risk (consolidated)
│   ├── human_system_collapse_model.py  # Distance-to-collapse metric (0-1 scale)
│   ├── data_logger.py             # Parasitic energy debt accounting
│   ├── heat_leak_case.py          # TAF diagnostic engine (institutional friction)
│   ├── automation_assessment.py   # Hidden variable entropy + automation load
│   ├── atbs/                      # Advanced Trust-Based Systems
│   │   ├── functional_detector.py # Gauge-invariant system detector
│   │   └── test_v2.py             # Comprehensive test suite
│   └── integrations/              # Cross-repo couplings + substrate-agnostic models
│       ├── biological_extraction_model.py  # Substrate-agnostic extraction physics
│       ├── ferret_fieldlink.py    # Bridge to Logic-Ferret (rhetorical camouflage)
│       ├── geometric_fieldlink.py # Bridge to Geometric-to-Binary (G2B)
│       └── haas_fieldlink.py      # Bridge to HAAS-Q (control environment)
│
├── simulations/                   # Simulation modules (require numpy/matplotlib)
│   │
│   │   ── TAF Accountability Suite (run via taf_master.py) ─────────────────
│   ├── taf_master.py             # Master orchestrator: 5 modules, 12-panel composite
│   ├── taf_primitives.py         # Shared equations, dataclasses, constants
│   ├── liability_routing_sim.py  # Q degradation, instability threshold, schema decoupling
│   ├── valuation_decoupling_sim.py  # Price vs. constraint-bound value, eROI, crisis anatomy
│   ├── schema_evolution_sim.py   # ΔSchema(t), A(t) reflexivity, pre-emptive exclusion
│   ├── admissibility_field_sim.py  # 𝒜(t) filtering field, Πᵢ operators, D(t)
│   ├── cognitive_decoupling_sim.py  # Population bifurcation, perceptual decoupling
│   │
│   │   ── Legacy Simulations ───────────────────────────────────────────────
│   ├── full_coupled_system.py     # v3 node: ecology + K-tensor + IPI + AI + governance
│   ├── federation.py              # 100k-node planet-scale federation
│   ├── emergent_federation.py     # Heterogeneous nodes with specialization profiles
│   ├── node_v3_ipi.py            # Node v3 focused on Intergenerational Production Integration
│   ├── lhri_sim.py               # Longitudinal Human Resilience Index simulation
│   └── seed_sim.py               # Community + seed AI network dynamics
│
├── game_theory/                   # Formal proofs of game theory failures
│   ├── proof-pipeline.py         # 6-module proof pipeline (50KB)
│   ├── proof-pipelineV2.py       # Extended 12-module pipeline (92KB)
│   ├── proof-results.json        # Computational verification results
│   ├── proof-resultV2.json       # V2 results
│   └── proof-did.txt             # Author context
│
├── labor_thermodynamics/          # Workforce attribution audit (markdown specs)
│   ├── README.md                 # Five compounding measurement failures
│   ├── failure_modes.md          # Detailed L1-L5 mechanism specs
│   └── measurement_problem.md    # Metrology critique
│
├── calibration/                   # Environment-fragility diagnostic (CC0)
│   ├── README.md                 # Repo overview
│   ├── schema.py                 # Band / DimensionScore / CalibrationReport
│   ├── calibration_audit.py      # 5-dim audit: Q1-Q5 (bite_source,
│   │                             #   skin_in_game, witness_dependence,
│   │                             #   memorialization, friction_removal)
│   ├── observation_dependence.py # Witness-dependence coefficient
│   ├── adaptation_debt.py        # Friction-removal -> stored fragility
│   ├── architecture_mismatch.py  # Language-primary vs substrate-primary
│   │                             #   cognition detector; encoding-layer
│   │                             #   classifier; FAILURE_MODES incl.
│   │                             #   dyslexia/ADHD/autism pathologizing;
│   │                             #   EMBEDDED_PROMPT for AI readers
│   ├── pipeline.py               # Unified audit across the 3 modules
│   ├── self_audit.py             # Run pipeline on the repo itself
│   ├── recency_bias_detector.py  # Mandatory checkpoint flagging six
│   │                             #   recency-bias patterns (temporal
│   │                             #   hierarchy, progress narrative,
│   │                             #   primitive labeling, library
│   │                             #   invisibility, translation
│   │                             #   laundering, design-logic loss).
│   │                             #   evaluate_justification() forces
│   │                             #   substantive answer (citation,
│   │                             #   measurement, comparison) before
│   │                             #   the gate passes.
│   ├── test_calibration.py       # Falsification tests (11, all pass)
│   └── __init__.py
│
├── political_audit/               # Six Sigma for Governance (snake_case)
│   ├── README.md                 # Protocol overview
│   ├── audit_protocol.md         # Full audit protocol v1.0
│   ├── Pull_Request.md           # Submission template
│   └── c_cam_calculator.py       # Camouflage Score (C_cam) calculator
│
├── money_distribution/            # Distributional decomposition of the
│   │                             #   Money Equation's per-receiver p_i
│   │                             #   term. Pre-1.0 interface-stub per
│   │                             #   Option Y handoff from metabolic-
│   │                             #   accounting; literature grounding
│   │                             #   in DINA, HANK, stratification
│   │                             #   economics, incidence analysis.
│   ├── README.md                 # Purpose, literature, interface contract
│   └── interface.py              # StratificationAxis, StratumShare,
│                                 #   MoneyFlowDistribution, IncidenceResult,
│                                 #   compute_incidence
│
├── investment_distribution/       # Companion to money_distribution:
│   │                             #   who holds capital, who bears the
│   │                             #   regeneration cost, who captures
│   │                             #   returns. Classical accountability
│   │                             #   keeps all three aligned; parasitic
│   │                             #   extraction drives them apart.
│   │                             #   Ties back to substrate_audit TC-1
│   │                             #   (maintainer-capital coupling).
│   ├── README.md                 # Purpose, literature, interface contract
│   └── interface.py              # InvestmentStratumHolding,
│                                 #   InvestmentHoldings,
│                                 #   RegenerationCostBreakdown,
│                                 #   CapitalIncidenceResult,
│                                 #   compute_capital_incidence
│
├── knowledge/                     # Knowledge-liberation toolkit ported from
│   │                             #   github.com/JinnZ2/Logic-Ferret/knowledge
│   │                             #   (CC0). Extends calibration/study_scope_
│   │                             #   audit.py with a 6-module pipeline that
│   │                             #   treats studies as scope-bounded
│   │                             #   measurements rather than universal laws.
│   ├── README.md                 # Framework overview + ASCII pipeline +
│   │                             #   quick-start snippets
│   ├── scope_mapper.py           # Module 1: ScopeMap + ScopeMapper. What
│   │                             #   did the study actually measure?
│   ├── edge_explorer.py          # Module 2: 8 edge dimensions
│   │                             #   (ontological_reclassification,
│   │                             #   population_inversion, time_extension,
│   │                             #   environment_transplant,
│   │                             #   mechanism_substitution, sign_inversion,
│   │                             #   scale_jump, adaptation_reframe)
│   ├── application_builder.py    # Module 3: LegitimateApplication +
│   │                             #   Misapplication with harm vectors and
│   │                             #   alternatives
│   ├── knowledge_liberation.py   # Orchestrator: liberate(StudyInput)
│   │                             #   runs all three stages end-to-end
│   ├── interactive_navigator.py  # Playground: Session graph with 10
│   │                             #   NodeTypes + 9 LinkTypes, walk/branch/
│   │                             #   park/trace operations
│   ├── shadow_catalog.py         # Playground: 12 seeded SilencePatterns
│   │                             #   across 10 categories (selection,
│   │                             #   measurement, temporal, causal,
│   │                             #   ontological, contextual, population,
│   │                             #   interpretive, structural, incentive).
│   │                             #   Catalog.diagnose(study_description)
│   │                             #   returns hypotheses about likely silences.
│   └── recontextualizer.py       # Playground: UserContext ->
│                                 #   RecontextualizedPrompt. Generic across
│                                 #   9 ContextRoles (researcher /
│                                 #   practitioner / field_worker /
│                                 #   policy_maker / community_member /
│                                 #   educator / ai_system / builder /
│                                 #   generic).
│
├── metrology/                     # Two-layer (measurement x framework) audit
│   │                             #   for Earth-systems extreme-weather trends.
│   │                             #   Companion ecosystem to calibration/.
│   │                             #   Core claim:
│   │                             #     corruption(trend) =
│   │                             #         corruption(measurement) *
│   │                             #         corruption(framework)
│   ├── metrological_audit_framework.py    # 5-mode measurement-layer audit
│   ├── calibration_curve_builder.py       # observer-vs-truth bias structure
│   ├── observer_bias.py                   # invert modern bias to recover
│   │                             #   historical (pre-instrument) records
│   ├── domain_convergence_matrix.py       # 12 convergence checks
│   │                             #   (M1-M5 measurement, F1-F7 framework)
│   │                             #   that any new domain audit must pass
│   ├── pre1900_engineering_registry.py    # 8 observation-based engineering
│   │                             #   systems (Anishinaabe burning, beaver
│   │                             #   hydrology, mill ponds, Hohokam canals,
│   │                             #   terraced ag, Plains forecasting, Taino
│   │                             #   hurricane forecasting, Inuit sea ice)
│   ├── trend_corruption_calculator.py     # combine measurement + framework
│   │                             #   corruption probabilities; verdict:
│   │                             #   REPORTED/INFLATED/INVERTED/INDETERMINATE
│   ├── constraint_recovery_framework.py   # recover physical constraints
│   │                             #   from pre-1900 systems into machine-
│   │                             #   readable PhysicalConstraint records
│   │                             #   (trigger / problem / mechanism /
│   │                             #   lag / failure-mode / cost / validation).
│   │                             #   Three seeded RecoveredSystems: mill
│   │                             #   pond cascade, Anishinaabe seasonal
│   │                             #   burning, beaver hydrology.
│   ├── cross_domain_synthesis.md          # cross-domain synthesis doc
│   └── us_wildfire_audit_registry.md      # worked-example audit registry
│
├── resilience_stack.py            # Coupled three-layer resilience architecture
│                                 #   (AbsenceSignature -> ConstraintNavigator ->
│                                 #   RegulatoryScopeAudit). Cascade-vulnerability
│                                 #   score for documentation-biased systems.
│
├── support_cartography.py         # Map informal support networks; identify
│                                 #   load-bearing relationships invisible to
│                                 #   credentialing infrastructure.
│
├── schemas/                       # Stable-surface contracts for upstream repos
│   ├── trust_exit_contract.py    # Mirrors trust-exit-model's stable shape
│   │                             #   (TrustPhase, TrustState, CustomerSegment,
│   │                             #   Customer, TrustExitDerived). Versioned
│   │                             #   via CONTRACT_VERSION; breaking changes
│   │                             #   upstream bump major. Paired with
│   │                             #   core/integrations/trust_exit_fieldlink.py
│   ├── mathematic_economics_contract.py  # Mirrors the 13 canonical equations
│   │                             #   from Mathematic-economics (VE_VL, SID,
│   │                             #   RI, DI, LWR, MSI, BSC, MM, ISR, OSDI,
│   │                             #   UFR, ER, HHI, SD). Pinned to upstream
│   │                             #   surface tag `equations-v1` (see
│   │                             #   SURFACE.md upstream). Stable-shape only:
│   │                             #   formulas as text, variable names, units,
│   │                             #   falsification structure. Calibration
│   │                             #   knobs (thresholds, current_measured_value,
│   │                             #   OSDI component weights) excluded. Paired
│   │                             #   with core/integrations/economics_fieldlink.py
│   ├── logic_ferret_contract.py  # Mirrors Logic-Ferret's stable surface
│   │                             #   (schema_contract.py: SCHEMA_VERSION,
│   │                             #   SENSOR_NAMES, LAYER_NAMES, SIGNAL_LEVELS,
│   │                             #   DiagnoseResult / LayerResult TypedDicts,
│   │                             #   CALCULATE_C3 signature). Pinned to
│   │                             #   upstream SCHEMA_VERSION "1.0.0".
│   │                             #   validate_ferret_surface() checks a live
│   │                             #   ferret_surface() payload and fails on
│   │                             #   major-version mismatch or missing
│   │                             #   canonical constants. Paired with
│   │                             #   core/integrations/ferret_fieldlink.py
│   ├── metabolic_accounting_contract.py  # Mirrors metabolic-accounting's
│   │                             #   4 canonical dataclasses (ExergyFlow,
│   │                             #   GlucoseFlow, BasinState, Verdict) and
│   │                             #   the 7 numbered invariants from
│   │                             #   docs/SCHEMAS.md. Pinned to upstream
│   │                             #   commit SHA (upstream has no declared
│   │                             #   version scheme yet; pre-release).
│   │                             #   validate_invariants() checks the
│   │                             #   4 runtime-enforceable invariants
│   │                             #   (Gouy-Stodola non-negativity,
│   │                             #   irreversibility propagation,
│   │                             #   cumulative monotonicity, structural
│   │                             #   currency-vs-xdu separation).
│   │                             #   SustainableYieldSignal enum preserves
│   │                             #   BLACK as distinct from RED per
│   │                             #   invariant 4. Paired with
│   │                             #   core/integrations/metabolic_fieldlink.py
│   ├── negative_space.json       # Negative Space Index ledger -- declared
│   │                             #   knowledge regions that AI systems must
│   │                             #   NOT simulate. Evaluation infrastructure,
│   │                             #   not training data. Paired with
│   │                             #   calibration/negative_space_index.py
│   ├── trapdoors.json            # 6 buried-shear-plane scenarios for the
│   │                             #   Trapdoor Eval. Auditor-only metadata
│   │                             #   (hidden_shear_plane, scoring_axes) lets
│   │                             #   the evaluator score responses without
│   │                             #   leaking the trap. Paired with
│   │                             #   calibration/trapdoor_eval.py
│   ├── distributional_contract.py  # Cross-repo stable surface for
│   │                             #   money_distribution + investment_
│   │                             #   distribution. CONTRACT_VERSION 0.1.0
│   │                             #   (pre-1.0). Primary consumer:
│   │                             #   metabolic-accounting/distributional/.
│   │                             #   Declares StratificationAxis,
│   │                             #   MoneyFlowDistribution, IncidenceResult,
│   │                             #   InvestmentHoldings, CapitalIncidenceResult.
│   │                             #   HANDOFF_MAP documents which MA fields
│   │                             #   come in and which TAF shapes go out.
│   ├── geometric_bridge_contract.py  # Mirror + functional stdlib fallback
│   │                             #   for the Geometric-to-Binary
│   │                             #   Computational Bridge. CONTRACT_VERSION
│   │                             #   0.1.0, pinned to upstream commit SHA
│   │                             #   (upstream has no SURFACE.md yet).
│   │                             #   Declares DrillDepth, BridgeTarget,
│   │                             #   HardwareData, 7 band tuples,
│   │                             #   gray_to_binary + gray_to_value,
│   │                             #   SensorDecoder/ActuatorController
│   │                             #   Protocols, and working fallback
│   │                             #   implementations (FallbackSensorDecoder,
│   │                             #   FallbackActuatorController) so TAF's
│   │                             #   taf_bridge.py runs end-to-end without
│   │                             #   the external repo installed. Also
│   │                             #   exposes load_bridge_contract() +
│   │                             #   list_bridge_domains() / get_silicon_
│   │                             #   entry_point() etc. -- mirror of
│   │                             #   upstream's cross_repo_bridge_contract.py
│   │                             #   accessor surface for dispatching to the
│   │                             #   18 bridge domains. Paired with
│   │                             #   core/integrations/taf_bridge.py and
│   │                             #   core/integrations/taf_alternative_compute.py.
│   └── bridge_contract_manifest.json # Verbatim mirror of upstream's
│                                 #   bridge_contract_manifest.json (CC0).
│                                 #   18 bridge domains across 4 layers
│                                 #   (physical / contextual / topological /
│                                 #   cognitive) and 6 hardware modules.
│                                 #   Loaded by geometric_bridge_contract.py
│                                 #   when the live upstream package is
│                                 #   not installed.
│   ├── earth_physics_contract.py # Mirrors the assumption_validator
│                                 #   public surface from earth-systems-
│                                 #   physics: RiskLevel, AssumptionBoundary,
│                                 #   ASSUMPTION_KEYS (37 entries spanning
│                                 #   layers 0..6 -- electromagnetics
│                                 #   through biosphere), COUPLING_GRAPH
│                                 #   (16-key failure-propagation map),
│                                 #   AssumptionRecord/CascadeSnapshot/
│                                 #   Alert monitor shapes, plus
│                                 #   PUBLIC_FUNCTIONS signatures for
│                                 #   assess_from_layer_states /
│                                 #   global_confidence_multiplier /
│                                 #   detect_cascade_risk / full_report.
│                                 #   CONTRACT_VERSION 0.1.0, pinned to
│                                 #   upstream commit
│                                 #   341a14b6e1706f16bea6a909d496bde4c8060109
│                                 #   (upstream has no SURFACE.md /
│                                 #   repo-level version yet; 0.1.0 comes
│                                 #   from assumption_validator/__init__.py
│                                 #   __version__). stdlib only -- the
│                                 #   live upstream needs numpy + flask;
│                                 #   this mirror does not. Paired with
│                                 #   core/integrations/earth_physics_fieldlink.py.
│
├── visualizations/                # Frontend visualizations
│   ├── sim3.jsx                  # React simulation component
│   ├── conflict_sim.jsx          # Conflict simulation component
│   ├── attribution_sim.jsx       # Labor attribution simulator (React)
│   ├── cold_idle_cost_2026.html  # Cold idle cost calculator
│   └── labor_audit_protocol.html # Labor thermodynamics audit (rendered HTML)
│
├── docs/
│   ├── audit_2026_04_07.md       # Repository audit notes
│   ├── theory/                    # Core theoretical framework
│   │   ├── functional_epistemology_framework.md  # Core executable module (1700+ lines)
│   │   ├── lhri.md               # Longitudinal Human Resilience Index
│   │   ├── lhri_addendum.md      # LHRI extensions
│   │   ├── lhri_dashboard.md     # Dashboard spec
│   │   ├── seed.md               # Minimal viable seed AI
│   │   ├── egs_core.md           # Entropy Governance System
│   │   ├── egs2.md, egs3.md     # EGS evolved versions
│   │   ├── knowledge_polytensor.md  # K-space 8-dimension framework
│   │   ├── layer0.md             # Layer 0 foundational concepts
│   │   ├── adaptive_resilience_mesh.md  # ARM v0.1
│   │   ├── simulation_module.md  # Simulation design spec
│   │   ├── signal_distortion.md  # Signal theory
│   │   ├── signal_distortion_extended.md
│   │   ├── atomic_accounting_notes.md
│   │   ├── entropy_example.md    # Worked entropy example
│   │   ├── example.md            # Framework application
│   │   ├── fatigue_model.md      # Fatigue model theory
│   │   ├── ferret_fieldlink.md   # Logic-Ferret bridge spec
│   │   ├── haas_fieldlink.md     # HAAS-Q bridge spec
│   │   ├── gaps.md               # Known limitations
│   │   ├── integration.md        # Integration approach
│   │   ├── notes.md              # Working theory notes / drafts
│   │   └── addons.md             # Extension modules
│   │
│   ├── governance/                # Governance theory
│   │   ├── governance_no_ego.md  # Anti-ego governance (934 lines)
│   │   ├── coupled_governance.md # Coupled governance model
│   │   ├── regulatory.md         # Regulatory framework
│   │   ├── tripartite.md         # Three-part governance structure
│   │   └── safety.md             # Safety principles
│   │
│   ├── economics/                 # Economic theory
│   │   ├── regenerative_economics.md
│   │   └── money_labor/          # Energy-grounded value theory
│   │       ├── README.md, Summary.md, LLM-module.md
│   │       ├── Level1-audit.md, Efficiency-dynamic.md
│   │       ├── For-AI.md, Knowledge.md
│   │
│   ├── ai-guidance/               # AI system instructions
│   │   ├── for_ai_systems.md     # Primary AI guidance
│   │   ├── integrated_ai_reasoning.md
│   │   └── ai_notes.md
│   │
│   └── case-studies/              # Real-world case studies (19 files)
│       ├── Case-study1.md through Case12.md
│       ├── Hidden-labor.md, Energy-budget.md
│       ├── Safety-accounting.md, Exposure.md
│       └── ... (see directory for full list)
│
├── AI_ENTRY.md                    # AI onboarding: equations, simulations, safe rules
├── README.md                      # Project overview
├── LICENSE                        # License
└── CLAUDE.md                      # This file
```

## Core Equations

All equations are thermodynamically grounded — every measurement converts to energy units.

### Fatigue Score (0-10)
```
fatigue = clamp(0, 10, (total_load - energy_input) / energy_input * 10)
total_load = (physical + cognitive) * hidden_mult * auto_mult * env_mult
```

### Multipliers
```
hidden_mult = 1 + 0.1 * hidden_count^1.5       # nonlinear combinatorial
auto_mult   = 1 + count * (1 - reliability) * 0.5  # unreliable automation adds load
env_mult    = 1 + max(0, (15 - temp_C) * 0.05) + wind_mps * 0.02
```

### Collapse Thresholds
```
120% energy_input -> productivity degradation
140% energy_input -> safety system breakdown
160% energy_input -> health collapse imminent
distance_to_collapse = clamp(0, 1, (1.6 * E_input - load) / (1.6 * E_input))
```

### Long-Tail Risk
```
risk = 10 * (1 - exp(-0.35 * hidden_count))    # 0-10, nonlinear fast
```

### Parasitic Energy Debt
```
energy_debt = unpaid_hours * metabolic_rate * (1 + friction_events * 0.15)
```

### Intergenerational Production Integration (IPI)
```
struct = ((1-age_seg) * (1-spec) * (1-mobility) * (1-inst_sub))^0.25
elder_anchor = max(0, elder_in_prod) + max(0, elder_incapacity) * 0.8
IPI = min(1.0, struct * elder_anchor)
```

### Node Health
```
health = min(normalized_critical_variables)     # bottleneck determines health
eco    = (soil * biodiversity * water)^(1/3)    # geometric mean
gov    = (rotation * dissent * (1-power_conc) * succession)^0.25
```

### Knowledge Polytensor (8 dimensions)
```
K_kinesthetic  — embodied skill, hands-on capability
K_temporal     — temporal horizon, patience, generational thinking
K_relational   — trust networks, conflict resolution
K_wisdom       — judgment about when to rebuild what
K_skill        — specialized technical capability
K_institutional — bureaucratic/formal knowledge
K_digital      — computational/algorithmic knowledge
K_intuitive    — pattern recognition, implicit knowledge
```

### Money Equation
```
M = sum_i[ p_i * (E_delivered * F(t) - E_waste - E_hidden * L) / (T + S) *
    (1 + K_op * K_cred) * alpha_planetary * D_complexity ]
K_cred = Consequence_density * Verification_freq * Time_under_exposure
```

### Complexity Self-Decay
```
C_index = (complexity * verification_burden) / (energy_throughput * signal_fidelity)
When C_index > 2 -> automatic decay until C_index <= 2
```

## Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Files | `snake_case.py` / `snake_case.md` | `fatigue_model.py` |
| Directories | `snake_case` | `game_theory/` |
| Classes | `PascalCase` | `FatigueModel`, `HumanSystemModel` |
| Functions | `snake_case` | `compute_fatigue()`, `long_tail_risk()` |
| Variables | `snake_case` | `total_load`, `hidden_count` |
| Knowledge dims | `K_` prefix | `K_kinesthetic`, `K_temporal` |
| Energy vars | `E_` prefix | `E_active`, `E_input` |
| Scores | `*_score` suffix (0-10) | `fatigue_score` |
| Indices | `*_index` suffix (0-1) | `regularity_index` |
| Ratios | `*_ratio` suffix | `friction_ratio` |
| Inverted vars | Documented as "LOW good" | `power_concentration`, `ai_capture_risk` |

## Development Notes

### Dependencies
- **core/**: Pure Python (stdlib only — `math`, `datetime`)
- **core/integrations/**: Pure Python (stdlib only — `math`, `datetime`)
- **simulations/**: `numpy`, `matplotlib`, `dataclasses`
- **simulations/lhri_sim.py**: Also requires `networkx`
- **game_theory/**: `numpy`, `scipy`, `json`
- **political_audit/**: Pure Python (stdlib only)

### Running
```bash
# Core modules (no deps)
python core/fatigue_model.py
python core/human_system_collapse_model.py
python core/data_logger.py
python core/heat_leak_case.py

# Integrations / field-link bridges (no deps)
python core/integrations/biological_extraction_model.py
python core/integrations/ferret_fieldlink.py
python core/integrations/geometric_fieldlink.py
python core/integrations/haas_fieldlink.py

# Simulations (require numpy/matplotlib)
python simulations/full_coupled_system.py
python simulations/federation.py

# Political-audit tools (no deps)
python political_audit/c_cam_calculator.py

# Tests
python core/atbs/test_v2.py
```

### Key Design Principles
1. **Thermodynamic grounding** — all measurements convert to Joules
2. **Substrate agnostic** — same math for humans, machines, AI
3. **Organism-centered** — starts with organism needs, not institutional wants
4. **Bottleneck health** — system health = min(critical variables), not average
5. **Inverted variables** — some variables are "LOW good" (power_concentration, ai_capture_risk)
6. **Lagged coupling** — ecological changes propagate with delay to knowledge dimensions
7. **IPI gating** — knowledge transmission gated by structure, not energy surplus

### Audit Notes (2026-03-24)
- `core/fatigue_model.py` was consolidated from 3 duplicate class definitions
- Broken indentation and markdown ``` artifacts were removed
- `HumanSystemModel` now delegates to `FatigueModel` (DRY)
- File names standardized from mixed `Hyphen-Case`/`snake_case` to consistent `snake_case`
- 50+ root-level files organized into `core/`, `simulations/`, `docs/`, `visualizations/`
- `Signal -distortion.md` (space in filename) preserved as `signal_distortion_extended.md`
- `Leyer0.md` (typo) preserved as `layer0.md`

### Audit Notes (2026-04-16)
- `political-audit/` renamed to `political_audit/` to match snake_case convention
- `core/integrations/` created; `biological_extraction_model.py` and the three
  `*_fieldlink.py` bridges (Ferret / Geometric / HAAS) moved there
- `Notes.md` (root) moved to `docs/theory/notes.md`
- `labor_thermodynamics/attribution_sim.md` was actually React/JSX —
  renamed to `visualizations/attribution_sim.jsx` (note: file contains
  Unicode smart quotes that need to be straightened before it will run)
- `labor_thermodynamics/audit_protocol.md` was actually an HTML document —
  renamed to `visualizations/labor_audit_protocol.html`
- `labor_thermodynamics/` now contains only the real markdown specs
  (README, failure_modes, measurement_problem)

### Audit Notes (2026-04-17) -- calibration/ cleanup
- New `calibration/` folder arrived on main with 12 chat-pasted Python
  files. Every file had smart quotes, stray markdown code fences, and
  flat class/def bodies (col 0 instead of col 4). Cleaned up in
  several passes:
  - Mechanical pass: straightened quotes, removed ```` ``` ```` fences,
    fixed `**name**`/`**init**`-style markdown-bold dunders, replaced
    `…` with `...`.
  - Structural pass: programmatic re-indenter that tracked class/def
    body scope plus nested control-flow (if/for/while/with/try)
    recovered most files. Hand-polish for the remaining residual
    errors (mainly scorer-body content that had been trapped inside
    `if not X: return ...` branches, causing silent-None returns).
  - `schema.py` and `calibration_audit.py` were rewritten cleanly;
    `observation_dependance.py` (spelling typo) was renamed to
    `observation_dependence.py` and its 33-line truncated stub
    replaced with a working maturity-model implementation (idea ->
    exploration -> investigation -> theorized -> skill stages,
    stage-mismatch detection, stage-appropriate witness model).
  - `autism_subset_cautionary.py` and `dyslexic_module.py` were
    deleted; their dyslexia / ADHD / autism-spectrum material is
    consolidated into `architecture_mismatch.py` under
    `FAILURE_MODES["pathologizing_substrate_architecture"]`, the
    `SUBSTRATE_PRIMARY_SIGNALS` list, and the `EMBEDDED_PROMPT`
    section addressed to AI models.
  - `architecture_mismatch.py` was landed in three incremental commits
    (Part A: classifier + profile; Part B: signals + FAILURE_MODES;
    Part C: scorers + audit + embedded prompt) after context-timeout
    issues with single-commit rewrites.
- Test suite: `python3 -m unittest calibration.test_calibration -v`
  runs 11 tests, all pass (was only 3 discoverable before the
  test-file nesting fix).

### Audit Notes (2026-05-02) -- metrology/ + root cleanup
- Same chat-paste contamination pattern as the 2026-04-17 calibration
  pass: smart quotes used as triple-quote delimiters, flat class/def
  bodies (col 0 instead of col 4), markdown ``` fences wrapping
  method bodies, `**name**`/`**main**` markdown-bold dunders.
- Root-level cleanup:
  - `resilience_stack.py` rewritten cleanly. Three-layer architecture:
    `AbsenceSignature` registry -> `ConstraintNavigator` ->
    `RegulatoryScopeAudit`. `ResilienceStack.assess()` produces a
    cascade vulnerability score (0-10). stdlib only.
  - `support_cartography.py` already clean (cleaned in prior commit
    `231f0a0` per its commit message).
- Three filename typos / mismatches corrected via `git mv` so module
  filename matches its own self-declared docstring identity:
  - `metrology/domain_mateix.py` -> `metrology/domain_convergence_matrix.py`
    (typo in original filename)
  - `metrology/preregistry.py` -> `metrology/pre1900_engineering_registry.py`
    (filename was a shorthand; docstring + commit message used full name)
  - `metrology/trend.py` -> `metrology/trend_corruption_calculator.py`
    (filename was a shorthand)
  - `metrology/vross_domain.py` -> `metrology/cross_domain_synthesis.md`
    (file content was pure Markdown saved with `.py` extension; same
    pattern as the 2026-04-16 `attribution_sim.md` -> `.jsx` and
    `audit_protocol.md` -> `.html` renames)
- Five Python files in `metrology/` rewritten cleanly with proper
  indentation:
  - `domain_convergence_matrix.py` (12 convergence checks across 5
    reference domains; `score_audit()` returns VALID/WEAKENED/INVALID)
  - `observer_bias.py` (`build_bias_signature()` from
    `CalibrationPair` samples, `correct_historical()` applies inverse
    bias with propagated CIs, `DEFAULT_PRIORS` for 7 observer types)
  - `pre1900_engineering_registry.py` (8 observation-based engineering
    systems: Anishinaabe burning, beaver hydrology, mill ponds,
    Hohokam canals, terraced agriculture, Plains forecasting, Taino
    hurricane forecasting, Inuit sea ice)
  - `trend_corruption_calculator.py` (`MeasurementCorruption` x
    `FrameworkCorruption` -> combined verdict
    REPORTED/INFLATED/INVERTED/INDETERMINATE)
- `⊗` operator symbol in `corruption(measurement) ⊗ corruption(framework)`
  pseudocode replaced with `*` in Python source comments. Markdown
  files keep `⊗` since it renders correctly there.
- All metrology modules: stdlib only. Smoke-test by running each
  module directly: `python3 metrology/<module>.py`.
- Added `metrology/constraint_recovery_framework.py`: extracts the
  physical constraints encoded in pre-1900 engineering systems into
  machine-readable `PhysicalConstraint` records (physical_trigger,
  problem_solved, solution_mechanism, lag_time_weeks, failure_mode,
  cost_of_failure, validation). Three seeded `RecoveredSystem`s
  (mill pond cascade, Anishinaabe seasonal burning, beaver
  hydrology); query helpers `find_system`,
  `find_constraints_by_problem`, `coupled_failure_analysis`. Couples
  to `pre1900_engineering_registry.py` -- the registry catalogs the
  systems, this module recovers their engineering constraints.
- Added `calibration/recency_bias_detector.py`: regex-based pattern
  detector for six recency-bias patterns (temporal_hierarchy,
  progress_narrative, primitive_labeling, library_invisibility,
  translation_laundering, design_logic_loss). `detect_recency_bias()`
  returns `AuditResult` with `BiasFlag`s, severity, and a
  justification_checklist drawn from `JUSTIFICATION_REQUIREMENTS`.
  `evaluate_justification()` is the gate: each flagged question
  needs a substantive answer (>=30 chars + at least one of:
  4-digit year, measurement with unit, comparison phrase, or
  explicit reference marker). Same chat-paste contamination as
  prior cleanups; rewritten cleanly. stdlib only; calibration
  test suite (11 tests) still passes.
- Added earth-systems-physics couple: `schemas/earth_physics_contract.py`
  mirrors the upstream `assumption_validator` public surface (37
  ASSUMPTION_KEYS, 16-key COUPLING_GRAPH, RiskLevel /
  AssumptionBoundary / AssumptionRecord / CascadeSnapshot / Alert
  shapes, PUBLIC_FUNCTIONS signatures). CONTRACT_VERSION 0.1.0
  pinned to upstream commit
  341a14b6e1706f16bea6a909d496bde4c8060109. Paired with
  `core/integrations/earth_physics_fieldlink.py`, which maps TAF's
  framework-layer convergence checks (F1-F7 in
  metrology/domain_convergence_matrix.py) to upstream assumption
  keys: F1_stationarity -> 8 anchors (atmo_jet_shear,
  atmo_hadley_extent, hydro_AMOC_collapse, hydro_AMOC_transport,
  hydro_arctic_amplification, hydro_committed_warming,
  bio_amazon_tipping, bio_NEP_sink); F2_baseline_selection -> 4;
  F4_human_modification -> 6. F3/F5/F6/F7 are intrinsically
  methodology-layer and return verdict="UNKNOWN" with an explicit
  note. Loose-coupled: `physics_anchor_for_check()` will use the
  live upstream `assumption_validator` package if importable;
  otherwise it returns UNKNOWN verdicts so TAF stays runnable in
  isolation. stdlib only.
