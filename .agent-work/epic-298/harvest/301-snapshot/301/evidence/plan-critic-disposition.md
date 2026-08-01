# Cold-critic findings and disposition — issue #301

Two cold critics were run, both with no authoring context. Running the *design* critic was
not required; running the *plan* critic was mandatory under
`lesson:cold-critic-mandatory-for-measurement-dependent-plans`, since this run's acceptance
depends on a required round-trip test (cross-session retrieval).

Triage authority: mine under inherited latitude (test strategy, implementation structure).
Nothing here reopens a pre-ruling or a floated decision.

## Critic 1 — on the design comparison

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | Two of six "unanimity" claims were manufactured; a third overstated | SERIOUS | **ACCEPTED.** Verified each mechanically before accepting. `durable_root()` appears in A:1, B:5, C:0, D:0 — and D was my recommendation. Id-scheme is 2-of-4, not 4-of-4. C's partition sits at `###` under `## entry:`, so the `grep '^## '` claim fails for C. COMPARISON.md §0 now records the error and the commands that proved it; a correction was sent to the Admiral. |
| 2 | No candidate tested a cross-**worktree** boundary, only cross-process | SERIOUS | **ACCEPTED.** This is the sharpest practical consequence of finding 1. Now an explicit requirement: g2 c5, g3 c3, and a mechanical check at g3-integrate c3. |
| 3 | D bundles all five agent-supplied fields into one assertion, so disputing one requires a rewrite | SERIOUS | **ACCEPTED** — a direct hit on `decision:no-foreclosure-is-testable`. Closed by graft 5 (per-field addressability for the agent bin only), and by g1 c5, g2 c6, g3 c7. |
| 4 | D's negative filter is silently breakable by an injected `- status: retired` line in free text | SERIOUS | **ACCEPTED.** Closed by graft 4 (single-line enforcement at the writer) plus a fixture. |
| 5 | My stated cost of A's file-move was wrong — all candidates cross-reference by id, not path | SERIOUS | **ACCEPTED.** My lean flipped to A and the Admiral was told it flipped and why. |
| 6 | C's INDEX critique was correct, arguably understated | FINE | Confirmed, no action. |

## Critic 2 — on the gate plan

| # | Finding | Severity | Disposition |
|---|---|---|---|
| 1 | g3 c2/c3 gameable — a compliant-on-paper test need not cross a real boundary | SERIOUS | **ACCEPTED.** Added g3-integrate c3, a mechanical check requiring `sys.executable`, `subprocess`, and `git worktree add` in the test file. Closes the two cheapest fakes. It proves the boundary was *invoked*, not that the test is correct — the reviewer still judges that. |
| 2 | No exercised test for per-field dispute, the priority-1 protected intent | SERIOUS | **ACCEPTED**, and this was the best finding of either critic. The obligation would have been met only in prose. Added g2 c6 (the write op must exist) and g3 c7 (a round-trip proving the disputed field changed, the sibling did not, and the sibling's line is byte-identical). |
| 3 | The repo's `!`-negation pattern unused in the three places it most applies | SERIOUS | **ACCEPTED**, and this one stings: `lesson:prove-command-fails-postcondition` was handed to me in my own launch order and I did not apply it. g2-integrate c3 is now a real negation check against three named fixture paths, and g2 c7 requires those fixtures to exist at exactly those paths. |
| 4 | Git does not track empty directories, so a bare-directory layout vanishes at commit | MEDIUM | **ACCEPTED.** g1-integrate c1 now requires `git ls-files` to return something for the store path. |
| 5 | The plan treats a floated recommendation as ratified | MINOR by the critic's grading, **treated as blocking by me** | **ACCEPTED.** The critic is right that this would repeat, one level up, exactly the manufactured-consensus failure §0 records. Added e0-context p1: a ratification record must exist before g1 starts; absent one, stop and reach up. |
| 6 | The promised #300 re-check never became an executable step | MINOR | **ACCEPTED.** Added g3-integrate c4, with an explicit defer-and-flag branch if #300 has not merged. |
| — | Scope fence respected; gate sequencing chains correctly; g1 keeps the suite green; #300 held as an obligation rather than a code dependency | FINE | Verified by the critic, no action. |

## Not accepted

Nothing was rejected. Both critics' findings were either accepted or already-fine
confirmations. That is itself worth noting rather than hiding: my first-pass design comparison
and my first-pass gate plan each had multiple real defects, and both were caught by cold reads
rather than by me.

## What neither critic could check

- Actual crew behaviour — whether dispatched implementers will write the adversarial fixtures
  the prose asks for. That is precisely why findings 1–3 became mechanical checks.
- #300's real manifest shape (concurrent worktree, out of scope) — held as an obligation and
  re-checked at g3-integrate c4.
- Anything empirical: no store code exists yet, so every finding is a static reading.
