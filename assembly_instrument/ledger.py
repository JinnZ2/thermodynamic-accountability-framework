#!/usr/bin/env python3
# ledger.py -- CC0, stdlib only, python >= 3.5
# Status: co-authored (JinnZ2 + Claude), 2026-11-03.
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
#              never touched. M11: each output record keeps its origin node(s)
#              and the merge event in a provenance block (mergeprov.py).
#
#   python3 ledger.py add LEDGER "FR1|..."       append a compact report line
#   python3 ledger.py verify LEDGER
#   python3 ledger.py merge A B OUT [NODE_A NODE_B]   OUT must not exist;
#                                                nodes default to file names

import hashlib
import json
import os
import sys

import compact
import headrec  # M10: head record per ledger
import mergeprov  # M11: merge keeps origin node + merge event
from refs import canonical

GENESIS = "0" * 64
KINDS = ("report", "checkout")


class LedgerError(ValueError):
    pass


def _h(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def _record(kind, body, prev, provenance=None):
    return mergeprov.make_record(_h, kind, body, prev, provenance)


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
        if not mergeprov.record_hash_ok(_h, r):     # covers provenance (M11)
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
    probs = verify(recs) + head_problems(path, recs)
    if probs:
        raise LedgerError("ledger chain broken, refusing to append: " + probs[0])
    rec = _record(kind, body, recs[-1]["hash"] if recs else GENESIS)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
    headrec.write_head(path, recs + [rec])
    return rec


def head_problems(path, records, head=None):
    """M10: chain vs head. head=None reads the sidecar; pass a PUBLISHED head
    (headrec.parse("COUNT:HASH")) to check against a copy held elsewhere."""
    return headrec.check(records, head if head is not None else headrec.read_head(path))


def merge(a, b, node_a="a", node_b="b"):
    """Union by body_hash into NEW records, re-chained. M11: every output record
    carries provenance.origins (each (node, record_hash) its body came from; a
    body on both sides keeps both) and provenance.merges (this event appended)."""
    for name, recs in (("a", a), ("b", b)):
        probs = verify(recs)
        if probs:
            raise LedgerError("ledger %s broken: %s" % (name, probs[0]))
    if node_a == node_b:
        raise LedgerError("node labels must differ (both %r): origins would be indistinguishable" % node_a)
    return mergeprov.merge(_h, [(node_a, a), (node_b, b)])


def provenance(record):
    """Origins + merge events of a record; a never-merged record has none."""
    return record.get("provenance") or {"origins": [], "merges": []}


def node_label(path):
    """Default origin node for a merge input: the file name without extension."""
    return os.path.splitext(os.path.basename(path))[0]


def write_new(path, records):
    if os.path.exists(path):
        raise LedgerError("%s exists; merge writes a new file only" % path)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
    headrec.write_head(path, records)


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
            recs = read(argv[1])
            probs = verify(recs) + head_problems(argv[1], recs)
            for p in probs:
                print("BROKEN " + p)
            print("intact" if not probs else "%d problems" % len(probs))
            return 1 if probs else 0
        if len(argv) in (4, 6) and argv[0] == "merge":
            na, nb = node_label(argv[1]), node_label(argv[2])
            if len(argv) == 6:                       # merge A B OUT NODE_A NODE_B
                na, nb = argv[4], argv[5]
            out = merge(read(argv[1]), read(argv[2]), na, nb)
            write_new(argv[3], out)
            print("merged %d records -> %s" % (len(out), argv[3]))
            return 0
    except (LedgerError, compact.ReportError) as e:
        sys.stderr.write("REJECTED: %s\n" % e)
        return 1
    sys.stderr.write("usage: ledger.py add LEDGER \"FR1|...\" | verify LEDGER | merge A B OUT [NODE_A NODE_B]\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
