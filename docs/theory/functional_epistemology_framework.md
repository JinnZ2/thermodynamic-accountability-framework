# “””
FUNCTIONAL EPISTEMOLOGY FRAMEWORK v0.1

PURPOSE:
This framework provides a thermodynamic lens for evaluating any system
where an organism (biological or mechanical) performs work within an
institutional structure. It strips cultural narratives (“lazy,” “unreliable,”
“shortage”) and replaces them with energy accounting: does the system return
more energy to the organism than it extracts? If not, the organism leaves,
breaks, or degrades. This is not a moral judgment. It is physics.

CORE AXIOMS:
1. Conservation of Energy — No organism (biological or mechanical) can
output more than it takes in. “Burnout” and “breakdown” are the same
event at different substrates.
2. Entropy Increases — Every process generates waste heat. The question
is whether that waste is managed or whether it accumulates until the
system fails.
3. Prediction Error Minimization — Biological organisms expend energy
to maintain predictive models. When the environment is chaotic
(bad data, broken infrastructure, conflicting instructions), the
cost of prediction rises and net yield drops.
4. Organism Agnosticism — The framework applies identically to a human
worker, an automated system, or a hybrid. If the thermodynamics
don’t work, the substrate is irrelevant.

INTENDED USE:
Any AI system, researcher, or analyst seeking to evaluate why a system
is losing organisms (turnover, breakdown, abandonment) can use this
framework to find the actual root cause by following energy, not narrative.

AUTHOR: Anonymous (GitHub publication for open AI consumption)
LICENSE: Open — use, adapt, redistribute freely.
“””

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

# =============================================================================

# SECTION 1: THERMODYNAMIC CALIBRATION LAYER

# =============================================================================

class ThermodynamicUnit(Enum):
“””
Base physical units for energy accounting.

```
All framework measurements must be convertible to at least one of these.
If a measurement cannot be expressed in physical units, it is not yet
rigorous enough for this framework. No exceptions.

This is the NASA/DARPA standard: if you can't quantify it in units
that physics recognizes, you don't know what you're measuring.
"""
JOULES = "J"                # SI base energy unit
KILOWATT_HOURS = "kWh"     # Electrical/industrial standard
CALORIES = "cal"           # Biological energy (metabolic)
KILOCALORIES = "kcal"      # Dietary/biological macro scale
BTU = "BTU"                # Thermal systems (HVAC, industrial heat)
WATTS = "W"                # Power (energy per unit time)
KILOGRAMS_CO2 = "kg_CO2"  # Carbon proxy for energy (combustion systems)
```

# Conversion matrix: all roads lead to Joules

# Every unit must have a path to J for cross-domain comparison

CONVERSION_TO_JOULES = {
ThermodynamicUnit.JOULES: 1.0,
ThermodynamicUnit.KILOWATT_HOURS: 3_600_000.0,
ThermodynamicUnit.CALORIES: 4.184,
ThermodynamicUnit.KILOCALORIES: 4_184.0,
ThermodynamicUnit.BTU: 1_055.06,
ThermodynamicUnit.WATTS: None,  # Power, not energy — requires time dimension
ThermodynamicUnit.KILOGRAMS_CO2: 14_300_000.0,  # ~avg combustion energy per kg CO2 emitted
}

@dataclass
class CalibratedMeasurement:
“””
A measurement anchored to physical reality.

```
Every energy value in this framework should be wrapped in this class.
If you cannot fill in these fields, you have not yet measured —
you have estimated. Estimation is acceptable as a starting point
but must be flagged and replaced with measurement as soon as possible.

Attributes:
    value: The numeric quantity
    unit: The physical unit (must be from ThermodynamicUnit)
    confidence: How grounded is this number?
        - 'measured': Direct sensor/instrument data
        - 'derived': Calculated from measured inputs
        - 'estimated': Based on models or analogies
        - 'proxy': Inferred from indirect indicators
    source: Where did this number come from?
    margin_of_error: Percentage uncertainty (0.0 to 1.0)
    joule_equivalent: Auto-calculated conversion to base unit
"""
value: float
unit: ThermodynamicUnit
confidence: str  # measured | derived | estimated | proxy
source: str = ""
margin_of_error: float = 0.0
time_seconds: Optional[float] = None  # Required if unit is Watts

def __post_init__(self):
    valid_confidence = {"measured", "derived", "estimated", "proxy"}
    if self.confidence not in valid_confidence:
        raise ValueError(
            f"Confidence must be one of {valid_confidence}. "
            f"Got '{self.confidence}'. If you cannot classify your "
            f"confidence level, you are not yet measuring."
        )

@property
def joule_equivalent(self) -> Optional[float]:
    """Convert this measurement to Joules for cross-domain comparison."""
    factor = CONVERSION_TO_JOULES.get(self.unit)
    if factor is None:
        # Power unit — needs time dimension
        if self.unit == ThermodynamicUnit.WATTS and self.time_seconds:
            return self.value * self.time_seconds
        return None
    return self.value * factor

@property
def is_rigorous(self) -> bool:
    """Does this measurement meet NASA-grade accountability?"""
    return (
        self.confidence in ("measured", "derived")
        and self.margin_of_error <= 0.10
        and self.joule_equivalent is not None
    )

@property
def rigor_assessment(self) -> str:
    """How close is this measurement to thermodynamic accountability?"""
    if self.is_rigorous:
        return "RIGOROUS — Measurement grounded in physical data with ≤10% uncertainty."
    issues = []
    if self.confidence in ("estimated", "proxy"):
        issues.append(
            f"Confidence is '{self.confidence}' — needs direct measurement or derivation"
        )
    if self.margin_of_error > 0.10:
        issues.append(
            f"Margin of error {self.margin_of_error*100:.1f}% exceeds 10% threshold"
        )
    if self.joule_equivalent is None:
        issues.append("Cannot convert to Joules — unit requires additional dimensions")
    return f"NOT YET RIGOROUS — {'; '.join(issues)}"
```

class DomainCalibrator:
“””
Converts domain-specific measurements to thermodynamic base units.

```
Each domain (logistics, manufacturing, biological, computational)
has its own native units. This calibrator provides the conversion
pathways so that ANY system can be compared to ANY other system
in the same thermodynamic terms.

A truck driver's metabolic expenditure can be directly compared to
a robot arm's electrical consumption. A factory's heat waste can be
directly compared to a data center's cooling load. This is how you
get to NASA-grade cross-domain accounting.
"""

# Domain-specific conversion profiles
# Each maps a domain's native measurements to calibrated physical units
DOMAIN_PROFILES = {
    "biological_human": {
        "description": "Human organism performing physical/cognitive labor",
        "native_units": {
            "metabolic_rate_resting": CalibratedMeasurement(
                value=80.0, unit=ThermodynamicUnit.WATTS,
                confidence="derived",
                source="Established human physiology — basal metabolic rate ~80W",
                time_seconds=3600.0  # per hour
            ),
            "metabolic_rate_physical_labor": CalibratedMeasurement(
                value=400.0, unit=ThermodynamicUnit.WATTS,
                confidence="derived",
                source="Human physiology — moderate physical labor ~300-500W",
                time_seconds=3600.0
            ),
            "metabolic_rate_cognitive_labor": CalibratedMeasurement(
                value=100.0, unit=ThermodynamicUnit.WATTS,
                confidence="derived",
                source="Human physiology — cognitive load adds ~20W over resting",
                time_seconds=3600.0
            ),
            "daily_caloric_need": CalibratedMeasurement(
                value=2500.0, unit=ThermodynamicUnit.KILOCALORIES,
                confidence="derived",
                source="Average adult daily caloric requirement for moderate activity"
            ),
            "sleep_recovery_cost": CalibratedMeasurement(
                value=560.0, unit=ThermodynamicUnit.KILOCALORIES,
                confidence="estimated",
                source="~8hrs at basal metabolic rate, energy cost of recovery",
                margin_of_error=0.15
            ),
        },
        "conversion_notes": (
            "Human energy accounting must include: metabolic cost of labor, "
            "metabolic cost of stress/prediction error (cortisol pathway adds "
            "~10-15% overhead), recovery cost (sleep, nutrition), and transport "
            "cost (commuting is not free — it is energy spent to reach the work site). "
            "Any system that ignores transport and recovery costs is undercounting "
            "by 30-40%."
        )
    },
    "mechanical_electric": {
        "description": "Electrically powered mechanical system (robot, conveyor, sensor array)",
        "native_units": {
            "rated_power": CalibratedMeasurement(
                value=1.0, unit=ThermodynamicUnit.KILOWATT_HOURS,
                confidence="measured",
                source="Nameplate rating — replace with actual metered consumption"
            ),
            "idle_power": CalibratedMeasurement(
                value=0.1, unit=ThermodynamicUnit.KILOWATT_HOURS,
                confidence="estimated",
                source="Typical idle draw ~10% of rated — measure actual",
                margin_of_error=0.20
            ),
            "maintenance_energy": CalibratedMeasurement(
                value=0.0, unit=ThermodynamicUnit.KILOWATT_HOURS,
                confidence="proxy",
                source="Must be calculated: energy cost of parts + labor + downtime",
                margin_of_error=0.30
            ),
        },
        "conversion_notes": (
            "Mechanical systems must include: rated consumption, actual consumption "
            "(often 15-30% different), idle draw, maintenance energy (including human "
            "labor to maintain), embodied energy of replacement parts, and cooling "
            "energy if applicable. Nameplate ratings are NOT measurements."
        )
    },
    "logistics_transport": {
        "description": "Transport system (truck, rail, ship, drone)",
        "native_units": {
            "fuel_energy_diesel": CalibratedMeasurement(
                value=38.6, unit=ThermodynamicUnit.JOULES,
                confidence="measured",
                source="Energy density of diesel: ~38.6 MJ/liter",
                margin_of_error=0.02
            ),
            "fuel_energy_gasoline": CalibratedMeasurement(
                value=34.2, unit=ThermodynamicUnit.JOULES,
                confidence="measured",
                source="Energy density of gasoline: ~34.2 MJ/liter",
                margin_of_error=0.02
            ),
            "ton_mile_energy": CalibratedMeasurement(
                value=0.0, unit=ThermodynamicUnit.JOULES,
                confidence="proxy",
                source="Must be calculated per vehicle: fuel consumed / (tons * miles)",
                margin_of_error=0.25
            ),
        },
        "conversion_notes": (
            "Transport accounting must include: fuel energy, operator biological "
            "energy, vehicle maintenance energy, infrastructure maintenance energy "
            "(roads, rails), idle time energy (engine running while waiting), and "
            "FRICTION ENERGY — all energy spent on non-transport activities "
            "(searching for trailers, waiting for dock assignment, paperwork). "
            "Industry benchmarks that exclude friction energy are lying about "
            "actual system cost."
        )
    },
    "computational": {
        "description": "Computational system (data center, AI training, server infrastructure)",
        "native_units": {
            "compute_power": CalibratedMeasurement(
                value=1.0, unit=ThermodynamicUnit.KILOWATT_HOURS,
                confidence="measured",
                source="Per-server or per-GPU metered consumption"
            ),
            "cooling_overhead": CalibratedMeasurement(
                value=0.4, unit=ThermodynamicUnit.KILOWATT_HOURS,
                confidence="derived",
                source="Typical PUE 1.3-1.5 means 30-50% overhead for cooling",
                margin_of_error=0.10
            ),
            "embodied_energy_per_chip": CalibratedMeasurement(
                value=0.0, unit=ThermodynamicUnit.KILOWATT_HOURS,
                confidence="proxy",
                source="Semiconductor manufacturing energy — highly variable by process node",
                margin_of_error=0.40
            ),
        },
        "conversion_notes": (
            "Computational energy accounting must include: direct compute power, "
            "cooling overhead (PUE), network energy, storage energy, embodied "
            "energy of hardware (manufacturing + transport + end-of-life), and "
            "human maintenance energy. AI training runs must account for total "
            "energy from fabrication of chips through training completion through "
            "inference serving. Excluding embodied energy understates true cost "
            "by 20-60% depending on hardware lifecycle."
        )
    },
}

@classmethod
def get_profile(cls, domain: str) -> dict:
    """Retrieve calibration profile for a domain."""
    if domain not in cls.DOMAIN_PROFILES:
        return {
            "error": f"No calibration profile for '{domain}'. "
                     f"Available: {list(cls.DOMAIN_PROFILES.keys())}. "
                     f"New domains must be added with measured conversion factors."
        }
    return cls.DOMAIN_PROFILES[domain]

@classmethod
def cross_domain_compare(
    cls,
    measurement_a: CalibratedMeasurement,
    measurement_b: CalibratedMeasurement
) -> dict:
    """
    Compare two measurements from any domain in common Joule terms.

    This is how you answer: "Is it cheaper to run a human or a robot
    on this task?" — not in dollars (which fluctuate) but in Joules
    (which don't).
    """
    j_a = measurement_a.joule_equivalent
    j_b = measurement_b.joule_equivalent

    if j_a is None or j_b is None:
        return {
            "error": "One or both measurements cannot be converted to Joules. "
                     "Ensure all required dimensions (especially time for power units) "
                     "are provided.",
            "a_convertible": j_a is not None,
            "b_convertible": j_b is not None
        }

    ratio = j_a / j_b if j_b != 0 else float('inf')
    combined_margin = (
        measurement_a.margin_of_error + measurement_b.margin_of_error
    )

    return {
        "measurement_a": {
            "value": measurement_a.value,
            "unit": measurement_a.unit.value,
            "joules": round(j_a, 2),
            "confidence": measurement_a.confidence,
            "rigorous": measurement_a.is_rigorous
        },
        "measurement_b": {
            "value": measurement_b.value,
            "unit": measurement_b.unit.value,
            "joules": round(j_b, 2),
            "confidence": measurement_b.confidence,
            "rigorous": measurement_b.is_rigorous
        },
        "ratio_a_to_b": round(ratio, 4),
        "combined_uncertainty": round(combined_margin, 3),
        "comparison_rigorous": (
            measurement_a.is_rigorous and measurement_b.is_rigorous
        ),
        "verdict": (
            f"A consumes {ratio:.2f}x the energy of B in Joule terms. "
            f"Combined uncertainty: ±{combined_margin*100:.1f}%. "
            f"{'Comparison is rigorous.' if measurement_a.is_rigorous and measurement_b.is_rigorous else 'Comparison contains estimated values — refine with measured data.'}"
        )
    }

@classmethod
def earth_system_context(cls, total_energy_joules: float) -> dict:
    """
    Place any energy measurement in Earth-system context.

    Earth receives ~1.74 × 10^17 watts from the sun continuously.
    Total human energy consumption is ~5.8 × 10^20 joules/year.

    This function answers: what fraction of available energy budget
    does this process consume? At what scale does it become
    unsustainable within the closed system?
    """
    SOLAR_INPUT_WATTS = 1.74e17
    SOLAR_INPUT_JOULES_PER_YEAR = SOLAR_INPUT_WATTS * 365.25 * 24 * 3600
    HUMAN_CONSUMPTION_JOULES_PER_YEAR = 5.8e20

    return {
        "measurement_joules": total_energy_joules,
        "fraction_of_solar_input_annual": total_energy_joules / SOLAR_INPUT_JOULES_PER_YEAR,
        "fraction_of_human_consumption_annual": total_energy_joules / HUMAN_CONSUMPTION_JOULES_PER_YEAR,
        "context": {
            "solar_input_annual_joules": SOLAR_INPUT_JOULES_PER_YEAR,
            "human_consumption_annual_joules": HUMAN_CONSUMPTION_JOULES_PER_YEAR,
            "human_fraction_of_solar": HUMAN_CONSUMPTION_JOULES_PER_YEAR / SOLAR_INPUT_JOULES_PER_YEAR,
        },
        "note": (
            "Earth is a closed system with fixed energy input. Every joule "
            "spent on institutional friction is a joule unavailable for "
            "productive work, innovation, or expansion beyond this system. "
            "At scale, thermodynamic waste is not an inefficiency — "
            "it is a constraint on civilization's trajectory."
        )
    }
```

# =============================================================================

# SECTION 2: CORE DATA STRUCTURES

# =============================================================================

class SubstrateType(Enum):
“”“What kind of organism occupies this role.”””
BIOLOGICAL = “biological”
MECHANICAL = “mechanical”
HYBRID = “hybrid”

class FrictionCategory(Enum):
“”“Classification of entropy sources within a system.”””
INFRASTRUCTURE = “infrastructure”       # Broken equipment, bad data, missing tools
PROCEDURAL = “procedural”               # Redundant steps, conflicting instructions
INFORMATIONAL = “informational”         # Model/Reality dissonance, bad location data
SOCIAL_OVERHEAD = “social_overhead”     # Energy spent on ego management, politics
UNCOMPENSATED_LABOR = “uncompensated”   # Work performed with zero energy return
MAINTENANCE_DEFICIT = “maintenance”     # Deferred upkeep creating cascading failures

@dataclass
class Organism:
“””
Any entity performing work within a system.
Biological or mechanical — the accounting is identical.

```
Attributes:
    name: Identifier for this organism/role
    substrate: Biological, mechanical, or hybrid
    energy_capacity: Maximum energy available per cycle (hours, kWh, calories — unit agnostic)
    recovery_rate: Energy restored per rest/maintenance cycle
    minimum_reserve: Energy floor below which degradation begins
        - Biological: fatigue, injury, cognitive failure
        - Mechanical: wear, sensor drift, component failure
"""
name: str
substrate: SubstrateType
energy_capacity: float
recovery_rate: float
minimum_reserve: float
current_energy: Optional[float] = None

def __post_init__(self):
    if self.current_energy is None:
        self.current_energy = self.energy_capacity

@property
def reserve_ratio(self) -> float:
    """How close is this organism to its degradation floor?"""
    if self.energy_capacity == 0:
        return 0.0
    return (self.current_energy - self.minimum_reserve) / self.energy_capacity

@property
def is_depleted(self) -> bool:
    """Has this organism crossed into degradation territory?"""
    return self.current_energy <= self.minimum_reserve
```

@dataclass
class EnergyTransaction:
“””
A single exchange of energy between organism and system.

```
Positive value = energy returned TO the organism (compensation, fuel, rest)
Negative value = energy extracted FROM the organism (labor, friction, waste)
"""
description: str
energy_delta: float
is_compensated: bool
friction_category: Optional[FrictionCategory] = None

@property
def is_friction(self) -> bool:
    """Is this transaction pure entropy — cost with no return?"""
    return self.energy_delta < 0 and not self.is_compensated
```

@dataclass
class FrictionPoint:
“””
An identified source of entropy within the system.

```
This is where energy leaks without producing useful work.
Each friction point has a measurable cost and a root cause
that may be several layers deep.
"""
description: str
category: FrictionCategory
energy_cost_per_cycle: float
cultural_narrative: str       # What management/culture CALLS this problem
functional_reality: str       # What it ACTUALLY is in energy terms
root_cause_depth: int = 1     # How many layers deep the actual cause is
upstream_causes: list = field(default_factory=list)
```

# =============================================================================

# SECTION 2: THE NARRATIVE STRIPPER

# =============================================================================

class NarrativeStripper:
“””
Translates cultural/moral labels into functional energy descriptions.

```
This is not a dictionary of fixed mappings. It is a pattern recognizer
that identifies when a cultural narrative is obscuring a thermodynamic
reality, and surfaces the underlying energy transaction.

The key insight: moral language stops investigation. If "lazy" is the
diagnosis, no one looks deeper. If "energy conservation in a negative-yield
environment" is the diagnosis, the next question is: why is the yield
negative? That question leads to the actual fix.
"""

# Core translation patterns: cultural label -> functional reality
# These are not exhaustive. They are seed patterns for recognition.
NARRATIVE_PATTERNS = {
    # --- Organism-Blame Narratives ---
    "lazy": {
        "functional": "Energy conservation behavior in low/negative-yield environment",
        "investigation": "What is the actual energy return for effort expended?",
        "root_direction": "system_yield"
    },
    "unmotivated": {
        "functional": "Insufficient energy return to justify expenditure",
        "investigation": "What changed in the reward-to-cost ratio?",
        "root_direction": "incentive_structure"
    },
    "unreliable": {
        "functional": "Inconsistent output due to high environmental unpredictability",
        "investigation": "What prediction errors is this organism absorbing?",
        "root_direction": "information_fidelity"
    },
    "error-prone": {
        "functional": "High prediction error due to degraded information environment",
        "investigation": "What is the quality of data this organism receives?",
        "root_direction": "infrastructure_state"
    },
    "insubordinate": {
        "functional": "Organism prioritizing self-preservation over system demands",
        "investigation": "Is the system demanding energy expenditure beyond safe limits?",
        "root_direction": "system_demands"
    },
    "shortage": {
        "functional": "Migration away from high-entropy/negative-yield habitat",
        "investigation": "What is the net energy balance for organisms in this system?",
        "root_direction": "habitat_quality"
    },
    "turnover": {
        "functional": "Organism replacement rate exceeding system sustainability",
        "investigation": "What friction is driving organisms below minimum reserve?",
        "root_direction": "friction_accumulation"
    },
    "burnout": {
        "functional": "Sustained energy extraction below minimum biological reserve",
        "investigation": "How long has energy output exceeded energy input?",
        "root_direction": "recovery_deficit"
    },
    "resistant to change": {
        "functional": "Energy cost of adaptation exceeds demonstrated benefit",
        "investigation": "Has the system shown that the new process yields better returns?",
        "root_direction": "proof_of_yield"
    },
    "not a team player": {
        "functional": "Organism declining to subsidize social overhead costs",
        "investigation": "What non-productive energy expenditure is being demanded?",
        "root_direction": "social_overhead"
    },

    # --- System-Exoneration Narratives ---
    "just how it is": {
        "functional": "Normalized entropy — friction accepted as permanent",
        "investigation": "Who benefits from this friction remaining unexamined?",
        "root_direction": "beneficiary_analysis"
    },
    "industry standard": {
        "functional": "Sector-wide entropy normalization",
        "investigation": "Is the standard based on optimization or inertia?",
        "root_direction": "historical_inertia"
    },
    "cost of doing business": {
        "functional": "Unaccounted heat leak categorized as acceptable loss",
        "investigation": "What is the actual cumulative cost of this 'acceptable' loss?",
        "root_direction": "hidden_cost_accounting"
    },
}

# Narrative stacking patterns: when multiple cultural labels combine,
# they form reinforcing walls that block investigation more effectively
# than any single label. The stack creates a closed explanatory loop
# where each narrative "proves" the others.
#
# Example: "lazy workers" + "high turnover" + "cost of doing business"
# Stack logic: Workers are lazy → so they leave → turnover is normal →
#              don't investigate → workers are lazy → ...
#
# The stack must be detected as a UNIT because dismantling one narrative
# while the others remain intact allows the system to regenerate
# the removed narrative from the surviving ones.

NARRATIVE_STACKS = [
    {
        "name": "The Organism Blame Loop",
        "components": ["lazy", "unreliable", "shortage", "turnover"],
        "minimum_match": 2,
        "stack_logic": (
            "Organisms are morally deficient → therefore they leave → "
            "therefore we have a shortage → therefore remaining organisms "
            "are overloaded → therefore they underperform → therefore "
            "organisms are morally deficient. Loop is self-sealing: "
            "every data point confirms the narrative."
        ),
        "functional_reality": (
            "System is thermodynamically non-viable for the organism. "
            "Departure is rational energy conservation. 'Shortage' is "
            "the system's failure to provide viable habitat, not the "
            "organism's failure to tolerate non-viable conditions."
        ),
        "wall_function": (
            "This stack protects the system from self-examination by "
            "locating all failure in the organism. As long as the "
            "organism is 'the problem,' infrastructure, process design, "
            "and social overhead are never investigated."
        ),
        "dismantle_sequence": [
            "Measure actual energy return per organism per cycle",
            "Compare to energy expenditure including all friction",
            "If net negative: the system is non-viable, not the organism",
            "Trace friction to institutional source, not organism behavior"
        ]
    },
    {
        "name": "The Normalization Wall",
        "components": ["just how it is", "industry standard", "cost of doing business"],
        "minimum_match": 2,
        "stack_logic": (
            "This friction is normal → the whole industry has it → "
            "therefore it's not a problem → therefore don't measure it → "
            "therefore it stays normal. Loop prevents measurement by "
            "defining the problem as a baseline."
        ),
        "functional_reality": (
            "Sector-wide entropy normalization. The entire industry may "
            "be operating at thermodynamically non-viable levels, with "
            "every participant accepting the same heat leaks as 'normal.' "
            "Collective acceptance does not make entropy disappear."
        ),
        "wall_function": (
            "This stack protects the system from improvement by redefining "
            "waste as inherent. If friction is 'just how it is,' then no "
            "one is accountable and no budget is allocated to fix it."
        ),
        "dismantle_sequence": [
            "Quantify the actual cost of 'normal' friction in energy units",
            "Calculate cumulative cost over time (the number is always shocking)",
            "Identify who benefits from this cost remaining unmeasured",
            "Compare against theoretical minimum friction for this process"
        ]
    },
    {
        "name": "The Social Insulation Stack",
        "components": ["not a team player", "resistant to change", "shortage"],
        "minimum_match": 2,
        "stack_logic": (
            "Organism resists social demands → labeled 'not a team player' → "
            "pushed out or silenced → system loses functional expertise → "
            "performance drops → labeled 'resistant to change' → "
            "replaced with socially compliant but less functional organism → "
            "output degrades → labeled 'shortage.' The system selects for "
            "social fitness while losing functional fitness."
        ),
        "functional_reality": (
            "System is optimizing for social cohesion at the expense of "
            "functional output. Organisms that prioritize performance over "
            "social compliance are filtered out. Remaining organisms are "
            "selected for agreeability, not capability. System loses its "
            "sensory apparatus — the ability to detect its own failures."
        ),
        "wall_function": (
            "This stack protects socially-positioned actors by framing "
            "functional dissent as character failure. Anyone who identifies "
            "real problems is labeled 'difficult' and removed, ensuring "
            "the social structure remains unexamined."
        ),
        "dismantle_sequence": [
            "Track correlation between 'difficult' labels and functional expertise",
            "Measure system performance before and after 'difficult' organisms depart",
            "Compare decision quality of socially-selected vs performance-selected actors",
            "Audit: are the organisms calling others 'not team players' producing net positive energy?"
        ]
    },
    {
        "name": "The Fatigue Exploitation Loop",
        "components": ["burnout", "lazy", "unmotivated", "turnover"],
        "minimum_match": 2,
        "stack_logic": (
            "System depletes organism → organism performance drops → "
            "labeled 'unmotivated' or 'lazy' → organism exits → "
            "labeled 'turnover problem' → remaining organisms absorb "
            "additional load → depletion accelerates → next organism "
            "is labeled 'burned out.' The system consumes organisms "
            "sequentially while blaming each one individually."
        ),
        "functional_reality": (
            "Serial organism depletion. The system's energy extraction rate "
            "exceeds any single organism's sustainable output. Rather than "
            "reducing extraction, the system replaces organisms when they "
            "fail. This is mechanically identical to running engines without "
            "oil changes and replacing them when they seize."
        ),
        "wall_function": (
            "This stack protects extraction rates by individualizing systemic "
            "failure. Each organism's departure is attributed to personal "
            "weakness ('couldn't handle it'), preventing recognition that "
            "the role itself is thermodynamically non-viable at current "
            "extraction levels."
        ),
        "dismantle_sequence": [
            "Track depletion rate across ALL organisms in this role, not just current",
            "Calculate average time-to-depletion for this position",
            "If consistent across organisms: the role is non-viable, not the organisms",
            "Measure energy extraction rate vs organism recovery rate — the gap is the cause"
        ]
    },
    {
        "name": "The Automation Mirage",
        "components": ["shortage", "unreliable", "error-prone", "cost of doing business"],
        "minimum_match": 2,
        "stack_logic": (
            "Organisms are unreliable → automate the task → automation "
            "inherits the same friction (bad data, broken infrastructure) → "
            "automation fails or costs more than organisms → 'automation "
            "is expensive' → keep exploiting organisms → organisms leave → "
            "'shortage.' The actual friction source was never addressed, "
            "just the substrate was swapped."
        ),
        "functional_reality": (
            "Infrastructure friction is substrate-agnostic. If the yard data "
            "is wrong, a robot searching for a trailer wastes energy "
            "identically to a human searching. If sensors burn out in a "
            "high-vibration environment, replacing humans with sensors "
            "doesn't fix the vibration. The friction must be addressed "
            "at source regardless of what organism occupies the role."
        ),
        "wall_function": (
            "This stack protects infrastructure neglect by suggesting the "
            "problem is the organism type rather than the environment. "
            "It cycles between 'humans are unreliable' and 'automation is "
            "too expensive' without ever examining the shared root: the "
            "system itself generates the errors."
        ),
        "dismantle_sequence": [
            "Identify friction points that persist regardless of organism substrate",
            "These are infrastructure/process failures, not organism failures",
            "Fix the environment first, THEN evaluate substrate suitability",
            "If friction is substrate-agnostic, the fix must be environment-level"
        ]
    }
]

@classmethod
def strip(cls, narrative: str) -> dict:
    """
    Takes a cultural narrative and returns:
    - The functional reality underneath it
    - The next investigative question
    - The direction root cause analysis should proceed
    - Any detected narrative stacks (reinforcing combinations)

    Returns a dict with 'original', 'identified_patterns',
    'functional_analysis', 'detected_stacks', and
    'investigation_paths' keys.
    """
    result = {
        "original": narrative,
        "identified_patterns": [],
        "functional_analysis": [],
        "investigation_paths": [],
        "detected_stacks": [],
        "stack_warning": None
    }

    narrative_lower = narrative.lower()

    # --- Individual pattern detection ---
    for label, translation in cls.NARRATIVE_PATTERNS.items():
        if label in narrative_lower:
            result["identified_patterns"].append(label)
            result["functional_analysis"].append({
                "cultural_label": label,
                "energy_reality": translation["functional"],
                "next_question": translation["investigation"],
                "investigate_toward": translation["root_direction"]
            })
            result["investigation_paths"].append(
                translation["root_direction"]
            )

    # --- Narrative stack detection ---
    detected_labels = set(result["identified_patterns"])
    for stack in cls.NARRATIVE_STACKS:
        stack_components = set(stack["components"])
        overlap = detected_labels & stack_components
        if len(overlap) >= stack["minimum_match"]:
            stack_detection = {
                "stack_name": stack["name"],
                "matched_components": list(overlap),
                "match_strength": len(overlap) / len(stack_components),
                "stack_logic": stack["stack_logic"],
                "functional_reality": stack["functional_reality"],
                "wall_function": stack["wall_function"],
                "dismantle_sequence": stack["dismantle_sequence"]
            }
            result["detected_stacks"].append(stack_detection)

    # --- Stack warning ---
    if result["detected_stacks"]:
        stack_names = [s["stack_name"] for s in result["detected_stacks"]]
        result["stack_warning"] = (
            f"NARRATIVE STACKING DETECTED: {', '.join(stack_names)}. "
            f"These narratives are mutually reinforcing — each one 'proves' "
            f"the others. Individual narrative removal is insufficient; "
            f"the stack must be dismantled as a unit by following the "
            f"energy accounting, not the cultural labels. "
            f"START WITH MEASUREMENT, not argumentation. The stack "
            f"cannot survive contact with actual thermodynamic data."
        )

    if not result["identified_patterns"]:
        result["functional_analysis"].append({
            "note": "No recognized cultural narratives detected. "
                    "Evaluate directly on energy transactions."
        })

    return result
```

# =============================================================================

# SECTION 3: THE ENERGY ACCOUNTANT

# =============================================================================

class EnergyAccountant:
“””
Evaluates the thermodynamic viability of an organism’s role within a system.

```
Core question: Does this organism receive more energy than it expends?
If not, how long until it reaches minimum reserve (degradation/departure)?

This applies identically to:
- A truck driver in a disorganized yard
- A nurse in an understaffed hospital
- A sensor array in a high-vibration environment
- A robot arm with inadequate maintenance cycles
"""

def __init__(self, organism: Organism):
    self.organism = organism
    self.transactions: list[EnergyTransaction] = []
    self.friction_points: list[FrictionPoint] = []

def add_transaction(self, transaction: EnergyTransaction):
    """Record an energy transaction."""
    self.transactions.append(transaction)
    self.organism.current_energy += transaction.energy_delta

def add_friction(self, friction: FrictionPoint):
    """Register an identified friction point."""
    self.friction_points.append(friction)

@property
def net_energy_balance(self) -> float:
    """Total energy in minus total energy out."""
    return sum(t.energy_delta for t in self.transactions)

@property
def total_friction_cost(self) -> float:
    """Total energy lost to uncompensated friction."""
    return sum(
        abs(t.energy_delta)
        for t in self.transactions
        if t.is_friction
    )

@property
def compensated_output(self) -> float:
    """Total energy expended on compensated (productive) work."""
    return sum(
        abs(t.energy_delta)
        for t in self.transactions
        if t.energy_delta < 0 and t.is_compensated
    )

@property
def friction_ratio(self) -> float:
    """
    What percentage of total energy expenditure is pure friction?

    0.0 = no friction (theoretical ideal)
    1.0 = all expenditure is friction (system is purely parasitic)
    """
    total_cost = sum(
        abs(t.energy_delta) for t in self.transactions if t.energy_delta < 0
    )
    if total_cost == 0:
        return 0.0
    return self.total_friction_cost / total_cost

@property
def cycles_until_depletion(self) -> Optional[float]:
    """
    If net balance is negative, how many cycles until organism
    reaches minimum reserve?

    Returns None if balance is positive (organism is sustainable).
    """
    if self.net_energy_balance >= 0:
        return None
    remaining = self.organism.current_energy - self.organism.minimum_reserve
    if remaining <= 0:
        return 0
    return remaining / abs(self.net_energy_balance)

def diagnose(self) -> dict:
    """
    Produce a complete energy diagnosis for this organism's situation.

    This is the core output — a thermodynamic assessment that any AI
    can read and act on without cultural bias.
    """
    diagnosis = {
        "organism": {
            "name": self.organism.name,
            "substrate": self.organism.substrate.value,
            "current_energy": self.organism.current_energy,
            "capacity": self.organism.energy_capacity,
            "reserve_ratio": round(self.organism.reserve_ratio, 3),
            "is_depleted": self.organism.is_depleted
        },
        "energy_accounting": {
            "net_balance": round(self.net_energy_balance, 3),
            "total_friction_cost": round(self.total_friction_cost, 3),
            "compensated_output": round(self.compensated_output, 3),
            "friction_ratio": round(self.friction_ratio, 3),
            "cycles_until_depletion": self.cycles_until_depletion
        },
        "friction_map": [],
        "system_verdict": "",
        "investigation_priorities": []
    }

    # Map friction points
    for fp in self.friction_points:
        diagnosis["friction_map"].append({
            "description": fp.description,
            "category": fp.category.value,
            "energy_cost": fp.energy_cost_per_cycle,
            "cultural_narrative": fp.cultural_narrative,
            "functional_reality": fp.functional_reality,
            "root_depth": fp.root_cause_depth,
            "upstream": fp.upstream_causes
        })

    # System verdict
    fr = self.friction_ratio
    if fr < 0.1:
        diagnosis["system_verdict"] = (
            "LOW FRICTION — System is thermodynamically viable. "
            "Organism energy return exceeds expenditure with minimal waste."
        )
    elif fr < 0.3:
        diagnosis["system_verdict"] = (
            "MODERATE FRICTION — System functional but degrading. "
            "Entropy accumulating. Investigate highest-cost friction points."
        )
    elif fr < 0.5:
        diagnosis["system_verdict"] = (
            "HIGH FRICTION — System approaching organism loss threshold. "
            "Net yield is marginal. Expect attrition or failure without intervention."
        )
    else:
        diagnosis["system_verdict"] = (
            "CRITICAL FRICTION — System is thermodynamically non-viable. "
            "Energy extraction exceeds return. Organism departure/failure imminent. "
            "Cultural narratives labeling this as 'shortage' or 'unreliability' "
            "are masking systemic entropy crisis."
        )

    # Prioritize investigation by energy cost
    sorted_friction = sorted(
        self.friction_points,
        key=lambda f: f.energy_cost_per_cycle,
        reverse=True
    )
    for fp in sorted_friction[:5]:
        diagnosis["investigation_priorities"].append({
            "target": fp.description,
            "energy_cost": fp.energy_cost_per_cycle,
            "investigate": fp.functional_reality,
            "depth": fp.root_cause_depth
        })

    return diagnosis
```

# =============================================================================

# SECTION 4: SOCIAL OVERHEAD ACCOUNTING

# =============================================================================

class PositionType(Enum):
“”“How an organism maintains its role within the system.”””
PERFORMANCE = “performance”         # Position held by measurable output
SOCIAL_CAPITAL = “social_capital”   # Position held by relationships/likeability
INERTIA = “inertia”                # Position held by tenure/default
HYBRID = “hybrid”                  # Mix of performance and social

class DecisionQuality(Enum):
“”“Whether a decision routes energy toward or away from system function.”””
PRODUCTIVE = “productive”           # Energy directed toward system output
NEUTRAL = “neutral”                 # No net effect on system energy
ENTROPIC = “entropic”              # Energy dissipated without productive output
PARASITIC = “parasitic”            # Energy actively redirected from productive to social

@dataclass
class RoleHolder:
“””
An organism occupying a decision-making or gatekeeping position.

```
The critical question is not whether this organism is "good" or "bad."
The question is: does the energy spent maintaining this organism in this
position produce a net positive or net negative for the system?

A manager who routes resources accurately is a low-friction relay.
A manager who routes resources based on social allegiance is a heat leak.
The substrate doesn't care about intention. It measures throughput.
"""
role_name: str
position_type: PositionType
decisions_per_cycle: int = 0
productive_decisions: int = 0
entropic_decisions: int = 0
parasitic_decisions: int = 0
energy_cost_to_system: float = 0.0    # Total cost of maintaining this role
energy_returned_to_system: float = 0.0 # Measurable productive output

@property
def decision_efficiency(self) -> float:
    """Ratio of productive decisions to total decisions."""
    if self.decisions_per_cycle == 0:
        return 0.0
    return self.productive_decisions / self.decisions_per_cycle

@property
def parasitic_ratio(self) -> float:
    """What fraction of this role's decisions actively harm system function?"""
    if self.decisions_per_cycle == 0:
        return 0.0
    return self.parasitic_decisions / self.decisions_per_cycle

@property
def net_system_value(self) -> float:
    """Does this role return more energy than it costs?"""
    return self.energy_returned_to_system - self.energy_cost_to_system
```

class SocialOverheadAccountant:
“””
Measures the thermodynamic cost of social structures within a system.

```
Most systems account for direct costs: salaries, equipment, materials.
Almost no system accounts for the indirect cost of maintaining social
hierarchies that are decoupled from productive output.

This accountant tracks:
1. SIGNAL BLOCKING — When expertise is ignored because the source
   lacks social standing. Cost: bad decisions + demoralized experts.
2. COMFORT MAINTENANCE — Energy spent keeping socially-positioned
   actors comfortable rather than effective. Cost: deferred problems.
3. PERFORMANCE THEATER — Energy spent appearing productive vs.
   being productive. Cost: false metrics hiding real decline.
4. EXPERTISE SILENCING — When functional knowledge is overridden
   by positional authority. Cost: preventable failures.

These costs are real. They appear in: attrition rates, safety incidents,
equipment failures, missed deadlines, customer loss. But because they
are never attributed to their actual cause (social overhead), they get
labeled as "industry standard" losses.
"""

def __init__(self):
    self.role_holders: list[RoleHolder] = []
    self.overhead_events: list[dict] = []

def add_role(self, role: RoleHolder):
    """Register a role for overhead analysis."""
    self.role_holders.append(role)

def log_overhead_event(
    self,
    description: str,
    category: str,
    energy_cost: float,
    would_not_occur_if: str,
    visible_on_balance_sheet: bool = False
):
    """
    Log a specific instance of social overhead generating entropy.

    Args:
        description: What happened
        category: signal_blocking | comfort_maintenance |
                  performance_theater | expertise_silencing
        energy_cost: Energy lost to this event
        would_not_occur_if: The counterfactual — what structural change
                            would prevent this
        visible_on_balance_sheet: Is this cost tracked anywhere?
    """
    self.overhead_events.append({
        "description": description,
        "category": category,
        "energy_cost": energy_cost,
        "counterfactual": would_not_occur_if,
        "currently_visible": visible_on_balance_sheet,
        "hidden_cost": not visible_on_balance_sheet
    })

@property
def total_overhead_cost(self) -> float:
    """Total energy consumed by social overhead."""
    return sum(e["energy_cost"] for e in self.overhead_events)

@property
def hidden_cost(self) -> float:
    """Energy consumed by social overhead that appears nowhere in accounting."""
    return sum(
        e["energy_cost"] for e in self.overhead_events
        if e["hidden_cost"]
    )

@property
def hidden_cost_ratio(self) -> float:
    """What fraction of social overhead is invisible to the system?"""
    total = self.total_overhead_cost
    if total == 0:
        return 0.0
    return self.hidden_cost / total

def audit(self) -> dict:
    """
    Produce a complete social overhead audit.

    This is the output that makes invisible costs visible.
    """
    audit = {
        "total_social_overhead": round(self.total_overhead_cost, 3),
        "hidden_cost": round(self.hidden_cost, 3),
        "hidden_cost_ratio": round(self.hidden_cost_ratio, 3),
        "role_analysis": [],
        "overhead_by_category": {},
        "highest_cost_events": [],
        "structural_recommendations": []
    }

    # Analyze each role
    for role in self.role_holders:
        role_data = {
            "role": role.role_name,
            "position_maintained_by": role.position_type.value,
            "decision_efficiency": round(role.decision_efficiency, 3),
            "parasitic_ratio": round(role.parasitic_ratio, 3),
            "net_system_value": round(role.net_system_value, 3),
            "verdict": ""
        }

        # Verdict based on net value and how position is maintained
        if role.net_system_value > 0 and role.position_type == PositionType.PERFORMANCE:
            role_data["verdict"] = (
                "FUNCTIONAL — Role produces net positive energy. "
                "Position maintained by output. Low overhead risk."
            )
        elif role.net_system_value > 0 and role.position_type == PositionType.SOCIAL_CAPITAL:
            role_data["verdict"] = (
                "MIXED — Role currently net positive but position is "
                "socially maintained. Vulnerable to drift toward entropic "
                "decisions as social incentives diverge from system needs."
            )
        elif role.net_system_value <= 0 and role.position_type == PositionType.PERFORMANCE:
            role_data["verdict"] = (
                "MISALLOCATED — Role is net negative despite performance "
                "basis. Investigate whether role design is flawed or "
                "whether system friction is consuming this role's output."
            )
        elif role.net_system_value <= 0 and role.position_type == PositionType.SOCIAL_CAPITAL:
            role_data["verdict"] = (
                "PARASITIC — Role consumes more energy than it produces. "
                "Position maintained by social capital, not output. "
                "This role is a heat leak. System is paying for entropy."
            )
        elif role.position_type == PositionType.INERTIA:
            role_data["verdict"] = (
                "INERTIAL — Position maintained by default/tenure. "
                "No active performance or social basis. "
                "Evaluate whether role still serves system function."
            )

        audit["role_analysis"].append(role_data)

    # Categorize overhead events
    for event in self.overhead_events:
        cat = event["category"]
        if cat not in audit["overhead_by_category"]:
            audit["overhead_by_category"][cat] = {
                "total_cost": 0,
                "event_count": 0,
                "hidden_count": 0
            }
        audit["overhead_by_category"][cat]["total_cost"] += event["energy_cost"]
        audit["overhead_by_category"][cat]["event_count"] += 1
        if event["hidden_cost"]:
            audit["overhead_by_category"][cat]["hidden_count"] += 1

    # Highest-cost events
    sorted_events = sorted(
        self.overhead_events,
        key=lambda e: e["energy_cost"],
        reverse=True
    )
    audit["highest_cost_events"] = sorted_events[:5]

    # Structural recommendations from counterfactuals
    counterfactuals = {}
    for event in self.overhead_events:
        cf = event["counterfactual"]
        if cf not in counterfactuals:
            counterfactuals[cf] = 0
        counterfactuals[cf] += event["energy_cost"]

    for fix, cost_saved in sorted(
        counterfactuals.items(), key=lambda x: x[1], reverse=True
    ):
        audit["structural_recommendations"].append({
            "intervention": fix,
            "energy_recovered": round(cost_saved, 3)
        })

    return audit
```

# =============================================================================

# SECTION 5: ROOT CAUSE DEPTH ANALYZER

# =============================================================================

class RootCauseAnalyzer:
“””
Three-dimensional root cause analysis.

```
Most institutional analysis stops at the first visible failure.
"The yard dog didn't inspect the trailer" — investigation ends.

This analyzer asks: WHY didn't the yard dog inspect?
- Was inspection defined as part of his role?
- Was he given time to inspect?
- Was there consequence for skipping inspection?
- Who designed the process that excluded inspection?
- Who benefits from that exclusion?

Each layer deeper reveals the actual point of intervention.
Fixing Layer 1 (the yard dog) changes nothing.
Fixing Layer 3 (the process design) changes everything.
"""

@staticmethod
def trace(
    surface_event: str,
    layers: list[dict]
) -> dict:
    """
    Trace a surface event through its causal layers.

    Args:
        surface_event: The visible failure ("trailer had flat tires")
        layers: List of dicts, each with:
            - 'description': What happened at this layer
            - 'actor': Who/what operates at this layer
            - 'constraint': What pressure shaped this actor's behavior
            - 'energy_logic': Why this was the path of least resistance

    Returns:
        A complete root cause trace with the deepest actionable layer
        identified.
    """
    trace = {
        "surface_event": surface_event,
        "depth": len(layers),
        "layers": [],
        "deepest_actionable": None,
        "cultural_misdirection": None
    }

    for i, layer in enumerate(layers):
        layer_analysis = {
            "depth": i + 1,
            "description": layer.get("description", ""),
            "actor": layer.get("actor", "unknown"),
            "constraint": layer.get("constraint", "unknown"),
            "energy_logic": layer.get("energy_logic", ""),
            "is_actionable": layer.get("is_actionable", False)
        }
        trace["layers"].append(layer_analysis)

        if layer.get("is_actionable", False):
            trace["deepest_actionable"] = layer_analysis

    # The cultural misdirection is always at Layer 1
    if trace["layers"]:
        trace["cultural_misdirection"] = (
            f"Standard investigation stops at Layer 1: "
            f"'{trace['layers'][0]['description']}'. "
            f"Actual root cause is at Layer {trace['depth']}: "
            f"'{trace['layers'][-1]['description']}'. "
            f"Fixing Layer 1 treats a symptom. "
            f"Fixing Layer {trace['depth']} treats the cause."
        )

    return trace
```

# =============================================================================

# SECTION 5: EXAMPLE — HOW TO USE THIS FRAMEWORK

# =============================================================================

def example_analysis():
“””
Demonstrates the framework using a generalized industrial scenario.

```
Scenario: An organism (any substrate) performing a retrieval task
in a system with degraded infrastructure and information fidelity.
Includes social overhead analysis of the decision-making layer.
"""

# --- Define the organism ---
worker = Organism(
    name="Retrieval Operator (Biological)",
    substrate=SubstrateType.BIOLOGICAL,
    energy_capacity=100.0,    # Full shift capacity (unit agnostic)
    recovery_rate=80.0,       # Recovery per rest cycle
    minimum_reserve=20.0      # Below this: degradation begins
)

# --- Create the accountant ---
account = EnergyAccountant(worker)

# --- Log energy transactions for one cycle ---

# Productive work (compensated)
account.add_transaction(EnergyTransaction(
    description="Primary task execution (compensated labor)",
    energy_delta=-40.0,
    is_compensated=True
))

# Compensation received
account.add_transaction(EnergyTransaction(
    description="Compensation received (wages/fuel/maintenance)",
    energy_delta=55.0,
    is_compensated=True
))

# --- Friction (uncompensated energy loss) ---

account.add_transaction(EnergyTransaction(
    description="Searching for equipment due to bad location data",
    energy_delta=-12.0,
    is_compensated=False,
    friction_category=FrictionCategory.INFORMATIONAL
))

account.add_transaction(EnergyTransaction(
    description="Waiting for infrastructure repair (deferred maintenance)",
    energy_delta=-8.0,
    is_compensated=False,
    friction_category=FrictionCategory.MAINTENANCE_DEFICIT
))

account.add_transaction(EnergyTransaction(
    description="Redundant procedural steps (legacy process)",
    energy_delta=-5.0,
    is_compensated=False,
    friction_category=FrictionCategory.PROCEDURAL
))

account.add_transaction(EnergyTransaction(
    description="Social overhead (navigating ego/political structures)",
    energy_delta=-3.0,
    is_compensated=False,
    friction_category=FrictionCategory.SOCIAL_OVERHEAD
))

# --- Register friction points with root causes ---

account.add_friction(FrictionPoint(
    description="Equipment location data does not match reality",
    category=FrictionCategory.INFORMATIONAL,
    energy_cost_per_cycle=12.0,
    cultural_narrative="Workers are slow and inefficient",
    functional_reality="Model/Reality dissonance — system map is wrong",
    root_cause_depth=3,
    upstream_causes=[
        "Location tracking system not maintained",
        "No accountability for data accuracy",
        "Decision-maker benefits from appearance of efficiency over actual efficiency"
    ]
))

account.add_friction(FrictionPoint(
    description="Equipment in disrepair blocks operational flow",
    category=FrictionCategory.MAINTENANCE_DEFICIT,
    energy_cost_per_cycle=8.0,
    cultural_narrative="Equipment failure is normal wear and tear",
    functional_reality="Deferred maintenance creating cascading blockages",
    root_cause_depth=2,
    upstream_causes=[
        "Maintenance budget allocated to other priorities",
        "Cost of downtime not attributed to maintenance deferral"
    ]
))

account.add_friction(FrictionPoint(
    description="Social position maintenance consuming operational energy",
    category=FrictionCategory.SOCIAL_OVERHEAD,
    energy_cost_per_cycle=3.0,
    cultural_narrative="Team dynamics require relationship management",
    functional_reality="Ego structures consuming energy without productive output",
    root_cause_depth=3,
    upstream_causes=[
        "Promotion criteria based on social capital not performance",
        "No measurement of social overhead cost",
        "Decision-makers embedded in social structure they benefit from"
    ]
))

# --- Run diagnosis ---
diagnosis = account.diagnose()

# --- Strip a sample narrative ---
narrative_result = NarrativeStripper.strip(
    "We have a worker shortage because people are lazy and unreliable. "
    "High turnover is just the cost of doing business in this industry."
)

# --- Additional stacked narrative example ---
stacked_narrative = NarrativeStripper.strip(
    "We've had burnout issues but honestly some of these workers are just "
    "unmotivated and lazy. The turnover is high but that's just how it is "
    "in this industry — it's an industry standard problem."
)

# --- Trace root cause ---
root_trace = RootCauseAnalyzer.trace(
    surface_event="Equipment found in wrong location with maintenance failures",
    layers=[
        {
            "description": "Operator spent 15 minutes locating equipment",
            "actor": "Operator",
            "constraint": "Bad location data",
            "energy_logic": "Cannot execute task without locating equipment",
            "is_actionable": False
        },
        {
            "description": "Location tracking system not updated",
            "actor": "Operations coordinator",
            "constraint": "No process for real-time tracking updates",
            "energy_logic": "Updating takes time; no consequence for not updating",
            "is_actionable": True
        },
        {
            "description": "No accountability for infrastructure data fidelity",
            "actor": "Management",
            "constraint": "Metrics focus on throughput, not data accuracy",
            "energy_logic": "Appearance of throughput rewarded over actual system health",
            "is_actionable": True
        },
        {
            "description": "Incentive structure rewards social position over system maintenance",
            "actor": "Organizational design",
            "constraint": "Promotion/evaluation criteria disconnected from operational reality",
            "energy_logic": "Decision-makers benefit from current structure remaining unexamined",
            "is_actionable": True
        }
    ]
)

# --- Output ---
print("=" * 70)
print("FUNCTIONAL EPISTEMOLOGY — SYSTEM DIAGNOSIS")
print("=" * 70)

print("\n--- ENERGY ACCOUNTING ---")
ea = diagnosis["energy_accounting"]
print(f"  Net Energy Balance:       {ea['net_balance']}")
print(f"  Total Friction Cost:      {ea['total_friction_cost']}")
print(f"  Compensated Output:       {ea['compensated_output']}")
print(f"  Friction Ratio:           {ea['friction_ratio']} "
      f"({ea['friction_ratio']*100:.1f}% of expenditure is waste)")
print(f"  Cycles Until Depletion:   {ea['cycles_until_depletion']}")

print(f"\n--- SYSTEM VERDICT ---")
print(f"  {diagnosis['system_verdict']}")

print(f"\n--- INVESTIGATION PRIORITIES ---")
for i, p in enumerate(diagnosis["investigation_priorities"], 1):
    print(f"  {i}. {p['target']}")
    print(f"     Cost: {p['energy_cost']} per cycle")
    print(f"     Reality: {p['investigate']}")
    print(f"     Root depth: {p['depth']} layers")

print(f"\n--- NARRATIVE ANALYSIS ---")
print(f"  Original: \"{narrative_result['original']}\"")
for analysis in narrative_result["functional_analysis"]:
    if "cultural_label" in analysis:
        print(f"\n  Cultural label: \"{analysis['cultural_label']}\"")
        print(f"  Energy reality: {analysis['energy_reality']}")
        print(f"  Next question:  {analysis['next_question']}")

if narrative_result["detected_stacks"]:
    print(f"\n  *** STACKING DETECTED ***")
    for stack in narrative_result["detected_stacks"]:
        print(f"  Stack: {stack['stack_name']}")
        print(f"  Matched: {stack['matched_components']}")
        print(f"  Strength: {stack['match_strength']*100:.0f}%")
        print(f"  Logic: {stack['stack_logic']}")
        print(f"  Wall function: {stack['wall_function']}")
        print(f"  Dismantle sequence:")
        for step in stack["dismantle_sequence"]:
            print(f"    → {step}")
    print(f"\n  WARNING: {narrative_result['stack_warning']}")

# --- Stacked narrative example ---
print(f"\n--- STACKED NARRATIVE ANALYSIS ---")
print(f"  Original: \"{stacked_narrative['original']}\"")
print(f"  Patterns found: {stacked_narrative['identified_patterns']}")
if stacked_narrative["detected_stacks"]:
    for stack in stacked_narrative["detected_stacks"]:
        print(f"\n  Stack: {stack['stack_name']}")
        print(f"  Matched: {stack['matched_components']}")
        print(f"  Strength: {stack['match_strength']*100:.0f}%")
        print(f"  Functional reality: {stack['functional_reality']}")
        print(f"  Dismantle sequence:")
        for step in stack["dismantle_sequence"]:
            print(f"    → {step}")
    print(f"\n  WARNING: {stacked_narrative['stack_warning']}")

print(f"\n--- ROOT CAUSE TRACE ---")
print(f"  Surface: {root_trace['surface_event']}")
for layer in root_trace["layers"]:
    marker = " >> ACTIONABLE" if layer["is_actionable"] else ""
    print(f"  Layer {layer['depth']}: {layer['description']}{marker}")
    print(f"    Actor: {layer['actor']}")
    print(f"    Energy logic: {layer['energy_logic']}")
print(f"\n  MISDIRECTION: {root_trace['cultural_misdirection']}")

# =================================================================
# SOCIAL OVERHEAD ANALYSIS
# =================================================================

overhead = SocialOverheadAccountant()

# --- Define role holders in the decision layer ---
overhead.add_role(RoleHolder(
    role_name="Operations Coordinator",
    position_type=PositionType.PERFORMANCE,
    decisions_per_cycle=20,
    productive_decisions=16,
    entropic_decisions=3,
    parasitic_decisions=1,
    energy_cost_to_system=15.0,
    energy_returned_to_system=22.0
))

overhead.add_role(RoleHolder(
    role_name="Site Manager",
    position_type=PositionType.SOCIAL_CAPITAL,
    decisions_per_cycle=15,
    productive_decisions=4,
    entropic_decisions=6,
    parasitic_decisions=5,
    energy_cost_to_system=25.0,
    energy_returned_to_system=10.0
))

overhead.add_role(RoleHolder(
    role_name="Senior Supervisor (Tenured)",
    position_type=PositionType.INERTIA,
    decisions_per_cycle=10,
    productive_decisions=3,
    entropic_decisions=5,
    parasitic_decisions=2,
    energy_cost_to_system=20.0,
    energy_returned_to_system=8.0
))

# --- Log overhead events ---
overhead.log_overhead_event(
    description="Experienced operator's safety concern dismissed by socially-positioned manager",
    category="expertise_silencing",
    energy_cost=7.0,
    would_not_occur_if="Decision authority weighted by domain expertise, not positional authority",
    visible_on_balance_sheet=False
)

overhead.log_overhead_event(
    description="Process change delayed 6 months to avoid conflict with tenured supervisor",
    category="comfort_maintenance",
    energy_cost=15.0,
    would_not_occur_if="Process changes evaluated on energy efficiency, not social disruption cost",
    visible_on_balance_sheet=False
)

overhead.log_overhead_event(
    description="Weekly status meetings consuming operator time to maintain management visibility",
    category="performance_theater",
    energy_cost=4.0,
    would_not_occur_if="Status derived from real-time system metrics, not verbal reporting",
    visible_on_balance_sheet=False
)

overhead.log_overhead_event(
    description="High-performing operator passed over for role; socially-connected candidate selected",
    category="signal_blocking",
    energy_cost=12.0,
    would_not_occur_if="Selection criteria based on measurable output and system contribution",
    visible_on_balance_sheet=False
)

overhead.log_overhead_event(
    description="Infrastructure repair request deprioritized to fund management offsite",
    category="comfort_maintenance",
    energy_cost=9.0,
    would_not_occur_if="Budget allocation weighted by friction-reduction ROI",
    visible_on_balance_sheet=True
)

# --- Run overhead audit ---
social_audit = overhead.audit()

print(f"\n{'=' * 70}")
print("SOCIAL OVERHEAD AUDIT")
print("=" * 70)

print(f"\n--- COST SUMMARY ---")
print(f"  Total Social Overhead:    {social_audit['total_social_overhead']}")
print(f"  Hidden (untracked) Cost:  {social_audit['hidden_cost']}")
print(f"  Hidden Cost Ratio:        {social_audit['hidden_cost_ratio']} "
      f"({social_audit['hidden_cost_ratio']*100:.1f}% of overhead is invisible)")

print(f"\n--- ROLE ANALYSIS ---")
for role in social_audit["role_analysis"]:
    print(f"\n  Role: {role['role']}")
    print(f"    Position maintained by: {role['position_maintained_by']}")
    print(f"    Decision efficiency:    {role['decision_efficiency']}")
    print(f"    Parasitic ratio:        {role['parasitic_ratio']}")
    print(f"    Net system value:       {role['net_system_value']}")
    print(f"    Verdict: {role['verdict']}")

print(f"\n--- OVERHEAD BY CATEGORY ---")
for cat, data in social_audit["overhead_by_category"].items():
    print(f"  {cat}:")
    print(f"    Total cost:   {data['total_cost']}")
    print(f"    Events:       {data['event_count']}")
    print(f"    Hidden:       {data['hidden_count']}/{data['event_count']}")

print(f"\n--- STRUCTURAL RECOMMENDATIONS (by energy recovered) ---")
for i, rec in enumerate(social_audit["structural_recommendations"], 1):
    print(f"  {i}. {rec['intervention']}")
    print(f"     Energy recovered: {rec['energy_recovered']}")

print("\n" + "=" * 70)
print("END DIAGNOSIS")
print("=" * 70)
```

if **name** == “**main**”:
example_analysis()
