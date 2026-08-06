# RETURN — `cmdr-419-governor-identity`, issue #419 (epic-418 workstream A)

## 1. Verdict

**This is a win, not a measured negative.** I was asked to give the context governor per-agent
identity, keyed `session_id#agentId` rather than session alone, with the done-condition set explicitly
as *"a trip fires from a per-agent reading on a live run"* rather than "readings appear". That is what
happened, and it was observed rather than inferred. The binding store now composes a per-agent key in
one place, an unusable identity binds nothing at all, the gauge writer reads each agent's fill from
that agent's own transcript with the sidechain filter inverted and an `agentId` equality that makes a
wrong path fail closed, and the design document that was wrong about all of this is corrected. On a
live two-arm run, subagent ALPHA reached 33% of a 1M window and the engine **refused its `advance`**,
while the byte-identical script on the unmodified hooks produced no reading and advanced normally.

**It carries one honest limit, and I want it read next to the win rather than under it.** The binding
store resolves a relative `--file` against the hook payload's `cwd`, and for an agent dispatched into a
worktree that `cwd` is the **main checkout** (#269). **60 of the 64 live binding entries were exactly
this**, including every spine my own crews claimed. So per-agent identity is proven for agents whose
`cwd` is the project directory — which is what the acceptance sandbox was — and a worktree-dispatched
agent's reading still lands in a phantom `.agent-work/` inside the main checkout while the engine reads
the worktree copy. This predates #419 and is orthogonal to it, but it is the next thing standing
between the governor and firing on real Constellation runs. Filed as **#440**.

## 2. Evidence

**Isolation proof, first command run, exit 0:**

```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/epic418-a-419
worktree OK: in C:/Programs/constellation-skills-wt/epic418-a-419
EXIT=0
```

**PR:** [#445](https://github.com/fredcai6/constellation-skills/pull/445) —
`gh pr view 445 --json state` → `state=OPEN`, `mergeable=CONFLICTING`. See §7 for the conflict; it is
in two shared append-only logs only, and I deliberately did not resolve it.

**Branch:** `epic-418/a-419-governor-identity`, base `990712f` on clean main, pushed. Commits:
`4767782` (plan + probe), `340c46d` (g1), `5491bd4` (g2), `f8b0743` (g3 + doc), `54233a6` (acceptance),
`7f22360` (sweep, reconcile, triage, feedback).

**The test suite that gates the claim:**

```
$ python -m pytest tests -q
1667 passed, 2 skipped, 550 subtests passed in 431.51s     EXIT=0
```

Baseline at HEAD `990712f`, clean tree: **1621 passed, 2 skipped**. Delta **+46**, so a run reporting
1621 would have meant the new tests were never written — the closeout check asserts strictly greater,
not equal, for exactly that reason.

**A trap worth passing up: `py` is not the test runner on this box.** It resolves to a codex runtime
with no pytest, and `py -m unittest discover -s tests` reports 4 loader errors and 11 mutation-floor
failures that are **pure interpreter artifacts**. I nearly recorded that as a red baseline. Every
handoff after that carried the correction and no crew hit it. Independently re-verified by a cold
critic.

**Non-vacuity, measured rather than argued** — the single most valuable practice of this run:

| gate | revert target | new tests that go red |
|---|---|---|
| g1 | `spine_rail.py` → `HEAD~1` | **13 of 16** |
| g2 | `gauge_writer_hook.py` → `340c46d` | **23 of 30** |

Both counts were reproduced independently by their reviewers, one of which added **five targeted
mutations** of its own (parent fallback reinstated → 3 red; `agentId`-alone → 1; sidechain-alone → 2;
widened allowlist → 3; bare-session keying → 11).

**The acceptance, verbatim.** Two arms, one variable — the settings file's hook directory. Both arms
name the *same* `checklist_engine.py`, so the trip code is held constant:

```
REFUSED: g1: context at 33% is at/over the hard limit — advancing is blocked until you
request a refresh, so work is handed off at a seam rather than lost to a runaway.
Run: attach g1 --type refresh-request --field seam=g1 --field why_ref=<why-id>
```

| | treatment (this worktree's hooks) | control (main checkout's hooks) |
|---|---|---|
| binding keys | 3 — one bare (parent), two composite, each holding **exactly one** spine | **1** bare key holding **3** spines |
| gauges written | 4, fills 0.329482 / 0.102211 / 0.094663 / 0.064216 | `ambiguous-binding`, `candidate_count: 3` |
| ALPHA's gate after `advance` | `in-progress`, `refusals=1` | `complete`, `refusals=0` |

**The pairing is what carries the verdict**, because two keys, two distinct readings, a fired trip and
a silent control **all still pass on a crossed attribution** — and a crossed attribution is exactly the
misattribution class #202/#261 already reverted once. A cold critic caught that the obvious evidence
missed it. Recomputed by the reviewer with a parser importing neither hook: **2 of 2 dispatched, 4 of 4
overall**, each gauge's sampled moment appearing in no other agent's transcript. A parent-transcript
fallback at ALPHA's instant would have read **0.047769**, not 0.329482.

**Identity provenance.** Nothing on the acceptance path supplied the identity: a 7-pattern sweep over
71 pre-run files returned zero hits, and the pre-seeded-binding, hand-made-transcript and env-var
evasions were each closed separately. `identity_resolution_ms` measured **0.078–0.084 ms** against the
issue's 100 ms placeholder budget.

**The sweep.** Dry run first with the before-state recorded to a file in this worktree, then a real run
that re-read and re-evaluated against a fresh read and refused to write a map derived from a stale one.
**64 entries → 1.** Drop reasons: 60 pointed at spine files that do not exist (that is #440), 3 held
released leases. Sweeper deleted after its one run.

**Rework:** one round, at g3, on a correct reviewer BLOCK.

## 3. Isolation proof

Pasted verbatim in §2 above — `worktree OK`, exit 0, run as the first command before any git operation.

## 4. Scope-discipline report

Per your standing ruling, each corner case I chose not to chase is commented at its code site and
floated here.

| corner case | comment at | why not chased |
|---|---|---|
| Nothing reaps an abandoned agent's key; `release` is the only removal path, and per-agent keying multiplies key count by every wave's fan-out | `scripts/hooks/spine_rail.py`, the release branch in `handle_post_tool_use` | Outside the issue's stated scope, and the issue itself mandates deleting the one-time sweeper. Filed as #441 |
| The binding store's load-modify-save takes no lock, so a concurrent claim can be lost — and a lost write's symptom is silence, indistinguishable from an idle governor | `scripts/hooks/spine_rail.py`, `_save_json_map` | Concurrency was out of scope. Raised independently by two reviewers and a cold critic. Filed as #441 |
| `spine_rail`'s denylist and `gauge_writer_hook`'s allowlist disagree, so an id like `a:b` gets an orphaned binding entry | both modules, at their respective checks | No filesystem hazard — verified at source, the key is only ever a dict key. `spine_rail` was closed and reviewed at g1. Filed as #441 |
| `docs/GAUGE_WRITER_HOOK.md`'s eyeball-check section and three code comments still claimed a four-field record after the optional fifth shipped | fixed, not deferred | Bounded and in-class, so I ruled them in rather than passing them up. Seven sites across four files, each found by a different pass |

Also **narrowed, not skipped, and this one needs your ruling** — see §7.

## 5. Map impact

There is no `docs/architecture/` map in this repo at all. The orientation receipt records
**DEGRADED-NO-MAP**, discharged with two hash-pinned substitutes, the unmapped gap, and an escalation
to you. Reconcile therefore folded directly into the structural record the change actually touches,
per the spine's no-packet-map path.

An architecture reconcile needs to know four things about the net change:

1. **The binding store's outer key is now per-agent** — `session_id` for a top-level agent,
   `session_id#agent_id` for a dispatched one, and **no entry at all** for an unusable identity. This
   is the load-bearing interface shape of the whole workstream, and it is the shape workstream F's
   caller-identity work will meet.
2. **The reading's source moved.** A dispatched agent's fill comes from its own derived transcript, so
   the sidechain filter's polarity is now scope-dependent rather than constant.
3. **Nesting is safe, and this was measured, not assumed.** The harness writes every agent's transcript
   flat under the **root** session's `subagents/` directory regardless of `spawnDepth`, so the
   derivation holds at depth 2. Had it not, the governor would have been permanently and silently blind
   for every nested agent.
4. **The binding store has four named structural limits**, now written into
   `docs/GAUGE_WRITER_HOOK.md` rather than left to be rediscovered: the worktree path defect, the
   unreaped key, the unlocked write, and the unvalidated recorded path.

## 6. Triage candidates

Ten candidates, all routed. Consolidated to **five issues** on purpose, since this epic exists partly
to stop correct findings being filed at the wrong granularity. Full recommendations in
`.agent-work/archive/2026-08-05-issue-419-governor-identity/TRIAGE_RECOMMENDATIONS.md`.

- **#440 — the governor still cannot fire on a worktree-dispatched run.** The most important thing I
  found. It is the honest scope limit on this issue's win.
- **#441 — binding-store durability:** no lock, no reaper, unvalidated recorded paths, divergent
  `agent_id` rules. Four gaps in one module, one owner.
- **#442 — the engine's rail and its HARD refusal read badly to the agent they are aimed at.** Real
  dispatched agents in the acceptance run read the `RAIL:` banner as a possible prompt-injection
  attempt and said so in their transcripts; and the refusal's remedy string assumes a
  Constellation-aware reader, which is #331's offered-and-declined question wearing a new hat.
- **#443 — `docs/agents/engine-config.json` does not exist** while every template's `config_ref` names
  it, so the rework cap, replan policy and human checkpoints are defaults nobody chose. Reported by
  three separate crews in this run alone.
- **#444 — nothing links the gauge record's field count across its seven assertion sites.**

Two `recommend-and-defer`, deliberately not filed because neither has a code target in this repo:
`git worktree add` into the scratchpad failing on Windows MAX_PATH (target is crew doctrine), and this
run's own evidence-hygiene defect where one archived artifact does not regenerate from its archived
producer.

## 7. Things I need you to look at

**A deliberate departure from the spec, narrowed rather than skipped.** The spec retires the
pre-migration bare-key bindings **unconditionally**, reasoning that no liveness test applies to them by
construction. That reasoning predates this epic dispatching concurrent runs whose bindings are
bare-keyed **and live right now**. An unconditional sweep would have deleted **your own** binding
mid-run. So I reported both counts and narrowed the rule: the unconditional rule would have dropped all
64; I dropped 63 and spared the single entry with an existing spine and an active lease — which was
`admiral-epic-418`. Graded `settled/human · leans g5-sweep`; only you may unsettle it.

**The probe's branch point resolved outside what either branch anticipated.** Your pre-ruling gave
three outcomes: own-transcript-path → re-key; parent's path → ship the matcher; neither → stop and
escalate. What the payload actually carries is the **parent's** path *and* a per-agent `agent_id`. By
the letter that is branch two, but branch two's whole purpose was to *discover* an identity the payload
now hands over free — so shipping the 250-line matcher would have been building a search for a value
already in the argument list. I took the cheaper mechanism you had already blessed (re-key), did not
invent a third, and am surfacing it rather than absorbing it. If you read that as out-of-taxonomy, the
work is unaffected — only the label is.

**The PR conflicts, and I left it deliberately.** `gh pr view 445` reports `CONFLICTING`, and the
conflict is confined to `.agent-work/AGENT_FEEDBACK.md` and `.agent-work/LESSONS.md` — the two shared
append-only logs that `_COMMON.md` says you harvest. "Keep both sides" is the correct resolution and I
am confident of it, but merging `origin/main` into this branch would pull in sibling workstreams' engine
changes (#420's channel fixes, #422's wired invariants) that my green was **not** measured against, and
I would rather hand you a clean, self-contained, verified branch than a merged one whose 1667 I cannot
vouch for.

## 8. Workflow feedback

Where the corpus, the engine, or this launch order fought me. The full retrospective is in
`.agent-work/AGENT_FEEDBACK.md`; these are the ones that cost real time.

- **`init_work_area.py` does not resolve the `<branch>` placeholder.** The Commander spine's archive
  gate therefore ships `gh pr list --head <branch> ...` — text a POSIX shell reads as an input redirect
  from a file named `branch`, so the check cannot run at all rather than merely failing. I corrected it
  through the engine's `retext-check` amend rather than by hand-editing the spine. Every delegated
  Commander using this template hits this at its very last gate.
- **`verify-frame` and `MISSION_FRAME.template.md` contradict each other under a DEGRADED
  orientation.** The template requires graded `decision:` anchors; `verify-frame` refuses *any* anchor
  id when no map was read. I kept decisions out of the frame and put them in `execute.json` where
  `grade_lint` sees them. Already filed as #394 — this is a confirming instance, not a re-file.
- **The `Agent` tool refused both `name` and `run_in_background`** for an in-process teammate. So the
  design-it-twice candidates and the cold critic panel ran synchronously, and the doctrine's standing
  instruction to tell every background subagent to `SendMessage` before ending its turn is unreachable
  at this tier. It worked; the doctrine just describes a capability I do not have.
- **One crew's final message was blocked by a permission classifier** and its evidence had to be
  recovered from its own transcript. The #145 shape: environmental, not a scope problem. Its reviewer
  judged the substitution *stronger* evidence, since no agent authored it.
- **The launch order was unusually good on one axis and I want to name it**, because it is repeatable:
  the pre-build probe pre-ruling paid for the entire run. Twenty minutes of looking at a real payload
  deleted a 250-line module from the plan and turned two named hazards into unreachable states rather
  than mitigated ones. Freezing "look before you design" as a *ruling* rather than advice is what made
  it happen first instead of never.
- **The cold panel earned its cost twice over**, and both wins were things no author would have found:
  every `command` postcondition in my frozen plan was already green at HEAD with zero code written, and
  the acceptance evidence passed on a crossed attribution. That first finding is a **recurrence** of a
  banked lesson, from a second commander using the same template, which is exactly the discriminator
  that lesson's bank-reason named — so it is now the template's problem, not an authoring habit. I
  exported it upstream as debt with a concrete repair: **run every `command` postcondition against the
  tree at plan-freeze time and refuse to freeze any that exits 0.**
