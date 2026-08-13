# Triage recommendations — `commander-315-native`

Authority: local commits are allowed; issue creation requires explicit human approval under
`docs/agents/ORCHESTRATOR_CONTEXT.md`. The launch order supplies delegated triage authority but
does not authorize tracker writes. Accordingly, completed adjacent repairs are `fixed-now`; all
other issue-ready records are `recommend-and-defer`. No tracker issue was created.

## tc6 — Spawn every crew in its assigned worktree

- **Classification:** bug, tooling
- **Source:** `crew-handoffs/g1-implementer-result.md`; `crew-handoffs/g1-reviewer-result.md`
- **Structural anchor:** `scripts/run_crew.py::crew_cwd`, dispatch and resume launch seams
- **Observation:** Before the follow-up, `launch_process` received no `cwd`, so CLI crews inherited
  the dispatcher's directory instead of their recorded worktree. Expected dispatch and resume to
  use one absolute assigned-worktree cwd, while legacy entries with no worktree retain `None`.
  **Conditions:** CLI dispatch/resume, including default `--root=.` and `--worktree=.`.
  **Type:** measured — source inspection, a direct default-dot probe, and reviewer red/green arming.
  **Rev:** `ed25bf8f` plus the pre-repair worktree.
- **Priority:** high — the inherited cwd directly defeated native origin isolation.
- **Disposition:** `fixed-now` — commit `48f07123`; focused suite 171 passed and the full suite
  passed 2,981 with 6 skipped.
- **Issue authority:** local fix authorized; no issue needed.

## tc7 — Scope MCP engine cwd to the bound spine worktree

- **Classification:** bug, tooling, structure/constraint mismatch
- **Source:** `crew-handoffs/g1-implementer-result.md`; `crew-handoffs/g1-reviewer-result.md`
- **Structural anchor:** `scripts/mcp_spine_server.py::run_engine`
- **Observation:** The in-process door was intentionally cwd-independent, while the native engine
  guard reads ambient cwd. Consequently `spine_open` followed by `claim` could not drive the new
  worktree through one MCP session. Expected the door to stand in the bound spine's worktree only
  for the synchronous engine call and restore its caller cwd on every exit.
  **Conditions:** origin-stamped spine opened in a linked worktree and driven through stdio MCP.
  **Type:** measured — the untouched lifecycle round trip failed before the repair; success,
  exception, and `SystemExit` restoration were independently armed and reviewed.
  **Rev:** `ed25bf8f` plus the pre-repair worktree.
- **Priority:** high — this blocked the MCP-first workflow selected for the epic.
- **Disposition:** `fixed-now` — commit `48f07123`; lifecycle, scoped-chdir, origin, and full-suite
  evidence are green.
- **Issue authority:** local fix authorized; no issue needed.

## tc8 — Extend origin stamping to child checklists

- **Classification:** missing capability anchor, tooling
- **Source:** `PLAN_CRITIC_TRIAGE.md` finding 4; `g1b-implementer-result.md`
- **Structural anchor:** child `review.json` and `IMPLEMENTER_PLAN.json` instantiation paths
- **Desired behavior:** Child checklists should carry a trustworthy origin stamp when created in a
  crew worktree. Today they carry no `origin`, so the engine intentionally takes its compatibility
  fallback and does not enforce native worktree isolation. **Type:** measured — the g1b
  implementer's live `IMPLEMENTER_PLAN.json` had no origin. **Rev:** `48f07123`.
- **Priority:** medium — the guard covers parent spines but not the checklists most crews drive.
- **Disposition:** `recommend-and-defer` — separate creation paths and compatibility policy exceed
  the bounded follow-up; explicit issue-filing approval was unavailable.
- **Issue authority:** ask user.

## tc9 — Preserve recovery when an origin worktree has been removed

- **Classification:** bug, tooling, unresolved decision
- **Source:** `PLAN_CRITIC_TRIAGE.md` finding 11
- **Structural anchor:** `scripts/checklist_engine.py::origin_worktree_refusal`
- **Observation:** A stamped spine whose worktree no longer exists cannot be force-claimed from a
  recovery tree because `claim` remains guarded. Expected an authorized recovery route for stale
  state after worktree removal. **Conditions:** removed origin worktree, unreleased/stale lease,
  recovery caller elsewhere. **Type:** inferred — read from the guarded verb set and containment
  predicate; the destructive removed-worktree scenario was not executed. **Rev:** `48f07123`.
- **Open question:** Whether recovery should be a narrowly authenticated exception, a lifecycle
  operation, or an explicit archive-state transition needs an authority ruling and armed test.
- **Priority:** medium — uncommon, but it affects recovery from interrupted closeout.
- **Disposition:** `recommend-and-defer` — architecture/policy impact and no filing approval.
- **Issue authority:** ask user.

## tc10 — Replace the hand-maintained shipped command-check census

- **Classification:** cleanup, missing test, tooling
- **Source:** `crew-handoffs/g1-reviewer-result.md` out-of-scope observation 2
- **Structural anchor:** `tests/test_shipped_check_commands_resolve.py::EXPECTED_COMMAND_CHECK_COUNT`
- **Observation:** The exact expected count is manually updated when templates change; the
  authorized deletion changed it from 13 to 12, and no template edit updates it automatically.
  Expected census drift to be derived or diagnosed without an unrelated manual constant edit.
  **Conditions:** adding or removing a shipped command-kind check. **Type:** measured — reviewer
  mutations to 11 and 13 both failed, proving 12 is load-bearing but manually coupled.
  **Rev:** `ed25bf8f` and retained at `48f07123`.
- **Priority:** low — the suite catches drift, but with maintenance friction.
- **Disposition:** `recommend-and-defer` — not adjacent enough for the reviewed fix and no filing
  approval.
- **Issue authority:** ask user.

## tc11 — Isolate the gauge containment test from live run writers

- **Classification:** bug, missing test, tooling
- **Source:** `COMMANDER_RESULT.md` section 7; `REPLAN_INPUT.json` discrepancy D4
- **Structural anchor:** `tests/test_gauge_chain_writer_to_trip.py`
- **Observation:** The containment test snapshots the repository's live `.agent-work` tree; a crew
  launcher writing `crew-runs.json` during the assertion produced one failure. Expected the test
  to measure only the gauge chain's writes, independent of unrelated concurrent harness activity.
  **Conditions:** full suite concurrent with a crew registry write. **Type:** measured — failed
  once, then passed on rerun and three isolated runs after the writer stopped. **Rev:** `ed25bf8f`
  plus active Commander/crew processes.
- **Priority:** medium — nondeterministic full-suite reds obscure real integration failures.
- **Disposition:** `recommend-and-defer` — needs a deliberate isolation design and no filing
  approval was present.
- **Issue authority:** ask user.

## tc12 — Avoid incidental JSON escape and layout churn during spine instantiation

- **Classification:** cleanup, tooling
- **Source:** `COMMANDER_RESULT.md` section 14; `REPLAN_INPUT.json` discrepancy D3
- **Structural anchor:** `scripts/init_work_area.py::instantiate_spine`
- **Observation:** Instantiation reserializes the resolved object with `json.dumps(indent=2)`,
  escaping 34 non-ASCII characters and reflowing hand-formatted condition objects. Expected adding
  `origin` not to create unrelated byte-level churn. **Conditions:** templates with non-ASCII or
  compact hand formatting. **Type:** measured — before/after bytes were compared; parsed content,
  key order, rendered text, and trailing newline were unchanged. **Rev:** `ed25bf8f`, retained at
  `48f07123`.
- **Priority:** low — readability/diff noise, with no runtime semantic impact measured.
- **Disposition:** `recommend-and-defer` — post-review cleanup was intentionally not mixed into the
  certified change; no filing approval.
- **Issue authority:** ask user.

## tc13 — Normalize lifecycle origin paths across symlink traversal

- **Classification:** bug, tooling
- **Source:** `PLAN_ALTERNATIVES.md`, candidate-B finding
- **Structural anchor:** `scripts/spine_lifecycle.py::build_origin`
- **Observation:** Lifecycle origin stores `str(Path(worktree))` without resolving it, while the
  engine compares normalized resolved ambient cwd containment. A worktree reached through a
  symlink can therefore false-refuse from its own tree. Expected both sides to share one canonical
  path convention. **Conditions:** lifecycle opened with a symlink-traversing worktree path.
  **Type:** inferred — read from the two producer/comparison implementations; not executed because
  `spine_lifecycle.py` was explicitly out of scope. **Rev:** `48f07123`.
- **Priority:** medium — valid worktrees can become unusable under a plausible path shape.
- **Disposition:** `recommend-and-defer` — explicitly excluded production area and no filing
  approval.
- **Issue authority:** ask user.

## tc14 — Reduce manually synchronized origin-guarantee prose

- **Classification:** cleanup, missing doc
- **Source:** `FOWLER_PASS.json` duplicated-code finding; g1c reviewer out-of-scope observations
- **Structural anchor:** `scripts/checklist_engine.py`, `docs/CHECKLIST_SCHEMA.md`,
  `tests/test_spine_origin_isolation.py`
- **Observation:** The coverage/unbypassability guarantee and non-forwardability limitation are
  hand-authored in three places with no synchronization check. Expected a correction not to leave
  stale copies. **Conditions:** future wording or contract changes. **Type:** measured — repository
  search identified the three maintained copies. **Rev:** `48f07123`.
- **Priority:** low — maintenance risk, not a current behavioral defect.
- **Disposition:** `recommend-and-defer` — a durable documentation ownership choice is broader than
  this fix and issue creation was not approved.
- **Issue authority:** ask user.

## tc15 — Reassess checklist_engine's accumulating reasons to change

- **Classification:** architecture weakness, research hardening
- **Source:** `FOWLER_PASS.json` divergent-change finding
- **Structural anchor:** `scripts/checklist_engine.py`
- **Desired behavior:** Keep engine responsibilities cohesive enough that lease, gauge, rail,
  journal, trip, checklist execution, and worktree identity changes do not all converge on one
  large module. Today those independent axes share the same roughly 3,450-line module.
  **Type:** measured — responsibilities and module size were enumerated during the Fowler pass.
  **Rev:** `48f07123`.
- **Open question:** A Cartographer pass should first identify an earned boundary; extracting the
  new one-caller predicate alone would create the speculative seam prohibited by doctrine.
- **Priority:** low — architecture pressure exists, but no present defect justifies extraction.
- **Disposition:** `recommend-and-defer` — architecture investigation and no filing approval.
- **Issue authority:** ask user.

## tc16 — Decide whether ORIGIN_EXEMPT_VERBS should be production data

- **Classification:** cleanup, tooling
- **Source:** `FOWLER_PASS.json` speculative-generality finding
- **Structural anchor:** `scripts/checklist_engine.py::ORIGIN_EXEMPT_VERBS`
- **Observation:** Production runtime reads only `ORIGIN_GUARDED_VERBS`; the exempt constant exists
  as documentation and as the partition test's subject. Expected shipped constants either to
  participate in runtime classification or have their test-only/documentary ownership made
  explicit. **Conditions:** current engine classification implementation. **Type:** measured —
  code-object names and repository references were inspected. **Rev:** `48f07123`.
- **Priority:** low — partly earned by exhaustive new-verb coverage, with no runtime bug.
- **Disposition:** `recommend-and-defer` — requires a small design choice but was outside the
  reviewed slice and no issue filing was authorized.
- **Issue authority:** ask user.

## Routing summary

- `fixed-now`: tc6, tc7 — commit `48f07123`.
- `recommend-and-defer`: tc8–tc16 — issue-ready above; explicit tracker-write approval absent.
- `filed`: none.
- Unrouted candidates: none.
