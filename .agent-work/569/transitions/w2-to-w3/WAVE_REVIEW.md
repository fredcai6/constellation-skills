## Wave review -- wave 2 (`w2-basis`, `w2-ledger`, `w2-reindex`)

**All three lanes merged.** #653 at `55381c12`, #656 at `333f02b4`, #657 at `ace7f0c2`. Main verified
green at **3731 passed, 9 skipped, 0 failed** in a clean detached worktree.

### What the wave proved

- **Sonnet carries engine surgery.** The v1 contract named `checklist_engine.py` (4,101 lines) as the
  likeliest double-block trigger. Three lanes, three merges, **zero escalations**, every lane
  `attempt=1` with `total_rework=0`.
- **`w2-basis` invented the family-B remedy unprompted.** No launch order asked for it: implementing a
  hand-authored basis field, it refused to certify a HEAD it had not been verified against and wrote
  the refusal into the test. That is the strongest available evidence that the mechanism is one agents
  reach for naturally rather than machinery imposed on them.

### What the wave refuted

| claim | verdict |
|---|---|
| A `MERGEABLE`, approved, "0 failed" PR yields a green main | **False.** #645 merged clean and turned `MapTreeFreshnessTests` red. The defect existed on **neither parent**. |
| There is no automated defence against a PR that reds main | **False, and the wave's sharpest correction.** `ci.yml` triggers on `pull_request`, so CI already tests `refs/pull/N/merge` and **already went red on #645**. Ignored because the last 12 runs are 12 failures. |
| The unlaunched member issues are all one defect family | **False.** 4 A / 4 B / 3 both / 2 C / 1 neither. Family B was already filed **seven times**. |
| Refresh-requests raised by a commander are answered | **False.** 8 raised, 0 answered. Nothing *consumes* a refresh-request; the relaunch **is** the refresh. |
| `CommanderSpineBasisFields` guards the shipped basis fields | **False.** 3 skipped -- pinned to whole-repo `HEAD`, inert one wave later. |
| A crew dispatched via `run_crew.py` gets its own door | **False for `spine=None`.** All 7 crews inherited the dispatcher's pair and each rediscovered it independently. |

### Disposition

**`replan`.** Wave 3 is re-decomposed into four family-cut lanes and becomes the **last** wave; wave 4
is cancelled. Lane 3 shrank from "build an Admiral-side test-merge protocol" to "add one `ubuntu-latest`
job", because the mechanism already existed and was merely untrusted.


### Fixed-boundary changes -- recorded in the latitude contract, not proposed here

Four of this boundary's changes touch surfaces the replan schema treats as **fixed** (`intent_and_why`, `fixed_decisions`, `good_enough`, `hard_constraints`). They are deliberately **absent** from `material_changes`, because the schema models a fixed-boundary entry as a *delegate proposing a change upward* -- it forces `applicable: false` and an escalation packet, and permits only one boundary per packet. That is the wrong shape here: **the human already ruled on all four**, in conversation at the wave-2 checkpoint, and they are recorded where human rulings belong --
`.agent-work/569/LATITUDE_CONTRACT.md` v2 (v1 preserved at `LATITUDE_CONTRACT-v1-wave1-2.md`), `.agent-work/569/INTERROGATION_RECORD.json`, and the `ADMIRAL_LOG` entries for this checkpoint.

For the record, the four are:

- **`fixed_decisions`** — #558 is REFUTED on measurement and closes with the measurement posted on it. The corpus carries exactly ONE reviewer signature (EXECUTE_PLAN.template.json c2); the invoker level already happens behaviourally; 'the chain terminates at a human' is a doctrine line that enforces nothing and codifies the escalation the human wants reduced; `n` has no dial to constrain. Its executor/reviewer/invoker cut survives as one line of prose.
  *Why:* The human's own pushback -- 'the dispatcher typically has a solid trust but verify attitude. is there actually something here? I am starting to think not' -- was correct, and going looking for where trust-but-verify is written down found that it is NOT: fleet-doctrine.md:194 ships verify-checks-green then merge, with no step inspecting the merge result. More reviewers is structurally the wrong instrument for a defect that exists on neither parent.
- **`good_enough`** — Appetite: three waves; cleared autonomous through wave 3 INCLUDING merges, present the epic summary at closeout for acceptance.
  *Why:* Human ruling at the wave-2 checkpoint refresh ('still sonnet, you got the latitude'), recorded in LATITUDE_CONTRACT.md v2.
- **`hard_constraints`** — No new unwired checker, AND no new mechanism where an existing one is merely untrusted -- check first whether the guard already exists and its signal is being discarded (decision:fix-the-instrument-not-the-check).
  *Why:* w3-ci is the case in point, and generalising it is the sharpest thing wave 2 taught. Also newly constrained: the `basis` field is NOT backfilled across the 65 (measured 2/19 gain), and the Admiral's monitor MUST poll for `REFRESH REQUESTED:` and actually relaunch -- wave 2 raised 8 and answered 0.

**Schema gap, parked:** the replan packet has no way to record a fixed-boundary change the human authorised out-of-band. Every such change is forced into the escalation shape, which refuses the launch — so the only way to proceed is to omit it from the packet, which is exactly how a planning record loses the changes that matter most.
