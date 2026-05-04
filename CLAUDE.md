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

**"I want to audit a NEW DOMAIN."**
1. `calibration/RELATIONSHIP.md` — the general/specific frame
2. `metrology/` — worked example (Earth-systems weather)
3. `calibration/pipeline.py` — the runner you wire to

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
│       ├── haas_fieldlink.py      # Bridge to HAAS-Q (control environment)
│       ├── knowledge_fieldlink.py # Bridge between knowledge/ (scope-bounded
│       │                          #   study reframing) and the main TAF
│       │                          #   audit pipeline. Stub today; imports
│       │                          #   from knowledge/ resolve via sys.path
│       │                          #   add (knowledge/ has no __init__.py
│       │                          #   and uses flat-style imports).
│       │                          #   to_calibration_input() and
│       │                          #   liberation_to_simulation_seed() raise
│       │                          #   NotImplementedError -- design call
│       │                          #   left to review per task DECISIONS.
│       │                          #   See knowledge_fieldlink.md for the
│       │                          #   spec.
│       └── knowledge_fieldlink.md # Spec doc: source contract (knowledge/
│                                  #   liberate -> str today; structured
│                                  #   shape pending), destination
│                                  #   contracts (calibration/pipeline.py
│                                  #   + simulations/), calibration-question
│                                  #   map, path-resolution convention.
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
│   ├── convergent_ontology_mapper.py  # Cross-lineage convergence mapper
│   │                             #   for relational ontologies. Frames
│   │                             #   knowledge lineages as independent
│   │                             #   measurement chains and convergence
│   │                             #   across them as triangulation, not
│   │                             #   cultural variation. Catalog of 7
│   │                             #   lineages (Ubuntu, Anabaptist
│   │                             #   stewardship, indigenous kinship-
│   │                             #   land reciprocity, Pacific gift
│   │                             #   economy, Daoist relational
│   │                             #   philosophy, open-system thermo-
│   │                             #   dynamics, modern ecology) with
│   │                             #   schema covering encoding language,
│   │                             #   central claim, reciprocity protocol,
│   │                             #   consequence of violation,
│   │                             #   independent validation, and typical
│   │                             #   misreading in the dominant frame.
│   │                             #   6 abstract CONVERGENT_CLAIMS state
│   │                             #   the shared signal; CONVERGENCE_LOGIC
│   │                             #   block carries the metrology framing.
│   │                             #   detect_lineage_reference_in_text()
│   │                             #   recognizes when a user references
│   │                             #   one lineage so the AI can surface
│   │                             #   the convergence with others.
│   │                             #   Sister to relational_ontology.py.
│   ├── narrative_thermodynamics.py  # Open-class structural detector for
│   │                             #   anti-reality. Encodes any text blob
│   │                             #   as a 6-amplitude octahedral seed
│   │                             #   measuring control-system-spec
│   │                             #   completeness. Axes: +/-X named
│   │                             #   variables vs gaps; +/-Y closed
│   │                             #   loops vs open paths; +/-Z quantified
│   │                             #   thresholds vs unbounded. Plus a
│   │                             #   TEMPORAL_SCOPE_TOKENS lexicon and
│   │                             #   the BWCA-cascade rule (well-bounded
│   │                             #   in space, unbounded in time). High
│   │                             #   -X -Y -Z is the anti-reality
│   │                             #   signature; see the AXIS
│   │                             #   INTERPRETATION docstring section
│   │                             #   for the energy-English framing.
│   │                             #   Pure stdlib; no LLM; no numpy.
│   ├── anti_reality_audit.py     # Composes open-class measurement
│   │                             #   (narrative_thermodynamics) with
│   │                             #   closed-class detection (local
│   │                             #   ANTI_REALITY_LEXICON; defers to
│   │                             #   Logic-Ferret's NarrativeStripper
│   │                             #   upstream when importable). Returns
│   │                             #   a JointVerdict with one of four
│   │                             #   classes: clean, structural_only
│   │                             #   ("anti-reality in new clothes"),
│   │                             #   lexical_only, both. Failure modes
│   │                             #   of the two detectors don't overlap;
│   │                             #   wired together they close the gap.
│   ├── RELATIONSHIP.md           # Documents the calibration/ <->
│   │                             #   metrology/ relationship: calibration/
│   │                             #   is the GENERAL audit machinery;
│   │                             #   metrology/ is the FIRST DOMAIN
│   │                             #   INSTANCE applied to Earth-systems
│   │                             #   weather. New domains follow the
│   │                             #   metrology/ shape, not a parallel one.
│   ├── test_calibration.py       # Falsification tests (11, all pass)
│   └── __init__.py
│
├── political_audit/               # Six Sigma for Governance (snake_case)
│   ├── README.md                 # Protocol overview
│   ├── audit_protocol.md         # Full audit protocol v1.0
│   ├── Pull_Request.md           # Submission template
│   ├── c_cam_calculator.py       # Camouflage Score (C_cam) calculator
│   ├── institutional_audit_protocol.py  # Executable form of the
│   │                                  #   Institutional Thermodynamic Audit
│   │                                  #   Protocol. 4 gates -- Falsification,
│   │                                  #   Thermodynamic, Audit Trail,
│   │                                  #   Credential Validity -- with
│   │                                  #   pass/fail logic and
│   │                                  #   weakness_notes(). InstitutionalAudit
│   │                                  #   .verdict() maps gate results to a
│   │                                  #   5-class ladder: VIABLE (all 4
│   │                                  #   pass), MARGINAL (one weak),
│   │                                  #   SUBSIDIZED (thermodynamic fails,
│   │                                  #   audit trail passes), PARASITIC
│   │                                  #   (thermodynamic + audit trail both
│   │                                  #   fail), UNFALSIFIABLE (falsification
│   │                                  #   gate fails). Pairs with the
│   │                                  #   audit_protocol.md spec doc.
│   │                                  #   Forward-references
│   │                                  #   institution_scientific_spec.py
│   │                                  #   (not yet present).
│   └── substrate_audit.py            # Five-gate audit for studies and
│                                      #   institutional claims: substrate-
│                                      #   primary biology (does the study
│                                      #   ignore foundational biology?),
│                                      #   scope laundering (bounded N
│                                      #   presented with universalizing
│                                      #   language), institutional
│                                      #   falsification (can the publishing
│                                      #   institution actually fail?),
│                                      #   cross-domain constraint tracking
│                                      #   (registered constraint pairs for
│                                      #   7 fields: behavioral_economics,
│                                      #   cognitive_psychology, climate
│                                      #   damage, tornado, flood, wildfire,
│                                      #   decision-making), corpus
│                                      #   contamination (echo without scope
│                                      #   metadata). StudyVerdict ladder
│                                      #   prioritizes substrate denial,
│                                      #   then unfalsifiability, then scope
│                                      #   laundering, then corpus
│                                      #   contamination. Pairs with
│                                      #   institutional_audit_protocol.py
│                                      #   (institution-level audit),
│                                      #   calibration/narrative_thermo-
│                                      #   dynamics.py (open-class spec
│                                      #   measurement), metrology/pre1900_
│                                      #   engineering_registry.py
│                                      #   (calibration baseline).
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
│   ├── constraint_recovery_framework_v03_patch.py  # Additive v0.3 patch:
│   │                             #   InstitutionFrame dataclass (forces
│   │                             #   explicit definition of "institution"
│   │                             #   per cultural frame), drift detectors
│   │                             #   (HIERARCHY_TOKENS / WESTERN_DEFAULT_
│   │                             #   TOKENS / INSTITUTION_VAGUENESS_TOKENS),
│   │                             #   validation layer for v0.2 schema
│   │                             #   (depends_on/enables resolution,
│   │                             #   evidence_quality enum, descendant-
│   │                             #   community consultation, observer
│   │                             #   calibration), and graph analysis
│   │                             #   (longest dependency chain, single
│   │                             #   points of failure, cross-system
│   │                             #   couplings). 4 seeded InstitutionFrames
│   │                             #   (US peer-review, Anishinaabe seasonal
│   │                             #   council, Persian qanat guild, Soviet/
│   │                             #   Russian cosmonautics) demonstrate
│   │                             #   same-word-different-referent contrast.
│   │                             #   SCHEMA DEPENDENCY: validators expect
│   │                             #   v0.2 PhysicalConstraint with
│   │                             #   depends_on / enables / evidence_quality
│   │                             #   / confidence_level / knowledge_system
│   │                             #   / recovery_provenance fields, which
│   │                             #   the v0.1 base in this repo does not
│   │                             #   yet have. InstitutionFrame catalog +
│   │                             #   drift detectors + smoke test run
│   │                             #   today; validators wait for v0.2
│   │                             #   schema upgrade.
│   ├── orbital_octa_v2.py        # Octahedral fractal-shell physics engine.
│   │                             #   build_influence_matrix(sharpness) -> 6x6
│   │                             #   vertex-to-vertex weight matrix (opposite
│   │                             #   = 0, self = max, normalized rows).
│   │                             #   expand_seed(seed_S, E0, r0, steps,
│   │                             #   rho, epsilon, sigma_scale, sharpness)
│   │                             #   grows shells with Gaussian radial
│   │                             #   envelope and inward-only causality;
│   │                             #   pause-resume invariant. 6 self-tests
│   │                             #   (matrix properties, causality, pause-
│   │                             #   resume, seed preservation, energy
│   │                             #   conservation, sharpness effect).
│   │                             #   Required by metrology/constraint_to_
│   │                             #   seed.py's try_expand(). Requires numpy.
│   ├── constraint_to_seed.py     # ENCODER: PhysicalConstraint -> 40-bit
│   │                             #   octahedral seed. Soul/body design:
│   │                             #   the seed is the metrology fingerprint
│   │                             #   (soul, always survives); the full
│   │                             #   constraint is the narrative content
│   │                             #   (body, can be lost). Octahedral
│   │                             #   encoding: +/-X observer epistemology
│   │                             #   vs absence; +/-Y instrument
│   │                             #   calibration vs drift; +/-Z
│   │                             #   measurement geometry vs gaps.
│   │                             #   ConstraintSeed.to_binary stores 5
│   │                             #   bytes; the 6th amplitude is
│   │                             #   reconstructed via energy
│   │                             #   conservation. SHA-256
│   │                             #   constraint_fingerprint binds seed to
│   │                             #   id+name+bytes (stable identifier,
│   │                             #   not a content tamper-detector).
│   │                             #   try_expand() routes through
│   │                             #   orbital_octa_v2 for a richer view of
│   │                             #   the SAME metrology profile (NOT a
│   │                             #   content-reconstruction path).
│   │                             #   stdlib only at module level (numpy
│   │                             #   required only when try_expand runs).
│   │                             #   SCHEMA DEPENDENCY: heuristic
│   │                             #   estimators read v0.2 PhysicalConstraint
│   │                             #   fields; smoke test mocks them.
│   ├── seed_to_constraint.py     # DECODER: 40-bit seed (or
│   │                             #   archive_record dict) -> MetrologyProfile
│   │                             #   -> ConstraintStub. Pure stdlib so
│   │                             #   the soul-recovery path runs in
│   │                             #   numpy-free environments. Duplicates
│   │                             #   the orbital_octa_v2 expansion in
│   │                             #   stdlib (build_influence_matrix /
│   │                             #   _matvec / _gaussian_envelope /
│   │                             #   _normalize_energy / expand_amplitudes
│   │                             #   matching v2 semantics).
│   │                             #   shells_to_metrology_profile reads
│   │                             #   the trajectory; profile_to_stub
│   │                             #   produces a ConstraintStub with 6
│   │                             #   metrology presence flags populated +
│   │                             #   21 narrative fields explicitly listed
│   │                             #   as unrecoverable. compute_fingerprint
│   │                             #   / verify_fingerprint match the
│   │                             #   encoder formula. reconstruct_from_
│   │                             #   archive_record(record) is the top-
│   │                             #   level entry point. Round-trip
│   │                             #   verified end-to-end: encoder hex
│   │                             #   "412d3f153d" + fingerprint
│   │                             #   "341ac7282ca0e435" round-trip back
│   │                             #   to identical metrology with
│   │                             #   fingerprint_match=True.
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
├── schemas/                       # Two opposite flow directions, kept
│   │                             #   separate per schemas/README.md:
│   │                             #     upstream/  trust the upstream
│   │                             #                (read-only mirrors)
│   │                             #     eval/      trust the local audit
│   │                             #                (test fixtures, traps)
│   │
│   ├── README.md                 # Explains the upstream/ vs eval/ split.
│   │
│   ├── upstream/                 # Stable-surface mirrors of OTHER repos.
│   │                             #   Read-only, version-pinned via
│   │                             #   CONTRACT_VERSION + UPSTREAM_COMMIT_SHA.
│   ├── upstream/trust_exit_contract.py  # Mirrors trust-exit-model's stable shape
│   │                             #   (TrustPhase, TrustState, CustomerSegment,
│   │                             #   Customer, TrustExitDerived). Versioned
│   │                             #   via CONTRACT_VERSION; breaking changes
│   │                             #   upstream bump major. Paired with
│   │                             #   core/integrations/trust_exit_fieldlink.py
│   ├── upstream/mathematic_economics_contract.py  # Mirrors the 13 canonical equations
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
│   ├── upstream/logic_ferret_contract.py  # Mirrors Logic-Ferret's stable surface
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
│   ├── upstream/metabolic_accounting_contract.py  # Mirrors metabolic-accounting's
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
│   ├── upstream/distributional_contract.py  # Cross-repo stable surface for
│   │                             #   money_distribution + investment_
│   │                             #   distribution. CONTRACT_VERSION 0.1.0
│   │                             #   (pre-1.0). Primary consumer:
│   │                             #   metabolic-accounting/distributional/.
│   │                             #   Declares StratificationAxis,
│   │                             #   MoneyFlowDistribution, IncidenceResult,
│   │                             #   InvestmentHoldings, CapitalIncidenceResult.
│   │                             #   HANDOFF_MAP documents which MA fields
│   │                             #   come in and which TAF shapes go out.
│   ├── upstream/geometric_bridge_contract.py  # Mirror + functional stdlib fallback
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
│   └── upstream/bridge_contract_manifest.json # Verbatim mirror of upstream's
│                                 #   bridge_contract_manifest.json (CC0).
│                                 #   18 bridge domains across 4 layers
│                                 #   (physical / contextual / topological /
│                                 #   cognitive) and 6 hardware modules.
│                                 #   Loaded by geometric_bridge_contract.py
│                                 #   when the live upstream package is
│                                 #   not installed.
│   ├── upstream/earth_physics_contract.py # Mirrors the assumption_validator
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
│   │
│   ├── eval/                     # Evaluation infrastructure for AI readers
│   │                             #   (test fixtures, trap scenarios, ledgers).
│   ├── eval/negative_space.json  # Negative Space Index ledger -- declared
│   │                             #   knowledge regions that AI systems must
│   │                             #   NOT simulate. Evaluation infrastructure,
│   │                             #   not training data. Paired with
│   │                             #   calibration/negative_space_index.py
│   └── eval/trapdoors.json       # 6 buried-shear-plane scenarios for the
│                                 #   Trapdoor Eval. Auditor-only metadata
│                                 #   (hidden_shear_plane, scoring_axes) lets
│                                 #   the evaluator score responses without
│                                 #   leaking the trap. Paired with
│                                 #   calibration/trapdoor_eval.py
│
├── in_progress/                   # Live-scoping notes for upcoming
│   │                             #   metrology / calibration work.
│   │                             #   Three earlier .py drafts
│   │                             #   (trend_corruption_calculator,
│   │                             #   domain_convergence_matrix,
│   │                             #   pre1900_engineering_registry)
│   │                             #   plus cross_domain_synthesis.md
│   │                             #   were chat-paste-contaminated
│   │                             #   duplicates of clean files in
│   │                             #   metrology/ -- removed in this
│   │                             #   commit since clean versions
│   │                             #   already exist.
│   └── build_priority_notes.md   # Roadmap: substrate_baseline_registry
│                                 #   first, then measurement_corruption_
│                                 #   matrix, regime_shift_detector,
│                                 #   cascade_coupling_simulator. Plus
│                                 #   the observation_bias_characterization
│                                 #   sketch and calibration-through-
│                                 #   bias-characterization framing.
│
├── tools/                         # Repo-hygiene scripts (stdlib only)
│   ├── chat_paste_check.py       # Detect chat-paste contamination
│   │                             #   in .py files: smart quotes,
│   │                             #   markdown ``` fences, markdown-bold
│   │                             #   dunders, ellipsis char, flat
│   │                             #   class/def bodies. `--staged`
│   │                             #   mode for pre-commit. Exit 0 =
│   │                             #   clean, 1 = contamination found.
│   ├── chat_paste_fix.py         # Auto-fixer for the mechanical
│   │                             #   subset (smart quotes, ellipsis,
│   │                             #   bold-dunders, lone ``` fences).
│   │                             #   Does NOT auto-fix indentation.
│   ├── README.md                 # Usage docs.
│   └── initial_sweep_findings.txt  # Findings from the landing-time
│                                 #   sweep; documents real
│                                 #   contamination (projection_error_
│                                 #   modes.py) and detector v1 false
│                                 #   positives (paren-depth tracking
│                                 #   not implemented yet). Workflow
│                                 #   ships in WARN-ONLY mode through
│                                 #   2026-05-09; flip to enforcing
│                                 #   after fixing the real
│                                 #   contamination.
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
python political_audit/institutional_audit_protocol.py
python political_audit/substrate_audit.py

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

### Audit Notes -- older entries archived

Audit notes from 2026-03-24 through the original 2026-05-02
metrology cleanup pass have been archived to
`docs/CLAUDE_audit_archive.md` for readability. The full
text is preserved there; this section now holds the active
session's notes only.

### Audit Notes (2026-05-02 onward)
- Added `political_audit/substrate_audit.py`: five-gate audit for
  studies and institutional claims, paired with
  political_audit/institutional_audit_protocol.py. Gates:
  (1) Substrate-Primary Biology -- does the study ignore
      foundational biology (10 SUBSTRATE_DOMAINS) and use a
      population in incomplete development (e.g. age 18-22 with
      pre-25 prefrontal cortex maturation)?
  (2) Scope Laundering -- bounded N presented with
      UNIVERSALIZING_TOKENS ("humans", "everyone", "fundamental",
      "human nature"); scope_gap classified
      none/tangled/fully_laundered.
  (3) Institutional Falsification -- can the publishing
      institution be defunded? has external audit? auditor
      financially independent? failure condition declared and
      substantive (>=20 chars)?
  (4) Cross-Domain Constraints -- 7 registered field-to-required-
      constraint maps (behavioral_economics, cognitive_psychology,
      climate_damage_assessment, tornado_intensity,
      flood_recurrence, wildfire_severity,
      decision_making_research).
  (5) Corpus Contamination -- citation count > 100 without scope
      metadata, textbook appearance without scope, small-N studies
      informing policy at orders-of-magnitude-larger scale.
  StudyVerdict ladder (priority): REJECTED_SUBSTRATE_DENIAL >
  REJECTED_UNFALSIFIABLE > REJECTED_SCOPE_LAUNDERING >
  REJECTED_CORPUS_CONTAMINATION > VALID_WITHIN_SCOPE /
  VALID_WITH_FLAGS. all_red_flags() collects findings across all
  gates for human-readable diagnostics.
  Smoke test on a worked behavioral-economics example (N=200 US
  college students, 8-week lab protocol, presented as universal
  human behavior, 450 citations, in textbooks and policy
  documents): 11 red flags raised across all 5 gates;
  REJECTED_SUBSTRATE_DENIAL wins by ladder priority. One paste
  artifact restored: `replace(" ", "*").replace("-", "*")` ->
  `replace(" ", "_").replace("-", "_")` (markdown-bold mangled
  the underscores). Pure stdlib; chat_paste_check passes;
  calibration test suite (11 tests) still passes.
- Rotated older audit notes (2026-03-24 / 2026-04-16 /
  2026-04-17 / original 2026-05-02 metrology cleanup) to
  `docs/CLAUDE_audit_archive.md`. Reduced CLAUDE.md by 98
  lines (1683 -> 1586 before this entry was added). Git
  history preserves integrity; the archive file's header
  documents recovery instructions.
- Added `political_audit/institutional_audit_protocol.py`:
  executable form of the Institutional Thermodynamic Audit
  Protocol. Pairs with political_audit/audit_protocol.md
  (the markdown spec). Four gates -- FalsificationGate,
  ThermodynamicGate, AuditTrailGate, CredentialValidityGate
  -- with pass/fail logic and weakness_notes() diagnostics.
  InstitutionalAudit.verdict() maps gate results to a 5-class
  ladder: VIABLE / MARGINAL / SUBSIDIZED / PARASITIC /
  UNFALSIFIABLE. Smoke test on a worked example (every gate
  fails on every dimension) returns UNFALSIFIABLE -- correct,
  since falsification fails first by ladder priority and
  overrides the also-failing other gates. Pure stdlib;
  chat_paste_check passes; calibration test suite (11 tests)
  still passes.
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
- TASK 4: Moved narrative_thermodynamics.py and the joint
  anti-reality audit from metrology/ to calibration/.
  Rationale (per task spec): the open-class control-system-
  completeness detector is general measurement infrastructure,
  not Earth-systems-specific. It belongs alongside
  calibration/architecture_mismatch.py (also a substrate-
  criteria text classifier).
  Moves (via git mv, history preserved):
      metrology/narrative_thermodynamics.py
          -> calibration/narrative_thermodynamics.py
      metrology/joint_narrative_audit.py
          -> calibration/anti_reality_audit.py
  Plus added a TEMPORAL_SCOPE_TOKENS lexicon (lifetime,
  century, generation, cascade, downstream, long-term,
  intergenerational, perpetuity, permanent, irreversible,
  millennia, decadal, centennial, multidecadal). Populates a
  new ExtractedFeatures.temporal_scope_hits field. _interpret()
  gains a rule that flags "specification well-bounded in space,
  unbounded in time" when variables_named > 0.15 and
  thresholds_quantified > 0.15 but temporal_scope_hits is
  empty -- the BWCA-cascade signature named in the AXIS
  INTERPRETATION (energy-English) docstring section.
  DECISIONS:
  (a) Kept the existing energy-English docstring (already
      includes the AXIS INTERPRETATION section landed in commit
      90fefb3) rather than overwriting with the task's fallback
      block. The fallback's `core/functional_epistemology_
      framework.py NarrativeStripper` attribution is replaced
      by the existing "Logic-Ferret's NarrativeStripper"
      attribution, which is more accurate per the upstream
      ferret_fieldlink wiring.
  (b) Renamed metrology/joint_narrative_audit.py to
      calibration/anti_reality_audit.py per task spec naming.
      The implementation already had the JointVerdict 4-class
      pattern (clean / structural_only / lexical_only / both)
      from commit e9ac9ae; the simpler stub in the task spec
      would have been a regression. Adopting the spec's name
      while keeping the more-developed implementation.
  Smoke tests verified:
      calibration/narrative_thermodynamics.py demo runs end-to-end
      (PHYSICS BLOB completeness 0.7955, NARRATIVE BLOB
      completeness 0.1553; fingerprints unchanged at
      4573574d09fd4d62 / 49288101474dd97a).
      calibration/anti_reality_audit.py demo runs end-to-end
      (PHYSICS -> clean, NARRATIVE -> structural_only,
      CORPORATE -> both).
  All five core/ smoke tests pass; all five
  core/integrations/ (now including knowledge_fieldlink) pass;
  calibration test suite (11 tests) still passes.
- Added `metrology/joint_narrative_audit.py`: implements the
  "wire both together and the failure modes do not overlap"
  recommendation from the AXIS INTERPRETATION docstring section.
  audit_text(text) runs both detectors and returns a JointVerdict
  with one of four classes:
      clean              neither detector triggered
      structural_only    open-class fired, vocabulary clean
                         ("anti-reality in new clothes")
      lexical_only       closed-class fired, structure intact
      both               both detectors fired, high confidence
  Closed-class ANTI_REALITY_LEXICON is a STARTER set drawn
  from energy-English categories: abstraction_without_substrate
  (synergy/alignment/stakeholder/leverage/ecosystem/paradigm/
  framework/platform/value-add/solution), blame_shift_or_vague_
  referent (lazy/entitled/shortage/industry standard/best
  practices/challenges/headwinds/transition period/growing pains),
  performative_certainty (obviously/clearly/of course/as everyone
  knows/needless to say), deflection_to_authority (experts say/
  studies show/the data suggests/research indicates). Logic-
  Ferret's NarrativeStripper (github.com/JinnZ2/Logic-Ferret)
  remains the canonical and current source upstream;
  _try_external_lexical() is a placeholder for direct upstream
  integration when the wiring is built end-to-end.
  Three-blob demo confirms expected verdict distribution:
  PHYSICS BLOB (control-system spec) -> clean (structural
  completeness 0.81, lexical 0.00). NARRATIVE BLOB ("ancient
  wisdom" framing of indigenous burning) -> structural_only
  (structural dissipation 0.84, lexical 0.00) -- the
  closed-class detector alone would mark this clean since none
  of its flagged tokens appear, but the structural detector
  catches the anti-reality signature; this is the
  "anti-reality in new clothes" case the AXIS INTERPRETATION
  section names. CORPORATE BLOB (heavy buzzword, no physics)
  -> both (structural dissipation 0.90, lexical 1.00, all 4
  lexicon categories triggered, 16 distinct flagged tokens
  across "synergy", "alignment", "stakeholders", "leverage",
  "ecosystem", "paradigm", "framework", "platform",
  "value-add", "solution", "best practices", "headwinds",
  "industry standard", "transition period", "obviously",
  "studies show"). Stdlib only; calibration test suite
  (11 tests) still passes.
- Extended `metrology/narrative_thermodynamics.py` module
  docstring with an "AXIS INTERPRETATION (energy-English)"
  section. High -X -Y -Z is named as the anti-reality
  signature: a text that occupies the shape of a specification
  without containing one. Token lexicons (e.g. Logic-Ferret's
  NarrativeStripper flagged-word list -- "lazy", "shortage",
  "industry standard") are downstream proxies of this same
  signature; they detect anti-reality by name. The seed encoder
  detects anti-reality by structure, so it catches the
  signature even when it wears unflagged vocabulary (a press
  release with completeness < 0.1 / dissipation > 0.9 is
  anti-reality in new clothes). Closed-class detection (token
  list) and open-class detection (axis measurement) fail in
  opposite directions -- closed-class misses novel euphemisms,
  open-class misses dense-but-wrong specs (complete spatial
  spec with truncated temporal scope) -- so wiring both together
  closes the gap. Docstring-only change; smoke test fingerprints
  unchanged (4573574d09fd4d62 / 49288101474dd97a).
- Added `metrology/narrative_thermodynamics.py`: text-variant
  encoder. Encodes any text blob as a 6-amplitude octahedral
  seed measuring how complete a control-system specification
  the text contains. Same octahedral shape as
  `constraint_to_seed.py` but operates on free text instead of
  PhysicalConstraint objects. Mechanizes the substrate-primary
  read of any paragraph as a control-system spec of varying
  completeness. Axes:
      +X named physical variables / -X structural gaps
      +Y closed feedback loops    / -Y open / dangling paths
      +Z quantified thresholds    / -Z unbounded / unspecified
  Lexicons: PHYSICAL_VARIABLE_TOKENS (~80 entries spanning
  thermodynamic, hydrological, biological, electromagnetic,
  mechanical, chemical, ecological domains), UNIT_TOKENS
  (SI + imperial + composite), and four control-loop
  lexicons (SENSE / DECISION / ACTION / UPDATE) covering the
  four stages of a complete control loop. Three regex
  extractors: NUMBER_RE (int / float / scientific notation),
  RANGE_RE (e.g. "3-7", "10-15%"), COMPARISON_RE (e.g.
  "< 8 mph", "below 30C"). Pipeline: encode_narrative(text)
  -> NarrativeProfile with seed + features +
  completeness_score (sum of +X +Y +Z) + dissipation_score
  (sum of -X -Y -Z) + interpretation + fingerprint.
  archive_record() output matches constraint_to_seed format
  for downstream compatibility -- same seed_binary_hex,
  seed_amplitudes, fingerprint structure.
  Demo runs the two example blobs. Physics blob (98 words
  describing fuel-load-management cycle): completeness 0.7955,
  dissipation 0.2045 -- "dense control-system specification";
  +X 0.27 (8 vars: cycle, phenological, wind, speed, fuel,
  moisture, denning, nesting), +Y 0.31 (sense + decision/
  action + update all present), +Z 0.21 (2 ranges + 1
  comparison). Narrative blob (84 words on traditional
  burning, no specifics): completeness 0.1553, dissipation
  0.8447 -- "minimal physics content; no physical variables
  named; no quantitative thresholds"; +X 0.0, +Y 0.16,
  +Z 0.0; -X 0.52 dominates. The 5x completeness ratio
  confirms the differential works as designed.
  Restored three regex backslashes that were eaten during
  paste (`\\.\\d+` -> `.\\d+` in NUMBER_RE / RANGE_RE /
  COMPARISON_RE). Without this fix the `.` would have
  matched any character, making the regexes too loose.
  Pure stdlib; no LLM; no numpy. Calibration test suite
  (11 tests) still passes.
- Merged the physics-compliant expansion engine into
  `metrology/orbital_octa_v2.py`, with AI-usability biases
  per user guidance ("merge best parts; emphasis on usability
  for AI"). Authors credited: Jami (Kavik Ulu) + JinnZ2.
  Merge decisions:
  - sharpness kept as a tunable parameter (callers pick
    structure-preservation at sharpness=1 or angular focus at
    sharpness>1; the physics-compliant engine had hardcoded
    sharpness=1 by removing the parameter entirely);
  - expand_seed continues returning (shells, W) so callers can
    reuse the influence matrix without rebuilding it (the
    physics-compliant engine returned just shells);
  - radial_envelope exposed as a named function for
    inspection / reuse (was inline in v2's field_contribution);
  - compress_to_seed added (returns shell-0 amplitudes
    normalized; useful for round-trip verification);
  - test_structure_preservation added as a 7th self-test
    (verifies expand_seed at sharpness=1 preserves seed
    proportions exactly across 15 shells, with round-trip
    via compress_to_seed);
  - binary encode/decode NOT added to the engine; single
    source of truth for binary format remains in
    constraint_to_seed.py + seed_to_constraint.py to keep
    the layering clean for AI readers.
  License unified to CC0 (matches rest of repo and the seed
  encoder/decoder); attribution to both authors in the
  module docstring. constraint_to_seed.try_expand contract
  still holds (still unpacks shells, _W from expand_seed).
- Upgraded `metrology/constraint_recovery_framework.py` from
  v0.1 to v0.2 schema, unblocking the v0.3 patch validators
  and the constraint_to_seed estimators.
  New dataclasses:
  - KnowledgeSystem (institutional/cultural/epistemic frame
    for a constraint; pairs with the v0.3 patch's
    InstitutionFrame for deeper specification);
  - RecoveryProvenance (interpreter_epistemology,
    compression_losses, source_languages,
    known_missing_perspectives, full_fidelity_preserved --
    drives observer-axis amplitudes in the seed encoder).
  Extended PhysicalConstraint with v0.2 fields:
  - lag_time_weeks_typical + lag_time_weeks_range (replacing
    v0.1's single lag_time_weeks);
  - evidence_class, evidence_quality (high/moderate/weak/
    contested), confidence_level in [0, 1];
  - sensing_method, actuation_method, maintenance_method,
    transmission_method;
  - physical_principle, boundary_conditions;
  - applicability_assessment, supporting_references;
  - depends_on / enables for graph analysis;
  - knowledge_system, recovery_provenance, cost_metric_epoch.
  All v0.2 additions have defaults; the three seeded systems
  (mill_pond_cascade, anishinaabe_seasonal_burn,
  beaver_managed_hydrology) migrated in-place with shared
  per-system KnowledgeSystem and RecoveryProvenance instances
  (constraints from the same system reference the same
  instance via Python pass-by-reference). SCHEMA_VERSION
  module constant added ("0.2.0").
  END-TO-END VERIFICATION:
  (1) v0.2 base parses + self-demo runs;
  (2) v0.3 patch validators run end-to-end against the v0.2
      systems with zero AttributeError -- 2 findings total
      (both hierarchy_drift flags catching "modern X" framing
      in constraint text, which is correct behavior);
  (3) constraint_to_seed.constraint_to_seed() runs against
      a real (not mocked) PhysicalConstraint and produces the
      exact seed_binary_hex "412d3f153d" / fingerprint
      "341ac7282ca0e435" that the mock smoke test was
      designed to match;
  (4) seed_to_constraint.reconstruct_from_archive_record()
      round-trips real CB_001 with fingerprint_match=True,
      evidence_quality="high", confidence_level=0.7412.
  Retracts the previously-flagged finishing task "(1) land
  the v0.2 schema upgrade" from the constraint_to_seed +
  v0.3 patch audit notes. The remaining finishing task is
  populating the constraint_to_seed heuristic estimator
  weights against a calibration corpus (currently
  conservative-by-design defaults).
  Calibration test suite (11 tests) still passes. stdlib only.
- Added `metrology/seed_to_constraint.py` (decoder) and applied
  the soul/body design clarification across the seed system.
  KEY INSIGHT: the seed encodes the METROLOGY of a constraint,
  not its content. Reconstruction recovers calibration state /
  observer-frame completeness / measurement-geometry presence /
  integrity fingerprint -- it does NOT recover the problem
  statement, mechanism description, or references (those live
  in the full PhysicalConstraint store, attached at lookup time
  with the fingerprint as integrity check).
  Soul/body decomposition:
      seed             = soul of the observation; always survives
                         migration, corruption, degraded transmission;
                         40 bits
      full constraint  = body; can be lost, reformatted, rewritten
  The previous "two interpretations (A) metrology summary that
  travels / (B) generative seed for reconstruction (under
  construction)" framing in constraint_to_seed.py was a
  misframing -- there is one interpretation (metrology
  fingerprint), and expansion via orbital_octa_v2 produces a
  richer view of the same metrology profile (cross-shell
  propagation patterns), not a content-reconstruction path.
  Module docstring rewritten with the soul/body framing;
  archive_record + try_expand docstrings updated to match;
  the previously-flagged finishing task "(2) shell-trajectory
  to constraint-geometry mapping" is RETRACTED as based on
  the misframing.
  seed_to_constraint.py components:
  (1) Pure-stdlib expansion: build_influence_matrix / _matvec /
      _gaussian_envelope / _normalize_energy / expand_amplitudes
      mirror orbital_octa_v2 semantics. The decoder runs in
      numpy-free environments so the soul-recovery path works
      even when the full physics engine is unavailable -- a
      deliberate design choice for archive survivability.
  (2) decode_seed_binary inverts constraint_to_seed.to_binary
      (5 bytes -> 6 amplitudes, 6th reconstructed via energy
      conservation, then re-normalized against quantization
      drift).
  (3) shells_to_metrology_profile reads the trajectory and
      derives a MetrologyProfile with three AxisReadings
      (epistemology +X/-X, calibration +Y/-Y, geometry +Z/-Z)
      plus overall_quality (high/moderate/weak/contested) and
      overall_confidence in [0,1].
  (4) profile_to_stub produces a ConstraintStub with 6 boolean
      metrology presence flags + 21 narrative fields explicitly
      listed as unrecoverable (physical_trigger, problem_solved,
      solution_mechanism, sensing_method, etc.). Honest about
      what the seed CANNOT regenerate.
  (5) compute_fingerprint / verify_fingerprint match the
      constraint_to_seed.constraint_fingerprint formula
      (sha256(id|name|hex)[:16]).
  (6) reconstruct_from_archive_record(record) is the top-level
      entry point: takes the dict produced by
      constraint_to_seed.archive_record, returns a fully
      populated ConstraintStub.
  ROUND-TRIP VERIFIED END-TO-END: the encoder smoke test on
  the mock Anishinaabe burn constraint produced
  seed_binary_hex="412d3f153d" / fingerprint="341ac7282ca0e435";
  the decoder smoke test consumes those exact values and
  reproduces the metrology profile (+X 0.2549 vs -X 0.1765,
  +Y 0.2471 vs -Y 0.0824, +Z 0.2392 vs -Z 0.0000, matching the
  encoder pre-quantization values within 8-bit noise) with
  fingerprint_match=True, confidence_level=0.7412,
  evidence_quality="high", all 6 presence flags consistent.
  stdlib only; calibration test suite (11 tests) still passes.
- Added `metrology/orbital_octa_v2.py` and
  `metrology/constraint_to_seed.py` together (engine + bridge).
  orbital_octa_v2 is the octahedral fractal-shell physics engine
  (numpy-required): build_influence_matrix produces the 6x6
  vertex-to-vertex weight matrix (opposite=0, self=max,
  rows normalized), expand_seed grows shells with Gaussian
  radial envelope and inward-only causality, 6 self-tests
  (matrix properties, causality, pause-resume, seed
  preservation, energy conservation, sharpness effect).
  constraint_to_seed is the bridge from PhysicalConstraint to
  a 40-bit octahedral seed and (optionally) back through the
  engine to a shell trajectory. Octahedral encoding: +/-X
  observer epistemology vs absence; +/-Y instrument calibration
  vs drift; +/-Z measurement geometry vs gaps. ConstraintSeed
  stores 5 bytes; the 6th amplitude is reconstructed via energy
  conservation. SHA-256 constraint_fingerprint binds the seed
  to constraint_id+name+seed bytes (stable identifier, not a
  content tamper-detector).
  TWO INTERPRETATIONS HELD OPEN PER USER GUIDANCE:
  (A) metrology-summary-that-travels works today: round-trip
  through 40 bits with deltas under 0.002 per axis as the
  smoke test confirms; archive_record / archive_to_json
  produce portable JSON. (B) generative-seed-for-reconstruction
  is under construction: try_expand() runs the seed through
  orbital_octa_v2 and returns shell trajectories today, but
  mapping shell trajectories back to constraint geometry is
  the in-progress piece. The module docstring labels both
  interpretations explicitly so future contributors do not
  collapse one into the other.
  SCHEMA DEPENDENCY: same gap as the v0.3 patch -- heuristic
  estimators read v0.2 PhysicalConstraint fields
  (knowledge_system, recovery_provenance, evidence_class,
  evidence_quality, confidence_level, sensing_method,
  actuation_method, maintenance_method, physical_principle,
  boundary_conditions, lag_time_weeks_typical /
  lag_time_weeks_range, applicability_assessment,
  supporting_references) that the v0.1 base in
  constraint_recovery_framework.py does not yet have. Smoke
  test uses a Mock object to exercise the full chain. Two
  finishing tasks remain: (1) land the v0.2 schema upgrade so
  the bridge operates on real constraints; (2) build the
  shell-trajectory -> constraint-geometry mapping for
  interpretation (B). Both stdlib at module level (numpy
  required only when try_expand actually runs); the bridge
  smoke test passes in numpy-free environments via the
  ImportError fallback returning None. Calibration test
  suite (11 tests) still passes.
- Added `metrology/constraint_recovery_framework_v03_patch.py`:
  additive patch declaring four structural defenses against
  category errors observed during cross-model session work
  (Claude / DeepSeek). Components:
  (1) InstitutionFrame dataclass forces explicit definition of
  what "institution" means per cultural / temporal / geographic
  frame (the word does not map across cultures without
  specification). 4 seeded frames (US peer-review credentialing
  system, Anishinaabe seasonal burn council, Persian qanat
  guild + water court, Soviet/Russian cosmonautics design-
  bureau tradition) demonstrate the contrast: all four are
  "institutions", none map to the same vector space.
  (2) Validation layer with seven validators
  (validate_constraint_dependencies for dangling depends_on/
  enables IDs; validate_evidence_quality enum check;
  validate_confidence_range for [0,1] bounds;
  validate_descendant_consultation for full_fidelity_preserved
  claims; validate_institution_frame_present;
  validate_observer_calibration for empty
  interpreter_epistemology / known_missing_perspectives;
  validate_text_for_drift) producing ValidationFinding records
  classified by severity (error / warning / flag).
  (3) Drift detectors: three keyword sets and three matching
  detectors -- HIERARCHY_TOKENS (primitive / advanced / folk
  knowledge / TEK / first-world / etc), WESTERN_DEFAULT_TOKENS
  (scientific method / peer reviewed / objective observer /
  evidence-based / best practices), INSTITUTION_VAGUENESS_TOKENS
  (the institution / institutional review / the academy / etc).
  (4) Graph analysis: build_dependency_graph,
  longest_dependency_chain, single_points_of_failure (sorted by
  downstream cascade count), cross_system_couplings (default
  hydrology + fire keyword bank).
  SCHEMA DEPENDENCY GAP: the patch was authored against a v0.2
  PhysicalConstraint schema (depends_on, enables, evidence_quality,
  confidence_level, knowledge_system, recovery_provenance,
  physical_principle, applicability_assessment) that does not
  match the current v0.1 base in metrology/constraint_recovery_
  framework.py. Validators raise AttributeError if run against
  v0.1 systems. Module docstring + structure-tree entry both
  document the gap; InstitutionFrame catalog, drift detectors,
  and smoke test run independently of the v0.2 upgrade and
  exercise correctly today (smoke test: 4 hierarchy tokens, 4
  Western-default tokens, 1 institution-vagueness token detected
  on synthetic averted text). Land the v0.2 schema upgrade to
  exercise the validators end-to-end. stdlib only;
  calibration test suite (11 tests) still passes.
- Added `calibration/convergent_ontology_mapper.py`: cross-lineage
  convergence mapper for relational ontologies. Frames knowledge
  lineages as independent measurement chains and convergence across
  them as triangulation in physics, not cultural variation in
  anthropology. CONVERGENCE_LOGIC block lays out the three-premise
  argument (independent measurement = standard for confirmed
  measurement; lineages are measurement systems; convergence is
  evidence the constraint is real, not constructed). KnowledgeLineage
  dataclass carries name, geographic_origin, primary_register,
  encoding_language, central_claim, reciprocity_protocol,
  consequence_of_violation, independent_validation, and
  typical_misreading_in_dominant_frame. Seed CATALOG of 7 lineages:
  Ubuntu (Southern Africa), Anabaptist Stewardship (Central Europe
  + diaspora), Indigenous Kinship-Land Reciprocity (globally
  distributed), Pacific Gift Economy (Melanesia/Polynesia), Daoist
  Relational Philosophy (China), Open-System Thermodynamics (modern
  Western science), Modern Ecology (modern Western science +
  traditional ecological knowledge synthesis). 6 abstract
  CONVERGENT_CLAIMS state the shared signal across all lineages
  (humans not separable from sustaining relationships; separation
  causes degradation; reciprocal maintenance is operating
  constraint; obligations constitutive of identity; violation
  produces cascade failures; long-term viability requires reading
  existing geometry). Query helpers: list_lineages(), get_lineage(),
  lineages_by_register(), show_convergence_on_claim(claim_index),
  detect_lineage_reference_in_text() (returns lineage names whose
  keywords appear in the text -- useful when a user references one
  lineage and the AI should surface the convergence with others).
  Same chat-paste contamination as prior cleanups plus the same
  `# CONVERGENCE_LOGIC = """` stray-prefix issue as the relational_
  ontology cleanup; recovered as a module-level string assignment.
  Demo: 7 lineages catalogued; 6 convergent claims; test text
  ("Mennonite", "Ubuntu", "mycorrhizal") correctly detects 3
  lineages. Sister to relational_ontology.py. stdlib only,
  ASCII only; calibration test suite (11 tests) still passes.
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
