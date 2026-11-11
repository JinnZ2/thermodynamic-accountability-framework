"""
test_unknown_axis.py -- UNKNOWN is a coverage axis, not a severity.

Planted known-answer cases (a)/(b)/(c) from unknown_axis_cases.PLANTED,
plus the two print rules. stdlib unittest. CC0.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_audit import (run_full_audit, _aggregate_status,
                           _STATUS_RANK, NOT_DETERMINABLE)
from unknown_axis_cases import PLANTED, CASES, BEFORE, render


class TestPlanted(unittest.TestCase):

    def test_planted_answers(self):
        for cid, _src, kw, exp in PLANTED:
            with self.subTest(case=cid):
                r = run_full_audit(system_id=cid, **kw)
                self.assertEqual(r.severity, exp["severity"])
                self.assertEqual(len(r.coverage), exp["coverage_count"])

    def test_b_prints_both_axes(self):
        _cid, _s, kw, _e = PLANTED[1]
        r = run_full_audit(**kw)
        self.assertEqual(r.overall_status, "GREEN+COVERAGE(3: UNKNOWN=3)")
        self.assertNotEqual(r.overall_status, "GREEN")
        self.assertIn("Coverage: 3", r.summary)

    def test_coverage_entries_carry_expiry(self):
        _cid, _s, kw, _e = PLANTED[1]
        r = run_full_audit(**kw)
        self.assertEqual(sorted(e["input"] for e in r.coverage),
                         ["K_cred", "hidden_count", "long_tail_risk"])
        for e in r.coverage:
            self.assertIn("pr77", e["expiry_condition"])
            self.assertIn("pr78", e["expiry_condition"])


class TestRules(unittest.TestCase):

    def test_unknown_not_in_rank_table(self):
        self.assertNotIn("UNKNOWN", _STATUS_RANK)

    def test_aggregate_ignores_unmeasured(self):
        self.assertEqual(_aggregate_status(["UNKNOWN", "GREEN"]), "GREEN")
        self.assertEqual(_aggregate_status(["UNKNOWN"]), NOT_DETERMINABLE)
        self.assertEqual(_aggregate_status([]), NOT_DETERMINABLE)
        self.assertEqual(_aggregate_status(["not_a_label"]), NOT_DETERMINABLE)
        self.assertEqual(_aggregate_status(["RED", "UNKNOWN"]), "RED")

    def test_single_color_never_alone_with_coverage(self):
        for cid, _src, kw in CASES:
            r = run_full_audit(system_id=cid, **kw)
            if r.coverage:
                self.assertNotIn(r.overall_status, ("GREEN", "YELLOW", "RED"))

    def test_existing_cases_severity_changes(self):
        # Severity (not the one-string form) vs main @ dc1c8c1. Moved:
        # T1 (no input) and T3 (its RED came only from a crash).
        changed = []
        for cid, _src, kw in CASES:
            r = run_full_audit(system_id=cid, **kw)
            if r.severity != BEFORE[cid]:
                changed.append(cid)
        self.assertEqual(changed, ["T1_empty", "T3_healthy_clean"])

    def test_crash_is_gap_not_red(self):
        r = run_full_audit(function_audit={"function": None})
        self.assertEqual(r.severity, NOT_DETERMINABLE)
        self.assertEqual([e["kind"] for e in r.coverage], ["GAP_INSTRUMENT_CRASH"])
        self.assertEqual(r.red_flags, [])

    def test_crash_records_missing_path(self):
        # Point negative_space at a path that does not exist; the crash
        # must reach coverage carrying that path, and not reach severity.
        import negative_space_index as N
        saved = N._DEFAULT_LEDGER
        N._DEFAULT_LEDGER = saved.parent / "no_such_ledger.json"
        try:
            r = run_full_audit(response_text="x")
        finally:
            N._DEFAULT_LEDGER = saved
        gaps = [e for e in r.coverage if e["kind"] == "GAP_INSTRUMENT_CRASH"]
        self.assertEqual([e["module"] for e in gaps], ["negative_space"])
        self.assertTrue(gaps[0]["missing_path"].endswith("no_such_ledger.json"))
        self.assertTrue(gaps[0]["reason"].startswith("FileNotFoundError"))

    def test_existing_cases_no_crash_after_path_fix(self):
        for cid, _src, kw in CASES:
            r = run_full_audit(system_id=cid, **kw)
            self.assertEqual(
                [e for e in r.coverage if e["kind"] == "GAP_INSTRUMENT_CRASH"], [], cid)

    def test_info_kind_separate(self):
        r = run_full_audit(system_state={"trust_level": "high"})
        kinds = r.to_dict()["coverage_by_kind"]
        self.assertEqual(kinds.get("INFO"), 1)
        self.assertEqual(kinds.get("UNKNOWN"), 7)

    def test_generated_doc_current(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "docs", "UNKNOWN_AXIS.md")
        with open(path) as fh:
            self.assertEqual(fh.read(), render(None))



class TestPipelineNotMeasured(unittest.TestCase):

    def test_no_modules_not_measured(self):
        from pipeline import _aggregate, NOT_MEASURED
        self.assertEqual(_aggregate({}), (None, "undetermined", "NO_MODULES_RUN"))


class TestConfidenceExperiment(unittest.TestCase):

    def test_selftest(self):
        import contextlib, io
        import confidence_unknown_experiment as X
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(X.selftest(), 0)



class TestSilentFillExperiments(unittest.TestCase):

    def _quiet(self, fn):
        import contextlib, io
        with contextlib.redirect_stdout(io.StringIO()):
            return fn()

    def test_register_resolves(self):
        import silent_fill_register as R
        self.assertEqual(self._quiet(R.selftest), 0)

    def test_band_experiment(self):
        import pipeline_band_experiment as X
        self.assertEqual(self._quiet(X.selftest), 0)

    def test_missing_experiment(self):
        import calibration_missing_experiment as X
        self.assertEqual(self._quiet(X.selftest), 0)
        p1 = [c for c in __import__("calibration_cases").cases()
              if c[0] == "P1_one_dim_worst"][0][2]
        self.assertAlmostEqual(X.calibration_score(p1, "C")[0], 0.7)
        self.assertAlmostEqual(X.calibration_score(p1, "A")[0], 1.0)


if __name__ == "__main__":
    unittest.main()
