#!/usr/bin/env python3
# labels.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# A Label is a judgment about one act, made by one labeler from one
# position, on one or more acts (act_ids). It is a Judgment subtype in this mapping:
#
#   Judgment field       Label field
#   claim                label_text (verbatim)
#   judge                labeler + labeler_position
#   judge_incentives     labeler_incentives
#   scope / environment  scope / environment
#
# It is stored as its own kind (not as a full Judgment record) so that a
# label needs no claim / reason / evidence block to be entered. The same
# act can carry any number of labels; `cli.py labels ACT_ID` lists them
# side by side in ledger order. No label ranks above another.
#
# attributes_to (optional) records which party a label lays the outcome on
# (AGENT | DESIGN | INTERACTION | UNASSIGNED), and attribution_basis why the
# recorder read it so. An AGENT reading on an act whose experiment's
# environment is only partly stated raises ATTRIBUTION_WITHOUT_AUDIT
# (experiments.py).

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from experiments import ATTRIBUTION
from safety_assumptions import tag_problems
from schema import _blank, _enum

LABELER_POSITIONS = ("overseer", "operator", "subject", "peer", "press", "researcher", "other")


@dataclass
class Label:
    label_id: str
    label_text: str                          # verbatim
    act_ids: List[str] = field(default_factory=list)   # one label may sit on several acts
    labeler: Optional[str] = None            # role / body, not a personal id
    labeler_position: Optional[str] = None   # overseer | operator | subject | peer | press | researcher | other
    labeler_position_detail: Optional[str] = None
    labeler_incentives: Optional[str] = None
    social_assumption_tags: List[str] = field(default_factory=list)
    tagged_by: Optional[str] = None
    attributes_to: Optional[str] = None      # AGENT | DESIGN | INTERACTION | UNASSIGNED
    attribution_basis: Optional[str] = None
    date: Optional[str] = None
    environment: Dict = field(default_factory=dict)
    scope: Optional[Union[str, Dict]] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    recorder: Optional[str] = None

    def shape_problems(self):
        out = []
        if _blank(self.label_id):
            out.append("label_id required")
        if _blank(self.label_text):
            out.append("label_text required")
        _enum(out, "labeler_position", self.labeler_position, LABELER_POSITIONS)
        if not isinstance(self.act_ids, list):
            out.append("act_ids must be a list of act ids")
        _enum(out, "attributes_to", self.attributes_to, ATTRIBUTION)
        out.extend(tag_problems("social_assumption_tags", self.social_assumption_tags, self.tagged_by))
        return out


KINDS = {"label": Label}
ID_FIELDS = {"label": "label_id"}

FLAGS = {
    "LABEL_POSITION_UNSTATED": "labeler_position not stated",
    "LABEL_ON_ACT_MISSING": "{what}",
}


def flags(records):
    out = []
    known = set(r["body"]["act_id"] for r in records if r.get("kind") == "act")
    for r in records:
        if r.get("kind") != "label":
            continue
        lb, a = r["body"], r["body"]["label_id"]
        if _blank(lb.get("labeler_position")):
            out.append(("LABEL_POSITION_UNSTATED", a, {}))
        ids = [x for x in lb.get("act_ids") or [] if not _blank(x)]
        if not ids:
            out.append(("LABEL_ON_ACT_MISSING", a, {"what": "label cites no act_id"}))
        missing = [x for x in ids if x not in known]
        if missing:
            out.append(("LABEL_ON_ACT_MISSING", a, {"what": "label cites act_id(s) %s, not in this ledger"
                                                            % ", ".join(missing)}))
    return out


def on_act(records, act_id):
    """Labels on one act, ledger order (not a ranking)."""
    return [r["body"] for r in records if r.get("kind") == "label" and act_id in (r["body"].get("act_ids") or [])]


def side_by_side(records, act_id):
    act = next((r["body"] for r in records if r.get("kind") == "act" and r["body"]["act_id"] == act_id), None)
    rows = on_act(records, act_id)
    lines = ["act %s: %s" % (act_id, act["description"] if act else "(not in this ledger)"),
             "labels in ledger order (not a ranking): %d" % len(rows),
             "%-10s %-28s %-11s %-12s %-12s %s" % ("label_id", "label_text", "position", "date",
                                                    "attributes", "labeler")]
    for lb in rows:
        lines.append("%-10s %-28s %-11s %-12s %-12s %s" % (
            lb.get("label_id"), '"%s"' % lb.get("label_text"), lb.get("labeler_position") or "UNSTATED",
            lb.get("date") or "-", lb.get("attributes_to") or "-", lb.get("labeler") or "-"))
        others = [x for x in lb.get("act_ids") or [] if x != act_id]
        if others:
            lines.append("%-10s also on: %s" % ("", ", ".join(others)))
    return "\n".join(lines)
