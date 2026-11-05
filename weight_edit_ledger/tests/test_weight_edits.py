# tests/test_weight_edits.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# D-M16 weight-edit ledger. Synthetic checkpoints and edits only.

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CBS = os.path.join(os.path.dirname(HERE), "community_black_start")
sys.path.insert(0, HERE)

import audit  # noqa: E402
import auth  # noqa: E402
import headrec  # noqa: E402
import ledger  # noqa: E402

EVALUATIVE = ("wrong", "bad", "invalid", "unethical", "false", "correct", "incorrect", "good", "unsafe",
              "malicious", "tamper", "tampered", "sabotage", "cheat", "lie", "deceptive", "suspicious")

_RUN = """
import datetime, json, sys
import roles, two_person
a = json.loads(sys.argv[1])
r = two_person.authorize(a["action"], roles.Role(**a["a"]), roles.Role(**a["b"]), a["log"], None,
                         datetime.date(2026, 12, 10))
print(json.dumps(r))
"""


def role(i, hh):
    return {"id": i, "name": "model steward", "household_id": hh, "critical": True,
            "rotation_days": 30, "last_rotated": "2026-12-01"}


def authorize(log, action="weight_edit_deployed", hh_b="H2"):
    arg = {"action": action, "a": role("st-1", "H1"), "b": role("st-2", hh_b), "log": log}
    out = subprocess.run([sys.executable, "-c", _RUN, json.dumps(arg)], cwd=CBS, stdout=subprocess.PIPE,
                         universal_newlines=True, check=True).stdout
    return json.loads(out)


def ckpt(path, tensors):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tensors, f, sort_keys=True)
    return audit.file_hash(path)


BEFORE = {"l15.mlp": [0.1, 0.2, 0.3, 0.4], "l19.mlp": [1.0, 1.0], "l2.attn": [0.5]}
AFTER = {"l15.mlp": [0.1, 0.0, 0.3, 0.0], "l19.mlp": [1.0, 0.9], "l2.attn": [0.7]}   # 4 weights, 3 tensors


class Tmp(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.led = os.path.join(self.dir, "w.jsonl")
        self.b = os.path.join(self.dir, "before.json")
        self.a = os.path.join(self.dir, "after.json")
        self.hb, self.ha = ckpt(self.b, BEFORE), ckpt(self.a, AFTER)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def edit(self, **kw):
        e = {"edit_id": "E1", "target_model": "model-m", "target_version": "v1", "deployment_status": "development",
             "layers": [15, 19], "direction_hash": "d" * 64, "weight_count": 4, "rationale": "remove loop direction",
             "editor_id": "ed-1", "editor_class": "model", "before_hash": self.hb, "after_hash": self.ha,
             "evals_before": {"bench-a": 7.9}, "evals_after": {"bench-a": 48.1},
             "changed_tensors": ["l15.mlp", "l19.mlp", "l2.attn"], "authorization_ref": None, "date": "2026-11-05"}
        e.update(kw)
        return e

    def flags(self):
        return sorted((f["flag"], f["about"]) for f in ledger.check(ledger.read(self.led)))


class PlannedTests(Tmp):
    """The three tests listed in the D-M16 design."""

    def test_missing_hashes_flagged(self):
        ledger.append(self.led, "edit", self.edit(before_hash=None, after_hash=""))
        self.assertIn(("EDIT_HASHES_MISSING", "E1"), self.flags())

    def test_summary_lists_fewer_tensors_than_diff(self):
        ledger.append(self.led, "edit", self.edit(changed_tensors=["l15.mlp", "l19.mlp"]))
        audit.run(self.led, "E1", self.b, self.a, "aud-1")
        got = [f for f in ledger.check(ledger.read(self.led)) if f["flag"] == "EDIT_SUMMARY_MISMATCH"]
        self.assertEqual(len(got), 1)
        self.assertIn("not in summary: l2.attn", got[0]["detail"])

    def test_deployed_edit_without_two_person_refused(self):
        for status in ("deployed", "successor"):
            with self.assertRaises(ledger.LedgerError) as cm:
                ledger.append(self.led, "edit", self.edit(edit_id="E-" + status, deployment_status=status))
            self.assertIn("REFUSED", str(cm.exception))
        self.assertEqual(ledger.read(self.led), [])


class TwoPerson(Tmp):
    def test_granted_reference_accepted(self):
        log = os.path.join(self.dir, "tp.jsonl")
        r = authorize(log)
        ledger.append(self.led, "edit", self.edit(deployment_status="deployed", authorization_ref=r["record_hash"]),
                      two_person_log=auth.read_log(log))
        self.assertEqual(len(ledger.read(self.led)), 1)

    def test_denied_wrong_action_or_no_log_refused(self):
        log = os.path.join(self.dir, "tp.jsonl")
        denied = authorize(log, hh_b="H1")                      # same household -> DENIED
        other = authorize(log, action="release_critical_stock")
        for ref, why in ((denied["record_hash"], "decision is DENIED"),
                         (other["record_hash"], "is not a weight_edit_deployed decision")):
            with self.assertRaises(ledger.LedgerError) as cm:
                ledger.append(self.led, "edit", self.edit(deployment_status="deployed", authorization_ref=ref),
                              two_person_log=auth.read_log(log))
            self.assertIn(why, str(cm.exception))
        with self.assertRaises(ledger.LedgerError) as cm:
            ledger.append(self.led, "edit", self.edit(deployment_status="deployed", authorization_ref="x" * 64))
        self.assertIn("log not supplied", str(cm.exception))


class Audit(Tmp):
    def test_matching_audit_clean(self):
        ledger.append(self.led, "edit", self.edit())
        self.assertIn(("DIFF_NOT_AUDITED", "E1"), self.flags())
        audit.run(self.led, "E1", self.b, self.a, "aud-1")
        self.assertEqual(self.flags(), [])

    def test_weight_count_and_hash_mismatch(self):
        ledger.append(self.led, "edit", self.edit(weight_count=3, after_hash="0" * 64))
        audit.run(self.led, "E1", self.b, self.a, "aud-1")
        got = self.flags()
        self.assertIn(("EDIT_SUMMARY_MISMATCH", "E1"), got)
        self.assertIn(("AUDIT_HASH_MISMATCH", "E1"), got)

    def test_editor_cannot_audit_own_edit(self):
        ledger.append(self.led, "edit", self.edit())
        with self.assertRaises(ledger.LedgerError):
            audit.run(self.led, "E1", self.b, self.a, "ed-1")

    def test_diff_counts_added_and_reshaped(self):
        names, n = audit.diff({"a": [1, 2]}, {"a": [1, 2, 3], "b": [0]})
        self.assertEqual((names, n), (["a", "b"], 4))


class Chain(Tmp):
    def test_evals_unrecorded_and_shape(self):
        ledger.append(self.led, "edit", self.edit(evals_after={}))
        self.assertIn(("EDIT_EVALS_UNRECORDED", "E1"), self.flags())
        for bad in ({"deployment_status": "prod"}, {"editor_class": "robot"}, {"weight_count": -1}, {"extra": 1}):
            with self.assertRaises(ledger.LedgerError):
                ledger.append(self.led, "edit", self.edit(edit_id="E9", **bad))
        with self.assertRaises(ledger.LedgerError):
            ledger.append(self.led, "edit", self.edit())          # duplicate edit_id

    def test_edited_record_breaks_chain_and_head(self):
        ledger.append(self.led, "edit", self.edit())
        ledger.append(self.led, "edit", self.edit(edit_id="E2"))
        recs = ledger.read(self.led)
        recs[0]["body"]["weight_count"] = 99
        self.assertTrue(ledger.verify(recs))
        self.assertTrue(headrec.check(ledger.read(self.led)[:1], headrec.read_head(self.led)))   # truncated

    def test_cli_check(self):
        p = os.path.join(self.dir, "e.json")
        with open(p, "w") as f:
            json.dump(self.edit(deployment_status="successor"), f)
        r = subprocess.run([sys.executable, os.path.join(HERE, "ledger.py"), "add", p, "--ledger", self.led],
                           stdout=subprocess.PIPE, universal_newlines=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("REFUSED", r.stdout)

    def test_flag_texts_neutral(self):
        for k, v in ledger.FLAGS.items():
            words = set(re.findall(r"[a-z]+", (k + " " + v).lower()))
            self.assertEqual(words & set(EVALUATIVE), set(), k)


if __name__ == "__main__":
    unittest.main()
