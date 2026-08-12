# Review Result

## Assigned Gate

`g1-review` — work-id `r418-460`, issue #460. Target: the **uncommitted working tree** of
`C:/Programs/constellation-skills-wt/r418-460`, files `scripts/apply_episode_delta.py` and
`tests/test_episode_store.py`.

Survey: `.agent-work/r418-460/g1-review/review.json` (engine-driven, session `rev-g1-460`, 12 items,
consolidated). Fowler record: `.agent-work/r418-460/g1-review/fowler-pass.json`.

## Result

`APPROVE`

No blockers. Three triage candidates, all recorded in the survey.

## Per-check findings against the six close criteria

### C1 — registered in `OP_KINDS`, dispatched at both sites, both ending in `else: raise`

**PASS.** Verified against the file, not the handoff's quoted line numbers.

- `OP_KINDS` (line 170) = `("create", "amend-assertion", "restate-assertion", "retire")`.
- `validate_delta` dispatches to `_validate_restate_assertion`.
- `apply_delta` carries the restate branch and a terminal `else` at line 1252.
- `_dry_run_log` carries the restate branch and a terminal `else` at line 1436.
- Each `else` raises `_unhandled_op_kind_message(kind, site)` naming **its own** site, so a failure says
  which chain missed the op.

Wiring counts reproduced and they match the implementer's claim exactly (external call sites, excluding
the `def` line and one docstring mention): `_apply_restate_assertion` 2, `_validate_restate_assertion` 1,
`_restatement_history_line` 1, `_unhandled_op_kind_message` 2.

### C2 — the history line is built inside the writer from the parsed original (LOAD-BEARING)

**PASS.** This is the criterion the gate rests on, so I established it two ways.

*By reading the code.* `_apply_restate_assertion` reads the original off the parsed record **before**
overwriting it:

```
original_statement = assertion.statement
assertion.statement = op["statement"].strip()
assertion.history.append(
    _restatement_history_line(op["history"].strip(), original_statement)
)
```

and the builder is

```
return f"restated — {reason} — original statement was: {original_statement}"
```

`reason` is the caller's `history` value; `original_statement` comes only from `assertion.statement`.
The op's field allowlist is `RESTATE_ALLOWED_FIELDS = ("op", "id", "assertion", "statement", "history")`,
checked **first**, before the per-field checks — so there is no caller-supplied field that reaches the
`original_statement` argument. **No caller can author, supply, or influence the quoted-original text.**

*By experiment.* I ran the shipped writer against a real store and confirmed the quoted original is the
record's, and that a caller reason claiming the record said something else does not change what is quoted.
Mutation M5 — rewire the builder to quote `op["statement"]` instead of the parsed original — turns **5
tests red**, so the property is test-pinned, not merely true by accident.

One nuance, filed as a triage candidate rather than a blocker (see tc2 below): a caller's *reason* can
embed the literal marker text, producing two markers on one line. The genuine original still survives
verbatim as the last one — nothing is destroyed — but the docstring's claim that a reader "needs no
knowledge of how the reason was worded" is an overclaim.

### C3 — `kind`, `strength`, `lifecycle-standing`, siblings, `## Mechanical`, `## Retirement` untouched

**PASS.** The applier assigns exactly two things: `assertion.statement` and one appended
`assertion.history` entry. Nothing else is written. Pinned by
`test_restate_changes_only_the_named_assertions_statement`, which byte-compares each sibling assertion
block, the whole `## Mechanical` slice and the whole `## Retirement` slice. Mutation M6 (make the restate
also flip `lifecycle-standing`) turns that test red, so the guard works. I separately confirmed
`render_episode(parse_episode(text)) == text` still holds on a real restated file.

### C4 — tests exist and pass for (a) through (g)

**PASS.** All seven present, and each demonstrated able to fail.

| | covered by | mutation that reddens it |
|---|---|---|
| (a) only the named statement changes; siblings + mechanical byte-identical | `test_restate_changes_only_the_named_assertions_statement` | M6 |
| (b) history line carries the original verbatim | `test_the_appended_history_line_carries_the_original_statement_verbatim`, `test_the_history_line_quotes_the_record_not_the_caller` | M5 (5 red) |
| (c) multi-line statement refused | `test_a_multi_line_statement_is_refused` (subtests over `\n`, `\r`, `\u2028`, `\x0b`) | — reuses create's `_require_str` |
| (d) unknown assertion id refused | `test_an_unknown_assertion_id_is_refused` (uses `a9`, well-formed but absent, so the refusal must come from the applier's lookup, not the regex) | — |
| (e) two-op delta, invalid second op, first op's file unchanged | `test_a_two_op_delta_with_an_invalid_second_op_leaves_the_first_ops_file_unchanged`, plus `test_the_two_op_atomicity_exercise_is_not_vacuous` | — the vacuity twin is the right instinct |
| (f) `--dry-run` logs the op and writes nothing | `test_a_restate_under_dry_run_logs_the_op_and_writes_nothing`, `test_the_dry_run_log_line_matches_the_one_a_real_apply_emits` | M1 (4 red) |
| (g) misfiled extra field refused | `test_a_misfiled_extra_field_on_the_op_is_refused`, `test_a_misfiled_lifecycle_standing_is_refused_even_when_it_is_a_legal_value` | M7 (7 red) |

Two tests deserve specific credit. `test_the_history_line_quotes_the_record_not_the_caller` states the
protected property as an **experiment** — same op text against two records with different originals must
produce different history lines — so it fails against any implementation that lets the caller influence
the quoted text, rather than asserting a format string. And `test_every_op_kind_is_dispatched_at_both_sites`
derives its guard from the consumer: it asserts `sorted(minimal) == sorted(m.OP_KINDS)` and
`probed == 2 * len(OP_KINDS)`, satisfying CREW_CONTEXT's "any guard that loops must assert what it
looped over."

### C5 — the suite is green, real exit code

**PASS.** I ran it myself from the worktree root, with `python`, never `py`:

```
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
1742 passed, 4 skipped, 672 subtests passed in 450.58s (0:07:30)
EXIT=0
```

Exit code captured immediately after the redirect so no pipeline masked it. Matches the handoff's
expected 1742 / 4 / 672 / 0 exactly. Log: `.agent-work/r418-460/g1-review/pytest_full.txt`.

### C6 — nothing under `episodes/`, `docs/`, or the three fenced scripts modified

**PASS.**

- `git diff --name-only HEAD` filtered of `.agent-work/` returns exactly the two allowed files.
- No untracked file anywhere outside `.agent-work/`.
- `git status --porcelain -- episodes docs scripts/checklist_engine.py scripts/collect_feedback.py scripts/verify_worktree_precondition_coverage.py` is **empty**.
- `docs/EPISODE_STORE.md` and `docs/agents/*` untouched; no new advice-accumulating file.
- `episodes/` still clean after a full suite run, so no test escapes to the real store.

## Handoff compliance

The change does what the handoff asked and nothing more. Fields are exactly `id`, `assertion`,
`statement`, `history`. Single-line enforcement on the new statement **reuses** create's `_require_str` /
`_reject_newline` rather than reimplementing it, so it cannot drift from create's. Refusals are in place
for unknown episode id, unknown assertion id, malformed assertion id, missing/blank `statement`,
missing/blank `history`, and any misfiled extra field. Both dispatch sites gained an `else` that raises.

## Scope drift

None. See C6.

Noted, not blocked on, per the handoff: implementer scratch remains under `.agent-work/r418-460/` —
`evidence/mutate_probe.py`, `evidence/mutate_probe_dispatch.py`, `fixup.py`,
`r418-460-g1-implement/`. Commander's to clean up. My own scratch is confined to
`.agent-work/r418-460/g1-review/` (`pytest_full.txt`, `mut1.txt`, `fowler-pass.json`, and the isolated
`mutant/` tree).

## Evidence verdict

Reproduced, not accepted.

I did **not** run the implementer's probes. I built an independent harness: a full copy of the relevant
tree at `.agent-work/r418-460/g1-review/mutant/`, so **no source or test file in the worktree was
modified at any point**. Every mutation asserted it had applied before running (a `sed` that matches
nothing leaves a green suite that reads exactly like a passing guard), and the copy was restored to
pristine and byte-compared at the end.

| mutation | result |
|---|---|
| M1 — register at `apply_delta` only (restate branch deleted from `_dry_run_log`) | **4 tests red**, exactly the count claimed |
| M2 — `else` removed from `apply_delta` only | red (SUBFAILED `site='apply_delta'`) |
| M3 — `else` removed from `_dry_run_log` only | red (SUBFAILED `site='_dry_run_log'`) |
| M4 — widen the allowlist with `original`, prefer `op["original"]` | **GREEN — 21 passed, exit 0** (see tc1) |
| M5 — history quotes the new statement, not the original | 5 tests red |
| M6 — restate also flips `lifecycle-standing` | red |
| M7 — misfiled-extra-field guard removed | 7 tests red |
| M8 — history replaced instead of appended | red |

Each `else` is caught **independently** — one does not imply the other, which was the asymmetry that
caused the original defect. That claim is now verified, not asserted.

## Code/doc quality

Good. The four new functions are 27 / 19 / 16 / 16 lines *including* docstrings (measured with `ast`,
not by eye); code-line counts are ~15 / 7 / 1 / 5. They follow the module's established
`_validate_X` / `_apply_X` pair shape. Error messages name the failing site rather than being generic.
The allowlist is checked first so a misfiled field is refused for the reason it is actually wrong.

Comment density is high (~60 of 126 added lines in the applier are prose), but it matches the host
file's existing voice and records **why** — the defect class the `else: raise` closes, which field must
never reach the quoted original — rather than restating what the code does. Judged `overridden` in the
Fowler pass against `global-crew.md`'s "match the surrounding code's in-file documentation conventions."

## Map impact verdict

- **Evidence supports claimed change:** Yes. The suite figures, the mutation counts and the wiring
  counts all reproduce.
- **Constraints not violated:** Yes. `episodes/` untouched and still the sole write path; every test
  invocation passes an explicit `--store-root` to a tempdir; the test command was run exactly as
  specified with `python`; and `docs/EPISODE_STORE.md` §5 ("the record grows rather than getting
  rewritten") is honored — verified behaviorally, including that a **second** restatement appends
  rather than replacing, so every earlier wording stays recoverable.
- **Notes match the diff:** Yes. Nothing structural is overstated. The op adds no module, no seam and
  no external interface.
- **Decision candidates surfaced:** None needed. The inbound decision anchor — add a `restate-assertion`
  op rather than annotate with `amend-assertion`, `@grade: settled/inherited` — is **confirmed** by the
  code rather than contradicted: `_validate_amend_assertion` accepts no `statement` field at all, so
  `amend-assertion` genuinely cannot do this job. Nothing to unsettle.
- **Durable context routed:** Three triage candidates recorded in the survey (`tc1`–`tc3`) rather than
  fixed silently or dropped. Documenting the op is gate g4 and is correctly absent here.

## Reconciliation check

No divergence needing Commander reconciliation.

## Blockers

- None.

## Out-of-scope observations

**tc1 — the field allowlist's membership is not test-pinned (the one I would fix first).**
Mutation M4 — add an `original` key to `RESTATE_ALLOWED_FIELDS` and change the applier to
`op.get("original", assertion.statement)` — runs **green**: 21 passed, exit 0, no test notices. The
shipped code has no such hole, so C2 holds today. The gap is that nothing stops a later change from
reopening the exact evidence-destruction risk this gate exists to close, in the store's only write path.
`test_a_misfiled_extra_field_on_the_op_is_refused` iterates a *hand-authored* list of six field names —
the shape CREW_CONTEXT warns against — and a negative list cannot see a widened positive one. One line
closes it: `assertEqual(m.RESTATE_ALLOWED_FIELDS, ("op","id","assertion","statement","history"))`.
Not a blocker: the realistic regression (rewiring the existing call site) is caught by M5.

**tc2 — a docstring overclaim, plus an optional hardening.**
`_restatement_history_line`'s docstring says the original "goes LAST, behind a fixed marker, so it is the
unambiguous tail of the line: a reader needs no knowledge of how the reason was worded to see where the
quoted original begins." Reproduced counterexample — a caller reason containing the marker text yields:

```
- history: restated — spoofed — original statement was: THE RECORD NEVER SAID THIS — original statement was: Always pass --store-root episodes.
```

The genuine original survives verbatim as the **last** occurrence, so no evidence is destroyed and C2 is
unaffected. But a reader splitting on the *first* marker reads the caller's forged text. Fix is any one
of: reject a reason containing the marker in `_validate_restate_assertion`; delimit the original; or
correct the docstring to say "the last occurrence." CREW_CONTEXT's own rule — "assert against behaviour,
never against text that describes it" — is why this is worth recording.

**tc3 — collapse the duplicated dispatch chains.**
`apply_delta` and `_dry_run_log` now hold two near-identical 12-line `if/elif` chains differing only in
the site name, and adding one op required four coordinated edit sites. That duplication is precisely what
produced the silent-skip defect the new `else: raise` catches. A single `_dispatch_op(tx, op)` helper
would make "registered at one site only" *unrepresentable* rather than merely guarded. Out of this
handoff's minimal-change scope, and the current guard plus
`test_every_op_kind_is_dispatched_at_both_sites` do close the failure mode — but the structural fix is
strictly better.

**Not a finding, recorded for completeness.** A `restate-assertion` against an assertion inside a
**retired** episode is accepted. This matches `amend-assertion`'s behavior and is arguably correct
(a retired episode is retained, not frozen), and the handoff's task statement says nothing about it,
so I am not treating it as a defect — only noting that the behavior is unspecified.

## Workflow Feedback

- **Handoff gaps:** The **Survey State Location** field and the SKILL's own instruction disagree with
  each other on the path shape, and the handoff's own two mentions differ in nesting depth from the
  skill's `.agent-work/<work-id>/<gate>-review/review.json`. I used the handoff's explicit path
  (`.agent-work/r418-460/g1-review/review.json`) since it was the more specific instruction. Worth
  making the handoff say "this overrides the skill's default" explicitly. Second, the handoff's
  **Close Criteria** list seven lettered sub-cases under criterion 4 but the survey template has six
  generic items, so the mapping from criteria to survey checks is left entirely to the reviewer — I
  appended `r4a`–`r4e` to carry the Constraints section, but the lettered (a)–(g) cases ended up
  documented in this result rather than as engine-visible checks.
- **Context rediscovered:** The handoff warned its line numbers were stale and told me to verify against
  the file — that warning was accurate and useful, and I did. What I had to dig up unaided was **how the
  test module loads the writer** (`importlib` from `ROOT/"scripts"`, `ROOT = parents[1]`). That detail is
  what made an isolated mutation harness possible without editing any tracked file, and it is exactly the
  thing a handoff that says "do not modify any source or test file" *and* "reproduce the mutation" needs
  to carry — otherwise those two instructions look mutually exclusive and a reviewer may mutate in place
  and hope to restore.
- **Instructions improvised around:** Two.
  (1) **Engine gap.** `r6-fowler`'s postcondition ships with the literal placeholder
  `python scripts/verify_fowler_pass.py <fowler-pass-record-path>`, and the item's imperative instructs
  the reviewer to "fill this item's postcondition command with the real record path." **No engine verb
  can do that.** `amend` is refused on a survey (`REFUSED: amend applies to gated checklists`), and
  `attest` cannot satisfy a `command` postcondition by design. Meanwhile `record` refuses with
  "Do not edit the JSON — use the engine." So the instruction and the refusal message contradict one
  another and the only path forward is the edit the refusal warns against. I substituted **only the
  placeholder token** in `check.command`, touching no `status`, `result` or `satisfied` field, and I am
  logging it here rather than leaving it silent. The clean fix is a `parameterize`/`bind` verb, or
  having `verify_fowler_pass.py`'s postcondition resolve a conventional path.
  (2) The skill says to append "one check per inherited rule" but `append` creates flat siblings only —
  nesting under `r4` is refused — so `r4a`–`r4e` sit as top-level items and the parent/child relationship
  exists only in my findings text.
- **What would have made this easier:** State in the handoff how to reproduce mutations without touching
  tracked files (copy the tree; the test module resolves the writer from `ROOT/"scripts"`). It is the
  single highest-value line the handoff could add, because "do not modify any source or test file" and
  "re-run the mutation yourself" read as a contradiction until you know the loader's shape.

## Return status

`complete`
