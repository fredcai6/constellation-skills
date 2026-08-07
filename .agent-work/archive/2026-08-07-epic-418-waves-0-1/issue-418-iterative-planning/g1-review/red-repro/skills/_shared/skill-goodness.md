# Skill-goodness criteria (shared reference)

The single standard for what makes a constellation skill *good*. **Two skills consume this one file:** `write-a-skill` reads it while **authoring** a new skill; `curator` reads it while **maintaining** the corpus. Authoring and maintaining hold the *same* criteria — a skill is not judged by one bar when written and a different bar when kept. Keep this the one home for the standard; wire new consumers to it rather than restating it.

Remixed native from the capability of Matt Pocock's `writing-great-skills` (the ideas, not its wording).

## Contents

- [Root virtue: predictability](#root-virtue-predictability)
- [The mechanical subset — already a machine check](#the-mechanical-subset--already-a-machine-check)
- [The semantic subset — reviewer-judged](#the-semantic-subset--reviewer-judged)
- [How the two consumers use this](#how-the-two-consumers-use-this)

## Root virtue: predictability

**A good skill makes the agent do the same thing every run.** Predictability = same process every run — that is the whole point of a skill and the property every criterion below serves. This is native to constellation: a rail is a hard check the run takes *every* time, and a skill is good when it turns a judgement an agent would otherwise improvise into a repeatable procedure. When a criterion is unclear, ask: *does this make the next run more predictable, or less?*

## The mechanical subset — already a machine check

These properties are **mechanically decidable and already measured** by `scripts/curate_corpus.py`. Do NOT re-implement them and do NOT re-judge them by eye — run the script and read its rows. It measures, per skill:

- **Size / sprawl** — a skill that has grown into a manual should split or move detail to `references/`.
- **Description discipline** — length budget, third-person register, a **when-to-use** trigger marker, and (for confusable-pair skills) an **exclusion clause**.
- **Invoker tag** — the `invoker:` frontmatter declares who invokes the skill.
- **Reference TOCs** — a long `references/*.md` carries a `## Contents` anchor.
- **Duplication signatures** — the same doctrine sentence copied across skills is drift; consolidate to `_shared/`.

`curate_corpus.py` **flags, never gates** (it always exits 0). For authoring, the `write-a-skill` rail (`verify_skill_registered.py`) turns the mechanical subset into a mint-time refusal for the *broken* cases (unparseable, no when-to-use marker, missing exclusion on a confusable skill, missing invoker) plus the one property the corpus tool cannot see — **install-bundle registration** (below). Soft budgets (size, description length, TOC, duplication) stay advisory rows, not mint gates.

### The one thing the corpus tool cannot see: registration

A skill's directory is auto-discovered, but the scripts and shared doctrine it needs are wired **only** by its entries in `install_constellation.py` (`SKILL_SCRIPT_BUNDLES`, `SKILL_REFERENCE_BUNDLES`). An unregistered skill installs as a **dead seam** — no doctrine, no rail script — while looking fine on disk. This is the failure mode the mint rail exists to catch: registration is part of goodness, not an afterthought.

## The semantic subset — reviewer-judged

These are **judgement calls an independent fresh-context reviewer makes** — never a machine gate, never the author's self-grade. The reviewer holds them as a checklist:

- **Completion-criteria sharpness** — "done" is a checkable state, not a vibe. Could two agents disagree on whether the skill finished?
- **The no-op test** — strip a sentence: if the run would go identically without it, it is sediment, cut it.
- **Leading words** — the skill opens by telling the agent what to *do*, not by narrating background.
- **Negation / negative space** — it says what NOT to do and where it does NOT apply, not only the happy path.
- **Split justification** — if it does two jobs, there is a stated reason they live together rather than as two skills.
- **Sediment** — accreted caveats, dead cross-references, and hedges that no longer earn their place get removed.

The reviewer, not the author or the script, decides whether the skill is *good* here. A defended exception to the mechanical rail also needs the reviewer's co-sign plus a log entry — self-assertion never passes.

## How the two consumers use this

- **`write-a-skill` (author):** classify → scaffold → draft against these criteria, then hand the draft to an independent reviewer who checks the semantic subset. The mint rail enforces the mechanical/registration subset.
- **`curator` (maintain):** measure with `curate_corpus.py` (the mechanical subset), mend mechanical drift in place, and route semantic-subset decisions to Triage rather than silently redesigning.

Same criteria, two lifecycle moments. When the parked charter⊕curator canonization (#9) lands, it reuses this same reference — no second copy.
