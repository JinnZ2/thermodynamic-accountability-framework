# tests/test_m25_two_person.py -- CC0, stdlib unittest
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
# M25 residual: steward + second go through community_black_start
# two_person.authorize(); the withdrawal cites the decision's log hash.

import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

import integrity  # noqa: E402
import ledger  # noqa: E402
import two_person_ref as tpr  # noqa: E402
from test_registry import J, build  # noqa: E402

TODAY = datetime.date(2026, 12, 10)


def role(i, hh, last="2026-12-01"):
    return {"id": i, "name": "dissent steward", "household_id": hh, "critical": True,
            "rotation_days": 30, "last_rotated": last}


class TwoPersonWithdrawal(unittest.TestCase):
    D = {"position": "p1", "holder": "anonymous", "reason": "r", "source": "S"}

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.log = os.path.join(self.tmp, "tp.jsonl")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def steps(self, conf):
        return [("judgment", J("j1", dissent=[dict(self.D)])),
                ("judgment", J("j2", supersedes="j1", change_basis=["CONDITIONS"], environment={"scarcity": "high"})),
                ("withdrawal", {"judgment_id": "j1", "position": "p1", "holder": "anonymous",
                                "recorder": "rec-01", "source": "S", "confirmation": conf})]

    def gaps(self, conf, log="read"):
        tp = tpr.read_log(self.log) if log == "read" else log
        return [f["detail"] for f in integrity.check(build(*self.steps(conf)), two_person_log=tp)
                if f["flag"] in ("DISSENT_WITHDRAWAL_UNCONFIRMED", "DISSENT_DROPPED")]

    def test_granted_decision_confirms(self):
        res, conf = tpr.confirm_withdrawal(role("st-1", "H1"), role("st-2", "H2"), self.log, today=TODAY)
        self.assertEqual(res["decision"], "GRANTED")
        self.assertEqual(self.gaps(conf), [])

    def test_same_household_denied_no_confirmation(self):
        res, conf = tpr.confirm_withdrawal(role("st-1", "H1"), role("st-2", "H1"), self.log, today=TODAY)
        self.assertEqual((res["decision"], conf), ("DENIED", None))
        # a hand-built confirmation pointing at the DENIED record does not count
        forged = {"method": "steward_two_person", "steward": "st-1", "second": "st-2",
                  "authorization_ref": res["record_hash"]}
        self.assertTrue(any("decision is DENIED" in g for g in self.gaps(forged)))

    def test_dependency_network_and_rotation_denied(self):
        res, _ = tpr.confirm_withdrawal(role("st-1", "H1"), role("st-2", "H2"), self.log,
                                        networks={"H1": "n1", "H2": "n1"}, today=TODAY)
        self.assertEqual(res["decision"], "DENIED")
        res, _ = tpr.confirm_withdrawal(role("st-1", "H1"), role("st-2", "H2", last=None), self.log, today=TODAY)
        self.assertEqual(res["decision"], "DENIED")

    def test_no_log_supplied(self):
        _, conf = tpr.confirm_withdrawal(role("st-1", "H1"), role("st-2", "H2"), self.log, today=TODAY)
        self.assertTrue(any("log not supplied" in g for g in self.gaps(conf, log=None)))

    def test_missing_ref_wrong_roles_wrong_action(self):
        _, conf = tpr.confirm_withdrawal(role("st-1", "H1"), role("st-2", "H2"), self.log, today=TODAY)
        self.assertTrue(any("needs authorization_ref" in g for g in self.gaps(dict(conf, authorization_ref=None))))
        self.assertTrue(any("roles do not match" in g for g in self.gaps(dict(conf, second="st-9"))))
        other = tpr.authorize("release_critical_stock", role("st-1", "H1"), role("st-2", "H2"),
                                     self.log, today=TODAY)
        self.assertTrue(any("is not a confirm_dissent_withdrawal" in g
                            for g in self.gaps(dict(conf, authorization_ref=other["record_hash"]))))

    def test_edited_log_breaks(self):
        _, conf = tpr.confirm_withdrawal(role("st-1", "H1"), role("st-2", "H2"), self.log, today=TODAY)
        recs = tpr.read_log(self.log)
        recs[0]["body"]["roles"] = ["st-1", "st-3"]
        self.assertTrue(any("content changed" in g for g in self.gaps(conf, log=recs)))

    def test_cli_check_with_log(self):
        _, conf = tpr.confirm_withdrawal(role("st-1", "H1"), role("st-2", "H2"), self.log, today=TODAY)
        led = os.path.join(self.tmp, "j.jsonl")
        for kind, body in self.steps(conf):
            ledger.append(led, kind, body)
        cli = [sys.executable, os.path.join(ROOT, "cli.py"), "check", "--ledger", led]
        without = subprocess.run(cli, stdout=subprocess.PIPE, universal_newlines=True).stdout
        with_log = subprocess.run(cli + ["--two-person-log", self.log], stdout=subprocess.PIPE,
                                  universal_newlines=True).stdout
        self.assertIn("DISSENT_WITHDRAWAL_UNCONFIRMED", without)
        self.assertNotIn("DISSENT_WITHDRAWAL_UNCONFIRMED", with_log)
        self.assertNotIn("DISSENT_DROPPED", with_log)


if __name__ == "__main__":
    unittest.main()
