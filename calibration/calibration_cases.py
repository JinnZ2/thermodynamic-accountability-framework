"""
calibration_cases.py -- the existing system descriptions that reach the
calibration pipeline, extracted from the files that define them.

Each dict is read from its source by AST, and only its assignment is
executed; self_audit.py writes JSON files when imported, so it is not
imported. Sources: test_calibration.py (3), pipeline.py __main__ (1),
self_audit.py (2). Nothing here is a new measurement.

stdlib only. CC0.
"""

from __future__ import annotations

import ast
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _extract(path: str, name: str) -> dict:
    src = open(os.path.join(_HERE, path)).read()
    for node in ast.walk(ast.parse(src)):
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == name):
            ns: dict = {}
            exec(compile(ast.Module([node], []), path, "exec"), ns)
            return ns[name]
    raise KeyError(f"{name} not found in {path}")


def cases() -> list[tuple[str, str, dict]]:
    return [
        ("C1_sparse", "test_calibration.test_minimal_input_produces_valid_output",
         {"system_id": "sparse"}),
        ("C2_calibrated", "test_calibration.test_calibrated_system_scores_green",
         _extract("test_calibration.py", "calibrated_system")),
        ("C3_domesticated", "test_calibration (domesticated)",
         _extract("test_calibration.py", "domesticated")),
        ("C4_pipeline_main", "pipeline.__main__ test_system",
         _extract("pipeline.py", "test_system")),
        ("C5_self_optimistic", "self_audit.OPTIMISTIC",
         _extract("self_audit.py", "OPTIMISTIC")),
        ("C6_self_honest", "self_audit.HONEST",
         _extract("self_audit.py", "HONEST")),
        # Planted: one measured dimension, four missing. Expected answer
        # fixed in advance from calibration_audit.score_bite_source and
        # CalibrationReport.aggregate (0.6 mean + 0.4 worst).
        ("P1_one_dim_worst", "planted: bite_source 1.0, 4 missing",
         {"system_id": "p1",
          "feedback_events": [{"type": "personal", "count": 10}]}),
        ("P2_one_dim_best", "planted: bite_source 0.0, 4 missing",
         {"system_id": "p2",
          "feedback_events": [{"type": "impersonal", "count": 10}]}),
    ]
