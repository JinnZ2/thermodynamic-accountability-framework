#!/usr/bin/env python3
# schema.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (Kavik + Claude), 2026-11-04.
#
# DATA INTEGRITY ONLY. This module checks that a record is well-formed. It
# never rates a judgment, a judge or a tradition.
#
#   Judgment     one version of a stated judgment (unique judgment_id per record)
#   Application  the judgment applied to a case (scope / environment / date)
#   Transfer     the record that says why an application outside the recorded
#                scope was made
#   Withdrawal   a dissent withdrawn by its own holder
#
# Shape errors (wrong enum, superseded_by set by hand) are REJECTED at the
# door. Completeness gaps are not errors: they are integrity flags, raised by
# integrity.py, and the record is stored anyway.

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional

JUDGE_TYPES = ("person", "body", "tradition", "court", "other")
EVIDENCE_TAGS = ("OBSERVED", "DERIVED", "PROPOSED")
CHANGE_BASIS = ("CONDITIONS", "EVIDENCE", "NONE_STATED")
VOLUMES = ("thin", "medium", "solid")

# Required for completeness (MISSING_FIELD). `source` is checked separately
# as NO_SOURCE so one gap is not counted twice.
REQUIRED = ("judgment_id", "version", "claim", "scope.who", "scope.act_type",
            "environment", "date", "judge.name_or_body", "judge.type",
            "reason", "recorder", "volume")


class SchemaError(ValueError):
    pass


def _blank(v):
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    if isinstance(v, (list, dict)):
        return len(v) == 0
    return False


@dataclass
class Judgment:
    judgment_id: str
    version: Optional[str] = None
    claim: Optional[str] = None                 # as stated by the judge
    scope: Dict = field(default_factory=dict)   # {who, act_type, conditions, [dates: {from, to}]}
    environment: Dict = field(default_factory=dict)   # {scarcity, threat, tech_level, other}
    date: Optional[str] = None                  # ISO
    date_approx: bool = False                   # historical dates may be approximate
    judge: Dict = field(default_factory=dict)   # {name_or_body, type}
    judge_incentives: Optional[str] = None      # stakes held, as documented
    reason: Optional[str] = None                # argument as stated, verbatim where possible
    evidence: List[Dict] = field(default_factory=list)   # [{item, tag, source}]
    dissent: List[Dict] = field(default_factory=list)    # [{position, holder, reason, source}]
    supersedes: Optional[str] = None
    superseded_by: Optional[List[str]] = None   # DERIVED from the chain at read time only
    change_basis: List[str] = field(default_factory=list)
    change_detail: Optional[str] = None
    framing_check: Optional[Dict] = None        # {done, variants_tried, result_text}
    recorder: Optional[str] = None              # role code, not a personal ID
    source: Optional[str] = None
    volume: Optional[str] = None

    def get(self, dotted):
        cur = asdict(self)
        for part in dotted.split("."):
            if not isinstance(cur, dict):
                return None
            cur = cur.get(part)
        return cur

    def missing(self):
        return [k for k in REQUIRED if _blank(self.get(k))]

    def shape_problems(self):
        out = []
        if _blank(self.judgment_id):
            out.append("judgment_id required")
        if self.superseded_by:
            out.append("superseded_by is derived from the chain; do not set it by hand")
        jt = (self.judge or {}).get("type")
        if jt is not None and jt not in JUDGE_TYPES:
            out.append("judge.type must be one of %s" % (JUDGE_TYPES,))
        for e in self.evidence or []:
            if e.get("tag") not in EVIDENCE_TAGS:
                out.append("evidence tag must be one of %s" % (EVIDENCE_TAGS,))
        for c in self.change_basis or []:
            if c not in CHANGE_BASIS:
                out.append("change_basis entries must be from %s" % (CHANGE_BASIS,))
        if self.volume is not None and self.volume not in VOLUMES:
            out.append("volume must be one of %s" % (VOLUMES,))
        fc = self.framing_check
        if fc is not None and (not isinstance(fc, dict) or "done" not in fc):
            out.append("framing_check must be null or {done, variants_tried, result_text}")
        if self.supersedes and self.supersedes == self.judgment_id:
            out.append("a judgment cannot supersede itself")
        return out

    def to_dict(self):
        d = asdict(self)
        d.pop("superseded_by", None)
        return d

    @staticmethod
    def from_dict(d):
        known = set(Judgment.__dataclass_fields__)
        extra = set(d) - known
        if extra:
            raise SchemaError("unknown field(s): %s" % ", ".join(sorted(extra)))
        return Judgment(**d)


@dataclass
class Application:
    application_id: str
    judgment_id: str
    scope: Dict = field(default_factory=dict)
    environment: Dict = field(default_factory=dict)
    date: Optional[str] = None
    recorder: Optional[str] = None
    source: Optional[str] = None


@dataclass
class Transfer:
    application_id: str
    reason: str                  # why the judgment is carried to the new scope
    recorder: Optional[str] = None
    source: Optional[str] = None


@dataclass
class Withdrawal:
    judgment_id: str             # the version that carried the dissent
    position: str
    holder: str
    withdrawn_by_holder: bool = True
    recorder: Optional[str] = None
    source: Optional[str] = None


KIND_CLASSES = {"judgment": Judgment, "application": Application,
                "transfer": Transfer, "withdrawal": Withdrawal}
