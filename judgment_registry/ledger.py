#!/usr/bin/env python3
# ledger.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
# Append-only JSONL, SHA-256 hash chain. Same pattern as
# assembly_instrument/ledger.py, kept as its own module because that one
# only accepts its own two record kinds and runs FR1 report checks.
#
#   {"kind", "body", "body_hash", "prev_hash", "hash"}
#   append()  the only write; no edit or delete exists
#   verify()  any edit, deletion or reorder breaks the chain
#   merge()   union by body_hash into a NEW record list; inputs untouched;
#             M11: each record keeps origin node(s) + merge event (mergeprov.py)
#
# A new version never edits an old one: supersession is a new record that
# points back. superseded_by is derived here, at read time.

import hashlib
import json
import os
from dataclasses import asdict

from schema import KIND_CLASSES, Judgment, SchemaError, SignalIntervention

import headrec  # M10: head record per ledger
import mergeprov  # M11: merge keeps origin node + merge event

GENESIS = "0" * 64


class LedgerError(ValueError):
    pass


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


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
            if line:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    raise LedgerError("line %d is not JSON" % n)
    return out


def verify(records):
    probs, prev = [], GENESIS
    for i, r in enumerate(records):
        if r.get("kind") not in KIND_CLASSES:
            probs.append("record %d: unknown kind %r" % (i, r.get("kind")))
        if r.get("prev_hash") != prev:
            probs.append("record %d: prev_hash does not match (deleted, inserted or reordered)" % i)
        if _h(r.get("body")) != r.get("body_hash"):
            probs.append("record %d: body changed after it was written" % i)
        if not mergeprov.record_hash_ok(_h, r):     # covers provenance (M11)
            probs.append("record %d: hash mismatch" % i)
        prev = r.get("hash")
    return probs


def build(kind, body):
    """Shape check only. Completeness gaps pass through and are flagged later."""
    cls = KIND_CLASSES.get(kind)
    if cls is None:
        raise LedgerError("kind must be one of %s" % (tuple(KIND_CLASSES),))
    try:
        obj = Judgment.from_dict(body) if cls is Judgment else cls(**body)
    except TypeError as e:
        raise LedgerError("bad %s record: %s" % (kind, e))
    except SchemaError as e:
        raise LedgerError(str(e))
    if cls is Judgment:
        probs = obj.shape_problems()
        if probs:
            raise LedgerError("; ".join(probs))
        for d in obj.dissent or []:          # D-M7: dissent is a position; holder defaults to anonymous
            if isinstance(d, dict) and not str(d.get("holder") or "").strip():
                d["holder"] = "anonymous"
        return obj.to_dict()
    if cls is SignalIntervention:
        probs = obj.shape_problems()
        if probs:
            raise LedgerError("; ".join(probs))
    return asdict(obj)    # defaults filled in, so stored bodies are complete


def append_records(records, kind, body):
    """Pure version of append: returns the new record list."""
    probs = verify(records)
    if probs:
        raise LedgerError("chain broken, refusing to append: " + probs[0])
    clean = build(kind, body)
    if kind == "judgment":
        ids = {r["body"]["judgment_id"] for r in records if r["kind"] == "judgment"}
        if clean["judgment_id"] in ids:
            raise LedgerError("judgment_id %s exists; a new version needs a new id that supersedes it"
                              % clean["judgment_id"])
    if kind == "intervention":
        ids = {r["body"]["intervention_id"] for r in records if r["kind"] == "intervention"}
        if clean["intervention_id"] in ids:
            raise LedgerError("intervention_id %s exists; a new version needs a new id"
                              % clean["intervention_id"])
    rec = _record(kind, clean, records[-1]["hash"] if records else GENESIS)
    return list(records) + [rec]


def head_problems(path, records, head=None):
    """M10: chain vs head. head=None reads the sidecar; pass a PUBLISHED head
    (headrec.parse("COUNT:HASH")) to check against a copy held elsewhere."""
    return headrec.check(records, head if head is not None else headrec.read_head(path))


def append(path, kind, body):
    old = read(path)
    probs = head_problems(path, old)
    if probs:
        raise LedgerError("head check failed, refusing to append: " + probs[0])
    recs = append_records(old, kind, body)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(recs[-1], sort_keys=True, ensure_ascii=False) + "\n")
    headrec.write_head(path, recs)
    return recs[-1]


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


def write_new(path, records):
    if os.path.exists(path):
        raise LedgerError("%s exists; merge writes a new file only" % path)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n")
    headrec.write_head(path, records)


def bodies(records, kind):
    return [r["body"] for r in records if r.get("kind") == kind]


def judgments(records):
    """Judgment objects in ledger order, superseded_by derived from the chain."""
    js = [Judgment.from_dict(b) for b in bodies(records, "judgment")]
    succ = {}
    for j in js:
        if j.supersedes:
            succ.setdefault(j.supersedes, []).append(j.judgment_id)
    for j in js:
        j.superseded_by = succ.get(j.judgment_id) or None
    return js
