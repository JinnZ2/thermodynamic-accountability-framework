"""
Geometric-Bridge Contract -- stable surface of the Geometric-to-Binary
Computational Bridge that TAF's taf_bridge.py and taf_alternative_
compute.py depend on.

The upstream repo (github.com/JinnZ2/Geometric-to-Binary-Computational-
Bridge) ships the canonical implementation of sensor decoding, actuator
routing, hardware data shapes, and Gray-code conversion. It does NOT
yet publish a SURFACE.md or SCHEMA_VERSION, so this contract is pinned
against a specific commit SHA (same pattern as metabolic-accounting).

Unlike contracts for pure-data repos (trust-exit, metabolic-accounting,
Logic-Ferret), this one provides WORKING fallback implementations.
Reason: TAF's taf_bridge.py calls these symbols in method bodies; if
the upstream isn't installed, silent-None stubs would crash at first
use. The fallback here lets TAF audit its own energy-accounting and
admissibility-field math end-to-end without an external dependency.
When the upstream IS installed, TAF prefers it (see the guarded
`try: from geometric_bridge import ...` blocks in taf_bridge.py).

UPSTREAM PIN
------------
    geometric_bridge_ref:         https://github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge
    geometric_bridge_commit_sha:  ba1a5251be7d39bcef865e47e7dd8c513d0044ed

When upstream publishes a SURFACE.md or tag scheme, migrate from the
commit-SHA pin to a tag pin (same migration path as
metabolic-accounting will take).

CONTRACT_VERSION 0.1.0 reflects upstream's pre-release status (no
published SURFACE.md, rapid development cadence, 500+ commits).

License: CC0 1.0 Universal.
Dependencies: stdlib only (dataclasses, enum, typing).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Dict, List, Optional, Protocol, Tuple


CONTRACT_VERSION = "0.1.0"
UPSTREAM = "github.com/JinnZ2/Geometric-to-Binary-Computational-Bridge"
UPSTREAM_COMMIT_SHA = "ba1a5251be7d39bcef865e47e7dd8c513d0044ed"


# ---------------------------------------------------------------
# ENUMS (canonical, fixed)
# ---------------------------------------------------------------

class DrillDepth(Enum):
    """Escalation depth for sensor-derived alerts.

    Values mirror upstream conventions. Ordering reflects escalation
    severity: PASS < MONITOR < ALERT < QUARANTINE.
    """
    PASS = "pass"
    MONITOR = "monitor"
    ALERT = "alert"
    QUARANTINE = "quarantine"


class BridgeTarget(Enum):
    """Actuator-routing categories for thermal/physical control."""
    THERMAL = "thermal"
    PRESSURE = "pressure"
    ELECTRICAL = "electrical"
    MECHANICAL = "mechanical"


# ---------------------------------------------------------------
# HARDWARE DATA SHAPE
# ---------------------------------------------------------------

@dataclass(frozen=True)
class HardwareData:
    """One snapshot of sensor readings from an instrumented system.

    Fields are normalized to [0.0, 1.0] unless a physical unit is
    explicitly named. Consumers should treat absent values as None
    rather than inferring defaults.
    """
    health_score: Optional[float] = None         # 0-1, higher is healthier
    temperature_c: Optional[float] = None        # degrees Celsius
    noise_level: Optional[float] = None          # 0-1 normalized
    drift_rate: Optional[float] = None           # 0-1 normalized
    voltage_v: Optional[float] = None            # volts
    current_a: Optional[float] = None            # amperes
    lifetime_fraction: Optional[float] = None    # 0-1, consumed-life fraction
    timestamp: Optional[str] = None              # ISO-8601 if provided
    source_id: str = ""                          # device / sensor identifier
    extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "HardwareData":
        known = {"health_score", "temperature_c", "noise_level", "drift_rate",
                 "voltage_v", "current_a", "lifetime_fraction",
                 "timestamp", "source_id"}
        extra = {k: v for k, v in d.items() if k not in known}
        return cls(
            health_score=d.get("health_score"),
            temperature_c=d.get("temperature_c"),
            noise_level=d.get("noise_level"),
            drift_rate=d.get("drift_rate"),
            voltage_v=d.get("voltage_v"),
            current_a=d.get("current_a"),
            lifetime_fraction=d.get("lifetime_fraction"),
            timestamp=d.get("timestamp"),
            source_id=str(d.get("source_id", "")),
            extra=extra,
        )


# ---------------------------------------------------------------
# QUANTIZATION BANDS (functional stdlib defaults)
# ---------------------------------------------------------------
# When upstream is not installed, taf_bridge / taf_alternative_compute
# fall back to these values. They match the normalized 0-1 convention
# used by HardwareData. When the upstream IS installed, its real bands
# (which may differ numerically) win.

HEALTH_BANDS: Tuple[float, ...]    = (0.00, 0.25, 0.50, 0.75, 1.00)
TEMP_BANDS: Tuple[float, ...]      = (0.00, 0.25, 0.50, 0.75, 1.00)
NOISE_BANDS: Tuple[float, ...]     = (0.00, 0.25, 0.50, 0.75, 1.00)
DRIFT_BANDS: Tuple[float, ...]     = (0.00, 0.01, 0.05, 0.10, 0.50)
LIFETIME_BANDS: Tuple[float, ...]  = (0.00, 0.25, 0.50, 0.75, 1.00)
VOLTAGE_BANDS: Tuple[float, ...]   = (0.00, 0.25, 0.50, 0.75, 1.00)
CURRENT_BANDS: Tuple[float, ...]   = (0.00, 0.25, 0.50, 0.75, 1.00)


# ---------------------------------------------------------------
# GRAY CODE CONVERSION (deterministic stdlib implementation)
# ---------------------------------------------------------------
# Gray code is a well-defined binary encoding; the math is
# deterministic regardless of upstream. These functions match
# upstream's behavior by construction.

def gray_to_binary(gray: int) -> int:
    """Convert a Gray-code integer to its binary equivalent.

    Standard algorithm: XOR all bits from MSB toward LSB.
    Example: gray_to_binary(0b1011) -> 0b1101 (13)
    """
    if gray < 0:
        raise ValueError("Gray codes are non-negative integers")
    binary = gray
    g = gray
    while g > 0:
        g >>= 1
        binary ^= g
    return binary


def gray_to_value(gray: int, bands: Tuple[float, ...]) -> float:
    """Quantize a Gray-coded sensor reading to a band value.

    Converts the Gray code to a binary index, then returns
    bands[index]. Index is clamped into [0, len(bands)-1].
    """
    if not bands:
        raise ValueError("bands tuple must not be empty")
    index = gray_to_binary(gray)
    index = max(0, min(len(bands) - 1, index))
    return bands[index]


# ---------------------------------------------------------------
# PROTOCOLS (upstream class surfaces, for consumer type hints)
# ---------------------------------------------------------------

class SensorDecoderProtocol(Protocol):
    """Structural type for upstream's SensorDecoder class.

    A SensorDecoder consumes raw HardwareData and produces a
    DrillDepth routing decision plus any per-sensor annotations.
    Upstream's concrete class is interchangeable with any object
    implementing this protocol.
    """
    def decode(self, hardware: HardwareData) -> Dict[str, Any]: ...
    def drill_depth(self, hardware: HardwareData) -> DrillDepth: ...


class ActuatorControllerProtocol(Protocol):
    """Structural type for upstream's ActuatorController class."""
    def route(self, target: BridgeTarget, command: Dict[str, Any]) -> bool: ...


# ---------------------------------------------------------------
# MINIMAL FALLBACK IMPLEMENTATIONS
# ---------------------------------------------------------------
# Conservative implementations used when the upstream package is not
# installed. Enough to keep TAF's taf_bridge.py functional end-to-end
# on TAF-only deployments.

class FallbackSensorDecoder:
    """Minimal SensorDecoder: drills based on health_score bands."""

    def decode(self, hardware: HardwareData) -> Dict[str, Any]:
        return {
            "health_score": hardware.health_score,
            "temperature_c": hardware.temperature_c,
            "noise_level": hardware.noise_level,
            "drift_rate": hardware.drift_rate,
            "drill_depth": self.drill_depth(hardware).value,
        }

    def drill_depth(self, hardware: HardwareData) -> DrillDepth:
        h = hardware.health_score if hardware.health_score is not None else 1.0
        if h >= HEALTH_BANDS[-2]:
            return DrillDepth.PASS
        if h >= HEALTH_BANDS[-3]:
            return DrillDepth.MONITOR
        if h >= HEALTH_BANDS[1]:
            return DrillDepth.ALERT
        return DrillDepth.QUARANTINE


class FallbackActuatorController:
    """Minimal ActuatorController: records but does not actuate."""

    def __init__(self) -> None:
        self.routed: List[Tuple[BridgeTarget, Dict[str, Any]]] = []

    def route(self, target: BridgeTarget, command: Dict[str, Any]) -> bool:
        self.routed.append((target, dict(command)))
        return True


# Aliases so taf_bridge / taf_alternative_compute can fall back to
# these by importing the names the upstream ships.
SensorDecoder = FallbackSensorDecoder
ActuatorController = FallbackActuatorController


# ---------------------------------------------------------------
# RUNTIME SURFACE VALIDATION
# ---------------------------------------------------------------

@dataclass(frozen=True)
class SurfaceCheckResult:
    compatible: bool
    missing_symbols: Tuple[str, ...] = ()
    notes: str = ""


REQUIRED_SYMBOLS = (
    "SensorDecoder", "ActuatorController",
    "HardwareData", "DrillDepth", "BridgeTarget",
    "HEALTH_BANDS", "TEMP_BANDS", "NOISE_BANDS", "DRIFT_BANDS",
    "gray_to_value", "gray_to_binary",
)


def validate_upstream_surface(namespace: Dict[str, Any]) -> SurfaceCheckResult:
    """Check whether a namespace (e.g. an imported geometric_bridge
    module's __dict__) provides the symbols TAF depends on.

    Upstream doesn't publish a SURFACE.md yet, so this check is
    permissive: it verifies that each REQUIRED_SYMBOLS name exists.
    Value/type compatibility is caller-dependent and tested by TAF's
    unit tests, not by this validator.
    """
    missing = tuple(s for s in REQUIRED_SYMBOLS if s not in namespace)
    if missing:
        return SurfaceCheckResult(
            compatible=False,
            missing_symbols=missing,
            notes=f"Upstream is missing: {list(missing)}",
        )
    return SurfaceCheckResult(
        compatible=True,
        notes="All required symbols present.",
    )


# ---------------------------------------------------------------
# BRIDGE CONTRACT MANIFEST ACCESSORS
# ---------------------------------------------------------------
# Mirror of upstream's cross_repo_bridge_contract.py. Loads either
# the live upstream's bridge_contract_manifest.json (when the package
# is installed) or our local mirror at
# schemas/bridge_contract_manifest.json. Provides the same accessor
# surface declared by upstream's __all__:
#     load_bridge_contract, list_bridge_domains, get_bridge_domain,
#     get_solver_name, get_top_level_encoder, get_silicon_entry_point,
#     list_hardware_modules, get_hardware_module
#
# This is the 18-domain registry through which TAF can dispatch to
# alternative-compute paradigms (sound, electric, gravity, magnetic,
# light, pressure, thermal, wave, chemical, community, resilience,
# biomachine, coop, cyclic, vortex, geometric_fiber, consciousness,
# emotion). Each domain carries a silicon_entry_point string that
# names the upstream class to import for hardware-aware dispatch.

import json as _json
import functools as _functools
import pathlib as _pathlib

_MIRROR_MANIFEST_PATH = (
    _pathlib.Path(__file__).resolve().parent / "bridge_contract_manifest.json"
)


@_functools.lru_cache(maxsize=1)
def load_bridge_contract() -> Dict[str, Any]:
    """Load the bridge contract manifest.

    Resolution order:
      1. The live upstream package's manifest, if importable
         (`from cross_repo_bridge_contract import load_bridge_contract`)
      2. TAF's local mirror at schemas/bridge_contract_manifest.json

    The two are kept in lockstep by surface_staleness_check.py. The
    upstream commit SHA pinned in this contract (UPSTREAM_COMMIT_SHA)
    is the version of the manifest the local mirror tracks.
    """
    try:
        from cross_repo_bridge_contract import (  # type: ignore
            load_bridge_contract as _upstream_loader,
        )
        return _upstream_loader()
    except ImportError:
        return _json.loads(_MIRROR_MANIFEST_PATH.read_text())


def _bridge_index() -> Dict[str, Dict[str, Any]]:
    return {entry["name"]: entry
            for entry in load_bridge_contract()["bridge_domains"]}


def _hardware_index() -> Dict[str, Dict[str, Any]]:
    return {entry["name"]: entry
            for entry in load_bridge_contract()["hardware_module_catalog"]}


def list_bridge_domains() -> List[str]:
    """Return bridge domain names in canonical contract order."""
    return [entry["name"]
            for entry in load_bridge_contract()["bridge_domains"]]


def get_bridge_domain(name: str) -> Dict[str, Any]:
    """Return manifest metadata for one bridge domain."""
    key = name.strip().lower()
    idx = _bridge_index()
    if key not in idx:
        available = ", ".join(sorted(idx))
        raise KeyError(
            f"Unknown bridge domain '{name}'. Available domains: {available}"
        )
    return idx[key]


def get_solver_name(name: str) -> str:
    """Return the canonical registry solver name for a bridge domain."""
    return get_bridge_domain(name)["solver_name"]


def get_top_level_encoder(name: str) -> str:
    """Return the canonical top-level encoder import path."""
    return get_bridge_domain(name)["top_level_encoder"]


def get_silicon_entry_point(name: str) -> str:
    """Return the canonical silicon-side entry point import path.

    This is the alternative-compute dispatch entry: the import path
    a consumer would use to instantiate the hardware-aware encoder
    for a given bridge domain. TAF's taf_alternative_compute.py can
    use this to delegate to the upstream's silicon adapters when
    available.
    """
    return get_bridge_domain(name)["silicon_entry_point"]


def list_hardware_modules() -> List[str]:
    """Return hardware-module names in canonical contract order."""
    return [entry["name"]
            for entry in load_bridge_contract()["hardware_module_catalog"]]


def get_hardware_module(name: str) -> Dict[str, Any]:
    """Return manifest metadata for one hardware-side module."""
    key = name.strip().lower()
    idx = _hardware_index()
    if key not in idx:
        available = ", ".join(sorted(idx))
        raise KeyError(
            f"Unknown hardware module '{name}'. Available modules: {available}"
        )
    return idx[key]


# ---------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------

if __name__ == "__main__":
    print(f"Contract mirror version:  {CONTRACT_VERSION}")
    print(f"Upstream:                 {UPSTREAM}")
    print(f"Upstream commit SHA:      {UPSTREAM_COMMIT_SHA}")
    print(f"Required symbols:         {len(REQUIRED_SYMBOLS)}")
    print()

    # Gray code round-trip
    for g in (0, 1, 2, 3, 4, 5, 15, 255):
        print(f"  gray {g:3d} -> binary {gray_to_binary(g):3d}")

    # Band lookup
    v = gray_to_value(0b11, HEALTH_BANDS)  # gray 3 -> binary 2 -> HEALTH_BANDS[2]
    print(f"  gray_to_value(0b11, HEALTH_BANDS) = {v}")
    assert v == HEALTH_BANDS[2]

    # Fallback SensorDecoder
    dec = SensorDecoder()
    hw_healthy = HardwareData(health_score=0.95)
    hw_failing = HardwareData(health_score=0.05)
    print(f"  healthy -> {dec.drill_depth(hw_healthy)}")
    print(f"  failing -> {dec.drill_depth(hw_failing)}")
    assert dec.drill_depth(hw_healthy) == DrillDepth.PASS
    assert dec.drill_depth(hw_failing) == DrillDepth.QUARANTINE

    # Surface validator against this module's own namespace
    import sys
    ns = vars(sys.modules[__name__])
    result = validate_upstream_surface(ns)
    print(f"  self-validate: compatible={result.compatible}  {result.notes}")
    assert result.compatible

    # Surface validator against an incomplete namespace
    broken = {k: ns[k] for k in list(ns)[:5]}
    result2 = validate_upstream_surface(broken)
    print(f"  broken:        compatible={result2.compatible}  "
          f"missing={list(result2.missing_symbols)}")
    assert not result2.compatible

    print()
    print("Regression guards: OK")
