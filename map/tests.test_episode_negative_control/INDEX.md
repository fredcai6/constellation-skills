# tests.test_episode_negative_control
tests/test_episode_negative_control.py, 1150 lines, 17 holes

#305 gate g3 — the NEGATIVE CONTROL for `zero agent effort is literal`.

The claim under test is `docs/EPISODE_STORE.md` §4's mechanical bin: *a run where the
agent records nothing must still yield the full mechanical field group*. A field an
agent can omit by forgetting is not mechanically captured — it is agent-supplied
wearing a mechanical label — so this file drives a **real engine spine** in which the
agent authors nothing at all, and then compares the composed group, field by field,
against a tally this harness keeps **itself**.

Three properties make this a control rather than a demonstration.

**1. The oracle is independent.** `_ControlRun` increments its own expectation at the
moment it issues the triggering call — when it issues a reopen it expects honored, it
increments `_reopens` on that line. It never calls `mechanical_fields()`,
`reopen_total()`, `failed_command_count()` or `context_manifest.rev()` to decide what
the answer should be, and it never re-derives an expectation from the checklist JSON.
Any of those would compare the thing to itself. `context-manifest-ref`'s revision is
computed here as a raw git blob OID (`sha1(b"blob <n>\0" + data)`), and independently
cross-checked against `git hash-object --no-filters`, which is a second witness that
shares no code with the producer.

**2. It exercises BOTH lease topologies, because only one of them is production.**
Gates live in the CHILD gate-plan a parent spine delegates to, and that child never
receives a lease (#357). `_lease_role` reads `engine_session.claimed_by`, and
`refusals` is armed only by `claim` — so on the child both are structurally
unavailable, and no agent action can change it. A control that drove only a claimed
standalone spine would report all ten fields green and prove nothing about the seam
that actually fires in production. Both topologies are driven through the SAME verb
sequence, so the lease is the only difference between them and the delta cannot be
attributed to anything else.

**3. Refusal is asserted, not skipped.** A field the composer legitimately refuses is
expected as `REFUSED` and the comparison fails if it turns up *present* — so the
refusal assertions can themselves go red (`test_red_proof_sharp_fabricated_role`
proves exactly that). A non-reading stays visibly distinct from an uncollected one.

**The comparison returns a list of mismatched field NAMES, never a boolean.** That is
what lets the red-proofs below assert `mismatches == ["failed-commands"]` — a per-field
claim. A non-zero exit code is not proof a check can fail: an import error, a collection
error and an empty test selection all exit non-zero too.

imports stdlib: __future__.annotations, ast, builtins, contextlib, hashlib, inspect, io, json, os, pathlib.Path, subprocess, sys, textwrap
imports third-party: apply_episode_delta, context_manifest, episode_capture, pytest, query_episodes
imported by: none found

```python
REPO_ROOT = Path(__file__).resolve().parents[1]
ENGINE = REPO_ROOT / 'scripts' / 'checklist_engine.py'
MECHANICAL_GROUP = tuple(episode_capture.REQUIRED_MECHANICAL_FIELDS) + ('artifact-ref',)
AGENT_TEXT_FLAGS = frozenset({'--why', '--note', '--finding', '--reason', '--statement', '--verdict', '--s...
ALLOWED_FLAGS = {'claim': frozenset({'--session-id', '--claimed-by', '--worktree'}), 'start': frozenset...
VALUELESS_FLAGS = frozenset({'--mechanical', '--force', '--dry-run'})
PARENT_ROLE = 'commander'
REFUSED = _Refused()
FORBIDDEN_PRODUCERS = tuple(((episode_capture, name) for name in ('mechanical_fields', 'reopen_total', 'faile...
FORBIDDEN_IDENTIFIERS = frozenset({name for _, name in FORBIDDEN_PRODUCERS} | {'compose', 'snapshot', 'episode_...
DECLARED_CONTEXT = ({'root': 'repo', 'path': 'seed.txt'}, {'root': 'repo', 'path': 'changed_by_the_run.txt'})
```

- [_flag_pairs](_flag_pairs.md) function: `(flag, value)` for every flag in one issued argv, positionals dropped.
- [_Refused](_Refused.md) class: Sentinel: this field is expected to be ABSENT, and absence is the correct
  - [_Refused.__repr__](_Refused.__repr__.md) method: HOLE: no docstring
- [Expect](Expect.md) class: One field's expected value plus the INDEPENDENT source it came from.
  - [Expect.__init__](Expect.__init__.md) method: HOLE: no docstring
  - [Expect.__repr__](Expect.__repr__.md) method: HOLE: no docstring
- [compare_fields](compare_fields.md) function: The comparison. Returns the names of the fields that do not match, in
- [_independence_harness](_independence_harness.md) function: Make every producer under test UNCALLABLE, and the emitted snapshot UNREADABLE.
  - [_independence_harness.patch](_independence_harness.patch.md) method: HOLE: no docstring
  - [_independence_harness.raiser](_independence_harness.raiser.md) method: HOLE: no docstring
    - [_independence_harness.raiser.boom](_independence_harness.raiser.boom.md) method: HOLE: no docstring
  - [_independence_harness.guard](_independence_harness.guard.md) method: HOLE: no docstring
  - [_independence_harness.guarded_open](_independence_harness.guarded_open.md) method: HOLE: no docstring
  - [_independence_harness.guarded_read_text](_independence_harness.guarded_read_text.md) method: HOLE: no docstring
  - [_independence_harness.guarded_read_bytes](_independence_harness.guarded_read_bytes.md) method: HOLE: no docstring
- [blob_oid](blob_oid.md) function: Git blob OID over `data`'s own bytes, computed here.
- [_git](_git.md) function: HOLE: no docstring
- [expected_rows](expected_rows.md) function: What the delivered-context rows MUST say, computed HERE from the files' bytes.
- [compare_manifest_rows](compare_manifest_rows.md) function: Mismatched declared PATHS, in declaration order — a list of names, never a bool,
- [_write_json](_write_json.md) function: HOLE: no docstring
- [_plan](_plan.md) function: Two gates, identical on parent and child so the LEASE is the only difference.
  - [_plan.gate](_plan.gate.md) method: HOLE: no docstring
- [_ControlRun](_ControlRun.md) class: Drives ONE checklist through the real engine CLI and keeps its own tally.
  - [_ControlRun.__init__](_ControlRun.__init__.md) method: HOLE: no docstring
  - [_ControlRun._run](_ControlRun._run.md) method: HOLE: no docstring
  - [_ControlRun._session](_ControlRun._session.md) method: HOLE: no docstring
  - [_ControlRun.drive](_ControlRun.drive.md) method: The whole run. Every action is one a run mechanically requires.
  - [_ControlRun.expectations](_ControlRun.expectations.md) method: HOLE: no docstring
  - [_ControlRun.compose](_ControlRun.compose.md) method: The reading under test. Attribute lookup on the module happens HERE, at call
  - [_ControlRun.manifest](_ControlRun.manifest.md) method: The step's delivery manifest, as the seam wrote it (#360, see `expectations`).
  - [_ControlRun.snapshot](_ControlRun.snapshot.md) method: What the SEAM wrote on its own, with no test asking it to.
- [control](control.md) function: One real parent->child gated run, driven once for the whole module.
- [test_control_records_nothing_agent_authored](test_control_records_nothing_agent_authored.md) function: `zero agent effort` is literal — asserted over the ACTUAL argv of every call.
- [test_claimed_parent_topology_yields_the_full_mechanical_group](test_claimed_parent_topology_yields_the_full_mechanical_group.md) function: (a) A claimed spine: every one of the ten fields present AND correct.
- [test_unclaimed_child_topology_refuses_only_role_and_refusals](test_unclaimed_child_topology_refuses_only_role_and_refusals.md) function: (b) The PRODUCTION shape: gates live in a child gate-plan that never gets a
- [test_the_seam_emits_the_same_group_unasked](test_the_seam_emits_the_same_group_unasked.md) function: The group is not merely composable on demand — the seam wrote it during the run.
- [test_every_field_has_a_named_independent_source](test_every_field_has_a_named_independent_source.md) function: C3: the control must be able to say, per field, what the independent source was —
- [test_declared_context_is_delivered_and_pinned](test_declared_context_is_delivered_and_pinned.md) function: The delivered-context half of the manifest, EXERCISED and compared per row.
- [test_a3_a_null_manifest_does_not_read_as_success](test_a3_a_null_manifest_does_not_read_as_success.md) function: Attack A3, now REACHABLE: every declared ref resolves to a missing file.
- [test_red_proof_blunt_hardcoded_composer](test_red_proof_blunt_hardcoded_composer.md) function: R1: the composer returns plausible constants. The control must name EVERY field.
- [test_red_proof_sharp_drops_exactly_one_derivation](test_red_proof_sharp_drops_exactly_one_derivation.md) function: R2: drop EXACTLY ONE derivation. The control must name EXACTLY that field.
- [test_red_proof_sharp_fabricated_role](test_red_proof_sharp_fabricated_role.md) function: R3: the REFUSAL assertions must be falsifiable too, or they are the vacuum.
- [test_red_proof_sharp_inflated_reopens](test_red_proof_sharp_inflated_reopens.md) function: R4: run-scoped `reopens` and step-scoped `rework-count` are two facts, not one
- [_create_op](_create_op.md) function: A create op. `id` is deliberately absent — the writer ASSIGNS it (EPISODE_STORE
- [seeded_store](seeded_store.md) function: A temp store seeded through the SANCTIONED WRITER, never by hand-placing files.
- [test_cross_run_retrieval_links_episodes_across_runs](test_cross_run_retrieval_links_episodes_across_runs.md) function: The acceptance surface: an episode written by one run is reachable from another
- [test_rhyme_search_survives_consolidation](test_rhyme_search_survives_consolidation.md) function: Mark one cluster member CONSOLIDATED, then confirm rhyme-search still finds its
- [test_321_observation_where_a_handed_id_is_validated](test_321_observation_where_a_handed_id_is_validated.md) function: #321: the store validates ids it LISTS but not every id it is HANDED.
- [test_canon_episode_store_untouched](test_canon_episode_store_untouched.md) function: Belt and braces (b): the tracked store's blob OIDs are READ and compared, not
