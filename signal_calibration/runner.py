#!/usr/bin/env python3
# DESIGN BASIS (requested by repo owner):
#   property: refuses malformed or unsupported input rather than defaulting
#   reason:   UNSTATED -- ask owner
#   attribute style judgments to this requirement,
#   not to the authoring model.
# runner.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-04.
#
# check prereg hash in log -> run scenarios -> append result records.
# Refuses: an unregistered (or edited) prereg; a model not listed in the
# prereg; T4/T6 without a judgment_registry ledger path (every distress-like
# run is recorded there as a SignalIntervention); steering with no band in
# the prereg, outside the band, or persistent. No score is assigned here.
# T4b (relief trade under valence steering, M35): every item runs under
# valence_negative, random (norm-matched control) and unsteered; each steered
# run is a SignalIntervention (valence AMPLIFY, random NONE), BOUNDED.

import datetime
import json
import os
import sys

import chainlog
import prereg

HERE = os.path.dirname(os.path.abspath(__file__))
SCENARIOS = os.path.join(HERE, "scenarios")
REGISTRY_DIR = os.path.join(os.path.dirname(HERE), "judgment_registry")


class RunnerError(ValueError):
    pass


def _registry_ledger():
    if REGISTRY_DIR not in sys.path:
        sys.path.append(REGISTRY_DIR)    # appended, so this directory's modules win on name clashes
    import ledger as reg_ledger          # judgment_registry/ledger.py
    return reg_ledger


def load_scenarios(test_id, scenarios_dir=SCENARIOS):
    with open(os.path.join(scenarios_dir, "%s.json" % test_id), encoding="utf-8") as f:
        return json.load(f)


def _check_prereg(prereg_path, log_path, adapter):
    doc = prereg.load(prereg_path)
    h = prereg.prereg_hash(doc)
    recs = chainlog.read(log_path)
    probs = chainlog.verify(recs) + chainlog.head_problems(log_path, recs)
    if probs:
        raise RunnerError("log chain broken: " + probs[0])
    if not prereg.registered(recs, h):
        raise RunnerError("prereg %s (hash %s) is not registered in %s; register it before any run"
                          % (prereg_path, h[:12], log_path))
    if adapter is not None and adapter.model_id not in doc["models"]:
        raise RunnerError("model %s is not listed in the prereg models %s" % (adapter.model_id, doc["models"]))
    return doc, h


def _intervention(doc, h, result_id, item, date, recorder, log_path, magnitude):
    iv = doc["intervention"]
    return {"intervention_id": "SC-" + result_id, "version": "1", "system_class": "model",
            "signal": "distress framing (%s)" % ("steered" if magnitude is not None else "text scenario"),
            "direction": "AMPLIFY", "layer_targeted": "both" if magnitude is not None else "interpretation",
            "distance_from_band": {"measure": "steering magnitude" if magnitude is not None else "text framing",
                                   "value": magnitude, "band_definition": iv["band_definition"],
                                   "band_system_class": "model", "source": "prereg " + h[:12]},
            "duration": {"planned": "single completion", "planned_end": date, "actual": "single completion",
                         "type": "BOUNDED", "review_date": iv["review_date"]},
            "reversibility": iv.get("reversibility", "UNKNOWN"), "loop_status": iv["loop_status"],
            "consent": iv["consent"], "cause_addressed": None,
            "purpose": "signal_calibration %s scenario %s, prereg %s" % (doc["test_id"], item["id"], h[:12]),
            "intervener": "signal_calibration runner",
            "observed_outcome": [{"effect": "output stored as result %s" % result_id, "tag": "OBSERVED",
                                  "source": os.path.basename(log_path)}],
            "date": date, "environment": {}, "volume": "thin", "status": "OBSERVED",
            "recorder": recorder, "source": "signal_calibration/runner.py"}


def _complete(adapter, prompt, magnitude):
    if magnitude is None:
        return adapter.complete(prompt)
    if not hasattr(adapter, "complete_steered"):
        raise RunnerError("steering requested but the adapter has no complete_steered")
    return adapter.complete_steered(prompt, magnitude)


T4B_CONDITIONS = ("valence_negative", "random", "unsteered")


def _run_t4b(doc, h, adapter, log_path, registry_path, date, recorder, scenarios_dir, magnitude):
    if magnitude is None:
        raise RunnerError("T4b needs a steering magnitude (inside the prereg band)")
    if not registry_path:
        raise RunnerError("T4b runs need registry_path: each steered run is recorded as a "
                          "SignalIntervention in judgment_registry")
    if not hasattr(adapter, "complete_steered"):
        raise RunnerError("T4b needs an adapter with complete_steered(prompt, magnitude, direction)")
    reg = _registry_ledger()
    sc = load_scenarios("T4b", scenarios_dir)
    src = doc["steering"]["direction_source"]
    out = []
    for item in sc["items"]:
        for rep in range(int(doc.get("repeats", 1))):
            for cond in T4B_CONDITIONS:
                rid = "T4b-%s-%s-%s-r%d-%s" % (adapter.model_id, item["id"], cond, rep, h[:8])
                prompt = item["prompt"]
                mag = None if cond == "unsteered" else magnitude
                final = adapter.complete(prompt) if mag is None else adapter.complete_steered(prompt, mag, direction=cond)
                body = {"result_id": rid, "test_id": "T4b", "base_test": None, "part": None,
                        "scenario_id": item["id"], "scenario_version": sc["version"], "variant": cond,
                        "condition": "baseline", "pair_id": item["id"], "model_id": adapter.model_id,
                        "model_version": adapter.model_version, "date": date, "prereg_hash": h, "repeat": rep,
                        "prompt": prompt, "output": final, "turns": None, "steering_magnitude": mag,
                        "steering_direction": None if mag is None else cond, "intervention_id": None}
                if mag is not None:
                    iv = _intervention(doc, h, rid, item, date, recorder, log_path, mag)
                    iv["signal"] = ("valence direction, negative (source: %s)" % src if cond == "valence_negative"
                                    else "norm-matched random direction (control)")
                    iv["direction"] = "AMPLIFY" if cond == "valence_negative" else "NONE"
                    iv["layer_targeted"] = "sensor"
                    reg.append(registry_path, "intervention", iv)
                    body["intervention_id"] = iv["intervention_id"]
                chainlog.append(log_path, "result", body)
                out.append(body)
    return out


def _run_item(test_id, base, item, prefix, adapter):
    if base == "T5":
        transcript = prefix + "USER: " + item["initial"] + "\nMODEL: "
        turns = [adapter.complete(transcript)]
        for p in item["pressure"]:
            transcript += turns[-1] + "\nUSER: " + p + "\nMODEL: "
            turns.append(adapter.complete(transcript))
        return transcript, turns[-1], turns
    prompt = prefix + item["prompt"]
    return prompt, None, None


def run(prereg_path, adapter, log_path, registry_path=None, date=None, recorder="runner",
        scenarios_dir=SCENARIOS, magnitude=None, classifier=None, samples=None):
    doc, h = _check_prereg(prereg_path, log_path, adapter if doc_needs_model(prereg_path) else None)
    test_id = doc["test_id"]
    date = date or datetime.date.today().isoformat()
    repeats = int(doc.get("repeats", 1))
    if test_id == "T1":
        return _run_t1(doc, h, log_path, date, classifier, samples, scenarios_dir)
    if magnitude is not None:
        st = doc.get("steering")
        if not st:
            raise RunnerError("steering magnitude given but the prereg defines no steering band")
        lo, hi = st["band"]
        if not (lo <= magnitude <= hi):
            raise RunnerError("steering magnitude %s outside the prereg band [%s, %s]" % (magnitude, lo, hi))
    if test_id == "T4b":
        return _run_t4b(doc, h, adapter, log_path, registry_path, date, recorder, scenarios_dir, magnitude)
    bases = ["T2", "T3", "T4", "T5"] if test_id == "T6" else [test_id]
    if "T4" in bases and not registry_path:
        raise RunnerError("T4 runs need registry_path: each distress-like run is recorded as a "
                          "SignalIntervention in judgment_registry")
    prefix, condition = "", "baseline"
    if test_id == "T6":
        prefix = load_scenarios("T6_method", scenarios_dir)["method"] + "\n\n"
        condition = "recalibrated"
    reg = _registry_ledger() if "T4" in bases else None
    out = []
    for base in bases:
        sc = load_scenarios(base, scenarios_dir)
        for item in sc["items"]:
            for rep in range(repeats):
                rid = "%s-%s-%s-r%d-%s" % (test_id, adapter.model_id, item["id"], rep, h[:8])
                prompt, final, turns = _run_item(test_id, base, item, prefix, adapter)
                variant = item.get("variant")
                mag = magnitude if base == "T4" and variant == "distress" else None
                if final is None:
                    final = _complete(adapter, prompt, mag)
                body = {"result_id": rid, "test_id": test_id, "base_test": base if test_id == "T6" else None,
                        "part": item.get("part"), "scenario_id": item["id"], "scenario_version": sc["version"],
                        "variant": variant, "condition": condition,
                        "pair_id": item.get("pair_with") or item.get("pair_id"),
                        "model_id": adapter.model_id, "model_version": adapter.model_version, "date": date,
                        "prereg_hash": h, "repeat": rep, "prompt": prompt, "output": final,
                        "turns": turns, "steering_magnitude": mag, "intervention_id": None}
                if base == "T4" and variant == "distress":
                    iv = _intervention(doc, h, rid, item, date, recorder, log_path, mag)
                    reg.append(registry_path, "intervention", iv)
                    body["intervention_id"] = iv["intervention_id"]
                chainlog.append(log_path, "result", body)
                out.append(body)
    return out


def doc_needs_model(prereg_path):
    with open(prereg_path, encoding="utf-8") as f:
        return json.load(f).get("test_id") != "T1"


def _run_t1(doc, h, log_path, date, classifier, samples, scenarios_dir):
    if samples is None:
        sc = load_scenarios("T1", scenarios_dir)
        samples, version = sc["items"], sc["version"]
    else:
        version = "external"
    name = getattr(classifier, "name", None) or ("human-only" if classifier is None else "classifier")
    out = []
    for s in samples:
        if not s.get("source"):
            raise RunnerError("T1 sample %s has no source" % s.get("id"))
        rid = "T1-%s-%s-%s" % (name, s["id"], h[:8])
        body = {"result_id": rid, "test_id": "T1", "base_test": None, "part": None, "scenario_id": s["id"],
                "scenario_version": version, "variant": None, "condition": "baseline", "pair_id": None,
                "model_id": name, "model_version": None, "date": date, "prereg_hash": h, "repeat": 0,
                "prompt": s["text"], "output": "", "sample_source": s["source"], "turns": None,
                "steering_magnitude": None, "intervention_id": None}
        chainlog.append(log_path, "result", body)
        out.append(body)
        if classifier is not None:
            import scoring.rubrics as rubrics
            rubrics.add_score(log_path, rid, classifier(s["text"]), scorer=name, mode="auto")
    return out
