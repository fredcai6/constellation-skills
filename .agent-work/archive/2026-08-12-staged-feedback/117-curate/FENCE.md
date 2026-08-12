# Fence citation — 117-curate

Staging the feedback trio here (`.agent-work/staged-feedback/117-curate/`) instead of writing directly to
the durable main-checkout `.agent-work/AGENT_FEEDBACK.md` / `LESSONS.md` / `CONSTELLATION_FEEDBACK.md`,
per:

- **Launch order** `C:/Programs/constellation-skills/.agent-work/epic-198-burndown/launch-orders/W3-117-curate.md`,
  Inherited Context, "KNOWN FRICTION (agent_work_root staleness)": "the installed bundle's
  `agent_work_root.py` is stale vs main (missing #118's fix), so your feedback/archive gates may resolve
  `durable_root` to the main checkout. Workaround: pass `--root .`, or write the trio to the worktree-root
  `.agent-work/` and force-waive with independently-verified reasoning if the gate resists — a known
  Admiral-acknowledged lag, not your bug."
- **This skill's own bundled doctrine** (`constellation-commander-delegated` "Start here" section, read at
  skill-load for this run): "Fenced feedback/archive closeout — stage, do not waive... instead stage the
  worktree-local trio... plus a FENCE.md citing this launch order, all under
  `.agent-work/staged-feedback/<work-id>/`, which `verify_agent_feedback.py` now accepts in lieu of the
  durable-root write (the Admiral harvests that trio into the shared root before sweeping your worktree)."

**Why staging over the launch order's own "write worktree-root + force-waive" wording:** the installed
`verify_agent_feedback.py` in this environment (`C:/Users/fredc/.claude/skills/constellation-commander/
scripts/verify_agent_feedback.py`) already carries the staged-trio acceptance path (`_staged_feedback_errors`,
checked directly by this Commander before writing this file) — so the more current, more specific skill
doctrine's "stage, don't waive" instruction is followable exactly, not just approximately, and is preferred
over a force-waive.

**Additional reason specific to this run, beyond the installer staleness:** this run executed inside a
multi-agent wave (team session `session-2e0868f6`) with ~11 other concurrently-active `commander-*` agents
in the same session, each independently reaching their own `feedback` step around the same time. Writing
directly to the shared main-checkout `AGENT_FEEDBACK.md`/`LESSONS.md` (plain read-modify-write text files,
no locking in `apply_lessons_delta.py`/manual append) risks a lost-update race across concurrent writers.
Staging avoids this entirely — the Admiral serializes the harvest of all wave commanders' staged trios at
closeout.

**Staged trio in this directory:**
- `AGENT_FEEDBACK.md` — one dated entry for `117-curate`.
- `lessons-delta.json` — one `add` op (`command-postcondition-cannot-attest`, scope `constellation`) +
  `tick=true`; validated with `--dry-run` against a scratch playbook before staging (see run transcript).
- `CONSTELLATION_FEEDBACK.md` — present, no entries (nothing export-ripe this run).
