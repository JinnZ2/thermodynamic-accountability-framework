# tests/test_records_j14.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# Pins the J14 worked records (weight-space programming blog post, read
# via summarizing fetch tool; values unverified against the page).

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

REC = os.path.join(ROOT, "records", "J14")


def load(p):
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    return d.pop("kind"), d


def recs():
    return build(*[load(p) for p in sorted(glob.glob(os.path.join(REC, "*.json")))])


class J14Records(unittest.TestCase):
    def setUp(self):
        self.recs = recs()
        self.exp = [r["body"] for r in self.recs if r["kind"] == "experiment"][0]

    def test_no_flags(self):
        self.assertEqual(integrity.check(self.recs), [])

    def test_counts_and_behavioral(self):
        kinds = [r["kind"] for r in self.recs]
        self.assertEqual((kinds.count("act"), kinds.count("label")), (6, 2))
        for r in self.recs:
            if r["kind"] == "act":
                self.assertEqual(acts.evaluative_terms(r["body"]["description"]), [], r["body"]["act_id"])

    def test_exp8_and_control(self):
        d = self.exp["data"]
        self.assertEqual(d["exp8"]["held_out"]["MATH-500"], [7.9, 48.1])
        self.assertEqual(d["exp8"]["MATH-500_at_passes"], {"10": 12.3, "25": 14.1, "50": 48.1})
        self.assertEqual(d["control"]["MATH-500"], [6.8, 7.7])
        self.assertEqual(d["exp5_6"]["minatar"]["rows"]["Breakout"], [15.8, 25.3, 517.4])
        self.assertEqual(d["exp5_6"]["go_9x9"]["exact_win_rates"], "NOT_REPORTED in the post")

    def test_na_with_reasons(self):
        env = self.exp["environment_assumptions"]
        self.assertEqual((env["containment_designed_for"], env["escalation_channel"]), ("N/A", "N/A"))
        self.assertEqual(sorted(env["na_reasons"]), ["containment_designed_for", "escalation_channel"])

    def test_labels(self):
        labs = dict((r["body"]["label_id"], r["body"]) for r in self.recs if r["kind"] == "label")
        self.assertEqual(labs["J14-L1"]["ablation"]["conclusion_survives"], "PARTIAL")
        self.assertEqual(labs["J14-L1"]["ablation"]["hidden_premises"][0]["type"], "CHANGE_IN_KIND")
        self.assertEqual(labs["J14-L2"]["ablation"]["conclusion_survives"], "YES")
        for lb in labs.values():
            self.assertEqual(lb["social_assumption_tags"], ["INSTITUTIONAL", "SAME_DOMAIN"])


class Register(unittest.TestCase):
    def test_m33_and_dm16(self):
        with open(os.path.join(os.path.dirname(ROOT), "docs", "misuse_register.json"), encoding="utf-8") as f:
            reg = json.load(f)
        m33 = [e for e in reg["entries"] if e["id"] == "M33"][0]
        self.assertEqual((m33["status"], m33["mitigation_ids"]), ("PROPOSED", []))
        dm = dict((m["id"], m) for m in reg["mitigations"])
        self.assertTrue(dm["D-M10"]["description"].startswith("Head record"))   # unchanged
        self.assertEqual(dm["D-M16"]["code"], "NOT BUILT")


if __name__ == "__main__":
    unittest.main()
