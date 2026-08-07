# Implementer Handoff

Concise fragments. Omit filler.

## Gate
`g1` — Admiral diet (fold operating-doctrine list + detemporalize admiral-owned history framing)

## Task
Edit `skills/admiral/SKILL.md` and `skills/admiral/references/fleet-doctrine.md` (and one line of `skills/admiral/templates/LATITUDE_CONTRACT.template.md`) to: (a) drop the "learned from field fleets" history framing; (b) trim operating-doctrine bullets that DUPLICATE `_shared` buckets or `fleet-doctrine.md` down to a pointer, keeping genuine admiral-specific deltas inline; (c) rewrite all history/temporal framing as timeless current truth, preserving every operative rule. Meaning-preserving throughout. This is a diet, not a rewrite — keep the voice and structure; change only what these instructions name.

## Protected Intent
Admiral doctrine still says exactly what it said operationally; only duplication and origin-story framing are removed. An agent loading admiral loses NO operative rule.

## Test Mode
inspection-only — doc edits; verified by grep + command-derived word counts + full suite green (no behavior surface).

## Close Criteria
- `skills/admiral/SKILL.md:36` heading "Operating doctrine, learned from field fleets:" → "Operating doctrine:" (drop the history framing).
- Bullet edits below applied exactly as specified (fold-vs-cut per bullet).
- All temporal/history framing in both files rewritten timeless per the list below.
- Every FORBIDDEN string (below) is ABSENT from `skills/admiral/SKILL.md`; every REQUIRED pointer name present.
- Full suite green: `py -m pytest tests/test_install_constellation.py -q`.
- Before/after `wc -w` for both files produced.

## Allowed Scope
`skills/admiral/SKILL.md`, `skills/admiral/references/fleet-doctrine.md`, `skills/admiral/templates/LATITUDE_CONTRACT.template.md` (one line only, item L below). Nothing else.

## Specific Exclusions
- NOT `skills/commander/**` (owned by issue #107).
- NOT `_shared/**` (owned elsewhere; do not touch `_shared/windows.md` provenance lines — they are a sanctioned honest-null keep).
- NOT `tests/**`, NOT `docs/ROADMAP.md`.
- Do NOT re-fold a cut duplicate into `fleet-doctrine.md` — a bullet that duplicates a `_shared` bucket is CUT to its pointer, full stop (its home already exists).

## Constraints
- **FORBIDDEN strings — must NOT appear anywhere in `skills/admiral/SKILL.md` after your edit** (a residual/pin test asserts their absence): `Unchanged-tree shortcut` (capital-U + space; the existing lowercase `§unchanged-tree-shortcut` at ~line 61 is SAFE — keep that form, do NOT Titlecase it), `idle_notification`, `breaks recurrence counting`, and the un-hyphenated phrase `delegate is not a replacement` (the existing hyphenated `delegate-not-replacement` pointer at ~line 45 is SAFE and MUST survive — keep the hyphen).
- **REQUIRED pointer names — must remain present in `skills/admiral/SKILL.md`**: `global-everyone.md`, `global-orchestrator.md`, `references/fleet-doctrine.md`. Do not sever any carrier pointer.
- Do not introduce any new `global-*.md` filename.
- Reconcile-then-cut: keep genuine admiral operating deltas inline; cut only what is genuinely duplicated elsewhere.

## Exact edits

### A. Heading — `SKILL.md:36`
`Operating doctrine, learned from field fleets:` → `Operating doctrine:`

### B. Bullet "One Commander per issue" (~line 38) — TRIM duplicated provisioning mechanics to the fleet-doctrine pointer; KEEP deltas (one-per-issue, model-tier + Budget slot, never-two).
The full 3-step worktree-provisioning gate and the `isolation:"worktree"` no-op fact already live in `references/fleet-doctrine.md` ("Worktree isolation is a harness no-op on Windows") and `_shared/windows.md`. Replace the inline restatement with a pointer, keeping the admiral deltas. Target result (adjust wording to flow, keep substance):
> One Commander per issue, each in its own worktree you **provision explicitly** and verify before the wave — see `references/fleet-doctrine.md`, "Worktree isolation is a harness no-op on Windows" (the Agent-tool `isolation:"worktree"` flag is a silent no-op; provision, gate, and never run two Commanders in one worktree — stop/confirm-dead the original before a continuation). Pick model tier per issue complexity — least-powerful model that works, escalating only when complexity, ambiguity, or risk demands it — and record it in the launch order's Budget model-tier slot.

### C. Bullets "Every dispatch carries LAUNCH_ORDER", "Right-size the dispatch", "One writer per shared document", "Status to the user" (~lines 39-42) — KEEP as-is (genuine admiral deltas, no duplication, no history framing).

### D. Bullet "Merge green" (~line 43) — CUT the merge-gating clause that duplicates fleet-doctrine "Adjudication invariants" ("gate merges on the check exit codes, never chain a merge after a watch command") to a pointer; KEEP the sequencing/verify-main/rebase deltas. Target:
> Merge green, reviewed PRs sequentially; verify main before each wave dispatch. Hold rebases to wave boundaries; if ground shifts under a running Commander, stop-and-relaunch on fresh ground rather than steering mid-flight. The merge-gating invariants (gate on the check exit code, never chain a merge onto a watch command, close only on verified-merged, re-validate after promotion) live in `references/fleet-doctrine.md`, "Adjudication invariants".

### E. Bullet "A Commander that dies or stalls" (~line 44) — KEEP the admiral deltas; the recovery mechanics already point to fleet-doctrine. MUST-KEEP-INLINE (do not cut): "verify from the artifact set (branch/commit/PR/files)" **and** the **clean-room reviewer subagent**, "never blocking on a dropped verdict", "confirm it dead before you reuse or sweep its worktree", and BOTH pointers — `references/global-orchestrator.md` (§idle-subagent-adjudication) and `references/fleet-doctrine.md` "Adjudication invariants". You may lightly tighten prose but must not drop any of those. No history framing here to change.

### F. Bullet "Field your Commanders' queries" (~line 45) — KEEP. MUST-KEEP-INLINE: "you are their reachable tier", the query-fielding behavior, the return-and-relaunch vs dead-Commander-recovery distinction, the out-of-band escalation via the latitude contract, and the hyphenated `delegate-not-replacement` pointer to `references/global-everyone.md`. No cut.

### G. Bullet "Surviving long detached compute" (~line 46) — REWRITE the history framing "State-note-first is now engine-enforced" as timeless; KEEP the pointer + the operative fact. Target:
> **Surviving long detached compute is platform doctrine, not project lore** — the three kill vectors, watcher-sleep, the "completed"-but-sleeping hazard, detach + state-note-first, and the recovery drill live in `references/fleet-doctrine.md`. The spine enforces state-note-first: `execute` refuses to start until `.agent-work/<epic-id>/STATE_NOTE.md` is filled (precondition p2). Carry its launch-execution rules into every launch order and follow its recovery drill when a ship dies; keep `.agent-work/LESSONS.md` for genuinely project-specific fleet rules rather than relearning platform doctrine there.

### H. Bullet "The project's playbook" (~line 47) — KEEP as-is.

### I. Closeout harvest bullet (~line 56) — REWRITE "g1's git-common-dir resolution now points ... so this harvest is mostly automatic" as timeless; KEEP the operative caveat (mostly-automatic vs manual-fallback). Change the clause to:
> Git-common-dir resolution points the durable trio at one shared root, so this harvest is **mostly automatic**; the manual collection above is the fallback for consuming projects on older scripts or any hand reconciliation.
(Leave the rest of the bullet intact.)

### J. `fleet-doctrine.md:38` — `This is now **mechanical, not advisory**:` → `This is **mechanical, not advisory**:` (drop "now").

### K. `fleet-doctrine.md` ~lines 118-127 (the "Live grounding: this epic ... issue-54 had to improvise ... g1's git-common-dir resolution now removes ...") — CUT the war story, KEEP the operative fact (critic must-survive). Replace the "Live grounding: ..." sentence through "... any hand reconciliation." with:
> Git-common-dir resolution points the durable trio at one shared root, so the harvest is **mostly automatic**; the manual harvest above remains the fallback for consuming projects on older scripts, or any hand reconciliation.
(Keep everything before "Live grounding:" — the harvest-before-sweep rule itself — unchanged.)

### L. `fleet-doctrine.md` ~lines 165-172 (compact-step quirk) — REWRITE the removal/migration narrative as timeless; KEEP the operative caveat. Replace with:
> - The Commander spine has no dedicated `compact` step: `/compact` is user-level and most harnesses don't expose it to agents, so context headroom and the **mandatory** commander skill reload open `execute`'s imperative directly — compaction is best-effort (run it if the harness exposes it, else rely on auto-compaction), the reload is not. A spine instantiated with its own `compact` step still runs it to completion.

### M. `fleet-doctrine.md:10` provenance ("Distilled from field fleets (f1brainz epics #372/#378/#453) ...") — HONEST-NULL KEEP, do NOT edit. A reference is the sanctioned home for platform provenance; this grounds the "platform not project" claim. (Recorded as honest-null in the report.)

### N. `skills/admiral/templates/LATITUDE_CONTRACT.template.md:39` — detemporalize the label only: `**Worked example (this epic).**` → `**Worked example.**`. Keep the entire example body (the classifier-veto fallback shape is operative pedagogy).

## Map Anchors (inbound)
- **Structural:** `skills/admiral/SKILL.md`, `skills/admiral/references/fleet-doctrine.md`, `skills/admiral/templates/LATITUDE_CONTRACT.template.md`.
- **Constraints:** residual-signature test (`tests/test_install_constellation.py` ~735); pointer-name preservation (not suite-covered — verify by grep).
- **Decision anchors:** fold-vs-cut per bullet (rulings given above; do not improvise beyond them).

## Deliverable Path Check
- **Committed** — `skills/admiral/SKILL.md`, `skills/admiral/references/fleet-doctrine.md`, `skills/admiral/templates/LATITUDE_CONTRACT.template.md`; run `git check-ignore <path>` for each, confirm exit 1 (not ignored), record it.
- **Local-only** — `.agent-work/issue-103/crew-handoffs/g1-implement-result.md` (your IMPLEMENTER_RESULT), under `.agent-work/` (gitignored) — intentionally absent from the committed diff.

## Required Evidence
- `git check-ignore` exit codes for the 3 committed files.
- Before/after `wc -w skills/admiral/SKILL.md skills/admiral/references/fleet-doctrine.md`.
- Grep proving FORBIDDEN strings absent and REQUIRED pointer names present in `skills/admiral/SKILL.md`:
  `grep -nE "Unchanged-tree shortcut|idle_notification|breaks recurrence counting|delegate is not a replacement" skills/admiral/SKILL.md` (expect no output)
  `grep -oE "global-everyone.md|global-orchestrator.md|fleet-doctrine.md|delegate-not-replacement|§unchanged-tree-shortcut" skills/admiral/SKILL.md | sort -u` (expect all present)
- Full suite tail: `py -m pytest tests/test_install_constellation.py -q`.

## Verification Commands
```bash
cd /c/Programs/constellation-wt-103
git check-ignore skills/admiral/SKILL.md; echo "exit:$?"
wc -w skills/admiral/SKILL.md skills/admiral/references/fleet-doctrine.md
grep -nE "Unchanged-tree shortcut|idle_notification|breaks recurrence counting|delegate is not a replacement" skills/admiral/SKILL.md
grep -oE "global-everyone.md|global-orchestrator.md|fleet-doctrine.md|delegate-not-replacement" skills/admiral/SKILL.md | sort -u
py -m pytest tests/test_install_constellation.py -q
```

## Suggested Model Tier
`stronger — register-sensitive meaning-preservation across entangled inherited/delta doctrine`

## Authority
All fold-vs-cut rulings are decided (above) — do NOT re-litigate scope or invent additional cuts. If an exact-edit target string does not match the current file text (drift), adapt to the current wording preserving the SAME substance and note it; do not skip the edit. Stop and return if a required operative fact cannot be preserved while making a cut.

## Stop Conditions
Stop and return if: a cut would drop an operative rule you cannot rehome within scope; a FORBIDDEN string is unavoidable; the suite goes red for a reason outside these edits; scope must be exceeded.

## Return Format
Return IMPLEMENTER_RESULT (also WRITE it to `.agent-work/issue-103/crew-handoffs/g1-implement-result.md`): completed edits per item A-N, files changed, before/after word counts, grep evidence (forbidden absent / pointers present), suite tail, assumptions, stop conditions hit, out-of-scope observations, workflow feedback. Your final message must be the complete IMPLEMENTER_RESULT before you idle.
