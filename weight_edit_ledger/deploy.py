#!/usr/bin/env python3
# deploy.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# Deploy gate (partial use enforcement for D-M16). A checkpoint passes only
# if its hash is a registered base, or the after_hash at the end of an
# unbroken run of logged edits starting from a registered base:
#
#   base_hash --E1--> after_1 --E2--> after_2 ... --En--> candidate hash
#     (each edit's before_hash == the previous hash in the run)
#
# An unlogged edit breaks hash continuity, so the candidate is unreachable
# -> UNLOGGED_EDIT_CHAIN_BREAK, exit 1. This does not make editors log; it
# makes an unlogged edit undeployable through this gate. A ledger whose own
# chain or head is broken fails the gate too.
#
#   python3 deploy.py CHECKPOINT_FILE_OR_SHA256 [--ledger L]
# Exit: 0 reachable | 1 not reachable / ledger broken | 2 usage

import os
import re
import sys

import ledger
import loaders

FLAGS = {
    "UNLOGGED_EDIT_CHAIN_BREAK": "checkpoint {h} is not a registered base and no run of logged edits "
                                 "from a registered base ends at it",
}


def path_to(records, target):
    """-> (base record or None, [edit ids]) for the first run of logged edits
    from a registered base that ends at target; (None, None) if none."""
    bases = ledger.bases_of(records)
    if target in bases:
        return bases[target], []
    out_edges = {}
    for r in records:
        if r.get("kind") == "edit":
            e = r["body"]
            if e.get("before_hash") and e.get("after_hash"):
                out_edges.setdefault(e["before_hash"], []).append(e)
    seen = set(bases)
    frontier = [(h, bases[h], []) for h in sorted(bases)]
    while frontier:
        nxt = []
        for h, base, run in frontier:
            for e in out_edges.get(h, []):
                a = e["after_hash"]
                if a == target:
                    return base, run + [e["edit_id"]]
                if a not in seen:
                    seen.add(a)
                    nxt.append((a, base, run + [e["edit_id"]]))
        frontier = nxt
    return None, None


def gate(path, target):
    """-> dict: ok, flag (or None), base, edits, notes (check() flags on the run)."""
    recs = ledger.read(path)
    probs = ledger.verify(recs) + ledger.head_problems(path, recs)
    if probs:
        return {"ok": False, "flag": "UNLOGGED_EDIT_CHAIN_BREAK", "base": None, "edits": None,
                "detail": "ledger chain broken: " + probs[0], "notes": []}
    base, run = path_to(recs, target)
    if base is None:
        return {"ok": False, "flag": "UNLOGGED_EDIT_CHAIN_BREAK", "base": None, "edits": None,
                "detail": FLAGS["UNLOGGED_EDIT_CHAIN_BREAK"].format(h=target[:12]), "notes": []}
    notes = [f for f in ledger.check(recs) if f["about"] in run]
    return {"ok": True, "flag": None, "base": base["base_id"], "edits": run, "detail": None, "notes": notes}


def main(argv):
    argv = list(argv)
    path = ledger._opt(argv, "--ledger") or "weight_edits.jsonl"
    if len(argv) != 1:
        sys.stderr.write("usage: deploy.py CHECKPOINT_FILE_OR_SHA256 [--ledger L]\n")
        return 2
    arg = argv[0]
    target = arg if re.fullmatch(r"[0-9a-f]{64}", arg) and not os.path.exists(arg) else loaders.file_hash(arg)
    res = gate(path, target)
    if not res["ok"]:
        print("UNLOGGED_EDIT_CHAIN_BREAK  " + res["detail"])
        return 1
    print("reachable from base %s via %d logged edit(s): %s"
          % (res["base"], len(res["edits"]), " -> ".join(res["edits"]) or "(base itself)"))
    for f in res["notes"]:
        print("  note %-24s %-12s %s" % (f["flag"], f["about"], f["detail"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
