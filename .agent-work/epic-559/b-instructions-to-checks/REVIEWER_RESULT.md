# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`epic-559/b-instructions-to-checks / g2-review`

## Result
`BLOCK`

## Handoff compliance
Partially satisfied. Scope discipline held: all six shipped role templates were swept (per CENSUS.md),
only the three that needed edits were touched, and the pre-ruling was applied consistently. But the
handoff's second, explicitly named deliverable — "fix the gate that cannot fail (#562)" — is not
reliably fixed. `EXECUTE_PLAN.g1-implement.c1`'s new `match={"status":"complete"}` requires an exact,
case-sensitive `payload.status == "complete"` (confirmed by reading `checklist_engine.py:853-855`). I
scanned every `implementer-result` evidence record recorded anywhere under `.agent-work/` in this
repo's history — 119 records across 40+ real Commander runs, archived and live, 2026-07-08 through
2026-08-10 — and only 28 (24%) carry that exact shape. 41 records (more than "status") use a
`verdict` field instead; 36 carry neither field; 11 use an unrelated bespoke schema
(`gate_id`/`red_exit`/`green_exit`). The fix does not convert a check that cannot fail into one that
reliably passes for legitimate completed work — it converts it into one that blocks the plurality of
this repo's own historical conventions, including the single most common one ("verdict"). This is
the same defect with the sign flipped, exactly as the review handoff warned, and it decides the
verdict below.

## Scope drift
None. `git diff --name-only 9d593e0a 0ee69c94` touches only the three named template files. Grepped
the diff for every hard no-go (`checklist_engine.py`, `run_crew.py`, `settings.json`, `docs/agents/*`,
any `skills/*/SKILL.md` or `skills/*/references/*`) and found none. `git log --oneline main..HEAD`
shows exactly one local, unpushed commit. The diff is 4 insertions / 4 deletions across 3 files with
only the targeted lines changed — consistent with a surgical raw-text edit, not a `json.load`/
`json.dump` round-trip. Re-validated all three edited files as valid JSON myself.

## Evidence verdict
Reproduced the full suite myself: `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR=
NO_COLOR=1 python -m pytest -q tests` → `2532 passed, 1 skipped, 1102 subtests passed in 104.68s`,
matching IMPLEMENTER_RESULT.md's claimed counts exactly. The before/after table, the shown-failing/
shown-passing demonstration for both converted checks, and the #562 fix + six-template sweep are all
present. I independently re-drove `ADMIRAL_SPINE.init.c1` through the real engine in a fresh git
worktree rather than trusting the transcript (see below), and it reproduced the claimed refuse-then-
pass sequence. Gap: the #562 fix's own demonstration only tests a scratch spine with hand-picked
`status=blocked`/`status=complete` values — it never stress-tests the fix against real historical
evidence shapes. That stress test is what I ran independently (119 real records, 24% match rate), and
it overturns the fix's soundness even though the narrower evidence the handoff explicitly asked for
was technically supplied.

## Code/doc quality
Checked against `docs/agents/CREW_CONTEXT.md`'s Verification Discipline section. "A check that cannot
fail is indistinguishable from one that passed" is satisfied — both converted checks are shown failing
then passing (I reproduced this for `ADMIRAL_SPINE.init.c1` myself in a worktree). "Assert against
behaviour, never text that describes it" is satisfied — both are command-exit/artifact-match checks.
But "Define a guard by its consumer's behaviour, not by a hand-maintained list" is violated:
`match={"status":"complete"}` was defined by analogy to a *different* evidence type's field name
(`review-result`'s `verdict`), not by consulting what the actual consumer — a Commander attaching
`implementer-result` evidence — actually computes. The implementer's own Assumptions section admits
this was inference. My sweep of 119 real records confirms the guess diverges from actual practice in
76% of cases. Ran the Fowler code-smell pass (`.agent-work/epic-559/b-instructions-to-checks/
FOWLER_PASS.json`, `verify_fowler_pass.py` exits 0): 10/12 baseline smells absent from a diff this
small; `duplicated-code` is present but overridden (three templates independently carry the same
"run init_work_area.py as a check" shape — no shared check-library exists across standalone JSON
templates, and matching that established convention is the task's own point); `primitive-obsession`
is flagged — the same root cause as above, restated as a design smell: a hand-typed string field with
no shared vocabulary or enforced contract across producers.

## Map impact verdict
- **Evidence supports claimed change:** Partially. The claimed behavior changes (two gate-close
  checks now refuse under stated conditions) are real and demonstrated for the narrow scratch-spine
  case, but the `g1-implement.c1` claim of "fixing" #562 does not hold against real-world evidence —
  see Handoff compliance and Blockers.
- **Constraints not violated:** Yes — all hard no-gos held (verified above).
- **Notes match the diff:** Yes. IMPLEMENTER_RESULT.md's Map Impact section correctly identifies this
  as a behavior change to two gate-close checks and correctly notes there is no `docs/architecture`
  map to reconcile against (verified: `docs/architecture` does not exist in this repo).
- **Decision candidates surfaced:** Yes — the implementer's Out-of-scope observations correctly
  surface that the `implementer-result` attach-fields convention is undocumented, and correctly
  declines to invent the fix outside its named scope.
- **Durable context routed:** Yes — routed to Workflow Feedback / Out-of-scope rather than fixed
  silently. I additionally routed a second, independently-found gap to triage (see Out-of-scope
  observations below).

## Reconciliation check
None. No `docs/architecture` map exists in this repo (`ls docs/architecture` → no such directory),
confirmed independently. Nothing to reconcile.

## Blockers
- **`EXECUTE_PLAN.g1-implement.c1`'s #562 fix blocks real Commander runs.** `match=
  {"status":"complete"}` requires exact-case `payload.status == "complete"`
  (`checklist_engine.py:853-855`, exact dict equality, confirmed by reading the source). Of 119 real
  `implementer-result` evidence records recorded across this repo's `.agent-work/` history (archived
  and live, 40+ distinct Commander runs, 2026-07-08 to 2026-08-10): 28 (24%) match exactly; 41 (the
  plurality, more common than "status") use a `verdict` field the check does not recognize at all;
  36 carry neither field; 11 use an unrelated schema (`gate_id`/`red_exit`/`green_exit`); a further 3
  carry `status` in the wrong case (`"COMPLETE"`). Representative payloads: `commander-424`
  (`status:"complete"` — passes), `commander-f2` (`verdict:"complete"` — fails), `r418-460` and
  `issue-467-trip-semantics` (neither field — fails), `issue-418-iterative-planning` (bespoke schema —
  fails). This is not a documentation gap ("nothing tells a Commander to attach `status`") — it is
  that real Commanders in this repo's own history have never converged on one field name, so the fix
  does not convert a check that cannot fail into one that reliably passes for legitimate completed
  work. It converts it into one that blocks the majority shape, including the single most common one.
  Every future Commander implement gate that follows the more common precedent, or any precedent
  other than the exact literal this fix hard-codes, is now permanently blocked at `g1-implement.c1` —
  reproducing #562's own defect with the sign flipped, at a blast radius that spans every Commander
  run in the repo. **Fix path:** either constrain the check to whatever field convention the repo
  actually documents and enforces (which does not yet exist — see Out-of-scope observations below),
  or revert to a presence-only check honestly matching the already-shipped `g1-review.c1` pattern
  until that convention is written down and enforced.

## Out-of-scope observations
- The `implementer-result` attach-fields convention this fix now depends on is undocumented anywhere
  a Commander could read it from (confirmed independently; same gap the implementer's own Out-of-scope
  section names). This is the root cause of the Blockers item above and belongs to whoever documents
  and enforces the convention repo-wide, not to a three-template edit.
- `REVIEW_SURVEY.template.json`'s `r6-fowler.c1` check command ships with a literal
  `<fowler-pass-record-path>` placeholder that `scripts/init_work_area.py::resolve_spine` cannot
  resolve — its token set is only `<work-id>`, `<role-skill-dir>`, `<role-session-id>`,
  `<repo-root>` (confirmed by reading `resolve_spine`'s source). The item's own imperative claims this
  placeholder resolves "exactly like `<work-id>`," but unlike `<work-id>` it has no automated resolver
  and must be hand-substituted by whoever instantiates the survey. I hit this live: my own
  `REVIEW_SURVEY.json` was instantiated with it unresolved, and I had to repair it myself via
  `amend --delta` (retext-check) mid-review, with no discoverable dispatching-Commander session
  anywhere in reach (this worktree, the main checkout, and every sibling worktree) to cite as the
  authority the repair path names. Filed as triage candidate `tc1` on this survey (out of this diff's
  3-file scope, but the exact "census that quietly miscounts" defect class this task exists to catch —
  CENSUS.md's row #21 calls this gate "already converted, no action" without catching that the check's
  command text is non-functional out of the box).

## Workflow Feedback
- **Handoff gaps:** None in REVIEW_HANDOFF.md itself — it correctly named the decisive question
  (r4a) and pre-supplied enough context to investigate it without further clarification. The gap I hit
  was upstream of the handoff, in how `REVIEW_SURVEY.json` was instantiated for me (see Context
  rediscovered).
- **Context rediscovered:** `r6-fowler.c1`'s check command carried an unresolved
  `<fowler-pass-record-path>` placeholder — the skill's own imperative describes a NORMAL PATH
  (resolve at instantiation) and a REPAIR PATH (`amend --delta`, authority = "the dispatching
  Commander named in your reviewer handoff"), but no Commander is named anywhere in REVIEW_HANDOFF.md
  or discoverable in any reachable `.agent-work/` tree for this specific gate — there is no
  Commander-level `execute.json`/`spine.json` wrapping `epic-559/b-instructions-to-checks` anywhere I
  could find. I used `--authority human` and logged why, since inventing a Commander session id would
  have violated the instruction more directly than an honest substitution. Recommend the reviewer
  skill's REPAIR PATH text name a fallback authority for exactly this case (no discoverable Commander),
  rather than only naming the ideal case.
- **Instructions improvised around:** `mcp__spine__spine_amend` and `mcp__spine__spine_capture` both
  required interactive tool-use permission I could not obtain in this non-interactive dispatch (the
  door returned "you haven't granted it yet" on every attempt, including retries). I fell back to the
  engine's CLI (`python scripts/checklist_engine.py --file "$SPINE_FILE" amend/flag-candidate ...`)
  for these two verbs only — all other verbs (`claim`, `start`, `record`, `consolidate`) worked
  through the MCP door without issue. Saying so here per the handoff's own instruction that a CLI
  fallback, named and justified, is evidence, not a mark against me.
- **What would have made this easier:** Documenting the `implementer-result` attach-fields convention
  (see Out-of-scope observations) before this task existed, so #562 would not have needed a guess by
  analogy in the first place. Separately, pre-resolving `REVIEW_SURVEY.json`'s `r6-fowler.c1`
  placeholder at instantiation time (as the NORMAL PATH already describes) would have saved a mid-review
  repair.

## Return status
`complete`
