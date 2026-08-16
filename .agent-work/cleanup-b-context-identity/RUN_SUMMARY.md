# Run summary — lane B, `cleanup-b-context-identity`

For the Admiral. Written at the `review` step by leg 3, which is the leg that
closed the lane's execution.

## Verdict

**#600 is shipped, independently reviewed `APPROVE`, and integrated. #500 is
handed back as a settled design for the third time, on the engine's own
refusal.** The branch is parked, not merged — publication is the Admiral's class.

## What shipped

**#600 — a gauge reading is named for the agent that produced it** (commit
`3bc87e93`, 12 files, +1352/−202).

A context reading now belongs to an **agent** instead of a **folder**:

- `scripts/gauge_reader.py` holds the **one** definition of the owner key —
  `owner_key()` (slug plus 12-hex SHA-256, total over every string),
  `gauge_filename()`, `GAUGE_FILENAME`, `record_owner()`.
- `scripts/hooks/gauge_writer_hook.py` loads it by path, writes
  `gauge-<owner>.json`, and stamps a matching `owner` field into the record. Its
  ambiguity guard became a question about **attribution** rather than count.
- `scripts/checklist_engine.py` resolves the same name from its **own** active
  lease `session_id`. With no lease it reads the unowned `gauge.json` and trips
  exactly as today. With a lease and no owner-keyed file, the answer is **no
  reading** — deliberately no fallback to the shared file.

Filename **and** field, both: the filename removes the collision, the field makes
a mismatch detectable if one ever reappears.

## Gates closed

| gate | outcome |
|---|---|
| `e0-context` | closed — intent reconciled against the order as amended by ruling 1 |
| `g0-measure` | closed on leg 1's **accepted** measurement (`a89d61e3`), not re-run |
| `g1-implement` | closed and committed at `3bc87e93` |
| `g1-review` | closed — verdict **`APPROVE`**, checks (a)–(i) all PASS, 4 findings, **0 blocking** |
| `g1-integrate` | closed at `35ca31d1` — all five postconditions met |
| `g2-implement-500` | closed via the engine's `skip` on its authored **HAND-BACK** branch |

Then `reconcile` (`d000837f`), `triage`, and this `review`.

## The rulings, and one amendment made mid-flight

R1–R5 held. The one live question was **R4**, and it is worth the Admiral's
attention because of how it resolved rather than what it resolved.

Leg 2's implementer narrowed R4's third case and **carried the departure up
rather than burying it**. The Admiral then amended his own ruling
(`ADMIRAL_RULING-2.md`): with 2+ candidates carrying two or more **distinct**
owners under one binding key, skip-plus-sidecars is correct, because one binding
key has one transcript belonging to one agent, and owner-keying the *destination*
cannot make a single sample true of two owners.

That amendment arrived **after** `execute.json` was frozen, so the `g1-review`
gate imperative's check (d) still demanded the superseded behaviour. It was
**relayed to the reviewer through the handoff rather than by hand-editing the
frozen gate** — the reviewer verified the amended behaviour and was told
explicitly not to raise a finding against the change for matching the ruling.

The two things the Admiral held to were both verified, by driving rather than
reading:

- **#488's case still WRITES, and its test is same-owner-discriminating.** Flip
  the owner strings and the assertion fails — so it pins the same-owner path
  specifically, not merely "two candidates". *(One correction for the record:
  ruling 2 says #488's case "lands in row 2". It lands in row 1 — same directory
  plus same owner dedupes to a single candidate. The required outcome holds; only
  the row attribution is off by one.)*
- **The skip stays VISIBLE**, with sidecar content shown on both runs.

## Review quality

The reviewer took the implementer's word for nothing and tested two claims by
**mutation**, restoring both byte-identical:

- **R2 is total** — 482 real session ids harvested from 5496 JSON files, **0
  failures, 0 collisions**, including 111 slash-bearing ids, `null`, and the
  literal `'$SID'`.
- **Both out-of-scope extensions are FORCED, not discretionary.** It installed to
  `/tmp/g1rev-install`, confirmed the destination is flat, and drove the
  installed hook with `CLAUDE_PROJECT_DIR` unset. A checkout-only loader would
  fail into **no owner in every install** — a dark governor. It reverted
  `map/INDEX.md` and watched the freshness guard go red.
- **Fences hold**, whole-file by diff scope and the in-file `claim`-path fence by
  AST comparison. #601's `claimed_at` re-stamp survives.
- **Blast radius reproduces exactly**: 23 files / 186 occurrences.

## Measurement

**Failure-set difference is ZERO**, both sides measured at gate time on a cleared
cache in a clean env:

| tree | result |
|---|---|
| branch `ccb8b8d8` | 3104 passed, 6 skipped, **0 failed** |
| `main` `d7b911a7`, re-measured in a clean detached worktree | 3089 passed, 7 skipped, **0 failed** |

Two circulating figures are superseded: **3057** (frozen order) and the **3089**
quoted in `LAUNCH_ORDER-3.md` — note the freshly measured `main` also lands on
3089, for a *different* tree, which is exactly why critic F7 required a
difference rather than an absolute.

## The lane C re-measurement — measured, not assumed

The gate required reporting whether #549 landed and **re-running the probe rather
than assuming either way**. It landed (`915daefa`, merged in `df6f951b`).

`main` at `d7b911a7` is the clean isolate: it carries **#549 and not #600**.
Running the original pre-fix probe there still prints `VERDICT: CANDIDATE 2
CONFIRMED` — the orchestrator's `0.9` overwriting the dispatched agent's `0.02`
at one path, with `observed_at > claimed_at` so the #477/#601 guard still does
not fire.

**#549 removed one route into the collision; the mechanism was untouched.** The
Admiral's reading is confirmed by measurement. #600 was still load-bearing.

## The probe, retired properly

Post-fix the archived probe printed `VERDICT: NEITHER — the dispatched agent's
write was skipped`. Nothing was skipped: both agents wrote, to owner-keyed files
the probe was not watching. Left alone it would have told a future reader that
#600 **silenced** the governor.

It now asserts the post-fix world and exits non-zero **naming which invariant
broke** — including when a reading is simply **lost**, since "no collision" is
also what a dark governor looks like. On a tree predating #600 it refuses to run
and says so. The pre-fix output is retained byte-identical as
`probe_cross_key.pre-fix.out`, and `measurement/README.md` maps every artifact to
the world it describes.

Verifying it in **both** directions paid for itself: the red run exposed a real
defect in the probe's own module loader (no `sys.modules` registration, which
`@dataclass(frozen=True)` field resolution needs). It had only ever worked
because the *post-fix* hook registers `gauge_reader` as a side effect — invisible
in exactly the world the probe was written for.

## Architecture reconciled

No packet map exists in this repo, so the structural record was reconciled
directly. The implementer had already folded #600 into `docs/GAUGE_WRITER_HOOK.md`
and `docs/CHECKLIST_SCHEMA.md`, including R4 as amended; this run verified that
rather than trusting it and **added the one durable fact neither carried** — the
lane C re-measurement — so it survives the work area being archived. It also
states plainly that `decision:identity-not-time` is **not complete**: an agent
holding no lease is still unattributable, and closing that needs the *harness*
identity passed into the engine.

**One fenced-file violation was caught and reverted**, not shipped: `.mcp.json`
had been changed (`python3` → `py`) during the run. Lane A owns it.

## Triage — six routed, none filed

Filing is publication, and publication must be floated per the launch order, so
all six are **`recommend-and-defer`**, issue-ready in
`TRIAGE_RECOMMENDATIONS.md`. Zero `fixed-now`, zero `filed`.

| id | candidate | priority |
|---|---|---|
| **T1** | R4 row 2 is an untested governor branch | **HIGH** |
| **T2** | a `SessionStart` hook tells a crew to drive its **parent's** gate | **HIGH** |
| **T3** | a blocked Commander goes lease-stale while healthy | **HIGH** |
| T4 | a format sweep is not a dependency sweep | MEDIUM |
| T5 | sidecars per-directory while readings are per-owner | LOW |
| T6 | `verify-frame` refuses decision ids under a degraded map | MEDIUM |

Three deserve the Admiral's eye:

- **T1 is the sharpest thing this review found and it is not fixed.** R4 row 2 —
  write every candidate when 2+ share one owner — is correct by direct drive but
  **nothing tests it**: reverting to the old skip-on-count rule leaves **all 616
  gauge tests green**. A future simplification would restore the #488-class dark
  governor with no failing test anywhere. It **clears all four fix-now rungs**
  and was still deferred, because it surfaced at `g1-review` and by then
  `g1-integrate` had closed — adding code outside a gate is the one thing this
  run may not do. **It is the next leg's first pickup**, as a small crew gate
  before #500.
- **T2 now has three occurrences** — both crews and this Commander. Until the
  hook is fixed, the explicit warning in crew handoffs is load-bearing; the
  reviewer says it is what made the misfire unambiguous.
- **T3 reproduced independently this leg**: `advance execute` was refused with a
  stale lease after ~25 minutes blocked on the crew. The Admiral is filing this
  one himself; leg 3's reproduction is new evidence for it.

## Why #500 was handed back

Not a judgement call — the engine refused the gate:

```
REFUSED: g2-implement-500: context at 17% is at/over the hard limit, so this is
not the moment to BEGIN work here.
```

The reading it fired on is this leg's **own** owner-keyed gauge, stamped with its
owner. Before `3bc87e93` that same trip would have been unattributable, since
three distinct harness keys are bound to this one spine. **The governor this wave
built is what governed the wave that built it**, which makes the boundary
declaration evidence rather than assertion.

#500 is a **refuse-where-we-currently-permit** change touching the fenced
`claim` path — an implementer crew, an independent review, and red/green evidence
against the real engine. Beginning that at 17%, with the spine tail still owed,
meant abandoning it mid-way, which the gate forbids by name.

`DESIGN_500.md` returns **accepted and unchanged**. R5 already settled the shape
as option (a), so the next leg inherits a settled design and a named authority,
not an open question. Declared in `G2_BOUNDARY_DECLARATION.md` before any work
started.

## Returned for replanning

`REPLAN_INPUT.json` verifies via `verify_iterative_role_artifacts.py commander`:
**#600** as the completed outcome, **#500** as the one open current-wave issue,
nine wave-evidence entries, and **ten classified discrepancies** — all evidence,
**none auto-filed**.

## What remains

`feedback` and `archive`. The lane is parked at `archive` as ordered; the branch
is **not** merged.

_Leg 3, `commander-cleanup-b-context-identity`, 2026-08-16._
