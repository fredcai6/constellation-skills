# Launch Order: `impl-w5-addressing` — crew addressing (#507 + #370 + #413)

Epic #418, wave 5 (the final wave). **Implementer-with-plan** — this is bounded, well-understood
work; it does not need a Commander's full spine.

## Mission

**A crew's handoff names an ephemeral agent instance as its delivery target.** Instance names are
ephemeral — a Commander that trips is replaced by `-h`, then `-i`, then `-j` — so by the time a crew
delivers, the name in its handoff often no longer resolves.

**The failure is bidirectional, and neither end can recover alone:**

- **Crew → Commander.** `SendMessage` to `commander-w4-467-h` fails with *"No agent named
  'commander-w4-467-h' is reachable. Did you mean: commander-w4-467-b, -c, -d"* — **the lookup
  resolves a lineage toward its origin, not its head.** A handoff naming `-h` lands on `-a`, the
  retired first instance.
- **Commander → crew.** The crew's reply-to identity is a **type** (`general-purpose`), not a name.
  The misrouted Commander cannot send it back: *"No agent named 'general-purpose' is reachable."*

**Only the Admiral, in the middle, can address both ends.**

### Measured, not anecdotal — three filings, three epics, one defect

| Issue | Epic | Evidence |
|---|---|---|
| **#507** | #418 wave 4 | Three deliveries, three misroutes, three Admiral relays — **in one wave.** In the third, *the loop could not close without the Admiral at all.* |
| **#413** | #298 issue #310 | **4/4 dispatches failed.** Agents' own words: *"`commander-310` and `general-purpose` are both unreachable via SendMessage from my thread."* |
| **#370** | #298 issue #304 | A g4 reviewer returned **APPROVE with 13 items, 0 blockers, 3 triage** — including a finding the successor needed. Its commander had handed off hours earlier. **The result survived only because the recipient chose to forward it rather than discard it.** Nothing in the protocol required that. |

Every misrouted message carried a **completed verdict**. Nothing was lost only because well-behaved
agents compensated — which is exactly what this epic exists to stop relying on.

**Confirm all three collapse to one defect against the issue BODIES before closing any of them.**
`gh issue view <n> --json body`. Do not close on a title match.

## The fix — address the job, not the agent

This is the **job-file-not-agent-file** principle the epic keeps rediscovering, applied to crew
addressing. A handoff's delivery target should be the **work-id and gate** —
`issue-467-trip-semantics / g4-review` — not an agent instance:

- the artifact path is **stable across every relaunch**; the agent name is not;
- the successor finds the result by reading its own work area, which it does anyway on cold start;
- it removes the reply-path problem entirely, because nobody has to name a live process.

Concretely: change the handoff templates' delivery instruction from *"SendMessage to
`<commander-name>`"* to *"write your result to `<work-area>/crew-handoffs/<gate>-<role>-result.md`
and announce completion"*. **The write is already required; only the announcement is misaddressed.**

## Pre-Rulings

1. **The shape above is the recommended one, overridable with a stated reason.**
2. **NOT OVERRIDABLE — the acceptance test must exercise a relaunch.** #507: *"Relaunch a Commander
   mid-gate, then complete a crew. The delivery must succeed."* Today it fails. **And note the trap
   the issue names explicitly: the current handoffs would still "pass" any check that only verifies
   the result file exists — the file always exists; it is the announcement that misroutes.** A check
   that only stats the file is a check that cannot fail.
3. **If instance-addressing is kept for announcements, the lineage-resolves-to-origin behaviour is a
   bug on its own** — the retired first instance is the least useful member of a lineage to deliver
   to. Note it in your return whether or not you fix it.
4. **Do not "fix" this by telling agents to try harder.** A doctrine sentence asking crews to guess a
   base name is what already happened, ad hoc, twice — and it worked only because the wrong recipient
   chose to be helpful.

## Honest-Null Clause

**A measured negative is a complete deliverable.** If the announcement genuinely cannot be made
job-addressed within the harness's dispatch model, say so with the evidence and report what the
nearest workable thing is. Do not ship a change you cannot demonstrate.

## Inherited Latitude

You may: choose the artifact path convention; edit handoff templates and the doctrine sentences that
describe them; add tests; open and push your PR; comment on all three issues. You may **not**: touch
`scripts/checklist_engine.py` or `tests/test_checklist_engine.py` (crew 4 owns them this wave);
edit `skills/<role>/references/global-*.md` — those are **install-time copies** that
`install_constellation.py` regenerates, so an edit there is silently overwritten; the canonical source
is `skills/_shared/global-*.md`.

## File Ownership

**Yours alone this wave:** crew handoff templates and the doctrine text describing crew delivery.

**Explicitly not yours:** `scripts/checklist_engine.py`, `tests/test_checklist_engine.py` (crew 4);
`scripts/verify_iterative_role_artifacts.py`, `COMMANDER_SPINE.template.json` (crew 1);
`scripts/install_constellation.py` (crew 2); `docs/CREW_CONTEXT.md`, `docs/TREND_SNAPSHOT.md` (crew 5).

Working notes: `notes-1.md`. **Never `findings-1.md`** — the harness `Write` tool refuses that basename.

## Workspace

- **Worktree:** `C:/Programs/constellation-skills-wt/epic418-w5-addressing` — **provisioned and verified.**
- **Branch:** `epic-418/w5-crew-addressing`, based on `ea854471`.
- All nine installed bundles were re-synced immediately before this dispatch.

## Inherited Context

- **This defect will bite F (#424) harder than it bit this wave.** F is the MCP front door — it is
  *about* the dispatch loop. Leaving crew addressing broken makes F harder to run and harder to
  measure. That is why a three-epic-old issue is in the final wave of this one.
- The cost scales with exactly the thing this project encourages: **a wave that relaunches its
  Commander — which a context trip makes routine — misroutes every crew delivery after the first
  relaunch.** #467 (merged last wave) makes trips *more* graceful and therefore *more* frequent.

## Budget

- **Model tier: Sonnet.** One fix, three closes, a well-understood mechanism.

## Stop Conditions

Stop and float if: the fix needs `checklist_engine.py`; any of the three issues does **not** collapse
against its body; or the relaunch acceptance test cannot be made to fail on today's code.

## Return Shape

Fixed / honest-null / blocked. **The relaunch acceptance test, shown failing on today's code and
passing on yours** — not just passing. For each of the three issues, whether you confirmed the
collapse against the body, quoted. PR number. Anything you did not do.
