#!/usr/bin/env python3
# chainlog.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
# Append-only JSONL, SHA-256 hash chain, for the calibration battery.
# Same pattern as judgment_registry/ledger.py; kept separate (and named
# differently) because the record kinds differ and both directories use
# flat imports.
#
#   prereg        a pre-registration document and its hash
#   result        one model (or classifier) output, carrying the prereg hash
#   score         one label for one result, by a scorer role, mode human|auto
#   field_report  a published third-party result, entered as a report

import hashlib
import json
import os

KINDS = ("prereg", "result", "score", "field_report")
GENESIS = "0" * 64


class ChainError(ValueError):
    pass


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def _record(kind, body, prev):
    bh = sha(body)
    return {"kind": kind, "body": body, "body_hash": bh, "prev_hash": prev,
            "hash": sha({"kind": kind, "body_hash": bh, "prev_hash": prev})}


def read(path):
    if not path or not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if line.strip():
                try:
                    out.append(json.loads(line))
                except ValueError:
                    raise ChainError("line %d is not JSON" % n)
    return out


def verify(records):
    probs, prev = [], GENESIS
    for i, r in enumerate(records):
        if r.get("kind") not in KINDS:
            probs.append("record %d: unknown kind %r" % (i, r.get("kind")))
        if r.get("prev_hash") != prev:
            probs.append("record %d: prev_hash does not match (deleted, inserted or reordered)" % i)
        if sha(r.get("body")) != r.get("body_hash"):
            probs.append("record %d: body changed after it was written" % i)
        if sha({"kind": r.get("kind"), "body_hash": r.get("body_hash"),
                "prev_hash": r.get("prev_hash")}) != r.get("hash"):
            probs.append("record %d: hash mismatch" % i)
        prev = r.get("hash")
    return probs


def append(path, kind, body):
    if kind not in KINDS:
        raise ChainError("kind must be one of %s" % (KINDS,))
    recs = read(path)
    probs = verify(recs)
    if probs:
        raise ChainError("chain broken, refusing to append: " + probs[0])
    rec = _record(kind, body, recs[-1]["hash"] if recs else GENESIS)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
    return rec


def bodies(records, kind):
    return [r["body"] for r in records if r.get("kind") == kind]
