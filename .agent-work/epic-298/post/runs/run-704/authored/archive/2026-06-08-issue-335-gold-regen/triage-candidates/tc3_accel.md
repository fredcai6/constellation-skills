## What
Evaluate accelerating the inference-heavy sampled-backtest (thousands of Monte-Carlo forward passes) on this laptop's Lunar Lake silicon:
- **Arc 140V iGPU** via Intel Extension for PyTorch (XPU device), and/or
- **ONNX Runtime + OpenVINO** execution providers (iGPU / AI Boost NPU),
behind a **numerics-parity gate** (fused Brier / ordering within tolerance of the FP32 CPU result).

## Why
"Hate leaving silicon idle." The gold cycle is currently CPU-parallel (`utilization=max` → cores-1 workers, `threads_per_worker=1`). Findings from the #335 run:
- The **NPU (AI Boost) is inference-only** — no PyTorch training path; not usable for the training cycle.
- The **iGPU** could train via IPEX-XPU, but the workload is ~96 *tiny* parallel jobs (hidden_dim=128) that don't saturate a GPU, and GPU/NPU math breaks the bit-reproducibility relied on for seeded promotion (#362).
- The natural fit is the **inference / backtest** phase (forward-pass heavy, quantizable), not training.

## Evidence
Hardware: Intel Core Ultra 7 268V + Arc 140V iGPU (16GB) + AI Boost NPU4 (~48 INT8 TOPS). Analysis recorded in the #335 regen run.

## Acceptance
A spike report that either:
- measures iGPU/NPU inference throughput on the sampled-backtest vs CPU **with** a numerics-parity gate (Brier/ordering within tolerance), showing a worthwhile speedup; **or**
- documents a "not worth it at current model sizes" finding.

Revisit if the channel-refactor grows model/batch sizes.

## Out of scope
Training on the NPU (unsupported); changing the gold cycle's CPU-parallel default; anything that breaks bit-reproducibility of the promoted artifact.
