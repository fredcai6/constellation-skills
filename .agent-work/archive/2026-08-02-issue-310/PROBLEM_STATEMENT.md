# Problem statement — issue #310, B2 gate evaluation

**Reconciled against `LAUNCH_ORDER-310.md` (frozen principal), the issue body, the Admiral's
2026-08-02 comment on #310, and the confirmed spec
`.agent-work/archive/2026-07-31-explore-grander-scale/DESIGN_SPEC.md`.**
Measured in worktree `C:/Programs/constellation-skills-wt/e298-310`, branch `epic-298/310`,
at **`dbd5414`** unless another revision is named.

## State the limitation FIRST

1. **This repo carries no architecture map.** All three map candidates are absent
   (`docs/architecture/generated/map.json`, `docs/architecture/index.md`, `docs/architecture/`).
   The orientation receipt is `DEGRADED-NO-MAP`, discharged at `.agent-work/issue-310/map-orientation.json`
   with four substitutes, an unmapped statement, and an escalation. **Every structural number below is
   derived from the filesystem at a named revision, not read off a map.**
2. **"Always-loaded" is not recorded anywhere in the tree.** It is a property of how the harness loads
   a skill, established empirically by #393, not asserted by any artifact. My operational definition
   (below) is therefore a *stated convention*, and I report the conditionally-loaded surface separately
   so a reader who disagrees with the convention can recombine the numbers.
3. **Gate (b) — the role-competence test — cannot be run experimentally in this run.** Testing
   "kernel + fragments" requires a kernel+fragments decomposition to exist, and none does. Building it
   *is* the break. This is a genuine chicken-and-egg in the gate as specified, not a shortfall of effort.
   What is available instead is **observational** evidence, named as such.

## What B2 actually asks (verbatim from the confirmed spec, line 77)

> The break proceeds only if **(a)** the corpus-size trend from git shows deletion alone is not getting the
> always-loaded role surface small enough, and **(b)** a role-competence test shows an agent operating from
> kernel-plus-fragments-plus-artifacts completes a representative mid-spine step as correctly as one holding
> the monolith. **If deletion alone suffices, the break is not taken — that outcome is success, not failure.**

Two consequences that govern this whole run:

- **(a) and (b) are conjunctive, and (a) is decisive in the negative.** If the trend shows deletion *is*
  getting the always-loaded role surface small enough, the break is not taken **regardless of (b)**.
  Gate (a) is the cheap one and it can settle the question on its own.
- **The spec never defines "small enough".** Critic finding S2 in the same document says so explicitly:
  *"No size measurement, no failure attributable to skill size, no threshold at which the current shape
  stops working."* The EDIT that restaged B2 added the gate but **did not add a threshold**. This is
  carried forward as the run's central finding, not resolved by inventing one — see "Escalation" below.

## The two axes — say which one you measured

- **Mode axis (already split).** `1e8043a` (#107) — verified against the tree: `skills/commander/SKILL.md`
  went from 107 lines to a stub (−102/+5), `skills/commander-delegated/SKILL.md` was added (18 lines), and
  `skills/commander/references/commander-core.md` was added (121 lines). Eight files changed.
- **Content axis (what B2 proposes).** Kernel + just-in-time fragments selected by the active spine node.
  **Not started.** No fragment directory, no projection generator, no selector.

Reporting the mode split as satisfying B2 would be wrong. Reporting B2 as unstarted work on a monolith
would also be wrong — the always-loaded surface is already small. Both readings are refused.

## Operational definitions (stated before any number)

| Bin | Definition | Rationale |
|---|---|---|
| **always-loaded** | a role's `SKILL.md` + every `references/*.md` that `SKILL.md` names by path | #393: the harness loads the skill body; named references are what a compliant agent reads at its context step |
| **conditionally-loaded** | `templates/`, `scripts/`, and any `references/` file **not** named by `SKILL.md` | loads on materialization / dispatch, not at skill load |

Counted in **lines** and **bytes**, both reported. Bytes are primary (line counts hide CRLF and long-line
changes); lines are secondary because they are what a human reads.

## Order-vs-tree reconciliation (rule: trust the tree, say so plainly)

| Order's claim | Tree at the revision named | Verdict |
|---|---|---|
| `skills/commander/SKILL.md` is 16 lines, 0 × "map" | 16 lines, 0 hits at `cfa2c40` **and** at `dbd5414` | **HOLDS** |
| spine `context` imperative 2,210 chars / 9 × map | **2,198** chars / **9** map at `cfa2c40` | **map count exact; char count off by 12** |
| spine `plan` imperative 3,393 chars / 11 × map | **3,377** chars / **11** map at `cfa2c40` | **map count exact; char count off by 16** |
| `1e8043a` split commander by mode | verified, 8 files | **HOLDS** |
| #307 and #308 must land first | #307 CLOSED (PR #398 MERGED); #308 merged as `a4934cb` (PR #407) | **HOLDS** |

The char-count deltas are ≈0.5% and are consistent with the order having counted the **JSON-escaped**
form of the imperative (`\u2014` is 6 characters escaped, 1 decoded) where I count the **decoded** string.
The substantive claim — the map contract lives only in per-task imperatives — is unaffected, and the
map-occurrence counts match exactly. **I proceed on the decoded counts and label them as such.**

One thing the order did not carry, found while checking it: the `context` imperative **shrank**
2,198 → 1,926 chars (−272, −12.4%) between `cfa2c40` and `dbd5414`. That is a deletion event inside the
window this gate is supposed to measure.

## What this run will produce

**Gate (a) — trends. Fully deliverable.**
- corpus size over time at named revisions;
- per-role **always-loaded** surface over time, all roles enumerated **with the count asserted**;
- per-role **conditionally-loaded** surface over time, reported separately;
- deletion events attributable to B1/tripwired deletion, counted.

**Gate (b) — role-competence. Observational only, and labelled so.**
The controlled paired arm is out of reach (limitation 3 above). What *is* available is the epic's own
field record of the mechanism that already implements "an agent operating from artifacts alone":
the **refresh / job-file-not-agent-file relaunch** — a *fresh* agent cold-started from `current` alone,
mid-spine, with no handoff document and no memory of the run. That is Assumption 1 running in production.
Every such relaunch in this epic is a datapoint on artifact-sufficiency. It is **observational, uncontrolled,
and has no monolith arm to compare against** — it can support "artifacts were sufficient here", never
"as correctly as one holding the monolith".

**Verdict shape.** One of the three named outcomes, with the evidence that selects it. Assembled, not ruled.

## Escalation to the Admiral (taken up, not resolved here)

**The gate as written cannot be adjudicated on its own terms, because "small enough" was never defined.**
I can report the trend precisely. I cannot rule whether the resulting number is "small enough" without
inventing the threshold the spec's own critic (S2) flagged as missing — and rule 9 of my launch order
forbids exactly that kind of self-granted verdict. I will therefore report the trend, state what a
threshold would have to look like for each of the three outcomes to follow, and hand the threshold choice
to Tommy along with the break decision. Flagging now rather than at review.

## Out of scope

Authoring any kernel/fragment decomposition; changing any role skill; defining the threshold; making the
break decision; merging.
