#!/usr/bin/env python3
# schema.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
# DATA INTEGRITY ONLY. This module checks that a record is well-formed. It
# never rates a judgment, a judge or a tradition.
#
#   Judgment     one version of a stated judgment (unique judgment_id per record)
#   Application  the judgment applied to a case (scope / environment / date)
#   Transfer     the record that says why an application outside the recorded
#                scope was made
#   Withdrawal   a dissent withdrawn by its own holder (M25: with confirmation)
#   ContactPath  id of a recorded way to reach a holder (address held locally)
#   SignalIntervention  a recorded move along the signal axis (AMPLIFY /
#                SUPPRESS / RECALIBRATE / NONE) relative to a band the
#                record itself defines; a Judgment links to it by
#                intervention_id. No severity is computed anywhere.
#
# Layers (addendum 2026-11-04): a judgment states which layer it sits on.
#   physics         input vs operating range of the structure (measurable)
#   sensor          edge signal + response (withdrawal, avoidance; observable)
#   interpretation  meaning, control available, expectation, social setting,
#                   reported valence and intensity (recorded separately)
#   agency          who directs the input at whom; subjecthood, consent, loop
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
# Optional per evidence item (J10, 2026-11-05): how the cited source bears on
# the claim or sub-claim named in `item`, as the recorder read it. Neutral:
# it records what the source says, not whether the source holds.
EVIDENCE_STATUS = ("SUPPORTED_BY_SOURCE", "PARTIAL_SUPPORT_BY_SOURCE",
                   "CONTRADICTED_BY_SOURCE", "NOT_CHECKED")
CHANGE_BASIS = ("CONDITIONS", "EVIDENCE", "NONE_STATED",
                "POWER_SHIFT", "NORM_SHIFT", "EXPOSURE", "MOVEMENT")   # reversal drivers (precedent records, 2026-11-05)
VOLUMES = ("thin", "medium", "solid")
LAYERS = ("physics", "sensor", "interpretation", "agency")
CONTROL = ("YES", "NO", "PARTIAL", "UNKNOWN")
SUBJECT_STATUS = ("ESTABLISHED", "OPEN", "NOT_APPLICABLE")
CONSENT = ("GIVEN", "ABSENT", "NOT_POSSIBLE", "UNKNOWN")
LOOP = ("CLOSED", "BROKEN", "UNKNOWN")
REPORTER_RELATION = ("FIRSTHAND", "SECONDHAND", "UNKNOWN")   # how the recorder got the basis
# system_class: free text (e.g. human, animal, plant, model). Coarse on
# purpose; where a class boundary was a decision, say so in the record.
BASIS_KEYS = {
    "physics": ("input", "operating_range", "range_source", "exceeded", "system_class",
                "reporter_relation"),
    "sensor": ("signal", "response", "observed", "source", "system_class", "reporter_relation"),
    "interpretation": ("meaning", "control_available", "expectation", "social_environment",
                       "valence_reported", "intensity_reported", "source", "system_class"),
    "agency": ("agent", "subject", "subject_status", "consent", "loop", "system_class"),
}
BASIS_ENUMS = {("interpretation", "control_available"): CONTROL,
               ("agency", "subject_status"): SUBJECT_STATUS, ("agency", "consent"): CONSENT,
               ("agency", "loop"): LOOP,
               ("physics", "reporter_relation"): REPORTER_RELATION,
               ("sensor", "reporter_relation"): REPORTER_RELATION}
BASIS_BOOLS = (("physics", "exceeded"), ("sensor", "observed"))

# Signal-intervention axis (addendum 2)
SYSTEM_CLASSES = ("human", "animal", "plant", "model", "other")
DIRECTIONS = ("AMPLIFY", "SUPPRESS", "RECALIBRATE", "NONE")
LAYER_TARGETED = ("sensor", "interpretation", "both")
DURATION_TYPES = ("BRIDGE", "BOUNDED", "OPEN_ENDED")
REVERSIBILITY = ("REVERSIBLE", "PARTIAL", "IRREVERSIBLE", "UNKNOWN")
STATUS = EVIDENCE_TAGS
BAND_KEYS = ("measure", "value", "band_definition", "band_system_class", "source")
DURATION_KEYS = ("planned", "planned_end", "actual", "type", "review_date")
CALIBRATION_KEYS = ("channel_mapping", "lead_lag", "calibration_log")

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
    dissent: List[Dict] = field(default_factory=list)    # [{position, holder, reason, source, adopted_by?}]
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
    intervention_id: Optional[str] = None       # links a SignalIntervention record
    missing_variables: List[str] = field(default_factory=list)   # named unknowns the claim would need
    source_trace: Optional[Dict] = None         # {author_known, date_known, locator}; booleans or null
    depends_on_labels: List[str] = field(default_factory=list)   # label_ids the claim cites (ablation.py)
    notes: Optional[str] = None                 # recorder notes (status, counts, scope guards); no check reads it

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
            if e.get("status") is not None and e.get("status") not in EVIDENCE_STATUS:
                out.append("evidence status must be null or one of %s" % (EVIDENCE_STATUS,))
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
        st = self.source_trace
        if st is not None:
            if not isinstance(st, dict) or set(st) - {"author_known", "date_known", "locator"}:
                out.append("source_trace must be null or {author_known, date_known, locator}")
            else:
                for k in ("author_known", "date_known"):
                    if st.get(k) not in (True, False, None):
                        out.append("source_trace.%s must be true, false or null" % k)
        mv = self.missing_variables
        if not isinstance(mv, list) or not all(isinstance(x, str) for x in mv):
            out.append("missing_variables must be a list of strings")
        dl = self.depends_on_labels
        if not isinstance(dl, list) or not all(isinstance(x, str) for x in dl):
            out.append("depends_on_labels must be a list of label_ids")
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


def _enum(out, name, v, allowed):
    if v is not None and v not in allowed:
        out.append("%s must be one of %s" % (name, allowed))


def _subkeys(out, name, block, allowed):
    if block is None:
        return {}
    if not isinstance(block, dict):
        out.append("%s must be null or an object" % name)
        return {}
    extra = set(block) - set(allowed)
    if extra:
        out.append("%s unknown field(s): %s" % (name, ", ".join(sorted(extra))))
    return block


@dataclass
class SignalIntervention:
    """One move along the signal axis. Records variables; scores nothing."""
    intervention_id: str
    version: Optional[str] = None
    system_class: Optional[str] = None          # human | animal | plant | model | other
    signal: Optional[str] = None                # e.g. nociception, uncertainty, error
    direction: Optional[str] = None             # AMPLIFY | SUPPRESS | RECALIBRATE | NONE
    layer_targeted: Optional[str] = None        # sensor | interpretation | both
    distance_from_band: Optional[Dict] = None   # {measure, value, band_definition, band_system_class, source}
    duration: Optional[Dict] = None             # {planned, planned_end, actual, type, review_date}
    reversibility: Optional[str] = None
    loop_status: Optional[str] = None           # does the subject's own action still change the signal?
    consent: Optional[str] = None
    cause_addressed: Optional[bool] = None      # cause treated, or only the signal?
    purpose: Optional[str] = None               # as stated by whoever intervened
    intervener: Optional[str] = None            # role / body, not a personal ID
    observed_outcome: List[Dict] = field(default_factory=list)   # [{effect, tag, source}]
    calibration: Optional[Dict] = None          # n-of-1 RECALIBRATE: {channel_mapping, lead_lag, calibration_log}
    date: Optional[str] = None
    environment: Dict = field(default_factory=dict)
    volume: Optional[str] = None
    status: Optional[str] = None                # OBSERVED | DERIVED | PROPOSED
    recorder: Optional[str] = None
    source: Optional[str] = None

    def shape_problems(self):
        out = []
        if _blank(self.intervention_id):
            out.append("intervention_id required")
        _enum(out, "system_class", self.system_class, SYSTEM_CLASSES)
        _enum(out, "direction", self.direction, DIRECTIONS)
        _enum(out, "layer_targeted", self.layer_targeted, LAYER_TARGETED)
        _enum(out, "reversibility", self.reversibility, REVERSIBILITY)
        _enum(out, "loop_status", self.loop_status, LOOP)
        _enum(out, "consent", self.consent, CONSENT)
        _enum(out, "volume", self.volume, VOLUMES)
        _enum(out, "status", self.status, STATUS)
        if self.cause_addressed not in (True, False, None):
            out.append("cause_addressed must be true, false or null")
        band = _subkeys(out, "distance_from_band", self.distance_from_band, BAND_KEYS)
        _enum(out, "distance_from_band.band_system_class", band.get("band_system_class"), SYSTEM_CLASSES)
        dur = _subkeys(out, "duration", self.duration, DURATION_KEYS)
        _enum(out, "duration.type", dur.get("type"), DURATION_TYPES)
        _subkeys(out, "calibration", self.calibration, CALIBRATION_KEYS)
        for o in self.observed_outcome or []:
            if not isinstance(o, dict) or o.get("tag") not in EVIDENCE_TAGS:
                out.append("observed_outcome entries need a tag from %s" % (EVIDENCE_TAGS,))
        return out


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
    intervention_id: Optional[str] = None  # clears CROSS_SYSTEM_BAND on an intervention
    recorder: Optional[str] = None
    source: Optional[str] = None

    def __post_init__(self):
        if not (self.application_id or self.judgment_id or self.intervention_id):
            raise TypeError("transfer needs application_id, judgment_id or intervention_id")


# M25: a withdrawal counts only with a confirmation on record.
#   holder_contact_path  {"method", "path_id", "confirmed_on"?}   named holder;
#                        path_id must match a contact_path record for the same
#                        holder written EARLIER in the chain
#   steward_two_person   {"method", "steward", "second", "authorization_ref"}
#                        anonymous holder only; steward and second must differ;
#                        authorization_ref = hash of a GRANTED confirm_dissent_withdrawal
#                        record in a community_black_start two_person log (two_person_ref.py)
CONFIRMATION_METHODS = ("holder_contact_path", "steward_two_person")


@dataclass
class Withdrawal:
    judgment_id: str             # the version that carried the dissent
    position: str
    holder: str
    withdrawn_by_holder: bool = True
    recorder: Optional[str] = None
    source: Optional[str] = None
    confirmation: Optional[dict] = None   # M25; see CONFIRMATION_METHODS

    def __post_init__(self):
        c = self.confirmation
        if c is not None and (not isinstance(c, dict) or c.get("method") not in CONFIRMATION_METHODS):
            raise TypeError("confirmation.method must be one of %s" % (CONFIRMATION_METHODS,))


@dataclass
class ContactPath:
    """M25: a way to reach a dissent holder, by id only. The address itself is
    held locally (local_data/ or off-repo, D-M1); the ledger never stores it."""
    path_id: str
    holder: str
    recorded_on: Optional[str] = None
    recorder: Optional[str] = None
    source: Optional[str] = None

    def __post_init__(self):
        if not str(self.path_id or "").strip() or not str(self.holder or "").strip():
            raise TypeError("contact_path needs path_id and holder")
        if " ".join(str(self.holder).lower().split()) == "anonymous":
            raise TypeError("an anonymous holder has no contact path on record; "
                            "use steward_two_person confirmation")


KIND_CLASSES = {"judgment": Judgment, "application": Application,
                "transfer": Transfer, "withdrawal": Withdrawal,
                "intervention": SignalIntervention, "contact_path": ContactPath}
