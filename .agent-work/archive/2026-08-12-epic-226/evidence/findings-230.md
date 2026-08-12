# Findings — commander-230 (issue #230, epic-226 item D)

Worktree: `C:/Programs/constellation-wt-230` · branch `issue-230` · base `main` @ `83a31b1`
Sole writer of this file: cmd-230.

## 0. Worktree isolation (launch order, "Workspace")

```
$ py scripts/verify_worktree_isolation.py --here C:/Programs/constellation-wt-230
worktree OK: in C:/Programs/constellation-wt-230
EXIT=0
```

## 1. PR-7 — verify the launch order's claims against the code BEFORE planning

Ran the exact grep the launch order prescribes, inside the worktree:

```
$ cd C:/Programs/constellation-wt-230
$ grep -rn "@grade\|grade_lint\|guess.ledger\|guess ledger" skills/ scripts/ tests/
(no output)
```

**Result: zero hits in shipped code.** No `@grade` tag, no `grade_lint.py`, no guess-ledger
mechanism exists anywhere under `skills/`, `scripts/`, or `tests/`. The launch order's own
claim ("this is a genuine build-from-zero, not a rediscovery") is **CONFIRMED by
independent measurement**, not taken on trust.

**No honest null applies to any of the five build items.** All five are build-from-zero.
Reported here with the same rigor a null would get, per the Honest-Null Clause.

## 2. Decision-block inventory (which files genuinely hold a decision block)

Surveyed every candidate the launch order's Inherited Latitude named, plus a repo-wide
grep for `Pre-Rulings` / `Decision Anchors` / `anchors`. Verified each holds a *genuine*
decision block before treating it as an edit target.

| File | Genuine decision block? | Evidence |
|---|---|---|
| `skills/admiral/templates/LATITUDE_CONTRACT.template.md` | **YES** — `## Pre-Rulings` L51, placeholder bullet L53 | template |
| `skills/admiral/templates/LAUNCH_ORDER.template.md` | **YES** — `## Pre-Rulings` L11, placeholder bullet L13 | template |
| `skills/commander/templates/MISSION_FRAME.template.md` | **YES** — `## Decision Anchors & Decision Pressure` L26, bullets L28-29 | template |
| `skills/commander/templates/EXECUTE_PLAN.template.json` | **YES** — `anchors.decision[]` array L27 | template (JSON) |
| `skills/commander/references/commander-core.md` | **PARTIAL — see discrepancy below** | live doctrine prose |
| `skills/commander-delegated/SKILL.md` | **NO — false positive confirmed** | L24 merely *names* "Pre-Rulings" in prose, pointing at the LAUNCH_ORDER's section. No heading, no bullets, no JSON. |
| `skills/cartographer/references/map-model.md` | **NO — false positive confirmed (different sense)** | `## Decision Anchors` L252 is the MAP concept: durable rationale *files* at `docs/architecture/decisions/*.md`, one per decision, with a promote/reject lifecycle. It is the definitional source of the `decision:<id>` id-space the real blocks cite, but is not itself a list of decisions to grade. |

Both suspected false positives the launch order flagged **are** false positives. Confirmed
before touching, exactly as the Inherited Latitude required.

### Discrepancy vs the launch order (recorded, not silently absorbed)

The launch order's File Ownership grants me "the **Decision Anchors section** of
`skills/commander/references/commander-core.md`". **That section does not exist under that
name.** commander-core.md has no `## Decision Anchors` heading. The concept lives there
under two other headings — `## Decision candidates` (L112) and `## Mission frame` (L116,
which names "decision anchors and decision pressure" at L118 and the per-gate `anchors`
block at L130). The authoritative `## Decision Anchors` *definition* is in the
Cartographer's `map-model.md`, which is fenced away from me.

Disposition: this is a naming slip in the launch order, not a scope question. I write the
tag convention into the genuine decision-anchors discussion inside commander-core.md (the
Mission frame / Decision candidates area) — the same content the order intended, at its
real address. Narrow named ownership honored; nothing outside the grading topic touched.

### In-scope-adjacent, deliberately NOT edited (fenced)

`skills/commander/templates/IMPLEMENTER_HANDOFF.template.md:46` and
`skills/commander/templates/REVIEWER_HANDOFF.template.md:48` each carry a
`- **Decision anchors:** ...` field inside a "Map Anchors (inbound)" block. These are
plausible tag-convention targets but sit in `skills/commander/**` **beyond** the two files
this launch order names — fenced to #231. Not edited. Filed as a triage candidate.

## 3. #231 collision check (Pre-Ruling: file-ownership tension)

```
$ gh pr list --repo fredcai6/constellation-skills --state open --json number,title,headRefName
[]
```

**Zero open PRs.** No #231 PR touches `MISSION_FRAME.template.md` or `commander-core.md`.
No collision; the stop-and-query condition did not trigger.

## 4. Test house style (governs the acceptance tests)

`tests/` is flat, one `test_<tool>.py` per `scripts/<tool>.py`. House style, verified
against `test_agent_work_root.py` and `test_verify_worktree_isolation.py`:

- `unittest.TestCase` classes, **not** bare pytest functions; no `tmp_path` fixtures.
- Scripts loaded via `importlib.util.spec_from_file_location` from `ROOT/"scripts"/f"{name}.py"`
  (`scripts/` is not an importable package).
- CLI tested by calling `main(argv_list)` directly and asserting the return code — not by
  `subprocess.run([sys.executable, ...])`.
- `tempfile.TemporaryDirectory()` for on-disk fixtures; classes grouped by concern.

`tests/test_grade_lint.py` matches this style.

## 5. Lesson conditioning (from `.agent-work/LESSONS.md` Active)

- `verify-launch-order-claims-against-code` — **applied**, section 1. Outcome this run:
  the launch order's build-from-zero claim was accurate. This is a **third data point** for
  the lesson and the first where the launch order did *not* overstate to-build work. It
  also caught a **different** kind of launch-order/code mismatch (the non-existent
  "Decision Anchors section" in section 2) — the verify habit paid out on a naming slip
  rather than an already-shipped mechanism.
- `verify-harness-field-and-drive-real-writer` — **applied to fixture design.** The
  seeded-violation fixture plans are real Markdown/JSON decision blocks in the exact shape
  the shipped templates emit (verified against the four template files in section 2), not
  hand-simplified stand-ins that would pass even if the parser mis-read the real format.
  The round-trip test drives the **real shipped template text** through the linter.
- `test-harness-concurrency-failsafe` / `observe-midprocess-state-not-via-end-output` —
  **do not apply.** `grade_lint.py` is a single-pass static scanner: no threads, no
  subprocesses, no long-running or mid-process state to observe. Confirmed, not assumed.

## 6. Context substitution (recorded, per the context step's own imperative)

This repo carries **no `docs/agents/` overlay** — it is the skill-source repo. So
`ORCHESTRATOR_CONTEXT.md`, `GLOSSARY.md`, and `engine-config.json` are absent **by design**.
Substituted: the launch order's Inherited Context block (its declared charter-lite carrier),
`LATITUDE_CONTRACT.md`, and the bundled `global-orchestrator.md` / `global-everyone.md`.
The engine degrades the missing `config_ref` to built-in defaults — sanctioned degradation;
the overlay was **not** created.

No architecture map (`docs/architecture/`) covers `scripts/` tooling, so the map-first read
resolves to the doctrine files above.

## 7. Design-it-twice disposition

- **Pre-empted** for the grammar/schema and the executor decision rules — ratified by the
  archived 3-agent panel (`dit-I2-caller-RESULT.md`), pasted verbatim into the launch order.
  Not re-derived; implemented as frozen.
- **Run by me** for the one load-bearing interface the panel left open: `grade_lint.py`'s
  CLI surface, output format, and the parse strategy for locating recognized decision
  blocks. See section 8.

## 8. Parse-strategy design (the interface the panel left to me)

Recorded as a design decision with its untaken roads, since the panel did not rule on it.

**Chosen: anchor-first scan, block-scoped classification.**
`@grade:` is the sole greppable anchor (invariant 7). The scanner finds decision-bearing
lines first, then asks which recognized block each sits in — rather than parsing Markdown
structure top-down and hunting for grades within it.

Why: it makes locality mechanical. A grade can never be found outside the decision it
grades, because the grade is located *from* the decision line (Markdown: the tag is a child
line of the decision bullet; JSON: the tag is inside the decision string itself). A
structure-first parser would have to re-associate grades with decisions after the fact —
exactly the drift invariant 7 forbids.

**Untaken roads (recorded, not built):**
- *Full Markdown AST parse* — rejected: adds a dependency to a repo whose scripts are
  stdlib-only, and buys nothing, since the grammar is line-oriented by construction.
- *Structure-first block parse* — rejected per the locality argument above.
- *Tolerant grade-anywhere scan* (accept `@grade:` on any line, no block requirement) —
  rejected: invariant 1 scopes grading to recognized blocks; a grade in free prose would
  silently count toward the inventory and dilute the FAIL signal.

**Degradation rule (from the grammar): only `@grade: <tier>` is hard-required.** Every
other field's absence degrades — `settle:` missing on a guess is a FAIL by invariant 4,
provenance missing on settled is a WARN by invariant 3, absent `leans` is legal by
invariant 5 — but a malformed field never crashes the scanner. This is the "fail visibly
rather than emit plausible wrong output" inherited doctrine applied to a linter: an
unparseable tag reports as a violation, never as a silent pass.

## 9. THE FORK — where each half lives

Item 3's ratified fork ("lint loud, execute safe") splits across two homes:

- **Lint loud** = `grade_lint.py`'s exit code. Ungraded decisions in recognized blocks FAIL
  pre-flight, so new plans cannot ship ungraded. This half is **executable**.
- **Execute safe** = doctrine prose. At execution time, an ungraded decision reads as
  `settled` — legacy plans behave exactly as today, and the tag only ever *buys* freedom,
  never removes it. This half is **doctrine-observed-at-first-use**, per the issue's own
  acceptance line.

**Critically: no runtime tier-checking logic goes into `scripts/checklist_engine.py`.**
That file is #227's sole writer this wave and is fenced from me. The launch order's
project-specific Pre-Ruling is explicit that item 2 and item 3 are *prose describing rules*,
not engine code. Honored: `checklist_engine.py` was never opened for writing.

## 10. Deferred, per the issue's own boundaries (NOT built)

Named untaken roads, recorded so a later reader does not mistake them for omissions:
numeric confidence · depends-on edges · a stored ledger table · per-decision revisit
override (all four are the issue's explicit out-of-scope list) · cross-artifact `leans` and
`expires` (both deferred PENDING Thread C / issue H #234 — implementing either here would
be scope creep into a different thread).

The issue's **burden checkpoint** is also recorded, not resolved: after the first epic that
runs fully graded, review actual authoring burden vs value and keep/trim.
