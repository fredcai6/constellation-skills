# Reviewer Handoff — g1: a gauge reading is named for the agent that produced it (#600)

Work id: `cleanup-b-context-identity` · worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity`
· branch `cleanup/b-context-identity` · merge base `a69bbac4`.

## Gate

`g1-review` in `.agent-work/cleanup-b-context-identity/execute.json`. Read that
gate's imperative — it lists checks (a)–(i) and they are your spine.

## Survey State Location

`.agent-work/cleanup-b-context-identity/crew-handoffs/g1-reviewer-survey.json`
(create it if absent; drive it through the engine).

## What Was Implemented

A context reading now belongs to an **agent**, not a **folder**. The writer emits
`gauge-<owner>.json` beside the spine — owner normalized **slug plus hash** from
the binding entry's `engine_session` — and stamps an `owner` field into the
record. The engine resolves the same name from its **own** active lease
`session_id`.

Read these three in this order before the diff:

1. `.agent-work/cleanup-b-context-identity/ADMIRAL_RULING-1.md` — **R1–R5 are the
   authority.** R1 and R2 are the human's own rulings. Where the frozen launch
   order disagrees, the ruling wins.
2. `.agent-work/cleanup-b-context-identity/crew-handoffs/g1-implementer-result.md`
   — what was built, the TDD evidence, and **three flagged departures** you must
   adjudicate rather than accept.
3. `.agent-work/cleanup-b-context-identity/crew-handoffs/g1-implementer-handoff.md`
   — the close criteria the work was commissioned against.

**The defect is measured, not assumed.** Two *distinct* binding keys whose spine
files share one `.agent-work/<work-id>/` each resolved to one gauge candidate,
each took the clean single-candidate branch, and each wrote — last writer wins.
The foreign write is **fresh**, so `observed_at > claimed_at` and #477/#601's
timestamp guard is **structurally blind** to it.

## How to Inspect the Diff

```
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity
git diff a69bbac4 -- scripts/ tests/ docs/ map/
git diff --stat a69bbac4
```

Live corroboration you can see for yourself: `.agent-work/.spine-rail-binding.json`
holds **three** distinct harness keys all carrying
`engine_session: commander-cleanup-b-context-identity` against the identical
spine, and `.agent-work/cleanup-b-context-identity/gauge-commander-cleanup-b-context-iden-88c76234484d.json`
is the Commander's own owner-keyed reading, written by the changed hook.

## Task Statement

Independently verify the g1 diff against R1–R4. **Reproduce every pasted command
yourself; take the implementer's word for nothing.**

## Close Criteria

Checks (a)–(i) in the gate imperative, all of them. The four that carry the most
risk, and why:

- **(b) R2 holds TOTALLY.** Feed the checkout's **real** session ids through the
  normalizer and confirm **every** one yields a usable key — slash-bearing ids
  (82 of 398 fail the allowlist that was originally proposed), the live entries
  carrying `engine_session: null`, and the one carrying the literal `'$SID'`.
  A normalizer that rejects even one input is the invisible-coverage-loss failure
  R2 exists to prevent: **losing the governor never shows up as a test failure.**
  Check that `skip` and `uncalibrated` are reserved so an owner cannot collide
  with `SKIP_FILENAME` / `UNCALIBRATED_FILENAME`.
- **(c) R3 holds, both halves.** A **leaseless** checklist still reads the unowned
  `gauge.json` and trips **exactly as today**. Separately: a **leased** checklist
  with no owner-keyed gauge returns `None` rather than falling back to the shared
  file. The fail-safe is "no *attributable* reading yields `None`" — confirm it
  has not become "no lease yields nothing".
- **(d) R4 and #488.** An Admiral's `spine.json` plus its
  `latitude-interrogation.json` in **one** work directory must still **write**.
  That regression cost an entire wave of dark governor.
- **(a) The governor never REFUSES where it previously permitted.** **Enumerate**
  the refusal paths; do not sample them. This is the lane's hard latitude
  boundary — a new refusal is not shippable here and must be floated.

## The three departures you are adjudicating

The implementer flagged all three rather than taking them quietly. Judge each on
the merits; you may confirm, narrow, or reject.

1. **R4 narrowed in one branch.** With 2+ candidates under **one** binding key
   resolving to **two distinct owners**, the implementer **skips** instead of
   writing every candidate. The argument: one binding key has exactly **one**
   transcript, so writing it to both files agent A's fill against agent B — the
   fan-out dead end tried, measured and reverted in #202/#261. R4's *rationale*
   ("the writer could not tell whose reading it held") is satisfied by
   owner-keying; its literal wording did not anticipate that third branch. The
   branch behaves exactly as today, so it cannot make the governor louder.
   **Test the claim that this branch is unreachable-or-conservative, and say
   whether you agree the literal reading would re-arm a known dead end.**
2. **Three files outside Allowed Scope:** `scripts/install_constellation.py` (+
   its test) and `map/INDEX.md`. The claimed justification is that the install
   destination is **flat**, so a loader written only for this checkout's layout
   would fail in **every install** — silently, into no owner, leaving the writer
   producing `gauge.json` while a leased engine reads `gauge-<owner>.json`. That
   is a **dark** governor, not an inert one. **Verify that claim by installing and
   driving the real loader**, not by reading the argument. If it does not hold,
   the extension is not justified and should come out.
3. **The sidecars stay per-directory and unowned** (`decision:sidecar-name`).
   Confirm this cannot cause one agent's skip/uncalibrated sidecar to be read as
   another's.

## Allowed Scope

Review only. Do not edit implementation files. Write your survey and your
`REVIEW_RESULT`.

## Specific Exclusions

**Fenced — confirm they are byte-identical rather than trusting the claim:**
`scripts/hooks/spine_rail.py`, `tests/test_spine_rail.py`, `scripts/run_crew.py`
(lane C); `scripts/mcp_spine_server.py`, `.mcp.json` (lane A); `episodes/**`;
`checklist_engine.py`'s **claim path** (#601 landed on `main` this morning).

`measurement/probe_cross_key.py` is **deliberately** left describing the *pre-fix*
world and is **not** a defect — retiring it belongs to the Commander at
`g1-integrate`. Do not flag it as stale.

## Constraints the Implementation Must Respect

- **Clear `__pycache__` before every measurement** (#597). Stale bytecode
  fabricates failures that look like defects; it cost this epic hours twice.
- Platform Linux, Python 3.12 as `py`. CI is one `windows-latest` job, **red at
  baseline** — local Linux is the only real signal.
- **Hook code is not fenced by git isolation.** `CLAUDE_PROJECT_DIR` is resolved
  once at session launch and inherited unchanged, so a hook change cannot be
  validated from inside the session that contains it. Validate in a **fresh
  process**, never a fixture that hand-injects that variable — supplying it proves
  nothing about what the harness delivers.
- **R1's limit must be respected and stated, not overclaimed.** #601's timestamp
  comparison must still be present and still fire on the sequential relaunch case.
  This wave fixes the **concurrent** collision and does **not** complete
  `decision:identity-not-time`. If the result claims otherwise, that is a finding.

## Map Anchors (inbound)

- The map is **DEGRADED** (`map/ids.jsonl` empty, per-module `INDEX.md` targets
  absent). The real entry point is `docs/GAUGE_WRITER_HOOK.md`, the hash-pinned
  substitute in `.agent-work/cleanup-b-context-identity/map-orientation.json`.
  Its "Skip-on-uncertainty, enumerated" section is the design intent for the
  write side.
- Read side: `scripts/gauge_reader.py`'s `_PROFILES` note (`:76`). Policy side:
  the trip block comment from `scripts/checklist_engine.py:1328`.
- Decisions in force, with grades, in
  `.agent-work/cleanup-b-context-identity/MISSION_FRAME.md`.
- **Recorded dead end:** fan-out — writing one reading to *every* bound spine —
  was tried and reverted (#202/#261). Relevant to departure 1.

## Evidence Produced

In `g1-implementer-result.md`: RED at the merge base and GREEN at head for the
four required node ids, the two verification commands with pasted output, a
re-measured `main` baseline, the reconciled blast-radius count, and a
fresh-process demonstration at `measurement/demo_owner_keyed_gauge.py` with
`.before.out` / `.after.out`.

**Re-run all of it.** The four discriminating node ids:

```
tests/test_gauge_writer.py::OwnerKeyedGaugePath::test_two_keys_one_work_dir_each_keep_their_own_reading
tests/test_gauge_writer.py::OwnerKeyedGaugePath::test_two_spines_one_key_one_owner_still_writes
tests/test_gauge_reader.py::OwnerKeyNormalization::test_every_live_session_id_yields_a_usable_owner
tests/test_checklist_engine.py::TripGaugeReadingOwnership::test_leaseless_checklist_reads_the_unowned_gauge
```

```
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity && \
  find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

The merge gate is a **failure-set difference** against a `main` baseline
**re-measured at gate time**, not an absolute number. `main` was 3057 passed / 0
failed at dispatch; measure both sides yourself and report both.

## Suggested Model Tier

Opus. A governor that must become neither bypassable nor trigger-happy, spanning
three modules that move together, with three flagged departures to adjudicate.

## Stop Conditions

Stop and return rather than pushing through if the change makes the governor
refuse where it currently permits, if a fenced file was edited, or if you need
context this handoff does not carry. Reach up rather than guessing past a gap.

## Return Format

Write `REVIEW_RESULT` to
`.agent-work/cleanup-b-context-identity/crew-handoffs/g1-reviewer-result.md`
**before ending your turn** — that write is the delivery.

Include a `Verdict` of exactly `APPROVE` or `BLOCK`, your findings with
severities, your explicit adjudication of each of the three departures, every
command you re-ran with its pasted output, both suite numbers and their
difference, and a `Workflow Feedback` section.

**One warning, from the implementer's own postscript.** A `SessionStart` hook may
tell you to drive the *parent Commander's* `execute` gate, because it resolves
`SPINE_FILE` from an inherited environment. **That is not your run.** Acting on it
requires a `--force` takeover of a live parent's lease and would deadlock the
wave. Drive your own survey only, and note the misfire in Workflow Feedback.
