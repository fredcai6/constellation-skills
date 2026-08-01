# Plan critic disposition — issue #309

Cold solo critic (Sonnet, general-purpose agent, dispatched read-only against
`MISSION_FRAME.md` + `PLAN_ALTERNATIVES.md` + `execute.json` only — no author context, no
notes-309.md). Mandatory per `lesson:cold-critic-mandatory-for-measurement-dependent-plans`
(this plan's acceptance depends on a recall/noise measurement). Every finding triaged below
by the Commander (delegated mode — no human to triage to; disposed within Inherited
Latitude, floatable if disputed).

1. **BLOCKING — g1-seed c1 vacuous.** The original check
   (`git status --porcelain .agent-work/ | wc -l -eq 0 || git check-ignore -q ...`) passes
   unconditionally once `.agent-work/` is confirmed tracked (first branch trivially true,
   `.agent-work/` untracked files never show under a directory-scoped porcelain the way I
   wrote it) — and even the ignore branch only proves the directory *could* be ignored, not
   that it holds 4 files. **DISPOSITION: FIXED.** Replaced with explicit `test -f` on all 4
   named files plus a count check plus a real `git check-ignore -q` on an actual file (not
   the bare directory). See `execute.json` g1-seed.c1.

2. **BLOCKING — g0's adversarial test could pass with or without the fix.** A traversal id
   that doesn't resolve to a real existing file returns None from `resolve_episode_path`
   whether or not the `ID_RE` guard exists — a not-found id is not evidence the guard
   fired. **DISPOSITION: FIXED.** g0-fix321-implement's imperative now requires the test to
   (a) assert the traversal target really exists on disk, (b) demonstrate the PRE-fix
   path-join would have pointed at it, (c) only then assert the POST-fix guard refuses it.
   See `execute.json` g0-fix321-implement.

3. **SERIOUS — ground-truth freeze not mechanically enforced.** Prose-only "frozen before
   dispatch" claim, no barrier to post-hoc editing. **DISPOSITION: FIXED.** g1-seed now
   records a hash of `GROUND_TRUTH.json` as evidence at authoring time; g3-score's
   imperative requires reverifying that hash BEFORE scoring, and fails loudly on mismatch.

4. **SERIOUS — g5's `git diff --quiet` compares to the index, not HEAD.** A staged-but-
   uncommitted change to a live corpus file would pass. **DISPOSITION: FIXED.** Changed to
   `git diff --quiet HEAD -- <files>`.

5. **SERIOUS — g3-score's checks are both `check: null` (self-attestation only) in the one
   gate whose entire job is proving non-vacuity.** **DISPOSITION: PARTIALLY FIXED, one
   accepted residual.** Tightened the imperative to require an explicit, quote-grounded,
   non-defaulted outcome for SD5 and DECOY1 (never "silence reads as not-found"), and added
   a mechanical hash-reverify sub-check inside c1. The final recall/noise arithmetic itself
   remains a `null`-checked attestation — I accept this residual because recall/noise are
   *counts against a frozen ground truth*, not a boolean the engine can independently
   recompute without re-parsing free-text viewpoint reports (out of proportion to this
   issue's bound); the mitigation is that my own return (Return Shape item 2) shows the
   actual SD5/DECOY1 outcomes verbatim, not just the attested claim, so anyone reading the
   return can independently check the arithmetic without trusting the attestation alone.

6. **SERIOUS — g1-seed's precondition on g0 completing was an unnecessary serialization**
   (g1's own imperative never touches the episode store; the #321 exposure is at g3/g4).
   **DISPOSITION: FIXED.** Dropped the p1 dependency on g0; g1 now only depends on plan
   confirmation. (g0 and g1 could in principle run as independent tracks; kept sequential
   in `items` ordering for simplicity of a single-threaded Commander run, not because of a
   real dependency — noted so a future run doesn't reintroduce the false dependency as a
   "fix.")

7. **MINOR — g4-episodes c1 was prose-only.** **DISPOSITION: FIXED.** Added a command
   check confirming `query_episodes.py select --field run --value issue-309` returns at
   least one `issue-309-NNN` id, run against the POST-#321-fix code (this store is the one
   this run itself may have just patched).

8. **MINOR — scoring ambiguity when one quoted line supports both an SD and DECOY1.**
   **DISPOSITION: ACCEPTED, not fixed mechanically.** Noted as a real scoring judgment call;
   g3-score's imperative already requires quote-grounding every outcome, which is the
   available mitigation — a finding that cites the SAME line for two different
   ground-truth items gets recorded against both with the shared citation stated explicitly,
   rather than silently picked one way. Genuinely a case-by-case call at scoring time, not a
   plannable-away ambiguity.

9. **Unverifiable from the 3 read files (SD5 unfindability, DECOY1 validity) — correctly
   flagged as unchecked, not passed.** These depend on the actual seeded text, authored
   AFTER the critic ran (ground truth is frozen at g1, after plan approval). No action
   needed at plan stage; this is exactly what g3-score's own scoring step exists to verify
   empirically rather than assume from the plan.

**Separately, my own follow-up check (not a critic finding) surfaced a plan-invalidating
premise defect**: the original plan assumed `.agent-work/` is gitignored (inherited from
`docs/EPISODE_STORE.md` §1's own claim). `git check-ignore -v .agent-work/issue-309/corpus-slice/`
returned exit 1 (NOT ignored) before any mitigation — `.agent-work/` was made TRACKED at
commit b69e6c8 (#326), after EPISODE_STORE.md §1 was written. Both `EPISODE_STORE.md` and my
own first-draft `MISSION_FRAME.md` carried the same now-false premise. Fixed with a
worktree-local `.agent-work/issue-309/.gitignore` (`corpus-slice/`), re-verified with
`git check-ignore -v` (exit 0, confirmed). This is itself a real, live incoherence in the
corpus (EPISODE_STORE.md §1's git-check-ignore transcript is now stale) — filed as a triage
candidate, see Return Shape item 6.

**Panel-vs-single choice, reaffirmed after disposition**: single lightweight critic was
sufficient — it caught two BLOCKING vacuous-check defects and three SERIOUS issues on its
own; nothing in its findings suggests a wider panel was needed for a plan this bounded.
