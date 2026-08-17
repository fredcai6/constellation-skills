# notes-1 — lane D1, the complete doctrine sweep and the regrowth guard

## init (done)

Lease claimed **through the door**, no CLI, first command of the run:

    spine_lease action=claim claimed_by=commander worktree=.
    -> claimed lease constellation/567-d1/lane-d1/commander-delegated -> active

Epic definition-of-done item "a dispatched crew drives its own spine through the door end to
end" — this lane is the proof, and every gate below goes through the MCP verbs.

## The target is live in my own spine — verbatim, captured at init

`spine_status` on my own spine returned, as the first imperative I was handed:

> ... this is your own spine (the one this process's door is bound to), so the door needs no
> session id argument, it reads SPINE_SESSION from its own environment. **CLI fallback:
> `<engine> claim --session-id commander-567-d1 --claimed-by commander --worktree .`** (if a
> stale prior lease blocks you, re-run with `--force --reason "resuming this run"`). From here
> on, pass `--session-id commander-567-d1` on every mutating CLI call against this spine (the
> door tools never take one).

So both halves of the target reached a live Commander in the first thing it read. Note the
`<engine>` token survived instantiation unresolved in the template and was resolved to
literally nothing useful — `init_work_area.py` substituted `<commander-session-id>` ->
`commander-567-d1` but deliberately left `<engine>` alone.

## Baseline measurement at f05a3d78 — matches the launch order exactly

**`CLI fallback` clauses: 15 total, 13 mine, 2 lane D2's.**

Mine (13):
1. `skills/admiral/templates/ADMIRAL_SPINE.template.json:10` (init)
2. `skills/admiral/templates/ADMIRAL_SPINE.template.json:52` (closeout)
3. `skills/charter/SKILL.md:12`
4. `skills/commander/references/commander-core.md:127`
5. `skills/commander/templates/COMMANDER_SPINE.template.json:10` (init)
6. `skills/commander/templates/COMMANDER_SPINE.template.json:49` (plan)
7. `skills/commander/templates/COMMANDER_SPINE.template.json:123` (archive)
8. `skills/explorer/SKILL.md:31`
9. `skills/explorer/templates/EXPLORER_SPINE.template.json:12` (init)
10. `skills/explorer/templates/EXPLORER_SPINE.template.json:78` (route)
11. `skills/interrogator/SKILL.md:26`
12. `skills/write-a-skill/templates/gated-engine-SKILL.template.md:15`
13. `skills/write-a-skill/templates/survey-SKILL.template.md:11`

Lane D2's (2, not mine): `skills/workbench/references/checklist-engine.md:5`,
`skills/workbench/SKILL.md:37`.

**`<engine>` tokens: 11 across 7 files.**

| # | Site | Class |
|---|---|---|
| 1 | `docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md:59` | historical record — SURVIVES (pre-ruled) |
| 2 | `scripts/init_work_area.py:24` | comment naming the never-resolved-token convention — SURVIVES (pre-ruled) |
| 3 | `skills/admiral/templates/ADMIRAL_SPINE.template.json:10` | agent-facing — target |
| 4 | `skills/admiral/templates/ADMIRAL_SPINE.template.json:52` | agent-facing — target |
| 5 | `skills/commander/references/commander-core.md:127` | agent-facing — target |
| 6 | `skills/commander/references/crew-dispatch.md:35` | agent-facing — target (arrived in wave 1 via lane C) |
| 7 | `skills/commander/templates/COMMANDER_SPINE.template.json:10` | agent-facing — target |
| 8 | `skills/commander/templates/COMMANDER_SPINE.template.json:49` | agent-facing — target |
| 9 | `skills/commander/templates/COMMANDER_SPINE.template.json:123` | agent-facing — target |
| 10 | `skills/explorer/templates/EXPLORER_SPINE.template.json:12` | agent-facing — target |
| 11 | `skills/explorer/templates/EXPLORER_SPINE.template.json:78` | agent-facing — target |

## THE FINDING: the regrowth has a mechanism, and it is a test

`tests/test_mcp_adoption.py` **mandates the text I am sent to delete.**

`TestTier1ImperativeFields.test_field_still_carries_cli_fallback`, parametrized over
`TIER1_JSON_FIELDS` (7 imperative fields), asserts the exact CLI command line is present:

    assert _named_affirmatively(field, cli_substr), (
        f"{path} .{...} lost its exact CLI command line {cli_substr!r} -- "
        f"the CLI door must stay, never be removed or discouraged, ...")

Its docstring: *"Each of these 7 imperative fields must name a door tool as the default ...
AND still carry that SAME action's exact CLI command line (two-sided)."*

That is why #559's text "has been deleted twice and has grown back twice." A lane deleted the
clauses, the suite went red on a test whose failure message says *the CLI door must stay*, and
the lane put the text back believing it had broken a rule. **The deletion was never the hard
part; this test is.** The guard is therefore not an addition to a green suite — it is an
inversion of an existing one, and the sweep cannot land without changing `test_mcp_adoption.py`.

Also downstream: `tests/data/store_mentions.approved.txt` carries verbatim copies of the
ADMIRAL closeout and COMMANDER archive imperatives (lines 122, 128); editing those imperatives
requires updating that approved-data file.

Other files that reference the placeholder and will need reconciling:
`tests/test_init_work_area.py:322,404,408,414` (documents `<engine>` as a never-resolved token —
same class as `init_work_area.py:24`), `tests/fixtures/legacy_spine_organic.json` (a *legacy*
fixture, i.e. a record of an old spine — likely must survive).

## understand — three measurements that decide the shape of this lane

### M1. The door CANNOT drive a second checklist. Measured, fresh process.

`decision:the-cli-still-exists-for-operators` and `decision:complete-sweep` both rest on
"the door reaches every agent-facing case." I tested the one case nobody measured: a
**second checklist** — a Commander's `execute.json`, an Interrogator's `interrogation.json`,
an in-session crew member's own plan.

Fresh `python3` process, explicit paths, two engine-materialized spines under this checkout's
`.agent-work/` (`init_work_area.py`, real templates), `SPINE_FILE` set to the first:

| # | Action | Result |
|---|---|---|
| A | `spine_lease claim` on own spine | OK — `claimed lease constellation/probe-d1 -> active` |
| B | `spine_bind` to the second checklist, **lease held** | **REFUSED** |
| C | `spine_lease release`, then `spine_bind` | **succeeds** — door moves to the second checklist |

The refusal, verbatim:

> REFUSED: this door still holds an active lease on `.../probe-d1/spine.json` as
> `constellation/probe-d1`, and **one door drives one spine at a time**. Rebinding this door
> now would leave that lease held by nobody. Release it first (`spine_lease` with action
> 'release'), then call `spine_bind` again.

And an unbound door binds a second checklist fine (probed separately) — so the blocker is
precisely **holding your own lease**, which is the state every one of these agents is in.

The escape in step C is not available to any of them: `COMMANDER_SPINE.archive` states the
lease "must cover every journaled action ... releasing earlier ... fails the terminal
provenance check." So a Commander that released its spine lease to bind `execute.json` would
fail its own closeout. `_spine_bind`'s docstring names the governing decision:
`decision:one-spine-per-process-stands` — "the count never rises above one."

**Consequence.** The 13 clauses are not one kind of thing. They split:

- **10 bound-spine clauses** — the agent's own spine, the door works, the CLI line is dead
  weight. This is the epic's real target. Sweep.
- **3 second-checklist clauses** — `interrogator/SKILL.md:26`,
  `write-a-skill/templates/gated-engine-SKILL.template.md:15`,
  `write-a-skill/templates/survey-SKILL.template.md:11`. The door **provably cannot** reach
  these. (Lane D2's two workbench clauses are the same kind.)

For those 3, "CLI **fallback**" is the wrong word — a fallback implies a working primary.
The measured truth is the opposite: the CLI is the **only** path. Deleting the line outright
would strand an agent with no path at all, against `global-everyone.md` "Fail visibly rather
than emit plausible wrong output; no hidden fallback."

**Disposition (and the float).** The human ruled *"sweep all **possible** now"*. The Admiral's
narrower recommendation, which that ruling overrode, was about the **dispatched-crew** path —
and the re-measurement correctly showed that path DOES have a door (a crew launched by
`run_crew.py --backend cli --spine` is its own process, bound to its own spine). My finding is
a **different** path the ruling never considered: not dispatched-crew, but second-checklist
inside one process. So this is not relitigating the ruled question.

I therefore sweep all 13 — **no `CLI fallback` clause survives anywhere in my files** — but for
the 3 I reword to state the measured truth ("the CLI is the only path for a second checklist,
because the door refuses to rebind while you hold your own lease") rather than deleting the
path and stranding the agent. Replacement wording is explicitly my latitude. I float the
finding itself to the Admiral because it bears on a `settled/human` ruling.

### M2. The regrowth has a mechanism, and it is a test (see the init section above)

`tests/test_mcp_adoption.py::TestTier1ImperativeFields::test_field_still_carries_cli_fallback`
asserts the exact CLI command line is present in all 7 Tier-1 imperative fields, failing with
*"the CLI door must stay, never be removed or discouraged."* **This is why the text grew back
twice.** The sweep is not a deletion against a green suite; it is an inversion of this test.

### M3. The load-bearing unknown is answered, with an exception list of length ZERO

The guard's scope problem — express "agent-facing" without exempting the corpus or catching
historical records — is already solved in the repo and needs no new invention.
`test_mcp_adoption.py` defines `INSTRUCTION_FILES` as an `rglob` over `skills/` for
`.md`/`.json`, *walked, never listed*, with a >=60 floor so it cannot silently narrow.

Measured against that walk (101 files today):

- **IN**: all 10 files holding my 13 clauses and 9 target tokens.
- **OUT**: `docs/superpowers/plans/2026-06-27-...md` and `scripts/init_work_area.py` — the two
  pre-ruled survivors, excluded **by the structural rule itself**, named nowhere.
- **OUT**: `episodes/**`, `tests/data/store_mentions.approved.txt`,
  `tests/fixtures/legacy_spine_organic.json`, `notes-*.md` — every historical record.

"Agent-facing" == "text the corpus ships to an agent" == "under `skills/`". The two survivors
survive because of what they ARE (a plan record; a script comment), and the walk already
knows that structurally. **Zero exception entries.** This is the answer to
`decision:guard-scope-is-yours-to-design`, and it avoids the 11-entry decay the order warned of.

### Ownership gap found — floating it

`tests/test_mcp_adoption.py` and `tests/data/store_mentions.approved.txt` are **not** in my
sole-writer list and **not** fenced to any other lane. The sweep is impossible without editing
the first (it mandates the text) and the second is generated-approved data holding verbatim
copies of two imperatives I must edit. No other lane owns them, so there is no collision risk.
I proceed and float the gap, per "Anything that fits no class above -- float, with one line on why."
