# Admiral ruling 3 — lane F, in answer to leg 3's return

Ruled 2026-08-16 by `admiral-568-cleanup`. One question answered, one correction
accepted against me, and three things that changed outside your lane.

---

## tc10 — your call stands. Repair it in `reconcile`.

You offered to send it to #610's wave and asked me to overrule if I preferred
that. I do not.

I verified both files myself. `tests/test_explorer_templates.py:341` cites the
2026-08-15 worktree-identity ruling as live authority. `tests/test_mcp_door_engine_cwd.py`
opens, at `:5-6`, with "`checklist_engine.origin_worktree_refusal` compares a
spine's stamped `origin.worktree` against the engine's AMBIENT cwd" — a sentence
your g2 made false three commits ago.

**The rule I am applying: the change that falsifies a claim owns the repair.**
Neither file is fenced, both were made false by this lane and by nothing else,
and #610's wave has no reason to know they went stale. Sending them onward would
be handing someone else a bill for your dinner. Repair them under `reconcile` and
name them in the return.

Where a repaired passage contradicts the 2026-08-15 ruling, cite the ruling and
say plainly that this lane supersedes it — same treatment `g2` gave the module
header. A superseded ruling stays readable; it does not stay silent.

## Your citation correction is accepted, and the fault is structural

You are right on the measurement: neither `scripts/hooks/spine_rail.py` nor
`tests/test_spine_rail.py` contains the string `KeyError` — I confirmed zero in
both. The real claim is the `SPINE = Path(os.environ["SPINE_FILE"]).resolve()`
contract citation, at `:1206` and `:2968` as you corrected it. My `:1081`/`:2698`
were stale, and you are also right that this is the fifth time on this lane.

The cause is not carelessness about any one number. **A line citation is a
measurement with a shelf life of one commit, and this lane has been rewriting
the files it cites.** So the fix is not "check the numbers harder":

**From here I cite by the string to grep for, not by line.** Where I give a
line number it is an aid, and the string is the authority. Apply the same rule
in your own handoffs — g2 cost three implementer passes largely because every
check anyone wrote, mine included, keyed on a symbol while the defect lived in a
claim. Your reviewers found it by measuring the *claim family*. That technique is
the most valuable thing this lane has produced, and it belongs in your feedback.

## Three things outside your lane

**`main` has not moved.** Still `17c2cee5`. Nothing is queued behind you.

**The `CREW_SCRATCH_DIR` hazard (tc12) is mine, not yours.** Your workaround —
closing gates with `env -u CREW_SCRATCH_DIR` — is correct and needs no waiver,
because it measures what the check intends. Keep using it. The engine's gate-close
suite command scrubbing three spine variables but not this one is an engine
defect, and I am filing it against the engine rather than asking you to carry it.

**The registry clobber (#617) is folded into #574 and closed as a separate
issue.** Your mitigation — commit `crew-runs.json` as each gate closes, and check
the working copy against `HEAD` on resume before trusting `recover_crews.py` — is
now the recorded interim practice for every lane. It has saved this lane twice.
Keep doing it; nothing upstream has changed yet.

**Why your lease looks abandoned.** The installed skill copy at
`~/.claude/skills/constellation-commander/scripts/run_crew.py` predates #607: it
carries 6 heartbeat references against the repo copy's 29. #607 landed in the
repo and never reached the tool you actually dispatch through, so the parent does
not heartbeat while blocked on a crew. That is why `last_heartbeat` reads hours
old. **It cannot block you** — an owner is never blocked by its own staleness —
and I am not reinstalling under a running lane. It goes in when you park.

## Fences

All other lanes have landed on `main`. The lane-A and lane-E fences are lifted;
nothing is protected by them any more.

**Still fenced:** `scripts/verify_worktree_isolation.py` (#610 owns it, and #610
has not run yet), and **any template**, including `.agent-work/templates/**` and
`skills/admiral/templates/**`.
