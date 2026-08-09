# Implementer Handoff

## Gate
`g1-implement` — work-id `r418-460`, issue #460, worktree `C:/Programs/constellation-skills-wt/r418-460`, branch `epic-418/b-460-episodes-observations`.

## Task
Add a fourth op kind, `restate-assertion`, to `scripts/apply_episode_delta.py`.

**Why it is needed, and why not the cheaper alternative.** Issue #460 asks for the prescriptive
`workaround` statements in `episodes/active/` to be rewritten as observations, and asserts the
rewrite goes through `amend-assertion`. That is not true of the code: `_validate_amend_assertion`
(`scripts/apply_episode_delta.py:970`) accepts no `statement` field, and `_apply_amend_assertion`
(`:1227`) changes only `lifecycle-standing` plus one appended history line — deliberately, per its
own comment. A cold plan critic raised the cheaper route: leave the text alone and mark it
`lifecycle-standing: superseded` with a history line. It is rejected, on the record — the
prescriptive sentence would still stand as the live statement, so an agent opening the file still
finds an instruction, and the issue's first acceptance criterion is that every workaround *reads*
as an observation. `episodes/` must never be hand-edited, so there is no third way.

**The constraint this op must answer to.** `docs/EPISODE_STORE.md` §5 says the record grows rather
than getting rewritten, and its worked example deliberately leaves `statement` untouched. That
section is **not** support for this op — it is what the op has to satisfy. It is satisfied by
preserving the original wording **verbatim** in the assertion's own history, so nothing the store
ever asserted is destroyed.

## Protected Intent
The episode store is a record of what happened. This op exists so a prescriptive record can be
restated as an observation **without losing what the record originally said**. An implementation
that lets the original wording be dropped, paraphrased, or supplied by the caller defeats the
whole point.

## Test Mode
Test-after allowed; tests are load-bearing and must be in the same delivery. The op is a new code
path in the store's only write path, so the seven listed cases below are the deliverable, not a
nice-to-have.

## Close Criteria
- `restate-assertion` is in `OP_KINDS` (`scripts/apply_episode_delta.py:151`), validated, and
  registered at **both** apply/dry-run dispatch sites.
- The op takes exactly: `id`, `assertion` (`a<n>` or `d<n>`), `statement` (the new text), and
  `history` (why it was restated). Any other field on the op is refused.
- It replaces exactly that one assertion's `statement` and appends **one** `- history:` line that
  carries the **original statement verbatim**. The history line is built **inside the writer** from
  the parsed original, so a caller cannot supply a history line that misquotes what was there. The
  caller's `history` value supplies only the *reason*.
- It does **not** touch `kind`, `strength`, `lifecycle-standing`, any sibling assertion, any
  `## Mechanical` line, or the `## Retirement` block.
- Single-line enforcement on the new `statement` applies exactly as it does at create time.
- Validation refuses: unknown episode id; unknown assertion id; missing/blank `statement`;
  missing/blank `history`; any misfiled extra field.
- Both dispatch sites gain an `else: raise` so the next op added cannot repeat the silent-skip
  defect described below.
- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` is green with the real exit code captured.

## Allowed Scope
- `scripts/apply_episode_delta.py`
- `tests/test_episode_store.py`

Both are pre-authorized for edit, including reconciling any existing test whose scenario this
change alters (none is expected — this adds an op rather than changing one).

## Specific Exclusions
- **Do not edit `scripts/checklist_engine.py` (owned by issue #433), `scripts/collect_feedback.py`
  (#464), or `scripts/verify_worktree_precondition_coverage.py` (#436)** — three siblings are
  running concurrently in their own worktrees this wave.
- **Do not edit anything under `episodes/`.** This gate ships the write path only; the actual
  record rewrite is gate g2. Fixtures for tests go in a tmp store, never the real one.
- **Do not edit `docs/EPISODE_STORE.md`** — documenting the new op is gate g4.
- **Do not edit anything under `docs/agents/`.**
- Do not create any file that accumulates distilled advice for future agents, whatever it is named.
- Never create a file whose basename contains `findings`.

## Constraints
- `episodes/` is never hand-edited; `scripts/apply_episode_delta.py` is the only write path.
- Every `apply_episode_delta.py` invocation in evidence or tests against the real store must pass
  `--store-root episodes`. The default resolves against the *installed skill directory* and would
  silently build a store outside the repo while every gate reported green.
- Test command is exactly `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`. **Never `py` for
  pytest**; `FORCE_COLOR=3` gives false reds for `python` too. Capture the **real** exit code.
- Branch baseline: **1721 passed, 4 skipped, 643 subtests, exit 0**. Any deviation other than your
  own added tests is a stop condition.
- Windows host. Use forward-slash absolute paths.

## Map Anchors (inbound)
- **Structural:** `docs/EPISODE_STORE.md` — record grammar, seam set, write-path doctrine
  (hash-pinned substitute; this repo ships no packet map). `episodes/README.md` — store layout.
  `scripts/apply_episode_delta.py` — the only write path.
- **Capability:** the episode write path.
- **Constraints/assumptions:** an episode records what happened and is never read back as a rule
  (`docs/agents/ORCHESTRATOR_CONTEXT.md`, "The Retired Learning Playbook"). `docs/EPISODE_STORE.md`
  §5 — the record grows rather than getting rewritten; that is the constraint a restatement must
  answer to, not support for one.
- **Decision anchors:** add a `restate-assertion` op rather than annotating with `amend-assertion`.
  `@grade: settled/inherited · leans g1-implement` — decided by the Commander under LO-460's
  Inherited Latitude ("how the rewrite is applied through `apply_episode_delta.py`") and ratified by
  the Admiral. Not yours to unsettle; if the code makes it impossible, stop and return.
- **Map confidence flags:** no packet map exists (`map_orient` returned DEGRADED-NO-MAP, discharged
  with four hash-pinned substitutes). `docs/EPISODE_STORE.md` is the structural record this run
  reconciles into. Verify line numbers rather than trusting the ones quoted here.

## Deliverable Path Check
- **Committed** — `scripts/apply_episode_delta.py`; `git check-ignore scripts/apply_episode_delta.py`
  exited **1** (not ignored).
- **Committed** — `tests/test_episode_store.py`; `git check-ignore tests/test_episode_store.py`
  exited **1** (not ignored).
Both files already exist and are tracked, so `git diff` shows both.

## Required Evidence

**Load-bearing — prove rigorously.** Tests in `tests/test_episode_store.py` covering:

- **(a)** a restate changes only the named assertion's `statement`, and leaves every sibling
  assertion, every `## Mechanical` line, `strength`, `kind`, `lifecycle-standing` and the
  `## Retirement` block **byte-identical**;
- **(b)** the appended history line contains the **original statement verbatim**;
- **(c)** a multi-line `statement` is REFUSED;
- **(d)** an unknown assertion id is REFUSED;
- **(e)** the delta is all-or-nothing — a two-op delta whose second op is invalid leaves the first
  op's file unchanged on disk;
- **(f)** a restate under `--dry-run` LOGS the op and writes nothing;
- **(g)** a misfiled extra field on the op is REFUSED.

**Load-bearing — verify it yourself before you code.** **Two dispatch sites, not one.**
`apply_delta` (`:1152`, dispatch at `:1169`) and `_dry_run_log` (`:1298`, dispatch at `:1310`)
dispatch on op kind independently and **neither has an `else` branch**. An op registered in only
one of them makes `--dry-run` silently skip it: no log line, no error, exit 0, "DRY RUN — no
write". Confirm this against the code, register `restate-assertion` at **both**, and add an
`else: raise` at both.

**Confirmatory — a spot-check suffices.** The full suite result and the unknown-episode-id refusal.

## Wiring Grep
One command showing every symbol this slice adds with a call site outside its own definition:

```bash
grep -rn "restate-assertion\|restate_assertion" --include=*.py . | grep -v "def _validate_restate_assertion" | grep -v "def _apply_restate_assertion"
```

State the **count of external call sites** for each new symbol. Zero external call sites for either
new function is a stop condition — the two dispatch sites plus `OP_KINDS` are exactly what wires
this op in, and that is the defect this gate exists to avoid.

## Verification Commands

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_episode_store.py
```

Capture the real exit code of each (`echo "EXIT=$?"` immediately after).

## Suggested Model Tier
Stronger (Opus). The op is small but its correctness conditions are precise and the store is the
run's protected asset.

## Authority
Decided already, not yours to revisit: that the op is `restate-assertion` rather than an
`amend-assertion` annotation; that the original wording is preserved verbatim in history; that the
writer builds the history line rather than the caller. Yours: the internal shape of the validator
and applier, the history line's exact format (state what you chose and why), test structure.

Not yours under any framing: promoting anything into `docs/agents/*`; creating a file that
accumulates advice for future agents; touching the three fenced sibling-owned scripts.

## Stop Conditions
Stop and return if: allowed scope must be exceeded; a specific exclusion must be touched; required
evidence cannot be produced; the suite is red for any reason other than your own in-progress tests;
a decision outside the given authority is needed.

## Return Format
Return **IMPLEMENTER_RESULT** to `.agent-work/r418-460/crew-handoffs/g1-implement-result.md`:
completed slice, files changed, test mode satisfied, evidence produced (with real exit codes),
assumptions used, stop conditions hit, out-of-scope observations, workflow feedback (what in this
handoff or the workflow made the work harder than it needed to be).
