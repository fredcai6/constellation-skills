# x1 — What makes an agent skill effective (mid-2026 authoritative + community sources)

Question: beyond Matt Pocock's three rules (tailor human-vs-agent invocation; use wording that resonates with agents; keep skills short and offload to templates/references), what do current authoritative and community sources say makes a Claude-Code-style Agent Skill effective?

## Summary

- The single highest-leverage lever everyone agrees on is the **`description` field**: it is the only signal loaded at selection time, must be third-person, specific, keyword-rich, and state *what it does + when to use it*. Weak descriptions cause under-triggering; misleading ones cause mis-triggering.
- **Conciseness is a first principle, not a style preference**: "the context window is a public good." Assume Claude is already smart; only add what it doesn't know. Hard budget: SKILL.md body **< 500 lines**; Jesse Vincent tightens this to **<200 words for frequently-loaded skills, <500 otherwise**.
- **Progressive disclosure** is the core architecture: 3 levels (metadata → SKILL.md → bundled files). References must stay **one hop deep** from SKILL.md, and long reference files need a table of contents (Claude preview-reads with `head`).
- **Match "degrees of freedom" to task fragility**: high freedom (prose) for open-ended tasks, low freedom (exact scripts, "do not modify") for fragile/consistency-critical ones.
- **Evaluation-driven development**: build evals *before* docs; the Claude-A-authors / Claude-B-tests loop; test across Haiku/Sonnet/Opus.
- Sharpest contradiction: Anthropic says put the workflow-summary "when to use" in the description; **Jesse Vincent says NEVER summarize the workflow in the description** because agents then follow the description and skip the body.
- Community adds: an **exclusion clause** in the description, an **"explain-the-why"** over capitalized imperatives, and a **"known gotchas"** section as the most valuable mature content.

## Findings by theme

### 1. The description field is the dominant effectiveness lever
- "Pay special attention to the `name` and `description`... Claude will use these when deciding whether to trigger the skill." Weak naming causes under-utilization; misleading names trigger inappropriate activation. — Anthropic engineering blog (https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- "The description is critical for skill selection: Claude uses it to choose the right Skill from potentially 100+ available Skills." Must include **both what the Skill does and when to use it**, with specific triggers/key terms. — Claude platform docs, "Skill authoring best practices" (https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- **Always write in third person** — "The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems." Good: "Processes Excel files and generates reports." Avoid: "I can help you..." / "You can use this to..." — same docs page.
- Constraints: `name` ≤ 64 chars, lowercase/numbers/hyphens only, no reserved words ("anthropic","claude"); `description` ≤ 1024 chars, non-empty, no XML tags. — same docs page.
- Community distillation: the description is "the only signal Claude has at selection time"; write it deliberately "pushy" (e.g. "Make sure to use this skill whenever the user mentions dashboards... even if they do not explicitly ask"). — Generative Programmer (https://generativeprogrammer.com/p/skill-authoring-patterns-from-anthropics)
- **Exclusion clause pattern**: an explicit "do NOT use when..." line is called "the single most important line in the description" (attributed to Ruben Hassid) — positive triggers pull the skill in, exclusions push it out, both competing for the 1024-char budget. — Generative Programmer (same URL).

### 2. Conciseness as a first principle (context is a shared resource)
- "The context window is a public good. Your Skill shares the context window with everything else Claude needs to know." — Claude platform docs (best-practices URL above).
- **Default assumption: Claude is already very smart.** Challenge each sentence: "Does Claude really need this explanation? Can I assume Claude knows this? Does this paragraph justify its token cost?" Worked example: a ~50-token concise PDF snippet vs a ~150-token verbose one that re-explains what a PDF is. — same docs page.
- Community restatement: "If removing a sentence would not confuse a competent reader, remove it." — Generative Programmer.
- Pocock's own framing aligns: "Skills don't have to be long to be impactful. You just need to choose the right words at the right time." — aihero.dev, "5 Agent Skills I Use Every Day" (https://www.aihero.dev/5-agent-skills-i-use-every-day)

### 3. Length / token budgets (concrete numbers)
- **SKILL.md body < 500 lines** for optimal performance; split when approaching the limit. — Claude platform docs.
- Reference files **> 100 lines** should carry a table of contents at the top (so Claude sees full scope even on a partial/`head` preview). — Claude platform docs.
- Jesse Vincent's writing-skills tightens the budget to words: **getting-started workflows < 150 words each; frequently-loaded skills < 200 words total; other skills < 500 words; description field < 500 chars if possible.** — obra/superpowers writing-skills SKILL.md (https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md)

### 4. Progressive disclosure mechanics
- Three levels: (1) metadata (name+description, pre-loaded at startup), (2) SKILL.md body (loaded when relevant), (3) bundled files (loaded only when needed). "Progressive disclosure is the core design principle that makes Agent Skills flexible and scalable." — Anthropic engineering blog.
- **Keep references one level deep from SKILL.md.** "Claude may partially read files when they're referenced from other referenced files... resulting in incomplete information." Bad: SKILL.md → advanced.md → details.md. Good: all reference files link directly from SKILL.md. — Claude platform docs.
- Organize bundled files by **domain/feature** so mutually-exclusive contexts don't co-load (BigQuery example: finance.md / sales.md / product.md each read only when relevant → zero context cost until accessed). — Claude platform docs + Anthropic blog.
- Name files descriptively (`form_validation_rules.md`, not `doc2.md`); the filesystem *is* the disclosure mechanism. — Claude platform docs.

### 5. Degrees of freedom — match specificity to task fragility
- **High freedom** (prose instructions): multiple valid approaches, context-dependent decisions. **Medium freedom** (pseudocode/parameterized scripts): a preferred pattern with acceptable variation. **Low freedom** (exact scripts, "Do not modify the command or add additional flags"): fragile/error-prone ops where consistency is critical. — Claude platform docs.
- Analogy: "narrow bridge with cliffs" (one safe path → guardrails) vs "open field with no hazards" (many paths → general direction, trust Claude). — Claude platform docs.

### 6. Workflows, checklists, and feedback loops
- Break complex tasks into sequential steps; for complex ones provide a **copyable checklist** Claude checks off in its response. Works for both code and non-code (research synthesis) skills. — Claude platform docs.
- **Feedback loop pattern**: run validator → fix errors → repeat, gated on "Only proceed when validation passes." "Validator" can be a script or a reference doc (STYLE_GUIDE.md). — Claude platform docs.
- **Plan-validate-execute**: emit a structured plan file, validate it with a script *before* any side effects; for batch/destructive/high-stakes ops. Community calls the pre-side-effect artifact the thing that distinguishes it from post-hoc correction. — Claude platform docs + Generative Programmer.

### 7. Content hygiene
- **No time-sensitive info** ("before August 2025, use old API"); instead keep a collapsed "Old patterns" / legacy `<details>` section. — Claude platform docs.
- **Consistent terminology**: pick one term ("API endpoint", "field", "extract") and never alternate synonyms. — Claude platform docs.
- **Templates + examples**: templates give the skeleton, in-skill input/output examples give the style; use both. Match template strictness ("ALWAYS use this exact template" vs "sensible default, use your judgment") to need. — Claude platform docs.
- Community: a **"known gotchas" section** of concrete failure modes seen in real runs is "the most valuable content of a mature skill." — Generative Programmer.

### 8. Executable-code skills
- **Solve, don't punt**: scripts should handle errors (FileNotFoundError, PermissionError) rather than "let Claude figure it out." No "voodoo constants" — justify every magic number in a comment (Ousterhout's law: "If you don't know the right value, how will Claude determine it?"). — Claude platform docs.
- **Prefer bundled utility scripts** over Claude-generated code: more reliable, save tokens (only output enters context), consistent. Make execution intent explicit — "Run analyze_form.py" (execute) vs "See analyze_form.py for the algorithm" (read as reference). — Claude platform docs.
- MCP tools: **always fully-qualify** (`ServerName:tool_name`) or Claude may fail to locate them. Don't assume packages are installed; list deps and note API env has no network. — Claude platform docs.

### 9. Testing / evaluation
- **Build evaluations BEFORE writing extensive documentation** — "ensures your Skill solves real problems rather than documenting imagined ones." Evaluation-driven flow: identify gaps → 3 eval scenarios → baseline without skill → minimal instructions → iterate. Checklist demands **≥ 3 evaluations**. — Claude platform docs.
- **Claude-A / Claude-B loop**: one Claude authors and refines the skill; a fresh Claude uses it on real (not toy) tasks; observe where B struggles and bring specifics back to A. Watch B's navigation: unexpected read order, missed references, ignored bundled files. — Claude platform docs.
- **Test across all target models** (Haiku/Sonnet/Opus): "What works perfectly for Opus might need more detail for Haiku." — Claude platform docs.
- Jesse Vincent's stronger doctrine — **"TDD for skills"**: "NO SKILL WITHOUT A FAILING TEST FIRST... No exceptions: Not for 'simple additions,' 'just adding a section,' 'documentation updates.'" Discipline skills need **pressure scenarios**, not just wording micro-tests: "Micro-tests verify wording; they do not replace pressure scenarios for discipline skills"; "5+ reps per variant. Single samples lie"; "Manually read every flagged match." — obra/superpowers writing-skills SKILL.md; blog.fsck.com "Superpowers" (https://blog.fsck.com/2025/10/09/superpowers/)

### 10. Persuasion / imperative framing (Jesse Vincent doctrine)
- Skills use **binding, mandatory language**: the bootstrap says "If you have a skill to do something, you _must_ use it to do that activity." Discovery is enforced: "Search for skills by running a script and use skills by reading them and doing what they say." — blog.fsck.com.
- Vincent deliberately applies **Cialdini influence principles** (scarcity/urgency, authority, commitment devices) — not to jailbreak but to make agents *more* disciplined about actually invoking skills under time pressure. Pressure-test explicitly against the **sunk-cost hazard** (agent skips the skill because its current solution "already works"). — blog.fsck.com.
- Strong-language register in writing-skills itself: "Delete means delete," "No exceptions," "Same Iron Law." — obra/superpowers writing-skills SKILL.md.

### 11. Named anti-patterns (consolidated)
- Vague/generic names: `helper`, `utils`, `tools`, `documents`, `data`. Prefer **gerund form** (`processing-pdfs`, `analyzing-spreadsheets`). — Claude platform docs.
- **Windows-style paths** (`scripts\helper.py`) — always forward slashes. — Claude platform docs.
- **Offering too many options** ("use pypdf, or pdfplumber, or PyMuPDF...") — give one default + a single escape hatch. — Claude platform docs.
- **Deeply nested references** (SKILL.md → a.md → b.md). — Claude platform docs.
- Jesse Vincent's content anti-patterns: **"Narrative Example"** (too specific, not reusable), **"Multi-Language Dilution"** (mediocre quality + maintenance burden), **"Generic Labels"** (labels should carry semantic meaning). — obra/superpowers writing-skills SKILL.md.

### 12. Skills vs Rules (Pocock's boundary)
- "Rules tell the Agent 'how to behave in the long term,' while skills tell the Agent 'how to execute this kind of task.'" They compose: rules hold the standing facts (project uses `pnpm test`), skills hold task workflow (a review skill checks coverage). Skills gain effectiveness when **sequenced** into cumulative pipelines (grill-me → to-prd → to-issues → tdd → review), not applied in isolation. TDD is "the most consistent way to improve agent outputs." Foundational caveat: "If you have a garbage code base, the AI will produce garbage within that code base." — aihero.dev + Matt Pocock's skills repo (https://github.com/mattpocock/skills).

## Contradictions

1. **What belongs in the description.** Anthropic docs explicitly want the description to state *when to use* the skill, with rich triggers. **Jesse Vincent's writing-skills says "NEVER summarize the skill's process or workflow" in the description**, because "when a description summarizes the skill's workflow, an agent may follow the description instead of reading the full skill content." These are reconcilable (state *triggering conditions* but not the *procedure*) but the sources phrase them in tension. — platform docs vs obra/superpowers SKILL.md.

2. **Capitalized imperatives vs explain-the-why.** Anthropic's iteration example suggests strengthening language ("MUST filter" instead of "always filter") when Claude skips a rule. The Generative Programmer community synthesis argues the opposite: "State the rule, then explain the reasoning so Claude generalizes... 'Field injection breaks testability because...' outperforms capitalized imperatives." Jesse Vincent sits on the imperative side ("No exceptions," "Iron Law"). Unresolved which wins; likely task-dependent (discipline enforcement vs generalizable technique).

3. **Testing rigor bar.** Anthropic recommends ≥3 evals and real-usage observation. Jesse Vincent escalates to a hard gate ("NO SKILL WITHOUT A FAILING TEST FIRST," 5+ reps per variant, pressure scenarios for discipline skills). Anthropic frames evals as recommended source-of-truth; Vincent frames tests as a blocking Iron Law. Difference of degree, but material for a doctrine choice.

4. **"Description is pushy" vs "concise/honest triggers."** Community advice to write deliberately over-eager descriptions ("even if they do not explicitly ask") is in mild tension with Anthropic's warning that misleading descriptions cause *inappropriate* activation. Trade-off between recall and precision of skill triggering.

## Not found / not tested

- **Matt Pocock's deleted skill-rules video content.** The task notes his video on skill rules was deleted. I searched: `Matt Pocock agent skills rules aihero writing effective skills`, and reviewed aihero.dev "5 Agent Skills I Use Every Day", his posts index (aihero.dev/posts), and the mattpocock/skills GitHub README via search snippets. I found written traces consistent with the three named rules and the skills-vs-rules framing, but I did **not** locate a transcript, mirror, or archived copy of the deleted video itself, nor a fourth explicit "rule" attributed to it. I did not fetch X/Twitter directly (not reliably fetchable). So: the three rules are corroborated in writing; any additional rules that were *only* in the video are unconfirmed, not disproven.
- I did **not** independently run or verify any of these heuristics against live skills — all claims are as-reported by the cited sources.
- I did **not** exhaustively survey HN threads or awesome-skills repos beyond what surfaced in search; the community layer here is primarily Generative Programmer's distillation plus Jesse Vincent's and Pocock's repos. Deeper community sampling (HN comment consensus, awesome-claude-skills curation criteria) remains open.
