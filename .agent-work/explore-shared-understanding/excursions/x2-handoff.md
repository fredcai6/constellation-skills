# Excursion X2 — Research handoff: the agent-skill teaching/explaining ecosystem

**One named question:** What existing agent skills / tools have the goal of *teaching a user concepts* or *explaining code & changes to a human* — and what concrete mechanisms do they use that transfer to our setting (agents writing to one expert-but-learning architect)?

**Type:** research (web + any locally findable skill source; cite everything).

**Scope — cover these, ONLY these:**
1. **Matt Pocock's `/teach` and `/grill-me`** — go past the blog: find the actual skill *structure* if public (GitHub, aihero repos, gists) — the SKILL.md, the prompts, the "learning record" file format. If not public, say so precisely (scoped null). We already have his blog's high-level description; this excursion wants the *mechanism/structure*.
2. **"explain-diff" / change-explaining tools** — anything (skills, GitHub Actions, IDE features, `gh` tools, PR-summarizers) whose job is explaining what a code change does to a human. What do they extract, at what level, and how do they decide depth?
3. **Broader skill ecosystems** — superpowers, Claude plugin marketplaces, Cursor/Copilot "explain", community "tutor"/"onboarding"/"codebase explainer" skills. 3–5 concrete examples with their mechanism.
4. For each: **what transfers** to a per-user, in-flow, expert-audience teaching setting, and **what does NOT** (scoped — say what you evaluated and did NOT).

**What "answered" looks like:** ~1 page, cited, that lets a designer say "these 3 mechanisms are worth stealing, these are a mismatch, and here's the closest existing thing to what we want."

**Budget / stop:** ~15 min; 5–8 solid sources. Report what exists; do NOT design our solution. Scoped-nulls doctrine on every "not transferable."

**Result artifact (write here):** `.agent-work/explore-shared-understanding/excursions/x2-skill-ecosystem.md`
