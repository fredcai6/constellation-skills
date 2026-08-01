# Latitude Contract: `epic-226`

Status: **CONFIRMED 2026-07-24 by Fred** — "all good go", with one amendment folded
in (see PR-2 and the CI rows: GitHub Actions minutes are unavailable, so #229's CI is
authored but verified locally). Every `[REC]` line below is now live as written.
Interrogation record: `.agent-work/epic-226-latitude/INTERROGATION_RECORD.json`
(`verify_interrogation.py` exit 0, 10 questions, sign-off captured).

## Epic Intent
Spend agent effort on the actual problem instead of the scaffolding, and seed the
step-back capability. Cut from the CONFIRMED spec "design-thrust: step-lighter,
step-back" (explorer run `explore-design-thrust`, confirmed 2026-07-24 by Fred;
3-lens cold critique, 30/30 findings dispositioned).

The outcome that must not be violated: **the epic is a batching convenience, not a
coordination claim.** Items A–F are independently merited and may land in any order
except the single encoded edge (C blocks F). No cross-issue coupling may be invented
to justify serializing them.

## Success Shape
Six dispatchable issues each merged green with their own stated acceptance met:

| Issue | Wave | Substance | Acceptance anchor (from the issue) |
|---|---|---|---|
| A #227 | 0 | engine answerability: `current` as complete gate briefing, recovery-bearing REFUSED, over-read instrument | 906-suite green + golden-output tests per state/refusal family; INV-1 oracle, INV-2 no-subprocess, INV-3 enumeration tests; `measure_overread` baseline + post-change delta committed |
| B #228 | 0 | install: resolve the Python launcher at install time | installer test asserts stamped interpreter resolves; simulated `py`-less install names a working interpreter; install/fingerprint tests green |
| C #229 | 0 | CI: gate merges on the 906-test suite + engine coverage floor + skip-guard | **AMENDED (see PR-2b):** workflow authored correctly, but proven by running its own command set **locally** — a seeded failing test makes the suite command exit non-zero; a git-less run makes the skip-guard exit non-zero; the coverage floor is measured and documented with its command. No GitHub run is required or claimed. |
| D #230 | 0 | planning: `@grade` fixedness schema + `grade_lint.py` | grade_lint unit tests over seeded-violation fixture plans; template round-trips |
| E #231 | 0 | prototyper: three-valued verdicts, captured-to-worktree, commander→prototyper seam | prototyper template round-trip (verdict + disposition enums accepted by workbench close); seam paragraph lands in commander understand doctrine |
| F #232 | 1 | hardening: `_glob_to_regex` property tests, #205 atomic eval meta, doc-drift sweep | **AMENDED (PR-2b cascade):** new tests green under **C's workflow command set run locally**, with zero unexpected skips; grep for the stale phrases returns nothing |

**#233 (G) and #234 (H) are NOT part of the success shape.** They are shaped design
threads carrying a standalone refusal marker, routed for a future human-led explorer
pass — same status as #139. Dispatching either is a contract violation.

**Honest nulls are complete deliverables.** A Commander that measures a headline
mechanism as already-shipped, or a sub-fix as unneeded, returns a measured negative
with its scope stated (what was tested, what was NOT) and that is a **successful**
close, not a failure. This is live doctrine here specifically because
`lesson:verify-launch-order-claims-against-code` is active in the inbox with two
prior data points — every launch order in this epic carries the verify-before-plan
clause.

## Checkpoint Protocol
`[REC]` **Cleared autonomous through wave 0; stop-and-present at the wave-0/wave-1
boundary; then cleared through to closeout** (closeout's own acceptance step is the
final human gate regardless).

What reaches the user at a checkpoint: plain-English summary of what merged and what
it changes, any rulings made, any escalations pending, and evidence on demand — not
a wall of diffs.

## Decision Classes

| Class | Disposition |
|---|---|
| Architecture / structural change | `[REC] surfaced` — beyond what the issue already specifies |
| Scope change: narrowing, or an honest-null return | `[REC] delegated` (logged as RULING) |
| Scope change: adding scope, or dropping an issue outright | `[REC] surfaced` |
| Merge to main | `[REC] delegated` on green tests + reviewer APPROVE |
| Issue filing / closing | `[REC] delegated` for the epic's own issues; new-issue filing for out-of-scope discovery also delegated (Triage drains them) |
| Fix-now triage (bounded fix applied immediately, not filed) | `[REC] delegated`, logged as RULING |
| Spend / budget / model tier | `[REC] delegated` within the tiers set below; a tier escalation beyond them is surfaced |
| Production defaults / user-visible behavior | `[REC] surfaced` |
| **Doctrine / shipped-template edit** (project-specific class) | `[REC] delegated when the edit is the one its issue already specifies` (A's two `global-everyone.md` riders, D's planning-template tag convention, E's commander understand paragraph); **surfaced** if a Commander wants to reshape doctrine beyond its issue |
| **Self-hosting engine change** (project-specific class) | `[REC] delegated but gated` — see Pre-Rulings PR-1; a *failed* live-spine probe escalates immediately |
| **Out-of-taxonomy** | **always escalates, with one line on why it fit no class** |

- **Apply a lesson / fold doctrine** — `[REC] delegated` for the four active inbox
  lessons' routine handling, **but** a graduation that reshapes project doctrine
  (`.md` / `.template.*`) still carries `authority=human` on its apply op per the
  closeout imperative. Constellation-scoped lessons are always exported, never
  silently confirmed.

## Permission prerequisites

| Delegated class | External actions implied | Pre-clearance or fallback |
|---|---|---|
| Merge to main | `gh pr merge`, `git push`, `git worktree add/remove` | No standing allowlist entry exists. **Fallback (recorded now, per the worked example):** on a classifier veto, take one human approval in the moment and **batch the remaining equivalent merges to the next checkpoint** rather than re-litigating each. |
| Issue filing / closing | `gh issue create`, `gh issue close`, `gh issue comment` | Same fallback shape: one approval, then batch. |
| CI work (C #229) | writing `.github/workflows/*.yml`; **no** `gh run`/Actions execution | **SETTLED BY PR-2b, not a fallback:** Actions minutes are unavailable, so the Commander authors the workflow and proves it by running its command set locally. It does not trigger, poll, or report a GitHub run. |
| Self-hosting engine change (A #227) | read-only `current` against the LIVE `.agent-work/epic-226/spine.json`; mutating verbs against a **copy** only | Pre-cleared here explicitly: the Admiral runs these probes itself, in the main checkout, before merging A. Never a mutating verb against the live spine from a test. |
| Doctrine / template edit | writes under `skills/_shared/global-*.md` and `skills/*/templates/` | Pre-cleared for the issue-specified edits. **Canonical-source rule:** doctrine edits go to `skills/_shared/global-*.md`, NEVER to `skills/<role>/references/global-*.md` (install-time copies that `install_constellation.py` regenerates — an edit there is silently overwritten). |

## Float-Up Routing
When a Commander floats — a `user-decision` **or a context query**: for a decision,
adjudicate inside delegated classes and log a RULING; escalate surfaced classes and
out-of-taxonomy to Fred. For a **context query**, answer from epic knowledge and
continue the Commander (return-and-relaunch with context intact), reaching Fred
out-of-band only when the answer is beyond my knowledge or latitude.

Per-class nuance: a Commander floating "issue X's headline mechanism appears already
shipped" is **not** a decision — it is the expected honest-null path. Rule it
delegated, confirm the evidence against the code myself, and log it.

## Comms
`[REC]` Plain English by default, technical depth on demand. No invented project
dialect in anything Fred reads; role vocabulary stays in agent-to-agent artifacts.

## Budget / Model Parameters
`[REC]` **Commanders:** Opus for A #227 and D #230 (the two design-heavy issues —
A rewrites the engine's whole output surface behind three invariants, D introduces a
grammar plus a linter plus executor doctrine). Sonnet for B #228, C #229, E #231,
F #232. **Crew:** Sonnet throughout. **No Fable at any tier** (standing rule).

**Usage-limit budget.** Wave 0 as five concurrent Commanders + crew draws the shared
pool hard. `[REC]` Launch all five; if the pool shows strain, the fallback is a 3-then-2
split (A, C, D first — C unblocks wave 1, A and D are the long poles — then B, E).
If a limit reset is near, defer the next dispatch **past** the reset rather than
launching into it.

## Pre-Rulings
Foreseeable ambiguities ruled in advance; each overridable by Fred at any checkpoint.

- **PR-1 (self-hosting, mandatory).** A #227 rewrites `checklist_engine.py` — the live
  engine driving this very spine. It is built and reviewed in an isolated worktree.
  **Before merge**, the Admiral verifies: (a) read-only `current` against the LIVE
  `.agent-work/epic-226/spine.json` exits 0 under the new engine; (b) a mutating verb
  (`advance`) against a **COPY** of that spine behaves sanely (refuses or succeeds, does
  not crash). Only then merge, sync the checkout, and drive remaining advances on the
  new engine. A failed probe **escalates immediately** — it does not get worked around.
- **PR-2 (no CI until C).** Wave-0 merges cannot gate on GitHub status checks because
  none exist yet. They gate on a locally-run `pytest tests/` exit code captured in the
  Commander's return, re-verified by me on the merged main.
- **PR-2b (Actions unavailable — HUMAN AMENDMENT, 2026-07-24).** Fred: *"my github actions
  are used up, so let's make the ci but only expect it to run locally."* Therefore:
  - C #229 **authors** the workflow file correctly (a real, valid, reviewable
    `.github/workflows/*.yml` a future runner would execute), but its **acceptance evidence
    is local**: run the exact command set the workflow invokes and demonstrate each guard
    fires — seeded failing test ⇒ non-zero exit; git-less environment ⇒ skip-guard non-zero,
    not a silent green; coverage floor measured and documented with its command.
  - **No Commander waits on, polls for, or claims a GitHub Actions run.** A verdict asserting
    "CI green" without a local command transcript is invalid evidence.
  - **Cascade:** PR-2's local-gating rule extends to **wave 1** as well. F #232's "green in
    CI" acceptance reads as "green under C's workflow command set, run locally."
  - The pre-check #229 names ("verify windows-latest provisions git-bash") cannot be settled
    empirically without a run — it is answered from GitHub's documented runner image spec and
    recorded as a **documented assumption**, not a measurement. Say which it is.
  - Standing note: this repo is **public**, and public repos normally get unlimited free
    Actions minutes, so the cap is more likely a spending-limit/account setting than a true
    cap. Flagged to Fred; his constraint governs regardless. If Actions later becomes
    available, the workflow is already correct and needs only to be run.
- **PR-3 (batched re-verification).** Wave-0's five merges are batched: merge sequentially,
  then re-run the full suite **once** on the final merged main in a fresh worktree, rather
  than per-PR. Governed by the unchanged-tree evidence contract.
- **PR-4 (worktree isolation is not free).** The Agent-tool `isolation:"worktree"` flag is
  a silent no-op on Windows. Every Commander gets a worktree I provision with an explicit
  `git worktree add`, logged in the ADMIRAL_LOG, and the wave is gated on
  `py scripts/verify_worktree_isolation.py <all paths>` exiting 0 before launch.
- **PR-5 (two issues touch `checklist_engine.py`).** A #227 (rewrite) and F #232(a)
  (`_glob_to_regex` property tests) both land in that file — but F is wave 1, strictly
  after A merges, so there is no concurrent-edit collision. F's Commander rebases onto
  post-A main and writes its property tests against the **new** engine surface.
- **PR-6 (canonical doctrine source).** Any doctrine edit targets `skills/_shared/global-*.md`.
  A launch order that names `skills/<role>/references/global-*.md` as an edit target is
  wrong and gets corrected before dispatch.
- **PR-7 (verify the launch order against the code first).** Active inbox lesson
  `verify-launch-order-claims-against-code` (2 prior data points): every Commander greps
  the named symbol/mechanism against current code BEFORE planning. A headline mechanism
  already shipped is an honest null; the live defect may be an unnamed sibling.
- **PR-8 (#219/#220 threads stay live).** #220 was surgically rewritten and #219 commented
  at filing time. A Commander that finds adjacent #220/#219 work does NOT absorb it — it
  files or comments and stays in its lane. Only A's declared #220 absorptions (items 3, 5,
  and 6's by-reference sub-bullet) are in scope.

## Expiry
`[REC]` The wave-0/wave-1 checkpoint, **or** 24h from confirmation, whichever comes
first. Crossing it forces a contract-refresh decision before further dispatch.

## Confirmation

**2026-07-24 — confirmed by Fred (human, at the keyboard):** *"all good go. note my
github actions are used up, so let's make the ci but only expect it to run locally"*

All six recommendations accepted as drafted, plus the Actions amendment recorded above
as **PR-2b** (and cascaded into C #229's and F #232's acceptance rows). Recorded as
`user-decision` evidence on the spine's `latitude` step. Interrogation record:
`.agent-work/epic-226-latitude/INTERROGATION_RECORD.json` — `verify_interrogation.py`
exit 0, sign-off captured, survey consolidated `RESOLVED`.
