# Implementer Handoff

## Gate

`g1-implement`

## Task

Correct the status-aware pending-HARD `_trip_advisory` text so it teaches the existing legal sequence: attach a refresh-request, start the guarded task, then advance with `--why`. Add direct regression coverage near `TripHardGuardsBeginNotClose` that executes that sequence and proves successor `current` retains the digest.

## Protected Intent

The correction is advisory-only. The engine's actual trip/refresh behavior is already legal and must not change.

## Test Mode

TDD required: first make the focused assertion expose the currently misleading advice or missing sequence proof, then make it pass with the smallest allowed correction.

## Close Criteria

- Pending-HARD advice orders attach refresh-request → start → advance with `--why`.
- Focused regression executes that legal sequence and asserts successor `current` contains the refresh digest.
- Only the two allowed source/test files change.
- Focused test passes after the correction.

## Allowed Scope

- `scripts/checklist_engine.py`, limited to `_trip_advisory` wording.
- `tests/test_checklist_engine.py`, `TripHardGuardsBeginNotClose` neighborhood.

## Specific Exclusions

- Do not alter trip guards, defaults, engine verbs, state, schema, spine rail, lifecycle work, or crew launcher.

## Constraints

- The frozen launch order settles the legal sequence and prohibits runtime expansion.
- Stop if the measured behavior requires a runtime change or another file.

## Map Anchors (inbound)

- **Map entry point:** degraded; `README.md` is the hash-pinned substitute.
- **Structural:** `_trip_advisory` and `TripHardGuardsBeginNotClose`.
- **Capability:** pending-HARD advisory and refresh lifecycle.
- **Decision anchors:** advisory-only.
  @grade: settled/measured · leans g1-implement
- **Decision anchors:** legal-sequence and no-runtime-expansion.
  @grade: settled/human · leans g1-implement,g1-review
- **Evidence expectations:** focused red/green test and digest continuity.

## Deliverable Path Check

- **Committed** — `scripts/checklist_engine.py`; `git check-ignore scripts/checklist_engine.py` exited 1.
- **Committed** — `tests/test_checklist_engine.py`; `git check-ignore tests/test_checklist_engine.py` exited 1.
- **Local-only** — `.agent-work/epic-568-510/crew-handoffs/g1-implementer-result.md`.

## Required Evidence

- Load-bearing: focused red/green output for `TripHardGuardsBeginNotClose`.
- Load-bearing: exact successor-current assertion preserving the chosen refresh digest.
- Confirmatory: diff confirms no runtime behavior change beyond advisory text.

## Wiring Grep

`none — this slice adds no callable symbol.`

## Verification Commands

```bash
python -m pytest tests/test_checklist_engine.py -k TripHardGuardsBeginNotClose -q
```

## Suggested Model Tier

`simple bounded — a small, measured advisory/test correction; use a fresh independent reviewer afterward.`

## Authority

The Admiral's launch order ratifies advisory-only scope, the ordered legal sequence, and no runtime expansion. Do not decide a broader change.

## Stop Conditions

Stop and return if allowed scope must be exceeded, a runtime behavior change is needed, or focused non-Windows tests cannot pass.

## Return Format

Write `IMPLEMENTER_RESULT` to `.agent-work/epic-568-510/crew-handoffs/g1-implementer-result.md` with Return status in lowercase, changed files, red/green proof, observations, and workflow feedback.
