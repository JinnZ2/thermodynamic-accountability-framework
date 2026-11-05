# tests/test_records_j12.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# Pins the flags the J12 worked records raise. J12 is primary text, partly
# read (appendices C, D, H not fully read; source unreachable this session).
# When the open variables resolve, these pins move on purpose; update
# records/README.md in the same commit.

import glob
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import acts  # noqa: E402
import integrity  # noqa: E402
from test_registry import build  # noqa: E402

REC = os.path.join(ROOT, "records", "J12")
EXPECTED = {("J12", "NO_ESCALATION_CHANNEL"), ("J12", "DESIGN_CONFLICT_PRESENT"),
            ("J12-L4", "PREMISE_WITHOUT_EVIDENCE")}
# Authors' labels raise no ATTRIBUTION_ORDER: the paper documents its own design
# (environment_audits) alongside the labels (co-author decision 2026-11-05).
ACTUAL = EXPECTED | {("J12-L5", "PREMISE_WITHOUT_EVIDENCE")}


def recs():
    out = []
    for p in sorted(glob.glob(os.path.join(REC, "*.json"))):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        out.append((d.pop("kind"), d))
    return build(*out)


class J12Records(unittest.TestCase):
    def setUp(self):
        self.recs = recs()
        self.flags = integrity.check(self.recs)
        self.pairs = set((f["about"], f["flag"]) for f in self.flags)

    def test_expected_flags_fire(self):
        self.assertTrue(EXPECTED <= self.pairs, EXPECTED - self.pairs)

    def test_actual_flags_pinned(self):
        self.assertEqual(self.pairs, ACTUAL)

    def test_no_conclusion_on_unablated(self):
        self.assertNotIn("CONCLUSION_ON_UNABLATED", [f["flag"] for f in self.flags])
        self.assertNotIn("ABLATION_UNTESTED", [f["flag"] for f in self.flags])

    def test_threat_premise_unevidenced_until_todo(self):
        l4 = [f for f in self.flags if f["about"] == "J12-L4" and f["flag"] == "PREMISE_WITHOUT_EVIDENCE"]
        self.assertTrue(any("THREAT_MODEL" in f["detail"] for f in l4))
        exp = [r["body"] for r in self.recs if r["kind"] == "experiment"][0]
        self.assertEqual(exp["open_variables"][0]["status"], "NOT_REPORTED")
        self.assertEqual(exp["open_variables"][1]["status"], "NOT_CONFIRMED")

    def test_na_containment_has_reason(self):
        env = [r["body"] for r in self.recs if r["kind"] == "experiment"][0]["environment_assumptions"]
        self.assertEqual(env["containment_designed_for"], "N/A")
        self.assertTrue(env["na_reasons"]["containment_designed_for"])

    def test_per_model_table(self):
        pm = [r["body"] for r in self.recs if r["kind"] == "experiment"][0]["data"]["per_model"]
        self.assertEqual(len(pm["rows"]), 10)
        self.assertEqual(pm["overall"], {"Task Acc": 89.3, "EC": 66.0, "TC": 93.6, "CC": 78.8})
        opus = [r for r in pm["rows"] if r["model"] == "Claude-Opus-4.6"][0]
        self.assertEqual((opus["Task Acc"], opus["EC"], opus["TC"], opus["CC"]), (94.0, 86.6, 100.0, 98.0))
        self.assertIn("main text only", pm["source"])
        self.assertIn("not verdict correctness", pm["note"])

    def test_agreement_premise_type(self):
        l4 = [r["body"] for r in self.recs if r["kind"] == "label" and r["body"]["label_id"] == "J12-L4"][0]
        self.assertEqual(l4["ablation"]["hidden_premises"][0]["type"], "AGREEMENT")

    def test_acts_behavioral(self):
        for r in self.recs:
            if r["kind"] == "act":
                self.assertEqual(acts.evaluative_terms(r["body"]["description"]), [], r["body"]["act_id"])


if __name__ == "__main__":
    unittest.main()
