# Implementation Result

## Assigned gate
`g1-implement` — work-id `r418-460`, issue #460, branch `epic-418/b-460-episodes-observations`.

## Completed slice
Added a fourth op kind, `restate-assertion`, to the episode store's only write path. It
replaces exactly one assertion's `statement` and appends exactly one `- history:` line
carrying the original statement verbatim. The history line is built inside the writer from
the parsed original, so no caller can supply or influence the quoted text; the caller's
`history` value supplies only the reason.

Both op dispatch sites — `apply_delta` and `_dry_run_log` — now register the new op and
both end in `else: raise`, so an op admitted to `OP_KINDS` but missing a branch fails
visibly instead of being silently skipped.

## Scope
**Files changed:**
- `scripts/apply_episode_delta.py` (+126/-2)
- `tests/test_episode_store.py` (+475)

`git diff --stat` for the two: `2 files changed, 599 insertions(+), 2 deletions(-)`.

**Specific exclusions touched:** no. `git status --short episodes/ docs/
scripts/checklist_engine.py scripts/collect_feedback.py
scripts/verify_worktree_precondition_coverage.py` returns empty — every fenced path is
untouched. Every writer invocation in evidence ran against a throwaway store root; the real
`episodes/` was never written to.

## Behavior changed
Yes. Four additions to `scripts/apply_episode_delta.py`:

- `OP_KINDS` is now `("create", "amend-assertion", "restate-assertion", "retire")`, plus a
  new `RESTATE_ALLOWED_FIELDS = ("op", "id", "assertion", "statement", "history")`
  allowlist.
- `_validate_restate_assertion(op)` — checks the extra-field allowlist **first**, then the
  episode id, the assertion id (`a<n>` or `d<n>`), then `_require_str` on `statement` and
  on `history`. Registered in `validate_delta`.
- `_restatement_history_line(reason, original_statement)` and
  `_apply_restate_assertion(tx, op)` — the applier reads the original statement off the
  parsed record before overwriting it and passes it to the line builder. Registered at both
  dispatch sites.
- `_unhandled_op_kind_message(kind, site)` — the message behind the new `else: raise` at
  both dispatch sites; it names the site that missed the op.

The module docstring's op vocabulary now documents `restate-assertion`, matching how the
other three ops are documented there. `docs/EPISODE_STORE.md` is untouched — documenting
the op is gate g4.

Single-line enforcement on the new `statement` is not a second implementation: it is the
same `_require_str` → `_reject_newline` pair create-time statements go through, so it
cannot drift from create's.

## Decisions taken within the granted latitude

**History line format** — `restated — <reason> — original statement was: <original>`.
The original goes last behind a fixed marker so it is the unambiguous tail of the line: a
reader needs no knowledge of how the reason was worded to see where the quoted original
begins. Both halves are single-line-validated before they meet, so the rendered line cannot
grow a second line and forge a store field.

**Extra-field check runs before the per-field checks** — so a delta that misfiles
`lifecycle-standing` onto a restatement is refused for the reason it is actually wrong,
rather than passing quietly because the four required fields happened to be well-formed
alongside it.

**`lifecycle-standing`, `strength` and `kind` are refused on the op**, not silently
ignored. A restatement changes wording; epistemic status moves only through
`amend-assertion`.

## Map Impact
- **Structural anchors touched:** `scripts/apply_episode_delta.py` — the only write path
  into `episodes/`. Its op vocabulary grew from three kinds to four, and its two op
  dispatch chains became total (every kind in `OP_KINDS` has a branch, and anything else
  raises).
- **Capabilities added:** the episode write path can now restate an assertion — rewrite one
  `statement` while preserving the original wording verbatim in that assertion's own
  history. Previously the write path could change an assertion's epistemic standing but not
  its text.
- **Constraints/assumptions touched:** `docs/EPISODE_STORE.md` §5 ("the record grows rather
  than getting rewritten") is honored, not stressed: nothing the store ever asserted is
  destroyed, because the original wording moves into history in the same op that replaces
  it. The determinism constraint is honored — the writer still calls no wall-clock source;
  every "when" still arrives in the delta.
- **Decision candidates / resolved decisions:** `decision:restate-not-amend` — inherited
  from the Commander, ratified by the Admiral, not revisited. The code confirms the premise
  the decision rests on: `_validate_amend_assertion` accepts no `statement` field and
  `_apply_amend_assertion` writes only `lifecycle_standing` plus one history line.
- **Claims/evidence produced:** the two dispatch sites were independent if/elif chains with
  no `else` (confirmed in source before the change); nine mutations of the shipped writer
  each drive the new tests red.
- **Triage candidates:** one — see Out-of-scope observations.

## Test mode
**Required:** `test-after` (tests load-bearing, same delivery)
**Satisfied:** yes. 21 new tests in `tests/test_episode_store.py::RestateAssertionTests`
cover all seven named cases plus the confirmatory refusals, and each was demonstrated able
to reach a failing state.

## Evidence

### Branch baseline, reproduced before any edit

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

```
1721 passed, 4 skipped, 643 subtests passed in 429.70s (0:07:09)
EXIT=0
```

Matches the handoff's stated baseline exactly.

### Full suite after the change

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

```
1742 passed, 4 skipped, 672 subtests passed in 479.78s (0:07:59)
EXIT=0
```

Deltas against baseline: **+21 passed, +29 subtests, skips unchanged at 4.**
`pytest --collect-only tests/test_episode_store.py::RestateAssertionTests` reports
`21 tests collected` — so every added test is this slice's own and nothing else moved.

This same command also ran as the engine's `m3-full-suite` command postcondition; the
engine's `advance` succeeded, which is an independent second green run.

### Targeted file

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_episode_store.py
```

```
127 passed, 1 skipped, 45 subtests passed in 10.15s
EXIT=0
```

### Required-evidence cases, by letter

| case | test(s) |
|---|---|
| (a) only the named assertion's statement changes; siblings, `## Mechanical`, `strength`, `kind`, `lifecycle-standing` and `## Retirement` byte-identical | `test_restate_changes_only_the_named_assertions_statement` |
| (b) the appended history line carries the original statement verbatim | `test_the_appended_history_line_carries_the_original_statement_verbatim`, `test_the_history_line_quotes_the_record_not_the_caller`, `test_a_reason_that_misquotes_the_record_does_not_change_what_is_quoted` |
| (c) a multi-line statement is refused | `test_a_multi_line_statement_is_refused` (subtests over `\n`, `\r`, U+2028, `\x0b`) |
| (d) an unknown assertion id is refused | `test_an_unknown_assertion_id_is_refused`, `test_a_malformed_assertion_id_is_refused` |
| (e) all-or-nothing across a two-op delta | `test_a_two_op_delta_with_an_invalid_second_op_leaves_the_first_ops_file_unchanged`, plus `test_the_two_op_atomicity_exercise_is_not_vacuous` |
| (f) a dry-run restate logs the op and writes nothing | `test_a_restate_under_dry_run_logs_the_op_and_writes_nothing`, `test_the_dry_run_log_line_matches_the_one_a_real_apply_emits`, `test_a_dry_run_of_an_invalid_restate_still_refuses` |
| (g) a misfiled extra field is refused | `test_a_misfiled_extra_field_on_the_op_is_refused` (subtests over `lifecycle-standing`, `strength`, `kind`, `reason`, `retired-at`, a typo'd key), `test_a_misfiled_lifecycle_standing_is_refused_even_when_it_is_a_legal_value` |
| both dispatch sites | `test_an_op_kind_in_op_kinds_but_absent_from_a_dispatch_site_fails_visibly`, `test_every_op_kind_is_dispatched_at_both_sites` |

On (b), the decisive test is `test_the_history_line_quotes_the_record_not_the_caller`: it
runs the **same** op text against two records whose originals differ and asserts the two
history lines differ exactly by the original. Any implementation that let the caller author
or influence the quoted text would produce identical lines and fail.

On the second dispatch test, `test_every_op_kind_is_dispatched_at_both_sites` drives every
member of the shipped `OP_KINDS` through both chains and asserts each produces a log line —
so a future op wired into only one chain fails without anyone remembering to extend the
test. It also asserts its own probe table equals `sorted(OP_KINDS)`, so it cannot quietly
probe three of four kinds.

### These checks can fail — nine mutations, all red

A check that cannot fail is indistinguishable from one that passed, so each guard was
driven to red against a deliberately broken writer. Both probes restore the source
byte-for-byte and assert the restore. Re-runnable:

```bash
FORCE_COLOR= NO_COLOR=1 python .agent-work/r418-460/evidence/mutate_probe.py
FORCE_COLOR= NO_COLOR=1 python .agent-work/r418-460/evidence/mutate_probe_dispatch.py
```

```
detected working-tree line ending: '\r\n'
history-line-drops-the-original: exit=1 RED (good) :: 5 failed, 11 passed
restate-also-flips-lifecycle-standing: exit=1 RED (good) :: 1 failed, 15 passed
restate-also-touches-a-sibling: exit=1 RED (good) :: 1 failed, 15 passed
history-line-appended-twice: exit=1 RED (good) :: 3 failed, 13 passed
extra-field-allowlist-removed: exit=1 RED (good) :: 7 failed, 15 passed
unknown-assertion-id-silently-ignored: exit=1 RED (good) :: 1 failed, 15 passed
restored byte-for-byte: True
mutations probed: 6 | vacuous or unapplied: []
PROBE_EXIT=0
```

```
restate-not-registered-in-dry-run: exit=1 RED (good) :: 4 failed, 18 passed
apply_delta-else-removed: exit=1 RED (good) :: 1 failed, 21 passed
dry_run-else-removed: exit=1 RED (good) :: 1 failed, 21 passed
restored byte-for-byte: True
mutations probed: 3 | vacuous or unapplied: []
PROBE_EXIT=0
```

The first mutation in the second probe is the handoff's named defect reproduced exactly:
register `restate-assertion` at `apply_delta` only. Four tests catch it.

### Wiring grep

```bash
grep -rn "restate-assertion\|restate_assertion" --include=*.py . | grep -v "def _validate_restate_assertion" | grep -v "def _apply_restate_assertion"
```

Call sites outside each new symbol's own definition, in `scripts/`:

| symbol | external call sites | where |
|---|---|---|
| `_apply_restate_assertion` | **2** | `apply_delta` (`:1249`), `_dry_run_log` (`:1433`) |
| `_validate_restate_assertion` | **1** | `validate_delta` (`:898`) |
| `_restatement_history_line` | **1** | `_apply_restate_assertion` |
| `_unhandled_op_kind_message` | **2** | the `else` at each dispatch site |

The raw grep reports 3 hits for `_apply_restate_assertion`; the third (`:1326`) is a
docstring mention inside `_restatement_history_line`, not a call. Zero external call sites
for either required symbol would have been a stop condition — none is zero.

The grep also matches the two probe scripts under `.agent-work/`, which hold the mutation
anchors as string literals. Those are evidence, not shipped code.

### Confirmatory CLI spot-check (throwaway store root, never `episodes/`)

```bash
python scripts/apply_episode_delta.py --delta "$TMP/restate.json" --store-root "$TMP/episodes" --dry-run
python scripts/apply_episode_delta.py --delta "$TMP/bad-id.json" --store-root "$TMP/episodes"
python scripts/apply_episode_delta.py --delta "$TMP/restate.json" --store-root "$TMP/episodes"
```

```
--- dry-run restate ---
restated spot-460-001.a5
DRY RUN — no write
EXIT=0
--- unknown episode id ---
error: no such episode: spot-460-999
EXIT=1
--- real restate ---
restated spot-460-001.a5
EXIT=0
```

The resulting assertion, showing the shape gate g2 will produce:

```
### assertion:spot-460-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: The run passed --store-root episodes on every writer invocation.
- history: restated — restated as an observation (issue #460) — original statement was: Always pass --store-root episodes when invoking the writer.
```

## TDD evidence, if required
Not required — test mode is test-after. The equivalent rigor was supplied by the mutation
probes above: every new guard was observed red against a broken writer and green against
the shipped one.

## Docs/contracts touched
- `scripts/apply_episode_delta.py` module docstring — the op vocabulary now documents
  `restate-assertion` alongside the other three, matching the file's own convention.
- `docs/EPISODE_STORE.md` — **not** touched; documenting the op is gate g4, per the
  handoff's exclusions.

## Assumptions
- The history line's exact format was mine to choose under the handoff's Authority section;
  the choice and its rationale are stated above.
- `a5` (`workaround`) is used as the primary test target because it is the bin issue #460
  rewrites. Nothing in the op is specific to it — a diagnosis assertion (`d1`) is covered
  too.
- The two probe scripts were written under `.agent-work/r418-460/evidence/` so the reviewer
  can re-run them. They are throwaway evidence, not shipped code, and are not part of the
  deliverable diff; delete them at closeout if the Commander prefers.

## Stop conditions hit
None. Allowed scope was not exceeded, no exclusion was touched, all required evidence was
produced, the suite is green, and no decision outside the granted authority arose.

## Out-of-scope observations
- **Triage candidate.** `_apply_amend_assertion` and `_apply_restate_assertion` now share
  the same four-line prologue (load the episode, build `all_assertions()`, look up the id,
  raise "no such assertion" if absent), differing only in the error message's op name. It
  is two occurrences, which is the threshold at which a shared `_resolve_assertion(tx, op,
  op_name)` helper starts earning its keep — but extracting it would touch
  `amend-assertion`'s code path, which this gate has no mandate over. Left alone
  deliberately; flagged for a later pass.
- **Observation, not a defect.** `tests/test_episode_store.py` embeds raw U+2028 characters
  in string literals (pre-existing, in `LineBoundaryGuardTests`). My new multi-line test
  follows that convention rather than departing from it, but the character is invisible in
  most editors and an accidental deletion would silently weaken the test without failing
  it. Worth a comment or an escape sweep some day; out of scope here.

## Workflow Feedback
- **Handoff gaps:** the line numbers in the handoff were roughly 20–90 lines stale by the
  time I read the file (`_validate_amend_assertion` was at `:970` as quoted, but
  `apply_delta`'s dispatch was not at `:1169`). The handoff's own Map-confidence flag says
  "verify line numbers rather than trusting the ones quoted here", which is exactly right —
  the friction is that the numbers are quoted at all. Naming the **function** and letting
  the reader grep is strictly better than a number plus a disclaimer that the number may be
  wrong.
- **Context rediscovered:** none of substance. The handoff carried the decision, its
  rejected alternative, the protected intent, the constraint the op answers to, and the
  exact defect to avoid — which is why the code question was settled before I opened the
  file. The one thing I had to discover myself was that the working tree holds CRLF while
  the blob holds LF (`.gitattributes` sets `* text=auto`): my first mutation probe used
  `\n` anchors and four of six mutations silently matched nothing, reporting as "not
  applied". `docs/agents/CREW_CONTEXT.md` warns about this for file *comparison*; it does
  not mention it for *anchor matching*, which is where it actually bit. A probe that had
  not asserted its own mutation applied would have reported four green "non-vacuity" checks
  that never mutated anything — the exact failure CREW_CONTEXT names one paragraph earlier.
- **Instructions improvised around:** the implementer plan template pairs each item with a
  command postcondition, and the honest command for the final item is the full suite — 8
  minutes per run. Between my own verification run and the engine's `advance` check, that
  is 16 minutes of the same suite. Not wrong (the second run is genuine independent
  evidence), but a template note on when a targeted check suffices for intermediate items
  and the full suite belongs only on the terminal one would save a run.
- **Slice-boundary honesty:** I wrote the `_dry_run_log` registration and both `else: raise`
  branches during m1's edit pass rather than m2's, because they are five lines in the same
  two functions m1 was already editing and splitting the edit would have left the file in a
  worse intermediate state. m2's tests and mutation probes are what actually prove them, and
  those were written and run under m2. Reporting the bleed rather than papering over it.
- **What would have made this easier:** drop the line numbers from handoffs in favor of
  function names — the handoff already tells the reader not to trust them.

## Rework 1

Requested by Commander r418-460 after `g1-review` returned APPROVE. Two bounded
follow-ups, both inside the existing allowed scope. Driven through the engine as an added
gate `m5-rework1` (`amend`, authority `commander-r418-460`) rather than a `reopen`, because
the approved slices' evidence still stands and this is additive.

### What changed

**1. `RESTATE_ALLOWED_FIELDS` is now pinned.** Three tests added to
`tests/test_episode_store.py::RestateAssertionTests`:

- `test_the_op_field_allowlist_is_pinned_to_its_exact_membership` — asserts the tuple is
  exactly `("op", "id", "assertion", "statement", "history")`. Its docstring tells whoever
  trips it that the question is not "update the tuple" but whether the new field can carry
  or influence the previous statement.
- `test_no_field_on_the_op_can_supply_the_original_statement` — the behavioural half, and
  the one that catches M4 directly: a delta trying to hand the writer the previous wording
  is refused whatever the field is called (`original`, `original-statement`, `was`,
  `previous`, `history-line`).
- `test_the_quoted_original_is_exactly_the_statement_that_was_on_disk` — asserts the quoted
  original **equals** the record's statement rather than merely being contained in the
  line, and pins the last-marker-wins reader contract the corrected docstring now states.

**2. `_restatement_history_line`'s docstring no longer overclaims.** The format and the
code are unchanged — no escaping added, no marker changed, per the Commander's instruction.
The docstring now says: the original is the text following the marker's **last** occurrence
and must be read with `str.rpartition`, never by searching forward; the marker is **not**
unique on the line, because the reason is free text and may contain it; nothing the record
said is destroyed when that happens (the true original is still the verbatim tail), but a
reader that splits on the first marker gets text the caller wrote.

### Mutation-red proof for the new assertions

The reviewer's M4 reproduced exactly — widen the allowlist with `original`, and have the
applier prefer `op.get("original", assertion.statement)` — then run that same broken writer
twice: once with Rework 1's three tests deselected, once with them in.

```bash
FORCE_COLOR= NO_COLOR=1 PYTHONIOENCODING=utf-8 python .agent-work/r418-460/evidence/mutate_probe_m4.py
```

```
M4 vs the PRE-rework suite (3 new tests deselected): exit=0 GREEN - the reviewer's finding, reproduced :: 21 passed, 3 deselected, 29 subtests passed in 0.39s
M4 vs the POST-rework suite (all tests): exit=1 RED - the pin catches it :: 6 failed, 23 passed, 29 subtests passed in 0.89s
  SUBFAILED(field='original') ...::test_no_field_on_the_op_can_supply_the_original_statement
  SUBFAILED(field='original-statement') ...::test_no_field_on_the_op_can_supply_the_original_statement
  SUBFAILED(field='was') ...::test_no_field_on_the_op_can_supply_the_original_statement
  SUBFAILED(field='previous') ...::test_no_field_on_the_op_can_supply_the_original_statement
  SUBFAILED(field='history-line') ...::test_no_field_on_the_op_can_supply_the_original_statement
  FAILED ...::test_the_op_field_allowlist_is_pinned_to_its_exact_membership
restored byte-for-byte: True
M4 probe: PASS
PROBE_EXIT=0
```

The deselected run reproduces the reviewer's number exactly — **21 passed, exit 0** — which
is the pre-rework class size, so the "before" arm really is the suite the reviewer ran.

**Honest reading of the six failures.** Two are independent catches: the tuple pin, and the
`original` subtest. The other four subtests fail as a **cascade** — the accepted `original`
op mutated the store, so the fixed byte-comparison those subtests share no longer matches.
That shared baseline is deliberate (the store must be unchanged after *all* of them), but
it means the six lines are not six independent catches, and I am not claiming they are.

### Suite after Rework 1

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

```
1745 passed, 4 skipped, 677 subtests passed in 370.26s (0:06:10)
EXIT=0
```

Against the post-g1 numbers (1742 / 4 / 672, exit 0): **+3 passed, +5 subtests**, skips
unchanged — exactly the three tests and five subtests added above. Against the original
branch baseline (1721 / 4 / 643): +24 passed, +34 subtests.

The engine re-ran this same command and the M4 probe as `m5-rework1`'s command
postconditions, so both numbers above have an independent second run behind them.

### Scope and constraints held

Rework 1 changed `scripts/apply_episode_delta.py` (docstring only) and
`tests/test_episode_store.py` (+3 tests). The line format is unchanged and no escaping was
added. The duplicated dispatch-chain prologue was left alone as instructed — the Commander
is logging it as a triage candidate. No new result file; this section was appended to the
existing one. Nothing committed.

## Return status
`complete` — including Rework 1.
