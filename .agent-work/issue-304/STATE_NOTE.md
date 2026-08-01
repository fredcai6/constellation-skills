# Crash-resume state note - issue-304

- **step:** execute - gate g1-integrate (blocked on re-review verdict), then g2
- **slug:** `issue-304` - branch `epic-298/304` - worktree `C:/Programs/constellation-skills-wt/e298-304`
- **next command:** `py C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-304/execute.json current`
- **pid:** none - foreground commander; re-review is resumed subagent `a9717a0c8b80d89fd`
- **expected artifact:** `.agent-work/issue-304/crew-handoffs/g1-review-result-2.md` (fresh APPROVE/BLOCK)

_Updated: 2026-08-02T00:05:00Z_

## g1: BUILT AND GREEN, awaiting re-review verdict only

Required suite **91 passed**; `--self-test` exit 0; **FULL suite exit 0**. B1 fixed both directions
(bad substitute -> exit 10, real substitute -> exit 0, positive control checked). M4 pinned with
multi-element filler cases. Mutation floor asserts the mutation APPLIED via strict count delta.

**If the verdict is APPROVE:** attest `g1-integrate` p1, start it, attach the review-result with
`--field verdict=APPROVE`, then `advance g1-integrate` (the command check re-runs on advance; it is NOT
attestable).

## g2 IS READY TO DISPATCH - handoff is written and already updated for PRE-B

`.agent-work/issue-304/crew-handoffs/g2-implementer-handoff.md`. Two things were added after PRE-B and
they are the highest-value items in the gate:

1. **THE ANCHOR CHANGE.** Re-anchor `tasks.context.imperative` from "Read the current map ..." to
   **"Before you open any source file, resolve and read the map input."** PRE-B measured that the
   late-anchored form (served `:40`, "BEFORE authoring execute.json") produces exact compliance with
   zero orientation - #698 read source at call 25 and the map at call 57 and satisfied it. Context
   precedes exploration; plan does not. **This is the untested variable.**
2. **The fallback oracle.** Corpus-declared fallback set (README.md, AGENTS.md, docs/ index, CLAUDE.md)
   whose resolution is verified by FILESYSTEM EXISTENCE - an oracle the agent does not author.
   Agent-declared additions allowed but LABELLED UNVERIFIED. Partial fix; do not claim it closes the gap.

Dispatch via `run_crew.py --backend external` after `recover_crews.py issue-304` is clean, then an Agent
subagent, then `--verify-result`.

## Pre-registration is DONE and committed - do not redo it

- `0119fa4` - TRIPWIRES.md T1-T4 (the prose deletions)
- `1662b90` - T5 (the anchor change)
- `b9773c9` - run artifacts

g3 files episodes AFTER the run, each citing these SHAs, with a REAL observed-behavior.

## Do NOT do these

- Do not point ANY tooling at `C:/Programs/f1Brainz`. A sibling PRE-B dispatch is capturing against it.
  Use a local fixture or scratch clone. (`orient` WRITES a receipt into whatever --root it gets.)
- Do not build a bootstrap/CLAUDE.md stanza (Q1 ruled: map is orchestrator content).
- Do not fix #341, #342, #344, or the `--receipt-dir` item.
- Do not overclaim: necessity gate is a REGRESSION FLOOR, sensitivity 0/4 specificity 0/1.

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
