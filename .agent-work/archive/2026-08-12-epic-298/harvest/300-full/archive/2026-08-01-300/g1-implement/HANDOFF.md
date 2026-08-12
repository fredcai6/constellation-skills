# Implementer Handoff

## Gate

`g1-implement` (issue #300, epic-298). Worktree root: `C:/Programs/constellation-skills-wt/298-300`.
Absolute paths everywhere — your cwd resets between bash calls.

## Task

Build the deterministic projection substrate and its manifest:

1. **A revision-identity function** — the git blob OID of the LF-normalised bytes, computed
   in-process, no `git` subprocess.
2. **An optional ordered `context_refs` declaration** on the spine task object.
3. **A pure producer** in `scripts/context_manifest.py` that resolves the active step's declaration
   and emits the manifest, selecting via the **existing** `active_id()` imported from
   `checklist_engine` — never a second selector.
4. **The manifest**, written under `.agent-work/<work-id>/context/<step>.json`.
5. **The first real declaration** on the Commander spine template's `context` step.
6. **The cross-environment determinism test.**

## Protected Intent

The manifest answers **what was made available to an agent, at which revision** — *delivery, not
use*. It is not an access trace, not transcript analysis, and not an archive of file contents. A
design that quietly widens toward proving *use* is wrong, not ambitious.

## Test Mode

**TDD required for the identity function** (`rev`): write the equality-against-`git hash-object` test
and the CRLF/LF-twin test first, watch them fail, then implement. Test-after is acceptable for the
rest. Reason: `rev` is the one primitive the entire manifest rests on, and a silently-wrong hash is
this design's worst failure mode — it produces plausible output forever.

## The design — already settled, do not redesign

Settled by a 3-author design-it-twice panel plus Tommy's ruling. Full record:
`.agent-work/300/DIT-COMPARISON.md` (read its **ADDENDUM** too). Surface a contradiction rather than
quietly deviating.

### Revision identity

```python
def rev(data: bytes) -> str:
    body = data.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(body) + body).hexdigest()
```

Three panel authors independently verified this equals `git hash-object <path>` and
`git rev-parse HEAD:<path>` for tracked clean files under this repo's `.gitattributes`
(`* text=auto`, `core.autocrlf=true`). It handles tracked, dirty, untracked, gitignored and
out-of-repo files with **no case analysis**.

- Absent file → `rev: null`, entry **retained**, no exception. Absence-by-design is normal here.
- Present but unreadable (permissions, is-a-directory) → **raise**. Keeps `null` meaning one thing.
- Path resolving outside its declared root (`..` traversal) → **raise**.
- **No commit SHA anywhere.** It lies about dirty trees and says nothing about untracked files.

### Declaration — `context_refs`

A new **optional** key on the spine task object, beside `constraints`/`directives`. Ordered list;
each entry `{"root": "skill"|"repo"|"durable", "path": "<posix relative path>", "required": bool}`.

- **Absent → empty manifest, no crash.** Every existing spine must keep working untouched. Verify
  this against a real existing spine, not a fixture.
- Roots resolve via an injected mapping the caller supplies. `skill` → the skill dir, `repo` → repo
  root, `durable` → `agent_work_root`'s durable root. **Absolute root paths never appear in the
  manifest content** — they are environment-varying.
- **No globs, no directory patterns, no `os.listdir`, no `sorted()` over paths, ever.** A glob would
  import filesystem ordering — a named irreproducibility source — into the record. **Declaration
  order is content** and is emitted verbatim.

### The manifest — ONE envelope

```json
{
  "contract": 1,
  "step": "context",
  "files": [
    {"root": "skill", "path": "references/global-orchestrator.md", "rev": "6241c56c…"},
    {"root": "repo",  "path": "docs/agents/GLOSSARY.md",            "rev": null}
  ],
  "run": { "…": "every legitimately-varying fact lives here and ONLY here" }
}
```

- `run` is **the entire exclusion set — one JSON pointer, `/run`**. Timestamps, run ids, absolute
  roots, host facts. Nothing varying may live outside it.
- Row is exactly `{root, path, rev}`. Do **not** add `bytes`, `state`, `canon` or `tracked`:
  `state` is `rev == null`; `bytes` is redundant against `rev`; and trackedness is
  **environment-varying**, which is a determinism hazard, not a feature.
- `required` lives in the **declaration**, not in the manifest.
- Serialise `json.dumps(obj, indent=2, ensure_ascii=False) + "\n"`, written with
  `open(..., "w", encoding="utf-8", newline="\n")`. **The `newline="\n"` is load-bearing on
  Windows**, not hygiene.
- Written to `.agent-work/<work-id>/context/<step>.json`.
- **Metadata only.** Never concatenate or copy file contents.

### Producer

`scripts/context_manifest.py`, importing `active_id` from `checklist_engine`. One pure function of
`(checklist, roots, reader)`; the **filesystem reader is a single injected impure edge** — that is
what lets the tests point the whole thing at a fixture tree. Mirror the engine's
`_STATE_CONTRACT_VERSION` idiom for `contract`.

**There is NO new CLI verb.** Cut deliberately as YAGNI — the manifest is a JSON file, and a verb
would touch the engine's persistence control flow for a convenience print. Do not add one.

## Close Criteria

- `rev` equals `git hash-object` for a real tracked clean file in this repo — proven by running both.
- CRLF and LF twins of identical content produce the **same** `rev`.
- A manifest is produced by driving the **real** producer through the engine's `active_id()`
  selector — not a hand-injected fixture (a hand-built fixture passes green even if production never
  works).
- A spine with no `context_refs` produces an empty manifest and does not crash.
- The Commander spine template's `context` step carries a real declaration.
- Cross-environment determinism holds (below).
- Targeted plus broader suites green.

## The determinism test — this is the issue's single acceptance test

`tests/test_context_determinism.py`. It must:

1. `git worktree add` a **clean second checkout** at the same commit, into a temp dir.
2. Run the producer there with mutated `LC_ALL`, `LANG`, and `PYTHONHASHSEED`.
3. Compare **content** — everything except the `/run` subtree — and assert byte-identity.

**Do not assert byte-identical whole output**: the manifest carries `run`, which legitimately varies.
Exclude exactly `/run` and **nothing else**. If any other field must be masked to make the test pass,
that field is in the wrong subtree and **the design is wrong, not the test** — stop and report it.

**State the limit honestly in a comment:** same OS, same filesystem. This exercises path ordering,
locale and hash ordering — not a cross-OS rebuild.

**Trap** (`lesson:windows-subprocess-env-does-not-shadow-path-resolution`): on Windows, passing
`env=` into `subprocess.run` does **not** change which executable an unqualified name resolves to.
Assert the locale mutation actually **took effect inside the child**; do not assume it did.

**Cleanup:** remove the temp worktree in a `finally`. Do not leave stray worktrees.

## Adversarial fixtures — required, not optional

A test that parses the real shipped corpus proves the **corpus is clean**, not that the **tool is
correct**. Bugs unreachable from real artifacts pass it silently. Ship fixtures authored to make the
tool return a **wrong** answer:

- CRLF/LF twins that **must** agree (false-FAIL hunt).
- A file whose bytes changed but whose recorded `rev` did not — must **not** silently pass.
- Untracked-vs-absent: the same declared path present in one environment and absent in another must
  not make two environments disagree on **content**.
- A declaration-order permutation that **must** register as a difference (order is content).

Also required, because `g1.c6` runs `-k 'no_globs or newline_pinned or py312_compatible'` and a
`-k` matching nothing exits 5 (a failure):

- `test_no_globs…` — the producer performs no filesystem enumeration.
- `test_…newline_pinned…` — every write pins `newline="\n"`.
- `test_…py312_compatible…` — no 3.13+-only API is used (see Constraints).

## Allowed Scope

- **New:** `scripts/context_manifest.py`, `tests/test_context_manifest.py`,
  `tests/test_context_determinism.py`, fixtures under `tests/fixtures/`.
- **Edit:** `skills/commander/templates/COMMANDER_SPINE.template.json` — add `context_refs` to the
  `context` step **only**.
- **Edit, minimally:** `scripts/checklist_engine.py` — only if `active_id` needs exporting. Prefer
  importing what already exists. Any engine edit beyond an import surface is a stop condition.
- Pre-authorised: reconciling any existing test that the new optional field legitimately disturbs.
  None is expected — the field is optional — but if one breaks, that is in scope to fix minimally.

## Specific Exclusions

- **No committed `CONTEXT_PROJECTION.json` and no `scripts/context_projection.py`.** Ruled out of
  #300's scope by Tommy on 2026-08-01. Do not build the ahead-of-time generator back in.
- **`docs/CHECKLIST_SCHEMA.md`, `docs/CHECKLIST_ENGINE_DESIGN.md`, and the declaration-vs-prose
  lint** are **gate g3's**, not yours. Do not touch them.
- **`verify_spec_confirmed.py`** — owned by issue #303.
- Do **not** delete or reword the `context` step's imperative prose. It carries the
  substitute-and-record rule and the "sanctioned degradation" rule, which g3 pins with a lint.
  Your declaration sits **alongside** that prose.
- Do not hand-edit `.agent-work/LESSONS.md` or any engine JSON.

## Constraints

- **`python -m pytest`, never `py -m pytest`** — `py` resolves to a runtime with no pytest here.
- **CI pins Python 3.12** (`.github/workflows/ci.yml:34`); this host is 3.14.3. Do **not** use
  `Path.read_text(newline=)` or `Path.write_text(newline=)` — that kwarg is **3.13+**. Use
  `open(..., newline=...)`. A sibling issue in this epic shipped a red CI on exactly this.
- All commands assume cwd = the worktree root; the engine passes no `cwd=` to check commands.
- No LLM inference, no semantic routing, no network at assembly time. Pure function of
  (canon, selector state).
- Every manifest row must stay expressible later as an assertion with a subject and a source — do not
  add fields that would have to be re-litigated.

## Map Anchors (inbound)

- **Structural:** `scripts/checklist_engine.py` — `active_id()` (~:184) is THE selector, reused not
  duplicated; `state()`/`render_human()`/`_STATE_CONTRACT_VERSION` (~:1336–1471) is the seam and
  versioning idiom this mirrors.
- **Capability:** `capability:spine-keyed-context-delivery` — deterministic *selection* exists today;
  the declaration, the assembly and the record do not.
- **Constraints:** `constraint:stochastic-boundary`; `constraint:markdown-in-git`;
  `constraint:delivery-not-use`; `constraint:extend-dont-parallel`; `constraint:windows-corpus`;
  `constraint:no-foreclosure`.
- **Decision anchors:**
  - `decision:rev-is-lf-normalised-blob-oid`
    `@grade: settled/measured · leans g1-implement · settle: already settled — three independent authors verified equality with git hash-object on real files including CRLF twins`
  - `decision:declaration-field-is-context_refs`
    `@grade: settled/measured · leans g1-implement`
  - `decision:no-globs-order-is-content`
    `@grade: settled/measured · leans g1-implement`
  - `decision:producer-is-a-sibling-module`
    `@grade: guess · leans g1-implement · settle: if the import seam creates a second effective selector, inline it into checklist_engine.py instead`
- **Evidence expectations:** `claim:revision-identity-present`, `claim:manifest-on-every-assembly`,
  `claim:deterministic-across-environments`.
- **Map confidence flags:** `scripts/agent_work_root.py` returns the **worktree**, not the main
  checkout, while an Admiral lease is active — verified live this run. The `durable` root token must
  account for that; do not assume the durable root is the main checkout.

## Deliverable Path Check

Run by the Commander before dispatch:

- **Committed** — `git check-ignore <path>` exit **1** (not ignored) for all four:
  `scripts/context_manifest.py`, `tests/test_context_manifest.py`,
  `tests/test_context_determinism.py`, `skills/commander/templates/COMMANDER_SPINE.template.json`.
- **Local-only** — `.agent-work/300/context/context.json`: `git check-ignore` exit **0**, i.e.
  intentionally gitignored. This is **Tommy's ruling**, not an oversight — the manifest lives under
  `.agent-work/`. The reviewer must **not** expect it in the diff.

The three new files are untracked until staged: `git diff` shows 1 changed file; the new ones appear
in `git status`.

## Required Evidence

**Load-bearing — prove rigorously:**

1. `rev` == `git hash-object` on a real tracked file: paste both commands and both outputs.
2. CRLF/LF twins produce the same `rev`.
3. A manifest produced by driving the real producer through `active_id()`.
4. The cross-environment determinism run: paste the transcript showing two **distinct** checkout
   paths and the content comparison result.

**Confirmatory — a spot-check suffices:** empty-declaration no-crash; the spine template edit;
the no-globs / newline / 3.12 assertions.

## Verification Commands

```bash
cd C:/Programs/constellation-skills-wt/298-300
python -m pytest tests/test_context_manifest.py -q
python -m pytest tests/test_context_determinism.py -q
python -m pytest tests/test_context_manifest.py -q -k 'no_globs or newline_pinned or py312_compatible' --no-header
grep -q 'context_refs' skills/commander/templates/COMMANDER_SPINE.template.json
python -m pytest tests/test_checklist_engine.py -q
python -m pytest tests/ -q
test -f .gitattributes && ! grep -nE '(^|[[:space:]])(-text|binary)([[:space:]]|$)' .gitattributes
```

All must exit 0 when you are done. The last one is an invariant that must **stay** passing: the
identity function equals `git hash-object` only while no path is exempted from LF normalisation.

## Suggested Model Tier

Stronger. The design is fully specified, but a silently-wrong identity function is undetectable by
inspection and permanent, and the determinism test involves real worktree and environment
manipulation with a named Windows trap.

## Authority

Settled, not yours to revisit: the identity function; the `context_refs` shape and name; no globs;
one envelope with `/run` as the entire exclusion set; no CLI verb; no committed artifact
(**Tommy's ruling**); prose stays.

Yours to decide and log: internal code structure, fixture layout, test naming (subject to the `-k`
selectors above), and how the injected reader/roots are threaded.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; a specific exclusion must be touched; the
determinism comparison needs to exclude anything **beyond** `/run`; `active_id()` cannot be reused
without creating a second selector; or the `rev` function cannot be made to equal `git hash-object`
for some real case in this repo — that last one is a **design-invalidating** finding, so report it
rather than working around it.

## Return Format

Return `IMPLEMENTER_RESULT` to
`C:/Programs/constellation-skills-wt/298-300/.agent-work/300/g1-implement/IMPLEMENTER_RESULT.md`:
completed slice, files changed, test mode satisfied, evidence produced (with the pasted transcripts
above), assumptions used, stop conditions hit, out-of-scope observations, and workflow feedback —
what in this handoff or the workflow made the work harder than it needed to be.
