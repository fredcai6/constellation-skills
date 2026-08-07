# Triage Recommendations — issue-58 (explorer + prototyper epic)

Seven candidates from `execute.json` triage_candidates, gate reviews, and run friction. Dispositions below are PROPOSED; issues are filed only on explicit human approval (spine triage.c2).

---

## T1. CYCLE.template.json dangling config_ref

- **Classification:** bug (template)
- **Source:** tc2 (g2 reviewer out-of-scope observation)
- **Problem:** shipped cycle template referenced `docs/agents/engine-config.json`, absent in fresh repos.
- **Current truth:** RESOLVED — g4 dropped the key after verifying `load_config` degrades to `{}` and surveys never consult rework_cap; a config-less runtime test now guards it (tests/test_explorer_templates.py).
- **Disposition:** **fixed-now** — commit `9b89e53` (verified by g4 reviewer against engine source). No issue needed.

## T2. Gate sequencing for skill-creation epics: minimal SKILL.md first

- **Classification:** missing doc (Commander planning doctrine)
- **Source:** tc1(a); g2 implementer out-of-scope observation, endorsed by g2 reviewer
- **Problem:** creating `skills/<name>/templates/` before `SKILL.md` exists makes installer discovery abort, turning the full suite red for multiple gates (issue-58 carried a human waiver across g2–g4 for this).
- **Suggested scope:** one planning-guidance line in Commander doctrine (or the gate-plan template): when a plan creates a new skill directory, the first gate touching it ships at least a minimal frontmatter SKILL.md.
- **Acceptance:** a future skill-creation plan keeps `pytest tests/ -q` green at every gate boundary.
- **Priority:** medium — cost was a waiver + diagnostic detours, not corruption.
- **Disposition (proposed):** **filed**

## T3. Scope suite waivers by root cause, not file name

- **Classification:** missing doc (handoff doctrine)
- **Source:** tc1(b); g2 reviewer workflow feedback (BL-1 was triggered by a file-name-pinned waiver wording while the root cause was correctly understood)
- **Problem:** a Close Criterion pinned an expected transient to one test file; the same root cause surfaced in a second file (installer-in-setUp), converting a benign transient into a BLOCK round-trip.
- **Suggested scope:** handoff-template guidance: describe expected-failure waivers by root cause with the file distribution shown, and require implementers to derive distribution claims mechanically (`grep '^FAILED' | sort | uniq -c`).
- **Priority:** medium.
- **Disposition (proposed):** **filed** (could be merged with T2 into one "gate-plan hygiene lessons from issue-58" issue)

## T4. run_crew.py `cli` backend drift: claude CLI rejects `--session`

- **Classification:** tooling bug
- **Source:** run friction (g1: `error: unknown option '--session'`); worked around all run via `--backend external` + Agent-tool dispatch
- **Problem:** the `cli` backend's launcher invocation no longer matches the current claude CLI's flags, so spawn-mode crews fail at launch.
- **Suggested scope:** update the launcher invocation (or auto-detect flag support), add a smoke test or a graceful capability check that reports the drift instead of a raw getopt error.
- **Priority:** medium-high — the default backend is silently broken on current CLI versions; external backend masks it.
- **Disposition (proposed):** **filed**

## T5. Admiral pre-ruling seam for shaped-design intake

- **Classification:** unresolved decision / feature
- **Source:** design exploration (deferred during spec; user: "no admiral line, this might go to a commander instead or be saved for later")
- **Problem:** the explorer routes confirmed specs to to-issues/Commander; whether an Admiral can pre-rule shaped-design intake (accept/decline classes of specs under a latitude contract) was deliberately left unresolved.
- **Suggested scope:** design question only — explore when Admiral-tier intake rules should exist and what they'd add over the Commander line shipped in g5.
- **Priority:** low — no current consumer.
- **Disposition (proposed):** **filed** (as a design-question issue) — or drop if you'd rather leave it in the spec's out-of-scope record.

## T6. Standardize critical spec review beyond explorer (Charter doctrine)

- **Classification:** feature (doctrine)
- **Source:** user during shaping ("I really appreciate a critical review of specs when we get to it, we should make that standard")
- **Problem:** cold critical review is now mechanical inside explorer, but "specs get a cold critical review" as a general standard (e.g. Commander plan-time specs, Charter compilations) lives nowhere.
- **Suggested scope:** Charter-level doctrine line + where the panel-scaling rule generalizes; possibly reuse explorer's CRITIC_HANDOFF as the shared template.
- **Priority:** medium.
- **Disposition (proposed):** **filed**

## T7. Explorer dogfood drill (post-merge)

- **Classification:** missing test (end-to-end doctrine exercise)
- **Source:** DESIGN_SPEC Testing pathway 5 (explicitly post-merge, not this run's gate)
- **Problem:** human-only convergence and downstream refusal are doctrine + verifier backstops; their end-to-end behavior is exercised only by a real run.
- **Suggested scope:** first real `constellation-explorer` run on a genuine idea; record friction to AGENT_FEEDBACK per normal lesson flow; confirm the hard gate and Commander intake line behave downstream.
- **Priority:** high — it's the epic's stated follow-through.
- **Disposition (proposed):** **filed**

---

**FINAL dispositions (human-approved 2026-07-08: "for all but t5 just go ahead and knock em out"):**
- T1 — fixed-now, commit `9b89e53` (no issue)
- T2 — filed: #89
- T3 — filed: #90
- T4 — filed: #91
- T5 — recommend-and-defer: user chose not to file this run; recorded here and in the spec's exploration record for a future pass
- T6 — filed: #92
- T7 — filed: #93
