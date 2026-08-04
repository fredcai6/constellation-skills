# exc-7-simple-english — a simplified technical English standard for this project's reports

**Excursion:** `EXCURSION_BRIEF exc-7-simple-english` (`.agent-work/explore-post-phase1/IDEAS_BOARD.md:89-94`)
**Question:** What should a simplified-technical-English standard for this project's reports look like, drawing on ASD-STE100 and similar controlled languages, including a local-glossary mechanism and mechanically checkable rules?
**Type:** research and drafting. No doctrine edits. This file is the only file written.
**Date:** 2026-08-03. Repo at `main` = `79db918`.

This report is written under the ten rules it proposes, so you can judge the style by reading it.

---

## VERDICT

**The problem is vocabulary, not sentence length — and a naive "write shorter sentences" standard would fire on the wrong thing.** I measured five of this repo's human-facing artifacts. Their sentences already sit inside the ASD-STE100 limits: medians of 12 to 15 words against a 20-to-25-word cap. What is actually dense is undefined project dialect. About one word in forty is a coined project term, and **not one of those terms is defined anywhere in the repo.** A search for a glossary or terminology heading across every Markdown file in the repo returns zero results.

The fix that matches the measurement is a glossary plus one check that runs off it, not a prose style guide. Doctrine already names `docs/agents/GLOSSARY.md` in four places and the Charter skill already carries an imperative to write it. **The slot is specified and empty.** Filling it converts the dominant defect from a matter of taste into a matter of lookup.

ASD-STE100 supports this reading directly. The standard pairs its writing rules with a controlled dictionary, and it explicitly permits company-specific terms — "technical names" and "technical verbs" — when they come from a company glossary or terminology database. **A local glossary is not a workaround to the standard; it is the part of the standard this project is missing.**

---

## 0. SCOPE — what I did and did not examine

**Examined.** Public pages for ASD-STE100 (`asd-ste100.org` about and FAQ pages, ASD Europe, Wikipedia, TechScribe listing, a technical-writing summary), ISO 24495-1:2023 via its publisher and the Plain Language Association, the US Federal Plain Language Guidelines via digital.gov and search summaries, the Attempto Controlled English literature, and one third-party repurposing of STE for agent-facing English. In this repo: `.agent-work/epic-298/EPIC_SUMMARY.md`, `.agent-work/explore-post-phase1/evidence/exc-1-epic298-RESULT.md`, the same directory's `exc-4-issues-RESULT.md`, `docs/agents/CREW_CONTEXT.md`, `docs/agents/ORCHESTRATOR_CONTEXT.md`, the body of issue #331, and the module docstring of `scripts/grade_lint.py`.

**NOT examined — treat these as open, not as settled negatives.**

- **The official ASD-STE100 Issue 9 PDF itself.** It is free but gated behind a request form. I fetched a third-party copy of Issue 8 and it returned unparseable binary. **Every specific numeric rule below (the 20-word and 25-word caps, the six-sentence paragraph, the three-noun cluster) comes from secondary sources, not from the standard's own text.** Confirm against the official PDF before anyone writes a number into doctrine.
- **The full text of ISO 24495-1:2023.** It is paywalled; the ANSI preview returned HTTP 403. I have the four principles by name from secondary sources but not the clause-level guidelines under them.
- **The Federal Plain Language Guidelines PDF.** Two copies returned unparseable binary. The 15-to-20-word figure below is from a search summary, not from the document.
- **Other controlled languages I did not evaluate:** Caterpillar Technical English, IBM EasyEnglish, Basic English, and the pre-2004 AECMA Simplified English lineage beyond its history.
- **Any measurement of whether agents write or read better under a controlled vocabulary.** I found no study testing this on LLM agents. The nearest evidence is about human readers and machine translation, and it is mixed (see §1.4). **The claim that this will help agent-to-agent communication is a hypothesis in this report, not a finding.**
- **The rest of the repo's artifacts.** I sampled five files and one issue. The coined-term rate below is measured over three of them, not over the corpus.

---

## 1. WHAT THE STANDARDS ACTUALLY SAY

### 1.1 ASD-STE100 Simplified Technical English

STE is a controlled natural language for technical documentation. The European Association of Aerospace Industries began work in 1983 at the request of European airlines, which wanted one form of English for aircraft maintenance documentation that non-native speakers could read reliably. It was renamed ASD-STE100 in 2004 and is maintained by the Simplified Technical English Maintenance Group. **Issue 9 was published on 15 January 2025.**

The standard has exactly two parts, and the split matters for this proposal:

> "STE has two parts: a set of writing rules (part 1) and a controlled dictionary (part 2)."
> — [ASD-STE100 FAQ](https://www.asd-ste100.org/STE_faq.html)

**Part 1** is "53 writing rules in 9 sections that focus on word choice, grammar, sentence structure, and style" ([about STE](https://www.asd-ste100.org/about_STE.html)).

**Part 2** is roughly 900 approved words, and the governing constraint is one word, one meaning:

> "each word has only one meaning and is approved with only one part of speech"
> — [about STE](https://www.asd-ste100.org/about_STE.html)

The dictionary also lists about 1,200 *unapproved* words, each paired with an approved alternative. So the dictionary is not only an allowlist; it is a redirect table.

**The escape hatch is the load-bearing part for us.** STE permits terms outside the 900 words, under two categories:

> Technical nouns and verbs are "applicable to a company, industry, or subject field" and can include non-approved terms when they are part of "official documentation, engineering drawings, company glossaries, or terminology databases."
> — [ASD-STE100 FAQ](https://www.asd-ste100.org/STE_faq.html)

Read that against this repo. Words like `spine`, `arm`, `lease`, `gate` are exactly "technical nouns applicable to a subject field." STE would allow every one of them **on the condition that a company glossary defines them.** This repo has the terms and not the glossary. That is the whole gap, stated in the standard's own vocabulary.

**Specific writing rules** — all from secondary sources, all needing confirmation against Issue 9:

| Rule | Statement | Source |
|---|---|---|
| Sentence length | "no more than 20 words in instructions (procedures) and 25 words in descriptive texts" | [Wikipedia](https://en.wikipedia.org/wiki/Simplified_Technical_English), corroborated by [ClickHelp](https://clickhelp.com/clickhelp-technical-writing-blog/what-is-simplified-technical-english/) |
| Paragraph length | "A paragraph must be at most six sentences long." | [ClickHelp](https://clickhelp.com/clickhelp-technical-writing-blog/what-is-simplified-technical-english/) |
| Noun clusters | "Do not use more than three nouns in a row: 'overhead panel' is permitted, but 'overhead panel battery section' is not." | [ClickHelp](https://clickhelp.com/clickhelp-technical-writing-blog/what-is-simplified-technical-english/) |
| Voice | "Never use the passive voice... not 'The screws should be replaced' (by whom?!), but 'The mechanics replace the screws.'" | [ClickHelp](https://clickhelp.com/clickhelp-technical-writing-blog/what-is-simplified-technical-english/) |
| Verbs | Restricted to infinitive, imperative, simple present, simple past, simple future, and past participle used as an adjective | [Wikipedia](https://en.wikipedia.org/wiki/Simplified_Technical_English) |
| Structure | One instruction per sentence; one topic per paragraph; omit no sentence parts; use vertical lists for complex material | [Wikipedia](https://en.wikipedia.org/wiki/Simplified_Technical_English) |

Two of the published rewrite examples are worth keeping, because they show the method is substitution rather than compression:

| Ordinary English | STE |
|---|---|
| "Follow the safety instructions" | "Obey the safety instructions" |
| "The temperature must be adjusted" | "Adjust the temperature" |
| "No leaks permitted" | "Make sure that there are no leaks" |

Source: [ClickHelp](https://clickhelp.com/clickhelp-technical-writing-blog/what-is-simplified-technical-english/). Note the third example gets *longer*. STE optimizes for one reading, not for brevity.

**On automated checking, the standard's own maintainers are cautious:**

> "several commercial companies offer language checking tools" supporting STE, but "no tool can replace the standard itself." ASD and the STEMG "DO NOT endorse or certify any company" claiming full STE compliance through automated solutions.
> — [ASD-STE100 FAQ](https://www.asd-ste100.org/STE_faq.html)

That is a direct caution against the version of this idea where a linter is the standard. It argues for checks that are narrow and obviously correct, which is what §4 proposes.

### 1.2 ISO 24495-1:2023, plain language

Published June 2023. Drafted and approved by experts from 25 countries representing 19 languages. It rests on four principles: **relevance, findability, understanding, and usability** ([ISO](https://www.iso.org/standard/78907.html), [ITLawCo summary](https://itlawco.com/iso-24495-12023-plain-language-standard/)).

Those trace to the definition the International Plain Language Federation adopted in 2014:

> plain language is communication where "wording, structure and design are so clear that intended readers can easily — find what they need, — understand what they find, and — use that information"
> — [PLAIN](https://plainlanguage.com/plain-language/iso-plain-language-standard/)

One point from the scope is directly relevant, because it settles a question someone will raise:

> The standard's widest use is for documents intended for the general public. "However, it is also applicable, for example, to technical writing, legislative drafting or using controlled languages."
> — [ISO 24495-1:2023 scope](https://www.iso.org/standard/78907.html)

So the plain-language frame and the controlled-language frame are not rivals. ISO explicitly contemplates both. **"Intended readers" is the operative phrase for us: the intended readers of an agent report are Tommy and other agents, not the general public.** That licenses precise technical terms and forbids undefined ones — which is the same conclusion STE reaches by a different route.

### 1.3 US Federal Plain Language Guidelines

The Plain Writing Act of 2010 "established the requirement that content for the public is written for its specific audience" ([digital.gov](https://digital.gov/guides/plain-language)). The Guidelines themselves recommend:

- **Sentence length:** "Write in short sentences," aiming for **15 to 20 words per sentence**.
- **Jargon:** "don't use jargon or technical terms when everyday words have the same meaning," and "when a technical term is necessary, define it the first time it appears."
- **Abbreviations:** they "constantly require the reader to look back to earlier pages, or to consult an appendix. The best solution is to find a simplified name for the entity you want to abbreviate."
- **Consistency:** use the same word for the same concept rather than varying terminology.

Sourced from search summaries of the Guidelines ([WordRake](https://www.wordrake.com/resources/federal-plain-language-guidelines), [digital.gov style guide](https://digital.gov/style-guide)); I could not parse the primary PDF.

Two of these are the strongest rules for this project. "Define it the first time it appears" is the glossary rule. "Use the same word for the same concept" attacks a pattern I found repeatedly in the audit (§2, pattern D).

### 1.4 Controlled language for machines, and the honest caveat

The formal end of this field is **Attempto Controlled English**, developed at the University of Zurich since 1995. ACE is "a precisely defined subset of English that can automatically and unambiguously be translated into first-order logic," so "every ACE text has a single and well-defined formal meaning" ([Wikipedia](https://en.wikipedia.org/wiki/Attempto_Controlled_English)). Tobias Kuhn's [survey and classification of controlled natural languages](https://attempto.ifi.uzh.ch/site/pubs/papers/kuhn2014cl.pdf) is the standard reference for the whole design space.

**ACE is the wrong model for us and it is worth saying why.** ACE buys unambiguous machine parsing at the cost of a grammar authors must be trained in. We do not need first-order logic out of a status report. We need a human and another agent to agree on what "arm" means. STE's design point — ordinary English, restricted vocabulary, human-readable without training — is the right one.

**The caveats I found, which cut against this whole proposal and should be recorded:**

- On simplification generally: "although language models effectively reduce text complexity as measured by objective readability metrics, improvements in readability do not guarantee the maintenance of content accuracy or laypeople's understandability." **A rewrite that scores better can say less.** For this project, where reports carry measured numbers and honest nulls, losing content is a worse failure than being hard to read.
- On controlled language for machines: controlled languages and machine-translation systems "deal only with the sentence as the unit of processing; to be effective, controlled languages must be contextualised at the document level" ([Measuring the Translatability of Simplified English in Procedural Documents](https://www.researchgate.net/publication/3229950_Measuring_the_Translatability_of_Simplified_English_in_Procedural_Documents)). A per-sentence linter cannot reach the defects that live in document structure.
- **I found no evidence, either way, that a controlled vocabulary improves agent-to-agent comprehension.** The brief's premise that jargon is "suspected of confusing agents talking to each other" remains a suspicion. §5 names the cheapest test.

---

## 2. THE REPO AUDIT

### 2.1 The measurement, and the surprise in it

I measured sentence-length distribution over prose in five files, excluding code fences, inline code, table rows, headings, and blockquotes, and splitting list items apart so adjacent bullets are not welded into one oversized pseudo-sentence. Script: `scratchpad/measure.py` (throwaway, not committed).

| File | Prose sentences | Mean words | Median | Max | Over 25 words |
|---|---|---|---|---|---|
| `.agent-work/epic-298/EPIC_SUMMARY.md` | 66 | 13.4 | 12 | 37 | 6 (9%) |
| `evidence/exc-1-epic298-RESULT.md` | 147 | 18.0 | 15 | 64 | 33 (22%) |
| `evidence/exc-4-issues-RESULT.md` | 153 | 15.7 | 13 | 45 | 22 (14%) |
| `docs/agents/CREW_CONTEXT.md` | 44 | 16.0 | 15 | 38 | 7 (16%) |
| `docs/agents/ORCHESTRATOR_CONTEXT.md` | 9 | 13.8 | 15 | 23 | 0 (0%) |

**Caveat on these numbers, stated because the repo's own doctrine demands it.** My first two runs of this script were wrong. Run 1 reported a 111-word maximum; that was several bullets welded together because bullets are not separated by blank lines. Run 2 still reported 104 words, because the splitter did not break a sentence that begins with `#331`. The table above is run 3. **A residual imprecision remains:** the 64-word and 60-word cases in `exc-1` are still probably two sentences each, where a quotation mark or a semicolon defeated the split. Treat the "over 25 words" column as an upper bound.

**The surprise: sentence length is largely a non-problem.** Against the STE caps of 20 words for procedures and 25 for descriptive text, these files are already compliant on average. The median sentence in every file is 12 to 15 words. Only `exc-1` has a substantial tail.

**So a standard built on sentence length would be measuring the wrong thing.** That is the single most useful finding here, and it is the kind of thing that only comes out of counting.

### 2.2 The real density: undefined project dialect

I counted occurrences of 36 candidate coined terms across the three report-style artifacts.

| File | Words | Coined-term hits | Share of tokens |
|---|---|---|---|
| `EPIC_SUMMARY.md` | 996 | 28 | 2.8% |
| `exc-1-epic298-RESULT.md` | 4,363 | 119 | 2.7% |
| `exc-4-issues-RESULT.md` | 8,801 | 161 | 1.8% |

Most frequent terms across all three: `gate` (37), `episode` (36), `corpus` (35), `arm` (25), `supersed*` (22), `spine` (18), `instrument` (14), `graduat*` (12), `lease` (10), `latitude` (8), `collat*` (7), `rhyme` (6), `kernel-break` (6), `conjunct` (6), `gauge` (6), `two-bin` (5), `trip` (5), `harvest` (4), `ablation` (4), `projection` (4), `sediment` (3).

**And the definitions do not exist.** A case-insensitive search for a heading matching glossary, terms, terminology, or vocabulary across every Markdown file in the repo returns **zero matches**:

```
grep -rniE "^#{1,3} *(glossary|terms|terminology|vocabulary)" --include=*.md .
   (no output)
```

Roughly one word in forty is a term whose meaning exists only in the heads of the agents and the human who coined it, and in the run artifacts where it was first used.

### 2.3 Offender patterns, with real sentences

**Pattern A — a coined term used bare, carrying the main claim.**

> "The **PRE arm** was not map-deprived — the map existed, was cited in an auto-loaded `CLAUDE.md`, was read in 4/4 runs and was useful — and it still scored **0/5 on orientation order**."
> — `.agent-work/epic-298/EPIC_SUMMARY.md:10-12`

"Arm" appears 25 times across the sampled artifacts and is never defined. It is borrowed from clinical-trial design, where an arm is one group in a controlled comparison. A reader who does not already hold that borrowing cannot recover it from context, because the sentence uses it as a known quantity. The same file also compounds it into "ablation arm", "measurement arm", and "clean arm" without ever establishing the base term.

**Pattern B — metaphor carrying the claim instead of illustrating it.**

> "The other ~65 issues are the **sediment** of producing those."
> — `evidence/exc-1-epic298-RESULT.md:125`, quoting `LESSONS_AUDIT.md`

> "#337 independently tabulates the same shape appearing four times in one epic **in four costumes**."
> — `evidence/exc-4-issues-RESULT.md:259`

> "it is the highest-confidence target in the backlog because **the mechanism built to find rhymes already found it**, wrote it down, and said so."
> — `evidence/exc-4-issues-RESULT.md:261`

The third is the sharpest case. It is a good sentence and it is also unreadable to anyone who does not know that "rhyme" is this project's word for a recurring pattern across episodes. The metaphor is doing the work that a plain statement should do first.

**Pattern C — compressed notation and borrowed formalism, unexpanded.**

> "It rests on gate (b) alone: never run, **n=0**, the gates are **conjunctive**, so a **conjunction with an unrun conjunct** cannot close."
> — `.agent-work/epic-298/EPIC_SUMMARY.md:31-32`

Twenty-three words, inside the STE cap, and still hard. The difficulty is four pieces of unexpanded shorthand in one sentence, not its length. Plainly: *gate (b) has never been run, so it has no result. All gates must pass together. A set that includes an untested member cannot pass.*

> "so an identically-instrumented POST arm would **null by construction**"
> — `evidence/exc-1-epic298-RESULT.md:43`, and again in the body of issue #331

"Null by construction" is a genuinely useful compression, and it is used in a GitHub issue body — the most public, least context-carrying surface this project writes to.

**Pattern D — the same thing under several names.**

Within `exc-1-epic298-RESULT.md` alone: the measurement setup is "the arm", "the PRE arm", "the apparatus", "the instrument", and "the capture rig". Episodes live in "the store", "the episode store", and "the record store", and `CREW_CONTEXT.md:47` introduces "Record Stores" as a category covering three different things. This is the exact pattern the Federal Guidelines name: use the same word for the same concept.

**Pattern E — the aphorism standing in for the evidence.**

> "**It stopped recurring where it was written down and kept recurring where it was not.** That is a mechanism, verified by grep, not a moral."
> — `.agent-work/epic-298/EPIC_SUMMARY.md:70-71`

The second sentence is defending the first against the charge the first invites. Memorable phrasing reads as a moral, and the author knew it. The underlying fact — a grep returned 2 lines, both in one file, none at orchestrator tier — is stated just above and is stronger without the epigram.

**Pattern F — dialect leaking into agent-to-agent surfaces.**

> "The tag **welds** to its decision either on the decision's own Markdown list-item line, or on the next non-blank line as a child of that bullet..."
> — `scripts/grade_lint.py:19-21`

> "Three binding rulings from a **cold-critic** review"
> — `scripts/grade_lint.py:24`

This is a module docstring, read by every agent that touches the script. "Welds" and "cold critic" are both undefined project dialect. Note also `decision:placeholder-is-not-a-decision` and its siblings — coined slugs used as identifiers, which is fine, but they are never glossed.

### 2.4 The counter-example worth copying

`docs/agents/CREW_CONTEXT.md` is the clearest writing I sampled, and it is not the shortest. Its sentences average 16 words with a 38-word maximum, both higher than `EPIC_SUMMARY.md`. What it does differently is that it names the actor and the mechanism in the same sentence:

> "A check that cannot fail is indistinguishable from one that passed. Before you offer a check as evidence, demonstrate it can reach a failing state — run it against the pre-change tree and show it red, or mutate the thing it guards and watch it go red, then restore."
> — `docs/agents/CREW_CONTEXT.md:78-81`

> "`py` resolves to 3.12.13 (which matches CI's pin) but **has no pytest installed**, so `py -m pytest` does not run the suite — it reads as a silently green run."
> — `docs/agents/CREW_CONTEXT.md:26-28`

Both state a rule and the concrete reason in one move, with no coined term. **This is the house style to standardize on.** It already exists; it does not need to be invented.

---

## 3. PROPOSAL — ten writing rules for agent reports

Drafted for the human's decision. Not shipped, not written into doctrine.

Each rule is stated so it can be applied to the next report without interpretation. The "check" column says whether a machine could enforce it, which matters because mechanization over prose is a project principle.

| # | Rule | Why | Mechanizable? |
|---|---|---|---|
| **1** | **Lead with the outcome.** The first sentence after any heading states what happened or what you found. Reasoning follows. | ISO's *findability* principle. A reader who stops after one sentence should have the answer. | No — human review |
| **2** | **One claim per sentence.** Target 25 words. A sentence over 35 words is a defect. | STE: 20 words for procedures, 25 for descriptive text. Our measured median is 12 to 15, so this rule mostly guards a tail. | **Yes** |
| **3** | **Put each qualification in its own sentence.** Do not nest a caveat inside the claim it qualifies. | Attacks pattern C. The 23-word `n=0` sentence is short and still carries four separate claims. | Partly — count clauses |
| **4** | **Define every project term on its first use in the document,** or link it to the glossary. One clause is enough: "the PRE arm (the runs captured before the change)". | Federal Guidelines: "when a technical term is necessary, define it the first time it appears." STE permits company terms only when a company glossary defines them. | **Yes — see check PL001** |
| **5** | **One name per thing, per document.** Choose one of "arm", "apparatus", "instrument", "capture rig" and use only it. | Federal Guidelines on consistency. Attacks pattern D. | Partly — synonym sets |
| **6** | **Name the actor.** Write "the commander re-derived it", not "it was re-derived". | STE requires active voice. "Should be replaced" — by whom? | Partly — passive detection |
| **7** | **Every number carries its unit and its denominator.** Write "4 of 4 runs", never "improved". Write "10 of 21 tokens, as the commander counted them", never "10 tokens". | This project has already been bitten twice: the 10-of-21 versus 29-of-46 disagreement, and the ruling that a threshold without a unit is unanswerable. | Partly — bare-number heuristic |
| **8** | **Metaphor may follow the plain statement; it may never replace it.** State the fact, then the image, in that order, if the image earns its place. | Attacks patterns B and E. "The mechanism built to find rhymes already found it" is memorable and does not transmit. | No — human review |
| **9** | **Expand compressed notation on first use.** Say what a field name measures before you cite its value: "`map_before_src` (whether the run read the map before any source file) went 0 of 4 to 4 of 4." | Attacks pattern C. Field names are the most common undefined term in measured reports. | Partly — identifier detection |
| **10** | **State what you did not examine, in plain words, near the top.** No coined term is permitted inside a scope limitation. | This project already requires scoped nulls. The rule adds only that the null itself must be readable. | Partly — section presence |

**Rules 1 through 10 are ordered by how much they would have helped the artifacts I audited.** Rules 4, 8, and 9 address the patterns I actually found. Rule 2 is cheap and mostly inert. If only three rules ship, ship 4, 8, and 9.

**One rule I deliberately did not include.** STE restricts verb tenses to six forms and bans most auxiliaries. That is right for aircraft maintenance procedures, where a mechanic executes steps. It is wrong for research reports that must express counterfactuals, unrealized conditions, and honest uncertainty — "an identically-instrumented arm *would* null" cannot be written in simple present. Importing STE's verb rules would force this project's reports to overclaim.

---

## 4. PROPOSAL — the local glossary

### 4.1 Where it lives: the slot already exists

`docs/agents/GLOSSARY.md` **does not exist in this repo** and is referenced in four places:

| Reference | What it says |
|---|---|
| `skills/_shared/global-everyone.md:6` | read `docs/agents/GLOSSARY.md` "if they exist" |
| `skills/_shared/global-orchestrator.md:6` | same |
| `skills/_shared/global-crew.md:6` | same |
| `docs/CONSTELLATION_OVERVIEW.md:38` | Charter owns it; audience "all roles"; scope "shared terms only; no workflow state" |

And the Charter skill already carries the imperative to create it:

> "Write docs/agents/GLOSSARY.md (shared terms only). Confirm it with the user."
> — `.agent-work/20260728-charter-refresh/charter.json:233`

**So no new plumbing is needed.** Every role already reads the path conditionally, the ownership is assigned, and the scope rule is written. A sibling project has one: `notes-308.md:25` records that f1brainz has a 41-line `GLOSSARY.md` on disk, though unindexed in its README.

The conditional phrasing "if they exist" is doing real damage here. It means every agent has been correctly following an instruction to read a file that is not there, for as long as the doctrine has said so.

### 4.2 What goes in it

One term per row. Four columns, no more.

```markdown
| Term | Plain-English definition | Where it came from | Do not confuse with |
|---|---|---|---|
| arm | One group of runs in a before-and-after comparison. "PRE arm" is the runs captured before a change; "POST arm" is after. | Borrowed from clinical-trial design (epic #298, issue #299). | "harvest" — an arm is captured, a harvest is read back. |
| rhyme | Two or more episodes showing the same underlying pattern. Finding them is "rhyme-search". | `docs/EPISODE_STORE.md:372`. | "duplicate" — a rhyme is a shared shape, not the same event twice. |
| lease | The claim one agent holds on a worktree so no second agent writes into it. | epic #298, issues #357/#369. | "latitude" — a lease is exclusivity, latitude is permission. |
```

**Three scope rules, following the existing "shared terms only; no workflow state" ruling:**

1. **A term earns a row when it has been used in two separate runs** and is not a plain English word. One use is a coinage; two is dialect.
2. **The definition is written for someone who has not read the run that coined it.** No glossary entry may use another undefined coined term.
3. **No workflow state.** The glossary says what a lease is. It never says which lease is currently held.

### 4.3 How terms get in

**Three routes, in decreasing order of how much I trust them:**

- **The human hits a term and asks.** Highest-signal route. Tommy's confusion is the ground truth this whole excursion exists to serve. Any term he asks about is admitted, no debate.
- **The candidate census proposes it** (check PL003, §4.3). A term used often enough across artifacts and absent from the glossary gets proposed. This is accretion, not fiat, and matches the project's accrete-then-consolidate habit.
- **An agent coins a term and files it.** Weakest route, because the coiner is the worst judge of whether a term is obvious. Should require the two-runs rule before admission.

**Removal matters as much as admission.** A term whose mechanism was deleted should lose its row. Otherwise the glossary becomes the thing that keeps dead dialect alive.

---

## 5. PROPOSAL — three mechanical checks

Written in the idiom `scripts/grade_lint.py` already establishes: coded offense identifiers, WARN and FAIL tiers, per-file scoping. A candidate script name is `scripts/lint_report_language.py`. **I did not write it.**

Because this repo holds that "a check that cannot fail is indistinguishable from one that passed" (`CREW_CONTEXT.md:78`), each check below names how it goes red.

### PL001 — undefined glossary term (FAIL)

**The check runs off the glossary, not off a hand-maintained jargon list.** For every term in `docs/agents/GLOSSARY.md`, if it appears in a report under `.agent-work/`, its **first** occurrence must either link to the glossary or be followed within the same sentence by a parenthetical gloss. Later occurrences are unrestricted.

**Why this direction.** Detecting jargon in general needs judgment a linter does not have. Detecting whether a *known* term was introduced needs only string matching. It also creates the right incentive: the glossary is the only way a term becomes checkable, so growing the glossary is what makes the check bite.

**How it goes red:** delete the parenthetical from a report's first use of "arm" and the check must FAIL naming that file and line. Add a term to the glossary that appears unglossed in an existing report and the check must FAIL without any report being edited.

**Known limitation, stated up front:** this check cannot see a coined term that is not yet in the glossary. It enforces introduction, never coverage. PL003 is what grows coverage.

### PL002 — sentence length (WARN at 26, FAIL at 36)

**Unit: words per sentence, counted over prose only** — excluding fenced code, inline code, table rows, headings, and blockquotes, and splitting list items apart.

**Thresholds have a measured basis, not a taste basis.** Current medians are 12 to 15 words and current means are 13 to 18. STE's descriptive cap is 25. A WARN at 26 sits just above both the standard and current practice, so it fires on genuine outliers. A FAIL at 36 catches only what is already indefensible: 6 sentences in `EPIC_SUMMARY.md` and roughly 33 in `exc-1` exceed 25 words today.

**How it goes red:** concatenate two sentences in any report and the count must cross. Run it against `exc-1-epic298-RESULT.md` unmodified and it must already report offenders — if it reports clean on that file, the parser is broken.

**I rate this the least valuable of the three** and include it because it is nearly free and because it will keep the tail from growing. **Do not let it become the standard.** The measurement in §2.1 says length is not this project's problem.

### PL003 — candidate coinage census (WARN, report-only)

Not a gate. A periodic report, run the way `curate_corpus.py` is run. It counts tokens across `.agent-work/` artifacts that are (a) absent from an ordinary English word list, or hyphenated compounds, (b) absent from `docs/agents/GLOSSARY.md`, and (c) present in **two or more separate run directories**. It prints them ranked by frequency as glossary candidates.

**This is the mechanism that grows the glossary without anyone deciding by hand what counts as jargon.** The two-run rule is what stops it from proposing every one-off phrase.

**How it goes red:** it cannot fail, by design — which is why it must never be a gate. Its correctness test is different: seed a known coined term into two run directories and confirm it appears in the output ranked appropriately; add it to the glossary and confirm it drops out.

### Rejected as a check: noun clusters

STE caps noun strings at three. This repo violates it constantly — "reviewer-handoff template graduations", "measured-arm playbook", "map-input contract entrypoint". I am not proposing it as a check because English noun-cluster detection needs part-of-speech tagging, which brings a dependency and a false-positive rate that a repo this size should not take on for a style rule. **Worth listing in the written rules as guidance; not worth mechanizing.**

---

## 6. WHAT I WOULD DO FIRST, AND THE ONE THING WORTH TESTING

**Cheapest useful move, in order:**

1. **Write `docs/agents/GLOSSARY.md` with the 21 terms counted in §2.2.** Doctrine already points at it from four places and the Charter skill already owns the imperative. This is the only step that needs no new code and closes a real, measured gap.
2. **Adopt rules 4, 8, and 9** as report-writing guidance. They address the three patterns the audit actually found.
3. **Build PL001 only.** It runs off the glossary from step 1 and needs no judgment.
4. **Leave PL002 and PL003 until PL001 has fired on a real report.**

**The one thing worth testing before believing the premise.** The brief says jargon is "suspected of confusing agents talking to each other." I found no evidence for or against that, and I would not build a standard on it untested. The cheap test: take one existing artifact, hand a fresh agent the version with the glossary and the version without, ask both the same three factual questions about its content, and compare. **This project already knows how to run a before-and-after comparison, and it already knows the failure mode** — an identically-instrumented pair can produce a result that means nothing (issue #331). Whoever runs it should read #331 first.

---

## 7. SOURCES

**Primary and near-primary:**
- [ASD-STE100 home](https://www.asd-ste100.org/) and [About STE](https://www.asd-ste100.org/about_STE.html) — 53 rules, 9 sections, ~900 approved words, technical nouns and verbs
- [ASD-STE100 FAQ](https://www.asd-ste100.org/STE_faq.html) — two-part structure, free distribution, company-glossary provision, position on automated checkers
- [ASD Europe: Simplified Technical English](https://www.asd-europe.org/standards-specifications/simplified-technical-english/) — governance, STEMG
- [ISO 24495-1:2023](https://www.iso.org/standard/78907.html) — scope, four principles, applicability to controlled languages
- [Plain Language Association International](https://plainlanguage.com/plain-language/iso-plain-language-standard/) — the 2014 IPLF definition
- [digital.gov plain language guide](https://digital.gov/guides/plain-language) — Plain Writing Act of 2010
- [Kuhn, *A Survey and Classification of Controlled Natural Languages*](https://attempto.ifi.uzh.ch/site/pubs/papers/kuhn2014cl.pdf) — the CNL design space
- [Attempto Controlled English](https://en.wikipedia.org/wiki/Attempto_Controlled_English)

**Secondary, used for specific rule text I could not obtain from the standard:**
- [Wikipedia: Simplified Technical English](https://en.wikipedia.org/wiki/Simplified_Technical_English) — sentence and paragraph limits, verb restrictions, history
- [ClickHelp: STE Rules and Examples](https://clickhelp.com/clickhelp-technical-writing-blog/what-is-simplified-technical-english/) — noun clusters, voice, rewrite examples
- [TechScribe: ASD-STE100](https://www.techscribe.co.uk/techw/asd-simplified-technical-english.htm) — listed; the host refused connection during this run
- [WordRake: Complying with Federal Plain Language Guidelines](https://www.wordrake.com/resources/federal-plain-language-guidelines) — jargon, abbreviations, sentence length
- [danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill) — an existing repurposing of STE for agent-facing English; paraphrases rule categories and explicitly does not reproduce the approved dictionary
- [Measuring the Translatability of Simplified English in Procedural Documents](https://www.researchgate.net/publication/3229950_Measuring_the_Translatability_of_Simplified_English_in_Procedural_Documents) — the sentence-versus-document-level caveat

**In-repo evidence:** `.agent-work/epic-298/EPIC_SUMMARY.md`; `.agent-work/explore-post-phase1/evidence/exc-1-epic298-RESULT.md`; `.agent-work/explore-post-phase1/evidence/exc-4-issues-RESULT.md`; `docs/agents/CREW_CONTEXT.md`; `docs/agents/ORCHESTRATOR_CONTEXT.md`; `docs/CONSTELLATION_OVERVIEW.md:38`; `skills/_shared/global-{everyone,orchestrator,crew}.md:6`; `.agent-work/20260728-charter-refresh/charter.json:233`; `scripts/grade_lint.py:1-45`; `notes-308.md:25`; GitHub issue #331.
