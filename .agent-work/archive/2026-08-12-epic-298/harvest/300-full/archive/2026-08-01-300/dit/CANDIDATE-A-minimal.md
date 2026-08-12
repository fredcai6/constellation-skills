# Candidate A — "Four Keys"

**Constraint: `minimal-interface` (the YAGNI arm).**

One line: **a manifest is `{contract, step, files:[{path, rev}]}` — a flat, timestamp-free,
content-addressed, declaration-ordered list, produced by one new pure function beside `state()`
and printed by one new read-only engine verb. There is nothing else in it.**

Every element below survived the question *what breaks today if this is absent?* Everything that
did not survive is listed in §7 and §8 with the cost named.

---

## 1. Ground truth I verified before designing (not assumed)

Run in the worktree at `b69e6c8`:

| Claim | Command | Result |
|---|---|---|
| Git's blob OID is reproducible in-process | `py -c "sha1(b'blob %d\0' + content.replace(CRLF,LF))"` on `skills/_shared/global-orchestrator.md` | `6241c56ccda9cda53422ab3cecc1edbf168caa9c` — **identical** to `git rev-parse HEAD:skills/_shared/global-orchestrator.md` |
| …and CRLF is the whole difference | `git hash-object --no-filters` same file | `5269d887…` — different. Working tree is CRLF (`core.autocrlf=true`, 10389 bytes, contains `\r\n`) |
| It works for files outside the repo | `git hash-object C:\Programs\constellation-skills\.agent-work\LESSONS.md` | `2b699204…` = my LF-normalised sha1; raw-byte sha1 is `bac6cf89…` |
| `docs/agents/` genuinely absent here | `ls docs/agents` in this worktree | `No such file or directory` |
| …and untracked-but-present in the main checkout | `ls C:\Programs\constellation-skills\docs\agents\` | `ORCHESTRATOR_CONTEXT.md` only (LF, 1960 B, oid `2a5ed203936c1dbd7703ad98dd546c87cec1c004`) |
| `_shared/` is copied verbatim into each skill's `references/` at install | `install_constellation.py:121-135` (`SKILL_REFERENCE_BUNDLES`, commander → `_GLOBAL_ORCHESTRATOR`) | verbatim copy, so source oids are the delivered oids |
| The selector to extend | `active_id(cl)` at `checklist_engine.py:184` | "first item in order that is not terminal" — this is the whole selector |

The last row is the load-bearing one for `decision:extend-dont-parallel`: I add no selection logic
at all. I call `active_id(cl)`.

---

## 2. The shape — real bytes

Declaration on the Commander spine's `context` step (see §4), and the manifest it produces.
The three non-null `rev` values below are **real, computed** oids from the commands in §1.

```json
{
  "contract": 1,
  "step": "context",
  "files": [
    { "path": "skill:references/global-orchestrator.md", "rev": "6241c56ccda9cda53422ab3cecc1edbf168caa9c" },
    { "path": "skill:references/global-everyone.md",     "rev": "b10abd32711f4579509c80e7376e9ea79806866c" },
    { "path": "repo:docs/agents/ORCHESTRATOR_CONTEXT.md", "rev": "2a5ed203936c1dbd7703ad98dd546c87cec1c004" },
    { "path": "repo:docs/agents/GLOSSARY.md",             "rev": null },
    { "path": "repo:docs/agents/engine-config.json",      "rev": null },
    { "path": "work:LESSONS.md",                          "rev": "2b699204778158c5def7e401529a46fd24f74faa" }
  ]
}
```

Serialised as: **UTF-8, no BOM, `json.dumps(m, indent=2, ensure_ascii=False)` + one `\n`, written
with `newline="\n"`.** The encoding is part of the contract, not a detail, because byte-comparison
*is* the determinism test (§6). On Windows the `newline="\n"` is not optional.

That is the entire schema. Four keys, two of them inside `files[]`.

**Why each key survives deletion:**

- **`contract`** (int) — the only field justified by a *future* rather than by today's read, and
  it earns it: #301 is designing a **durable** store right now. An unversioned record persisted to
  disk can never be safely reinterpreted; the break is not hypothetical, it is the flag day #301
  would eat. It also mirrors `_STATE_CONTRACT_VERSION` at `checklist_engine.py:1354`, so the
  engine has one versioning idiom, not two.
- **`step`** (str) — without it the object is unattributable. The same repo yields a different set
  per step; #307's drift check must know *which declaration* to regenerate from; #301 must be able
  to hold several and tell them apart. Breaks today, three ways.
- **`files`** (ordered list) — the payload. **Order is content**, not presentation: doctrine has
  precedence ("inherited global doctrine, *then* project deltas"), and the delivery order is the
  reading order. It is never sorted (see §6).
- **`path`** (str) — `scheme:posix/relative/path`. Three schemes, resolved by the caller (§5):
  `skill:` (the running skill's install dir), `repo:` (project root), `work:` (the `.agent-work`
  root). All three are needed *today* by the one worked example: `references/…` is skill-relative,
  `docs/agents/…` is repo-relative, and `.agent-work/LESSONS.md` genuinely lives in a different
  checkout when a run happens in a worktree. A scheme prefix inside the existing string costs zero
  new fields.
- **`rev`** (40-hex str, or `null`) — acceptance criterion 2. See §3.

---

## 3. Revision identity

**`rev` is the git blob OID of the LF-normalised bytes that were delivered — computed in-process,
never by subprocess:**

```python
def _rev(data: bytes) -> str:
    body = data.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\x00" % len(body) + body).hexdigest()
```

Verified in §1 to equal `git rev-parse HEAD:<path>` for tracked, clean files. That equality is the
whole design: **one identity function, one field, no case analysis.**

| Situation | What happens | Why this is right |
|---|---|---|
| Tracked and clean | `rev` == the committed blob OID; `git cat-file -p <rev>` retrieves it | the manifest is joinable to git history for free |
| Tracked and **dirty** | `rev` == the OID of the bytes the agent actually got, which is *not* in the object DB | this is the honest answer. A commit SHA would have lied about what was delivered |
| **Untracked** (`docs/agents/ORCHESTRATOR_CONTEXT.md`) | same computation, real oid (`2a5ed203…`) | no special case, no `tracked:` flag |
| **Outside the repo** (`.agent-work/LESSONS.md`, ignored, in another checkout) | same computation, real oid (`2b699204…`) | no `source_repo:` field |
| **Absent** (`docs/agents/GLOSSARY.md`) | `rev: null`, entry retained, exit 0 | absence-by-design is normal here; a declared-but-missing file must be *recorded*, not fatal |
| Present but unreadable (permission, is-a-directory) | **raises**; assembly fails loudly | keeps `null` meaning exactly one thing |
| Resolves outside its declared root (`..` traversal) | **raises** | cheap guard; a declaration that escapes its root is a spine bug |

**No repo commit SHA anywhere.** What breaks today if it is absent? Nothing: every entry already
carries a finer-grained identity that survives dirty trees, worktrees, and untracked overlays — all
three of which occur in this corpus and none of which a commit SHA describes correctly. The cost is
real and stated in §8.

Residual honesty: `rev` proves *identity*, not *retrievability*. For an untracked file the oid names
content that git cannot hand back. Drift detection only needs identity; forensic replay would need
more, and #300 is not asked for replay.

---

## 4. Where the context set is declared

**One new optional key on the Task object: `context` — an ordered list of scheme-prefixed path
strings.** Nothing else.

```json
"context": {
  "id": "context",
  "title": "Load baseline context",
  "context": [
    "skill:references/global-orchestrator.md",
    "skill:references/global-everyone.md",
    "repo:docs/agents/ORCHESTRATOR_CONTEXT.md",
    "repo:docs/agents/GLOSSARY.md",
    "repo:docs/agents/engine-config.json",
    "work:LESSONS.md"
  ],
  "imperative": "Read your inherited global doctrine …",
  "…": "every other field unchanged"
}
```

Documented as one row in `docs/CHECKLIST_SCHEMA.md`'s Task table, next to `constraints` /
`directives`. A step with no `context` key yields `files: []` — every existing spine keeps working
untouched, so the fan-out is *only* the templates I choose to annotate (Commander first).

Naming hazard, flagged rather than hidden: `tasks["context"]["context"]` is legal but reads badly.
`context_files` avoids it at the cost of a longer name. I pick `context`; this is cosmetic and the
panel can flip it for free.

**No globs. No directory patterns. No `optional:` flags. No per-entry labels or reasons.** A glob
would import filesystem ordering — one of the three named irreproducibility sources — into the
record for zero benefit. A literal ordered list touches `os.listdir` never.

**What happens to the prose that names those files today: nothing. It stays, verbatim.**

Deleting it is tempting and wrong. The imperative carries things a path list cannot express — *where
the repo carries no `docs/agents/` overlay, substitute the closest repo doctrine and record the
substitution*; *a missing engine-config is a sanctioned degradation, do NOT create the overlay*;
*note any lesson this run's evidence contradicts*. Stripping the paths out of that prose would
either take the surrounding instructions with them or leave dangling references. It is a behaviour
change to every Commander run, with unbounded blast radius, for zero benefit today.

The cost — two sources of truth that can drift — is real, and I pay it with **one test, not one
field**: assert that every `repo:`/`skill:` path declared on a step appears verbatim in that step's
`imperative`. It catches drift in the direction that matters (declaration silently narrowed) and
cannot catch the other (prose names a file the declaration omits). The declaration is authoritative;
the prose is the human explanation of it.

---

## 5. Producer / consumer API

**Producer — one function, in `scripts/checklist_engine.py`, immediately after `state()`:**

```python
_MANIFEST_CONTRACT_VERSION = 1

def context_manifest(cl: dict, roots: dict[str, Path]) -> dict:
    """The active step's declared context, resolved and revision-stamped.

    Pure given (cl, roots, filesystem). Selection is `active_id(cl)` — the SAME
    selector `state()` uses; this adds no second assembly path (extend-dont-parallel).
    Reads file BYTES only: no git subprocess, no network, no inference. INV-2 is not
    violated because this is not `state()` — but it borrows the discipline: it never
    runs a condition check and never mutates.
    """
```

`roots` is `{"skill": Path, "repo": Path, "work": Path}`, supplied by the caller. It is **not**
recorded in the manifest — absolute paths are environment-varying and would be the first entry in an
otherwise-empty exclusion set. Making roots an explicit argument (rather than discovered) is also
what makes the whole thing testable: point them at a fixture tree.

**CLI — one new read-only verb:**

```
py scripts/checklist_engine.py --file .agent-work/300/spine.json context
```

Prints the manifest JSON to stdout, exit 0. Read-only, so it joins `current` in the two
`args.verb != "current"` write guards at `checklist_engine.py:2508` and `:2523` — which become a
`READ_ONLY_VERBS` set. Not in `MUTATING_VERBS`, so it never journals.

**Consumer:** `json.loads(...)`. That is the whole consumer API. `#301` embeds the object; `#307`
re-runs the verb and compares; a human runs the verb.

**The verb does not concatenate the files' bytes.** This is my sharpest YAGNI call and I want it
argued, not buried. What breaks today if there is no concatenated blob? Nothing. #301 wants the
manifest; #307 wants the manifest; the agent reads the listed files itself, exactly as it does
today — and a 40 KB doctrine blob piped through stdout is a context-cost *regression* against the
agent's own file reads. It also gives the cleanest possible stochastic-boundary story: between canon
and the active surface there is **zero** transformation, only resolution and identification.

The cost: acceptance criterion 1 ("produced on every deterministic assembly") is satisfied
*definitionally* — the manifest **is** the output of the assembly, there is no other assembly — not
by a structural interlock that makes bypassing impossible. An agent can still open files by hand
without invoking the verb, exactly as it can today. I do not claim otherwise. If the panel wants the
interlock, `--emit` is `"".join(read(p) for p in files)` over the same return value and needs **no
manifest change** — which is itself evidence the seam is in the right place.

---

## 6. The exclusion set

**Empty.** Zero fields legitimately vary. The determinism test is:

```
assert manifest_bytes_env_A == manifest_bytes_env_B
```

No filtering, no field masking, no "compare everything except…". This is the single biggest payoff
of the minimal stance, and it is a direct answer to fixed-constraint 6: the smallest, most explicit,
most structurally-separable exclusion set is the one with no members.

The three named irreproducibility sources, each closed by construction:

| Source | Closed by |
|---|---|
| **Line endings** | `rev` LF-normalises before hashing (verified §1: matches git's own oid under `core.autocrlf=true`); the serializer writes `newline="\n"` |
| **Filesystem ordering** | never enumerated. `files` order == declaration order == a committed JSON literal. No glob, no `listdir`, no `sorted()` |
| **Locale** | no `sorted()` on strings, no `strftime`, no locale-sensitive number or case formatting; encoding pinned UTF-8, `ensure_ascii=False` |

Also excluded, each because it would create the exclusion set I am refusing to have: timestamps,
run/session id, `work_id`, hostname, OS, user, absolute paths, elapsed time, file mtime, file size.
**Time and run identity belong to the episode record (#301), which already owns them.** Putting a
timestamp here would mean every drift check needed a masking rule — and a masking rule is a place
where a real difference can hide.

---

## 7. Self-scoring

**Depth — 3/5.** It hides the genuinely fiddly parts behind one call: CRLF normalisation, the
tracked/untracked/out-of-repo trichotomy collapsed to one code path, absence-as-`null`, traversal
refusal. A consumer never learns that Windows exists. But it **leaks `roots` upward**: every caller
must know the three roots and get them right, and a caller that passes a wrong `repo` root gets a
plausible, deterministic, wrong manifest. That leak is deliberate (it is what makes the function
pure and fixture-testable) but it is a leak, and I score it as one.

**Locality — 4.5/5.** One optional Task key (`docs/CHECKLIST_SCHEMA.md` + the templates I annotate),
one function and one verb in `checklist_engine.py`, one paragraph in
`docs/CHECKLIST_ENGINE_DESIGN.md`, tests. No new script, no new file format, no new directory, no
new dependency. Spines without a `context` key are unaffected, so rollout is per-template.

**Seam placement — 3.5/5.** Right for the two machine consumers: #301 embeds the dict verbatim,
#307 diffs the bytes. **Wrong for the third named consumer, the human reading a git diff.** A diff
of manifests is a diff of hex strings; it tells a reviewer *that* doctrine changed, never *what*
changed. I have no rendering adapter and no plan for one.

**Testability — 3.5/5.** The producer is excellent: pure given `roots`, so a fixture tree drives
every branch with no git, no network, no spine mutation. The **declaration** is the weak half —
nothing structurally prevents a `context` list that is deterministically, reproducibly *wrong* about
what the step needs. The §4 test narrows this; it does not close it.

**The adversarial fixtures.** A round-trip over the shipped corpus proves the corpus is clean, not
that the tool is right. These five fixtures make the tool return a *wrong* answer if it is broken:

1. **CRLF twin (the essential one).** Two fixture trees, byte-identical except one is CRLF and one
   LF. Manifests must be **byte-identical**. A tool that hashes raw bytes passes the entire real
   corpus (single checkout, one line-ending convention) and fails here. This is the exact Windows
   bug that no round-trip can surface.
2. **Basename shadow — the silent PASS.** `repo:docs/agents/GLOSSARY.md` absent, but
   `skill:references/GLOSSARY.md` present with different content. Expect `rev: null`. A resolver
   that falls back across roots returns a *valid-looking 40-hex oid for the wrong file* — the most
   dangerous failure this design can have, and invisible without this fixture.
3. **Absent-by-design — the false FAIL.** All of `repo:docs/agents/*` missing (the real state of
   this repo). Expect three `rev: null` entries and exit 0. A tool that treats absence as an error
   fails a valid corpus.
4. **Anti-sort.** Declare `["repo:z.md", "repo:a.md"]`. Expect that order. Catches any accidental
   `sorted()` or glob — including one introduced later by a well-meaning cleanup.
5. **Identical twins.** Two different declared paths with identical content, plus the same path
   declared twice. Expect the same `rev` twice and both entries present. Catches path-keyed
   memoisation and silent dedup.

**Foreclosure risk — 4/5 (low).** Each entry is already assertion-shaped: subject = the path,
predicate = "was delivered at revision R", source = this manifest, evidence = the oid. Crucially I
carry **no strength field and no prose** — strength is a judgement, and a judgement inside a record
that must be a pure function of (canon, selector state) would violate B0.1 outright. So Stratum A can
be built *over* these entries without first having to reconcile a second opinion. The one real
foreclosure seam: entries have **no stable id**, so a later assertion pointing at "the third entry"
is positional and fragile. Mitigation available without a contract break, since duplicate paths are a
spine bug: address an entry by `(manifest content hash, path)`.

---

## 8. What my constraint made me give up

Honestly, and in descending order of how much it hurts:

1. **No human rendering. This is the worst of it.** One of the three real consumers is a person
   reading a git diff to review what agents will see, and I hand them hex. The ports arm would keep
   a rendering adapter; I deleted it because nothing *breaks* today without it — but "nothing
   breaks" and "nobody is served" are not the same sentence, and here they diverge.
2. **No separation of in-memory shape from on-disk encoding.** The dict *is* the JSON. If a second
   encoding is ever needed, every consumer that touches the dict is exposed. I traded a real seam
   for four keys.
3. **No repo commit SHA.** Per-file oids are strictly more accurate, but they cost you the one-token
   "which world was this assembled in" handle. Anyone asking that question must go to the episode
   record or resolve oids by hand.
4. **No file is written anywhere.** #307's drift check needs a committed artifact to diff against;
   my design produces no artifact and no location convention, so #307 must own persistence entirely.
   That is a real hand-off of work, not a saving.
5. **No structural interlock on AC1** (§5). Definitional satisfaction, not enforced.
6. **The prose duplication persists** (§4). Two places name the same files; one test guards one
   direction.
7. **No per-entry role, reason, or `optional` flag.** Why `GLOSSARY.md` is in the list, and whether
   its absence is sanctioned or a gap, lives only in the imperative prose — unreadable to a machine.

I stand behind 1–7 as correct *under my constraint*, and I would not pretend 1 and 4 are small.

---

## 9. Obligations I offer #301, and cross-interface risk

**What #301 can rely on, unconditionally, in contract 1:**

- The context field value is a **JSON object** with exactly the keys `contract` (int),
  `step` (str), `files` (list). No key is ever absent; no key is ever added within contract 1.
  Adding one bumps `contract`.
- Each `files[]` element has exactly `path` (str, `scheme:posix/path`, scheme ∈ {`skill`, `repo`,
  `work`}) and `rev` (40-lowercase-hex str, **or `null`** for declared-but-absent). `files` may be
  empty; it is never absent, never `null`.
- **It carries no time, no run id, no session id, no hostname, no absolute path.** #301 owns run
  identity and time completely and will never have to strip anything from my object before storing.
- **Byte-stability**: identical canon ⇒ byte-identical serialisation. #301 may content-address,
  deduplicate, or cache manifests safely.
- **Self-describing**: `step` makes a *list* of manifests unambiguous. If an episode spans several
  assembled steps, the context field may hold either one object or a list of them; I impose neither.
- **Addressing**: the manifest carries **no id of its own**. To point at one by reference, address it
  by `sha256` of its canonical serialisation (UTF-8, LF, `indent=2`, key order as emitted). I will
  publish the serializer so both sides compute identical bytes. I do not store that hash inside the
  object — a record cannot contain its own hash.

**Cross-interface risks, flagged rather than designed around:**

- **R1 (by-value vs by-reference) — the live one.** I write no file. If #301's durable store wants
  the context field to be a *reference* (path or id) rather than an embedded value, my design must
  grow a `--out` flag and a location convention. That is a genuine change on my side; it is the one
  place #301's decision can force mine. **Float to the Admiral if #301 lands on by-reference.**
- **R2 (who owns time).** If #301 expects each context object to be self-dating, we have a direct
  conflict: I refuse a timestamp because it would create the exclusion set §6 exists to avoid. My
  position is that the episode carries the time. This needs an explicit ruling if #301 disagrees.
- **R3 (cardinality).** If #301 assumes one context per episode, and a Commander run assembles per
  *step*, the field must accept a list. Cheap to fix on #301's side now, expensive later.
- **R4 (contract coupling).** #301 storing `contract: 1` records durably means my version bump
  becomes their migration. This is the intended cost of `contract` existing — but they should know
  they are on the hook for reading it, not ignoring it.

None of R1–R4 is designed around silently, and I have edited nothing outside this file.
