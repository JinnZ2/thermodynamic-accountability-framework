# schema.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (Kavik + Claude).
#
# One Item = one thing a community needs to hold through a TRUE black start
# (wide-area, months-long, no outside help). Restoration runs community-first,
# then interconnects outward. Government / military action is an OPTIONAL
# PARALLEL input (parallel_input=True): it may help, it is never a
# prerequisite, so nothing may list it in depends_on.
#
#   L0 life floor     heat, water, sanitation, medical cold chain
#   L1 enablers       fuel + non-grid pumps, self-starting generation,
#                     starting energy, off-grid comms, transport, people
#   L2 spares+know    transformers, breakers, relays, SCADA batteries,
#                     water chemicals, knowledge holders
#   L3 interconnect   sync, protection settings, frequency authority,
#                     pre-event trust agreements between communities

from dataclasses import dataclass, field, asdict
from typing import List, Optional

LEVELS = (0, 1, 2, 3)
VOLUMES = ("thin", "medium", "solid")
STATUSES = ("OBSERVED", "DERIVED", "PROPOSED")
TRIGGER_KINDS = ("threshold", "action", "debt", "handoff")


@dataclass
class Item:
    id: str
    name: str
    level: int
    function: str
    hours_to_fail_without_grid: Optional[float] = None
    non_grid_substitute: Optional[str] = None
    local_holder: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)
    trigger: str = ""
    lead_time_days: Optional[float] = None
    volume: str = "thin"
    status: str = "PROPOSED"
    parallel_input: bool = False
    note: Optional[str] = None

    def problems(self) -> List[str]:
        """Field-level problems. Empty list = valid. Never raises."""
        out = []
        if not isinstance(self.id, str) or not self.id:
            out.append("id empty")
        if self.level not in LEVELS:
            out.append("level %r not in 0-3" % (self.level,))
        if self.volume not in VOLUMES:
            out.append("volume %r not in %s" % (self.volume, VOLUMES))
        if self.status not in STATUSES:
            out.append("status %r not in %s" % (self.status, STATUSES))
        kind = (self.trigger or "").split(":", 1)[0].strip()
        if kind not in TRIGGER_KINDS:
            out.append("trigger must start with one of %s + ':'" % (TRIGGER_KINDS,))
        for f in ("hours_to_fail_without_grid", "lead_time_days"):
            v = getattr(self, f)
            if v is not None and (not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0):
                out.append("%s must be null or > 0" % f)
        if not isinstance(self.depends_on, list):
            out.append("depends_on must be a list")
        return out


ITEM_FIELDS = set(Item.__dataclass_fields__)


def item_from_dict(d: dict) -> Item:
    """Build an Item; unknown keys are ignored, missing optional keys get
    defaults, None depends_on becomes []. Null-safe."""
    kw = {k: v for k, v in (d or {}).items() if k in ITEM_FIELDS}
    if kw.get("depends_on") is None:
        kw["depends_on"] = []
    kw.setdefault("id", "")
    kw.setdefault("name", kw.get("id", ""))
    kw.setdefault("level", -1)
    kw.setdefault("function", "")
    return Item(**kw)


def item_to_dict(it: Item) -> dict:
    return asdict(it)
