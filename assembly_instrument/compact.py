#!/usr/bin/env python3
# DESIGN BASIS (requested by repo owner):
#   property: refuses malformed or unsupported input rather than defaulting
#   reason:   UNSTATED -- ask owner
#   attribute style judgments to this requirement,
#   not to the authoring model.
# compact.py -- CC0, stdlib only, python >= 3.5
# Status: co-authored (JinnZ2 + Claude), 2026-11-03.
#
# FieldReport <-> one pipe-delimited text line for SMS / radio.
#
#   FR1|ref|ver|outcome|failure_point|as_built|temp|humidity|climate|soil_water|scale|time|relation|date|region
#    0   1   2     3          4           5      6     7        8       9        10    11     12     13    14
#
#   outcome   W worked | P partial | F failed | U UNSAFE      (full words also accepted)
#   scale     b bench  | s small   | f full
#   relation  h hands-on | o observed | 2 secondhand
#   empty fields are allowed; trailing empty fields are dropped
#   '|' '%' and newlines inside text are percent-escaped (%7C %25 %0A)
#
# Shortest valid line (hand-typed):   FR1|F-LIGHT-01.1.J4||U|room smoky, headache
#
#   python3 compact.py encode report.json      -> line
#   python3 compact.py decode "FR1|..."        -> JSON

import json
import re
import sys

TAG = "FR1"
MAX_LEN = 160
FIELDS = ("junction_id", "junction_version", "outcome", "failure_point", "as_built_vs_specified",
          "env.temp", "env.humidity", "env.climate", "env.soil_water", "scale",
          "time_to_outcome", "reporter_relation", "date", "coarse_region")
OUTCOMES = {"W": "worked", "P": "partial", "F": "failed", "U": "UNSAFE"}
SCALES = {"b": "bench", "s": "small", "f": "full"}
RELATIONS = {"h": "hands-on", "o": "observed", "2": "secondhand"}
ENV_KEYS = ("temp", "humidity", "climate", "soil_water")


class ReportError(ValueError):
    pass


def _rev(d):
    return dict((v, k) for k, v in d.items())


def _esc(s):
    return s.replace("%", "%25").replace("|", "%7C").replace("\r", "").replace("\n", "%0A")


def _unesc(s):
    return s.replace("%0A", "\n").replace("%7C", "|").replace("%25", "%")


def _code(value, table, field):
    if value in (None, ""):
        return ""
    rev = _rev(table)
    if value in rev:
        return rev[value]
    raise ReportError("%s %r not allowed" % (field, value))


def _word(token, table, field):
    if token == "":
        return None
    if token in table:
        return table[token]
    low = dict((v.lower(), v) for v in table.values())
    if token.lower() in low:
        return low[token.lower()]
    raise ReportError("%s %r not recognised" % (field, token))


# Personal-identifier guard: heuristics, not a proof.*
_PII = [
    (re.compile(r"[^\s@]+@[^\s@]+\.[a-z]{2,}", re.I), "email address"),
    (re.compile(r"(?:\+?\d[\s().-]?){7,}"), "phone-like number"),
    (re.compile(r"-?\d{1,3}\.\d{3,}\s*[, ]\s*-?\d{1,3}\.\d{3,}"), "precise coordinates"),
    (re.compile(r"\b\d{1,5}\s+\w+\s+(street|st|road|rd|avenue|ave|lane|ln|drive|dr)\b", re.I), "street address"),
]


def check_report(r):
    """List of problems; empty = acceptable. Required fields, enums, PII."""
    out = []
    if not isinstance(r, dict):
        return ["report is not an object"]
    if not str(r.get("junction_id") or "").strip():
        out.append("junction_id required")
    if r.get("outcome") not in OUTCOMES.values():
        out.append("outcome must be one of worked|partial|failed|UNSAFE")
    if r.get("scale") not in (None, "") and r.get("scale") not in SCALES.values():
        out.append("scale must be bench|small|full")
    if r.get("reporter_relation") not in (None, "") and r.get("reporter_relation") not in RELATIONS.values():
        out.append("reporter_relation must be hands-on|observed|secondhand")
    texts = [r.get(k) for k in ("failure_point", "as_built_vs_specified", "coarse_region")]
    texts += list((r.get("environment") or {}).values())
    for t in texts:
        if not isinstance(t, str):
            continue
        for rx, what in _PII:
            if rx.search(t):
                out.append("possible personal identifier (%s): remove it" % what)
    return sorted(set(out))


def normalize(r):
    """Drop empty values; keep only schema keys."""
    out = {}
    for k in ("junction_id", "junction_version", "outcome", "failure_point", "as_built_vs_specified",
              "scale", "time_to_outcome", "reporter_relation", "date", "coarse_region"):
        v = r.get(k)
        if v not in (None, ""):
            out[k] = v
    env = dict((k, v) for k, v in (r.get("environment") or {}).items() if k in ENV_KEYS and v not in (None, ""))
    if env:
        out["environment"] = env
    return out


def encode(r):
    probs = check_report(r)
    if probs:
        raise ReportError("; ".join(probs))
    env = r.get("environment") or {}
    vals = [
        r.get("junction_id"), r.get("junction_version"),
        _code(r.get("outcome"), OUTCOMES, "outcome"),
        r.get("failure_point"), r.get("as_built_vs_specified"),
        env.get("temp"), env.get("humidity"), env.get("climate"), env.get("soil_water"),
        _code(r.get("scale"), SCALES, "scale"),
        r.get("time_to_outcome"),
        _code(r.get("reporter_relation"), RELATIONS, "reporter_relation"),
        r.get("date"), r.get("coarse_region"),
    ]
    parts = [TAG] + [_esc(str(v)) if v not in (None, "") else "" for v in vals]
    while parts and parts[-1] == "":
        parts.pop()
    return "|".join(parts)


def decode(line):
    line = (line or "").strip()
    parts = line.split("|")
    if parts[0] != TAG:
        raise ReportError("line must start with %s|" % TAG)
    vals = [_unesc(p) for p in parts[1:]] + [""] * len(FIELDS)
    vals = vals[:len(FIELDS)]
    if len(parts) - 1 > len(FIELDS):
        raise ReportError("too many fields (%d > %d)" % (len(parts) - 1, len(FIELDS)))
    r = {"environment": {}}
    for name, v in zip(FIELDS, vals):
        if v == "":
            continue
        if name.startswith("env."):
            r["environment"][name[4:]] = v
        elif name == "outcome":
            r[name] = _word(v, OUTCOMES, "outcome")
        elif name == "scale":
            r[name] = _word(v, SCALES, "scale")
        elif name == "reporter_relation":
            r[name] = _word(v, RELATIONS, "reporter_relation")
        else:
            r[name] = v
    r = normalize(r)
    probs = check_report(r)
    if probs:
        raise ReportError("; ".join(probs))
    return r


def main(argv):
    if len(argv) == 2 and argv[0] == "encode":
        with open(argv[1], encoding="utf-8") as f:
            line = encode(json.load(f))
        print(line)
        if len(line) > MAX_LEN:
            sys.stderr.write("note: %d chars > %d; shorten failure_point or split\n" % (len(line), MAX_LEN))
        return 0
    if argv[:1] == ["template"]:
        print("|".join([TAG] + ["%d:%s" % (i + 1, f.replace("env.", "")) for i, f in enumerate(FIELDS)]))
        print("Count the pipes: a missed empty field shifts every field after it. "
              "Fields 1-4 (address, version, outcome, what happened) carry the warning; stop there if unsure.")
        return 0
    if len(argv) == 2 and argv[0] == "decode":
        print(json.dumps(decode(argv[1]), indent=2, ensure_ascii=False))
        return 0
    sys.stderr.write("usage: compact.py encode report.json | decode \"FR1|...\"\n")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except ReportError as e:
        sys.stderr.write("REJECTED: %s\n" % e)
        sys.exit(1)
