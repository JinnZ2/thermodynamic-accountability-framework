# tests/test_intervention.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
# SYNTHETIC fixtures only ("signal-s", "band-b1" are placeholders).
# J6-J9 real-world records are NOT entered here.

import json
import os
import re
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import cli  # noqa: E402
import integrity  # noqa: E402
import ledger  # noqa: E402
import report  # noqa: E402
from test_registry import EVALUATIVE, J, build  # noqa: E402

AS_OF = "2000-06-01"


def IV(iid, **kw):
    base = {"intervention_id": iid, "version": "1", "system_class": "human", "signal": "signal-s",
            "direction": "RECALIBRATE", "layer_targeted": "sensor",
            "distance_from_band": {"measure": "m1", "value": 1.5, "band_definition": "band-b1 0-1 units",
                                   "band_system_class": "human", "source": "S"},
            "duration": {"planned": "2 weeks", "planned_end": "2000-01-15", "actual": None,
                         "type": "BOUNDED", "review_date": None},
            "reversibility": "REVERSIBLE", "loop_status": "CLOSED", "consent": "GIVEN",
            "cause_addressed": True, "purpose": "Stated purpose text.", "intervener": "role-1",
            "observed_outcome": [{"effect": "effect-1", "tag": "OBSERVED", "source": "S"}],
            "date": "2000-01-01", "environment": {"other": "env-1"}, "volume": "thin",
            "status": "OBSERVED", "recorder": "rec-01", "source": "S"}
    base.update(kw)
    return base


def icodes(recs):
    return [f["flag"] for f in integrity.check(recs, as_of=AS_OF)]


class InterventionFlagTests(unittest.TestCase):
    def test_complete_record_no_flags(self):
        self.assertEqual(icodes(build(("intervention", IV("i1")))), [])

    def test_suppress_cause_unstated(self):
        recs = build(("intervention", IV("i1", direction="SUPPRESS", cause_addressed=None)))
        self.assertEqual(icodes(recs), ["CAUSE_STATUS_UNSTATED"])

    def test_cause_null_on_amplify_does_not_flag(self):
        self.assertEqual(icodes(build(("intervention", IV("i1", direction="AMPLIFY", cause_addressed=None)))), [])

    def test_open_ended_without_review(self):
        dur = {"planned": "indefinite", "type": "OPEN_ENDED", "review_date": None}
        self.assertEqual(icodes(build(("intervention", IV("i1", duration=dur)))), ["OPEN_ENDED_WITHOUT_REVIEW"])
        dur["review_date"] = "2000-03-01"
        self.assertEqual(icodes(build(("intervention", IV("i1", duration=dur)))), [])

    def test_human_band_on_model_record(self):
        steps = [("intervention", IV("i1", system_class="model"))]
        got = [f for f in integrity.check(build(*steps), as_of=AS_OF)]
        self.assertEqual([f["flag"] for f in got], ["CROSS_SYSTEM_BAND"])
        self.assertIn("'human'", got[0]["detail"])
        self.assertIn("'model'", got[0]["detail"])
        steps.append(("transfer", {"intervention_id": "i1", "reason": "Stated reason for using this band."}))
        self.assertEqual(icodes(build(*steps)), [])

    def test_outcome_unrecorded_past_planned_end(self):
        recs = build(("intervention", IV("i1", observed_outcome=[])))
        self.assertEqual(icodes(recs), ["OUTCOME_UNRECORDED"])
        self.assertEqual([f["flag"] for f in integrity.check(recs, as_of="2000-01-10")], [])

    def test_outcome_unrecorded_when_actual_set(self):
        dur = {"planned": "1 day", "planned_end": None, "actual": "1 day", "type": "BRIDGE"}
        self.assertEqual(icodes(build(("intervention", IV("i1", duration=dur, observed_outcome=[])))),
                         ["OUTCOME_UNRECORDED"])

    def test_each_unstated_field(self):
        recs = build(("intervention", IV("i1", direction=None, reversibility=None, loop_status=None,
                                         consent=None, duration={"planned": "x"},
                                         distance_from_band={"measure": "m1", "value": 2})))
        self.assertEqual(sorted(icodes(recs)),
                         ["BAND_UNDEFINED", "CONSENT_UNSTATED", "DIRECTION_UNSTATED",
                          "DURATION_TYPE_UNSTATED", "LOOP_UNSTATED", "REVERSIBILITY_UNSTATED"])

    def test_judgment_link(self):
        recs = build(("intervention", IV("i1")), ("judgment", J("j1", intervention_id="i1")))
        self.assertEqual(icodes(recs), [])
        recs = build(("judgment", J("j1", intervention_id="i9")))
        self.assertEqual(icodes(recs), ["INTERVENTION_NOT_FOUND"])


class InterventionShapeTests(unittest.TestCase):
    def test_rejections(self):
        for bad in (IV("i1", direction="DIM"), IV("i1", system_class="robot"), IV("i1", reversibility="MAYBE"),
                    IV("i1", loop_status="HALF"), IV("i1", consent="IMPLIED"), IV("i1", cause_addressed="yes"),
                    IV("i1", layer_targeted="agency"), IV("i1", status="GUESS"),
                    IV("i1", duration={"type": "FOREVER"}), IV("i1", duration={"extra": 1}),
                    IV("i1", distance_from_band={"score": 3}),
                    IV("i1", observed_outcome=[{"effect": "e", "tag": "GUESS"}]), dict(IV("i1"), severity=1),
                    IV("")):
            with self.assertRaises(ledger.LedgerError):
                ledger.append_records([], "intervention", bad)

    def test_duplicate_id_refused(self):
        with self.assertRaises(ledger.LedgerError):
            ledger.append_records(build(("intervention", IV("i1"))), "intervention", IV("i1", version="2"))

    def test_n_of_1_template_loads_once_filled(self):
        with open(os.path.join(ROOT, "templates", "intervention_n_of_1_recalibrate.json")) as f:
            body = json.load(f)
        kind = body.pop("kind")
        with self.assertRaises(ledger.LedgerError):
            ledger.append_records([], kind, body)       # empty id is refused until filled
        body["intervention_id"] = "n1"
        recs = ledger.append_records([], kind, body)
        self.assertEqual(recs[0]["body"]["calibration"]["calibration_log"], [])


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.recs = build(("intervention", IV("i-bridge", direction="SUPPRESS",
                                              duration={"planned": "6 h", "type": "BRIDGE"})),
                          ("intervention", IV("i-open", direction="SUPPRESS", cause_addressed=False,
                                              duration={"planned": "indefinite", "type": "OPEN_ENDED",
                                                        "review_date": None})))

    def test_axis_lists_all_variables(self):
        out = report.axis(self.recs, "i-bridge")
        for k in report.ROWS:
            self.assertIn(k, out)
        self.assertIn("BRIDGE", out)

    def test_compare_side_by_side(self):
        out = report.compare(self.recs, "i-bridge", "i-open")
        self.assertIn("i-bridge", out)
        self.assertIn("OPEN_ENDED", out)
        self.assertIn("False", out)

    def test_no_computed_score_field(self):
        for out in (report.axis(self.recs, "i-open"), report.compare(self.recs, "i-bridge", "i-open")):
            low = out.lower()
            for w in ("score", "severity", "rank", "total", "rating", "harm"):
                self.assertNotIn(w, low, w)
        self.assertEqual(set(k for k, _ in report.axis_rows(IV("x"))), set(report.ROWS))

    def test_cli_axis(self):
        d = tempfile.mkdtemp()
        try:
            led = os.path.join(d, "j.jsonl")
            for iid in ("a", "b"):
                p = os.path.join(d, iid + ".json")
                with open(p, "w") as f:
                    json.dump(dict(IV(iid), kind="intervention"), f)
                self.assertEqual(cli.main(["add", p, "--ledger", led]), 0)
            self.assertEqual(cli.main(["axis", "a", "--ledger", led]), 0)
            self.assertEqual(cli.main(["axis", "--compare", "a", "b", "--ledger", led]), 0)
            self.assertEqual(cli.main(["check", "--as-of", AS_OF, "--ledger", led]), 0)
        finally:
            shutil.rmtree(d)


class InterventionNeutralityTest(unittest.TestCase):
    def test_new_flag_strings(self):
        recs = build(("intervention", IV("i1", direction=None, reversibility=None, loop_status=None, consent=None,
                                         duration={"type": "OPEN_ENDED"}, distance_from_band={"value": 1},
                                         observed_outcome=[])),
                     ("intervention", IV("i2", direction="SUPPRESS", cause_addressed=None, system_class="model",
                                         duration={"actual": "3 days", "type": "BRIDGE"}, observed_outcome=[])),
                     ("judgment", J("j1", intervention_id="zz")))
        flags = integrity.check(recs, as_of=AS_OF)
        want = {"DIRECTION_UNSTATED", "BAND_UNDEFINED", "OPEN_ENDED_WITHOUT_REVIEW", "REVERSIBILITY_UNSTATED",
                "LOOP_UNSTATED", "CONSENT_UNSTATED", "CAUSE_STATUS_UNSTATED", "OUTCOME_UNRECORDED",
                "CROSS_SYSTEM_BAND", "INTERVENTION_NOT_FOUND"}
        self.assertTrue(want <= set(f["flag"] for f in flags), set(f["flag"] for f in flags))
        for f in flags:
            words = set(re.findall(r"[a-z]+", (f["flag"] + " " + f["detail"]).lower().replace("_", " ")))
            self.assertEqual(sorted(words & set(EVALUATIVE)), [], f)


if __name__ == "__main__":
    unittest.main()
