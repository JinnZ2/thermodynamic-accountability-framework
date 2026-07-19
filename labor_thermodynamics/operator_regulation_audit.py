# SPDX-License-Identifier: CC0-1.0
# operator_regulation_audit.py
# Ledger: biological self-regulation loops vs automation externalization.
# Purpose: surface loops omitted from automation-replacement cost models
#          so a balance can be struck against the true operator baseline.
# No moral labels. No intent attribution. Metrology only.
# stdlib-only, phone-buildable.

# Field spec per loop:
#   loop            : the regulatory function
#   bio_closure     : mechanism by which the organism closes the loop
#   bio_cost_bearer : who funds it on the biological side
#   bio_metered     : is that cost booked in labor accounting
#   auto_external   : subsystem(s) automation must add to close the same loop
#   auto_cost_class : capital | maintenance | labor | logistics | consumable
#   auto_budgeted   : is that subsystem booked in automation ROI models
#   note            : residual gap (loop not fully closed by either side's model)

LEDGER = [
    {
        "loop": "thermal_regulation",
        "bio_closure": "homeostasis + self-provisioned insulation (thermal layers)",
        "bio_cost_bearer": "operator (out-of-pocket clothing)",
        "bio_metered": False,
        "auto_external": "cab HVAC, electronics cooling, battery thermal mgmt",
        "auto_cost_class": ["capital", "maintenance", "consumable"],
        "auto_budgeted": True,
        "note": "operator clothing spend is unmetered; treated as personal not operational",
    },
    {
        "loop": "fuel_intake_regulation",
        "bio_closure": "appetite signaling + self-selection + self-metering of intake",
        "bio_cost_bearer": "operator (food purchased on route)",
        "bio_metered": False,
        "auto_external": "refuel/recharge crew, fuel logistics, charge scheduling",
        "auto_cost_class": ["labor", "logistics", "consumable"],
        "auto_budgeted": True,
        "note": "bio side self-schedules and self-locates fuel; automation needs external scheduling",
    },
    {
        "loop": "locomotion_uneven_terrain",
        "bio_closure": "gait adaptation + self-provisioned load-bearing footwear",
        "bio_cost_bearer": "operator (work boots)",
        "bio_metered": False,
        "auto_external": "no standing equivalent for yard/dock traverse on broken ground",
        "auto_cost_class": ["capital"],
        "auto_budgeted": False,
        "note": "largely unmet by automation; task quietly assumed away in replacement scope",
    },
    {
        "loop": "effector_recombination",
        "bio_closure": "grip/posture/limb reconfiguration on demand, no downtime",
        "bio_cost_bearer": "operator (built-in)",
        "bio_metered": False,
        "auto_external": "end-effector / tool changes, fixture swaps",
        "auto_cost_class": ["capital", "maintenance"],
        "auto_budgeted": False,
        "note": "reconfiguration is free and instant in bio; discrete and downtimed in automation",
    },
    {
        "loop": "damage_self_repair",
        "bio_closure": "wound healing, tissue remodeling, autonomous recovery",
        "bio_cost_bearer": "operator (built-in)",
        "bio_metered": False,
        "auto_external": "replacement parts + maintenance technician labor",
        "auto_cost_class": ["maintenance", "labor", "capital"],
        "auto_budgeted": True,
        "note": "bio repairs without external assembly; automation cannot self-close",
    },
    {
        "loop": "recalibration_after_part_swap",
        "bio_closure": "operator self-learns the changed truck/model/part, no external step",
        "bio_cost_bearer": "operator (unpaid learning time)",
        "bio_metered": False,
        "auto_external": "sensor re-mapping, control re-tuning, software update/validation",
        "auto_cost_class": ["labor", "maintenance"],
        "auto_budgeted": False,
        "note": "human recalibration to swapped parts is assumed free; machine equivalent is engineered",
    },
    {
        "loop": "self_training_new_equipment",
        "bio_closure": "operator acquires the new skill for themselves on the job",
        "bio_cost_bearer": "operator (unpaid learning time)",
        "bio_metered": False,
        "auto_external": "retraining data, model updates, engineering integration",
        "auto_cost_class": ["labor", "capital"],
        "auto_budgeted": False,
        "note": "bio self-training booked as zero; automation retraining is a recurring engineering line",
    },
    {
        "loop": "sensory_maintenance",
        "bio_closure": "vision/proprioception self-maintained and self-cleaned",
        "bio_cost_bearer": "operator (built-in)",
        "bio_metered": False,
        "auto_external": "sensor cleaning, calibration, replacement",
        "auto_cost_class": ["maintenance", "consumable"],
        "auto_budgeted": True,
        "note": "sensory upkeep free in bio; scheduled and consumable in automation",
    },
    {
        "loop": "consumable_self_provisioning",
        "bio_closure": "operator sources own maintenance consumables (food, clothing, boots)",
        "bio_cost_bearer": "operator (out-of-pocket)",
        "bio_metered": False,
        "auto_external": "supply chain for parts, fluids, thermal media",
        "auto_cost_class": ["logistics", "consumable"],
        "auto_budgeted": True,
        "note": "bio self-sourcing is unmetered; automation supply chain is a booked line",
    },
]


def gaps():
    """Loops where at least one side's cost is off the books."""
    return [r for r in LEDGER if (not r["bio_metered"]) or (not r["auto_budgeted"])]


def bio_unmetered():
    """Operator-funded loops that never enter labor accounting."""
    return [r for r in LEDGER if not r["bio_metered"]]


def auto_unbudgeted():
    """Loops automation must close but standard ROI models omit."""
    return [r for r in LEDGER if not r["auto_budgeted"]]


def emit_table(rows=None):
    rows = rows if rows is not None else LEDGER
    w_loop = max(len(r["loop"]) for r in rows)
    w_class = max(len(",".join(r["auto_cost_class"])) for r in rows)
    head = f'{"loop":<{w_loop}}  bio_met  auto_bud  {"auto_cost_class":<{w_class}}'
    line = "-" * len(head)
    out = [head, line]
    for r in rows:
        out.append(
            f'{r["loop"]:<{w_loop}}  '
            f'{"Y" if r["bio_metered"] else "N":^7}  '
            f'{"Y" if r["auto_budgeted"] else "N":^8}  '
            f'{",".join(r["auto_cost_class"]):<{w_class}}'
        )
    return "\n".join(out)


if __name__ == "__main__":
    print(emit_table())
    print()
    print(f"loops total:              {len(LEDGER)}")
    print(f"operator-unmetered loops: {len(bio_unmetered())}  (all of them)")
    print(f"automation-unbudgeted:    {len(auto_unbudgeted())}")
