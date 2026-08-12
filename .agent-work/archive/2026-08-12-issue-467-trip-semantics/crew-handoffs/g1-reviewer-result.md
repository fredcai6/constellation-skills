# REVIEW_RESULT

ACCEPT WITH FINDINGS

The RED is genuine. It reproduces #431 and not something adjacent, and it survived every attempt I
made to break it — including two control variants and one escape route the repro does not itself
test. Eight non-blocking findings, no blockers. The most important of them is not about the repro:
it is that the result's Scope section makes a claim about version control that is false at HEAD.

Gate: `g1-review` of `.agent-work/issue-467-trip-semantics/execute.json` (issue #467, epic #418 wave 4).
Survey driven at `.agent-work/issue-467-trip-semantics/g1-review/review.json` (7/7 items, consolidated).
Everything below was run by me at HEAD `19b879f2ad0cf5854f02580f2d3f53a017219812`.

---

## Answer 1 — Was a fresh, valid reading actually READ? YES.

Two independent proofs: the engine's own advisory, and the reader's own verdict on the planted record.

I re-ran the repro myself and read the exit code from a redirect, never a pipe:

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-467
python .agent-work/issue-467-trip-semantics/red-repro/repro_431.py --all > /tmp/rev-repro-all.txt 2>&1; echo "REAL_EXIT=$?"
grep -c "ASSERT OK" /tmp/rev-repro-all.txt; grep -c "ASSERT FAIL" /tmp/rev-repro-all.txt
```

```
REAL_EXIT=0
24
0
```

The engine proving it read the number, from my own transcript (`grep -n CONTEXT /tmp/rev-repro-all.txt`):

```
71:| CONTEXT 30% (>= hard): `advance` is BLOCKED until you request a refresh. Run: attach g2 --type refresh-request --field seam=g2 --field why_ref=<why-id>  - then hand off.
135:| CONTEXT 30% (>= hard): `advance` is BLOCKED until you request a refresh. Run: attach g2 ...
175:| CONTEXT 30% (>= hard): refresh already requested for g2 - hand off now; do not keep working.
308:| CONTEXT 30% (>= hard): `advance` is BLOCKED until you request a refresh. Run: attach g2 ...
```

Line 58 of the same transcript is the other half of the pair — `no CONTEXT advisory before the gauge
exists`, same spine, same session. Silence and headroom are therefore distinguishable in this run.

Then I checked the planted record would actually survive `gauge_reader.read()` rather than trusting
that the advisory implied it:

```bash
python -c "import sys; sys.path.insert(0,'scripts'); import gauge_reader; ..."
```

```
raw file: {"schema_version": 1, "fill_fraction": 0.3, "model": "claude-opus-5", "observed_at": "2026-08-08T10:51:12.676477Z"}
read() -> Reading(schema_version=1, fill_fraction=0.3, model='claude-opus-5', observed_at=datetime.datetime(2026, 8, 8, 10, 51, 12, 676477, tzinfo=datetime.timezone.utc))
thresholds_for(claude-opus-5) (soft,hard) = (0.08, 0.15)
REQUIRED_FIELDS = ('schema_version', 'fill_fraction', 'model', 'observed_at')
all required present: True
max_age = 0:30:00   skew tol = 0:02:00
fill >= hard ? True (0.3 >= 0.15)
```

All four required fields present; `claude-opus-5` is in `_PROFILES` so the record is calibrated and
`_parse_record` does not reject it; `observed_at` is planted at `now - 5s`, inside the 30-minute
staleness window and not in the future. `read()` returns a `Reading`, not `None`. The band is not
no-opped.

## Answer 2 — Is the stale DIGEST the real consequence of the shipped instruction? YES.

**The control exists and differs from the trip run only in the gauge.** I diffed the two scratch
spines as normalized JSON rather than taking the claim:

```
--- face-a(tripped)          +++ counterfactual
-  "session_id": "repro-431-a",        +  "session_id": "repro-431-a-cf",
-  "refusals": 1,                      +  "refusals": 0,
-  "evidence": [ {"id":"e-g2-1", "type":"refresh-request", "payload":{"seam":"g2","why_ref":"w-1"}} ],
+  "evidence": [],
-  "status": "in-progress",            +  "status": "complete",
+  {"gate":"g2","id":"w-2","why":"CURRENT UNDERSTANDING: ..."}
```

Same `items`, same gates, same imperatives, same postcondition ids and statements. Every delta is a
*downstream consequence* of the refusal — the refusal count, the refresh-request the refusal told the
agent to attach, g2's status, and the missing `w-2` why-record which is the defect itself. Nothing
about the spine's shape differs. The staleness is attributable to the refusal.

**I then ran a tighter control than the repro's own, because the repro's counterfactual removes the
gauge FILE, which conflates "no gauge" with "gauge below hard".** PROBE 1 builds the identical Face A
spine, plants the gauge at the same path at the same moment with `fill_fraction 0.02`, and advances:

```
PROBE1 advance exit=0
PROBE1 DIGEST = "CURRENT UNDERSTANDING: g2 found the reader's None path is reached from three distinct failure modes, ..."
PROBE1 RESULT: digest_is_fresh=True  digest_is_stale=False
```

The RED survives the tighter control: it is the gauge's **number**, not the gauge's **presence**,
that produces the stale DIGEST. See finding N4.

**And I verified in source, not from the report, that `advance` really is the sole DIGEST writer** —
otherwise the whole property would be an artifact of the repro's choice of verbs:

```bash
grep -n "_append_why(\|_append_reopen_marker(" scripts/checklist_engine.py
```
```
1095:def _append_why(...)          1109:def _append_reopen_marker(...)
1901:            _append_why(cl, iid, why=None, mechanical=True)      # inside advance() (1854-1916)
1903:            _append_why(cl, iid, why=why.strip(), mechanical=False)  # inside advance()
2123:    _append_reopen_marker(cl, iid, reason)                        # inside reopen()
2125:        _append_reopen_marker(cl, did, reason)                    # inside reopen()
```

Both `_append_why` call sites are inside `advance()`; `reopen` writes only a marker, which
`_latest_why_record` skips. `record()` at 1917 writes no why. Confirmed.

**The one thing the repro asserts in prose rather than in code, I tested.** The result says "a further
`advance` would be permitted" after the keyed attach. PROBE 2:

```
PROBE2 post-attach `current` HARD line: 'CONTEXT 30% (>= hard): refresh already requested for g2 - hand off now; do not keep working.'
PROBE2 post-attach advance exit=0
PROBE2 DIGEST after that advance = "CURRENT UNDERSTANDING: ..."
PROBE2 RESULT: hard_band_released_and_advance_succeeded=True  digest_now_fresh=True
```

True. This is the sharpest statement of what #431 actually is, and it is worth stating precisely
because it is what the fix will be measured against: **#431 is not a mechanical deadlock. The engine
permits the advance that would write a fresh DIGEST; it just tells the agent, in the same breath, not
to run it.** An agent that obeys "hand off now; do not keep working" strands a stale brief. An agent
that disobeys is fine. So the staleness is the consequence of the shipped *instruction*, which is
exactly what question 2 asks — and it is not an arrangement by the repro, because stopping at that
point is literally what the engine's own text told the agent to do. See finding N3.

## Answer 3 — Would this go GREEN under the planned fix, and RED again if reverted? YES, and yes.

**Reverted → RED again, by construction.** The repro holds no copy of the engine. Line 58 is
`ENGINE = WORKTREE / "scripts" / "checklist_engine.py"` and line 120 execs it with `sys.executable`,
so it always tests whatever is at HEAD. Restoring the refusal restores exactly the run above.

**Under the fix (HARD moves from `advance` to `start`/`reopen`): 11 of the 24 assertions flip.**
I walked all 24 against the fix. `start g2` happens before the gauge is planted, so the tripped agent
is never stopped, its `advance --why` lands, and the DIGEST is fresh.

Flips (11) — every load-bearing #431 claim is here:

| assertion | why it flips |
|---|---|
| Face A: `advance g2 is REFUSED by the HARD band` | advance now exits 0 |
| Face A: `the refusal prints the exact remedy command` | there is no refusal |
| Face A: `the CURRENT understanding was NOT written` | it is written |
| Face A: `successor's current shows the refresh request` | no refusal, so no attach |
| Face A: `the successor is pointed at g2` | g2 completes; spine goes terminal |
| **Face A: `the DIGEST STILL names the PRE-TRIP understanding`** | **the core #431 claim; DIGEST becomes CURRENT** |
| **Face A: `successor told NOTHING of the understanding actually held`** | **CURRENT_WHY now appears** |
| Face A: `cf_digest != successor_digest` | both become CURRENT_WHY, so they are equal |
| Face B: `the refusal it gets is the HARD-band one` | it becomes the postcondition refusal |
| Face B: `the HARD refusal never mentions c2` | the refusal now names c2 |
| Face B: `the two refusals are different instructions` | both become the same postcondition refusal |

Pass on **both** sides (13) — I checked each against the handoff's warning, and **none of them is
offered as evidence of #431**. They are the harness, the setup, the control, and the honest-scope
limit, in that order:

- *Harness / prove-the-read* (5): the three `--assert-gauge-read` assertions, plus Face A's and
  Face B's own "the reading was read" pair. These prove the band fired at all. They must pass on both
  sides — and they are **load-bearing for exactly that reason**: without them, a post-fix "green" run
  would be indistinguishable from a run where the gauge silently stopped being read. This is the
  no-absence-is-evidence rule doing its job, not padding.
- *Setup* (2): `g2's postconditions are ALL satisfied` (the `n/m met` tally) and `the successor's
  current carries a DIGEST line at all`. These establish the preconditions of the experiment.
- *Control* (1): `with no HARD refusal, the SAME advance writes the CURRENT understanding`. The
  control arm has no gauge, so the fix cannot reach it. It must pass on both sides or it is not a
  control.
- *Honest scope* (5): the below-HARD assertions in Face B and `current DOES still list c2 [unmet]`.
  These are deliberate **negative** scope claims — statements about what is NOT masked.

So: no assertion is dressed up as #431 evidence while being insensitive to the fix. That was the
thing to find, and it is not there.

One mechanical observation on the flip path, finding N6: Face A's flip is caught by
`expect_refusal=True` **raising**, so under the fix the script dies at the first flip and reports one
message. Face B's flips are caught as ordinary assert-fails, which is the better shape.

## Answer 4 — Is `git diff --stat -- scripts tests` empty? YES — and I checked three more ways.

```bash
git diff --stat -- scripts tests > /tmp/rev-diffstat.txt 2>&1; echo "EXIT=$?"; echo "bytes: $(wc -c < /tmp/rev-diffstat.txt)"
git status --porcelain -- scripts tests > /tmp/rev-status.txt 2>&1;  echo "bytes: $(wc -c < /tmp/rev-status.txt)"
git diff --cached --stat -- scripts tests
git diff --stat main...HEAD -- scripts tests
git rev-parse HEAD
```

```
EXIT=0
bytes: 0          <- worktree diff
bytes: 0          <- status, incl. untracked
(empty)           <- staged
(empty)           <- every commit on this branch vs main
19b879f2ad0cf5854f02580f2d3f53a017219812
```

The literal question the handoff asks — is the worktree diff empty — **would pass even if a commit on
this branch had rewritten `scripts/checklist_engine.py`**, because a committed change is not a
worktree diff. That is a check that could pass while the claim it stands for is false, which is this
epic's own defect wearing a small hat. I ran `main...HEAD` for that reason; it is empty too, so the
claim holds on its strongest reading: the engine under test is byte-identical to main. See W3.

Also verified clean: `.claude/settings.json` (#458) and `.agent-work/epic-418-redux/**`, both on the
branch and in the worktree. No part of the fix is implemented — the repro only runs the shipped
engine as a subprocess.

**Suite tripwire**, re-run by me rather than taken from the report, exit code from a redirect and
`python -m pytest`, never `py` (#454):

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests > /tmp/rev-suite.txt 2>&1; echo "REAL_EXIT=$?" >> /tmp/rev-suite.txt
```
```
1793 passed, 2 skipped, 683 subtests passed in 378.02s (0:06:18)
REAL_EXIT=0
```

Exactly the recorded baseline, independently confirmed.

---

## Scope-limit check

The handoff asked me to confirm the result does not claim wider than the scope the implementer
volunteered. **It does not.** Face B's limit — `current` still lists `c2 [unmet]` at HARD, so the
masking is scoped to the `advance` refusal path — is stated in the result (§4) *and* asserted in the
script (line 421, `"c2 [unmet]" in out`), and I watched that assertion pass in my own run. The result
explicitly tells reviewers not to read it wider. That is the right standard and it was met.

One wording caution, N7: the result calls the property "the deadlock" while simultaneously disclosing
that the advance would be permitted. Both statements are true and the disclosure is right there, but
downstream summaries that quote only the word "deadlock" will overstate. Prefer: *an agent that
follows the engine's own instruction strands a stale brief.*

## Findings

**Blocking: none.**

**Non-blocking:**

- **N1 — the result's version-control claim is false at HEAD.** §Scope says "Files changed: none under
  version control. Created, all local-only and deliberately not `git add`ed". But
  `git ls-files -- .agent-work/issue-467-trip-semantics/red-repro/` lists `repro_431.py`, all four
  transcripts, and 25 throwaway `scratch/**` files; they landed in commit `62f564c7`. The implementer
  handoff's Deliverable Path Check said, in terms, "do **not** `git add` or commit it". The statement
  was probably true when written and was made false by a later commit — but it is false now, and
  checking a claim against the world is what this gate is for. **Consequence, and the reason this is a
  finding and not a nit: the disposable scratch is now tracked, so every re-run of the repro dirties
  25+ tracked files.** My own re-run did exactly that. `decision:red-leaves-no-residue` rules that out.
  Recommend untracking `red-repro/scratch/**` at minimum, and correcting the sentence.
- **N2 — an unverifiable claim about a moving target.** §Scope states the live gauge "still reads
  `fill_fraction 0.126843, observed_at 2026-08-08T10:22:49.263Z`, byte-identical to what was there
  before this gate." `gauge.json` is git-ignored and rewritten by the harness hook continuously; when
  I read it it was `0.06344 @ 2026-08-08T10:48:22.868Z`. No wrongdoing is implied — the hook writes
  it — but a reviewer who took the claim literally would find a different value and wrongly conclude
  someone had touched the file. This is the inherited "pin a claim to the revision you read it at"
  rule: do not report a read of a continuously-rewritten file as a stability property.
- **N3 — the most load-bearing structural sentence is prose, not an assertion.** "A further `advance`
  would be permitted" is what makes #431 an instruction-conformance defect rather than a mechanical
  block, and g2–g4's fix design leans on it. It is narrated, not asserted. I verified it (PROBE 2
  above), so this is not a gap in the *finding* — but it is the assertion the repro most deserved.
- **N4 — Face A's control varies gauge presence, not gauge value.** The counterfactual omits the gauge
  file entirely, so strictly it controls for "a gauge exists" rather than "the gauge reads high". My
  PROBE 1 closes the gap and the RED survives. Face B does exercise a below-HARD gauge, so the
  ingredient was on hand; Face A just did not use it.
- **N5 — dead code that misleads about the very gap the result files.** `why_ref_from_current()`
  (lines 228–232) is never called; grep finds only its own `def`. Its presence implies the why-record
  id is recoverable from engine output. My PROBE 4 shows it is not: no `w-N` appears in `current` or
  in the refusal text before the attach. Delete it, or a later reader will conclude the result's own
  triage candidate 2 is already solved.
- **N6 — under the fix, only the first flip is reported.** `expect_refusal=True` raises rather than
  recording an assert-fail, so Face A dies at step 2 post-fix. Face B's shape (assert on the refusal's
  text) is the better one.
- **N7 — "deadlock" overstates in isolation.** See Scope-limit check above.
- **N8 — Fowler pass, 3 flagged / 2 overridden.** Record:
  `.agent-work/issue-467-trip-semantics/g1-review/fowler-pass.json`; `verify_fowler_pass.py` exits 0.
  Flagged: *speculative-generality* (N5), *long-method* (`face_a()` is 90 lines holding two
  experiments; the counterfactual control this review turns on is not separately runnable, which is
  why I had to write my own), *message-chains* (`WORKTREE = HERE.parents[2]` derives the
  engine-under-test by positional index, and "this is the unmodified HEAD engine" is the gate's
  load-bearing claim; `ENGINE` is printed to the transcript but never asserted). Overridden with logged
  standards: *duplicated-code* — the read-proof block appears three times, but
  `constraint:no-absence-is-evidence` requires each face to prove its **own** read, and sharing the
  assertion would let one face's read stand in for another's; *primitive-obsession* — the gauge is
  planted as a raw dict rather than a typed record so it exercises the shipped reader's validation
  instead of pre-satisfying it.

**Corroborated, not a finding:** the result's triage candidate 2 (the `<why-id>` copy-paste trap) is
real. PROBE 3: `attach ... --field why_ref=<why-id>` exits **0**, and the following `advance` is still
**refused** — a silent no-op. Worth the Triage issue the result proposes.

## What I could not verify, and why

- **Whether the live `spine.json` / `gauge.json` were modified by the implementer.** `gauge.json` is
  git-ignored and hook-rewritten, `spine.json` shows as modified but a live Commander run owns it, and
  the handoff forbids me from touching either. Not verified; out of scope. N2 records what I could see.
- **The implementer's own pytest transcript.** I did not audit it; I re-ran the suite myself instead,
  which is the stronger check. Note that `git diff main...HEAD -- scripts tests` being empty already
  makes a suite regression from this gate impossible.

## Workflow Feedback

- **W1 — `r6-fowler`'s postcondition is a check that cannot pass on a survey, which is this epic's
  defect inverted.** `REVIEW_SURVEY.template.json` ships c1's command as
  `python scripts/verify_fowler_pass.py <fowler-pass-record-path>` — a POSIX shell reads `<...>` as a
  redirect from a nonexistent file, so it always fails. The reviewer SKILL.md says to fill it in before
  recording, but **no engine verb can**: `amend` refuses (`amend applies to gated checklists`) and
  `attest` refuses (`c1 is engine-checked; cannot attest`). I force-waived it with the real command and
  its real exit 0 recorded in the waiver. The Fowler pass itself genuinely passed. Fix: have the
  reviewer fill the command at survey **instantiation** (before `claim`), or allow `amend` on surveys.
- **W2 — survey/gated vocabulary mismatch in the skill.** The reviewer SKILL.md repeatedly says to
  `advance` each check; on a survey `advance` refuses with `advance is for gated checklists; use
  record`. Cost one round trip. The skill should say `record`, or say both.
- **W3 — the handoff's question 4 is weaker than the claim it protects.** `git diff --stat -- scripts
  tests` is a worktree-only check; a commit on the branch that edited `scripts/` would sail through it
  while "the RED is observable at the unmodified HEAD" was false. Recommend future handoffs require
  `git diff --stat main...HEAD -- scripts tests` alongside it. It came out clean here — this is about
  the check, not the result.
- **W4 — the handoff was otherwise the sharpest I have worked from.** Naming the specific failure mode
  (a manufactured RED), telling me my job was to break the claim rather than confirm it, and warning
  in advance that a bare ACCEPT would itself read as a check that could not fail — those three lines
  are why I wrote the four probes instead of re-running the repro and agreeing with it. Keep them.
- **W5 — one thing that would have made this easier.** The handoff asked me to verify the control
  "differs from the trip run **only** in the gauge" but gave no sanctioned way to compare two spines.
  I wrote a normalized-JSON differ. A one-line recipe in the handoff would have saved a round trip,
  and it is reusable at every gate that claims a counterfactual.
