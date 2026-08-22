# Check-script census — epic 569, wave w1-wiring

Source of truth for whether this repo's "built but not wired" pattern (issues #345, #444, #368)
deserves a mechanism. Taken fresh at base commit `244665ee`, redoing the Admiral's own pasted grep
(`LAUNCH_ORDER-w1-wiring.md`, "The measurement that motivated this") properly, per that section's own
instruction: a crude `skills/`-only grep cannot tell a script invoked from a CI workflow, a git hook, a
pytest test, or another script from one nothing calls at all.

## Method

For each `scripts/{verify,check,prove,measure}_*.py` (26 at this commit), checked in this order and
recorded in the Evidence column:

1. Does it appear inside a `"kind": "command"` block in a shipped `skills/*/templates/*.json`? →
   **live**, mechanically gated.
2. Is it invoked as a real step in `.github/workflows/*.yml`? → **live**, CI-gated.
3. Is it imported/invoked from `scripts/hooks/*.py`? → **live**, hook-gated. (None were.)
4. Is it called **unconditionally, from inside another script's own code** (a hard function call an
   operator cannot skip by forgetting a separate step) — where that caller is itself reachable from (1),
   (2), (3), a role's `SKILL.md` real operational instruction, or another such caller? → **live**,
   transitively wired.
5. Does a `tests/` test call its check/scan/verify function **unconditionally against the real,
   committed repo** (`ROOT`/`REPO_ROOT`, not a temp dir or an authored fixture) and assert pass/fail on
   the result — so a real regression in the repo would fail that test, and that test is part of the
   suite `.github/workflows/ci.yml` runs (`pytest tests/ -q`)? → **live**, suite-gated. This was found
   by re-checking every "no caller" candidate's own test file after `verify_retirement.py`'s
   `test_canon_is_clean` caught a real violation in this census's own first draft (below) — proof this
   category is not academic. A test that only exercises the checker against synthetic/fixture input
   checks the *tool's* correctness, not the *repo's*; that case falls through to (6).
6. Otherwise: does it have its own dedicated pytest coverage, doc references, and a still-current
   purpose? → **unwired** (built, usually tested and documented, but nothing outside its own test suite
   or its own prose mentions invokes it — the exact "built but not wired" pattern this census exists to
   measure).
7. Otherwise (no test coverage, no current caller, purpose superseded or one-off): **dead**.

**A defined exclusion, stated plainly so it is checkable:** a script that is merely *named in a role's
`SKILL.md` as a separate, optional CLI step* ("run `verify_X.py <arg>`") is **not** counted live by that
mention alone. That instruction is prose — the two-bin rule (`docs/agents/GLOSSARY.md`) says enforced
means checked by command or attested by a named human, and an agent can skip a prose-named step with
nothing refusing. This is different from a script called unconditionally from *inside* another live
tool's own function body, which cannot be skipped by omission, and different again from category (5)
above. One script below (`verify_diagnosis.py`) is unwired by this distinction alone; a second
(`verify_skill_registered.py`) is prose-instructed by this same distinction **and separately** live via
category (5) — both are stated, not silently folded into one bucket.

**A correction made mid-census, reported rather than hidden.** The first draft of this census applied
categories (1)-(4) and (6)-(7) only, missing (5) — it treated "has a dedicated test" as evidence of
*coverage*, not of *enforcement*, without checking whether any of those tests actually assert against
the real repo. Running the full suite against that first draft's own disposition work (see
**Disposition** below) tripped `verify_retirement.py`'s own `unapproved-store-mention` guard on a line
this census itself had just written — a live check, in the suite, catching a real thing, while this
census still called `verify_retirement.py` "unwired." That failure is what prompted re-checking every
other "unwired" candidate's test file for the same pattern; five were reclassified as a result
(`verify_retirement.py`, `verify_context_declaration.py`, `verify_coverage_ledger.py`,
`verify_skill_registered.py`, `check_template_overlay_freshness.py`) and one launch-order framing
(`check_template_overlay_freshness.py`'s predicted "sharp irony") is retracted below, not merely
corrected quietly.

## Census

| Script | Classification | Evidence |
|---|---|---|
| `verify_cycles.py` | live | `skills/explorer/templates/EXPLORER_SPINE.template.json:37` command check |
| `verify_episode_captured.py` | live | `skills/admiral/templates/ADMIRAL_SPINE.template.json:56`, `skills/commander/templates/COMMANDER_SPINE.template.json:118,128` command checks |
| `verify_fowler_pass.py` | live | `skills/reviewer/templates/REVIEW_SURVEY.template.json:53` command check |
| `verify_interrogation.py` | live | `skills/interrogator/templates/INTERROGATION.template.json:28` command check |
| `verify_iterative_role_artifacts.py` | live | `skills/admiral/templates/ADMIRAL_SPINE.template.json:42`, `skills/commander/templates/COMMANDER_SPINE.template.json:74`, `skills/explorer/templates/EXPLORER_SPINE.template.json:68` command checks (this run's own `execute` step ran it) |
| `verify_spec_confirmed.py` | live | `skills/explorer/templates/EXPLORER_SPINE.template.json:56,67` command checks |
| `verify_state_note.py` | live | `skills/admiral/templates/ADMIRAL_SPINE.template.json:37`, `skills/commander/templates/COMMANDER_SPINE.template.json:70` command checks (this run's own `execute` step ran it) |
| `verify_skip_guard.py` | live | `.github/workflows/ci.yml` "Skip guard" step calls it directly on `junit-report.xml`. Missed by the Admiral's `skills/`-only grep — the first correction this redo makes. |
| `verify_worktree_isolation.py` | live | `scripts/spine_lifecycle.py:459-466` calls `verify_worktree_isolation.check_distinct_real(...)` unconditionally inside `open_work()`'s self-verify step (step 8 of real spine minting), not merely the ad hoc admiral-run CLI use the launch order describes |
| `verify_issue_set.py` | live | `scripts/file_issue_set.py:262,307` calls `verify_issue_set(manifest, brief)` unconditionally inside the filer's own code; `file_issue_set.py` is named as a real operational step in `skills/to-initial-issues/SKILL.md:32` ("On an authorized filing go-ahead, run `scripts/file_issue_set.py`") |
| `verify_episode_observations.py` | live | `scripts/apply_episode_delta.py:936-937,959` imports it as the write-time instruction-shaped-statement guard, called unconditionally from `_apply_create`/`_apply_restate_assertion` on every real episode write (`apply_episode_delta.py` is the sole episode write path, doctrine-cited) |
| `verify_declared_dispatch.py` | live | narrow-path (see note below the table) — `scripts/generate_spine.py:589-598` (`_compile_dispatch_entry`) auto-injects a `command`-kind postcondition running this script for every authored `[[gate.dispatch]]` entry. That compiler path is itself live (see `generate_spine.py` disposition below) — but it is **not** the path that produced this very commander's own spine, so this script is dead weight on the operational template-instantiation path even though it is reachable via the compiler path |
| `verify_context_declaration.py` | live | Category (5): `tests/test_context_declaration_lint.py::test_lint_passes_over_real_shipped_spine_templates` and `::test_default_discovery_finds_the_commander_spine_and_passes` call its lint unconditionally against every real `skills/*/templates/*.json`, asserting exit 0 -- a real regression in a shipped template fails the suite. No `command`-kind check in any template itself. |
| `verify_coverage_ledger.py` | live | Category (5): `tests/test_verify_coverage_ledger.py::test_real_repo_ledger_passes` calls `main([])` (default = real repo root) and asserts exit 0 against the actual `docs/removability_ledger.json`/`docs/installed_externals_manifest.json`. |
| `verify_diagnosis.py` | unwired | prose-instructed (see note above) — `skills/diagnose/SKILL.md:55` step 3 instructs "Clear the rail: `python <skill-dir>/scripts/verify_diagnosis.py <finding.json>`" — a real, separately-run CLI step named in prose, not gated by any `command`-kind check; an agent following the Diagnose role could skip it with nothing refusing. 1 test ref. |
| `verify_epic_418_demo.py` | unwired | `scripts/verify_iterative_planning_acceptance.py:57` dynamically loads it (`_load`), but that caller is itself unwired (below) — no live path reaches either. 1 test ref. Historical one-time acceptance proof for epic #418. |
| `verify_installed_bundles.py` | unwired | Referenced only in **comments** in `scripts/install_constellation.py:488,1674` ("reconstructs this dataclass from an..."), never actually imported or called there. 2 test refs. |
| `verify_iterative_planning_acceptance.py` | unwired | "Verify all ten frozen iterative-planning acceptance items offline" — reads as a durable regression suite for the still-live iterative-planning feature (`REPLAN_INPUT.json`, `verify_iterative_role_artifacts.py`), but nothing re-runs it; only its own 1 test ref calls it. |
| `verify_retirement.py` | live | Category (5), found the hard way: `tests/test_retirement_guard.py::test_canon_is_clean` calls `verify_retirement.scan(REPO_ROOT) == []` unconditionally. It caught a real violation on this census's own first draft (see the correction note above) -- direct, in-session proof this is a live, suite-enforced guard, not merely the manual command `AGENT_GUIDE.md` also documents. |
| `verify_skill_registered.py` | live | Category (5): `tests/test_write_a_skill.py::test_write_a_skill_clears_its_own_rail` and `::test_new_lean_replan_skill_is_registered_and_clears_the_mint_rail` call it unconditionally against the real `skills/` corpus ("Uses the live registration maps + the real skills/ corpus"). Also separately prose-instructed in `skills/write-a-skill/SKILL.md:36` -- both are true; the suite-gated path is what makes it live, not the prose step alone. |
| `check_corpus_freshness.py` | unwired | Referenced only in comments in `scripts/install_constellation.py:2219,2252`; not called there. 1 test ref. |
| `check_role_spine_bookends.py` | unwired | Referenced only in `check_template_overlay_freshness.py`'s docstring (prose comparison, no import/call). 2 test refs. |
| `check_skill_freshness.py` | unwired | Named in `install_constellation.py`'s printed human-facing messages ("Run `check_skill_freshness.py` to reconcile") at 5 sites — advisory text, never an actual call. 3 test refs. |
| `check_template_overlay_freshness.py` | live | Category (5), and the launch order's predicted "sharp irony" is **retracted, not confirmed**: `tests/test_check_template_overlay_freshness.py::test_real_repo_overlay_has_no_stale_templates` calls `CTOF.check(REPO_ROOT)` unconditionally and asserts no template is stale -- its own docstring: "the next time skills/ moves and the overlay does not follow, this is what says so." Zero references in `skills/`, CI workflow, or hooks directly, but the suite-gated test is real enforcement the crude grep cannot see. |
| `prove_docstring_only.py` | dead | Zero test references (the only script in the 26 with none). No caller anywhere in current `scripts/`, `tests/`, `skills/`, `.github/`. Appears only in **archived** `.agent-work/archive/` run artifacts from three already-closed efforts (epic-298 twice, issue-305, epic-418-redux), each an ad hoc one-time manual proof, never promoted to a reusable, tested mechanism. |
| `measure_overread.py` | unwired | Real, tested (`tests/test_measure_overread.py`), actively used as a **measurement instrument** across multiple epic-567 launch orders and `skills/_shared/global-everyone.md`'s own doctrine ("Enforcement lint is deliberately deferred until post-ship `measure_overread.py` evidence shows the rule is broken often enough"). Deliberately manual-invocation-only; not miscategorized as forgotten. |

**Row count: 26.** **Classification counts: 17 live (7 template-command-check, 1 CI-workflow, 4
cross-script/hard-call, 5 suite-gated-test, 1 compiler-path-only — `verify_declared_dispatch.py`
double-counts into both the cross-script and compiler-path notes above, so these sub-tallies sum to
18 against 17 rows by design), 8 unwired, 1 dead.**

This corrects the Admiral's pasted pre-census in three directions, not one: it moves
`verify_skip_guard.py`, `verify_worktree_isolation.py`, `verify_issue_set.py`,
`verify_episode_observations.py`, and `verify_declared_dispatch.py` from "zero references" into
**live** by checking CI, hooks, and cross-script calls the `skills/`-only grep is blind to, exactly as
the launch order predicted; then, on top of that first pass, catching this census's **own** initial
under-count (see the correction note above) moves `verify_context_declaration.py`,
`verify_coverage_ledger.py`, `verify_retirement.py`, `verify_skill_registered.py`, and
`check_template_overlay_freshness.py` from "unwired" into **live** by checking whether a `tests/` test
asserts each one against the real repo, not merely covers its logic. `check_template_overlay_freshness.py`
in particular **retracts** the launch order's predicted "sharp irony" rather than confirming it: it is
genuinely enforced, by a suite-gated test the `skills/`-only grep (and this census's own first pass)
both missed.

## generate_spine.py disposition

**`generate_spine.py` has a genuinely live caller** — `scripts/spine_lifecycle.py::_compile_spine()`
(lines 377-390) imports it directly and calls `generate_spine.spec_shape_faults`, `compile_spec`, and
`probe_spec` (`spine_lifecycle.py:94,381,385,387`). `_compile_spine` is called from
`spine_lifecycle.open_work()` (line 445), which is wired to the **`spine_open` MCP tool**
(`scripts/mcp_spine_server.py:1552`) — a real, documented (`skills/_shared/checklist-engine.md`),
heavily-tested MCP door verb (`tests/test_mcp_spine_bind.py`, `tests/test_mcp_door_unbound.py`,
`tests/test_mcp_lifecycle.py`, `tests/test_mcp_identity.py`, and others). The launch order's own
`grep -rln generate_spine skills/` (returning only `docs/CHECKLIST_SCHEMA.md`) is accurate for that
literal scope but undersells the picture: it was scoped to `skills/` only, and the real caller lives in
`scripts/`.

**But that live path is not the one that produces the spines actually driven by real Commander/Admiral/
Crew work — including this very run's own spine.** Per `references/stand-up-work-area.md` (the doctrine
this run's own dispatcher followed), a Commander's `spine.json` is produced by
`scripts/init_work_area.py --spine <template>`, which resolves placeholders in a **pre-authored,
hand-written** `*.template.json` (e.g. `COMMANDER_SPINE.template.json`) and **never imports or calls
`generate_spine.py` at all**. Confirmed directly: `grep -c '"because"' skills/commander/templates/
COMMANDER_SPINE.template.json` → **0**, against **19** `"check": null` qualitative-style postconditions
in that same file. No skill's `SKILL.md` or spine template instructs an agent to call the MCP
`spine_open` tool as its means of standing up a bounded-issue run; `spine_open` is exercised by the
engine's own test suite and exists (per `skills/_shared/checklist-engine.md`) for "a session that starts
with nothing bound" to mint its own work directly through the MCP door — a real, tested capability, but
not the path any of the 19 shipped role skills route through today.

**Consequence for epic 569 wave 2, stated unambiguously:** `generate_spine.py`'s `because`-requiring
compile step (`generate_spine.py:200-204`) is real and live, but it is invisible to essentially all of
the 65 `check: null` qualitative conditions the epic's own measurement counted, because those conditions
live in hand-authored `*.template.json` files that are never compiled — `init_work_area.py` performs
pure placeholder substitution on them, nothing else. "Half the fix already exists" is true only for
whatever thin slice of driven spines goes through `spine_open`/`generate_spine.py` (measured here as:
none of the 19 shipped role skills). Wave 2 cannot lean on the compiler already requiring `because` to
close the 65-condition gap; it must either (a) add a `because`-shaped field directly to the hand-authored
`*.template.json` authoring discipline (bypassing the compiler, since these files are never compiled), or
(b) migrate the standard work-area stand-up path from `init_work_area.py`'s raw substitution to
`spine_lifecycle.open_work()`'s `generate_spine`-compiled path — a materially larger architecture change
than wave 2's own framing assumed. This choice is wave 2's to make, not this wave's; it is reported here
because the launch order named it as the fact wave 2 is blocked on.

`generate_spine.py` disposition, one line: **has a live caller (via `spine_lifecycle.py` → MCP
`spine_open`), but that caller is not on the path that produces any spine actually driven by a shipped
role skill today.** Do not delete it — it is real, tested, load-bearing for the `spine_open` verb — but
do not build wave 2 on the assumption that authoring a `because`-carrying spec and compiling it is what
happens today.

## #368/#444 re-measurement

### `#368` — the Task-field group

The group is the checklist engine's `Task` field set, independently declared across what is now
**5 sites**: (1) the engine's own canonical builder (`checklist_engine.py::_build_amend_task`/`append`,
read via `tests/test_checklist_engine.py::_builder_task_keys()`, fenced — read, not edited, this run);
(2) `docs/CHECKLIST_SCHEMA.md`'s `## Task` field table; (3) `TaskFieldCompleteness._EXCLUDED_FIELDS`
(the completeness-loop's stated exclusion set); (4) `TaskFieldCompleteness._fully_populated_gate()`
(the completeness test's fixture); (5) `TemplateOnlyFieldAllowlist.ALLOWLIST` (the template-only field
allowlist commit `244665ee` extended with `map_check_note`).

**Current count, taken from the live code, not the issue text:** builder emits **14** fields;
`TemplateOnlyFieldAllowlist.ALLOWLIST` (template-only fields) carries **8** fields (`anchors`,
`bookend`, `context_headroom_note`, `context_headroom_tokens`, `context_refs`, `kind`, `map_check_note`,
`why_exempt`); union = **22** fields. `docs/CHECKLIST_SCHEMA.md`'s Task table lists **19**. The
`#368`-era "eleven" is stale by more than the one field the launch order flagged — the group has grown
materially since the issue was filed.

**#368's premise ("no consistency check") is already substantially fixed, not open.** Three live test
classes (`tests/test_checklist_engine.py`: `TaskFieldCompleteness` #420/#433, `TemplateOnlyFieldAllowlist`
#475, `SchemaDocFieldReconciliation` #476) form a closed reconciliation loop —
builder-keys-are-a-subset-of-fixture-keys, shipped-templates'-fields-are-accounted-for-by-builder-or-
allowlist, and doc-table-reconciles-with-builder-plus-allowlist — all 7 tests pass at this commit
(verified: `python -m pytest tests/test_checklist_engine.py -k "TaskFieldCompleteness or
TemplateOnlyFieldAllowlist or SchemaDocFieldReconciliation" -q` → `7 passed`). Commit `244665ee`'s own
change (adding `map_check_note` to both the allowlist and the schema doc) is exactly what this
established discipline requires to stay green.

**One narrow, already-acknowledged gap remains, by design, not by oversight.**
`SchemaDocFieldReconciliation` checks `undocumented_builder` (builder fields missing from the doc) and
`unaccounted_doc` (doc fields not accounted for by builder-or-allowlist) — but **not** the third
direction: an allowlist field the doc omits. Measured directly: `context_headroom_note`,
`context_headroom_tokens`, and `kind` are in the allowlist but absent from the doc table's 19, and the
test does not catch this — its own docstring says why: "a field the allowlist carries but the doc omits
is not itself a failure here," to keep the doc **verifiable** against the engine rather than
**authoritative** over it. Not fixed in this wave: it is a stated, deliberate design choice in the
existing mechanism, not an accidental drift the "smallest fix" principle calls for patching, and
`docs/CHECKLIST_SCHEMA.md` is outside this run's editable scope beyond what the mission names.

### `#444` — the gauge-record field group

The group is the context-governor gauge record's field set, declared across **7 sites**:
(1) `scripts/gauge_reader.py::REQUIRED_FIELDS` (4-tuple); (2) `scripts/gauge_reader.py`'s `Reading`
dataclass; (3) `scripts/hooks/gauge_writer_hook.py`'s write-dict literal (the real writer); (4)
`docs/GAUGE_WRITER_HOOK.md`'s field table; (5) `tests/test_gauge_writer.py`'s own asserted field set
(line 152); (6) `tests/test_gauge_reader.py`'s `FRESH_RECORD` fixture; (7) `tests/test_checklist_engine.py`'s
own gauge-record literals used for Trip-policy tests. This matches the issue's "seven assertion sites"
naming.

**Current count:** 4 required fields (`schema_version`, `fill_fraction`, `model`, `observed_at`), plus
2 conditional fields — `owner` (added by #600, present whenever the candidate has one) and
`identity_resolution_ms` (dispatched agents only, #419) — 6 possible fields total, not the 4 the doc's
own field table names.

**Unlike `#368`, no reconciliation check exists for this group, and the drift it predicts is live and
present right now, not hypothetical.** `docs/GAUGE_WRITER_HOOK.md`'s own field table is headed "This is
the one place the record's shape is stated; everything else in this document points here" — but that
table lists only 5 rows (`schema_version`, `fill_fraction`, `model`, `observed_at`,
`identity_resolution_ms`); it omits `owner`, even though the same document's own prose three sections
earlier (line 43) says the writer adds "`owner` whenever the candidate has one (#600)," and
`tests/test_gauge_writer.py:152` asserts the real record carries exactly `{schema_version, fill_fraction,
model, observed_at, owner}`. The doc's canonical table has been stale since #600 shipped, inside the same
file that names itself authoritative. No test parses this table the way `_doc_task_field_table()` parses
`docs/CHECKLIST_SCHEMA.md`'s Task table for `#368`'s group.

**Fixed in this wave (fix-now triage, bounded, in scope):** `docs/GAUGE_WRITER_HOOK.md`'s field table
gained the missing `owner` row, and `tests/test_gauge_writer.py` gained a reconciliation test —
`test_field_table_reconciles_with_reader_and_writer` — mirroring the proven `#368` pattern
(`_doc_task_field_table`/`_assert_doc_reconciles_with_builder`): it parses the doc's field table and
asserts it names exactly `gauge_reader.REQUIRED_FIELDS` plus the named conditional fields
(`owner`, `identity_resolution_ms`), so a future field added to the writer or the reader without a
doc-table update fails the suite instead of silently drifting further. See **Disposition** below.

**One-check-vs-two verdict:** **one mechanism, reused, covers both groups.** Both are structurally
comparable — a hand-authored Markdown field table plus one or more Python field-list sources of truth —
so the same parse-the-table-and-reconcile-against-code pattern `#368`'s existing tests already prove out
applies directly to `#444`'s group. They are not forced into artificial unification: `#368`'s mechanism
already existed and needed no new code, `#444`'s needed the pattern newly applied, and the two live in
their own respective test files (`tests/test_checklist_engine.py` for Task fields, fenced and unedited
this run; `tests/test_gauge_writer.py` for gauge fields, edited this run) rather than one shared module —
this is a repeated pattern, not a shared caller, which is the right shape given the two groups belong to
unrelated subsystems.
