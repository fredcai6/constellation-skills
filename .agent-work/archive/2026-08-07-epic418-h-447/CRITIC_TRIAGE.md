# Cold critic triage — issue #447

Two-critic cold panel, Opus, no authoring context, read only PROBLEM_STATEMENT + MISSION_FRAME +
PLAN_ALTERNATIVES. Panel-vs-single was chosen as a panel: this run retires
`lesson:falsify-a-check-against-a-decoy-before-trusting-it`, a twice-observed lesson about checks that
cannot fail, so shipping an unfalsified guard here would be the third instance.

**Verdict on the panel: it earned its dispatch.** It falsified two load-bearing claims I had labelled
"measured". Every finding below marked ACCEPTED was re-verified by me at source before acceptance —
not taken on the critics' word.

## ACCEPTED — BLOCKING, and I was wrong

### T1. `durable_root()` does NOT resolve to the main checkout. My §5 was false.

I claimed the stranding trap was measured away. It was not. `scripts/agent_work_root.py:136-140`:
under an **active Admiral epic lease** the main checkout is fenced read-only, so `durable_root()`
returns the *fallback* — this worktree. Re-verified by running the real gate:

```
$ python .../scripts/verify_agent_feedback.py epic418-h-447 --phase feedback
EXIT=1
durable feedback log does not mention work id 'epic418-h-447':
  C:\Programs\constellation-skills-wt\epic418-h-447\.agent-work\AGENT_FEEDBACK.md
```

Epic #418's spine holds an active lease, so my own gate points at **my worktree's** copy — the exact
file the retirement deletes. A plain `git rm` at g5 would strand my own closeout, and the two exits
would have been (a) recreate the retired file to pass the gate — literally #308's failure shape — or
(b) a human override in a run with no reachable human.

**Resolution — `decision:untrack-do-not-delete`.** g5 uses `git rm --cached`, not `git rm`. The file
leaves the **index** (which is what "shipped" means, and what the guard's path census checks) while
the working-tree copy survives for the duration of this run. My closeout then runs the pre-change
installed gate against a file that still exists on disk. After merge, a main checkout keeps a local
untracked leftover that dies with the next clone, and a commander still running the old installed
spine finds it — so the migration has no wedge window in either direction.
`@grade: settled/measured · settle: re-run the gate command above after g5 and confirm exit 0`

### T2. `.agent-work/` is TRACKED, not gitignored — and the store's own README says otherwise.

`.gitignore:1` is a comment reading *".agent-work/ is TRACKED: run artifacts, verdicts, lessons and
archives are durable project history, not scratch."* `git ls-files .agent-work | wc -l` → **3069**.

`episodes/README.md:12` asserts the opposite — *".agent-work/ is gitignored (see .gitignore line 1)"*
— and builds the store's entire "why a tracked path" argument on it. The store's own doctrine cites a
false fact about line 1 of a file it names.

**Consequences:** `decision:fencing-mechanism-dissolves` is **WITHDRAWN** — its premise was this false
claim. `stage_feedback.py` and the fence branch exist for *epic-lease fencing*, which is real and is
this run's own situation. They leave the deletion set. `episodes/README.md:12` becomes an in-scope
correction, because a load-bearing falsehood in the store's rationale is exactly the kind of thing the
next retirement would reason from.

### T3. The "nothing prescribes reading episodes" baseline was measured in the wrong directory.

I scoped the sweep to `skills/**` (0 hits) and declared constraint 4 satisfied by absence. But
`docs/agents/**` has 8 hits, including two live prescriptions:
- `docs/agents/CREW_CONTEXT.md:60` — *"**Read them with `scripts/query_episodes.py`** and the engine's
  `current` verb."*
- `docs/agents/GLOSSARY.md:16` — defines `harvest` as *"Reading stored episodes back to act on them."*

`CREW_CONTEXT.md` is what every crew role reads at its context step. So the violation of the run's
governing constraint already exists, in the doctrine directory the frame itself names as the doctrine
surface. **Both lines become in-scope edits**, and every guard leg extends to `docs/agents/**`,
`episodes/README.md`, `README.md`, `SKILL_INDEX.md`, `docs/POSITIONING.md`.

### T4. Four of the five proposed guard legs were already green. The guard was mostly theatre.

Measured by both critics independently on the untouched tree:

| proposed leg | state at `cbd9aee` | catches R1–R5? |
|---|---|---|
| bundle asymmetry (`query_episodes.py` in zero bundles) | already green — **both** scripts are in zero bundles; the asymmetry is manufactured by my own g3 | 0 of 5 |
| no episode address in instructions | already green (0 episode mentions under `skills/`); `ID_RE` matches any issue id, so it ships with a whitelist on day one | 0 of 5 |
| schema has no slot for a rule | already green, and the premise is false — `episodes/active/issue-308-001.md:46-50` already carries an imperative rule inside a `workaround` statement | 0 of 5 |
| wordlist over `skills/**` | already green | 2 of 5, and only inside `skills/` |
| retired-name absence | **genuinely red** (200+ sites) | n/a |

And the bundle argument is broken four ways, each measured: the reader runs from the repo with zero
installs; `Read`/`Grep` need no reader at all; `install_constellation.py:915` is an unfiltered
`copytree` of the whole skill dir; and `SCRIPT_RUNTIME_COMPANIONS` already ships `episode_capture.py`
into nine skills without any `SKILL_SCRIPT_BUNDLES` entry — **verified**: it is present in the
installed `~/.claude/skills/constellation-commander/scripts/`.

**Resolution — the guard is re-specified.** Legs replaced with critic 2's simpler, stronger set:

- **Leg A — path census.** `git ls-files` must not list the retired paths. Two lines, unparaphraseable,
  and it is the only leg that catches a future agent re-committing `.agent-work/LESSONS.md` verbatim
  (which advertises its own read path in its own preamble, so zero new mentions appear anywhere).
- **Leg B — frozen approval census of every shipped site naming the episode store**, compared against
  `tests/data/store_mentions.approved.txt` with a required reason per entry. Measured today: **18
  lines**, and **0** under `skills/`. So g3's rewiring makes this leg genuinely go RED, and the
  approval diff becomes the human-readable record of every shipped site that touches the store. Its
  failure message states the discriminator: *"if this is a WRITE path, approve it with a reason; if it
  tells an agent to READ the store and condition behaviour on it, it violates
  `constraint:episodes-are-not-prescriptions`."*
- **Leg C — presence half** (`tests/test_prose_deletions.py`'s rule: *"An absence-only suite would pass
  just as happily on a template that had deleted everything"*). The capture command must still be
  named in both spine imperatives, be in the install bundles, and exist on disk.
- **Leg D — retired-name absence** over the shipped surface, with each record-only root
  (`docs/superpowers/`, `tests/fixtures/`, `.agent-work/`, `episodes/`) carrying a **written reason**.

Dropped: bundle asymmetry, episode-address regex, schema-kind pinning (duplicates
`tests/test_episode_fields.py`). Kept small: the output-valve sentinel test, folded into g2 as one
test rather than a leg with its own ceremony.

**Honest limit, stated not papered over:** no mechanical leg catches a successor playbook that never
names episodes (`docs/agents/RUN_LESSONS.md`), or prescriptions written *inside* `workaround`
statements. The mitigation is the `docs/agents/` tombstone naming the **shape** — no successor
playbook, no read-and-apply loop — not a test pretending to cover it.

## ACCEPTED — amendments folded in

- **T5.** Guard sweep roots enumerated from the actual `git grep -l` output, not asserted.
  `tests/fixtures/*.jsonl` are recorded transcripts and cannot be edited without falsifying a
  recording — record-only with that reason.
- **T6.** `deny_globs` on `archive.c4` is **not** an independent mechanism: it is `mode: staged`, so it
  sees only changed paths inside a run that reaches that check. Stop counting it. CI pytest is the
  enforcement. (It also means this run's own `git rm --cached` may trip c4 and need a recorded waiver.)
- **T7.** `store_root()`'s replacement semantics must be **named**, not left as "the fix". Chosen:
  keep `store_root()` as the default seam, and pass `--store-root` explicitly from the spine commands,
  because the docstring already rules out `durable_root()` for a documented reason and I am not
  overturning that ruling inside a retirement.
- **T8.** g4 carry rule made explicit to avoid the fabrication asymmetry: **carry only a lesson whose
  `grounding` already names the observed event.** All six qualify (each cites a concrete artifact line).
  Anything that would need a synthesised `observed-behavior` is dropped with a reason instead.
- **T9.** One fresh-store smoke check in g7: run the capture gate against a repo with an empty
  `episodes/` and assert it behaves, since the corpus installs onto other repos.

## REJECTED, with reason

- **Critic 1's "re-plan from scratch."** The findings are bounded to exactly two areas — closeout
  sequencing (T1, T2) and the guard's leg set and sweep scope (T3, T4, T5). The rest of the frame
  (the obligation list, record-vs-doctrine split, historical-docs ruling, the `c1` bare-attest
  constraint, the AGENT_FEEDBACK drop-with-reason) both critics verified clean. Per the standing
  scope-discipline ruling, amend and freeze; do not restart.
- **A spine postcondition running the guard every run.** Still rejected, but now for the right reason:
  CI pytest is the single enforcement and I say so plainly, rather than leaning on `deny_globs` as a
  fictitious second mechanism (T6).
