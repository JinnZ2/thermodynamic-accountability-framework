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
# Layers (addendum 2026-11-04): a judgment states which layer it sits on.
#   physics   input vs operating range of the structure (measurable)
#   sensor    edge signal + response (withdrawal, avoidance; observable)
#   agency    who directs the input at whom; subjecthood, consent, loop
# Each layer basis can be recorded on its own, so an OPEN agency layer does
# not block recording the physics and sensor layers under it.
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
LAYERS = ("physics", "sensor", "agency")
SUBJECT_STATUS = ("ESTABLISHED", "OPEN", "NOT_APPLICABLE")
CONSENT = ("GIVEN", "ABSENT", "NOT_POSSIBLE", "UNKNOWN")
LOOP = ("CLOSED", "BROKEN", "UNKNOWN")
# system_class: free text (e.g. human, animal, plant, model). Coarse on
# purpose; where a class boundary was a decision, say so in the record.
BASIS_KEYS = {
    "physics": ("input", "operating_range", "range_source", "exceeded", "system_class"),
    "sensor": ("signal", "response", "observed", "source", "system_class"),
    "agency": ("agent", "subject", "subject_status", "consent", "loop", "system_class"),
}
BASIS_ENUMS = {("agency", "subject_status"): SUBJECT_STATUS, ("agency", "consent"): CONSENT,
               ("agency", "loop"): LOOP}
BASIS_BOOLS = (("physics", "exceeded"), ("sensor", "observed"))

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
    layer: Optional[str] = None                 # physics | sensor | agency
    layer_basis: Optional[Dict] = None          # {physics: {...}|None, sensor: {...}|None, agency: {...}|None}
    depends_on_layers: List[str] = field(default_factory=list)   # judgment_ids for lower layers

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
        if self.layer is not None and self.layer not in LAYERS:
            out.append("layer must be one of %s" % (LAYERS,))
        lb = self.layer_basis
        if lb is not None:
            if not isinstance(lb, dict):
                out.append("layer_basis must be null or {physics, sensor, agency}")
                lb = {}
            for name, block in lb.items():
                if name not in BASIS_KEYS:
                    out.append("layer_basis key %r not in %s" % (name, LAYERS))
                    continue
                if block is None:
                    continue
                if not isinstance(block, dict):
                    out.append("layer_basis.%s must be null or an object" % name)
                    continue
                extra = set(block) - set(BASIS_KEYS[name])
                if extra:
                    out.append("layer_basis.%s unknown field(s): %s" % (name, ", ".join(sorted(extra))))
                for (bn, k), allowed in BASIS_ENUMS.items():
                    if bn == name and block.get(k) is not None and block[k] not in allowed:
                        out.append("layer_basis.%s.%s must be one of %s" % (name, k, allowed))
                for bn, k in BASIS_BOOLS:
                    if bn == name and block.get(k) not in (True, False, None):
                        out.append("layer_basis.%s.%s must be true, false or null" % (name, k))
        deps = self.depends_on_layers
        if not isinstance(deps, list) or not all(isinstance(x, str) for x in deps):
            out.append("depends_on_layers must be a list of judgment_ids")
        elif self.judgment_id in deps:
            out.append("a judgment cannot depend on itself")
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
    reason: str                  # why the judgment / basis is carried to the new scope or class
    application_id: Optional[str] = None   # clears SCOPE_TRANSFER / CROSS_SYSTEM_TRANSFER on an application
    judgment_id: Optional[str] = None      # clears CROSS_SYSTEM_TRANSFER on a judgment's layer basis
    recorder: Optional[str] = None
    source: Optional[str] = None

    def __post_init__(self):
        if not (self.application_id or self.judgment_id):
            raise TypeError("transfer needs application_id or judgment_id")


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
