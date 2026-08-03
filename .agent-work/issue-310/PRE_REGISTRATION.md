# Pre-registration — issue #310, B2 gate (a)

**Committed BEFORE the trend instrument exists and before any surface number is measured.**
This is #307's discipline, inherited deliberately: a discrimination named after the numbers arrive is
not a discrimination. Tamper-evidence is git — this file's commit is an ancestor of the walker's.

Authored by `commander-310` at the `plan` gate, worktree `C:/Programs/constellation-skills-wt/e298-310`,
branch `epic-298/310`, HEAD at authoring time **`c60f0ad`**.

---

## 0. What is already known, so it cannot later be presented as a finding

Stated up front so nothing below can be laundered into a discovery:

- `skills/commander/SKILL.md` is **16 lines, 0 occurrences of "map"** at `cfa2c40` and at `c60f0ad`.
- #304's two tripwired deletions removed **172 words** (86 + 86); the corpus moved **−168** words
  (63,849 → 63,681). Published in `TREND_SNAPSHOT.md` §3.
- Both of those deletions landed in `COMMANDER_SPINE.template.json` and `EXECUTE_PLAN.template.json` —
  **both under `templates/`**, i.e. the conditionally-loaded bin.
- The corpus is **19 skills** (`_shared` is not one, per `install_constellation.py:245`).
- `scripts/curate_corpus.py:49-50` carries `SKILL_WORD_TARGET = 400` and `SKILL_LINE_HARD_FLAG = 500`.

## 1. The bin definitions, fixed now (Admiral ruling, not a discovered contract)

- **always-loaded** = that commit's `SKILL.md` + every `references/<file>` token that `SKILL.md` names,
  resolved role-locally first, then through **that commit's own** `SKILL_REFERENCE_BUNDLES`
  (`scripts/install_constellation.py`).
- **conditionally-loaded** = `templates/`, `scripts/`, and any `references/` file the `SKILL.md` does
  **not** name.

**This is a RECONSTRUCTION, not a discovered contract. Nothing in the tree declares one.** It is the
**Admiral's** ruling inside a delegated measurement mission — attributed so a reader knows who to argue
with. The two bins are **never summed by the instrument**; the recombination arithmetic is published so a
reader who rejects this bin can re-derive from the columns **without a re-run**.

## 2. The hypotheses, named before measurement

**H1 (the load-bearing one — from candidate B's §2e).**
*Deletion pressure in this corpus lands predominantly on the **conditionally-loaded** bin, not the
always-loaded bin.*
- **Confirmed if** the gross bytes deleted from `templates/` + `scripts/` + unnamed `references/`
  materially exceed those deleted from `SKILL.md` + named `references/`, across the census.
- **Falsified if** always-loaded deletions are comparable or larger.
- **Why it matters, stated before the answer:** if H1 holds, then *"keep deleting"* has been reducing a
  surface B2 was never worried about, and the observed deletion events do **not** license the inference
  that deletion pressure is shrinking the always-loaded role surface. **This is the finding most likely
  to decide gate (a), in either direction.**

**H2.** *The always-loaded surface has grown, not shrunk, over the corpus's life, despite the commander's
own `SKILL.md` shrinking 107 → 16 lines.*
- **Confirmed if** total always-loaded bytes at HEAD exceed those at the first comparable revision.
- **Falsified if** it is flat or down.
- **Pre-committed caveat:** role *births* inflate this trivially. Per-role trajectories and a per-role
  mean are reported alongside the total, and a role's **death is never counted as deletion pressure**.

**H3.** *Which role is "biggest" — and therefore whether any given threshold is breached — depends on the
unit chosen (bytes vs lines), and no unit has been chosen anywhere in the corpus.*
- Already partially observed at `c60f0ad`: by **lines** the max is `docent` (143); by **bytes** it is
  `admiral` (17,214, at only 77 lines). `docent` is 5th by bytes. **The rank order reverses.**
- **Confirmed if** the reversal persists across the census. **Falsified if** it is an artifact of one
  revision.

## 3. Outcome mapping, fixed BEFORE the numbers (this is the anti-laundering commitment)

Per the confirmed spec (line 77), gates (a) and (b) are **conjunctive**, and **(a) is decisive in the
negative**. Committing now to which reading selects which outcome:

**`break-proceeds` is NOT SELECTABLE by this run, and that is established by logic, not by the numbers.**
Gates (a) and (b) are conjunctive; gate (b) was not run and, per §5 below, has **n = 0**. A conjunction
with an unrun conjunct cannot be satisfied. **The three-outcome frame therefore resolves, for this run,
to a two-way call** between `not-yet-earned` and `deletion-pressure-suffices`. No fourth label is
invented to paper over the foreclosed third — this is simply what the conjunction permits. Stated here,
in advance, rather than discovered at the verdict: dangling an unreachable outcome is exactly the silent
relaxation that makes a verdict unattributable.

**Selection table — the criterion distinguishing outcomes (1) and (2), fixed before any number:**

| # | if | then |
|---|---|---|
| R1 | NARROW always-loaded **decreases** over the window, **and** enumerated deletion events land **on the always-loaded bin** | `deletion-pressure-suffices` |
| R2 | NARROW always-loaded **increases or is flat**, **and** deletion events land predominantly on the **conditionally-loaded** bin (H1 holds) | **`not-yet-earned`** — (a) leans *away* from "deletion suffices", but (b) is unrun, so the break cannot be earned; this is the row that says *the ablation arm is the thing that would settle it* |
| R3 | **n is too small, or the change is smaller than routine edit churn, to distinguish R1 from R2** | **`not-yet-earned`** |
| R4 | NARROW and WIDE definitions **select different rows** | **`not-yet-earned`** — the disagreement *is* the finding |
| R5 | no threshold can be supplied for "small enough" | **`not-yet-earned`** — an unadjudicable gate has not been adjudicated |

**R3 and R5 are the pre-committed defaults, and they are committed now precisely because they are the
outcomes an agent would be tempted to escape later.** Naming them in advance is what stops the census
from being read backwards into whichever verdict the numbers seem to flatter.

**Already-known facts bearing on R3, recorded before the census runs.** Verified independently by this
Commander against `origin/main`, and separately by the Admiral at `ecce75c`:

NARROW always-loaded moved **15,831 → 15,858 words (+27, +0.17%)**; corpus **63,681 → 63,781 (+100)**;
`SKILL.md` count unchanged at **19**. **Reported gross against gross, never net:** the net +100 already
contains the epic's deliberate **172-word** tripwired deletion, so gross growth was **≈272 words**.
***The corpus grew despite the deletion.***

**And n itself is not cleanly definable — which is a finding, not a nuisance.** Measured:

```
git merge-base --is-ancestor baseline/304-trend-snapshot origin/main   -> FALSE (not an ancestor)
merge-base(baseline, origin/main)                                     =  8de2faa
baseline..origin/main            -- skills/                           ->  3
8de2faa..origin/main             -- skills/                           ->  3   (5d2585b, 9a0cb17, a4934cb)
```

The baseline revision **is not an ancestor of `main`** — #304 squash-merged, putting the revision the
baseline was measured *inside* off the line. So **n is 2 or 3 depending on a judgement call about whether
`5d2585b`, #304's own squash-merge, counts as a change since a baseline taken mid-flight within it.**
**Neither number is defensible without saying that, and this run picks neither silently.** Both are far
below any plausible threshold of discriminability, so the ambiguity does not change the verdict — but it
demonstrates something the tidy number would hide: **this corpus cannot currently express a clean
measurement interval across a squash-merged boundary at all.** That is a second, independent consequence
of squash-merge on measurement.

Whether n≈3 at +0.17% can distinguish R1 from R2 is itself a **required finding**, not an assumption.

## 3a. Terminology, banned and required (M3)

The bare term **"always-loaded" is BANNED** in every artifact this run produces. Two definitions are in
play and they must never share a label:

- **NARROW-ALWAYS-LOADED** = `skills/*/SKILL.md` only. This is the **#304 series' definition** and it is
  the **verdict's primary number**, because comparability with the declared baseline is what makes this
  run a successor rather than a second baseline.
- **WIDE-ALWAYS-LOADED** = `SKILL.md` + named `references/` + bundled `_shared` per
  `SKILL_REFERENCE_BUNDLES`. This run's convention (the Admiral's reconstruction). A **supplement**.

**If NARROW and WIDE select different rows of the table above, that disagreement IS the finding and
forces `not-yet-earned` (R4).** Publishing recombination arithmetic solves *recombination*; it does not
solve *selection*. Both must be published and the outcome named under each.

## 4. What would make this arm a FAILED CAPTURE rather than a datapoint

Applied **blind** and stated before any result, per #307's void discipline:

- The walker cannot reproduce `TREND_SNAPSHOT` §1's published figures at `baseline/304-trend-snapshot`
  (19 `SKILL.md`, 15,831 words, 100 files, 63,681 words) → **the instrument is wrong; the series is void**,
  regardless of how plausible its curve looks.
- The reviewer's independent hand-recomputation (≥2 panel revisions, by `git show`, **without running the
  instrument**) disagrees with the instrument → **void**, and the disagreement is reported, not resolved
  by re-running the instrument until it agrees.
- Running the instrument twice at the same HEAD is not byte-identical → **void** (non-determinism).

**A void set is preserved and reported, never deleted.** These criteria are outcome-independent: each is
a fact about instrument correctness and says nothing about which of the three outcomes the data favours.

## 5. What this arm CANNOT establish, committed now so it is not overclaimed later

- **Gate (b) has n = 0. Not "weak evidence" — NO evidence.** This corrects an earlier framing in this
  run's own problem statement and an instruction from the Admiral, both of which proposed treating this
  epic's refresh / cold-start relaunches as observational gate-(b) data. They are not. **Every relaunched
  agent held the full monolith**, so those runs hold the always-loaded surface *constant*. The defect is
  not a missing control arm — **the treatment was never varied.** They bound Assumption 1 (artifacts
  carry state between steps) and contribute **zero** to the kernel-vs-monolith comparison. The verdict is
  forbidden from entering any relaunch count in the (b) column.
- **The claim "a competence arm is impossible" is WITHDRAWN as overstated.** An **ablation** arm — run
  one representative mid-spine step with sections of today's monolith *withheld* versus full — varies the
  treatment and requires **zero authoring of a decomposition**. It is not run here for **runway**, not
  for impossibility. The concrete cost estimate and the reason for declining are recorded in the
  competence document so the decline is **attributable rather than asserted-impossible**, and the arm is
  filed as an issue.
- **It cannot answer "small enough".** No threshold exists. 184 reproducible rows is still zero
  threshold, and a mechanically rigorous curve must not read as though it settled the gate.
- **It measures the CONTENT axis's premise, not the content axis.** The commander is already split on
  the **mode** axis (`1e8043a`/#107). Nothing here tests a kernel+fragments decomposition, because none
  exists.
- **The census is a per-PR series, not a per-edit series** — this repo squash-merges, so intra-PR
  grow-then-shrink is invisible.
- **Full history is not one comparable series.** `SKILL_REFERENCE_BUNDLES` and `_shared/` do not exist
  before the regime boundary; earlier rows have an **undefined**, not zero, bundled component.
- **The full-history design relocates the hand-chosen judgement rather than removing it** — from
  revision-choice to **role-lineage**-choice. The lineage table is hand-authored. Said here, and to be
  repeated where a reader will see it, not buried in a methods appendix.
