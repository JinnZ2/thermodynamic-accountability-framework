# tests/test_records_j10.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# Pins the flags the J10 worked records actually raise (records/J10*.json).
# These are the first non-synthetic records; they are sourced and thin.
# If a rule changes, this test moves on purpose: update the pins and the
# records/README.md table in the same commit.

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import schema  # noqa: E402
from test_registry import EVALUATIVE, build, codes  # noqa: E402

REC = os.path.join(ROOT, "records")

ACTUAL = {
    "J10a": ["MISSING_FIELD", "INCENTIVES_UNRECORDED", "NO_FRAMING_CHECK", "LOWER_LAYER_SECONDHAND",
             "SUBJECT_OPEN"],
    "J10b": ["MISSING_FIELD", "SOURCE_UNTRACEABLE", "INCENTIVES_UNRECORDED", "NO_FRAMING_CHECK"],
    "J10c": ["NO_FRAMING_CHECK"],
}


def load(jid):
    with open(os.path.join(REC, jid + ".json"), encoding="utf-8") as f:
        return json.load(f)


class J10Records(unittest.TestCase):
    def setUp(self):
        self.recs = build(*[("judgment", load(j)) for j in sorted(ACTUAL)])

    def test_flags_pinned(self):
        for jid, want in ACTUAL.items():
            self.assertEqual(codes(self.recs, jid), want, jid)

    def test_mechanism_subclaim_status(self):
        ev = load("J10b")["evidence"]
        self.assertIn("CONTRADICTED_BY_SOURCE", [e.get("status") for e in ev])

    def test_missing_variables_recorded(self):
        for jid in ACTUAL:
            self.assertGreaterEqual(len(load(jid)["missing_variables"]), 6, jid)

    def test_status_values_neutral(self):
        words = set(w for v in schema.EVIDENCE_STATUS for w in v.lower().split("_"))
        self.assertEqual(sorted(words & set(EVALUATIVE)), [])


class NewFlagRules(unittest.TestCase):
    """LOWER_LAYER_SECONDHAND and SOURCE_UNTRACEABLE (2026-11-05), synthetic variations."""

    def flags(self, d):
        return codes(build(("judgment", d)), d["judgment_id"])

    def test_firsthand_basis_clears_secondhand_flag(self):
        d = load("J10a")
        d["layer_basis"]["sensor"]["reporter_relation"] = "FIRSTHAND"
        self.assertNotIn("LOWER_LAYER_SECONDHAND", self.flags(d))

    def test_unstated_relation_raises_nothing(self):
        d = load("J10a")
        for n in ("physics", "sensor"):
            d["layer_basis"][n].pop("reporter_relation")
        self.assertNotIn("LOWER_LAYER_SECONDHAND", self.flags(d))

    def test_secondhand_via_dependency(self):
        d = load("J10a")
        dep = load("J10c")
        dep["layer_basis"]["sensor"]["reporter_relation"] = "SECONDHAND"
        d["layer_basis"] = {"agency": d["layer_basis"]["agency"],
                            "interpretation": d["layer_basis"]["interpretation"]}
        d["depends_on_layers"] = ["J10c"]
        recs = build(("judgment", dep), ("judgment", d))
        self.assertIn("LOWER_LAYER_SECONDHAND", codes(recs, "J10a"))

    def test_source_untraceable_needs_both_unknown_and_no_locator(self):
        d = load("J10b")
        self.assertIn("SOURCE_UNTRACEABLE", self.flags(d))
        d["source_trace"]["locator"] = "comment permalink (synthetic)"
        self.assertNotIn("SOURCE_UNTRACEABLE", self.flags(d))
        d = load("J10b")
        d["source_trace"]["date_known"] = True
        self.assertNotIn("SOURCE_UNTRACEABLE", self.flags(d))

    def test_bad_shapes_rejected(self):
        d = load("J10b")
        d["source_trace"] = {"author_known": "no"}
        self.assertTrue(schema.Judgment.from_dict(d).shape_problems())
        d = load("J10a")
        d["layer_basis"]["sensor"]["reporter_relation"] = "HEARSAY"
        self.assertTrue(schema.Judgment.from_dict(d).shape_problems())


class EvidenceStatusShape(unittest.TestCase):
    def test_unknown_status_rejected(self):
        d = load("J10b")
        d["evidence"][0]["status"] = "REFUTED"
        self.assertTrue(schema.Judgment.from_dict(d).shape_problems())

    def test_missing_variables_shape(self):
        d = load("J10a")
        d["missing_variables"] = "transcript"
        self.assertTrue(schema.Judgment.from_dict(d).shape_problems())


if __name__ == "__main__":
    unittest.main()
