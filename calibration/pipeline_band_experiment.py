"""
pipeline_band_experiment.py -- how should unified_audit read the
pipeline's band?  An experiment; unified_audit.py is not changed.

unified_audit._run_legacy_pipeline maps unified_band through a table
keyed GREEN/YELLOW/RED, but the pipeline emits Band.value strings
(calibrating / drifting / mauling / memorialized_only). Nothing matches,
so the .get(band, "YELLOW") fallback fires on every run (SILENT_FILL SF01
in silent_fill_register.py). Three readings, none picked:

    A  unmatched band -> GAP_INSTRUMENT_UNRECOGNIZED_LABEL (coverage), no severity
    B  explicit mapping PROPOSED below (to be edited by Kavik)
    C  current behaviour (YELLOW for every band)

stdlib only. CC0.
"""

from __future__ import annotations

GAP_INSTRUMENT_UNRECOGNIZED_LABEL = "GAP_INSTRUMENT_UNRECOGNIZED_LABEL"

# Current map in unified_audit._run_legacy_pipeline.
CURRENT_MAP = {"GREEN": "GREEN", "green": "GREEN", "YELLOW": "YELLOW",
               "yellow": "YELLOW", "RED": "RED", "red": "RED"}

# PROPOSED -- one reading of schema.Band. memorialized_only (EXTINCT) is
# the worst band; mapping it to RED is a choice, not a derivation.
PROPOSED_MAP = {
    "calibrating": "GREEN",
    "drifting": "YELLOW",
    "mauling": "RED",
    "memorialized_only": "RED",
}


def status(band: str, variant: str) -> str:
    if variant == "A":
        return CURRENT_MAP.get(band, GAP_INSTRUMENT_UNRECOGNIZED_LABEL)
    if variant == "B":
        return PROPOSED_MAP.get(band, CURRENT_MAP.get(band, GAP_INSTRUMENT_UNRECOGNIZED_LABEL))
    return CURRENT_MAP.get(band, "YELLOW")


def rows():
    from calibration_cases import cases
    from pipeline import run_unified_audit
    from unified_audit import _run_legacy_pipeline
    out = []
    for cid, _src, desc in cases():
        rep = run_unified_audit(desc)
        band = rep["unified_band"]
        actual = _run_legacy_pipeline(desc)[0]
        out.append((cid, rep["unified_score"], band,
                    status(band, "A"), status(band, "B"), status(band, "C"),
                    actual))
    return out


def render() -> str:
    lines = ["| case | pipeline score | band | A | B (PROPOSED) | C (current) | unified_audit today |",
             "|---|---|---|---|---|---|---|"]
    for cid, sc, band, a, b, c, act in rows():
        s = "None" if sc is None else f"{sc:.4f}"
        lines.append(f"| {cid} | {s} | {band} | {a} | {b} | {c} | {act} |")
    return "\n".join(lines) + "\n"


def selftest() -> int:
    rs = rows()
    bad = [r[0] for r in rs if r[5] != r[6]]   # C must equal what runs today
    checks = len(rs) + 1
    if status("calibrating", "A") != GAP_INSTRUMENT_UNRECOGNIZED_LABEL:
        bad.append("A does not route unmatched to GAP_INSTRUMENT_UNRECOGNIZED_LABEL")
    print(f"checks: {checks}   failed: {len(bad)}")
    for b in bad:
        print("  FAIL C != current on", b)
    return 1 if bad else 0


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print(render())
