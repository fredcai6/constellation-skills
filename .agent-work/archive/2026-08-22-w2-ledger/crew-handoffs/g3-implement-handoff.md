# Implementer Handoff

## Gate
g3-implement (work-id: w2-ledger)

## Task
Make closeout visibly render the override ledger (issue #504) — currently nothing outside the
engine's own internal trip-advisory logic reads `override_ledger`/`trip_ledger`, so a completed run
that used overrides is indistinguishable from a clean one at closeout. Four parts, **all required
together** — they travel together or the feature silently defeats itself (a design-review finding
from plan time: PLAN_CRITIC.md Finding 1 traced a real failure if PART C ships without PART B).

**PART A** — add a small pure `override_summary(cl: dict) -> dict` to `scripts/checklist_engine.py`
(near `_override_entries`, landed in g1), returning counts by kind:
`{"trip": N, "force-claim": N, "force-release": N, "waive": N, "waive_authority_mismatch": N}` (the
last counts entries where `kind == "waive"` and `authority_mismatch` is true) plus the full ordered
list of entry ids. Read only `_override_entries(cl)` — same purity discipline as
`begin_over_line_records` (no subprocess/gauge/clock).

**PART B** — `scripts/apply_episode_delta.py`: add `"overrides"` to `MECHANICAL_ALL_FIELDS` (it is
dict-shaped like `artifact-ref`, NOT a scalar, so it does not belong in
`MECHANICAL_SCALAR_FIELDS`), and add a corresponding shape check inside `_validate_create` so a
malformed `overrides` value is refused the same way other structured mechanical fields are.
**Without this, PART C's write is either silently dropped by any caller that whitelists to the old
field set, or hard-refuses episode creation the first time any workflow copies
`mechanical_fields()`'s full output into a `create` op for a run that used any override** — exactly
the runs this feature exists to surface, and the failure would ship untested if PART B and PART C
are not both done and both tested together.

**PART C** — `scripts/episode_capture.py`: extend `mechanical_fields()` with the same idiom already
used for `refusals`: `fields["overrides"] = override_summary(checklist)` gated on the summary being
non-empty — a run with zero override entries reports nothing here, matching the `refusals`
absence-is-meaningful convention. Do NOT add `"overrides"` to `REQUIRED_MECHANICAL_FIELDS` — same
reasoning already applied to `artifact-ref` there: its absence is definitionally valid, not a gap.

**PART D** — `scripts/spine_lifecycle.py` `finish_work`: attach `overrides` (computed via
`override_summary(spine)`, reading through `_override_entries` — **NEVER** via a raw
`spine.get("trip_ledger")` + `e.get("outcome")` read; under the schema g1/g2 landed, non-trip kinds
carry no `outcome` field at all, so a raw-key shortcut here would silently report zero forever or
raise a `TypeError` on a mixed set) to **EVERY** dict `finish_work` returns: the verify refusal
(`stage: "verify"`), the advance-release refusal (`stage: "advance-release:<substage>"`), the
archive refusal (`stage: "archive"`), AND the final success dict — **all four return points**, not
just one or two. A test per return point is required (see Close Criteria) — this is the single
most common way this gate ships incomplete: covering only the success path and one refusal path,
missing the other two.

## REWORK NOTE (attempt 2 — reads this section first)

Attempt 1 correctly landed PARTS A-D and correctly flagged, as an out-of-scope observation, that
`scripts/apply_episode_delta.py`'s `Episode` dataclass / `render_episode` / `parse_episode` /
`_apply_create` never actually persist the `mechanical["overrides"]` value into the rendered
episode `.md` text — it passes `_validate_create`'s shape check (PART B) and is then silently
dropped before `_apply_create` builds the `Episode` object. This means the DURABLE half of this
gate's Protected Intent ("visibly distinguish... via the persisted episode record") is unmet: an
episode file on disk shows no trace of override activity even when `mechanical["overrides"]` was
supplied.

**Resolution (Commander decision, in-latitude "implementation shape"):** the launch order's own
pre-ruling states closeout rendering "is part of the deliverable, not a follow-up" — so this gap is
closed now, in this gate, not deferred. **PART E** (new, additive to A-D, all of which stay as
attempt 1 landed them — do not re-touch A-D except where E requires a mechanical wiring):

1. `scripts/apply_episode_delta.py`: add `overrides: dict = field(default_factory=dict)` to the
   `Episode` dataclass (after `artifact_refs`, before `agent_supplied` — dict-shaped, defaulted,
   matching the optional/absence-is-meaningful convention the rest of this file already uses for
   `retired_reason`/etc., NOT a required positional field).
2. `render_episode`: when `ep.overrides` is non-empty, render ONE line in the "## Mechanical"
   section (after the `failed-commands`/`artifact-ref` lines): `- overrides: <compact JSON via
   json.dumps(ep.overrides, sort_keys=True)>`. When empty/absent, render nothing — matching
   `artifact-ref`'s repeatable-line idiom and this file's own absence-is-meaningful convention.
   This file's own comment states `render(parse(text)) == text` is an exact-pair invariant — your
   change must preserve that round-trip for both the overrides-present and overrides-absent cases.
3. `parse_episode`: extract the `overrides` line from the mechanical block (parse the JSON back into
   a dict) alongside the existing `artifact-ref` extraction; default to `{}` when the line is absent.
4. `_apply_create`: pass `overrides=mech.get("overrides") or {}` into the constructed `Episode`.

Add a round-trip test: build an `Episode` with a non-empty `overrides` dict, `render_episode` it,
`parse_episode` the result, and assert equality (both the parsed `Episode.overrides` value and that
`render_episode(parse_episode(rendered_text)) == rendered_text`, the file's own documented
invariant). Also test the empty/absent case renders no `overrides` line at all and round-trips
cleanly. Extend `_apply_create`'s own existing test coverage (wherever it lives — likely alongside
`OverridesMechanicalFieldTests` in `tests/test_episode_store.py`, or a new sibling test) to confirm
a `create` op carrying `mechanical.overrides` actually produces a persisted `.md` file containing
the rendered line — this is the fix for exactly the gap attempt 1's Out-of-scope observation named.

Do not touch anything outside `Episode`/`render_episode`/`parse_episode`/`_apply_create` in this
file for PART E — the rest of `apply_episode_delta.py`'s machinery (amend-assertion, retirement,
consolidation, etc.) is unrelated and off-limits.

## Protected Intent
A run that carried override activity must be visibly distinguishable — via the persisted episode
record AND via the immediate return of `finish_work` — from a run that carried none. Neither render
target may be added at the cost of breaking existing episode-creation or closeout call sites.

## Test Mode
Test-after (well-specified, four small additions with an existing test-file home for each: the
engine test file for `override_summary`, `tests/test_episode_fields.py` for `mechanical_fields`,
`tests/test_spine_lifecycle.py` for `finish_work`, plus whichever file covers
`apply_episode_delta.py`'s validator — search for `MECHANICAL_ALL_FIELDS`/`_validate_create` to find
it).

## Close Criteria
- `override_summary(cl)` exists, pure, reads only `_override_entries(cl)`, returns the exact shape
  named in PART A.
- `"overrides"` is in `MECHANICAL_ALL_FIELDS` (not `MECHANICAL_SCALAR_FIELDS`); `_validate_create`
  has a shape check for it (e.g. must be a dict if present) mirroring how `artifact-ref` is handled
  there.
- **Round-trip test (load-bearing — this is PLAN_CRITIC.md Finding 1's exact untested gap from the
  original design):** a fixture whose `mechanical_fields()` output (including a non-empty
  `"overrides"`) is passed through `apply_episode_delta.py`'s actual `create`-op validation path
  (not just `mechanical_fields()` alone) does NOT raise `EpisodeDeltaError`.
- A fixture with an empty/absent `override_ledger` produces `mechanical_fields()` output with NO
  `"overrides"` key at all (absence-is-meaningful, matching `refusals`).
- `REQUIRED_MECHANICAL_FIELDS` is unchanged (no `"overrides"` added there).
- `finish_work`'s `overrides` field is computed via `override_summary`/`_override_entries` — a test
  using the NEW schema (an `override_ledger` fixture with non-trip kinds, which carry no `outcome`
  field) confirms it does NOT read raw `trip_ledger`/`outcome` and does NOT raise or silently
  zero-out.
- All FOUR `finish_work` return points (verify refusal, advance-release refusal, archive refusal,
  success) carry `"overrides"` — one dedicated test per return point, not a single test that happens
  to hit only one path.
- PART E (attempt 2): `Episode.overrides` field exists (dict, defaulted); `render_episode` emits
  one compact-JSON line when non-empty, nothing when empty; `parse_episode` recovers it;
  `_apply_create` wires `mech.get("overrides")` through. The round-trip invariant
  (`render_episode(parse_episode(text)) == text`) holds for both the overrides-present and
  overrides-absent cases — test both explicitly. A `create` op carrying `mechanical.overrides`
  produces an actual persisted `.md` file whose text contains the rendered line (not just a
  validated-then-discarded value).

## Allowed Scope
`scripts/checklist_engine.py` (new `override_summary` only — do not touch `_override_entries`,
`_append_override_entry`, `waive()`, or `dispatch()`, all landed/reviewed in g1/g2);
`scripts/apply_episode_delta.py` (`MECHANICAL_ALL_FIELDS`, `_validate_create` only);
`scripts/episode_capture.py` (`mechanical_fields()` only); `scripts/spine_lifecycle.py`
(`finish_work` only); test files for all four (pre-authorized for new coverage).

## Specific Exclusions
- Do NOT add `"overrides"` to `REQUIRED_MECHANICAL_FIELDS`.
- Do NOT change `close_work`/`open_pr`'s bodies beyond `finish_work`'s own return dict.
- Do NOT touch anything landed in g1/g2 (`_override_entries`, `_append_override_entry`, `waive()`,
  `dispatch()`'s claim/release/waive branches) — read-only context.
- Do NOT touch `generate_spine.py`, `specs/`, the attest/condition surface, shipped spine templates.

## Constraints
- `override_summary`'s counts and id-list must be derivable purely from `_override_entries(cl)` —
  no direct `cl.get("override_ledger")`/`cl.get("trip_ledger")` reads outside that function.
- `finish_work`'s `overrides` computation must work correctly on a schema where non-trip kinds lack
  an `outcome` field (this is the actual shipped schema after g1/g2 — verify against the real
  `_append_override_entry` call sites in `dispatch()`, not an assumed shape).

## Map Anchors (inbound)
- **Map entry point:** `scripts/checklist_engine.py` (`_override_entries`, landed g1) first, then
  `scripts/apply_episode_delta.py` (search `MECHANICAL_ALL_FIELDS`/`_validate_create`), then
  `scripts/episode_capture.py` (search `mechanical_fields`), then `scripts/spine_lifecycle.py`
  (search `finish_work`).
- **Structural:** `struct:scripts/episode_capture.py#mechanical_fields, function`;
  `struct:scripts/apply_episode_delta.py#_validate_create, function`;
  `struct:scripts/spine_lifecycle.py#finish_work, function`.
- **Capability:** `capability:closeout-episode-capture`; `capability:closeout-finish-work`.
- **Constraints/assumptions:** `constraint:no-unwired-checker` — any new check must run somewhere
  that can fail it; `constraint:mechanical-fields-and-episode-delta-allowlist-travel-together` — the
  reason PART B and PART C are one gate, not two.
- **Decision anchors:** `decision:closeout-render-target-is-both` — wire `mechanical_fields`
  (durable) AND `finish_work`'s return dict (immediate), not one or the other.
  `@grade: settled/human · leans g3-implement`
- **Evidence expectations:** `claim:finish_work-currently-blind-to-trip-ledger` — verified at plan
  time by grep; this gate is the fix.

## Deliverable Path Check
- **Committed** — `scripts/checklist_engine.py`; `scripts/apply_episode_delta.py`;
  `scripts/episode_capture.py`; `scripts/spine_lifecycle.py`; plus whichever test files you touch.
  Verify each with `git check-ignore <path>` exiting 1 before you finish.

## Required Evidence
- The round-trip test (mechanical_fields → apply_episode_delta create-op validation) pass/fail,
  individually — this is the load-bearing one.
- `pytest tests/test_episode_fields.py -q` full output.
- `pytest tests/test_spine_lifecycle.py -q` full output.
- Whichever test file covers `apply_episode_delta.py`'s validator — full output.
- `pytest tests/test_checklist_engine.py -q` full output (confirmatory — you're adding a pure
  function there, should not regress anything).
- Four individual pass/fail results, one per `finish_work` return point.

## Wiring Grep
```bash
grep -rn "override_summary" --include=*.py . | grep -v "def override_summary"
```
State the count of call sites found (expected: `mechanical_fields()` and `finish_work`, plus your
own tests).

## Verification Commands
```bash
cd /home/tommy/projects/569-w2-ledger
python -m pytest tests/test_episode_fields.py tests/test_spine_lifecycle.py tests/test_checklist_engine.py -q
grep -n "override_summary" scripts/checklist_engine.py scripts/episode_capture.py scripts/spine_lifecycle.py
```

## Suggested Model Tier
simple bounded — sonnet. Four well-specified, individually small edits across four files; the risk
is completeness (all four `finish_work` return points, the PART B/PART C pairing), not conceptual
difficulty.

## Authority
The decision to render at both `mechanical_fields` and `finish_work`'s return dict (rather than
picking one) was made by the Commander at plan time. Do not drop either target without stopping and
reporting why.

## Stop Conditions
Stop and return if: the round-trip test cannot be made to pass without a change PART B doesn't
already cover; `finish_work`'s four return points don't have a clean common computation point
(name the actual structural obstacle); required evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced,
assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/w2-ledger/crew-handoffs/g3-implement-implementer-result.md` before ending your turn.
