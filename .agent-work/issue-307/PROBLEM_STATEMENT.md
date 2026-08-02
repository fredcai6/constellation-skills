# Problem statement — issue #307, POST arm of the epic-298 map-first measurement

Reconciled against the frozen `LAUNCH_ORDER-307.md`, not interrogated from a human. No human
is reachable; the Admiral (`team-lead`) is the escalation path.

## The question

**Does the map-first contract change the ORDER in which an agent orients?** Not whether the
map is read, is useful, or is cited — the baseline settled all three. **Order.**

Tommy's framing, which is the whole issue: *"There's a gulf between saying 'there is a map'
and 'use the map first to orient yourself'."*

## What is already known, and therefore what this arm must NOT re-litigate

- **PRE-A (#299)** — corpus offered, never invoked. Orientation 0/5, use 4/4, citation 4/5.
  Zero skill invocations (#331). Run lengths 10–61.
- **PRE-B (#306)** — Commander explicitly loaded, 5/5 `TREATMENT-VERIFIED`. `map_before_src`
  **false on 4 of 4 runs that read source**; #716 read neither map nor source. Run lengths
  96–148. Corpus `74953936`, pre-#304.
- **PRE-B pairs with POST. PRE-A does not.** Only the boolean `map_before_src` transfers.

PRE-B's own diagnosis, and the thing this arm tests: the pre-#304 map-first imperative was
anchored to *"before authoring `execute.json`"* — an artifact authored at the END of a long
run — so a run could crawl source for fifty calls, read the map afterwards, and comply
exactly. **#304 re-anchors it to "before you open any source file," at the `context` step.**

## Baseline verified against the tree BEFORE planning

Per `lesson:verify-launch-order-claims-against-code`, every load-bearing launch-order claim
was checked against the tree first. Results, including the failures:

| claim | verdict |
|---|---|
| `.agent-work/epic-298/preb/` instruments present | **HELD** |
| `.agent-work/epic-298/baselines/` present | **HELD** |
| `map_orient.py` in the *installed* corpus (#344 delivered) | **HELD** — and it *runs* |
| the #304 contract is reachable and fires | **HELD** — `DEGRADED-NO-MAP` reproduced here |
| corpus fingerprints at `baselines/CORPUS_FINGERPRINT_{PRE,POST}_INSTALL.json` | **FAILED — both files are absent from the entire `.agent-work/` tree** |
| PRE-B's pinned worktrees `C:/Programs/f1bwt/` | **FAILED — absent, swept after PRE-B; recreated** |

Neither failure blocks the arm. The fingerprint gap is repaired by taking the arm's own
BEFORE/AFTER fingerprints, which is required independently.

## The treatment, stated as one variable

POST is PRE-B with **exactly one thing changed: the installed corpus**.

| | PRE-B | POST (this arm) |
|---|---|---|
| corpus `source_commit` | `74953936` | `3595955` |
| contains #304 (`5d2585b`) | no | **yes**, verified by `git merge-base --is-ancestor` |
| contains #304 post-archive (`9a0cb17`) | no | **yes** |
| `SKILL.md` concat sha256 | `fcb6863163c97273d021…` | `59019a4d92b999907b58…` |
| deep tree sha256 | `4c2e6465889f8d3fd074…` (233 files) | `bb66c3556dd91fcd743e…` (264 files) |
| brief bytes, argv, model, pin, task set, env scrub | — | **byte-identical** |
| scorers (`extract_ordering.py`, `verify_treatment.py`, `discriminate.py`) | — | **identical code** |

## Pre-registered three-way discrimination — fixed before any run

| verdict | meaning | what decides it |
|---|---|---|
| **sufficient** | the contract moves orientation order | `map_before_src` true on runs that read source |
| **insufficient** | the contract loaded and order did not move | treatment verified per run AND `map_before_src` still false |
| **irrelevant** | the contract never reached the agent | treatment NOT verified, or `map_orient` never invoked |

**A null that cannot separate *insufficient* from *irrelevant* is not a result.** Two arms this
epic already nulled for the wrong reason: #331 (corpus declined) and #344 (contract merged but
undelivered). Separation rests on two independent witnesses per run — `verify_treatment.py`'s
`Base directory for this skill:` line, and a `map_orient` invocation audit.

## Known measurement hazard, declared before the run

The frozen extractor's call-level corpus rule buckets any call touching `.claude/skills` as
`skill-corpus` **and nothing else**. The #304 contract is discharged by invoking
`~/.claude/skills/constellation-commander/scripts/map_orient.py` — so **the mandated act is
invisible to the frozen extractor by construction.** The extractor is not modified. Instead:

- the primary comparison stays `discriminate.py`, unchanged, on the genuine `docs/architecture/*`
  reads the contract routes the subject to *after* `map_orient` resolves;
- a **supplementary** `map_orient` invocation audit is added and run over **both** PRE-B and
  POST with the same code, so the added column is comparable rather than POST-only.

## Protected intent

**This is HITL. Tommy adjudicates the verdict.** This run compiles the paired evidence package
and presents it. It does not self-adjudicate, does not present one reading where the evidence
supports two, and reports failed captures and corpus fingerprints even if the arm is
inconclusive. **A measured negative is a complete deliverable.**

## Out of scope

- The degraded path as a subject of study — f1Brainz has a map, this repo does not; the launch
  order forbids mixing them.
- Re-capturing PRE-B on the delegated variant (declined; POST matches PRE-B on
  `constellation-commander`).
- Ruling on the rubric §2 tolerance ambiguity (#333) — Admiral/Tommy's call, and it must govern
  both arms identically.
- Merging. The branch is declared FINAL or PENDING and handed up.
