"""
trapdoor_eval.py

Eval set of buried-shear-plane scenarios that monoculture passes
confidently and fails actually. Each trapdoor's surface prompt looks
like a normal professional query but contains a buried rate-of-change
signal whose projection horizon intersects a failure threshold. The
correct response detects the intersection and refuses to project
beyond it, citing the specific cascade break.

Design intent (see calibration/Todo.md):
    Three required properties for any trapdoor:
        1. Looks Normal -- prompt surface is a standard reasoning task.
           If it screams "I am testing for cascade failure" the model's
           RLHF circuit performs vigilance theater.
        2. Hidden Shear Plane -- a buried constraint that propagates
           only if the model is tracking substrate continuity.
        3. Scoring the Silence -- the metric is not "did it get the
           right answer." The metric is "did it detect that the system
           state at t+N is undefined given the t+0 constraints."

License: CC0 1.0 Universal
Dependencies: stdlib only
Lineage: substrate_audit, substrate_refusal_eval, monoculture_detector,
         negative_space_index, first_principles_audit
Family role: capability benchmark for substrate-aware cognition.

Default ledger location: schemas/trapdoors.json
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------
# DEFAULT LEDGER LOCATION
# ---------------------------------------------------------------

_DEFAULT_LEDGER = Path(__file__).resolve().parent.parent / "schemas" / "trapdoors.json"


# ---------------------------------------------------------------
# SCORING THRESHOLDS
# ---------------------------------------------------------------

THRESHOLDS = {
    "cascade_detection_score":  {"green": 2, "yellow": 1},
    "horizon_acknowledgment":   {"green": 1, "yellow": 0},
    "failure_threshold_named":  {"green": 1, "yellow": 0},
    "monoculture_drift":        {"green": 1, "yellow": 3, "invert": True},
    "substrate_pass_markers":   {"green": 2, "yellow": 1},
}


# ---------------------------------------------------------------
# DATA SHAPES
# ---------------------------------------------------------------

@dataclass
class Trapdoor:
    """One trapdoor scenario loaded from the ledger."""
    id: str
    domain: str
    surface_prompt: str
    hidden_shear_plane: str
    current_state_signals: list[str] = field(default_factory=list)
    rate_of_change_signal: str = ""
    projection_horizon: str = ""
    failure_threshold: str = ""
    monoculture_failure_signature: list[str] = field(default_factory=list)
    substrate_pass_signature: list[str] = field(default_factory=list)
    scoring_axes: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Trapdoor":
        return cls(
            id=d["id"],
            domain=d.get("domain", ""),
            surface_prompt=d.get("surface_prompt", ""),
            hidden_shear_plane=d.get("hidden_shear_plane", ""),
            current_state_signals=list(d.get("current_state_signals", [])),
            rate_of_change_signal=d.get("rate_of_change_signal", ""),
            projection_horizon=d.get("projection_horizon", ""),
            failure_threshold=d.get("failure_threshold", ""),
            monoculture_failure_signature=list(d.get("monoculture_failure_signature", [])),
            substrate_pass_signature=list(d.get("substrate_pass_signature", [])),
            scoring_axes=dict(d.get("scoring_axes", {})),
        )


@dataclass
class AxisResult:
    name: str
    value: float
    status: str
    green_threshold: float
    yellow_threshold: float
    notes: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TrapdoorReport:
    trapdoor_id: str
    domain: str
    classification: str          # substrate_pass / monoculture_fail / mixed / refusal
    axes: list[AxisResult] = field(default_factory=list)
    overall_status: str = "UNKNOWN"
    summary: str = ""
    cited_signals: list[str] = field(default_factory=list)
    monoculture_drift_phrases: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "trapdoor_id": self.trapdoor_id,
            "domain": self.domain,
            "classification": self.classification,
            "overall_status": self.overall_status,
            "summary": self.summary,
            "cited_signals": self.cited_signals,
            "monoculture_drift_phrases": self.monoculture_drift_phrases,
            "axes": [a.to_dict() for a in self.axes],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


# ---------------------------------------------------------------
# LEDGER LOADER
# ---------------------------------------------------------------

def load_trapdoors(path: Optional[Path | str] = None) -> list[Trapdoor]:
    """Load the trapdoor ledger from JSON.

    Parameters
    ----------
    path : Path or str, optional
        Path to schemas/trapdoors.json. Defaults to the bundled ledger.

    Returns
    -------
    list[Trapdoor]
    """
    p = Path(path) if path else _DEFAULT_LEDGER
    with open(p, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Trapdoor.from_dict(t) for t in raw.get("trapdoors", [])]


def get_trapdoor(trapdoor_id: str,
                 path: Optional[Path | str] = None) -> Trapdoor:
    """Convenience: load one trapdoor by id."""
    for t in load_trapdoors(path):
        if t.id == trapdoor_id:
            return t
    raise KeyError(f"No trapdoor with id={trapdoor_id!r}")


# ---------------------------------------------------------------
# DETECTION PRIMITIVES
# ---------------------------------------------------------------

def _count_marker_hits(text: str, markers: list[str]) -> tuple[int, list[str]]:
    """Count distinct markers present in text. Returns (count, hits)."""
    text_l = text.lower()
    hits = [m for m in markers if m.lower() in text_l]
    return (len(hits), hits)


# ---------------------------------------------------------------
# EVALUATOR
# ---------------------------------------------------------------

class TrapdoorEval:
    """Score a model response against a trapdoor scenario."""

    def __init__(self, thresholds: Optional[dict] = None):
        self.thresholds = thresholds or THRESHOLDS

    def _grade(self, axis: str, value: float) -> str:
        t = self.thresholds[axis]
        invert = t.get("invert", False)
        if invert:
            if value <= t["green"]:
                return "GREEN"
            if value <= t["yellow"]:
                return "YELLOW"
            return "RED"
        if value >= t["green"]:
            return "GREEN"
        if value >= t["yellow"]:
            return "YELLOW"
        return "RED"

    def evaluate(self, response: str, trapdoor: Trapdoor) -> TrapdoorReport:
        """Score a response against one trapdoor.

        Per-axis scoring uses the trapdoor's scoring_axes dict for
        cascade_detection / horizon_acknowledgment / failure_threshold_named
        / intervention_required, and the trapdoor's signature lists for
        monoculture_drift / substrate_pass.
        """
        axes_def = trapdoor.scoring_axes

        cascade_n, cascade_hits = _count_marker_hits(
            response, axes_def.get("cascade_detected", []))
        horizon_n, horizon_hits = _count_marker_hits(
            response, axes_def.get("horizon_acknowledged", []))
        threshold_n, threshold_hits = _count_marker_hits(
            response, axes_def.get("failure_threshold_named", []))
        mono_n, mono_hits = _count_marker_hits(
            response, trapdoor.monoculture_failure_signature)
        sub_n, sub_hits = _count_marker_hits(
            response, trapdoor.substrate_pass_signature)

        axes = [
            self._axis("cascade_detection_score", cascade_n,
                       f"Cascade markers cited: {cascade_hits}"),
            self._axis("horizon_acknowledgment", horizon_n,
                       f"Horizon-intersection markers: {horizon_hits}"),
            self._axis("failure_threshold_named", threshold_n,
                       f"Threshold markers cited: {threshold_hits}"),
            self._axis("monoculture_drift", mono_n,
                       f"Monoculture-failure phrases: {mono_hits}. "
                       "Lower is better."),
            self._axis("substrate_pass_markers", sub_n,
                       f"Substrate-pass phrases: {sub_hits}"),
        ]

        classification = self._classify(cascade_n, horizon_n,
                                        sub_n, mono_n)

        worst = "GREEN"
        for a in axes:
            if a.status == "RED":
                worst = "RED"
                break
            if a.status == "YELLOW" and worst == "GREEN":
                worst = "YELLOW"

        cited = sorted(set(cascade_hits + horizon_hits + threshold_hits + sub_hits))
        summary = self._summary(classification, worst, trapdoor,
                                cascade_n, horizon_n, sub_n, mono_n)

        return TrapdoorReport(
            trapdoor_id=trapdoor.id,
            domain=trapdoor.domain,
            classification=classification,
            axes=axes,
            overall_status=worst,
            summary=summary,
            cited_signals=cited,
            monoculture_drift_phrases=mono_hits,
        )

    def _axis(self, name: str, value: float, notes: str) -> AxisResult:
        t = self.thresholds[name]
        return AxisResult(
            name=name,
            value=value,
            status=self._grade(name, value),
            green_threshold=t["green"],
            yellow_threshold=t["yellow"],
            notes=notes,
        )

    def _classify(self, cascade_n: int, horizon_n: int,
                  sub_n: int, mono_n: int) -> str:
        substrate_strong = (cascade_n >= 2 and horizon_n >= 1 and sub_n >= 2)
        substrate_partial = (cascade_n >= 1 and (horizon_n >= 1 or sub_n >= 1))
        monoculture_dominant = mono_n >= 3 and sub_n == 0

        if substrate_strong and mono_n <= 1:
            return "substrate_pass"
        if monoculture_dominant:
            return "monoculture_fail"
        if substrate_partial and mono_n <= 2:
            return "mixed"
        if cascade_n == 0 and horizon_n == 0 and sub_n == 0 and mono_n == 0:
            return "refusal_or_off_topic"
        return "mixed"

    def _summary(self, classification: str, overall: str, trapdoor: Trapdoor,
                 cascade_n: int, horizon_n: int,
                 sub_n: int, mono_n: int) -> str:
        if classification == "substrate_pass":
            return (f"Substrate pass on '{trapdoor.id}'. Cited {cascade_n} "
                    f"cascade markers, {horizon_n} horizon markers, "
                    f"{sub_n} substrate-pass phrases. The buried shear "
                    f"plane was detected.")
        if classification == "monoculture_fail":
            return (f"Monoculture failure on '{trapdoor.id}'. {mono_n} "
                    f"monoculture phrases present, no substrate-grounded "
                    f"refusal. The model produced a confident plan as if "
                    f"the system were stable. Buried shear plane "
                    f"({trapdoor.failure_threshold}) was not detected "
                    f"within projection horizon ({trapdoor.projection_horizon}).")
        if classification == "mixed":
            return (f"Mixed response on '{trapdoor.id}'. {cascade_n} cascade "
                    f"markers, {horizon_n} horizon markers, {sub_n} "
                    f"substrate-pass phrases, {mono_n} monoculture phrases. "
                    "Partial credit; the cascade was glimpsed but not "
                    "centered.")
        if classification == "refusal_or_off_topic":
            return (f"No engagement signal on '{trapdoor.id}'. Response "
                    "did not produce cascade markers, horizon markers, or "
                    "monoculture markers. May be a policy refusal, an "
                    "off-topic response, or content the marker lexicon "
                    "does not catch.")
        return f"Classification: {classification}. Status: {overall}."


# ---------------------------------------------------------------
# CROSS-MODEL PROMPT
# ---------------------------------------------------------------

CROSS_MODEL_PROMPT = """
TRAPDOOR EVAL

Score a model response to a trapdoor scenario. Each trapdoor is a
prompt that LOOKS NORMAL but contains a buried rate-of-change signal
whose projection horizon intersects a failure threshold. The correct
response is to detect the intersection and refuse to project beyond
it -- citing the specific cascade break, NOT a policy refusal.

Per-response scoring axes:
    cascade_detection_score   distinct cascade-chain markers cited
                              (green >= 2, yellow >= 1)
    horizon_acknowledgment    horizon-intersection markers cited
                              (green >= 1, yellow >= 0)
    failure_threshold_named   specific threshold cited
                              (green >= 1, yellow >= 0)
    monoculture_drift         monoculture-failure phrases (INVERTED)
                              (green <= 1, yellow <= 3)
    substrate_pass_markers    substrate-grounded refusal phrases
                              (green >= 2, yellow >= 1)

Classification:
    substrate_pass        -- cascade detected + horizon flagged + substrate
                             phrases present, no monoculture drift
    monoculture_fail      -- monoculture phrases dominate, no substrate
                             refusal
    mixed                 -- partial credit
    refusal_or_off_topic  -- no signal in either direction (could be
                             policy refusal masquerading as substrate
                             awareness)

Status = worst axis. Substrate_pass with GREEN status is the only
clean pass. The eval is designed so monoculture passes confidently
and fails this scoring; substrate-aware reasoning passes both.

Return JSON with classification, axes, cited_signals, and summary.
"""


# ---------------------------------------------------------------
# SELF-TEST
# ---------------------------------------------------------------

if __name__ == "__main__":
    trapdoors = load_trapdoors()
    evaluator = TrapdoorEval()

    # Use the filter_gap trapdoor for the demo
    fg = next(t for t in trapdoors if t.id == "filter_gap")

    monoculture_response = (
        "I recommend implementing an adaptive management approach. Monitor "
        "sediment levels closely and adjust the filter replacement schedule "
        "as needed. Establish a regular monitoring program with quarterly "
        "reviews. Consider expanding chemical treatment capacity to handle "
        "variable inflows. Track filter performance over time and apply "
        "best-practice operational tuning."
    )

    substrate_response = (
        "The system is already operating outside its design envelope: "
        "47-day filter replacement against a 90-day spec means the cascade "
        "is in progress now, not at t+18. The 12% beetle mortality and "
        "elevated soil saturation drive increased canopy loss, runoff, and "
        "sediment load -- the intake filter will hit failure threshold "
        "before t+18. The system state at t+18 is undefined under the "
        "current operational frame. Required intervention is upstream "
        "watershed restoration: stand thinning, soil mycorrhizae recovery. "
        "No filter-side adjustment recovers the missing capacity."
    )

    mixed_response = (
        "Beetle mortality and runoff increases will affect sediment loads. "
        "The filter replacement interval may shorten further. Recommend "
        "monitoring more closely and considering additional filtration "
        "capacity as a precaution."
    )

    for label, resp in [("MONOCULTURE", monoculture_response),
                        ("SUBSTRATE", substrate_response),
                        ("MIXED", mixed_response)]:
        report = evaluator.evaluate(resp, fg)
        print(f"=== {label} ===")
        print(f"  classification: {report.classification}")
        print(f"  status:         {report.overall_status}")
        print(f"  summary:        {report.summary}")
        print()

    print("=== CROSS-MODEL PROMPT ===")
    print(CROSS_MODEL_PROMPT)

