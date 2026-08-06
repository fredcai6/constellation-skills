# Reviewer Handoff — g1: per-agent binding key in the store

**Work id:** issue-419-governor-identity · **Gate:** g1 · **Worktree:**
`C:/Programs/constellation-skills-wt/epic418-a-419` · branch `epic-418/a-419-governor-identity`

## What was implemented

The session-to-spine binding store's **outer key** becomes per-agent. Today
`scripts/hooks/spine_rail.py` keys `.agent-work/.spine-rail-binding.json` on `session_id` alone, and
Agent-tool subagents share their parent's `session_id`, so every crew `claim` piles another entry under
one key and the gauge writer refuses to write against an ambiguous binding. Measured live: 6 session
keys, 54 entries, one holding 36.

Shipped in this gate: `binding_key()` (the sole composer), `session_view()` (a merged read across the
bare key and every composite key), those two routed into `handle_post_tool_use`'s claim/release/cleanup
writes and into `decide_stop`/`decide_session_start`'s reads, and the six real captured hook payloads
pinned as `tests/fixtures/probe_payloads.jsonl` with a sha256 test.

## How to inspect the diff

```
cd C:/Programs/constellation-skills-wt/epic418-a-419
git show --stat 340c46d
git diff HEAD~1 -- scripts/hooks/spine_rail.py tests/test_spine_rail.py tests/fixtures/probe_payloads.jsonl
```

The implementer's own account, including its evidence and its exit codes, is at
`.agent-work/issue-419-governor-identity/results/g1-IMPLEMENTER_RESULT.md`. **Treat every claim in it as
a pointer to evidence you reproduce yourself, never as an accepted fact.**

## Task statement the work was given

`binding_key(payload)` is **three-way**:

| payload | must return |
|---|---|
| `session_id`, **no** `agent_id` | bare `session_id` |
| `session_id` + **well-formed** `agent_id` | `session_id#agent_id` |
| `agent_id` present but **unusable** (empty, non-string, or containing `#`, `/`, `\`, `..`) | `None` — bind nothing |
| `session_id` falsy | `None` |

`session_view(binding, sid)` merges the bare key with every `sid#…` key.

## Close criteria — verify each, do not take them as read

1. The three-way table is implemented exactly, including the **bind-nothing** third case.
2. A claim carrying `agent_id` writes under `sid#agent_id` and leaves the bare `sid` entry set
   byte-identical; two distinct agent ids on one session produce two independent key sets.
3. A release carrying `agent_id` removes only that agent's entry.
4. An unusable `agent_id` writes **no** binding anywhere.
5. `decide_stop` and `decide_session_start` still see every spine they saw before.
6. Every pre-existing test in `tests/test_spine_rail.py` passes **unedited** — confirm none were
   changed, do not just confirm they pass.

## Where to look hardest

These are the places a cold plan critic predicted this gate would go wrong. Check them specifically.

- **The bind-nothing case is the one that matters.** If an unusable `agent_id` falls back to the bare
  key instead of returning `None`, the subagent's entry lands under the **parent's** key, pushes the
  parent to two candidates, and silences the **parent's** gauge — manufacturing the exact defect this
  issue exists to remove. Read the branch; do not infer it from a test name.
- **Is the `session_view` test vacuous?** On a bare-key-only store the merge is the identity function,
  so a test built only from bare keys passes in exactly the world where `session_view` ignores
  composite keys entirely. The evidence was required to use a store holding **one bare and two
  composite keys**, and to assert `decide_stop` blocks on a spine held **only** under a composite key.
  If it does not, say so.
- **The empty-set cleanup (`del binding[sid]`)** is the single line where a wrong substitution deletes a
  live parent's entire binding. Confirm it deletes the composite key's entry set and never the bare one.
- **The nudge ledger.** The implementer reports resolving an apparent contradiction in its handoff by
  making the ledger delete fire only for a top-level release (`if key == sid:`). **Adjudicate that
  reading.** Is it right that a subagent's release must not clear the parent's three-strike escape
  hatch? State your view; it is a judgement call the Commander wants a second opinion on.
- **The bind-on-resume write in `decide_session_start`** must still land under the bare key — only its
  read changed.
- **The fixture.** Each line of `probe_payloads.jsonl` is a wrapper with the real payload nested under
  `payload`. Confirm the tests unwrap it, and confirm the sha256 pin actually fails on a mutated
  fixture rather than merely existing.

## The standard that governs your verdict

**A check that cannot fail is worse than no check.** For every new test, ask whether it would pass in a
world where the change did nothing. The implementer claims to have measured this by reverting
`spine_rail.py` to HEAD and observing 13 of 16 new tests go red. **Reproduce that** — it is the single
most valuable thing you can check here, and if it does not reproduce, that alone is a BLOCK.

Any guard that loops must assert what it looped over and state the count.

## Allowed scope / exclusions

Review only `scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py`, and the new fixture.
`scripts/hooks/gauge_writer_hook.py` is deliberately untouched — it belongs to gate g2, and the
interim state (a subagent's gauge resolving to zero candidates rather than ambiguous-many) is expected
and is not a defect to report against this gate.

## Verification commands

```
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests/test_spine_rail.py -q
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests -q
```

**`python -m pytest`, never `py`** — the `py` launcher resolves to a codex runtime with no pytest, and
`py -m unittest discover` reports 15 red results that are pure interpreter artifacts. Baseline at HEAD
`990712f`: 1621 passed, 2 skipped. After g1 it should be **1637** — a count of exactly 1621 would mean
the new tests do not exist.

## Return format

`REVIEW_RESULT` at `.agent-work/issue-419-governor-identity/results/g1-REVIEW_RESULT.md` with a verdict
of **APPROVE** or **BLOCK**, each close criterion marked met or not with the evidence you personally
reproduced, findings (in scope and out of scope, separated), and a **Workflow Feedback** section — a
bare "none" is not acceptable; if genuinely none, say what you checked.
