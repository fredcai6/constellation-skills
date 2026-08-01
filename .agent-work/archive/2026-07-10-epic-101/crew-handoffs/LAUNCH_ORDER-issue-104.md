# Launch Order: commander-104 — issue #104 (Cluster C: constellation-curator, measure-then-mend)

Commanders start cold. Paste, don't point.

## Mission
Execute issue #104: build the `constellation-curator` skill (human-only invoker, periodic corpus maintenance) per the spec section pasted in the issue body. Deliverables:
1. `scripts/curate_corpus.py` — the measurement pass. MECHANICAL checks only (decidability-honest, T7): per-skill line/word counts vs soft budgets, description length + pronoun-based person check + presence of a when-to-use clause + exclusion-clause marker presence, invoker-tag presence, duplication-signature clustering (shingle constants justified in code comments), TOC presence for >100-line references. Emits a findings table + `--json` machine output. **Flags never gates: always exit 0** (enforced in code). A skill dir it cannot parse is a findings row, not a crash. NO baseline/drift-diff (deferred to v2 by spec ruling S7).
2. `skills/curator/SKILL.md` — the skill: trigger (human runs it as periodic maintenance; never scheduled/agent-dispatched/code-change-reaction), invariant #1 measure-before-mend (every invocation starts with the script), invariant #2 flags-never-gates, mend rules (mechanical verifiable-by-inspection fixes in place; git diff is the review gate; no engine checklist — fixed linear pass), route rules (design decisions become triage recommendations, never silent curator edits), outputs (CURATOR_REPORT.md + --json record). Portfolio duty documented as OPTIONAL and dormant until the eval harness exists (#106) — no dependency on E.
3. Tests: golden-file test of `curate_corpus.py` over a fixture corpus whose planted flaws DERIVE FROM THE MEASURED REAL FAILURE MODES (T6) — the boilerplate/engine-string/banner duplication shapes that cluster A just eliminated (see Prior-Wave Verdicts; the pre-#108 git history has real examples: use `git show 2696769:skills/<skill>/SKILL.md` to source authentic planted flaws). Flags-never-gates falsified by asserting exit 0 on a maximally-flagged fixture.
4. Install wiring: curator into `install_constellation.py` bundle maps (script bundle for curate_corpus.py per existing per-skill script precedent), `SKILL_INDEX.md` entry, per-skill install tests.
5. Cross-cutting: curator's description gets exclusion clauses for its confusable pair (scout / write-a-skill style siblings per spec rule 1). Invoker-tag convention: curator SKILL.md declares its own tag (human); DO NOT retro-tag the other 15 skills (that's the curator's own first real run, post-epic).
6. **Acceptance (T5, binding):** post-build, run `curate_corpus.py` over the REAL corpus in your worktree. Near-quietness on the duplication detectors is necessary-not-sufficient; paste the findings table in your report. ADDITIONALLY dispatch an independent fresh-context sweep agent (given NEITHER the script NOR the epic's fix list — just "survey skills/ for duplication clusters of doctrine text across SKILL.md files, command-derived") and paste its verdict. Divergence between the two is a finding, not a failure.

## Prior-Wave Verdicts (pasted)
- PR #108 (cluster A, merged): boilerplate/engine-string/banners/scoped-nulls/world-verification/delegate-not-replacement single-sourced into `_shared/global-everyone.md`; unchanged-tree/crew-idle into `_shared/global-orchestrator.md`; sibling-ids in lessons-auditor. Content-pin + no-residual-duplicate tests guard them (tests/test_install_constellation.py). Corpus word counts moved: e.g. commander 2580→2452, corpus total 17097→16649.
- PR #109 (cluster D, merged): root manifest.json deleted; ROADMAP reframed; workbench typo fixed.
- PR #110 (cluster F + commander diet, merged): commander split — `skills/commander/SKILL.md` now a 254-word human entry; `skills/commander/references/commander-core.md` (2237w, TOC'd); NEW skill `skills/commander-delegated/` (385w); crew-dispatch reference extracted; suite at 446 tests; skill roster now 15.
- PR #111 (cluster B diets, merged, main=eacd175 — your base): admiral folded to pointers; docent HTML constraints → `skills/docent/references/self-contained-html.md`; interrogator register-rewritten in place; history framing detemporalized corpus-wide.
Implication for your detectors: the corpus you measure is POST-cleanup — your golden fixtures carry the planted flaws; the real corpus should be near-quiet.

## Pre-Rulings
- Curator is a NEW skill dir `skills/curator/` — its reference/script bundle wiring follows existing per-skill precedent exactly.
- No new `global-*.md` filenames (bundle glob pins composition).
- Soft budgets: encode the spec's heuristics (e.g. <500 lines hard-flag, word targets) as constants with a comment naming them curator review heuristics, never gates.
- Semantic judgments (is this clause a procedure? does register match tag?) are explicitly NOT the script's job — the script may shortlist candidates but never claims those verdicts; SKILL.md assigns them to the human mend pass.
- Superpowers is a competitor: never cite or import its doctrine.
- Source repo is authority; never edit installed copies.
- Do not modify other skills' content (your acceptance sweep only READS them). Exception: none. Findings about other skills are report rows / triage recommendations.

## Honest-Null Clause
If the independent sweep or your own run finds remaining real duplication clusters, that is a FINDING to report (with the table), not a failure — the epic routes it. A detector that finds nothing on fixtures is a broken detector; prove yours bite via the golden tests.

## Inherited Latitude
You decide: script structure, shingle/threshold constants (justified in comments), fixture design (derived from real pre-#108 shapes), report format, test naming. Float to Admiral: any urge to add gates/exit-codes ≠ 0, baseline/drift machinery (rejected S7), agent-dispatched modes (rejected), retro-tagging other skills, touching other skills' content.

## File Ownership
Yours: `skills/curator/**` (new), `scripts/curate_corpus.py` (new — NOTE: check where per-skill scripts actually live; if precedent is `skills/<skill>/scripts/`, follow precedent and say so), `SKILL_INDEX.md` (one entry), `tests/` additions, `install_constellation.py` (curator entries). Fences: no other skill's content; no `_shared/` content; no `docs/ROADMAP.md`. Findings: `.agent-work/issue-104/` INSIDE your worktree; never write main-checkout canonical LESSONS/AGENT_FEEDBACK.

## Workspace
Worktree: `C:\Programs\constellation-wt-104` — branch `constellation/issue-104`, base eacd175, created via `git worktree add ../constellation-wt-104 -b constellation/issue-104`.
First step: `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-104` (forward slashes — backslash args mangle in the Bash tool) — must exit 0; paste output. Server-side merge is the Admiral's; never merge locally.

## Inherited Context
Active lessons binding this mission:
- Dogfooding divergence: drive your engine from THE REPO'S OWN commander templates/scripts, not installed copies. NOTE post-#110: the repo's commander is now entry + `references/commander-core.md` — read the core for full doctrine.
- Plan-scope completeness: one execute.json gate per deliverable class (script, skill, tests, install wiring, acceptance sweep — gate each).
- Under-epic durable writes: stage feedback/lessons worktree-local for harvest.
- Baseline reconcile at understand: verify the spec's assumptions against post-wave-2 code before planning.
- New tracked files are untracked until staged — say so in diff evidence.
- Never round-trip shipped JSON templates through json.load/dump; surgical text edits only.
- Review artifacts under `.agent-work/issue-104/crew-handoffs/<gate>-review/`.
- Any crew you spawn must deliver its full report as its final message before idling.
- Counts command-derived with pasted output.

## Pre-empted Steps
None — full spine. Issue #104's body is the authoritative spec section; cite it.

## Data Locations
All inputs tracked. Pre-cleanup corpus shapes for fixtures: `git show 2696769:<path>` (pre-#108 commit). Epic work area (read-only): `C:\Programs\constellation-skills\.agent-work\epic-101\`.

## Budget
- **Model tier (required):** inherit session model (new-module design judgment). Crew may run one tier down; the independent acceptance sweep agent SHOULD run one tier down and fresh-context.

## Stop Conditions
Stop and return when: the script's mechanical scope can't cover a spec-named check without semantic judgment (report the boundary, don't fake determinism); install wiring forces changes to other skills' bundles; or context gaps. Asking up is always sanctioned.

## Return Shape
Final message = full report: deliverables summary (script checks list, skill interface, fixture provenance), golden-test falsification evidence, real-corpus findings table (pasted), independent-sweep verdict (pasted), suite result (command + tail), PR URL, isolation output, map impact, triage candidates, workflow feedback. Deliver BEFORE going idle. PR body via `gh pr create -F <tempfile>`, never --body heredoc.
