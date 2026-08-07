# Plan rigor — cold critic + design-it-twice, and what I did with each finding

Both mechanisms ran (bias-to-yes, neither skipped). Both were Opus, no Fable. Neither author had
my authoring context; the critic read only the frame, problem statement and gate plan, and the
alternative author read only the source and the real payload fixture.

## Design-it-twice — convergence

**Candidate A (mine, frozen):** existence-verified candidate roots — resolve a relative `--file`
against an ordered root list and take the first candidate that is really there.

**Candidate B (authored under the constraint "no filesystem search, no git subprocess — make the
truth be TOLD to the hook"):** the engine prints `##SPINE-ABS## <realpath>` on `claim`/`release`;
the hook reads it out of `tool_response.stdout`, with a provenance ladder behind it and a
`path_source`/`told` field on the binding entry.

**Converged on A, with two grafts from B.** B's own honest self-assessment is what decides it:
*"the engine that prints lives in the worktree. A worktree branched before this change prints
nothing → the exact bug persists, invisibly. Worst mode: it fails precisely in old worktrees,
which is the population that has the bug."* Every worktree currently in flight in this epic was
branched before any fix, so B would be silently inert on exactly the runs #440 exists to rescue.
Second, B depends on the marker surviving to `tool_response.stdout` — and `_COMMON.md` explicitly
instructs agents in this epic to **redirect command output to a file** to capture real exit codes,
which erases the marker.

Grafted from B into A:

- **`--worktree <dir>` as a resolution rung.** The engine's `claim` CLI already accepts it; when
  it is absolute it is told-truth and beats every guessed root.
- **`path_source` on the binding entry.** Record which rung resolved the path. Additive value
  field (not the key), and it is what lets the acceptance evidence prove *which* mechanism fired
  rather than only that the answer came out right.

Not grafted: the `##SPINE-ABS##` engine print, for the two reasons above.

## Cold critic — 12 findings, dispositioned

| # | Finding | Sev | Disposition |
|---|---|---|---|
| 1 | Control arm has no **positive** control — every unrelated null (missing import, uncalibrated model, no `agent_id`, stale reading) masquerades as "the bug reproduced" | BLOCKER | **ACCEPTED.** g2 now requires control to produce a real `gauge.json` with `fill >= hard` **at the wrong path**. Control must be shown to have worked and missed, not merely to have been quiet. This was the critic's strongest objection and it was right. |
| 2 | "Only the hook path differs" is false unless each arm has a **complete** module set — `gauge_writer_hook` imports `spine_rail` as a sibling and nulls silently if it cannot | BLOCKER | **ACCEPTED.** Each arm gets a full `scripts/` tree (worktree HEAD vs `git archive cbd9aee`), and the arm evidence carries a recursive diff of the two trees showing `scripts/hooks/spine_rail.py` as the only difference. |
| 3 | `gauge.json` carries no agent id, so "whose reading is this" is unanswerable from the artifact | BLOCKER | **ACCEPTED, three independent discriminators instead of one.** (a) the binding key is composite `session_id#agent_id` — only a dispatched agent produces that; (b) `identity_resolution_ms` is written **only** on a dispatched agent's record (#419), so a 5-field record is proof of a subagent origin; (c) the critic's own cheap trick — parent and subagent run on **different models**, so `gauge.json`'s `model` field attributes the reading. |
| 4 | g2 settles resolution rung 1 only; the git-worktree rung and the bind-nothing branch ride through ungated while the frame calls g2 their settle experiment | BLOCKER | **ACCEPTED, and the frame's claim narrowed.** A subagent's shell cwd resets between calls, so a real subagent *always* carries its `cd` in-command — the live fire genuinely cannot exercise the later rungs. They are settled instead by a **fresh-subprocess integration test against a real `git worktree` on disk** (not an in-context fixture, not a hand-injected root). `RETURN.md` states which rung each piece of evidence settles. |
| 5 | "First existing wins" picks the wrong root exactly where this bug has been running — the old behaviour seeded phantom `.agent-work/<work_id>/` decoys in the main checkout | BLOCKER | **ACCEPTED.** A candidate now has to be a **valid checklist**, not merely a file that exists: it must parse as JSON and carry the checklist shape. (The phantom dirs in fact contain `gauge.json` and no `spine.json`, so `exists()` would have held here — but that is luck, not design, and a work-id collision would break it.) |
| 6 | `cd /c/Programs/...` (MSYS form from the Bash tool) is not a Windows path and fails `exists()` | SHOULD-FIX | **ACCEPTED.** Normalize `/x/...` → `X:/...`; handle quoted paths, `Set-Location`, `pushd`, and `;` chains (PowerShell 5.1 has no `&&`). |
| 7 | `release` breaks: the spine may be archived or gone, so no candidate exists → bind nothing → the entry leaks forever | SHOULD-FIX | **ACCEPTED.** `release` resolves against the **recorded binding** for that key (unique suffix match) before it tries the filesystem, so a release still removes what a claim put there. |
| 8 | Timing — the gauge the `advance` reads is one tool call old and expires at 30 min | SHOULD-FIX | **ACCEPTED.** At least one tool call between inflation and `advance`; evidence records `observed_at` against wall clock. |
| 9 | The HARD cap is absolute tokens and an uncalibrated model yields **no reading at all** | SHOULD-FIX | **ACCEPTED.** The harness asserts the acting model is a `_PROFILES` key before it runs an arm, and names the token target. |
| 10 | Hook execution order is assumed | NOTE | **ACCEPTED.** `spine_rail` is pinned ahead of `gauge_writer_hook` in the arm settings file. |
| 11 | "Strictly greater than 1688" is not a regression test — adding 3 and deleting 1 still passes | NOTE | **ACCEPTED.** Also assert `failed == 0`, and that no previously-passing test id disappeared. |
| 12 | g3 mutates a live store shared with a running Admiral, with no lock | NOTE | **ACCEPTED.** g3's ruling is biased to **leave-to-age-out**; any mutation is dry-run-first with the before-state recorded. |

Nothing was dismissed. Findings 1, 2, 3, 5 and 7 each changed the plan in a way that would otherwise
have produced either a false green or a fix that quietly broke `release`.
