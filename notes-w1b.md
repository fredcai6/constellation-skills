# Working notes — w1-verdict (#371, epic 569 wave 1)

Sole-writer scratch file per LAUNCH_ORDER File Ownership. Terse; the durable artifacts are
`.agent-work/w1-verdict/{MISSION_FRAME,PLAN_ALTERNATIVES,PLAN_CRITIC,execute,REPLAN_INPUT,RESULT}.md/.json`
and the crew handoffs/results under `.agent-work/w1-verdict/crew-handoffs/`.

## Chosen shape
Bare list = membership (`have in want[k]`). Rejected `{"any_of": [...]}` — ties on backward/forward
corpus-collision risk (zero list/dict-valued match or payload values anywhere in the sampled
corpus), loses on Depth (bare list is literally the shape #371 shows an author naturally writing)
and Locality (no shared-helper shape-detection edge cases). See `PLAN_ALTERNATIVES.md`.

## In-flight fixes beyond the two named comparison sites
- A present-but-non-`dict` `match` crashed both sites (`AttributeError` on `.items()`) before this
  run — worse than the wedge (crash, not silent). Guarded at both sites; `validate_spine` flags it
  as a **blocking shape fault**, not the new report-only family. `PLAN_CRITIC.md` Finding 1.
- Shared comparator helper (`_artifact_match_satisfied`) replaces the two sites' inline duplicate
  logic — pure refactor, `PLAN_CRITIC.md` Finding 2.

## Real limitation found, not fixed (floated)
`validate_spine.validate()` is only called from `generate_spine.py` and `spine_lifecycle.py` — never
from the path a Commander uses to hand-author `execute.json` (this run's own `execute.json`
included). The new guard does not cover the most common real authoring path. Wiring it in is
check-wiring, fenced to `w1-wiring` this wave. `PLAN_CRITIC.md` Finding 3, `REPLAN_INPUT.json` D1.

## Process notes (also captured as episodes)
- Crew door-binding gap: both cli-backend crews got no `SPINE_FILE`/`SPINE_SESSION` despite
  `crew-runs.json`'s `door_bound: true`; each authored its own local plan/survey and drove it via
  CLI. Episode w1-verdict-001.
- CLI mutating verbs need explicit `--session-id` on every call once a lease is claimed (the shipped
  template's "no session id argument" framing is MCP-door-specific). Episode w1-verdict-002.
- Map is DEGRADED-UNPARSEABLE at base commit 244665ee (map/INDEX.md references nonexistent packet
  dirs; independently reproduced via `tests/test_code_map.py`'s freshness test, 3x). Episode
  w1-verdict-003, `REPLAN_INPUT.json` D0.

## Evidence commit
Red-proof ran at `244665ee0f669a0bb23847c8fa695c430910c06d` (base, pre-fix): `False`.
Post-fix green-proof + full suite ran against the working tree that became this run's single
commit (see `RESULT.md` for the exact SHA once committed — this note is written before that commit
lands).
