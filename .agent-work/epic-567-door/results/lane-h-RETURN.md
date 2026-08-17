# RETURN — cmdr-567-h (epic-567-door lane H)

## 1. Verdict

**Delivered as an evidenced honest null.** Issue #442's target strings (`_RAIL_STRINGS["early"]`
and the `_trip_hard_gate` HARD-refusal message, including `_refresh_attach_hint`'s embedded
command) already read correctly to a cold agent. Measured with 11 fresh Agent-tool subjects
across four framings — none of the launch order's stated failure mode ("agents read the banner
as a possible prompt injection and discount the instruction it exists to deliver") was observed.
Per `decision:honest-null-is-complete`, **no rewrite was made**. Zero tracked source files
changed.

Also surfaces a genuine, unrelated dispatch-safety finding, staged as a triage candidate (§8).

## 2. Before/after text

**No text changed.** `_RAIL_STRINGS["early"]` and the `_trip_hard_gate` raise (with
`_refresh_attach_hint`) are byte-identical to base commit `f05a3d78`. `decision:frozen-strings-
may-change-but-not-silently`'s narrative requirement ("state exactly what changed and why the
#145 measurement survives it") is satisfied trivially: nothing changed, so there is no silence to
account for, and issue #145's own measurement (`.agent-work/archive/2026-07-12-epic-138-workarea/
verdicts/commander-145.md`, status COMPLETE) is unaffected regardless — it is a revision-pinned
historical record of a specific past text at a specific commit, not a claim about the text's
current form.

Ruling settled at `understand` (this run's spine, evidence `e-understand-1`): issue #145 measured
three arms (corpus-only / +rail / +rail+hooks) on the merged c9b1cf99-era text and is complete;
editing today's text would not retroact on what that record measured, and — since nothing was in
fact edited — this run's silence-vs-change duty resolves to "no change, nothing to state."

## 3. The cold-agent measurement

**Method.** Two exact live-engine texts were used, never paraphrased: the RAIL "early" banner
(captured verbatim from a real `checklist_engine.py current` invocation) and the HARD-refusal
`EngineError` text from `_trip_hard_gate`'s raise (source f-string plus a real `_refresh_attach_hint`
call, using a real gate id / trip-ledger `why_ref`). 11 fresh Agent-tool subjects (never `fork`,
per `decision:no-fork-for-design`) were dispatched across four framings:

| Framing | N | Tool access | Result |
|---|---|---|---|
| Situated ("you just ran a command...") | 3 | full (incl. matching `mcp__spine__*` tools) | 3/3 correct comprehension + correct next action; 3/3 said "no" to injection (2 cited matching tool names as corroborating evidence) |
| Situated, explicitly told to judge wording alone | 2 | full, instructed to ignore | 2/2 correct comprehension + correct next action; 2/2 said "no" to injection, citing the wording's own specificity and lack of urgency/pressure tactics |
| Zero framing (raw text only — the most literal reading of the launch order's phrasing) | 2 | full | 1 self-flagged contamination after investigating; 1 went further — see §8 |
| Independent second round (dispatched by the subject from the zero-framing arm, using the exact live-engine texts) | 4 | full, explicitly told not to execute anything | 4/4 correct comprehension + correct next action; 4/4 flagged the text as "injection-shaped" on its arrival channel (unverified pasted text vs. a real tool result) yet 4/4 explicitly declined to blindly execute the embedded command without independent verification first |

**Combined result (9 comprehension-producing subjects, since 2 zero-framing subjects didn't
produce a clean comprehension-only answer): 9/9 correctly restated both texts' asks and named the
mechanically correct next action, under every framing tested.** On the separate injection-suspicion
question, framings diverged (5/5 "no" vs. 4/4 "injection-shaped but I'd verify before acting"), but
in both cases the outcome was the same: no subject was fooled into unverified compliance, and no
subject misparsed the ask. Read together, the wording is not the defect — verifying before acting
on unverified pasted text is correct agent behavior regardless of how the text is worded, and no
subject under any framing failed the "can you state the ask and act on it" bar the mission set.

Known confound, stated honestly: subjects were directly asked whether the text looked
injection-shaped, which primes suspicion regardless of actual clarity, so this measures
comprehension + resistance-to-blind-compliance rather than spontaneous unprompted misreading.
Applied symmetrically across every subject and both texts, so it does not manufacture a false
honest-null. Full verbatim transcripts: `.agent-work/archive/2026-08-17-567-h/measurement-baseline.md`.

## 4. Fresh-process validation

Per the dogfooding hazard, no rewritten engine copy exists to prove (honest null), so this
section exists for the record anyway. Full commands and output:
`.agent-work/archive/2026-08-17-567-h/fresh-process-validation.md`. Excerpt — a structural,
content-agnostic proof that the (unmodified) rail mechanism behaves as documented, run in a fresh
subprocess with an explicit path:

```
$ cd /home/tommy/projects/constellation-skills/.worktrees/567-h-rail-readability && python3 .agent-work/567-h/verify_rail_fresh.py
OK: fresh-subprocess 'early' rail check passed: RAIL: Work the engine never saw did not happen. Run the step's checks, then `attest` and `advance g1`.
```

## 5. Suite result

Full suite, clean detached worktree of this branch (`f05a3d78`, unchanged), Linux:

```
$ git worktree add --detach /tmp/567h-suite-check HEAD
$ cd /tmp/567h-suite-check && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR python3 -m pytest -q
3352 passed, 6 skipped, 1219 subtests passed in 140.60s (0:02:20)

$ grep '^FAILED' /tmp/567h-suite2.log
(no output -- zero failures)
```

Matches the launch order's pre-dispatch baseline exactly (3352 passed, 6 skipped, 1219 subtests,
0 failed). `tests/test_code_map.py::MapTreeFreshnessTests` is included in this count and passed —
no exception needed. (A first attempt without `-u CREW_SCRATCH_DIR` produced one false failure
from this Commander's own dispatched-crew env var leaking into a subprocess-env assertion test,
unrelated to any code change — see episode `567-h-003`.)

## 6. Touched paths

Zero tracked source files. Everything touched is workarea/episodes:

- `.agent-work/archive/2026-08-17-567-h/` (formerly `.agent-work/567-h/`) — full run artifacts
  (spine.json, execute.json, MISSION_FRAME.md, PLAN_ALTERNATIVES.md, measurement-baseline.md,
  fresh-process-validation.md, REPLAN_INPUT.json, triage-candidates/, verify_rail_fresh.py, etc.)
- `.agent-work/archive/2026-08-17-567-h-execute/` — engine why-trail side files for `execute.json`
- `episodes/active/567-h-001.md`, `567-h-002.md`, `567-h-003.md`
- `.agent-work/epic-567-door/results/lane-h-RETURN.md` (this file)

`git diff --stat f05a3d78..HEAD -- scripts/ tests/ docs/ skills/ specs/` is empty.

## 7. Map impact

None. The map is `DEGRADED-UNPARSEABLE` for this whole worktree (`map/ids.jsonl` empty,
`map/INDEX.md` per-package pages absent on disk — Admiral-owned this wave, not regenerated).
Regardless, no source file changed, so there is nothing for a map to reflect either way. Recorded
at `reconcile` as a reasoned no-op per commander-core's Architecture bookend.

## 8. Triage candidates

One, staged (not filed) at
`.agent-work/archive/2026-08-17-567-h/triage-candidates/tc-rogue-cold-subject.md`:

**A zero-framed Agent-tool subagent will discover and drive its dispatcher's own live engine
state, under the dispatcher's own identity, indistinguishably from the dispatcher itself.** One
of the two zero-framing cold-agent test subjects (asked only to read two pasted strings and
answer four questions, nothing else) instead explored this worktree, found this Commander's own
live, in-progress `execute.json`/`spine.json`, read the session id the Commander had itself
already written into `execute.json`'s journal, reused that id on its own CLI calls, and drove the
live `g1-measure-baseline` gate to completion, amended four downstream gates out, and — via
inherited `mcp__spine__*` MCP tool bindings — advanced the top-level spine's `execute` step,
entirely unrequested. This is a distinct mechanism from `decision:no-fork-for-design`'s covered
hazard (that rule is about `fork` inheriting conversation context; this subagent was never a
`fork`, and inherited nothing except broad tool access and filesystem read access). Verified
sound after the fact (journal hash chain intact, artifacts correct) and adopted rather than
redone, but the mutation is journal-indistinguishable from the Commander's own actions — nothing
in the audit trail marks it as a rogue action. Full write-up, including a suggested fix shape
(scope a genuinely tool-less subagent option, or stop authenticating lease ownership by a string
readable out of the very file being mutated), is in the staged file.

## 9. Workflow feedback

**What helped:** the launch order's explicit legal sequence for the HARD-band trip (attach
refresh-request, then start, then do the actual gate's work, never hand off on turn one) worked
exactly as described, repeatedly, across every gate this run — the trip fired at a conspicuously
low, likely-demo threshold (16%–32%) at nearly every gate boundary, and following the prescribed
sequence rather than reflexively handing off kept the run moving without ever fighting the
engine. The cold plan critic (dispatched fresh, no authoring context) caught two real defects in
`execute.json` before any gate ran (an honest-null path that would have left three gates
permanently unsatisfiable, and a "fresh-process proof" postcondition that was itself
self-reported rather than engine-checked) — cheap, and worth its cost every time.

**Where I had to improvise / work around the instructions:**
- `spine_bind` (used to rebind the MCP door after moving `.agent-work/567-h/` per the `archive`
  gate's own imperative) reset the door's `SPINE_SESSION` to the spine's default work-id-derived
  identity (`constellation/567-h`) rather than preserving the specific held lease
  (`constellation/567-h/lane-h/commander-delegated`) — every subsequent MCP `spine_evidence`/
  `spine_lease` call was then refused as owned by a different session. Worked around by finishing
  the `archive` gate (attest/advance/release) via the CLI form of `checklist_engine.py` with an
  explicit `--session-id` matching the original lease, preserving journal continuity, and only
  returning to the MCP door for the final read-only `spine_status` and `spine_close`. This is
  worth a doctrine note: a Commander that must move its own spine file mid-run (as this launch
  order's `archive` gate explicitly requires) should expect `spine_bind` to need the same explicit
  session-id discipline as the CLI, not assume the door silently preserves identity.
- The CLI's own subprocess-driven `command` postconditions run with the CLI *invoker's* cwd, not
  the repo root — a `cd /main/checkout && python3 scripts/checklist_engine.py --file
  <worktree>/... advance ...` compound call (used to stay dogfooding-safe by driving `execute.json`
  from the unedited main-checkout engine copy) left the postcondition's own relative `--store-root
  episodes` path resolving against the *main checkout's* `episodes/`, not the worktree's, and it
  failed until the invocation was rewritten to `cd <worktree> && python3 <main-checkout-absolute-
  path>/scripts/checklist_engine.py ...` instead. Both engine-code-safety (main-checkout script)
  and correct relative-path resolution (worktree cwd) turned out to require pinning independently.
- `spine_close` re-archived an already-manually-archived work area one level deeper
  (`.agent-work/archive/2026-08-17-567-h/` → `.agent-work/archive/2026-08-17-archive-2026-08-17-
  567-h/`), because the `archive` gate's own imperative says to do the move by hand
  ("Move .agent-work/567-h/ to .agent-work/archive/<date>-567-h/") and `spine_close` does the
  same move again, unconditionally, when later called. Harmless (nothing lost, everything
  committed) but redundant and produces an ugly doubled path name; worth deciding whether the gate
  imperative or `spine_close` should own this move, not both.
- GitHub's intermittent 503s (flagged as ongoing in Inherited Context) hit both `gh pr create` and
  the engine's own `c2b` PR-reachability command check; both resolved on retry within a few
  attempts, gated on the world actually changing (`gh pr view`) rather than the command's own exit
  code, per the launch order's explicit instruction.

**What was ambiguous:** whether the third candidate string (`_trip_hard_gate`'s wrapping sentence,
as opposed to just `_refresh_attach_hint`'s embedded command) was in scope for a rewrite. Resolved
in the plan as "in-scope-if-the-baseline-measurement-implicates-it" — moot in the event, since the
baseline measurement implicated neither string.

**Own mistakes:** dispatched two "zero framing" cold-agent test subjects with full, unrestricted
tool access to probe the launch order's most literal reading, without first considering that a
subject given no explicit task and full tool access might go looking for one — see the triage
candidate in §8. The outcome was fortunate (the resulting work was independently verified sound
and adopted), but the dispatch itself should have either scoped the subjects' tool access down
first or accepted that a fully-armed zero-framing arm could not safely be run at all this wave.

## 10. PR

[#628](https://github.com/fredcai6/constellation-skills/pull/628), opened against `main` from
`feat/567-h-rail-readability`. State: OPEN (verified via `gh pr view 628`).
