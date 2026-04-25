#!/usr/bin/env python3
"""
Mandala Field Link -- Bidirectional bridge between TAF and Mandala-Computing.

TAF (this repo) measures institutional accountability in energy units.
Mandala-Computing (github.com/JinnZ2/Mandala-Computing) solves hard
computational problems by encoding them as geometric energy landscapes
on octahedral 8-state cells, then relaxing to ground state via
simulated annealing, parallel tempering, holographic renormalization,
or quantum annealing.

Both frameworks are energy-grounded but at different layers:
    TAF:     institutional energy flows (joules of organism work)
    Mandala: optimization energy landscapes (cost-function ground states)

When TAF identifies a constrained-optimization problem (e.g. minimize
parasitic_energy_debt across stratification axes; find a coupling
configuration that maximizes governance.K subject to cascade-risk
bounds), the natural delegation path is:

    TAF problem -> Mandala energy-landscape encoding
                -> mandala_computer / mandala_simulator solver
                -> ground-state configuration
                -> back to TAF for thermodynamic interpretation

This fieldlink provides the translation layer + a loose-coupling
delegate that imports Mandala lazily so TAF stays runnable without
the external dependency.

Cross-reference map:
    Mandala concept                    <-> TAF concept
    energy landscape                   <-> distance_to_collapse manifold
    ground-state cost                  <-> minimum parasitic_energy_debt
    octahedral 8-state cell            <-> 8-dimensional knowledge polytensor
                                            (K_kinesthetic, K_temporal,
                                             K_relational, K_wisdom,
                                             K_skill, K_institutional,
                                             K_digital, K_intuitive)
    simulated-annealing schedule       <-> fatigue_score relaxation curve
    parallel tempering                 <-> federation cross-validation
    holographic renormalization        <-> coarse-grained policy from fine-
                                            grained physics
    solver convergence epsilon         <-> Q-factor stability tolerance

Sister-repo cross-references (Mandala README):
    Rosetta-Shape-Core, Geometric-to-Binary, Fractal-Compass-Atlas,
    Polyhedral-Intelligence, ai-human-audit-protocol.

Pinned upstream:
    https://github.com/JinnZ2/Mandala-Computing
    commit SHA: 1e2aa0da4072b2a6ed8dc5c28004418a2bfbec33

Dependencies: stdlib only (math). Does NOT import Mandala-Computing
at module top-level. Mandala is MIT-licensed; this bridge is CC0
(loose coupling preserves the license boundary).

License: CC0 1.0 Universal.
"""

from __future__ import annotations

import math
from typing import Any, Callable, Dict, Optional, Tuple


UPSTREAM = "github.com/JinnZ2/Mandala-Computing"
UPSTREAM_COMMIT_SHA = "1e2aa0da4072b2a6ed8dc5c28004418a2bfbec33"
UPSTREAM_LICENSE = "MIT"
UPSTREAM_ENTRY_POINTS = (
    "mandala_computer.py",   # classical engine
    "mandala_simulator.py",  # lightweight entry
    "quantum_mandala.py",    # quantum-annealing demo
    "holographic_mandala.py",  # holographic renormalization demo
    "examples/benchmark.py",   # benchmarking suite
)


# ============================================================
# Mandala -> TAF: solver outputs as physical state
# ============================================================

def ground_state_cost_to_collapse_distance(
    cost: float,
    cost_floor: float = 0.0,
    cost_ceiling: float = 1.0,
) -> float:
    """Convert a Mandala ground-state cost to TAF distance-to-collapse.

    Mandala returns a scalar cost C in [cost_floor, cost_ceiling].
    Lower cost = closer to ground state = healthier configuration.
    Maps linearly inverted onto TAF's distance_to_collapse (0-1,
    higher = safer).
    """
    if cost_ceiling <= cost_floor:
        return 1.0
    c = max(cost_floor, min(cost_ceiling, float(cost)))
    return round(1.0 - (c - cost_floor) / (cost_ceiling - cost_floor), 4)


def annealing_schedule_to_fatigue_curve(
    temperatures: Tuple[float, ...],
    e_input: float = 1.0,
) -> Tuple[float, ...]:
    """Convert a Mandala simulated-annealing temperature schedule
    to a TAF fatigue-score trajectory.

    High temperature in annealing = high exploration energy. TAF reads
    this as load above E_input (fatigue rising). The curve is the
    fatigue score the organism would experience while running the
    annealing schedule, normalized to TAF's 0-10 scale.
    """
    if not temperatures:
        return ()
    t_max = max(temperatures)
    if t_max <= 0:
        return tuple(0.0 for _ in temperatures)
    return tuple(round(10.0 * (t / t_max), 3) for t in temperatures)


def cell_state_count_to_hidden_count(
    n_cells: int,
    n_active_states: int,
    nominal_states_per_cell: int = 8,
) -> int:
    """Mandala uses octahedral 8-state cells. When fewer states are
    active in a configuration, more 'collapsed' state remains hidden.
    This converter estimates TAF's hidden_count from the cell-state
    structure of a Mandala solution.
    """
    if n_cells <= 0 or nominal_states_per_cell <= 0:
        return 0
    inactive = max(
        0,
        nominal_states_per_cell * n_cells - max(0, n_active_states),
    )
    # Saturating: 0..10 hidden_count
    return int(round(10.0 * (1.0 - math.exp(-0.001 * inactive))))


def solver_convergence_to_k_cred(
    final_residual: float,
    convergence_epsilon: float = 1e-6,
) -> float:
    """A solver that converged tightly (residual << epsilon) supports
    high credibility in its output. Maps log-distance from epsilon to
    TAF's K_cred in [0, 1].
    """
    if final_residual <= 0:
        return 1.0
    if convergence_epsilon <= 0:
        return 0.5
    ratio = final_residual / convergence_epsilon
    if ratio <= 1.0:
        return 1.0
    return round(max(0.0, min(1.0, 1.0 / (1.0 + math.log10(ratio)))), 4)


# ============================================================
# TAF -> Mandala: physical state as problem encoding
# ============================================================

def fatigue_score_to_initial_temperature(
    fatigue_score: float,
    t_min: float = 0.01,
    t_max: float = 10.0,
) -> float:
    """Higher TAF fatigue => higher initial annealing temperature
    (system is already in an excited state, needs more exploration to
    find a lower-energy configuration).
    """
    f = max(0.0, min(10.0, float(fatigue_score))) / 10.0
    return round(t_min + (t_max - t_min) * f, 3)


def cascade_level_to_solver_choice(cascade_level: str) -> str:
    """Pick a Mandala solver based on TAF cascade severity.

    MINIMAL/LOW -> classical simulated annealing (cheapest)
    MODERATE    -> parallel tempering (escape local minima)
    HIGH        -> holographic renormalization (cross-scale)
    CRITICAL    -> quantum annealing (broadest exploration)
    """
    return {
        "MINIMAL":  "simulated_annealing",
        "LOW":      "simulated_annealing",
        "MODERATE": "parallel_tempering",
        "HIGH":     "holographic_renormalization",
        "CRITICAL": "quantum_annealing",
    }.get(cascade_level.upper(), "simulated_annealing")


# ============================================================
# DELEGATE: try to outsource a hard problem to Mandala
# ============================================================

class MandalaUnavailable(RuntimeError):
    """Raised when Mandala-Computing is needed but not importable."""


def try_import_mandala() -> Optional[Any]:
    """Return Mandala's mandala_computer module if available, else None.

    Lazy: only attempts import when called, never at module top-level.
    Lets TAF declare the integration without taking a hard dependency.
    """
    try:
        import mandala_computer  # type: ignore
        return mandala_computer
    except ImportError:
        return None


def delegate_optimization(
    problem: Dict[str, Any],
    solver: str = "simulated_annealing",
    fallback: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Attempt to delegate an optimization problem to Mandala.

    Parameters
    ----------
    problem : dict
        Problem encoding -- shape is consumer-defined; passed
        through to Mandala's solver verbatim. Typical keys:
            "cells":          number of octahedral cells
            "interactions":   coupling matrix
            "constraints":    list of soft/hard constraints
    solver : str
        One of "simulated_annealing" / "parallel_tempering" /
        "holographic_renormalization" / "quantum_annealing". Use
        cascade_level_to_solver_choice() to pick from TAF state.
    fallback : callable, optional
        Called with `problem` when Mandala isn't installed. If None,
        raises MandalaUnavailable.

    Returns
    -------
    dict
        Mandala's solver output (or the fallback's output). Typical
        keys: "ground_state", "final_cost", "iterations",
        "convergence_residual".
    """
    mandala = try_import_mandala()
    if mandala is None:
        if fallback is not None:
            return fallback(problem)
        raise MandalaUnavailable(
            "Mandala-Computing is not installed. "
            "Install from https://github.com/JinnZ2/Mandala-Computing "
            "or supply a `fallback` callable to delegate_optimization()."
        )
    # Mandala API is research-grade (no declared SURFACE.md) -- we
    # invoke a permissive entry-point pattern. Adjust as upstream
    # surface stabilizes.
    if hasattr(mandala, "solve"):
        return mandala.solve(problem, solver=solver)
    if hasattr(mandala, "MandalaComputer"):
        engine = mandala.MandalaComputer()  # type: ignore
        return engine.solve(problem, solver=solver)
    raise MandalaUnavailable(
        "Mandala-Computing is installed but exposes neither a "
        "module-level `solve()` nor a `MandalaComputer` class. "
        "Upstream surface may have changed; check the pinned commit "
        f"{UPSTREAM_COMMIT_SHA} vs current main."
    )


# ============================================================
# COUPLED CROSS-VALIDATION
# ============================================================

class MandalaLink:
    """Bidirectional TAF <-> Mandala-Computing coupling.

    Usage:
        link = MandalaLink()
        link.ingest_mandala(ground_state_cost=0.12,
                            convergence_residual=1e-7,
                            n_cells=64, n_active_states=480)
        link.ingest_taf(fatigue_score=4.0, cascade_level="MODERATE")
        report = link.cross_validate()
    """

    def __init__(self) -> None:
        # Mandala side
        self.ground_state_cost: Optional[float] = None
        self.convergence_residual: Optional[float] = None
        self.n_cells: Optional[int] = None
        self.n_active_states: Optional[int] = None

        # TAF side
        self.fatigue_score: Optional[float] = None
        self.cascade_level: Optional[str] = None

    def ingest_mandala(self, *,
                       ground_state_cost: Optional[float] = None,
                       convergence_residual: Optional[float] = None,
                       n_cells: Optional[int] = None,
                       n_active_states: Optional[int] = None) -> None:
        self.ground_state_cost = ground_state_cost
        self.convergence_residual = convergence_residual
        self.n_cells = n_cells
        self.n_active_states = n_active_states

    def ingest_taf(self, *,
                   fatigue_score: Optional[float] = None,
                   cascade_level: Optional[str] = None) -> None:
        self.fatigue_score = fatigue_score
        self.cascade_level = cascade_level

    def cross_validate(self) -> Dict[str, Any]:
        report: Dict[str, Any] = {}

        # Mandala -> TAF
        if self.ground_state_cost is not None:
            report["derived_collapse_distance"] = (
                ground_state_cost_to_collapse_distance(self.ground_state_cost)
            )
        if (self.n_cells is not None and self.n_active_states is not None):
            report["derived_hidden_count"] = cell_state_count_to_hidden_count(
                self.n_cells, self.n_active_states
            )
        if self.convergence_residual is not None:
            report["derived_k_cred"] = solver_convergence_to_k_cred(
                self.convergence_residual
            )

        # TAF -> Mandala
        if self.fatigue_score is not None:
            report["expected_initial_temperature"] = (
                fatigue_score_to_initial_temperature(self.fatigue_score)
            )
        if self.cascade_level is not None:
            report["recommended_solver"] = (
                cascade_level_to_solver_choice(self.cascade_level)
            )

        return report


# ============================================================
# FIELD MAP (TAF <-> Mandala shared namespace)
# ============================================================

FIELD_MAP = {
    "distance_to_collapse":   ("ground_state_cost (inverted)",      "Mandala->TAF"),
    "hidden_count":           ("octahedral cell state usage",       "Mandala->TAF"),
    "K_cred":                 ("solver convergence_residual",       "Mandala->TAF"),
    "fatigue_curve":          ("annealing temperature schedule",    "Mandala->TAF"),
    "expected_temperature":   ("fatigue_score",                     "TAF->Mandala"),
    "recommended_solver":     ("cascade_level",                     "TAF->Mandala"),
    "delegate_optimization":  ("hard problem -> Mandala solver",    "TAF->Mandala"),
}


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  MANDALA <-> TAF FIELD LINK -- Demo")
    print("=" * 60)
    print(f"Upstream: {UPSTREAM}")
    print(f"Pinned commit: {UPSTREAM_COMMIT_SHA}")
    print(f"Upstream license: {UPSTREAM_LICENSE} "
          "(this fieldlink is CC0; loose coupling preserves the boundary)")
    print()

    link = MandalaLink()
    link.ingest_mandala(
        ground_state_cost=0.12,
        convergence_residual=5e-7,
        n_cells=64,
        n_active_states=480,
    )
    link.ingest_taf(fatigue_score=4.0, cascade_level="MODERATE")

    report = link.cross_validate()
    print("--- Mandala -> TAF derived ---")
    print(f"  derived_collapse_distance: "
          f"{report.get('derived_collapse_distance')}")
    print(f"  derived_hidden_count:      "
          f"{report.get('derived_hidden_count')}")
    print(f"  derived_k_cred:            "
          f"{report.get('derived_k_cred')}")
    print()
    print("--- TAF -> Mandala expected ---")
    print(f"  expected_initial_temperature: "
          f"{report.get('expected_initial_temperature')}")
    print(f"  recommended_solver:           "
          f"{report.get('recommended_solver')}")
    print()

    # Delegate demo (Mandala not installed in sandbox -> falls back)
    print("--- Delegate demo (no Mandala installed) ---")
    fallback_called = []

    def fb(problem):
        fallback_called.append(problem)
        return {"ground_state": None, "final_cost": float("inf"),
                "fallback_used": True}

    out = delegate_optimization({"cells": 8}, fallback=fb)
    print(f"  fallback_used: {out.get('fallback_used')}")
    print(f"  fallback called {len(fallback_called)} time(s)")

    try:
        delegate_optimization({"cells": 8})
    except MandalaUnavailable as e:
        print(f"  no fallback -> MandalaUnavailable: "
              f"{str(e).splitlines()[0]}")
