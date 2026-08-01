# Implementer Handoff

Concise fragments. Paste, don't point — you start cold.

## Gate
`g4-implement` (issue #104, constellation-curator, cluster C)

## Task
Wire the `constellation-curator` skill into the installer: bundle its script and its
global-doctrine references, add its `SKILL_INDEX.md` entry, and add dedicated per-skill
install tests. Surgical edits only.

Repo: `C:\Programs\constellation-wt-104` (branch constellation/issue-104). The script
`scripts/curate_corpus.py` (G1) and `skills/curator/SKILL.md` (G2) already exist and are
committed. `discover_skills()` already finds curator (SKILL_NAMES was updated in G2); this
gate adds the BUNDLE wiring so the installed curator carries its script + references.

## Read first
- `scripts/install_constellation.py` — specifically `SKILL_SCRIPT_BUNDLES` (dict of
  skill -> tuple of scripts bundled into `<installed>/scripts/`) and
  `SKILL_REFERENCE_BUNDLES` (skill -> tuple of `_shared` refs bundled into
  `<installed>/references/`), and the `_GLOBAL_*` bucket constants above them.
- `tests/test_install_constellation.py` — the per-skill install-test pattern. Model your
  new tests on `test_explorer_script_bundle_lands_in_installed_skill` (line ~668) and
  `test_global_doctrine_buckets_bundled_per_audience` (line ~181).

## Decisions already made (do NOT revisit — from the mission frame DC1)
- **Script bundle:** `SKILL_SCRIPT_BUNDLES["curator"] = ("curate_corpus.py",)`. Follows the
  per-skill top-level-script precedent exactly (e.g. docent bundles `docent_freshness.py`).
- **Reference bucket:** `SKILL_REFERENCE_BUNDLES["curator"] = _GLOBAL_EVERYONE`
  (`global-everyone.md` + `windows.md`). Rationale (recorded, ratified at reconcile): the
  curator is a solo, non-orchestrating, human-invoked role that dispatches no crew and
  drives no engine checklist — same audience as interrogator and lessons-auditor. Do NOT
  invent a new `global-*.md` filename (the bundle glob pins composition); reuse the existing
  `_GLOBAL_EVERYONE` constant.

## Close Criteria (each proven in your IMPLEMENTER_RESULT)
1. `SKILL_SCRIPT_BUNDLES["curator"] = ("curate_corpus.py",)` added.
2. `SKILL_REFERENCE_BUNDLES["curator"] = _GLOBAL_EVERYONE` added (reuse the existing
   constant — do not spell out a new tuple, and do NOT add any new global-*.md filename).
3. `SKILL_INDEX.md` gains ONE curator entry, matching the file's existing entry format
   (heading `## Constellation Curator`, a `Path:` line, and a one-paragraph description
   consistent with the others).
4. New per-skill install tests in `tests/test_install_constellation.py`:
   - `curate_corpus.py` bundles into `<target>/constellation-curator/scripts/curate_corpus.py`.
   - the `_GLOBAL_EVERYONE` bucket lands: `<target>/constellation-curator/references/`
     contains BOTH `global-everyone.md` and `windows.md`.
   - curator installs + discovers as a skill (a dry-run or real install of `--skills curator`
     succeeds and creates `constellation-curator/SKILL.md`).
   - Each test is written so it would RED if the corresponding bundle entry were dropped
     (state this in your result — e.g. "delete the SKILL_SCRIPT_BUNDLES['curator'] line ->
     this assert reds").
5. `py -m pytest tests/ -q` GREEN (existing + new).
6. `test_bundled_scripts_carry_their_sibling_imports` still passes (it checks every bundled
   script's `from X import` siblings are co-bundled — `curate_corpus.py` is stdlib-only, so
   it should carry no sibling-import requirement; confirm).

## Allowed Scope
- `scripts/install_constellation.py` — ONLY the two new curator dict entries (script bundle
  + reference bundle). Do NOT modify any other skill's bundle entries.
- `SKILL_INDEX.md` — ONLY the one new curator entry.
- `tests/test_install_constellation.py` — ADD curator install tests. You may NOT alter
  existing tests except: none expected (SKILL_NAMES already carries curator from G2).

## Specific Exclusions
- Do NOT change any other skill's `SKILL_SCRIPT_BUNDLES` / `SKILL_REFERENCE_BUNDLES` entry.
- Do NOT add a new `global-*.md` file or a new bucket constant.
- Do NOT edit `skills/curator/SKILL.md` or `scripts/curate_corpus.py`.
- Do NOT touch `docs/ROADMAP.md` or any `_shared/` content.

## Constraints
- Surgical text edits to `install_constellation.py` (it contains shipped dict literals —
  add lines, do not reformat the file).
- Match the exact house style of the existing per-skill tests (load_installer, tempfile,
  `--dest`, `env={}`, `out=lambda _: None`).

## Map Anchors (inbound)
- **Structural:** `install_constellation.py` bundle maps; `SKILL_INDEX.md`;
  `tests/test_install_constellation.py`.
- **Capability:** curator ships its script + the everyone reference bucket at install.
- **Constraint:** no new global filename; bundle glob pins composition; per-skill precedent.
- **Decision:** DC1 `_GLOBAL_EVERYONE` bucket (ratified reasoning above).
- **Evidence:** install tests assert script + bucket land, and would red if an entry dropped.

## Deliverable Path Check
All three targets are already tracked (committed) files — your edits ride into the diff:
`scripts/install_constellation.py`, `SKILL_INDEX.md`, `tests/test_install_constellation.py`.

## Required Evidence (paste into IMPLEMENTER_RESULT)
- The diff of the two `install_constellation.py` dict-entry additions and the `SKILL_INDEX.md`
  entry.
- The new test functions' code.
- `py -m pytest tests/ -q` tail (green) AND `py -m pytest tests/test_install_constellation.py -v -k curator`
  showing the curator tests named and passing.
- A one-line falsification note per new test (which entry's deletion reds it).

## Verification Commands
```bash
cd C:/Programs/constellation-wt-104
py -m pytest tests/test_install_constellation.py -v -k curator
py -m pytest tests/ -q
py scripts/install_constellation.py --agent codex --scope user --dest /tmp/curator-install-g4 --skills curator
ls /tmp/curator-install-g4/constellation-curator/scripts /tmp/curator-install-g4/constellation-curator/references
```

## Suggested Model Tier
`simple bounded — reason: mechanical wiring against a clear precedent`

## Authority
Decided (do not revisit): the two bundle entries and their values (DC1); one index entry;
tests model the explorer/global-bucket precedents. You DECIDE: test names, index paragraph
wording (consistent with siblings).

## Stop Conditions
Stop and return if: wiring curator forces a change to another skill's bundle entry; a new
global-*.md filename seems required (it is not — reuse `_GLOBAL_EVERYONE`); required
evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, evidence (pasted diffs + test
runs + falsification notes), assumptions, stop conditions hit, out-of-scope observations,
workflow feedback. WRITE the full IMPLEMENTER_RESULT as your final message AND to the given
result path before going idle.
