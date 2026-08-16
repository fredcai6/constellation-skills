# Implementation Result

## Assigned gate
`g3` — issue #603, **rework attempt 2** (mechanical blockers only; the substance of `4e1f22cb`
was untouched and not re-litigated).

## Completed slice
Commit `359d93df` — three doc references now name the mechanism that runs, and `map/INDEX.md`
is rebuilt against the staged tree. 3 files, 13 insertions, 9 deletions.

Both blockers are closed, and blocker 1 closed for the reason the handoff predicted: the
freshness guard went green from a map rebuild alone, with no test edited and no behaviour
touched. The map was only ever short by the one test module that was still untracked when the
previous rebuild ran.

## Scope
**Files changed:**
- `scripts/mcp_spine_server.py` — two docstrings, nothing else
- `examples/mcp-interactive-demo/README.md` — one paragraph
- `map/INDEX.md` — regenerated, never hand-edited

**Specific exclusions touched:** `no`. `_identity_violation`, `checklist_engine.py`,
`scripts/hooks/**`, `run_crew.py`, `gauge_reader.py`, `install_constellation.py` and the
refuted `SPINE_ENGINE` triage candidates are all untouched — confirmed by the commit's own
file list above. The fourth stranded reference I found lives in `scripts/hooks/spine_rail.py`
and I did **not** fix it for exactly this reason; it leaves as a triage candidate.

## Behavior changed
`no`. The server diff is two docstrings. The door's own four test modules
(`test_mcp_door_unbound.py`, `test_mcp_lifecycle.py`, `test_mcp_identity.py`,
`test_mcp_spine_server.py`) pass, including `test_mcp_lifecycle.py:194`'s identifier ban over
`_spine_open`'s own source — the docstring I rewrote sits inside the banned function, and the
ban is AST-scoped, so it stays green without being weakened.

## What the three fixes now say

| Location | Was | Now |
|---|---|---|
| `mcp_spine_server.py:685` | appends to `REJECTIONLOG`, deleted by `4e1f22cb` | appends to `_rejectionlog()`, the derivation that replaced it — and which returns `None` when nothing is bound, already documented at `:704-708` |
| `mcp_spine_server.py:962-965` | root comes from `_primary_checkout_for_lifecycle` "(ambient `SPINE_FILE`, re-read fresh)" | that function reads **no environment at all**: the bound spine's own checkout when there is one, this script's own location when there is not |
| `README.md:68-71` | cites `test_mcp_json_referenced_spine_file_exists_and_loads`; calls the demo a fixture `.mcp.json` "points at" | cites `test_mcp_json_spine_file_is_overridable_and_any_default_loads`; "pointed at", plus one clause noting the default is empty since #603 and the test still holds any default that reappears to the same standard |

The second was the one that mattered. `spine_open` exists to serve an **unbound** door, and its
own docstring claimed its repo root came from an ambient `SPINE_FILE` read — the exact
`os.environ` read `4e1f22cb` removed *because* it raised `KeyError` on that path. The sentence
contradicted the tool's reason for existing.

**One line beyond the handoff's letter, declared:** the handoff scoped the README to "the
stranded test name". I also changed `points at` → `pointed at` in the same sentence. The same
commit emptied `.mcp.json`'s default, so the present tense was false; it is the same class of
defect, one word, same sentence. Say so if you want it reverted.

## Map Impact
- **Structural anchors touched:** `scripts/mcp_spine_server.py` — `_log_rejection` and
  `_spine_open` docstrings only; no symbol added, removed, renamed or re-signatured.
- **Capabilities added/changed/affected:** none — see "Behavior changed".
- **Constraints/assumptions touched:** the inherited `global-everyone.md` rule *"enumerate the
  blast radius of your own change — by command, never by memory"* was applied as the gate's own
  method, not just honored.
- **Decision candidates / resolved decisions:** none. `decision:one-spine-per-process-stands`,
  `decision:fail-closed-beats-fail-open` and `decision:bind-on-open-over-new-verb` are all
  untouched, as the handoff stated.
- **Trust limitations / drift found:** the two `map/scripts.mcp_spine_server/` pages the handoff
  asked me to commit **are not tracked files**. `.gitignore:73` ignores `map/*` except
  `INDEX.md` and `ids.jsonl`. They regenerate locally and are correct now, but they cannot
  appear in any commit; only `map/INDEX.md` can, and it does.
- **Triage candidates:** one, `tc1`, recorded in the plan — see "Out-of-scope observations".

## Test mode
**Required:** `test-after` — this rework is documentation plus a generated index, and "any
behaviour change" is an explicit stop condition, which forecloses TDD.
**Satisfied:** `yes`. The existing suite is the check, and it ran clean-env and green.

## Evidence

**Load-bearing 1 — full clean-env suite, green with the count.**

```bash
find . -name __pycache__ -type d -not -path "./.git/*" -exec rm -rf {} +   # issue #597
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

**Result:** `pass` — **3093 passed, 6 skipped, 1153 subtests passed** in 125.87s, exit 0.
Transcript: `.agent-work/cleanup-a-door/evidence/g3-rework-full-suite.txt`. The engine re-ran
this same command as `m4-suite`'s own postcondition check, so it is measured twice.

The previous attempt's only failure was
`MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`. It passes
now, and passes from a rebuild alone.

**Load-bearing 2 — the blast-radius sweep, with its before and after counts.**

The identifier list is derived *from the commit*, never from the handoff's table:

```bash
git show 4e1f22cb -U0 | grep -E '^-' \
  | grep -oE '^-\s*(def [_a-zA-Z0-9]+|class [_a-zA-Z0-9]+|[A-Z][A-Z0-9_]{2,} *=)' \
  | sed -E 's/^-\s*(def |class )?//; s/ *=$//' | sort -u
# -> CALLLOG ENGINE REJECTIONLOG SPINE START_MARKER
#    test_mcp_json_referenced_spine_file_exists_and_loads
#    test_removed_spine_directory_still_runs
# ENGINE and SPINE survive as module globals (re-bound, not removed).

git grep -nw -E 'CALLLOG|REJECTIONLOG|START_MARKER|test_mcp_json_referenced_spine_file_exists_and_loads|test_removed_spine_directory_still_runs'
git grep -n 're-read fresh'          # the claim the commit invalidated without renaming anything
git grep -n 'os\.environ\[.SPINE_FILE.\]' -- ':!.agent-work'
```

**Result:** `pass`. Full output, both passes:
`.agent-work/cleanup-a-door/evidence/g3-rework-blast-radius.txt`.

- **BEFORE: 4** stranded references, all documentation. **The handoff's table named 3.**
- **AFTER: 0** in scope; **1** survives, deliberately, inside the lane-B/C fence.

| # | Location | Disposition |
|---|---|---|
| 1 | `scripts/mcp_spine_server.py:685` | fixed |
| 2 | `scripts/mcp_spine_server.py:962-963` | fixed |
| 3 | `examples/mcp-interactive-demo/README.md:69` | fixed |
| 4 | `scripts/hooks/spine_rail.py:1081` | **not fixed — fenced.** Triage candidate `tc1` |

Not stranded, deliberately left alone: `notes-a.md:12,15,35` is the commander's lane-A notes,
headed *"Base a69bbac4"* and describing the pre-fix defect at pre-fix line numbers — a dated
record, correctly pinned; rewriting it would falsify it. Everything under `.agent-work/**`
(archive, handoffs, results, plans, evidence) is the same: each is a statement about the tree
as it stood when written.

The sweep also taught one thing worth carrying: **a blast-radius grep for a removed identifier
must be word-bounded.** My first version of the check was not, and it flagged the surviving
environment-variable names `SPINE_CALLLOG` and `SPINE_START_MARKER` — overrides this change
deliberately preserves. Corrected through the engine's `amend`/`retext-check`, recorded in the
plan's `amendments`, never by hand-editing the JSON.

**Confirmatory 3 — the rework commit's diffstat.**

```bash
git show --stat 359d93df
```

**Result:** `pass` —

```
 examples/mcp-interactive-demo/README.md | 9 +++++----
 map/INDEX.md                            | 5 +++--
 scripts/mcp_spine_server.py             | 8 +++++---
 3 files changed, 13 insertions(+), 9 deletions(-)
```

`map/INDEX.md` is **3 insertions, 2 deletions** — exactly the number the reviewer measured at
this commit. That agreement is what confirms the diagnosis rather than merely restating it.
Captured at `.agent-work/cleanup-a-door/evidence/g3-rework-diffstat.txt`.

## TDD evidence, if required
Not required — test-after, per the stop condition forbidding behaviour change. No test was
written, edited or deleted in this rework.

## Docs/contracts touched
- `scripts/mcp_spine_server.py` — `_log_rejection` and `_spine_open` docstrings
- `examples/mcp-interactive-demo/README.md` — the "Why it lives here" paragraph
- `map/INDEX.md` — regenerated

## Assumptions
- The three `map/scripts.mcp_spine_server/` pages regenerate correctly but are untracked, so
  "committed" for them means "correct on disk". Only `map/INDEX.md` is a committable map
  artifact in this repo.
- `.agent-work/**` and `notes-a.md` are dated records, not live documentation, so a reference
  to a since-renamed identifier in them is history rather than drift.

## Stop conditions hit
`none`. No behaviour change was required; the map rebuild did produce a green suite; the
blast-radius sweep found nothing that was not a doc reference — the fourth hit is a docstring,
which is why it is a triage candidate and not a block; scope was not exceeded.

## Out-of-scope observations

**`tc1` — `scripts/hooks/spine_rail.py:1081`, the fourth stranded reference.**
`_handle_door_lease`'s docstring quotes `SPINE = Path(os.environ["SPINE_FILE"]).resolve()` as
`mcp_spine_server.py`'s *"existing contract"*. `4e1f22cb` deleted that exact line. Two things
are now wrong and the second is substantive rather than cosmetic:

1. The expression no longer exists.
2. After bind-on-open, the door's binding can **change at runtime**. So `SPINE_FILE` in the
   hook process's environment is no longer guaranteed to name the spine the door is currently
   bound to — which is precisely the inference `_handle_door_lease` makes, and it feeds
   `decision:door-binding-source-of-truth`.

Not touched: `scripts/hooks/**` is fenced to lanes B and C by this handoff's own exclusions.
Worth routing to whichever lane owns that file, as correctness, not tidiness.

**A third firing of the stale-map trap is not currently loaded.** Five untracked `.py` probe
scripts sit under `.agent-work/cleanup-a-door/g3-review/`, which looks like the same setup that
fired twice. It cannot fire from them: `scripts/code_map/discovery.py:16` excludes the
`.agent-work/` prefix from the mappable corpus outright. The trap needs an untracked `.py`
**outside** `.agent-work/`, and there is none right now.

## Workflow Feedback

- **Handoff gaps:** two, both factual rather than unclear. (a) *"regenerate the two
  `map/scripts.mcp_spine_server/` pages"* under **Allowed scope → `map/**`** and *"Committed —
  `map/**`"* under **Deliverable path check** cannot both be satisfied: `.gitignore:73` makes
  those pages untracked. The Deliverable path check's own `git check-ignore` probe would have
  caught this — it was stated as exiting 1, but `git check-ignore map/scripts.mcp_spine_server/_log_rejection.md`
  exits 0. It looks like the probe was run against `map/` rather than against a file inside it.
  (b) **Blocker 2**'s table of three is presented as near-complete ("confirm there is no
  fourth"); there is a fourth, and it sits in a file the same handoff fences off — so the
  sweep's real output was a routing decision, not a confirmation.
- **Context rediscovered:** what `REJECTIONLOG`, `CALLLOG` and `START_MARKER` were *renamed
  to*. The handoff named the stale identifiers but not their successors, so each had to be
  traced back through `_telemetry_path` before the docstring could be rewritten. One column of
  "→ now" in the blocker-2 table would have carried it.
- **Instructions improvised around:** the crew skill says a dispatched crew drives the spine
  bound in its environment and must *not* author its own plan. My `SPINE_FILE` is the
  **Commander's** `spine.json`, leased by `commander-cleanup-a-door` and sitting on the
  `execute` step — not a crew spine, and not mine to drive. I followed the local convention
  instead (`crew-plans/g<N>-implementer-plan.json`, as g1/g2/g3 attempt 1 all did) and authored
  `crew-plans/g3-rework-implementer-plan.json` under session
  `constellation/cleanup-a-door/g3-rework/implementer/attempt-1`. The skill's two branches —
  "a spine is bound for you" and "nothing is bound" — do not cover "a spine is bound, but it
  belongs to your parent."

  The same gap fires a second way, and it will fire on **every** crew you dispatch: the spine
  stop hook keys on `SPINE_FILE`, so at the end of this run it reported *"SPINE MID-FLIGHT:
  gate execute is still open — you are in the MIDDLE of the spine"* and instructed me to load
  `constellation-commander`, rewrite `STATE_NOTE.md` and drive `execute.json` gate by gate.
  That gate is yours — `LEASE active: commander-cleanup-a-door` — and my own work file reports
  `DONE: no open items`, lease released. I did not act on it: a crew driving its Commander's
  `execute` gate is precisely what the lease exists to prevent, and I ran no mutating verb
  against your `spine.json`. Read-only `current` on both files is how I confirmed which was
  which. Worth teaching the hook to compare the bound spine's lease holder against the calling
  session before it declares a crew mid-flight.
- **What would have made this easier:** state the test mode explicitly. This handoff has no
  **Test mode** field; it is inferable (documentation-only work plus a stop condition banning
  behaviour change ⇒ test-after), but the result template requires the value verbatim, so every
  rework handoff without the field forces the same inference.

## Return status
`complete`
