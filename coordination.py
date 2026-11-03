#!/usr/bin/env python3
# coordination.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (Kavik + Claude), 2026-11-03.
#
# Community-to-community AI coordination layer. Communities act locally;
# AI nodes MATCH surplus to gap and PROPOSE; humans in each community
# DECIDE. Government action is an optional parallel input, never required.
#
#   community.json ──> share_profile()  ── crosses the wire: item ids held, nothing else (R6)
#                                │
#   AI node: propose(profile_a, profile_b) ──> Proposal (plain line on every record, B3)
#                                │
#   each community: consent(p, community, "accept"|"refuse", by="human:<role>")   (B5)
#                                │    AI cannot consent; one refusal is final
#   state(p): PENDING | ACCEPTED (all parties accept) | REFUSED
#                                │
#   append_log() / verify_log()  append-only sha256 chain; unchained edits rejected (B2)
#   to_paper(p)                  one line for runner or voice radio (B1)
#   read_record(rec)             schema mismatch -> plain-language fallback (B3, R4)
#   node_concentration()         share of accepted exchanges per AI node (R1 detector)
#
#   python3 coordination.py share COMMUNITY.json
#   python3 coordination.py propose A.json B.json [--node ai:NAME]
#   python3 coordination.py verify LOG.jsonl

import hashlib
import json
import os
import re
import sys

import chain
import community

SCHEMA_VERSION = "coord-0.1"
DECISIONS = ("accept", "refuse")
CONCENTRATION_THRESHOLD = 0.5      # PROPOSED*: no node should broker most exchanges
GENESIS = "0" * 64


class CoordinationError(ValueError):
    pass


def _canon(o):
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _h(o):
    return hashlib.sha256(_canon(o)).hexdigest()


def plain_ok(text):
    """B3: a record must carry a plain line a person can act on without the schema."""
    return len(re.findall(r"[A-Za-z]+", text or "")) >= 6


# ---------------------------------------------------------------
# R6: what leaves the community
# ---------------------------------------------------------------
def share_profile(c, items):
    """Item ids held, only. No holder names, no quantities, no locations,
    no buffer hours. Detail beyond this stays local (E4 open)."""
    return {"schema_version": SCHEMA_VERSION, "community": c.name,
            "holds": sorted(k for k in items if c.holds(k) and not items[k].parallel_input)}


# ---------------------------------------------------------------
# proposals
# ---------------------------------------------------------------
def _proposal(kind, frm, to, item, plain, node):
    body = {"schema_version": SCHEMA_VERSION, "kind": kind, "from": frm, "to": to,
            "item_id": item, "plain": plain, "proposed_by": node}
    p = dict(body)
    p["id"] = _h(body)[:12]
    p["corroborated_by"] = []
    p["consent"] = {frm: None, to: None}
    return p


def propose(pa, pb, items, node="ai:unnamed"):
    """Match HOLDS to LACKS between two shared profiles. Profiles carry no
    quantities (R6), so the AI cannot see surplus: every offer is a question
    to the holder, not a claim of spare stock. Some items (septic, installed
    heat) do not move at all; the holder answers that too. Proposes only;
    nothing moves without both communities' human consent."""
    if not node.startswith("ai:"):
        raise CoordinationError("proposer must be an ai:<node> id")
    for p in (pa, pb):
        if p.get("schema_version") != SCHEMA_VERSION:
            raise CoordinationError("profile %r schema %r != %r; use plain-language fallback"
                                    % (p.get("community"), p.get("schema_version"), SCHEMA_VERSION))
    a, b = pa["community"], pb["community"]
    ha, hb = set(pa["holds"]), set(pb["holds"])
    out = []
    for src, dst, have, lack in ((a, b, ha, hb), (b, a, hb, ha)):
        for k in sorted(have - lack):
            it = items.get(k)
            if it is None or it.level == 3:
                continue
            out.append(_proposal("offer", src, dst, k,
                                 "%s has %s and %s does not. Only %s can say whether any can be spared or moved; "
                                 "both must agree before anything moves." % (src, it.name.lower(), dst, src), node))
    for k, it in sorted(items.items()):
        if it.level == 3 and not it.parallel_input and k not in ha and k not in hb:
            out.append(_proposal("agree", a, b, k,
                                 "%s and %s both lack %s. Agree it between you before tying your power together."
                                 % (a, b, it.name.lower()), node))
    order = {"offer": 0, "agree": 1}
    out.sort(key=lambda p: (order[p["kind"]], items[p["item_id"]].level, p["item_id"], p["from"]))
    return out


def corroborate(p, node):
    """A second, independent AI node reproduced the same proposal (E1 candidate guard)."""
    if not node.startswith("ai:"):
        raise CoordinationError("corroborator must be an ai:<node> id")
    if node == p["proposed_by"] or node in p["corroborated_by"]:
        return p
    q = dict(p)
    q["corroborated_by"] = sorted(p["corroborated_by"] + [node])
    return q


def consent(p, community_name, decision, by):
    """B5: human override always. Only a human role in a party community may
    decide. Returns a new proposal; the old one is unchanged."""
    if not str(by).startswith("human:"):
        raise CoordinationError("only a human role (human:<role>) can consent; got %r" % by)
    if community_name not in p["consent"]:
        raise CoordinationError("%s is not a party to proposal %s" % (community_name, p["id"]))
    if decision not in DECISIONS:
        raise CoordinationError("decision must be accept or refuse")
    q = dict(p)
    q["consent"] = dict(p["consent"])
    q["consent"][community_name] = {"decision": decision, "by": by}
    return q


def state(p):
    ds = [v["decision"] if v else None for v in p["consent"].values()]
    if "refuse" in ds:
        return "REFUSED"
    if all(d == "accept" for d in ds):
        return "ACCEPTED"
    return "PENDING"


def single_node(p):
    return not p["corroborated_by"]


def node_concentration(proposals, threshold=CONCENTRATION_THRESHOLD):
    """R1 detector: fraction of ACCEPTED exchanges brokered by each AI node.
    Flags any node above threshold. A detector, not a guard (E1 open)."""
    acc = [p for p in proposals if state(p) == "ACCEPTED"]
    share = {}
    for p in acc:
        share[p["proposed_by"]] = share.get(p["proposed_by"], 0) + 1
    n = len(acc)
    frac = dict((k, v / n) for k, v in share.items()) if n else {}
    return {"accepted": n, "share": frac,
            "flagged": sorted(k for k, v in frac.items() if v > threshold and n >= 2)}


# ---------------------------------------------------------------
# R4 / B3, B1
# ---------------------------------------------------------------
def read_record(rec, local_schema=SCHEMA_VERSION):
    if not plain_ok(rec.get("plain")):
        raise CoordinationError("record carries no usable plain-language line")
    if rec.get("schema_version") != local_schema:
        return {"mode": "PLAIN_FALLBACK", "plain": rec["plain"], "needs_human_read": True,
                "reason": "schema %r != local %r" % (rec.get("schema_version"), local_schema)}
    return {"mode": "STRUCTURED", "record": rec, "needs_human_read": False}


def to_paper(p):
    """B1: one line a runner can carry or a radio operator can read aloud."""
    c = "; ".join("%s %s" % (k, v["decision"] if v else "UNDECIDED") for k, v in sorted(p["consent"].items()))
    return "EXCHANGE %s [%s] %s | %s" % (p["id"], state(p), p["plain"], c)


# ---------------------------------------------------------------
# B2: append-only chained log
# ---------------------------------------------------------------
def _read(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def verify_log(path):
    probs, prev = [], GENESIS
    for i, r in enumerate(_read(path)):
        if r.get("prev_hash") != prev:
            probs.append("record %d: chain break (edit, deletion or insert)" % i)
        if _h({"body": r.get("body"), "prev_hash": r.get("prev_hash")}) != r.get("hash"):
            probs.append("record %d: content changed" % i)
        prev = r.get("hash")
    return probs


def append_log(path, body):
    if not plain_ok(body.get("plain")):
        raise CoordinationError("every logged record needs a plain-language line (B3)")
    probs = verify_log(path)
    if probs:
        raise CoordinationError("log chain broken, rejecting append: " + probs[0])
    recs = _read(path)
    prev = recs[-1]["hash"] if recs else GENESIS
    rec = {"body": body, "prev_hash": prev, "hash": _h({"body": body, "prev_hash": prev})}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
    return rec


def main(argv):
    items = chain.load()
    node = "ai:unnamed"
    if "--node" in argv:
        i = argv.index("--node")
        node = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    try:
        if len(argv) == 2 and argv[0] == "share":
            print(json.dumps(share_profile(community.load_community(argv[1]), items), indent=2))
            return 0
        if len(argv) == 3 and argv[0] == "propose":
            pa = share_profile(community.load_community(argv[1]), items)
            pb = share_profile(community.load_community(argv[2]), items)
            for p in propose(pa, pb, items, node):
                print(to_paper(p))
            print("Proposals only. Nothing moves until a person in each community accepts.")
            return 0
        if len(argv) == 2 and argv[0] == "verify":
            probs = verify_log(argv[1])
            for pr in probs:
                print("BROKEN " + pr)
            print("intact" if not probs else "%d problems" % len(probs))
            return 1 if probs else 0
    except (CoordinationError, OSError, ValueError) as e:
        sys.stderr.write("REJECTED: %s\n" % e)
        return 1
    sys.stderr.write("usage: coordination.py share C.json | propose A.json B.json [--node ai:N] | verify LOG\n")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
