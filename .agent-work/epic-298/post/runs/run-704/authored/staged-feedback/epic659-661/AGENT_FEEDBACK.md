# Agent Feedback — staged (fenced), epic659-661 (SegmentMap, epic #659 Build 1)

## 2026-07-25 — epic659-661 — cmdr-661 (delegated commander, issue #661)

**Run shape:** commander (delegated) · full spine driven init → context → understand → plan
(plan-alternatives inline + 1 cold plan critic) → execute (2 crew gates) → reconcile (cartographer
delta) → triage → review → feedback → archive; all 4 `user-decision` checkpoints cited to the frozen
launch order through the engine.

**Instruction adherence:** fully followed the launch order and skill doctrine. Never solved by hand;
every deliverable came out of the gated spine. All 4 crews (g1/g2 implement+review) dispatched via
`run_crew.py --backend external` + synchronous Agent-tool subagents + `--verify-result`, with
`recover_crews.py` before each (no CLI binary in this harness). All artifact postconditions satisfied
via `attach` / `attest --evidence` (never `attest` on artifact kinds). Fenced feedback staged here
rather than written to shared durable logs. Built the frozen three-way hybrid exactly as ruled — no
re-litigation of the interface. Both gates independently APPROVED first pass; 40 unit tests green
under the real 3.14 interpreter; 0 rework cycles, 0 BLOCK verdicts, 0 waives.

**Friction / unclear:**
- **DOMINANT — the sandbox `py` shim shadows the real 3.14 launcher.** The `py` first on PATH
  (`C:/Users/fredc/.local/bin/py`) is a codex-runtime Python 3.12 shim lacking project deps; it fails
  to even collect the suite. The real launcher is 3.14 at
  `C:/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe`. This shadows silently, so the engine's
  frozen `py -m pytest` **command postconditions** (g1/g2 integrate) resolve to the shim and falsely
  fail collection unless the `advance` is issued with
  `export PATH="/c/Users/fredc/AppData/Local/Microsoft/WindowsApps:$PATH"` prepended in the same shell.
  Worked around via the PATH prepend on both integrate advances and by putting the prep line up front
  in every crew handoff. Banked as `lesson:sandbox-py-shim-shadows-real-launcher`.
- **`get_latest` spec-wording is self-inconsistent.** The frozen MINIMAL spec says "most recent
  non-historical map," but Build-1 cold maps are all `status="historical"`, so a literal reading kills
  the seed resolver. Disposed within latitude (functional reading: exclude only superseded) + surfaced
  as a decision candidate to the Admiral (→ #664). Not a blocker (real consumer is Build 3).

**Crew-reported friction (harvested from gN-integrate Workflow Feedback sections):**
- G1 impl + both reviewers: my G1 handoff close-criteria gave the `simplification_limits` command
  without the required `--paths` flag, and a blanket forbidden-token grep matched docstring *mentions*
  of `property_mixture` (never imports); both caught + corrected in-flight — a sharper handoff targets
  the import statement, not the bare token.
- G2 reviewer: bespoke verification scripts in a worktree hit the editable-install `.pth` trap (a bare
  script imports the MAIN repo `src/`, which lacks `segment_map`); confirms
  `lesson:editable-install-pth-worktree-trap`. `py -m pytest` from the worktree is safe (rootdir).
- G2 reviewer cosmetic triage: `_valid_kwargs()` test fixture duplicated across test_runtime.py /
  test_store.py → a shared conftest.py would DRY it (deferred to keep the reviewed artifact frozen).

**What worked:**
- The cold plan critic paid off: 5 findings (all sharpenings, no rebuild) folded in before freeze —
  the identity-layering standalone-green fix, the once-per-load call-count assertion, fully-qualified
  unique class_ids + load-from-stored-labels, and shipping the MixtureFitAdapter — produced a module
  the two independent reviewers approved first pass (the G2 reviewer even ran a mutation-probe
  confirming the label-stability test is genuinely load-bearing).
- Synchronous (`run_in_background: false`) crew dispatch kept the turn alive throughout — no
  wait-by-ending-turn stalls, no Admiral nudges (confirms
  `lesson:delegated-commander-foreground-poll-over-watcher-yield`).
- Reading all 3 design-it-twice excursion RESULTs + the substrate before planning made the frozen
  hybrid fully buildable with zero interface ambiguity floated.

**Improvement signals:**
- A project-configured interpreter that the engine/`run_crew.py` resolve instead of bare `py` would
  have removed the single biggest friction of the run (the shim-shadowing) — the engine command
  postcondition mechanism silently resolving `py` to a deps-less shim is a real cross-run trap.
- Two standing constellation-debt lessons re-confirmed (`engine-artifact-attest` 19th recurrence;
  `from-child-refuses-on-gated-checklist` 1st confirming recurrence) — both exported to the staged
  CONSTELLATION_FEEDBACK.md with concrete upstream-fix proposals.
