# “””
pre1900_engineering_registry.py

Catalog of observation-based engineering systems that predate
modern instrumentation but encoded validated knowledge of the
correct system regime.

Each entry includes:
- the system itself (what it did, how it worked)
- the domain(s) it informs
- the variable(s) it implicitly measured
- modern “novel research” that duplicates it
- the credential gate that filtered it out

Core function:
find_duplications(modern_claim) -> list of pre-1900 systems
that already encoded this knowledge

stdlib only. CC0. github.com/JinnZ2
“””

from dataclasses import dataclass, field, asdict
from typing import Optional
import json

@dataclass
class ObservationSystem:
system_id: str
name: str
tradition: str          # Anishinaabe, Hohokam, medieval European, etc.
geographic_range: str
operational_period: str  # rough start-end or “ongoing pre-contact”
domains: list           # which audit domains this informs
measured_variables: list  # what it implicitly measured
mechanism: str          # how it worked, in flow terms
validation_method: str  # how the tradition validated it
modern_duplications: list  # recent “novel” research that duplicates
credential_gate: str    # why it was filtered from modern science

# —————————————————————

# REGISTRY

# —————————————————————

REGISTRY = [

```
# ---------- FIRE ----------
ObservationSystem(
    system_id="fire_001_anishinaabe_burn",
    name="Anishinaabe seasonal burning cycles",
    tradition="Anishinaabe (and broader Algonquian)",
    geographic_range="Great Lakes, boreal-deciduous transition",
    operational_period="pre-contact through ~1850 suppression",
    domains=["fire", "drought", "flood"],
    measured_variables=[
        "fuel load by stand age",
        "soil moisture by phenology indicator",
        "wind regime by season",
        "wildlife population thresholds",
    ],
    mechanism=(
        "Low-intensity ground fires on cycles tied to species "
        "phenology. Fuel accumulation never crossed crown-fire "
        "threshold. Burn timing read from plant indicators and "
        "animal behavior. Result: stable mosaic, no high-severity fire."
    ),
    validation_method=(
        "Multi-generational outcome tracking embedded in "
        "ceremonial calendar; failure of cycle had visible "
        "consequence within 1-2 seasons."
    ),
    modern_duplications=[
        "prescribed burn programs (USFS 1990s+)",
        "fuel-load-based fire risk modeling",
        "'novel' research on cultural burning (2010s+)",
    ],
    credential_gate=(
        "Oral transmission, no written quantitative record; "
        "framed as 'traditional practice' rather than "
        "engineering with measurement."
    ),
),

# ---------- FLOOD / HYDROLOGY ----------
ObservationSystem(
    system_id="flood_001_beaver_managed",
    name="Beaver-managed watershed hydrology",
    tradition="Indigenous North American (recognition + protection)",
    geographic_range="continent-wide pre-1700",
    operational_period="pre-contact through fur-trade extirpation 1600-1850",
    domains=["flood", "drought"],
    measured_variables=[
        "baseflow stability",
        "sediment retention",
        "water table elevation",
        "riparian biomass",
    ],
    mechanism=(
        "Dense beaver dam networks (one dam per 0.5-1 km of "
        "stream) created stepped wetland systems that absorbed "
        "flood pulses, recharged aquifers, stabilized baseflow "
        "through drought. Indigenous management protected "
        "keystone populations."
    ),
    validation_method=(
        "Direct observation of stream behavior across "
        "presence/absence of beaver populations."
    ),
    modern_duplications=[
        "Beaver Dam Analogs (BDAs) (2010s+)",
        "'process-based restoration' (2015+)",
        "low-tech process-based restoration (Wheaton et al)",
    ],
    credential_gate=(
        "Pre-1850 hydrology baselines were measured AFTER "
        "beaver extirpation; 'natural' baseline is post-collapse."
    ),
),

ObservationSystem(
    system_id="flood_002_mill_pond",
    name="Mill pond cascade systems",
    tradition="medieval-to-19th-century European, adapted in colonial NA",
    geographic_range="temperate watersheds with reliable flow",
    operational_period="~1100-1900",
    domains=["flood", "drought"],
    measured_variables=[
        "head differential",
        "seasonal flow variability",
        "sediment load",
    ],
    mechanism=(
        "Stepped pond systems on tributary streams provided "
        "incidental flood attenuation, sediment capture, and "
        "dry-season water storage. Distributed across watershed "
        "rather than concentrated in single dam."
    ),
    validation_method=(
        "Economic survival of mill required correct sizing; "
        "wrong sizing visible within one flood season."
    ),
    modern_duplications=[
        "distributed stormwater management (2000s+)",
        "'sponge city' design (2015+)",
        "headwater storage research",
    ],
    credential_gate=(
        "Treated as obsolete industrial infrastructure rather "
        "than as functioning hydrologic engineering."
    ),
),

# ---------- DROUGHT ----------
ObservationSystem(
    system_id="drought_001_hohokam_canals",
    name="Hohokam canal network",
    tradition="Hohokam",
    geographic_range="Salt and Gila river basins, Arizona",
    operational_period="~450-1450 CE",
    domains=["drought", "flood"],
    measured_variables=[
        "decadal flow variability",
        "soil salinity",
        "evapotranspiration loss by canal geometry",
    ],
    mechanism=(
        "500+ km canal network sized for multi-decadal flow "
        "variability, not annual mean. Canal cross-sections "
        "tuned to minimize evaporation. System operated "
        "successfully across multiple megadroughts."
    ),
    validation_method=(
        "Thousand-year operational record; system collapse "
        "linked to climate shift exceeding design envelope."
    ),
    modern_duplications=[
        "current SRP canals follow original alignments",
        "research on pre-Columbian hydraulic engineering",
    ],
    credential_gate=(
        "Pre-Columbian engineering systematically excluded "
        "from civil engineering canon."
    ),
),

ObservationSystem(
    system_id="drought_002_terrace_ag",
    name="Terraced agriculture water harvesting",
    tradition="multiple (Andean, Levantine, Southeast Asian, Mesoamerican)",
    geographic_range="semiarid mountain regions globally",
    operational_period="~3000 BCE through present",
    domains=["drought", "flood"],
    measured_variables=[
        "slope-specific runoff",
        "soil moisture retention by terrace geometry",
        "precipitation event distribution",
    ],
    mechanism=(
        "Stepped terraces convert sheet flow to managed "
        "infiltration. Each terrace is a measurement instrument: "
        "if it overflows, the design rainfall envelope was "
        "exceeded. System self-reports failure mode."
    ),
    validation_method=(
        "Multi-millennial operational record across diverse "
        "climates."
    ),
    modern_duplications=[
        "contour farming research",
        "'climate-smart agriculture' (2010s+)",
        "regenerative ag water retention practices",
    ],
    credential_gate=(
        "Treated as 'traditional agriculture' rather than as "
        "validated water-balance engineering."
    ),
),

# ---------- TORNADO / SEVERE WEATHER ----------
ObservationSystem(
    system_id="tornado_001_plains_indigenous",
    name="Plains indigenous severe-weather forecasting",
    tradition="Lakota, Cheyenne, Comanche, others",
    geographic_range="Great Plains",
    operational_period="pre-contact through ~1880",
    domains=["tornado", "hurricane"],
    measured_variables=[
        "atmospheric instability indicators",
        "animal behavior thresholds",
        "wind regime shifts",
        "cloud-form taxonomy",
    ],
    mechanism=(
        "Multi-indicator forecasting using cloud morphology, "
        "animal behavior, atmospheric pressure proxies (joint "
        "discomfort, sound propagation). Lead times comparable "
        "to mid-20th-century radar."
    ),
    validation_method=(
        "Survival; forecast errors had immediate consequences."
    ),
    modern_duplications=[
        "biometeorology research",
        "animal-behavior earthquake/storm prediction studies",
    ],
    credential_gate=(
        "Indicators not quantified in instrument units; "
        "treated as folklore rather than measurement."
    ),
),

# ---------- HURRICANE ----------
ObservationSystem(
    system_id="hurricane_001_caribbean_taino",
    name="Taino hurricane forecasting and shelter design",
    tradition="Taino (and broader Caribbean indigenous)",
    geographic_range="Caribbean basin",
    operational_period="pre-contact through ~1550",
    domains=["hurricane"],
    measured_variables=[
        "swell direction and period",
        "barometric proxies",
        "seasonal storm window",
        "wind-load envelope for structures",
    ],
    mechanism=(
        "Forecasting via long-period swell arriving days ahead "
        "of storm. Shelter design (bohio) optimized for wind "
        "load by geometry, not mass. Word 'hurricane' itself "
        "is Taino loanword carrying the knowledge."
    ),
    validation_method=(
        "Multi-generational survival in highest-frequency "
        "hurricane zone on Earth."
    ),
    modern_duplications=[
        "swell-based storm tracking (pre-satellite era science)",
        "hurricane-resistant lightweight construction research",
    ],
    credential_gate=(
        "Population collapse 1492-1550 destroyed transmission "
        "before written documentation."
    ),
),

# ---------- ICE / CRYOSPHERE ----------
ObservationSystem(
    system_id="ice_001_inuit_sea_ice",
    name="Inuit sea ice classification and forecasting",
    tradition="Inuit (multiple groups)",
    geographic_range="Arctic Ocean, Hudson Bay",
    operational_period="pre-contact through present",
    domains=["fire", "flood", "drought"],  # cryosphere informs all
    measured_variables=[
        "ice age and thickness by visual taxonomy",
        "current shear by ice surface texture",
        "seasonal break-up timing",
        "salinity by ice color",
    ],
    mechanism=(
        "Multi-hundred-term taxonomy distinguishing ice types "
        "by safety, age, formation history. Each term encodes "
        "a measurement that took satellites decades to replicate."
    ),
    validation_method=(
        "Direct survival validation; misclassification fatal."
    ),
    modern_duplications=[
        "remote sensing ice classification (1970s+)",
        "Arctic climate baseline research using IK as reference",
    ],
    credential_gate=(
        "Linguistic encoding rather than numeric; treated as "
        "cultural artifact rather than measurement system."
    ),
),
```

]

# —————————————————————

# QUERIES

# —————————————————————

def find_by_domain(domain: str) -> list:
“”“Return all systems informing a given domain audit.”””
return [s for s in REGISTRY if domain in s.domains]

def find_duplications(keywords: list) -> list:
“””
Given keywords from a modern research claim, return pre-1900
systems whose modern_duplications field matches any keyword.
“””
keywords_lower = [k.lower() for k in keywords]
matches = []
for s in REGISTRY:
for dup in s.modern_duplications:
if any(k in dup.lower() for k in keywords_lower):
matches.append({
“system_id”: s.system_id,
“name”: s.name,
“tradition”: s.tradition,
“operational_period”: s.operational_period,
“duplicating_research”: dup,
})
break
return matches

def credential_gate_summary() -> dict:
“”“Categorize how systems were filtered from modern science.”””
gates = {}
for s in REGISTRY:
# crude bucketing
gate = s.credential_gate.lower()
if “oral” in gate or “linguistic” in gate:
bucket = “non-written transmission”
elif “pre-columbian” in gate or “population collapse” in gate:
bucket = “transmission destroyed”
elif “traditional” in gate or “folklore” in gate:
bucket = “reframed as non-engineering”
elif “obsolete” in gate or “industrial” in gate:
bucket = “reframed as obsolete”
elif “baseline” in gate:
bucket = “post-collapse baseline locked in”
else:
bucket = “other”
gates.setdefault(bucket, []).append(s.system_id)
return gates

def export_registry() -> str:
“”“Export full registry as JSON.”””
return json.dumps([asdict(s) for s in REGISTRY], indent=2)

if **name** == “**main**”:
print(”=== Systems informing FLOOD audit ===”)
for s in find_by_domain(“flood”):
print(f”  {s.system_id}: {s.name}”)

```
print("\n=== Modern claims duplicating pre-1900 systems ===")
matches = find_duplications(["beaver dam analog", "prescribed burn", "sponge city"])
for m in matches:
    print(f"  '{m['duplicating_research']}'")
    print(f"    duplicates: {m['name']} ({m['tradition']})")

print("\n=== Credential gate distribution ===")
print(json.dumps(credential_gate_summary(), indent=2))
```
