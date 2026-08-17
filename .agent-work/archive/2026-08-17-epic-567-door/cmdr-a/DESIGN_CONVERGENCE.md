# Design convergence — binding the MCP door to an existing spine

Lane A of epic #567. Base `600de020`. Written for a reader who has not seen the run.

**`decision:convergence-is-human-only`.** I generated and compared; **the human
picks.** This document is a defended recommendation, not a ratified choice.
Closing the gate that produced it does not settle it. Where I have already
implemented the recommendation, that is stated plainly below along with how to
revert it.

> ## AMENDED after a cold plan critic — read this first
>
> A cold critic (no authoring context) found 5 blocking defects in this document and
> the gate plan. Two changed the design, and the most important one **inverted this
> document's central argument.** The amendments are folded into the sections below;
> this box records what changed so a reader is not misled by a version they may have
> seen earlier. Full critique: `crew-handoffs/COLD_PLAN_CRITIC.md`.
>
> 1. **The containment root was too wide, and the comparison that chose it was
>    unmeasured on one side.** The original recommendation used
>    `_primary_checkout_for_lifecycle()`, which resolves `--git-common-dir` and
>    therefore jumps to the primary checkout — and `.worktrees/` nests *inside* it.
>    **Measured: 4205 reachable spine-shaped files, 3505 of them in other lanes'
>    checkouts** — a strict superset of the 683 I used to disqualify candidate C for
>    "maximum reach". I killed C on a number and crowned A on a sentence. The root is
>    now `<the door's own checkout>/.agent-work/` via `--show-toplevel`, plus a
>    cross-checkout refusal: **683, and zero cross-worktree.**
> 2. **The isolation section contradicted itself.** It said a sibling worktree's live
>    spine was reachable and, 18 lines later, that another checkout was not. A linked
>    worktree *is* another checkout. Fix 1 makes the reassuring sentence true; that is
>    the purpose of fix 1, not tidiness.
> 3. **One claim about guard strength was overstated** — see "Why A over B", corrected.
> 4. Two line references in this document were wrong and are corrected
>    (`_spine_open` is at `:968`; `_resolve_confined` at `:322`).
>
> Adopting fix 1 rather than only floating it is sanctioned:
> `decision:isolation-not-fencing` is graded `guess/admiral`, and a `guess` is revisited
> **freely** once its `settle:` experiment has run. Its recorded `settle:` was "name the
> property in the design doc and have the reviewer attack it" — which is exactly what
> happened. Regraded `settled/measured`.

## The question, in one sentence

Where and how does a running MCP door acquire a binding to a spine file that
**already exists**?

## Why this needed designing at all — the state of the code

The launch order's premise is that the door "binds `SPINE_FILE`/`SPINE_SESSION` as
module-level constants at launch." At `600de020` that is only half true, and the
half that is false changes the whole problem.

The previous lane A (`cleanup/a-door`, merged `33dc3086`) already shipped, under
`decision:bind-on-open-over-new-verb`:

- `_bind_process_to(spine_file, session)` (`mcp_spine_server.py:878`) — a named,
  module-level rebinder that moves both identity roots and mirrors them into
  `os.environ`.
- Late binding for all four import-time derivations of `SPINE` that made rebinding
  unsafe.
- `_unbound_refusal()` asked **per call, never cached**, explicitly because a
  rebind can happen mid-life.
- A module-wide AST pin asserting assignments to `SPINE`/`SESSION` are exactly
  `{module scope, _bind_process_to}`.

So the door can already rebind, safely, with a guard and a pin around the one place
that does it. **What is missing is a trigger.** `_bind_process_to` has exactly one
caller — `_spine_open` (`:1041`) — and `spine_open` mints; its own description says
it "acts on a spine that does not exist yet."

The design space is therefore not "how do we build per-dispatch identity." It is
**"where does the second call to `_bind_process_to` go."**

## The panel

Three candidates, each under one named distinct constraint. Panel rather than a
pair because this touches architecture and a recorded security property; doctrine
says "when in doubt, panel." Run as **fresh agents, not forks** — lane G's incident
this wave was its own context-inheriting fork driving the Commander's `spine.json`
under the same lease id, so each panel agent was told explicitly that it has no
spine and must not run the engine.

Untaken roads, named rather than silently skipped: **`max-flexibility`** (multi-spine
access from one door) violates `decision:one-spine-per-process-stands`, a `settled`
decision not mine to unsettle; **`ports-and-adapters`** (a pluggable "spine locator"
port) would be one adapter, and one adapter is a hypothetical seam.

| | A — `minimal-interface` | B — `no-new-tool` | C — `per-call-identity` |
|---|---|---|---|
| Shape | one new tool `spine_bind(spine_file)` | `spine_open` becomes adopt-or-mint on `work_id` | calls may name their own spine, confined to a bound **root** |
| Reach added *(one predicate, see note)* | **683**, cross-checkout **0** *(amended; was 4205/3505)* | any spine under `<root>/.agent-work/<work_id>` for any nameable `work_id` | **683**, 51 leased, **674** legal `--from-child` targets |
| New env var | no | no | yes (`SPINE_ROOT`) |
| Verdict | **winner, with one correction** | strong runner-up, self-refuted | **well-argued negative** |

> **Note on the counts, because an earlier version of this table compared numbers that
> were not comparable** (the critic's M9). Every reach figure above and below now uses
> **one predicate**, stated once: a parseable JSON dict with an `items` list, a `tasks`
> dict, and a truthy `work_id` (from `origin.work_id` or the top level) — i.e. exactly
> the population the corrected rule will bind. Measured **2026-08-16 in this worktree**.
> The tree is live and grows while you measure it: the critic's independent re-run
> differed by +1 and then +2 within seven minutes, as concurrent lanes wrote spine
> files. **Treat every number here as a snapshot, not a property of the population.**
> The earlier "124 spines" figure was files literally *named* `spine.json`, a different
> predicate over a different root, and comparing it to the 52-file census was comparing
> nothing.

### Four-axis comparison

**Depth.** B wins. It hides its whole existence/ambiguity matrix behind one library
function and adds no tool; the caller learns one optional word in a payload it
already parses. A is good but leaks one thing upward unavoidably — the caller must
possess the path. C is shallowest: it adds nine tool arguments and a configuration
variable, and pushes the containment question onto whoever sets `SPINE_ROOT`.

**Locality.** A wins. One dispatch function, one schema entry, one route, two
constant edits, one extracted helper; no caller of anything changes and no existing
tool changes behaviour. B is mixed by its own admission — it fans out into the
skills corpus, because the corpus currently tells dispatched crews their spine is
already bound and that instruction needs a second sentence, with a two-sided pin
over it. C fans out across `_identity_violation` itself, which is the one function
in the module that most rewards being left alone.

**Seam placement.** Genuinely contested, and it is the axis that decides the run.
B wins on the tests — every pin is already drawn around exactly the two places it
touches, and none has to move. A loses on the caller it inconveniences: someone who
just wants `spine_status` to work now needs to know a tool exists and spend a call
first. **But B loses on the boundary, and that outranks both.** B puts a
bind-to-anything capability behind an argument on a tool whose description promises
creation, guarded only by `_rebind_refusal` — the weakest guard in the module,
which fails open when no lease is held. C's seam is at the guard itself, and moving
that seam means re-opening a function whose docstring records six previous defeats.

**Testability.** All three are strong; A is most granular. Each of A's nine refusals
is a pure function of `(args, SPINE, filesystem)` and independently reachable, and
the harness already exists (`_load_module` gives a fresh module per binding,
`FullStdioRoundTripTests` shows the two-door round trip). B is testable as a library
function with no door at all. C's hard part is not testability but that its central
property is a claim about what is on disk at call time.

## What killed C, in its own measurements

C designed its constraint as well as it can be designed and then reported the
negative. Its root has no good source, and the constraint that requires a root is
what makes that unanswerable:

- `SPINE.parent` is **safe** — its reach delta is exactly two files in a real work
  area (`execute.json` and `g1-review/review.json`, the Implementer's and
  Reviewer's own plans, which is precisely the capability `IDENTITY_TRADE.md` §2
  named as the price it paid). But it is derived from a bound **file**, so an
  unbound door has no root at all. It cannot answer the question asked.
- `SPINE_ROOT` set per dispatch is safe but **buys nothing**: a launcher that knows
  the work area's path can set `SPINE_FILE` in the same breath.
- `SPINE_ROOT` with a static default is the only genuinely distinct option, and it
  is the maximum-reach one: **124 readable spines, 99 with no active lease, 674
  files carrying a `consolidation` key and therefore legal `--from-child`
  targets.** Since #609 the engine asserts nothing about location, so those 99 are
  writable.

And C's answer to "what do we delete" is, honestly, **nothing** — its only deletion
candidate is `IDENTITY_TRADE.md` §2's isolation sentence and the guard that enforces
it. A candidate whose only deletion is the security property is answering "nothing."

## What killed B, in its own words

B's self-objection is the most valuable single paragraph the panel produced:

> "I rejected the *tighter* design because it broke a test suite, and shipped the
> *looser* one because it broke none. A reviewer is entitled to read that as
> optimizing for green CI over the security property the CI exists to measure."

The reachable sequence B names and does not refuse: release the lease, `spine_open`
with any `work_id` in the tree, read another lane's gate state, claim it as
`constellation/<that work_id>`, drive it, and `spine_close` it if terminal.
`_rebind_refusal` fails open on "no lease" by design, and releasing is one call.

Its rejection of sub-shape (b) — lazy self-resolution from ambient state — is
nonetheless a **result worth keeping**: it measured that ambient resolution turns
~10 tests red, including `test_empty_spine_file_refuses_rather_than_binding_the_cwd`
(`test_mcp_door_unbound.py:223`). That is independent confirmation that inferring a
binding from the door's location is the exact fail-open defect the previous lane
deliberately removed, not merely a stylistic worry.

## The decisive measurement, and why the winner needs a correction

Candidate A derives the door's session from the spine's stamped `origin.work_id`,
and refuses (its `R7`) any spine lacking it. A named, in its own §7, the
measurement that would prove it wrong. **I ran it.**

Live spine-shaped JSON under `.agent-work/` and `.worktrees/*/.agent-work/`,
excluding `archive/` and `templates/`:

| | count |
|---|---|
| live spine-shaped files | **52** |
| carrying `origin.work_id` | **4** |
| no origin, but top-level `work_id` | **48** |
| **neither** | **0** |

**A as written refuses 92% of the live population**, and two of the refusals are
fatal to the mission specifically:

- `.agent-work/epic-567-door/spine.json` — **the Admiral's own live spine** — has
  `origin: None`. The Admiral's refusal is the grounding the order gives for
  `decision:solve-the-general-case`, so A could not bind the one spine the
  pre-ruling was written about.
- `.agent-work/implementer-315-native-g1/IMPLEMENTER_PLAN.json` — `origin: None`.
  That is the file type #559 is literally about.

My own `cmdr-a/spine.json` **does** carry `origin.work_id`, because
`init_work_area.py --spine` stamps it. So an implementer testing this feature on its
own spine would have seen it work while it failed on every spine the issue names —
a check that cannot fail. I only caught it because the candidate was honest enough
to name its own falsifier.

**The correction is one field and it is complete.** Derive from `origin.work_id`
when present, else the spine's top-level `work_id` — a required field on every
spine the engine drives. That covers **52/52, 100%**. `session_id_for(work_id)`
keeps its single definition and `open_work` keeps calling it, so a spine minted by
`open_work` still yields a byte-identical session; the fallback only adds coverage
for spines minted another way (`init_work_area.py`, `generate_spine.py`, a
hand-compiled plan). `R7` does not disappear — it narrows to "neither field
present", which the census says is currently never but is still the right
fail-closed posture.

## Recommendation

**Candidate A's `spine_bind`, with the session derived from `work_id` rather than
`origin.work_id`.** A named hybrid, not a menu: A's seam, A's containment root, A's
refusal set, one corrected field — where the correction is the difference between
solving the mission and refusing it.

Two smaller borrowings from the other two candidates, both earned:

- **`session_id_for(work_id)` extracted into `spine_lifecycle.py`** and shared with
  `open_work:357`. A and B proposed this **independently**, which is the evidence
  that the seam is real rather than hypothetical — "one adapter = a hypothetical
  seam; two = a real one."
- **C's narrow-root measurement is kept as the reach baseline.** It establishes that
  the crew case needs only two files of extra reach, which is the yardstick any
  future widening should be measured against.

Why A over B, in one line — **corrected after the critic, which caught this as
overstated**: both widen reach; **A makes the widening legible and adds `R8` (refuse a
bind onto a demonstrably-live identity); the guard is the same guard.**

The original wording said B was "guarded by the module's weakest guard" as though A
were not. Wrong. `spine_bind` **is** a rebind and sits behind the same
`_rebind_refusal`, which fails open in the same three documented directions including
"no lease" — and releasing a lease is one call. So the sequence I held against B
(release, bind another lane's spine, drive it) is reachable through `spine_bind` too.
What actually separates them is smaller, and worth stating precisely:

- A's capability lives behind a tool whose entire declared purpose is to bind, with
  its refusal set enumerated and its reach stated in its own description — versus an
  argument on a tool whose description promises creation.
- A adds `R8`, a genuinely new refusal: it declines a bind onto an identity another
  live process is holding. That closes the "two agents on one lease" failure
  `IDENTITY_TRADE.md` names rather than inheriting it.
- **After the amendment A's root is narrower than B's** — `683` and no cross-checkout
  reach, against any spine under `<root>/.agent-work/<work_id>` for any nameable
  `work_id`.

That is real security-usability value and a real reduction in reach. It is not the
stronger *guard* I originally claimed, and the human should weigh the corrected
version.

### The population objection, now answered with a count rather than an exception

The critic's sharpest simplicity finding: I called "every dispatch that can call
`spine_bind` could have been launched bound" the strongest objection on the table and
rebutted it by naming **one** exception (the Admiral), while this same document killed
candidate C's per-dispatch option with "a launcher that knows the work area's path can
set `SPINE_FILE` in the same breath." Fair hit on the argument, so I went and counted.
The population is **structural, not broken launchers**, and `scripts/run_crew.py` says
so itself:

- **`ExternalBackend` — the Agent-tool dispatch path — refuses `--spine` outright**
  (`:1673-1680`): "ExternalBackend spawns no process and builds no environment, so
  nothing binds the value into a child's SPINE_FILE/SPINE_SESSION." It then prints an
  **unconditional** warning (`:1709-1715`) that the crew's door is UNBOUND, above a
  comment calling out-of-band binding *"impossible by construction"*. The repo already
  knows the capability is missing and ships a permanent warning in place of it — and
  that comment's premise is now **stale**, because the previous lane made binding late.
- **Any orchestrator whose spine is created after its door.** The Admiral and this
  Commander both mint their spine with `init_work_area.py` mid-session. `SPINE_FILE`
  cannot name a file that does not exist yet, and "relaunch the door" means killing the
  session and losing the run. That is not a launcher fix.

So the population is not one caller shape. It is every Agent-tool crew dispatch plus
every orchestrator that mints its own spine, and for both, `SPINE_FILE`-at-launch is
unavailable rather than merely inconvenient.

## The isolation property — what replaces "one file per process"

Stated explicitly, as `decision:isolation-not-fencing` requires.

**Before:** one spine per process, decided at launch (`SPINE_FILE`) or at a
successful `spine_open` (mint).

**After:** one spine per process, decided at launch, at mint, **or by one confined
binding to a spine that already exists inside the door's own checkout's work-area
tree, whose session identity the spine itself dictates.** The count never rises above
one. Only the moment of decision moves — which is exactly what
`decision:bind-on-open-over-new-verb` already did once.

Said as a property in one line: **one checkout's work-area tree per process.**

**What an agent can reach that it could not before, said plainly and now with the
number beside it:** any readable spine-shaped JSON object carrying a `work_id`, under
`<the door's own checkout>/.agent-work/`. Measured in this tree: **683 files — 651
archived records, 32 live; 51 carry an `engine_session` marked active.** Before, an
unbound door could reach nothing at all, and a bound door only what it was launched
with or what it minted. **That is a real widening on a security boundary.** It is
named here rather than left for the tests to certify.

**What it deliberately does NOT reach — this is the amendment, and it is the reason
the "another checkout" bullet below is now true.** The earlier version of this design
used `_primary_checkout_for_lifecycle()` (`:797`), which resolves `--git-common-dir`
and therefore lands on the **primary** checkout, with `.worktrees/` nested inside it.
Measured, that root reaches **4205** spine-shaped files, **3505 of them inside other
lanes' checkouts**, 307 under an active lease. The root is now derived with
**`--show-toplevel`** — from the door's own script when unbound, from `SPINE.parent`
when bound — and a candidate whose own `--show-toplevel` differs from the door's is
**refused**. One flag is the whole difference between reaching one checkout and
reaching every worktree in the repository.

| root | reachable | cross-checkout | active lease |
|---|---|---|---|
| `--git-common-dir` (original design) | 4205 | 3505 | 307 |
| `--show-toplevel` + cross-checkout refusal (**adopted**) | **683** | **0** | 51 |

A further narrowing is available and I am deliberately **not** taking it unilaterally:
651 of the 683 sit under `archive/`, and an archived spine is a closed record that is
never a legitimate bind target, so excluding it would cut reach to **32**. I leave that
to the human and the reviewer, because it introduces a second notion of "what is
bindable" keyed on path rather than structure — and this document has already been
wrong once by adding reach without measuring it.

**What still holds it in** — five things, only one of which is new machinery:

1. The containment root confines **which** spines: `<own checkout>/.agent-work/`,
   through the same `_resolve_confined` predicate with a different `bound_dir` — the
   reuse `_spine_open` already demonstrates by passing `wt_root`.
2. **A cross-checkout refusal** confines it further: a candidate whose own
   `--show-toplevel` differs from the door's is rejected. This is the one genuinely
   new guard, and it exists because without it item 1 is not enough — `.worktrees/`
   nests inside the primary checkout, so a root derived the obvious way silently
   admits every sibling lane.
3. `work_id` confines **which identities**: identity is a function of the spine, never
   of a model-supplied string. `IDENTITY_TRADE.md` §3 Option B settled that a
   caller-supplied identity buys nothing, because "any string it can supply, it can
   supply its parent's."
4. `R8` refuses a bind onto an identity that is demonstrably live — the "two agents on
   one lease" failure `IDENTITY_TRADE.md` names, closed rather than inherited.
5. `_rebind_refusal` still forbids orphaning a lease this process holds — though see
   "Why A over B" for the honest limit of that guard: it fails open on "no lease", for
   `spine_bind` exactly as for `spine_open`.

**What an agent still cannot do:** drive two spines at once; **drive a spine in another
checkout, including a sibling worktree** (true because of item 2 — in the earlier
version of this design this bullet was flatly false, and a cold critic caught it 18
lines from the sentence that contradicted it); reach outside `.agent-work/`; name its
own identity; or point any of the nine pass-through tools anywhere —
`_identity_violation` is untouched and still an equality check against `SPINE` at call
time.

**Which side of the trade this takes:** the **env-binding** side, unchanged.
Identity stays process state — two globals, one binder, one equality check — and
does not become a per-call argument for any engine verb. The composition failure
`IDENTITY_TRADE.md` records is env-isolation composed with per-call **paths**; the
nine verbs that carry the engine's real power gain no path and no session argument.
After `spine_bind` returns, this door is indistinguishable from a door launched
bound to that spine.

## Two obligations the recommendation inherits, neither of which may be dodged

1. **`tests/test_mcp_identity.py:817` will fail, by design.** It walks all of
   `TOOLS` and flags any property whose name contains `spine`, `session`, `engine`,
   `checklist_file` or `identity`. `spine_bind.spine_file` is literally that pin's
   own positive control. This is the pin working, and its failure message says what
   to do: a **tool-scoped** exemption plus an `IDENTITY_TRADE.md` amendment in the
   same change, "so that cannot happen silently." **The cheaper dodge — naming the
   argument `work_file` or `plan_path` so the pin passes — must be refused.** That
   is precisely the spelling game `_identity_violation`'s docstring records losing
   six times, turned by the author against his own test.
2. **`tests/test_mcp_lifecycle.py:135`'s `ALLOWED` set grows by one name.** That is
   *widening an allow-list*, not loosening a ban: the pin forbids
   `call_lifecycle_tool` from producing content any way other than delegating to a
   named dispatch function, and a third named dispatch function preserves that
   property exactly. Its own failure text endorses the move — "Route new lifecycle
   logic through its own top-level dispatch function." The positive control at
   `:156` stays untouched and must still fail on a mutate-then-return; if it goes
   green, something was weakened. The previous lane's record contains a
   **superseded** passage where it first proposed to "extend a pin" and the cold
   critic corrected it as the dangerous direction — so the distinction is drawn here
   deliberately, not glossed.

## What would have to be true for this recommendation to be wrong

- **If every launcher path can be fixed**, `spine_bind` has no population. A's own
  §6 makes this argument against itself and it is the strongest objection on the
  table: every dispatch that *can* call `spine_bind` is one that could have been
  launched bound, since `run_crew --spine` already puts that exact string in the
  child's environment as a matched pair. Then the right answer is a launcher fix
  plus a better refusal message — zero new tools. **What defeats this objection is
  the Admiral's case**, which is not a dispatch at all: a top-tier orchestrator in
  its own process, with no launcher above it to fix, and a spine that already
  exists. I reproduced that refusal in my own process at step one of this run.
- **If `IDENTITY_TRADE.md` §2's confinement property is not amendable** — if the
  human reads "the door cannot be pointed at another run's spine" as settled rather
  than as a recorded trade — this candidate is dead as written, whatever its
  internals look like. This is the one question I most want ruled.
- **If two processes binding one spine is common rather than exceptional**, `R8`
  becomes the normal outcome and the tool refuses more than it binds. Identity would
  then have to be per-**assignment** rather than per-spine, which cannot be derived
  from a spine at all.
- **If the real complaint is only "`spine_status` fails on an unbound door"**, the
  seam belongs at first-call resolution and B's rejected sub-shape deserves another
  look despite its ~10 red tests.

## Panel-vs-single record

Panel of 3, because the decision touches architecture and a recorded security
property. Surfaced here so the human can overturn the scaling call. In hindsight the
panel earned its cost twice over: C's negative removed the issue's own filed
recommendation from contention with numbers rather than argument, and B's
self-objection is what made A's boundary advantage legible.
