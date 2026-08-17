# IMPLEMENTER_RESULT — g3-implement, rework 1/3: the archive-gate clause

**Return status: complete**

Work id `567-d1` · gate `g3-implement` · crew `constellation/567-d1/g3/implementer/attempt-2`
Worktree `/home/tommy/projects/constellation-skills/.worktrees/567-d1-doctrine-sweep-guard`
Branch `feat/567-d1-doctrine-sweep-guard` · parent `constellation/567-d1/lane-d1/commander-delegated`

Plan driven: `.agent-work/567-d1/crew-scratch/g3-implementer-attempt-2-74e194cfc852/IMPLEMENTER_PLAN.json`
(4 items, all complete, journal beside it). Session `constellation/567-d1-g3-implementer-attempt-2`.
My door was **unbound** at start (`SPINE_FILE` unset, only `SPINE_PARENT`), so I authored this plan,
bound it, and drove it — the same path the shipped prose describes.

---

## 1. What changed

Two files. `git diff --stat specs/` is `41 +` and `44 +`, **85 insertions, zero deletions** — one line
more per file than the predecessor's `39`/`42`, because the repaired clause re-wraps to six lines
where the old one used four. Nothing outside `specs/**` was edited (`git status --porcelain` filtered
of `.agent-work/` shows only the two specs).

The repair is **byte-identical in both files** — `md5sum` over the clause in each:
`4070a2008c867390757bdf0800ca9df5` for both.

### 1a. Before (both files, identical)

```
process: with your own lease held, binding a second checklist is REFUSED --
"one door drives one spine at a time ... release it first" -- and the escape
that refusal names is barred for you, because the archive gate requires the
lease to cover every journaled action, so releasing it to reach a second
checklist fails your own closeout. Read the two halves together and the rule is
```

### 1b. After (both files, identical)

```
process: with your own lease held, binding a second checklist is REFUSED --
"one door drives one spine at a time ... Release it first" -- and that
escape is not yours to take: your role skill holds the lease open until
your last action, because the lease must cover every journaled action, and
releasing it early fails the terminal provenance check. Dispatched without
a spine of your own you arrive holding no lease -- nothing to release, and
the escape never arises. Read the two halves together and the rule is
```

Two changes, not one.

1. **The blocked clause**, replaced as the handoff directed: the inherited name (**terminal
   provenance check**, *the lease must cover every journaled action*) instead of a renamed gate, and
   the escape scoped to who actually faces it — the role holding its own lease. The second sentence
   is the honest answer for the other reader: a crew that arrives unbound has no lease to release, so
   the escape never arises for it. No closeout is claimed for a role that has none.
2. **`release it first` → `Release it first`.** The specs present that fragment as a verbatim quote
   of the door. It is not: the refusal's second sentence begins `Release it first (...)`. Found by
   the probe, not by reading — see §3a. Fixing it is squarely close criterion 7, since a quotation is
   an assertion about what another component says.

`archive gate` now appears nowhere in `specs/` or `skills/`. No other line of the diff moved: the
wrap was laid out so the last new line ends exactly where the old one did, leaving the following
lines untouched.

**On the reviewer's duplication observation.** Both files still carry the paragraph. TOML has no
include, comments are dropped, and a new key reaches no reader (the predecessor measured this and I
re-measured it, §3d), so there is no way to state the fact once that both files can carry — and the
handoff barred restructuring to achieve one. What I did instead is make the pair **checkable**:
`verify_claims.py` extracts the clause from each file, whitespace-normalises, and fails if they
diverge. The duplication stays; silent divergence cannot.

---

## 2. Why the new clause is true, claim by claim

| # | The claim now in both files | What makes it true |
|---|---|---|
| 1 | "your role skill holds the lease open until your last action" | `skills/implementer/SKILL.md:17` and `skills/reviewer/SKILL.md:17`: *"only then `release` the engine session lease **as your very last action**"*. Checked against **both** the repo copy and the installed copy a dispatched crew actually loads. |
| 2 | "the lease must cover every journaled action" | Same two lines, verbatim — this is the inherited wording, not a paraphrase. |
| 3 | "fails the terminal provenance check" | Same two lines name the check: *"fails the **terminal provenance check**"*. The specs invent no third name, which was the handoff's first requirement. |
| 4 | "Dispatched without a spine of your own you arrive holding no lease" | `run_crew._crew_door_env(spine=None)` binds neither variable, so the door is unbound (§3b); an unbound door has nothing to hold a lease on, measured directly — `spine_status` REFUSES with "no spine is bound to this door". I am the live case. |
| 5 | "nothing to release, and the escape never arises" | Follows from 4 and is measured: in the `unbound-then-bind` probe case, `spine_bind` succeeds with no release step anywhere. |

**What the clause deliberately does NOT claim.** It does not say a mechanical gate enforces the
terminal provenance check on this path. It says the role's own skill holds the lease open — which is
where the rule actually lives. The reviewer's `tc1` stands untouched and unclosed: the only
mechanical enforcement is `evals/euler-*/checks/spine_completed.py::journal_consistent`, which no
live path calls. Naming role doctrine as role doctrine is what keeps the sentence true; a future
author who checks it finds the line in their own skill, which is the point of stating a reason.

---

## 3. Evidence

Every assertion left standing in the added prose — not just the repaired clause — is enumerated as an
**executable check**, because that is what the BLOCK was about. Two scripts, both under the crew
scratch dir, neither touching a repo file:

- `.agent-work/567-d1/crew-scratch/g3-implementer-attempt-2-74e194cfc852/verify_claims.py` — **51
  checks, all PASS, exit 0.**
- `.agent-work/567-d1/crew-scratch/g3-implementer-attempt-2-74e194cfc852/door_probe.py` — **16
  checks, all PASS, exit 0**, across three fresh processes.

Both are wired as `command` postconditions on my own plan, so the **engine re-ran them at advance**,
not just me at a terminal.

### 3a. The refusal, re-measured — and the quote that was not verbatim

`door_probe.py` runs three cases, each its own process (the door resolves `SPINE_FILE` at import, so
one process cannot hold two states — CREW_CONTEXT "Two Engines Are Alive In Your Session"):

| case | expected | observed |
|---|---|---|
| `bound-then-rebind` | REFUSED | REFUSED, and `spine_status` afterwards still shows the **first** spine |
| `released-then-rebind` | SUCCESS (positive control) | SUCCESS — the *identical* bind, so the refusal is conditioned on holding your own lease and nothing else |
| `unbound-then-bind` | status REFUSED, bind SUCCESS | as expected; `SPINE_SESSION` returned equals `spine_lifecycle.session_id_for(work_id)` |

The live refusal, verbatim:

```
REFUSED: this door still holds an active lease on '...probe-a.json' as
'constellation/567-d1-g3i2-probe-a', and one door drives one spine at a time. Rebinding this door
now would leave that lease held by nobody. Release it first (`spine_lease` with action 'release'),
then call `spine_bind` again.
```

**The probe reads the quoted fragment out of the specs themselves** — `tomllib` → the imperative →
the one quoted string containing "one door drives one spine" → split on the ellipsis → each half must
appear in the live refusal. That is why it caught `release` vs `Release`: it compared the shipped
text against the door, not against a copy I had typed. It is also its own red-proof — it ran **red on
exactly that check** before the fix and green after, on unchanged probe code.

### 3b. The dispatch environment, measured under a *controlled* ambient env

| `_crew_door_env` call | result |
|---|---|
| `spine=<path>` | `SPINE_FILE` + `SPINE_SESSION` + `SPINE_PARENT` bound |
| `spine=None`, no ambient pair | `SPINE_PARENT` only — door unbound, no lease of its own |
| `spine=None`, dispatcher holds a pair | **the dispatcher's own pair, passed through verbatim** |

The third row is a finding, and it is why this check failed the first time the **engine** ran it:
the engine ran it from a door process that had `SPINE_FILE` set, my shell did not, and the same
script gave two answers. The script now clears and sets the ambient env explicitly, so it measures
the launcher instead of the environment it happens to run in, and passes identically in both. See §5.

### 3c. The engine behaviour behind the reviewer spec's dialect sentence

Measured on `checklist_engine`, not on the text describing it:

```
checklist_engine.advance(survey) -> EngineError 'advance is for gated checklists; use record'
checklist_engine.record(gated)   -> EngineError 'record is for survey checklists; use advance'
```

The split is symmetric, so *"the survey dialect is not the gated one"* is a real division rather than
a convention. And the "shared with every other plan" claim is exercised on **both** dialects:
`attest` + `flag_candidate` + `block` all succeed on each. That check needed care — the survey
template's only postcondition is engine-checked, so probing the shipped conditions measures the
condition's *kind*, not the dialect. The probe injects the same qualitative condition into both
in-memory copies, and separately confirms that an engine-checked condition refuses `attest` on
**both** for the same reason.

### 3d. The header comment's compiler claims, re-derived

| comment claim | measurement |
|---|---|
| `_compile_gate` builds from a FIXED field list | added `doctrine` to a gate → absent from the compiled task (14 keys, listed by the check) |
| `compile_spec` does the same at top level | added top-level `doctrine` → absent from the compiled spine |
| `spec_shape_faults` has no unknown-key fault | fault list with and without two invented keys is **identical** (0 vs 0) |
| comments are dropped | the header comment's own text is absent from the compiled spine, while `one door drives one spine at a time` **and** `terminal provenance check` are present |
| `compile_condition` folds `because` into the statement | `compile_condition(qualitative)` → `'a statement -- QUALITATIVE: the reason'` |

### 3e. Tool inventory, decision id, and the reviewer's cross-reference

- All nine tools the two imperatives name exist in the door's own `TOOLS`, with the verbs claimed:
  `spine_evidence` ⊇ {attest, attach}, `spine_lease` ⊇ {claim, release}, `spine_capture` ==
  {append, flag-candidate}, `spine_halt` ∋ block, `spine_survey_result` == {record, consolidate} and
  described "Survey-type plans only". `spine_amend`'s `authority` is **required**, so "under a named
  authority" is accurate.
- **No tool takes a session id**: every tool's `inputSchema` properties scanned, 0 hits across 12.
- `decision:one-spine-per-process-stands` is real, and cited where the behaviour lives —
  `scripts/mcp_spine_server.py` and `docs/CHECKLIST_ENGINE_DESIGN.md`.
- The reviewer spec's *"r6-fowler's own REPAIR PATH below"* points at text that is there.
- Neither `constraints` array repeats the withdrawn archive-gate reason.

### 3f. Guard, parse, compile, scope

```
$ python3 -c "import tomllib; ... "                      -> toml ok
$ grep -rn 'archive gate' specs/ skills/                  -> (nothing, exit 1)
$ python3 -m pytest tests/test_cli_retirement_guard.py -q -> 2 failed, 17 passed
$ grep -oE 'specs/[A-Za-z0-9_./-]+' /tmp/g3r2-guard.log   -> (nothing)
$ non-workbench site filter                               -> (nothing)
$ generate_spine --check-only (both specs)                -> would compile clean
$ git status --porcelain, minus .agent-work/ and specs/   -> (nothing)
```

The two failures are byte-identical to the predecessor's baseline and to mine before I started: both
sites are `skills/workbench/references/checklist-engine.md` and `skills/workbench/SKILL.md`, lane
D2's fenced files, which `g5-final` re-checks after the rebase.

### 3g. Red-proof, because a check that cannot fail is indistinguishable from one that passed

Reintroduced the withdrawn wording into `specs/implementer.spine.toml` (mutation asserted applied),
re-ran `verify_claims.py`:

```
48/50 claim checks passed
  FAILED: the blocked clause is gone: neither spec names an 'archive gate'
  FAILED: both specs carry the repaired clause with identical wording
```

Restored from a byte copy → `50/50`, exit 0. The second failure is the linked-pair check firing on
divergence, which is exactly its job. (The 50→51 difference is the ambient-env case added afterwards
in §3b.)

---

## 4. Close criteria

| # | Criterion | Status |
|---|---|---|
| 1 | Both specs name the door | met — unchanged from attempt 1 |
| 2 | Both state the second-checklist truth | met — the refusal, its now-verbatim quote, and a barred escape that is true for each reader |
| 3 | Guard reports no violation at any `specs/` address | met — §3f, re-verified by the engine at each advance |
| 4 | Both files still parse as TOML | met — §3f, plus a clean compile |
| 5 | Schema question settled and reasoned | met — untouched from attempt 1, and the comment's five claims re-measured (§3d) |
| 6 | Dangling `config_ref` recorded with evidence | met — untouched; the candidate still stands |
| **7** | **No claim names a gate, check or file that does not exist or does not do what the claim says; every remaining assertion verified** | **met — §2 and §3, 67 executable checks across two scripts** |
| **8** | **Both files parse as TOML; guard reports no violation at any `specs/` address** | **met — §3f** |

Constraints honoured: `specs/**` only; no door path promised that the measurement does not show, and
none denied that it does; no command line shown anywhere in the prose (no bracket, brace, `$` or `%`
placeholder at all); no issue filed; nothing edited under `tests/`, `skills/`, `scripts/`,
`episodes/`, `docs/` or `map/INDEX.md`.

**No stop condition was hit.** One true statement did cover both files' readers without splitting the
paragraph, and no remaining assertion turned out unverifiable.

---

## 5. One finding for the Commander

**`run_crew.py` hands a no-`--spine` child the dispatcher's own spine, when the dispatcher has one.**
Measured (§3b). `_crew_door_env`'s docstring states the intent — with no `spine`, "the
inherited-environment route is genuinely untouched, both variables together" — and the alternative it
rules out (deriving `SPINE_SESSION` unconditionally) was a worse bug. But the consequence is that
such a child's `spine_status` **succeeds and shows the parent's spine**, with no refusal to warn it,
while the crew skills open by telling it that spine is its own. Every crew in this lane hit the
benign version: the pair was absent, `spine_status` refused, and the refusal text told them what to
do. The hazardous version differs only in the dispatcher's environment.

**Recorded, not fixed** — `scripts/**` and `skills/**` are fenced from this lane. The existing
`.agent-work/567-d1/triage-candidates/headless-dispatch-inherits-parent-spine.md` already carries the
observed symptom from a headless probe, so I **updated it in place** with the mechanism and the
measurement rather than opening a duplicate; the doctrine half belongs to the existing
`dispatched-crew-spine-is-not-bound.md`. Flagged through the door as `tc1`. **No issue filed.**

This is also why the shipped prose is worded as it is: unbound is a state the door **reports**, not
one a role can infer from how it was dispatched.

---

## 6. Map Impact

No architecture map exists, so this is a note for whoever builds one, in the inbound anchor
vocabulary. It adds one line to the predecessor's, and does not restate it:

- `specs/implementer.spine.toml`, `specs/reviewer.spine.toml` — their second paragraph is a **linked
  pair**: near-verbatim in both files, with no include mechanism available. A map entry for either
  should say so, and point at the check that now enforces it.
- `run_crew.py::_crew_door_env` — the **spine-pair pass-through** is a doctrine surface, not just a
  launcher detail: it decides whether a dispatched crew's door is unbound or silently bound to its
  parent. Reference it from any entry about crew dispatch.
- No structural, capability or dependency change. Prose only.

---

## 7. Workflow Feedback

**What helped.**

- **The handoff quoted the blocked clause verbatim, gave the measurement table row by row, and named
  the replacement wording's source (`skills/{reviewer,implementer}/SKILL.md:17`).** That is the
  difference between a rework and a guess: I never had to re-derive what was wrong, only to verify it
  and write the replacement. Zero clarification cost.
- **"Prefer accuracy over completeness … cut it rather than hedging it."** That line is what produced
  the second sentence instead of a hedge. Without it the temptation was to keep the old reasoning and
  qualify it, which would have shipped a longer paragraph that was still partly false.
- **"Verify each factual assertion you leave in place, not just the one you fixed."** This is the
  instruction that earned its keep twice: it found the `release`/`Release` quotation defect and the
  ambient-env behaviour in §5. Neither was reachable by reading the prose carefully; both fell out of
  writing the assertions down as code. **Keep this line in every rework handoff.**
- The POSIX/`dash` warning and the `test_gauge_chain_writer_to_trip.py:604` warning were both correct
  and both saved a real failure. Inherited from the original handoff and still paying.

**What got in the way.**

- **The reviewer verified the quoted fragment by eye and reported it "verbatim"; it was not.** The
  BLOCK report says *"The fragment both specs quote is verbatim"* — one word's capitalisation off,
  inside the same sentence the whole gate turns on. This is not a criticism of the review, which was
  otherwise the most useful document in this gate: it is evidence for its own thesis. A quotation is
  an assertion about another component's behaviour, and the standard the review itself cites —
  *assert against behaviour, never against text that describes it* — applies to it. The cheap durable
  fix: when prose quotes a runtime string, the check should **extract the quote from the file** and
  match it against the live output, which is now how `door_probe.py` works and is reusable.
- **The engine ran my check in an environment mine did not have, and got a different answer.** My
  shell had no `SPINE_FILE`; the door process did. Same script, same repo, opposite verdict. That is
  a genuinely useful refusal — it caught an environment-dependent measurement I would otherwise have
  shipped as evidence — but it cost a debugging cycle because a `command` check's failure is reported
  as `postconditions unmet ['c1']` with **no captured stdout/stderr**, and `status_detail` was `{}`.
  Surfacing the failing check's output in the refusal would have collapsed that cycle to one read.
- **`docs/agents/CREW_CONTEXT.md`'s Python Invocation section is stale** and states the opposite of
  what is true: it records `python3` as having no pytest, measured 2026-08-10. Measured now, all
  three of `py`, `python`, `python3` report pytest 9.1.1. The section's own advice — check before you
  run — is what saved it, but a crew that trusted the recorded measurement instead of the method
  would have avoided the interpreter the handoff's own commands use. Already a staged candidate
  (`crew-context-python-invocation-stale.md`), so I did not open a second.

**My own mistakes.**

- My first version of the shared-verb check probed the survey template's shipped conditions and read
  the resulting refusal as a falsification of the prose. It was measuring condition *kind*, not
  dialect. Caught because the failure message named the reason (`c1 is engine-checked; cannot
  attest`) — good engine error text did the work my probe design should have.
- I wrote three checks whose expectations I had assumed rather than looked up (the session-id format,
  the `spine_survey_result` description string, "the first item has a postcondition"). All three
  failed on first run and all three were my error, not the code's. Cheap to fix, but the pattern is
  worth naming: when writing a verification script, read the value before asserting on it, or the
  first run measures the author rather than the subject.
- I nearly left the `release`/`Release` mismatch as an observation on the grounds that the handoff
  said one clause. The reason to fix it is that it is the *same* defect class as the BLOCK — an
  assertion inside a sentence advertising a measurement — and it sits three words away.

---

## 8. Stop-hook note

If the Stop hook fires with `SPINE MID-FLIGHT: gate execute is still open`, the answer is the same
one the previous two crews recorded: that is the Commander's spine, not mine. My own plan is driven
to `DONE` and my lease released as the last action. `g3-implement` is `in-progress` because this
crew is what fills it, and it closes when the Commander verifies this artifact. Recorded here only so
the count is visible; the durable fix remains a lease-ownership check in the hook.
