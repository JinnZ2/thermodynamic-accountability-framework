# tests/test_defenses.py -- CC0, stdlib unittest
# Provenance: co-authored (Kavik + Claude).

import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import chain  # noqa: E402
import defenses as d  # noqa: E402

PLAIN = "County offers two pallets of drinking water for the clinic."


class AidTests(unittest.TestCase):
    def aid(self, conditions, cat="state"):
        return d.AidRecord(cat, "State emergency office", "water_potable", conditions, PLAIN)

    def test_clean_aid_still_needs_human(self):
        s = d.aid_status(self.aid(["delivered to the fire hall by Friday"]))
        self.assertEqual(s["state"], "NO_TERMS_FLAGGED")
        self.assertTrue(s["needs_human_review"])

    def test_control_terms_flagged(self):
        cases = ["distribution only through our staff",
                 "community must register all residents",
                 "provide a full inventory of fuel holdings",
                 "security personnel stationed at the depot",
                 "in exchange for authority over the water plant",
                 "repayment due within 90 days"]
        for c in cases:
            s = d.aid_status(self.aid([c]))
            self.assertEqual(s["state"], "CONTROL_TERMS_FLAGGED", c)

    def test_unknown_source_flagged(self):
        self.assertEqual(d.aid_status(self.aid([], cat="unknown"))["state"], "CONTROL_TERMS_FLAGGED")

    def test_incomplete_aid(self):
        a = d.AidRecord("rebels", "", "fuel_stock", [], "x")
        self.assertEqual(d.aid_status(a)["state"], "INCOMPLETE")


class ClaimTests(unittest.TestCase):
    def test_claim_about_other_community_needs_direct_contact(self):
        c = d.Claim("B", "Community B is hoarding fuel and plans to cut our road.", ["r1", "r2", "r3"])
        self.assertEqual(d.claim_status(c, "A")["state"], "DO_NOT_ACT")
        c.direct_contact = "radio call with B council, 2026-12-02"
        self.assertEqual(d.claim_status(c, "A")["state"], "ACTIONABLE")

    def test_single_source_caution_only(self):
        c = d.Claim("A", "The well on the north road is contaminated, do not drink.", ["r1"])
        self.assertEqual(d.claim_status(c, "A")["state"], "CAUTION_ONLY")

    def test_duplicate_sources_count_once(self):
        c = d.Claim("A", "The well on the north road is contaminated, do not drink.", ["r1", "r1"])
        self.assertEqual(d.claim_status(c, "A")["state"], "CAUTION_ONLY")

    def test_quarantined_source_not_counted(self):
        q = d.Quarantine("A")
        q.add("r2", "human:council", "sent three false reports about the bridge last week")
        c = d.Claim("A", "The well on the north road is contaminated, do not drink.", ["r1", "r2"])
        s = d.claim_status(c, "A", q)
        self.assertEqual(s["state"], "CAUTION_ONLY")
        self.assertEqual(s["quarantined_sources"], ["r2"])


class QuarantineTests(unittest.TestCase):
    def test_local_human_only_and_needs_reason(self):
        q = d.Quarantine("A")
        with self.assertRaises(ValueError):
            q.add("ai:n9", "ai:n1", "it seems suspicious to me today")
        with self.assertRaises(ValueError):
            q.add("ai:n9", "human:council", "bad")
        q.add("ai:n9", "human:council", "node proposed exchanges nobody in either town asked for")
        self.assertTrue(q.blocks("ai:n9"))
        recs = [{"source": "ai:n9", "x": 1}, {"source": "ai:n1", "x": 2}]
        self.assertEqual(q.filter(recs), [{"source": "ai:n1", "x": 2}])
        q.remove("ai:n9", "human:council")
        self.assertFalse(q.blocks("ai:n9"))

    def test_quarantine_is_per_community(self):
        qa, qb = d.Quarantine("A"), d.Quarantine("B")
        qa.add("ai:n9", "human:council", "node proposed exchanges nobody in either town asked for")
        self.assertFalse(qb.blocks("ai:n9"))


class RegistryTests(unittest.TestCase):
    def test_trust_vetters_seeded_and_chain_valid(self):
        items = chain.load()
        self.assertIn("trust_vetters", items)
        self.assertTrue(chain.is_clean(chain.validate(items)))

    def test_register_has_r8_and_defenses(self):
        with open(os.path.join(ROOT, "coordination_register.json")) as f:
            reg = json.load(f)
        ids = [r["id"] for r in reg["risks"]]
        self.assertIn("R8", ids)
        self.assertEqual([x["id"] for x in reg["defenses"]], ["D1", "D2", "D3", "D4", "D5"])
        self.assertIn("B6", [b["id"] for b in reg["backups"]])
        e = dict((x["id"], x) for x in reg["experiments"])
        self.assertIn("historical", e["E7"]["question"].lower())
        self.assertIn("manual capability", e["E9"]["question"])


if __name__ == "__main__":
    unittest.main()
