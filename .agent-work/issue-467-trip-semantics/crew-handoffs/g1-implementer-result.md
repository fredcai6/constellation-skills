# IMPLEMENTER_RESULT

## Assigned gate
`g1-implement` — of `C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/issue-467-trip-semantics/execute.json` (issue #467, epic #418 wave 4).

## Completed slice
A disposable, runnable reproduction of issue #431's deadlock at the unmodified HEAD, built as an **end-to-end DIGEST-staleness property**, not as "advance raises". Both faces reproduce; every claim is asserted in code and backed by the engine's own literal output.

**Single command that rebuilds everything from scratch and reproduces both faces:**

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-467
python .agent-work/issue-467-trip-semantics/red-repro/repro_431.py --all
```

Final run: **24 `ASSERT OK`, 0 `ASSERT FAIL`, real exit 0.** Exit 1 would mean an assertion failed (a scoped null, with the transcript naming which one). The run wipes the entire `scratch/` root first — including the `context/`/`mechanical/` manifest sidecars the engine drops there — so "rebuilds from nothing" is literally true.

## Scope

**Files changed:** none under version control. Created, all local-only and deliberately not `git add`ed:

- `C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/issue-467-trip-semantics/red-repro/repro_431.py`
- `C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/issue-467-trip-semantics/red-repro/transcript-all.txt`
- `C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/issue-467-trip-semantics/red-repro/transcript-face-a.txt`
- `C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/issue-467-trip-semantics/red-repro/transcript-face-b.txt`
- `C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/issue-467-trip-semantics/red-repro/transcript-gauge-read.txt`
- `C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/issue-467-trip-semantics/red-repro/scratch/**` (throwaway spines + planted gauges, deleted and rebuilt on every run)
- `C:/Programs/constellation-skills-wt/epic418-a2-467/.agent-work/issue-467-trip-semantics/crew-plans/g1-implementer-plan.json` (my own engine-driven implementer plan)

**Specific exclusions touched:** no.
- Nothing under `scripts/` or `tests/` — proved below.
- `.claude/settings.json` (#458) untouched.
- Nothing written under `.agent-work/epic-418-redux/**`.
- No part of the fix implemented; the script only *runs* the shipped engine as a subprocess.
- The live `.agent-work/issue-467-trip-semantics/gauge.json` and `spine.json` were **not** modified. The live gauge still reads `fill_fraction 0.126843, observed_at 2026-08-08T10:22:49.263Z`, byte-identical to what was there before this gate. My plan file sits in `crew-plans/`, a directory with **no** `gauge.json` sibling, so driving it could never touch the live reading.

## Behavior changed
No. Zero source change by construction — the repro observes the engine, it does not alter it.

## Test mode
**Required:** `evidence-only` (inspection-only, evidence-capturing — #467: the RED leaves no residue).
**Satisfied:** yes. No pytest case was written, nothing was added under `tests/`, nothing was wired into the suite. The deliverable is a runnable script plus its captured literal output.

---

## Evidence

### 1. LOAD-BEARING — `git diff --stat -- scripts tests` is empty

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-467
git diff --stat -- scripts tests > /tmp/g1-diffstat.txt 2>&1; echo "DIFF_EXIT=$?"
```

Verbatim result:

```
DIFF_EXIT=0
--- begin ---
--- end ---
bytes:
0
```

Zero bytes of output. Corroborated by `git status --porcelain -- scripts tests`, which also printed nothing.

### 2. LOAD-BEARING — the planted reading was proved to have been READ

`_gauge_path` resolves the gauge as `Path(spine).parent / "gauge.json"`, so the repro plants it beside its **scratch** spine. Planted record (from the transcript):

```
planted gauge: ...\red-repro\scratch\face-a\gauge.json
  {"schema_version": 1, "fill_fraction": 0.3, "model": "claude-opus-5", "observed_at": "2026-08-08T10:29:47...Z"}
```

`claude-opus-5` → `_PROFILES (1_000_000, 80_000, 150_000)` → hard = 0.15, so 0.30 is comfortably over.

The engine's own advisory, verbatim from `current`:

```
CONTEXT 30% (>= hard): `advance` is BLOCKED until you request a refresh. Run: attach g2 --type refresh-request --field seam=g2 --field why_ref=<why-id>  - then hand off.
```

The repro asserts both that this line exists and that the percentage it reports is the one planted. It also runs a **silence/advisory pair on the same spine and session**: `current` with no gauge present prints no `CONTEXT` line; `current` after planting prints the line above. A silent governor and a governor with headroom are therefore distinguishable in this run, and "nothing happened" is never used as evidence.

### 3. LOAD-BEARING — Face A: the stale DIGEST at the seam, asserted in code

Setup, driven entirely by the engine's own verbs (`claim`, `start`, `attest`, `advance`) — no hand-written end state:

- `g1` completes. Its `advance` writes why-record `w-1`, the **PRE-TRIP** understanding. That record is now the live DIGEST.
- `g2` is started and worked to `1/1 met` (the engine's own tally), so nothing but the gauge can block its advance. The agent's real understanding has moved on into `g2`.
- Gauge planted at 0.30, over HARD.

The agent tries to advance carrying its current understanding, and is refused:

```
REFUSED: g2: context at 30% is at/over the hard limit - advancing is blocked until you request a refresh, so work is handed off at a seam rather than lost to a runaway. Run: attach g2 --type refresh-request --field seam=g2 --field why_ref=<why-id>
(exit 1)
```

The agent then does **exactly** what the engine told it to and stops:

```
$ checklist_engine.py --file spine.json attach g2 --type refresh-request --field seam=g2 --field why_ref=w-1
| attached e-g2-1 (refresh-request) to g2
| (exit 0)
```

A cold successor reads `current` alone:

```
LEASE active: repro-431-a (by repro-431, heartbeat ...)
ACTIVE g2 [in-progress] - Do the g2 work, then satisfy its postconditions.
1/1 met
next: advance g2 --why "<understanding>" (or --mechanical)
DIGEST: PRE-TRIP UNDERSTANDING: g1 established the seam contract; the writer is the only producer and the reader must fail safe to None.
REFRESH REQUESTED: g2 (why_ref w-1)
CONTEXT 30% (>= hard): refresh already requested for g2 - hand off now; do not keep working.
```

**This is the defect, and it is exactly the one the handoff warned against manufacturing.** The HARD refusal has **released** — the engine now says "refresh already requested … hand off now", and a further `advance` would be permitted. So the deadlock is *not* "advance raises". The deadlock is that the `DIGEST:` line in that very output still names the **pre-trip** understanding, because the `advance` that would have written the current one was refused and `advance` is the sole `why_trail` writer.

Assertions that hold (from the transcript, all `ASSERT OK`):

- the successor's DIGEST **equals** `PRE_TRIP_WHY` (an equality, not an eyeball);
- the understanding the agent actually held appears **nowhere** in the successor's `current`;
- that understanding was never written to the trail at all (the refused advance wrote nothing);
- the successor is pointed at `g2`, the gate the predecessor was working — so the brief it inherits is stale by exactly one gate.

**Counterfactual control.** The repro then builds the *identical* spine with **no gauge planted**, drives it through the same verbs, and runs the same `advance g2`. It succeeds, and `current` reads:

```
DIGEST: CURRENT UNDERSTANDING: g2 found the reader's None path is reached from three distinct failure modes, so the retry belongs in the caller, not the reader.
```

Asserted: the counterfactual DIGEST equals the current understanding, and differs from the tripped run's DIGEST. So the staleness is attributable to the HARD refusal and to nothing else about the spine's shape.

### 4. CONFIRMATORY — Face B: the HARD refusal masks the unmet postcondition

Same setup, but `g2` is in-progress with `c2` unmet (`1/2 met`). At 0.30 the agent gets only:

```
REFUSED: g2: context at 30% is at/over the hard limit - advancing is blocked until you request a refresh ... Run: attach g2 --type refresh-request --field seam=g2 --field why_ref=<why-id>
```

With the gauge rewritten to `fill_fraction 0.02` (below both bands), the *same* advance gives the refusal that was hidden:

```
REFUSED: g2: postconditions unmet ['c2'] Recovery: attest g2 --cond c2 --which postconditions --note "<verification>". Do not edit the JSON - use the engine.
```

Asserted: the HARD refusal does not name `c2`; the two refusal texts differ; the postcondition refusal became reachable only once the HARD band stopped firing. `_trip_hard_gate` runs at the `dispatch` chokepoint *before* `_run_verb`, which is why one instruction masks the other.

**Honest scope, asserted in the script so the transcript carries it:** `current` **does** still list `c2 [unmet]` even at HARD. The masking is scoped to the `advance` **refusal path**, not to the whole engine. An agent that reads `current` can still see `c2`; an agent that follows the refusal's own instruction ("request a refresh, then hand off") acts on the refusal text and hands off believing context was its only blocker. Reviewers should not read this finding wider than that.

### 5. CONFIRMATORY — suite at baseline (tripwire against accidental edits)

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-467
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests > /tmp/g1-suite.txt 2>&1; echo "REAL_EXIT=$?"
```

```
REAL_EXIT=0
1793 passed, 2 skipped, 683 subtests passed in 356.83s (0:05:56)
```

Exactly the recorded baseline. Exit code read from a redirect, never from a pipe. `python -m pytest`, never `py` (#454).

### Reproduction commands, all four modes

```bash
cd C:/Programs/constellation-skills-wt/epic418-a2-467
python .agent-work/issue-467-trip-semantics/red-repro/repro_431.py --all                 # REAL_EXIT=0
python .agent-work/issue-467-trip-semantics/red-repro/repro_431.py --assert-gauge-read   # REAL_EXIT=0
python .agent-work/issue-467-trip-semantics/red-repro/repro_431.py --face a              # REAL_EXIT=0
python .agent-work/issue-467-trip-semantics/red-repro/repro_431.py --face b              # REAL_EXIT=0
```

Each mode deletes and rebuilds its own scratch directory before driving it, so there is no run-to-run carryover. Transcripts land beside the script as `transcript-<mode>.txt`.

---

## Map Impact

- **Structural anchors touched:** none changed. Anchors *exercised* as observation targets: `scripts/checklist_engine.py` — `_trip_hard_gate` (~1439), `advance` (sole `why_trail` writer), `_latest_why_record` / `_digest` (~1121–1143), `_why_suffix` (~1179), `dispatch` (~2649, where the HARD guard runs before `_run_verb`); `scripts/gauge_reader.py` — `read()`, `thresholds_for()`, `_PROFILES`.
- **Capabilities affected:** none changed. The Trip two-band gate policy (`docs/CHECKLIST_SCHEMA.md` §Trip) is confirmed to behave as documented; the defect is in the *interaction* between that policy and why-capture, not in either alone.
- **Constraints touched:** `constraint:fail-safe-on-no-reading` honored and relied on — the repro plants a valid fresh reading and never infers behavior from an absent one. `constraint:no-absence-is-evidence` discharged by the silence/advisory pair on the same spine and session.
- **Decision anchors confirmed by evidence:** `decision:red-is-end-to-end-staleness` is now **measured**, not just argued — the transcript shows the HARD refusal releasing after the keyed `attach` while the DIGEST stays stale, which is precisely why an exception-only repro would have proved nothing. `decision:red-leaves-no-residue` honored: nothing under `tests/`, nothing wired into the suite.
- **Claims/evidence produced:** `claim:431-deadlock-real` — **supported**. Literal engine output showing the stale DIGEST at the seam, the planted reading quoted, its being-read proved, and a no-gauge counterfactual isolating the cause.
- **Trust limitations:** the Face B masking claim is scoped to the `advance` refusal path only (see §4). The repo carries no `docs/architecture` packet map (DEGRADED-NO-MAP, discharged); `docs/CHECKLIST_SCHEMA.md` §Trip served as the structural authority and matched the observed behavior exactly.
- **Triage candidates:** see Out-of-scope observations below.

## Docs/contracts touched
None. The repro is self-documenting: `repro_431.py`'s module docstring states what it proves and, explicitly, what it does not.

## Assumptions
- The pre-trip/current understandings are synthetic strings chosen to be unmistakably distinct. The defect is structural (which record the trail's tail holds), so the content of the text is irrelevant to the property being asserted.
- A two-gate spine is the smallest shape that exhibits "stale by exactly one gate". A deeper spine would restate the same property, not a stronger one.
- I read the scratch spine's raw JSON in exactly two places, both to assert a **negative** or to recover a why-record id (`_read_trail_text`, `_live_why_id`). The engine has no verb that displays an *absent* record, so there is no engine-output route to "this why was never written". Flagged rather than hidden, since doctrine treats reading spine JSON for state as a violation; here it is a scratch file, and it is the assertion surface, not the drive surface. My own plan was driven through the engine only.

## Stop conditions hit
None. No source modification was needed, the planted gauge was shown to have been read, the deadlock reproduced at HEAD, and no decision outside the granted authority arose.

## Out-of-scope observations

1. **The release path is the trap the fix must not re-create (for g2–g4).** Once the keyed `refresh-request` exists, HARD releases and `current` prints "refresh already requested … hand off now; do not keep working." A successor that takes that literally inherits a stale DIGEST; one that ignores it and advances writes a fresh DIGEST but has already been told not to. Any fix should be measured against Face A's exact assertion, which is why the repro asserts an equality rather than an exception.
2. **Triage candidate — the refusal's `<why-id>` placeholder is a copy-paste trap. Verified, not inferred.** `_refresh_attach_hint` prints a literal `why_ref=<why-id>` that the agent must resolve from the DIGEST itself. The engine already knows the id (`_latest_why_record`), so it could interpolate it. I tested the copy-paste path on a throwaway copy of the Face A scratch spine with its keyed request stripped:

   ```
   $ attach g2 --type refresh-request --field seam=g2 --field why_ref=<why-id>
   attached e-g2-1 (refresh-request) to g2
   exit 0
   $ advance g2 --why x
   REFUSED: g2: context at 30% is at/over the hard limit - advancing is blocked until you request a refresh ...
   exit 1
   ```

   The `attach` **succeeds** and the `advance` is **still refused** — the identity-aware release in `_trip_hard_gate` (#190) compares `payload.why_ref` against the live why-record id, and `<why-id>` never matches. So an agent that copies the command the refusal tells it to run gets a silent no-op: it believes it has requested a refresh, the engine disagrees, and nothing says so. Not in scope for this gate; worth a Triage issue.
3. **Triage candidate — `current` accepts no `--session-id`.** Every other verb takes it; `current` errors with `unrecognized arguments`. Harmless here and arguably correct for a read-only verb, but it costs a round trip for anyone scripting the engine uniformly.

## Workflow Feedback

- **Handoff gaps:** none material — this was the most precise handoff I have worked from, and the three repeated warnings in the dispatch (empty source diff, end-to-end staleness not "advance raises", prove the reading was read) were exactly the three places I would otherwise have cut a corner. One small gap: the handoff says to run "the literal `attach … --field why_ref=<why-id>` command the refusal prints", but the printed command is not literally runnable — `<why-id>` is a placeholder needing the live DIGEST's record id. I read the trail to resolve it (`w-1`); worth naming in the handoff, since a reviewer comparing my command to the printed one will see a difference.
- **Context rediscovered:** the exact `current` output format (`ACTIVE <gate> [status]`, `n/m met`, `postconditions:` block) — I guessed a shape, the first assertion was vacuous against it, and I rewrote it to key off the engine's own `n/m met` tally. A one-line sample of `current`'s rendered output in the anchors would have removed that round trip. Also `current`'s rejection of `--session-id`, which cost one run.
- **Instructions improvised around:** the doctrine that reading spine JSON for state is a violation does not cover asserting a **negative** about state — "this why-record was never written". No engine verb shows an absent record. I read the scratch spine's raw JSON for that one assertion and for recovering the why-record id, and flagged it in Assumptions rather than hiding it.
- **What would have made this easier:** put a single verbatim `current` transcript in the Map Anchors. Three of my four false starts were about output shape, not about the defect.

## Return status
`complete`
