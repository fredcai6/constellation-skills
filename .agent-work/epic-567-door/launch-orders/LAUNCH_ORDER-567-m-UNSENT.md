# Launch Order: `cmdr-567-m` — retire `skills/workbench` entirely (#565's remainder)

Epic **#567**, final cleanup lane **M**. You are the only lane running. You start cold.

## Mission

**Delete `skills/workbench/` and leave nothing broken.** The human's words: *"workbench is dead,
the stub is unnecessary weight."*

Lane D2 already removed the teaching half (289 → 124 lines) in wave 2 and **floated** the rest.
This is that rest.

## What is actually there, measured on `main` at `85ea4598`

```
20L  skills/workbench/SKILL.md
29L  skills/workbench/templates/DEFAULT.template.json
18L  skills/workbench/templates/STATE_NOTE.template.md
43L  skills/workbench/templates/WORKFLOW_CLOSEOUT.template.md
29L  skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md
64L  skills/workbench/references/checklist-engine.md
39L  skills/workbench/references/status-model.md
```

## Who actually depends on each file — measured, live code only

Run over `skills/ scripts/ tests/ specs/ docs/agents/`, excluding `.agent-work/` and `episodes/`
run artifacts, which quote these paths constantly as history and are **not** dependencies:

| file | live referrers |
|---|---|
| `templates/STATE_NOTE.template.md` | `skills/admiral/templates/ADMIRAL_SPINE.template.json`, `skills/commander/templates/COMMANDER_SPINE.template.json` |
| `references/status-model.md` | `skills/reviewer/templates/REVIEW_RESULT.template.md`, `skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`, `skills/implementer/templates/IMPLEMENTER_RESULT.template.md` |
| `references/checklist-engine.md` | `tests/test_shipped_check_commands_resolve.py`, `tests/test_cli_retirement_guard.py`, `tests/test_install_constellation.py`, `tests/test_mcp_adoption.py` |
| `templates/WORKFLOW_CLOSEOUT.template.md` | `tests/data/store_mentions.approved.txt` |
| `templates/CONSTELLATION_FEEDBACK.template.md` | `tests/data/store_mentions.approved.txt` |
| `templates/DEFAULT.template.json` | **zero** |

**Every one of those referrers is a prose path string, not a code lookup** — e.g. the Admiral
spine says *"…from `.agent-work/templates/STATE_NOTE.template.md`, or the bundled
`skills/workbench/templates/STATE_NOTE.template.md`"*. So the work is a move plus a text update,
not a mechanism change. **Verify that claim yourself before relying on it.**

## Why the stub exists at all

`scripts/install_constellation.py:322-324`:

```python
skill_md = source_path / "SKILL.md"
if not skill_md.exists():
    raise InstallError(f"source skill is missing SKILL.md: {source_path}")
```

Every non-underscore directory under `skills/` must carry a parseable `SKILL.md` or the **whole
installer** fails. The 20-line stub is the tax the installer charges for keeping a template
directory in that tree. Its own description already tells agents not to invoke it.

**And `install_constellation.py:320` already skips underscore-prefixed directories** — the comment
there reads *"`_shared` holds bundled refs, not a skill"*. So a destination that needs **no new
installer mechanism** already exists. The Admiral's read is that `skills/_shared/` is the obvious
home; `_shared` currently fans **references** into each skill (`:1983`), so check whether templates
need the same treatment or merely need to exist in the repo. **The destination is yours to
determine — do not take the Admiral's guess as settled.**

## Hard constraints

- **`DEFAULT.template.json` has zero live referrers. Check that properly before deleting it** — a
  zero-reference count is the easiest thing in this repo to get wrong, and the Admiral got a
  reference count wrong twice this session by not excluding run artifacts. If it is genuinely
  dead, delete it and say what you checked.
- **`tests/data/store_mentions.approved.txt` pins text verbatim.** Two of the surviving files are
  named there. A path change that does not update the census trips
  `test_every_approved_entry_exists_verbatim`, which is a retirement guard, not a nuisance.
- **Do not weaken any guard to make the move pass.** In particular `tests/test_cli_retirement_guard.py`
  walks `skills/` — if your move changes what it walks, the walk must still reach the corpus and its
  own floor test (`>= 60` files) must still hold.
- **Prove every role spine still starts.** An Admiral, a Commander and an Explorer spine each
  instantiate and reach their first gate in a fresh process, and `verify_state_note.py <work-id>`
  exits 0. The Admiral spine's `execute` precondition names STATE_NOTE **by path**; a move that
  breaks it breaks every Admiral run at `execute`, which is how this epic's own session would have
  died.
- **Run the installer for real, not only dry-run**, and confirm it exits 0 with workbench gone.
  Note that a real install with `--dest` elsewhere no longer touches the calling repo (#619, fixed
  this epic) — but `git diff` afterwards anyway and say what you saw.
- Do not regenerate or hand-edit `map/INDEX.md` (#544). Your branch is green **except**
  `MapTreeFreshnessTests`.
- File no issue; stage candidates under `.agent-work/567-m/triage-candidates/`.
- Pass `--model sonnet` on any crew you dispatch. Given the size, consider whether you need one.

## Honest-Null Clause

If the move turns out to cost more mechanism than the stub does — for instance if templates
genuinely must be installed per-skill and `_shared` cannot carry them — **say so with the evidence
and stop.** A measured "the stub is the cheaper answer" is a complete deliverable and the human
would rather have it than a forced move.

## Budget

**Sonnet**, commander and any crew. This is a bounded refactor with existing tests as the bar.

## Return Shape

`.agent-work/epic-567-door/results/lane-m-RETURN.md`, committed on your branch. Include: where the
files went and why; every referrer updated, listed; what you checked before deleting
`DEFAULT.template.json`; the installer run output; the three spines starting; the suite tally with
the `^FAILED` grep and the commit sha; touched paths; triage candidates; and your own mistakes.

Then push and tell the Admiral the head sha — it gates on the exact head, not the reported one.
