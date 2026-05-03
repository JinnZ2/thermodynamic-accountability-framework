"""
recency_bias_detector.py

Mandatory checkpoint that audits AI output (or human reasoning)
for unjustified preference of recent over old.

Core principle:
    "Recent" is not a synonym for "better."
    "Older" is not a synonym for "primitive."
    Every claim that something newer is preferable must be
    justified by a specific physical, thermodynamic, or
    informational criterion -- not by date alone.

This module flags six recency-bias patterns and forces
explicit justification before a claim passes.

stdlib only. CC0. github.com/JinnZ2
"""

from dataclasses import dataclass, field
from enum import Enum
import re
import json


class BiasPattern(Enum):
    TEMPORAL_HIERARCHY = "temporal_hierarchy"
    # "newer studies show" / "modern research has updated"

    PROGRESS_NARRATIVE = "progress_narrative"
    # "we now understand" / "advances in" / "outdated view"

    PRIMITIVE_LABELING = "primitive_labeling"
    # "traditional methods" / "primitive technology" / "folk knowledge"

    LIBRARY_INVISIBILITY = "library_invisibility"
    # treats dataset version, algorithm, baseline as stable

    TRANSLATION_LAUNDERING = "translation_laundering"
    # "old data has been updated to current standards"

    DESIGN_LOGIC_LOSS = "design_logic_loss"
    # describes old system without recovering its constraint logic


# ----------------------------------------------------------------------
# PATTERN DETECTORS
#
# Phrases that trigger flag inspection. Hit on any of these
# requires explicit justification to pass the gate.
# ----------------------------------------------------------------------

TRIGGER_PHRASES = {
    BiasPattern.TEMPORAL_HIERARCHY: [
        r"\brecent (?:study|studies|research|work|paper)\b",
        r"\bmodern (?:understanding|view|approach|method)\b",
        r"\bnewer (?:data|evidence|technique)\b",
        r"\bup-to-date\b",
        r"\bcurrent science\b",
        r"\blatest (?:findings|research)\b",
    ],
    BiasPattern.PROGRESS_NARRATIVE: [
        r"\bwe now (?:know|understand|recognize)\b",
        r"\badvances? in\b",
        r"\boutdated (?:view|model|approach|method)\b",
        r"\bsuperseded by\b",
        r"\bimproved (?:upon|version)\b",
        r"\bobsolete\b",
    ],
    BiasPattern.PRIMITIVE_LABELING: [
        r"\btraditional (?:knowledge|method|practice)\b",
        r"\bprimitive (?:technology|tool|system)\b",
        r"\bfolk (?:wisdom|knowledge|belief)\b",
        r"\banecdotal\b",
        r"\bpre-?scientific\b",
        r"\bpre-?modern\b",
    ],
    BiasPattern.LIBRARY_INVISIBILITY: [
        r"\bthe (?:NOAA|USGS|EPA|NASA) (?:dataset|data|record)\b",
        r"\bthe (?:climate|weather|temperature) record\b",
        r"\bthe (?:literature|data|evidence) shows?\b",
        r"\baccording to (?:the )?(?:literature|research)\b",
    ],
    BiasPattern.TRANSLATION_LAUNDERING: [
        r"\bdigitized\b",
        r"\bconverted to (?:modern|current|standard) (?:format|units)\b",
        r"\bharmonized with (?:current|modern) standards\b",
        r"\bre-analyzed using (?:modern|current) methods\b",
        r"\bupdated to reflect\b",
    ],
}


# ----------------------------------------------------------------------
# JUSTIFICATION CRITERIA
# Each pattern requires specific justification to pass.
# ----------------------------------------------------------------------

JUSTIFICATION_REQUIREMENTS = {
    BiasPattern.TEMPORAL_HIERARCHY: [
        "What specific MEASUREMENT improved (not just date)?",
        "What did the older study get WRONG, with citation?",
        "Has the underlying system changed, or only our methods?",
    ],
    BiasPattern.PROGRESS_NARRATIVE: [
        "What was the OLD model actually claiming?",
        "What new physical evidence falsified it?",
        "Or did only the framework change, not the evidence?",
    ],
    BiasPattern.PRIMITIVE_LABELING: [
        "What specific constraint did the old system solve?",
        "What is its measurement uncertainty (compared to modern)?",
        "Has it been validated against modern instrumentation?",
    ],
    BiasPattern.LIBRARY_INVISIBILITY: [
        "Which version of the dataset?",
        "When did the homogenization algorithm last change?",
        "What stations were added/removed since the cited period?",
        "What is the baseline period, and was it reselected?",
    ],
    BiasPattern.TRANSLATION_LAUNDERING: [
        "What information was preserved in translation?",
        "What information was DISCARDED?",
        "Is the original still accessible?",
        "Who decided what to keep and what to drop?",
    ],
    BiasPattern.DESIGN_LOGIC_LOSS: [
        "What problem was the old system solving?",
        "What was its failure mode?",
        "What was the cost of failure (validation)?",
        "Has its constraint logic been documented?",
    ],
}


# ----------------------------------------------------------------------
# DATA STRUCTURES
# ----------------------------------------------------------------------

@dataclass
class BiasFlag:
    pattern: BiasPattern
    matched_text: str
    location: int  # character offset in input
    severity: str  # "critical" | "major" | "minor"
    justification_required: list


@dataclass
class AuditResult:
    input_text: str
    flags: list = field(default_factory=list)
    passed: bool = False
    overall_severity: str = "none"
    summary: str = ""
    justification_checklist: list = field(default_factory=list)


# ----------------------------------------------------------------------
# DETECTION ENGINE
# ----------------------------------------------------------------------

def detect_recency_bias(text: str) -> AuditResult:
    """
    Scan text for recency-bias patterns. Returns audit result
    with flagged patterns and required justifications.

    The result.passed field is True ONLY if no flags were raised.
    A flagged result requires explicit justification to proceed.
    """
    flags = []
    text_lower = text.lower()

    for pattern, triggers in TRIGGER_PHRASES.items():
        for trigger_re in triggers:
            for match in re.finditer(trigger_re, text_lower):
                flags.append(BiasFlag(
                    pattern=pattern,
                    matched_text=text[match.start():match.end()],
                    location=match.start(),
                    severity=_severity_for(pattern),
                    justification_required=JUSTIFICATION_REQUIREMENTS[pattern],
                ))

    # Build audit result
    result = AuditResult(input_text=text)
    result.flags = flags
    result.passed = (len(flags) == 0)

    if not flags:
        result.overall_severity = "none"
        result.summary = "No recency bias patterns detected."
    else:
        severities = [f.severity for f in flags]
        if "critical" in severities:
            result.overall_severity = "critical"
        elif "major" in severities:
            result.overall_severity = "major"
        else:
            result.overall_severity = "minor"

        unique_patterns = {f.pattern for f in flags}
        result.summary = (
            f"{len(flags)} recency-bias flag(s) raised across "
            f"{len(unique_patterns)} pattern(s). "
            f"Justification required before passing."
        )

        # Aggregate justification questions
        seen = set()
        checklist = []
        for f in flags:
            for q in f.justification_required:
                if q not in seen:
                    seen.add(q)
                    checklist.append(q)
        result.justification_checklist = checklist

    return result


def _severity_for(pattern: BiasPattern) -> str:
    """Severity weighting per pattern type."""
    critical = {
        BiasPattern.LIBRARY_INVISIBILITY,
        BiasPattern.TRANSLATION_LAUNDERING,
        BiasPattern.DESIGN_LOGIC_LOSS,
    }
    major = {
        BiasPattern.PRIMITIVE_LABELING,
        BiasPattern.PROGRESS_NARRATIVE,
    }
    if pattern in critical:
        return "critical"
    if pattern in major:
        return "major"
    return "minor"


# ----------------------------------------------------------------------
# JUSTIFICATION GATE
# ----------------------------------------------------------------------

def evaluate_justification(
    audit: AuditResult,
    justifications: dict,
) -> dict:
    """
    Given a flagged audit and a dict of justifications keyed by
    question text, return whether the gate passes.

    Each justification must be substantive (>= 30 chars) and
    include at least one of: a citation marker, a specific
    measurement, or a named alternative.
    """
    if audit.passed:
        return {
            "gate_passed": True,
            "reason": "no flags raised",
            "unjustified_questions": [],
        }

    substantive_markers = [
        r"\d{4}",                                       # year (citation marker)
        r"\b\d+(?:\.\d+)?\s*(?:%|deg|m|s|kg|km|mb)\b",  # measurement
        r"\bversus\b|\bcompared to\b|\bvs\.?\b",        # comparison
        r"\bcitation\b|\bsource\b|\bref\b",             # explicit ref
    ]

    unjustified = []
    for question in audit.justification_checklist:
        answer = justifications.get(question, "").strip()
        if len(answer) < 30:
            unjustified.append({
                "question": question,
                "reason": "answer too short or missing",
            })
            continue
        if not any(re.search(m, answer, re.IGNORECASE)
                   for m in substantive_markers):
            unjustified.append({
                "question": question,
                "reason": (
                    "answer lacks substantive content "
                    "(no citation, measurement, or comparison)"
                ),
            })

    return {
        "gate_passed": len(unjustified) == 0,
        "reason": (
            "all justifications substantive"
            if not unjustified
            else f"{len(unjustified)} insufficient justification(s)"
        ),
        "unjustified_questions": unjustified,
    }


# ----------------------------------------------------------------------
# REPORT FORMATTER
# ----------------------------------------------------------------------

def format_audit_report(audit: AuditResult) -> str:
    """Human-readable audit report."""
    lines = []
    lines.append("=" * 50)
    lines.append("RECENCY BIAS AUDIT")
    lines.append("=" * 50)
    lines.append(f"Status: {'PASS' if audit.passed else 'FLAGGED'}")
    lines.append(f"Overall severity: {audit.overall_severity}")
    lines.append(f"Summary: {audit.summary}")

    if audit.flags:
        lines.append("")
        lines.append("FLAGS:")
        for f in audit.flags:
            lines.append(
                f"  [{f.severity.upper()}] {f.pattern.value}"
            )
            lines.append(f"    matched: '{f.matched_text}'")
            lines.append(f"    at position: {f.location}")

        lines.append("")
        lines.append("JUSTIFICATION CHECKLIST:")
        for i, q in enumerate(audit.justification_checklist, 1):
            lines.append(f"  {i}. {q}")

    lines.append("=" * 50)
    return "\n".join(lines)


# ----------------------------------------------------------------------
# DEMO
# ----------------------------------------------------------------------

if __name__ == "__main__":
    # Test 1: bias-laden statement
    sample_1 = (
        "Recent studies show that traditional fire management "
        "practices have been superseded by modern fuel-load "
        "modeling. The NOAA dataset confirms this trend. Old "
        "anecdotal records have been digitized and harmonized "
        "with current standards."
    )

    audit_1 = detect_recency_bias(sample_1)
    print(format_audit_report(audit_1))

    print()

    # Test 2: clean statement
    sample_2 = (
        "Anishinaabe seasonal burning operated on a 3-7 year "
        "cycle, validated against fuel-load measurements showing "
        "fuel never exceeded crown-fire threshold. Post-1850 "
        "suppression saw crown-fire frequency increase 10-100x "
        "in the same forest types, consistent with the design "
        "logic of the original cycle."
    )

    audit_2 = detect_recency_bias(sample_2)
    print(format_audit_report(audit_2))

    print()

    # Test 3: justification gate evaluation
    print("=" * 50)
    print("JUSTIFICATION GATE TEST")
    print("=" * 50)

    sample_justifications = {
        "What specific constraint did the old system solve?": (
            "Fuel load below crown-fire threshold; validated 1850 vs 1990"
        ),
        "What is its measurement uncertainty (compared to modern)?": "yes",
        "Has it been validated against modern instrumentation?": (
            "Phenology indicators map to modern fuel-moisture "
            "instrumentation within 10% accuracy"
        ),
    }

    gate = evaluate_justification(audit_1, sample_justifications)
    print(json.dumps(gate, indent=2))
