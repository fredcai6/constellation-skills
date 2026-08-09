# notes-1 — issue-507-370-413-addressing (crew addressing fix)

## Environment landmine — already fixed in plan.json, but READ THIS
Under the Bash tool, `py` and `python` resolve to **different interpreters**: `py` has no
`pytest` installed (stdlib-only, fine for the engine/verifier scripts), `python` does
(`pytest 9.0.2`). **Always run the test suite with `python -m pytest`, never `py -m
pytest`** — the latter fails with `ModuleNotFoundError` on `pytest` itself, which is easy to
misread as a red suite (it never ran at all). This matters directly for the NOT-OVERRIDABLE
relaunch acceptance test: both the "shown failing on today's code" and "passing on yours"
runs must go through `python -m pytest`, or neither is real evidence.
`m4-acceptance-test`'s `c2` command postcondition in `plan.json` was originally authored
with `py -m pytest ...` (before this was known) and has already been corrected via the
engine's `amend --delta ... retext-check` verb (audited in `plan.json`'s `amendments`) to
`python -m pytest tests/test_crew_delivery_addressing.py -q`. No further action needed there
— just remember it for any ad hoc `pytest` invocation outside the plan too.

## CORRECTION — do not close #413 alongside #507/#370 (working verdict, re-derive before trusting)

team-lead(Admiral) cautioned against inheriting the launch order's "one defect, three
filings" framing uninvestigated — their own #439/#484/#446 collapse call was one-for-two
today (#446 was refuted). Re-reading all three bodies independently in this session (not
from the launch order's summary, not from team-lead's caution — from `gh issue view <n>
--json body` directly):

- **#507 + #370 collapse.** Same failure MODE: an address that was **correct when the
  handoff was written** and **stale by delivery time**, because the dispatching commander
  had moved on in between. #507: the dispatcher tripped/relaunched (`-h` no longer resolves,
  falls back to the retired origin `commander-w4-467`). #370: the dispatcher deliberately
  handed off — and its own body is explicit that the message **reached the exact named
  agent** ("the result survived only because the recipient chose to forward it") — it wasn't
  misrouted, the named recipient simply no longer owned the gate. Same shape: valid-at-write,
  stale-at-read.
- **#413 looks DISTINCT.** Its body: *"The commander was spawned as a subagent and therefore
  never registered under an addressable name [to its own children] ... commander-310 is not
  reachable from this session (only commander-305h, commander-307, commander-308,
  commander-308b exist)."* `commander-310` never had a relaunch/lineage suffix at all —
  no `-a`/`-b` chain for it specifically, and it never shows up as ANY resolvable name in the
  four independent agents' reachable sets. This is **never-valid-from-the-start**
  (a structural non-registration gap: a spawned subagent's own identity isn't addressable to
  its own children), not **valid-then-stale**. Different failure mode from #507/#370, even
  though it presents identically (an Admiral-relay round trip) and the fix below happens to
  relieve its symptom too.

**Working verdict, NOT yet re-confirmed by a fresh read this pass — re-derive, don't just
copy:** #507 + #370 genuinely collapse to this fix's root cause (close both, PR carries
`Closes #507` + `Closes #370`). #413 is a distinct root cause — comment on it explaining the
split, note the fix relieves its practical symptom (delivery no longer depends on a crew
addressing its own dispatcher by name AT ALL, so "never addressable to begin with" stops
mattering in practice) without claiming to have fixed the underlying harness registration
gap, and **leave #413 open** for a human to judge whether the symptom relief is enough.
**`plan.json`'s `m1-confirm-collapse` and `m5-pr-and-issues` gates were rescoped via `amend`
to require this per-pair verification** (not a blanket three-way close) — read their
imperatives fresh rather than assuming this note is still right by the time you act on it.

## Status
Context Governor tripped HARD (fill ~16-19%, hard threshold 0.15 for this gate) before
`m0-context` could even `start` — this fired on the FIRST `current`/`start` call, before any
plan work began, because of the pre-plan research already done in this session. A
`refresh-request` is attached to `m0-context` (evidence `e-m0-context-1`); engine lease
released. **A fresh implementer should claim the lease and `start m0-context` — it should
land with a fresh (low-fill) context budget and proceed normally.**

The plan file `.agent-work/issue-507-370-413-addressing/plan.json` is intact and untouched
past the lease/refresh-request bookkeeping: `m0-context` is still cleanly `pending`, nothing
was started, nothing needs to be undone.

## Research digest — read this before re-doing any exploration

**Root cause (confirmed against all three issue BODIES, not titles):**
#507, #370, #413 are the same defect: a crew handoff/spawn-prompt addresses an **ephemeral
agent instance** (SendMessage to the dispatching Commander's live name) as the delivery
target. This breaks whenever that instance is gone — relaunched/tripped (#507, #370) — or was
never addressable to begin with (#413: a spawned subagent cannot SendMessage its own
dispatching parent, 4/4 dispatches failed).

- **#507** (epic #418 wave 4): three deliveries, three misroutes. `SendMessage` to
  `commander-w4-467-h` (a successor instance) resolves toward the **origin** of the lineage,
  landing on `commander-w4-467` (retired), not the live successor. Bidirectional: the
  misrouted retired instance can't reply either (`general-purpose` is not a reachable name).
- **#370** (epic #298 #304): a reviewer's APPROVE (13 items, 0 blockers, 3 triage) was
  addressed to the commander that dispatched it — which had handed off hours earlier and
  owned nothing. Survived only because the stood-down recipient chose to forward it.
- **#413** (epic #298 #310): 4/4 subagent dispatches could not `SendMessage` their own
  dispatching commander at all (`commander-310` unreachable from the child's own thread) —
  every result had to relay through the Admiral (`main`).

**Key discovery — the fix's real mechanism ALREADY EXISTS in production code:**
`scripts/run_crew.py` already establishes a job/gate-addressed result-artifact contract
(`--result <path>`, freshness-checked against dispatch time) and `scripts/recover_crews.py`
(`classify_entry` / `STATE_COMPLETE`) already discovers a **completed** crew purely from the
durable `.agent-work/<work-id>/crew-runs.json` registry — keyed by `work_id/gate/role`, with
**zero dependency on any agent name**. For the `external` backend (what this harness actually
uses — Agent-tool subagents, no headless CLI), `pid` is always `None`, so a `running` entry
with a fresh result already classifies `STATE_COMPLETE` with no liveness/identity check at
all.

**So the actual bug is narrower than "build a new mechanism" — it's doctrine text
mis-describing which channel is load-bearing:**
`skills/commander/references/commander-core.md` line 147 currently reads: *"Any background
subagent you dispatch ... must be told in its spawn prompt to deliver its result via
`SendMessage` before ending its turn."* This treats the ephemeral-name announcement as the
delivery, when the already-required job-addressed **write** (the handoff's result path) is
what's actually durable across a relaunch.

## Fix plan (all in scope; File Ownership confirmed against LO-w5-c3-addressing.md)

1. **`skills/commander/references/commander-core.md`** (the ~line 147 paragraph) +
   **`skills/commander/references/crew-dispatch.md`**: recast SendMessage as a best-effort,
   non-load-bearing courtesy ping. The WRITE to the job/gate-addressed result path is the
   real delivery. A resumed/relaunched Commander runs `recover_crews.py`/`--verify-result`
   FIRST (cold-start, not just "before a fresh dispatch") to discover an already-completed
   crew before assuming one must be (re)dispatched or waited on. Explicitly note the
   lineage-resolves-to-origin bug (Pre-Ruling 3 in the launch order) as an open, unfixed
   harness-level quirk (outside this repo's control) — note it, don't attempt to fix the
   `SendMessage` resolution behavior itself.

2. **`skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`** +
   **`REVIEWER_HANDOFF.template.md`** — "Return Format" sections: name the path convention
   explicitly — `.agent-work/<work-id>/crew-handoffs/<gate>-<role>-result.md` — as the
   delivery. This convention is **already real**: confirmed both in
   `tests/test_crew_launcher.py`'s `result_rel()` helper (`.agent-work/{work_id}/crew-handoffs/{gate}-{role}-result.md`)
   and in actual prior run artifacts, e.g. `.agent-work/issue-467-trip-semantics/crew-handoffs/`
   (the literal site of the #507 incident) which already holds files named
   `g4-result.md`, `g1-result.md`, etc. So this is documenting an existing convention, not
   inventing a new one — low risk.

3. **NEW `tests/test_crew_delivery_addressing.py`** — the NOT-OVERRIDABLE acceptance test.
   Must exercise a simulated relaunch and prove the **announcement/delivery mechanism**
   itself, not mere file existence (Pre-Ruling 2's named trap: a file-existence-only check
   "always passes" and proves nothing). Design:
   - Test A (characterizes today's bug): model instance-name addressing exactly as
     `commander-core.md` currently instructs it, grounded in #507's literal evidence table —
     a requested name that no longer resolves after a simulated dispatcher-identity change
     (relaunch) lands on the retired **origin** instance, not the live successor. Assert the
     resolved target != the live successor — i.e. it demonstrably misroutes.
   - Test B (proves the fix): using the REAL `run_crew.py`/`recover_crews.py` functions
     (import via the `load_module` pattern already used in `tests/test_crew_launcher.py`,
     not mocks) — dispatch-record + write the result artifact, then simulate the relaunch
     (a fresh "commander" call with **no shared identity** with the original — a different
     session/instance, only the durable registry+result on disk), and show
     `recover_crews.classify_entry` reports `STATE_COMPLETE` regardless of which instance
     name is asking. No agent name appears anywhere in this discovery path.
   - Run `py -m pytest tests/test_crew_delivery_addressing.py -q`, must exit 0 with both
     tests passing (one demonstrating the misroute, one demonstrating the survives-relaunch
     property).

4. **PR + issues**: push `epic-418/w5-crew-addressing`, PR body `Closes #507`, `Closes #370`,
   `Fixes #413`, quoting the collapse argument above (with the exact body quotes already
   captured in this file). Comment the same collapse confirmation on each of the three
   issues. **Do not manually close any issue** — closing rides the PR merge (Mission /
   Pre-Ruling: confirm collapse against bodies before closing, and merge-closes is the
   safest way to honor "before" without racing review).

## Constraints already verified against the launch order
- Excluded files (must not touch): `scripts/checklist_engine.py`,
  `tests/test_checklist_engine.py`, `scripts/verify_iterative_role_artifacts.py`,
  `COMMANDER_SPINE.template.json`, `scripts/install_constellation.py`,
  `docs/CREW_CONTEXT.md`, `docs/TREND_SNAPSHOT.md`. None of the fix files above are on this
  list.
- `commander-core.md` and `crew-dispatch.md` are Commander-specific reference docs, **not**
  `skills/<role>/references/global-*.md` install-time copies — safe to edit directly.
- The two handoff templates are explicitly "crew handoff templates" — mine per File
  Ownership. Adding a new test file is explicitly granted under Inherited Latitude ("add
  tests").

## Plan file state
`.agent-work/issue-507-370-413-addressing/plan.json` — 6 gated items authored:
`m0-context` (pending, untouched) → `m1-confirm-collapse` → `m2-fix-doctrine` →
`m3-fix-templates` → `m4-acceptance-test` → `m5-pr-and-issues`. Each already carries
concrete imperatives/postconditions matching the fix plan above — a fresh agent can
`start m0-context` and proceed straight through without re-planning.

## Already read in full this session (no need to re-fetch)
`skills/commander/references/commander-core.md`, `skills/commander/references/crew-dispatch.md`,
`skills/commander/templates/IMPLEMENTER_HANDOFF.template.md`,
`skills/commander/templates/REVIEWER_HANDOFF.template.md`, `skills/_shared/windows.md`,
`scripts/run_crew.py` (full), `scripts/recover_crews.py` (full),
`tests/test_crew_launcher.py` (helpers: `load_module`, `write_handoff`, `result_rel`,
`fake_launch`), issue bodies for #507/#370/#413 (full, via `gh issue view --json body`).

---

## m1-confirm-collapse — independent re-verification (fresh agent, `impl-w5-addressing-b`)

Re-fetched all three bodies fresh this session (`gh issue view <n> --repo fredcai6/constellation-skills
--json number,title,body,state`, not reused from this file) and re-read them independently, without
copying the working verdict above. My own reasoning lands on the **same split**, confirmed against the
quotes below.

**#507 + #370 collapse — same failure mode: valid when the handoff was written, stale by delivery
time, because the dispatching Commander's identity changed in between.**

- **#507** body: *"`SendMessage` to `commander-w4-467-h` fails with 'No agent named "commander-w4-467-h"
  is reachable... resolves a lineage toward its origin, not its head. A handoff naming `-h` lands on
  `-a`, the retired first instance."* — `-h` was a real, live successor at some point (a crew wrote a
  handoff naming the instance that existed when the handoff was made); by the time delivery happened the
  Commander had relaunched further, and the *resolution* of a no-longer-current lineage member routes to
  the retired origin instead of erroring or reaching the live head. Valid-at-write, stale-at-read, root
  cause = an identity-addressed target rather than a job-addressed one.
- **#370** body: *"It addressed the commander that dispatched it. That commander had handed off hours
  earlier, was stood down, owned nothing... The result survived only because the recipient chose to
  forward it rather than discard it."* — here delivery is NOT misrouted (the named agent is reached
  exactly), but the name was only valid at dispatch time; the dispatcher had since handed off the gate. Same
  shape as #507 (the address is anchored to a moment-in-time identity, not the durable job/gate), different
  proximate trigger (deliberate handoff vs. relaunch) producing the identical practical failure: a
  completed verdict addressed to an agent that no longer owns the work.

**#413 is distinct — never-valid-from-the-start, not staleness.**

- **#413** body: *"Note what the reachable set contains: the other commanders of this epic are all
  addressable, and the dispatching parent is not. The commander was spawned as a subagent and therefore
  never registered under an addressable name, while its own children could see every peer-level agent."*
  and the direction table: *"child → dispatching commander: fails, 4/4"* while every other direction
  tested (Admiral→commander, commander→child, child→Admiral) worked. `commander-310` carries no
  lineage suffix at all in this incident — there is no relaunch, no handoff, no window during which the
  address was good and then went stale. The child→dispatching-parent direction simply does not resolve,
  structurally, regardless of timing. This is a harness reachability gap (a spawned subagent is not
  addressable to its own children), not the address-staleness defect #507/#370 share.

**Verdict (independently confirmed, not copied): #507 + #370 collapse to this fix's root cause — close
both. #413 is a distinct root cause — comment explaining the split, note the fix relieves its practical
symptom (delivery no longer depends on a crew addressing its dispatcher by name at all, so a
never-addressable-parent stops mattering in practice) without claiming to fix the underlying harness
registration gap, and leave #413 open.** This matches Admiral's ruling relayed in the dispatch message;
recorded here as an independent re-derivation per the gate's own constraint ("never close on a title
match; body evidence only").
