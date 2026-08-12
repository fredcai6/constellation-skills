# Launch Order: `commander-308 — issue #308, first collated consolidation AND retire the playbook`

You start cold. Everything below is pasted, not pointed at.

**This issue is HITL.** You assemble evidence and candidates; **Tommy makes the calls.** Two-bin routing rulings and pathway verdicts are his, always. Do not decide them, do not pre-empt them, and do not present a single option where a real choice exists.

## Mission

Two halves, and the second is why this issue grew.

**Half 1 — exercise collation end to end (spec B1).** Rhyme-search the accumulated episode store, select one cluster, route it through the two-bin rule, land **one** consolidation (a mechanization change with a rationale pointer, or an instruction change with a tripwire and an expected-improvement record). **The routing decision is the reviewable evidence** — more than the change itself. Source episodes marked consolidated per retirement policy.

**Half 2 — retire the playbook.** Tommy ruled `.agent-work/LESSONS.md` a dead end. Verbatim:

> *"The playbook is a dead end between two useful things — an episodic lesson accumulator and actual updates of doctrine. The hard cap was intended to not let things hang out, but it just leads to forgetting when it's not cleaned up. The closest thing to a playbook is agents repo local directions. That's already a thing, let's use that. Agree that episodes capture the tally concept, we just need to actually clean up the episodes regularly (which is the curator's job, fundamentally)."*

And: *"Lessons shouldn't be used by live agents really in the future — we want to keep them working from local & global doctrine only."*

Concretely:

1. **Land the consolidation in `docs/agents/`, not LESSONS.md.**
2. **Drop the 20-entry hard cap**, naming what replaces it — the curator's regular cleanup, per the ruling. Removing it without a retention story just moves the problem.
3. **Every currently-active lesson gets a terminal disposition** — graduate to `docs/agents/` or the doctrine file that owns it, or delete with a reason. Nothing stays "active." **Retirement MOVES the file** (`decision:retirement-moves-the-file`); it does not annotate in place.
4. **Cut live agents off from lessons.** Launch orders and inherited-context blocks currently ride the Active section into every dispatch. That stops.
5. **#322 folds in** — `CONSTELLATION_OVERVIEW`'s truth-layer taxonomy omits the episode store, and the cutover ruling is what fixes it.

## The destination is already solved — copy it, do not invent it

`docs/agents/` in **f1Brainz** (commit `3541d292`) contains:

- `ORCHESTRATOR_CONTEXT.md` — planning and gate authority
- `CREW_CONTEXT.md` — implementation rules
- `engine-config.json` — checklist-engine project defaults

All three listed in its `README.md` documentation index, so they are discoverable rather than buried. **This repo has one file there** (`ORCHESTRATOR_CONTEXT.md`, landed in #325). So the crew-tier question the re-scope listed as open is **already answered in practice**, in a repo that has been running Constellation crews for months. Landing the crew file here is catching up to established practice, not pioneering.

**And Tommy's tiering principle governs where things go:**

| tier | audience |
|---|---|
| the repo's auto-loaded `CLAUDE.md` | **every** agent touching the repo |
| `docs/agents/{ORCHESTRATOR,CREW}_CONTEXT.md` | orchestrators / crew |
| a role's own skill | that role |

> *"We are tuning these artifacts to roles and not every agent in the repo needs this info. Even within constellation, the map is orchestrator content, not implementer content."*

**Placing content at a broader tier than its audience is a defect, not a delivery win.** Every graduation you route must name its tier and justify it.

## Prior-Wave Verdicts (pasted)

**#301 — episode store. MERGED `195e893`.** `episodes/README.md`, `episodes/active/`, `episodes/retired/` on `origin/main`. The `active`/`retired` split realizes the file-move ruling in the directory structure.

**#309 — coherence sweep. MERGED `967493c`. Recall 4/4, noise 0/7.** Two predictive episodes filed (`issue-309-001`, `issue-309-002`). It also fixed **#321** (the store validated ids it LISTED but not ids it was HANDED) — so programmatic writes are now guarded at `resolve_episode_path()`.

**Its most useful finding for you is a live coherence defect, not a seeded one: #348.** `docs/EPISODE_STORE.md` §1 claims `.agent-work/` is gitignored — **invalidated by #326, which landed in this same epic.** Days-old stale doctrine nobody had noticed. **Expect more of this class**; the corpus has been changing under itself all epic.

**#302 — Tommy's two-bin ruling. No third bin; Assumption 6 stands; B0.3 unchanged.** *"Machinize the mechanizable. We don't need stochastic reasoning for predictable logic... these are aspirations."* The third-bin candidates were ruled **not catastrophic**, not *mechanizable*. That distinction matters when you route your cluster.

**#342 — the store cannot express a confirmed prediction.** `LIFECYCLE_STANDINGS = ("active","disputed","superseded","rejected")` — **no `confirmed`.** A prediction checked and **held** is indistinguishable from one **never checked**; both sit at `active`. `create` requires `observed-behavior`, so a genuinely predictive episode cannot be filed before the event without fabricating an observation. **This bites your retirement policy directly** — "marked consolidated" needs a representation the store does not currently have. Decide how you handle it and say so; changing the store is #301's territory, so a workaround here is legitimate and a silent one is not.

## Pre-Rulings

Overridable if evidence contradicts them — say so when overriding.

- decision:destination-is-docs-agents — consolidation lands in `docs/agents/`, following f1Brainz's realized structure.
  `@grade: settled/human · leans #308`
- decision:retirement-moves-the-file — a retired episode's file **moves**; files stay clean of history unless they are themselves historical. Archives are a legitimate separate strategy.
  `@grade: settled/human · leans #308,#301`
- decision:no-cap-replacement-by-hygiene — the 20-entry cap goes; the curator's regular cleanup replaces it. Do not substitute a different numeric cap.
  `@grade: settled/human · leans #308`
- decision:tier-must-be-justified — every graduation names its tier and why that audience. Broader-than-audience is a defect.
  `@grade: settled/human · leans #308`
- decision:one-consolidation-not-many — land exactly **one**. This issue proves the loop, it does not clear the backlog.
  `@grade: settled/inherited · leans #308` (from spec B1)

## Honest-Null Clause

A measured negative is a complete, successful deliverable, reported with the same rigor as a win. The spec is explicit: *"if deletion alone suffices, the break is not taken — that outcome is success, not failure."*

Applied here with force: **if rhyme-search over the accumulated store finds no cluster worth consolidating, that is a real result** — it would mean the store is too thin, or the accumulation is not producing rhymes, and both are findings the epic needs. **Do not manufacture a cluster to have something to consolidate.** A forced consolidation would prove the loop runs while proving nothing about whether it works.

Scoped nulls: *"this store at this size produced no cluster"* — never *"collation does not work."*

## The methodology bar

**A check that cannot fail is indistinguishable from one that passed** — five recurrences in this epic (#337), including a test that survived two independent reviewer rounds, a losing condition bounded at 0, a mutation whose `sed` silently did not match, and a verification that compared two empty strings and reported a match. The sharpened rule:

> **Prove you read both things, then compare.** Empty-vs-empty, missing-vs-missing and skipped-vs-skipped all pass a naive equality check.

Applied to you: **"source episodes marked consolidated" and "the lesson was graduated" are both claims about state you must verify by reading, not by having performed the write.** And when you verify a file moved or a deletion landed, compare **normalized content or blob OIDs, never raw working-tree bytes** (#319 — the Admiral walked into this an hour after warning another issue about it).

## Inherited Latitude

**Delegated** — adjudicate and log: architecture/structural choices inside your deliverable; issue filing/closing on `fredcai6/constellation-skills` (`gh` pre-cleared — **file findings directly, never bank them worktree-locally**); fix-now triage; full test suite; `git push` to `epic-298/*`; **merge when green and reviewed, gated on the CI check exit code read at source — and confirm the status text reads `pass`, not merely that the command exited 0** (`gh pr checks` has been seen exiting 0 on a **pending** check).

**Must float — and for this issue that list is longer than usual:**
- **The two-bin routing ruling on your selected cluster — Tommy's, always.** This is the issue's spine.
- **Whether the consolidation pattern is trusted** after one live instance — his.
- Any change to the destination structure beyond copying f1Brainz's.
- Scope changes; production defaults; anything out-of-taxonomy.

**If your `gh pr merge` is refused by a permission classifier** — this happened to #309 despite the contract pre-clearing it (#145 recurrence) — **report it and hand the action up. Do not route around it.**

## File Ownership

Working notes: **`notes-308.md`**. Sole writer. Never `findings-308.md` — the harness `Write` tool refuses any basename containing "findings."

## Workspace

Worktree provisioned at dispatch; path given then. **First command from inside it:** `py scripts/verify_worktree_isolation.py --here "<path>"` — must exit 0, paste the output.

**Do not touch `C:/Programs/constellation-skills`** — it holds Tommy's uncommitted work. Other commanders may be live in sibling worktrees; never enter one. Edit canonical `skills/_shared/global-*.md`, **never** the `skills/<role>/references/` copies that `install_constellation.py` regenerates.

## Inherited Context

**Python/CI:** `py` is 3.12.13 (matches CI's pin) but has **no pytest**; `python` is 3.14.3 with pytest 9.0.2. Run the suite with `python -m pytest`. **Neither interpreter reproduces CI** — a local green is never the gate.

**The engine agents run is a DIFFERENT BINARY from the repo's** — 120,146 bytes vs 125,764, 108 lines apart (#344), because the installed corpus is 18 commits stale and a project-level install is **shadowed** by the global one. Two engine facts were re-verified in the served copy and hold: `_run_check_command` passes **no `cwd=`**, and postcondition **stdout is captured and discarded** (evidence is `{cmd, exit, shell}` only), so **the exit code is the only signal reaching the spine.** Any *other* engine claim you rely on, check against `~/.claude/skills/constellation-commander/scripts/checklist_engine.py`, not only the repo.

**Windows:** explicit `encoding='utf-8', newline='\n'` on every write. MAX_PATH is real. PR bodies via `gh pr create -F <tempfile>`. **Backticks inside double-quoted shell strings are executed and silently drop words** — use `--body-file`. Absolute paths for `git worktree add`.

**Engine:** never hand-edit spine/survey JSON. `--finding` text with backticks is shell-mangled. On a **survey**, `record` is the re-record verb; `advance`/`reopen` refuse as gated-only.

**Method:** *verify launch-order claims against the code* — **three of this Admiral's orders have carried wrong claims this epic, all caught by the commander they were handed to.** If something here does not match what you find, **the code wins, and say so in your return.** *Derive distribution claims from a command — and a command is only as good as its predicate* (a word count derived correctly from a command was still wrong because the command encoded a bad assumption about sentence boundaries).

## Budget

- **Model tier (required): Opus.** Cold plan critic **mandatory** — it has caught a blocking defect in every plan this epic, without exception. Sub-dispatches at the least-powerful tier that works. **No Fable at any tier; name the model explicitly on every dispatch.**
- Rewrite your crash-resume state note before **each** detach.

## Stop Conditions

Stop and return when: the two-bin routing question is ready (that is Tommy's and it is the point of the issue); rhyme-search finds no cluster (report the null, do not manufacture one); scope would change; **or you need context this order does not cover — return-and-query me, I answer and continue you.** Asking up is always sanctioned.

## Return Shape

Deliver your artifact and verdict **before** going idle.

1. **The cluster, and the routing question posed for Tommy** — with both bins argued, not one recommended into inevitability.
2. The consolidation landed, with its tier named and justified.
3. **Every active lesson's terminal disposition**, itemized. Nothing left "active."
4. Cap removed; the retention story that replaces it, stated.
5. Live-agent lesson intake cut — which orders/templates changed.
6. #322 folded; #342 handled, with your workaround named.
7. **Verification that source episodes are actually marked consolidated** — read back, not assumed; compared by normalized content or blob OID.
8. Map impact; triage candidates filed, numbers listed.
9. Workflow feedback — blunt.
10. `verify_worktree_isolation.py --here` output.
11. **PR number, CI check exit code AND status text**, read at source.
12. **Branch status: FINAL, or PENDING with what is still coming** (#338 — a terminal spine and a released lease describe the *run*, not the *ref*).
