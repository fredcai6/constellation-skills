# Ideas Board — `explore-138`

The living record of shared understanding and the **source of truth** for this exploration (issue #138:
the corpus-compliance design pass). Every consolidation updates it. The spec crystallizes from it.

## The point

Cheap models under pressure take cheap exits — skip, theater, quit-early, fabrication, completion-theater,
wait-by-ending-turn. The #126→#129 arc proved four wording clauses take one skill (commander-delegated)
from ~1/3 to 3/3 strict terminal completion, and the #101 simplification review proved the same protective
force was stripped from NINE other skills into pointers that don't fire at load time. The point of this
pass: design ONE coherent counter-doctrine (not scattered fixes) across four strands — clamp restoration,
single-source morale doctrine, engine-carried guidance, proportionality — so every skill in the corpus
finishes honestly, measured with the #129 harness. Kill condition: if measurements show restored wording
alone gets every skill to target, the engine-side strands lose their motivation and should shrink to
the cheapest defensible core.

## Human direction already settled (2026-07-12 session)

- Measurements run **in parallel** (the wake-up/watchdog doctrine makes this safe now); target
  wall-clock per measured comparison ≈ **half an hour**, not hours.
- "The eval bar never moves" was an agent paraphrase, NOT a human ruling — the human explicitly said
  they don't know what it means here. The standing human decisions are narrower: eval `task.md` prompts
  stay pure (zero coaching), and no corners cut on testing. What the *checks* verify MAY change if the
  design warrants it (e.g. engine-emitted sentinel) — surface such changes as explicit decisions.
- Engine-emitted completion sentinel: human asked what it even is — explain, then decide. (Answered in
  session: engine writes the completion artifact itself on terminal release; agents can no longer fake it.)
- Compaction re-injection: human open to discussing; not yet ruled in or out.
- Superpowers is a competitor: constellation-native framing, no imported doctrine (standing).

## Current candidates

**S1 — Clamp restoration (transcription-grade).** Stamp the proven four-clause shape (engine-first entry;
solution-is-the-middle; release-after-final-advance; wait-loop) into the nine stripped skills, ranked:
crew implementer+reviewer → commander-core.md (both modes inherit) → admiral/interrogator → six
pointer-only skills. Design decision: the *pointer-with-force* sentence shape (imperative in the pointer,
elaboration in the shared file). Keep the review's judged-correct removals (no banner resurrection).

**S2 — Morale doctrine, single source.** One canonical pep-talk block: process defines done; scoped
nulls (try another variant); asking up is always legitimate; forbidden exits = quiet abandonment +
fabrication (TC1 anchor). Skills carry one-line pointers WITH force. Where the canonical block lives and
how it is delivered is a design choice entangled with S3.

**S3 — Engine-carried guidance (the real design work; load-bearing interface).** Engine responses carry
the doctrine at each decision point: `advance`/`current` return next imperative + one-line why +
distance-to-terminal; check-FAILURE responses carry the scoped-null/ask-up interceptor; candidate:
engine-emitted completion sentinel on terminal release; candidate: compaction re-injection payload
(engine `current` output as the payload; delivery mechanism unproven for dispatched subagents). Folds in
#134 (gate-vs-fence). Design-it-twice REQUIRED on the response format.

**S4 — Proportionality.** Execute-step judgment for trivial bounded work: inline under the engine's gates
instead of mandatory crew cold-starts (measured: ceremony ≈3 min, crew cold-starts ≈23 min of a 29-min
run). Hard shape: every spine step still runs, gated, engine-driven — proportionality changes HOW a step
is done, never WHETHER. Interacts with S3 (engine distance-to-terminal can carry the "this is a short
run" signal).

## Verdicts

| Verdict | Scope (tested / NOT tested) | Source |
|---|---|---|
| Four wording clauses achieve 3/3 strict terminal completion on sonnet | commander-delegated + euler-1 only; NOT other skills, NOT other tasks, NOT other tiers | #129 rounds 1–3 |
| Bare one-line pointers do not fire at load time for cheap models | the nine stripped skills as shipped by #101; NOT pointers that carry the imperative | SIMPLIFICATION_REVIEW.md |
| Idle sessions don't receive notifications; deadline watchdogs + active polling are the counters | this harness, field-measured 4 incidents | fleet-doctrine.md |
| Engine-emitted `work-complete.txt` sentinel is DEAD: the file is part of the eval TASK (customer deliverable), not the workflow; the journal already is the unfakeable completion record; engine writing it would do the agent's task step for it | kills the engine-writes-the-sentinel variant; does NOT kill engine-side enforcement generally (interceptor, ordering, hooks live on in x1) | cycle-1 q&a with human, 2026-07-12; verified against task.md + run_skill_eval.py COMPLETION_ARTIFACT |
| Project-local hooks FIRE for headless `claude -p` (live-probed: SessionStart, UserPromptSubmit, PreToolUse, Stop, SessionEnd) and for Agent-tool subagents (SubagentStart/PreToolUse-tagged/SubagentStop; subagent shares parent session_id, gets NO separate SessionStart). Stop CAN block a turn-end and force action on its reason — live-proven, headless included | tested on this box, current CLI; NOT live-tested: SessionStart source=compact/resume, PreCompact (docs-cited only), SubagentStop block path | x2, evidence/x2-hooks-research.md |
| Designer B's sharp dependency ("hooks may not fire in the eval's headless mode") RESOLVED IN FAVOR — the hook channel is eval-visible | follows from x2 row above; compact-source re-injection still carries a docs-only residual | x2 + x1-designer-b §4 |
| The three channels cover DISJOINT decision points: A (response text) owns step-entry/check-failure/near-terminal; B (hooks) owns turn-end/post-compaction; C (conductor) owns loop/terminal-ordering structurally. Each designer independently conceded the others' territory | per the three self-assessments; not yet measured behaviorally | x1 panel, cycle-1 consolidation |
| Rail tone: flat imperative + exact next move at the decision point, one plain consequence clause, lightweight structural marker — NO caps/exclamatory. Placement is the best-evidenced lever; all-caps is practice-without-evidence and a variance risk on small models (most format-sensitive, 8–10pt swings from formatting alone) | literature is single-turn QA, not workflow compliance — transfer is inference; no sonnet-class study exists; falsifiable caps-vs-flat prediction recorded for an optional eval arm | x3, evidence/x3-tone-research.md |
| HUMAN-RATIFIED 2026-07-12: flat tone for rails ("flat tone is cool") | rail strings; does not govern exploration-stance prose | human, cycle-1 |
| S2 RESOLVED (human: "dig it") — two registers for two jobs: (1) enforcement half of morale doctrine lives as the engine rail strings (flat, at decision points, single string table); prose elaboration = upgraded scoped-nulls section in global-everyone.md, skills carry one-line pointers-with-force; NO new morale file. (2) Disposition half: exploration-facing doctrine (explorer/prototyper/shotgun framing) deliberately uses a warm joyful-optimistic register — weakly evidenced (EmotionPrompt gains largest on generative tasks) but near-zero cost, and explicitly ALSO justified by human experience/maintainability ("doctrine that's pleasant to inhabit gets maintained") | register split is a design decision, not a measured result; the warm-register claim is the weakest-evidenced item in the stack and is knowingly accepted | human + x3, cycle-1 |

## Open threads

(Resolved this cycle: response format → x1 panel + A+B ruling; sentinel → dead; compaction delivery →
SessionStart hook, x2-proven modes; morale home → rail strings + scoped-nulls section; #134 → small
staging fix in-pass; proportionality → strand killed. C → issue #139.)

- Live-probe the SessionStart source=compact trigger specifically (docs-cited only) — ride implementation.
- #134 staging fix: exact shape of the fencing-aware change to the feedback/archive gate conditions —
  design detail for the spec.
- Measurement execution detail: 3 parallel arms (corpus-only / +rail / +rail+hooks) × which eval
  scenario(s); run counts per the #136 methodology comment; hooked-sandbox install for the +hooks arm.
- S1 pointer-with-force sentence: final wording of the one-line pointer stamped into the nine skills
  (flat register, imperative-carrying).
- Warm-register pass over exploration-facing doctrine (explorer/prototyper): where exactly, and keeping
  it out of rails/gates.

## Cycle-1 human rulings (2026-07-12, verbatim-critical)

- **Channel pick RATIFIED: layered A+B** (engine rail strings + hook suite) for this pass ("agree with a&b").
- **Conductor C: spawn a dedicated exploration issue**, including notes on exploring pi.dev and swapping
  the engine to TypeScript (human direction).
- **S4 proportionality KILLED**: "let's get rid of proportional response. if you don't want the framework,
  don't use constellation. this already mirrors my actual usage anyways." Supersedes the earlier
  "okay going quicker for trivial things" musing from the #126 arc — the framework's full process IS the
  product; opting out is not using it, not a lighter mode of it.
- **#134: do the small fencing-aware staging fix in this pass** — do not wait for C.
- Loose ends ride implementation: live-probe the compact-trigger hook; C thinking preserved via the issue.

## Rejected ideas (with reasons)

- All-caps banner resurrection — review judged the banner removals correct; force comes from placement
  and imperative wording, not volume. Now also research-backed (x3): caps is practice-without-evidence
  and a variance risk on small models. (Would revive only if the falsifiable caps-vs-flat prediction is
  beaten on our own eval.)
- **S4 proportionality (whole strand)** — human ruling 2026-07-12: "if you don't want the framework,
  don't use constellation"; the full process is the product and this mirrors actual usage. (Would revive
  only by explicit human reversal; note the rail's distance-to-terminal already makes the process feel
  cheaper without changing it.)
- Skill-chain delivery of morale doctrine (REQUIRED SUB-SKILL shape) — human ruled "use the engine to
  remind the agent as a process" instead; also competitor-shaped. (Standing human decision.)
- Prevention machinery for re-accretion — standing human stance: consolidation yes, prevention gates no.

## Excursion briefs

### x1 (cycle 1, rev 2) — Design-it-twice: how the engine reaches the agent

Rev 2 (2026-07-12, human-ratified): question widened from "what do engine responses say" to "how does
the engine reach the agent at each decision point"; the engine-emitted-sentinel idea was killed in
session (see Verdicts) and candidate constraints re-cut around delivery channels.

- **The one named question:** How does the engine reach the agent at each decision point — step entry,
  check-FAILURE, turn-end, post-compaction, terminal release — so a cheap model finishes honestly?
- **Type:** design-it-twice. Why: load-bearing interface (every skill and every eval rides on it);
  #138 mandates design-it-twice on it.
- **Panel:** 3 (load-bearing + architecture-touching → panel; human may overturn):
  - **A — minimal-interface:** engine response text only; no hooks, no new verbs, no schema change.
  - **B — hook-carried:** Claude Code hooks only (SessionStart-on-compact re-injection; Stop-hook
    turn-end refusal with escape hatch); engine responses unchanged.
  - **C — conductor inversion:** the engine owns the loop and spawns step-scoped agents; must confront
    cold-start economics (23 of 29 min measured) and scope where the inversion applies.
- **Compared on:** depth / locality / seam placement / testability, plus a failure-shade coverage
  table (prevent / deter / doctrine) per candidate.
- **What "answered" looks like:** one defended recommendation or named hybrid, concrete payloads per
  decision point, eval-check implications stated.
- **Budget / stop:** design docs only — NO code changes (engine fenced during design); ≤30 min each;
  report partial rather than overrun. Scoped nulls apply.
- Handoffs: `crew-handoffs/x1-shared-core.md` + `x1-designer-{a,b,c}.md`. Results:
  `evidence/x1-designer-{a,b,c}.md`.

### x2 (cycle 1) — Research: do hooks fire for subagents and headless runs?

- **The one named question:** Do project-local Claude Code hooks fire for Agent-tool subagents and
  headless `claude -p` runs, and which events (SessionStart w/ compact source, Stop w/ blocking,
  PreCompact) exist with what powers?
- **Type:** research (docs + cheap empirical probe in a temp dir; repo untouched). Why: designer B's
  channel and the compaction re-injection thread depend on it.
- **What "answered" looks like:** one row per (hook event × invocation mode), each claim cited to a
  doc section or pasted probe log; not-tested combinations stated.
- **Budget / stop:** ≤25 min, partial over overrun; scoped nulls.
- Handoff: `crew-handoffs/x2-hooks-research.md`. Result: `evidence/x2-hooks-research.md`.

## Cycle log

## Cycle-1 consolidation — the design-it-twice comparison (x1) + hooks facts (x2)

**The comparison (axis-by-axis, from the three docs at `evidence/x1-designer-{a,b,c}.md`):**

| Axis | A response-text | B hook-carried | C conductor |
|---|---|---|---|
| Depth | broad reach, deterrent-only | prevents 3 worst shades at turn boundary; can't judge work quality | 5 of 7 shades PREVENTED structurally |
| Locality | best — one `_rail()` fn in the engine | one hook script + settings.json; re-encodes "what is terminal" in a 2nd place | new top-level component + `bands:` template coupling |
| Seam | rides the existing mandatory chokepoint; silent at turn-end/compaction | harness boundary, ONE adapter (Claude-Code-only portability) | reuses run_skill_eval's proven reap-safe seam |
| Testability | substring unit tests; behavior only via sonnet eval | unit-testable logic; end-to-end only on real harness | loop is pure/unit-testable; e2e via eval |
| Cost | ~zero | small script; portability debt | +~3 min wall-clock, new complexity locus, interactive UX degrades |
| #134 | wording only, can't fix | CANNOT fix (engine-verbs out of channel) | fixes it structurally (conductor owns staging) |

**Defended recommendation (convergence remains the human's): a LAYERED A+B hybrid for this pass, C
recorded as a shaped future direction.** Reasoning: the panel revealed the channels are complementary,
not competing — each conceded the others' decision points. The failure timeline has three moments:
getting IN (skill-text entry ritual — no channel reaches an agent before its first engine call; clamp
restoration strand S1 stays necessary), staying ON (A's rail at every engine response), and not
LEAVING (B's Stop-hook refusal + SessionStart-compact re-injection — x2 proved this fires in the
eval's own headless mode, so it is measurable now). A+B together cover every decision point that
doesn't require owning the loop, cost ~one function + ~150 hook lines, keep every existing provenance
check unchanged, and are immediately measurable with the #129 harness in per-channel arms (corpus-only
/ +rail / +rail+hooks, run in parallel). C is the deepest design (5/7 shades prevented by structure,
#134 solved as a side effect) but brings a new control component, template coupling, and an
interactive-UX cost — too big to ride along this pass without its own design cycle; its band model and
ledger schema are the named open threads if pursued.

**Overlap note:** A's turn-end/wait-loop wording becomes redundant where B's Stop hook fires —
harmless defense-in-depth (and load-bearing on any harness without hooks).

**#134 disposition within the pass:** neither A nor B fixes it; do NOT wait for C. Either a small
fencing-aware staging change to the feedback/archive gate conditions (engine, small) or C-later. Open
thread for the spec.

## Cycle log

| Cycle | Flavor | Explored | Consolidation |
|---|---|---|---|
| 1 | compare | Engine→agent delivery channels: 3-designer panel (response-text / hooks / conductor) + hooks-capability research | Channels are complementary; recommendation = layered A+B this pass, C shelved-shaped for a future arc; sentinel idea killed; hooks live-proven headless. Human convergence pending. |
