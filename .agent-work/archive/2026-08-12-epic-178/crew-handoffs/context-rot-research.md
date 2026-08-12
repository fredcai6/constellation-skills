# Context-rot research → Governor threshold calibration (2026-07-19)

Deep-research pass (105 agents, 22 sources, 25 claims verified 23-confirmed/2-refuted) to set the Context Governor's SOFT/HARD thresholds. Question: at what fill fraction does effective performance degrade, for 200K vs 1M windows, esp. for agentic work.

## Verified findings (all high-confidence, 3-0 unless noted)

1. **No safe fraction.** Degradation is continuous and non-uniform, present even on trivial tasks, across all 18 frontier models Chroma tested (Claude 4, GPT-4.1, Gemini 2.5, Qwen3). Not a cliff at a fixed fill %.
2. **Driven by ABSOLUTE token count, not window fraction.** NoLiMa held needle depth constant across window sizes → "the main limiting factor is the increased context length," not position. arXiv 2510.05381: "the sheer length of the input alone can hurt performance." Onset clusters ~32K (hard) → ~100K (easier), *independent of advertised window*.
3. **A 1M model is usable to a LOWER fraction than a 200K model** (counter-intuitive). RULER: effective length clusters ~32–64K regardless of claim (GPT-4 64K/128K = 50%; Yi-34B 32K/200K = 16%). So a 1M model's degradation band (~32–100K) is only ~3–10% of its window.
4. **Operational rollover (from practitioner replications):** 200K-window models "roll over by 80–100K"; 1M-window models "stop behaving like 1M models past ~200K." Effective ≈ 15–30% of a 1M window at best.
5. **Agentic/reasoning degrades EARLIEST — the load-bearing finding here.** arXiv 2510.05381: a large share of the problem-solving drop happens within **~7K tokens**, far below where retrieval fails (59% accuracy drop @7K while retrieval fell 8%). BABILong: models "effectively utilize only 10–20% of context." Two-hop reasoning collapses to 25.9% @32K.
6. **Messy real context degrades earlier than clean NIAH** — low needle-question similarity + semantically-similar distractors + real history all pull the curve in. NIAH overstates usable context.
7. **Lost-in-the-middle is real and persists on 1M models** (U-curve by position), though some frontier models flatten it at shorter lengths.

## Recommendation (research synthesis; medium confidence — engineering judgment, no study prescribes a handoff fraction)

Express thresholds as an **absolute-token cap**, not a pure fraction: `min(fraction, absolute)`. Shade DOWN for agentic work.
- SOFT ≈ min(0.5×window, ~80–100K tokens)
- HARD ≈ min(0.7×window, ~150K tokens)

### Proposed model-keyed `_THRESHOLDS` (fraction = cap / real window), agentic-shaded

| Model | Window | SOFT cap | HARD cap | → SOFT frac | → HARD frac |
|---|---|---|---|---|---|
| claude-opus-4-8 | 1M | ~80K | ~150K | **0.08** | **0.15** |
| claude-sonnet-5 | 1M | ~80K | ~150K | **0.08** | **0.15** |
| claude-fable-5 | 1M | ~80K | ~150K | **0.08** | **0.15** |
| claude-haiku-4-5-20251001 | 200K | ~90K | ~140K | **0.45** | **0.70** |
| DEFAULT (unknown → 200K assumed) | 200K | — | — | **0.40** | **0.65** |

Note: for the 200K model the old `0.5/0.75` fraction guess roughly holds; for 1M models the fractions collapse to ~0.08/0.15 because the absolute cap dominates. This is exactly why the reader is model-keyed.

## Caveats (where evidence is thin)
- No study measures a soft/hard HANDOFF fraction for a genuine multi-step agent; agentic numbers extrapolate from single-shot reasoning/retrieval benchmarks. The specific 80/150K caps are engineering judgment.
- The absolute-not-fraction finding is proven *inferentially* (same absolute lengths degrade across different-window models), not by one controlled fraction-held-constant experiment — but well corroborated (RULER, NoLiMa, arXiv 2510.05381).
- 1M-model direct effective-length data is the thinnest part; the 1M recommendation carries the most uncertainty. Newest 1M frontier models may push the band up.
- NoLiMa single-digit-K and the ~7K reasoning figure are stress ceilings (adversarial / small-model); RULER ~85%-baseline (~32–64K) is the representative operational band.
- Fast-moving field; all sources 2023–2026.

## Open questions (candidates for first-run measurement — the gauge now enables this)
- Does the absolute band shift up for the newest 1M frontier models, or stay pinned ~32–100K?
- Real agentic handoff curve (tool-call chains, scratchpad state) — unmeasured.
- Does context hygiene (relevant working state vs. stale tool output) push the usable fraction higher?
- Should HARD trigger on a degradation SIGNAL (self-consistency / probe drop) rather than a static token count?

Key sources: Chroma "Context Rot" (research.trychroma.com/context-rot); RULER (arXiv 2404.06654); NoLiMa (arXiv 2502.05167); arXiv 2510.05381 (EMNLP 2025); Lost in the Middle (arXiv 2307.03172); BABILong (arXiv 2406.10149). Full report: task wgtkrn5sx output.
