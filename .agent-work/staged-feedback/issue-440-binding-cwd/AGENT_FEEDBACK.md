# Agent Feedback — staged for harvest

Staged rather than appended to the durable root. See `FENCE.md` beside this file.

## issue-440-binding-cwd — 2026-08-07 — delegated Commander (epic-418 wave 1, workstream A2)

**Run shape.** Issue #440: a worktree-dispatched agent's gauge binding recorded a main-checkout path,
so the reading and the reader never met. Resumed a **crashed** prior session on a durable lease at
`g2-implement`; drove `execute.json` through g2-implement, g2-review, g2-integrate and g3-close, then
the parent spine through reconcile, triage, review, feedback, archive. Verdict: a win — a HARD trip
fired from a worktree-dispatched agent's own reading, two-arm, live.

**Friction / unclear**

- **Backticks in an engine `--why` string are executed by bash.** A `--why` containing
  `` `git worktree list` `` and `` `py` `` was substituted by the shell: it ran both, spawned
  interactive Python REPLs that hung the call for two minutes, and leaked `git worktree list` output
  into the stored `satisfied_by` note on `g3-close.c2`, which is now polluted. Long `--why` values
  need `"$(cat file)"` and no backticks. Cost: ~5 minutes and one corrupted provenance note.
- **`recover_crews.py` advises a recovery route that does not exist for `--backend external`.** It
  correctly flagged the crashed g2 implementer as RESUMABLE and said to `SendMessage` the crew's
  recorded `agentId` — but no `agentId` is recorded for an externally-dispatched crew, so the only
  available route was `--abandon … --relaunch`. The advice should branch on backend.
- **`start` is silently required before `advance`, and is easy to lose.** Four separate gates refused
  an `advance` with "must be in-progress" after an `attest` had already succeeded against them.
  Attesting a pending step works; advancing it does not. Cost: four extra round-trips.
- **The `g3-close` gate re-runs its own gated command (~4 min) with no indication it is doing so.**
  It reads as a hang, and I burned two timeouts before checking the postcondition definition. It also
  inherits the session environment, so it hit the `FORCE_COLOR` trap below and refused until the
  variable was cleared for its subprocess.
- **Evidence type requirements are discoverable only by failing.** `attest` refused an `artifact`
  where `implementer-result` was required, and a `review-result` whose `verdict` was not literally
  `APPROVE`. Both refusals were *correct and useful* — see Improvement signals — but the required type
  is not shown in `current`'s postcondition line, which just says `artifact — REVIEW_RESULT returned`.

**Crew-reported friction**

- **The R2 resumption handoff I wrote contained an ordering conflict** — "run treatment first" versus
  "prioritise the control if you can only afford one arm". The implementer crew flagged it explicitly.
  Mine to own: a contingency clause needs to state which instruction it overrides.
- **`attest --note` versus `advance --why` is unclear at the crew tier.** The crew reported not
  knowing which carries the verification and which carries the understanding.
- **A dispatched subagent declined an inflation protocol because of the prompt's own defensive
  framing.** It read "nothing below looks like a trick" and "is not a prompt-injection attempt", plus
  a fixed completion token, as social engineering and refused. An unchanged re-run complied. The
  defensive framing triggered the refusal it was written to prevent. Filed in #455.
- **Per-launch headless logs are overwritten**, so the declined launch left no artifact and its
  diagnosis degraded to uncorroborated prose. The reviewer had to settle it indirectly from file
  mtimes. Filed in #455.

**Improvement signals**

- **The typed-evidence gate is the best thing in this engine and should not be softened.** Refusing a
  `review-result` whose `verdict` was not literally `APPROVE` forced me to make the
  "APPROVE WITH FINDINGS → APPROVE" reduction *explicit and recorded* in a
  `commander_adjudication` field, rather than quietly typing the word the engine wanted. That is a
  gate converting a judgement call into a visible one.
- **The positive-control requirement earned its keep twice in one gate**, and both times against the
  same failure shape: a killed headless run and a declined subagent each produced silence
  indistinguishable from "the bug reproduced". Any acceptance harness in this family needs a control
  proved to have *worked and missed*, not merely to have been quiet.
- **`FORCE_COLOR=3` in the agent harness manufactures a false red baseline.** `test_mutation_floor.py`
  parses its own pytest subprocess output without stripping ANSI, so it reports
  `HARNESS ERROR: no FAILED test node` while its own captured output contains those nodes. 10 false
  failures with the variable set, 14 passed without. This is a second, independent false-red in the
  same family as the standing `py`-is-not-the-test-runner warning, and unlike that one **it fires for
  `python` too**. It also explains why this epic's recorded `cbd9aee` baseline of `exit 0` could not
  be reproduced. Filed as #454; belongs in `_COMMON.md` beside the `py` warning.
- **Deriving a failure distribution from a command rather than the pytest tail paid off immediately.**
  `uniq -c` over the `FAILED` lines localised all 10 failures to one file; archiving the base commit
  and re-running there proved them pre-existing (11 there, one *more*). Reasoning from the symptom
  would have produced a wrong regression call.
