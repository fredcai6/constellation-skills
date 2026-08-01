# Plan — issue #102 (Cluster A)

## Mission frame (lean — skill-source repo, no packet map)

The map adds little here: these are mechanical doctrine relocations whose safety was
established by the epic's c2-x2 verification. No `docs/architecture` packet map exists;
the structural record that matters is (a) the `_shared/` bucket files and their bundling
in `install_constellation.py:SKILL_REFERENCE_BUNDLES`, and (b) the test glob that pins
bundle composition. Frame kept lean per the commander doctrine's trivial-change allowance.

- **Intent:** eliminate duplication-with-drift so doctrine lives once and patches once;
  primary beneficiary is agents loading these skills. Token win comes from deletions
  (banners) + relocations, honestly measured by before/after word counts.
- **Affected capabilities:** every role's SKILL.md (the product); `_shared` buckets;
  the installer's bundle mechanism; the test suite (structural-only today).
- **Structural anchors:** `global-everyone.md` (all skills), `global-orchestrator.md`
  (orchestrator tier only), `design-it-twice-brief.md` (orchestrator bundle);
  install_constellation.py:94-113; test_install_constellation.py:196-208 (glob),
  :679-690 (the one content-pin model).
- **Governing constraints:** append into existing bucket files only (never a new
  `global-*.md`); reconcile-then-cut every move; each carrier keeps a pointer naming the
  shared file; keep the 36-test suite green at every gate boundary.
- **Decision anchors:** cross-tier rules → global-everyone; orchestrator-only → global-
  orchestrator; banners → deleted; sibling-ids single home = lessons-auditor.
- **Out of scope (fenced):** manifest.json, repo-root stray file, docs/ROADMAP.md, typos
  outside carriers (issue #105 owns hygiene); anything beyond the 10 moves + net.
- **Map confidence:** high — carriers grep-confirmed at understand; one delta logged
  (banners = 6, not "charter twice").

## Design-it-twice — the gate decomposition (plan-phase)

The MOVES themselves are design-it-twice-skipped by the issue (trivial mechanical
relocations, safety pre-verified). The remaining live plan decision is **how to gate 10
moves that share carriers** (commander/SKILL.md recurs in 6 moves; admiral/SKILL.md in 4).
Two candidates under distinct constraints; converge to one. Panel-vs-single: **single-
pair**, because fairly-easy — sequential crews mean no real worktree collision risk, so the
decomposition is a bite-size/reviewability tradeoff, not architecture. Surfaced, overridable.

- **Candidate A — one gate per move (10 + net = 11 gates), constraint: smallest-bite /
  max per-move isolation.** Each move gets its own implement/review/integrate with its own
  grep evidence. Pro: cleanest per-move return shape, focused reviews. Con: 22 crew
  dispatches — exceeds a single session window; many gates touch the same 2 files
  sequentially anyway, so isolation buys little over grouping.
- **Candidate B — group by destination + nature (7 gates), constraint: fewest-gates that
  keeps reviews focused and the suite green at each boundary.** g1 boilerplate, g2 engine-
  string, g3 banners, g4 three cross-tier→everyone rules, g5 two→orchestrator rules,
  g6 two single-home relocations, g7 regression net. Pro: fits the window; each gate is a
  coherent reconcile unit; per-move grep evidence still carried inside each gate. Con: a
  grouped gate bundles 2-3 moves, so its review must check each sub-move.

**Convergence → Candidate B.** Depth: B's gates are coherent reconcile units (one
destination bucket or one nature per gate). Locality: B groups by the file(s) actually
touched, so a gate owns its carriers cleanly. Testability: identical — both carry per-move
before/after grep evidence and the same g7 net. Seam placement: B draws gate boundaries at
destination buckets, matching how the installer bundles. A's only edge (per-move isolation)
is neutralized because crews run sequentially. **Hybrid taken:** keep A's per-move grep-
evidence granularity INSIDE B's grouped gates — every move still gets its own before/after
carrier-count pair in the gate evidence, so the per-move return table is preserved.

- **Untaken road:** Candidate A (one-gate-per-move) — skipped as not worth the doubled
  dispatch count given sequential crews neutralize its isolation benefit. Named here.

## Gate plan (execute.json) — 7 gates

| Gate | Moves | Destination | Notes |
|---|---|---|---|
| g1 | 1 mandatory-compliance boilerplate | global-everyone | ~10-file fan-out; own gate |
| g2 | 2 engine-invocation string | global-everyone | ~10-file drift; own gate |
| g3 | 3 banner deletion | (deleted) | 6 banners; mechanical |
| g4 | 4 scoped-nulls, 5 world-verification, 8 delegate-not-replacement | global-everyone | three cross-tier 2-carrier rules |
| g5 | 6 unchanged-tree, 7 crew-idle | global-orchestrator | commander+admiral(+fleet-doctrine) |
| g6 | 9 dedup-sibling-ids, 10 design-it-twice restatements | lessons-auditor / pointers | single-home + pointer-cut |
| g7 | 11 regression net | tests | content-pins (moves 1,2,4,5,6,7,8,9) + no-residual + word counts |

Ordering: g1-g6 (prose edits + pointers, no new global-* filename) keep the 36-test suite
structurally green at each boundary; g7 adds content-pin + residual tests LAST, when every
inline copy is already cut and all bucket content present → first run is green (no known-red
window, no waiver detour).

Each crew gate: gN-implement (fill IMPLEMENTER_HANDOFF, dispatch), gN-review (fill
REVIEWER_HANDOFF, dispatch), gN-integrate (verify suite green + per-move grep evidence).
Move-4 partial: prototyper spike-domain applications (measurement.md/ui.md) stay local;
only the general principle moves — handoff states this so a full cut isn't mistaken for the goal.
