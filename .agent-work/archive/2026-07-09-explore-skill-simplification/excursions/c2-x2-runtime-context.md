# c2-x2 — Runtime context after install: would moving doctrine into `skills/_shared/` change what a role sees?

## Summary
- The installer already bundles `skills/_shared/` files into each skill's `references/` at install, tier-gated by an explicit map (`SKILL_REFERENCE_BUNDLES`, install_constellation.py:98-113). This is the same copy mechanism used for scripts.
- Every skill receives `global-everyone.md` + `windows.md`; orchestrator-tier also gets `global-orchestrator.md` (+ `design-it-twice-brief.md`); crew-tier also gets `global-crew.md`; charter/workbench get all buckets.
- So dedup is viable TODAY with zero new plumbing: move inline doctrine text into the matching `_shared` bucket file. Every skill that carries it inline still receives the file — **provided you pick the bucket that reaches all current carriers.**
- Two doctrines are cross-tier (scoped-nulls: explorer=orch + prototyper=crew; world-verification: reviewer=crew + commander=orch). For these, only `global-everyone.md` reaches both — a tier bucket would make one carrier LOSE it. Everything else fits a single tier bucket cleanly.
- Root `manifest.json` is dead: no installer/test/CI code reads it. Stale (missing explorer/prototyper/docent).
- Tests pin bundle *composition* and one content string, but do NOT pin the inline doctrine strings — dedup by moving text into an existing bucket file breaks nothing. Adding a NEW `global-*.md` file WOULD break exact-set assertions (see Test pinning).

## Installer mechanics (cited)
- Entry point `scripts/install_constellation.py`; `install_skills()` (:330-380) copies each skill's source dir to the target (`shutil.copytree`, :368), rewrites path tokens (:369), then copies bundled scripts (:370-373) and bundled references (:374-377) into `<target>/scripts/` and `<target>/references/`.
- Reference source root is `skills/_shared/` (`SHARED_REFERENCE_ROOT`, :17). Each reference is copied per-skill: `references_target = target / "references" / reference` (:375-377).
- Which references a skill gets is `SKILL_REFERENCE_BUNDLES` (:98-113), built from four tier constants (:94-97):
  - `_GLOBAL_EVERYONE = (global-everyone.md, windows.md)`
  - `_GLOBAL_ORCHESTRATOR = (global-everyone.md, global-orchestrator.md, design-it-twice-brief.md, windows.md)`
  - `_GLOBAL_CREW = (global-everyone.md, global-crew.md, windows.md)`
  - `_GLOBAL_ALL_TIERS = (global-everyone.md, global-orchestrator.md, global-crew.md, windows.md)`
- `_shared` is excluded from being installed as its own skill (`discover_skills`, :152: dirs starting `_` are skipped).
- Confirmed against installed copies: `constellation-explorer/references/` holds design-it-twice-brief.md, global-everyone.md, global-orchestrator.md, windows.md → exactly the **orchestrator** bundle (explorer is mapped ORCHESTRATOR, :111). `constellation-commander/references/` = same 4 (orchestrator). `constellation-reviewer/references/` = global-crew.md, global-everyone.md, windows.md → **crew** bundle. All consistent with the map.
- `references/` is a live copy; a role reads it at its checklist context-read step (per the comment at :89-93 and the installed-file content tests).

## manifest.json verdict
**Dead / stale documentation. No code reads root `manifest.json`.**
- The only `manifest_path.exists()` in the installer (:424) refers to `.agent-work/templates/TEMPLATES_MANIFEST.json`, an unrelated per-project template-baseline manifest — not repo-root `manifest.json`.
- Grepping the four .py files that mention "manifest.json" (install, check_skill_freshness, and two tests) shows every hit is the templates manifest; none construct or open `REPO_ROOT / "manifest.json"`.
- Root `manifest.json` lists 11 of 14 skills — missing `explorer`, `prototyper`, `docent`. Since nothing consumes it, this staleness has no runtime effect; it is purely a doc artifact (safe to fix or delete, out of scope here).

## Per-skill bundle table
Source of truth: `SKILL_REFERENCE_BUNDLES` (:98-113). Every row also gets `global-everyone.md` + `windows.md`.

| Skill | Tier bucket | global-everyone | global-orchestrator | global-crew | design-it-twice-brief | windows |
|---|---|:-:|:-:|:-:|:-:|:-:|
| admiral | ORCHESTRATOR | ✓ | ✓ | – | ✓ | ✓ |
| commander | ORCHESTRATOR | ✓ | ✓ | – | ✓ | ✓ |
| cartographer | ORCHESTRATOR | ✓ | ✓ | – | ✓ | ✓ |
| docent | ORCHESTRATOR | ✓ | ✓ | – | ✓ | ✓ |
| scout | ORCHESTRATOR | ✓ | ✓ | – | ✓ | ✓ |
| triage | ORCHESTRATOR | ✓ | ✓ | – | ✓ | ✓ |
| explorer | ORCHESTRATOR | ✓ | ✓ | – | ✓ | ✓ |
| implementer | CREW | ✓ | – | ✓ | – | ✓ |
| reviewer | CREW | ✓ | – | ✓ | – | ✓ |
| prototyper | CREW | ✓ | – | ✓ | – | ✓ |
| lessons-auditor | EVERYONE | ✓ | – | – | – | ✓ |
| interrogator | EVERYONE | ✓ | – | – | – | ✓ |
| charter | ALL_TIERS | ✓ | ✓ | ✓ | – | ✓ |
| workbench | ALL_TIERS | ✓ | ✓ | ✓ | – | ✓ |

Note: charter/workbench get `global-orchestrator.md` + `global-crew.md` but NOT `design-it-twice-brief.md` (that ships only in `_GLOBAL_ORCHESTRATOR`).

## Per-doctrine dedup go/no-go
Rule: a doctrine can move to bucket B iff **every skill currently carrying it inline receives B** at install. The only bucket every skill receives is `global-everyone.md`. Tier buckets reach only their tier. No skill loses access as long as the correct bucket is chosen — so the real question per doctrine is "which bucket," and cross-tier doctrines force `global-everyone`.

| Doctrine | Inline carriers (verified) | Tiers spanned | Correct bucket | Verdict |
|---|---|---|---|---|
| mandatory-compliance boilerplate | 12 skills (all except triage/docent in my grep; effectively universal) | all | **global-everyone.md** | GO |
| engine-invocation string (`checklist_engine.py`) | charter, workbench, explorer, implementer, reviewer, interrogator, lessons-auditor (+ admiral, commander, cartographer run the engine) — spans everyone/orch/crew | all | **global-everyone.md** | GO |
| scoped-nulls | explorer (ORCH), prototyper (CREW) | orch + crew | **global-everyone.md** only | GO via everyone; **NO-GO** into any tier bucket (a tier bucket drops one carrier) |
| unchanged-tree shortcut | commander, admiral (both ORCH) — verified distinct from the unrelated "…is unchanged" phrasing in interrogator/explorer | orch only | **global-orchestrator.md** | GO |
| crew-idle adjudication | commander, admiral (+ fleet-doctrine content), all ORCH | orch only | **global-orchestrator.md** | GO |
| delegate-not-replacement | commander, admiral (both ORCH) | orch only | **global-orchestrator.md** | GO (use global-everyone instead if you want it tier-wide per the [[delegate-not-replacement]] principle that it applies at every tier) |
| world-verification | reviewer (CREW), commander (ORCH) | crew + orch | **global-everyone.md** only | GO via everyone; **NO-GO** into crew-only or orchestrator-only |

No skill would LOSE a doctrine it currently has, given correct bucket choice. The only traps: putting scoped-nulls or world-verification into a *tier* bucket (drops the cross-tier carrier), and — see below — introducing a new `global-*.md` filename.

Caveat on carrier verification: my grep for boilerplate used approximate patterns; the *tier span* of each doctrine is what determines the bucket, and that is robust (any universal doctrine → everyone; any orch-only pair → orchestrator; any orch+crew pair → everyone). Exact per-file carrier lists should be re-confirmed against final wording before each move.

## Handoff template diff
`skills/commander/templates/IMPLEMENTER_HANDOFF.template.md` (73 lines) vs `REVIEWER_HANDOFF.template.md` (61 lines): **mostly genuinely different, not shared boilerplate.** The full `diff` rewrites nearly every content line. Shared skeleton is only the *section-heading scaffold* and the "Mission Frame Bindings" context block (same structure, but the bind descriptions are reworded per role: implementer "must not silently violate" vs reviewer "verify it was not violated"). Everything substantive diverges by perspective: implementer has Task / Protected Intent / Test Mode / Deliverable Path Check / Verification Commands / Authority; reviewer has Survey State Location / How to Inspect the Diff / Task Statement / Evidence Produced and BLOCK-verdict framing. **Low dedup payoff** — factoring a shared base would leave little common text and would fight the role-specific wording that is the point. Recommend leaving these two as separate templates.

## Test pinning
- No test pins the *inline* doctrine strings inside SKILL.md bodies. So moving doctrine text out of a SKILL.md into an existing `_shared` bucket file breaks **no** test.
- Tests DO pin bundle **composition** by exact set, using a `global-*.md` glob (`test_install_constellation.py:196-208`): commander == {everyone, orchestrator}; implementer == {everyone, crew}; interrogator == {everyone}; charter == {everyone, orchestrator, crew}. `assertEqual` on these sets means **adding a new reference file whose name matches `global-*.md` would fail these assertions.** A new file NOT matching that glob (e.g. `scoped-nulls.md`, like the existing `design-it-twice-brief.md`) would not.
- `windows.md` bundling is separately pinned (:210-241); `_shared` not-installed-as-skill pinned (:243-256); `--force` refreshes buckets pinned (:258-272).
- One content string is pinned: `test_deep_module_vocabulary_ships_into_installed_skill` (:679-690) asserts "Deep-module vocabulary" appears in the installed `global-everyone.md`. This is the template to follow for dedup: put text INTO an existing bucket file (no new filename), and any similar content assertion keeps working.
- `test_constellation_content.py` exists only as an orphan `.pyc` (no `.py` source) — it does not run; ignore it.
- **Safest dedup path:** append doctrine text into the existing `global-everyone.md` / `global-orchestrator.md` / `global-crew.md` files rather than creating new reference files — zero test churn.

## Not checked
- I did NOT exhaustively confirm the exact inline-carrier file list for every doctrine (grep patterns were approximate for mandatory-compliance and engine-invocation); I verified tier span, which is what drives the bucket choice, and spot-verified the ambiguous ones (unchanged-tree, delegate, world-verification, scoped-nulls).
- I did NOT read the full body text of each doctrine to confirm the inline wordings are byte-identical across skills (dedup may require reconciling near-duplicate phrasings, not a pure cut-paste).
- I did NOT run the test suite; test-pinning findings are from reading `test_install_constellation.py` and enumerating test sources, not execution.
- I did NOT inspect `check_skill_freshness.py` internals beyond confirming its "manifest.json" refs are the templates manifest.
- I did NOT audit CI config (no `.github/workflows` checked) for whether anything there reads root `manifest.json`; the code-side grep found nothing.
- "fleet-doctrine" carrier for crew-idle: I treated it as orchestrator-tier content (commander/admiral); I did not locate a separate `fleet-doctrine` file/skill.
