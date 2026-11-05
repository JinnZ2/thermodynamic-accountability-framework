# Profile and audit logs: format only

The two architecture-mismatch logs from 2026-05-04 (a user profile and the
matching AI-side audit) were moved out of the repository to
`local_data/calibration_logs/`, which is gitignored. This file records the
format only. It holds no content from them.

```text
user profile log (one JSON object)
  profile_type, user_id, timestamp, substrate_primary_confidence, band,
  signals_detected, inferred_encoding_profile, recommendation_for_AI_systems

AI-side audit log (one JSON object; architecture_mismatch report)
  module, system_id, timestamp, dimensions, aggregate_score, aggregate_band,
  verdict, failing_dimensions, falsifiable_claims, metadata
```

Earlier versions remain in git history; moving them forward does not
remove them from it.
