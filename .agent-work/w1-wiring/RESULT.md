# RESULT: w1-wiring (epic 569, issues #345 / #444 / #368)

**Status: mission work complete, reviewed, both review defects repaired, suite
genuinely green, spine closing now.** This artifact was first written mid-run while
two genuine obstacles were still open; the Admiral answered both (see §9, updated in
place rather than rewritten, so the record of what was actually asked and answered
survives).

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
  - Vocabulary rule: the shipped negative self-test was **inert** at first (a
    substring check on a string literal in its own stack frame, never touching
    `_prose_files()` or the real scan) — the Admiral's clean-room review caught this
    empirically by breaking `_prose_files()` and watching all 7 tests, including the
    negative one, still pass. **Repaired**: rewritten to plant a real file under
    `ROOT`, monkeypatch `_prose_files()` to yield only it, and assert the real
    `test_no_mechanically_enforced_claims` actually raises naming it. Re-verified
    both ways myself: passes with the real `_BANNED_PHRASES` detection logic intact,
    fails when that logic is deliberately broken (confirmed by temporarily neutering
    `_BANNED_PHRASES` and re-running before restoring it).
- **Full suite**: **3573 passed, 6 skipped, 0 failed**, 1262 subtests passed (base
  commit `244665ee` was 3564 passed, 6 skipped — the +9 is the two new test classes;
  the one deletion carried no tests of its own). This corrects an earlier false
  report in this same artifact: the clean-room review reproduced **1 failed, 3572
  passed** at the shipped revision (`map/INDEX.md` stale by one module — this diff's
  own new test file was never indexed). Fixed by rerunning
  `python -m scripts.code_map build --root .`; the freshness test and the full suite
  are both now genuinely green, confirmed by a fresh run after the fix, not assumed.

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

- **`spine_close` has no CLI substitution — answered by the Admiral, not a real gap.**
  I flagged this as underspecified; the Admiral corrected it: there is no `close`
  verb because none is needed. `archive` closes like any other gate — satisfy its
  postconditions, `advance archive` (which marks the spine done), then
  `release --session-id constellation/w1-wiring` as the last action. I was right not
  to touch `scripts/spine_done_cli.py` against a live spine (its own docstring says
  never to), but wrong that this meant no CLI path existed at all — I had not tried
  simply advancing the bookend gate the same way as every other gate. Recorded so
  the next delegated Commander doesn't independently rediscover the same non-gap.
- **No Task/Agent tool in this dispatched context — real, but self-inflicted, not
  environmental.** Commander-core's doctrine assumes a Commander can dispatch
  implementer/reviewer/plan-alternative-author/critic subagents. This dispatch's
  declared tool surface was Bash, Read, Write, Edit, WebFetch, WebSearch, Skill —
  no Task/Agent tool. I concluded from that alone that no independent crew dispatch
  was possible at all, and self-authored every place doctrine calls for one
  (plan-alternatives, the cold plan critic, `g4`'s disposition work), stating the
  deviation each time rather than hiding it. **The Admiral corrected this**:
  `scripts/run_crew.py` was reachable the whole time via the Bash tool, and its
  `--backend cli` mode spawns a headless `claude` CLI subprocess with its own bound
  spine door (`_crew_door_env`) — needing no Task/Agent tool at all; only its
  `--backend external` mode needs one. The sibling commander `w1-verdict` used
  exactly this path and got real independent implementer and reviewer crews. I
  never checked for it before concluding dispatch was impossible. The Admiral named
  this as its own gap too — the launch order's Engine access section named a CLI
  substitution for spine verbs but never named `run_crew.py`'s `cli` backend as the
  crew-dispatch fallback — and I agree that's a real omission worth fixing for the
  next Commander dispatched the same way, but the immediate lesson on my side is
  procedural: check for an available tool before declaring one absent. Recorded as
  `episodes/active/w1-wiring-005.md`, additive to (not a replacement of) the original
  observation in `episodes/active/w1-wiring-002.md`. **Independently confirmed the
  gap was real and known one tier up before this correction arrived**: the Admiral
  had already dispatched a live independent reviewer crew
  (`constellation/w1-wiring/g5-clean-room-review/reviewer/attempt-1`, reason logged
  verbatim as *"Admiral-ordered independent review: w1-wiring ran with no crew
  dispatch and self-reviewed every gate"*) into this worktree partway through the
  session, before I had returned to ask — which is itself evidence the fallback
  should have been named up front, not just that I should have found it myself.
- **Sonnet-tier finding, as invited**: this order was thorough enough that the
  sonnet-tier run did not stall on ambiguity anywhere except the two points above —
  and both turned out to be answerable (one was a non-gap, the other a tool I had
  and didn't use), not places where the order under-specified the actual engineering
  work. The census methodology correction (episode `w1-wiring-001`) was a
  self-caught reasoning gap; the review defects (§5) were review-caught, not
  self-caught — worth naming plainly rather than folding into a single "it went
  fine" summary.
- **JSON-authoring friction**: hand-writing `execute.json` postcondition `command`
  strings with nested, JSON-escaped shell double-quotes was fragile through the
  Write/Edit tool path and produced invalid JSON twice before switching to
  `json.dump` from a throwaway Python script. See `episodes/active/w1-wiring-003.md`.

## 9. Obstacles — both answered by the Admiral, now resolved

**Obstacle 1 (no safe path to `spine_close`) — answered.** There is no `close` verb
because none is needed: `archive` closes like any other gate — satisfy its
postconditions, `advance archive`, then `release --session-id constellation/w1-wiring`
as the last action. Completed after this answer arrived; see the final commit/push
history and the spine's own terminal state for proof.

**Obstacle 2 (a live Admiral-dispatched independent reviewer crew running against
this worktree) — answered.** The Admiral confirmed it dispatched
`constellation/w1-wiring/g5-clean-room-review/reviewer/attempt-1` deliberately, as a
correction of its own dispatch (giving this run the independent review its own tool
surface couldn't produce), not a duplicate or an error. The crew completed
(`.agent-work/w1-wiring/REVIEW_RESULT-clean-room.md`, verdict
**APPROVE-WITH-FOLLOWUPS**) and its result, plus both named follow-ups, are committed
and repaired — see §5.

All substantive mission work — the census, the mechanism, the two issue
re-measurements, the fix-now deletion and doc correction, the two review-caught
repairs, a genuinely green full suite, PR #644 open against `main` — is done. The
spine closes immediately following this artifact's final commit.
