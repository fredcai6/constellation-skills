# docs/agents/engine-config.json is referenced by three files and does not exist

`specs/implementer.spine.toml` and `specs/reviewer.spine.toml` both set
`config_ref = "docs/agents/engine-config.json"`. The Commander spine's `context` imperative also
names it as a project delta to read. `EXECUTE_PLAN.template.json` sets the same `config_ref`.

**Measured:** `docs/agents/` contains exactly CREW_CONTEXT.md, GLOSSARY.md, ORCHESTRATOR_CONTEXT.md.
The file does not exist. The engine tolerates the dangling reference (this run's plan drove fine),
so it is latent rather than breaking.

**Candidate fix:** create the config, or drop the `config_ref` from the specs and the template.
