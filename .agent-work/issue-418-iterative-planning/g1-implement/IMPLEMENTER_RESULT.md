# Implementation Result

gate_id: g1  
red_exit: 1  
green_exit: 0  
diff_digest: sha256:6cbbac6e4c8bd29cca580e5aca324a107a35f7921ae2a1149311f774adf9db30

## Assigned gate

`g1 — Canonical initial cut`

## Completed slice

Hard-renamed the cut-work skill to `constellation-to-initial-issues`; added the
strict v1 shaped-brief/current-wave manifest seam; restricted filing to current
issues; strengthened epic and every-child receipt recovery; and implemented the
exact installer migration policy.

## Scope

**Files changed:**

- `skills/to-issues/**` deleted; `skills/to-initial-issues/**` added.
- `tests/test_to_issues.py` deleted; `tests/test_initial_issues.py` added.
- `scripts/verify_issue_set.py`, `scripts/file_issue_set.py`,
  `scripts/install_constellation.py`.
- `tests/test_install_constellation.py`.
- `README.md`, `SKILL_INDEX.md`, `docs/CONSTELLATION_OVERVIEW.md`,
  `docs/POSITIONING.md`, `skills/write-a-skill/SKILL.md`.
- Explorer live route only: `skills/explorer/SKILL.md` and
  `skills/explorer/templates/EXPLORER_SPINE.template.json`.

**Specific exclusions touched:** no. `.agent-work/archive/**`, legacy transcript
fixtures, external/removability provenance, tracker architecture, and checklist
engine were not edited. No live GitHub/network operation ran.

## Behavior changed

Yes. A confirmed strict v1 shaped brief is now the direct cutter input. The
builder copies `title` and `source_path` exactly, preserves planning context,
and adds runnable drafts only under `current_wave.issues`. Forecast entries
cannot carry runnable fields and never reach adapter find/create calls. Zero
edges pass; dangling and cyclic edges fail. The epic renderer emits exactly the
eight frozen headings.

Receipts are bound to a canonical manifest digest and checked against expected
epic/child keys before any adapter call. The identical find/create/receipt
protocol covers the epic and every current child across before-file,
after-file-before-receipt, and after-receipt crashes.

## Map Impact

- **Structural anchors touched:** `README.md` and `SKILL_INDEX.md` now expose one
  canonical `to-initial-issues` route; the old live skill tree is deleted.
- **Capabilities added/changed/affected:** initial cut and offline filing now
  consume a versioned shaped brief and make only one current wave actionable.
- **Constraints/assumptions touched:** single canonical execution path honored;
  existing Markdown/GitHub adapter seam and receipt recovery retained and
  strengthened.
- **Decision candidates / resolved decisions:** hard rename and current-wave-only
  actionability implemented; Commander clarified v1 `parked_possibilities` as a
  possibly empty array of nonempty strings.
- **Claims/evidence produced:** strict schema/mapping, eight headings,
  zero/dangling/cycle edges, forecast spy, nine crash-window combinations,
  receipt mismatch, installer migration matrix, registration, and live-name
  audits are executable and green.
- **Trust limitations / drift found:** no architecture map existed; public
  interfaces and live registrations were verified directly as instructed.

## Test mode

**Required:** test-first  
**Satisfied:** yes — tests and the hard test rename were applied before any
production script, skill, installer, or documentation edit. The required
focused command then failed on the absent canonical paths/helpers/registration.

## TDD evidence

Identical RED/GREEN command:

```bash
uv run python -m pytest -q tests/test_initial_issues.py tests/test_install_constellation.py
```

**RED output (exit 1, before production edits):**

```text
FFFF..FFFFF...................F.FF...F..... [ 36%]
...
E FileNotFoundError: ...skills/to-initial-issues/templates/SHAPED_BRIEF.template.json
E AttributeError: module 'verify_issue_set' has no attribute 'build_initial_manifest'
E install_constellation.InstallError: unknown skill(s): to-initial-issues
27 failed, 104 passed, 365 subtests passed in 13.75s
```

The historical transcript above remains the causal RED captured before
production edits. Reproducing the final test overlay against `HEAD` now yields
the same intended missing-behavior failures but reports `29 failed, 104 passed,
365 subtests passed`: two CLI/calendar checks were added while green after the
historical RED. This expected overlay delta does not replace or rewrite the
original test-first evidence.

**GREEN output (exit 0):**

```text
................................... [ 29%]
................................................................................ [ 95%]
.....                                                                    [100%]
120 passed, 389 subtests passed in 14.18s
```

**Refactor while green:** yes — corrected the offline assertion to distinguish
forecast rendering in the epic from forecast issue creation, then added CLI
round-trip coverage and valid-calendar-date enforcement while retaining green.

## Additional evidence

```bash
uv run python scripts/verify_skill_registered.py --skill to-initial-issues
```

```text
skill ok: to-initial-issues is registered, mechanically clean, and installs (--dry-run)
```

```bash
uv run python -m pytest -q tests/test_explorer_templates.py
```

```text
24 passed in 1.02s
```

The scoped public-helper wiring grep found executable callers/tests for
`verify_shaped_brief`, `build_initial_manifest`, `verify_issue_set`,
`render_epic_body`, `manifest_key`, and `file_issue_set`. The tracked old-name
audit found `93` paths and `0` unexpected paths after applying the exact
historical/fixture/external-provenance/migration allowlist. `git diff --check`
passed.

The current diff digest is SHA-256 over the exact ordinal-sorted 20-path G1
inventory, encoding each entry as `UTF-8(path) + NUL + current bytes (or the
UTF-8 bytes of <deleted>) + NUL`. It was recomputed after the final focused
test. This includes the four untracked new skill files and new focused test,
which ordinary unstaged `git diff` output omits.

Reproducible evidence is persisted beside this result:

- `.agent-work/issue-418-iterative-planning/g1-implement/G1_DIGEST_PATHS.txt`
- `.agent-work/issue-418-iterative-planning/g1-implement/recompute_g1_digest.ps1`

```powershell
& '.agent-work\issue-418-iterative-planning\g1-implement\recompute_g1_digest.ps1'
```

```text
sha256:6cbbac6e4c8bd29cca580e5aca324a107a35f7921ae2a1149311f774adf9db30
```

Exact ordinal-sorted inventory:

```text
README.md
SKILL_INDEX.md
docs/CONSTELLATION_OVERVIEW.md
docs/POSITIONING.md
scripts/file_issue_set.py
scripts/install_constellation.py
scripts/verify_issue_set.py
skills/explorer/SKILL.md
skills/explorer/templates/EXPLORER_SPINE.template.json
skills/to-initial-issues/SKILL.md
skills/to-initial-issues/references/manifest.md
skills/to-initial-issues/templates/INITIAL_ISSUE_SET.template.json
skills/to-initial-issues/templates/SHAPED_BRIEF.template.json
skills/to-issues/SKILL.md
skills/to-issues/references/manifest.md
skills/to-issues/templates/ISSUE_SET.template.json
skills/write-a-skill/SKILL.md
tests/test_initial_issues.py
tests/test_install_constellation.py
tests/test_to_issues.py
```

The stale `71aa91e4…` identity came from PowerShell culture sorting. The
persisted helper explicitly uses `StringComparer.Ordinal`, removing that
platform-sensitive ambiguity and reproducing the reviewer's `6cbbac6e…` bytes.

## Rename inventory

- Canonical skill: `skills/to-initial-issues/SKILL.md`, frontmatter
  `constellation-to-initial-issues`.
- Templates/references: strict `SHAPED_BRIEF.template.json`, strict
  `INITIAL_ISSUE_SET.template.json`, and updated `references/manifest.md`.
- Old live skill: all three tracked `skills/to-issues/**` files deleted; no alias.
- Focused tests: `tests/test_to_issues.py` deleted and
  `tests/test_initial_issues.py` added.
- Registry/bundles: installer script/reference bundle keys renamed.
- Installer migration: exact `constellation-to-issues` destination only;
  no-force refusal names `--skills to-initial-issues --force`; force removes
  only legacy before installing canonical; dry-run is non-mutating; subset and
  full-force outcomes are tested.
- Public docs/index: README, skill index, overview, positioning, and
  write-a-skill lean example updated.
- Explorer live route: skill prose and spine template updated to the canonical
  route name only.
- Script/test docstrings and CLI surfaces use shaped brief/current wave terms.
- Preserved allowlist: archives and run artifacts, legacy transcript fixtures,
  Matt Pocock/external provenance and removability ledgers, plus the explicit
  installer migration constant/tests.

## Docs/contracts touched

- `skills/to-initial-issues/templates/SHAPED_BRIEF.template.json`
- `skills/to-initial-issues/templates/INITIAL_ISSUE_SET.template.json`
- `skills/to-initial-issues/references/manifest.md`
- Live README/index/overview/positioning/Explorer route surfaces listed above.

## Assumptions

- The v1 parked shape follows the Commander's adjudication: an array of
  nonempty strings, possibly empty.
- Existing unrelated dirty-worktree changes listed at dispatch remain owned by
  other work and were not modified by this run.

## Stop conditions hit

- The frozen imperative omitted the parked-entry shape. Work paused and the
  decision was returned upward. Commander resolved it as the exact nonempty-
  string array contract; implementation resumed without inventing an object
  shape.
- No other stop condition was hit.

## Out-of-scope observations

- None. A transient concurrent `uv` cache-initialization race occurred twice;
  retrying the exact commands succeeded without code or environment changes.

## Workflow Feedback

- **Handoff gaps:** the G1 imperative said parked possibilities used the shape
  “below,” but did not state that shape. The Commander supplied the missing
  exact v1 contract.
- **Context rediscovered:** the live-name allowlist had to be reconstructed from
  tracked historical run artifacts and external/removability provenance because
  the handoff named categories but no path list.
- **Instructions improvised around:** the installed Implementer skill required
  the first command to instantiate/claim before reading the handoff closely,
  while dispatch required reading that handoff to know the work area. The skill
  and handoff were read together before the plan was created; no task work began
  before the lease was claimed.
- **Rework evidence identity:** the original result said “sorted” without
  defining ordinal versus culture sorting. The rework persists an ordinal
  inventory and executable helper; this is why the refreshed digest differs.
- **What would have made this easier:** carry the exact old-name path allowlist
  and every strict nested schema, including parked entries, in the frozen gate
  artifact.

## Return status

`complete`
