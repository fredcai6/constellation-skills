# Cold plan critic — panel of 2, every finding dispositioned

Panel-vs-single: **panel (2 lenses)**, scaled by weight — this plan changes a load-bearing interface
(the binding key). The third standard lens, simplicity/YAGNI, is a **named untaken road**: it was
already run as the design-it-twice axis itself (candidate A "minimum diff" vs candidate B "seam-first"),
adjudicated below, so a third critic re-arguing it would re-litigate a decision already made on evidence.

Critics read the problem statement, the mission frame and the candidate `execute.json` only. Neither was
given authoring context. Dispositions are the Commander's, citing `LAUNCH_ORDER:Inherited Latitude`;
none was self-triaged by a critic.

## Design-it-twice convergence (recorded before the critics ran)

Two candidates were authored in parallel under distinct constraints: **A = minimum diff** (no new module,
edit the two hooks in place) and **B = seam-first** (a new pure `scripts/hooks/agent_scope.py` with an
injected existence predicate and five named callers).

**Converged on A, with four grafts from B.** The deciding fact is the probe's: identity arrives in the
payload, so the "which agent am I" question is a dictionary lookup, not a search. B's own text concedes
the point — *"Under a minimum-diff constraint this alternative wins outright."* A already gets the
one-place property B's seam was built to buy, because `binding_key()` is the sole composer and the gauge
writer calls it through the module handle it already loads. B additionally needs an installer-companion
gate that A does not. The launch order's mandatory scope ruling — *do what we need to do and no more* —
points the same way.

Grafted from B: (1) pin the real captured payloads as a sha256-pinned test fixture, so the unit layer
argues with real harness output instead of typed dicts; (2) reject a non-token `agent_id` before it is
interpolated into a filesystem path; (3) B's enumeration of checks-that-cannot-fail, used as the
reviewer's brief; (4) two subagents consuming deliberately different amounts, so a parent-fallback world
fails by construction.

## Findings and dispositions

| # | Lens | Finding | Disposition |
|---|---|---|---|
| 1 | intent | `binding_key` falling back to the **bare** key on a present-but-malformed `agent_id` contradicts done-condition 3 and would push the parent's key to 2 entries, silencing the *parent's* gauge — the fix's error path causing the very blindness it removes | **EDIT.** `binding_key` returns `None` for present-but-malformed `agent_id`; the caller writes no binding at all. New g1 postcondition asserts it. Absent `agent_id` still means bare key — that is a top-level agent, not an unresolved one |
| 2 | test | Every `command` postcondition in the plan is **already green at HEAD with zero code written** — they are re-runs of the baseline dressed as verification | **EDIT.** Each integrate command now names the new test classes by node id, so it fails on a tree where they were never written. g6 states the expected count delta instead of an unusable bare 1621 |
| 3 | test | g4's evidence **passes on a swap** — A's reading written to B's spine satisfies every listed assertion, and swap is exactly the misattribution class this issue exists to kill | **EDIT.** g4 now asserts the *pairing*: for each agent, the fill recomputed from `agent-<id>.jsonl` must equal the `gauge.json` in the spine directory that same id's binding key points at. Count stated: 2 of 2 |
| 4 | intent | g4-integrate c2's "the parent's binding did not accumulate" is vacuous — the run shape never has the parent claim anything, so it is 0 == 0 | **EDIT.** The parent claims its own spine in the treatment arm; assert the bare key holds exactly its one entry and the parent's own gauge is written (pre-fix it would not be) |
| 5 | test | g5's exact-diff check is already falsified: the live store drifted 54 → 59 entries between plan time and the critic's read, and `_save_json_map` has **no lock**, so the sweeper races five live sibling runs | **EDIT.** c2 compares only the DROP set and tolerates concurrent additions; the sweep re-reads and verifies the file is unchanged immediately before writing (compare-and-swap); the sibling sessions' keys are named and asserted present in the after-state |
| 6 | intent | g5 is the only irreversible gate and the only one with no independent review | **EDIT, mechanically rather than by crew** — putting a crew inside the main checkout's live shared state is the larger risk. The KEEP/DROP predicate is re-evaluated at real-run time (not trusted from plan time), and the survival of every active-lease entry is asserted as its own postcondition |
| 7 | test | The `isSidechain`-truthy conjunct is **unfalsifiable** against the named fixture: all 4 of its lines are truthy with the same `agentId`, so agentId-equality alone passes every stated assertion | **EDIT.** A derived fixture line carries the matching `agentId` with `isSidechain` falsy and must be skipped. Line counts stated |
| 8 | test | `binding_key`'s rejection branch has **no coverage**, and "real payloads only" forbids the test that would give it any. The real set contains zero malformed ids | **EDIT.** Adversarial rows are explicitly *derived by mutating the pinned real payloads*; this is not the forbidden injection — it proves rejection, not delivery. Row counts stated: 6 real + at least 6 adversarial |
| 9 | test | The pinned payload file's lines are **wrappers** — the real payload is nested under `payload` — which g1's "copy byte-identically" instruction does not say | **EDIT.** Stated in g1's imperative. A cheap correction that would otherwise have cost a rework round-trip |
| 10 | intent+test | g4-integrate c1 — the postcondition that **is** the issue — has no `override_policy`, so the SOFT-only partial discharge the plan itself predicts has no sanctioned exit but Commander assertion | **EDIT.** c1 gains an `override_policy` with `authority: admiral`; the SOFT branch is stated explicitly as a float, never a quiet pass |
| 11 | intent | A subagent that never claims a spine becomes **fully invisible** after this change, where today it produces a (misattributed) reading. A real coverage loss, nowhere named | **EDIT.** Named in the g3 doc edit beside the surviving-orchestrator residual, and one non-claiming subagent is dispatched in g4 so it is observed rather than assumed |
| 12 | intent | The probe only captured `spawnDepth 1`, but 52 real depth-2 agents exist in this project. If a nested agent's payload names its *parent agent's* transcript, the derivation yields a path that never exists — permanent silent fail-closed | **EDIT.** One nested dispatch added to the g4 run. If it fails closed, that is a recorded measured negative and a triage candidate, not a blocker |
| 13 | test | g4's two constraints contradict: "nothing may contain the string `agent_id`" forbids the constructed payload the "feed an unresolvable identity" negative control requires | **EDIT.** The prohibition is scoped to the **acceptance path**; the unresolvable-identity control is a unit test in g2, where constructing a payload is legitimate |
| 14 | test | The `agent_id` grep is a can-this-fail sweep: undefined scope (the hook source it wires *must* contain the string), no count, and blind to injection by pre-seeded binding file, hand-made transcript, or env var | **EDIT.** Restated as *corroborating*, with an exact command, a stated file count, and the assertions it cannot make added: the sandbox binding file and `subagents/` directory are both empty before the run |
| 15 | test | `decision:union-read-preserves-stop-rail` settles itself against a **bare-key-only store**, where the merge is the identity function — it passes in the world where the union read does nothing | **EDIT.** The settle now uses a store with one bare and two composite keys, and asserts `decide_stop` blocks on a spine held only under a composite key. Entry count stated |
| 16 | intent | g2's identity-duration field traces to none of the six done-conditions, so g6's own rule obliges deleting it | **REJECT the deletion, EDIT the trace.** It is not creep: the issue names it in its own words ("Identity resolution records its own duration in the gauge write, per-call budget 100ms"). It is now anchored to that bullet so g6's trace resolves, and g4 asserts the recorded duration is inside budget on the live run — closing the separate finding that nothing ever read it |
| 17 | test | Named-but-untested failure modes: the nudge-ledger asymmetry, the bind-on-resume write staying bare, and the empty-set cleanup deleting the composite key rather than the bare one (the single line where a wrong substitution deletes a live parent's whole binding) | **EDIT.** All three become explicit evidence anchors on g1 |
| 18 | test | Moving the `binding_key` call out of `resolve_gauge_path` strands the existing `_spine_rail is None` guard, so a sibling-import failure would raise into the outer swallow and the governor goes silent with no diagnostic | **EDIT.** g2's constraints now say where the guard goes |
| 19 | intent | g3's imperative forbids a grep proxy while g3's postconditions require one | **EDIT.** Resolved explicitly: grep to *enumerate*, judgement to *adjudicate*, with the occurrence count archived, plus a full read of the two named sections — because a sentence can assert the old polarity without using any of the swept words |
| 20 | intent+test | Per-agent keying multiplies key cardinality, an abandoned agent's key is never removed, `_save_json_map` has no lock, and this run deletes the only sweeper | **TRIAGE, not fixed here.** Out of the issue's stated scope, and the issue itself mandates deleting the sweeper. Filed as a triage candidate; the abandonment case gets a comment at the code site per the scope ruling |

Nothing was rejected as noise. One finding (16) was rejected on its recommendation and accepted on its
underlying gap; the rest were edits.
