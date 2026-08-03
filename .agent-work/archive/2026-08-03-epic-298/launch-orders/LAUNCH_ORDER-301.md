# Launch Order: `commander-301 — issue #301 (epic-298 element C)`

Commanders start cold. Everything you need is pasted here; do not assume you can open anything by reference alone.

## Mission

Issue **#301 — Episode record and durable store: design-it-twice, then implement.**

Verbatim from the issue:

> Implement the episode record and its durable, queryable store (spec B1): explicitly partitioned mechanical vs agent-supplied field groups; suspected cause / proposed remedy as separate optional assertions; records must remain expressible as assertions under the Stratum A truth model (non-foreclosure); explicit retirement policy (retired = excluded from ordinary rhyme-search, retained in history). Replaces the evaporate-after-graduation inbox behavior. Design-it-twice (REQUIRED by the spec for this load-bearing interface) before fixing the schema. Acceptance: store exists; partition documented; retirement policy stated; a seeded episode is retrievable across sessions. Out of scope: automated capture wiring (issue G), consolidation (issue J).

**How it serves the epic.** Epic #298 is one closed vertical slice proving Constellation skills can natively enter, consume, and improve a shared, observable knowledge substrate. The episode record is one of the epic's **two load-bearing interfaces** (the other is the projection manifest, issue #300, running concurrently).

**The governing spec text for B1, pasted** (this is the design's own statement of your obligations):

> **Episodes are durable and queryable.** Before any diagnosis, an observation preserves two explicitly partitioned field groups. **Mechanically captured** (from engine and harness state, zero agent effort): run/project, role and active spine step, context manifest (what was loaded, at which revision), refusals, reopens, rework counts, failed commands, artifact references. **Agent-supplied** (kept deliberately small): task intent, expected behavior, observed behavior, impact/cost, workaround. Suspected cause and proposed remedy are separate, optional assertions. The episode record must remain expressible as assertions under the Stratum A truth model — it is the first accumulating store this design builds, and it must not become a silo the assertion model is later built *alongside* rather than *over*. The current inbox's evaporate-after-graduation behavior is replaced: the structured episode outlives its consolidation, so rhymes remain findable across runs. The store is not exempt from lifecycle: consolidated, superseded, and stale episodes are retired by the same explicit policy discipline the corpus itself lives under (retired means excluded from ordinary rhyme-search, retained in history).

**The Stratum A truth model you must not foreclose** (also pasted, since you cannot open the spec):

> **One assertion truth model.** All truth claims — code structure, historical fact, personal belief, philosophical argument, cross-project analogy — use the same mechanics: an identified assertion with source, supporting and challenging evidence, and a qualitative weak/medium/strong assessment that allocates trust-but-verify attention and creates no inertia against decisive new evidence. Belief strength and lifecycle standing (disputed, superseded, rejected) remain separate dimensions.

**Governing spec principle (B0.1, the stochastic boundary):** stochastic work happens *upstream of canon*; between canonical truth and an agent's active surface every transformation is **deterministic and attributable**. Finding that episodes rhyme is a sensor (LLM) job; **the store that makes rhymes findable is mechanical.** You are building the mechanical half.

## Prior-Wave Verdicts (pasted)

None — you are in wave 0. Two concurrent siblings you must not collide with:

- **#300 (projection generator + manifest)** is running concurrently in its own worktree. Your episode record has a **context field that consumes #300's manifest**. You do **not** design or edit the manifest. Define the obligation your context field places on a manifest (what it must carry: what was loaded, at which canonical revision) and design against that obligation. If you believe the manifest must change shape to serve you, that is a **float to the Admiral**, not a cross-edit.
- **#303 (confirm-gate refusal exercise)** touches `verify_spec_confirmed.py` read-only. No overlap expected.

**Explicitly downstream of you, not yours:** issue #305 (mechanical episode capture from engine state, with negative control) wires automated capture; issue #308 (first collated consolidation) runs the rhyme-search and consolidation loop. Build the store and prove a seeded episode is retrievable; do not build capture wiring or consolidation.

## Pre-Rulings

Ruled in advance, each overridable if evidence contradicts it — say so when overriding.

- decision:design-it-twice-required — you run design-it-twice on the episode-record interface: **3+ parallel candidate designs, each under one named distinct constraint**, compared on depth / locality / seam placement / testability, converging to one opinionated recommendation or named hybrid (never a menu). Required by the spec for this interface; **not** skippable as a trivial case.
  `@grade: settled/inherited · leans plan`
- decision:convergence-is-human — you generate and compare; **the Admiral surfaces the convergence choice to Tommy.** Float your comparison with a recommendation; do not self-converge and proceed.
  `@grade: settled/human · leans plan`
- decision:markdown-in-git — canonical storage stays **Markdown in git**. No database, no query language, no backend. Tommy's explicit direction in the confirmed spec, superseding an earlier exploration finding that favored Neo4j: *"Markdown is sufficient until observed pressure earns a backend."* "Queryable" here means findable by deterministic means over Markdown in git — not a query engine.
  `@grade: settled/human · leans plan,implement`
- decision:lessons-inbox-keeps-running — the existing `.agent-work/LESSONS.md` machinery **stays operative** for this epic's own runs. You are building the new store **alongside** it. Cutover is ruled at issue #308, **not** assumed by you. Do not migrate, disable, or rewrite the existing inbox.
  `@grade: guess · leans #301,#308 · settle: at #308, run one consolidation on the new store and rule on cutover`
- decision:full-cold-panel — issue #301 is in the epic's **full cold-panel review class** (spec B0.4: issues B, C, F, G, H build or change mechanisms). You may **not** default to a light single-reviewer pass.
  `@grade: settled/inherited · leans review`
- decision:no-foreclosure-is-testable — "must remain expressible as assertions under the Stratum A truth model" is an acceptance obligation, not a hope. Show your work: state concretely how an episode record maps onto (identified assertion, source, supporting/challenging evidence, qualitative strength) with lifecycle standing as a separate dimension. A design that can only satisfy this by rewriting the record later has **not** satisfied it.
  `@grade: settled/inherited · leans plan,review`
- decision:cross-session-retrieval-is-the-acceptance-test — "a seeded episode is retrievable across sessions" is exercised, not asserted. Seed episodes, end the session boundary honestly, retrieve. The spec also names a harder companion exercise owned downstream (seed across several runs, consolidate one cluster, confirm rhymes involving consolidated episodes' neighbors are still findable) — design so that stays possible.
  `@grade: settled/inherited · leans implement,review`

## Honest-Null Clause

A measured negative on the stated question is a complete, successful deliverable. Report it with the same rigor as a win. If design-it-twice shows the minimal store is far smaller than the issue implies, say so plainly — that is a result, not a shortfall. Per scoped-nulls doctrine, every null states what was tested **and what was not**.

## Inherited Latitude

**You may decide** (log it, proceed): implementation structure inside the chosen design; test strategy and fixtures; file layout of the store; bounded fix-now triage of defects in code you touch; filing issues to the tracker (`gh issue create` is **pre-cleared** — file findings directly, never bank them worktree-locally for harvest).

**You must float to the Admiral**: the design-it-twice convergence choice (surfaced to Tommy); any change to the obligations between your context field and #300's manifest; any scope change; any user-visible/production default change; **any two-bin routing ruling** (whether a doctrine item is prose-with-tripwire or mechanism-owned — Tommy's, always); any proposal to alter or retire the existing LESSONS.md machinery.

**Out-of-taxonomy always escalates** with one line on why it fit no class.

## File Ownership

Your working notes file: **`notes-301.md`**, in your own worktree, sole writer this wave.

> Name it `notes-301.md`, **never** `findings-301.md`. The harness `Write` tool refuses any path whose basename contains "findings" ("Subagents should return findings as text, not write report files") — a guard aimed at unprompted report-dumping, which cannot tell that this file was deliberately assigned. Three agents hit it in one epic and each worked around it with a shell heredoc. The guard is not ours to change; the word is.

Do **not** leave working notes at the repo root of the main checkout (a prior epic left `notes-261.md`/`notes-269.md` there permanently — filed as issue #278). Keep it inside your worktree.

**Fences:** you are the sole writer of the episode-record/store code and tests. **Do not edit `.agent-work/LESSONS.md` by hand under any circumstances** — structured deltas via `apply_lessons_delta.py` only. Do not edit `#300`'s projection/manifest code.

## Workspace

**Absolute worktree path:** `C:/Programs/constellation-skills-wt/298-301`
**Branch:** `epic-298/301` · **Base commit:** `b69e6c8` (main, verified fresh at dispatch)
**Created by:** `git worktree add -b epic-298/301 ../constellation-skills-wt/298-301 main`

First step, before any git operation: run `py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-skills-wt/298-301` — it must exit 0, proving you are in your own worktree and not the shared checkout. Paste its output into your return report.

**Windows worktree hazard (grounded, do not skip):** the Agent-tool `isolation:"worktree"` flag is a **silent no-op** on this platform. Your isolation comes from the explicitly-provisioned worktree above, which is why the verification command is mandatory rather than ceremonial.

NOTE: PR integration defaults to **server-side merge** (the GitHub merge on the PR itself, not a local merge that would diverge your worktree from main).

## Inherited Context

**Engine drive is mandatory.** Load `constellation-commander-delegated` and drive its spine through the checklist engine to completion. Work the engine never saw did not happen. Drive the engine from **this repo's own vendored** `scripts/checklist_engine.py` (this repo *is* the constellation-skills source — the globally-installed copy and the repo's source copy can diverge; the repo's copy governs). Instantiate your work area with `--skill-dir` pointing at your worktree root so spine command postconditions resolve to your vendored `./scripts/`.

**Active lessons relevant to this mission** (from `.agent-work/LESSONS.md`):

- `lesson:verify-launch-order-claims-against-code` — **verify this order's named claims against the current code before planning.** Grep the named symbols/paths yourself: a headline mechanism that already shipped becomes an honest-null, and a named-but-nonexistent edit target is a naming slip, not a build task. Recurred across two epics (5 mentions, 2 confirms). Specifically: read what `apply_lessons_delta.py` and the current LESSONS.md format actually do before designing their successor's neighbor.
- `lesson:round-trip-tests-prove-artifacts-not-parsers` — a round-trip test over the **real shipped artifacts** proves those artifacts are clean, not that your tool is correct. Bugs unreachable from the shipped artifacts pass silently. Pair every round-trip/enumeration test with **adversarial fixtures** authored to make the tool return a WRONG answer (false FAIL on valid input, silent PASS on invalid input), and instruct your reviewer to hunt that class rather than only re-running the suite.
- `lesson:cold-critic-mandatory-for-measurement-dependent-plans` — run the cold plan critic as **mandatory** for any gate plan whose acceptance depends on a required round-trip/parser test. Yours does (cross-session retrieval).
- `lesson:test-harness-concurrency-failsafe` — a test harness driving real concurrent file I/O needs try/except with a guaranteed stop-signal in `finally` and `daemon=True` helper threads; a writer dying without signaling stop hangs the whole pytest process.
- `lesson:crew-plan-file-shares-parent-gauge-directory` — put any dispatched crew's plan file in its **own subdirectory** under your work area, not in the work-id root; a root-level plan file shares your spine's `gauge.json` and can trip the Context Governor's HARD band on an unrelated reading.
- `lesson:prove-command-fails-postcondition` — to prove a command **correctly fails**, use a `! <command>` bash-negation wrapper as the postcondition's `command` field, making "the guard fired" a mechanically re-verified check rather than a self-reported attest.

**Platform / technical invariants:**

- **Windows shell:** Bash tool for POSIX sequences, PowerShell for cmdlets — never heredocs into PowerShell. Engine `command` postconditions run under a POSIX shell; author them in POSIX form.
- **PR bodies:** write to a temp file and use `gh pr create -F <file>`. Never a heredoc or PowerShell here-string for `--body` (here-strings work for `git commit -m` only).
- **Never hand-edit any engine JSON** to change state — the engine owns that file and stamps the provenance. Consume state via `current`, not by opening the file.
- **Editing a shipped compact-format JSON template:** edit the raw text **surgically**; never round-trip through `json.load`/`json.dump` (it reflows the whole file and destroys blame). Re-validate with `json.load` afterward.
- **Escalating upward is always legitimate.** A delegate is not a replacement. If you need context this order does not cover, return and query the Admiral — it answers and continues you.

**Project doctrine deltas** (`docs/agents/ORCHESTRATOR_CONTEXT.md`): workflow mechanisms and verifiers are a **strengthened durable system** — targeted automated verification plus the relevant broader suite; name both commands. A genuine no-test-surface exception needs a stated rationale. Pushes/PRs/merges to `main` are **pre-cleared** for you under this order for green + reviewed work on `epic-298/*`.

## Pre-empted Steps

- **Epic-level context is established** — epic intent, the confirmed spec's B1 text, the Stratum A truth model, and B0's governing principles are pasted above. Cite this launch order rather than re-deriving them.
- **The design-it-twice decision is already made** (pre-ruling) — run it, don't re-litigate it.
- **The review class is already set** (full cold panel) — don't re-derive it.
- **The storage-medium question is already ruled** (Markdown in git) — don't re-open it.

Everything else — understanding, plan, execution, reconcile — you drive normally.

## Data Locations

- Main checkout (untracked inputs your worktree does **not** contain): `C:/Programs/constellation-skills`
- Current lessons inbox to read as prior art (read-only): `C:/Programs/constellation-skills/.agent-work/LESSONS.md`
- `.agent-work/` at the main checkout is **read-only to you** while the Admiral's epic lease is active. Your own `.agent-work/` resolves to your **worktree** root; that is expected under an epic, not a bug.
- `docs/agents/` exists in the main checkout and is **untracked** — it will **not** be present in your worktree. Copy what you need in rather than reaching into the main checkout.
- Epic latitude contract (context, not yours to edit): `C:/Programs/constellation-skills/.agent-work/epic-298/LATITUDE_CONTRACT.md`

## Budget

- **Model tier (required):** **Opus** for you as Commander. Dispatch crew at the least-powerful tier that does the job — Sonnet for mechanical implementation and review passes. **Never dispatch above Opus.** Name a model explicitly on every dispatch you make.
- **Compute/time, session-window:** you are one of three concurrent commanders in wave 0. Keep crew dispatches lean. Near a usage-limit reset, finish and return rather than launching fresh crew into it.

## Stop Conditions

Stop and return when:

- The design-it-twice comparison is ready and needs its **convergence choice** (a float, and the expected mid-mission return — return with your comparison and recommendation; the Admiral answers and continues you).
- A decision outside your inherited latitude is required (scope change, two-bin routing, user-visible behavior, anything touching the live LESSONS.md machinery).
- Your grep-before-plan finds the mission's premise already satisfied at HEAD (honest-null — a complete deliverable).
- Evidence for a required acceptance criterion is impossible to produce as specified.
- Budget crossed, or you need context this order does not cover and cannot safely proceed without.

Asking up is always sanctioned.

## Return Shape

Write your result artifact **before** going idle — an idle notification with no artifact reads as stalled, not done. Deliver first.

Write your verdict to: **`C:/Programs/constellation-skills-wt/298-301/.agent-work/verdict-301.md`**

Required contents:

1. **Verdict** — shipped / honest-null / blocked, in one line, then the substance.
2. **Evidence** — the design-it-twice comparison (candidates, constraints, axes, recommendation); the documented mechanical/agent-supplied partition; the stated retirement policy; the cross-session retrieval exercise and what it actually proved; the concrete Stratum A expressibility mapping; test commands and exit codes; PR number and merge state.
3. **`verify_worktree_isolation.py --here` output** — the matched worktree path, pasted.
4. **Map impact** — what the architecture map should now say that it does not.
5. **Triage candidates** — file them to the tracker directly (pre-cleared) and list the issue numbers; do not bank them worktree-locally.
6. **Workflow feedback** — friction, misfitting instructions, engine defects. Reporting misfit is compliance, not deviation.

Also stage your durable trio worktree-locally at `.agent-work/staged-feedback/301/` (lessons-delta, `AGENT_FEEDBACK.md` entry, `CONSTELLATION_FEEDBACK.md` exports) so the Admiral can harvest it before the worktree is swept.
