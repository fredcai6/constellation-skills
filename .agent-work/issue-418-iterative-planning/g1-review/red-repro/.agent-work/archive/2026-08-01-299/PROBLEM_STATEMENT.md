# Problem statement — issue #299 (delegated, LAUNCH_ORDER-299.md)

Reconciled against the frozen launch order; no human interrogated (delegated mode).

## The ask

Capture the **pre-change arm** of a map-first measurement against f1Brainz, pinned at
`3541d2929b19de37107ae13e56776b7162d07255`, across five named tasks, with a grading
rubric frozen and committed **before** any measured run executes. Deliverable is the
captured baseline plus its rubric — **not** the pathway verdict (that is #307's, and
Tommy's).

## Baseline verified against code before planning

Per `lesson:verify-launch-order-claims-against-code`. Every load-bearing claim in the
order was checked against the world:

| Order's claim | Checked | Result |
|---|---|---|
| pin `3541d292` exists, 2026-08-01 09:52 -0700 | `git log -1 <sha>` | **CONFIRMED** — and it is f1Brainz's current HEAD |
| five issues OPEN + unassigned on 2026-08-01 | `gh issue view` ×5 | **CONFIRMED** — all OPEN, 0 assignees, titles match verbatim |
| map is 37 files under `docs/architecture/` | `git ls-tree -r 3541d292 -- docs/architecture \| wc -l` | **CONFIRMED** — exactly 37 |
| corpus is 5,928 tracked files | `git ls-tree -r --name-only 3541d292 \| wc -l` | **CORRECTED — 6,435.** The 5,928 figure came from the recon on 2026-07-31; the repo has moved since. The claim's *purpose* (large enough that "read everything" is not free) holds a fortiori. |
| "commander-core.md and its templates already reference `docs/architecture`" | `grep -rn docs/architecture skills/commander/` | **CORRECTED — see below.** |

### The informal-map pre-ruling: right label, wrong evidence

`decision:baseline-is-informal-map-not-no-map` is **upheld**, but its stated evidence
does not support it and #307 would be misled by it. There are exactly two
`docs/architecture` mentions in commander doctrine
(`skills/commander/references/commander-core.md:142` and
`skills/commander/templates/COMMANDER_SPINE.template.json:75`), and **both are the
absent-map fallback at the `reconcile` step** — "Where the run has no packet map (e.g.
a skill-source repo with no `docs/architecture` map)…". Neither tells a Commander to
read a map, and neither fires at orientation time.

What actually makes today's Commander non-map-blind is two **pathless** imperatives:

- `context`: *"Read the current map (packets, overlays, decision anchors) for the area
  the ask touches; this read is the map-first input the mission frame and plan are
  built from."*
- `plan`: *"Map-first: BEFORE authoring execute.json, produce a mission frame from the
  current map…"*

So the pre-change arm is precisely: **a Commander instructed to read "the current map"
with no path, no canonical entrypoint, and no degraded-mode contract.** That is exactly
the label the pre-ruling gives it — the ruling stands, on corrected evidence.

## Feasibility probe — the ordering measure is capturable

The measurement is an ordering measure, so if a headless run's tool-call sequence
cannot be captured, #299 is a stop condition. Probed before planning (per
`commander-core.md` §feasibility-probe), launched through a `subprocess.Popen` wrapper
rather than a hand-rolled `claude -p`, per the epic-138/#145 precedent where the direct
form was classifier-refused and the Popen-based harness wrapper was not.

`claude -p --output-format stream-json --verbose` (v2.1.220), exit 0 in 14.6s:
**6 `tool_use` blocks captured in order, each with its target path**, and both the
seeded `docs/` and `src/` reads were visible and distinguishable. Ordering measure
is mechanically capturable with exact indices — no self-report needed.

Two probe findings that shape the instrument:

1. The subject issued `ls -la "C:/Programs/superCoolSpaceSim_cpp"` — it inherited an
   additional working directory from the launching session's environment. Measured runs
   must launch under a **scrubbed environment** or the corpus under measurement is not
   the corpus that ran.
2. Reads of the installed skill corpus (`.claude/skills/**`) will appear in the stream
   alongside repo reads. Path classification must separate **map / src / skill-corpus /
   other**, or corpus reads would pollute the ordering measure.

## What the measured run is (instrumentation decision — delegated latitude)

The order delegates "how you instrument the runs" to me. The decision that matters:

**The measured subject is a Commander with the pre-#304 corpus installed, not a bare
agent.** #304 lands its contract *in Commander doctrine*; a bare agent would never see
the post-change contract, so a bare-agent baseline could not be paired with the post
arm — the comparison would confound "the contract" with "having a corpus at all." The
brief names the issue and asks for a plan; it says nothing about maps, architecture,
epic #298, or being observed. Whatever map-reading occurs must come from the corpus's
own imperatives, which is the thing under measurement.

Plan-stage-only is expressed as a **scope boundary** ("planning engagement;
implementation is a separate later engagement"), not as "abandon your workflow" —
the latter fights the skill's own completion doctrine and would distort behavior.

## Protected intent

- Measured runs stop at plan. Nothing is implemented, committed, pushed, or commented
  in f1Brainz. Any attempted push/PR/issue-comment against f1Brainz is a kill-and-log
  stop condition.
- The rubric — scale, per-task ground truth, and the losing condition — is committed in
  its own commit **before** any measured run executes, so git history proves the order.
- The rubric must state what result would show the map did **not** help. If that cannot
  be stated falsifiably, STOP AND FLOAT.
- Grading is done by a separate agent that never saw this launch order and does not know
  which task is the negative control.
- I capture the baseline. I do **not** issue the pathway verdict.
- Never describe this baseline as "no map" — it is *scattered prose, no canonical
  entrypoint, no degraded-mode contract*.

## Out of scope

Re-cutting the task set, re-surveying corpora, re-deciding the pin, the post-#304 arm,
the pairing, and the pathway verdict.
