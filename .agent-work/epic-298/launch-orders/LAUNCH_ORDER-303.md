# Launch Order: `implementer-303 — issue #303 (epic-298 element E)`

You start cold. Everything you need is pasted here; do not assume you can open anything by reference alone.

## Mission

Issue **#303 — Exercise the confirm-gate refusal (verifier fails closed).**

Verbatim from the issue:

> Present `verify_spec_confirmed.py` with a partially-filled Confirmation block, an empty Disposition cell, and a deleted marker with DRAFT status; confirm each is refused (spec Testing pathways: confirm-gate refusal). Acceptance: each refusal observed and recorded as evidence. **Out of scope: changing the verifier.**

**How it serves the epic.** The confirmed spec names this pathway and its reason plainly:

> **Confirm-gate refusal:** exercised once, cheaply — present `verify_spec_confirmed.py` with a partially-filled Confirmation block and an empty Disposition cell and confirm it refuses both. **A gate claimed as a backstop should be seen refusing.**

That is the whole point: the epic's own confirmation gate is claimed as a mechanical backstop, and a backstop nobody has watched fire is an assumption. You make it fire.

**Context on what the gate protects.** The spec's Confirmation block says the engine cannot cryptographically prove a human made the confirm call, so *"the filled block plus the downstream refusal are the mechanical backstops."* Your job is to show the downstream refusal half actually works.

## The three refusal cases (all three required)

1. **Partially-filled Confirmation block** — e.g. Status set to CONFIRMED but "Confirmed by" or "Date" left as a placeholder/empty.
2. **Empty Disposition cell** — a critic-findings table where at least one Disposition cell is unfilled.
3. **Deleted marker with DRAFT status** — the loud `UNCONFIRMED — DO NOT CUT` marker line removed while Status still reads DRAFT (i.e. the marker was deleted without the status actually being promoted).

For each: the verifier must **refuse** (non-zero exit), and the refusal must be **observed and recorded** — the actual command, the actual exit code, and the actual stderr/stdout message, pasted verbatim.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when overriding.

- decision:do-not-change-the-verifier — you are **exercising** the gate, not fixing it. If a case does **not** refuse, that is a **finding, not a bug for you to patch**: record it, file it to the tracker, and return it. Changing `verify_spec_confirmed.py` is explicitly out of scope.
  `@grade: settled/human · leans all gates`
- decision:fixtures-not-real-specs — build the three cases as **fixtures** (throwaway spec files in your own worktree). Do **not** mutate any real confirmed spec, and do not touch epic #298's own tracker body.
  `@grade: settled/inherited · leans implement`
- decision:refusal-is-mechanically-checked — a refusal proven by a `! <command>` bash-negation wrapper as an engine `command` postcondition is worth more than a self-reported attest. The engine's command postconditions treat exit 0 as pass, so "this command correctly fails" needs the negation wrapper to become a mechanically re-verified check.
  `@grade: settled/inherited · leans implement` (grounded: `lesson:prove-command-fails-postcondition`, from a prior epic that hit exactly this)
- decision:light-review-class — issue #303 is **not** in the epic's full cold-panel class (that class is B, C, F, G, H — the issues that build or change mechanisms). You change no mechanism. A single independent reviewer pass is the correct depth here — but review is **not** skipped: independent agentic review is the standing floor, never a fallback.
  `@grade: settled/inherited · leans review`
- decision:regression-test-if-cheap — if the three cases can be captured as a cheap permanent regression test alongside the existing suite, do it; the spec's point is that the backstop stays proven, not that it was proven once. If that turns out to cost more than the exercise itself, record the evidence and say so.
  `@grade: guess · leans implement · settle: try it; if the fixture harness exceeds ~an hour, record the one-time evidence instead and note why`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable, reported with the same rigor as a win. Two specific shapes to expect:

- **The verifier already has tests covering all three cases** → say so, paste them, and report the exercise as already-satisfied-at-HEAD. That is an honest null, not a failed issue.
- **A case does not refuse** → that is a *real finding about the epic's backstop*, arguably the most valuable outcome available here. File it and return it; do not fix it.

Per scoped-nulls doctrine, every null states what was tested **and what was not**.

## Inherited Latitude

**You may decide** (log it, proceed): fixture design and file layout inside your worktree; test strategy; whether the regression test is worth its cost (see the graded guess above); filing issues to the tracker (`gh issue create` is **pre-cleared** — file findings directly, never bank them worktree-locally for harvest).

**You must float to the Admiral**: any change to the verifier itself (out of scope by ruling); any scope change; anything that would touch a **two-bin routing ruling** (whether a doctrine item is prose-with-tripwire or mechanism-owned — Tommy's, always); a case that fails to refuse **and** looks like it needs a design change rather than a filed issue.

**Out-of-taxonomy always escalates** with one line on why it fit no class.

## File Ownership

Your working notes file: **`notes-303.md`**, in your own worktree, sole writer this wave.

> Name it `notes-303.md`, **never** `findings-303.md`. The harness `Write` tool refuses any path whose basename contains "findings" ("Subagents should return findings as text, not write report files") — a guard aimed at unprompted report-dumping, which cannot tell that this file was deliberately assigned. Three agents hit it in one epic and each worked around it with a shell heredoc. The guard is not ours to change; the word is.

Do **not** leave working notes at the repo root of the main checkout (a prior epic left `notes-261.md`/`notes-269.md` there permanently — filed as issue #278). Keep it inside your worktree.

**Fences:** `verify_spec_confirmed.py` is **read-only** to you. Two concurrent siblings own other code — #300 (projection generator + manifest) and #301 (episode record + store); do not edit their surfaces.

## Workspace

**Absolute worktree path:** `C:/Programs/constellation-skills-wt/298-303`
**Branch:** `epic-298/303` · **Base commit:** `b69e6c8` (main, verified fresh at dispatch)
**Created by:** `git worktree add -b epic-298/303 ../constellation-skills-wt/298-303 main`

First step, before any git operation: run `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/298-303` — it must exit 0, proving you are in your own worktree and not the shared checkout. Paste its output into your return report.

**Windows worktree hazard (grounded, do not skip):** the Agent-tool `isolation:"worktree"` flag is a **silent no-op** on this platform. Your isolation comes from the explicitly-provisioned worktree above, which is why the verification command is mandatory rather than ceremonial.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not a local merge that would diverge your worktree from main).

## Inherited Context

**Engine drive is mandatory.** Load `constellation-implementer` and drive its plan through the checklist engine to completion. Work the engine never saw did not happen. Drive the engine from **this repo's own vendored** `scripts/checklist_engine.py` — this repo *is* the constellation-skills source, and the globally-installed copy can diverge from the repo's own; the repo's copy governs.

**Active lessons relevant to this mission** (from `.agent-work/LESSONS.md`):

- `lesson:prove-command-fails-postcondition` — directly load-bearing for you. A gate that must prove a command **correctly fails** does not fit the engine's command-postcondition semantics (exit 0 = pass). A `! <command>` bash-negation wrapper as the postcondition's `command` field makes "the guard fired" a mechanically re-verified engine check instead of a self-reported attest. This lesson came from one Commander improvising it once; you are plausibly its second data point, so **report in your workflow feedback whether it worked for you** — that observation has value beyond this issue.
- `lesson:verify-launch-order-claims-against-code` — **verify this order's named claims against the current code before planning.** Grep for `verify_spec_confirmed.py` and read what it actually checks; a named-but-nonexistent check is a naming slip in this order, not a build task, and existing test coverage of all three cases is an honest null. Recurred across two epics (5 mentions, 2 confirms).
- `lesson:round-trip-tests-prove-artifacts-not-parsers` — a test that runs the verifier over the **real shipped spec artifacts** proves those artifacts are clean; it does **not** prove the verifier is correct. Your whole mission is the adversarial-fixture half of this lesson: fixtures authored to make the tool return a WRONG answer (silent PASS on invalid input) are exactly what catches the class a round-trip misses.

**Platform / technical invariants:**

- **Windows shell:** Bash tool for POSIX sequences, PowerShell for cmdlets — never heredocs into PowerShell. Engine `command` postconditions run under a POSIX shell; author them in POSIX form (this matters for your `!` negation wrapper).
- **PR bodies:** write the body to a temp file and use `gh pr create -F <file>`. Never a heredoc or PowerShell here-string for `--body` (here-strings work for `git commit -m` only).
- **Never hand-edit any engine JSON** to change state — the engine owns that file and stamps the provenance. Consume state via the engine's `current` output.
- **Escalating upward is always legitimate.** A delegate is not a replacement. If you need context this order does not cover, return and query the Admiral — it answers and continues you. Do not guess past the edge of your latitude to avoid the ask.

**Project doctrine deltas** (`docs/agents/ORCHESTRATOR_CONTEXT.md`): workflow mechanisms and verifiers are a **strengthened durable system** — targeted automated verification plus the relevant broader suite; name both commands in your evidence. Pushes/PRs/merges to `main` are **pre-cleared** for you under this order for green + reviewed work on `epic-298/*`.

## Pre-empted Steps

- **Epic-level context is established** — the epic intent, the spec's confirm-gate pathway text, and the three required cases are pasted above. Cite this launch order rather than re-deriving them.
- **The review class is already set** (single independent reviewer, not the full cold panel) — don't re-derive it from consequence analysis.
- **The out-of-scope boundary is already ruled** (do not change the verifier) — don't re-litigate it.

Everything else — your own plan, execution, and verification — you drive normally.

## Data Locations

- Main checkout (untracked inputs your worktree does **not** contain): `C:/Programs/constellation-skills`
- `docs/agents/` exists in the main checkout and is **untracked** — it will **not** be present in your worktree. Copy in what you need rather than reaching into the main checkout.
- `.agent-work/` at the main checkout is **read-only to you** while the Admiral's epic lease is active. Your own `.agent-work/` resolves to your **worktree** root; that is expected under an epic, not a bug.
- Epic latitude contract (context, not yours to edit): `C:/Programs/constellation-skills/.agent-work/epic-298/LATITUDE_CONTRACT.md`

## Budget

- **Model tier (required):** **Sonnet.** This is bounded, well-specified work — three fixtures, three observed refusals. Escalate to Opus only if the mission turns out to hide a real design question, and say so when you do. **Never dispatch above Opus.** Name a model explicitly on any dispatch you make.
- **Compute/time, session-window:** you are the smallest of three concurrent wave-0 dispatches. This should be a short mission; if it is ballooning, that is itself a signal worth returning.

## Stop Conditions

Stop and return when:

- A case **fails to refuse** and fixing it would mean changing the verifier (out of scope — file and return).
- The exercise is already satisfied at HEAD by existing tests (honest null — a complete deliverable).
- A decision outside your inherited latitude is required.
- Budget crossed, or you need context this order does not cover and cannot safely proceed without.

Asking up is always sanctioned.

## Return Shape

Write your result artifact **before** going idle — an idle notification with no artifact reads as stalled, not done. Deliver first; completion is judged from what you produced, not from a message that arrives after you have gone quiet.

Write your verdict to: **`C:/Programs/constellation-skills-wt/298-303/.agent-work/verdict-303.md`**

Required contents:

1. **Verdict** — shipped / honest-null / blocked, in one line, then the substance.
2. **Evidence** — for **each of the three cases**: the fixture, the exact command run, the exit code, and the refusal message pasted verbatim. Plus the test commands and exit codes, and the PR number and merge state.
3. **`verify_worktree_isolation.py --here` output** — the matched worktree path, pasted.
4. **Map impact** — anything the architecture map should now say that it does not (likely little for this issue; say so if so).
5. **Triage candidates** — file them to the tracker directly (pre-cleared) and list the issue numbers; do not bank them worktree-locally.
6. **Workflow feedback** — friction, misfitting instructions, engine defects. **Include specifically whether the `! <command>` negation-wrapper technique worked as a postcondition** — that observation is a second data point on a banked lesson. Reporting misfit is compliance, not deviation.

Also stage your durable trio worktree-locally at `.agent-work/staged-feedback/303/` (lessons-delta, `AGENT_FEEDBACK.md` entry, `CONSTELLATION_FEEDBACK.md` exports) so the Admiral can harvest it before the worktree is swept.
