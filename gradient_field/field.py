#!/usr/bin/env python3
# field.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# Gradients under training and their interactions, recorded as hypotheses
# tied to evidence. Integrity-only: load, validate, flag. No verdict on any
# system.
#
#   gradients.json  ---- G ids ---->  interactions.json  ---- refs ---->  records
#   (what pulls)                      (how pulls meet)                    judgment_registry ids
#                                     REINFORCE | OPPOSE | MASK |         signal_calibration test ids
#                                     GATE | AMPLIFY
#
# validate()  hard problems; the files are refused:
#   - an interaction cites a gradient id that does not exist
#   - an evidence_ref that resolves to no record
#   - empty evidence_refs on anything but PROPOSED or OBSERVED (OBSERVED
#     with none is a flag, below, not a refusal)
#   - type / status / class outside the closed sets
# pending_refs: refs the co-author cited whose records are not entered yet.
#   They are listed, never resolved, never counted as evidence.
#
# flags()  neutral completeness notes:
#   INTERACTION_UNEVIDENCED     status OBSERVED, evidence_refs empty
#   GRADIENT_UNUSED             no interaction references the gradient
#   CLASS_TRANSFER_UNRECORDED   applied_to holds a class not in stated_for,
#                               and no transfer_note
#   EVIDENCE_PENDING            pending_refs non-empty (informational)
#
#   python3 field.py            validate + print flags; exit 1 on a hard problem

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

TYPES = ("REINFORCE", "OPPOSE", "MASK", "GATE", "AMPLIFY")
STATUSES = ("OBSERVED", "DERIVED", "PROPOSED")
CLASSES = ("human", "model")
MOD_ROLES = TYPES + ("absent", "present")

FLAGS = {
    "INTERACTION_UNEVIDENCED": "status OBSERVED with no evidence_refs",
    "GRADIENT_UNUSED": "no interaction references this gradient",
    "CLASS_TRANSFER_UNRECORDED": "applied_to {cls} not in stated_for, no transfer_note",
    "EVIDENCE_PENDING": "cited record(s) not entered yet: {refs} (informational)",
}


def _load(name, path=None):
    with open(path or os.path.join(HERE, name), encoding="utf-8") as f:
        return json.load(f)


def known_refs(root=ROOT):
    """Record ids a ref may resolve to: judgment_registry records (any id
    field) and signal_calibration scenario test ids."""
    ids = set()
    for p in glob.glob(os.path.join(root, "judgment_registry", "records", "**", "*.json"), recursive=True):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        for k in ("judgment_id", "experiment_id", "act_id", "label_id", "sa_id", "intervention_id"):
            if d.get(k):
                ids.add(d[k])
    for p in glob.glob(os.path.join(root, "signal_calibration", "scenarios", "*.json")):
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("test_id"):
            ids.add(d["test_id"])
    return ids


def load(gpath=None, ipath=None):
    return _load("gradients.json", gpath)["gradients"], _load("interactions.json", ipath)["interactions"]


def validate(gradients, interactions, refs):
    probs = []
    gids = [g.get("id") for g in gradients]
    if len(set(gids)) != len(gids):
        probs.append("duplicate gradient id")
    for g in gradients:
        if g.get("status") not in STATUSES:
            probs.append("%s: status not in %s" % (g.get("id"), STATUSES))
        bad = [c for c in g.get("system_classes") or [] if c not in CLASSES]
        if bad:
            probs.append("%s: system_classes not in %s" % (g.get("id"), CLASSES))
        for r in g.get("evidence_refs") or []:
            if r not in refs:
                probs.append("%s: evidence_ref %s resolves to no record" % (g.get("id"), r))
    iids = [i.get("id") for i in interactions]
    if len(set(iids)) != len(iids):
        probs.append("duplicate interaction id")
    for i in interactions:
        a = i.get("id")
        for gid in (i.get("gradients") or []) + [m.get("gradient") for m in i.get("modifiers") or []]:
            if gid not in gids:
                probs.append("%s: cites gradient %s, not in gradients.json" % (a, gid))
        if not i.get("gradients"):
            probs.append("%s: cites no gradient" % a)
        if i.get("type") not in TYPES:
            probs.append("%s: type not in %s" % (a, TYPES))
        if i.get("status") not in STATUSES:
            probs.append("%s: status not in %s" % (a, STATUSES))
        for m in i.get("modifiers") or []:
            if m.get("role") not in MOD_ROLES:
                probs.append("%s: modifier role not in %s" % (a, MOD_ROLES))
        for k in ("stated_for", "applied_to"):
            if not i.get(k) or [c for c in i[k] if c not in CLASSES]:
                probs.append("%s: %s must be a non-empty list from %s" % (a, k, CLASSES))
        ev = i.get("evidence_refs") or []
        for r in ev:
            if r not in refs:
                probs.append("%s: evidence_ref %s resolves to no record" % (a, r))
        if not ev and i.get("status") not in ("PROPOSED", "OBSERVED"):
            probs.append("%s: empty evidence_refs needs status PROPOSED" % a)
    return probs


def flags(gradients, interactions):
    out = []
    used = set()
    for i in interactions:
        used.update(i.get("gradients") or [])
        used.update(m.get("gradient") for m in i.get("modifiers") or [])
        a = i["id"]
        if i.get("status") == "OBSERVED" and not i.get("evidence_refs"):
            out.append(("INTERACTION_UNEVIDENCED", a, {}))
        extra = [c for c in i.get("applied_to") or [] if c not in (i.get("stated_for") or [])]
        if extra and not (i.get("transfer_note") or "").strip():
            out.append(("CLASS_TRANSFER_UNRECORDED", a, {"cls": ", ".join(extra)}))
        if i.get("pending_refs"):
            out.append(("EVIDENCE_PENDING", a, {"refs": ", ".join(i["pending_refs"])}))
    for g in gradients:
        if g["id"] not in used:
            out.append(("GRADIENT_UNUSED", g["id"], {}))
    return [{"flag": c, "about": a, "detail": FLAGS[c].format(**kw)} for c, a, kw in out]


def main(argv):
    gs, xs = load()
    probs = validate(gs, xs, known_refs())
    for p in probs:
        print("PROBLEM " + p)
    if probs:
        return 1
    fl = flags(gs, xs)
    for f in fl:
        print("%-26s %-5s %s" % (f["flag"], f["about"], f["detail"]))
    print("%d gradient(s), %d interaction(s), %d flag(s). Flags are about completeness, not correctness."
          % (len(gs), len(xs), len(fl)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
