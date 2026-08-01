# Crash-resume state note - issue-304

- **step:** execute - gate g1-integrate (g1 implement done, g1 review returned BLOCK, rework in flight)
- **slug:** `issue-304` - branch `epic-298/304` - worktree `C:/Programs/constellation-skills-wt/e298-304`
- **next command:** `py C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-304/execute.json current`
- **pid:** none - foreground commander; rework running as resumed subagent `aa5138cd649f1b77e`
- **expected artifact:** `.agent-work/issue-304/crew-handoffs/g1-result.md` updated in place with the B1/B2/B3 fixes

_Updated: 2026-08-01T23:05:00Z_

## g1 status

- g1-implement: COMPLETE. `scripts/map_orient.py`, `<repo-root>` placeholder, `tests/test_map_orient.py`,
  `tests/test_mutation_floor.py`. Exit vocabulary 0/10/11/12/13, clear of argparse(2)/traceback(1)/127.
- g1-review: COMPLETE, verdict **BLOCK**.
- **B1 (blocker, reproduced by me):** `pin_substitutes` writes `content_hash="unreadable"` and
  `is_filler("unreadable")` is False, so a NONEXISTENT substitute path discharges the degraded record at
  exit 0. The exact silent-degradation hole the contract exists to close.
- **B2 (major):** reviewer's own mutation M4 (`not any(is_filler)` -> `not all(is_filler)`) SURVIVED -
  every filler test uses single-element lists where any and all are identical.
- **B3 (minor):** the result artifact claimed `.agent-work/probe/` was removed; it was not.
- Out of scope, filed as triage: `orient` writes a receipt into any `--root` (recommend `--receipt-dir`);
  the mutation kill criterion is class-level, not reason-level.

---

## Run context a fresh agent needs (beyond the five lines)

**Engine lease `commander-304-e298` is HELD.** Pass `--session-id commander-304-e298` on every mutating
call. Release it **only** after the final `advance archive`.

**Spine:** `.agent-work/issue-304/spine.json` — init/context/understand/plan complete, execute in progress.
**Child plan:** `.agent-work/issue-304/execute.json` — 13 tasks, 4 gate triads (g1→g4) + e0-context.

### Rulings already made — do not reopen

- **Q1 RULED: candidate B is OUT.** No bootstrap stanza, no install lifecycle. *The map is orchestrator
  content, not implementer content.* Placing content at a broader tier than its audience is a defect.
- **Q3 APPROVED:** tripwires pre-registered in a committed `TRIPWIRES.md` (git = tamper-evident
  timestamp), episodes filed **after** the run with a real `observed-behavior`. Ruling kept, rationale
  replaced — see `notes-304.md`.
- **Q2 PROVISIONAL GO:** build to necessity + reported-degradation. *Shipping* it as the definitive
  meaning of "primacy" rides with the merge and is still Tommy's. Keep gate-vs-report **flag-flippable**.
- **All 15 critic findings triaged and ACCEPTED**, with two Admiral amendments folded into `execute.json`:
  1. The mutation harness must **assert the mutation APPLIED before asserting red** — a no-op mutation and
     a killed mutant both yield green.
  2. The trend snapshot must **name its consumer** (the next snapshot) and when the successor is expected.

### The framing this ships under — do not overclaim

- The **necessity gate is a regression floor**, measured sensitivity **0/4**, specificity **0/1** against
  the baseline five. **Never** describe it as the fix for the measured defect.
- The genuinely new value is **reported degraded mode**: a repo without a map currently has **no contract
  at all** — silent crawl, no record.
- **Ordering is not mechanizable by the corpus.** Needs a `PreToolUse` hook → settings.json → Tommy's per
  #180. Measured only. Known bypass to name in the writeup: crawl first, write anchors into the frame
  afterward — that is the *measured behavior*, not a hypothetical loophole.

### Facts established — do not re-derive

- Command-check **stdout is discarded**; the **exit code is the only signal** reaching the spine.
- Command checks get **no cwd** → issue **#341**.
- Deletion target is **172 words, 86 per template** (not 112 — corrected twice).
- `"no docs/agents/ overlay at all"` occurs **twice**; the **first is load-bearing** and must survive.
- `docs/agents/` **exists** here; `docs/architecture/` **does not** — this repo is the degraded case.
- Episode store has **no `confirmed`** standing → **#342**.
- Installed corpus is **18 commits stale**, 3 of 11 scripts differ → **#344**.

### Triage filed

**#341**, **#342**, **#343**, **#344** — spine tc1–tc4. `#336` gets the subtraction note when g3 lands.
