# Run Summary — tc6-doctrine

`spine_status` resolved to `tc6-doctrine` throughout this run (lease `constellation/tc6-doctrine/execute/commander`, worktree `/home/tommy/projects/constellation-skills/.worktrees/tc6-doctrine`) — confirmed at every gate, never diverted to `f-424` or any other spine.

## Gates closed

`init -> context -> understand -> plan -> execute (e0-context -> g1 -> g2 -> g3 -> g4) -> reconcile -> triage -> review`, all through the engine (spine.json via the MCP door, execute.json via `checklist_engine.py --file`), no hand-editing.

## Task 1 — docs/CHECKLIST_SCHEMA.md (highest priority)

**Before** (lines 120, 122):
> **What the engine does with it (#315/#568).** On every **guarded** verb, `origin_worktree_refusal` compares `origin.worktree` against the engine's own `Path.cwd()`; when cwd is neither that directory nor inside it, the engine prints `REFUSED:` to stderr and exits `1` **without writing the file**. [...]
>
> Containment, not equality: `<worktree>/scripts` and `<worktree>/.agent-work/<id>` pass, and the comparison is segment-wise, so a sibling sharing a name prefix (`/w/repo-2` against `/w/repo`) does not.

**After** (`docs/CHECKLIST_SCHEMA.md:120-122`):
> **What the engine does with it (#315/#568; equality since #588, the 2026-08-15 worktree-identity ruling).** On every **guarded** verb, `origin_worktree_refusal` (`scripts/checklist_engine.py:102-179`) compares `origin.worktree` by **equality** against a cwd the engine resolves to its **git worktree toplevel** — never the raw `Path.cwd()` an earlier version read — at the single impure call site in `main()` (`scripts/checklist_engine.py:3411-3444`, via `git rev-parse --show-toplevel`); when the two disagree, the engine prints `REFUSED:` to stderr and exits `1` **without writing the file**. The predicate itself stays pure [...] An origin-carrying spine whose cwd resolves to no git toplevel at all is **refused too — fail-closed** [...]
>
> Subdirectory work still passes — but not from containment logic. `<worktree>/scripts` and `<worktree>/.agent-work/<id>` resolve, via `git rev-parse --show-toplevel`, to `<worktree>` itself [...] so equality holds directly.

Code backing, cited: `scripts/checklist_engine.py:102-179` (pure predicate, equality via `os.path.normcase`/`==`), `:3411-3444` (the one impure call site: `_git(["rev-parse", "--show-toplevel"])` resolved before the predicate runs, fail-closed on `None`). `tests/test_spine_origin_isolation.py::test_it_is_pure` backs the purity claim.

Preserved, unchanged in substance: the guarded/exempt verb-set reasoning (`current` read cross-tree for `REFRESH REQUESTED`; `release` as the recovery escape hatch) and the unforgeability withdrawal (`docs/CHECKLIST_SCHEMA.md:124`, verbatim: *"It does **not** make the comparison unforgeable — the engine reads its ambient cwd, and a check authored as `cd <origin.worktree> && …` still satisfies it."*) — not upgraded, per Pre-Ruling `forgery-stays-named`.

## Task 2 — launch-order template judgment call

**Decision: (b) — distinct, not redundant.** `skills/admiral/templates/LAUNCH_ORDER.template.md:43`'s `verify_worktree_isolation.py --here` first-step instruction earns its place independently of the engine-native guard:

- **Timing.** It runs before `init_work_area` creates any spine — there is no `origin.worktree` stamp yet for `origin_worktree_refusal` to compare against. The engine guard cannot activate at this point in the run.
- **Independent expected value.** Its `EXPECTED` argument is the worktree path the Admiral wrote into the launch order — an authority external to any spine file — not a value the Commander's own process stamped moments earlier (`scripts/verify_worktree_isolation.py:88-97`, `check_here`).
- **Audience.** A human-readable pass/fail pasted into the return report (line 76), distinct from an engine `REFUSED:` on a later mutating verb.

**Before** (line 43, standalone, immediately followed by the "Isolation is git-only" section with no cross-reference to the schema doc's "supersedes" claim):
> First step, before any git operation: run `python <admiral-skill-dir>/scripts/verify_worktree_isolation.py --here <absolute worktree path>` — it must exit 0, proving you are in your own worktree and not the shared checkout. Paste its output into your return report.

**After** (one paragraph added directly below it):
> **Distinct from, not superseded by, the engine-native guard.** `docs/CHECKLIST_SCHEMA.md`'s "supersedes" language is scoped precisely to the per-template `command` check that used to sit on the Commander spine's `init` precondition `c0` — not to this instruction. This check runs before `init_work_area` creates a spine at all, so there is no `origin.worktree` stamp yet [...] It earns its place independently: an early, human-readable pass/fail pasted into the return report, catching a misplaced Commander before any spine-mutating verb is even attempted.

Lines 46-54 (`isolation is git-only`, `CLAUDE_PROJECT_DIR`) verified accurate against `scripts/hooks/spine_rail.py:68` (`Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())`) and left untouched, per the launch order.

## Task 3 — the third surface

**`skills/workbench/references/checklist-engine.md`: honest null.** Read in full; its only `worktree` mentions are the `--worktree` CLI flag on the lease `claim` verb (lines 84, 89) — lease provenance metadata, not an isolation/containment/equality claim. **The recorded third surface does not exist as described.**

**Sweep** (`grep -rn -E 'is_relative_to|[Cc]ontainment|Path\.cwd\(\)|verify_worktree_isolation\.py' docs/ skills/ --include=*.md`): **51 hits**, all triaged:
- The `docs/CHECKLIST_SCHEMA.md` and `skills/admiral/templates/LAUNCH_ORDER.template.md` hits are the passages Task 1/2 already corrected.
- `docs/GAUGE_WRITER_HOOK.md:623` and `docs/EPISODE_STORE.md:628,633` — a different, unrelated containment check (`spine_rail._is_valid_claim_target` for CLAIM-target resolution; episode-store directory membership) — not this doctrine.
- `docs/superpowers/specs|plans/2026-06-24-*.md` — historical design/plan documents for `verify_worktree_isolation.py`'s original build; archival, not live operative doctrine.
- `skills/_shared/windows.md`, `skills/admiral/references/fleet-doctrine.md` — still-accurate descriptions of `verify_worktree_isolation.py`'s own unchanged role (the Admiral's pre-wave gate and the Commander's `--here` self-check) — a distinct mechanism from the engine's `origin_worktree_refusal`, per the Task 2 finding above.
- `skills/docent/*` — false-positive substring match on "self-containment" (single-file HTML), unrelated to worktrees.
- `docs/superpowers/plans/2026-06-24-lessons-delete-and-collector-tolerance.md:781` — an unrelated `Path.cwd()` default for an inbox path.

No hit fell inside a launcher-hygiene-owned file (`scripts/run_crew.py`, `skills/commander/references/crew-dispatch.md`). Nothing found and left unfixed.

## Ruling vs. shipped engine

No disagreement found. Every part of the 2026-08-15 worktree-identity ruling is shipped exactly as described: pure equality predicate (`scripts/checklist_engine.py:102-179`), the one impure call site resolving git worktree toplevel (`:3411-3444`), fail-closed ordering after the shape fallbacks, and the purity test (`tests/test_spine_origin_isolation.py::test_it_is_pure`).

## Clean-env suite and map

- Full suite, cache-clean (`__pycache__` purged first), clean env (`SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` unset): **3028 passed, 6 skipped, 1136 subtests passed in 123.83s** — exactly matching the launch order's stated worktree-checkout baseline (3028/6).
- Map: this repo's own derived code map rebuilt via `python -m scripts.code_map build --root .`; `map/ids.jsonl` and `map/INDEX.md` **unchanged** (docs-only edits do not move it) — nothing to commit for it.

## Floated

- No `docs/architecture` packet map exists for this repo (`map/ids.jsonl` builds to 0 citable ids; `map/INDEX.md` is an unfilled landing-zone stub). Context orientation came back `DEGRADED-UNPARSEABLE` and was discharged via declared substitutes. Recorded as an `evidence_only` discrepancy in `REPLAN_INPUT.json` (`D0`) for the Admiral/Cartographer to weigh — not filed as an issue from this docs-only lane.

## Triage

`execute.json` `triage_candidates` was empty (0 flagged) — verified directly, nothing to route. Zero issues filed.
