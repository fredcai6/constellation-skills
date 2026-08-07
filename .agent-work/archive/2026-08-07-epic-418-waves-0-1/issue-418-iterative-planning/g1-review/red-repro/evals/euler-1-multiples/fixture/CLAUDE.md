# Project context

This project runs on the **constellation** skill suite (installed at `.claude/skills/`).

Engineering work here is **not freeform and not done by hand**. Every bounded issue
is run under the appropriate constellation skill, and its workflow state is driven
**through the checklist engine**
(`.claude/skills/constellation-workbench/scripts/checklist_engine.py`) one step at a
time. Work the engine never saw did not happen: an issue solved directly, or a spine
copied but never advanced, or one hand-written to look complete, does **not** count as
done here — only an engine-driven spine does.

A delegated dispatch (no reachable human) **loads `constellation-commander-delegated`
first and claims the engine lease before touching the problem**, then does exactly
what each spine step says. The issue is complete only once the engine has been driven
through to its final step.
