# Candidate B — `ports-and-adapters`

**Constraint:** ports-and-adapters. Mirror the seam `scripts/checklist_engine.py` already uses
(`state(cl) -> dict` pure projection + `render_human` adapter + `contract` version int,
`checklist_engine.py:1336-1554`, documented in `docs/CHECKLIST_ENGINE_DESIGN.md` §Answerability).

**Stance:** the record's **in-memory shape**, its **on-disk encoding**, and its **consumers** are
three separable concerns. Every fact below that I could check, I checked — the commands are shown.

---

## 1. The shape

Four siblings at the envelope root. The whole design rides on this split:

| key | what it is | varies? |
|---|---|---|
| `contract` | int, the shape version — same role as `_STATE_CONTRACT_VERSION` | no |
| `content_digest` | `sha256:<hex>` over the canonical encoding of `content` | no (pure fn of `content`) |
| `content` | **everything that is a pure function of (canon, selector state)** | no |
| `run` | **the entire exclusion set** — one subtree, one JSON pointer `/run` | yes, by design |

### Worked example — real bytes

The Commander spine's `context` step (`skills/commander/templates/COMMANDER_SPINE.template.json`,
`tasks.context`), driven in **this** worktree at HEAD `b69e6c8`. Every `blob` below is a real
`git hash-object` output; `content_digest` is the real sha256 of the canonical encoding of the
`content` object exactly as printed. `docs/agents/` is genuinely absent in this repo (absent-by-design
for a skill-source repo — the imperative says so), so four entries exercise the `absent` branch:

```json
{
  "contract": 1,
  "content_digest": "sha256:54314d71b1e8ee4685e67f3a874a9b64c3b0c6c2a0d1858f19fa6398159908b4",
  "content": {
    "spine": {
      "work_id": "300",
      "step": "context",
      "declared_by": "tasks.context.context_refs",
      "selector_contract": 1
    },
    "entries": [
      {
        "ref": "doctrine:global-orchestrator",
        "declared_path": "references/global-orchestrator.md",
        "role": "doctrine",
        "required": true,
        "state": "committed",
        "resolved_path": "skills/_shared/global-orchestrator.md",
        "blob": "6241c56ccda9cda53422ab3cecc1edbf168caa9c",
        "bytes": 10251,
        "origin": {
          "repo": "constellation-skills",
          "commit": "b69e6c8c9911e4010d7e66fa13275e950f33ade8"
        }
      },
      {
        "ref": "doctrine:global-everyone",
        "declared_path": "references/global-everyone.md",
        "role": "doctrine",
        "required": true,
        "state": "committed",
        "resolved_path": "skills/_shared/global-everyone.md",
        "blob": "b10abd32711f4579509c80e7376e9ea79806866c",
        "bytes": 17194,
        "origin": {
          "repo": "constellation-skills",
          "commit": "b69e6c8c9911e4010d7e66fa13275e950f33ade8"
        }
      },
      {
        "ref": "overlay:orchestrator-context",
        "declared_path": "docs/agents/ORCHESTRATOR_CONTEXT.md",
        "role": "project-delta",
        "required": false,
        "state": "absent",
        "resolved_path": null,
        "blob": null,
        "bytes": null,
        "origin": null
      },
      {
        "ref": "overlay:glossary",
        "declared_path": "docs/agents/GLOSSARY.md",
        "role": "project-delta",
        "required": false,
        "state": "absent",
        "resolved_path": null,
        "blob": null,
        "bytes": null,
        "origin": null
      },
      {
        "ref": "overlay:engine-config",
        "declared_path": "docs/agents/engine-config.json",
        "role": "engine-config",
        "required": false,
        "state": "absent",
        "resolved_path": null,
        "blob": null,
        "bytes": null,
        "origin": null
      },
      {
        "ref": "lessons:active",
        "declared_path": ".agent-work/LESSONS.md",
        "role": "lessons",
        "required": false,
        "state": "absent",
        "resolved_path": null,
        "blob": null,
        "bytes": null,
        "origin": null
      }
    ]
  },
  "run": {
    "run_id": "300-context-1",
    "generated_at": "2026-07-31T22:41:07.913224+00:00",
    "producer": "scripts/context_manifest.py@1",
    "host": { "os": "nt", "python": "3.13.2" },
    "cwd": "C:/Programs/constellation-skills-wt/298-300"
  }
}
```

**Entry order is declaration order** — never filesystem order. That is the structural answer to one
of the brief's three named Windows irreproducibility sources. If a declaration ever admits a glob,
its expansion sorts by codepoint over the `/`-normalised path, and that rule lives in the resolver
adapter, not in the projection.

**An absent declared file is recorded, never dropped.** A manifest that silently omitted the four
`docs/agents/` entries would be byte-indistinguishable from one where nothing was declared. That is
exactly the defect class HEAD just fixed one commit ago in the governor
(`b69e6c8 fix(governor): make a non-reading visible, distinct from a low reading`). Same law here.

---

## 2. Revision identity

**Primary identity is the git blob sha1 of the LF-normalised content.** Not the commit. Verified:

```
$ git hash-object skills/_shared/global-orchestrator.md
6241c56ccda9cda53422ab3cecc1edbf168caa9c
$ git rev-parse HEAD:skills/_shared/global-orchestrator.md
6241c56ccda9cda53422ab3cecc1edbf168caa9c
$ py -c "...sha1(b'blob %d\0'%len(lf)+lf)..."
6241c56ccda9cda53422ab3cecc1edbf168caa9c        # pure Python, no git subprocess
```

Three consequences, all verified rather than assumed:

1. **CRLF-immune.** This corpus has `.gitattributes: * text=auto` and `core.autocrlf=true`. I tested
   the twin directly:
   ```
   $ git hash-object --no-filters crlf.md   c30dea8a3641ea99b125d04d599d843712292759
   $ git hash-object --no-filters lf.md     422c2b7ab3b3c668038da977e4e93a5fc623169c
   $ git hash-object --path docs/x.md crlf.md  422c2b7ab3b3c668038da977e4e93a5fc623169c
   $ git hash-object --path docs/x.md lf.md    422c2b7ab3b3c668038da977e4e93a5fc623169c
   ```
   The named line-ending irreproducibility source is **eliminated structurally**, not excluded. It
   never reaches the exclusion set.
2. **No git required.** The digest is `sha1(b"blob %d\0" % len(lf) + lf)` in pure Python. So identity
   works for a file that is untracked, outside the repo, or in no repo at all — and the projection
   needs no subprocess, which is what makes the INV-2-style purity law below enforceable.
3. **Content-addressed across repos.** `install_constellation.py:520` copies shared doctrine into each
   installed skill with `shutil.copy2` — a verbatim byte copy. So an installed
   `.claude/skills/constellation-commander/references/global-orchestrator.md` hashes **identically** to
   `skills/_shared/global-orchestrator.md` in this repo. A commit-only identity would report
   "untracked, unknown" for the file the agent actually opened. The blob proves it is byte-identical
   to a known canonical revision even though it lives in a different checkout.

`origin` is the **secondary, best-effort** enrichment — the answer to "which published revision",
which is not always answerable. `state` is a closed five-value vocabulary:

| `state` | when | `blob` | `origin` |
|---|---|---|---|
| `committed` | tracked, clean, blob == `HEAD:<path>` | yes | `{repo, commit}` from that file's own repo |
| `dirty` | tracked, working-tree bytes differ from `HEAD:<path>` | yes | `{repo, commit: null, head: <HEAD>}` — honest: exact bytes known, no published revision |
| `untracked` | inside a repo, not in the index (`docs/agents/` in a host repo) | yes | `{repo, commit: null}`; if a `CORPUS.json` marker governs the path, its `source_commit` is carried as `origin.corpus_source_commit` |
| `external` | resolves outside every known repo root (`.agent-work/LESSONS.md` in a different checkout) | yes | `{repo: null}` or that other repo's `{repo, commit}` if it is one |
| `absent` | declared, does not resolve | `null` | `null` |

The invariant the whole record leans on: **`blob` is present for every state except `absent`.** So the
manifest always answers "which exact bytes"; it answers "which published revision" only when that
question has an answer, and says so in one enumerated field rather than by omission.

Realistic non-`committed` entries as they appear in a host repo (f1brainz-shaped):

```json
{ "ref": "overlay:glossary", "declared_path": "docs/agents/GLOSSARY.md", "role": "project-delta",
  "required": false, "state": "untracked", "resolved_path": "docs/agents/GLOSSARY.md",
  "blob": "a3f19c…", "bytes": 4127,
  "origin": { "repo": "f1brainz", "commit": null } }

{ "ref": "lessons:active", "declared_path": ".agent-work/LESSONS.md", "role": "lessons",
  "required": false, "state": "external", "resolved_path": "../f1brainz/.agent-work/LESSONS.md",
  "blob": "77b204…", "bytes": 9033,
  "origin": { "repo": null, "commit": null } }
```

`resolved_path` is always **relative to the manifest's own repo root**, never absolute — absolute
paths are host facts and belong in `run.cwd`.

---

## 3. Where it is declared

A new **optional** field `context_refs` on a spine task, alongside `constraints`/`directives`:

```json
"context": {
  "id": "context",
  "title": "Load baseline context",
  "imperative": "Read your inherited global doctrine (this skill's references/global-orchestrator.md …",
  "context_refs": [
    { "ref": "doctrine:global-orchestrator", "path": "references/global-orchestrator.md",
      "role": "doctrine", "required": true },
    { "ref": "overlay:glossary", "path": "docs/agents/GLOSSARY.md",
      "role": "project-delta", "required": false }
  ],
  "postconditions": [ … ]
}
```

Absent `context_refs` → empty declaration → empty `entries`, no crash. Same backward-compatibility
posture the engine already uses for `why_trail` (`setdefault` on first write, `checklist_engine.py:965`)
and for the gauge reader (`_load_gauge_reader` returns `None` and the policy simply does nothing).

**The prose stays.** I do not strip the file names from the imperative, for a reason that is visible in
the real text: the `context` imperative does not merely *list* files, it carries the substitution rule
("where the repo carries no `docs/agents/` overlay at all … substitute the closest repo doctrine you
can find and record the substitution") and the config degradation rule ("a missing engine-config is a
sanctioned degradation, not a gap to fix — do NOT create the overlay file"). No declaration schema I
am willing to ship carries that, and inventing one would be semantics smuggled into data.

That leaves **two sources for one list**, which is a real drift hazard and I will not pretend otherwise.
The mitigation is a lint in the existing `verify_*.py` family: every `path` in `context_refs` must
appear verbatim in that task's `imperative`, and every path-shaped token in the imperative must be
declared or explicitly `"declared": false`-listed. Mechanical, no judgment. **Required, not optional** —
without it this design has a silent-divergence failure mode within one release.

---

## 4. Producer / consumer API — the three ports

The seam I am buying is that **exactly one function touches the filesystem**.

### Port A — declaration source
```python
def declared_refs(cl: dict, step_id: str) -> list[dict]:
    """Pure. The authored context declaration for a step, in authored order. []
    when the task has no `context_refs`."""
```
Shipped adapter: the spine field above. (This is the port I am least sure earns its name — see §7.)

### Port B — resolver  ← *the impure edge, and the whole testability story*
```python
class Resolver(Protocol):
    def resolve(self, ref: dict) -> dict:
        """ref -> {resolved_path, exists, content: bytes|None, repo, head, tracked, dirty}.
        The ONLY component permitted to touch the filesystem or invoke git."""
```
- `FilesystemGitResolver(roots)` — real. Owns base-dir search order (skill dir → repo root → work-area
  root), `git ls-files`/`git rev-parse`, and the `/`-normalisation of paths.
- `MappingResolver({path: bytes})` — a pure in-memory double. **No filesystem, no git, no subprocess.**

### Port C — projection
```python
_MANIFEST_CONTRACT_VERSION = 1

def manifest_state(declared: list[dict], resolved: list[dict], *,
                   work_id: str, step_id: str) -> dict:
    """Pure projection: (declaration, resolved facts) -> the `content` object.
    Mirrors state(cl) -> dict exactly."""
```
**INV-M1 (purity), stated the same way INV-2 is:** `manifest_state` never opens a file, never invokes
git, never calls `subprocess`. It computes blob shas from bytes it was *handed*. Building the record is
not a probe. Pinned by the same mechanism the engine already uses for INV-2
(`tests/test_checklist_engine.py:3856`, `mock.patch.object(E.subprocess, "run", side_effect=AssertionError)`).

### Adapters out — two encoders, deliberately
```python
def canonical_bytes(content: dict) -> bytes:
    """Hashing form ONLY. Never written to disk."""
    return json.dumps(content, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")

def content_digest(content: dict) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(content)).hexdigest()

def render_manifest_json(envelope: dict) -> str:
    """Disk form: pretty, diff-friendly, authored key order."""
    return json.dumps(envelope, ensure_ascii=False, indent=2) + "\n"

def render_manifest_human(view: dict) -> str:
    """Courtesy view, exactly as render_human() is for state(). Not the interface."""
```

The split is the core ports move: **the digest encoding and the disk encoding are different adapters.**
Consequences — the drift check is immune to pretty-printing changes; the human-diff consumer gets
authored key order (`ref, declared_path, role, …`) instead of the alphabetical mush `sort_keys=True`
would produce; and a future adapter (YAML, a Markdown table, whatever #301 wants) plugs in without
touching either the projection or the contracted digest.

**Producer call** — one function, wired at the CLI boundary:
```python
emit_manifest(cl, step_id, *, resolver, out_dir) -> Path
```
Wired into `dispatch()` on `start <step>` — the same chokepoint the doctrine rail and the Trip policy
already ride, so the verb functions stay pure and existing exact-equality tests keep passing. Written
to `.agent-work/<work_id>/context/<step_id>.manifest.json`, with `.<rework_count>.` interposed on a
re-start after `reopen` (`rework_count` is already a real field on every task — no new counter).

"Produced on every deterministic assembly" is therefore defined as **every `start`**. Named honestly as
a definition, not a discovery — see §7.

**Consumer call:**
```python
def read_manifest(path) -> dict:
    """Parse, refuse an unknown `contract`, and verify the stored `content_digest`
    matches content_digest(view["content"]) — a hand-edited manifest is a refusal,
    not a silent pass."""
```
- **#301**: `episode["context"] = {"manifest": "<repo-relative path>", "content_digest": "sha256:…"}`.
  Pointer + digest, never a copy — the same rule the engine already enforces for refresh-request
  payloads ("payload carries POINTERS ONLY … never copies of state", `checklist_engine.py:1012-1027`).
- **Drift check (#307)**: `content_digest(manifest_state(declared_refs(cl, step), GitResolver().resolve_all(...))) == stored["content_digest"]`. One string compare. It never enumerates fields, so it can never fall out of sync with the schema.
- **Human reading a git diff**: reads the committed `<step>.manifest.json` directly.

---

## 5. The exclusion set

**The exclusion set is one JSON pointer: `/run`.** Not a field list. Not a per-field annotation.

```python
EXCLUDED = ("/run",)   # the drift check hashes `content`; it never sees `run`
```

Everything that legitimately varies lives in `run`: `generated_at`, `run_id`, `producer`, `host.os`,
`host.python`, `cwd`. The drift check does not filter anything out — it hashes a *different subtree*.
That is the difference between an exclusion set that is structurally separable (the brief's constraint 6)
and one that is a maintained list. Adding a new varying field later means adding it to `run`; no
consumer changes.

Two of the three named irreproducibility sources never reach `run` at all:
- **line endings** — normalised into the blob sha (§2, verified);
- **filesystem ordering** — declaration order, never a directory walk (§1).
- **locale** — `ensure_ascii=False` + explicit UTF-8 encode in both encoders; the disk write uses
  `open(..., "w", encoding="utf-8", newline="\n")`. The `newline="\n"` is load-bearing on Windows,
  where Python's text mode would otherwise translate `\n` → `\r\n` and hand a POSIX rebuild different
  bytes for identical content.

---

## 6. Self-scoring

**Depth — strong for consumers, taxed for implementers.** A consumer sees four root keys and one entry
shape. CRLF normalisation, base-dir search order, git tracked/dirty classification, blob computation,
`/`-normalisation, and the two-encoder split are all behind the seam. But three named ports is three
concepts an *implementer* must hold, and Port A currently has one adapter. Depth bought for the
consumer, paid by the maintainer.

**Locality — medium.** New `scripts/context_manifest.py`; ~10 lines at `dispatch()` in
`checklist_engine.py`; one optional spine field documented in `docs/CHECKLIST_SCHEMA.md`; one lint
script; `context_refs` added to the Commander spine template's `context` step. It does **not** fan out
into every skill's prose, because the declaration lives on the spine template. It does fan out to every
*spine template* that wants declarations — nine other Commander steps and the Admiral/Explorer/Scout
spines will eventually each want one. That is real, additive fan-out I am not hiding.

**Seam placement — strong, with one soft joint.** The resolver seam is where the tests want it (§ below).
The digest/disk split is where the drift check wants it. The declaration port is where the prose→data
migration wants it. The soft joint: `emit_manifest` hooks a *temporal* event (`start`), not a structural
boundary. "Every deterministic assembly" holds only because I define assembly as `start`. If context is
ever assembled outside `start` — a re-read mid-gate, a subagent dispatch — the acceptance criterion
silently stops holding with no test failing. That is my weakest seam and I will not dress it up.

**Testability — strong.** `MappingResolver` makes every branch reachable with no repo, no filesystem, no
subprocess. `manifest_state` is a pure function tested by table.

**Adversarial fixtures.** A round-trip over the shipped corpus proves the corpus is clean, not that the
tool is correct. Five fixtures that catch *this design* being broken:

1. **CRLF twin (false FAIL on valid input).** `MappingResolver` handed `b"a\r\nb\n"` and `b"a\nb\n"` for
   the same declared ref. `content_digest` must be identical. A producer that hashed raw bytes passes
   the real-corpus round-trip on one machine and fails here — this is the second-environment failure,
   caught without a second environment.
2. **Digest mutation sweep (silent PASS on invalid input — the important one).** Take a golden `content`,
   programmatically mutate *every leaf*: flip one hex digit of one `blob`; drop one entry; swap two
   entries; change one `state` from `committed` to `untracked`; null one `origin.commit`. Assert
   `content_digest` changes for **every** mutation. This is what catches a drift check that hashes a
   *subset* of content and therefore silently passes a corpus that genuinely changed — the failure mode
   no real-corpus test can produce.
3. **`run`-only variation (false FAIL).** Two manifests with every `run` field different (timestamp,
   run_id, os `nt` vs `posix`, python version, cwd) and byte-identical `content`. Digest must match; the
   drift check must PASS. This is the exclusion set's own test, and it fails loudly the day someone
   "helpfully" moves a timestamp into `content`.
4. **Absent vs undeclared (silent PASS).** Manifest X declares `docs/agents/GLOSSARY.md` and it is
   absent; manifest Y does not declare it. Their digests must differ. Catches the tempting
   "skip files that don't exist" optimisation — the exact defect shape of `b69e6c8`.
5. **Windows newline regression.** Write via the encoder, read the file back in **binary**, assert
   `b"\r" not in raw`. A test that reads it back in text mode passes on Windows regardless, which is
   how this bug ships.

**Foreclosure risk — low.** Each entry maps 1:1 onto a Stratum A assertion with no reshaping:
subject `blob:<sha>`, predicate `was-made-available-at(step)`, object `(work_id, step_id)`, source
`(manifest path, content_digest)`. `role` refines the predicate; `state` becomes an attribute of the
source. Deliberately **no `strength` field**: every manifest entry is by construction the same strength
(mechanically derived, deterministic), and shipping a per-entry strength now would invite callers to
vary confidence *inside* the manifest rather than in Stratum A — which is precisely the foreclosure the
brief warns about. `contract` gives Stratum A a version to migrate from.

---

## 7. What my constraint made me give up

- **Port A is speculative and I can't defend it on today's evidence.** There is exactly one declaration
  source (the spine field) and I cannot name a concrete second one. As a named protocol with a docstring
  and an indirection, it currently buys nothing but symmetry. If a reviewer wants it collapsed into
  `manifest_state`, that is a fair cut and I would take it. Ports B and C pay for themselves immediately
  (testability, purity); Port A does not.
- **Two encoders are more machinery than one, and they create a failure mode a single encoder does not
  have**: a manifest whose stored `content_digest` disagrees with its own on-disk `content` — a hand-edit,
  a bad merge. I have to pay for that with a verify-on-read in `read_manifest`, which a
  single-canonical-encoder design gets for free. I think the split is worth it (pretty-print changes
  can't break drift; the human diff stays readable) but it is not free and I am not calling it free.
- **`content` carries nothing host-specific — deliberately, at a real consumer's expense.** No absolute
  paths, no host repo name, no timestamps. The human reading a git diff has to look in `run` to answer
  "where did this come from on my machine". I traded that consumer's convenience for the drift check's
  cleanliness. It is a genuine loss, and the fitness-for-use argument against it is legitimate.
- **No file content, only digests.** A manifest read six months from now cannot reconstruct what the
  agent saw unless the blob is still reachable — and for `untracked`/`external` entries (`docs/agents/`,
  `.agent-work/LESSONS.md`) it very often will not be. Copying content would fix that and I refuse: the
  record would stop being a manifest and start being an archive, and the brief's "delivery, not use"
  boundary would blur. Named limitation, deliberately accepted.
- **Every new spine step that wants a declaration pays authoring cost**, and the imperative-vs-declaration
  lint is a hard prerequisite, not a nice-to-have. A design that put the declaration *inside* the prose
  (extraction by regex, as `verify_state_note.py` already does for `STATE_NOTE.template.md`) would have
  no drift hazard at all. I rejected it because regex-over-prose is not a port and cannot be swapped —
  but it is a real cost of my stance, not a free win.

---

## 8. Obligations offered to #301, and cross-interface risk

**#301 may rely on:**

1. **Identity/addressing.** Every manifest is addressable by `(repo-relative path, content_digest)`.
   `content_digest` is `"sha256:" + 64 lowercase hex`, stable across machines and OSes, and a pure
   function of `content` alone. Safe as a value key or a dedup key.
2. **`contract`** is an int at the envelope root, monotonically increasing; a breaking shape change
   bumps it. #301 may pin and refuse an unknown value.
3. **The context field may be exactly** `{"manifest": "<repo-relative path>", "content_digest": "sha256:…"}`.
   If #301 prefers self-containment, it may embed the whole `content` object verbatim instead — `content`
   carries no absolute paths and no host facts, so it stays valid anywhere. Both are supported.
4. **`content.entries` is order-stable, never deduplicated, and never drops an entry** — including
   `absent` ones. Count and order are contracted facts.
5. **Every entry answers "which bytes"** (`blob`, present unless `state == "absent"`) and states
   explicitly whether it can answer "which published revision" (`state` + `origin`).

**#301 must NOT rely on:**

- Anything under `/run` — that is the declared exclusion set and may differ between two runs that
  produced identical context.
- The on-disk pretty-printing. Only `content`'s canonical hashing form is contracted; the disk adapter
  may change without a `contract` bump.
- The file path `.agent-work/<work_id>/context/<step>.manifest.json` if the work-area layout moves.
  Store the path #301 was handed; do not reconstruct it.

**Cross-interface risks — flagged, not designed around:**

- **Cardinality.** I emit **one manifest per spine step**. If #301's episode record assumes a single
  `context` field per episode and an episode spans several steps, #301 gets N pointers where it expected
  one. I will not silently redesign to one-per-episode (it would destroy per-step attribution, which is
  the whole point). I offer a list-of-pointers shape and flag that if #301 has already assumed
  cardinality 1, **one of us must change** — a float to the Admiral, not a cross-edit.
- **Size, if embedded.** If #301 needs the context field self-contained, embedding `content` is
  unbounded: it grows linearly with declared refs (~1.6 KB canonical for six entries here). I cannot
  bound it. If #301 has a size budget on the episode record, the pointer form is the only safe option
  and #301 should say so.
- **Emission timing.** My producer fires at `start`. If #301 timestamps or orders episodes against
  something other than step transitions, the manifest's `run.generated_at` is *not* an episode boundary
  and must not be used as one — it lives in the exclusion set precisely because it is not load-bearing.
