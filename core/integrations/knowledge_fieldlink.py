#!/usr/bin/env python3
"""
knowledge_fieldlink.py

Bridge between knowledge/ (scope-bounded study reframing)
and the main TAF audit pipeline.

Flow:

    knowledge.knowledge_liberation.liberate(StudyInput)
        -> result document
        -> knowledge_fieldlink.to_calibration_input()
        -> calibration.pipeline input
        -> calibration.pipeline.CalibrationReport

UPSTREAM SHAPE NOTE
-------------------
knowledge.knowledge_liberation.liberate() currently returns a
formatted str (a unified output document). The original task
spec referenced a `LiberationResult` dataclass that the
upstream does not yet expose. This fieldlink works against
what is actually importable today and accepts `Any` for the
result parameter; when knowledge/ adopts a structured return
type, switch the `result` parameter type to that dataclass
and walk its fields directly.

CALIBRATION-QUESTION MAPPING (design call)
------------------------------------------
The intended map (from the task spec; substantive design
call left for review) is:

    scope_map population_inversion warning   -> Q3 witness_dependence
    edge_explorer time_extension warning     -> Q4 memorialization
    edge_explorer scale_jump warning         -> Q4 memorialization
    edge_explorer mechanism_substitution     -> Q1 bite_source

The stubs below preserve those category names so the
implementer can fill in the walk against whatever upstream
shape ships.

Stdlib only. CC0.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# Resolve knowledge/ on sys.path so its flat-style imports
# (from scope_mapper import ...) work when this fieldlink is
# imported from elsewhere in the repo. Mirrors the pattern
# used by core/integrations/earth_physics_fieldlink.py for
# repo-root path resolution.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_KNOWLEDGE_DIR = os.path.join(_REPO_ROOT, "knowledge")
if _KNOWLEDGE_DIR not in sys.path:
    sys.path.insert(0, _KNOWLEDGE_DIR)

# Imports from knowledge/. Available today:
#   - liberate(study: StudyInput) -> str
#   - StudyInput dataclass
#   - ScopeMap, ScopeMapper
# Not yet available (per upstream-shape-note above):
#   - LiberationResult (returned today as formatted str)
try:
    from knowledge_liberation import liberate, StudyInput  # type: ignore[import-not-found]
    from scope_mapper import ScopeMap, ScopeMapper  # type: ignore[import-not-found]
    _KNOWLEDGE_AVAILABLE = True
except Exception:
    _KNOWLEDGE_AVAILABLE = False
    liberate = None  # type: ignore[assignment]
    StudyInput = None  # type: ignore[assignment]
    ScopeMap = None  # type: ignore[assignment]
    ScopeMapper = None  # type: ignore[assignment]


def knowledge_available() -> bool:
    """True iff knowledge/ modules are importable."""
    return _KNOWLEDGE_AVAILABLE


# ---------------------------------------------------------------
# OUTPUT SHAPE
# ---------------------------------------------------------------

@dataclass
class CalibrationLink:
    """Calibration-pipeline-ready payload derived from a
    knowledge/ liberation run."""
    study_id: str
    declared_scope: Dict[str, Any] = field(default_factory=dict)
    edge_warnings: List[str] = field(default_factory=list)
    legitimate_applications: List[str] = field(default_factory=list)
    misapplications: List[str] = field(default_factory=list)
    suggested_calibration_questions: List[str] = field(
        default_factory=list
    )


# ---------------------------------------------------------------
# BRIDGE FUNCTIONS (stubs; design call deferred to review)
# ---------------------------------------------------------------

def to_calibration_input(result: Any) -> CalibrationLink:
    """Convert a knowledge/ liberation result into the shape
    calibration/pipeline.py can ingest as a witness-dependence
    and scope-bound input.

    Implementation map (from task spec):

        scope_map population_inversion risk -> Q3 witness_dependence
        time_extension or scale_jump        -> Q4 memorialization
        mechanism_substitution              -> Q1 bite_source

    Today's blocker: knowledge.knowledge_liberation.liberate()
    returns formatted str rather than a structured dataclass.
    Implementer needs to either (a) parse the str sections or
    (b) wait for an upstream shape change and walk fields
    directly. The latter is cleaner; this stub holds the seat
    for it.
    """
    raise NotImplementedError(
        "Stub. Implementer: walk the liberation result and "
        "populate a CalibrationLink. See module docstring "
        "for the calibration-question map. Blocked on upstream "
        "structured return type; today's liberate() returns str."
    )


def liberation_to_simulation_seed(
    result: Any,
) -> Dict[str, Any]:
    """Convert a liberation result into a parameter dict that
    simulations/ runners can consume (e.g. as a witness-
    coefficient input or a scope-bound parameter override).

    Same upstream-shape blocker as to_calibration_input(). The
    primary candidate consumer is simulations/loop_6_ai_default_
    prior_distortion.py (the L6 default-prior-distortion sim) --
    its institutional_capture_mult and publication_visibility
    parameters are natural targets for liberation-derived
    overrides.
    """
    raise NotImplementedError(
        "Stub. Implementer: choose which sim consumes this "
        "first (loop_6, federation, lhri) and shape the seed."
    )


# ---------------------------------------------------------------
# DEMO
# ---------------------------------------------------------------

if __name__ == "__main__":
    print("knowledge_fieldlink: bridge stub. See module doc.")
    print(f"knowledge_available(): {knowledge_available()}")
    if knowledge_available():
        print("upstream knowledge/ modules imported cleanly:")
        print(f"  liberate:    {liberate.__module__}.liberate")
        print(f"  StudyInput:  {StudyInput.__module__}.StudyInput")
        print(f"  ScopeMap:    {ScopeMap.__module__}.ScopeMap")
        print(f"  ScopeMapper: {ScopeMapper.__module__}.ScopeMapper")
    else:
        print("knowledge/ modules NOT importable from this context")
