"""
timing_as_constraint.py

Framework: timing as a load-bearing constraint layer in physical systems.

## Premise

Western institutional design strips temporal scope from physical systems
in pursuit of permanence. A motor without timing is dead metal. A building
code without scope is a falsified audit. This module restores timing to
its position as a *precision measurement instrument*, not a decoration.

## Core claim

Every physical system has a valid operational window defined by coupled
variables (thermal, moisture, load, substrate motion, material decay).
Strip the temporal scope and you remove the diagnostic signature that
tells you the system is failing. Failure becomes catastrophic instead
of observable.

Sister to:
  - core/regulation_cascade_mapper.py
      (thermodynamic consequence mapping for municipal/regulatory codes;
       this module adds the missing temporal dimension to that audit)
  - calibration/recency_bias_detector.py
      (the recency-bias gate; permanence-without-scope is a recency
       anomaly being projected as universal default)

License: CC0
Stdlib only.
"""

from dataclasses import dataclass, field


# =============================================================================
# 1. Scope: the valid operational window of a physical system
# =============================================================================

@dataclass
class Scope:
    """
    Defines the operational envelope of a designed system.

    A system is *in scope* when all coupled variables sit inside their
    declared bounds. Outside scope, the design assumptions are falsified
    and continued operation is running on borrowed audit.
    """
    name: str
    thermal_range_c: tuple[float, float]         # (min, max) Celsius
    moisture_range_pct: tuple[float, float]      # relative humidity %
    load_range_kn: tuple[float, float]           # structural load kN
    substrate_motion_mm_yr: tuple[float, float]  # subsidence/uplift mm/yr
    material_decay_pct_yr: float                 # expected decay rate

    def in_scope(self, state: dict) -> bool:
        return (
            self.thermal_range_c[0] <= state["thermal_c"] <= self.thermal_range_c[1]
            and self.moisture_range_pct[0] <= state["moisture_pct"] <= self.moisture_range_pct[1]
            and self.load_range_kn[0] <= state["load_kn"] <= self.load_range_kn[1]
            and self.substrate_motion_mm_yr[0] <= state["substrate_mm_yr"] <= self.substrate_motion_mm_yr[1]
        )

    def scope_exit_signature(self, state: dict) -> list[str]:
        """Return which variables have left scope. Diagnostic signature."""
        exits = []
        if not (self.thermal_range_c[0] <= state["thermal_c"] <= self.thermal_range_c[1]):
            exits.append("thermal")
        if not (self.moisture_range_pct[0] <= state["moisture_pct"] <= self.moisture_range_pct[1]):
            exits.append("moisture")
        if not (self.load_range_kn[0] <= state["load_kn"] <= self.load_range_kn[1]):
            exits.append("load")
        if not (self.substrate_motion_mm_yr[0] <= state["substrate_mm_yr"] <= self.substrate_motion_mm_yr[1]):
            exits.append("substrate_motion")
        return exits


# =============================================================================
# 2. Cycle: timing as a precision measurement instrument
# =============================================================================

@dataclass
class Cycle:
    """
    A scheduled diagnostic interval. Not maintenance overhead.
    A measurement instrument that tells you the system is alive
    and operating inside its valid envelope.
    """
    name: str
    interval_years: float
    measurement: str           # what is measured at this cycle
    threshold: float           # value at which scope-exit is flagged
    units: str

    def due(self, last_run_year: float, current_year: float) -> bool:
        return (current_year - last_run_year) >= self.interval_years


# =============================================================================
# 3. Audit: a system is only valid if its scope and cycles are declared
# =============================================================================

@dataclass
class TemporalAudit:
    """
    Audits whether a designed system declares its temporal scope.
    A code or regulation without scope and cycles is a falsified audit:
    it claims permanence the physics does not grant.
    """
    system_name: str
    scope: Scope | None
    cycles: list[Cycle] = field(default_factory=list)

    def is_falsified(self) -> tuple[bool, list[str]]:
        reasons = []
        if self.scope is None:
            reasons.append("no_scope_declared")
        if not self.cycles:
            reasons.append("no_diagnostic_cycles")
        return (bool(reasons), reasons)


# =============================================================================
# 4. Energy ledger: counter-acting cost vs adaptation cost
# =============================================================================

def lifecycle_energy_cost(
    counteract_kwh_per_year: float,
    adaptation_setup_kwh: float,
    cycle_kwh_per_event: float,
    cycle_interval_years: float,
    horizon_years: float,
) -> dict:
    """
    Compare two design philosophies over a time horizon.

    counteract: continuous resistance to substrate motion (pumping,
                rigid-foundation reinforcement, climate-control overhead).
    adaptation: one-time setup plus periodic adjustment cycles.

    Returns total kWh for each philosophy over the horizon.
    """
    counteract_total = counteract_kwh_per_year * horizon_years
    n_cycles = horizon_years / cycle_interval_years
    adaptation_total = adaptation_setup_kwh + (cycle_kwh_per_event * n_cycles)
    return {
        "counteract_kwh": counteract_total,
        "adaptation_kwh": adaptation_total,
        "ratio_counteract_to_adaptation": (
            counteract_total / adaptation_total
            if adaptation_total > 0 else float("inf")
        ),
    }


# =============================================================================
# 5. Falsifiable claims
# =============================================================================

CLAIMS = [
    "A regulation with no declared scope is a falsified audit.",
    "A system stripped of timing has no diagnostic signature; failure becomes catastrophic, not observable.",
    "Adaptation cost over a horizon is bounded; counteraction cost is unbounded.",
    "Material decay (e.g. lumber dimensional loss) is scope-exit, not failure: codes ignoring it are tracking the wrong variable.",
    "Building codes inheriting Western permanence assumptions cannot represent substrate motion as a design input.",
    "Cycles are measurement instruments. Removing them does not simplify a system; it blinds it.",
    "Two systems with identical static specs but different temporal scopes have different physics.",
    "Maintenance scheduled to scope is design; maintenance triggered by visible failure is salvage.",
]


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    # Example: 1970 building code audited against thermodynamic reality
    legacy_code = TemporalAudit(
        system_name="National Building Code 1970 (legacy)",
        scope=None,
        cycles=[],
    )
    falsified, reasons = legacy_code.is_falsified()
    print(f"{legacy_code.system_name}: falsified={falsified}, reasons={reasons}")

    # Example: scope-aware code for a delta city
    delta_scope = Scope(
        name="Ganga delta urban scope",
        thermal_range_c=(5.0, 45.0),
        moisture_range_pct=(30.0, 95.0),
        load_range_kn=(0.0, 250.0),
        substrate_motion_mm_yr=(-30.0, 5.0),
        material_decay_pct_yr=0.5,
    )
    cycles = [
        Cycle(
            "foundation_settlement_check", 2.0,
            "differential_settlement", 10.0, "mm",
        ),
        Cycle(
            "material_density_check", 5.0,
            "wood_density_loss", 8.0, "%",
        ),
        Cycle(
            "substrate_motion_resurvey", 1.0,
            "vertical_land_motion", 25.0, "mm/yr",
        ),
    ]
    modern_code = TemporalAudit("Scope-aware delta code", delta_scope, cycles)
    falsified, reasons = modern_code.is_falsified()
    print(f"{modern_code.system_name}: falsified={falsified}, reasons={reasons}")

    energy = lifecycle_energy_cost(
        counteract_kwh_per_year=12000.0,
        adaptation_setup_kwh=8000.0,
        cycle_kwh_per_event=400.0,
        cycle_interval_years=2.0,
        horizon_years=50.0,
    )
    print(f"50-year energy ledger: {energy}")
