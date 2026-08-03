# Crash-resume state note — issue-310

- **step:** execute · gate `g1-implement` (B2 evidence gate (a): the corpus/per-role surface census)
- **slug:** `issue-310` · branch `epic-298/310` · worktree `C:/Programs/constellation-skills-wt/e298-310` · PR **#410** (open, do NOT merge — hand up)
- **next command:** `python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file C:/Programs/constellation-skills-wt/e298-310/.agent-work/issue-310/execute.json current`
- **pid:** none — foreground (crews dispatched via `run_crew.py`, blocking)
- **expected artifact:** `.agent-work/issue-310/TRENDS.md` + `.agent-work/issue-310/trends/{measure_surface.py,trends.json,panel.json}`

_Updated: 2026-08-03T03:10:00Z_

---

## What a fresh agent must know before touching anything

**This is HITL and architectural. You assemble evidence; TOMMY makes the kernel-break call.** Do not
self-adjudicate. The only failure mode is an **unattributable** verdict.

**The verdict is already largely determined and it is a sanctioned outcome.** Do not go looking for a way
to make it more positive:

- `SELECTED-OUTCOME` is heading for **`not-yet-earned`**. The spec calls that success.
- **`break-proceeds` is FORECLOSED**, by logic not by numbers: gates (a) and (b) are conjunctive and
  gate (b) was never run. The three-outcome frame **resolves to a two-way call**.
- **Gate (b) is n = 0** — not weak evidence, *no* evidence. Every refresh/cold-start relaunch in this epic
  held the **full monolith**, so the treatment was never varied. **Never enter a relaunch count in the
  (b) column.**

**Binding artifacts, in reading order:**
1. `.agent-work/issue-310/PRE_REGISTRATION.md` — committed **before** the instrument existed. Fixes the
   bin definitions, H1/H2/H3, the 5-row outcome-selection table, and the void criteria. **Binding.**
2. `.agent-work/issue-310/PROBLEM_STATEMENT.md` and `MISSION_FRAME.md`.
3. `.agent-work/issue-310/PLAN_ALTERNATIVES.md` — panel convergence + disposition of all 15 critic findings.
4. `.agent-work/epic-298/launch-orders/LAUNCH_ORDER-310.md` — the frozen principal.

**Numbers already verified in this Commander's own hands (do not re-derive from memory):**

| quantity | value | at |
|---|---|---|
| commits touching `skills/` since baseline | **2 or 3 — ambiguous, and that is a finding** | `baseline/304-trend-snapshot`..`origin/main` |
| NARROW-ALWAYS-LOADED (`skills/*/SKILL.md`) | 15,831 → **15,858** words (+27, **+0.17%**) | baseline → `origin/main` |
| corpus | 63,681 → **63,781** words (net **+100**) | baseline → `origin/main` |
| gross growth vs deliberate deletion | **≈272 gross growth against a 172-word tripwired deletion** | same window |
| `SKILL.md` count | **19** (`_shared` excluded per `install_constellation.py:245`) | `origin/main` |

**Traps that have already bitten this run:**
- The baseline is **NOT an ancestor of `main`** (#304 squash-merged). Address baselines **by tag**
  (`baseline/304-trend-snapshot`, `baseline/304-g2-approve`) — a bare sha is GC-eligible.
- The bare term **"always-loaded" is BANNED**. Use `NARROW-ALWAYS-LOADED` / `WIDE-ALWAYS-LOADED`.
- Report **gross against gross, never net** — net hides the deletion inside the growth.
- Two of this run's own gate checks were **checks that could not fail** and had to be replaced. Re-run any
  check you rely on against a **decoy** before trusting it.
- `py` is Python 3.12 with **no pytest** and silently no-ops under PowerShell. Use `python` (3.14.x).
- Peer→peer `SendMessage` does **not** reach `commander-310`; all three panel agents had to relay through
  the Admiral (`main`).

**Do NOT merge** (`gh pr merge` is vetoed by the harness classifier, #408 — Tommy runs merges).
**Do NOT commit to `main`.** Commit at every gate; push; the PR is already open.
