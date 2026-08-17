# Implementation Result

## Assigned gate
`g4-implement` — dispose issues **#596** and **#526**.

## Completed slice

Both issues disposed, each backed by a grep rather than an opinion, and each with the negative
quoted. Full reasoning and all quoted output live in the two disposition files; this result is the
summary and the verification.

- **`.agent-work/567-d1/dispositions/596.md`** — **reproduces, sharper than framed.** The issue's
  crux is confirmed: the `feedback` gate has exactly one postcondition (`verify_episode_captured.py`),
  so `commander-delegated`'s *"A `FENCE.md` citation without the staged export still fails the gate"*
  is **false as written**. Two corrections to the issue's framing, both measured: (a)
  `CONSTELLATION_FEEDBACK.md` was never retired — `verify_retirement.RETIRED_NAMES` holds only
  `LESSONS.md` / `AGENT_FEEDBACK.md` — so the defect is not a retired file still being mandated; (b)
  the fourth site the issue names (the `feedback` imperative's "Include the crew Workflow Feedback")
  is **refuted** — it names no file and mandates no export, so it was not changed. The real defect:
  **three live sites mandate collecting or staging an export that zero gates write.** Repaired by
  rescoping each to "collect it where one exists", not by deleting the channel.
- **`.agent-work/567-d1/dispositions/526.md`** — **split verdict.** Defect 1 **does not reproduce**,
  and `git log -S` over all history shows it never did in the corpus: the phrasing lived only in
  issue #456's own `.agent-work/` run records, so "stock close criteria" is a misattribution. No fix
  was manufactured for it. Widening by *shape* as the handoff directed did find the same defect with
  a different script name — 16 of 17 shipped command checks use a `<*-skill-dir>` resolver token and
  `REVIEW_SURVEY.template.json`'s `r6-fowler.c1` was the one bare path — fixed. Defect 2
  **reproduces**; the convention is now written in `skills/reviewer/SKILL.md`, from this lane's own
  two-round `g1b` review.

## Scope

**Files changed:**
- `skills/commander-delegated/SKILL.md` (#596 — the false gate claim)
- `skills/admiral/SKILL.md` (#596 — the "mandated substep"; plus `harvest` → `collect` at :97 for the
  glossary's one-name-per-thing)
- `skills/admiral/references/fleet-doctrine.md` (#596 — "removal is not permitted until it is
  collected")
- `tests/data/store_mentions.approved.txt` (#596 — **lockstep census upkeep, see below**)
- `skills/reviewer/SKILL.md` (#526 defect 2 — the survey-reuse convention)
- `skills/reviewer/templates/REVIEW_SURVEY.template.json` + `.agent-work/templates/` overlay +
  `.agent-work/templates/.baseline/constellation-reviewer/` mirror (#526 defect 1 widened — all three
  copies, byte-identical after the edit, each re-validated with `json.load`)

**Specific exclusions touched:** no. No fenced file was edited — `docs/agents/**`,
`skills/workbench/**`, `episodes/**`, `scripts/mcp_spine_server.py`, `scripts/run_crew.py`,
`scripts/checklist_engine.py`, `map/INDEX.md` and `tests/test_cli_retirement_guard.py` are all
untouched. Two findings that land in fenced files are staged as triage candidates instead.

**One file outside the handoff's allowed-scope list, deliberately, and flagged:**
`tests/data/store_mentions.approved.txt`. It is not fenced. Three of the four #596 sites are keyed
**line-for-line** in that frozen approval census, so editing the prose fires two tests in
`tests/test_retirement_guard.py` — a suite the handoff never names. Measured, not assumed: after the
three prose edits and before the census moved, `2 failed, 14 passed`, naming
`skills/admiral/SKILL.md:96` as an unapproved store mention and the census entry as stale. The census
is a lockstep artifact of the text it approves, exactly like the `.agent-work/templates/` +
`.baseline/` mirrors the handoff *does* require be moved together, and gate `g1b` of this lane set
the precedent — commit `aeba10ae` edited `skills/**` and moved this same census in the same commit.
Moved it the same way (entries plus the reason line above each); `16 passed` after.
`skills/admiral/references/fleet-doctrine.md` needed no census edit — only its `episodes/`-bearing
line is keyed, and the reflow was authored around that one line, leaving it byte-identical.

## Behavior changed

**No.** Doctrine and doc text only, plus one command-check path that resolves to a byte-identical
string in this repo (`python scripts/verify_fowler_pass.py ...`) and to the correct installed path in
a consuming project. No runtime code changed; no script's capability was touched.

## Map Impact

No architecture map exists in this repo (`map_orient` → `DEGRADED-UNPARSEABLE`), so this is framed
against the handoff's named entry points.

- **Constraints/assumptions touched:** the assumption that a Commander run produces a
  `CONSTELLATION_FEEDBACK.md` export is **removed** from three doctrine sites and replaced by the
  measured fact that no gate writes one. `constraint:episodes-are-not-prescriptions` is honored — no
  successor playbook, no read-and-apply loop, nothing added for an agent to consult.
- **Decision candidates:** whether the export channel should have a *producer* again, or whether the
  workbench template's claim that one exists should be corrected — staged, not decided (fenced file).
- **Claims/evidence produced:** the `feedback` gate's postcondition set, quoted; the zero-write-site
  count across both spines and `commander-core.md`; the 16-of-17 resolver-token classification of
  shipped command checks; this run's own `g1b` two-round survey as the grounding for the new reviewer
  convention.
- **Trust limitations / drift found:** `tests/data/store_mentions.approved.txt` couples the retirement
  guard to the exact wording of skill prose. Any future gate that edits a census-keyed line must move
  the census in the same commit; the handoff's close criteria named only the CLI retirement guard.
- **Triage candidates:** two, staged under `.agent-work/567-d1/triage-candidates/` (below). No issues
  filed, per the standing constraint.

## Test mode
**Required:** `evidence-only` (doc/doctrine change; no runtime behaviour, so no new runtime test is
owed — the guard and the adoption suite are the checks).
**Satisfied:** yes. No script behaviour was changed, so nothing new is owed a test. The one template
edit that *could* have changed behaviour was proven inert in this layout rather than asserted (below).

## Evidence

```bash
# 1. the gate's own closing check, in the anchored form the Commander's g4-integrate uses
test -s .agent-work/567-d1/dispositions/596.md \
  && test -s .agent-work/567-d1/dispositions/526.md \
  && { python3 -m pytest tests/test_cli_retirement_guard.py -q > /tmp/g4-guard.log 2>&1 || true; } \
  && ! grep -oE '^E +(skills|specs|[.]agent-work)/[A-Za-z0-9_./-]+' /tmp/g4-guard.log \
     | sed 's/^E *//' | grep -qv '^skills/workbench/'
```
**Result:** pass. The CLI guard's two surviving violations name
`skills/workbench/references/checklist-engine.md` and `skills/workbench/SKILL.md` — lane D2's fenced
files, expected and untouched by this gate. Nothing outside `skills/workbench/`.

```bash
python3 -m pytest tests/test_mcp_adoption.py -q          # 172 passed, 2 skipped
py -m pytest tests/test_retirement_guard.py -q           # 16 passed
py -m pytest tests/test_shipped_check_commands_resolve.py tests/test_validate_spine.py \
   tests/test_record_postcondition_wiring.py tests/test_fowler_pass.py \
   tests/test_engine_survey_retext_and_newlines.py tests/test_retirement_guard.py \
   tests/test_mcp_adoption.py -q                          # 313 passed, 2 skipped
```
**Result:** pass. The whole suite was **not** run, per the handoff —
`tests/test_gauge_chain_writer_to_trip.py:604` snapshots `.agent-work/` and this run's own engine
records would fail it. Test selection was widened instead: every suite that reads the template or the
census I touched.

```bash
# 3. every edited .json still parses, and the three template copies did not drift
python3 -c "import json; [json.load(open(p)) for p in (...)]"
md5sum skills/reviewer/templates/REVIEW_SURVEY.template.json \
       .agent-work/templates/REVIEW_SURVEY.template.json \
       .agent-work/templates/.baseline/constellation-reviewer/REVIEW_SURVEY.template.json
# d8c1fb421b78799a1cae8662c04fe467  (x3)
```
**Result:** pass. Edited as raw text, never round-tripped through `json.load`/`json.dump`.

```bash
# 4. the resolver-token fix PROVEN to resolve, not asserted — init_work_area.resolve_spine
#    run over the edited template in both layouts
source-repo (no --skill-dir) -> python scripts/verify_fowler_pass.py .agent-work/567-d1/FOWLER_PASS.json
installed skill dir          -> python /home/tommy/.claude/skills/constellation-reviewer/scripts/verify_fowler_pass.py .agent-work/567-d1/FOWLER_PASS.json
installed script exists: True    vendored script exists: True
```
**Result:** pass, and byte-identical to today's resolved text in this repo — so the change cannot
regress this run's own reviewer.

## TDD evidence, if required

Not required (evidence-only mode). But the one check that could have passed vacuously was red-proofed
rather than trusted: the census coupling was **observed failing** (`2 failed, 14 passed`, naming
`skills/admiral/SKILL.md:96`) before the census was moved, and green after (`16 passed`). That is a
guard demonstrated able to reach a failing state, not one assumed to work.

## Docs/contracts touched
- `skills/commander-delegated/SKILL.md`, `skills/admiral/SKILL.md`,
  `skills/admiral/references/fleet-doctrine.md`, `skills/reviewer/SKILL.md` — agent-facing doctrine.
- `skills/reviewer/templates/REVIEW_SURVEY.template.json` (+ two mirrors) — a shipped command check.
- `tests/data/store_mentions.approved.txt` — the approval census, moved in lockstep.
- `.agent-work/templates/TEMPLATES_MANIFEST.json` — **not** updated. It records the baseline sha the
  last install shipped; hand-editing it would claim an install that never ran. Matches gate `g2`'s
  standing call on this branch ("manifest deliberately left honest"). No test reads this repo's own
  manifest against its own baseline.

## Assumptions
- Updating `tests/data/store_mentions.approved.txt` is lockstep upkeep of a `skills/**` edit rather
  than a scope breach. Grounded in gate `g1b`'s precedent on this branch (`aeba10ae`), not asserted —
  and flagged here for the Commander to overturn if that reading is wrong. If it is overturned, the
  three #596 prose edits must be reverted with it; they cannot stand without it.
- The two scripts the handoff put in reach (`scripts/collect_feedback.py`, `scripts/agent_work_root.py`)
  are **out of scope and unchanged**. Reasons given in full in `596.md` §6: `collect_feedback.py` is a
  live tool with a live caller serving a cross-project channel the per-repo episode store cannot
  replace, and `agent_work_root.py:4` is a docstring that describes rather than instructs. Neither
  mandates the export, and #596 is about the mandate.

## Stop conditions hit
None. No stop condition fired: no fenced file needed editing, the `feedback` gate's real
postconditions **confirmed** the issue's sharpest claim rather than contradicting it, and no fix
required a successor playbook — the repair only removes claims about gates and adds no new file,
store, or thing to consult.

## Out-of-scope observations

Two, both staged under `.agent-work/567-d1/triage-candidates/` and flagged into the plan
(`tc1`, `tc2`). No issues filed.

1. **`feedback-export-template-claims-a-writer-that-is-gone.md`** —
   `skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md:4` still says the export is
   *"Appended by the feedback/closeout steps"*. Measured: no step appends it. This is the
   producer-side twin of the three collector-side sites `g4` just fixed, and the last live claim that
   something writes one. `skills/workbench/**` is fenced to lane D2, and the fix needs a ruling
   (correct the sentence, or give a step the job), not a wording change.
2. **`prose-names-vendored-script-paths-corpus-wide.md`** — skill *prose* names bundled scripts as
   `scripts/<name>.py` at 91 sites across 27 files, which is only correct where the target repo
   vendors `scripts/` at its root; `references/global-everyone.md` says the opposite. The engine-run
   command checks are now clean; this is the prose half, and at 91 sites it is a Curator/Charter
   ruling rather than a `g4` edit.

## Workflow Feedback

- **Handoff gaps:**
  1. **The "gate's own closing check" printed in the handoff can never pass.** Its
     `grep -oE '(skills|specs|[.]agent-work)/...'` is unanchored, so it matches the pytest failure
     *summary* sentence — *"scanned 3098 texts across 216 files (101 under skills/, 2 under specs/,
     113 under `.agent-work/templates/`)"* — and `.agent-work/templates/` is not
     `^skills/workbench/`, so the check fails on a clean tree. The Commander's actual `g4-integrate`
     check (`.agent-work/567-d1/amend-census.json`) already anchors on `^E +` and is correct; the
     handoff carries the older, unanchored copy. I amended my own plan's three checks to the anchored
     form through the engine (`amend --delta`, reason recorded) rather than running a check I knew
     could not pass. **Fix: copy the check text out of the spine, not out of the previous handoff.**
  2. **Close criterion 3 and the fence list both miss `tests/test_retirement_guard.py`.** The handoff
     says "keeps the guard green" and means `test_cli_retirement_guard.py`, but the #596 edits are
     coupled line-for-line to `tests/data/store_mentions.approved.txt`, which a *different* guard
     enforces, and that file appears in neither the allowed-scope list nor the fence list. That is
     the single biggest thing that could have gone wrong here: a lane that edited the three sites and
     ran only the two named checks would have shipped a red suite and never seen it. **Fix: when a
     gate's targets are census-keyed, say so in Allowed Scope and name the census.**
  3. **"The four sites the issue names" was carried forward without being checked.** Site 4 (the
     `feedback` imperative) is not a mandate, and the handoff asks me to "verify each still says what
     the issue claims" — which is right — but frames the count as four throughout, including in the
     required-evidence section. It cost nothing here, but a table of four rows reads as four defects.
- **Context rediscovered:** that `CONSTELLATION_FEEDBACK.md` is **not** a retired file. Both the
  issue's framing and the handoff's phrase "still mandated **after the switch to the episode ledger**"
  imply it was retired alongside `LESSONS.md`; `verify_retirement.RETIRED_NAMES` says otherwise, and
  the whole shape of the fix turns on it — a retired file gets deleted references, a live one gets
  rescoped ones. The handoff's map anchors pointed at the governing doctrine, which was the right
  pointer; the anchor that would have settled it in one read is `RETIRED_NAMES` in
  `scripts/verify_retirement.py`.
- **Instructions improvised around:** none of substance. The engine's `attest` verb takes `--note`,
  not `--why` (the flag `advance` requires) — a small asymmetry worth a line in the engine reference,
  since the refusal for the wrong one is an argparse usage dump rather than the engine's own
  imperative refusal.
- **What would have made this easier:** one line in the handoff's Verification Commands naming
  `tests/test_retirement_guard.py` and the census. Everything else in the handoff was strong — in
  particular, pre-ruling #526 as a `guess`, printing the Commander's preliminary greps as things to
  *confirm or refute* rather than as findings, and saying outright that an evidenced negative is a
  complete disposition. That framing is why defect 1's negative got written up with the same rigor as
  the fixes instead of being quietly padded with a manufactured change.

## Return status
`complete`
