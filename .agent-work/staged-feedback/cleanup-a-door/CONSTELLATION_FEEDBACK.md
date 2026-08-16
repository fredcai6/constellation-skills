# Workflow feedback — `cleanup-a-door` (#604, #605, #603)

Commander, delegated, one working session. Base `a69bbac4`, head `5a626351`.
5 episodes at `episodes/active/cleanup-a-door-00{1..5}.md`.

## How closely the run followed the skills

Fully, and the engine is what made that checkable. Every gate was opened, closed and
reworked through the engine; no spine file was hand-edited. The one thing I did outside the
crew loop was correct `skills/workbench/references/checklist-engine.md` at `reconcile`,
which is that step's own mandate but sits outside the order's enumerated ownership list —
reported rather than quietly done.

## What actually cost time, in order

1. **The context HARD band tripped on eleven `start`/`reopen` verbs**, beginning at 22% of a
   1M window with ~780K left. The band is an absolute 150K cap, which a Commander exceeds by
   loading its skill, references, templates and the order. The launch order had *pre-ruled*
   that this is not a stop condition and named the legal sequence (attach refresh-request →
   `start` → work). **That pre-ruling was load-bearing**: without it the locally-correct
   reading at each trip is "advance and hand off", which the order itself names as producing
   an infinite handoff chain with no deliverable. A band expressed as a fraction of the
   window, or one that subtracts a role's load-in cost, would remove eleven round trips.

2. **Three of four review BLOCKs were documentation truth, never behaviour.** The functional
   change was correct and green from its first attempt. What kept failing was prose that no
   longer described the code — and two of those escaped the sweep meant to catch them:
   - a **line-based** `grep` cannot see a string built from adjacent literals
     (`git grep -F 're-read fresh'` → 0 files tree-wide; normalized sweep → 1);
   - a sweep scoped to **edit permission** rather than **blast radius** reported
     `LIVE IN-SCOPE HITS: 0` while its own output listed six live hits, four of them in the
     changed module's own docstring. That scoping was **my** handoff error.

   The durable cause is underneath both: the door's binding rule is restated in ~7 places.
   The final review noted, correctly, that fixing one restatement introduced the next
   imprecision — the smell producing its own next instance inside one run.

3. **The map-freshness ordering trap fired twice** (g1 and g3). `code_map` enumerates via
   `git ls-files`, so a rebuild run while a new file is still untracked is self-consistent
   and passes its own guard; staging the file turns it red. It is invisible by construction.
   A gate in between repaired the first instance incidentally, which hid it. This is a
   plausible pre-commit hook or a stated "rebuild the map last" ordering.

## What was ambiguous, missing, or contradictory in the order

- **The "door-detection change" is undefined.** File Ownership grants two files "for the
  door-detection change only, which lands last" — a change Mission never describes, the
  three issues never mention, and which exists nowhere in the repo (one grep hit, a false
  positive). Floated; not invented. This is the single ambiguity that cost real deliberation.
- **"This repo has no `docs/agents/` overlay" is false.** All three overlay files are
  tracked. Cheap to check, and the run read the right files.
- **The order's main baseline (3057) was off by one**; measured 3058 at the same commit.
- **The gate order in Mission was wrong on the evidence.** Taking #605 before #603 keeps
  every commit coherent, because #603 deletes the demo's only consumer. Overridden and
  declared, per the order's own "overridable if evidence contradicts it".

## What worked, and would be worth keeping

- **The cold plan critic paid for itself before any code was written.** Four blocking
  findings, all independently reproducible; the plan as first frozen could not have reached
  its own exit criterion. Withholding `LAUNCH_ORDER.md` from the critic mattered — its best
  findings were exactly where the plan had inherited the order's blind spots.
- **Crews that refuted their own predecessors by measurement.** One reviewer disproved two
  triage candidates the implementer had raised rather than forwarding them; another caught
  that `HEAD` had moved past the commit its handoff named and reviewed `HEAD`; another
  corrected its own methodology error mid-review (a differently-named clone fails
  `code_map` for a bogus reason) before reporting.
- **The final review recorded a `fail` and carried it past consolidation with an explicit
  `--override-reason` rather than downgrading it to a pass.** That is the behaviour that
  makes an APPROVE trustworthy.
- **`run_crew.py --spine` already binds a child's door correctly**, which is why crews could
  drive their own spines through the door all run while the *operator* session could not —
  a neat illustration of exactly the gap #603 closed.

## Cross-lane consequence worth a process note

This change falsified claims in **three files fenced to lanes B and C**
(`scripts/run_crew.py:468-471`, `scripts/hooks/spine_rail.py:1081`,
`tests/test_spine_rail.py:2698`). A lane cannot fix what it cannot touch, and nothing in the
launch order says who sweeps them. That is a merge-order hazard: whoever lands last inherits
them as stale-claim findings.
