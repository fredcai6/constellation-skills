# notes-460 — issue #460, episode records read as prescriptions

Commander `r418-460`, delegated under `LO-460.md`. Worktree
`C:/Programs/constellation-skills-wt/r418-460`, branch `epic-418/b-460-episodes-observations`.

## Isolation proof (first command, before any git operation)

```
$ python scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/r418-460
worktree OK: in C:/Programs/constellation-skills-wt/r418-460
EXIT=0
```

## Pre-declared subsumption candidate set — DECLARED BEFORE THE FIRST CHANGE

Standing obligation from the confirmed spec: name the candidates up front so an empty
subsumption set is visible rather than silent. Drawn from the open tracker under
`theme:episode-store`, `theme:checks-that-cannot-fail`, and `theme:built-not-wired`, plus the
four issues `LO-460` names as "in this neighbourhood".

| # | Issue | Why it is a candidate | Prior call |
|---|---|---|---|
| 1 | #400 | `LESSONS.md`'s preamble instructs agents to read an empty bank — the same read-as-rule inversion, at the retired playbook | named in LO-460 |
| 2 | #403 | the lessons read-path cut is unverifiable; downstream AGENT_GUIDEs still instruct the read | named in LO-460 |
| 3 | #404 | the lessons feedback loop lost its observer — the spine still says "bank for re-observation" | named in LO-460 |
| 4 | #277 | lessons-delta id grammar mismatch (`lesson:foo`) | named in LO-460 |
| 5 | #285 | (LO-460 names it; HITL batch-confirm item) | named in LO-460 |
| 6 | #399 | the store STRUCTURALLY FORCES local diagnosis and FORBIDS honest gaps | K3, issue says out of scope |
| 7 | #342 | no `confirmed` lifecycle-standing | K3, issue says out of scope |
| 8 | #392 | consolidation candidate: "a check that cannot register its own failure" | theme:checks-that-cannot-fail |

Report of what was actually closed is at the end of this file.

## Problem statement (reconciled against LO-460, no human reachable)

**Protected intent.** `episodes/` is a store of *things that happened*. A record that tells a
future agent what to do is the retired learning playbook growing back inside the store that
replaced it.

**The defect.** Of the 32 pre-#447 records in `episodes/active/`, most carry a `workaround`
assertion written in imperative mood, second person, or with a forward-aimed modal. They read
as instructions. The 16 `issue-447-*` records honour the constraint.

**Three things must be true when this run ends.**

1. Every `workaround` in `episodes/active/` reads as a record of what was done.
2. Something that **can fail** keeps it true — or an honest, measured null saying no command can.
3. Records that state a genuine rule are collected as **doctrine candidates for the human**.
   They are not written into `docs/agents/*` and are not parked in a new file. That is the hard
   boundary.

## Baseline reconciliation — where the launch order's assumed baseline is not true

`LO-460` and issue #460 both assume the rewrite can be applied with the writer as it stands:

> "Rewrites go through `scripts/apply_episode_delta.py`'s `amend-assertion` op only ... and each
> amendment appends its history line."

**That is not true of the code.** `_apply_amend_assertion` (`scripts/apply_episode_delta.py:1227`)
changes exactly one thing — the assertion's `lifecycle-standing` — and appends one history line.
Its own comment is explicit: *"kind/strength/statement, every sibling assertion, every mechanical
line, and the retirement block are all left exactly as parsed."* `_validate_amend_assertion`
(`:970`) accepts no `statement` field at all. **There is no write path that can change an
assertion's statement text.**

This is not an oversight in the writer. `docs/EPISODE_STORE.md` §5 is deliberate: its worked
amendment changes only `lifecycle-standing` and explicitly leaves `statement` untouched, and its
prose says an episode *"never needs rewriting later."* Stated precisely, because a cold critic
caught an earlier draft of this note leaning on §5 as if it endorsed restatement: §5 is the
**constraint a restatement has to answer to**, not support for one.

So the issue's acceptance criteria and the store's own design are in genuine tension, and it has
to be resolved rather than papered over. **Departure, applied under inherited latitude** ("how the
rewrite is applied through `apply_episode_delta.py`" is explicitly mine to decide): add one new op
to the writer, `restate-assertion`, which replaces a single assertion's `statement` **and appends
a history line carrying the original wording verbatim**. Nothing is destroyed — the prescriptive
text stays visible in the record's own history, which is what keeps the store honest about what it
used to say. Using `amend-assertion` alone would leave every prescription standing as the live
statement and fail acceptance criterion 1.

## Plan-step rigor mechanisms

**Cold plan critic — RUN.** One critic with no authoring context, reading only `MISSION_FRAME.md`,
`execute.json`, and the code they point at. It returned 12 findings, 2 of them BLOCK. All 12 were
accepted and the plan was re-authored before freezing. The two that mattered:

1. **The naive detector does not survive the corpus.** Measured over all 253 assertion statements
   in `episodes/active/`: 41 imperative hits, 30 deontic-modal hits, 2 second-person hits — about
   65 flags against ~24 real defects. 31 of the 41 imperative hits are `task-intent`, which is
   bare-infinitive *by house convention* — `docs/EPISODE_STORE.md:171`, the store's own canonical
   worked record, is in that form. The naive detector flags the document that defines the format.
   Plan now scopes the imperative rule to `workaround` and `proposed-remedy`, drops bare-modal
   matching entirely (measured: `must`/`should` here are overwhelmingly descriptive), and requires
   the numbers be re-measured after narrowing.
2. **The guard's pass requirement punished the honest outcome.** g2 correctly leaves an ungrounded
   prescriptive record alone; a guard demanding a clean store then goes red on exactly that, and
   the only escapes are to fabricate a rewrite or file the lexicon down until the corpus passes.
   Plan now carries an exception list keyed by (episode id, assertion id) with a required reason
   per entry, seeded only from g2's ungrounded list, and the guard fails on a stale entry too.

Also accepted: two writer dispatch sites, not one (`--dry-run` would silently skip a new op);
real command postconditions at g3-integrate that run the guard green against the real store and
red against a fixture; a second red case not drawn from the corpus; `--strict` so the honest-null
branch does not contradict the red-proof; a test that runs the guard over the real `episodes/` so
it does not run once and never again; g4 retargeted off §10 and given an invariant that §5 be
reconciled; g4 bounded so the doc edit cannot become quiet doctrine promotion.

**The one finding I overrode.** The critic argued the cheaper route was `amend-assertion` with
`lifecycle-standing: superseded` plus a history line — no writer change at all. Rejected, on the
record: that leaves the prescriptive sentence standing as the live statement, so an agent opening
the file still finds an instruction, and the issue's first acceptance criterion is that every
workaround *reads* as an observation. The critic was right on one connected point and the frame
was corrected for it: `docs/EPISODE_STORE.md` §5 is **not** support for restating a statement — its
worked example deliberately leaves `statement` untouched. §5 is the constraint the new op has to
answer to, which it does by preserving the original verbatim in history, and g4 reconciles §5.

**Plan-alternatives (design-it-twice) — NAMED UNTAKEN ROAD.** Not run. The one live design fork
here is restate-vs-annotate, and the cold critic surfaced it and forced it onto the record, which
is what a second plan candidate would have produced. Running a panel to rediscover the same fork
was not worth the budget under the launch order's scope ruling. Recorded as skipped, not silent.

## Execution log — commander-r418-460-b (second commander on this spine)

Took over the lease at the `plan` seam after the first commander's context trip. Discharged
its refresh-request by advancing `plan` (c3 attested against `LAUNCH_ORDER:Mission`, c6's
`verify-frame` run by the engine), then entered `execute`.

### g1 — the `restate-assertion` write path: DONE

Shipped in `scripts/apply_episode_delta.py`: a fourth op kind taking `id`, `assertion`,
`statement`, `history`. It replaces one assertion's statement and appends one history line
carrying the **original verbatim**, built inside the writer from the parsed original so no
caller-supplied field can reach the quoted text. Registered in `OP_KINDS` and at **both**
dispatch sites (`apply_delta`, `_dry_run_log`), each now ending in `else: raise` — the
cold critic's silent-`--dry-run`-skip defect, confirmed against the code and closed.

`tests/test_episode_store.py`: 24 new tests.

**Evidence in the Commander's own hands** (not taken from the crew):
- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_episode_store.py` → `130 passed,
  1 skipped, 50 subtests`, **EXIT=0**.
- Crew-run full suite `1745 passed, 4 skipped, 677 subtests`, EXIT=0 (branch baseline was
  1721/4/643; +24 passed is exactly the added tests).
- Mutation probe M4 re-run by me: widen the field allowlist with `original` and prefer it
  over the parsed statement → **pre-rework suite GREEN (exit 0), post-rework suite RED
  (exit 1)**, source restored byte-for-byte. The guard on this gate can fail.

Reviewer verdict **APPROVE**, load-bearing property verified by code reading *and* by
experiment in an isolated tree copy.

**Rework 1**, commanded after the APPROVE, on the reviewer's first triage candidate: the
field allowlist was not test-pinned, so a later widening could silently reopen the
evidence-destruction hole the op exists to close. Three tests added; the docstring's
"unambiguous tail" overclaim corrected to state that the marker is not unique on the line
and the original is the **last** occurrence.

### Triage candidates logged this run (engine `flag-candidate`)

- `tc1` — `apply_delta` and `_dry_run_log` carry two near-identical dispatch chains; a
  `_dispatch_op` helper would make single-site registration unrepresentable rather than
  merely guarded.
- `tc2` — `_apply_amend_assertion` and `_apply_restate_assertion` share an identical
  four-line prologue; extracting it would touch `amend-assertion`, which #460 has no
  mandate over.
- `tc3` — the engine's survey-mode `r6-fowler` postcondition ships a literal
  `<fowler-pass-record-path>` placeholder and its imperative says to fill it in, but no
  engine verb can: `amend` is refused on surveys, `attest` cannot satisfy a `command`
  postcondition, and `record` refuses with "Do not edit the JSON — use the engine."
  Belongs to **#433**, which owns `scripts/checklist_engine.py` this wave.

### Second context trip, at the g1-integrate seam

HARD trip at 153K against the calibrated 150K cap for `claude-opus-5` (gauge
`fill_fraction` 0.153, observed fresh — not a stale reading from the predecessor). The
engine refused `advance g1-integrate` and a `refresh-request` is filed on that gate
(`e-g1-integrate-2`, `why_ref` `w-3` in `execute.json`).

**What the successor does first:** `advance g1-integrate` (its `review-result` evidence is
already attached with verdict APPROVE; its command postcondition re-runs the store tests).
Then g2. The **g2 implementer handoff is already written** at
`.agent-work/r418-460/crew-handoffs/g2-implement-handoff.md`.

**One thing the successor needs that is not yet in a handoff:** g3 requires a `<pre-g2-sha>`
— the commit that holds the 32 canon records *before* the rewrite — so the detector can be
measured against the corpus as it was. The commit this note lands in is that sha.

**`<pre-g2-sha>` for g3's measurement: `c9d9dd7cf380e497ab8b356122a525e4644605db`** — the g1
commit. `episodes/active/` is untouched at that sha, so it holds the 32 canon records exactly
as they read before the rewrite.

## g2 outcome — verified at the tree, not taken on trust

**48 examined / 32 in scope / 27 restated.** Committed at `770f3e06`. Independently checked:
24 files changed, 54 insertions, 27 deletions — exactly 27 statement lines replaced and 27 history
lines appended, nothing else touched. Zero `issue-447` files appear in the diff, so the 16 records
that already honoured the constraint were left alone. All five UNGROUNDED assertions
(`issue-304-g3-005.d2`, `issue-308-014.a5`, `issue-308-015.a5`, `issue-308-017.a5`,
`issue-308-019.a5`) are unmodified. `query_episodes.py --store-root episodes enumerate` exits 0.

Sample, `issue-308-001.a5` — the record the #447 handoff had pointed a crew at as its migration
precedent, and the issue's own worked BEFORE:

- was: *"Give the harness the same fail-safe discipline as the production code under test: wrap
  per-iteration work in try/except..."*
- now: *"The harness was given the same fail-safe discipline as the production code under test:
  per-iteration work was wrapped in try/except..."*, with the original preserved verbatim on the
  appended `history` line.

## The #461 collision LO-460 asked me to report

`tests/test_episode_negative_control.py::test_canon_episode_store_untouched` blocked the gate. Its
final assertion is `git status --porcelain episodes/` == `""`, so it goes red for **any**
uncommitted change to canon — which is precisely what #460 exists to produce. It reads only git
status, never content, so no restatement can affect it.

The guard is wider than its stated intent. Its docstring scopes it to proving *that test module's*
synthetic consolidation never reached canon, and the assertion two lines above it
(`REPO_ROOT not in seeded_store["root"].parents`) already establishes exactly that. The blanket
dirty check cannot distinguish "a test leaked into canon" from "the running gate legitimately
changed the store and has not committed yet".

Committing cleared it honestly — re-running the failed test itself: `1 passed`, exit 0. No code
change was needed and none was made; `tests/` is outside g2's allowed scope. **This is the
collision LO-460 anticipated when it held #461 to the wave's second half: yes, my work changes what
that control should assert.** Narrowing it to its stated intent is worth its own issue, and its
shape is the same class the episodes it guards are all about — a check whose pass condition is
broader than the property it was written to establish.

## Doctrine candidates — 22, for the HUMAN

Collected only. Nothing written into `docs/agents/*`; no new file created to hold any of it. The
full table with per-candidate grounding is at
`.agent-work/r418-460/crew-handoffs/g2-implement-result.md` § "Evidence 4". The strongest four by
the store's own recorded evidence:

1. `issue-308-002.a5` — before planning, grep the launch order's named defect AND verify a named
   edit target exists at the named address. Nine mentions, six confirmations, zero disconfirmations
   across three epics — the most-confirmed entry in the migrated bank.
2. `issue-308-019.a5` — require a check to demonstrate it ran against something that could have
   failed it; mutation-test the guard and assert the mutation applied. Five-plus instances in one
   epic.
3. `issue-308-008.a5` — run the cold plan critic as mandatory, not bias-to-yes, for any plan whose
   acceptance rests on a before/after measurement or a parser test. Every run that ran it found a
   plan-invalidating defect before dispatch.
4. `issue-308-005.a5` — pair every round-trip test over real artifacts with adversarial fixtures
   built to make the tool answer wrongly. Confirmed three times over three tools.

Four further entries are tool/platform facts rather than doctrine and are listed separately.

## For g4, found by the g2 crew and confirmed

`docs/EPISODE_STORE.md`'s own canonical worked record carries a prescriptive assertion at
`governor-268-003.d2` — *"...should enumerate every sibling template carrying the pattern"*. The
document that defines the record format models the shape this issue removes. That belongs in g4's
reconciliation, and it is a second instance of the same inversion the issue was filed about.

## Subsumption report — 0 of 8 closed

Of the pre-declared set (#400, #403, #404, #277, #285, #399, #342, #392), **zero closed**. None was
reached: #400/#403/#404/#277 sit at the retired playbook and its compiled guides rather than in the
store, and #399/#342/#392 are the K3 cluster the issue puts out of scope. Declaring them was the
obligation; closing none of them is the honest number.
