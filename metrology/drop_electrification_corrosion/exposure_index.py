#!/usr/bin/env python3
# exposure_index.py -- CC0, stdlib-only (urllib, csv, json, math), python >= 3.8
# Status: co-authored (operator work order + model build).
#
# TASK 2 of WORK_ORDER.md: charging-weighted exposure index, per site.
# Builds the common denominator between lab drop counts and outdoor
# panel exposure. Does NOT test, and does not assume, the mechanism:
# the lab causal link is intervention-tested on lab surfaces only;
# field relevance is INFERRED.
#
# ENERGY MAP
#
#   sites.csv (lat, lon, elev, terrain, tilt, damage)   <- panel_datasets.md
#      |
#   pick_station()   isd-history.csv: nearest with record overlap
#      |               stamps: distance_km, elev_delta_m        DERIVED
#   fetch_hourly()   NCEI global-hourly, per year, as far back as listed
#      |               [network]  NOT_TESTABLE in this container
#   parse_isd_csv()  TMP, DEW -> RH (Magnus), AA1 precip          OBSERVED/DERIVED
#      |
#   hourly_rain()    1-h reports direct; multi-h spread, flagged
#      |
#   FILTER: wet hours only (rain_mm > WET_THRESHOLD_MM)
#      |               monthly/annual means are never formed
#      v
#   per site:  wet_hours/yr, rain_mm/yr                           DERIVED
#              index = SUM_wet( rain_mm_h * weight(RH, T) )       weight STUB
#              slide drops/yr = rain x catchment x cos(tilt)
#                               x runoff_fraction / drop_volume   named params
#      |
#   uncertainty_band()  distance x elevation x terrain -> band    PROPOSED***
#      |                  fit_weight = 1/band^2 (loose sites kept)
#      v
#   index_by_site.csv  +  gradient_check.json (BUILT-IN CHECK)
#
# BUILT-IN CHECK (gradient_check): if damage tracks the index best at
# TIGHT-band sites and worst at WIDE-band sites, the index is doing
# work. No gradient -> the index is not measuring what it claims.
# Without per-site damage rates the verdict is NOT_TESTABLE, said so.
#
# TAGS: OBSERVED (read from a source), DERIVED (computed from observed),
# PROPOSED (hypothesis / rule with no calibration). Trailing asterisks =
# thin volume; more = thinner.
#
# CLI
#   python3 exposure_index.py --selftest
#   python3 exposure_index.py run --sites sites.csv --out index_by_site.csv
#        [--isd-history isd-history.csv] [--hourly-dir DIR] [--fetch]
#        [--drop-volume-ul V --catchment-m2 A --runoff-fraction F]
#        [--weight-params params.json] [--wet-threshold-mm 0.0] [--min-years 1]
#   python3 exposure_index.py fetch-history --out isd-history.csv     [network]
#   python3 exposure_index.py fetch STATION YEAR --out f.csv          [network]

import csv
import io
import json
import math
import os
import sys
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------
# SCOPE-STAMPED CONSTANTS
# ---------------------------------------------------------------
# Lab values: stated in the operator work order context line.
# NOT verified against the paper (Task 1 BLOCKED). Tag OBSERVED* (one
# second-hand statement).
LAB = {
    "drop_volume_ul": (35.0, "WORK_ORDER context line; unverified vs paper", "OBSERVED*"),
    "slide_length_cm": (4.0, "WORK_ORDER context line; unverified vs paper", "OBSERVED*"),
    "drops_to_pinhole": (3000, "WORK_ORDER '~3000'; press also reports 10000 (conflict)", "OBSERVED**"),
    "charge_nC_range": ((0.2, 2.0), "WORK_ORDER context line; unverified vs paper", "OBSERVED*"),
}

# Marshall & Palmer 1948 (J. Meteorol. 5:165) DSD; Atlas et al. 1973
# (Rev. Geophys. Space Phys. 11:1) fall speed. Cited from model
# knowledge, source not fetched here: OBSERVED* as literature constants.
MP_N0, MP_LAMBDA_COEF, MP_LAMBDA_EXP = 8000.0, 4.1, -0.21
ATLAS_A, ATLAS_B, ATLAS_C = 9.65, 10.3, 0.6
D_MIN_MM, D_MAX_MM, D_STEP_MM = 0.1, 6.0, 0.01

WET_THRESHOLD_MM = 0.0          # wet hour = rain_mm > this. Named parameter.
HOURS_PER_YEAR = 8766.0
MIN_OBSERVED_YEARS = 1.0        # station must cover >= this many years

NCEI_ACCESS_URL = "https://www.ncei.noaa.gov/access/services/data/v1"
ISD_HISTORY_URL = "https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv"

TERRAIN_CLASSES = ("flat", "complex", "coastal")


class NotParameterized(Exception):
    """A stub was asked for a number before its parameters exist."""


def sphere_diameter_mm(volume_ul: float) -> float:
    return (6.0 * volume_ul / math.pi) ** (1.0 / 3.0)


# ---------------------------------------------------------------
# STATION SELECTION
# ---------------------------------------------------------------
def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    a = (math.sin((p2 - p1) / 2) ** 2
         + math.cos(p1) * math.cos(p2) * math.sin(math.radians(lon2 - lon1) / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(a))


@dataclass
class Station:
    station_id: str
    name: str
    lat: float
    lon: float
    elev_m: Optional[float]
    begin: str
    end: str
    distance_km: float = float("nan")

    def years_listed(self) -> float:
        try:
            b, e = int(self.begin[:4]), int(self.end[:4])
            return float(e - b + 1)
        except (ValueError, TypeError):
            return 0.0


def read_isd_history(text: str) -> List[Station]:
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        try:
            lat, lon = float(row["LAT"]), float(row["LON"])
        except (ValueError, KeyError, TypeError):
            continue
        if lat == 0.0 and lon == 0.0:
            continue
        try:
            el = float(row.get("ELEV(M)", ""))
            el = None if el <= -999 else el
        except ValueError:
            el = None
        out.append(Station(row["USAF"] + row["WBAN"], row.get("STATION NAME", ""),
                           lat, lon, el, row.get("BEGIN", ""), row.get("END", "")))
    return out


def nearest_stations(stations: List[Station], lat: float, lon: float, k: int = 3,
                     min_years: float = MIN_OBSERVED_YEARS) -> List[Station]:
    cands = []
    for s in stations:
        if s.years_listed() < min_years:
            continue
        c = Station(**{**asdict(s)})
        c.distance_km = haversine_km(lat, lon, s.lat, s.lon)
        cands.append(c)
    cands.sort(key=lambda s: s.distance_km)
    return cands[:k]


# ---------------------------------------------------------------
# FETCH (network). Written to the NCEI Access Data Service v1 contract.
# NOT_TESTABLE here: ncei.noaa.gov denied by this container's egress.
# ---------------------------------------------------------------
def _get(url: str, timeout: int = 180) -> str:
    import urllib.request
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def fetch_history() -> str:
    return _get(ISD_HISTORY_URL)


def fetch_hourly_year(station_id: str, year: int) -> str:
    import urllib.parse
    q = urllib.parse.urlencode({
        "dataset": "global-hourly", "stations": station_id,
        "startDate": "%d-01-01T00:00:00" % year, "endDate": "%d-12-31T23:59:59" % year,
        "format": "csv", "dataTypes": "TMP,DEW,AA1,AA2,WND",
    })
    return _get(NCEI_ACCESS_URL + "?" + q)


# ---------------------------------------------------------------
# PARSE ISD global-hourly CSV
#   TMP/DEW "+0250,1" tenths degC, quality; +9999 missing
#   AA1/AA2 "01,0005,9,1" period h, depth tenths mm, condition, quality
#   quality 2,3,6,7 = suspect/erroneous -> dropped
# ---------------------------------------------------------------
BAD_QC = set("2367")


@dataclass
class HourRecord:
    hour: str
    t_c: Optional[float] = None
    td_c: Optional[float] = None
    rh_pct: Optional[float] = None
    precip_mm: Optional[float] = None
    precip_period_h: Optional[int] = None


def _tenths(s: str) -> Optional[float]:
    if not s:
        return None
    p = s.split(",")
    if p[0].lstrip("+-") in ("9999", "99999"):
        return None
    if len(p) > 1 and p[1] in BAD_QC:
        return None
    try:
        return int(p[0]) / 10.0
    except ValueError:
        return None


def _aa(s: str) -> Tuple[Optional[int], Optional[float]]:
    if not s:
        return None, None
    p = s.split(",")
    if len(p) < 4 or p[0] == "99" or p[1] == "9999" or p[3] in BAD_QC:
        return None, None
    try:
        return int(p[0]), int(p[1]) / 10.0
    except ValueError:
        return None, None


def rh_magnus(t_c: float, td_c: float) -> float:
    """RH % from T and dew point (Magnus, Alduchov-Eskridge 1996 coefs). DERIVED."""
    a, b = 17.625, 243.04
    return 100.0 * math.exp(a * td_c / (b + td_c)) / math.exp(a * t_c / (b + t_c))


def parse_isd_csv(text: str, hours: Optional[Dict[str, HourRecord]] = None) -> Dict[str, HourRecord]:
    """One HourRecord per clock hour. Precip: shortest-period report wins;
    overlapping METAR/SYNOP reports are never summed."""
    hours = {} if hours is None else hours
    for row in csv.DictReader(io.StringIO(text)):
        d = row.get("DATE", "")
        if len(d) < 13:
            continue
        rec = hours.setdefault(d[:13], HourRecord(hour=d[:13]))
        t, td = _tenths(row.get("TMP", "")), _tenths(row.get("DEW", ""))
        if t is not None:
            rec.t_c = t
        if td is not None:
            rec.td_c = td
        for col in ("AA1", "AA2"):
            per, dep = _aa(row.get(col, ""))
            if per and (rec.precip_period_h is None or per < rec.precip_period_h):
                rec.precip_period_h, rec.precip_mm = per, dep
    for rec in hours.values():
        if rec.t_c is not None and rec.td_c is not None:
            rec.rh_pct = min(100.0, rh_magnus(rec.t_c, rec.td_c))
    return hours


def hourly_rain(hours: Dict[str, HourRecord]) -> Dict[str, Tuple[Optional[float], bool]]:
    """hour -> (mm in that hour, came_from_multihour_report).
    None = no precip information (missing), never 0. Multi-hour totals
    are spread uniformly backward only into hours lacking a 1-h report;
    the flag keeps that blur visible, because spreading decouples rain
    from the RH/T of the hour it actually fell in."""
    keys = sorted(hours)
    out: Dict[str, Tuple[Optional[float], bool]] = {k: (None, False) for k in keys}
    for k in keys:
        if hours[k].precip_period_h == 1:
            out[k] = (hours[k].precip_mm, False)
    pos = {k: i for i, k in enumerate(keys)}
    for k in keys:
        r = hours[k]
        if r.precip_period_h and r.precip_period_h > 1 and r.precip_mm is not None:
            share = r.precip_mm / r.precip_period_h
            i = pos[k]
            for j in range(max(0, i - r.precip_period_h + 1), i + 1):
                if out[keys[j]][0] is None:
                    out[keys[j]] = (share, True)
    return out


# ---------------------------------------------------------------
# WEIGHT (STUB). weight(RH, T): relative charge separated per unit
# rain, vs lab conditions. Parameters come from Task 1 (humidity and
# temperature dependence). Every field None -> NotParameterized; None is
# never silently 1.0.
#
#   rh_ref_pct        lab RH during runs                 Task 1 field 8
#   rh_form           "exp" | "logistic"                 functional form
#   rh_slope_per_pct  dln(w)/dRH (exp) or steepness (logistic)
#   rh_half_pct       logistic midpoint (logistic only)
#   t_ref_c           lab temperature                    Task 1 field 7
#   t_slope_per_c     dln(w)/dT
#
# The form is a hypothesis. Replace it if Task 1 shows another shape;
# do not tune it to fit damage data (that would make the built-in check
# circular).
# ---------------------------------------------------------------
@dataclass
class WeightParams:
    rh_ref_pct: Optional[float] = None
    rh_form: Optional[str] = None
    rh_slope_per_pct: Optional[float] = None
    rh_half_pct: Optional[float] = None
    t_ref_c: Optional[float] = None
    t_slope_per_c: Optional[float] = None

    def missing(self) -> List[str]:
        need = ["rh_ref_pct", "rh_form", "rh_slope_per_pct", "t_ref_c", "t_slope_per_c"]
        if self.rh_form == "logistic":
            need.append("rh_half_pct")
        return [k for k in need if getattr(self, k) is None]


def weight(rh_pct: float, t_c: float, p: WeightParams) -> float:
    miss = p.missing()
    if miss:
        raise NotParameterized("weight(RH, T) missing: " + ", ".join(miss))
    if p.rh_form == "exp":
        f_rh = math.exp(p.rh_slope_per_pct * (rh_pct - p.rh_ref_pct))
    elif p.rh_form == "logistic":
        def lg(x):
            return 1.0 / (1.0 + math.exp(p.rh_slope_per_pct * (x - p.rh_half_pct)))
        f_rh = lg(rh_pct) / lg(p.rh_ref_pct)
    else:
        raise NotParameterized("rh_form must be 'exp' or 'logistic'")
    return f_rh * math.exp(p.t_slope_per_c * (t_c - p.t_ref_c))


def ion_factor(ion_mmol_l: float, *_args) -> float:
    """PROPOSED*** slot, NOT in the index. Carried hypothesis: charge
    separation peaks in low-conductivity water while electrochemical
    attack rises with ions, so damage per drop is worst mid-gradient.
    Not tested here; bench work required. Rain chemistry per site
    (e.g. NADP/NTN Na+, Cl-) would feed it."""
    raise NotParameterized("ion_factor is a PROPOSED hypothesis slot; no form exists")


# ---------------------------------------------------------------
# DROP COUNT (named runoff geometry; no hidden defaults)
#   slide drops = rain_depth_m x catchment_m2 x cos(tilt)
#                 x runoff_fraction / drop_volume_m3
#   catchment_m2      panel area whose runoff passes one slide track
#   runoff_fraction   share of intercepted water leaving as discrete
#                     sliding drops (vs film flow, splash, evaporation)
#   drop_volume_ul    volume of a sliding drop (lab: 35 uL OBSERVED*)
# ---------------------------------------------------------------
@dataclass
class DropParams:
    drop_volume_ul: Optional[float] = None
    catchment_m2: Optional[float] = None
    runoff_fraction: Optional[float] = None

    def missing(self) -> List[str]:
        return [k for k, v in asdict(self).items() if v is None]


def slide_drops(rain_mm: float, tilt_deg: float, p: DropParams) -> float:
    miss = p.missing()
    if miss:
        raise NotParameterized("slide_drops missing: " + ", ".join(miss))
    vol_m3 = rain_mm * 1e-3 * p.catchment_m2 * math.cos(math.radians(tilt_deg)) * p.runoff_fraction
    return vol_m3 / (p.drop_volume_ul * 1e-9)


def impact_drops_per_m2(rain_mm_h: float) -> Tuple[float, float]:
    """Alternative counting rule: raindrops STRIKING a horizontal m^2 in
    one hour at rate R (Marshall-Palmer x Atlas, N0 rescaled so volume
    flux == R). Returns (count, fraction with D >= lab drop D).
    Kept to show the rule choice: per cm2 of catchment, impact counting
    exceeds runoff counting (35 uL slide drops) by a factor of ~160 at
    1 mm/h and ~50 at 10 mm/h for the same rain. DERIVED from these two
    models only."""
    if rain_mm_h <= 0:
        return 0.0, 0.0
    lam = MP_LAMBDA_COEF * rain_mm_h ** MP_LAMBDA_EXP
    d_lab = sphere_diameter_mm(LAB["drop_volume_ul"][0])
    num = vol = ge = 0.0
    for i in range(int(round((D_MAX_MM - D_MIN_MM) / D_STEP_MM))):
        d = D_MIN_MM + (i + 0.5) * D_STEP_MM
        f = MP_N0 * math.exp(-lam * d) * max(0.0, ATLAS_A - ATLAS_B * math.exp(-ATLAS_C * d)) * D_STEP_MM
        num += f
        vol += f * (math.pi / 6.0) * (d * 1e-3) ** 3
        if d >= d_lab:
            ge += f
    k = rain_mm_h / (vol * 3.6e6)
    return num * 3600.0 * k, ge / num


# ---------------------------------------------------------------
# UNCERTAINTY BAND (PROPOSED***: rule of thumb, not calibrated)
#   base 0.10
#   distance    <=5 km +0 | <=25 +0.15 | <=50 +0.35 | >50 +0.60
#   |elev d|    <=50 m +0 | <=200 +0.15 | >200 +0.35 | unknown +0.25
#   terrain     flat +0 | complex +0.25 | unknown +0.20
#               coastal: +0.10 if <=5 km, else +0.40 (sea-breeze boundary)
#   class       TIGHT <=0.20 | MEDIUM <=0.50 | WIDE >0.50
#   fit_weight  1/band^2  -- loose sites down-weighted, never dropped
# ---------------------------------------------------------------
BAND_RULE_TAG = "PROPOSED***"


def uncertainty_band(distance_km: Optional[float], elev_delta_m: Optional[float],
                     terrain: Optional[str]) -> Tuple[Optional[float], str, List[str]]:
    if distance_km is None or distance_km != distance_km:
        return None, "UNBOUNDED", ["no station distance"]
    b, why = 0.10, []
    for lim, add in ((5, 0.0), (25, 0.15), (50, 0.35)):
        if distance_km <= lim:
            b += add
            break
    else:
        add = 0.60
        b += add
    if distance_km > 5:
        why.append("distance %.1f km" % distance_km)
    if elev_delta_m is None:
        b += 0.25
        why.append("elevation delta unknown")
    elif abs(elev_delta_m) > 200:
        b += 0.35
        why.append("elev delta %.0f m" % elev_delta_m)
    elif abs(elev_delta_m) > 50:
        b += 0.15
        why.append("elev delta %.0f m" % elev_delta_m)
    if terrain not in TERRAIN_CLASSES:
        b += 0.20
        why.append("terrain unknown")
    elif terrain == "complex":
        b += 0.25
        why.append("complex terrain")
    elif terrain == "coastal":
        if distance_km > 5:
            b += 0.40
            why.append("coastal, station >5 km: sea-breeze boundary")
        else:
            b += 0.10
            why.append("coastal")
    cls = "TIGHT" if b <= 0.20 else ("MEDIUM" if b <= 0.50 else "WIDE")
    return b, cls, why


# ---------------------------------------------------------------
# PER-SITE PROFILE
# ---------------------------------------------------------------
@dataclass
class SiteResult:
    row: Dict[str, str] = field(default_factory=dict)


def site_profile(hours: Dict[str, HourRecord], tilt_deg: float, wp: WeightParams,
                 dp: DropParams, wet_threshold_mm: float = WET_THRESHOLD_MM) -> Dict[str, object]:
    rain = hourly_rain(hours)
    observed = sum(1 for v, _ in rain.values() if v is not None)
    years = observed / HOURS_PER_YEAR
    wet = rh_miss = 0
    total = multih = idx = 0.0
    can_w = not wp.missing()
    for k in sorted(rain):
        mm, spread = rain[k]
        if mm is None or mm <= wet_threshold_mm:
            continue                       # FILTER: precipitation hours only
        wet += 1
        total += mm
        if spread:
            multih += mm
        h = hours[k]
        if h.rh_pct is None or h.t_c is None:
            rh_miss += 1
            continue
        if can_w:
            idx += mm * weight(h.rh_pct, h.t_c, wp)
    out = {
        "hours_observed": observed,
        "years_observed": round(years, 3),
        "wet_hours_total": wet,
        "wet_hours_per_year": round(wet / years, 2) if years else "",
        "rain_total_mm": round(total, 2),
        "rain_mm_per_year": round(total / years, 2) if years else "",
        "frac_rain_from_multihour": round(multih / total, 4) if total else "",
        "wet_hours_rh_or_t_missing": rh_miss,
    }
    if can_w:
        out["index_weighted"] = round(idx, 4)
        out["index_per_year"] = round(idx / years, 4) if years else ""
        out["index_status"] = "STUB_FORM_PARAMETERIZED" + ("; RH/T gaps excluded" if rh_miss else "")
    else:
        out["index_weighted"] = ""
        out["index_per_year"] = ""
        out["index_status"] = "NOT_PARAMETERIZED (weight awaits Task 1)"
    if not dp.missing() and years:
        out["slide_drops_per_year"] = round(slide_drops(total / years, tilt_deg, dp), 1)
        out["drop_status"] = "DERIVED from named params"
    else:
        out["slide_drops_per_year"] = ""
        out["drop_status"] = "NOT_PARAMETERIZED: " + ", ".join(dp.missing()) if dp.missing() else "no years"
    return out


CSV_COLUMNS = [
    "site_id", "dataset_ref", "lat", "lon", "coord_source", "site_elev_m",
    "terrain_class", "terrain_source", "tilt_deg",
    "station_id", "station_name", "station_elev_m", "distance_km", "elev_delta_m",
    "record_begin", "record_end",
    "hours_observed", "years_observed", "wet_hours_total", "wet_hours_per_year",
    "rain_total_mm", "rain_mm_per_year", "frac_rain_from_multihour",
    "wet_hours_rh_or_t_missing",
    "index_weighted", "index_per_year", "index_status",
    "slide_drops_per_year", "drop_status",
    "uncertainty_band_frac", "band_class", "index_lo", "index_hi", "fit_weight",
    "band_reasons", "band_rule_tag",
    "damage_rate", "damage_metric", "damage_source",
    "status",
]

COLUMN_TAGS = {
    "lat": "OBSERVED* (per coord_source)", "lon": "OBSERVED* (per coord_source)",
    "terrain_class": "per terrain_source", "station_elev_m": "OBSERVED (isd-history)",
    "distance_km": "DERIVED", "elev_delta_m": "DERIVED",
    "hours_observed": "OBSERVED", "wet_hours_total": "OBSERVED", "rain_total_mm": "OBSERVED",
    "wet_hours_per_year": "DERIVED", "rain_mm_per_year": "DERIVED",
    "frac_rain_from_multihour": "DERIVED", "index_weighted": "DERIVED x STUB weight",
    "slide_drops_per_year": "DERIVED x named params (PROPOSED geometry)",
    "uncertainty_band_frac": BAND_RULE_TAG, "band_class": BAND_RULE_TAG,
    "fit_weight": BAND_RULE_TAG, "damage_rate": "OBSERVED (per damage_source)",
}


def _f(s) -> Optional[float]:
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def run(sites_path: str, out_path: str, isd_history_path: Optional[str] = None,
        hourly_dir: Optional[str] = None, do_fetch: bool = False,
        wp: Optional[WeightParams] = None, dp: Optional[DropParams] = None,
        wet_threshold_mm: float = WET_THRESHOLD_MM,
        min_years: float = MIN_OBSERVED_YEARS) -> List[Dict[str, object]]:
    wp = wp or WeightParams()
    dp = dp or DropParams()
    with open(sites_path, encoding="utf-8") as f:
        sites = list(csv.DictReader(f))
    stations: List[Station] = []
    if isd_history_path and os.path.exists(isd_history_path):
        with open(isd_history_path, encoding="utf-8") as f:
            stations = read_isd_history(f.read())
    rows = []
    for s in sites:
        r = {c: "" for c in CSV_COLUMNS}
        for c in ("site_id", "dataset_ref", "lat", "lon", "coord_source", "site_elev_m",
                  "terrain_class", "terrain_source", "tilt_deg",
                  "damage_rate", "damage_metric", "damage_source"):
            r[c] = s.get(c, "")
        r["band_rule_tag"] = BAND_RULE_TAG
        lat, lon = _f(s.get("lat")), _f(s.get("lon"))
        if lat is None or lon is None:
            r["status"] = "NO_COORDINATES (Task 3: NOT FOUND)"
            r["band_class"] = "UNBOUNDED"
            rows.append(r)
            continue
        if not stations:
            r["status"] = "NO_STATION_LIST (isd-history not available; NOAA unreachable here)"
            r["band_class"] = "UNBOUNDED"
            rows.append(r)
            continue
        st = nearest_stations(stations, lat, lon, k=1, min_years=min_years)
        if not st:
            r["status"] = "NO_STATION"
            rows.append(r)
            continue
        st = st[0]
        site_el = _f(s.get("site_elev_m"))
        ed = (site_el - st.elev_m) if (site_el is not None and st.elev_m is not None) else None
        r.update({"station_id": st.station_id, "station_name": st.name,
                  "station_elev_m": st.elev_m if st.elev_m is not None else "",
                  "distance_km": round(st.distance_km, 2),
                  "elev_delta_m": round(ed, 1) if ed is not None else "",
                  "record_begin": st.begin, "record_end": st.end})
        band, cls, why = uncertainty_band(st.distance_km, ed, s.get("terrain_class") or None)
        r["uncertainty_band_frac"] = round(band, 3) if band is not None else ""
        r["band_class"] = cls
        r["band_reasons"] = "; ".join(why)
        r["fit_weight"] = round(1.0 / band ** 2, 3) if band else ""
        hours: Dict[str, HourRecord] = {}
        got = 0
        try:
            y0, y1 = int(st.begin[:4]), int(st.end[:4])
        except ValueError:
            y0 = y1 = 0
        for y in range(y0, y1 + 1):
            path = os.path.join(hourly_dir, "%s_%d.csv" % (st.station_id, y)) if hourly_dir else None
            text = None
            if path and os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    text = f.read()
            elif do_fetch:
                try:
                    text = fetch_hourly_year(st.station_id, y)
                    if path:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(text)
                except Exception as e:      # network failure is a recorded state
                    r["status"] = "FETCH_FAILED %s: %s" % (y, type(e).__name__)
                    break
            if text:
                parse_isd_csv(text, hours)
                got += 1
        if not hours:
            r["status"] = r["status"] or "NO_HOURLY_DATA"
            rows.append(r)
            continue
        tilt = _f(s.get("tilt_deg"))
        prof = site_profile(hours, tilt if tilt is not None else 0.0, wp, dp, wet_threshold_mm)
        r.update(prof)
        if tilt is None and not dp.missing():
            r["drop_status"] += "; tilt unknown, cos=1 used"
        iy = _f(prof.get("index_per_year"))
        if iy is not None and band is not None:
            r["index_lo"] = round(iy * (1 - band), 4)
            r["index_hi"] = round(iy * (1 + band), 4)
        r["status"] = r["status"] or "OK (%d station-years read)" % got
        rows.append(r)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return rows


# ---------------------------------------------------------------
# BUILT-IN CHECK
# ---------------------------------------------------------------
def _ranks(xs: List[float]) -> List[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    rk = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for m in range(i, j + 1):
            rk[order[m]] = (i + j) / 2.0 + 1
        i = j + 1
    return rk


def spearman(x: List[float], y: List[float]) -> Optional[float]:
    if len(x) < 3:
        return None
    rx, ry = _ranks(x), _ranks(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    return sxy / math.sqrt(sxx * syy) if sxx and syy else None


def gradient_check(rows: List[Dict[str, object]], min_n: int = 5, margin: float = 0.2) -> Dict[str, object]:
    """Damage vs index correlation by band class, per damage metric
    (metrics are never pooled). Verdicts:
      GRADIENT_PRESENT  rho_TIGHT - rho_WIDE >= margin and rho_TIGHT > 0
      INVERTED          rho_WIDE - rho_TIGHT >= margin
      NO_GRADIENT       otherwise -> index not measuring what it claims
      NOT_TESTABLE      fewer than min_n usable sites in TIGHT or WIDE
    A GRADIENT_PRESENT verdict is necessary, not sufficient: tight-band
    sites (often flat, near airports) can differ systematically from
    loose ones in coating system, age, or pollution."""
    by_metric: Dict[str, Dict[str, List[Tuple[float, float]]]] = {}
    for r in rows:
        d, i = _f(r.get("damage_rate")), _f(r.get("index_per_year"))
        cls = r.get("band_class")
        if d is None or i is None or cls not in ("TIGHT", "MEDIUM", "WIDE"):
            continue
        by_metric.setdefault(r.get("damage_metric") or "unspecified", {}).setdefault(cls, []).append((i, d))
    out = {"rule": "rho(damage, index) by band class; min_n=%d margin=%.2f" % (min_n, margin),
           "tag": "DERIVED test of a PROPOSED index", "metrics": {}}
    if not by_metric:
        out["verdict"] = "NOT_TESTABLE"
        out["reason"] = "no site has both a damage rate and a computed index"
        return out
    verdicts = []
    for m, groups in by_metric.items():
        res = {}
        for cls in ("TIGHT", "MEDIUM", "WIDE"):
            pts = groups.get(cls, [])
            res[cls] = {"n": len(pts), "rho": spearman([p[0] for p in pts], [p[1] for p in pts])}
        t, w = res["TIGHT"], res["WIDE"]
        if t["n"] < min_n or w["n"] < min_n or t["rho"] is None or w["rho"] is None:
            v = "NOT_TESTABLE"
        elif t["rho"] - w["rho"] >= margin and t["rho"] > 0:
            v = "GRADIENT_PRESENT"
        elif w["rho"] - t["rho"] >= margin:
            v = "INVERTED"
        else:
            v = "NO_GRADIENT"
        res["verdict"] = v
        out["metrics"][m] = res
        verdicts.append(v)
    out["verdict"] = verdicts[0] if len(set(verdicts)) == 1 else "MIXED: " + ",".join(verdicts)
    return out


# ---------------------------------------------------------------
# SELFTEST (offline)
# ---------------------------------------------------------------
FIXTURE_HOURLY = """STATION,DATE,SOURCE,REPORT_TYPE,TMP,DEW,AA1,AA2
00000199999,2020-07-01T00:53:00,7,FM-15,"+0250,1","+0240,1","01,0000,9,1",
00000199999,2020-07-01T01:53:00,7,FM-15,"+0240,1","+0235,1","01,0050,9,1",
00000199999,2020-07-01T02:53:00,7,FM-15,"+0230,1","+0228,1","01,0100,9,1",
00000199999,2020-07-01T03:53:00,7,FM-15,"+9999,9","+9999,9","01,0020,9,1",
00000199999,2020-07-01T04:53:00,7,FM-15,"+0220,1","+0150,1",,
00000199999,2020-07-01T05:53:00,7,FM-15,"+0220,1","+0150,1","01,0030,9,3",
00000199999,2020-07-01T05:59:00,7,FM-12,,,,"06,0060,9,1"
"""

FIXTURE_HISTORY = """"USAF","WBAN","STATION NAME","CTRY","STATE","ICAO","LAT","LON","ELEV(M)","BEGIN","END"
"000001","99999","NEAR","US","NC","","34.02","-78.00","5","20190101","20201231"
"000002","99999","FAR","US","NC","","35.00","-79.00","300","19730101","20251231"
"000003","99999","ZERO","US","","","0.0","0.0","0","19730101","20251231"
"000004","99999","NEW","US","NC","","34.00","-78.00","5","20250101","20250101"
"""


def selftest() -> int:
    import tempfile
    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))

    ck("lab 35 uL -> 4.06 mm", abs(sphere_diameter_mm(35) - 4.058) < 0.01)
    ck("haversine 1 deg lat", abs(haversine_km(0, 0, 1, 0) - 111.19) < 0.1)
    sts = read_isd_history(FIXTURE_HISTORY)
    ck("history skips 0,0", all(s.name != "ZERO" for s in sts))
    near = nearest_stations(sts, 34.0, -78.0, k=2, min_years=1)
    ck("nearest with >=1 listed year", near[0].name == "NEW")
    ck("min_years=2 skips 1-year record", nearest_stations(sts, 34.0, -78.0, k=1, min_years=2)[0].name == "NEAR")
    ck("too-short record excluded", "NEW" not in [s.name for s in nearest_stations(sts, 34.0, -78.0, k=5, min_years=2)])
    ck("RH(T==Td)=100", abs(rh_magnus(20, 20) - 100) < 1e-9)

    hrs = parse_isd_csv(FIXTURE_HOURLY)
    rain = hourly_rain(hrs)
    ck("0.0 is a measured dry hour", rain["2020-07-01T00"][0] == 0.0)
    ck("bad-QC 1-h dropped; AA2 6-h kept", hrs["2020-07-01T05"].precip_period_h == 6)
    ck("6-h spread only into uncovered hours, flagged",
       rain["2020-07-01T04"] == (1.0, True) and rain["2020-07-01T01"] == (5.0, False))

    prof = site_profile(hrs, 30.0, WeightParams(), DropParams())
    ck("dry hour excluded by wet filter", prof["wet_hours_total"] == 5)
    ck("rain total 5+10+2+1+1", abs(prof["rain_total_mm"] - 19.0) < 1e-9)
    ck("index NOT_PARAMETERIZED by default", prof["index_weighted"] == "" and "NOT_PARAMETERIZED" in prof["index_status"])
    ck("RH/T-missing wet hour counted", prof["wet_hours_rh_or_t_missing"] == 1)
    ck("multihour fraction visible", abs(prof["frac_rain_from_multihour"] - 2.0 / 19.0) < 1e-3)
    try:
        weight(80, 20, WeightParams())
        ck("weight refuses without params", False)
    except NotParameterized:
        ck("weight refuses without params", True)
    unit = WeightParams(rh_ref_pct=50, rh_form="exp", rh_slope_per_pct=0.0, t_ref_c=20, t_slope_per_c=0.0)
    p2 = site_profile(hrs, 30.0, unit, DropParams())
    ck("unit weight index == rain with RH/T present", abs(p2["index_weighted"] - 17.0) < 1e-9)
    lg = WeightParams(rh_ref_pct=50, rh_form="logistic", rh_slope_per_pct=0.2, rh_half_pct=70,
                      t_ref_c=20, t_slope_per_c=0.0)
    ck("logistic weight == 1 at reference", abs(weight(50, 20, lg) - 1.0) < 1e-12)
    ck("logistic falls with RH", weight(90, 20, lg) < weight(40, 20, lg))
    try:
        ion_factor(1.0)
        ck("ion_factor is a refusal slot", False)
    except NotParameterized:
        ck("ion_factor is a refusal slot", True)

    dp = DropParams(drop_volume_ul=35.0, catchment_m2=1e-4, runoff_fraction=1.0)
    ck("runoff count: 1000 mm, 1 cm2, 30 deg -> ~2474 drops",
       abs(slide_drops(1000.0, 30.0, dp) - 2474.36) < 0.1)
    try:
        slide_drops(1.0, 0.0, DropParams(drop_volume_ul=35.0))
        ck("drop count refuses missing geometry", False)
    except NotParameterized:
        ck("drop count refuses missing geometry", True)
    n_imp, frac = impact_drops_per_m2(10.0)
    ratio = (n_imp / 10.0 * 1e-4) / slide_drops(1.0, 0.0, dp)
    ck("impact/runoff count ratio ~50 at 10 mm/h (rule choice visible)", 30 < ratio < 80)
    ck("lab-size impact drops rare at 10 mm/h", frac < 0.01)

    b, c, _ = uncertainty_band(2.0, 10.0, "flat")
    ck("2 km flat, small dz -> TIGHT", c == "TIGHT")
    b2, c2, _ = uncertainty_band(40.0, 300.0, "complex")
    ck("40 km complex, 300 m -> WIDE", c2 == "WIDE")
    _, c3, w3 = uncertainty_band(12.0, 5.0, "coastal")
    _, c4, _ = uncertainty_band(12.0, 5.0, "flat")
    ck("coastal widens vs flat at same gap (sea breeze)", c3 != c4 and any("sea-breeze" in x for x in w3))
    ck("no distance -> UNBOUNDED", uncertainty_band(None, None, None)[1] == "UNBOUNDED")

    # end-to-end run on fixtures
    td = tempfile.mkdtemp()
    hp = os.path.join(td, "hist.csv")
    with open(hp, "w") as f:
        f.write(FIXTURE_HISTORY)
    hd = os.path.join(td, "hourly")
    os.mkdir(hd)
    with open(os.path.join(hd, "00000199999_2020.csv"), "w") as f:
        f.write(FIXTURE_HOURLY)
    sp = os.path.join(td, "sites.csv")
    with open(sp, "w") as f:
        f.write("site_id,lat,lon,site_elev_m,terrain_class,tilt_deg\n"
                "S1,34.0,-78.0,5,flat,30\nS2,,,,,\n")
    rows = run(sp, os.path.join(td, "out.csv"), hp, hd, False, unit, dp, min_years=2)
    ck("run: site with coords computed", rows[0]["status"].startswith("OK") and rows[0]["band_class"] == "TIGHT")
    ck("run: band columns present", rows[0]["index_lo"] != "" and rows[0]["fit_weight"] != "")
    ck("run: no-coord site kept with reason", rows[1]["status"].startswith("NO_COORDINATES"))
    rows_nohist = run(sp, os.path.join(td, "out2.csv"), None, None, False)
    ck("run: no station list -> stated, not zero", rows_nohist[0]["status"].startswith("NO_STATION_LIST")
       and rows_nohist[0]["index_weighted"] == "")

    # built-in check on synthetic damage: tight tracks, wide is noise
    syn = []
    noise = [0.9, 0.1, 0.7, 0.3, 0.5, 0.2, 0.8]
    for i in range(7):
        syn.append({"band_class": "TIGHT", "index_per_year": i, "damage_rate": 2 * i + 1, "damage_metric": "m"})
        syn.append({"band_class": "WIDE", "index_per_year": i, "damage_rate": noise[i], "damage_metric": "m"})
    ck("check: GRADIENT_PRESENT when tight tracks, wide does not", gradient_check(syn)["verdict"] == "GRADIENT_PRESENT")
    flat = [dict(r, damage_rate=r["index_per_year"]) for r in syn]
    ck("check: NO_GRADIENT when both track equally", gradient_check(flat)["verdict"] == "NO_GRADIENT")
    ck("check: NOT_TESTABLE with no damage", gradient_check(rows_nohist)["verdict"] == "NOT_TESTABLE")
    two = syn + [dict(r, damage_metric="other") for r in flat]
    ck("check: metrics never pooled", "MIXED" in gradient_check(two)["verdict"])

    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("PASS " if ok else "FAIL ") + n)
    print("%d checks, %d failed" % (len(checks), len(bad)))
    return 1 if bad else 0


# ---------------------------------------------------------------
# CLI
# ---------------------------------------------------------------
def _opt(argv, name, cast=str, default=None):
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv):
            return cast(argv[i + 1])
    return default


def main(argv: List[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(open(__file__, encoding="utf-8").read().split("import csv")[0])
        return 2
    if argv[0] == "--selftest":
        return selftest()
    if argv[0] == "fetch-history":
        text = fetch_history()
        with open(_opt(argv, "--out", default="isd-history.csv"), "w", encoding="utf-8") as f:
            f.write(text)
        return 0
    if argv[0] == "fetch" and len(argv) >= 3:
        text = fetch_hourly_year(argv[1], int(argv[2]))
        with open(_opt(argv, "--out", default="%s_%s.csv" % (argv[1], argv[2])), "w", encoding="utf-8") as f:
            f.write(text)
        return 0
    if argv[0] == "run":
        wp = WeightParams()
        wpath = _opt(argv, "--weight-params")
        if wpath:
            with open(wpath, encoding="utf-8") as f:
                wp = WeightParams(**json.load(f))
        dp = DropParams(_opt(argv, "--drop-volume-ul", float), _opt(argv, "--catchment-m2", float),
                        _opt(argv, "--runoff-fraction", float))
        out = _opt(argv, "--out", default="index_by_site.csv")
        hd = _opt(argv, "--hourly-dir")
        if hd:
            os.makedirs(hd, exist_ok=True)
        rows = run(_opt(argv, "--sites", default="sites.csv"), out,
                   _opt(argv, "--isd-history"), hd, "--fetch" in argv, wp, dp,
                   _opt(argv, "--wet-threshold-mm", float, WET_THRESHOLD_MM),
                   _opt(argv, "--min-years", float, MIN_OBSERVED_YEARS))
        chk = gradient_check(rows)
        chk_path = os.path.join(os.path.dirname(os.path.abspath(out)), "gradient_check.json")
        with open(chk_path, "w", encoding="utf-8") as f:
            json.dump({"status": "co-authored", "column_tags": COLUMN_TAGS, "check": chk}, f, indent=2)
            f.write("\n")
        for r in rows:
            print("%-28s %-8s %s" % (r["site_id"], r["band_class"] or "-", r["status"]))
        print("BUILT-IN CHECK:", chk["verdict"], "-", chk.get("reason", ""))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
