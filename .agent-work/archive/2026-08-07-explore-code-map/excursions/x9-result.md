# x9 result — the prefix grammar: what prior art supports, and how it lands on the existing map-model

**Type:** research · **Date:** 2026-08-05 · Everything read-only; nothing installed, run, or written into any repo.

**Read first (constraints honored, not re-derived):** `x8-result.md` (the 454-item content classes and the three resisting classes), `x3-result.md` (markers are the mechanism; the composite taxonomy; the free-prose F1 numbers), `x2-result.md` §1.2 and §3.2 (Doxygen grouping; org-babel's provenance-marker law).
**Model read in full:** `skills/cartographer/references/map-model.md`, `skills/cartographer/templates/ARCHITECTURE_DECISION.template.md`, and f1Brainz's live `overlays/constraints.yml` + `overlays/purposes.yml`.

---

## Direct answer

**Recommended grammar: four node-minting tags plus one reference form, written as `Word:` paragraph prefixes inside ordinary docstrings — `Assumption:`, `Constraint:`, `Rationale:`, `Rejected:`, and `See: <node-id>`. Nothing else; the untagged docstring body stays untagged and becomes the struct's purpose.**

Two findings carry it, and the second is the more useful one.

**The strongest prior-art anchor is Go's `Deprecated:` convention** — a bare capitalized word plus a colon starting a paragraph inside an ordinary doc comment, with no sigil, no new syntax, and no parser of its own. It is adopted across the whole Go ecosystem and is consumed by two independent tools (pkg.go.dev hides the identifier; staticcheck's SA1019 warns on use). It is the only assertion marker surveyed that achieved ecosystem-wide adoption *without* a formal specification, a build step, or a verifier, and it is the exact shape this design needs: authored where the code is, invisible to every tool that does not know about it, mechanically detectable by the one that does.

**The mapping half has a cleaner answer than expected: the grammar needs no edge vocabulary at all.** Every edge type in the map model is uniquely determined by the *kind of its target node* — `supports` targets `capability:`, `constrained-by` targets `constraint:`/`assumption:`, `explained-by` targets `decision:`, `verified-by` targets `claim:`, `emits` targets `event:`. The only edge that is not (`depends-on`, struct→struct) is the one x1 already showed is extracted from imports and calls rather than from prose. So a crawler that knows (a) the enclosing struct, from the comment's position, and (b) the target node's kind, from its id prefix, can emit the edge by table lookup. **The tags only have to name nodes. The edges fall out.** That is what makes a classified comment become a graph statement mechanically, and it is why the tag count can stay at four.

The line that decides *which* four is also principled: **the grammar mints only the node kinds whose truth is local to a single anchor.** `assumption:`, `constraint:`, and `claim:` are assertions one author, looking at one function, is competent to make. `capability:`, `event:`, and `decision:` are not — the map model reserves all three behind an explicit promotion gate (a capability is promoted only when "shared or cross-cutting"; an event only when it "crosses a boundary"; a decision anchor requires authority, structural consequence, and a review trigger). A comment cannot know whether a behavior is cross-cutting. So comments *reference* those three by id and never mint them. The tag vocabulary stops exactly where the model's judgment gate starts, which is also why this stays a standard rather than an invention.

---

## 1. Survey: what shipped, what stuck, what died

### 1.1 The five families

**(a) Doc-generator tag sets — Javadoc, JSDoc, Doxygen.** Javadoc's core is `@param`, `@return`, `@throws`, `@see`, `@deprecated`, `@author`, `@since`. Measured usage in one Java corpus is dominated by three of them: **`@param` 18,052 occurrences, `@return` 11,100, `@throws` 5,342** ([arXiv:1806.04616](https://arxiv.org/pdf/1806.04616), *secondary* — reached through a search summary; corpus not inspected). Doxygen went the other way and now ships **roughly 180 special commands** ([Doxygen: Special Commands](https://www.doxygen.nl/manual/commands.html), *primary*), of which only about a dozen express an assertion or judgment rather than formatting, linking, or structure: `\note`, `\warning`, `\attention`, `\remark`, `\pre`, `\post`, `\invariant`, `\deprecated`, `\bug`, `\todo`, `\test`, `\important`.

The pattern across the family is consistent and it is the survey's first lesson: **the tags that get used are the ones whose content is derivable from, and checkable against, the declaration they sit on.** `@param` names a parameter that exists; the doclint checks it. `\invariant` names a condition nobody verifies, and it is rare. Note also what x3 measured about `@param`/`@throws` — they are "at least two times more predictable than a non-javadoc comment sentence," i.e. the most-used tags carry the least information. That is a warning against choosing tags by adoption alone.

**(b) Python docstring styles — Google, NumPy, reST field lists.** Sphinx's Napoleon recognizes about 23 section headers: `Args`/`Arguments`/`Parameters`, `Keyword Arguments`, `Other Parameters`, `Returns`/`Return`, `Yields`/`Yield`, `Raises`, `Warns`, `Attributes`, `Methods`, `Example`/`Examples`, `References`, `See Also`, `Note`/`Notes`, `Warning`/`Warnings`, `Todo` ([Sphinx: napoleon](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html), *primary*).

**Count how many of those 23 express a judgment rather than restating the signature or pointing somewhere: exactly three — `Note`, `Warning`, `Todo`.** Every other section is either signature-derived (parameters, returns, raises, yields, attributes) or navigational (examples, references, see also). The most widely deployed docstring grammar in Python, after fifteen years of accretion, contains three assertion-force markers, and none of them is typed by *what kind* of assertion it is. That is the empirical size of the hole this grammar fills, and it is also a size argument: four is not obviously too few.

One concrete adoption datum that matters more than it looks: **`napoleon_custom_sections` lets a project register its own section headers in one config line**, optionally styled like an existing section ([same source](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html), *primary*). So four new `Word:` prefixes can become first-class rendered sections in an existing Sphinx build without forking anything — which supplies the "something visibly consumes it" property that §1.3 argues is the survival condition.

**(c) Contract conventions — Eiffel DbC, JML, ACSL, .NET Code Contracts, Microsoft SAL.** Eiffel is the small, surviving one: `require` / `ensure` / `invariant`, three keywords, executable at runtime, part of the language. JML is the large, academic one, and its own community says why: JML "has become a very large language, containing many different specification constructs, **some of which are only sensible in a single analysis technique**" — the community is still working toward "a single JML language, with a single semantics" ([JML Reference Manual](https://www.openjml.org/documentation/JML_Reference_Manual.pdf) and surrounding literature, *secondary*). That is vocabulary bloat diagnosed from the inside, and it is the sharpest available argument for the IBIS discipline the brief imposes.

**.NET Code Contracts is the family's clearest death.** It is not supported in .NET 5 or later; Microsoft's own guidance now points to nullable reference types instead ([Microsoft Learn: Code Contracts](https://learn.microsoft.com/en-us/dotnet/framework/debug-trace-profile/code-contracts), *primary*; the developer confusion trail is visible in [dotnet/docs#17640](https://github.com/dotnet/docs/issues/17640) and [dotnet/runtime#23869](https://github.com/dotnet/runtime/issues/23869), *secondary*). What it required was a binary rewriter and a static checker — machinery that had to be installed, configured, and kept working across toolchain versions. What replaced it was a language feature with zero setup cost. **The annotation lost to the thing that needed no ceremony.**

**SAL is the family's clearest survival, and for the opposite reason.** `_In_`, `_Out_`, `_Inout_`, `_Ret_maybenull_` and friends annotate function parameters, and "the majority of C Runtime functions included with Visual Studio 2005 and the Windows SDK functions were annotated" ([Microsoft Learn: Understanding SAL](https://learn.microsoft.com/en-us/cpp/code-quality/understanding-sal), *primary*). SAL survived because the compiler reads it and the developer sees a warning. Same shape as Go's `Deprecated:`; different syntax; identical mechanism.

**(d) Annotation and attribute systems.** Java `@Deprecated` and `@SuppressWarnings`, Rust `#[deprecated(since, note)]` and `#[must_use]`. These are the highest-compliance assertion markers in existence, and the reason is that the compiler enforces them: `#[must_use]` produces a warning at every call site that drops the value. They are also the least transferable to this design, because they need a language change to add a new one. Noted and set aside.

**(e) Lightweight, unspecified conventions — the TODO/FIXME/HACK/XXX lineage, and the lint-suppression grammars.** `TODO`/`FIXME`/`HACK`/`XXX` have no specification, no owner, and universal adoption. The entire self-admitted-technical-debt literature is built on them as a keyword pre-filter (x3 §1.4: 33,093 heuristically filtered comments reduced to 2,457 SATD instances before any classifier runs). They cost nothing and mean nothing precise, which is exactly the trade.

The more interesting sub-family is the machine-directive one: `# noqa: E501`, `# type: ignore[arg-type]`, `// eslint-disable-next-line <rule>`, `//nolint:<linter>`, `#pragma warning disable`, `@ts-expect-error`, and — the one x2 §2.1 already flagged as worth stealing — `# docstr-coverage:excused`. Every one of these is a `marker:argument` pair placed next to the code it is about, and every one is adopted heavily inside its ecosystem. **They stuck because a tool reads them and the author immediately sees the consequence.**

### 1.2 What each family covers, in one table

| Family | Assertion classes it covers | Adoption friction | Verdict |
|---|---|---|---|
| Javadoc / JSDoc core | precondition-on-input, postcondition, exceptional condition, deprecation, pointer | none — plain comment text, generator optional | **stuck**; usage concentrates in 3 signature-derived tags |
| Doxygen full set (~180) | everything, including grouping, pre/post/invariant, bug, todo, test | none to write; ~180 commands to learn | **stuck as a generator, collapsed to a used subset**; the judgment commands are rare |
| Doxygen `\defgroup`/`\ingroup`/`@{ @}` | concept membership spanning N declarations | low; needs group definitions somewhere | **stuck**, and it is the 20-year-old answer to concept-spanning (x2 §1.2) |
| Napoleon / Google / NumPy sections (~23) | signature restatement + `Note`, `Warning`, `Todo` | none; extensible via `napoleon_custom_sections` | **stuck**; carries only 3 judgment markers, none typed |
| Eiffel DbC (3 keywords) | pre / post / invariant | language-level; runtime-checked | **stuck inside Eiffel**, never travelled |
| JML | pre/post/invariant/frame/purity/nullity and much more | verifier toolchain; large, contested vocabulary | **academic only**; bloat named by its own community |
| .NET Code Contracts | pre / post / invariant | binary rewriter + static checker | **died**; unsupported from .NET 5, superseded by a zero-setup language feature |
| SAL | parameter roles, nullity, buffer sizes | none at write time; compiler already reads it | **stuck at Windows scale** |
| `@Deprecated`, `#[must_use]`, `#[deprecated]` | directive to caller, obligation on return value | language change to add a new one | **stuck**; not extensible by us |
| TODO/FIXME/HACK/XXX | "something is wrong here", untyped | zero | **stuck universally, means nothing precisely** |
| `# noqa`, `# type: ignore`, `eslint-disable`, `docstr-coverage:excused` | a scoped, typed exemption or judgment about a specific check | zero; the tool already parses comments | **stuck**; the cleanest working model of `marker: argument` next to the code |

### 1.3 The survival condition, stated once

Across all eleven rows there is one predictor of whether a comment-tag grammar was adopted, and it is not expressiveness, precision, or standardization:

> **A tag survives when writing it changes what some tool does, and the author sees that change. A tag dies when using it requires installing machinery first.**

Go's `Deprecated:` (no syntax, two consumers) and SAL (no setup, compiler reads it) sit at one end. .NET Code Contracts (rewriter plus checker) sits at the other, and it is dead. JML sits near it, alive only where a verifier is already part of the workflow. Doxygen's `\invariant` is the in-between case: costless to write, but nothing reads it, so nobody writes it.

**The design consequence is direct.** The four tags proposed below must ship with the crawler that consumes them, and the first visible consequence should be cheap — a hole-queue entry, a rendered Sphinx section, or a drift-diff line — not a verification result. Shipping the grammar without a consumer reproduces `\invariant`.

---

## 2. The proposed grammar

### 2.1 Recommendation — four node-minting tags and one reference form

Written as `Word:` at the start of a paragraph inside an ordinary docstring or comment block. Go's form exactly: no sigil, no bracket syntax, no position requirement beyond starting its own paragraph. An optional `[stable-id]` immediately after the colon fixes the node id when the author wants one; otherwise the id is slugged from the text and the crawler carries it as low-confidence.

```
Assumption: FastF1 team names match the stored session_classifications.team
            values. If this drifts, the estimate_store backfill silently
            mismatches constructors.

Constraint: [db_only_data_access] Analysis reads from the DB only; no direct
            FastF1 calls from this module.

Rationale:  The brake-onset knee is a benign kink, not a discontinuity — the
            energy and force state identities agree across it.

Rejected:   A dense N x N cross-view covariance matrix. It reproduces this
            result and costs O(n^2) memory; do not re-propose it.

See:        decision:decoupled_1d_longitudinal
```

Five markers. Four mint nodes; `See:` mints only an edge.

**Why these four names, tag by tag.**

- **`Assumption:`** — no doc-generator ships an `\assume` command, so there is no established *tag* to borrow. There is, however, an established *lexical* marker: x3's assumption corpus is built entirely on self-claimed assumptions flagged with the word "assume" (3,084 across nine repositories), and the F1 0.9584 detector rests on that marking. So this is the established word without an established tag, which is the honest framing. It also names a map-model node kind exactly.
- **`Constraint:`** — deliberately *not* `Requires:` and *not* `Invariant:`, despite both being better-established. `requires` in JML, Eiffel, and Doxygen's `\pre` all mean a precondition on a call; `invariant` in all three means a state predicate over object fields. f1Brainz's real constraints are neither: `constraint:latent_power_no_evo_import` is an import-direction rule and `constraint:db_only_data_access` is an architectural policy. Borrowing a thirty-year-old contract keyword and using it for something else is worse than using the model's own plain-English kind name, which is what `Constraint:` is — not coined dialect, just the noun already in `overlays/constraints.yml`.
- **`Rationale:`** — the most established name available, and it is established in five independent places at once: Pascarella's `PURPOSE::RATIONALE`, Rani's CCTM `Rationale`, the standard ADR section heading, the Cartographer decision template's `## Rationale`, and f1Brainz's own `rationale:` field inside `constraints.yml`.
- **`Rejected:`** — from the ADR/decision-template section `## Rejected Alternatives`, which the Cartographer template already uses with a usage rule that reads like a specification for this tag: *"Preserve an alternative ONLY when a future agent is likely to rediscover or re-propose it."* x8 measured this class at 58 records with 84% anchoring on live code, and it earns its own tag rather than folding into `Rationale:` for two reasons: its job is different (prevent re-proposal, not explain a shape), and its lifecycle is different (its anchor is the thing most likely to be deleted).
- **`See:`** — from Javadoc `@see` / Doxygen `\see` / NumPy `See Also`, strengthened by requiring a typed node id as the argument. It absorbs Doxygen `\ingroup`'s job (concept membership spanning N declarations, x2 §1.2) and x8's named systematic loss (the decision-to-code index) with one marker, because the target's kind prefix already carries the edge semantics.

**What the grammar deliberately does not claim: `Note:`, `Warning:`, `Todo:`, `Example:`.** All four are existing Napoleon sections with existing meaning and rendering. `Todo:` in particular is future work, which the map model routes to Triage and explicitly excludes from the map. The grammar must live inside the docstring convention it shares a file with, not fight it.

**The zero-tag majority case.** The untagged docstring body needs no tag at all: it becomes the enclosing `struct:` node's `purpose` field, exactly as x1 measured (72% of classes and public functions already carry a docstring; 646 parameters already have prose in Google-style `Args:` blocks). This is the discipline the brief asks for, applied honestly — the single largest content class in x8's census, explanation-what, earns *no* tag, because position already types it.

### 2.2 Untaken road A — two tags (maximal parsimony)

`Assumption:` and `Constraint:` only. Rationale and known-false stay in the untagged body attached to the struct as purpose prose; the decision-to-code index is recovered by matching bare `decision:<id>` strings anywhere in a comment.

**The case for it:** IBIS taken to its limit — three node types and nothing else for fifty years ([Kunz & Rittel, 1970; gIBIS](https://www.cognexus.org/IBIS-A_Tool_for_All_Reasons.pdf)). x8 showed 89% of why-content anchors fine without any tag. And `assumption:`/`constraint:` are the two map-model kinds that genuinely have nowhere else to live.

**Why not:** it discards `Rejected:`, which x8 showed is simultaneously the smallest class (58 records, one per eight source files) and the highest value per record — the class whose whole stated purpose is stopping the next agent re-proposing a dead idea. And it pushes rationale retrieval back onto free-prose classification, which is precisely the thing x3 measured at F1 0.21–0.31 and the exploration already culled. Parsimony that reintroduces the culled failure mode is not parsimony.

### 2.3 Untaken road B — seven tags, one per overlay kind

`Capability:`, `Event:`, `Constraint:`, `Assumption:`, `Decision:`, `Claim:`, `Rejected:`. Perfect 1:1 with the map model; no mapping table needed at all.

**The case for it:** the mapping section below shrinks to "the tag is the kind." Nothing to remember.

**Why not, and this is the load-bearing reason:** three of those kinds are gated behind judgment the model states explicitly. A capability is promoted "when the behavior is shared or cross-cutting — referenced by more than one struct." An event is promoted only when it "crosses a boundary" or is "a named contract other structures observe." A decision anchor requires authority, current structural consequence, and a review trigger. **Not one of those conditions is knowable from inside a single function's docstring.** A `Capability:` tag would let any author mint a durable node on a local property, which breaks the sparseness doctrine the model spends its whole Inclusion Rule defending. The four recommended tags are exactly the assertions whose truth is local to their anchor; `See:` covers the rest by reference.

---

## 3. The mapping table — tag to emitted statement

**Anchor** = the enclosing `struct:` node, resolved from the comment's position (module, class, or function), which is x1's measured mechanism. **Provenance** on everything the crawler emits is `generated`; **evidence** is `<path>:<line>`.

| Tag | Node emitted | Edge emitted | Notes |
|---|---|---|---|
| *(untagged docstring body)* | none | none | sets `struct:<anchor>.purpose` |
| `Assumption: <text>` | `assumption:<id>` — `kind: assumption`, `label` from first clause, `summary` = full text | `struct:<anchor> --constrained-by--> assumption:<id>` | matches the model's assumption shape exactly ("what is relied on, and what breaks if false") |
| `Constraint: <text>` | `constraint:<id>` — `kind: constraint`, `label` = text | `struct:<anchor> --constrained-by--> constraint:<id>` | same shape as f1Brainz's live `constraints.yml` entries |
| `Rationale: <text>` | `claim:<id>` — `kind: claim`, `summary` = text | `struct:<anchor> --explained-by--> claim:<id>` | see §4: the model contradicts itself on this edge |
| `Rejected: <text>` | `claim:<id>` — `kind: claim`, `summary` = text, `origin.tag: Rejected` | `struct:<anchor> --explained-by--> claim:<id>` | a negative claim; the `origin.tag` field is what makes "do not re-propose" mechanically findable |
| `See: capability:<id>` | none | `struct:<anchor> --supports--> capability:<id>` | edge type derived from target kind |
| `See: constraint:<id>` / `See: assumption:<id>` | none | `struct:<anchor> --constrained-by--> target` | the multi-anchor case: the same constraint referenced from N files |
| `See: decision:<id>` | none | `struct:<anchor> --explained-by--> decision:<id>` | **this is x8's decision-to-code index, recovered** |
| `See: claim:<id>` | none | `struct:<anchor> --verified-by--> claim:<id>` | |
| `See: event:<id>` | — | **not emitted** | direction is ambiguous from a comment; see §5 |

**The mechanical rule underneath the table, stated once:** the edge type is a pure function of the target node's kind. A crawler needs no edge vocabulary and no edge tags — it needs the anchor (from position) and the target kind (from the id prefix), and the edge is a six-row lookup. `depends-on` is the sole exception and it never comes from prose; x1 already derives it from imports and calls.

**One added field, serving two requirements at once.** Every generated overlay node carries `origin: {tag: <Tag>, path: <file>, line: <n>}`. It distinguishes `Rationale:`-claims from `Rejected:`-claims without a new node kind, and it *is* the provenance marker org-babel's detangle law requires (x2 §3.2) — the pointer that makes graph-side edits a lookup back into the source rather than a similarity match. Two open threads served by one field.

**Confidence.** Nodes minted with an explicit `[stable-id]` get `confidence: high`; nodes with a slugged id get `confidence: medium`, because the id is not author-guaranteed to be stable across a rewording. This matters for the rename/move identity thread (open thread 2) and does not solve it.

---

## 4. A contradiction inside `map-model.md` that this mapping exposes

Surfaced rather than smoothed, because the `Rationale:` row depends on it.

The **Edge Types** section says `explained-by  node -> decision  (this is explained by that decision anchor)` — target restricted to `decision:`.

The **Migration From Prior Ontology** section says short verifiable rationale "becomes a `claim:` (**reached via `verified-by` or `explained-by`**)" — explicitly allowing `explained-by` to target a `claim:`.

These cannot both stand. The mapping above follows the migration section, and the recommended fix is to widen the edge table to `explained-by  node -> decision | claim`, for two reasons: "explained by" is what a reader means when a claim explains a shape, and `verified-by` means something different and useful that should not be overloaded (the model calls it "the trust dimension"). Routing rationale through `verified-by` would make every explanatory comment look like evidence of correctness, which is a worse outcome than a one-line amendment. **This is a small, concrete change to `map-model.md` that the grammar requires; it is not optional and it is not this excursion's to make.**

---

## 5. The residue — what the grammar deliberately does not carry

Named as untaken roads, with the reason each is refused rather than deferred.

**(a) Deleted-anchor known-false — x8's falsification, 6 records.** The grammar carries `Rejected:` for the 84% of known-false records whose anchor is live code, which is the standard shape ("we chose A over B", and A's function is B's obituary). It does **not** solve the other shape ("we built B, measured it, removed it"), and it cannot: a tag cannot live in a file that no longer exists. The P1b braking-kernel record has no `src/` file to sit in. This needs a home outside the source tree — a surviving decision anchor, or a tombstone record keyed to the deleted path — and the grammar should not pretend otherwise. **Refused, not deferred:** any attempt to place the tombstone on a *nearby surviving* file makes the record's anchor arbitrary, which is how it gets deleted the second time.

**(b) Artifact staleness — 5 records.** No code line is wrong; a stored `.db` or `.json` is. There is no incorrect line to tag, and the fact is time-varying with no event that would prompt a comment update when someone re-batches. A comment asserting "this artifact is stale" is a lie in waiting the moment it is regenerated. This belongs to a runnable check whose result feeds a `claim:` via `verified-by` — the trust dimension the model already has — not to a write-time tag.

**(c) Freeze-before-look provenance — 3 records.** The load-bearing fact is a commit *ordering*, which git proves and a comment cannot, and a copied comment survives exactly the invalidation the discipline exists to catch. This yields a rule worth stating as doctrine rather than as an exclusion: **no tag may assert a fact about the file's own history.** Any such assertion is copy-paste-survivable, and a survivable false assertion is worse than an absent one.

**(d) The forward roadmap — 9 items.** Future interfaces for code that does not exist. The map model routes future work to Triage and lists "future architecture plans" as out of scope; `Todo:` is deliberately unclaimed for the same reason. Not carried.

**(e) Claims above every file — 3 parentless purpose nodes.** `purpose:race_prediction` and its two siblings say what the *system* is for. No file owns them, so no comment position anchors them. They stay curated. This is the one place the grammar visibly cannot replace the overlay.

**(f) Measurement tables — the soft-(c) 11.** The grammar carries the *verdict sentence* ("do NOT wire; keep `prepare_coast_samples` incumbent") as `Rejected:` or `Rationale:`. The 20-line swept-parameter tables stay wherever they are. A tag that swallowed a table would produce a `claim:` summary nobody can read.

**(g) The `emits` edge.** `See: event:<id>` is not emitted because the direction is ambiguous — the same reference in a producer's docstring and a consumer's docstring means opposite things, and nothing in the comment distinguishes them. Emission is better detected from a publish call site than from prose. Of the six edge types, comments produce four (`supports`, `constrained-by`, `explained-by`, `verified-by`), code structure produces one (`depends-on`), and `emits` stays curated.

---

## 6. Scoped nulls

Each kills *this pass under these conditions*, not the idea.

**Nothing was measured.** No tag was written into any file, no crawler was written or run, no comment was parsed. Every claim about what a crawler *would* emit is design over two documents, not an observation. The mapping table has never been executed against a single real docstring.

**The mapping was checked against one map model and one repository.** `map-model.md` plus f1Brainz's live overlays. Whether the "edge type is a function of target kind" property survives a second repository's overlays, or a future model revision, is untested — and the whole no-edge-vocabulary result rests on it.

**Tag-name collisions were checked only against Napoleon.** `Assumption:`, `Constraint:`, `Rationale:`, `Rejected:`, and `See:` were checked for conflict against Sphinx/Napoleon's 23 section headers and Javadoc's core tags. **Not checked:** Doxygen's ~180 commands for a `\see`-adjacent collision in a C++ file, JSDoc's tag set, pydoclint / darglint / flake8-docstrings rule behavior on unrecognized paragraph prefixes, or what any of these do when the same file mixes conventions.

**Not surveyed at all, and one of them is a real gap.** The **Checker Framework** — Java's `@Nullable`/`@NonNull` pluggable-type ecosystem — is arguably the largest deployed assertion-annotation system in existence and was not examined; if any body of practice has measured what happens when thousands of developers write typed assertions at scale, it is that one. Also unsurveyed: Ada/SPARK contracts, ACSL/Frama-C, Dafny, Liquid Haskell, Kotlin contracts, Swift documentation markup, C# XML doc comments (`<summary>`/`<remarks>`/`<exception>`), rustdoc's section conventions beyond the two attributes named, Sphinx directives (`.. deprecated::`, `.. versionadded::`), and Doxygen's `\xrefitem` custom-command mechanism — which is the closest thing to a user-definable tag kind in a shipped generator and would have been the most directly relevant thing to read.

**No usage-frequency data for the judgment tags.** The claim that Doxygen's `\invariant`/`\pre`/`\post` are rare rests on the command list plus the Javadoc frequency numbers plus x3's taxonomy proportions, **not** on a measured Doxygen corpus. Nobody counted. Likewise no measurement of how often Napoleon's `Note`/`Warning` are actually used.

**The Javadoc frequency numbers are secondary.** 18,052 / 11,100 / 5,342 reached this report through a search summary of [arXiv:1806.04616](https://arxiv.org/pdf/1806.04616); the paper was not fetched and the corpus it measured is unknown here. Treat the *ordering* as safe and the absolute counts as approximate.

**The .NET Code Contracts death was diagnosed, not measured.** That it is unsupported from .NET 5 is primary from Microsoft's own docs. That the *reason* was the rewriter-and-checker setup cost is this report's reading of the deprecation plus developer issue threads, not a stated cause from Microsoft.

**The survival condition in §1.3 is an inference over eleven cases, not a result.** It fits every row surveyed, and it was not tested against a counter-example search — no deliberate hunt was made for a widely-adopted tag that nothing consumes, or for a tool-consumed tag that failed anyway.

**Not asked, therefore not answered: whether anyone will write the tags.** x3's assumption corpus varied from 1,460 self-claimed assumptions in TensorFlow to 8 in Keras. Tag density is a property of a project's culture, not of code. Nothing here predicts adoption inside constellation projects, and the agent-education half of the standard is where that question actually lives.

**Anchor resolution is assumed, and only half-measured.** That a docstring's enclosing struct is derivable from position is x1-measured for Python. For leading comments (culled in cycle 1 at +1.7pp), for module-level tags that should attach to a package rather than a file, and for languages without a docstring convention, it is untested. A `Constraint:` written at module scope about a whole package has no obvious anchor level, and this pass did not settle it.

---

## Sources

Doc-generator tag sets:
- [Doxygen: Special Commands](https://www.doxygen.nl/manual/commands.html) · [Doxygen: Grouping](https://www.doxygen.nl/manual/grouping.html) *(via x2 §1.2)*
- [Sphinx: napoleon extension](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html) — section list and `napoleon_custom_sections`
- [*Deep Learning to Detect Redundant Method Comments*, arXiv:1806.04616](https://arxiv.org/pdf/1806.04616) — Javadoc tag frequencies *(secondary)*

Contract conventions:
- [JML Reference Manual, 2nd ed.](https://www.openjml.org/documentation/JML_Reference_Manual.pdf) · [Formal Specification with JML (Chalmers chapter)](https://www.cse.chalmers.se/~ahrendt/papers/JML16chapter.pdf)
- [Microsoft Learn: Code Contracts](https://learn.microsoft.com/en-us/dotnet/framework/debug-trace-profile/code-contracts) · [dotnet/docs#17640](https://github.com/dotnet/docs/issues/17640) · [dotnet/runtime#23869](https://github.com/dotnet/runtime/issues/23869)
- [Microsoft Learn: Understanding SAL](https://learn.microsoft.com/en-us/cpp/code-quality/understanding-sal) · [SAL Annotations](https://learn.microsoft.com/en-us/cpp/c-runtime-library/sal-annotations)

Lightweight conventions:
- [Go wiki: Deprecated](https://go.dev/wiki/Deprecated) · [staticcheck SA1019](https://staticcheck.io/docs/checks#SA1019) — **the recommended grammar's primary anchor**
- [docstr_coverage](https://github.com/HunterMcGushion/docstr_coverage) — `# docstr-coverage:excused` *(via x2 §2.1)*

Vocabulary discipline:
- [Kunz & Rittel, IBIS; Conklin, *IBIS: A Tool for All Reasons*](https://www.cognexus.org/IBIS-A_Tool_for_All_Reasons.pdf) — three node types, unchanged since 1970

The model being mapped onto:
- `skills/cartographer/references/map-model.md` · `skills/cartographer/templates/ARCHITECTURE_DECISION.template.md`
- `C:\Programs\f1Brainz\docs\architecture\overlays\constraints.yml`, `overlays\purposes.yml`
