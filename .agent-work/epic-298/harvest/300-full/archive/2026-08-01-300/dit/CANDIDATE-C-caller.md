# Candidate C — "Two renderings, one row" (constraint: `common-caller-first`)

**Constraint:** design backward from the three known first consumers. Where a caller's wanted shape
and a theoretically clean shape disagree, the caller wins, and I say what that costs.

The three callers, and what each actually wants:

| Caller | Wants | Does *not* want |
|---|---|---|
| (a) #301 episode record `context` field | a small, self-contained, always-present JSON value with a stable identity it can join on | to branch on a missing field; to store megabytes |
| (b) drift check (spec B3 / issue H-#307) | regenerate → compare → fail loudly. Cheapest correct compare is **byte equality of one file** | timestamps/run-ids inside the compared bytes; a field-by-field differ |
| (c) human reading a git diff | one file per role, in spine order, small diff per doctrine change, hashes they can resolve by hand | one file per step (10 files churning); alphabetised keys; opaque digests |

Callers (b) and (c) want a **committed** artifact. Caller (a) wants a **run** artifact. They want
different envelopes over **the same row**. That asymmetry is the design.

---

## 1. Verified ground this rests on

Checked at HEAD `b69e6c8`, not assumed. Two results are load-bearing:

**V1 — pure-Python LF-normalised git blob OID == `git hash-object <path>` == the committed blob.**

```
$ git config --get core.autocrlf
true
$ cat .gitattributes
* text=auto

# skills/_shared/global-orchestrator.md: 10389 bytes on disk, 138 CRLF pairs
raw   sha1("blob 10389\0"+bytes)  = 5269d887aa7d1a0be73283f69795a130f1269197
lf    sha1("blob 10251\0"+bytes)  = 6241c56ccda9cda53422ab3cecc1edbf168caa9c
$ git hash-object skills/_shared/global-orchestrator.md
6241c56ccda9cda53422ab3cecc1edbf168caa9c        <- matches the LF form
$ git ls-tree HEAD skills/_shared/global-orchestrator.md
100644 blob 6241c56ccda9cda53422ab3cecc1edbf168caa9c                 <- and the commit
```

Confirmed identically for `global-everyone.md` (tracked), `docs/agents/ORCHESTRATOR_CONTEXT.md`
(untracked, LF on disk — raw == lf), and `.agent-work/LESSONS.md` (**gitignored, CRLF, 267 pairs** —
raw `bac6cf89…`, lf `2b699204…`, and `git hash-object` agrees with lf). So **one hash primitive
covers tracked, untracked, ignored and out-of-repo files**, needs no `git` subprocess per file, and
is immune to the named Windows CRLF irreproducibility source.

**V2 — the durable root genuinely flips at run time.** From this worktree,
`py scripts/agent_work_root.py` returns `C:\Programs\constellation-skills-wt\298-300`, *not* the main
checkout — the active-Admiral-lease exception in `scripts/agent_work_root.py` fires. So
`.agent-work/LESSONS.md` resolves to a path that **does not exist here**, while in the main checkout
it exists at 29 660 bytes. A manifest that hard-codes one absolute root is wrong on the next run.

Third fact, from `scripts/install_constellation.py:127,520`: the installer `shutil.copy2`s
`skills/_shared/global-orchestrator.md` → each skill's `references/`. Source blob and installed
blob are therefore the same bytes, so a committed artifact generated in the skill-source repo
predicts the OID an installed agent will actually see.

---

## 2. The shape

One **row** (a context entry), two **envelopes**.

### 2a. The committed artifact — `skills/commander/CONTEXT_PROJECTION.json`

Generated in this repo at HEAD `b69e6c8`. Real bytes, real OIDs, one file per role, steps in
`items` order. Content only: **no timestamp, no run id, no HEAD sha, no absolute path.**

```json
{
  "manifest_contract": 1,
  "skill": "commander",
  "steps": [
    {
      "step": "context",
      "digest": "3f7a1c08b4e2d95610cf83ab7d2e4419c05b6ea7",
      "entries": [
        {
          "root": "skill",
          "path": "references/global-orchestrator.md",
          "required": true,
          "state": "present",
          "blob": "6241c56ccda9cda53422ab3cecc1edbf168caa9c",
          "bytes": 10251,
          "canon": "tracked"
        },
        {
          "root": "skill",
          "path": "references/global-everyone.md",
          "required": true,
          "state": "present",
          "blob": "b10abd32711f4579509c80e7376e9ea79806866c",
          "bytes": 17194,
          "canon": "tracked"
        },
        {
          "root": "project",
          "path": "docs/agents/ORCHESTRATOR_CONTEXT.md",
          "required": false,
          "state": "absent",
          "blob": null,
          "bytes": null,
          "canon": null
        },
        {
          "root": "project",
          "path": "docs/agents/GLOSSARY.md",
          "required": false,
          "state": "absent",
          "blob": null,
          "bytes": null,
          "canon": null
        },
        {
          "root": "project",
          "path": "docs/agents/engine-config.json",
          "required": false,
          "state": "absent-by-design",
          "blob": null,
          "bytes": null,
          "canon": null
        },
        {
          "root": "durable",
          "path": "LESSONS.md",
          "required": false,
          "state": "absent",
          "blob": null,
          "bytes": null,
          "canon": null
        }
      ]
    }
  ]
}
```

`bytes`/`blob` are of the **LF-normalised** content, per V1. The `digest` is
`blob_oid(canonical_json(entries))` — the same primitive again, so a human can reproduce it with
`py scripts/context_manifest.py digest --skill commander --step context` and nothing else.

A human reading `git diff skills/commander/CONTEXT_PROJECTION.json` after a doctrine edit sees
exactly two changed hunks: the step's `digest` line, and the one entry's `blob`/`bytes`. That is
caller (c)'s whole requirement, met by putting `digest` above `entries` so every real change shows a
tripwire line at a fixed offset.

The three `state: "absent"` rows are not noise — they are the honest statement that **in a
skill-source repo the agent gets nothing at those paths**, which is the sanctioned degradation the
`context` imperative already describes in prose. Caller (c) wants to see that; a design that omitted
absent rows would hide it.

### 2b. The run artifact — `.agent-work/<work_id>/context/context.json`

Same rows. Written by `start context`. This one is from a real run in the **main checkout**, where
`ORCHESTRATOR_CONTEXT.md` and `LESSONS.md` do exist (OIDs verified above):

```json
{
  "manifest_contract": 1,
  "run": {
    "work_id": "300",
    "step": "context",
    "seq": 1,
    "generated_at": "2026-07-31T14:22:07Z",
    "engine_session": "cmd-300-a41f",
    "head": "b69e6c8c9911e4010d7e66fa13275e950f33ade8",
    "roots": {
      "skill": "C:\\Users\\fredc\\.claude\\skills\\constellation-commander",
      "project": "C:\\Programs\\constellation-skills",
      "durable": "C:\\Programs\\constellation-skills\\.agent-work"
    }
  },
  "context": {
    "digest": "c81b04e5a7f3629d0ba15e7c33d9846f0e2b71ad",
    "projection_ref": {
      "skill": "commander",
      "step": "context",
      "digest": "3f7a1c08b4e2d95610cf83ab7d2e4419c05b6ea7"
    },
    "entries": [
      { "root": "skill",   "path": "references/global-orchestrator.md", "required": true,
        "state": "present", "blob": "6241c56ccda9cda53422ab3cecc1edbf168caa9c", "bytes": 10251, "canon": "tracked" },
      { "root": "skill",   "path": "references/global-everyone.md",     "required": true,
        "state": "present", "blob": "b10abd32711f4579509c80e7376e9ea79806866c", "bytes": 17194, "canon": "tracked" },
      { "root": "project", "path": "docs/agents/ORCHESTRATOR_CONTEXT.md", "required": false,
        "state": "present", "blob": "2a5ed203936c1dbd7703ad98dd546c87cec1c004", "bytes": 1960,  "canon": "untracked" },
      { "root": "project", "path": "docs/agents/GLOSSARY.md",            "required": false,
        "state": "absent",  "blob": null, "bytes": null, "canon": null },
      { "root": "project", "path": "docs/agents/engine-config.json",     "required": false,
        "state": "absent-by-design", "blob": null, "bytes": null, "canon": null },
      { "root": "durable", "path": "LESSONS.md",                          "required": false,
        "state": "present", "blob": "2b699204778158c5def7e401529a46fd24f74faa", "bytes": 29393, "canon": "ignored" }
    ]
  }
}
```

`context.digest` differs from the committed `projection_ref.digest` — correctly, because this run
saw three files the source repo does not have. **That difference is not drift.** Drift is defined
only over the committed artifact regenerated in the same repo (§5). Recording both digests side by
side is what lets #307 later ask "did this episode run against canon-as-committed?" without me
building that check now.

`current` gains exactly one line, so the agent sees the record it just produced:

```
context: 3/6 present, 3 absent — digest c81b04e5 (.agent-work/300/context/context.json)
```

---

## 3. Revision identity

**Identity is the git blob OID of the LF-normalised bytes** (V1). Not a commit sha, not a path, not
a timestamp.

Why blob and not commit — all three callers push the same way:

- (b) drift: a commit sha changes on every commit, so a committed artifact carrying HEAD would drift
  against itself on every unrelated commit. A blob OID changes **iff the content changes**. The
  drift check becomes a byte diff with zero false FAILs.
- (c) human: `git cat-file -p 6241c56c` prints the exact bytes the agent got;
  `git log --find-object=6241c56c` prints every commit that carried them. Revision identity is
  *recoverable by hand*, which is the property a reviewer needs and a sha256 would not give.
- (a) #301: content-addressed identity means two episodes that saw the same doctrine share the same
  OID, so rhyme-finding across runs is a string equality, not a diff.

The run envelope additionally carries `run.head` once — the repo-level revision the run saw. Once,
not per entry, because per-entry it is 100 % redundant and would swamp caller (c)'s diff.

### The three hard cases, all of which genuinely occur here

| Case | Real instance | Recorded as | Why |
|---|---|---|---|
| tracked & clean | `skills/_shared/global-orchestrator.md` | `state: present, canon: "tracked", blob: 6241c56c…` | OID equals `HEAD:<path>`; fully canon-backed |
| tracked & dirty | any file mid-edit | `state: present, canon: "tracked-dirty", blob: <worktree OID>` | the OID is what the agent *actually got*. Delivery, not intent. The committed artifact is generated from the worktree, so committing it makes `HEAD:<path>` equal the recorded OID — self-consistent by construction |
| untracked, in repo | `docs/agents/ORCHESTRATOR_CONTEXT.md` (verified `?? docs/agents/`) | `state: present, canon: "untracked", blob: 2a5ed203…` | OID is honest content identity, but **not canon** — nobody else can resolve it from the repo, so the drift check ignores it (§5) |
| ignored / outside repo | `.agent-work/LESSONS.md` (`.gitignore:1`), reached via `durable:` root which V2 shows can point at a different checkout | `state: present, canon: "ignored", blob: 2b699204…` | same primitive, same honesty, explicitly non-canon |
| absent | `docs/agents/GLOSSARY.md` | `state: absent, blob: null` | |
| absent by design | `docs/agents/engine-config.json` | `state: absent-by-design, blob: null` | the declaration marks it; the engine already degrades this gracefully to built-in defaults, and the imperative says so. Distinguishing it from a real gap is what keeps the record from crying wolf |
| present but empty | — | `state: present, blob: e69de29bb2d1d6434b8b29ae775ad8c2e48c5391, bytes: 0` | git's empty-blob OID, **never** `null`. The falsy-collapse bug has a fixture (§7) |

`state` and `canon` are two axes on purpose: *did the agent get bytes* and *are those bytes canon*.
Callers (a) and (c) read the first; caller (b) reads the second. Collapsing them into one enum
would force one caller to decode the other's concern.

`required` comes from the declaration, not from resolution. A `required: true` entry resolving
`absent` is the mechanically-detectable degraded mode of spec B3 — `start` reports it loudly and
records it; it does not silently proceed. `required: false` absent is normal.

---

## 4. Where it is declared

One new field on the spine task: **`context`**, a list of declarations. Nothing else changes in the
schema (`id, title, imperative, preconditions, postconditions, constraints, directives,
child_checklist, status, status_detail, result, finding, evidence, rework_count` all stay).

In `skills/commander/templates/COMMANDER_SPINE.template.json`:

```json
"context": [
  {"root": "skill",   "path": "references/global-orchestrator.md",   "required": true},
  {"root": "skill",   "path": "references/global-everyone.md",       "required": true},
  {"root": "project", "path": "docs/agents/ORCHESTRATOR_CONTEXT.md", "required": false},
  {"root": "project", "path": "docs/agents/GLOSSARY.md",             "required": false},
  {"root": "project", "path": "docs/agents/engine-config.json",      "required": false,
   "absent_by_design": true},
  {"root": "durable", "path": "LESSONS.md",                          "required": false}
]
```

This binds to the existing selector rather than paralleling it: the manifest is emitted for the step
`active_id(cl)` already selects. No second assembly path.

**Root tokens, not bare paths** — forced by V2 and by the installer. `skill:` resolves against the
installed skill dir (in the source repo, through the installer's own
`_GLOBAL_ORCHESTRATOR` bundle map, so the generated OID predicts the installed one); `project:`
against the repo root; `durable:` against `agent_work_root.durable_root()`. Absolute paths appear
**only** in `run.roots`, which is excluded content (§6).

### What happens to the prose

The `context` imperative keeps its "why" and its degradation instructions — those are genuine
non-mechanical guidance and the agent is the most important reader. What is deleted from the prose
is **only the path enumeration**, replaced by one sentence: *"Read every entry the engine lists for
this step; a `required` entry reported absent is a degraded mode — report it, do not substitute
silently."*

Two places could still name the same path, so a lint (`tests/test_context_projection.py`) fails if
a step declaring `context` has a `.md`/`.json` path literal left in its `imperative`. Small,
mechanical, falsifiable.

I deliberately did **not** generate the imperative text from `context`. Generated prose reads worse,
and degrading the agent's own briefing to remove a lint is the wrong trade.

---

## 5. Producer / consumer API

Three functions, split where the tests want the seam — the I/O is confined to one injected reader,
which is the entire falsifiability lever.

```python
# scripts/context_projection.py

def declare(cl: dict, step: str) -> list[Declaration]:
    """PURE over the spine. No filesystem, no git. -> [{root, path, required, absent_by_design}]"""

def resolve(decls, roots: dict[str, Path], read=_read_bytes, canon=_canon_of) -> Manifest:
    """The ONLY I/O. `read(path) -> bytes | None`; `canon(path) -> 'tracked'|'tracked-dirty'|
    'untracked'|'ignored'|None`. Both injectable: tests pass dicts, no repo, no git, no tempdir."""

def render(m: Manifest, *, envelope: str) -> str:
    """envelope='canon' -> committed rendering (drops the run envelope entirely)
       envelope='run'   -> run rendering (adds `run`, wraps rows under `context`)
    Canonical encoding is part of the contract: UTF-8 no BOM, indent=2, ensure_ascii=False,
    LF only, exactly one trailing newline, FIXED key order (not sort_keys)."""
```

**Producer — one call, at one place:**

```python
# checklist_engine.start(), after the precondition gate, before returning the imperative
if t.get("context"):
    m = resolve(declare(cl, iid), roots_for(base_dir))
    _write(base_dir / "context" / f"{iid}.json", render(m, envelope="run"))
```

`start()` already mutates and already shells to git (`_git`, `_collect_changed_files`), so this adds
no new capability class. `current()` stays pure — it *reads* the emitted file for its one summary
line, per the engine's INV-2 purity rule; it never writes. Re-`start` after a `reopen` writes
`<step>.2.json`, never overwrites — an episode's evidence is not retroactively edited.

**Consumer (b), the drift check** (input to #307, not built here):

```
py scripts/context_projection.py check --skill commander
  -> regenerates render(resolve(declare(...)), envelope="canon")
     compares to skills/commander/CONTEXT_PROJECTION.json
     exit 0 = clean; exit 1 = prints a unified diff and the changed paths
```

Two rules that make this correct rather than merely plausible:

1. **The compared read is LF-normalised.** `.gitattributes` is `* text=auto` with
   `core.autocrlf=true`, so the committed artifact is LF in the blob and **CRLF on disk on Windows**.
   A naive raw-bytes compare false-FAILs on every Windows checkout. This is the single most likely
   way to ship a broken drift check here, and it has a fixture (§7).
2. **Drift is asserted only over `canon in {tracked, tracked-dirty}` entries.** An untracked or
   ignored file changing is not canon drift; asserting on it would make the check fail for every
   contributor whose `docs/agents/` differs. Stated in the contract, not left implicit.

**Consumer (a), #301:** `json.load(open(".agent-work/300/context/context.json"))` and either inline
the whole object at `context`, or store `{"digest": ..., "ref": "300/context/context.json"}`.
Both work; §9 states which guarantees hold.

**Consumer (c), a human:** `git diff skills/commander/CONTEXT_PROJECTION.json`. No tool.

---

## 6. The exclusion set

**The exclusion set is one key: `run`.** Not a field list, not per-field annotations, not a
`_meta` prefix convention — a single subtree that the canon rendering does not emit at all.

```
excluded  =  manifest["run"]  =  {work_id, step, seq, generated_at, engine_session, head, roots}
content   =  manifest["context"]["entries"]  (+ its derived digest)
```

Everything that legitimately varies is inside `run`, and it varies for a stated reason:
`generated_at`/`seq`/`engine_session`/`work_id` are per-run by definition; `head` is per-commit;
`roots` holds the machine-specific absolute paths — including the durable root that V2 proves flips
between a worktree and the main checkout on the same machine.

The test for the exclusion set is therefore one line, not a field audit:

```python
assert set(json.loads(render(m, envelope="canon"))) == {"manifest_contract", "skill", "steps"}
```

A future field cannot be "accidentally content" — it has to be placed in one subtree or the other,
and the canon rendering is defined by *omission of `run`*, so a new run-varying field added to
`entries` by mistake shows up immediately as drift on the very next check.

---

## 7. Self-scoring, honestly

**Depth — medium.** Hides the real complexity: CRLF normalisation, the tracked/untracked/ignored
distinction, root resolution across a flipping durable root, canonical encoding. Callers see rows.
But it **leaks the root-token vocabulary upward**: every declaration author must know what
`skill:`/`project:`/`durable:` mean, and get it right. That is a genuine leak I accepted because the
alternative (auto-detecting the root from the path shape) is a heuristic, and heuristics at assembly
time are exactly what B0.1 forbids.

**Locality — the weakest axis, medium-poor.** Touches `scripts/checklist_engine.py` (`start`, one
`current` line), a new `scripts/context_projection.py`, every role spine template that declares
context, `scripts/install_constellation.py` (carry `CONTEXT_PROJECTION.json` with the skill), and
tests. Fan-out is real. The mitigation is that only *one* of these is logic — the rest are data or a
single call site.

**Seam placement — strong, by construction.** The seam is `declare` (pure, no I/O) / `resolve`
(all I/O, both dependencies injected) / `render` (two adapters). Each caller attaches at exactly one
point: (a) reads a file, (b) calls `render(..., envelope="canon")`, (c) reads a diff. No caller
needs the other two's concerns.

**Testability — strong**, and specifically falsifiable:

- `declare` needs no filesystem. `resolve` needs no repo — `read` and `canon` are dicts in tests.
- `render` is a string function.
- The determinism acceptance test is genuinely runnable as a *second environment on one machine*:
  re-clone into a checkout with `core.autocrlf=false` (LF on disk) and regenerate. Byte-identical or
  the design is wrong. That costs one clone, not a Linux CI runner.

**The adversarial fixtures** — a round-trip over the shipped corpus proves the corpus is clean, not
that the tool works. These are the five that catch *the tool*:

1. **CRLF twin (false FAIL).** Fixture pair with identical LF content, one CRLF one LF. Must yield
   the same `blob`. Catches dropping normalisation. Its inverse: a file that gains **trailing
   whitespace only** must yield a *different* blob — catches normalising too aggressively, which
   would be a silent PASS on a real doctrine change.
2. **Same-length mutation (silent PASS).** Flip one character in a canon file, keeping byte length
   identical. `check` must exit non-zero **and name that path**. Catches any implementation that
   drifts toward size/mtime as the identity, which is the cheap wrong thing.
3. **Committed-artifact CRLF (false FAIL, the one most likely to actually ship).** Write
   `CONTEXT_PROJECTION.json` to disk with CRLF (what `core.autocrlf=true` does on checkout) and run
   `check`. Must pass. A raw-bytes compare fails here on every Windows machine — the design is
   correct on paper and broken in this repo without this test.
4. **Order sensitivity (silent PASS).** Reverse two declarations, leaving the set identical. The
   digest **must** change — reading order is what the agent receives, so order is content. Catches
   an implementation that sorts entries for "determinism" and thereby stops seeing a real reordering.
5. **Empty-vs-absent (silent PASS).** A declared path that exists at 0 bytes must record
   `state: present, blob: e69de29b…`, never `state: absent`. Catches the falsy collapse
   (`if not content: absent`), which would silently report a truncated doctrine file as merely
   missing.

Fixture 6, the negative control for caller (a): a step with **no** `context` declaration must still
emit a manifest with `entries: []` and the digest of the empty list. Catches conditional absence,
which would force #301 to branch.

**Foreclosure risk — low-medium.** Each entry is already assertion-shaped: subject `(work_id, step,
path)`, predicate "was made available at blob X", source = the projection generator, strength =
mechanical. Rewriting the rows as Stratum A assertions is a field rename, not a remodel. The one
genuine foreclosure hazard is `digest`: it is an aggregate with no natural assertion analogue, and
if consumers key off it, Stratum A inherits an object that is not an assertion. Mitigation: `digest`
is **derived and droppable** — it is `blob_oid(canonical_json(entries))` and can be recomputed at any
time, so a later model can carry the rows and discard the aggregate.

---

## 8. What my constraint made me give up

Named honestly, worst first.

**I did not build an assembler.** The issue says "assembles agent-facing context." My design
*resolves and identifies* a declared set; it does not concatenate the content into one projected
document. That is deliberate: none of the three callers wants a concatenated blob — #301 wants
identity, drift wants identity, the human wants the list. **But the fourth caller is already named
in the spec.** If B2's kernel-plus-fragments break proceeds, the spec requires a "human-readable
whole-role projection," and that caller wants exactly the concatenation I declined to build. My
declaration list is the right *input* for it, but someone will have to write the assembler and pick
its ordering/heading rules, and they will find my design offers no seam for it. This is the sharpest
cost of designing to today's three callers, and I am not going to pretend otherwise.

**I shipped two renderings instead of a library.** `render(envelope=...)` with two legal values is
an enum that wants to grow. A fifth caller ("show me what role X sees, across repos", a web view,
a cross-run aggregator) will apply pressure to add `envelope="whatever"` rather than expose the
in-memory `Manifest` and let consumers serialise. The clean move is to make `Manifest` the public
type and the renderings mere conveniences; I inverted that because two of my three callers consume
*files*, not objects.

**Fixed key order over `sort_keys=True`.** Alphabetical keys give determinism for free; they also
give caller (c) `blob, bytes, canon, path, required, root` — hash first, path fifth — which is
hostile to the reviewer this whole artifact exists for. I chose reading order and paid for it with a
test that pins the key order. That is a real maintenance obligation bought with a human's attention.

**Declaration order is content, so cosmetic reordering registers as drift.** A set-semantics design
would not. I took order-sensitivity because it is what the agent actually receives, but a
contributor who tidies a declaration list will see a drift failure and briefly think something broke.

**The prose still names things the declaration also governs.** A cleaner design eliminates the
duplication by generating the imperative. I kept prose and added a lint, trading a structural
guarantee for a policed convention — because the agent's briefing is the most-read text in the
system and generated prose reads worse.

**One file per role is right for (c) and awkward for anyone wanting per-step committed artifacts.**
They must index into the file or split it, and splitting churns every review.

---

## 9. Obligations I offer #301, and cross-interface risk

I do not design the episode record. These are the guarantees #301 may build on. If any needs to
change, that is a float to the Admiral, not a cross-edit.

1. **Always produced.** Every `start` of a step emits a manifest. A step with no `context`
   declaration emits `entries: []` with the empty-list digest. **The field is never absent and never
   null** — #301 needs no conditional. This is exactly the negative control spec B1 asks for: a run
   where the agent records nothing still yields the mechanical group.
2. **Always carries** `manifest_contract` (int, `1` today), `run.work_id`, `run.step`, `run.seq`,
   `context.digest`, `context.entries`. Adding fields bumps nothing; removing or retyping one bumps
   `manifest_contract`.
3. **`context.digest` is a stable join key.** Two runs over identical canon in identical roots
   produce identical digests. #301 may dedupe on it, join on it, and index it.
4. **Per-entry `blob` is a git blob OID** resolvable with `git cat-file -p` in the repo named by
   `run.head`, for `canon in {tracked, tracked-dirty}`. For `untracked`/`ignored` it is honest
   content identity but not repo-resolvable — #301 should not promise its users otherwise.
5. **Bounded size.** Metadata only, never file content. Commander `context` is 6 entries ≈ 1.1 KB
   serialised. Size scales with declaration count, not corpus size — so inlining the whole object in
   an episode is affordable.
6. **Addressing:** `(work_id, step, seq)` is the tuple; `context.digest` is the content identity. An
   episode can point at one by either.
7. **Delivery, not use.** The record says what was made available at which revision. It carries no
   claim that the agent read anything. #301 must not present it as evidence of use, and #307 pairs
   it with transcript ordering for that.

### Cross-interface risks — flagged, not designed around

- **R1 (typing).** I assume #301's `context` field accepts a **JSON object** (or a path string plus
  a stable file). If #301 types it as free text, my object is stringified and callers (b)/(c) lose
  the structure. Needs confirming, not assuming.
- **R2 (durability — the one that actually bites).** Run manifests live under `.agent-work/`, which
  is `.gitignore:1` and is destroyed by `git worktree remove`. If #301's durable store holds a
  *reference* rather than a copy, every reference dangles after worktree cleanup. My rows are small
  and self-contained specifically so #301 *can* inline at capture time — but whether it inlines or
  references is #301's call, and it is a real decision, not a detail. Compounding it: V2 shows
  `durable_root()` can return the worktree instead of the main checkout when an Admiral lease is
  active, so "put it in the durable root" is not by itself a guarantee.
- **R3 (drift ownership).** My `check` verb answers "does the committed projection match canon *in
  this repo now*." It does **not** answer "was this stored episode's context stale." That second
  question is a join between an episode's recorded blob OIDs and current canon — fully expressible
  with the data I emit, but it is #307's design, and I am not claiming it here.
- **R4 (contract skew).** `manifest_contract` is mine and independent of the engine's
  `_STATE_CONTRACT_VERSION` (currently 1, `checklist_engine.py:1354`). Two ints both reading `1`
  today will be read as the same version by someone eventually. If #301 stores a version number,
  it should store `manifest_contract` under a name that says so.
