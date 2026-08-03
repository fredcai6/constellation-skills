# B2 gate evaluation — the evidence packet

**For Tommy. Issue #310, epic #298.** Assembled by `commander-310`; **the kernel-break call is yours.**

```
SELECTED-OUTCOME: not-yet-earned
THRESHOLD-CHOICE-HANDED-UP: Tommy
UNIT-CHOICE-HANDED-UP: Tommy
GATE-B-N: 0
```

---

## Limitations first, not in a footnote

1. **Gate (b) was never run. n = 0** — no evidence, not weak evidence. Detail below.
2. **The corpus census that would have strengthened gate (a) was cut by you** on 2026-08-03 as premature.
   It is preserved and filed (#415), and **this verdict rests on none of it.**
3. **This repo has no architecture map.** Every structural number here is derived from the filesystem at
   a **pinned SHA or tag**, not read off a map (`DEGRADED-NO-MAP`, discharged before any source read).
   *No number in this document addresses a moving ref* — an earlier draft used `origin/main` as the
   terminal address for the whole of §3, which would have made it unreproducible the moment `main` moved.
4. **Nobody has chosen a threshold, and nobody has chosen a unit.** Both are open, and §5 argues the
   second is worse than the first.

**One mechanical note for anyone re-running these numbers:** both baselines are **annotated** tags, so a
bare `git rev-parse baseline/304-trend-snapshot` returns the **tag object**, not the commit. Every address
here uses `^{commit}` and yours must too, or you will measure the wrong object.

---

## 1. Which axis was measured — and both misreadings refused

**The commander is already split — on the MODE axis.** `1e8043a` (#107), verified against the tree:
`skills/commander/SKILL.md` 107 lines → a 16-line stub, `commander-delegated/SKILL.md` added (18 lines),
`references/commander-core.md` added (121 lines), 8 files changed.

**B2 proposes a split on the CONTENT axis** — a small always-loaded kernel plus just-in-time fragments
selected by the active spine node. **By name, it is unstarted**: there is no fragment directory, no
projection generator, no selector.

**But "unstarted" is a claim about names, and I do not rule it.** The corpus's existing three-bin shape —
`SKILL.md` as trigger/pointer, `references/` as doctrine, `templates/` as interface — is already
kernel-shaped, and #307 showed per-task delivery through the spine template moving behaviour that
always-loaded delivery could not. **Whether B2's content axis is substantially further along under a
different name is an open question and it is yours** (restated in §8).

Two readings are available and **both are refused**:

- ❌ *"The mode split already satisfies B2."* It does not. Different axis.
- ❌ *"B2 is unstarted work on a monolith."* It is not. `skills/commander/SKILL.md` is **16 lines with
  zero occurrences of the word "map"** at both `cfa2c40` and **`9a90298`**. **The always-loaded surface is
  already small.**

---

## 2. Why `break-proceeds` is FORECLOSED — by logic, not by numbers

The confirmed spec (line 77) makes the gates **conjunctive**:

> *"The break proceeds only if **(a)** the corpus-size trend… **and (b)** a role-competence test shows an
> agent operating from kernel-plus-fragments-plus-artifacts completes a representative mid-spine step as
> correctly as one holding the monolith."*

**Gate (b) has n = 0.** A conjunction with an unrun conjunct cannot close. **No amount of trend evidence
can select `break-proceeds`**, so the three-outcome frame **resolves, for this run, to a two-way call**
between *not-yet-earned* and *deletion-pressure-suffices*.

### The correction that produced n = 0 — and it corrected me and the Admiral both

I originally proposed this epic's **refresh / cold-start relaunches** as observational gate-(b) evidence,
and the Admiral endorsed it. A cold plan critic showed we were both wrong:

> *"Every relaunched agent held the **full monolith**… **the treatment was never varied**."*

A study that never varies its independent variable does not have a small sample of the effect — **it has
no sample of it.** Those runs bound Assumption 1 (artifacts carry state between steps); they contribute
**zero** to a kernel-vs-monolith comparison, and no relaunch count appears in the (b) column here.

**And the excuse that would have covered this is withdrawn.** I claimed a competence arm was
*impossible* — "building the decomposition IS the break" — and graded that claim `settled/structural`. It
is neither. An **ablation** arm (run one mid-spine step with doctrine sections *withheld* vs full) varies
the treatment with **zero authoring**. Regraded `guess/structural`; design and cost filed as **#414**.
Gate (b) is unrun for **runway and your scope ruling**, not for impossibility.

---

## 3. Gate (a): thin, sign is up — and NOT load-bearing for the outcome

**Read §2 first. The outcome is already selected there, without any number.** Everything in this section
is **corroboration, not selection** — it is consistent with the outcome and could not select it, because
selecting on a size figure would require a unit and a threshold, and §5 shows neither exists.

Window pinned at both ends: **`fc1685a`** (= `baseline/304-trend-snapshot^{commit}`) → **`9a90298`**.
Both endpoints re-derived independently by this Commander, not taken from the census.

**Scope is named per row, because the rows do not share a denominator** — the NARROW rows are a *subset*
of the corpus rows, not a parallel measure:

| scope | quantity | value | provenance |
|---|---|---|---|
| all of `skills/` | words added | **+222** | measured (census, unreviewed) |
| all of `skills/` | words deleted | **−122** | measured (census, unreviewed) |
| all of `skills/` | net words | 63,681 → **63,781** (**+100**) | measured, re-derived independently |
| `skills/` file count | | **100**, unchanged | measured, re-derived independently |
| `skills/*/SKILL.md` (NARROW-ALWAYS-LOADED) | net words | 15,831 → **15,858** (**+27**) | measured, re-derived independently |
| `skills/*/SKILL.md` | file count | **19**, unchanged | measured, re-derived independently |

The two scopes nest: the corpus net **+100** decomposes as **+27** NARROW and **+73** conditionally-loaded.

**What this shows:** there was real deletion inside the window — 122 words — and growth still exceeded it.
**What it does not show:** whether that matters. That would need a threshold and a unit.

**Correction, recorded rather than quietly fixed.** An earlier version of this packet said *"gross growth
≈272 against a 172-word deletion."* **That was wrong.** The 172-word #304 tripwire deletion landed
**before** the baseline was taken — `baseline/304-g2-approve^{commit}` (`a8d9467`) is 63,849 words and
`baseline/304-trend-snapshot^{commit}` (`fc1685a`) is 63,681, with the deletion commits (`ea52b2f`,
`456cac0`) between them. **The baseline is already post-deletion**, so the old claim compared a pre-window
deletion against in-window growth and double-counted.

*(An earlier draft also justified the corrected figures by noting that 222 − 122 = 100 "closes exactly."
**That clause has been deleted: it proves nothing.** `net = added − deleted` is definitionally true and
closes for any scope, correct or incorrect — a check whose output is identical whether the comparison is
sound or broken. Like-for-like is established by the pinned endpoints and the named scopes above, which
is the only thing that can establish it.)*

*(Commit counting is dropped entirely. `5d2585b` has a `skills/` tree OID byte-identical to the
baseline's — a zero-delta row — so the interval-size question had no numerical consequence.)*

---

## 4. The structural finding — and it is the one that bears on the work you are doing now

Two definitions of a role's always-loaded surface were in play, and they are named separately here
because they are not interchangeable:

- **NARROW-ALWAYS-LOADED** — `skills/*/SKILL.md` only. The #304 baseline's definition, and the primary
  number in §3, because comparability with the declared baseline is what makes this run a *successor*
  rather than a second baseline.
- **WIDE-ALWAYS-LOADED** — `SKILL.md` **plus every `references/` file it names**. The Admiral's ruled
  reconstruction of what an agent actually loads. *A reconstruction, not a contract discovered in the
  tree — nothing in the tree declares one.*

**And the WIDE rule does not close.** At HEAD, of 21 named reference tokens, **10 cannot be resolved from
the citing role's own directory** — roles cite across role boundaries, and the shared `_shared/global-*.md`
bundle is injected at *install* time by `scripts/install_constellation.py`, not present in the repo shape
at all. **So WIDE-ALWAYS-LOADED, as ruled, cannot be evaluated from role-local files alone.**

> **The fact:** at **`9a90298`**, of **21** named reference tokens across the corpus, **10 do not resolve
> inside the citing role's own directory.**

**The inference, labelled as one:** if that holds, a role's always-loaded surface cannot be computed from
the role's local files, and *you cannot decompose a role into fragments if you cannot determine what the
role loads.* **The fact is measured; the inference is drawn under a reconstructed bin and is the part a
reader can argue with.** The fact alone is enough to matter to the substrate work.

**This is not a metrics finding and it does not die with the census.** It reads as a structural
precondition on B2's content axis: any kernel/fragment split has to answer *"what does this role actually load?"* first,
and today that answer requires resolving through the installer's bundle table (`SKILL_REFERENCE_BUNDLES`),
which only exists after a regime boundary partway through the corpus's life. **It bears directly on the
substrate rework in flight.**

**A warning from the halted implementer, worth more than the census it came with:** the instrument's
*measurements* are substrate-independent — they read git history. **Its bins are not.**
`WIDE-ALWAYS-LOADED` reconstructs a loading contract that does not exist in the tree, so **a substrate
rework could make that bin wrong in a way no re-run would reveal.** If the kernel-break question is ever
reopened, **re-examine the bin ruling before trusting any number computed under it** — which is an
independent argument that measuring now would have been premature.

---

## 5. The other finding: **there is no unit, not just no threshold**

The spec's own critic (S2) flagged that B2 has *"no threshold at which the current shape stops working."*
True. But there is a worse problem underneath it.

**The same corpus produces opposite orderings depending on the unit you measure in.** At HEAD:

| role | lines | rank by lines | bytes | rank by bytes |
|---|---:|---:|---:|---:|
| `docent` | **143** | **1st** | 7,281 | **5th** |
| `explorer` | 99 | 2nd | 13,729 | 2nd |
| `lessons-auditor` | 80 | 3rd | 9,270 | 3rd |
| `admiral` | 77 | **4th** | **17,214** | **1st** |

**The rank fully reverses at both ends.** `docent` is the biggest role by lines and 5th by bytes;
`admiral` is 4th by lines and the biggest by bytes (long lines).

And the corpus is **already internally inconsistent about this**. `scripts/curate_corpus.py:49-50`:

```python
SKILL_WORD_TARGET   = 400   # soft target; body WORDS over this -> flag
SKILL_LINE_HARD_FLAG = 500  # hard LINE flag; body LINES over this -> flag
```

**Three units in play — words, lines, and bytes — in one file, with no stated relationship between them.**

**Therefore: a threshold is meaningless until a unit is fixed.** Asking you for *N* without asking for the
unit would hand you an unanswerable question, so both go up together.

*(Those two constants are the corpus's **only** in-tree size line. **Offered, explicitly not adopted:**
they govern `SKILL.md` **body size**, not the always-loaded **role surface** B2 asks about — which is why
they cannot simply be promoted into B2's threshold.)*

---

## 6. #307's evidence, with both bounds intact

#307 is the one **direct** signal in favour of the fragment thesis: `map_before_src` went **0/4 → 4/4**
when the map contract moved into per-task spine imperatives, while the always-loaded skill text carried
**zero** occurrences of "map". The PRE arm was *not* map-deprived — the map was present, cited in
auto-loaded `CLAUDE.md`, read 4/4 — and still scored **0/5 on orientation order**.

**Both bounds carried, neither softened:**

1. **It measures PLACEMENT, not DECOMPOSITION.** One contract moved to a per-task slot is not a role
   broken into a kernel plus fragments. Suggestive; not proof.
2. **The manipulation was 8 days and +31 files, not #304 alone.** Containment proven, exclusivity not.

---

## 7. The verdict, and which pre-registered row fired

**`SELECTED-OUTCOME: not-yet-earned`** — *keep deleting, re-evaluate in a follow-on.*

**Selected by gate (b), and by nothing else.** Gate (b) was never run; the gates are conjunctive; a
conjunction with an unrun conjunct cannot close. **`break-proceeds` is therefore not selectable, and the
break is not earned.** *This argument uses no unit, no threshold, and no number* — which is what makes it
survive the fact that neither a unit nor a threshold exists.

That corresponds to **row R5** of the table pre-registered in `PRE_REGISTRATION.md` **before any number
existed** (committed `410299d`, an ancestor of every measurement here): *an unadjudicable gate has not
been adjudicated.*

**Row R3 (the "n is too small" row) is deliberately NOT invoked.** It would have fired the outcome on a
size judgement — *"+0.17% is within routine churn"* — which is a **threshold denominated in words**, i.e.
exactly the two choices §5 says nobody has made. Founding the verdict there would have made this document
depend on the gap it is escalating. **A cold reader caught that circularity and the verdict was re-founded
on gate (b) rather than patched.**

**`deletion-pressure-suffices` is NOT selected either**, and the reason is worth stating: the one thing
gate (a) does show points the other way — real deletion happened inside the window and **growth still
exceeded it**. So this is *not* a finding that deletion is working and the break is therefore unnecessary.
It remains corroboration, not selection.

**This is the outcome the issue explicitly blesses**: *"If deletion-trend data is still thin, the
legitimate outcome is 'not yet earned'… the gate concluding insufficient evidence is the staging working,
not a failure."* **It is delivered early and on evidence already in hand, and I am not apologising for
it.**

### Guard against this document's own rigor

There is no census here, and that is deliberate. **Had a whole-history series been attached, its
mechanical reproducibility would have *looked* like it settled something** — and it would not have,
because the gate's threshold and unit do not exist. A curve cannot answer a question whose numerator is
undefined. **The absence of a chart in this document is a feature of it.**

**And the verdict does not lean on a size number at all** (§7), which is the strongest form of that
guard: there is no figure here whose emphasis could substitute for a threshold nobody has set.

---

## 8. What is actually being asked of you

1. **The unit** — bytes, lines, or words? Nothing in the corpus has chosen, and the answer changes the
   ranking (§5).
2. **The threshold** — once a unit exists, what is "small enough" for a role's always-loaded surface?
3. **Whether gate (b) is ever worth buying** — #414 says what it costs. Until something varies the
   treatment, `break-proceeds` stays foreclosed no matter how much trend evidence accumulates.

**The open question, restated from §1 and explicitly not decided:** the corpus's existing three-bin shape —
`SKILL.md` as trigger/pointer, `references/` as doctrine, `templates/` as interface — is **already
kernel-shaped**, and #307 showed per-task delivery through the spine template moving behaviour that
always-loaded delivery could not. It is possible B2's content axis is further along under a different
name than "unstarted" suggests, and that the remaining work is a **selector and a naming** question
rather than a re-architecture. **I am not ruling on that. It is a durable-structure choice and it is
yours.**

---

**No kernel-break decision has been taken in this document.** Evidence assembled, outcome named, both
open choices handed up.
