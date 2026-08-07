# Implementation Result — issue-419-governor-identity, gate g2

## Assigned gate
`g2` — the gauge writer attributes the reading to the acting agent.

## Completed slice

All five pieces (a)–(e) of the handoff, in `scripts/hooks/gauge_writer_hook.py`:

- **(a)** `resolve_gauge_path`'s second parameter is now the **binding key**, not the session id
  (renamed, docstring rewritten). The caller passes `_binding_key(data)`, which delegates to
  `spine_rail.binding_key`.
- **(b)** `derive_subagent_transcript(transcript_path, agent_id)` — the pure helper returning
  `Path(transcript_path).with_suffix("") / "subagents" / f"agent-{agent_id}.jsonl"`, or `None`.
- **(c)** With an `agent_id` in the payload the reading comes from the derived transcript and **only**
  from it. Absent derived file ⇒ `gauge-skip.json` with `reason: "subagent-transcript-missing"` and
  return, before `compute_record` is ever reached.
- **(d)** `find_latest_usage` and `compute_record` take **one** `agent_id` parameter. `None` = today's
  filter exactly; set = the line must be `isSidechain` **truthy** *and* carry top-level
  `agentId == agent_id`.
- **(e)** `identity_resolution_ms` written as an optional fifth field on the record.

Engine plan driven end to end: `.agent-work/issue-419-governor-identity/g2-IMPLEMENTER_PLAN.json`,
lease `impl-419-g2`, items `m0-context, m1, m2, m3, m4, m5, m6`, TDD red→green attested per gate.

## Scope

**Files changed:**
- `scripts/hooks/gauge_writer_hook.py` (+189 / −21)
- `tests/test_gauge_writer.py` (+569 / **−0**)
- `tests/fixtures/subagent_transcript_with_mainchain_tail.jsonl` (new, 5 lines)

```
$ git diff --numstat scripts/hooks/gauge_writer_hook.py tests/test_gauge_writer.py
189	21	scripts/hooks/gauge_writer_hook.py
569	0	tests/test_gauge_writer.py

$ git diff -U0 tests/test_gauge_writer.py | grep -E "^-[^-]"
(no output)
```
Exit 0 / exit 1 (grep, no match). **Zero deleted lines in the test file** — every one of the 37
pre-existing tests is literally unedited, not merely still-passing.

**Specific exclusions touched:** no. `scripts/gauge_reader.py`, `scripts/checklist_engine.py`,
`scripts/hooks/spine_rail.py` and `docs/GAUGE_WRITER_HOOK.md` are untouched (`git status --short`
lists only the three files above).

## Behavior changed

Yes.

- A dispatched agent's gauge binding resolves under `session_id#agent_id`; a top-level agent keeps the
  bare `session_id`. Parent and child each see exactly **one** candidate, so neither is ambiguous and
  neither goes silent.
- A dispatched agent's reading is computed from its own derived transcript with the sidechain polarity
  inverted and `agentId` equality enforced.
- New silence cause, positively localized: `gauge-skip.json` `reason: "subagent-transcript-missing"`.
- New optional fifth field `identity_resolution_ms` on a dispatched agent's record.
- **Unchanged** for any payload with no `agent_id`.

## The no-parent-fallback invariant, audited

```
$ grep -n "compute_record(\|find_latest_usage(\|read_path\|acting_agent_id" scripts/hooks/gauge_writer_hook.py
286:def find_latest_usage(transcript_path, agent_id=None):
352:def compute_record(transcript_path, agent_id=None):
371:        found = find_latest_usage(transcript_path, agent_id)
592:        acting_agent_id = data.get("agent_id") if "agent_id" in data else None
593:        if acting_agent_id is None:
594:            read_path = transcript_path
605:            read_path = derive_subagent_transcript(transcript_path, acting_agent_id)
606:            unresolved = read_path is None or not os.path.isfile(read_path)
615:        record, uncalibrated = compute_record(read_path, acting_agent_id)
632:        if acting_agent_id is not None:

$ grep -rn "compute_record(\|find_latest_usage(" --include=*.py . | grep -v "^./tests/" | grep -v gauge_writer_hook.py
(no output)
```

There is exactly **one** `compute_record` call site in the codebase, and `read_path = transcript_path`
appears only inside the `acting_agent_id is None` branch. The parent's transcript is structurally
unreachable while `agent_id` is present. Backed behaviorally by
`test_subagent_reading_is_computed_from_its_own_transcript_only` (intercepts `compute_record` and
asserts the exact path it was handed) and `test_missing_derived_transcript_never_calls_compute_record`.

## Test mode

**Required:** test-first. **Satisfied:** yes — each of m1–m5 wrote its tests, observed them red against
the then-current tree (recorded in that gate's `--why`), then implemented to green. Red counts per gate:
m1 4, m2 4, m3 4, m4 8, m5 2.

## Evidence — the three required verification commands

```
$ cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests/test_gauge_writer.py -q
...................................................................      [100%]
67 passed in 0.98s
EXIT=0
```

```
$ cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests/test_gauge_writer.py tests/test_gauge_reader.py tests/test_spine_rail.py -q
........................................................................ [ 77%]
..........................................                               [100%]
186 passed in 1.78s
EXIT=0
```

```
$ cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests -q
........................................................................ [ 92%]
........................................................................ [ 96%]
.................................s.........................              [100%]
1667 passed, 2 skipped, 550 subtests passed in 430.86s (0:07:10)
EXIT=0
```

Baseline at HEAD `340c46d` re-measured in this worktree before any edit:
`1637 passed, 2 skipped, 550 subtests passed in 445.78s`, exit 0. **1667 > 1637**; the delta is exactly
the 30 tests added here.

## Revert-measured non-vacuity — 23 of 30

`scripts/hooks/gauge_writer_hook.py` restored to `git show HEAD:...` (HEAD = `340c46d`), tests left
untouched, suite re-run, file restored, suite re-confirmed.

```
$ cp "$SP/gauge_writer_hook.NEW.py" ...   # backup taken first
$ git show HEAD:scripts/hooks/gauge_writer_hook.py > scripts/hooks/gauge_writer_hook.py
--- reverted to HEAD (340c46d) ---
$ python -m pytest tests/test_gauge_writer.py -q
...
23 failed, 44 passed in 1.63s
REVERT_EXIT=1
```

The 23 that went red:

```
test_binding_key_helper_returns_none_when_spine_rail_failed_to_load
test_binding_key_helper_delegates_to_spine_rail
test_subagent_payload_never_writes_to_the_parents_gauge
test_unresolvable_identity_writes_nothing
test_local_allowlist_is_stricter_than_spine_rails_denylist
test_local_allowlist_admits_the_real_observed_id_shape
test_derived_subagent_transcript_shape
test_derive_subagent_transcript_refuses_an_unusable_id
test_subagent_with_missing_derived_transcript_leaves_gauge_untouched
test_subagent_with_missing_derived_transcript_writes_no_gauge_at_all
test_subagent_reading_is_computed_from_its_own_transcript_only
test_find_latest_usage_takes_one_agent_id_parameter
test_real_subagent_transcript_yields_its_usage_for_its_own_agent_id
test_real_subagent_transcript_returns_none_for_a_different_agent_id
test_default_polarity_reaches_every_line_and_still_returns_none
test_matching_agent_id_on_a_main_chain_line_is_skipped
test_the_skipped_tail_line_is_itself_perfectly_usable
test_compute_record_carries_the_agent_id_through
test_dispatched_agent_writes_its_own_reading_to_its_own_binding
test_a_wrong_derived_transcript_fails_closed_rather_than_misattributing
test_identity_resolution_duration_is_recorded_within_budget
test_identity_resolution_duration_tracks_a_deliberately_slowed_step
test_the_four_required_fields_keep_their_meaning_alongside_the_fifth
```

Restore and re-confirm:

```
$ cp "$SP/gauge_writer_hook.NEW.py" scripts/hooks/gauge_writer_hook.py
--- restored ---
$ python -m pytest tests/test_gauge_writer.py -q
67 passed in 0.97s
RESTORED_EXIT=0
```

**The 7 that stayed green under the revert, and are therefore NOT evidence of this change.** Naming
them rather than counting them away:

| test | why it is green at HEAD | keep? |
|---|---|---|
| `test_resolve_gauge_path_keys_on_the_composite_key_not_the_session` | `resolve_gauge_path` was always a dict lookup; only its *caller* changed. Pins the contract, proves nothing. | yes, as a contract pin |
| `test_spine_rail_missing_writes_nothing_and_does_not_raise` | at HEAD the None-module path already skipped via the empty candidate list. The guard's real proof is `test_binding_key_helper_returns_none_when_spine_rail_failed_to_load`, which IS red. | yes, as the end-to-end companion |
| `test_rejected_agent_id_writes_nothing_even_when_its_key_is_bound` | at HEAD the lookup uses the bare `s1`, which this test does not bind, so nothing is written for the wrong reason. It WAS red at its own gate (m2) against the m1 tree. | yes — red where it mattered |
| `test_missing_derived_transcript_never_calls_compute_record` | same shape: at HEAD, zero candidates short-circuit before `compute_record`. Red at m3 against the m2 tree. | yes — red where it mattered |
| `test_top_level_payload_still_reads_the_session_transcript` | deliberate no-change control | yes |
| `test_fixture_premises_hold` | pins the fixtures the conjunct test rests on | yes |
| `test_top_level_record_keeps_exactly_the_frozen_four_fields` | deliberate no-change control | yes |

Two of those seven (`rejected_agent_id...`, `missing_derived_transcript_never_calls...`) are green only
because a **full** revert also removes the composite keying, which makes their setup unreachable for a
different reason. Both were observed red at their own gate. The other five are controls or pins and
were never meant to be evidence.

## The sidechain conjunct — line counts and reach

`tests/fixtures/real_subagent_transcript.jsonl`: **4 lines**, all `isSidechain: true`, all
`agentId af45cec63b2835a40`, one usable assistant line (`claude-opus-4-8`, `4823 + 1088 + 15111 =
21022` tokens, `2026-07-07T05:30:40.581Z`).

**The trap, confirmed:** all three assertions the handoff names are satisfied by an implementation that
checks `agentId` equality alone and drops the sidechain half — the conjunct is unfalsifiable against a
fixture whose every line is sidechain.

New fixture `tests/fixtures/subagent_transcript_with_mainchain_tail.jsonl`: **5 lines** — the 4 real
lines byte-identical (asserted in `test_fixture_premises_hold`) plus one derived tail line carrying the
**matching** `agentId af45cec63b2835a40` with `isSidechain: false`, on `claude-sonnet-5`, with
`7 + 3000 + 300000 = 303007` tokens. It sits **last**, so the reverse scan meets it **first**.

Reach measured by wrapping `_iter_tail_lines_reverse` and counting the lines actually consumed:

| assertion | fixture | lines | reach | result |
|---|---|---|---|---|
| default polarity | real | 4 | **4** | `None` (the pre-existing assertion, unedited) |
| own `agent_id` | real | 4 | **1** | `("claude-opus-4-8", 21022, "2026-07-07T05:30:40.581Z")` |
| different `agent_id` | real | 4 | **4** | `None` |
| own `agent_id` | derived | 5 | **2** | the real line — the matching-`agentId` main-chain tail is **skipped** |
| default polarity | derived | 5 | **1** | the tail line **is** the answer |

The last row is the control that makes the fourth meaningful: the tail line is skipped because of the
sidechain conjunct, not because it is unparseable or missing a field.

## Close criteria

| # | criterion | met |
|---|---|---|
| 1 | gauge path resolves from the composite key; a dispatched agent finds its own binding | **yes** — `test_resolve_gauge_path_keys_on_the_composite_key_not_the_session`, `test_dispatched_agent_writes_its_own_reading_to_its_own_binding` |
| 2 | a subagent's reading comes from its own derived transcript, polarity inverted, `agentId` equality enforced | **yes** — the reach table above + `test_subagent_reading_is_computed_from_its_own_transcript_only` |
| 3 | `agent_id` + derived transcript absent ⇒ `gauge.json` byte- **and** mtime-identical, no uncalibrated flag, `gauge-skip.json` carrying `subagent-transcript-missing` | **yes** — `test_subagent_with_missing_derived_transcript_leaves_gauge_untouched`. The prior mtime is stamped to `1_500_000_000_000_000_000` ns (2017) before the call, so the mtime assertion cannot pass on filesystem timestamp granularity |
| 4 | an unresolvable identity writes nothing | **yes** — `test_unresolvable_identity_writes_nothing` over `("", None, "sess#agent", "..", "a/b", "a\\b", 17)`, asserting no `gauge.json`, no uncalibrated flag and no skip sidecar anywhere under the tree |
| 5 | a payload with no `agent_id` is byte-identical in behavior to today | **yes** — 37 pre-existing tests unedited and green (0 deleted lines), plus `test_top_level_payload_still_reads_the_session_transcript` and `test_top_level_record_keeps_exactly_the_frozen_four_fields` |
| 6 | every pre-existing test in `tests/test_gauge_writer.py` passes **unedited** | **yes** — `git diff -U0` shows zero removed lines |

## Constraints

1. **`_spine_rail is None` guard carried to the new call site** — it lives in `_binding_key`, which
   deliberately carries **no** `try/except` of its own so a missing guard surfaces as a raised
   `AttributeError` in `test_binding_key_helper_returns_none_when_spine_rail_failed_to_load` instead of
   being absorbed one frame up by `handle_post_tool_use`'s outer swallow. That test is red at HEAD.
2. **No-`agent_id` byte-identical** — see close criterion 5.
3. **Allowlist, not denylist** — `_AGENT_ID_ALLOWED = re.compile(r"\A[A-Za-z0-9_-]{1,64}\Z")`, applied
   inside `_binding_key` *before* delegating and re-applied inside `derive_subagent_transcript`.
   `test_local_allowlist_is_stricter_than_spine_rails_denylist` asserts, for each of
   `a:b a*b a?b a<b a>b a"b a|b "a b" a.b` and a 65-char id, that **`spine_rail.binding_key` admits it
   and this module does not** — the two are compared in the same assertion, so the test measures the gap
   rather than describing it. A rejected value writes nothing; there is no sanitize/repair path.
4. **Windows path reality** — a rejected character produces a deliberate `return None` skip, not an
   exception. `test_rejected_agent_id_writes_nothing_even_when_its_key_is_bound` binds the offending
   composite key first, so an implementation that admitted the character would have somewhere to write
   and would write there.
5. **Zero engine change for the new reason** — `scripts/gauge_reader.py` and
   `scripts/checklist_engine.py` untouched; the string is added at the call site only.
6. **Fail-open at the process level, fail-closed about records** — every new branch returns `{}`; no
   exception escapes; no uncertain reading is written.

## Identity-resolution duration

Measured across the two identity steps (binding-key composition, transcript derivation including the
existence check) and accumulated. The binding-store read between them is *binding* resolution, a
pre-existing cost the issue did not scope, and is deliberately not counted — stated in the code.

A real record produced by the real handler, against real captured fixture input:

```json
{
  "schema_version": 1,
  "fill_fraction": 0.021022,
  "model": "claude-opus-4-8",
  "observed_at": "2026-07-07T05:30:40.581Z",
  "identity_resolution_ms": 0.11380005162209272
}
```

**0.114 ms against the 100 ms placeholder budget** (~880x headroom), which is what identity being an
O(1) payload lookup buys.

It is a **measurement, not a constant**: `test_identity_resolution_duration_tracks_a_deliberately_slowed_step`
writes a record, then wraps `spine_rail.binding_key` in a 30 ms sleep and writes the same record again
with the same binding, the same agent and the same derived transcript, and requires
`slow >= 25.0` **and** `slow > fast + 20.0`. A hardcoded value, or a timer around the wrong span, fails
both.

**The fifth field rides the dispatched-agent path only.** That is forced, not chosen: the pre-existing
`test_golden_fixture_produces_well_formed_record` pins the record to exactly four keys, and constraint 2
requires a no-`agent_id` payload to be byte-identical. There is also no identity to resolve for a
top-level agent. The reasoning is written into the code at the write site so a later reader does not
"fix" it. **Flagging it for the reviewer** as the one place my reading of piece (e) narrows the
handoff's wording ("record the duration in the gauge write") to "record it when there was an identity
to resolve".

## Docs/contracts touched

- `docs/GAUGE_WRITER_HOOK.md` — **not touched**, per the exclusion; it belongs to g3. It is wrong today.
- The module docstring in `gauge_writer_hook.py` gained a bullet describing the #419 attribution
  contract. That file is in scope and its in-file documentation would otherwise contradict its own code.

## Assumptions

- `HEAD` for the non-vacuity measurement means `340c46d` (g1's commit), the tip of this branch, not the
  epic base — the handoff's "revert your file to HEAD" reads as the immediately preceding state.
- The derived-transcript shape holds. Not re-verified against a live harness here (that is g4's job);
  taken as settled/measured from the pre-build probe plus the cold critic's independent re-verification,
  and the fail-closed branch is what makes a wrong shape cost silence rather than a wrong number.

## Stop conditions hit

None. No close criterion was unmeetable, no excluded file needed editing, no existing test needed
editing, and the derived-transcript shape held.

## Out-of-scope observations (triage candidates, not fixed here)

1. **`spine_rail._AGENT_ID_REJECT` and this module's allowlist now disagree by design, and the gap has a
   small live consequence.** For an `agent_id` such as `a:b`, `spine_rail` *writes* a binding under
   `s1#a:b` while this module refuses to resolve it — so that binding is orphaned: written, never read,
   never cleaned up (the `release` path deletes by the same composite key, so it does clear on a clean
   release, but not on a crash). No filesystem hazard, since `spine_rail` only uses the value as a dict
   key. The durable fix is to move the allowlist into `spine_rail` and have both hooks share it, which
   is exactly the "single place the key is composed" property g1 was built around. `spine_rail.py` is
   closed to this gate, so this is recorded, not done.
2. **The parent-orchestrator multi-binding gap survives**, as `PROBLEM_STATEMENT.md` already states: an
   orchestrator legitimately holding N spines under its bare `session_id` is still ambiguous. Nothing
   here changes that, and nothing here makes it worse — the subagent entries that used to pile onto the
   parent's key no longer do.
3. **`docs/GAUGE_WRITER_HOOK.md` needs three corrections, not two** — the sidechain inversion and the
   `agent_id`/`agent_type` field-table rows are already named for g3; add the new
   `subagent-transcript-missing` skip reason and the optional `identity_resolution_ms` field.
4. **`_clear_skip_flag`'s known residual now has one more entry point.** A `subagent-transcript-missing`
   flag is cleared the next time that same path resolves to a single candidate with a real outcome, and
   otherwise persists — the same accepted, bounded residual documented under
   `decision:skip-sidecar-fanout-and-clear`. Behavior is consistent with the existing reasons; noting it
   so the reviewer does not read it as new.

## Map Impact

- **Structural anchors touched:** `gauge_writer_hook.py` — `resolve_gauge_path` (second parameter is now
  the binding key), `find_latest_usage` and `compute_record` (each gained one `agent_id` parameter),
  `handle_post_tool_use` (derive-or-skip branch). Two new module-level seams: `_binding_key` (the guarded
  delegation to `spine_rail.binding_key`) and `derive_subagent_transcript` (the pure derivation).
- **Capabilities added/changed:** the gauge writer can now attribute a reading to a dispatched agent
  rather than going silent on ambiguity; new positively-localized silence cause
  `subagent-transcript-missing`; new optional record field `identity_resolution_ms`.
- **Constraints/assumptions relied on:** `constraint: fail-closed on identity — skip-on-uncertainty,
  never fabricate` (now enforced at three points: unresolvable key, rejected `agent_id`, absent derived
  transcript). `assumption: the derived transcript shape <slug>/<session_id>/subagents/agent-<id>.jsonl`
  — settled/measured upstream, not re-measured here, and the fail-closed branch bounds its cost.
- **Decisions resolved locally:** the fifth field is dispatched-agent-only (forced by the frozen 4-field
  record and the byte-identical constraint); the allowlist lives in this module rather than replacing
  `spine_rail`'s denylist (forced by the exclusion, with the durable fix filed above as candidate 1);
  the binding-store read is excluded from the identity-resolution measurement.
- **Claims/evidence produced:** 23/30 revert-measured non-vacuity; the sidechain conjunct is falsifiable
  against the new fixture and is falsified; the parent's transcript is structurally unreachable while
  `agent_id` is present (single call site, audited by command).
- **Trust limitations:** `docs/GAUGE_WRITER_HOOK.md` remains wrong and now diverges from the code in two
  further places (candidate 3). Nothing here is validated against a live harness — that is g4, and
  `CLAUDE_PROJECT_DIR` being fixed at session launch (#269) means it cannot be validated from inside
  this worktree at all.

## Workflow Feedback

- **Handoff gaps.** Piece **(e)** and constraint **2** are in direct tension and the handoff does not
  resolve it: (e) says record the duration "in the gauge write", constraint 2 says a no-`agent_id`
  payload must be byte-identical, and the pre-existing
  `test_golden_fixture_produces_well_formed_record` pins the record to exactly four keys. Only one
  reading survives all three — the field is dispatched-agent-only — so I took it, wrote the reasoning
  into the code, and flagged it above. Naming that in the handoff would have saved the deliberation and,
  more importantly, would have removed the chance of me guessing the other way.
- **Handoff gaps, second.** The **Required verification commands** block and the **Required evidence**
  block do not state which `HEAD` the revert measurement is against. On a gate that follows another gate
  on the same branch, "revert to HEAD" could mean g1's commit or the epic base; the two give different
  counts. I assumed g1's commit (`340c46d`) and said so. One word in the handoff fixes this
  permanently.
- **Context rediscovered.** Nothing significant. The inbound anchors' line numbers (~145, ~194, ~238,
  ~399) were accurate and the "read the code, not the document" confidence flag on
  `docs/GAUGE_WRITER_HOOK.md` was correct and saved real time. The one thing I had to derive myself was
  the real fixture's usage arithmetic (`4823 + 1088 + 15111 = 21022`, model, timestamp) — the anchor
  says "one usable assistant line on `claude-opus-4-8`" but not its value, and every polarity assertion
  needs it. Carrying that number in the anchor would be cheap.
- **Instructions improvised around.** `IMPLEMENTER_PLAN.template.json` has `config_ref:
  "docs/agents/engine-config.json"`, but that file **does not exist** in this repo. The engine accepts
  it silently and falls back to defaults, so the rework cap and replan policy this plan ran under are
  the engine's built-ins, not the project's. g1's plan and the Commander spine carry the same dangling
  ref, so this is repo-wide and pre-existing, not something I introduced — but a config reference that
  can dangle without a warning is a check that cannot fail.
- **Instructions improvised around, second.** The skill says to run each item's verification through the
  engine's `command` postcondition. The full suite takes **7m10s**, which is inside the Bash tool's 10
  minute ceiling but too close to it to run inside an `advance` — a timeout there kills the engine
  process mid-verb and leaves the gate `in-progress`. I ran the full suite as its own foreground command
  and attested `m6.c2` with the real output and exit code, keeping the engine `command` check on the
  fast three-module run. Worth saying out loud in the skill: for a long suite, attest with pasted output
  rather than wrapping it in a `command` postcondition.
- **What would have made this easier.** One line in the handoff resolving the (e)/constraint-2 tension,
  and the fixture's usage sum in the structural anchor.

## Return status
`complete`
