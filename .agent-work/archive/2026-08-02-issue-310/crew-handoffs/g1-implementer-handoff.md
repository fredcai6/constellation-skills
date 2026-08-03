# IMPLEMENTER_HANDOFF — issue-310 gate g1: the corpus/per-role surface census

## Assigned task

Build the trend instrument for **B2 evidence gate (a)** and produce its dataset and report.

**Deliverables (exact paths, all under `C:/Programs/constellation-skills-wt/e298-310`):**
- `.agent-work/issue-310/trends/measure_surface.py` — the instrument
- `.agent-work/issue-310/trends/trends.json` — the committed dataset
- `.agent-work/issue-310/trends/panel.json` — the pre-registered interpretation panel
- `.agent-work/issue-310/TRENDS.md` — the human-readable report

## Protected intent

This measurement feeds a **HITL architectural decision that a human named Tommy makes, not you and not
me.** You are assembling evidence. **Do not decide the kernel break. Do not invent a "small enough"
threshold.** A measured negative is a complete, successful deliverable.

## READ FIRST — binding

`.agent-work/issue-310/PRE_REGISTRATION.md`. It was committed **before this instrument existed** and it
fixes the bin definitions, hypotheses H1/H2/H3, the outcome-selection table, and the **void criteria**.
It is binding. Read `.agent-work/archive/2026-08-02-issue-304/TREND_SNAPSHOT.md` second — it declares
this run its **successor** and states what a successor must do.

## Constraints (inherited; do not re-derive, do not violate)

1. **The bare term "always-loaded" is BANNED.** Emit two separately-labelled series that the script
   **never sums**:
   - **`NARROW-ALWAYS-LOADED`** = `skills/*/SKILL.md` only. This is the **#304 baseline's** definition and
     the **verdict's primary number** — comparability is what makes this run a successor rather than a
     second baseline.
   - **`WIDE-ALWAYS-LOADED`** = `SKILL.md` + every `references/<file>` token that `SKILL.md` names,
     resolved role-locally first, then through **that commit's own** `SKILL_REFERENCE_BUNDLES` in
     `scripts/install_constellation.py`. A supplement, not the primary.
   - **`CONDITIONALLY-LOADED`** = `templates/`, `scripts/`, and any `references/` file the `SKILL.md` does
     **not** name.
   Publish the arithmetic to recombine them so a reader who rejects the convention re-derives **without a
   re-run**. *(The WIDE bin is a **reconstruction ruled by the Admiral**, not a contract discovered in the
   tree — nothing in the tree declares one. Say so in the manifest, in those words.)*
2. **Gross, never net.** Per interval emit **gross-added and gross-deleted separately, per bin.** Gate (a)
   asks whether deletion keeps up with growth, so growth must be measured directly, not inferred from
   endpoint differences. A net-only row is a defect.
3. **Address baselines BY TAG**, never bare sha: `baseline/304-trend-snapshot` (= `fc1685a`),
   `baseline/304-g2-approve` (= `a8d9467`). They are **not ancestors of `main`** (#304 squash-merged) and
   a bare sha is GC-eligible. A `rev-list` walk will never visit them — **union them in explicitly.**
4. **Assert every enumeration's count.** Under-inclusive enumeration presented as complete has bitten this
   epic **five times**. Roles, commits, files, unresolved tokens — assert the count, from a command.
5. **Every number names the revision or tag it was measured at.**
6. **19 roles.** `_shared` is **not** a skill (`scripts/install_constellation.py:245`). `TREND_SNAPSHOT`
   §2 listing it as a 20th role is a **defect, filed as #411** — diverge from the baseline there and say
   you did.
7. **A role's death is an org change and must NEVER read as deletion pressure.** Report roles entering
   and leaving the window separately from deletion. Role lineage is **hand-authored data** — say so where
   a reader will see it, not in a methods appendix. `git log --follow` is forbidden.
8. **Do NOT rebuild #307's instruments** (`.agent-work/epic-298/preb/`, `.agent-work/epic-298/post/`).
   Reuse `fingerprint_global_corpus.py`'s digest/byte conventions, and **state in writing** why anything
   you cannot reuse cannot be reused.
9. **No checkout, ever.** `git ls-tree -r --long` gives blob sizes directly; `git cat-file --batch` gives
   content. Measured: 184 commits touch `skills/`, ~0.1 s per `ls-tree`.

## Method

**(a) Census.** Walk every commit touching `skills/` (`git rev-list --reverse HEAD -- skills/`), unioned
with the tagged off-line baselines. One row per landed change. **This repo squash-merges**, so the series
is per-PR, not per-edit — intra-PR grow-then-shrink is invisible. **Say so.**

**(b) Regime break.** `_shared/` and `SKILL_REFERENCE_BUNDLES` do not exist before the regime boundary
(candidate analysis puts it near `84fd28f`, 2026-06-27 — **verify it yourself, do not trust it**). Before
that boundary the bundled component is **`null`, never `0`** — undefined, not zero.

**(c) BLOCKING baseline reproduction — this is an external oracle you cannot fake.** Reproduce
`TREND_SNAPSHOT` §1 at tag `baseline/304-trend-snapshot`: **19 `SKILL.md`, 15,831 words, 100 files,
63,681 words.** If you cannot, **the series is VOID** and you say so — you do not tune until it agrees.
Also re-derive the baseline at `5d2585b` (#304's merged form) and **report the delta between the two**;
that delta is itself a finding about what squash-merge does to a published baseline.

**(d) Test H1 across all rows.** *Does deletion land on `CONDITIONALLY-LOADED` rather than on the
always-loaded bins?* The one deletion event documented with exact arithmetic (#304's, 172 words) landed
**entirely in `templates/`**. **This is the likeliest decisive finding for gate (a) — do not let it become
a footnote.**

**(e) Is a trend computable at all?** *Required finding, not optional.* State **n**, the interval in
**commits and days**, and **the smallest change the instrument can distinguish from routine edit churn**.
Report that **n is 2 or 3 and WHY it is ambiguous** — the baseline is not an ancestor of `main`, so
whether `5d2585b` (#304's own squash-merge) counts is a judgement call. **Do not pick one silently.**

**(f) §3's re-run has no direct analogue.** Define it as the enumerated **deletion-event set** in the
window — **which may be EMPTY**. An empty set with its count asserted is a complete reportable result.

**(g) `panel.json`** = a small set of hand-justified revisions used **only** as the reporting/interpretation
layer over the census, **never** as the measurement.

## Required interface — this is the gate's closeout check

`measure_surface.py --verify --data <trends.json> --doc <TRENDS.md>` must **re-derive every figure from
git**, reconcile it against the committed dataset **and** against the headline numbers quoted in
`TRENDS.md`, run the blocking baseline reproduction, and **exit non-zero on any mismatch**.

**Do not weaken this into a keyword grep.** Its predecessor *was* a keyword grep and it was replaced after
being run against a one-line decoy containing only the keywords — **the decoy passed.**

## Numbers already verified by the Commander (reproduce these; flag any disagreement loudly)

| quantity | value | at |
|---|---|---|
| NARROW-ALWAYS-LOADED | 15,831 → **15,858** words (+27, +0.17%) | baseline → `origin/main` |
| corpus | 63,681 → **63,781** words (net +100) | baseline → `origin/main` |
| gross growth vs deliberate deletion | **≈272 gross growth against a 172-word deletion** | same window |
| `SKILL.md` count | **19** | `origin/main` |
| commits touching `skills/` in window | **3** (`5d2585b`, `9a0cb17`, `a4934cb`) — or 2, see (e) | baseline..`origin/main` |

## Test mode

No runtime behaviour changes. Evidence is **inspection + reproduction**: the instrument run twice at the
same HEAD must be **byte-identical**, and the blocking baseline reproduction must pass. Add a small
fixture test over a short commit slice if it is cheap; if you judge there is no useful test surface, say
so with a reason rather than skipping silently.

## Allowed scope

`.agent-work/issue-310/trends/**` and `.agent-work/issue-310/TRENDS.md` only.

## Specific exclusions

**Do not modify anything under `skills/`, `scripts/`, `tests/`, or `docs/`.** Do not edit
`PRE_REGISTRATION.md` (it is pre-committed and tamper-evidence matters). Do not merge, do not push to
`main`, do not touch the main checkout at `C:/Programs/constellation-skills`.

## Verification commands (POSIX form, absolute paths)

```
cd "C:/Programs/constellation-skills-wt/e298-310"
python ".agent-work/issue-310/trends/measure_surface.py" --verify \
  --data ".agent-work/issue-310/trends/trends.json" \
  --doc  ".agent-work/issue-310/TRENDS.md"
```

**Interpreter: `python` (3.14.x, has pytest). `py` is 3.12.13 with NO pytest and silently no-ops under
PowerShell, reading as a green suite.**

## Stop conditions

Stop and report if: the blocking baseline reproduction fails (**void — report, do not tune**); the two
runs are not byte-identical (**void — non-determinism**); or the census contradicts a Commander-verified
number above. **Report a void set; never quietly drop one.**

## Return format

`IMPLEMENTER_RESULT` written to
`C:/Programs/constellation-skills-wt/e298-310/.agent-work/issue-310/crew-handoffs/g1-result.md`:
evidence (pasted command output, not descriptions of it), blockers, scope drift, assumptions,
out-of-scope observations, and a **Workflow Feedback** section.

**You MUST also deliver a short verdict summary via `SendMessage` to `commander-310` before ending your
turn** — and if that address is unreachable, send it to `main` with an explicit relay request, because
peer-to-peer delivery has failed for every agent in this run so far.
