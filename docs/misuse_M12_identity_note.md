# M12 -- self-declared identities: design note

Provenance: co-authored (JinnZ2 + Claude), 2026-11-05. Status: PROPOSED,
thin. Design note only; no code change in this round.

## The surface

```text
string a record carries          who checks it today
human:<role> / ai:<node>         nobody (prefix only)
roles.Role.id, household_id      nobody (declared in roles.json)
recorder (judgment_registry)     nobody (role code)
scorer id (signal_calibration)   nobody
SIGCAL_MODEL_ID                  nobody (env var set by the runner's operator)
```

Anyone who can append a record can write any of these strings. Consent,
corroboration, two-person approval, coder agreement and "model tested" all
rest on them.

## Why it cannot be fully closed here

Binding a string to a person or a model needs identity infrastructure:
keys held per person, an issuer, revocation, and devices that keep the keys
safe. None of that is stdlib-only, phone-runnable or free of a central
party, and a key registry is itself a list of people (M1). So this repo
does not claim to close M12.

## Partial mitigations in place

```text
mechanism                       where                          what it raises the cost of
contact_paths independence      defenses.claim_status          N fake ids on ONE contact path count as one
  (default since E10/T2)                                       source; the forger needs N paths
steward attestation             holders.py contact_via         holder contact goes through a steward ROLE,
                                                               so a fake holder needs a steward to vouch
two-person rule (D7)            two_person.authorize           one forged role is not enough; needs a second
  incl. quarantine (D-M11)                                     role in another household and dependency
                                                               network, with current rotation
hash chain + head (D-M10)       headrec.py, all four ledgers   a forged record cannot be inserted earlier or
                                                               swapped later without breaking chain or head
header line (D-M6)              judgment_registry cli          "Registered = documented, not correct."
```

None of these verifies who wrote a record. Each one makes a single forged
string insufficient for the action it gates.

## Residual (logged)

- A person who controls two roles in two households (or two contact paths)
  defeats D7 and contact_paths alike.
- recorder, scorer and SIGCAL_MODEL_ID are unchecked labels; outputs should
  say so (not yet done).
- Out-of-band confirmation (in person, by a known voice on radio) for any
  record that gates an action is policy, not code.

## What would move it

- E: a tabletop where one participant holds two roles; does the community
  notice before the two-person rule passes? (NOT RUN, not registered.)
- A design that marks every identity string as "declared, unverified" in
  CLI output, the way D-M6 marks the registry.
