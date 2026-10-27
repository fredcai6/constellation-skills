---
name: pi-commander
description: Submit a bounded repository task to a local Constellation Pi Commander, resume its conversation, and inspect its progress and reviewed results.
---

# Pi Commander client

Use the local project at `/home/tommy/projects/constellation-pi`. Read its README
for the current interface and limits. Run commands from that project with
`npm start -- ...`. Pi owns the Commander and crew sessions; this skill is a client.

For a new task, supply the target repository, Constellation source checkout, working
Python executable, and a concise task through `new`. Keep the printed run directory.
Use `chat` to talk to that Commander and `status` to inspect its current engine gate,
plan, crew results, sessions, and known usage. Reuse the run directory when resuming.
Never start a duplicate run merely because the Commander is waiting for a decision.

The first version follows plan → implement → review → accept. Nominal operations
are selected from role and engine state. A review BLOCK can return to implementation
through `repair`, retaining the concrete reviewer findings and separate crew sessions.
A crew result is evidence to assess, not proof that the reported work is correct.

`approve` represents a human decision. Relay an explicit human approval and its
reason; do not manufacture that approval as a client agent. `override` exists for
explicit direction from the human or a higher-level agent. Name the directing
principal and reason. Read the current CLI help before using exceptional operations.
Do not edit checklist files to change engine state.

The Claude key must already be available to the process through ANTHROPIC_API_KEY.
Keep credentials out of prompts, command output, and run records. Defaults use Haiku
with bounded requests. Status records known usage; calls interrupted at the provider
may still be billed. Remote Telegram access and additional providers are deferred.
