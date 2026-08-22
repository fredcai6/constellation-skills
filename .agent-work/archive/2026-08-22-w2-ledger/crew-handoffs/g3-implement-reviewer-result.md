# Review Result

## Assigned Gate
g3-implement (work-id: w2-ledger) — attempt 2 (PART E rework)

## Result
`APPROVE`

## Handoff compliance
All five parts verified against the diff:

- **PART A** — `override_summary(cl)` in `scripts/checklist_engine.py` exists, pure (reads
  only `_override_entries(cl)`, confirmed both by reading the body and by the diff's own
  call-graph test `test_does_not_read_the_ledger_keys_directly`, which patches
  `_override_entries` and asserts the output is driven entirely by its return value).
  Returns exactly `{"trip", "force-claim", "force-release", "waive",
  "waive_authority_mismatch", "ids"}`.
- **PART B** — `"overrides"` is in `MECHANICAL_ALL_FIELDS`, not
  `MECHANICAL_SCALAR_FIELDS`; `_validate_create` rejects a non-dict value.
- **Load-bearing round-trip test** — `test_overrides_field_survives_the_create_op_validation_path`
  (`tests/test_episode_fields.py`) drives a *real* `mechanical_fields()` output (captured via
  the engine's own snapshot seam, not hand-assembled) through
  `apply_episode_delta.validate_delta` directly. This is the actual validator, not a mock —
  read the test body and confirmed it.
- A fixture with an empty/absent `override_ledger` produces no `"overrides"` key
  (`test_absent_when_the_ledger_is_empty`); `REQUIRED_MECHANICAL_FIELDS` is unchanged.
- **PART C** — `mechanical_fields()` sets `fields["overrides"]` gated on
  `overrides["ids"]` being non-empty — absence-is-meaningful, matching `refusals`.
- **PART D** — `finish_work`'s `overrides` is computed once via `override_summary(spine)`
  at step 1 and carried onto all four return points. Verified with a schema fixture whose
  entries carry no `outcome` field (`_override_ledger_fixture()`), and four dedicated tests
  each drive a distinct path: `test_verify_refusal_carries_overrides`,
  `test_advance_release_refusal_carries_overrides`, `test_archive_refusal_carries_overrides`,
  `test_success_carries_overrides` — read each; each asserts the matching `stage` value
  before asserting `overrides`, confirming it actually exercises the named return path.
- **PART E** — `Episode.overrides: dict = field(default_factory=dict)` added;
  `render_episode` emits one compact-JSON line only when non-empty; `parse_episode` recovers
  it; `_apply_create` wires `mech.get("overrides") or {}` through.
  `test_create_op_with_overrides_persists_rendered_line` reads the actual `.md` file from
  disk via `read_exact(episode_path(...))`, not an in-memory `Episode` — confirmed. Both
  `EpisodeOverridesRoundTripTests` cases assert the file's exact documented invariant
  `render_episode(parse_episode(text)) == text` for the present and absent cases.

## Scope drift
None. Hunk-level inspection of `scripts/apply_episode_delta.py` confirms zero diff outside
`MECHANICAL_ALL_FIELDS`, `Episode`, `render_episode`, `parse_episode`, `_validate_create`,
`_apply_create` — amend-assertion, retirement, and consolidation logic show only unmodified
context lines. `scripts/checklist_engine.py` diff is `override_summary` only.
`scripts/episode_capture.py` diff is confined to `mechanical_fields()`. `scripts/spine_lifecycle.py`
diff is confined to `finish_work`'s docstring and body. `map/INDEX.md` changes are
entity-count deltas only (build artifact). No item from Specific Exclusions was touched.

## Evidence verdict
Ran the full suite myself: `py -m pytest -q` → **3660 passed, 6 skipped, 1274 subtests
passed** in 153.82s, exit code 0 — matches the claimed baseline-plus-additions exactly,
not trusted from the pasted count. `py -m pytest tests/test_code_map.py -q` → 148 passed,
63 subtests passed — no stale-entity failures, `map/INDEX.md` is fresh. Independently
reproduced the render/parse round-trip invariant via a standalone script constructing an
`Episode` with non-empty and empty `overrides`, confirming `render_episode(parse_episode(text))
== text` both ways, matching the test suite's claims rather than only trusting test names.

## Code/doc quality
Minimal, well-scoped, tested. Docstrings on `override_summary` and the `finish_work`
comment block explain non-obvious invariants (purity discipline; why one computation of
`overrides` is safe to reuse across all four return points) rather than restating code.
See Fowler pass below for the full smell-by-smell verdict (r6-fowler, `FOWLER_PASS.json`):
10 smells absent, 2 overridden with logged reason (`primitive-obsession` — a plain dict
matches this file's own dict-shaped-mechanical-field convention; `shotgun-surgery` — the
4-file spread is the shape decision:closeout-render-target-is-both requires), none flagged.

## Map impact verdict
- **Evidence supports claimed change:** yes — every Map Anchor structural target
  (`mechanical_fields`, `_validate_create`, `Episode`, `render_episode`, `parse_episode`,
  `_apply_create`, `finish_work`) shows the exact change the handoff describes.
- **Constraints not violated:** yes — `constraint:no-unwired-checker`,
  `constraint:mechanical-fields-and-episode-delta-allowlist-travel-together`, and
  `constraint:render-parse-round-trip-invariant` all hold, independently verified.
- **Notes match the diff:** yes — no missing or overstated impact.
- **Decision candidates surfaced:** n/a — `decision:closeout-render-target-is-both` was
  already `@grade: settled/human`; this gate satisfies it fully, raises no new decision.
- **Durable context routed:** yes — the one open item (missing "## Return status" line)
  is a template-compliance nit already flagged by the Commander, not new durable context.

## Reconciliation check
None. `decision:closeout-render-target-is-both` is now fully satisfied by both render
targets; no divergence from recorded architecture.

## Blockers
- none

## Out-of-scope observations
- The dataclass field-ordering deviation from the handoff's literal suggested position
  (`overrides` after `artifact_refs`, before `agent_supplied`) is confirmed a genuine
  Python constraint, not a corner cut: constructing the dataclass in that literal order
  raises `TypeError: non-default argument 'agent_supplied' follows default argument`.
  Attempt 2's actual placement (after `agent_supplied`) is the only legal spot among the
  optional/defaulted fields. No action needed; recorded here per the handoff's own request
  to confirm this before approving.
- Both IMPLEMENTER_RESULT attempts omit the required "## Return status" line — a
  template-compliance gap, not a content gap. Agree with the Commander's "complete" reading:
  every close criterion is independently verifiable as met, no blockers or stop conditions
  are stated, and the content is unambiguous.

## Workflow Feedback
- **Handoff gaps:** none — the review handoff's Close Criteria and Constraints sections
  were precise enough to drive every check without needing to re-derive intent.
- **Context rediscovered:** the review handoff's `SPINE_FILE`/`SPINE_SESSION` env pointed at
  the parent Commander's own `execute` spine, not a spine bound for this reviewer crew
  (`crew-runs.json` confirms `"spine": null"`, `"door_bound": true`, `"parent":
  "constellation/w2-ledger/commander/commander"`). `spine_status` did not refuse (it
  returned the Commander's `execute` gate content directly); the confirming signal was
  `spine_bind`'s refusal ("this door still holds an active lease on
  '.../spine.json' ... Release it first"). Authored my own survey at the handoff's named
  Survey State Location and drove it via `scripts/checklist_engine.py`'s CLI
  (`claim`/`start`/`record`/`consolidate`), never touching the parent's `execute` gate or
  releasing its lease. This matches a pattern already seen on other gates in this same
  project; the durable fix (branching the reviewer skill's engine-drive step on whether
  `SPINE_FILE` is genuinely bound to this crew) is still outstanding.
- **Instructions improvised around:** the skill's default assumption ("a spine is bound
  for you; call `spine_status` first") does not hold for a `run_crew.py` `cli`-backend
  crew whose own `crew-runs.json` entry records `spine: null` — I built and drove my own
  survey file instead, per the same recovery path documented in this project's own prior
  runs.
- **What would have made this easier:** the review handoff's "Survey State Location" field
  already pointed at the right path — no change needed there. The skill itself could name
  the `spine: null` / `door_bound: true` shape explicitly as the trigger to author-and-CLI
  rather than assume-and-drive.

## Return status
`complete`
