# Plan alternatives — issue #307, run BEFORE the plan froze

The launch order fixes the method almost completely: the pin, the task set, the treatment, the
scorers, the arm it pairs with, and the pre-registered discrimination are all frozen. The
genuine latitude is narrow, so this is three real candidates over the one axis that was
actually open — **how POST gets measured without becoming its own confound** — plus the roads
not taken, named rather than silently dropped.

## The open axis

POST pairs with PRE-B. PRE-B's instruments exist. The question is how much of them to reuse
when POST needs at minimum a different output directory and an honest arm label.

### Candidate A — reuse under the constraint "change nothing at all"

Run `capture_preb.py` completely untouched, into a new `--out`, and record the arm label in a
sidecar file next to each run because `meta.json` will say `"arm": "PRE-B"`.

- **For:** literally zero instrument delta. The strongest possible comparability claim.
- **Against:** every archived `meta.json` in the POST arm asserts it is PRE-B. A future reader
  — the exact reader `PREB_RECORD.md` §"three arms, two series" was written to protect — finds
  ten run directories claiming to be the same arm, and the sidecar is the only thing
  contradicting them. **That trades a real, permanent provenance defect for a purity that is
  cosmetic**, because the label is never read by the measured path.
- **Verdict: rejected.**

### Candidate B — reuse under the constraint "only what cannot be a confound may change"

Add one additive, default-preserving `--arm` label flag to `capture_preb.py`, derive
`run_all_post.py` from `run_all_preb.py` changing only the worktree template, runs root,
fingerprint path and the label. Scorers untouched.

- **For:** the brief bytes, argv, env scrub, pin assertion, pristine assertion,
  no-worktree-corpus assertion and launch path are all byte-identical, and the flag's default
  reproduces PRE-B exactly — so the change is *checkable* rather than merely claimed. Every
  archived artifact is honestly labelled.
- **Against:** it is still a diff against a spent arm's instrument.
- **Verdict: CHOSEN.** Declared in writing to the Admiral before any run, per the launch order.

### Candidate C — reuse under the constraint "the new measure must be trustworthy"

B, plus a supplementary `map_orient` invocation audit.

This one is forced by a hazard that only exists on the POST side: the frozen extractor buckets
any call touching `.claude/skills` as `skill-corpus` **and nothing else**, and the #304
contract is discharged by invoking a script that lives under `.claude/skills`. **The mandated
act is invisible to the primary instrument by construction.** Without a second witness, a run
that ran the contract and a run that never did are indistinguishable — which is precisely the
*insufficient* vs *irrelevant* boundary the arm exists to draw.

- **Against:** it is new code in an experiment whose discipline is reusing old code.
- **Mitigation, and the reason this is acceptable:** the same code is run over **PRE-B**, where
  it must report zero by construction (that corpus has no `map_orient.py` at all). **Run: 0
  invocations across 5 runs / 595 tool calls. Negative control passed.** A non-zero result
  there would have meant the audit was matching noise and its POST column had to be discarded.
- **Verdict: CHOSEN, layered on B.** The primary outcome stays `discriminate.py`, unmodified.

## Convergence

**B + C.** Reuse everything that scores; add exactly one label flag and one derived driver; add
one new measure only where the primary instrument is blind by construction, and validate it
against the prior arm before trusting a single POST number from it.

## Untaken roads, named

1. **Re-capture PRE-B on `constellation-commander-delegated`** so the pair shares the variant
   PRE-B's record flagged in its §12. **Declined by ruling** carried in the launch order; POST
   matches PRE-B on `constellation-commander` instead. Cost: the pair shares the *human-driven*
   variant, whose spine carries `user-decision` postconditions a headless subject must talk its
   way through. PRE-B's 5/5 no-stall completion is what makes this safe.
2. **Increase n above 1 per task.** Would give the first variance estimate this epic has had.
   Not taken: the task set is frozen at five and the arm is ~$57 and ~40 minutes per pass.
   Left as the obvious next arm if the result is close to the line.
3. **Patch the frozen extractor's corpus rule** so `map_orient` calls stop being swallowed.
   **Deliberately not taken** — it would rescore PRE-B under different code and destroy the
   pairing. Measured and declared instead, exactly as PRE-B handled the same rule (§8 item 6).
4. **Grade the POST plans blind, as PRE-B did.** Not part of this launch order's mission, which
   is the ordering evidence package. The transcripts and final answers are archived, so a
   grading pass remains possible later without re-running anything.
5. **Rule on the rubric §2 tolerance ambiguity (#333)** before pairing. Two independent graders
   have now hit it. Not this run's to rule, and it does not touch the ordering measure — but if
   the seam scores are ever paired it must govern both arms identically.
