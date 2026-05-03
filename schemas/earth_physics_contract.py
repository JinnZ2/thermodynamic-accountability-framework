"""
Earth-Systems-Physics Contract -- stable surface of the
``assumption_validator`` package declared in
github.com/JinnZ2/earth-systems-physics.

This module mirrors what the upstream package exports as its public
API:

    - RiskLevel              (registry.py) -- GREEN / YELLOW / RED
    - AssumptionBoundary     (registry.py) -- stability envelope shape
    - ASSUMPTION_KEYS        (registry.py) -- frozen list of ~37
                                              REGISTRY identifiers
    - COUPLING_GRAPH         (registry.py) -- failure propagation graph
    - AssumptionRecord       (monitors.py) -- one timestamped reading
    - CascadeSnapshot        (monitors.py) -- cascade-state snapshot
    - Alert                  (monitors.py) -- transition alert shape
    - assess_from_layer_states  (registry.py) -- function signature
    - global_confidence_multiplier  (registry.py) -- function signature
    - detect_cascade_risk    (registry.py) -- function signature
    - full_report            (registry.py) -- function signature

UPSTREAM PIN
------------
    earth_systems_physics_ref:         https://github.com/JinnZ2/earth-systems-physics
    earth_systems_physics_commit_sha:  341a14b6e1706f16bea6a909d496bde4c8060109
    earth_systems_physics_version:     0.1.0  (assumption_validator/__init__.py __version__)

Upstream does NOT currently declare a SURFACE.md or version tag at
the repo level. The 0.1.0 version comes from the
``assumption_validator`` subpackage's __version__. This mirror is
pinned to a specific commit SHA. When upstream either (a) moves
main forward with surface-affecting changes, or (b) adopts a
SURFACE.md + repo-level CONTRACT_VERSION pattern like
Mathematic-economics and Logic-Ferret, bump CONTRACT_VERSION here
and update the SHA.

CONTRACT_VERSION 0.1.0 reflects upstream's pre-release status.

Dependencies: stdlib only (dataclasses, enum, typing). The full
upstream package depends on numpy + flask; this mirror does NOT
require either.

License: CC0 1.0 Universal (matches upstream).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


CONTRACT_VERSION = "0.1.0"
UPSTREAM = "github.com/JinnZ2/earth-systems-physics"
UPSTREAM_COMMIT_SHA = "341a14b6e1706f16bea6a909d496bde4c8060109"
UPSTREAM_VERSION = "0.1.0"  # assumption_validator/__init__.py __version__


# ---------------------------------------------------------------
# RISK LEVELS
# ---------------------------------------------------------------

class RiskLevel(Enum):
    """Three-tier validity state for any single physics assumption.

    GREEN  = parameter inside its stable envelope; equation valid
    YELLOW = parameter in transition zone; equation degrading
    RED    = parameter past red_threshold; equation invalid in the
             current regime (not just a parameter shift -- the
             governing equation no longer applies).
    """
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


# ---------------------------------------------------------------
# ASSUMPTION BOUNDARY (stable shape)
# ---------------------------------------------------------------

@dataclass
class AssumptionBoundary:
    """Mirror of upstream registry.AssumptionBoundary.

    Captures the stability envelope of a single physics assumption.
    Method bodies (``assess``, ``proximity_to_red``) are not part
    of this contract -- callers should resolve to the live upstream
    package when behavioral semantics are needed. This shape is
    sufficient for static inspection, registry diffing, and
    fieldlink stub fallbacks.
    """
    name: str
    parameter: str
    units: str
    green_range: Tuple[float, float]
    yellow_range: Tuple[float, float]
    red_threshold: float
    higher_is_worse: bool
    source_layer: int            # 0 (electromagnetics) .. 6 (biosphere)
    layer_key: str               # key in the layer's output dict
    couplings: List[str] = field(default_factory=list)
    rate_of_change: float = 0.0
    notes: str = ""


# ---------------------------------------------------------------
# REGISTRY KEYS (frozen mirror)
# ---------------------------------------------------------------

# The 37 assumption identifiers declared in upstream registry.REGISTRY
# at commit 341a14b. Layer-prefixed:
#   em_*    layer 0  electromagnetics + magnomechanics
#   mag_*   layer 1  magnetosphere
#   iono_*  layer 2  ionosphere
#   atmo_*  layer 3  atmosphere
#   hydro_* layer 4  hydrosphere
#   litho_* layer 5  lithosphere
#   bio_*   layer 6  biosphere
ASSUMPTION_KEYS: List[str] = [
    # Layer 0: electromagnetics + magnomechanics
    "em_plasma_frequency",
    "em_magnonic_damping",
    "em_magnonic_prop_length",
    "em_magnomech_coupling",
    "em_magnomech_v_acoustic",
    "em_magnomech_piezo",
    # Layer 1: magnetosphere
    "mag_standoff_Re",
    "mag_rotation_coupling",
    # Layer 2: ionosphere
    "iono_critical_freq",
    "iono_joule_heating",
    "iono_schumann_shift",
    # Layer 3: atmosphere
    "atmo_ghg_forcing",
    "atmo_net_forcing",
    "atmo_coriolis",
    "atmo_jet_shear",
    "atmo_hadley_extent",
    "atmo_convection",
    # Layer 4: hydrosphere
    "hydro_AMOC_collapse",
    "hydro_bottom_water",
    "hydro_deep_ventilation",
    "hydro_AMOC_transport",
    "hydro_arctic_amplification",
    "hydro_ice_albedo",
    "hydro_committed_warming",
    # Layer 5: lithosphere
    "litho_LOD_change",
    "litho_polar_drift",
    "litho_fault_stress",
    "litho_volcanic_enhancement",
    # Layer 6: biosphere
    "bio_NEP_sink",
    "bio_permafrost_flux",
    "bio_permafrost_CH4",
    "bio_ocean_pH",
    "bio_coral_dissolution",
    "bio_marine_productivity",
    "bio_amazon_tipping",
    "bio_co2_accumulation",
    "bio_planetary_boundaries",
]


# ---------------------------------------------------------------
# COUPLING GRAPH (verbatim mirror)
# ---------------------------------------------------------------

# Failure-propagation edges: when key K's status degrades, each entry
# in COUPLING_GRAPH[K] is a downstream assumption whose validity is
# now in question. Note: a few targets (grid_frequency, bio_crop_yield,
# atmo_blocking, hydro_SST, hydro_SST_dist, litho_ice_loss,
# bio_food_web, hydro_SA_precip) are downstream observables that are
# referenced as targets but are not themselves AssumptionBoundary keys
# in the registry. They are real coupling endpoints recognized by the
# upstream cascade detector; mirrors should preserve them verbatim.
COUPLING_GRAPH: Dict[str, List[str]] = {
    "mag_rotation_coupling":      ["atmo_coriolis", "litho_LOD_change", "grid_frequency"],
    "litho_LOD_change":           ["mag_rotation_coupling", "atmo_coriolis"],
    "atmo_coriolis":              ["atmo_jet_shear", "hydro_AMOC_transport", "atmo_hadley_extent"],
    "atmo_jet_shear":             ["bio_crop_yield", "atmo_blocking", "atmo_hadley_extent"],
    "atmo_ghg_forcing":           ["hydro_SST", "bio_permafrost_flux", "hydro_arctic_amplification"],
    "hydro_AMOC_collapse":        ["atmo_jet_shear", "bio_amazon_tipping", "hydro_SST_dist"],
    "hydro_AMOC_transport":       ["atmo_net_forcing", "bio_marine_productivity"],
    "hydro_arctic_amplification": ["atmo_jet_shear", "bio_permafrost_flux", "litho_ice_loss"],
    "hydro_ice_albedo":           ["atmo_net_forcing", "hydro_arctic_amplification"],
    "bio_permafrost_flux":        ["atmo_ghg_forcing", "bio_permafrost_CH4", "bio_co2_accumulation"],
    "bio_permafrost_CH4":         ["atmo_ghg_forcing", "bio_permafrost_flux"],
    "bio_NEP_sink":               ["bio_co2_accumulation", "bio_permafrost_flux", "bio_amazon_tipping"],
    "bio_amazon_tipping":         ["bio_NEP_sink", "atmo_ghg_forcing", "hydro_SA_precip"],
    "bio_ocean_pH":               ["bio_coral_dissolution", "bio_marine_productivity"],
    "bio_marine_productivity":    ["bio_co2_accumulation", "bio_food_web"],
    "litho_volcanic_enhancement": ["atmo_net_forcing", "bio_marine_productivity"],
}


# ---------------------------------------------------------------
# MONITOR-LAYER SHAPES (stable shape only, no behavior)
# ---------------------------------------------------------------

@dataclass
class AssumptionRecord:
    """One timestamped reading for a monitored assumption.

    timestamp is a ``datetime`` upstream; mirrored here as ``Any`` to
    keep the contract stdlib-only without importing datetime at
    contract scope. Consumers that need real datetime semantics
    should use the upstream class directly via the fieldlink.
    """
    timestamp: Any
    value: float
    status: str         # one of RiskLevel.value
    penalty: float      # 0.0 GREEN .. 1.0 RED
    proximity: float    # 0.0 (at green floor) .. 1.0 (at red threshold)


@dataclass
class CascadeSnapshot:
    """Cascade-state snapshot at one polling instant."""
    timestamp: Any
    level: str          # MINIMAL | LOW | MODERATE | HIGH | CRITICAL
    n_red: int
    n_yellow: int
    n_coupled: int
    multiplier: float
    message: str


@dataclass
class Alert:
    """Transition alert raised when an assumption changes status."""
    timestamp: Any
    assumption_id: str
    assumption_name: str
    alert_type: str
    previous_status: str
    current_status: str
    message: str
    hours_to_red: Optional[float] = None
    cascade_level: Optional[str] = None


# ---------------------------------------------------------------
# FUNCTION SIGNATURES (documentation only)
# ---------------------------------------------------------------

# These signatures document what the live upstream package exposes.
# The fieldlink ``earth_physics_fieldlink.py`` provides callable
# wrappers (with stdlib fallbacks); this contract lists them so
# downstream consumers can statically check the surface they couple
# to.

PUBLIC_FUNCTIONS: Dict[str, str] = {
    "assess_from_layer_states":
        "(layer_states: Dict[int, Dict]) -> Dict[str, Dict]",
    "global_confidence_multiplier":
        "(assessments: Dict[str, Dict]) -> float",
    "detect_cascade_risk":
        "(assessments: Dict[str, Dict]) -> Dict",
    "full_report":
        "(layer_states: Dict[int, Dict]) -> Dict",
}


# ---------------------------------------------------------------
# VALIDATION HELPERS
# ---------------------------------------------------------------

def validate_layer_states_shape(layer_states: Dict[int, Dict]) -> List[str]:
    """Static check that a layer_states payload matches the upstream
    contract: keys are ints in 0..6, values are dicts.

    Returns list of human-readable error strings; empty list = OK.
    Does NOT validate per-layer key contents (those depend on which
    upstream layer module was used to populate the state).
    """
    errors: List[str] = []
    if not isinstance(layer_states, dict):
        return [f"layer_states must be dict, got {type(layer_states).__name__}"]
    for k, v in layer_states.items():
        if not isinstance(k, int):
            errors.append(f"layer key {k!r} must be int (0..6)")
            continue
        if not (0 <= k <= 7):
            errors.append(f"layer key {k} out of range; expected 0..6 (or 7 for infrastructure)")
        if not isinstance(v, dict):
            errors.append(f"layer {k} value must be dict, got {type(v).__name__}")
    return errors


def known_assumption(key: str) -> bool:
    """True iff ``key`` is one of the canonical AssumptionBoundary
    identifiers in the upstream registry at the pinned commit."""
    return key in ASSUMPTION_KEYS


__all__ = [
    "CONTRACT_VERSION",
    "UPSTREAM",
    "UPSTREAM_COMMIT_SHA",
    "UPSTREAM_VERSION",
    "RiskLevel",
    "AssumptionBoundary",
    "ASSUMPTION_KEYS",
    "COUPLING_GRAPH",
    "AssumptionRecord",
    "CascadeSnapshot",
    "Alert",
    "PUBLIC_FUNCTIONS",
    "validate_layer_states_shape",
    "known_assumption",
]
