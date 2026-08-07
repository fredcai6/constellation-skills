# Design-it-twice Brief: `I1 engine answerability`

## The one thing being designed twice

The **engine answerability interface**: how an agent driving a constellation checklist (spine/survey) asks the engine about its own state, and how a refused verb guides recovery — such that there is *never* a reason to open spine.json/cycle JSON or the engine's source. One decision, realized differently per agent: what the query/recovery surface is, where it lives, and what it promises.

Evidence base (read these): `.agent-work/explore-design-thrust/excursions/x1-overread-RESULT.md` (measured over-read: agents read spine.json for condition ids; read engine SOURCE hunting an unblock verb after terse REFUSED; `current --verbose` truncation forces raw reads), `.agent-work/explore-design-thrust/IDEAS_BOARD.md` (ideas 1–2, package A). Engine source: `C:/Users/fredc/.claude/skills/constellation-explorer/scripts/checklist_engine.py` (same engine bundled in all skills; ~1046 stmts, verbs listed in argparse).

## Count and panel — a surfaced choice

**N=3 (panel).** This interface is architecture-touching: every constellation role calls it on every run; its shape decides whether the engine-output-only rule is enforceable. When in doubt, panel.

## The constraints (one per agent, each distinct and named)

1. **minimal-interface** — smallest possible addition to the existing verb set; prefer enriching existing outputs (current/REFUSED text) over new verbs; every addition must justify itself against "could an existing verb's output carry this?"
2. **common-caller-first** — design outward from the three observed caller needs in x1 (get condition ids; recover from a refused/blocked state; get untruncated step detail); the interface is whatever makes those transcripts shortest.
3. **ports-and-adapters** — separate the engine's queryable state (port) from its presentations (adapters: human-readable CLI text, machine-readable JSON via e.g. --json); design the port so future adapters (a conductor process, a hook) consume the same state without new verbs.

## Compared on

- **Depth** — does it hide checklist mechanics behind the seam, or leak JSON structure upward?
- **Locality** — is the change contained in checklist_engine.py + rail strings, or does it fan out into every SKILL.md?
- **Seam placement** — is the boundary where callers (agents mid-run) actually stand, i.e. reachable from the exact moment of confusion (a REFUSED message, a truncated line)?
- **Testability** — can "agent never needs the file" be exercised and falsified (e.g. the structure-blindness eval, idea 5)?

## Output — a recommendation, never a menu

Each agent returns ONE candidate interface in deep-module terms (verbs/flags/output contracts, invariants, error modes, what the rail strings promise) + self-scores on the four axes. The orchestrator (not you) synthesizes the recommendation.

## Untaken-road record — loud skips

(maintained by the orchestrator in the spec)

## Panel-vs-single record

Panel of 3 — architecture-touching, every role is a caller.
