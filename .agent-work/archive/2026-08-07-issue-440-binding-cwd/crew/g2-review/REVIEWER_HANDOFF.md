# Reviewer Handoff — g2-review, issue #440 (epic-418 workstream A2)

Worktree `C:/Programs/constellation-skills-wt/epic418-a2-440`, branch `epic-418/a2-440-binding-cwd`,
HEAD `b332287`. **Use absolute paths — your shell's cwd resets between bash calls.**

## Your job

An implementer crew ran a two-arm live-fire acceptance harness and reported a **win**: a HARD governor
trip fired from a per-agent gauge reading produced by an agent **dispatched into a worktree**. The
Commander re-ran the verifier and it passes. Your job is to decide whether that claim survives an
independent, hostile read.

**Answer two questions, and refuse to take the harness's word for either.**

> **Q1. Is the captured trip genuinely produced by the WORKTREE-DISPATCHED agent's own reading** —
> rather than by the parent session, or by a file the harness placed itself?
>
> **Q2. Do the two arms differ ONLY in the hook path?**

These are the two ways this result could be a lie, and they are the whole reason this gate exists.

## Why the bar is this high — read this before anything else

**The mechanism under repair is the same mechanism that makes an in-worktree validation lie.**
`CLAUDE_PROJECT_DIR` resolves once at session launch and is inherited unchanged by every subagent
(issue #269), so an agent dispatched into a worktree still runs the **main checkout's** hook code.
A green obtained from inside this worktree therefore proves nothing — it is the same process that
would run the *unchanged* code.

This epic has already filed **three** issues in the tests-that-cannot-fail family (#432, #446, and a
finding inside #419's own run). Assume this is a fourth until you have shown otherwise.

The single most important thing you can do: **look for the value being proved getting handed to the
code that is supposed to derive it.** If the harness put the worktree root into any payload field,
fixture, env var, settings key, or prompt string that the hook then reads back, the result is void.
Read `run_two_arm.py` for this specifically. The claim is that `spine_rail.py` derived the root via
`git worktree list` and recorded `path_source: "git_worktree"` — test that claim, do not accept it.

## What is claimed, so you know what to attack

| | treatment (HEAD, fixed) | control (`cbd9aee`, pre-fix) |
|---|---|---|
| binding resolved to | worktree spine, `path_source: git_worktree` | sandbox main, `path_source: null` |
| gauge beside worktree spine | present, fill **0.559655** | absent |
| gauge at phantom path in sandbox main | absent | present, fill **0.562149** |
| `advance` | **REFUSED**, real exit **1** | succeeded, real exit **0** |
| gate after | stayed `in-progress` | `complete` |

HARD for `claude-sonnet-5` is **0.15**. Parent ran `opus`, subagent ran `sonnet`.

Claimed attribution, three independent ways, on both arms: a composite `session_id#agent_id` binding
key (only a dispatched agent keys composite); `identity_resolution_ms` present on the record (the
writer emits that fifth field **only** for a dispatched agent, #419); and `gauge.json`'s own `model`
field naming the subagent rather than the parent.

Claimed control quality: the control is a **positive** control — it produced a real over-HARD reading
**at the wrong path** rather than going quiet. That is what rules out the three impostors that would
otherwise masquerade as "the bug reproduced": an incomplete sibling `scripts/` set (the writer nulls
**silently** if `gauge_writer_hook.py` cannot import `spine_rail.py` as a filesystem sibling), an
uncalibrated model (absent from `gauge_reader._PROFILES` yields no reading at all), and a subagent
that never received an `agent_id`.

## Where everything is

- Harness: `.agent-work/issue-440-binding-cwd/acceptance/run_two_arm.py`
- Evidence verifier: `.agent-work/issue-440-binding-cwd/acceptance/verify_evidence.py` (has a
  `--selftest` mode that damages copies of the evidence and asserts each one fails)
- Evidence: `.agent-work/issue-440-binding-cwd/acceptance/evidence/` — `arm-treatment.json`,
  `arm-control.json`, `arm-diff.txt`, `preflight-arms.json`, `settings-{treatment,control}.json`,
  `prompt-*.txt`, `headless-*.log`, `live-checkout-untouched.json`, `probe.json`
- The crew's own account: `.agent-work/issue-440-binding-cwd/crew/g2-implement/IMPLEMENTER_RESULT.md`
- The fix under test: `scripts/hooks/spine_rail.py` (commits `9d44aa6` g1, `38214ec` g1b)
- Reference: `docs/GAUGE_WRITER_HOOK.md` — especially "Skip-on-uncertainty, enumerated", which lists
  every reason the writer legitimately writes nothing. That is your diagnostic checklist.

## Specific things to check, beyond the two questions

1. **The arm-difference claim, verified yourself.** `arm-diff.txt` is a recursive `diff -rq` of the
   two complete `scripts/` trees naming exactly one differing file. Confirm the diff was taken over
   whole trees and not a curated subset, and confirm the two settings files differ only in the hook
   path. Read `build_arms()` and `build_settings()` rather than trusting the recorded output.
2. **Whether the fills are close enough to carry the argument.** 0.5597 vs 0.5621 is offered as proof
   that the outcome difference is the hook path and not the inflation. Decide whether that holds.
3. **Freshness.** `verify_evidence.py` checks `observed_at` against a 30-minute window. Attempt 1's
   evidence was ~28 hours stale and correctly failed. Confirm the passing evidence is genuinely from
   the fresh run and that nothing stale was carried forward.
4. **A check the crew REWROTE rather than satisfied — adjudicate it.** The original guard asserted the
   live checkout's `.agent-work/.spine-rail-binding.json` was byte-identical before and after. It
   failed (4213 → 4663 bytes). The crew diagnosed concurrent live-agent writes (including this run's
   own engine `claim`, and a second Commander, cmdr-447, running right now), argued byte-stability is
   unsatisfiable for shared live state, and replaced it with a leakage test — no sandbox path present
   in the live store — plus a fifth selftest mutation proving the replacement can fail. **Rewriting a
   failing acceptance check is exactly the shape that should draw scrutiny.** Say plainly whether this
   was a legitimate correction or a weakening. Verify the live store really holds no sandbox path.
5. **Whether `verify_evidence.py` can actually fail.** Run `--selftest`. Then try to break it yourself
   in a way its five mutations do not cover.
6. **The first treatment launch went quiet and was re-run.** The crew reports the subagent *declined
   the inflation protocol*, reading the prompt's own defensive framing as social engineering, and that
   it re-ran the arm **unchanged**. Confirm from `headless-*.log` that the arm was re-run unchanged
   and not adjusted until it passed. A quiet run that gets retried until it speaks is a garden of
   forking paths; a declined run that complies on an identical re-run is not. Decide which this was.

## Scope — hard

- **Review only. Change nothing.** Do not modify any script, hook, test, or evidence file. If you
  find a defect, that is a finding to report.
- Do not re-run the arms. They are expensive headless runs that inflate a subagent past 150K tokens,
  and this account hit a weekly usage limit during attempt 1. Reading the evidence, reading the
  harness source, and re-running the cheap verifier is your method. If you believe an arm genuinely
  must be re-run to settle a question, **say so as a finding** and stop rather than launching it.
- **Never touch the live checkout** `C:/Programs/constellation-skills` — not its
  `.agent-work/.spine-rail-binding.json`, not its `.claude/settings*.json`, not any real worktree.
  Reading the live binding store is fine and is needed for check 4; writing it is not.
- Do not commit.

## Constraints

- Use `python`, **never** `py` — `py` on this box resolves to a runtime with no pytest and produces
  fake failures.
- **Gate on real exit codes.** Redirect to a file, then echo `$?`. `cmd | tail -5; echo $?` captures
  `tail`'s exit code, not `cmd`'s. This has already cost this epic one wrong call.
- If you dispatch anything, **cap it at Opus or lower and name the model explicitly. No Fable at any
  tier** — the user's global default is `fable`, so an unspecified model is a violation.
- A `.get()` on a guessed field name returns `None`, and `None` reads as a clean negative. Read the
  schemas in `scripts/gauge_reader.py` and `docs/GAUGE_WRITER_HOOK.md` rather than guessing.

## Verdict shape

State **APPROVE**, **APPROVE WITH FINDINGS**, or **REJECT**, and answer Q1 and Q2 explicitly with the
specific evidence that settled each. Do not hedge: if you cannot settle a question from the available
evidence, say which question and what would settle it.

A finding that the result is **not** what it claims is a valuable outcome, not a failure of this gate.
So is a clean approval. What is not acceptable is agreeing with the crew because the crew was thorough.

## Return format

Write `REVIEW_RESULT` to
`C:/Programs/constellation-skills-wt/epic418-a2-440/.agent-work/issue-440-binding-cwd/crew/g2-review/REVIEW_RESULT.md`
**before you go idle**, and deliver it as your final message: verdict first, then Q1, then Q2, then
findings (each with file and line), then anything you could not settle.
