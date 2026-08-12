# Triage candidates from g1 (#467)

Logged by `commander-w4-467-c` at `g1-integrate`, per the gate imperative "Log out-of-scope finds as
triage candidates." **None of these are filed** — filing is the Admiral's/human's call, and this run
has no filing authority. Each records what was observed and by whom, so a later triage pass does not
have to re-derive it.

Sources: the g1 REVIEW_RESULT (`crew-handoffs/g1-reviewer-result.md`), the g1 IMPLEMENTER_RESULT, and
my own verification at `g1-integrate`.

---

## TC-1 — A check that cannot PASS: `r6-fowler` in `REVIEW_SURVEY.template.json`

**Reviewer W1, reproduced by the reviewer; not independently re-run by me.**

The template ships `r6-fowler`'s c1 command as
`python scripts/verify_fowler_pass.py <fowler-pass-record-path>`. A POSIX shell parses the literal
`<...>` as a redirect from a nonexistent file, so the check **always fails**. The reviewer SKILL.md
tells the reviewer to fill the command in before recording, but **no engine verb can**: `amend`
refuses (`amend applies to gated checklists`) and `attest` refuses (`c1 is engine-checked; cannot
attest`). The reviewer force-waived it with the real command and its real exit 0 recorded in the
waiver; the Fowler pass itself genuinely passed.

**Why this matters beyond one survey.** Epic #418 has been hunting checks that **cannot fail**. This
is the mirror: a check that **cannot pass**. Both are invisible for the same reason — the outcome is
determined by the check's construction rather than by the world — and a forced waiver is the only
exit, which trains agents to force-waive. Reviewer's suggested fix: fill the command at survey
**instantiation** (before `claim`), or allow `amend` on surveys.

**Class:** `evidence_only` for #467; a real defect in a shipped template, owned by whoever owns
`REVIEW_SURVEY.template.json`.

---

## TC-2 — The same species, in this run's own frozen plan: `g1-integrate` c3

**Mine, found at `g1-integrate`. Floated to the Admiral; unresolved at the time of writing.**

`g1-integrate` c3 is `artifact: review-result, match {verdict: "APPROVE"}` — the literal string. The
reviewer handoff authored at the g1 seam prescribed a **different vocabulary**: `ACCEPT` /
`ACCEPT WITH FINDINGS` / `REJECT`, and said in terms that `ACCEPT WITH FINDINGS` is the healthy
outcome and a bare `ACCEPT` would itself read as a check that could not fail. The reviewer obeyed the
handoff and returned `ACCEPT WITH FINDINGS` with 0 blocking findings.

So the **frozen plan and the frozen handoff disagree on the word**, and c3 cannot pass as written
without either fabricating an artifact or waiving.

**The generalizable defect:** an `artifact`-kind postcondition that matches on a **free-text verdict
string** couples the gate to a vocabulary defined in a *different* document, with nothing checking
the two agree. The plan author and the handoff author were the same agent, one step apart, and it
still diverged. Candidate fix directions (not chosen here): a canonical verdict enum the templates
share; or `match` on `blocking_findings == 0` rather than on a verdict word.

**Class:** `evidence_only` for #467's done-conditions; `blocks_current_wave_exit` for this gate until
the Admiral rules.

---

## TC-3 — The trip protocol sweeps disposable evidence into permanent history

**Reviewer N1, re-derived and **re-attributed** by me.**

The reviewer found that the g1 IMPLEMENTER_RESULT's §Scope claim — "Files changed: none under version
control … deliberately not `git add`ed" — is **false at HEAD**, and that the consequence is real:
`red-repro/scratch/**` is tracked, so every repro re-run dirties tracked files, which
`decision:red-leaves-no-residue` rules out.

**Confirmed in my hands:**
- `git ls-files -- .agent-work/issue-467-trip-semantics/red-repro | wc -l` → **29**
- `git check-ignore -v .../red-repro/repro_431.py` → exit **1** (not ignored)
- my own `--all` re-run then left **25 modified tracked files** (`git diff --name-only -- .../red-repro | wc -l`)

**But the attribution is different from the reviewer's reading.**
`git log --oneline --diff-filter=A -- .../red-repro/repro_431.py` → **`62f564c7`**, and
`git show --stat 62f564c7 -- .../red-repro` → **29 files changed, 1953 insertions**. All 29 entered
tracking in the **predecessor Commander's seam-commit at the trip**, not through any `git add` by the
implementer. The implementer's claim was **true when written**; the handoff protocol falsified it.

**Why this is the interesting part.** "Commit at the seam before handing off" is doctrine, and it is
what makes a trip lossless. Its unpriced side effect is that it commits *everything* in the work
area, including artifacts a gate deliberately kept local-only and disposable. The two rules —
commit-at-the-seam and leaves-no-residue — are in direct tension, and nothing currently notices.
The implementer handoff even carried a Deliverable Path Check saying not to commit it; the Commander
committing at a seam does not consult that.

**Class:** `evidence_only` for #467. The remedy (untrack `red-repro/**`, correct the sentence) is
outside the frozen plan and was floated, not done.

---

## TC-4 — `why_ref=<why-id>` attaches with exit 0 and does not release HARD

**Found by the g1 implementer, independently corroborated by the reviewer's PROBE 3, and
independently corroborated again by `TRIP_OBSERVATION.md` item 4.**

Copy-pasting the refusal's own literal `why_ref=<why-id>` placeholder **attaches with exit 0** and the
following `advance` is **still refused** — a silent no-op on the exact command the engine prints at
the agent. The reviewer's PROBE 4 shows the real id is not recoverable from `current` or from the
refusal text, so an agent following the printed instruction has no way to get it right.

**Already in the plan:** `g2(d)` fixes this by emitting the concrete why-id. Recorded here because it
now has three independent confirmations and because the *shape* — an engine printing a command that
fails silently when followed literally — is worth a look wherever else the engine prints commands.

**Class:** `evidence_only` (already owned by g2).

---

## TC-5 — Gauge misattribution at a handoff: many keys, one path

**`RESUME_OBSERVATION.md` (predecessor), with a material correction from me — see
`RESUME_OBSERVATION.md` §"Second resume".**

`.agent-work/.spine-rail-binding.json` keys bindings per-agent (`session_id#agent_id`, #419) but every
key resolves to one **spine-derived** `gauge.json`. Last writer wins, so at a live handoff the
predecessor's reading can be attributed to the successor.
`gauge_writer_hook.handle_post_tool_use`'s `ambiguous-binding` guard fires on *one key → many paths*
and is blind to the mirror case, *many keys → one path*.

**My correction:** it does **not** make the round trip loop permanently. It bites only while the
tripped predecessor is still taking tool calls. Once it goes quiet the successor's own reading
overwrites and the band releases unaided. I observed exactly that.

**Fix direction (recorded, not implemented):** the engine already holds a **lease** naming the spine's
owner. A gauge writer that declines to write for an agent not holding the lease would close this with
a mechanism that already exists.

**Class:** `evidence_only` for #467's done-conditions; DC5 evidence.

---

## TC-6 — Smaller reviewer findings, recorded so they are not lost

- **N2** — the implementer result pins a stability claim to `gauge.json`, a git-ignored file the
  harness hook rewrites continuously. A later reader who checks it finds a different value and
  wrongly concludes someone tampered. Inherited rule: do not report a read of a continuously-rewritten
  file as a stability property.
- **N3** — the most load-bearing structural sentence ("a further `advance` would be permitted") is
  narrated prose, not an assertion. It is what makes #431 an instruction-conformance defect rather
  than a lock, and g2–g4 lean on it. The reviewer's PROBE 2 verified it.
- **N4** — Face A's counterfactual varies gauge **presence**, not gauge **value**. The reviewer's
  PROBE 1 (gauge present at 0.02) closes the gap and the RED survives. Face B already had the
  ingredient.
- **N5** — `why_ref_from_current()` (repro lines 228–232) is dead code, never called, and implies the
  why-id is recoverable from engine output when PROBE 4 shows it is not. Deleting it would stop a
  later reader concluding TC-4 is already solved.
- **N6** — under the fix, `expect_refusal=True` raises rather than recording an assert-fail, so Face A
  would report only its first flip. Face B's shape (assert on the refusal text) is better.
- **W2** — the reviewer SKILL.md says `advance` each check; a survey refuses with
  `advance is for gated checklists; use record`. Cost one round trip.
- **W3** — the handoff's question 4, `git diff --stat -- scripts tests`, is **worktree-only**: a commit
  on the branch that edited `scripts/` would sail through it while "the RED is at unmodified HEAD" was
  false. Future handoffs should require `git diff --stat main...HEAD -- scripts tests` alongside it. It
  came out clean here — I ran both.
- **W5** — the handoff asked the reviewer to verify a counterfactual "differs only in the gauge" but
  gave no sanctioned way to compare two spines. It wrote a normalized-JSON differ. A one-line recipe
  would be reusable at every gate claiming a counterfactual.
