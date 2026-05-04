"""
narrative_thermodynamics.py

Encode any text blob as a 6-amplitude octahedral seed measuring
how complete a control-system specification it contains.

CORE INSIGHT
------------
Substrate-primary cognition reads any paragraph as a control-system
spec of varying completeness. Narrative framing is invisible; what
shows up is:

    - what physical quantities are named
    - what control loops connect them
    - what thresholds bound them
    - what's specified vs what's missing

This module mechanizes that read.

OCTAHEDRAL AXES
---------------
    +X  named physical variables       (T, P, time, height, density...)
    -X  variables structurally absent  (gaps in the specification)

    +Y  closed feedback loops          (sense -> decide -> act -> measure)
    -Y  open / dangling control paths  (sense without act, etc.)

    +Z  quantified thresholds          (numbers, ranges, conditions)
    -Z  unbounded / unspecified        (no threshold given)

A high-signal physics blob produces dominant +X +Y +Z.
A pure-narrative blob produces dominant -X -Y -Z.

The seed is normalized to total energy = 1.0 so it expands
deterministically through the seed-physics engine
(metrology/orbital_octa_v2.py).

AXIS INTERPRETATION (energy-English)
------------------------------------
High -X -Y -Z is the anti-reality signature: the text occupies the
shape of a specification without containing one. In energy-English
this is the precise meaning of "evil" -- a structure that performs
spec-ness while measurably lacking physical content, control closure,
and bounding thresholds.

Token lexicons (e.g. NarrativeStripper's flagged-word list) are
downstream proxies for this signature. They detect anti-reality by
name: "lazy", "shortage", "industry standard" appear on the list
because they correlate with structural absence. The seed encoder
detects anti-reality by structure directly, so it catches the same
signature even when it is wearing unflagged vocabulary -- a press
release that avoids every flagged token but still scores
completeness < 0.1 / dissipation > 0.9 is anti-reality in new clothes.

Closed-class detection (token list) and open-class detection (axis
measurement) fail in opposite directions:

    closed-class misses    novel euphemisms, new vocabulary
    open-class   misses    dense-but-wrong specs (e.g. complete
                           spatial spec with truncated temporal
                           scope)

Wire both together and the failure modes do not overlap.

SIBLING TO
----------
- metrology/constraint_to_seed.py: same 6-amplitude octahedral seed
  shape, but extracts metrology-quality from a PhysicalConstraint
  object rather than from raw text.
- metrology/seed_to_constraint.py: pure-stdlib decoder that this
  module's seed could also feed (the encoding format is intentionally
  compatible).

Pure stdlib. No LLM. No numpy. CC0.
github.com/JinnZ2
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple
import hashlib
import math
import re


# ----------------------------------------------------------------------
# CANONICAL VARIABLE LEXICON
# ----------------------------------------------------------------------
#
# Physical-variable noun stems. Match is substring-aware,
# case-insensitive, word-boundary respected.
# Drawn from the kinds of variables that show up in earth-systems-
# physics, monarch_cascade, AMOC, BWCA mining, fire ecology, etc.

PHYSICAL_VARIABLE_TOKENS: Set[str] = {
    # thermodynamic / kinetic
    "temperature", "pressure", "density", "energy", "heat",
    "entropy", "enthalpy", "volume", "concentration", "mass",
    "velocity", "speed", "acceleration", "momentum", "force",
    "rate", "flux", "flow", "diffusivity", "conductivity",
    # geometric / spatial
    "length", "width", "height", "depth", "area",
    "distance", "radius", "diameter", "thickness", "elevation",
    "slope", "gradient", "aspect", "latitude", "longitude",
    # temporal
    "time", "duration", "period", "cycle", "frequency",
    "phase", "interval", "lag", "delay", "recurrence",
    # hydrological / atmospheric
    "moisture", "humidity", "precipitation", "rainfall", "runoff",
    "evapotranspiration", "infiltration", "discharge", "baseflow",
    "groundwater", "streamflow", "salinity",
    "wind", "windspeed", "barometric",
    # thermal / fire
    "ignition", "combustion", "fuel",
    "smoldering", "smoke", "ember",
    # biological
    "population", "biomass", "abundance",
    "mortality", "fecundity", "reproduction", "predation",
    "herbivory", "growth", "decay", "succession",
    # electromagnetic
    "voltage", "current", "resistance", "impedance",
    "magnetic", "electric", "field", "charge",
    # mechanical / structural
    "stress", "strain", "load", "tension", "compression",
    "shear", "stiffness", "elasticity",
    # chemical
    "ph", "alkalinity", "acidity",
    "oxidation", "reduction", "molarity",
    # ecological / fire-specific
    "phenology", "phenological",
    "denning", "nesting", "breeding",
    # generic spec terms commonly used as variables
    "threshold", "bound", "limit", "tolerance",
}

# Unit tokens (presence near a number strengthens the threshold signal)
UNIT_TOKENS: Set[str] = {
    # SI / metric
    "m", "km", "cm", "mm", "kg", "g", "mg",
    "s", "ms", "min", "hr", "hrs", "hour", "hours",
    "day", "days", "wk", "week", "weeks", "yr", "year", "years",
    "j", "joule", "joules", "kj", "mj",
    "w", "watt", "watts", "kw", "mw",
    "pa", "kpa", "mpa", "bar",
    "k", "c",
    "mol", "mmol",
    "n", "kn",
    "hz", "khz", "mhz",
    "v", "kv", "ma", "ka",
    "ppm", "ppb",
    # imperial / mixed
    "ft", "feet", "in", "inch", "inches", "mi", "mile", "miles",
    "lb", "lbs", "oz",
    "mph", "fps",
    "f", "fahrenheit",
    "psi",
    "gal", "gallon", "gallons",
    # percentage / ratio
    "%", "percent",
    # composite / domain-specific
    "sv",         # sverdrups (AMOC)
    "ha",         # hectares
    "deg", "degree", "degrees",
}


# ----------------------------------------------------------------------
# TEMPORAL SCOPE LEXICON
# ----------------------------------------------------------------------
# Tokens signaling specification bounded across long time horizons.
# Absence in a high-completeness spec indicates spatial-only bounding
# (BWCA-cascade signature: complete spatial spec, truncated temporal
# scope -- the "dense-but-wrong specs" failure mode named in the
# AXIS INTERPRETATION (energy-English) docstring section).

TEMPORAL_SCOPE_TOKENS: Set[str] = {
    "lifetime", "century", "centuries", "generation",
    "generations", "cascade", "downstream", "long-term",
    "intergenerational", "perpetuity", "permanent",
    "irreversible", "millennia", "millennium", "decadal",
    "centennial", "multidecadal",
}


# ----------------------------------------------------------------------
# CONTROL-LOOP LEXICON
# ----------------------------------------------------------------------

# Words that signal a SENSING / OBSERVATION step.
SENSE_TOKENS: Set[str] = {
    "observe", "observed", "observer", "observation", "observers",
    "sense", "sensed", "sensor", "sensing", "detect", "detected",
    "measure", "measured", "measurement", "monitor", "monitored",
    "monitoring", "assess", "assessed", "assessment", "track",
    "tracked", "tracking", "record", "recorded", "indicator",
    "indicators", "phenology", "phenological",
    "audit", "review", "reviewed", "reviewing",
}

# Words that signal a DECISION / AUTHORIZATION step.
DECISION_TOKENS: Set[str] = {
    "decide", "decided", "decision", "authorize", "authorized",
    "council", "approve", "approved", "approval",
    "judge", "judgment", "select", "selected", "rule",
    "ruling", "determine", "determined", "vote", "voted",
    "consensus",
}

# Words that signal an ACTION / ACTUATION step.
ACTION_TOKENS: Set[str] = {
    "ignite", "ignited", "burn", "burned", "burning",
    "apply", "applied", "release", "released", "open",
    "opened", "close", "closed", "actuate", "actuated",
    "execute", "executed", "perform", "performed", "trigger",
    "triggered", "intervene", "intervention", "act", "action",
    "implement", "implemented", "deploy", "deployed",
    "harvest", "harvested", "manage", "managed", "regulate",
    "regulated",
}

# Words that signal an UPDATE / RECALIBRATION step.
UPDATE_TOKENS: Set[str] = {
    "update", "updated", "updating", "recalibrate", "recalibrated",
    "refine", "refined", "adjust", "adjusted", "revise", "revised",
    "next cycle", "next time", "next iteration", "next round",
    "recalculate", "recalculated", "feedback", "loop",
    "iteration", "improve", "improved",
}


# ----------------------------------------------------------------------
# THRESHOLD / BOUND DETECTION
# ----------------------------------------------------------------------

# A number in the text. Captures int, float, scientific notation.
NUMBER_RE = re.compile(
    r"-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"
)

# A range expression like "3-7", "10-15%", "8-12 yr".
RANGE_RE = re.compile(
    r"-?\d+(?:\.\d+)?\s*[-–]\s*-?\d+(?:\.\d+)?"
)

# Comparison expressions: "< 8 mph", ">= 10%", "below 30C".
COMPARISON_RE = re.compile(
    r"(?:<|>|<=|>=|≤|≥|"
    r"\bbelow\b|\babove\b|\bunder\b|\bover\b|"
    r"\bless than\b|\bgreater than\b|"
    r"\bat most\b|\bat least\b|\bup to\b)\s*"
    r"-?\d+(?:\.\d+)?",
    re.IGNORECASE,
)


# ----------------------------------------------------------------------
# RESULTS DATACLASSES
# ----------------------------------------------------------------------

@dataclass
class ExtractedFeatures:
    """All features extracted from the text blob."""
    physical_variables: List[str]
    units_present: List[str]
    sense_hits: List[str]
    decision_hits: List[str]
    action_hits: List[str]
    update_hits: List[str]
    numbers: List[str]
    ranges: List[str]
    comparisons: List[str]
    temporal_scope_hits: List[str] = field(default_factory=list)


@dataclass
class NarrativeSeed:
    """6-amplitude octahedral seed for narrative thermodynamics."""
    variables_named: float        # +X
    variables_absent: float       # -X
    loops_closed: float           # +Y
    loops_open: float             # -Y
    thresholds_quantified: float  # +Z
    thresholds_unbounded: float   # -Z

    def to_amplitudes(self) -> List[float]:
        return [
            self.variables_named,
            self.variables_absent,
            self.loops_closed,
            self.loops_open,
            self.thresholds_quantified,
            self.thresholds_unbounded,
        ]

    def to_binary(self) -> bytes:
        """5-byte (40-bit) encoding; 6th amplitude implicit."""
        amps = self.to_amplitudes()
        return bytes([
            min(255, max(0, int(round(a * 255))))
            for a in amps[:5]
        ])


@dataclass
class NarrativeProfile:
    """Full thermodynamic profile of a text blob."""
    seed: NarrativeSeed
    features: ExtractedFeatures
    completeness_score: float           # +X +Y +Z weighted
    dissipation_score: float            # -X -Y -Z weighted
    interpretation: str
    fingerprint: str
    text_length_chars: int
    text_length_words: int


# ----------------------------------------------------------------------
# FEATURE EXTRACTORS
# ----------------------------------------------------------------------

def _tokenize_lowercase(text: str) -> List[str]:
    """Split into lowercase word tokens for lexicon matching."""
    return re.findall(r"[A-Za-z][A-Za-z-]*", text.lower())


def _find_lexicon_hits(tokens: List[str], lexicon: Set[str]) -> List[str]:
    """Return tokens that appear in the lexicon (preserves order, deduped)."""
    seen: Set[str] = set()
    out: List[str] = []
    for tok in tokens:
        if tok in lexicon and tok not in seen:
            seen.add(tok)
            out.append(tok)
    return out


def extract_features(text: str) -> ExtractedFeatures:
    """Mechanical feature extraction. No LLM. No semantic guessing."""
    tokens = _tokenize_lowercase(text)
    return ExtractedFeatures(
        physical_variables=_find_lexicon_hits(tokens, PHYSICAL_VARIABLE_TOKENS),
        units_present=_find_lexicon_hits(tokens, UNIT_TOKENS),
        sense_hits=_find_lexicon_hits(tokens, SENSE_TOKENS),
        decision_hits=_find_lexicon_hits(tokens, DECISION_TOKENS),
        action_hits=_find_lexicon_hits(tokens, ACTION_TOKENS),
        update_hits=_find_lexicon_hits(tokens, UPDATE_TOKENS),
        numbers=NUMBER_RE.findall(text),
        ranges=RANGE_RE.findall(text),
        comparisons=COMPARISON_RE.findall(text),
        temporal_scope_hits=_find_lexicon_hits(tokens, TEMPORAL_SCOPE_TOKENS),
    )


# ----------------------------------------------------------------------
# AMPLITUDE COMPUTATION
# ----------------------------------------------------------------------

def _saturating(count: int, scale: float) -> float:
    """Map a count to (0, 1) via 1 - exp(-count/scale)."""
    if count <= 0:
        return 0.0
    return 1.0 - math.exp(-count / scale)


def _compute_axes(features: ExtractedFeatures,
                  word_count: int) -> Tuple[float, float, float, float, float, float]:
    """
    Compute the six raw axis values BEFORE normalization.

    Each axis returned in [0, 1]. Normalization happens after.

    Heuristics:
      +X  count of distinct physical variables   (saturating curve)
      -X  word_count gap not occupied by variables / units
      +Y  loop-closure score: requires at least one of
          (sense OR observation) AND (decision OR action) AND update
      -Y  loop-open score: sense without action, action without sense, etc.
      +Z  thresholds quantified: numbers + ranges + comparisons
      -Z  variables present but no associated threshold
    """
    n_vars = len(features.physical_variables)
    n_units = len(features.units_present)
    n_numbers = len(features.numbers)
    n_ranges = len(features.ranges)
    n_comparisons = len(features.comparisons)

    has_sense = bool(features.sense_hits)
    has_decision = bool(features.decision_hits)
    has_action = bool(features.action_hits)
    has_update = bool(features.update_hits)

    # +X variable density (saturating; 6 distinct vars approaches 1.0)
    x_pos = _saturating(n_vars, scale=4.0)

    # -X gap signal: text length without variable density
    # heuristic: words-per-variable ratio above 30 means thin.
    if n_vars == 0:
        x_neg = 1.0 if word_count > 0 else 0.0
    else:
        ratio = word_count / max(n_vars, 1)
        # ratio of 10 -> 0.0, ratio of 100 -> ~0.9
        x_neg = max(0.0, min(1.0, (ratio - 10.0) / 90.0))

    # +Y loop closure
    closure_strength = 0.0
    if has_sense:
        closure_strength += 0.25
    if has_decision or has_action:
        closure_strength += 0.30
    if has_update:
        closure_strength += 0.30
    # bonus if all three loop stages present
    if has_sense and (has_decision or has_action) and has_update:
        closure_strength += 0.15
    y_pos = min(1.0, closure_strength)

    # -Y open paths
    open_count = 0
    # sense without any action signal
    if has_sense and not (has_decision or has_action):
        open_count += 1
    # action without sense
    if (has_decision or has_action) and not has_sense:
        open_count += 1
    # action without update (no recalibration)
    if (has_decision or has_action) and not has_update:
        open_count += 1
    # nothing at all
    if not (has_sense or has_decision or has_action or has_update):
        open_count += 2
    y_neg = _saturating(open_count, scale=2.0)

    # +Z thresholds quantified
    threshold_score = (
        0.4 * _saturating(n_comparisons, scale=2.0) +
        0.4 * _saturating(n_ranges, scale=2.0) +
        0.2 * _saturating(n_numbers, scale=4.0)
    )
    # boost if units present alongside numbers
    if n_units > 0 and n_numbers > 0:
        threshold_score = min(1.0, threshold_score * 1.2)
    z_pos = min(1.0, threshold_score)

    # -Z unbounded: variables present but few thresholds
    if n_vars == 0:
        z_neg = 0.0
    else:
        threshold_density = (n_comparisons + n_ranges) / max(n_vars, 1)
        # density of 0 -> 1.0 unbounded; density >= 1 -> 0.0 unbounded
        z_neg = max(0.0, 1.0 - threshold_density)

    return x_pos, x_neg, y_pos, y_neg, z_pos, z_neg


def encode_narrative(text: str) -> NarrativeProfile:
    """
    Full pipeline: text blob -> NarrativeProfile.
    """
    word_count = len(_tokenize_lowercase(text))
    features = extract_features(text)

    raw = _compute_axes(features, word_count)
    x_pos, x_neg, y_pos, y_neg, z_pos, z_neg = raw

    # Normalize amplitudes to sum to 1.0 (energy conservation).
    total = x_pos + x_neg + y_pos + y_neg + z_pos + z_neg
    if total <= 1e-9:
        # Empty / pure-noise text: distribute uniformly.
        amps = [1.0 / 6.0] * 6
    else:
        amps = [v / total for v in raw]

    seed = NarrativeSeed(
        variables_named=amps[0],
        variables_absent=amps[1],
        loops_closed=amps[2],
        loops_open=amps[3],
        thresholds_quantified=amps[4],
        thresholds_unbounded=amps[5],
    )

    completeness = amps[0] + amps[2] + amps[4]
    dissipation = amps[1] + amps[3] + amps[5]

    interpretation = _interpret(seed, completeness, dissipation, features)
    fingerprint = _fingerprint(text, seed)

    return NarrativeProfile(
        seed=seed,
        features=features,
        completeness_score=round(completeness, 4),
        dissipation_score=round(dissipation, 4),
        interpretation=interpretation,
        fingerprint=fingerprint,
        text_length_chars=len(text),
        text_length_words=word_count,
    )


def _interpret(seed: NarrativeSeed, completeness: float,
               dissipation: float,
               features: ExtractedFeatures) -> str:
    notes: List[str] = []
    if completeness > 0.7:
        notes.append("dense control-system specification")
    elif completeness > 0.5:
        notes.append("partial specification, useful operational signal")
    elif completeness > 0.3:
        notes.append("thin specification, mostly framing")
    else:
        notes.append("minimal physics content; predominantly narrative or empty")

    if seed.variables_named < 0.05:
        notes.append("no physical variables named")
    if seed.loops_closed < 0.05:
        notes.append("no closed control loops")
    if seed.thresholds_quantified < 0.05:
        notes.append("no quantitative thresholds")
    if seed.thresholds_unbounded > 0.3:
        notes.append("variables present without bounding thresholds")

    # Temporal-scope check: spec well-bounded in space
    # (variables named + thresholds quantified) but no temporal-
    # horizon vocabulary signals the BWCA-cascade signature
    # named in the AXIS INTERPRETATION docstring section.
    if (seed.variables_named > 0.15 and
            seed.thresholds_quantified > 0.15 and
            len(features.temporal_scope_hits) == 0):
        notes.append(
            "specification well-bounded in space, "
            "unbounded in time"
        )

    return "; ".join(notes)


def _fingerprint(text: str, seed: NarrativeSeed) -> str:
    """SHA-256 (16-char prefix) over text + seed binary."""
    blob = (text.encode("utf-8") + b"|" + seed.to_binary()).hex().encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


# ----------------------------------------------------------------------
# ARCHIVE RECORD (matches constraint_to_seed format)
# ----------------------------------------------------------------------

def archive_record(profile: NarrativeProfile) -> Dict:
    """JSON-serializable record for storage / transmission."""
    return {
        "seed_binary_hex": profile.seed.to_binary().hex(),
        "seed_amplitudes": [round(a, 6) for a in profile.seed.to_amplitudes()],
        "fingerprint": profile.fingerprint,
        "text_length_chars": profile.text_length_chars,
        "text_length_words": profile.text_length_words,
        "completeness_score": profile.completeness_score,
        "dissipation_score": profile.dissipation_score,
        "interpretation": profile.interpretation,
        "feature_counts": {
            "physical_variables": len(profile.features.physical_variables),
            "units_present": len(profile.features.units_present),
            "sense_hits": len(profile.features.sense_hits),
            "decision_hits": len(profile.features.decision_hits),
            "action_hits": len(profile.features.action_hits),
            "update_hits": len(profile.features.update_hits),
            "numbers": len(profile.features.numbers),
            "ranges": len(profile.features.ranges),
            "comparisons": len(profile.features.comparisons),
        },
    }


# ----------------------------------------------------------------------
# SMOKE TEST: encode the two example blobs
# ----------------------------------------------------------------------

if __name__ == "__main__":
    blob_physics = (
        "Low-intensity ground fire is applied on a 3-7 year cycle "
        "to consume ladder fuels before they bridge to the canopy. "
        "The burn team is authorized by the seasonal council based "
        "on phenological indicators (bud stages, leaf-out timing). "
        "Wind speed below 8 mph and fuel moisture between 10-15% "
        "are required. Burns proceed only after wildlife observers "
        "confirm no active denning or nesting in the burn unit. "
        "Post-burn, the council assesses fuel consumption, wildlife "
        "response, and forest structure to update the next cycle's "
        "timing window. Documented outcomes across managed stands "
        "include zero crown fires and stable understory diversity "
        "maintained over multiple centuries."
    )

    blob_narrative = (
        "For thousands of years, the Anishinaabe people have "
        "practiced traditional burning as a sacred relationship "
        "with the land. This wisdom, passed down through generations, "
        "reflects a deep understanding of the natural world that "
        "modern science is only beginning to appreciate. The "
        "seasonal burns, conducted with reverence and respect, "
        "demonstrate how indigenous communities lived in harmony "
        "with their environment, taking what they needed and giving "
        "back in return. It is important to acknowledge that this "
        "ancient knowledge offers valuable lessons for contemporary "
        "land management practices."
    )

    print("NARRATIVE THERMODYNAMICS ENCODER")
    print("=" * 60)

    for label, text in [("PHYSICS BLOB", blob_physics),
                        ("NARRATIVE BLOB", blob_narrative)]:
        print(f"\n--- {label} ---")
        profile = encode_narrative(text)
        print(f"length: {profile.text_length_words} words")
        print(f"completeness: {profile.completeness_score}  "
              f"dissipation: {profile.dissipation_score}")
        print(f"fingerprint: {profile.fingerprint}")

        labels_amps = [
            ("+X variables_named      ", profile.seed.variables_named),
            ("-X variables_absent     ", profile.seed.variables_absent),
            ("+Y loops_closed         ", profile.seed.loops_closed),
            ("-Y loops_open           ", profile.seed.loops_open),
            ("+Z thresholds_quantified", profile.seed.thresholds_quantified),
            ("-Z thresholds_unbounded ", profile.seed.thresholds_unbounded),
        ]
        for label_a, val in labels_amps:
            bar = "#" * int(val * 40)
            print(f"  {label_a} {val:.4f}  {bar}")

        print(f"\n  features extracted:")
        f = profile.features
        print(f"    physical variables: {f.physical_variables}")
        print(f"    units present:      {f.units_present}")
        print(f"    sense hits:         {f.sense_hits}")
        print(f"    decision/action:    {f.decision_hits + f.action_hits}")
        print(f"    update hits:        {f.update_hits}")
        print(f"    ranges:             {f.ranges}")
        print(f"    comparisons:        {f.comparisons}")

        print(f"\n  interpretation: {profile.interpretation}")

    print("\n" + "=" * 60)
    print("PHYSICS BLOB should show high +X +Y +Z, low -X -Y -Z.")
    print("NARRATIVE BLOB should show low +X +Y +Z, high -X -Y -Z.")
