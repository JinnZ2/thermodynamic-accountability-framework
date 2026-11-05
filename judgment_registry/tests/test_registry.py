# tests/test_registry.py -- CC0, stdlib unittest
# Provenance: co-authored (Kavik + Claude), 2026-11-04.
# SYNTHETIC fixtures only. "Judge Q", "Council R", act type "act-7" etc. are
# placeholders; no real-world judgment is seeded here.

import json
import os
import re
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import chain  # noqa: E402
import cli  # noqa: E402
import integrity  # noqa: E402
import ledger  # noqa: E402

EVALUATIVE = ("wrong", "bad", "invalid", "unethical", "fad", "false", "correct", "incorrect",
              "good", "evil", "immoral", "illegitimate", "outdated", "biased", "flawed",
              "error", "right", "better", "worse", "superior", "inferior", "backward")


def J(jid, **kw):
    base = {"judgment_id": jid, "version": "1", "claim": "Synthetic claim text for act-7.",
            "scope": {"who": "group-A", "act_type": "act-7", "conditions": "cond-1"},
            "environment": {"scarcity": "low", "threat": "low", "tech_level": "t1"},
            "date": "1900-01-01", "judge": {"name_or_body": "Judge Q", "type": "person"},
            "judge_incentives": "none documented in source S", "reason": "Stated reason text.",
            "evidence": [{"item": "e1", "tag": "OBSERVED", "source": "S"}],
            "dissent": [], "framing_check": {"done": True, "variants_tried": ["v1"], "result_text": "same"},
            "recorder": "rec-01", "source": "synthetic source S", "volume": "thin"}
    base.update(kw)
    return base


def build(*steps):
    recs = []
    for kind, body in steps:
        recs = ledger.append_records(recs, kind, body)
    return recs


def codes(recs, about=None):
    return [f["flag"] for f in integrity.check(recs) if about is None or f["about"] == about]


class CleanTests(unittest.TestCase):
    def test_complete_record_no_flags(self):
        self.assertEqual(codes(build(("judgment", J("j1")))), [])

    def test_clean_supersession_no_flags(self):
        recs = build(("judgment", J("j1")),
                     ("judgment", J("j2", version="2", supersedes="j1", change_basis=["CONDITIONS"],
                                    change_detail="scarcity rose",
                                    environment={"scarcity": "high", "threat": "low", "tech_level": "t1"})))
        self.assertEqual(codes(recs), [])


class FlagTests(unittest.TestCase):
    def test_silent_replacement(self):
        recs = build(("judgment", J("j1")), ("judgment", J("j2", claim="Different synthetic claim.")))
        self.assertEqual(codes(recs, "j2"), ["UNCHAINED_CHANGE"])

    def test_different_judges_coexist(self):
        recs = build(("judgment", J("j1")),
                     ("judgment", J("j2", judge={"name_or_body": "Council R", "type": "body"})))
        self.assertEqual(codes(recs), [])

    def test_identical_environment_and_evidence(self):
        recs = build(("judgment", J("j1")),
                     ("judgment", J("j2", version="2", supersedes="j1", change_basis=["EVIDENCE"])))
        self.assertEqual(codes(recs, "j2"), ["NO_NEW_CONDITIONS_OR_EVIDENCE"])

    def test_change_basis_unstated(self):
        for basis in ([], ["NONE_STATED"]):
            recs = build(("judgment", J("j1")),
                         ("judgment", J("j2", supersedes="j1", change_basis=basis,
                                        environment={"scarcity": "high"})))
            self.assertEqual(codes(recs, "j2"), ["CHANGE_BASIS_UNSTATED"], basis)

    def test_dissent_dropped_and_withdrawn(self):
        d = {"position": "p1", "holder": "member-3", "reason": "r", "source": "S"}
        steps = [("judgment", J("j1", dissent=[d])),
                 ("judgment", J("j2", supersedes="j1", change_basis=["CONDITIONS"],
                                environment={"scarcity": "high"}))]
        self.assertEqual(codes(build(*steps), "j2"), ["DISSENT_DROPPED"])
        steps.append(("withdrawal", {"judgment_id": "j1", "position": "p1", "holder": "member-3",
                                     "recorder": "rec-01", "source": "S"}))
        self.assertEqual(codes(build(*steps), "j2"), [])

    def test_scope_transfer(self):
        app = {"application_id": "a1", "judgment_id": "j1",
               "scope": {"who": "group-B", "act_type": "act-7"}, "date": "1950-01-01",
               "recorder": "rec-01", "source": "S"}
        steps = [("judgment", J("j1")), ("application", app)]
        f = [x for x in integrity.check(build(*steps)) if x["flag"] == "SCOPE_TRANSFER"]
        self.assertEqual(len(f), 1)
        self.assertIn("scope.who", f[0]["detail"])
        steps.append(("transfer", {"application_id": "a1", "reason": "Stated reason for carrying it over."}))
        self.assertEqual(codes(build(*steps)), [])

    def test_in_scope_application_no_flag(self):
        app = {"application_id": "a2", "judgment_id": "j1", "scope": {"who": "Group-A ", "act_type": "act-7"}}
        self.assertEqual(codes(build(("judgment", J("j1")), ("application", app))), [])

    def test_date_outside_recorded_range(self):
        j = J("j1", scope={"who": "group-A", "act_type": "act-7", "dates": {"from": "1900", "to": "1910"}})
        app = {"application_id": "a3", "judgment_id": "j1", "date": "1920-05-01"}
        f = [x for x in integrity.check(build(("judgment", j), ("application", app)))
             if x["flag"] == "SCOPE_TRANSFER"]
        self.assertIn("dates", f[0]["detail"])

    def test_missing_fields_source_incentives_framing(self):
        recs = build(("judgment", J("j1", reason="", judge={"name_or_body": "Judge Q"}, source=None,
                                     judge_incentives=None, framing_check=None)))
        got = integrity.check(recs)
        cs = [f["flag"] for f in got]
        self.assertEqual(sorted(cs), ["INCENTIVES_UNRECORDED", "MISSING_FIELD", "NO_FRAMING_CHECK", "NO_SOURCE"])
        miss = [f for f in got if f["flag"] == "MISSING_FIELD"][0]["detail"]
        self.assertIn("reason", miss)
        self.assertIn("judge.type", miss)

    def test_dangling_and_fork(self):
        recs = build(("judgment", J("j1")),
                     ("judgment", J("j2", supersedes="j1", change_basis=["EVIDENCE"], environment={"x": 1})),
                     ("judgment", J("j3", supersedes="j1", change_basis=["EVIDENCE"], environment={"x": 2})),
                     ("judgment", J("j4", supersedes="j9", change_basis=["EVIDENCE"],
                                    scope={"who": "group-Z", "act_type": "act-9"})))
        self.assertEqual(codes(recs, "j1"), ["SUPERSESSION_FORK"])
        self.assertEqual(codes(recs, "j4"), ["SUPERSEDES_NOT_FOUND"])


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.path = os.path.join(self.d, "j.jsonl")

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_tamper_detected_and_append_refused(self):
        ledger.append(self.path, "judgment", J("j1"))
        ledger.append(self.path, "judgment", J("j2", supersedes="j1", change_basis=["EVIDENCE"],
                                               environment={"x": 1}))
        self.assertEqual(ledger.verify(ledger.read(self.path)), [])
        with open(self.path) as f:
            lines = f.read().splitlines()
        rec = json.loads(lines[0])
        rec["body"]["claim"] = "edited later"
        with open(self.path, "w") as f:
            f.write(json.dumps(rec) + "\n" + lines[1] + "\n")
        self.assertTrue(ledger.verify(ledger.read(self.path)))
        with self.assertRaises(ledger.LedgerError):
            ledger.append(self.path, "judgment", J("j3", scope={"who": "g", "act_type": "a"}))

    def test_deletion_detected(self):
        recs = build(("judgment", J("j1")), ("judgment", J("j2", judge={"name_or_body": "R", "type": "body"})),
                     ("judgment", J("j3", judge={"name_or_body": "S", "type": "body"})))
        self.assertTrue(ledger.verify([recs[0], recs[2]]))

    def test_merge_idempotent(self):
        a = build(("judgment", J("j1")))
        b = build(("judgment", J("j1")), ("judgment", J("j2", judge={"name_or_body": "R", "type": "body"})))
        m = ledger.merge(a, b)
        self.assertEqual(len(m), 2)
        self.assertEqual(ledger.merge(m, m), m)
        self.assertEqual(ledger.merge(m, b), m)
        self.assertEqual(ledger.verify(m), [])

    def test_merge_refuses_existing_file(self):
        open(self.path, "w").close()
        with self.assertRaises(ledger.LedgerError):
            ledger.write_new(self.path, [])

    def test_shape_rejections(self):
        for bad in (J("j1", superseded_by=["j2"]), J("j1", volume="huge"),
                    J("j1", evidence=[{"item": "e", "tag": "GUESS"}]), J("j1", judge={"type": "deity-x"}),
                    J("j1", change_basis=["VIBES"]), dict(J("j1"), extra_field=1), J("j1", supersedes="j1")):
            with self.assertRaises(ledger.LedgerError):
                ledger.append_records([], "judgment", bad)

    def test_duplicate_id_refused(self):
        recs = build(("judgment", J("j1")))
        with self.assertRaises(ledger.LedgerError):
            ledger.append_records(recs, "judgment", J("j1", version="2"))

    def test_old_version_untouched_by_supersession(self):
        recs = build(("judgment", J("j1")))
        before = json.dumps(recs[0], sort_keys=True)
        recs = ledger.append_records(recs, "judgment", J("j2", supersedes="j1", change_basis=["EVIDENCE"],
                                                         environment={"x": 1}))
        self.assertEqual(json.dumps(recs[0], sort_keys=True), before)
        self.assertNotIn("superseded_by", recs[0]["body"])
        self.assertEqual(ledger.judgments(recs)[0].superseded_by, ["j2"])


class ChainTests(unittest.TestCase):
    def setUp(self):
        d = {"position": "p1", "holder": "m3", "reason": "r", "source": "S"}
        self.recs = build(("judgment", J("j1", dissent=[d])),
                          ("judgment", J("j2", version="2", supersedes="j1", change_basis=["CONDITIONS"],
                                         environment={"scarcity": "high"}, dissent=[d])),
                          ("judgment", J("j3", version="3", supersedes="j2", change_basis=["EVIDENCE"],
                                         environment={"scarcity": "high"},
                                         evidence=[{"item": "e2", "tag": "DERIVED", "source": "S2"}])))

    def test_lineage_from_any_member(self):
        for start in ("j1", "j2", "j3"):
            steps = chain.lineage(self.recs, start)
            self.assertEqual([s["judgment_id"] for s in steps], ["j1", "j2", "j3"])
        self.assertEqual([s["dissent_count"] for s in steps], [1, 1, 0])
        self.assertIn("j3 v3", chain.format_lineage(steps))

    def test_diff(self):
        d = chain.diff(self.recs, "j2", "j3")
        self.assertEqual(set(d), {"version", "supersedes", "change_basis", "evidence", "dissent"})


class CliTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        self.led = os.path.join(self.d, "j.jsonl")

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_add_check_export(self):
        f = os.path.join(self.d, "r.json")
        with open(f, "w") as fh:
            json.dump(J("j1"), fh)
        self.assertEqual(cli.main(["add", f, "--ledger", self.led]), 0)
        self.assertEqual(cli.main(["check", "--ledger", self.led]), 0)
        self.assertEqual(cli.main(["lineage", "j1", "--ledger", self.led]), 0)
        self.assertEqual(cli.main(["export", "--ledger", self.led]), 0)
        self.assertEqual(cli.main([]), 2)


class NeutralityTests(unittest.TestCase):
    """Fails if any flag name, template or emitted detail uses an evaluative word."""

    def _scan(self, text):
        words = set(re.findall(r"[a-z]+", text.lower().replace("_", " ")))
        return sorted(words & set(EVALUATIVE))

    def test_flag_names_and_templates(self):
        for name, tmpl in integrity.FLAGS.items():
            self.assertEqual(self._scan(name + " " + tmpl), [], name)

    def test_emitted_details(self):
        d = {"position": "p1", "holder": "m3", "reason": "r", "source": "S"}
        recs = build(("judgment", J("j1", dissent=[d], judge_incentives=None, framing_check=None, source="")),
                     ("judgment", J("j2", supersedes="j1")),
                     ("judgment", J("j3", claim="Other synthetic claim.")),
                     ("application", {"application_id": "a1", "judgment_id": "j1", "scope": {"who": "group-B"}}))
        flags = integrity.check(recs)
        self.assertGreaterEqual(len(set(f["flag"] for f in flags)), 7)
        for f in flags:
            self.assertEqual(self._scan(f["flag"] + " " + f["detail"]), [], f)


if __name__ == "__main__":
    unittest.main()
