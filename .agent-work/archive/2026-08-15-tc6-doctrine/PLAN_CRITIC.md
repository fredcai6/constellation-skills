# Cold Plan Critic — tc6-doctrine

Independent agent, given only `MISSION_FRAME.md` + `PLAN_ALTERNATIVES.md`, no authoring context. Verdict:
findings to triage. Triaged below (delegated mode: Admiral launch order is the ratifying authority for
this checkpoint, citing `LAUNCH_ORDER:Mission` and `LAUNCH_ORDER:Evidence required`).

## Findings and disposition

1. **"map regeneration" in the verify gate contradicts the frame's Out-of-Scope line — blocker.**
   Correct catch: the frame's Out-of-Scope bullet ("building or repairing a `docs/architecture` packet
   map") and the launch order's explicit Evidence-required line ("Regenerate the map:
   `python -m scripts.code_map build --root .`, commit if it moves") name two *different* artifacts —
   the absent `docs/architecture` packet map vs. this repo's own derived code map
   (`map/ids.jsonl`/`map/INDEX.md`, already rebuilt once during `context` orientation). **Disposition:
   fix-now.** `g4`'s imperative in `execute.json` names the exact command and the exact two files, and
   states explicitly this is not packet-map construction.

2. **`g3`'s sweep isn't fenced against out-of-scope / concurrently-owned files — blocker.**
   Correct: `scripts/run_crew.py`, `skills/commander/references/crew-dispatch.md`, and
   `.worktrees/launcher-hygiene/` are owned by the concurrent `launcher-hygiene` lane per the launch
   order's File Ownership section, and a broad `docs/`+`skills/` grep could surface a hit there.
   **Disposition: fix-now.** `g3`'s imperative in `execute.json` states explicitly: a hit inside the
   `launcher-hygiene`-owned files is recorded as a finding only, never edited, and `.worktrees/launcher-hygiene/`
   is excluded from the grep's search roots entirely.

3. **`g3`'s close criteria are unfalsifiable as written — real gap.**
   Correct: "measure and sweep" without a stated method can't be checked for exhaustiveness.
   **Disposition: fix-now.** `g3`'s postconditions in `execute.json` name the exact `grep -rn` invocation
   (search terms `is_relative_to|containment|Path\.cwd\(\)|verify_worktree_isolation\.py` across `docs/`
   and `skills/`, excluding `.worktrees/`) and require the match count stated in the return evidence —
   pre-authoring the invariant chain per `commander-core.md` "Doc-only gates."

4. **Testability is self-graded; no independent implementer/reviewer crew — minor sharpening, not a
   blocker.** Accepted as-is. This run's gates are reasoning gates (doctrine's own sanctioned shape for a
   document/diagnosis deliverable authored in context already held) — crew dispatch is reserved for code
   or independently-verifiable changes, and the launch order's own File Ownership section already
   functions as a pre-approved, file-scoped plan for a bounded docs fix. Spinning up an implementer/reviewer
   pair for three doc edits is disproportionate weight, and the launch order's "Do not dispatch a crew"
   caution (in the context of the test-suite backgrounding hazard) further biases this run toward staying
   in one context. The independent check this run gets instead: every rewritten passage is required to
   carry a quoted before/after plus a `file:line` citation into the *actual, currently-running* code
   (`docs/CHECKLIST_SCHEMA.md`, `scripts/checklist_engine.py`) — a check any reader (Admiral, human) can
   independently reproduce without re-running the gate.

5. **Sequencing rationale ("matches launch order numbering") is implicit — minor sharpening.**
   **Disposition: fix-now, cheap.** `execute.json`'s `g3` precondition states explicitly that it depends
   on `g1` having closed first, so the sweep never flags `g1`'s own not-yet-corrected passage as a false
   positive.

## Panel-vs-single, confirmed

Single critic, not a panel — this plan neither spawns epics nor touches architecture (weight-scaling rule,
`references/global-orchestrator.md`).
