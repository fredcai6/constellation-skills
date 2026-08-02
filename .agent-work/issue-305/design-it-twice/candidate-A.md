# Candidate A — "One seam, one optional second seam"

Constraint: **MINIMUM ENGINE SURFACE.**

> Persisted by commander-305. The authoring agent ran under a read-only planning toolset
> and could not write files; it returned the document in its result message and declined
> to work around the restriction via shell redirects. Text below is its output, verbatim
> in substance. Its line-number claims were independently re-verified by commander-305
> before this candidate was weighed — see the convergence note at the foot.

## 1. The seam, and why it's the assembly point

**Seam: `checklist_engine.py:dispatch()`, the `if v == "current":` branch (verified at
lines 2387–2391 in this worktree, not `main()`'s 2549–2585 as `MISSION_FRAME.md`
approximates — `main()` only calls `dispatch()` and conditionally persists; the actual
verb branching, including `current`, lives in `dispatch()`).**

```python
if v == "current":
    message = current(cl) + _trip_advisory(cl, base_dir)
```

This is where `render_human(state(cl))` — the act of handing an agent its step briefing —
actually happens (`current()` itself, lines 1603–1604, is `return render_human(state(cl))`).
It is the one place that is:

- reached by **every** read of the plan, by construction (`current` is the only way an
  agent learns what to do next),
- **read-only for spine state** — `main()` never `save()`s on `args.verb == "current"`
  (lines 2558, 2573), so a manifest write here mutates no engine-owned JSON, only the
  separate file `context_manifest.manifest_path()` already names,
- already carrying `base_dir` as a parameter, which is what any filesystem-facing side
  effect needs.

Engine diff for this seam: one `import episode_capture`, one call
`episode_capture.emit_current_manifest(cl, base_dir)` inserted after computing `message`.
All roots-resolution, error-swallowing, and field logic live in a new module
`scripts/episode_capture.py`.

**Non-negotiable property: it must never change `current`'s exit code or output.**
`dispatch()` has no try/except around the `current` branch, and nothing upstream in
`main()` catches non-`EngineError` exceptions on this path — an uncaught `OSError`/
`ValueError` from a naive `produce()` call would crash a verb all three concurrent
commanders rely on. So `emit_current_manifest` catches broadly (`except Exception`), a
documented exception to narrow-except style. This matters concretely: `build_manifest()`
raises `ValueError` when `active_id(cl) is None` (checklist fully terminal) — a real,
common case that must still exit 0.

## 2. Roots resolution — mechanical, not a new CLI flag

`produce()` needs `roots: {skill, repo, durable}`. None exist as engine state today. A new
CLI flag would mean the agent must remember to pass it → violates zero-agent-effort. So,
derivation, entirely inside `episode_capture.py`, zero engine surface:

- `repo` — `git rev-parse --show-toplevel` with `cwd=base_dir` (git discovers upward;
  `base_dir` is the checklist's own directory, a subdirectory of the repo, not the root).
- `skill` — `Path(__file__).resolve().parent.parent`, co-located with `checklist_engine.py`
  in `<skill-dir>/scripts/`. Verified against the served install.
- `durable` — `agent_work_root.durable_agent_work(repo_root)`, existing and tested,
  already handling the linked-worktree/Admiral-lease flip.

## 3. Gate list

Exit-code vocabulary for every check: **0 = pass, 3 = genuine red, 4 = fixture/setup
failure**. Never 1 or 2 (argparse misuse, unhandled traceback), so the only signal that
survives is never ambiguous between "the subject is broken" and "the check is broken."

**G1 — Byproduct seam.** `dispatch()`'s `current` branch calls
`emit_current_manifest(cl, base_dir)`.
Close: (a) `git diff --stat -- scripts/checklist_engine.py` ≤ 3 changed lines. (b) `current`
against a fixture whose active step declares `context_refs` exits 0 AND leaves valid JSON at
`manifest_path(...)`. (c) Against a fixture with no `active_id`, exits 0 with no manifest
write.

**G2 — Roots are mechanical.** No new CLI flags for roots. Close: `current` from a cwd other
than the repo root still resolves correctly; a fixture engine at `<tmp>/scripts/` resolves
`skill:` to `<tmp>`.

**G3 — Fail-soft.** Production never changes `current`'s exit code across: terminal
checklist, uncovered root (`DeclarationError`), and not-a-git-repo. Close: exit 0 in all
three. One fixture runs from **outside any git repo**.

**G4 — Mechanical field assembler.** New `episode_capture.mechanical_fields(cl, base_dir,
journal_path)`. Field sourcing:

- `run` = `cl["work_id"]`; `project` = `Path(repo_root).name`;
  `role` = `cl["engine_session"]["claimed_by"]`; `spine-step` = `active_id(cl)` (the one
  selector, imported, never re-derived); `context-manifest-ref` = `str(manifest_path(...))`.
- `rework-count` = `cl["tasks"][active_id]["rework_count"]` — scoped to the **active** step.
- `reopens` = count of journal lines with `verb == "reopen"` — **whole run**. A deliberate
  asymmetry with `rework-count`, inferred from the two distinct field names and sources; not
  confirmed against `EPISODE_STORE.md` prose. Flagged as an assumption.
- `failed-commands` = evidence items across all tasks with `type == "command-output"` and
  `payload.exit != 0` (appended *before* the raise, so it survives the refusal path).
- `artifact-ref` = for each task's `artifact`-kind postcondition that is satisfied,
  `"<task-id>.<evidence_type>#<satisfied_by>"`. Chosen over parsing a `path` key because
  evidence payload shape is freeform and there is no universal path field in the schema.

**G5 — Refusal recording (the float).** `main()`'s `except EngineError` branch gains one
line: `cl["refusal_count"] = cl.get("refusal_count", 0) + 1`, before the existing
`save(path, cl)`. `current` never enters this branch, so this is provably disjoint from G1.
Close: a fixture triggering a refusal leaves `refusal_count == 1`; a second leaves 2.
*Disposition if ruled out of scope:* `mechanical_fields()` **refuses** (raises, does not emit
`0`) when it cannot find the counter — a silent `0` would misrepresent a run that actually
got refused, exactly the failure class the negative control exists to catch.

**G6 — `run.dirty` removal.** `context_manifest.py`-only, zero engine touch. `run_facts()`
drops the parameter and key; `build_manifest()` stops reading `state.get("dirty")`; the
~10 assertions in `tests/test_context_manifest.py` referencing `m["run"]["dirty"]` updated in
the same gate, along with the stale docstring prose. `CONTENT_KEYS` unchanged — `dirty` was
never content.

**G7 — #300 AC1 now has a domain, and can fail.** Run against
`skills/commander/templates/COMMANDER_SPINE.template.json`'s real `context` step (the one
real spine that already declares `context_refs`) — green after G1. Then run the identical
check against the **pre-#305** engine materialized to a scratch path — must go red. Same
fixture, same script, both times. Exit 0 then 3.

**G8 — Negative control, and proof it can fail.**
*Green:* drive a fixture through `claim → start → attest → advance` with real command
postconditions, recording nothing beyond what postconditions mechanically require. Run
`mechanical_fields()`, wrap as a `create` op, feed to `apply_episode_delta.validate_delta()`
— **the real writer's own validator, reused as the oracle rather than reimplemented**.
Assert no error.
*Red-proof:* take the same green output, delete exactly one mechanical field at a time
(loop over all 9 required scalars), re-validate, assert `EpisodeDeltaError` **is** raised for
every one. If any field's absence does not raise, that field is a vacuous check — the class
this epic has hit four times — and the gate names it.
*Honest gap:* `artifact-ref` cannot be exercised this way — it is list-shaped and optional
(`_validate_create` defaults it to `[]`), so an empty list is definitionally valid. The
control has no red case for this one field. Disclosed, not hidden.

**G9 — End-to-end round-trip.** G8's green delta with real `agent_supplied` text → real
`apply_episode_delta.py --delta` against a scratch `--store-root` → `query_episodes.py`,
confirming all 11 `_FIELD_READERS` read back what G4 asserted.

## 4. What I deliberately did not do

- Did not redesign the writer, the field group, or the store layout. G8 reuses the real
  validator as oracle specifically so a future field-group change surfaces as a failure
  rather than silent drift.
- Did not wire automatic episode **creation**. #305 makes the mechanical bin available with
  zero effort; it does not make creation itself a byproduct — that needs the agent-supplied
  bin, which is real judgment.
- Did not add CLI flags for roots — a flag shifts the zero-effort burden to the invoker.
- Did not build a `role` fallback for lease-less runs.
- Did not make `reopens`/`failed-commands` scoping configurable.

## 5. Honest weaknesses under my own constraint

1. **Two engine touch points if G5 lands, not one.** G1 is read-only and low-risk; G5 sits
   on the shared `except EngineError` path hit by every mutating verb in every skill —
   inherently higher blast radius even at one line. Weakest point under a literal reading of
   the constraint; a stricter reviewer could demand G5 be its own issue.
2. **`role` has no fallback.** For a run with no active lease (legal), `role` is
   unresolvable and the assembler refuses rather than guessing. This silently narrows
   "complete for engine-driven runs" to "complete for *leased* engine-driven runs" — a
   narrowing not signed off.
3. **`artifact-ref` under-captures.** Only postcondition-satisfying artifact evidence is
   surfaced; a free-floating attached item is invisible though genuinely in engine state.
4. **`reopens` vs `rework-count` scoping is inferred, not confirmed.**
5. **No concurrency/atomicity story.** `write_manifest()` does a plain `open(..., "w")`, not
   an atomic rename. Parallel agents against a shared spine can interleave.
6. **G8's green fixture has zero refusals by construction** — it cannot distinguish
   "refusals correctly 0" from "refusals silently absent." The real proof is G5's own
   deliberately-refused fixture, not G8's.

## 6. How I'd know this was the wrong choice

- If a reviewer flags G5 as touching too hot a shared path, split it into its own issue —
  narrow, isolated, doesn't invalidate the rest.
- If `_validate_create`'s allowlist changes upstream, G4/G8 fail loudly (G8 calls the real
  validator) rather than silently pass — intended failure mode, not wrongness.
- If concurrent writers to the same manifest path matter in practice, the missing atomic
  write is the concrete signal the byproduct mechanism is wrong.

---

## Convergence note (commander-305, added after weighing both candidates)

Candidate A's structural correction is **confirmed at source**: `dispatch()` is at
`checklist_engine.py:2375` and the `current` branch at `:2387`. `MISSION_FRAME.md`'s
"assembly seam" address was the *persist* point, not the branch. The frame is corrected.

Candidate A's central premise — *"`current` is the only way an agent learns what to do
next"* — is **false**, and candidate B is what caught it. `RAIL_VERBS =
{"claim", "current", "start", "advance", "attest", "attach"}` (`checklist_engine.py:206`,
verified): six verbs carry the doctrine rail, so an agent can drive a whole spine via
`start`/`attest`/`advance` and **never call `current` once**. Emitting the manifest solely
on the `current` branch is therefore skippable by an agent that simply does not ask — which
is precisely the failure mode `decision:manifest-is-a-byproduct` exists to prevent.

This is design-it-twice earning its keep: the minimum-surface candidate's seam is correct in
*location* and wrong in *coverage*, and only the adversarial constraint surfaced it.
