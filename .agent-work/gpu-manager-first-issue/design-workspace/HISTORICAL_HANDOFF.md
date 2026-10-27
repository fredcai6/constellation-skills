# GPU manager: handoff

Recovered 2026-10-22 from session `5e4caaec-8d65-56f7-9f39-7f537e3e1193` (2026-10-10, resume with `claude --resume 5e4caaec-8d65-56f7-9f39-7f537e3e1193` from `~/projects`). **Nothing is built.** No repo, code or README exists yet. The session ended before the experiments and the design doc.

## Problem

One card (R9700, 32 GB VRAM). You often want to take the local LLM down for a few hours of batch compute (tennis fits, charts, orrery), then bring it back. Today you do this by hand. The agent docs in orrery and tennis_elo say "never stop `docker-llm-1` / `docker-asr-1`", which contradicts what you do, so agents can't free the card and nothing tells them it's gone. The goal is to pull the LLM/GPU management out of the journal repo into a general GPU manager that works across projects.

## Current state (as of 2026-10-10)

- **Journal repo owns the servers:** `services/llm/Dockerfile` (llama.cpp ROCm build, pinned `b10327`), `llm` (:8005) and `asr` (:8006) in `infra/docker/docker-compose.yml`, plus `fetch-model.sh` and `setup-models-drive.sh`.
- **Orrery** calls :8005 heavily (about 365 references), plus :8006 and its own `orrery-embed-judge` container.
- **tennis_elo** starts `jaxstate-rocm` containers ad hoc (`docker run --device /dev/kfd`).
- **f1brainz-tyres, journal-transcribe** use the GPU occasionally.
- **Outage handling differs:** journal falls back to Claude when the LLM is down; orrery's harness treats it as an error.
- About 280 references to the container name `docker-llm-1` sit in orrery and tennis_elo docs.

## Rulings (yours)

- **Two tiers.**
  - **Interactive:** the Telegram agent (daily check-ins, tutoring, ad hoc) on ONE fixed 27B config. Always wins, never downsized. ASR comes up alongside it, because check-ins are moving to audio.
  - **Batch:** orrery, tennis, f1brainz and journal recurring processing. All equal ("project du jour"); you launch them all. Other models (e.g. orrery's 4B) are batch tenants.
- **Journal becomes just another client.** The local LLM moves out of it. Drop the vestigial Claude fallback (a separate journal change).
- **No pre-warming for check-ins.** A cold start of tens of seconds is fine; replies usually come within an hour or not at all.
- **Batch job rules:**
  - checkpoint about every 10 minutes (so a job can be killed at any moment, and survive workstation reboots);
  - chunks under 4 hours, so jobs interleave;
  - declare approximate VRAM and scale to fit, so some batch work can run beside the 27B;
  - report progress, e.g. `gpu progress --chunk 2/4 --pct 50`;
  - a job that can't checkpoint, or can't fit in 4 h chunks, is allowed, but its agent asks you first.
- **Deliverables:**
  - a README at the root of `~/projects` stating accepted GPU usage;
  - your machine status box generalised into a local web page (an extension of your site) showing jobs and chunk progress.
- **Process:** write a short design for the new repo and a draft README; you review before anything is built.

## Physical constraints found

- `docker pause` frees compute, **not VRAM**. A paused 20 GB job still blocks the 27B.
- Freeing memory means the process exits. Options: CRIU with the AMD GPU plugin (not installed, Docker checkpoint is off by default, fragile; not recommended), or make jobs save and resume. Resume is the recommended route; tennis fits already do it (`theta_*.npy`, `fit_restart*.log` in `scratch/jaxstate`).
- Derating a running job is weak. The power cap only goes 300 to 210 W (about 30%), needs root, and is card-wide. CU mask, JAX memory fraction and llama context are start-time only. So derate means restart smaller.
- An idle LLM uses almost no compute, only memory. A job beside an idle LLM should run near full speed (unmeasured).
- Rough sizes: 27B at 64k context is about 20 GB; short context about 17 GB; 4B about 3.5 GB. While you chat with the 27B, about 12 GB is left for batch.

## Proposed shape (agent's, not yet ratified)

- **New repo** (placeholder name `gpu-box`) takes the Dockerfile, the `llm`/`asr` services, the model scripts and a `gpu` command. Journal keeps only its connection settings (`LOCAL_LLM_URL`, enable flags) and reaches the server over a shared Docker network.
- **A small custom broker** owns the card. Nothing else starts GPU containers directly. Slurm was rejected: it doesn't treat VRAM as a resource and can't see LLM demand.
  - Jobs: `gpu submit --vram 20G --priority batch -- <cmd>`.
  - Operator commands: `gpu status`, `gpu take` (you override everything), `gpu release`.
  - Each tenant has a registry entry: name, start/stop, approximate VRAM, whether it is interruptible.
  - The broker sits in front of :8005 so it can see LLM demand. The Telegram bot gets its own key and is tagged interactive; everything else is batch.
  - When interactive demand arrives: kill batch jobs (at most about 10 minutes lost), load the 27B, and keep it through an idle window (about 20 to 30 min) so tutoring doesn't drop.
  - Status page reads everything from the broker's single state.
- Shape A (explicit claim/release) vs. shape B (`llama-swap` load-on-demand): the agent leaned A, built so B can be added later. Your later answers (broker with requests and priorities) moved toward a hybrid; unresolved.

## Open questions

1. **Non-resumable batch job when you message the bot:** kill and redo its chunk, or make your message wait? The agent proposed requiring save/resume as a condition to run at all, so it is always "kill". Unanswered, and in tension with your "I get to choose" exception.
2. **Voice notes / ASR:** you said ASR comes up with the 27B, but not whether ASR is counted as interactive for eviction purposes or how much VRAM it reserves.
3. **Idle windows:** how long the 27B stays after your last message (20 to 30 min proposed), and the minimum hold time for a batch job so a busy agent doesn't keep evicting fits.
4. **What happens to LLM callers when the LLM is down** (e.g. an orrery agent calling :8005 during a batch run): fail fast, queue, or have the broker answer "busy, retry"? And should orrery use the 4B instead?
5. **Who can claim the card:** can agents run `gpu submit` themselves (tennis agents launch GPU containers directly today), or only you?
6. **Container name:** keep `docker-llm-1` (avoids the roughly 280-reference sweep) or rename and sweep?
7. **Default state when idle:** LLM loaded by default (you said yes), and the batch-to-LLM handback trigger when the queue empties.
8. **Downsized LLM modes** (short context, 4B): agent suggested; you want a single fixed config for the Telegram agent, so probably only as batch tenants. Confirm.
9. **Status page:** how it extends the existing status box and website, and what it must show beyond jobs and chunk progress.
10. **Batch adoption:** how existing tenants (tennis `jaxstate-rocm`, orrery, f1brainz) get the checkpoint/progress contract, and who retrofits them.

## Experiments not yet run

The card was busy (tennis `v34waves-gpu-fe` at 78%), so none of these ran. Run them when the card is idle and without interrupting live work:

- cold-load time of the 27B (guess: 20 to 60 s);
- confirm a paused container keeps its VRAM;
- slowdown of a small fit running beside an idle 4B (or 27B).

## Next steps

1. Run the three experiments above when the card is idle.
2. Write the short design for the new repo and a draft `~/projects/README` GPU-usage section.
3. You review; resolve the open questions.
4. Only then build: new repo, broker, `gpu` CLI, journal-as-client change, status page.

Related memory: `gpu-manager-project.md` in the Claude memory directory.
