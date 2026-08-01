# Cold plan critic — issue #300 `execute.json`

Read: `.agent-work/300/MISSION_FRAME.md`, `.agent-work/300/execute.json`. No authoring context.
All claims below were checked against the worktree at `C:/Programs/constellation-skills-wt/298-300`.
Commands shown were actually run; exit codes are measured, not inferred.

**Count: 5 BLOCKING · 7 SERIOUS · 7 MINOR.**

I do not triage. Every finding below is for someone else to dispose of.

---

## BLOCKING

### B1 — `g3.c6`'s postcondition passes when the guard it exists to prove does not exist

**What is wrong.** The check text is `! A || B`. POSIX shell binds `!` to the pipeline, so this is
`(! A) || B`. When the collection probe `A` **fails** — because `tests/test_context_declaration_lint.py`
or the test id inside it does not exist — `! A` is true, the `||` short-circuits, and the whole list
exits **0**. The engine records exit 0 as PASS (`_check_condition`: `cond["satisfied"] = proc.returncode == 0`,
`scripts/checklist_engine.py:699`). The condition whose entire purpose is "the lint actually FIRES on a
divergent fixture (proving the guard works, not merely that the corpus is clean)" is satisfied by
**not writing the fixture at all**.

**Evidence.** Run verbatim in the worktree, with no lint and no test file present:

```
$ bash -c '! py -m pytest tests/test_context_declaration_lint.py::test_divergent_declaration_is_rejected --co -q > /dev/null 2>&1 || py -m pytest tests/test_context_declaration_lint.py::test_divergent_declaration_is_rejected -q'
$ echo $?
0
```

The statement's own gloss — "Postcondition is a bash negation so 'the guard fired' is a mechanically
re-verified engine check" — is a misreading of what got negated. The negation is applied to the
*collection probe*, not to the lint. Nothing in this check ever observes the lint failing on bad input.

**What I would do.** Delete the probe-and-guard construction entirely. The condition should be the
plain command `py -m pytest tests/test_context_declaration_lint.py::test_divergent_declaration_is_rejected -q`
(missing file → pytest exit 4, missing id → exit 4; both fail, which is correct), where that test's
body asserts the lint returns non-zero / raises on a divergent fixture. If the intent was to prove the
lint fails on bad input from the shell, then the negation belongs on the *lint invocation*:
`! py scripts/<lint>.py .agent-work/300/fixtures/divergent-spine.json`. Either way the current text
must not ship.

---

### B2 — `py -m pytest` does not work in the shell the engine actually uses; six of eight command postconditions are unrunnable

**What is wrong.** Command checks are routed through a POSIX shell (`_run_check_command`,
`scripts/checklist_engine.py:651-664`: `subprocess.run([shell, "-c", command])`, where `_find_posix_shell`
prefers `shutil.which("bash")`). In that bash, `py` resolves to a shim on a runtime that has no pytest.

**Evidence.**

```
$ which py
/c/Users/fredc/.local/bin/py
$ py -m pytest --version > /dev/null 2>&1; echo $?
1                                  # "No module named pytest"
$ python -m pytest --version
pytest 9.0.2                       # works
```

Affected: `g1.c2`, `g1.c3`, `g1-integrate.c1`, `g2.c2`, `g2-integrate.c1`, `g3.c2`, `g3-integrate.c1`.
Most of these fail closed (annoying, not dangerous) — but `g3.c6` fails **open** (see B1), and it fails
open *because of this*. The two defects compose: today, in this worktree, `g3.c6` returns PASS solely
because `py -m pytest` is broken. `py scripts/context_projection.py --check` (`g2.c3`) and the `py -c`
one-liner (`g4.c2`) are unaffected — those are stdlib-only and `py` runs them.

The repo's own docs carry both conventions (`docs/superpowers/plans/2026-06-24-lease-owner-liveness.md`
uses `python -m pytest`; `…lessons-delete-and-collector-tolerance.md` uses `py -m pytest`), so this is not
settled house style the plan can lean on.

**What I would do.** Replace every `py -m pytest` with `python -m pytest` and re-run each postcondition
string in bash before the plan is frozen. A frozen plan whose evidence commands were never executed
once is not a frozen plan, it is a wish list.

---

### B3 — No gate mechanically enforces an APPROVE verdict; the plan drops the `match` the house template ships

**What is wrong.** All three review gates state "REVIEW_RESULT verdict APPROVE" with
`check: {"kind": "artifact", "evidence_type": "review-result"}` and **no `match`**. The engine's artifact
check (`scripts/checklist_engine.py:713-725`) iterates evidence, and with `want = chk.get("match", {})`
empty, `all(...)` over an empty dict is vacuously true — so **any** non-superseded `review-result` evidence
satisfies it, including a BLOCK. The three integrate gates carry no verdict condition at all
(`g1-integrate.c1`, `g2-integrate.c1`, `g3-integrate.c1` are pytest commands only). Result: a BLOCK verdict
advances every gate in this plan.

**Evidence.** The repo's own canonical plan template does exactly what this plan omits —
`skills/commander/templates/EXECUTE_PLAN.template.json:52`:

```json
{"id": "c2", "statement": "reviewer verdict is APPROVE",
 "check": {"kind": "artifact", "evidence_type": "review-result", "match": {"verdict": "APPROVE"}}}
```

and the template deliberately keeps the review gate's condition weak ("REVIEW_RESULT **returned**") while
putting the verdict assertion on *integrate*. This plan inverted that: strong statement, weak check, and
the integrate-side assertion deleted.

Same class, lower blast radius: `g1.c1` / `g2.c1` / `g3.c1` state "IMPLEMENTER_RESULT returned with **no
unresolved blockers**" but check only that some `implementer-result` evidence exists. The "no unresolved
blockers" half is unchecked. (The house template has the same weakness, so this half is inherited, not
introduced — but the statement/check mismatch is still real.)

**What I would do.** Add `"match": {"verdict": "APPROVE"}` to each review gate's `c1`, or restore the
house split (review gate: "returned"; integrate gate: `match: {verdict: APPROVE}`). Do not ship three
gates whose stated close criterion is not the criterion the engine evaluates.

---

### B4 — `g3.c5` passes today, before any work is done

**What is wrong.** `grep -qi 'context' docs/CHECKLIST_SCHEMA.md` is meant to prove "the declaration field
is documented in the Task table." The word "context" is already all over that file.

**Evidence.**

```
$ grep -ci 'context' docs/CHECKLIST_SCHEMA.md
10
```

Matching lines include `why_trail`/Context-Governor prose (line 3), the survey row "extend from context"
(line 18), and "Trip — two-band context-gauge gate policy" (line 323). None is the Task-table row this
condition claims to verify. The condition is satisfiable by deleting the whole gate's work.

Note the contrast, and it is a real one: `g3.c3` and `g3.c4` are **sound**. Both phrases exist verbatim
in the template today (`grep -c` → 1 each), so those two are genuine non-regression guards on prose that
must survive. `c5` is the only vacuous one, and it is vacuous in the opposite direction — it asserts a
*new* fact with a check that was already true.

**What I would do.** Pin the actual new token, not the English word. Grep for the literal field name in
a table-row context, e.g. `grep -q '^| \`<field-name>\`' docs/CHECKLIST_SCHEMA.md` (a `^|` anchor forces
it to be a table row, not prose). Whatever the field ends up being called, the check must be one that
fails on today's file — verify that by running it against `HEAD` before freezing.

---

### B5 — The only real declaration, and the plan's own named acceptance test, both live inside the one gate that may be deleted

**What is wrong.** `g1`'s scope is schema only: "(2) the OPTIONAL ordered declaration field on the spine
task object." The **first declaration on a real spine** is `g2` item (3): "the first real declaration on
the Commander spine's context step." `g2` is explicitly a "CONTINGENT GATE — do not start until the
floated convergence choice has landed," and the frame says the Admiral may "rule the committed artifact
out of #300's scope."

If `g2` is amended out, #300 ships:

- a declaration field with **zero users** — no spine in the repo declares anything;
- an empty manifest on every real run, so acceptance criterion "a manifest is produced on every
  deterministic assembly" is satisfied **vacuously** (every manifest is `[]`);
- `g3`'s lint (`c2`, "the lint is green over the real shipped spine templates") passing over an empty
  declaration set — green because there is nothing to pin;
- **no cross-environment determinism evidence at all**, because `claim:deterministic-across-environments`
  appears in exactly one place in the whole plan: `g2.c4`. The frame calls it "the pre-ruled acceptance
  test" and `decision:determinism-is-the-acceptance-test` is graded `settled/inherited`. The acceptance
  test is inside the deletable gate.

This is the "broken tool passes every named check" case the panel gate was created to catch, and it is
reachable by an Admiral ruling the plan itself anticipates.

**What I would do.** Split `g2` at its real seam. The first real spine declaration, and the
determinism exercise over the *run manifest*, are run-time-half work and belong in `g1` — they do not
depend on the committed artifact in any way. Leave `g2` holding only the committed
`skills/commander/CONTEXT_PROJECTION.json` and its generator, which is the genuinely contingent part.
Then the contingent gate can be deleted without hollowing out the issue.

---

## SERIOUS

### S1 — Acceptance criterion "consumable as another issue's episode-record `context` field" is owned by no postcondition

`g3`'s imperative item (4) is "a short, explicit statement of the obligations issue #301 may rely on and
the ones it may not." Nothing in `g3.c1`–`c6` mentions it. `g3-review`'s imperative does not mention it
either — it names the invariant chain and the lint fixture only. The frame says this claim is "checked by
shape/obligation assertions only," but no gate contains such an assertion.

A crew can skip item (4) entirely and every check in the plan stays green. One of the issue's three
acceptance criteria has zero enforcement.

**What I would do.** Add a `g3` postcondition naming the obligations artifact by path and grepping for
its required sections (the may-rely list and the may-not list), plus a shape assertion — e.g. a test that
loads a produced run manifest, `json.load`s it, and asserts it is a JSON value assignable to a `context`
field without transformation. Add it to `g3-review`'s imperative too.

### S2 — Acceptance criterion "manifest on every assembly" is not in any frozen postcondition statement

`claim:manifest-on-every-assembly` — with the explicit lesson that it must be proved "by driving the REAL
producer through the engine, never a hand-injected fixture" — appears only in `g1`'s `anchors.evidence`.
The frozen statement of `g1.c2` names only "the identity function equals git hash-object on a real tracked
file, and CRLF/LF twins of the same content produce the SAME rev." The command runs the whole file, so
whatever the crew writes passes; but the *frozen statement* — the thing that survives into review and
integrate — omits the headline claim.

This is inconsistent with the plan's own stated discipline: `g3` pre-authors its invariant chain
explicitly "so the crew verifies a frozen chain rather than improvising." `g1` did not get the same
treatment for its most important claim.

**What I would do.** Extend `g1.c2`'s statement to name the third assertion explicitly ("…and a manifest
is produced by driving the real producer through the engine's `active_id()` selector, not a hand-built
fixture"), and pin the specific test id in a separate condition if the file is going to hold both.

### S3 — The pre-ruled acceptance test is a `check: null` self-attestation

`g2.c4` — "second-environment determinism exercised from a CLEAN CHECKOUT and the two artifacts
byte-compared; the transcript of both runs is pasted in the result" — has `"check": null`. It is attested
by the Commander. The single most important, explicitly pre-ruled piece of evidence in the entire plan is
the one with no mechanical check, in a plan that elsewhere refuses to accept "a grep-for-marker proxy."

`g2-review`'s imperative asks the reviewer to "confirm the second-environment rebuild really used a CLEAN
CHECKOUT (not the same worktree twice)" — but the reviewer only sees what the transcript says it did.
There is no artifact the reviewer can independently re-derive.

**What I would do.** Make it checkable. The determinism exercise can be scripted: `git worktree add` a
clean checkout at the same commit into the scratch area, run the generator there, `cmp` the two outputs,
exit non-zero on difference. That is a `kind: command` check that genuinely runs two environments. If the
scripted version is considered to weaken "second environment," then require the transcript to be a
committed file at a named path and grep it for both worktree paths and a `cmp`/`diff` exit line — a
weaker check, but not a bare attestation.

### S4 — `g3-integrate.c1` claims "the broader engine suite" and excludes every module that reads the changed files

The command is `py -m pytest tests/ -q -k 'context or checklist_engine'`; the statement is "the whole
targeted set plus the broader engine suite re-run green."

The change edits `skills/commander/templates/COMMANDER_SPINE.template.json`, `docs/CHECKLIST_SCHEMA.md`,
and adds `skills/commander/CONTEXT_PROJECTION.json`. Six test modules read those paths. **None** survives
the `-k` filter:

```
$ python -m pytest tests/ -q -k 'context or checklist_engine' --co -q   # 326/1159 collected
test_spine_provenance_check:  0 collected      # TEMPLATE = skills/commander/templates/COMMANDER_SPINE.template.json
test_install_constellation:   0 collected      # 11 references to COMMANDER_SPINE.template.json, incl. a name inventory
test_clamp_presence:          0 collected      # skills/commander/references/commander-core.md
test_init_work_area:          0 collected
test_feedback_tooling:        0 collected
test_apply_lessons_delta:     0 collected
```

`test_install_constellation.py` asserts on template names and manifest status
(`self.assertEqual("up-to-date", statuses["COMMANDER_SPINE.template.json"])`, line 1423) and
`discover_skills` iterates `source_root.iterdir()` — adding a new file under `skills/commander/` is
precisely the kind of change these tests exist to catch. No gate in this plan ever runs them.

For the record, the adjacent worry is **not** a problem: `-k` that deselects everything exits 5, not 0
(`python -m pytest tests/test_checklist_engine.py -q -k 'zzz_no_such_test'; echo $?` → `5`), so the filter
cannot silently pass on zero tests.

**What I would do.** Make the final integrate condition `python -m pytest tests/ -q` with no `-k`. The
suite is 1159 tests and collects in under a second; there is no cost argument for filtering it. If a full
run is genuinely too slow, at minimum add the six named modules explicitly.

### S5 — Sequencing: the committed artifact's only freshness check runs before the gate that mutates doctrine

`g2.c3` (`py scripts/context_projection.py --check`) is the sole verification that the committed
`CONTEXT_PROJECTION.json` matches canon. `g3` then edits `docs/CHECKLIST_SCHEMA.md`,
`docs/CHECKLIST_ENGINE_DESIGN.md`, and the spine template's imperative prose. `g3-integrate.c1` runs
pytest only. `g4-cold-panel` has no command postconditions touching it.

So: if any path in the projection's declaration is touched by `g3` — and `g3` is *the doctrine gate*, the
one whose job is editing doctrine — the shipped artifact is stale at merge and nothing notices. This is a
baseline that an earlier gate established and a later gate destroys, with no re-establish step.

**What I would do.** Add `py scripts/context_projection.py --check` to `g3-integrate.c1` (or as a
separate `c2`), guarded to no-op if `g2` was amended out. Better: put it in a final pre-return condition
so it is the *last* thing verified, not the first.

### S6 — Scope drift: `g2` anchors on spec B2, which the mission frame lists as out of scope

`g2`'s capability anchor (repeated in `g2-review` and `g2-integrate`) is:

> `capability:reviewable-doctrine-diff` — spec B2: "a versioned script builds the projection, so every
> doctrine change produces a reviewable diff of what agents will actually see"

The mission frame's Out of Scope section says:

> The kernel-plus-fragments break and the whole-role human-readable projection (**spec B2, conditional,
> decided at issue L**).

A gate cannot be anchored on a capability the frame declares out of scope and deferred to a different
issue. Either the frame's exclusion is wrong or the anchor is. Additionally: none of the issue's three
acceptance criteria (manifest on assembly, revision identity, consumable by #301) mentions a committed
per-role artifact at all — `g2` items (1) and (2) serve no stated acceptance criterion of #300.

I note the drift is **toward delivery-side over-build, not toward use**. I looked specifically for the
access-tracing/transcript class named in the brief and found none: no gate, constraint, or anchor
mentions reading a transcript, counting reads, or recording access. `constraint:delivery-not-use` is
restated in all three implement gates. That part of the plan is clean.

**What I would do.** Resolve the contradiction before freezing. If the frame is right, `g2` items (1)+(2)
belong to issue H/L and this gate reduces to the run-manifest determinism work (see B5). If `g2` is right,
the frame's Out of Scope line must be amended.

### S7 — `g2.c3` promotes the plan's own stated-insufficient evidence to a postcondition

`g2.c3` regenerates the committed artifact in the same worktree that just produced it and asserts the
tree is unchanged. The gate's own constraint list says "A round-trip over the real corpus is NOT
sufficient evidence on its own," and the frame cites
`lesson:round-trip-tests-prove-artifacts-not-parsers`. `c3` is exactly that round trip, with the
additional weakness that generator and checker are the same code reading the same filesystem — a
generator that produces garbage deterministically passes `c3` every time.

It is not wrong to have `c3`; idempotence is worth pinning. It is wrong that `c3` is a *hard* check while
`c4` — the one that actually discriminates a correct tool from a clean corpus — is `check: null` (S3).
The plan's check strength is inverted relative to its own evidence hierarchy.

**What I would do.** Keep `c3`, restate it honestly as "the generator is idempotent on its own output
(necessary, not sufficient)", and fix `c4` per S3 so the discriminating check is the mechanical one.

---

## MINOR

### M1 — `g4.c2` is a self-authored token, and `g4.c1` is unchecked

`g4.c2` runs a Python one-liner requiring `'DISPOSITION' in t and 'UNTRIAGED: 0' in t` in a file the
Commander writes itself. It proves the Commander typed a string. `g4.c1` — "three critic reports
produced, each from a cold read of the diff plus the mission frame only" — is `check: null`. So the
panel depth that `decision:full-cold-panel` calls "the floor, not a target to negotiate down" has no
evidence at all; a single critic plus a hand-typed `UNTRIAGED: 0` closes the gate.

Fix: require the three report files at named paths and check their existence and non-emptiness in `c1`;
have `c2` count disposition markers against finding markers rather than trusting a hand-written total.

### M2 — Command checks inherit the process cwd; every command string here is relative

`_run_check_command` calls `subprocess.run([shell, "-c", command])` with **no `cwd=`**
(`scripts/checklist_engine.py:663`), unlike `_git` a hundred lines above, which does pass `cwd=base_dir`.
Every command in this plan is relative (`tests/…`, `docs/…`, `.agent-work/300/…`). They resolve against
wherever the engine process was launched, not against the spine's `base_dir`. Correct if the Commander
always runs from the repo root; silently wrong (and, for `g4.c2`, silently *failing* rather than
passing, which is at least safe) if not.

Fix: either state "all commands assume cwd = worktree root" as a plan constraint, or make the paths
tolerate being run elsewhere.

### M3 — `constraint:windows-corpus` and `no-globs` are called load-bearing and have no check and no reviewer instruction

The frame says `newline="\n"` on every write is "load-bearing, not hygiene," and `g1` forbids
"globs, directory patterns, os.listdir, sorted() over paths." Both appear only in `constraints` arrays.
`g1-review`'s imperative directs the reviewer at round-trip blindness and `active_id()` — not at these.
A mechanical grep over the new files (`open(` without `newline=`; `glob`/`listdir`/`sorted(`) is a
two-line check and would be worth more than either constraint string.

### M4 — `e0-context` directs the crew at three things this repo does not have

The imperative says to read `docs/agents/ORCHESTRATOR_CONTEXT.md`, `docs/agents/GLOSSARY.md`, and "the
relevant Cartographer packet(s)". Verified: `docs/agents` does not exist and `docs/architecture` does not
exist in this worktree. The imperative carefully explains that the *engine-config* absence is sanctioned
degradation, but says nothing about the other three, and the frame's map-substitution note is in a
document `e0` tells the crew to read only *after* those paths. This is inherited verbatim from
`EXECUTE_PLAN.template.json` — it is boilerplate that was not localized.

Fix: one clause noting all `docs/agents/` and `docs/architecture/` content is absent-by-design here and
the frame's substitution applies, or reorder so the frame is read first.

### M5 — `config_ref` points at a file the plan itself declares absent

`"config_ref": "docs/agents/engine-config.json"` with a long imperative explaining it is a dead path.
If the run needs no non-default engine settings, drop the key. If it does, inline a `config` object — as
the imperative itself advises. Carrying a known-dead reference plus 400 words explaining why it is dead
is worse than carrying neither.

### M6 — The `anchors` block is duplicated verbatim three times per gate

`g1`'s anchors block appears identically in `g1-implement`, `g1-review`, `g1-integrate`; same for `g2`
and `g3`. That is roughly 350 of the file's 751 lines. The house template solves this with
`"anchors": {"inherits": "g1-implement anchors — review verifies the change against the same … anchors"}`
(`EXECUTE_PLAN.template.json`, `g1-review`). The plan under critique ignores that idiom. It matters
concretely because `g2` is expected to be amended via the engine's `amend` verb — which now means
amending three copies consistently or leaving two stale.

Fix: use `"inherits"` on the review and integrate gates.

### M7 — YAGNI: the read-only CLI verb in `g1` item (5)

"one read-only CLI verb that prints it, joining `current` in the write guards and never journaling."
No acceptance criterion of #300 requires a CLI surface — the manifest needs to exist, carry revision
identity, and be consumable by #301, all of which are satisfied by the producer plus the on-disk file.
The verb costs edits at two write-guard sites (`checklist_engine.py` ~2508/2523, both confirmed present
as `args.verb != "current"`) and a `MUTATING_VERBS` exemption, i.e. it touches the engine's persistence
control flow for a convenience print.

It is the single clearest deletion in the plan. If a human wants to read the manifest, it is a JSON file.

---

## Where the plan is sound

Stated plainly so the list above is not read as uniform condemnation:

- **The POSIX-shell concern does not apply.** I expected `grep -q`, `!`, and `||` to break on Windows.
  They do not: the engine deliberately routes command checks through bash and refuses to fall back to
  cmd.exe (`_run_check_command`, `checklist_engine.py:651-675`), and bash + grep are present on this host.
  The shell forms in this plan are safe; only their *logic* (B1) is wrong.
- **`g3.c3` and `g3.c4` are genuine invariants.** Both phrases exist verbatim in
  `COMMANDER_SPINE.template.json` today (`grep -c` → 1 each). They correctly guard prose that a
  path-list refactor would be tempted to delete, and they will actually fail if it is deleted.
- **Structural anchors are accurate**, not decorative: `active_id()` is at line 184, `state()` at 1470,
  `_STATE_CONTRACT_VERSION` at 1354, the read-only write guards at ~2508/2523. Someone verified these.
- **No drift toward use.** I hunted the access-tracing/transcript class specifically and found nothing.
- **The targeted-plus-broader test split** in `g1` (`c2` targeted, `c3` broader engine suite) is the
  right shape for a mechanism change; the failure is only that `g3-integrate` narrows it again (S4).
- **The contingency handling for `g2`** — amend via the engine verb, never hand-edit — is the correct
  mechanism. The problem is what was put *inside* the contingent gate (B5), not how the contingency
  is expressed.
