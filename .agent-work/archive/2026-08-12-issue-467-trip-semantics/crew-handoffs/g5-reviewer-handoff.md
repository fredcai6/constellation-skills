# Reviewer Handoff — `g5-review` (DC5: the acceptance round trip)

Issue #467 (epic #418), branch `epic-418/a2-467-trip-semantics`, worktree
`C:/Programs/constellation-skills-wt/epic418-a2-467`. Work only in this worktree, absolute paths.

## Gate

`g5-review`. The gate before it, `g5-acceptance`, is closed and is what you are reviewing.

**The question is whether the round trip HAPPENED — not whether `ACCEPTANCE.md` says it did.**
Everything below is a claim to be attacked, including the parts that read as settled.

## Survey State Location

Create your review survey at
`.agent-work/issue-467-trip-semantics/g5-review/review.json`.
Never at the worktree root. Build every scratch fixture in your own temp directory.

## Pin the engine by hash, not by size

Re-derive at the moment you use it; do not copy a number forward from any document, including this one:

```
git rev-parse HEAD                              # expect 6bc971e579b6c34cd3af70f0e09b30a601584d51
git rev-parse HEAD:scripts/checklist_engine.py  # expect c281cb68eaac65d1169dd6737a6a322728df98eb
```

Anything you measure about engine behaviour must come from `scripts/checklist_engine.py`
**in this worktree**, never an installed skill bundle. (`ACCEPTANCE.md` states the engine blob is
byte-identical at `cc4aed99`, `27ae8563` and HEAD. Check that rather than assume it.)

## What was implemented

`g5-acceptance` is a **measurement**, not a code change. No file under `scripts/` or `tests/` was
touched by it. What it produced:

1. A **separate acceptance spine** at `.agent-work/acceptance-467/spine.json` (never this run's own
   spine), authored once by `acceptance/build_acceptance_spine.py`, which refuses to run twice.
2. **Two dispatched Sonnet agents.** `acc-89f734` (A) worked gate `a1`, was **refused** at
   `start a2` by the shipped begin-work guard, filed the refresh-request the refusal printed,
   released and stopped. `acc-7f3d1b` (B) was dispatched **cold** with the `current` output as its
   entire prompt and closed `a2`.
3. A **verifier** at `.agent-work/issue-467-trip-semantics/acceptance/verify_round_trip.py`
   (9 assertions, plus a `--self-test` that mutates the real inputs nine ways).
4. Two probes: `acceptance/probe_close_side.py`, `acceptance/probe_dc4_neighbour.py`.
5. `.agent-work/issue-467-trip-semantics/ACCEPTANCE.md` (447 lines) — the write-up under review.
6. `evidence/g5-*.txt` — every command output cited.

## How to inspect

The work is **committed**, tree clean. The gate's own output is commits `27ae8563` and `6bc971e5`:

```
git show --stat 27ae8563
git show --stat 6bc971e5
git status --porcelain          # must be empty; re-check after every revert (CRLF renormalisation)
```

Do **not** review `git diff main...HEAD` — that shows unrelated merged-PR divergence.

**`.agent-work/` is TRACKED in this repository, not ignored.** `ACCEPTANCE.md` §8 exists because
the predecessor's own closing digest said otherwise and the why-trail is append-only so the wrong
sentence could not be edited out. Nothing was lost. Do not report the correction as a defect; do
feel free to confirm it (`git check-ignore -v` on `ACCEPTANCE.md` exits 1).

## Task statement (what `g5-acceptance` was told to do)

> On a real spine with a planted, asserted over-threshold reading, agent A works a gate, trips,
> closes its gate carrying its handoff, files the refresh-request, and goes idle; agent B is
> dispatched COLD with the `current` output alone — no separate handoff document, no re-briefing
> from your own memory of the run — and completes what A was mid-way through. Record B's VERBATIM
> dispatch prompt in the acceptance record so the cold-start claim is falsifiable after the fact.
> Write a verifier script that reads the resulting spine and asserts mechanically: two distinct
> engine session ids acted, A's why-record exists at the tripping gate, B advanced a gate after A's
> last action, and the trip ledger holds the expected entries. Then re-run the g1 RED and record
> that it no longer reproduces. Verify #431 is dissolved with evidence; do NOT close it. Write
> `ACCEPTANCE.md` with a reading-exists assertion for every claim about trip behaviour and
> per-done-condition accounting DC1–DC6.

## Close criteria — each becomes a review check

**C1. B's verbatim dispatch prompt contains nothing but the `current` output.**
If it carries any re-briefing, the measurement is void. Source of truth is
`.agent-work/acceptance-467/PROMPT-B.txt`.
*Already independently confirmed by the Admiral:* 3754 bytes, sha256
`3da641137aa5b7c67bf59c35c6991911a05adb3958458bbbf8f505a98d92f80f`, opening with the engine's
`RAIL:` / `LEASE` / `ACTIVE` output, no briefing language. **Check it anyway** — but a disagreement
with this specific finding is worth escalating in your report, not filing as a routine note.
Also judge: is the block quoted in `ACCEPTANCE.md` §2 byte-identical to `PROMPT-B.txt`? The claim is
that equality was asserted in code rather than by eye. Verify the equality yourself.
And judge the harder version of the question: the spine's **gate imperatives** are inside that
prompt (they are rendered by `current`). The claim is that they are *job-file* content authored
before A ever ran and never edited afterwards. Test that claim — the journal, the builder script's
refuse-to-rerun behaviour, and git are all available to you. If any imperative was edited after A
ran, the cold-start claim collapses.

**C2. The verifier actually discriminates.**
**Break its inputs YOURSELF. Do not trust `--self-test`.** The predecessor's own self-test found a
defect *inside its own verifier* — the "override not in force" mutation was being caught by an
earlier `fill >= hard` assertion, so the override assertion never fired on its own; a check that
only ever fires behind another check is a check that cannot fail. That is the single strongest
reason a second pair of hands has to try. Construct your own broken round trips from the real
inputs and confirm each is rejected by the assertion you intended, not by an earlier one. Suggested
attacks beyond the nine: an assertion that passes on an empty list; a mutation that changes a value
the verifier never reads; feeding it a spine where the two session ids differ only in case or
whitespace. Note that `verify_round_trip.py` hardcodes `ACC` to an absolute path and takes `--acc`
to override it — copy the inputs to your own temp directory and point it there.

**C3. The two session ids are genuinely distinct agents**, not one agent renaming itself. The
journal (`.agent-work/acceptance-467/spine.json.journal`) and the two logs
(`log-acc-89f734.txt`, `log-acc-7f3d1b.txt`) are the evidence. A's last action is claimed at
20:08:25 and B's first at 20:11:11, i.e. no overlap. Verify the timestamps and the ordering from
the journal, not from the table in `ACCEPTANCE.md`.

**C4. B's completed work corresponds to what A was mid-way through, not to something easier.**
**This is the strongest evidence in the gate and should be reviewed as such.** `a1`'s imperative
made A invent a six-hex nonce and forbade writing it to disk; `a2`'s imperative required item 6 to
*be* that nonce. B wrote `6. NONCE: 4b3dc4`; A's why-record `w-1` says "The nonce is 4b3dc4." That
containment is what separates a round trip from two agents doing adjacent chores.
The claim that matters is **that the nonce existed nowhere else on disk when B was dispatched.**
Count it yourself across the whole acceptance directory and the worktree — the predecessor reports
0 in A's log (A caught the engine echoing its own `DIGEST:` into that log and redacted the one
occurrence), 0 in `roundtrip.md` before B ran, 2 in `spine.json`'s `why_trail`. A redaction that A
performed on its own log is exactly the kind of thing to check rather than accept: read the log,
see whether the redaction is visible and explained, and judge whether the surrounding text could
have carried the nonce to B by another route.

**C5. Every trip claim carries a reading-exists assertion.** No absence is evidence.
`ACCEPTANCE.md` §0 is a six-row reading ledger; check that **every** claim about trip behaviour in
the document traces to one of those rows, and that each row traces to something the **engine**
wrote (`trip_ledger` entries carry their own `fill`/`hard`/`model`). Specifically check the
planted-vs-live split §0 declares: R1/R2 planted, R3 live. The predecessor reports an asymmetry
against itself — the gauge **writer** was silent for agent A with no skip record to say why, while
the **governor** fired at all six events. Judge whether that is stated honestly and whether it
undercuts any claim built on R1/R2.

**C6. The per-done-condition accounting is honest, with `partial` where partial is true.**
`ACCEPTANCE.md` §6. Read each verdict against the evidence cited for it.
- **DC2 is reported `done-by-different-means`, not `done`.** The reasoning is §5a: the shipped
  engine draws the line *between verbs* (`TRIP_HARD_GUARDED_VERBS = {"start", "reopen"}`; `advance`
  is never governor-refused), so #467's literal DC2 text describes a distinction the engine does
  not have. Verify the claim about the engine directly from source, and judge whether the departure
  is stated plainly enough that a reader meets it without reading the DIT.
- **DC6 is reported `partial` and that is the correct answer.** Both rendered lines were observed
  live in B's own prompt and the historical line survives the mandated close, but at closeout
  `_trip_advisory` returns early on the `gate is None` path and both lines go silent. That is
  `tc19` / issue **#504**, filed and **deferred by Admiral ruling**. **Do not round DC6 up to
  done, and do not block on #504 being unfixed** — an honest partial is the result the Admiral will
  report. If you think the partial is *under*-stated, say so; that is in scope.
- Also in scope: DC1, DC3, DC4, DC5 are reported `done`. Attack any of them.

**C7. The RED no longer reproduces, and the non-reproduction is not an absence argument.**
`python .agent-work/issue-467-trip-semantics/red-repro/repro_431.py --all` — for that script
**exit 1 means "NOT reproduced"**, which is the outcome the fix predicts; exit 0 would mean the
defect is back. Confirm it asserts the engine printed `CONTEXT 30% (>= hard)` and that g2's
postconditions were all met *before* it attempts the advance. Note that re-running it rewrites its
own tracked `red-repro/scratch/` fixtures — expected residue, already committed; check
`git status --porcelain` after and report if it leaves the tree dirty.

**C8. #431 is verified dissolved and NOT closed.** §4. The three legs are the RED, the standing pin
`test_handoff_advance_at_hard_with_no_refresh_request_closes_and_freshens_digest` at
`tests/test_checklist_engine.py:3514` (which asserts `_refresh_requests_anywhere(cl) == []` on both
sides so the guard cannot silently lift), and the close-side probe. Re-run the probe and confirm
all three moves happen at **one and the same** reading. Confirm no artifact in this gate closes
#431 or claims it closed.

## Two things you must be told, so you do not report them as defects

**1. Agents A and B were deliberately NOT dispatched through `run_crew.py`, and that is not a
process violation.** `g5-acceptance` carries an **explicit crew waiver** (it is in the gate
imperative: the deliverable is a measurement whose instrument is two dispatched agents, and a crew
implementing it would sit between the measurement and the thing measured). A and B are measurement
instruments, not Implementer/Reviewer crews. Bolting a `run_crew.py` result-artifact contract onto
B would have been one more surface for re-briefing the very agent whose prompt had to stay pure.
Provenance therefore lives in `PROMPT-A.txt` / `PROMPT-B.txt`, the two agent logs, and the journal.
**You will find no `crew-runs.json` entry for A or B. That absence is by design.** Report it only
if you think the provenance that replaced it is inadequate — that is a legitimate finding — but do
not report the missing wrapper entry as a lapse in itself.

**2. The verifier stays where it is.** It sits at
`.agent-work/issue-467-trip-semantics/acceptance/verify_round_trip.py`, the path the plan declared
and `g5-acceptance` c1 names. The Admiral has **ruled** against promoting it to `scripts/` now:
moving it would change the artifact under review after the measurement. Promotion is recorded as a
follow-on question. "This should live in `scripts/`" is a triage candidate, not a blocker.

## Allowed scope

Read anything. Run anything read-only. Build your own fixtures and mutations in temp.

## Specific exclusions — flag if touched, but do not block on un-inspectability

- Do **not** mutate `.agent-work/acceptance-467/spine.json`, its journal, `roundtrip.md`, the two
  `PROMPT-*.txt` files, or either agent log. **They are the measured artifact.** Copy to temp and
  attack the copy. If you dirty them, say so immediately.
- Do **not** touch `.agent-work/issue-467-trip-semantics/execute.json`, `spine.json`, `gauge.json`
  or `STATE_NOTE.md` — the Commander holds their lease. Do not run `checklist_engine.py` against
  them.
- Do not commit. Do not push.
- `tc19` / #504 is deferred by ruling; g4's shipped mechanisms, g2's and g3's mechanisms, and the
  `tc4` refactor are all out of scope.
- `C:/Programs/constellation-skills/.claude/settings.local.json` (the gauge-writer hook) is outside
  your worktree. It is **Commander-verified, not reviewer-verified** — note anything you cannot
  inspect and move on; un-inspectability is not a BLOCK ground.

## Constraints the measurement had to respect

- **NO ABSENCE IS EVIDENCE.** Assert a reading existed before any claim about trip behaviour. If a
  run observes no trip, name which of the two you observed: a silent governor, or a governor with
  headroom.
- **`constraint:cold-start-from-current-alone`** — B gets `current` and nothing else.
- **`constraint:job-file-not-agent-file`** — B reuses A's spine file; it is never copied or
  recreated.
- **DC5 may not be reported `partial` on the strength of DC1–DC4 landing.** Either the round trip
  completes, or it is returned as a scoped null naming the specific mechanism that failed to
  express — never as "this approach is impossible."

## Map anchors (inbound)

Inherited from `g5-acceptance`; the review verifies the measurement, not the write-up.

- **Structural:** `scripts/checklist_engine.py` — the shipped begin-work guard, the trip ledger, the
  advisory, and the `current` cold-start surface (`_why_suffix`).
- **Capability:** the reach-up / refresh round trip — trip, handoff, refresh, resume.
- **Constraints:** `constraint:no-absence-is-evidence`, `constraint:cold-start-from-current-alone`,
  `constraint:job-file-not-agent-file`.
- **Decision anchor:** `decision:round-trip-is-the-point` — DC1–DC3 are all satisfiable while every
  tripped agent produces a useless handoff, because none of them look at the far end.
- **Map confidence flag — and it is WRONG, which matters.** The gate's `confidence_flags` say
  "#458: the gauge writer is not wired in tracked settings, so every reading in this acceptance is
  planted rather than harness-produced." Half is right (no *tracked* setting wires it); half is
  wrong (it **is** wired as an untracked `PostToolUse` `*` hook and demonstrably fires). The
  correction is `ACCEPTANCE.md` §0. Confirm rather than trust — in either direction.

## Evidence produced (re-measure it; do not accept the report)

| Claim | Where |
|---|---|
| verifier passes 9/9 | `evidence/g5-verifier.txt`; postcondition `g5-acceptance.c1` |
| self-test rejects 9/9 | `evidence/g5-verifier-selftest.txt` — **and you must break the inputs yourself** |
| RED does not reproduce | `evidence/g5-red-nonrepro.txt` (exit 1 = not reproduced) |
| close-side, three moves at one reading | `evidence/g5-close-side.txt` (exit 0) |
| DC4 override vs neighbour at one reading | `evidence/g5-dc4-neighbour.txt` (exit 0) |
| anti-vacuity check fires | `evidence/g5-antivacuity.txt` (real exit 5 on empty collection, 0 on the real pattern) |
| full suite | `evidence/g5-suite.txt` — 1867 passed, 2 skipped, 829 subtests, real exit 0 at `cc4aed99` |

Re-run the full suite yourself and explain any delta:

```
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

## Standing traps on this run — all still apply

1. **NEVER pipe pytest before reading its exit status.** The predecessor piped pytest to `tail` and
   read `EXIT=0` from the very command that exits 5 — while proving an anti-vacuity check fires.
   Redirect to a file and echo `$?`; a piped `$?` is the pipe's. This is the most reliable way to
   manufacture a false green here, and it has already bitten this run twice.
2. **`SUBFAILED` vs `FAILED`.** pytest reports subtest failures as `SUBFAILED(param) path::Class::test`.
   A `FAILED`-only grep produced two false survivors in an earlier review on this run and would have
   caused a wrong BLOCK. Match both.
3. **Verify on what the agent DOES, never on what it is TOLD.**
4. `main()` does **not** save state on `current`.
5. **Clock skew / stale gauge.** A reading is discarded when >30 min old *or dated in the future*.
   A hand-typed `observed_at` slightly ahead of the wall clock collapses to `None`, the scenario
   reads as "no gauge", and the test goes **vacuously green**. Generate every timestamp from the
   clock.
6. **No mock in the advisory path** for any seam measurement — pass a real `base_dir` holding a real
   `gauge.json` rather than patching `_read_gauge`, and drive the real CLI in a subprocess.
7. **CRLF.** `git checkout` of a subset of files can renormalise line endings and dirty
   `test_context_manifest`. Check `git status --porcelain` after every revert.
8. **Pin the engine by hash, never by byte size.** An earlier handoff on this run quoted a size that
   matched nothing on disk and the reviewer was right to call it out.

## Suggested model tier

**Sonnet.** Standing default for reviewers on this run. No named Opus reason applies: the criteria
are enumerated, the artifacts are on disk, and the work is a bounded attack on a stated measurement.

## Verdict discipline — read before you write anything

Return **exactly one** of `APPROVE` or `BLOCK` as the first line, then `blocking_findings: <n>`.

- **Do not invent a third verdict string and do not soften one to fit.** The Commander is under
  standing orders to float any other verdict to the Admiral rather than reword it, so a
  non-conforming verdict stalls the gate instead of passing it.
- **BLOCK only for something that actually blocks** — a finding that falsifies a close criterion. A
  finding that does not is an observation; say so and let it be one.
- **APPROVE if it holds.** Do not manufacture a blocking finding to justify the review. A BLOCK on
  this gate is a real and respected outcome — the last one on this run was right and drove a rework
  — so if the round trip did not happen, say so plainly.
- Out-of-scope finds go in a **triage candidates** section, not the verdict.

## Stop conditions

Stop and return BLOCK if the artifacts cannot be accessed, if evidence is absent or unverifiable, or
if a policy decision is required before a verdict is possible. Return without a verdict only if you
cannot reach a defensible one — and then report "this specific check failed", never "this approach
is impossible."

## Return format

Write your `REVIEW_RESULT` to
`.agent-work/issue-467-trip-semantics/crew-handoffs/g5-reviewer-result.md`.
First line `APPROVE` or `BLOCK`; second line `blocking_findings: <n>`; then:

1. Your answer to the deciding question — **did the round trip happen?** — with the measurements
   behind it.
2. **Your own attacks on the verifier**, listed one by one: what you broke, which assertion caught
   it, and whether any assertion turned out to be unreachable behind another. This section is the
   reason you were dispatched.
3. The prompt-purity check: your byte/hash comparison and your reading of the prompt for briefing
   language.
4. The nonce-containment check: your own counts, and your judgement of A's self-redaction.
5. Per-criterion findings C1–C8.
6. Non-blocking findings.
7. Triage candidates.
8. Workflow feedback — what in this handoff or the workflow made the review harder than it needed
   to be.

**Deliver it via `SendMessage` to `commander-w4-467-j` before ending your turn.**
