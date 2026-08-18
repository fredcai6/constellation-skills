# RETURN — cmdr-567-j (epic-567-door lane J)

## 1. Verdict

**Delivered.** Both fixes shipped, reviewed, and independently verified:

- **#619** — a real (non-`--dry-run`) install no longer rewrites the installer checkout's own
  tracked `.mcp.json` when the run declares a destination elsewhere (`--dest`/`--project`). The
  plain self-install path (no `--dest`/`--project`) is unchanged.
- **#633** — `run_crew.py` now resolves an unset `--model` from a declared role×harness tier
  table at the single `CrewSpec` construction choke point, refuses an out-of-set model by name,
  and requires + records a `--reason` for a non-default in-set choice.

Full suite green in a clean detached worktree except the one pre-authorized failure
(`MapTreeFreshnessTests`). PR opened against `main`.

**A correction to the launch order's own framing, confirmed with the Admiral mid-run**: #633's
actual defect was never a silently-inherited host default. `decision:refuse-a-tierless-dispatch`
(#611) had already closed that exact failure mode before this wave began — `run_crew.py` already
refused a dispatch with no `--model` at all. The 15 unintended Opus crews the launch order cites
came from a Commander writing `"Opus"` into the handoff's free-text **Suggested Model Tier**
field, with reasons — an unconstrained field, not a silent inheritance. The fix built this wave
(a declared table + a pure resolver at the one construction choke point) closes the defect either
way, regardless of which upstream path fed the value, so no replan was needed — only the record.

## 2. The installer — before and after

**Before** (confirmed live on `main`, reproducing lane D2's exact finding): `main()`'s real-CLI
branch always calls `apply_repo_mcp_config_wiring(default_mcp_config_path(), interpreter, ...)`
after every real install, where `default_mcp_config_path()` resolves to
`Path(__file__).resolve().parents[1] / ".mcp.json"` — the installer *script's own* checkout,
completely independent of `--dest`. Running the installer with `--dest` pointing entirely
outside the repo still stamped a machine-probed interpreter into the calling checkout's tracked
`.mcp.json`.

**After**: a pure `is_self_install(args) -> bool` predicate
(`args.dest is None and args.project is None`) gates the *entire*
`apply_repo_mcp_config_wiring(...)` call — not just its path argument — so the call never fires
at all unless the run is a plain self-install or an explicit `mcp_config_path` override was given
(the shape every existing test already used).

**Real-world proof, run independently by both the reviewer and me outside the test suite:**

```
$ sha256sum .mcp.json
ce8f91b8fff74bbbd1c7dc2f2786a919ea2dc97dae9a563e4e6effd13dbb7f8e  .mcp.json
$ py scripts/install_constellation.py --agent codex --scope user --dest /tmp/g1-real-dest-proof --skills workbench
Codex:
Installing 1 skill(s) into /tmp/g1-real-dest-proof
...
Installed. Restart Codex to pick up new or updated skills.
$ sha256sum .mcp.json
ce8f91b8fff74bbbd1c7dc2f2786a919ea2dc97dae9a563e4e6effd13dbb7f8e  .mcp.json
$ git diff --stat .mcp.json
(empty)
```

Byte-identical hash before and after; `git diff --stat` shows nothing. The self-install path
(no `--dest`) is unchanged — the existing `RepoMcpConfigWiringTests` suite passes unmodified.

One accepted, documented edge case: `--scope user` with no `--dest` still satisfies
`is_self_install` and still wires the checkout's own `.mcp.json`, even though the install target
is the user's home directory rather than the checkout's own project scope. This matches today's
behavior and is not treated as a second bug this wave.

## 3. The table — values, shape, location, harness dimension

**Location**: `scripts/run_crew.py`, a module-level `ROLE_MODEL_TIERS` dict beside
`build_crew_argv`, plus a frozen `ResolvedModel` dataclass and a pure, zero-I/O
`resolve_model(role, harness, requested, reason) -> ResolvedModel`.

**Values** (`decision:ship-todays-tiers`, harness `"claude"` only):

| Role | Default | Allowed |
|---|---|---|
| admiral | opus | {opus} |
| commander | sonnet | {sonnet, haiku} |
| implementer | sonnet | {sonnet, haiku} |
| reviewer | sonnet | {sonnet, haiku} |
| critic | sonnet | {sonnet, haiku} |
| cartographer | sonnet | {sonnet, haiku} |

**Harness dimension**: declared, never detected. `CrewSpec.launcher` (`--command`, default
`"claude"`) was already the real, working harness signal — `build_crew_argv` already threads it
to the actual launcher binary invoked. `resolve_model` keys directly on that value; no new flag,
no detection logic. `"codex"` and `"local"` exist as harness keys with **empty** role dicts — the
schema expresses them (the human's stated requirement), but no model identifiers are invented for
either, since no Codex/local dispatch is wired up anywhere in this repo yet. A dispatch against
either currently refuses by name rather than guessing.

**Resolution semantics** (five branches, exact order): (1) an undeclared role/harness pair
refuses by name; (2) no `--model` given resolves the role's default, no reason needed; (3) an
out-of-set `--model` refuses by name; (4) an in-set non-default `--model` with no `--reason`
refuses; (5) an in-set default-or-reasoned choice succeeds.

## 4. The refusal and the reason, each demonstrated

**Refused by name** (out-of-set model), from `tests/test_crew_launcher.py::ResolveModelTests::test_out_of_set_model_is_refused_by_name`:
a `CrewLaunchError` naming the rejected model, the role, and the full allowed set — mirroring the
duplicate-crew guard's own named-refusal phrasing.

**Reason recorded**: `tests/test_crew_launcher.py`'s new non-default-in-set tests
(`test_non_default_in_set_choice_with_no_reason_is_refused` /
`...with_reason_succeeds_and_carries_reason`) prove a non-default in-set `--model` with no
`--reason` refuses, and the same choice with `--reason` succeeds with the reason threaded through
`build_entry` into the `crew-runs.json` registry entry (`if reason: entry["reason"] = reason`,
same "recorded when present" shape as `model`).

## 5. A no-`--model` crew, proven from the registry

Dispatched a real crew through **this worktree's own** `scripts/run_crew.py` (not the installed
skill copy, which still carries the pre-fix behavior — see §9) with `--role implementer` and
**no `--model` flag at all**. Its `crew-runs.json` entry:

```json
{
  "crew_id": "constellation/567-j/g4-verify/implementer/attempt-1",
  "status": "completed",
  "model": "sonnet",
  "exit_code": 0,
  "result_present": true,
  "result_fresh": true
}
```

`sonnet` is `implementer`'s declared `ROLE_MODEL_TIERS` default — resolved from the role, proven
from the registry entry, not asserted from the code.

## 6. Suite result

Full suite on Linux, `git worktree add --detach /tmp/567-j-suite-verify <commit>` (never the
working copy), `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR`:

```
$ py -m pytest tests/ -q
...
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
1 failed, 3398 passed, 6 skipped, 1219 subtests passed in 140.89s
```

`^FAILED` grep: exactly one line, the pre-authorized `MapTreeFreshnessTests` failure named in
this launch order's Inherited Context. Nothing else failed.

**Commit**: `0a47ef39f1044d5a9d9310bee4706cabb852494c` (base `9b38b9d9`, branch
`feat/567-j-launcher-declared-defaults`).

## 7. Touched paths

**Changed:**
- `scripts/install_constellation.py` — `is_self_install`, `main()`'s `wire_repo_mcp_config` guard.
- `scripts/run_crew.py` — `ROLE_MODEL_TIERS`, `ResolvedModel`, `resolve_model`; `CrewSpec.reason`
  field and `__post_init__`; `build_entry`'s `reason` param; `build_parser`'s `--reason`; both
  `main()` `CrewSpec(...)` construction sites (now symmetric).
- `tests/test_install_constellation.py`, `tests/test_crew_launcher.py` — corresponding tests.

**Wanted to touch, did not (fenced or out of scope):**
- `skills/admiral/templates/LAUNCH_ORDER.template.md`, `.agent-work/templates/LAUNCH_ORDER.template.md` —
  in my ownership per the launch order, but the fix landed entirely inside `run_crew.py`'s own
  choke point; no template field was needed to express a per-dispatch reason (`--reason` is a
  plain CLI flag, not something a launch order template needs to declare). Left untouched rather
  than manufacture a change.
- `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py`, any `*SPINE*.template.json`,
  `specs/` — fenced to lane K.
- `map/INDEX.md` — Admiral-owned (#544).
- Real Codex/local model identifiers in `ROLE_MODEL_TIERS` — no verified facts to populate them
  with (§3).

## 8. Triage candidates

All staged under `.agent-work/567-j/triage-candidates/`, none filed (per
`decision:no-issue-filing-mid-run`):

1. **`crew-block-parent-waive-handshake-undocumented.md`** — the engine's own door refuses a crew
   waiving a check on its own bound spine ("always ask up"), but the two routes its own refusal
   text names for the parent to act instead are both filed defects (#632 impersonation, #369
   forced-claim attribution loss). The actual working protocol (release → parent claims → parent
   waives → parent releases → child reclaims) was executed by hand with the Admiral and is
   nowhere written down.
2. **`handoff-only-crew-inherits-parent-spine-env.md`** — a `--handoff`/`--result` (no `--spine`)
   crew dispatch still inherits the parent's live `SPINE_FILE`/`SPINE_SESSION` unchanged.
   Independently discovered and correctly worked around by two separate crews this wave (g1-review,
   g2-implement).
3. **`implementer-handoff-repo-root-monkeypatch-recipe.md`** — a handoff test recipe that says
   "monkeypatch `REPO_ROOT`" doesn't work for a function with a def-time-bound default; the working
   pattern (`func.__defaults__` patching) should be named in shared handoff-authoring guidance.
4. **`review-survey-template-unfilled-reviewer-skill-dir.md`** — `REVIEW_SURVEY.template.json`'s
   `r6-fowler` check carries an unfilled `<reviewer-skill-dir>` placeholder; every self-bootstrapped
   reviewer survey hits the same `amend --delta retext-check` detour.
5. **`spine-advance-from-child-gated-checklists-unsupported.md`** — `spine_advance --from_child`
   (and `checklist_engine.py consolidate`) only supports a `survey`-type child; a Commander's own
   `execute.json` is always `gated`, so the documented consolidation path is unusable for the one
   child checklist every Commander run produces.

## 9. Workflow feedback

**What helped**: the launch order's pre-rulings were load-bearing and correct in every case I
tested them against reality — `decision:pass-model-explicitly` in particular (I passed `--model
sonnet` on every dispatch, and would have been badly bitten otherwise, since the *installed* skill
copy of `run_crew.py` still hard-refuses a bare `--model`-less dispatch — see next). The
plan-alternatives + cold-critic sequence caught two real defects before any code was written: a
null-deref in the installer's guard (calling `apply_repo_mcp_config_wiring(None, ...)`) and a
bypass of `launch_crew()`/`record_external_attempt()` if resolution had been pre-computed in
`main()` instead of inside `CrewSpec.__post_init__`. Both would have shipped silently without that
step.

**My own mistakes, indicted plainly**:

1. **I nearly proved the g4 registry claim against the wrong `run_crew.py`.** My first g4-verify
   dispatch went through `py /home/tommy/.claude/skills/constellation-commander/scripts/run_crew.py`
   — the *installed* copy, which still carries the pre-fix hard refusal (`docs/agents/
   ORCHESTRATOR_CONTEXT.md`'s own "the engine under edit is not the engine in play" section names
   this exact class of mistake, and I made it anyway on the very check meant to prove the fix). It
   refused with the *old* message, which momentarily looked like a regression before I noticed I
   was dispatching against the wrong file. Fixed by invoking this worktree's own `scripts/run_crew.py`
   directly. Worth a sharper personal lesson: when the artifact under test *is* the dispatch
   mechanism, name which copy every single dispatch command uses, not just the ones the handoff
   already flagged.
2. **My g3-implement handoff under-scoped the blast radius of a shared choke point.** I named
   exactly two tests to rewrite; wiring `resolve_model` into `CrewSpec.__post_init__` actually
   broke three more, scattered across two other test classes, because any existing test
   constructing a `CrewSpec` with a falsy or arbitrary `model` string against a now-populated
   role/harness pair collided. The implementer correctly stopped rather than guess — exactly the
   discipline the doctrine asks for — and I had to rule and rework. A pre-flight `grep -n 'model="'`
   against the table's populated keys, named in the handoff, would have caught this before
   dispatch instead of after.
3. **I initially wrote the mission frame with fabricated-shaped `decision:`/`claim:` anchors**
   against a repo I already knew had no map, and only discovered `plan.c6`'s hard refusal — and
   then discovered I could not self-waive it — after authoring the full frame. A faster path
   would have been checking whether *any* anchor could resolve (a one-line `map_orient.py
   verify-frame` probe against an empty frame) before investing in the frame's content, though I
   don't think a cheaper legitimate path existed to avoid the escalation itself — the self-waive
   refusal is a real, deliberate integrity control, not a bug to route around.

**What got in the way**: the `plan.c6` self-waive refusal, once hit, has no documented recovery —
see triage candidate 1. The `execute.json` child-checklist consolidation gap — see triage
candidate 5 — cost real time at the one moment (execute closeout) every Commander run reaches.

## 10. PR

Opened against `main` from `feat/567-j-launcher-declared-defaults`. Number and head sha recorded
after the `gh pr create` step below.
