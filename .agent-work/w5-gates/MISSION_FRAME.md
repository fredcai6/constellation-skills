# Mission Frame — w5-gates (epic #418 wave 5, crew 1)

**Orientation mode: `DEGRADED-NO-MAP`.** The context step looked for a packet map at all four
resolution candidates and found none — this is the constellation skill-SOURCE repo and it carries no
`docs/architecture/` map, no overlays, and no decision anchors. This frame is therefore cut from the
four documents the orientation receipt hash-pinned as substitutes, and **cites no map anchor ids**,
because there is no map for an anchor id to be a member of. Naming ids here would be a same-breath
assertion, which is exactly what the frame check refuses.

The hash-pinned reading this frame is built from:

- `README.md` — section "Repo layout vs. installed layout": the repo-vs-installed duality.
- `docs/CHECKLIST_SCHEMA.md` — the engine's condition kinds, evidence shapes, and waiver semantics.
- `docs/agents/ORCHESTRATOR_CONTEXT.md` — subsystem rigor and the evidence-and-verification map.
- `docs/agents/GLOSSARY.md` — project terminology.

This is **not** a trivial-change skip. The frame is shrunk to what the substitutes actually carry.

## Intent

Fix the three defects that make the gates at both ends of a Constellation run unclosable, so six
issues close. Every one of the three is an instance of the epic's central finding: a check whose
signal is identical in the healthy and the defective world. Two are its mirror — **a check that
cannot pass**, which invites a waiver or a doctored verdict. One turns out, on inspection, to be at
risk of becoming **a check that cannot fail** if fixed the way its issues suggest.

## Affected Capabilities

The substitutes name capabilities in prose, not as anchor ids. The three this run touches:

- **Role-artifact verification** — `ORCHESTRATOR_CONTEXT.md` classes "workflow mechanisms and
  verifiers" as a *strengthened durable system* whose required evidence is "targeted automated tests
  plus relevant broader suite". Both fix A and fix B land inside that class, so both owe targeted
  tests plus the broader suite, and neither has a no-test-surface exception available.
- **Boundary transition verification** — the closure check for an Admiral boundary. Today it can only
  be satisfied by a boundary that authorizes a launch, so a boundary that correctly exits `stop`
  can never close it.
- **Spine instantiation and archive closure** — the shipped Commander spine template's archive
  postcondition, and the token resolution that fills it at instantiation time.

## Examples / Events

- **The live specimen for fix A** is this epic's own `w4-to-close` boundary: a recorded, verified
  `stop` transition that the closure check cannot accept. It is the fixture, and it is real.
- **The live specimen for fix B** is this run itself: the guard refuses from this worktree, so the
  spine's own `execute` closure check cannot pass here — on every Commander run, not just this one.
- **The live specimen for fix C** is every successful epic: the archive check accepts only an OPEN
  pull request, so a merged one — the strongest evidence the work landed — fails it.

## Structural Anchors

No `struct:` ids exist to cite. The structures this run lands in, named by path, are the three files
the launch order assigns to this crew alone, plus their tests:

- `scripts/verify_iterative_role_artifacts.py` — fixes A and B.
- `skills/commander/templates/COMMANDER_SPINE.template.json` — fix C.
- `scripts/init_work_area.py` — inspected for fix C's token resolution; expected to stay untouched.

`README.md`'s layout section is the one structural fact this run genuinely depends on: a skill lives
at `skills/<name>/` in the repo and is bundled to `constellation-<name>/` under the agent's skills
root when installed, with shared infrastructure copied into every bundle so each is self-contained.
Fix B's whole job is to answer *which of those two shapes am I running from* — and the repo's own
name, `constellation-skills`, collides with the installed prefix, which is the defect.

## Governing Constraints / Assumptions

- **The engine's verdict for a `command` condition is the exit code.** `docs/CHECKLIST_SCHEMA.md`
  states a `command` check "runs `check.command`" and passes on "exit 0", and records only
  `{cmd, exit, shell}` as evidence. Standard output is not part of the verdict. Any check text this
  run authors or repairs must therefore carry its verdict in the exit status — a command that prints
  a falsy word and exits 0 is a check that cannot fail. This constraint governs fix C directly.
- **`command` check text runs under a POSIX shell.** Same document. An unquoted `<` in check text is
  an input redirection, not a placeholder — this is the actual failure mode of the archive check, and
  it is not the failure mode either issue describes.
- **A waiver is the human's decision, recorded, never an agent's quiet satisfaction.** Same document.
  The existence of the waiver path is why fix A is worth doing rather than routing around: the epic
  should not have to spend a waiver against the human's name to close a gate that is simply wrong.
- **Verifier changes owe targeted tests plus the broader suite** (`ORCHESTRATOR_CONTEXT.md`).
- **Pushes and pull requests need explicit human approval** unless pre-approved for the work
  (`ORCHESTRATOR_CONTEXT.md`, Repo Action Authority). The launch order pre-approves opening and
  pushing this run's pull request; it approves nothing on `main`.

## Decision Anchors & Decision Pressure

No `decision:` anchors exist in this repo to inherit — there are no decision anchors at all. The
choices this run forces are therefore all pressure, carrying no grade, surfaced as candidates:

- **Decision pressure — how a `stop` boundary satisfies its closure check.** The launch order
  pre-rules the shape and names two acceptable alternatives. Resolved understanding says two clauses
  block a `stop` packet, not one, so the pre-ruling's option 1 needs option 2 to be implementable at
  all. The Admiral has ruled: take them combined.
- **Decision pressure — how a running process identifies an installed bundle.** By structure, not by
  name. Widening the guard so it passes everywhere is explicitly refused: that would convert a check
  that wrongly refuses into a check that cannot fail, which is worse.
- **Decision pressure — what question the archive check is asking.** "Is there a pull request
  carrying this work" rather than "is there an open one". The narrower reading is the defect.
- **Decision pressure — whether boundary freshness is in scope at all.** Deferred, with a
  falsification rather than a shrug: the stateless variant is green in exactly the world it was
  written to catch. Routed to triage as recommend-and-defer.

## Claims / Evidence Surfaces

No `claim:` ids exist. The claims this run must leave checkable, and how each is checked:

- *A `stop` boundary with a recorded, verified, rendered transition packet closes its gate.* Checked
  by a test that exercises the `stop` path — which has never been exercised — over a fixture copied
  from the live packet, never the live packet itself.
- *A closure check still goes red on a corrupted packet.* Checked by a mutation test. Not
  overridable. A closure check that passes on an unverified packet has moved the defect, not fixed it.
- *The guard answers "where am I running from" correctly in all three places it is asked* — installed
  bundle, source repo, Commander worktree. Checked by a test per location; the third location is in
  neither issue and is a finding this run returns.
- *The archive check passes on a merged pull request and fails when there is none.* Checked by
  running it against real branches in both states, with the verdict read from the exit code.
- Per `ORCHESTRATOR_CONTEXT.md`, each of the above owes a targeted test **and** the relevant broader
  suite; naming both commands is required.

## Map Confidence / Staleness / Disputes

- **The architecture map is absent, not stale.** Confidence in it is not low — there is nothing to
  have confidence in. The orientation receipt escalates this to the Admiral as a standing repo-level
  gap, not as a blocker for this run.
- **The one unmapped seam this run actually depends on is the source-repo/installed-bundle duality**,
  which is precisely what fixes B is about. Nothing in the repo records it as an architectural fact;
  `README.md` documents it in prose, and that prose is hash-pinned here.
- **How this alters the plan:** because no map asserts the structural relationship between
  `skills/<name>/templates/*.template.json`, the top-level `scripts/` they invoke, and the installed
  bundles those templates are copied into, no gate in this plan may assume it. Every gate that
  depends on that relationship must **measure it on disk** — the guard's behavior is verified by
  running it from each of the three locations, not by reasoning from a map that does not exist. That
  is a verification step planned in place of a trusted map, which is the required response to an
  unverified area.

## Out of Scope

- `scripts/checklist_engine.py` and `tests/test_checklist_engine.py` — another crew's sole writer
  this wave. If a fix appears to need them, that is a float, not a decision.
- `scripts/install_constellation.py`, the handoff templates, `docs/CREW_CONTEXT.md`,
  `docs/TREND_SNAPSHOT.md` — other crews.
- `ADMIRAL_SPINE.template.json` — not this run's file, which is why a separate boundary mode is
  declined: that template names the mode string.
- The `repair` decision's authorization question — a real question, deliberately untouched.
- Boundary freshness — deferred with the falsification above, not silently dropped.
- Hooks and any `settings.json`. No issue closed that this run did not verify. No observation
  promoted into doctrine.
