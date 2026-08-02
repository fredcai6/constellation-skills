# AGENT_FEEDBACK (staged)

Run retrospective for work-id **667-join** (epic #659 Wave 4a — "the join"). Staged per the
launch-order fence; the Admiral harvests into the shared `.agent-work/AGENT_FEEDBACK.md`.

## 2026-07-26 — 667-join (cmdr-667, delegated)

**What went well**
- The launch order + DESIGN_SPEC §4/T7 were complete and binding. The one load-bearing ambiguity
  (does the join normalize the weights?) was FORCED by the spec's own T7-1 invariant (uniform ⇒
  exactly the driver-overall mean is an identity only under a normalized weighted average) — resolved
  to a settled/inherited decision, not a float.
- Both crews delivered synchronously foreground, zero idle-yields, zero Admiral nudges. The 4 T7
  invariants + T7-5 + honest quadrature σ all pass (18/18), independently reviewer-reproduced.

**Instruction adherence**
- All artifact-check postconditions satisfied via `attach` (never `attest`) — user-decision at
  understand/plan/triage/review; implementer-result/review-result at gN-implement/gN-review, and
  review-result re-attached at gN-integrate for the APPROVE-match. `attest --which` for null
  conditions; `advance` (not attest) for command postconditions.
- All 4 crew dispatches via `run_crew.py --backend external` + Agent-tool subagent, `recover_crews.py`
  before each, `--verify-result` confirming freshness. No headless claude CLI in this harness.
- execute.json (gated) driven to DONE, then plain `attest execute --cond c1` on the spine (NO
  --from-child). Feedback trio staged per the fence; nothing shared committed on the branch.

**Friction / unclear**
- Self-authored g1-integrate c3 `simplification_limits` command was malformed (bare positionals; needs
  `--paths`; the `-m` form hits the editable-.pth worktree trap) — caught by the reviewer, fixed via
  engine `amend --retext-check` on the still-pending gate (not a hand-edit, not a waive).
- Bounded-slice scope gap: launch order named 4 circuits but only Great Britain is on disk (#666
  fp_slice swept at closeout; #664 ran GB-only). Floated twice; finalized on path A (GB-real +
  synthetic) within latitude, harness left season-ready for the other 3.
- Real-data thin path nuance: at as_of_round=12 GB's c1 is thin-but-RESOLVED (weight_on_thin=0, a
  measured outcome); fully-thin demonstrated at as_of_round=9; the partial-unresolved path is covered
  by the g1 synthetic thin-widening test (GB is a single round — no clean intermediate cutoff).
- The staged AGENT_FEEDBACK format is picky: the entry must be ONE `## ` block (inner `## ` headings
  truncate it) and the signal sections must be `**bold**` labels, not `###` — cost two retries.

**Crew-reported friction**
- g1 implementer flagged the handoff's `-m src.utils.simplification_limits` verification command as
  wrong (bare positionals + editable-.pth `-m` trap) and used the `--paths` file-invocation instead;
  also a minor "no store import" vs "consume FingerprintCell from store" tension (resolved: value-object
  type import only, no DB opened). Folded the corrected command into the g1-review handoff.
- g2 implementer surfaced a load-bearing structural fact NOT in the handoff: `reference_laps.map_version`
  is per-circuit, so the fit pools season-wide (`map_version=None`) and only composition is per-circuit —
  confirmed sound by the g2 reviewer; recorded in the map delta.
- g2 reviewer flagged that `.agent-work/` is not broadly gitignored here, so the emitted JSON summary
  isn't auto-ignored — left unstaged (staged deliverables explicitly, never `git add -A`).

**Improvement signals**
- The cold plan critic earned its cost: caught a genuine σ-propagation BLOCKER (unresolved σ capped
  instead of fattening) + forced the T7-5 non-degenerate test, both pre-freeze. Design-it-twice +
  cold critic on a load-bearing interface is worth the round-trip.
- `amend --retext-check` is the clean, sanctioned remedy for a malformed self-authored command
  postcondition on a pending/in-progress gate — worth naming in commander-core so a commander doesn't
  reach for `waive` (wrong tool) or a hand-edit (forbidden).
- The launch order could have flagged that #666's fp_slice is swept at #666 closeout, so a 4-circuit
  validation needs regeneration up front — it would have surfaced the scope float at understand.
