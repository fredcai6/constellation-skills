# Plan alternative A — `smallest-diff`

**Work id:** `epic-559/c3-lifecycle` · **Role:** `plan-alt-a` · **Constraint:** the least new
structure that satisfies every required property.

## 1. The candidate, one paragraph

Two new tool schemas (`spine_open`, `spine_close`) join the *already-registered* `spine` MCP
server's `TOOLS` list and are dispatched from one new sibling function, `call_lifecycle_tool`,
that sits beside `call_tool` in `scripts/mcp_spine_server.py` and is wired in at the JSON-RPC
`tools/call` branch — `call_tool`'s own body, and the AST pin that walks it, are untouched.
`spine_open` never reads the door's bound `SPINE`/`SESSION` globals at all: it takes `work_id` +
`spec` + explicit `branch`/`worktree`/`base` from the caller, shells `git worktree add`, calls
`scripts/init_work_area.py` and `scripts/generate_spine.py` **as libraries** (new functions added
to `init_work_area.py`, not new modules), verifies the result with
`verify_worktree_isolation.check_distinct_real` called **in-process**, and on any failure rolls the
worktree back and refuses. `spine_close` takes no arguments at all: it reads the door's own bound
spine, refuses unless the terminal gate is complete and the lease is released (both already true by
the time a caller gets there, because `spine_advance`/`spine_lease release` are the *existing*
doors that do steps 1–3 of the fixed close order), then moves the work area with `git mv`, spine and
journal last, commits, and reports. The worktree record lives inside the spine itself, a top-level
`origin` block the engine already tolerates and round-trips untouched. The declared-dispatch
property reuses the existing `[gate.claim]` injection pattern in `generate_spine.py`: a new
`[[gate.dispatch]]` table compiles into a `directives.dispatch` block plus one injected `script`-kind
postcondition against one new, small, unavoidable file — `scripts/verify_declared_dispatch.py` —
which is the only genuinely new module this candidate ships. Everything else is an addition to a
file that already does this class of work.

## 2. The gate plan

Six gates. `g0` is a reasoning gate (naming decision, no crew — matches the precedent
`DESIGN_NOTE.md` set at C2's own `g0-design`). `g1`–`g4` are implementer crew gates, ordered so each
ships its own tests with its own code — no gate boundary is crossed with a known-red suite. `g5` is
an independent reviewer survey gate, required because `g2` and `g3` both carry a large claim
(destructive git operations — `worktree add`/`worktree remove`/`git mv`/`git commit` — are the kind
of blast radius the pre-ruling "a greater claim requires greater review" exists for).

### g0 — freeze the lifecycle contract (reasoning gate, no crew)

**Waiver reason:** this is a naming-and-authority decision — where the tool lives, what `origin`
holds, one tool vs. two — with nothing for a reviewer to *run*; C2's `DESIGN_NOTE.md` §0 sets this
exact precedent for the same class of decision.

**Imperative:** Write `.agent-work/epic-559/c3-lifecycle/LIFECYCLE_CONTRACT.md` (the path
`MISSION_FRAME.md`'s own decision-pressure section already commits to) recording, verbatim and
falsifiably: the `origin` block's exact keys; `spine_open`'s exact input schema; `spine_close`'s
exact refusal predicate (terminal-gate-complete AND lease-released); the `[[gate.dispatch]]` TOML
shape and the fields `verify_declared_dispatch.py` checks; and the worktree-path/branch-naming
decision pushed to the caller (see §5, "where the constraint hurts").

**Close criteria:** `LIFECYCLE_CONTRACT.md` exists and is non-empty (arrival only, per the C2
precedent — content is judged by `g5`, not machine-checked here).

**Evidence:** the file itself, committed.

### g1 — carried findings (crew: implementer)

**Imperative:** Fix `cond.get("not_yet_written")` bare truthiness in `scripts/generate_spine.py`
(both call sites — `compile_condition` at the `not_yet_written` branch, and `_probe_pytest`'s
dispatch to `_probe_pytest_not_yet_written`) by adding a **spec-shape fault**, not a silent
coercion: a `not_yet_written` key present with a non-bool value (e.g. the TOML string `"false"`) is
refused at generation with a new fault code `spec-non-bool-not-yet-written`, naming the field and
its type — consistent with this generator's own stated ethos ("a check is a shell string typed from
memory, and a wrong one does not announce itself"; silently reinterpreting `"false"` as absent is
the same class of silent misread the generator exists to kill, one level up). Reconcile
`DESIGN_NOTE.md` §4, §7, §10 to shipped behaviour: §4 needs the new fault code listed alongside the
existing spec-shape-fault vocabulary; §7's fault list needs the same addition; §10's defect table is
otherwise accurate and needs no change beyond confirming it still holds (verified during this gate,
not assumed).

**Close criteria (checkable):**
- `python -m pytest -q -k "NotYetWrittenNonBool" tests/test_generate_spine.py` collects ≥ 2 and
  passes (one VIOLATING: `not_yet_written = "false"` refused with `spec-non-bool-not-yet-written`;
  one INNOCENT: `not_yet_written = true` compiles exactly as before, `check: null`, the declared
  statement suffix).
- `grep -c "spec-non-bool-not-yet-written" .agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md`
  ≥ 1 (the reconciliation landed in the frozen contract doc, not just the code).
- `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`
  still passes at ≥ 2824 (no regression from the new fault).

**Evidence:** the diff to `generate_spine.py` and `DESIGN_NOTE.md`; the new pytest fixtures; a full
suite run.

### g2 — open (crew: implementer) — LARGE CLAIM

**Claim text:** "this gate adds the only code path in the corpus that runs `git worktree add` and,
on failure, `git worktree remove`, un-reviewed today; a wrong rollback predicate destroys a worktree
that should have survived."

**Imperative:** Add `open_work(work_id, spec, root, branch, worktree, base, claimed_by="agent")` to
`scripts/init_work_area.py`. In order: refuse if `worktree` already exists on disk (no silent
overwrite); refuse if a spine already exists at `<worktree>/.agent-work/<work_id>/spine.json` with
an active, non-abandoned `engine_session` (never reuse an occupied work area even under a fresh
worktree path — mirrors `agent_work_root._active_epic_lease`'s own read-only scan style); run
`git worktree add <worktree> -b <branch> <base>` from `root`; on any subprocess or Python exception
from this point on, roll back with `git worktree remove --force <worktree>` (and `git worktree
prune`) before re-raising a legible refusal — **the roll-back path itself needs its own test**, not
just the happy path; call `init_work_area.init_work_area` then `generate_spine.main` (imported, not
subprocessed — "as libraries") against `<worktree>/.agent-work/<work_id>/spine.json`; inject the
`origin` block (`work_id`, `branch`, `worktree` (absolute), `base_commit` = `git rev-parse <base>`,
`opened_at`, `opened_by`) into the written spine with a plain `json.load`/`json.dump` round-trip;
call `verify_worktree_isolation.check_distinct_real([worktree], registered_worktrees(),
primary_checkout())` **in-process** (never trust `git worktree add`'s own exit code alone) and roll
back on a negative result exactly as on any other failure. Wire `spine_open` into
`mcp_spine_server.py`: a new tool schema (`work_id`, `spec`, `branch`, `worktree`, `base` all
required strings — no optional convention-guessing, see §5), and a `call_lifecycle_tool` branch that
imports `init_work_area.open_work` and returns its result as text, reporting
`SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` values for the caller to pass to a subsequent
`run_crew.py` dispatch into the new worktree (the tool cannot set env vars for a process that does
not exist yet — it can only state them).

**Close criteria (checkable):**
- `python -m pytest -q -k "OpenRollback or OpenOccupiedRefusal or OpenSelfVerification or
  OpenOriginRoundTrip" tests/test_spine_lifecycle.py` collects ≥ 8 and passes. Fixtures, named:
  - VIOLATING `OpenOccupiedRefusal::test_refuses_when_worktree_path_exists` — target path already a
    directory → refused by name, nothing created.
  - VIOLATING `OpenOccupiedRefusal::test_refuses_when_work_id_spine_already_active_elsewhere` — a
    spine at a *different* path with `engine_session.status == "active"` for the same `work_id` →
    refused by name.
  - INNOCENT `OpenOccupiedRefusal::test_succeeds_on_a_genuinely_free_work_id_and_path`.
  - VIOLATING `OpenRollback::test_forces_a_late_failure_and_asserts_the_worktree_is_gone` — monkeypatch
    `generate_spine.main` (or `validate_spine.validate`) to raise *after* `git worktree add`
    succeeds; assert the worktree is no longer in `git worktree list --porcelain` afterward and the
    call raised/refused (not "half a worktree, no spine").
  - VIOLATING `OpenSelfVerification::test_git_reports_success_but_isolation_check_fails` — monkeypatch
    `check_distinct_real` to return `(False, "...")` even though `git worktree add` exited 0; assert
    `open_work` still refuses and rolls back — the property the launch order names explicitly
    ("verifies its own result... rather than trusting that git returned 0").
  - INNOCENT `OpenSelfVerification::test_real_worktree_add_passes_the_self_check`.
  - INNOCENT `OpenOriginRoundTrip::test_origin_survives_a_claim_start_attest_advance_drive` — drives a
    real generated spine through the engine end to end and asserts `origin` is byte-identical to
    what `open_work` wrote (re-proves mission-frame measurement 5 against *this* spine, not just the
    ad hoc one the Commander drove).
- `python -m pytest -q -k "IdentityBindingPinTests" tests/test_mcp_identity.py` still passes — see
  §4(a) for the required, scoped edit to `TOOL_MINIMAL_ARGS`/the `call_tool`-direct sweep this gate
  must make, or this suite goes red for a reason that has nothing to do with a real redirect.
- Full suite green (command as in `g1`).

**Evidence:** diff, new tests, a pasted `git worktree list --porcelain` before/after a rollback
fixture run (so the rollback claim is demonstrated, not asserted).

### g3 — close (crew: implementer) — LARGE CLAIM

**Claim text:** "this gate adds the only code path in the corpus that moves and commits
`.agent-work/<work-id>/` programmatically; a wrong ordering predicate corrupts the spine driving the
close, exactly the failure the fixed order in the launch order exists to prevent."

**Imperative:** Add `close_work(spine_path, session, root)` to `scripts/init_work_area.py` (or,
if it reads more naturally beside the door's own spine-reading helpers, to `mcp_spine_server.py`
directly — decided at `g0`, both are equally small; this candidate defaults to `init_work_area.py`
for symmetry with `open_work`). Read the bound spine's raw JSON (the same "read `spine.json`
directly, do not go through the engine's rendering" convention `agent_work_root._active_epic_lease`
already uses) and refuse — no partial action — unless **both**: `engine_session.status ==
"released"` (steps 1–3 of the fixed order are the caller's job via the *existing* `spine_advance`
and `spine_lease release` tools, already doctrine, already tested; `spine_close` does not
re-implement or re-call them) and `all(tasks[i]["status"] == "complete" for i in items)` (every gate,
not just the closeout one — the launch order's "the closing advance puts the work away" reads as the
whole run being over). Refuse if `.agent-work/archive/<work_id>/` already exists (never overwrite a
prior archive). Then, in order: for every top-level entry directly under `.agent-work/<work_id>/`
**except** `spine.json` and `spine.json.journal`, `git mv <entry> .agent-work/archive/<work_id>/<entry>`
(each call names its own paths — never `-A`, never `.`); then `git mv spine.json` and, if present,
`git mv spine.json.journal`, both last; `git commit -m "archive <work_id>: ready to PR"`; report a
readiness verdict naming `origin.branch`, the new `git rev-parse HEAD`, and "ready to PR — nothing
else is pushed or opened." Wire `spine_close` into `mcp_spine_server.py`: an **empty** input schema
(it acts on nothing the caller supplies — see §4(d)) and a `call_lifecycle_tool` branch.

**Close criteria (checkable):**
- `python -m pytest -q -k "CloseOrderingRefusal or CloseArchivesInPlace or CloseStagesByName or
  CloseCannotEatItsOwnSpine" tests/test_spine_lifecycle.py` collects ≥ 8 and passes:
  - VIOLATING `CloseOrderingRefusal::test_refuses_while_lease_still_active` — call `close_work`
    before `release`; assert the work area is untouched (`.agent-work/<work_id>/` still has every
    file it had, nothing under `archive/`).
  - VIOLATING `CloseOrderingRefusal::test_refuses_while_a_non_terminal_gate_is_pending` — released
    lease, but an earlier gate's status is not `"complete"` (e.g. `"skipped"` counts as
    non-terminal here — deliberately stricter than "not pending"; argued in §5) → refused.
  - INNOCENT `CloseOrderingRefusal::test_succeeds_once_genuinely_terminal_and_released`.
  - `CloseCannotEatItsOwnSpine::test_real_close_after_a_real_terminal_advance_and_release` — the
    mission-frame-promised evidence surface: drive a real generated spine through
    `claim → start → attest → advance` on every gate, `release`, THEN `close_work`, and assert the
    spine lands at `.agent-work/archive/<work_id>/spine.json` with `origin` and every gate's
    `evidence[]` intact (nothing lost mid-move).
  - `CloseStagesByName::test_no_git_add_dash_a_or_dot_anywhere_in_close_work` — an AST/source-text
    guard over `close_work`'s own body (the `_cli_only_verb_violations` house style, applied to a
    fixed predicate rather than a corpus sweep): no literal `"-A"` or bare `"."` reaches a
    `subprocess.run(["git", "add", ...])`/`["git", "mv", ...])` call. VIOLATING: a mutated copy of
    the function with `git add -A` spliced in — the guard must catch it (positive control, in the
    assertion path, per the launch order's own review standard).
- `python -m pytest -q -k "IdentityBindingPinTests" tests/test_mcp_identity.py` still passes (empty
  schema means no `TOOL_MINIMAL_ARGS` surprises here, but the sweep-scope edit from `g2` must still
  cover `spine_close`).
- Full suite green.

**Evidence:** diff, new tests, the before/after directory listing of one real close run.

### g4 — declared dispatch (crew: implementer)

**Imperative:** Extend `generate_spine.py`'s spec shape with `[[gate.dispatch]]` (fields: `role`
required, `model` required; `parent` is **not** author-declared per entry — it is filled from the
spec's existing top-level `parent` field, exactly the value `_handback_contract`'s `hand_back_to`
already uses). Add `spec-dispatch-missing-field` (missing `role` or `model` on a declared dispatch)
and `spec-dispatch-unresolved-parent` (a `[[gate.dispatch]]` declared while the spec's own
`parent` is absent or the shipped-template placeholder shape — there is nothing concrete to fill in,
so refuse rather than emit a dispatch record naming `"unknown"`) to `spec_shape_faults`. In
`_compile_gate`, for each declared dispatch: render `directives.dispatch` (a list of
`{role, model, parent}` dicts, so a crew reading the gate sees exactly what it must dispatch and
under what identity) and inject one postcondition per entry,
`id = f"dispatch-verified-{role}"`, `kind = "command"`,
`command = "cd <repo-root> && python scripts/verify_declared_dispatch.py <work-id> <gate-id> <role>
<model> <parent> --root <repo-root>"` (every token `shlex.quote`d; `<work-id>`/`<repo-root>` are the
existing resolver-owned tokens, `gate-id`/`role`/`model`/`parent` are literal strings already known
at generation time). Write `scripts/verify_declared_dispatch.py`: reads
`.agent-work/<work_id>/crew-runs.json`, filters to **non-abandoned** entries matching
`(work_id, gate, role)`, refuses (exit 1, naming what was found) if none exist ("this dispatch never
ran") or if **any** matching entry's `parent`/`model` differ from the declared values (naming the
offending entry) — deliberately over every matching attempt, not just the latest; a corrected
mistake is still a mistake that happened (argued in §5), and abandoning the bad attempt is the
documented way to clear it.

**Close criteria (checkable):**
- `python -m pytest -q -k "DispatchSpecShape or DispatchInjectedPostcondition or
  VerifyDeclaredDispatch" tests/test_generate_spine.py tests/test_verify_declared_dispatch.py`
  collects ≥ 10 and passes. Fixtures:
  - VIOLATING `DispatchSpecShape::test_missing_model_refused`,
    `DispatchSpecShape::test_declared_without_resolvable_parent_refused`.
  - INNOCENT `DispatchSpecShape::test_role_and_model_and_top_level_parent_present_compiles`.
  - VIOLATING `VerifyDeclaredDispatch::test_wrong_parent_named_the_grandparent_fails` — an entry
    whose `parent` is a different (but real-looking) session id, reproducing the exact defect the
    launch order names ("six sub-crews were dispatched naming the Admiral as parent").
  - VIOLATING `VerifyDeclaredDispatch::test_missing_model_fails`,
    `VerifyDeclaredDispatch::test_no_matching_entry_at_all_fails`.
  - INNOCENT `VerifyDeclaredDispatch::test_matching_entry_passes`.
  - ACCEPTED_FALSE_ALARM `VerifyDeclaredDispatch::test_abandoned_bad_attempt_does_not_block` — an
    entry with the wrong parent but `abandoned: true` is ignored, so this is not a false alarm at
    all once abandonment is respected; named here because a *naive* first draft of this checker
    (ignoring `abandoned`) would have flagged it, and the fixture pins that the real one does not.
- Full suite green.

**Evidence:** diff, new tests, one real `generate_spine.py` run against a fixture spec carrying
`[[gate.dispatch]]`, pasted.

### g5 — independent review (crew: reviewer, survey-type)

**Waiver reason:** none — this is the crew gate the two LARGE claims in `g2`/`g3` require.

**Imperative:** Drive the standard reviewer survey against the full `g1`–`g4` diff, with the launch
order's own two-question standard named explicitly in the handoff ("does this mechanism work, and is
the value it carries correct" — not just "does the rollback test pass" but "is `git worktree remove
--force` actually what ran, on actually the right path"). Specifically re-run, live, not from
memory: the rollback fixture (confirm the worktree is truly gone via `git worktree list`, not just
that an assertion string says so); the close-cannot-eat-its-own-spine fixture; and the sweep
(`python scripts/validate_spine.py --sweep --root .` still exactly 23).

**Close criteria:** `spine_survey_result consolidate` reaches `verdict: APPROVE`, which — per
`c-escalation`'s mechanism on `g2`/`g3` — is what an `artifact`/`review-result` postcondition on
those two gates is waiting for (note the residual: `DESIGN_NOTE.md` §6's own correction already
states this only *fires* on a `gated` spec, which this Commander's own driving spine is — so it is
genuinely enforced here, not the survey-side gap that correction floats).

**Evidence:** the survey checklist's own consolidated result; the re-run command outputs, pasted
verbatim.

## 3. The violating fixtures — summary table

| Guard | VIOLATING | INNOCENT |
|---|---|---|
| `spec-non-bool-not-yet-written` | `not_yet_written = "false"` (string) | `not_yet_written = true` (bool) |
| occupied-worktree refusal (path) | target path exists | target path free |
| occupied-worktree refusal (work-id) | active spine for the work-id elsewhere | no such spine |
| open rollback | late failure after `git worktree add` | all steps succeed |
| open self-verification | `check_distinct_real` returns False despite git exit 0 | real add, real check, both agree |
| close ordering (lease) | called before `release` | called after `release` |
| close ordering (terminal) | a non-last gate not `complete` | every gate `complete` |
| close stage-by-name | mutated `close_work` with `git add -A` spliced in | the real, unmutated function |
| dispatch spec-shape | missing `model` / no resolvable `parent` | `role`+`model` present, top-level `parent` concrete |
| declared-dispatch check | recorded entry names the wrong parent | recorded entry matches declared parent+model |
| declared-dispatch abandonment | (ACCEPTED_FALSE_ALARM, not a real gap) wrong-parent entry marked `abandoned` | — |

Every guard above has both sides pinned in §2's close criteria; none is exercised only on its happy
path.

## 4. The four answers, argued

**(a) How open is reachable through a door that binds one spine at import and whose `call_tool` is
AST-pinned to two return shapes.** It is reachable because it never enters `call_tool` at all.
`_identity_violation` and the pass-through pin
(`tests/test_mcp_identity.py::IdentityBindingPinTests::test_call_tool_can_only_produce_content_two_ways`)
are properties of one function's body; a second function, `call_lifecycle_tool`, dispatched from a
sibling branch in `main()`'s `tools/call` handling, is invisible to that AST walk and carries no
obligation to return only `as_result(run_engine(...))` or `_tool_error(...)`. This is not a loophole
around the pin — it is exactly what the pin's own docstring already concedes is a different tool
family ("the CLI door deliberately does NOT have [confinement], which is why the two doors are
different tools rather than two copies of one"): `spine_open` is a third kind, alongside the bound
MCP door and the per-call CLI, and it earns that by never touching `SPINE`/`SESSION` at all — it
reads `work_id`/`spec`/`branch`/`worktree`/`base` from its own arguments and writes a *new* file the
bound door was never addressing. The concrete implementation risk this candidate must not skip: the
identity pin's own `test_no_argument_can_change_what_the_door_reads_or_where_it_reads_it` iterates
`module.TOOLS` and calls `module.call_tool(tool["name"], ...)` for **every** tool in that list — once
`spine_open`/`spine_close` are added to `TOOLS`, that loop hits `call_tool`'s dead `raise
KeyError(name)` fallback for both, because they are *not* handled inside `call_tool` by design.
`g2`'s close criteria therefore require a scoped edit: that sweep must iterate
`TOOL_NAMES - LIFECYCLE_TOOL_NAMES`, not all of `TOOLS`, and `call_lifecycle_tool` needs its own,
separate containment pin (an AST/text guard asserting `spine_open`'s branch never references
`module.SPINE`/`module.SESSION`/`run_engine` at all — the property that makes not-presupposing-a-
bound-spine a checked fact rather than a claim). Missing this edit is not cosmetic: an un-scoped
sweep would either false-positive-crash on every test run (loud, at least honest) or, if someone
"fixed" it by adding `spine_open`/`spine_close` handling *inside* `call_tool` to make the sweep pass,
that would be the exact regression the pin exists to catch, arriving through the back door of a test
maintenance chore instead of a redirect. Naming this now, at plan time, is the whole point of the
mission frame's warning about absence-and-ubiquity reading as correct.

**(b) Where the worktree record lives.** Top-level `origin` on the spine itself, on the mission
frame's own measurement 5 (an unknown top-level key round-trips a full engine drive untouched, and
`validate_spine._shape_faults` has no unknown-key fault). A sidecar file was considered and rejected
for the reason this whole epic exists: two files that can independently drift is the shape of every
defect this epic is closing, and a worktree record that disagrees with the spine describing it is
exactly that shape one level up. The honest residual, stated rather than patched: nothing in
`checklist_engine.py` defends `origin` — no verb reads it, no verb refuses a missing or malformed
one. `g2`'s `OpenOriginRoundTrip` fixture is a regression test *pinning* the round-trip, not a proof
the engine enforces it; if a future `amend` or hand-authored edit corrupts `origin`, nothing but that
one test would notice.

**(c) Whether the declared dispatch is data the engine consults or prose a crew retypes.** Data a
generated **postcondition** consults, mechanically, at `advance` time — not data the *engine's own
verbs* interpret (the engine dispatches nothing, and this candidate does not ask it to). The
generator compiles `[[gate.dispatch]]` into a `command`-kind check against
`scripts/verify_declared_dispatch.py`, which reads the durable `crew-runs.json` registry and refuses
`advance` unless a real, non-abandoned entry recorded the declared `role`/`model`/`parent`. The
rendered `directives.dispatch` block is still prose a crew reads before dispatching — that channel is
not removed, because nothing forces an agent to *read* a tool's instructions before calling it — but
it is no longer the only thing standing between the instruction and the outcome: get the dispatch
wrong (wrong parent, wrong model, or skip it entirely) and the gate will not close, full stop, the
same way a wrong `--file` cannot silently succeed today.

**(d) One lifecycle tool or two, and why.** Two, and this candidate's own implementation is the
argument: `spine_open` and `spine_close` have **disjoint input schemas** (open requires five string
arguments naming a spine that does not exist yet; close requires **none**, because it acts
exclusively on the one spine its own process is already bound to) and **disjoint hazard classes**
(open's entire hazard is "did I address the right *new* location," which is a path-construction
problem; close's entire hazard is "did I move the *right, already-bound* file at the *right time*,"
which is an ordering problem). Folding both behind one `action` argument on a single tool would force
one input schema to carry both a to-be-created path (open) and nothing (close), and — more
concretely — would put both code paths inside one function that a future reviewer has to re-verify
carries no `SPINE`/`SESSION` reference on the open branch AND correctly *does* read them on the close
branch, which is precisely the "a guard written for one hazard covers the other by accident" failure
mode `_identity_violation`'s own docstring already lists as history (`--from-child` and `--delta`
sharing `_resolve_confined` is instructive by *contrast*: that sharing is safe because both flags
carry the exact same hazard — a caller-supplied path the engine will read. Open and close do not
share a hazard, so they should not share a function).

## 5. Where this constraint hurts

**No worktree/branch naming convention.** `spine_open` requires `branch`/`worktree`/`base` as
explicit caller-supplied strings rather than deriving them from `work_id` by a documented rule (e.g.
`epic-<n>/<slug>` and a sibling `-wt/` directory, the pattern visibly in use on this very run). Under
`smallest-diff` that derivation is one more function to write, one more thing to test (what happens
to a `work_id` with characters that are unsafe in a branch name or a path segment?), and one more
place a convention can drift from whatever a human actually types by hand elsewhere in the corpus.
Pushing it to the caller is strictly less code, but it means `spine_open` does not, by itself, fully
answer "how do I open work" — the caller still has to know the convention. `best-seam-placement`
would very plausibly centralize that convention inside the lifecycle module as one of its interface
guarantees, which is a genuine ergonomic win this candidate declines to buy.

**`close_work`'s home is a coin flip, not a forced move.** §2 places it in `init_work_area.py` "for
symmetry with `open_work`," but nothing about `close_work` actually needs anything `init_work_area.py`
already has (`init_work_area`, `resolve_spine`, `instantiate_spine` are all about *creating* a work
area; `close_work` only reads a spine and moves files). Under `smallest-diff` this is a defensible
"reuse the file that already plays this role in the corpus" call, but it is genuinely arbitrary, and
it means `init_work_area.py`'s name stops accurately describing its contents (it now also *tears
down* a work area). A reviewer who read only the filename would not guess `close_work` lives there.

**The `not_yet_written` fix is a spec-shape refusal, which is stricter than "add an isinstance
guard" literally reads.** The handoff's wording ("add an isinstance guard") most naturally reads as a
narrow type-check at the two existing call sites, which would be smaller than what this candidate
proposes (a new fault code, threaded through `_cond_faults`, with its own fixtures and its own
`DESIGN_NOTE.md` update). This candidate chose the stricter reading because a silent isinstance-only
guard reproduces the exact silence the generator's own charter refuses ("a wrong [check] does not
announce itself") — but it is a larger diff than the minimal literal instruction, and it is worth the
Commander's explicit sign-off rather than assuming it at plan time.

**One reviewer gate for four implementer gates.** `smallest-diff` argues for as few gates as cover
the properties, which pushed this candidate toward one `g5` review covering `g1`–`g4` together rather
than a review after each. The corpus's stated doctrine is "independent reviewer every time" — this
candidate is stretching "every time" to mean "every *epic*," not "every gate," on the grounds that
`g1` and `g4` carry no destructive operation and do not need the same scrutiny as `g2`/`g3`. That is
an interpretation call, not a measured fact, and `best-seam-placement` might reasonably run a review
per gate instead, at real wall-clock cost (per the design-it-twice brief, candidates are serial, not
parallel).

## 6. Scoring

| Axis | Self-score | Why |
|---|---|---|
| **Depth** | High | The caller learns almost nothing new: two tool calls, one with five required strings and one with none, both riding the already-registered `spine` server. No new module to learn beyond one small verifier script's own CLI. |
| **Locality** | Medium | A change to the close ordering touches exactly one function (`close_work`), but that function's *placement* is arbitrary (§5), so "which file do I open to change close" is not self-evident the way it would be with a dedicated lifecycle module. |
| **Seam placement** | Medium-low | The boundary is real (open/close are genuinely disjoint, §4d) but it is drawn at *function* granularity inside files that already do adjacent-but-different work, not at a place a test can address by a stable public name the way `checklist_engine.advance` or `generate_spine.compile_spec` can. A test for "did close archive correctly" imports `init_work_area.close_work` — a function sitting in a file whose docstring is entirely about *creating* work areas. |
| **Testability** | High | Every required property (rollback, occupied-worktree refusal, close ordering) is a plain Python function callable directly in a unit test, with no MCP transport in the loop for the unit-level fixtures (the JSON-RPC-over-subprocess tests, matching `test_mcp_identity.py`'s own style, are reserved for the tool-wiring layer only). |

**What it would lose to `best-seam-placement`.** A dedicated lifecycle module gets to *name* the
seam — `open_work`/`close_work` living somewhere whose docstring is entirely about the lifecycle
would resolve this candidate's locality and seam-placement weaknesses directly, and would very
plausibly also solve the naming-convention gap in §5 as a designed interface guarantee rather than a
pushed-to-caller omission. It would cost real new structure (a module, its own test file, a decision
about whether the MCP door and a future CLI both become adapters over it) that this candidate is
constitutionally required to avoid absent a property that cannot be met otherwise — and by this
candidate's own read, every required property *can* be met without it. Whether that trade is worth
paying is exactly the question the Commander is converging on.

## 7. Measurements that contradict or refine the mission frame

None contradict. Two are refinements worth the Commander's attention because they are load-bearing
for this candidate specifically and were not spelled out at the granularity `g2`/`g3` need:

1. **The identity pin's `call_tool`-direct sweep will KeyError on the two new tool names unless
   scoped.** This is not in `MISSION_FRAME.md`'s claim table (item 3, "the pass-through door is still
   pass-through," states the *destination* property but not this specific mechanical trap in the
   *test that proves it*). Re-verified live by reading
   `tests/test_mcp_identity.py::IdentityBindingPinTests.test_no_argument_can_change_what_the_door_reads_or_where_it_reads_it`
   end to end (lines ~914–1063 of that file): it iterates `module.TOOLS` and calls
   `module.call_tool(tool["name"], ...)` for every entry, with no filter. Any candidate that adds
   `spine_open`/`spine_close` to `TOOLS` without touching this test either breaks it immediately (loud,
   safe) or invites a "fix" that puts the new tools inside `call_tool` (silent, exactly the regression
   the pin exists to prevent). §4(a) and `g2`'s close criteria name the required, scoped edit
   explicitly so this is decided at plan time, not discovered mid-implementation.

2. **`checklist_engine.claim()` already records a `worktree` field on `engine_session`** (verified,
   `scripts/checklist_engine.py:960-1046`; `spine_lease`'s own tool schema already exposes a
   `worktree` argument today). This is a *narrower* worktree record than the `origin` block this
   candidate proposes — it is set by whoever claims the lease, is not necessarily the worktree the
   spine was *opened* in (a resumed session could claim from anywhere), and does not survive a
   `release` the way `origin` (immutable, written once at open) does. It does not contradict the Q2
   answer, but it means an implementer reading `checklist_engine.py` cold will find a field that
   *looks* like it already solves this problem and is not the one this plan relies on — worth a
   one-line note in `LIFECYCLE_CONTRACT.md` at `g0` so `g2`'s reviewer does not mistake the two.

`python scripts/validate_spine.py --sweep --root .` re-run this turn: exactly **23** fault lines,
matching the frozen baseline. The full pytest suite (2824 passed / 3 skipped / 1121 subtests) was
**not** re-run in this planning pass — it is a ~2800-test suite and re-running it does not change a
plan document; every gate above names it as a close criterion instead, which is where a real
divergence would actually be caught.

## Workflow Feedback

**What helped:** `MISSION_FRAME.md`'s "decision pressure" section had already named the file
(`LIFECYCLE_CONTRACT.md`) and gate (`g0`) this candidate needed for its reasoning gate, and its
"structural measurements" table gave exact line numbers and re-runnable commands rather than prose
claims — both saved real verification time. `DESIGN_NOTE.md`'s `not_yet_written`/`CORRECTION` section
was an unusually good model for how to *write* a candidate: it argues from a measured, live-driven
counter-example rather than asserting a property, and this result tries to match that bar, especially
in §4 and §7.

**What got in the way:** the handoff's "add an isinstance guard" for the carried `not_yet_written`
finding reads as smaller than what turned out to be the right fix once I read the generator's own
stated ethos closely (see §5's third bullet) — a sentence distinguishing "guard = refuse loudly" from
"guard = coerce silently" in the launch order itself would have removed one judgment call this
candidate had to make and flag rather than resolve. Separately: `test_mcp_identity.py` is 1557 lines
and the load truncated it at line 1128 on the first read; the load-bearing fact for this plan (the
`call_tool`-direct sweep in `test_no_argument_can_change_what_the_door_reads_or_where_it_reads_it`)
was inside the truncated remainder and only surfaced because I went back for it specifically —
worth flagging in a future handoff that this file's back half carries a property later gates will
need, not just DC2/DC3 fixtures.
