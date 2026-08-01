# x3 research excursion — what emphasis/tone actually works on LLM agents?

## The one named question

What does published research and credible practitioner evidence say about which *form of emphasis*
most effectively gets an LLM agent to comply with process instructions: exclamatory/all-caps shouting,
flat imperative statements, naming consequences/mechanisms, emotional appeals, repetition, structural
placement (position in context), or markup (XML tags, headers, bold)?

Context (do not re-derive): we are choosing the tone for short "rail" strings a workflow engine appends
to its responses to keep cheap models (sonnet-class) from abandoning/faking a multi-step workflow. Our
own field data: four flat-imperative clauses (rule + the exact next move, placed at the decision point)
took compliance from ~1/3 to 3/3; prior all-caps banners were removed without measured loss. Popular
competitor skill frameworks and Cursor's system prompts lean heavily exclamatory (EXTREMELY IMPORTANT,
NEVER, YOU MUST). The open question is whether that style is load-bearing or cargo cult.

## Type

Research. Primary sources REQUIRED: peer-reviewed or arXiv papers (e.g. work on prompt emphasis,
EmotionPrompt-style emotional stimuli, politeness/tone effects, instruction-position/recency effects,
prompt sensitivity), official vendor prompting guidance (Anthropic, OpenAI docs), and credible
practitioner writeups (leaked/published production system prompts count as evidence of practice, not
of effectiveness — distinguish the two!). Cite everything; contradictions surfaced, not smoothed.

## What "answered" looks like

A findings doc that:
1. Inventories the emphasis mechanisms found in the literature with measured effect sizes where they
   exist (which benchmark, which model class, which year — effects on old models may not transfer).
2. Distinguishes "widely practiced" from "measured effective" explicitly.
3. States what is known about SMALL/cheap models specifically vs frontier models.
4. Ends with a ranked recommendation for our rail-string tone + a falsifiable prediction we could test
   with our own eval harness (e.g. "flat-imperative+next-move will beat all-caps on sonnet by X").
5. States what was NOT found / NOT covered (scoped nulls).

## Budget / stop conditions

- ≤25 minutes; partial findings over overrun.
- Web research only; no repo changes.
- Do not import competitor doctrine as authority — their prompts are DATA about practice, never a
  design source to copy.

## Result path (write the findings doc here)

`C:/Programs/constellation-skills/.agent-work/explore-138/evidence/x3-tone-research.md`
