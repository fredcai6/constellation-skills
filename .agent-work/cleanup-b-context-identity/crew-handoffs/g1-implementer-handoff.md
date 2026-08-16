# Implementer Handoff — g1: a gauge reading is named for the agent that produced it (#600)

Work id: `cleanup-b-context-identity` · worktree
`/home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity`
· branch `cleanup/b-context-identity` · base `a69bbac4`.

## Gate

`g1-implement` in `.agent-work/cleanup-b-context-identity/execute.json`.

## Task

Make a context reading belong to an **agent** instead of to a **folder**.

Today `.agent-work/<work-id>/gauge.json` is one file per work directory. The
writer resolves it from a binding key; the engine resolves it from the spine's
parent directory. Neither carries any agent identity, so two agents whose spine
files sit in one work directory write to the same file and the last one wins.

**This is measured, not assumed.** `.agent-work/cleanup-b-context-identity/measurement/probe_cross_key.py`
drives the real `handle_post_tool_use` in a fresh process with two distinct
binding keys bound into one work directory. Output
(`measurement/probe_cross_key.out`):

```
after DISPATCHED agent's call : {... "fill_fraction": 0.02 ...}
after ORCHESTRATOR's call     : {... "fill_fraction": 0.9 ...}
gauge-skip.json               : (none)
VERDICT: CANDIDATE 2 CONFIRMED.
```

The orchestrator's 90% overwrote the dispatched agent's 2%, and **nothing
noticed** — no skip sidecar, no guard. `resolve_gauge_path`
(`scripts/hooks/gauge_writer_hook.py:233`) enumerates candidates for **one**
binding key, and the ambiguity guard (`:609`, `len(gauge_paths) > 1`) is
therefore **within-key**. Nothing anywhere compares across keys.

The overwrite is **fresh**, which is why the existing guard cannot help:
`observed_at > claimed_at`, so `_reading_predates_claim`
(`scripts/checklist_engine.py:1444`) returns False. #477/#601's timestamp
comparison can only ever catch a reading *older* than the claim.

## Protected Intent

- The governor must never **refuse** anywhere it currently permits. Every change
  here may only make it quieter, never louder. If your design would add a
  refusal, **stop and say so** — that is outside this lane's latitude and must be
  floated to the Admiral.
- Fail **open** on every uncertainty. No reading is always an acceptable outcome;
  a confidently wrong reading never is.
- Silence must stay **visible**. This subsystem has been burned twice by a quiet
  governor (#252 miscalibration, #271 ambiguous binding). If a reading is
  declined, the agent is told why and what to do.

## Test Mode

Test-led. There is a test surface and it is well developed. Write the failing
test first, watch it fail for the right reason, then fix.

**Evidence standard, inherited from `tests/test_checklist_engine.py::TripGaugeReadingOwnership`
(that class's own bar, and #601's two relaunch tests live there too):** red-before
/ green-after over **behaviour**, driving the **real** reader and a **real** gauge
file on disk. Never a patched `_read_gauge`. Never a fixture that hand-injects
`CLAUDE_PROJECT_DIR` — that variable is what the harness delivers, and a test that
supplies it proves nothing about the harness.

## Amended by `ADMIRAL_RULING-1.md` — read this before the Close Criteria

The float this gate was blocked on has been ruled. **The ruling supersedes the
frozen order and this handoff's original wording wherever they disagree**, and the
Close Criteria below are already rewritten to it. Five things changed:

- **R1 — filename *and* field, and the timestamp guard STAYS.** `decision:identity-not-time`
  is **amended, not satisfied**. Identity handles the **concurrent** case, time the
  **sequential** one. The frozen order's "should end up unnecessary" is
  **withdrawn**: a relaunch reuses its predecessor's lease name *by design*, so no
  identity scheme can see it, and #601's comparison is permanent. This wave fixes
  the concurrent collision and **does not complete** `identity-not-time` — passing
  the *harness* identity into the engine is the only route to that and is out of
  scope. Do not claim otherwise in your result.
- **R2 — normalize an unusable owner, never reject one.** Slug **plus hash**, total
  over every input. **82 of 398** distinct session ids in this checkout fail the
  `[A-Za-z0-9_-]{1,64}` allowlist this handoff originally told you to reuse, because
  slash-bearing lease names are current fleet practice. Rejecting takes the governor
  away from a fifth of the fleet permanently and **invisibly** — losing the governor
  never shows up as a test failure, and this repo has been burned twice by silent
  governors (#252, #271) and once by a wave-long dark one (#488).
- **R3 — a leaseless checklist keeps exactly today's behaviour.** Owner-keying
  applies only where a lease exists.
- **R4 — the ambiguity guard is about attribution, not count.**
- **R5 — `decision:consume-on-lease-change` is settled.** Still not this gate's
  business; #500 is a separate gate.

## Close Criteria

1. **The writer names the record for its owner** — `gauge-<owner>.json` beside the
   spine, where `<owner>` is normalized from the `engine_session` carried by the
   binding entry it already resolved — **and also stamps an `owner` field into the
   record**. The filename *removes* the collision; the field makes a mismatch
   *detectable* if one ever reappears. Both, not either (R1).
2. **The engine resolves the same name from its own active lease `session_id`.**
   Those two strings are the same value by construction: the binding entry's
   `engine_session` is parsed from `claim --session-id X`, and the lease's
   `session_id` is that same `X`. Verified live right now — the binding store holds
   **three** distinct harness keys all carrying
   `engine_session: commander-cleanup-b-context-identity` against the identical
   spine, which is the collision itself, sitting in front of you.
3. **Normalize, never reject (R2).** Every lease session id must yield a usable
   owner key: **slug plus hash**. Cover the slash-bearing ids, the live entries
   carrying `engine_session: null`, and the one carrying the literal `'$SID'`. The
   allowlist idiom this handoff originally pointed you at
   (`spine_rail.is_usable_agent_id`, `scripts/hooks/spine_rail.py:447`ff) is still
   worth **reading** for its character-class reasoning, but **rejection is
   withdrawn** — read it, do not copy its refusal. `spine_rail.py` stays **fenced**
   for edits. **Reserve `skip` and `uncalibrated`** as owner names: both would pass
   any sane allowlist and would collide with `SKIP_FILENAME` /
   `UNCALIBRATED_FILENAME`.
4. **No lease keeps today's behaviour (R3).** With no lease there is no owner, so
   the engine reads the unowned `gauge.json` and trips on it **exactly as today**.
   Where a lease **does** exist and no owner-keyed gauge resolves, return `None` —
   no fallback to the shared file, which would reinstate the folder-owned file this
   issue exists to remove (`decision:unattributable-means-no-reading`). The
   fail-safe is "no *attributable* reading yields `None`"; it must **not** become
   "no lease yields nothing".
5. **The ambiguity guard becomes a question about attribution (R4).** In
   `resolve_gauge_path`, dedupe by resolved **owner-keyed** path, write **every**
   distinct candidate, and fire the `len(...) > 1` skip **only** when a candidate
   cannot be attributed an owner at all. The guard exists because the writer could
   not tell *whose* reading it held; the owner in the filename answers that by
   construction. Two spines in one work directory under the **same** owner still
   collapse to one file — that is **#488's own case** and it must stay working.
6. **One definition of the owner key.** It is computed on both sides of a process
   boundary — the hook from the binding entry, the engine from its own lease — and
   drift between them silently stops every reading resolving. Define it **once** in
   `scripts/gauge_reader.py` and load it in the hook through the by-path loader
   idiom this codebase already uses twice (`gauge_writer_hook._load_spine_rail`,
   `checklist_engine._load_gauge_reader`), keeping the existing fail-safe: a load
   failure yields no owner, which is today's behaviour and not a new refusal. This
   is `decision:one-owner-key-definition`, graded a **guess** — if you depart from
   it, argue the departure in your result.
7. **The sidecars do not follow the gauge name by themselves.** Corrected by the
   cold critic (F4): `SKIP_FILENAME` and `UNCALIBRATED_FILENAME` are **constants**
   on both sides, not `.with_name()` derivations. Decide explicitly whether they go
   per-owner and **state the choice**; do not assume it falls out.
8. **Name what the advisories resolve to.** `_uncalibrated_advisory` and
   `_no_reading_advisory` take `base_dir` only and sit **outside** the trip region
   (F5). Left on the shared path they would report on a file nobody reads. A
   declined or absent reading must still produce a **visible** advisory naming the
   cause and the remedy, in the shape that family already uses.
9. **`#601`'s timestamp comparison stays (R1).** Do not delete or weaken it. It is
   the sequential-relaunch half of the fix, permanently and by design. Confirm in
   your result that it is still present and still fires.

## Allowed Scope

- `scripts/hooks/gauge_writer_hook.py`
- `scripts/gauge_reader.py`
- `scripts/checklist_engine.py` — **gauge, trip and refresh regions only**,
  roughly `_gauge_path` (`:1372`) through `_why_suffix` (`:1308`) and the trip
  block. Note `_gauge_path`'s callers (`_read_gauge`, `_uncalibrated_advisory`,
  `_no_reading_advisory`) will need the checklist threaded through; that is in
  scope and mechanical.
- `tests/test_gauge_writer.py`, `tests/test_gauge_reader.py`,
  `tests/test_checklist_engine.py`, `tests/test_gauge_chain_writer_to_trip.py`
- `docs/GAUGE_WRITER_HOOK.md`, `docs/CHECKLIST_SCHEMA.md` — update the prose you
  invalidate.

## Specific Exclusions

- **Fenced, do not edit:** `scripts/hooks/spine_rail.py`, `scripts/run_crew.py`
  (lane C); `scripts/mcp_spine_server.py`, `.mcp.json` (lane A).
  `spine_rail.py`'s one `gauge.json` mention (`:769`) is a comment about a check
  that keys on `items`, not on the filename, so the design should need no edit
  there. **If you find it does, stop and report** rather than editing.
- **`tests/test_spine_rail.py` is fenced too** (cold critic F11). Its 2 occurrences
  of the literal name belong to a module lane C is editing concurrently. Do not
  touch it; the coupling goes to the Admiral as a cross-lane note.
- **Runtime coupling to lane C, stated rather than implicit:** reading
  `spine_rail.is_usable_agent_id`'s alphabet couples this design to a module lane C
  may change under you. Reading is permitted; note the coupling in your result.
- `checklist_engine.py`'s **claim path** changed on `main` this morning (#601).
  Leave it alone unless your design requires it — and say so if it does.
- `episodes/**` — those are historical records, never edited. Several mention
  `gauge.json`; leave every one of them exactly as it is.
- `#500` (the refresh-request consume path) is **not** in this gate.

## Constraints

- Clear `__pycache__` before **every** measurement. Stale bytecode fabricates
  failures that look like defects (#597) and it cost this epic hours twice.
- Platform Linux, Python 3.12 as `py`. CI is one `windows-latest` job, **red at
  baseline** — local Linux is the only real signal.
- Hook code is **not** fenced by git isolation. `CLAUDE_PROJECT_DIR` is resolved
  once at session launch and inherited unchanged, so you cannot validate a hook
  change from inside the session that contains it. Validate in a **fresh
  process**. (Measured in this run: in this session that variable is *unset*
  entirely, so the hook resolved the project dir from cwd. Do not build a harness
  that quietly depends on that.)

## Map Anchors (inbound)

- **Map entry point:** `map/INDEX.md` names `scripts.gauge_reader`,
  `scripts.hooks.gauge_writer_hook`, `scripts.checklist_engine`. The map is
  **DEGRADED** — `map/ids.jsonl` is empty and every per-module `INDEX.md` target
  is absent — so the real entry point is `docs/GAUGE_WRITER_HOOK.md`, the
  hash-pinned substitute recorded in
  `.agent-work/cleanup-b-context-identity/map-orientation.json`. **Read it before
  changing the writer**; its "Skip-on-uncertainty, enumerated" and "Known limits
  of the binding store itself" sections are the design intent.
- The read side's intent is in `scripts/gauge_reader.py`'s `_PROFILES` note
  (`:76`); the policy side's is the trip block comment from
  `scripts/checklist_engine.py:1328`. **Read both before changing either.**
- Decisions in force, as **amended by the ruling**: `decision:identity-not-time`
  (amended, R1), `decision:owner-in-the-filename` (settled, filename *and* field),
  `decision:normalize-never-reject` (settled, R2),
  `decision:no-lease-keeps-todays-behaviour` (settled, R3 — this **replaces**
  `decision:no-shared-file-fallback`), `decision:ambiguity-guard-is-about-attribution`
  (settled, R4), `decision:unattributable-means-no-reading`,
  `decision:no-new-state-file`, `decision:one-owner-key-definition` (a guess, raised
  this leg). Their wording and grades are in
  `.agent-work/cleanup-b-context-identity/MISSION_FRAME.md`; the rulings themselves
  are in `.agent-work/cleanup-b-context-identity/ADMIRAL_RULING-1.md`.
- **Recorded dead end — do not re-propose it:** writing one reading to *every*
  bound spine ("fan-out") was tried and reverted, because it cross-writes one
  agent's reading into an unrelated agent's work area (#202/#261). A confident
  wrong record is worse than silence.

## Deliverable Path Check

All committed, all verified before dispatch with `git check-ignore <path>`
exiting **1** (not ignored):

`scripts/hooks/gauge_writer_hook.py`, `scripts/gauge_reader.py`,
`scripts/checklist_engine.py`, `tests/test_gauge_writer.py`,
`tests/test_gauge_reader.py`, `tests/test_checklist_engine.py`,
`tests/test_gauge_chain_writer_to_trip.py`, `docs/GAUGE_WRITER_HOOK.md`.

## Wiring Grep — do this FIRST, before any edit

**Enumerate by command, never by memory, every artifact that asserts the literal
name `gauge.json`, and STATE THE COUNT in your result.** You are the author, and
the author is the only one positioned to know the blast radius of a *format*
change — and the one who reliably does not look.

The Commander's own enumeration at dispatch time, for you to reproduce and
**correct**, not to trust:

```
grep -rl "gauge\.json\|gauge-uncalibrated\.json\|gauge-skip\.json" \
  --include='*.py' --include='*.md' --include='*.json' . \
  | grep -v '^\./\.git/' | grep -v '__pycache__' | grep -v '\.agent-work/'
```

→ **21 files**: 5 code (one of them fenced `spine_rail.py`), 5 test (125
occurrences, `test_gauge_writer.py` alone has 64), 2 docs, 7 episodes (leave
alone), 2 notes. Report your own count and reconcile any difference.

**Zero occurrences is the WRONG target.** Under R3 the literal name **survives** on
the leaseless read path. Each occurrence needs an explicit **change/no-change
disposition**, not deletion.

## Required Evidence

- **These four tests, by exact node id** — they are the only checks in this gate's
  plan that can discriminate the fixed world from the broken one, because the four
  existing suites already pass (cold critic F8). Create exactly these names:

  ```
  tests/test_gauge_writer.py::OwnerKeyedGaugePath::test_two_keys_one_work_dir_each_keep_their_own_reading
  tests/test_gauge_writer.py::OwnerKeyedGaugePath::test_two_spines_one_key_one_owner_still_writes
  tests/test_gauge_reader.py::OwnerKeyNormalization::test_every_live_session_id_yields_a_usable_owner
  tests/test_checklist_engine.py::TripGaugeReadingOwnership::test_leaseless_checklist_reads_the_unowned_gauge
  ```

  The **second** is #488's exact shape — an Admiral's `spine.json` and its
  `latitude-interrogation.json` in **one** work directory — and asserts the write
  **happens**. That regression cost an entire wave of dark governor and must not be
  re-armed by a rename (R4). The **third** must feed real session ids **including
  slash-bearing ones** and the live `null` / literal `'$SID'` cases (R2).
  The gate's postcondition runs these node ids verbatim, so a different name fails
  the gate even if the test is good.
- Run all four against the merge base `a69bbac4` and **paste the RED result**, with
  the output showing they fail for the **right reason** — not merely that they fail.
  Then paste them green at your head.
- A fresh-process demonstration that two agents in one work directory now each keep
  their own reading. **Do not edit `measurement/probe_cross_key.py`** — after this
  change it takes its `after_sub is None` branch and prints `VERDICT: NEITHER`,
  which misdescribes the fixed world; keeping it truthful about the *pre-fix* world
  until integration is deliberate, and updating it is the Commander's job at
  `g1-integrate`. Write your demonstration as a new artifact.
- The blast-radius count from the Wiring Grep, reconciled, with a per-occurrence
  disposition.
- Confirmation that #601's timestamp comparison is still present and still fires.
- Pasted output of every verification command below.

## Verification Commands

POSIX form, absolute paths, cache cleared:

```
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity && \
  find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q \
    tests/test_gauge_writer.py tests/test_gauge_reader.py \
    tests/test_checklist_engine.py tests/test_gauge_chain_writer_to_trip.py
```

```
cd /home/tommy/projects/constellation-skills/.worktrees/cleanup-b-context-identity && \
  find . -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q
```

The full suite was **3057 passed / 0 failed** on `main` at `a69bbac4` at dispatch.
Report your own numbers; a difference is the thing that matters, not the absolute.

## Suggested Model Tier

Opus. This is a governor that must become neither bypassable nor trigger-happy,
and the change spans three modules that have to move together.

## Authority

Admiral launch order `LAUNCH_ORDER.md` (frozen) **as amended by
`ADMIRAL_RULING-1.md` R1–R5**, relaunched under `LAUNCH_ORDER-2.md`, via Commander
`commander-cleanup-b-context-identity` (leg 2). No human is reachable. Take a
genuine gap up, do not guess past it. Where the ruling and the frozen order
disagree, the **ruling** wins — R1 and R2 are the human's own rulings.

## Stop Conditions

Stop and return rather than pushing through if: your design would make the
governor refuse where it currently permits; it requires editing a fenced file or
the `claim` path; the measured mechanism turns out not to be what the fix targets;
or you need context this handoff does not carry. **A measured negative is a
complete deliverable** — if the design cannot work, report that with the evidence
and stop. Do not ship a fix aimed at a mechanism you could not reproduce.

## Return Format

Write `IMPLEMENTER_RESULT` to
`.agent-work/cleanup-b-context-identity/crew-handoffs/g1-implementer-result.md`
**before ending your turn** — that write is the delivery.

Include: `Return status` (one of `complete | partial | blocked | out-of-scope |
failed`, **lowercase**), what changed and why, the blast-radius count, the
red-before/green-after evidence, every verification command with its pasted
output, decisions you made and their grades, anything you had to leave undone,
and a `Workflow Feedback` section (what in this handoff or the tooling got in
your way — it is harvested, not ignored).
