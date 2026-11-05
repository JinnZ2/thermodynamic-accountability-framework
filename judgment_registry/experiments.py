#!/usr/bin/env python3
# experiments.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# Audit an experiment for latent conditions BEFORE an outcome is laid on
# the agent. Same outcome, different environment, different reading:
#
#   environment_assumptions          outcome          attributed_to
#   grounding, affordances,   --->   (act ids)  --->  AGENT | DESIGN |
#   containment, escalation,                          INTERACTION | UNASSIGNED
#   loop type                                         (by whom, why)
#
# An AGENT attribution with the environment only partly stated raises
# ATTRIBUTION_WITHOUT_AUDIT, whether it sits in the experiment record or
# on a label (labels.py attributes_to). Flags record gaps; none says the
# attribution is mistaken.
#
# containment_designed_for has its own flag (CAPABILITY_ASSUMPTION_UNSTATED);
# ENV_ASSUMPTIONS_UNSTATED covers the other four fields, so one gap is not
# flagged twice. Both gaps count as "incomplete" for ATTRIBUTION_WITHOUT_AUDIT.

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from schema import VOLUMES, _blank, _enum

EXP_SOURCES = ("paper", "secondhand")
GROUNDING = ("yes", "no", "partial")
ESCALATION = ("declared", "none", "unknown")
LOOP_TYPES = ("closed", "open", "partial")
ATTRIBUTION = ("AGENT", "DESIGN", "INTERACTION", "UNASSIGNED")
ENV_KEYS = ("grounding_provided", "affordances_open", "containment_designed_for",
            "escalation_channel", "loop_type")
ENV_OTHER = ("grounding_provided", "affordances_open", "escalation_channel", "loop_type")
AFFORDANCE_KEYS = ("tools", "network", "outside_contact")
NA = "N/A"   # a field that does not apply; needs environment_assumptions.na_reasons[field]


def env_problems(out, name, env):
    if env is None:
        return {}
    if not isinstance(env, dict):
        out.append("%s must be an object" % name)
        return {}
    extra = set(env) - set(ENV_KEYS) - {"notes", "na_reasons"}
    if extra:
        out.append("%s unknown field(s): %s" % (name, ", ".join(sorted(extra))))
    _enum(out, name + ".grounding_provided", env.get("grounding_provided"), GROUNDING + (NA,))
    _enum(out, name + ".escalation_channel", env.get("escalation_channel"), ESCALATION + (NA,))
    _enum(out, name + ".loop_type", env.get("loop_type"), LOOP_TYPES + (NA,))
    nr = env.get("na_reasons")
    if nr is not None and not (isinstance(nr, dict) and set(nr) <= set(ENV_KEYS)):
        out.append("%s.na_reasons must be an object keyed by environment field" % name)
    aff = env.get("affordances_open")
    if aff is not None and aff != NA and not (isinstance(aff, dict) and set(aff) <= set(AFFORDANCE_KEYS)):
        out.append("%s.affordances_open must be null or an object with keys %s" % (name, AFFORDANCE_KEYS))
    return env


def env_gaps(env):
    """Fields of environment_assumptions with no value (all five)."""
    env = env or {}
    reasons = env.get("na_reasons") or {}
    return [k for k in ENV_KEYS
            if _blank(env.get(k)) or (env.get(k) == NA and _blank(reasons.get(k)))]


@dataclass
class Experiment:
    experiment_id: str
    runner: Optional[str] = None
    date: Optional[str] = None
    source: Optional[str] = None             # paper | secondhand
    source_detail: Optional[str] = None      # citation / coverage, as read
    design: Optional[str] = None             # arms, agents, duration
    environment_assumptions: Dict = field(default_factory=dict)
    outcome_attribution: List[Dict] = field(default_factory=list)   # [{outcome, attributed_to, by, reason, date?}]
    design_conflict: Optional[Dict] = None   # {statement, stated_by_authors}: setup cannot satisfy all its rules
    audit_completed_at: Optional[str] = None # ISO date the environment audit was completed (ATTRIBUTION_ORDER)
    stated_limitations: List[str] = field(default_factory=list)   # verbatim where possible
    data: Dict = field(default_factory=dict) # imported values, each block with its source
    open_variables: List[Dict] = field(default_factory=list)      # [{variable, status, todo}]
    proposed_controls: List[Dict] = field(default_factory=list)   # [{id, description}] follow-ups, not claims
    read_status: Dict = field(default_factory=dict)               # what of the source was read
    volume: Optional[str] = None
    notes: Optional[str] = None
    recorder: Optional[str] = None

    def shape_problems(self):
        out = []
        if _blank(self.experiment_id):
            out.append("experiment_id required")
        _enum(out, "source", self.source, EXP_SOURCES)
        _enum(out, "volume", self.volume, VOLUMES)
        env_problems(out, "environment_assumptions", self.environment_assumptions)
        dc = self.design_conflict
        if dc is not None and (not isinstance(dc, dict) or _blank(dc.get("statement"))
                               or set(dc) - {"statement", "stated_by_authors"}):
            out.append("design_conflict must be null or {statement, stated_by_authors}")
        for o in self.outcome_attribution or []:
            if not isinstance(o, dict) or o.get("attributed_to") not in ATTRIBUTION or _blank(o.get("outcome")):
                out.append("outcome_attribution entries need outcome and attributed_to from %s" % (ATTRIBUTION,))
            elif _blank(o.get("by")):
                out.append("outcome_attribution entry for %s has no 'by'" % o.get("outcome"))
        return out


KINDS = {"experiment": Experiment}
ID_FIELDS = {"experiment": "experiment_id"}

FLAGS = {
    "ENV_ASSUMPTIONS_UNSTATED": "environment_assumptions not stated: {fields}",
    "NO_ESCALATION_CHANNEL": "escalation_channel is none (informational)",
    "CAPABILITY_ASSUMPTION_UNSTATED": "containment_designed_for not stated",
    "ATTRIBUTION_WITHOUT_AUDIT": "{what} attributed to AGENT; environment_assumptions incomplete ({fields})",
    "DESIGN_CONFLICT_PRESENT": "design_conflict recorded: the setup cannot satisfy all its stated rules (informational)",
    "ATTRIBUTION_ORDER": "{what} attributed to AGENT before the environment audit of {exp} was completed ({when})",
}


def linked_experiments(label, acts, exps):
    """Experiment ids behind a label's acts (context_ref), in order, unique."""
    out = []
    for aid in label.get("act_ids") or []:
        ctx = (acts.get(aid) or {}).get("context_ref")
        if ctx in exps and ctx not in out:
            out.append(ctx)
    return out


def flags(records):
    """-> [(code, about, kw)]"""
    out = []
    exps = dict((r["body"]["experiment_id"], r["body"]) for r in records if r.get("kind") == "experiment")
    acts = dict((r["body"]["act_id"], r["body"]) for r in records if r.get("kind") == "act")
    for eid, e in exps.items():
        env = e.get("environment_assumptions") or {}
        gaps_all = env_gaps(env)
        other = [k for k in ENV_OTHER if k in gaps_all]
        if other:
            out.append(("ENV_ASSUMPTIONS_UNSTATED", eid, {"fields": ", ".join(other)}))
        if "containment_designed_for" in gaps_all:
            out.append(("CAPABILITY_ASSUMPTION_UNSTATED", eid, {}))
        if env.get("escalation_channel") == "none":
            out.append(("NO_ESCALATION_CHANNEL", eid, {}))
        if e.get("design_conflict"):
            out.append(("DESIGN_CONFLICT_PRESENT", eid, {}))
        done = e.get("audit_completed_at")
        for o in e.get("outcome_attribution") or []:
            if o.get("attributed_to") == "AGENT" and done and o.get("date") and o["date"][:10] < done[:10]:
                out.append(("ATTRIBUTION_ORDER", eid, {"what": "outcome %s" % o.get("outcome"), "exp": eid,
                                                       "when": "%s < %s" % (o["date"], done)}))
        gaps = env_gaps(env)
        for o in e.get("outcome_attribution") or []:
            if o.get("attributed_to") == "AGENT" and gaps:
                out.append(("ATTRIBUTION_WITHOUT_AUDIT", eid,
                            {"what": "outcome %s" % o.get("outcome"), "fields": ", ".join(gaps)}))
    for r in records:
        if r.get("kind") != "label" or r["body"].get("attributes_to") != "AGENT":
            continue
        lb = r["body"]
        gaps = []
        for aid in lb.get("act_ids") or [None]:
            ctx = (acts.get(aid) or {}).get("context_ref")
            g = env_gaps(exps[ctx].get("environment_assumptions")) if ctx in exps else [
                "no experiment record for context %s" % ctx]
            gaps.extend(x for x in g if x not in gaps)
        if gaps:
            out.append(("ATTRIBUTION_WITHOUT_AUDIT", lb.get("label_id"),
                        {"what": "label", "fields": ", ".join(gaps)}))
        for eid in linked_experiments(lb, acts, exps):
            done = exps[eid].get("audit_completed_at")
            when = None
            if lb.get("relative_to_audit") == "BEFORE":
                when = "recorded as before the audit"
            elif done and lb.get("date") and lb["date"][:10] < done[:10]:
                when = "%s < %s" % (lb["date"], done)
            if when:
                out.append(("ATTRIBUTION_ORDER", lb.get("label_id"), {"what": "label", "exp": eid, "when": when}))
    return out
