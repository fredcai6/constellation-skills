# Implementation Result

## Assigned gate
`g1 — per-agent binding key in the store` (work id `issue-419-governor-identity`, branch
`epic-418/a-419-governor-identity`). Driven through the engine on
`.agent-work/issue-419-governor-identity/g1-IMPLEMENTER_PLAN.json` (six items, lease `impl-419-g1`).

## Completed slice
The session-to-spine binding store now has a per-agent outer key. A subagent's claim is filed under
`session_id#agent_id`; a top-level agent keeps its bare `session_id`; an unresolved identity binds
nothing. Readers merge both key shapes, so nothing that was visible before is now invisible.

## Scope
**Files changed:**
- `scripts/hooks/spine_rail.py` — added `BINDING_KEY_SEP`, `binding_key(payload)`,
  `session_view(binding, sid)`; routed the claim write, the release delete and the empty-set cleanup
  in `handle_post_tool_use` through `binding_key(data)`; routed the reads in `decide_stop` and
  `decide_session_start` through `session_view`. (+156/−20 lines.)
- `tests/test_spine_rail.py` — 16 new tests appended. Zero deleted or modified lines
  (`git diff -U0 | grep -c '^-[^-]'` → `0`), so every pre-existing test passes unedited.
- `tests/fixtures/probe_payloads.jsonl` — new; byte-identical copy of
  `.agent-work/issue-419-governor-identity/evidence/probe-payloads.jsonl`.

Committed locally as `340c46d` on `epic-418/a-419-governor-identity` (those three files only — the
Commander's `.agent-work/` state is left uncommitted). Not pushed, no PR, no issues filed.

**Specific exclusions touched:** no. `scripts/hooks/gauge_writer_hook.py`, `scripts/gauge_reader.py`,
`scripts/checklist_engine.py` and every other file under `scripts/` are untouched; no new module, no
migration code, no change to `_foreign_worktree`, `_is_old_shape_binding_entry` or the nudge ledger's
shape.

## Behavior changed
Yes.

- **Write:** `handle_post_tool_use` keys on `binding_key(data)` instead of `data["session_id"]`.
- **Read:** `decide_stop` and `decide_session_start` iterate `session_view(binding, sid)` instead of
  `binding.get(sid)`.
- **Unchanged on purpose:** the bind-on-resume write in `decide_session_start` stays under the bare
  `session_id` (SessionStart carries no `agent_id`); the nudge / three-strike ledger stays keyed by
  the bare `session_id`; a top-level payload's key is byte-for-byte what it was before.

## The composition table, with counts

Measured over the six pinned payloads plus twelve rows derived by mutating them, printed by
`test_binding_key_composition_table_over_the_six_real_payloads` and
`test_binding_key_rejects_unusable_agent_ids_derived_from_real_payloads`:

```
$ python -m pytest tests/test_spine_rail.py -q -k binding_key -s
  Bash   agent_id=None               -> 'c9b25095-7728-405e-bfe7-69c03d7343b0'
  Bash   agent_id='a8f0a946eaaa2fe6c' -> 'c9b25095-7728-405e-bfe7-69c03d7343b0#a8f0a946eaaa2fe6c'
  Bash   agent_id='adb52b4ec6c7dbd40' -> 'c9b25095-7728-405e-bfe7-69c03d7343b0#adb52b4ec6c7dbd40'
  Agent  agent_id=None               -> 'c9b25095-7728-405e-bfe7-69c03d7343b0'
  Agent  agent_id=None               -> 'c9b25095-7728-405e-bfe7-69c03d7343b0'
  Bash   agent_id=None               -> 'c9b25095-7728-405e-bfe7-69c03d7343b0'
composition table: 4 bare / 2 composite over 6 real payloads
.  rejected: empty agent_id
  rejected: null agent_id
  rejected: int agent_id
  rejected: dict agent_id
  rejected: separator in agent_id
  rejected: forward slash in agent_id
  rejected: backslash in agent_id
  rejected: parent traversal in agent_id
  rejected: empty session_id, subagent
  rejected: missing session_id, subagent
  rejected: empty session_id, parent
  rejected: missing session_id, parent
adversarial rows derived from real payloads and rejected: 12
..
3 passed, 60 deselected in 0.29s
EXIT=0
```

**4 bare / 2 composite** over the 6 real payloads, and **12** adversarial rows — twice the required
six — every one derived by mutating a real captured payload and every one binding nothing. The two
unmutated bases are asserted usable first, so each `None` is caused by the mutation, not by the base.

## The real decomposition of the six payloads — NOT the handoff's 3/2/1

The handoff said "3 parent-scope Bash/Write calls, 2 subagent-scope, 1 parent `Agent`-dispatch —
check the real decomposition." Checked. It is **2 / 2 / 2**:

```
$ python -m pytest tests/test_spine_rail.py -q -k probe_fixture -s
probe_payloads.jsonl normalized bytes = 13155, sha256 = b03536865c8c0215939346447ebd196c579cf051228aa5a9bb75898c10a37402
.probe decomposition: 2 parent Bash / 2 subagent-scope / 2 parent Agent-dispatch
subagent agent_ids: ['a8f0a946eaaa2fe6c', 'adb52b4ec6c7dbd40']
.
2 passed, 58 deselected in 0.28s
EXIT=0
```

Two parent `Bash` calls, two subagent-scope `Bash` calls with distinct `agent_id`s, and **two**
parent `Agent`-dispatch calls (one per dispatched subagent), both with no `agent_id`. No `Write`
calls in the capture at all. All six share one `session_id` — the pile-up this gate fixes.

## The sha256 pin, and why it hashes normalized bytes

The pin is over the fixture's **newline-normalized** bytes
(`b03536865c8c0215939346447ebd196c579cf051228aa5a9bb75898c10a37402`, 13155 bytes), not raw
working-tree bytes. The working tree holds CRLF (raw sha256
`804313f4ab0fc56cbf08bf4553ecdba517c3405199e1f9d9b21f870540d5a97c`, 13161 bytes) while
`.gitattributes` sets `* text=auto`, so a raw-byte hash would break on the next checkout for reasons
having nothing to do with a hand-edit — `docs/agents/CREW_CONTEXT.md` names this exact trap. The copy
itself was verified byte-identical to the evidence file.

**The pin was demonstrated to catch the edit it exists to catch.** A convenient `agent_id` was
hand-injected into payload 0 of the fixture; the pin and the decomposition and the composition table
all went red, then the fixture was restored byte-identically:

```
$ (inject agent_id='hand-injected' into payload 0)
fixture hand-edited: injected agent_id into payload 0
$ python -m pytest tests/test_spine_rail.py -q -k "probe_fixture or binding_key"
composition table: 3 bare / 3 composite over 6 real payloads
FAILED tests/test_spine_rail.py::test_probe_fixture_sha256_pin - assert 13184...
FAILED tests/test_spine_rail.py::test_probe_fixture_decomposition - assert (1...
FAILED tests/test_spine_rail.py::test_binding_key_composition_table_over_the_six_real_payloads
3 failed, 2 passed, 69 deselected in 0.47s
TAMPERED_EXIT=1
restored byte-identical: True
```

## The `session_view` settle contains composite keys

`test_session_view_merges_one_bare_and_two_composite_keys` builds a **five-key** store through the
real claim writer from the real payloads — **one bare key, two composite keys** (one per agent), plus
two decoys: another session's composite key, and a `<sid>-lookalike` key that starts with the sid but
is not a child of it. Printed by the test:

```
store keys = 5 (1 bare + 2 composite + 2 decoy); merged view entries = 3
```

Three keys contribute, one entry each; the merged view holds exactly **3** entries and neither decoy
appears. The lookalike is why the prefix test is `sid + BINDING_KEY_SEP`, not a bare `startswith`.

`test_stop_blocks_on_mid_flight_spine_held_only_under_a_composite_key` is the non-vacuous half: the
bare key holds only a released, complete spine, and the sole mid-flight spine is bound under a
subagent's composite key. `decide_stop` blocks and its reason names that spine's gate
(`g9`, `COMPOSITE-MARKER`). On a bare-key-only store this test cannot exist; against the pre-change
hook it fails.

## The remaining required evidence

- **A composite claim leaves the bare key's entry set byte-identical** —
  `test_post_claim_subagent_writes_composite_key_bare_set_byte_identical` snapshots
  `json.dumps(binding[sid], sort_keys=True)` before the subagent's claim and asserts equality after.
- **Two distinct `agent_id`s produce two independent key sets** —
  `test_post_claim_two_agent_ids_give_two_independent_key_sets`; each key holds exactly one candidate
  (`[len(v) for v in binding.values()] == [1, 1]`), which is precisely the gauge writer's ambiguity
  test, and nothing lands under the bare parent key.
- **A composite release removes only that agent's entry** —
  `test_post_release_composite_removes_only_that_agents_entry`: three keys before, the other agent's
  key and the parent's bare key intact after.
- **A release under a composite key leaves `nudges[bare_sid]` untouched** —
  `test_post_release_composite_leaves_bare_nudge_ledger_untouched`, with
  `test_post_release_parent_still_clears_its_own_bare_nudge_ledger` guarding the other half.
- **An unusable `agent_id` writes no binding anywhere** —
  `test_post_claim_unusable_agent_id_writes_no_binding_anywhere` fires seven malformed claims and
  asserts the whole store is unchanged (`json.dumps(after) == before`), including that nothing leaked
  under the parent's bare key.
- **The empty-set cleanup removes the composite key and leaves the bare key's entries intact** —
  `test_post_release_empty_set_cleanup_deletes_composite_key_not_bare` puts the parent and the
  subagent on the *same* spine path under different keys, so a wrong `del binding[sid]` would wipe the
  live parent's binding; after the subagent's release the composite key is gone and the parent's entry
  set is byte-identical.
- **`decide_session_start`'s bind-on-resume write lands under the bare key** —
  `test_session_start_bind_on_resume_still_writes_under_the_bare_key`: the sid already holds a foreign
  composite entry (so the scan path is genuinely reached), and the new entry appears under the bare
  `sid` with the composite entry untouched.
- **`decide_session_start` still reaches a composite-only spine** —
  `test_session_start_resumes_from_a_spine_bound_only_under_a_composite_key`, with the spine placed
  outside `proj/.agent-work` and `_scan_active_spine(proj) == []` asserted, so the composite key is the
  only route to it.

## Test mode
**Required:** `test-first` (a test surface exists).
**Satisfied:** yes. Every implementation slice was driven red → green, and the red was attested to the
engine at each gate with its real output:

- m1-fixture RED: `2 failed, 58 deselected`, exit 1 — `FileNotFoundError` on the fixture.
- m2-binding-key RED: `3 failed, 60 deselected`, exit 1 — `AttributeError: module 'spine_rail' has no
  attribute 'binding_key'. Did you mean: 'binding_path'?`
- m3-write-routing RED: `6 failed, 9 passed, 55 deselected`, exit 1 — composite key absent; entries
  piled under the bare sid.
- m4-read-routing RED: `3 failed, 4 passed, 67 deselected`, exit 1 — no `session_view`; Stop allowed a
  composite-only mid-flight spine; SessionStart returned `{}`.

## Evidence — the handoff's required verification commands

```bash
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests/test_spine_rail.py -q
```
```
74 passed in 0.95s
EXIT1=0
```
**Result:** pass. 58 before, 74 after: 16 new tests, 0 pre-existing tests edited.

```bash
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest tests/test_gauge_writer.py tests/test_gauge_reader.py -q
```
```
82 passed in 1.08s
EXIT2=0
```
**Result:** pass.

```bash
cd C:/Programs/constellation-skills-wt/epic418-a-419 && python -m pytest -q
```
```
1637 passed, 2 skipped, 550 subtests passed in 446.64s (0:07:26)
FULL_EXIT=0
```
**Result:** pass. Baseline at HEAD `990712f` was 1621 passed, 2 skipped, 550 subtests; +16 is exactly
the 16 tests added here, so nothing else moved.

## Would these checks pass in a world where the change did nothing?

No, and that was measured rather than argued. `scripts/hooks/spine_rail.py` was reverted to HEAD
(tests and fixture left in place) and the module re-run:

```bash
git checkout HEAD -- scripts/hooks/spine_rail.py && python -m pytest tests/test_spine_rail.py -q
```
```
13 failed, 61 passed in 1.31s
REVERTED_EXIT=1
```

All 13 hook-dependent new tests go red against the pre-change hook, and all 61 pre-existing tests stay
green. The two remaining new tests (`test_probe_fixture_sha256_pin`,
`test_probe_fixture_decomposition`) pass against the old hook by design — they guard the fixture, not
the hook — and their own failure mode was demonstrated separately by tampering with the fixture
(above). The file was then restored from a byte-copy and the module re-run: `74 passed`, exit 0.

## Close criteria

| # | criterion | verdict |
|---|---|---|
| 1 | `binding_key` implements the three-way table exactly | **met** — 6 real + 12 derived adversarial rows |
| 2 | composite claim leaves the bare set byte-identical; two `agent_id`s give two key sets | **met** |
| 3 | a composite release removes only that agent's entry | **met** |
| 4 | an unusable `agent_id` writes no binding anywhere | **met** |
| 5 | `decide_stop` / `decide_session_start` still see every spine they saw before | **met** — 61 pre-existing tests unedited and green, plus the composite-only Stop and SessionStart cases |
| 6 | every existing test in `tests/test_spine_rail.py` passes unedited | **met** — `git diff -U0 tests/test_spine_rail.py \| grep -c '^-[^-]'` → `0`; 468 insertions, 0 deletions |

## Map Impact

- **Structural anchors touched:** `scripts/hooks/spine_rail.py` — three new module-level symbols
  (`BINDING_KEY_SEP`, `binding_key`, `session_view`) and four routed call sites
  (`handle_post_tool_use` claim / release / cleanup, `decide_stop` read, `decide_session_start` read).
- **Capabilities added/changed:** the binding store can now attribute an entry to the agent that
  produced it, which is the precondition for a per-agent gauge reading.
- **Constraints/assumptions touched:** fail-closed on unresolved identity is now mechanical, not
  prose. `binding_key` is the **single** composer of the composite key anywhere in the codebase; gate
  g2 must call it through the `_spine_rail` handle `gauge_writer_hook.py` already loads
  (`_load_spine_rail`, line 103; `_spine_rail` bound at line 120), not compose a second one.
- **Decision candidates:** `decision:agent-id-null-is-unusable` — a payload carrying `agent_id: null`
  reads as present-but-unusable and binds nothing, per the handoff's literal table ("not a string").
  See the assumption below; this one is worth a Commander glance.
- **Claims/evidence produced:** the harness delivers `agent_id` on subagent tool calls and omits the
  key entirely on parent calls — now pinned as a fixture rather than asserted in prose.
- **Trust limitations:** this repo has no `docs/architecture` map, and `docs/GAUGE_WRITER_HOOK.md` is
  known wrong about the sidechain filter. I read the code, not the document, and changed neither.

## Blast radius — every reader of what I changed, enumerated by command

`grep -rln "spine-rail-binding\|load_binding\|binding_path\|spine_rail" --include=*.py --include=*.md
--include=*.json .` returns **89** paths; 84 are `.agent-work/` run artifacts, notes and archives that
only describe the store. The live readers are five:

| path | effect |
|---|---|
| `scripts/hooks/spine_rail.py` | changed here |
| `scripts/hooks/gauge_writer_hook.py:159` | still `binding.get(session_id)` — **gate g2's**, untouched, see below |
| `tests/test_spine_rail.py`, `tests/test_gauge_writer.py` | green (74 / 82) |
| `.claude/settings.json`, `scripts/install_constellation.py` | register the hook by path; key shape is opaque to them |
| `docs/GAUGE_WRITER_HOOK.md` | describes the store; correcting it is out of my scope (issue's item 4) |

**The interim state between g1 and g2, stated plainly:** `gauge_writer_hook.resolve_gauge_path` reads
`binding.get(session_id)` and so cannot see a composite key. Until g2 routes it through `binding_key`,
a subagent's gauge resolves to **zero** candidates and writes nothing — where before it resolved to
an ambiguous **many** and also wrote nothing. No reading is lost. The parent side strictly improves:
its bare key now holds only its own entries, so the `len(gauge_paths) > 1` ambiguity that silenced it
may already be gone. `tests/test_gauge_writer.py` passes unchanged because its fixtures are bare-keyed.

## Docs/contracts touched
None. `docs/GAUGE_WRITER_HOOK.md` is wrong about the sidechain filter and silent on `agent_id`, but
correcting it is a later gate's scope and the handoff forbids widening.

## Assumptions

- **`agent_id: null` binds nothing.** The handoff's table says an `agent_id` that is "not a string"
  is unusable, and `None` is not a string, so I implemented it literally and documented it in the
  docstring. The probed harness never sends null — it omits the key — so this is unreachable today.
  It is worth one Commander glance because the blast radius is asymmetric: if a future harness sent
  `agent_id: null` on *parent* calls, this reading would unbind every top-level agent, whereas
  treating null as absent would only mis-file a subagent. I did not build for that hypothetical; I am
  flagging it.
- Merge order in `session_view` is store order, so if the same `abs_spine_path` were ever bound under
  both a bare and a composite key, the later key wins. The entries would be near-identical (same
  spine, same worktree) and only `engine_session` / `claimed_at` could differ, so no reader's decision
  changes. `decide_stop` iterates values, `decide_session_start` takes the first non-foreign one.

## Stop conditions hit
None. No close criterion was unreachable, `gauge_writer_hook.py` never needed editing, no existing
test needed editing, and the three-way rule held up — the empty-set-cleanup test is the concrete case
where the two-way version would have deleted a live parent's binding.

## Out-of-scope observations

1. **The handoff's stated fixture decomposition (3/2/1) is wrong; it is 2/2/2.** The handoff told me
   to verify rather than trust it, so this is the mechanism working, but any other artifact quoting
   3/2/1 should be corrected.
2. **`docs/GAUGE_WRITER_HOOK.md` now has a second inaccuracy** beyond the known sidechain one: its
   description of the store as "mapping session_id -> spine path" no longer holds for subagents. The
   issue already owns correcting that file (its item 4); recording it so it is not forgotten.
3. **`gauge_writer_hook.py`'s docstring (lines 26–33) describes the binding as keyed by `session_id`.**
   That prose is now stale in the same way. It sits inside g2's file, so I left it.
4. **A pre-existing test monkeypatches `_scan_active_spine` to return a spine *dict* where the real
   function returns a *list of tuples*** (`tests/test_spine_rail.py:391`, the `#261` regression test).
   The test still proves its point because it never reaches the scan branch, but the stub does not
   match the contract it replaces, so if that test ever did reach the branch it would fail for the
   wrong reason. Not touched — it is a pre-existing test and editing it is out of scope.

## Workflow Feedback

- **Handoff gaps:** two real ones.
  1. **Constraint 1 and the required-evidence list contradict each other on the nudge ledger.**
     Constraint 1 says "the nudge/escape-hatch ledger deletion on release keeps the bare
     `session_id`", which read alone means a subagent's release deletes `nudges[bare_sid]`. The
     evidence list says "a release under a composite key leaves `nudges[bare_sid]` untouched." Both
     can hold only if the ledger stays bare-keyed *and* the delete fires only for a top-level release.
     I implemented that reading (`if key == sid:`) because the evidence section is named as the gate,
     and I commented both halves at the code site. If Commander wanted the other reading, this is the
     one line to change.
  2. **The 3/2/1 decomposition was wrong** (it is 2/2/2). The handoff hedged it explicitly, which
     saved the round-trip — that hedge is the pattern to keep.
- **Context rediscovered:** the fixture's CRLF-under-`text=auto` hazard. The handoff said "pin its
  sha256" with no mention that a raw-byte hash is exactly the Windows failure `CREW_CONTEXT.md` warns
  about; I had to find that myself and normalize. Worth one clause in any future "pin a fixture"
  instruction.
- **Instructions improvised around:** the implementer plan template models one implementation item
  (`m1`) plus context, so the vertical-slice guidance and the "one item per implementation step"
  instruction had to be reconciled by hand into six items. That worked fine — noting it only because
  the template's shape suggests a smaller plan than the doctrine asks for. Also: the engine refuses
  `start <id>` while a `check: null` precondition is unmet, and the template's own note about
  attest-then-start is buried in `m1`'s imperative rather than stated at the top; I hit the refusal
  once before reading it.
- **What would have made this easier:** resolve the nudge-ledger contradiction above in the handoff
  text, and state in the "pin the fixture" instruction that the hash must be over normalized bytes on
  this repo.

## Return status
`complete`
