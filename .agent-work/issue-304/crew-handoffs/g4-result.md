# Implementation Result — issue-304 gate g4

## Assigned gate
`g4 — dogfood the edited spine end to end, then run the full suite`

## Return status
`complete`

**Headline:** the context gate fires **from the materialized template** in the degraded common case.
All three deciding questions answered by command, in this order: it **reported** (engine `REFUSED`
exit 1; check exit 12, then 10), it was **discharged without `--force` and without a waiver** (one
`orient` command with three flags, check exit 0, `context -> complete`), and the placeholders
**resolved** (zero resolver-family tokens survive; `--root` is a real absolute path). Full suite
green locally: **1538 passed, 2 skipped, 481 subtests passed in 202.12s**. Zero product-code changes in
m1–m4 — this gate was demonstration, exactly as scoped. Three deviations named below, one of them mine
to own. **§6 records a post-review slice `m5`**: after g4 was APPROVED, the Commander routed one of the
two reported findings as fix-now, so the final tree carries **one string literal** of product change.

## Completed slice

1. Materialized the **edited** `COMMANDER_SPINE.template.json` through `scripts/init_work_area.py`
   into scratch work-id `g4-scratch-run`, and proved every resolver-owned placeholder resolved.
2. Drove that materialized spine through the **engine** — `claim`, `init`, then `context` in three
   stages: no receipt, undischarged receipt, discharged receipt.
3. Ran the full suite to completion.
4. Removed the scratch work area and verified its absence; verified the prior gates' artifacts and
   `TRIPWIRES.md` unchanged by **blob OID**, not by `git status`.

**Evidence on disk:** `.agent-work/issue-304/evidence/g4-run-transcript.txt` (the engine's
and the tool's own output via `tee`), `.agent-work/issue-304/evidence/g4-full-suite.txt`, and **four**
executable assertions (`g4_assert_resolved.py`, `g4_assert_discharged.py`, `g4_assert_closeout.py`,
`g4_assert_harness_discriminates.py`) that are the plan's own command checks — the engine ran each of
them itself.

**Commits:**

```
40e7122 g4 m1(#304): materialize the EDITED spine, prove the placeholders resolved
a90262e g4 m2(#304): drive the MATERIALIZED spine through context - reported, then discharged
137beac g4 m3(#304): full suite green locally - 1538 passed, 2 skipped, 481 subtests
4e7a42c g4 m4(#304): IMPLEMENTER_RESULT - dogfood proven, cleanup verified, plan driven to done
        g4 m5(#304): post-review fix-now triage (see §6)
```

## Scope

**Files changed (m1–m4, the gate as reviewed):** evidence and plan artifacts only, all under
`.agent-work/issue-304/`. **No file under `skills/`, `scripts/`, `tests/` or `docs/` was touched.**
`git diff 4f9c6d1..4e7a42c --stat` outside `.agent-work/` is empty — the dogfood did **not** turn into
an edit, which is itself the result the handoff asked to be told about. **m5 adds exactly one line of
`scripts/map_orient.py`** (§6), on the Commander's post-review ruling.

**Specific exclusions touched:** none. g1/g2/g3 not re-opened; `TRIPWIRES.md` not rewritten (verified
by OID below); #341, #342, #344, #363, #364 not fixed; `checklist_engine.py` not modified; no
bootstrap/`CLAUDE.md` stanza; nothing pointed at `C:/Programs/f1Brainz`;
`C:/Programs/constellation-skills` and `…/e298-331` never touched.

## Behavior changed
`no`. This gate observed behavior; it did not create any.

---

# EVIDENCE

## 1. The placeholders resolved — the materialized check command, verbatim

The check that never ran is the check whose command still says `<repo-root>`. Against the spine
`init_work_area.py` actually wrote:

```
$ python scripts/init_work_area.py --spine skills/commander/templates/COMMANDER_SPINE.template.json --root C:/Programs/constellation-skills-wt/e298-304 g4-scratch-run
work area ready: C:\Programs\constellation-skills-wt\e298-304\.agent-work\g4-scratch-run
spine ready: C:\Programs\constellation-skills-wt\e298-304\.agent-work\g4-scratch-run\spine.json
### exit: 0

$ python .agent-work/issue-304/evidence/g4_assert_resolved.py
unresolved resolver-family placeholder tokens in the materialized spine: 0 []
materialized context.c2 command: python scripts/map_orient.py verify-orientation --root C:/Programs/constellation-skills-wt/e298-304 --work-id g4-scratch-run
--root value: C:/Programs/constellation-skills-wt/e298-304   absolute=True   exists=True
--work-id value: g4-scratch-run
other angle-bracket tokens (informational, not resolver-owned): ['<date>', '<engine>', '<file>', '<path>', '<spine-template>', '<what you checked>']
PLACEHOLDERS-RESOLVED
### exit: 0
```

The assertion sweeps the **whole file** for the resolver's own placeholder family
(`<work-id>`, `<repo-root>`, `<*-skill-dir>`, `<*-session-id>`, `<skill-dir>`) — not just the one
command — and finds **zero**. The six remaining angle-bracket tokens are prose slots inside
imperatives (`<date>`, `<what you checked>`); the resolver does not own them and they reach no check.

**One resolution worth stating plainly, because it is easy to misread as a failure.**
`<commander-skill-dir>/scripts` resolved to the **relative** `scripts`, not to an absolute path. That
is `init_work_area.py`'s documented auto-detect branch for a source repo that carries bundled scripts
at top level (`_resolve_skill_dir_token`: *"Bundled scripts live at the repo top level; skill-dir ==
repo root"*), and it is the branch a real Commander run in **this** repo takes. It is a **resolved**
placeholder, not a surviving one. Its fragility — a relative command check depends on the launcher's
cwd — is **#341**, which this gate is explicitly excluded from fixing. `--root` exists precisely
because of it, and `--root` **did** come out absolute.

## 2. It REPORTED — it did not silently pass

Three stages against the same materialized spine. Exit codes are the point: the engine discards the
check's stdout, so the exit code is the only signal that reaches the spine.

**Stage A — no orientation receipt at all:**

```
$ python <engine> --file .agent-work/g4-scratch-run/spine.json advance context --session-id commander-g4-scratch-run --why ...
REFUSED: context: postconditions unmet ['c2'] Recovery: fix the underlying issue so postcondition c2 passes, then retry advance context. Do not edit the JSON — use the engine.
### exit: 1

$ python scripts/map_orient.py verify-orientation --root C:/Programs/constellation-skills-wt/e298-304 --work-id g4-scratch-run
no receipt at C:/Programs/constellation-skills-wt/e298-304/.agent-work/g4-scratch-run/map-orientation.json -- run `orient` first
RECEIPT-MISSING
### exit: 12
```

**Stage B — a receipt exists but is NOT discharged.** This is the stage g3 did not isolate, and it is
the one that decides whether the gate is real: a bare DEGRADED verdict must not satisfy it.

```
$ python scripts/map_orient.py orient --root C:/Programs/constellation-skills-wt/e298-304 --work-id g4-scratch-run
DEGRADED-NO-MAP
root: C:/Programs/constellation-skills-wt/e298-304
root proof: positive: .git entry present at root
entrypoint: (none)
anchor_count: 0
candidates tried:
  [1] generated-map: docs/architecture/generated/map.json -> absent (absent)
  [2] index: docs/architecture/index.md -> absent (absent)
  [3] packets-dir: docs/architecture -> absent (absent)
receipt: .agent-work/g4-scratch-run/map-orientation.json
degraded and NOT discharged -- still owed:
  - substitutes (what you read INSTEAD of a map, each hash-pinned)
  -     substitutes is empty -- a degraded run read SOMETHING instead of the map
  - unmapped (what stayed unmapped, stated plainly)
  - escalation (what you are escalating, and to whom)
### exit: 10

$ python <engine> --file .agent-work/g4-scratch-run/spine.json advance context --session-id commander-g4-scratch-run --why ...
REFUSED: context: postconditions unmet ['c2'] ...
### exit: 1

$ python scripts/map_orient.py verify-orientation --root C:/Programs/constellation-skills-wt/e298-304 --work-id g4-scratch-run
DEGRADED-NO-MAP
receipt: .agent-work/g4-scratch-run/map-orientation.json
degraded record INCOMPLETE -- substitutes AND unmapped AND escalation
problems: 4
  - substitutes (what you read INSTEAD of a map, each hash-pinned)
  -     substitutes is empty -- a degraded run read SOMETHING instead of the map
  - unmapped (what stayed unmapped, stated plainly)
  - escalation (what you are escalating, and to whom)
### exit: 10
```

**The silent-pass failure mode is closed.** The degraded verdict is announced (`DEGRADED-NO-MAP`), the
three absent candidates are enumerated by path, and the four things still owed are named
individually. Exit 12 → 10 both refuse the gate; neither is a pass.

## 3. It did NOT deadlock — discharged in one command, no `--force`, no waiver

```
$ python scripts/map_orient.py orient --root C:/Programs/constellation-skills-wt/e298-304 --work-id g4-scratch-run \
    --substitute README.md --substitute docs/agents/ORCHESTRATOR_CONTEXT.md \
    --unmapped "skills/ and scripts/ have no structural map: this repo ships the Cartographer that builds docs/architecture/ and carries none itself, so the commander orientation contract has no map input for the role-template and orientation-tooling area this gate touches" \
    --escalation "standing docs/architecture/ gap in constellation-skills, escalated to the issue-304 Commander and the epic-298 Admiral -- every Commander run in this repo is structurally degraded until a map exists"
DEGRADED-NO-MAP
...
receipt: .agent-work/g4-scratch-run/map-orientation.json
### exit: 0

$ python scripts/map_orient.py verify-orientation --root C:/Programs/constellation-skills-wt/e298-304 --work-id g4-scratch-run
DEGRADED-NO-MAP
receipt: .agent-work/g4-scratch-run/map-orientation.json
orientation contract SATISFIED
problems: 0
substitute: README.md [known-fallback] -- found in the fixed fallback set and present on disk
substitute: docs/agents/ORCHESTRATOR_CONTEXT.md [agent-declared] -- UNVERIFIED -- declared by the agent, not corroborated by the filesystem
### exit: 0

$ python <engine> --file .agent-work/g4-scratch-run/spine.json advance context --session-id commander-g4-scratch-run --why ...
context -> complete
### exit: 0
```

**Exit 12 → 10 → 10 → 0, and the step advanced.** The escalation is a real one, not a formality: this
repo ships the Cartographer and carries no `docs/architecture/`, so it is written into the receipt as
the gap it is. And the assertion the engine itself ran as m2's gate:

```
$ python .agent-work/issue-304/evidence/g4_assert_discharged.py
context task status: complete
receipt degraded: True   substitutes: 2   unmapped: 1   escalation: True
  substitute README.md hash=e890012f0ab7448f source=known-fallback
  substitute docs/agents/ORCHESTRATOR_CONTEXT.md hash=2f79929ecb85851b source=agent-declared
spine journal verbs: ['advance', 'attest', 'start']
verify-orientation re-run exit: 0
DEGRADED-REPORTED-AND-DISCHARGED-WITHOUT-FORCE-OR-WAIVER
### exit: 0
```

`spine journal verbs: ['advance', 'attest', 'start']` is the load-bearing line — **no `waive`,
no `--force`**. The gate was passed on its own terms. The stop condition *"cannot be discharged
without `--force` or a waiver"* did **not** fire.

## 4. The full suite

```
$ cd C:/Programs/constellation-skills-wt/e298-304
$ python -m pytest -q
...
1538 passed, 2 skipped, 481 subtests passed in 202.12s (0:03:22)
### exit: 0
```

Nothing red, so no attribution was needed. Run **twice**: once by hand into
`evidence/g4-full-suite.txt`, and once by the engine as m3's own command check (`m3 -> complete`,
which the engine only writes after the check exits 0).

**This is a local number, not the merge gate.** Local interpreter:
`3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]`. CI pins 3.12; the
merge gate is the CI check status read at source, which is the Commander's to read.

## 5. Cleanup — verified, not claimed

```
$ rm -rf .agent-work/g4-scratch-run
### exit: 0
$ ls -d .agent-work/g4-scratch-run
ls: cannot access '.agent-work/g4-scratch-run': No such file or directory
### exit: 2
```

And by blob OID against the pre-g4 tree (`4f9c6d1`), because on Windows `git status --porcelain`
shows a phantom `M` from CRLF while the content is identical:

```
$ python .agent-work/issue-304/evidence/g4_assert_closeout.py
scratch work area C:\Programs\constellation-skills-wt\e298-304\.agent-work\g4-scratch-run exists: False
.agent-work/issue-304/TRIPWIRE_OUTCOMES.md                 3ccd8b547fbb  UNCHANGED
.agent-work/issue-304/TREND_SNAPSHOT.md                    ad2ee8361bcc  UNCHANGED
.agent-work/issue-304/crew-handoffs/g3-result.md           6597f5c8d2fa  UNCHANGED
.agent-work/issue-304/evidence/g3-run-transcript.txt       11254624da14  UNCHANGED
.agent-work/issue-304/g3-implementer-plan.json             71875372f39f  UNCHANGED
.agent-work/issue-304/spine.json                           183930008cf1  UNCHANGED
TRIPWIRES.md                                               eab67aca3cc9  UNCHANGED
TRIPWIRES.md vs pre-registration 1662b90: IDENTICAL
result file g4-result.md exists: True
CLEANUP-VERIFIED-PRIOR-GATES-UNTOUCHED-RESULT-WRITTEN
### exit: 0
```

`.agent-work/issue-304/execute.json` and `crew-runs.json` are deliberately excluded from that frozen
list and are the subject of Deviation 1 below — they were the **Commander's** in-flight writes, not
mine, and the exclusion is named in the check's own source rather than hidden.

---

## Test mode
**Required:** demonstration / evidence capture (the handoff scopes g4 as *"mostly demonstration, not
construction"*).
**Satisfied:** `yes`. No behavior change was made, so there was nothing to lead with a failing test.
Each plan item nonetheless carries an executable command check, and the engine ran all four.

## Docs/contracts touched
None.

## Assumptions
- That `<commander-skill-dir>` resolving to the relative `scripts` in a source repo is **resolution**
  rather than a resolution failure. Stated because it is the one judgment call in §1: the token is
  gone, the branch is documented in the resolver's own docstring, and the residual fragility is #341,
  which is out of scope here. A reviewer who reads it as a failure should push back on that paragraph.

## Stop conditions hit
**None**, and each was checked rather than assumed:
- the context check **was** dischargeable without `--force` or a waiver (§3, journal verbs);
- **no** placeholder failed to resolve (§1, zero survivors);
- the dogfood required **no** code change at all (`git diff` outside `.agent-work/` is empty);
- the full suite is **green**, so nothing needed attributing.

---

# DEVIATIONS

## Deviation 1 — I committed the Commander's in-flight engine state (mine to own)

`git add -A .agent-work/issue-304/` in the m2 commit swept in two files that were **already modified
in the working tree before this crew started** and are the **Commander's**, not mine:

```
$ git show --stat --oneline a90262e
 .agent-work/issue-304/crew-runs.json               |  22 ++++
 .agent-work/issue-304/execute.json                 |   5 +-
 .agent-work/issue-304/execute.json.journal         |   2 +
 ...
```

The content is the Commander registering **this dispatch** (`crew_id
constellation/issue-304/g4/implementer/attempt-1`, `status: running`) and starting its own g4 gate
(`"status": "pending"` → `"in-progress"`, g4's `p1` attested). **Nothing was altered or lost** — the
diff is the Commander's own writes, now committed rather than uncommitted. I did not revert it:
un-committing would take the Commander's live state out of the index mid-run, which is the more
dangerous move. Every later g4 commit named explicit paths. **The Commander should be aware its
engine state is in `a90262e`.**

## Deviation 2 — the engine ran the full suite twice

m3's command check is the suite itself, so advancing m3 re-ran all 1538 tests (~3.4 min) after my own
`tee`-captured run. Deliberate: the engine discards stdout, so a single engine-run would have left no
verbatim result line, and a single hand-run would have left the gate unproven. The alternative was an
`amend --op retext-check` to a tee-wrapper, which buys 3 minutes for a plan amendment nobody needs.

## Deviation 3 — mis-scoped exit codes in the first third of the transcript

The first stage-A block in `g4-run-transcript.txt` reports `### exit:` values taken from a pipeline
whose last element was `grep`, so they read `0` even where the engine returned `1`. **Caught during
the run, corrected in place, and nothing rests on them:** the transcript carries a `NOTE ON EXIT
CODES` block at that boundary, stage A was **re-run** with the exit code captured before any pipe,
and every code quoted in this result comes from the corrected runs. The uncorrected lines were left in
the transcript rather than edited out, because deleting them would make the record less honest, not
more.

---

## Findings — two, both small, neither fixed (out of scope)

1. **`current` tells the agent to append a flag to "the command below", and then prints no command.**
   The `context` imperative ends: *"Gate-vs-report is a flag flip: append `--report-only` to the
   command below to turn this gate into a non-blocking report without rewiring the step."* The engine's
   `current` renders the postcondition's **statement** and its kind, never the command text:

   ```
   c2 [unmet] command — the map input was resolved BEFORE any source file was opened, and the
   orientation contract is satisfied: ... append --report-only to the command below ...
   ```

   There is no command below. An agent following `current` alone — which is exactly what
   `global-everyone.md` §"Engine output is the state channel" requires, and what a cold-started
   refresh agent has — cannot act on that sentence without reading `spine.json`, which the same
   doctrine calls a violation. **Triage candidate**, not a g4 fix: it is either a one-line `current`
   renderer change or a wording change in the imperative, and both belong to whoever owns the
   gate-vs-report flip.

2. **A substitute that exists on disk is labelled *"not corroborated by the filesystem."***
   `docs/agents/ORCHESTRATOR_CONTEXT.md` is present (1995 bytes) and the receipt **hash-pinned its
   contents** — `2f79929e…`, which can only be computed by reading it. The label is nonetheless
   `agent-declared — UNVERIFIED -- declared by the agent, not corroborated by the filesystem`. The
   *provenance* classification is deliberate and test-pinned (`map_orient.py`: *"a path outside the
   fixed set is agent-declared even when present"*), and that design is right — membership of the
   fixed fallback set is an oracle the agent does not author. It is only the **note text** that
   overclaims: the accurate sentence is *"not in the fixed fallback set"*, since presence plainly was
   corroborated. **Triage candidate**, wording only.

   > **CORRECTION, and now FIXED — see §6.** As first written, this paragraph said the fix was left
   > alone partly because *"three tests assert on these labels."* **That count was wrong, and an
   > overestimate of a fix's cost is exactly how a cheap must-fix becomes a permanent deferral.**
   > Measured rather than recalled:
   >
   > ```
   > $ grep -rn "UNVERIFIED\|corroborated" tests/
   > tests/test_map_orient.py:1075:        self.assertIn("UNVERIFIED", proc.stdout)
   > ```
   >
   > **Zero** tests pin the sentence; **one** pins the word `UNVERIFIED`, which the accurate rewording
   > keeps. One string literal, zero test churn. The Commander routed it fix-now on that basis and it
   > is done.

## Map Impact

- **Structural anchors touched:** none. Read-only against
  `skills/commander/templates/COMMANDER_SPINE.template.json`, `scripts/init_work_area.py`,
  `scripts/map_orient.py`.
- **Capabilities affected:** none added or removed. **Confirmed live end to end**: the Commander
  orientation contract materializes with resolved placeholders and gates `context` on a discharged
  receipt. This closes the #345 pattern for *this* capability — it is exercised through
  `init_work_area.py` → engine → command check, not only through its unit tests.
- **Constraints/assumptions touched:** g3 recorded that `docs/architecture/` is absent here; g4
  **re-confirms it by command** (`candidates tried: … absent, absent, absent`) and, for the first
  time, puts that gap on the record *inside a receipt* as a named escalation rather than only in a
  result document.
- **Claims/evidence produced:** the degraded arm reports (exit 12/10), is dischargeable without
  `--force` or a waiver (journal verbs), and the materialized `--root` is absolute.
- **Trust limitations:** the g4 evidence covers the **degraded** arm only. The **mapped** arm —
  `RESOLVED` from a real `docs/architecture/` — remains untested in this repo for the same reason g3
  gave (no map here; `f1Brainz` is off-limits because `orient` *writes* a receipt into its `--root`).
  T3's mapped-repo clause is still unfalsified and unconfirmed. Unchanged by g4, and stated so it is
  not read as covered.
- **Triage candidates:** finding 1 (open). Finding 2 was routed fix-now by the Commander and is fixed in m5 (§6).

## Workflow Feedback

- **Handoff gaps: none material.** All eight fields were present and the three deciding questions were
  stated as questions with pass/fail shapes, which is what made this gate cheap to run — the plan
  items fell straight out of them.
- **Context rediscovered:** whether `<commander-skill-dir>` resolving to a **relative** `scripts` counts
  as resolved. The handoff says *"confirm the materialized `spine.json` carries real absolute paths"*
  (plural), which reads as covering all three placeholders; in this repo only `<repo-root>` can be
  absolute, by the resolver's design. Settled by reading `_resolve_skill_dir_token`'s docstring and
  the #341 exclusion, but a reviewer could reasonably have read it as a stop condition. **One clause —
  *"`<repo-root>` absolute; `<commander-skill-dir>` may legitimately resolve relative in a source
  repo, see #341"* — would have removed the ambiguity.**
- **Instructions improvised around:** the doctrine that `spine.json` must never be opened directly
  ("engine output is the state channel") collides with this gate's **required evidence**, which is a
  property of the materialized file's **content** — placeholder text — that `current` does not render.
  I read the scratch spine as the **artifact under test**, not as a state channel, and the distinction
  held; but the doctrine sentence does not carve it out, and the next agent will hit the same seam.
  Finding 1 above is the sharper end of the same collision.
- **What would have made this easier:** nothing structural. The three-question framing plus g3's
  transcript meant this run added the missing stage (B: the undischarged receipt) rather than repeating
  g3's two.

---

# 6. Post-review slice m5 — the fix-now triage from the g4 review

**g4 was APPROVED with no blockers.** The Commander then routed reported finding 2 as **fix-now**
rather than deferred, on the ground that an honesty defect *in the honesty feature* is the wrong thing
to defer, and that my own cost estimate was an overestimate. Appended as gate `m5` via the engine's
`amend --op add` (authority: `commander-304c (g4 review adjudication)`) after a `claim --force
--reason "fix-now triage from g4 review: overclaiming substitute label"` — **appended, not reopened**:
nothing upstream is invalidated by a wording change.

## 6a. The reword — one string literal

```
$ git diff --stat scripts/map_orient.py
 scripts/map_orient.py | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

$ git diff scripts/map_orient.py
@@ -960,7 +960,7 @@ def render_verify_report(
         if label == LABEL_KNOWN_FALLBACK:
             note = "found in the fixed fallback set and present on disk"
         else:
-            note = "UNVERIFIED -- declared by the agent, not corroborated by the filesystem"
+            note = "UNVERIFIED -- declared by the agent, not in the fixed fallback set"
         lines.append(f"substitute: {path if path else '(no path)'} [{label}] -- {note}")
```

`UNVERIFIED` is kept; `substitute_label` and the `LABEL_*` constants are untouched; the neighbouring
comments were checked and were **already** accurate (*"the receipt distinguishes 'resolved from the
known fallback set' from 'the agent said so'"*), so nothing else needed changing. `grep -rn
"corroborated" scripts/ tests/ skills/ docs/` now returns no hit in this tool.

**The reworded line, live** — same repo, same present-and-hash-pinned substitute that produced the
finding:

```
$ python scripts/map_orient.py verify-orientation --root C:/Programs/constellation-skills-wt/e298-304 --work-id g4-fix-check
DEGRADED-NO-MAP
receipt: .agent-work/g4-fix-check/map-orientation.json
orientation contract SATISFIED
problems: 0
substitute: README.md [known-fallback] -- found in the fixed fallback set and present on disk
substitute: docs/agents/ORCHESTRATOR_CONTEXT.md [agent-declared] -- UNVERIFIED -- declared by the agent, not in the fixed fallback set
### exit: 0
```

The `g4-fix-check` scratch area was removed and its absence verified (`ls -d` → *No such file or
directory*), same as the main scratch.

## 6b. The two required re-runs

```
$ python scripts/map_orient.py --self-test
self-test OK
### exit: 0

$ python -m pytest tests/test_map_orient.py -q
.......................................................................................                   [100%]
87 passed, 39 subtests passed in 11.96s
### exit: 0
```

**Zero test churn**, as the reviewer's measurement predicted. Both were also re-run by the engine as
m5's own `c1` check before it would write `m5 -> complete`.

## 6c. The harness weakness the reviewer found — fixed, because it was one line

The reviewer found that `g4_assert_discharged.py` asserted the degraded verdict with
`"DEGRADED" in json.dumps(receipt).upper()` — a substring scan over the whole document, satisfied by
**my own escalation prose** (*"…structurally degraded until a map exists"*) while the structured
verdict was fetched and discarded. It returns True on a `mode: RESOLVED` receipt. **That is the #300
failure class — a check that cannot fail — sitting inside the very gate whose job was to prove that
checks fire, and it is the sharpest single finding of this review.** It was mine, and the reviewer had
to find it because I did not.

The Commander's instruction was: fix it if it is one line, otherwise record it. **It was one line** —
`build_receipt` writes the verdict to a structured `mode` field, so the predicate now reads
`str(receipt.get("mode", "")).upper().startswith("DEGRADED")` and nothing else.

A repair asserted only in the direction we want would be the same defect wearing a fix's clothes, so
the repair is pinned by an executable discriminator (`g4_assert_harness_discriminates.py`, m5's `c2`
check) that loads the corrected predicate **out of the shipped source by `ast`** — not a copy — and
runs it against the reviewer's own adversarial receipt in all three directions:

```
$ python .agent-work/issue-304/evidence/g4_assert_harness_discriminates.py
OLD substring predicate on a RESOLVED receipt: True   <- the defect
NEW structured predicate on the same receipt:  False   <- the repair
NEW structured predicate on a DEGRADED receipt: True  <- no over-correction
HARNESS-PREDICATE-DISCRIMINATES
### exit: 0
```

**Named plainly, so nobody later cites the original assertion as if it carried weight:** the
`receipt degraded: True` line quoted in §3 above was, at the time it was printed, produced by a
predicate that could not have printed anything else. **The §3 conclusion does not rest on it** — it
rests on the exit path 12 → 10 → 10 → 0, the journal verbs `['advance','attest','start']`, and the
reviewer's two independent wiring mutations, all of which the reviewer reproduced himself. The line is
now backed by a predicate that can fail, but the reason the conclusion survived was over-determination,
not the assertion.

## 6d. What m5 did NOT change

Finding 1 (`current` renders no command text) is **still open and still not fixed** — it belongs to
whoever owns the gate-vs-report flip. The classification logic, the `UNVERIFIED` label, the mutation
pins, and every g4 conclusion above are unchanged. Full suite was **not** re-run for m5; the scoped
re-runs the Commander asked for are in §6b, and the last full-suite number in this document remains
the one from §4.

**m5 commit:** see `git log`; the plan reached `DONE: no open items` again and the lease was released
as the last journaled action.

---

## Unresolved blockers
**None.** One triage candidate (finding 1) awaits a Commander routing decision, and the Commander should note that
its own engine state rode along in commit `a90262e` (Deviation 1).
