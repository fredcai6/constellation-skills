# PLAN_ALT_B — issue #419, governor per-agent identity

**Candidate B of a design-it-twice comparison. This is a plan, not an implementation.**
Nothing outside this file is touched by the act of writing it.

---

## Constraint

**SEAM-FIRST / MAXIMUM TESTABILITY.**

The question *"which agent am I, and where is that agent's own transcript"* is treated as a real
interface with more than one caller, not as an expression inlined at each use site. The plan places
that interface deliberately, justifies the placement in deep-module terms, and optimizes for:

1. a **pure**, directly unit-testable identity function with no filesystem, environment, or clock
   dependency;
2. a test surface that exercises **every** failure mode without a live harness;
3. a shape where a **future third caller costs nothing**.

A larger diff is accepted where it buys those three. Where the larger diff does *not* buy them, it is
declined — that boundary is drawn explicitly in "What this constraint costs".

---

## Where the seam goes and why

### The placement

A new module, **`scripts/hooks/agent_scope.py`**, stdlib-only, side-effect-free at import, ~110 lines.
It exposes exactly one data shape and three functions:

```
AgentScope            frozen record: binding_key, transcript_path, is_subagent,
                      agent_id, agent_type, sidechain_expected
derive(payload)       PURE. dict -> AgentScope | None. No I/O, no env, no clock.
resolve(payload, *, exists=os.path.isfile)
                      derive() plus the ONE existence check, predicate injected.
line_matches_scope(line_obj, scope)
                      PURE. Does this transcript JSONL line belong to this scope?
```

`derive` computes:

| payload condition | binding_key | transcript_path | sidechain_expected |
|---|---|---|---|
| `session_id` present, no `agent_id` | `session_id` | payload's `transcript_path` | `False` |
| `session_id` + valid `agent_id` | `session_id + "#" + agent_id` | `Path(tp).with_suffix("") / "subagents" / f"agent-{agent_id}.jsonl"` | `True` |
| no `session_id` | `None` (fail closed) | — | — |
| `agent_id` present but `transcript_path` absent/blank | `None` (fail closed) | — | — |
| `agent_id` not a plain token (empty, non-str, contains `#`, `/`, `\`, or `..`) | `None` (fail closed) | — | — |

`resolve` returns `None` additionally when the derived transcript does not exist. **That is the whole
of the fail-closed rule, in one place:** `None` means bind nothing and write nothing, and there is no
code path in the module that can return the parent's transcript for a subagent scope.

The last row is not defensive decoration. `agent_id` is interpolated into a filesystem path
(`agent-{agent_id}.jsonl`), so it is a path-construction surface fed by a harness field this repo does
not own. Rejecting separators and `..` is a genuine failure mode with a genuine unit test, and it lives
at the seam because otherwise each of the four callers would have to remember it.

**Naming, deliberately:** *not* `agent_identity.py`. That name belongs to the ~250-line discovery
matcher the probe killed (PROBLEM_STATEMENT "the matcher does not ship"). Reusing the name would
invite a future reader to think the search-for-identity mechanism landed after all. `agent_scope.py`
names what it actually is: the acting agent's scope, handed over by the harness and normalized.

### The callers — why this is an interface and not a helper

| # | Caller | What it takes from the seam |
|---|---|---|
| 1 | `spine_rail.handle_post_tool_use` (claim/release writer) | `binding_key` |
| 2 | `spine_rail.decide_stop` / `decide_session_start` (lookup + bind-on-resume writer) | `binding_key` |
| 3 | `gauge_writer_hook.handle_post_tool_use` | `binding_key`, `transcript_path`, `sidechain_expected` |
| 4 | the one-time sweeper (g6) | key classification (`derive` semantics, read backwards) |
| 5 | the acceptance harness's assertion (g7) | the derivation it must independently predict |

Five call sites across three lifecycles (hook-time, one-time migration, acceptance). Callers 1–3 are
production; 4 and 5 exist because the change must be migrated and proven, and both would otherwise
re-implement the derivation by hand — which is how a migration script and the code it migrates drift
apart.

### The deletion test

**Delete `agent_scope.py`. Does complexity vanish, or reappear across N callers?**

It reappears. Six decisions travel with the identity question:

1. Is there an `agent_id` on this payload at all?
2. If so, what is the composite key's separator and field order?
3. How is the per-agent transcript path derived from the parent's?
4. Is that path present, and what happens when it is not?
5. What counts as a malformed `agent_id` (path injection, empty, non-string)?
6. Which `isSidechain` polarity does this scope expect?

Deleted, those six land in five places. The spine rail needs 1–5 (not 6). The gauge writer needs all
six. The sweeper needs 1, 2, 5 read in reverse. The acceptance harness needs 2, 3, 6 to state what it
expects. Every one of the six is a place where two call sites can silently disagree — and a
disagreement between the *writer* of the binding key and the *reader* of it is exactly the class of
defect this issue exists to fix (the store today is written under one key semantics and read under
another). So the module is load-bearing under the deletion test: **it hides six decisions behind a
one-argument interface, and its interface is strictly smaller than its implementation.**

**Contrast — the module that fails the same test.** Delete the prototype's `agent_identity.py`
matcher and complexity genuinely *does* vanish, because the harness hands over the value the matcher
was searching for. That is why the matcher does not ship and this module does. The deletion test is
the thing that distinguishes them; "it's a module, modules are good" is not.

### Depth and locality

- **Depth:** interface = one dict in, one small frozen record out. Implementation = five validation
  branches, a path derivation, a polarity rule, and an injected existence check. Interface strictly
  smaller than implementation. Passes.
- **Locality:** the payload-shape knowledge (`agent_id`, `agent_type`, `transcript_path`,
  `subagents/agent-<id>.jsonl`) is currently smeared across two hooks and a doc that is *wrong about
  it today*. After this change, one module knows the harness payload shape and one doc section
  documents it. Locality improves; it does not merely move.
- **Cost of a third caller:** `from-path load agent_scope; scope = agent_scope.resolve(payload)`. Two
  lines, zero new decisions. Except for one real exception, gated at g4: a caller that is a *shipped
  hook* also needs an installer companion declaration. That cost is named, not hidden.

### The considered alternative, and why it is rejected under this constraint

Put the same pure functions **inside `spine_rail.py`**. `gauge_writer_hook` already path-loads
`spine_rail`, and `SCRIPT_RUNTIME_COMPANIONS["gauge_writer_hook.py"] = ("spine_rail.py",)` already
declares it — so this option costs **zero** installer work and skips gate g4 entirely.

Rejected under constraint B, for two reasons that are specific rather than aesthetic:

1. `spine_rail.py` is ~600 lines of side-effecting file I/O whose module docstring states its
   PostToolUse job is *only* binding discovery. Importing it to reach one pure function drags the
   whole rail into the sweeper's and the acceptance harness's import graph — a wider interface for the
   non-hook callers, which is the opposite of what this constraint buys.
2. Testability: a dedicated module gets a dedicated test file whose *only* subject is the identity
   derivation. Folded into `test_spine_rail.py`, the identity tests compete for attention with the
   Stop-rail's escape-hatch tests and a failure reads as "the rail broke" rather than "the derivation
   broke".

Under a *minimum-diff* constraint this alternative wins outright. That is precisely the axis the
design-it-twice comparison should adjudicate, so it is recorded here rather than argued away.

---

## Gate list

Nine gates. Each is the smallest bite that ends in an independently checkable state.

---

### g0 — Pin the real payload corpus as a test fixture

**Changes:** copies `.agent-work/issue-419-governor-identity/evidence/probe-payloads.jsonl` verbatim to
`tests/fixtures/probe_payloads.jsonl`, plus `tests/fixtures/probe_payloads.meta.json` recording
harness version `2.1.222`, capture date, source path, and the sha256 of the payload file. No source
changes.

**Why first:** this is the gate that converts every later unit test from "a check over a dict I typed"
into "a check over real harness output". Without it, the whole unit layer is arguing with itself.

**Close criteria**
- The fixture is **byte-identical** to the evidence file (sha256 equal).
- A test asserts that equality against the recorded sha256, so a future hand-edit of the fixture fails
  the suite rather than silently weakening every test built on it.
- The 6 payloads decompose as observed: 3 parent-scope (no `agent_id`), 2 subagent-scope with distinct
  `agent_id`, 1 parent `Agent`-tool dispatch with no `agent_id`.

**Evidence:** both sha256 values; the passing pin test; the 3/2/1 decomposition printed from the
fixture by the test itself.

---

### g1 — The seam module, pure, with no callers

**Changes:** adds `scripts/hooks/agent_scope.py` and `tests/test_agent_scope.py`. Nothing imports the
new module yet; behavior of the shipped system is unchanged by this gate, by construction.

**Close criteria**
- `derive` is **total**: over the g0 corpus and over ~15 constructed malformed payloads it returns an
  `AgentScope` or `None` and never raises.
- `derive` is **pure**: a test that monkeypatches `os.path.isfile`, `os.path.exists`, and `open` in the
  module's namespace to raise, then calls `derive` over the whole corpus and gets the same results as
  the unpatched run. This is the assertion that keeps the I/O boundary honest as the module evolves.
- Every row of the derivation table above has a test, including all five fail-closed rows.
- `resolve` is tested with an **injected** `exists` predicate for both outcomes, so the I/O branch is
  covered with no filesystem involved.
- One test pins the derived path shape against a subagent transcript that **actually exists on this
  box** from the probe (`<slug>/<session_id>/subagents/agent-<agent_id>.jsonl`), not a fixture — the
  one place a real artifact, not a recording, is the oracle.
- `line_matches_scope` is tested in both polarities (below, g3, is where it is wired).

**Evidence:** `py -m pytest tests/test_agent_scope.py -v` output; a branch-by-branch table naming which
test covers each of the six hidden decisions; the real-path pin's resolved path and its line count.

---

### g2 — spine_rail writes and reads the composite key through the seam

**Changes:** `handle_post_tool_use` derives its outer key via `agent_scope.derive`, not from
`data["session_id"]`. `decide_stop` and `decide_session_start` derive their **lookup** key through the
same call, so exactly one expression in the repo knows what a binding key is. Fail-closed: scope
`None` ⇒ return `{}` with no write, at every one of the three sites.

**Close criteria**
- The **entire existing `tests/test_spine_rail.py` passes with no assertion edited.** If any existing
  assertion must change, this gate blocks and the change is adjudicated, because these payloads carry
  no `agent_id` and must therefore be strictly equivalent to today.
- New test: a subagent-scope claim payload writes `binding["<sid>#<agent_id>"]`, and the parent's bare
  `<sid>` entry is untouched in the same store.
- New test — **strict equivalence**: for every parent payload in the g0 corpus, the binding file
  produced by the new writer is byte-identical to the file produced by the pre-change writer for the
  same input. (Run once against the old function held in a fixture module; this is a one-shot
  equivalence proof, not a permanent test.)
- New test: subagent claim whose derived transcript does not exist ⇒ **the binding file is not created
  at all** (asserted by absence, not by an empty dict).
- Release under a subagent scope removes only that composite key's entry.

**Evidence:** full `test_spine_rail.py` run before and after with identical pass sets; the byte-diff of
the two binding files from the equivalence test (expected: empty); the composite-key store dumped.

---

### g3 — Gauge writer reads the acting agent's own transcript, correct polarity

**Changes:**
- `resolve_gauge_path(project_dir, binding_key)` — parameter renamed and re-meant from `session_id`.
  It stays a plain string so its own tests need no seam.
- `find_latest_usage(transcript_path, sidechain_expected)` — the `isSidechain` test becomes
  `bool(d.get("isSidechain")) == sidechain_expected`, delegated to `line_matches_scope`, which
  additionally requires `d.get("agentId") == scope.agent_id` on a subagent scope.
- `handle_post_tool_use` routes through `agent_scope.resolve`, using the scope's transcript and
  polarity.
- **Observability of the new skip cause.** When `resolve` returns `None` because the derived transcript
  is missing but `derive` returned a usable key, the writer resolves that key's gauge path and writes
  `gauge-skip.json` with reason `identity-transcript-missing`. This is the seam's split paying rent:
  `derive` still yields a *place to complain*, even when `resolve` refuses to yield a *reading*. When
  `derive` itself returns `None` there is no key and therefore no path, so that cause stays silent —
  the same class as today's zero-candidates.

**Close criteria**
- **Two-polarity test, mutually exclusive:** one transcript containing both a main-chain assistant line
  and a sidechain assistant line with different token totals. Parent scope must return the main-chain
  total; subagent scope must return the sidechain total. Deleting the filter fails one of the two —
  which is the property that makes this a real test (see the cannot-fail section).
- `tests/fixtures/real_subagent_transcript.jsonl` (already in the repo, 4 lines, all `isSidechain`,
  carrying `agentId`) is read successfully under a matching subagent scope and **rejected** under a
  non-matching `agent_id`.
- Missing derived transcript ⇒ no `gauge.json` write and exactly one `gauge-skip.json` with the new
  reason.
- `checklist_engine._skip_reason_advisory` renders the new reason string without an enum lookup —
  verified by calling it, not by reading it.
- Every touched test in `tests/test_gauge_writer.py` is **enumerated with its reason**, and each is
  classed as mechanical re-plumbing (signature) or genuine semantic change. A semantic change here
  needs a written justification.

**Evidence:** `pytest tests/test_gauge_writer.py tests/test_gauge_reader.py -v`; the enumerated touched-test
table; the advisory's rendered text for the new reason.

---

### g4 — Packaging closure for the new module

**Changes:** `SCRIPT_RUNTIME_COMPANIONS` gains `agent_scope.py` for **both** `gauge_writer_hook.py`
and `spine_rail.py` (the latter has no companion entry today because it loaded nothing);
`SCRIPT_SOURCE_SUBDIRS["agent_scope.py"] = "hooks"`; affected `SKILL_SCRIPT_BUNDLES` updated.

**Why this is its own gate:** a shipped hook that path-loads an undeclared sibling **breaks in every
consuming project** while passing every test in this repo, because in this repo the sibling is simply
there. This is the concrete price of the separate-module choice and it gets a gate rather than a
footnote.

**Close criteria**
- A test installs into a tmp dir and then **executes** the installed `gauge_writer_hook.py` as a
  subprocess with a real payload from the g0 fixture, from the installed location, asserting a
  `gauge.json` lands. Declaration-string assertions alone do not close this gate — the archive already
  records that the existing companion guard is a regex-only single-hop form.
- `test_install_constellation.py` passes in full.

**Evidence:** the tmp install tree listing showing `agent_scope.py` present under each bundle; the
subprocess run's exit code, stdout, and the written `gauge.json`.

---

### g5 — Documentation corrected (done-condition 4)

**Changes:** `docs/GAUGE_WRITER_HOOK.md`:
- the field table's `isSidechain` row becomes **scope-dependent polarity**, not "must be falsy";
- new rows for the payload's `agent_id` and `agent_type`;
- the binding-key section documents the composite `session_id#agent_id` key, that a parent keeps its
  bare `session_id`, and that `agent_scope.derive` is the **single owner** of that derivation;
- the enumerated skip causes gain `identity-transcript-missing`;
- the fan-out/ambiguity paragraph is corrected: per-agent keying makes "exactly one" true again for a
  dispatched agent, and states the residual it does **not** close (a genuine orchestrator holding N
  spines is still ambiguous — #202/#261's known cost, per the issue's own out-of-scope ruling).

**Close criteria:** a claim-by-claim table where every factual assertion in the touched sections cites
the file and line of the code as it stands *after* g1–g4. Any claim that cannot be cited is deleted
from the doc rather than softened.

**Evidence:** the doc diff; the claim→code-citation table.

---

### g6 — One-time sweep of the stale bare-key bindings (done-condition 5)

**Changes:** a temporary `scripts/one_time/sweep_stale_bindings.py`, deleted before this gate closes.

**The rule, stated before the code exists.** Remove a binding entry iff its spine file is absent **or**
its recorded lease `status != "active"`. Never remove an entry whose lease is live. **Never re-key an
existing entry** — nothing in the store records which agent wrote it, so re-keying would be a guess,
and a guess about attribution is the exact defect this issue exists to eliminate. Bare keys that
survive the rule are left to self-heal as those sessions re-claim under the g2 writer.

**Order, non-negotiable:**
1. **Dry run.** Writes `evidence/binding-before.json` (verbatim copy of the live store) and
   `evidence/sweep-plan.json` (every key and entry it would remove, each annotated with which clause of
   the rule fired). Mutates nothing.
2. **Real run.** Writes `evidence/binding-after.json`.
3. **Compare.** The actual before→after delta must equal the plan exactly.
4. **Delete the sweeper.**

**Close criteria**
- `binding-before.json` exists and is recorded before any mutation, with its own sha256.
- Actual delta == planned delta, asserted by a comparison whose output is captured, not eyeballed.
- The post-sweep store loads cleanly through `spine_rail.load_binding` with no entry dropped by the
  old-shape filter.
- No entry with an active lease was removed (asserted over the before-state, independently of the
  sweeper's own logging).
- `scripts/one_time/sweep_stale_bindings.py` does not exist at gate close (`git status` clean of it).

**Evidence:** the three JSON artifacts + sha256s; the delta comparison output; the key-count before and
after against the recorded live baseline (6 session keys / 54 bindings at the time of this run);
`git status`.

---

### g7 — Live acceptance: a real trip from a per-agent reading (done-condition 6)

**The only vehicle.** `CLAUDE_PROJECT_DIR` is fixed at session launch, so an agent dispatched into this
worktree runs the **main checkout's** hook code. Therefore: a fresh headless
`claude -p --settings <abs settings file>` whose hook commands name **this worktree's**
`scripts/hooks/spine_rail.py` and `scripts/hooks/gauge_writer_hook.py` by absolute path — the same
vehicle the pre-build probe already proved end to end. `gauge_writer_hook` registers with matcher `*`
(it must see every tool call); `spine_rail` keeps Stop / SessionStart / PostToolUse.

**Shape of the run.** The parent dispatches **two concurrent subagents**, each of which:
- claims its **own** spine in its **own** `.agent-work/<id>/` under a scratch root,
- then diverges: **HEAVY** genuinely consumes context by reading real repo file content until it passes
  a band; **LIGHT** makes one trivial tool call and stops,
- then each runs `checklist_engine.py current` against its own spine, and attempts `advance`.

**Close criteria — all five required.**

| # | Criterion |
|---|---|
| a | The binding store holds two **distinct** composite keys `<sid>#<agent_id_A>` and `<sid>#<agent_id_B>`, alongside the parent's bare `<sid>`. |
| b | Two `gauge.json` files, one per subagent work dir, with **materially different** `fill_fraction`. |
| c | HEAVY's `current` carries the trip; LIGHT's carries no trip. |
| d | The `agent_id` in each binding key equals the `agentId` on the lines of the per-agent transcript the reading was actually taken from. |
| e | Nothing in the run hand-injected `agent_id`: the settings file and both dispatch prompts are captured verbatim and contain no such value. |

**Trip target and the fallback ruling.** Target **HARD** (`fill >= 0.15` on a 1M-window model =
150,000 real tokens), because HARD produces a *refusal* — `_trip_hard_gate` blocks `advance` — and a
refused command is falsifiable in a way a rendered advisory string is not. If HEAVY cannot cross 0.15
within a bounded budget of **3 attempts**, the gate closes on a **SOFT** trip (`fill >= 0.08` =
80,000 tokens; the engine renders `CONTEXT NN% (>= soft)`) with the achieved fill recorded and the
HARD shortfall filed as a **scoped null** — "this specific target was not reached in 3 attempts",
never "HARD is unreachable". Criteria (b) and (d) are **not** subject to that fallback; they hold in
either case.

**Evidence:** the settings file; both dispatch prompts verbatim; the binding store snapshot; both
`gauge.json` files; both engine `current` outputs verbatim; HEAVY's refused `advance` output verbatim
(or, under the fallback, HEAVY's SOFT advisory plus the recorded fill); both per-agent transcript
paths with line counts and the `agentId` values read from them.

---

### g8 — Broader suite and reconcile

**Changes:** none to source beyond anything the suite exposes. Files the residual as a triage
candidate.

**Close criteria**
- Full `pytest tests/` passes.
- The residual is filed, not silently absorbed: `_foreign_worktree` inside `_entry_mid_flight_view`
  exists to suppress subagent-claimed entries sitting under the parent's key. Composite keying removes
  most of what that guard was defending against, so it becomes **mostly dead**. It is **not deleted in
  this run** — deleting it is a behavior change to the Stop rail, outside this issue's scope — it is
  filed as a triage candidate with the reasoning attached.
- The parent-orchestrator multi-binding gap is restated as still open (per the issue's own out-of-scope
  ruling), so nobody later reads this run as having closed it.

**Evidence:** full suite output; the filed triage candidate.

---

## How the acceptance gate proves a trip actually fired

Three properties, stacked, each closing a hole the one before it leaves open.

**1. The differential is the proof of attribution.** Two concurrent subagents under one `session_id`,
with deliberately different consumption, must produce **two gauge readings with materially different
fill**. A parent-transcript fallback — the exact misattribution #202/#261 ruled against, and the
failure this issue exists to prevent — produces **identical** fills for both, because both would be
reading the same file. So the differential cannot be satisfied by the broken behavior. "A gauge.json
appeared under the subagent's work dir" is *not* a close criterion, because a fallback satisfies it
too.

**2. The trip is proved by a refusal, not by a string.** At HARD, `_trip_hard_gate` blocks `advance`
until a `refresh-request` is filed. A refused command with captured output is the trip *acting*. The
SOFT advisory (`CONTEXT NN% (>= soft)`) is a rendered string; it does discharge the letter of "a trip
fires", but it is the fallback, and the plan says so up front rather than discovering the distinction
after the fact.

**3. The negative control closes the coincidence.** LIGHT reaches no band and therefore shows **no**
trip in the same run, on the same harness, under the same `session_id`, with the same hooks wired. So
the observed trip is attributable to HEAVY's own fill and not to any run-wide condition.

**And the constraint that guards all three:** every `agent_id` in the run originates in the harness.
The settings file and both prompts are captured verbatim as evidence precisely so that this is
inspectable rather than asserted. A fixture that hand-injects `agent_id` to prove the harness delivers
`agent_id` is forbidden, and criterion (e) exists to make that forbiddenness checkable.

---

## Migration and back-compat for the existing binding-store shape

**The store's shape does not change. Only its key space widens.**

Today: `{session_id: {abs_spine_path: {spine, engine_session, worktree, claimed_at}}}`.
After: the outer key is `session_id` **or** `session_id#agent_id`. Inner structure untouched. The
frozen four-field gauge record is untouched. `load_binding`'s old-flat-shape filter
(`_is_old_shape_binding_entry`) is untouched and keeps working, because the value shape is unchanged.

**Why the composite key is unambiguous.** A harness `session_id` is a UUID and an `agent_id` is a
plain hex token (observed: `a8f0a946eaaa2fe6c`); neither contains `#`. The seam rejects any `agent_id`
containing `#`, so a composite key always splits on `rsplit("#", 1)`. Only the sweeper needs to split
one; production code only ever *constructs* keys, never parses them.

**Forward compat.** A bare key is still exactly what a parent writes, so pre-change entries for parents
remain correct and readable with no migration at all.

**The genuinely stale part, and what is done about it.** Pre-change entries written *by subagents* are
sitting under the parent's bare key, misattributed. Nothing in the store records who wrote an entry, so
they cannot be identified, let alone re-keyed. The sweep therefore removes only what is **provably
dead** — absent spine file, or a lease that is not active — and leaves everything else to self-heal on
the next claim under the new writer. This is a deliberate under-reach: a sweeper that guessed which
bare entries "look like" subagent entries would be re-introducing exactly the attribution guess this
issue removes.

**Rollback.** Reverting g2 restores bare-key writing; composite keys left in the store are then simply
never looked up, and age out under the same dead-entry rule. No destructive migration to undo.

---

## Which tests are legitimate, and which would be checks that cannot fail

### Legitimate unit tests over a pure function

These are legitimate because their **input is the contract** and their **output is the derivation**,
and the derivation is the thing that can be wrong. They may *assume* the payload shape; they may never
*assert* it.

1. **Derivation table coverage (g1).** For each of the six table rows, assert the key, the transcript
   path, and the polarity. Fails on a wrong separator, wrong field order, wrong path segment, or a
   missing fail-closed branch.
2. **Purity (g1).** Patch `os.path.isfile` / `os.path.exists` / `open` in the module namespace to
   raise; `derive` must produce identical results. Fails the moment someone adds an I/O call to the
   pure half.
3. **Injected-existence branches (g1).** `resolve` with `exists=lambda p: True` and
   `exists=lambda p: False`. Fails if the fail-closed branch is dropped.
4. **Malformed `agent_id` rejection (g1).** Empty, non-string, `..`, `/`, `\`, `#`. Fails if the path
   surface is left open.
5. **Two-polarity transcript selection (g3).** One transcript, both a main-chain and a sidechain
   assistant line with **different** token totals; parent scope must get one, subagent scope the other.
   Deleting the filter makes one of the two fail — that mutual exclusivity is what gives the test
   teeth.
6. **Strict parent equivalence (g2).** Old writer vs new writer over the g0 parent payloads, byte-diff
   of the resulting binding files. Fails on any unintended change to existing behavior.
7. **Installed-hook execution (g4).** Executes the *installed* hook as a subprocess. Fails if a runtime
   companion is undeclared — the failure mode a declaration-string assertion is blind to.
8. **Sweep plan == sweep delta (g6).** Fails if the sweeper's stated intent and its actual mutation
   diverge.

Their inputs are real harness output, pinned by sha256 at g0. That is what keeps (1)–(4) from being
arguments with a dict I typed myself.

### Checks that cannot fail — named, and ruled out

1. **Injecting `agent_id` into a payload and asserting `agent_id` is present.** Circular, and
   explicitly forbidden by the mission frame. **Ruled out.** Replaced by g7 criterion (e): the settings
   file and prompts are captured verbatim and contain no injected value; the ids come from the harness
   or the gate does not close.
2. **"A `gauge.json` exists under the subagent's work dir."** A parent-transcript fallback — the
   defect — also creates that file. The check passes while the bug is live. **Ruled out.** Replaced by
   the differential, g7 criterion (b).
3. **A sidechain test whose fixture contains *only* sidechain lines.** It passes with the filter
   inverted, and it passes with the filter **deleted entirely**. **Ruled out.** Replaced by the
   two-polarity mutually-exclusive test (g3).
4. **"The sweeper ran and the store still parses."** True of a sweeper that does nothing, and true of a
   sweeper that deletes everything. **Ruled out.** Replaced by plan-equals-delta plus the independent
   assertion that no live-lease entry was removed, computed from the before-state rather than from the
   sweeper's own log.
5. **"`SCRIPT_RUNTIME_COMPANIONS` contains the string `agent_scope.py`."** Asserts a declaration, not a
   closure; the repo's own archive records that the existing companion guard is a regex-only single-hop
   form that would miss a real gap. **Ruled out.** Replaced by executing the installed hook (g4).
6. **"A trip advisory string appeared somewhere in the run's output."** The parent could produce one;
   a stale gauge from an unrelated spine could produce one. **Ruled out.** Replaced by: the trip must be
   observed on HEAVY's *own* spine, with LIGHT as a same-run negative control, and at HARD it must be a
   refused `advance` rather than rendered text.
7. **"The full suite still passes."** Necessary, never sufficient — it passed before the change too,
   with the defect live. Kept at g8 as a regression floor, **not counted** as evidence for any
   done-condition.

---

## The three biggest risks this constraint creates

**1. Seam ossification around a single-probe observation.** The record's vocabulary — `binding_key`,
derived `transcript_path`, `sidechain_expected` — freezes an interpretation of harness fields observed
on **one** build (2.1.222) in **one** probe. If a later harness ships a direct
`agent_transcript_path`, or changes the `subagents/` layout, the seam is the wrong shape and now four
callers depend on it — the failure a well-placed seam is supposed to prevent, arriving through the
seam itself. *Mitigations:* the record carries only **derived facts**, never policy; the module
docstring pins the harness version the derivation was observed on and names the probe evidence file;
the module is capped at ~110 lines so replacing it costs less than repairing it. Additionally, g1's
real-path pin fails loudly (rather than silently reading nothing) if the layout moves.

**2. A green unit suite outrunning live truth.** Eight fast, thorough tests over a pure function feel
like proof and cost 200ms. Every one of their inputs is a **recording**. The live layer is one
expensive run on one harness build. That asymmetry is exactly how "all tests pass, the governor is
still blind" survives — the state this issue is fixing today. *Mitigations:* exactly one g1 test uses a
**real artifact on disk** rather than a fixture as its oracle; g7 is non-optional and cannot be
discharged by any unit result; and the g7 differential is designed so the *specific* broken behavior
(parent-transcript fallback) fails it, rather than being merely absent from it.

**3. A larger diff landing on a live, shared, fail-open rail.** Routing `decide_stop` and
`decide_session_start` through the seam touches the Stop rail — a mechanism whose failure modes are
*blocking honest turns* and *silently ceasing to block dishonest ones*, neither of which any identity
unit test can see. "Accept a larger diff" is precisely where a regression in the 3-strike escape hatch
or the foreign-worktree guard would hide. *Mitigations:* the Stop/SessionStart change is **key
derivation only** — one expression swapped, no control flow touched; g2 will not close if any existing
`test_spine_rail.py` assertion needs editing; and the strict-equivalence byte-diff proves parent
behavior is unchanged rather than merely still-passing. Secondarily, a fourth risk is folded in here
because it shares the mitigation: the new `identity-transcript-missing` skip sidecar is a new writer
output on a live path, and g3 requires the engine's advisory to *render* it (verified by calling), not
merely to tolerate it.

---

## What this constraint costs

**Files and volume.** +3 files (`agent_scope.py`, `tests/test_agent_scope.py`,
`tests/fixtures/probe_payloads.jsonl` + its meta), ~400 lines including tests, for what a minimum-diff
candidate could express as roughly 30 lines edited across two existing files. Roughly a 10x volume
multiplier on a change whose *logic* is small.

**Signature churn.** `resolve_gauge_path`'s parameter is re-meant and `find_latest_usage` gains one.
Both ripple into `tests/test_gauge_writer.py` as **re-plumbing that adds no coverage** — pure churn
that a reviewer must read and confirm is inert. g3 therefore requires each touched test to be
enumerated and classed, which is itself extra work the constraint creates.

**A real packaging cost, gated at g4.** A third path-loaded module is not free in this repo: it needs
`SCRIPT_RUNTIME_COMPANIONS` entries under **both** hooks, a `SCRIPT_SOURCE_SUBDIRS` row, and bundle
updates — and if any of that is missed, the hook **breaks in every consuming project while every test
here passes**. This is the sharpest single cost of choosing a separate module over folding the
functions into `spine_rail.py`, and it is why g4 demands an executed installed hook rather than a
string assertion. The alternative placement skips this gate entirely.

**Gates.** Nine instead of the five or six a minimum-diff plan would need — g0 (fixture pinning) and g4
(packaging) exist *only* because of this constraint.

**What the cost buys, stated plainly so the comparison is fair.** One place in the repo knows what a
binding key is and where an agent's transcript lives; every failure mode is reachable from a unit test
in under a second with no harness; the path-injection surface on `agent_id` is closed once instead of
four times; the sweeper and the acceptance harness predict the derivation from the same code that
performs it rather than re-deriving it by hand; and a future caller adds two lines. Whether that is
worth roughly 10x the diff on a change this size is exactly the question the design-it-twice comparison
exists to answer — and this plan does **not** claim it obviously is.
