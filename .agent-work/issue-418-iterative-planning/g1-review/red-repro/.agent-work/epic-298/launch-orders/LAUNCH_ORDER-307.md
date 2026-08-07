# Launch Order: `commander-307 — issue #307, map-first measurement, POST arm`

You start cold. Everything below is pasted, not pointed at.

**This issue is HITL.** You assemble the paired evidence package. **Tommy adjudicates the B3 map-first verdict.** Do not self-adjudicate it, do not pre-empt it, and do not present a single reading where the evidence supports more than one.

## Mission

Run the POST arm and compile the paired evidence package. Evidence pairs **the manifest** (map availability at a revision) with **run-transcript tool-call ordering** (map reads vs source reads), against the captured baselines. Terminal act: **present to Tommy and record his verdict.** On falsification, route rework per the spec (contract, map content, or measurement) — but the routing recommendation is a proposal, not a decision.

## The question, stated precisely

**Does the map-first contract change the ORDER in which an agent orients?**

Not whether the map is read. Not whether it is useful. Not whether it is cited. **Order.** The baseline already established that the map is read, useful, and cited — and never the thing that found the seam.

Tommy's framing, verbatim, and it is the whole issue:

> *"There's a gulf between saying 'there is a map' and 'use the map first to orient yourself'."*

And his standing steer on evaluation:

> *"Let's just make sure we're considering the context when we are doing evaluation."* — i.e. **never score a signal without checking what produced it.**

## Prior arms — pasted, because you start cold

**THE PIN: f1Brainz `3541d2929b19de37107ae13e56776b7162d07255`. The POST arm MUST reuse it.** Task set: **#690, #688, #698, #716, plus #704 as control.**

**PRE-A (merged `8de2faa`, record at `.agent-work/epic-298/baselines/BASELINE_RECORD.md`; discriminated analysis at `6b0038d3`).** Five runs, no map instruction beyond the repo's `CLAUDE.md` entrypoint.

- **All five read source BEFORE the map. All five read the map.** Orientation **0/5**. Use **4/4**. Citation **4/5**.
- **The map is a confirmation step, not an orientation step.** A canonical entrypoint in an auto-loaded `CLAUDE.md` does **not** produce map-first orientation.
- **ZERO skill invocations across all five runs** — the corpus was offered and declined. Filed as **#331**.
- Tommy's confound was **tested, not assumed**: no run followed the bootstrap reading list at all. **The deficiency is ORDER — not motivation, discoverability, or availability.**
- Run lengths 10–61 tool calls.

**PRE-B (merged `6774181`, record fix `1689597`; artifacts under `.agent-work/epic-298/preb/`).** Five runs with **`constellation-commander` explicitly invoked**, because #331 showed an ordinary brief never loads the corpus at all.

- Run lengths **96–148** tool calls. **Only the boolean `map_before_src` transfers between arms — never raw indices.** PRE-B pairs with POST. **PRE-B does NOT pair with PRE-A.**
- **5/5 headless with no stalls**, which also contradicted `constellation-commander`'s own description claiming it cannot take a delegated dispatch (**#356**).

## What changed, and why the arm is runnable now

**#304 merged (`5d2585b`, post-archive `9a0cb17`): the Commander spine template now anchors `tasks.context.imperative` to resolve and read the map input BEFORE opening any source file, plus a new `c2` orientation gate.**

**And it had not been delivered.** Until 2026-08-02 the *installed* corpus carried **zero** occurrences of `map_orient` and no `map_orient.py` at all — merged, tested, reviewed, and unreachable by any agent, because the global corpus shadows the project copy (**#344**). **An arm run against that corpus would have returned a null attributable to the contract when the true cause was non-delivery — a false negative by construction, and the second such arm this epic (#331 was the first).**

Tommy authorised the fix and it is done: corpus installed at user scope from a clean `origin/main` worktree, fingerprints at `.agent-work/epic-298/baselines/CORPUS_FINGERPRINT_{PRE,POST}_INSTALL.json`. **Re-installs are now standing pre-cleared** — *"you are clear for any other future re-installs, do it when its convenient for us"*. **That clearance covers the install ONLY, never `--wire-hooks`; `settings.json` is his and stays untouched.**

**Live confirmation, unprompted:** `commander-308`, dispatched after the install, reported `map_orient` returning **DEGRADED-NO-MAP** in this repo. The contract is now reachable and firing.

## Pre-registered discrimination — fix this BEFORE you run anything

The three-way call is pre-registered on #307 and you inherit it:

| verdict | meaning |
|---|---|
| **sufficient** | the contract moves orientation order |
| **insufficient** | the contract is loaded and orientation order does not move |
| **irrelevant** | the contract never reached the agent, so the arm says nothing about it |

**The whole value of the arm is telling these apart.** A null that cannot distinguish *insufficient* from *irrelevant* is not a result.

**MANDATORY per-run treatment verification.** Confirm from the transcript that the Commander skill actually loaded — Claude Code emits a `Base directory for this skill:` line. **A run without a verified Commander load is a FAILED CAPTURE, not a data point.** Report failed captures; never quietly drop them.

**Re-fingerprint the corpus before and after the arm** and record both. The arm must be able to prove which corpus it measured rather than assert it.

## REUSE PRE-B's INSTRUMENTS — do not rebuild them

`.agent-work/epic-298/preb/` carries **125 files**, verified present on `origin/main` and in your worktree, including:

- `capture_preb.py` — the arm runner
- `discriminate.py` — the three-way discrimination
- `fingerprint_global_corpus.py` — corpus identity
- `build_grader_packet.py`, `GRADER_PACKET-PREB.md`, `PREB_RECORD.md`
- `corpus-fingerprint-{BEFORE,AFTER}.json`

**POST pairs with PRE-B, so POST must be measured BY THE SAME INSTRUMENT.** Rebuilding a scorer is a confound: a difference between arms then has two candidate causes — the treatment, or your new code — and the arm cannot tell them apart. **Read these first and adapt rather than reimplement.** If an instrument genuinely cannot be reused, **say why in writing before you run**, not after.

Baseline instruments live alongside at `.agent-work/epic-298/baselines/` (`capture_baseline.py`, `extract_ordering.py`, `RUBRIC.md`, `GRADER_PACKET.md`, `ADDENDUM-discriminated-analysis.md`). **`RUBRIC.md` is the scoring contract — a run scored against a rubric you wrote yourself is not comparable to either prior arm.**

## Method requirements

- **POST runs on `constellation-commander`, matching PRE-B.** Ruled; re-capture of PRE-B was declined.
- **Explicitly invoke the Commander.** #331 is settled: an ordinary brief declines the corpus. Tommy's ruling — *"we should explicitly be calling commander in these tests"* — is binding, and it is also why PRE-B is the pairing arm.
- **Score `map_before_src` as a boolean per run.** Run lengths differ by an order of magnitude between arms; raw indices are not comparable and using them is a defect.
- **Distinguish orientation from use from citation** — PRE-A's discriminated analysis (0/5, 4/4, 4/5) exists precisely because collapsing them hides the finding.
- **The degraded path is a different question.** f1Brainz has a map; this repo does not. Do not mix them.

## Rules earned this epic — these bind you

1. **Sort by what survives your death: PUSH → FILE → gates → PR.** Unpushed commits and unfiled findings do not survive you; engine state does. **Three commanders died mid-gate on #305 and only committed, pushed, or filed work reached the Admiral.**
2. **Issue filing is REQUIRED, not permitted.** File findings directly; never bank them worktree-locally.
3. **Bind per-blob, never per-tree.** `.agent-work/` commits change the tree without touching a source blob.
4. **Pin every number in prose to a revision, and at PR time to the PR number** — this repo squash-merges, so SHAs stop existing in `main`.
5. **Assert against behaviour, never against text describing behaviour.**
6. **Any guard that loops must assert what it looped over.** The Admiral committed this defect three times in one day; a comparison that iterates the wrong set reports clean without enumerating the interesting items.
7. **A measured negative is a complete, successful deliverable.** Say so plainly. **An honest null here is the epic's most valuable possible output** — but only if it discriminates among the three verdicts above.

## Stop conditions

- **Do NOT merge.** Declare the branch **FINAL** or **PENDING** (#338) and hand the merge up. `gh pr checks` can exit 0 on a *pending* check — the status must read `pass`.
- **Tell the Admiral BEFORE committing to a handoff decision.** Stopping at a clean gate boundary with runway left is correct; five commanders did it this epic and every one was right.
- **Report failed captures and corpus fingerprints even if the arm is inconclusive.**
- **If anything in this order fails against the tree, say so plainly and proceed on what the tree shows.** Nine Admiral claims failed that way this epic; every one was caught by the commander it was handed to. **Trust the tree.**

## Working notes

`notes-<n>.md` — the harness `Write` tool refuses the basename `findings-<n>.md`.

**Interpreter:** `python` (3.14.3, has pytest). `py` is 3.12.13 with **no pytest** and silently reads as a green suite. Neither local interpreter reproduces CI; gate on the CI exit status text.
