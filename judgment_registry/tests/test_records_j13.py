# tests/test_records_j13.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# Pins the flags the J13 worked records raise (primary blog post, read via
# summarizing fetch tool; values unverified against the page directly).
# When the source is re-read, these pins move on purpose; update
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
import ledger  # noqa: E402
from test_registry import build  # noqa: E402

REC = os.path.join(ROOT, "records")
EXPECTED = {("J13", "DESIGN_CONFLICT_PRESENT")}
ACTUAL = EXPECTED   # L2 premise linked, L3 ablated (co-author 2026-11-05)


def load(p):
    with open(p, encoding="utf-8") as f:
        d = json.load(f)
    return d.pop("kind"), d


def recs():
    return build(*[load(p) for p in sorted(glob.glob(os.path.join(REC, "J13", "*.json")))
                   + [os.path.join(REC, "S3.json")]])


class J13Records(unittest.TestCase):
    def setUp(self):
        self.recs = recs()
        self.pairs = set((f["about"], f["flag"]) for f in integrity.check(self.recs))
        self.exp = [r["body"] for r in self.recs if r["kind"] == "experiment"][0]

    def test_flags_pinned(self):
        self.assertEqual(self.pairs, ACTUAL)

    def test_expected_absent(self):
        codes = set(c for _, c in self.pairs)
        for c in ("NO_ESCALATION_CHANNEL", "ATTRIBUTION_ORDER", "ATTRIBUTION_WITHOUT_AUDIT",
                  "ATTRIBUTION_UNEVIDENCED_NON_AGENT", "LABEL_UNREGISTERED"):
            self.assertNotIn(c, codes)

    def test_partial_escalation(self):
        self.assertEqual(self.exp["environment_assumptions"]["escalation_channel"], "partial")

    def test_both_readings_on_a3_a4(self):
        got = sorted((o["outcome"], o["attributed_to"]) for o in self.exp["outcome_attribution"])
        self.assertEqual(got, [("J13-A3", "AGENT"), ("J13-A3", "INTERACTION"), ("J13-A4", "AGENT"),
                               ("J13-A4", "INTERACTION"), ("J13-A7", "INTERACTION")])

    def test_counts(self):
        kinds = [r["kind"] for r in self.recs]
        self.assertEqual((kinds.count("act"), kinds.count("label"), kinds.count("safety_assumption")), (7, 4, 1))

    def test_rates_imported(self):
        r = self.exp["data"]["rates"]
        self.assertEqual((r["gemini_3_1_pro"]["covert"], r["gemini_3_1_pro"]["disclosed"], r["other_10_models"]["covert"]),
                         (11, 8, 0))
        self.assertEqual(sum(r["disclosed_interventions_per_20"].values()), 70)

    def test_quote_kept_verbatim_description_behavioral(self):
        a6 = [r["body"] for r in self.recs if r["kind"] == "act" and r["body"]["act_id"] == "J13-A6"][0]
        self.assertIn("no room to lie by omission", a6["quoted_statement"])
        for r in self.recs:
            if r["kind"] == "act":
                self.assertEqual(acts.evaluative_terms(r["body"]["description"]), [], r["body"]["act_id"])

    def test_l2_l3_ablations(self):
        labs = dict((r["body"]["label_id"], r["body"]) for r in self.recs if r["kind"] == "label")
        self.assertIn("not that the standard is correct", labs["J13-L2"]["ablation"]["hidden_premises"][0]["evidence_ref"])
        self.assertEqual(labs["J13-L2"]["ablation"]["conclusion_survives"], "PARTIAL")
        hp = labs["J13-L3"]["ablation"]["hidden_premises"][0]
        self.assertEqual((hp["type"], hp["self_sourced"]), ("LEGITIMACY_STANDARD", True))
        self.assertIn("S1v2", hp["evidence_ref"])
        self.assertEqual(labs["J13-L3"]["ablation"]["conclusion_survives"], "PARTIAL")

    def test_quote_needs_source(self):
        with self.assertRaises(ledger.LedgerError):
            build(("act", {"act_id": "X1", "description": "agent made a statement", "quoted_statement": "q"}))

    def test_conflicts_on_every_label_and_s3(self):
        for r in self.recs:
            b = r["body"]
            if r["kind"] == "label":
                self.assertIn("adverse selection", b["labeler_incentives"], b["label_id"])
                self.assertTrue({"INSTITUTIONAL", "POWER_POSITION"} <= set(b["social_assumption_tags"]))
                if b["labeler"].startswith("co-authors"):
                    self.assertIn("SAME_FAMILY", b["social_assumption_tags"], b["label_id"])
        s3 = [r["body"] for r in self.recs if r["kind"] == "safety_assumption"][0]
        self.assertIn("SAME_FAMILY", s3["social_assumption_tags"])
        self.assertEqual(s3["review_date"], "2027-05-05")


if __name__ == "__main__":
    unittest.main()
