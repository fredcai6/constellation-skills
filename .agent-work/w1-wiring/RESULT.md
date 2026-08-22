# RESULT: w1-wiring (epic 569, issues #345 / #444 / #368)

**Status: mission work complete and merge-ready; spine NOT closed. Returning to the
Admiral with two genuine obstacles rather than guessing past them (see "Obstacles" below).**

## 1. Verdict

**Mixed** — the census (taken fresh, not assumed) shows the population is mostly
built-and-tested-but-unwired, not mostly dead code, so the honest-null "delete only"
outcome does not apply. Shipped the smallest mechanism #345 asks for (options 1 and 2:
a registration lint and a vocabulary rule, both blocking, both proven to fail) plus one
dead-code deletion, plus a separate fix for a live `#444` drift the census found along
the way.

## 2. The census

Every check-shaped script in `scripts/`, classified live/unwired/dead with one evidence
string per row: **`docs/CHECK_SCRIPT_CENSUS.md`**, committed at
`09a4bbc4`/`eb01c015` (see PR #644). 26 rows: **17 live, 8 unwired, 1 dead**.

This redoes the Admiral's pasted `skills/`-only grep against CI workflows, git hooks,
cross-script calls, and — critically — pytest tests that assert a script's check
function against the **real, committed repo** (not a fixture), which the crude grep
cannot see. That last category was missed in this census's own first draft; the
correction is documented in the census itself (see "A correction made mid-census").
Concretely: `verify_retirement.py`'s own suite-gated test
(`tests/test_retirement_guard.py::test_canon_is_clean`) caught a real violation on this
census document's own line 52 mid-run, while the census still called that script
"unwired" — direct, in-session proof of the gap, fixed rather than hidden.

## 3. `generate_spine.py` disposition

**Has a live caller, but not on the path that produces any spine a shipped role skill
actually drives.** `scripts/spine_lifecycle.py::_compile_spine()` imports and calls
`generate_spine.py` directly; `spine_lifecycle.open_work()` is wired to the MCP
`spine_open` tool (`scripts/mcp_spine_server.py`), a real, tested, documented verb. But
the operational path that produced *this Commander's own spine* —
`scripts/init_work_area.py --spine <template>`, per `references/stand-up-work-area.md`
— resolves placeholders on a hand-authored `*.template.json` and never touches
`generate_spine.py` at all. Confirmed: `COMMANDER_SPINE.template.json` carries 19
`"check": null` qualitative postconditions and **0** `because` fields.

**For wave 2, unambiguously:** "half the fix already exists" is true only for
whichever thin slice of driven spines goes through `spine_open` — measured here as
none of the 19 shipped role skills. Wave 2 cannot lean on the compiler already
requiring `because`; it must either add a `because`-shaped field directly to the
hand-authored `*.template.json` discipline, or migrate the standard stand-up path to
the compiled one — a materially larger change than the epic's own framing assumed.
Full detail in `docs/CHECK_SCRIPT_CENSUS.md`'s "generate_spine.py disposition" section.

## 4. `#368` / `#444` re-measurement

- **`#368`** (Task-field group): now 5 sites, 22-field union — not the issue's stale
  "eleven". The premise ("no consistency check") is **already substantially fixed**:
  3 existing test classes in `tests/test_checklist_engine.py` form a closed
  reconciliation loop (7 passing tests, verified this run). One narrow, deliberately-
  scoped gap remains (an allowlist field the doc can omit without failing) — by design,
  not oversight; not patched.
- **`#444`** (gauge-record field group): 7 sites, 6 possible fields. **No
  reconciliation existed**, and a live, current drift was found:
  `docs/GAUGE_WRITER_HOOK.md`'s own field table — headed "the one place the record's
  shape is stated" — was missing the `owner` field added by #600. **Fixed**: the doc
  table gained the `owner` row, and `tests/test_gauge_writer.py` gained
  `GaugeRecordFieldTableReconciliation`, reusing `#368`'s proven parse-table-reconcile-
  against-code pattern.
- **One-check-vs-two**: one mechanism (the pattern), reused across two independent
  test files (their subsystems are unrelated) — not a shared caller, not forced
  unification. Full detail in `docs/CHECK_SCRIPT_CENSUS.md`.

## 5. Evidence

- **PR**: [#644](https://github.com/fredcai6/constellation-skills/pull/644), branch
  `epic-569/w1-wiring` → `main`, pushed and open (not yet merged — merge state is the
  Admiral's/human's call).
- **New check, where it runs**: `tests/test_check_script_registration.py`
  (`RegistrationLint`, `VocabularyRule`) and `tests/test_gauge_writer.py`
  (`GaugeRecordFieldTableReconciliation`) — plain pytest tests, part of `tests/`, which
  `.github/workflows/ci.yml` runs on every push/PR (`pytest tests/ -q`) and which this
  repo's own doctrine calls "the real gate." **Blocking**, not report-only — the
  adjudication was already in hand at authoring time (the census itself), so no
  promotion trigger is needed.
- **Proof each can fail**:
  - Registration lint: added a real throwaway `scripts/verify_temp_red_proof.py`,
    reran the test, watched it fail naming the exact file, deleted it, reran green.
    Also ships a permanent in-suite negative self-test.
  - Gauge reconciliation: temporarily deleted the `owner` row from
    `docs/GAUGE_WRITER_HOOK.md`, reran the test, watched it fail with the exact drift
    ("missing from the doc ['owner']"), restored it, reran green. Also ships a
    permanent in-suite negative self-test.
- **Full suite**: 3573 passed, 6 skipped, 1262 subtests passed (base commit
  `244665ee` was 3564 passed, 6 skipped — the +9 is the two new test classes; the one
  deletion carried no tests of its own).

## 6. Map impact

`map/INDEX.md` **was** stale after the deletion (60 vs 61 modules) — rebuilt via
`python -m scripts.code_map build --root .` and committed. `map/ids.jsonl` and
`docs/architecture/generated/map.json` remain **empty** — this is a pre-existing
condition at base commit `244665ee` (the `context` step returned
`DEGRADED-UNPARSEABLE`, discharged in `.agent-work/w1-wiring/map-orientation.json`),
not something this run's changes caused or could fix within scope. `AGENT_GUIDE.md`'s
Documentation Map gained a row for the new `docs/CHECK_SCRIPT_CENSUS.md`. Reported as
a triage candidate (below), not silently worked around.

## 7. Triage candidates

Filing is the disfavoured exit per the launch order; both candidates below are
**recommend-and-defer**, routed in `execute.json`'s `triage_candidates`, neither
self-filed:

1. **Empty code-map anchor system** (`map/ids.jsonl`, `docs/architecture/generated/
   map.json` both empty at this revision). Rebuilding it is a materially larger
   undertaking than this bounded wave and not one of #345/#444/#368. Affects every
   future run's `context`-step map orientation for this repo.
2. **No Task/Agent tool in this dispatched context.** See Workflow Feedback below —
   affects every wave dispatched the same way, not just this one.

Neither was fixed here; both are named plainly for the Admiral to route.

## 8. Workflow feedback

- **Underspecified: the archive step's `spine_close` call has no CLI substitution.**
  The launch order names 5 MCP tools to read as CLI verbs (`spine_lease`,
  `spine_evidence`, `spine_advance`, `spine_status`, `spine_start`) but **not**
  `spine_close`, and `checklist_engine.py`'s CLI has no `close` verb at all (verified:
  `--help` lists exactly `current, claim, heartbeat, release, start, advance, record,
  consolidate, skip, block, resume, reopen, append, amend, attest, waive, attach,
  flag-candidate`). A CLI-native equivalent exists — `scripts/spine_done_cli.py`,
  wrapping the same `spine_lifecycle.finish_work` `spine_close` uses — but its own
  docstring says plainly: *"NEVER run this against a live spine file. Every example
  and every test invocation targets a `tmp_path` fixture, never a real repo's
  `.agent-work/`."* Running it against my own live spine anyway, or hand-simulating
  `spine_close`'s effects (advance the bookend, release the lease, reap bindings, move
  the work area), is exactly what "never manually call the final `spine_advance`,
  `spine_lease release`, reap, or filesystem move" forbids. **This is the decision
  this order should have made for me and didn't**: either name a CLI substitution for
  `spine_close` too, or say explicitly that a delegated CLI-only Commander cannot
  reach a terminal archive and should always hand the last step to the Admiral.
- **Underspecified/real constraint: no Task/Agent tool in this dispatched context.**
  Commander-core's doctrine assumes a Commander can dispatch implementer/reviewer/
  plan-alternative-author/critic subagents. This dispatch had none — Bash, Read,
  Write, Edit, WebFetch, WebSearch, Skill only. Every place doctrine calls for an
  independent subagent (plan-alternatives, cold plan critic, `gN-implement`/
  `gN-review` crew pairs) was instead self-authored by this same agent, with the
  deviation stated at each occurrence rather than hidden. This measurably weakens the
  independence design-it-twice and cold-critic review exist for. **Discovered
  mid-run that the Admiral is already compensating for this**: a live,
  Admiral-dispatched independent reviewer crew (`run_crew.py`, parent
  `constellation/569`) started running against this very worktree partway through
  this session — `constellation/w1-wiring/g5-clean-room-review/reviewer/attempt-1`,
  reason logged verbatim as *"Admiral-ordered independent review: w1-wiring ran with
  no crew dispatch and self-reviewed every gate."* That confirms the gap is real and
  already known one tier up; this run's own episode
  (`episodes/active/w1-wiring-002.md`) and this feedback section are additional,
  independent evidence of the same thing.
- **Sonnet-tier finding, as invited**: this order was thorough enough that the
  sonnet-tier run did not stall on ambiguity anywhere except the two points above —
  both genuine tooling/process gaps, not places where the order under-specified the
  actual engineering work. The census methodology correction (see episode
  `w1-wiring-001`) was a self-caught reasoning gap, not something better
  specification would have prevented.
- **JSON-authoring friction**: hand-writing `execute.json` postcondition `command`
  strings with nested, JSON-escaped shell double-quotes was fragile through the
  Write/Edit tool path and produced invalid JSON twice before switching to
  `json.dump` from a throwaway Python script. See `episodes/active/w1-wiring-003.md`.

## 9. Obstacles (why this stops before a terminal archive)

1. **No safe path to `spine_close`.** See Workflow Feedback above. I have committed
   and pushed all real work, opened PR #644, and run the archive-phase episode-capture
   gate (`verify_episode_captured.py w1-wiring --store-root episodes --phase archive`
   → 4 episodes confirmed). The spine's `archive` step is `in-progress` with `p1`
   satisfied; `c1`/`c2`/`c2b`/`c4`/`c5` are not yet attested/checked, and `c3`
   ("`spine_close` is authorized as the sole final transition") is deliberately left
   unattested rather than asserted on a call I cannot make.
2. **A live Admiral-dispatched independent reviewer crew is running against this
   worktree right now** (`constellation/w1-wiring/g5-clean-room-review/reviewer/
   attempt-1`, PID confirmed alive at report time, no result yet at
   `.agent-work/w1-wiring/REVIEW_RESULT-clean-room.md`). I did not dispatch it, do not
   have its handoff, and it is not mine to wait on or interfere with — `crew-runs.json`
   / `crew-runs.json.lock` / `crew-runs/` are deliberately left uncommitted so I do not
   snapshot another process's live bookkeeping mid-flight.

**Requesting**: the Admiral either (a) integrates this reviewer's verdict and drives
the terminal `spine_close` itself (it already has the authorized channel this
delegated CLI context does not), or (b) tells me explicitly how to close a
CLI-driven delegated spine safely, so this gap is closed for every future wave
dispatched the same way, not just this one.

All substantive mission work — the census, the mechanism, the two issue
re-measurements, the fix-now deletion and doc correction, full green suite, PR — is
done and merge-ready regardless of how the terminal archive step resolves.
