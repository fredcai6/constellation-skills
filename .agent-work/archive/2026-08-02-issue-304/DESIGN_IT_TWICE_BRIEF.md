# Design-it-twice Brief: `map-input contract — delivery surface and shape`

## The one thing being designed twice

**Where the map-input contract lives and what shape it takes, such that map orientation is PRIMARY
(before source exploration) rather than merely AVAILABLE.**

One load-bearing decision. Not "how do we resolve a path" — resolution already exists and is measured
insufficient. The decision is the **delivery surface + enforcement shape** of the primacy contract.

## Count and panel — a surfaced choice

**N = 3 (panel).** Rationale: this is a load-bearing interface that touches corpus architecture, it
crosses a repo-ownership boundary in at least one candidate, and the Admiral explicitly declined to
pre-rule it. Global doctrine: "a load-bearing interface or architecture-touching plan runs a panel.
When in doubt, panel." Surfaced for the Admiral to overturn.

## Held fixed for all candidates

- The deficiency is **primacy and contract, not path** (ratified, not re-openable).
- Wiring point is **context** and **plan**, not reconcile (`decision:contract-at-context-and-plan`).
- Degraded mode must be **REPORTED**, never a silent fallback to code crawling, and is the **common
  case** (`decision:degraded-mode-is-the-common-case`) — this repo itself has no `docs/architecture/`.
- Two-bin rule holds: **no third bin** (`#302` ruling). Machinize the mechanizable; the rest stays prose
  and does not earn a bin.
- The check must be provably falsifiable **by mutation** (#300 finding).

## Measured facts every candidate must design against

- **Finding 2 (#299):** ZERO `Skill` invocations across five runs, with the tool present and all 19
  skills enumerated in every `system/init`. Four of five never read a corpus file at all. The corpus was
  **offered and declined**.
- **Finding 1 (#299):** all five runs read source before the map; every run *did* eventually read the
  map. Failure is **ordering**, not availability.
- The only surface reliably delivered in every measured run is the target repo's auto-loaded `CLAUDE.md`.

## The constraints (one per agent, each distinct and named)

- **Candidate A — `concern-owned-corpus-only`.** The contract lives entirely in Constellation-owned
  surfaces. No file the target repo owns is ever written or generated into. Clean ownership boundary.
- **Candidate B — `delivered-surface-first`.** Optimize for the instruction actually reaching the agent
  whether or not any role is invoked. May project a thin generated stanza into the consuming repo's
  always-loaded bootstrap, and must fully price that boundary cost and maintenance surface.
- **Candidate C — `two-bin-maximal`.** Put as much as possible in the **machine** bin — engine-enforced,
  not prose-requested — and minimize prose to what genuinely cannot be mechanized. Directly applies
  Tommy's ruling: "machinize the mechanizable. we don't need stochastic reasoning for predictable logic."

## Compared on

- **Depth** — does it hide resolution/degradation behind the seam, or leak it into every caller's prose?
- **Locality** — contained, or fanned out across 11 templates and N repos?
- **Seam placement** — is the boundary where the *caller* (a Commander at context/plan) and the *tests*
  want it?
- **Testability** — can primacy and degraded-report each be exercised and **falsified** on their own?
- **Delivery** (added axis, forced by Finding 2) — does the instruction reach an agent that did not
  invoke a role?

## Framing block — presented to the Admiral WHILE the agents run

- **Constraints in play:** the three above, chosen to span the ownership boundary (A never crosses it,
  B crosses it deliberately, C tries to make the question moot by moving enforcement into the engine).
- **Dependencies:** all three must touch `COMMANDER_SPINE.template.json` (context + plan) and inherit
  the #317 fold-in. B additionally depends on a generation/refresh mechanism and a target-repo write
  path. C depends on the engine's command-postcondition machinery and on `#315` cwd behavior.
- **Illustrative sketch — NOT A PROPOSAL, zero weight at convergence:** a `resolve_map_entrypoint.py`
  wired as a command postcondition at context, printing `RESOLVED <path>` or `DEGRADED <reason>`.
  Offered only to prime parallel reasoning; it must not anchor the outcome.

## Output — a recommendation, never a menu

**Convergence is human-only per the latitude contract. What follows is a defended recommendation the
Admiral/Tommy decides on — this Commander did not decide it.**

### Two engine facts, verified in code, that reshape the comparison

Candidate C asserted these; I checked both in `scripts/checklist_engine.py` and both hold:

1. **stdout from a `command` postcondition is captured and discarded.** `_run_check_command` (~line 701)
   runs `subprocess.run([shell,"-c",command], capture_output=True)`, and `_check_condition` records
   evidence as `{"cmd","exit","shell"}` only. **The exit code is the only machine-readable signal that
   reaches the spine.** The brief's own illustrative sketch — a script "printing `RESOLVED <path>`" as a
   command postcondition — would print into a void. The sketch was wrong; it was marked not-a-proposal,
   and it is now retired on evidence.
2. **#315 is worse than "relative paths resolve oddly."** `_run_check_command` takes only `command` and
   passes **no `cwd`** to `subprocess.run`. `_check_condition` threads `base_dir` into the
   `git-change-policy` branch but *not* into the `command` branch. There is no cwd control at all.

Consequence, binding on any winner: the report must be an **exit-code vocabulary**, and the root must be
**absolute, baked at spine-materialization time** (a `<repo-root>` placeholder in `init_work_area.py`,
which does not exist today — verified).

### Unanimous across all three candidates (not actually in dispute)

Independent agreement under three different constraints is the strongest signal the panel produced:

1. An ordered candidate list for the entrypoint, where **RESOLVED requires citable content, not mere file
   existence** — a scaffolded-but-empty `index.md` must read DEGRADED, because a false RESOLVED is
   strictly worse than an honest one.
2. A **receipt** recording verdict + substitutes + the stated gap.
3. Degraded **completeness** machine-checked and gate-blocking at `context`.
4. A **mission-frame anchor check** at `plan`: anchors must be drawn from the map (or from declared
   substitutes). Anchor ids exist *only* in the map, so citing them is a set-membership proof the map was
   read. This is the best seam in the panel — it turns "did the map inform the plan" into a question a
   machine can answer with zero stochastic judgement.
5. Delete the same dead-path prose (2 files, **172 words / 86 per template** - see the correction
   below) and retarget the pathless imperatives.
6. **Keep** the bare `config_ref` line in all 11 templates. The line works (`load_config` degrades
   correctly); only the prose about it is false.
7. **The #317 contradiction resolves by subtraction.** Delete Commander's 172 words and Charter is left
   as the single remaining statement about that path. No Charter edit, no new arbitration prose, nothing
   added to hold the line. All three reached this independently.
8. **Preventive enforcement of tool-call order is impossible for anything the corpus owns.** It needs a
   `PreToolUse` hook, which needs `settings.json`, which #180 established is a human-owned surface.

### The finding that matters most — a partial, scoped null against the issue's own framing

All three candidates, under three different constraints, independently concluded: **primacy-as-tool-call-
ordering cannot be preventively mechanized by the corpus.** What *can* be mechanized is:

- **necessity** — the map was read, and its content is load-bearing in the plan; and
- **reported degradation** — degrading is fine, degrading *silently* is refused.

That is a genuine scoped null and it is surfaced, not buried. It does not say "map-first cannot be
mechanized" — it says *this* property splits into an enforceable half and a prose half, and the panel
found the seam between them in three independent passes.

### Recommendation — a named hybrid

**Candidate C's core, with A's anchor-vocabulary framing, the ordering audit built but REPORT-ONLY, and
B's bootstrap stanza held as a separate human decision.**

Axis by axis:

- **Depth** — C wins. It is the only candidate designed against the *real* engine (exit-code vocabulary,
  no-cwd). A and B both lean on printed output that the engine discards.
- **Locality** — A and C tie; both are contained in Commander templates plus two scripts. B fans out
  permanently into every consuming repo.
- **Seam placement** — A articulates it best (anchor ids exist only in the map), C mechanizes it best
  (`verify-frame`). Take A's framing, C's implementation.
- **Testability** — C wins decisively. Promoting the five captured baseline transcripts into the
  regression suite makes *the measurement that found the defect* the suite that pins the fix; four of the
  five must be refused by the check, and 716 (`NO-SRC-READ`) must pass. A fixture nobody can quietly
  relax to match a belief.
- **Delivery** — B is the only candidate that scores above zero, and it says so honestly. A scores zero
  and admits it. C scores zero and admits it.

**Why the ordering audit is built but NOT gated.** It is the only instrument that measures the actual
property, so it must exist. But C names its own fatal risk correctly: it is coupled to an undocumented
transcript schema, it cannot see subagent reads, and an upstream change would convert the gate into a
silent fleet-wide no-op that *reports honestly and continuously that it is not measuring* — exactly the
signal a busy fleet learns to scroll past. A gate that can silently stop gating is worse than a
measurement that reports. Report-only keeps the instrument and refuses the false assurance.

**Why B is separated rather than rejected.** B is the only answer to Finding 2, and its own weakness
statement is the most honest thing in the panel: its load-bearing bet is *the same class of thing the
null already tested* — f1Brainz's bootstrap already names an exact path and lost 5/5. B's differentiator
is a shape claim (an agent executes a named command more reliably than it honours an ordering adjective)
with zero measurement behind it. That is a real bet worth taking cheaply, as an **opt-in
`--wire-bootstrap` that is never a default** — but it crosses a repo-ownership boundary, so it is
Tommy's call, not mine.

## FINAL CONVERGENCE — revised on new evidence + Tommy's Q1 ruling

Two inputs landed after the panel: commander-299's discriminated analysis, and Tommy's Q1 ruling. Both
change the answer. Recorded as a revision rather than quietly folded in.

### Correction carried forward: the deletion target is 172 words, not 112

Both figures were mine and both were wrong before this one. The cold critic re-measured the full
deletable block: **86 words per template, 172 total.** My earlier extraction counted only sentences
literally containing `engine-config` and dropped each block's trailing sentence. The **substance** —
2 templates, not 11 — is unaffected and is the load-bearing part.

### Q1 RULED: candidate B is OUT

Tommy: *"the map is orchestrator content, not implementer content."* The principle is sharper than the
ruling — **placing content at a broader tier than its audience is a defect, not a delivery win.** Three
tiers: auto-loaded `CLAUDE.md` (every agent), `ORCHESTRATOR_CONTEXT.md` / `CREW_CONTEXT.md`
(orchestrators / crew), a role's own skill (that role). B reached for the universal tier and would have
pushed orchestrator content at every implementer in every consuming repo, forever — inverting a split
f1Brainz already practises.

**B's motivating premise also collapsed.** Zero-invocation was read as "a Commander-doctrine contract
reaches nobody." It is not: in production, a Commander run *does* invoke the Commander. The baseline
measured generic agents **because the rig launched generic agents** — a defect in the measurement rig,
not a delivery defect in the product. **Candidate A's reach weakness therefore largely evaporates**: it
was scored against a population the product never claimed to serve.

### The discriminated baseline — the deficiency is narrower than the panel assumed

| measure | result |
|---|---|
| **Orientation** (map before source) | **0 of 5** |
| **Use** (returned to the map) | **4 of 4**, 3-5 separate calls each |
| **Citation** (map artifacts named in the plan) | **4 of 5**; two proposed *editing* packets |

The map was **genuinely used - as verification and justification after the seam was found, never as the
thing that found it.** Not apathy (they used it well). Not ritual (a ritual read is one bootstrap touch
and never again). **A sequencing failure, precisely and only.**

Consequence: any candidate whose value is making the map *more available* or *more prominent* solves a
problem the data says is already solved. **The variable is order.**

### The hard finding: the necessity gate does not catch the measured defect

**Citation was 4 of 5. Those four runs would PASS an anchor-citation necessity gate - and they are the
runs that exhibited the defect.**

Sharpest form: **against the measured five, the necessity gate has zero discriminating power, and its
only firing would have been wrong.**

- 4 runs - defect present, gate **passes** -> false negatives.
- 1 run (#716, no citation) - gate **fires**, but #716's correct answer was *"this work is not in this
  repo."* Non-engagement was right there -> false positive.

It catches map-**ignoring**. The measured failure is map-**lateness**. Different populations.

### The steelman, and why it fails

Steelman: the anchor requirement sits on the mission frame, authored *before* `execute.json`, so it
enforces ordering at **gate granularity** - map-before-plan rather than map-before-first-grep. A real,
weaker primacy, and arguably the more useful one.

**Name it as the gate's known bypass, and the steelman fails - not on theory, on the data.** The bypass
is not a loophole someone *might* find; it is **the measured behavior**. All four citing runs found the
seam by crawling, then cited map artifacts in their plans. Required to author a frame with anchor ids,
they would have produced a correct one from the map they had already read for confirmation. Gate
satisfied, behavior unchanged.

Map-before-plan is satisfied by map-before-plan-*document*, and the plan document is written last. The
ordering that matters is map-before-**hypothesis**, and the hypothesis forms during exploration, long
before any artifact exists.

Nor is it rescued by requiring pre-crawl *expectations*: nothing the corpus owns can distinguish an
expectation written before the crawl from one written after. **The only ordering evidence is the
transcript**, which cannot be preventively gated.

### What the contract actually delivers - revised and honest

1. **Reported degraded mode - genuinely new, and the real value.** The 4/5 citation happened in a repo
   that *has* a map. In a repo without one - the common case, and this repo - there is currently **no
   contract at all**: silent fallback to crawling, no record. That half is unsolved, and this fixes it.
2. **Necessity gate - ships as a floor, not as the fix.** It mechanizes a behavior already occurring at
   4/5. Worth having as a regression guard so map-ignoring cannot silently return; **not** to be
   described as the answer to what was measured.
3. **Ordering - not mechanizable by the corpus.** With B out it needs a `PreToolUse` hook -> settings.json
   -> Tommy's per #180. Measured only.

### The REPORT-ONLY audit's consumer - named

- **During this epic: commander-299's measurement rig** - the audit feeds the POST arm's comparison
  against the frozen PRE arm. Real, named, currently live.
- **After this epic: nobody yet.** Stated, not hidden. If no consumer emerges at epic close, the audit
  should be **retired** rather than left running as decoration.

Gate-vs-report stays **reversible by a flag**, so a later ruling for gating is a flip, not a rebuild.

### Final recommendation

**Candidate C's core + A's anchor-vocabulary framing, ordering audit REPORT-ONLY behind a flag, B
removed by ruling.** Shipped and *described* as a reported-degraded-mode contract with a necessity
floor - explicitly **not** as the fix for the measured sequencing defect, which the corpus cannot reach.

## Untaken-road record — as-run addendum

The brief's illustrative sketch (stdout-printing command postcondition) is **retired on evidence**, not
merely untaken: verified impossible as an engine-visible report. Recorded because a sketch that turns out
to be unbuildable is a finding, not a footnote.

## Untaken-road record

- **`minimal-diff` / prose-only edit of the two existing pathless imperatives.** Not generated as a full
  candidate: it is the null hypothesis the #299 baseline already tested in effect — f1Brainz's bootstrap
  is prose naming an exact path, and it did not produce map-first ordering. Named here as a loud skip; it
  survives as the honest-null comparison point rather than as a design candidate.
- **Hook/harness-level enforcement** (a `PreToolUse` hook refusing source reads before a map read). Not
  generated: it requires settings.json wiring the corpus does not own and cannot ship, and #180 shows
  settings wiring is a human-owned surface. Named as an untaken road with a real reason.

## Panel-vs-single record

**Panel (3), because it touches architecture, crosses a repo-ownership boundary, and the Admiral
explicitly refused to pre-rule the fork.** Surfaced for overturn.
