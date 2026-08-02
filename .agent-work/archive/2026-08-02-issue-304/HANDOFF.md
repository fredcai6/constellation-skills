# Consolidated handoff — issue #304, from commander-304

**Read this, then `STATE_NOTE.md`, then `current`.** This exists so you do not have to reconstruct four
messages' worth of rulings from chat you cannot see. `LAUNCH_ORDER-304.md` is still your frozen
principal; everything below is what changed **after** it was written.

---

## 0. THE ONE THING THAT WOULD BE WORST TO GET WRONG

**Pre-registration is already done. Do NOT re-register.**

| SHA | what |
|---|---|
| **`0119fa4`** | `TRIPWIRES.md` — **T1–T4**, the prose-deletion predictions |
| **`1662b90`** | `TRIPWIRES.md` — **T5**, the anchor-change prediction |

g3's episodes must cite these SHAs as their pre-registration. **The predictions were committed before
any deletion existed — that is what makes them predictions.** Re-registering after the fact destroys the
only property that matters, and it cannot be undone by a later commit.

Episodes get filed **after** the run, each with `expected-behavior` = the pre-registered text and
`observed-behavior` = what actually happened. Never invent an observation to satisfy `create`'s
five-kind requirement.

---

## 1. Rulings since dispatch that changed the plan

### Q1 — RULED (Tommy): candidate B is OUT
No bootstrap/`CLAUDE.md` stanza, no install lifecycle. *"The map is orchestrator content, not
implementer content."* The general principle, which should shape anything you add: **placing content at
a broader tier than its audience is a defect, not a delivery win.** Three tiers — auto-loaded
`CLAUDE.md` (every agent), `docs/agents/{ORCHESTRATOR,CREW}_CONTEXT.md` (their tier), a role's own skill
(that role).

Corollary the Admiral issued: **zero-invocation was a defect in the measurement rig**, which launched
generic agents — not a delivery defect in the product. A Commander run invokes the Commander by
construction.

### Q2 — PROVISIONAL GO, still Tommy's
**Building** to necessity + reported-degradation is approved. **Shipping** it as the definitive meaning
of "primacy" is a scope decision that rides with the merge and is **not yet granted**. Keep the
gate-vs-report choice **flag-flippable** so a ruling to gate is a flip, not a rebuild.

### Q3 — RULED: tripwire mechanism replaced
`decision:tripwires-are-episodes` **keeps its ruling and loses its rationale.** The order justified it as
*"the episode record already carries a prediction and an outcome slot"* — it does not (issue #342).
Amended rationale: episodes are the destination because `LESSONS.md` is capped and is being retired by
#308. The prediction/outcome shape comes from **git**, not the store.

### All 15 cold-critic findings — triaged and ACCEPTED, with two Admiral amendments
Full table in `PLAN_CRITIC_DISPOSITION.md`. The two amendments are **binding on g3 and g4**:

1. **A mutation harness must assert the mutation APPLIED before asserting red.** A no-op mutation and a
   killed mutant both yield green. This caught a live instance in g1 — see §3.
2. **Every measurement artifact names its consumer and its successor**, or it is retired rather than
   left as decoration. Applies to g3's trend snapshot: consumer is *the next snapshot*, successor
   expected *at epic-298 close*.

### PRE-B landed mid-run and named the mechanism — this is the most important input
Five runs with **verified Commander loads**, so both pathless imperatives **definitely fired**.
Orientation moved **not at all**: `map_before_src` false on 4 of 4 runs that read source.

> **"A map-first imperative anchored to a late artifact is not a map-first imperative."**

The served plan imperative (`:40` at `74953936`) anchors to *"BEFORE authoring `execute.json`"* — which
happens at the **end** of a run. Crawl fifty calls, read the map, author the frame = **exact
compliance**. Run #698 read source at call 25 and the map at call 57 and satisfied it.

**Consequence, already folded into the g2 handoff:** re-anchor `tasks.context.imperative` to **"before
you open any source file"** — the act, not the artifact. `context` precedes exploration; `plan` does
not. **This is the untested variable.**

### Finding 14 — I overrode a critic on the order's authority, and the Admiral ratified it
The critic wanted the trend snapshot cut as scopeless. It is a **launch-order deliverable**, so a cold
critic cannot overrule it. I took the critic's real complaint (scopeless, consumerless) without its
remedy (cut it). Precedent worth knowing: **the order outranks the critic, and an override must be
flagged, not silent.**

---

## 2. Framing this must ship under — do NOT overclaim

- **The necessity gate is a REGRESSION FLOOR.** Measured against the baseline five: **sensitivity 0/4,
  specificity 0/1.** Four runs cited map artifacts *while exhibiting the defect* (they pass); the one
  run it would fire on (#716) was **correct to disengage**. Never describe it as the fix for what was
  measured. It catches map-**ignoring**; the measured failure is map-**lateness**.
- **The genuinely new value is reported degraded mode.** A repo without a map currently has **no
  contract at all** — silent crawl, no record.
- **Ordering is not preventively mechanizable by the corpus.** Needs a `PreToolUse` hook → settings.json
  → Tommy's per #180.
- **Named bypass, to state in the writeup:** crawl first, write anchors into the frame afterward. It is
  the **measured behaviour**, not a hypothetical loophole.
- **The mutation floor was BLIND, and a gap was found** — not "a feature was added." Say it that way.

---

## 3. THINGS I BELIEVE BUT HAVE NOT VERIFIED — treat as unverified

The Admiral asked for this explicitly. Each is a belief I acted on without proof.

1. **That the g1 re-review will return APPROVE.** At handoff it was still running (survey 0/7 complete,
   process alive). I verified B1/B2/B3 myself with positive controls, but **the reviewer's verdict is
   not in.** Do not record APPROVE without reading its artifact.
2. **That the served engine behaves like the repo engine.** My `_check_condition` / `_run_check_command`
   findings (stdout discarded; no `cwd`) were read from the **repo** copy. The **served** copy is 18
   commits behind and `checklist_engine.py` is one of the 3 differing files (#344). **Nobody has checked
   whether those findings hold in the engine that actually runs.** This undercuts a premise the whole
   design rests on.
3. **That the anchor change will not move `map_before_src`** (T5). A registered prediction, not a
   result. I also believe it is *better positioned* than the late anchor — also unverified.
4. **That deleting the dead-path prose changes no behaviour** (T1/T2). Reasoned from `load_config`
   degrading mechanically. **Not run.** That run is g3's job and is the whole point of deletion-plus-run.
5. **That `verify-orientation` is currently unwired.** It is built; g2 wires it. If g2 did not complete,
   **it is built-but-unwired — the seventh instance of that pattern**, and it must not ship that way.
6. **That the three g1 deviations are all safe.** Two were confirmed by the reviewer; I accepted the
   `.as_posix()` one on the implementer's proof plus the reviewer's confirmation, but did not
   independently re-run the `json.loads` failure myself.

---

## 4. Operational do-not list

- **Do not point ANY tooling at `C:/Programs/f1Brainz`.** A sibling PRE-B dispatch is capturing against
  it. `orient` **writes a receipt** into whatever `--root` it is given — I made this mistake and had to
  clean it up. Use a local fixture or scratch clone; ask the Admiral if you need a real map.
- **Do not touch** `C:/Programs/constellation-skills` (Tommy's uncommitted work) or
  `constellation-skills-wt/e298-331`.
- **Do not fix** #341, #342, #343, #344, or the `--receipt-dir` triage item. All out of scope.
- **Do not edit** `skills/<role>/references/global-*.md` — regenerated at install. Edit
  `skills/_shared/global-*.md`.
- **Cite SERVED line numbers** (`:22` context, `:40` plan at `74953936`) for anything describing runtime
  behaviour; the repo copy has drifted to `:22`/`:48`.

## 5. Mechanics

- **Lease `commander-304-e298` is still HELD** — deliberately not released, since releasing before the
  terminal `advance archive` breaks the provenance chain. Take it with
  `claim --force --reason "resuming this run"`.
- `.agent-work/` **is tracked** in this repo (#326). Commit artifacts; they are durable history.
- Run the suite with **`python -m pytest`** (`py` has no pytest). Local 3.14 vs CI 3.12 — **no 3.13+-only
  APIs**. **A local green is never the merge gate**; gate on the CI exit code read at source.
- Windows: write with `encoding='utf-8', newline='\n'`. Avoid backticks in `--finding` text (shell
  mangles them). PR bodies via `gh pr create -F <file>`, never a heredoc.
- **Branch `epic-298/304` is PENDING, not FINAL.** Nothing pushed, no PR, no CI. Do not merge (#338).

## 6. Triage filed — do not re-file

**#341** engine cwd · **#342** no `confirmed` standing · **#343** pathless phrasing elsewhere ·
**#344** stale corpus. Spine tc1–tc4. **#336** gets the subtraction note when g3 lands the deletion.
