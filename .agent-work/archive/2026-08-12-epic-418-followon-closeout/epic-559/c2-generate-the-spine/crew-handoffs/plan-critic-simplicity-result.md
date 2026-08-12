# Cold plan critique — lens: simplicity / YAGNI

**Work id:** `epic-559/c2-generate-the-spine` · **Read:** `CANDIDATE_PLAN.md`, `MISSION_FRAME.md`, plus
the repository source the plan names (`scripts/validate_spine.py`, `scripts/checklist_engine.py`,
`scripts/init_work_area.py`, `docs/CHECKLIST_SCHEMA.md`, the shipped `skills/*/templates/*.json`) and
the closest in-epic precedent, `.agent-work/epic-559/c1-spine-lint/` (the oracle this plan imports).
Did not read the three `plan-alt-*-result.md` candidates or the launch order, per the handoff.

Five findings. None BLOCKING — the design is sound on its own terms; every finding below is "this
wave is carrying more surface than this wave's own proof exercises."

---

## SERIOUS — g1 and g2 are one gate wearing two crew dispatches

**What is wrong.** The plan sequences the pure compiler (g1) and the CLI/probes/refusal (g2) as two
separate Commander-level gates, each a full `crew` gate ("close criteria... crew") — a fresh
implementer handoff, a fresh cold-reviewer dispatch, a fresh rework loop, for each.

**Evidence.** `.agent-work/epic-559/c1-spine-lint/HANDOFF.md` is the closest precedent in this same
epic: it built `scripts/validate_spine.py` — comparable or greater scope than g1+g2 combined (all four
falsifiability fault detectors, the subprocess-based pytest-collection probe, shape faults, the CLI,
`discover_checklist_templates`). That entire module shipped under **one** Commander-level
implement-then-cold-review cycle (`.agent-work/epic-559/c1-spine-lint/IMPLEMENTER_PLAN.json`,
`REVIEW_SURVEY.json`, one rework round producing `REVIEW_SURVEY2.json`) — not two. C1's own internal
spine had "four gates," per its handoff, but those are sub-steps inside one crew dispatch, not four
separate Commander-level crew-dispatch-plus-cold-review cycles.

**What it costs.** A full extra implementer dispatch + cold-reviewer dispatch + possible rework loop —
the most expensive unit of work this process has — for a boundary the plan's own ordering argument
("the pure compiler is proven before anything depends on it") does not require to be a *separate crew
gate*; it only requires the compiler to be written and tested before the CLI imports it, which one
crew can do in one dispatch exactly as C1's crew wrote shape-faults before wiring the CLI that calls
them, inside one gate.

**Smallest fix.** Merge g1 and g2 into one crew gate ("the generator: pure compiler, CLI, probes,
refusal") whose close criteria is the union of both rows — unit tests over plain dicts, the
`render_human` handback-rendering test, `validate_spine.py --sweep` unchanged, the control-pairing
refusal proof, and each probe demonstrated once against a defect-shaped fixture and once against a
sound one. Six gates become five; four crew gates become three.

---

## SERIOUS — the pure/impure module split contradicts this repo's own precedent

**What is wrong.** The plan proposes two files: `scripts/spine_spec.py` (pure) and
`scripts/generate_spine.py` (impure CLI/IO), justified as a testability seam.

**Evidence.** The two modules the plan itself points to as authority both keep the pure/impure split
at **function** granularity inside **one file**, not across two modules:
- `scripts/checklist_engine.py` (3352 lines): `evaluate_git_change_policy` (line 579, pure —
  `docs/CHECKLIST_SCHEMA.md`:195 calls it "fully unit-testable without a working tree") sits in the
  same file as `_collect_changed_files` (line 681, impure — shells out to `git diff`) and `main()`
  (line 3266).
- `scripts/validate_spine.py` (665 lines, the module this plan's CLI imports and calls as "the literal
  last word"): the pure `_fault_*` functions (`_fault_all_null`, `_fault_artifact_no_match`,
  `_fault_unresolved_placeholder`) sit in the same file as the impure `_collects_zero` /
  `_resolve_interpreter` (subprocess-calling) and `main()`.

Neither precedent module needed a second file to keep its pure core independently unit-testable with
plain dicts — `docs/CHECKLIST_SCHEMA.md` cites `evaluate_git_change_policy`'s testability as a fact
about the *function*, not about which file it lives in.

**What it costs.** A second file to keep in sync, a second import to wire (`generate_spine.py` must
import every public name it needs from `spine_spec.py`), and a module boundary that buys nothing this
repo's own established pattern doesn't already buy at the function level.

**Smallest fix.** One file, `scripts/generate_spine.py`: `compile_spec`/`compile_condition` written as
free functions that touch no `Path`, `open`, or `subprocess` (enforced by the same convention the two
precedent files already use, not by a file boundary), the CLI and probes below them, `main()` last. If
g1/g2 merge (finding above), this stops being two questions.

---

## SERIOUS — `git_change_policy` earns nothing this wave; it is speculative generality by the plan's own table

**What is wrong.** The kind table's own "defect it addresses" column reads `—` for
`git_change_policy` — it is the only row with no defect behind it. The plan's "Known weaknesses"
section already concedes neither role spec uses it.

**Evidence.** Cross-checked against `docs/CHECKLIST_SCHEMA.md:168-195`: `git-change-policy`'s inline
policy is not a small shape — `mode`, `max_file_bytes`, `deny_globs`, `allow_globs`,
`require_human_waiver_for_binary`, plus an `override_policy` sub-object (confirmed live in
`skills/commander/templates/COMMANDER_SPINE.template.json`'s closeout gate, 7 fields on one check).
That is real TOML-schema surface, real `compile_condition` branching, and — per the plan's own
"Three-way guard fixtures" rule — a VIOLATING/INNOCENT/ACCEPTED_FALSE_ALARM fixture set, all for a kind
that g3's actual deliverable (`specs/implementer.spine.toml`, `specs/reviewer.spine.toml`) never
instantiates and g4's real crew-dispatch proof therefore never exercises. `MISSION_FRAME.md`'s four
named acceptance-example defects (unquoted selector, zero-collect, wrong invocation, wrong population)
map to `pytest`, `script`, and `population`; none maps to `git_change_policy`.

**What it costs.** Compiler surface, TOML-schema surface, and a fixture set proven only by contrived
unit tests this wave writes for itself — the exact "recreates the defect one level removed" risk the
plan's own "Known weaknesses" section names for the *other* un-oracled probes, but here for a kind with
no defect motivating it at all.

**Smallest fix.** Cut `git_change_policy` from this wave's closed vocabulary. Add it in the wave that
actually authors a closeout-gate spec, against a real caller, exactly as `A` (per the plan's own
recommendation writeup) showed what dropping a kind costs when there *is* a caller. Deletion-test
result: the complexity vanishes — it does not reappear in g3 or g4, because nothing there calls it.

---

## MINOR — `recorded` is `artifact` wearing a different name

**What is wrong.** `recorded`'s author-facing field list is empty (the table's "author writes" column
is `—`), and it compiles to `artifact` / `user-decision`.

**Evidence.** `scripts/validate_spine.py:453` already special-cases exactly this shape:
`ACCEPTED_ARTIFACT_TYPES_WITHOUT_MATCH = {"user-decision"}` — a bare (no-`match`) `artifact` check with
`evidence_type: "user-decision"` is already legitimate to the oracle, with no separate kind needed. An
author writing `kind = "artifact", evidence_type = "user-decision"` directly produces the identical
compiled JSON `recorded` would produce, with zero information loss.

**What it costs.** One more entry in the closed vocabulary to document, dispatch in
`compile_condition`, and test, for a shape the `artifact` kind already expresses losslessly.
Deletion-test result: vanishes cleanly, does not reappear — no caller needs `recorded` specifically,
only what it compiles to.

**Smallest fix.** Drop `recorded`; document the `artifact` + `evidence_type = "user-decision"` +
no-`match` combination as the qualitative-but-closes-on-something-real pattern instead. Seven kinds
become five (`qualitative`, `pytest`, `script`, `population`, `artifact`), each with a defect or a
mission-frame acceptance example behind it — matching the count the handoff's own framing points at.

---

## MINOR — TOML is the one format precedent-break in the corpus, for an ergonomics gain the plan doesn't demonstrate

**What is wrong.** The spec format is TOML; the generator's output, the 20 shipped templates it is
diffed against in g3, `config_ref`, and every other on-disk artifact `checklist_engine.py` or
`validate_spine.py` touches are JSON.

**Evidence.** `find . -iname "*.toml"` returns nothing in this repository today — TOML has zero
precedent here. `find skills -name "*.json" | wc -l` returns 20. `compile_spec(spec: dict) -> dict` is
already format-agnostic per the plan's own module shape (the CLI hands it a plain dict) — swapping
`tomllib.load(f, "rb")` for `json.load(f)` in the one impure call site is the entire cost of dropping
TOML, and it removes the only new stdlib dependency and the only file-extension convention this run
would introduce that nothing else in the repo uses.

**What it costs.** Not a functional risk (`tomllib` is stdlib, verified at 3.12.3), but it is
complexity with no demonstrated payer: the plan does not show a spec author for whom TOML's
array-of-tables syntax over nested JSON was the deciding ergonomics factor, and every downstream
consumer (the oracle, the diff-against-shipped-templates step in g3, the engine itself) already speaks
JSON only.

**Smallest fix.** `specs/<role>.spine.json` instead of `.toml`. If the array-of-tables ergonomics are
judged worth keeping despite the corpus having no precedent for them, that judgment belongs in
`DESIGN_NOTE.md` (g0) as a named, argued choice — right now the plan states TOML as settled fact
("There is no raw-command field anywhere in the format" carries the weight; the file format doesn't)
without weighing it against the alternative that costs one line to switch to.

---

## Checked, not a defect — `claims_rollup` is not redundant with the per-gate `directives.claim`

The handoff asked me to check whether `claims_rollup` is a third mechanism for one property, redundant
with per-gate claim rendering plus the auto-injected postcondition. Read `render_human` directly
(`scripts/checklist_engine.py:2141-2178`): it renders `directives` only for `view["active"]` — the
**single currently-active** task. Once a gate advances past `g1`, `g1`'s own `directives.claim` is no
longer rendered by `current` for anything after it; nothing else re-surfaces it. `claims_rollup` on the
terminal gate is therefore the *only* channel by which a reviewer reading the terminal state sees an
earlier gate's large claim — not a redundant third mechanism, but the only one with the right lifetime.
Not a finding; reported per the handoff's instruction to say so when the answer is "checked, and it
holds."

One adjacent, weaker observation, offered as an opinion rather than a finding (I did not verify it
against a live render): the auto-injected escalation *postcondition*'s own `statement` field could
plausibly carry the claim text itself, which would make the separate `directives.claim` entry on the
same gate redundant with it — both render on the active gate's `current` output. I did not check
whether this loses anything `directives.claim`'s structured shape gives a downstream reader (e.g. the
rollup's own construction), so I am not ranking it.
