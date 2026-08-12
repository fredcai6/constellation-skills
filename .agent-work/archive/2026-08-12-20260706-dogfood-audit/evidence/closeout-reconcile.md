# Cartographer epic-level reconcile — 20260706-dogfood-audit

Repo: `constellation-skills` (skill source). Diff range: `363d27a..d442845` (21 PRs, 74 files,
+12139/-381). No `docs/architecture/` or `docs/agents/` exists in this repo — there is no map to
reconcile packets/overlays/index against. This is a prose-record reconcile, as every commander
reconcile in this epic was.

## Net structural change (from `git diff --stat`)

- Engine verb additions in `scripts/checklist_engine.py`: `attest --evidence`, `amend` (gated-only
  mid-run re-plan: add/drop/rescope on PENDING gates, all-or-nothing, audit log to `amendments`),
  `reopen` cascade (downstream complete/in-progress gates reset to pending, evidence marked
  `superseded`), lease refresh-on-**success**-only, `no-posix-shell` refusal (bash-less Windows box
  refuses to run POSIX-form `command` checks through cmd.exe rather than silently misinterpreting).
- Pluggable crew backend: `scripts/run_crew.py` restructured around `CrewBackend` /
  `CliBackend` / `ExternalBackend`, plus `scripts/recover_crews.py`.
- Durable-root resolution: new `scripts/agent_work_root.py` (`durable_root()` — resolves to the
  MAIN checkout when called from a linked worktree, else no-op), wired into 4 scripts:
  `apply_lessons_delta.py`, `collect_feedback.py`, `verify_agent_feedback.py`,
  `verify_lessons_applied.py`.
- `scripts/init_work_area.py` gains spine instantiation.
- Drill gate in `scripts/apply_lessons_delta.py` (lines ~453-471): a ripe `constellation`-scoped
  lesson's apply now **refuses** to retire/encode the lesson unless the op carries a `drill` field
  referencing `docs/superpowers/drills/<lesson-id>.md` — field-presence check only, process-doc
  analogue of a regression test.
- New skill `constellation-docent` (+ `scripts/docent_freshness.py` + a demo explainer site under
  `docs/explainer-demo/` — built from an external project's map as a shipped demo, not this repo's
  own map).
- New platform layer `skills/_shared/windows.md`.
- Wide doctrine/template changes across admiral, commander, charter, lessons-auditor, workbench,
  triage, reviewer templates.

## Verified consistent

- **`README.md`** skill-set table (`README.md:16-27`) lists all 12 skills including
  `constellation-docent` — already updated in this epic's diff (`README.md` +1 line).
- **`docs/CHECKLIST_SCHEMA.md`** — thoroughly updated for every new engine verb: `amendments` field
  (line 43), `amend` verb section, `attest --evidence` semantics, `reopen` cascade + `superseded`
  evidence field, `no-posix-shell` shell value (replacing the old `cmd-fallback` naming), lease
  refresh-on-success wording. This is the most load-bearing prose doc for the engine changes and it
  tracks the new reality accurately.
- Backend abstraction (`CrewBackend`/`CliBackend`/`ExternalBackend`, `recover_crews.py`) is
  documented at the right altitude — `skills/commander/SKILL.md`,
  `skills/commander/templates/COMMANDER_SPINE.template.json`, and a dedicated design spec
  (`docs/superpowers/specs/2026-07-07-crew-backend-design.md`) — not a top-level-overview gap.

## Mismatches

1. **`docs/RECURSIVE_IMPROVEMENT_DESIGN.md:18,33-34,134`** — still reference the retired
   "Template Update Candidates" table in `WORKFLOW_CLOSEOUT.template.md`. That table was deleted
   and replaced by the "Lesson dispositions" section (confirmed at
   `skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md:24`) per
   `docs/superpowers/plans/2026-06-27-lessons-apply-or-defer.md` (Step 2, "Retire the Template
   Update Candidates table"). Two runs this epic already flagged this staleness per the brief.
   **Fix:** replace the three "Template Update Candidates" references with "Lesson dispositions"
   and point the follow-through-check line (134) at `verify_lessons_applied.py` /
   `apply_lessons_delta.py`, which now own that mechanism.

2. **`docs/RECURSIVE_IMPROVEMENT_DESIGN.md:391-399` (§5.2)** — describes `apply_lessons_delta.py`
   as mechanically enforcing cap/uniqueness/counter rules for ADD/AMEND/RETIRE ops, but omits the
   drill gate added this epic (`scripts/apply_lessons_delta.py:453-471`): a ripe
   `constellation`-scoped lesson cannot be retired/encoded without a `drill` field pointing at
   `docs/superpowers/drills/<lesson-id>.md`. **Fix:** add one sentence to §5.2 naming the drill-gate
   requirement as the regression-test analogue that was added alongside the deterministic-merge
   mechanism.

3. **`docs/RECURSIVE_IMPROVEMENT_DESIGN.md:416-423` (§5.5)** — proposes concurrency isolation via a
   per-work-id sidecar file (`AGENT_FEEDBACK.<work-id>.md`) with serialized consolidation at
   Admiral closeout. The mechanism actually built this epic is different: `scripts/agent_work_root.py`
   `durable_root()`, which routes every linked worktree's `.agent-work/` writes to the single MAIN
   checkout root instead of scattering per-worktree sidecars, wired into 4 scripts (listed above).
   §5.5 is a superseded proposal, not current truth. **Fix:** rewrite §5.5 to describe the
   durable-root mechanism as the shipped answer to the concurrency-isolation problem (or add a
   "superseded by durable-root, see `agent_work_root.py`" note if the sidecar idea is deliberately
   kept as a rejected alternative).

4. **`docs/CONSTELLATION_OVERVIEW.md:4-13`** (core-loop role list) — lists Charter, Commander,
   Workbench, Interrogator, Cartographer, Scout, Implementer, Reviewer, Triage but omits Admiral,
   Lessons-auditor, and now Docent. This gap predates the epic (Admiral/Lessons-auditor already
   existed before `363d27a`), but the epic added a new skill (Docent) without touching this file —
   the Cartographer/Scout/Implementer/Reviewer contract row-set doesn't reflect an epic-level "no
   touch needed" judgment so much as an existing blind spot getting wider. Not called out in the
   brief's known-stale list, so flagging as newly-noticed. **Fix:** either extend the role list to
   the full current set or add a one-line note that it intentionally covers only the
   per-issue execution loop (Admiral/Lessons-auditor/Docent operate at epic/audit level, outside
   it) — whichever is true should be stated, not left ambiguous.

5. **`docs/CONSTELLATION_OVERVIEW.md:36`** (Relationship Contract table, Cartographer row) — lists
   Cartographer's `docs/architecture/packets/` + `index.md` as consumed by "Scout, Commander,
   Implementer, Reviewer" only. Docent's entire purpose (per `skills/docent/SKILL.md:8-12,27-52`)
   is reading that same map truth (`index.md`, `packets/**`, `overlays/**`, `decisions/**`) to
   generate a human-facing site — it is a real consumer this epic added and the row doesn't name
   it. **Fix:** add Docent to that row's consumer list (read-only consumer, never edits).

## Map-instantiation recommendation

**Not yet — but the trigger is close, and defer with a named revisit condition rather than
silently continuing.**

Reasoning: the Inclusion Rule ties map cost to planning/boundary/rule/trust value, and this repo's
"structure" is still mostly skill-authoring content (`SKILL.md` + templates + references per skill)
that Charter/Commander/Scout already navigate directly — a struct hierarchy over 12
mostly-independent skill directories doesn't obviously earn its keep yet. But this epic did add
real cross-cutting architecture that a map would make legible faster than prose: the crew-backend
abstraction (a real boundary — `CrewBackend` interface vs. `CliBackend`/`ExternalBackend`
implementations vs. `recover_crews.py` recovery path), the durable-root layer (a constraint that
materially governs 4 scripts' file-location behavior and would be exactly the kind of thing a
`constraint:` overlay node exists for), and Docent as a new consumer of a map that doesn't exist yet
in this repo (it's dogfooding on other projects' maps, not its own).

If a map is built, keep it minimal and packet-first per doctrine — not a full C4 sweep:

- `struct:` nodes for `scripts/` (container) and `skills/*/` (component per skill), generated/scan
  level for the rest.
- A `constraint:` overlay for the durable-root rule ("`.agent-work` writes from a linked worktree
  must resolve to the main checkout") anchored to the 4 wired scripts — this is exactly a
  Inclusion-Rule "Rule preservation" case.
- A `capability:` overlay for "pluggable crew dispatch" anchored to `run_crew.py`, `CrewBackend`,
  and its two implementations — an Inclusion-Rule "Boundary correctness" case, since getting the
  backend/implementation direction wrong is a real risk as more backends get added.
  the checklist engine (`checklist_engine.py`) itself is probably the single highest-value packet
  candidate given how much surface it now carries (leases, amend, reopen cascade, attest) — if only
  one packet gets written first, it should be this one.

**Revisit condition:** if a third crew backend is added, or the engine gains another verb class,
build the minimal map above rather than deferring again — at that point prose-only reconcile will
start missing real boundary drift.

## Structural risks introduced by the epic

- **Reopen cascade correctness** (`checklist_engine.py`, documented `CHECKLIST_SCHEMA.md` lines
  ~290) is the highest-blast-radius new mechanism — a bug here silently invalidates downstream gate
  evidence across a whole run. Well-documented; no code review was in scope here, but it's the
  first thing I'd want covered by `tests/test_checklist_engine.py` (which did grow +411 lines this
  epic, consistent with that risk being taken seriously).
- **Durable-root fallback-on-error is silent-by-design** (`agent_work_root.py:75-78`): any git error
  or non-git directory falls back to `start`/cwd unchanged, "never raises." That's the right default
  (fail visibly to old behavior, don't invent a wrong root) but means a genuine git misconfiguration
  in a linked worktree will silently NOT get the shared-root benefit rather than erroring loud — worth
  confirming that's the intended failure mode versus a place callers should check a return signal.
- **No structural map exists to catch drift on the new abstractions going forward** — this is the
  same point as the recommendation above, phrased as risk: without at least a constraint anchor for
  durable-root and a capability anchor for the backend split, the next Commander touching either has
  no map artifact telling it those boundaries are load-bearing; it has to rediscover that from code
  and this reconcile note.
