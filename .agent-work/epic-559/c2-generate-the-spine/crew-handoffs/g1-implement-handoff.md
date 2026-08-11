# Implementer Handoff — `g1` · the generator

**Work id:** `epic-559/c2-generate-the-spine` · **Gate:** `g1-implement` · **Model:** Sonnet
**Dispatched by:** the Commander (delegated) under Admiral `admiral-epic-418-followon`.
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine`, branch
`epic-559/c2-generate-the-spine`.

## Gate

`g1` of `.agent-work/epic-559/c2-generate-the-spine/execute.json` — build the spine generator.

## Task

Write **one** new file, `scripts/generate_spine.py`, plus its tests.

**Read `.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md` first, in full. It is frozen and it
is your contract.** It gives you the exact TOML fields, the exact compiled output for each of the five
check kinds, the exact handback contract, what a large claim injects, the nine spec-shape faults, the
CLI order of operations and exit codes, and the guard-fixture rule. Where the note and your judgment
disagree, the note wins. Where it is silent, decide and say so in your result.

The one-line summary of what you are building: **a spec format with no raw-command field, and a
generator that refuses to emit anything `scripts/validate_spine.py` would reject.**

## Protected Intent

A check is a shell string typed from memory, and a wrong one does not announce itself — it exits 0 and
the gate opens on nothing. Four of ~17 hand-authored spines last wave carried checks that could not do
their job and **none was caught by its author**. This generator removes the place where that mistake is
made.

Two properties are not optional in the output, and both must be verified **against behaviour**, not
against JSON that merely looks right:

1. **Every gate carries a place to record beliefs, concerns and open questions** — the `handback`
   contract in `directives` (DESIGN_NOTE §5). It names `attach`, `flag-candidate` and `block`, the
   three channels the engine really persists. It does **not** offer arrays: a cold critic proved no
   engine verb appends to a `directives` field on an active gate, so arrays would render empty forever.
2. **Judgment is carried up, not buried** (DESIGN_NOTE §6). `magnitude = "large"` injects a
   `c-escalation` postcondition checking `review-result` matches `verdict: APPROVE`, renders on the
   gate, and rolls up onto the last gate.

## Test Mode

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

Use `python`, **not** `python3` — on this host `python` has pytest 9.1.1 importable and `python3` does
not. Unsetting the three spine variables matters: `scripts/mcp_spine_server.py` reads `SPINE_FILE` **at
import time** and raises `KeyError` without it, so a test that imports the door would otherwise pass or
fail for the wrong reason. Baseline at this commit: **2689 passed, 3 skipped, 1121 subtests** in ~107s.

**TDD.** Write the failing test first and observe it fail, then make it pass. Your own plan's RED step
is a `check: null` postcondition you attest — never a command check, which would run the
by-design-failing test and block your gate.

## Close Criteria

1. `scripts/generate_spine.py` exists: `compile_spec` / `compile_condition` **pure** (dict in, dict out
   — no `Path`, no `open`, no `subprocess` reachable from them), with the probes, the oracle call, the
   write and `main()` below them, in the same file.
2. `CHECK_KINDS = ("qualitative", "pytest", "script", "population", "artifact")` exists as a
   module-level constant. **A later gate pins DESIGN_NOTE.md's kind list against this exact constant**,
   so do not rename it.
3. **The control pairing, demonstrated for real, both halves:** one spec whose *translation completes*
   on the pure `compile_spec` path and which the guarded CLI then **refuses with nothing written**
   (`test ! -f <out>` after the run), and the **same spec corrected**, accepted and written. Paste both
   runs. Note the wording deliberately: `compile_spec` translates, it does not judge — do not describe
   it as "accepting".
4. Each of the five kinds compiles to exactly the output DESIGN_NOTE §4 specifies, asserted by test.
5. Each probe is pinned with **≥2 VIOLATING** fixtures it must catch, **≥2 INNOCENT** it must not, and
   a **populated** `ACCEPTED_FALSE_ALARM` bucket — populated, not merely named, for `script` and
   `population`. One fixture per side cannot tell a real AST parse from a string match on the one flag
   the fixture happens to use. Model the shape on `tests/test_mcp_adoption.py::_cli_only_verb_violations`.
6. A test **renders a generated gate through the engine's own `checklist_engine.render_human`** and
   asserts the handback block appears. Not a JSON-shape assertion — the actual rendered text.
7. A test **drives each of the three handback verbs** (`attach`, `flag-candidate`, `block`) against a
   generated spine and asserts the record lands where the contract says it lands.
8. A **falsification-floor** test for the claim escalation, in the style of
   `tests/test_mutation_floor.py`: deleting the injection must turn a named test red. A guard whose own
   removal changes nothing is the defect this epic exists to find.
9. A fixture pins the **undecidable refusal** so it cannot silently regress to a warning that still
   writes.
10. `python scripts/validate_spine.py --sweep --root .` still reports exactly **23** fault lines. You
    changed no shipped template, so this number must not move.
11. The full suite passes in the test mode above.

## Allowed Scope

- **Create** `scripts/generate_spine.py`.
- **Create** `tests/test_generate_spine.py` (and TOML/JSON fixture files under `tests/` if you need
  them).
- **Create** nothing else. If you believe another file must change, **stop and say so** rather than
  changing it.

## Specific Exclusions

- **Do not modify `scripts/validate_spine.py`.** It is the acceptance oracle. Moving the oracle to make
  your output pass is how a check stops meaning anything. Import it and call it.
- **Do not modify `scripts/checklist_engine.py`** or the engine's on-disk format.
- **Do not modify any shipped template** under `skills/*/templates/`. If your generator and a shipped
  template disagree, that is a **finding** for your result, not a fix.
- **Do not re-declare** `ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH` or `_RESOLVER_OWNED_TOKEN_RE`. Import
  them, so your exception sets cannot drift from the oracle's.
- Do not write role specs — that is the next gate. A minimal TOML fixture for your own tests is fine.
- Do not run `scripts/install_constellation.py`. It rewrites the tracked `.mcp.json` interpreter (#539).
- Do not touch `settings.json`, do not push, do not `git add -A` (`.agent-work/` is tracked here — stage
  by name).

## Constraints

- The engine's on-disk format does not change; emit what the engine already reads.
- `validate_spine.validate(spine, repo_root=root)` is the **literal last statement before success**, and
  any `Fault` or any `.undecidable` entry refuses with **nothing written** — not even a partial file.
- The oracle's fault messages are printed **verbatim** (`str(fault)`), never paraphrased.
- Every emitted `command` check is anchored `cd <repo-root> && …`. `<repo-root>` is resolver-owned and
  legitimate unresolved in output.
- The `script` probe **never imports** its target. `ast.parse` only.
- Undecidable **refuses**. There is no flag to skip it.

## Map Anchors (inbound)

This repo has **no architecture map** — `map_orient` returns `DEGRADED-UNPARSEABLE` (no
`docs/architecture/`, `map/INDEX.md` is an unfilled template, `map/ids.jsonl` is empty). Your map entry
point is therefore the declared substitute reading, hash-pinned in
`.agent-work/epic-559/c2-generate-the-spine/map-orientation.json`:

- **`docs/CHECKLIST_SCHEMA.md`** — the engine's on-disk contract. Read the `Task` table, the `Condition`
  table, the three check kinds, and §Rendering. **This is your primary entry point.**
- `scripts/validate_spine.py` — the oracle. Read all 665 lines; its docstring already names "a future
  spine generator" as its caller.
- `scripts/checklist_engine.py` lines 2089–2140 (`_directive_leaf`, `_render_directive_lines`) and
  2141–2195 (`render_human`) — how `constraints` and `directives` reach the agent.
- `scripts/init_work_area.py` — `_RESOLVER_OWNED_TOKEN_RE` and `resolve_spine`.
- Structural anchors, constraints and decisions for this gate are in `execute.json`'s `g1-implement`
  `anchors` block; the frame they were cut from is `.agent-work/epic-559/c2-generate-the-spine/MISSION_FRAME.md`.

## Deliverable Path Check

- `scripts/generate_spine.py` — `git check-ignore scripts/generate_spine.py` exits **1** (not ignored).
  Verified by the Commander before dispatch.
- `tests/test_generate_spine.py` — same family (`tests/` is tracked).

## Required Evidence

Paste **commands and their output**, not descriptions of them:

1. Both halves of the control pairing (close criterion 3), including the `test ! -f <out>` proving
   nothing was written on the refusal.
2. Each probe catching its VIOLATING fixtures and passing its INNOCENT ones.
3. The `render_human` output showing the handback block on a generated gate.
4. The falsification-floor test going red with the injection deleted, and green with it restored.
5. `python scripts/validate_spine.py --sweep --root .` fault-line count, before and after your change.
6. The full suite in the declared test mode.

## Wiring Grep

**Required.** `scripts/generate_spine.py` is a new callable surface, so name how it is reached. Run and
paste `grep -rn "generate_spine" --include=*.py --include=*.md . | grep -v '\.agent-work'` and state
plainly which references are real callers and which are only its own tests. We reliably build the
capability and unreliably wire the guarantee: a symbol only its own tests call is not yet wired, and
saying so is the correct answer for this gate — the role specs that call it land at `g2`.

## Verification Commands

POSIX form, absolute paths:

```
cd /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests

test $(cd /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine && python scripts/validate_spine.py --sweep --root /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine | grep -cE '^  \[') -eq 23
```

Quote any `-k` selector you write. An unquoted one is one of the four defects that motivated this
mission.

## Suggested Model Tier

Sonnet. The human's instruction is verbatim: *"prefer sonnet crews."*

## Authority

The dispatching Commander (delegated), under Admiral `admiral-epic-418-followon`. Anything beyond the
allowed scope comes back to me rather than being decided in the diff.

## Stop Conditions

Stop and return what you have if:

- the oracle would have to move for your design to work — that is a **finding and a float**, never a
  patch;
- the engine's format genuinely cannot carry something DESIGN_NOTE.md asks for — say what and why;
- a shipped template and your generator disagree — record it as a finding, do not edit the template;
- your scope would have to grow beyond the two files above.

**Asking up is always sanctioned.** A return-and-query costs one round trip; a wrong guess costs the
gate.

## Return Format

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g1-implement-result.md` **before you end your
turn** — that write is the delivery.

It must contain: **Return status** on its own line, whose value I copy verbatim into the gate's
evidence and which must be lowercase `complete` (never `COMPLETE` or `Complete`) — the engine's artifact
match is exact dict equality, so any other spelling leaves the gate permanently unsatisfiable. Then:
what you built, the pasted evidence above, every finding (including any shipped-template disagreement),
anything you decided where the design note was silent, and a **Workflow Feedback** section — where the
handoff, the design note or the tooling got in your way. That section feeds the run's retrospective and
is not optional.
