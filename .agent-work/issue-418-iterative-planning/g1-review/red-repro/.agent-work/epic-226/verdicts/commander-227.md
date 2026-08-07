# Commander verdict — issue #227 (epic-226 item A, wave 0)

**PR:** [#241](https://github.com/fredcai6/constellation-skills/pull/241) — branch `issue-227`, 5 commits, open against `main`.
**Commander:** `cmd-227` (opus) · crew at sonnet · no Fable at any tier.
**Worktree:** `C:/Programs/constellation-wt-227` · **Spine:** driven to terminal through the vendored engine.

---

## 1. Verdict per build item

| # | Item | Verdict |
|---|---|---|
| 1 | `current` as a complete gate briefing | **SHIPPED**, with a scoped honest null (below) |
| 2 | Recovery-bearing `REFUSED` | **SHIPPED** — four defects found and fixed across three rework rounds |
| 3 | Ports-lite state projection | **SHIPPED** |
| 4 | Output ordering — operative line last | **SHIPPED** — the Admiral's field defect is closed |
| 5 | `measure_overread.py` + baseline/delta | **SHIPPED**, with a **scoped honest null** on the delta |
| 6 | Two doctrine riders | **SHIPPED** — plus a PR-6 finding |

### Item 1 — honest null on half of it (PR-7)

Verified against `scripts/checklist_engine.py` **before planning**, per the active
`verify-launch-order-claims-against-code` lesson:

- **Already shipped:** `current()` never truncated the imperative. No slicing, no `textwrap`, no
  ellipsis anywhere in the render path. The "full imperative verbatim (never elided)" half of item 1
  was already true at HEAD.
- **Already shipped:** INV-2 purity. `current()` never called `_check_condition`, so the projection
  was already pure. This was **preserved and now tested**, not introduced.
- **Genuinely missing:** the conditions block. `current` showed no condition ids at all — which is
  precisely why I had to open `spine.json` four times in this very run.

**Tested / NOT tested:** I verified elision and purity by reading the whole render path and by a test
that fails if `subprocess` is invoked. I did **not** test whether any *other* engine output path
elides content — only `current`.

### Item 6 — PR-6 finding

The pre-ruling warned that editing `skills/<role>/references/global-*.md` would be silently
overwritten by the installer. Sound in principle, but **no role copy is tracked in this repo at all**
(`git ls-files "skills/*/references/global-*.md"` returns empty) — they are materialized only at
install time. So there was nothing in-repo to regenerate and running the installer was unnecessary.
`test_shared_sync_integrity_installed_references_match_source_bytes` installs fresh from `_shared`
into a temp root and passes.

---

## 2. Evidence

### Worktree isolation

```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-227
worktree OK: in C:/Programs/constellation-wt-227
EXIT=0
```

### `pytest tests/` — locally run (PR-2; no CI exists)

```
$ cd C:/Programs/constellation-wt-227 && PYTHONIOENCODING=utf-8 python -m pytest tests/ -q
..s.......................                                               [100%]
998 passed, 2 skipped, 250 subtests passed in 33.41s
EXIT=0
```

Branch-point baseline was `905 passed, 2 skipped, 244 subtests` — so **+93 tests, zero regressions**.
The launch order's "906-suite" is the colloquial name; 907 are collected.

**Use `python`, not `py`.** On this box `py` resolves to a pytest-less runtime
(`codex-primary-runtime`). Live evidence for #228; not fixed here.

### Named tests

| Test | Covers |
|---|---|
| `Inv1CompletenessOracle.test_current_output_covers_advance_why_and_attest_evidence` | INV-1 oracle |
| `Inv2PurityNoSubprocess.test_current_never_invokes_subprocess` | INV-2 no-subprocess |
| `Inv3RecoveryEnumeration.test_generated_grid_every_state_caused_refusal_is_non_generic` | INV-3 enumeration |
| `Inv3ExclusionCheck`, `Inv3StartNonActiveEnumeration` | exclusion honesty; non-active `start` |
| `UnknownCondIdRecovery.test_unknown_cond_id_enumerates_every_real_id_on_the_task` | fourth axis |
| `GoldenOutputBriefing` (6) | per active-task state **+** the three no-active-task branches |
| `RecoveryRunnabilityAudit`, `RecoveryActiveGatePosition`, `RecoveryPositionAudit` | closed-loop runnability |
| `LegacySpineBackwardCompat` (5) | real captured pre-#179 spine renders, never raises |

All pass inside the 998.

**How the oracles resist self-confirmation** (`lesson:verify-harness-field-and-drive-real-writer`):

- INV-1's map is **hand-authored from the verb bodies**, not walked from argparse. `advance --why`
  and `attest --evidence` are required at *runtime* but optional at the parser — an argparse-derived
  map would have omitted exactly the two arguments agents most often read source to discover. The
  assertions read `current()`'s literal output string, never `state()`'s own `next_verbs`.
- INV-3's grid is **generated** from the engine's status vocabulary × `MUTATING_VERBS`, with the
  coverage count derived from the grid, so a new status or verb forces the test to notice. The
  exclusion set is derived from `MUTATING_VERBS`, not hand-listed.
- Both were proven to **bind** by reverting the fix and observing red, then restoring and confirming
  a byte-identical tree.

### `measure_overread` — baseline and delta

| Measurement | Command | Result |
|---|---|---|
| **Baseline** (pristine engine, commit `324437b`) | `cd C:/Programs/constellation-wt-227 && PYTHONIOENCODING=utf-8 python scripts/measure_overread.py` | `AGGREGATE_STRUCTURAL_READS: 6` (4 runs, 0/3/2/1, mean 1.50) |
| **Post-change**, same command, same corpus | *(identical)* | `AGGREGATE_STRUCTURAL_READS: 6` — **delta 0** |
| **Post-change, live transcripts** under the new engine | `python scripts/measure_overread.py --corpus /tmp/postchange` | `31` over 2 runs → **state=1, engine_source=30** |

The baseline was captured **before** any engine edit (`git diff --stat -- scripts/checklist_engine.py`
empty at that commit) — the cold plan critic caught that a baseline taken after g2/g3 would be
fiction, and the gate order was rewritten to fix it.

### PR-1 probe — `current` against a COPY of the live epic spine

```
$ python scripts/checklist_engine.py --file <COPY of .agent-work/epic-226/spine.json> current
LEASE active: admiral-epic-226-b (by admiral, heartbeat 2026-07-24T22:48:37…)
ACTIVE execute [in-progress] — Before entering this step and before EACH detached wave launch, …
postconditions:
  c1 [unmet] null — every epic issue dispositioned (merged, honest-null closed, deferred with ruling, or escalated)
  c2 [unmet] null — ADMIRAL_LOG current through the last wave: all rulings, incidents, merges, and errors logged
2/4 met
next: attest execute --cond c1 --which postconditions | attest execute --cond c2 --which postconditions
DIGEST: Latitude contract CONFIRMED by Fred 2026-07-24 …
PROBE_EXIT=0
```

Exit 0, renders cleanly, no `KeyError`. The copy was deleted after the probe. **No mutating verb was
ever run against the live spine, or against any spine outside my worktree.**

### Item 4 — the field defect, closed

```
--- refusal, stderr | tail -1 ---
REFUSED: g5-delta is 'pending', must be in-progress to advance Recovery: g5-delta is not the
active gate; the checklist works gates in order and 'g3-integrate' must be worked first --
run `current` to see g3-integrate's legal next move (do not act on g5-delta yet).
Do not edit the JSON — use the engine.

--- success, stdout | tail -1 ---
next: attest g3-integrate --cond c2 --which postconditions --evidence <evidence-id> | …
```

Before this change `tail -1` returned the RAIL banner on both streams. Your field evidence is the
acceptance evidence.

### Rail freeze (#145) — byte-identical across the whole branch

```
$ git diff main..HEAD -- scripts/checklist_engine.py | grep -c "_RAIL_STRINGS"
0
```

---

## 3. The finding worth your attention

**Four defects in gate g3, all the same shape: a recovery line naming a command that refused when
actually run.** It consumed the full rework budget (3/3).

None was a careless branch. Each time, **the test fixtures could not express the failing state**:

1. Suggested terminal verbs while a blocking condition was still open.
2. `blocked`-no-prior named `reopen`, which requires `complete`.
3. `_next_verbs` on a **non-active** gate suggested `start`, which refuses — invisible because every
   recovery fixture was single-task, so the lone task was always active by construction.
4. `start`'s own guard named `start <active>` unconditionally — refuses when the active gate is
   `in-progress` or `blocked`; invisible because `_make_non_active()` hardcoded the guard to `pending`,
   the one state where the advice was accidentally safe.

Every fix was validated against a world where its bug could not exist. The generalizable rule — and
this is the lessons-audit input I most want carried forward: **when a test asserts on generated
advice, it must execute the advice, and its fixtures must be parameterized on every dimension the
advice depends on.** Status was covered from the start; *position* was not, and that alone cost two
rework rounds.

Mitigations shipped: fixtures parameterized over status **and** position; `RecoveryRunnabilityAudit`
invokes each command a recovery names; the hazard is recorded in `docs/CHECKLIST_ENGINE_DESIGN.md`
where the next editor will hit it.

**My own final check:** 4,320 combinations of (target status × status_detail × precondition ×
postcondition × condition-kind × active/non-active position × active-gate status × verb), invoking
every command each recovery names — **zero bare recoveries**, and the only refusing commands reduce to
one state (`artifact` postcondition with `satisfied: True`, no evidence, no `attested`) that three
reviews independently confirmed is **unreachable through the engine** — producible only by hand-editing
the JSON, which item 6's rider now forbids.

---

## 4. Honest nulls, with scope

**A. Item 5's fixed-corpus delta is zero — by construction, not by failure.** The committed corpus is
a fixed set of *historical* transcripts; re-scanning it after the engine changes cannot move the
number. It proves the instrument is **deterministic**; it cannot demonstrate behavior change.

Behavior evidence is separate: 31 raw reads over 2 live post-change crew transcripts, decomposing to
**30 engine-source + 1 state** — and the 30 are implementer crews whose *assigned task was editing
`checklist_engine.py`*, so an engine-source read is their work, not over-read. The component the fix
targets is **1 state read across two full crew runs**.

First-person datum, from the population the fix actually targets: **I opened `spine.json`
programmatically four times before the conditions block existed** — purely to enumerate condition ids
— **and zero times afterwards** for that purpose.

**NOT shown:** (1) no controlled A/B — pre- and post-change transcripts are different agents doing
different work; (2) the corpus is **synthetic-but-labelled**, because no raw JSONL transcripts exist
under `.agent-work/archive/` and real ones carry user conversation content that must not enter a
public repo; (3) the instrument cannot separate a legitimate engine-source read from over-read, which
is why the raw 31 means nothing undecomposed; (4) **no token figure is produced** — this counts read
*events*, so it neither confirms nor refutes the ~8.8k tokens/run headline. Quoting it as token
evidence would be overreaching.

**B. Item 1's imperative-elision and INV-2 purity halves were already shipped** — see §1.

---

## 5. Map impact

No packet map exists in this skill-source repo, so I reconciled the structural record directly
(`4b6506d`), into `docs/CHECKLIST_ENGINE_DESIGN.md`:

- The rail section **actively described the old append-suffix behavior** — it would have contradicted
  the code. Now records banner-first ordering, the field evidence, and unchanged stream assignment.
- New **Answerability** section: the `state()`/`render_human()` port, the deliberate no-public-`--json`
  deviation from the ratified panel, INV-1/2/3, the CLI-boundary recovery seam with `EngineError`'s
  structured attributes, and the standing four-defect hazard.
- The verb table's `current` line no longer described what `current` does.

`docs/CHECKLIST_SCHEMA.md` is a **reasoned no-op**: the projection is derived, not persisted; no schema
field changed.

**Capabilities changed:** `engine-current` (rewritten), `engine-refusal` (new recovery channel),
`engine-rail` (position moved; strings frozen), `overread-measurement` (new), `shared-doctrine` (two riders).
**New seam:** `state(cl) -> dict` — internal, versioned via `contract`, no public adapter.

---

## 6. Triage candidates — all `recommend-and-defer`, none filed, none absorbed (PR-8)

I have **no standing authorization** for `gh issue create` and cannot reach the human, so these are
handed to you to drain.

1. **`waive()`'s 4 raise sites are unwired into `recovery_for()`.** Exhaustiveness gap; names no wrong
   command. **I deliberately did not take this as fix-now triage** — the g3 reviewer had just approved
   and the rework budget was spent; slipping an unreviewed engine edit past the review that had caught
   four defects in that exact surface was the wrong trade.
2. **`py` resolves to a pytest-less runtime; `python` works.** Every template saying `py scripts/...` is
   a latent false-red. Live field evidence for **#228**; not absorbed.
3. **The launch-order template's claim that `.agent-work/archive/` holds usable transcripts is false.**
   None exist. This cost this run its corpus. **The one I'd act on beyond filing** — it will mislead the
   next Commander too.
4. **`advance`'s `from_child` and `consolidate`'s 3 raise sites are bare-but-honest.** Same class as (1).
5. **The archived design-it-twice panel's exhibits use `attest --id t-3`, but the shipped CLI takes `id`
   positionally.** An implementer following the panel verbatim writes non-runnable commands — which is
   exactly what happened here.

---

## 7. Workflow feedback (lessons-audit input)

- **The launch order was excellent, with one factual error** — the `.agent-work/archive/` transcript
  claim (§6.3). Everything else pasted enough that I never needed to ask up.
- **PR-7 changed the plan, exactly as intended.** Verifying before planning turned item 1 from
  "build it" into "half of it already exists" and redirected effort to the real gap. Keep this clause.
- **The cold plan critic was the highest-leverage 8 minutes of the run.** It caught that g3's baseline
  would be unproducible after g1/g2 overwrote the engine — a defect that would have invalidated item
  5's acceptance entirely — plus three self-confirming-test traps, *before* any crew was dispatched.
  All 10 findings were accepted. **Recommend making the cold critic mandatory rather than bias-to-yes**
  for any gate plan whose acceptance depends on a before/after measurement.
- **Design-it-twice was correctly pre-empted.** The archived panel settled the `StateView` shape *and*
  its five invariants, so the pre-ruling's "run it for a new load-bearing interface" did not fire —
  there was no new interface to invent. Reading all three candidates cost minutes and saved a panel.
- **Background subagents are unavailable at this tier.** `Agent(run_in_background: true)` fails with
  "In-process teammates cannot spawn background agents", so every crew ran synchronously and every
  rework required `SendMessage` + an in-turn polling loop. Two polls hit the 10-minute Bash ceiling and
  had to be re-issued. Not blocking, but it made a 3-rework gate expensive.
- **`run_crew.py --backend external` + `--verify-result` worked exactly as documented** — the freshness
  check caught nothing stale, but I trusted it more for having run it.
- **The engine dogfooded its own fix mid-run.** After g3 landed I began piping engine calls through
  `tail -1` and it just worked. Before g2 I was dumping `spine.json` with inline Python to find
  condition ids; after, the conditions block answered it. That is the clearest signal the issue
  targeted something real.
- **Rework cap of 3 was exactly right and nearly binding.** A fourth defect would have escalated rather
  than returned. Given all four were one shape, I'd note the cap counts *rounds*, not *root causes* —
  four symptoms of one fixture-blindness cause consumed the whole budget.

---

## 8. Decisions floated

**None requiring your adjudication.** Every choice sat inside Inherited Latitude. Two rulings recorded
as decision candidates:

1. **Recovery composes at the CLI boundary**, not at the raise sites — preserving the verb-purity design
   law at `checklist_engine.py:160-164`. `EngineError` carries structured attributes; nothing re-parses
   message text.
2. **The RAIL banner moves to the front for all railed verbs including `current`**; suffix ordering after
   the body is unchanged. Item 4 specifies the ordering change verbatim, so this is inside the issue.

Neither reworded, reordered, or merged anything into the five frozen rail strings.

**Not done, and flagged rather than assumed:** no public `--json` flag, no `explain`/`show` verb, no
SKILL.md body edits, no absorption of #220's surviving items or #219's threads.
