# Epic retrospective source — epic #418 (`epic-418-redux`)

> **REPURPOSED 2026-08-08. This was written as a run brief for a `constellation-lessons-auditor`
> dispatch. That skill does not exist** — this epic's own **#447** retired it, replacing
> `LESSONS.md` and `AGENT_FEEDBACK.md` with `episodes/`. I was working from a stale copy of the
> Admiral skill, loaded before this epic rewrote it. Live closeout substep 1 is *"Record the epic
> retrospective as **episodes**"*, written **by the Admiral itself** via `apply_episode_delta.py`
> and proven with `verify_episode_captured.py` — **no subagent**.
>
> The content below is not wasted: it is exactly the raw material substep 1 wants. **But the rule it
> must now obey is different, and stricter.**

**THE RULE THAT CHANGED — read before writing a single episode.** From live doctrine:

> *An episode is a record, not a rule: write what you observed, and do **not** write a rule for a
> future agent to follow — a rule to follow belongs in `docs/agents/*` and is a human's call.*

Several candidates below are phrased as *rules* because I drafted them for an auditor whose job was
to route lessons into permanent homes. **As episodes they must be rewritten as observations.** Not a
formality: **#460's guard enforces it mechanically**, and it already caught a wave-3 crew writing an
episode whose remedy opened with an imperative verb. Anything below that reads "always do X" is a
`docs/agents/*` proposal for Tommy, **not** an episode.

- **One episode per distinct thing that happened** — not one per wave, and not a summary.
- **Only write path:** `apply_episode_delta.py --store-root episodes` on every invocation.
- **Prove capture** with `verify_episode_captured.py` before advancing.

**Status: waves 0-3 complete; wave 4 (#467) in flight, section G filled as it happens (36 observations
so far). Not final until #467's per-done-condition accounting lands.**

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
| 4 | #467 (A2) | **IN FLIGHT** — g1 complete (RED verified by adversarial review); 3/16 gates |

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

### G. Wave 4 (#467, A2 trip semantics) — in flight; these are recorded as they happened

**Still open**: the per-done-condition accounting and the DC6 compliance mechanism, which land when
the Commander returns. Everything below is already observed and committed.

**Each of these is one distinct thing that happened. Write them as observations — what was expected,
what was seen, what it cost, what worked around it. None of them is a rule.**

18. **The Commander tripped the governor while implementing the governor's trip semantics.** Asserted
    reading `0.2758`, hard `0.15`, engine printed `CONTEXT 28% (>= hard)`. It handed off at the seam
    and lost nothing. **Three instances ran in sequence; all three handed off cleanly; zero work
    lost.**
19. **The trip is only evaluated when a gated verb is attempted**, so an agent crosses the line
    unnoticed mid-gate and meets the refusal at the boundary. Two asserted readings, same hour: a
    Commander at 0.2758 (tripped at its gate) and the Admiral at 0.2629 (never asked). **DC1 is
    satisfied for gate-crossing roles and structurally silent for long-single-gate roles** — an
    Admiral sits inside `execute` for a whole epic.
20. **The Admiral's launch order contained an instruction that could not be obeyed**, and so does
    `global-everyone.md` §reach-up: *"write a refresh-request AND make sure `current` carries the
    DIGEST"* — only `advance` writes a why-record, and `advance` is what the refusal blocks. **#431
    had propagated into the doctrine written on top of it.**
21. **The capability was never missing; only the instruction was.** `attach` → `advance --why` →
    `attach` was accepted by the shipped engine at every step. The trip needed to stop saying
    *"blocked"* and start saying *"close this gate carrying your handoff, then stop."*
22. **A Commander that trips mid-step cannot update the spine's cold-start surface at all** —
    `advance` is the only writer of the why-trail and `execute` spanned 16 gates. The first instance
    tripped at a step boundary and could write its handoff; the second tripped mid-step and could
    not, leaving the spine's DIGEST two agents stale. **Mid-step is the ordinary case.**
23. **The reach-up signal has no notion of being served.** Active-gate-keyed, so a compliant handoff
    erases its own signal; records are permanent attachments with empty `ts`, so a *served* request
    reads as live until its gate starts. **The Admiral came one command from relaunching a healthy
    Commander, and then its replacement, in a loop.**
24. **Copy-pasting the refusal's own printed remedy attaches with exit 0 and does not release the
    block** — a silent no-op on the exact command the engine prints. Reasoned from source by one
    instance, then confirmed empirically by another.
25. **The gauge is a single-slot, unowned value.** A successor is judged on its predecessor's fill
    until its own first tool call overwrites it. Two windows — live overlap, and a stale-value
    window even when nothing is running. Both self-clear. **Recorded three times, at three different
    severities, by three agents**: claimed as *"the round trip cannot close"*, downgraded by its own
    author, then independently re-measured by a third with no stake. **The Admiral amplified the
    first version to the user before it was settled.**
26. **The Admiral stopped an agent to unblock its successor and thereby confounded the measurement**
    of the defect being reported — the idleness that cleared the symptom was the idleness it caused.
    A later instance's arrival reading, taken with both predecessors already stopped, is the
    uncontaminated one.
27. **A cold critic panel caught the Commander's own compliance observable being true by
    construction** — green in both worlds — before it shipped. Two critics independently. A second
    catch: one flag would have silently restored #431 after the fix.
28. **`LO-467.md` is reachable from nothing in the spine**, and it is where the environment
    invariants live. A cold successor inherits the plan and not the ground rules.
29. **An implementer volunteered a scope limit against its own result** — that the masking is
    confined to the `advance` refusal path — and asserted it in its own script rather than leaving it
    for a reviewer to find.
30. **Three agents disagreed in sequence, on the record, and were told not to reconcile it.** The
    Admiral directed that the earlier accounts not be rewritten, because a claim made, downgraded by
    its author, and re-measured by a third party is stronger evidence than any tidy single version.

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

31. **A reviewer found the mirror of the epic's whole subject: a check that cannot PASS.** The run
    had been hunting checks that stay green in both worlds. `r6-fowler`'s c1 ships a literal
    `<fowler-pass-record-path>` in its command, which a POSIX shell reads as a redirect from a
    nonexistent file, so it always fails. A gate's `verdict: "APPROVE"` disagreed with the frozen
    handoff's `ACCEPT WITH FINDINGS` vocabulary, so it too could not pass. **Both were headed for a
    waiver rather than a fix, which is how they survive.**
32. **An adversarial reviewer reframed the defect it was reviewing.** Its probe showed the blocked
    `advance` succeeds after the attach and writes a fresh DIGEST — so #431 is an
    **instruction-conformance** defect, not a mechanical deadlock: the engine permits the verb and
    in the same breath tells the agent not to run it. The repro had narrated this in prose rather
    than asserting it, and the reviewer said so.
33. **A wave-3 fix was complete and unreachable by the only role that needs it.** `amend` with a
    `retext-check` op is the sanctioned way to fill that placeholder, shipped by #465. It is
    documented in `docs/CHECKLIST_SCHEMA.md` and appears nowhere in the reviewer's SKILL.md, repo or
    installed. The reviewer force-waived instead. **Third built-but-not-wired instance in this epic.**
34. **The handoff protocol swept disposable evidence into permanent history.** 29 `red-repro/` files
    became tracked, so every re-run dirties 25 tracked files against a `red-leaves-no-residue`
    decision. `--diff-filter=A` puts all 29 in the predecessor's seam commit at its trip, not in any
    `git add` by the implementer — **the implementer's claim was true when written and the
    Admiral's commit-at-the-seam instruction falsified it.** Nobody priced that cost.
35. **A Commander refused to fabricate an artifact to satisfy a gate**, and floated for a ruling
    instead — the second time in the wave a crew declined an available green.
36. **The Admiral's messages consumed a crew's remaining headroom**, moving it from 0.147 to 0.1536
    against a 0.15 limit. Direction from above is a charge against the context budget the design
    reserves for building the handoff.

37. **Two Commanders mutated one run for four minutes and the lease did not stop it.** The Admiral
    dispatched a successor while its predecessor was still awake. Nothing was lost, and the crew's
    diagnosis was that this was luck: **every agent in the session shares one session id**, so
    `claim` treats a teammate as an idempotent self-resume. One agent's lease release carried the
    other's identity string.
38. **A rule that gates an action fired; rules that must be remembered did not.** Seven written rules,
    six broken by their own author the same day. The one that ever caught anything stood between the
    Admiral and a dispatch — it blocked a relaunch that would have destroyed a healthy Commander,
    before any evidence was weighed.
39. **An empty source diff was produced by a crew deliberately stashing its own fix** to confirm its
    new tests go red without it. Read from the diff alone, that is indistinguishable from 526 lines
    destroyed. `git stash list` separated them in one command.
40. **A monitor recommended relaunching a healthy Commander twice, on two different causes** — once
    on a served refresh-request reading as live, once on "quiet" that was a Commander waiting on its
    crew. Both times the recommendation was correct in form and wrong in fact.
41. **Nine monitor defects shared one shape: a proxy standing in for a fact only the thing itself
    reports.** File mtimes, a rendered string, a substring, a subprocess exit code, "quiet". Each was
    right until the world produced the case where it wasn't, and every failure looked like health.
42. **The Admiral ran to 54.9% fill against a 15% hard line and was never once asked to stop** — the
    trip evaluates only on a gated verb, and an orchestrator sits inside one step for a whole epic.
    It wrote its own handoff unprompted, which is the thing the design cannot compel.
43. **A boundary verifier refused four consecutive times, every refusal on shape rather than
    substance** — objects written as strings, and an issue id belonging to neither the completed nor
    the open list when those must exactly partition the wave.
44. **A wave-3 capability was complete and unreachable by the only role that needs it.** The
    sanctioned verb existed and was documented in the engine schema, and appeared nowhere in the
    reviewer's own skill. The reviewer force-waived a check it could have filled.
45. **The same unpassable check was found latent in four further gates** by a crew that read ahead of
    itself rather than meeting it four more times at four closing advances.

---

## 49. The base rate is higher than the Commander's four — three more found in one hour, none by looking

2026-08-08T16:57:33Z. `g4-implement` produced `CHECK_THAT_CANNOT_FAIL.md`, which documents **four specimens of the
defect inside issue #467 alone** — one of them the Commander's own near-miss, caught by two cold critics
before code was written — and argues that four instances in four artifacts by four actors *who all knew
the issue was about that defect* is "not an anecdote, it is a base rate."

Independent corroboration from the Admiral side, all inside the same hour, **none of it from searching
for the pattern** — each surfaced while doing an unrelated errand:

1. **#313 (installer).** `resolve_interpreter()` proves an interpreter *starts and runs a script*.
   Identical signal in both worlds: the interpreter that cannot run the suite also starts and also runs
   scripts. Found while sweeping cheap fixes — and my first draft of the finding was **wrong in the
   ordinary direction** (I claimed the installed commands were broken; they exit 0).
2. **#501 (the launch gate).** `_installed_skills_root()` guards with
   `name.startswith("constellation-")` to assert "you are running from an installed skill" — and the
   **repository is named `constellation-skills`**. The predicate matches the one directory it exists to
   reject. Found while dry-running a boundary to avoid a shape refusal.
3. **#502 (the provenance chain).** The journal is hash-chained specifically to make forgery expensive,
   and records `verb, task, session_id, ts, hashes` — **never the engine that executed the verb**, with
   four divergent builds live. Found while pre-computing an install sync.

**The generalization the crew's document should carry but cannot, because it only sees its own issue:**
three of these sit in **verification and provisioning machinery** — the installer's probe, the gate that
refuses launches, the chain that proves a run happened. The defect concentrates in the layer whose whole
job is to be trustworthy, and that is not a coincidence: **machinery that reports on other things is
rarely reported on by anything.** #467's four specimens are all inside the work; these three are inside
the instruments that judge the work.

Route: the crew's artifact stays theirs and is not to be edited by me. This observation belongs in the
epic retrospective as the **outer** frame around it.
