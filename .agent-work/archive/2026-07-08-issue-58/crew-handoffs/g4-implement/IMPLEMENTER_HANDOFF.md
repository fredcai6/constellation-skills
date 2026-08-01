# Implementer Handoff

## Gate
g4 — constellation-explorer SKILL.md + remaining templates (issue-58)

## Task
Author the explorer's doctrine and the four remaining templates. Design contract: `.agent-work/issue-58/DESIGN_SPEC.md` (CONFIRMED, read-only) — governing text is ALL of "Chosen design 1" (every doctrine paragraph). Model SKILL.md idiom on `skills/commander/SKILL.md` (the orchestrator-tier exemplar).

1. **`skills/explorer/SKILL.md`** — frontmatter `name: constellation-explorer` (match sibling frontmatter conventions). Content requirements, all verbatim-greppable where quoted:
   - Role: orchestrator-tier; **upstream only** (human invokes with a raw idea, before any issue exists); requires a reachable human by construction; **no delegated/autonomous mode**. Work id convention `explore-<topic>`.
   - **Headline doctrine, in this order** (spec Headline doctrine 1–3):
     1. Premature convergence is THE failure mode this skill exists to prevent. The agent never initiates convergence; only the human says "converge to spec". Ripeness may be flagged only as a **standalone message containing nothing else**.
     2. Scoped nulls, optimistic persistence: a failed excursion kills *that specific test under those conditions*, never the idea class; every negative verdict states what was and was NOT tested; impossibility requires evidence spanning the class; default next move after a null is another variant.
     3. Hard gate, mechanism not just prose: `verify_spec_confirmed.py` refusal; the `UNCONFIRMED — DO NOT CUT` marker; the honest trust-model statement (engine records a user-decision rather than cryptographically proving one; no delegated mode means fabricating one violates doctrine with no sanctioned path; verifier + downstream refusal are the mechanical backstops).
   - Spine walk-through referencing `templates/EXPLORER_SPINE.template.json` (exists as of g2) and the engine verbs; instantiation via `init_work_area.py --spine`.
   - **Flavors**: Shotgun (deliberately challenging idea count, default ~20, human-set; wild entries sanctioned; culled ideas stay on the board with reasons — a cull is a scoped verdict), Compare (2–5 candidates developed seriously, recommendation-led, hybrids allowed), Refine (harden one direction; consolidation output is spec-shaped). Natural arc shotgun → compare → refine → spec; re-orderable and repeatable; **a refine that kills its candidate drops back to compare or shotgun — the loop working, not failing**.
   - Interrogator seam: load constellation-interrogator for question phases exactly as Commander's understand step does; cycle survey = interrogation survey with flavor framing.
   - **Excursion ramps**: off-ramp = EXCURSION_BRIEF recorded on the board before dispatch; background dispatch; on-ramp = result lands in cycle record + board before consolidation; either side initiates; dispatch through `run_crew.py` (durable registry) with `recover_crews.py` run **before each dispatch and before consolidation**; slow-excursion rule (human decides: wait, or consolidate with the excursion as an open thread — never silently dropped); one-brief-no-double-entry (prototype section fields identical to PROTOTYPE_HANDOFF).
   - **Ideas board as source of truth**: every consolidation updates it; the spec crystallizes from it; a resumed session reads it instead of chat history; mid-exploration shelve files IT as the shaped-design issue, loudly marked unconfirmed.
   - **Spec phase**: per-section approval, delta-based re-confirmation after the first pass; design-it-twice standard on every load-bearing interface, skip only with a stated reason.
   - **Critical review**: cold full adversary (no exploration record, nothing sacred, human filters relitigation noise); panel scaled by weight (default one critic; epic-spawning/architecture-touching specs get the 3-lens panel: intent-fit / testability / simplicity-YAGNI); **when in doubt, panel**; findings land in the spec's structured table; human triages every finding (EDIT / RE-EXPLORE / REJECT); confirm opens only when every Disposition cell is filled; critic-driven return to exploration = engine `reopen` of explore, with the documented cascade cost (spec/review/confirm reset, evidence superseded but retained; survivable because the board is the source of truth).
   - **Route**: human routes the confirmed spec — hand to to-issues/a Commander, file one shaped-design issue holding the full body, or shelve unconfirmed with the marker header. **Explorer never cuts issues itself.** Archive work area; release lease.
2. **`skills/explorer/templates/EXPLORER_STARTING_QUESTIONS.template.md`** — first-cycle seed questions: the itch; for whom; what does done feel like; what already exists; what would make this pointless. Note that later cycles seed from the board's open threads instead.
3. **`skills/explorer/templates/IDEAS_BOARD.template.md`** — sections: the point; current candidates; verdicts (with scope of what was tested); open threads; rejected ideas with reasons; cycle log.
4. **`skills/explorer/templates/EXCURSION_BRIEF.template.md`** — the single dispatch template for all three excursion types: the one named question; type (research | prototype | design-it-twice); what "answered" looks like; budget/stop conditions. **Prototype section: copy the six field headings from the real `skills/prototyper/templates/PROTOTYPE_HANDOFF.template.md` (exists as of g3) — Question / Branch / Host-project conventions / Location / Stop conditions / Return format. The six top-level headings are the frozen contract; sub-bullets may be adapted.** Design-it-twice section: 3+ parallel agents, distinct constraints (minimal-interface / max-flexibility / common-caller-first / ports-and-adapters), compared on depth, locality, seam placement, testability; opinionated recommendation or hybrid. Research section: primary sources, cited findings.
5. **`skills/explorer/templates/CRITIC_HANDOFF.template.md`** — cold-read contract: critic receives the spec ONLY (no exploration record); assigned lens (or full-adversary single-critic mode); nothing sacred, may attack deliberate decisions; return format = findings rows matching the fixed table columns `| ID | Lens | Severity | Finding | Disposition | Reason |` with Disposition/Reason left EMPTY (human fills them at triage — the critic never self-triages).

### Carry-forward fix (small, authorized scope addition)
6. **`skills/explorer/templates/CYCLE.template.json`** (g2 file, edit authorized by Commander per reviewer carry-forward tc2): it currently carries `"config_ref": "docs/agents/engine-config.json"`, which can hard-fail the engine in a repo without that file — the spine went inline-config for exactly this reason. Switch it to the same inline `config` approach (or drop the key if surveys don't need one — check how the engine loads survey checklists and what `.agent-work/issue-58/interrogation.json` does). Then extend `tests/test_explorer_templates.py` (additive only) with one runtime check: an instantiated cycle survey can be loaded/driven by the engine in a directory with no engine-config file.

## Protected Intent
This SKILL.md is where the epic's founding values become operative doctrine: don't rush to conclusions (convergence is human-only — say this explicitly; it is literally the point of this skill), scoped nulls with optimistic persistence, and the mechanical hard gate. The marker discipline matters: `UNCONFIRMED — DO NOT CUT` as a **standalone line** is what the verifier enforces — any SKILL.md/template mention of the marker must be inline in prose so it never trips a false refusal, and the shelve-route instruction must tell the agent to place it as a standalone header line so it IS enforceable (g2 reviewer carry-forward).

## Test Mode
Additive tests only for item 6. Doctrine grep/invariant tests are g5's. Your verification = integrate command below + full-suite distribution report.

## Close Criteria
- All five explorer files (items 1–5) exist with the content requirements; item 6 edit done with its runtime test.
- Headline doctrine present in order 1-2-3 with the key phrases greppable: "never initiates convergence", "standalone message", "NOT tested", "UNCONFIRMED — DO NOT CUT" (inline prose only), "no delegated", scoped-nulls passage genuine.
- EXCURSION_BRIEF prototype-section headings byte-match the six PROTOTYPE_HANDOFF top-level headings (compare against the real file).
- CRITIC_HANDOFF return format matches the fixed table columns exactly; Disposition/Reason documented as human-only.
- **Full-suite inflection**: with `skills/explorer/SKILL.md` present, installer discovery no longer aborts — waived class 1 clears and class 2 UNMASKS. Expected: the ONLY remaining failures are expected-skills-list assertions in `tests/test_install_constellation.py` (both new skills discovered but not yet in the expected list — g5). The 5 `test_feedback_tooling.py` failures should CLEAR. Report the distribution by root cause (grep '^FAILED' | sed 's/::.*//' | sort | uniq -c). Any failure outside the expected-skills class = stop condition.
- `python -m pytest tests/test_explorer_templates.py -q` green (including your new runtime check).
- Commit on `constellation/issue-58`.

## Allowed Scope
- NEW: `skills/explorer/SKILL.md`, `skills/explorer/templates/EXPLORER_STARTING_QUESTIONS.template.md`, `skills/explorer/templates/IDEAS_BOARD.template.md`, `skills/explorer/templates/EXCURSION_BRIEF.template.md`, `skills/explorer/templates/CRITIC_HANDOFF.template.md`
- EDIT (carry-forward tc2 only): `skills/explorer/templates/CYCLE.template.json` (config_ref → inline/removed), `tests/test_explorer_templates.py` (additive runtime check only)

## Specific Exclusions
- Do NOT touch: `scripts/**`, `skills/explorer/templates/EXPLORER_SPINE.template.json` and `DESIGN_SPEC.template.md` (g2, frozen), `skills/prototyper/**` (g3, frozen — READ PROTOTYPE_HANDOFF for alignment, never edit it), `skills/_shared/**`, `skills/commander/**` (the Commander understand-step line is g5's), `tests/test_install_constellation.py` (g5), `.agent-work/issue-58/DESIGN_SPEC.md`.

## Constraints
- Register/length consistent with skills/commander/SKILL.md (orchestrator exemplar); doctrine concise and imperative, not essayistic.
- Contractual strings: marker text, flavor names, excursion type names, table columns, the six HANDOFF headings, disposition vocabulary (EDIT / RE-EXPLORE / REJECT).
- Marker discipline per Protected Intent (standalone = enforced; inline = mention).
- Fail visibly; no silent fallback (applies to the CYCLE config fix — a missing config file must not crash NOR be silently mis-defaulted; match how the engine/spine handle it).

## Map Anchors (inbound)
- **Structural:** skills/explorer/SKILL.md (NEW) + 4 NEW templates; EDIT CYCLE.template.json + test_explorer_templates.py; reads skills/prototyper/templates/PROTOTYPE_HANDOFF.template.md (frozen contract), skills/commander/SKILL.md (exemplar)
- **Capability:** explorer doctrine complete; excursion dispatch contract; critic cold-read contract; cycle survey runtime robustness
- **Constraints/assumptions:** six-heading freeze (g3 reviewer: top-level headings only, not sub-bullets); marker standalone-vs-inline discipline (g2 reviewer); spec F1–F10 dispositions
- **Decision anchors:** DESIGN_SPEC "Chosen design 1" every paragraph — surface conflicts, don't improvise
- **Evidence expectations:** targeted explorer-templates suite green; full-suite inflection to expected-skills-only failures (feeds g4-integrate.c1, human waiver still in force through g5)

## Deliverable Path Check
- **Committed** — all paths; verify none gitignored.

## Required Evidence
- Pasted targeted + full-suite outputs with per-file failure distribution and root-cause attribution (expect the inflection described above).
- Pasted diff of the six EXCURSION_BRIEF prototype-section headings next to PROTOTYPE_HANDOFF's (byte-match proof).
- Grep outputs for the doctrine key phrases.

## Verification Commands

```bash
python -m pytest tests/test_explorer_templates.py -q
python -m pytest tests/ -q
grep -n "UNCONFIRMED" skills/explorer/SKILL.md skills/explorer/templates/*.md
```

## Suggested Model Tier
stronger — the SKILL.md is the epic's doctrinal core with many contractual phrases, plus a cross-file alignment contract and a runtime-behavior edit.

## Authority
Design fixed by DESIGN_SPEC.md. You may choose prose wording, ordering within sections, and template formatting. You may NOT change contractual strings (Constraints), the doctrine order 1-2-3, the six-heading contract, or anything frozen in g2/g3. The CYCLE config fix is pre-authorized as scoped in item 6; anything beyond it in that file is not. Surface conflicts instead.

## Stop Conditions
Stop and return if: any full-suite failure falls outside the expected-skills-list class after SKILL.md lands; the engine cannot drive a config-less cycle survey without a script change (scripts are frozen — surface it); PROTOTYPE_HANDOFF's headings don't match what this handoff enumerates; an exclusion must be touched; or a decision outside authority is needed.

## Return Format
Return IMPLEMENTER_RESULT at `.agent-work/issue-58/crew-handoffs/g4-implement/IMPLEMENTER_RESULT.md`: completed slice, files changed, evidence produced (pasted, incl. distribution + inflection confirmation + heading byte-match), assumptions, stop conditions hit, out-of-scope observations, workflow feedback (run-specific; bare `none` = unfilled).
