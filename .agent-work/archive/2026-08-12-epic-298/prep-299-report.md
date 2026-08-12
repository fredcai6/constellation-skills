# Prep for #299 — dogfood corpus + baseline candidates

Status: COMPLETE (recon only — no decisions made, no repos changed)

Scope reminder: #299 asks Tommy to (a) pick the dogfood corpus, (b) pick 3-5
representative Commander tasks, (c) capture baseline runs of those tasks
BEFORE #304 (the map-input contract change) merges. #304 has not merged —
the baseline window is open as of 2026-07-31.

---

## 1. Candidate corpora

All paths below were checked directly on disk; nothing here is inferred.

### constellation-skills (`C:/Programs/constellation-skills`) — self-dogfood
- **No architecture map.** `docs/architecture/` does not exist (checked: not
  found). No `index.md` anywhere under `docs/`.
- 263 tracked files (`git ls-files | wc -l`). Small.
- Active: commits present through late July (this session's own git status
  shows commits merging same week).
- **#304 names `docs/architecture/index.md` as the canonical entrypoint, with
  an explicit "absent-state" degraded mode as the alternative.** Since that
  file doesn't exist here, this repo can currently only ever exercise the
  *degraded-mode* path, never genuine map-first orientation. It cannot prove
  the hypothesis; it could only demonstrate the fallback branch.
- Note: issue #300 (projection generator) and #304 (contract) are *of* this
  repo — using constellation-skills as the corpus would mean dogfooding the
  measurement tool on itself while it's mid-construction, which is a
  legitimate but different (and circular-flavored) test than "does map-first
  help a Commander navigate a real target codebase."

### superCoolSpaceSim_cpp (`C:/Programs/superCoolSpaceSim_cpp`)
- **Not a git repo** (`git rev-parse --is-inside-work-tree` → "fatal: not a
  git repository").
- Directory contents: only `.` and `..` and a single 0-byte file named `nul`.
  There is no source code, no docs, nothing to orient on.
- **Disqualified outright.** This is an empty/placeholder directory, not a
  working project. Flagging plainly rather than speculating about what it
  might become.

### f1Brainz (`C:/Programs/f1Brainz`) — path recorded in
`docs/DEBT_SWEEP_CADENCE.md:12` (grepped directly, not guessed)
- **Has a live architecture map.** `docs/architecture/index.md` exists,
  reconciled **2026-07-27** (4 days before today) for epic #659 closeout.
  Full structure: `docs/architecture/{index.md, MAP_BUILD.md, decisions/,
  overlays/, packets/, reference/}` — 37 files total under
  `docs/architecture/`. 16 domain packets (`physics.md`, `models.md`,
  `data.md`, `strategy.md`, `calibration.md`, etc.) — a Commander has
  genuine per-domain material to orient from before touching source.
- Large: 5,928 tracked files (`git ls-files`).
- **Actively worked right now**: 57 commits in the last 30 days, most recent
  commit and most recent architecture-doc commit both **2026-07-27**
  (`git log -5 --oneline -- docs/architecture` shows a steady cadence of
  "docs(#NNN): reconcile architecture map for ..." commits — map maintenance
  is a live, established habit in this repo, not a one-off).
- Rich open-issue backlog at Commander scale: issues in the 680-717 range
  are individually bounded (single-module or cross-module fixes/design
  questions), not epics.
- **Caveat found while checking cleanliness of the baseline**: the *current*
  `constellation-skills/skills/commander/references/commander-core.md` (and
  its templates) already reference `docs/architecture` — so today's Commander
  is not "map-blind." The pre-#304 baseline is "scattered-prose,
  no-canonical-entrypoint, no-degraded-mode-contract" map-reading, not a
  true no-map control. That's actually the correct comparison arm for what
  #304 changes (scattered prose → single canonical contract) — just don't
  describe the baseline as "no map" when reporting it; it's "informal map."

### network_elo (`C:/Programs/network_elo`) — found via the same
DEBT_SWEEP_CADENCE.md list, checked for completeness
- Has an architecture map (`docs/architecture/{index.md, packets/(10),
  overlays/, decisions/}`).
- 764 tracked files. 182 commits in the last-30-days window, **but** last
  commit AND last architecture-doc commit are both **2026-07-17** — i.e.
  despite the high commit count, this repo has been untouched for the last
  ~2 weeks relative to today (2026-07-31). Not currently active.
- Only 4 open issues, and they read as large/vague ("consider second order
  uncertainty rigorously", "Epic: Club pivot") rather than bounded
  Commander-scale tasks.

### story_time (`C:/Programs/story_time`) — same list, checked for
completeness
- Has an architecture map (`docs/architecture/{index.md, packets/(16),
  overlays/, decisions/}`).
- 182 tracked files. **0 commits in the last 30 days**; last commit
  2026-06-27, last architecture-doc commit 2026-06-24 — dormant for over a
  month.
- Open issues are almost entirely multi-phase epics ("Epic: CYOA fusion
  (Phase 7)", "Epic: Monte Carlo QD outer loop (Phase 6)"), not
  Commander-bounded tasks.

**Detectability read**: constellation-skills (no map) can't demonstrate
map-first value at all right now. superCoolSpaceSim_cpp is empty — not a
codebase. network_elo and story_time both have maps but are currently
dormant, and their open-issue backlogs skew too coarse (epics) or too thin
(4 issues) for a clean 3-5 task set. f1Brainz is the only corpus that is
simultaneously: (a) large enough that "just read everything" isn't free,
(b) has a genuinely current, actively-maintained map, (c) is under live
development right now (so the map could plausibly be stale/wrong in a real
way, not just untested), and (d) has a backlog of individually-bounded
issues at the right grain.

---

## 2. Candidate tasks (all in f1Brainz, `gh issue list --repo fredcai6/f1Brainz`)

### Representative (finding the right seam plausibly benefits from a map)

- **#696** — "Roadmap: Builds 2-3 + carried threads (post-#659 forward map —
  anti-orphan)". Requires synthesizing current system state across the whole
  physics pipeline before proposing what's next. Without a map this forces a
  full-codebase crawl; with one, it's closer to targeted verification. This
  is close to the purest map-first test in the backlog.
- **#717** — "Rethink the driver-utilization observable: unit / reference /
  per-lap sampling / predictability / grip-as-identifiability (design
  investigation)". Spans the driver-fingerprint and physics/grip modules;
  title alone doesn't localize which files own "the observable," so a
  Commander has to find the seam rather than being handed it.
- **#690** — "Reconcile #664 G σ⁺ band scale (whole-lap pace σ) with
  per-class deficit units". Cross-module reconciliation between the grip
  baseline (G) calculation and per-class deficit units — the boundary
  between two components, which is exactly what a map states explicitly
  and code crawling has to reverse-engineer.
- **#688** — "Grip-fit rain exclusion too aggressive: 'any wet sample' drops
  ~55% of weekends". The title names the symptom, not the file; locating
  where rain exclusion is implemented inside `grip_baseline` requires either
  reading the physics packet or crawling source.
- **#716** — "constellation: work_id-with-slash parsing breaks
  run_crew.py + verify_agent_feedback.py (nested Commander-under-Admiral)".
  Different flavor deliberately: this is a cross-cutting *tooling* bug
  (constellation harness embedded in f1Brainz), not a physics-domain task.
  Useful as a stress case — it tests whether the map covers this area at
  all, and if not, whether degraded-mode triggers correctly rather than a
  silent crawl.

### Uninformative (already localized — map can't add value; skip these)

- **#703** — bug already pinned to one test file (`test_damage_tractability.py`).
- **#710** — already lists the exact three files to repoint
  (`segment_map/{store,identity,derivation/derive}.py`).
- **#715** — names the exact private helpers and both files involved.
- **#704** — names the exact file (`instrument_panel/replication.py`).
- **#712/#713/#714** — "#670 follow-on" chain; each already inherits its
  location from #670, so the seam is pre-found by construction.
- **#691** — HITL pre-registration decision, not a code-navigation task at all.

---

## 3. Baseline feasibility

**What has to run**: one Commander (or commander-delegated) execution per
chosen task — minimum 5 runs for the 5 tasks above, more if Tommy wants
repeat runs per task for variance (not requested by #299's acceptance
criteria as written, which says "baseline runs," plural, of "those tasks" —
reads as one run per task, not N).

**What to archive per run**: the full transcript (tool-call sequence, in
particular whether/when `docs/architecture/*` paths appear relative to first
`src/` read — this is the raw material the eventual verdict in #307 needs),
the Commander's final plan/diff, and the task outcome (did it find the
right seam, correctness against what a human would call right). This
directly feeds #307's pairing of "projection manifest" + "run-transcript
ordering" + "correctness against baseline" — the manifest side doesn't exist
yet (#300 is AFK/not done), but transcript ordering and outcome can be
captured now by hand/log-scrape even without the formal manifest.

**Where to put it**: f1Brainz already has an established
`.agent-work/<issue>-<slug>/` convention for its own work (e.g.
`628-driver-utility`, `644-physics-fit-headless-hang`). Baseline runs live
naturally there, but the *epic* they serve is #298 in constellation-skills —
a different repo. This is a real cross-repo archiving decision nobody has
made yet: either (a) baseline artifacts live under f1Brainz's own
`.agent-work/` with a distinguishing prefix (e.g.
`.agent-work/constellation-298-baseline/`) and constellation-skills'
epic references them by absolute path, or (b) transcripts get copied into
constellation-skills' own `.agent-work/epic-298/`. Not deciding this here —
flagging it because #299's acceptance criterion ("baseline transcripts
archived and referenced") needs a concrete answer before the first run.

**Cost**: 5 full agentic Commander runs against a 5,928-file live repo —
each is a real, possibly tens-of-minutes, non-trivial-token run, not a
dry pass. Rough order of magnitude: same cost class as running 5 normal
Commander issues.

**Hazard 1 — these are real backlog items.** All five chosen tasks are live,
unassigned f1Brainz issues. Running Commander on them for baseline
measurement will, if allowed to complete normally, actually change f1Brainz
(implement the fix, open a PR, possibly merge). That's fine as genuine
dogfooding, but it means the baseline "spends" real backlog items now,
before the post-#304 comparison arm exists — there's no clean way to re-run
the *same* task fresh later, since the codebase will have moved. If Tommy
wants a true pre/post pair on identical tasks, the runs may need to stop at
the plan stage (not merge) and be replayed after #304 on a pinned commit,
rather than being allowed to land.

**Hazard 2 — the baseline isn't a clean no-map control** (see §1 caveat on
commander-core.md already referencing docs/architecture). Worth stating in
whatever gets filed as the baseline record so nobody later reads "baseline"
as "map-first behavior didn't exist before #304" — it existed informally;
#304 is formalizing/consolidating it, not inventing it from zero.

**Hazard 3 — map drift risk during the window.** f1Brainz is under active
development (57 commits/30 days, most recent 2026-07-27). If baseline runs
are spread over multiple days, the map itself could be reconciled again
mid-window (it already has a demonstrated cadence of "docs(#NNN): reconcile
architecture map" commits), changing what "map-first" means run-to-run.
Pinning a base commit for the baseline window (the way f1Brainz's own map
already stamps a base commit, e.g. `5f802731` in the current index.md) is
probably necessary.

---

## 4. Recommendation

**Corpus: f1Brainz.** It's the only candidate that is large enough for
"read everything" to not be free, has a genuinely current and
actively-maintained architecture map (not stale, not synthetic), is under
live development right now, and has a backlog of individually-bounded
issues at Commander grain. constellation-skills has no map to test against;
superCoolSpaceSim_cpp is empty; network_elo and story_time both have maps
but are currently dormant and their backlogs are the wrong grain (too thin
or too coarse).

**Task set**: #696, #717, #690, #688, #716 (five issues, reasoning per task
in §2), with #703/#710/#715/#704/#712-714/#691 explicitly excluded as
uninformative.

**Strongest reason**: f1Brainz is the only corpus where a map plausibly
changes what a Commander does — big enough to make full-codebase crawling
costly, with a map current enough (4 days old, actively reconciled) that
"the map is just stale and code-crawling is smarter anyway" isn't a
confound built into the choice.

**Strongest argument against this recommendation**: f1Brainz is *also* the
corpus a different, already-running epic actively depends on for its real
production roadmap (physics pipeline, Builds 2-3, live HITL calibration
decisions). Using its real backlog issues as measurement fodder for a
constellation-skills epic mixes two different projects' priorities —
running an experimental Commander against #696/#717/etc. for baseline
capture is real engineering time spent on f1Brainz's actual roadmap items,
gated by a different epic's schedule (#298/#299), not f1Brainz's own. If
Tommy is protective of f1Brainz's current sprint focus, that argues for
either picking tasks f1Brainz would deprioritize anyway, or accepting that
this measurement literally borrows real time from a different active
project.
