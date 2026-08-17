# Cold plan critic — lane D1 gate plan

Inputs read: `MISSION_FRAME.md`, `execute.json`, `plan-rigor/BRIEF_COMMON.md`. Nothing else. No
authoring context. I did not open the repo, so anything that depends on file contents I have not
read is marked SPECULATIVE.

## Summary judgment

The plan's diagnosis is right and its best idea is genuinely good: it identifies that the regrowth
mechanism is a *test that mandates the text* and inverts it in the same gate as the sweep. That is
root-cause work, not deletion.

Its verification layer is not. The plan has **13 items and exactly four world-facing postconditions**
— the four `kind: command` checks at the integrate steps. Every other check is `kind: artifact`
matching `status: complete` or `verdict: APPROVE`, i.e. a crew's self-report and a second crew's
opinion of it. Of those four world-facing checks:

- one **cannot fail** (`g2-integrate` c2),
- one **cannot fail** (`g4-integrate` c2),
- one is near-vacuous (`g3-integrate` c2),
- one may be **unable to pass** without violating the plan's own scope constraint (`g1-integrate` c2).

And the deliverable gate's own specificity proof — the thing that shows the guard does not
over-fire — is **vacuous by construction**.

So: a plan whose subject is "a check that cannot fail" (frame line 60, citing
`global-orchestrator.md §"A check that cannot fail"`) closes on four of them.

## Ranked findings

| # | Gate | Severity | Finding |
|---|------|----------|---------|
| 1 | `g2-implement` | **critical** | Specificity proof is vacuous by construction |
| 2 | `g2-integrate` c2 | **critical** | `\| tail -5` makes the check unable to fail |
| 3 | `g4-integrate` c2 | **critical** | `test -d .agent-work/567-d1` passed before the run began |
| 4 | `g2-implement` | **high** | Guard pattern unspecified exactly where discrimination is hardest |
| 5 | `g1-integrate` c2 | **high** | Check greps `skills/workbench/**`, which the plan forbids touching |
| 6 | all | **high** | Three declared evidence surfaces have no postcondition |
| 7 | `g1`/`g2` order | **medium** | Guard-after-sweep throws away a free, real red-proof |
| 8 | `g3` | **medium** | Adds new door prose in `specs/`, outside the guard's walk |
| 9 | `g3-integrate` c2 | **medium** | Passes on one file of two, and on the bare word "door" |
| 10 | whole plan | **medium** | Nothing makes the guard harder to delete than the test it replaces |
| 11 | `g4`, anchors | **low** | Unrelated scope; anchor blocks duplicated nine times |
| 12 | line 4 | **low** | `config_ref` points at a file the frame says does not exist |

---

## Lens 1 — intent-fit

### F10. The plan does not close "the text must not grow back". It closes "the text is gone and one test says so."

The frame's own history is the argument against the plan. The text was deleted twice and regrew
twice, and the frame establishes *why*: a test mandated it
(`test_field_still_carries_cli_fallback`, "the CLI door must stay, never be removed or
discouraged"). The regrowth vector was **a test that contradicted an agent's instructions**, and
the resolution was that the text won.

`g1-implement` now does the mirror-image move: it finds a test that contradicts the new intent and
rewrites it. That is correct here — but it is also a live demonstration, inside this plan, of the
exact operation that would defeat the new guard. Nothing in the plan makes the new guard more
durable than the old test was. The entire defense is prose: the guard must "carry a failure
message that tells a future agent WHY the text must not come back and where the ruling lives"
(`g2-implement`).

Which raises the concrete version of this finding: **where does the ruling live?** The plan
forbids the only durable home. `g4-implement` constraints: *"Do not promote any observation into
docs/agents/* -- that is the human's call"*. The frame's Out of Scope: *"Filing any issue — ruled
none; candidates staged as files"*. So the failure message can point at: issue #559 (closed by this
very run), or `.agent-work/567-d1/` (a scratch directory that does not survive the epic). A future
agent that trips the guard will follow the pointer and find nothing.

This may be unfixable inside the lane's constraints — that is a legitimate answer. But it should be
*stated*, not left implied. Two cheap options: (a) surface to the human at plan approval that the
ruling needs a durable home in `docs/agents/ORCHESTRATOR_CONTEXT.md` and that the lane is currently
forbidden to put it there; (b) have the guard's failure message quote the ruling in full rather
than cite a location, so the guard is self-contained and deleting it destroys the reason too.

### F8. `g3` adds new, unguarded door text — in the lane whose thesis is that this text regrows.

`g3-implement` gives `specs/implementer.spine.toml` and `specs/reviewer.spine.toml` door
vocabulary. Both carry "ZERO door mentions today". The guard's scope is
`INSTRUCTION_FILES` = rglob over `skills/` for `.md`/`.json` (BRIEF_COMMON line 18). **`specs/`
is not in that walk, and `.toml` is not in those extensions.** So `g3` creates a fresh surface of
door/CLI doctrine that (i) did not exist before this run, (ii) is the exact category of text this
epic is trying to control, and (iii) is invisible to the guard the same run just built.

Either bring `specs/` into the guard's walk, or drop `g3`. Doing neither is the worst option.

### What is sound (stated, per the brief)

- **The g1 pairing is correct.** *"TWO HALVES OF ONE GATE, because doing either alone leaves the
  suite red."* Splitting the sweep from the mandate-inversion would force one side to be undone.
  This is the plan's best reasoning.
- **Reusing `INSTRUCTION_FILES` instead of inventing a scope is the right answer to the named
  decay mode.** `decision:guard-scope-is-the-existing-corpus-walk` is graded `settled/measured`
  with the measurement stated (10 targets IN, both pre-ruled survivors OUT, exception list length
  ZERO). Expressing scope as a *rule the walk applies* rather than a list is precisely the fix for
  the 11-entry exception list.
- **Demanding a specificity proof at all is above average.** Most guard plans prove only
  sensitivity. That the plan asks "does it fire on a legitimate mention?" is right — the execution
  of that proof is F1 below, but the instinct is correct.
- **The frame is honest about DEGRADED orientation** and does not launder five hash-pinned
  substitutes into "a map".

---

## Lens 2 — testability

### F1. `g2-implement`'s specificity proof cannot fail. CRITICAL.

Exact string:

> *"Also prove it does NOT fire on a legitimate historical mention -- add a real `<engine>` mention
> under `docs/superpowers/` or `episodes/` in the scratch state and show the guard stays green."*

The guard's scope is an rglob over **`skills/`** (`decision:guard-scope-is-the-existing-corpus-walk`;
BRIEF_COMMON line 18). `docs/superpowers/` and `episodes/` are not under `skills/`. The guard
**structurally cannot read those directories**. The proof therefore succeeds no matter what the
guard's pattern is — it would succeed against a guard that fires on the empty string, against a
guard with a broken regex, against a guard that does nothing at all.

What world does it report clean in? *Every* world. It is a test of the scope rule the plan already
measured, dressed as a test of the pattern.

The real specificity risk is inside `skills/`, and the plan names it itself —

### F4. The guard must discriminate two near-identical strings in the same three files, and the plan neither specifies the pattern nor tests the discrimination. HIGH.

`g1-implement` rewords the 3 second-checklist clauses so that they *positively assert the CLI*:

> *"reword to state that measured truth -- the CLI is the ONLY path for a second checklist because
> the door refuses to rebind while the agent holds its own lease"*

And `decision:second-checklist-clauses-are-reworded-not-deleted` states the requirement outright:

> *"the g2 red-proof must still catch a genuine reintroduction at these same sites"*

So in `skills/interrogator/SKILL.md` and both `write-a-skill` templates, the guard must pass on
"the CLI is the only path…" and fail on "CLI fallback: …". That is the hardest call the guard has
to make, at three known sites, and `g2-implement` specifies the pattern only as *"the 'CLI
fallback' clause pattern"* — undefined. If the pattern is the literal string, regrowth spelled
"CLI fall-back", "fall back to the CLI", or "command-line fallback" walks straight through. If the
pattern is broader, it red-lights the three sites `g1` just authored.

Fix: pin the pattern in the plan, and replace the F1 proof with the proof that matters — reintroduce
a fallback clause **at one of those three reworded sites**, show RED; confirm the reworded text
itself stays GREEN. That is a proof only a correct pattern passes.

### F2. `g2-integrate` c2 cannot fail. CRITICAL.

Exact command:

```
python3 -m pytest tests/test_retirement_guard.py tests/test_mcp_adoption.py -q 2>&1 | tail -5
```

A pipeline's exit status is the exit status of its **last** command. `pipefail` is not set. `tail`
exits 0 whenever it can read its input — which is always. Worlds this reports clean in:

- the guard **fails** (pytest exit 1) — tail exits 0, gate closes;
- `tests/test_retirement_guard.py` **does not exist** (pytest exit 4, "file or directory not
  found") — tail exits 0, gate closes;
- collection errors, import errors, syntax errors in the guard — all exit 0 through `tail`;
- `python3` not on PATH — tail reads empty input, exits 0.

The middle case is not hypothetical: `g2-implement` explicitly leaves the filename open — *"Decide
and state whether the guard belongs in `tests/test_retirement_guard.py` or its own module."* The
plan invites the implementer to choose a name, then hard-codes the other name in the check that is
supposed to catch them. The most likely real-world outcome is a guard in a new module, a
`file or directory not found`, and a green gate.

Fix: drop `| tail -5`, or prefix `set -o pipefail;`. And close the filename hole — either the plan
names the file, or the check discovers it. Pytest's `-q` output is on stdout for the human; the
gate should read the exit code.

Note also what this check does **not** assert even when repaired: it says nothing about the guard's
**count**. `g2-implement` requires the guard to *"state the COUNT of files it looped over so it
cannot pass vacuously on an empty set"*, and no postcondition anywhere verifies that a count was
printed, let alone that it clears the ≥60 floor (BRIEF_COMMON line 19). A guard that walks zero
files, prints nothing, and passes satisfies every check in this plan.

### F3. `g4-integrate` c2 cannot fail. CRITICAL.

Exact command:

```
test -d .agent-work/567-d1
```

That directory already exists. It held `MISSION_FRAME.md`, `notes-1.md`, `map-orientation.json`,
and `execute.json` itself before `e0-context` ran. This check passed before the run started, passes
if `g4` does nothing, passes if `g4` does the wrong thing, and passes if the implementer crashes on
its first tool call. It is a placeholder, not a postcondition.

`g4`'s own claim is *"each of #596 and #526 has a disposition backed by a grep, not by an
opinion"*, with required evidence *"the grep output that establishes each disposition, including a
negative one"*. A falsifiable check would test for those artifacts existing and non-empty, or
re-run the reconciliation grep for `CONSTELLATION_FEEDBACK` over the owned files. If no falsifiable
postcondition can be written for `g4` — see F11: that is evidence `g4` should not be a gate.

### F5. `g1-integrate` c2 is scoped wrong and its outcome depends on unstated cross-lane state. HIGH.

Exact command:

```
test -z "$(grep -rn -i 'CLI fallback' skills/ || true)" && test -z "$(grep -rn '<engine>' skills/ || true)"
```

This greps **all** of `skills/`. The gate it closes is forbidden from touching part of it:
`g1-implement` constraint — *"Do NOT touch `skills/workbench/**` … other lanes own them"* — and
the frame's Out of Scope says lane D2 *"deletes those files, including 2 of the 15 clauses"*.

The arithmetic: 13 clauses in D1's files + 2 in workbench = 15 in `skills/`. If D2's deletion is
not yet in this tree, the check finds 2 and **fails**, and the only way to close the gate is to
violate the constraint. If D2's deletion *is* in the tree, it passes — but then the gate's outcome
silently depends on a merge the plan never verifies. The frame says D1 *"merges last"* and to
*"Expect a rebase before the final gate"*, so which world obtains at `g1-integrate` time is
genuinely undetermined by the plan.

Either way it is a defect: a check whose result is governed by another lane's state, written as if
that dependency did not exist. Fix: scope the grep to what this lane owns
(`--exclude-dir=workbench`), and make the workbench dependency an explicit precondition rather than
a hidden one.

Lesser point on the same command: `-i 'CLI fallback'` pins one spelling. As the Commander's
spot-check that is tolerable — the guard is what has to be robust — but see F4.

### F9. `g3-integrate` c2 is near-vacuous. MEDIUM.

Exact command:

```
test -n "$(grep -rn -i 'door' specs/ || true)"
```

Passes if the substring "door" appears **anywhere** in **any** file under `specs/`, in any case,
in any context. Worlds it reports clean in:

- the implementer edits `implementer.spine.toml` and never opens `reviewer.spine.toml` — the gate's
  own anchor says *both* carry zero door mentions today and both need vocabulary;
- a spec says only "the door is not available to this role" — the opposite of the intent;
- someone writes the word in a comment, or in "doorway", or in a `# TODO: door`.

It also cannot see the actual claim it is meant to close: *"specs/*.spine.toml name the door as the
path for a role whose own spine is bound, **and name the CLI as the only path for a second
checklist**"*. The check tests half a word of a two-part claim.

Minimum fix: assert both files independently (`grep -qi door specs/implementer.spine.toml && grep
-qi door specs/reviewer.spine.toml`) and assert the second clause too. Better fix: see F11.

### F6. Three declared evidence surfaces have no postcondition at all. HIGH.

The frame and the anchors declare evidence that no gate checks:

1. **Full suite green.** Frame line 87: *"full suite on Linux in a clean detached worktree of the
   branch, `^FAILED` grep pasted, only `MapTreeFreshnessTests` permitted to fail."* The same item
   is repeated in `g1`'s anchors (`"the full suite green except
   tests/test_code_map.py::MapTreeFreshnessTests"`, three times). **No `command` check in the plan
   runs the full suite.** `g1-integrate` runs two greps; `g2-integrate` runs two test files. A
   sweep across 10 instruction files plus a regenerated `store_mentions.approved.txt` can break
   tests neither of those touches.
2. **The guard's count.** Required by prose in `g2-implement` and in the constraint block; checked
   nowhere. See F2.
3. **Post-rebase re-run.** The frame anticipates a rebase before the final gate because lane E
   changes the door's own refusal text. The last gate in the plan is `g4-integrate`, whose check is
   `test -d`. **The plan ends without ever re-running the guard against the merged tree.** The
   guard's scope includes `skills/workbench/**`, which another lane is deleting; the guard's
   correctness is coupled to that landing, and nothing re-verifies it after the merge.

Add a final postcondition that runs the guard and the full suite on the rebased tree, with the
`^FAILED` grep and the `MapTreeFreshnessTests` exemption expressed *in the command*, not in prose.

### Preconditions are unenforced (SPECULATIVE)

Every `preconditions` entry in the file has `"check": null` and `"satisfied": false` — e.g.
`g2-implement` p1 *"g1-integrate closed: the corpus is swept and the suite is green"*. I have not
read the engine, so it may enforce ordering structurally from `items`. If it does not, these are
prose, and `p1` on `g2` in particular is doing real work (the guard's red-proof assumes a clean
corpus).

---

## Lens 3 — simplicity / YAGNI

### F11. `g4` is a different issue. Three items, 23% of the plan.

#596 (CONSTELLATION_FEEDBACK mandates vs the episode ledger) and #526 (stale close criteria,
survey-reuse convention) have no relationship to "the CLI is not a second path" or to the guard.
The frame's Intent (lines 3–8) is entirely about the CLI text and the mechanism that makes the
third deletion stick. The plan itself suspects half of `g4` is already dead —
`decision:526-may-be-stale`: *"the Admiral grepped `skills/commander/` for the build script #526
names and found NO match."*

`g4` costs a full implement/review/integrate triad, three copies of an anchors block, and it is the
gate that ended up with `test -d` as its postcondition — which is what happens when a gate has no
crisp world-facing outcome to assert.

I have not read the launch order, so this may be welded into D1 and not droppable unilaterally.
**Then surface it at plan approval as the question it is**: does #559's guard have to wait behind
two unrelated dispositions, one of which is probably stale? If yes, `g4` needs a real postcondition.
If no, dispose #526 as a one-line evidenced "does not reproduce" outside the gate structure.

`g3` is the same shape at lower cost: three items for prose edits to two TOML files (its own
decision says *"prose not new keys"*). Fold it into `g1` or drop it — and if it stays, F8 applies.

### F7. Reorder: author the guard **first**, and the red-proof becomes free and real. MEDIUM.

Today: `g1` sweeps → `g2` writes the guard against an already-clean tree, then manufactures a red
state on scratch, captures RED, reverts, captures GREEN, and confirms a clean tree.

That red-proof is synthetic. The same agent writes the pattern *and* chooses the string to
reintroduce, so it will reintroduce exactly what its own regex matches. That is the weakest form of
this proof.

Invert the order and the proof is handed to you by the world:

- **new g1** — author the guard against the *dirty* tree. It must go RED, naming **13 clause sites
  and 9 token sites in 10 real files**. Close criterion: guard exists and fails with that census.
  A guard whose pattern is wrong cannot produce that census; a guard that walks zero files cannot
  either. This is a sensitivity proof against real text at real sites, not a sample of one.
- **new g2** — sweep + invert the mandate. The guard goes GREEN as a *consequence* of the work.

What this deletes: the entire scratch-state dance, the *"Revert every scratch edit and confirm a
clean tree"* constraint, and the risk of a guard tuned to its own synthetic sample. It also does
the specificity proof properly, because the three reworded clauses (F4) land in the sweep gate with
the guard already live and watching them.

One thing to handle: while both `test_field_still_carries_cli_fallback` and the new guard exist,
they directly contradict each other — one mandates the string, the other forbids it. That is
*correct and informative* for the duration of one gate, but the plan must not leave both live
across a merge boundary. Make the mandate-inversion and the sweep the same gate, as it already
does.

### F12. The plan is an instance of the defect it is fixing.

Each gate's `anchors` block — `structural`, `constraint`, `decision`, `claim`, `evidence` — is
duplicated **byte-identically across all three items of its triad**. `g1-implement`,
`g1-review`, `g1-integrate` carry the same five arrays; same for `g2`, `g3`, `g4`. That is nine
redundant copies of instruction text that must now be hand-synchronised, in a plan whose entire
thesis is that duplicated instruction text drifts and regrows. Edit one copy of
`decision:second-checklist-clauses-are-reworded-not-deleted` and eleven other places silently
disagree.

The four `review` imperatives are also byte-identical, and the boilerplate is **false at two of
them**: *"The reviewer must independently re-run this gate's verification command and confirm the
count it reports"* — `g3` and `g4` report no count. Copy-paste that has stopped being true is
exactly the decay the guard is for.

If the schema permits a triad-level or plan-level anchors block, use it. If not, trim the
review/integrate copies to a reference to the implement item.

### F13. `config_ref` dangles. LOW, but odd.

`execute.json` line 4: `"config_ref": "docs/agents/engine-config.json"`.

The frame (lines 42–45) flags this exact path as a defect in `specs/implementer.spine.toml` and
`specs/reviewer.spine.toml` — *"`config_ref` points at `docs/agents/engine-config.json`, which
**does not exist in this repo**"* — and `g3-implement` asks the implementer to *"record (do not
necessarily fix)"* it. The plan noticed the dangling reference in two files it barely depends on
and reproduced it verbatim in the file that drives the entire run. Whether the engine tolerates
this is unknown to me (SPECULATIVE — I have not read the engine). If it does not, everything
downstream is unverified.

---

## The single change I would make if only one were allowed

Delete `| tail -5` from `g2-integrate` c2 and pin the guard's filename in the plan. Right now the
gate that delivers #559 closes green when the guard does not exist.

## The second

Replace `g2-implement`'s specificity proof. Proving the guard ignores `docs/superpowers/` proves
the rglob is an rglob. Prove instead that it fires on a reintroduced `CLI fallback:` clause at one
of the three sites `g1` reworded, and stays green on the reworded text itself. That is the only
proof in this plan that a wrong pattern would fail.
