#!/usr/bin/env python3
# headrec.py -- CC0, stdlib only, python >= 3.5
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# M10 mitigation: a head record per hash-chained ledger.
#
#   ledger.jsonl            r0 -> r1 -> ... -> r(n-1)
#   ledger.jsonl.head.json  {"count": n, "head_hash": hash(r(n-1))}
#
# A chain alone verifies after its newest records are cut off, or after it is
# rebuilt from scratch. A head does not:
#
#   truncated  len(chain) < head.count               -> problem
#   rebuilt    chain[head.count - 1].hash != head    -> problem
#   grown      len(chain) > head.count, prefix same  -> ok (older published head)
#   no head    chain non-empty, head missing         -> problem
#
# The sidecar is rewritten on every append. It sits next to the ledger, so
# someone who can rewrite the ledger can rewrite the sidecar too: the defense
# is a PUBLISHED copy of the head (bulletin, radio, paper, another node),
# checked with `check LEDGER COUNT:HASH`. Publish the line `show` prints.
#
# Identical copy in each ledger folder (folders are copied to devices on
# their own); misuse_guard/tests checks that the copies are byte-identical.
#
#   python3 headrec.py show LEDGER                 line to publish
#   python3 headrec.py check LEDGER [COUNT:HASH]   exit 1 on any problem
#   python3 headrec.py adopt LEDGER                write a head for an existing
#                                                  ledger (after checking it
#                                                  against a published copy)

import json
import os
import sys

GENESIS = "0" * 64
SUFFIX = ".head.json"


def head_path(ledger_path):
    return ledger_path + SUFFIX


def head_of(records):
    return {"count": len(records), "head_hash": records[-1]["hash"] if records else GENESIS}


def write_head(ledger_path, records):
    tmp = head_path(ledger_path) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(head_of(records), f, sort_keys=True)
        f.write("\n")
    os.replace(tmp, head_path(ledger_path))


def read_head(ledger_path):
    p = head_path(ledger_path)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def parse(text):
    """'COUNT:HASH' -> head dict."""
    n, _, h = text.partition(":")
    return {"count": int(n), "head_hash": h.strip()}


def check(records, head):
    """Problems (list of str) comparing a chain with a head. [] = consistent."""
    if head is None:
        return ["no head record: truncation or rebuild cannot be detected"] if records else []
    try:
        n, h = int(head["count"]), str(head["head_hash"])
    except (KeyError, TypeError, ValueError):
        return ["head record is malformed"]
    if n < 0:
        return ["head record is malformed"]
    if len(records) < n:
        return ["chain has %d record(s), head says %d: truncated" % (len(records), n)]
    got = records[n - 1].get("hash") if n else GENESIS
    if got != h:
        return ["record %d hash differs from head: chain rebuilt or edited" % (n - 1)]
    return []


def _read(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def main(argv):
    if len(argv) >= 2 and argv[0] in ("show", "check", "adopt"):
        recs = _read(argv[1])
        if argv[0] == "show":
            hd = head_of(recs)
            print("%d:%s" % (hd["count"], hd["head_hash"]))
            return 0
        if argv[0] == "adopt":
            write_head(argv[1], recs)
            print("head written: %d record(s)" % len(recs))
            return 0
        head = parse(argv[2]) if len(argv) > 2 else read_head(argv[1])
        probs = check(recs, head)
        for p in probs:
            print("HEAD " + p)
        return 1 if probs else 0
    sys.stderr.write("usage: headrec.py show|adopt LEDGER | check LEDGER [COUNT:HASH]\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
