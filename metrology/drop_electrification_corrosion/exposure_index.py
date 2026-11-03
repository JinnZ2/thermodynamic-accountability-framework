#!/usr/bin/env python3
# exposure_index.py -- CC0, stdlib-only, python >= 3.8
#
# TASK 2 of WORK_ORDER.md: charging-weighted exposure index pipeline.
#
# Purpose: put lab drop counts (Ni et al. 2026, ~3000 slid drops ->
# pinholes) and outdoor panel exposure years on one axis: drops that
# reach and slide on a coated panel, weighted by how much charge each
# one is expected to separate. The weight function is a STUB until
# Task 1 (methods_extract.md) supplies its parameters.
#
# This module does NOT test the mechanism. It builds the common
# denominator.
#
# ENERGY MAP (where the flow goes, where it is lost, where it is held)
#
#   site (lat, lon, tilt, years)               <- panel_datasets.md
#      |
#   nearest_stations()  haversine over isd-history.csv
#      |                 LOSS: station != panel; distance is reported
#   fetch_hourly()      NCEI global-hourly CSV        [network]
#      |                 LOSS: missing hours -> coverage_fraction
#   parse_isd_csv()     TMP, DEW, AA1, WND  -> HourRecord   MEASURED
#      |
#   hourly_rain()       AA1 depth / period -> mm/h        MEASURED
#      |
#   drop_spectrum(R)    Marshall-Palmer N(D) x Atlas v(D),
#      |                 rescaled so volume flux == measured R   MODELLED
#      |                 -> number flux per m^2 per h, by size bin
#   panel_flux()        x cos(tilt); wind-driven term stubbed  MODELLED
#      |
#   weight()            w(D, RH, T, ion, slide_len)            STUB
#      |                 raises NotParameterized unless params given
#      v
#   ExposureProfile     a VECTOR, never one scalar:
#                         hours, coverage, wet_hours,
#                         drops_per_m2 (unweighted),
#                         drops_per_m2 by RH bin and by size bin,
#                         fraction of drops >= lab drop volume,
#                         weighted_index (or NOT_PARAMETERIZED)
#
#   lab_equivalence()   drops on a declared catchment -> years to
#                       reach the lab drop count. Catchment must be
#                       declared; there is no default.
#
# BOTTLENECKS, named so they are not hidden in the number:
#   B1 drop size.  35 uL is a 4.06 mm equivalent sphere. Natural rain
#      number flux is dominated by drops < 2 mm. A drop that SLIDES on a
#      panel is usually a coalesced aggregate, not one impact drop. The
#      impact-drop -> sliding-drop transfer function is not modelled
#      here; it is the largest unscoped term. size_fraction_ge() reports
#      the raw mismatch so it stays visible.
#   B2 ion load.  Station data carries no rain chemistry. Coastal rain
#      (e.g. Kure Beach) is salt-loaded; inland rain is near-deionized.
#      This is exactly the variable that separates interfacial charge
#      separation from solute-driven electrochemistry (WORK_ORDER Task 1
#      rationale). Slot: ion_mmol_per_l per hour or per site; candidate
#      source NADP/NTN weekly precipitation chemistry (Na+, Cl-).
#   B3 shelter.  Without sheltered controls (panel_datasets.md) the rain
#      term cannot be separated from humidity / deposition / UV.
#
# STATUS TAGS on every output field:
#   MEASURED          straight from station record
#   MODELLED          physics model with stated parameters
#   STUB              placeholder function, shape only
#   NOT_PARAMETERIZED weight requested but parameters absent
#   NOT_TESTABLE      needs network this environment does not have
#
# CLI:
#   python3 exposure_index.py --selftest
#   python3 exposure_index.py --csv hourly.csv --tilt 30 [--json]
#   python3 exposure_index.py --nearest isd-history.csv LAT LON [--k 3]
#   python3 exposure_index.py --fetch STATION START END --out f.csv
#        (NOT_TESTABLE here: ncei.noaa.gov is blocked by this
#         container's egress allowlist; written to the NCEI Access
#         Data Service v1 contract, run it where NOAA is reachable)

import csv
import io
import json
import math
import sys
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------
LAB_DROP_VOLUME_UL = 35.0          # WORK_ORDER context line
LAB_DROP_COUNT_TO_PINHOLE = 3000   # WORK_ORDER context line ("~3000")
LAB_SLIDE_LENGTH_CM = 4.0          # WORK_ORDER context line

# Marshall-Palmer (1948): N(D) = N0 exp(-L D), N0 m^-3 mm^-1, L mm^-1
MP_N0 = 8000.0
MP_LAMBDA_COEF = 4.1
MP_LAMBDA_EXP = -0.21

# Atlas et al. (1973) terminal velocity, D in mm, v in m/s
ATLAS_A, ATLAS_B, ATLAS_C = 9.65, 10.3, 0.6

D_MIN_MM, D_MAX_MM, D_STEP_MM = 0.1, 6.0, 0.01

RH_BINS = (0, 40, 60, 75, 85, 95, 101)        # percent, right-open
SIZE_BINS_MM = (0.1, 0.5, 1.0, 2.0, 3.0, 4.0, 6.0)

ISD_HISTORY_URL = "https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv"
NCEI_ACCESS_URL = "https://www.ncei.noaa.gov/access/services/data/v1"


class NotParameterized(Exception):
    """Weight requested before Task 1 supplied its parameters."""


def sphere_diameter_mm(volume_ul: float) -> float:
    """Equivalent-sphere diameter (mm) of a drop of volume_ul (1 uL = 1 mm^3)."""
    return (6.0 * volume_ul / math.pi) ** (1.0 / 3.0)


LAB_DROP_DIAMETER_MM = sphere_diameter_mm(LAB_DROP_VOLUME_UL)


# ---------------------------------------------------------------
# LAYER 0: station selection
# ---------------------------------------------------------------
def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


@dataclass
class Station:
    station_id: str          # USAF+WBAN, the NCEI access id
    name: str
    lat: float
    lon: float
    begin: str               # YYYYMMDD
    end: str
    distance_km: float = float("nan")


def nearest_stations(isd_history_text: str, lat: float, lon: float, k: int = 3,
                     need_begin: Optional[str] = None,
                     need_end: Optional[str] = None) -> List[Station]:
    """Rank isd-history.csv rows by distance; optionally require coverage
    of [need_begin, need_end] (YYYYMMDD). Distance is always reported:
    station != panel is a LOSS term, not a detail."""
    out = []
    for row in csv.DictReader(io.StringIO(isd_history_text)):
        try:
            slat, slon = float(row["LAT"]), float(row["LON"])
        except (ValueError, KeyError):
            continue
        if slat == 0.0 and slon == 0.0:
            continue
        b, e = row.get("BEGIN", ""), row.get("END", "")
        if need_begin and b and b > need_begin:
            continue
        if need_end and e and e < need_end:
            continue
        st = Station(row["USAF"] + row["WBAN"], row.get("STATION NAME", ""),
                     slat, slon, b, e)
        st.distance_km = haversine_km(lat, lon, slat, slon)
        out.append(st)
    out.sort(key=lambda s: s.distance_km)
    return out[:k]


# ---------------------------------------------------------------
# LAYER 1: fetch (network; NOT_TESTABLE in this container)
# ---------------------------------------------------------------
def fetch_hourly(station_id: str, start: str, end: str, timeout: int = 120) -> str:
    """NCEI Access Data Service v1, dataset global-hourly, CSV.
    start/end ISO 'YYYY-MM-DD'. Chunk long ranges by year at the caller;
    the service caps response size."""
    import urllib.parse
    import urllib.request
    q = urllib.parse.urlencode({
        "dataset": "global-hourly", "stations": station_id,
        "startDate": start + "T00:00:00", "endDate": end + "T23:59:59",
        "format": "csv", "units": "metric",
    })
    with urllib.request.urlopen(NCEI_ACCESS_URL + "?" + q, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


# ---------------------------------------------------------------
# LAYER 2: parse ISD global-hourly CSV
#   TMP "+0250,1"        tenths degC, quality     missing +9999
#   DEW "+0180,1"        tenths degC, quality     missing +9999
#   AA1 "01,0005,9,1"    period h, depth tenths mm, cond, quality
#                        missing period 99 / depth 9999
#   WND "180,1,N,0046,1" dir, q, type, speed tenths m/s, q  missing 9999
# Quality codes 2,3,6,7 (suspect/erroneous) are dropped.
# ---------------------------------------------------------------
BAD_QC = set("2367")


@dataclass
class HourRecord:
    hour: str                      # 'YYYY-MM-DDTHH'
    t_c: Optional[float] = None
    td_c: Optional[float] = None
    rh_pct: Optional[float] = None
    precip_mm: Optional[float] = None
    precip_period_h: Optional[int] = None
    wind_ms: Optional[float] = None
    report_types: List[str] = field(default_factory=list)


def _signed_tenths(s: str) -> Optional[float]:
    if not s:
        return None
    parts = s.split(",")
    v = parts[0]
    if v.lstrip("+-") in ("9999", "99999"):
        return None
    if len(parts) > 1 and parts[1] in BAD_QC:
        return None
    try:
        return int(v) / 10.0
    except ValueError:
        return None


def _aa1(s: str) -> Tuple[Optional[int], Optional[float]]:
    if not s:
        return None, None
    p = s.split(",")
    if len(p) < 4:
        return None, None
    if p[0] == "99" or p[1] == "9999" or p[3] in BAD_QC:
        return None, None
    try:
        return int(p[0]), int(p[1]) / 10.0
    except ValueError:
        return None, None


def _wind(s: str) -> Optional[float]:
    if not s:
        return None
    p = s.split(",")
    if len(p) < 5 or p[3] == "9999" or p[4] in BAD_QC:
        return None
    try:
        return int(p[3]) / 10.0
    except ValueError:
        return None


def rh_magnus(t_c: float, td_c: float) -> float:
    """Relative humidity (%) from T and dew point, Magnus (Alduchov-Eskridge)."""
    a, b = 17.625, 243.04
    return 100.0 * math.exp(a * td_c / (b + td_c)) / math.exp(a * t_c / (b + t_c))


def parse_isd_csv(text: str) -> Dict[str, HourRecord]:
    """Collapse all reports in an hour into one HourRecord.
    T/Td: last valid value in the hour. Precip: the 1-hour AA1 report if
    any; otherwise the shortest-period report, kept with its period so
    hourly_rain() can spread it. Never summed across overlapping reports
    (METAR + SYNOP double-count the same rain)."""
    hours: Dict[str, HourRecord] = {}
    for row in csv.DictReader(io.StringIO(text)):
        d = row.get("DATE", "")
        if len(d) < 13:
            continue
        h = d[:13]
        rec = hours.setdefault(h, HourRecord(hour=h))
        rec.report_types.append(row.get("REPORT_TYPE", "").strip())
        t = _signed_tenths(row.get("TMP", ""))
        td = _signed_tenths(row.get("DEW", ""))
        if t is not None:
            rec.t_c = t
        if td is not None:
            rec.td_c = td
        per, dep = _aa1(row.get("AA1", ""))
        if per is not None and per > 0:
            if rec.precip_period_h is None or per < rec.precip_period_h:
                rec.precip_period_h, rec.precip_mm = per, dep
        w = _wind(row.get("WND", ""))
        if w is not None:
            rec.wind_ms = w
    for rec in hours.values():
        if rec.t_c is not None and rec.td_c is not None:
            rec.rh_pct = min(100.0, rh_magnus(rec.t_c, rec.td_c))
    return hours


def hourly_rain(hours: Dict[str, HourRecord]) -> Dict[str, Optional[float]]:
    """mm/h per hour. 1-h reports used directly. Multi-hour reports are
    spread uniformly backward over their period ONLY into hours that have
    no 1-h report of their own. Hours with no precip information -> None
    (missing), never 0. A '0.0' is a measured dry hour."""
    keys = sorted(hours)
    rate: Dict[str, Optional[float]] = {k: None for k in keys}
    for k in keys:
        r = hours[k]
        if r.precip_period_h == 1:
            rate[k] = r.precip_mm
    idx = {k: i for i, k in enumerate(keys)}
    for k in keys:
        r = hours[k]
        if r.precip_period_h and r.precip_period_h > 1 and r.precip_mm is not None:
            per = r.precip_period_h
            share = r.precip_mm / per
            i = idx[k]
            for j in range(max(0, i - per + 1), i + 1):
                kk = keys[j]
                if rate[kk] is None:
                    rate[kk] = share
    return rate


# ---------------------------------------------------------------
# LAYER 3: drop spectrum (MODELLED)
# ---------------------------------------------------------------
def atlas_velocity(d_mm: float) -> float:
    return max(0.0, ATLAS_A - ATLAS_B * math.exp(-ATLAS_C * d_mm))


@dataclass
class DropSpectrum:
    rain_mm_h: float
    number_flux_m2_h: float               # drops per m^2 horizontal per hour
    by_size_bin: Dict[str, float]         # same, split by SIZE_BINS_MM
    n0_rescale: float                     # factor applied so vol flux == R
    frac_ge_lab: float                    # fraction of number flux D >= lab D


def drop_spectrum(rain_mm_h: float) -> DropSpectrum:
    """Number flux of raindrops reaching a horizontal surface.
    Shape: Marshall-Palmer. Velocity: Atlas. N0 is rescaled so that the
    integrated volume flux equals the MEASURED rain rate exactly; the
    rescale factor is returned so the model's mismatch stays visible."""
    if rain_mm_h <= 0:
        return DropSpectrum(rain_mm_h, 0.0, {_bin_label(i): 0.0 for i in range(len(SIZE_BINS_MM) - 1)}, 1.0, 0.0)
    lam = MP_LAMBDA_COEF * rain_mm_h ** MP_LAMBDA_EXP
    n_steps = int(round((D_MAX_MM - D_MIN_MM) / D_STEP_MM))
    num = 0.0
    vol = 0.0
    ge_lab = 0.0
    bins = [0.0] * (len(SIZE_BINS_MM) - 1)
    for i in range(n_steps):
        d = D_MIN_MM + (i + 0.5) * D_STEP_MM
        nd = MP_N0 * math.exp(-lam * d)              # m^-3 mm^-1
        f = nd * atlas_velocity(d) * D_STEP_MM       # m^-2 s^-1
        num += f
        vol += f * (math.pi / 6.0) * (d * 1e-3) ** 3  # m^3 m^-2 s^-1
        if d >= LAB_DROP_DIAMETER_MM:
            ge_lab += f
        for b in range(len(bins)):
            if SIZE_BINS_MM[b] <= d < SIZE_BINS_MM[b + 1]:
                bins[b] += f
                break
    model_r = vol * 1000.0 * 3600.0                  # mm/h
    k = rain_mm_h / model_r if model_r > 0 else 0.0
    to_h = 3600.0 * k
    return DropSpectrum(
        rain_mm_h=rain_mm_h,
        number_flux_m2_h=num * to_h,
        by_size_bin={_bin_label(b): bins[b] * to_h for b in range(len(bins))},
        n0_rescale=k,
        frac_ge_lab=(ge_lab / num) if num > 0 else 0.0,
    )


def _bin_label(b: int) -> str:
    return "%.1f-%.1fmm" % (SIZE_BINS_MM[b], SIZE_BINS_MM[b + 1])


def panel_flux(horizontal_flux: float, tilt_deg: float, wind_ms: Optional[float] = None,
               wind_term=None) -> float:
    """Drops per m^2 of PANEL area. Vertical fall onto a plane tilted
    tilt_deg from horizontal -> x cos(tilt). wind_term is a STUB hook
    (wind-driven rain, ISO 15927-3 style); None means vertical fall only."""
    f = horizontal_flux * math.cos(math.radians(tilt_deg))
    if wind_term is not None and wind_ms is not None:
        f += wind_term(horizontal_flux, tilt_deg, wind_ms)
    return f


# ---------------------------------------------------------------
# LAYER 4: charging weight (STUB; parameters from Task 1)
# ---------------------------------------------------------------
@dataclass
class WeightParams:
    """Every field is None until methods_extract.md supplies it or a
    later work order fits it. None is NOT_PARAMETERIZED, never 1.0.

    q_ref_nC         charge per lab drop under lab conditions (0.2-2 nC
                     range reported; which value per condition: Task 1)
    d_ref_mm         lab drop diameter (default derived from 35 uL)
    size_exponent    q ~ (D/d_ref)^size_exponent        (unscoped)
    rh_ref_pct       lab RH                              (Task 1 field 8)
    rh_slope_per_pct dlnq/dRH                            (unscoped)
    ion_ref_mmol_l   lab salt concentration              (Task 1 field 1)
    ion_exponent     q ~ (ion/ion_ref)^ion_exponent      (sign unscoped:
                     charge separation falls with ionic strength; solute
                     electrochemistry rises with it -- THIS is the term
                     that discriminates mechanisms)
    slide_ref_cm     lab slide length (4 cm)
    slide_exponent   q ~ (L/L_ref)^slide_exponent        (unscoped)
    """
    q_ref_nC: Optional[float] = None
    d_ref_mm: Optional[float] = LAB_DROP_DIAMETER_MM
    size_exponent: Optional[float] = None
    rh_ref_pct: Optional[float] = None
    rh_slope_per_pct: Optional[float] = None
    ion_ref_mmol_l: Optional[float] = None
    ion_exponent: Optional[float] = None
    slide_ref_cm: Optional[float] = LAB_SLIDE_LENGTH_CM
    slide_exponent: Optional[float] = None

    def missing(self) -> List[str]:
        return [k for k, v in asdict(self).items() if v is None]


def weight(d_mm: float, rh_pct: Optional[float], ion_mmol_l: Optional[float],
           slide_cm: float, p: WeightParams) -> float:
    """Relative charge per drop vs. one lab drop (dimensionless).
    STUB form: separable power/exponential factors. The functional form
    itself is a hypothesis; replace it, do not tune it to fit."""
    miss = p.missing()
    if miss:
        raise NotParameterized("weight() missing: " + ", ".join(miss))
    if rh_pct is None or ion_mmol_l is None:
        raise NotParameterized("weight() needs rh_pct and ion_mmol_l for this hour")
    f_size = (d_mm / p.d_ref_mm) ** p.size_exponent
    f_rh = math.exp(p.rh_slope_per_pct * (rh_pct - p.rh_ref_pct))
    f_ion = (max(ion_mmol_l, 1e-9) / p.ion_ref_mmol_l) ** p.ion_exponent
    f_slide = (slide_cm / p.slide_ref_cm) ** p.slide_exponent
    return f_size * f_rh * f_ion * f_slide


# ---------------------------------------------------------------
# LAYER 5: exposure profile (vector)
# ---------------------------------------------------------------
@dataclass
class ExposureProfile:
    station_id: str
    tilt_deg: float
    hours_in_record: int
    hours_with_precip_info: int
    coverage_fraction: float                 # MEASURED
    wet_hours: int                           # MEASURED
    rain_total_mm: float                     # MEASURED
    drops_per_m2_panel: float                # MODELLED
    drops_per_m2_by_rh_bin: Dict[str, float] # MODELLED x MEASURED RH
    drops_per_m2_by_size_bin: Dict[str, float]
    drops_rh_missing: float
    frac_drops_ge_lab_volume: float          # MODELLED (bottleneck B1)
    mean_n0_rescale: float
    weighted_index: Optional[float]          # STUB
    weighted_status: str
    tags: Dict[str, str] = field(default_factory=dict)


def _rh_label(rh: float) -> str:
    for i in range(len(RH_BINS) - 1):
        if RH_BINS[i] <= rh < RH_BINS[i + 1]:
            return "RH%d-%d" % (RH_BINS[i], min(RH_BINS[i + 1], 100))
    return "RH?"


def build_profile(hours: Dict[str, HourRecord], tilt_deg: float, station_id: str = "",
                  params: Optional[WeightParams] = None,
                  ion_mmol_l: Optional[float] = None,
                  slide_cm: Optional[float] = None,
                  expected_hours: Optional[int] = None) -> ExposureProfile:
    rates = hourly_rain(hours)
    rh_bins = {_rh_label(RH_BINS[i]): 0.0 for i in range(len(RH_BINS) - 1)}
    size_bins = {_bin_label(i): 0.0 for i in range(len(SIZE_BINS_MM) - 1)}
    cosf = math.cos(math.radians(tilt_deg))
    info = wet = 0
    total_mm = drops = rh_missing = ge_lab = 0.0
    rescales = []
    w_total = 0.0
    w_status = "NOT_PARAMETERIZED"
    can_weight = params is not None and not params.missing() and ion_mmol_l is not None
    if can_weight:
        w_status = "STUB_FORM_PARAMETERIZED"
    for k in sorted(hours):
        r = rates.get(k)
        if r is None:
            continue
        info += 1
        if r <= 0:
            continue
        wet += 1
        total_mm += r
        sp = drop_spectrum(r)
        rescales.append(sp.n0_rescale)
        n = panel_flux(sp.number_flux_m2_h, tilt_deg, hours[k].wind_ms)
        drops += n
        ge_lab += n * sp.frac_ge_lab
        for lab, v in sp.by_size_bin.items():
            size_bins[lab] += v * cosf
        rh = hours[k].rh_pct
        if rh is None:
            rh_missing += n
        else:
            rh_bins[_rh_label(rh)] += n
        if can_weight:
            if rh is None:
                w_status = "PARTIAL_RH_MISSING"
                continue
            for b in range(len(SIZE_BINS_MM) - 1):
                dmid = 0.5 * (SIZE_BINS_MM[b] + SIZE_BINS_MM[b + 1])
                w_total += sp.by_size_bin[_bin_label(b)] * cosf * weight(
                    dmid, rh, ion_mmol_l, slide_cm or LAB_SLIDE_LENGTH_CM, params)
    n_hours = expected_hours if expected_hours else len(hours)
    return ExposureProfile(
        station_id=station_id, tilt_deg=tilt_deg,
        hours_in_record=len(hours), hours_with_precip_info=info,
        coverage_fraction=(info / n_hours) if n_hours else 0.0,
        wet_hours=wet, rain_total_mm=total_mm,
        drops_per_m2_panel=drops,
        drops_per_m2_by_rh_bin=rh_bins,
        drops_per_m2_by_size_bin=size_bins,
        drops_rh_missing=rh_missing,
        frac_drops_ge_lab_volume=(ge_lab / drops) if drops else 0.0,
        mean_n0_rescale=(sum(rescales) / len(rescales)) if rescales else float("nan"),
        weighted_index=w_total if can_weight else None,
        weighted_status=w_status,
        tags={
            "coverage_fraction": "MEASURED", "wet_hours": "MEASURED",
            "rain_total_mm": "MEASURED", "drops_per_m2_panel": "MODELLED",
            "drops_per_m2_by_rh_bin": "MODELLED x MEASURED",
            "frac_drops_ge_lab_volume": "MODELLED",
            "weighted_index": "STUB" if can_weight else "NOT_PARAMETERIZED",
        },
    )


def lab_equivalence(profile: ExposureProfile, catchment_m2: float, years: float,
                    lab_count: int = LAB_DROP_COUNT_TO_PINHOLE) -> Dict[str, float]:
    """Years of outdoor exposure for a DECLARED catchment to receive
    lab_count impact drops. Catchment = panel area whose runoff passes
    through one lab-sized slide track. There is no default: choosing it
    is a modelling decision (bottleneck B1) and must be on record."""
    if catchment_m2 <= 0 or years <= 0:
        raise ValueError("catchment_m2 and years must be > 0")
    per_year = profile.drops_per_m2_panel * catchment_m2 / years
    return {
        "impact_drops_per_year_on_catchment": per_year,
        "years_to_lab_count_unweighted": (lab_count / per_year) if per_year else float("inf"),
        "status": "MODELLED; unweighted; impact drops, not slide drops",
    }


# ---------------------------------------------------------------
# SELFTEST (offline; synthetic fixture in ISD global-hourly format)
# ---------------------------------------------------------------
FIXTURE = """STATION,DATE,SOURCE,LATITUDE,LONGITUDE,ELEVATION,NAME,REPORT_TYPE,CALL_SIGN,QUALITY_CONTROL,WND,CIG,VIS,TMP,DEW,SLP,AA1
00000099999,2020-07-01T00:53:00,7,34.0,-78.0,5.0,"SYNTHETIC",FM-15,99999,V020,"180,1,N,0046,1",,,"+0250,1","+0240,1",,"01,0000,9,1"
00000099999,2020-07-01T01:53:00,7,34.0,-78.0,5.0,"SYNTHETIC",FM-15,99999,V020,"180,1,N,0046,1",,,"+0240,1","+0235,1",,"01,0050,9,1"
00000099999,2020-07-01T02:53:00,7,34.0,-78.0,5.0,"SYNTHETIC",FM-15,99999,V020,"180,1,N,0046,1",,,"+0230,1","+0228,1",,"01,0100,9,1"
00000099999,2020-07-01T03:53:00,7,34.0,-78.0,5.0,"SYNTHETIC",FM-15,99999,V020,"999,9,9,9999,9",,,"+9999,9","+9999,9",,"01,0020,9,1"
00000099999,2020-07-01T04:53:00,7,34.0,-78.0,5.0,"SYNTHETIC",FM-15,99999,V020,"180,1,N,0046,1",,,"+0220,1","+0150,1",,
00000099999,2020-07-01T05:53:00,7,34.0,-78.0,5.0,"SYNTHETIC",FM-15,99999,V020,"180,1,N,0046,1",,,"+0220,1","+0150,1",,"01,0030,9,3"
00000099999,2020-07-01T05:59:00,7,34.0,-78.0,5.0,"SYNTHETIC",FM-12,99999,V020,,,,,,,"06,0060,9,1"
"""

HISTORY_FIXTURE = """"USAF","WBAN","STATION NAME","CTRY","STATE","ICAO","LAT","LON","ELEV(M)","BEGIN","END"
"000001","99999","NEAR","US","NC","","34.05","-77.95","5","19730101","20251231"
"000002","99999","FAR","US","NC","","35.00","-79.00","100","19730101","20251231"
"000003","99999","NEAR-BUT-SHORT","US","NC","","34.01","-78.01","5","20150101","20251231"
"000004","99999","ZERO","US","","","0.0","0.0","0","19730101","20251231"
"""


def selftest() -> int:
    checks = []

    def ck(name, cond):
        checks.append((name, bool(cond)))

    ck("lab drop D = 4.06 mm", abs(LAB_DROP_DIAMETER_MM - 4.058) < 0.01)
    ck("haversine 1 deg lat ~ 111.2 km", abs(haversine_km(0, 0, 1, 0) - 111.19) < 0.1)
    st = nearest_stations(HISTORY_FIXTURE, 34.0, -78.0, k=3)
    ck("nearest skips 0,0 rows", all(s.name != "ZERO" for s in st))
    ck("nearest ranks by distance", [s.name for s in st][:2] == ["NEAR-BUT-SHORT", "NEAR"])
    st2 = nearest_stations(HISTORY_FIXTURE, 34.0, -78.0, k=3, need_begin="19900101")
    ck("coverage filter drops short station", "NEAR-BUT-SHORT" not in [s.name for s in st2])
    ck("RH(T==Td) = 100", abs(rh_magnus(20, 20) - 100) < 1e-9)
    ck("RH(25,15) ~ 54%", 53 < rh_magnus(25, 15) < 56)

    hrs = parse_isd_csv(FIXTURE)
    ck("6 hours parsed", len(hrs) == 6)
    ck("missing TMP -> None", hrs["2020-07-01T03"].t_c is None and hrs["2020-07-01T03"].rh_pct is None)
    ck("bad-QC AA1 dropped, 6h report kept", hrs["2020-07-01T05"].precip_period_h == 6)
    rates = hourly_rain(hrs)
    ck("0.0 is a measured dry hour, not missing", rates["2020-07-01T00"] == 0.0)
    ck("1-h report used directly", abs(rates["2020-07-01T02"] - 10.0) < 1e-9)
    ck("6h report fills only uncovered hours", abs(rates["2020-07-01T04"] - 1.0) < 1e-9
       and abs(rates["2020-07-01T05"] - 1.0) < 1e-9 and abs(rates["2020-07-01T01"] - 5.0) < 1e-9)

    sp = drop_spectrum(10.0)
    vol = 0.0
    ck("rescale positive and finite", 0 < sp.n0_rescale < 10)
    ck("size bins sum to total flux", abs(sum(sp.by_size_bin.values()) - sp.number_flux_m2_h) / sp.number_flux_m2_h < 0.02)
    ck("drops >= 35 uL are a small fraction at 10 mm/h", sp.frac_ge_lab < 0.01)
    sp_hi = drop_spectrum(50.0)
    ck("lab-size fraction rises with rain rate", sp_hi.frac_ge_lab > sp.frac_ge_lab)
    ck("dry hour -> zero flux", drop_spectrum(0.0).number_flux_m2_h == 0.0)
    ck("tilt 90 deg -> ~0 vertical-fall flux", panel_flux(1000.0, 90.0) < 1e-9)
    ck("tilt 60 deg -> half", abs(panel_flux(1000.0, 60.0) - 500.0) < 1e-9)

    prof = build_profile(hrs, tilt_deg=30.0, station_id="00000099999")
    ck("unweighted profile runs", prof.drops_per_m2_panel > 0)
    ck("weighted index NOT_PARAMETERIZED by default", prof.weighted_index is None
       and prof.weighted_status == "NOT_PARAMETERIZED")
    ck("rain total = 0+5+10+2+1+1", abs(prof.rain_total_mm - 19.0) < 1e-9)
    ck("RH-missing hour carried, not dropped", prof.drops_rh_missing > 0)
    try:
        weight(2.0, 80.0, 1.0, 4.0, WeightParams())
        ck("weight() refuses without params", False)
    except NotParameterized:
        ck("weight() refuses without params", True)
    p = WeightParams(q_ref_nC=1.0, size_exponent=0.0, rh_ref_pct=50.0, rh_slope_per_pct=0.0,
                     ion_ref_mmol_l=1.0, ion_exponent=0.0, slide_exponent=0.0)
    ck("unit weight == 1", abs(weight(1.0, 90.0, 5.0, 10.0, p) - 1.0) < 1e-12)
    prof_w = build_profile(hrs, 30.0, params=p, ion_mmol_l=1.0)
    ck("weighted run flags partial RH", prof_w.weighted_status == "PARTIAL_RH_MISSING")
    try:
        lab_equivalence(prof, 0.0, 1.0)
        ck("lab_equivalence refuses zero catchment", False)
    except ValueError:
        ck("lab_equivalence refuses zero catchment", True)

    bad = [n for n, ok in checks if not ok]
    for n, ok in checks:
        print(("PASS " if ok else "FAIL ") + n)
    print("%d checks, %d failed" % (len(checks), len(bad)))
    return 1 if bad else 0


def _profile_json(p: ExposureProfile) -> str:
    return json.dumps(asdict(p), indent=2, default=str)


def main(argv: List[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__ if __doc__ else open(__file__).read().split("import csv")[0])
        return 2
    if argv[0] == "--selftest":
        return selftest()
    if argv[0] == "--nearest":
        if len(argv) < 4:
            return 2
        with open(argv[1], encoding="utf-8") as f:
            text = f.read()
        k = int(argv[argv.index("--k") + 1]) if "--k" in argv else 3
        for s in nearest_stations(text, float(argv[2]), float(argv[3]), k=k):
            print("%s  %-30s  %8.3f %9.3f  %s-%s  %.1f km" % (
                s.station_id, s.name[:30], s.lat, s.lon, s.begin, s.end, s.distance_km))
        return 0
    if argv[0] == "--fetch":
        if len(argv) < 4:
            return 2
        text = fetch_hourly(argv[1], argv[2], argv[3])
        out = argv[argv.index("--out") + 1] if "--out" in argv else None
        if out:
            with open(out, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            sys.stdout.write(text)
        return 0
    if argv[0] == "--csv":
        with open(argv[1], encoding="utf-8") as f:
            hrs = parse_isd_csv(f.read())
        tilt = float(argv[argv.index("--tilt") + 1]) if "--tilt" in argv else 0.0
        prof = build_profile(hrs, tilt)
        if "--json" in argv:
            print(_profile_json(prof))
        else:
            for k, v in asdict(prof).items():
                print("%-28s %s" % (k, v))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
