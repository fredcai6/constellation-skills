# Implementer Handoff — g1: per-agent binding key in the store

**Work id:** issue-419-governor-identity · **Gate:** g1 · **Repo root / worktree:**
`C:/Programs/constellation-skills-wt/epic418-a-419` · branch `epic-418/a-419-governor-identity`

## Assigned task

Give the session-to-spine binding store a **per-agent outer key**.

Today `scripts/hooks/spine_rail.py` keys `.agent-work/.spine-rail-binding.json` on the harness
`session_id` alone. Agent-tool subagents **share their parent's `session_id`**, so every crew `claim`
piles another entry under one key; the gauge writer then sees more than one candidate, calls it
ambiguous, and writes nothing. That is why the context governor is silent on exactly the runs that
matter. Measured live in the main checkout: 6 session keys, 54 entries, one key holding 36.

Three pieces of work:

**(a) Pin the real captured payloads as a test fixture.** Copy
`.agent-work/issue-419-governor-identity/evidence/probe-payloads.jsonl` to
`tests/fixtures/probe_payloads.jsonl`, and add a test that pins its sha256 so a later hand-edit fails
the suite rather than silently weakening every test built on it. This converts the whole unit layer
from "a check over a dict I typed" into "a check over real harness output".

> **This will cost you a rework round-trip if you miss it:** each line in that file is a **wrapper** —
> `{captured_at, cwd, env, env_claude_keys, pid, raw, raw_len, payload}` — and the actual hook payload
> is nested under `payload`. Every test must unwrap it.

**(b) Two pure helpers in `scripts/hooks/spine_rail.py`.**

- `BINDING_KEY_SEP = "#"`.
- `binding_key(payload) -> str | None`. **Three-way, not two-way:**

  | payload | returns |
  |---|---|
  | `session_id` present, **no** `agent_id` | bare `session_id` — a top-level agent, behavior unchanged |
  | `session_id` + a **well-formed** `agent_id` | `f"{session_id}#{agent_id}"` |
  | `agent_id` **present but unusable** — empty, not a string, or containing `#`, `/`, `\` or `..` | **`None`** |
  | `session_id` falsy | **`None`** |

  `None` means **bind nothing**: the caller writes no entry at all.
- `session_view(binding, sid) -> dict` — the merged `{abs_spine_path: entry}` across the bare `sid`
  key and every key starting `sid + "#"`.

**(c) Route the call sites.** In `handle_post_tool_use`, the claim write, the release delete and the
empty-set cleanup all key off `binding_key(data)`. In `decide_stop` and `decide_session_start`, the
**reads** go through `session_view`.

## Protected intent

The point is that a reading can be attributed to the agent that produced it. `binding_key` is the
**single place** the composite key is composed anywhere in the codebase — the gauge writer (gate g2)
will call it through the `_spine_rail` module handle it already loads, so the two hooks cannot drift.
Do not add a second composer.

## Why the third case must bind nothing (do not "simplify" this)

A cold critic traced the damage path for the tempting two-way version, where an unusable `agent_id`
falls back to the bare key: that files the **subagent's** entry under the **parent's** key, pushes the
parent to two candidates, and silences the **parent's** gauge — manufacturing the exact blindness this
issue exists to remove. Fail closed instead: that subagent alone goes unbound and nobody else is
affected.

`agent_id` is interpolated into a filesystem path (`agent-{agent_id}.jsonl`) by the next gate, and it
is a harness field this repo does not own. The token check is a real failure mode, not decoration.

## Allowed scope

- `scripts/hooks/spine_rail.py`
- `tests/test_spine_rail.py`
- `tests/fixtures/probe_payloads.jsonl` (new)

## Specific exclusions

- **`scripts/hooks/gauge_writer_hook.py` is gate g2's.** Do not touch it.
- No change to `scripts/gauge_reader.py`, `scripts/checklist_engine.py`, or anything else under
  `scripts/`.
- No new module. No migration code — the store's **value** shape is untouched and only the outer key's
  alphabet widens, so a bare key and `bare#agent` are distinct keys and old and new writers coexist
  without collision.
- No change to `_foreign_worktree`, `_is_old_shape_binding_entry`, or the nudge ledger's shape.

## Constraints

1. **The nudge/escape-hatch ledger deletion on release keeps the bare `session_id`.** That ledger is
   documented as keyed by `session_id` alone and `decide_stop` writes it under the bare id; splitting
   it per-agent would weaken the three-strike hatch. **Put a comment at the code site** saying so, or a
   reviewer will read it as a missed substitution.
2. **The bind-on-resume write in `decide_session_start` stays under the bare `session_id`.**
   `SessionStart` never carries an `agent_id`, so a resumed session is by definition top-level. Only
   its **read** changes.
3. **The empty-set cleanup (`del binding[sid]`) is the single line where a wrong substitution deletes a
   live parent's entire binding.** It must delete the composite key's entry set, never the bare one.
4. Stdlib only. Windows-friendly. The hook must never raise and never block a tool call — every new
   path stays inside the existing fail-open discipline.

## Close criteria

1. `binding_key` implements the three-way table above exactly.
2. A claim carrying `agent_id` writes under `sid#agent_id` and leaves the bare `sid` entry set
   byte-identical. Two distinct `agent_id`s on one `session_id` produce two independent key sets.
3. A release carrying `agent_id` removes only that agent's entry.
4. A payload with an unusable `agent_id` writes **no** binding anywhere.
5. `decide_stop` and `decide_session_start` still see every spine they saw before.
6. Every existing test in `tests/test_spine_rail.py` passes **unedited**.

## Required evidence — read this section as the gate, because two of these are the whole point

- **The composition table, with counts stated.** All **6** real pinned payloads (2 subagent-scope with
  distinct ids, 4 with no `agent_id`), **plus at least 6 adversarial rows derived by mutating those
  real payloads**. Deriving adversarial rows is *not* the forbidden hand-injection — it proves
  *rejection*, not *delivery* — and it is necessary because the real capture contains zero malformed
  ids and zero falsy session ids, so the rejection branch is otherwise unreachable by any test.
- **The `session_view` settle must contain composite keys.** A cold critic caught the obvious test
  being vacuous: on a bare-key-only store the merge is the identity function, so the test passes in
  exactly the world where `session_view` ignores composite keys entirely. Build a store holding **one
  bare key and two composite keys**, state the entry count, and assert `decide_stop` blocks on a
  mid-flight spine held **only** under a composite key.
- A release under a composite key leaves `nudges[bare_sid]` untouched.
- `decide_session_start`'s bind-on-resume write still lands under the bare key.
- The empty-set cleanup removes the composite key and leaves the bare key's entries intact.
- The sha256 pin test on the fixture, and the 3/2/1 decomposition of the 6 payloads printed by the
  test itself (3 parent-scope Bash/Write calls, 2 subagent-scope, 1 parent `Agent`-dispatch — check the
  real decomposition and state what you actually find rather than trusting this line).

**A check that cannot fail is worse than no check.** Before you call a test done, ask whether it would
pass in a world where your change did nothing. If yes, it is not evidence.

## Test mode

Test-led where a test surface exists — it does here. `tests/test_spine_rail.py` is a pytest module.

## Required verification commands

```
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests/test_spine_rail.py -q
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests/test_gauge_writer.py tests/test_gauge_reader.py -q
```

**Use `python -m pytest`, never `py`.** The `py` launcher on this box resolves to a codex runtime with
no pytest installed; `py -m unittest discover` reports 15 red results that are all interpreter
artifacts. Baseline at HEAD `990712f`, clean tree: **1621 passed, 2 skipped, 550 subtests passed**.

## Inbound anchors

- **Structural:** `scripts/hooks/spine_rail.py` — `handle_post_tool_use` (~line 308), `decide_stop`
  (~419), `decide_session_start` (~503), `load_binding` (~103).
- **Constraint:** fail-closed — an unresolved identity binds nothing. Skip-on-uncertainty must not be
  weakened.
- **Decision (settled/measured, not yours to reopen):** identity comes from the payload's `agent_id`.
  The prototype's ~250-line discovery matcher **does not ship**. This was settled by a live probe on
  harness 2.1.222 and independently re-verified by a cold critic against the pinned payloads.
- **Confidence flag:** this repo has **no** `docs/architecture` map. `docs/GAUGE_WRITER_HOOK.md` is the
  nearest structural record and it is **known to be wrong** about the sidechain filter. Read the code,
  not the document.

## Stop conditions

Stop and return if: the change cannot meet a close criterion; you find you must edit
`gauge_writer_hook.py` to make g1 work; an existing test must be edited rather than added to; or you
conclude the three-way rule is wrong. Do not widen scope to fix something you find — record it as a
finding and return it.

## Authority

Delegated Commander `cmdr-419-governor-identity` under the frozen epic-418 launch order. Local commits
are fine; do not push, do not open a PR, do not file issues.

## Return format

`IMPLEMENTER_RESULT` at
`.agent-work/issue-419-governor-identity/results/g1-IMPLEMENTER_RESULT.md`, containing: what you
changed (file + what), the evidence above with real command output and **real exit codes**, every close
criterion marked met or not, anything you deliberately did not do, findings out of scope, and a
**Workflow Feedback** section (where the handoff, the corpus or the tooling fought you — a bare "none"
is not acceptable; if genuinely none, say what you checked).
