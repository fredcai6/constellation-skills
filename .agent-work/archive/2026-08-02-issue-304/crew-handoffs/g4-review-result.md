# Review Result — issue-304 gate g4

## Assigned Gate
`g4 — dogfood the edited Commander spine end to end in this repo (degraded common case), then run the full suite`

## Result
`APPROVE`

Survey driven end to end through the engine: `.agent-work/issue-304/g4-review/review.json`
(13 items, all visited, consolidated `verdict=APPROVE findings=0`). Fowler pass:
`.agent-work/issue-304/g4-review/FOWLER_PASS.json`, rail exit 0.

---

# THE QUESTION THE HANDOFF EXISTS TO ASK: **CAN THIS CHECK FAIL?**

## Answer: YES — by execution, two mutations, both of my own devising

Neither is among the **ten** in `tests/test_mutation_floor.py` (all ten target `map_orient.py`
**internals**) nor among the **four** g3's reviewer aimed at the template (all four target its
**prose**). Mine are the first to attack the **wiring** — the seam the handoff named as g4's hazard.

Harness discipline borrowed from the floor's own doctrine: **every mutation asserts it APPLIED.**
My first R-B attempt refused loudly at 0 anchor matches (CRLF) rather than silently under-applying —
a non-applied mutation must never masquerade as a killed mutant.

### MUTATION R-A — point the check at a subcommand that does not exist

Run against a **fully discharged** receipt, i.e. a state where the real check exits 0 and the gate
*should* pass. This isolates the wiring to exactly one bit.

```
MUTATION R-A APPLIED
  before: python scripts/map_orient.py verify-orientation --root C:/Programs/constellation-skills-wt/e298-304 --work-id g4rev-mutA
  after : python scripts/map_orient.py verify-orientaton  --root C:/Programs/constellation-skills-wt/e298-304 --work-id g4rev-mutA

=== the mutated command run by hand ===
map_orient.py: error: argument command: invalid choice: 'verify-orientaton' (choose from orient, verify-orientation, verify-frame)
### mutated-command exit: 2

=== engine advance under MUTATION R-A (receipt fully discharged) ===
### engine advance exit: 1
REFUSED: context: postconditions unmet ['c2'] Recovery: fix the underlying issue so postcondition c2 passes, then retry advance context. Do not edit the JSON — use the engine.
```

**Control — revert ONLY that one token, same spine, same receipt, nothing else touched:**

```
MUTATION R-A REVERTED (wiring is the ONLY thing changed; receipt untouched)
=== engine advance with the SAME receipt, wiring restored ===
### engine advance exit: 0
context -> complete
```

**Identical state. One bit of wiring. Opposite outcome.** The engine really runs the command; the
gate is not decorative.

### MUTATION R-B — neuter `verify-orientation`'s refusal itself

The sharper direction, and the one that directly answers "would the demonstration have looked the
same if the contract did nothing?" Fresh scratch, **no receipt at all**.

```
=== BASELINE (unmutated tool, no receipt) ===
### engine advance exit: 1
REFUSED: context: postconditions unmet ['c2'] ...
```

```
  applied 2x: return EXIT_RECEIPT_UNUSABLE -> return EXIT_OK  # MUTANT
  applied 1x: return _gate(args, code)     -> return EXIT_OK  # MUTANT
MUTATION R-B APPLIED: cmd_verify_orientation refuses nothing -- every path returns EXIT_OK

=== the neutered tool by hand, NO receipt ===
### neutered check exit: 0
no receipt at C:/Programs/.../g4rev-mutB/map-orientation.json -- run `orient` first
RECEIPT-MISSING

=== engine advance under MUTATION R-B, still NO receipt on disk ===
ls: cannot access '.agent-work/g4rev-mutB/map-orientation.json': No such file or directory
### engine advance exit: 0
context -> complete
```

**Under a contract that does nothing, the spine sails straight through to `context -> complete`
with no receipt in existence.** That is exactly what the g4 demonstration did **not** do. The exit
code of `verify-orientation` is precisely and solely what gates the step.

R-B is **additionally killed by the shipped suite**: `31 failed, 174 passed` across
`test_map_orient.py test_mutation_floor.py test_spine_provenance_check.py test_spine_rail.py`,
including `MutationFloor::test_0_unmutated_baseline_is_green`.

**Product code restored and proven restored:**

```
restored
worktree OID: dbac7795c6a391bb1d1f7787d5a05565be3c2b5f
HEAD OID:     dbac7795c6a391bb1d1f7787d5a05565be3c2b5f
baseline was: dbac7795c6a391bb1d1f7787d5a05565be3c2b5f
--- git diff --quiet HEAD -- scripts/map_orient.py --- exit 0 (identical)
--- MUTANT marker gone? --- 0 occurrences
```
```
101 passed, 50 subtests passed in 151.83s (0:02:31)   ### exit: 0
```

**Verdict on the hazard: the demonstration is NOT one that would have looked identical if the
contract did nothing. Not a BLOCK.**

---

## Handoff compliance

**PASS.** All three claims re-run in my own scratch work-id `g4rev-scratch`, never read from the report.

### Claim 1 — it reports rather than silently passing: exit path 12 → 10 → 10 → 0

**Stage A (no receipt):**
```
--- receipt present? ---
ls: cannot access '.agent-work/g4rev-scratch/map-orientation.json': No such file or directory
=== STAGE A: advance context with NO receipt ===
### engine advance exit: 1
REFUSED: context: postconditions unmet ['c2'] ...
=== STAGE A: the check itself, exit captured before any pipe ===
### check exit: 12
no receipt at C:/Programs/constellation-skills-wt/e298-304/.agent-work/g4rev-scratch/map-orientation.json -- run `orient` first
RECEIPT-MISSING
```

**Stage B — THE MIDDLE STAGE the handoff flags as carrying the new information: receipt PRESENT but
UNDISCHARGED, and the gate still refuses.**
```
=== STAGE B step 1: bare orient (creates an UNDISCHARGED receipt) ===
### orient exit: 10
DEGRADED-NO-MAP
root: C:/Programs/constellation-skills-wt/e298-304
root proof: positive: .git entry present at root
entrypoint: (none)
anchor_count: 0
candidates tried:
  [1] generated-map: docs/architecture/generated/map.json -> absent (absent)
  [2] index: docs/architecture/index.md -> absent (absent)
  [3] packets-dir: docs/architecture -> absent (absent)
receipt: .agent-work/g4rev-scratch/map-orientation.json
degraded and NOT discharged -- still owed:
  - substitutes (what you read INSTEAD of a map, each hash-pinned)
  -     substitutes is empty -- a degraded run read SOMETHING instead of the map
  - unmapped (what stayed unmapped, stated plainly)
  - escalation (what you are escalating, and to whom)

=== STAGE B step 2: receipt IS on disk now ===
-rw-r--r-- 1 fredc 197609 1534 Aug  1 22:01 .agent-work/g4rev-scratch/map-orientation.json

=== STAGE B step 3: engine advance with the receipt PRESENT ===
### engine advance exit: 1
REFUSED: context: postconditions unmet ['c2'] ...

=== STAGE B step 4: the check itself, exit before any pipe ===
### check exit: 10
DEGRADED-NO-MAP
receipt: .agent-work/g4rev-scratch/map-orientation.json
degraded record INCOMPLETE -- substitutes AND unmapped AND escalation
problems: 4
  - substitutes (what you read INSTEAD of a map, each hash-pinned)
  -     substitutes is empty -- a degraded run read SOMETHING instead of the map
  - unmapped (what stayed unmapped, stated plainly)
  - escalation (what you are escalating, and to whom)
```
A bare DEGRADED verdict does **not** satisfy the gate. All three absent map candidates are
enumerated by path; all four owed items are named individually.

**Stage C (discharged):**
```
### orient exit: 0
### check exit: 0
DEGRADED-NO-MAP
orientation contract SATISFIED
problems: 0
substitute: README.md [known-fallback] -- found in the fixed fallback set and present on disk
substitute: docs/agents/ORCHESTRATOR_CONTEXT.md [agent-declared] -- UNVERIFIED -- declared by the agent, not corroborated by the filesystem
=== STAGE C step 3: engine advance ===
### engine advance exit: 0
context -> complete
```

**12 → 10 → 10 → 0 reproduced exactly.**

### Claim 2 — no deadlock, no `--force`, no waiver. Journal checked myself:

```
=== MY scratch spine journal verbs ===
raw entries: 6
verb sequence: ['start', 'attest', 'advance', 'start', 'attest', 'advance']
distinct sorted: ['advance', 'attest', 'start']
waive present: False
force present: False
```
Discharged in **one** `orient` command with three flags. The gate is dischargeable **honestly**, not
merely bypassable.

### Claim 3 — placeholders resolved. My own independent sweep:

```
resolver-family survivors: 0 []
c2 command: python scripts/map_orient.py verify-orientation --root C:/Programs/constellation-skills-wt/e298-304 --work-id g4rev-scratch
other angle-bracket tokens: ['<date>', '<engine>', '<file>', '<path>', '<spine-template>', '<what you checked>']
--- all command checks ---
  init.c1:      python scripts/init_work_area.py g4rev-scratch
  context.c2:   python scripts/map_orient.py verify-orientation --root C:/... --work-id g4rev-scratch
  plan.c6:      python scripts/map_orient.py verify-frame --root C:/... --work-id g4rev-scratch
  execute.p2:   python scripts/verify_state_note.py g4rev-scratch
  feedback.c1:  python scripts/verify_agent_feedback.py g4rev-scratch --phase feedback
  feedback.c2:  python scripts/verify_lessons_applied.py --file .agent-work/LESSONS.md
  archive.c1:   python scripts/verify_agent_feedback.py g4rev-scratch --phase archive
```
**Zero resolver-family tokens survive in the materialized `spine.json`.** The six remaining
angle-bracket tokens are prose slots the resolver does not own and no check consumes.

**The relative-`scripts` caveat is a documented branch, not a resolution failure wearing a plausible
explanation.** `init_work_area.py:80-92`, `_resolve_skill_dir_token`'s own docstring:

> *"When omitted, auto-detect the source-repo layout (bundled scripts at `<root>/scripts`) and
> collapse the token form `<token>/scripts` -> `scripts` so the init command references the real
> top-level script path."*

`--root` did come out **absolute and existing**. Residual fragility is #341, out of scope, not re-filed.

## Scope drift

**PASS — none.** `git diff --stat 4f9c6d1..HEAD -- . ':(exclude).agent-work'` is **empty**. All 12
changed files are under `.agent-work/issue-304/`. `git diff --quiet HEAD -- . ':(exclude).agent-work'`
exits **0**: the product tree is identical to HEAD, before and after my review.

Exclusions honored: g1/g2/g3 not re-opened; #341/#342/#344/#363/#364 not fixed; no bootstrap or
`CLAUDE.md` stanza; `TRIPWIRES.md` not rewritten. Every occurrence of `f1Brainz`,
`C:/Programs/constellation-skills` or `e298-331` in the diff is **prose stating the constraint** —
no command was ever run against them, by g4 or by me.

### Cleanup claims — re-verified independently by blob OID (never `git status`)

```
.agent-work/issue-304/TRIPWIRE_OUTCOMES.md                 3ccd8b547fbb  UNCHANGED
.agent-work/issue-304/TREND_SNAPSHOT.md                    ad2ee8361bcc  UNCHANGED
.agent-work/issue-304/crew-handoffs/g3-result.md           6597f5c8d2fa  UNCHANGED
.agent-work/issue-304/evidence/g3-run-transcript.txt       11254624da14  UNCHANGED
.agent-work/issue-304/g3-implementer-plan.json             71875372f39f  UNCHANGED
.agent-work/issue-304/spine.json                           183930008cf1  UNCHANGED
TRIPWIRES.md                                               eab67aca3cc9  UNCHANGED
=== TRIPWIRES.md vs pre-registration 1662b90 ===
1662b90: eab67aca3cc947fed3ed489cba059e52c05f46ac
worktree:eab67aca3cc947fed3ed489cba059e52c05f46ac
=== implementer scratch removed? ===
ls: cannot access '.agent-work/g4-scratch-run': No such file or directory
```
Every OID matches the implementer's reported prefix. **The removal claimed did happen.**

## Evidence verdict

**PASS.** Required evidence present, reproducible, and it demonstrates the behavior — I reproduced
all of it. See the mutation section above for the load-bearing part.

**Full suite, my own run:**
```
1538 passed, 2 skipped, 481 subtests passed in 224.18s (0:03:44)
### exit code 0
```
Counts identical to the claim (1538/2/481). It did not hang. Local interpreter
`3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]`; CI pins `3.12`.
**No 3.13+-only API in any of the three evidence scripts** — nothing to BLOCK on. `python -m pytest`
throughout; zero occurrences of `py -m pytest` anywhere in `.agent-work/issue-304/`.

### Deviations judged

1. **`a90262e` swept in the Commander's in-flight engine state — BENIGN and purely ADDITIVE.**
   `execute.json` gained only `satisfied: false -> true`, a `satisfied_by` string, and
   `pending -> in-progress`. The journal gained exactly two entries (seq 42 `attest`, 43 `start`,
   both `g4-implement`). I verified the whole chain:
   ```
   execute.json.journal entries: 47
   hash-chain breaks: NONE -- chain intact end to end
   session_ids present: ['None', 'commander-304-e298']
   ```
   Every non-null `session_id` is the Commander's; **no crew session ever wrote to that journal**
   (the `None` ids are pre-lease entries seq 1–15). **Nothing altered, nothing lost.** The
   implementer's judgment not to un-commit live state mid-run was the right one. *Commander: your
   state is in `a90262e` — note it.*
2. **Suite run twice** — justified; the engine discards stdout, so a single engine-run leaves no
   verbatim line and a single hand-run leaves the gate unproven. Accepted.
3. **Mis-scoped exit codes in the first transcript block — handled honestly, and every quoted code
   is from the corrected runs.** The `NOTE ON EXIT CODES` block sits at the boundary
   (`g4-run-transcript.txt:65-68`), stage A is re-run below it with codes captured before any pipe,
   and the uncorrected lines are left visible rather than edited out. **Independent check:** the exit
   codes quoted in `g4-result.md` for the gate stages are `1, 12, 10, 1, 10, 0, 0, 0` — which is
   *exactly* what my own reproduction produced, line for line. Leaving the bad lines in place was
   the honest choice and it cost nothing.

### The stated scope gap — stated, not papered over

**Confirmed.** `g4-result.md` Map Impact / Trust limitations says plainly that g4 covers the
**degraded arm only**, that the `RESOLVED` arm is untested here, and that **T3's mapped-repo clause
remains unfalsified AND unconfirmed**. I re-confirmed the premise by command: all three map
candidates absent, `docs/agents/` contains `ORCHESTRATOR_CONTEXT.md` alone. This is a scoped null in
the doctrinal sense — a specific test not run, not a closed branch. The degraded demonstration does
not read as full coverage anywhere in the result.

### Overclaim scan

`grep -iE '\b(prevent|guarantee|ensure|always|never fails|fully covered|complete coverage)\b'` over
`g4-result.md` returns **nothing**. The ratified limitations (sensitivity 0/4, specificity 0/1,
regression-floor-not-fix, partly self-attested) are nowhere contradicted. **No overclaim to flag.**

## Code/doc quality

**PASS.** Fowler pass over the only code in the diff — the three evidence assertions — recorded at
`.agent-work/issue-304/g4-review/FOWLER_PASS.json`; rail exits 0:

```
fowler pass ok: smells=12, flagged=['shotgun-surgery', 'comments-as-deodorant'],
overridden=['long-method', 'duplicated-code', 'primitive-obsession']
```
Each override carries the specific standard that wins plus why it subordinates the smell (all three
reduce to `global-crew.md` "no speculative abstraction" over one-shot archived evidence). No
`rail_exception` was needed or self-granted.

## Map impact verdict

- **Evidence supports claimed change:** yes — I reproduced every claim independently, and the one
  genuine capability claim (the orientation contract is now exercised end to end through
  `init_work_area.py` → engine → command check, not only through unit tests) is precisely what my
  own dogfood demonstrates.
- **Constraints not violated:** yes — product tree byte-identical to HEAD; all six inherited
  constraints verified by command as their own survey checks.
- **Notes match the diff:** yes — "zero structural anchors touched" is literally true; nothing
  overstated.
- **Decision candidates surfaced:** yes — both findings reported and deliberately not fixed, with the
  scope reason given. Correct call.
- **Durable context routed:** yes — two triage candidates from the implementer, plus one of mine.

## Reconciliation check

**PASS.** No divergence from recorded architecture, because there is none to diverge from — and that
absence is now on the record *inside a receipt* as a named escalation for the first time, which is
the reconciliation-relevant fact. Confirmed by command, not by reading.

---

## Blockers

**NONE.**

## Findings by severity

### MAJOR (defect — not a blocker for g4)

**F1. A present, hash-pinned substitute is reported as "not corroborated by the filesystem."**
*The handoff asked specifically for a severity on this one. Here it is, with reasoning.*

Reproduced verbatim in my own run:
```
substitute: docs/agents/ORCHESTRATOR_CONTEXT.md [agent-declared] -- UNVERIFIED -- declared by the agent, not corroborated by the filesystem
```
The file **is** present (1995 bytes, stat'd) and its contents **are** hash-pinned in the receipt:
```
{'path': 'docs/agents/ORCHESTRATOR_CONTEXT.md', 'content_hash': '2f79929ecb85851bd54ebf71145b2043547d6cdedc9eea9a91cb1c0786b1b496', 'source': 'agent-declared'}
ORCHESTRATOR_CONTEXT.md exists: True size: 1995
```
A sha256 can only be produced by **reading the file off the filesystem**. The sentence asserts the
opposite of what the receipt beside it proves. Source: `scripts/map_orient.py:963`.

**Why MAJOR.** This issue's headline deliverable is *honest reported degraded mode*, and
`render_verify_report` is that deliverable's **own output surface** — the one line a reader consults
to learn what a degraded run actually stood on. A degraded-mode report that misdescribes its own
evidence is a self-inflicted wound in the signature feature. It also teaches a wrong model: readers
learn "agent-declared means we could not confirm it exists," when the true meaning is **"not in the
fixed fallback set."** The downstream cost is real — a reader who believes the substitute may be
absent discounts a substitute that *was* read and pinned, which is exactly the evidence the degraded
arm exists to preserve.

**Why NOT a blocker.** (a) It errs in the **safe** direction: it understates verification, never
overstates it — and the dangerous direction is explicitly mutation-pinned (`every substitute reported
as known-fallback`, `the provenance line dropped from the report`). (b) No gate behavior changes; the
*classification* itself is correct, deliberate and right, since fixed-fallback-set membership is an
oracle the agent does not author. (c) g4 was scoped to **zero product-code changes**, so fixing it
here would have been the scope violation. Reporting-without-fixing was the correct call.

**One correction to the stated cost of fixing.** `g4-result.md` says it was left alone partly because
"three tests assert on these labels." That overstates it:
```
=== tests asserting the NOTE TEXT 'not corroborated' ===
  ZERO tests pin that sentence
=== the only pinned substring ===
tests/test_map_orient.py:1075:        self.assertIn("UNVERIFIED", proc.stdout)
```
The accurate rewording keeps `UNVERIFIED`. **The fix is one string literal with zero test churn** —
so this is a *cheap* must-fix to route before #304 closes, not a costly one to defer.

**F2. `g4_assert_discharged.py`'s degraded assertion is satisfied by the agent's own prose.**
*My finding — not reported by the implementer, not named in the handoff.*

The docstring promises the check asserts "the orientation receipt records a DEGRADED verdict." The
code is a whole-document substring scan, and the structured verdict is read one line earlier and then
**discarded**:
```python
verdict = receipt.get("verdict") or receipt.get("status") or ""     # fetched...
degraded = "DEGRADED" in json.dumps(receipt).upper()                # ...and never used
```
`escalation` is agent-authored free text, and the escalation actually passed at g4 contained the word:
*"...every Commander run in this repo is structurally **degraded** until a map exists."* Demonstrated:
```
verdict field says: RESOLVED
g4_assert_discharged.py's actual test -> 'DEGRADED' in json.dumps(receipt).upper(): True
Where the substring comes from:
  ... in this repo is structurally degraded until a map...
```
So the evidence line `receipt degraded: True` quoted in `g4-result.md` is produced by a substring
match on agent-authored prose, not by a verdict read. **This is the #300 failure class — an assertion
structurally unable to falsify the property it exists to falsify — appearing inside the evidence of
the gate that exists to hunt it.**

**Not a blocker:** the property is over-determined by stronger, independently-reproduced lines in the
same run (`orient` printed `DEGRADED-NO-MAP` at exit 10; `verify-orientation` printed
`DEGRADED-NO-MAP`; and the same script's `verify-orientation re-run exit: 0` is genuinely
load-bearing, which mutation R-B proves). **No conclusion in `g4-result.md` is wrong.** The script is
archived one-shot evidence, so there is nothing to fix in place — but the *pattern* belongs in
lessons.

### MINOR

**F3. `current` tells the agent to append a flag to "the command below," then prints no command.**
Confirmed two ways. **By execution** — `current` on the context step printed the c2 statement ending
`...append --report-only to the command below to turn this gate into a non-blocking report without
rewiring the step.` followed by `0/2 met` / `next: start context`. There is no command below. **At
source** — `checklist_engine.py:1431` is the sole open-condition renderer:
```python
lines.extend(f"  {c['id']} [unmet] {c['kind']} — {c['statement']}" for c in open_conds)
```
It emits id, kind and statement and **never** `check.command`. An agent obeying
`global-everyone.md` §"Engine output is the state channel" cannot act on that sentence without
opening `spine.json`, which the same doctrine calls a violation. MINOR rather than major because the
flip is an author-time affordance, not a runtime path — the gate is fully dischargeable without ever
reading that sentence, as my own run proves.

**F4. Shotgun surgery in the evidence scripts (observation).** The scratch work-id is hardcoded
independently in all three; a partial re-point would leave one script asserting against an absent
work area, where several checks degrade to trivially-satisfied rather than failing loudly. Cannot
actually be incurred — they are archived one-shots.

## Out-of-scope observations / triage candidates

Recorded in the survey as `tc1`, `tc2`, `tc3`:

- **tc1 (MAJOR, cheap):** reword `map_orient.py:963` — "not corroborated by the filesystem" →
  "not in the fixed fallback set." One string literal, zero test churn. Route before #304 closes.
- **tc2 (MINOR):** either render `check.command` in `current` or reword the c2 statement; owner is
  whoever owns the gate-vs-report flip.
- **tc3 (OBSERVATION):** the substring-scan-satisfied-by-own-prose pattern in
  `g4_assert_discharged.py` — the #300 failure class inside this gate's own evidence. Belongs in
  TRIPWIRES/lessons as a pattern, not as a code fix.

Not re-filed and explicitly out of scope per the handoff: #341, #342, #344, #363, #364, the
bootstrap/`CLAUDE.md` stanza (ruled OUT by the human).

## Known limitations — confirmed as stated, NOT novel finds

Measured sensitivity **0/4**, specificity **0/1**; ships as a **regression floor**, not the fix for
map-lateness; the degraded check is partly self-attested. All ratified, all consistent with what I
observed. The **mapped (`RESOLVED`) arm remains untested** — correctly stated in the result and not
papered over.

## Reviewer's own cleanup

Three scratch work areas created and removed (`g4rev-scratch`, `g4rev-mutA`, `g4rev-mutB`), confirmed
absent by `ls`. `scripts/map_orient.py` restored and proven by blob OID. Product tree byte-identical
to HEAD. `TRIPWIRES.md` untouched. The only worktree deltas are the Commander's own live engine
writes and my untracked survey directory `.agent-work/issue-304/g4-review/`.

## Workflow Feedback

- **Handoff gaps:** The handoff was unusually good — it named the hazard, the mechanism, and the
  falsification shape, which is why the mutations were cheap to design. One genuine gap: it told me
  to devise a mutation "not among the nine in `tests/test_mutation_floor.py`," but the file actually
  carries **ten** real mutations plus two harness self-tests (12 `name=` entries). I had to count
  them myself to be sure I wasn't duplicating one. A stale count in a handoff is the kind of thing a
  reviewer must verify anyway, but the off-by-one cost a check.
- **Context rediscovered:** Which mutations g3's reviewer had already aimed at the template. The
  handoff said "the four the g3 reviewer aimed at the template" without naming them, so I had to grep
  `g3-review-result.md` to confirm mine were distinct (M1–M4, all against the template's *prose*;
  mine are against the *wiring*, so no overlap). **Naming the four in one line would have saved that
  round-trip** — and it is the same information the handoff already had.
- **Instructions improvised around:** Two. (1) The reviewer skill says a `survey`'s `current` will
  not display a `refresh-request`; no trip fired, so this never bit, but I confirmed the caveat is
  accurate before relying on it. (2) More materially: doctrine forbids opening `spine.json` to read
  state, yet **both** of my mutations require *writing* the scratch spine's check-command text. I
  resolved it the same way the implementer did — the scratch spine is the **artifact under test**,
  not a state channel, and I never hand-edited a `satisfied` flag or a status; every state change
  went through the engine. The doctrine sentence still does not carve this out, and every future
  reviewer doing wiring mutation testing will hit the same seam.
- **What would have made this easier:** One concrete change — have the handoff **name the prior
  reviewers' mutations explicitly** (ids and one-line descriptions) rather than by count. Both the
  "nine" (actually ten) and "the four" cost me verification passes whose only output was "yes, mine
  are different." The Commander already holds that list.

## Return status
`complete`
