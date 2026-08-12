# Cold plan critic — panel of 2, findings and disposition

Both critics read `execute.json` and `MISSION_FRAME.md` only, and were explicitly forbidden the
launch order, `notes-1.md`, the alternatives brief, the convergence record, and `spine.json`. Both
were permitted to read repository source, which is what made their strongest findings measurements
rather than opinions.

**Panel-vs-single: a panel of 2, surfaced for the approver to overturn.** Rationale: this plan gates
the epic's own close, and the two lenses are genuinely different — one on the epic's own subject
(a check that cannot fail), one on scope, sequencing and completeness. The scaling call cost two
parallel reads and it was worth it: the block came from the first lens and the correction of a false
plan claim came from the second, and neither found the other's headline.

**Verdicts: critic 1 BLOCK (narrowly, on two gates). Critic 2 APPROVE-WITH-FINDINGS (nine).**

## Accepted and fixed in the plan

| # | Finding | Disposition |
|---|---|---|
| C1-F1 | **g1-integrate.c1 was a check that cannot fail.** The critic replaced the guard with an unconditionally-permissive version — the exact thing g1-review says must go red — and the closing command still exited 0, 12 passed. No test in the file touches the guard, and the runtime tests all invoke the verifier from an installed tempdir bundle where the guard never refuses. | **Fixed.** Every gate now closes on a `-k` selector keyed to a test naming contract stated in its own implement imperative. A zero-match selector exits 5, so a gate whose tests were never written fails closed. I re-measured this myself rather than taking it on report: `guard_location`, `stop_mutation` and `archive_c2b` each exit **5** on the current tree. |
| C1-F2 | **g3-integrate.c1 the same, and worse** — fix C touches no Python, nothing in the suite reads `archive.c2b`'s text (the one near-hit skips it because it asserts only on commands containing a `.py` token), and `<branch>` is not a resolver-owned token so instantiation cannot catch it either. A byte-identical template would have closed the gate. | **Fixed** by the same device, plus an explicit instruction to extract the command text *from* the template rather than restate it. |
| C2-F2 | **#501's second Acceptance criterion had no gate.** It asks for a mutation test pointing the resolver at a wrong root; g1 had none. | **Fixed.** `g1-integrate.c2` is a mutation floor with `allowed: false`. This is my own tightening — the launch order marks only fix A's floor non-overridable — and it is inside inherited latitude ("you may add tests"). |
| C1-F6 / C2-F5 | **g2's precondition asserted a technical dependency that does not exist.** Both critics measured it false independently: g2's pytest verification reaches the verifier through a tempdir bundle where the guard passes today, unfixed. | **Fixed, and the claim was mine.** `p1` now states the honest basis — same-file edit serialization and reviewer locality — and names the one place the dependency *is* real (`g4-integrate.c2`, which invokes the repo copy directly). My convergence record made this claim on the strength of overruling `best-seam`'s own "editorial, not technical" note; `best-seam` was right and I was wrong. |
| C1-F3 | **The non-overridable floor could be made unpassable by correct work.** `-k mutation` fails closed on zero matches (good), but nothing told the implementer the test's name must contain `mutation` — so a correctly-written test named otherwise yields exit 5 on a condition where waiver is shut by design, forcing an amend against the human's authority. | **Fixed.** The naming contract is stated in each implement imperative and flagged load-bearing. Selectors are distinct per gate (`guard_*`, `stop_*`, `archive_*`) so no gate's floor can be satisfied by a sibling's test. |
| C1-F7 | **g4-integrate.c2 was judged by the machine's installed corpus**, not the branch under review — identical today, so honest by accident, but it would go green or red on machine state invisible to a PR reviewer. | **Fixed.** c2 now passes `--skills-root` explicitly. Note this makes the new flag load-bearing, which is now stated in g1-implement. |
| C1-F8 / C2-F8 | **g4-integrate.c2's imperative forbade a waiver its own `override_policy` permitted.** | **Fixed by resolving toward the policy, not the prose.** c2 stays waivable so an environment fault cannot hard-block the run, and the imperative now says a waiver here is a float to the Admiral carrying the finding, never a local decision. Making it non-waivable was the other option; it was declined because the condition depends on machine state and an unpassable check is the defect this whole run is about. |
| C2-F1 | **A relayed evidence anchor was wrong about polarity.** The main checkout is a *wrong-accept* at the guard (which then fails downstream naming the wrong problem); the *worktree* is the outright refusal. My anchor implied the refusal was the main-checkout defect, and it is relayed to the reviewer via `inherits`. | **Fixed.** The anchor now states both polarities explicitly and marks which one is in the issues and which is this run's own finding. |
| C2-F3 | **Collateral red in a non-owned file that is not `checklist_engine.py` had no route out** — g4 could not edit it, had no float instruction for it, and could not go green, leaving only the waiver the frame condemns. | **Fixed.** The float rule is generalized to any non-owned file, in every gate's constraints. |
| C2-F4 | **A red window across three gate boundaries** — the full suite first appeared at g4. The critic conceded the coupling is empirically thin but noted the plan asserted that rather than knowing it. | **Fixed, cheaply.** Each of g1/g2/g3-integrate gains a **coupled-suite** condition over the eight test files that consume the spine template, the installer, or the work-area resolver. Measured: **44s**, against **947s** for the full suite, which stays at g4. The critic's proposal was the full suite on every gate; that would have cost about 48 minutes of re-evaluation across the run for the same information. |
| C2-F6 | **"Exercise the resolved command text" had no mechanism** — no test in this repo invokes `gh`, and the verifier is explicitly network-free. | **Fixed.** The mechanism is named: a stub `gh` early on PATH, asserting on the exit code through the same POSIX shell the engine uses. An honest-null clause is added for the case where it cannot be done without real network. |
| C2-F7 | **An existing negative assertion must be inverted** (`tests/test_iterative_planning_doctrine.py:461-462`, "stop cannot authorize NEXT_WAVE") and the plan never said so — which under pre-ruling 6 is exactly the kind of edit that must be authorized on the face of the plan rather than discovered. | **Fixed.** Named with its line in g2-implement, with the reason it is the fix rather than a check bent to pass, and added to g2-review's required confirmations. |
| C2-F9 | **No gate emitted the triage candidates the plan promised.** | **Fixed.** g4-integrate's imperative routes all three deferrals to the spine's triage step by name. |
| C1-F5 | Every close criterion's real meaning lived in discarded stdout. | **Addressed by the selector fix** — the claim now rides in the `cmd` field the engine does record. |
| C1-F4 | Three gates closed on a byte-identical command, so two of the three closes proved nothing new. | **Addressed by the selector fix.** |

## Accepted as true, recorded, not fixed here

- **C1-F9 — `implementer-result` conditions carry no `match`,** so an IMPLEMENTER_RESULT recording
  BLOCKED would satisfy them. This is verbatim the shipped `EXECUTE_PLAN.template.json:21`. It is a
  corpus-level defect, not this plan's invention, and the template is not this run's file.
  **→ triage candidate.**
- **C2's aside — `config_ref` points at `docs/agents/engine-config.json`, which does not exist**
  anywhere in the repo; `load_config` falls back to `{}` silently and nobody is told. Also inherited
  from the shipped template. **→ triage candidate.**
- **C2-F9's sharpest sub-point — after fix A, `ADMIRAL_SPINE.template.json`'s execute prose and its
  `directives.decisions` block will still describe `repair` as an enforced exit.** That template is
  explicitly not this run's file. **→ triage candidate**, routed at g4-integrate.

## Corrections to my own prior claims

Two things I asserted are now on the record as wrong, both caught by measurement:

1. **g2's precondition was not a technical dependency** (C1-F6 / C2-F5). I overruled the
   `best-seam` candidate's own honest note to claim it was. It was right.
2. **The g1 evidence anchor described the wrong failure polarity** for the main checkout (C2-F1).

Neither changes the gate decomposition; both changed what the gates tell their crews.

## What the critics checked and found sound

Recorded so coverage can be told from silence. Both confirmed independently: the `<branch>`
input-redirection diagnosis; that `<branch>` is genuinely outside the resolver's owned-token set and
`<repo-root>` is a real existing token; that two clauses block a `stop` packet, not one (with a third
`_require` at :144 that needs no change); that the stdout-discard and POSIX-shell claims hold against
`docs/CHECKLIST_SCHEMA.md`; that `test "$(…)" -gt 0` carries its verdict in the exit code and that
#484's suggested replacement does not; that the structural predicate actually resolves the main
checkout correctly on this machine; that all six issues map to a gate with no orphan; that every file
in the ownership scope has a gate or an explicit exclusion; and that `anchors` is a real engine field
surfaced on the active gate, not decoration.
