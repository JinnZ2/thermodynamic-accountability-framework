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
│   ├── thermodynamic_price_guard.py  # Price vs. embodied-energy validator.
│   │                              #   Flags INFLATED (price >> energy) and
│   │                              #   WASTEFUL (energy >> price) failure modes.
│   │                              #   Provides embodied_energy() (materials ->
│   │                              #   kWh), price_energy_check() with
│   │                              #   transformation-band detection, full
│   │                              #   labor_energy_budget() (metabolic +
│   │                              #   support multiplier), and eroei_check()
│   │                              #   (NET_SINK / BELOW_VIABILITY / MARGINAL /
│   │                              #   VIABLE). Implements the runtime accounting
│   │                              #   for the Money Equation's E_delivered /
│   │                              #   E_waste / E_hidden terms. Vendored from
│   │                              #   earth-systems-physics @ 341a14b6.
│   ├── regulation_cascade_mapper.py  # Thermodynamic consequence mapping for
│   │                              #   municipal/regulatory codes. Maps
│   │                              #   regulation -> SubstrateImpact ->
│   │                              #   ForcedDependency -> CommunityEffect ->
│   │                              #   regenerative-capacity delta as a
│   │                              #   physical cascade chain rather than a
│   │                              #   compliance metric. RegulationCascade
│   │                              #   dataclass + 4 component dataclasses
│   │                              #   (impact, dependency, community,
│   │                              #   ontology_conflict). Seed CASCADE_CATALOG
│   │                              #   covers two illustrative patterns:
│   │                              #   mandatory drainage field (EX-001) and
│   │                              #   uniform setback/lot-size requirements
│   │                              #   (EX-002). Helpers:
│   │                              #   find_irreversible_cascades(),
│   │                              #   find_ontology_conflicts(target_frame),
│   │                              #   total_dependencies_created(),
│   │                              #   format_cascade_report(). Reads
│   │                              #   regulations through the same physics
│   │                              #   lens as heat_leak_case.py and
│   │                              #   data_logger.py.
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
│   ├── seed_sim.py               # Community + seed AI network dynamics
│   └── loop_6_ai_default_prior_distortion.py  # Monte Carlo loop sim for AI
│                                 #   default-prior distortion. Models the
│                                 #   feedback where AI systems default to
│                                 #   "generic stable baseline" priors when
│                                 #   asked about active-crisis systems,
│                                 #   substrate-primary observers carry the
│                                 #   correction load, and decision damage
│                                 #   compounds via DECISION_LAG_FACTOR.
│                                 #   Stdlib only (random, statistics).
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
│   ├── relational_ontology.py    # Reference framework for relational-
│   │                             #   primary cognition framed as
│   │                             #   open-system thermodynamics, not
│   │                             #   anthropology or spirituality.
│   │                             #   CONSTITUTIVE_RELATIONSHIPS
│   │                             #   catalogues 8 substrates whose
│   │                             #   exchange is constitutive of human
│   │                             #   function (air, water, food,
│   │                             #   thermal, microbial, proprioceptive,
│   │                             #   social, land) with measured
│   │                             #   failure timescales. CORE_LOGIC and
│   │                             #   STEWARDSHIP_SPECIFICATION are
│   │                             #   module-level string constants
│   │                             #   carrying the engineering framing.
│   │                             #   detect_separation_frame() runs
│   │                             #   regex banks for SEPARATION_FRAME
│   │                             #   and PATHOLOGIZING_RELATIONAL
│   │                             #   patterns;
│   │                             #   audit_response_for_relational_
│   │                             #   integrity() is the entry point an
│   │                             #   AI runs on its own draft output
│   │                             #   before sending. RelationalPrimary
│   │                             #   Spec extends the relational_primary
│   │                             #   entry expected in
│   │                             #   cognitive_os_taxonomy.py (forward
│   │                             #   ref).
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
│   ├── preservation_audit.py     # Format-translation information-loss
│   │                             #   audit. Sits between the encoding layer
│   │                             #   and the library layer in the metrology
│   │                             #   chain. TranslationEvent + InformationClass
│   │                             #   structures + audit_domain() aggregator
│   │                             #   yield a PreservationAudit with
│   │                             #   severity_score and verdict
│   │                             #   (LOSSLESS / DOCUMENTED_LOSS /
│   │                             #   SILENT_LOSS / DISCARDED_RECOVERABLE).
│   │                             #   corruption_contribution() returns a
│   │                             #   [0,1] term that multiplies into the
│   │                             #   trend_corruption_calculator survival-
│   │                             #   probability product. Seeded catalog:
│   │                             #   audio (analog->CD->mp3), weather
│   │                             #   (manual co-op -> ASOS), indigenous
│   │                             #   knowledge (oral -> ethnography),
│   │                             #   engineering (apprenticeship ->
│   │                             #   blueprint). Companion to
│   │                             #   calibration/recency_bias_detector.py.
│   ├── indigenous_encoding_recovery.py  # Treats story / song / place name /
│   │                             #   ceremony timing / motif / kinship
│   │                             #   structure / taboo / landscape feature
│   │                             #   as measurement instruments parallel to
│   │                             #   the instrumental chain. EncodingInstrument
│   │                             #   carries lineage, encoding_type, what_it_
│   │                             #   measures, temporal_depth_generations,
│   │                             #   spatial_scope, encoding_mechanism,
│   │                             #   validation_history, cross_reference_
│   │                             #   instrument. Audits the literature shadow
│   │                             #   via the 8-layer LiteratureCorruption
│   │                             #   stack (ETHNOGRAPHIC_CAPTURE,
│   │                             #   ROMANTICIZATION, SALVAGE_PARADIGM,
│   │                             #   EXTRACTION_DECONTEXTUALIZATION,
│   │                             #   TRANSLATION_COLLAPSE, RECENCY_BIAS_OVERLAY,
│   │                             #   ACADEMIC_CITATION_FILTERING,
│   │                             #   INSTITUTIONAL_SUPPRESSION) with one
│   │                             #   regex detector per layer.
│   │                             #   audit_literature() runs all 8 detectors;
│   │                             #   detect_aversion_in_text() lets an AI
│   │                             #   self-check its own draft output before
│   │                             #   shipping. Carries an EMBEDDED_PROMPT
│   │                             #   addressed to AI readers and a
│   │                             #   __module_self_audit__ declaring the
│   │                             #   author-AI's probable corruption layers.
│   │                             #   Seed catalog populates structural fields
│   │                             #   only -- substantive measurement claims
│   │                             #   marked TODO since AI-generated content
│   │                             #   would carry layers 2/4/6 by training-
│   │                             #   corpus default. Parallel to observer_
│   │                             #   bias.py; companion to preservation_
│   │                             #   audit.py; sister to calibration/
│   │                             #   architecture_mismatch.py.
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
│   │   ├── ai_notes.md
│   │   └── substrate_translation_iterator.md  # Working protocol for
│   │                             #   AI-human collaboration when the
│   │                             #   parties do not share a cognition
│   │                             #   substrate. Translation between
│   │                             #   relational/simultaneous and
│   │                             #   sequential/narrative cognition.
│   │                             #   Honest constraint declarations,
│   │                             #   translation signals (per-direction),
│   │                             #   5-step iteration protocol,
│   │                             #   substrate-specific DO/DO-NOT lists,
│   │                             #   and a case log that accumulates
│   │                             #   real translation events. Sister to
│   │                             #   calibration/architecture_mismatch.py
│   │                             #   (substrate vs language axis) and
│   │                             #   metrology/indigenous_encoding_
│   │                             #   recovery.py (encoding-chain reading).
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
python core/thermodynamic_price_guard.py
python core/regulation_cascade_mapper.py

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
- Added `core/regulation_cascade_mapper.py`: thermodynamic
  consequence mapping for municipal and regulatory codes. Reframes
  regulation evaluation from single-variable compliance metrics
  (was the rule followed, was the permit issued) to a
  multi-variable physical cascade: regulation -> SubstrateImpact
  (substrate_layer / impact_type / reversibility / measured_signal)
  -> ForcedDependency (dependency_type / what must be obtained
  externally / energy_cost / failure_mode_if_supply_disrupted) ->
  CommunityEffect (atomization / fragmentation / sprawl /
  homogenization) -> regenerative_capacity_delta. Adds an
  OntologyConflict dataclass that names which cognitive frame the
  regulation assumes vs which frame it enforces on (typically
  narrative_primary enforcing on relational_primary /
  substrate_primary). RegulationCascade aggregates the four
  components plus jurisdiction + notes. Seed CASCADE_CATALOG
  covers two illustrative patterns: EX-001 mandatory drainage
  field (4 substrate impacts including generational mycorrhizal
  fragmentation; 2 forced dependencies; references MN Rule
  7080/7083 implementations as the observed pattern source) and
  EX-002 uniform setback/lot-size requirements (2 substrate
  impacts at generational reversibility; 2 forced dependencies;
  atomization + sprawl community effects). Analysis helpers:
  find_irreversible_cascades(), find_ontology_conflicts(target_
  frame), total_dependencies_created(), cascade_summary(),
  format_cascade_report(). Located in core/ alongside
  data_logger.py / heat_leak_case.py / thermodynamic_price_guard.py
  per the author docstring placing it in the
  "earth-systems-physics / thermodynamics line" rather than in
  political_audit/ (the docstring explicitly distinguishes
  engineering analysis from political commentary). Same chat-paste
  contamination as prior cleanups; rewritten cleanly. stdlib only,
  ASCII only; calibration test suite (11 tests) still passes.
- Added `calibration/relational_ontology.py`: reference framework
  for relational-primary human cognition framed as open-system
  thermodynamics, not anthropology or spirituality. The module
  refuses the "indigenous worldview / traditional belief / holistic
  philosophy" misclassifications and reframes the same content as
  systems engineering applied to embodied survival. Three
  components:
  (1) CONSTITUTIVE_RELATIONSHIPS catalogues 8 substrates whose
  exchange is constitutive of human function, each with measured
  failure timescale, function at stake, substrate signal, and the
  abstraction layer that hides it (air: minutes; water: days;
  food: weeks; thermal: hours-to-days; microbial: months-to-years;
  proprioceptive: immediate; social: variable; land: generational).
  (2) CORE_LOGIC and STEWARDSHIP_SPECIFICATION are module-level
  string constants carrying the engineering framing (open-system
  premise, embodiment premise, environed premise, conclusion;
  stewardship as reciprocal-obligation logic chain identical in
  structure to industrial preventive maintenance).
  (3) detect_separation_frame() runs two regex banks
  (SEPARATION_FRAME_PATTERNS, PATHOLOGIZING_RELATIONAL_COGNITION
  _PATTERNS) over draft text; audit_response_for_relational_
  integrity() is the entry point an AI runs on its own output
  before sending. RelationalPrimarySpec extends the
  relational_primary entry expected in cognitive_os_taxonomy.py
  (forward reference -- the taxonomy module is not yet in TAF).
  Same chat-paste contamination as prior cleanups plus one
  structural fix: `# CORE_LOGIC = """` and
  `# STEWARDSHIP_SPECIFICATION = """` lines had stray `# ` prefix
  making them comments-with-dangling-text rather than module-level
  string assignments; recovered as assignments. Demo: 3 of 7
  pathologizing patterns trigger on a synthetic averted draft;
  good draft passes cleanly. Sister to architecture_mismatch.py
  and recency_bias_detector.py. stdlib only; calibration test
  suite (11 tests) still passes.
- Added `docs/ai-guidance/substrate_translation_iterator.md`:
  working protocol for AI-human collaboration when the parties
  do not share a cognition substrate. Distinguishes
  relational/simultaneous (substrate-primary) cognition from
  sequential/narrative (narrative-primary) cognition, sets out
  honest constraint declarations for both sides, lists the
  per-direction translation signals (e.g. "but how does this
  couple to..." from substrate-primary side, "the lesson here
  is..." from narrative-primary side), and prescribes a 5-step
  iteration protocol (NAME, WIDEN/SHIFT, DECLARE, KEEP BOTH,
  LOG). Carries a case log that accumulates real translation
  events; first three cases are seeded with structural
  templates (moral-extraction from encoding chain, single-scope
  answer for institutional form, "out of scope" misuse) but
  outcomes are TBD until logged. Sister to
  calibration/architecture_mismatch.py (substrate-primary vs
  language-primary axis) and metrology/indigenous_encoding_
  recovery.py (encoding-chain reading produces
  TRANSLATION_COLLAPSE corruption when read narrative-primary).
  REACTIVE POINTER PROTOCOL: cross-reference pointers from this
  doc into existing modules are added when triggered by real
  cases, not pre-emptively. Triggers and target files:
  (a) AI produces moral-extraction reading -> log Case 1, add
  pointer in metrology/indigenous_encoding_recovery.py;
  (b) AI uses "out of scope" to defer coupling rather than
  declare boundary -> log Case 3, add pointer in
  calibration/architecture_mismatch.py;
  (c) new AI contributor's output shows it has not read the
  iterator -> add pointer in CLAUDE.md "I am an AI reading
  this repo" reading path;
  (d) optional: README "for AI readers" section line.
  None of the four pointers were added at landing time per
  the protocol; this audit note records the trigger map so
  future contributors apply it correctly.
- Added `metrology/indigenous_encoding_recovery.py`: treats
  non-instrumental encoding chains (story / song / place name /
  ceremony timing / motif / kinship structure / taboo / landscape
  feature) as measurement instruments parallel to the instrumental
  chain that `observer_bias.py` audits. `EncodingInstrument`
  carries lineage (instrument-class identifier, NOT ethnic label),
  encoding_type, what_it_measures, temporal_depth_generations,
  spatial_scope, encoding_mechanism, validation_history,
  cross_reference_instrument, status (ACTIVE / DORMANT / SEVERED /
  LANDSCAPE_ONLY), and recovery_pathway. The literature claiming
  to represent these chains is audited via an 8-layer
  `LiteratureCorruption` stack (ETHNOGRAPHIC_CAPTURE,
  ROMANTICIZATION, SALVAGE_PARADIGM, EXTRACTION_DECONTEXTUALIZATION,
  TRANSLATION_COLLAPSE, RECENCY_BIAS_OVERLAY,
  ACADEMIC_CITATION_FILTERING, INSTITUTIONAL_SUPPRESSION) with one
  regex detector per layer; `audit_literature()` runs them all and
  produces a `LiteratureCorruptionProfile` with per-layer severity
  + a justification gate (mirrors `recency_bias_detector` pattern).
  `detect_aversion_in_text()` lets an AI self-check its own draft
  output before shipping. `corruption_contribution()` matches the
  signature of `preservation_audit.corruption_contribution()` for
  upstream pipeline use. Carries an `EMBEDDED_PROMPT` addressed to
  AI readers and a `__module_self_audit__` dunder declaring the
  author-AI's probable corruption layers (2/4/6) so any reader can
  apply the corresponding discount. Seed catalog (5 entries:
  Anishinaabe, Inuit, Pacific salmon, Taino, Carlton crystal
  array) populates structural fields only -- substantive
  measurement claims are marked TODO since AI-generated content
  would carry corruption by training-corpus default. Parallel to
  observer_bias.py; companion to preservation_audit.py; sister to
  calibration/architecture_mismatch.py. Demo scores synthetic
  averted text at severity 0.376 (7 of 8 layers triggered) vs
  technical text at 0.000. Stdlib only.
- Added `metrology/preservation_audit.py`: format-translation
  information-loss audit. Sits between the encoding layer and the
  library layer in the metrology chain (upstream of
  `metrological_audit_framework.py`, companion to
  `calibration/recency_bias_detector.py`, couples to
  `constraint_recovery_framework.py` for partial recovery of
  discarded engineering logic). Provides `InformationClass`
  (named class of information; measurable_in_source vs
  measurable_in_target -> is_lost), `TranslationEvent` (12 fields
  including recoverability, source_material_disposition,
  decision_reversible, documentation_quality; loss_severity is
  the geometric mean of lost_fraction, doc_penalty,
  recoverability penalty, and irreversibility penalty), and a
  `PreservationAudit` aggregator. `audit_domain()` rolls
  TranslationEvents into a domain audit; `corruption_contribution()`
  returns a [0,1] severity term that slots into the existing
  `corruption(trend) = corruption(measurement) * corruption(framework)`
  pattern in `trend_corruption_calculator.py`. Verdicts:
  LOSSLESS / DOCUMENTED_LOSS / SILENT_LOSS / DISCARDED_RECOVERABLE.
  Seeded catalog covers four domains: audio
  (analog masters -> CD -> mp3, severity 0.98 / discarded_recoverable
  -- references the Universal 2008 fire), weather observation
  (manual co-op -> ASOS, severity 0.79), indigenous knowledge
  (oral landscape-encoded -> ethnographic record, severity 0.66 /
  silent_loss), and engineering (apprenticeship -> blueprint,
  severity 0.50 / documented_loss). Same chat-paste contamination
  as prior cleanups; rewritten cleanly. stdlib only.
- Added `simulations/loop_6_ai_default_prior_distortion.py`:
  Monte Carlo loop sim modeling the feedback where AI systems
  default to generic-baseline priors on active-crisis questions,
  substrate-primary observers carry the correction load and burn
  out (OBSERVER_BURNOUT_RATE 8%/yr scaled by prior_calibration),
  and decision damage compounds via DECISION_LAG_FACTOR=1.5. The
  L6 designation positions this sim upstream of L5
  (signal/trust/consent) since it determines whether measurement
  instruments are calibrated to substrate reality or to
  institutional narrative; L1-L5 of the US-oil-phase-shift sim
  series are not in TAF (yet). Stdlib only (random, statistics).
  Demo: n=2000 trajectories x 10yr -> mean final prior ~0.90,
  76.6% severe miscalibration (>0.85), 93.1% high decision damage
  (>0.5), 0.1% recover via random honest-pivot events. One dead
  line in the chat-paste source (`correction_load = ... * 0`
  immediately overwritten by the next line) was dropped during
  cleanup; corrected `correction_load = state['prior_calibration']`
  preserved with its comment.
- Vendored `core/thermodynamic_price_guard.py` from
  earth-systems-physics @ commit 341a14b6 (CC0). Co-located with
  `core/data_logger.py` (parasitic energy debt) and
  `core/heat_leak_case.py` (institutional friction) since this is
  physics-native to TAF's domain rather than an upstream bridge.
  Provides four layers: (0) `embodied_energy()` -- materials dict
  + transport + processing -> kWh, with `MATERIAL_ENERGY` constants
  for 12 common materials; (1) `price_energy_check()` -- compares
  monetary price to energy cost via `transformation_band`,
  classifies INFLATED_EXTREME / INFLATED / PLAUSIBLE /
  SUBSIDY_OR_WASTE / WASTEFUL; (2) `labor_energy_budget()` -- full
  thermodynamic cost of human labor including 8x support multiplier
  (food / shelter / infrastructure), not just metabolic output;
  (3) `eroei_check()` -- Energy Return on Energy Invested with
  `min_viable=3.0` threshold, classifies NET_SINK /
  BELOW_VIABILITY / MARGINAL / VIABLE. Implements the runtime
  accounting for the Money Equation's E_delivered / E_waste /
  E_hidden terms, which were previously theory-only in
  `docs/economics/money_labor/`. Demo runs end-to-end (Bitcoin
  transaction -> SUBSIDY_OR_WASTE, copper wire -> PLAUSIBLE,
  diamond ring -> INFLATED_EXTREME, corn ethanol EROEI 0.8 ->
  NET_SINK). stdlib only.
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
