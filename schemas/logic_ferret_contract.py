"""
Logic-Ferret Contract -- stable surface of Logic-Ferret's schema_contract.

This module mirrors what Logic-Ferret declares as its canonical stable
surface:
    - SCHEMA_VERSION (semver string)
    - SENSOR_REGISTRY keys (13 sensor names)
    - LAYER_NAMES (8 layers used by DIAGNOSE)
    - SIGNAL_LEVELS ("strong" / "moderate" / "weak")
    - FALLACY_NAMES (dynamic; validated at runtime via ferret_surface())
    - DiagnoseResult / LayerResult (TypedDicts)
    - CALCULATE_C3 signature

TAF's ferret_fieldlink imports the constants and TypedDicts from here
and calls `validate_ferret_surface()` with Logic-Ferret's `ferret_surface()`
output at startup. If the major version differs, the fieldlink bails
rather than silently decoding against a stale shape.

UPSTREAM PIN
------------
    logic_ferret_schema_version: 1.0.0
    logic_ferret_ref:            https://github.com/JinnZ2/Logic-Ferret
    source_file:                 schema_contract.py

When upstream bumps SCHEMA_VERSION major (1.x.x -> 2.0.0), bump
CONTRACT_VERSION major here and update the mirrored constants.
Minor bumps (1.0.0 -> 1.1.0 for additions) do NOT require a TAF-side
bump -- the validator is forward-compatible on additions.

Versioning:
    CONTRACT_VERSION 1.1.0 = pinned against Logic-Ferret schema_contract.py
                              SCHEMA_VERSION "1.1.0".

    1.1.0 adds (all additive / backward-compatible):
      - shared tier vocabulary (GREEN/AMBER/RED/BLACK) matching
        metabolic-accounting and TAF
      - TIER_LEVELS, SIGNAL_TO_TIER, CAMOUFLAGE_TIER_THRESHOLDS
      - three new helper functions: score_to_tier, layer_tiers,
        sensor_tiers (mirrored in SIGNATURES)
      - SignatureMismatch exception + assert_signatures() contract
        check on the upstream side (this mirror provides an
        equivalent check_signatures())

    Upstream invariant clarified:
      "BLACK is only ever elevated into by a consumer that fuses
       Ferret output with an irreversibility source (e.g. TAF
       past-cliff basins)."
    Logic-Ferret emits GREEN/AMBER/RED from its own data; TAF/MA
    supply the BLACK signal when present.

Dependencies: stdlib only (typing, dataclasses).
License: CC0 1.0 Universal.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, TypedDict


CONTRACT_VERSION = "1.1.0"
UPSTREAM = "github.com/JinnZ2/Logic-Ferret"
UPSTREAM_SCHEMA_VERSION = "1.1.0"
UPSTREAM_SOURCE_FILE = "schema_contract.py"


# ---------------------------------------------------------------
# TYPE ALIASES (matching upstream)
# ---------------------------------------------------------------

SensorScore = float
SensorFlags = Dict[str, Any]
# AssessFn is (text: str) -> (SensorScore, SensorFlags). Not a runtime
# callable on our side -- just documented signature for consumers that
# want to invoke a Logic-Ferret sensor through a fieldlink.


# ---------------------------------------------------------------
# STRUCTURED OUTPUT SHAPES
# ---------------------------------------------------------------

class LayerResult(TypedDict, total=False):
    """One layer's contribution to DIAGNOSE output. All fields optional
    per upstream's total=False."""
    layer: str
    hits: int
    matches: List[str]
    signal: str              # one of SIGNAL_LEVELS
    structural_hits: int
    performative_hits: int
    negative_hits: int
    positive_hits: int
    divergence: int


class DiagnoseResult(TypedDict):
    """Top-level diagnose() output shape. All four fields required."""
    layers: List[LayerResult]
    fallacies: Dict[str, int]
    camouflage_score: float
    verdict: str


# ---------------------------------------------------------------
# CANONICAL CONSTANTS (mirrored from upstream schema_contract.py)
# ---------------------------------------------------------------

# The 13 sensor names exposed by SENSOR_REGISTRY upstream. Names are
# part of the contract -- they are what TAF keys friction-ratio
# weightings against in ferret_fieldlink.py. Order matches upstream
# for stable presentation; semantics do not depend on order.

SENSOR_NAMES: Tuple[str, ...] = (
    "Propaganda Tone",
    "Reward Manipulation",
    "False Urgency",
    "Gatekeeping",
    "Narrative Fragility",
    "Agency Score",
    "Propaganda Bias",
    "Logic Fallacy Ferret",
    "Gaslight Frequency",
    "Responsibility Deflection",
    "True Accountability",
    "Meritocracy Detector",
    "Conflict Diagnosis",
)


# The 8 layer names used by conflict_diagnosis.diagnose upstream.
# These are the keys consumers walk in a DiagnoseResult["layers"] list.

LAYER_NAMES: Tuple[str, ...] = (
    "Stated Problem",
    "Feasibility Gap",
    "Incentive Mapping",
    "Systemic Alignment",
    "Consequence Analysis",
    "Hidden Driver",
    "Peripheral Signals",
    "Feedback Loops",
)


# The three valid values of LayerResult["signal"].
SIGNAL_LEVELS: Tuple[str, ...] = ("strong", "moderate", "weak")


# ---------------------------------------------------------------
# TIER VOCABULARY (added in 1.1.0)
# ---------------------------------------------------------------
# Shared four-level vocabulary with the sibling frameworks
# (metabolic-accounting, TAF). String constants, not an enum --
# strings survive JSON, IPC, and cross-framework imports cleanly.
#
# Logic-Ferret emits GREEN / AMBER / RED from its own data.
# BLACK is reserved per upstream invariant: rhetoric is not
# thermodynamically irreversible, so Logic-Ferret never produces
# BLACK on its own. Consumers that fuse Ferret output with an
# irreversibility source (e.g. TAF past-cliff basins or
# metabolic-accounting Verdict.BLACK) may elevate.

GREEN = "GREEN"
AMBER = "AMBER"
RED   = "RED"
BLACK = "BLACK"

TIER_LEVELS: Tuple[str, ...] = (GREEN, AMBER, RED, BLACK)

# Per-layer signal ("strong"/"moderate"/"weak") -> Tier mapping.
SIGNAL_TO_TIER: Dict[str, str] = {
    "strong":   RED,
    "moderate": AMBER,
    "weak":     GREEN,
}

# Score thresholds on [0.0, 1.0] -> Tier. Sorted high-to-low;
# first threshold a score meets wins. Mirrors upstream's
# CAMOUFLAGE_TIER_THRESHOLDS verbatim.
CAMOUFLAGE_TIER_THRESHOLDS: Tuple[Tuple[float, str], ...] = (
    (0.70, RED),
    (0.45, AMBER),
    (0.00, GREEN),
)


# FALLACY_NAMES is dynamic upstream (derived from fallacy_overlay.
# FALLACY_PATTERNS.keys()). We do NOT hard-code the list here; TAF
# consumers should treat fallacy names as data from
# `ferret_surface()["fallacy_names"]` at runtime and validate counts
# against whatever names are present in the upstream version we're
# talking to.


# ---------------------------------------------------------------
# SIGNATURE DOCUMENTATION (non-executable, for consumers)
# ---------------------------------------------------------------

SIGNATURES: Dict[str, str] = {
    "assess":        "(text: str) -> (float, Dict[str, Any])",
    "diagnose":      ("(text: str) -> "
                      "{layers, fallacies, camouflage_score, verdict}"),
    "annotate_text": "(text: str) -> (str, Dict[str, int])",
    "calculate_c3":  "(Dict[str, float]) -> (float, Dict[str, float])",
    # Added in 1.1.0
    "score_to_tier": "(float) -> str",
    "layer_tiers":   "(text: str) -> Dict[str, str]",
    "sensor_tiers":  "(text: str) -> Dict[str, str]",
}


class SignatureMismatch(Exception):
    """Raised when a pinned signature has drifted from this contract.

    Mirrors upstream's SignatureMismatch. TAF's ferret_fieldlink can
    keep its own SIGNATURES copy and call check_signatures() below on
    import; any drift raises with every offending key named.
    """


def check_signatures(expected: Dict[str, str]) -> None:
    """Mirror of upstream's assert_signatures() against this contract.

    Consumers that pin individual signatures can call this to bail
    loudly on drift rather than silently decoding against a stale
    shape. Raises SignatureMismatch listing every offending key.
    """
    diffs = []
    for key, want in expected.items():
        got = SIGNATURES.get(key)
        if got is None:
            diffs.append(f"{key}: missing from contract (expected {want!r})")
        elif got != want:
            diffs.append(
                f"{key}: expected {want!r}, contract has {got!r}"
            )
    if diffs:
        raise SignatureMismatch(
            f"Logic-Ferret schema {UPSTREAM_SCHEMA_VERSION} signature "
            f"drift:\n  " + "\n  ".join(diffs)
        )


# ---------------------------------------------------------------
# RUNTIME SURFACE VALIDATION
# ---------------------------------------------------------------

@dataclass(frozen=True)
class SurfaceCheckResult:
    """Result of validating an upstream ferret_surface() payload."""
    compatible: bool
    upstream_version: str
    expected_version: str
    missing_sensors: Tuple[str, ...] = ()
    extra_sensors: Tuple[str, ...] = ()
    missing_layers: Tuple[str, ...] = ()
    extra_layers: Tuple[str, ...] = ()
    missing_signal_levels: Tuple[str, ...] = ()
    # Added in 1.1.0
    missing_tier_levels: Tuple[str, ...] = ()
    tier_vocabulary_available: bool = False
    notes: str = ""


def _major(version: str) -> int:
    """Extract major version from a semver string; -1 on parse failure."""
    try:
        return int(version.split(".")[0])
    except (ValueError, AttributeError, IndexError):
        return -1


def validate_ferret_surface(
    surface: Dict[str, Any],
    expected_schema_version: str = UPSTREAM_SCHEMA_VERSION,
) -> SurfaceCheckResult:
    """Validate a `ferret_surface()` payload against this contract.

    Parameters
    ----------
    surface : dict
        Output of upstream `ferret_surface()`. Shape:
        {schema_version, sensor_names, layer_names, signal_levels,
         fallacy_names, signatures}.
    expected_schema_version : str
        The upstream schema_version this TAF contract was pinned to.
        Defaults to UPSTREAM_SCHEMA_VERSION ('1.0.0').

    Returns
    -------
    SurfaceCheckResult
        .compatible is True when the upstream major version matches
        expected AND all canonical constants are present (additions
        are tolerated).
    """
    upstream_version = str(surface.get("schema_version", ""))
    expected = str(expected_schema_version)

    # Major-version check
    major_match = _major(upstream_version) == _major(expected)

    # Sensor names: all our canonical sensors must still be present
    upstream_sensors = tuple(surface.get("sensor_names", []))
    missing_sensors = tuple(
        s for s in SENSOR_NAMES if s not in upstream_sensors
    )
    extra_sensors = tuple(
        s for s in upstream_sensors if s not in SENSOR_NAMES
    )

    # Layer names: all our canonical layers must still be present
    upstream_layers = tuple(surface.get("layer_names", []))
    missing_layers = tuple(
        l for l in LAYER_NAMES if l not in upstream_layers
    )
    extra_layers = tuple(
        l for l in upstream_layers if l not in LAYER_NAMES
    )

    # Signal levels: exact match required (removing one is breaking)
    upstream_signals = tuple(surface.get("signal_levels", []))
    missing_signals = tuple(
        s for s in SIGNAL_LEVELS if s not in upstream_signals
    )

    # Tier vocabulary check (1.1.0+). Older upstreams omit tier_levels;
    # that's backward-compatible so we treat absence as "not available"
    # rather than incompatible.
    upstream_tiers = tuple(surface.get("tier_levels", []))
    if upstream_tiers:
        missing_tier_levels = tuple(
            t for t in TIER_LEVELS if t not in upstream_tiers
        )
        tier_available = not missing_tier_levels
    else:
        missing_tier_levels = ()
        tier_available = False

    compatible = (
        major_match
        and not missing_sensors
        and not missing_layers
        and not missing_signals
        and not missing_tier_levels
    )

    notes_parts = []
    if not major_match:
        notes_parts.append(
            f"Major-version mismatch: upstream={upstream_version!r}, "
            f"expected={expected!r}. Breaking change upstream -- "
            f"bump CONTRACT_VERSION on this side and update mirrors."
        )
    if missing_sensors:
        notes_parts.append(
            f"Missing canonical sensors: {list(missing_sensors)}."
        )
    if missing_layers:
        notes_parts.append(
            f"Missing canonical layers: {list(missing_layers)}."
        )
    if missing_signals:
        notes_parts.append(
            f"Missing canonical signal levels: {list(missing_signals)}."
        )
    if missing_tier_levels:
        notes_parts.append(
            f"Missing canonical tier levels: {list(missing_tier_levels)}."
        )
    if extra_sensors or extra_layers:
        notes_parts.append(
            "Upstream has additions not in this mirror (sensors: "
            f"{list(extra_sensors)}, layers: {list(extra_layers)}). "
            "Non-breaking on our side; consider bumping minor in TAF "
            "to surface the additions to consumers."
        )
    if upstream_tiers and not tier_available:
        notes_parts.append(
            "Upstream exposes tier_levels but is missing canonical "
            "entries."
        )

    return SurfaceCheckResult(
        compatible=compatible,
        upstream_version=upstream_version,
        expected_version=expected,
        missing_sensors=missing_sensors,
        extra_sensors=extra_sensors,
        missing_layers=missing_layers,
        extra_layers=extra_layers,
        missing_signal_levels=missing_signals,
        missing_tier_levels=missing_tier_levels,
        tier_vocabulary_available=tier_available,
        notes=" ".join(notes_parts) or "Surface matches contract.",
    )


# ---------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------

if __name__ == "__main__":
    print(f"Contract mirror version:     {CONTRACT_VERSION}")
    print(f"Upstream:                    {UPSTREAM}")
    print(f"Pinned upstream schema:      {UPSTREAM_SCHEMA_VERSION}")
    print(f"Canonical sensors:           {len(SENSOR_NAMES)}")
    print(f"Canonical layers:            {len(LAYER_NAMES)}")
    print(f"Signal levels:               {list(SIGNAL_LEVELS)}")
    print()

    # Simulate a well-formed 1.1.0 ferret_surface() payload.
    ok_surface = {
        "schema_version": "1.1.0",
        "sensor_names": list(SENSOR_NAMES),
        "layer_names": list(LAYER_NAMES),
        "signal_levels": list(SIGNAL_LEVELS),
        "fallacy_names": ["ad_hominem", "strawman", "false_equivalence"],
        "tier_levels": list(TIER_LEVELS),
        "signal_to_tier": dict(SIGNAL_TO_TIER),
        "camouflage_tier_thresholds": [
            list(pair) for pair in CAMOUFLAGE_TIER_THRESHOLDS
        ],
        "signatures": SIGNATURES,
    }
    result = validate_ferret_surface(ok_surface, expected_schema_version="1.1.0")
    print(f"OK 1.1.0     -> compatible={result.compatible}  "
          f"tier_available={result.tier_vocabulary_available}")

    # Major-version mismatch
    bumped = dict(ok_surface, schema_version="2.0.0")
    result = validate_ferret_surface(bumped)
    print(f"Bumped major -> compatible={result.compatible}")
    print(f"                {result.notes}")

    # Missing a canonical sensor
    broken = dict(ok_surface)
    broken["sensor_names"] = [s for s in SENSOR_NAMES if s != "Gatekeeping"]
    result = validate_ferret_surface(broken)
    print(f"Broken       -> compatible={result.compatible}")
    print(f"                {result.notes}")

    # Forward-compatible addition
    extended = dict(ok_surface)
    extended["sensor_names"] = list(SENSOR_NAMES) + ["New Sensor X"]
    result = validate_ferret_surface(extended)
    print(f"Extended     -> compatible={result.compatible}  {result.notes}")

    # Signature drift detection (new in 1.1.0 mirror)
    try:
        check_signatures({"layer_tiers": "(wrong signature)"})
        print("Signature drift -> FAILED to raise")
    except SignatureMismatch as e:
        print(f"Signature drift -> raises SignatureMismatch: "
              f"{str(e).splitlines()[0]}")
    check_signatures({"layer_tiers": SIGNATURES["layer_tiers"]})
    print("Signature match -> no exception")

    # Assertions for CI
    assert validate_ferret_surface(
        ok_surface, expected_schema_version="1.1.0").compatible
    assert not validate_ferret_surface(bumped).compatible
    assert not validate_ferret_surface(broken).compatible
    assert validate_ferret_surface(extended).compatible
    # Tier vocabulary present when upstream is 1.1.0+
    assert validate_ferret_surface(
        ok_surface, expected_schema_version="1.1.0"
    ).tier_vocabulary_available
    print()
    print("Regression guards: OK")