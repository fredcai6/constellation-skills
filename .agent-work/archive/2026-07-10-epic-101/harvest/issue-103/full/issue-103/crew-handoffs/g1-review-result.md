# REVIEW_RESULT — g1 (Admiral diet)

REVIEW_RESULT verdict:

**APPROVE**

Engine postcondition attested: `g1-review.c1`.

Target reviewed: the UNCOMMITTED working tree in `C:\Programs\constellation-wt-103` (not `main...HEAD`). Independently reproduced every grep, both word counts, and the suite. Did not trust the IMPLEMENTER_RESULT — regenerated its evidence.

## Scope
`git status --porcelain` = exactly the three allowed files, nothing else:
```
 M skills/admiral/SKILL.md
 M skills/admiral/references/fleet-doctrine.md
 M skills/admiral/templates/LATITUDE_CONTRACT.template.md
```
No out-of-scope file touched. `skills/commander/**`, `_shared/**`, `tests/**`, `docs/ROADMAP.md` all untouched. No new `global-*.md` filename introduced.

## Per-check findings

### Meaning preserved — all four critic-flagged MUST-SURVIVE facts present (read from current file text, not just the diff)
1. **"dies or stalls" bullet** (SKILL.md:44) — PASS. Retains "verify from the artifact set (branch/commit/PR/files)", "**clean-room reviewer subagent**", "still confirm it dead before you reuse or sweep its worktree", the `global-orchestrator.md` (§idle-subagent-adjudication) pointer, AND the `fleet-doctrine.md`, "Adjudication invariants" pointer. The merge-gating invariants that were trimmed from SKILL.md:43 (gate on exit code / never chain onto watch / close only on verified-merged / re-validate after promotion) are folded to the same "Adjudication invariants" pointer — a fold-to-pointer, not a drop.
2. **"Field your Commanders' queries" bullet** (SKILL.md:45) — PASS. Retains "you are their reachable tier", the query-fielding imperative, the return-and-relaunch vs dead-Commander-recovery distinction, out-of-band escalation, and the hyphenated `delegate-not-replacement` doctrine pointer to `references/global-everyone.md`.
3. **Harvest "mostly-automatic vs manual-fallback" caveat in BOTH files** — PASS. SKILL.md:56 (closeout item 4): "...harvest is **mostly automatic**; the manual collection above is the fallback for consuming projects on older scripts or any hand reconciliation." fleet-doctrine.md (~line 118): "...the harvest is **mostly automatic**; the manual harvest above remains the fallback for consuming projects on older scripts, or any hand reconciliation."
4. **Compact-step operative caveat** (fleet-doctrine.md:158-163) — PASS. Retains compaction best-effort ("run it if the harness exposes it, else rely on auto-compaction"), reload mandatory ("the reload is not"), and "A spine instantiated with its own `compact` step still runs it to completion."

### History framing gone — PASS
`grep -rniE "learned from field fleets|is now|now mechanical|now point|removed —|Live grounding|\(this epic\)|before this change|this epic"` across all three files → exit 1 (no match). War-story remnant sweep `grep -rn "issue-54|improvise|12+ manual|snapshot-then-delta|20260706-dogfood-audit"` → exit 1. The "learned from field fleets" heading is now plain "Operating doctrine:"; "is now engine-enforced" → "The spine enforces state-note-first"; "This is now mechanical" → "This is **mechanical**"; the issue-54 improvise war story and "(this epic)" label (LATITUDE_CONTRACT "Worked example (this epic)" → "Worked example") are all removed/detemporalized.

### No forbidden signature in SKILL.md — PASS
`grep -nE "Unchanged-tree shortcut|idle_notification|breaks recurrence counting|delegate is not a replacement"` → exit 1. Required lowercase/hyphen forms retained: `§unchanged-tree-shortcut` (SKILL.md:61) and `delegate-not-replacement` (SKILL.md:45). Note "recurrence counting" (unqualified) legitimately survives in item 4's rationale; the forbidden phrase is specifically "breaks recurrence counting", which is absent.

### Pointer names present — PASS
`global-everyone.md`, `global-orchestrator.md`, `fleet-doctrine.md` all present in SKILL.md.

### fleet-doctrine.md:10 provenance — PASS (correctly KEPT)
"Distilled from field fleets (f1brainz epics #372/#378/#453)..." present and intentionally retained (honest-null); not treated as a defect.

### Suite green — PASS
`py -m pytest tests/test_install_constellation.py -q` → `38 passed, 118 subtests passed in 3.13s`.

### Reported evidence reproduced
- Word counts: SKILL.md 1410 → 1405; fleet-doctrine.md 1630 → 1541 (matches IMPLEMENTER_RESULT exactly).
- Forbidden greps empty, pointers present, suite green — all independently confirmed.

## Blockers
None.

## Out-of-scope observations
None. The diff is confined to register/framing edits (temporal → timeless, dup → pointer) with no behavioral or structural change.

## Workflow feedback
- Fold-vs-cut rulings were pre-decided in the handoff, and the trims are genuine duplicate-to-pointer folds (merge-gating invariants, worktree-isolation mechanics) rather than drops — meaning-preservation held cleanly, no register-loss.
- The handoff's explicit MUST-SURVIVE list with exact substrings made independent verification fast and unambiguous; a good pattern for register-sensitive diet gates.
