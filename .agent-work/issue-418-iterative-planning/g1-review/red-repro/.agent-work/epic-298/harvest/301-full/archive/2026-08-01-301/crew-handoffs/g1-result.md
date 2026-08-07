# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

VERDICT: COMPLETE

## Assigned gate
`g1` — episode record grammar and store doctrine (issue #301, epic-298) — **rework 2 of a
3-rework cap**, answering `.agent-work/301/crew-handoffs/g1-review-result-2.md` (round-2
`BLOCK`).

## Completed slice
Closed the three round-2 findings and swept the whole class (a MECHANISM described
concretely that silently assumes one retirement-layout option) across every section of
`docs/EPISODE_STORE.md`. All four fixes accepted from rework 1 (SS7 self-contradiction,
`is_episode_in_ordinary_search` membership seam, SS2 path claim, the two self-found SS2
instances) are untouched in substance — only referenced, never rewritten.

## Scope
**Files changed:**
- `docs/EPISODE_STORE.md` (untracked, modified this rework)

**Specific exclusions touched:** no — `.agent-work/LESSONS.md` and
`scripts/apply_lessons_delta.py` untouched; no executable code or tests added; the
retirement layout itself is never chosen anywhere in the current text (both options
remain live in every new seam's adapter pair); `episodes/README.md` re-checked, no edit
needed (already basename-only, no bare full-path instance).

## Behavior changed
No — prose/doctrine only, no executable code, no tests. This gate ships no code by design.

## Per-fix account

**FIX 1 (the important one) — enumeration half of "enumerate non-retired episodes" was
unspecified.** Named a second seam, **`iter_episode_ids(include_retired)`**, in §7,
parallel to §2's already-accepted id-sequence-scan treatment (which is referenced, not
edited): Option-A adapter unions `episodes/active/*.md` and, when `include_retired`,
`episodes/retired/*.md`; Option-B adapter globs `episodes/*.md` unconditionally
(`include_retired` is a no-op for that adapter's own filtering). Stated the composition
rule explicitly: "enumerate non-retired episodes" = `iter_episode_ids(include_retired=False)`
then confirm each id via `is_episode_in_ordinary_search()` before including it — scan then
filter, both steps always, neither folded into the other, so correctness never depends on
which adapter g4 binds. §2's id-sequence scan is now named as this same seam's other
caller (`include_retired=True`), not a bespoke one-off. Rewrote §8's primitive list (fetch
by id, enumerate non-retired, select, neighbour enumeration) so each is explicitly built
from named seams, never an inlined path/glob/grep.

**FIX 2 — no write-side seam for the retire op.** Named **`apply_retirement(episode_id,
reason)`** in §7, placed right after the Layout HELD OPEN paragraph. States explicitly
that the content update (the `status`/`retired-reason`/`retired-at`/`consolidated-into`
field diff already shown in the worked example) is identical under both options and not
gated by layout; only the layout effect differs — Option-A adapter performs the diff then
moves the file `episodes/active/<id>.md` → `episodes/retired/<id>.md`; Option-B adapter
performs the diff only, path unchanged. §10's g2 bullet updated to name this seam as g2's
retire-op obligation.

**FIX 3 (minor) — §9 relied on §2's disclaimer with no local pointer.** Added one sentence
at the top of §9 pointing back to §2's basename-vs-path disclaimer, with a one-clause note
that §9's argument (git commit/merge/fetch mechanics) is unaffected by which layout option
binds — same treatment §7 (SS7) already got in rework 1.

## Sweep — whole class, beyond the three named fixes

Re-read all 10 sections plus `episodes/README.md`. `grep -n 'episodes/'` across the whole
doc, checked every hit for an unqualified bare-path/mechanism claim:

- **Found and fixed (beyond the 3 named findings): §3's worked-example header**
  (`` `episodes/governor-268-003.md`: ``) — same class as SS9's pre-fix state, a bare flat
  path with no local pointer. Fixed with the same pattern: "Option B's path, shown for
  concreteness; per §2's disclaimer, only the basename is settled."
- **Found and fixed (beyond the 3 named findings): §8's "fetch by id = a direct path
  read" claim was itself layout-dependent** — under Option A, which subdirectory holds the
  file is exactly the open question, and no seam covered it. Named a fourth seam,
  **`resolve_episode_path(episode_id)`** — Option-A adapter tries `episodes/active/<id>.md`
  then `episodes/retired/<id>.md`; Option-B adapter is the fixed path. Wired into §7's
  membership-seam paragraph (the "fetch-by-id needs no membership check" sentence now
  correctly distinguishes "no membership check needed" from "does need path resolution")
  and into §8's rewritten primitive list.
- **Checked, no fix needed:** §2 (already-accepted scan/glob treatment, left untouched —
  only referenced from the new seams); §6 (Stratum A table — no path/mechanism claims);
  `episodes/README.md` (basename-only notation throughout, no bare full-path instance).
- **Added the closing consolidation:** a "**The full seam set, gathered in one place**"
  table in §7, naming all five mechanisms — store root (§1, no adapter, layout-invariant),
  `apply_retirement` (write), `is_episode_in_ordinary_search` (membership),
  `iter_episode_ids` (enumeration), `resolve_episode_path` (fetch-by-id) — with their
  adapters, and stating plainly that g4 binds exactly 4 adapters (one per layout-affected
  row) while the store root needs none.

## Map Impact
- **Structural anchors touched:** none — doc-only gate, no code structure.
- **Capabilities added/changed/affected:** none — no executable capability, prose contract
  only.
- **Constraints/assumptions touched:** `decision:episode-store-shape` remains **not
  resolved** — both retirement-layout options stay live in every new seam's adapter pair;
  no adapter is chosen anywhere in the current text.
- **Decision candidates / resolved decisions:** none newly resolved. Four new named seams
  (`apply_retirement`, `iter_episode_ids`, `resolve_episode_path`, plus the already-accepted
  `is_episode_in_ordinary_search`) are scaffolding to carry forward to g2/g3/g4, not
  resolutions of the layout question itself.
- **Claims/evidence produced:** `git status --short` and `python -m pytest tests/ -q`
  reproduced independently below.
- **Trust limitations / drift found:** none found beyond what this rework fixed.
- **Triage candidates:** none identified beyond this gate's own scope.

## Test mode
**Required:** `evidence-only` (this gate ships no executable code or tests).
**Satisfied:** yes — `git status --short` and `python -m pytest tests/ -q` both reproduced
below, matching the required baseline exactly.

## Evidence

```bash
$ git status --short
 A episodes/README.md
?? docs/EPISODE_STORE.md
```

**Result:** pass — exactly the two allowed files, no scope drift.

```bash
$ python -m pytest tests/ -q
1157 passed, 2 skipped, 260 subtests passed in 31.13s
```

**Result:** pass — exact match to the required baseline (1157 passed, 2 skipped).

## TDD evidence, if required
Not applicable — inspection-only gate, no code, no tests (per handoff's explicit
exclusion).

## Docs/contracts touched
- `docs/EPISODE_STORE.md` — the contract this gate exists to produce.

## Assumptions
- None beyond what rework 1 already stated. The four new/extended seams
  (`apply_retirement`, `iter_episode_ids`, `resolve_episode_path`, and the completed
  `is_episode_in_ordinary_search` composition) are named as contracts for g2/g3 to
  implement against, not implemented here.

## Stop conditions hit
- None.

## Out-of-scope observations
- None beyond what is already carried by §10's existing obligations list (updated this
  round to name the new seams g2/g3 must call).

## Workflow Feedback
- **Handoff gaps:** None material. The round-2 BLOCK's "concretely, what breaks" framing
  (tracing what a literal builder would write against the current text) was exactly the
  right test to hand forward — applying the same trace to §8's "fetch by id = a direct
  path read" sentence (not itself one of the three named findings) is what surfaced the
  `resolve_episode_path` gap during the sweep. Worth naming explicitly in the next
  rework-dispatch template for this doc class: after fixing the named findings, re-run the
  literal-builder trace against every remaining primitive description, not just the ones
  already flagged.
- **Context rediscovered:** None — the round-2 review-result, the current doc text, and
  rework 1's plan file (`.agent-work/301/crew-handoffs/g1-rework-plan.json`, read for
  pattern/precedent) carried everything needed.
- **Instructions improvised around:** None. `docs/agents/engine-config.json` referenced by
  the plan's `config_ref` does not exist in this worktree (same as rework 1's plan, which
  completed successfully anyway) — the engine evidently tolerates a missing config_ref by
  falling back to defaults; noting this in case a future rework wants to confirm that
  behavior is intentional rather than silently permissive.
- **What would have made this easier:** Nothing structural. One suggestion: the round-2
  review's own "what would a builder literally write" trace is powerful enough that it
  might be worth promoting from a reviewer technique to an implementer self-check step
  named explicitly in the rework dispatch template, since it is what caught both the named
  gap (enumeration) and the sweep-found one (fetch-by-id path resolution) this round.

## Return status
`complete`
