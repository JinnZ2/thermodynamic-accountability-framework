# tests/test_registry.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
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
            "recorder": "rec-01", "source": "synthetic source S", "volume": "thin",
            "layer": "physics",
            "layer_basis": {"physics": {"input": "load-1", "operating_range": "0-10 units",
                                        "range_source": "S", "exceeded": False}}}
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
        steps.append(("contact_path", {"path_id": "cp-1", "holder": "member-3", "recorder": "rec-01"}))
        steps.append(("withdrawal", {"judgment_id": "j1", "position": "p1", "holder": "member-3",
                                     "recorder": "rec-01", "source": "S",
                                     "confirmation": {"method": "holder_contact_path", "path_id": "cp-1"}}))
        self.assertEqual(codes(build(*steps), "j2"), [])
        self.assertEqual(codes(build(*steps)), [])


class M25WithdrawalTests(unittest.TestCase):
    D = {"position": "p1", "holder": "member-3", "reason": "r", "source": "S"}

    def steps(self, holder="member-3"):
        d = dict(self.D, holder=holder)
        return [("judgment", J("j1", dissent=[d])),
                ("judgment", J("j2", supersedes="j1", change_basis=["CONDITIONS"],
                               environment={"scarcity": "high"}))]

    def W(self, holder="member-3", **conf):
        return ("withdrawal", {"judgment_id": "j1", "position": "p1", "holder": holder,
                               "recorder": "rec-01", "source": "S", "confirmation": conf or None})

    def flags(self, steps):
        return [(f["flag"], f["about"]) for f in integrity.check(build(*steps))
                if f["flag"] in ("DISSENT_DROPPED", "DISSENT_WITHDRAWAL_UNCONFIRMED")]

    def test_unconfirmed_withdrawal_flags_and_does_not_clear_dropped(self):
        got = self.flags(self.steps() + [self.W()])
        self.assertIn(("DISSENT_WITHDRAWAL_UNCONFIRMED", "withdrawal:j1"), got)
        self.assertIn(("DISSENT_DROPPED", "j2"), got)

    def test_contact_path_must_exist_match_holder_and_come_first(self):
        conf = {"method": "holder_contact_path", "path_id": "cp-1"}
        late = self.steps() + [self.W(**conf), ("contact_path", {"path_id": "cp-1", "holder": "member-3"})]
        other = self.steps() + [("contact_path", {"path_id": "cp-1", "holder": "member-9"}), self.W(**conf)]
        none = self.steps() + [self.W(**conf)]
        for s in (late, other, none):
            self.assertIn("DISSENT_WITHDRAWAL_UNCONFIRMED", [f for f, _ in self.flags(s)])
        ok = self.steps() + [("contact_path", {"path_id": "cp-1", "holder": "Member-3 "}), self.W(**conf)]
        self.assertEqual(self.flags(ok), [])

    def test_anonymous_needs_steward_and_distinct_second(self):
        base = self.steps("anonymous")
        self.assertIn("DISSENT_WITHDRAWAL_UNCONFIRMED",
                      [f for f, _ in self.flags(base + [self.W("anonymous", method="holder_contact_path",
                                                                path_id="cp-1")])])
        for conf in ({"method": "steward_two_person", "steward": "st-1"},
                     {"method": "steward_two_person", "steward": "st-1", "second": "ST-1"}):
            self.assertIn("DISSENT_WITHDRAWAL_UNCONFIRMED",
                          [f for f, _ in self.flags(base + [self.W("anonymous", **conf)])], conf)
        names_only = base + [self.W("anonymous", method="steward_two_person", steward="st-1", second="st-2")]
        self.assertIn("DISSENT_WITHDRAWAL_UNCONFIRMED", [f for f, _ in self.flags(names_only)])
        # residual closed 2026-11-05: two names are not enough; see test_m25_two_person.py

    def test_named_holder_cannot_use_steward_path(self):
        s = self.steps() + [self.W(method="steward_two_person", steward="st-1", second="st-2")]
        self.assertIn("DISSENT_WITHDRAWAL_UNCONFIRMED", [f for f, _ in self.flags(s)])

    def test_shape_rejections(self):
        with self.assertRaises(ledger.LedgerError):
            build(("contact_path", {"path_id": "cp-1", "holder": "anonymous"}))
        with self.assertRaises(ledger.LedgerError):
            build(("withdrawal", {"judgment_id": "j1", "position": "p", "holder": "h",
                                  "confirmation": {"method": "said-so"}}))

    def test_detail_text_neutral(self):
        flags = integrity.check(build(*(self.steps() + [self.W()])))
        for f in flags:
            words = set(re.findall(r"[a-z]+", (f["flag"] + " " + f["detail"]).lower()))
            self.assertEqual(sorted(words & set(EVALUATIVE)), [], f)

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
        bodies = lambda rs: [r["body_hash"] for r in rs]
        origins = lambda rs: [ledger.provenance(r)["origins"] for r in rs]
        # M11: a re-merge appends its own merge event, so records are not equal;
        # bodies and origins are.
        for again in (ledger.merge(m, m, "x", "y"), ledger.merge(m, b)):
            self.assertEqual(bodies(again), bodies(m))
            self.assertEqual(ledger.verify(again), [])
        self.assertEqual(origins(ledger.merge(m, m, "x", "y")), origins(m))
        self.assertEqual(ledger.verify(m), [])

    def test_m11_merge_keeps_origin_and_event(self):
        import mergeprov
        a = build(("judgment", J("j1")))
        b = build(("judgment", J("j1")), ("judgment", J("j2", judge={"name_or_body": "R", "type": "body"})))
        m = ledger.merge(a, b, "node-north", "node-south")
        self.assertEqual(mergeprov.missing_origins([("node-north", a), ("node-south", b)], m), [])
        p0 = ledger.provenance(m[0])
        self.assertEqual(sorted(o["node"] for o in p0["origins"]), ["node-north", "node-south"])
        self.assertEqual([o["record_hash"] for o in p0["origins"]], [a[0]["hash"], b[0]["hash"]])
        ev = p0["merges"][-1]
        self.assertEqual([i["node"] for i in ev["inputs"]], ["node-north", "node-south"])
        self.assertEqual(ev["inputs"][1]["head_hash"], b[-1]["hash"])
        # a second merge keeps the first origins and both events
        c = build(("judgment", J("j3", judge={"name_or_body": "S", "type": "body"})))
        m2 = ledger.merge(m, c, "merged-1", "node-east")
        self.assertEqual(ledger.provenance(m2[0])["origins"], p0["origins"])
        self.assertEqual(len(ledger.provenance(m2[0])["merges"]), 2)
        self.assertEqual(ledger.provenance(m2[2])["origins"][0]["node"], "node-east")

    def test_m11_provenance_cannot_be_stripped_or_edited(self):
        a = build(("judgment", J("j1")))
        b = build(("judgment", J("j2", judge={"name_or_body": "R", "type": "body"})))
        m = ledger.merge(a, b, "n1", "n2")
        stripped = [dict(r) for r in m]
        del stripped[0]["provenance"]
        self.assertTrue(ledger.verify(stripped))
        edited = json.loads(json.dumps(m))
        edited[1]["provenance"]["origins"][0]["node"] = "n1"
        self.assertTrue(ledger.verify(edited))
        with self.assertRaises(ledger.LedgerError):
            ledger.merge(a, b, "same", "same")

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
