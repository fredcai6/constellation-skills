# PLAN_ALT_A — candidate A: MINIMUM DIFF

Issue #419, epic-418 workstream A. One of two candidate gate plans authored independently for a
design-it-twice comparison. **Nothing here is implemented.** This document is a plan only.

---

## Constraint

**Make the trip fire with the smallest possible change to shipped code.**

Operationally, that means:

- **No new module under `scripts/`.** The two existing hook files are edited in place.
- **No new mechanism where a shipped one already covers the case.** The `gauge-skip.json` sidecar
  family and the engine's forward-compatible unknown-reason advisory already exist; a new fail-closed
  cause costs one call site and zero engine changes.
- **Every added line is load-bearing for one of the six done-conditions**, or for keeping a shipped
  behavior from regressing as a side effect of those lines.
- **Minimum diff means minimum *behavior* change too.** Where re-keying the store would silently
  narrow an existing reader's view, the plan restores that view rather than accepting a quiet
  regression it did not set out to make.
- Optimizing for: a diff a reviewer can hold in their head, and the smallest surface that can regress.

The payload already carries `agent_id` (probe, six real payloads, harness 2.1.222). Identity is a
dictionary lookup, not a search. Under this constraint the whole change is therefore: **compose a
different outer key, read a different transcript file, invert one boolean.**

### What this plan explicitly does NOT change

The gauge record stays frozen at four fields. `gauge_reader.py` is untouched. `checklist_engine.py` is
untouched. `_foreign_worktree` stays exactly as it is. The nudge/escape-hatch ledger stays keyed by
bare `session_id`. `TAIL_BYTES`, `MODEL_WINDOWS`, `_is_contained`, the atomic-write path, and both
sidecar families keep their current shapes. No binding-file schema version is introduced (there never
was one).

### Estimated diff

| file | added | removed | nature |
|---|---|---|---|
| `scripts/hooks/spine_rail.py` | ~20 | ~4 | two pure helpers + key substitution at three sites |
| `scripts/hooks/gauge_writer_hook.py` | ~22 | ~6 | one pure helper + one param + one branch |
| `docs/GAUGE_WRITER_HOOK.md` | ~16 | ~6 | field table, binding shape, skip-cause list |
| `tests/test_spine_rail.py`, `tests/test_gauge_writer.py` | ~120 | 0 | pure-function tests only |
| throwaway (deleted before close) | — | — | sweeper + acceptance harness, both outside `scripts/` |

---

## Gate list

Ordering property that holds at **every** gate boundary: the system is never worse than it is today.
Each gate either narrows uncertainty or leaves it where it was. No intermediate state can produce a
*wrong* reading — only no reading. This is what makes the small bites safe to land separately.

Test-class labels used below, per the hard constraint:
**[unit]** = pure function over data the test constructs — legitimate, expected, and *not* proof that
the harness delivers anything. **[live]** = a real headless `claude -p` run. Only [live] evidence can
discharge done-condition 6.

---

### g1 — Per-agent binding key in the store (write side + preserved read views)

**Done-conditions served:** 1.

**What it changes** — `scripts/hooks/spine_rail.py` only:

1. New module constant and two pure helpers:
   - `BINDING_KEY_SEP = "#"`
   - `binding_key(data) -> str | None` — returns `f"{session_id}#{agent_id}"` when the payload carries
     a non-empty string `agent_id`, else bare `session_id`, else `None`. This is the **single place**
     the composite key is composed anywhere in the codebase; `gauge_writer_hook.py` calls it through
     the `_spine_rail` module handle it already loads, so the two hooks cannot drift.
   - `session_view(binding, sid) -> dict` — merged `{abs_spine_path: entry}` across the bare `sid` key
     and every `sid + "#"`-prefixed key.
2. `handle_post_tool_use`: `sid = data.get("session_id")` becomes `key = binding_key(data)`; the claim
   write, the release delete, and the empty-set cleanup all use `key`.
   **The nudge deletion on release keeps the bare `sid`** — the escape-hatch ledger is documented as
   keyed by `sid` ALONE and `decide_stop` writes it under bare `sid`. Splitting it per-agent would
   weaken the 3-strike hatch. This asymmetry is deliberate and must be called out in the diff, or a
   reviewer will read it as a missed substitution.
3. `decide_stop`: `binding.get(sid) or {}` becomes `session_view(binding, sid)`.
4. `decide_session_start`: same substitution on the **read**. The bind-on-resume **write** stays under
   bare `sid` — `SessionStart` never carries `agent_id` (subagents do not get one), so a resumed
   session is by definition top-level.

**Why the union read is non-regression, not scope creep:** today every subagent entry already lives
under the parent's bare `sid`, so `session_view(binding, sid)` returns *exactly the set today's
`binding.get(sid)` returns*. Without it, re-keying would silently stop the Stop rail from deterring a
parent that ends its turn while a same-cwd subagent's spine is open — a deterrent regression invisible
to every test in the suite. Four lines to hold behavior still.

**Close criteria**

- `binding_key` returns the composite form iff `agent_id` is a non-empty string; bare `sid` when
  `agent_id` is absent, empty, whitespace, or a non-string; `None` when `session_id` is falsy.
- A claim carrying `agent_id` writes under `sid#agent_id` and leaves the bare `sid` entry set byte-
  identical. Two distinct `agent_id`s on one `session_id` produce two independent key sets.
- A release carrying `agent_id` removes only that agent's entry.
- `decide_stop` and `decide_session_start` return **identical** results before and after, for a store
  populated only with bare keys.
- `tests/test_spine_rail.py` passes unchanged apart from additions.

**Evidence**

- [unit] New tests in `tests/test_spine_rail.py`: key composition table; claim/release isolation
  between two agent ids; `session_view` union; a golden before/after assertion that a bare-key-only
  store yields the same `decide_stop` verdict.
- [command] `py -m pytest tests/test_spine_rail.py -q`.

---

### g2 — The gauge writer attributes to the acting agent (composite lookup + own transcript + fail-closed)

**Done-conditions served:** 1 (read side), 2 (path half), 3.

**These three edits cannot be split.** Looking up the composite key without also switching transcripts
would write the *parent's* fill to the *subagent's* gauge path — the exact misattribution #202/#261
ruled against. Splitting the fail-closed check off would do the same on a missing derived transcript.
One gate.

**What it changes** — `scripts/hooks/gauge_writer_hook.py` only:

1. `resolve_gauge_path(project_dir, session_id)` → parameter renamed to `binding_key`, docstring line
   updated. Body is otherwise unchanged (`binding.get(binding_key)`). The two existing tests call it
   positionally, so the rename is safe.
2. New pure helper `_subagent_transcript(parent_path, agent_id) -> Path | None`:
   `Path(parent).with_suffix("") / "subagents" / f"agent-{agent_id}.jsonl"`, wrapped, `None` on any
   exception. Path shape confirmed to exist by the probe.
3. `handle_post_tool_use`, after `gauge_path = gauge_paths[0]`:
   - the lookup becomes
     `resolve_gauge_path(project_dir, _spine_rail.binding_key(data) if _spine_rail else None)`;
   - if `data.get("agent_id")` is present, `transcript_path` is replaced by the derived path, and if
     that file does not exist the hook writes `_write_skip_flag(gauge_path, "subagent-transcript-missing")`
     and returns. **No fallback to the parent's transcript, ever.**

**Why the new skip reason costs nothing:** `gauge_reader.skip_reason` does not whitelist reason
strings, and `checklist_engine._skip_reason_advisory` already ends in a forward-compatible branch that
renders an unrecognized reason verbatim. So the one drift mode this plan *can* surface becomes visible
in the engine's own output with zero engine change.

**State after g2, before g3:** a subagent's derived transcript is found, every line in it is
`isSidechain: true`, `find_latest_usage` skips them all, `compute_record` returns `(None, None)`, and
the hook writes `no-usable-record`. No reading, no wrong reading. Safe to land alone.

**Close criteria**

- With a store keyed `sid#a1` and a payload carrying `agent_id="a1"`, exactly one candidate resolves,
  and it is a1's spine. With the same payload and a store holding only bare `sid`, **zero** candidates
  resolve (a subagent never inherits the parent's binding).
- A payload with no `agent_id` behaves exactly as today.
- `agent_id` present + derived transcript absent ⇒ no `gauge.json` write, no `gauge-uncalibrated.json`
  write, and a `gauge-skip.json` carrying `reason: "subagent-transcript-missing"`.
- No code path passes a parent transcript to `compute_record` when `agent_id` is present. Verifiable
  by reading the single branch.

**Evidence**

- [unit] `_subagent_transcript` path-shape test against the literal layout the probe recorded.
- [unit] `resolve_gauge_path` under composite and bare keys.
- [unit] Fail-closed test: temp dirs, `agent_id` set, derived file deliberately absent; assert
  `gauge.json` unchanged on disk (mtime + bytes) and the skip sidecar's reason.
- [command] `py -m pytest tests/test_gauge_writer.py -q`.

---

### g3 — Sidechain polarity, tied to the agent it belongs to

**Done-conditions served:** 2 (reading half).

**What it changes** — one signature and one filter in `gauge_writer_hook.py`:

- `find_latest_usage(transcript_path, agent_id=None)`. When `agent_id is None`, the filter is today's:
  skip anything with truthy `isSidechain`. When `agent_id` is given, the filter **inverts and
  tightens**: the line must be `isSidechain` truthy **and** `d.get("agentId") == agent_id`.
- `compute_record(transcript_path, agent_id=None)` passes it through.
- The handler passes `agent_id=data.get("agent_id")`.

**One parameter, not two.** "This is agent X's own transcript" is a single fact; expressing it as
`expect_sidechain` + `expect_agent_id` would let a caller set an incoherent pair. The `agentId`
equality check is the cheap guard that makes a wrong *derived path* fail closed instead of producing a
confidently misattributed number.

**Close criteria**

- `find_latest_usage(tests/fixtures/real_subagent_transcript.jsonl)` (default polarity) still returns
  `None` — the existing assertion at `tests/test_gauge_writer.py:427` stays green, unedited.
- `find_latest_usage(<same fixture>, agent_id="af45cec63b2835a40")` returns
  `("claude-opus-4-8", 21022, "2026-07-07T05:30:40.581Z")` — a hand-computed expectation from a
  **real captured subagent transcript** already in the repo (4823 + 1088 + 15111).
- The same call with a *different* `agent_id` returns `None`.
- `compute_record(<fixture>, agent_id="af45cec63b2835a40")` yields `fill_fraction == 21022/1_000_000`.
- The golden main-chain transcript test is unaffected.

**Evidence**

- [unit] The four assertions above.
- [command] `py -m pytest tests/test_gauge_writer.py tests/test_gauge_reader.py -q`.
- Note in the gate record: this fixture is real captured harness output, but the test still only
  proves the *parser*. It proves nothing about delivery — that is g5's job, and the gate record must
  say so rather than let a green suite imply coverage it does not have.

---

### g4 — Correct `docs/GAUGE_WRITER_HOOK.md`

**Done-conditions served:** 4.

**What it changes** — four edits, prose only:

1. Field table row `isSidechain` (line ~213): today it reads "must be falsy". Replace with the
   polarity rule — falsy for a main-chain read, **truthy** for a subagent's own transcript — and add
   an `agentId` row (top-level, must equal the payload's `agent_id`).
2. A short second table for the **payload** fields the hook reads: `transcript_path`, `session_id`,
   `agent_id` (present only on a subagent's tool call — the fact the whole fix rests on), `agent_type`.
3. The binding-shape paragraph (line ~318): the outer key is now `session_id` for a top-level agent
   and `session_id#agent_id` for a dispatched one; the "exactly one spine" coupling now holds
   per-agent; the residual parent-orchestrator-with-N-spines ambiguity survives and is named as
   surviving.
4. The skip-cause list (~248–290): add `subagent-transcript-missing`, stating the fail-closed rule in
   the doc's own voice — never fall back to the parent's transcript.

**Close criteria**

- No sentence in the document asserts the pre-fix polarity anywhere (grep `falsy`, `isSidechain`,
  `sidechain` and read every hit).
- Every field the shipped code reads appears in one of the two tables, and no field appears that the
  code does not read.
- The doc's own claim about which key the binding uses matches `binding_key`'s implementation.

**Evidence**

- The diff, plus a recorded grep transcript of `isSidechain|sidechain|falsy|session_id` over the doc
  with each hit adjudicated in the gate record.

---

### g5 — Acceptance: a real trip, from a per-agent reading, on a live run

**Done-conditions served:** 6 (and the live confirmation of 1, 2, 3).

**What it changes:** nothing under version control. The harness is throwaway, lives outside `scripts/`
in the scratchpad, and is not committed.

**Vehicle.** A fresh headless `claude -p` launched with `--settings <file>` naming **this worktree's**
hooks by absolute path, cwd set to a clean sandbox so `CLAUDE_PROJECT_DIR` resolves to the sandbox and
the live main-checkout binding store is never touched. This is precisely the vehicle the pre-build
probe already proved end to end.

**Sandbox.** `<scratch>/accept419/` containing `.agent-work/accept419-work/spine.json` — a real gated
spine created by **this worktree's** `checklist_engine.py`, with at least two gates so there is a real
`advance` to refuse. A generated ~800 KB plain-text corpus in the sandbox, split into chunks, as
genuine reading material.

**Two arms, one variable.** Only the hook path differs.

- **Arm A (control):** settings point at `C:/Programs/constellation-skills/scripts/hooks/…` — the
  unmodified shipped hooks.
- **Arm B (treatment):** settings point at `C:/Programs/constellation-skills-wt/epic418-a-419/scripts/hooks/…`.

**Run shape (identical in both arms).** The parent dispatches **one** subagent on a 1M-window model
present in `MODEL_WINDOWS` (`claude-sonnet-5` or `claude-opus-5`). The subagent is told to: claim the
sandbox spine through the worktree engine; read the corpus chunk by chunk; run
`checklist_engine.py … current` between chunks and report its output **verbatim**; when it believes it
is done reading, attempt `advance` and report verbatim whatever comes back. It is **not** told what
output to expect, what a trip is, or what number to reach. Target fill ≥ 0.15 (HARD, 150 K tokens
against a 1 M window); ≥ 0.08 (SOFT) is recorded on the way as an intermediate observation.

**Nothing in the settings file, the prompt, or the sandbox mentions `agent_id`.** `grep -ri "agent_id"`
over the entire acceptance harness returning zero hits is itself a recorded piece of evidence — the
harness cannot be accused of handing the hook the value it is supposed to discover.

**Which band discharges the done-condition:** **HARD.** The MISSION_FRAME leaves this open; this plan
resolves it to HARD because HARD is a *refusal* — `advance` raises and the gate does not move, which
leaves a falsifiable trace in the spine state file itself. SOFT is an advisory suffix on a string, and
a string can be misread. SOFT-only is a **fallback that escalates**: recorded, floated to the Admiral
as a partial discharge, never quietly counted as done. (The `ROLLOUT CAVEAT` against exercising HARD in
production does not bind here — the sandbox is disposable and holds no real work.)

**Close criteria** — all seven, in Arm B:

1. `<sandbox>/.agent-work/.spine-rail-binding.json` holds exactly one key matching `<uuid>#<hex>`, and
   its entry's `spine` is the sandbox spine.
2. `~/.claude/projects/<slug>/<session_id>/subagents/agent-<agent_id>.jsonl` exists, and the
   `<agent_id>` in that filename equals the `#`-suffix of the binding key.
3. `gauge.json` exists beside the sandbox spine, `fill_fraction >= 0.15`, `model` is the dispatched
   model.
4. **The attribution proof.** Recomputing the reading independently: the last `assistant` line of the
   subagent's own transcript, summed over the three usage fields, divided by 1 000 000, **equals**
   `gauge.json`'s `fill_fraction`. The same computation over the *parent's* transcript
   (`<session_id>.jsonl`) yields a **materially different** value, below `soft`.
5. The subagent's verbatim report contains `CONTEXT` + `(>= hard)` from `current`, and the `advance`
   attempt returned the engine's refusal text (`… is at/over the hard limit — advancing is blocked
   until you request a refresh …`).
6. The sandbox spine state file shows the gate **did not advance** (still `in-progress`), and the
   journal carries no advance record at that moment.
7. Arm A, same script: no `gauge.json` at that path (or a `gauge-skip.json` with
   `ambiguous-binding`), no `CONTEXT` line in the subagent's report, and `advance` succeeded.

**Evidence** (all archived under `.agent-work/issue-419-governor-identity/evidence/`)

- Both settings files, the launch commands, and both arms' full stdout.
- The binding store snapshot from each arm.
- Both `gauge.json` files (or the absence, recorded as a directory listing).
- Copies of the subagent transcript and the parent transcript, plus the recomputation script's output
  showing the two fill numbers side by side.
- The sandbox spine + journal after each arm.
- The zero-hit `agent_id` grep over the harness.

---

### g6 — Sweep the live binding store

**Done-conditions served:** 5.

**Precondition:** the fixed hook is the code live sessions actually execute — i.e. the change is on
`main` in `C:/Programs/constellation-skills`. Sweeping before that is pointless: the old writer
immediately re-accumulates bare-key entries. If the merge has not happened at this point, the gate
records the sweep as **pending-on-merge** and says so out loud rather than running early.

**Measured now, in the live store:** 6 session keys, 54 entries — one key holding 36, one holding 10,
and the session dispatching this epic holding 5.

**What it changes:** `C:/Programs/constellation-skills/.agent-work/.spine-rail-binding.json`, once.

**Sweeper location:** `.agent-work/issue-419-governor-identity/mechanical/sweep_stale_bindings.py` —
deliberately **not** under `scripts/`, because it is not a shipped capability and the constraint
forbids one. Deleted in g7.

**Staleness rule (the only rule; anything else is left alone):** drop an entry iff its `spine` file
does not exist, **or** the spine's `engine_session.status` is not `"active"`. A live parent binding
under a bare key is legitimate and must survive — the sweep removes *dead* entries, not *bare* ones.

**Sequence, in order, no step skippable:**

1. **Dry run.** Copy the store verbatim to `evidence/binding-before.json`. Emit
   `evidence/binding-sweep-plan.md`: every one of the 54 entries with key, spine path, spine-exists,
   lease status, and KEEP/DROP with the reason. Record the totals.
2. **Real run**, writing atomically via the same tmp+`os.replace` discipline the hooks use.
3. **Verify.** Snapshot to `evidence/binding-after.json`; assert the diff is exactly the DROP set from
   step 1 and nothing else; assert every KEEP entry is byte-identical.
4. **Delete the sweeper.**

**Close criteria**

- `binding-before.json` exists and predates the mutation.
- The before→after diff is exactly the planned DROP set — no entry dropped that the plan did not name,
  no entry kept that it did.
- Every surviving entry's spine file exists and its lease is active.
- The sweeper file no longer exists.

**Evidence:** the three artifacts above, the sweeper's own stdout for both runs, and a `git status`
showing the sweeper gone.

---

### g7 — Closeout

**Done-conditions served:** all six, jointly re-confirmed.

**What it changes:** nothing.

**Close criteria**

- `py -m pytest -q` — the full suite, green. Per the project rigor delta, the targeted tests are not
  enough on their own for a workflow mechanism.
- The complete diff reviewed against the constraint: no new file under `scripts/`; exactly two source
  files touched; every added line traceable to a numbered done-condition or to the named
  non-regression obligation in g1. Any line that fails that trace is deleted.
- All six done-conditions mapped to their closing gate and evidence artifact in one table.
- Sweeper deleted, acceptance harness outside the repo, `git status` clean apart from the intended diff.

**Evidence:** the suite output, the reviewed diff, the done-condition→evidence table.

---

## How the acceptance gate proves a trip actually fired

The claim to be proven is a chain of four links. Breaking any one of them fails the gate; none of the
four can be satisfied by the harness handing the hook an answer.

**Link 1 — the harness delivered the identity, we did not.** The binding store contains a key of the
form `<uuid>#<hex>`. Nothing in the settings file, the launch command, the sandbox, or the prompt
contains the string `agent_id` (recorded grep, zero hits). The only route by which that hex could
reach the store is `PostToolUse` stdin. Confirmed independently: the same hex names a real transcript
file the harness created at `…/<session_id>/subagents/agent-<hex>.jsonl`.

**Link 2 — the reading came from the agent's own context, not its parent's.** Two numbers, both
computed after the run by re-reading the raw transcripts: the subagent's own tail usage sum, and the
parent's. The first equals `gauge.json`'s `fill_fraction` to float precision. The second does not, and
sits below `soft`. This is the load-bearing measurement of the whole issue — it is what distinguishes
"a reading appeared" (the thing the done-condition explicitly refuses to accept) from "*this agent's*
reading appeared". If the two numbers coincide, the gate fails as misattribution regardless of whether
a trip fired.

**Link 3 — the fill is real, not staged.** The tokens got there by the subagent genuinely reading an
800 KB corpus into its own window, chunk by chunk. No fixture, no injected record, no edited
`gauge.json`. The `observed_at` in `gauge.json` falls between the subagent's first and last chunk
reads — checkable against the transcript's own timestamps.

**Link 4 — the trip actually fired, and fired *because of that reading*.** Not "the code path that
would trip was reached" — the engine refused. `advance` returned the hard-limit refusal text, and the
spine state file shows the gate still `in-progress` afterward. The refusal quotes the fill percentage,
which matches `gauge.json`, which matches link 2's subagent number. And Arm A — byte-identical script,
unmodified hooks, same corpus, same model — produced no reading and advanced normally. The only
variable between "silent governor" and "engine refuses to advance" is the hook code this gate plan
changes.

**Named falsifiers.** Any of these fails the gate rather than being explained away: the binding key is
bare; the two fill numbers in link 2 match each other; `observed_at` predates the subagent's first
chunk read (a stale or parent-sourced record); `advance` succeeded despite a `>= hard` reading; Arm A
also tripped (then the change is not what caused it); or the subagent's report is paraphrased rather
than verbatim.

---

## Migration and back-compat for the existing binding-store shape

**No migration code ships. None is needed** — this is the strongest property of the minimum-diff
constraint and it should be weighed accordingly in the comparison.

- **The shape does not change.** `{outer_key: {abs_spine_path: {spine, engine_session, worktree,
  claimed_at}}}` is untouched. Only the *alphabet of the outer key* widens: previously always a bare
  `session_id`, now also `session_id#agent_id`. `load_binding` never interpreted the outer key; it
  iterates and filters on the *value's* shape.
- **The old-shape guard is untouched.** `_is_old_shape_binding_entry` still drops pre-#202 flat
  entries. That path is orthogonal and gets no new behavior.
- **Old entries stay meaningful.** A bare key written before this change still means "this session's
  binding". Read by the new code as a top-level agent's binding — which, for a parent, is exactly
  right. Nothing needs rewriting; nothing is misread.
- **Mixed writers coexist safely.** Between the merge and every live session restarting, the same file
  is written by both the old code (bare keys) and the new (composite). They never collide: a bare key
  and `bare#agent` are distinct keys, and each writer only ever mutates its own. Worst case during the
  overlap is today's ambiguity persisting for old sessions — no wrong reading is possible.
- **The key is self-describing.** Presence of `#` distinguishes the two forms with no version field
  and no lookup table. Session ids are UUIDs and cannot contain `#`; `session_view`'s prefix match on
  `sid + "#"` is safe even if an agent id someday did.
- **Downgrade is clean.** Reverting the two files leaves composite keys in the store as inert entries
  the old reader simply never matches. They are dead weight, not corruption — and the same staleness
  rule g6 uses would collect them.
- **One accepted collision.** `session_view` merges per-spine dicts across keys, so if two agents under
  one session claimed the *identical absolute spine path*, the merged view keeps one entry. Only
  `decide_stop`/`decide_session_start` consume the merged view, and both only need the *set of spine
  paths*, which is unaffected. Recorded as an accepted, bounded residual.

---

## The three biggest risks this constraint creates

**1. The proof is a one-off, and the failure mode is silence.**
The only evidence that any of this works end to end is a manual live run that CI can never repeat —
hand-injecting `agent_id` is forbidden, and minimum-diff forbids building the test vehicle or module
that could make the live run repeatable. So the moment g5's artifacts are archived, this mechanism is
unguarded forever. And its failure mode is *silence*: if the harness renames `agent_id`, `binding_key`
quietly falls back to a bare key, the store returns to today's ambiguity, and every symptom is
identical to a governor that is merely idle. Partial mitigation: the *other* drift mode — the
`subagents/agent-<id>.jsonl` layout changing — is made visible for one line of cost via the new
`subagent-transcript-missing` skip reason, which the engine already knows how to render. The
`agent_id`-rename mode stays fully silent. A reviewer should read this as the price of the constraint,
not as an oversight.

**2. The behavior most at risk is the one nothing tests.**
The g1 union read exists purely to stop the Stop rail from silently losing its deterrent. It is fiddly
in a way that does not announce itself: the nudge ledger stays bare-`sid` while bindings go composite,
the merged view can collide on identical spine paths, and the prefix match must not catch a different
session whose id happens to be a prefix. Get any of it wrong and there is no wrong number and no red
test — there is a parent that ends its turn mid-spine and nobody notices for weeks. Unit tests can pin
the helpers; they cannot pin the live rail.

**3. Unbounded key growth in a shared store, with the reaper deleted by mandate.**
Every dispatched subagent now mints a new outer key, and a key is only removed by a successful
`release`. Agents that die, are cancelled, or are killed mid-run leave their key behind forever. The
live store is already at 54 entries under 6 keys with no housekeeping; per-agent keying multiplies the
*key* count by the fan-out factor of every wave. Minimum diff ships no reaper and g6 deletes the
sweeper by mandate, so the next cleanup is another hand-written throwaway. Meanwhile `session_view`
scans every key on **every Stop and every SessionStart** — O(keys), on a file that now grows per
subagent rather than per session. Nothing here is urgent; all of it compounds.

---

## What this constraint makes me unable to do

- **Give identity a seam.** There is no `agent_identity.py`, so there is no single place that owns
  "who is acting", no versioned contract for it, and no home for a fallback if the harness ever stops
  supplying `agent_id`. The knowledge is spread across two hook files, held together only by the
  convention that one calls the other's helper.
- **Make the live proof repeatable.** No test vehicle, no recorded-payload replay harness, no fixture
  path that could re-run g5's chain automatically. Every future change in this area will face the same
  manual, expensive, judgment-heavy acceptance run — or, more likely, will skip it.
- **Serve any consumer but the trip.** Per-agent identity is genuinely useful to episode capture, the
  crew launcher, and the feedback channel. Inlined into two hooks, it is unavailable to all of them;
  the next consumer re-derives it or lifts it, and at that point the "one place" property of
  `binding_key` is gone.
- **Instrument identity resolution.** The MISSION_FRAME's decision pressure — does resolution duration
  ride the gauge record or a sidecar — is answered here by *not measuring it*. Resolution is a
  dictionary lookup from an argument already in hand, so there is nothing to measure; but the answer is
  "no instrument", and if that assumption ever stops holding, nothing will say so.
- **Refactor around what the change exposes.** `resolve_gauge_path` still takes what it now calls a
  binding key while living beside code that says `session_id` everywhere; `handle_post_tool_use` still
  interleaves transcript checks and path resolution in an order that only just accommodates the
  fail-closed branch. Both are left as they are, because reviewability of the diff was the thing being
  optimized.
- **Close the parent-orchestrator gap.** An orchestrator legitimately holding N spines under one bare
  key stays ambiguous and stays silent. Out of scope by the issue's own words — but worth naming that
  this constraint has no path to it even if scope reopened.
