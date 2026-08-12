**What this run produced**

Design-it-twice on the episode-record interface (4 parallel candidates under distinct named
constraints), a defended convergence recommendation floated to the Admiral, a mission frame,
and a frozen 3-gate `execute.json`. Execution has NOT started — it is deliberately blocked at
`e0-context` p1 pending the Admiral's ruling on the floated convergence choice, because
`decision:convergence-is-human` forbids self-converging and proceeding.

**What went well**

- The panel paid for itself, measurably. Four agents under four constraints, no contact,
  converged on four decisions (one file per episode; retirement never deletes; the LLM never
  writes the store directly; cause and remedy separately attachable). A single pass would have
  produced those same four as unargued assumptions rather than findings — a concrete
  bias-to-yes argument for design-it-twice from this run's own evidence.
- Both cold critics found real defects; neither was a rubber stamp. The design critic found I
  had manufactured consensus on two of six "unanimity" claims (verified before accepting:
  `durable_root()` appears in candidates A:1, B:5, C:0, D:0 — and D was the one I
  recommended). The plan critic found the gate plan had no exercised test for the priority-1
  non-foreclosure obligation, the very thing `decision:no-foreclosure-is-testable` rules must
  be shown rather than hoped.

**Friction / unclear**

- A doctrine instruction a delegated Commander cannot follow. `commander-core.md` says every
  dispatched subagent must be told to deliver via `SendMessage`. A delegated Commander runs as
  a teammate, and teammates cannot spawn named subagents ("the team roster is flat"), so the
  subagent has no channel back. All four panel dispatches failed on first attempt. Filed as #314.
- The repo's own documented test command false-reds. 24 places prescribe `py -m pytest`; on
  this host `py` resolves to a runtime with no pytest, so the documented command looks like a
  broken suite while `python -m pytest` is green (1157 passed, 2 skipped). One of the 24 is a
  drill's worked example of an engine command postcondition, so an agent copying it into a
  gate gets an `advance` refusal reading as "your change broke the tests." Filed as #313.
- `stage_feedback.py` and `verify_agent_feedback.py` disagree about the body format, and the
  staging script does not check. The staging script reported "staged feedback ready" twice;
  the verifier then failed the result twice. Two distinct undocumented requirements: the
  signal sections must be **bold labels** (`**Friction / unclear**`), not `##` headings — and
  more sharply, `_entry_block()` delimits an entry from its `## <work-id>` heading to the
  *next* `## ` line, so ANY `##` subheading in the body silently truncates the entry to
  nothing. A body written with normal Markdown headings fails with a message ("no bullets
  under its signal sections") that describes a symptom well downstream of the cause. The
  staging script's own help text cites `_staged_feedback_errors`, so it knows the contract; it
  should validate the body against it, or at minimum name the three required labels.
- Engine friction: `attest` succeeds on a `pending` step, then `advance` refuses it. Hit twice
  (`understand`, `plan`) — attesting works while the step is still `pending`, and only the
  later `advance` reveals `start` was needed first. Having `attest` warn or imply `start`
  would remove the trap. Minor: two commands lost, no gate.
- `current` rejects `--session-id`, though the spine's init text says to pass it "on every
  mutating engine call." Correct behaviour (it is not mutating), slightly under-documented.

**Crew-reported friction**

- none — confirmed after review: the four design-panel subagents and both cold critics all
  returned complete deliverables with no blockers and no friction reported in their returns.
  No implementer/reviewer crew has been dispatched yet, because execution is gated on the
  convergence ruling, so this is a genuine null rather than uncollected.

**Improvement signals**

- An inherited lesson pasted into a launch order still did not fire.
  `lesson:prove-command-fails-postcondition` was handed to me verbatim under a heading naming
  it relevant, and I still authored three "the writer REJECTS X" postconditions as
  `check: null` attestations. A cold reader caught it. Suggests the launch order's
  inherited-lessons section needs a verification step against the authored artifact rather
  than more prominent placement.
- `lesson:verify-launch-order-claims-against-code` held again and earned its cost.
  `grep -ril "episode|stratum|rhyme"` returned zero hits, converting "is this already shipped?"
  from an open worry into a settled fact before planning. Negative this time (the premise
  held, no honest-null), but the check is what made the premise known.
- Design-it-twice convergence needs a per-claim verification discipline. The
  `design-it-twice-brief.md` output contract asks for a recommendation with axis-by-axis
  reasoning; it never asks the converger to verify cross-candidate claims mechanically. That
  gap is exactly where my manufactured consensus lived.

**Execution-phase addendum (gates g1-g3, added after the gates ran)**

- Three of four gates closed: g1 (record grammar doc, 3 review rounds + 2 reworks), g2 (validated
  writer, 2 rounds + 1 rework), g3 (retrieval + acceptance, 1 round, APPROVE). g4 is blocked by
  design on Tommy's retirement-layout ratification. PR #320 open, not merged.
- The review rounds earned their cost. Every g1 round found a real instance of one root cause:
  describing a mechanism concretely while silently assuming the layout held for ratification. The
  g2 round demonstrated a silent data corruption — a U+2028 value forging the exact status line
  the guard existed to block. The g3 round proved by eight mutations that the acceptance tests can
  actually fail, which is stronger evidence than the tests passing.
- Two defects were fixed under fix-now triage on the same precedent, both found by review rather
  than by me: `artifact-ref` losing trailing whitespace on round-trip, and `select_episodes()`
  degrading a bare string to character membership.
- The rework cap is 3 per gate and g1 used 2. Worth knowing that a prose gate can approach the cap
  legitimately — the cap is not only for code.

**The design-it-twice blind spot — stated plainly, because it outlives this issue**

A panel varies what it is told to vary, and inherits everything it is not.

Four candidates compared record shapes rigorously, under four deliberately distinct constraints,
with no contact between them. All four put the store at `.agent-work/episodes/`. Not one checked
whether that directory was tracked. It is gitignored at `.gitignore:1` with zero tracked files,
so all four identically violated `decision:markdown-in-git` — the one storage ruling that was
settled, human-given, and non-negotiable.

The convergence step could not catch it, because the panel agreed. Unanimity across differing
constraints reads as strong evidence, and here it was evidence of nothing but shared inheritance.
That is the same failure as my manufactured-consensus error one level up, and the two together
say the mechanism's weak spot is not how candidates differ but what they share.

The precise trap is worth naming exactly: **copying the neighbour's location copied the one
property the new store must not have.** `LESSONS.md` is a deliberately transitory inbox — its own
preamble says it is "where lessons pass through, not where they live." The episode spec's whole
point is that the structured episode *outlives* its consolidation. The prior art was the right
model for the record grammar and precisely the wrong model for where the records live, and
nothing in the brief distinguished those two kinds of borrowing.

Two mitigations, one cheap and one general. Cheap: for any candidate that names a **path**, run
`git check-ignore` on it before comparing — this would have caught it in one command, before any
design work. General: at convergence, ask what every candidate assumed **in common** and verify
that, rather than only adjudicating where they diverge.

It surfaced at a gate's deliverable path check, which is late but not too late — worth noting
that the check that caught it exists because the handoff template requires classifying every
deliverable path as committed or local-only. That template line did real work here.

**Portability addendum — the local suite could not have caught the CI failure**

PR #320 went CI-red at 39 failures after a locally-green run, on `Path.read_text(newline=)`
(Python 3.13+) against CI's pinned 3.12. Here `python` is 3.14.3 and `py` is 3.12.13 — the CI
version — so local green was answering a different question than CI, and nothing said so.

The sting is that the skew came from my own filed guidance: #313 says `py -m pytest` false-reds,
which routes agents onto the interpreter *further* from CI. False-red and false-green are the
same defect with opposite signs. Posted the version numbers to #313, plus the trap that a
launcher name can resolve differently in a shell than in a subprocess spawned by the test runner
(`py` was 3.12 from the shell and 3.14 from inside pytest), which made my first guard silently
skip — a guard that never runs reads as coverage while providing none.

Fix centralized in two named helpers rather than scattered across 13 call sites, because the
`newline=""` semantics are load-bearing for the line-boundary guard. Guard added and
mutation-verified. CI green at 1270 passed.

**Two additions the Admiral asked be stated plainly**

The traceback under-reported the blast radius. CI named one call site; there were 13, and the
other twelve sat in files the failing tests never reached. Patching the named line would have
produced a green CI over a still-broken store — the worst outcome available, since that green
would then have been trusted. A traceback reports where execution stopped, not where the defect
lives; for an environment failure those diverge, because an unavailable API is unavailable
everywhere it is used while only the first reached use raises.

And a cross-run shape worth more than any of its instances: a check that cannot fail is
indistinguishable from a check that passed. Three instances in this epic by three different
mechanisms — my floor guard discovering by name, finding nothing, and skipping green; #300's two
vacuous postconditions; and the standing round-trip lesson's tests that only ever see clean
artifacts. Mutation-testing a guard (break it, watch it go red, restore) is the cheap general
repair, and is what turned my own guard from an assertion into evidence.

**The panel blind spot has two shapes, and the second one is not the panel's fault**

Stated plainly at the Admiral's request, because the second shape indicts brief-authoring rather
than candidate diligence.

A panel inherits from the **neighbour it copies** and from the **brief it is handed**, and
neither is visible in how the candidates differ. My case was the first shape: four candidates
took the store's location from the LESSONS.md prior art, and copying the neighbour's location
copied the one property the new store must not have.

Commander-300's case was the second, and it is the more insidious one. Its convergence claimed
"metadata only, never file content" as a panel finding; it was the brief's own framing handed
back three times and read as agreement. The assumption did not come from prior art the panel
chose to copy — **it came from the person asking the question.** No amount of candidate-side care
could have surfaced that, because the candidates *are* the echo. Which means a brief author
cannot audit their own framing by reading the candidates, and the shared-assumption check for
that shape has to be run by someone who did not write the brief.

Both shapes pair with this run's manufactured-consensus error into one statement: these are all
failures about what candidates SHARE rather than how they differ, and in each case agreement read
as evidence when it was only inheritance.

**Gate g4 addendum — the ratified layout, and what binding it taught**

Tommy ruled the retirement layout (the file moves) and g4 bound it. PR #320 merged as `195e893b8`
after gating on the CI exit code verified at source. Final: 1308 passed / 2 skipped on CI.

The deferral paid off measurably: binding the ratified answer changed adapter bodies and did not
require changing a single g3 retrieval primitive. The stop condition written for that exact
possibility never fired. Two reworks and three review rounds at g1 — spent keeping the decision
open in *implementation* rather than only in wording — are what bought that.

Binding it also relocated the silent-omission class twice more, and full cold panel caught both.
The first would have shipped a store **unreadable by its own tooling**: the non-episode classifier
did not move when membership moved from file content to file location, so the gate's own `README`
placeholders became a phantom episode id in both scanned directories. That is the same defect
shape as the newline guard two gates earlier — a hand-maintained list standing in for a predicate
the code can decide — which is why it landed as a *confirm* on an existing lesson rather than a
new one. The second is filed as #321.

Two process notes worth more than either bug. **A cold panel on a small diff was not ceremony:**
the diff at g4 was four adapter bodies, and it hid a defect that made the deliverable unusable on
first use. Sizing review to diff size would have missed it. And **I nearly dismissed a real
finding through an incomplete reproduction** — the reviewer's fifth trap did not reproduce on my
first two attempts, because I read its precondition as "non-empty store" when it was actually
"traversal target present." Two failed reproductions is not a refutation, and the cost of assuming
otherwise would have been shipping a merge condition unmet.
