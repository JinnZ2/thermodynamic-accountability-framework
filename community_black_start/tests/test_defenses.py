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
        self.assertEqual(d.claim_status(c, "A", independence_mode="ids")["state"], "ACTIONABLE")
        self.assertEqual(d.claim_status(c, "A")["state"], "CAUTION_ONLY")   # default: no paths recorded

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
        s = d.claim_status(c, "A", q, "ids")
        self.assertEqual(s["state"], "CAUTION_ONLY")
        self.assertEqual(s["quarantined_sources"], ["r2"])


WELL = "The well on the north road is contaminated, do not drink."


class SybilTests(unittest.TestCase):
    """Candidate fix for the D3 Sybil gap (E10, PROPOSED): count independence
    by distinct contact paths, not distinct ids."""

    def test_two_ids_one_path_pass_ids_fail_paths(self):
        c = d.Claim("A", WELL, ["r1", "r2"],
                    contact_paths={"r1": "radio ch 3 north farm", "r2": "Radio  CH 3 north farm"})
        self.assertEqual(d.claim_status(c, "A", independence_mode="ids")["state"], "ACTIONABLE")   # the gap, ids mode
        s = d.claim_status(c, "A", independence_mode="contact_paths")
        self.assertEqual(s["state"], "CAUTION_ONLY")
        self.assertEqual(s["independence"]["shared_paths"], {"radio ch 3 north farm": ["r1", "r2"]})

    def test_distinct_paths_actionable(self):
        c = d.Claim("A", WELL, ["r1", "r2"],
                    contact_paths={"r1": "in person at the fire hall", "r2": "radio ch 3 north farm"})
        self.assertEqual(d.claim_status(c, "A", independence_mode="contact_paths")["state"], "ACTIONABLE")

    def test_unconfirmed_id_does_not_count(self):
        c = d.Claim("A", WELL, ["r1", "r2"], contact_paths={"r1": "in person at the fire hall"})
        s = d.claim_status(c, "A", independence_mode="contact_paths")
        self.assertEqual(s["state"], "CAUTION_ONLY")
        self.assertEqual(s["independence"]["unconfirmed_ids"], ["r2"])

    def test_quarantined_path_not_counted(self):
        q = d.Quarantine("A")
        q.add("r2", "human:council", "sent three false reports about the bridge last week")
        c = d.Claim("A", WELL, ["r1", "r2"],
                    contact_paths={"r1": "in person at the fire hall", "r2": "radio ch 3 north farm"})
        s = d.claim_status(c, "A", q, "contact_paths")
        self.assertEqual(s["state"], "CAUTION_ONLY")
        self.assertEqual(s["independence"]["distinct_contact_paths"], 1)

    def test_both_counts_always_reported(self):
        c = d.Claim("A", WELL, ["r1", "r2", "r3"], contact_paths={"r1": "x", "r2": "x"})
        ind = d.claim_status(c, "A")["independence"]
        self.assertEqual((ind["distinct_ids"], ind["distinct_contact_paths"]), (3, 1))

    def test_d5_still_first(self):
        c = d.Claim("B", "Community B is hoarding fuel and plans to cut our road.", ["r1", "r2"],
                    contact_paths={"r1": "a", "r2": "b"})
        self.assertEqual(d.claim_status(c, "A", independence_mode="contact_paths")["state"], "DO_NOT_ACT")

    def test_bad_mode_rejected(self):
        with self.assertRaises(ValueError):
            d.claim_status(d.Claim("A", WELL, ["r1"]), "A", independence_mode="votes")


class IndexTests(unittest.TestCase):
    def test_defense_index_matches_register_and_every_defense_has_r_links(self):
        with open(os.path.join(ROOT, "coordination_register.json")) as f:
            reg = json.load(f)
        self.assertEqual(sorted(d.DEFENSE_INDEX), sorted(x["id"] for x in reg["defenses"]))
        for x in reg["defenses"]:
            self.assertTrue(any(r.startswith("R") for r in x["against"]), x["id"])


class DefaultTests(unittest.TestCase):
    def test_default_is_contact_paths_after_t2(self):
        import inspect
        self.assertEqual(inspect.signature(d.claim_status).parameters["independence_mode"].default,
                         "contact_paths")
        with open(os.path.join(ROOT, "coordination_register.json")) as f:
            t2 = dict((x["id"], x) for x in json.load(f)["decisions"])["T2"]
        self.assertTrue(t2["result"]["rule_fired"])


class ThresholdTests(unittest.TestCase):
    """Decision T1: warn at 1 < act at 2 < certify at 3. Pinned so drift
    shows up as a red test, not a silent change."""

    def test_ladder_order(self):
        asm = os.path.join(os.path.dirname(ROOT), "assembly_instrument")
        if not os.path.isfile(os.path.join(asm, "status.py")):
            self.skipTest("assembly_instrument not beside community_black_start")
        sys.path.insert(0, asm)
        try:
            import status  # noqa
        finally:
            sys.path.remove(asm)
        self.assertEqual(d.ACT_MIN_SOURCES, 2)
        self.assertEqual(status.DEFAULT_N, 3)
        self.assertLess(1, d.ACT_MIN_SOURCES)
        self.assertLess(d.ACT_MIN_SOURCES, status.DEFAULT_N)

    def test_register_records_decision(self):
        with open(os.path.join(ROOT, "coordination_register.json")) as f:
            reg = json.load(f)
        t1 = dict((x["id"], x) for x in reg["decisions"])["T1"]
        self.assertIn("on purpose", t1["verdict"])
        e = dict((x["id"], x) for x in reg["experiments"])
        self.assertEqual(e["E10"]["status"], "NOT_RUN")
        self.assertIn("E10", [r for r in reg["risks"] if r["id"] == "R8"][0]["experiment"])


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
        self.assertEqual([x["id"] for x in reg["defenses"]], ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11"])
        self.assertIn("B6", [b["id"] for b in reg["backups"]])
        e = dict((x["id"], x) for x in reg["experiments"])
        self.assertIn("historical", e["E7"]["question"].lower())
        self.assertIn("manual capability", e["E9"]["question"])


if __name__ == "__main__":
    unittest.main()
