# IMPLEMENTER HANDOFF — issue-305 gate g1: assembly seam

## Assigned task

Make the #300 context manifest a **byproduct of starting a spine step**, so it is produced by
the act of an agent activating a step and there is no separate act anyone can forget.

Emit from `checklist_engine.start()` and `checklist_engine.reopen()` — **the two and only two
sites in the module that set `status = "in-progress"`** (`:1635` and `:1852`), which
`advance()` at `:1644` requires (`if t["status"] != "in-progress": raise EngineError(...)`).

**Why these two sites and not the `dispatch()` chokepoint.** On a gated spine every gate that
ever advances must first be started — the engine's own status machine enforces it, not agent
goodwill. So `start`/`reopen` already gives unskippability with **one verb** of blast radius
instead of every verb. This matters concretely: two other commanders are live on this engine
right now. It is also semantically the correct seam — `context_manifest.py`'s own docstring
says the manifest records *"these files were made available to the agent running **this
step**"*, and emitting at step activation is exactly that.

## Protected intent

`decision:manifest-is-a-byproduct` — *assembly emits the manifest; nothing calls a "write the
manifest" step.* `@grade: settled/human`. If producing the manifest is something a capture path
**calls**, it will be skipped somewhere. If it is something activation **emits**, it cannot be.

## Allowed scope

- **NEW** `scripts/episode_capture.py` — all logic lives here.
- `scripts/checklist_engine.py` — an import and **one call per site** (two calls). Nothing else.
- **NEW** `tests/test_episode_capture.py`.

## Specific exclusions

- Do **not** touch `scripts/apply_episode_delta.py` or `scripts/query_episodes.py`. Frozen
  contracts.
- Do **not** touch `dispatch()`, `main()`, or any other verb. The refusal-counter question is a
  **different gate (g2)** and is pending an Admiral ruling — do not anticipate it.
- Do **not** remove `run.dirty` — that is g4.
- Do **not** add a CLI flag for roots. A flag shifts the zero-effort burden onto the invoker.

## The design, already adjudicated — implement it, do not redesign it

**Write-if-absent, never overwrite.** The manifest is a per-step **delivery snapshot**. If a
later verb rewrote it, it would become "whatever was available at the last verb call" and
destroy the record it exists to be. This is also load-bearing for g2: `EPISODE_STORE.md:679-689`
requires `context-manifest-ref` to be `<manifest-ref>@<revision>`, and explicitly names *"a
live-mutating index with no historical snapshot"* as a contract violation requiring a float.
Write-if-absent is what makes the pin honest.

**Roots, resolved mechanically:**

| Token | Source | Why |
|---|---|---|
| `repo` | worktree root | `docs/agents/ORCHESTRATOR_CONTEXT.md` etc. resolve here |
| `durable` | `agent_work_root.durable_root()` — the **CHECKOUT ROOT** | **Not** `durable_agent_work()`. The one shipped declaration is `{"root":"durable","path":".agent-work/LESSONS.md"}` (`COMMANDER_SPINE.template.json:31`); the wrong helper returns `<root>/.agent-work` and double-nests it to `.agent-work/.agent-work/LESSONS.md` |
| `skill` | the installed skill dir (parent of `scripts/`) | where `references/global-*.md` live |

The double-nesting trap is not hypothetical and it is **silent**: `read_bytes` returns `None`
for a missing file and `rows()` records `rev: null` without raising, so a wrong root ships a
plausible-looking manifest and every check goes green. Assert the **resolved absolute path**,
not the code.

**Fail-soft but NOT silent.** The emit must never change any verb's exit code or output —
`build_manifest()` legitimately raises `ValueError` when every item is terminal (`active_id`
is `None`), and a crash here breaks every verb for every concurrent commander. So catch
broadly; this is a deliberate, documented exception to narrow-except style, and say so in a
comment.

**But a swallowed failure must not vanish.** On a failed emit, write a **stub manifest
recording the failure** (what failed, and that it failed) instead of writing nothing. Inherited
doctrine, and my launch order names it: *a non-reading must be visibly distinct from an
uncollected one*. "No manifest" and "manifest failed" must be tellable apart by a later reader.

## Close criteria

1. Starting a step whose task declares `context_refs` writes a valid manifest at
   `context_manifest.manifest_path(...)`; `reopen` does the same.
2. An already-present manifest for that step is **not** overwritten.
3. No verb's exit code changes, across at least: a fully terminal checklist, a declaration
   naming a root the caller did not map, and a directory that is not a git repo.
4. `durable` resolves so `.agent-work/LESSONS.md` lands at the checkout root — asserted on the
   **resolved path**.
5. A failed emit leaves a failure-recording stub, not silence.
6. `scripts/checklist_engine.py` diff is an import plus two call sites. Nothing else.

## Required evidence

- The resolved absolute path for each of the three root tokens, printed from a real run.
- A manifest produced by a real `start` — pasted, showing non-null `rev` on at least one row,
  so the test is not passing over an all-null manifest.
- Exit codes for the three fail-soft cases.
- A before/after showing the write-if-absent behavior (second `start` does not change the file).

## Verification commands (POSIX form, absolute paths)

```sh
cd "C:/Programs/constellation-skills-wt/e298-305" && python -m pytest tests/ -q
cd "C:/Programs/constellation-skills-wt/e298-305" && python -m pytest tests/test_episode_capture.py -q
```

## Constraints

- **Windows:** explicit `encoding='utf-8', newline='\n'` on every write. `Path.read_text(newline=...)`
  is **3.13+** and passed locally then failed CI on PR #320 for 39 tests — do not use it.
- **Python:** `py` is 3.12.13 (CI's pin) with **no pytest**; `python` is 3.14.3 with pytest.
  Run tests with `python -m pytest`. **Neither reproduces CI — a local green is never the gate.**
- Do not import `subprocess` into `context_manifest.py`; it has a guard test asserting its own
  source never contains that identifier. `episode_capture.py` is a different file and is free.
- A round-trip test over shipped artifacts proves the **artifacts**, not the tool. Pair every
  such test with adversarial fixtures authored to make the tool return a **wrong** answer.

## Stop conditions

Stop and return to me if: the seam turns out not to be unskippable (i.e. you find a path to
`advance` that never passes `start`/`reopen` — that would invalidate the gate's premise and is
exactly the kind of finding I want, not a failure); the engine diff cannot stay at two call
sites; or the fail-soft rule and the not-silent rule turn out to conflict irreconcilably.

## Return format

`IMPLEMENTER_RESULT` with: verdict, files changed, the evidence above pasted (not summarized),
what you did NOT do, and a **Workflow Feedback** section — blunt, including anything in this
handoff that was wrong or that cost you time.
