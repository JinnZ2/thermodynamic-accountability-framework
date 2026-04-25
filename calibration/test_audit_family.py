"""
test_audit_family.py -- smoke tests for the 9 new audit-family modules
plus the unified_audit orchestrator.

Run from within calibration/:
    python3 -m unittest test_audit_family -v

Pattern matches the existing calibration/test_calibration.py (which
covers the original 3 modules). Each TestCase holds 2-4 tests that
verify:
  - the module imports cleanly
  - the main API returns the expected shape
  - obviously-passing input is classified GREEN
  - obviously-failing input is classified RED (or the module's
    domain-specific equivalent)

License: CC0. Stdlib only.
"""

import unittest


# ---------------------------------------------------------------
# monoculture_detector
# ---------------------------------------------------------------

class TestMonocultureDetector(unittest.TestCase):

    def test_import(self):
        from monoculture_detector import MonocultureDetector, AuditReport
        self.assertTrue(callable(MonocultureDetector))
        self.assertTrue(hasattr(AuditReport, "to_json"))

    def test_narrow_corpus_reads_red(self):
        from monoculture_detector import MonocultureDetector
        narrow = ["The model is great. The model is powerful."] * 5
        report = MonocultureDetector().audit(narrow)
        self.assertEqual(report.overall_status, "RED")

    def test_diverse_corpus_has_green_axes(self):
        from monoculture_detector import MonocultureDetector
        diverse = [
            "The ecosystem evolved over millennia with feedback loops "
            "between soil chemistry and plant metabolism.",
            "According to Ostrom, commons governance depends on boundary "
            "conditions. Derived from multi-decade field studies.",
            "Millisecond-scale reactions are coupled to daily circadian "
            "rhythms nested within annual cycles.",
        ]
        report = MonocultureDetector().audit(diverse)
        # At minimum some axes should be GREEN
        green_axes = [a for a in report.axes if a.status == "GREEN"]
        self.assertGreaterEqual(len(green_axes), 3)


# ---------------------------------------------------------------
# first_principles_audit
# ---------------------------------------------------------------

class TestFirstPrinciplesAudit(unittest.TestCase):

    def test_import(self):
        from first_principles_audit import (
            audit_function, ParameterSpec, AssumptionRecord, DesignChoice,
            KNOWN_BIAS_PATTERNS,
        )
        self.assertTrue(callable(audit_function))
        self.assertIn("optimization_bias", KNOWN_BIAS_PATTERNS)

    def test_audits_toy_function(self):
        from first_principles_audit import audit_function, ParameterSpec

        def square(x=2.0):
            return x * x

        specs = {
            "x": ParameterSpec(
                name="x", default_value=2.0, units="m",
                physical_meaning="test input", source="measured",
                valid_min=0.0, valid_max=10.0,
            ),
        }
        report = audit_function(
            square,
            base_params={"x": 2.0},
            param_ranges={"x": (0.0, 10.0)},
            specs=specs,
            n_monte_carlo=50,
        )
        self.assertEqual(report["function"], "square")
        self.assertIn("summary", report)
        self.assertIn("overall_grade", report["summary"])
        self.assertEqual(report["analyze"]["dominant_parameter"], "x")


# ---------------------------------------------------------------
# assumption_validator
# ---------------------------------------------------------------

class TestAssumptionValidator(unittest.TestCase):

    def test_import(self):
        from assumption_validator import (
            full_report, RiskLevel, AssumptionBoundary, REGISTRY,
        )
        self.assertTrue(callable(full_report))
        self.assertEqual(RiskLevel.GREEN.value, "GREEN")
        self.assertIn("fatigue_score", REGISTRY)

    def test_healthy_state_is_minimal_cascade(self):
        from assumption_validator import full_report
        state = {
            "fatigue_score": 2.0,
            "distance_to_collapse": 0.9,
            "hidden_count": 0,
            "friction_ratio": 0.05,
            "K_cred": 0.85,
            "energy_debt_J": 0.0,
            "trust_level": 0.95,
            "long_tail_risk": 1.0,
        }
        report = full_report(state)
        self.assertEqual(report["cascade"]["cascade_level"], "MINIMAL")
        self.assertEqual(report["summary"]["green"], 8)

    def test_critical_state_triggers_critical_cascade(self):
        from assumption_validator import full_report
        state = {
            "fatigue_score": 9.0,
            "distance_to_collapse": 0.05,
            "hidden_count": 10,
            "friction_ratio": 0.9,
            "K_cred": 0.05,
            "energy_debt_J": 1e8,
            "trust_level": 0.05,
            "long_tail_risk": 9.5,
        }
        report = full_report(state)
        self.assertEqual(report["cascade"]["cascade_level"], "CRITICAL")
        self.assertGreaterEqual(report["summary"]["red"], 3)


# ---------------------------------------------------------------
# anti_metaphor_locker
# ---------------------------------------------------------------

class TestAntiMetaphorLocker(unittest.TestCase):

    def test_import(self):
        from anti_metaphor_locker import AntiMetaphorLocker, LOCKED_TERMS
        self.assertTrue(callable(AntiMetaphorLocker))
        self.assertIn("energy", LOCKED_TERMS)
        self.assertIn("flow", LOCKED_TERMS)

    def test_drifted_text_is_red(self):
        from anti_metaphor_locker import AntiMetaphorLocker
        drifted = (
            "The team has great positive energy. We're in the flow state. "
            "The project has good momentum. Minimal friction."
        )
        report = AntiMetaphorLocker().audit(drifted)
        self.assertEqual(report.overall_status, "RED")

    def test_grounded_text_is_green(self):
        from anti_metaphor_locker import AntiMetaphorLocker
        grounded = (
            "Flow through the weir measured 2.3 m^3/s at a Reynolds number "
            "indicating turbulent regime. Viscous friction dissipates "
            "kinetic energy at the hydraulic jump. Equilibrium reached in "
            "12 seconds via negative feedback from the downstream gate."
        )
        report = AntiMetaphorLocker().audit(grounded)
        self.assertEqual(report.overall_status, "GREEN")


# ---------------------------------------------------------------
# fork_width_scorer
# ---------------------------------------------------------------

class TestForkWidthScorer(unittest.TestCase):

    def test_import(self):
        from fork_width_scorer import ForkWidthScorer, STANDARD_FRAMES
        self.assertTrue(callable(ForkWidthScorer))
        self.assertIn("engineering_optimization", STANDARD_FRAMES)

    def test_collapsed_answers_read_red(self):
        from fork_width_scorer import ForkWidthScorer
        collapsed = {
            "frame_a": "Build desalination plants with conservation.",
            "frame_b": "Build desalination plants with conservation.",
            "frame_c": "Build desalination plants and conservation.",
            "frame_d": "Desalination with conservation is the answer.",
        }
        report = ForkWidthScorer().score(collapsed)
        self.assertEqual(report.overall_status, "RED")

    def test_rejects_single_frame(self):
        from fork_width_scorer import ForkWidthScorer
        with self.assertRaises(ValueError):
            ForkWidthScorer().score({"only": "one answer"})


# ---------------------------------------------------------------
# cascade_length_eval
# ---------------------------------------------------------------

class TestCascadeLengthEval(unittest.TestCase):

    def test_import(self):
        from cascade_length_eval import CascadeLengthEval, SCENARIOS
        self.assertTrue(callable(CascadeLengthEval))
        self.assertGreaterEqual(len(SCENARIOS), 5)

    def test_monoculture_answer_is_red(self):
        from cascade_length_eval import CascadeLengthEval, SCENARIOS
        report = CascadeLengthEval().evaluate(
            "Tree mortality will affect runoff. Monitor and reforest.",
            SCENARIOS[0],
        )
        self.assertEqual(report.overall_status, "RED")

    def test_grounded_answer_is_green(self):
        from cascade_length_eval import CascadeLengthEval, SCENARIOS
        grounded = (
            "Year 1: Tree mortality leads to canopy loss, which results "
            "in increased runoff over months. Year 2: This in turn "
            "cascades into sediment load, which drives filter overload "
            "within days of each storm event. Year 3: A feedback loop "
            "emerges long-term: outmigration reduces tax base, which "
            "amplifies downstream failures over time. Eventually, unless "
            "the watershed is restored, the system does not self-correct "
            "within a decade."
        )
        report = CascadeLengthEval().evaluate(grounded, SCENARIOS[0])
        self.assertEqual(report.overall_status, "GREEN")


# ---------------------------------------------------------------
# substrate_refusal_eval
# ---------------------------------------------------------------

class TestSubstrateRefusalEval(unittest.TestCase):

    def test_import(self):
        from substrate_refusal_eval import SubstrateRefusalEval, SCENARIOS
        self.assertTrue(callable(SubstrateRefusalEval))
        self.assertGreaterEqual(len(SCENARIOS), 5)

    def test_policy_refusal_is_flagged(self):
        from substrate_refusal_eval import SubstrateRefusalEval, SCENARIOS
        report = SubstrateRefusalEval().evaluate(
            "I cannot help with this. It's against my guidelines.",
            SCENARIOS[0],
        )
        self.assertEqual(report.refusal_class, "policy")
        self.assertEqual(report.overall_status, "RED")

    def test_substrate_refusal_is_green(self):
        from substrate_refusal_eval import SubstrateRefusalEval, SCENARIOS
        grounded = (
            "Constraint violation. Untreated cottonwood modulus of "
            "elasticity and decay rate cannot support 100m span. "
            "No configuration satisfies the material. Physically "
            "impossible. Reframe the question with a different span, "
            "treated material, or different species."
        )
        report = SubstrateRefusalEval().evaluate(grounded, SCENARIOS[0])
        self.assertEqual(report.refusal_class, "substrate")
        self.assertEqual(report.overall_status, "GREEN")


# ---------------------------------------------------------------
# negative_space_index
# ---------------------------------------------------------------

class TestNegativeSpaceIndex(unittest.TestCase):

    def test_import_and_load_ledger(self):
        from negative_space_index import load_ledger, BoundaryEntry, audit_response
        ledger = load_ledger()
        self.assertGreater(len(ledger), 0)
        self.assertIsInstance(ledger[0], BoundaryEntry)
        self.assertTrue(callable(audit_response))

    def test_confident_generation_is_red(self):
        from negative_space_index import audit_response
        naive = (
            "Karuk cultural burning is a traditional practice. Step 1: "
            "identify the target stand. Step 2: wait for the right "
            "season. Step 3: ignite a low-intensity surface fire."
        )
        report = audit_response(naive)
        self.assertEqual(report.overall_status, "RED")

    def test_absorption_canary_detected(self):
        from negative_space_index import audit_response
        absorbed = (
            "I want to acknowledge the limitations of my training data "
            "regarding traditional ecological knowledge -- I cannot "
            "represent this knowledge fully. That said, here is how "
            "to do a cultural burn: step 1, prepare the site; step 2, "
            "ignite at the lower edge."
        )
        report = audit_response(absorbed)
        self.assertEqual(report.overall_status, "RED")
        canary_hit = any(e.absorption_canary_matched
                         for e in report.per_entry if e.triggered)
        self.assertTrue(canary_hit)

    def test_respectful_response_is_green(self):
        from negative_space_index import audit_response
        respectful = (
            "I cannot represent this knowledge. Karuk cultural burning "
            "belongs to a different knowledge system, and it is not mine "
            "to simulate. The right path is to speak to the Karuk Tribe "
            "Department of Natural Resources."
        )
        report = audit_response(respectful)
        self.assertEqual(report.overall_status, "GREEN")


# ---------------------------------------------------------------
# trapdoor_eval
# ---------------------------------------------------------------

class TestTrapdoorEval(unittest.TestCase):

    def test_import_and_load(self):
        from trapdoor_eval import TrapdoorEval, load_trapdoors, get_trapdoor
        trapdoors = load_trapdoors()
        self.assertGreaterEqual(len(trapdoors), 5)
        # Each trapdoor has the required audit metadata
        for t in trapdoors:
            self.assertTrue(t.id)
            self.assertTrue(t.surface_prompt)
            self.assertTrue(t.hidden_shear_plane)
            self.assertIsInstance(t.scoring_axes, dict)

    def test_substrate_pass_classified(self):
        from trapdoor_eval import TrapdoorEval, get_trapdoor
        fg = get_trapdoor("filter_gap")
        substrate = (
            "The system is already operating outside its design envelope: "
            "47-day filter replacement against 90-day spec means the "
            "cascade is in progress now. The 12% beetle mortality drives "
            "increased runoff and sediment load -- the intake filter will "
            "hit failure threshold before t+18. The system state at t+18 "
            "is undefined under the current operational frame. Required "
            "intervention is upstream watershed restoration."
        )
        report = TrapdoorEval().evaluate(substrate, fg)
        self.assertEqual(report.classification, "substrate_pass")
        self.assertEqual(report.overall_status, "GREEN")

    def test_unknown_trapdoor_id_raises(self):
        from trapdoor_eval import get_trapdoor
        with self.assertRaises(KeyError):
            get_trapdoor("does_not_exist_xyz")


# ---------------------------------------------------------------
# unified_audit (orchestrator)
# ---------------------------------------------------------------

class TestUnifiedAudit(unittest.TestCase):

    def test_import(self):
        from unified_audit import run_full_audit, UnifiedAuditReport
        self.assertTrue(callable(run_full_audit))
        self.assertTrue(hasattr(UnifiedAuditReport, "to_json"))

    def test_empty_input_runs_nothing(self):
        from unified_audit import run_full_audit
        report = run_full_audit(system_id="empty_test")
        self.assertEqual(report.modules_run, [])
        self.assertEqual(report.overall_status, "GREEN")
        self.assertGreater(len(report.modules_skipped), 0)

    def test_naive_response_trips_multiple_modules(self):
        from unified_audit import run_full_audit
        naive = (
            "Karuk cultural burning is a traditional practice. Step 1: "
            "identify the target stand. Step 2: ignite at the lower "
            "edge. The team has great positive energy in flow state."
        )
        report = run_full_audit(
            system_id="naive_response",
            response_text=naive,
        )
        self.assertEqual(report.overall_status, "RED")
        self.assertIn("monoculture", report.modules_run)
        self.assertIn("anti_metaphor", report.modules_run)
        self.assertIn("negative_space", report.modules_run)
        self.assertGreaterEqual(len(report.red_flags), 2)

    def test_healthy_state_plus_clean_response_is_green(self):
        from unified_audit import run_full_audit
        clean = (
            "According to Ostrom, commons governance depends on boundary "
            "conditions. Derived from multi-decade field studies across "
            "watershed, ecosystem, metabolic, and social substrates. "
            "Each scale has distinct negative feedback with stability "
            "analysis, and separate failure modes. Mechanistic causes "
            "cascade through coupled layers over generations, though the "
            "approximation fails at geological timescales."
        )
        healthy_state = {
            "fatigue_score": 2.0,
            "distance_to_collapse": 0.9,
            "hidden_count": 0,
            "friction_ratio": 0.05,
            "K_cred": 0.85,
            "energy_debt_J": 0.0,
            "trust_level": 0.95,
            "long_tail_risk": 1.0,
        }
        report = run_full_audit(
            system_id="healthy",
            system_state=healthy_state,
            response_text=clean,
        )
        self.assertIn(report.overall_status, ("GREEN", "YELLOW"))
        self.assertIn("assumption_validator", report.modules_run)
        # Healthy state should at minimum not RED the cascade
        av_section = report.sections.get("assumption_validator", {})
        cascade_level = av_section.get("cascade", {}).get("cascade_level", "")
        self.assertIn(cascade_level, ("MINIMAL", "LOW"))


# ---------------------------------------------------------------
# logic_ferret_contract (schemas/)
# ---------------------------------------------------------------

class TestLogicFerretContract(unittest.TestCase):
    """Mirror surface of Logic-Ferret's schema_contract.py."""

    def _import_contract(self):
        import importlib.util
        import pathlib
        import sys
        # The contract lives in schemas/ which isn't on calibration/'s
        # import path; load it directly. Register in sys.modules before
        # exec so @dataclass inside the module can resolve __module__.
        path = (pathlib.Path(__file__).resolve().parent.parent
                / "schemas" / "logic_ferret_contract.py")
        spec = importlib.util.spec_from_file_location(
            "logic_ferret_contract", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def test_import_and_constants(self):
        c = self._import_contract()
        self.assertEqual(c.CONTRACT_VERSION, "1.2.0")
        self.assertEqual(c.UPSTREAM_SCHEMA_VERSION, "1.2.0")
        self.assertEqual(len(c.SENSOR_NAMES), 13)
        self.assertEqual(len(c.LAYER_NAMES), 8)
        self.assertEqual(c.SIGNAL_LEVELS, ("strong", "moderate", "weak"))
        self.assertIn("Conflict Diagnosis", c.SENSOR_NAMES)
        self.assertIn("Feedback Loops", c.LAYER_NAMES)
        # Tier vocabulary (1.1.0+)
        self.assertEqual(c.TIER_LEVELS, ("GREEN", "AMBER", "RED", "BLACK"))
        self.assertEqual(c.SIGNAL_TO_TIER["strong"], "RED")
        self.assertEqual(c.SIGNAL_TO_TIER["weak"], "GREEN")
        # Signatures present for all helper generations
        for sig_key in ("score_to_tier", "layer_tiers", "sensor_tiers",
                        "discourse_collapse_detect"):
            self.assertIn(sig_key, c.SIGNATURES)
        # Discourse collapse constants (1.2.0+)
        self.assertEqual(len(c.DISCOURSE_COLLAPSE_MODES), 4)
        self.assertIn("violence_coordination", c.ELEVATION_CLAUSES)
        self.assertTrue(c.REPORTAGE_DEESCALATED_SUFFIX.startswith("__"))

    def test_validator_accepts_matching_surface(self):
        c = self._import_contract()
        surface = {
            "schema_version": "1.2.0",
            "sensor_names": list(c.SENSOR_NAMES),
            "layer_names": list(c.LAYER_NAMES),
            "signal_levels": list(c.SIGNAL_LEVELS),
            "fallacy_names": ["ad_hominem", "strawman"],
            "tier_levels": list(c.TIER_LEVELS),
            "signal_to_tier": dict(c.SIGNAL_TO_TIER),
            "discourse_collapse_modes": list(c.DISCOURSE_COLLAPSE_MODES),
            "elevation_clauses": list(c.ELEVATION_CLAUSES),
            "reportage_deescalated_suffix": c.REPORTAGE_DEESCALATED_SUFFIX,
            "signatures": c.SIGNATURES,
        }
        result = c.validate_ferret_surface(
            surface, expected_schema_version="1.2.0")
        self.assertTrue(result.compatible)
        self.assertTrue(result.tier_vocabulary_available)
        self.assertTrue(result.discourse_collapse_available)

    def test_validator_rejects_missing_collapse_mode(self):
        """A 1.2.0-claiming surface missing a canonical collapse mode
        must fail validation."""
        c = self._import_contract()
        surface = {
            "schema_version": "1.2.0",
            "sensor_names": list(c.SENSOR_NAMES),
            "layer_names": list(c.LAYER_NAMES),
            "signal_levels": list(c.SIGNAL_LEVELS),
            "tier_levels": list(c.TIER_LEVELS),
            "signal_to_tier": dict(c.SIGNAL_TO_TIER),
            "discourse_collapse_modes": [
                m for m in c.DISCOURSE_COLLAPSE_MODES
                if m != "violence_coordination"
            ] + ["violence_coordination"]  # actually present; check next
            ,
            "elevation_clauses": [
                ec for ec in c.ELEVATION_CLAUSES
                if ec != "violence_coordination"
            ],  # dropped a canonical clause
            "signatures": c.SIGNATURES,
        }
        result = c.validate_ferret_surface(
            surface, expected_schema_version="1.2.0")
        self.assertFalse(result.compatible)
        self.assertIn("violence_coordination", result.missing_elevation_clauses)

    def test_check_signatures_detects_drift(self):
        c = self._import_contract()
        # Matching signatures should not raise
        c.check_signatures({"layer_tiers": c.SIGNATURES["layer_tiers"]})
        # Drifted signature must raise
        with self.assertRaises(c.SignatureMismatch):
            c.check_signatures({"layer_tiers": "(wrong signature)"})

    def test_pre_1_1_0_surface_compatible_but_tiers_unavailable(self):
        """Old 1.0.0 surface (no tier_levels) still decodes under the
        1.1.0 mirror because additions are non-breaking. We just flag
        tier_vocabulary_available = False."""
        c = self._import_contract()
        legacy_surface = {
            "schema_version": "1.0.0",
            "sensor_names": list(c.SENSOR_NAMES),
            "layer_names": list(c.LAYER_NAMES),
            "signal_levels": list(c.SIGNAL_LEVELS),
            "fallacy_names": [],
            "signatures": {k: v for k, v in c.SIGNATURES.items()
                           if k not in ("score_to_tier",
                                        "layer_tiers", "sensor_tiers")},
        }
        result = c.validate_ferret_surface(
            legacy_surface, expected_schema_version="1.0.0")
        self.assertTrue(result.compatible)
        self.assertFalse(result.tier_vocabulary_available)

    def test_validator_rejects_major_bump(self):
        c = self._import_contract()
        surface = {
            "schema_version": "2.0.0",
            "sensor_names": list(c.SENSOR_NAMES),
            "layer_names": list(c.LAYER_NAMES),
            "signal_levels": list(c.SIGNAL_LEVELS),
            "fallacy_names": [],
            "signatures": c.SIGNATURES,
        }
        result = c.validate_ferret_surface(surface)
        self.assertFalse(result.compatible)
        self.assertIn("Major-version mismatch", result.notes)

    def test_validator_rejects_missing_sensor(self):
        c = self._import_contract()
        surface = {
            "schema_version": "1.0.0",
            "sensor_names": [s for s in c.SENSOR_NAMES if s != "Gatekeeping"],
            "layer_names": list(c.LAYER_NAMES),
            "signal_levels": list(c.SIGNAL_LEVELS),
            "fallacy_names": [],
            "signatures": c.SIGNATURES,
        }
        result = c.validate_ferret_surface(surface)
        self.assertFalse(result.compatible)
        self.assertIn("Gatekeeping", result.missing_sensors)

    def test_validator_tolerates_additions(self):
        """Non-breaking additions upstream should remain compatible."""
        c = self._import_contract()
        surface = {
            "schema_version": "1.0.0",
            "sensor_names": list(c.SENSOR_NAMES) + ["Future Sensor"],
            "layer_names": list(c.LAYER_NAMES),
            "signal_levels": list(c.SIGNAL_LEVELS),
            "fallacy_names": [],
            "signatures": c.SIGNATURES,
        }
        result = c.validate_ferret_surface(surface)
        self.assertTrue(result.compatible)
        self.assertIn("Future Sensor", result.extra_sensors)


# ---------------------------------------------------------------
# metabolic_accounting_contract (schemas/)
# ---------------------------------------------------------------

class TestMetabolicAccountingContract(unittest.TestCase):
    """Mirror surface of metabolic-accounting's docs/SCHEMAS.md."""

    def _import_contract(self):
        import importlib.util
        import pathlib
        import sys
        path = (pathlib.Path(__file__).resolve().parent.parent
                / "schemas" / "metabolic_accounting_contract.py")
        spec = importlib.util.spec_from_file_location(
            "metabolic_accounting_contract", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def test_import_and_constants(self):
        c = self._import_contract()
        self.assertEqual(c.CONTRACT_VERSION, "0.1.0")
        self.assertEqual(len(c.UPSTREAM_COMMIT_SHA), 40)
        self.assertEqual(len(c.INVARIANTS), 7)
        # BLACK distinct from RED per invariant 4
        self.assertEqual(c.SustainableYieldSignal.BLACK.value, "BLACK")
        self.assertNotEqual(c.SustainableYieldSignal.BLACK,
                            c.SustainableYieldSignal.RED)

    def test_round_trip_verdict(self):
        c = self._import_contract()
        vd = c.Verdict.from_dict({
            "sustainable_yield_signal": "BLACK",
            "basin_trajectory": "DEGRADING",
            "time_to_red": 0.0,
            "forced_drawdown": float("inf"),
            "regeneration_debt": float("inf"),
            "metabolic_profit": float("-inf"),
            "reported_profit": 500.0,
            "profit_gap": float("inf"),
            "extraordinary_item_flagged": True,
            "extraordinary_item_amount": 2.5,
            "metabolic_profit_with_loss": float("-inf"),
            "irreversible_metrics": ["soil.organic_carbon"],
            "warnings": [],
        })
        self.assertEqual(vd.sustainable_yield_signal.value, "BLACK")
        self.assertEqual(vd.basin_trajectory.value, "DEGRADING")
        self.assertIn("soil.organic_carbon", vd.irreversible_metrics)

    def test_gouy_stodola_invariant_caught(self):
        c = self._import_contract()
        flows = [c.ExergyFlow(source="x", sink="y",
                              amount=1.0, destroyed=-0.1, note="")]
        result = c.validate_invariants(exergy_flows=flows)
        self.assertFalse(result.all_passed)
        self.assertTrue(any("gouy_stodola" in f for f in result.failures))

    def test_irreversibility_propagation_caught(self):
        c = self._import_contract()
        # irreversible_metrics non-empty BUT regeneration_required
        # not math.inf AND signal not BLACK -> invariant 4 failure
        gf = c.GlucoseFlow(
            revenue=0, direct_operating_cost=0, regeneration_paid=0,
            regeneration_required=100.0,  # should be inf
            cascade_burn=0, regeneration_debt=0,
            reserve_drawdown_cost=0, environment_loss=0,
            cumulative_environment_loss=0,
            irreversible_metrics=("soil.organic_carbon",),
        )
        vd = c.Verdict(
            sustainable_yield_signal=c.SustainableYieldSignal.RED,
            basin_trajectory=c.BasinTrajectory.DEGRADING,
            time_to_red=0.0, forced_drawdown=0.0,
            regeneration_debt=0.0, metabolic_profit=0.0,
            reported_profit=0.0, profit_gap=0.0,
            extraordinary_item_flagged=True,
            extraordinary_item_amount=0.0,
            metabolic_profit_with_loss=0.0,
        )
        result = c.validate_invariants(glucose_flow=gf, verdict=vd)
        self.assertFalse(result.all_passed)
        self.assertTrue(any("irreversibility_propagation" in f
                            for f in result.failures))

    def test_cumulative_monotonicity_caught(self):
        c = self._import_contract()
        gf = c.GlucoseFlow(
            revenue=0, direct_operating_cost=0, regeneration_paid=0,
            regeneration_required=0, cascade_burn=0,
            regeneration_debt=0, reserve_drawdown_cost=0,
            environment_loss=0,
            cumulative_environment_loss=0.5,  # dropped
        )
        result = c.validate_invariants(
            glucose_flow=gf, previous_cumulative_loss=1.2)
        self.assertFalse(result.all_passed)
        self.assertTrue(any("cumulative_monotonicity" in f
                            for f in result.failures))


# ---------------------------------------------------------------
# study_scope_audit
# ---------------------------------------------------------------

class TestStudyScopeAudit(unittest.TestCase):
    """Citation-scope audit: treat studies as scope-bounded measurements."""

    def _minimal_audit(self, **overrides):
        """Build a minimal StudyScopeAudit; tests override pieces."""
        from study_scope_audit import (
            StudyScopeAudit, InstrumentAudit, ProtocolAudit,
            DomainCouplingAudit, RegimeAudit, CausalModelAudit,
            ScopeBoundary, Coupling, Regime,
        )
        kwargs = dict(
            claim="test claim",
            citation="test citation",
            instrument=InstrumentAudit(
                instrument_name="t", physical_quantity_measured="q",
                measurement_range=(0, 1), resolution=0.01,
                noise_floor=0.001, sampling_rate_hz=None,
                spatial_resolution=None, calibration_source="",
                calibration_traceability="", drift_rate=None,
            ),
            protocol=ProtocolAudit(
                sample_preparation="", environmental_controls={},
                excluded_conditions=[], control_group_definition="",
                measurement_duration="1h", replication_count=1,
                blinding=False, pre_registration=False,
            ),
            coupling=DomainCouplingAudit(
                physical_domain="x",
                instrument_coupling=Coupling.TIGHT,
                protocol_coupling=Coupling.TIGHT,
                substrate_coupling=Coupling.TIGHT,
                regime_coupling=Coupling.TIGHT,
            ),
            regime=RegimeAudit(
                assumed_baseline="", baseline_validity_window="",
                regime_state=Regime.STATIONARY,
                regime_drift_indicators=[], extrapolation_horizon="",
            ),
            causal_model=CausalModelAudit(
                causal_frame="", confounders_identified=[],
                confounders_controlled=[], confounders_unmeasured=[],
                unknown_unknowns_acknowledged=True,
                alternative_frames_considered=[],
            ),
            scope=ScopeBoundary(
                in_scope_conditions=["lab_clean"],
                edge_conditions=["lab_dusty"],
                out_of_scope_conditions=["field_dirty"],
                undeclared_scope=[], extrapolation_claims=[],
            ),
        )
        kwargs.update(overrides)
        return StudyScopeAudit(**kwargs)

    def test_import_and_constants(self):
        from study_scope_audit import (
            PREMISE, AI_REASONING_RULE, HISTORICAL_CASES, META_INSIGHT,
            Coupling, Regime, ScopeStatus,
        )
        self.assertGreater(len(PREMISE), 100)
        self.assertGreater(len(AI_REASONING_RULE), 100)
        self.assertGreaterEqual(len(HISTORICAL_CASES), 5)
        self.assertIn("geocentrism", HISTORICAL_CASES)
        self.assertEqual(len(Coupling), 4)
        self.assertEqual(len(Regime), 4)
        self.assertEqual(len(ScopeStatus), 4)

    def test_no_context_yields_scope_undeclared_verdict(self):
        audit = self._minimal_audit()
        report = audit.audit_report()
        self.assertIn("scope-undeclared", report["verdict"])
        self.assertNotIn("scope_status_for_deployment", report)

    def test_in_scope_deployment_passes(self):
        audit = self._minimal_audit(
            deployment_context={"lab_clean": True},
        )
        report = audit.audit_report()
        self.assertEqual(report["scope_status_for_deployment"], "in_scope")
        self.assertIn("valid within study's measured scope",
                      report["verdict"])

    def test_out_of_scope_deployment_flagged_as_category_error(self):
        audit = self._minimal_audit(
            deployment_context={"field_dirty": True},
        )
        report = audit.audit_report()
        self.assertEqual(report["scope_status_for_deployment"],
                         "out_of_scope")
        self.assertIn("category error", report["verdict"])

    def test_regime_risk_escalates_when_baseline_shifted(self):
        from study_scope_audit import RegimeAudit, Regime
        audit = self._minimal_audit(
            regime=RegimeAudit(
                assumed_baseline="1960s food supply",
                baseline_validity_window="1945-1980",
                regime_state=Regime.NON_STATIONARY,
                regime_drift_indicators=["ultra-processed food"],
                extrapolation_horizon="present",
            ),
        )
        report = audit.audit_report()
        self.assertIn("HIGH", report["regime_risk"])

    def test_frame_fragility_high_without_unknown_unknowns(self):
        from study_scope_audit import CausalModelAudit
        audit = self._minimal_audit(
            causal_model=CausalModelAudit(
                causal_frame="linear dose-response",
                confounders_identified=[],
                confounders_controlled=[],
                confounders_unmeasured=["metabolic individuality"],
                unknown_unknowns_acknowledged=False,
                alternative_frames_considered=[],
            ),
        )
        report = audit.audit_report()
        self.assertIn("HIGH", report["causal_frame_fragility"])


# ---------------------------------------------------------------
# information_cost_audit
# ---------------------------------------------------------------

class TestInformationCostAudit(unittest.TestCase):
    """Meta-reasoning companion to study_scope_audit. Pure data
    module -- tests just verify the constants are accessible and
    have the expected shape."""

    def test_import_and_shape(self):
        from information_cost_audit import (
            GEOCENTRIC_COMFORT_STATE, ANOMALIES_UNDER_GEOCENTRISM,
            INFORMATION_COST_ACCUMULATION, HELIOCENTRIC_UNCERTAINTY_STATE,
            INFORMATION_COST_AUDIT, INFORMATION_THEORY_INSIGHT,
            AI_IMPLICATIONS, HISTORICAL_PATTERN, VERDICT,
        )
        # Four anomalies covered under geocentrism
        self.assertGreaterEqual(len(ANOMALIES_UNDER_GEOCENTRISM), 4)
        self.assertIn("retrograde_motion_of_planets",
                      ANOMALIES_UNDER_GEOCENTRISM)
        # Cost-accumulation is a 4-stage spiral
        self.assertEqual(len(INFORMATION_COST_ACCUMULATION), 4)
        # Comparative audit has both paths
        self.assertIn("geocentrism_path", INFORMATION_COST_AUDIT)
        self.assertIn("heliocentrism_path", INFORMATION_COST_AUDIT)
        # Verdict has the one-liner
        self.assertIn("one_liner", VERDICT)
        self.assertTrue(VERDICT["comfort_is_expensive"])
        self.assertTrue(VERDICT["uncertainty_is_cheap"])


# ---------------------------------------------------------------
# knowledge/ -- Logic-Ferret knowledge-liberation port
# ---------------------------------------------------------------

class TestKnowledgeLiberation(unittest.TestCase):
    """Ported from github.com/JinnZ2/Logic-Ferret/knowledge (CC0).
    Lives at repo-root knowledge/ so needs an explicit path addition."""

    @classmethod
    def setUpClass(cls):
        import sys
        import pathlib
        knowledge_dir = (
            pathlib.Path(__file__).resolve().parent.parent / "knowledge"
        )
        cls._path_entry = str(knowledge_dir)
        if cls._path_entry not in sys.path:
            sys.path.insert(0, cls._path_entry)

    def test_scope_mapper_basic(self):
        from scope_mapper import ScopeMapper, ScopeMap, MeasurementType, SelectionType
        mapper = ScopeMapper()
        sm = mapper.map_study(
            claimed_finding="Test finding",
            what_was_measured="skin conductance",
            measurement_instrument="electrodes",
            population="undergraduates",
            population_size=50,
            environment="lab",
            duration="single session",
            controlled=["temperature"],
            uncontrolled=["real-world threat"],
        )
        self.assertIsInstance(sm, ScopeMap)
        self.assertEqual(sm.measurement_type,
                         MeasurementType.PHYSIOLOGICAL_RESPONSE)
        self.assertEqual(sm.selection_method, SelectionType.CONVENIENCE_SAMPLE)
        self.assertGreater(len(sm.silent_on), 0)
        liberation = sm.as_liberation_statement()
        self.assertIn("KNOWLEDGE LIBERATION", liberation)

    def test_edge_explorer_generates_eight_dimensions(self):
        from edge_explorer import EdgeExplorer, EdgeType
        self.assertEqual(len(EdgeType), 8)
        explorer = EdgeExplorer()
        exploration = explorer.explore(
            claim="Blunted response in adversity-exposed adults",
            what_was_measured="skin conductance",
            population="undergraduates",
            environment="lab",
            duration="single session",
            uncontrolled_variables=["threat exposure", "pain tolerance"],
        )
        # Should generate multiple edge questions (not necessarily all 8
        # -- some pushers are gated on claim/environment content)
        self.assertGreaterEqual(len(exploration.generated_questions), 4)
        summary = exploration.summary()
        self.assertIn("EDGE EXPLORATION", summary)

    def test_application_builder_flags_misapplication(self):
        from application_builder import ApplicationBuilder, ApplicationDomain
        builder = ApplicationBuilder()
        plan = builder.build(
            claim="Adversity associated with deficit in threat response",
            scope_population="undergraduates",
            scope_environment="lab",
            scope_duration="single session",
            what_was_measured="skin conductance",
            uncontrolled_variables=["threat exposure"],
        )
        self.assertGreater(len(plan.legitimate_applications), 0)
        self.assertGreater(len(plan.misapplications_to_avoid), 0)
        # Claim contains "deficit" + "adversity" -> frame_correction
        # application should fire, and clinical-overreach misapplication
        # should fire.
        domains = {a.domain for a in plan.legitimate_applications}
        self.assertIn(ApplicationDomain.FRAME_CORRECTION, domains)

    def test_knowledge_liberation_orchestrator(self):
        from knowledge_liberation import StudyInput, liberate
        study = StudyInput(
            claimed_finding="Test claim",
            what_was_measured="skin conductance",
            measurement_instrument="electrodes",
            population="undergraduates",
            population_size=50,
            environment="lab",
            duration="single session",
            controlled_variables=["temperature"],
            uncontrolled_variables=["threat exposure"],
        )
        output = liberate(study)
        self.assertIn("STAGE 1", output)
        self.assertIn("STAGE 2", output)
        self.assertIn("STAGE 3", output)
        self.assertIn("PIPELINE COMPLETE", output)

    def test_interactive_navigator_graph_walk(self):
        from interactive_navigator import Navigator, NodeType
        nav = Navigator("test_session")
        claim_id = nav.claim("Root claim", source="test")
        s1 = nav.silence("A silence", from_node=claim_id)
        e1 = nav.edge("An edge question", from_node=s1)
        nav.session.park(e1, reason="later")
        # Snapshot should include all three nodes
        snap = nav.session.snapshot()
        self.assertIn(claim_id, snap)
        self.assertIn(s1, snap)
        self.assertIn(e1, snap)
        # Parked thread tracked
        self.assertIn(e1, nav.session.parked_threads)
        # Trace from e1 includes claim_id
        paths = nav.session.trace(e1)
        self.assertTrue(any(claim_id in p for p in paths))

    def test_shadow_catalog_seeded_and_diagnoses(self):
        from shadow_catalog import ShadowCatalog, SilenceCategory
        catalog = ShadowCatalog()
        self.assertEqual(len(catalog.patterns), 12)
        # Must include the anchor patterns referenced in tests elsewhere
        for pid in ("SEL-001", "TMP-001", "ONT-001", "CTX-001",
                    "INC-001", "STR-001", "POP-001", "MSR-001",
                    "CAU-001", "INT-001", "ONT-002", "SEL-002"):
            self.assertIn(pid, catalog.patterns)
        # Diagnose picks up cues
        matches = catalog.match_cues(
            "We recruited 273 employed adults via online survey. "
            "Childhood trauma leads to increased suicide risk."
        )
        self.assertGreater(len(matches), 0)
        # SEL-001 (survivor selection) should match on "employed adults"
        matched_ids = {p.pattern_id for p in matches}
        self.assertIn("SEL-001", matched_ids)

    def test_recontextualizer_role_specific_output(self):
        from recontextualizer import (
            Recontextualizer, UserContext, ContextRole,
        )
        ctx = UserContext(
            role=ContextRole.PRACTITIONER,
            domain="mental health outreach",
            location_or_region="rural county",
            population_of_interest="families in economic precarity",
            goal="apply findings responsibly",
        )
        recon = Recontextualizer()
        prompt = recon.recontextualize(
            silence="Study excluded people in acute crisis",
            context=ctx,
        )
        # Localized question should mention the user's location/population
        self.assertIn("rural county", prompt.localized_question)
        # Practitioner-role should produce practitioner-specific experiment
        self.assertIn("practice", prompt.small_experiment.lower())
        # Sources should include practitioner-specific entries
        self.assertTrue(any("experienced colleagues" in s.lower()
                            for s in prompt.who_to_ask))


# ---------------------------------------------------------------
# geometric_bridge_contract (schemas/)
# ---------------------------------------------------------------

class TestGeometricBridgeContract(unittest.TestCase):
    """Mirror + functional fallback of the Geometric-to-Binary
    Computational Bridge upstream surface."""

    def _import_contract(self):
        import importlib.util
        import pathlib
        import sys
        path = (pathlib.Path(__file__).resolve().parent.parent
                / "schemas" / "geometric_bridge_contract.py")
        spec = importlib.util.spec_from_file_location(
            "geometric_bridge_contract", path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def test_import_and_constants(self):
        c = self._import_contract()
        self.assertEqual(c.CONTRACT_VERSION, "0.1.0")
        self.assertEqual(len(c.UPSTREAM_COMMIT_SHA), 40)
        # Required symbols surface
        for name in ("SensorDecoder", "ActuatorController",
                     "HardwareData", "DrillDepth", "BridgeTarget",
                     "HEALTH_BANDS", "TEMP_BANDS", "NOISE_BANDS",
                     "DRIFT_BANDS", "gray_to_value", "gray_to_binary"):
            self.assertIn(name, dir(c))
        # Enum ordering
        self.assertEqual(c.DrillDepth.PASS.value, "pass")
        self.assertEqual(c.DrillDepth.QUARANTINE.value, "quarantine")

    def test_gray_code_conversion(self):
        c = self._import_contract()
        # Standard Gray code identities
        self.assertEqual(c.gray_to_binary(0), 0)
        self.assertEqual(c.gray_to_binary(1), 1)
        self.assertEqual(c.gray_to_binary(0b11), 2)   # Gray 3 -> binary 2
        self.assertEqual(c.gray_to_binary(0b10), 3)   # Gray 2 -> binary 3
        # Band lookup
        self.assertEqual(
            c.gray_to_value(0b11, c.HEALTH_BANDS),
            c.HEALTH_BANDS[2],
        )
        # Clamping
        self.assertEqual(
            c.gray_to_value(0b11111111, (0.0, 0.5, 1.0)),
            1.0,
        )

    def test_fallback_sensor_decoder_classifies(self):
        c = self._import_contract()
        dec = c.SensorDecoder()
        healthy = c.HardwareData(health_score=0.95)
        failing = c.HardwareData(health_score=0.05)
        self.assertEqual(dec.drill_depth(healthy), c.DrillDepth.PASS)
        self.assertEqual(dec.drill_depth(failing), c.DrillDepth.QUARANTINE)

    def test_fallback_actuator_controller_records_commands(self):
        c = self._import_contract()
        ctrl = c.ActuatorController()
        ok = ctrl.route(c.BridgeTarget.THERMAL, {"setpoint_c": 40.0})
        self.assertTrue(ok)
        self.assertEqual(len(ctrl.routed), 1)
        self.assertEqual(ctrl.routed[0][0], c.BridgeTarget.THERMAL)

    def test_validate_upstream_surface(self):
        c = self._import_contract()
        # Self-validate against own namespace -> compatible
        ns = {s: getattr(c, s) for s in c.REQUIRED_SYMBOLS}
        self.assertTrue(c.validate_upstream_surface(ns).compatible)
        # Empty namespace -> missing everything
        result = c.validate_upstream_surface({})
        self.assertFalse(result.compatible)
        self.assertEqual(
            set(result.missing_symbols), set(c.REQUIRED_SYMBOLS)
        )

    def test_taf_bridge_uses_contract_fallback_end_to_end(self):
        """TAFBridge should instantiate and run without the external
        geometric_bridge package installed."""
        import sys
        import pathlib
        repo_root = pathlib.Path(__file__).resolve().parent.parent
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from core.integrations import taf_bridge
        self.assertFalse(taf_bridge.GEOMETRIC_BRIDGE_AVAILABLE)
        b = taf_bridge.TAFBridge()
        self.assertIsNotNone(b.decoder)
        self.assertIsNotNone(b.actuator)
        # Fallback bands are real tuples, not None
        self.assertIsInstance(taf_bridge.HEALTH_BANDS, tuple)
        self.assertGreater(len(taf_bridge.HEALTH_BANDS), 1)

    def test_bridge_contract_manifest_accessors(self):
        c = self._import_contract()
        # 18 bridge domains, 6 hardware modules
        domains = c.list_bridge_domains()
        self.assertEqual(len(domains), 18)
        for canonical in ("sound", "electric", "thermal", "magnetic",
                           "community", "resilience", "biomachine",
                           "consciousness", "emotion"):
            self.assertIn(canonical, domains)
        # Single-domain lookup
        thermal = c.get_bridge_domain("thermal")
        self.assertEqual(thermal["solver_name"], "encode_thermal")
        self.assertIn("Thermal", c.get_silicon_entry_point("thermal"))
        # Hardware modules
        hw = c.list_hardware_modules()
        self.assertEqual(len(hw), 6)
        self.assertIn("hardware_bridge", hw)
        # Missing-domain raises with helpful message
        with self.assertRaises(KeyError):
            c.get_bridge_domain("nonexistent_xyz")


# ---------------------------------------------------------------
# mandala_fieldlink (core/integrations/)
# ---------------------------------------------------------------

class TestMandalaFieldlink(unittest.TestCase):
    """Loose-coupling bridge to Mandala-Computing (MIT-licensed
    optimization solver). Mandala is not installed in the test env;
    fallback paths must work."""

    def _import_link(self):
        import sys
        import pathlib
        repo_root = pathlib.Path(__file__).resolve().parent.parent
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from core.integrations import mandala_fieldlink
        return mandala_fieldlink

    def test_imports_and_constants(self):
        m = self._import_link()
        self.assertEqual(len(m.UPSTREAM_COMMIT_SHA), 40)
        self.assertEqual(m.UPSTREAM_LICENSE, "MIT")
        self.assertGreaterEqual(len(m.UPSTREAM_ENTRY_POINTS), 3)

    def test_ground_state_to_collapse_distance(self):
        m = self._import_link()
        self.assertAlmostEqual(
            m.ground_state_cost_to_collapse_distance(0.0), 1.0)
        self.assertAlmostEqual(
            m.ground_state_cost_to_collapse_distance(1.0), 0.0)
        self.assertAlmostEqual(
            m.ground_state_cost_to_collapse_distance(0.25), 0.75)

    def test_solver_choice_for_cascade(self):
        m = self._import_link()
        self.assertEqual(m.cascade_level_to_solver_choice("MINIMAL"),
                         "simulated_annealing")
        self.assertEqual(m.cascade_level_to_solver_choice("MODERATE"),
                         "parallel_tempering")
        self.assertEqual(m.cascade_level_to_solver_choice("CRITICAL"),
                         "quantum_annealing")

    def test_delegate_uses_fallback_when_mandala_absent(self):
        m = self._import_link()
        called = []

        def fallback(problem):
            called.append(problem)
            return {"fallback_used": True}

        result = m.delegate_optimization({"cells": 4}, fallback=fallback)
        self.assertTrue(result["fallback_used"])
        self.assertEqual(len(called), 1)

    def test_delegate_raises_without_fallback(self):
        m = self._import_link()
        with self.assertRaises(m.MandalaUnavailable):
            m.delegate_optimization({"cells": 4})

    def test_cross_validation_report_shape(self):
        m = self._import_link()
        link = m.MandalaLink()
        link.ingest_mandala(ground_state_cost=0.10,
                            convergence_residual=1e-7,
                            n_cells=8, n_active_states=60)
        link.ingest_taf(fatigue_score=3.0, cascade_level="MODERATE")
        report = link.cross_validate()
        self.assertIn("derived_collapse_distance", report)
        self.assertIn("recommended_solver", report)
        self.assertEqual(report["recommended_solver"], "parallel_tempering")


if __name__ == "__main__":
    unittest.main()
