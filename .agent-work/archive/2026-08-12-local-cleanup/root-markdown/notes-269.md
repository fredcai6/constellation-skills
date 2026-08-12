# notes-269.md — Commander working notes, issue #269

Sole writer this wave: governor-269 Commander. Do not rename to "findings-269.md" (harness Write guard).

## Understand — reconciled problem statement (delegated mode, no live human)

Source of truth: `LAUNCH_ORDER-269.md` (Mission, Prior-Wave Verdicts, Pre-Rulings). Reconciled against
current code at base commit `2c169a5` per `lesson:verify-launch-order-claims-against-code`.

**Verified claims (code-grounded, not taken on the order's word):**

- `.claude/settings.json` (worktree copy) wires every hook via
  `py "${CLAUDE_PROJECT_DIR}/scripts/hooks/spine_rail.py" <Event>` — the hook *script path itself* is
  resolved through `${CLAUDE_PROJECT_DIR}`, an env var expanded by the harness before the hook process
  ever starts. `scripts/hooks/spine_rail.py:54` and `scripts/hooks/gauge_writer_hook.py:384` also read
  `os.environ.get("CLAUDE_PROJECT_DIR")` internally for state-path resolution. Two independent
  resolution points, same variable, both fixed at whatever value the harness set at session launch.
- `scripts/verify_worktree_isolation.py` (read in full) checks only git-worktree topology: registered
  worktree, distinct from primary checkout, distinct from siblings (gate mode); `git rev-parse
  --show-toplevel` matches an expected path (`--here` mode). It does not read or report
  `CLAUDE_PROJECT_DIR` anywhere in its source — confirms the order's claim that isolation-as-measured
  and hook-code-as-run are two different, currently-unlinked facts.
- Edit targets both exist at the named paths: `skills/admiral/templates/LAUNCH_ORDER.template.md` and
  `skills/admiral/references/fleet-doctrine.md` (NOT top-level `references/` — that path does not exist
  in this repo; the launch order's `references/fleet-doctrine.md` shorthand resolves under
  `skills/admiral/`).

**Mission (unchanged from order, restated for the record):** three parts, priority order:
1. Doctrine — state the fresh-process-probe rule in the launch-order template's Workspace section and
   in fleet-doctrine.md. Pre-ratified for edit (`decision:doctrine-edit-needs-human`).
2. Detection — should `verify_worktree_isolation.py` also report which project dir hooks will resolve
   to. Verdict may be "no"; a reasoned no is a complete answer.
3. Analysis only — should a worktree-scoped agent run worktree hooks at all. Recommend, do not implement.
   `decision:no-resolution-change` forbids changing resolution behaviour in this PR.

**No map exists** (`docs/architecture/` absent in this repo — skill-source repo, no packet map). Mission
frame will be shrunk accordingly per commander-core.md's "map is context, not a tax" allowance; the
launch order's pasted prior-wave verdicts substitute for map anchors on this narrowly-scoped, mostly
doc-and-analysis mission.

**No gap found requiring an Admiral round-trip.** The order's baseline claims check out against code;
proceeding under the frozen order.

## Mission frame (shrunk — no docs/architecture map in this repo)

**Intent.** Make the CLAUDE_PROJECT_DIR-pinning constraint visible where an agent meets it (doctrine),
decide whether the isolation checker can also detect it, and produce a reasoned recommendation on
whether worktree-scoped agents should run worktree hooks at all (analysis only, no implementation).

**Affected capabilities.** `scripts/verify_worktree_isolation.py` (isolation gate, read-only this run);
`skills/admiral/templates/LAUNCH_ORDER.template.md` `## Workspace` section; `skills/admiral/references/fleet-doctrine.md`
"Worktree isolation is a harness no-op on Windows" section.

**Structural anchors.** `scripts/hooks/spine_rail.py:54`, `scripts/hooks/gauge_writer_hook.py:384` (both
resolve `CLAUDE_PROJECT_DIR` independently); `.claude/settings.json` (committed, worktree-visible, wires
spine_rail.py) vs `.claude/settings.local.json` (gitignored, main-checkout-only, wires gauge_writer_hook.py
— confirmed absent from this worktree, see Live evidence below).

**Governing constraints/decisions.** `decision:no-resolution-change` (no change to resolution behaviour,
part 3 analysis-only); `decision:fail-open-is-inviolable`; `decision:doctrine-edit-needs-human` (pre-ratified
for parts 1-2); `decision:verify-by-fresh-process`; `decision:no-threshold-values` (not touched by this
mission — no thresholds involved); `decision:scope-is-visibility-not-repair`.

**Claims/evidence surfaces.** Wave-1 evidence-202-crosswrite-gauge.json (main checkout, read-only). This
run's own live reproduction (below) is a second, independent, fresh-process data point.

**Map confidence.** No packet map exists (skill-source repo). Confidence in the code-level claims above is
HIGH — grounded directly in source reads and a live in-session reproduction, not inference.

**Out of scope.** Any change to `CLAUDE_PROJECT_DIR` resolution; any threshold value; #257
(skills-work-installed); general worktree-isolation repair beyond visibility.

## Live evidence — fresh-process reproduction, this session (not wave-1's, not a fixture)

While driving this very Commander run (dispatched into worktree `C:/Programs/constellation-skills-wt/governor-269`,
isolation-verified OK), ordinary Bash tool calls fired real PostToolUse hooks. Checking the main checkout's
binding file after several such calls:

`C:/Programs/constellation-skills/.agent-work/.spine-rail-binding.json` (main checkout, NOT my worktree) now
contains, under this session's id, an entry for MY OWN spine:
```
"C:\\Programs\\constellation-skills\\.agent-work\\governor-269\\spine.json": {
  "spine": "C:\\Programs\\constellation-skills\\.agent-work\\governor-269\\spine.json",
  "engine_session": "governor-269-session",
  "worktree": "C:\\Programs\\constellation-skills",
  ...
}
```
My REAL spine.json lives at `C:/Programs/constellation-skills-wt/governor-269/.agent-work/governor-269/spine.json`
(confirmed present, growing, journal updating). The hook-observed "worktree" is the MAIN CHECKOUT, and the
recorded spine path is a phantom path under the main checkout that was never created
(`C:/Programs/constellation-skills/.agent-work/governor-269/` does not exist — confirmed by `ls`). This is a
live, fresh, non-fixture reproduction of the exact #269 defect for THIS run, not a re-citation of wave-1's.

**CLAUDE_PROJECT_DIR is not visible to ordinary tool-call subprocesses.** Directly probed in both this
session's Bash tool (`echo "CLAUDE_PROJECT_DIR=$CLAUDE_PROJECT_DIR"` -> empty) and PowerShell tool
(`$env:CLAUDE_PROJECT_DIR` -> empty; `$PWD` -> `C:\Programs\constellation-skills`, the main checkout, despite
this being my dispatched worktree session). The harness evidently substitutes/injects `CLAUDE_PROJECT_DIR`
only at the moment it constructs and spawns an actual hook subprocess (matching `spine_rail.py`/`gauge_writer_hook.py`
each independently reading `os.environ.get("CLAUDE_PROJECT_DIR")`), not into arbitrary Bash/PowerShell tool
subprocesses. This is the key finding for part 2 (see Gate g2 below).

**gauge_writer_hook.py is wired only via a gitignored, main-checkout-only file.** `.claude/settings.local.json`
exists at the main checkout (wires `gauge_writer_hook.py` on PostToolUse `*`) but does NOT exist in this
worktree (confirmed: `ls .claude/` in the worktree shows only the committed `settings.json`, which wires
`spine_rail.py` only). Relevant context for part 3's recommendation, not something this run fixes (#257-adjacent,
out of scope).

## Gate plan (execute.json) — 3 reasoning gates, one per mission part

No crew dispatch: all three deliverables are prose/analysis/diagnosis produced from context already held
(doctrine edits, a detection verdict, a recommendation) — no new code path, no independently-verifiable
runtime behavior change. Per commander-core.md "Crew gate vs reasoning gate," this is the correct shape;
each gate's invariants are pre-authored below and held to *higher* self-scrutiny for lacking a second
reviewer.

- **g1 — Doctrine (Part 1, required).** Edit `## Workspace` in LAUNCH_ORDER.template.md and the
  "Worktree isolation is a harness no-op" section in fleet-doctrine.md to state the fresh-process-probe rule.
  Invariant: both files, post-edit, contain a sentence naming that hook changes/resolution cannot be
  validated from inside the worktree that contains them (grep-checked).
- **g2 — Detection (Part 2, required, verdict may be "no").** Decide and document whether
  `verify_worktree_isolation.py` should report hook-resolution project dir. Invariant: a documented verdict
  with evidence exists (attest, no command check — this is a diagnosis, not a runtime assertion).
- **g3 — Open question analysis (Part 3, analysis + recommendation only, no implementation).** Document the
  worktree-hooks-vs-pinned-hooks tradeoff and a recommendation. Invariant: documented recommendation exists
  (attest).

## Part 2 verdict — Detection: NO, verify_worktree_isolation.py should not report hook-resolution project dir

**Verdict: NO.** A reasoned negative, per the Honest-Null Clause.

**Reasoning, grounded in the Live evidence section above:**

1. `CLAUDE_PROJECT_DIR` is not visible to the process context `verify_worktree_isolation.py` actually runs
   in. Tested directly, live, this session, in both the Bash tool (`echo "CLAUDE_PROJECT_DIR=$CLAUDE_PROJECT_DIR"`
   -> empty) and the PowerShell tool (`$env:CLAUDE_PROJECT_DIR` -> empty). This is the exact process class
   `verify_worktree_isolation.py` runs in when a Commander executes it as its first step (an ordinary script
   invocation, not a harness-constructed hook command). Adding a read of `os.environ.get("CLAUDE_PROJECT_DIR")`
   to the script would read empty every time it matters, which is worse than silence — it reads as "no
   override, you're fine" when the true answer is "unknowable from here, and something else entirely governs
   it."
2. Even the fallback signal doesn't help: `os.getcwd()` inside the script would just restate what `--here`
   already establishes topologically (the script's own invocation directory) — no new information about what
   a *later* hook subprocess will resolve, since that resolution is proven (Live evidence) to be governed by
   the fixed, harness-internal `CLAUDE_PROJECT_DIR`, independent of the calling process's cwd.
3. **The moment-of-check problem, concretely, not hypothetically.** The launch order's own doctrine (now also
   restated in g1's doctrine edit) has the isolation check run as the Commander's **very first action, before
   any git operation**. At that moment, in this run, zero hooks had fired yet — so even the one side-channel
   that DOES carry the resolved value after the fact (the `.spine-rail-binding.json` "worktree" field, see
   Live evidence) had no entry for this session yet either. There is no data source available at the moment
   the check is meant to run that would let it answer the question. This is a direct instance of the Honest-
   Null Clause's own example: "the check runs at a moment where the answer isn't knowable."
4. A heavier alternative — have the check itself fire a real hook (e.g. trigger a trivial tool-use event and
   observe the side effect, the way this run's own Live evidence was gathered) — would work, but is out of
   proportion to a sub-second topology gate meant to run before any real work starts, and effectively
   duplicates launching a fresh headless probe (already the prescribed technique for a Commander who actually
   needs to validate hook-resolution, per `decision:verify-by-fresh-process`, now stated in g1's doctrine
   edit). Building that into the mandatory first-step gate would slow every dispatch to pay for a check most
   missions (anything not touching hook code) don't need.

**What this run tested:** live CLAUDE_PROJECT_DIR visibility in Bash and PowerShell tool subprocess
environments, this session, fresh (not a fixture); the binding-file's existing content and its absence at
the moment isolation-check-equivalent timing would apply. **What this run did NOT test:** whether a
separately-launched headless `claude -p` process's own top-level shell (as opposed to Bash/PowerShell
*tool* calls inside an already-running interactive session) exposes `CLAUDE_PROJECT_DIR` differently — not
needed for this verdict, since the question is about `verify_worktree_isolation.py`'s ordinary invocation
context (which this run's own dispatch — a real Commander's first step — already exercises directly), not
about the headless-probe technique itself (that technique is unaffected by this verdict; it remains the
right tool for missions that actually need to validate hook-resolution changes, per `decision:verify-by-fresh-process`).

**Consequence for the plan:** no code change to `verify_worktree_isolation.py` in this PR. The visibility
gap is closed instead by g1's doctrine edit, which puts the warning at the exact place and moment a
Commander reads the Workspace section — immediately above the instruction to run the very check that
cannot detect the mismatch. Per `decision:scope-is-visibility-not-repair`'s own settle clause: "if part 2
lands and the mismatch is legible at claim time, visibility was sufficient" — here it lands via g1's text,
not via g2's code, and that satisfies the same settle condition.

## Part 3 — open question: should a worktree-scoped agent run worktree hooks at all (analysis + recommendation, NOT implemented)

**Two resolutions in play, currently conflated.** `spine_rail.py`/`gauge_writer_hook.py` use
`CLAUDE_PROJECT_DIR` for two distinct things that could, in principle, be decoupled: (a) which **hook code**
runs, and (b) where **hook state** (binding file, gauge.json) is written. The launch order frames this as one
question ("should worktree hooks run at all"); the evidence gathered this run says it is really two.

**Arguments for keeping hook CODE pinned to the main checkout (status quo):**
- **Anti-tamper / one consistent rail.** If hook code resolved per-worktree, an agent's own branch could
  edit the governance code that judges it (e.g. weaken the fail-open check, alter thresholds, disable the
  trip mechanism) and that edited code would then govern that same agent, inside that same worktree, before
  any human or reviewer ever sees the diff. Pinning to the main checkout means the referee is never the
  thing under edit. This matters specifically for the Context Governor (epic #267's own subject): its whole
  job is to catch a degrading agent's own judgment, which is exactly the scenario where "trust the agent to
  not have miscalibrated its own referee" is weakest.
- **One code path to reason about and debug**, matching `decision:fail-open-is-inviolable`'s spirit — the
  fleet already treats this rail's reliability as inviolable; a rail whose code varies by worktree is a
  harder reliability guarantee to make.

**Arguments for resolving hook CODE per-worktree:**
- **Testability in place** — this is #269's own root complaint: a Commander cannot validate its own hook
  change without a fresh-process workaround. Per-worktree resolution would make "edit, then just run it"
  work directly.
- Symmetry with git isolation: every OTHER artifact (source, tests, `.agent-work/`) is worktree-scoped;
  hooks are the one exception.

**Recommendation: keep hook CODE pinned to the main checkout. Do not switch to per-worktree code
resolution.** The anti-tamper property is a safety property specific to a governance rail, not a
convenience preference, and testability is already addressable without it: part 1's doctrine edit plus
`decision:verify-by-fresh-process` institutionalize the fresh-process workaround as the sanctioned path, and
that workaround gets cheaper with tooling (e.g. a small wrapper script around a headless `claude -p` probe)
rather than by weakening the pin. This is a recommendation only, per `decision:no-resolution-change` — the
human takes it up.

**The state-path half is a separate, real, currently-open defect that this recommendation does NOT resolve.**
Cross-write is empirically confirmed twice now — wave 1's evidence-202 (an Admiral opus reading crossing into
a Sonnet Commander's directory) and this run's own live reproduction (Live evidence section above: my
governor-269-session's spine-rail binding entry, and by the same mechanism its gauge writes, land in the main
checkout's `.agent-work/`, not my worktree's). Decoupling state-path resolution from code-path resolution
(pin code, but scope state per-worktree) sounds like a clean fast-follow but is **not** cheaply achievable
today: it needs a reliable **live, per-call** signal for "which worktree is this agent actually in," and two
independent findings now rule out the two obvious candidates — `CLAUDE_PROJECT_DIR` (this run, and the
launch order's own framing) and the PostToolUse payload's `cwd` field (wave 1 finding (b), pasted in this
order: "cwd on a PostToolUse payload is fixed at session launch and inherited by subagents"). A real fix
needs either (a) a new explicit signal threaded from the dispatching Commander's own `claim`/dispatch call
(the engine's `claim --worktree` argument already carries this — worth checking whether it can be surfaced
to the hook layer, not verified this run) or (b) keying state by something already unique per work-id/session
rather than by resolved directory at all. **Flagging this as a triage candidate for the tracker** (see Triage
section) rather than solving it here — solving it is squarely repair, not visibility, and out of this
mission's scope per `decision:scope-is-visibility-not-repair`.

## Design-it-twice / cold-critic: named untaken road. The gate plan is a direct 1:1 enumeration of the
launch order's three already-frozen, priority-ordered mission parts — there is no novel architecture or
load-bearing interface choice at the gate-plan level to generate alternatives over (the alternatives that
matter are INSIDE g2/g3's analysis, not in how the gates are shaped). Skipping plan-alternatives and a
separate cold-critic subagent for the gate *shape* is a proportionate skip for a Sonnet-tier, single-session,
already-scope-frozen mission; the substantive part-2/part-3 verdicts below are instead held to higher
self-scrutiny per the reasoning-gate rule, and part 3 explicitly does NOT converge to an implementation
choice (that convergence is reserved for the Admiral/human, per `decision:no-resolution-change`).
