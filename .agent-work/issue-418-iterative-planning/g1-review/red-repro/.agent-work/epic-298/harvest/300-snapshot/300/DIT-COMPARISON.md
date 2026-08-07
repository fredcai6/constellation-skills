# Design-it-twice comparison — the projection manifest interface (issue #300)

**Status: comparison complete, recommendation defended, CONVERGENCE NOT TAKEN.**
Per `decision:convergence-is-human` in `LAUNCH_ORDER-300.md`, the choice below is floated to the
Admiral, who surfaces it to Tommy. I generated and compared; I did not settle.

Candidates: `.agent-work/300/dit/CANDIDATE-{A-minimal,B-ports,C-caller}.md`
Shared brief: `.agent-work/300/DIT-BRIEF.md`

---

## Panel-vs-single record

**Panel, N=3.** Rationale: one of epic-298's two declared load-bearing interfaces; the confirmed
spec requires design-it-twice here and `decision:design-it-twice-required` re-rules it
non-skippable. "When in doubt, panel." Three parallel Opus authors, one named constraint each,
none seeing the others' work.

| Candidate | Constraint | Author's own one-line shape |
|---|---|---|
| A | `minimal-interface` | `{contract, step, files:[{path, rev}]}` — flat, timestamp-free, printed by a read-only `context` verb; writes no file |
| B | `ports-and-adapters` | `{contract, content_digest, content, run}` behind three ports (declaration / resolver / pure projection) with two encoders |
| C | `common-caller-first` | one entry row, two envelopes: a **committed** `skills/<role>/CONTEXT_PROJECTION.json` plus a run-local manifest |

## Untaken roads (loud skips)

- **`max-flexibility` / "assertion-native" as a fourth candidate** — not generated. Reason: the
  no-foreclosure requirement (`decision:no-foreclosure`) is a *property to score every candidate on*,
  not a design stance one candidate can own. Making it a fourth constraint would have produced a
  candidate that pre-builds Stratum A, which the pre-ruling forbids. It was applied as a fifth
  comparison axis to all three instead.
- **Regex-extraction of paths from the existing imperative prose** (no new declaration field) —
  named and rejected inside candidate B, not given its own author. Reason: `verify_state_note.py`
  already does regex-over-prose in this repo, so the pattern is real, but a regex over prose cannot
  be swapped, versioned, or made to carry `required`. Recorded here so the rejection is visible.

---

## What all three independently converged on

This is the strongest result of the panel: three authors under three different constraints, none
seeing the others, agreed on five things and each verified them against live bytes. **These are not
open choices — treat them as settled findings.**

1. **Revision identity is the git blob OID of the LF-normalised bytes, computed in-process.**
   `sha1(b"blob %d\0" % len(lf) + lf)`. All three verified it equals `git hash-object` /
   `git rev-parse HEAD:<path>` under this repo's `* text=auto` + `core.autocrlf=true`. One function
   covers tracked, dirty, untracked, gitignored, and out-of-repo files **with no case analysis and
   no git subprocess**. A commit SHA was independently rejected by all three: it lies about dirty
   trees and says nothing at all about `docs/agents/` (untracked) or `.agent-work/LESSONS.md`
   (gitignored, and in a different checkout under a worktree). This structurally eliminates CRLF —
   the corpus's single largest named irreproducibility source — rather than excluding it.
2. **The declaration is a new *optional* ordered list on the spine task**, root-token-prefixed,
   sitting beside `constraints`/`directives`. Absent → empty manifest, so every existing spine keeps
   working untouched. Fan-out is only the templates we choose to annotate.
3. **No globs, no directory patterns, ever.** A glob would import filesystem ordering — the second
   named irreproducibility source — into the record for no benefit. Declaration order **is content**
   and is never sorted: doctrine has reading precedence ("inherited global doctrine, *then* project
   deltas").
4. **The imperative prose is not deleted.** All three found the same thing in the real text: the
   `context` imperative carries rules a path list cannot express — the substitute-and-record rule
   when `docs/agents/` is absent, and "a missing engine-config is a sanctioned degradation, do NOT
   create the overlay file." All three therefore keep prose and add a **mechanical lint** pinning
   declaration against prose. (A and B keep the prose verbatim; C deletes only the bare path
   enumeration and keeps the why.)
5. **Metadata only — never file content.** The record says what was made available at which
   revision. It is not an archive and carries no claim of use. All three refused to widen it.

---

## Where they genuinely differ — the actual decision

### Choice 1 (load-bearing): is there a **committed** artifact?

| | A | B | C |
|---|---|---|---|
| Committed, diffable artifact in git | **none** | none | **`skills/<role>/CONTEXT_PROJECTION.json`** |
| Run-local artifact | none (stdout only) | `.agent-work/<wid>/context/<step>.manifest.json` | yes, alongside the committed one |
| Who owns persistence | pushed onto #306 | the producer | the producer |

This is the decision. Spec **B2** says, in its own words: *"Ahead-of-time generation for
slow-changing, role-shaped doctrine: a versioned script builds the projection, **so every doctrine
change produces a reviewable diff of what agents will actually see**."* The issue restates it.
A and B produce **no diff in git at all** — under either, a doctrine change produces nothing a human
or a drift check can compare against, and the epic's spec B3 drift check (issue #306) would have to
invent its own committed artifact later. Only C delivers the spec's stated purpose.

A's counter is honest and worth recording: writing no file gives the cleanest stochastic-boundary
story and the smallest surface. But it satisfies acceptance criterion 1 *definitionally* ("the
manifest is the output of the assembly because there is no other assembly") rather than structurally,
and it delivers the substrate's stated reason for existing to a later issue.

### Choice 2: the exclusion set

- **A: empty.** Elegant — the determinism test is a literal byte comparison with no masking rule,
  and a masking rule is exactly where a real difference can hide. But it is empty *only because A
  persists nothing* and pushes time/run-identity onto #301.
- **B and C: one JSON pointer, `/run`.** Not a maintained field list — a subtree the content
  rendering omits entirely. A new varying field cannot be "accidentally content"; it has to be
  placed in one subtree or the other.

C gets both properties at once, which A and B each get only one of: its **committed** artifact has
**no `run` key at all** (A's empty-exclusion-set property, applied exactly where the determinism test
runs), while its run artifact quarantines every varying fact in one pointer (B's discipline).

### Choice 3: how much port machinery

B's author disowns his own Port A: *"Port A is speculative and I can't defend it on today's
evidence… it currently buys nothing but symmetry."* B's two-encoder split also creates a failure
mode a single encoder does not have — a stored digest disagreeing with its own on-disk content —
paid for with a verify-on-read. Only B's **resolver port** (the single impure edge, filesystem +
git, injectable) pays for itself immediately, and it pays in exactly the currency the pre-rulings
care about: it is what lets the determinism test point the whole thing at a fixture tree.

### Axis scoring

| Axis | A | B | C |
|---|---|---|---|
| **Depth** | high — one call hides CRLF, the four file states, encoding | medium — consumers see 4 keys, implementers pay for 3 ports + 2 encoders | medium-high |
| **Locality** | highest — one function + one verb, no new file | medium — new module, ports, two encoders | lowest — engine + new script + role templates + installer + tests |
| **Seam placement** | good, but stops short of where B2 needs it | over-built at Port A, right at the resolver | right for all three known callers; no seam for B2's later whole-role projection |
| **Testability** | good; empty exclusion set makes the determinism test one byte compare | best — one injectable impure edge | good; adds a real lint and a key-order pin |
| **Foreclosure risk (Stratum A)** | lowest — a `{path, rev}` row is already an assertion with a source | low | low |

---

## Recommendation — a named hybrid: **"C's two artifacts, A's row, B's resolver"**

Not a menu. One shape:

1. **Declaration** — the converged answer (2,3 above): optional ordered `context` list on the spine
   task; each entry `{root, path, required}` with root tokens `skill:` / `repo:` / `durable:`;
   no globs. The `required` flag lives in the **declaration**, not in the manifest.
2. **Row** — A's minimal `{root, path, rev}`. Drop C's `bytes`, `canon`, and `state`: `state` is
   `rev == null`, `bytes` is redundant against `rev` for identity, and `canon` (tracked/untracked)
   is **environment-varying**, which is a determinism hazard, not a feature — see the amendment below.
3. **Two envelopes** — C's structure. A committed, content-only
   `skills/<role>/CONTEXT_PROJECTION.json` (**zero** varying fields, empty exclusion set), and a
   run-local `.agent-work/<work-id>/context/<step>.json` carrying the same content plus one `run`
   subtree that is the entire exclusion set (`/run`, B's pointer discipline). #301 consumes the run
   artifact; the drift check and the human diff read the committed one.
4. **Producer** — one pure function beside `state()`, selecting via the **existing** `active_id(cl)`
   (this is what satisfies `decision:extend-dont-parallel` — no second selector), with B's resolver
   as the single injectable impure edge. **Drop B's Port A and B's two-encoder split**: one
   canonical encoder, `json.dumps(..., indent=2, ensure_ascii=False)` + `"\n"`, written
   `newline="\n"` (not optional on Windows).
5. **CLI** — A's one read-only `context` verb for the run manifest, plus
   `scripts/context_projection.py` to generate/regenerate the committed artifact. #300 ships
   generate + emit + a determinism test; the loud-failing drift **gate** stays issue #306's.

### The load-bearing amendment the comparison produced

Comparing the three surfaced a defect none of them had alone, and it would have shipped a broken
drift check:

**`rev` for a non-tracked file varies by environment, so it cannot go in the committed artifact.**
`docs/agents/ORCHESTRATOR_CONTEXT.md` is *absent* in this worktree and *untracked-but-present* in the
main checkout — candidate A recorded a real OID for it (`2a5ed203…`), candidate C recorded
`state: "absent"` for the same file. Both are honest about their own environment and they **disagree
with each other**. A committed artifact built that way false-FAILs its own drift check on the next
machine.

The fix falls out of the ahead-of-time-vs-per-run distinction spec B2 already draws — same row
shape, two truth-sources:

- **Committed artifact**: `rev` resolves **only from the git object DB** (tracked paths). Anything
  not tracked is `null`. Deterministic across environments because it is a pure function of the
  object DB, not of the working filesystem.
- **Run manifest**: `rev` resolves from the **bytes actually delivered** (working tree), including
  untracked and out-of-repo files. That is the honest delivery record, and it is per-run by nature.

### Why it wins, axis by axis

**Seam placement** — it is the only shape that delivers the substrate's stated purpose (a reviewable
git diff of what agents will see) inside this issue rather than deferring it to #306, and it puts
the one seam that pays for itself (the injectable resolver) exactly where the determinism test needs
to point.
**Testability** — the committed artifact keeps A's empty-exclusion-set property, so the determinism
acceptance test is a literal byte comparison with no masking rule at the exact place the pre-ruling
requires it (clean checkout, second environment).
**Locality** — it accepts C's largest cost (fan-out across engine + script + templates + tests)
knowingly. That is the price of a committed artifact and there is no cheaper way to buy one.
**Depth / foreclosure** — A's three-key row keeps each entry trivially expressible as a Stratum A
assertion (`path` = subject, `rev` = source identity), and drops the two fields (`canon`, `bytes`)
that would have to be re-litigated later.

### Adversarial fixtures this must ship with

Per `lesson:round-trip-tests-prove-artifacts-not-parsers`, a determinism run over the real corpus
proves the corpus is clean, not that the tool is right. Required alongside it:

- a fixture whose CRLF and LF twins **must** produce the same `rev` (false-FAIL hunt);
- a fixture where a declared file's bytes changed but the manifest is stale — the check must **not**
  silently PASS;
- an untracked-vs-absent fixture, the exact shape of the amendment defect above;
- a declaration-order permutation that **must** register as drift (order is content).

---

## Framing block — for Tommy, presented with the float (explicitly NOT a proposal)

**Constraints in play:** minimal-interface (what is the least we can get away with), ports-and-adapters
(where should the seam sit), common-caller-first (what do the three real consumers actually want).

**Held fixed for all three:** Markdown-in-git canon; no LLM at assembly time; extend the existing
spine selector; delivery-not-use; no foreclosure of the assertion model; determinism proved by
rebuild in a second environment.

**What the choice really is, in one sentence:** whether issue #300 ships a **committed, diffable
artifact** (more files touched now, but the spec's "every doctrine change produces a reviewable
diff" becomes true immediately), or ships only a **run-time record** (smaller and cleaner now, but
the diff — the reason the substrate exists — lands later in issue #306).

**Illustrative sketch — not a proposal, carries zero weight at convergence:** one committed JSON per
role listing, per spine step, the ordered files that step delivers and each one's git blob OID;
a twin of it written per run under `.agent-work/`, with timestamps quarantined in a single `run` key.

---

## Cross-interface risks toward #301 (flagged, not designed around)

All three authors independently flagged the same two. Neither is mine to settle:

- **Durability (all three, C's R2).** Run manifests live under `.agent-work/`, which is gitignored
  and destroyed by `git worktree remove`. If #301's durable store holds a *reference* rather than a
  copy, every reference dangles after worktree cleanup. Rows are deliberately small so #301 *can*
  inline at capture time — but inline-vs-reference is #301's call and a real decision.
  Compounding it: `agent_work_root.py` returns the **worktree**, not the main checkout, while an
  Admiral lease is active (verified live in this worktree by candidate C), so "put it in the durable
  root" is not by itself a guarantee.
- **Cardinality (B).** One manifest per spine **step**. If #301's episode record assumes a single
  `context` field per episode and an episode spans several steps, #301 gets N pointers where it
  expected one. Collapsing to one-per-episode would destroy per-step attribution, which is the point.
  If #301 has already assumed cardinality 1, **one of us must change** — that is an Admiral float.
- **Typing (C's R1).** Assumes #301's `context` field accepts a JSON object or a path string. If it
  is typed as free text, the structure is lost for the drift and human-diff consumers.
- **Contract skew (C's R4).** The manifest's `contract` int is independent of the engine's
  `_STATE_CONTRACT_VERSION` (both read `1` today). Whatever #301 stores should be named so the two
  cannot be confused.

---

# ADDENDUM — shared-assumption audit (added after the comparison froze)

Prompted by a finding from sibling issue #301, relayed by the Admiral: **a panel varies what it is
told to vary and inherits everything it is not.** #301's four candidates unanimously chose a store
location that was gitignored — violating a settled human ruling — and not one caught it, because all
four inherited the location from prior art without checking. Agreement was read as evidence when it
was only inheritance.

That signal is the same one my comparison rests on. So the useful question is not "are the five
converged findings right" but **"which of them did all three authors *inherit* rather than
*derive*?"** Audited below, honestly, including where the answer is unflattering.

## Mechanical check first: `git check-ignore` on every path this recommendation names

#301's error was catchable with one command before any design work. Run against all ten paths:

```
tracked-ok  skills/commander/CONTEXT_PROJECTION.json
tracked-ok  scripts/context_manifest.py
tracked-ok  scripts/context_projection.py
tracked-ok  tests/test_context_manifest.py
tracked-ok  tests/test_context_determinism.py
tracked-ok  tests/test_context_projection.py
tracked-ok  tests/test_context_declaration_lint.py
tracked-ok  docs/CHECKLIST_SCHEMA.md
tracked-ok  skills/commander/templates/COMMANDER_SPINE.template.json
IGNORED     .agent-work/300/context/context.json
```

**#301's specific error does not reproduce here.** The committed artifact is genuinely committable,
and the one ignored path is the run-local manifest — which is *supposed* to be ephemeral and was
already flagged upward as the durability risk #301 must decide (inline vs reference). Confirmed
mechanically rather than by reading, since that is the whole lesson.

## The five "converged findings", re-graded: derived or inherited?

| # | Finding | Verdict |
|---|---|---|
| 1 | revision identity = git blob OID of LF-normalised bytes | **derived** (with one inherited premise — see below) |
| 2 | declaration = optional ordered field **on the spine task** | **INHERITED** — the *location* was never questioned |
| 3 | no globs; declaration order is content | **derived** independently, three times |
| 4 | prose stays, pinned by a lint | **derived** — each author quoted the real imperative text |
| 5 | metadata only, never file content | **NOT PANEL EVIDENCE — my own brief echoed back** |

### Finding 5 — I over-claimed, and this is the correction

I wrote "delivery, not use" and "metadata only, never file content" into the shared brief as
**fixed constraint 4**. All three authors then "converged" on it. That is not three independent
minds agreeing; that is my own constraint handed back to me three times. Presenting it to the
Admiral as one of five independently-converged findings was wrong, and it is exactly the
manufactured-consensus shape #301 hit. **Corrected: four converged findings, not five.**

The same hair needs splitting on finding 1. "Identity comes from git" was *given* — I put
`markdown-in-git` in the brief, which forecloses any non-git answer. What was genuinely derived, and
independently verified against live bytes by each author, is the sharper part: **blob OID rather
than commit SHA, LF-normalised, computed in-process without a subprocess.** That part stands as real
evidence. The framing does not.

### Finding 2 — the inherited assumption nobody tested

All three authors put the declaration on the **spine task object**, beside `constraints`/`directives`.
None asked whether it belongs there. They inherited the location from the existing schema shape the
same way #301's candidates inherited theirs from `LESSONS.md`. The alternative — a per-skill
declaration file, or a top-level map keyed by step id — was never generated by anyone.

The consequence, which surfaces only once you ask the question: **`spine.json` is instantiated per
work area from the template.** So the declaration is *copied* into every work area at init time. A
doctrine change to the declaration therefore does not reach in-flight work areas. That is arguably
*correct* — the manifest should record what that run was actually told, not what canon says today —
but it means a spine instantiated last week and the committed artifact generated from today's
template can legitimately disagree, and a naive drift check would report that as drift.

**Disposition:** not a defect in the recommendation, and not a reason to reopen the panel — the
location is still the right one, for the reason the panel never articulated (per-run fidelity beats
per-run freshness for a delivery record). But it is a **real obligation on the drift check** (issue
H's territory), and it is now stated rather than assumed: *the drift check compares canon against
the committed artifact, never against an instantiated work-area spine.*

### Finding 1's inherited premise, now closed mechanically

All three authors verified the blob-OID equality under this repo's `.gitattributes` as it stands
today: `* text=auto`, no exemption. **None checked what happens if a path is ever marked `-text` or
`binary`** — git would stop LF-normalising it, and the in-process
`sha1(b"blob %d\0" + data.replace(b"\r\n", b"\n"))` would silently diverge from `git hash-object`
for that path. A silent divergence in the identity function is the worst failure this design has.

Closed by amendment, not by prose: `g1-implement.c7` now pins the invariant with
`test -f .gitattributes && ! grep -nE '(-text|binary)' .gitattributes`. Verified in **both**
directions before freezing — exit 0 today, exit 1 after appending `*.md -text` (then restored, tree
clean). Note this is the *correct* use of the bash-negation wrapper: it wraps the thing that must
fail to match. Contrast the cold critic's finding B1, where the same wrapper was applied to a probe
and inverted the check silently.

## What this audit cost and what it bought

Two commands and one amendment. It bought: one over-claim retracted before Tommy ruled on it, one
inherited assumption converted into a stated obligation on a downstream issue, and one silent-
divergence hazard converted into a mechanical invariant. The method's blind spot is real, and the
mitigation is cheap enough that it should run on every panel, not just the ones that go wrong.

## Errata — issue numbering

Everything above originally called the drift check "issue H". Its real number is **#306**
(*Mechanize the drift check: committed projection vs regenerated canon*), and the references have
been corrected. **#307** is a different issue (*Map-first measurement: paired evidence from
representative runs*) and the surviving references to it — the transcript-ordering pairing that
answers the *use* question the manifest deliberately does not — are correct as written.

`DIT-BRIEF.md` line 92 is **deliberately left uncorrected**: it says "issue H/#307's territory",
which is wrong, but it is the frozen brief the three panel authors actually received and is kept as
the historical record of their inputs. No candidate relied on the number.
