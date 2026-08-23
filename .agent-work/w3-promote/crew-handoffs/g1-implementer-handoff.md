# Implementer Handoff

## Gate
g1-implement (execute.json, work-id w3-promote)

## Task
Promote exactly 8 named `check: null` conditions in
`skills/commander/templates/COMMANDER_SPINE.template.json` to real, mechanically-checked
conditions using only the engine's existing check kinds (`command`, `artifact`,
`git-change-policy`) — per `decision:no-new-check-kinds`. Then red-proof each promotion and sync
the `.agent-work/templates/` overlay.

## Protected Intent
Every promotion must be a check that can genuinely fail — never a decorative artifact an agent can
trivially self-satisfy with a matching-shaped payload. A check that cannot discriminate the healthy
world from the defective one is worse than the honest `check: null` it replaces (this epic's own
thesis). Do not promote anything beyond the 8 named below, even if it looks tempting.

## Test Mode
Test-after allowed (this is data/JSON + pytest test authorship, not application code with a TDD
red/green cycle). Each promotion still needs its own red-proof test (see Required Evidence).

## Close Criteria
- Exactly these 8 conditions in `skills/commander/templates/COMMANDER_SPINE.template.json` change
  from `"check": null` to a real `check` object — no other condition in the file is touched:
  1. `init.c1` ("engine session lease claimed for this spine") → `command`: run a command that
     reads `.agent-work/<work-id>/spine.json`'s own `engine_session.status` field and exits 0 iff
     it equals `"active"`, non-zero otherwise. Use `python3 -c "..."` reading the file at the path
     resolved from the checklist's own `base_dir` convention (mirror how other `command` checks in
     this same file already reference `<repo-root>`/`<work-id>` placeholders — grep the file for
     the exact placeholder tokens already in use, e.g. `archive.c2b`'s command, and match that
     convention exactly rather than inventing a new one).
  2. `plan.c1` ("mission frame produced...") → `artifact`, `evidence_type: "mission-frame"`,
     `match: {"status": ["produced", "skipped-as-trivial"]}`.
  3. `plan.c4` ("plan-alternatives run...") → `artifact`, `evidence_type: "plan-alternatives"`,
     `match: {"converged": true}`.
  4. `plan.c5` ("cold plan critic run...") → `artifact`, `evidence_type: "plan-critic"`,
     `match: {"triaged": true}`.
  5. `plan.c2` ("execute.json authored...") → `artifact`, `evidence_type: "execute-plan"`,
     `match: {"exists": true}` — this is an EXISTENCE-ONLY promotion. Do NOT change the
     condition's `statement` text (it still describes anchors-cut-from-frame and ownership-scope
     coverage, which stay unverified by this check — that's correct, not a bug).
  6. `reconcile.c1` ("map reflects the implemented changes") → `artifact`,
     `evidence_type: "file-diff"`, `match: {"nonempty": true}`.
  7. `archive.c2` ("branch committed and pushed") → `command`: a check that verifies the local
     branch has no unpushed commits (e.g. compare `git rev-parse @` against `git rev-parse @{u}`
     inside a `<repo-root>`-relative invocation matching this file's existing command-check
     convention).
  8. `archive.c3` ("spine_close is authorized...") → `artifact`, `evidence_type: "user-decision"`
     (reuse the exact pattern already used 3x in this same file at `archive.c5`, `review.c1`,
     `triage.c2` — grep them and match the shape exactly, do not invent a new `match` shape).
- The other 11 `check: null` conditions in this file are untouched, byte-for-byte, including their
  `bookend: true` markers on `init` and `archive`.
- `.agent-work/templates/COMMANDER_SPINE.template.json` byte-matches the edited
  `skills/commander/templates/COMMANDER_SPINE.template.json` (copy, not hand-retype); confirmed by
  `python3 scripts/check_template_overlay_freshness.py` reporting no stale files.
- A red-proof test class added to `tests/test_checklist_engine.py` (new class, e.g.
  `CommanderSpineW3PromotePromotions`, modeled directly on the existing `CommanderSpineBasisFields`
  class in the same file — read it first) that: pins `PINNED_HEAD` via `git rev-parse HEAD` captured
  at implementation time; `skipTest` (never fail) if HEAD has since moved; for EACH of the 8
  promoted conditions, asserts (a) the promoted `check` shape exactly matches what you shipped, (b)
  no other condition in the file carries a non-null check outside the pre-existing 5 + these 8, (c)
  attacks each with an ADVERSARY-CHOSEN mutation, not a restatement of the check's own match text —
  e.g. for the `init.c1` command check, mutate `engine_session.status` to a value `claim` never
  legitimately writes (not merely "absent") and assert `advance` refuses (command checks are
  satisfied by `advance`, never `attest` — confirm this in your test); for an `artifact` check,
  attach a wrong-`type` evidence item and assert `attest()` raises `EngineError` with the message
  `"is type {type!r}, not the required {want_type!r}"` (verbatim substring), then attach a
  correctly-typed but non-matching payload and assert the `"does not match required"` message.
  Log each mutation's own one-line rationale as a code comment distinct from the check's own match
  dict (e.g. `# attacks the boundary the match does NOT cover`, not a restatement of it).
- If this gate's edit clears `init` or `reconcile` from `falsifiable-all-null` (both are currently
  single-postcondition all-null gates — promoting `init.c1`/`reconcile.c1` clears them), update
  `tests/test_validate_spine.py`'s `TestCorpusSweepFindings.test_measured_finding_totals` floor
  assertions (`>= 15` for `falsifiable-all-null`, currently measured fresh at 19 — see the comment
  there citing a stale "21", which you should also correct to the fresh number) so the suite stays
  green. Re-run `python3 -m pytest tests/test_validate_spine.py -q` after editing and confirm green.
- Full `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q` green.

## Allowed Scope
- `skills/commander/templates/COMMANDER_SPINE.template.json` (hand-edit as raw text ONLY — never
  `json.load`/`json.dump` it; re-validate with `json.load` afterward as a parse-check, never
  reformat/reflow the file).
- `.agent-work/templates/COMMANDER_SPINE.template.json` (overlay sync — copy the same edit).
- `tests/test_checklist_engine.py` (add the new red-proof test class only — do not modify existing
  test classes, including `CommanderSpineBasisFields`).
- `tests/test_validate_spine.py` (update the floor assertion numbers only, if triggered).

## Specific Exclusions
- Do not touch `plan.c6`'s check text (already amended this run via `spine_amend`, unrelated to
  this gate).
- Do not touch any condition other than the 8 named above, even ones that look promotable (e.g.
  `context.c1`, `execute.c1`, `triage.c1` were deliberately assessed and left `check: null` —
  leave them exactly as-is).
- Do not touch `checklist_engine.py` or any other engine code — this gate reuses existing check
  kinds verbatim.
- Do not touch the `basis` field on `plan.c2`/`c4`/`c5` (already present from a prior wave,
  `decision:no-basis-backfill` keeps it out of this gate's scope — leave those `basis` objects
  exactly as they are, only change the sibling `check` field).

## Constraints
- `decision:no-new-check-kinds` — only `command`, `artifact`, `git-change-policy`.
- `decision:blocking-where-adjudicated` — all 8 ship BLOCKING (not report-only): this wave has the
  Admiral adjudication in hand, and each promotion reuses a check kind already live elsewhere in
  this same file (grep the file for existing `"kind": "artifact"` / `"kind": "command"` uses before
  writing yours, to match style/shape).
- Compact-format JSON: hand-edit raw text, surgically. This is the single most important
  constraint — a `json.load`/`json.dump` round-trip on this file destroys blame across the whole
  file and will be treated as a scope violation regardless of whether the JSON content is correct.

## Map Anchors (inbound)
- **Map entry point:** `docs/CHECK_SCRIPT_CENSUS.md` (which check-kinds/scripts are already live in
  this corpus) and `docs/CHECKLIST_SCHEMA.md`'s "Condition (pre/post)" + "What 'engine-checked'
  means" sections (the exact 3-kind contract). No code-map packet applies (repo map is
  DEGRADED-UNPARSEABLE; these are data-only JSON conditions the map never modeled).
- **Decision anchors:**
  `decision:no-new-check-kinds` — promotion only, no new engine mechanism.
  `@grade: settled/human · leans g1-implement`
  `decision:blocking-where-adjudicated` — ship blocking where adjudication is in hand (this wave
  has it).
  `@grade: settled/human · leans g1-implement`

## Deliverable Path Check
- **Committed** — `skills/commander/templates/COMMANDER_SPINE.template.json`; verify with
  `git check-ignore skills/commander/templates/COMMANDER_SPINE.template.json` exiting 1.
- **Committed** — `.agent-work/templates/COMMANDER_SPINE.template.json`; verify with
  `git check-ignore .agent-work/templates/COMMANDER_SPINE.template.json` exiting 1.
- **Committed** — `tests/test_checklist_engine.py`, `tests/test_validate_spine.py` (if touched).

## Required Evidence
- `git diff -- skills/commander/templates/COMMANDER_SPINE.template.json` showing exactly the 8
  conditions' `check` fields changed, nothing else.
- `python3 -c "import json; json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json',encoding='utf-8')); print('OK')"` — parse-check.
- `python3 scripts/check_template_overlay_freshness.py` — must report no stale files.
- `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q` — full green,
  pasted verbatim, including the new test class's own test names in the output.
- The red-proof test class's own source, quoted in the result, showing each mutation's rationale
  comment.

## Wiring Grep
`grep -n '"check"' skills/commander/templates/COMMANDER_SPINE.template.json` before and after your
edit — paste both, showing exactly 8 lines flip from `null` to a real object.

## Verification Commands
```bash
python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q
python3 scripts/check_template_overlay_freshness.py
python3 -c "import json; json.load(open('skills/commander/templates/COMMANDER_SPINE.template.json',encoding='utf-8')); print('OK')"
```

## Suggested Model Tier
simple bounded — mechanical JSON edits + pytest authorship following an already-proven pattern
(`CommanderSpineBasisFields`) in the same file; the launch order mandates sonnet tier corpus-wide.

## Authority
The 8-condition list, their check kinds, and blocking-vs-report-only are already decided by the
Commander (this handoff) — do not re-litigate which conditions promote. If you find one of the 8
genuinely cannot be shipped as specified (e.g. the exact command-check convention this file already
uses turns out incompatible), stop and return rather than improvising a different shape.

## Stop Conditions
Stop and return if: any of the 8 named promotions cannot be expressed in an existing check kind as
specified; the red-proof reveals the promotion doesn't actually discriminate (i.e., it's decorative
after all); any edit would require touching `checklist_engine.py`.

## Return Format
Return IMPLEMENTER_RESULT per the standard shape (completed slice, files changed, test mode
satisfied, evidence produced, assumptions used, stop conditions hit, out-of-scope observations,
workflow feedback). `Return status` field: `complete | partial | blocked | out-of-scope | failed`,
lowercase. Write to `.agent-work/w3-promote/crew-handoffs/g1-implementer-result.md` before ending
your turn.
