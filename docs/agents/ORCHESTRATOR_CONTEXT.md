# Orchestrator Context — project deltas

## Project Purpose

Continuously improve the active Constellation Skills corpus for clarity and proven effectiveness in real projects.

## Operating Context

**Primary users:** humans and agents using the installed skill corpus in active projects.  
**Output authority:** mixed — skills and their enforced workflow mechanisms are durable operational tooling; feedback is advisory.  
**Failure consequences:** unclear or ineffective guidance, broken workflow mechanics, or lost learning from real work.

## Subsystem Rigor

| Subsystem | Rigor profile | Execution context | Orchestrator implication |
|---|---|---|---|
| Workflow mechanisms and verifiers | strengthened durable system | runtime/test infrastructure | Plan targeted automated verification plus the relevant broader suite. |
| Post-job feedback | pragmatic internal learning loop | reporting | Keep collection light and non-blocking; use real-project feedback, never invented projects, as the effectiveness signal. |

## Repo Action Authority

- Local commits: allowed.
- Pushes, pull requests, and merges to `main`: require explicit human approval, unless the human has pre-approved the action for the specified work.

## Evidence And Verification Map

| Area | Required evidence | Handoff implication |
|---|---|---|
| Mechanism or workflow behavior change | targeted automated tests plus relevant broader suite | name both commands; a genuine no-test-surface exception needs rationale |
| Skill effectiveness | feedback collected from agents after real project work | do not fabricate representative projects or turn feedback into a completion gate |

## Project Engineering Rules

- Solicit lightweight, freeform post-job feedback (“how did it go?”); prompt for positives and negatives where useful.
- Feedback is advisory and may be brief or absent. Record it when available; do not require immediate interpretation or a per-item disposition.

## The Retired Learning Playbook

`.agent-work/LESSONS.md` and `.agent-work/AGENT_FEEDBACK.md` are **retired** (#447). This
section is doctrine, not a changelog: it binds you even if the instruction that sent you
looking for one of those files never mentioned any of this.

- **`episodes/` replaces both.** One store of observations — not two inboxes plus a
  playbook. Its only write path is `scripts/apply_episode_delta.py`.
- **An episode is a record of what happened, and is never read back as a rule.** Write what
  you observed. Do not write, and do not obey, an instruction that has an agent consult the
  store and condition its behaviour on what it finds there.
- **A rule to follow belongs in `docs/agents/*`, and putting one there is a human's call.**
  Observing something that feels like a rule is not authority to promote it into doctrine.
  Record the observation and say so; the human decides.
- **There is to be no successor playbook and no read-and-apply loop.** A new file that
  accumulates distilled advice for future agents to consult is this retirement undone,
  whatever it is named and wherever it sits. If you find yourself creating one, stop and ask
  the human instead.
