# Admiral Log — `epic-568`

> Write per `constellation-how-to-talk` — clear, concise, grounded, one name per thing (`docs/agents/GLOSSARY.md`).

Contract: `.agent-work/epic-568/LATITUDE_CONTRACT.md` · Plan: `wave 1 = #315 alone (serialized engine-core lane); everything past wave 1 is forecast, not a queue — contract expires at wave 1 merge`

The run's audit trail, and the raw material the closeout episodes are written from. Append
entries **as they happen** — an unlogged ruling didn't happen. Own errors in the open: an
ADMIRAL ERROR entry that names the mistake and the fix is a closeout asset, not a liability.

Entry grammar (one line of date + tag, then the substance):

- `RULING` — an adjudication inside delegated latitude: what was decided, under which decision class, and why.
- `WAVE` — a wave launched: commanders, issues, worktrees, key launch-order terms (pre-rulings, fences, budgets).
- `INCIDENT` — a commander/crew death, stall, collision, or environmental kill: what died, autopsy, recovery action.
- `MERGE` — a PR merged: checks gated on exit code, diff verified in-fence, merge style and why.
- `ADMIRAL ERROR` — a mistake you own: what happened, cost, immediate fix, and what an episode would record about it.
- `CHECKPOINT` — a contract checkpoint reached: what was presented, what the human decided.
- `ESCALATION` — a surfaced or out-of-taxonomy decision sent to the human, and the answer.

## Rulings & events

- `2026-08-12` — `INCIDENT`: the `spine` MCP door is bound to a wave-1 scratch demo spine
  (`constellation-skills-wt/f-424/.../interactive-demo/spine.json`), not to this epic — the exact
  defect W2 in the post-418 handoff predicted. The `spine-epic` door is dead (connection closed).
  Recovery: drive this spine through the engine CLI with `--session-id admiral-epic-568` on every
  mutating call. Not routed around, recorded.
- `2026-08-12` — `WAVE`: work area `.agent-work/epic-568/` scaffolded from the admiral spine
  template; lease `admiral-epic-568` claimed active.
- `2026-08-12` — `CHECKPOINT`: latitude settled. Ran `constellation-interrogator` as a survey at
  `.agent-work/epic-568-latitude/interrogation.json` — ten questions, eight decisions taken to the
  human and two facts resolved from source, consolidated and lease released.
  `verify_interrogation.py` exit 0. Human sign-off: "Confirmed as written." Contract at
  `.agent-work/epic-568/LATITUDE_CONTRACT.md`, attached as evidence `e-latitude-1`.
- `2026-08-12` — `RULING`: **#315 is not the one-line fix the epic body calls it.**
  `checklist_engine.py:787` runs `subprocess.run([shell, "-c", command])` with no `cwd=` at all —
  the fail-open repro is confirmed, and the fix is one argument. But every relative check path in
  every shipped spine template currently resolves against the launcher's directory, so adding
  `cwd=` changes what all of them resolve against. Ruled under the epic-planning class: #315 is
  wave 1 **alone**, and its Commander must enumerate the blast radius by command and state the
  count. Confirmed by the human at the latitude gate.
- `2026-08-12` — `RULING`: **#552's denominator does not reconcile and the backfill needs it
  settled.** The issue says 43 active leases on disk. Scanning `git ls-files '*spine.json'` finds
  91 spines carrying an `engine_session`, 24 still `active` — matching the post-418 handoff's W7.
  Different denominators (on-disk vs tracked). Recorded as a pre-ruling graded `guess`, not
  settled; the settle experiment is to scan both sets once and state each count with its
  denominator before any backfill runs.
- `2026-08-12` — `ESCALATION`: the delegated merge authority granted at latitude would be vetoed
  by the harness classifier — `.claude/settings.local.json` allows only `Bash(gh issue *)` and two
  python one-liners. This is #408/#145, both members of this epic, landing on this epic's own
  Admiral before wave 1, and the post-418 run hit the same wall on `git branch -D` (handoff U3).
  Human ruled: pre-clear the merge path before wave 1, entries drafted and shown before written.
  **Resolved 2026-08-12** — human approved "merge path only, hygiene later". Seven entries written
  to `.claude/settings.local.json`: `gh pr create|view|list|checks|diff|merge` and `git push`, all
  in the canonical `Bash(cmd:*)` prefix form. JSON re-validated after the edit. Branch deletion and
  worktree management (`git branch -d|-D`, `git worktree add|remove|prune`) **deliberately not
  pre-cleared** — deferred to the closeout checkpoint when we know what actually needs deleting.
  Consequence accepted in advance: worktree provisioning for wave 1 and the closeout sweep will
  each hit the classifier, and each takes the recorded fallback (one live approval, remainder
  batched). The existing `Bash(gh issue *)` space-glob entry was left alone rather than silently
  rewritten to the canonical form.
- `2026-08-12` — `ESCALATION`: **I mis-read the deferral.** I recorded worktree management as
  deferred wholesale and planned wave 1 around a classifier prompt on `git worktree add`. The human
  corrected it: the objection was to **auto-deletes**, not to creation. Added
  `Bash(git worktree add:*)` and `Bash(git worktree list:*)` (the latter read-only, named explicitly
  rather than slipped in). `git worktree remove`, `git worktree prune`, `git branch -d` and
  `git branch -D` remain deliberately un-precleared and go to the closeout conversation. Cost: none
  — caught before dispatch. What an episode would record: an option label that bundles creation and
  deletion under one word ("hygiene") got read as one decision when the human was making two.

- TRANSITION | boundary=wave-1-launch | decision=advance | verified
- TRANSITION | boundary=wave-1-target-falsified | decision=repair | verified
- TRANSITION | boundary=wave-1-recut | decision=replan | verified
- `2026-08-12` — `INCIDENT`: **a live repro of #270 and #235, on this epic's own Admiral.** The
  `spine_rail` Stop hook fired at the wave-1 checkpoint and reported the run as abandoning an
  active gate — "you are in the MIDDLE of the spine... do not end your turn to wait." But the
  confirmed latitude contract says no wave is pre-cleared and the human clears each launch, so
  stopping there **is** the contract. The rail cannot tell a contract-mandated human checkpoint
  from an abandoned run, which is exactly what #270 files. Recovery: took the rail's own sanctioned
  exit and blocked the gate with `--authority human` rather than stopping silently. Worth carrying
  into WP3 planning as evidence measured in anger rather than reconstructed.
- `2026-08-12` — `RULING`: the issue-#315 claim of "five shipped relative checks" is **not** carried
  into the launch order as fact. A crude line-count over `.agent-work/templates/*.json` already hits
  nine template files, so five looks low — but a line count is not an enumeration, and both numbers
  are pasted into the order marked advisory-only with an explicit instruction not to inherit either.
  The Commander measures it. Ruled under fix-now triage / epic-planning; graded `guess` with the
  settle experiment named in the order.
- `2026-08-12` — `WAVE`: wave 1 prepared, **not launched** — awaiting the contract's human clearance.
  Launch order written to `.agent-work/epic-568/LAUNCH_ORDER-wave1-315.md`: one Commander,
  `commander-315`, Opus, serialized engine-core lane, issue #315 alone. Worktree
  `/home/tommy/projects/constellation-skills-wt/epic-568-315` on branch `epic-568/c1-check-cwd` off
  `3e4e07a3` — **not yet provisioned**, because `git worktree add` was deliberately left out of the
  pre-cleared allowlist and will take the recorded fallback (one live approval). Main verified clean
  and in sync with origin at `3e4e07a3`. Prelaunch gate green:
  `verify_iterative_role_artifacts.py admiral-prelaunch --work-id epic-568` exit 0.
- `2026-08-12` — `WAVE`: worktree provisioned.
  `git worktree add /home/tommy/projects/constellation-skills-wt/epic-568-315 -b epic-568/c1-check-cwd 3e4e07a3`
  exit 0; `git worktree list` shows exactly two entries, the main checkout and this one, both at
  `3e4e07a3`. `verify_worktree_isolation.py --here <wt>` exits 1 from the main checkout **as
  designed** — it passes only from inside the worktree, which is the Commander's first step, so the
  exit 1 here is the check working, not a failure. Launch order updated with the real provisioning
  evidence.
- `2026-08-12` — `INCIDENT`: `git worktree list` shows **no** `f-424` worktree, yet the `spine` MCP
  door served a gate from a path inside `constellation-skills-wt/f-424/`. The door is reading a
  spine file in a directory git no longer tracks as a worktree. Recorded, not chased — it sits next
  to the unvalidated-path gap filed in #441 and may be evidence for it.
- `2026-08-12` — `CHECKPOINT`: human gave explicit go on the wave-1 dispatch. The permission
  correction and the launch clearance were asked separately on purpose — the contract makes each
  launch the human's call, and a cleared obstacle is not a cleared launch.
- `2026-08-12` — `WAVE`: **wave 1 launched.** One Commander, `commander-315`, Opus tier, dispatched
  synchronously into `/home/tommy/projects/constellation-skills-wt/epic-568-315` on branch
  `epic-568/c1-check-cwd` off `3e4e07a3`, carrying
  `.agent-work/epic-568/LAUNCH_ORDER-wave1-315.md`. Issue #315 alone; serialized engine-core lane,
  no other Commander touching `checklist_engine.py`. Key launch-order terms: repro before and after
  is the acceptance evidence; the blast radius is enumerated **by command** with the count stated;
  the issue's "five relative checks" is marked an inherited claim to re-measure, not a fact;
  `spine_rail.py` and `agent_work_root.py` are out of bounds and must be floated; the honest-null
  clause is explicit. Dispatched synchronously rather than detached so the wait happens inside the
  turn — the wait-by-ending-turn failure is what kills a headless Admiral.
- `2026-08-12` — `ADMIRAL ERROR`: **I nearly gated a merge on the exit code of `tail`.** I ran
  `gh pr checks 576 2>&1 | tail -10; echo "CHECKS_EXIT=$?"` and read `CHECKS_EXIT=0` as a green
  gate. `$?` after a pipeline is the *last* command's status, so that 0 was `tail` succeeding.
  Re-run without the pipe: `gh pr checks 576` exits **8** — checks pending. Cost: none, caught
  before any merge. This is the merge-gating invariant ("gate on the check exit code") defeated by
  shell mechanics rather than by ignoring the rule, and it is a check that cannot fail — the
  piped form returns 0 in the healthy and the broken world alike. What an episode would record:
  the invariant says "gate on the exit code" and does not say "a pipe replaces the exit code you
  meant to read."
- `2026-08-12` — `INCIDENT`: my first re-run of the Commander's `enumerate_checks.py` returned
  "TOTAL command checks: 0" and I briefly read it as contradicting the Commander. The script takes
  its input files as argv; I invoked it bare. My error, and the same family as the one above — an
  under-inclusive enumeration reporting clean. Re-run with the file globs it reproduces the
  Commander's table cell for cell.
- `2026-08-12` — `RULING`: **wave-1 evidence verified at source, not accepted on the return.**
  Independently confirmed, in this order: (1) `verify_worktree_isolation.py:100-123` — `_git()`
  calls `subprocess.run(["git", *args])` with no `cwd=`, so `current_toplevel()` measures the
  ambient cwd as the check's *subject*; forcing `cwd=<repo-root>` would make the comparison
  `X == X`, converting a live gate into a tautology. The Commander's central claim holds.
  (2) `git diff main...HEAD -- scripts/ skills/` is empty — no production code, neither forbidden
  file touched, so the serialized-lane constraint was honored. (3) Re-ran `enumerate_checks.py`
  over both corpora: 22 checks / 6 literal-relative / 11 cwd-defaulting = **17 cwd-dependent**, and
  21 / 5 / 10 = 15. Matches the Commander's table exactly. The filed claim of "five" measures
  **17**. (4) The independent review is a genuine reproduction, not a restatement — the reviewer
  rebuilt the red-first proof itself and quotes line numbers it read. Verdict APPROVE.
- `2026-08-12` — `ESCALATION`: the Commander returned **blocked on a decision outside its latitude**,
  correctly. Its three options — engine exports the launcher cwd plus a `--from` flag on the
  isolation checker; a schema flag exempting environment-observing checks; or close #315 as
  measured-not-worth-it — are all **architecture/structural**, and its "wave 1 should split"
  proposal is a **scope change**. Both classes are `surfaced` under the latitude contract, so this
  is not mine to rule. Taking it to the human.
- `2026-08-12` — `ESCALATION`: **the contract's merge gate is unsatisfiable, a second escalation
  independent of the first.** The contract delegates merge to me on "a green check exit code plus an
  independent reviewer APPROVE". The APPROVE exists and is genuine. Green does not and cannot:
  `gh pr checks 576` exits 1, and the last **five** runs on `main` all failed — including
  `3e4e07a3`, this PR's own base. This is the pre-existing Windows CI breakage recorded as handoff
  W8 ("Windows CI red since 08-11, deferred by your decision"); the #555 fix exists unmerged on
  `fix/mcp-door-launchable`. Measured the regression question exactly rather than assuming: main's
  failure set and the PR's are **identical** — 76 each, `comm` shows zero present in the PR and
  absent from main, and zero fixed — while the PR adds two passing tests (2854 → 2856), the new
  guard file. So the change introduces no regression, but the delegated condition's literal text
  cannot be met by any PR in this repo today. A delegation whose precondition is unsatisfiable is
  not a delegation, so this goes to the human rather than being quietly reinterpreted by me as
  "green enough".
- `2026-08-12` — `RULING`: no replan transition authored yet. The execute directive gates a
  transition on the **next launch**, and no launch is pending — this run is escalating, not
  dispatching. Authoring an `advance` or `replan` exit now would encode a decision that belongs to
  the human under two surfaced classes. The transition gets written once the human rules, carrying
  their ruling.
- `2026-08-12` — `CHECKPOINT`: **the human rejected all three Commander options and supplied a
  fourth, which the evidence supports better than any of them.** Their framing: this is a spine-init
  discipline problem, not an engine-argument problem — when a spine is created, make the worktree
  and initialize the spine inside it, and record the repo reference *in the spine itself* rather
  than passing it to the engine. Measured against source before accepting it, and it holds:
  * `scripts/spine_lifecycle.py:83` `build_origin()` already returns exactly that block —
    `{work_id, branch, worktree, base, opened_at, opened_by, parent}` — and `worktree` is the local
    reference the checks need.
  * `open_work()` already does the whole disciplined sequence in one call: worktree, branch, work
    area, compiled spine, `origin` stamped, isolation self-verified, with rollback after
    `git worktree add`.
  * `init_work_area.py:148` already computes `Path(root).resolve()`, uses it for string
    substitution, and **discards it**. Every ingredient exists at init.
  * And it is unused: **0 of 107 tracked `spine.json` files carry an `origin` block**, and the
    engine never reads one — the only `origin` in `checklist_engine.py` is the git ref
    `origin/main`.
  Cause located: two init paths exist. The disciplined one is reachable only through the
  `spine_open` MCP door, which is **dead in this session** (`MCP error -32000`). The undisciplined
  one — `init_work_area.py` plus a hand-run `git worktree add` — is one command and always works.
- `2026-08-12` — `ADMIRAL ERROR`: **I used the undisciplined path myself, for this very epic, an
  hour before diagnosing it.** I scaffolded `.agent-work/epic-568/` with `init_work_area.py` and ran
  `git worktree add` by hand for wave 1, so this epic's own spine carries no `origin` — it is one of
  the 107. I did not notice that the dead `spine-epic` door had silently demoted me from a
  disciplined path to a different one; I read it as a tool being unavailable rather than a workflow
  being unavailable. Cost: none directly, and it produced the clearest possible evidence for the
  human's diagnosis. What an episode would record: a broken door does not announce that the path
  behind it was the one with the discipline in it.
- `2026-08-12` — `RULING`: **direction set to the human's framing; wave 1 held for repair.** Options
  A (engine exports launcher cwd) and B (schema exemption flag) are rejected — A makes the engine
  reconstruct a value that is known at init, B distributes an exemption to every future check
  author. The `origin`-block framing writes the fact once, where it is already computed, into a
  field that already exists. Encoded as a `material_exception` transition with decision `repair`:
  the current wave's target is falsified, the forecast is held, and `launch_id` is null so no next
  wave can launch until the costing settles. `commander-315` continued in place — a query
  round-trip, not a relaunch: it returned with context intact, so it is answered and continued, not
  cold-started.
- `2026-08-12` — `ADMIRAL ERROR`: I first authored the repair transition with a **re-cut** wave and a
  revised forecast. The G2 verifier refused it — "repair must hold the current wave exactly" — and
  the refusal was right. A `repair` holds the wave and forecast unchanged while blocking evidence is
  settled; re-cutting them is a `replan`, and a replan needs the costing I do not have yet. Fixed by
  holding both exactly against `current_plan`. Worth recording because the instinct to encode the
  new direction immediately would have written a plan change the evidence does not yet support.
- `2026-08-12` — `TRIAGE`: **doctrine and code disagree on what a `repair` exit produces, and the
  disagreement is invisible until you author one.** `constellation-admiral/SKILL.md:63` says the
  prelaunch check "requires exactly one matching `advance`, `repair`, `replan`, or `stop` exit and
  writes `CURRENT_TRUTH.md` plus `WAVE_REVIEW.md` from the verified result". The script disagrees:
  `verify_iterative_role_artifacts.py:237-259` `_require_launch_authorization` documents that
  "`repair` stays refused -- that one is a real authorization question", and the render call sits at
  lines 298-299, **after** that refusal. So a `repair` can never reach the renderer. Confirmed
  empirically: this boundary's directory holds only the two JSON packets — no `CURRENT_TRUTH.md`,
  no `WAVE_REVIEW.md`. The refusal itself is correct behavior for a launch gate. The gap is that a
  repair is doctrinally a first-class exit that renders planning truth, and mechanically it renders
  nothing and exits nonzero, which reads to an author as a broken transition rather than a working
  refusal. Filed as a triage candidate, not fixed here — it is outside wave 1's issue.
- `2026-08-12` — `RULING`: **the costing landed and it caught a trap in the direction itself.
  Verified by re-running the Commander's demonstration, not accepted on the claim.** Cut naively —
  "store the repo root in the spine, then pass it to the check as `cwd`" — the human's direction
  **is the falsified fix wearing a new hat**. `origin.worktree` and the EXPECTED value inside the
  isolation check are **byte-identical**, because both derive from the same resolved root at
  creation. Reproduced live via `d_trap_demo.sh`: with the launcher standing in the wrong worktree,
  `cwd = launcher's own` REFUSES (the gate works) and `cwd = origin.worktree` PASSES (the gate is
  disarmed). Same defect, new spelling.
  The Commander's resolution is stronger than either: with `origin.worktree` stored, the engine
  compares its **own** `Path.cwd()` against it **natively at verb entry**, so the isolation check
  stops being a subprocess command at all and `init.c0`'s command check is **deleted** rather than
  repaired. No schema flag, no env var, no `--from`. Undisarmable by a child process's cwd, and it
  runs on every verb rather than only where someone wired a check.
- `2026-08-12` — `RULING`: **the write side and the read side must land in one change.** The
  costing's sequencing risk is real: an engine that reads `origin.worktree` must fall back to the
  inherited cwd for spines that lack it (refusing breaks 12 role templates on day one, and deriving
  a root from `base_dir` reintroduces the defect), which makes the fix **inert until spines actually
  carry `origin`**. So the ~8-line write side in `init_work_area.py` is not a convenience — it is
  what makes the engine change do anything. Cutting them apart ships a no-op and a false green.
  PR #576's landed guard is what catches exactly that half-built shape.
- `2026-08-12` — `RULING`: **the dead `spine_open` door does not gate this work, and I was wrong to
  imply it might.** The Commander measured what I had assumed: `open_work()` requires a compiled
  spec, and only 2 specs exist against 12 role templates, so routing roles through it is a ~10-spec
  migration. Stamping `origin` in `init_work_area.py` reaches all 12 with no door and no spec. The
  door is worth fixing on its own merits and is not a prerequisite. My earlier framing — that the
  disciplined path is unreachable *because* the door is dead — was half right: the door is dead, but
  it was never the only barrier, and naming it as the blocker would have gated 40 lines behind a
  migration.
- `2026-08-12` — `RULING`: the spine count reconciles. I measured 107, the Commander 108. Both are
  correct against different trees: `git ls-files '*spine.json'` returns 107 on `main` and 108 on
  `epic-568/c1-check-cwd`, which added the Commander's own spine. A live instance of the
  pin-a-claim-to-its-revision rule — neither number is wrong, and neither is meaningful unbound.
  Of the 108, **106 are archived dead runs; the live backfill population is 2**.
- `2026-08-12` — `CHECKPOINT`: human confirmed the re-cut and **amended the merge gate**: *"okay with
  the independent red, we should be green except for the existing reds."* The contract's merge term
  is now **no new failures against the `main` baseline** plus an independent reviewer APPROVE,
  applied as a set difference that must be empty — not a judgment that the checks look close enough.
  Written into `LATITUDE_CONTRACT.md` rather than held in my head, with the note that it lapses when
  `main` goes green. Attached as evidence `e-execute-2`. Also recorded there: merging PR #576 does
  **not** trip the contract expiry, because it carries the guard and not the fix; wave 1 closes when
  the re-cut lands.
- `2026-08-12` — `ADMIRAL ERROR`: I authored the re-cut by **rewriting the launched issue #315 in
  place**, and the G2 verifier refused it — "applicable result must preserve launched open issue
  '315'". The refusal was right and the rule is a good one: you do not re-scope what you launched,
  because that rewrites history the launch already committed to. Corrected to the honest encoding —
  the launched item **completed** with a measured negative plus a merged guard (which the contract
  explicitly calls a complete, successful deliverable), and the re-cut is a **new** plan item,
  `315-native`, superseding it. The GitHub issue #315 stays open until that lands. Second refusal in
  the same authoring pass: I classified the amended merge gate as `blocks_current_wave_exit` while
  dispositioning it `record_evidence_only`; the human's amendment resolved it, so the classification
  became `evidence_only`. Both refusals were the engine teaching correct semantics, not obstacles.
- `2026-08-13` — `WAVE`: **wave 1 re-cut prepared, not launched** — awaiting the contract's
  stop-and-present clearance. Transition `wave-1-recut`, decision `replan`, verifier exit 0,
  `CURRENT_TRUTH.md` and `WAVE_REVIEW.md` rendered. Launch order at
  `.agent-work/epic-568/LAUNCH_ORDER-wave1-recut.md`. Fresh worktree
  `/home/tommy/projects/constellation-skills-wt/epic-568-315-native` on branch
  `epic-568/c2-native-isolation` off **`9bb8c1b6`**, which already carries the merged guard —
  deliberately **not** the prior Commander's worktree, which stays intact for harvest at closeout.
  Key launch-order terms: the trap demonstration is pasted verbatim so the new Commander cannot walk
  into it; both halves land as one change (a no-go, not a preference); `init.c0`'s command check is
  deleted, not repaired; the root must be a parameter distinct from `base_dir`; the merged guard is
  named as the wave's own tripwire against a half-build.
- `2026-08-13` — `CHECKPOINT`: human cleared the re-cut launch.
- `2026-08-13` — `WAVE`: **wave 1 re-cut launched.** `commander-315-native`, Opus, dispatched
  synchronously into `/home/tommy/projects/constellation-skills-wt/epic-568-315-native` on branch
  `epic-568/c2-native-isolation` off `9bb8c1b6`, carrying
  `.agent-work/epic-568/LAUNCH_ORDER-wave1-recut.md`. Plan item `315-native`, superseding the
  falsified target of #315. Serialized engine-core lane: no other Commander touching
  `checklist_engine.py`. Dispatched synchronously so the wait happens inside the turn.
- `2026-08-13` — `CHECKPOINT`: human went AFK granting wider latitude — *"you can keep pushing
  through wave 1. you may follow reasonably sized judgement calls. try to get through this."*
  Recorded in `LATITUDE_CONTRACT.md` with an explicit boundary: bounded structural changes serving
  an already-ruled direction are now mine; direction, intent, scope and production defaults are
  still not. The wave-boundary checkpoint still stands.
- `2026-08-13` — `INCIDENT`: `commander-315-native` **tripped the context governor's HARD gate at
  `start execute`** and reached up rather than pushing through. Not a stall and not a death: the
  `refresh-request` is filed on its own spine, the lease is **held**, and `current` carries both the
  `DIGEST:` and `REFRESH REQUESTED: execute (why_ref w-4)`. Reading at the trip was **23.8%** against
  an 80K soft / 150K hard band on a 1M window, with `execute` reserving 30000 tokens of headroom. It
  checked the old "reads ~5x high" defect (#252) and confirmed it fixed, so the reading is real. Zero
  source files changed; no PR, deliberately — a PR carrying only planning artifacts, for a change
  whose central ruling is "both halves land as ONE change", would be noise. Recovery is a **refresh
  relaunch**, the third shape: a fresh Commander into the **same worktree and the same spine file**,
  cold-started from `current` alone. Not a query round-trip, not the dead-agent drill.
- `2026-08-13` — `INCIDENT`: a live repro of member issue **#510** sits in that trip's own advisory.
  It instructs `advance execute --why "<understanding>"`, but `execute` is `pending` with unmet
  postconditions, so the engine refuses that verb — the advisory prescribes the one verb that cannot
  run. #510 is filed as exactly this and is in the deferred set; recorded as evidence measured in
  anger, not chased.
- `2026-08-13` — `RULING` (float 1, under the widened latitude): **authorize the four-file deletion
  of `init.c0` and its coverage apparatus.** The Commander measured that deleting the check alone
  takes `verify_worktree_precondition_coverage.py` and three enumeration tests from 7 passed to
  `3 failed, 4 passed`, because that script exists to assert the very wiring being removed. The
  pre-ruling `decision:delete-not-repair-init-c0` is graded `settled/measured`, and the doctrine for
  that tier is re-measure and revisit on contradicting evidence — this is that measurement, so
  revisiting is inside the grade's own rules rather than an override. Ruling: delete coherently.
  Once enforcement is engine-native, *per-template coverage of a command check* is the wrong
  question, so the script and its three tests retire with it. The alternative — keep `init.c0` — 
  ships a check that cannot fail, for the isolation reason specifically, into every Commander spine
  minted from the template. That is the exact defect class this epic exists to remove, and shipping
  it knowingly to avoid a four-file diff would be indefensible.
- `2026-08-13` — `ADMIRAL ERROR`: **my launch order overclaimed the change's property, and a
  reviewer working from my frame would have certified something the change does not deliver.** I
  wrote that an engine-native comparison "cannot be lied to by a child process's cwd". The Commander
  falsified it: `_run_check_command` passes no `cwd=` at all, so `--here` already reads the engine's
  own ambient cwd, and the native comparison reads the same value one indirection earlier. A check
  authored as `cd <origin.worktree> && ...` still satisfies it while the work happens elsewhere. The
  change remains worth making, for **coverage, unbypassability from the spine, and an independent
  expected side** — not for non-forwardability. Launch order corrected before relaunch.
- `2026-08-13` — `ADMIRAL ERROR`: **I named the merged guard as the wave's tripwire and it is not.**
  I told the Commander that a green `tests/test_worktree_precondition_wiring.py` proves both halves
  landed. It does not: every fixture in it builds an origin-less spine by hand, so it is green **by
  construction** and blind to the stamped path entirely. It is evidence for the fallback branch
  only. Consequence: the wave needs a **new** test that actually exercises a spine carrying `origin`,
  and I have added it as an exit criterion rather than leaving the gap papered over by a guard that
  cannot see it. This is the check-that-cannot-fail family again, authored by me, in the very wave
  convened to remove one.
- `2026-08-13` — `ADMIRAL ERROR`: my launch order asserted "the wired hooks call the engine you are
  changing" and instructed fresh-process validation on that basis. False. `spine_rail.py`'s own
  docstring says do **not** subprocess the engine and it keeps that promise — it reconstructs
  `current` in-process and its one subprocess is `git worktree list`; `gauge_writer_hook.py` never
  calls the engine. The real cross-tree caller is `mcp_spine_server.py:361`, which calls
  `checklist_engine.main()` in-process and never chdirs. Corrected in the order; the validation
  instruction had no subject and would have cost the next Commander real effort.
- `2026-08-13` — `WAVE`: refresh relaunch delivered. Fresh `commander-315-native` cold-started from
  `current` alone into the **same** spine and worktree, re-claimed the same session id, and
  implemented. **PR #577 open**, `a04d7828`+`ed25bf8f`+`890ff76f` on `epic-568/c2-native-isolation`.
  Production diff is 8 files: `checklist_engine.py` +98, `init_work_area.py` +23,
  `verify_worktree_precondition_coverage.py` **deleted** (-146), `docs/CHECKLIST_SCHEMA.md` +30, and
  four test files including a new `tests/test_spine_origin_isolation.py` (+513, 31 tests).
- `2026-08-13` — `RULING`: **two claims I distrusted on sight both check out.** Verified at source
  rather than accepted.
  (a) *"`init.c0` deleted"* looked false — `.agent-work/templates/COMMANDER_SPINE.template.json`
  still carries the isolation precondition and the diff does not touch it. It is **not** false: the
  check is gone from the **canonical** source, `skills/commander/templates/`. The copies that still
  carry it are `.agent-work/templates/` and its `.baseline/`, which `install_constellation.py`
  regenerates — the same canonical-vs-install-copy distinction this skill's own doctrine names for
  `global-*.md`. The Commander edited the right file. **Consequence to carry forward:** until an
  install runs, agents instantiating from `.agent-work/templates/` still get the old `init.c0`, so
  the deletion is not live in this checkout. Flagged, not a defect in the change.
  (b) *The merged guard shrank* 305→239 lines and 5→3 tests, and I had told the Commander not to
  weaken it. Diffing the test names shows it was **refocused, not weakened**: the four removed tests
  (`test_failure_output_states_enumerated_count`,
  `test_passes_once_new_entry_carries_the_precondition`,
  `test_refuses_new_second_entry_without_naming_known_fixed_entry`,
  `test_refuses_broken_copy_and_passes_real_fixed_tree`) all tested the **coverage script that was
  authorized for deletion**. The two replacing them —
  `test_gate_passes_launcher_standing_in_the_worktree` and
  `test_gate_refuses_launcher_standing_in_the_main_checkout` — test the **behaviour**. That is a
  strengthening, and it is the "assert against the behaviour, never against text describing the
  behaviour" rule applied correctly.
- `2026-08-13` — `RULING`: **PR #577 is NOT merged, and the gate is why.** The amended merge gate is
  an **empty** failure-set difference against the `main` baseline. The measured difference is
  `{tests/test_mcp_lifecycle.py}` — one new failure, not zero. The gate says refuse, so I refuse.
  This is deliberately not a judgment that one failure is close enough: I wrote the gate as a set
  difference precisely so it could not be softened in the moment, and softening it the first time it
  bites would make it decoration.
- `2026-08-13` — `ESCALATION`: **the float exceeds even the widened latitude — parked for the human.**
  The failing test is the collision itself, and it is real: `spine_open` creates a **new** worktree
  and stamps `origin.worktree` to it, then the next verb `claim` runs in-process via
  `mcp_spine_server.py:361`, which never chdirs. The process cannot already be standing in a
  directory that did not exist a moment earlier, so **`spine_open` → `claim` in one session is
  impossible through the door, by construction.** The Commander rejected two cheaper fixes on
  measurement — narrowing verb scope fails because the round trip drives `start`/`attach`/`advance`,
  all mutating; and having the door supply `SPINE.parent`'s toplevel measures **equal** to
  `origin.worktree` by construction, which is the `X == X` trap again. Every remaining fix changes
  **who sets cwd**, in `run_crew.py` or `mcp_spine_server.py`. Both are production behaviour of
  shipped modules, which my own widened-latitude note explicitly excludes. Commander recommends
  options 1+2 (crew launcher passes `cwd=`; the door chdirs around its in-process call). I agree
  with that recommendation and am not acting on it.
  It also falsified another frozen claim of its own in the process: `run_crew.launch_process`
  (`run_crew.py:676`) passes **no `cwd=`**, so a crew inherits the *dispatcher's* cwd.
- `2026-08-13` — `CHECKPOINT`: human ruled **options 1 + 2** on the collision — `run_crew.launch_process`
  passes `cwd=<the spine's worktree>`, and the MCP door `chdir`s around its in-process
  `checklist_engine.main()` call — and granted **reinstall at my discretion**. Attached as evidence
  `e-execute-3`. Neither module is on the forbidden list (`spine_rail.py`, `agent_work_root.py`), so
  the Commander may take both. Human AFK again.
- `2026-08-13` — `RULING`: continuing `commander-315-native` rather than relaunching fresh. It
  returned on a **float**, not a trip, with its lease held and its context intact, so this is the
  answer-and-continue round trip. Accepted risk: it is at ~185k tokens and the earlier hard trip
  fired at ~238k, so it may trip mid-implementation. That is a governed outcome with a known
  recovery — refresh-relaunch a fresh agent from `current` — and it cost nothing last time, whereas
  cold-starting a fresh agent now would discard a working understanding of a change it just wrote.
- `2026-08-13` — `RULING`: I will run the reinstall the human authorized **only after** #577 merges,
  not before. `.agent-work/templates/` is the install-generated copy, so regenerating it before the
  canonical deletion is on `main` would either be a no-op or would stamp a half-state into the tree
  the wave is still measuring against.
- `2026-08-13` — `RULING`: ratified the Commander's MCP-only `retext-check` amendment to
  `g1-integrate.c1`: run the full suite as `env -u SPINE_FILE -u SPINE_ENGINE -u SPINE_SESSION
  python -m pytest tests/ -q -p no:randomly`. Exact reproduction under the MCP-bound environment was
  **1 failed, 2980 passed** at
  `tests/test_mcp_identity.py::DC3InheritanceMechanismTests::test_launching_the_parent_never_touches_the_calling_processs_own_environ`;
  the identical command with those three ambient door bindings cleared was **2981 passed**. This is a
  correction to the gate's test environment, not a waiver and not production rework: the test explicitly
  asserts that a caller's own environment starts clean, while an engine-owned command launched by the MCP
  door necessarily inherits the door's identity bindings unless the check clears them. The amendment
  preserves the full-suite intent and stays inside the human's widened latitude for bounded structural
  changes serving the already-ruled direction.
- `2026-08-13` — `RULING`: authorized `commander-315-native` to push exactly
  `epic-568/c2-native-isolation` at local completion commit `48f07123` to update the already-open PR
  **#577** and satisfy its archive gate. This is not new publication latitude: the live Admiral
  `STATE_NOTE.md` explicitly records `git push` as cleared for wave 1. No merge authority is added by
  this ruling; merge remains Admiral-gated on the amended empty failure-set difference and verified
  review evidence.
- `2026-08-13` — `INCIDENT`: the scoped push of `epic-568/c2-native-isolation` to update
  existing PR **#577** was refused by the harness approval layer because it requires direct user
  approval; the Admiral's recorded delegation was not accepted as sufficient. No workaround was
  attempted. The Commander recorded an MCP block with authority `human` and moved its bound job file
  to `.agent-work/archive/2026-08-13-commander-315-native/spine.json`. Substantive completion commit
  `48f07123` and archive/episode commit `6f7bbf56` are local and the branch is two commits ahead of
  origin; only push, final archive advance, and lease release remain. No merge was attempted.
- `2026-08-13` — `MERGE-GATE`: after the human directly approved the exact operation, the Admiral
  root pushed `epic-568/c2-native-isolation` to origin, advancing PR **#577** from `890ff76f` to
  `d564d575`. GitHub reports the PR **OPEN**, mergeable, and not merged; its `test` check is pending.
  This entry records a branch push only — no merge was attempted or authorized.
- `2026-08-13` — `WAVE`: `commander-315-native` reached terminal archive through MCP after the
  remote update was verified. Archive conditions **6/6** passed; final MCP `advance` returned
  `archive -> complete`, and the immediately following final journaled action released lease
  `commander-315-native`. Local and remote branch parity is 0/0 at `d564d575`. Seven episodes were
  captured and tracked. Expected residual worktree changes are confined to the archived
  `spine.json` and journal entries recording the final resume, attestations, advance, and release.
- `2026-08-13` — `MERGE-GATE`: PR **#577** GitHub `test` check completed **FAIL** after
  11m02s (Actions run `31767606605`, job `94666577724`). The human's conditional authority was to
  merge and push only if the check/failure-set gate passed; that condition did not occur. PR remains
  OPEN, mergeable, and not merged at `d564d575`. No merge or further push was attempted.
- `2026-08-14` — `CHECKPOINT`: exact pytest-node set comparison against current `main` at
  `9bb8c1b6` / Actions run `31666537556`: PR #577 has **85** unique failing nodes, of which **76
  are identical to main** and **9 are new**. The nine are confined to the Windows job: eight new
  `tests/test_crew_worktree_cwd.py` nodes (seven cascading through the same pre-existing Windows
  hook/interpreter refusal, one Windows path-string assertion) plus Windows-only code-map rebuild
  drift. No baseline failure disappeared. Linux engine-owned and independent-review suites remain
  green at **2,981 passed, 6 skipped**.
- `2026-08-14` — `RULING` (human): *"not worried about windows failures right now"*. Applied as
  an explicit Windows-only exception to the amended empty-difference merge gate for PR #577. It
  does not waive Linux failures, review, head-SHA pinning, or verified-merged evidence. Merge is
  authorized against exact head `d564d575`; branch deletion is not authorized.
- `2026-08-14` — `MERGE`: PR **#577** squash-merged with exact expected head
  `d564d5751c802daac4a795000e0101886a3bb75c`; GitHub returned merged commit
  `0dd6a6eb54f9493149bb5f36337853426f17eab1`. Connector state independently reported the PR
  merged, `origin/main` advanced to that commit, and local `main` fast-forwarded normally. No
  branch deletion was attempted.
- `2026-08-14` — `ADMIRAL ERROR`: the first post-promotion Linux suite on merged `main` was not
  green: **1 failed, 2,979 passed, 7 skipped, 1,130 subtests**. The sole failure was
  `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`.
  A fresh map saw 80 test modules / 4,543 entities while the committed root index named 78 / 4,500.
  This was not covered by the human's Windows exception and therefore was not waived.
- `2026-08-14` — `RULING`: repaired the post-promotion generated-artifact defect in the same wave,
  on dedicated branch `epic-568/wave1-map-refresh`. Regeneration changed only `map/INDEX.md`
  (4 additions, 2 removals). Focused freshness tests passed 2/2 and the exact full Linux suite
  passed **2,980 passed, 7 skipped, 1,130 subtests**.
- `2026-08-14` — `MERGE-GATE`: PR **#578** at exact head
  `a9e3adc0adb89e0d812e7e9ee196b474e319ab79` had **84** unique Windows failures against **85**
  on exact merged-main baseline `0dd6a6eb` / run `31810185629`: zero added and exactly the stale
  code-map failure removed. This satisfies the human's Windows-only exception while improving the
  failure set.
- `2026-08-14` — `MERGE`: PR **#578** squash-merged with the expected-head pin; GitHub returned
  `0448275ef08993967674cca0807457de15e8c299`. `origin/main` and local `main` were both verified at
  that SHA. Wave 1 is now promoted with its generated map current.
- `2026-08-14` — `CHECKPOINT`: the latitude contract explicitly expires at the wave-1 merge.
  No later issue is authorized for launch. The `wave-1-merged` transition stops and surfaces a
  contract-refresh decision to the human.
- TRANSITION | boundary=wave-1-merged | decision=stop | verified
- `2026-08-14` — `CHECKPOINT` (human contract refresh): cleared all retained wave-2 lanes:
  lease lifecycle, #441, #530, #510, and a bounded model-tier propagation addition for Codex
  dispatch. Required provable before/after outcomes and CI green except Windows, whose failures may
  remain. Lifecycle must float if measurement reveals material complexity. Model/spend routing is
  delegated: Sol for high-risk engine work/review, Terra for bounded implementation, Luna for
  mechanical measurement and verification; lower tiers do not adjudicate architecture.
- TRANSITION | boundary=wave-2-contract-refresh | decision=advance | verified
- `2026-08-14` — `WAVE-LAUNCH`: started three read-only wave-2 scouts with no engine-core
  implementation authority: `lifecycle_measure` on Sol/high, `spine_rail_measure` on Terra/medium,
  and `codex_tier_measure` on Luna/medium. The first measures the mandatory lifecycle float; the
  second jointly measures #441/#530 but may not implement either; the third costs the bounded
  harness addition. #510 is authorized and takes the next available slot. All were explicitly
  forbidden from engine CLI use and state mutation.
- `2026-08-14` — `INCIDENT`: the MCP `spine_open` lifecycle correctly created the Codex tier
  worktree under the repository's sibling `constellation-skills-wt/` convention, but Codex
  subagents are writable only under the primary workspace root. The Terra implementer could read
  and claim through MCP but could not patch. It released the lease without edits. The worktree was
  moved under repo-local `.worktrees/` as a reversible probe; that exposes a second seam:
  `origin.worktree` is intentionally immutable engine identity and now names the old location.
  No hand-edit or engine CLI workaround was attempted. This is evidence that Codex worktree
  placement must become configurable/compatible, not merely model metadata.
- `2026-08-14` — `RULING`: #510 is BOUNDED and its filed runtime premise is obsolete. The legal
  path already exists: attach refresh-request, start under the existing HARD release, then
  `advance --why`. The remaining defect is status-blind advisory text; no new verb/default/state
  change is needed.
- `2026-08-14` — `RULING`: #530 is BOUNDED and precedes #441 in the shared `spine_rail.py`
  queue. Derive stored worktree from the already-resolved spine path and prove parent/child Stop
  behavior in a real linked worktree. #441's transaction mechanics are clear, but active-binding
  reaper retention remains coupled to lifecycle policy and is held.
- `2026-08-14` — `FLOAT`: lifecycle crossed the human-defined complexity boundary. Current-main
  named-spine census is 109 tracked / 93 with session / 25 active, versus 101 on disk / 94 with
  session / 26 active. All 25 tracked active named spines are archived; 20 are nonterminal.
  Automatic release conflicts with explicit release-is-last semantics, and bulk cleanup cannot
  infer that archived nonterminal work is completed. Admiral `execute` was blocked through MCP;
  no engine-core implementation started.
- `2026-08-14` — `RULING` (human): approved the lifecycle package as proposed. Explicit release
  remains mandatory and becomes idempotent/journaled; no historical bulk mutation; child
  references become contained relative paths with legacy compatibility; archive refuses a
  resolvable nonterminal child. #383 remainder moves under #441, #208 moves to harvest
  completeness, and liveness/actor/durable-root work is deferred to high-risk waves. Immediate
  implementation resumes only for #530, #510, and Codex tier/worktree routing; #441 follows #530.
- TRANSITION | boundary=wave-2-lifecycle-ruling | decision=replan | verified
- `2026-08-14` — `INCIDENT` (owned): **the prior Admiral session died at heartbeat `16:03Z`, before
  the wave-2 Commanders it had launched reported back.** Restart at `19:54Z` found four idle
  worktrees, no live process, and the epic lease still held. Wave 2 had in fact run: #510, #530, and
  Codex tier each reached 9/10 steps with an independent reviewer APPROVE and parked at `archive`;
  #441 blocked at `execute`. No adjudication had happened in the ~3h gap. State note rewritten to
  ground truth before resuming the gate.
- `2026-08-14` — `RULING` (mine, delegated class `merge-to-main`): **the three parked lanes were
  never a human escalation and I mis-routed them as one.** All three name
  `authority_needed: Admiral` because their frozen LAUNCH_ORDERs fence them from push/PR/merge while
  `archive` c2/c2b require a pushed branch and an OPEN or MERGED PR. Commanders never publish; the
  Admiral publishes. The decision-classes table reads `Merge to main | delegated`, with `git push`
  and `gh pr create` pre-cleared before wave 1. The Commanders refused correctly; clearing it is
  mine. Correction logged rather than made silently.
- `2026-08-14` — `INCIDENT` (environment, not defect): **stale `__pycache__` contaminated the Codex
  worktree's gate result.** `tests/test_episode_negative_control.py::test_every_field_has_a_named_
  independent_source` failed there and passed on `main` with the test file byte-identical. Attributed
  by falsification, not inspection: reverting the lane's `run_crew.py` to `main` did not fix it,
  removing the lane's three episode files did not fix it, moving `.agent-work` aside did not fix it.
  The `.pyc` embeds `/home/tommy/projects/constellation-skills-wt/epic-568-codex-tier-routing` — the
  **pre-relocation** worktree path — so `inspect.getsource` resolved to a dead file and raised
  `OSError: could not get source code`. Clearing `__pycache__` passes. Fallout of the wave-1 move
  from `constellation-skills-wt/` to `.worktrees/`. **Any gate measured in a relocated worktree
  before this date is suspect and must be re-measured after a cache clear.** Triage candidate: the
  suite should refuse a bytecode cache whose embedded root is not the current root, rather than
  failing as an unrelated assertion 4,000 lines away.
- `2026-08-14` — `RULING` (mine, delegated class `merge-to-main`): **publication refused for all
  three lanes; wave 2 goes to repair, not advance.** Baseline re-measured at gate time rather than
  reused: `main` Linux is **2980 passed, 0 failed**, so the set difference is non-empty for every
  lane and each failure is introduced by its own lane. After clearing contaminated caches:
  **Codex tier** — 1 failure, `test_code_map` stale root index (4544 vs 4543 entities), mechanical;
  the change itself is clean under 2,985 passing tests and two independent APPROVEs.
  **#510** — 4 failures: three in `TripLedgerComplianceOnTheHardAdvisory`, i.e. *inside the advisory
  text its own diff rewrote*, plus the stale map. The lane changed hard-advisory wording and updated
  some asserting tests but not these three.
  **#530** — 3 failures: `test_episode_observations::RealStoreTests` ×2, because its own episode
  record `epic-568-530-001 a5 (workaround)` carries the imperative `'Use'` and is not on the
  exception list, plus the stale map.
  Every one of these is a *local Linux failure*, which the wave-2 gate says blocks merge outright —
  this never reaches the CI set-difference step. Reviewer APPROVE is necessary, not sufficient: all
  three reviewers verified targeted tests only (the Codex reviewer ran 166 launcher tests), and none
  ran the suite that caught this. That gap is the wave's real finding.
- TRANSITION | boundary=wave-2-gate-refusal | decision=replan | verified
- `2026-08-14` — `RULING` (human, at the wave-2 checkpoint): presented what merged (nothing this
  wave), what the evidence showed (all three lanes red against a green `main`), and what the next
  wave proposes. The human chose: **publish the Codex lane now, repair #510 and #530.** Rebuild
  `map/INDEX.md` in the Codex worktree, push and open its PR under the delegated merge class, then
  dispatch two repair Commanders in isolated worktrees with cache-clean full-suite exit criteria and
  a float pre-ruling on #510's advisory wording. Wave 2 is no longer pre-cleared past this point.
- `2026-08-14` — `WAVE LAUNCH` `epic-568-wave-2-repair`, boundary `wave-2-gate-refusal`, after
  `verify_iterative_role_artifacts.py admiral-prelaunch` returned **exit 0**. Two Commanders, one
  per issue, each in its own worktree, each registered in the durable crew registry before dispatch:
  `constellation/epic-568-510/g2-repair/commander/attempt-1` in `.worktrees/epic-568-510` and
  `constellation/epic-568-530/g2-repair/commander/attempt-1` in `.worktrees/epic-568-530`. Both on
  Claude Opus, per the wave-2 routing rule that engine-core lanes do not go to lower tiers. Launch
  orders `LAUNCH_ORDER-wave2-repair-510.md` and `-530.md` are frozen and carry pasted verdicts, the
  cache-clearing pre-ruling, file ownership fencing the two serialized engine-core lanes apart, the
  honest-null clause, findings-file assignments, and stop conditions. #510 carries the one pre-ruling
  that is explicitly **not** delegated: if the shipped advisory wording is itself wrong rather than
  its three tests being stale, that is agent-visible behavior and floats to the human.
- `2026-08-14` — `INCIDENT` (gate integrity; surfaced, not decided): **the Windows carve-out is not a
  carve-out, it is the whole of CI.** `.github/workflows/ci.yml` defines exactly one job, `test`, and
  it is `runs-on: windows-latest`. There is no Linux, macOS, or any other CI job. The wave-2 term
  "GitHub CI may remain red only for Windows jobs; any non-Windows CI failure blocks merge" is
  therefore vacuous as a blocking condition — no non-Windows CI job exists that could ever fail. The
  merge gate's real teeth for this epic are (a) the local Linux suite, run on this machine and
  nowhere else, and (b) the failure-set difference, which still catches *newly added* Windows
  failures. Baseline captured for the wave: `main` run `31812026263` at `0448275e`, **84 failing
  tests**, saved to `evidence/main-baseline-31812026263-failures.txt`.
  I am not changing the gate — `good_enough` is a fixed boundary and this is the human's call. It is
  logged because merging while believing CI carries independent blocking weight would be deciding on
  a false premise. Raised for the human at the next checkpoint.
- TRANSITION | boundary=wave-2-510-engine-ruling | decision=replan | verified
- `2026-08-14` — `WAVE LAUNCH` `epic-568-wave-2-510-engine`, boundary `wave-2-510-engine-ruling`,
  after `verify_iterative_role_artifacts.py admiral-prelaunch` returned **exit 0**. One Commander,
  `constellation/epic-568-510/g3-engine/commander/attempt-1`, Claude Opus, in `.worktrees/epic-568-510`,
  which I rebased onto `c23c3d0f` first (base `23ed6b70`; two `map/INDEX.md` conflicts resolved by
  regenerating, never hand-editing a generated file). Order `LAUNCH_ORDER-wave2-510-engine.md`.
  Three things in it are worth recording as deliberate:
  (a) **pre-ruling 3 requires enumeration before change** — every test asserting on `_trip_hard_gate`
  refusal or trip-ledger contents must be listed first, because the previous repair in this lane was
  defeated by a whole-string pin living in a *different* class that a targeted run cannot see;
  (b) **the honest-null clause is pointed at the human's own ruling** — if the enumeration shows the
  refusal is load-bearing rather than incidental, the Commander stops and reports rather than forcing
  the ruled fix through a structural surface. The human ruled on the information available then, and
  new measurement is what would properly revise it;
  (c) **the MCP-only constraint is withdrawn and replaced with a disclosed CLI fallback**, since I
  asserted it twice without checking it was satisfiable. Correcting my own order rather than letting
  a third Commander discover it.

- `2026-08-15` — `WAVE RETURN` **Codex archive attempt 1 refused, correctly, and caught me out.**
  It did not fail; it declined to act and reported why, which is worth more than a forced advance.
  Its session was launched with `SPINE_FILE`/`SPINE_SESSION`/`SPINE_ENGINE` unset, so its door bound
  to the interactive-demo spine `scratch-mcp-424`. **A `spine_lease claim` or `spine_advance` from
  there would have mutated the demo spine.** It called neither. It also declined to edit the shared
  `.mcp.json` (it would have corrupted two live Commanders' bindings) and declined the engine CLI
  (its order said MCP-only and `checklist_engine.py` was a serialized lane others held). Every one of
  those judgements was right and nothing was mutated.
  **It also found my order factually stale:** it told the Commander to close by noting PR #579
  "remains OPEN and unmerged", but #579 merged at `23:32:12Z` — *after* the order froze — so obeying
  the Return Shape would have meant writing something false. **Fifth correction to my own launch
  orders this epic, all from Commanders falsifying me.** A frozen order is not a true order; it
  freezes what was true when written, and this run is now two-for-two on stale facts surviving into
  live instructions.
- `2026-08-15` — `INCIDENT` (infrastructure, third independent hit): **the unbindable spine door
  moved from an annoyance to a blocker.** Wave-2 Commanders #530 and #510 both floated it; the Codex
  archive Commander is the third, and the first for whom it stopped the work outright — archive is
  otherwise fully satisfiable (`c1`, `c2`, `c2b`, `c4` all verified; only `c3`, the lease release, is
  unreached). Three independent agents, three different coping strategies, one shared cause. Filed as
  a high-priority triage candidate; the fix is not authorized under the current contract.
- `2026-08-15` — `RULING` (mine, delegated): **relaunch the archive crew through the `cli` backend
  with `--spine`**, which binds `SPINE_FILE` and an assignment-keyed `SPINE_SESSION` into the child
  before its MCP servers start. Attempt 1 abandoned via the registry's own `--abandon --relaunch`
  path so the attempt counter and duplicate-guard stay honest, not by dispatching a duplicate. Order
  `LAUNCH_ORDER-wave2-archive-codex-attempt2.md` supersedes the stale one, corrects the PR state to
  MERGED, carries attempt 1's verified postconditions so they are not re-derived, and **instructs the
  Commander to stop rather than fall back if its door still resolves to a foreign spine** — with the
  door bound, a fallback would be covering up the very signal that made attempt 1 valuable.

- `2026-08-15` — `RULING` (mine, correcting my own over-caution): **the epic spine is driven through
  the engine CLI, per the contract's existing pre-ruling, and I was wrong to refuse it.**
  I had been treating "spine interaction is MCP-only" as binding on me and told the human I would
  rather stall at closeout than use a side channel. That constraint comes from the replan packet's
  `hard_constraints`, which govern **Commanders'** spine interaction. The contract itself already
  carries `decision:door-unusable-this-session`, graded `settled/measured · leans all-waves`: *"the
  `spine` MCP door is bound to a foreign scratch spine and `spine-epic` is dead, so this Admiral
  drives its spine through the engine CLI with an explicit `--session-id`."* Measured and settled
  before this session ever started.
  **The error was mine and it was consequential in the honest direction** — I nearly handed back a
  run stalled at closeout on a question the contract had already answered, and I stated that
  intention to the human before checking the source of the rule I was obeying. Enforcing a
  constraint without reading where it came from is the same failure as ignoring one.
  Acted on it: `checklist_engine.py --file .agent-work/epic-568/spine.json heartbeat --session-id
  admiral-epic-568` → heartbeat refreshed from `2026-08-14T16:03:27Z` (8.5 hours stale, inherited
  from the session that died) to `2026-08-15T00:48:23Z`. A stale lease on a live run is exactly the
  dead-ownership signal this epic exists to fix, and mine was the worst-aged one in the tree.
  **Closeout is therefore reachable from this session.** `execute` stays in-progress only until the
  two in-flight lanes return.
- `2026-08-15` — `LANE CLOSED` **Codex tier routing is terminal.** Archive attempt 2 completed the
  gate and **released its lease at `00:49:37Z`**, release-is-last honored. The lease record carries
  `previous_session_id` and a `takeover_reason` naming the dead predecessor, so it is a takeover with
  provenance rather than a recreated lease. First lane of the epic to reach a terminal state cleanly.
  **This confirms the door-binding ruling by result, not by argument:** the identical gate that three
  successive sessions could not reach cleared within minutes once the child was dispatched through
  the `cli` backend with `--spine`. The blocker was never the gate.
- `2026-08-15` — `INCIDENT` (owned, my measurement error): **I measured #510's gate while its
  Commander was still live, and briefly reported a false red.** The full suite at head `36212183`
  returned 2 failures in `test_episode_observations::RealStoreTests`, and I stated the lane was not
  publishable. It was not a lane defect. The Commander was mid-write on
  `episodes/active/epic-568-510-004/005/006.md`; a targeted rerun minutes later passed, and
  `git status` then showed those three files modified in the working tree. I had checked for a clean
  tree beforehand and caught a momentary gap between the Commander's own operations, which is not
  the same as the lane being at rest.
  **#530's Commander had already documented this exact hazard and I had already logged it:**
  *"Episode repairs are only measurable once committed — a mid-edit run always shows red on the
  unstaged edit."* I recorded that warning and then walked into it four hours later.
  **Ruling for the rest of this run and for the state note:** a lane is measured only after its
  Commander has formally returned, never on spine state or a `git status` snapshot. A live Commander's
  worktree is not a measurable artifact. The earlier result is void, not evidence, and #510's actual
  gate is unmeasured until its report lands.
  This is the third time this run that a plausible red has turned out to be an artifact of how it was
  measured rather than a defect — after the stale `.pyc` and the foreign spine door. All three cost
  real time and two of them were mine.
## Merges

- `2026-08-13` — **PR #576 merged (squash) → `main` at `9bb8c1b6`.** The wave-1 regression guard;
  no production code.
  **Gated under the amended merge gate, re-measured at merge time rather than reused.** The
  contract's original "green check exit code" is unsatisfiable while `main` is red, so the human
  amended it to *no new failures against the `main` baseline*. Applied as a set difference on a
  **fresh** PR run (`31662725956`, not the earlier `31641278091`) against the latest `main` run
  (`31619252908`): 76 failures each, `comm -13` returns **empty**, and the PR adds 2 passing tests.
  Independent reviewer APPROVE on file, with the reviewer having rebuilt the red-first proof rather
  than restating it.
  **Verified at source, not on the merge command's exit code:** `gh pr view 576` reports
  `state=MERGED`, `git log origin/main` shows `9bb8c1b6` at the tip, and
  `git cat-file -e origin/main:tests/test_worktree_precondition_wiring.py` confirms the guard is
  actually on `main`.
  Squash-merged, so the branch commits (`b513e6d0..32d7ccf4`) never become ancestors of `main`.
  **Cite `9bb8c1b6` for this work from here on**, not the branch commits — deleting the branch would
  orphan them.
  Note: merging this does **not** close wave 1 and does not trip the contract expiry. It carries the
  guard, not the fix. Recorded in the contract rather than decided silently.
- `2026-08-14` — **PR #577 merged (squash) → `main` at `0dd6a6eb`.** Native spine-origin worktree
  isolation plus crew/MCP cwd normalization. Human accepted the Windows-only delta; Linux and
  independent review gates were green.
- `2026-08-14` — **PR #578 merged (squash) → `main` at `0448275e`.** Six-line generated map refresh
  discovered by post-promotion verification. Linux full suite green; Windows failure-set delta
  strictly improved by one with none added.

- `2026-08-14` — **PR #579 opened → `epic-568-codex-tier-routing` at `a34cf500`.** Codex crew
  model-tier/reasoning-effort metadata, plus a mechanical `map/INDEX.md` regeneration as the final
  commit. Not yet merged: opened under the delegated merge class so the lane's Commander can satisfy
  its `archive` c2/c2b postconditions, which require a pushed branch and an OPEN or MERGED PR.
  **Gate measured at the exact published head, not reused from the Commander's run:** cache-clean
  full Linux suite **2986 passed / 0 failed** at `a34cf500`, against a freshly re-measured `main`
  baseline of **2980 passed / 0 failed** at `0448275e`. Failure-set difference empty. Two
  independent APPROVEs on file, one of them on the rework.
  **Verified at source rather than on the command's exit code:** `gh pr view 579` reports
  `state=OPEN`, `baseRefName=main`, `headRefOid=a34cf500…`, matching the local head exactly.
  CI has not been consulted yet; the merge decision waits on the PR's own run and the Windows-only
  carve-out, and is a separate logged act.
- `2026-08-14` — **PR #579 MERGE REFUSED at the gate. Escalated, not decided.**
  CI run `31841505188` completed `failure` (as every run here does — CI is one `windows-latest` job).
  Applied the amended gate as a set difference rather than reading the exit code:
  **`main` baseline 84 failures / PR 89 failures / `comm -13` returns 5, none removed.**
  The five added are the lane's own new tests:
  `BackendEquivalenceTests::test_reasoning_effort_is_metadata_only_and_recorded`,
  `::test_cli_resume_reads_reasoning_effort_from_registry`,
  `::test_legacy_resume_without_reasoning_effort_does_not_crash`,
  `ParentCliTests::test_abandon_relaunch_inherits_stored_reasoning_effort_when_not_reasserted`,
  `::test_abandon_relaunch_legacy_registry_without_reasoning_effort_stays_compatible`.
  **The letter of the gate refuses this merge: "Any test failing on the PR and not on `main` refuses
  the merge."** I am honoring that and not merging.
  **But the cause is not the change.** All five raise the identical pre-existing Windows defect that
  already reddens `main`: `install_constellation.InstallError: refusing to emit a hook command that
  does not start with a command word`, from a quoted `python.exe` path that PowerShell parses as a
  string literal. That error appears 201 times in the baseline run's log, and **68 of `main`'s 84
  baseline failures are in the same two files** — sibling tests in the very same
  `BackendEquivalenceTests` class already fail on `main`. The lane added five tests that traverse an
  already-broken Windows path; it did not break anything.
  **The question is one of gate interpretation and is the human's, not mine.** Read literally, the
  rule freezes test growth anywhere near the broken Windows path until #555 is fixed — no PR may add
  a test that touches it. Read by intent, the carve-out covers exactly this: a Windows-only failure
  from a known pre-existing defect. Both readings are defensible from the contract text, the gate is
  part of `good_enough` (a fixed boundary the human amended twice), and merging on my own reading
  would be deciding a boundary I do not own. Surfaced at the checkpoint with the evidence above.
  Evidence: `evidence/main-baseline-31812026263-failures.txt`, `evidence/pr579-31841505188-failures.txt`.
- `2026-08-14` — `RULING` (human, on the escalation above): **the merge gate is refined to compare by
  cause, not by test name.** A newly failing test is non-blocking when its error signature matches a
  failure already present on the `main` baseline; a failure carrying a *new* signature still refuses
  the merge. This is a `good_enough` amendment made under the human's authority, not my reading.
  It keeps the gate's teeth against genuinely new breakage while unfreezing test growth around the
  known Windows `InstallError` defect. **Third amendment to this gate**, after the 2026-08-12
  set-difference amendment and the wave-2 Windows carve-out — recorded in the contract rather than
  applied silently.
- `2026-08-14` — `WAVE RETURN` **#530 repaired and green.** Reworded `epic-568-530-001` statement
  `a5` from imperative to indicative and refreshed the map (commit `adeb1cd6`, rebased to
  `4ceace75`). Suite 3 failed → 0 failed. **The Commander falsified my launch order on one point and
  said so instead of complying:** I asserted an uncommitted `tests/test_spine_rail.py` change existed
  and told it to decide what to do with it. There was none — the 93 test lines were already committed
  at `97eb5d34` inside the APPROVEd diff, and `git diff HEAD` was empty on arrival. My error, from
  reading a `git status` line without checking what it referred to. **Fourth correction to my own
  launch orders this epic, all from Commanders falsifying me.** Recorded because an Admiral whose
  errors go unlogged looks more reliable than it is.
- `2026-08-14` — `FLOAT ACCEPTED, ESCALATED` **#510 stopped under pre-ruling 2, correctly.** It
  repaired 3 of 4 failures and refused the fourth. The refused one is not a stale expectation: at a
  pending gate reached by the agent's *own legal close* (g3, not the gate it is trapped in), the
  shipped wording says *"begin THIS guarded gate (`start g3`)"* while `_trip_hard_gate` refuses that
  exact `start` with *"so a FRESH agent starts this one."* The Commander simulated obedience and the
  ledger ended `[('g2','begin-refused'), ('g3','begin-refused'), ('g3','begin-released')]` — **the
  engine's own compliance signal brands the agent an offender for doing what the engine just told it
  to do.** The pre-change wording is also wrong at g3, so neither string is pinnable and re-pinning
  either way would have been the lane deciding agent-visible behavior. The defect is in `7426ffb1`,
  not in the repair. One deliberate failing test remains as the marker, documented in place; nothing
  was deleted, skipped, or loosened (assertion census `assertEqual 12 → 13`, all else unchanged), and
  an independent falsifier confirmed reverting only the test file reproduces the three original
  failures. **This is the human's decision class. #510 does not publish until it is ruled.**
- `2026-08-14` — `INCIDENT` (infrastructure, owned): **the "spine interaction is MCP-only" hard
  constraint was unsatisfiable for both dispatched Commanders, and I did not check that before
  writing it into their orders.** `scripts/mcp_spine_server.py:145-146` binds the door at module
  import from `SPINE_FILE`, and `.mcp.json` defaults that to the interactive demo; a running server
  cannot be rebound, and `tests/test_mcp_identity.py:914` pins that no argument may redirect it.
  Both Commanders' `mcp__spine__` doors came up on a foreign scratch spine and `mcp__spine-epic__`
  returned `Connection closed` — the same failure that dropped my own epic door earlier.
  #530 obeyed the constraint and therefore could not take its lease or attach evidence, reporting
  the gap rather than working around it. #510 used the engine CLI — the same engine the door wraps,
  same lease and journal provenance, explicitly not hand-edited state — and disclosed it plainly.
  **I accept #510's deviation and own the cause.** The constraint was impossible to satisfy from the
  session I dispatched it into, and a Commander that discloses a documented deviation is behaving
  better than one that silently stalls. The fix is mine, not theirs: crew dispatch must export
  `SPINE_FILE`/`SPINE_ENGINE`/`SPINE_SESSION` into the child environment *before* its MCP servers
  start. Filed as a triage candidate; no wave-2 latitude covers implementing it.
  Note the stale-path theme recurring: #530's foreign door pointed at `constellation-skills-wt/f-424/…`,
  the **pre-relocation** prefix. The wave-1 move survives in ambient MCP config as well as in `.pyc`
  files.
- `2026-08-14` — `RULING` (mine, delegated): **neither Commander released its lease, and both were
  right not to.** Release-is-last means after the closing advance on a terminal archive; releasing a
  non-terminal spine would strand archive's own closeout outside any lease. Both leases stay live for
  the authorised closer.

- `2026-08-14` — **PR #579 merged (squash) → `main` at `e0c998b6`.** Codex crew model-tier/reasoning
  metadata plus its mechanical map refresh. Merged under the human's cause-based gate amendment:
  all five added Windows failures were verified individually to carry the `install_constellation.
  InstallError: refusing to emit a hook command` signature, which is present 201 times in the
  baseline run and accounts for 65 failures in `test_crew_launcher.py` alone. No added failure
  carried a new signature. **Verified at source:** `gh pr view 579` reports `state=MERGED`,
  `mergeCommit=e0c998b6`; `git log origin/main` confirms it at the tip. Squash-merged, so cite
  `e0c998b6`, not the branch commits.
- `2026-08-14` — `RULING` (mine, delegated class `merge-to-main`): **#530's map commit was rebased
  rather than hand-merged.** Merging #579 first moved `main` and put both lanes in conflict on
  `map/INDEX.md`, which both had regenerated. Resolved by rebasing `epic-568/530-binding` onto
  `e0c998b6` and **regenerating** the map, never by hand-editing a generated artifact — a
  hand-merged map is a map that no longer matches its generator. Integration work, not the
  Commander's issue; the lane's own diff is untouched.
- `2026-08-14` — **PR #580 opened → `epic-568/530-binding` at `4ceace75`.** Spine-rail binding
  worktree derived from the spine path. **Gate re-measured by me at the exact published head rather
  than reusing the Commander's numbers**, and against a freshly re-measured baseline since `main`
  had moved: head **2988 passed / 0 failed**, `main` at `e0c998b6` **2986 passed / 0 failed**. The
  +2 is the red/green guard the issue closes on. Independent reviewer APPROVE on file. Awaiting CI
  for the cause-based set difference before merge.
- `2026-08-14` — **PR #580 merged (squash) → `main` at `c23c3d0f`.** Spine-rail binding worktree
  derived from the spine path. **The set difference was empty in both directions — 89 on the
  re-measured `main` baseline (run `31850708554` at `e0c998b6`), 89 on the PR (run `31851097391`),
  nothing added and nothing removed** — so this merge passed the *strict* name-based gate and never
  needed the human's cause-based amendment. Recorded because a gate that is amended should still be
  reported as unused when it is unused. The baseline moved 84 → 89 because #579 added five tests
  that fail on the known Windows defect; that rise is accounted for, not drift.
  **Verified at source:** `gh pr view 580` reports `state=MERGED`, `mergeCommit=c23c3d0f`;
  `git log origin/main` shows it at the tip; and `git cat-file -e origin/main:tests/test_spine_rail.py`
  confirms the guard is genuinely on `main` rather than merely claimed.
- `2026-08-14` — `RULING` (human, on the #510 float): **change the engine to permit the `start` the
  advisory tells the agent to issue.** The instruction becomes true rather than the wording being
  narrowed. I flagged the trade-off before the human chose: this alters engine gate semantics and
  the compliance ledger, and it reaches past #510's original cut into `checklist_engine.py` behavior.
  The human owns that call and made it. Consequences I now own: this is engine-core implementation,
  so it takes the serialized lane, and #510 does not publish until it lands with a red/green proof.

- `2026-08-15` — `WAVE RETURN` **#510 engine lane: the ruling's premise was falsified before it was
  implemented, and that is the most valuable thing this wave produced.**
  The human ruled *"change the engine to permit the `start` its advisory instructs."* The Commander
  measured first, per pre-ruling 3, and found **the engine already permits it for an agent who
  obeys**: the advisory names an *order* — request the refresh, *then* begin — and attaching the
  request first sends the guard down its release path. `start g3 → PERMITTED`, measured before any
  code changed. My own launch order asserted `_trip_hard_gate` "refuses that exact start"; it does
  not. The earlier `begin-refused` came from starting *before* attaching.
  **Implementing the ruling literally would have been a no-op, and the lane would have reported
  success while the symptom survived.** This is the sixth correction to my own orders this epic and
  the first that would have produced a silent false positive rather than a stall.
  What actually fires on obedience is the **branding**. Fixed there: `_trip_hard_gate` records the
  instructed `start` under its own outcome `begin-instructed`, appended with the same nine fields and
  the same append-only guarantee, but outside the pair the compliance selectors count. Selectors
  unchanged; `_trip_advisory` wording byte-for-byte untouched. The exemption requires all three of
  `verb == start`, gate is **active**, status is `pending` — `reopen`, an unrequested start, and any
  other gate stay as #467 left them.
  Evidence: new class 4/8 → 8/8 asserting over selectors not text; suite **2997 passed / 0 failed** at
  `bf7953b6` (I re-measured at the exact head, against a re-measured `c23c3d0f` baseline of 2986/0);
  independent falsifier **APPROVE** on a 1152-state differential sweep with zero states differing in
  raise, entry count, or gate status and exactly 3 relabel. Nothing deleted or loosened
  (`assertEqual` 614 → 632, zero methods removed). Best proof: driving its own closeout the engine
  recorded four `begin-instructed` entries and rendered no TRIP LEDGER line — the old engine would
  have branded that same compliant run four times.
- `2026-08-15` — `RULING` (mine, Admiral authority under the lane's `tc3`): **amended
  `docs/CHECKLIST_SCHEMA.md` to record the third outcome.** The doc closed the vocabulary at two
  values, so a reader of the contract would have classified a real `begin-instructed` entry as
  malformed. The lane was fenced from `docs/` and reported instead of reaching, which was correct.
  Not in the reserved class — this is `docs/`, not `docs/agents/*`. I wrote it from the measured
  behavior rather than from the commit message, and **left the historical-selector section unchanged
  after checking it**: it names `begin-refused`/`begin-released` because those genuinely are the two
  the selectors count, which is precisely why the third is excluded. Editing it would have made the
  doc worse.
- `2026-08-15` — **PR #581 opened → `epic-568/510-hard-advisory` at `bf7953b6`.** Held **unmerged**
  pending the human, despite merge being delegated: what was delivered is not what was literally
  ruled. The ruling rested on a premise the lane then falsified, and the fix serves the ruling's
  *intent* (obedience must not read as non-compliance) by a different mechanism than its *words*.
  Merging that on delegated authority would be deciding, on the human's behalf, that their intent
  survived the correction of their facts. That is theirs to confirm.
- `2026-08-15` — `INCIDENT` (harness, reported not routed around): the environment refused the
  Commander's mandated `FINDINGS-wave2-engine.md` write ("Subagents should return findings as text,
  not write report files"), colliding with the order's Data Locations clause. It folded the findings
  into its result rather than reaching for a shell write to defeat a tool-level guard. Correct
  behavior; my order created the collision by mandating a file the harness forbids.
- `2026-08-15` — `RULING` (mine, accepting a disclosed deviation): the Commander drove its own
  closeout while over the hard line, using the documented release path with a reason recorded in each
  request's `note`. Disclosed, journaled, and exactly the mechanism this lane just made non-punitive.
  Accepted.
- `2026-08-15` — `RULING` (human, on the #510 premise correction): **merge #581 — the intent
  survived the correction of the facts.** Confirmed that the goal was "obeying the engine must not
  read as non-compliance", that the `begin-instructed` relabel satisfies it, and that abandoning the
  literal no-op was right. Also confirmed the `docs/CHECKLIST_SCHEMA.md` amendment stands as an
  Admiral integration edit rather than being routed through its own lane. Merge proceeds under the
  cause-based gate once CI reports.
- `2026-08-15` — `WAVE LAUNCH` **#530 archive Commander**, `constellation/epic-568-530/archive/...`,
  dispatched through the **`cli` backend with `--spine`** so its door is bound before its MCP servers
  start. This is now the standard dispatch for any Commander that must mutate a spine; out-of-band
  `external` dispatch hands the child a door pointed at the demo spine. Order
  `LAUNCH_ORDER-wave2-archive-530.md` carries the merge evidence, the rebase disclosure, and an
  explicit instruction to **stop rather than fall back** if `spine_status` resolves to a foreign
  spine. It also pre-authorizes folding findings into the result if the harness refuses the findings
  file, since another Commander already hit that collision and was right not to defeat a tool guard
  with a shell write. Its predecessor's refusal to release a non-terminal lease is confirmed correct
  in the order rather than silently overridden.
- `2026-08-15` — `LANE CLOSED` **#530 is terminal.** Archive complete, **lease released at
  `01:10:00Z`**, zero blockers, takeover provenance recorded
  (`constellation/epic-568-530 -> .../archive/commander`). The Commander checked its door resolved to
  `epic-568-530` *before* mutating anything, exactly as ordered, and then **re-verified every
  publication claim at source rather than accepting my order's word for it** — branch head, local vs
  published divergence (`0 0`), PR state, the squash commit, and `git cat-file` proof that both the
  guard and the episode are genuinely on `main`. That is the standard: my order is a claim, not
  evidence.
- `2026-08-15` — `INCIDENT` (harness defect, found by result): **the crew launcher reports `failed`
  for a successful archive.** `run_crew.py` judges completion by the existence of the `--result`
  artifact, but the `archive` gate **moves the entire work area** — result artifact included — into
  `.agent-work/archive/<date>-<work-id>/`. So the launcher checks a path that archival has just
  emptied, and a correctly completed archive always reports failure. Observed here: crew
  `constellation/epic-568-530/archive/commander/attempt-1 -> failed` while the archived spine shows
  `archive: complete`, lease released, zero blockers.
  **This is the fourth false signal of the run**, after the stale `.pyc`, the foreign spine door, and
  my own mid-flight measurement. It fails in the expensive direction: an Admiral trusting the exit
  status would relaunch a Commander onto an already-archived lane, and the duplicate-guard would not
  stop it because the first attempt is marked failed. I caught it only because I check spine state
  rather than launcher verdicts. Filed as a triage candidate.
- `2026-08-15` — **PR #581 merged (squash) → `main` at `addf98c6`.** The `begin-instructed` outcome:
  obeying the HARD advisory no longer reads as non-compliance. **Set difference empty in both
  directions — 89 on the re-measured `main` baseline (run `31852340403` at `c23c3d0f`), 89 on the PR
  (run `31855447743`)** — so this passed the strict name-based gate, like #580 before it. The human's
  cause-based amendment has now gone **unused on two of the three merges** it was granted for; only
  #579 ever needed it. Worth stating: the gate was loosened once, on evidence, and the loosening
  turned out to matter less than the argument for it suggested.
  **Verified at source, not on the merge command:** `gh pr view 581` reports `state=MERGED`,
  `mergeCommit=addf98c6`; `git log origin/main` shows it at the tip; and reading the merged blobs
  directly confirms `begin-instructed` is present in both `scripts/checklist_engine.py` (4 hits) and
  `docs/CHECKLIST_SCHEMA.md` (3 hits) on `main` — code and its contract doc landed together, which
  was the whole point of the tc3 amendment.
- `2026-08-15` — `WAVE LAUNCH` **#510 archive Commander**, dispatched via `cli` backend with
  `--spine` (bound door), order `LAUNCH_ORDER-wave2-archive-510.md`. The order does three things
  deliberately: it tells the Commander its predecessor's **premise correction was accepted by the
  human** and that refusing to implement a no-op was right; it reports that **`tc3` was amended by
  me** and shipped in the same PR, including why the historical-selector section was left alone; and
  it **warns in advance that the launcher will probably report `failed`** because `archive` relocates
  the result artifact — telling it not to react, retry, or move the file back to satisfy a check that
  is itself wrong. Forewarning a known-bad signal costs one paragraph; letting an agent discover it
  mid-closeout costs a wrong decision.
- `2026-08-15` — `LANE CLOSED` **#510 is terminal.** Archive complete, **lease released at
  `01:22:59Z`**, zero blockers, takeover provenance from the engine Commander recorded. All three
  wave-2 implementation lanes are now merged and archived with their leases released.
- `2026-08-15` — `CONFIRMED` **the launcher's inverted archive verdict reproduced exactly as
  predicted.** I forewarned this Commander that `run_crew.py` would likely report `failed` because
  `archive` relocates the result artifact, and told it not to react. It reported
  `constellation/epic-568-510/archive/commander/attempt-1 -> failed` while its archived spine shows
  `archive: complete`, lease released, zero blockers — the same signature as #530. Predicted in
  advance, then observed: that is a confirmed defect, not an anecdote. The triage candidate stands at
  High.
- `2026-08-15` — `HYGIENE FINDING` (surfaced, not decided): **every lane's archived work area is
  stranded on its branch and is not on `main`.** All three lanes were **squash**-merged, so their
  branch commits never became ancestors of `main` — and each Commander then committed its archived
  work area *after* its PR merged. Comparing trees directly rather than with a three-dot diff (which
  misleadingly replays already-squashed content): `epic-568/510-hard-advisory` differs from `main`
  **only** under `.agent-work/` — 92 files, ~6,071 insertions of archive records and staged feedback.
  The other two lanes are the same shape.
  This matters because `.agent-work/archive/` **is tracked**: `main` carries 8,143 files under it
  from previous runs. So the repo's convention is that archived work areas live in history, and this
  epic's do not. Deleting the lane branches at hygiene time would silently discard them — and
  branch deletion is exactly what closeout hygiene asks for.
  Not decided by me. Sweeping ~6k lines of work-area records onto `main` is a judgement about what
  the repo should carry, not a mechanical tidy, and the contract reserves nothing about it either
  way. Raised at the closeout checkpoint with the branches left intact meanwhile.
- `2026-08-15` — `RULING` (human, at the closeout checkpoint): **sweep the stranded archived work
  areas onto `main` before deleting any lane branch**, preserving the repo's existing convention that
  archived work areas live in tracked history. Branch deletion follows the sweep, not before it.
- `2026-08-15` — `RULING` (human, at the closeout checkpoint): **close epic 568 on the four
  dispositioned items and carry #441 forward.** #441 keeps its own spine and lease intact and is
  picked up under a fresh contract after its external Codex quota lifts on 2026-08-20T06:19Z. The
  epic's definition of done required every authorized issue to be evidence-dispositioned; the human
  has explicitly accepted closing with one carried rather than holding the epic open six days and
  blocking the serialized lane meanwhile. Recorded as an accepted deviation from the stated
  definition of done, not as a quiet reinterpretation of it.
- `2026-08-15` — `HYGIENE DETAIL` **the three archives are not in the same state, because nothing
  said they had to be.** `epic-568/510-hard-advisory` and `epic-568-codex-tier-routing` each committed
  their archived work area to their branch (both 2 commits ahead of their remote);
  `epic-568/530-binding` left its archive at `.agent-work/archive/2026-08-14-epic-568-530/`
  **untracked on disk**, branch tip still at the repair commit `4ceace75`. None of the three orders
  said whether to commit the archive, so all three complied and diverged — the same pattern as the
  unsatisfiable MCP-only constraint earlier in the run, where silence and impossibility both produced
  variation rather than refusal. The sweep therefore needs two mechanisms: `git checkout <branch> --
  <paths>` for the two committed archives, and a plain add for #530's untracked one.
- `2026-08-15` — `ARCHITECTURE RECONCILE` (closeout c3, cartographer subagent; its own spine advanced
  and lease released). **The map is current — and the reconcile found that the epic's central
  guarantee is narrower than the epic believed.**
  Map verdict: `map/INDEX.md` and `map/ids.jsonl` rebuild byte-clean at HEAD, suite green at 2997/0,
  no map edit needed. Scope correction worth recording: `docs/architecture/` does not exist in this
  repo and never has, so this repo's structural map **is** the generated code map. It also ships
  `scripts/build_architecture_map.py`, fully tested, and has never run it on itself.
  **tc1 — the `.worktrees/` relocation measurably weakened `origin_worktree_refusal`, the very gate
  wave 1 added.** The refusal admits any cwd by containment (`checklist_engine.py:155`,
  `here.is_relative_to(root)`). Measured by calling the real function: a spine stamped with the
  **primary checkout**, driven from cwd `<repo>/.worktrees/epic-568-441`, is **not refused**; the same
  spine driven from `<repo>-wt/epic-568-315` **is** refused. Under the old sibling layout containment
  could never be satisfied that way. Nesting worktrees inside the repo makes a primary-stamped spine
  drivable from inside every nested worktree. Asymmetric rather than broken — but this epic's
  isolation guarantee is quietly narrower than its own record claims.
  **tc2 — the relocation exists only on disk.** `grep -rn "\.worktrees" scripts/ skills/ docs/ tests/`
  returns **zero hits**. `_default_wt_root` still returns `<repo>-wt`, and the MCP door
  (`mcp_spine_server.py:678`) passes no `wt_root=`, so **it still creates worktrees at the sibling
  path**. Live proof of the split: `.worktrees/epic-568-codex-tier-routing`'s spine is stamped
  `origin.worktree = .../constellation-skills-wt/epic-568-codex-tier-routing` while physically sitting
  in `.worktrees/`, and both layouts are registered in `git worktree list` simultaneously. Since
  `origin.worktree` is immutable engine identity, every already-stamped spine names the old location
  permanently.
  tc3–tc6 also recorded: no owner for "where does a worktree live" (twelve independent computations,
  two disagreeing answers to spine ownership, two producers normalizing differently); a stale
  `_default_wt_root` docstring the map faithfully republishes; `.worktrees/` neither tracked nor
  ignored, with `test_spine_lifecycle.py:136-160` **skipping** so the default-layout path has no live
  coverage — the same relocation whose stale `__pycache__` fabricated this run's phantom failure; and
  doctrine reading inconsistently across the launch-order template, `CHECKLIST_SCHEMA.md`, and the
  agent-facing engine reference, none of which says where a worktree should be created.
  **This does not block the close the human authorized, and I am not reopening the wave on it.** It
  goes into the epic summary as a stated limit on what wave 1 actually delivered, because accepting a
  summary that claims isolation was established would be accepting something the measurement
  contradicts.
- `2026-08-15` — **PR #583 merged (squash) → `main` at `297a0d09`.** The archive sweep the human
  authorized. Set difference empty in both directions (89 vs 89). Verified on `main` by counting the
  swept trees rather than trusting the merge: `2026-08-14-epic-568-530` 55 files,
  `2026-08-15-epic-568-510` 89, `2026-08-15-epic-568-codex-tier-local` 38, plus the staged feedback.
  Branch deletion is only now safe.
- `2026-08-15` — `RULING` (mine, repo hygiene, pre-cleared class): **branch deletion verified by
  content, not by ancestry.** Every lane was squash-merged, so `git branch -d` cannot confirm
  anything and ancestry checks are meaningless here. Instead I asked the only question that matters —
  *what exists on this branch that is absent from `main`* (`git diff --diff-filter=A`) — for all
  eight branches. Seven return **zero**. `epic-568/c1-check-cwd` returns exactly one file,
  `scripts/verify_worktree_precondition_coverage.py`, whose absence is **intended**: it was removed
  under the authorized four-file deletion earlier in the epic. Nothing is lost by deleting these.
- `2026-08-15` — `RULING` (mine, disposition rather than silent loss): **the abandoned first Codex
  spine `epic-568-codex-tier-routing` is discarded with its worktree, and recorded here instead of
  swept.** It is a work area that never ran — lease released, all three steps (`implement`, `review`,
  `integrate`) still `pending`, no evidence, no result. The work was redone as
  `epic-568-codex-tier-local`, which is what merged and archived. It is untracked and exists on no
  branch, so removing the worktree ends it.
  I did **not** sweep it onto `main`, deliberately. Committing a **nonterminal** spine into tracked
  history is the exact shape this epic's lifecycle ruling exists to prevent — archive refuses a
  resolvable nonterminal child, and the standing handoff already records 24 archived spines in a bad
  state. Adding a twenty-fifth to preserve a record of nothing having happened would be paying in the
  currency the epic is trying to stop spending.
  This entry **is** the preservation: the record survives in the log, which is archived to `main`,
  while the empty artifact does not. Stated as a decision so it is not mistaken later for an
  oversight.
- `2026-08-15` — `HYGIENE` **#441 is explicitly exempt from the sweep.** Its branch
  `epic-568/441-binding-store` and worktree `.worktrees/epic-568-441` are **retained**, holding a live
  spine with `execute` blocked and its lease intact, per the human's ruling to carry it forward to
  after 2026-08-20T06:19Z. Deleting it would destroy the state the carry-forward depends on.
- `2026-08-15` — `HYGIENE COMPLETE` (closeout c4, less the log archival). Eight branches deleted
  after the content check above: the three lane branches, both closeout branches, and the three
  wave-1 branches. Five worktrees removed (`epic-568-510`, `-530`, `-codex-tier-routing`, and both
  `constellation-skills-wt/` wave-1 trees), then `git worktree prune`.
  **Retained deliberately:** branch `epic-568/441-binding-store` and worktree
  `.worktrees/epic-568-441`, which hold the carried-forward spine with `execute` blocked and its
  lease live.
  Side effect worth naming: removing the two `constellation-skills-wt/` trees **eliminates the split
  layout the cartographer flagged as tc2** — the sibling location now has no live worktrees, even
  though the code still defaults there. That narrows the immediate confusion without fixing the
  defect, and it does not touch already-stamped `origin.worktree` values, which name the old location
  permanently.
- `2026-08-15` — `FINDING` (pre-existing, out of scope, recorded not fixed): **two stray work areas
  sit at `constellation-skills-wt/s` and `constellation-skills-wt/t`**, dated 2026-08-09, found while
  confirming the sibling worktree root was empty after the sweep. Each contains exactly `context/`
  and `mechanical/` — work-area subdirectories — and **neither is a registered git worktree**.
  Something built work-area paths from a work id consumed character-by-character rather than as a
  string, and created a directory per character. `s` and `t` are the tail of `constellation-skills-wt`
  read that way, or of some id ending in them; either way the path was constructed, not chosen.
  Direct corroboration of the cartographer's **tc3** — no owner for "where does a worktree live",
  twelve independent computations of it across `scripts/`, two of which already disagree about spine
  ownership. This is what that looks like when one of them is wrong.
  **Not fixed.** It predates epic 568 by five days, sits outside every authorized item, and the
  contract expires with this closeout. Left in place rather than deleted so the evidence survives for
  whoever picks up tc3 — a directory pair is cheap, and quietly removing the symptom of a
  path-construction bug would make it harder to find, not easier.
## Closeout

- `2026-08-15` — **Episodes captured.** Twelve, one per distinct thing that happened across the epic
  rather than one per wave, written through `apply_episode_delta.py` (the only write path into
  `episodes/`) and merged as PR #582 → `main` at `f43af44b`. Capture gate
  `verify_episode_captured.py epic-568 --phase feedback` exit 0. They are records, not rules: none
  prescribes behavior for a future agent, because a rule to follow belongs in `docs/agents/*` and is
  the human's to write. Writing them was also a live test of the episode-observation guard that
  caught #530 mid-epic — every `workaround` statement is in indicative mood, and the guard passes.
- `2026-08-15` — **Reconcile status.** Map current: `map/INDEX.md` and `map/ids.jsonl` rebuild
  byte-clean at HEAD, no map edit needed. Six findings recorded (tc1–tc6), the load-bearing one being
  that the `.worktrees/` relocation measurably weakened `origin_worktree_refusal` — the gate wave 1
  existed to add — and exists on disk only, with zero occurrences of `.worktrees` anywhere in source.
- `2026-08-15` — **Harvest and hygiene sweep.** Archives swept to `main` (PR #583 → `297a0d09`) and
  verified by counting the landed trees. Eight branches deleted, each first proven to hold nothing
  absent from `main`. Five worktrees removed; `epic-568/441-binding-store` and its worktree retained
  by ruling. Four triage candidates left filed and unimplemented — the bytecode-cache trap, the
  unbindable spine door, the inverted archive verdict, plus tc1–tc6 from the reconcile — all
  `recommend-and-defer`, since tracker creation is outside the delegated classes and the contract
  authorizes no work beyond the wave-2 items.
- `2026-08-15` — **Summary acceptance.** The epic summary was presented to the human as a published
  artifact and **accepted**, including its explicit statement that **wave 1 established worktree
  isolation only partially, in one direction, and only on disk**. That sentence was the point of
  presenting it: the alternative was a summary claiming a guarantee the measurement contradicts.
  The human also accepted closing on four dispositioned items with #441 carried, which is a stated
  deviation from the epic's own definition of done ("every authorized issue is evidence-dispositioned")
  rather than a reinterpretation of it.
- `2026-08-15` — **Epic 568 closed.** Four merges to `main`: `e0c998b6` (#579 Codex tier metadata),
  `c23c3d0f` (#580 spine-rail binding), `addf98c6` (#581 `begin-instructed`), plus the closeout pair
  `f43af44b` (#582 episodes) and `297a0d09` (#583 archives). Linux suite 2980 → **2997 passed, 0
  failed**. CI remains a single `windows-latest` job, red from pre-existing breakage, its failure set
  moved 84 → 89 entirely from tests this epic added to an already-broken path.
  **The finding worth carrying:** almost nothing that cost this run time was wrong code producing an
  obvious error. Five separate signals were confidently wrong — stale bytecode from a worktree that
  moved, a spine door answering about someone else's spine, three reviewer APPROVEs that had not run
  the suite, an Admiral measurement taken on a moving tree, and a launcher verdict inverted by design.
  The engine change that landed is the same story in code: the compliance ledger recorded an offence
  for obeying the engine. Whether that becomes doctrine is the human's call, not mine; it is in the
  episodes as observation only.
