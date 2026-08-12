# Mission Frame — issue #300, projection generator + manifest

**Map substitution stated up front.** This skill-source repo carries no `docs/architecture/`
packet map (no Cartographer packets, no `capability:`/`struct:` node ids). Per the commander-core
architecture bookend, the structural record is reconciled directly against the docs that own the
affected design: `docs/CHECKLIST_ENGINE_DESIGN.md`, `docs/CHECKLIST_SCHEMA.md`,
`docs/CONSTELLATION_OVERVIEW.md`. Anchors below are written against real files and symbols rather
than map node ids. This is **not** a trivial-change frame skip — the frame is full; only its
vocabulary is substituted.

## Intent

Ship the minimal deterministic projection substrate and its manifest: make the per-spine-step
context set **machine-readable**, assemble it **deterministically**, and emit a **manifest**
recording what was made available and at which canonical revision — as a byproduct of assembly,
never as a separate act. Bound: delivery, not use.

## Affected Capabilities

- **Spine-keyed context delivery** — today the engine deterministically *selects* the active step
  and prints its `imperative`; the canonical Markdown that imperative names is opened by hand.
  This run adds the declaration + assembly + record layer beneath that selection, reusing the same
  selector.
- **Engine state projection** (`state(cl) -> dict` / `render_human`) — relied on, not changed. The
  new producer sits beside it and borrows its purity discipline and its contract-version idiom.
- **Determinism/reproducibility of agent-facing context** — new capability. Nothing today can
  answer "what did this agent have, at which revision".

## Structural Anchors

- `scripts/checklist_engine.py` — `active_id()` (~:184, the selector to extend, 6 lines);
  `state()` / `render_human()` / `_STATE_CONTRACT_VERSION` (~:1336–1471, the seam and the
  versioning idiom); the CLI read-only-verb write guards (~:2508, :2523).
- `skills/commander/templates/COMMANDER_SPINE.template.json` — where the declaration lands
  (a new optional key on the task object, beside `constraints`/`directives`).
- `docs/CHECKLIST_SCHEMA.md` — the Task table; the declaration needs one documented row.
- `docs/CHECKLIST_ENGINE_DESIGN.md` — §"Answerability" owns the projection-port design narrative;
  the reconcile step folds this change in here.
- `scripts/agent_work_root.py` — root resolution; **verified live** to return the *worktree*, not
  the main checkout, while an Admiral lease is active. Any `durable:` root token is affected.
- `tests/test_checklist_engine.py` — the existing engine suite the broader run must stay green on.

## Governing Constraints / Assumptions

- **constraint:stochastic-boundary (spec B0.1)** — between canonical truth and an agent's active
  surface every transformation is deterministic and attributable. No LLM at assembly time. Breaks
  the epic's founding principle if violated.
- **constraint:markdown-in-git** — canon stays Markdown in git; no DB, no query language. Tommy's
  explicit direction. Forces revision identity to come from git itself.
- **constraint:delivery-not-use** — the manifest answers what was *made available*. Access tracing
  and transcript analysis are named out of scope by the issue. Widening it is wrong, not ambitious.
- **constraint:extend-dont-parallel** — bind to the existing `active_id()` selector; a second
  assembly path violates "one canonical path; no speculative abstraction".
- **constraint:no-foreclosure** — manifest entries must stay expressible as Stratum A assertions
  (subject + source + evidence + qualitative strength) later. A `{path, rev}` row already is one.
- **assumption:5 (spec)** — "deterministic recipes can express real working sets", *partially*
  grounded by the spine's gate notes. **Verified this run:** the grounding is for *selection* only;
  assembly is genuinely unbuilt. The assumption is weaker than it reads and this run is its first
  real exercise.
- **constraint:windows-corpus** — CRLF, filesystem ordering, and locale are the named real
  irreproducibility sources. `newline="\n"` on every write is load-bearing, not hygiene.

## Claims / Evidence Surfaces

- **claim:manifest-on-every-assembly** — checked by a test that drives the real producer through the
  engine, not a hand-built fixture (`lesson:verify-harness-field-and-drive-real-writer`).
- **claim:revision-identity-present** — checked by asserting the computed identity equals
  `git hash-object` / `git rev-parse HEAD:<path>` for a tracked clean file, and is still produced
  for dirty, untracked, gitignored, and out-of-repo files.
- **claim:deterministic-across-environments** — the pre-ruled acceptance test: rebuild from a
  **clean checkout in a second environment**, byte-compare, with the exclusion set structurally
  separate from content. Round-trip over the real corpus is **not** sufficient on its own
  (`lesson:round-trip-tests-prove-artifacts-not-parsers`) — adversarial fixtures required: CRLF/LF
  twins must agree; a stale manifest must not silently PASS; untracked-vs-absent must not disagree
  between environments; a declaration-order permutation must register as drift.
- **claim:consumable-as-episode-context-field** — checked by shape/obligation assertions only. #301
  is concurrent; I state obligations, I do not test against its code.

## Decision Anchors & Decision Pressure

Inherited from the launch order (already ruled; not re-litigated):

- decision:design-it-twice-required — 3+ parallel candidates under named distinct constraints.
  `@grade: settled/inherited · leans plan` — **discharged**: 3-author panel run, comparison at
  `.agent-work/300/DIT-COMPARISON.md`.
- decision:convergence-is-human — I compare and recommend; Tommy picks via the Admiral.
  `@grade: settled/human · leans plan` — **floated, awaiting answer.**
- decision:extend-dont-parallel — `@grade: settled/inherited · leans implement`
- decision:markdown-in-git — `@grade: settled/human · leans plan,implement`
- decision:full-cold-panel — `@grade: settled/inherited · leans review`
- decision:determinism-is-the-acceptance-test — `@grade: settled/inherited · leans implement,review`
- decision:no-foreclosure — `@grade: settled/inherited · leans plan`

Settled by the panel's independent triple-convergence (evidence-backed, revisable only on
contrary evidence):

- decision:rev-is-lf-normalised-blob-oid — revision identity is the git blob OID of LF-normalised
  bytes, computed in-process; never a commit SHA, never a git subprocess.
  `@grade: settled/measured · leans g1-implement · settle: already settled — three independent
  authors each verified equality with git hash-object on real files, incl. CRLF twins`
- decision:declaration-is-optional-spine-field — the context set is declared as a new *optional*
  ordered list on the spine task; absent means empty, so existing spines are untouched.
  `@grade: settled/measured · leans g1-implement`
- decision:no-globs-order-is-content — never enumerate the filesystem; declaration order is content
  and is never sorted. `@grade: settled/measured · leans g1-implement`
- decision:prose-stays-plus-lint — the imperative keeps the rules a path list cannot express
  (substitute-and-record; sanctioned-degradation); a mechanical lint pins declaration against prose.
  `@grade: settled/measured · leans g2-doctrine`

**Decision pressure — surfaced, not settled by me:**

- *Committed artifact in #300, or deferred to issue #306?* This is the real content of the floated
  convergence choice. It decides whether the spec's "every doctrine change produces a reviewable
  diff" becomes true in this issue or later.
- *Manifest cardinality (one per spine step) vs #301's episode `context` field.* If #301 assumed one
  per episode, one of us must change — Admiral float, never a cross-edit.
- *Durability of run manifests.* They live under gitignored `.agent-work/`, destroyed by
  `git worktree remove`; and `agent_work_root.py` returns the worktree under an Admiral lease.
  Inline-vs-reference is #301's call.

## Map Confidence / Staleness / Disputes

- `docs/CHECKLIST_ENGINE_DESIGN.md` §Answerability — **high confidence**, written for #227 and
  matched against the live code by three independent authors this run. No verification gate needed.
- No `docs/architecture/` packet map exists — **absent, not stale**. Handled by the substitution
  declared at the top of this frame, not by a scout gate: there is nothing to scout.
- `scripts/agent_work_root.py` durable-root behaviour under an Admiral lease — **verified live this
  run** (returns the worktree). Previously would have been an unverified assumption; now grounded,
  and it constrains any `durable:` root token.

## Out of Scope

- Access tracing and transcript analysis (named out of scope by the issue; #307 owns the ordering
  question).
- The episode record's internals (#301, concurrent — obligations stated, no cross-edit).
- The loud-failing drift **gate** (issue #306) — this run may ship the regenerate-and-compare seam, but
  not the gate that fails a run on mismatch.
- Degraded-mode reporting on a missing required entry (issue F).
- The kernel-plus-fragments break and the whole-role human-readable projection — the **conditional**
  half of spec B2, decided at issue L. Precision matters here and the cold plan critic caught the
  ambiguity: B2 also contains the **ahead-of-time-generation** bullet ("a versioned script builds the
  projection, so every doctrine change produces a reviewable diff of what agents will actually see"),
  and *that* half is this issue's mandate, not out of scope. Only the kernel break and the whole-role
  projection are excluded.
- Any change to `verify_spec_confirmed.py` (#303's read-only surface).
