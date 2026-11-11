#!/usr/bin/env python3
# calibration/test_not_determinable_reason.py -- CC0, stdlib only
# Provenance: co-authored (Kavik + Claude), 2026-11-11.
# One test per not_determinable_reason value, plus the pipeline rule.
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unified_audit as U  # noqa: E402
import pipeline as PL      # noqa: E402


def _gap(*_a, **_k):
    return ("not_a_label", {})


class NotDeterminableReason(unittest.TestCase):

    def test_empty_audit_no_modules_run(self):          # T1
        r = U.run_full_audit()
        self.assertEqual(r.severity, U.NOT_DETERMINABLE)
        self.assertEqual(r.not_determinable_reason, U.NO_MODULES_RUN)
        self.assertEqual(r.to_dict()["not_determinable_reason"], U.NO_MODULES_RUN)

    def test_planted_c_all_inputs_unknown(self):        # planted (c)
        r = U.run_full_audit(system_state={})
        self.assertEqual(r.severity, U.NOT_DETERMINABLE)
        self.assertEqual(r.not_determinable_reason, U.ALL_INPUTS_UNKNOWN)

    def test_all_modules_gap_instrument(self):
        with mock.patch.object(U, "_run_monoculture", _gap), \
             mock.patch.object(U, "_run_anti_metaphor", _gap), \
             mock.patch.object(U, "_run_negative_space", _gap):
            r = U.run_full_audit(response_text="x")
        self.assertEqual(r.modules_run, ["monoculture", "anti_metaphor", "negative_space"])
        self.assertEqual(r.severity, U.NOT_DETERMINABLE)
        self.assertEqual(r.not_determinable_reason, U.ALL_MODULES_GAP_INSTRUMENT)

    def test_mixed_is_reported_not_forced(self):
        with mock.patch.object(U, "_run_monoculture", _gap), \
             mock.patch.object(U, "_run_anti_metaphor", _gap), \
             mock.patch.object(U, "_run_negative_space", _gap):
            r = U.run_full_audit(response_text="x", system_state={})
        self.assertEqual(r.not_determinable_reason, U.MIXED_UNKNOWN_AND_GAP_INSTRUMENT)

    def test_measured_severity_has_no_reason(self):
        r = U.run_full_audit(system_state={"fatigue_score": 9.0})
        self.assertNotEqual(r.severity, U.NOT_DETERMINABLE)
        self.assertIsNone(r.not_determinable_reason)

    def test_reason_function_direct(self):
        f = U._not_determinable_reason
        self.assertEqual(f([]), U.NO_MODULES_RUN)
        self.assertEqual(f(["UNKNOWN"]), U.ALL_INPUTS_UNKNOWN)
        self.assertEqual(f(["not_a_label"]), U.ALL_MODULES_GAP_INSTRUMENT)
        self.assertEqual(f(["UNKNOWN", "x"]), U.MIXED_UNKNOWN_AND_GAP_INSTRUMENT)
        self.assertIsNone(f(["UNKNOWN", "GREEN"]))


class PipelineNotMeasured(unittest.TestCase):

    def test_no_modules_not_measured(self):
        self.assertEqual(PL._aggregate({}), (None, PL.NOT_MEASURED, PL.NO_MODULES_RUN))

    def test_modules_ran_no_reason(self):
        r = PL.run_unified_audit({"system_id": "s"})
        self.assertIsNone(r["not_measured_reason"])
        self.assertNotEqual(r["unified_band"], PL.NOT_MEASURED)


if __name__ == "__main__":
    unittest.main()
