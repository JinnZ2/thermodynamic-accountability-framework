"""
confidence_unknown_experiment.py -- how should UNKNOWN enter the
confidence multiplier?  An experiment; it changes no default.

assumption_validator.global_confidence_multiplier multiplies (1 - penalty)
over assumptions. An UNKNOWN assumption carries no confidence_penalty, so
today it counts as fully confident. Three readings, none picked:

    A  no penalty (current behaviour)
    B  fixed penalty p per UNKNOWN assumption. p is a free parameter;
       reported at two values anchored in the registry's own scale:
       0.3 (the YELLOW ceiling, assess(): 0.3 * progress) and
       0.8 (the RED floor, assess(): 0.8 + 0.2 * excess)
    C  multiplier = NOT_DETERMINABLE when any assumption is UNKNOWN

INFO assumptions (non-numeric value) get no penalty in all three; they
are on the coverage axis in unified_audit, not in this experiment.

stdlib only. CC0.
"""

from __future__ import annotations

import contextlib
import io

B_PENALTIES = (0.3, 0.8)
NOT_DETERMINABLE = "NOT_DETERMINABLE"


def multiplier(assessments: dict, variant: str, p: float = 0.0):
    """Confidence multiplier under one variant. A reproduces upstream."""
    if variant == "C" and any(a.get("status") == "UNKNOWN"
                              for a in assessments.values()):
        return NOT_DETERMINABLE
    m = 1.0
    for a in assessments.values():
        if a.get("status") == "UNKNOWN":
            pen = p if variant == "B" else 0.0
        else:
            pen = a.get("confidence_penalty", 0.0)
            if not isinstance(pen, (int, float)):
                pen = 0.0
        m *= (1.0 - pen)
    return max(0.0, m)


def rows():
    """[(case_id, n_unknown, n_total, A, B@0.3, B@0.8, C, upstream)]."""
    from unified_audit import run_full_audit
    from unknown_axis_cases import CASES, PLANTED
    cases = [(c, k) for c, _s, k in CASES] + [(c, k) for c, _s, k, _e in PLANTED]
    out = []
    for cid, kw in cases:
        with contextlib.redirect_stdout(io.StringIO()):
            r = run_full_audit(system_id=cid, **kw)
        av = r.sections.get("assumption_validator")
        if not isinstance(av, dict) or "assumptions" not in av:
            continue
        asm = av["assumptions"]
        n_unk = sum(1 for a in asm.values() if a.get("status") == "UNKNOWN")
        out.append((cid, n_unk, len(asm),
                    multiplier(asm, "A"),
                    *[multiplier(asm, "B", p) for p in B_PENALTIES],
                    multiplier(asm, "C"),
                    av.get("global_confidence_multiplier")))
    return out


def _fmt(v):
    return v if isinstance(v, str) else f"{v:.4f}"


def render() -> str:
    head = ("| case | UNKNOWN / total | A (none) | "
            + " | ".join(f"B (p={p})" for p in B_PENALTIES)
            + " | C | upstream value |")
    lines = [head, "|" + "---|" * (5 + len(B_PENALTIES))]
    for cid, nu, nt, a, *rest in rows():
        *bs, c, up = rest
        lines.append(f"| {cid} | {nu} / {nt} | {_fmt(a)} | "
                     + " | ".join(_fmt(b) for b in bs)
                     + f" | {_fmt(c)} | {_fmt(up)} |")
    return "\n".join(lines) + "\n"


def selftest() -> int:
    asm = {"x": {"status": "GREEN", "confidence_penalty": 0.0},
           "y": {"status": "YELLOW", "confidence_penalty": 0.2},
           "z": {"status": "UNKNOWN"}}
    checks = [
        (abs(multiplier(asm, "A") - 0.8) < 1e-12, "A ignores UNKNOWN"),
        (abs(multiplier(asm, "B", 0.5) - 0.4) < 1e-12, "B applies p"),
        (multiplier(asm, "C") == NOT_DETERMINABLE, "C refuses on any UNKNOWN"),
        (multiplier({"x": asm["x"]}, "C") == 1.0, "C measures when none UNKNOWN"),
    ]
    for r in rows():
        checks.append((abs(r[3] - r[-1]) < 1e-12, f"A == upstream on {r[0]}"))
    bad = [m for ok, m in checks if not ok]
    print(f"checks: {len(checks)}   failed: {len(bad)}")
    for m in bad:
        print("  FAIL", m)
    return 1 if bad else 0


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print(render())
