# Implementation Result

## Assigned gate

`g1-implement` — a gauge reading is named for the agent that produced it (#600),
under `LAUNCH_ORDER.md` as amended by `ADMIRAL_RULING-1.md` R1–R5.

## Completed slice

A gauge reading now belongs to an **agent** instead of to a **folder**.

- `scripts/gauge_reader.py` gains the **one** definition of the owner key —
  `owner_key()` (slug + 12-hex SHA-256, total over every string),
  `gauge_filename()`, `GAUGE_FILENAME`, and `record_owner()`.
- `scripts/hooks/gauge_writer_hook.py` loads that module by path and writes
  `gauge-<owner>.json`, stamping a matching `owner` field into the record. Its
  ambiguity guard became a question about **attribution** rather than count.
- `scripts/checklist_engine.py` resolves the same name from its own active
  lease's `session_id`. With **no lease** it reads the unowned `gauge.json` and
  trips on it exactly as today.

Driven through the engine as `.agent-work/cleanup-b-context-identity/crew-handoffs/g1-implementer-plan.json`
(m0-context → m1-owner-key → m2-writer → m3-engine → m4-evidence → m5-result).

## Scope

**Files changed:**

- `scripts/gauge_reader.py`
- `scripts/hooks/gauge_writer_hook.py`
- `scripts/checklist_engine.py` — gauge/trip region only
- `tests/test_gauge_reader.py`, `tests/test_gauge_writer.py`,
  `tests/test_checklist_engine.py`, `tests/test_gauge_chain_writer_to_trip.py`
- `docs/GAUGE_WRITER_HOOK.md`, `docs/CHECKLIST_SCHEMA.md`
- **Outside the handoff's Allowed Scope — flagged, see below:**
  `scripts/install_constellation.py`, `tests/test_install_constellation.py`,
  `map/INDEX.md`

**Specific exclusions touched:** **no.** `scripts/hooks/spine_rail.py`,
`tests/test_spine_rail.py`, `scripts/run_crew.py`, `scripts/mcp_spine_server.py`,
`.mcp.json`, `episodes/**` and `measurement/probe_cross_key.py` are all
byte-identical (`git diff HEAD` empty for each). `spine_rail.py`'s `gauge.json`
mention at `:769` needed **no** edit, as the handoff predicted — it is a comment
about a check that keys on `items`. The **claim path** in `checklist_engine.py`
is untouched.

### The three scope extensions, and why

1. **`scripts/install_constellation.py` (+ its test).** The full suite caught
   what my own Wiring Grep could not. `gauge_reader.py` had to be declared a
   runtime companion of `gauge_writer_hook.py`, and the guard test
   (`test_gauge_writer_hook_dynamic_loads_are_declared_as_companions`) hardcodes
   the expected set and says in its own docstring to "update
   SCRIPT_RUNTIME_COMPANIONS and this expectation together".

   Chasing it surfaced a **real defect in my first draft**: the install
   destination is **flat** (`SCRIPT_SOURCE_SUBDIRS`' own comment says so), so a
   loader written only for this checkout's `scripts/hooks/` + `scripts/` layout
   would have failed in **every install** — silently, into no owner, leaving the
   writer producing `gauge.json` while a leased engine read `gauge-<owner>.json`.
   That is a **dark** governor, not merely an inert one, and it is the exact
   shape of the bug the companion mechanism was built for after the Context
   Governor shipped inert everywhere. `_load_gauge_reader` now tries both
   locations, and `test_installed_gauge_writer_hook_actually_loads_its_gauge_reader`
   installs the skill and drives the real loader against the installed layout.

   I judged this required rather than optional: criterion 6 mandates the by-path
   load, and shipping it without the companion declaration would break installs.
   Reviewer may reverse it cheaply — it is one tuple entry, one loader loop, one
   test.

2. **`map/INDEX.md`.** `test_code_map.py::MapTreeFreshnessTests` went red on
   entity counts and names its own remedy. I ran `py -m scripts.code_map build
   --root .`; the diff is 13 lines of counts and nothing else.
   **`map/ids.jsonl` is still 0 bytes**, so the map's recorded `DEGRADED`
   status is unchanged. The per-module packets the build also produced are
   **gitignored** (`.gitignore:73 map/*`) and are not deliverables.

## Behavior changed

**Yes.**

- Two agents whose spines share one work directory each keep their own reading.
- A record carries an `owner` field whenever the writer can attribute it, and a
  field that disagrees with its filename declines the reading **visibly**.
- The `len(candidates) > 1` skip no longer fires when every candidate resolves
  to one owner — that everyday case (a Commander leasing both its `spine.json`
  and its `execute.json`) now gets a reading where it used to get silence.
- **Nothing refuses where it previously permitted.** Every change is in the
  permit or the quiet direction. `_owner_mismatch` only ever suppresses a
  reading, and HARD cannot fire without one.

## The measured defect, and the departure I am flagging

### `decision:ambiguity-guard-is-about-attribution` — I narrowed R4's literal wording

R4 says: "dedupe by resolved owner-keyed path, write **every** distinct
candidate, and fire the guard only when a candidate cannot be attributed an
owner at all."

I implemented that in two of its three branches and **narrowed the third**:

| candidates | owners | behaviour |
|---|---|---|
| 1 | any | write (unchanged) |
| 2+ | all one owner | **write every candidate** — R4 as ruled |
| 2+ | any candidate with **no** owner | skip + `ambiguous-binding` sidecars — R4 as ruled |
| 2+ | **two or more distinct owners** | skip + sidecars — **my departure** |

**The argument.** Two distinct owners under **one binding key** means two agents
reached through one harness identity, and there is exactly **one transcript** to
read. Writing that record to both files files agent A's context fill against
agent B. That is the fan-out the Map Anchors name as a recorded dead end — tried,
measured, and reverted in #202/#261 — and the handoff says do not re-propose it.

R4's stated *rationale* is fully satisfied by what I built: the guard existed
because the writer "could not tell **whose** reading it held", and one owner
answers that. What owner-keying removes is the **overwrite**; it does not tell
two agents' readings apart, which is the cross-write the dead end is about. So
the ruling's reasoning and the recorded dead end conflict only in this one
branch, and I took the conservative side — it is identical to today's behaviour
there, so it cannot make the governor louder or wronger than it already is.

**Grade: a guess, raised here.** It is a one-line condition
(`len(owners) > 1` in `handle_post_tool_use`) and trivially reversible if the
Admiral wants the literal reading. I did not want to take it quietly in either
direction.

### `decision:sidecar-name` (criterion 7) — the sidecars stay per-directory and unowned

Stated explicitly, as required, rather than left to fall out.
`SKIP_FILENAME`/`UNCALIBRATED_FILENAME` remain constants on both sides.

- The `ambiguous-binding` skip is **by definition** a case with no owner to name.
- An uncalibrated model is a **standing defect in this repo's tables**, equally
  true for everyone at that path, not an agent-specific observation.
- Both are advisory-only and never refuse anything, so a shared advisory is at
  worst shown to an agent it does not concern — the same as today.
- They resolve via `.with_name(...)` from whatever gauge path they are handed, so
  they keep working unchanged from the owned and unowned paths alike, with **zero**
  reader change and no risk of losing a visible advisory.

**Grade: a guess.** The residual is that one owner's `no-usable-record` advisory
can be rendered to another owner sharing the directory.

### `decision:one-owner-key-definition` (criterion 6) — followed, not departed from

Defined once in `scripts/gauge_reader.py`, loaded in the hook through the
existing by-path loader idiom, load failure yields no owner (today's behaviour).

### `decision:no-lease-keeps-todays-behaviour` (R3) — followed, and symmetric

The engine side and the writer side agree: **no owner ⇒ the unowned
`gauge.json`**. On the writer that is a binding entry with no usable
`engine_session` (the live store in the main checkout carries `None` entries
right now); on the engine it is no lease, a released lease, or nothing to key on.
Where a lease **does** name an owner and no such file exists, the answer is
`None` — **no fallback** to the shared file.

### `decision:identity-not-time` — **not completed**, as R1 requires me to say

This wave fixes the **concurrent** collision. It does **not** complete
`identity-not-time`; passing the harness identity into the engine remains the
only route to that and was out of scope.

## Blast radius (Wiring Grep), reconciled

**At dispatch, the Commander enumerated 21 files.** I reproduce **21 files** with
that exact command — the file count matches.

**Occurrence count differs, and the Commander's was low.** The handoff cites
"125 occurrences" across 5 test files with "`test_gauge_writer.py` alone has 64".
Counting *occurrences* (`grep -o | wc -l`) rather than *matching lines*
(`grep -c`) gives **68 lines / 68 occurrences** for that file and **219
occurrences over 21 files** overall. I believe the dispatch figure counted
matching lines on some files and occurrences on others.

**One classification correction.** The Commander's "5 code" includes
`skills/commander/templates/COMMANDER_SPINE.template.json`, which is a **spine
template, not code**, and is **outside Allowed Scope**. Its single mention is
prose inside a `context_headroom_note` explaining that "`gauge.json` keeps only
the latest reading" — **still true**, and true of `gauge-<owner>.json` too.
**No change.**

**After the change: 23 tracked files / 186 occurrences.** The two added files are
`scripts/install_constellation.py` and `tests/test_install_constellation.py`,
which acquired the literal **only through prose I wrote** in the comments
explaining the companion declaration.

**Zero occurrences was correctly the wrong target** — under R3 the literal
survives on the leaseless read path.

### Per-occurrence disposition

| file | occ. | disposition |
|---|---|---|
| `scripts/gauge_reader.py` | 5 | **CHANGED** — `GAUGE_FILENAME` is now the unowned name; sidecar constants unchanged |
| `scripts/hooks/gauge_writer_hook.py` | 25 | **CHANGED** — resolution, write loop, docstrings |
| `scripts/checklist_engine.py` | 5 | **CHANGED** — `_gauge_path` composes the name; unowned literal survives as the leaseless fallback |
| `scripts/install_constellation.py` | 1 | **CHANGED** — new prose in the companion comment |
| `tests/test_gauge_writer.py` | 20 | **CHANGED** — path expectations moved to pinned `GAUGE`/`GAUGE2`; remaining literals are the unowned-path tests and the `_atomic_write_json` primitive test |
| `tests/test_checklist_engine.py` | 31 | **CHANGED** — `_write_gauge` writes the acting session's file; leaseless cases pass `session_id=None` |
| `tests/test_gauge_chain_writer_to_trip.py` | 37 | **CHANGED** — existing chain pinned to the leaseless path; new owned chain added |
| `tests/test_gauge_reader.py` | 13 | **CHANGED** — `OwnerKeyNormalization` added |
| `tests/test_install_constellation.py` | 2 | **CHANGED** — new prose + installed-layout test |
| `docs/GAUGE_WRITER_HOOK.md` | 19 | **CHANGED** — new `#600` section, 3 corrected passages, skip enumeration rewritten |
| `docs/CHECKLIST_SCHEMA.md` | 1 | **CHANGED** — "Which file" paragraph added to the Trip section |
| `scripts/hooks/spine_rail.py` | 1 | **no change** — fenced; comment keys on `items`, not the filename, as predicted |
| `tests/test_spine_rail.py` | 2 | **no change** — fenced (cold critic F11) |
| `skills/commander/templates/COMMANDER_SPINE.template.json` | 1 | **no change** — prose still true; outside scope |
| `episodes/active/*.md` (7 files) | 15 | **no change** — historical records, never edited |
| `notes-1.md`, `notes-b.md` | 8 | **no change** — this epic's own measurement notes, describing the pre-fix world truthfully |

## Test mode

**Required:** test-first.
**Satisfied:** yes — red observed at the merge base, for the right reason, over
**behaviour** as well as symbol absence; the real reader and real gauge files on
disk throughout; no patched `_read_gauge`; no fixture hand-injecting
`CLAUDE_PROJECT_DIR` on the engine side.

## TDD evidence

### RED, at the merge base

`git diff --stat a69bbac4 -- scripts/` was **empty** when this ran, so the source
under test was byte-for-byte the merge base.

```
$ find . -name __pycache__ -type d -prune -exec rm -rf {} + ; env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q <the four node ids>

FAILED tests/test_gauge_writer.py::OwnerKeyedGaugePath::test_two_keys_one_work_dir_each_keep_their_own_reading
FAILED tests/test_gauge_writer.py::OwnerKeyedGaugePath::test_two_spines_one_key_one_owner_still_writes
SUBFAILED(session_id='admiral-epic-178') tests/test_gauge_reader.py::OwnerKeyNormalization::test_every_live_session_id_yields_a_usable_owner
SUBFAILED(session_id='cartographer/epic-178') ...
SUBFAILED(session_id='constellation/cleanup-b-context-identity/g1/implementer/attempt-1') ...
SUBFAILED(session_id='$SID') ...
SUBFAILED(session_id='$SESSION') ...
   [14 subtests, one per live session id]
FAILED tests/test_checklist_engine.py::TripGaugeReadingOwnership::test_leaseless_checklist_reads_the_unowned_gauge
16 failed, 1 passed in 0.31s
```

The mechanical reason is symbol absence:

```
E   AttributeError: module 'gauge_reader' has no attribute 'gauge_filename'
E   AttributeError: module 'gauge_reader' has no attribute 'owner_key'
```

**The behavioural red — the right reason — is the fresh-process demonstration**,
run against that same merge-base source
(`measurement/demo_owner_keyed_gauge.before.out`):

```
files written in the one work directory:
  execute.json
  gauge.json
  spine.json

DISPATCHED agent's file  : gauge.json
  -> {... 'fill_fraction': 0.9 ...}
ORCHESTRATOR's file      : gauge.json
  -> {... 'fill_fraction': 0.9 ...}
shared gauge.json        : {... 'fill_fraction': 0.9 ...}
gauge-skip.json          : None

VERDICT: COLLISION -- both agents resolve to ONE file, gauge.json.
  The surviving fill is 0.9; the other agent's reading was destroyed with no
  skip sidecar and no guard.
```

That reproduces `probe_cross_key.py`'s measurement exactly: 0.9 destroys 0.02,
nothing notices.

### GREEN, at my head

```
$ env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q <the same four node ids>
4 passed, 13 subtests passed in 0.19s
```

The same demonstration script, unedited, against the fixed source
(`measurement/demo_owner_keyed_gauge.after.out`):

```
files written in the one work directory:
  execute.json
  gauge-owner-dispatched-b6445a5eac4f.json
  gauge-owner-orchestrator-8c6bb04ff8f5.json
  spine.json

DISPATCHED agent's file  : gauge-owner-dispatched-b6445a5eac4f.json
  -> {'schema_version': 1, 'fill_fraction': 0.02, 'model': 'claude-opus-4-8', 'observed_at': '2026-08-16T12:00:00.000Z', 'owner': 'owner-dispatched-b6445a5eac4f'}
ORCHESTRATOR's file      : gauge-owner-orchestrator-8c6bb04ff8f5.json
  -> {'schema_version': 1, 'fill_fraction': 0.9, 'model': 'claude-opus-4-8', 'observed_at': '2026-08-16T12:00:00.000Z', 'owner': 'owner-orchestrator-8c6bb04ff8f5'}
shared gauge.json        : None
gauge-skip.json          : None

VERDICT: EACH AGENT KEPT ITS OWN READING.
```

**`measurement/probe_cross_key.py` was not edited** — confirmed by
`git diff HEAD -- .../probe_cross_key.py` returning empty. The demonstration is a
**new** artifact at `.agent-work/cleanup-b-context-identity/measurement/demo_owner_keyed_gauge.py`,
written to be direction-agnostic so the same script run before and after is the
evidence, with no edit in between to argue about.

**Refactor while green:** yes — the map rebuild and the installer companion work
were done after green and re-verified.

## Evidence — verification commands, pasted

### Command 1 (handoff verbatim)

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity && \
  find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
    tests/test_gauge_writer.py tests/test_gauge_reader.py \
    tests/test_checklist_engine.py tests/test_gauge_chain_writer_to_trip.py
```

**Result: pass.**

```
616 passed, 237 subtests passed in 4.77s
```

### Command 2 (handoff verbatim)

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity && \
  find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

**Result: pass.**

```
3072 passed, 6 skipped, 1164 subtests passed in 126.49s (0:02:06)
```

### The baseline, measured rather than quoted

The handoff cites 3057 passed at dispatch. I measured it myself in a clean
detached worktree at `a69bbac4`:

```
3057 passed, 7 skipped, 1146 subtests passed in 124.39s (0:02:04)
```

**The delta reconciles exactly, with no pre-existing test changing status:**

- **+14** new tests (enumerated by `git diff a69bbac4 -- tests/ | grep -cE '^\+\s*def test_'`).
- **+1** from a test that *skipped* only in my baseline checkout:
  `tests/test_spine_lifecycle.py:161` skips when the checkout is not under the
  `<wt_root>/<work-slug>` convention, and I measured the baseline in `/tmp`. It
  runs and passes in this worktree.

3057 + 14 + 1 = **3072**. 7 − 1 = **6 skipped**.

### #601's timestamp comparison — still present, still fires

Confirmed, as criterion 9 requires. `_reading_predates_claim` is at
`scripts/checklist_engine.py:1518`, unmodified, and its behaviour is pinned:

```
$ py -m pytest -q \
    tests/test_checklist_engine.py::TripGaugeReadingOwnership::test_a_relaunch_reclaim_restamps_claimed_at \
    tests/test_checklist_engine.py::TripGaugeReadingOwnership::test_leg_ones_reading_stops_refusing_leg_two_after_its_own_reclaim \
    tests/test_checklist_engine.py::TripGaugeReadingOwnership::test_reading_sampled_before_the_claim_does_not_refuse_begin_work \
    tests/test_checklist_engine.py::TripGaugeReadingOwnership::test_a_self_measured_reading_over_hard_still_refuses
4 passed in 0.05s
```

Those four now drive **owner-keyed** files (their `_write_gauge` helper writes the
acting session's own file), so they prove the two halves compose: identity picks
the file, time decides whether the reading in it is this leg's.

### Deliverable path check

`git check-ignore <path>` exits **1** (not ignored) for every changed file,
including the three scope extensions and the new demonstration script.

## Docs/contracts touched

- `docs/GAUGE_WRITER_HOOK.md` — new section "The reading belongs to an agent, not
  to a folder (#600)"; steps 2 and 4 of the opening list corrected; the
  four-fields section extended; the "Skip-on-uncertainty, enumerated" ambiguous-
  binding bullet rewritten to the attribution question.
- `docs/CHECKLIST_SCHEMA.md` — "Which file (#600)" added to the Trip section.

## Map Impact

- **Structural anchors touched:** the map is **DEGRADED** (`map/ids.jsonl` empty,
  no `docs/architecture/` packets), so there are no citable anchor ids. Against
  the hash-pinned substitute entry point recorded in `map-orientation.json`:
  `scripts.gauge_reader`, `scripts.hooks.gauge_writer_hook`,
  `scripts.checklist_engine` (gauge/trip region), plus the newly-implicated
  `scripts.install_constellation` (runtime-companion declaration).
- **Capabilities changed:** a context reading is attributable to an agent;
  concurrent agents in one work directory no longer clobber each other; the
  everyday one-agent-two-spines case gains a reading it previously lost to the
  ambiguity skip.
- **Constraints/assumptions touched:** *newly relied on* —
  `binding_entry.engine_session == lease.session_id`, true by construction
  because the entry is parsed from the `claim --session-id` that creates the
  lease. *Newly relied on* — the installer's **flat** destination layout, which
  the two-location loader depends on. **Honored:** the governor never refuses
  where it previously permitted; fail-open on every uncertainty; silence stays
  visible.
- **Decisions:** `decision:owner-in-the-filename` (settled, implemented as
  filename **and** field); `decision:normalize-never-reject` (settled);
  `decision:no-lease-keeps-todays-behaviour` (settled, symmetric on both sides);
  `decision:one-owner-key-definition` (guess, followed);
  `decision:unattributable-means-no-reading` (implemented as no fallback);
  `decision:ambiguity-guard-is-about-attribution` (**narrowed — see above**);
  `decision:sidecar-name` (**raised and answered here** — per-directory,
  unowned); `decision:identity-not-time` (**not completed**, per R1);
  `decision:no-schema-change` — **stressed**: the record gains an `owner` field.
  It rides the same additive bargain `identity_resolution_ms` already struck
  (`gauge_reader` validates its four REQUIRED fields and does not reject
  extras), so it costs no reader change, but it is a second additive field and
  the "frozen four" is now four-required-plus-two-optional.
- **Trust limitations / drift found:** the map's DEGRADED state is unchanged —
  `map/ids.jsonl` is still empty after the rebuild. `map/INDEX.md`'s entity
  counts were stale relative to `scripts/` and are now current.
- **Triage candidates:**
  1. **Cross-lane note to the Admiral (as instructed).** This design **reads**
     `spine_rail.is_usable_agent_id`'s alphabet reasoning, which couples it to a
     module **lane C may change**. I read it and deliberately did **not** copy
     its refusal (R2). Nothing imports it; the coupling is conceptual, in the
     character class `_OWNER_UNSAFE` uses.
  2. **Sidecar advisories can be shown to the wrong owner** when two owners share
     a work directory (see `decision:sidecar-name`). Advisory-only, never
     refuses. Not fixed here.
  3. **`_clear_skip_flag`'s known residual widens slightly.** Sidecars stay
     per-directory while readings are now per-owner, so a stale
     `gauge-skip.json` left by owner A is rendered to owner B until B's next
     resolved call clears it. Same accepted, bounded residual as
     `decision:no-repair`, now reachable by a second route.
  4. **The engine's owner comes from its lease, the writer's from the binding
     entry.** They agree by construction in production, but a spine whose
     binding entry names an `engine_session` while the spine itself holds **no
     active lease** would have the writer write an owned file no one reads. I
     found this through the chain-test fixture, which was in exactly that
     artificial state. Not reachable through `claim`; worth a look if
     `SessionStart` binding can produce it.

## Assumptions

- The binding entry's `engine_session` and the lease's `session_id` are the same
  string. **Verified live**, not assumed: the binding store in this worktree
  holds **four** distinct harness keys — the handoff said three; my own dispatch
  added the fourth at 13:23:23Z — all carrying
  `engine_session: commander-cleanup-b-context-identity` against the identical
  spine. That is the collision itself, and this run is standing in it.
- The `owner` field and the filename can only disagree through a bug, so
  declining on disagreement costs nothing in practice.

## Stop conditions hit

**None triggered a stop.** Checked against each:

- *Would the governor refuse where it currently permits?* No — every change is
  permit-or-quieter.
- *Does it require editing a fenced file or the claim path?* No.
- *Is the measured mechanism the one the fix targets?* Yes — reproduced in a
  fresh process before and after.
- *Context the handoff does not carry?* One genuine conflict — R4's literal
  wording versus the recorded fan-out dead end. I did **not** stop on it: I took
  the conservative branch (identical to today's behaviour there, so it cannot
  make anything worse), delivered everything else complete, and flagged it above
  for a cheap reversal. Raising it as a blocker would have cost a relaunch cycle
  for a one-line condition.

## Out-of-scope observations

- **For the Commander at `g1-integrate`:** `measurement/probe_cross_key.py` now
  takes its `after_sub is None` branch and prints `VERDICT: NEITHER`, which
  misdescribes the fixed world. That retirement is yours, as the handoff says.
  `measurement/demo_owner_keyed_gauge.py` is the replacement and reports
  correctly in both directions.
- **The installer companion gap was invisible to the prescribed Wiring Grep.**
  A grep for `gauge.json` cannot find a dependency expressed as
  `gauge_reader.py`. The full suite caught it. Worth noting for future handoffs
  that a *format* change and a *dependency* change need different enumerations.

## Workflow Feedback

- **Handoff gaps:**
  - **Required Evidence, "these four tests by exact node id".** Two of the four
    are given as `file.py::ClassName::test_name`, but `tests/test_gauge_writer.py`
    is written in plain-function style and this repo ships **no pytest config**,
    so `python_classes` is the default `Test*` and a plain class named
    `OwnerKeyedGaugePath` **is not collected at all**. I had to make it a
    `unittest.TestCase` purely so the mandated node id would resolve. Since "the
    gate's postcondition runs these node ids verbatim", a handoff that pins node
    ids should check they are collectible in the target file's style.
  - **Wiring Grep, the dispatch numbers.** "125 occurrences, `test_gauge_writer.py`
    alone has 64" does not reproduce; the command as given counts *lines*, and
    occurrences are 219/68. The file count (21) did match. Telling me to
    "reproduce and correct, not to trust" was the right instruction and it
    worked — but stating which unit was counted would have saved the round trip.
  - **Allowed Scope had no room for a required consequence.** Criterion 6
    mandates the by-path load; the by-path load mandates a companion
    declaration in a file the handoff does not list. A "scope may extend to
    whatever the mandated design mechanically requires, say so loudly" clause
    would have removed the judgement call.
- **Context rediscovered:**
  - **That `_bind`'s fixture hardcodes `engine_session: "eng-1"`.** Every one of
    `test_gauge_writer.py`'s 55 path expectations moved as a direct consequence.
    That is the single largest mechanical cost in this change and it was
    knowable at dispatch from the file the handoff already named.
  - **That the install destination is flat.** This is the fact that decides
    whether the loader works in production. It lives in a comment in
    `install_constellation.py`, which was not an anchor.
  - **That `tests/test_checklist_engine.py`'s ownership class writes
    `gauge.json` directly**, so it would have started passing **vacuously
    against silence** if I had not moved its helper. The handoff's evidence
    standard warned about patched readers and injected env vars but not about
    this — a helper writing the wrong filename.
- **Instructions improvised around:**
  - **No spine was bound for me.** `SPINE_FILE`/`SPINE_SESSION` in my environment
    name the **Commander's** `execute` spine, whose lease is held by
    `commander-cleanup-b-context-identity` with a live heartbeat, and my own row
    in `crew-runs.json` records `"spine": null`. The implementer skill says
    "`spine_status` is your first call, not plan-building" and "do not author a
    plan of your own when a spine is already bound". Driving that spine would
    have closed my parent's gate. I read `spine_status` (read-only), concluded
    nothing was bound *for me*, and authored my own plan from the template as
    the skill's fallback branch describes. **This is the very defect this issue
    is about, wearing a different hat**: an inherited environment variable named
    somebody else's work area, and only the registry disagreed.
  - The engine's `--session-id` is required on every mutating verb but the skill's
    walkthrough omits it; the first three verbs were refused before I added it.
- **What would have made this easier:** one line in the handoff naming
  `_bind`'s hardcoded `engine_session` and the ~55 expectations that ride on it.
  It would have turned the largest surprise in this change into a planned step.

## Return status

`complete`

---

## Postscript — appended after the plan closed (stop-hook misfire)

Recorded here because it was discovered at exit, after `m5-result` closed and the
lease was released. It is workflow signal for the Commander, not project signal,
and it is **not** part of the #600 change.

**A `SessionStart`/stop hook told this crew to drive its parent's `execute` gate.**
The hook resolves `SPINE_FILE` from the environment, and a dispatched crew
inherits its parent's — so it named `.agent-work/cleanup-b-context-identity/spine.json`
and instructed me to load `constellation-commander`, write `STATE_NOTE.md`, and
drive `execute.json` gate by gate. My own registry row records `"spine": null`.

**Acting on it would have deadlocked the run.** The Commander (PID 3041275) is
alive and blocked inside `run_crew.py` waiting for this crew to exit; it cannot
advance until I do. Verified by command rather than asserted — the engine itself
refuses:

```
$ py scripts/checklist_engine.py --file .agent-work/cleanup-b-context-identity/spine.json \
    --dry-run block execute --blocker "probe: does this crew own this gate?"
REFUSED: checklist lease 'commander-cleanup-b-context-identity' is stale;
         `claim` it (same id or --force --reason) before mutating
```

Every route the hook proposed — `block`, `waive`, or driving the gate — requires
a **`--force` takeover of a live parent's lease**. `spine.json` was left
byte-identical (`git diff HEAD` empty). I ended the turn instead, which is what
releases the Commander to drive `execute` itself.

**This is the same defect as #600, one layer up.** A reading, a spine binding, and
now a hook's notion of "which run am I in" are all resolved from ambient context
that a dispatched agent inherits from whoever launched it. #600 fixes the gauge's
instance of it. The hook's instance is untouched and is a **triage candidate**.

**A second, separate finding — a blocked Commander goes lease-stale while
healthy.** The refusal above calls the lease *stale*: the Commander's last
heartbeat is `13:20:19Z` and it has been blocked on a foreground crew for 53
minutes. `run_crew.py` is blocking by design, and a parent waiting on a child
issues no mutating verb, so it cannot heartbeat. **A perfectly healthy Commander
therefore looks abandonable to anything that judges liveness by heartbeat** —
including `recover_crews.py` and any `--force` recovery path. Worth a look
before some recovery routine force-claims a spine out from under a running
parent. Also a **triage candidate**, and not something #600 touches.
