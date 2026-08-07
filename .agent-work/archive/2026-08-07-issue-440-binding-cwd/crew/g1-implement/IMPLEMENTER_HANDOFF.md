# Implementer Handoff

## Gate
`g1` (issue #440, epic-418 workstream A2). Worktree `C:/Programs/constellation-skills-wt/epic418-a2-440`, branch `epic-418/a2-440-binding-cwd`, base `cbd9aee`. **Work only in that worktree; use absolute paths.**

## Task

Fix how `scripts/hooks/spine_rail.py` resolves a **relative** `--file` argument when it records a
session→spine binding, so that an agent working in a **git worktree** binds its *own* worktree's
spine instead of a same-named path inside the main checkout.

Today: `handle_post_tool_use` (l.438) does `cwd = data.get("cwd") or str(project_dir)` and
`_resolve_abs` (l.390) joins the relative `--file` onto it. The harness fixes `CLAUDE_PROJECT_DIR`
at session launch (#269) and the payload's `cwd` is the **session launch directory** — measured,
identical across a parent and its subagents (`tests/fixtures/probe_payloads.jsonl`, six real
payloads). So a worktree-dispatched agent's binding points into the main checkout, the gauge writer
then writes `gauge.json` into a phantom `.agent-work/<work_id>/` there, and the engine — reading the
worktree's copy — never sees it. Measured 2026-08-05: **60 of 64 live binding entries** were exactly
this shape.

Replace "join onto `cwd` and trust it" with an **ordered, validated candidate-root resolution**.

### The resolution ladder — exact order, and the `path_source` each records

| Rung | Base | `path_source` |
|---|---|---|
| 0 | `--file` is already absolute → use as-is | `absolute` |
| 1 | an **absolute** `--worktree <dir>` in the observed command (the engine's `claim` CLI already accepts this option) | `worktree_opt` |
| 2 | the **last** `cd` / `Set-Location` / `pushd` target parsed out of the observed command text | `cd_target` |
| 3 | the payload's `cwd` (today's behaviour) | `payload_cwd` |
| 4 | each git worktree root registered against `project_dir` (`git worktree list --porcelain`) | `git_worktree` |
| 5 | `project_dir` | `project_dir` |

**A candidate only wins if it validates as a checklist.** Not `exists()` alone: the *old defect has
been creating phantom `.agent-work/<work_id>/` directories inside the main checkout*, so a bare
existence test can be decoyed by leftovers from the very bug being fixed. Require: the path exists,
parses as JSON, and carries the checklist shape (a top-level `"items"` list — cross-check against
what `load_spine`/the engine actually require, and use the weakest test that positively identifies
a checklist).

**No candidate validates → bind nothing.** Return `{}` and write no entry. This matches the store's
existing fail-closed posture (`binding_key` returning `None`; the gauge writer's
skip-on-uncertainty): a binding that names a spine which is not there is precisely this defect, and
silence is a better outcome than a confident wrong record.

**Rung 0 keeps today's behaviour exactly** — an absolute `--file` is already ground truth. Decide on
the evidence whether an absolute `--file` should *also* be validated; if you make it validate, say
why, and be sure it cannot break a `release` whose spine is gone.

### `release` is not `claim` — handle it explicitly

At `release` time the spine may already be archived, moved or deleted, so **no** candidate would
validate and the entry would leak forever (and abandoned keys already have no reaper). For the
`release` verb: **first try to resolve against the recorded binding for this key** — if exactly one
recorded `abs_spine` under that key ends with the relative `--file` suffix, that is the answer.
Only fall through to the filesystem ladder if that is ambiguous or empty. A release must still
remove what its own claim put there.

### Path normalization

The Bash tool on this box is git-bash, so a `cd` target is routinely written MSYS-style
(`/c/Programs/foo`), which is not a valid Windows path and fails `exists()`. Normalize `/x/...` →
`X:/...`. Also handle: quoted targets containing spaces, `;` chains (PowerShell 5.1 has no `&&`),
and `cd` with a relative target (resolve it against the payload `cwd`, and if the result does not
validate, fall through — do not guess).

### `path_source`

Record the winning rung as an **additive value field** `path_source` on the binding entry, beside
`spine`, `engine_session`, `worktree`, `claimed_at`. This is provenance: it is what lets the
acceptance run prove *which* mechanism resolved the path rather than only that the answer came out
right. **Additive value field only** — the binding *key* shape is untouchable (see Exclusions).

## Protected Intent

The context governor must fire on the agent shape the corpus actually runs in. Every Commander under
an Admiral epic runs in a worktree, so a governor that works only for agents whose `cwd` is the
project root is a governor that is off in production. Nothing you do may make the store record a
**confident wrong path** — a missing binding is recoverable, a wrong one silently misattributes one
agent's context reading to another agent's work area.

## Test Mode

**TDD required** for the resolution ladder. Write the failing test first for each rung — the whole
issue is that the current code returns a plausible-looking wrong answer, so a test written after the
fact is very easy to write in a shape that could never have failed.

## Close Criteria

- A payload whose `cwd` is a main checkout, whose command `cd`s into a worktree and claims a spine
  there with a relative `--file`, produces a binding entry naming the **worktree's** spine.
- Each rung 0–5 is reachable and is covered by a test that fails against the pre-change code (or,
  for rungs that are unchanged behaviour, a test that pins the behaviour).
- **Rung 4 is proven against a real `git worktree` on disk, in a fresh subprocess.** Create a
  temporary git repo, `git worktree add` a second tree, put a real checklist JSON in the worktree,
  and run the hook as a subprocess with a payload whose `cwd` is the main tree and whose command
  carries **no** `cd`. Assert the binding names the worktree path. This test must not set the
  worktree path into any env var, fixture field or payload field that the hook then reads back.
- No candidate validates → no entry is written at all, and the store is byte-unchanged.
- A `release` still removes the entry its `claim` created, including when the spine file has been
  deleted in between.
- `handle_post_tool_use` still returns `{}` on every path, including every new failure mode, and
  never raises.
- The git probe does not run on the common path (rungs 0–3 answer first) and is bounded by a short
  timeout, so a slow/locked/absent `git` cannot hang a PostToolUse hook.
- `tests/test_spine_rail.py` and `tests/test_gauge_writer.py` both green; no existing test's
  assertion is weakened to make room.

## Allowed Scope

- `scripts/hooks/spine_rail.py` — the whole change.
- `tests/test_spine_rail.py` — targeted tests (the natural home; add, do not weaken).
- A new test module if the fresh-subprocess/real-worktree integration test does not sit naturally in
  the above — say which you chose and why.
- `tests/test_gauge_writer.py` — **pre-authorized for minimal reconciliation only** if the added
  `path_source` field trips one of its binding fixtures. Reconcile it minimally; do not restructure.

## Specific Exclusions

- **The binding key shape** — `session_id` / `session_id#agent_id` / `None`, and `binding_key()`
  itself. Owned by #419, and it is a load-bearing interface the Admiral must approve changing.
- **`scripts/hooks/gauge_writer_hook.py`'s read side** and `scripts/checklist_engine.py`'s trip
  bands. They inherit the fix; they do not change. (Owned by #419 / #182.)
- **#269** — the harness's fixed `CLAUDE_PROJECT_DIR`. Not ours (`decision:not-fixing-269`,
  settled/human). If your fix would need #269 to change, **stop and return** — that is a scope
  change for the Admiral.
- The three other known limits named in `docs/GAUGE_WRITER_HOOK.md` — no reaper for abandoned keys,
  no lock around load-modify-save, no validation of a shell-mangled `--file`. Do not fix them.
  If you touch code next to one, leave a comment naming it and float it in your result.
- The live main checkout's `.agent-work/.spine-rail-binding.json` and any real `.claude/settings*.json`.
  **Do not read-modify-write them.** A live Admiral session is using them.

## Constraints

- PostToolUse **never blocks and never raises**: every new path stays inside the existing
  `try/except` and returns `{}` on failure.
- Skip-on-uncertainty: silence beats a confident wrong record.
- **A test that cannot fail is worse than no test.** No test may hand-inject the root it claims to
  prove the hook derives. This epic has already filed three issues in that family (#432, #446, and a
  finding inside #419's own run) — do not make it four.
- Use `python`, never `py`: `py` on this box resolves to a runtime with **no pytest** and produces
  fake failures.
- Scope discipline (settled/human, Tommy): build the thing that needs to work; do not chase every
  corner case. A corner case you choose not to chase gets a **comment at the code site naming it**
  and a line in your result — never silence.
- Match the surrounding code: this module's comments carry issue numbers and explain *why a
  tempting alternative was rejected*. Write in that register.

## Map Anchors (inbound)

This repo has **no architecture map** (orientation `DEGRADED-NO-MAP`); the hash-pinned substitute is
`docs/GAUGE_WRITER_HOOK.md`. Read its section **"Known limits of the binding store itself (#419)"** —
its first bullet is this defect, stated in full.

- **Structural:** `scripts/hooks/spine_rail.py` — `_resolve_abs` (l.390), `handle_post_tool_use`
  (l.438); `tests/test_spine_rail.py`; `tests/fixtures/probe_payloads.jsonl` (six real payloads).
- **Capability:** session→spine binding maintenance — which absolute spine path an acting agent's
  claim is recorded against.
- **Constraints/assumptions:** PostToolUse never blocks; skip-on-uncertainty; binding key shape
  unchanged; `CLAUDE_PROJECT_DIR` fixed at session launch.
- **Decision anchors:**
  - `fix-the-resolution-not-the-caller` — the fix lands in the resolution, not in call sites.
    `@grade: settled/measured · leans g1 · settle: DONE — the payload carries no per-agent root, so the resolution must verify against the filesystem`
  - `not-fixing-269` — the harness's fixed `CLAUDE_PROJECT_DIR` is upstream and out of scope.
    `@grade: settled/human · leans g1`
  - `existence-verified-resolution` — ordered rungs, first *validating* candidate wins, bind nothing
    if none.
    `@grade: guess · leans g1 · settle: the two-arm live fire at g2`
- **Evidence expectations:** a worktree-dispatched agent's binding entry names
  `<worktree>/.agent-work/<work_id>/spine.json`; `tests/test_spine_rail.py` green and grown.
- **Map confidence flags:** no map exists — verify every structural claim above against the source
  rather than trusting this handoff's line numbers.

## Deliverable Path Check

- **Committed** — `scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py` (and any new test
  module). Run `git check-ignore <path>` for each and confirm exit **1**; record the commands and
  exit codes. A new test module is untracked until staged: `git diff` will show one file fewer than
  `git status`.
- **Local-only** — `.agent-work/issue-440-binding-cwd/crew/g1-implement/IMPLEMENTER_RESULT.md`;
  intentionally under `.agent-work/`, so the reviewer should not expect it in the diff.

## Required Evidence

**Load-bearing — prove these rigorously:**

1. The rung-4 real-`git worktree` fresh-subprocess test, with its output pasted, **and** a short
   statement of how you know it could fail (e.g. paste it failing against the pre-change hook).
2. The worktree-dispatched claim producing a worktree-rooted binding entry, with the resulting
   entry pasted verbatim including `path_source`.
3. `python -m pytest tests/test_spine_rail.py tests/test_gauge_writer.py -q` — full output tail and
   the **real** exit code. Redirect to a file and echo `$?`; `cmd | tail` captures `tail`'s exit code,
   not the command's.

**Confirmatory — a spot-check suffices:** the per-rung unit tests, the no-raise fuzz, the
`release`-after-spine-deleted case.

Report test counts before and after. `tests/test_spine_rail.py` had **74** tests at `cbd9aee`;
re-derive rather than trusting that number.

## Wiring Grep

Required. One command naming every symbol you add, showing a call site outside its own definition:

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-440 && grep -rn "<each new symbol>" --include=*.py . | grep -v "def <symbol>"
```

State the count of external call sites found for each. **Zero external call sites for any new symbol
is a stop condition, not a note** — a helper only its own definition and its own tests reference is
shipped-inert.

## Verification Commands

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-440
python -m pytest tests/test_spine_rail.py tests/test_gauge_writer.py -q > /tmp/g1.txt 2>&1; echo "EXIT=$?"; tail -20 /tmp/g1.txt
git check-ignore scripts/hooks/spine_rail.py; echo "EXIT=$?"
```

Do **not** run the full suite — it takes 7 minutes and the Commander runs it at g3.

## Suggested Model Tier

**Stronger (Opus).** The failure mode is a plausible-looking wrong answer, the ordering has real
traps, and the test design is the part most likely to go wrong. **No Fable, at any tier.**

## Authority

Already decided, do not re-open: the ladder and its order; validate-not-merely-exists; bind-nothing
on total failure; `path_source` as an additive value field; `release` resolving from the recorded
binding first. Decided by the Commander under the Admiral's launch order, after a cold critic panel
and a design-it-twice comparison (`.agent-work/issue-440-binding-cwd/CRITIC_TRIAGE.md`).

**Yours to decide** (record the choice and why): the exact checklist-validity test; whether an
absolute `--file` also validates; where the integration test lives; the git-probe timeout value.

**Not yours alone:** anything touching the binding key shape, anything needing #269 to change,
anything that would make PostToolUse able to block or raise.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; a specific exclusion must be touched; the
required evidence cannot be produced; or a decision outside the given authority is needed. A
measured negative reported honestly is a complete deliverable — never a fabricated green.

## Return Format

Write `IMPLEMENTER_RESULT` to
`C:/Programs/constellation-skills-wt/epic418-a2-440/.agent-work/issue-440-binding-cwd/crew/g1-implement/IMPLEMENTER_RESULT.md`
**before you go idle**, and also deliver it as your final message: completed slice, files changed,
test mode satisfied, evidence produced (with real exit codes), assumptions used, stop conditions
hit, out-of-scope observations, and workflow feedback — what in this handoff or the workflow made
the work harder than it needed to be.
