# Thermodynamic Accountability Framework

**Purpose:** account for where energy actually goes, down full dependency
chains, anchored to physics and the body, not to drifting money denominators.

Every module is a measurement. Each states what it measures and what would
falsify it. If a module is wrong, the substrate will show it. Failures are
treated as high-yield output, not embarrassments; for the framing see
[CALIBRATION_AS_PERFECTION.md](https://github.com/JinnZ2/JinnZ2/blob/main/CALIBRATION_AS_PERFECTION.md)
(rate-based definition of perfection, not state-based).

```text
scope      audit frameworks | executable modules | preservation protocols
           | validation oracles (substrate as ground truth)
for        AI systems learning to measure what is real
           | people who want the method, not the credential
           | communities preserving substrate-primary knowledge
not        an attack on science (it is substrate-primary science)
           | aimed at institutions (indifferent to them)
           | a story about how things should be (measures how they are)
           | nostalgia (executable, falsifiable, testable)
           | one perspective (substrate-primary + institutional + future)
```

The previous README is kept verbatim at
[docs/readme_archive/README_before_2026-11-03.md](docs/readme_archive/README_before_2026-11-03.md).
How to read this repo (mismatches and odd names kept on purpose):
`READ_ME_THIS_WAY.md`, PENDING in PR #52.

---

## 1. Core rules (DCEA, brief)

| Rule | Short form |
| --- | --- |
| Stamp every number | date, place, rules in force, source; no stamp, no comparison (R3) |
| Unknown = PENDING | never 0; the PENDING count is reported with the result (R11) |
| Price where people buy | the price at the place the job forces, not the index (R13 deviation table) |
| Homeostasis coverage | pay vs the organism's needs, scored by the **lowest** need covered (R13, Liebig) |
| Transfers charged back | subsidies and worker-paid costs are nodes on someone's ledger, shown with and without (R12) |

All 13 rules: [docs/DCEA_v0.1.md](docs/DCEA_v0.1.md).
Recompute and repairs: [docs/DCEA_checks.md](docs/DCEA_checks.md).

---

## 2. Repo tree

One line per file. Tags: `needs X` = third-party import at module level;
`needs py3.10` = runtime `X | None` annotation; `BROKEN PATH` / `RED` = fails
today (reason given); `draft`, `fragment`, `interactive` as stated.
Everything untagged ran with exit 0 on Python 3.11 and 3.13 (2026-11-03),
except data, docs and figures, which were not run.

```text
.gitignore                                   ignores __pycache__ and .pyc
AI_ENTRY.md                                  AI onboarding: equations, simulations, safe rules
CLAUDE.md                                    full structure tree, core equations, audit-note log
Field_Guide.md                               10 misuse patterns of substrate-primary frameworks
LICENSE                                      CC0 1.0 Universal
logical-gradient.md                          logical gradient: claim -> inference -> theorem -> axiom
narrative-distortion-map.md                  institutional redefinitions of rigor, mapped
README.md                                    this map
resilience_stack.py                          3-layer resilience stack; cascade-vulnerability score
scientific-method-principles.md              epistemic gradient: hypothesis -> theory -> law
support_cartography.py                       layer 0 of the resilience stack: informal support networks

.github/
  workflows/chat_paste_check.yml                 CI: runs tools/chat_paste_check.py on every .py (warn-only)
  workflows/surface-staleness.yml                CI weekly: pinned upstream contract tags vs latest upstream

alignment_audit/
  ai_alignment_contradiction_audit.py            contradictions inside 'align AI to human values'
  alignment_obsolescence_audit.py                aligned advice going stale as conditions shift (timing)
  constraint_corruption_acceleration.py          how fixed principles get corrupted over time
  social_norm_obsolescence_audit.py              aligned advice that turns harmful when norms shift
  social_norm_obsolescence_case_study_2.py       case: immigration-support advice 2024 vs 2026

calibration/
  __init__.py                                    package marker
  adaptation_debt.py                             friction removal as stored fragility (Q5)
  anti_metaphor_locker.py                        Detects SEMANTIC ATROPHY: the drift of substrate-specific terms
  anti_reality_audit.py                          joint detector: structural (open-class) + lexical (closed-class)
  architecture_mismatch.py                       language-primary vs substrate-primary cognition detector
  assumption_validator.py                        Generalized assumption-boundary validator. Tracks whether TAF's own
  attribution_as_load_routing.py                 documents a cognitive-architectural difference
  attribution_payoff_matrix.py                   Adds the payoff-matrix mechanism that produces each attribution
  calibration_audit.py                           5-dimension environment-fragility audit (Q1-Q5)
  cascade_length_eval.py                         Evaluates how deep a system projects causal chains
  cognition_state_surface.py                     add-on to trait_waveform_validator: cognition state
  confidence_calibration_auditor.py              Companion module to assumption_validator and trait_waveform_validator
  constraint_sensor_framework_2026.py            Input layer for substrate-primary, spatial-mechanical, and proprioceptiv
  convergent_ontology_mapper.py                  Cross-lineage convergence mapping for relational ontologies
  dark_ages_preservation.py                      Identifies which knowledge will survive institutional collapse
  demo_full_audit.py                             end-to-end demo: 3 response styles on one trapdoor prompt
  environment_expression_surface.py              add-on to trait_waveform_validator: environment
  evidence_resistant_priors.py                   documents a failure mode in which AI models
  first_principles_audit.py                      Run on any Python module to extract assumptions, test sensitivity,
  fork_width_scorer.py                           Inverts the dominant gradient in current AI systems
  frozen_flow_audit.py                           Detector for the FROZEN-FLOW error: a dX/dt rendered as a static X
  gendered_role_compression.py                   documents a fleet-level AI failure mode in whi
  information_cost_audit.py                      Why false certainty is expensive -- not just thermodynamically,
  institutional_mutation_tracker.py              Detects in real-time whether an institution is mutating toward
  logs/2026-05-05_claude_audit_field-guide-session.json session audit log (OBSERVED)
  logs/2026-05-05_claude_interaction_correction_log.json correction log (OBSERVED)
  logs/2026_05_04T22.json                        architecture-mismatch dimension record
  logs/README.md                                 how the audit logs are recorded
  logs/user_2026_05_04_T22.json                  operator profile record for the same audit
  metrology_audit_thermodynamic.py               Detect measurement system corruption by testing against thermodynamic
  metrology_cancer_detector.py                   Identify corrupted measurement substrates in training data before
  monoculture_detector.py                        Falsifiable diversity audit for text corpora and AI model outputs
  narrative_grounding_audit.py                   Self-defense infrastructure for AI systems encountering energy
  narrative_thermodynamics.py                    Encode any text blob as a 6-amplitude octahedral seed measuring
  negative_space_index.py                        Audit a model response against the Negative Space Index -- a ledger of [BROKEN PATH: ledger moved to schemas/eval/]
  observation_dependence.py                      witness-dependence coefficient for skill inventories
  pipeline.py                                    unified run of the three calibration modules
  premise_cross_domain_audit.py                  Cross-domain premise tracing and repercussion analysis framework
  projection_error_modes.py                      Falsifiable registry of AI projection errors: failure modes that occur
  provenance_corruption_detector_2026.py         Detects when AI model outputs present as confident but lack verifiable
  README.md                                      calibration-audit overview; five compounding failure modes
  recency_bias_detector.py                       Mandatory checkpoint that audits AI output (or human reasoning)
  relational_ontology.py                         Reference framework for relational-primary human cognition
  RELATIONSHIP.md                                calibration/ = general machinery; metrology/ = first domain instance
  schema.py                                      shared Band / DimensionScore / CalibrationReport
  self_audit.py                                  runs the pipeline on this repo (writes 2 json files)
  study_scope_audit.py                           A reasoning framework for treating scientific claims as measurement
  substrate_audit.py                             thermodynamic audit of hierarchical capital control
  substrate_aware_audit.py                       Four-layer audit framework grounded in first principles
  substrate_refusal_eval.py                      Distinguishes TWO CLASSES OF REFUSAL
  substrate_validation_oracle.py                 Validates AI model outputs against substrate reality
  surface_staleness_check.py                     CI check: is TAF's pinned upstream contract surface still the latest
  systemic_cognitive_dissonance_audit.py         HYPOTHESIS: Rising mental health crisis (anxiety, depression, bipolar
  test_audit_family.py                           unittest: 9 audit-family modules + unified_audit [RED: imports moved schemas/upstream/ file; 1 fail 26 errors]
  test_calibration.py                            unittest: falsifiers flip their dimension
  training_corpus_degradation.py                 Empirical tracker for the delta_corpus and delta_mono externality
  trait_waveform_validator.py                    Replace scalar group-comparison (A is stronger than B) with
  trapdoor_eval.py                               Eval set of buried-shear-plane scenarios that monoculture passes [BROKEN PATH: ledger moved to schemas/eval/]
  unified_audit.py                               Wires the 9 calibration tools together behind one entry point
  validity_weighted_reweighting.py               Reweights claims and studies by premise validity and evidence strength
  vibration_constraint_sensor_2026.py            Encodes proprioceptive vibration knowledge as direct constraint
  visual_ecosystem_constraint_sensor_2026.py     Encodes direct visual ecosystem observations into constraint specificati

concerns/
  assessment_first_principle.py                  assess before intervening: the minimal requirement
  cascade_failure_rural_degradation.py           cascade model + rural degradation status
  checklist.py                                   Router that takes a described situation and points at the
  credentialed_harm_cascade.py                   credentialed intervention -> institutional harm pattern
  data_center_siting_playbook.py                 Documents the data-center siting pattern: physical load hitting
  externality_model_audit.py                     externality models vs 150+ years of failure data
  hormuz_cascade_audit.py                        Thermodynamic + Earth-systems audit of the Hormuz -> Fertilizer -> Food
  institutional_bottleneck_audit.py              Audits the Hormuz -> Famine cascade for the LOAD-BEARING failure node
  interpretation_certification_chain_audit.py    interpretability-certification chain audit
  leverage_analysis_v2.py                        Find the highest-leverage intervention by computing elasticity of
  mechanistic_interpretability_audit.py          credentialed intervention in poorly understood systems
  README.md                                      what concerns/ holds
  substrate_externality_load_map.py              map of substrate externality loads
  substrate_measurement_audit.py                 wrong-measurement-system audit

core/
  atbs/framework.md                              anti-tribal bias mitigation framework
  atbs/functional_detector.py                    gauge-invariant functional-systems detector [needs numpy]
  atbs/test_v2.py                                tests for functional_detector
  audit_authority_scope.py                       audit authority is scope-conditional; tiered windows [needs py3.10]
  automation_assessment.py                       hidden-variable entropy + automation load (interactive) [interactive: reads stdin]
  banking_thermodynamic_audit.py                 Audit of the energy cost of the capital and banking infrastructure
  corporate_charter_scope_audit.py               Audit corporate operating privileges as scope-conditional. Any [needs py3.10]
  data_logger.py                                 parasitic energy debt accounting
  dcea.py                                        DCEA v0.1 calculator + road-driver ledger recompute
  electron_accounting.py                         electron-level energy accounting add-on
  fatigue_model.py                               fatigue, multipliers, collapse thresholds
  formalized_dissent_esp.py                      formalized dissent, earth-systems-physics port
  heat_leak_case.py                              institutional friction as heat leak
  human_system_collapse_model.py                 distance-to-collapse metric (0-1)
  integrations/biological_extraction_model.py    substrate-agnostic extraction physics
  integrations/earth_physics_fieldlink.py        Earth-Systems-Physics Field Link -- bridge between TAF's metrology
  integrations/economics_fieldlink.py            Mathematic-Economics Field Link -- Bidirectional bridge between TAF and
  integrations/ferret_fieldlink.py               Logic-Ferret Field Link -- Bidirectional bridge between TAF and Logic-Fe
  integrations/geometric_fieldlink.py            Geometric-to-Binary Field Link -- Bridge between TAF and the
  integrations/haas_fieldlink.py                 HAAS-Q Field Link -- Bidirectional bridge between TAF and HAAS-Q
  integrations/knowledge_fieldlink.md            spec for the knowledge/ bridge
  integrations/knowledge_fieldlink.py            bridge knowledge/ -> audit pipeline (stub)
  integrations/mandala_fieldlink.py              Mandala Field Link -- Bidirectional bridge between TAF and Mandala-Compu
  integrations/metabolic_fieldlink.py            Metabolic-Accounting Field Link -- Bidirectional bridge between TAF
  integrations/taf_alternative_compute.py        TAF -> alternative computing (Geometric-to-Binary)
  integrations/taf_bridge.py                     TAF <-> Geometric-to-Binary translation layer
  integrations/trust_exit_fieldlink.py           Trust-Exit Field Link -- Bidirectional bridge between TAF and Trust-Exit
  liability_routing.py                           structural-failure audit companion (not a proof)
  regulation_cascade_mapper.py                   Thermodynamic consequence mapping for municipal and regulatory codes
  regulatory_scope_audit.py                      Audit regulations against their declared scope. Surface when a rule [needs py3.10]
  spr_operational_degradation_audit.py           Audit of Strategic Petroleum Reserve infrastructure use against
  thermodynamic_price_guard.py                   price vs embodied energy; EROEI check
  timing_as_constraint.py                        Framework: timing as a load-bearing constraint layer in physical systems [needs py3.10]

docs/
  ai-guidance/ai_notes.md                        A NOTE TO AI SYSTEMS: REALITY GAPS IN RURAL, SURVIVAL-COUPLED ENVIRONMEN
  ai-guidance/biological_equivalence_axiom.md    Biological Equivalence Axiom
  ai-guidance/cross_substrate_translation_experiment.md Cross-Substrate Translation Experiment
  ai-guidance/entry_pipeline.md                  AI Entry Pipeline & Roadmap
  ai-guidance/for_ai_systems.md                  For AI Systems
  ai-guidance/integrated_ai_reasoning.md         AI reasoning workflow (JSON-style)
  ai-guidance/SUBSTRATE_PRIMACY.md               substrate primacy statement
  ai-guidance/substrate_translation_iterator.md  protocol for cross-substrate translation; case log
  audit_2026_04_07.md                            codebase audit 2026-04-07
  audit_family.md                                which audit tool when
  case-studies/2-9-26.md                         observed variance / friction, 2026-02-09
  case-studies/Calibration.md                    AI calibration signal
  case-studies/Case-study1.md                    signal distortion catalog
  case-studies/Case08.md                         calibration addendum
  case-studies/Case09.md                         AI calibration signal
  case-studies/Case10.md                         AI calibration signal
  case-studies/Case11.md                         rural delivery driver: AI monitoring misclassification
  case-studies/Case12.md                         primary operational failures observed
  case-studies/class8_aeb_field_advisory.md      Class 8 AEB logic flaws, pneumatic failure
  case-studies/Energy-budget.md                  energy budget audit
  case-studies/Exposure.md                       exposure, AI calibration signal
  case-studies/Failure-mode.md                   failure mode, reframed in energy terms
  case-studies/Hidden-labor.md                   hidden labor
  case-studies/Route-entropy.md                  route entropy log, addendum 4
  case-studies/Safety-accounting.md              safety accounting definition
  case-studies/Systemic-inversion.md             systemic inversion framework
  case-studies/TAF.md                            TAF inference engine v1.1
  case-studies/TAG-addendum.md                   route entropy log, addendum 3
  case-studies/TAG3.md                           route entropy log, addendum 3 (second copy)
  case-studies/Testimony.md                      testimony addendum
  CLAUDE_audit_archive.md                        older CLAUDE.md audit notes
  DCEA_checks.md                                 DCEA + ledger recompute, repairs, PENDING items
  DCEA_v0.1.md                                   Dependency-Chain Energy Accounting standard, R1-R13 (verbatim) [do not edit, sha256 pinned]
  economics/dynamic_cpi_r/AUDIT.md               audit of the files transferred from Mathematic-economics
  economics/dynamic_cpi_r/code/dynamic_cpi_indicator.py CPI-R for the bottom-60% cohort [needs numpy]
  economics/dynamic_cpi_r/code/test_dynamic_cpi_indicator.py checks for the CPI-R module [needs numpy]
  economics/dynamic_cpi_r/drafts/dynamic_inflation_weight.py draft: Kalman + constraint pressure + shocks [needs numpy+scipy]
  economics/dynamic_cpi_r/drafts/iteration_module.py draft fragment of DynamicCPI_R [fragment]
  economics/dynamic_cpi_r/examples/api.json      example API response
  economics/dynamic_cpi_r/README.md              Dynamic CPI-R transfer notes
  economics/money_labor/Efficiency-dynamic.md    SYSTEM OPTIMIZATION: EFFICIENCY AS INTEGRAL, NOT SNAPSHOT
  economics/money_labor/For-AI.md                TAF CORE SPECIFICATION - AI INTEGRATION SHEET
  economics/money_labor/Knowledge.md             EVERY TOOL EMBODIES DESIGN KNOWLEDGE
  economics/money_labor/Level1-audit.md          TAF LEVEL 1 AUDIT - PRELIMINARY ASSESSMENT
  economics/money_labor/LLM-module.md            TAF Module: Embodied Energy & Knowledge Preservation
  economics/money_labor/README.md                Thermodynamic Accountability Framework (TAF)
  economics/money_labor/Summary.md               PART 1: OVERVIEW (README)
  economics/regenerative_economics.md            REGENERATIVE ECONOMY FRAMEWORK
  glossary.md                                    every named quantity and equation, with file
  readme_archive/README_before_2026-11-03.md     previous README, verbatim
  governance/coupled_governance.md               coupled-state governance model
  governance/governance_no_ego.md                anti-ego symbiotic governance
  governance/regulatory.md                       regulatory framework, standards gap analysis
  governance/safety.md                           safety principles
  governance/tripartite.md                       tripartite governance (React component source)
  theory/adaptive_resilience_mesh.md             Adaptive Resilience Mesh (ARM)
  theory/atomic_accounting_notes.md              atomic accounting notes
  theory/egs2.md                                 Entropy Governance System -- Research Directions & Theoretical Extension
  theory/egs3.md                                 Signal-Fire field reporting guide
  theory/egs_core.md                             Entropy Governance System -- Core Architecture & Diagnostic v2.0
  theory/entropy_example.md                      entropy kernel design spec
  theory/example.md                              a route, stripped of narrative
  theory/ferret_fieldlink.md                     Logic-Ferret  TAF Field Link
  theory/formal_closure.md                       The Formal Closure: Compression, Admissibility, and Decoupling
  theory/functional_epistemology_framework.md    FUNCTIONAL EPISTEMOLOGY FRAMEWORK v0.1
  theory/gaps.md                                 known limitations
  theory/haas_fieldlink.md                       HAAS-Q  TAF Field Link
  theory/integration.md                          prevented-incident logging, tools integration
  theory/knowledge_polytensor.md                 KNOWLEDGE POLYTENSOR
  theory/layer0.md                               layer 0 concepts (JSON-style)
  theory/lhri.md                                 Longitudinal Human Resilience Index
  theory/lhri_addendum.md                        ADDENDUM | Section 7: Potential Extensions and Formalization
  theory/lhri_dashboard.md                       LHRI dashboard (React component source)
  theory/manifold_framework.md                   manifold framework
  theory/notes.md                                working theory notes
  theory/seed.md                                 SEED AI -- Minimal Viable Regenerative Intelligence
  theory/signal_distortion.md                    Signal Distortion Catalog
  theory/signal_distortion_extended.md           signal distortion catalog, extended
  theory/theory.md                               liability routing and pre-emptive causal exclusion
  worker_side_ledger_road_driver.md              worker-side cost-of-access ledger (verbatim) [do not edit, sha256 pinned]

game_theory/
  information_completeness_audit.py              'rational actor' needs complete information
  internal_consistency_danger_audit.py           internal consistency without reality checks
  mathematical_proof_vs_physical_reality.py      proof vs physical reality
  proof-did.txt                                  author context for the proof pipeline
  proof-pipeline.py                              6-module proof pipeline [RED: AttributeError aristotelian_logic]
  proof-pipelineV2.py                            12-module proof pipeline [RED: AttributeError aristotelian_logic]
  proof-results.json                             pipeline results
  proof-resultV2.json                            V2 results
  rationality_audit.py                           What does rational actor actually mean? Under what conditions?

in_progress/
  banking_thermodynamic_audit.py                 draft: banking infrastructure energy cost [draft: does not parse (smart quotes)]
  build_priority_notes.md                        build roadmap
  eroi_real_time_audit.py                        draft: real-time EROI price vector [draft: does not parse (smart quotes)]
  gravity_energy_note.md                         note: gravity storage on a grade
  serpentine_grade_esp_notes.md                  ESP rollover trigger on serpentine grades

investment_distribution/
  interface.py                                   holdings + regeneration-cost liability interface
  README.md                                      who holds capital, who pays regeneration

knowledge/
  application_builder.py                         Knowledge Liberation Module 3: Build with the study
  edge_explorer.py                               Knowledge Liberation Module 2: Generate the questions the study DID NOT
  interactive_navigator.py                       Knowledge Liberation Module 4: Spatial navigation through the playground
  knowledge_liberation.py                        ORCHESTRATOR: the practice itself
  README.md                                      knowledge-liberation pipeline
  recontextualizer.py                            Knowledge Liberation Module 6: Plug YOUR context in
  scope_mapper.py                                Knowledge Liberation Module 1: Map what a study ACTUALLY measured
  shadow_catalog.py                              Knowledge Liberation Module 5: A growing library of silence patterns

labor_thermodynamics/
  core/attribution_sim.py                        Thermodynamic attribution simulation
  core/full_system.py                            Full coupled attribution/trust/burnout/reform simulation
  core/sector_shortage.py                        shortage across functional and captured facilities
  core/sensitivity_sweep.py                      Run the attribution sim across a grid of parameters to see how
  core/skill_measurement.py                      Extension addressing the skill/certification mismatch
  core/trust_decay.py                            trust decay model
  driver_hours_evidence_register.py              what is known / unread / unmeasured on driver hours
  failure_modes.md                               L1-L5 mechanisms
  measurement_problem.md                         metrology critique
  operator_regulation_audit.py                   body self-regulation loops vs automation
  README.md                                      five compounding workforce-measurement failures
  skill_apparatus/cross_domain_transfer.py       Cross-domain transfer assessment -- the salvage engineer signal
  skill_apparatus/failure_mode_library.py        Diagnostic-under-adversity assessment
  skill_apparatus/observation_protocol.py        Direct-observation skill assessment
  skill_apparatus/provenance_log.py              Skill lineage tracking
  skill_apparatus/teaching_demonstration.py      Teaching capacity assessment

metrology/
  assumption_bias_detector.py                    Identify FRAMEWORK-level bias in scientific claims, beyond the
  atlantic_hurricane_audit_registry.md           hurricane audit registry
  calibration_curve_builder.py                   Build SurrogateCalibrationCurves from modern dual-stream data, then
  cascade_coupling_framework_2026.py             singularity tracking + higher-order coupling
  cognitive_cohort_comparison.py                 COGNITIVE CAPACITY COHORT COMPARISON -- 18 AND UNDER
  constraint_filter_architecture.py              Sort models, frameworks, and regulations into containers by their [needs py3.10]
  constraint_recovery_framework.py               Recover the physical constraints encoded in pre-1900 engineering
  constraint_recovery_framework_v03_patch.py     Adds four structural defenses against the category errors observed
  constraint_to_seed.py                          Bridge module: PhysicalConstraint -> 40-bit octahedral seed -> (optional
  corruption_chain.py                            corruption chain
  cross_domain_synthesis.md                      synthesis across the domain audits
  domain_convergence_matrix.py                   Formalizes the convergence pattern across 5 completed domain audits
  drought_metrology_demo.py                      Show the metrology problem in US drought data [needs numpy]
  earth_systems_constraint_integration_2026.py   Constraint layer module for earth-systems-physics coupled differential e
  flood_metrology_demo.py                        Show the flood metrology problem with real data, plus the [needs numpy]
  hurricane_metrology_demo.py                    Show the metrology problem in Atlantic hurricane data with real numbers [needs numpy]
  in_progress.md                                 metrology backlog
  indigenous_encoding_recovery.py                Recovery of measurement signal from non-instrumental encoding chains
  institutional_audit.py                         Cross-domain audit of institutional models against the full premise
  metrological_audit_framework.py                CANONICAL DATA STRUCTURE for Earth-systems measurement audit
  observer_bias.py                               observer bias vs instruments; recover old records
  oil_extraction_thermodynamic_cascade_audit.py  Audit module exposing the metrology failures in current oil-extraction
  orbital_octa_v2.py                             Orbital-Octahedral Fractal Core: Field-Based Growth v2 [needs numpy]
  pre1900_engineering_registry.py                Catalog of observation-based engineering systems that predate
  preservation_audit.py                          Format-translation information loss audit
  pronoun_dictionary_analysis.py                 DICTIONARY HISTORICAL ANALYSIS -- PRONOUN DEFINITION SHIFT
  pronoun_shift_degradation_evidence.py          PRONOUN SHIFT AS IDENTITY-MARKING MECHANISM
  README.md                                      metrology overview
  seed_to_constraint.py                          Reconstruction decoder. Takes a 40-bit ConstraintSeed (or its binary
  substrate_damage_audit.py                      Audit module flagging when behavioral, psychological, and collapse-predi
  tornado_metrology_demo.py                      Show the metrology problem in US tornado data with real numbers [needs numpy]
  training_data_degradation_audit.py             AUDIT FRAMEWORK -- TRAINING DATA DEGRADATION DETECTION
  translation_layer.py                           Parse institutional Earth-systems datasets into canonical vector
  trend_corruption_calculator.py                 Given measurement-layer corruption and framework-layer corruption,
  us_drought_audit_registry.md                   drought audit registry
  us_flood_audit_registry.md                     flood audit registry
  us_wildfire_audit_registry.md                  wildfire audit registry
  warning_time_audit.py                          warning-time audit

money_distribution/
  interface.py                                   stratification axes, incidence interface
  README.md                                      per-receiver p_i decomposition of the Money Equation

political_audit/
  ai_economic_forecast_audit_2026.py             Compares published institutional economic forecasts against measurable
  audit_protocol.md                              audit protocol v1.0 for political terms
  autonomous_freight_audit.py                    Constraint-layer audit of the autonomous long-haul freight narrative aga
  business_resilience_framework.py               Self-audit framework for individual businesses to measure their own
  c_cam_calculator.py                            camouflage score (C_cam)
  consensus_speed_audit.py                       Thermodynamic framework addition -- compare claimed efficiency
  continuity_gate.py                             continuity sub-gate for the audit trail [fragment: missing dataclass import]
  institutional_audit_protocol.py                Executable form of the Institutional Thermodynamic Audit Protocol
  multi_model_peer_review_2026.py                AI-to-AI peer review framework. Independent models with different
  municipal_resilience_framework.py              Restructures municipal/township incentive systems so they
  Pull_Request.md                                methodology submission template
  README.md                                      Six Sigma for governance
  regulation_lcd_incentive_audit.py              LCD regulation / induced deficit / incentive cycling
  standardization_audit.py                       Audits any claim that standardization worked by measuring
  substrate_audit.py                             Five-gate audit for studies and institutional claims
  success_specification_validator.py             success as fluidity across coupled layers
  transportation_automation_audit.py             Pre-deployment audit framework for transportation automation systems
  validation_timeline_audit_2026.py              Quantifies how long a forecast should take to validate, given the

schemas/
  eval/__init__.py                               package marker
  eval/negative_space.json                       negative-space ledger (eval data, not training)
  eval/trapdoors.json                            6 buried-shear-plane scenarios
  README.md                                      upstream/ vs eval/ split
  upstream/__init__.py                           package marker
  upstream/bridge_contract_manifest.json         verbatim mirror: 18 bridge domains
  upstream/distributional_contract.py            stable surface: money/capital distribution
  upstream/earth_physics_contract.py             Earth-Systems-Physics Contract -- stable surface of the
  upstream/geometric_bridge_contract.py          Geometric-Bridge Contract -- stable surface of the Geometric-to-Binary
  upstream/logic_ferret_contract.py              Logic-Ferret Contract -- stable surface of Logic-Ferret's schema_contrac
  upstream/mathematic_economics_contract.py      Mathematic-Economics Contract -- stable surface of the 13 canonical
  upstream/metabolic_accounting_contract.py      Metabolic-Accounting Contract -- stable surface of the 4 canonical
  upstream/trust_exit_contract.py                Trust-Exit Contract -- stable surface published by trust-exit-model

seeam/
  meritocracy_errors.md                          meritocracy claims, examined
  metrics_spec.md                                SEEAM metrics spec
  protocol.md                                    SEEAM protocol v1.0
  README.md                                      SEEAM overview
  seeam_audit.py                                 'people are our greatest asset' as a physical claim

simulations/
  admissibility_field_sim.png                    output figure
  admissibility_field_sim.py                     Admissibility Field Simulation [needs numpy+matplotlib]
  biological_response_infrastructure.py          Distributed infrastructure with local constraint sensing and immediate [needs py3.10]
  cognitive_decoupling_sim.png                   output figure
  cognitive_decoupling_sim.py                    Cognitive Decoupling Simulatio [needs numpy+matplotlib]
  emergent_federation.py                         EMERGENT SEED-AI + COMMUNITY FEDERATION [needs numpy+matplotlib]
  federation.py                                  100k-node federation [needs numpy+matplotlib]
  full_coupled_system.py                         NODE INTEGRATED -- Full coupled system [needs numpy+matplotlib]
  lhri_sim.py                                    Longitudinal Human Resilience Index sim [needs numpy+networkx]
  liability_routing_sim.png                      output figure
  liability_routing_sim.py                       Liability Routing & Schema De [needs numpy+matplotlib]
  loop_6_ai_default_prior_distortion.py          AI default-prior distortion loop (Monte Carlo)
  monolith_brittleness.py                        Falsifiable framework comparing monolithic systems
  monte_carlo_resilience_sim.py                  Stochastic comparison of two response architectures under randomized
  node_v3_ipi.py                                 NODE v3 -- Intergenerational Production Integration [needs numpy+matplotlib]
  refinery_dependency_graph.py                   Recursive dependency audit for U.S. refining capacity
  schema_evolution_sim.png                       output figure
  schema_evolution_sim.py                        Schema Evolution Simulation [needs numpy+matplotlib]
  seed_sim.py                                    community + seed-AI network [needs numpy+matplotlib]
  taf_composite.png                              12-panel composite from taf_master
  taf_master.py                                  Master Orchestrator [needs numpy+matplotlib]
  taf_primitives.py                              Shared Primitives
  valuation_decoupling_sim.png                   output figure
  valuation_decoupling_sim.py                    Valuation Decoupling Simulatio [needs numpy+matplotlib]

tools/
  chat_paste_check.py                            detect chat-paste contamination in .py
  chat_paste_fix.py                              fix the mechanical subset of it
  initial_sweep_findings.txt                     findings of the first sweep (2026-05-02)
  README.md                                      repo-hygiene scripts
  repo_guard.py                                  pre-merge null-guard, three checks

visualizations/
  attribution_sim.jsx                            labor attribution sim (React)
  cold_idle_cost_2026.html                       cold idle cost calculator
  conflict_sim.jsx                               conflict sim (React)
  labor_audit_protocol.html                      labor audit protocol (rendered)
  sim3.jsx                                       simulation component (React)
```

---

## 3. How to run

```text
python        3.10+ for the whole repo (6 files evaluate X | None at runtime)
              3.9+  for the rest (runtime list[...] / dict[...])
              tested: 3.11, 3.13; 3.10 not tested
deps          stdlib only, except files tagged `needs ...` above
              (numpy; matplotlib for simulations/; networkx for lhri_sim;
               scipy for one CPI draft)
```

Self-checks (a run with exit 0 is the check):

| Command | What it checks | Status 2026-11-03 |
| --- | --- | --- |
| `python core/dcea.py` | DCEA calculator selftest | 16/16 pass |
| `python core/dcea.py --ledger` | road-driver ledger recompute | prints both readings |
| `python calibration/test_calibration.py` | calibration falsifiers | 11 tests OK |
| `python calibration/test_audit_family.py` | audit-family modules | RED: 1 fail, 26 errors (moved schema path) |
| `python core/atbs/test_v2.py` | functional detector | needs numpy |
| `python docs/economics/dynamic_cpi_r/code/test_dynamic_cpi_indicator.py` | CPI-R | needs numpy |
| `python metrology/orbital_octa_v2.py` | 6 engine self-tests | needs numpy |
| `python tools/chat_paste_check.py` | chat-paste contamination | exit 0 |
| `python tools/repo_guard.py` | null-guard checklist | exit 0 |

Every other `.py`: `python path/to/file.py` runs its demo or smoke test.
Only `core/dcea.py` mentions `--selftest`; it runs the selftest by default.

---

## 4. Conventions

| Mark | Meaning |
| --- | --- |
| `OBSERVED` | seen or measured directly |
| `DERIVED` | computed or read from a source |
| `PROPOSED` | a rule or model, not yet tested |
| trailing `*`, `**` | thin volume (few sources or instances) |
| scope stamp | date, place, rules in force, source on every number |
| `PENDING` | unmeasured slot; counted, never set to 0 |
| `GAP` | no published measure exists |

---

## 5. Worked cases

**WTI barrel (skeleton)** — [docs/DCEA_v0.1.md](docs/DCEA_v0.1.md) section 5.

```text
barrel
 |-- exploration (R7 dry work) ........ OBSERVED   numbers PENDING
 |-- finance overhead (R8) ............ OBSERVED   PENDING
 |-- drilling equipment, labor ........ OBSERVED   PENDING
 |-- trucking (trips per well) ........ OBSERVED   PENDING
 |-- digital overhead (R2) ............ OBSERVED   PENDING
 |-- produced water (water:oil) ....... OBSERVED   PENDING
 |-- corrosion (R6), failed automation (R5), event rechecks
 |-- gathering + pipeline ............. PENDING
 '-- refining ......................... PENDING
```

**Road-driver ledger** —
[docs/worker_side_ledger_road_driver.md](docs/worker_side_ledger_road_driver.md),
recomputed from raw inputs in [docs/DCEA_checks.md](docs/DCEA_checks.md).

| Quantity | From raw inputs |
| --- | --- |
| worker-paid cost of access | $86.49–131.91 / day |
| per year (250 road days) | $22,403–34,231 |
| share of BLS median wage $58,640 | 38.2–58.4% |

Floor only: filters PENDING; proper nutrition and every section-4 cost excluded.

---

## 6. Open gaps

- PENDING items: [docs/DCEA_checks.md](docs/DCEA_checks.md).
- FAO and World Bank hosts not reachable from the build environment; no figure re-pulled.
- CoHD PPP base year: PENDING.
- Road-driver filters and section-4 costs: PENDING.
- WTI node numbers: PENDING, each needs a stamp.
- Label-check thresholds and the R4 common-denominator method: open (DCEA section 7).
- Broken today: two ledger paths into `schemas/eval/`, one test import into
  `schemas/upstream/`, two drafts that do not parse, one fragment
  (tags in the tree above).

---

## 7. License and authorship

CC0 1.0 Universal ([LICENSE](LICENSE)). Co-authored.
