"""
concerns/cascade_failure_rural_degradation.py

CASCADE FAILURE MODEL + RURAL DEGRADATION STATUS

Empirical snapshot of US/global agricultural substrate degradation
plus the cascade-failure model with explicit threshold timing and
the loss-to-formation rate math that makes recovery-during-load
mathematically impossible.

Tenth module in concerns/. Companion to:
- externality_model_audit            (150-year long-arc record)
- substrate_externality_load_map     (structural argument)
- data_center_siting_playbook        (current 2025-2026 case)
- this module                        (concrete threshold timing +
                                       loss-vs-formation arithmetic)

The four together: structural argument + historical record + current
case + cascade timing. Each is auditable independently.

License: CC0 -- public domain
Dependencies: stdlib only
"""

# ============================================================
# CURRENT STATE: US RURAL DEGRADATION SNAPSHOT (2026)
# ============================================================

midwest_soil_loss = {
    "total_loss_160_years": "57.6 billion metric tons of topsoil eroded",
    "carbon_removed": "1.4 +/- 0.5 Pg (petagram) carbon from hillslopes",
    "current_rate": "2 millimeters of soil per year (Corn Belt)",
    "erosion_vs_formation": "10 to 1,000 times faster than pre-agricultural rates",
    "area_impacted": "35% of cultivated area has lost A-horizon soil",
    "economic_annual_loss": "$2.8 +/- $0.9 billion in crop yield reduction",
    "prairie_remaining": "less than 0.1% of original prairie",
}

global_agricultural_degradation = {
    "fertile_soil_loss_rate": "24 billion tons of fertile soil per year",
    "percentage_degraded_by_2050": "95% of Earth's land on course to be degraded",
    "percentage_already_degraded": "40% of world's agricultural land already severely degraded",
}


# ============================================================
# THE CASCADE MODEL -- thermodynamic shape with thresholds
# ============================================================

CASCADE_SEQUENCE = """
                    PRESSURE POINT 1
                    (Load applied to substrate)
                         |
                         v
            +-----------------------------+
            |   Soil loss (2mm/year)      |
            |   Carbon removed            |
            |   Nutrient cycling breaks   |
            +--------------+--------------+
                           |
                    THRESHOLD 1 CROSSED
                    (5-10 years, variable)
                           |
                           v
            +-----------------------------+
            |   Microbial population      |
            |   decline                   |
            |   Nitrogen fixation falls   |
            +--------------+--------------+
                           |
                    PRESSURE POINT 2
                    (Compounding load)
                           |
                           v
            +-----------------------------+
            |   Pollinator habitat        |
            |   collapses                 |
            |   Plant reproduction fails  |
            +--------------+--------------+
                           |
                    THRESHOLD 2 CROSSED
                    (10-20 years)
                           |
                           v
            +-----------------------------+
            |   Food crop yield decline   |
            |   40% insect decline        |
            |   Genetic diversity loss    |
            +--------------+--------------+
                           |
                    THRESHOLD 3 CROSSED
                    (15-25 years)
                           |
                           v
            +-----------------------------+
            |   PHASE CHANGE              |
            |   Agricultural system       |
            |   becomes unreliable        |
            |   Price volatility rises    |
            |   Regional food insecurity  |
            +-----------------------------+
                           |
                  (Propagates to cities)
                           |
                           v
            +-----------------------------+
            |   Urban supply shock        |
            |   Inflation                 |
            |   Social destabilization    |
            +-----------------------------+
"""


# ============================================================
# RECOVERY TIME DATA -- what it takes to NOT be in cascade
# ============================================================

recovery_timelines = {
    "degraded_forested_ecosystems": "decades to millennia for full recovery",
    "heavily_degraded_systems_with_intervention": (
        "faster than predicted, but 20-40+ years typical"
    ),
    "soil_carbon_recovery_from_agriculture": (
        "30-35 years to equilibrium in moderately degraded"
    ),
    "severely_degraded_soil": (
        "90% carbon loss; recovery equation fundamentally different"
    ),
    "critical_constraint": (
        "if pressure continues during recovery period, system locks into "
        "degraded state permanently"
    ),
}


# ============================================================
# THE MATH -- why "stop loading" is the only working intervention
# ============================================================

the_math = {
    "soil_loss_rate": "2 mm/year in Midwest",
    "soil_formation_rate": "0.03 mm/year under best conditions",
    "ratio": "~65:1 (loss to formation)",
    "meaning": (
        "every year of continued pressure adds 65x more deficit than "
        "recovery can address"
    ),
}


recovery_impossibility_during_load = {
    "scenario_A": {
        "status": "continue loading (data centers + agriculture)",
        "soil_trajectory": "cumulative deficit increases",
        "recovery_probability": "zero",
        "timeframe": "system locks into permanent degradation",
    },
    "scenario_B": {
        "status": "stop all new load, allow recovery",
        "soil_trajectory": "deficit stops accumulating",
        "recovery_begins": "year 1",
        "critical_question": "can this particular substrate still recover?",
        "assessment_period": "10-15 years to know if reversible",
    },
}


# ============================================================
# EMPIRICAL FINDINGS -- factual summary
# ============================================================

empirical_findings = [
    "57.6 billion tons of topsoil eroded in 160 years",
    "current rate: 65x faster loss than natural formation",
    "40% of world's agricultural land severely degraded",
    "insect populations declining 8x faster than vertebrates",
    "soil recovery under continued pressure: does not occur",
    (
        "soil recovery with pressure relief: 20-40 years typical, but "
        "requires full stoppage"
    ),
    "if phase change occurs (food system failure), recovery window closes",
    (
        "UK security assessment 2026: tipping points are 'real geopolitical "
        "risk'"
    ),
    (
        "Global Challenges Foundation 2026: crossing multiple thresholds "
        "risks collapse of most ecosystems"
    ),
]


# ============================================================
# RUN -- print the documentary record
# ============================================================

def _print_dict(d, indent="  "):
    for k, v in d.items():
        if isinstance(v, dict):
            print(f"{indent}{k}:")
            _print_dict(v, indent + "  ")
        elif isinstance(v, list):
            print(f"{indent}{k}:")
            for item in v:
                print(f"{indent}  - {item}")
        else:
            print(f"{indent}{k}: {v}")


def run():
    print("=" * 72)
    print("CASCADE FAILURE MODEL + RURAL DEGRADATION STATUS")
    print("=" * 72)

    print("\nMIDWEST SOIL LOSS (2026 SNAPSHOT)")
    print("-" * 72)
    _print_dict(midwest_soil_loss)

    print("\nGLOBAL AGRICULTURAL DEGRADATION")
    print("-" * 72)
    _print_dict(global_agricultural_degradation)

    print("\nTHE CASCADE -- thermodynamic shape with thresholds")
    print("-" * 72)
    print(CASCADE_SEQUENCE)

    print("\nRECOVERY TIMELINES -- what it takes to NOT be in cascade")
    print("-" * 72)
    _print_dict(recovery_timelines)

    print("\nTHE MATH -- loss-to-formation ratio")
    print("-" * 72)
    _print_dict(the_math)

    print("\nRECOVERY IMPOSSIBILITY DURING LOAD")
    print("-" * 72)
    _print_dict(recovery_impossibility_during_load)

    print("\nEMPIRICAL FINDINGS")
    print("-" * 72)
    for finding in empirical_findings:
        print(f"  - {finding}")

    print()
    print("=" * 72)
    print("THE LOAD-VS-FORMATION CONSTRAINT")
    print("=" * 72)
    print("""
  Soil loss rate (Midwest):       2 mm/year
  Soil formation rate (best):     0.03 mm/year
  Ratio:                          ~65:1

  Every additional year of load adds 65x more deficit than the
  best-case recovery rate can address. Recovery cannot run
  concurrently with continued load; the arithmetic forbids it.

  Scenario A (continue load):     cumulative deficit increases,
                                   recovery_probability = 0,
                                   system locks into permanent
                                   degradation.
  Scenario B (stop new load):     deficit stops accumulating,
                                   recovery begins year 1,
                                   reversibility assessable
                                   over 10-15 years.

  The thresholds in the cascade above (5-10 yrs / 10-20 yrs /
  15-25 yrs) are wall-clock estimates from soil-science and
  ecology literature. Each crossed threshold reduces the
  reversibility window. After phase change (threshold 3),
  the window closes.
""")


if __name__ == "__main__":
    run()
