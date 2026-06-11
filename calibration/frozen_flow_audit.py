"""
frozen_flow_audit.py
====================================================================
Detector for the FROZEN-FLOW error: a dX/dt rendered as a static X.

A model is STRUCTURALLY BLIND to violating a governing quantity Q
iff  Q governs the system's regime  AND  Q is not a state variable
of the model. Blindness => no internal falsifier for Q can ever fire
=> downstream fidelity cannot recover validity.

    corruption(trend) = corruption(measurement) x corruption(framework)
    Q unmeasured => corruption(measurement)=TOTAL on Q => product TOTAL,
    however rigorous the downstream framework. Fidelity downstream of a
    frozen variable launders the freeze; it does not cure it.

AUTO-FLAG (this version):
    a quantity that is secretly a rate (dX/dt under scope) AND is
    PRESCRIBED (imposed as a set value) is a frozen flow, detected
    without anyone declaring it. The secretly_a_rate flag is what
    separates a LEGITIMATE boundary condition (fine to prescribe)
    from a LAUNDERED differential (the fraud signature).

stdlib only. CC0. github.com/JinnZ2
====================================================================
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class QKind(Enum):
    CONSERVED = "conserved"     # angular momentum, mass, energy
    TRANSPORT = "transport"     # momentum diffusion, heat flux, coupling
    RATE      = "rate"          # creep rate, slip rate, dX/dt directly
    THRESHOLD = "threshold"     # a regime boundary in some parameter


@dataclass
class GoverningQuantity:
    name: str
    kind: QKind
    governs: str
    secretly_a_rate: bool        # is this noun actually dX/dt under scope?
    law: str = ""


@dataclass
class Model:
    name: str
    state_variables: set         # quantities the model EVOLVES
    prescribed: set              # quantities IMPOSED by hand (set, not evolved)
    headline_output: str
    output_rides_on: set


@dataclass
class RegimeCheck:
    param: str
    claimed_regime: str
    actual_spans: str
    inversion_at: str
    inverts: bool


class Status(Enum):
    EVOLVED    = "EVOLVED"        # Q is a state variable. good.
    PRESCRIBED = "PRESCRIBED"     # Q imposed by hand.
    ABSENT     = "ABSENT"         # Q not in the model at all.


@dataclass
class Finding:
    quantity: str
    status: Status
    blind: bool                  # can a falsifier for Q fire from inside?
    frozen_flow: bool            # AUTO: a rate imposed as static. the freeze.
    load_bearing: bool           # does the headline output ride on this?
    note: str = ""


# --------------------------------------------------------------------
# THE DETECTOR
# --------------------------------------------------------------------
def audit(system: list,
          model: Model,
          regimes: Optional[list] = None) -> dict:

    findings: list = []

    for q in system:
        if q.name in model.state_variables:
            status, blind = Status.EVOLVED, False
        elif q.name in model.prescribed:
            status, blind = Status.PRESCRIBED, True
        else:
            status, blind = Status.ABSENT, True

        # AUTO-FLAG: a rate that has been imposed as a set value.
        # this is the laundering signature, found without being told.
        frozen = (status == Status.PRESCRIBED and q.secretly_a_rate)

        if status == Status.EVOLVED:
            note = "evolved; a violation here CAN fire a falsifier"
        elif frozen:
            note = ("FROZEN FLOW: a dX/dt imposed as static X. "
                    "this is the laundered differential, auto-detected")
        elif status == Status.PRESCRIBED:
            note = ("prescribed, but not a rate -> legitimate boundary "
                    "condition. blind on its value, not a freeze")
        else:  # ABSENT
            note = ("absent. " + ("a governing rate is simply gone"
                    if q.secretly_a_rate else "omitted from the model"))

        load_bearing = q.name in model.output_rides_on and blind
        findings.append(
            Finding(q.name, status, blind, frozen, load_bearing, note))

    blind_qs            = [f for f in findings if f.blind]
    frozen_flows        = [f for f in findings if f.frozen_flow]
    load_bearing_frozen = [f for f in findings if f.frozen_flow and f.load_bearing]
    load_bearing_blind  = [f for f in findings if f.load_bearing]
    measurement_total   = len(blind_qs) > 0

    regime_flags = []
    for r in (regimes or []):
        if r.inverts:
            regime_flags.append(
                f"{r.param}: claim assumes '{r.claimed_regime}' but real value "
                f"spans {r.actual_spans}; inverts at {r.inversion_at}. "
                f"frozen model cannot represent the regime it actually enters")

    # verdict tiers -- frozen flow is now distinguished from plain blindness
    if not measurement_total:
        verdict = "PASS -- every governing quantity is evolved; falsifiers can fire"
    elif load_bearing_frozen:
        verdict = ("STRUCTURAL FRAUD (frozen flow) -- the headline output rides on "
                   "a dX/dt that was imposed as static. the laundered step does "
                   "all the work")
    elif load_bearing_blind:
        verdict = ("STRUCTURAL FRAUD (omission) -- the output rides on a governing "
                   "quantity that is absent. no falsifier can fire")
    elif frozen_flows:
        verdict = ("FROZEN FLOW PRESENT -- a rate is imposed as static; the model "
                   "is blind to it, though the headline output does not ride on it "
                   "yet")
    else:
        verdict = ("STRUCTURALLY BLIND -- a governing quantity is unevolved "
                   "(boundary condition or omission), no rate laundered")

    return {
        "model": model.name,
        "findings": findings,
        "regime_flags": regime_flags,
        "measurement_corruption": "TOTAL" if measurement_total else "bounded",
        "frozen_flows": [f.quantity for f in frozen_flows],
        "load_bearing_freezes": [f.quantity for f in load_bearing_frozen],
        "verdict": verdict,
    }


# --------------------------------------------------------------------
# RENDER
# --------------------------------------------------------------------
def show(result: dict) -> None:
    print("=" * 70)
    print(f"MODEL: {result['model']}")
    print("-" * 70)
    print(f"{'quantity':<24}{'status':<12}{'blind':<7}{'FROZEN':<8}{'load-bearing'}")
    for f in result["findings"]:
        mark = "<<<" if f.frozen_flow else ""
        print(f"{f.quantity:<24}{f.status.value:<12}"
              f"{str(f.blind):<7}{str(f.frozen_flow):<8}{f.load_bearing} {mark}")
    print("-" * 70)
    print(f"corruption(measurement) = {result['measurement_corruption']}")
    if result["frozen_flows"]:
        print(f"auto-detected frozen flows: {result['frozen_flows']}")
    if result["load_bearing_freezes"]:
        print(f"the freeze doing all the work: {result['load_bearing_freezes']}")
    for flag in result["regime_flags"]:
        print(f"  regime: {flag}")
    print(f"\nVERDICT: {result['verdict']}")
    print("=" * 70 + "\n")


# ====================================================================
# INSTANCES
# ====================================================================
if __name__ == "__main__":

    L = GoverningQuantity(
        "angular_momentum", QKind.CONSERVED,
        "orientation of spin axis in space", secretly_a_rate=False,
        law="dL/dt = external torque only")
    coupling = GoverningQuantity(
        "viscous_coupling", QKind.TRANSPORT,
        "whether crust can move independent of mantle", secretly_a_rate=True,
        law="momentum diffuses in tau ~ rho L^2 / eta")
    crust_orientation = GoverningQuantity(
        "crust_orientation", QKind.RATE,
        "where your latitude ends up", secretly_a_rate=True,
        law="d(theta)/dt must come FROM the torque+coupling ledger")

    # 1) POLE-SHIFT SIM
    poleshift = Model(
        "rapid-pole-shift simulation (24-72h)",
        state_variables={"ocean_surge", "coastline", "surface_elevation"},
        prescribed={"crust_orientation"},
        headline_output="surge + relocate to 90N",
        output_rides_on={"crust_orientation", "ocean_surge"})
    eta_regime = RegimeCheck(
        "eta (mantle viscosity)", "low enough to slip in days",
        "1e19-1e21 Pa.s (Re ~ 1e-13)",
        "Re ~ 1: above it inertia leads, below it only creep exists", True)
    show(audit([L, coupling, crust_orientation], poleshift, [eta_regime]))

    # 2) SCHOOLBOOK MANTLE
    creep = GoverningQuantity(
        "creep_rate", QKind.RATE, "that the mantle convects at all",
        secretly_a_rate=True, law="d(strain)/dt = stress / eta")
    heat_flux = GoverningQuantity(
        "convective_heat_flux", QKind.TRANSPORT,
        "plate motion, volcanism, the surface readout",
        secretly_a_rate=True, law="core heat carried up by convection")
    ball = Model(
        "schoolbook 'ball inside ball' mantle",
        state_variables=set(),
        prescribed={"creep_rate", "convective_heat_flux"},
        headline_output="solid sphere, volcanoes = cracks",
        output_rides_on={"creep_rate", "convective_heat_flux"})
    show(audit([creep, heat_flux], ball))

    # 3) KNOWLEDGE TRANSMISSION AS WALLS
    flux = GoverningQuantity(
        "transmission_flux", QKind.TRANSPORT,
        "whether a held-open question propagates through a room",
        secretly_a_rate=True, law="d(understanding)/dt spreads cell-to-cell")
    walls = Model(
        "book->student, boundaries are walls",
        state_variables=set(), prescribed={"transmission_flux"},
        headline_output="knowledge delivered one direction, on schedule",
        output_rides_on={"transmission_flux"})
    show(audit([flux], walls))

    # 4) HONEST CONVECTION MODEL -- must PASS
    convection = Model(
        "geodynamic convection model (evolves the flow)",
        state_variables={"creep_rate", "convective_heat_flux", "viscous_coupling"},
        prescribed=set(),
        headline_output="plate velocities, slab stalling at 660 km",
        output_rides_on={"creep_rate", "convective_heat_flux"})
    show(audit([creep, heat_flux, coupling], convection))

    # 5) LEGITIMATE PRESCRIBED BOUNDARY CONDITION -- must NOT be called a freeze.
    #    surface temp IS imposed in real climate runs; it is not a rate.
    #    proves secretly_a_rate is doing the discriminating work.
    surface_temp = GoverningQuantity(
        "surface_temperature_BC", QKind.THRESHOLD,
        "top boundary of a mantle/ocean run", secretly_a_rate=False,
        law="imposed boundary value, legitimately held fixed")
    honest_bc = Model(
        "convection run with prescribed surface-temp BC",
        state_variables={"creep_rate", "convective_heat_flux"},
        prescribed={"surface_temperature_BC"},
        headline_output="interior flow given a fixed top temperature",
        output_rides_on={"creep_rate", "convective_heat_flux"})
    show(audit([creep, heat_flux, surface_temp], honest_bc))
