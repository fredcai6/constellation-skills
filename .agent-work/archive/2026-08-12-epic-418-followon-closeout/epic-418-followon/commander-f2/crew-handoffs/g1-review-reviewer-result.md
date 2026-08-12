# Review Result

## Assigned Gate
`g1-review` (issue #542/#541, workstream F2, epic-418-followon, commander-f2)

## Result
`BLOCK`

## Handoff compliance

**Criterion A — the trade document carries all six frozen items.** PASS, verified item by item against `IDENTITY_TRADE.md`:

1. **Option taken, stated plainly** — SS1: "Bind identity to the container, and require every seam to declare the granularity at which its container actually separates."
2. **Property given up, named** — SS2: "An in-session dispatched crew member cannot drive its own plan through the door," with the concrete Commander/Implementer/Reviewer consequence spelled out, not gestured at.
3. **Each rejected option, would-cover / would-not-cover** — SS3: Option A (per-call spine argument) and Option B (caller-supplied identity) both carry explicit "would have covered" / "would NOT have covered" (or "covered: nothing") language.
4. **General shape, stated fleet-wide** — SS4: a two-row table (MCP door / Stop-hook binding) plus a blockquote rule generalizing beyond MCP.
5. **Hook seam addressed, and why** — SS5: "Yes, and it is the case that makes the general form necessary rather than decorative," naming the `session_view()` merge defect mechanism.
6. **No-per-call-argument answer** — SS6: "The door has a fallback; the hook does not... fails closed," stated as the uniform answer for both seams.

All six present and load-bearing.

**Criterion B — the pin can lose.** PARTIAL. Reproduced independently by mutating the real `scripts/mcp_spine_server.py` (never a copy), restoring via `git checkout --`, and confirming `git diff HEAD~1 -- scripts/` back to 0 lines after every mutation.

| # | Mutation | Result | Restore confirmed |
|---|---|---|---|
| Baseline | none | `python -m pytest -q tests/test_mcp_identity.py::IdentityBindingPinTests` → **5 passed** | — |
| 1 | Add `spine_file` to `spine_status`'s `inputSchema.properties` | **RED**: `IdentityBindingPinTests::test_no_tool_accepts_an_argument_that_could_redirect_the_door` (matches Commander's claim) | `git diff --stat` empty; 5 passed |
| 2 | `SPINE` late-bound via module-level `__getattr__` (PEP 562) instead of import-time binding | **RED**: `IdentityBindingPinTests::test_identity_is_bound_at_import_and_is_immune_to_later_environment_change` (matches Commander's claim), **plus** a bonus RED on `test_two_doors_bound_to_two_spines_do_not_share_a_binding` (`KeyError: 'SPINE_FILE'`, since env is restored by the time that test's second `module.SPINE` read fires) | `git diff --stat` empty; 5 passed |
| 3 (mine) | `call_tool`'s `spine_status` handler honors an undeclared `spine_override` argument, redirecting the engine call to an arbitrary `--file` path — **never added to any tool's `inputSchema`** | **5 passed. Nothing went red.** | `git diff --stat` empty; 5 passed |

Mutation 3 is the finding the handoff warned would be the most valuable one to surface. `IdentityBindingPinTests` inspects (a) the declared `TOOLS` schema shape and (b) import-time immutability of `module.SPINE`/`module.SESSION` — it never exercises `call_tool`'s actual runtime dispatch. A future change that adds a per-call redirect purely in handler logic, without touching any `inputSchema`, defeats `IDENTITY_TRADE.md`'s own claim ("the door literally cannot be pointed at another run's spine, because there is no argument that would let it... confinement by construction, not by convention") **silently** — exactly the failure mode the pin exists to prevent, and exactly the case that does not go red.

**Criterion C — pin is outcome-neutral.** Holds, with a caveat worth naming. The two pinned properties (no identity-marker tool args; import-time immutability) are, by construction, satisfiable only by Option C among the three named options — Options A and B both add an argument and would trip `test_no_tool_accepts_an_argument_that_could_redirect_the_door`. This is not a hidden decision made in the test: the document's own account is that a deliberate future move to A/B requires editing this test alongside `IDENTITY_TRADE.md`, and `test_the_pin_can_fail` (a positive control) proves the detector genuinely works rather than being vacuously green. Not a defect standing alone — but combined with the Mutation-3 gap, the pin's actual guarantee is narrower than the document's prose claims.

**Criterion D — honest-scope claim holds.** PASS. The new diff hunk (`IdentityBindingPinTests`, lines 665–840) never spawns a subprocess or a Task-tool subagent and never asserts anything about harness-internal MCP client reuse — it only imports the module directly and inspects `TOOLS`/`SPINE`/`SESSION`/file existence. `DC3InheritanceMechanismTests`' pre-existing scope note (untouched by this diff — confirmed via `git diff HEAD~1`, which is a pure 177-line addition with 0 deletions) is the only place in this file that discusses the harness seam, and it is cited, not re-measured, exactly as claimed.

**Criterion E — `git diff HEAD~1 -- scripts/` is empty.** PASS, both before my mutations and after full restore.

## Scope drift
None. `git show 36a1bdcd --stat` confirms `scripts/hooks/spine_rail.py` and `scripts/checklist_engine.py` were untouched by the commit. My own temporary mutations to `scripts/mcp_spine_server.py` were restored via `git checkout --` each time, confirmed via `git diff HEAD~1 -- scripts/` returning to 0 lines. One accidental side effect during this review is disclosed under Workflow Feedback and was reverted before recording any further findings.

## Evidence verdict
The handoff's stated evidence (`python -m pytest -q tests/test_mcp_identity.py::IdentityBindingPinTests` → `5 passed`) reproduces exactly. However, the handoff's **required** evidence — "the full suite green after restore: `python -m pytest -q`, `0 failed`" — does **not** reproduce:

```
python -m pytest -q
...
1 failed, 2271 passed, 1 skipped, 1079 subtests passed in 100.18s
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
```

Root cause verified: commit `36a1bdcd` added `IdentityBindingPinTests` to `tests/test_mcp_identity.py` (that module's own entity count goes from 36 to 45 entities on a fresh `python -m scripts.code_map build`), but `map/INDEX.md` was last regenerated at `c66d2ffa` and `git diff HEAD~1 -- map/INDEX.md` is empty — the map was never rebuilt for this gate. This is mechanical (rerun the map build and commit it) and does not touch the identity decision itself, but it is real, reproducible, and it is the specific evidence the handoff asked me to reproduce.

## Code/doc quality
Fowler pass run (`r6-fowler`, recorded to `.agent-work/epic-418-followon/commander-f2/g1-review/fowler-pass.json`, `scripts/verify_fowler_pass.py` exits 0): 10 of 12 baseline smells absent; 2 overridden with a logged repo-standard + reason (`divergent-change` and `comments-as-deodorant`, both citing this file's own pre-existing DC2/DC3 documentation-density convention as the standard that subordinates the smell). No blocking quality finding.

Handoff constraints checked: `python -m pytest` used exclusively throughout (never `python3`/`py`); no writes introduced in the diff lack `encoding='utf-8'`; the review checklist JSON was driven only through `checklist_engine.py` verbs, never hand-edited.

## Map impact verdict
- **Evidence supports claimed change:** Yes for the identity decision and pin themselves (criteria A, D, E). No for the "full suite green" claim (see Evidence verdict).
- **Constraints not violated:** Yes — allowed scope and specific exclusions were respected by the commit under review.
- **Notes match the diff:** `IDENTITY_TRADE.md`'s claims about what the pin covers slightly overstate what `IdentityBindingPinTests` actually checks (see Criterion B / Mutation 3) — the document's confinement claim is about runtime behavior, the pin only checks declared schema + import-time binding.
- **Decision candidates surfaced:** N/A — this gate correctly stayed within the Commander's delegated authority; I am not re-opening the identity decision, only reporting that its pin's coverage is narrower than claimed.
- **Durable context routed:** Yes — the stale `map/INDEX.md` finding is flagged as triage candidate `tc1` in the survey (`.agent-work/epic-418-followon/commander-f2/g1-review/review.json`) in addition to being a BLOCK finding here.

## Reconciliation check
`IDENTITY_TRADE.md` is itself the durable architecture record this gate is required to produce (`identity-trade-is-recorded`, settled/human) — it does not diverge from a prior baseline, it establishes one. No conflict with `docs/CHECKLIST_ENGINE_DESIGN.md:310-312`, which the document correctly cites as reaching the same conclusion independently.

## Blockers
- **Mutation 3 (pin coverage gap):** `IdentityBindingPinTests` does not exercise `call_tool`'s runtime dispatch. An undeclared per-call `spine_override` argument, read directly by the `spine_status` handler and never added to any tool's `inputSchema`, silently defeats `IDENTITY_TRADE.md`'s "no argument that would let it" claim without tripping any of the 5 pin tests. Recommend either (a) narrowing the trade document's claim to "no *declared* per-call argument" and naming this as a known limitation, or (b) adding a 6th pin test that drives `call_tool` directly with an out-of-schema identity-marker key and asserts it is rejected/ignored.
- **Stale `map/INDEX.md`:** `python -m pytest -q` is not actually green after commit `36a1bdcd` — `tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build` fails because the map was never regenerated after this gate's test additions. Fix: `python -m scripts.code_map build --root .` and commit the result.

## Out-of-scope observations
- None beyond the two blockers above (both are in-scope findings against this gate's own required evidence, not out-of-scope discoveries).

## Workflow Feedback

- **Handoff gaps:** None material. The handoff was unusually precise and pre-empted most ambiguity (it even told me which two mutations to run and what evidence to name).
- **Context rediscovered:** The "Survey State Location" convention named in the reviewer skill (`.agent-work/<work-id>/<gate>-review/review.json`) is not itself present as a labeled field in this handoff — I inferred the path (`.agent-work/epic-418-followon/commander-f2/g1-review/review.json`) from the pattern description and the repo's existing `.agent-work/epic-418-followon/commander-f2/` layout. Naming the exact survey path explicitly in the handoff (as it already does for the result path) would remove that inference step.
- **Instructions improvised around:** None on the engine/skill side. On my own side: while recording the `r3-evidence` finding I wrote a `--finding` string containing backticks around a shell command as illustrative text; bash executed it as a live command substitution inside the double-quoted argument (`` `python -m scripts.code_map build --root .` ``), which actually ran the code-map builder and rewrote the tracked `map/INDEX.md` in place — a real, if accidental, out-of-scope write. Caught immediately via `git status --porcelain`, reverted with `git checkout -- map/INDEX.md` before any further recording, and confirmed clean. No lasting effect, but it is exactly the kind of scope violation this run's own doctrine warns about, so I am logging it rather than quietly moving on.
- **What would have made this easier:** Nothing structural. The one process-level lesson (mine, not the skill's): never put literal backticks/command-looking text inside an engine `--finding`/`--summary` argument passed through a shell double-quoted string — write it with a different quoting style or strip the backticks even when only illustrating a command name.

## Return status
`complete`
