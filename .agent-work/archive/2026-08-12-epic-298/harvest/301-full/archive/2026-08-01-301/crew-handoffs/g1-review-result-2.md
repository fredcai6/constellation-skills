# Review Result — RE-REVIEW (round 2)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1` — episode record grammar and store doctrine (issue #301, epic-298) — **RE-REVIEW** of a
rework that followed a prior `BLOCK` (`.agent-work/301/crew-handoffs/g1-review-result.md`).

## Result
`BLOCK`

VERDICT: BLOCK

Driven survey: `.agent-work/301/g1-review-2/review.json` (session `reviewer-g1-301-rereview`,
claimed/consolidated/released), Fowler pass record: `.agent-work/301/g1-review-2/fowler-pass.json`
(`verify_fowler_pass.py` exit 0). This is an independent re-review — I did not assume the prior
BLOCK's analysis or the implementer's rework account were correct, and re-derived every claim
against the current text of `docs/EPISODE_STORE.md` and `episodes/README.md`.

## Handoff compliance
The three findings that produced the original `BLOCK` are **genuinely fixed**, verified by
direct comparison of the current text against the prior review's quoted offending passages, not
by trusting the implementer's summary:

- **Finding 1 (§7 self-contradiction) — FIXED.** The "never deleted, moved, or truncated ... at
  the same path" sentence is no longer an unconditional claim. It now reads: content-preservation
  holds under either option; "shown here **under Option B**... the file itself never moves";
  under **Option A**, "the identical field update happens... accompanied by a file **move**." The
  self-contradiction the prior reviewer found is gone.
- **Finding 3 (§2 filename/path claim) — FIXED.** §2 now distinguishes: the **basename** is the
  id under either option; the **full path** is layout-dependent (`episodes/<id>.md` under Option
  B, `episodes/active|retired/<id>.md` under Option A), with a pointer back to §7.
- **The two additional §2 instances the implementer self-found (id-sequence-derivation scan,
  query-primitive glob illustration) — both genuinely fixed**, each with explicit Option A/B
  treatment (the sequence scan states the Option A union of `episodes/active/<run>-*.md` and
  `episodes/retired/<run>-*.md`; the glob illustration notes the root changes under Option A but
  the free-lookup-key property holds under either).
- **Finding 2 (membership-predicate seam) — PARTIALLY fixed.** A real named seam,
  `is_episode_in_ordinary_search(episode_id)`, is added in §7 with two adapters (an Option-A
  directory check, an Option-B status check), and §8 was rewritten so the per-id retirement
  filter routes through it instead of naming a grep directly at the call site. This genuinely
  makes the **per-id membership check** additive — a real fix, not cosmetic. **But see the
  load-bearing finding below: this does not fully close the gap.**

## Scope drift
None. `git status --short` shows exactly `A episodes/README.md`, `?? docs/EPISODE_STORE.md` —
the same two files as the original gate. `episodes/README.md` was re-checked but not modified
(confirmed). All specific exclusions honored (`LESSONS.md`/`apply_lessons_delta.py` untouched,
#300's manifest not designed, no capture/consolidation code, retirement layout itself never
chosen anywhere in the current text — both options remain explicitly live in §7).

## Evidence verdict
All claimed side-effects independently reproduced, not taken from either report:
- `git status --short --untracked-files=all` → exactly the two allowed files.
- `python -m pytest tests/ -q` → **1157 passed, 2 skipped, 260 subtests passed in 31.63s** —
  exact match to the baseline.
- `git check-ignore episodes/` → exit **1** (not ignored) — matches the claim.
- `grep -c 'is_episode' docs/EPISODE_STORE.md` → **3** matches (lines 422, 435, 466) — matches
  the implementer's claimed count exactly.

## Code/doc quality
Fowler pass (r6-fowler): 12/12 baseline smells visited, rail exits 0. 10 absent, 1 overridden
(`primitive-obsession`, subordinate to `constraint:markdown-in-git`, same reasoning as the prior
review), 1 **flagged**: `shotgun-surgery` — reduced by the new seam but not eliminated; the
base-enumeration scan feeding the seam is itself still layout-dependent and unaddressed (same
root cause as the finding below).

## Map impact verdict
- **Evidence supports claimed change:** yes, verified independently.
- **Constraints not violated:** yes — markdown-in-git, mechanical-only, retired-is-excluded-not-
  deleted all honored.
- **Notes match the diff:** yes — §2/§7/§8 are the sections actually edited, matching the
  implementer's account; §1/§3/§4/§5/§6/§9/§10 confirmed unchanged and still correct (no
  regression against anything the prior review passed clean).
- **Decision candidates surfaced:** `decision:episode-store-shape` correctly still **not
  resolved**; the new seam name is correctly flagged as scaffolding to carry forward, not a
  resolution.
- **Durable context routed:** yes.

Not independently blocking; folded into the finding below (same root cause the Map Impact's own
"Trust limitations" section claims is now closed, but is not fully closed — see below).

## Reconciliation check
No `docs/architecture/` packet exists in this worktree (confirmed directly). No architecture
divergence beyond what is captured in the finding below.

## Findings, most serious first

### 1. [BLOCKER — High] The membership-predicate seam covers only the per-id filter; the base
candidate-enumeration g3's "enumerate non-retired episodes" needs is still layout-dependent and
unaddressed — so "additive, not a rewrite" is not yet demonstrated for the whole primitive
**File:** `docs/EPISODE_STORE.md`, §7 (closing paragraph) and §8.

**This directly answers the re-review's load-bearing question.** I traced concretely what g3
would have to write against the current text for "enumerate non-retired episodes" (§8). That
primitive needs two things: (a) a **base enumeration** — where do the candidate episode ids/files
to consider come from — and (b) the **per-id filter** — is each one currently in the ordinary-
search set. The new seam, `is_episode_in_ordinary_search(episode_id)`, genuinely and correctly
covers (b). It does **not** cover (a). §8's only description of the mechanism is "a deterministic
scan that... calls the `is_episode_in_ordinary_search()` seam" — the scan's own source is never
specified, and no glob/path pattern is shown for it anywhere in the document. (Confirmed by
`grep -n -i 'scan\|glob' docs/EPISODE_STORE.md`: every concrete glob/scan instance is in §2's
id-sequence-derivation case; none exists for the retrieval primitives §7/§8 describe.)

This is the **same layout-dependence §2 already resolved for its own sibling case**: "the scan
must cover every episode for that run regardless of retirement status... under Option B that is
one glob over `episodes/`; under Option A it is the union of `episodes/active/<run>-*.md` and
`episodes/retired/<run>-*.md`." §7/§8 do not extend that same treatment to the retrieval scan the
new seam was introduced to protect.

**Concretely, what breaks:** if g3 is built literally to this text and a builder picks the most
natural-reading implementation — a flat glob over `episodes/*.md` feeding the seam per id — that
scan silently returns **nothing** the moment Option A binds (files have moved under
`episodes/active/` and `episodes/retired/`, neither of which a non-recursive `episodes/*.md` glob
matches). Fixing that is a **real code change to g3's own scan logic**, not an adapter swap at
the named seam — exactly the failure mode ("additive in letter, a rewrite in effect") the
original BLOCK and this rework were both about, just one level deeper: the rework closed the gap
for the per-id **check**, but not for the **enumeration** that feeds it.

**Fix:** one more short paragraph in §7 or §8, mirroring §2's already-existing treatment —
either (a) state that the base scan itself is layout-agnostic by construction (e.g., a recursive
glob `episodes/**/*.md`, which matches both the flat Option-B layout and the nested Option-A
layout unchanged), or (b) explicitly name the Option A/B union the way §2 does for the id-
sequence scan, and say the base-enumeration source is also part of what g4's binding fixes (in
which case the "additive, not a rewrite" claim needs to be scoped down to acknowledge this). This
is narrow, cheap, and prose-only — it does not re-open the layout decision itself, and should not
meaningfully delay g2/g3.

### 2. [Moderate] No write-side seam is named for g2's writer's actual retire mechanics, even
though the original hunt-preemption question named "the writer's retire op" explicitly
**File:** `docs/EPISODE_STORE.md`, §7, §10.

The rework named a **read-side** seam (`is_episode_in_ordinary_search`) but the document is
silent on how g2's writer (built in the *next* gate, before g4 binds the layout) will physically
execute a retire under either option. Grep for `retire_episode` / `retire(` finds nothing; §10's
list of g2's obligations mentions only the mandatory non-empty reason and single-line
enforcement, not the layout question.

This is **lower risk than finding 1**, not zero: §7's now-fixed worked example already
establishes that the field diff is identical and required under both options, and Option A's
extra step (the file move) is a strict *addition* on top of that diff rather than an alternative
implementation of it — so g2's retire is plausibly additive-by-construction even without an
explicit seam, unlike the read side where grep-vs-directory-check are genuinely alternative
implementations of the same question. But the document does not say this explicitly, where it
took pains to make the analogous read-side point explicit. Recommend a one-sentence note in §7 or
§10 stating that g2's retire writes the field diff only, and the file move (if Option A binds) is
purely additive at g4 — closing the same class of ambiguity the read side just closed.

### 3. [Minor — Low] §9 (cross-worktree) continues to use bare `episodes/<id>.md` notation,
relying entirely on §2's blanket disclaimer rather than a local pointer
**File:** `docs/EPISODE_STORE.md`, §9, lines ~498, ~503.

Not a new contradiction — §2 states "every... example in this document that writes the flat form
`episodes/<id>.md` is illustrating the id, not asserting a settled path," which technically
covers §9's instances too. But a reader who starts at §9 (a plausible entry point — "cross-
worktree sharing" reads as a self-contained concern) has no local pointer back to that disclaimer
the way §7's SS7 gets. Cheap to fix in the same pass as finding 1; not blocking on its own.

### 4. [Observation — carries to g3] Fowler shotgun-surgery flag
Same root cause as finding 1 — resolves automatically once finding 1 is fixed with an explicit
layout-agnostic (or Option A/B-scoped) base-scan treatment.

## What I verified as fine (independently, not taken on either report's word)
- `git check-ignore episodes/` exits 1 — reproduced myself.
- `python -m pytest tests/ -q` — reproduced myself, 1157 passed / 2 skipped / 260 subtests, exact
  match.
- `git status --short --untracked-files=all` — confirmed only the two allowed files touched.
- `grep -c 'is_episode' docs/EPISODE_STORE.md` — reproduced, 3, matches claim.
- Findings 1 and 3 from the prior BLOCK, and the two implementer-self-found §2 instances — all
  read in full against the prior review's exact quoted text and confirmed genuinely fixed, not
  merely reworded.
- No regression: §1 (tracked-path rationale, named seam for `durable_root()`), §2's panel-
  unanimity retraction, §4 (literal partition headings), §5/§6 (worked dispute walkthrough +
  Stratum A table, lifecycle-standing as a separate dimension), §8's no-ranking/no-similarity
  statement and the #300 obligation framed as an obligation not a spec, §9's epic-lease-exception
  and read-only-fence treatment — all re-read in full this round and textually intact.
- `episodes/README.md` re-confirmed clean: uses basename-only notation (`<episode-id>.md`), never
  the ambiguous full bare path form; no layout assumption found.
- No `docs/architecture/` packet exists in this worktree — confirmed directly.
- Fowler pass rail (`verify_fowler_pass.py`) exits 0 against a full 12-smell record for this
  round's diff.

## What I could not check, and why
- Whether a g3 implementer would in fact hit the base-scan gap in finding 1, versus correctly
  inferring the layout-agnostic treatment by analogy to §2 — this is a prediction about future
  work, not directly testable at this gate. My confidence rests on the text being silent on its
  face (no glob/path pattern shown for the retrieval scan anywhere, confirmed by grep), not on
  who reads it next.
- No code exists yet, so I could not execute retrieval directly — this gate is inspection-only by
  design and I did not ask for tests, per the handoff's explicit exclusion.

## Blockers
- Finding 1 above. A narrow, prose-only fix confined to §7/§8 — no design re-litigation, no
  re-opening of the retirement-layout decision itself. Recommend: add one paragraph making the
  base-enumeration scan for g3's retrieval primitives explicitly layout-agnostic (recursive glob,
  or the same Option A/B union treatment §2 already has), so "additive, not a rewrite" is
  demonstrated for the whole primitive (scan + filter), not just the filter half. Small, targeted
  — should not meaningfully delay g2/g3.

## Out-of-scope observations
- Finding 2 (write-side retire-op seam silence) — carry into the same fix pass if convenient;
  otherwise safe to defer to g2/g4 given the lower risk reasoning above.
- Finding 3 (§9 bare-path reliance on disclaimer) — cheap, fold into the same pass as finding 1.
- Finding 4 — informational, resolves automatically once finding 1 is fixed.

## Workflow Feedback
- **Handoff gaps:** None material. The re-review dispatch's "THE LOAD-BEARING QUESTION" section
  was exactly as well-targeted as the original hunt-preemption ask — naming the precise test
  ("trace concretely what g3 would actually write") is what surfaced finding 1, which a looser
  "does this look fixed?" pass would likely have missed, since the per-id seam genuinely does
  look complete on a first read and only breaks down when you ask "where does the id being tested
  come from in the first place."
- **Context rediscovered:** None — the two prior handoffs/results and the doc itself carried
  everything needed.
- **Instructions improvised around:** Same r6-fowler docs-only-diff situation as the prior round
  (no code exists to smell-test). I followed the prior reviewer's precedent of treating
  sections/claims as the analog of methods/classes rather than invoking the co-sign/override
  escape hatch, which again produced a genuinely useful flag (shotgun-surgery, reinforcing
  finding 1) rather than ceremony. Seconding the prior round's suggestion that the skill text
  acknowledge this as a sanctioned reading for a docs-only diff.
- **What would have made this easier:** Nothing structural. One suggestion for future rework
  dispatches on this kind of "close the gap" finding: when a fix introduces a new named
  abstraction (here, the seam), the re-review should explicitly re-run the "what would a builder
  literally write" trace against the abstraction's boundary, not just against the previously-
  flagged sentences — the seam's own definition read as complete in isolation; the gap only
  showed up by asking what calls it and where that caller's inputs originate.

## Return status
`complete`
