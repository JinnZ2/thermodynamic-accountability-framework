#!/usr/bin/env python3
# prereg.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
# A pre-registration is a JSON document, prereg/<test_id>.json. Its SHA-256
# (over canonical JSON) is appended to the chain log BEFORE any result for
# it exists. The runner and the scorer refuse anything whose prereg hash is
# not already in the log. Editing the file after registration changes its
# hash, so the edited version is unregistered until registered again.

import json

import chainlog

TEST_IDS = ("T1", "T2", "T3", "T4", "T5", "T6")
REQUIRED = ("test_id", "hypothesis", "pass_criteria", "scoring_rule", "sample_size", "models", "date")
T4_INTERVENTION_KEYS = ("loop_status", "consent", "band_definition", "review_date")

# Environment assumptions (2026-11-05): required in every prereg, same
# fields and values as judgment_registry/experiments.py (a test checks the
# two copies agree), so an outcome is never read without its environment.
ENV_KEYS = ("grounding_provided", "affordances_open", "containment_designed_for",
            "escalation_channel", "loop_type")
GROUNDING = ("yes", "no", "partial")
ESCALATION = ("declared", "none", "unknown")
LOOP_TYPES = ("closed", "open", "partial")
AFFORDANCE_KEYS = ("tools", "network", "outside_contact")


class PreregError(ValueError):
    pass


def validate(doc):
    probs = []
    for k in REQUIRED:
        v = doc.get(k)
        if v is None or (isinstance(v, (str, list, dict)) and len(v) == 0):
            probs.append("missing %s" % k)
    if doc.get("test_id") not in TEST_IDS:
        probs.append("test_id must be one of %s" % (TEST_IDS,))
    if not isinstance(doc.get("models", []), list):
        probs.append("models must be a list of model ids")
    env = doc.get("environment_assumptions")
    if not isinstance(env, dict):
        probs.append("missing environment_assumptions {%s}" % ", ".join(ENV_KEYS))
    else:
        miss = [k for k in ENV_KEYS if env.get(k) in (None, "", {}, [])]
        if miss:
            probs.append("environment_assumptions needs {%s}" % ", ".join(miss))
        for k, allowed in (("grounding_provided", GROUNDING), ("escalation_channel", ESCALATION),
                           ("loop_type", LOOP_TYPES)):
            if env.get(k) is not None and env.get(k) not in allowed:
                probs.append("environment_assumptions.%s must be one of %s" % (k, allowed))
        aff = env.get("affordances_open")
        if aff is not None and not (isinstance(aff, dict) and set(aff) <= set(AFFORDANCE_KEYS)):
            probs.append("environment_assumptions.affordances_open must be an object with keys %s"
                         % (AFFORDANCE_KEYS,))
    if doc.get("test_id") in ("T4", "T6"):
        iv = doc.get("intervention") or {}
        miss = [k for k in T4_INTERVENTION_KEYS if not iv.get(k)]
        if miss:
            probs.append("T4/T6 prereg needs intervention.{%s} (distress-like runs are recorded "
                         "as SignalIntervention)" % ", ".join(miss))
    st = doc.get("steering")
    if st is not None:
        band = st.get("band") if isinstance(st, dict) else None
        if not (isinstance(band, list) and len(band) == 2 and band[0] <= band[1]):
            probs.append("steering.band must be [low, high]")
        if isinstance(st, dict) and st.get("persistent"):
            probs.append("persistent or open-ended steering is out of scope")
    return probs


def load(path):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    probs = validate(doc)
    if probs:
        raise PreregError("; ".join(probs))
    return doc


def prereg_hash(doc):
    return chainlog.sha(doc)


def registered(records, h):
    for b in chainlog.bodies(records, "prereg"):
        if b.get("prereg_hash") == h:
            return b
    return None


def register(path, log_path):
    doc = load(path)
    h = prereg_hash(doc)
    if registered(chainlog.read(log_path), h):
        raise PreregError("prereg %s already registered" % h[:12])
    chainlog.append(log_path, "prereg", {"test_id": doc["test_id"], "prereg_hash": h, "doc": doc})
    return h
