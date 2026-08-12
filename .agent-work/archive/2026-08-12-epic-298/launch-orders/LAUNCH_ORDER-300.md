# Launch Order: `commander-300 — issue #300 (epic-298 element B)`

Commanders start cold. Everything you need is pasted here; do not assume you can open anything by reference alone.

## Mission

Issue **#300 — Projection generator + manifest: design-it-twice, then implement.**

Verbatim from the issue:

> Implement the minimal projection substrate and its manifest. The substrate (spec B2, non-conditional): a versioned script that deterministically assembles agent-facing context from canonical Markdown, so every doctrine change produces a reviewable diff; the spine's existing gate-note loading is the partially-grounded starting point (Assumption 5) — extend it, do not build a parallel one. The manifest: for anything deterministically assembled into agent context, record what was loaded and from which canonical revision, as a free byproduct of assembly (spec B2). Design-it-twice (REQUIRED by the spec for this load-bearing interface): 3+ parallel interface designs under distinct constraints, compared on depth/locality/seam/testability, before fixing the schema. Acceptance: manifest produced on every deterministic assembly; revision identity present; consumable as the episode record's context field. Out of scope: access tracing, transcript analysis.

**How it serves the epic.** Epic #298 is one closed vertical slice proving Constellation skills can natively enter, consume, and improve a shared, observable knowledge substrate. Your manifest is one of the epic's **two load-bearing interfaces** (the other is the episode record, issue #301, running concurrently). The manifest is the epic's honest observability instrument: it answers *what was made available to an agent, at which revision* — delivery, not use. Issue #307 later pairs it with run-transcript ordering to produce the map-first verdict, and issue #301's episode record consumes it as the episode's context field.

**Governing spec principle (B0.1, the stochastic boundary):** stochastic work happens *upstream of canon*; between canonical truth and an agent's active surface **every transformation is deterministic and attributable**. Your generator sits entirely on the deterministic side. No semantic routing, no LLM inference at assembly time.

## Prior-Wave Verdicts (pasted)

None — you are in wave 0. Two concurrent siblings you must not collide with:

- **#301 (episode record + durable store)** is running concurrently in its own worktree. Your manifest must be **consumable as the episode record's context field**, but you do **not** design or edit the episode record. Define your manifest's shape on its own merits and state its obligations clearly enough that #301 can consume it. If you believe you need to change something on #301's side, that is a **float to the Admiral**, not a cross-edit.
- **#303 (confirm-gate refusal exercise)** touches `verify_spec_confirmed.py` read-only. No overlap expected.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when overriding.

- decision:design-it-twice-required — you run design-it-twice on the manifest interface: **3+ parallel candidate designs, each under one named distinct constraint**, compared on depth / locality / seam placement / testability, converging to one opinionated recommendation or named hybrid (never a menu). This is required by the spec for this interface and is **not** skippable as a trivial case.
  `@grade: settled/inherited · leans plan`
- decision:convergence-is-human — you generate and compare the candidates; **the Admiral surfaces the convergence choice to Tommy.** Float your comparison with a recommendation; do not self-converge and proceed.
  `@grade: settled/human · leans plan`
- decision:extend-dont-parallel — extend the spine's existing gate-note loading; do not build a second parallel assembly path. One canonical path (inherited doctrine: "one canonical path; no speculative abstraction").
  `@grade: settled/inherited · leans implement`
- decision:markdown-in-git — canonical storage stays Markdown in git. No database, no query language, no new backend. Tommy's explicit direction in the confirmed spec.
  `@grade: settled/human · leans plan,implement`
- decision:full-cold-panel — issue #300 is in the epic's **full cold-panel review class** (spec B0.4: issues B, C, F, G, H build or change mechanisms). You may **not** default to a light single-reviewer pass. Independent agentic review at full panel depth is the floor here.
  `@grade: settled/inherited · leans review`
- decision:determinism-is-the-acceptance-test — the projection's determinism must be exercised, not asserted. The spec's named pathway: rebuild from a **clean checkout in a second environment**, with a declared exclusion set for legitimately varying fields (timestamps, run ids) kept **separate from content**. Windows line endings, filesystem ordering, and locale are the real irreproducibility sources on this corpus — design the test to catch them.
  `@grade: settled/inherited · leans implement,review`
- decision:no-foreclosure — the manifest must not foreclose the Stratum A truth model (assertions with source, supporting/challenging evidence, qualitative strength). You are not building it; you must not make it harder to build over your record later.
  `@grade: settled/inherited · leans plan`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win. If the design-it-twice comparison shows the minimal-extension candidate is the right answer and there is far less to build than the issue implies, **say so plainly** — that is a result, not a shortfall. Per scoped-nulls doctrine, every null states what was tested **and what was not**.

## Inherited Latitude

**You may decide** (log it, proceed): implementation structure inside the chosen design; test strategy and fixtures; file layout within the projection substrate; bounded fix-now triage of defects you find in the code you touch; filing issues to the tracker (`gh issue create` is **pre-cleared** — file findings directly, never bank them worktree-locally for harvest).

**You must float to the Admiral**: the design-it-twice convergence choice (surfaced to Tommy — see pre-rulings); any change to the manifest's obligations toward #301's episode record; any scope change (adding, dropping, or re-scoping work); any user-visible/production default change; anything that would touch a **two-bin routing ruling** (whether a doctrine item is prose-with-tripwire or mechanism-owned) — those are Tommy's, always.

**Out-of-taxonomy always escalates** with one line on why it fit no class.

## File Ownership

Your working notes file: **`notes-300.md`**, in your own worktree, sole writer this wave.

> Name it `notes-300.md`, **never** `findings-300.md`. The harness `Write` tool refuses any path whose basename contains "findings" ("Subagents should return findings as text, not write report files") — a guard aimed at unprompted report-dumping, which cannot tell that this file was deliberately assigned. Three agents hit it in one epic and each worked around it with a shell heredoc. The guard is not ours to change; the word is.

Do **not** leave working notes at the repo root of the main checkout — a prior epic left `notes-261.md`/`notes-269.md` there permanently (that is filed as issue #278). Keep it inside your worktree and let it die with the worktree after harvest.

**Fences:** you are the sole writer of the projection substrate and its manifest code/tests. Do not edit `.agent-work/LESSONS.md` by hand under any circumstances (see Inherited Context).

## Workspace

**Absolute worktree path:** `C:/Programs/constellation-skills-wt/298-300`
**Branch:** `epic-298/300` · **Base commit:** `b69e6c8` (main, verified fresh at dispatch)
**Created by:** `git worktree add -b epic-298/300 ../constellation-skills-wt/298-300 main`

First step, before any git operation: run `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/298-300` — it must exit 0, proving you are in your own worktree and not the shared checkout. Paste its output into your return report.

**Windows worktree hazard (grounded, do not skip):** the Agent-tool `isolation:"worktree"` flag is a **silent no-op** on this platform. Your isolation comes from the explicitly-provisioned worktree above, which is why the verification command is mandatory rather than ceremonial.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not a local merge that would diverge your worktree from main).

## Inherited Context

**Engine drive is mandatory.** Load `constellation-commander-delegated` and drive its spine through the checklist engine to completion. Work the engine never saw did not happen. Drive the engine from **this repo's own vendored** `scripts/checklist_engine.py` (this repo *is* the constellation-skills source — the globally-installed copy and the repo's source copy can diverge; the repo's copy governs). Instantiate your work area with `--skill-dir` pointing at your worktree root so spine command postconditions resolve to your vendored `./scripts/`.

**Active lessons relevant to this mission** (from `.agent-work/LESSONS.md`; conditioned into your planning and handoff authoring):

- `lesson:verify-launch-order-claims-against-code` — **verify this order's named claims against the current code before planning.** Grep the named symbols/paths yourself: a headline mechanism that already shipped becomes an honest-null, and a named-but-nonexistent edit target is a naming slip, not a build task. This has recurred across two epics (5 mentions, 2 confirms). Specifically: confirm what the spine's gate-note loading actually does today before designing an extension to it.
- `lesson:round-trip-tests-prove-artifacts-not-parsers` — a round-trip test that lints/parses the **real shipped artifacts** proves those artifacts are clean; it does **not** prove your tool is correct. Bugs unreachable from the shipped artifacts pass it silently. Pair every round-trip/enumeration test over real artifacts with **adversarial fixtures** authored to make the tool return a WRONG answer (false FAIL on valid input, silent PASS on invalid input), and instruct your reviewer to hunt that specific class rather than only re-running the suite. This is directly load-bearing for you: a determinism check over the real corpus is exactly this shape.
- `lesson:cold-critic-mandatory-for-measurement-dependent-plans` — run the cold plan critic as **mandatory**, not optional, for any gate plan whose acceptance depends on a before/after measurement or a required round-trip/parser test. Both apply to you. Two commanders in one epic independently found it caught a plan-invalidating defect before any crew was dispatched.
- `lesson:test-harness-concurrency-failsafe` — if you write a test harness driving real concurrent file I/O, wrap per-iteration work in try/except with a guaranteed stop-signal in `finally`, and mark helper threads `daemon=True`. A writer thread dying without signaling stop leaves a non-daemon reader spinning and hangs the whole pytest process.
- `lesson:crew-plan-file-shares-parent-gauge-directory` — place any dispatched crew's own plan file in its **own subdirectory** under your work area (e.g. `.agent-work/<work-id>/<gate>-implement/plan.json`), not directly in the work-id root. A plan file in the work-id root resolves to the **same `gauge.json`** as your own spine, which can trip the Context Governor's HARD band on a reading that has nothing to do with the fresh crew.
- `lesson:prove-command-fails-postcondition` — a gate that must prove a command **correctly fails** does not fit the engine's command-postcondition semantics (exit 0 = pass). Use a `! <command>` bash-negation wrapper as the postcondition's `command` field to make "the guard fired" a mechanically re-verified engine check rather than a self-reported attest.

**Platform / technical invariants:**

- **Windows shell:** use the Bash tool for POSIX command sequences, PowerShell for cmdlets — never feed heredocs to PowerShell. Engine `command` postconditions run under a POSIX shell; author them in POSIX form.
- **PR bodies:** write the body to a temp file and use `gh pr create -F <file>`. Never a heredoc or a PowerShell here-string for `--body` (both fail for PR bodies; here-strings work for `git commit -m` only).
- **Never hand-edit `.agent-work/LESSONS.md`.** Structured deltas via `apply_lessons_delta.py` only.
- **Never hand-edit any engine JSON** (`spine.json`, plans, surveys) to change state — the engine owns that file and stamps the provenance that proves the work was driven. Consume state via the engine's `current` output, not by opening the file.
- **Escalating upward is always legitimate.** A delegate is not a replacement. If you need context this order does not cover, return and query the Admiral — it answers and continues you. Do not guess past the edge of your latitude to avoid the ask.

**Project doctrine deltas** (`docs/agents/ORCHESTRATOR_CONTEXT.md`): workflow mechanisms and verifiers are a **strengthened durable system** — plan targeted automated verification plus the relevant broader suite. Mechanism or workflow behavior change requires targeted automated tests **plus** the relevant broader suite; name both commands. A genuine no-test-surface exception needs a stated rationale. Local commits allowed; pushes/PRs/merges to `main` need approval — **pre-cleared for you** under this order for green + reviewed work on `epic-298/*` (see Budget).

## Pre-empted Steps

- **Epic-level context is established** — the epic intent, the confirmed spec's governing principles (B0.1 stochastic boundary, B0.3 two-bin rule, B0.4 consequence-scaled review), and the load-bearing-interface obligation are pasted above. Cite this launch order rather than re-deriving them.
- **The design-it-twice decision is already made** (pre-ruling above) — do not re-litigate whether to run it; run it.
- **The review class is already set** (full cold panel) — do not re-derive it from consequence analysis.

Everything else — your own understanding, plan, execution, and reconcile — you drive normally.

## Data Locations

- Main checkout (untracked inputs your worktree does **not** contain): `C:/Programs/constellation-skills`
- `.agent-work/` durable root at the main checkout: `C:/Programs/constellation-skills/.agent-work/` — **read-only to you** while the Admiral's epic lease is active. Your own `.agent-work/` resolves to your **worktree** root; that is expected under an epic, not a bug.
- `docs/agents/` (engine config, orchestrator/crew context) exists in the main checkout and is **untracked** — it will **not** be present in your worktree. If a spine `config_ref` needs it, copy what you need into your worktree rather than reaching into the main checkout.
- Epic latitude contract (context, not yours to edit): `C:/Programs/constellation-skills/.agent-work/epic-298/LATITUDE_CONTRACT.md`

## Budget

- **Model tier (required):** **Opus** for you as Commander. Dispatch crew at the least-powerful tier that does the job — Sonnet for mechanical implementation and review passes; escalate only where complexity, ambiguity, or risk demands it. **Never dispatch above Opus.** Name a model explicitly on every dispatch you make.
- **Compute/time, session-window:** you are one of three concurrent commanders in wave 0. Keep crew dispatches lean. If you are approaching a usage-limit reset, finish and return rather than launching a fresh crew into it.

## Stop Conditions

Stop and return when:

- The design-it-twice comparison is ready and needs its **convergence choice** (that is a float, and the expected mid-mission return — return with your comparison and recommendation, and the Admiral will answer and continue you).
- A decision outside your inherited latitude is required (scope change, two-bin routing, user-visible behavior).
- Your grep-before-plan finds the mission's premise is already satisfied at HEAD (honest-null — return it as a complete deliverable).
- Evidence for a required acceptance criterion is impossible to produce as specified.
- Budget crossed, or you need context this order does not cover and cannot safely proceed without.

Asking up is always sanctioned.

## Return Shape

Write your result artifact **before** going idle — an idle notification with no artifact reads as stalled, not done. Deliver first; the Admiral judges completion from what you produced, not from a message that arrives after you have gone quiet.

Write your verdict to: **`C:/Programs/constellation-skills-wt/298-300/.agent-work/verdict-300.md`**

Required contents:

1. **Verdict** — shipped / honest-null / blocked, in one line, then the substance.
2. **Evidence** — the design-it-twice comparison (candidates, constraints, axes, recommendation); test commands run and their exit codes; the determinism exercise and what it actually proved; PR number and merge state.
3. **`verify_worktree_isolation.py --here` output** — the matched worktree path, pasted, as evidence you worked in isolation.
4. **Map impact** — what the epic's architecture map should now say that it does not.
5. **Triage candidates** — out-of-scope work you found. File them to the tracker directly (`gh issue create` is pre-cleared) and list the issue numbers here; do not bank them worktree-locally.
6. **Workflow feedback** — friction, misfitting instructions, engine defects. Report misfit; it is compliance, not deviation.

Also stage your durable trio worktree-locally at `.agent-work/staged-feedback/300/` (lessons-delta, `AGENT_FEEDBACK.md` entry, `CONSTELLATION_FEEDBACK.md` exports) so the Admiral can harvest it before the worktree is swept.
