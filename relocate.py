"""exc-8 tracer: relocate ONE step-specific instruction out of always-loaded
Commander prose (references/commander-core.md) into the engine-pushed gate
template (templates/EXECUTE_PLAN.template.json, task g1-implement).

Relocation, not duplication: the sentence is DELETED from the prose and
INSERTED into the imperative the engine renders through `current`.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent

# The one stranded instruction. Lives today ONLY at commander-core.md:73.
PROSE_SENTENCE = (
    " Before dispatch, fill the handoff's Deliverable Path Check: for each "
    "committed deliverable, run `git check-ignore <path>` and confirm exit 1, "
    "or record the artifact as intentionally local-only."
)

# Same instruction, re-voiced for the gate imperative (backticks dropped: the
# engine renders imperatives as plain text, not markdown).
GATE_SENTENCE = (
    " Before dispatch, fill the handoff's Deliverable Path Check section: for "
    "each committed deliverable of this gate, run 'git check-ignore <path>' and "
    "confirm it exits 1 (not ignored), recording the exact command and its exit "
    "code in the handoff; or record the artifact as intentionally local-only."
)

ANCHOR = "Dispatch a subagent invoking constellation-implementer"


def main() -> int:
    core = ROOT / "skills/commander/references/commander-core.md"
    plan = ROOT / "skills/commander/templates/EXECUTE_PLAN.template.json"

    text = core.read_text(encoding="utf-8")
    if PROSE_SENTENCE not in text:
        print("FAIL: prose sentence not found verbatim in commander-core.md")
        return 1
    core.write_text(text.replace(PROSE_SENTENCE, ""), encoding="utf-8")
    print("removed from prose : commander-core.md")

    d = json.loads(plan.read_text(encoding="utf-8"))
    imp = d["tasks"]["g1-implement"]["imperative"]
    if ANCHOR not in imp:
        print("FAIL: anchor not found in g1-implement imperative")
        return 1
    d["tasks"]["g1-implement"]["imperative"] = imp.replace(
        " " + ANCHOR, GATE_SENTENCE + " " + ANCHOR, 1
    )
    plan.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
    print("inserted into gate : EXECUTE_PLAN.template.json g1-implement")

    # Invariant: exactly one home for the instruction, and it is the template.
    n_prose = core.read_text(encoding="utf-8").count("check-ignore")
    n_gate = plan.read_text(encoding="utf-8").count("check-ignore")
    print(f"check-ignore occurrences -> prose={n_prose} gate_template={n_gate}")
    return 0 if (n_prose == 0 and n_gate == 1) else 1


if __name__ == "__main__":
    sys.exit(main())
