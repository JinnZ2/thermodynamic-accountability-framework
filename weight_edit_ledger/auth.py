#!/usr/bin/env python3
# auth.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# Resolves a two-person authorization_ref against a community_black_start
# two_person log (D7). Same check as judgment_registry/two_person_ref.py,
# generalized to any action; repeated here so this folder imports nothing
# from another (both have their own ledger.py).
#
#   ref -> log record: chain intact, kind two_person, action matches, GRANTED

import hashlib
import json
import os

GENESIS = "0" * 64


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


def ref_gap(ref, action, log):
    """'' when ref resolves to a GRANTED decision for action; else what is missing."""
    ref = str(ref or "").strip()
    if not ref:
        return "no authorization_ref"
    if log is None:
        return "two_person log not supplied; authorization_ref not checked"
    probs = chain_problems(log)
    if probs:
        return probs[0]
    rec = next((r for r in log if r.get("hash") == ref), None)
    if rec is None:
        return "authorization_ref %s not in the two_person log" % ref[:12]
    b = rec.get("body") or {}
    if b.get("kind") != "two_person" or b.get("action") != action:
        return "authorization_ref %s is not a %s decision" % (ref[:12], action)
    if b.get("decision") != "GRANTED":
        return "authorization_ref %s decision is %s" % (ref[:12], b.get("decision"))
    return ""
