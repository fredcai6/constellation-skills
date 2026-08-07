# x10 candidate 2 — storage design under **rename-survival-first**

*Design document. Nothing built, nothing run. One constraint taken seriously and
every other property spent on it, with the bill itemised in §8.*

---

## Headline — the one idea, and the three moves it forces

**Nothing that changes when code is refactored may appear in a store path, a
store filename, or a statement's identity.** Refactoring changes exactly four
things — the file's path, the symbol's name, the line numbers, and the docstring
wording — so all four are demoted to *properties*, recorded in one place each,
and every one of them is removed from every identity.

Three consequences follow, and they are the whole design:

1. **Store paths are derived from opaque serials, never from source paths.**
   `nodes/3b/51/n3b5136d824/` holds `Config.load_config`'s bundle and will still
   hold it after the file moves twice and the method is renamed three times.
   Mirroring the source tree (`store/src/utils/config.py/…`) was rejected on the
   first constraint: a file move would rename thousands of store paths.
2. **Serials are deterministic hashes of the entity's *birth* name, minted once
   and frozen.** No counter file, no mint-time coordination, no merge conflicts
   between branches, and — crucially — no dependence on content, so an edit
   never re-mints.
3. **The one record that maps serial → current name/path is decomposed so that a
   refactor touches exactly one row per refactored thing.** Names are stored
   *relative to the parent*, so a file move rewrites one line, not one line per
   descendant.

The measured payoff, walked in §4: the brief's rename scenario — a file move
**and** a method rename in the same commit — produces a **12-line store diff, of
which zero lines are statements**. Nothing re-mints and no human ruling is
needed.

The bill, itemised in §8: a `facts.jsonl` in this store is unreadable without
the ledger, derived statements carry no `file:line`, and a 50/50 function split
is the one place identity honestly breaks.

---

## 1. On-disk layout, concretely

### 1.1 The tree

```
docs/map/
  index/
    ledger/00.tsv … ff.tsv        identity: serial → current name, parent, state
    names.tsv                     derived: current+historic qualname → serial
    aliases.tsv                   merged/superseded serial → live serial
    rulings.jsonl                 append-only human decisions (cascade rung -1)
    RUN.json                      last crawled commit, counts, crawler version
    RUN.md                        human changelog for the run (what a PR reviewer reads)
    PENDING.md                    identity questions the crawler could not settle
  nodes/
    3b/51/n3b5136d824/            Config.load_config's bundle
      facts.jsonl                 derived structural statements — serial↔serial only
      prose.md                    purpose prose (derived from docstring; human-editable)
      tags.jsonl                  tag-minted node stubs + their write-back origins
    f2/c1/nf2c1bd3616/            Config's bundle
    13/42/n134239b8d6/            src.utils.config's bundle
    88/7b/n887b59481b/            the Assumption: node minted inside load_config
  views/                          rendered articles (committed, `-diff` in .gitattributes)
.map-cache/                       GITIGNORED: positions, inverse index, sqlite
```

**Sharding.** `nodes/<hex[0:2]>/<hex[2:4]>/<serial>/`. Serials are hashes, so the
spread is uniform and permanent — unlike a monotonic counter, which would pile
every new entity into the last shard. Same scheme for the ledger:
`index/ledger/<hex[0:2]>.tsv`, 256 shards. On f1Brainz (~21k entities) that is
~80 rows per shard; at the brief's 10× target (~210k entities) it is ~800 rows
per shard, ~60 KB each. A refactor rewrites a handful of rows in a handful of
shards.

**Bundle owners.** Only *declaration-owning* entities get a directory: package,
module, class, function/method. Parameters, class attributes, module state and
locals get serials (they must — statements point at them) but no directory;
their statements live in the bundle of the declaration that **encloses the source
span**. So bundle membership is by **anchor, not by subject** — a `param-of`
statement whose subject is the parameter still files under the function. This is
why the median bundle is cohesive rather than one line long: x7b's slice has 429
distinct statement *subjects* but only ~120 declarations, and f1Brainz repo-wide
has ~4,700 declarations against 16,767 named containers.

**Empty files are not materialised.** Most bundles are `facts.jsonl` only;
`prose.md` appears for the 72% of classes and public functions x1 measured as
carrying a docstring; `tags.jsonl` appears for the few hundred tagged entities.

### 1.2 Where directory-per-subject / file-per-layer lands

The parent's lean is kept in shape and rejected in addressing.

- **Kept: directory per subject.** One directory per declaration, three files
  inside it split by layer — derived structure (`facts.jsonl`), prose
  (`prose.md`), author-minted concept nodes (`tags.jsonl`). That is the
  file-per-layer split, honouring the substrate verdict that statements are
  JSON-lines and prose is markdown, and it keeps a rewrite of the derived layer
  from ever touching the file a human edits.
- **Deviated: the directory is named by serial, not by subject name.** Naming it
  `nodes/src.utils.config/Config/load_config/` would make the layout beautiful
  and would re-mint the world on the brief's own scenario. Under this
  constraint that is not a trade, it is the failure mode.
- **Deviated: no fourth "positions" file.** See §1.4.

### 1.3 The `Config.load_config` bundle — actual contents

Serials below are real, computed as
`"n" + sha1("f1brainz\0<kind>\0<birth-qualname>").hexdigest()[:10]`, so every
example path in this document is internally consistent and reproducible.

| serial | kind | birth qualname |
|---|---|---|
| `n134239b8d6` | module | `src.utils.config` |
| `nf2c1bd3616` | class | `src.utils.config:Config` |
| `n3b5136d824` | function | `src.utils.config:Config.load_config` |
| `n3b235e9f7f` / `n828241d062` | param | `…load_config.cls` / `.config_file` |
| `n1dec543f1b` `n594f75f2fb` `n477af278df` | container | `Config.CONFIG_DIR`, `._config_data`, `._config_source` |
| `nfe6c53c9d2` `nd8804ba2be` `n7cb9325e3d` `n15797d173b` | local | `config_path`, `config_source`, `e`, `f` |
| `n28b0e92e14` `n065e502635` `nb517c51b44` | function | `Config._validate_config`, `._setup_fastf1_cache`, `._setup_logging` |
| `nb66db646a8` `n436c2626b6` `n7e543d4955` `n425dc8a526` `nc9b584a420` `n62593c7b9e` | external | `pathlib:Path`, `builtins:open`, `builtins:str`, `yaml:`, `yaml:safe_load`, `yaml:YAMLError` |
| `nc828d25214` | class | `src.models.exceptions:ConfigurationError` |
| `n887b59481b` | tag | the `Assumption:` minted in this docstring |

**`docs/map/nodes/3b/51/n3b5136d824/facts.jsonl`** — the full derived set for
`Config.load_config`, aggregated from x7b's real output for this function
(28 occurrence rows collapse to 26 fact lines; `documents` is not a fact line,
see below):

```jsonl
{"s":"n3b235e9f7f","p":"param-of","o":"n3b5136d824"}
{"s":"n828241d062","p":"param-of","o":"n3b5136d824"}
{"p":"calls","o":"n065e502635"}
{"p":"calls","o":"n28b0e92e14"}
{"p":"calls","o":"n436c2626b6"}
{"p":"calls","o":"n7e543d4955","n":4}
{"p":"calls","o":"nb517c51b44"}
{"p":"calls","o":"nb66db646a8"}
{"p":"calls","o":"nc828d25214","n":3}
{"p":"calls","o":"nc9b584a420"}
{"p":"calls","o":"?","n":2,"why":"dispatch-unknown-base"}
{"p":"reads","o":"n15797d173b"}
{"p":"reads","o":"n1dec543f1b"}
{"p":"reads","o":"n3b235e9f7f","n":14}
{"p":"reads","o":"n425dc8a526","n":2}
{"p":"reads","o":"n477af278df","n":2}
{"p":"reads","o":"n594f75f2fb","n":6}
{"p":"reads","o":"n62593c7b9e"}
{"p":"reads","o":"n7cb9325e3d","n":2}
{"p":"reads","o":"n828241d062","n":5}
{"p":"reads","o":"nd8804ba2be","n":3}
{"p":"reads","o":"nfe6c53c9d2","n":6}
{"p":"writes","o":"n15797d173b"}
{"p":"writes","o":"n477af278df"}
{"p":"writes","o":"n594f75f2fb"}
{"p":"writes","o":"nd8804ba2be"}
{"p":"writes","o":"nfe6c53c9d2","n":2}
```

Four rules are visible in that file and each is a consequence of the constraint:

- **`s` is omitted when the subject is the bundle owner.** Two thirds of lines
  lose a field, and the owner's serial appears in the path rather than 27 times
  in the body — so a bundle is never rewritten because of something about its
  own identity.
- **Occurrence counts, not occurrence positions.** `"n":14` replaces fourteen
  `{"line":…,"col":…}` rows. This preserves x4's validated hole-ranking signal
  (distinct-caller and total-call counts) at a cost of one integer, and it is the
  single largest source of churn removed. `"n"` is omitted when it is 1.
- **Sorted canonically by `(s ?? "", p, o)`.** Deterministic output is what makes
  a re-derive diff mean something; §5 depends on it.
- **`documents` is not a fact line.** x7b emits 81 `documents` statements whose
  object is a prose string. Prose belongs in `prose.md`; the existence of that
  file *is* the `documents` statement. This keeps the largest, most reword-prone
  strings out of the JSONL entirely.

**`docs/map/nodes/3b/51/n3b5136d824/prose.md`:**

```markdown
<!-- map: n3b5136d824 · src.utils.config:Config.load_config · crawl 2026-08-06 a91f3c2 -->

Load and validate configuration from YAML file. Resolves a bare filename against
`Config.CONFIG_DIR`, caches the parsed document on the class, and re-reads only
when the requested source differs from the cached one.

## Parameters
- `[n828241d062]` **config_file** — Name of config file in configs/ directory

## Returns
Validated configuration dictionary.

## Raises
- `[nc828d25214]` **ConfigurationError** — If config file missing or invalid
```

The HTML comment on line 1 is the **one deliberate legibility concession**: it
is derived, the crawler owns it, and it churns one line per renamed entity —
never one line per *reference to* a renamed entity, which is the churn that
matters. Everything else in the file is name-free at the identity level; the
bracketed serials are the write-back pointers org-babel's law requires (x2 §3.2),
and the human-readable names beside them are prose, not identity.

**`docs/map/nodes/3b/51/n3b5136d824/tags.jsonl`** — the stub the anchor keeps,
given this `Assumption:` added to the docstring:

```
Assumption: The configs/ directory is the only search root for a bare filename.
            An absolute path bypasses it entirely; if a caller passes a relative
            path expecting cwd-resolution, it silently resolves under CONFIG_DIR.
```

```jsonl
{"o":"n887b59481b","p":"constrained-by","tag":"Assumption","ord":1,"origin":{"owner":"n3b5136d824","line_hint":52}}
```

and the minted node's own bundle,
**`docs/map/nodes/88/7b/n887b59481b/prose.md`:**

```markdown
<!-- map: n887b59481b · assumption · minted in n3b5136d824 · crawl 2026-08-06 a91f3c2 -->

The configs/ directory is the only search root for a bare filename. An absolute
path bypasses it entirely; if a caller passes a relative path expecting
cwd-resolution, it silently resolves under CONFIG_DIR.
```

with one ledger row (§2.2) giving it `kind: assumption`, a slugged
`name: configs_dir_only_search_root`, and `confidence: medium` per x9 §3 (no
author-supplied `[stable-id]`). The edge `struct --constrained-by--> assumption`
falls out of the target's kind exactly as x9's six-row lookup specifies; no edge
vocabulary is stored.

### 1.4 What is *not* on disk, and why

**Positions are gitignored.** `file:line:col` for every derived occurrence is
44,554 rows for 67 files (x7b), ~300k repo-wide, ~3M at the brief's 10× target —
and every one of them moves when a line is inserted at the top of a file. Under
this constraint that tier is pure poison: it is the largest thing in the store,
it churns on edits that change nothing semantically, and it re-mints on every
move. It lives in `.map-cache/positions/`, keyed by module serial with the path
in a header line, rebuilt by the crawler in the same pass that writes the store.

The asymmetry is deliberate and principled: **positions are dropped exactly
where they would be churn (millions of derived facts) and kept exactly where they
are load-bearing (hundreds of author-attached tag origins, which need the
pointer for write-back).** Even there the durable half of the pointer is the
owner serial and the line is called `line_hint`, refreshed each crawl.

**Fingerprints are not stored either.** The rename cascade needs the *previous*
run's body/signature/doc hashes to match against. Rather than commit a volatile
fingerprint tier, the crawler parses **two trees** — the base commit recorded in
`RUN.json` and HEAD — and computes both sides on the fly. At x7b's measured
2.3 s per 67 files a second parse is free, and it removes an entire committed
tier whose only job was to churn.

---

## 2. Identity scheme

### 2.1 The serial

```
serial  =  "n" + sha1( project_salt || 0x00 || kind || 0x00 || birth_qualname )[:10 hex]
```

- **Opaque.** Ten hex characters. It encodes nothing a refactor can change.
- **Content-free.** Deliberately *not* a content hash. A content hash re-mints on
  every edit, which is the exact opposite of the requirement. The per-node
  content hash the substrate verdict calls for still exists — it is the
  supersession trigger, carried on the *fact set*, not on the identity.
- **Birth-derived, then frozen.** `birth_qualname` is the fully-qualified name
  the entity had **when first seen**, and it is never recomputed. `load_config`
  renamed to `load` keeps `n3b5136d824` forever; the string
  `src.utils.config:Config.load_config` survives only inside a hash preimage
  nobody consults again.
- **Deterministic across clones and branches.** Two branches that independently
  add the same new function mint the *same* serial, so a merge produces one
  ledger row rather than a conflict. This is why the scheme beats a monotonic
  counter: a counter is shared mutable state at mint time and would conflict on
  every parallel branch.
- **Project-scoped for cross-project reach.** Fully qualified as
  `f1b:n3b5136d824`; the bare form is used inside a project's own store. The
  salt is the project id, so two projects never collide even on identical
  qualnames — satisfying the substrate's "per-project graphs, cross-project reach
  by declared location".
- **Collision on resurrection, handled.** If a qualname's serial is already taken
  by an `absent` entity whose body similarity to the newcomer is below 0.40, the
  newcomer mints `n3b5136d824~2`. Deterministic, still merge-safe, and rare.

**Who assigns.** The crawler, and only the crawler, during the identity-resolution
phase of a run — after extraction, before any file is written. No human ever
types a serial into source. No hand edit ever creates one.

**When.** At the single moment an extracted declaration reaches rung 5 of the
cascade (§3) without matching anything.

### 2.2 The ledger — decomposed so a refactor touches one row

`index/ledger/3b.tsv` (tab-separated, sorted by serial):

```tsv
serial	kind	name	parent	path	state	born	changed	was
n3b235e9f7f	param	cls	n3b5136d824		live	7f21a04	7f21a04
n3b5136d824	function	load_config	nf2c1bd3616		live	7f21a04	7f21a04
```

`index/ledger/13.tsv`:

```tsv
serial	kind	name	parent	path	state	born	changed	was
n134239b8d6	module	src.utils.config	n5408b83ce0	src/utils/config.py	live	7f21a04	7f21a04
```

The load-bearing detail: **`name` is relative to `parent`, and `path` is
populated only on module and package rows.** The full qualname is reconstructed
by walking the parent chain. Therefore:

- a **file move** rewrites the module row's `path` and `name` — **one line**,
  regardless of how many entities the file declares;
- a **symbol rename** rewrites that symbol's row — **one line**, regardless of
  how many entities reference it;
- a **package re-root** rewrites the package row — one line.

The obvious alternative (store the full qualname on every row) would turn the
brief's file move into ~50 ledger lines for `config.py` alone and ~16,000 for a
top-level package rename. Relative naming is what makes the ledger's diff
proportional to the *refactor*, not to the *subtree*.

`was` accumulates superseded names, `;`-joined, capped at five with older ones
retired to `aliases.tsv`. It exists so that human-written `See: Config.load_config`
still resolves after the rename, with a soft warning rather than an error.

`state` is `live`, `absent` (declaration gone; retained for re-match and for
tombstone anchoring), or `merged:<serial>`.

### 2.3 Stability guarantees, stated honestly

| Event | Serial survives? | Mechanism | Human ruling? |
|---|---|---|---|
| File move / rename | **Yes, always** | git rename detection → qualname rewrite (rung 2) | No |
| File move git scores below its rename threshold | Usually | falls to rung 3/4 on body similarity | Only in the gray band |
| Symbol rename, body unchanged | **Yes, always** | rung 3 scores 1.00 | No |
| Symbol rename + partial rewrite | Yes down to ~35% body retention | rung 3 graded similarity | Gray band below that |
| Method moved to another class | Usually | rung 4, threshold 0.85 | Gray band 0.55–0.85 |
| Docstring reworded | **Yes, always** | text is not in any identity | No |
| Lines inserted above | **Yes, always** | positions are not stored | No |
| Signature change (param added) | Yes for the function; the new param mints | rung 1 on the function | No |
| Function split, one clear survivor | Yes for the survivor | rung 3 highest score wins | No |
| Function split, two comparable residues | **No — both re-mint** | the honest failure (§3.4) | **Yes** |
| Function merge | Yes for the winner; loser aliases | §3.4 | Only on a tie |
| Delete, then re-add same name later | Yes (or `~2` if bodies differ) | absence window + resurrection rule | No |
| Base commit unreachable (shallow clone, rewritten history) | **No — renames re-mint** | rung 1 only; documented fallback | Yes, en masse |
| Ledger lost or corrupted | **No — everything re-mints** | git history is the only protection | n/a |

The last two rows are not hedges; they are the design's two catastrophic modes
and they are in §8.

---

## 3. The assignment mechanism — an ordered cascade

Inputs to a crawl: `base` (last-crawled commit, from `RUN.json`), `HEAD`, the
ledger, `rulings.jsonl`, and two parses (base tree, HEAD tree). Output: a serial
for every declaration in HEAD, plus state transitions for everything in the
ledger that HEAD does not contain.

### 3.1 The rungs

**Rung -1 — a standing human ruling.** `rulings.jsonl` is consulted first and
its verdicts are permanent. Format:

```jsonl
{"run":"2026-08-06T14:02Z","by":"tommy","q":"n3b5136d824","decision":"continues-as","parent":"nf2c1bd3616","name":"load"}
{"run":"2026-08-06T14:02Z","by":"tommy","q":"n0177ad3e91","decision":"distinct-from","other":"n91b2c4d5e6"}
```

A ruling is cheap to write and never expires. This is the escape hatch for
everything the cascade gets wrong.

**Rung 0 — an author-supplied anchor.** A docstring line `Id: n3b5136d824`
pins the entity. Available but *not* the primary mechanism: it is written back
into source by the crawler only when the cascade has previously failed for that
entity and a human ruled on it, so the ruling becomes self-enforcing without
anyone hand-authoring identifiers.

**Rung 1 — exact structural match.** Same `kind`, same `parent` serial, same
`name`. Hash lookup, O(n). This resolves essentially everything in a normal
commit and costs nothing.

**Rung 2 — path-rename rewrite (this is the move mechanism).**
`git diff -M --find-renames=40% --name-status base..HEAD` yields a path-rename
map. For every module whose new path is the target of a rename, the module
matches its old serial directly, and — because names are stored relative to the
parent — **every descendant then resolves on rung 1 unchanged.** A pure file
move therefore costs one lookup and re-mints nothing.

Git's own rename detection is used here deliberately, in preference to
content-hashing files ourselves: it is already computed, already tuned, already
what the reviewer sees in the PR, and it is the only signal that survives a file
being moved *and* rewritten in one commit. Its heuristic nature is a dependency
and appears in §8.

**Rung 3 — sibling rename, graded.** For each still-unmatched new declaration,
the candidate pool is the unmatched `live`/`absent` ledger entities with the
**same parent serial and same kind**. Score:

| Component | Weight | Definition |
|---|---|---|
| body similarity | 0.60 | `difflib.SequenceMatcher` ratio over the normalised AST token stream — literals folded, the entity's own name erased, callee names kept |
| signature shape | 0.15 | 1.0 if arity, parameter names, defaults and decorators all match; 0.5 if parameter names match but defaults differ; else 0 |
| doc first line | 0.10 | exact match of the docstring's first sentence |
| sibling ordinal | 0.05 | 1.0 if the index among siblings is equal, 0.5 if ±1 |
| fact-set Jaccard | 0.10 | Jaccard of `{(p,o)}` from the base parse against HEAD |

Greedy best-first assignment, each old entity consumed once. **≥ 0.70 → automatic
match. 0.40–0.70 → PENDING. < 0.40 → no match.**

A pure rename scores **1.00**. A rename with 60% of the body retained scores
0.36 + 0.15 + 0.10 + 0.05 + 0.06 ≈ 0.72 — still automatic. That is the case that
matters, because renaming and reworking in one commit is the normal human
behaviour.

**Rung 3b — unique residual pairing.** If, under one parent, exactly one old and
one new declaration of the same kind remain unmatched, propose the pair at a
lowered bar: automatic at ≥ 0.40, PENDING below. This catches "renamed *and*
substantially rewritten", where every similarity signal is weak but the
structural situation is unambiguous.

**Rung 4 — cross-parent move.** Pool widens to all unmatched entities of the same
kind repo-wide (a method moved to a different class, a helper moved to a
different module without a file rename). Same scoring, **threshold raised to
0.85**, gray band 0.55–0.85 → PENDING. The bar is higher because a false
positive here is the worst outcome this design can produce: it fuses two
unrelated entities' histories and silently re-parents a human's prose.

**Rung 5 — mint.** §2.1.

**Symmetric closing pass.** Every ledger entity HEAD did not match goes
`state: absent`, `changed: <sha>`, and stays eligible for rungs 3/4 for a window
of 50 crawls or 90 days, whichever is longer. After the window it moves to
`index/ledger-retired.tsv`, still resolvable, no longer a match candidate.

Absent-but-retained entities are a free win the board is already looking for:
open thread 3 asks where a deleted-anchor tombstone lives, and x9 §5(a) refuses
to place it on a nearby surviving file because that makes the anchor arbitrary.
Here it is not arbitrary. The P1b braking kernel's serial still exists with
`state: absent`, so a `Rejected:` claim anchored to it still resolves, and a
plan query touching the concept still surfaces it. **This design does not solve
the tombstone problem, but it removes the specific obstruction x9 named**, and
that is worth recording even though it is outside the brief.

### 3.2 What is automatic and what a human rules on

**Automatic, no human:** rungs -1, 0, 1, 2; rung 3 ≥ 0.70; rung 3b ≥ 0.40;
rung 4 ≥ 0.85; all minting; all absence marking; merge-winner selection when the
scores differ by more than 0.15.

**Requires a ruling, written to `PENDING.md`:**

1. Any score in a gray band (3: 0.40–0.70; 3b: < 0.40 with a unique residual;
   4: 0.55–0.85).
2. A split whose two best residues score within 0.15 of each other.
3. A merge whose two claimants score within 0.15 of each other.
4. **Any proposed match that crosses `kind`** — function↔class, container↔function.
   Never automatic at any score.
5. Retiring an absent entity before its window expires.
6. Flattening an alias chain.

`PENDING.md` is written for a human to answer in one line each:

```markdown
## Identity questions from crawl a91f3c2 (base 7f21a04)

- [ ] **n0177ad3e91** `src.physics.brake:_solve_knee` (absent) vs new
      `src.physics.brake:solve_brake_knee` — score **0.58** (body 0.71, sig 0,
      doc 0, ordinal 1.0, facts 0.44). Same? → `continues-as` / `distinct-from`
```

This lands on an existing step rather than adding one: the T2 verdict already
says the Cartographer workflow becomes *tool run + hole adjudication + cleanup*.
Identity rulings ride the hole-adjudication step. Expected volume is the reason
this is affordable — a repo that renames aggressively produces a handful of gray-band
questions per crawl, not a queue.

### 3.3 Split

One declaration becomes two. The cascade scores both new declarations against
the original.

- **Clear survivor** (best − second ≥ 0.15): the winner takes the original
  serial. The other mints, and its ledger row records `from: n3b5136d824 (split)`.
  Nothing existing is rewritten; every inbound reference still points at the
  survivor, which is correct because the survivor is what the callers still call.
  Fully automatic.
- **Comparable residues** (within 0.15): **both mint, the original goes
  `absent`, and a ruling is filed.** This is a genuine re-mint and it is the one
  place this design fails at its own job. The mitigation is not technical — it is
  that the human answers one line in `PENDING.md` and the next crawl applies it
  retroactively, moving the original serial onto the chosen residue and rewriting
  the two ledger rows. The prose that was attached to the original is *not* lost
  in the interim: it stays in `nodes/3b/51/n3b5136d824/prose.md`, attached to an
  absent entity, and the ruling reattaches it.

### 3.4 Merge

Two declarations become one. Both old entities match the same new declaration.

- The higher scorer **keeps its serial and continues**. The loser gets
  `state: merged:<winner>` and a row in `aliases.tsv`.
- **Facts referencing the loser are not rewritten.** They do not need to be: the
  T2 verdict rebuilds facts wholesale each run, so the next crawl derives them
  against the winner naturally. Rewriting them at merge time would be exactly the
  "re-mint the world" behaviour this design exists to avoid.
- The alias therefore exists for one purpose only: **keeping author-written
  attachments valid.** A `See:` in someone's docstring, a `tags.jsonl` origin, a
  hand-edited `prose.md`, a decision file's cross-reference — all of these point
  at the loser and must keep resolving. The loser's bundle directory is merged
  into the winner's (facts dropped, prose appended under a
  `<!-- merged from n… -->` marker, tags moved) and its directory removed.
- Ties within 0.15 → ruling.

Alias chains are never garbage-collected automatically. §8 owns that.

---

## 4. The rename scenario, walked

**The change.** `src/utils/config.py` → `src/utils/configuration.py`, and
`Config.load_config` → `Config.load`, in one commit `a91f3c2`. Nothing else
edited.

### 4.1 What the crawler does

1. Reads `RUN.json`: base = `7f21a04`.
2. `git diff -M --find-renames=40% --name-status 7f21a04..a91f3c2` →
   `R097  src/utils/config.py  src/utils/configuration.py`.
   Path-rename map: `{configuration.py: config.py}`.
3. Parses both trees. Base parse yields the old declaration set with
   fingerprints; HEAD parse yields the new one.
4. Cascade, entity by entity:

| Entity in HEAD | Rung | Result |
|---|---|---|
| module `src.utils.configuration` | 1 miss → **2** | path-rename map says it was `config.py`; module row `n134239b8d6` matches. **Survives.** |
| class `Config` | **1** | parent = `n134239b8d6` (just matched), name `Config` → `nf2c1bd3616`. **Survives.** |
| `Config.load` | 1 miss → **3** | pool = unmatched children of `nf2c1bd3616`, kind function → `load_config` (`n3b5136d824`). Body identical → 0.60; signature `(cls, config_file="default.yaml")` identical → 0.15; doc first line identical → 0.10; same ordinal → 0.05; fact-set Jaccard 1.0 → 0.10. **Score 1.00 → automatic.** |
| params `cls`, `config_file` | **1** | parent `n3b5136d824` matched, names unchanged. **Survive.** |
| containers `CONFIG_DIR`, `_config_data`, `_config_source`, … | **1** | parent `nf2c1bd3616` matched. **Survive.** |
| every other function in the file | **1** | **Survive.** |
| callers elsewhere in the repo | untouched | their files did not change; their facts are re-derived to the same serials |

**Nothing reaches rung 4 or 5. Nothing re-mints. `PENDING.md` is empty.**

### 4.2 The diff a reviewer sees

```diff
--- a/docs/map/index/ledger/13.tsv
+++ b/docs/map/index/ledger/13.tsv
@@
-n134239b8d6	module	src.utils.config	n5408b83ce0	src/utils/config.py	live	7f21a04	7f21a04
+n134239b8d6	module	src.utils.configuration	n5408b83ce0	src/utils/configuration.py	live	7f21a04	a91f3c2	src.utils.config

--- a/docs/map/index/ledger/3b.tsv
+++ b/docs/map/index/ledger/3b.tsv
@@
-n3b5136d824	function	load_config	nf2c1bd3616		live	7f21a04	7f21a04
+n3b5136d824	function	load	nf2c1bd3616		live	7f21a04	a91f3c2	load_config

--- a/docs/map/nodes/13/42/n134239b8d6/prose.md
+++ b/docs/map/nodes/13/42/n134239b8d6/prose.md
@@ -1 +1 @@
-<!-- map: n134239b8d6 · src.utils.config · crawl 2026-08-01 7f21a04 -->
+<!-- map: n134239b8d6 · src.utils.configuration · crawl 2026-08-06 a91f3c2 -->

--- a/docs/map/nodes/3b/51/n3b5136d824/prose.md
+++ b/docs/map/nodes/3b/51/n3b5136d824/prose.md
@@ -1 +1 @@
-<!-- map: n3b5136d824 · src.utils.config:Config.load_config · crawl 2026-08-01 7f21a04 -->
+<!-- map: n3b5136d824 · src.utils.configuration:Config.load · crawl 2026-08-06 a91f3c2 -->

--- a/docs/map/index/names.tsv        (derived index, regenerated)
+++ b/docs/map/index/names.tsv
   ~50 lines: every qualname under this module, rewritten

--- a/docs/map/index/RUN.json
+++ b/docs/map/index/RUN.json
   base/head shas, counts

+++ b/docs/map/index/RUN.md
   the human summary, below
```

Everything else in the header comments of the file's other bundles changes the
same way — **one line each, 9 declarations in `config.py`** — so the honest total
is:

| Tier | Lines changed |
|---|---|
| `index/ledger/*.tsv` | **2** (module row, renamed method row) |
| `nodes/**/prose.md` header comments | 9 (one per declaration that has prose) |
| `nodes/**/facts.jsonl` | **0** |
| `nodes/**/tags.jsonl` | **0** |
| `index/names.tsv` (derived) | ~50 |
| `views/**` | ~20 files, `-diff` marked |
| `index/RUN.*` | 2 files |

**Two lines of identity, zero lines of statement.** If the header-comment
concession is turned off (`header_comments: false`), the store diff outside the
derived indexes is exactly **two lines**.

`RUN.md`, which is what the reviewer actually reads:

```markdown
# Crawl a91f3c2 (base 7f21a04) — 2026-08-06T14:02Z

**Identity: 0 minted, 0 retired, 2 renamed, 0 pending rulings.**

| serial | was | now | rung | score |
|---|---|---|---|---|
| n134239b8d6 | src.utils.config (src/utils/config.py) | src.utils.configuration (src/utils/configuration.py) | 2 (git R097) | — |
| n3b5136d824 | Config.load_config | Config.load | 3 | 1.00 |

**Facts: 44,554 → 44,554 (+0 / -0).**  No structural change detected.

⚠ 3 source references use superseded names — `See: Config.load_config` at
`docs/decisions/config-caching.md:14`, `src/data/collector.py:88`,
`tests/test_config.py:12`. They still resolve.
```

### 4.3 What survives, what re-mints, what a human rules on

- **Survives:** every serial; every statement; all prose; all tag nodes; every
  inbound reference from every other file in the repo; all author-written `See:`
  references, via the `was` column.
- **Re-mints:** nothing.
- **Human rules on:** nothing. The three stale `See:` references are a warning,
  not a gate — the human may fix them at leisure, and if they never do, the
  reference keeps resolving.

**The variant that would have hurt.** If the same commit had also rewritten
`load`'s body to ~30% of the original *and* git had scored the file rename below
40% (so rung 2 never fired), rung 3 would score 0.18 + 0.15 + 0 + 0.05 + 0.03 =
0.41 — barely automatic, and only because rung 3b's unique-residual rule applies.
Below that, one line in `PENDING.md`. The design does not claim this never
happens; it claims the cost is one line of human attention rather than a re-mint.

---

## 5. The re-derive diff scenario, walked

**The change.** `Config.load` gains `strict: bool = False`, documents it, and
calls a new `Config._validate_strict()` when the flag is set. Commit `c4d8e11`.

```python
    @classmethod
    def load(cls, config_file: str = "default.yaml", strict: bool = False) -> Dict[str, Any]:
        """
        Load and validate configuration from YAML file.

        Args:
            config_file: Name of config file in configs/ directory
            strict: Reject unknown top-level keys instead of ignoring them
        ...
            cls._validate_config()
            if strict:
                cls._validate_strict()
```

Cascade: `load` matches on rung 1 (nothing about it moved). `strict` mints
`n7c87e760cd`; `_validate_strict` mints `n930d775b0b`. Two mints, both appended
to their ledger shards — appends, not insertions, because sorting by serial hash
means a new row lands wherever its hash falls, and within a 256-shard scheme that
is a single-line insert.

**The store diff:**

```diff
--- a/docs/map/nodes/3b/51/n3b5136d824/facts.jsonl
+++ b/docs/map/nodes/3b/51/n3b5136d824/facts.jsonl
@@ -1,3 +1,4 @@
 {"s":"n3b235e9f7f","p":"param-of","o":"n3b5136d824"}
+{"s":"n7c87e760cd","p":"param-of","o":"n3b5136d824"}
 {"s":"n828241d062","p":"param-of","o":"n3b5136d824"}
 {"p":"calls","o":"n065e502635"}
@@ -8,6 +9,7 @@
 {"p":"calls","o":"nc828d25214","n":3}
 {"p":"calls","o":"nc9b584a420"}
+{"p":"calls","o":"n930d775b0b"}
 {"p":"calls","o":"?","n":2,"why":"dispatch-unknown-base"}
 {"p":"reads","o":"n15797d173b"}
@@ -14,6 +16,7 @@
 {"p":"reads","o":"n62593c7b9e"}
 {"p":"reads","o":"n7cb9325e3d","n":2}
+{"p":"reads","o":"n7c87e760cd"}
 {"p":"reads","o":"n828241d062","n":5}

--- a/docs/map/nodes/f2/c1/nf2c1bd3616/facts.jsonl
+++ b/docs/map/nodes/f2/c1/nf2c1bd3616/facts.jsonl
@@
+{"p":"contains","o":"n930d775b0b"}

--- a/docs/map/index/ledger/7c.tsv
+++ b/docs/map/index/ledger/7c.tsv
@@
+n7c87e760cd	param	strict	n3b5136d824		live	c4d8e11	c4d8e11

--- a/docs/map/index/ledger/93.tsv
+++ b/docs/map/index/ledger/93.tsv
@@
+n930d775b0b	function	_validate_strict	nf2c1bd3616		live	c4d8e11	c4d8e11

--- a/docs/map/nodes/3b/51/n3b5136d824/prose.md
+++ b/docs/map/nodes/3b/51/n3b5136d824/prose.md
@@
 - `[n828241d062]` **config_file** — Name of config file in configs/ directory
+- `[n7c87e760cd]` **strict** — Reject unknown top-level keys instead of ignoring them

+++ b/docs/map/nodes/93/0d/n930d775b0b/facts.jsonl   (new bundle, 3 lines)
+++ b/docs/map/nodes/93/0d/n930d775b0b/prose.md      (new bundle)
```

**Nine changed lines across four existing files, plus one new bundle** — for a
code change of five lines. The correspondence is tight and it holds because the
canonical sort keeps everything else in place. Note what does *not* appear: the
callee `_validate_config`'s bundle is untouched, because inbound edges are not
stored (the inverse index is built in memory in one pass); and no line-number
churn appears anywhere, because line numbers are not in the store.

**The honest weakness of this diff.** A reviewer reading it sees
`{"p":"calls","o":"n930d775b0b"}` and cannot tell what was called. They must
either read `RUN.md` — which the crawler writes name-resolved —

```markdown
**Facts: 44,554 → 44,558 (+4 / -0).**
- `Config.load` (n3b5136d824): +param `strict`, +calls `Config._validate_strict`, +reads `strict`
- `Config` (nf2c1bd3616): +contains `Config._validate_strict`
**Identity: 2 minted (`strict`, `_validate_strict`), 0 renamed, 0 pending.**
```

— or read the rendered view. The raw diff is precise and unreadable; the
readable artefact is derived. That is the constraint's central trade and §8.2
owns it.

---

## 6. Tag attachment and slug drift

### 6.1 The identity of a tag-minted node

```
serial = "n" + sha1( salt || "tag" || "[" + stable_id + "]" )[:10]            # rung 0
serial = "n" + sha1( salt || "tag" || birth_anchor_serial + "#" + Tag + "#" + ordinal )[:10]
```

The second form is the whole answer to slug drift: **the slug is not in the
preimage.** Identity is derived from *the anchor's serial* and *the tag's
ordinal among same-tag siblings at birth* — two things a rewording cannot touch,
and (because the anchor is itself a serial) two things a rename cannot touch
either. For the §1.3 example, anchor `n3b5136d824`, first `Assumption:` →
`n887b59481b`.

The slug still exists — it is the node's `name` in the ledger, used for
human-written `See:` targets and rendered headings, and it moves to the `was`
column when the wording changes. It is a **property, selected on**, never an
identity. This is the substrate verdict's "opaque serial identity, selection on
properties" applied to the concept layer, and it makes x9's `confidence: medium`
caveat unnecessary for *identity* (though it still applies to whether the author
meant the same thing).

### 6.2 Docstring reworded — walked

The author rewrites the assumption:

```diff
-Assumption: The configs/ directory is the only search root for a bare filename.
-            An absolute path bypasses it entirely; if a caller passes a relative
-            path expecting cwd-resolution, it silently resolves under CONFIG_DIR.
+Assumption: A bare config filename is resolved only against Config.CONFIG_DIR —
+            never against the process working directory. Callers passing a
+            relative path expecting cwd semantics get a silent mis-resolution.
```

Cascade for tag nodes, run after structural identity is settled:

1. Same anchor serial + same tag + identical normalised text → match. (Miss.)
2. Same anchor + same tag + **exactly one live and one new** → match, regardless
   of text. **Hit.** This is the common case and it costs nothing.
3. If several same-tag siblings exist under one anchor: greedy match on word-set
   similarity ≥ 0.50; then by ordinal; leftovers mint.

Store diff:

```diff
--- a/docs/map/index/ledger/88.tsv
+++ b/docs/map/index/ledger/88.tsv
@@
-n887b59481b	assumption	configs_dir_only_search_root	n3b5136d824		live	7f21a04	7f21a04
+n887b59481b	assumption	bare_config_filename_resolved_against_config_dir	n3b5136d824		live	7f21a04	e02b7f5	configs_dir_only_search_root

--- a/docs/map/nodes/88/7b/n887b59481b/prose.md
+++ b/docs/map/nodes/88/7b/n887b59481b/prose.md
@@ -2,4 +2,4 @@
-The configs/ directory is the only search root for a bare filename. An absolute
-...
+A bare config filename is resolved only against Config.CONFIG_DIR — never
+...

--- a/docs/map/nodes/3b/51/n3b5136d824/tags.jsonl
+++ b/docs/map/nodes/3b/51/n3b5136d824/tags.jsonl
@@
-{"o":"n887b59481b","p":"constrained-by","tag":"Assumption","ord":1,"origin":{"owner":"n3b5136d824","line_hint":52}}
+{"o":"n887b59481b","p":"constrained-by","tag":"Assumption","ord":1,"origin":{"owner":"n3b5136d824","line_hint":54}}
```

The serial holds. The edge holds. Any `See:` pointing at the old slug still
resolves through `was`. The `line_hint` moved by two, which is the only thing
about this diff that is noise — and it is confined to `tags.jsonl` because
`line_hint` is the design's one deliberate exception to the no-positions rule.

**The residual weakness, stated:** with two or more `Assumption:` paragraphs
under the same anchor, *reordering* them while also rewording both can swap their
identities, because word-set similarity is the only remaining discriminator. The
mitigation is a lint: when an anchor carries ≥2 same-tag paragraphs, the crawler
emits an advisory into `RUN.md` recommending `[stable-id]`, which moves them to
rung 0 permanently. Not solved, bounded.

### 6.3 The `See:` reference problem, and why humans never write serials

`See: n887b59481b` would be an unwritable, unreadable disaster in source. So:
**humans write names, the store holds serials, and the ledger owns the
mapping** — including historic names, which is precisely what makes references
survive renames. `See: constraint:db_only_data_access` resolves through
`names.tsv` at crawl time. If a resolution fails, the crawler emits a warning
into `RUN.md` and records the unresolved reference as `{"p":"see","o":"?",
"raw":"constraint:db_only_data_access"}` — it never guesses and never drops.

---

## 7. Docent feasibility

A renderer loads all 256 ledger shards into one dictionary (serial → kind, name,
parent, path, state) in a single pass, walks `nodes/**` streaming each
`facts.jsonl`, and resolves every `o` against that dictionary while
simultaneously accumulating the inverse index that gives each page its "called
by" and "written by" sections — one pass, no database, and at f1Brainz scale
(~21k entities, ~300k facts) it fits comfortably in memory. Each bundle becomes
one page: `prose.md` renders as the body, `facts.jsonl` as the structural
sections, `tags.jsonl` as the assumption/constraint callouts, with the
parent-chain walk supplying breadcrumbs and the module row's `path` supplying the
"view source" link. The site's URLs are the serials, which means **a permalink
into the docent survives every rename and every file move** — a bookmark, a
cross-reference from a decision file, or an agent's cached pointer all stay
valid, and the page simply displays a different name than it did last month.

---

## 8. Costs and risks of taking rename-survival seriously

Ordered by how much I would worry.

**8.1 The store is unreadable without the ledger, and that is a single point of
catastrophic failure.** `{"p":"calls","o":"n930d775b0b"}` means nothing on its
own. Lose or corrupt `index/ledger/`, and every statement in the store becomes
noise while the source code is perfectly fine — and rebuilding the ledger from
scratch re-mints every serial, which discards every rename that was ever
resolved and orphans every hand-written `See:`. Git history is the only
protection, and it is real protection, but the design's entire value rests on one
small file family surviving. A path-keyed store degrades gracefully under the
same corruption; this one does not degrade, it stops.

**8.2 Candidate 1's constraint is spent, deliberately and almost entirely.** A
derived fact carries no name, no path, and no line. A PR reviewer cannot audit
crawler output from the diff — they can see *that* four facts were added and
must read `RUN.md` or the rendered view to see *what*. Both of those are
generated by the same crawler whose output is being audited, so the audit is not
independent. The mitigation that would restore independence — a name-resolved
`.diff` artefact generated by a second tool reading only the ledger — is more
machinery, and I have not designed it.

**8.3 No positions means the store alone cannot answer "where".** x4's ranked
hole list with `file:line`, drift reports, jump-to-source, and any evidence field
of the form `<path>:<line>` all require `.map-cache/`, which is gitignored and
therefore absent in a fresh clone until the crawler runs. Everything is
rebuildable in seconds (x7b: 2.3 s for 67 files), so this is friction rather than
loss — but it means the committed store is not self-sufficient for the exact
audit use case the Cartographer workflow cares about, and it means a consumer
skill cannot be a pure file reader.

**8.4 The cascade can silently fuse two entities, and that is the worst failure
this design has.** A rung-4 false positive at 0.86 re-parents a human's prose
onto an unrelated function without asking. Nothing downstream detects it: the
facts are re-derived correctly, the views render, and the only symptom is that
`_solve_knee`'s carefully written rationale is now attached to
`solve_gearshift`. Mitigations are partial — the 0.85 bar, the never-cross-kind
rule, and the fact that every rung-3/4 match is logged in `RUN.md` with its
component scores so a reviewer *can* spot it. Nobody is required to look.

**8.5 The design now depends on git's rename heuristic and on crawl cadence.**
Rung 2 is the cheapest and most reliable rung and it is not ours. `-M`'s
similarity threshold is configurable and its cost grows with the change set; more
importantly, a crawl whose base is several commits back sees the **net** diff,
which can hide an intermediate rename entirely (rename A→B in one commit, B→C in
the next, and git may report A→C or may report a delete and an add). The stated
requirement is therefore: **crawl at every merge to the trunk.** Skipping crawls
degrades identity survival silently. A crawl whose base commit is unreachable
(shallow clone, rewritten history, a fresh clone of a repo whose store predates
it) falls back to rung 1 only, which re-mints every rename since the last
reachable base — the design's second catastrophic mode, and the reason
`RUN.json`'s base sha must be treated as load-bearing state.

**8.6 Alias chains are permanent and nothing collects them.** Every merge adds a
row to `aliases.tsv` and every read path must consult it. After years the file is
long, resolution is two lookups deep in places, and flattening it requires a
human ruling because flattening is the one operation that *does* rewrite
author-written references. I chose unbounded growth over automatic rewriting
because automatic rewriting of a human's `See:` is exactly the class of silent
damage 8.4 describes.

**8.7 The 50/50 split is an honest re-mint.** §3.3. Two comparable residues both
mint, the original goes absent, and the human's prose sits on an absent entity
until a ruling arrives. The design cannot do better without guessing, and
guessing here is 8.4.

**8.8 Two crawler-owned lines still churn on rename.** The `prose.md` header
comment (one line per renamed declaration) and `tags.jsonl`'s `line_hint`. Both
are concessions I made on purpose — legibility and write-back respectively — and
both are strictly proportional to what actually changed, never to inbound
references. `header_comments: false` removes the first for anyone who wants the
constraint pure.

**8.9 Serials fuse on qualname resurrection.** Delete `foo()`, add an unrelated
`foo()` two years later, and the birth-name hash collides. The `~2` suffix rule
catches it when the absent row is still in the ledger and the bodies differ; it
does **not** catch it once the entity has aged into `ledger-retired.tsv` and the
matcher stops consulting it. Bounded and rare, but real.

**8.10 Two things the parent's lean gave up for free that I paid for.** A
path-mirrored store lets you `ls` the store and understand it, and lets `git log`
on a source file's store counterpart show that entity's map history directly.
Here, `git log docs/map/nodes/3b/51/n3b5136d824/` gives the history of an
*identity* rather than a *file* — which is more correct and less discoverable. A
`map log <qualname>` CLI closes the gap; it is machinery that a path-mirrored
store would not need.

**8.11 Not designed, and it should be named rather than implied:** the
concurrent-branch merge of two ledgers that both renamed the same entity
differently (deterministic mint makes *additions* merge cleanly; conflicting
*renames* are a normal git text conflict on one line, which is the good outcome,
but nobody has walked it); the cost of the second full parse on a very large
repo; and whether 256 shards is the right number at 10× scale.
