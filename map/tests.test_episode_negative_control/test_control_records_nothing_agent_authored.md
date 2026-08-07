# tests.test_episode_negative_control:test_control_records_nothing_agent_authored
function, tests/test_episode_negative_control.py:664, 78 lines

```python
def test_control_records_nothing_agent_authored(control)
```

`zero agent effort` is literal — asserted over the ACTUAL argv of every call.

**The honest claim, stated exactly as it is:** the control supplies the engine no
agent-authored NARRATIVE. Every string it hands over is a fixed identifier declared in
this module — the work id, the temp repo's directory name, `PARENT_ROLE`, the
condition ids, and one `reopen --reason` — and nothing composed at issue time. No
`--why`, no `--note`, no `--finding`.

The mechanical fields that echo those identifiers — `run`, `project`, `role` — are
echoing what the run is *made of*, not prose an agent wrote *about* the run, and it
cannot be otherwise: a run must have an id, a project and a lease holder. A guard
demanding that no supplied string reach them would be unfalsifiable theatre.

**What the assertion below actually checks, which is narrower than that claim:** the
argv census. Every flag is sanctioned for its verb (closed-world), `advance` carries
`--mechanical`, `attest` carries no `--note`, and the flags named in
`AGENT_TEXT_FLAGS` hold exactly the two declared constants. Identifiers passed
positionally, and `--cond`, are outside its reach — stated here because the whole
point of this gate is that a docstring must not claim more than its code checks. Two
earlier versions of this docstring did exactly that: "nothing agent-authored was
recorded" (false — `reopen --reason` writes to `why_trail`), then "exactly ONE fixed
constant, and it feeds no mechanical field" (false in both halves — `--claimed-by` is
a second one and it *is* the `role` field). Each was corrected only after a mutation
proved it false, which is the lesson: the sentence is not evidence, the census is.

The previous version of this test asserted only that the issued VERB NAMES were a
subset of `VERBS` — something `_ControlRun._run` already asserts on every call — and
left every claim about flags in a comment. Mutation M1 (rewrite every
`advance --mechanical` to `advance --why "<prose>"` and add a `--note` to every
`attest`) passed it cleanly while four rows of agent prose landed in `why_trail` and
`satisfied_by`. A guard that cannot fail is the thing this whole gate exists to
detect, so it is now a CLOSED-WORLD census over `run.calls`: every flag token must
be sanctioned for its verb, `advance` must positively carry `--mechanical`, `attest`
must positively carry no `--note`, and the free-text census must come back holding
exactly the one permitted constant.

calls internal: _flag_pairs
calls stdlib: builtins.set x3, builtins.sorted x2
reads internal: ALLOWED_FLAGS x4, _ControlRun x2, AGENT_TEXT_FLAGS, PARENT_ROLE, _ControlRun.REOPEN_REASON, _ControlRun.VERBS
reads stdlib: builtins.str x4, builtins.list, builtins.set, builtins.tuple
unresolved: 5 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: none found
