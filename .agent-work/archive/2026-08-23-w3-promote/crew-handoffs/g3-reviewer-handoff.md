# Reviewer Handoff

## Gate
g3-implement (execute.json, work-id w3-promote) — reviewing the implementer's completed slice

## Survey State Location
Create your review survey checklist at `.agent-work/w3-promote/g3-review/review.json`.

## What Was Implemented
3 of 4 candidate `check: null` conditions in `skills/admiral/templates/ADMIRAL_SPINE.template.json`
promoted to real `command`-kind checks (no new engine mechanism): `init.c2`, `latitude.c1`,
`execute.c2`. The fourth candidate, `closeout.c4` ("branches dispositioned, worktrees swept,
ADMIRAL_LOG archived"), was deliberately left `check: null` — the implementer found no stable,
pinnable archive-path convention (the destination directory name is keyed on the wall-clock date
read at close time, not at spine-authoring time, plus a `/`→`-` transform on `work_id` that the
resolver's own `<work-id>` placeholder substitution never performs). Overlay
(`.agent-work/templates/ADMIRAL_SPINE.template.json`) synced byte-identical. A new red-proof test
class `AdmiralSpineW3PromotePromotions` added to `tests/test_checklist_engine.py`, adjacent to g1's
own `CommanderSpineW3PromotePromotions` class. `tests/test_validate_spine.py` was NOT touched — the
implementer's claim is that no all-null gate cleared (each of `init`/`latitude`/`execute`/`closeout`
already had a non-null postcondition before this edit), so no floor update was triggered.

## How to Inspect the Diff
Uncommitted working tree. `git status --porcelain` then `git diff` for each file below
(untracked-safe). Note the worktree also carries UNRELATED uncommitted work from a prior gate
(`g1`'s COMMANDER_SPINE promotion, already reviewed and integrated — do not re-review it; scope
your diff inspection to the ADMIRAL_SPINE-related files named below only).

## Task Statement
Promote the bucket-2 conditions in `skills/admiral/templates/ADMIRAL_SPINE.template.json` per
`notes-1.md`'s ADMIRAL_SPINE section, using only existing engine check kinds
(`decision:no-new-check-kinds`), red-proof each with an adversary-chosen mutation, keep the suite
green at this gate boundary. Full handoff:
`.agent-work/w3-promote/crew-handoffs/g3-implementer-handoff.md`. Full result:
`.agent-work/w3-promote/crew-handoffs/g3-implementer-result.md`.

## Close Criteria
- Exactly 3 conditions changed in `ADMIRAL_SPINE.template.json` (`init.c2`, `latitude.c1`,
  `execute.c2`); `closeout.c4` and every other condition in the file untouched — verify against
  `git diff`.
- Each promoted `check` shape matches what the handoff specified (re-read
  `g3-implementer-handoff.md`'s Close Criteria items 1-4 and diff against the actual JSON):
  `init.c2` mirrors g1's landed `COMMANDER_SPINE.template.json` `init.c1` seam verbatim
  (substituting only the file's own placeholder style if different — confirm it isn't different);
  `latitude.c1` is existence+nonempty only (`test -s ...LATITUDE_CONTRACT.md`); `execute.c2` is
  existence+pattern only (nonempty AND at least one `^- TRANSITION` line) — freshness/"current
  through last wave" must NOT be claimed by the check text or its `statement`.
- `command`-kind eligibility for each promoted condition is justified against THIS SAME template's
  own pre-existing (non-null) checks, not merely cited from COMMANDER_SPINE — spot-check the
  implementer's claim that `init.c1`, `execute.p2`, `execute.c3`, `closeout.c2` were already
  `command`-kind in this file before this change (grep the pre-image via `git show HEAD:skills/admiral/templates/ADMIRAL_SPINE.template.json`).
- `closeout.c4`'s left-null disposition: independently verify the implementer's claim by reading
  `archive_name_for` / the archive-move logic in `scripts/spine_lifecycle.py` yourself — does the
  destination path genuinely depend on a wall-clock value with no placeholder-family member, and
  does `work_id.replace('/', '-')` genuinely diverge from the resolver's own `<work-id>`
  substitution? If either premise doesn't hold, that is a BLOCK-worthy finding (the implementer
  under-promoted a promotable condition).
- Overlay (`.agent-work/templates/ADMIRAL_SPINE.template.json`) byte-matches; confirm yourself with
  `python3 scripts/check_template_overlay_freshness.py`.
- The new red-proof test class: for each of the 3 promoted conditions, does it (a) assert the exact
  shipped shape, (b) assert no other condition in the file changed, (c) attack with a mutation that
  is NOT a restatement of the check's own command text (e.g. `init.c2`'s mutation should use a
  lease-status value the lease machinery itself never legitimately writes, not merely an absent
  key)? Read each discrimination test closely and judge for yourself whether it is genuinely
  adversarial.
- Confirm `tests/test_validate_spine.py`'s empty diff is actually correct: independently re-run the
  corpus-wide `falsifiable-all-null` sweep and confirm ADMIRAL_SPINE's own fault count for the
  `init`/`latitude`/`execute`/`closeout` gates did not drop to zero unexpectedly, or that if it did,
  the floor was in fact updated (do not just trust the implementer's "empty diff" claim — verify the
  underlying reasoning).
- Full suite green AFTER all of the above:
  `python3 -m pytest tests/test_checklist_engine.py tests/test_validate_spine.py -q`.

## Allowed Scope
`skills/admiral/templates/ADMIRAL_SPINE.template.json`,
`.agent-work/templates/ADMIRAL_SPINE.template.json`, `tests/test_checklist_engine.py` (new class
only), `tests/test_validate_spine.py` (floor numbers only, if you find it SHOULD have changed). You
are reviewing, not editing — BLOCK with specific findings if something is wrong, do not fix it
yourself.

## Specific Exclusions
Do not touch or re-review `skills/commander/templates/COMMANDER_SPINE.template.json` or its overlay
(g1's, already integrated on this branch). Do not touch `checklist_engine.py`.

## Constraints the Implementation Must Respect
- `decision:no-new-check-kinds` — only kinds already live in the engine, verify no new kind invented.
- `decision:blocking-where-adjudicated` — all 3 shipped blocking (no report-only); verify this is
  actually justified per-condition against THIS template's own pre-existing checks (not borrowed
  eligibility from a different template).
- Compact-format JSON hand-edit discipline — check the diff doesn't look reflowed/reformatted (a
  `json.dump` round-trip would visibly rewrite unrelated whitespace/key-ordering elsewhere in the
  file; confirm it didn't — the diff should be a handful of single-line changes).

## Map Anchors (inbound)
- **Structural:** `skills/admiral/templates/ADMIRAL_SPINE.template.json`.
- **Decision anchors:** `decision:no-new-check-kinds` `@grade: settled/human`;
  `decision:blocking-where-adjudicated` `@grade: settled/human`;
  `decision:red-proof-each-promotion` `@grade: settled/admiral`.

## Evidence Produced
See `g3-implementer-result.md`'s Evidence section (diff, wiring grep before/after, JSON
parse-check, overlay freshness, full pytest run). Independently reproduce every command rather than
trusting the pasted output.

## Suggested Model Tier
simple bounded — mechanical verification against a well-specified handoff.

## Stop Conditions
Return BLOCK if: any promoted check's shape diverges from spec without a stated, sound reason; the
red-proof for any condition is not genuinely adversarial (restates the match/command text); the
overlay is stale; the full suite is not green; any excluded file was touched; `closeout.c4`'s
left-null reasoning does not hold up under your own independent read of `spine_lifecycle.py`.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback. Write to
`.agent-work/w3-promote/crew-handoffs/g3-reviewer-result.md` before ending your turn.
