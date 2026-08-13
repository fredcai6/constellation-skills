# Crash-resume state note — commander-315-native

The run stopped at a HARD context trip on `execute`. This is a governed idle, not a crash:
a **fresh** Commander resumes the SAME spine file (job-file-not-agent-file). It should
cold-start from `current` alone plus the artifacts listed below — it must not be re-briefed
from a handoff document.

- **step:** execute · REFUSED at `start execute` by the Trip HARD gate; a `refresh-request` is pending on the spine
- **slug:** commander-315-native · branch `epic-568/c2-native-isolation` · worktree `/home/tommy/projects/constellation-skills-wt/epic-568-315-native`
- **next command:** `cd /home/tommy/projects/constellation-skills-wt/epic-568-315-native && py scripts/checklist_engine.py --file .agent-work/commander-315-native/spine.json claim --session-id commander-315-native --claimed-by commander-delegated --worktree . && py scripts/checklist_engine.py --file .agent-work/commander-315-native/spine.json current`
- **pid:** none — foreground; no crew was ever dispatched, so nothing is running
- **expected artifact:** `.agent-work/commander-315-native/crew-handoffs/g1-implementer-result.md` (not yet produced)

## Why it stopped

`claude-opus-5` profile is (1M window, 80K soft, 150K hard). The `execute` gate declares
`context_headroom_tokens: 30000`, so its begin-work line is (150000-30000)/1000000 = **12%**.
The reading was **23.8%** — about 238K tokens, over the 150K hard cap even before the gate's
own reserve. The governor correctly refused to let this agent BEGIN the run's longest and
least abandonable gate. The old "reads ~5x high" defect (#252) does not apply: `gauge.json`
names `claude-opus-5`, so the reading resolved the real 1M profile.

## What the fresh Commander inherits (all committed on the branch)

- `MISSION_FRAME.md` — the frame, verified FRAME-OK against the degraded-map receipt
- `PLAN_ALTERNATIVES.md` — two cold candidates and the converged design (candidate B plus two amendments)
- `PLAN_CRITIC.md` — 17 confirmed findings from a cold critic
- `PLAN_CRITIC_TRIAGE.md` — the disposition of every one of them
- `execute.json` — the frozen gate plan, already rewritten to carry the critic's corrections
- `repro_native.py` + `REPRO-before.txt` — the before-state repro, arming case captured
- `COMMANDER_RESULT.md` — the full run record, including what must be floated to the Admiral
- `notes-1.md` (repo root) — working notes

## What it must do first

Read `COMMANDER_RESULT.md` section "Open floats". Two items need the Admiral's answer and
must not be silently decided: mission item 3 (delete `init.c0`), and the correction to the
launch order's non-forwardability claim. Neither blocks implementing halves one and two.

_Updated: 2026-08-13T05:15:00Z_
