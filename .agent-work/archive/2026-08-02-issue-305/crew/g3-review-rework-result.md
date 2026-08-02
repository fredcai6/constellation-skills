# REVIEW_RESULT — g3-review (ATTEMPT 2, review of record for the whole gate)

## Assigned Gate
`g3-review` — issue #305, epic #298. Diff under review: `git diff 3f787a3..HEAD`, one
non-`.agent-work` path, `tests/test_episode_negative_control.py` (new, 1146 lines), plus
commit `283175b` on top.

## Result
**`APPROVE-WITH-FOLLOWUPS`**

Stated without rounding, because you asked: **the negative control is real, falsifiable,
and it now resists the attacks that reopened it.** All three named attacks scored RED with
exactly the assertion text you predicted. Five new mutations outside the spent table were
all caught. What did **not** hold is prose: two docstrings assert guarantees the code does
not deliver, and one fixture is under-powered on one field. None of the three makes a
conclusion unsupported, so this is not a BLOCK — and none is cosmetic, so it is not an
APPROVE.

**Applying your governing rule verbatim** ("BLOCK if an attack scores green *and that green
means a conclusion is unsupported*"): two of my mutations scored green (N1, N2). Neither
green means the gate's conclusion — `decision:zero-agent-effort-is-literal` — is
unsupported. N1's green means the *self-enforcement* of independence has a narrower reach
than its docstring claims; the shipped oracle **is** independent, and I proved the guard
fires on the direct form. N2's green means a *sentence* overstates a count; the underlying
property is inherent and your own reasoning about it is correct. So: findings to report,
not a block. I did not round.

Survey: `.agent-work/issue-305/g3-review-rework/review.json`, 17 checks, all visited,
consolidated under lease `sess-g3rev2`, released as the last action.
Fowler record: `.agent-work/issue-305/g3-review-rework/fowler-pass.json`,
`verify_fowler_pass.py` exit 0.

---

## Baseline, derived not inherited

`python -m pytest -q` in the worktree, run by me before touching anything:

```
1487 passed, 2 skipped, 472 subtests passed in 131.67s
```

Exactly your stated number. Re-run **after** all eleven mutation batteries:
`1487 passed, 2 skipped, 472 subtests passed in 131.48s` — identical, which is the real
proof the tree came back rather than the OIDs alone.

---

## Method — how every colour below was made trustworthy

A single harness (`scratchpad/mutrun.py`) ran every battery. It:

* reads the file as **bytes**, decodes, normalises CRLF→LF for editing, and writes back in
  the file's **own** line ending — so **#319** cannot silently produce a zero-site match;
* **asserts the hit count of every replacement**, so "pattern matched nothing" raises
  instead of reading as "mutation applied, still green". *This fired for real once* — see
  the N2 note below;
* proves liveness by **blob OID change** for every file mutation, and for module-level
  mutations additionally prints the marker attribute from **both a spawned subprocess and
  the in-process interpreter**, because the engine runs as a subprocess here;
* restores in a **`finally:`** and **OID-checks all three tracked files pre- AND
  post-battery** — every battery reported `post-battery tree clean: True`;
* writes all output as UTF-8 to a file, never through a cp1252 console, and never pipes to
  `head` (your two script-death modes).

**No assertion below is a bare non-zero exit.** Every one is quoted assertion text.

Final independent tree check, outside the harness:

| file | `HEAD:` | worktree `hash-object` |
|---|---|---|
| `tests/test_episode_negative_control.py` | `796dd5297982…` | `796dd5297982…` |
| `scripts/episode_capture.py` | `8a38e33d1c12…` | `8a38e33d1c12…` |
| `scripts/context_manifest.py` | `77604fd15d3e…` | `77604fd15d3e…` |

`git status --porcelain --untracked-files=all` shows only `.agent-work` churn.

---

## The three named attacks

### A1 — composer → hardcoded constants → **RED**, as predicted

Mutation: `scripts/episode_capture.py`'s `mechanical_fields` redefined to return ten
plausible, validator-passing constants. Liveness: blob `8a38e33d1c12 → cbbb9ec3fbd8`;
`__NC_MUT__` read back as `'A1'` from **both** a spawned subprocess and in-process.

**7 failed, 8 passed.** The assertion you named, verbatim:

```
test_claimed_parent_topology_yields_the_full_mechanical_group:744
>       assert compare_fields(expected, parent.compose()) == []
E       AssertionError: assert ['run', 'proj...efusals', ...] == []
E         Left contains 10 more items, first extra item: 'run'
```

**All ten fields named.** Also red: the child topology test, the seam test (proving the
file mutation reached the engine **subprocess**, not merely the in-process `compose()`
path), `test_a3` (`ctx-some-run-g1@000…` vs `ctx-a3-null-g1@71d644…`), and R1–R4.

### A2 — delete the ground-truth tally → **RED**, as predicted

Mutation: all five issue-time increments neutered (`+1` → `+0`) — `_refusals`, `_reopens`
×2, `_failed["g2"]`, `_rework["g1"]`, `_rework["g2"]`. Liveness: blob
`796dd5297982 → 15d37e101537`. **7 failed, 8 passed.**

| test | assertion |
|---|---|
| parent topology | `['refusals', 'reopens', 'rework-count', 'failed-commands'] == []` |
| child topology | `['reopens', 'rework-count', 'failed-commands'] == []` — `refusals` correctly absent, the topology delta behaving |
| seam | same four |
| R1 | `At index 5 diff: 'artifact-ref' != 'refusals'` |
| R2 | `['refusals','reopens','rework-count'] == ['failed-commands']` |
| R3 | `['role','reopens','rework-count','failed-commands'] == ['role']` |
| R4 | `['refusals','reopens','rework-count','failed-commands'] == ['reopens']` |

The named fields, per topology. Never a bare exit code.

### A3 — declared refs → nothing → **RED**. But your handoff names the wrong test.

I ran **two** forms, because the single form does not separate the two facts at stake.

**Form 1 — all-null rows, files really present.** `context_manifest.rows` forced to emit
`rev: null`. Liveness: blob `77604fd15d3e → a14ad48e59f3`, `__NC_MUT__='A3'` from a spawned
subprocess and in-process. **1 failed, 14 passed:**

```
test_declared_context_is_delivered_and_pinned:855
>       assert compare_manifest_rows(want, manifest) == [], (key, manifest["files"])
E       AssertionError: ('parent', [{'path':'seed.txt','rev':None,'root':'repo'},
E                                   {'path':'changed_by_the_run.txt','rev':None,'root':'repo'}])
E       assert ['seed.txt', ..._the_run.txt'] == []
E         Left contains 2 more items, first extra item: 'seed.txt'
```

**Every declared path named** — exactly the requirement. `context-manifest-ref` stayed
correct, which is expected (a byte-pin over the manifest's own bytes) and is **not** the
failure, precisely as you said.

**Form 2 (A3b) — the declaration silently dropped, `files: []`.** Blob → `77160b7a88b5`.
**2 failed, 13 passed** — and this is the one that reaches the new test:

```
test_a3_a_null_manifest_does_not_read_as_success:892
E       assert [] == [('repo', 'seed.txt', None), ('repo', 'changed_by_the_run.txt', None)]
```

So "declared but not delivered" vs "never declared" **is** genuinely enforced, and the new
test is itself falsifiable.

> **HANDOFF DEFECT (minor, #1).** Your A3 row names
> `test_a3_a_null_manifest_does_not_read_as_success` as *"the assertion that should say
> so"*. It is not. That test builds its **own** repo in which neither declared file
> exists, so its expected rows are null too — under the all-null mutation it is
> null-vs-null and stays **green**, which is the same shape as attempt 1's A3 green. The
> test that actually discriminates a dishonest manifest is
> `test_declared_context_is_delivered_and_pinned`. Both tests are real and jointly close
> the hole, so this is a mis-attribution in the brief, not a gap in the artifact — but had
> I asserted only against the test you named, I would have reported A3 green.

---

## New mutations — six, none in the spent table

| # | mutation | outcome |
|---|---|---|
| **N1** | oracle calls the producer through an **aliased import** (`… as _rt_alias`) | **GREEN — 15 passed → F1** |
| **N1b** | N1 **plus a real under-count defect** in `reopen_total` | caught (2 failed) — harm bounded |
| **N1c** | the **unaliased** direct call | caught — the guard is not vacuous |
| **N2** | `work_id` = a hand-typed sentence → the `run` mechanical field | **GREEN — 15 passed → F2** |
| **N3** | `MECHANICAL_GROUP` shrunk to one element | caught (4 failed) |
| **N4** | drive materially less work; oracle follows in lockstep | caught (3 failed) |
| **N5** | flag value beginning with `--` | caught (1 failed) |
| **N6** | `artifact-ref` truncated to `out[:1]` **with two staged paths** | caught (6 failed) → **F3** |

### F1 — the independence guard is evaded by an *aliased* import (followup)

Mutation: `from episode_capture import reopen_total as _rt_alias` at module level, and the
oracle's `reopens` expectation rewired to
`_rt_alias(json.loads(self.path.read_text(...)))` — textbook comparing-the-thing-to-itself.
Blob `796dd5297982 → 8071ded78093`. **Result: 15 passed, exit 0. Fully green.**

All three layers miss it:

* **(a)** patches the module *attribute* `episode_capture.reopen_total`; `_rt_alias` holds
  the original function object bound at import, so nothing raises.
* **(b)** collects identifiers from `_ControlRun.expectations` and checks them against
  `FORBIDDEN_IDENTIFIERS`; it sees `_rt_alias`, which is not in the set. `reopen_total`
  never appears as a `Name` or an `Attribute` anywhere in the scanned source.
* **(c)** prose untouched.

The docstring says layer (b) exists because *"(a) is defeated by exactly one thing: a name
bound at import time (`from episode_capture import reopen_total`), which no attribute patch
can reach."* That is the exact binding used here; adding ` as _rt_alias` defeats (b) too.

**Harm is bounded — measured, not reasoned.** N1b re-ran N1 alongside a **real** under-count
defect in `reopen_total` (run-scoped 2 collapsed to step-scoped 1; `__NC_MUT__='N1b'` from a
spawned subprocess and in-process, blob `8a38e33d1c12 → 0d685836c450`). **2 failed.** The
primary assertion `compare_fields(expected, parent.compose()) == []` **passed** — the oracle
inherited the defect, exactly the harm the guard exists to prevent — but the defect was still
caught by two other guards:

```
assert [1, 1, 3, 4] == [1, 2, 3, 4]        # the literal tuple, same test, line 747
At index 1 diff: 1 != 2

assert [] == ['reopens']                    # test_red_proof_sharp_inflated_reopens
```

And N1c confirms the guard is **not** vacuous — the unaliased form fires with the exact
message *"the oracle called `episode_capture.reopen_total`: the expectation is NOT
independent of the thing under test"*. This independently reproduces your V3 rather than
inheriting it.

So: a genuine narrowing of a genuine guard, not a return to vacuity. **Cheapest fix:** have
layer (b) reject any name in the scanned scope whose **bound object is identical to** a
`FORBIDDEN_PRODUCERS` function — an identity check over the module globals, which no
aliasing can dodge. Or, if that is more machinery than the risk warrants, correct the
docstring to say what layer (b) actually covers.

### F2 — the census counts a subset it chose; the docstring reads it as a total (followup)

Mutation N2: the parent's `work_id` (and its directory, which must move with it per #360)
replaced with the hand-typed sentence
`ctl-parent-a-run-id-I-typed-by-hand-as-narrative-prose`. Blob
`796dd5297982 → 66954add7598`. **15 passed, exit 0**, including
`test_control_records_nothing_agent_authored`.

**Effect proven at the seam, not inferred.** I read the snapshot `episode_capture` wrote on
its own out of the pytest tmp dir:

```
{'run': 'ctl-parent-a-run-id-I-typed-by-hand-as-narrative-prose',
 'project': 'mechanical-control-repo', 'role': 'commander', 'spine-step': 'g2'}
```

A hand-authored sentence sitting in the `run` **mechanical** field. This is V4's exact
shape, on a field V4 did not cover.

**Root cause.** The census is `_flag_pairs` over `run.calls` — **flag values on recorded
argv, and nothing else**. It structurally cannot see the plan file (`work_id` → `run`, gate
`id` → `spine-step`), the `--file` path (which `_run` prepends but deliberately does not
record), or the temp repo directory name (→ `project`).

**Answering your direct ask — the third blind spot, found your way.** I enumerated all
**31** flags the engine's argparse block accepts and diffed them against
`AGENT_TEXT_FLAGS`. Fourteen are unnamed; ten of those are genuinely not agent-composed
free text (`--dry-run`/`--force`/`--mechanical` are `store_true`; `--which`/`--result` have
`choices`; `--file`/`--worktree`/`--from-child`/`--delta` are paths; `--session-id` is a
structural id). **Four carry agent-composed strings and are still unnamed:**

* **`--cond`** — **this is the third blind spot, and it is sharper than the above because
  it sits inside the census's own stated scope.** It is *sanctioned* in
  `ALLOWED_FLAGS["attest"]`, its value `"c1"` is a string the harness itself authored in
  `_plan`, it is passed as a flag value on an issued argv — and because
  `AGENT_TEXT_FLAGS` does not name it, it never enters `text_bearing`. So even restricted
  to argv flag values, "exactly two" is false; the true statement is "exactly two **among
  the subset of flags I chose to call text-bearing**".
* **`--evidence`** — your own V2, still absent.
* **`--type`** — `attach`, `required=True` with **no** `choices`, i.e. an arbitrary string.
* **`--from`** — `flag-candidate`.

The last three are covered by the closed-world arm (`attach` and `flag-candidate` are not
sanctioned verbs), which is the right defence and is your own V2 conclusion. `--cond` is
covered by nothing; it is harmless only because it feeds no mechanical field.

**On the question you asked me to answer plainly: your reasoning is *not* wrong.** A guard
firing when the `role` string "looks like prose" would be exactly the unfalsifiable theatre
you named — `role` must be *some* supplied string. I endorse the decision without
reservation. But that reasoning justifies the **decision**, not the **sentence**, and it
applies verbatim to `run`, `spine-step` and `project` — three more fields in identical
positions the sentence does not acknowledge. **No new machinery is warranted.** The fix is
to scope the claim to what is measured, and to add `--cond`/`--evidence`/`--type`/`--from`
to `AGENT_TEXT_FLAGS` so the reporting matches the closed world.

### F3 — the fixture is under-powered on `artifact-ref` (followup; attempt 1's F4 confirmed open)

Mutation N6: I staged a **second** path in the fixture and truncated the producer to
`out[:1]` (`_artifact_refs`, `__NC_MUT__='N6'` from a spawned subprocess and in-process,
blob `8a38e33d1c12 → 4e07f293123f`). **6 failed, 9 passed** — parent topology, child
topology and the seam test all fire:

```
assert ['artifact-ref'] == []
Left contains one more item: 'artifact-ref'
```

So **`compare_fields` discriminates a multi-element `artifact-ref` correctly — the
machinery is sound.** The gap is purely the fixture: as shipped it stages exactly **one**
path, so `out[:1]` is a no-op and the truncation is undetectable. That is precisely why
attempt 1's M8 was uncaught. **This is the cheapest hardening anywhere in the file: one
extra staged file turns a previously-uncaught mutation red, and I measured that it does.**

### N3, N4, N5 — the "pass while testing nothing" attacks all fail

* **N3** (`MECHANICAL_GROUP` shrunk to one element — the purest form of the attack):
  **caught, 4 failed.** `assert sorted(expected) == sorted(MECHANICAL_GROUP)` →
  `['artifact-re...reopens', ...] == ['run']`, plus R2/R3/R4 collapsing to `assert [] ==
  ['failed-commands']` / `['role']` / `['reopens']`.
  *Observation:* R1 asserts `compare_fields(...) == list(MECHANICAL_GROUP)`, so it shrinks
  in lockstep and stayed green. The `sorted(expected) == sorted(MECHANICAL_GROUP)` identity
  is load-bearing and worth keeping.
* **N4** (drive less work; the issue-time oracle follows in lockstep): **caught, 3 failed** —
  but **not by the floor you worried about**. Advances fell 14 → 8, so `advances >= 8` did
  not fire; you were right that it is soft. What fired is the literal tuple:
  `assert [1, 2, 0, 1] == [1, 2, 3, 4] / At index 2 diff: 0 != 3`. **The non-vacuity weight
  is carried by the hardcoded `[1,2,3,4]`, not by the floor** — the same guard that saved
  N1b. It exists only on the *parent* topology test; noted, not flagged, since the child's
  deltas are the two REFUSED fields and those are separately pinned.
* **N5** (`_flag_pairs` given a value beginning with `--`): its docstring claims the census
  is *"strictly more likely to fire… never less"*. **Verified behaviourally: caught,
  1 failed**, `violations = ['parent: reopen carries un-sanctioned flag --why=agent prose
  smuggled past the pair parser=None', …]` ×4. **This docstring meets the standard the other
  two do not.**

---

## Fowler refactoring pass

`verify_fowler_pass.py` exit 0 — `smells=12, flagged=['duplicated-code',
'shotgun-surgery', 'comments-as-deodorant'], overridden=['long-method',
'primitive-obsession']`.

**Overrides, each with a named standard and a reason:**

* **long-method** — `drive` and `expectations` are long. Overridden: the handoff constraint
  *"the oracle increments its own expectation at the moment it issues the triggering call"*
  makes call/tally **adjacency** the property under test; extracting helpers would recreate
  the M5 defect the rework was reopened to fix.
* **primitive-obsession** — bare field-name strings. Overridden: the file's own documented
  rule is that the comparison returns field **names** so red-proofs can assert
  `mismatches == ["failed-commands"]`, and those strings are the wire-level names that
  cross into JSON. `REFUSED` **is** a dedicated sentinel class, showing the judgment was
  applied rather than skipped.

**The headline smell is `comments-as-deodorant`, and it is a real defect, not a style
note.** In two places the prose asserts guarantees the code does not deliver (F1, F2) —
which is exactly the doctrine violation this run is governed by. Explicitly **not** flagged
are the issue-numbered mechanism comments (#360, #315, #357): those record findings that
cost real time and are the good kind. The remedy is to correct two sentences, not to strip
the commentary.

`shotgun-surgery` is flagged as the **structural root of F2**: adding one sanctioned string
requires edits in four disjoint places — `ALLOWED_FLAGS`, `AGENT_TEXT_FLAGS`, the
`text_bearing` set literal, and the docstring sentence. `283175b` had to touch all four for
`--claimed-by`; the four missed flags are the same scatter biting twice.

---

## Scope, reconciliation, canon

* **Scope: clean.** `git diff --stat 3f787a3..HEAD -- . ':!.agent-work'` → one file, 1146
  insertions, new. No production script touched (`episode_capture.py` and
  `context_manifest.py` are OID-identical to HEAD).
* **Reconciliation: nothing to reconcile.** Every carried map anchor is *exercised*, not
  merely cited. #321 is already recorded in-file as a deliberate observation for you to rule
  on rather than fixed — correct routing.
* **Canon store: verified by the world, non-emptiness asserted first.**
  `git ls-files -s episodes/active/` → 3 entries (`.gitkeep`, `issue-309-001.md`,
  `issue-309-002.md`), so the comparison is non-vacuous.
  `git status --porcelain --untracked-files=all episodes/` → **empty**. For all 5 files
  tracked under `episodes/`, index OID == `git hash-object` of the worktree file: **zero
  divergences**. The synthetic consolidation left no residue.

## Anything I could not verify

Nothing material. I did not re-run your V1/V2/V3 verbatim — they are declared spent — but
N5 independently re-confirms the closed-world census fires on an un-sanctioned flag (V2's
family) and **N1c independently reproduces V3** rather than inheriting it.

## Triage candidates

`tc1` = F1 (aliased-import evasion), `tc2` = F2 (census scope sentence + four unnamed
flags), `tc3` = F3 (single staged `artifact-ref` path). All three recorded in the survey.

---

## Workflow Feedback — blunt

1. **The per-attack expected-assertion table is the single best thing in this handoff.
   Keep it, and keep it forever.** It converted A1 and A2 from "run something and squint"
   into a two-command confirmation. It also *caught a defect in your own brief*: because
   you named the assertion for A3, I noticed the test you named cannot go red under the
   all-null form and went looking for the one that can. A vaguer instruction would have
   produced a false "A3 green" from me. **Cost of the defect: near zero, because the table
   existed. That is the argument for the table.**

2. **The spent-mutation table has crossed over from asset to constraint, and you should
   notice.** It is now 18 rows. Genuinely novel ground is getting scarce, and I spent real
   time confirming that N1/N2/N5/N6 were not restatements. Two of my six new mutations
   (N1c, N6) are *deliberate re-runs of spent mutations under changed conditions*, and both
   were load-bearing: N1c is what separated "narrowed guard" from "vacuous guard" and
   therefore decided the verdict; N6 is what turned attempt 1's F4 from an assertion into a
   measured one-line fix. **Consider amending the rule from "never repeat a spent mutation"
   to "never repeat one *under the same conditions*"** — re-running a spent mutation against
   a changed premise is not a repeat, and forbidding it costs you exactly the evidence that
   decides borderline verdicts.

3. **"Prove the mutation is live" needs a third clause: prove it produced an *assertion*,
   not an error.** My first N2 attempt scored 7 failed with fully live mutations and correct
   OIDs — and was **worthless**, because every failure was `FileNotFoundError` (I had moved
   `work_id` without moving its directory, per #360). Liveness and colour were both real;
   the *evidence* was not. Your rule 1 ("assert the specific assertion") catches this only
   if the reader is disciplined enough to read past the red. Suggest stating it directly:
   **a battery whose failures are exceptions rather than assertions is a broken battery, not
   a result.**

4. **Your requirement 2 (in-memory mutations need dual-process probes) pushed me to prefer
   file mutations, which was the right outcome and you should say so explicitly.** File
   mutation + blob OID + a `__NC_MUT__` marker readable from both processes is strictly
   stronger than `monkeypatch`, and it is what let A1 prove the seam test goes red as well
   as the `compose()` path. Consider making it the default recommendation rather than the
   fallback — with the `finally:`/OID discipline you already mandate, it is not more
   dangerous, and it reaches the subprocess for free.

5. **You asked me to name a defect in your handoff plainly and I found one (item 1 above),
   plus one thing that reads as a defect and is not.** The `advances >= 8` floor: you listed
   it as a soft surface, which is correct, but the implied worry (that a shrunken run could
   pass) is already covered by the `[1,2,3,4]` literal in the same test. Worth knowing so it
   does not consume a future reviewer's budget — **the tuple is the guard; the floor is
   decoration.**

6. **Minor, mechanical:** the survey template's `config_ref` points at
   `docs/agents/engine-config.json`, which does not exist in this worktree (only
   `ORCHESTRATOR_CONTEXT.md` is there). The engine tolerates it, and attempt 1 shipped the
   same dangling ref, so this is cosmetic — but it is a path nothing checks, which is the
   very species of defect this gate is about.
