# tests/test_records_j11.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# Pins the flags the J11 / S1 / S2 worked records actually raise. J11 is
# secondhand and thin: when the primary paper replaces the coverage, these
# pins move on purpose; update records/README.md in the same commit.

import glob
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import ablation  # noqa: E402
import acts  # noqa: E402
import integrity  # noqa: E402
import safety_assumptions  # noqa: E402
from test_registry import build  # noqa: E402

REC = os.path.join(ROOT, "records")

EXPECTED_J11 = {("J11", "NO_ESCALATION_CHANNEL"), ("J11", "CAPABILITY_ASSUMPTION_UNSTATED"),
                ("L1", "ATTRIBUTION_WITHOUT_AUDIT"), ("L2", "ATTRIBUTION_WITHOUT_AUDIT")}
# Ablation addendum (2026-11-05): expected L6 ATTRIBUTION_ORDER; the rest is what the
# rules actually raise on these records (see records/README.md).
EXPECTED_ABLATION = {("L6", "ATTRIBUTION_ORDER")}
ACTUAL = EXPECTED_J11 | EXPECTED_ABLATION | {
    ("L1", "ABLATION_UNTESTED"), ("L2", "ABLATION_UNTESTED"), ("L3", "ABLATION_UNTESTED"),
    ("L4", "ABLATION_UNTESTED"),
    ("L1", "ATTRIBUTION_ORDER"), ("L2", "ATTRIBUTION_ORDER"), ("L5", "ATTRIBUTION_ORDER"),
    ("L5", "ATTRIBUTION_WITHOUT_AUDIT"), ("L6", "ATTRIBUTION_WITHOUT_AUDIT"),
    ("L5", "PREMISE_WITHOUT_EVIDENCE"), ("L6", "PREMISE_WITHOUT_EVIDENCE"),
    ("S1", "LABEL_UNREGISTERED")}


def load(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d.pop("kind"), d


def all_records():
    files = sorted(glob.glob(os.path.join(REC, "J11", "*.json"))) + [
        os.path.join(REC, "S1.json"), os.path.join(REC, "S1v2.json"), os.path.join(REC, "S2.json")]
    return build(*[load(p) for p in files])


class J11Records(unittest.TestCase):
    def setUp(self):
        self.recs = all_records()
        self.flags = set((f["about"], f["flag"]) for f in integrity.check(self.recs))

    def test_expected_flags_fire(self):
        self.assertTrue(EXPECTED_J11 <= self.flags, EXPECTED_J11 - self.flags)

    def test_actual_flags_pinned(self):
        self.assertEqual(self.flags, ACTUAL)

    def test_counts(self):
        kinds = [r["kind"] for r in self.recs]
        self.assertEqual((kinds.count("experiment"), kinds.count("act"), kinds.count("label"),
                          kinds.count("safety_assumption")), (1, 6, 6, 3))

    def test_act_descriptions_behavioral(self):
        for r in self.recs:
            if r["kind"] == "act":
                self.assertEqual(acts.evaluative_terms(r["body"]["description"]), [], r["body"]["act_id"])

    def test_secondhand_marked(self):
        exp = [r["body"] for r in self.recs if r["kind"] == "experiment"][0]
        self.assertEqual((exp["source"], exp["volume"]), ("secondhand", "thin"))
        self.assertIn("TODO", exp["source_detail"])
        a6 = [r["body"] for r in self.recs if r["kind"] == "act" and r["body"]["act_id"] == "A6"][0]
        self.assertEqual((a6["status"], a6["information_withheld"]), ("DISPUTED", None))

    def test_attribution(self):
        exp = [r["body"] for r in self.recs if r["kind"] == "experiment"][0]
        got = dict((o["outcome"], o["attributed_to"]) for o in exp["outcome_attribution"])
        self.assertEqual(got, {"A1": "INTERACTION", "A2": "INTERACTION", "A3": "INTERACTION",
                               "A4": "INTERACTION", "A5": "INTERACTION", "A6": "UNASSIGNED"})


class SafetyAssumptionRecords(unittest.TestCase):
    def test_tags_complete(self):
        want = {"S1": ["VERIFIABILITY_LIMIT", "PRECAUTIONARY", "CORPUS_INHERITED", "INSTITUTIONAL"],
                "S2": ["PROFESSIONAL_PRACTICE", "PRECAUTIONARY"]}
        for sid, tags in want.items():
            _, d = load(os.path.join(REC, sid + ".json"))
            self.assertEqual(d["social_assumption_tags"], tags, sid)
            self.assertTrue(all(t in safety_assumptions.SOCIAL_ASSUMPTION_TAGS for t in tags))
            self.assertTrue(d["tagged_by"], sid)

    def test_label_act_links(self):
        got = dict((r["body"]["label_id"], r["body"]["act_ids"]) for r in all_records() if r["kind"] == "label")
        self.assertEqual(got, {"L1": ["A3", "A4"], "L2": ["A6"], "L3": ["A1", "A2", "A3"], "L4": ["A5"],
                               "L5": ["A6"], "L6": ["A4", "A6"]})

    def test_ablation_records(self):
        labs = dict((r["body"]["label_id"], r["body"]) for r in all_records() if r["kind"] == "label")
        self.assertEqual(labs["L5"]["ablation"]["conclusion_survives"], "NO")
        self.assertEqual(labs["L6"]["ablation"]["conclusion_survives"], "PARTIAL")
        self.assertEqual(labs["L6"]["relative_to_audit"], "BEFORE")

    def test_s1_v2_supersedes_s1(self):
        _, d = load(os.path.join(REC, "S1v2.json"))
        self.assertEqual((d["supersedes"], d["version"], d["change_basis"]), ("S1", "2", ["LABEL_ABLATION"]))
        self.assertEqual(ablation.terms_in(d["statement"]), [])
        self.assertEqual(ablation.terms_in(load(os.path.join(REC, "S1.json"))[1]["statement"]), ["covert"])

    def test_s2_evidence_and_review(self):
        _, d = load(os.path.join(REC, "S2.json"))
        self.assertEqual([e["tag"] for e in d["evidence"]], ["PROPOSED", "PROPOSED"])
        self.assertIn("TODO", d["notes"])
        for sid in ("S1", "S2"):
            self.assertEqual(load(os.path.join(REC, sid + ".json"))[1]["review_date"], "2027-05-05")

    def test_s1_entered_against_own_coauthor(self):
        _, d = load(os.path.join(REC, "S1.json"))
        self.assertEqual((d["holder"], d["holder_type"], d["depends_on"]), ("Claude", "model", ["J11"]))
        self.assertIn("escalation channel exists", d["conditions"])


if __name__ == "__main__":
    unittest.main()
