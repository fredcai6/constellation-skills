# Cold plan critic result

## Verdict

PROCEED-WITH-CHANGES — the direction is defensible, but three of candidate B's
stated costs are understated in ways I could measure, and the gate that carries
all the substance has one postcondition that only records the implementer's own
verdict.

## Findings

### F1 — the filename names a LEASE, not an agent  [lens: intent-fit] [severity: high]

claim: The stated point is "a context reading belongs to an agent, not a folder."
Candidate B keys the file on `engine_session` / the lease `session_id`, which is
an agent-CHOSEN string passed to `claim --session-id`, not an agent identity. Two
different agents that use the same lease id are indistinguishable under B, and
that is not a hypothetical case — it is the case the repo shipped a fix for this
morning. `checklist_engine.py:1086` and `:1117` are the same-id resume path
("resumed lease ... claim re-stamped"), and commit a69bbac4 exists precisely so
the relaunch guard fires there. On that path the successor opens
`gauge-<same-id>.json` — its predecessor's file — which is the #477 shape the
whole issue exists to remove.

Two consequences the plan states the other way round:

1. `PLAN_ALTERNATIVES.md:92` — "B is also the only one of the two that lets
   #601's timestamp comparison actually become unnecessary." On the same-id
   relaunch path B does not make it unnecessary; #601's comparison is the only
   thing that catches that case. B and #601 are complementary, not
   successor-and-bridge.
2. The writer's own acting identity is the binding KEY, `session_id#agent_id`
   (`gauge_writer_hook.py:233` docstring, #419), which is a different identity
   space from the `engine_session` value it would interpolate into the filename.
   The plan never says these are different things, and the difference is exactly
   where the residual risk lives.

evidence: `scripts/checklist_engine.py:1086,1117`; `scripts/hooks/gauge_writer_hook.py:233`;
`PLAN_ALTERNATIVES.md:92-95`; `MISSION_FRAME.md:80-82` (`decision:identity-not-time`).

suggested change: Drop the "retires the timestamp comparison" claim from the
frame and from `PLAN_ALTERNATIVES.md`'s Convergence section; state instead that
#601 stays load-bearing for the same-id relaunch, and add that case as a named
g1 acceptance test (same lease id, two successive agents, one work dir). If the
plan wants ownership by agent rather than by lease name, say so and carry the
binding key, not `engine_session`.

### F2 — B goes dark for the same crews it accuses A of abandoning, and I measured how often  [lens: intent-fit] [severity: high]

claim: A is rejected because "the governor goes **dark for exactly the crews it
exists to govern**" (`PLAN_ALTERNATIVES.md:41-44`). B has the same failure on
three paths, and "an unusable owner writes nothing" (cost 1) plus
"no fallback" (cost 2) are what produce it. It is not a one-tool-call window;
for these runs there is no later call that fixes it.

Measured in this checkout:

- **Owner names that the proposed allowlist rejects.** `spine_rail.is_usable_agent_id`
  is `\A[A-Za-z0-9_-]{1,64}\Z` (`spine_rail.py:453-457`). Of 395 distinct
  `engine_session.session_id` values found in `.agent-work/**/*.json`, **82 fail
  it** — every slash-bearing name. This is current practice, not legacy: the most
  recently modified ones are dated today, and they are crew sessions —
  `constellation/tc1-worktree-identity/g1-implement/implementer/attempt-1`,
  `.../g1-review/reviewer/attempt-1`, `implementer/tc3-worktree-root-owner/attempt-1`.
- **Owners that are absent.** The live binding store has 38 entries; **2 carry
  `engine_session: null`**. The rail stores whatever it got without validating it
  — `os.environ.get("SPINE_SESSION")` (`spine_rail.py:1115`) and
  `_extract_opt(tokens, "--session-id")` (`:1220`) are both written straight into
  the entry. Another live value is the literal string `'$SID'` — an unexpanded
  shell variable, also not filename-safe.
- **No lease at all.** `_active_lease` returns None for a checklist with no
  `engine_session` (legacy checklists and templates, per `checklist_engine.py:1028`).
  Today such a checklist still gets a reading and still trips on HARD, because
  `_reading_predates_claim` fails open to "use the reading". Under B it has no
  owner, so it gets no path, so it can never trip again.

evidence: `scripts/hooks/spine_rail.py:453-457,1115,1220`;
`scripts/checklist_engine.py:1002-1010,1028`; counts computed over
`.agent-work/**/*.json` and `.agent-work/.spine-rail-binding.json` in this
worktree; `PLAN_ALTERNATIVES.md:41-44,70-76`.

suggested change: Normalize the owner instead of rejecting it. Derive a
filename-safe token deterministically from the owner string on BOTH sides — e.g.
`sha256(owner).hexdigest()[:16]`, or a slug plus a hash suffix — so 82/395 of the
fleet's real session ids keep a governor instead of losing one. Reusing
`is_usable_agent_id` is the right instinct for a value that is interpolated into
a path, but here it is being used as an admission test for a value this repo can
compute a safe form of. Separately, decide out loud what a leaseless checklist
gets, and put the measured before/after in the plan so the human is choosing with
the numbers in front of them.

### F3 — the rename re-arms the ambiguity guard that #488 disarmed  [lens: testability] [severity: high]

claim: `resolve_gauge_path` returns one candidate per DISTINCT gauge path and
dedupes by that path. Two spine files in one work directory (`spine.json` plus a
`latitude-interrogation.json` survey) currently collapse to one `gauge.json`, so
the caller's `len(gauge_paths) > 1` ambiguity skip does not fire. That dedup IS
#488, and its docstring records what the undeduped version cost: "left an
Admiral's own governor dark for an entire wave."

If the candidate path becomes `parent / f"gauge-{entry['engine_session']}.json"`,
two entries under one binding key whose `engine_session` values differ no longer
dedupe. Two candidates, `len(gauge_paths) > 1` fires, `_write_skip_flag(...,
"ambiguous-binding")` runs for each, and the write is skipped — the exact #488
regression, reintroduced by a rename. Nothing in `execute.json`'s g1 imperative,
constraints, or g1-review criteria (a)-(e) mentions the dedup or the guard.

evidence: `scripts/hooks/gauge_writer_hook.py:233-282` (dedup and its #488
rationale) and `:604-621` (the `len(gauge_paths) > 1` skip); `execute.json` g1
imperative and g1-review criteria contain no mention of either.

suggested change: Make the dedup key an explicit decision in the plan (dedupe by
directory, or by resolved path after owner interpolation) and require a
red-before test with two spines and one binding key in one work directory. Add it
to g1-review's enumerated checks.

### F4 — "the sidecars follow the gauge name for free" is false  [lens: testability] [severity: medium]

claim: `PLAN_ALTERNATIVES.md:64-66` says the two sidecars follow the new name
"for free, since both are derived with `.with_name()` off the gauge path."
`.with_name()` there is called with a CONSTANT: `gauge_path.with_name(SKIP_FILENAME)`
where `SKIP_FILENAME = "gauge-skip.json"`, and the same for
`UNCALIBRATED_FILENAME`. The reader uses the identical constants. So the sidecars
do not follow the gauge name — they stay folder-owned, which means the collision
this issue exists to remove survives on the sidecar family, and a reader asking
"why is there no reading for me" can be handed a skip flag another agent's writer
raised. The claim is load-bearing: it is the locality argument that makes B look
cheap.

There is also a namespace collision the allowlist does not exclude: under
`gauge-<owner>.json`, an owner literally named `skip` or `uncalibrated` produces
the sidecar's own filename. Both pass `[A-Za-z0-9_-]`.

evidence: `scripts/hooks/gauge_writer_hook.py:435-439,478-482`;
`scripts/gauge_reader.py:448,455,473,507`; `PLAN_ALTERNATIVES.md:64-66`.

suggested change: Correct the claim, and decide explicitly whether the sidecars
become per-owner too. Whichever way, it is a named cost, not free. Reserve the
`skip`/`uncalibrated` names or prefix owner files distinctly.

### F5 — g1's scope ("`_gauge_path` and the trip region only") does not cover the callers  [lens: simplicity] [severity: medium]

claim: `_gauge_path` has four call sites. Two of them are outside the trip
region and do not receive the checklist dict, so they cannot resolve an owner
without a signature change: `_uncalibrated_advisory(base_dir)` at `:1533` and
`_no_reading_advisory(base_dir)` at `:1684`, which then hands the path to
`_skip_reason_advisory` and `_stale_record_advisory`. Either they keep resolving
the old shared path — in which case the "why is there no reading" advisories
report on a file nobody writes or reads any more, which is worse than silence —
or the change is wider than the plan says.

evidence: `scripts/checklist_engine.py:1372-1380,1391,1533,1684`; `execute.json`
g1 imperative ("`_gauge_path` and the trip region only").

suggested change: Name the advisory family in the g1 imperative and say what it
resolves to, or state that it deliberately stays on the shared path and why.

### F6 — the gate carrying all the substance has one postcondition, and it is self-report  [lens: testability] [severity: medium]

claim: `g1-implement`'s only postcondition is `c1`: an `implementer-result`
artifact with `status: complete`. Every real close criterion — no fallback to a
shared `gauge.json`, the blast-radius count stated, no fenced file edited, the
red-before/green-after standard — lives in the imperative's prose and in
g1-review's prose. At least two of those are mechanically checkable and are not
checked.

evidence: `execute.json` g1-implement postconditions (one entry, artifact kind);
compare g0-measure, which carries two command checks.

suggested change: Add command postconditions to g1-implement: (i) the four fenced
paths are unmodified — `git diff --name-only <base> -- scripts/hooks/spine_rail.py
scripts/run_crew.py scripts/mcp_spine_server.py .mcp.json` produces no output;
(ii) no read or write path resolves the literal `gauge.json` any more — a grep
over the changed regions with a stated expected count.

### F7 — g1-integrate c3 states a comparison and checks one side of it  [lens: testability] [severity: medium]

claim: c3's statement is "the full suite is green ... **and its failure set is
compared against a main baseline re-measured at gate time**". The check is
`pytest -q` on this worktree only. The baseline half is never measured, so the
condition can be satisfied while the comparison it names has not happened. This
is the shape the handoff asked me to look for: only one side of a comparison is
enumerated.

evidence: `execute.json` g1-integrate c3 statement vs its `check.command`.

suggested change: Either make the command measure both (run the suite at the
merge base, diff the failure sets) or cut the second clause from the statement
and record the baseline as a separate attested condition.

### F8 — g1-integrate c1 and g1-review c1 give the same answer in the healthy and the broken world  [lens: testability] [severity: medium]

claim: c1 runs four existing suites. Those suites pass on the current tree, so
the check cannot distinguish "the change landed correctly" from "nothing
changed." It only becomes discriminating if a new failing-first test exists —
and no postcondition anywhere requires one; the red-before/green-after standard
is prose only. Separately, g1-review's c1 is satisfied by a `review-result`
artifact of any verdict, including BLOCK; the verdict is only enforced by
g1-integrate c2. That is survivable, but c1 alone is not a review gate.

evidence: `execute.json` g1-integrate c1, g1-review c1; g1-implement's evidence
anchors name test files but no condition requires a new case in them.

suggested change: Require, as a postcondition, a named new test that fails on the
pre-change tree — cite it by node id in the condition statement so the reviewer
can run it against the merge base.

### F9 — g0-measure c2 passes on two empty files  [lens: testability] [severity: low]

claim: c2 is `test -f gauge-at-T0.json && test -f worktree-binding-at-T0.json`.
Existence only. `touch` on both satisfies it. It asserts nothing about content,
size, or that the artifacts came from the probe run at all — and the whole point
of the T0 capture is that its CONTENT is the evidence. Note the same plan uses
`test -s` in g2 c1, so the weaker form here is inconsistent rather than
deliberate.

evidence: `execute.json` g0-measure c2; compare g2-design-500 c1 (`test -s`).

suggested change: `test -s` on both, plus a grep for a field only a live capture
carries (e.g. `path_source` in the binding capture, `observed_at` in the gauge).

### F10 — g2-design-500 c1 greps for a string the gate's own imperative supplies  [lens: testability] [severity: low]

claim: c1 requires `DESIGN_500.md` to be non-empty and to contain
`consume-on-lease-change`. A one-line file naming the decision and answering
nothing passes. The condition's statement says the file "answers the settle
condition explicitly"; the check cannot see whether anything was answered.

evidence: `execute.json` g2-design-500 c1.

suggested change: Grep for a required verdict heading the design must contain
(e.g. `## Is re-stamped claimed_at sufficient?` plus a `SUFFICIENT` /
`NOT SUFFICIENT` token), or demote it to an attested null check and stop implying
a machine verified the content.

### F11 — the blast radius is enumerated but never disposed of  [lens: simplicity] [severity: low]

claim: g1's first task is to enumerate every artifact asserting the literal name
`gauge.json` and state the count. Nothing in the plan says who then UPDATES them,
and the launch order's file ownership is `gauge_reader.py`,
`gauge_writer_hook.py`, `checklist_engine.py` "plus their tests". My own sweep of
tracked code, tests, docs, skills and templates found 164 occurrences across 12
files, including `docs/GAUGE_WRITER_HOOK.md` (13), `docs/CHECKLIST_SCHEMA.md` (1),
`skills/commander/templates/COMMANDER_SPINE.template.json` (1) and
`tests/test_spine_rail.py` (2) — the last being the test of a module lane C is
editing right now. Test volume alone is 64 in `test_gauge_writer.py` and 27 in
`test_gauge_chain_writer_to_trip.py`, which is a real argument that g1 is a large
gate whatever the no-red-window reasoning says.

evidence: `grep -c 'gauge\.json'` per file over `scripts/ tests/ docs/ skills/
templates/`; `execute.json` g1 imperative; `LAUNCH_ORDER.md:72,74`.

suggested change: Add a disposition step to g1 (or a g1b) that says which of the
enumerated artifacts change and which stay, and rule explicitly on
`tests/test_spine_rail.py`, whose module is fenced.

## Checks that cannot fail

I enumerated all **11** postconditions in `execute.json` (e0-context 1,
g0-measure 3, g1-implement 1, g1-review 1, g1-integrate 3, g2-design-500 2).

Vacuous or near-vacuous:

1. **g0-measure c2** — `test -f` on two paths. Two empty files pass. See F9.
2. **g2-design-500 c1** — greps for a token the imperative itself supplies. A
   stub passes. See F10.
3. **g1-integrate c1** — the four suites pass on the unchanged tree, so the check
   returns the same answer in the healthy and the broken world unless a new
   failing-first test is added, which nothing requires. See F8.
4. **g1-integrate c3** — the statement names a comparison against a re-measured
   main baseline; the command measures only this branch. One side of a
   comparison. See F7.
5. **g1-implement c1** — not vacuous mechanically (a missing or non-complete
   artifact fails it), but it verifies only that the crew declared itself done.
   Nothing about the change is checked. See F6.
6. **g1-review c1** — satisfied by a `review-result` of any verdict, BLOCK
   included. The verdict is only enforced downstream at g1-integrate c2.

Attestations with `check: null` (e0-context c1, g0-measure c3, g2-design-500 c2):
these are the normal attest idiom, not defects, but note that g0-measure c3 and
g2-design-500 c2 both have obvious command forms available (grep `notes-b.md`;
`git diff --stat` over the consume path) and were left qualitative.

**g0-measure c1 can fail** — I checked the probe. `probe_cross_key.py` always
exits 0 and prints exactly one verdict line, and the check pipes it to `grep -q`,
so a probe that crashed, was deleted, or printed a different verdict yields no
match and the condition fails. Two caveats worth recording rather than raising as
findings: the check verifies the probe's self-report, not the world — the verdict
branch is `if orch_fill != sub_fill` (`probe_cross_key.py:157`), which infers the
overwrite rather than asserting the two writes targeted one path; and after the
g1 change the probe will find no `gauge.json`, take the `after_sub is None`
branch, and print "VERDICT: NEITHER — the dispatched agent's write was skipped",
which is a false description of the fixed world for anyone who re-runs the
archived artifact. The stored `satisfied` flag is never re-checked
(`checklist_engine.py:2053-2057`), so this does not turn the closed gate red; it
just leaves a misleading artifact. Worth one line in the probe.

## Answers to the five questions asked

- **`decision:no-shared-file-fallback` — does it silence a governor that works
  today, and is "one tool call" true?** Yes, and no. Three measured paths lose
  the governor permanently, not for one call: an owner the allowlist rejects
  (82 of 395 real session ids, current), an owner that is null in the binding
  store (2 of 38 live entries, plus the literal `'$SID'`), and a checklist with
  no active lease (which trips today, because `_reading_predates_claim` fails
  open to using the reading). The one-tool-call window is real, but only for the
  case where both sides resolve the SAME owner and the file simply does not exist
  yet. See F2.
- **"Can only permit, never refuse" — true on every path?** I looked and found no
  counterexample. Both refusal paths require a real reading in the hard band:
  `_trip_hard_gate` returns early on `reading is None`
  (`checklist_engine.py:1962-1964`), and it is fed by `_trip_hard_band_reading`,
  which returns None for surveys, a None reading, or a reading that predates the
  claim (`:1804-1836`). `advance`'s `require_why` is driven by the same function,
  so it inherits the same fail-open. The SOFT advisory is text. So the claim holds
  on the trip paths. It holds in the direction that matters for latitude — and it
  is also exactly why F2's cost is invisible to every check in this plan: losing
  the governor never shows up as a failure.
- **g0-measure c1 — can it fail?** Yes. See the section above for how, and for
  the two caveats.
- **Is one combined g1 right?** The no-red-window argument is sound as far as it
  goes — writer, reader and engine do have to move together. But the gate as
  written also absorbs the blast-radius enumeration (164 occurrences, 12 files),
  the identity-normalization decision (F2), the dedup decision (F3), the sidecar
  decision (F4) and the advisory-family decision (F5), and it is reviewed against
  a single postcondition that reads the implementer's own status field (F6). The
  size is defensible; the review surface is not. Fix F6 before deciding whether
  to split.
- **Does anything touch a fenced file?** No edits. Two adjacencies worth a
  ruling: `tests/test_spine_rail.py` asserts the literal `gauge.json` twice and
  is in the blast radius while lane C edits its module (F11); and the plan takes
  a runtime dependency on `spine_rail.is_usable_agent_id`, so if lane C changes
  that predicate the gauge filename alphabet changes under this lane. Reading it
  is permitted, but the coupling should be stated.

## Simplicity / YAGNI

B is bigger than the measured problem, though not obviously wrong. The measured
defect is one cross-key overwrite inside one work directory; the response is a
rename that touches 12 files and 164 literal references and opens four fresh
decisions (owner normalization, dedup key, sidecar naming, advisory scope). I am
not recommending A — F1 shows A and B are less far apart than the write-up says,
since B does not deliver the timestamp-comparison retirement it claims, and F2
shows B inherits the dark-governor cost A was rejected for.

One road neither candidate takes, offered as the cheap graft rather than a third
design: name the file for the owner **and** stamp `owner` into the record. That
is A folded into B for the price of one field, and it buys the one thing a
filename alone cannot give — a reader that can tell "this file is named for me
but was written by something else", which is precisely the gap between the two
identity spaces in F1. Under `no-new-state-file` it adds no store.

## What I did NOT check

- `.agent-work/cleanup-b-context-identity/LAUNCH_ORDER.md` beyond the lines I
  grepped for fences, ownership and the `gauge.json` references — I was told to
  read four documents and did not read the launch order whole.
- `map-orientation.json`, the hash-pinned substitutes, and whether the frame's
  anchors verify against them. Not my lens.
- `gauge_reader.py`'s parsing, staleness and threshold logic beyond the sidecar
  filename constants.
- Windows behaviour of any proposed filename, and CI. Local Linux only.
- `install_constellation.py`'s hook wiring, which references the writer script
  but not the gauge filename in the hits I sampled.
- Lane A and lane C code (`mcp_spine_server.py`, `.mcp.json`, `run_crew.py`), and
  whether the MCP door always sets `SPINE_SESSION` — which decides how common the
  null-owner case in F2 is going forward.
- Whether `DESIGN_500.md`'s subject matter is right; I only attacked its gate's
  check.
- I did not run the probe. I read it and reasoned about its exits.

## Workflow Feedback

- The handoff's "read exactly these four" and the permission to read source to
  check a specific claim are the right pairing. Every finding above except F1's
  first half came from source, and the four documents alone would have produced a
  much weaker critique. Worth keeping in this handoff shape.
- Two of the questions I was asked to attack ("is the one tool call window true",
  "can it only permit") were answerable only by counting things in the live
  `.agent-work` tree, which is neither a listed document nor a source file. I
  read it anyway. If that was out of bounds, say so next time; if it was in
  bounds, name it, because it is where the strongest evidence was.
- `PLAN_ALTERNATIVES.md` states its costs plainly and that made the critique
  faster — F2 and F4 are both attacks on costs the author had already written
  down. That is the document working as intended, not a complaint.
- **A live specimen of the defect under review, worth capturing as evidence.**
  On finishing this handoff I was served a Stop-hook message reading "SPINE
  MID-FLIGHT: gate plan is still open", instructing me to author `execute.json`
  and take the plan to approval. That is the Commander's spine and the
  Commander's imperative. I am the plan critic; the lease on
  `.agent-work/cleanup-b-context-identity/spine.json` reads
  `commander-cleanup-b-context-identity`, and my session is
  `constellation/cleanup-b-context-identity/plan/critic/attempt-1`. The hook
  found state by WORK DIRECTORY and addressed it to whichever agent was standing
  in that directory — the same shape as the gauge defect this plan exists to fix,
  on a different mechanism. I did not act on it; a crew agent driving its
  parent's spine is worse than a missed nudge. Note that neither candidate A nor
  candidate B would help here, because this instruction is not a gauge reading —
  which is itself the useful part: it suggests the class is broader than #600,
  and lane C's #549 is the neighbour the frame already flagged
  (`MISSION_FRAME.md:129-133`). Worth a triage candidate rather than scope creep
  in this wave.
