"""
silent_fill_register.py -- register of places that write a value where
nothing was measured, and of constants with no stated source.

Kinds:
    SILENT_FILL         a missing or unmatched input is replaced by a
                        value that reads as a measurement
    UNSOURCED_CONSTANT  a number used in a calculation whose source is
                        not stated (or is borrowed from another quantity)

Each entry is resolved by quote at its line in the working tree;
--selftest fails if a quote no longer sits on its line. Status is OPEN
for every entry: the variants are recorded, none is picked.

Entries marked ordered=True were named in the 2026-11-11 work order;
ordered=False were found while doing it and are registered, not acted on.

stdlib only. CC0.
"""

from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))

# (id, kind, path relative to calibration/, line, quote, what, variants, ordered)
REGISTER = [
    ("SF01", "SILENT_FILL", "unified_audit.py", 368, '}.get(band, "YELLOW")',
     "pipeline unified_band is a Band.value (calibrating/drifting/mauling/"
     "memorialized_only); the map keys are GREEN/YELLOW/RED, so every band "
     "is unmatched and the fallback YELLOW is returned",
     "A unmatched -> GAP_INSTRUMENT coverage | B explicit mapping, PROPOSED "
     "| C current; see pipeline_band_experiment.py", True),

    ("SF02", "SILENT_FILL", "calibration_audit.py", 41, "score=0.5,",
     "bite_source: no feedback events -> 0.5",
     "A void | B assumed (PROPOSED table) | C baseline (current); "
     "see calibration_missing_experiment.py", True),
    ("SF03", "SILENT_FILL", "calibration_audit.py", 50,
     "score = personal / total if total else 0.5",
     "bite_source: events present but all counts zero -> 0.5",
     "not switched by the experiment (events exist; the counts are zero)", True),
    ("SF04", "SILENT_FILL", "calibration_audit.py", 81, "score=0.5,",
     "skin_in_game: no decisions -> 0.5",
     "A void | B assumed | C baseline", True),
    ("SF05", "SILENT_FILL", "calibration_audit.py", 121, "score=0.5,",
     "witness_dependence: no skills inventoried -> 0.5",
     "A void | B assumed | C baseline", True),
    ("SF06", "SILENT_FILL", "calibration_audit.py", 160, "score=0.0,",
     "memorialization_extinction: none flagged -> 0.0 (GREEN). Not a 0.5, "
     "but the same move: absence read as the best value",
     "A void | B assumed | C baseline", True),
    ("SF07", "SILENT_FILL", "calibration_audit.py", 216, "score=0.5,",
     "adaptation_debt (friction removal): no friction events -> 0.5",
     "A void | B assumed | C baseline", True),

    ("SF08", "SILENT_FILL", "schema.py", 94, "return 0.0, Band.GREEN",
     "CalibrationReport.aggregate with no scores -> 0.0 GREEN",
     "registered only", False),
    ("SF09", "SILENT_FILL", "observation_dependence.py", 68, "score=0.5,",
     "observation_dependence: no events -> 0.5 (same shape as SF02)",
     "registered only", False),
    ("SF10", "SILENT_FILL", "observation_dependence.py", 104, "score=0.5,",
     "observation_dependence: no events -> 0.5", "registered only", False),
    ("SF11", "SILENT_FILL", "observation_dependence.py", 141, "score=0.5,",
     "observation_dependence: no events -> 0.5", "registered only", False),
    ("SF12", "SILENT_FILL", "adaptation_debt.py", 92, "score=0.5,",
     "adaptation_debt: no friction events -> 0.5", "registered only", False),
    ("SF13", "SILENT_FILL", "adaptation_debt.py", 129, "score=0.5,",
     "adaptation_debt: no friction events -> 0.5", "registered only", False),

    ("UC01", "UNSOURCED_CONSTANT", "confidence_unknown_experiment.py", 27,
     "B_PENALTIES = (0.3, 0.8)",
     "variant B penalty values. Borrowed from assumption_validator: 0.3 is "
     "the YELLOW ceiling (assess(): 'penalty = 0.3 * progress', :89) and 0.8 "
     "the RED floor ('0.8 + 0.2 * excess', :95). Those are penalties for a "
     "measured out-of-range value; nothing states they apply to an absent one",
     "A/B/C kept open; a sourced penalty for 'no value' would replace these", True),
]


def resolve(entry) -> bool:
    _id, _k, path, line, quote, *_ = entry
    with open(os.path.join(_HERE, path)) as fh:
        lines = fh.read().splitlines()
    return 0 < line <= len(lines) and quote in lines[line - 1]


def render() -> str:
    out = ["| id | kind | file:line | what | variants | ordered |",
           "|---|---|---|---|---|---|"]
    for e in REGISTER:
        _id, kind, path, line, _q, what, variants, ordered = e
        out.append(f"| {_id} | {kind} | calibration/{path}:{line} | {what} | "
                   f"{variants} | {'yes' if ordered else 'found'} |")
    return "\n".join(out) + "\n"


def selftest() -> int:
    bad = [e[0] for e in REGISTER if not resolve(e)]
    ids = [e[0] for e in REGISTER]
    checks = len(REGISTER) + 1
    if len(set(ids)) != len(ids):
        bad.append("duplicate ids")
    print(f"checks: {checks}   failed: {len(bad)}")
    for b in bad:
        print("  FAIL", b)
    return 1 if bad else 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print(render())
