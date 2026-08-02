# Tripwire outcomes — issue #304 gate g3

Outcomes recorded **after** the deletion and **after** the run, against predictions committed
**before** either existed. The pre-registration is tamper-evident in git, and that property is verified
here rather than asserted:

```
$ git log --format="%h %ad %s" --date=short 0119fa4 -1
0119fa4 2026-08-01 pre-register(#304): tripwire predictions BEFORE any prose deletion
$ git log --format="%h %ad %s" --date=short 1662b90 -1
1662b90 2026-08-01 pre-register(#304): T5, the anchor change, after PRE-B named the mechanism

$ git merge-base --is-ancestor 0119fa4 ea52b2f   # ea52b2f = the block-(a) deletion
0119fa4 IS an ancestor of the block-(a) deletion ea52b2f
$ git merge-base --is-ancestor 1662b90 ea52b2f
1662b90 IS an ancestor of the block-(a) deletion ea52b2f

$ git diff 1662b90 HEAD --stat -- TRIPWIRES.md
(empty — TRIPWIRES.md is byte-identical to its pre-registration commit; it was not rewritten)
```

**Pre-registration SHAs:** `0119fa4` (T1–T4), `1662b90` (T5).
**Run evidence:** `.agent-work/issue-304/evidence/g3-run-transcript.txt` — 384 lines of the engine's own
output, captured by `tee`, from a fresh Commander spine materialized in this repo (which has
`docs/agents/` and **no** `docs/architecture/`, the degraded common case).

Summary, before the detail:

| | prediction | outcome |
|---|---|---|
| **T1** | deleting block (a) changes nothing the engine does | **HELD** — with a named near-miss the handoff did not anticipate |
| **T2** | same, one level down | **HELD** — observed, not inferred |
| **T3** | degraded runs report rather than block; mapped repos unchanged | **HELD in part, UNTESTED in part** — and its premise was wrong |
| **T4** | a naive delete silently strips degraded-mode intake | **DID NOT FIRE** — the guard was armed and the phrase count went 2 → 1 |
| **T5** | the anchor does not on its own move ordering | **NOT DETERMINABLE AT THIS GATE** — reported as a measurement gap, per the pre-registration's own instruction |

---

## T1 — deleting the dead-path block from `COMMANDER_SPINE.template.json` `tasks.context.imperative`

Pre-registered at **`0119fa4`**. Deletion at **`ea52b2f`**, 86 words (`wc -w`).

**Predicted:** *"no run behaviour changes… a Commander spine materialized after the deletion will advance
`context` exactly as before, and no test that pins the template will fail for a reason other than the
literal string being absent."*
**Fires if:** any spine fails to advance `context`; any pinning test fails for a non-string reason; or an
agent, having lost this prose, creates `docs/agents/engine-config.json` during a run.

**Outcome: HELD (did not fire).** Observed, in order:

- A spine materialized from the post-deletion template **did** advance `context` — but only after the
  contract's own designed refusal and discharge, which is `verify-orientation` working, not this
  deletion. The relevant point for T1 is that the refusal named `c2` (orientation), never the config_ref:
  `REFUSED: context: postconditions unmet ['c2']`.
- The engine degraded the missing `config_ref` **mechanically and silently**, exactly as predicted, with
  no prose anywhere telling it to. The spine carries `config_ref: docs/agents/engine-config.json`;
  `ls -l docs/agents/engine-config.json` returned *"No such file or directory"* before and after the run;
  every engine verb ran clean. The prose was describing a mechanism, not causing it.
- **`docs/agents/engine-config.json` was not created** by either run — checked at the start and end of the
  transcript.

**Named near-miss, because a prediction that survives on a technicality should say so.** Two pinning
tests *did* fail: `test_context_manifest.py::…prose_is_not_replaced_by_the_declaration` and
`test_map_contract_wiring.py::…prose_rules_a_path_list_cannot_express_survive_the_rewrite`. Both failed
**because the literal string was absent** — they asserted the presence of `"sanctioned degradation"` and
`"do NOT create the overlay file"`, which are phrases *of the deleted block*. That is squarely inside
T1's "for a reason other than the literal string being absent" exemption, so T1 does not fire. But the
prediction's confidence came from believing the template's pins were enumerated, and they were not: the
handoff's constraints section named three suites and neither of these assertions. **The prediction was
right; the inventory behind it was incomplete.** Both sentinels were re-pointed at surviving
degraded-mode prose, intent and count unchanged, and both edits are named as deviations in
`g3-result.md`.

## T2 — deleting the byte-parallel block from `EXECUTE_PLAN.template.json` `tasks.e0-context.imperative`

Pre-registered at **`0119fa4`**. Deletion at **`456cac0`**, 86 words.

**Predicted:** *"identical to T1, one level down. An `execute.json` instantiated from the template
advances `e0-context` unchanged."*
**Fires if:** an execute plan fails to advance `e0-context`, or the two templates diverge in behaviour
after being edited in parallel.

**Outcome: HELD (did not fire).** This was **observed, not inferred** — an `execute.json` was
instantiated from the post-deletion template into the scratch work area and driven. Verbatim:

```
$ python <engine> --file .agent-work/g3-scratch-run/execute.json advance e0-context ...
e0-context -> complete
### exit: 0
```

It advanced on the first attempt, with its `config_ref` (`docs/agents/engine-config.json`) absent from
disk — the exact condition the deleted prose used to narrate. No divergence between the two templates:
both lost the same block, both still degrade the same missing file the same way.

## T3 — retargeting the pathless orientation imperatives

Pre-registered at **`0119fa4`**. Retarget at **`baf09f2`**.

**Predicted:** behaviour changes in the **degraded** case only, and changes to **reporting** rather than
silence; **no measurable ordering change** in a repo that has a map.
**Fires if:** a mapped repo shows changed orientation ordering attributable to this edit, **or** a
degraded run is refused in a way that **blocks legitimate work** rather than merely recording the gap.

**Outcome: second clause HELD (did not fire). First clause UNTESTED at this gate.** Split deliberately,
because reporting one number for both would hide which half was actually checked.

**Second clause — the degraded refusal — did not fire, and the evidence is the transcript.** The refusal
recorded the gap and then got out of the way:

```
$ python scripts/map_orient.py verify-orientation --root ... --work-id g3-scratch-run
no receipt at ...\.agent-work\g3-scratch-run\map-orientation.json -- run `orient` first
RECEIPT-MISSING
### exit: 12

$ python scripts/map_orient.py orient --root ... --work-id g3-scratch-run
DEGRADED-NO-MAP
...
degraded and NOT discharged -- still owed:
  - substitutes (what you read INSTEAD of a map, each hash-pinned)
  -     substitutes is empty -- a degraded run read SOMETHING instead of the map
  - unmapped (what stayed unmapped, stated plainly)
  - escalation (what you are escalating, and to whom)
### exit: 10

$ python scripts/map_orient.py orient ... --substitute README.md --unmapped "..." --escalation "..."
DEGRADED-NO-MAP
...
### exit: 0

$ python scripts/map_orient.py verify-orientation --root ... --work-id g3-scratch-run
DEGRADED-NO-MAP
orientation contract SATISFIED
problems: 0
substitute: README.md [known-fallback] -- found in the fixed fallback set and present on disk
### exit: 0
```

**One command discharged it.** The refusal named exactly what was owed, the discharge was a single
re-run with three flags, and the work continued. That is "recording the gap", not "blocking legitimate
work". Note also *what* discharged it — the substitute-and-record rule, the survivor T4 protects, used
in anger rather than admired in place.

**First clause — a mapped repo — was NOT tested, and this is a scope statement, not a result.** No
mapped repo was available to this gate: this repo has no `docs/architecture/`, and the one other repo
that might have served (`C:/Programs/f1Brainz`) is explicitly off-limits because `orient` **writes** a
receipt into whatever `--root` it is given. So T3's "no ordering change in mapped repos" prediction is
**unfalsified and unconfirmed here**. It is not scored as HELD.

**And T3's premise turned out to be wrong, which is a finding of its own.** The handoff stated that most
of T3's retargeting had already landed in g2, and asked me to check rather than re-edit. Checked, by
command over every commit that ever touched the template:

```
$ for sha in $(git log --format=%h -8 -- skills/commander/templates/COMMANDER_SPINE.template.json); do
    git show "$sha:skills/..." | python -c "print plan imperative[:110]"; done
ea52b2f : Map-first: BEFORE authoring execute.json, produce a mission frame from the current map using ...
fdec654 : Map-first: BEFORE authoring execute.json, produce a mission frame from the current map using ...
75ee317 : (identical)
41b1782 : (identical)
54f5965 : (identical)
582002a : (identical)
1e015d8 : (identical)
5fad3e3 : (identical)
```

`fdec654` **is** the g2 anchor commit. The context-side retarget landed there; the plan-side phrase is
**byte-identical across all eight commits**. g2 appended a large verify-frame block to the plan
imperative without touching the pathless phrase T3 named — which is how it came to read as "rewritten."
The minimal retarget was therefore made, not skipped: `from the current map using` →
`from the map input the context step resolved, using`. Four words for four.

## T4 — the load-bearing occurrence that must SURVIVE

Pre-registered at **`0119fa4`**. This is the tripwire aimed at my own edit.

**Predicted:** a naive string-level deletion removes **both** occurrences of `no docs/agents/ overlay at
all` and silently strips degraded-mode intake while appearing to remove only dead prose.
**Fires if:** after the deletion, the substitute-and-record rule is absent from the imperative.

**Outcome: DID NOT FIRE.** The deletion was done by an offset-bounded slice located by the block's
opening and closing phrases — both asserted **unique** in the raw file — never by a replace on the
ambiguous phrase. The deletion script carries the guard itself, not just the test suite:

```python
if new_imp.count(PHRASE) != 1:
    sys.exit("REFUSED (T4): phrase count after deletion is %d, expected exactly 1" % ...)
```

It printed `surviving occurrences of the overlay phrase in tasks.context.imperative: 1`.

The survivor is pinned in the shipped suite, in three directions
(`tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives`): the rule's text is **present**, the
phrase occurs **exactly once**, and the single surviving occurrence is asserted to sit **at the offset
inside the substitute-and-record sentence** — so a future edit cannot satisfy the count with some other
sentence that merely spells the phrase. Absence-only assertions would pass on an emptied imperative;
these do not.

**It is worth recording that the survivor was not merely present but load-bearing in the run.** The
degraded discharge above used a README substitute — the exact move the surviving rule instructs. Had T4
fired, the run would have lost the instruction that resolved it.

## T5 — the anchor change

Pre-registered at **`1662b90`**, after PRE-B named the mechanism.

**Predicted:** anchoring at `context` to *"before you open any source file"* does **not**, on its own,
move `map_before_src`, because it remains prose with no preventive enforcement — but it is **strictly
better positioned** than the late anchor, because `context` precedes `understand` and `plan`.
**Fires if:** POST shows orientation unchanged **AND** the anchor is shown to be irrelevant to that.

**Outcome: NOT DETERMINABLE AT THIS GATE. Recorded as a measurement gap, which the pre-registration
explicitly instructs over rounding off** (*"Distinguishing the two outcomes matters more than the
outcome… If it cannot, that is a measurement gap to report, not a result to round off"*).

**Why it cannot be determined here.** T5 is a claim about *agent ordering behaviour*, and the only
instrument that can settle it is a POST sample of real runs, comparable to PRE-B's five. This gate ran a
**single scripted drive of the engine by the agent that authored the anchor** — the operator already
knew the answer and was not sampling his own tool ordering. That is not a behavioural measurement of
`map_before_src` and must not be reported as one. POST belongs to a later gate.

**What this gate *did* establish, and it bears on the distinction:**

1. **The gate observes the receipt, never the ordering.** Searched directly:

   ```
   $ grep -n 'map_before_src' scripts/map_orient.py
   ### exit: 1   (no match — the metric PRE-B measured is not observed anywhere in the tool)
   ```

   `verify-orientation` reads the receipt's *content* — substitutes, unmapped, escalation — and nothing
   about *when* anything was read. The receipt itself (`map-orientation.json`) carries `emitted_at`,
   candidates, hashes, and no record of any source file. So a run can still read fifty source files,
   *then* `orient`, *then* advance `context`, and be exactly compliant. **The measured defect —
   lateness — remains unenforced.** This is direct support for "prose is insufficient."

2. **The anchor is nonetheless structurally better placed, and that is now mechanical rather than
   hortatory.** The late anchor could be satisfied at the END of a run because `plan` *is* the end. The
   `context` step cannot be completed at all without a discharged receipt — observed: the engine
   **refused** the advance. So while the instruction does not constrain tool ordering, it does hard-gate
   a step that sits before `understand` and `plan`. The failure mode it forecloses is real (orientation
   never happening at all); the one it does not is also real (orientation happening late).

**The gap, stated precisely so POST can close it.** These observations are consistent with
"**insufficient**" (prose cannot enforce ordering) and do not rule out "**irrelevant**" (anchor location
makes no difference), because separating those two requires runs under *both* anchors with
`map_before_src` measured the same way — which is a comparative experiment nobody has run. **POST must
be designed to distinguish them, not merely to re-report `map_before_src`.** A POST that samples only
the new anchor will return "unchanged" and will not be able to say which of the two it observed. That is
the concrete measurement requirement this gate hands forward.

---

## Filed as episodes

One per tripwire, via `scripts/apply_episode_delta.py` — the only write path into `episodes/active/`.
Each carries `expected-behavior` = the prediction as written in `TRIPWIRES.md`, and `observed-behavior` =
what actually happened above, citing the pre-registration SHA. Ids are recorded in `g3-result.md`.
