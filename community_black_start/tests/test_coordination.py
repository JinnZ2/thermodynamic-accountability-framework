# tests/test_coordination.py -- CC0, stdlib unittest
# Provenance: co-authored (Kavik + Claude).

import json
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import chain  # noqa: E402
import community  # noqa: E402
import coordination as co  # noqa: E402

ITEMS = chain.load()
EX = os.path.join(ROOT, "examples")
A = community.load_community(os.path.join(EX, "community_a.json"))
B = community.load_community(os.path.join(EX, "community_b.json"))
PA, PB = co.share_profile(A, ITEMS), co.share_profile(B, ITEMS)


class ShareTests(unittest.TestCase):
    def test_profile_carries_ids_only(self):
        self.assertEqual(set(PA), {"schema_version", "community", "holds"})
        blob = json.dumps(PA)
        for secret in A.holders.values():
            self.assertNotIn(secret, blob)
        self.assertNotIn("buffer", blob)


class ProposalTests(unittest.TestCase):
    def setUp(self):
        self.ps = co.propose(PA, PB, ITEMS, "ai:n1")

    def test_every_proposal_has_plain_line_and_is_pending(self):
        self.assertTrue(self.ps)
        for p in self.ps:
            self.assertTrue(co.plain_ok(p["plain"]))
            self.assertEqual(co.state(p), "PENDING")

    def test_offers_are_questions_not_surplus_claims(self):
        offer = [p for p in self.ps if p["kind"] == "offer"][0]
        self.assertIn("can say whether any can be spared", offer["plain"])

    def test_no_parallel_input_or_l3_offers(self):
        for p in self.ps:
            self.assertNotEqual(p["item_id"], "gov_parallel_restoration")
            if p["kind"] == "offer":
                self.assertNotEqual(ITEMS[p["item_id"]].level, 3)

    def test_proposer_must_be_ai_node(self):
        with self.assertRaises(co.CoordinationError):
            co.propose(PA, PB, ITEMS, "human:coordinator")

    def test_schema_mismatch_refused(self):
        with self.assertRaises(co.CoordinationError):
            co.propose(dict(PA, schema_version="coord-9"), PB, ITEMS, "ai:n1")


class ConsentTests(unittest.TestCase):
    def setUp(self):
        self.p = co.propose(PA, PB, ITEMS, "ai:n1")[0]
        self.a, self.b = self.p["from"], self.p["to"]

    def test_ai_cannot_consent(self):
        with self.assertRaises(co.CoordinationError):
            co.consent(self.p, self.a, "accept", "ai:n1")

    def test_non_party_cannot_consent(self):
        with self.assertRaises(co.CoordinationError):
            co.consent(self.p, "someone_else", "accept", "human:mayor")

    def test_both_accept_required(self):
        q = co.consent(self.p, self.a, "accept", "human:council")
        self.assertEqual(co.state(q), "PENDING")
        q = co.consent(q, self.b, "accept", "human:council")
        self.assertEqual(co.state(q), "ACCEPTED")

    def test_one_refusal_is_final(self):
        q = co.consent(self.p, self.a, "accept", "human:council")
        q = co.consent(q, self.b, "refuse", "human:council")
        self.assertEqual(co.state(q), "REFUSED")

    def test_consent_does_not_mutate_original(self):
        co.consent(self.p, self.a, "refuse", "human:council")
        self.assertEqual(co.state(self.p), "PENDING")


class DriftTests(unittest.TestCase):
    def _accepted(self, node):
        p = co.propose(PA, PB, ITEMS, node)[0]
        p = co.consent(p, p["from"], "accept", "human:x")
        return co.consent(p, p["to"], "accept", "human:x")

    def test_concentration_flagged(self):
        ps = [self._accepted("ai:n1") for _ in range(3)] + [self._accepted("ai:n2")]
        rep = co.node_concentration(ps)
        self.assertEqual(rep["flagged"], ["ai:n1"])
        self.assertAlmostEqual(rep["share"]["ai:n1"], 0.75)

    def test_balanced_not_flagged(self):
        ps = [self._accepted("ai:n1"), self._accepted("ai:n2")]
        self.assertEqual(co.node_concentration(ps)["flagged"], [])

    def test_corroboration(self):
        p = co.propose(PA, PB, ITEMS, "ai:n1")[0]
        self.assertTrue(co.single_node(p))
        self.assertTrue(co.single_node(co.corroborate(p, "ai:n1")))     # self does not count
        self.assertFalse(co.single_node(co.corroborate(p, "ai:n2")))


class FallbackTests(unittest.TestCase):
    def test_plain_fallback_on_schema_mismatch(self):
        p = co.propose(PA, PB, ITEMS, "ai:n1")[0]
        self.assertEqual(co.read_record(p)["mode"], "STRUCTURED")
        r = co.read_record(dict(p, schema_version="coord-2"))
        self.assertEqual(r["mode"], "PLAIN_FALLBACK")
        self.assertTrue(r["needs_human_read"])

    def test_record_without_plain_line_rejected(self):
        with self.assertRaises(co.CoordinationError):
            co.read_record({"schema_version": co.SCHEMA_VERSION, "plain": "x"})

    def test_paper_line(self):
        p = co.propose(PA, PB, ITEMS, "ai:n1")[0]
        line = co.to_paper(p)
        self.assertNotIn("\n", line)
        self.assertIn("PENDING", line)
        self.assertIn("UNDECIDED", line)


class LogTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.path = os.path.join(self.d, "log.jsonl")

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_chain_rejects_edits_and_appends_after_tamper(self):
        p = co.propose(PA, PB, ITEMS, "ai:n1")[0]
        co.append_log(self.path, p)
        co.append_log(self.path, co.consent(p, p["from"], "accept", "human:x"))
        self.assertEqual(co.verify_log(self.path), [])
        lines = open(self.path).read().splitlines()
        rec = json.loads(lines[0])
        rec["body"]["item_id"] = "fuel_stock_FAKE"
        with open(self.path, "w") as f:
            f.write(json.dumps(rec) + "\n" + lines[1] + "\n")
        self.assertTrue(co.verify_log(self.path))
        with self.assertRaises(co.CoordinationError):
            co.append_log(self.path, p)

    def test_log_requires_plain_line(self):
        with self.assertRaises(co.CoordinationError):
            co.append_log(self.path, {"kind": "offer"})


class RegisterTests(unittest.TestCase):
    def test_every_risk_mapped_and_every_experiment_has_a_null(self):
        with open(os.path.join(ROOT, "coordination_register.json")) as f:
            reg = json.load(f)
        self.assertEqual([r["id"] for r in reg["risks"]], ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"])
        b_ids = {b["id"] for b in reg["backups"]}
        e_ids = {e["id"] for e in reg["experiments"]}
        for r in reg["risks"]:
            self.assertTrue(set(r["backup"]) <= b_ids, r["id"])
            self.assertTrue(set(r["experiment"]) <= e_ids, r["id"])
            self.assertTrue(r["status"])
        for e in reg["experiments"]:
            self.assertTrue(e["cleanest_test"] and e["null"])
            self.assertEqual(e["status"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
