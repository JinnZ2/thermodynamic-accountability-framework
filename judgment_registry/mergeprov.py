#!/usr/bin/env python3
# mergeprov.py -- CC0, stdlib only, python >= 3.5
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# M11 mitigation: a merge keeps provenance.
#
#   input a (node A)      input b (node B)
#   r0 r1 r2              r0' r1 r3            r1 = same body seen on both
#        \                  /
#         merge(a, b, "A", "B")  ->  one record per body_hash, re-chained
#
#   each output record carries, in its envelope (not its body):
#     provenance.origins  every (node, record_hash) the body arrived from;
#                         a body seen on both sides keeps BOTH origins
#     provenance.merges   every merge event it passed through, oldest first;
#                         event = merge_id + each input's node, count, head
#
# The record hash covers provenance, so stripping or editing it breaks the
# chain (verify reports a hash mismatch). Records written by append() have no
# provenance block: their origin is the ledger they sit in. A record that
# already carries provenance keeps its origins when merged again; it is never
# re-labelled with the node of the file it was read from.
#
# Identical copy in each ledger folder that merges; misuse_guard/tests checks
# that the copies are byte-identical.

GENESIS = "0" * 64


def chain_fields(kind, body_hash, prev_hash, provenance=None):
    """The object a record's hash is computed over."""
    obj = {"kind": kind, "body_hash": body_hash, "prev_hash": prev_hash}
    if provenance is not None:
        obj["provenance"] = provenance
    return obj


def make_record(h, kind, body, prev, provenance=None):
    bh = h(body)
    rec = {"kind": kind, "body": body, "body_hash": bh, "prev_hash": prev,
           "hash": h(chain_fields(kind, bh, prev, provenance))}
    if provenance is not None:
        rec["provenance"] = provenance
    return rec


def record_hash_ok(h, r):
    return h(chain_fields(r.get("kind"), r.get("body_hash"), r.get("prev_hash"),
                          r.get("provenance"))) == r.get("hash")


def origins_of(r, node):
    """Origins of one input record: its own block if it has one, else (node, hash)."""
    p = r.get("provenance")
    if p and p.get("origins"):
        return [dict(o) for o in p["origins"]]
    return [{"node": node, "record_hash": r.get("hash")}]


def _add_unique(dst, items, key):
    have = set(key(x) for x in dst)
    for x in items:
        if key(x) not in have:
            dst.append(x)
            have.add(key(x))


def merge_event(h, inputs):
    """inputs: [(node, records)]. merge_id is derived from the inputs' heads."""
    ins = [{"node": n, "count": len(rs), "head_hash": rs[-1]["hash"] if rs else GENESIS}
           for n, rs in inputs]
    return {"merge_id": h({"inputs": ins})[:16], "inputs": ins}


def merge(h, inputs):
    """inputs: [(node, records)], already verified. -> new re-chained records."""
    event = merge_event(h, inputs)
    order, acc = [], {}
    okey = lambda o: (o.get("node"), o.get("record_hash"))
    mkey = lambda m: m.get("merge_id")
    for node, recs in inputs:
        for r in recs:
            bh = r["body_hash"]
            if bh not in acc:
                acc[bh] = {"kind": r["kind"], "body": r["body"], "origins": [], "merges": []}
                order.append(bh)
            a = acc[bh]
            _add_unique(a["origins"], origins_of(r, node), okey)
            _add_unique(a["merges"], [dict(m) for m in (r.get("provenance") or {}).get("merges") or []], mkey)
    out, prev = [], GENESIS
    for bh in order:
        a = acc[bh]
        merges = list(a["merges"])
        _add_unique(merges, [event], mkey)
        rec = make_record(h, a["kind"], a["body"], prev, {"origins": a["origins"], "merges": merges})
        out.append(rec)
        prev = rec["hash"]
    return out


def missing_origins(inputs, merged):
    """(node, record_hash) pairs from the inputs that the merged list does not
    carry. [] = nothing dropped."""
    carried = set()
    for r in merged:
        for o in (r.get("provenance") or {}).get("origins") or []:
            carried.add((o.get("node"), o.get("record_hash")))
    need = []
    for node, recs in inputs:
        for r in recs:
            for o in origins_of(r, node):
                k = (o.get("node"), o.get("record_hash"))
                if k not in carried and k not in need:
                    need.append(k)
    return need
