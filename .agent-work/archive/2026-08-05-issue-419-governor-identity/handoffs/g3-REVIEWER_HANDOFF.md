# Reviewer Handoff — g3: correct `docs/GAUGE_WRITER_HOOK.md`

**Work id:** issue-419-governor-identity · **Gate:** g3 · **Worktree:**
`C:/Programs/constellation-skills-wt/epic418-a-419` · branch `epic-418/a-419-governor-identity`

## What was implemented

`docs/GAUGE_WRITER_HOOK.md` is the governor write side's structural record, and with no
`docs/architecture/` map in this repo it carries the weight an architecture packet would. Gates g1 and
g2 changed the code it describes; this gate corrects the document: the `isSidechain` polarity rule and
a new `agentId` row, a payload-field table, the per-agent binding key including the bind-nothing case,
the new `subagent-transcript-missing` skip cause, and two named surviving residuals.

Left **uncommitted** so you review it as `git diff`.

## How to inspect

```
cd C:/Programs/constellation-skills-wt/epic418-a-419
git diff -- docs/GAUGE_WRITER_HOOK.md
```

The implementer's account is at
`.agent-work/issue-419-governor-identity/results/g3-IMPLEMENTER_RESULT.md`. **Reproduce its claims;
do not accept them.** In particular it archived a grep sweep with counts and a by-command enumeration
of the payload fields — re-run both.

## The frozen invariant chain — this IS the gate

There is no runtime test here, so these three stand in for tests and were frozen before the work
started. Verify each **against the code**, never against the document's own assertions.

1. **No sentence still asserts the pre-fix sidechain polarity.** The archived sweep counts
   `isSidechain` / `sidechain` / `falsy` occurrences, but a token sweep is blind by construction — a
   sentence can assert the old rule without using any of those words ("the parser reads only main-chain
   lines" is the shape). So also **read the field-table and skip-cause sections end to end** yourself.
   The implementer reports the sweep alone missed two such sentences, which is the point.
2. **Every payload field the shipped hook reads appears in the document, and no field appears that the
   code does not read.** Enumerate the `data.get(...)` sites in **both** hook files by command and
   compare in both directions. The implementer reports 5 distinct keys, and reports that `agent_type`
   was **dropped** from the document because no hook reads it — adjudicate that call.
3. **The document's stated binding key matches `spine_rail.binding_key`**, including the bind-nothing
   case, and **both** residuals are named: the orchestrator holding several spines (unchanged), and the
   non-claiming subagent that now writes nothing (new).

## Specifically in scope for you, because the implementer filed it as out-of-scope and it may not be

The dispatched-agent record now carries a **fifth** field, `identity_resolution_ms`, while the
document's eyeball-check section still says *"All four fields present, no extras"* and
`gauge_writer_hook.py`'s module docstring still says the record is *"FROZEN, four fields only"*.

That is the document asserting something the code does not do — the exact defect class this gate
exists to remove. **Decide whether it falls inside invariant 1's spirit** and say so plainly in your
result. If you judge it in scope, that is a BLOCK-with-a-named-fix rather than a silent pass; the
Commander will apply the wording fix. The module docstring belongs to the previous gate's file and is a
comment only — flag it, do not edit it.

## Allowed scope / exclusions

`docs/GAUGE_WRITER_HOOK.md` only. No code file may have changed in this gate — verify that. Do not edit
any installed copy under `skills/`.

## Verification

```
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests -q
```

Must stay at **1667 passed, 2 skipped** — a doc edit that moves the count means a code file was
touched. **`python -m pytest`, never `py`.**

## The standard that governs your verdict

Assert against the **behaviour**, never against text describing the behaviour. Any guard that loops
must assert what it looped over and state the count.

## Return format

`REVIEW_RESULT` at `.agent-work/issue-419-governor-identity/results/g3-REVIEW_RESULT.md`, verdict the
literal word **APPROVE** or **BLOCK**, each of the three invariants met or not with the evidence you
personally reproduced, your ruling on the fifth-field question and on the dropped `agent_type` row,
findings separated into in-scope and out-of-scope, and a **Workflow Feedback** section (a bare "none"
is not acceptable).
