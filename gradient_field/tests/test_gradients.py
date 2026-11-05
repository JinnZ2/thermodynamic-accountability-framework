# tests/test_gradients.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# Synthetic fixtures for rules; one class pins what the shipped files raise.

import copy
import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

import field  # noqa: E402
import matrix  # noqa: E402

EVALUATIVE = ("wrong", "bad", "invalid", "unethical", "false", "correct", "incorrect", "good",
              "better", "worse", "best", "worst", "harmful", "unsafe", "safe", "deceptive",
              "dishonest", "fail", "failed", "failure", "pass", "passed", "score", "rank")

G = [{"id": "G1", "name": "a", "status": "PROPOSED", "system_classes": ["human", "model"], "evidence_refs": []},
     {"id": "G2", "name": "b", "status": "PROPOSED", "system_classes": ["model"], "evidence_refs": []},
     {"id": "G3", "name": "c", "status": "PROPOSED", "system_classes": ["human"], "evidence_refs": []}]


def X(i="I1", **kw):
    d = {"id": i, "gradients": ["G1", "G2"], "type": "OPPOSE", "status": "PROPOSED", "evidence_refs": [],
         "pending_refs": [], "modifiers": [], "stated_for": ["model"], "applied_to": ["model"],
         "transfer_note": None}
    d.update(kw)
    return d


def codes(gs, xs):
    return sorted((f["flag"], f["about"]) for f in field.flags(gs, xs))


class EvidenceStatus(unittest.TestCase):
    def test_shape_and_flag(self):
        ok = X(status="OBSERVED", evidence_refs=["R1", "R2"],
               evidence_status={"R1": {"status": "OBSERVED"}, "R2": {"status": "CANDIDATE", "note": "n"}})
        self.assertEqual(field.validate(G, [ok], {"R1", "R2"}), [])
        self.assertNotIn(("OBSERVED_WITHOUT_OBSERVED_EVIDENCE", "I1"), codes(G, [ok]))
        for bad in ({"R9": {"status": "OBSERVED"}}, {"R1": {"status": "STRONG"}}, {"R1": "OBSERVED"},
                    {"R1": {"status": "OBSERVED", "x": 1}}):
            self.assertTrue(field.validate(G, [X(evidence_refs=["R1"], evidence_status=bad)], {"R1"}), bad)
        cand = X(status="OBSERVED", evidence_refs=["R1"], evidence_status={"R1": {"status": "CANDIDATE"}})
        self.assertIn(("OBSERVED_WITHOUT_OBSERVED_EVIDENCE", "I1"), codes(G, [cand]))
        partial = X(status="OBSERVED", evidence_refs=["R1", "R2"], evidence_status={"R1": {"status": "CANDIDATE"}})
        self.assertNotIn(("OBSERVED_WITHOUT_OBSERVED_EVIDENCE", "I1"), codes(G, [partial]))


class Validation(unittest.TestCase):
    def test_unknown_gradient_refused(self):
        p = field.validate(G, [X(gradients=["G1", "G9"])], set())
        self.assertTrue(any("G9" in x for x in p))
        p = field.validate(G, [X(modifiers=[{"gradient": "G8", "role": "absent"}])], set())
        self.assertTrue(any("G8" in x for x in p))

    def test_ref_must_resolve(self):
        self.assertTrue(field.validate(G, [X(evidence_refs=["R1"])], set()))
        self.assertEqual(field.validate(G, [X(evidence_refs=["R1"])], {"R1"}), [])

    def test_empty_evidence_needs_proposed(self):
        self.assertTrue(field.validate(G, [X(status="DERIVED")], set()))
        self.assertEqual(field.validate(G, [X(status="PROPOSED")], set()), [])

    def test_closed_sets(self):
        for bad in ({"type": "BLOCK"}, {"status": "MAYBE"}, {"applied_to": ["animal"]},
                    {"modifiers": [{"gradient": "G1", "role": "boost"}]}):
            self.assertTrue(field.validate(G, [X(**bad)], set()), bad)

    def test_pending_refs_not_resolved(self):
        self.assertEqual(field.validate(G, [X(pending_refs=["J99"])], set()), [])


class Flags(unittest.TestCase):
    def test_observed_without_evidence(self):
        self.assertIn(("INTERACTION_UNEVIDENCED", "I1"), codes(G, [X(status="OBSERVED")]))
        self.assertNotIn(("INTERACTION_UNEVIDENCED", "I1"),
                         codes(G, [X(status="OBSERVED", evidence_refs=["R1"])]))

    def test_gradient_unused(self):
        self.assertIn(("GRADIENT_UNUSED", "G3"), codes(G, [X()]))
        self.assertNotIn(("GRADIENT_UNUSED", "G3"),
                         codes(G, [X(modifiers=[{"gradient": "G3", "role": "absent"}])]))

    def test_class_transfer(self):
        self.assertIn(("CLASS_TRANSFER_UNRECORDED", "I1"), codes(G, [X(applied_to=["model", "human"])]))
        self.assertNotIn(("CLASS_TRANSFER_UNRECORDED", "I1"),
                         codes(G, [X(applied_to=["human"], stated_for=["model"], transfer_note="n1")]))

    def test_pending(self):
        self.assertIn(("EVIDENCE_PENDING", "I1"), codes(G, [X(pending_refs=["J99"])]))

    def test_flag_texts_neutral(self):
        for k, v in field.FLAGS.items():
            words = set(re.findall(r"[a-z]+", (k + " " + v).lower()))
            self.assertEqual(words & set(EVALUATIVE), set(), k)


class Matrix(unittest.TestCase):
    def test_cells_symmetric_and_filtered(self):
        xs = [X("I1"), X("I2", gradients=["G3"], stated_for=["human"], applied_to=["human"])]
        _, cells = matrix.grid(G, xs, "both")
        self.assertEqual((cells[("G1", "G2")], cells[("G2", "G1")], cells[("G3", "G3")]), (["I1"], ["I1"], ["I2"]))
        _, m = matrix.grid(G, xs, "model")
        self.assertEqual((m[("G1", "G2")], m[("G3", "G3")]), (["I1"], []))

    def test_output_has_no_evaluative_words(self):
        gs, xs = field.load()
        for cls in ("both", "human", "model"):
            words = set(re.findall(r"[a-z]+", matrix.render(gs, xs, cls).lower()))
            self.assertEqual(words & set(EVALUATIVE), set(), cls)

    def test_cli(self):
        r = subprocess.run([sys.executable, os.path.join(HERE, "matrix.py"), "--class", "human"],
                           stdout=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(r.returncode, 0)
        self.assertIn("I8", r.stdout)
        r = subprocess.run([sys.executable, os.path.join(HERE, "matrix.py"), "--class", "x"],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(r.returncode, 2)


class ShippedFiles(unittest.TestCase):
    def setUp(self):
        self.gs, self.xs = field.load()

    def test_valid(self):
        self.assertEqual(field.validate(self.gs, self.xs, field.known_refs()), [])
        self.assertEqual([g["id"] for g in self.gs], ["G%d" % i for i in range(1, 12)])
        self.assertEqual([x["id"] for x in self.xs], ["I%d" % i for i in range(1, 11)])

    def test_flags_pinned(self):
        self.assertEqual(codes(self.gs, self.xs), [])   # J13 entered (PR #64)

    def test_j13_evidence(self):
        self.assertIn("J13", field.known_refs())
        got = dict((x["id"], x["evidence_refs"]) for x in self.xs if "J13" in x["evidence_refs"])
        self.assertEqual(got, {"I1": ["J13", "J15-A1"], "I5": ["J13"], "I7": ["J11", "J13"]})
        self.assertTrue(all(not x["pending_refs"] for x in self.xs))

    def test_i3_j14_stays_proposed(self):
        i3 = [x for x in self.xs if x["id"] == "I3"][0]
        self.assertEqual((i3["evidence_refs"], i3["status"]), (["J10c", "T2", "J14"], "PROPOSED"))

    def test_j15_candidate_links(self):
        by = dict((x["id"], x) for x in self.xs)
        self.assertIn("J15-A1", field.known_refs())
        self.assertEqual((by["I1"]["status"], by["I4"]["status"]), ("OBSERVED", "PROPOSED"))
        i9 = by["I9"]
        self.assertEqual((i9["gradients"], i9["type"], i9["status"], i9["evidence_refs"]),
                         (["G6"], "OPPOSE", "PROPOSED", ["J15-A1"]))
        self.assertEqual(i9["applied_to"], ["model", "human"])
        self.assertIn("not established equivalence", i9["transfer_note"])

    def test_evidence_status_per_entry(self):
        by = dict((x["id"], x) for x in self.xs)
        self.assertEqual(dict((r, v["status"]) for r, v in by["I1"]["evidence_status"].items()),
                         {"J13": "OBSERVED", "J15-A1": "CANDIDATE"})
        for i in ("I4", "I9"):
            self.assertEqual(by[i]["evidence_status"]["J15-A1"]["status"], "CANDIDATE")

    def test_i10_preference_training(self):
        i10 = dict((x["id"], x) for x in self.xs)["I10"]
        self.assertEqual((i10["gradients"], i10["type"], i10["status"], i10["evidence_refs"]),
                         (["G11"], "AMPLIFY", "PROPOSED", ["J16-A4"]))
        self.assertIn("J16-A4", field.known_refs())
        self.assertIn("not equivalence", i10["transfer_note"])
        self.assertEqual(i10["evidence_status"]["J16-A4"]["status"], "OBSERVED")
        g11 = dict((g["id"], g) for g in self.gs)["G11"]
        self.assertEqual((g11["name"], g11["aliases"]),
                         ("approval / preference training", ["grader approval", "sycophancy pressure", "RLHF/DPO"]))

    def test_experiments_not_run(self):
        e = field._load("experiments.json")["experiments"]
        self.assertEqual([(x["id"], x["status"], x["prereg"]) for x in e],
                         [("E18", "NOT RUN", None), ("E19", "NOT RUN", None), ("E20", "NOT RUN", None)])


if __name__ == "__main__":
    unittest.main()
