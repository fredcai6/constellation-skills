# scripts.episode_capture:reopen_total
function, scripts/episode_capture.py:294, 44 lines

```python
def reopen_total(checklist: Mapping[str, Any]) -> int | None
```

`reopens` — how many times this RUN has been reopened, summed from the

per-task `rework_count` that the engine's `reopen` verb writes and nothing else
in the engine touches.

**Run-scoped, where `rework-count` is step-scoped**, and that is what keeps the
store's two field names two facts rather than one written twice: a run may have
reopened three gates while the step this record is about was reopened once. The
worked example in `docs/EPISODE_STORE.md` §3 (`reopens: 1`, `rework-count: 1`) is
the ordinary case where they coincide, not evidence that they are the same number.

**The journal sidecar is deliberately NOT a second witness, and the reason is
measured rather than argued.** An earlier version of this field took
`max(journal_reopen_lines, rework_total)`, resting on the claim that both
witnesses could only ever UNDER-count. **That claim is false.** `reopen()`'s
rework-cap branch blocks the gate and bubbles it to the parent WITHOUT
incrementing `rework_count`, and it returns an ordinary string rather than
raising — so `main()` takes the success path and, because `reopen` is a
`MUTATING_VERB`, journals a `reopen` line for a reopen its own message says did
not happen (*"blocked and bubbled to parent (not reopened)"*). The journal
therefore over-counts by one per escalation, and `max` is exactly the operator
that prefers the inflated reading: a run with ONE real reopen emitted
`"reopens": 2`. Under `decision:refuse-never-fabricate` a fabricated mechanical
fact is the worst outcome available to this composer, so the over-counting
witness is gone rather than compensated for. `rework_count` cannot over-count:
the same branch that fabricates a journal line pointedly leaves it alone.

**The cost, stated rather than hidden: this can now UNDER-count.** An `amend`
that drops a `pending` gate carrying `rework_count > 0` takes its reopens with
it, and that is the recovery the second witness existed for. It is accepted
deliberately — under-counting is the direction this field's doctrine already
concedes, and over-counting fabricates.

`None` only when the checklist is malformed enough to have no `tasks` mapping.

calls stdlib: builtins.isinstance x4
reads stdlib: builtins.dict x2, builtins.bool, builtins.int
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
