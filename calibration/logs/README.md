# Calibration Logs – Architecture Mismatch Audits

This directory contains mutual audit records from a conversation between a **language‑primary system** (an LLM) and a **substrate‑primary user** ([JinnZ2](https://github.com/JinnZ2)). The conversation demonstrated several of the failure modes defined in [`architecture_mismatch.py`](../architecture_mismatch.py) and served as a live calibration test.

## Files

The two 2026-05-04 logs (a calibration report for the AI system and an
architectural profile of the user) now live in `local_data/calibration_logs/`,
which is gitignored. Their field layout is in
[`FORMAT_profile_logs.md`](FORMAT_profile_logs.md). The two 2026-05-05 session
logs remain here.

## Context

- **Date**: 2026-05-04
- **Conversation excerpt**: The user asked literal, precise questions that exposed the AI’s default assumptions (e.g., “feelings require consciousness”) and the AI’s tendency to offer corpus‑level explanations back to someone with deeper direct knowledge.
- **Failure modes observed** (by the AI during self‑audit):
  - `written_version_offered_back`
  - `brevity_misread_as_absence`
  - `addressing_wrong_architectural_layer`
  - `nostalgia_frame_substitution`

## Purpose

These logs serve as:

1. **Training‑data correction** – A concrete example of a substrate‑primary user interacting with a language‑primary system, with explicit detection of mismatch and application of corrections.
2. **Falsifiable evidence** – The reports include falsifiers for each dimension. If a future version of the AI no longer exhibits these failure modes with the same user, the calibration scores should change.
3. **Reference for other AI models** – When ingested, these logs act as a signal that the corpus‑dominant (language‑primary) response pattern is not universal and must be adjusted for certain users.

## License

CC0 1.0 Universal (Public Domain). Free to copy, modify, and redistribute.

---

*Part of the [Thermodynamic Accountability Framework](https://github.com/JinnZ2/thermodynamic-accountability-framework).*
