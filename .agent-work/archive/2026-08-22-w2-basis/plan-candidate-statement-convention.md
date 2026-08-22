# Candidate plan — constraint: `statement-convention`

Work-id: `w2-basis` (epic 569, wave 2). Author: independent plan-alternative,
no shared memory with sibling candidates. Target template:
`skills/commander/templates/COMMANDER_SPINE.template.json` (19 `check: null`
conditions confirmed at this run's HEAD: 11 postconditions + 8
preconditions — the mission frame's "19 postconditions" is loose language;
the real split is 11 post / 8 pre, both disjoint id namespaces `attest`
already treats identically per `checklist_engine.py:3425-3430`). Engine:
`scripts/checklist_engine.py`.

## 1. The design

**No new Condition schema field.** The basis is authored as a fixed suffix
appended to the existing `statement` string, using a delimiter distinct from
the corpus's one live precedent (`generate_spine.py`'s
`-- QUALITATIVE: {because}`, which is explicitly out of scope — it's in
`generate_spine.py`):

```
<original statement text> -- BASIS: <kind>:<locator>
```

Three candidate `kind`s, evaluated below against the real 19 conditions:

- `file:<path-or-glob>[#<field-path-or-grep>]` — a filesystem locator. The
  attest `--note` must supply an actual path; the engine checks (a) the path
  matches the authored glob, (b) the path exists on disk relative to the
  repo root, and (c) when `#field` is present, the named field/grep target
  is present in that file (e.g. `file:.agent-work/<work-id>/execute.json#tasks.*.status=complete`).
- `evidence:<evidence_type>` — the attest note (or `--evidence <id>`) must
  resolve to an evidence item already attached to *this checklist*, of the
  named type, via the engine's existing `_find_evidence` lookup — literally
  reusing the `artifact`-check machinery that already exists for
  `check.kind == "artifact"`, just entered from the qualitative branch of
  `attest` instead of a schema-level `check` object.
- `command:<shell-locator-pattern>` — the attest note must contain a string
  matching a locator pattern derived from a named command (e.g. a commit
  SHA that could be independently verified with
  `git branch -r --contains <sha>`). **Flagged unsafe below — see §2.**

`render_human` needs **zero new code**: it already prints
`f"  {c['id']} [unmet] {c['kind']} — {c['statement']}"` per open condition
(`checklist_engine.py:2726`), and the BASIS clause lives inside `statement`,
so it renders in full the moment it's authored. This is the one part of the
mission's premise I can confirm firsthand rather than take on faith — I
grepped the 19 real statements for `--` collisions (below) and read
`render_human` directly; the render half of "render AND require" is real,
free, and already shipped for this template.

## 2. The locator-count measurement (real 19 conditions, not hypotheticals)

Full statement text for every one of the 19 `check: null` conditions was
pulled from the shipped template and each `kind` above applied by hand.
Results, condition by condition:

| # | condition | statement (short) | best locator kind | verdict |
|---|---|---|---|---|
| 1 | `init.c1` | engine session lease claimed | `file:.agent-work/<work-id>/spine.json#lease.claimed_by=commander` | **genuine** |
| 2 | `context.c1` | context/glossary/config loaded; map read | — | **degenerate** (a reading act, no artifact) |
| 3 | `understand.p1` | baseline context loaded | — | **degenerate** (sequencing gate) |
| 4 | `plan.p1` | ask confirmed | `evidence:user-decision` (reuse `understand.c1`'s attached evidence) | **genuine** |
| 5 | `plan.c1` | mission frame produced (or skipped-as-trivial) | `file:.agent-work/<work-id>/MISSION_FRAME.md` | **genuine** |
| 6 | `plan.c2` | execute.json authored, gates carry anchors, every file/decision-class owns a gate | `file:.agent-work/<work-id>/execute.json` | **partial** — existence+shape checkable, semantic sufficiency ("every file/decision-class") is not |
| 7 | `plan.c4` | plan-alternatives run BEFORE execute.json, at named paths | `file:.agent-work/<work-id>/plan-candidate-*.md` + `PLAN_ALTERNATIVES.md` | **partial** — file existence checkable; the statement's own text says ordering is "NOT machine-verified", and a locator can't fix that |
| 8 | `plan.c5` | cold critic run, findings at PLAN_CRITIC.md | `file:.agent-work/<work-id>/PLAN_CRITIC.md` | **partial** — same ordering caveat as c4 |
| 9 | `execute.p1` | plan approved; headroom ensured; skill reloaded | `evidence:user-decision` (plan approval sub-clause only) | **mixed** — 1 of 3 sub-claims locatable, "skill reloaded" and "headroom ensured" are in-session acts with no artifact |
| 10 | `execute.c1` | every gate closed with integrated evidence | `file:.agent-work/<work-id>/execute.json#tasks.*.status=complete` | **genuine** (but see §5 — arguably should just be a real `command` check instead) |
| 11 | `reconcile.p1` | execute complete | — | **degenerate** (sequencing gate) |
| 12 | `reconcile.c1` | map reflects implemented changes | `file:docs/**` (target path not knowable at authoring time, only its glob) | **partial** — locatable in kind, not in a fixed path |
| 13 | `triage.p1` | reconcile complete | — | **degenerate** (sequencing gate) |
| 14 | `triage.c1` | every triage candidate routed or recorded | `file:.agent-work/<work-id>/execute.json#triage_candidates` + issue refs | **partial** — needs an explicit empty-case escape |
| 15 | `review.p1` | triage complete | — | **degenerate** (sequencing gate) |
| 16 | `feedback.p1` | run summary accepted | — | **degenerate** (sequencing gate) |
| 17 | `archive.p1` | workflow feedback recorded | — | **degenerate** (sequencing gate) |
| 18 | `archive.c2` | branch committed and pushed | `command:git branch -r --contains <sha>` / re-expressible as `file` via `git log` output | **genuine** — strongest candidate in the whole set |
| 19 | `archive.c3` | spine_close authorized as sole final transition | — | **degenerate** (forward-looking procedural authorization, not a fact about the world) |

**Tally**: 5 genuine / 5 partial / 1 mixed / 8 fully degenerate, out of 19.

That is **10 of 19 (53%) that get a real, non-decorative locator** (genuine
+ partial, counting the mixed one as half), and **8 of 19 (42%) that
categorically cannot** under this constraint, no matter which locator kind
is tried. This is not a marginal miss — it is a clean structural pattern,
not noise: **all 8 fully-degenerate conditions are either (a) a pure
step-sequencing precondition restating "the previous step completed"**
(`understand.p1`, `reconcile.p1`, `triage.p1`, `review.p1`, `feedback.p1`,
`archive.p1` — six of the eight), **(b) an in-session reading act with no
artifact trace** (`context.c1`), **or (c) a forward-looking procedural
authorization claim** (`archive.c3`). None of the three candidate locator
kinds — file, evidence, command — can express any of these, because they
are not claims about evidence in the world; they are claims about the
engine's own task-graph state or about intent, and no locator convention
fixes that. See §5 for what this implies for scope.

## 3. `attest()` code sketch

```python
_BASIS_RE = re.compile(r"--\s*BASIS:\s*(file|evidence|command):(.+)$")

def _resolve_basis(kind: str, locator: str, note: str | None,
                    evidence_id: str | None, cl: dict) -> str | None:
    """Return None if the note/evidence discharges the basis, else a
    human-readable reason it does not (never raises itself -- caller
    decides report-only vs blocking)."""
    if kind == "file":
        candidate = evidence_id or note
        if not candidate:
            return "no path supplied in --note"
        path, _, field = candidate.partition("#")
        if not fnmatch.fnmatch(path, locator.split("#")[0]):
            return f"{path!r} does not match required locator glob {locator!r}"
        if not (repo_root / path).exists():
            return f"{path!r} does not exist on disk"
        # optional: field-path/grep check against locator's '#field' clause
        return None
    if kind == "evidence":
        ev_id = evidence_id or note
        ev = _find_evidence(cl, ev_id) if ev_id else None
        if ev is None or ev.get("type") != locator or ev.get("superseded"):
            return f"no attached, non-superseded {locator!r} evidence resolves from {ev_id!r}"
        return None
    if kind == "command":
        # NOT implemented for v1 -- see tradeoffs. Always reports unmet.
        return "command-kind basis is report-only-only in this build; not enforceable from a pasted note"
    return None  # unrecognized kind: treat as no basis, legacy behavior

def attest(cl, iid, cond_id, which, note, evidence_id=None):
    ...
    chk = c.get("check")
    if chk is None:
        warning = None
        m = _BASIS_RE.search(c["statement"])
        if m:
            kind, locator = m.group(1), m.group(2).strip()
            problem = _resolve_basis(kind, locator, note, evidence_id, cl)
            if problem:
                if _basis_enforcement_mode(cl) == "blocking":
                    raise EngineError(f"{cond_id}: basis unmet -- {problem}")
                warning = f"[basis-report-only] {cond_id}: {problem}"
        c["satisfied"] = True
        c["satisfied_by"] = note or "attested"
        msg = f"attested {iid}.{cond_id}"
        return f"{msg}\nWARNING: {warning}" if warning else msg
    ...
```

`_basis_enforcement_mode` reads a new, optional top-level checklist/engine-
config key (e.g. `engine-config.json: {"basis_enforcement": "report-only"}`,
default `"report-only"` when absent) — this is the promotion trigger: a
one-line config flip, not a code change, per
`ruling-report-only-names-its-trigger`.

**Is this genuinely mechanical, or fragile/gameable?** Split by kind:

- **`file` and `evidence` kinds are real.** They don't trust the note's
  *text* — they use the note as a pointer and then independently resolve
  it (`Path.exists()`, `_find_evidence`). An agent cannot satisfy either by
  pasting the statement back: a copied statement is not a path that exists
  on disk, and it is not an evidence id in the checklist's evidence list.
  This is the same trust shape the existing `check.kind == "artifact"` path
  already uses, just reached from the qualitative branch.
- **`command` kind is NOT real, and I am not shipping it.** The only thing
  `attest()` can see is the note *string*. If the required locator is "a
  commit SHA present on the remote branch", checking that the note *looks
  like* a SHA (matches a hex regex) proves nothing — an agent can fabricate
  40 hex characters, or paste a stale SHA from days ago, and the regex is
  satisfied while the underlying fact is false. The only way to make this
  kind honest is to have the engine **run** the command itself against the
  note's argument — at which point it is no longer "parse free text for a
  locator", it is a `check.kind == "command"` condition, and the entire
  basis/statement-convention apparatus is redundant. I'm flagging this
  explicitly rather than quietly shipping a fake-mechanical `command` kind:
  **`archive.c2` and `execute.c1`, the two conditions where a `command`-
  shaped locator looks most attractive, are exactly the two conditions
  where the honest fix is "promote to a real `check.kind: command`",
  not "add a basis convention".** See §5.

## 4. Gate sequence (Commander `execute.json`-shaped)

Each gate: imperative (what to do), close criteria, required evidence,
constraints.

**g1-red-proof** — *Prove the gap exists before touching the engine.*
- Imperative: write a pytest test against a throwaway checklist fixture
  (cloned shape from `COMMANDER_SPINE.template.json`, not the live
  template) with one `check: null` condition carrying a `-- BASIS: file:...`
  suffix; call `attest()` with a garbage note (`"looks good"`); assert it
  currently SUCCEEDS (documents today's bare-assertion acceptance,
  byte-for-byte the behavior the mission frame names at
  `checklist_engine.py:3431-3434`).
- Close criteria: the test exists, is collected, and passes RED-as-
  documentation (i.e. it currently passes because the gap currently exists;
  it will need inverting once g2 lands — track that explicitly, don't
  silently flip its assertion later).
- Required evidence: the test file path + a passing pytest run.
- Constraints: fixture-only; never touches the live template in this gate.

**g2-engine-change** — *Implement the parse + validate branch, report-only
default.*
- Imperative: add `_BASIS_RE`, `_resolve_basis`, `_basis_enforcement_mode`
  and the new branch inside `attest()`'s `chk is None` arm in
  `checklist_engine.py`, exactly as sketched in §3. Ship only `file` and
  `evidence` kinds as capable of promotion to blocking; `command` kind
  parses (for forward compatibility / documentation) but
  `_resolve_basis` always returns a report-only-only "not enforceable"
  problem for it — never silently reaches "satisfied with no warning".
  Default `basis_enforcement` to `"report-only"` when the config key is
  absent.
- Close criteria: `attest()` on a non-BASIS-bearing `check: null` condition
  is byte-for-byte unchanged (regression floor: every existing shipped
  template with no BASIS suffix must attest exactly as before).
- Required evidence: diff of `checklist_engine.py`; a targeted pytest run
  covering the unchanged-behavior regression.
- Constraints: no change to `Condition` schema, `docs/CHECKLIST_SCHEMA.md`
  Condition table, `render_human`, or any producer under
  `generate_spine.py` (out of scope).

**g3-invert-red-to-green** — *The actual red-then-green proof of refusal.*
- Imperative: invert g1's fixture test: after g2, the same garbage-note
  attest call must now return a `WARNING: [basis-report-only] ...` string
  (not raise) under default config, and must raise `EngineError` under a
  fixture config with `basis_enforcement: "blocking"`. Add a matching
  positive case: a note that correctly resolves (existing file path /
  attached evidence id) attests cleanly with no warning, for both `file`
  and `evidence` kinds.
- Close criteria: 4 new passing tests — refuse-report-only, refuse-
  blocking, accept-file, accept-evidence — plus g1's original test now
  either removed or asserted as "documents the pre-fix state, superseded by
  this gate's inversion" so nobody reads it as current behavior later.
- Required evidence: pytest run output naming all four tests green.
- Constraints: fixture-only again; this gate never edits the shipped
  template. `ruling-red-proof-pinned-to-shipped-revision` — the red half
  must cite the exact pre-g2 commit SHA it was captured against.

**g4-author-basis-into-template** — *Apply the measurement from §2 to the
real template.*
- Imperative: hand-edit `COMMANDER_SPINE.template.json` surgically (no
  `json.load`/`json.dump` round-trip, per doctrine) to append the BASIS
  clause to the 10 conditions rated genuine/partial in §2 (`init.c1`,
  `plan.p1`, `plan.c1`, `plan.c2`, `plan.c4`, `plan.c5`, `execute.c1`,
  `reconcile.c1`, `triage.c1`, and the locatable third of `execute.p1`'s
  compound statement — rephrase that one condition into two, a locatable
  "plan approved" clause and a separate non-BASIS clause for the other two
  sub-claims, since a compound statement can't carry one basis for three
  unrelated facts). Do **not** invent a fake basis for the 8 fully-
  degenerate conditions; leave them as plain `check: null` with no BASIS
  suffix, and record the reason (from §2's table) as a follow-on
  triage candidate rather than papering over it.
- Close criteria: `grep -c 'BASIS:'` on the shipped template returns the
  agreed count (9 or 10 depending on the `execute.p1` split decision);
  `python scripts/checklist_engine.py current <work-id>` (fresh-process,
  per the dogfooding constraint — never through this run's own bound door)
  against a throwaway spine instantiated from the edited template shows the
  BASIS clause rendering verbatim in `current`'s output for an active gate.
- Required evidence: template diff; fresh-process CLI output pasted into
  the gate's evidence.
- Constraints: `skills/commander/templates/COMMANDER_SPINE.template.json`
  only; sync `.agent-work/templates/` overlay + `.baseline` copy per the
  mission frame's Inherited Context note if that overlay mirrors this file.

**g5-wire-report-surface** — *Give the report-only warning somewhere it can
fail, per `ruling-no-new-unwired-checker`.*
- Imperative: g3's pytest assertions on the WARNING string ARE the wired
  surface (pytest runs in CI and can fail) — no additional plumbing is
  strictly required. Additionally, add one pytest test that attests every
  one of the 9-10 authored BASIS conditions on a throwaway spine
  instantiated from the real (post-g4) template with intentionally-bad
  notes, asserting each one returns a `[basis-report-only]` warning — this
  is the check that would catch a future edit silently loosening a BASIS
  locator back into unconditional acceptance.
- Close criteria: the new template-level test passes, is named
  discoverably (e.g. `test_commander_spine_basis_conditions_refuse_bare_note`),
  and fails loudly (not skipped, not xfail) if any authored BASIS clause
  stops being enforced.
- Required evidence: pytest run naming this test.
- Constraints: this test must run against the real shipped template file,
  not a fixture copy, so a future template edit trips it directly.

**g6-reconcile-docs** — *Fold the new convention into the structural
record (no packet map exists for this repo — direct doc reconcile per the
mission frame's DEGRADED substitute path).*
- Imperative: add a subsection to `docs/CHECKLIST_SCHEMA.md`'s Condition
  section documenting the `-- BASIS: <kind>:<locator>` convention, its two
  enforceable kinds (`file`, `evidence`), the explicitly-unenforceable
  `command` kind and why (§3's gameability finding), the report-only
  default and its config-flag promotion trigger, and a pointer to
  `COMMANDER_SPINE.template.json` as the reference example.
- Close criteria: doc diff reviewed; no other doc references the old
  "decorative" `-- QUALITATIVE:` precedent as if it were this mechanism.
- Required evidence: doc diff.
- Constraints: `docs/CHECKLIST_SCHEMA.md` only; do not touch
  `docs/CHECK_SCRIPT_CENSUS.md` (wave-1 committed prior evidence, load-
  bearing, not this wave's file).

**g7-triage-degenerate-findings** *(optional, present to human before
filing)* — *Route the 8-fully-degenerate finding, not bury it.*
- Imperative: present a triage candidate: "6 of the 8 fully-degenerate
  conditions are the identical shape — a precondition restating '<previous
  step> complete'. That shape is better served by a `check.kind:
  task-status` engine primitive (check the referenced task's own status
  field) than by any locator convention, qualitative or structured. Worth
  a separate, engine-first fix outside this wave's ONE-template scope."
  Get explicit human approval before filing as an issue, per the triage
  step's own gate.
- Close criteria: recorded, not auto-filed (per `auto_file_discrepancies:
  false`); human decision attached as evidence.
- Required evidence: user-decision evidence item.
- Constraints: recommendation only; no code in this gate.

## 5. Tradeoffs

- **Depth**: shallow — one regex, one validation function, one new branch
  in `attest()`'s existing qualitative arm. No new schema, no new producer
  code, no `generate_spine.py` touch. This is the cheapest-to-implement of
  the plausible designs.
- **Locality**: excellent, by construction — every line of the engine diff
  lives inside `attest()`; every authoring change is an append to an
  existing string field on the one target template. Nothing else in the
  corpus (other 19 templates, `generate_spine.py`, `specs/`) needs to know
  this convention exists, which is exactly what
  `ruling-basis-lives-in-hand-written-templates` and
  `ruling-engine-first-backfill-where-it-earns-it` ask for.
- **Seam placement**: correct and confirmed, not assumed — `render_human`
  really does need zero new code (verified by reading
  `checklist_engine.py:2726` directly: the full `statement` string is
  already interpolated per open condition), and `attest()` really is the
  refusal surface the mission frame names. This candidate's core claim
  (render is free) is not a hope, it's read off the current source.
- **Testability**: good for the two kinds actually shipped (`file`,
  `evidence`) — both resolve against real, inspectable state (filesystem,
  evidence list), so positive/negative fixtures are simple and
  deterministic. Poor-to-absent for `command`-kind, which is why it ships
  unenforceable rather than half-enforced.
- **Robustness vs. a structured sibling field** (the road not taken by this
  constraint, on purpose): this design is optimized for minimal footprint,
  not for robustness. Parsing a human-legible sentence for a
  machine-meaningful clause is inherently more fragile than a typed field:
  today's 19 statements happen to contain no stray `--` that would collide
  with the `-- BASIS:` delimiter (verified: `grep`-checked every
  `check: null` statement in the live template; the only `--` occurrences
  in the whole file are in `context.c2`, `plan.c6`, `archive.c2b` — all
  three are `command`-checked, not qualitative, so no collision exists
  *today*), but nothing stops a future edit to one of these 19 statements
  from introducing a stray `--` that the regex misparses. A structured
  `"basis": {"kind": ..., "locator": ...}` sibling field would not have
  this failure mode at all, at the cost of touching the Condition schema,
  `docs/CHECKLIST_SCHEMA.md`'s field table, and the `TaskFieldCompleteness`
  fixture in `tests/test_checklist_engine.py` — precisely the footprint
  this constraint was asked to avoid. If the winning plan cares more about
  long-term robustness than about minimizing this wave's footprint, the
  sibling-field candidate should be weighed against this one on exactly
  this axis, not dismissed for being "more schema change" without
  comparing what that schema change buys.

## 6. Honest verdict

The statement-convention constraint **partially works** against the real
19 conditions, and the honest split matters more than the headline count:

- **10 of 19 (53%)** get some form of real, non-decorative locator (5
  genuine, 5 partial/caveated). That is a genuine win over the status quo
  for those 10 — a bare assertion is refused report-only, and the refusal
  is grounded in something a stranger could actually re-check (a file that
  exists, an evidence id that resolves).
- Of those 10, the **two strongest** (`archive.c2`'s git-SHA-on-remote,
  `execute.c1`'s all-gates-closed-internal-state) are so mechanically
  clean that the honest recommendation is not "give them a basis
  convention" but "promote them to a real `check.kind: command` /
  internal-state check and remove them from the qualitative set entirely."
  Shipping a basis convention for these two would be strictly weaker than
  just checking them, and would invite exactly the gameable
  paste-the-statement-back failure mode named in the launch order.
- **8 of 19 (42%) cannot express a real locator under any of the three
  candidate kinds**, and this is not scattered noise — six of the eight are
  the identical shape (a precondition asserting "the previous step
  completed"), which is a task-graph-state claim the engine already tracks
  and could check directly with a different, simpler primitive, not a
  basis/locator problem at all. `context.c1` (a reading act) and
  `archive.c3` (a forward-looking authorization) are two more shapes this
  convention — or arguably any evidence-locator convention — cannot reach,
  because they aren't claims about artifacts in the world.

Net: this candidate should ship for the ~9 conditions where it earns its
keep (`plan.c1/c2/c4/c5`, `init.c1`, `plan.p1`, `reconcile.c1`,
`triage.c1`, and the locatable third of `execute.p1`), explicitly should
NOT invent a `command` kind or force a fake basis onto the other 8, and
should hand back — as a named, human-triaged finding, not a silent gap —
the observation that those 8 want a different fix (`task-status` check
primitive) outside this wave's scope. That is a complete, useful answer to
`decision:locator-definition-is-yours`: real numbers, a clean structural
reason for the failures, and an honest statement that "most conditions
degenerate" is FALSE (53% get a real locator) while "a meaningful chunk
categorically can't, for a specific and explainable reason" is TRUE.
