## Result

**APPROVE**

Independent review of PR #492 (issue #465, epic #418 wave 3), branch `epic-418/w3a-465`, head `6774e75e`. Driven as an engine-tracked survey; full journal at `.agent-work/harvest-418-redux/reviews/w3a-465-review/g1-review/review.json` (+ `.journal`) in this reviewer's own worktree.

## The CRLF guarantee — mutation-tested, both directions

Green on the shipped code alone proves nothing, so I mutated `save()` on this Windows box and re-ran `tests/test_engine_survey_retext_and_newlines.py`:

1. **Reverted `save()` to the old text-mode `write_text`.** `test_save_preserves_lf_line_endings` went **RED**: `save() churned an LF file to CRLF (8 CRLF endings written)`. This is exactly the platform-discriminating fixture the test file's own comment names — on Windows the LF fixture is the one that catches the regression, since the old code already emitted CRLF on this platform. Restored, reran: `4 passed`.
2. **Forced `eol = b"\n"` unconditionally** (the "always write LF" over-correction the CRLF fixture exists to guard against). `test_save_preserves_crlf_line_endings` went **RED**: `save() wrote no CRLF endings at all`. Restored, reran: `4 passed`.

Both mutations reproduced a red the fix goes green on. I also confirmed the test file itself avoids the three forbidden shapes: fixtures are built with `write_bytes` (never `write_text`, which is born CRLF on Windows), assertions read via `read_bytes` (never `read_text`, which normalizes newlines and would go vacuous), and assertions are on CRLF/LF counts, never whole-file byte equality against the fixture (which would fail for the wrong reason since `save()` re-serializes with `indent=2`).

## The affordance, driven end to end via the raw CLI

Not just re-running the shipped pytest — I built a throwaway probe survey from the **raw, unedited template** (`skills/reviewer/templates/REVIEW_SURVEY.template.json`) with the `<fowler-pass-record-path>` placeholder still in `r6-fowler`'s command postcondition, exactly the shape a reviewer meets on the repair path. Claimed a lease, advanced through r0–r5, started r6-fowler, then ran, using only the syntax documented in `docs/CHECKLIST_SCHEMA.md`:

```
amend --delta <file> --reason "record path resolved for e2e probe" --authority "Commander w3a-465" --session-id probe-session
```

with `<file>` containing `{"ops": [{"op": "retext-check", "id": "r6-fowler", "cond": "c1", "which": "postconditions", "command": "..."}]}`.

Result: `amended: retext-check r6-fowler.c1 (authority Commander w3a-465)`. The postcondition's command text was corrected, `satisfied` stayed `false` (retext-check never satisfies), and `amendments[-1]` recorded `{reason, authority, ops: ["retext-check r6-fowler.c1"]}` — the audit trail the safety argument rests on is genuinely written and genuinely readable, confirmed by direct inspection, not by trusting the CLI's own success message. I then confirmed `record --result pass` still correctly **refuses** while the (now-corrected) command genuinely fails, and separately confirmed `add`/`drop`/`rescope` still **refuse** live on a survey with the documented "conservative choice, not a type-level impossibility" wording. No hand-editing of any survey JSON at any point.

The Commander handoff's own wrong `amend --op retext-check` phrasing (no such flag exists — ops live in the `--delta` file) is **not** present in the shipped template or docs; both consistently show the correct `--delta`-file shape.

## Prose corrections

`consolidate()` (line 1949) is unchanged by this diff (confirmed via the diff's own hunk headers — only `save`/`_dominant_newline` and `amend` were touched). `--override-reason` is a real, pre-existing flag (`--override-reason` at parser line 2575, wired at 2714). SKILL.md's corrected sentence now agrees with that: an open fail's two honest exits are BLOCK or APPROVE-with-`--override-reason`, and it still says never downgrade a fail to pass — it does not overstate in the other direction.

## Doc re-grep, reproduced independently

```
grep -rn "gated only|gated checklists only|gated-only" --include=*.md --include=*.py --include=*.json . \
  | grep -v "^./.agent-work" | grep -i amend
```

Returns exactly one hit — `docs/CHECKLIST_SCHEMA.md:280` — and it correctly describes `add`/`drop`/`rescope` as gated-only, not the `amend` verb itself. This matches the crew's own claim, reproduced rather than accepted. Also checked `skills/commander/references/commander-core.md`'s `amend` mention (accurate — Commander only ever drives gated plans) and `docs/CHECKLIST_ENGINE_DESIGN.md` (generic prose, not an applicability claim) — neither is stale.

## Fences

`git diff main...HEAD --stat -- . ':!.agent-work'` shows exactly the six allowed files (`scripts/checklist_engine.py`, `skills/reviewer/SKILL.md`, `skills/reviewer/templates/REVIEW_SURVEY.template.json`, `docs/CHECKLIST_SCHEMA.md`, `skills/workbench/references/checklist-engine.md`, `tests/test_engine_survey_retext_and_newlines.py`). None of the four excluded paths (`tests/test_episode_negative_control.py`, `scripts/hooks/gauge_writer_hook.py`, `tests/test_verify_spec_confirmed.py`, `tests/test_gauge_writer.py`) appear anywhere in the diff.

## Full suite

`FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests` — real exit code **0**: `1786 passed, 2 skipped, 683 subtests passed in 420.56s`.

This is lower than main's `1789 passed / 2 skipped / 683 subtests`, and the delta is explained, not a regression: this worktree's merge-base with main is `c0ad5ecd`, **before** the two wave-3 sibling merges (#461 via PR #490, #488/#489 via PR #491) landed on main. Main = pre-wave-3 base (1782, per `39110aba`'s own log line "main green at 1782 after the harvest") + those two merges' new tests (net +7) = 1789. This branch = the same 1782 base + this PR's own 4 new test nodes = 1786. `1782 + 4 = 1786` and `1782 + 7 = 1789` both check out exactly; the `683 subtests` and `2 skipped` are identical on both sides. No failures anywhere.

## Non-blocking findings (Fowler pass)

Independent Fowler pass at `.agent-work/harvest-418-redux/reviews/w3a-465-review/g1-review/fowler-pass.json`, `verify_fowler_pass.py` exits 0 (re-derived from scratch, not copied from the crew's own all-`absent` record):

- **long-method** (flagged, non-blocking): `amend()`'s new ~18-line survey-type-gate block is self-contained and could be extracted into a small top-level predicate mirroring the function's own existing nested `_floor()` helper pattern, for isolated testability. The block as shipped is short and reads cleanly in place.
- **shotgun-surgery** (flagged, non-blocking): one behavioral decision required prose correction at five doc/template sites. The code change itself stayed localized to two functions in one file; both the crew's and my own re-grep confirm all five sites were actually fixed with no sixth stale site.

## Reviewed by

Independent reviewer, worktree `C:/Programs/wt-rev-465`, isolation verified via `scripts/verify_worktree_isolation.py --here C:/Programs/wt-rev-465` (exit 0). Survey driven through the engine end to end: `claim` → seven checks (`r0`–`r6`) each `start`+`record` → `consolidate --verdict APPROVE` → `release`. State file: `.agent-work/harvest-418-redux/reviews/w3a-465-review/g1-review/review.json`.
