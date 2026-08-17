# Constellation Skills — Crew Context

**Audience / tier: crew.** Implementer, Reviewer and Prototyper — the roles that execute a
bounded task from a handoff. Orchestrator-tier content (planning authority, gate policy,
map reading, evidence strategy) belongs in `ORCHESTRATOR_CONTEXT.md`, not here, and content
every agent touching the repo needs belongs in the auto-loaded `CLAUDE.md`. Placing content
at a broader tier than its audience is a defect, not a delivery win.

**Project deltas over inherited global doctrine.** Implementation/review discipline,
required handoff fields, the result-is-the-deliverable rule, fail-visibly posture and the
generic block/stop criteria are inherited from the skills' `references/global-crew.md` +
`references/global-everyone.md`. This file carries only constellation-skills rules that
change implementation or review.

---

## Python Invocation

Which interpreter name has pytest installed varies by host — do not assume the previous
host's answer holds on this one. Check before you run anything that matters:

```bash
which py python python3
py --version && py -m pytest --version
python --version && python -m pytest --version
python3 --version && python3 -m pytest --version
```

One of these will run pytest; at least one other will fail with `No module named pytest`
and read as a silently green run if you don't check first. Use whichever name actually
answers with a pytest version on this host.

Measured on this host on 2026-08-10: `py` and `python` both resolve to
`/home/tommy/.local/bin/{py,python}`, both report Python 3.12.3, and both have pytest
9.1.1. `python3` resolves to `/usr/bin/python3.12`, also Python 3.12.3, but has no pytest
installed. None of this is guaranteed to match CI's pin — a local green is evidence,
never the gate.

---

## Writing Files On Windows

Pass `encoding='utf-8', newline='\n'` explicitly on **every** write. The default encoding
here is not UTF-8 and the default newline translation produces CRLF, which shows up later
as spurious diffs and as byte-level comparison failures. **The sanctioned exception:**
`scripts/checklist_engine.py`'s `save()` writes bytes directly and preserves whichever line
ending the target file already has instead of forcing `\n` — a byte-faithful writer earns
the same trust this rule protects, so it satisfies the rule's intent without its literal
mechanism.

`.gitattributes` sets `* text=auto`, so a checkout may legitimately hold CRLF while the blob
holds LF. **Never compare two files by raw working-tree bytes** — compare normalized content
or blob OIDs. A comparison that hashes working-tree bytes is silently wrong on Windows.

MAX_PATH is real. Prefer short paths under deeply-nested work areas.

---

## Record Stores Are Never Hand-Edited

Two stores in this repo are written **only** through their validated delta writers. An LLM
or a human editing them directly is a defect regardless of how correct the resulting text
looks — the writers enforce partition allowlists, mandatory reasons, single-line values and
all-or-nothing application.

| store | the only write path |
|---|---|
| `episodes/` | `scripts/apply_episode_delta.py` |
| any checklist (`spine.json`, `execute.json`, survey files) | `checklist_engine.py` verbs |

Retiring an episode **moves its file** between `episodes/active/` and `episodes/retired/`;
membership is the directory, never a parsed `status` field. That move is a write like any
other and goes through the writer above.

---

## Editing The Skill Corpus

Edit the canonical shared doctrine at `skills/_shared/global-*.md`. **Never** edit the
per-role copies under `skills/<role>/references/` — `scripts/install_constellation.py`
regenerates those, so an edit there is silently reverted at the next install.

---

## Two Engines Are Alive In Your Session

When your task touches engine or hook code (`scripts/checklist_engine.py`, `scripts/hooks/*`,
the MCP door), there are two copies of it alive in your session and they are not the same:

- **The copy you are RUNNING.** Hooks and your own survey state execute from the main
  checkout — `CLAUDE_PROJECT_DIR` resolves once at session launch (#269), so this holds even
  when your shell sits in a worktree.
- **The copy you are EDITING.** Your worktree's files, which nothing in your live session
  executes until you deliberately run them.

The rule: **drive the installed/main copy; edit and break the worktree copy.** Concretely:

- Validate changed hook or engine code **in a fresh process with an explicit path** — never
  by watching your own session's hooks fire. Your session runs the old code; a green turn
  after your edit is evidence of nothing.
- When a review's red-proof requires breaking the engine, break the **worktree** copy. Your
  own survey state lives in the copy you're driving; breaking that one corrupts your run.
- Keep your spine, lease and gauge traffic on the engine you're driving, not the one under
  edit.

---

## Verification Discipline

These are the rules that most often separate an accepted change from a reworked one here.

- **A check that cannot fail is indistinguishable from one that passed.** Before you offer a
  check as evidence, demonstrate it can reach a failing state — run it against the
  pre-change tree and show it red, or mutate the thing it guards and watch it go red, then
  restore. If you mutate, **assert the mutation actually applied**; a `sed` that silently
  matched nothing leaves a green suite that reads exactly like a passing guard.
- **Assert against behaviour, never against text that describes it.** Docstrings,
  `description=` fields, imperative prose and human-readable summaries are hand-authored and
  none is checked against what runs. A grep for a message string is not a test of the branch
  that emits it — especially when the message is built by an f-string, where the literal
  never appears in the source at all.
- **Any guard that loops must assert what it looped over.** A grep, glob or comparison over
  a set that turns out empty reports clean without ever examining an interesting item. Print
  or assert the count.
- **Define a guard by its consumer's behaviour, not by a hand-maintained list.** A list of
  characters, filenames or call sites drifts from the predicate the code actually applies,
  and the gap is silent. Express the guard as the property the consumer itself computes.
- **A round-trip test over the real shipped artifacts proves the artifacts are clean — it
  does not prove the tool is correct.** Pair it with adversarial fixtures authored to make
  the tool return a *wrong* answer: a false FAIL on valid input, a silent PASS on invalid
  input.

---

## Evidence You Owe Back

- Name the exact commands you ran and paste their real output, including exit codes. A
  Commander re-runs them; a summary that does not reproduce is a blocker.
- Report a measured negative as a complete result. "This specific check failed" is a finding;
  "this approach is impossible" is not a report a crew is positioned to make.
- Anything you found that is real but out of your task's scope goes back as a triage
  candidate rather than being fixed silently or dropped.
