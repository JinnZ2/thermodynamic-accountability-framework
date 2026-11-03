# community.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (Kavik + Claude).
#
# A Community records WHO locally holds each item and how long each segment
# holds without grid (buffer_hours). Buffer duration is the restoration
# denominator, not headcount.
#
#   gaps(c)            L0/L1 items this community has no holder for
#   interconnect(a,b)  L3 items both lack + what each holds that the other lacks

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from schema import Item


@dataclass
class Community:
    name: str
    holders: Dict[str, str] = field(default_factory=dict)       # item_id -> who holds it
    buffer_hours: Dict[str, Optional[float]] = field(default_factory=dict)  # segment -> hours

    def holds(self, item_id: str) -> bool:
        return bool(str(self.holders.get(item_id) or "").strip())


def load_community(path: str) -> Community:
    with open(path, encoding="utf-8") as f:
        d = json.load(f) or {}
    return Community(
        name=str(d.get("name") or path),
        holders={k: v for k, v in (d.get("holders") or {}).items()},
        buffer_hours={k: v for k, v in (d.get("buffer_hours") or {}).items()},
    )


def unknown_item_ids(c: Community, items: Dict[str, Item]) -> List[str]:
    return sorted(k for k in c.holders if k not in items)


def gaps(c: Community, items: Dict[str, Item]) -> List[dict]:
    """L0/L1 items with no holder in this community, life floor first."""
    out = []
    for it in sorted(items.values(), key=lambda x: (x.level, x.id)):
        if it.level in (0, 1) and not it.parallel_input and not c.holds(it.id):
            out.append({"id": it.id, "level": it.level, "name": it.name,
                        "substitute": it.non_grid_substitute})
    return out


def interconnect(a: Community, b: Community, items: Dict[str, Item]) -> dict:
    """L3 items neither holds, and complementary holdings (any level)."""
    both_lack = [k for k, it in sorted(items.items())
                 if it.level == 3 and not it.parallel_input and not a.holds(k) and not b.holds(k)]
    a_not_b = sorted(k for k in items if a.holds(k) and not b.holds(k))
    b_not_a = sorted(k for k in items if b.holds(k) and not a.holds(k))
    return {"both_lack_L3": both_lack,
            "a_offers_b": a_not_b, "b_offers_a": b_not_a,
            "a": a.name, "b": b.name}
