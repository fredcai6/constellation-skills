# Reconciliation result — defect ledger and live issue graph

Analysis only. No GitHub writes were made, no source/test/map/commit changes were
made. Everything below is a recommendation for the human to accept, edit, or
discard. Where a disposition recommends closing or re-scoping, the exact text
is included, unsent.

All commit SHAs are from the **main checkout** (`/home/tommy/projects/constellation-skills`,
current `main` HEAD `24b4665b`) unless marked **[integration-only]**, meaning the
commit exists on `afk/20260820-deficiency-integration` at `efe92791` (mirrored at
the read-only worktree `/tmp/constellation-20260820-integration`) but is **not**
yet an ancestor of `main`. `git merge-base --is-ancestor <sha> HEAD` was run
against every "Fixed" citation below to confirm placement.

---

## Part 1 — `CONSTELLATION_DEFECTS.md`, items 0–4

### Item 0 — same-session relaunch never advances `claimed_at`

**Disposition: FIXED on `main`, doubly.**

- `scripts/checklist_engine.py:1182-1216`, the idempotent-resume branch of
  `claim()`, now restamps `claimed_at = now` on every same-session re-claim, no
  `--force` required. Commit `a69bbac45` (2026-08-16 05:19, `#601`), an ancestor
  of `main` HEAD. The commit's own inline comment quotes this ledger item's exact
  measurement ("leg 2 told '18% (>= hard), stand down' on turn one").
- Reproduced live against current `main`:
  ```
  leg1 claimed_at: 2026-08-21T14:02:52.110436+00:00
  resumed lease leg-session (heartbeat refreshed, claim re-stamped)
  leg2 claimed_at: 2026-08-21T14:02:53.110539+00:00
  advanced: True
  ```
  A same-session `claim` with no `--force` now post-dates the predecessor's
  gauge sample, so `_reading_predates_claim` (#477) correctly disregards it.
  The item's documented `--force --reason` workaround is no longer necessary.
- The `a69bbac45` comment named a residual ("ownership measured in time... the
  real fix is identity, #600"). #600 landed the same day (`16ca93fd`/`3bc87e93`,
  closed 2026-08-16T15:09Z, also an ancestor of `main`): the gauge is now a
  per-owner file (`gauge-<owner>.json`), so a **concurrent** foreign write can
  no longer land in the same file at all — closing the gap #601 could not.
  `scripts/checklist_engine.py:1471-1567` (`_checklist_owner`, `_gauge_path`,
  `_owner_mismatch`) is the mechanism.

**Epic evidence's bearing on standing:** the handoff asks whether the epic's
findings (zero-lease `run_crew` dispatch, 58 stale-but-`active` leases,
`_is_stale` absent from rendering) change item 0's standing. They do not
contradict it — item 0 is specifically about a *foreign gauge reading* being
silently obeyed after a relaunch, which is fixed. The epic's findings are a
**different, still-open** concern: whether a lease *presents truthfully* as
live or dead. That is tracked under #457/#615 (Part 2) and reproduced live
below. Confusing the two would be a mistake; they are adjacent, not the same.

---

### Item 1 — Stop hook resolves the spine from `cwd`, hands the orchestrator a subordinate's gates

**Disposition: FIXED for the mechanism as filed; the issue this item maps to
(#457) stays open for a related, larger defect the epic's own evidence
reconfirms live.**

- The Stop hook (`scripts/hooks/spine_rail.py`, `decide_stop`) no longer
  resolves anything from `cwd`. Discovery is entirely PostToolUse-driven: it
  watches `claim`/`release` (CLI and the MCP door) and maintains a
  session-keyed binding store (`load_binding`), never re-derived from the
  directory the shell happens to sit in. `decide_stop` then compares the
  **acting agent's own binding key** (`binding_key(data)`) against each
  visible mid-flight entry's owner and **withholds the imperative** for any
  entry it does not own, rendering `(withheld: gate belongs to {owner})`
  instead of the foreign gate's actual next step
  (`scripts/hooks/spine_rail.py:1740-1768`).
- This is the composition of two landed fixes: the original parent/subagent
  fix (commit `915daefa`, "`decide_stop` stops rendering a subordinate's next
  imperative into a shared-session Stop-block") and `#609` lane F g3's
  generalization ("ownership is binding-key provenance, never the worktree" —
  `e3e50a69`, `6bba3fd2`, `7d12c29d`, `68d190f7`, `539ff636`, all
  2026-08-16). All are ancestors of `main` HEAD.
- Reproduced live: `tests/test_spine_rail.py::OwnershipIsBindingKeyNotWorktree::test_a_parents_stop_is_answered_with_its_own_gate_not_its_in_tree_crews`
  and `::test_a_crew_that_stops_is_not_handed_its_parents_gate` both **PASS**
  against current `main` (run today). The first test's own docstring names
  this exact failure mode: "the parent's own open gate never rendered at all."

**But the ledger item and issue #457 are not the same defect all the way
down**, and this is the sharpest ledger/code disagreement in this reconciliation:

- Ledger item 1's specific mechanism (cwd resolution → wrong spine → wrong
  imperative rendered) is fixed, as above.
- Issue #457 — which is the tracked issue for this ledger item — was
  **re-scoped by its own author mid-thread**, twice, after measurement. Its
  final framing (comments dated 2026-08-08/09) is not about *generation*
  (ancestor vs. descendant) at all: it is that `engine_session.status` and
  `last_heartbeat`, read from disk, **carry no liveness information in either
  direction** — a committed mid-run snapshot reads identically to a live run,
  and a healthy long-running inner gate reads identically to a dead one.
  165 `active`-status leases were counted in that thread's sample.
- That second half is **not fixed**. `_is_stale` (`scripts/checklist_engine.py:1083`)
  is called only from `claim`-time paths (`require_session`, `claim`'s
  blocking check) — never from `current()`/`render_human()`, never from
  `spine_rail.py`. Reproduced live against current `main`:
  ```
  cl["engine_session"] = {"session_id": "dead-agent", "status": "active",
                           "claimed_at": "2026-08-01T00:00:00+00:00",
                           "last_heartbeat": "2026-08-01T00:05:00+00:00", ...}
  E.current(cl) ->
  LEASE active: dead-agent (by x, heartbeat 2026-08-01T00:05:00+00:00)
  ACTIVE g1 [in-progress] — ...
  next: attest g1 --cond c1 --which postconditions
  ```
  A 20-day-dead lease renders exactly like a live one, with a "next" imperative
  a reader could act on. This is the epic's own **strongest finding**
  (`LIVED-CLUSTER-EVIDENCE.md` E3/Correction 2: "58 plans hold a live `active`
  lease... freely claimable... while presenting to a reader as owned and
  busy") and the human ruling's #1 success criterion ("does the system tell
  the truth?") names it directly.

**Recommendation:** do not close #457. Post a scoping comment (drafted below)
narrowing it to its own final half, since the generational-misattribution half
is done and tested.

> **Draft comment for #457 (not posted):**
> The generational-misattribution half of this issue — the Stop hook handing
> an ancestor's turn a descendant's imperative — is fixed and covered:
> `decide_stop`'s ownership/binding-key check (`#609` lane F g3, commits
> `e3e50a69`..`539ff636`) withholds a foreign entry's imperative unconditionally,
> and `tests/test_spine_rail.py::OwnershipIsBindingKeyNotWorktree` covers both
> directions (parent-sees-crew's-gate and crew-sees-parent's-gate).
>
> The half this issue's own thread reframed to — `engine_session.status` and
> `last_heartbeat` carrying no liveness signal on disk — is still live.
> Reconfirmed today: `_is_stale` is called only from `claim`-time paths
> (`require_session`, `claim`'s own blocking check), never from `current()`'s
> render path or from `spine_rail.py`, so a 20-day-dead lease renders
> identically to a live one with a "next" imperative attached. This is the
> same defect `#615`'s design obligation and this epic's own
> `LIVED-CLUSTER-EVIDENCE.md` (58/58 sampled `active` leases stale) landed on
> independently. Recommend narrowing this issue's title/scope to the
> liveness-presentation question and tracking it alongside `#615`, rather than
> closing it — the attribution half is done, the presentation half is the
> harder and still-open one.

---

### Item 2 — `verify_worktree_isolation.py --here` resolves git from `cwd`

**Disposition: FIXED — but not the way the item's own "Fix direction" proposed,
and that distinction matters.**

- Reproduced live against current `main`:
  ```
  $ cd /home/tommy/projects && python3 .../verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills
  git rev-parse --show-toplevel failed: fatal: not a git repository...
  --here asserts about the directory you are STANDING IN, not about
  /home/tommy/projects/constellation-skills. You are not inside a git
  repository, so there is nothing to compare — `cd .../constellation-skills`
  first, then run this again.
  rc=1
  ```
  The exit code is still 1 (correctly — isolation genuinely cannot be confirmed
  from outside a repo), but the message now says what actually happened
  instead of reading as "you are not isolated," which was this item's whole
  complaint.
- Commit `43c577d4` (2026-08-16, `fix(lane-d)` / `#602`), an ancestor of `main`
  HEAD, landed this the day after the ledger was filed.
- **The ledger's suggested fix direction — run `git rev-parse` with `cwd=<the
  --here path>` (equivalently `git -C <path>`) — was tried before, shipped,
  measured broken, and reverted.** `scripts/verify_worktree_isolation.py:150-158`
  carries the standing warning in the source itself:
  > "Do NOT 'fix' this by running git against EXPECTED... that makes the
  > comparison EXPECTED == EXPECTED, true for any valid worktree, and disarms
  > the gate. Measured in #315 / PR #576 — a naive cwd fix turned a real
  > refusal into a clean advance for a Commander standing in the wrong
  > checkout."
  If a human acted on item 2's literal fix direction today, it would
  reintroduce a previously-shipped-and-reverted regression. The actual fix
  (message clarity, mechanism unchanged) is the correct one and is already in.

**Ledger/code disagreement to flag explicitly:** item 2's diagnosis of the
*symptom* was right (misleading message); its proposed *mechanism fix* was
wrong and has independent falsifying history (#315/PR #576). No action needed
beyond noting this so nobody re-proposes the reverted fix.

---

### Item 3 — refresh-request has no consume path, successor inherits the stop signal

**Disposition: FIXED, but only on the integration branch — NOT yet on `main`.**

This item maps to issue **#500** (open, see Part 2). The fix:

- `scripts/checklist_engine.py`, `attach()` now stamps a `refresh-request`'s
  payload with the active lease's `claimed_at` as `lease_claimed_at` at write
  time; `has_pending_refresh_request()` now additionally requires that stamp
  to still match the *current* active lease's `claimed_at` — so any later
  `claim`, including a same-session relaunch re-claim, consumes the request
  before the successor's first `current`. Commit `4999cf89`
  **[integration-only]**, "fix: consume refresh requests on later claim,"
  2026-08-20.
- `git merge-base --is-ancestor 4999cf89 HEAD` (against `main`) returns
  false — **this fix is not on `main`.** It is only reachable via
  `afk/20260820-deficiency-integration` at `efe92791` / the read-only
  worktree `/tmp/constellation-20260820-integration`.
- The fix satisfies #500's stated acceptance criteria directly: "a
  refresh-request that has been served reports as not-pending, with no reopen
  involved" and "an agent that closes its gate carrying the handoff does not
  have to file a second request." A new test,
  `test_cli_successor_claim_consumes_request_before_first_current`, drives
  this through the actual CLI (`claim` → `attach` → `current` shows
  `REFRESH REQUESTED:` → `claim` again → `current` no longer shows it) and is
  included in the commit.

**Recommendation:** do not close #500 yet — the fix is real but unmerged. Once
`afk/20260820-deficiency-integration` (or its `4999cf89` commit specifically)
lands on `main`, close with:

> **Draft comment for #500 (not posted; hold until `4999cf89` reaches `main`):**
> Fixed by `4999cf89`, "fix: consume refresh requests on later claim."
> `attach()` now stamps a `refresh-request`'s payload with the active lease's
> `claimed_at`; `has_pending_refresh_request()` treats the request as pending
> only while that stamp still matches the active lease, so any later `claim`
> (including a same-session relaunch) consumes it before the successor's first
> `current`. A legacy unstamped request keeps the old gate-scoped behavior for
> back-compat. Verified via
> `test_cli_successor_claim_consumes_request_before_first_current`, which
> drives the exact CLI sequence this issue's acceptance criteria describe.

---

### Item 4 — commander `init` names an MCP door default on machines with no MCP

**Disposition: STALE PREMISE, already retired — and the residual documentation
defect the ledger item itself flagged is now independently FIXED.**

- The ledger entry already carries its own 2026-08-18 correction: the title's
  premise ("no MCP") was false for this machine, and the entry recharacterized
  the real defect as a *documentation* conflation — asserting a property of
  the machine when the governing property is of the *process* (a dispatched
  commander cannot reach a door regardless of what the host has installed).
- That documentation defect is now fixed. `skills/commander/templates/COMMANDER_SPINE.template.json`'s
  `init` imperative currently reads only "call the spine_lease MCP tool with
  action=claim..." — no "by default" framing, no CLI-fallback clause. Commit
  `010dd3087` (2026-08-17, `sweep(567-d1)`), an ancestor of `main` HEAD, is
  why: it removed the CLI-fallback framing everywhere a dispatched agent
  cannot actually reach a CLI second path, across 13 clauses in `skills/`, the
  tracked `.agent-work/templates/` overlay, and inverted the nine
  `test_mcp_adoption.py` assertions that had been *requiring* the old
  (misleading) phrasing — which is why, per that commit's message, the
  clauses had regrown twice before.
- No outstanding action. The ledger item's self-correction was itself
  correct, and the code has since caught up to it.

---

## Part 2 — issues this epic touched

| Issue | State | Disposition | Notes |
|---|---|---|---|
| **#500** | OPEN | Fixed, unmerged | = ledger item 3. See above; draft close text held pending merge to `main`. |
| **#613** | OPEN | Fixed, unmerged | Commit `8137814e` **[integration-only]**, "fix: suppress shared child parent heartbeat." Mechanism matches the issue's own suggested fix exactly: `_parent_lease_heartbeat` now takes `child_env` and skips starting the redundant heartbeat thread when the child inherits the *same* `SPINE_FILE`/`SPINE_SESSION` pair (the only case the issue calls dangerous). Reviewed and approved per the merge commit message. Not an ancestor of `main`. |
| **#636** | OPEN | Fixed, unmerged | Commits `1916ac14` + `123f1674` **[integration-only]**. `run_crew.py`'s crew-registry `save_registry` is now lock-guarded (`fcntl`/`msvcrt`) plus an atomic temp-file-then-rename write, replacing the bare read-modify-write the issue diagnosed ("each of the three processes reads the same prior state and the last write wins"). Not an ancestor of `main`. |
| **#638** | OPEN | Partially addressed, architecture question deliberately unresolved | Commit `d3d0c9ac` **[integration-only]**, "Merge Wave 1 mechanical issue #638," consolidates the archive-close sequence into one `spine_close`/`finish_work` call (`scripts/mcp_spine_server.py`, `scripts/spine_lifecycle.py`). This is a real usability improvement but does **not** resolve either of #638's two named symptoms: the self-waive escalation handshake (child blocks → parent can't act because the checklist is owned by the child's session) and the archive-move deadlock (moving a bound `spine.json` breaks release). Those are exactly the questions the two architecture-candidate design lanes are running on now; per this handoff's hard constraint, no architecture disposition is offered here. Recommend leaving #638 open. |
| **#457** | OPEN | Half fixed, half live | = ledger item 1. See above; draft scoping comment included. |
| **#615** | OPEN | Live, unaddressed | No code found that answers its central question ("should driving a leaseless spine require anything at all?"). Reproduced above (`current()` on a stale-but-`active` lease shows no staleness signal) — same shape, worse: a lease that *looks* active is equally unguarded once its heartbeat ages past `lease_stale_seconds`, per this epic's own Correction 2 (`require_session` refuses only on `_is_stale() == False`; a stale `active` lease is claimable by anyone, from anywhere, with a plain `claim`). |
| **#357** | OPEN | Mostly stale premise, per this epic's own measurement | Filed as "a dead session's lease on a child plan is unreclaimable and unguarded." This epic's `LIVED-CLUSTER-EVIDENCE.md` Correction 2 measured the opposite: a plain `claim` (no `--force`, unrelated session id, `worktree=/anywhere`) took a stranded plan cleanly. **The "unreclaimable" half is false and was the Admiral's own untested claim; the "unguarded" half is true and is now better tracked under #615's framing** (leaseless/stale-lease spines have no guard, full stop — not specifically child plans). Recommend re-scoping or closing #357 in favor of #615, since #357 as filed asks the wrong question ("who may reclaim") rather than the epic-confirmed one ("what should a stale lease present as, and should reclaiming be this cheap"). |
| **#369** | OPEN | Partially addressed | Point 2 (force-claim erases actor attribution) is **already answered on the lease surface**: `claim()`'s force-takeover branch (`scripts/checklist_engine.py:1230-1238`) unconditionally records `previous_session_id` and `takeover_reason`, confirmed in the current source, and `append_journal_entry` stamps every journal line with the acting `session_id` already. But #369's harder case — doctrine's own prescribed *same-session-id relaunch* (the idempotent-resume branch, ledger item 0's territory) — writes **no** attribution anywhere, because it is not a takeover by this code's own definition (`existing.get("session_id") == session_id`). That is the case #369's incident actually describes ("journal seq 44-47 carried commander-304-e298 and none of them were commander-304's"), and it remains completely unaddressed. Point 1 (resume-side "confirm aloneness" precondition) is pure doctrine with zero code enforcement found anywhere; still fully open. |
| **#632** | OPEN | Mis-scoped as filed; one mechanism fixed, the other live | This epic's own `CHANNEL-EXPERIMENT.md` (M1) found #632's stated mechanism — ambient env-var inheritance — is simply wrong for the in-harness Agent-tool dispatch channel, which resolves through a session-keyed binding *file* instead, sharing only the symptom. For the `run_crew --backend cli` subprocess channel #632 does describe correctly, the fix is already in current code and is explicitly self-documented as such: `_crew_door_env` (`scripts/run_crew.py`) **assigns** rather than `setdefault`s the child's `SPINE_FILE`/`SPINE_SESSION`/`SPINE_PARENT` specifically "because a door-bound dispatcher's own... silently win over the value being derived for a child... otherwise the child claimed the DISPATCHER's lease instead of its own" — i.e., #632's env-inheritance hazard on that channel is already closed. What remains fully open and unfixed is the **in-harness** mechanism: an Agent-tool subagent resolves its door binding through `.agent-work/.spine-rail-binding.json`, keyed by the shared harness session id, and nothing strips or scopes that automatically — every one of this epic's own three handoffs had to hand-write "do NOT call any `mcp__spine__*` tool" as prose. Recommend #632 either be split into two issues (one per channel/mechanism) or explicitly re-scoped to the in-harness binding-file case, since the subprocess-channel case it currently reads as describing is done. |
| **#634** | OPEN | No code fix found | Architecture-cluster issue ("plan frozen at bookends, mutable in middle"); one of the two candidate design lanes' subject. No disposition offered per hard constraint. |
| **#609** | CLOSED | Confirmed correctly closed | Landed the binding-key/ownership generalization item 1 depends on; also retired `origin_worktree_refusal`'s stamp-and-compare (surfacing #615 as a side effect, per that issue's own provenance). Consistent with current code. |
| **#600** | CLOSED | Confirmed correctly closed | Per-owner gauge file; verified present in `scripts/checklist_engine.py:1471-1567` and `scripts/gauge_reader.py`. Part of item 0's fix. |
| **#477** | CLOSED | Confirmed correctly closed | `_reading_predates_claim`/`_gauge_path` mechanism verified present and, combined with #600/#601, closes the loop this ledger's item 0 was filed against. |

---

## Part 3 — should become a new issue (not filed)

1. **`require_session`'s refusal text recommends two filed defects as remedies.**
   `scripts/checklist_engine.py:1148-1152`'s refusal for an active lease held
   by a different session says: pass `--session-id <the holder's>` (which is
   the impersonation hazard #632 describes) or `claim --force --reason ...`
   (which is #369's attribution-erasure hazard, confirmed above still live for
   the same-session-relaunch case). Verified live in current source; not
   covered by #615 (which is about the *no-lease* case, not the
   active-foreign-lease case) or by any other open issue found. This is the
   change the epic's own human ruling called "the cheapest high-value fix
   identified anywhere in this epic... a string edit" — worth its own issue so
   it does not get lost inside #615 or #632's larger scope.

2. **`origin.parent` is written by `build_origin` and carried by zero plans,
   on every dispatch channel measured.** Confirmed independently three times
   this epic: Lane B's 40-plan sample, and the `run_crew --backend cli`
   channel experiment (`CHANNEL-EXPERIMENT.md` M2), which measured `"parent":
   null` in the registry and no `parent` key in the child spine's `origin`
   block even for a dispatch where a real parent exists and the channel is
   the one designed to carry it. No open issue found naming this specifically
   (distinct from #632, #457, #615, #369, #634, #357, all of which are about
   authority/liveness, not lineage). Worth filing on its own: it is the one
   finding this epic's own corrections say "persists on both channels" and
   "is not an artifact of tooling choice."

3. **`init_work_area.py --spine` gives a raw `JSONDecodeError` traceback when
   handed a `.spine.toml` spec instead of the compiled JSON.** Found live
   while standing up the channel experiment (`CHANNEL-EXPERIMENT.md` M3):
   handing it `specs/reviewer.spine.toml` — the file that ships in this repo,
   in the obvious place, with "spine" in its name — fails with a stack trace
   instead of "that is the spec; compile it first with `generate_spine.py`."
   No existing issue found for this specific papercut (`init_work_area`
   search on GitHub returns #154 (closed, different symptom) and #609
   (closed, unrelated)). Cheap, concrete repro; good triage-candidate shape.

No other candidates met the bar for a new filing — everything else found
during this reconciliation maps onto an existing issue number (Part 2) or an
existing ledger item (Part 1).

---

## Summary of where the ledger and the live code disagreed

- **Item 2** disagreed with itself, in effect: its diagnosis was right, but
  its proposed fix direction had already been tried and reverted (#315/PR
  #576) for disarming the isolation gate. The shipped fix took the other
  (correct) path — better message, unchanged mechanism.
- **Item 1 / #457** disagreed by scope, not by correctness: the ledger's
  narrow framing (cwd resolution) is fixed; the issue's own later, broader
  reframing (leases carry no liveness signal) is not, and this epic's
  independent measurement (58/58 sampled active leases stale, `_is_stale`
  absent from every render path) landed on exactly the same broader defect
  from a completely different investigation. Two independent measurements
  agreeing is the strongest evidence in this whole reconciliation.
- **#357** disagreed with the epic's own earlier draft of itself: E3 in
  `LIVED-CLUSTER-EVIDENCE.md` claimed reclaim was impossible; Correction 2
  measured a plain `claim` succeeding from an unrelated session, no `--force`,
  from `/anywhere`. The corrected epic evidence and the live code agree with
  each other; #357 as originally filed does not.
- **Items 0, 3, 4** did not disagree with the code — they were confirmed
  fixed (0, 4 on `main`; 3 on the integration branch only) with the mechanism
  named and, for 0 and 2, reproduced live in this session.
