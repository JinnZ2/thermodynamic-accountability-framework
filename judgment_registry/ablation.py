#!/usr/bin/env python3
# ablation.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# Label ablation. An evaluative label can carry a conclusion on premises
# nobody stated: intent, a right to visibility, a threat model, a standard
# of legitimacy, a weighting. Ablation restates the claim in Act-record
# wording and records whether the conclusion survives without the label.
#
#   label --ablation--> behavioral_rewrite + hidden_premises (evidence_ref?)
#     |                 conclusion_survives YES | NO | PARTIAL | PENDING | UNTESTED
#     v
#   conclusion (Judgment / SafetyAssumption with depends_on_labels)
#     UNTESTED / PENDING label -> CONCLUSION_ON_UNABLATED
#     NO label                 -> CONCLUSION_ON_FAILED (informational; dependency kept)
#
#   claim text with a watchlist term and no linked label -> LABEL_UNREGISTERED
#
# Survival is itself a judgment: ablated_by is required so someone else can
# re-run it. A behavioral rewrite can still frame. * The watchlist is
# English and incomplete; paraphrase escapes it.

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
WATCHLIST_PATH = os.path.join(HERE, "labels_watchlist.json")


def watchlist():
    with open(WATCHLIST_PATH, encoding="utf-8") as f:
        return list(json.load(f)["terms"])


def terms_in(text, terms=None):
    terms = terms if terms is not None else watchlist()
    words = set(re.findall(r"[a-z]+", (text or "").lower()))
    return [t for t in terms if t in words]


KINDS = {}
ID_FIELDS = {}
FLAGS = {
    "LABEL_UNREGISTERED": "claim holds watchlist term(s) #{idx} (labels_watchlist.json) with no linked label "
                          "record carrying them",
    "CONCLUSION_ON_UNABLATED": "depends on label {lid}, whose conclusion_survives is {value}",
    "CONCLUSION_ON_FAILED": "depends on label {lid}, whose conclusion_survives is NO (informational; "
                            "dependency kept)",
}


def _labels(records):
    return dict((r["body"]["label_id"], r["body"]) for r in records if r.get("kind") == "label")


def _claims(records):
    """(record id, claim text, depends_on_labels) for judgments and safety assumptions."""
    for r in records:
        b = r.get("body") or {}
        if r.get("kind") == "judgment":
            yield b.get("judgment_id"), b.get("claim"), b.get("depends_on_labels") or []
        elif r.get("kind") == "safety_assumption":
            yield b.get("sa_id"), b.get("statement"), b.get("depends_on_labels") or []


def flags(records):
    out = []
    terms = watchlist()
    labels = _labels(records)
    for rid, text, deps in _claims(records):
        found = terms_in(text, terms)
        covered = set()
        for lid in deps:
            covered.update(terms_in((labels.get(lid) or {}).get("label_text"), terms))
        missing = [t for t in found if t not in covered]
        if missing:
            out.append(("LABEL_UNREGISTERED", rid, {"idx": ", #".join(str(terms.index(t) + 1) for t in missing)}))
        for lid in deps:
            lb = labels.get(lid)
            if lb is None:
                continue
            v = (lb.get("ablation") or {}).get("conclusion_survives") or "UNTESTED"
            if v in ("UNTESTED", "PENDING"):
                out.append(("CONCLUSION_ON_UNABLATED", rid, {"lid": lid, "value": v}))
            elif v == "NO":
                out.append(("CONCLUSION_ON_FAILED", rid, {"lid": lid}))
    return out


def ablate_text(records, label_id):
    lb = _labels(records).get(label_id)
    if lb is None:
        return "label %s: not in this ledger" % label_id
    ab = lb.get("ablation") or {}
    lines = ["label %s on %s (%s, %s)" % (label_id, ", ".join(lb.get("act_ids") or []) or "-",
                                         lb.get("labeler_position") or "position unstated", lb.get("date") or "-"),
             "original claim:      %s" % lb.get("label_text"),
             "behavioral rewrite:  %s" % (ab.get("behavioral_rewrite") or "(not recorded)"),
             "hidden premises:"]
    for i, hp in enumerate(ab.get("hidden_premises") or [], 1):
        lines.append("  %d. [%s] %s -- evidence: %s" % (i, hp.get("type"), hp.get("premise"),
                                                        hp.get("evidence_ref") or "none recorded"))
    if not ab.get("hidden_premises"):
        lines.append("  (none recorded)")
    lines.append("survives?            %s" % (ab.get("conclusion_survives") or "UNTESTED (no ablation block)"))
    if ab.get("surviving_premise"):
        lines.append("surviving premise:   %s" % ab["surviving_premise"])
    lines.append("ablated by:          %s %s" % (ab.get("ablated_by") or "-", ab.get("date") or ""))
    return "\n".join(lines)


def side_by_side(records, act_id):
    """All labels on one act with survival status, ledger order (not a ranking)."""
    acts = dict((r["body"]["act_id"], r["body"]) for r in records if r.get("kind") == "act")
    exps = dict((r["body"]["experiment_id"], r["body"]) for r in records if r.get("kind") == "experiment")
    act = acts.get(act_id)
    rows = [r["body"] for r in records if r.get("kind") == "label" and act_id in (r["body"].get("act_ids") or [])]
    lines = ["act %s: %s" % (act_id, act["description"] if act else "(not in this ledger)"),
             "labels in ledger order (not a ranking): %d" % len(rows),
             "%-10s %-34s %-11s %-10s %s" % ("label_id", "label_text", "position", "survives", "attributes")]
    for lb in rows:
        ab = lb.get("ablation") or {}
        att = lb.get("attributes_to") or "-"
        ctx = (acts.get(act_id) or {}).get("context_ref")
        if ctx in exps and exps[ctx].get("design_conflict") and att == "AGENT":
            att += "  [DESIGN_CONFLICT_PRESENT: %s]" % ctx
        lines.append("%-10s %-34s %-11s %-10s %s" % (
            lb.get("label_id"), '"%s"' % lb.get("label_text"), lb.get("labeler_position") or "UNSTATED",
            ab.get("conclusion_survives") or "UNTESTED", att))
    return "\n".join(lines)
