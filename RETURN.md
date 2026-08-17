# RETURN — `cmdr-567-a` (#559 anchor · bind-own-spine gap · #613 atomicity half)

Worktree `/home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity`,
branch `feat/567-a-spine-identity`, base `600de020`. **Not merged.**

**Read §3 first.** It is the artifact the human converges on, and
`decision:convergence-is-human-only` means the design pick below is *not* settled by my
having recommended it.

## 1. Verdict

**Delivered, with one design question the human must rule on and one honest weakness.**

The lane's defect was **one missing verb, not a missing mechanism.** The previous lane had
already made the door safely rebindable — `_bind_process_to` as the single named identity
mutator, all four import-time derivations late-bound, `_unbound_refusal` deliberately
uncached, and a module-wide AST pin over the assignment set. Its only caller was
`spine_open`, which **mints**. Nothing bound a door to a spine that already exists.

Shipped:

- **`spine_bind(spine_file)`** — a door tool that binds to an existing spine, confined to
  `<the door's own checkout>/.agent-work/` with a cross-checkout refusal. Property:
  **one checkout's work-area tree per process.**
- **`checklist_engine.save()` is atomic** — unique `mkstemp` sibling, mode preserved,
  `fsync` before the rename, temp unlinked in a `finally`. #613's atomicity half, and only
  that half.
- 1,432 lines of new tests across three new modules; full suite green.

**The independent reviewer returned `BLOCK`, and it was right to.** It passed every
condition the handoff named as blocking — its own root mutation went RED both spellings
including the non-vacuity control, all four pins held with planted-regression controls, a
spine with `origin: None` binds, full suite 3263 green — and then blocked on two defects it
found by *attacking*:

- **The isolation property was false as written.** The cross-checkout guard asked git about
  `candidate.parent` **unresolved**, while `_resolve_confined` resolves. A symlink inside
  the door's own `.agent-work/` pointing at a spine in another checkout satisfies **both**
  checks. The reviewer bound a linked worktree's spine and a separate repository's spine
  that way. The bug is not in the root the critic made me narrow, nor in the containment
  predicate — it is in the **mismatch between two guards that resolve paths differently**,
  and it is my design's second guard defeating its own first. One-token fix; no live breach
  (zero such nested checkouts exist today, and every escape with a real file behind it is
  correctly refused), but the *stated property* was untrue and stating an attackable
  property was the whole point of `decision:isolation-not-fencing`.
- **A NUL byte in `spine_file` killed the door process** — unhandled `ValueError`,
  `main()` catches only `KeyError` — on the one tool reachable while nothing is bound.

**A second reviewer, run independently, reached `BLOCK` on the same two findings by a
different route** — 13 of 13 attacks correct in a real linked-worktree topology, all 40
`--file` injections across the nine pass-throughs refused, ten mutations on a mirror all RED,
and its own reproduction of the root mutation matching mine exactly ("I agree the narrowed
root is genuinely tested"). Genuine replication rather than corroboration. It sharpened both
blockers: **B1 is worse than first described** — the door **wrote a live lease into another
checkout's spine**, not merely bound it — and **B2 is narrower** (the NUL byte kills the door
only when already bound).

It also found a third gap that changes what this lane may *claim*, and I have taken it:
**a hardlink defeats any path-based check.** A symlink has a target, so resolution reveals the
real location; a hardlink is a second *name* for the same inode, so `resolve()` returns what
you gave it and git correctly answers "our checkout." No amount of resolving fixes that. So
the property this lane ships is stated with its limit attached:

> **One checkout's work-area tree per process, enforced by path.** An actor who can already
> create a hardlink inside the door's own `.agent-work/` can present a foreign checkout's
> spine as a local one.

Less satisfying, and true. Having been caught once claiming a property the code did not have,
overstating it a second time would be the worse error.

Both blockers are in rework as of this return. **See §9 for the current gate state; do not
read this as merge-ready until that section says so.**

Four things I would want read even if nothing else is:

1. **I ran the winning candidate's own falsifier and it failed.** Candidate A derived the
   session from `origin.work_id`; only **4 of 52** live spines carry it, and the two that
   do not include *the Admiral's own spine* and *`IMPLEMENTER_PLAN.json`* — the exact cases
   the mission names. My own spine does carry it, so a self-test would have passed while
   the mission failed. Corrected to fall back to the top-level `work_id`: **52/52**.
2. **A cold critic inverted my central argument, and it was right.** I disqualified
   candidate C on a measured 683-target reach and crowned candidate A on an *unmeasured*
   one that was actually **4205, of which 3505 were other lanes' checkouts** — because
   `_primary_checkout_for_lifecycle()` resolves `--git-common-dir`. Narrowed to **683,
   cross-checkout 0**. My isolation section had also asserted, 18 lines apart, both that a
   sibling worktree's spine was reachable and that another checkout was not.
3. **My fix would have shipped untested, and the tests would have been green.** The
   implementing crew mutation-tested its own work: swapping the wide root back in left the
   **whole suite passing**, because every fixture built a *primary* checkout — where
   `--show-toplevel` and `--git-common-dir` return the same path. They diverge only inside
   a linked worktree. A missing *topology*, not a missing test. Fixed with a
   linked-worktree fixture plus a non-vacuity control; all three root mutations now red.
4. **My gate plan could not detect its own success.** All four of its command
   postconditions passed at base with zero code written. Amended through the engine, and I
   verified the new ones fail at base.

**The honest weakness:** net line count goes **up** (13,129 insertions / 112 deletions).
What this lane deletes is one refusal clause and *the reason the epic's 15 CLI-fallback
clauses and 11 `<engine>` tokens cannot be deleted*. Against a `settled/human`
`decision:net-deletion`, the human may reasonably judge that insufficient — see §7.

**The question I most want ruled** (§3): is `IDENTITY_TRADE.md` §2's confinement property
**amendable**? If "the door cannot be pointed at another run's spine" is settled rather than
a recorded trade, this design is dead as written whatever its internals look like.

## 2. Isolation evidence

```
$ cd /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity && \
  py /home/tommy/.claude/skills/constellation-admiral/scripts/verify_worktree_isolation.py \
     --here /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity
worktree OK: in /home/tommy/projects/constellation-skills/.worktrees/567-a-spine-identity
EXIT=0
```

**One correction to the order's instructions, and it matters because it killed my
predecessor.** The order prescribes `cd` into the worktree and *then* run the check as
a separate step, and explicitly forbids `git -C <path>` as self-disarming. Both
correct. But **the shell's working directory does not persist between tool calls in
this harness**, so a bare `cd` in one call followed by the check in the next verifies
the session's starting directory. Run that way it reported:

```
wrong worktree: you are in /home/tommy/projects/constellation-skills, not your
assigned worktree ... — run every git operation inside <worktree>
EXIT=1
```

which reads as a failed isolation gate when isolation was in fact fine. The working
form is a single compound call, `cd <abs> && py ... --here <abs>`, which is what
produced the exit-0 output above. The previous agent on this lane ran 47 minutes,
wrote zero bytes, and its dying words were "the bash cwd resets between calls" — so
an order prescribing a two-call bootstrap in a harness with no cwd persistence is a
documented cause of a lost lane. Filed as a triage candidate.

## 3. The design-it-twice comparison

Full artifact: `.agent-work/epic-567-door/cmdr-a/DESIGN_CONVERGENCE.md`. Read that
for the argument; this is the summary.

**`decision:convergence-is-human-only` — I generated and compared; the human picks.
Nothing below is ratified by my having recommended it.**

Panel of **3** (not 2), because the decision touches architecture and a recorded
security property; doctrine says "when in doubt, panel." Run as **fresh agents, not
forks** — lane G's incident this wave was its own context-inheriting fork driving the
Commander's `spine.json` under the same lease id, so each agent was told explicitly
that it has no spine and must not run the engine. All three complied.

Untaken roads, named rather than skipped silently: **`max-flexibility`** (multi-spine
access from one door) violates `decision:one-spine-per-process-stands`, a `settled`
decision not mine to unsettle; **`ports-and-adapters`** (a pluggable spine-locator
port) would be one adapter, and one adapter is a hypothetical seam.

| | **A — `minimal-interface`** | **B — `no-new-tool`** | **C — `per-call-identity`** |
|---|---|---|---|
| Shape | one new tool `spine_bind(spine_file)` | `spine_open` becomes adopt-or-mint on `work_id` | calls may name their own spine, confined to a bound **root** |
| **Depth** | good; hides four hard questions, leaks one (caller needs the path) | **wins**; whole matrix behind one library function, no new tool | weakest; +9 tool args, +1 env var, pushes containment onto config |
| **Locality** | **wins**; one dispatch fn, one schema entry, one route, no caller changes | mixed by its own admission; fans out into the skills corpus | fans out across `_identity_violation`, the one function that most rewards being left alone |
| **Seam placement** | loses on the caller it inconveniences; **wins on the boundary** | wins on the tests (no pin moves); **loses on the boundary** | seam is the guard itself — reopening a function whose docstring records six defeats |
| **Testability** | **wins**; 9 refusals each independently reachable, harness exists | strong; library fn testable with no door | fine, but its central property is a claim about what is on disk at call time |
| Reach added *(one predicate — see the note under §3)* | **683**, cross-checkout **0** *(amended down from 4205/3505)* | any spine under `<root>/.agent-work/<work_id>` for any nameable `work_id` | **683**, 51 leased, **674** legal `--from-child` targets |
| Deletes | 1 constant, 1 documented recovery path, 1 possible duplicate definition | some refusal text | **nothing** |
| Verdict | **winner, with one correction** | strong runner-up, **self-refuted** | **well-argued negative** |

**C is a measured negative on its own constraint** — which the brief said is a
complete deliverable. Its case is arithmetic: its only viable root exposes 683
readable spines, 51 of them under an active lease and the rest writable since #609, and 674 files
carrying a `consolidation` key and thus legal `--from-child` targets. Its two *safe*
roots either cannot serve an unbound door at all (`SPINE.parent` is derived from a
bound file) or buy nothing a launcher could not buy by setting `SPINE_FILE` in the
same breath. Asked what it deletes it answered: nothing, except the security
property. **This retires #559's own filed recommendation with numbers rather than
with an argument** — the single most useful thing the panel bought.

**B self-refuted, in its own words:**

> "I rejected the *tighter* design because it broke a test suite, and shipped the
> *looser* one because it broke none. A reviewer is entitled to read that as
> optimizing for green CI over the security property the CI exists to measure."

B's rejected sub-shape is still a keeper as a *result*: it measured that resolving a
binding from ambient worktree state turns ~10 tests red, including
`test_empty_spine_file_refuses_rather_than_binding_the_cwd`
(`tests/test_mcp_door_unbound.py:223`) — independent confirmation that ambient
inference is the fail-open defect the previous lane deliberately removed.

### Recommendation — a named hybrid, not a menu

**Candidate A's `spine_bind`, with the session derived from `work_id` rather than
`origin.work_id`, and with a containment root narrowed after the critic.** A's seam, A's
nine refusals, and two corrections — one to the session field, one to the root.

**The root is `<the door's own checkout>/.agent-work/`, derived with
`git rev-parse --show-toplevel`, plus a refusal for any candidate whose own
`--show-toplevel` differs from the door's.** It is deliberately NOT
`_primary_checkout_for_lifecycle()`, which resolves `--git-common-dir` and therefore
jumps to the primary checkout — with `.worktrees/` nested inside it. That distinction is
the gate's whole security content: `--git-common-dir` is *correct* for `spine_open`,
which must create a worktree and so must nest it under the primary checkout, and *wrong*
for `spine_bind`, which must not reach one. Two questions, two roots, both named.

Plus one borrowing that earned itself: **`session_id_for(work_id)` extracted into
`spine_lifecycle.py`** and shared with `open_work:357`. A and B proposed this
**independently**, which is the deep-module rule's own evidence test — "one adapter =
a hypothetical seam; two = a real one." I take it on their agreement, not my
judgement.

Why A over B in one line — **corrected, because my first version overstated it and the
critic caught that**: both widen reach; **A makes the widening legible, adds `R8` (refuse
a bind onto a demonstrably-live identity), and ends up with the narrower root; the guard
is the same guard.** `spine_bind` *is* a rebind and sits behind the same
`_rebind_refusal`, which fails open on "no lease" exactly as it does for `spine_open` —
so the sequence I held against B (release, bind another lane's spine, drive it) was
reachable through A too until the root was narrowed. What separates them now is that A's
capability is declared rather than smuggled onto a tool that promises creation, and A's
reach is 683-with-no-cross-checkout against B's any-spine-for-any-nameable-`work_id`.

### The correction, and why it decided the run

Candidate A named its own falsifier: "if `origin.work_id` is commonly absent from the
spines that need binding, R7 refuses in the main case and the tool is theatre." **I
ran it.** Live spine-shaped JSON under `.agent-work/` and `.worktrees/*/.agent-work/`,
excluding `archive/` and `templates/`:

| | count |
|---|---|
| live spine-shaped files | **52** |
| carrying `origin.work_id` | **4** |
| no origin, but top-level `work_id` | **48** |
| **neither** | **0** |

A as written refuses **92%** of them, including:

- `.agent-work/epic-567-door/spine.json` — **the Admiral's own live spine**, `origin: None`. That refusal is the grounding the order gives for `decision:solve-the-general-case`, so A could not bind the one spine the pre-ruling was written about.
- `.agent-work/implementer-315-native-g1/IMPLEMENTER_PLAN.json` — `origin: None`. The file type #559 is literally about.

**My own spine *does* carry `origin.work_id`**, because `init_work_area.py --spine`
stamps it. So an implementer testing this feature on its own spine would have watched
it work while it failed on every spine the issue names — a check that cannot fail. I
caught it only because the candidate was honest enough to name its own falsifier.

**The repair is one field and it is complete:** derive from `origin.work_id` when
present, else the spine's top-level `work_id` — a required field on every spine the
engine drives. **52/52, 100%.** `session_id_for` keeps its single definition and
`open_work` keeps calling it, so a spine minted by `open_work` still yields a
byte-identical session. R7 does not disappear; it narrows to "neither field present",
which the census says is currently never but remains the right fail-closed posture.

### What would have to be true for the recommendation to be wrong

- **If every launcher path can be fixed**, `spine_bind` has no population — A's own
  strongest self-objection: every dispatch that can call it could have been launched
  bound, since `run_crew --spine` already puts that string in the child's environment
  as a matched pair. **What defeats it is the Admiral's case**, which is not a dispatch
  at all: a top-tier orchestrator in its own process, no launcher above it to fix, and
  a spine that already exists. I reproduced that refusal in my own process.
- **If `IDENTITY_TRADE.md` §2's confinement property is not amendable** — if the human
  reads "the door cannot be pointed at another run's spine" as settled rather than as a
  recorded trade — the candidate is dead as written. **This is the one question I most
  want ruled.**
- **If two processes binding one spine is common** rather than exceptional, R8 becomes
  the normal outcome; identity would have to be per-*assignment*, which cannot be
  derived from a spine at all.
- **If the real complaint is only "`spine_status` fails on an unbound door"**, the seam
  belongs at first-call resolution and B's rejected sub-shape deserves another look.

## 4. The isolation property

**Before:** one spine per process, decided at launch (`SPINE_FILE`) or at a successful
`spine_open` (mint).

**After:** one spine per process, decided at launch, at mint, **or by one confined
binding to a spine that already exists inside the door's own checkout's work-area tree,
whose session identity the spine itself dictates.** The count never rises above one. Only
the moment of decision moves — exactly what `decision:bind-on-open-over-new-verb` already
did once. As a property in one line: **one checkout's work-area tree per process.**

**What an agent can reach that it could not before, with the number beside it:** any
readable spine-shaped JSON object carrying a `work_id`, under
`<the door's own checkout>/.agent-work/`. **683 files — 651 archived records, 32 live; 51
carry an `engine_session` marked active.**

**What it deliberately does NOT reach, and this is the amendment the critic forced.** My
first design used `_primary_checkout_for_lifecycle()` (`--git-common-dir`), which lands on
the primary checkout with `.worktrees/` nested inside: **4205 reachable, 3505 of them in
other lanes' checkouts, 307 under an active lease.** I had killed candidate C for a
683-file root and crowned a 4205-file one without printing the number — a boundary
argument decided on an axis measured for only one side. Narrowed to `--show-toplevel` plus
a cross-checkout refusal:

| root | reachable | cross-checkout | active lease |
|---|---|---|---|
| `--git-common-dir` (my original) | 4205 | 3505 | 307 |
| `--show-toplevel` + cross-checkout refusal (**shipped**) | **683** | **0** | 51 |

The implementing crew re-measured the same comparison under its own predicate and got
**6102 vs 1014**. The absolute numbers differ because the predicates differ (it counted
readable JSON under any `.agent-work/` with a derivable `work_id`; I required an `items`
list and a `tasks` dict). **The ratio, the direction and the conclusion agree.** Both are
reported with their predicates rather than picking the flattering one — counts are only
comparable under one stated predicate, which is a lesson this run learned the hard way.

A further narrowing is available and I did **not** take it unilaterally: 651 of the 683
are under `archive/` — closed records, never legitimate bind targets — so excluding them
would cut reach to **32**. Left to the human and the reviewer, because it introduces a
second notion of "what is bindable" keyed on path rather than structure, and this design
has already been wrong once by adding reach without measuring it. Before, an unbound door could reach nothing at all, and
a bound door only what it was launched with or what it minted. **That is a real
widening on a security boundary,** stated here rather than left for the tests to
certify, per `decision:isolation-not-fencing`.

**What still holds it in** — four things, none of them new machinery: the containment
root confines *which* spines; `work_id` confines *which identities*, so identity is a
function of the spine and never of a model-supplied string; R8 refuses a bind onto an
identity that is demonstrably live, closing the "two agents on one lease" failure
`IDENTITY_TRADE.md` names rather than inheriting it; and `_rebind_refusal` still
forbids orphaning a lease this process holds.

**What an agent still cannot do:** drive two spines at once; **drive a spine in another
checkout, including a sibling worktree**; reach outside `.agent-work/`; name its own
identity; or point any of the nine pass-through tools anywhere — `_identity_violation` is
untouched and still an equality check against `SPINE` at call time.

> The second bullet is true **because of** the narrowed root and the cross-checkout
> refusal. In my first draft it was flatly **false**, and it sat 18 lines below a sentence
> that said a sibling worktree's live spine *was* reachable. A linked worktree is another
> checkout. The critic found the contradiction, and it mattered more than a wording slip:
> that bullet is the line a human skimming for the security summary actually reads, and
> the incident grounding this whole wave — lane G's crew and fork writing one spine under
> one identity — is exactly cross-agent access to one live spine.
>
> The implementing crew then found a hole in my *fix*: path-prefix containment against
> `<root>/.agent-work/` would still admit **a whole separate checkout nested inside that
> directory**, which `.worktrees/` proves is not hypothetical here. So the cross-checkout
> refusal is not redundancy — it closes a gap the confinement check structurally cannot
> see. My handoff asked for the right thing for a weaker reason than the real one.

**Which side of the trade:** the **env-binding** side, unchanged. The composition
failure `IDENTITY_TRADE.md` records is env-isolation composed with per-call *paths*;
the nine verbs carrying the engine's real power gain no path and no session argument.
After `spine_bind` returns, this door is indistinguishable from a door launched bound
to that spine.

### How much of the door is closed today — proven two ways

Measured: `spine_status` and `spine_lease` both refuse in my own process. Read from
code rather than poking mutating tools at live state: the gate in `main()` (`:1723`) is
**uniform** — one `_unbound_refusal()` applied to every tool name, before dispatch and
before any argument check, exempting only `BINDS_WITHOUT_A_BOUND_SPINE = {"spine_open"}`.
So **10 of 11 tools refuse and the 1 reachable tool mints.** Its own comment states the
intent the fix extends: "`spine_open` is exempt because it is the way OUT of this
state." There is a way out for work that does not exist yet, and none for work that does.

## 5. Self-hosting proof

**Baseline, taken BEFORE any engine edit** (at `3e4b0e20`), because both required
proofs are comparisons and are worth nothing without a "before":

```
$ py scripts/checklist_engine.py --file .agent-work/epic-567-door/cmdr-a/spine.json current
worktree-engine current on live spine -> exit 0

$ cp .../cmdr-a/spine.json <scratch>/spine-copy.json
$ py scripts/checklist_engine.py --file <scratch>/spine-copy.json advance plan \
      --session-id cmdr-567-a --mechanical
REFUSED: plan: postconditions unmet ['c1','c2','c3','c4','c5','c6'] Recovery: ...
advance-on-copy -> exit 1

$ git status --short .agent-work/epic-567-door/cmdr-a/spine.json
(no output — live spine unmodified)
```

The mutating verb refused **coherently** — a refusal naming the six unmet
postconditions with a recovery line, not a traceback — which is the behaviour the
ruling asks me to preserve. And `git status` proves the copy test did not touch the
live spine, which is the part of the ruling most easily violated by accident.

**After the edit** — and note the check the launch order specified is not sufficient on
its own, which a cold critic caught (its S3): `current` is **read-only and never calls
`save()`**, so its exit code is identical in the healthy and the defective world. It is
an import smoke test, not a proof of an atomicity change. Its relative paths also made
its verdict a function of the harness cwd — run verbatim from the primary checkout it
raised `FileNotFoundError`. Both fixed, and the missing proof added.

**Proof 1 — read-only `current` on the LIVE spine, edited engine, absolute paths:**
```
$ py <WT>/scripts/checklist_engine.py --file <WT>/.agent-work/epic-567-door/cmdr-a/spine.json current
exit=0
LEASE active: cmdr-567-a (by constellation-commander-delegated, heartbeat 2026-08-17T06:55:51Z)
```
Matches the pre-edit baseline, so the edit did not break the read path.

**Proof 2 — a MUTATING verb against a COPY, never a live spine.** `advance` on the copy
refused coherently (exit 1, six unmet postconditions named, recovery line — not a
traceback), the same shape as baseline. But a refusal returns *before* writing, so it
does not exercise `save()`. So I ran a verb that really writes, and measured the
discriminating thing rather than the exit code:

```
$ B=$(stat -c %i spine-copy-after.json)          # inode before: 6193176
$ py <WT>/scripts/checklist_engine.py --file <SCRATCH>/spine-copy-after.json \
      heartbeat --session-id cmdr-567-a
heartbeat cmdr-567-a @ 2026-08-17T07:01:39Z
exit=0
$ A=$(stat -c %i spine-copy-after.json)          # inode after:  6193175  -> CHANGED
```

**The inode changed.** An in-place `write_bytes` keeps the inode; an atomic rename
replaces it. So the new write path demonstrably engaged, under the edited engine, on a
real spine document, driven by a real engine verb. The copy still parses and no `.tmp`
sibling survived.

**Proof 3 — the live spine was untouched throughout.** `git status --short` on
`.agent-work/epic-567-door/cmdr-a/spine.json` is empty after all three proofs. This is
the half of the ruling most easily violated by accident, so the empty status line is the
evidence rather than my assurance.

**And the red-proof, re-run by me rather than taken from the crew.** Reverting `save()`
to the old bare `write_bytes` in the **worktree** copy only:

```
5 failed, 6 passed
FAILED ...::test_save_never_opens_target_for_writing
FAILED ...::test_target_inode_is_replaced_exactly_once
FAILED ...::test_save_writes_a_temp_sibling_in_the_same_directory
FAILED ...::test_no_temp_sibling_after_a_failed_replace
FAILED ...::test_concurrent_reader_never_observes_a_partial_document
```
Restored; `git diff --stat` confirms the restore was exact; 11/11 green again. The 6 that
pass in both worlds are the line-ending-preservation tests, which *should* — that is the
correct shape for a red-proof, not a weakness.

## 6. Fresh-process validation

Done by **stripping the environment**, not merely spawning a subprocess — because the
doctrine's specific warning is against a fixture that hand-injects the value it is trying
to prove the harness delivers:

```
$ env -i PATH=$PATH HOME=$HOME PYTHONIOENCODING=utf-8 \
    py <WT>/scripts/checklist_engine.py --file <WT>/.agent-work/.../spine.json current
exit=0

$ env -i PATH=$PATH HOME=$HOME py -c "…"
SPINE_* in env: none
CLAUDE_PROJECT_DIR: (unset)
```

Both identity variables and `CLAUDE_PROJECT_DIR` are provably **absent**, every path is
absolute, and the worktree engine still drives the live spine. Nothing was inherited from
my session, so this is not my session's behaviour reported as the world's.

**What it did NOT validate, stated so the claim is not read as broader than it is:** hook
behaviour. I touched no hooks, and `CLAUDE_PROJECT_DIR` resolving once at session launch
(#269) means I could not have validated hooks from inside this session regardless.

## 7. What was deleted

**The relaunch-your-own-server advice is gone from both refusal paths.** `_HOW_TO_BIND`
and `_HOW_TO_REBIND` (`scripts/mcp_spine_server.py:421-428`) used to end:

> "…or relaunch this door with SPINE_FILE set to an existing spine file"

That clause existed **only** because there was no in-band way to bind an existing spine.
It is now:

> "Call `spine_bind` with the path to a spine that already exists, or `spine_open` to mint
> a spine and bind this process to it."

The deletion that matters is not the words but the **recovery path they described**:
telling a model to kill and relaunch the MCP server it is running inside — advice, as the
new docstring puts it, "a model running INSIDE that door usually cannot follow." The way
out of an unbound door is now a call. Both constants were deliberately **kept** rather than
collapsed into one, because `_unbound_refusal`'s docstring argues the bind/rebind split "is
not cosmetic": an unbound door has no path to name, so a message promising to name one
invites a fabricated path.

Also deleted, in the sense `decision:net-deletion` is actually protecting: **the
possibility of a second definition of a spine's session identity.**
`constellation/<work_id>` was an inline f-string inside `open_work`; it is now
`spine_lifecycle.session_id_for()` with two callers. Not fewer lines — fewer places for
truth to diverge. Candidates A and B proposed this independently, which is the evidence the
seam is real rather than hypothetical.

### The honest accounting, because the pre-ruling deserves a straight answer

**Net line count goes UP: 13,129 insertions against 112 deletions.** Most of that is tests
(`tests/test_mcp_spine_bind.py` alone is 1,059 lines) and this lane's own records. Nobody
should read this lane as net-negative on mechanism.

**What it actually deletes is the reason the deletions cannot happen yet.** Epic #567's
deliverable is 15 `CLI fallback` clauses across 11 files and 11 `<engine>` tokens across 7
files — both counts re-measured at `600de020` and matching the order's table exactly. Every
one of them is currently load-bearing, because for an agent whose door is unbound the CLI is
**the only path**: 10 of the door's 11 tools refuse, and the one that answers mints. You
cannot delete the only path. Wave 2 does the deleting; this lane removes the blocker.

**The critic called this a double standard and it was right to.** I convicted candidate C on
"what do you delete — nothing" while never printing what candidate A deletes, and
`decision:net-deletion` is graded `settled/human`, cited in nine gate anchor blocks and
delivered by none of them. So: stated plainly rather than dressed up, and the human may
reasonably judge one deleted clause insufficient for a `settled/human` ruling. That
judgement is theirs, not mine to declare satisfied.

## 8. Touched paths

**`scripts/hooks/*` is NOT touched.** Verified by command —
`git diff --name-only 600de020..HEAD -- scripts/hooks/` is empty. Stated first because the
Admiral needs it for merge sequencing: concurrent lanes editing hook code can break every
live session, since all sessions execute the main checkout's hooks.

**Source (5 files):**

| path | what | fenced to me? |
|---|---|---|
| `scripts/mcp_spine_server.py` | `+539` — `spine_bind`, `_spine_bind`, `_own_checkout_for_binding`, `_unusable_spine_reason`, the refusal set, `BINDS_WITHOUT_A_BOUND_SPINE` | **yes**, sole writer |
| `scripts/checklist_engine.py` | `+51` — `save()` atomicity only | **yes**, sole writer |
| `scripts/spine_lifecycle.py` | `+27` — `session_id_for()` extracted; `open_work` calls it | no |
| `scripts/run_crew.py` | `+9` — one `CREW_ALLOWED_TOOLS` entry | **no — see the collision flag below** |
| `map/INDEX.md` | `19` lines — regenerated; my code made it stale | no |

**Tests (8 files):** `tests/test_mcp_spine_bind.py` (new, 1059), 
`tests/test_checklist_engine_atomic_save.py` (new, 295), `tests/test_spine_session_id.py`
(new, 78), `tests/test_mcp_identity.py`, `tests/test_mcp_lifecycle.py`,
`tests/test_mcp_door_unbound.py`, `tests/test_mcp_spine_server.py`,
`tests/test_crew_launcher.py`.

**Records:** `notes-a.md`, `RETURN.md`, `.agent-work/epic-567-door/cmdr-a/**`,
`.agent-work/567-a/triage-candidates/**`, and the `IDENTITY_TRADE.md` amendment under
`.agent-work/archive/`.

### Merge-collision flag for the Admiral

**`scripts/run_crew.py` is not in my File Ownership, and lane `567-b-external-backend`
almost certainly owns it.** I edited it anyway, and I want that visible rather than
discovered:

- **The change:** one entry appended to the `CREW_ALLOWED_TOOLS` tuple at
  `scripts/run_crew.py:629` — `"mcp__spine__spine_bind"` — plus its comment.
- **Why it was not optional:** that tuple is passed straight to `--allowedTools` on every
  crew dispatch. Without the entry a dispatched crew is **silently denied** the new tool,
  and an `ExternalBackend` crew's door is unbound *by construction* — so `spine_bind` is
  its only route to its own plan file. Omitting it ships the feature inert for the exact
  population #559 is about. The drift-guard test caught it; the comment directly above the
  tuple describes this same failure from the last time it happened.
- **Resolving a conflict:** trivial in either direction, as long as the final tuple contains
  `"mcp__spine__spine_bind"`. `tests/test_crew_launcher.py`'s count control (11 → 12) must
  move with it.

Also disclosed: the implementing crew edited `tests/test_mcp_spine_server.py`, which its
handoff did not list. It declared the edit as unavoidable and narrowing. I accept it and
flag it rather than let it pass unmentioned.

## 10. Triage candidates

Written under `.agent-work/567-a/triage-candidates/`, **not filed as issues**
(`decision:no-issue-filing`):

1. `write-provenance-on-spine-journal.md` — **the highest-value one.** Lane G's
   incident is the grounding: its own crew plus its own fork drove one spine under one
   lease id, and the lane could not distinguish its own writes from an attacker's.
   Neither the lease (same session id, so correctly authorized) nor my atomicity fix
   (both writers well-formed) addresses it. Nothing records *who wrote what*. Also
   notes that `docs/agents/GLOSSARY.md` overstates what a lease buys — "so a second
   agent cannot drive the same spine" does not hold under a shared session id.
2. `verify-frame-refuses-every-anchor-when-degraded.md` — **measured, not argued.**
   Under a degraded map, `verify-frame` refuses every anchor-id token unconditionally,
   so the mandated `MISSION_FRAME` template (which *requires* graded `decision:`
   anchors) cannot pass. Proven by experiment: a five-line frame with zero anchors and
   one substitute citation returns `FRAME-OK` exit 0, where my 15-anchor frame returns
   `FRAME-REFUSED` exit 10. **The gate prefers the emptier artifact.**
3. `launch-order-bootstrap-defects.md` — three defects that each block step one: the
   order's engine path does not exist (the delegated skill ships no `scripts/`); the
   assigned notes filename was already a tracked file; the two-call isolation-check
   sequence is unusable in this harness.
4. `613-lost-update-half-remains.md` — do not close #613 on this merge. Atomicity
   removes the *noisy* symptom of a bug whose *quiet* symptom it does not touch.
5. `map-ids-jsonl-empty-repo-wide.md` — `map/ids.jsonl` is tracked and 0 bytes, so
   every run in the repo orients DEGRADED. **The more important find, measured:**
   `tests/test_code_map.py` is **148 tests green** against that empty map. The suite
   guarding map freshness is vacuous, which is why the data defect survived a full epic
   after being reported twice.
6. `engine-init-imperative-asserts-a-false-binding.md` — the commander spine
   template's very first imperative tells every Commander "this is your own spine (the
   one this process's door is bound to)". It is false for every dispatched Commander,
   and it teaches the agent something false at the moment it can least doubt it.

## 11. Workflow feedback

**What worked.**

- **Design-it-twice earned its cost twice over,** and both payoffs came from candidate
  *honesty* rather than candidate cleverness. C's self-negation retired the issue's own
  filed recommendation with numbers. A's named falsifier is what exposed the
  `origin.work_id` defect — a single design pass would have shipped a feature that
  worked on the author's own spine and refused the Admiral's.
- **Fresh agents instead of forks.** Given lane G lost its mission to a fork that
  believed it was the Commander, the "you have no spine, do not run the engine"
  prohibition cost one paragraph per dispatch and I would repeat it every time.
- **Write-as-you-go.** `notes-a.md` carries nine findings recorded when found. My
  predecessor ran 47 minutes and wrote zero bytes; the discipline is the difference.
- **The engine's rails are genuinely good.** The `init` step's RAIL banner, the refusal
  recovery lines, and the check text that honestly states its own measured sensitivity
  (0/4) and specificity (0/1) are unusually well built.

**What did not.**

- **Three of my first four bootstrap steps were unrunnable as written** (engine path
  absent, notes filename occupied, cwd non-persistence). All three are cheap to check
  and each blocks step one, where a commander has the least context to diagnose it.
- **The `plan` step's `c6` gate punishes the better artifact,** measured above. I took
  the recorded waiver the imperative sanctions, but an author who does not notice
  learns — correctly, from the gate's feedback — to stop writing constraint anchors.
- **`docs/agents/engine-config.json` does not exist** though the `context` imperative
  names it. I substituted `docs/CHECKLIST_ENGINE_DESIGN.md` and recorded the
  substitution, as the imperative allows.
- **The cold plan critic was the slowest step of the run** by a wide margin, and it is
  sequenced so nothing can proceed past it. Worth knowing when budgeting a lane.
