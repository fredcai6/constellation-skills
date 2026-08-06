# Done-condition trace — issue #419

Every done-condition from `PROBLEM_STATEMENT.md`, the gate that closed it, and the evidence that
proves it. Nothing here rests on a crew's claim: each row names an artifact I re-verified myself.

| # | Done-condition | Closed by | Evidence |
|---|---|---|---|
| 1 | A subagent's binding lives under `session_id#agent_id`; the parent keeps its bare `session_id` | g1, confirmed live at g4 | `evidence/g4-binding-treatment.json` — three keys: one bare holding the parent's spine, and `…#a6df3902f0bf72c29` and `…#a69093b8ea2f159f6` each holding exactly one. Control arm, same script: **one** bare key holding three spines |
| 2 | Each agent's reading comes from **its own** transcript, sidechain filter inverted | g2, confirmed live at g4 | The pairing, recomputed by the reviewer with a parser importing neither hook: 2 of 2 dispatched, 4 of 4 overall. A parent-transcript fallback at ALPHA's instant would have read 0.047769, not 0.329482. `evidence/g4-recompute-output.txt` |
| 3 | An unresolved identity binds nothing and writes nothing | g1 (bind side), g2 (write side) | `binding_key` returns `None` on a present-but-unusable `agent_id` — the cold critic's traced damage path showed the tempting bare-key fallback would file the child's entry under the parent's and silence the **parent's** gauge. Write side: `subagent-transcript-missing` sidecar, `gauge.json` byte- and mtime-identical. Reviewer reproduced with 12 unusable values producing 0 artifacts by `rglob` count |
| 4 | `docs/GAUGE_WRITER_HOOK.md` corrected — sidechain inversion and the `agentId` field | g3 (two rounds) | The first review BLOCKed correctly. Final: seven sites asserting a four-field record found across four files, none surviving; polarity sweep 5 lines / 7 occurrences at live line numbers, each adjudicated, plus an end-to-end read that caught two sentences the sweep could not see |
| 5 | The accumulated stale bindings are swept, dry-run and before-state first | g5 | `evidence/binding-before.json` (64 entries), `binding-sweep-plan.md` (every entry with a KEEP/DROP reason), `binding-after.json` (1). Sweeper deleted after its one run |
| 6 | **A trip fires from a per-agent reading on a live run** | g4 | `REFUSED: g1: context at 33% is at/over the hard limit` — in the treatment stdout **and** in the acting agent's own transcript. Its gate is left `in-progress` with `refusals=1` while every other agent in the same arm completed; the control arm's same agent completed |

## Scope discipline — corner cases deliberately not chased

Per the launch order's standing ruling. Each is commented at its code site and floated in `RETURN.md`.

| what | where the comment lives | why not chased |
|---|---|---|
| An abandoned agent's key is never reaped — `release` is the only removal path, and per-agent keying makes a wave mint N keys where it minted one | `scripts/hooks/spine_rail.py`, at the release/cleanup branch | Out of the issue's stated scope, and the issue itself mandates deleting the one-time sweeper. Filed as a triage candidate |
| The binding store's read-modify-write takes no lock, so a concurrent claim can be lost | `scripts/hooks/spine_rail.py`, at `_save_json_map` | Concurrency was out of scope. The g5 sweeper mitigated its own exposure with a re-read-and-confirm before writing; the shipped hook did not change. Raised independently by two reviewers and a cold critic — the strongest triage candidate this run produced |
| `spine_rail`'s denylist and `gauge_writer_hook`'s allowlist disagree by design, so an id like `a:b` gets an orphaned binding | both modules, at their respective checks | No filesystem hazard — verified at source: the binding key is only ever a dict key, never a path. The durable fix moves the allowlist into `spine_rail`, but that file was closed and reviewed at g1 |
| A worktree-dispatched agent's binding records a main-checkout path | see `RETURN.md` — this one is **not** a corner case, it is a material limit on the win, and it is called out there rather than buried here | Predates #419 and is orthogonal to it; fixing it is a different issue |

## Diff trace

Every changed line traces to a numbered done-condition or a named non-regression obligation:

- `scripts/hooks/spine_rail.py` → DC1, DC3. The `session_view` union read is the named non-regression
  obligation: without it, re-keying silently drops the Stop rail's deterrent with no red test.
- `scripts/hooks/gauge_writer_hook.py` → DC2, DC3. `identity_resolution_ms` traces to the issue's own
  bullet ("Identity resolution records its own duration in the gauge write, per-call budget 100ms
  (placeholder)") and is read by g4's live budget assertion — measured 0.078–0.084 ms.
- `scripts/gauge_reader.py` → comments only, AST-identical. The authoring-side blast radius of the
  fifth field.
- `docs/GAUGE_WRITER_HOOK.md` → DC4.
- `tests/` → the evidence for DC1–DC3, plus the pinned real-payload fixture.

No line failed the trace, so none was deleted.

## Suite

`python -m pytest tests -q` → **1667 passed, 2 skipped, 550 subtests passed**, exit 0.
Baseline at HEAD `990712f` was 1621 passed / 2 skipped, so the delta is **+46** and a run reporting
exactly 1621 would have meant the new tests were never written.
