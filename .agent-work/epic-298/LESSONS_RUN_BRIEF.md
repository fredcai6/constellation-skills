# Run Brief: `epic-298`

Compiled for the Lessons Auditor. Deliberately short — pointers and telemetry, not narrative. The run log is 400+ entries; **do not read it as a story, sample it against what you are classifying.**

## Intent

One closed vertical slice proving Constellation skills can enter, consume and improve a shared observable knowledge substrate: the reworked lessons/episode framework (B1) and the Commander map-first tracer (B3), under B0's stochastic-boundary and two-bin principles. Honest nulls are complete deliverables.

## Shape

Fleet of 11 dispatches across 4 waves · 7 of 12 epic issues closed at compile time (#304, #305, #307, #308, #310 open) · Opus for cold-panel issues, Sonnet for #309 and prep · **three commanders died on external limits or handed off mid-run; #304 has had three successive commanders.**

## Project-Customized Templates

`.agent-work/templates/` — check against `.baseline/` per TEMPLATES_MANIFEST before attributing any defect to a shipped template. **`COMMANDER_SPINE.template.json` is being modified by #304 in-flight** (map-first anchor + a new `c2` orientation gate); a defect found there may be this epic's own change, not baseline.

## Artifact Paths

- **Run log:** `.agent-work/epic-298/ADMIRAL_LOG.md` (large — sample, do not read through)
- **State note:** `.agent-work/epic-298/STATE_NOTE.md` (the digest; read this first)
- **Launch orders:** `.agent-work/epic-298/launch-orders/` — all 9 on `main` as of `22d0205`
- **Measurement arms:** `.agent-work/epic-298/baselines/` (PRE-A + addendum + probes), `.agent-work/epic-298/preb/` (PRE-B)
- **Harvests:** `.agent-work/epic-298/harvest/{300,301,303}/`
- **Commander archives:** `.agent-work/archive/2026-08-01-{299,309}/`
- **Feedback:** `.agent-work/AGENT_FEEDBACK.md`, `.agent-work/CONSTELLATION_FEEDBACK.md`
- **Playbook:** `.agent-work/LESSONS.md` — **at its 20/20 cap, and Tommy has ruled it a dead end.** #308 retires it: episodes accumulate, consolidation lands in `docs/agents/`, live agents read local+global doctrine only. **Do not route graduations back into it.**

## Known Telemetry Highlights

- **`a-check-that-cannot-fail`: 6 distinct costumes**, plus two structural findings — *you cannot audit your own falsifiability* (graded side) and *a command that executes is not a command that decides* (grader side). See #337. **A vacuous check plus an honest crew reads exactly like a passing check plus a compliant crew.**
- **Built-but-not-wired: 8 instances**, filed as one pattern at #345. Commander-304's framing: *"we reliably build the capability and unreliably wire the guarantee."*
- **~40 issues filed this run** (#313–#365), only a handful in the epic's own scope. That volume is the epic's real output and none of it is in its definition of done.
- **Admiral errors, self-reported:** 5+ launch-order claims failed verification against the tree (every one caught by the commander it was handed to); 2 merges past in-flight work stranding artifacts; **3 agents in one worktree**; a blocking ruling that crossed a commander's messages 3 times; endorsing a vacuous negative control while ruling on falsifiability.
- **Engine/infra defects found:** #315 (no cwd on command checks), #344 (installed corpus 18 commits stale, project install shadowed), #357 (lease does not protect child gate plans), #358 (consolidate and artifact emission not atomic), #362 (runtime dependency in no bundle).
- **Rework/BLOCKs:** #304 g1 blocked twice then approved; #305 g1 blocked on packaging; multiple crew reworks. **Every cold plan critic this epic caught a blocking defect — no exceptions.**
- **Corpus contradictions:** #336 (Charter creates the file Commander forbids), #348 (stale doctrine created by this epic's own #326).

## Instruction

Every candidate gets a routed disposition. **Graduations go to a named permanent home — `skills/_shared/global-*.md` (canonical, never the `references/` install copies) or `docs/agents/` — never back into the playbook.** Constellation-scoped lessons always export.
