#!/usr/bin/env python3
"""
Earth-Systems-Physics Field Link -- bridge between TAF's metrology
framework checks and the upstream ``assumption_validator`` package.

TAF (this repo) audits whether published Earth-systems trends survive
two-layer (measurement x framework) corruption analysis. The 12
convergence checks in ``metrology/domain_convergence_matrix.py``
include framework-layer items (F1 stationarity, F2 baseline
selection, F4 human modification) that describe the failure mode but
do not actually verify the physical regime.

Earth-systems-physics (github.com/JinnZ2/earth-systems-physics)
maintains a 37-entry assumption registry that flags, in real time,
which physics equations are valid for the current state vs. which
have crossed regime boundaries (RiskLevel.RED).

This fieldlink translates between them:

    earth-physics -> TAF:  RiskLevel of relevant assumptions ->
                           framework-check anchor
    TAF -> earth-physics:  framework-check IDs -> set of relevant
                           upstream assumption_keys

Stable input shape (contract): see ``schemas/earth_physics_contract.py``.
Pinned upstream commit: 341a14b6e1706f16bea6a909d496bde4c8060109.

The link is loose-coupled. It will use the live upstream
``assumption_validator`` package if importable; otherwise it falls
back to ``UNKNOWN`` verdicts so TAF stays runnable in isolation.

Dependencies: stdlib only.
License: CC0 (matches both repos).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Resolve the contract from TAF's schemas/ directory. Add repo root to
# sys.path if running this module directly (matches the convention
# used by the other *_fieldlink.py modules).
_HERE = __file__
try:
    from schemas.earth_physics_contract import (
        ASSUMPTION_KEYS,
        COUPLING_GRAPH,
        CONTRACT_VERSION,
        UPSTREAM_COMMIT_SHA,
        validate_layer_states_shape,
        known_assumption,
    )
except ImportError:
    import os
    _ROOT = os.path.abspath(os.path.join(os.path.dirname(_HERE), "..", ".."))
    if _ROOT not in sys.path:
        sys.path.insert(0, _ROOT)
    from schemas.earth_physics_contract import (  # type: ignore[no-redef]
        ASSUMPTION_KEYS,
        COUPLING_GRAPH,
        CONTRACT_VERSION,
        UPSTREAM_COMMIT_SHA,
        validate_layer_states_shape,
        known_assumption,
    )


# ---------------------------------------------------------------
# UPSTREAM AVAILABILITY
# ---------------------------------------------------------------

_UPSTREAM_AVAILABLE = False
_upstream_full_report = None  # type: ignore[assignment]
try:
    # Live upstream import. If earth-systems-physics is on sys.path
    # and its (numpy + flask) deps are satisfied, this will succeed
    # and the fieldlink will delegate real work to it.
    from assumption_validator import full_report as _upstream_full_report  # type: ignore[import-not-found]
    _UPSTREAM_AVAILABLE = True
except Exception:
    # Any import failure (missing package, missing numpy, etc.)
    # -> we operate in stub mode.
    _UPSTREAM_AVAILABLE = False


def upstream_available() -> bool:
    """True iff the live ``assumption_validator`` package is importable."""
    return _UPSTREAM_AVAILABLE


# ---------------------------------------------------------------
# TAF FRAMEWORK-CHECK -> UPSTREAM ASSUMPTION KEYS
# ---------------------------------------------------------------

# Maps each TAF framework-layer check from
# metrology/domain_convergence_matrix.py to the upstream
# assumption_validator keys whose RiskLevel anchors that check.
#
# F1 stationarity: the equations assume Holocene-typical regime;
#   any of these in RED means the regime has shifted.
# F2 baseline selection: anomalous-baseline detection requires
#   knowing whether the chosen baseline period itself sits inside
#   a now-shifted regime.
# F4 human modification: anthropogenic forcing turning a baseline
#   non-natural; bio_* + atmo_ghg_forcing are the relevant flags.
#
# F3 (count-as-trend), F5 (indigenous baseline excluded),
# F6 (linearity), F7 (uncertainty propagation) are not physics
# anchored -- they are methodological / epistemic, so the upstream
# validator does not speak to them. Listed as empty for completeness.
FRAMEWORK_CHECK_ANCHORS: Dict[str, List[str]] = {
    "F1_stationarity": [
        "atmo_jet_shear",
        "atmo_hadley_extent",
        "hydro_AMOC_collapse",
        "hydro_AMOC_transport",
        "hydro_arctic_amplification",
        "hydro_committed_warming",
        "bio_amazon_tipping",
        "bio_NEP_sink",
    ],
    "F2_baseline_selection": [
        "atmo_ghg_forcing",
        "atmo_net_forcing",
        "hydro_ice_albedo",
        "hydro_committed_warming",
    ],
    "F3_count_as_trend": [],
    "F4_human_modification": [
        "atmo_ghg_forcing",
        "bio_permafrost_flux",
        "bio_permafrost_CH4",
        "bio_co2_accumulation",
        "bio_planetary_boundaries",
        "bio_ocean_pH",
    ],
    "F5_indigenous_baseline": [],
    "F6_linearity": [],
    "F7_uncertainty_propagation": [],
}


# ---------------------------------------------------------------
# RESULT SHAPE
# ---------------------------------------------------------------

@dataclass
class PhysicsAnchor:
    """Result of anchoring a TAF framework check to upstream physics.

    verdict:
        "RED"     at least one anchored assumption is past its
                  red_threshold; the framework check fails physics
                  -- the cited regime is not the current regime.
        "YELLOW"  at least one anchored assumption is in transition.
        "GREEN"   all anchored assumptions stable in their envelope.
        "UNKNOWN" upstream package unavailable OR no anchors mapped
                  for this check (F3/F5/F6/F7 are intrinsically
                  UNKNOWN here and must be answered by the
                  measurement / methodology layer instead).
    """
    check_id: str
    verdict: str
    anchored_keys: List[str]
    red_keys: List[str] = field(default_factory=list)
    yellow_keys: List[str] = field(default_factory=list)
    green_keys: List[str] = field(default_factory=list)
    upstream_available: bool = False
    notes: str = ""


# ---------------------------------------------------------------
# CORE BRIDGE
# ---------------------------------------------------------------

def physics_anchor_for_check(
    check_id: str,
    layer_states: Optional[Dict[int, Dict]] = None,
) -> PhysicsAnchor:
    """Anchor one TAF framework check to upstream physics.

    Parameters
    ----------
    check_id : str
        One of the F1..F7 IDs from
        metrology/domain_convergence_matrix.py.
    layer_states : optional
        Output dict from upstream cascade_engine.run_all_layers().
        If None or upstream unavailable, returns verdict="UNKNOWN".

    Returns
    -------
    PhysicsAnchor with verdict, broken-down anchored keys, and a
    note explaining the result.
    """
    anchors = FRAMEWORK_CHECK_ANCHORS.get(check_id, [])

    if not anchors:
        return PhysicsAnchor(
            check_id=check_id,
            verdict="UNKNOWN",
            anchored_keys=[],
            upstream_available=_UPSTREAM_AVAILABLE,
            notes=(
                f"{check_id} is not physics-anchored; "
                f"answer at measurement/methodology layer"
            ),
        )

    if not _UPSTREAM_AVAILABLE or layer_states is None:
        return PhysicsAnchor(
            check_id=check_id,
            verdict="UNKNOWN",
            anchored_keys=anchors,
            upstream_available=_UPSTREAM_AVAILABLE,
            notes=(
                "upstream assumption_validator unavailable"
                if not _UPSTREAM_AVAILABLE
                else "no layer_states provided"
            ),
        )

    shape_errs = validate_layer_states_shape(layer_states)
    if shape_errs:
        return PhysicsAnchor(
            check_id=check_id,
            verdict="UNKNOWN",
            anchored_keys=anchors,
            upstream_available=True,
            notes=f"layer_states shape errors: {shape_errs}",
        )

    report = _upstream_full_report(layer_states)  # type: ignore[misc]
    assessments = report.get("assessments", report) if isinstance(report, dict) else {}

    red, yellow, green = [], [], []
    for k in anchors:
        a = assessments.get(k)
        if not isinstance(a, dict):
            continue
        status = str(a.get("status", a.get("risk", "UNKNOWN"))).upper()
        if status == "RED":
            red.append(k)
        elif status == "YELLOW":
            yellow.append(k)
        elif status == "GREEN":
            green.append(k)

    if red:
        verdict = "RED"
    elif yellow:
        verdict = "YELLOW"
    elif green:
        verdict = "GREEN"
    else:
        verdict = "UNKNOWN"

    return PhysicsAnchor(
        check_id=check_id,
        verdict=verdict,
        anchored_keys=anchors,
        red_keys=red,
        yellow_keys=yellow,
        green_keys=green,
        upstream_available=True,
        notes=f"anchored {len(anchors)} assumption(s) via upstream full_report()",
    )


def anchor_all_framework_checks(
    layer_states: Optional[Dict[int, Dict]] = None,
) -> Dict[str, PhysicsAnchor]:
    """Run every F1..F7 anchor in one call. Returns dict keyed by check_id."""
    return {
        check_id: physics_anchor_for_check(check_id, layer_states)
        for check_id in FRAMEWORK_CHECK_ANCHORS
    }


# ---------------------------------------------------------------
# COUPLING GRAPH HELPERS
# ---------------------------------------------------------------

def downstream_of(assumption_key: str) -> List[str]:
    """Direct downstream couplings for a single assumption.

    Returns the list of assumption keys (or downstream observables)
    whose validity is in question when ``assumption_key`` degrades.
    """
    return list(COUPLING_GRAPH.get(assumption_key, []))


def cascade_neighborhood(assumption_key: str, depth: int = 2) -> List[str]:
    """Breadth-first walk of the coupling graph from ``assumption_key``.

    depth=2 means: direct downstream + their direct downstream.
    Avoids cycles. Returns flat ordered list of unique keys
    (excluding the seed itself).
    """
    seen = {assumption_key}
    frontier = [assumption_key]
    out: List[str] = []
    for _ in range(max(depth, 0)):
        next_frontier: List[str] = []
        for k in frontier:
            for d in COUPLING_GRAPH.get(k, []):
                if d not in seen:
                    seen.add(d)
                    out.append(d)
                    next_frontier.append(d)
        frontier = next_frontier
    return out


# ---------------------------------------------------------------
# DEMO / SELF-TEST
# ---------------------------------------------------------------

def _demo() -> None:
    print(f"earth_physics_fieldlink CONTRACT_VERSION={CONTRACT_VERSION}")
    print(f"upstream pinned to commit={UPSTREAM_COMMIT_SHA[:12]}")
    print(f"upstream live import available: {upstream_available()}")
    print()

    print("Framework-check anchors (TAF F-check -> upstream assumption keys):")
    for check_id, keys in FRAMEWORK_CHECK_ANCHORS.items():
        if keys:
            print(f"  {check_id}: {len(keys)} anchor(s)")
            for k in keys:
                ok = "OK" if known_assumption(k) else "MISSING"
                print(f"    [{ok}] {k}")
        else:
            print(f"  {check_id}: not physics-anchored")
    print()

    print("Stub run (no layer_states; upstream may be unavailable):")
    anchors = anchor_all_framework_checks(layer_states=None)
    for check_id, a in anchors.items():
        print(f"  {check_id}: verdict={a.verdict}; {a.notes}")
    print()

    print("Coupling-graph cascade neighborhood example:")
    seed = "atmo_jet_shear"
    print(f"  seed: {seed}")
    print(f"  depth-1: {downstream_of(seed)}")
    print(f"  depth-2: {cascade_neighborhood(seed, depth=2)}")


if __name__ == "__main__":
    _demo()
