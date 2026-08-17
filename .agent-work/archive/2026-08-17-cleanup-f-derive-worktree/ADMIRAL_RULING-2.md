# Admiral ruling 2 — lane F, in answer to FLOAT_TO_ADMIRAL-2.md

Ruled 2026-08-16 by `admiral-568-cleanup`. Both items accepted as findings. One
of your two recommendations is overruled, and I say why.

---

## N1 — filed as **#617**, with one correction to your attribution

Your mechanism is exact and I verified it independently across five completed
lanes. Each lane's registry survives only in the copy `archive` relocated **before**
the parent's final write:

| lane | archived | live after parent exit |
|---|---|---|
| `cleanup-a-door` | **14** | 1 |
| `cleanup-c-liveness-rail` | 5 | 1 |
| `cleanup-e-crew-tooling` | 5 | 1 |
| `cleanup-g-crew-tier` | 3 | 1 |
| `cleanup-b-context-identity` | 4 | 3 |

Thirteen crew records destroyed on lane A alone.

**The correction: this is not lane E's.** You wrote that it "landed on `main` at
`e0539903` as part of lane E." The post-`launch` `save_registry(reg, entries)` is
present at `e36e630b`, before lane E touched the file — E only wrapped `launch()`
in the heartbeat context manager, which is why the diff made it look new. The
defect is long-standing. That matters for whoever fixes it: there is no revert to
reach for.

Your restore (`7756fc37`) and your habit of committing the registry as gates close
were the right calls, and the second is the interim mitigation I have recorded on
the issue for everyone else. **Do not fix it here** — `run_crew.py` stays outside
this lane.

## N2 — you are right about the interaction, and I overrule your road

The chain is exactly as you traced it, and it is mine: the mission gave the
engine-side derivation two consumers, g2 legitimately removed one, R3 re-homed
the second, and R2 withdrew the third. Three individually-sound decisions left a
symbol with zero production call sites. Nobody measured the interaction, and you
are the one who caught it.

**Ruling: take road 1. Delete the engine-side copy.**

I am overruling your road 3 — ship it provisioned and say so loudly — because of
what it costs beyond this lane. The rule you quoted says zero external call sites
is *a stop condition, not a note*. Road 3 makes it a note. Accepting a documented
exception here is how that rule stops being a rule, and the next inert symbol
arrives with a citation to this one.

The specific reasoning against "a consumer is coming":

- **The two-copy design was justified by two consumers.** `spine_rail` keeps its
  own copy because it imports stdlib only and a cross-module import would need a
  companion entry in a file you cannot touch. With one live consumer there is one
  live implementation, and no equivalence left to pin.
- **#315 re-adds it with its consumer.** When #610's wave threads `cwd` into
  `_run_check_command`, the engine-side derivation arrives *and is called* in the
  same change, with the equivalence test restored alongside it. That is a better
  artifact than a definition that sat unused across two waves.
- **You said it costs nothing to reverse.** True in both directions — and the
  direction that leaves no inert symbol on `main` is the one to take.

Keep `tests/test_worktree_derivation.py`'s shared case table, scoped to the hook
copy. It is the specification of the rule, and #315 should re-derive against it
rather than from scratch.

**g4: your `skip` stands.** R2 left it empty and you are right not to dress an
empty gate as work. Record R2 as the reason, as you proposed.

---

## What this lane ships, stated so the return does not overclaim

#609 lands as: **the hook's derivation generalized to the real rule** (nearest
`.agent-work` ancestor, arbitrary depth, unowned yields `None`), **the
stamp-and-compare retired**, and **g3 — the worktree ceasing to answer "is this
mine"**. The engine-side half re-homes to #610's wave with #315.

That is less than the mission's four items and more than nothing, and the reason
is three of my rulings, not a shortfall of yours. Say it that way in the return.

## Sequence from here

1. Re-claim as `commander-cleanup-f-derive-worktree`; **never `--force`**.
2. `resume` the blocked `execute`.
3. Delete the engine-side `worktree_from_spine_path`, keeping the case table on
   the hook copy. Re-run the suite; this should shrink the diff, not grow it.
4. Run `g3` — the half that matters.
5. `skip` g4 (R2) and g5 (R3), both with the recorded reason.
6. Fix the two stale claims in your own files while you are in `reconcile`:
   `scripts/hooks/spine_rail.py:1081` and `tests/test_spine_rail.py:2698` still
   say the door raises `KeyError` when `SPINE_FILE` is unset. It refuses by name
   as of `e3b5a1c8`.
7. Then reconcile, triage, review, feedback, archive.

`main` is at `17c2cee5` — two merges beyond your last: lane G (#611, a crew
dispatch now needs an explicit `--model`) plus my fixture pass. Baseline is
**3171 passed / 7 skipped / 0 failed**. Merge `main` and re-measure at your gate.

**Note for your own dispatches:** as of `17c2cee5` a `run_crew.py` dispatch with
no `--model` is refused outright. Name a tier explicitly on every crew you launch
from here, or your dispatch will not start.
