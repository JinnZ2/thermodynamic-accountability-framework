#!/usr/bin/env python3
# holders.py -- CC0, stdlib only, python >= 3.7
# Provenance: co-authored (JinnZ2 + Claude), 2026-11-05.
#
# D-M3 holder protection. A KnowledgeHolder record says that a skill exists
# in a coarse region and how available it is. It never says who holds it.
#
#   skill         what the knowledge is (e.g. "manual synchronizing")
#   region        coarse area; no digits, at most 3 words
#   availability  short text (e.g. "on call", "seasonal", "unknown")
#   contact_via   a steward ROLE CODE (e.g. "steward-north"), never a person
#
# Identity fields (name, phone, email, address, coordinates, ...) are
# rejected at the door. Real holder records live in local_data/ (D-M1).

import re
from dataclasses import dataclass, asdict

FORBIDDEN = ("name", "full_name", "first_name", "last_name", "identity", "person", "phone", "email",
             "address", "street", "household", "id_number", "dob", "birth", "coordinates", "lat",
             "lon", "lng", "latitude", "longitude", "photo", "plate")
ALLOWED = ("skill", "region", "availability", "contact_via")
ROLE_CODE = re.compile(r"^[a-z][a-z0-9_-]{1,31}$")


class HolderError(ValueError):
    pass


@dataclass
class KnowledgeHolder:
    skill: str
    region: str
    availability: str = "unknown"
    contact_via: str = ""

    @staticmethod
    def from_dict(d):
        keys = set(d or {})
        bad = sorted(k for k in keys if any(f in k.lower() for f in FORBIDDEN))
        if bad:
            raise HolderError("identity field(s) refused: %s" % ", ".join(bad))
        extra = sorted(keys - set(ALLOWED))
        if extra:
            raise HolderError("unknown field(s): %s" % ", ".join(extra))
        h = KnowledgeHolder(**d)
        probs = h.problems()
        if probs:
            raise HolderError("; ".join(probs))
        return h

    def problems(self):
        out = []
        if not (self.skill or "").strip():
            out.append("skill required")
        r = (self.region or "").strip()
        if not r:
            out.append("region required (coarse)")
        elif re.search(r"\d", r) or len(r.split()) > 3:
            out.append("region must be coarse: no digits, at most 3 words")
        if not ROLE_CODE.match(self.contact_via or ""):
            out.append("contact_via must be a steward role code like 'steward-north'")
        return out

    def to_dict(self):
        return asdict(self)
