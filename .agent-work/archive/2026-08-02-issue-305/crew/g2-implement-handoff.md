# Implementer Handoff — g2: the mechanical field composer

## Gate
`g2-implement`, issue #305, epic #298.

## The one-sentence job

Fill the **frozen** mechanical field group from engine state **with zero agent effort**, emitted as a snapshot at the same seam g1 built, so that **a run where the agent records nothing still yields the full group**.

The field group is not yours to design. `scripts/query_episodes.py`'s `_FIELD_READERS` already enumerates it exactly, and `scripts/apply_episode_delta.py::_validate_create` already enforces it. You are filling a contract, not authoring one.

## Field sourcing is ADJUDICATED — not your choice

| Field | Source |
|---|---|
| `run` | `cl["work_id"]` |
| `project` | **see the correction below — NOT `durable_root()`** |
| `role` | the lease's `claimed_by` |
| `spine-step` | `active_id(cl)` — **import the engine's selector, never re-derive it** |
| `context-manifest-ref` | `ctx-<work-id>-<step>@<rev>`, `rev` = `context_manifest.rev()` over the manifest's **own bytes** |
| `rework-count` | `task["rework_count"]` |
| `reopens` | successful `reopen` entries in the journal sidecar |
| `failed-commands` | evidence `type: command-output` with `payload.exit != 0` |
| `artifact-ref` | `_collect_changed_files()` (`checklist_engine.py:607`) — already repo-relative, matching the shipped episodes' shape |
| `refusals` | **needs a new engine counter — see below** |

`context-manifest-ref` satisfies `docs/EPISODE_STORE.md:679-689`'s `<manifest-ref>@<revision>` contract verbatim (*"pinning to its own blob hash at capture time"*). This is **why g1's write-if-absent is load-bearing**: a manifest that gets rewritten cannot be honestly pinned by revision.

Do **NOT** invent an `artifact-ref` evidence type. It has **zero occurrences across ~900 evidence items** and would create a second secretly-agent-dependent field — the exact class this issue exists to eliminate.

`reopens` and `failed-commands` survive a refusal because the evidence item is appended **before** the raise and `main()` persists on the error path.

## CORRECTION 1 — `project` must NOT use `durable_root()`

The plan originally said `project = Path(durable_root()).name`, reasoning that `durable_root()` yields the main checkout so `project` stays stable across epics.

**That is wrong, and I measured it rather than reading it.** `durable_root()` returns the worktree **unchanged** whenever an active Admiral epic lease exists — `agent_work_root.py` says so itself: *"the main checkout is fenced read-only, so honor the worktree."* **That is the condition every commander in this epic runs under.** Measured here:

```
durable_root(cwd)      -> C:/Programs/constellation-skills-wt/e298-305  -> project 'e298-305'
git-common-dir parent  -> C:/Programs/constellation-skills             -> project 'constellation-skills'
```

Corroborated by a real emitted manifest — `.agent-work/issue-305/context/g1-review.json` has `run.roots.durable` pointing at the worktree.

**Use the parent of `git rev-parse --git-common-dir`, resolved absolute, basename.** It is correct on all three topology paths (linked worktree → main checkout's `.git` regardless of lease; plain checkout → `.git` whose parent is the root; unaffected by leases entirely) because it asks git about **repository topology** rather than asking the work-area helper about **writability**. Different questions; this field wants the first.

**Fallback must REFUSE, not guess.** If git is absent or the directory is not a repository, refuse to emit `project`. A worktree-derived project silently poisons the one join meant to survive worktree deletion.

**Prove it the way it was missed:** the stability test **must run from a linked worktree under an active epic lease**, because that is the *only* condition under which the old formula was wrong. A test exercising only a plain checkout **passes on the broken formula** — that is exactly how this defect was going to ship. Cover both sides.

## CORRECTION 2 — `refusals` IS in scope, with four non-negotiable conditions

The Admiral ruled it in. Today the field has **no engine-state source**: a refusal raises `EngineError`, `main()` catches it (`checklist_engine.py` ~:2582) and **does** persist `cl`, but records nothing about the refusal. The journal sidecar cannot cover it — it is documented and implemented as **success-only**, with `append_journal_entry` sitting after the `return 1`. So `refusals` is today *secretly agent-dependent*, which `decision:zero-agent-effort-is-literal` forbids.

**Add the counter on `main()`'s `except EngineError` path, which already calls `save()`.** Four conditions:

1. **ADDITIVE ONLY.** No existing field changes meaning; no existing reader breaks on a checklist that lacks the counter. Construct a checklist saved *before* the counter existed and prove every reader still works.
2. **`docs/CHECKLIST_SCHEMA.md` updated in THIS SAME PR.** Non-negotiable — a schema change shipped with a stale doc is the exact defect #309's sweep found live. Not a follow-up.
3. **Prove the counter can be WRONG, and prove that test can FAIL.** Induce a real refusal, assert the counter incremented to the *specific* expected value, then break the increment and confirm the test goes red **on that specific assertion** — not merely non-zero exit, which an import error also produces. And cover the case a one-sided test misses: **induce a SUCCESSFUL verb and assert the counter did NOT move.** A counter that increments on everything passes a test that only ever checks it increments.
4. **STATE THE LATENCY in your result.** The engine change is latent until the installed corpus is refreshed (#344). Say so plainly; do not engineer around it.

## Also correct `docs/EPISODE_STORE.md:781`

It currently says *"#305 wires automated capture — nothing writes to this store on its own yet"*, which promises something the store's own validator **forbids**: `_validate_create` requires all five agent-supplied assertion kinds with non-empty statements, so a complete episode **cannot** exist without agent judgment.

The Admiral's adjudicated reading: **#305 delivers a mechanical snapshot, not auto-created episodes.** The acceptance criterion says *"the full mechanical **field group**"*, not a complete episode. Rewrite that line so a reader of `main` sees the true division: the mechanical half falls out of the engine with zero agent effort; the judgment half stays agent-initiated because it is irreducibly judgment.

## REFUSE, NEVER FABRICATE

If any field cannot be honestly sourced, the assembler **refuses** rather than emitting a silent `0` or a plausible default. **A fabricated mechanical fact is worse than an absent one.**

## The defect class your reviewer will hunt — build against it now

**A composer that returns plausible constants and reads no engine state would pass a presence-based check.** `_validate_create` is `isinstance(str) and value.strip()` for strings and `isinstance(int) and >= 0` for ints — nine hardcoded constants pass it, and so does a delete-one-field red-proof, because deleting a key from a dict is independent of how the dict was filled. **`validate_delta()` is a shape check on the way to the writer. It is NOT an oracle.**

So: for every field, construct a run where the **true value is non-default** (a real reopen, a real failed command, a real refusal) and confirm the composer *tracks* it rather than returning a constant that happened to match.

## Constraints

- Work ONLY in `C:/Programs/constellation-skills-wt/e298-305`. **Never touch `C:/Programs/constellation-skills`** — it holds the human's uncommitted work.
- **Do not modify** `scripts/episode_capture.py`'s seam logic, the emit call sites, or `tests/test_episode_capture.py`. g1 is closed and reviewed.
- Additive only on the engine — other commanders are live on it.
- `python -m pytest` (3.14.3 / pytest 9.0.2); `py` is 3.12.13 with **no pytest**. Neither reproduces CI.
- Explicit `encoding='utf-8', newline='\n'` on every write. `Path.read_text(newline=...)` is 3.13+ and **fails CI**.
- Compare normalized content or blob OIDs, **never raw working-tree bytes** (#319).
- Full suite is currently **1436 passed, 2 skipped, 471 subtests**. Run it before declaring done.

## A lesson from this run's own g1, so you do not repeat it

A postcondition meant to verify *"the engine diff is an import plus two call sites and nothing else"* was implemented as `git diff --stat` — **a command that exits 0 no matter what the diff contains.** It could not fail. **Every check you author must be able to go red, and you must show it going red.** A revert-based red proves your assertion matches the tree; only a genuinely *novel* input proves your check parses anything.

## Return

Write `IMPLEMENTER_RESULT` to `.agent-work/issue-305/crew/g2-implement-result.md` — what changed, evidence with **pasted real output** (including every red proof), close-criteria disposition, the #344 latency statement, blockers, and a blunt `Workflow Feedback` section. Your final message must contain the same content.
