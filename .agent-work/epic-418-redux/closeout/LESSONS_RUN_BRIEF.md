# Lessons-audit run brief — epic #418 (`epic-418-redux`)

**Status: DRAFT through wave 3. Wave 4 (#467) is in flight — its section is a marked slot and this
brief is not dispatchable until it is filled.** Compiled by the Admiral for the closeout
lessons-audit dispatch (`constellation-lessons-auditor`, fresh context).

---

## What this run was

Epic #418, the "mechanisms + cleanup" stage of the post-phase-1 overhaul. It **relaunched** as
`epic-418-redux` on 2026-08-07 when the predecessor's latitude contract expired at the wave-1
checkpoint; waves 0 and 1 stayed merged and the run continued on a fresh Admiral spine. The
predecessor is archived at `.agent-work/archive/2026-08-07-epic-418-waves-0-1/`.

**Spec of record:** `.agent-work/epic-418-redux/spec-revision/REVISED_SPEC.md` (confirmed by Tommy
2026-08-07; `verify_spec_confirmed.py` exits 0 on `--phase review` and `--phase confirm`). The
2026-08-03 original is superseded and kept only for provenance — several of its "by construction"
claims were **falsified by this epic's own execution**, which is itself an audit-relevant fact.

**Waves:**

| Wave | Issues | Outcome |
|---|---|---|
| 0 | #419 #420 #422 #425 | merged, closed |
| 1 | #440 #447 | merged, closed |
| 2 | #433 #436 #460 #464 | merged, closed |
| 3 | #461 #465 #488 #489 | merged, closed, all reviewed on the forge |
| 4 | #467 (A2) | **IN FLIGHT — fill this in** |

**Green baseline at wave-3 close:** `1793 passed, 2 skipped, 683 subtests, exit 0`.

---

## The organizing finding — treat this as the run's thesis, and audit it as a claim

**A check that cannot fail: a signal whose value is identical in the healthy and the defective
world.** This is not a theme the Admiral proposed and then found support for. It has **three
independent sources** inside the epic, which is why it is being handed to you as the spine of the
audit rather than one candidate among many:

1. **Critic finding F8** on the spec review — *"the purest check-that-cannot-fail in the document"*
   (*no absence is evidence*).
2. **#467's DC6**, which prices it as a deliberate design cost — *"an instruction is satisfied or
   ignored with identical traces."*
3. **Four independent field findings in wave 2**, from Commanders who hit it in unrelated code.

Every wave-3 issue was an instance: a guard that could not register its own failure.

**Your job on this is not to agree with it.** Audit whether the evidence actually supports promoting
it, and if it does, decide where it belongs — it is a candidate for a **doctrine section** or a
**Charter nomination**, not for a lesson-inbox entry that goes stale.

---

## Candidates for routing

Each of these needs a routed disposition: *graduate-and-retire to a named permanent home* /
*template delta* / *Charter nomination* / *constellation export* / *lesson-inbox delta* /
*drop-with-reason*. **No candidate may be left unrouted** — that is the engine-enforced rule.

### A. Method candidates (invented in the field this run)

1. **Mutation-testing the guard.** Break the branch a test defends; confirm the test goes red.
   **Invented unprompted by a wave-2 reviewer**, then carried into every subsequent launch order and
   review brief, where it caught real defects each wave. Strongest graduation candidate in the set.
2. **Harvest before sweep**, with the *content* test rather than the filename test:
   `h=$(git hash-object <f>); git cat-file -e "$h"` — non-zero means the content exists nowhere in
   git. A filename survey would have found five candidates and been **wrong about one**
   (`h-447/LESSONS.md`, already in git). See `.agent-work/harvest-418-redux/README.md`.
3. **Liveness is not a field, it is recent write activity.** A Commander's `spine.json` heartbeat
   read **27 minutes stale** while it was actively journaling its inner checklist. The discriminator
   that worked: `find <worktree> -newermt "-6 minutes" -type f`. Related open issue: **#457**.
4. **Never use ancestry to decide merge status** — squash-merge returns the same answer for merged
   and abandoned. Ask the forge. Corollary found this run: `git diff origin/main..HEAD` inside a
   worktree lists files where *main* is ahead, reading as though the branch reverted them.

### B. Platform/tooling hazards (candidates for a reference, not a lesson)

5. **Four silent `gh` hazards, all of which produced a false success signal:**
   - A backticked code span in a double-quoted `gh` argument is executed as **command
     substitution**; the comment posts anyway, missing that phrase, with every success signal
     intact. (Corrupted a comment on #264.)
   - `gh issue close -F <file>` accepts the flag, prints nothing, and **does not close**.
   - `gh issue close --comment` **silently discards** the comment when the issue was already closed
     by a PR body keyword. Two evidence write-ups evaporated before this was caught.
   - `gh pr merge` can **exit 1 on a merge that succeeded** (`--delete-branch` fails on a
     worktree-held branch).
6. **`gh pr review --approve` is refused platform-side** — "Can not approve your own pull request",
   because every agent authenticates as the same identity that authored every PR. Substitute:
   `--comment -F <file>` with the verdict on the first line. **Audit note:** the Admiral
   misattributed this to reviewer negligence in three launch orders and twice to the user before
   finding the cause. The misattribution is itself the lesson.
7. **`ci.yml` has no `paths-ignore`**, so an `.agent-work`-only commit runs the full 8-minute suite.
   Pushing per log entry put **6 concurrent CI runs on main, all the Admiral's**, starving a PR's
   own check ~25 minutes. Operating fix adopted mid-run: batch bookkeeping commits, push at
   boundaries. **Source fix is a code-fix issue candidate.**
8. **#468** — the repo-vendored `verify_iterative_role_artifacts.py` cannot run from this repo; its
   installed-skill guard passes by accident because the repo is named `constellation-skills`. Bit
   again at the wave-4 prelaunch.

### C. Code-fix issue candidates already on the board

- **#439 / #484 — two template-instantiation defects of one family**: `execute.c2` shipped a
  relative script path; `archive.c2b` shipped a **literal, never-substituted `<branch>`
  placeholder**. The second was *"caught only because `advance` actually ran the check and it
  failed."* **Two in one spine argues for a sweep of the class, not two point fixes** — that
  recommendation is the candidate.
- **The governor thread, recommended to land as one piece:** #458 (wire the gauge writer into
  *tracked* settings so it ships at all) · #264 (**1144 lines, 13 tests, unmerged**, asserting the
  gauge is still *measuring*) · #452 (multi-spine attribution). #488 shipped this run.
- **#457** — lease/heartbeat liveness. Deliberately **not** folded into wave 3: both readings of the
  field are uninformative, so fixing it means deciding how liveness is encoded at all.
- **#493, #495, #496, #497, #498** — filed by #465's triage. **#494 is already CLOSED**, so five,
  not six. Keep-or-drop is an acceptance-time question and this audit produces the evidence.

### D. Admiral self-findings — audit these as harshly as the rest

9. **The Admiral built three checks that could not fail, in the epic about checks that cannot fail.**
   (a) A crew-progress monitor that counted historical `.agent-work` files carried in the checkout,
   reporting identical counts for all three crews; (b) a refresh-state monitor that reported
   `refresh=1` for an hour after a relaunch had superseded it; (c) fixed only by keying on the
   **engine lease session id**, which changes on relaunch. **The general form — key a monitor on
   something that changes when the thing you are watching changes — is the candidate.**
10. **A status claim carried across three waves and a compaction, never re-derived from its source.**
    `STATE_NOTE.md` said *"A2 has no issue cut"* for the whole run and the Admiral twice told Tommy
    that cutting it was a scope decision it would not take. **#467 had been open and fully specified
    the entire time.** A stale note and a true note read identically — the run's own thesis, aimed at
    the run's own bookkeeping. Candidate: **state notes carry claims with a re-derivation command,
    or they carry pointers, not claims.**
11. **`$?` after a pipe captured `tail`'s exit**, reading a verifier REFUSAL as `VERIFY_EXIT=0`.
    Second instance of this family in the run. Fix adopted: redirect to a file, or `${PIPESTATUS[0]}`.
12. **A refresh-relaunch of a crew launched under a valid contract was ruled *continuation*, not
    further dispatch.** Flagged for Tommy to overrule; he has not. Record the ruling either way.

### E. Measurement produced this run

13. **First per-crew context-fill series** — `evidence/w3-gauge-series.tsv`, with four caveats
    recorded *before* anyone drew a conclusion from it (see its README). Chief among them: **the
    `dispatch` column is not an agent**, so a naive min/max by dispatch reads a relaunch as fill
    *falling*, which never happens.
14. **The trip band appears role-blind.** Same machine, same hook, same hour: crews tripped at
    **17-21%** fill; the Admiral ran to **44%** with no trip. Every trip this epic saw cost a
    relaunch at a seam and lost no work.
15. **The governor does not ship.** Tracked `.claude/settings.json` wires `spine_rail.py` only and
    the gauge writer on **nothing**; every governor observation this epic made came from one
    laptop's untracked `settings.local.json`. This is **#458** and it re-frames every governor
    measurement above as single-machine.
16. **Cross-project feedback sweep, 2026-08-08: no new or open candidates** across
    `f1Brainz`, `network_elo`, `story_time`. Evidence: `closeout/feedback-sweep-2026-08-08.md`.
    A clean sweep is a result, not a skipped step — record it as such.

### F. Doctrine candidates collected but not promoted

17. **#460's 22 doctrine candidates**, at `.agent-work/r418-460/crew-handoffs/g2-implement-result.md`
    § "Evidence 4". Collected, nothing promoted. **Promotion is always Tommy's call** — route them,
    do not promote them.

### G. Wave 4 — SLOT, FILL BEFORE DISPATCHING THIS BRIEF

> #467 (A2, trip semantics) is in flight as of 2026-08-08. Its per-done-condition accounting,
> its DC6 compliance mechanism, and the Commander's own dogfooding observation if it trips the
> governor mid-run, all belong here. **Do not dispatch this audit with this section empty.**

---

## Inputs the auditor should read

- `.agent-work/epic-418-redux/ADMIRAL_LOG.md` — the run's audit trail; every ruling, incident,
  merge, wave launch, transition exit and owned error.
- `.agent-work/epic-418-redux/LATITUDE_CONTRACT.md` — base contract + Addenda R1, R2.
- `.agent-work/epic-418-redux/STATE_NOTE.md` — including its own recorded staleness failure (D10).
- `.agent-work/epic-418-redux/launch-orders/` — four launch orders and two review briefs.
- `.agent-work/epic-418-redux/transitions/` — `w2-to-w3`, `w3-to-w4`.
- `.agent-work/harvest-418-redux/` — four files that existed **nowhere in the git object store**,
  collected from the predecessor run's worktrees before sweep. **Their disposition is explicitly
  left to this audit**: they are pre-retirement `RETURN.md` / `AGENT_FEEDBACK.md` formats, and
  `episodes/` replaced both. Convert to episodes, or drop with a reason.
- `episodes/` — the store. **Only write path is `apply_episode_delta.py --store-root episodes`.**
  An episode is a record, never read back as a rule.

## House rules for this audit

- **Every lesson you read, you end**: its operative content graduates to the doc that owns it and
  the lesson is retired, or it is deleted with a reason. Nothing audited stays active.
- **Write inbox deltas only via `apply_lessons_delta.py`.** Every graduation needs its paired
  `retire` op.
- When an op edits a shipped compact-format JSON template, edit the raw text **surgically** — never
  round-trip through `json.load`/`json.dump`, which reflows the file and destroys blame — then
  re-validate with `json.load`.
- **Sibling ids raised from different worktrees for the same defect are `confirm`s** of the existing
  lesson (or an `amend` to reword it), **not** new `add`s. A new slug for the same defect forks its
  identity.
