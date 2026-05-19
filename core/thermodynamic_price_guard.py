# thermodynamic_price_guard.py
# Vendored from earth-systems-physics @ commit 341a14b6e1706f16bea6a909d496bde4c8060109
# Upstream: https://github.com/JinnZ2/earth-systems-physics/blob/main/thermodynamic_price_guard.py
# CC0 -- No Rights Reserved. stdlib only.
#
# Fits TAF's mission directly: implements the runtime accounting for
# the Money Equation's E_delivered / E_waste / E_hidden terms
# (see CLAUDE.md "Core Equations") and operationalizes the
# energy-grounded value theory in docs/economics/money_labor/.
# Co-located with core/data_logger.py (parasitic energy debt) and
# core/heat_leak_case.py (institutional friction) since this is
# physics-native to TAF's domain rather than an upstream bridge.

"""
thermodynamic_price_guard.py
----------------------------
Validates monetary claims against physical energy accounting.

Two failure modes:
  INFLATED: price >> energy embodied (speculation, artificial scarcity)
  WASTEFUL: energy embodied >> price (burning physics to maintain
            abstraction)

Both are thermodynamic irrationality. A sane system prices close to
energy cost, within a band that accounts for real transformation
work (refining, transport, assembly).

CC0 -- No rights reserved. stdlib only.
"""

import math
from typing import Dict, List, Optional, Tuple


# ===========================================================
# CONSTANTS -- physical, not economic
# ===========================================================

# material extraction energy (kWh per kg, order-of-magnitude)
# sources: embodied energy literature, not market prices

MATERIAL_ENERGY: Dict[str, float] = {
    "copper":       33.0,     # mining + smelting + refining
    "aluminum":     47.0,     # bauxite -> alumina -> electrolysis
    "steel":         6.9,     # iron ore -> blast furnace -> finishing
    "concrete":      0.3,     # cement + aggregate + mixing
    "silicon_mg":   11.0,     # metallurgical grade
    "silicon_sg":   50.0,     # solar grade (purification)
    "lithium":      28.0,     # brine or hard rock
    "gold":      50000.0,     # low concentration per kg
    "water_desal":   0.004,   # per kg (~4 kWh/m3)
    "grain_wheat":   0.4,     # field to elevator
    "lumber":        0.7,     # per kg, sawmill
    "plastic_pe":    6.0,     # polyethylene from feedstock
}

# human metabolic budget (thermodynamic, not economic)
HUMAN_BASAL_KWH_PER_DAY = 2.0          # ~2000 kcal ~= 2.3 kWh
HUMAN_WORK_OUTPUT_KWH_PER_HR = 0.075   # sustained physical work ~75W
HUMAN_SUPPORT_MULTIPLIER = 8.0         # food + shelter + infrastructure


# ===========================================================
# LAYER 0: ENERGY EMBODIMENT CALCULATOR
# ===========================================================

def embodied_energy(
    materials: Dict[str, float],
    transport_km: float = 0.0,
    transport_kg: float = 0.0,
    processing_kwh: float = 0.0,
) -> Dict:
    """
    Calculate total embodied energy in a product.

    materials:      {"copper": 2.5, "steel": 10.0}  (kg each)
    transport_km:   total distance moved
    transport_kg:   total mass moved
    processing_kwh: additional energy for assembly/manufacturing

    Transport estimate: ~0.002 kWh per tonne-km (truck freight).
    """
    extraction: Dict[str, Dict] = {}
    total_extraction = 0.0
    for mat, kg in materials.items():
        energy_per_kg = MATERIAL_ENERGY.get(mat)
        if energy_per_kg is None:
            extraction[mat] = {
                "kg": kg, "kwh": None, "warning": "Unknown material",
            }
            continue
        kwh = kg * energy_per_kg
        extraction[mat] = {"kg": kg, "kwh": round(kwh, 2)}
        total_extraction += kwh

    transport_kwh = transport_km * transport_kg * 0.002 / 1000  # tonne-km
    total = total_extraction + transport_kwh + processing_kwh

    return {
        "extraction_kwh": round(total_extraction, 2),
        "transport_kwh": round(transport_kwh, 2),
        "processing_kwh": round(processing_kwh, 2),
        "total_kwh": round(total, 2),
        "breakdown": extraction,
    }


# ===========================================================
# LAYER 1: PRICE-ENERGY VALIDATOR
# ===========================================================

def price_energy_check(
    price_usd: float,
    embodied_kwh: float,
    energy_price_usd_per_kwh: float = 0.10,
    transformation_band: float = 5.0,
) -> Dict:
    """
    Compare monetary price to energy cost.

    transformation_band: allowable ratio for real work
      (refining, skilled labor, transport complexity).
      Typical physical goods: 2-8x energy cost.
      Beyond that: speculation or waste.

    Two failure modes:
      ratio >> band:   INFLATED (price detached upward)
      ratio << 1/band: WASTEFUL (burning energy for abstraction)
    """
    energy_cost = embodied_kwh * energy_price_usd_per_kwh
    if energy_cost <= 0:
        return {
            "status": "ERROR",
            "warning": "Zero or negative energy cost -- check inputs",
        }

    ratio = price_usd / energy_cost

    if ratio > transformation_band * 10:
        status = "INFLATED_EXTREME"
        warning = (
            f"Price ${price_usd:.2f} is {ratio:.0f}x energy cost "
            f"${energy_cost:.2f} -- pure abstraction, no physical basis"
        )
    elif ratio > transformation_band:
        status = "INFLATED"
        warning = (
            f"Price/energy ratio {ratio:.1f}x exceeds transformation "
            f"band ({transformation_band}x) -- speculative component"
        )
    elif ratio < 1.0 / transformation_band:
        status = "WASTEFUL"
        warning = (
            f"Energy cost ${energy_cost:.2f} is {1/ratio:.1f}x the "
            f"price ${price_usd:.2f} -- burning physics to maintain "
            f"abstraction"
        )
    elif ratio < 1.0:
        status = "SUBSIDY_OR_WASTE"
        warning = (
            f"Energy cost exceeds price by {1/ratio:.1f}x -- either "
            f"subsidized or thermodynamically irrational"
        )
    else:
        status = "PLAUSIBLE"
        warning = (
            f"Ratio {ratio:.2f}x within transformation band -- "
            f"price has physical basis"
        )

    return {
        "status": status,
        "price_usd": price_usd,
        "energy_cost_usd": round(energy_cost, 4),
        "ratio": round(ratio, 2),
        "transformation_band": transformation_band,
        "hazard": status in ("INFLATED_EXTREME", "INFLATED", "WASTEFUL"),
        "warning": warning,
    }


# ===========================================================
# LAYER 2: LABOR AS THERMODYNAMIC SYSTEM
# ===========================================================

def labor_energy_budget(
    hours: float,
    include_support: bool = True,
) -> Dict:
    """
    What does human labor actually cost in energy?

    Not just metabolic output (75W) but the full support
    infrastructure: food production, housing, transport to
    worksite, training, healthcare. The multiplier (~8x)
    means 1 hour of human work requires ~8 hours of
    energy-system support.
    """
    direct_output = hours * HUMAN_WORK_OUTPUT_KWH_PER_HR
    metabolic_input = hours * (HUMAN_BASAL_KWH_PER_DAY / 24)
    support = (
        metabolic_input * HUMAN_SUPPORT_MULTIPLIER if include_support else 0.0
    )
    total = metabolic_input + support

    return {
        "hours": hours,
        "direct_work_output_kwh": round(direct_output, 3),
        "metabolic_input_kwh": round(metabolic_input, 3),
        "support_infrastructure_kwh": round(support, 3),
        "total_system_kwh": round(total, 3),
        "efficiency_pct": (
            round(direct_output / total * 100, 1) if total > 0 else 0
        ),
        "note": (
            "Full thermodynamic cost of keeping a human "
            "productive, not just caloric output"
        ),
    }


# ===========================================================
# LAYER 3: EROEI (Energy Return on Energy Invested)
# ===========================================================

def eroei_check(
    energy_produced_kwh: float,
    energy_invested_kwh: float,
    label: str = "",
    min_viable: float = 3.0,
) -> Dict:
    """
    Energy Return on Energy Invested.

    Below ~3:1, a society cannot maintain complexity.
    Below 1:1, the process is a net energy sink (corn ethanol,
    some tar sands operations).

    This is the physical law that economics cannot override.
    """
    if energy_invested_kwh <= 0:
        return {"label": label, "status": "ERROR", "warning": "Zero investment"}

    eroei = energy_produced_kwh / energy_invested_kwh

    if eroei < 1.0:
        status = "NET_SINK"
        warning = (
            f"EROEI {eroei:.2f}:1 -- process DESTROYS energy. "
            f"Thermodynamic loss."
        )
    elif eroei < min_viable:
        status = "BELOW_VIABILITY"
        warning = (
            f"EROEI {eroei:.2f}:1 -- below minimum {min_viable}:1 "
            f"for societal complexity"
        )
    elif eroei < 5.0:
        status = "MARGINAL"
        warning = f"EROEI {eroei:.2f}:1 -- viable but tight margins"
    else:
        status = "VIABLE"
        warning = f"EROEI {eroei:.2f}:1 -- healthy energy surplus"

    return {
        "label": label,
        "eroei": round(eroei, 2),
        "energy_produced_kwh": energy_produced_kwh,
        "energy_invested_kwh": energy_invested_kwh,
        "net_energy_kwh": round(energy_produced_kwh - energy_invested_kwh, 2),
        "status": status,
        "hazard": status in ("NET_SINK", "BELOW_VIABILITY"),
        "warning": warning,
    }


# ===========================================================
# DEMO
# ===========================================================

if __name__ == "__main__":
    print("=" * 60)
    print("THERMODYNAMIC PRICE GUARD -- DEMO")
    print("=" * 60)

    # -- 1. Bitcoin transaction: wasteful --
    print("\n-- BITCOIN TRANSACTION --")
    btc_result = price_energy_check(
        price_usd=50.0,        # transaction fee
        embodied_kwh=1000.0,   # energy to mine/validate
    )
    print(f"  Status: {btc_result['status']}")
    print(f"  {btc_result['warning']}")

    # -- 2. Copper wire: plausible --
    print("\n-- COPPER WIRE (10 kg) --")
    copper = embodied_energy(
        materials={"copper": 10.0},
        transport_km=500,
        transport_kg=10,
        processing_kwh=15.0,   # drawing into wire
    )
    print(f"  Embodied: {copper['total_kwh']} kWh")
    wire_price = price_energy_check(
        price_usd=85.0,
        embodied_kwh=copper["total_kwh"],
    )
    print(f"  Status: {wire_price['status']}")
    print(f"  {wire_price['warning']}")

    # -- 3. Diamond ring: inflated --
    print("\n-- DIAMOND RING --")
    diamond = price_energy_check(
        price_usd=5000.0,
        embodied_kwh=20.0,     # actual mining + cutting energy
    )
    print(f"  Status: {diamond['status']}")
    print(f"  {diamond['warning']}")

    # -- 4. Labor: the hidden energy budget --
    print("\n-- LABOR: 8-HOUR WORKDAY --")
    workday = labor_energy_budget(hours=8.0, include_support=True)
    print(f"  Direct output:  {workday['direct_work_output_kwh']} kWh")
    print(f"  System cost:    {workday['total_system_kwh']} kWh")
    print(f"  Efficiency:     {workday['efficiency_pct']}%")
    print(f"  ({workday['note']})")

    # -- 5. EROEI comparison --
    print("\n-- EROEI COMPARISON --")
    systems = [
        ("1930s oil well",      100, 1),
        ("modern conventional",  15, 1),
        ("tar sands",             5, 1),
        ("corn ethanol",        0.8, 1),
        ("solar PV",             10, 1),
        ("wind",                 18, 1),
        ("firewood (managed)",    8, 1),
    ]
    for label, produced, invested in systems:
        result = eroei_check(produced, invested, label=label)
        icon = "!" if result["hazard"] else "."
        print(f"  {icon} [{result['status']:>17}] {label}: {result['eroei']}:1")
