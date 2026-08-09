# Architecture reconcile — epic-418-redux (closeout step 3)

Run by an independent Cartographer subagent (`cartographer-418`) on `main` at `fab5edcd`, driven
through the checklist engine (`.agent-work/epic-418-redux/closeout/cartographer/plan.json`).

## The starting fact, because everything else turns on it

**This repo ships the Cartographer and has never run one on itself.** There is no
`docs/architecture/` — no `index.md`, no `packets/`, no `overlays/`, no `decisions/`, no generated
`map.json`. Not stale, not deleted: never created.

```
git log --all --oneline -- docs/architecture      ->  (empty)
git ls-files | grep -E 'architecture|MAP_BUILD'   ->  only skills/cartographer/templates/* and
                                                      .agent-work/ archives of other runs
```

So a reconcile here has no graph to diff against. The durable structural record actually in use is
`docs/CONSTELLATION_OVERVIEW.md` (Relationship Contract + Truth layers), `docs/agents/*`,
`docs/CHECKLIST_SCHEMA.md`, and README's *Repo layout vs. installed layout* — the same surface
epic-298's reconcile treated as the record. This reconcile treats it the same way, and says so
rather than silently substituting it.

**One consequence worth stating plainly:** the overview's Relationship Contract lists
`Cartographer -> docs/architecture/packets/ + index.md` as a producer contract. That row is correct
*as corpus doctrine* — it describes what the role produces in a host project — and it is left
unchanged. It is not a claim about this repo, and it should not be read as one.

## The epic's net change

```
git diff --stat ea854471..HEAD -- . ':(exclude).agent-work'
-> 35 files, 4505 insertions, 82 deletions
```

Of which 21 are `episodes/active/*` (raw history, not architecture) and 5 are test files. **Nine
files carry the architectural surface:**

| File | Change | Architectural weight |
|---|---|---|
| `scripts/install_constellation.py` | +260 | new `--check-readiness` mode (#458): four separately testable items, report-only |
| `scripts/checklist_engine.py` | +242 | trip ledger, `directives` rendering, HARD guard moved off `advance` |
| `scripts/verify_iterative_role_artifacts.py` | +165/-22 | bundle detection by structure not name (#501); `--skills-root`; `stop` transitions verifiable (#506) |
| `skills/commander/templates/COMMANDER_SPINE.template.json` | 1/1 | `archive.c2b` reachability check rewritten (#439, #446, #484) |
| `skills/commander/references/{commander-core,crew-dispatch}.md` | +3/-1 | result-artifact path is the delivery, not `SendMessage` (#507, #370, #413) |
| `skills/{implementer,reviewer}/templates/*_HANDOFF.template.md` | +2 each | same |
| `skills/triage/{SKILL.md,templates/TRIAGE_RECOMMENDATION.template.md}` | +67/-11 | issues record observations with baselines, not prescribed fixes |
| `docs/agents/CREW_CONTEXT.md` | +6/-2 | sanctioned CRLF exception for `checklist_engine.save()` |

## Mismatches found, and how each was routed

**0. The overview's role list named a role this epic deleted. CORRECT — BUT NOT MY EDIT.**

`docs/CONSTELLATION_OVERVIEW.md`'s role block listed `Lessons-auditor`. **That line's deletion
appeared in the working tree during this session and I did not make it.** Flagged rather than
silently accepted, because it would otherwise ride into the Admiral's commit attributed to this
reconcile. I verified it independently and **it is correct**:

```
skills/lessons-auditor/            -> does not exist, and `git ls-files` returns nothing
~/.claude/skills/constellation-lessons-auditor/  -> does not exist
git log --all --diff-filter=D -- skills/lessons-auditor/SKILL.md  -> 77e428dc
git merge-base --is-ancestor 77e428dc ea854471   -> true
```

The skill was retired at `77e428dc` (#447, wave 4 of **this epic**). Because that predates the
wave-5 fork point, a diff scoped to `ea854471..HEAD` could never have surfaced it — worth noting as
a limit of fork-point-scoped reconciles, not just a one-off.

> **ADMIRAL, THIS AFFECTS YOUR NEXT STEP.** `STATE_NOTE.md` closeout step 2 says *"Lessons audit —
> fresh-context subagent, `constellation-lessons-auditor`."* **That skill exists nowhere** — not in
> `skills/`, not in the installed root, not in any project skills dir. This epic retired it in wave 4
> and the closeout plan still names it. Decide what step 2 actually runs before dispatching it.

`docs/RECURSIVE_IMPROVEMENT_DESIGN.md` also names `constellation-lessons-auditor` (l.268, l.335).
**Deliberately left alone:** that file's header declares it SUPERSEDED, a historical record kept
*unedited* on purpose. Correcting it would falsify the record. Not a mismatch.

**1. The Triage contract row — stale. RECONCILED IN PLACE.**

The row read *"bounded future work with evidence and acceptance criteria."* `ff1f39c9` dropped
impact/scope/non-goals/acceptance from the issue body and `f586a0a9` replaced them with observation
blocks carrying conditions, `type` and `rev`. Verified against the template's own headings —
`Observations`, `Desired behavior`, `Possible fix`, `Open questions`, `Recommended priority`; no
`Acceptance` anywhere. Row rewritten to current truth, including the deliberate absence, so a later
reader cannot mistake the gap for an oversight and re-add it.

**2. `--check-readiness` shipped undocumented. RECONCILED IN PLACE.**

260 lines of new user-facing installer behavior with zero README coverage. Added to README's Install
section. **The added text was verified by running the command**, not by reading the code:

```
$ python scripts/install_constellation.py --agent claude --scope project --project . --check-readiness
Claude Code:
  - engine: READY -- pytest runnable under ...python.exe (pytest 9.0.2)
  - skills: NOT READY -- no skills directory at .claude\skills
  - hooks: NOT READY -- Context Governor hooks: UNWIRED ...
  - work_area: READY -- .git present at .
  NOT READY
EXIT=1
```

**3. `tc4` — the install/instantiation seam. RULED AND ANCHORED.** See below.

**4. Adjacent to #528. ROUTED AS EVIDENCE, NOT A NEW ISSUE.** See below.

**Checked and found already clean** (the waves reconciled their own doc surface): the trip ledger
and `directives` rendering are both in `docs/CHECKLIST_SCHEMA.md` (l.361, l.124/139); the
`checklist_engine.save()` CRLF exception is in `docs/agents/CREW_CONTEXT.md`; `POSITIONING.md` and
`REMOVABILITY_LEDGER.md` are unaffected.

## `tc4` — the ruling

> Crew 1's g4 float: *the template → top-level-script → installed-bundle seam has no map id, and the
> only record that the three wave-5 fixes compose across it lives inside one test class.*

### The seam, stated precisely

```
source        skills/<role>/{templates,references,scripts}/*  +  repo-root scripts/*.py
                 |  install_constellation.py: shutil.copytree(skill.source_path, target)
                 |  plus shutil.copy2 per `required_scripts` entry from repo scripts/
                 |  (install_skills, scripts/install_constellation.py:1214 and :1224)
installed     <skills-root>/constellation-<role>/{SKILL.md,templates,references,scripts}
                 |  init_work_area.py: resolves the BUNDLE's template, substituting
                 |  <work-id> / <commander-skill-dir> / <repo-root> into check text
instantiated  .agent-work/<work-id>/spine.json
```

### Ruling: **the seam earns a durable anchor. It does not earn a `docs/architecture/` node.**

Recorded as a named section in `docs/CONSTELLATION_OVERVIEW.md` —
*"The install and instantiation chain: one source, three live copies"* — carrying the layer chain,
the governing constraint, the three measured instances, and the verification pointer.

**Why it earns an anchor.** It clears the Inclusion Rule on two counts, not one:

- *Rule preservation.* It governs which layer a fix must land in, and the rule is violated silently.
  Three violations in a single epic: #501 (name-vs-structure bundle detection), #439/#446/#484
  (`archive.c2b` check text), and the Admiral's own run blocked by a `spine.json` instantiated
  before its own repair landed.
- *Trust.* It bounds what a green suite proves. "Fixed" and "reaching the agent" are separable
  claims here, and nothing in the record said so.

**Why it does not earn a `docs/architecture/` node.** Three independent reasons, any one sufficient:

1. **There is no graph.** Minting `docs/architecture/index.md` + one packet + one overlay for a
   single seam is not a sparse map, it is ceremony with a maintainer of nobody. The map model's own
   doctrine — *"every durable node and edge has a maintenance cost"* — argues against a one-node map
   more strongly than against a missing one.
2. **#456 is in flight and owns the question of where map surface lives.** Hand-building a competing
   `docs/architecture/` tree now would pre-empt an answer that is actively being built. The Admiral's
   brief is explicit on this and it applies directly here.
3. **The seam is invisible to a derived map anyway.** #456's extractor is a Python AST walk. Hop one
   is a filesystem copy; hop two is JSON text substitution. **Neither is a reference edge**, so no
   static scan will ever produce them. This is not a gap in #456 — it is exactly the residue #456's
   own scoping leaves behind (*"the judgment layer stays with the Cartographer until a stated
   retirement gate"*). **So this anchor and #456 do not overlap, and #456 landing does not retire
   it.**

**Not promoted to a `capability:`.** The chain is not something the system *does* for a user; it is a
structural property of how the corpus is delivered. On the map model's own split — struct answers
*where*, capability answers *what the system does* — this is a constraint on structure. If a map is
ever built here, the intended shape is a `constraint:` node anchored to the three structural nodes
(`install_constellation.py`, `init_work_area.py`, the `skills/<role>/templates/` tree), with a
`verified-by` edge to a claim pointing at `ComposedShippedArtifactTests`. **Recorded here so the id
does not have to be re-derived**; not created, because there is nothing to create it in.

**On "the only record lives in one test class."** That part of the float is accurate and is *not*
fully resolved by this anchor. `ComposedShippedArtifactTests`
(`tests/test_iterative_planning_doctrine.py:1519`) remains the only executable check that the three
fixes compose as shipped. The prose anchor makes the seam findable and states the rule; it does not
make the rule enforceable. Making it enforceable — a check that compares a copy against its source
— is future work, and is routed below rather than done here.

## Triage candidates

**TC-A — no check compares an installed or instantiated copy against its source.**
`install_constellation.py` writes hop one and `init_work_area.py` writes hop two; nothing verifies
either afterwards. The failure mode is measured three times in this epic, and its worst form —
a live run holding a pre-fix `spine.json` — took an Admiral waiver to get past. Current truth is
recorded in the overview; **remediation is future work.** Note that the fix is not obvious: the
correct behavior for an already-running agent holding a stale copy is a real design question
(re-instantiate mid-run? refuse? warn?), and this epic's own no-mid-wave-re-install ruling is
evidence that the answer is not simply "always refresh."

**TC-B — routed to #528 as evidence, not filed as a new issue.**
#528 asks whether markdown templates belong in the derived map, and as what. This reconcile answers
the architecture half of that question and the answer sharpens #528 rather than duplicating it:

> The architecturally significant property of a shipped template is **not its extension and not its
> content schema — it is that it is copied and then instantiated**, so each one has up to three live
> copies at different ages. That property is invisible to a `*.json` glob (which is #528's own
> finding) *and* invisible to an AST-derived map (because neither hop is a reference edge). So
> extending the sweeps from `.json` to `.md` would widen coverage of the wrong axis, and #456's map
> will not close it either. The verification #528 is reaching for is a **copy-vs-source comparison**,
> which is TC-A, and it applies identically to both extensions.

Follows this epic's own precedent of routing a finding to an existing issue as evidence rather than
opening a near-duplicate. **Not posted** — this run is scoped to leave edits in the working tree; the
Admiral posts or drops it.

## Verdict

**The recorded architecture now describes the system as it stands at `fab5edcd`.** Three stale
claims found (one of them pre-existing in the working tree, verified and kept), one unmapped seam
anchored, two candidates routed. No drift left open.

## What this reconcile did not do

- **Did not create `docs/architecture/`.** Ruled above, with reasons.
- **Did not touch `.agent-work/epic-418-redux/spine.json`**, any lease, or anything under
  `constellation-skills-wt/epic418-*`.
- **Did not run the test suite.** No source file was changed — the edits are three documentation
  files — so there is nothing here a suite run would verify. The one behavioral claim added to
  README was verified by running the command it documents.
- **Did not commit.** Edits are left in the working tree for the Admiral.
- A published `constellation-docent` explainer site, if one exists, is now one reconcile behind and
  can be regenerated with the docent skill. Soft pointer, not a dependency of this run.

## Files changed

- `docs/CONSTELLATION_OVERVIEW.md` — Triage contract row corrected; new section *The install and
  instantiation chain: one source, three live copies*. **Also carries the `Lessons-auditor` role-list
  deletion, which arrived in the working tree from outside this run** — verified correct, kept, and
  called out above so the Admiral commits it knowingly rather than by accident.
- `README.md` — `--check-readiness` documented in the Install section
- `.agent-work/epic-418-redux/ARCHITECTURE_RECONCILE.md` — this file
- `.agent-work/epic-418-redux/closeout/cartographer/plan.json` (+ `.journal`) — the engine record
