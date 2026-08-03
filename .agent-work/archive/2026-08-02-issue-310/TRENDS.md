# TRENDS — the corpus/per-role surface census (issue #310, B2 evidence gate (a))

**This is the successor to `.agent-work/archive/2026-08-02-issue-304/TREND_SNAPSHOT.md`.**
That file declared its consumer to be "the NEXT trend snapshot", due "at EPIC-298 CLOSE", and said a
successor must re-run its §1–§3 against a later commit, paste both numbers, and state the delta. That is
what this file does. Measured at `9a90298` (2026-08-02), branch `epic-298/310`.

> **This measurement feeds a decision that a human named Tommy makes.** Nothing here decides the kernel
> break, and no "small enough" threshold is invented — none exists anywhere in the corpus. Where the
> honest finding is *"that cannot be computed at this n"*, this file says so and stops.

**The headline result is a measured negative and two falsified/confirmed hypotheses**, all reproducible:

| # | question | answer |
|---|---|---|
| **H1** | does deletion land on `CONDITIONALLY-LOADED` rather than on the `NARROW`/`WIDE` bins? | **FALSIFIED** — `NARROW-ALWAYS-LOADED` absorbs the **largest** share of deletion pressure (43.9% over all history, 54.4% post-regime) |
| **H2** | has the `NARROW` surface grown over the corpus's life? | **CONFIRMED** — 1,831 → 15,858 words, and the *per-role mean* grew 305 → 835 w/role, so it is not just role births |
| **H3** | does "biggest role" depend on the unit? | **CONFIRMED for the current corpus** — `docent` is **rank 1 by lines, rank 6 by bytes**; `admiral` is **rank 4 by lines, rank 1 by bytes** |
| **(e)** | is a trend computable at all over the successor window? | **NO.** n = 2 or 3; span 22.3 h; the window's NARROW movement (**+27 w**) sits **below the 25th percentile** of routine per-interval movement (35 w) and **81%** of moving intervals moved more |

---

## 0. The blocking baseline reproduction — the external oracle

Pre-registration §4: *if the walker cannot reproduce `TREND_SNAPSHOT` §1 at `baseline/304-trend-snapshot`,
the instrument is wrong and the series is void, regardless of how plausible its curve looks.* It
reproduces, exactly, all four figures:

```
$ python .agent-work/issue-310/trends/measure_surface.py --reproduce-baseline
reproducing TREND_SNAPSHOT sec.1 at baseline/304-trend-snapshot  (= fc1685a)
  OK        skillmd_files    expected      19  measured      19
  OK        skillmd_words    expected   15831  measured   15831
  OK        corpus_files     expected     100  measured     100
  OK        corpus_words     expected   63681  measured   63681
  (per-file-sum corpus words = 63682, concatenated = 63681)
  roles = 19 (expect 19; _shared is NOT a role)
BASELINE REPRODUCED
```

**The oracle was decoyed before it was trusted.** Pointed at a different revision it exits non-zero:
`--at baseline/304-g2-approve` → `MISMATCH corpus_words expected 63681 measured 63849`, exit 1;
`--at HEAD` → `MISMATCH skillmd_words expected 15831 measured 15858`, exit 1. The fixture suite mutation-
tests the same constant (`15831` → `15832` ⇒ 1 failed, 28 passed).

**One reproduction detail, because it is a trap for the next successor.** The published **63,681** is a
*concatenated* count (`git ls-files … | xargs -0 cat | wc -w`). The **per-file sum is 63,682**. Exactly one
file at the baseline — `skills/commander/templates/COMMANDER_SPINE.template.json` — has no trailing
newline, so under `cat` its last word fuses with the next file's first. Both numbers are emitted
(`corpus.words_concatenated`, `corpus.words_per_file_sum`). A successor that sums per-file counts and
compares against 63,681 will see a spurious −1.

## 1. The three bins, and who ruled them

**The bare two-word term is BANNED in this file.** Two definitions are in play and must never share a
label. Per the pre-registration:

| bin | definition | status |
|---|---|---|
| **`NARROW-ALWAYS-LOADED`** | `skills/<role>/SKILL.md` only | **#304's own definition, and this verdict's PRIMARY number** — comparability with the declared baseline is what makes this a successor rather than a second baseline |
| **`WIDE-ALWAYS-LOADED`** | `NARROW` + every `references/<file>` token a `SKILL.md` names, resolved role-locally first, then through *that commit's own* `SKILL_REFERENCE_BUNDLES` | a **supplement**, never the primary |
| **`CONDITIONALLY-LOADED`** | `templates/`, `scripts/`, and any `references/` or `_shared/` file no `SKILL.md` names | — |

> **The WIDE bin is a RECONSTRUCTION RULED BY THE ADMIRAL, not a contract discovered in the tree —
> nothing in the tree declares one.** It is attributed here so a reader knows who to argue with.

**The instrument never sums `NARROW` and `WIDE`** (they overlap by construction). It emits three
**disjoint** columns. The recombination arithmetic, published so a reader who rejects this bin convention
re-derives **without a re-run**:

```
WIDE-EXTRA  = WIDE - NARROW                        (the named-reference part alone)
WIDE        = NARROW + WIDE-EXTRA
CORPUS      = NARROW + WIDE-EXTRA + CONDITIONALLY-LOADED
```

The partition is exact at **every one of the 187 census rows** (asserted by `--verify` step 3 and by
`test_bins_are_an_exact_partition_of_the_tracked_corpus`). So, at the two endpoints:

| | `NARROW` | `WIDE-EXTRA` | **`WIDE`** (= sum of the two left) | `CONDITIONALLY-LOADED` | corpus |
|---|---|---|---|---|---|
| `baseline/304-trend-snapshot` (`fc1685a`) | 15,831 w | 22,148 w | **37,979 w** | 25,703 w | 63,681 w |
| `HEAD` (`9a90298`) | 15,858 w | 22,148 w | **38,006 w** | 25,776 w | 63,781 w |
| **delta** | **+27** | **0** | **+27** | **+73** | **+100** |

**`NARROW` and `WIDE` do NOT select different rows of the pre-registered table** — `WIDE-EXTRA` did not
move at all in the window, so both read `+27`, same sign, same magnitude. Pre-registration row **R4 does
not fire.**

### Two consequences of the Admiral's rule a reader may reasonably reject

Both are computed, not asserted, so they can be moved with the arithmetic above and no re-run:

1. **10 unresolved reference tokens at HEAD**, all *cross-role* citations (9 roles cite workbench's
   `references/checklist-engine.md`; `commander-delegated` cites `references/commander-core.md`). The
   rule resolves role-locally then through the bundle, and neither reaches another role's `references/`.
   **This does not under-count WIDE**: all 10 targets are already in `WIDE-EXTRA` via their owning role
   (`unresolved_ref_tokens_uncovered_count = 0`, asserted by test).
2. **`_shared/windows.md` and `_shared/skill-goodness.md` land in `CONDITIONALLY-LOADED`.** The installer
   ships them into every consuming role's `references/`, but no `SKILL.md` *names* them as
   `references/<file>`, and the ruling makes naming the membership test. Their combined weight is
   recoverable from `shared_files_not_named` in the dataset.

## 2. Headline figures — every one re-derived from git by `--verify`

Machine-checked, not decorative: `measure_surface.py --verify` requires this key set to be present
**exactly** (no missing, no extra) and recomputes **each value from git**, independently of both this
document and the committed dataset. A doc containing only the right *words* fails; see §9.

```headline-figures
conditional_words@baseline/304-trend-snapshot = 25703
corpus_files@baseline/304-trend-snapshot = 100
corpus_words@baseline/304-trend-snapshot = 63681
narrow_files@baseline/304-trend-snapshot = 19
narrow_words@baseline/304-trend-snapshot = 15831
role_count@baseline/304-trend-snapshot = 19
wide_extra_files@baseline/304-trend-snapshot = 21
wide_extra_words@baseline/304-trend-snapshot = 22148
corpus_files@5d2585b = 100
corpus_words@5d2585b = 63681
narrow_words@5d2585b = 15831
conditional_words@HEAD = 25776
corpus_files@HEAD = 100
corpus_words@HEAD = 63781
narrow_files@HEAD = 19
narrow_words@HEAD = 15858
rank_by_bytes_of_admiral@HEAD = 1
rank_by_bytes_of_docent@HEAD = 6
rank_by_lines_of_admiral@HEAD = 4
rank_by_lines_of_docent@HEAD = 1
role_count@HEAD = 19
unresolved_ref_tokens@HEAD = 10
wide_extra_files@HEAD = 21
wide_extra_words@HEAD = 22148
corpus_delta_words@window = 100
deletion_events@window = 3
gross_added_words@window = 222
gross_deleted_words@window = 122
gross_deleted_words_conditional@window = 106
gross_deleted_words_narrow@window = 16
gross_deleted_words_wide_extra@window = 0
n_excluding_squash_merge@window = 2
n_including_squash_merge@window = 3
narrow_delta_words@window = 27
deletion_events@census = 234
deletion_pressure_words_conditional@census = 13303
deletion_pressure_words_narrow@census = 15973
deletion_pressure_words_wide_extra@census = 7089
gross_added_words_conditional@census = 40783
gross_added_words_narrow@census = 34124
gross_added_words_wide_extra@census = 29889
gross_deleted_words_conditional@census = 17972
gross_deleted_words_narrow@census = 20097
gross_deleted_words_wide_extra@census = 8312
intervals@census = 186
intervals_moving_narrow_at_least_as_much_as_the_window@census = 113
narrow_movement_max_words@census = 2636
narrow_movement_median_words@census = 90
narrow_movement_p25_words@census = 35
narrow_movement_p75_words@census = 258
narrow_moving_intervals@census = 139
narrow_words_first@census = 1831
narrow_words_last@census = 15858
role_births@census = 19
role_count_first@census = 6
role_count_last@census = 19
role_deaths@census = 6
role_deaths_walk_order_artifact@census = 3
rows@census = 187
panel_revisions@panel = 7
panel_revisions_with_bundled_component_undefined@panel = 2
panel_revisions_with_unit_reversal@panel = 4
```

## 3. H1 — the load-bearing hypothesis. **FALSIFIED.**

*Pre-registered claim: "deletion pressure in this corpus lands predominantly on the conditionally-loaded
bin." Pre-registered stake: if it holds, the observed deletion events do not license the inference that
deletion pressure is shrinking the role surface — "the finding most likely to decide gate (a), in either
direction."*

**It does not hold. It is falsified in the opposite direction, and by a wide margin.**

Gross words deleted, then deletion **pressure** (gross deleted minus every word attributable to a role
*leaving* — a role's death is an org change and is never deletion pressure):

| bin | gross added | gross deleted | gross bytes deleted | **deletion pressure** | share |
|---|---|---|---|---|---|
| **`NARROW-ALWAYS-LOADED`** | +34,124 w | −20,097 w | −143,146 B | **15,973 w** | **43.9%** |
| `WIDE-EXTRA` | +29,889 w | −8,312 w | −54,945 B | 7,089 w | 19.5% |
| `CONDITIONALLY-LOADED` | +40,783 w | −17,972 w | −132,624 B | 13,303 w | 36.6% |

Over the 186 intervals of the whole census. Restricted to the **109 post-regime intervals** (after
`84fd28f`, where the WIDE bin is defined at all) the falsification is **stronger**, not weaker:

| bin | gross added | gross deleted | **deletion pressure** | share |
|---|---|---|---|---|
| **`NARROW-ALWAYS-LOADED`** | +22,443 w | −12,452 w | **8,784 w** | **54.4%** |
| `WIDE-EXTRA` | +16,207 w | −4,554 w | 3,457 w | 21.4% |
| `CONDITIONALLY-LOADED` | +19,785 w | −8,132 w | 3,894 w | 24.1% |

**What this means, stated in the pre-registration's own terms.** The single deletion event that was
documented with exact arithmetic — #304's, which landed **entirely in `templates/`** — is **not
representative of this corpus's history**. Deletion in this corpus falls *hardest* on the very bin B2
worries about. So the pre-registered "if H1 holds" reading (*deletion has been reducing a surface B2 was
never worried about*) **does not apply**.

**And this does NOT rescue the opposite reading either**, which is the part it would be easy to
overclaim. Every bin's gross **added** exceeds its gross **deleted** by a large margin: `NARROW` took
+34,124 against −20,097 (a **1.70:1** add:delete ratio; post-regime **1.80:1**). Deletion is landing on
`NARROW` *and losing to growth on `NARROW`*, throughout. The corpus does not shrink; it churns while
growing.

## 4. H2 — **CONFIRMED**, including under the pre-committed caveat

*Pre-registered claim: the `NARROW` surface has grown, not shrunk, over the corpus's life, despite the
commander's own `SKILL.md` shrinking 107 → 16 lines. Pre-committed caveat: role births inflate this
trivially, so report per-role trajectories and a per-role mean, and never count a role's death as
deletion.*

| | first census row `a83a3be` (2026-05-22) | last row `9a90298` (2026-08-02) |
|---|---|---|
| roles | 6 | 19 |
| `NARROW` total | 1,831 w | 15,858 w (**8.7×**) |
| **`NARROW` per-role mean** | **305.2 w/role** | **834.6 w/role** (**2.7×**) |

**The caveat is honoured and the claim survives it**: the per-role *mean* nearly tripled, so growth is not
an artifact of the corpus going from 6 roles to 19. Role churn over the census: **19 births, 6 deaths**
(plus the 6 roles present in the first row = 25 births total, matching `--role-lineage`), and **3 of the 6
"deaths" are walk-order artifacts, not org changes at all** (§7).

**The commander's own trajectory, which is the pre-registration's counter-example, holds and is
localised**: `skills/commander/SKILL.md` is **254 w / 16 lines** at both the baseline and HEAD — the
smallest `SKILL.md` of all 19 roles — while the **whole commander role** is 9 files / **10,636 w**, still
the largest role in the corpus. *The commander did not get smaller; its always-paid `SKILL.md` did, and
the mass moved into `references/` and `templates/`.* That is a mode split (`1e8043a`/#107), not a content
reduction, and it is exactly why the NARROW/WIDE distinction had to be kept separate.

Per-role `SKILL.md` at HEAD, all 19 (descending by words):

| role | words | lines | bytes | whole role |
|---|---|---|---|---|
| admiral | 2,413 | 77 | 17,137 | 6 files, 7,718 w |
| explorer | 1,893 | 99 | 13,630 | 8 files, 5,778 w |
| lessons-auditor | 1,356 | 80 | 9,190 | 4 files, 2,221 w |
| reviewer | 1,212 | 50 | 8,304 | 4 files, 2,253 w |
| interrogator | 1,055 | 50 | 7,169 | 3 files, 1,512 w |
| commander-delegated | 1,036 | 30 | 6,875 | 1 file, 1,036 w |
| docent | 1,005 | **143** | 7,138 | 2 files, 1,219 w |
| prototyper | 911 | 61 | 5,864 | 6 files, 2,537 w |
| implementer | 874 | 38 | 5,556 | 3 files, 1,626 w |
| curator | 617 | 51 | 4,311 | 1 file, 617 w |
| triage | 526 | 43 | 3,956 | 2 files, 771 w |
| diagnose | 455 | 61 | 3,128 | 3 files, 1,011 w |
| to-issues | 451 | 36 | 2,943 | 3 files, 955 w |
| write-a-skill | 449 | 42 | 3,235 | 4 files, 989 w |
| scout | 366 | 36 | 3,045 | 4 files, 1,382 w |
| cartographer | 347 | 27 | 2,883 | 7 files, 3,786 w |
| charter | 328 | 31 | 3,210 | 15 files, 6,305 w |
| workbench | 310 | 45 | 2,744 | 9 files, 4,701 w |
| **commander** | **254** | **16** | **1,715** | **9 files, 10,636 w** |

## 5. H3 — **CONFIRMED for the current corpus**, and it is not a curiosity

*Pre-registered claim: which role is "biggest" — and therefore whether any given threshold is breached —
depends on the unit chosen, and no unit has been chosen anywhere in the corpus.*

At HEAD the rank order reverses:

| role | rank by **lines** | rank by **bytes** |
|---|---|---|
| `docent` | **1** (143 lines) | **6** (7,138 B) |
| `admiral` | **4** (77 lines) | **1** (17,137 B) |

**Persistence across the census, measured at the panel revisions: 4 of 7 show the reversal.** The verdict
is `PARTIAL`, and the split is not random — the reversal is present at **every one of the four modern
(19-role) revisions** and absent at the three earliest ones, all of which **predate `docent`'s birth**
(2026-07-07). So: *confirmed for the corpus as it stands, not claimed for all history.*

**Why this matters and is not trivia:** `scripts/curate_corpus.py` carries `SKILL_WORD_TARGET = 400` and
`SKILL_LINE_HARD_FLAG = 500` — one target in words, one flag in lines, on the same artifact, with no
stated relation. Any "is this role small enough" question inherits that ambiguity before it is even asked.

## 6. (e) Is a trend computable at all? — **required finding: NO, not over this window**

**n is genuinely ambiguous, and this run picks neither value silently.**

```
$ git merge-base --is-ancestor baseline/304-trend-snapshot HEAD   -> non-zero (NOT an ancestor)
merge-base(baseline, HEAD)                                        =  8de2faa
```

The baseline **is not an ancestor of `main`** — #304 squash-merged, putting the revision the baseline was
taken *inside* off the line. So whether `5d2585b` (#304's *own* squash-merge) counts as a change *since* a
baseline taken mid-flight *within* it is a judgement call:

- **n = 3** counting `5d2585b`, `9a0cb17`, `a4934cb`
- **n = 2** excluding `5d2585b`

**New finding that bounds the ambiguity without resolving it: it does not matter numerically, because
`5d2585b` is a ZERO-DELTA row.** Verified independently of the instrument, by tree object id:

```
$ git rev-parse baseline/304-trend-snapshot^{commit}:skills
caefc5d50466ad8da8d8728e6af274b02c39b2ab
$ git rev-parse 5d2585b:skills
caefc5d50466ad8da8d8728e6af274b02c39b2ab
$ git diff --stat baseline/304-trend-snapshot 5d2585b -- skills/
(no output)
```

The `skills/` tree is **byte-identical** at the baseline and at #304's squash-merge. The n=2-vs-3
judgement call therefore has **zero measurement consequence** — but it is still a judgement call, and it
is still true that *this corpus cannot express a clean measurement interval across a squash-merged
boundary*. That is a second, independent consequence of squash-merge on measurement, and it is
**structural**, not incidental: the number is unaffected here only by luck.

**The interval, in commits and in days:**

| | |
|---|---|
| commits touching `skills/` in the window | **3, or 2** (see above) |
| calendar span | `fc1685a` 2026-08-01 21:02:57 −0700 → `9a90298` 2026-08-02 19:21:40 −0700 = **80,323 s = 22.3 hours = 0.93 days** |
| whole census span, for contrast | 2026-05-22 → 2026-08-02 = **72.2 days**, 184 skills-touching commits |

**The smallest change the instrument can distinguish from routine edit churn — measured, not asserted.**
"Routine churn" is the distribution of per-interval `NARROW` movement over the **139 of 186 intervals in
which `NARROW` moved at all**:

| statistic | \|net `NARROW` words\| per moving interval |
|---|---|
| minimum | 2 |
| **25th percentile** | **35** |
| median | 90 |
| 75th percentile | 258 |
| maximum | 2,636 |

**The window's entire `NARROW` movement is +27 words** (gross +43 / −16, i.e. 59 words of churn).

- **+27 is below the 25th percentile (35) of a single routine interval.**
- **113 of the 139 moving intervals — 81% — moved `NARROW` by at least as much as the whole window did.**
- Gross churn tells the same story: the window's 59 words of `NARROW` churn against a median moving-
  interval churn of 156.

**Therefore: at n = 2–3 over 22 hours, with a signal an order of magnitude below one routine interval's
movement, this instrument cannot distinguish "the surface is shrinking" from "the surface is growing"
from "nothing happened."** Pre-registration row **R3 fires**. That is the required finding, and it is a
complete result, not a shortfall — the instrument's resolution is measured and stated rather than assumed.

**Scope of this null, stated explicitly.** What failed is *the successor-window trend*, n ≈ 3 over 22
hours. What did **not** fail: the census itself (187 rows over 72 days is ample for H1/H2/H3, all of which
returned decisive answers), the baseline reproduction, or the instrument. A longer window would be
computable; this one is not.

## 7. §3's analogue — the enumerated deletion-event set in the window

`TREND_SNAPSHOT` §3 recorded what the run taking the snapshot itself moved. It has no direct analogue
here, so per the handoff it is defined as **the enumerated deletion-event set in the window** — an
(interval × bin) pair with non-zero deletion pressure. **It may be empty; an empty set with its count
asserted is a complete result.** It is not empty:

**Count = 3** (asserted from the dataset field `window.deletion_event_count`, re-derived by `--verify` as
`deletion_events@window`):

| commit | date | bin | gross deleted | gross added | net |
|---|---|---|---|---|---|
| `9a0cb17` | 2026-08-01 | `CONDITIONALLY-LOADED` | 20 w | 100 w | **+80** |
| `a4934cb` | 2026-08-02 | `NARROW-ALWAYS-LOADED` | 16 w | 43 w | **+27** |
| `a4934cb` | 2026-08-02 | `CONDITIONALLY-LOADED` | 86 w | 79 w | **−7** |

**Every deletion event in this window was outweighed or nearly outweighed by addition in the same
interval and the same bin.** Corpus-wide the set has **234** members over 186 intervals.

**Role departures are reported separately and never as deletion.** Over the census: 19 births and 6
deaths within intervals; **3 of the 6 deaths are walk-order artifacts**, not org changes — a branch commit
that introduced a role can sort before a main-line commit that does not have it yet, so the role appears
to die and be reborn at the merge. The per-bin field `deleted_role_departure` lets a reader subtract
genuine departures:

```
deletion_pressure_words = deleted_words - deleted_words_role_departure
```

> **ROLE LINEAGE IS HAND-AUTHORED DATA, NOT A MEASUREMENT — and you are reading it here, not in a methods
> appendix, deliberately.** `git log --follow` is forbidden for this census, so a role *rename* is visible
> to git only as a death plus a birth. The full-history design does not remove the hand-chosen judgement
> call; it **relocates** it from revision-choice to role-lineage-choice. The table (in
> `measure_surface.py`, `ROLE_LINEAGE`) claims: `conductor` → `pilot` (`3c24f7c`, commit subject says so),
> `pilot` → `commander` (`90cf856`, "fold pilot into commander"), `crew` → `implementer` + `reviewer`
> (`a6233e6`, R-status renames), and three walk-order artifacts. **Audit it, do not trust it:**
> `--role-lineage` enumerates every birth and death (25 / 6, final 19) so the table can be checked against
> the raw list, and a test asserts the two agree.

## 8. Disagreements with numbers verified upstream — **flagged loudly, as instructed**

Four of the five figures in the handoff's Commander-verified table reproduce **exactly**. One does not,
and the disagreement is arithmetic, not measurement.

| quantity | Commander's value | this census | verdict |
|---|---|---|---|
| `NARROW` words, baseline → `origin/main` | 15,831 → **15,858** (+27) | 15,831 → 15,858 (+27) | ✅ exact |
| corpus words, baseline → `origin/main` | 63,681 → **63,781** (+100) | 63,681 → 63,781 (+100) | ✅ exact |
| `SKILL.md` count at `origin/main` | **19** | 19 | ✅ exact |
| commits touching `skills/` in window | **3** (or 2) | 3 (or 2), `5d2585b` `9a0cb17` `a4934cb` | ✅ exact |
| gross growth vs deliberate deletion, **same window** | **"≈272 gross growth against a 172-word deletion"** | **+222 gross added against −122 gross deleted** | ❌ **DISAGREES** |

*(`origin/main` = `ab7b6be` and `HEAD` = `9a90298` share the identical `skills/` tree `93aa92e`, verified
by `git rev-parse`, so measuring at HEAD **is** measuring at `origin/main`.)*

### 🚩 The disagreement, in full

**The 172-word deletion is not in the window.** It landed in the interval
`baseline/304-g2-approve` → `baseline/304-trend-snapshot` — i.e. **before the baseline was taken**. The
baseline's 63,681 is the *post-deletion* figure. So the window's net +100 does **not** "already contain"
that deletion, and the ≈272 figure (100 + 172) is a decomposition of a window the deletion never entered.

The window's own gross, measured directly per the "gross, never net" rule:

```
gross added 222 w   gross deleted 122 w   net +100 w   (= the measured corpus delta, exactly)
```

**The underlying claim in the pre-registration — *"the corpus grew despite the deletion"* — survives, and
in fact strengthens.** The corpus grew +100 net *in a window carrying 122 words of its own gross
deletion*, and separately the 172/173-word deletion in the immediately preceding interval was more than
recovered within 22 hours. Only the arithmetic used to reach the claim was wrong.

### 🚩 A second, smaller disagreement: the published gross for #304's own deletion event

Calibrating the gross measurement against the one event with published exact arithmetic:

```
$ python .agent-work/issue-310/trends/measure_surface.py --calibrate-gross
baseline/304-g2-approve (a8d9467) -> baseline/304-trend-snapshot (fc1685a)
  skills/commander/templates/COMMANDER_SPINE.template.json
    +5w -87w +32B -574B  bin=CONDITIONALLY-LOADED
  skills/commander/templates/EXECUTE_PLAN.template.json
    +0w -86w +0B -570B  bin=CONDITIONALLY-LOADED
  GROSS  +5w  -173w   net -168w
  #304 published: -172 gross deleted, +4 (a NET figure for the retarget hunk), corpus -168
  net agreement: YES
```

**This is not instrument error.** #304's `+4` is a **net** figure for the retarget hunk (`from the current
map using` → `from the map input the context step resolved, using` — 9 words in for 5 out, +4 net), while
its `172` counts only the dead-path block and omits the 1 word (`current`) the retarget removed. Gross is
**5 in / 173 out**; `5 − 173 = −168 = 4 − 172`. Both bookkeepings close on the same net. The published
event **mixed a gross deletion with a net addition** — which is precisely the failure mode this run's
"gross, never net" constraint exists to prevent, caught in the baseline this run was told to reproduce.

**What survives untouched: both deleted files are under `templates/`, i.e. entirely in
`CONDITIONALLY-LOADED`** (`NARROW` deleted 0, `WIDE-EXTRA` deleted 0). That single data point is exactly as
#304 reported it. It is simply not representative — see §3.

## 9. The pre-registered outcome table, applied mechanically

Applying the pre-registration §3 selection table to the numbers above. **This is the mechanical
application of a table fixed before any number existed. It is not a decision — the kernel break is
Tommy's call, and this run has no authority over it.**

| row | condition | fires? |
|---|---|---|
| **R1** | `NARROW` **decreases** over the window **and** deletion events land on the `NARROW`/`WIDE` bins → `deletion-pressure-suffices` | **NO** — `NARROW` **increased** (+27). First clause fails. |
| **R2** | `NARROW` increases or is flat **and** deletion lands predominantly on `CONDITIONALLY-LOADED` (H1 holds) → `not-yet-earned` | **NO** — first clause holds, but **H1 is falsified** (§3). Second clause fails. |
| **R3** | n too small, or the change smaller than routine edit churn, to distinguish R1 from R2 → **`not-yet-earned`** | **YES** — +27 w is below the 25th percentile of one routine interval; 81% of moving intervals moved more (§6). |
| **R4** | `NARROW` and `WIDE` select different rows → `not-yet-earned` | **NO** — `WIDE-EXTRA` did not move; both read +27 (§1). |
| **R5** | no threshold can be supplied for "small enough" → **`not-yet-earned`** | **YES** — no threshold exists anywhere in the corpus, and H3 shows the question is not even unit-stable (§5). |

**Both R1 and R2 fail on their own terms** — which the pre-registration did not anticipate as an outcome,
and which is itself a finding: the data is not "H1 holds" *or* "deletion suffices"; it is a third shape,
*deletion falls hardest on `NARROW` and still loses to growth there*. **R3 and R5 both fire**, and both
were named in advance as the pre-committed defaults precisely because they are the outcomes an agent would
be tempted to escape later. Per the pre-registration, `break-proceeds` is **not selectable by this run at
all** — gates (a) and (b) are conjunctive and gate (b) has **n = 0** (never run; the treatment was never
varied), and a conjunction with an unrun conjunct cannot be satisfied.

**No threshold is invented here, and none should be read into the numbers above.** "43.9% of deletion
pressure lands on `NARROW`" is not a verdict about whether the surface is too big. It is an answer to a
narrower question — *where does deletion land* — and it happens to answer it against the pre-registered
expectation.

## 10. What this census cannot do — limitations that are structural, not gaps

1. **It is a per-PR series, not a per-edit series.** This repo **squash-merges**, so intra-PR
   grow-then-shrink is **invisible in every row**. A PR that added 3,000 words and deleted 2,900 appears
   as +100.
2. **Full history is not one comparable series.** `SKILL_REFERENCE_BUNDLES` and `skills/_shared/` do not
   exist before **`84fd28f` (2026-06-27)** — verified, not assumed: that commit is the first to introduce
   *both*, and its parent `b68c07b` has neither (0 `_shared` files, `bundles_at() -> None`). Before that
   boundary the bundled component is **`null`, never `0`** — undefined, not zero — at 2 of the 7 panel
   revisions. `WIDE-EXTRA` pre-regime is role-local resolution only and **must not be compared across the
   boundary.**
3. **Bin membership can shift with no edit.** A `references/` file becomes `WIDE-EXTRA` the moment a
   `SKILL.md` starts naming it. Levels can move without any gross add or delete; the gross columns are
   unaffected (no diff, no gross), which is why levels and gross are reported separately.
4. **Role lineage is hand-authored judgement** (§7), and `git log --follow` is forbidden.
5. **It measures the CONTENT axis's premise, not the content axis.** Nothing here tests a
   kernel+fragments decomposition, because none exists. The commander is already split on the **mode**
   axis (`1e8043a`/#107), which is a different thing.
6. **It says nothing about whether the corpus is the right size.** As #304 put it: a measuring stick, not
   a verdict. "Words went down" is not by itself an improvement, and neither is "words went up" a defect.
7. **Deliberate divergence from the baseline, filed as #411.** `TREND_SNAPSHOT` §2 lists `_shared` as a
   20th role. It is **not a role** — `scripts/install_constellation.py` (`discover_skills`) skips any
   directory whose name starts with `_`. This census counts **19 roles** at every revision where 19 is
   right, and asserts it by test. That is a divergence from the file this run is the successor to, and it
   is stated rather than silently applied.

## 11. Reproducing this, and what `--verify` actually proves

```bash
cd "C:/Programs/constellation-skills-wt/e298-310"
python ".agent-work/issue-310/trends/measure_surface.py" --verify \
  --data ".agent-work/issue-310/trends/trends.json" \
  --doc  ".agent-work/issue-310/TRENDS.md"
```

Five stages, each able to fail independently:

1. **The blocking baseline reproduction**, re-run live against `baseline/304-trend-snapshot`.
2. **The committed `trends.json` is re-derived from git** and compared field-by-field. Dataset drift or
   hand-editing fails here.
3. **The recombination arithmetic** — `NARROW + WIDE-EXTRA + CONDITIONALLY-LOADED == corpus` at every one
   of the 187 rows.
4. **Every headline figure in §2 is recomputed from git**, and the required key set must match **exactly**
   — a missing key and an unknown key both fail.
5. **Terminology and required substance** — the banned bare term, and the three bin names.

> **This check's predecessor in this epic was a keyword grep, and it was replaced after a one-line decoy
> containing only the keywords passed it.** This one is decoyed in §9 of the result file: a keyword-only
> one-line document, a dataset with one number altered, and a document with one headline altered all exit
> non-zero.

Other modes: `--reproduce-baseline [--at REV]`, `--calibrate-gross`, `--role-lineage`, `--snapshot REV`,
`--census --out FILE`, `--panel --out FILE`. Fixture suite:
`python -m pytest .agent-work/issue-310/trends/test_measure_surface.py -q`.

**No checkout, ever** — `git ls-tree -r --long` for sizes, `git cat-file --batch` for content, `git diff`
for gross. The working tree is never mutated by the instrument.

### Reuse from #307's instruments, and what could not be reused

`.agent-work/epic-298/preb/fingerprint_global_corpus.py` is **reused for its conventions**: raw-bytes-not-
decoded-text digests, sorted path order, path-relative keys, and `json.dumps(…, indent=2) + "\n"` written
`encoding="utf-8", newline="\n"`. Its **enumeration cannot be reused, and the reason is stated in writing
rather than implied**: it walks the *installed* global corpus on the filesystem
(`~/.claude/skills/constellation-*`) with **no revision parameter and no git access at all**, and its
output unit is a single digest, not a per-bin size. **A trend across 184 revisions cannot be taken from a
filesystem that holds only one of them.** Nothing under `.agent-work/epic-298/preb/` or
`.agent-work/epic-298/post/` was rebuilt.
