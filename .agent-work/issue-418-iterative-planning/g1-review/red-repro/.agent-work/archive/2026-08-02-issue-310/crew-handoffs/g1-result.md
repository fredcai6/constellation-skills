# IMPLEMENTER_RESULT — issue-310 gate g1 (census)

## Return status

**`HALTED-BY-SCOPE-CUT`** — stood down mid-`m5-verify` on a ruling from Tommy relayed via the epic-298
Admiral: *"we're making our life hard to come up with metrics too early… we're just reworking the
substrate."* Nothing deleted or reverted. Everything is committed on `epic-298/310`.

## Gate-by-gate state (7 plan items)

| # | gate | state |
|---|---|---|
| m0-context | load context, verify handoff complete | **complete** |
| m1-oracle | blocking baseline reproduction | **complete — PASSED, and decoyed** |
| m2-bins | three-bin classifier + regime boundary | **complete** (31 fixture tests) |
| m3-census | 187-row census, gross-not-net, determinism | **complete** (engine ran the two-run byte-identity check) |
| m4-report | `panel.json` + `TRENDS.md` | **complete** — written before the cut arrived |
| m5-verify | `--verify` + 3 decoys | **SKIPPED (OBE)** — clean run passed, decoy 1 of 3 proven; decoys 2–3 not run |
| m6-closeout | commit + result + delivery | **complete** |

## The blocking baseline reproduction: **PASSED**

Asked for explicitly, so verbatim:

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
EXIT=0
```

All four published figures reproduce exactly. **The series is not void.** The oracle was decoyed before it
was trusted: `--at baseline/304-g2-approve` → exit 1 (`corpus_words 63849`), `--at HEAD` → exit 1
(`skillmd_words 15858`). The fixture suite was mutation-tested (`15831`→`15832`, mutation asserted applied
⇒ `1 failed, 28 passed`).

## What `trends.json` actually contains right now

`schema: issue-310-surface-census/1`, 448 KB, deterministic (no wall-clock field; the engine verified two
runs at the same HEAD are byte-identical).

- **187 rows / 186 intervals.** 184 commits from `git rev-list --reverse HEAD -- skills/`, plus **3
  explicitly unioned**: both tagged baselines (neither is an ancestor of `main`, both confirmed absent
  from the walk) and **HEAD itself**, which touches no `skills/` file so `rev-list` never yields it.
- Per row: levels for all three disjoint bins (`NARROW-ALWAYS-LOADED` / `WIDE-EXTRA` /
  `CONDITIONALLY-LOADED`) in files, words, bytes and lines; `bundles_defined`; unresolved-token count.
- Per interval: **gross added and gross deleted separately, per bin**, in words, bytes and lines — plus
  `net` as a supplement. No row is net-only.
- Per interval: `roles_entered`, `roles_left`, `roles_left_classification`, and
  `deleted_role_departure` per bin, so `deletion_pressure = deleted − role_departure`.
- `window` (baseline→HEAD) with **both** n values; `deletion_events` (234 corpus-wide, 3 in the window);
  full `baseline_snapshot` and `head_snapshot` with per-role detail; a manifest carrying the
  Admiral-ruling attribution, the recombination arithmetic, and the hand-authored-lineage caveat.

`--verify --data trends.json --doc TRENDS.md` **ran clean before the cut** (5/5 stages, 62/62 headline
figures re-derived from git, exit 0, 49 s).

## Findings worth keeping independent of the census

These are facts about the repo and about #304's published baseline. They survive the census being dropped.

1. **🚩 A Commander-verified number is arithmetically wrong.** *"≈272 gross growth against a 172-word
   deletion, same window."* **The 172-word deletion is not in that window.** It landed in
   `baseline/304-g2-approve → baseline/304-trend-snapshot`, i.e. **before the baseline was taken**; the
   baseline's 63,681 is already the post-deletion figure. The window's own gross is **+222 added / −122
   deleted, net +100** — which closes exactly on the measured corpus delta. *The underlying claim ("the
   corpus grew despite the deletion") survives and strengthens; only the arithmetic was wrong.*

2. **🚩 #304's own published event mixed gross with net.** Its `172` is gross-deleted (dead-path block
   only); its `+4` is a **net** figure for the retarget hunk (9 words in for 5 out). True gross is **5 in
   / 173 out**. `5 − 173 = −168 = 4 − 172` — both close on the same net, so this is not instrument error.
   Worth keeping because it is exactly the failure mode the "gross, never net" rule exists to prevent,
   found *inside the baseline this run was told to reproduce*.

3. **#304's published 63,681 is a *concatenated* word count; the per-file sum is 63,682.** Exactly one
   file — `skills/commander/templates/COMMANDER_SPINE.template.json` — has no trailing newline, so under
   `cat` its last word fuses with the next file's first. Any future successor summing per-file counts will
   see a spurious −1 and think it drifted.

4. **`TREND_SNAPSHOT` §2 listing `_shared` as a 20th role is confirmed as a defect (#411).**
   `scripts/install_constellation.py:discover_skills` skips any directory whose name starts with `_`. The
   corpus is 19 roles at every revision measured.

5. **#304's squash-merge `5d2585b` is a zero-delta row.** `skills/` tree OID is byte-identical at
   `baseline/304-trend-snapshot` and at `5d2585b` (`caefc5d5…`), verified by `git rev-parse` independently
   of the instrument. The n = 2-or-3 judgement call therefore has **zero numerical consequence here** —
   though the structural point stands: this repo cannot express a clean measurement interval across a
   squash-merged boundary.

6. **`rev-list --reverse` manufactures fake role deaths.** 3 of the 6 role "deaths" in history (`docent`;
   `explorer`+`prototyper`) are **walk-order artifacts** — a branch commit that introduced a role sorts
   before a main-line commit that lacks it, so the role appears to die and be reborn at the merge. Their
   own first-parent diffs show no deletion. Any future history walk over this repo needs this correction.
   The three genuine lineage events are `conductor`→`pilot` (`3c24f7c`), `pilot`→`commander` (`90cf856`),
   `crew`→`implementer`+`reviewer` (`a6233e6`).

7. **10 cross-role reference citations are unresolvable under the Admiral's WIDE rule** (9 roles cite
   workbench's `references/checklist-engine.md`; `commander-delegated` cites `references/commander-core.md`).
   Role-local-then-bundle resolution never reaches another role's `references/`. Harmless for a corpus
   total (all 10 targets are already pulled in by their owning role), but it means **the rule does not
   model what an agent actually loads** — relevant to any future substrate work on reference bundling.

8. **`_shared/windows.md` and `_shared/skill-goodness.md` are shipped into every consuming role by the
   installer but named by no `SKILL.md`.** Under a naming-based membership test they fall outside the
   role's own surface, which is a real ambiguity in what "the role's doctrine" is.

9. **The unit question is live and unresolved in the corpus itself.** `scripts/curate_corpus.py` carries
   `SKILL_WORD_TARGET = 400` **and** `SKILL_LINE_HARD_FLAG = 500` — one target in words, one flag in
   lines, on the same artifact, no stated relation. At HEAD the rank order genuinely reverses: `docent` is
   **1st by lines, 6th by bytes**; `admiral` is **4th by lines, 1st by bytes**. Any future "is this small
   enough" question inherits this before it is asked.

*(Suppressed as census-dependent, and deliberately not carried forward: the H1/H2/H3 verdicts and the
computability null. They are in `TRENDS.md` if wanted; they are not offered here as standing findings.)*

## Scope

**Files added** (all inside the allowed scope, plus the engine plan and this result):

- `.agent-work/issue-310/trends/measure_surface.py`
- `.agent-work/issue-310/trends/test_measure_surface.py`
- `.agent-work/issue-310/trends/trends.json`
- `.agent-work/issue-310/trends/panel.json`
- `.agent-work/issue-310/TRENDS.md`
- `.agent-work/issue-310/g1-implementer-plan.json` (+ `.journal`) — mandated by the implementer skill;
  filed at the `#304` convention path, not under `trends/`
- `.agent-work/issue-310/crew-handoffs/g1-result.md` (this file)

**Specific exclusions touched:** **no.** Nothing under `skills/`, `scripts/`, `tests/` or `docs/` is in
the branch diff; `PRE_REGISTRATION.md` is unmodified. Nothing written to the main checkout. No push to
`main`, no merge.

**Behavior changed:** no. Measurement-only; the instrument never mutates the working tree (`ls-tree` /
`cat-file --batch` / `diff`, no checkout).

## Test mode

**Required:** inspection + reproduction. **Satisfied: yes**, with one gap left open by the cut.

- Blocking baseline reproduction: **PASSED**, and proven able to fail (2 decoy revisions, exit 1 each).
- Determinism: **PASSED** — the engine itself ran two full censuses and `cmp`'d them plus the committed
  file at `m3-census`.
- Fixture suite: **31 passed**, mutation-tested red then restored green.
- Gross measurement externally calibrated against #304's own published event (see finding 2).
- `--verify`: clean run **passed** (5/5 stages, 62/62 figures, exit 0). Decoy 1 of 3 — a one-line document
  containing only the keywords — **correctly failed** (`doc has no headline-figures block`, exit 1).
  **Decoys 2 and 3 (tampered dataset number, tampered doc headline) were NOT run** because the stand-down
  arrived first. That is the one unproven claim in this result, and it is named rather than glossed.

## Stop conditions hit

- **Scope cut from the human via the Admiral** — the one that ended the run. Complied immediately; nothing
  deleted, nothing reverted.
- None of the handoff's own stop conditions fired: baseline reproduction passed, the two runs were
  byte-identical, and the census contradicted **one** Commander-verified number, which is reported above
  rather than quietly dropped.

## Out-of-scope observations (triage candidates)

- **#411 is confirmed by measurement**, not just by reading the installer.
- **`rev-list --reverse` role-death artifacts** (finding 6) will bite any future history analysis of this
  repo; worth a note wherever such walks are authored.
- **Cross-role `references/` citations** (finding 7) mean no purely local rule can model an agent's real
  load set — a substrate-shaped observation, and possibly relevant to the rework now under way.
- **Word-vs-line unit split in `curate_corpus.py`** (finding 9) is a live inconsistency in shipped code.

## Workflow Feedback

- **Handoff gaps:** the *"Numbers already verified by the Commander (reproduce these; flag any
  disagreement loudly)"* table presented a **derived** figure (≈272 vs 172) alongside four **directly
  measured** ones, with no marking of which was which. The derived one was the wrong one. Marking
  provenance per row — *measured at rev X* vs *computed from A and B* — would have made the disagreement
  cheap to spot instead of something I had to reconstruct from interval boundaries.
- **Context rediscovered:** the handoff addressed the baselines by tag and gave shas `fc1685a` / `a8d9467`,
  but these are **annotated** tags — bare `git rev-parse baseline/304-trend-snapshot` returns the *tag
  object* (`222f693…`), not the commit. Every address needs `^{commit}`. One line in the handoff would
  have saved a false "the tags have moved" scare.
- **Instructions improvised around:** (a) `docs/agents/engine-config.json` does not exist in this repo, so
  the plan template's `config_ref` points at nothing — the engine degrades gracefully, but the template
  ships a path that is absent by design here. (b) The allowed scope named only `trends/**` and
  `TRENDS.md`, while the implementer skill *mandates* an engine plan file; I filed it at
  `.agent-work/issue-310/g1-implementer-plan.json` per the #304 convention in this same epic, and flag it
  here as deliberate, disclosed scope drift.
- **What would have made this easier:** the `--verify` interface was specified as *"re-derive every figure
  … and reconcile against the headline numbers quoted in `TRENDS.md`"*, but nothing said the doc must
  therefore carry those numbers in a **machine-readable** form. I had to invent the ````headline-figures```
  key/value block and the exact-key-set rule to make the requirement satisfiable at all. Naming that
  contract in the handoff would have removed a design decision from the implementer's plate — and it is
  the single thing that makes the check something other than a grep.

## A note on the cut

No objection, and nothing to appeal. Worth recording for whoever picks this up: the instrument's
*measurements* are substrate-independent (they read git history, not the current design), but the
*bins* are not — `WIDE-ALWAYS-LOADED` is a reconstruction of a loading contract that does not exist in the
tree, and a substrate rework may make it wrong in a way no re-run would reveal. If this is resumed, that
ruling is the first thing to re-examine, ahead of any number.
