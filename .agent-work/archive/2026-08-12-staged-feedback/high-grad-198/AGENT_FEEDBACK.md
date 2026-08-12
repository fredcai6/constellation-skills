# Agent Feedback Log

Unified, append-only retrospective across Constellation runs in this repo. Newest entries on top.

---

## `2026-07-19` — `high-grad-198`

**Run shape:** `commander-delegated` · full 10-step spine (init→archive) + execute.json child (e0→g1-implement→g1-review→g1-integrate) · subagents: 1 sonnet drill auditor, 1 opus independent reviewer.

**Instruction adherence:** `minor deviations` (all surfaced)
- Followed the delegated spine end-to-end via the engine. Design-it-twice run at proportionate altitude for a frozen-spec transcription: implementer-crew dispatch and a separate cold plan critic were skipped as **named untaken roads** (PLAN_NOTES.md) — the load-bearing independent check is the mandatory fresh reviewer on the output, which the launch order requires and which I did dispatch. The commander self-authored the 5 verbatim edits (sole-writer per file ownership; a handoff round-trip would ADD telephone-game drift on pre-approved text).
- G1's CREW_CONTEXT note (an AND/OR alternative) was deliberately not added — home genuinely ambiguous in a skill-source repo (the charter CREW_CONTEXT.template.md *generates* per-project files; a note there leaks into every consumer). Surfaced as a FLOAT; reviewer concurred the template annotation is the superior home.

**Friction / unclear:**
- Engine `--session-id` is a PER-VERB arg (after the subcommand), not global; my first `start/attest/advance` calls placed it before the verb and were rejected with an argparse "invalid choice" error, not a hint. One retry to correct.
- Hit `engine-attest-preconditions-before-start` firsthand (already exported, LESSONS_AUDIT item 9 / #-tracked): `start understand` REFUSED until p1 was attested; the `current` imperative narrates only postconditions, so the precondition-attest step is invisible until the refusal.
- The engine pretty-printed my compact work-area `execute.json` on `claim` (reflow). Harmless for a work-area child checklist (not a shipped template), but worth noting the claim path rewrites the file.

**Crew-reported friction:**
- Drill auditor (sonnet): clean HONEST-NULL — before-arm went straight to `advance`, never reached for `attest`; captured the engine's ground-truth refusal independently. Reported no handoff gaps.
- Reviewer (opus): no friction; independently reproduced suite + verified both engine mechanisms against `checklist_engine.py` source (attest refusal ~L1565, inline-config precedence L123-127).

**What worked:**
- Dogfooding the G1 remedy: my own `execute.json` carried an inline `config` object (not a `config_ref`) — the exact skill-source pattern the graduation documents. It just worked (engine prefers inline `config`).
- The engine running command-kind postconditions at `advance` (init.c1, g1-implement.c2 json.load, g1-integrate.c1 pytest) is exactly the mechanism G2 documents — I advanced command checks directly and never once reached for `attest`, corroborating the drill's honest-null (capable models handle it; the historical 3x recurrence likely drew on in-template contextual pull).

**Improvement signals:**
- `--session-id` arg-placement legibility (per-verb, after subcommand) → disposition: none new — minor, adjacent to the already-tracked engine CLI-ergonomics cluster (CONSTELLATION_FEEDBACK items 5-7); not re-filing a low-signal single instance.
- The command-postcondition honest-null is itself a data point that the G2 edit is a legibility strengthening rather than an error-preventer → disposition: recorded in the drill record + report; no playbook add (delegated mode does not self-apply doctrine, and this run IS the human-authorized application of the lesson).
