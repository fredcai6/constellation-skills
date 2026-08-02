# Crash-resume state note - issue-304

- **step:** execute - **g2 is CLOSED**; gate g3-implement is next
- **slug:** `issue-304` - branch `epic-298/304` - worktree `C:/Programs/constellation-skills-wt/e298-304`
- **next command:** `py C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-304/execute.json current`
- **pid:** none - foreground commander; g3 implementer dispatched as an in-process Agent subagent
- **expected artifact:** `.agent-work/issue-304/crew-handoffs/g3-result.md` (IMPLEMENTER_RESULT)

_Updated: 2026-08-02T03:50:00Z_

## g2 IS CLOSED — implement, review, integrate all complete

Reviewer round 1 **BLOCK** on one finding (`substitute_label` reachable only from `self_test`), reworked
as appended slice `m7` at `9d57e9b`, reviewer round 2 **APPROVE, 0 findings**. Across both rounds the
reviewer devised **seven** mutations outside the shipped set, all red; attacked the absent-frame refusal
with 12 variants for zero vacuous passes; reproduced all three reconstructed reds; and proved the
no-3.13+-API claim by compiling under `py` 3.12.13.

Close criteria re-run by the Commander, not taken on report: **312 passed, 435 subtests**, `--self-test`
exit 0. Wiring verified from the template JSON directly: `verify-orientation` at context `c2` (no
override policy), `verify-frame` at plan `c6` (`override_policy` human/reason-required), both on the
absolute `<repo-root>` placeholder.

**Settled:** the `CONTENT_HASH_RE {64}` survivor is a **false positive** — `$` already rejects longer
digests and `{64,}` would let a 128-char sha512 pass as a sha256 pin. Close it as not-a-defect.

**Filed to the tracker this session:** **#363** (reviewer skill directs the Fowler pass to be written
into the *installed template*, mutating the shared install), **#364** (the caller-grep doctrine misses
dead code in any module shipping its own self-test as a subcommand — needs "outside the def AND outside
the self-test").

**g3's implementer handoff is already written and committed** at
`.agent-work/issue-304/crew-handoffs/g3-implementer-handoff.md`. It survives a session death.

## RESUMED AFTER A DOUBLE SESSION-LIMIT DEATH

Two agents died on session usage limits, not stalls:

- **Commander (predecessor)** - dead, confirmed by 140 min with no filesystem write.
- **g2 implementer attempt-1** - dead. Last journal entry `2026-08-01T23:39:46Z` (m2 `start`);
  last file write `2026-08-01T23:44:23Z`; dead > 2h at resume.

**Its work was UNCOMMITTED and is now committed at `fdec654`** ("gate g2(#304): re-anchor map-first
to 'before you open any source file' (WIP, resumed)"). Everything below `6d35fe2` .. `fdec654` is
attempt-1's output: +536 lines `scripts/map_orient.py` (verify-frame), +252 `tests/test_map_orient.py`,
new `tests/test_map_contract_wiring.py` (271 lines), the template anchor change, installer registration.

## Where g2 actually is

`g2-implementer-plan.json` says: m0 complete, m1 complete, **m2 in-progress**, m3-m6 pending.
The FILESYSTEM says more is done than the plan records - attempt-1 wrote m2's implementation and
(per its own m1 digest, recorded as a deviation) m4/m5 substance, then died before attesting.

Measured at resume: `python -m pytest tests/test_map_orient.py -q` -> **68 passed, 39 subtests**;
`python scripts/map_orient.py --self-test` -> **exit 0**. That is m2's c2 command, green.

**The unresolvable-in-order problem:** every slice's `c1` is a TDD-red attestation
("observed FAILING **before** X exists"). X now exists. A fresh implementer cannot observe that red
in TDD order and must not pretend to. The sanctioned substitute is in the resume addendum
(`g2-implementer-handoff-RESUME.md`): revert the implementation file to `6d35fe2`, observe the
genuine red, restore, verify restoration by **blob OID** (never raw bytes - CRLF). Recorded as a
deviation, not as TDD order.

## Do NOT do these

- Do not point ANY tooling at `C:/Programs/f1Brainz` (`orient` WRITES a receipt into its `--root`).
- Do not touch `C:/Programs/constellation-skills` or `C:/Programs/constellation-skills-wt/e298-331`.
- Do not build a bootstrap/CLAUDE.md stanza (Q1 ruled: map is orchestrator content).
- Do not re-register the tripwires - `0119fa4` (T1-T4) and `1662b90` (T5), both pre-deletion.
- Do not fix #341, #342, #344, or the `--receipt-dir` item.
- Do not overclaim: necessity gate is a REGRESSION FLOOR, sensitivity 0/4, specificity 0/1.

---

## Run context a fresh agent needs

**Engine lease `commander-304-e298` is HELD** (re-claimed with `--force` at resume). Pass
`--session-id commander-304-e298` on every mutating call. Release **only** after the final
`advance archive`. The child `execute.json` carries `engine_session: null` and the lease does NOT
protect it (#357).

**Spine:** `.agent-work/issue-304/spine.json` - init/context/understand/plan complete, execute in progress.
**Child plan:** `.agent-work/issue-304/execute.json` - 13 tasks, 4 gate triads (g1->g4) + e0-context.

**g1 is COMPLETE and APPROVED** - re-review 8/8, 0 blockers, 2 triage, verdict in `g1-review-2/review.json`.
One honest survivor to take only if free: `CONTENT_HASH_RE {64}` -> `{64,}`.

### Rulings already made - do not reopen

- **Q1 RULED: candidate B is OUT.** No bootstrap stanza, no install lifecycle. The map is orchestrator
  content, not implementer content.
- **Q3 APPROVED:** tripwires pre-registered in a committed `TRIPWIRES.md`; episodes filed **after** the
  run with a real `observed-behavior`.
- **Q2 PROVISIONAL GO:** build to necessity + reported-degradation. Keep gate-vs-report **flag-flippable**
  (`--report-only` shipped).
- **All 15 critic findings triaged and ACCEPTED**, with two Admiral amendments in `execute.json`:
  the mutation harness must assert the mutation APPLIED before asserting red; the trend snapshot must
  name its consumer.
- **Design-it-twice is settled** - candidate B ruled OUT by Tommy.

### The framing this ships under - do not overclaim

- The **necessity gate is a regression floor**, sensitivity **0/4**, specificity **0/1**. Never describe
  it as the fix for the measured defect.
- The genuinely new value is **reported degraded mode**: a repo without a map currently has no contract
  at all - silent crawl, no record.
- **Ordering is not mechanizable by the corpus.** Needs a `PreToolUse` hook per #180. Known bypass to
  name in the writeup: crawl first, write anchors into the frame afterward - that is the *measured*
  behavior, not a hypothetical.

### Facts established - do not re-derive

- Command-check **stdout is discarded**; the **exit code is the only signal** reaching the spine.
- Command checks get **no cwd** -> #341.
- Deletion target is **172 words, 86 per template** (not 112).
- `"no docs/agents/ overlay at all"` occurs **twice**; the **first is load-bearing** and must survive.
- `docs/agents/` **exists** here; `docs/architecture/` **does not** - this repo is the degraded case.
- Episode store has **no `confirmed`** standing -> #342.
- Installed corpus is **18 commits stale**, 3 of 11 scripts differ -> #344.
- **#317 resolves by subtraction**: deleting Commander's 172 words leaves Charter as the sole remaining
  statement about `docs/agents/engine-config.json`. Note that on #336 when g3 lands.

### Triage filed

**#341**, **#342**, **#343**, **#344** - spine tc1-tc4. `#336` gets the subtraction note when g3 lands.

### What remains after g2

g3 (delete the 172 words, run the affected workflows, record outcomes against each tripwire, file
episodes citing the pre-registration SHAs, capture the trend snapshot) -> g4 (dogfood the gates in this
repo, itself the degraded common case; full suite) -> reconcile, triage, review, feedback, archive, PR.

### Standing invariants

- `python -m pytest`, not `py` (no pytest there). Neither local interpreter reproduces CI. Gate on the
  CI **status text `pass`**, not a zero exit.
- You cannot audit your own falsifiability - an independent reviewer must devise a mutation OUTSIDE the
  shipped set.
- Make the predicate the whole condition. A predicate with a boundary needs cases on both sides; one
  quantifying over a collection needs a multi-element case.
- Compare normalized content or blob OIDs, never raw bytes (Windows CRLF).
- State branch FINAL or PENDING explicitly in the return.
