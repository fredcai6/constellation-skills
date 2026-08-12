# Excursion X4 — Research handoff: how developer tools teach concepts in-flow

**One named question:** How do real developer tools and documentation practices teach concepts *in the flow of work* (not in a course) — and what patterns transfer to agents writing to one expert-but-learning architect?

**Type:** research (web + primary sources; cite everything).

**Scope — cover these, ONLY these:**
1. **Explanatory compiler/tooling errors** — Rust's `--explain E0499` / Elm's error messages / TypeScript's type-expansion: how they teach the concept behind an error at the moment it bites. What makes them land without condescending.
2. **The Diátaxis documentation framework** — its four modes (tutorial / how-to / reference / **explanation**). The "explanation" quadrant is essentially our build-milestone explainer (K9); capture what distinguishes good "explanation" docs from reference docs.
3. **Architecture Decision Records (ADRs) & literate programming** — decisions/code narrated with the *why*, as durable teaching artifacts. How they keep the "why" legible over time.
4. **"Explain this code / change" features** in IDEs & AI assistants (Copilot, Cursor, JetBrains) — how they pitch level and decide what's worth explaining.
5. **Progressive disclosure / glossaries-on-hover** in technical UIs — surfacing a definition only when wanted, without cluttering the expert's view (maps to our "gloss on first use" + register dial).

One paragraph each: mechanism + **what transfers vs. what does NOT** (scoped nulls).

**What "answered" looks like:** ~1 page, cited, giving a designer concrete in-flow teaching patterns worth borrowing (especially for K9 the milestone explainer and the first-use-gloss/dial), and which are a mismatch.

**Budget / stop:** ~15 min; 5–8 solid sources. Report what exists; do NOT design our solution.

**Result artifact (write here):** `.agent-work/explore-shared-understanding/excursions/x4-devtool-teaching.md`
