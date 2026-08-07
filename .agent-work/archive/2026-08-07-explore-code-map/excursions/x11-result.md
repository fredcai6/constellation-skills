# PROTOTYPE_RESULT — x11: the articles trial

**Question:** do articles generated from the statement store read as a usable alternative to reading the code — and what does the generator find missing in the statements when forced to render them?

**Verdict on readability is NOT mine.** The pages are at
`.agent-work/explore-code-map/evidence/x11/articles/` (start at `INDEX.md`). What follows is
what the generator could and could not do, measured.

---

## 1. What was built

| artifact | path | size |
| --- | --- | --- |
| 9 module pages + index | `evidence/x11/articles/*.md` | 3,331 lines / 121 KB |
| supplementary AST pass (READ-ONLY on f1Brainz) | `evidence/x11/supplement.py` | 174 lines |
| deterministic renderer | `evidence/x11/render.py` | 482 lines |
| gap counter output | `evidence/x11/gaplog.json` | — |

Rendering is pure templating. No sentence on any page was written by a model: every line is
either a fixed template string, a docstring copied verbatim, or a symbol/number lifted from a
statement. The judgment residue is visibly empty — there is no "this module is the heart of
the system" sentence anywhere, because nothing in the store could source one.

Provenance is marked in-page: unmarked = x7b statements, `[a]` = x7a, `[s]` = had to be fetched
from source (a gap). Of 3,331 rendered lines, **249 carry `[s]`** and **73 carry `[a]`**.

Coverage: 9 modules, 87 entities, 117 module/class attributes, 2,241 source lines. The store's
entity set is exactly complete — its 87 `contains`-derived entities match the AST's 87 with no
misses and no phantoms.

---

## 2. Statement-vocabulary gaps (the measured answer)

Every fact below had to come from source because no statement carries it. Counts are
occurrences across the 9 modules.

| id | missing from the vocabulary | hits | severity when rendering |
| --- | --- | --- | --- |
| **G7-value** | the **value** and **type annotation** of a constant or attribute. `writes` gives the name and nothing else. | 117 | **fatal for `constants.py`** — a 364-line module that is *entirely* constants renders as a bare name list. `DNF_POSITION` with no value is not usable. |
| **G5-span** | entity end line / line count. `q.line` gives the start only. | 96 | moderate — no way to say "this is a 56-line method vs a 3-line one", which is most of what tells a reader where the weight is. |
| **G1-kind** | entity kind: class / function / method / static method / class method / property / async. | 87 | **high** — the store cannot say whether `Config.get` is a method or `Config` is a class. Kind is inferable for classes (they appear as `contains` subjects) but not for property vs method vs staticmethod. |
| **G2-signature** | the callable signature: annotations, defaults, `*args`/`**kwargs`, keyword-only marker, return type. `param-of` gives ordered **names only**. | 79 | **high** — `iter_python_files(roots, project_root, extra_paths)` versus the real `iter_python_files(roots: Sequence[str \| Path], *, project_root: Path = PROJECT_ROOT, extra_paths: Optional[...] = None) -> List[Path]`. The first is not enough to call the function. |
| **G4-docbody** | the docstring past its **first line**. Both stores keep only the summary. | 48 | **high** — Args/Returns/Raises are where the contract lives. 40 of 72 documented entities (56%) have a body the store discards. |
| **G3-decorators** | decorator list (`@dataclass`, `@dataclass(frozen=True)`). | 4 | low count, high consequence — `@dataclass(frozen=True)` on `Violation` and `ResourcePlan` is the single most load-bearing fact about those types. |
| **G6-dunder** | `__all__` / declared re-export surface. | 0 present | untested here — no `src/utils` module declares `__all__`. |

Two more gaps are structural rather than per-fact:

- **G9 — no extraction-window statement.** Nothing in the store says which files were extracted.
  A "referenced by: 0 sites" reading is therefore ambiguous between *unused* and *outside the
  window*. Four of nine modules (`console`, `ids`, `f1_calendar`, `simplification_limits`) have
  no in-window importer purely because `scripts/` and `tests/` were never extracted. The renderer
  has to hard-code the caveat sentence; the store should have carried it.
- **G10 — stdlib vs third-party is not in the store.** `res: external` covers both. The split you
  see on the pages is the renderer calling `sys.stdlib_module_names`, i.e. a Python-specific
  judgment made at render time rather than a recorded fact.

### Defect found, not a gap

- **D1 — every `q.line` in x7b is 0-based, and the schema does not say so.** Verified across
  **all 87** entities: `store q.line - ast lineno == -1`, uniformly. x7a (SCIP) is 1-based for the
  same entities. Un-corrected, every source link in every article lands one line above the `def`.
  The renderer applies `+1` and says so in each page footer. Two stores disagreeing on line base
  with no statement declaring it is exactly the kind of thing that silently corrupts a map.

### What I expected to be a gap and was not

I initially rendered dataclass fields as "invisible to the extractor" and that was **wrong** —
x7b does emit a `writes` edge from the class for annotation-only declarations, so all 11
`RaceInfo` fields and all 117 attributes are present *by name*. I corrected the renderer before
finalizing. The gap is narrower and more precise than my first pass claimed: names yes,
annotations and values no.

A related near-miss worth recording: the annotations **are** in the store, just unattributed.
`RaceInfo` shows `reads stdlib: datetime.datetime x5, typing.Optional x4, builtins.str x3,
builtins.int x2, builtins.bool` — that is exactly the field type multiset, with no way to join a
type to its field. The information is there; the vocabulary cannot express the binding.

---

## 3. What x7a filled, and how well

x7a supplied **63** per-parameter prose statements for `src/utils`, rendered as `[a]` on 73 lines.
Quality is poor: **62 of the 63 simply repeat the parameter name and colon** before the prose
(`config_file — config_file: Name of config file in configs/ directory`). They are unsplit
fragments of the Args block, not parsed parameter docs.

More decisive: once G4-docbody is closed, x7a's parameter prose is **redundant** — the Args block
in the docstring body already says everything the 63 statements say, and says it correctly. x7a's
"richer param coverage" is a worse-formatted subset of one fact x7b already had access to and
chose not to store.

---

## 4. Noise the store forced the renderer to filter

The raw statement stream is not renderable as-is. Per entity the renderer drops:

- **`res: local`** — 660 reads + 226 writes across the slice. These are local-variable traffic
  inside function bodies. Rendered raw they swamp every real edge. Shown as a count line only
  (`Not shown: 18 local-variable reads, 9 local-variable writes`).
- **reads of the entity's own parameters** — `Config.load_config` alone has 19. Already covered by
  the Parameters section.
- **`res: unresolved`** — 215 in the slice, summarized with the extractor's `why`
  (`dispatch-unknown-base` dominates). Kept visible: a reader should know the map has 7 calls it
  could not resolve, not have them hidden.

Roughly **half the statements in the slice are not article material**. This is not a gap — it is a
finding about what a statement store is for. The store is a query substrate; an article needs a
curation layer on top, and that layer is renderer policy, not data.

---

## 5. Rendering cost

| measure | value |
| --- | --- |
| articles / source line ratio | **1.49x** (3,331 rendered lines from 2,241 source lines) |
| renderer + supplement | 656 lines of Python, written once, reused for all 9 modules |
| re-render wall time | under 2 seconds for the whole package |
| build time (agent, including all diagnosis and two corrections) | ~45 minutes |

The marginal cost of the 10th module is ~0. Essentially all cost is the one-time renderer, and
about a third of that renderer exists only to work around G1/G2/G4/G7 — the supplementary AST
pass (174 lines) would be deleted outright if the statement vocabulary carried kind, signature,
docstring body, and attribute values.

---

## 6. Honest self-assessment of readability

Stated as what I can defend, not as a verdict:

**Reads well.** Small, well-documented modules. `console.md` is genuinely a fair substitute for
reading `console.py` — 33 source lines, 2 functions, full docstrings, complete dependency picture,
and the "Referenced by" count is information the source file itself does not contain. `config.md`
and `f1_calendar.md` are navigable: the Contents list plus per-method Uses table answers "what
touches `_config_data`" faster than grep does.

**Reads badly.** `constants.md`. It is 340 rendered lines that list 52 constant names and cannot
say what any of them equal (G7). Everything a reader wants from that module is the value.

**The hole pages are the interesting case.** `simplification_limits.md` is 14 holes out of 15
entities — every article body is the `[HOLE] no docstring` marker. Whether that page is *useful*
(an honest, actionable hole queue rendered in place, with signature and call graph still intact
around each hole) or *useless* (14 screens of "we don't know") is precisely the judgment I should
not be making. It is the single most valuable page to put in front of the human.

**What I am confident is wrong with the pages:** the "Referenced by" line reads awkwardly when all
references are same-module, and repeated `[s]` markers get visually noisy on entity headers.

A second self-correction, recorded because it cuts the same way as the dataclass one: I first
rendered parameters out of declaration order and was about to log that as a gap. It was my bug —
`param-of` carries `q.line` **and** `q.col`, and sorting on both recovers declaration order
exactly, including across multi-line signatures where every parameter shares `col: 4`. I had
sorted on `col` alone. **Twice in this excursion my first reading blamed the store for something
the store had.** Both times the store was richer than a quick look suggested. Weight the gap table
accordingly: it is what survived two rounds of me being wrong in the pessimistic direction.

---

## 7. Scoped nulls

- One package (`src/utils`), one repo (f1Brainz), one language (Python). Nothing here says how the
  vocabulary holds for a language where signature and kind are not trivially AST-recoverable —
  x5's C++/clang and x6's MATLAB branches are untouched by this.
- The gap list is **what rendering an article demands**. A different consumer (a diff view, a
  search index, a dependency audit) would expose a different gap set. G1/G2/G4 are article-shaped
  needs; do not read them as "the vocabulary is 4 predicates short" in general.
- Readability is asserted, not measured. No human has read these pages. There was no comparison
  arm — nobody read `src/utils` source under the same conditions — so "usable alternative to
  reading the code" is untested, only *renderable*.
- The 1.49x ratio counts markdown lines against source lines including blanks and table rules;
  treat it as an order of magnitude, not a metric.
- x7a was used only for parameter prose. Its `documents` and structural coverage were not
  exhaustively mined; the "x7a is redundant once G4 closes" claim covers parameter prose only.
