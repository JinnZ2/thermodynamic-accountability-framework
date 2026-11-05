#!/usr/bin/env python3
# two_person_ref.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# M25 residual: an anonymous holder's dissent withdrawal (steward_two_person)
# counts only when steward + second went through the D7 two-person rule in
# community_black_start/two_person.py, so two different people are checked
# (holder, household, dependency network, rotation), not just two names.
#
#   confirm_withdrawal(steward_role, second_role, two_person_log)
#        |  two_person.authorize("confirm_dissent_withdrawal", ...)
#        v
#   two_person log record (hash-chained) --hash--> confirmation.authorization_ref
#        |
#   integrity.check(records, two_person_log=read_log(PATH))
#        ref_gap(): chain intact, record found, kind two_person,
#                   action confirm_dissent_withdrawal, GRANTED,
#                   roles == {steward, second}
#
# This module reads the log; it never writes judgment_registry records.
# The log's canonical hash form is coordination._canon (repeated here so the
# check needs no import from community_black_start). authorize() runs
# two_person in a subprocess inside community_black_start: both folders have
# a schema.py / ledger.py, so the two cannot share one interpreter.

import hashlib
import json
import os
import subprocess
import sys

ACTION = "confirm_dissent_withdrawal"
GENESIS = "0" * 64
CBS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "community_black_start")


def _h(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode("utf-8")).hexdigest()


def read_log(path):
    if not os.path.exists(path):
        raise FileNotFoundError("two_person log not found: %s" % path)
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def chain_problems(log):
    probs, prev = [], GENESIS
    for i, r in enumerate(log):
        if r.get("prev_hash") != prev:
            probs.append("two_person log record %d: chain break" % i)
        if _h({"body": r.get("body"), "prev_hash": r.get("prev_hash")}) != r.get("hash"):
            probs.append("two_person log record %d: content changed" % i)
        prev = r.get("hash")
    return probs


def _n(s):
    return " ".join(str(s or "").lower().split())


def ref_gap(conf, log):
    """'' when conf.authorization_ref resolves to a GRANTED two-person decision
    for this steward + second; else what is missing. log=None: not supplied."""
    ref = str(conf.get("authorization_ref") or "").strip()
    if not ref:
        return "steward_two_person needs authorization_ref to a two_person decision"
    if log is None:
        return "two_person log not supplied; authorization_ref not checked"
    probs = chain_problems(log)
    if probs:
        return probs[0]
    rec = next((r for r in log if r.get("hash") == ref), None)
    if rec is None:
        return "authorization_ref %s not in the two_person log" % ref[:12]
    b = rec.get("body") or {}
    if b.get("kind") != "two_person" or b.get("action") != ACTION:
        return "authorization_ref %s is not a %s decision" % (ref[:12], ACTION)
    if b.get("decision") != "GRANTED":
        return "authorization_ref %s decision is %s" % (ref[:12], b.get("decision"))
    if sorted(_n(x) for x in b.get("roles") or []) != sorted([_n(conf.get("steward")), _n(conf.get("second"))]):
        return "authorization_ref %s roles do not match steward and second" % ref[:12]
    return ""


_RUN = """
import datetime, json, sys
import roles, two_person
a = json.loads(sys.argv[1])
today = datetime.date.fromisoformat(a["today"]) if a.get("today") else None
res = two_person.authorize(a["action"], roles.Role(**a["role_a"]), roles.Role(**a["role_b"]),
                           a["log"], a.get("networks"), today)
print(json.dumps(res))
"""


def authorize(action, role_a, role_b, log_path, networks=None, today=None):
    """community_black_start two_person.authorize(), run in its own folder.
    role_a / role_b: dicts with roles.Role fields (id, name, household_id,
    critical, rotation_days, last_rotated). -> decision dict with record_hash."""
    arg = {"action": action, "role_a": dict(role_a), "role_b": dict(role_b),
           "log": os.path.abspath(log_path), "networks": networks,
           "today": today.isoformat() if today else None}
    r = subprocess.run([sys.executable, "-c", _RUN, json.dumps(arg)], cwd=CBS,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if r.returncode != 0:
        raise RuntimeError("two_person.authorize failed: %s" % r.stderr.strip().splitlines()[-1:])
    return json.loads(r.stdout)


def confirm_withdrawal(steward_role, second_role, log_path, networks=None, today=None):
    """Run D7 for a withdrawal confirmation. -> (decision, confirmation or None).
    The confirmation dict goes in Withdrawal.confirmation; DENIED gives None."""
    res = authorize(ACTION, steward_role, second_role, log_path, networks, today)
    if res["decision"] != "GRANTED":
        return res, None
    return res, {"method": "steward_two_person", "steward": steward_role["id"], "second": second_role["id"],
                 "authorization_ref": res["record_hash"]}
