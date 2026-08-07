# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1` — Admiral diet (fold operating-doctrine list + detemporalize admiral-owned history framing)

## Completed slice
Meaning-preserving diet of `skills/admiral/SKILL.md` and `references/fleet-doctrine.md` (plus one label line in `LATITUDE_CONTRACT.template.md`): dropped "learned from field fleets" origin-story framing, folded duplicated provisioning/merge-gating mechanics down to pointers, and rewrote all history/temporal framing as timeless current truth. No operative rule lost.

## Completed edits per item A–N
- **A** — DONE. `SKILL.md` heading `Operating doctrine, learned from field fleets:` → `Operating doctrine:`.
- **B** — DONE. "One Commander per issue" bullet: cut the inline 3-step provisioning restatement + `isolation:"worktree"` no-op fact to the fleet-doctrine pointer; kept admiral deltas (one-per-issue, explicit provision+verify-before-wave, never-two + stop/confirm-dead, model-tier pick, Budget slot). Applied the handoff's target wording.
- **C** — DONE (no-op). "Every dispatch / Right-size / One writer / Status to the user" bullets kept verbatim.
- **D** — DONE. "Merge green" bullet: cut the merge-gating clause (duplicates "Adjudication invariants") to a pointer; kept sequencing/verify-main/rebase deltas. Applied target wording.
- **E** — DONE (kept, no change needed). "A Commander that dies or stalls" bullet already carried all MUST-KEEP-INLINE items (artifact-set verify, clean-room reviewer subagent, never-block-on-dropped-verdict, confirm-dead-before-reuse, both pointers to §idle-subagent-adjudication and fleet-doctrine "Adjudication invariants") and had no history framing. Left intact.
- **F** — DONE (kept). "Field your Commanders' queries" bullet retains "you are their reachable tier", query-fielding, return-and-relaunch vs dead-recovery distinction, out-of-band escalation via latitude contract, and the hyphenated `delegate-not-replacement` pointer to `global-everyone.md`. No cut.
- **G** — DONE. "Surviving long detached compute" bullet: rewrote "State-note-first is now engine-enforced" → timeless "The spine enforces state-note-first: `execute` refuses to start until … (precondition p2)"; kept pointer + operative fact + LESSONS.md guidance. Applied target wording.
- **H** — DONE (no-op). "The project's playbook" bullet kept.
- **I** — DONE. Closeout harvest bullet: `g1's git-common-dir resolution now points …` → timeless `Git-common-dir resolution points … mostly automatic; the manual collection above is the fallback …`. Rest of bullet intact.
- **J** — DONE. `fleet-doctrine.md` `This is now **mechanical, not advisory**:` → `This is **mechanical, not advisory**:` ("now" dropped).
- **K** — DONE. `fleet-doctrine.md` harvest-before-sweep paragraph: cut the "Live grounding: this epic … issue-54 had to improvise … g1's git-common-dir resolution now removes …" war story; kept the operative fact (mostly-automatic + manual-fallback). Everything before "Live grounding:" (the harvest-before-sweep rule) unchanged.
- **L** — DONE. `fleet-doctrine.md` compact-step quirk: rewrote the removal/migration narrative as timeless; kept the operative caveat (compaction best-effort, reload mandatory, a spine instantiated with its own `compact` step still runs it).
- **M** — HONEST-NULL KEEP (no edit). `fleet-doctrine.md:10` "Distilled from field fleets (f1brainz epics #372/#378/#453) …" left untouched — a reference is the sanctioned home for platform provenance; grounds the "platform not project" claim. Confirmed intact (still at line 10).
- **N** — DONE. `LATITUDE_CONTRACT.template.md` `**Worked example (this epic).**` → `**Worked example.**` (label only; example body kept).

## Scope
**Files changed:**
- `skills/admiral/SKILL.md`
- `skills/admiral/references/fleet-doctrine.md`
- `skills/admiral/templates/LATITUDE_CONTRACT.template.md`

`git status --porcelain` (excluding gitignored `.agent-work/`) shows exactly these three modified — nothing else.

**Specific exclusions touched:** no — no `skills/commander/**`, no `_shared/**`, no `tests/**`, no `docs/ROADMAP.md`; template edit confined to the one label line (item N); no cut duplicate re-folded into fleet-doctrine.

## Behavior changed
no — doc-only diet, meaning-preserving. Inspection-only test mode. No behavior surface.

## Deliverable Path Check
- **Committed** — all three edited files return `git check-ignore … exit:1` (not ignored → will land in the diff).
- **Local-only** — this IMPLEMENTER_RESULT under `.agent-work/` (gitignored) — intentionally absent from the committed diff.

## Test mode
**Required:** evidence-only (inspection-only — grep + command-derived word counts + full suite green).
**Satisfied:** yes — grep proves FORBIDDEN absent / REQUIRED present; before/after `wc -w` produced; full suite green.

## Evidence

### git check-ignore (3 committed files) — expect exit 1 (not ignored)
```
skills/admiral/SKILL.md exit:1
skills/admiral/references/fleet-doctrine.md exit:1
skills/admiral/templates/LATITUDE_CONTRACT.template.md exit:1
```

### Before/after wc -w
```
BEFORE:  1410  skills/admiral/SKILL.md
         1630  skills/admiral/references/fleet-doctrine.md
AFTER:   1405  skills/admiral/SKILL.md
         1541  skills/admiral/references/fleet-doctrine.md
```
(SKILL.md −5 words; fleet-doctrine.md −89 words. Modest by design — a fold-to-pointer diet, not a rewrite; the bulk of the reduction is the fleet-doctrine "Live grounding" war story cut, item K.)

### Grep — FORBIDDEN absent (expect no output; grep exit 1)
```
$ grep -nE "Unchanged-tree shortcut|idle_notification|breaks recurrence counting|delegate is not a replacement" skills/admiral/SKILL.md
(no output)  grep-exit:1
```

### Grep — REQUIRED pointers present (all appear)
```
$ grep -oE "global-everyone.md|global-orchestrator.md|fleet-doctrine.md|delegate-not-replacement|§unchanged-tree-shortcut" skills/admiral/SKILL.md | sort -u
delegate-not-replacement
fleet-doctrine.md
global-everyone.md
global-orchestrator.md
§unchanged-tree-shortcut
```
The lowercase `§unchanged-tree-shortcut` and hyphenated `delegate-not-replacement` both survive with their safe forms.

### Full suite tail
```
$ py -m pytest tests/test_install_constellation.py -q
38 passed, 118 subtests passed in 3.65s
```
Also re-run by the engine as m3-verify's command check on `advance` → `m3-verify -> complete` (check passed).

## Engine run
Gated plan `.agent-work/issue-103/g1-implement-plan.json` driven to `DONE: no open items`. Lease `g1-sess-001` claimed, all four items (`m0-context`, `m1-skill`, `m2-fleet-template`, `m3-verify`) attested/advanced to complete, lease released.

## Map Impact
- **Structural anchors touched:** `skills/admiral/SKILL.md`, `skills/admiral/references/fleet-doctrine.md`, `skills/admiral/templates/LATITUDE_CONTRACT.template.md` — prose diet only; no symbol/structure/boundary change.
- **Constraints/assumptions touched:** residual-signature test (`tests/test_install_constellation.py` ~735) still green; pointer-name preservation (not suite-covered) verified by grep. Fold-to-pointer keeps fleet-doctrine as the single home for provisioning + adjudication + survival mechanics; SKILL.md now references rather than duplicates them.
- **Decision candidates:** none forced beyond the given rulings.
- **Trust limitations / drift found:** none — no exact-edit target drifted; every specified old-string matched current file text.

## Docs/contracts touched
- `skills/admiral/SKILL.md`, `skills/admiral/references/fleet-doctrine.md`, `skills/admiral/templates/LATITUDE_CONTRACT.template.md` (all in allowed scope).

## Assumptions
- Item B/D/G/I "adjust wording to flow" latitude: used the handoff's target wording verbatim where given; substance preserved.
- `docs/agents/engine-config.json` (plan `config_ref`) does not exist in this worktree; engine resolves to empty config → defaults. Confirmed harmless (`load_config` returns `{}` when the ref is absent).

## Stop conditions hit
- none. No cut required dropping an operative rule; no FORBIDDEN string was unavoidable; suite stayed green; scope not exceeded.

## Out-of-scope observations
- none.

## Workflow Feedback
Mandatory section.

- **Handoff gaps:** none material — the handoff was unusually precise (exact old→new strings per bullet, explicit fold-vs-cut rulings, FORBIDDEN/REQUIRED lists tied to a named test). One minor note: item G's target text refers to "(precondition p2)" while `fleet-doctrine.md` describes the STATE_NOTE gate without numbering it p2 in that section — I preserved the handoff's "p2" verbatim since it was the specified target; if the spine's actual precondition id differs, that's a pre-existing label to reconcile, not introduced here.
- **Context rediscovered:** the plan template's `config_ref` points at `docs/agents/engine-config.json`, which is absent in this repo layout (`docs/agents/` does not exist). Had to confirm the engine tolerates a missing ref. A handoff line noting "no engine-config in this repo; defaults apply" would have saved a lookup.
- **Instructions improvised around:** the `IMPLEMENTER_PLAN` template's TDD-shaped m1 (red/green postconditions) does not fit an inspection-only doc diet; per the template's own "collapse to the single green/observable postcondition" guidance I used check:null attests for the edit steps and a single command-check (the suite) for the final verify gate. Also: engine `record` requires `--result`; the command-check actually executes on `advance`, not `record` — the schema doc could state that ordering more prominently.
- **What would have made this easier:** a one-line "engine-config absent in this worktree; plan runs on defaults" note in the handoff, and (nice-to-have) a canonical inspection-only plan skeleton in the implementer templates so doc-diet gates don't have to bend the TDD-shaped default.

## Return status
`complete`
