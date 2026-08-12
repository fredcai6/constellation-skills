Follow-up to #420 (epic #418, workstream B). `state()`/`render_human()` in `scripts/checklist_engine.py` render `anchors` and `constraints` when populated on a gate (landed in #420), but `directives` is in the same unrendered-defect class: `state()` never reads it either, so a populated `directives` field never reaches `current`'s output, same silent-drop shape #420 fixed for the other two fields.

`directives` is documented in `docs/CHECKLIST_SCHEMA.md`'s Task table as `"forced primitive specifics handed down"` — real, structured content, not a bookkeeping field.

Out of #420's authorized scope (that issue's launch order capped the fix to "the two new fields": anchors + constraints) — flagged by both the implementer and the reviewer during that run's own verification (`tests/test_checklist_engine.py`'s `TaskFieldCompleteness._EXCLUDED_FIELDS` names it explicitly with this same reasoning).

**Suggested shape, same as #420:** confirm `directives` is genuinely populated somewhere in the live corpus (inventory before building, per #420's own vestigial-fields precedent — don't assume), then render it in `render_human()` when present, and extend `TaskFieldCompleteness` to cover it instead of excluding it.

<!-- constellation-key: epic:418:b-420-followup -->
