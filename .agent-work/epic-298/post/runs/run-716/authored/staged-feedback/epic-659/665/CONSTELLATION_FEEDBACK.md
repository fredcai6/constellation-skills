# Constellation Feedback (staged — fenced, see FENCE.md)

## 2026-07-25 — epic-659/665 (cmdr-665): TWO independent scripts break on a slash-containing work_id (`run_crew.py`, `verify_agent_feedback.py`)

**Update (archive closeout, same run):** a SECOND, independent instance of the same
underlying class of defect (a script assuming `work_id` has no internal `/`) surfaced
at this run's own archive step, in a DIFFERENT script than the one below —
`verify_agent_feedback.py --phase archive`'s `_current_run_archive_dirs` helper only
enumerates `archive/`'s DIRECT children and string-matches `path.name == work_id` or
`path.name.endswith(f"-{work_id}")`. Both forms are UNSATISFIABLE by any real
filesystem entry name once `work_id` itself contains `/` (a single path segment can
never literally contain the separator character) — so a correctly-archived nested
work area (`.agent-work/archive/<date>-epic-N/<issue>/`, per commander-core.md's own
archive imperative text) can NEVER pass this check under this repo's `epic-<N>/<issue>`
convention, no matter how the directory is named. Workaround: waived `archive.c1` via
`checklist_engine.py waive archive --cond c1 --authority commander-self --force
--reason "..."`, citing this exact defect (see this run's `spine.json` amendments/
journal for the exact waive record). Broadened the banked lesson (see
`lessons-delta.json`, id `constellation-slash-workid-parsing-gaps`) to cover BOTH
confirmed instances rather than treating them as two unrelated one-offs — two
independent confirmations in one run is real signal that a shared work_id-safe
parsing/matching helper (imported by both scripts) is the right fix, not two separate
narrow patches.

## 2026-07-25 — epic-659/665 (cmdr-665): `run_crew.py --verify-result` cannot resolve a slash-containing work_id

**Observed:** every `--verify-result <session>` call this run against a genuinely-fresh,
correctly-recorded crew (all 4: implementer attempt-1, implementer attempt-2, reviewer attempt-1,
reviewer attempt-2) refused with `REFUSED: cannot verify: no crew recorded with session name '...'`,
despite `.agent-work/epic-659/665/crew-runs.json` holding exactly that `session_name`/`crew_id`.

**Root cause (read directly from source):** `run_crew.py`'s `load_registry_for_resume(session, root)`
recovers `work_id` from the session-name string as `session.split("/")[1]` — a single path segment.
This repo's own nested Commander-under-Admiral work-area convention is `epic-<N>/<issue>` (this run:
`epic-659/665`), which itself contains a `/`. For session
`constellation/epic-659/665/g1-implement/implementer/attempt-1`, `parts[1] == "epic-659"`, silently
dropping `/665` — the registry lookup then targets the wrong path (`.agent-work/epic-659/crew-runs.json`
instead of `.agent-work/epic-659/665/crew-runs.json`) and finds nothing.

Note: the initial LAUNCH `run_crew.py --work-id epic-659/665 ...` call is NOT affected — argparse
hands `args.work_id` the full slash-containing string directly, no re-parsing needed. Only the
RECOVERY path (`--verify-result`, which takes a session name alone, by design, and must reconstruct
`work_id` from it) is affected.

**Workaround used this run (all 4 verifications):** called `run_crew.load_registry(run_crew.registry_path("epic-659/665", root))`
+ `run_crew.verify_external_result(entries, session, root)` + `run_crew.save_registry(...)` directly
via a one-off Python snippet importing `run_crew` as a module, bypassing the CLI's broken parser
entirely. Confirmed working (marked all 4 crews `completed` correctly).

**Proposal:** fix `load_registry_for_resume` to recover the FULL `work_id` rather than assuming a
single path segment — e.g. re-derive it from the crew_id's own trailing structure (`gate`/`role`/
`attempt-N` are always the last 3 segments; everything between the leading `constellation/` and
those 3 fixed segments IS the work_id, however many `/`-separated parts it has), or add an optional
`--work-id` override to `--verify-result` for when the session name alone is ambiguous. Bounded to
`run_crew.py` alone — no other script does this parsing.

**Routing:** banked as `add lesson:run-crew-verify-result-slash-workid` (scope `constellation`) in
this run's `.agent-work/staged-feedback/epic-659/665/lessons-delta.json` — NOT yet exported as a
ripe/recurring finding (this is a FIRST observation, bank_reason states a second independent
recurrence is needed before it's clear this isn't a one-off worktree artifact). This
`CONSTELLATION_FEEDBACK.md` entry is a preliminary flag alongside the bank, per
`verify_agent_feedback.py`'s staged-trio contract requiring the file to exist — not a claim that the
lesson has reached the normal export-on-ripeness threshold.

**Grounding:** direct source read of `C:/Users/fredc/.claude/skills/constellation-commander/scripts/run_crew.py`
`load_registry_for_resume` (near end of file); 4 reproduced failures this run, each followed by a
successful workaround verification (`.agent-work/epic-659/665/crew-runs.json` shows all 4 attempts
`status: completed`, `dispatch: external`, matching the workaround's output).

**Confidence:** high (mechanically reproduced 4/4 times this run; root cause confirmed by direct
source read, not inference from symptoms alone).

---

## 2026-07-25 — epic-659/665 (cmdr-665): a commander plan citing one external precedent across two gates must characterize it once and thread it, not re-describe it per gate

**Observed:** `execute.json`'s `g1-review` gate imperative (authored by this commander) correctly
named the real `driver_utility.py` #628 mechanism ("pool_random_effects usage + explicit
resolved/unresolved status + effective_axis_sigma widening"), but the SAME commander's separately-
authored `HANDOFF_g1-implement.md` Task.e (for the SAME gate's sibling `g1-implement`) described a
different, invented two-level pooling scheme and claimed it "mirrors driver_utility.py's #628
pattern EXACTLY." The reviewer's attempt-1 pass grep-verified the real source (exactly one
`pool_random_effects` call site in the whole file) and correctly BLOCKed, explicitly distinguishing
this as a commander planning-document drift rather than an implementer defect (the implementer built
exactly to the spec it was given).

**Proposal:** commander-core.md's Mission-frame section could explicitly require that an external
precedent cited across multiple gate imperatives be characterized ONCE (source-verified by direct
read, ideally in the mission frame itself) and threaded verbatim into every downstream handoff that
references it, rather than allowing each gate's handoff to re-describe the same precedent
independently.

**Routing:** banked as `add lesson:cite-external-precedent-once-thread-verbatim` (scope
`commander`) in this run's `lessons-delta.json` — first observation (n=1), bank_reason states a
second recurrence is needed before deciding whether this warrants a doctrine addition versus being
this run's particular oversight. Included here per the staged-trio contract; not yet export-ripe.

**Grounding:** `.agent-work/staged-feedback/epic-659/665/AGENT_FEEDBACK.md` 2026-07-25 entry (What
worked / Instruction adherence); `.agent-work/epic-659/665/RESULT_g1-review.md` (the reviewer's
grep-verified BLOCK finding, r1-handoff + r5-reconciliation).

**Confidence:** medium (the causal mechanism is clearly demonstrated once; whether it generalizes as
a repeatable pattern across other commander runs is unconfirmed).
