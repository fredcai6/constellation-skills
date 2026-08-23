# IMPLEMENTER_RESULT

## Gate
g5-implement (execute.json, work-id w3-promote)

## Return status
complete

## Summary
Promoted 1 of the 3 candidate `check: null` conditions in
`skills/charter/templates/CHARTER.template.json` to a real, mechanically-checked condition using
only the engine's existing `artifact` check kind (`decision:no-new-check-kinds`). The other 2
candidates were fresh-verified against the real shipped JSON and left `check: null` per the
handoff's own stated fallbacks, with the reasoning below.

1. **`project-templates.c1`** ("project-specific templates seeded") → `artifact`,
   `evidence_type: "project-templates"`, enum-match on `status` in `{"seeded", "skipped-no-need"}`.
   Mirrors g1's already-landed `COMMANDER_SPINE.template.json` `plan.c1` shape exactly (`artifact`
   + `status` enum-match): both conditions' tasks offer the same two-way disposition in prose
   ("Seed or update ... where the project needs them ... Skip with reason if none needed" here;
   "produced ... or explicitly skipped as trivial" for `plan.c1`). `artifact` is not a new kind for
   this file — `intent.c1`, `orchestrator-context.c1`, `crew-context.c1`, `glossary.c1`,
   `agent-guide.c1`, `engine-config.c1` are already `artifact`-kind here (all
   `evidence_type: "user-decision"`), so this ships blocking without a first-of-kind consult per
   `decision:blocking-where-adjudicated` — only the `evidence_type` string is new, which that
   decision does not gate. Full (non-split) promotion: `statement` text left byte-identical, no
   `basis` field added (mirrors `plan.c1` itself, which also carries no `basis`).

2. **`closeout.c1`** ("durable outputs complete; work area archived") — left `check: null` in
   full, not split. Unlike `COMMANDER_SPINE`/`ADMIRAL_SPINE`/`EXPLORER_SPINE`, `CHARTER.template.json`
   has no `init` task at all — no task-level scaffolding step establishes a dedicated work area, so
   "the work area" this condition names can only be the generic `.agent-work/<work-id>/` directory
   the engine stood up at spine-instantiation time. The only archive mechanism in this repo for that
   directory is the generic `scripts/spine_lifecycle.py::close_work` / `archive_name_for`, whose
   destination path is `f"{today}-{work_id.replace('/', '-')}"` — keyed on a wall-clock value read
   at close time, with no placeholder-family member (`<work-id>`, `<repo-root>`, `<*-skill-dir>`,
   `<*-session-id>`) able to pin it, plus the same `/`-strip transform `resolve_spine`'s own
   substitution never performs. This is the exact defect g3 already found and declined for
   `ADMIRAL_SPINE`'s `closeout.c4`. No stable archive-path convention exists here either, so per the
   handoff's explicit fallback ("If no stable archive-path convention can be confirmed, leave the
   whole condition check: null and say so"), `closeout.c1` stays fully unpromoted.

3. **`interrogate.c1`** ("doctrine resolved to role-operable decisions") — left `check: null`.
   A real, reusable, already-shipped verifier for `interrogation.json`'s companion terminal-state
   artifact DOES exist (`scripts/verify_interrogation.py`, invoked today by
   `INTERROGATION.template.json`'s own `zc-consolidate.c1` against
   `.agent-work/<work-id>/INTERROGATION_RECORD.json`, a path `tests/test_shipped_check_commands_resolve.py`
   already pins as resolving from `<work-id>` alone). Wiring that same script into CHARTER's own
   spine is not a genuine reuse for two independent reasons:
   - `scripts/init_work_area.py::resolve_spine` resolves EVERY `<ROLE-skill-dir>` token found in a
     template's text to the SAME single `--skill-dir` value passed for that template's own
     instantiation, regardless of what `ROLE` spells (`_resolve_skill_dir_token` is not a per-role
     lookup). Every shipped template today only references its own role's skill-dir token
     (`<commander-skill-dir>` only in `COMMANDER_SPINE`, `<admiral-skill-dir>` only in
     `ADMIRAL_SPINE`, `<reviewer-skill-dir>` only in `REVIEW_SURVEY`) — a `<interrogator-skill-dir>`
     token inside CHARTER's own spine would be the first cross-skill reference of this shape in the
     corpus, and would resolve WRONG in an installed repo: `scripts/install_constellation.py`'s
     per-skill script manifest bundles `verify_interrogation.py` only with `"interrogator"`, never
     with `"charter"` (`("checklist_engine.py",)` only), so the token would substitute CHARTER's
     own installed skill directory (which lacks the script), not interrogator's. It only appears to
     work in this source repo, where an omitted `--skill-dir` falls back to the shared top-level
     `scripts/` directory. A real fix means editing `scripts/install_constellation.py`'s manifest —
     outside this gate's Allowed Scope.
   - Independent of the above: `CHARTER.template.json` carries zero `command`-kind checks today (its
     only 6 pre-existing non-null checks are all `artifact`/`user-decision`) — a `command`-kind
     promotion here would be this template's first use of that kind, which
     `decision:blocking-where-adjudicated` says needs explicit Commander consultation before
     shipping blocking, not implementer say-so.

   Per the handoff's own fallback ("If none exists, leave check: null — do not invent a new
   verifier"), `interrogate.c1` stays `check: null`.

Promoting `project-templates.c1` (its task's ONLY postcondition) cleared 1 all-null gate per
`scripts/validate_spine.py`'s `falsifiable-all-null` fault (postcondition-only; ignores
preconditions) — measured corpus-wide count dropped from 15 (post-g4) to 14.
`tests/test_validate_spine.py`'s floor was updated in the same edit (both message text and the
numeric threshold, since the count genuinely dropped below the prior `>= 15` floor — confirmed by
re-running the corpus sweep pre/post-edit).

The `.agent-work/templates/CHARTER.template.json` overlay was re-synced (byte-copy of the edited
shipped file, never a `json.load`/`json.dump` round-trip) and re-verified with
`scripts/check_template_overlay_freshness.py` — clean. A new red-proof test class,
`CharterW3PromotePromotions` in `tests/test_checklist_engine.py`, sits adjacent to g1's
`CommanderSpineW3PromotePromotions`, g3's `AdmiralSpineW3PromotePromotions`, and g4's
`ExplorerSpineW3PromotePromotions`, same pattern: pinned HEAD
(`442a5826e23f3259bdfd3f92d301188c693b1b5e`, g4's own merged commit — the commit this gate's
uncommitted edit sits on top of), `skipTest` (never fail) on drift, an adversary-chosen mutation
(a differently-cased `status` string, mirroring `plan.c1`'s own test's adversary choice) plus a
positive control on the OTHER enum member (`skipped-no-need`, not `seeded`) to prove genuine
list-membership rather than a hardcoded match, plus dedicated pins for `interrogate.c1`/`closeout.c1`
staying null and for `project-templates.c1` keeping its statement text with no `basis` field.

## Scope
**Files changed:**
- `skills/charter/templates/CHARTER.template.json`
- `.agent-work/templates/CHARTER.template.json`
- `tests/test_checklist_engine.py`
- `tests/test_validate_spine.py`

**Specific exclusions touched:** no — `COMMANDER_SPINE.template.json`, `ADMIRAL_SPINE.template.json`,
`EXPLORER_SPINE.template.json`, their overlays, and `checklist_engine.py` were not touched.

## Behavior changed
Yes — 1 condition in `CHARTER.template.json` gained a real, engine-enforced check (previously
vacuous `check: null`); the engine will now genuinely refuse `project-templates` advance-by-artifact
unless a `project-templates` evidence item with `status` in `{"seeded", "skipped-no-need"}` is
attached.

## Map Impact
- **Structural anchors touched:** none new — reuses `checklist_engine.py`'s existing `artifact`
  check-kind machinery, no code changed.
- **Capabilities added/changed/affected:** `CHARTER.template.json`'s `project-templates` step now
  mechanically requires a typed status attestation instead of trusting an honest-but-unchecked
  attest.
- **Constraints/assumptions touched:** `decision:no-new-check-kinds` (honored — only `artifact`
  used, already live in this template); `decision:blocking-where-adjudicated` (honored — the one
  promotion reuses a kind already live in this file, so no first-use consult was needed;
  `interrogate.c1` WOULD have been a first-of-kind `command` use and was declined rather than
  consulted on, since a second, independent, sufficient reason (the install-manifest gap) already
  ruled it out on its own).
- **Triage candidates:** `interrogate.c1` is a genuine future candidate IF `verify_interrogation.py`
  is ever added to CHARTER's own install manifest (`scripts/install_constellation.py`) — that edit
  is out of scope here but would remove reason (1) above outright, leaving only the first-command-
  kind-use consult as a gate. `closeout.c1` would become promotable if CHARTER ever grows a
  work-area convention independent of the wall-clock archive path (e.g. a stable
  `.agent-work/<work-id>/` existence check that does not depend on archival timing) — worth a future
  issue, not invented here.

## Test mode
**Required:** test-after
**Satisfied:** yes — `CharterW3PromotePromotions` (5 tests) added after the JSON edits, red-proofed
with an adversary-chosen mutation, then the full listed suite run green.

## Evidence

```bash
$ git diff -- skills/charter/templates/CHARTER.template.json
```
```diff
--- a/skills/charter/templates/CHARTER.template.json
+++ b/skills/charter/templates/CHARTER.template.json
@@ -99,7 +99,7 @@
       "title": "Seed project templates",
       "imperative": "Seed or update .agent-work/templates/ with project-specific template versions where the project needs them (e.g. project review criteria). Skip with reason if none needed.",
       "preconditions": [],
-      "postconditions": [{"id": "c1", "statement": "project-specific templates seeded", "check": null, "satisfied": false}],
+      "postconditions": [{"id": "c1", "statement": "project-specific templates seeded", "check": {"kind": "artifact", "evidence_type": "project-templates", "match": {"status": ["seeded", "skipped-no-need"]}}, "satisfied": false}],
       "constraints": [], "directives": null, "child_checklist": null,
       "status": "pending", "status_detail": {}, "result": null, "finding": null, "evidence": [], "rework_count": 0
     },
```

```bash
$ python3 -c "import json; json.load(open('skills/charter/templates/CHARTER.template.json',encoding='utf-8')); print('OK')"
OK
```

```bash
$ python3 scripts/check_template_overlay_freshness.py
...
  ok                 .agent-work/templates/CHARTER.template.json -- matches skills/charter/templates/CHARTER.template.json
...
all 56 overlay template(s) checked -- none stale
```

```bash
$ python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q
........................................................................ [ 10%]
.................................................... [ 18%]
........................................................................ [ 29%]
...(collapsed)...
641 passed, 26 skipped, 148 subtests passed in 5.83s
```

```bash
$ python3 -m pytest tests/test_checklist_engine.py -k Charter -q
.....                                                                   [100%]
5 passed, 559 deselected, 1 subtests passed
```

```bash
$ git check-ignore skills/charter/templates/CHARTER.template.json; echo "exit=$?"
exit=1
$ git check-ignore .agent-work/templates/CHARTER.template.json; echo "exit=$?"
exit=1
```

**Result:** pass

## TDD evidence, if required
N/A (test-after per handoff's Test Mode).

## Docs/contracts touched
None — `docs/CHECK_SCRIPT_CENSUS.md` and `docs/CHECKLIST_SCHEMA.md` describe existing check kinds
this work only reuses; no new mechanism was introduced.

## Assumptions
- The `falsifiable-all-null` fault's postcondition-only scope (same discipline g1/g3/g4 used) means
  `project-templates` clearing is judged solely on its (single) postcondition; it has no
  preconditions at all, so this is unambiguous.
- `evidence_type: "project-templates"` is a fresh string with no prior corpus usage (confirmed by
  grep before authoring it) — `decision:no-new-check-kinds` bars a new check KIND, not a new
  `evidence_type`; this reads as consistent with `plan.c1`'s own `evidence_type: "mission-frame"`
  being fresh relative to the rest of `COMMANDER_SPINE` at the time g1 promoted it.

## Stop conditions hit
None triggering a blocked return. Two of the three named Stop Conditions scenarios were genuinely
encountered and resolved via the handoff's own pre-authorized fallbacks rather than a Commander
round-trip:
- `closeout.c1`'s archive-path convention could not be confirmed → Close Criteria's own explicit
  fallback ("leave the whole condition check: null and say so") applies directly.
- `interrogate.c1`'s reusable verifier exists as a script but cannot be confirmed to be *reliably
  wired* into CHARTER without an out-of-scope install-manifest edit, and would also be a first-of-
  kind `command` use in this file → Close Criteria's own fallback ("leave check: null — do not
  invent a new verifier") applies; the first-of-kind consult is moot once the wiring problem alone
  already rules the promotion out.
Flagging both here in case the Commander reads either differently — in particular, whether
`scripts/install_constellation.py`'s manifest gap for `verify_interrogation.py`/`"charter"` is
itself worth a triage candidate independent of this gate.

## Out-of-scope observations
- `scripts/install_constellation.py`'s per-skill script manifest does not bundle
  `verify_interrogation.py` with `"charter"`, even though CHARTER's own `interrogate` task drives
  `constellation-interrogator` in-context (per its imperative text) and that sub-drive's own
  `zc-consolidate.c1` needs the script to run. This did not block anything in THIS gate (CHARTER's
  own `interrogate.c1` postcondition is a separate concern from whether the child interrogator
  survey it drives can verify itself), but is worth a triage candidate: does an in-context
  `constellation-interrogator` invocation from CHARTER actually have `verify_interrogation.py`
  available in an installed (non-source) repo today?

## Workflow Feedback

- **Handoff gaps:** none of substance — the handoff's fresh-verify-first framing and per-condition
  fallback language made both declines (`closeout.c1`, `interrogate.c1`) straightforward without a
  round trip, same as g3/g4 found for their own declined candidates.
- **Context rediscovered:** had to trace `scripts/init_work_area.py::_resolve_skill_dir_token` and
  `scripts/install_constellation.py`'s per-skill script manifest by hand to confirm the
  `interrogate.c1` verifier-wiring problem is real and not speculative — the handoff's Map Anchors
  named `docs/CHECK_SCRIPT_CENSUS.md`/`docs/CHECKLIST_SCHEMA.md`, neither of which documents the
  cross-skill `<ROLE-skill-dir>` resolution behavior or the install manifest's per-skill script
  lists. Not a blocker, but a future handoff touching cross-skill script reuse could usefully name
  `scripts/init_work_area.py` and `scripts/install_constellation.py`'s `_ENGINE_SCRIPTS`-shaped
  mapping directly.
- **Instructions improvised around:** none.
- **What would have made this easier:** none — this gate closely mirrored g1/g3/g4's already-landed
  pattern and the handoff cited g1's `plan.c1` directly, which made the one real promotion fast to
  verify and land.
