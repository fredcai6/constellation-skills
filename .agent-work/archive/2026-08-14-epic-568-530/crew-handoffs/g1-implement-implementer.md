# Implementer Handoff

## Gate

`g1-implement`

## Task

Correct binding worktree attribution from a validated absolute spine path in
the claim writer and SessionStart bind-on-resume writer.

## Protected Intent

A child in a linked worktree must never be attributed to the launch checkout
merely because hook payload `cwd` is stale. Preserve existing release behavior.

## Test Mode

TDD required. First add a real git main-plus-linked-worktree regression that
fails on the current writer because it records the deliberately wrong main cwd.

## Close Criteria

- Add one small private helper that accepts only absolute
  `.agent-work/<work-id>/<name>.json` paths and derives the owning worktree.
- Malformed or out-of-layout paths return no attribution; they never fall back
  to payload `cwd`.
- Use that helper at claim and unambiguous SessionStart binding writes only.
- The real test uses one shared session, distinct agent ids, child payload cwd
  set to main, production claim/Stop/release/SessionStart paths, and proves:
  parent Stop blocks while parent is active; after parent release it is
  non-blocking while child remains active and foreign.
- Run `pytest -q tests/test_spine_rail.py`.

## Allowed Scope

- `scripts/hooks/spine_rail.py`
- `tests/test_spine_rail.py`
- `.agent-work/epic-568-530/notes-1.md` for local implementation notes only

## Specific Exclusions

- #441: no locking, identity unification, reaping, schema migration, or store
  transactionality.
- No change to release target resolution or engine/spine JSON.

## Constraints

- `abs_spine` is the only ownership source. Do not use payload cwd, observed
  cd, or `--worktree` text for the stored worktree.
- Keep compatibility with JSON checklists under `.agent-work/<work-id>/`.
- The new acceptance test must be real linked-worktree topology, not a
  pre-written binding, a monkeypatch, or a child path injected through payload,
  environment, cd, or `--worktree`.

## Map Anchors (inbound)

- **Map entry point:** `README.md` is the declared degraded-map substitute.
- **Capability:** binding records identify a resolved spine's owning worktree.
- **Constraint:** resolved abs_spine is the ownership source; payload cwd is
  not.
- **Decision anchors:** resolved-spine-owns-worktree.
  @grade: settled/measured · leans g1-implement
- **Decision anchors:** no-441-expansion.
  @grade: settled/human · leans g1-implement
- **Evidence expectations:** real linked-worktree regression and focused rail
  suite.

## Deliverable Path Check

- **Committed** — `scripts/hooks/spine_rail.py`; `git check-ignore
  scripts/hooks/spine_rail.py` exited 1 before dispatch.
- **Committed** — `tests/test_spine_rail.py`; `git check-ignore
  tests/test_spine_rail.py` exited 1 before dispatch.
- **Local-only** — `.agent-work/epic-568-530/crew-handoffs/g1-implement-implementer-result.md`;
  durable crew delivery artifact, intentionally untracked in this work area.

## Required Evidence

- Load-bearing: pre-fix red assertion and green corrected assertion for child
  stored worktree; production Stop/release/SessionStart assertions.
- Load-bearing: focused pytest output.
- Confirmatory: helper negative predicate cases.

## Wiring Grep

`rg -n "_worktree_from_spine" scripts/hooks/spine_rail.py` must show the
definition and both existing binding-write call sites. Report the call-site
count excluding the definition.

## Verification Commands

```bash
pytest -q tests/test_spine_rail.py
```

## Suggested Model Tier

`stronger` — real worktree topology and two production writers need careful
scope control.

## Authority

The Admiral's launch order settles the ownership source and excludes #441.
Float any lifecycle, release, binding schema, locking, identity, or reaping
decision.

## Stop Conditions

Stop and return if the real pre-fix topology cannot reproduce the wrong stored
worktree, any required scope expansion emerges, or any non-Windows regression
fails.

## Return Format

Write `IMPLEMENTER_RESULT` to
`.agent-work/epic-568-530/crew-handoffs/g1-implement-implementer-result.md`
before ending. Include lowercase `Return status: complete` only if all criteria
and focused tests pass; include files changed, red/green evidence, assumptions,
out-of-scope observations, and workflow feedback.
