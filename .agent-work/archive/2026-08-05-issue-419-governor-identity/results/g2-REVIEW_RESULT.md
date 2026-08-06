# Review Result — issue-419-governor-identity, gate g2

## Assigned Gate
`g2` — the gauge writer attributes the reading to the acting agent (commit `5491bd4`).

## Result
**APPROVE**

## How this review was driven

Survey `.agent-work/issue-419-governor-identity/g2-review/review.json`, engine lease
`reviewer-g2-419`, 21 checks (the 7 template items plus 14 appended from the handoff), every one
recorded through `checklist_engine.py`, consolidated `verdict=APPROVE findings=0`. Fowler-pass record
at `.agent-work/issue-419-governor-identity/g2-review/FOWLER_PASS.json`, rail exit 0.

Verification ran in an **isolated copy** at
`<scratchpad>/g2v` (`scripts/hooks/` + `tests/` + the three fixtures) so reverting and mutating the
module could not race the full-suite run in the worktree. `git worktree add` into the scratchpad was
attempted first and failed on MAX_PATH — noted under workflow feedback.

## Handoff compliance

All five pieces are present and I reproduced each behaviorally with my own harness
(`<scratchpad>/g2v/indep_check.py`, **19/19 pass**), which does not import the implementer's tests:

| # | what I asserted | result |
|---|---|---|
| 1 | dispatched agent's gauge holds **its own** fill `0.021022`, not the parent transcript's `0.159203` | pass |
| 2 | parent's `gauge.json` never created by a dispatched call | pass |
| 3 | derived transcript absent ⇒ gauge bytes **and** `st_mtime_ns` unchanged, no uncalibrated flag, skip reason `subagent-transcript-missing` | pass |
| 4 | another agent's transcript planted at the derived path ⇒ nothing written | pass |
| 5 | top-level payload ⇒ exactly the frozen four keys, parent's fill | pass |
| 6 | 12 unusable `agent_id` values ⇒ **0** artifacts anywhere under the tree (count stated) | pass |
| 7 | `_spine_rail = None` ⇒ `_binding_key` returns None without raising; handler writes nothing | pass |

## Scope drift

None. `git diff --name-only 340c46d..HEAD` lists exactly three files: `scripts/hooks/gauge_writer_hook.py`,
`tests/test_gauge_writer.py`, `tests/fixtures/subagent_transcript_with_mainchain_tail.jsonl`. The same
command filtered to `scripts/gauge_reader.py`, `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`
and `docs/GAUGE_WRITER_HOOK.md` returns **empty** — all four untouched, in the index and in the working
tree.

## Evidence verdict

**The non-vacuity measurement reproduces exactly, and against the right target.**

```
$ git show 340c46d:scripts/hooks/gauge_writer_hook.py > <isolated>/scripts/hooks/gauge_writer_hook.py
$ git hash-object <isolated>/scripts/hooks/gauge_writer_hook.py
c08fa96b26801bc5e6c40fba5a7eabc5bd3aa75e
$ git rev-parse 340c46d:scripts/hooks/gauge_writer_hook.py
c08fa96b26801bc5e6c40fba5a7eabc5bd3aa75e
$ python -m pytest tests/test_gauge_writer.py -q
23 failed, 44 passed in 1.63s
$ diff <the 23 names the implementer listed> <the 23 that actually failed>
(empty — exact set match)
$ # restore
67 passed in 1.02s
```

The reverted file is 23,974 bytes and contains neither `_binding_key` nor `derive_subagent_transcript`;
HEAD's is 33,306 and contains both. It is genuinely the pre-change file — the stale "revert to HEAD"
recipe g1's reviewer caught did not recur here.

Test accounting derived by command, not by reading the report:

```
$ comm over sorted test-name lists from both revisions
pre-existing: 37   at HEAD: 67   added: 30   removed: 0
$ comm -23 added.txt reverted_failures.txt      # added tests still green under the revert
7 — exactly the 7 the implementer named
$ comm -13 added.txt reverted_failures.txt      # red but not new
(empty)
```

44 passing under the revert = 37 pre-existing + 7 new-green, so **every pre-existing test is green in
both worlds** — the strong form of "unedited".

**Mutation testing — no check that cannot fail survived.** Five targeted mutations against the shipped
file, each applied with an asserted-unique anchor:

| mutation | tests turned red |
|---|---|
| A — reinstate a parent-transcript fallback when the derived transcript is missing | 3 (incl. `test_missing_derived_transcript_never_calls_compute_record`) |
| B — drop the sidechain half, keep `agentId` equality alone | 1 (`test_matching_agent_id_on_a_main_chain_line_is_skipped`) |
| C — drop the `agentId` equality, keep sidechain alone | 2 |
| D — widen `_AGENT_ID_ALLOWED` to `.{1,64}` | 3 |
| E — make `_binding_key` return the bare `session_id` | 11 |

Mutation A matters most: it turns red **one of the seven tests that survive the coarse revert**, which
is the proof that those seven are not filler.

Full suite at `5491bd4`: `1667 passed, 2 skipped, 550 subtests passed in 437.53s`, exit 0 — matches the
claimed 1667. The 1637-after-g1 baseline follows by construction (only one test file changed; 30 added,
0 removed; 1667 − 30 = 1637) rather than by burning another 7 minutes.

## Close criteria

1. **Composite-key resolution — MET.** `resolve_gauge_path`'s second parameter is `binding_key`,
   used as `binding.get(binding_key)`; the caller passes `_binding_key(data)`, which delegates to
   `_spine_rail.binding_key`. Parent `s1` and subagent `s1#af45…` each resolve to one distinct path.
   Mutation E ⇒ 11 red.
2. **Own derived transcript, polarity inverted, `agentId` equality — MET.** With `agent_id` present,
   `read_path = derive_subagent_transcript(...)` and nothing else. The filter is a genuine conjunct:
   `elif not d.get("isSidechain") or d.get("agentId") != agent_id: continue`. Mutations B and C show
   both halves are load-bearing.
3. **Missing derived transcript — MET, all four parts.** My harness stamped the prior gauge's mtime to
   `1_400_000_000_000_000_000` ns before the call, so the mtime assertion cannot pass on filesystem
   granularity: bytes identical, `st_mtime_ns` identical, no `gauge-uncalibrated.json`,
   `gauge-skip.json` reason `subagent-transcript-missing`. The branch returns before `compute_record`.
4. **Unresolvable identity writes nothing — MET.** 12 values (`""`, `None`, `"a:b"`, `"a*b"`, `"a?b"`,
   `"sess#agent"`, `".."`, `"a/b"`, `"a\\b"`, `17`, 65-char, `True`) against a tree that *had* a bound
   parent binding: **0** gauge/skip/uncalibrated artifacts by `rglob` count.
5. **No `agent_id` ⇒ byte-identical — MET.** The fifth field is gated behind
   `if acting_agent_id is not None`; a top-level record's key set is exactly the frozen four.
6. **Pre-existing tests unedited — MET.** `git diff -U0 … | grep -c "^-[^-]"` = **0** removed lines;
   0 removed test names; all 37 green in both worlds.

## The confident-wrong-number hunt

**No path exists by which the parent's transcript reaches `compute_record` while `agent_id` is present.**
Read from the branch, not inferred from a test name:

- `compute_record` has exactly **one** call site (line 615).
- `read_path` is assigned in exactly **two** places: line 594 (`transcript_path`, inside
  `if acting_agent_id is None`) and line 605 (the derived path, inside the `else`).
- The one edge worth chasing is `agent_id` **present but unusable** (`None`, `""`, malformed) —
  `acting_agent_id` would be `None` and the code would route to the parent's transcript. That is closed
  one step **earlier**: `_binding_key` returns `None` for any present-but-unusable `agent_id` (line 225)
  and the handler returns at line 573, before `read_path` is ever assigned. Verified with all 12 values.

The reverse direction is closed by the composite key: a subagent's reading is filed under
`session_id#agent_id`, so it cannot land on the parent's bare-`session_id` binding.

## The sidechain conjunct

The new fixture really does falsify it. I parsed it myself: 5 lines, lines 0–3 byte-identical to
`real_subagent_transcript.jsonl`, line 4 is `type=assistant`, `agentId=af45cec63b2835a40` (**matching**),
`isSidechain=False`, `claude-sonnet-5`, usage `7 + 3000 + 300000`. It is fully usable and sits **last**,
so the reverse scan meets it first. Usability is proved **positively** by the control: at default polarity
that line *is* the answer, at reach 1. So the conjunct — and only the conjunct — skips it.

## The `_spine_rail is None` guard

Carried, and it produces a visible skip rather than a swallowed exception. `if _spine_rail is None:
return None` is the first statement of `_binding_key`, which deliberately carries no `try/except` of its
own, so a missing guard would raise rather than be absorbed by the outer swallow. `resolve_gauge_path`
kept its own independent guard, so the guard was **duplicated** to the new call site, not moved away from
the old one.

## Second opinions the Commander asked for

**1. The duration field on the dispatched-agent path only — I agree, and I would not accept the
alternative.** "Records its own duration in the gauge write" has to mean "records it when there was an
identity to resolve": a top-level agent derives nothing and checks nothing, so a top-level field would
report the cost of nothing. It is also forced — `test_golden_fixture_produces_well_formed_record` pins
the record to four keys and the byte-identical constraint forbids editing it, so only one reading
survives all three requirements. The measurement is real, not a constant: the slowed-step test injects a
30 ms sleep into `spine_rail.binding_key` and requires `slow >= 25.0` **and** `slow > fast + 20.0`, which
both a hardcoded value and a timer around the wrong span fail. My harness read 0.082 ms.

**2. The allowlist/denylist divergence — characterization confirmed, including "no filesystem hazard."**
I traced every use of the binding key in `spine_rail.py`: it appears only as a dict key
(`binding[key][abs_spine]` on claim, `del binding[key]` on release, a `startswith` prefix test in
`session_view`). It is never interpolated into a path, opened, or joined. So `a:b` produces
`binding['s1#a:b']`, which this module refuses to compose and therefore never resolves — an orphaned
dict entry, cleared by a clean release under the same key, surviving only a crash. The divergence
**does** carry a comment at the code site (lines 161–171), which names the denylist, names the three
characters it still admits, and states why this module needs the stricter rule. Their test compares the
two functions in a single assertion rather than describing the gap, so it cannot drift silently.

## Code/doc quality

Meets the inherited crew rules and `CREW_CONTEXT.md`'s verification discipline:

- **Guards that loop assert what they looped over.** `_reaching()` counts the lines the reverse scan
  actually consumed and every polarity assertion pins the reach (1, 4, 4, 2, 1).
- **Assertions are behavioral**, not greps over prose: record contents, filesystem state, an intercepted
  `compute_record` path, an `inspect.signature` comparison.
- **Windows rules honored** — fixture writes pass `encoding='utf-8', newline='\n'`; the byte comparison
  is against content the test itself wrote, not against a checkout blob.
- **Fail-visibly holds** — every new branch returns `{}` and writes nothing; no repaired or sanitized
  path anywhere.

Fowler pass: 12/12 smells visited, rail exit 0, one flag (`long-method`), five logged overrides.

## Map impact verdict

- **Evidence supports claimed change:** yes — every capability claim is backed by a behavior I
  reproduced myself, and the 23/30 revert measurement is the non-vacuity backing.
- **Constraints not violated:** yes. `fail-closed on identity` is enforced at all three points
  (unresolvable key, rejected `agent_id`, absent derived transcript), each verified.
- **Notes match the diff:** yes. The two new module-level seams (`_binding_key`,
  `derive_subagent_transcript`) and the three signature changes are exactly what the diff shows; no
  structural claim is overstated or missing.
- **Decision candidates surfaced:** yes — the duration placement and the allowlist location were both
  raised for a second opinion rather than settled silently, which is the right call for both.
- **Durable context routed:** yes — four triage candidates recorded rather than fixed under a closed
  exclusion.

**Verified at source rather than accepted:** `scripts/gauge_reader.py:_parse_fields` checks only the
*presence* of `REQUIRED_FIELDS` and has no extras rejection, so the optional fifth field genuinely costs
zero reader change.

## Reconciliation check

Nothing for the Commander to reconcile at this gate. There is no `docs/architecture/` map in this repo.
`docs/GAUGE_WRITER_HOOK.md` is the only doc asserting anything about this module; it is knowingly stale,
assigned to g3, and excluded from report by the handoff. Its line 158 ("All four fields present, no
extras") now diverges one step further — already captured as the implementer's triage candidate 3.

## Blockers

- none

## Out-of-scope observations

1. **`handle_post_tool_use` is ~97 lines** and has accreted one uncertainty branch per issue (#202,
   #261, #271, #419). The g2 change is minimal and in the established shape, but the next branch added
   there is the one that will be hard to read. Suggested when a fifth reason to change it appears:
   extract the read-path decision into a helper returning `(read_path, skip_reason)`. Filed as survey
   triage candidate `tc1`.
2. **`identity_resolution_ms` is written unrounded** (`0.08230004459619522`). Four decimals would carry
   the same information. Cosmetic; no reader depends on it.
3. **Two untracked orphan directories** sit at the `.agent-work/` root: `issue-419-governor-identity-g1/`
   and `issue-419-governor-identity-g2/`, alongside
   `.agent-work/issue-419-governor-identity/issue-419-governor-identity-g1-review/`. These are engine
   context-manifest side-effects, not the implementer's doing (my own survey created the g2 sibling), but
   closeout should expect them.
4. The implementer's four triage candidates all check out; candidate 1 (move the allowlist into
   `spine_rail` so both hooks share it) is the right durable fix and correctly deferred, since
   `spine_rail.py` is closed to this gate.

## Workflow Feedback

- **Handoff gaps.** The handoff is the best I have reviewed under this epic — it named the revert target
  explicitly (`340c46d`, **not** `HEAD`), named the trap in the pre-existing fixture, and pre-flagged the
  two judgment calls. One gap: it gives the suite counts (1621 / 1637 / 1667) as the movement check but
  does not say the 1637 figure is unreproducible in under 7 minutes. I derived it arithmetically instead
  (one test file changed, 30 added, 0 removed) and said so; a line noting that the delta is the checkable
  quantity, not the absolute, would have saved the deliberation.
- **Context rediscovered.** Nothing about the change. What I did have to discover is environmental:
  `git worktree add` into the session scratchpad **fails on MAX_PATH** in this repo (paths under
  `.agent-work/dispatch-126-127/harvest/...` exceed the limit), so the standard "isolate the revert in a
  worktree" move is not available here. I fell back to copying `scripts/hooks/` + `tests/` + the three
  fixtures into a short scratch directory, which works because `test_gauge_writer.py` resolves the module
  as `Path(__file__).resolve().parents[1] / "scripts" / "hooks"`. `CREW_CONTEXT.md` says "MAX_PATH is
  real" but does not name this specific consequence; it is worth a line there.
- **Instructions improvised around.** Two.
  (a) `config_ref: "docs/agents/engine-config.json"` in `REVIEW_SURVEY.template.json` points at a file
  that **does not exist in this repo**. The engine accepts it silently and falls back to built-in
  defaults, so my survey ran under the engine's defaults, not the project's. The g2 implementer reported
  the identical dangling ref from the implementer template, and g1's plans carry it too — this is
  repo-wide, and a config reference that can dangle without a warning is itself a check that cannot fail.
  (b) The skill says to append checks "one per inherited rule"; the handoff supplied 14 distinct
  verification demands. I appended all 14 as flat siblings (the `append` verb refuses nesting under an
  existing id) which made `current` a long flat list. It worked, but grouping — e.g. one umbrella item
  per handoff section — is not expressible.
- **What would have made this easier.** Create `docs/agents/engine-config.json`, or make the engine warn
  on a dangling `config_ref`. That single change would fix the same reported friction across the
  reviewer, implementer, and Commander templates at once.

## Return status
`complete`
