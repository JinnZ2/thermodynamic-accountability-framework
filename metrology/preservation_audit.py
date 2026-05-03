"""
preservation_audit.py

Format-translation information loss audit.

Position in the metrology chain::

    raw phenomenon
        |
        v
    encoding layer (instruments / observers / oral tradition)
        |
        v
    [TRANSLATION LAYER]   <-- this module audits here
        |
        v
    library / dataset layer  (metrological_audit_framework.py)
        |
        v
    interpretation layer (observer_bias.py, domain_convergence_matrix.py,
                          calibration/recency_bias_detector.py)
        |
        v
    ground truth estimate

Core claim
----------
Format upgrades are not lossless. When a recording, observation, or
traditional system is translated to a "better" format, classes of
information are routinely discarded. Often the discarded classes were
never inventoried, and the decision to discard was not reversible.

Downstream consequences:
    - AI systems trained on the post-translation corpus never see the
      lost information classes.
    - The next generation treats the post-translation form as the
      reference, deepening the loss.
    - Library version audits (metrological_audit_framework) cannot
      recover this; the source material is gone before it enters the
      library.

Coupling
--------
- Upstream of: metrology/metrological_audit_framework.py
- Companion to: calibration/recency_bias_detector.py
  (recency bias is the *attitude* that justifies discard; this module
  audits the *event* of discard.)
- Couples to: metrology/constraint_recovery_framework.py
  (recovers what the discarded form encoded, when partial recovery
  is possible.)

License: CC0
Stdlib only.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


# ----------------------------------------------------------------------
# Enums
# ----------------------------------------------------------------------

class Recoverability(Enum):
    """Can the discarded information be reconstructed from the new form?"""

    NONE = "none"          # gone; new form does not contain it
    PARTIAL = "partial"    # some can be inferred but with loss
    FULL = "full"          # mathematically lossless transformation


class TranslationVerdict(Enum):
    """Outcome class for a translation event."""

    LOSSLESS = "lossless"                 # FULL recoverability, documented
    DOCUMENTED_LOSS = "documented_loss"   # PARTIAL/NONE, but loss documented
    SILENT_LOSS = "silent_loss"           # PARTIAL/NONE, loss undocumented
    DISCARDED_RECOVERABLE = "discarded_recoverable"
    # ^ source material destroyed/discarded; no recovery possible


# ----------------------------------------------------------------------
# Dataclasses
# ----------------------------------------------------------------------

@dataclass
class InformationClass:
    """One named class of information that may be lost in translation.

    Examples::

        InformationClass(
            name="harmonic_structure_above_22khz",
            description="Overtone content above CD sampling Nyquist",
            measurable_in_source=True,
            measurable_in_target=False,
        )
    """

    name: str
    description: str
    measurable_in_source: bool
    measurable_in_target: bool

    @property
    def is_lost(self) -> bool:
        return self.measurable_in_source and not self.measurable_in_target


@dataclass
class TranslationEvent:
    """One historical translation from source format to target format.

    Fields:
        source_format: identifier of the pre-translation form
        target_format: identifier of the post-translation form
        year: approximate year the translation became dominant practice
        institutional_actor: who drove the translation (industry, agency,
            standards body, individual practitioner)
        stated_rationale: the public justification at the time
        information_classes: list of InformationClass entries describing
            what was preserved vs lost
        recoverability: can the lost classes be reconstructed?
        source_material_disposition: what happened to the original
            artifacts (kept / archived / discarded / destroyed)
        decision_reversible: could the field still go back if it wanted to?
        documentation_quality: 0.0 (no record of what was lost) to 1.0
            (every loss class enumerated and published at the time)
        notes: free text
    """

    source_format: str
    target_format: str
    year: int
    institutional_actor: str
    stated_rationale: str
    information_classes: list[InformationClass]
    recoverability: Recoverability
    source_material_disposition: str
    decision_reversible: bool
    documentation_quality: float
    notes: str = ""

    def __post_init__(self) -> None:
        if not 0.0 <= self.documentation_quality <= 1.0:
            raise ValueError("documentation_quality must be in [0, 1]")

    @property
    def lost_classes(self) -> list[InformationClass]:
        return [c for c in self.information_classes if c.is_lost]

    @property
    def loss_severity(self) -> float:
        """0.0 (no loss) to 1.0 (total loss, undocumented, irreversible).

        Combines four factors:
            - fraction of information classes lost
            - inverse documentation_quality
            - recoverability penalty
            - irreversibility + source destruction penalty
        """
        if not self.information_classes:
            return 0.0

        n = len(self.information_classes)
        lost_fraction = len(self.lost_classes) / n
        doc_penalty = 1.0 - self.documentation_quality

        recov_penalty = {
            Recoverability.FULL: 0.0,
            Recoverability.PARTIAL: 0.5,
            Recoverability.NONE: 1.0,
        }[self.recoverability]

        disposition = self.source_material_disposition.lower()
        destroyed = any(
            tok in disposition
            for tok in ("discard", "destroy", "scrap", "lost", "thrown")
        )
        archived = any(
            tok in disposition for tok in ("archive", "preserved", "kept")
        )
        if destroyed and not self.decision_reversible:
            irrev_penalty = 1.0
        elif destroyed:
            irrev_penalty = 0.7
        elif not self.decision_reversible:
            irrev_penalty = 0.4
        elif archived:
            irrev_penalty = 0.0
        else:
            irrev_penalty = 0.2

        # Geometric mean over the four factors keeps any single low
        # value from washing out the others.
        factors = [
            max(lost_fraction, 1e-3),
            max(doc_penalty, 1e-3),
            max(recov_penalty, 1e-3),
            max(irrev_penalty, 1e-3),
        ]
        product = 1.0
        for f in factors:
            product *= f
        return product ** (1.0 / len(factors))

    def verdict(self) -> TranslationVerdict:
        if self.recoverability is Recoverability.FULL and not self.lost_classes:
            return TranslationVerdict.LOSSLESS

        disposition = self.source_material_disposition.lower()
        destroyed = any(
            tok in disposition
            for tok in ("discard", "destroy", "scrap", "lost", "thrown")
        )
        if destroyed and self.recoverability is not Recoverability.FULL:
            return TranslationVerdict.DISCARDED_RECOVERABLE

        if self.documentation_quality >= 0.5:
            return TranslationVerdict.DOCUMENTED_LOSS
        return TranslationVerdict.SILENT_LOSS


@dataclass
class PreservationAudit:
    """Audit result for a domain or set of translation events."""

    domain: str
    events: list[TranslationEvent]
    severity_score: float
    worst_verdict: TranslationVerdict
    discarded_recoverable_count: int
    silent_loss_count: int
    flagged_classes: list[str] = field(default_factory=list)
    notes: str = ""

    def summary(self) -> str:
        lines = [
            f"PreservationAudit[{self.domain}]",
            f"  events:                  {len(self.events)}",
            f"  severity_score:          {self.severity_score:.3f}",
            f"  worst_verdict:           {self.worst_verdict.value}",
            f"  discarded_recoverable:   {self.discarded_recoverable_count}",
            f"  silent_loss:             {self.silent_loss_count}",
        ]
        if self.flagged_classes:
            lines.append("  flagged information classes:")
            for c in self.flagged_classes:
                lines.append(f"    - {c}")
        if self.notes:
            lines.append(f"  notes: {self.notes}")
        return "\n".join(lines)


# ----------------------------------------------------------------------
# Audit pipeline
# ----------------------------------------------------------------------

_VERDICT_RANK = {
    TranslationVerdict.LOSSLESS: 0,
    TranslationVerdict.DOCUMENTED_LOSS: 1,
    TranslationVerdict.SILENT_LOSS: 2,
    TranslationVerdict.DISCARDED_RECOVERABLE: 3,
}


def audit_domain(
    domain: str,
    events: Iterable[TranslationEvent],
    notes: str = "",
) -> PreservationAudit:
    """Aggregate one or more TranslationEvents into a PreservationAudit."""

    events = list(events)
    if not events:
        return PreservationAudit(
            domain=domain,
            events=[],
            severity_score=0.0,
            worst_verdict=TranslationVerdict.LOSSLESS,
            discarded_recoverable_count=0,
            silent_loss_count=0,
            notes=notes or "no translation events recorded",
        )

    # Severity score: take the worst event, weighted up by count of bad
    # events. Worst-case dominates; bad-event count adds a saturating
    # penalty so a domain with many silent losses scores higher than a
    # domain with one.
    severities = [e.loss_severity for e in events]
    max_sev = max(severities)
    bad_count = sum(
        1
        for e in events
        if e.verdict()
        in (
            TranslationVerdict.SILENT_LOSS,
            TranslationVerdict.DISCARDED_RECOVERABLE,
        )
    )
    # saturating bump: 1 bad event -> +0.05, 5 -> +0.20, asymptote ~0.30
    bump = 0.30 * (1.0 - 1.0 / (1.0 + 0.4 * bad_count))
    severity_score = min(1.0, max_sev + bump)

    worst = max(events, key=lambda e: _VERDICT_RANK[e.verdict()]).verdict()

    discarded_recov = sum(
        1
        for e in events
        if e.verdict() is TranslationVerdict.DISCARDED_RECOVERABLE
    )
    silent = sum(
        1 for e in events if e.verdict() is TranslationVerdict.SILENT_LOSS
    )

    flagged: list[str] = []
    seen: set[str] = set()
    for e in events:
        for c in e.lost_classes:
            if c.name not in seen:
                seen.add(c.name)
                flagged.append(c.name)

    return PreservationAudit(
        domain=domain,
        events=events,
        severity_score=severity_score,
        worst_verdict=worst,
        discarded_recoverable_count=discarded_recov,
        silent_loss_count=silent,
        flagged_classes=flagged,
        notes=notes,
    )


# ----------------------------------------------------------------------
# Coupling to upstream metrology chain
# ----------------------------------------------------------------------

def corruption_contribution(audit: PreservationAudit) -> float:
    """Return a [0, 1] corruption probability for use upstream of
    metrological_audit_framework / trend_corruption_calculator.

    Convention matches the existing
        corruption(trend) = corruption(measurement) * corruption(framework)
    pattern. This function returns a *pre-measurement* corruption term::

        corruption(measurement) =
            1 - (1 - corruption_preservation) *
                (1 - corruption_library) *
                (1 - corruption_instrument)

    so a downstream caller multiplies survival probabilities (1 - c)
    rather than corruption probabilities directly.
    """
    return audit.severity_score


# ----------------------------------------------------------------------
# Seeded domain catalog
# ----------------------------------------------------------------------

def _audio_analog_to_digital() -> TranslationEvent:
    return TranslationEvent(
        source_format="analog_master_tape_and_vinyl",
        target_format="cd_44_1khz_16bit",
        year=1982,
        institutional_actor="recording industry / Sony-Philips",
        stated_rationale=(
            "digital is cleaner, no surface noise, perfect reproduction"
        ),
        information_classes=[
            InformationClass(
                name="harmonic_content_above_22khz",
                description=(
                    "Overtones above CD Nyquist; affects perceived "
                    "instrument timbre"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="tape_saturation_curve",
                description=(
                    "Soft-knee compression and harmonic generation "
                    "from magnetic tape; part of recorded sound"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="mechanical_resonance_signature",
                description=(
                    "Cutting-lathe and pressing-plant resonances "
                    "encoded into vinyl groove; identifies pressing"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="surface_noise_floor_structure",
                description=(
                    "Treated as defect; actually contains "
                    "stylus-groove interaction information"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="dynamic_range_envelope",
                description="Pre-loudness-war dynamics",
                measurable_in_source=True,
                measurable_in_target=True,  # preserved at this stage
            ),
        ],
        recoverability=Recoverability.NONE,
        source_material_disposition=(
            "many master tapes discarded after CD transfer; "
            "Universal 2008 fire destroyed est. 175,000 masters"
        ),
        decision_reversible=False,
        documentation_quality=0.2,
        notes=(
            "Compounded by mp3 (1995+) and streaming-loudness (2010+) "
            "translations; each round dropped further classes. See also "
            "the 'loudness war' as a separate translation event."
        ),
    )


def _audio_cd_to_mp3() -> TranslationEvent:
    return TranslationEvent(
        source_format="cd_44_1khz_16bit",
        target_format="mp3_128_to_320_kbps",
        year=1998,
        institutional_actor=(
            "consumer software industry / Fraunhofer / file-sharing era"
        ),
        stated_rationale="storage and bandwidth efficiency",
        information_classes=[
            InformationClass(
                name="psychoacoustic_masked_frequencies",
                description=(
                    "Frequencies discarded as 'inaudible' under "
                    "masking model; assumption fails for trained "
                    "listeners and on different playback systems"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="stereo_phase_coherence",
                description=(
                    "Joint-stereo modes collapse low-bit phase info"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="transient_attack_envelope",
                description=(
                    "Pre-echo artifacts on percussive attacks"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
        ],
        recoverability=Recoverability.NONE,
        source_material_disposition=(
            "CDs largely retained at consumer level but ripped-and-deleted "
            "common; commercial CD pressings declining"
        ),
        decision_reversible=True,  # CDs still exist; lossless rips possible
        documentation_quality=0.6,
        notes="Documentation quality higher because the codec is open.",
    )


def _weather_manual_to_automated() -> TranslationEvent:
    return TranslationEvent(
        source_format="manual_cooperative_observer_network",
        target_format="automated_surface_observing_system_asos",
        year=1995,
        institutional_actor="NOAA / NWS / FAA",
        stated_rationale=(
            "consistency, hourly cadence, reduced labor cost, "
            "removal of observer subjectivity"
        ),
        information_classes=[
            InformationClass(
                name="qualitative_sky_observation",
                description=(
                    "Cloud type, character, layering, evolution; "
                    "observer-judgment fields"
                ),
                measurable_in_source=True,
                measurable_in_target=False,  # ASOS reports cloud cover only
            ),
            InformationClass(
                name="phenomenon_context",
                description=(
                    "Notes on unusual events, frost timing, "
                    "first-flowering, animal behavior co-observed"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="local_microclimate_calibration",
                description=(
                    "Decades of one-observer-one-site continuity; "
                    "implicit calibration to site-specific drift"
                ),
                measurable_in_source=True,
                measurable_in_target=False,  # site moves and instrument swaps
            ),
            InformationClass(
                name="precipitation_type_discrimination",
                description=(
                    "Human can distinguish snow / sleet / freezing "
                    "rain / graupel; ASOS heated tipping bucket "
                    "cannot reliably"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="hourly_temperature_extrema",
                description="Min/max preserved at higher cadence",
                measurable_in_source=True,
                measurable_in_target=True,
            ),
        ],
        recoverability=Recoverability.PARTIAL,
        source_material_disposition=(
            "paper records partially archived (NCEI), partially lost; "
            "many co-op stations decommissioned"
        ),
        decision_reversible=False,  # observers retired, not replaceable
        documentation_quality=0.4,
        notes=(
            "Couples directly to metrology/observer_bias.py: the manual "
            "network was the calibration anchor for the pre-instrument "
            "record and is no longer running."
        ),
    )


def _oral_to_ethnography() -> TranslationEvent:
    return TranslationEvent(
        source_format="oral_landscape_encoded_knowledge_transmission",
        target_format="written_ethnographic_record",
        year=1900,  # representative; ranges 1850-1970
        institutional_actor=(
            "academic ethnography / Bureau of American Ethnology / "
            "missionary linguists"
        ),
        stated_rationale=(
            "preservation of dying knowledge before speakers passed"
        ),
        information_classes=[
            InformationClass(
                name="landscape_indexed_storage",
                description=(
                    "Knowledge keyed to physical landmarks; "
                    "retrieval requires being at the site"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="seasonal_phenological_triggers",
                description=(
                    "Knowledge releasable only at specific "
                    "ecological events (first flower, ice-out)"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="generational_hypothesis_testing",
                description=(
                    "Stories as multi-generation experiments; "
                    "transcript captures the result, not the test"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="kinship_constrained_release",
                description=(
                    "Some knowledge transmitted only along "
                    "specific kinship channels at specific ages"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="lexical_content",
                description="Word lists, named entities, discrete facts",
                measurable_in_source=True,
                measurable_in_target=True,
            ),
        ],
        recoverability=Recoverability.PARTIAL,
        source_material_disposition=(
            "many speakers passed before secondary recording; "
            "landscape continuity disrupted by displacement"
        ),
        decision_reversible=False,
        documentation_quality=0.3,
        notes=(
            "Ethnography captured the noun layer and missed the verb "
            "layer (energy_english repo). Transcript is not the system; "
            "it is one cross-section of the system."
        ),
    )


def _trad_engineering_to_blueprint() -> TranslationEvent:
    return TranslationEvent(
        source_format="apprenticeship_embodied_engineering_practice",
        target_format="formal_blueprint_and_engineering_code",
        year=1920,
        institutional_actor=(
            "professional engineering societies / building code authorities"
        ),
        stated_rationale=(
            "standardization, liability assignment, scalability"
        ),
        information_classes=[
            InformationClass(
                name="material_judgment",
                description=(
                    "Selecting timber, stone, soil by feel/sound; "
                    "rejecting flawed pieces by tap test"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="site_specific_adaptation",
                description=(
                    "Adjusting standard plan to local hydrology, "
                    "wind, solar, soil; encoded in journeyman habit"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="failure_mode_intuition",
                description=(
                    "What this kind of structure does when it fails; "
                    "guides tolerances and repair strategy"
                ),
                measurable_in_source=True,
                measurable_in_target=False,
            ),
            InformationClass(
                name="dimensional_specification",
                description="Sizes, materials, geometry",
                measurable_in_source=True,
                measurable_in_target=True,
            ),
            InformationClass(
                name="load_calculation",
                description="Quantitative structural analysis",
                measurable_in_source=False,  # implicit in source
                measurable_in_target=True,   # explicit in target
            ),
        ],
        recoverability=Recoverability.PARTIAL,
        source_material_disposition=(
            "tradespeople retired; apprenticeship chains broken in many "
            "trades; some preserved in heritage trades"
        ),
        decision_reversible=False,
        documentation_quality=0.5,
        notes=(
            "Couples to metrology/constraint_recovery_framework.py and "
            "metrology/pre1900_engineering_registry.py; together those "
            "modules reconstruct the discarded design logic."
        ),
    )


def seed_catalog() -> dict[str, list[TranslationEvent]]:
    """Return the seeded translation-event catalog, grouped by domain."""
    return {
        "audio": [_audio_analog_to_digital(), _audio_cd_to_mp3()],
        "weather_observation": [_weather_manual_to_automated()],
        "indigenous_knowledge": [_oral_to_ethnography()],
        "engineering": [_trad_engineering_to_blueprint()],
    }


# ----------------------------------------------------------------------
# CLI demo / smoke test
# ----------------------------------------------------------------------

def _demo() -> None:
    catalog = seed_catalog()
    for domain, events in catalog.items():
        audit = audit_domain(domain, events)
        print(audit.summary())
        print(
            f"  corruption_contribution: "
            f"{corruption_contribution(audit):.3f}"
        )
        print()


if __name__ == "__main__":
    _demo()
