# Implementation Result

## Assigned gate
`g0` — Package, CLI and discovery: the prototype behind a real entrypoint. Issue #456.

## Return status
`partial` — **stopped at a HARD context trip, not at a defect.** Three of ten plan
items are closed; the engine refused `advance` on the fourth and a `refresh-request`
is filed. Everything closed so far is committed and green. See **Stop conditions hit**
for the exact relaunch instruction.

## Completed slice

Two of the gate's three deliverables are in and test-first:

1. **The package exists.** `scripts/code_map/` is this repo's first Python package
   under `scripts/` (the 42 incumbents are flat modules; `scripts/hooks/` was the
   directory precedent).
2. **The discovery layer.** `discover_corpus()` enumerates the mappable corpus from
   `git ls-files` and excludes `.agent-work/`. Red/green demonstrated (below).
3. **The CLI.** `build_parser()` puts six pipeline stages behind `argparse` with
   `--root`, so nothing is pinned to one checkout. `python -m scripts.code_map` is
   the entrypoint.

**Not yet done** (items m3–m9, all still `pending` in the plan): the extract,
supplement, render and check stage ports; the `.gitignore` entries; the bundling
resolution; the end-to-end build; the full-suite run. The CLI already dispatches to
the four unported stages through lazy imports, so those slices drop in without
touching `cli.py`.

## Scope

**Files changed** — all four are **new**, so `git diff` does not show them; they are
committed at `7e13781`:

- `scripts/code_map/__init__.py` (new)
- `scripts/code_map/discovery.py` (new)
- `scripts/code_map/cli.py` (new)
- `scripts/code_map/__main__.py` (new)
- `tests/test_code_map.py` (new)
- `.agent-work/issue-456/g0-implementer-plan.json` (+ journal) — engine state

**Specific exclusions touched:** no. No defect fixes (D1/D2/D3 untouched — nothing
that reads a line number exists yet). No schema changes. The checks are not
rewritten — not ported yet either. `map/` is not built and not committed.
`scripts/build_architecture_map.py` untouched.

## Behavior changed

Yes — new behavior only; nothing existing was modified. Per the handoff I make **no
"no behavior change" claim**: the prototype hardcoded `ROOT` to `C:\Programs\f1Brainz`
and had no `argparse`, so there is no prior behavior to diff against. What I verified
instead is stated in Evidence.

## Test mode

**Required:** test-first (TDD) for the discovery exclusion and the CLI argument
handling; test-after allowed for the ports.
**Satisfied:** yes, for both TDD behaviors — each was observed failing before the code
existed, and the discovery exclusion was additionally observed failing *behaviorally*
(module present, exclusion absent). The ports are not started, so their test-after
obligation is not yet due.

## Evidence

### 1. The exclusion test red without the exclusion, green with it (load-bearing)

Two reds were captured, weakest first.

**Red A — test written before the module:**

```bash
python -m pytest tests/test_code_map.py -k discovery -q --color=no
```

```
E   ModuleNotFoundError: No module named 'scripts.code_map'
ERROR tests/test_code_map.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.24s
```

**Red B — the behavioral one.** `discovery.py` was first written with
`EXCLUDED_PREFIXES = ()` (mutation confirmed applied: the module was in place and
importable, and the failure names real leaked paths, so the filter ran and let them
through):

```
>       self.assertEqual([p for p in corpus if p.startswith(".agent-work/")], [])
E       AssertionError: Lists differ: ['.agent-work/archive/2026-08-02-issue-304[13962 chars].py'] != []
E       First list contains 141 additional elements.
E       First extra element 0:
E       '.agent-work/archive/2026-08-02-issue-304/evidence/g4_assert_closeout.py'

FAILED tests/test_code_map.py::DiscoveryTests::test_discovery_excludes_agent_work
FAILED tests/test_code_map.py::DiscoveryOnThisRepoTests::test_discovery_on_this_repo_excludes_agent_work
2 failed, 3 passed in 0.55s
```

**Green — exclusion restored to `(".agent-work/",)`:**

```
.....                                                                    [100%]
5 passed in 0.50s
```

The mutation is a one-line edit to `EXCLUDED_PREFIXES` in
`scripts/code_map/discovery.py`, which is what plan item `m8-falsifiable` will
re-demonstrate formally at the gate boundary.

Both exclusion tests assert their own input precondition first — that the tracked set
actually *contains* `.agent-work` Python files — so a filter test over an input with
nothing to filter cannot pass silently.

### 2. CLI argument handling: red then green

Red:

```
E   ImportError: cannot import name 'cli' from 'scripts.code_map'
ERROR tests/test_code_map.py
1 error in 0.24s
```

Green:

```bash
python -m pytest tests/test_code_map.py -k cli -q --color=no
```

```
7 passed, 5 deselected, 6 subtests passed in 0.24s
```

### 3. The CLI runs on this repo

```bash
python -m scripts.code_map discover --root . | wc -l
```

```
108
```

Exit code 0. **This is the re-derived corpus number: 108 mappable files**, measured at
commit `7e13781`. The baseline recorded 103 at probe time; the delta is exactly the
five Python files this slice adds (`__init__.py`, `discovery.py`, `cli.py`,
`__main__.py`, `tests/test_code_map.py`). Tracked Python files total 244 at this
revision, so the exclusion removes 136. **No test pins any of these numbers** — they
are a measurement; the tests assert the rule.

### 4. Not yet produced

The end-to-end `extract -> render` run, the full-suite green, the `.gitignore`
entries, the bundling resolution and the wiring grep are **not** in this result. They
belong to the unstarted items.

## TDD evidence, if required

- Failing test observed: yes, twice for discovery (import-time and behavioral) and
  once for the CLI — output pasted above.
- Passing test observed: yes — `5 passed`, then `7 passed`.
- Refactor while green: no refactor needed.

## Docs/contracts touched
- None. `docs/agents/*` untouched.

## Map Impact

- **Structural anchors touched:** `scripts/code_map/` — created; the repo's first
  Python package under `scripts/`, four modules. `.gitignore` and
  `scripts/install_constellation.py` are **not yet touched** (item m7).
- **Capabilities added:** *derive structure from source* — partially: the corpus the
  derivation runs over is now enumerable and runnable (`code_map discover`). *Render
  an agent-lean page tree* — not yet.
- **Constraints honored:** stdlib-only (`argparse`, `subprocess`, `pathlib` only —
  no third-party import anywhere in the package). *Nothing committed carries a
  position* — trivially held: nothing position-bearing has been produced yet. *The
  run report carries no timings* — not yet exercised; the ports will drop the
  prototype's `pass1_sec`/`render_sec` fields.
- **Decision candidates:** see **Assumptions** — the artifact directory `.code-map/`,
  and the two prototype renderer modules I did not port.
- **Claims/evidence produced:** the discovery exclusion rule is falsifiable and
  demonstrated red; the mappable corpus is 108 files at `7e13781`.
- **Trust limitations:** none found in the map (there is no map — orientation was
  DEGRADED-NO-MAP, as the handoff states).

## Assumptions

1. **Artifact location.** The rebuilt stores go to `<root>/.code-map/`
   (`statements.jsonl`, `supplement.json`), and the page tree to `<root>/map/`. The
   handoff fixed neither. `.code-map/` keeps the intermediates out of the tree that
   `gs` commits, so the render stage's `rmtree(map/)` cannot delete the stores it was
   just built from. The three `.gitignore` entries in item m7 will name these paths.
2. **`python -m scripts.code_map` is the entrypoint.** `scripts/` has no
   `__init__.py`, so it resolves as a namespace package and this works from the repo
   root, verified. Running `scripts/code_map/__main__.py` as a file cannot work — a
   file run as `__main__` has no package context, so the intra-package imports break.
   This is the same flatness hazard the bundling question is about.
3. **The two superseded prototype renderers are not ported** — `render.py` and
   `render_fn.py`, the x11 nine-file article prototype. `render_map.py` supersedes
   both for full-repo rendering. They hardcode a nine-module f1Brainz list and load
   from `evidence/x7a`/`x7b` paths that do not exist here, so they cannot run against
   this repo, and porting them would create symbols with **zero external call sites**
   — which this gate's own wiring grep names as a stop condition. The read-only
   prototype keeps them, so nothing is lost if the Commander wants them lifted.
   **Flagging this rather than deciding it silently.**

## Stop conditions hit

**One: the engine's HARD context band fired at `advance m2-cli`.**

```
REFUSED: m2-cli: context at 15% is at/over the hard limit — advancing is blocked
until you request a refresh, so work is handed off at a seam rather than lost to a
runaway.
```

This is a **correct trip, not a false one.** `gauge_reader.thresholds_for` puts a
1M-window model at 0.08 soft / 0.15 hard — 15% of 1M is the configured 150K-token
hard limit. The gauge reading was fresh (`fill_fraction 0.151219`, sampled during
this run), so I diagnosed it before complying rather than after.

Per `global-everyone.md` §reach-up I did not push through. Filed:

```bash
attach m2-cli --type refresh-request --field seam=m2-cli --field why_ref=w-2
# attached e-m2-cli-1 (refresh-request) to m2-cli
```

`current` now shows `REFRESH REQUESTED: m2-cli (why_ref w-2)`.

**Relaunch instruction for the Commander.** Launch a fresh implementer against the
same plan file — `.agent-work/issue-456/g0-implementer-plan.json` — and have it
**claim with the same session id, `g0-impl-9febe0be`**. A same-id re-claim is
idempotent, so no `--force` and no takeover record is needed. It should cold-start
from `current` alone: `advance m2-cli` (its work is done — 7 tests green, only the
gate is unclosed), then drive m3 through m9. The remaining work is the four stage
ports, `.gitignore`, the bundling resolution and the closeout evidence.

## Out-of-scope observations

1. **The `.gitignore` position-cache entry has nothing to ignore yet.** The handoff
   requires three narrow entries — statement store, supplement, position cache — but
   no gate in `gate-spec.json` produces a position cache: `g3` only removes positions
   from `ids.jsonl`, and pages still carry `path:line, N lines`. So the third entry
   will be anticipatory. Either a later gate should produce the cache or that line
   should be dropped, otherwise it becomes exactly the stale ignore line `g3`'s own
   close criterion complains about for the supplement. **Triage candidate.**
2. **`corpus` is overloaded.** `docs/agents/GLOSSARY.md` defines `corpus` as the
   installed skills corpus; this issue uses it for the source files being mapped. The
   handoff's required symbol name is `discover_corpus`, so I kept it and said
   "mappable corpus" everywhere the distinction matters. A glossary row would settle
   it. **Triage candidate.**
3. **`git ls-files` quoting.** The discovery layer uses `-z`, so paths with unusual
   characters cannot be silently mangled by git's default path quoting. Noting it
   because a later reader may be tempted to simplify it away.

## Workflow Feedback

- **Handoff gaps:** the handoff fixes the package location and the CLI but never
  names **where the rebuilt artifacts land**. "Narrow `.gitignore` entries for the
  statement store, the supplement, and the position cache" presupposes paths that no
  field supplies, so the ignore rules cannot be written until the implementer invents
  the layout. Add an **Artifact Paths** field. Related: the position cache is
  required to have an ignore entry but is produced by no gate (above).
- **Context rediscovered:** the fact that discovery should read `git ls-files` is in
  `gate-spec.json`, **not in the handoff** — the handoff says only "enumerates the
  mappable corpus". I found it by reading the gate spec. That is a mechanism choice
  the handoff should carry.
- **Instructions improvised around:** the handoff's module table lists six prototype
  modules to port, but two of them (`render.py`, `render_fn.py`) are superseded and
  cannot run here, and porting them would violate the same handoff's zero-external-
  call-sites stop condition. Two instructions in one document point opposite ways; I
  took the wiring rule as governing and flagged it (Assumption 3).
- **What would have made this easier:** the plan template's implicit shape is
  "one item per step", but a ten-item plan on a stronger model still hits the HARD
  band a third of the way in — 150K tokens does not cover reading ~90 KB of prototype
  plus the doctrine set plus the port itself. A gate this wide should be dispatched
  as **two implementer runs by design** (package/CLI/discovery, then the stage ports),
  not as one run that discovers the seam by tripping into it.
