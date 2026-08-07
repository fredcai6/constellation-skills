# Mission frame — issue #104 (constellation-curator, measure-then-mend)

**Map note (shrunk frame, said plainly):** this is a skill-source repo with no
`docs/architecture/` packet map and no `docs/agents/` overlay. The structural
record is the skills corpus itself plus `docs/*.md` design docs and
`install_constellation.py`. There is no map to distrust; the frame is built from
direct reads of the install wiring, example skills, and the test suite. No
scout/verification gate is warranted.

## Intent
Add the `constellation-curator` skill: a human-invoked, periodic corpus-maintenance
tool that MEASURES the skills corpus mechanically (`scripts/curate_corpus.py`),
then guides a human MEND pass, ROUTING design decisions to triage. It makes each
future accrete-then-consolidate run cheap and observable. Deliverables: the
measurement script, the SKILL.md, golden-fixture tests, install wiring, and a
two-sided acceptance check.

## Affected capabilities / structural anchors
- `scripts/` (top-level bundled-script family) — NEW `curate_corpus.py`. Precedent
  verified: no `skills/<skill>/scripts/` dirs exist; every script lives top-level
  and is bundled per-skill via `SKILL_SCRIPT_BUNDLES` in `install_constellation.py`.
  `curate_corpus.py` follows this precedent exactly.
- `skills/curator/` (NEW skill dir) — `SKILL.md` only (no references/templates:
  its doctrine is short and lives in one hop; the globals are bundled).
- `install_constellation.py` — `SKILL_SCRIPT_BUNDLES["curator"]` +
  `SKILL_REFERENCE_BUNDLES["curator"]`.
- `SKILL_INDEX.md` — one entry.
- `tests/` — NEW `test_curate_corpus.py`; additions to `test_install_constellation.py`.

## Governing constraints / assumptions (from launch order + spec, binding)
- Flags never gates: `curate_corpus.py` ALWAYS exits 0; findings are table rows.
  Enforced in code and falsified by a test.
- Mechanical-only (T7/decidability-honest): the script checks only mechanically
  decidable properties and never claims a semantic verdict (register-match,
  is-this-a-procedure). It may shortlist candidates; the human mend pass judges.
- NO baseline/drift-diff (S7 — deferred to v2).
- No new `global-*.md` filenames (bundle glob pins composition).
- Do NOT retro-tag the other 15 skills; curator declares only its own invoker tag.
- Source repo is authority; never edit installed copies; do not modify other
  skills' content (acceptance sweep only READS them).
- Fixtures' planted flaws DERIVE FROM real pre-#108 shapes (`git show 2696769:...`),
  not invented (T6).

## Decision anchors / decision pressure (surfaced as candidates for reconcile)
- **DC1 — curator reference bucket.** Curator is a solo, non-orchestrating,
  human-invoked role that dispatches no crew and drives no engine checklist.
  Chosen bucket: `_GLOBAL_EVERYONE` (global-everyone.md + windows.md) — same
  audience as interrogator and lessons-auditor (solo report/recommendation roles).
  **Complete comparison (cold-critic counter-evidence, weighed):** `global-orchestrator.md`
  names its audience as the high tier "Commander, Cartographer, Scout, Admiral,
  Triage", and both `scout` and `triage` — curator's nearest siblings in the spec
  (scout is its confusable pair; triage is its route/linear-pass precedent) — sit in
  `_GLOBAL_ORCHESTRATOR` despite themselves dispatching no crew. So orchestrator-bucket
  membership is NOT gated on crew-dispatch, and a scout-analogy would put curator there.
  Weighed AGAINST that: the epic's binding intent is that "each skill is visibly
  tailored to its invoker", and curator genuinely exercises none of the
  orchestrator-only payload (crew-dispatch, unchanged-tree, idle-adjudication,
  design-it-twice) as its own behavior; `_GLOBAL_EVERYONE` carries exactly the
  everyone-doctrine it does use (world-verification, scoped-nulls,
  delegate-not-replacement, deep-module vocab) and nothing it does not. The tailoring
  intent wins over the scout-consistency pull. Within inherited latitude (existing
  bucket, no new filename). Routed to reconcile AND surfaced as a triage candidate so
  the human ratifies the complete comparison at the epic boundary — the choice is
  cheaply reversible (a one-line bucket swap) if reconcile prefers scout-consistency.
- **DC2 — invoker-tag format.** A frontmatter key `invoker: human` (machine-
  detectable by the mechanical presence check). Seeds the convention the epic's
  cross-cutting rule 4 names; other skills stay untagged this run (curator's own
  first run flags them, as the spec expects).
- **DC3 — no report template shipped.** The curator's outputs (CURATOR_REPORT.md +
  `--json`) are described inline in SKILL.md rather than shipped as a
  `templates/` file, to avoid entangling curator in the template-baseline
  versioning machinery for a free-form human record. Keeps the skill one-hop.

## Claims / evidence surfaces
- The script's detectors BITE: proven by golden fixtures (a detector that finds
  nothing on fixtures is broken).
- Real corpus is near-quiet post-cleanup: proven by the own-run acceptance table.
- Detector/fixes don't share a blind spot: proven by the independent fresh-context
  sweep (T5) given neither the script nor the fix list.

## Out of scope (fences)
Other skills' content; `_shared/` content; `docs/ROADMAP.md`; retro-tagging;
baseline/drift machinery; agent-dispatched/scheduled curator modes; portfolio-duty
implementation (dormant until #106).
