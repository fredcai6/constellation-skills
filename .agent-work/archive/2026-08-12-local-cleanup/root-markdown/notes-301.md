# notes-301 — working notes, commander-301 (epic-298)

Named `notes-301.md`, never `findings-301.md` — the harness `Write` tool refuses any path
whose basename contains "findings", per the launch order's File Ownership note.

## Where the run stands

Spine driven `init → context → understand → plan` (all complete). Stopped **before** `execute`
at the launch order's own expected mid-mission return: the design-it-twice convergence choice
is a float, and `decision:convergence-is-human` says do not self-converge and proceed.

`execute.json` is frozen with 10 tasks / 3 crew gates, and its first task `e0-context` carries
a deliberate precondition p1 requiring a ratification record before g1 may start.

## Artifact index

| What | Where |
|---|---|
| Problem statement | `.agent-work/301/evidence/problem-statement.md` |
| Mission frame | `.agent-work/301/evidence/mission-frame.md` |
| Design brief (shared, 4 candidates read it) | `.agent-work/301/design-it-twice/BRIEF.md` |
| Candidates A–D | `.agent-work/301/design-it-twice/candidate-*.md` |
| Comparison + recommendation (**read §0 first**) | `.agent-work/301/design-it-twice/COMPARISON.md` |
| Both cold-critic dispositions | `.agent-work/301/evidence/plan-critic-disposition.md` |
| Frozen gate plan | `.agent-work/301/execute.json` |
| Crash-resume note | `.agent-work/301/STATE_NOTE.md` |
| Staged durable trio (Admiral harvests) | `.agent-work/staged-feedback/301/` |
| Verdict | `.agent-work/verdict-301.md` |

## The two things a successor must not re-learn the hard way

1. **COMPARISON.md was wrong once.** Its first version claimed six unanimous panel decisions;
   two were manufactured and a third overstated. §0 records the errors and the commands that
   disproved them. Do not read §1 without §0.
2. **pytest runs under `python`, not `py`** on this host. `py -m pytest` reports
   "No module named pytest", which reads like a broken suite. Baseline at `b69e6c8`:
   1157 passed, 2 skipped.

## Open threads

- Awaiting the Admiral's ruling on the convergence float (record shape + retirement mechanism).
- `g3-integrate` c4 requires re-checking the context-field obligation against **#300's merged**
  manifest shape, with an explicit defer-and-flag branch if #300 has not merged yet.
- Filed to the tracker this run: **#313** (`py -m pytest` false-red), **#314** (delegated
  Commanders cannot use the SendMessage delivery contract doctrine prescribes).
