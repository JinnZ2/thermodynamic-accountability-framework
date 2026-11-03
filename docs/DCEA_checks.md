# DCEA v0.1 + Worker-Side Ledger: checks

Companion to `docs/DCEA_v0.1.md` and `docs/worker_side_ledger_road_driver.md`.
Both are kept verbatim; findings go here. CC0. Recomputed by `python core/dcea.py`.

| File | sha256 at landing |
| --- | --- |
| docs/DCEA_v0.1.md | ec9d4de096d528599b0a7918a1efd4a171655a207cd01020127dddfea99819e7 |
| docs/worker_side_ledger_road_driver.md | a3ce0d7f4a6426c12f9c5e5dcd7b921df8235c6e0bab14cb3a28893dfeee1721 |

## 1. Ledger arithmetic (DERIVED, recomputed)

250 road days, BLS median wage $58,640. Filters PENDING; proper nutrition and every
section-4 item excluded, so every figure below is a floor.

| Reading | Daily | Annual | Share of wage |
| --- | --- | --- | --- |
| Stated in the ledger | $86 - $133 | $22,300 - $34,600 | 38% - 59% |
| From the rounded table rows | $86.00 - $133.00 | $22,282 - $34,502 | 38.0% - 58.8% |
| From the raw inputs | $86.49 - $131.91 | $22,403 - $34,231 | 38.2% - 58.4% |

- The stated daily range is the sum of the rounded rows. Each row was rounded outward
  (food 34.50 -> 35, water 12.71 -> 13, idling 65.50 -> 66), so the high end carries
  about $1.09/day of rounding, about $270/yr.
- The stated annual high ($34,600) sits about $100 above the rounded-row total and about
  $370 above the raw-input total. The low end is within $105 on both readings.
- Direction of every gap is small against the PENDING items it sits beside; the finding
  (a third to over half of pay goes to access) holds on all three readings.
- Correction to an earlier chat reading: the high end was first described as "about $100
  high". Against the raw inputs it is about $370 high.

## 2. Calculator repairs (section 6 of DCEA v0.1)

| Repair | Reason |
| --- | --- |
| `Optional[float]` for `energy_mj` | `float \| None` in a dataclass field is evaluated at class creation and raises TypeError before Python 3.10 |
| `pending_count` added | R11 asks for the count; `pending_share` divides by all nodes including the root, so it is a share of nodes, not of energy |
| `duplicate_names` added | `site_eroi` selects site nodes by name; two nodes sharing a name are counted together silently |

`single_source` is reported as a list (R9) and carries no energy weight; that is as specified.

## 3. R13 cross-reference

The R13 deviation table's CoHD row (US 2025 $2.86; China 3.68 / 4.59 vs earlier 3.13;
Japan 8.27 vs 5.98) is carried as given. The PPP base year stays PENDING. The FAO and
World Bank hosts were not reachable from this environment, so no figure was re-pulled.

## 4. Status of cited figures

Every literature figure in both documents (Williamson & Feyer 2000, FMCSA LTCCS,
IARC 2A, Orhun & Palazzolo 2019, USDA 2015, BLS prices, National Academies intake)
is carried, not verified here.
