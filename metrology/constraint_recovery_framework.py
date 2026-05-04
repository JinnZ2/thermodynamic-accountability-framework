"""
constraint_recovery_framework.py
=================================
Recover the physical constraints encoded in pre-1900 engineering
systems. Each system solved a real physical problem with a real
mechanism, validated by real failure costs. This framework
extracts those constraints into machine-readable form so they
can be re-used in modern design and audit work.

Core principle:
    Pre-1900 systems were not "traditional" or "primitive."
    They were constraint-satisfying engineering with embedded
    validation cycles. Recovering the constraints recovers the
    engineering knowledge.

SCHEMA VERSION
--------------
v0.2 (this file). Extends v0.1 with:
    - KnowledgeSystem and RecoveryProvenance dataclasses, so the
      epistemic frame and the reconstruction provenance travel
      with each constraint.
    - depends_on / enables fields for graph analysis.
    - evidence_class / evidence_quality / confidence_level for
      the v0.3 patch validators.
    - sensing_method / actuation_method / maintenance_method /
      transmission_method for explicit method descriptions.
    - physical_principle, boundary_conditions for physics
      grounding.
    - lag_time_weeks_typical + lag_time_weeks_range (replacing
      v0.1's single lag_time_weeks field).
    - applicability_assessment, supporting_references for
      transferability.
    - cost_metric_epoch so cost-of-failure currency is dated.

All v0.2 additions have defaults; existing seeded systems are
migrated in-place. Downstream consumers (the v0.3 patch validators
and metrology/constraint_to_seed.py estimators) operate against
this schema.

Structure per recovered constraint (v0.2):
    REQUIRED
        constraint_id           unique within registry
        name                    short identifier
        physical_trigger        what initiates the problem
        problem_solved          what fails without intervention
        solution_mechanism      how the system addresses it
        failure_mode            what happens if system fails
        cost_of_failure         validation: real consequence
        validation              historical record supporting it

    LAG TIMING (v0.2)
        lag_time_weeks_typical  representative response time
        lag_time_weeks_range    (low, high) tuple

    EVIDENCE (v0.2)
        evidence_class          observational class identifier
        evidence_quality        high / moderate / weak / contested
        confidence_level        in [0, 1]
        supporting_references   list of source pointers

    METHODS (v0.2)
        sensing_method          how the constraint is observed
        actuation_method        how the system acts on the constraint
        maintenance_method      how the system stays calibrated
        transmission_method     how the constraint knowledge propagates

    PHYSICS (v0.2)
        physical_principle      what physics is being applied
        boundary_conditions     dict of named bounds

    APPLICABILITY (v0.2)
        applicability_assessment    transferability statement

    GRAPH (v0.2)
        depends_on              constraint_ids this one depends on
        enables                 constraint_ids this one enables

    EPISTEMIC FRAME (v0.2)
        knowledge_system        KnowledgeSystem instance (or None)
        recovery_provenance     RecoveryProvenance instance (or None)

    BOOKKEEPING (v0.2)
        cost_metric_epoch       what era's currency / units the
                                cost-of-failure is in (e.g. "1900-USD")

stdlib only. CC0. github.com/JinnZ2
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
import json


SCHEMA_VERSION = "0.2.0"


# ---------------------------------------------------------------
# DATA STRUCTURES
# ---------------------------------------------------------------

@dataclass
class KnowledgeSystem:
    """
    The institutional / cultural / epistemic system within which
    this constraint was generated and validated.

    The word 'institution' has no stable cross-cultural referent;
    a US peer-review board, an Anishinaabe seasonal council, and a
    Persian qanat guild are all 'institutions' but none map to the
    same vector space. KnowledgeSystem forces explicit framing,
    paired with the v0.3 patch's InstitutionFrame dataclass for
    deeper specification when needed.
    """
    name: str
    ontology: str = ""                       # what the framework treats as real
    measurement_language: str = ""           # how the framework names quantities
    verification_method: str = ""            # how truth is established
    transmission_protocol: str = ""          # how knowledge propagates
    calibration_disruption_risks: str = ""   # what threatens calibration
    documented_outcomes: str = ""            # what has been observed
    institution_frame: Optional[Any] = None  # forward ref to InstitutionFrame


@dataclass
class RecoveryProvenance:
    """
    Tracks who recovered the constraint and what was lost in
    recovery. Critical for the seed metrology -- observer
    epistemology and observer absence both come from these fields.

    full_fidelity_preserved=True is a strong claim and the v0.3
    patch validator requires explicit descendant-community
    consultation evidence to back it up.
    """
    interpreter_epistemology: str = ""
    compression_losses: str = ""
    source_languages: List[str] = field(default_factory=list)
    known_missing_perspectives: List[str] = field(default_factory=list)
    full_fidelity_preserved: bool = False


@dataclass
class PhysicalConstraint:
    """A single recovered constraint from a pre-1900 system (v0.2)."""

    # ------- v0.1-required fields (no defaults) -------
    constraint_id: str
    name: str
    physical_trigger: str
    problem_solved: str
    solution_mechanism: str
    failure_mode: str
    cost_of_failure: str
    validation: str

    # ------- lag timing (v0.2 replaces v0.1 lag_time_weeks) -------
    lag_time_weeks_typical: float = 0.0
    lag_time_weeks_range: Tuple[float, float] = (0.0, 0.0)

    # ------- evidence (v0.2) -------
    evidence_class: str = ""
    evidence_quality: str = "moderate"  # high / moderate / weak / contested
    confidence_level: float = 0.5
    supporting_references: List[str] = field(default_factory=list)

    # ------- methods (v0.2) -------
    sensing_method: str = ""
    actuation_method: str = ""
    maintenance_method: str = ""
    transmission_method: str = ""

    # ------- physics (v0.2) -------
    physical_principle: str = ""
    boundary_conditions: Dict[str, str] = field(default_factory=dict)

    # ------- applicability (v0.2) -------
    applicability_assessment: str = ""

    # ------- dependency graph (v0.2) -------
    depends_on: List[str] = field(default_factory=list)
    enables: List[str] = field(default_factory=list)

    # ------- epistemic frame (v0.2) -------
    knowledge_system: Optional[KnowledgeSystem] = None
    recovery_provenance: Optional[RecoveryProvenance] = None

    # ------- bookkeeping (v0.2) -------
    cost_metric_epoch: str = ""


@dataclass
class RecoveredSystem:
    """A pre-1900 system with its constraints fully recovered."""
    system_id: str
    name: str
    period: str
    region: str
    measurements_recorded: dict = field(default_factory=dict)
    constraints: list = field(default_factory=list)
    notes: str = ""


# ---------------------------------------------------------------
# RECOVERY REGISTRY
# Each entry recovers the physical constraints of one system
# from the pre1900_engineering_registry.
# ---------------------------------------------------------------

RECOVERED_SYSTEMS = []


# Shared KnowledgeSystem / RecoveryProvenance instances per system.
# Constraints from the same system reference the same instance.

_anglo_milling_ks = KnowledgeSystem(
    name="Anglo-American milling tradition",
    ontology="watershed as engineered hydraulic system",
    measurement_language="head differential, flow, storage capacity",
    verification_method="economic survival of mill across flood seasons",
    transmission_protocol="apprenticeship + millwright treatises",
    calibration_disruption_risks=(
        "loss of millwright apprenticeship chain after rural electrification"
    ),
    documented_outcomes=(
        "centuries of operation across thousands of New England + "
        "Midwest watersheds"
    ),
)

_anishinaabe_burn_ks = KnowledgeSystem(
    name="Anishinaabe seasonal burn governance",
    ontology="forest as multi-generational fire-shaped landscape",
    measurement_language="phenology indicators + fuel-load + wildlife state",
    verification_method=(
        "multi-generational outcome tracking via ceremonial calendar; "
        "post-1850 suppression-era control evidence"
    ),
    transmission_protocol=(
        "oral ceremonial cycle + apprenticeship + seasonal songs"
    ),
    calibration_disruption_risks=(
        "transmission disruption from displacement and suppression"
    ),
    documented_outcomes=(
        "documented zero crown fires in managed stands across centuries"
    ),
)

_beaver_kinship_ks = KnowledgeSystem(
    name="Indigenous North American beaver-kinship hydrology",
    ontology="beaver as keystone hydraulic engineer + kin",
    measurement_language="dam density, baseflow stability, water table",
    verification_method=(
        "direct landscape observation across presence/absence of beaver"
    ),
    transmission_protocol="kinship-based knowledge holders + landscape literacy",
    calibration_disruption_risks="extirpation by fur trade 1600-1850",
    documented_outcomes=(
        "post-extirpation flood frequency 5-10x; modern BDA installations "
        "reproduce the pre-1850 hydrology"
    ),
)

_anglo_milling_rp = RecoveryProvenance(
    interpreter_epistemology="modern hydrologic engineering + historical mill records",
    compression_losses="qualitative apprentice judgment not in mill records",
    source_languages=["English"],
    known_missing_perspectives=[
        "millwright trade-secret knowledge lost post-1900",
        "downstream communities' observations of cascade effects",
    ],
    full_fidelity_preserved=False,
)

_anishinaabe_burn_rp = RecoveryProvenance(
    interpreter_epistemology="Western fire ecology + post-1990 cultural-burning literature",
    compression_losses="ceremonial structure + seasonal song content not in published record",
    source_languages=["English", "translated Anishinaabemowin"],
    known_missing_perspectives=[
        "no descendant-community review of this entry",
        "specific clan-level governance variations not represented",
    ],
    full_fidelity_preserved=False,
)

_beaver_kinship_rp = RecoveryProvenance(
    interpreter_epistemology="modern hydrology + ecological restoration literature",
    compression_losses=(
        "kinship-based relational protocols not capturable in engineering schema"
    ),
    source_languages=["English"],
    known_missing_perspectives=[
        "specific tribal knowledge systems vary regionally",
        "no descendant-community review of this entry",
    ],
    full_fidelity_preserved=False,
)


# ----- Mill Pond Cascade -----

mill_pond = RecoveredSystem(
    system_id="mill_pond_cascade",
    name="Mill Pond Cascade Hydrology",
    period="1750-1920",
    region="Upper Midwest (Wisconsin, Minnesota)",
    measurements_recorded={
        "water_level": "6-8 feet (seasonal)",
        "storage_duration": "8 months (April-November)",
        "outflow_rate": "2-4 ft/sec (controlled)",
        "fish_population": "stable (contemporary notes)",
    },
    constraints=[
        PhysicalConstraint(
            constraint_id="CP_001",
            name="seasonal_flood_prevention",
            physical_trigger="spring_snowmelt + rain (April-May)",
            problem_solved="catastrophic flooding without storage",
            solution_mechanism=(
                "pond absorbs 8-month supply, releases Oct-Nov"
            ),
            failure_mode="breached dam or overtopping -> flash flood",
            cost_of_failure=(
                "mill loss + downstream damage + recovery 2-3 years"
            ),
            validation=(
                "8 historical dam failures in region, "
                "avg repair cost 2.5 years income"
            ),
            lag_time_weeks_typical=8.0,
            lag_time_weeks_range=(4.0, 16.0),
            evidence_class="historical_records",
            evidence_quality="high",
            confidence_level=0.85,
            sensing_method="visual head-differential gauge + spillway level",
            actuation_method="sluice gate operation by miller",
            maintenance_method="annual inspection + post-storm walk",
            transmission_method="millwright apprenticeship",
            physical_principle="mass balance over watershed; storage attenuates pulse",
            boundary_conditions={
                "watershed_area_km2": "10-100",
                "mean_seasonal_flow_range": "2-4x",
            },
            applicability_assessment="directly transferable to similar watersheds",
            supporting_references=[
                "regional mill-record archives",
                "modern sponge-city research duplicating CP_001 logic",
            ],
            depends_on=[],
            enables=["CP_002"],
            knowledge_system=_anglo_milling_ks,
            recovery_provenance=_anglo_milling_rp,
            cost_metric_epoch="1850-1920 USD",
        ),
        PhysicalConstraint(
            constraint_id="CP_002",
            name="ground_storage_recovery",
            physical_trigger=(
                "summer drawdown (June-September) refills aquifer"
            ),
            problem_solved=(
                "well failures in drought (pre-pond, 3-4 per decade)"
            ),
            solution_mechanism=(
                "pond water infiltrates, raises water table 3-6 feet"
            ),
            failure_mode="dry wells -> no drinking water, no livestock",
            cost_of_failure=(
                "community relocation or 6-month water hauling"
            ),
            validation="post-pond: well failures drop to 0.3 per decade",
            lag_time_weeks_typical=24.0,
            lag_time_weeks_range=(12.0, 36.0),
            evidence_class="comparative_observation",
            evidence_quality="high",
            confidence_level=0.85,
            sensing_method="well levels + spring flow",
            actuation_method="passive infiltration through pond floor",
            maintenance_method="dredge to maintain pond floor permeability",
            transmission_method="community knowledge of well behavior",
            physical_principle="hydraulic head + soil hydraulic conductivity",
            boundary_conditions={
                "aquifer_type": "shallow unconfined",
            },
            applicability_assessment="transferable; depends on subsurface geology",
            supporting_references=["regional well-record archives"],
            depends_on=["CP_001"],
            enables=[],
            knowledge_system=_anglo_milling_ks,
            recovery_provenance=_anglo_milling_rp,
            cost_metric_epoch="1850-1920 USD",
        ),
        PhysicalConstraint(
            constraint_id="CP_003",
            name="fish_population_stability",
            physical_trigger="cold-water refuge during summer heat",
            problem_solved="warm-stream fish die-off in low-flow years",
            solution_mechanism=(
                "deep pond stratifies, bottom stays cold, "
                "fish refuge through August heat dome"
            ),
            failure_mode="pond too shallow or drawn too low -> die-off",
            cost_of_failure=(
                "loss of protein source for community + "
                "indicator species crash"
            ),
            validation=(
                "fish records continuous through 1750-1920 "
                "in pond-served watersheds; absent in drained ones"
            ),
            lag_time_weeks_typical=12.0,
            lag_time_weeks_range=(4.0, 24.0),
            evidence_class="comparative_observation",
            evidence_quality="moderate",
            confidence_level=0.70,
            sensing_method="seasonal fish presence + spawning surveys",
            actuation_method="maintain minimum pond depth",
            maintenance_method="dredging + spillway management",
            transmission_method="community fishing knowledge",
            physical_principle="thermal stratification + dissolved-oxygen balance",
            boundary_conditions={
                "minimum_depth_m": "2.5",
            },
            applicability_assessment="transferable to similar fish communities",
            supporting_references=["regional fish-record archives"],
            depends_on=["CP_001", "CP_002"],
            enables=[],
            knowledge_system=_anglo_milling_ks,
            recovery_provenance=_anglo_milling_rp,
            cost_metric_epoch="1850-1920 USD",
        ),
        PhysicalConstraint(
            constraint_id="CP_004",
            name="sediment_capture",
            physical_trigger="upland erosion during heavy rain",
            problem_solved="downstream channel siltation, navigation loss",
            solution_mechanism=(
                "pond settles sediment; periodic dredging "
                "returns it to fields as fertilizer"
            ),
            failure_mode=(
                "pond fills with sediment -> capacity loss -> "
                "constraint CP_001 fails next season"
            ),
            cost_of_failure="cascade failure of all four constraints",
            validation=(
                "dredging cycles documented at 7-12 year intervals "
                "in mill records; matches sediment yield calculations"
            ),
            lag_time_weeks_typical=2.0,
            lag_time_weeks_range=(0.0, 8.0),
            evidence_class="historical_records",
            evidence_quality="high",
            confidence_level=0.80,
            sensing_method="depth soundings",
            actuation_method="periodic dredging cycle",
            maintenance_method="dredge spoils returned to fields",
            transmission_method="millwright + farm community knowledge",
            physical_principle="Stokes settling + sediment-yield mass balance",
            boundary_conditions={
                "dredge_cycle_years": "7-12",
            },
            applicability_assessment="transferable",
            supporting_references=["mill-record dredge logs"],
            depends_on=["CP_001"],
            enables=["CP_001"],  # cyclic: cascade failure protection
            knowledge_system=_anglo_milling_ks,
            recovery_provenance=_anglo_milling_rp,
            cost_metric_epoch="1850-1920 USD",
        ),
    ],
    notes=(
        "Four constraints operate as coupled system. "
        "Failure of any one cascades. Modern 'sponge city' "
        "and 'distributed stormwater' research duplicates "
        "constraints CP_001 and CP_002 without crediting "
        "the prior art."
    ),
)
RECOVERED_SYSTEMS.append(mill_pond)


# ----- Anishinaabe Seasonal Burning -----

anishinaabe_burn = RecoveredSystem(
    system_id="anishinaabe_seasonal_burn",
    name="Anishinaabe Seasonal Burning Cycles",
    period="pre-contact through ~1850",
    region="Great Lakes, boreal-deciduous transition",
    measurements_recorded={
        "fuel_load": "kept below crown-fire threshold",
        "burn_frequency": "3-7 year cycle by stand type",
        "burn_timing": "phenology-indexed (plant indicators)",
        "wildlife_response": "tracked across 1-2 seasons",
    },
    constraints=[
        PhysicalConstraint(
            constraint_id="CB_001",
            name="fuel_load_management",
            physical_trigger="annual leaf litter + understory growth",
            problem_solved="crown-fire ignition during dry summer",
            solution_mechanism=(
                "low-intensity ground fire on 3-7 year cycle "
                "consumes ladder fuels before they bridge to canopy"
            ),
            failure_mode="missed cycle -> fuel accumulates -> crown fire",
            cost_of_failure=(
                "stand-replacing fire + soil sterilization + "
                "20-50 year recovery"
            ),
            validation=(
                "post-1850 suppression era: crown fire frequency "
                "increased 10-100x in same forest types"
            ),
            lag_time_weeks_typical=156.0,  # 3-year cycle minimum
            lag_time_weeks_range=(104.0, 364.0),  # 2-7 year cycle range
            evidence_class="suppression_era_comparison",
            evidence_quality="high",
            confidence_level=0.95,
            sensing_method="community observers assess understory density",
            actuation_method="authorized burn team ignites ground fire",
            maintenance_method="post-burn observation updates timeline",
            transmission_method="oral ceremonial cycle + apprenticeship",
            physical_principle="fuel ladder discontinuity",
            boundary_conditions={
                "forest_type": "pine/oak savanna",
                "ignition_source": "human-ignited",
            },
            applicability_assessment="directly transferable",
            supporting_references=[
                "post-1850 suppression: crown fire frequency up 10-100x",
            ],
            depends_on=[],
            enables=["CB_002", "CB_003"],
            knowledge_system=_anishinaabe_burn_ks,
            recovery_provenance=_anishinaabe_burn_rp,
            cost_metric_epoch="generational",
        ),
        PhysicalConstraint(
            constraint_id="CB_002",
            name="phenology_timing",
            physical_trigger=(
                "specific plant indicators reach defined stage"
            ),
            problem_solved=(
                "burning at wrong moisture/wind -> escape or "
                "incomplete burn"
            ),
            solution_mechanism=(
                "indicator species (e.g. specific bud stages, "
                "leaf-out timing) signal correct burn window"
            ),
            failure_mode="wrong-timing burn -> escape OR no effect",
            cost_of_failure=(
                "lost cycle (defer one year) OR uncontrolled fire"
            ),
            validation=(
                "phenology indicators map to modern fuel-moisture "
                "instrumentation within 10% accuracy"
            ),
            lag_time_weeks_typical=2.0,
            lag_time_weeks_range=(1.0, 4.0),
            evidence_class="instrument_concurrence",
            evidence_quality="high",
            confidence_level=0.88,
            sensing_method="phenology indicator observation",
            actuation_method="defer or proceed burn cycle",
            maintenance_method="track indicator species health year-over-year",
            transmission_method="seasonal songs + ceremonial calendar",
            physical_principle="fuel moisture content vs ignition energy",
            boundary_conditions={
                "indicator_species": "regional",
            },
            applicability_assessment="region-specific; indicators must be local",
            supporting_references=[
                "modern fuel-moisture instrumentation studies",
            ],
            depends_on=["CB_001"],
            enables=[],
            knowledge_system=_anishinaabe_burn_ks,
            recovery_provenance=_anishinaabe_burn_rp,
            cost_metric_epoch="generational",
        ),
        PhysicalConstraint(
            constraint_id="CB_003",
            name="wildlife_threshold_protection",
            physical_trigger="population density of indicator species",
            problem_solved=(
                "burning during nesting/denning -> population crash"
            ),
            solution_mechanism=(
                "burn deferred or relocated based on observed "
                "wildlife state; specific species act as red-light"
            ),
            failure_mode=(
                "ignored signal -> nest/den loss -> "
                "multi-year population recovery"
            ),
            cost_of_failure=(
                "loss of food source + ecosystem indicator + "
                "ceremonial obligation breach"
            ),
            validation=(
                "Indigenous burn timing documented to avoid "
                "sensitive periods; modern prescribed-burn programs "
                "now adopting same constraint after 30-year lag"
            ),
            lag_time_weeks_typical=8.0,
            lag_time_weeks_range=(2.0, 16.0),
            evidence_class="suppression_era_comparison",
            evidence_quality="moderate",
            confidence_level=0.80,
            sensing_method="wildlife population observation",
            actuation_method="burn deferral or relocation",
            maintenance_method="multi-year population tracking",
            transmission_method="ceremonial obligation + apprenticeship",
            physical_principle="wildlife population dynamics + fire avoidance",
            boundary_conditions={
                "indicator_species": "regional keystone species",
            },
            applicability_assessment="region-specific",
            supporting_references=[
                "modern prescribed-burn program adoption literature",
            ],
            depends_on=["CB_001"],
            enables=[],
            knowledge_system=_anishinaabe_burn_ks,
            recovery_provenance=_anishinaabe_burn_rp,
            cost_metric_epoch="generational",
        ),
    ],
    notes=(
        "Three constraints operating in coupled validation: "
        "fuel-load forces burn, phenology constrains timing, "
        "wildlife state can override. Multi-generational outcome "
        "tracking via ceremonial calendar."
    ),
)
RECOVERED_SYSTEMS.append(anishinaabe_burn)


# ----- Beaver-Managed Hydrology -----

beaver_hydrology = RecoveredSystem(
    system_id="beaver_managed_hydrology",
    name="Beaver-Managed Watershed Hydrology",
    period="pre-contact through 1600-1850 fur trade extirpation",
    region="continent-wide pre-1700",
    measurements_recorded={
        "dam_density": "1 dam per 0.5-1 km of stream",
        "baseflow_stability": "year-round flow even in drought",
        "water_table_elevation": "3-10 feet higher than post-extirpation",
        "riparian_biomass": "5-20x higher than current 'natural' baseline",
    },
    constraints=[
        PhysicalConstraint(
            constraint_id="CH_001",
            name="flood_pulse_attenuation",
            physical_trigger="storm event or snowmelt pulse",
            problem_solved="downstream flash flooding",
            solution_mechanism=(
                "stepped dam network spreads pulse across "
                "hundreds of small impoundments, releases gradually"
            ),
            failure_mode=(
                "dam network removed -> all pulses pass through "
                "directly -> downstream flood frequency 5-10x higher"
            ),
            cost_of_failure=(
                "downstream infrastructure damage + "
                "channel incision + sediment loss"
            ),
            validation=(
                "post-extirpation flood records show step-change "
                "increase in peak flows; modern BDA installations "
                "reproduce attenuation"
            ),
            lag_time_weeks_typical=4.0,
            lag_time_weeks_range=(1.0, 12.0),
            evidence_class="extirpation_comparison",
            evidence_quality="high",
            confidence_level=0.90,
            sensing_method="downstream gauge records",
            actuation_method="passive: dam network impoundment",
            maintenance_method="beaver population health",
            transmission_method="beaver kinship traditions",
            physical_principle="distributed storage attenuates flood pulse",
            boundary_conditions={
                "dam_density_per_km": "1-2",
            },
            applicability_assessment="directly transferable via BDAs",
            supporting_references=[
                "post-extirpation flood records",
                "modern BDA installation studies",
            ],
            depends_on=[],
            enables=["CH_002", "CH_003"],
            knowledge_system=_beaver_kinship_ks,
            recovery_provenance=_beaver_kinship_rp,
            cost_metric_epoch="generational",
        ),
        PhysicalConstraint(
            constraint_id="CH_002",
            name="drought_baseflow_maintenance",
            physical_trigger="precipitation deficit (months)",
            problem_solved="stream drying, fish kill, well failure",
            solution_mechanism=(
                "wetland storage releases water through dry season; "
                "raised water table sustains adjacent springs"
            ),
            failure_mode=(
                "no storage -> stream goes dry -> fish kill + "
                "well failures within 60-90 days of last rain"
            ),
            cost_of_failure=(
                "loss of riparian ecosystem + livestock water + "
                "domestic water"
            ),
            validation=(
                "current pre-1850 streams with restored beaver "
                "show 3-5x longer flow persistence than control"
            ),
            lag_time_weeks_typical=16.0,
            lag_time_weeks_range=(8.0, 36.0),
            evidence_class="restoration_comparison",
            evidence_quality="high",
            confidence_level=0.85,
            sensing_method="baseflow gauge + well-level observation",
            actuation_method="passive: wetland storage release",
            maintenance_method="beaver population health",
            transmission_method="beaver kinship traditions",
            physical_principle="surface storage + raised water table",
            boundary_conditions={
                "watershed_type": "perennial stream",
            },
            applicability_assessment="transferable in similar climate / geology",
            supporting_references=[
                "modern beaver-restoration baseflow studies",
            ],
            depends_on=["CH_001"],
            enables=[],
            knowledge_system=_beaver_kinship_ks,
            recovery_provenance=_beaver_kinship_rp,
            cost_metric_epoch="generational",
        ),
        PhysicalConstraint(
            constraint_id="CH_003",
            name="sediment_and_nutrient_cycling",
            physical_trigger="upland runoff carrying sediment + nutrients",
            problem_solved=(
                "downstream eutrophication + channel siltation + "
                "soil loss from uplands"
            ),
            solution_mechanism=(
                "pond network captures sediment + nutrients, "
                "feeds wetland productivity, returns organic material "
                "to soil through periodic dam abandonment"
            ),
            failure_mode=(
                "no capture -> nutrients flush to lakes -> "
                "algae blooms; sediment fills downstream reservoirs"
            ),
            cost_of_failure=(
                "reservoir capacity loss + drinking water "
                "contamination + fishery collapse"
            ),
            validation=(
                "modern beaver-restored systems show 50-90% "
                "reduction in downstream sediment and N export"
            ),
            lag_time_weeks_typical=52.0,
            lag_time_weeks_range=(12.0, 156.0),
            evidence_class="restoration_comparison",
            evidence_quality="high",
            confidence_level=0.85,
            sensing_method="downstream nutrient + sediment monitoring",
            actuation_method="passive: pond settling + wetland uptake",
            maintenance_method="beaver population health",
            transmission_method="beaver kinship traditions",
            physical_principle="settling + biological uptake + dam abandonment cycling",
            boundary_conditions={
                "watershed_load": "moderate to high",
            },
            applicability_assessment="transferable in similar watersheds",
            supporting_references=[
                "modern beaver-restoration nutrient studies",
            ],
            depends_on=["CH_001"],
            enables=[],
            knowledge_system=_beaver_kinship_ks,
            recovery_provenance=_beaver_kinship_rp,
            cost_metric_epoch="generational",
        ),
    ],
    notes=(
        "Pre-1850 hydrology baseline is post-extirpation, NOT "
        "natural. Modern 'natural flow regime' research builds "
        "on a corrupted baseline. Constraint CH_002 in particular "
        "explains why drought trends since 1850 may be measuring "
        "beaver loss as much as climate."
    ),
)
RECOVERED_SYSTEMS.append(beaver_hydrology)


# ---------------------------------------------------------------
# QUERY FUNCTIONS
# ---------------------------------------------------------------

def find_system(system_id: str) -> Optional[RecoveredSystem]:
    """Return the recovered system with matching ID."""
    for s in RECOVERED_SYSTEMS:
        if s.system_id == system_id:
            return s
    return None


def find_constraint(constraint_id: str) -> Optional[PhysicalConstraint]:
    """Return the constraint with matching ID across all systems."""
    for s in RECOVERED_SYSTEMS:
        for c in s.constraints:
            if c.constraint_id == constraint_id:
                return c
    return None


def find_constraints_by_problem(keyword: str) -> list:
    """Find all constraints across all systems matching a problem keyword."""
    keyword_lower = keyword.lower()
    matches = []
    for system in RECOVERED_SYSTEMS:
        for c in system.constraints:
            if (keyword_lower in c.problem_solved.lower() or
                    keyword_lower in c.name.lower()):
                matches.append({
                    "system": system.name,
                    "constraint": c.name,
                    "problem": c.problem_solved,
                    "mechanism": c.solution_mechanism,
                })
    return matches


def coupled_failure_analysis(system_id: str) -> dict:
    """
    Identify cascade failure paths within a recovered system.
    Returns each constraint plus what depends on it.
    """
    system = find_system(system_id)
    if not system:
        return {"error": f"system {system_id} not found"}

    return {
        "system": system.name,
        "constraint_count": len(system.constraints),
        "cascade_risk": (
            "high" if len(system.constraints) >= 3 else "moderate"
        ),
        "constraints": [
            {
                "id": c.constraint_id,
                "name": c.name,
                "lag_weeks_typical": c.lag_time_weeks_typical,
                "lag_weeks_range": list(c.lag_time_weeks_range),
                "failure_mode": c.failure_mode,
                "depends_on": list(c.depends_on),
                "enables": list(c.enables),
            }
            for c in system.constraints
        ],
        "notes": system.notes,
    }


def export_recovered_system(system_id: str) -> str:
    """Export a recovered system as JSON for cross-AI use."""
    system = find_system(system_id)
    if not system:
        return json.dumps({"error": f"system {system_id} not found"})
    return json.dumps(asdict(system), indent=2, default=str)


def export_all() -> str:
    """Export all recovered systems as JSON."""
    return json.dumps(
        [asdict(s) for s in RECOVERED_SYSTEMS],
        indent=2,
        default=str,
    )


# ---------------------------------------------------------------
# DEMO
# ---------------------------------------------------------------

if __name__ == "__main__":
    print(f"=== constraint_recovery_framework SCHEMA_VERSION={SCHEMA_VERSION} ===\n")

    print("=== MILL POND CONSTRAINT RECOVERY ===\n")
    mp = find_system("mill_pond_cascade")
    print(f"SYSTEM: {mp.system_id}")
    print(f"PERIOD: {mp.period}")
    print(f"REGION: {mp.region}\n")

    print("MEASUREMENTS RECORDED:")
    for k, v in mp.measurements_recorded.items():
        print(f"  {k}: {v}")
    print()

    print("CONSTRAINT RECOVERY (CP_001 sample):")
    print(json.dumps(asdict(mp.constraints[0]), indent=2, default=str))
    print()

    print("=== CROSS-SYSTEM PROBLEM SEARCH: 'flood' ===")
    matches = find_constraints_by_problem("flood")
    for m in matches:
        print(f"  {m['system']} -> {m['constraint']}")
        print(f"    problem: {m['problem']}")
        print(f"    mechanism: {m['mechanism']}\n")

    print("=== CASCADE FAILURE ANALYSIS: beaver hydrology ===")
    print(json.dumps(
        coupled_failure_analysis("beaver_managed_hydrology"),
        indent=2,
    ))
