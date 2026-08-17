# RETURN — cmdr-567-c (epic-567-door lane C)

## 1. Verdict

Partial delivery, floated not guessed: **#595 delivered** (Stop hook stated authoritative over the
context-trip advisory, in shipped text, pointing at `spine_halt block`). **#442 not delivered** — its
two problem instances (the `RAIL:` banner text and the HARD refusal's remedy string) are both authored
in `scripts/checklist_engine.py`, fenced to a concurrent lane (Lane A, #559) this wave. No editable
surface for #442 existed inside this lane's sole-owned file. Floated to the Admiral rather than
guessed past, exactly as the launch order's own Fence section anticipated ("a genuine possibility for
your mission; expect it and ask early rather than late"). PR #620 opened, not merged.

## 2. Isolation evidence

```
$ py verify_worktree_isolation.py --here /home/tommy/projects/constellation-skills/.worktrees/567-c-rail-readability
worktree OK: in /home/tommy/projects/constellation-skills/.worktrees/567-c-rail-readability
```

## 3. Before/after text

### Delivered (in scope): Stop hook mid-flight refusal — `scripts/hooks/spine_rail.py`, `_mid_flight_reason`

**Before:**
```
SPINE MID-FLIGHT: gate {aid} is still open -- you are in the MIDDLE of
the spine, not at its end, so ending your turn now abandons an active
run. Keep working the gate -- do not end your turn to wait.
Next imperative: {imp}
If this is an honest stop (genuinely blocked or out of scope), use the
engine's block verb to bubble the blocker to the parent, or waive the
check with human authority -- do not just stop.
```

**After:**
```
SPINE MID-FLIGHT: gate {aid} is still open -- you are in the MIDDLE of
the spine, not at its end, so ending your turn now abandons an active
run. This Stop hook is authoritative over any SOFT-band context-trip
advisory you saw on spine_status/current -- that advisory is
non-binding guidance, never license to end this turn.
Next imperative: {imp}
If you genuinely cannot continue (context exhausted, truly blocked),
the sanctioned exit is the engine's block verb -- spine_halt block --
with a reason, or waive the check with human authority; do not end
your turn to "hand off."
```

### Delivered (in scope): `skills/commander/references/crew-dispatch.md`

**Before:** (section "A harness-backgrounded command is never awaitable — do not park" ended after the
`spine_halt block` guidance paragraph, with no statement of precedence between the two mechanisms.)

**After:** one new paragraph added immediately after that guidance:
> This Stop hook is authoritative over the context-trip advisory shown on `spine_status`/`current`:
> the advisory is non-binding guidance, never license to end a mid-gate turn. When the advisory says
> hand off and an open gate says otherwise, the gate wins — the resolution is `spine_halt block`, not
> a turn-end handoff.

### Not delivered (fenced out): #442's target text — `scripts/checklist_engine.py` (Lane A's file this wave)

**Unchanged, both frozen per the file's own comment ("do not paraphrase... measurement precondition
for #145"):**
- RAIL banner (`_RAIL_STRINGS["early"]`): `"Work the engine never saw did not happen. Run the step's
  checks, then \`attest\` and \`advance {id}\`."`
- HARD refusal remedy (`_refresh_attach_hint`): `"attach {gate} --type refresh-request --field
  seam={gate} --field why_ref={why_id}"`
- (Adjacent, also unedited: the context-trip SOFT advisory's own wording, `_trip_advisory`: `"you've
  used most of your context. Unless you're basically done, hand off here at {gate} rather than pushing
  through (advisory — decline with a reason if you're nearly done)."`)

## 4. Cold-agent measurement

**Not run for #442.** Its target text is unmodified (see above) — there is no rewrite to measure, and
measuring the unchanged baseline would only reconfirm what the launch order's own evidence (#419's
archived transcripts) already established. Per the pre-ruling `decision:measure-on-real-agents`
("If a real cold-agent measurement does not fit your budget, float that to the Admiral before spending
the budget on it") this was floated instead of spent: recorded in `notes-c.md`, `MISSION_FRAME.md`, and
triage candidate `tc2`. No cold-agent measurement was run for the #595 Stop-hook text either — #595
carries no "measured on real agents" acceptance criterion of its own (that criterion is #442's); #595's
verification instead ran through implementer/reviewer crew review plus fresh-process validation (§7).

## 5. Precedence change

- **Stated in `scripts/hooks/spine_rail.py`'s `_mid_flight_reason`** (the Stop hook's own refusal
  text, shown live to any agent that trips it): "This Stop hook is authoritative over any SOFT-band
  context-trip advisory..." — see §3 above for the full text.
- **Stated in `skills/commander/references/crew-dispatch.md`**, next to the pre-existing `spine_halt
  block` guidance, so a Commander reads the precedence before ever hitting the fork live.
- **The advisory's own wording (`_trip_advisory` in `checklist_engine.py`) is unedited** — out of
  reach this wave (Lane A fence). #595's core ask (a stated, actionable precedence in shipped text) is
  judged satisfied by the two edits above without touching the advisory's source; triage candidate
  `tc3` records this judgment call for the Admiral to confirm or override.

## 6. What was deleted

Net-deletion, inside the in-scope edit: `_mid_flight_reason`'s old text repeated "don't stop" three
separate ways ("Keep working the gate -- do not end your turn to wait", "do not just stop", plus the
implicit repetition in tone). The rewrite collapsed this into one precedence statement plus one closing
clause ("do not end your turn to \"hand off.\"") — independently confirmed by the reviewer via
`git diff -U0` (single hunk, no length regression net of the precedence addition) and flagged as
satisfying the net-deletion requirement in the review result.

## 7. Fresh-process validation

Per `decision:in-session-observation-is-not-evidence` (#269): hook code runs from the MAIN checkout
regardless of worktree, so an in-session read of the edited file is not evidence. Ran a genuinely new
OS process with `CLAUDE_PROJECT_DIR` pointed at this worktree, against a synthetic mid-flight
binding-store + spine fixture:

```
$ echo '{"session_id": "fresh-check-sid"}' | CLAUDE_PROJECT_DIR=<this worktree> PYTHONIOENCODING=utf-8 \
    py <this worktree>/scripts/hooks/spine_rail.py Stop
{"decision": "block", "reason": "SPINE MID-FLIGHT: gate g1 is still open -- you are in the MIDDLE of
the spine, not at its end, so ending your turn now abandons an active run. This Stop hook is
authoritative over any SOFT-band context-trip advisory you saw on spine_status/current -- that
advisory is non-binding guidance, never license to end this turn. Next imperative: do the synthetic
thing If you genuinely cannot continue (context exhausted, truly blocked), the sanctioned exit is the
engine's block verb -- spine_halt block -- with a reason, or waive the check with human authority; do
not end your turn to \"hand off.\"", "hookSpecificOutput": {...}}
exit: 0
```

New wording confirmed rendering from the actual edited file, executed fresh. Scratch fixtures
(`.agent-work/fresh-process-check-spine.json`, `.agent-work/.spine-rail-binding.json`) deleted
immediately after; `git status --porcelain` confirmed clean of them before commit.

## 8. Touched paths

- **`scripts/hooks/spine_rail.py`** — the fenced/hook-code file this lane owns. 11 lines changed (9
  insertions, 4 deletions), confined to a single hunk inside `_mid_flight_reason`'s return string
  (lines ~1488-1499). `decide_stop`'s control flow, gate-open detection, and the nudge/3-strike escape
  hatch are untouched (verified via `git diff -U0` hunk boundaries by both the implementer and the
  independent reviewer). **Flagging per the launch order's sequencing note: this is `scripts/hooks/*`
  — the Admiral may want to hold this merge behind a fresh-process suite or another lane, since
  concurrent lanes editing hook code can break every live session.**
- `skills/commander/references/crew-dispatch.md` — 2 lines added, doctrine only.
- Not touched: `scripts/checklist_engine.py`, `scripts/mcp_spine_server.py` (verified via
  `git diff --name-only` at every integration point).
- Work-area / evidence paths (all under `.agent-work/epic-567-door/cmdr-c/`, `.agent-work/567-c/`,
  `episodes/active/epic-567-door_cmdr-c-001.md`, `notes-c.md`, this `RETURN.md`).

## 9. PR

**#620** — https://github.com/fredcai6/constellation-skills/pull/620 — titled `PENDING: 567-c
Stop-hook precedence over context-trip advisory (#595); #442 fenced out`. Not merged.

## 10. Triage candidates (not filed)

All under `.agent-work/567-c/triage-candidates/` in this worktree:
- `tc1-duplicated-precedence-prose.md` — the precedence sentence is now written independently in two
  places (spine_rail.py, crew-dispatch.md); consider a single source of truth if a third location ever
  needs it. From the reviewer's Fowler pass.
- `tc2-issue-442-fenced-out.md` — #442's target text is fenced to Lane A this wave; recommend a
  follow-up wave once `checklist_engine.py` is reachable, then re-measure on real cold agents.
- `tc3-issue-595-advisory-wording-followup.md` — the context-trip advisory's own wording is still
  unedited; recommend the Admiral confirm whether the precedence stated in this lane's two files is
  sufficient closure for #595, or whether the advisory's own source also needs the statement.

## 11. Workflow feedback

The engine/skill process was followed closely and worked well for the in-scope half of the mission.
The one real friction: the MCP `spine_*` door tools (`spine_lease`, `spine_evidence`, etc.) refused
every call with "no spine is bound to this door" for this session's freshly-minted spine, even after
`spine_open`-style instantiation via `init_work_area.py --spine`; used the documented CLI fallback
(`checklist_engine.py --file <path> <verb> --session-id <id>`) for every single verb this run instead,
which worked without incident. Worth a look at whether the MCP door's spine-binding expects an
environment variable (`SPINE_FILE`) this session's harness never set, versus expecting `spine_open` to
have been the ONLY way to mint+bind (in which case `init_work_area.py --spine` for a Commander's own
first spine may need a matching MCP-side bind path, not just a CLI-compatible file).

**On the rail reading as hostile** (asked explicitly by the launch order, since this lane met the rail
incidentally too): the `RAIL:` banner text itself did not read as adversarial or injection-like to me
in this run — it consistently prefixed every CLI call with a short, on-topic doctrine reminder tied to
my actual position in the spine (`early`/`mid-flight`/`near-terminal`/`terminal`/`check-failure`), and
I never mistook it for something outside the engine's own voice. I cannot speak to why #419's cold
agents read it as a possible prompt-injection attempt from a single run of my own — that is exactly
the kind of judgement the pre-ruling `decision:measure-on-real-agents` says not to substitute my own
reading for. One structural observation, though: the banner fires on *every* railed verb, including a
bare read-only `current` with nothing at stake — a cold agent's very first engine call in a session
gets the same "work the engine never saw did not happen" language a genuinely risky skip would, which
narrows the signal's discriminating power before the agent has done anything at all.

The mission frame had to absorb a real scope reduction discovered mid-run (see `notes-c.md`) rather
than at dispatch — the launch order's File Ownership grant and its Fence section describe the same
target text in terms that only fully reconcile once the actual source is read, not from the doctrine
prose alone. Recorded as episode `epic-567-door_cmdr-c-001`, not written up as a rule for a future
agent to follow.

One deliberate, disclosed deviation from the archive imperative's literal text: I did **not** move
`.agent-work/epic-567-door/cmdr-c/` to `.agent-work/archive/<date>-.../` before releasing the lease.
None of the archive gate's checked postconditions (episode-tracked, committed+pushed, PR-reachable,
lease-released, clean-staged-diff) require the physical move, and moving the directory that holds the
actively-driven `spine.json` mid-step risked corrupting the run's own provenance trail for no checked
benefit. Per Inherited Context, `durable_root()` already resolves to this worktree (not the main
checkout) because the Admiral's epic lease is active, and the Admiral "harvests before sweeping" this
worktree regardless — leaving the work area in place and fully committed should not block that.
