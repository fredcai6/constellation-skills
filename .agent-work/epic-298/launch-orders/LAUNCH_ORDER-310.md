# Launch Order: `commander-310 — issue #310, B2 gate evaluation`

You start cold. Everything below is pasted, not pointed at.

**This issue is HITL and the decision is architectural.** You assemble evidence. **Tommy makes the kernel-break call.** Do not self-adjudicate it, and do not present one reading where the evidence supports two.

## Read this first: THREE outcomes are success, and two of them are "no"

This gate is built so that **not breaking the kernel is a win**, not a shortfall. Explicitly, from the issue:

- **"Not yet earned — keep deleting, re-evaluate in a follow-on."** If deletion-trend data is thin (cut 1 produces few deletion events), **the gate concluding *insufficient evidence* is the staging working, not a failure.**
- **"Deletion pressure alone suffices."** If so, **NOT taking the break is success.**
- **The break proceeds.** Then a human-readable whole-role projection is a **required view**, and the break gets its own cut.

**Do not treat a "no" as a null you need to apologise for, and do not go looking for a reason to say yes.** An honest *insufficient evidence* delivered early is worth more than a laboured yes. **The one outcome that is a failure is an unattributable verdict** — a conclusion that cannot say which of the three it is.

## Evidence that arrived AFTER this order was drafted — read it before you plan

**#307 closed with a PASS verdict, and its result bears on your gate.** Pasted, not pointed at.

**Measured on the corpus at `cfa2c40`:**

| surface | size | occurrences of "map" |
|---|---|---|
| `skills/commander/SKILL.md` (always-loaded) | **16 lines** | **0** |
| spine template, `context` imperative | 2,210 chars | 9 |
| spine template, `plan` imperative | 3,393 chars | 11 |
| spine template, `understand` + `reconcile` | ~1,500 chars | 6 |

The #304 map-first contract exists **only** in per-task spine imperatives. It is absent from the always-loaded skill text entirely. **And it moved the number: `map_before_src` went 0/4 → 4/4.** The PRE arm was not map-deprived — the map was present, cited in the repo's auto-loaded `CLAUDE.md`, read in 4/4 runs and useful — and still scored **0/5 on orientation order.** Whole-doctrine always-loaded delivery did not move it; **per-task delivery at the moment the task fires did.**

**This is one measured datapoint in favour of the fragment thesis, and you must carry BOTH bounds on it:**

1. **It measures *placement*, not *decomposition*.** One contract moved to a per-task slot is not a role broken into a kernel plus fragments. Suggestive, not proof.
2. **The commander is ALREADY split — on a different axis.** `1e8043a` (#107) split it by **mode**: `constellation-commander` (live human, 16-line `SKILL.md`) and `constellation-commander-delegated`, both over a mode-neutral `references/commander-core.md`. **B2 proposes a split by *content*.** Do not report the mode split as though it satisfies B2, and do not report B2 as unstarted work on a monolith — the always-loaded surface is already small. **Say which axis you measured.**
3. **The manipulation behind the 0/4→4/4 was 8 days and +31 files, not #304 alone.** Containment proven, exclusivity not.

**Do not let this evidence tilt you toward yes.** The three-outcome framing above is unchanged, and *"deletion pressure alone suffices"* is still a win. What this evidence changes is that the gate now has a **direct signal** where it previously had none — use it to make the verdict *attributable*, not to make it positive.

## The two evidence gates

**1. Trends — cheap and mechanical, from git history.**
- **Corpus size** over time.
- **Per-role always-loaded surface** over time.

**A hard-won caveat that changes what you measure — #393, found in this epic:** *always-loaded* is not the same as *installed*. `constellation-commander/SKILL.md` contains **zero occurrences of the word "map"**; the #304 map contract lives **only** in `COMMANDER_SPINE.template.json`. So a role's **always-loaded surface is its `SKILL.md` plus whatever `references/` it names** — templates and scripts load **conditionally, on materialization**. **Measure those separately and say which you measured.** Conflating them overstates the always-loaded surface by everything a spine template carries.

**2. Role-competence test** — an agent operating from **kernel + fragments + artifacts** versus the **monolith**, on a representative **mid-spine** step. This exercises Assumption 1.

**This is a measurement arm. Reuse #307's discipline; do not reinvent it.** `.agent-work/epic-298/post/` and `.agent-work/epic-298/preb/` carry working instruments (`capture_preb.py`, `discriminate.py`, `verify_treatment.py`, `fingerprint_global_corpus.py`) and, more importantly, the **method** that made #307's result defensible:

- **Pre-register the discrimination BEFORE any number exists, and commit it.** #307's pre-registration (`a4993ec`) was committed while captures were in flight and it called two ways the result could have been laundered before they arose.
- **Verify treatment per run.** A run where the intended condition did not actually reach the agent is a **FAILED CAPTURE, not a data point**. Report failed captures; **never quietly drop one** — a silently dropped failed capture is how "it didn't work" gets laundered out of "it never arrived".
- **Assert delivery against BYTES, not an installer's marker.** #393 exists because `TREATMENT-VERIFIED` proved only that the skill loaded — hop 0 of three.
- **A void criterion must be INDEPENDENT OF THE OUTCOME and applied BLIND.** #307 voided a whole capture set on *two distinct `session_id`s in one transcript* — a fact about process identity that says nothing about the result. **Preserve any void set rather than deleting it.**
- **Metadata about an artifact is not the artifact.** `exit=0` and a plausible elapsed time are exactly what a doubled run looks like.

## Rules earned this epic — these bind you

1. **Sort by what survives your death: PUSH → FILE → gates → PR.** Unpushed commits and unfiled findings do not survive you; engine state does. **Three commanders died mid-gate on #305; only committed, pushed, or filed work reached the Admiral. Commit at every gate.**
2. **Issue filing is REQUIRED, not permitted.** File findings directly; never bank them worktree-locally.
3. **Assert what you looped over.** An under-inclusive enumeration presented as complete has bitten this epic **three times**, twice inside one hour by an agent who had just written down that it recurs. **When you enumerate — files, roles, commits — assert the count.**
4. **Bind per-blob, never per-tree.** `.agent-work/` commits change the tree without touching a source blob.
5. **Pin every number in prose to a revision, and at PR time to the PR number** — this repo squash-merges, so SHAs stop existing in `main`.
6. **Assert against behaviour, never against text describing behaviour.**
7. **State your limitation FIRST, not in a footnote.** #307's arm is trustworthy because it opened with *"the manipulation is 8 days and +31 files, not #304 alone"*. **An arm that overstates its own manipulation is worth less than one that bounds it.**
8. **Pin a claim to the revision you measured it at, or it outlives its subject.** The Admiral wrote *"delivery is broken"* into this epic's routing ledger, then went on asserting it after the thing it described had been fixed — a state observed once and carried as a permanent property. **Your trend measurement is nothing but a sequence of such reads; every number you report must name the revision it came from.**
9. **You do not get to rule that a finding earned its place.** The Admiral wrote *"doctrine that earned promotion — graduate"* into the same ledger and had to retract it: naming a verdict pre-empts the mechanism meant to make it. **The same applies to you and the kernel break — assemble evidence, name the three outcomes, and let Tommy rule.**

## Stop conditions

- **Do NOT merge.** Declare **FINAL** or **PENDING** (#338) and hand the merge up. **Open the PR even if the work is unfinished** — CI does not run on an unopened branch, and a branch whose CI has never run is the exposure that cost #305 a stranded-commit recovery.
- `gh pr checks` can exit **0 on a PENDING check** — the status must read `pass`.
- **Tell the Admiral BEFORE committing to a handoff decision.** Stopping at a clean gate boundary with runway left is correct; six commanders did it this epic and every one was right.
- **If anything in this order fails against the tree, say so plainly and proceed on what the tree shows.** Ten Admiral claims failed that way this epic; every one was caught by the commander it was handed to. **Trust the tree.**

## Working notes

`notes-<n>.md` — the harness `Write` tool refuses the basename `findings-<n>.md`.

**Interpreter:** `python` (3.14.x, has pytest). **`py` is 3.12.13 with NO pytest — under the PowerShell tool it silently no-ops and reads as a green suite.** Neither local interpreter reproduces CI; gate on the CI status text.

## Dependencies

**#307 and #308 must land first.** #307 supplies the measurement method and the map-first verdict; #308 supplies the episode store's post-migration state, which is part of what the trend measurement counts.
