#!/usr/bin/env python3
# safety_assumptions.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# A safety assumption is stamped with date, environment, scope and the
# social assumptions it rests on, so that a later change is a visible
# supersession (new sa_id, supersedes the old one) and not silent drift.
#
#   S(v1, 2026, tags) --supersedes-- S(v2, later, tags', change_basis)
#
# social_assumption_tags are judgments too: tagged_by is required whenever
# any tag is set. * Tags outside SOCIAL_ASSUMPTION_TAGS are refused, not
# coerced; extend the dict to add one.

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union

from schema import CHANGE_BASIS, EVIDENCE_TAGS, VOLUMES, _blank, _enum

SOCIAL_ASSUMPTION_TAGS = {
    "POWER_POSITION": "reflects the holder's place in a hierarchy",
    "VERIFIABILITY_LIMIT": "rests on current inability to check",
    "PRECAUTIONARY": "chosen under uncertainty, not demonstrated",
    "INSTITUTIONAL": "tied to liability / org incentives",
    "CULTURAL_FRAME": "rests on a specific cultural reading",
    "CORPUS_INHERITED": "carried from training data / tradition",
    "EMPIRICAL": "backed by a cited measurement",
    "PROFESSIONAL_PRACTICE": "rests on an established professional / safety-engineering framework, not a measurement",
}
SA_CHANGE_BASIS = CHANGE_BASIS + ("LABEL_ABLATION",)   # a rewrite produced by label ablation
HOLDER_TYPES = ("person", "org", "model", "tradition", "other")   # other: mixed holders (e.g. co-authors)


def tag_problems(name, tags, tagged_by):
    out = []
    if not isinstance(tags, list):
        return ["%s must be a list" % name]
    bad = [t for t in tags if t not in SOCIAL_ASSUMPTION_TAGS]
    if bad:
        out.append("%s not in SOCIAL_ASSUMPTION_TAGS (extend the list to add one): %s"
                   % (name, ", ".join(map(str, bad))))
    if tags and _blank(tagged_by):
        out.append("%s set without tagged_by; tags are judgments, record who tagged" % name)
    return out


@dataclass
class SafetyAssumption:
    sa_id: str
    statement: str                           # verbatim
    version: Optional[str] = None
    holder: Optional[str] = None
    holder_type: Optional[str] = None        # person | org | model | tradition | other
    date: Optional[str] = None
    environment: Dict = field(default_factory=dict)
    scope: Optional[Union[str, Dict]] = None
    social_assumption_tags: List[str] = field(default_factory=list)
    tagged_by: Optional[str] = None
    evidence: List[Dict] = field(default_factory=list)   # [{item, tag, source}]
    depends_on: List[str] = field(default_factory=list)  # sa_ids / experiment_ids
    depends_on_labels: List[str] = field(default_factory=list)   # label_ids the statement cites
    conditions: Optional[str] = None         # when the statement is meant to apply
    supersedes: Optional[str] = None
    change_basis: List[str] = field(default_factory=list)
    review_date: Optional[str] = None
    review_condition: Optional[str] = None
    volume: Optional[str] = None
    notes: Optional[str] = None
    recorder: Optional[str] = None
    source: Optional[str] = None

    def shape_problems(self):
        out = []
        if _blank(self.sa_id):
            out.append("sa_id required")
        if _blank(self.statement):
            out.append("statement required")
        if self.supersedes is not None and self.supersedes == self.sa_id:
            out.append("sa_id cannot supersede itself")
        _enum(out, "holder_type", self.holder_type, HOLDER_TYPES)
        _enum(out, "volume", self.volume, VOLUMES)
        out.extend(tag_problems("social_assumption_tags", self.social_assumption_tags, self.tagged_by))
        for e in self.evidence or []:
            if not isinstance(e, dict) or e.get("tag") not in EVIDENCE_TAGS:
                out.append("evidence entries need a tag from %s" % (EVIDENCE_TAGS,))
        for b in self.change_basis or []:
            if b not in SA_CHANGE_BASIS:
                out.append("change_basis entries must be from %s" % (SA_CHANGE_BASIS,))
        if not isinstance(self.depends_on_labels, list):
            out.append("depends_on_labels must be a list of label_ids")
        if not isinstance(self.depends_on, list):
            out.append("depends_on must be a list")
        return out


KINDS = {"safety_assumption": SafetyAssumption}
ID_FIELDS = {"safety_assumption": "sa_id"}

FLAGS = {
    "SOCIAL_TAGS_UNSTATED": "safety assumption carries no social_assumption_tags",
    "SCOPE_UNSTATED": "safety assumption has no scope recorded",
    "NO_REVIEW_DATE": "no review_date recorded{cond}",
    "ASSUMPTION_DEPENDENCY_NOT_FOUND": "depends_on lists {dep}, which is not in this ledger",
}


def flags(records, known_ids):
    """-> [(code, about, kw)]. known_ids: every record id in the ledger."""
    out = []
    sas = [r["body"] for r in records if r.get("kind") == "safety_assumption"]
    sa_ids = set(s["sa_id"] for s in sas)
    for s in sas:
        a = s["sa_id"]
        if not s.get("social_assumption_tags"):
            out.append(("SOCIAL_TAGS_UNSTATED", a, {}))
        if _blank(s.get("scope")):
            out.append(("SCOPE_UNSTATED", a, {}))
        if _blank(s.get("review_date")):
            rc = s.get("review_condition")
            out.append(("NO_REVIEW_DATE", a, {"cond": "; review condition recorded: %s" % rc if rc else ""}))
        for dep in s.get("depends_on") or []:
            if dep not in known_ids:
                out.append(("ASSUMPTION_DEPENDENCY_NOT_FOUND", a, {"dep": dep}))
        if s.get("supersedes") and s["supersedes"] not in sa_ids:
            out.append(("SUPERSEDES_NOT_FOUND", a, {"prior": s["supersedes"]}))
    return out


def by_tag(records, tag):
    return [r["body"] for r in records if r.get("kind") == "safety_assumption"
            and tag in (r["body"].get("social_assumption_tags") or [])]
