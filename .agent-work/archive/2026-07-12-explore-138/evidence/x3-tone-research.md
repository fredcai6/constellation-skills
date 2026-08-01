# x3 — What form of emphasis actually makes an LLM agent comply?

**Question:** which *form of emphasis* most reliably gets an agent to follow process
instructions — all-caps/exclamatory, flat imperative, consequence/mechanism naming, emotional
appeal, repetition, positional placement, or markup?

**One-line answer:** the measured evidence backs **positional placement (put the exact instruction
at the decision point) + flat, unambiguous imperative wording**, optionally reinforced by naming the
reason. All-caps / exclamatory shouting is *widely practiced but unsupported* by any controlled
measurement, and on small models it is a plausible *net risk* because small models are the most
sensitive to superficial formatting. Our own field data (4 flat-imperative clauses at the decision
point, 1/3 → 3/3) is consistent with the literature.

---

## 1. Inventory of emphasis mechanisms, with measured effects

Effect claims are tagged with **model class / year** because 2023-era effects frequently do not
transfer.

### A. Positional placement — STRONGEST measured support
- **Lost-in-the-middle** (Liu et al.): instructions/facts in the *middle* of context are
  underweighted; start and end dominate. Primacy + recency. Effect strongest when input fills up to
  ~50% of context. (frontier + open models, 2023–2025; robust, replicated.)
- **OpenAI GPT-4.1 guide** (2025, practitioner/vendor): place instructions at **both the beginning
  and end** of long context; if only once, above beats below. On **conflicting instructions, the
  model follows the one closer to the end** ("last instruction wins").
- **Our field data** matches: the win came from putting rule + next move *at the decision point*,
  not from louder wording.
- Verdict: **placement is the highest-leverage, best-evidenced lever.**

### B. Format / punctuation / capitalization sensitivity — measured, and it cuts AGAINST caps
- **"When Punctuation Matters"** (Seleznyov et al., 2024; 52 Natural-Instructions tasks; 8 models
  across Llama/Qwen/Gemma): format changes *alone* cause **8–10 accuracy-point swings**;
  **frontier models are substantially more robust; small open models are the most sensitive**;
  greedy decoding is less robust, especially for small models.
- Practitioner/learnprompting synthesis: ALL CAPS / multiple "!" / "rewards" **rarely improve and
  can be counterproductive**; capitalization mostly changes **output format**, not instruction
  adherence.
- Verdict: emphasis-by-typography is an *uncontrolled* variable that small models react to
  unpredictably. It is not a reliable compliance lever; it is a source of variance.

### C. Emotional appeal (EmotionPrompt) — measured, but 2023-era and fragile
- **EmotionPrompt** (Li et al., 2307.11760, 2023): appending stimuli like *"This is very important
  to my career"*: **+8% relative on Instruction Induction, +115% on BIG-Bench** (small/hard tasks),
  **+10.9% avg** on generative tasks (human study). Models: Flan-T5-Large, Vicuna, BLOOM, Llama 2,
  ChatGPT, GPT-4.
- Caveats: effects are **2023-model** results; successor work reports emotional framing also
  **increases sycophancy** and is inconsistent on newer models. The paper does **not** isolate
  small-vs-large differential.
- Verdict: real historically, but not a dependable 2025-agent lever; the mechanism ("name why it
  matters") survives better than the emotional wrapper.

### D. Politeness / tone — measured, small, inconsistent, direction REVERSES across generations
- **"Mind Your Tone"** (Dobariya & Kumar, 2510.04950, Oct 2025, GPT-4o): **rude beat polite**,
  84.8% (Very Rude) vs 80.8% (Very Polite) — a 4-pt spread *opposite* to earlier findings.
- **PLUM corpus** (cross-lingual, multi-model, 2606): polite lifts avg quality up to ~11%, impolite
  hurts, but **not consistent across languages/models**; **Llama most tone-sensitive (11.5% range),
  GPT most robust**.
- Verdict: tone is a small, model- and language-dependent effect whose *sign flips* between model
  generations. Do not build compliance on tone.

### E. Markup (XML tags / headers / bold) — vendor-measured for structure, not for "loudness"
- **Anthropic**: Claude is fine-tuned to attend to **XML tags**; use them to *separate* instructions
  from data/examples. Improves consistency and adherence. (Claude 3–4 class, current.)
- **OpenAI GPT-5.2 guide**: emphasis is carried by **word choice ("MUST" vs "should") and semantic
  grouping, not typographic excess**; favors structure over capitalization.
- Verdict: markup helps by *disambiguating boundaries*, not by shouting. Good for separation; not the
  emphasis mechanism per se.

### F. Repetition — vendor practice, modest
- GPT-4.1 guide: repeating the instruction at top **and** bottom of a long prompt beats once.
  Marginal, and mostly a positional effect (see A). Not independently well-measured.

### G. Consequence/mechanism naming — best-supported *wording* technique
- **Anthropic "be clear and direct"**: state exactly what you mean, *what success looks like*, and
  *what the output is for*; use numbered steps so nothing is skipped.
- Overlaps EmotionPrompt's durable core ("why this matters"). This is the wording analog of good
  placement: reduce ambiguity, name the stakes plainly — no capitals required.

---

## 2. Widely PRACTICED vs measured EFFECTIVE (kept explicit)

| Mechanism | Practiced? | Measured effective? |
|---|---|---|
| Positional placement (decision point / end) | yes | **yes — strong, replicated** |
| Flat imperative + unambiguous next move | some | **yes — indirectly (clarity, our field data)** |
| Consequence/mechanism naming ("why") | some | partial (Anthropic clarity; EmotionPrompt core) |
| XML/markup for separation | yes (Anthropic-driven) | yes, for consistency/boundaries |
| ALL CAPS / "EXTREMELY IMPORTANT" / "NEVER" / "YOU MUST" | **heavily** (Cursor, competitor skill frameworks) | **no controlled evidence; likely net-neutral-to-negative on small models** |
| Emotional appeal | some | 2023 yes; fragile now, adds sycophancy |
| Politeness/rudeness tone | folk practice | small, inconsistent, sign-flipping |
| Repetition | yes | marginal (mostly positional) |

**The competitor all-caps style is DATA about practice, not evidence of effect.** No study located
shows all-caps banners beating flat imperative on process compliance. Their prevalence is best
explained by copying and by cheap salience-for-humans, not by measured model gains.

## 3. Small / cheap model specifics (most relevant to sonnet-class rails)

- Small models are the **most format-sensitive** (8–10 pt swings from formatting alone; frontier
  models robust) — so typographic emphasis is *higher-variance*, not higher-mean, on exactly the
  models our rails target.
- Small models are **less robust under greedy decoding** — one more reason to remove ambiguity via
  placement/wording rather than add salience via capitals.
- Tone sensitivity is largest on **smaller/open models (Llama 11.5%)** and its *sign is unreliable*
  — a reason to avoid tone-as-lever precisely where we'd be tempted to use it.
- Net: for cheap models, the reliable knobs are **unambiguous wording + right position**; the
  unreliable ones are **caps, tone, emotion**.

## 4. Ranked recommendation for the rail-string tone

1. **Flat imperative stating the exact next move, placed at the decision point** (what we already
   found). Best-evidenced. Keep it.
2. **Name the rule's mechanism/consequence in one plain clause** ("...or the workflow will be marked
   abandoned"), no capitals. Cheap, weak-positive, aligns with Anthropic clarity + EmotionPrompt core.
3. **Use lightweight structural separation** (a leading marker / tag) so the rail is unambiguously an
   instruction, not narration — this is where markup earns its keep on small models.
4. **Repeat only across a genuine gap** (rail re-appended at each decision point already gives this).
5. **Drop all-caps / exclamatory / "YOU MUST NEVER" styling.** Unsupported, and a variance risk on
   sonnet-class models. Removing the old banners with no measured loss was the correct call.

### Falsifiable prediction for our sonnet eval
> Rewriting the current 4 flat-imperative rail clauses into an ALL-CAPS / "YOU MUST … NEVER …"
> variant will **not** raise sonnet-class compliance above the flat-imperative baseline (currently
> 3/3), and will show **equal-or-higher run-to-run variance**. Meanwhile, **moving** the rail from
> top-of-prompt to the decision point will move compliance more than any wording/caps change.
> Concretely: caps variant ≤ baseline compliance and ≥ baseline variance; position beats typography.
> If the caps variant reliably beats flat-imperative on ≥2 tasks with lower variance, this
> recommendation is falsified.

## 5. Scoped nulls — what was NOT found / NOT covered

- **No controlled head-to-head** of "exclamatory/all-caps" vs "flat imperative" on *agentic
  multi-step process compliance* specifically. All emphasis studies located measure **single-turn QA
  accuracy**, not workflow-adherence — the transfer to our setting is an inference, not a measurement.
- **No Claude-cheap-model (sonnet-class) published emphasis study** located; small-model evidence is
  from Llama/Qwen/Gemma/Flan-T5/Vicuna.
- **No 2025-frontier replication of EmotionPrompt on agentic compliance** located.
- **Consequence-naming was not isolated** from emotional framing in any controlled study; its support
  is indirect (Anthropic guidance + EmotionPrompt's core).
- Repetition's effect could not be cleanly separated from positional (start+end) effects.
- Politeness numbers come from small single-model or cross-lingual QA studies; none tested workflow
  abandonment.

---

### Sources
- EmotionPrompt — Li et al., arXiv 2307.11760 (2023). https://arxiv.org/abs/2307.11760
- Mind Your Tone (politeness, GPT-4o, 2025) — arXiv 2510.04950. https://arxiv.org/abs/2510.04950
- PLUM cross-lingual politeness corpus — arXiv 2604.16275. https://arxiv.org/pdf/2604.16275
- When Punctuation Matters (format robustness, 8 models, 2024) — arXiv 2508.11383. https://arxiv.org/html/2508.11383v1
- Lost in the Middle / position bias — see arXiv 2510.10276 and summaries; Liu et al. original.
- OpenAI GPT-4.1 prompting guide (placement, conflicts). https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide
- OpenAI GPT-5.2 prompting guide (word-choice over typography). https://developers.openai.com/cookbook/examples/gpt-5/gpt-5-2_prompting_guide
- Anthropic prompting best practices (clarity, XML tags). https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- learnprompting — format/labels (caps rarely helps). https://learnprompting.org/docs/intermediate/whats_in_a_prompt
