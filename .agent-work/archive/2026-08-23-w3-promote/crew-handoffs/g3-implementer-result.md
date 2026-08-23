# IMPLEMENTER_RESULT

## Gate
g3-implement (execute.json, work-id w3-promote) — attempt-2

## Return status
complete

## Summary
Found the work already done by a prior attempt in this same worktree (uncommitted). Verified
every promotion fresh against the shipped JSON and the referenced source (`archive_name_for` /
`_stage_and_move` in `scripts/spine_lifecycle.py`, the resolver's placeholder families in
`scripts/init_work_area.py`), confirmed the prior attempt's judgment calls hold up, then ran the
full verification suite. No further edits were needed; this result documents the fresh-verify and
confirms green.

3 of the 4 candidate conditions in `skills/admiral/templates/ADMIRAL_SPINE.template.json` were
promoted from `check: null` to `{"kind": "command", ...}`, matching the handoff's shapes exactly:

1. **`init.c2`** ("engine session lease claimed for this spine") → `command`, mirrors g1's landed
   `COMMANDER_SPINE.template.json` `init.c1` verbatim (same `.agent-work/<work-id>/spine.json`
   seam). `command`-kind is independently justified against THIS template's own pre-existing
   checks: the sibling condition in the SAME task, `init.c1` (line 13), is already `"kind":
   "command"` — not the first use of the kind in this file. (`command` is in fact this template's
   dominant kind before this change: `init.c1`, `execute.p2`, `execute.c3`, `closeout.c2` are all
   `command`; only `latitude.c2`/`closeout.c5` are `artifact`, and both are `user-decision`, a real
   human-confirmation event — never a stand-in for raw file existence.)
2. **`latitude.c1`** ("latitude contract written...") → `command`, existence+nonempty only:
   `test -s "<repo-root>/.agent-work/<work-id>/LATITUDE_CONTRACT.md"`. The judgment half (decision
   classes/float-up/expiry are *good*) stays uncovered — `latitude.c2` already covers human
   confirmation, per the handoff's own scoping.
3. **`execute.c2`** ("ADMIRAL_LOG current through the last wave...") → `command`,
   existence+pattern only: nonempty AND contains a line matching `^- TRANSITION` (the imperative's
   own documented grammar, confirmed by grep against `ADMIRAL_LOG.template.md` /
   `verify_iterative_role_artifacts.py`'s `admiral-prelaunch` audit field). "Current through the
   last wave" (freshness) is explicitly NOT claimed — only the presence of at least one grammar-
   conforming line.

**`closeout.c4` was left `check: null`, on purpose** — the fourth candidate did not clear the
handoff's own bar. Fresh-verified against `scripts/spine_lifecycle.py`:
`archive_name_for(work_id, today) -> f"{today}-{work_id.replace('/', '-')}"`, and `close_work`
moves `ADMIRAL_LOG.md` (an "other top-level entry") under that directory unchanged in name. Two
problems, either one alone sufficient to decline:
- `today` is read at CLOSE time, never at spine-authoring time — there is no fixed literal path a
  check text can pin, and the resolver's placeholder families (`scripts/init_work_area.py`
  `_PLACEHOLDER_RE`: `work-id`, `repo-root`, `*-skill-dir`, `*-session-id`) have no `<today>`
  member, so even instantiation-time substitution cannot supply it.
- the directory name also runs `work_id.replace('/', '-')`, a transform the resolver's own
  `<work-id>` substitution (a blind `str.replace`, confirmed by reading `resolve_spine`) never
  performs — a hand-authored glob keyed on the raw, unslashed work-id would silently mismatch any
  work_id containing `/`, which the resolver's own docstring treats as a legal shape.

No "real, stable path convention" survives fresh-verification; per the handoff's own stated
fallback ("If no stable path convention exists, leave this condition `check: null` and say so
explicitly... do not invent a path"), it stays unpromoted. This is a judgment call, not a stop
condition — the handoff pre-authorized exactly this outcome, so no Commander consult was needed.

The `.agent-work/templates/ADMIRAL_SPINE.template.json` overlay was already byte-identical to the
edited shipped file (re-verified via `diff`, exit 0). A red-proof test class,
`AdmiralSpineW3PromotePromotions` in `tests/test_checklist_engine.py`, sits adjacent to g1's own
`CommanderSpineW3PromotePromotions` class, same pattern: pinned HEAD (`skipTest` on drift), a
shape-match test, a `closeout.c4`-stays-null pin, an exhaustive "no other condition carries a
check" pin, and one adversary-chosen-mutation discrimination test per promoted condition (BAD
lease status value that the lease machinery itself never writes; an empty-but-existing contract
file; a lower-cased `transition` line that fails the documented `^- TRANSITION` grammar) — each
proving `advance()` refuses on the defect and `attest()` refuses outright once `check` is
non-null.

No all-null gate cleared: `init` (`c1` already non-null), `latitude` (`c2` already non-null),
`execute` (`c3` already non-null), and `closeout` (`c2`, `c5` already non-null) each already had a
non-null condition before this gate's edit, so `tests/test_validate_spine.py`'s floor needed no
update — confirmed by its empty diff.

## Evidence

### `git diff -- skills/admiral/templates/ADMIRAL_SPINE.template.json`
```diff
--- a/skills/admiral/templates/ADMIRAL_SPINE.template.json
+++ b/skills/admiral/templates/ADMIRAL_SPINE.template.json
@@ -11,7 +11,7 @@
       "preconditions": [],
       "postconditions": [
         {"id": "c1", "statement": "work area scaffolded and ADMIRAL_LOG created", "check": {"kind": "command", "command": "python <admiral-skill-dir>/scripts/init_work_area.py <work-id> && test -f .agent-work/<work-id>/ADMIRAL_LOG.md"}, "satisfied": false},
-        {"id": "c2", "statement": "engine session lease claimed for this spine", "check": null, "satisfied": false}
+        {"id": "c2", "statement": "engine session lease claimed for this spine", "check": {"kind": "command", "command": "python3 -c \"import json,sys; d=json.load(open('<repo-root>/.agent-work/<work-id>/spine.json', encoding='utf-8')); sys.exit(0 if d.get('engine_session',{}).get('status')=='active' else 1)\""}, "satisfied": false}
       ],
       "constraints": [], "directives": null, "child_checklist": null,
       "status": "pending", "status_detail": {}, "result": null, "finding": null, "evidence": [], "rework_count": 0, "bookend": true
@@ -22,7 +22,7 @@
       "imperative": "Read your inherited global doctrine ...",
       "preconditions": [{"id": "p1", "statement": "work area ready", "check": null, "satisfied": false}],
       "postconditions": [
-        {"id": "c1", "statement": "latitude contract written with decision classes, float-up routing, and expiry", "check": null, "satisfied": false},
+        {"id": "c1", "statement": "latitude contract written with decision classes, float-up routing, and expiry", "check": {"kind": "command", "command": "test -s \"<repo-root>/.agent-work/<work-id>/LATITUDE_CONTRACT.md\""}, "satisfied": false},
         {"id": "c2", "statement": "latitude contract confirmed by the human", "check": {"kind": "artifact", "evidence_type": "user-decision"}, "satisfied": false}
       ],
       "constraints": [], "directives": null, "child_checklist": null,
@@ -38,7 +38,7 @@
       ],
       "postconditions": [
         {"id": "c1", "statement": "every epic issue dispositioned (merged, honest-null closed, deferred with ruling, or escalated)", "check": null, "satisfied": false},
-        {"id": "c2", "statement": "ADMIRAL_LOG current through the last wave: all rulings, incidents, merges, transition exits, and errors logged", "check": null, "satisfied": false},
+        {"id": "c2", "statement": "ADMIRAL_LOG current through the last wave: all rulings, incidents, merges, transition exits, and errors logged", "check": {"kind": "command", "command": "test -s \"<repo-root>/.agent-work/<work-id>/ADMIRAL_LOG.md\" && grep -qE \"^- TRANSITION\" \"<repo-root>/.agent-work/<work-id>/ADMIRAL_LOG.md\""}, "satisfied": false},
         {"id": "c3", "statement": "NEXT_WAVE names a boundary whose exact transition is uniquely audit-recorded, G2-verified, repair-safe, and rendered before launch", "check": {"kind": "command", "command": "python <admiral-skill-dir>/scripts/verify_iterative_role_artifacts.py admiral-prelaunch --work-id <work-id>"}, "satisfied": false}
       ],
       "constraints": [],
```
(`.agent-work/templates/ADMIRAL_SPINE.template.json`'s diff is byte-identical to the above.)

### Wiring grep — before (git show HEAD) vs after
- before: 17 `"check"` occurrences, 10 `"check": null`
- after: 17 `"check"` occurrences, 7 `"check": null` (3 promoted, matches the 3 items above)

### JSON parse-check
```
$ python3 -c "import json; json.load(open('skills/admiral/templates/ADMIRAL_SPINE.template.json',encoding='utf-8')); print('OK')"
OK
```

### `python3 scripts/check_template_overlay_freshness.py`
```
...
  ok                 .agent-work/templates/ADMIRAL_SPINE.template.json -- matches skills/admiral/templates/ADMIRAL_SPINE.template.json
...
all 56 overlay template(s) checked -- none stale
```
(exit 0)

### Overlay byte-match
```
$ diff skills/admiral/templates/ADMIRAL_SPINE.template.json .agent-work/templates/ADMIRAL_SPINE.template.json
(no output — identical)
```

### `git check-ignore` (both exit 1 — tracked, not ignored)
```
$ git check-ignore skills/admiral/templates/ADMIRAL_SPINE.template.json; echo $?
1
$ git check-ignore .agent-work/templates/ADMIRAL_SPINE.template.json; echo $?
1
```

### Full pytest
```
$ python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q
642 passed, 13 skipped, 150 subtests passed in 5.71s
```
No failures. Skips are pre-existing HEAD-pin skip guards elsewhere in the suite (not this gate's
new class — its own `PINNED_HEAD` (`ff8e96402a6a76cc6e7f5c1bd92e91b36c830156`) matches current
`git rev-parse HEAD` exactly, so its own tests ran, not skipped).

### `tests/test_validate_spine.py`
`git diff` is empty — no floor change triggered (confirmed reasoning above).

## Diffs run
- `skills/admiral/templates/ADMIRAL_SPINE.template.json` — 3 conditions promoted (raw-text hand
  edit, no json.load/json.dump round-trip; whitespace/formatting elsewhere in the file is
  untouched, confirmed by the minimal 3-line diff above).
- `.agent-work/templates/ADMIRAL_SPINE.template.json` — overlay sync, byte-identical to the above.
- `tests/test_checklist_engine.py` — new class `AdmiralSpineW3PromotePromotions` appended after
  g1's `CommanderSpineW3PromotePromotions` (no existing test touched).
- `tests/test_validate_spine.py` — untouched (no trigger).
- `skills/commander/templates/COMMANDER_SPINE.template.json` and its overlay — untouched (g1's,
  confirmed by empty diff / git status).
- `checklist_engine.py` — untouched.

## Blockers
None. `closeout.c4` was evaluated and deliberately left `check: null` per the handoff's own
pre-authorized fallback (see Summary) — this is a reported judgment call, not a stop condition;
no Commander consult required per the handoff's own text.

## Note on prior attempt
This is attempt-2. On starting, the worktree already carried this exact promotion (uncommitted,
presumably from attempt-1). Rather than trusting it, every claim was fresh-verified independently
against the shipped JSON and the cited source files before treating it as correct: the 3
promotions' shapes, the `init.c1` sibling-kind justification, the resolver's placeholder-family
membership (no `<today>`), and `archive_name_for`'s exact destination-path formula. All held up
under fresh-verification; no corrections were needed. Nothing was committed — that is the
Commander's call, not this crew's.
