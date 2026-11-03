#!/usr/bin/env python3
# ledger.py -- CC0, stdlib only, python >= 3.5
# Status: co-authored (Kavik + Claude), 2026-11-03.
#
# Append-only JSONL ledger. One line per record:
#   {"kind": "report"|"checkout", "body": {...}, "body_hash": H(body),
#    "prev_hash": <hash of previous record or 64 zeros>, "hash": H(kind, body_hash, prev_hash)}
#
#   append()   the only write. No edit, no delete exists in this module.
#   verify()   recompute every hash and link; any edit or deletion breaks the chain.
#   merge()    union of two ledgers BY body_hash (same report forwarded twice
#              counts once). Output is a NEW file: a's records in order, then
#              b's records not already present, re-chained onto a. Inputs are
#              never touched.
#
#   python3 ledger.py add LEDGER "FR1|..."       append a compact report line
#   python3 ledger.py verify LEDGER
#   python3 ledger.py merge A B OUT              OUT must not exist

import hashlib
import json
import os
import sys

import compact
from refs import canonical

GENESIS = "0" * 64
KINDS = ("report", "checkout")


class LedgerError(ValueError):
    pass


def _h(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def _record(kind, body, prev):
    bh = _h(body)
    return {"kind": kind, "body": body, "body_hash": bh, "prev_hash": prev,
            "hash": _h({"kind": kind, "body_hash": bh, "prev_hash": prev})}


def read(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                raise LedgerError("line %d is not JSON" % n)
    return out


def verify(records):
    """List of problems; empty = intact chain."""
    probs = []
    prev = GENESIS
    for i, r in enumerate(records):
        if r.get("kind") not in KINDS:
            probs.append("record %d: unknown kind %r" % (i, r.get("kind")))
        if r.get("prev_hash") != prev:
            probs.append("record %d: prev_hash does not match record %d (deleted or reordered)" % (i, i - 1))
        if _h(r.get("body")) != r.get("body_hash"):
            probs.append("record %d: body edited (body_hash mismatch)" % i)
        expect = _h({"kind": r.get("kind"), "body_hash": r.get("body_hash"), "prev_hash": r.get("prev_hash")})
        if expect != r.get("hash"):
            probs.append("record %d: hash mismatch" % i)
        prev = r.get("hash")
    return probs


def append(path, kind, body):
    if kind not in KINDS:
        raise LedgerError("kind must be one of %s" % (KINDS,))
    if kind == "report":
        body = compact.normalize(body)
        probs = compact.check_report(body)
        if probs:
            raise LedgerError("report rejected: " + "; ".join(probs))
    recs = read(path)
    probs = verify(recs)
    if probs:
        raise LedgerError("ledger chain broken, refusing to append: " + probs[0])
    rec = _record(kind, body, recs[-1]["hash"] if recs else GENESIS)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
    return rec


def merge(a, b):
    """Union by body_hash. Returns new records (a's order, then b's new ones), re-chained."""
    for name, recs in (("a", a), ("b", b)):
        probs = verify(recs)
        if probs:
            raise LedgerError("ledger %s broken: %s" % (name, probs[0]))
    seen = set()
    out = []
    prev = GENESIS
    for r in list(a) + list(b):
        if r["body_hash"] in seen:
            continue
        seen.add(r["body_hash"])
        nr = _record(r["kind"], r["body"], prev)
        out.append(nr)
        prev = nr["hash"]
    return out


def write_new(path, records):
    if os.path.exists(path):
        raise LedgerError("%s exists; merge writes a new file only" % path)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")


def reports(records):
    return [r["body"] for r in records if r.get("kind") == "report"]


def checkouts(records):
    return [r["body"] for r in records if r.get("kind") == "checkout"]


def main(argv):
    try:
        if len(argv) == 3 and argv[0] == "add":
            rec = append(argv[1], "report", compact.decode(argv[2]))
            print("appended %s" % rec["hash"][:12])
            return 0
        if len(argv) == 2 and argv[0] == "verify":
            probs = verify(read(argv[1]))
            for p in probs:
                print("BROKEN " + p)
            print("intact" if not probs else "%d problems" % len(probs))
            return 1 if probs else 0
        if len(argv) == 4 and argv[0] == "merge":
            out = merge(read(argv[1]), read(argv[2]))
            write_new(argv[3], out)
            print("merged %d records -> %s" % (len(out), argv[3]))
            return 0
    except (LedgerError, compact.ReportError) as e:
        sys.stderr.write("REJECTED: %s\n" % e)
        return 1
    sys.stderr.write("usage: ledger.py add LEDGER \"FR1|...\" | verify LEDGER | merge A B OUT\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
