"""Build the g4 episode-delta that migrates every active lesson into the episode store.

Why a generator and not hand-written JSON: the rules below have to be applied the SAME
way to every record, and a script is the only form in which that is checkable. The rules
are Tommy's, relayed through the #308 re-scope:

  * An episode is an OBSERVATION, not a diagnosis. Migrate the lesson; do not judge it.
  * Required fields must be OBSERVABLE. Anything needing judgement must be optional and
    must NOT be solicited by name -- so this script writes NO `diagnosis` bin at all,
    even though the schema offers one. `suspected-cause` / `proposed-remedy` name the
    subject and thereby solicit a confident one-run guess.
  * NEVER back-fill a plausible-sounding value to satisfy a required field (#342). Where
    a lesson does not record a field, the statement says so explicitly, in-field, naming
    the source lesson. UNKNOWN is the marker; `strength` is `weak` wherever it appears.
  * A severity or cause claim the lesson's own author wrote is carried VERBATIM AND
    ATTRIBUTED, appended to `observed-behavior` -- because "someone once wrote that" is
    itself an observation. It is never promoted to a field and never stripped.

## Three schema facts that forced choices, all measured against
## scripts/apply_episode_delta.py at this commit

1. `agent_supplied` accepts EXACTLY five kinds, no more and no less (:136, :919). There
   is no `other-notes` field; an extra key is rejected as misfiled. So everything that
   does not fit the five rides inside them.
2. Every one of the five requires a NON-EMPTY `statement` and a `strength` (:942-955).
   A blank is not expressible. The schema refuses an empty value, not the word
   "unknown", so an honest in-field unknown is the only non-fabricating way through.
3. The `mechanical` bin's four counters are required non-negative INTEGERS (:158-162).
   There is no way to say "not recorded". Writing the ORIGIN run's counters would mean
   asserting four numbers this migration does not know, in the bin that is trusted
   BECAUSE it is machine-derived. So the mechanical bin describes the CAPTURE run
   (issue-308, commander, execute) where every value is a real observed fact, and the
   origin context -- origin run, origin lesson id, grounding artifacts -- rides in
   `artifact-ref` and in the statements, where "unknown" can be said out loud.

   The cost of that choice, stated rather than hidden: a query by `run` or `role` will
   not find a migrated observation under its ORIGIN run or role. Filed as a finding.

UNKNOWN_MARK is the token the count of unknown-carrying episodes is derived from, by
command, so the deliverable number is never eyeballed.
"""
import json
import pathlib

UNKNOWN_MARK = "UNKNOWN --"

PROVENANCE_REV = "752a62f"
LESSONS_AT = f".agent-work/LESSONS.md@{PROVENANCE_REV}"

# The capture run's real engine state. Every value here is an observed fact about
# THIS run, not a guess about the run the observation came from.
MECHANICAL_BASE = {
    "run": "issue-308",
    "project": "constellation-skills",
    "role": "commander",
    "spine-step": "execute",
    "context-manifest-ref": ".agent-work/issue-308/MISSION_FRAME.md@752a62f",
    "refusals": 0,
    "reopens": 0,
    "rework-count": 0,
    "failed-commands": 0,
}

def strength_for(statement: str, default: str) -> str:
    """Mechanical, not per-item judgement: an explicit unknown is `weak`, everything
    else takes the strength the record was authored at."""
    return "weak" if statement.startswith(UNKNOWN_MARK) else default


def build(records) -> dict:
    ops = []
    seen = set()
    for r in records:
        assert r["lesson"] not in seen, f"duplicate record for {r['lesson']}"
        seen.add(r["lesson"])
        # The provenance namespace is load-bearing, not decoration: `lesson:<id>` asserts
        # that a lesson of that id existed in the playbook and became this episode, and
        # migration_done.py counts exactly those. This run's OWN three observations never
        # were lessons, so they carry `observation:` instead. Writing them as `lesson:`
        # first made the check go red naming all three -- the check working as designed.
        ns = r.get("provenance", "lesson")
        refs = [f"{ns}:{r['lesson']}", f"origin-run:{r['origin_run']}", LESSONS_AT]
        refs.extend(r["refs"])
        assert set(r["a"]) == {"task-intent", "expected-behavior", "observed-behavior",
                               "impact-cost", "workaround"}, r["lesson"]
        for text in r["a"].values():
            assert text.strip() and "\n" not in text, f"{r['lesson']}: bad statement"
        ops.append({
            "op": "create",
            "mechanical": dict(MECHANICAL_BASE, **{"artifact-ref": refs}),
            "agent_supplied": {
                kind: {"strength": strength_for(text, "strong"), "statement": text}
                for kind, text in r["a"].items()
            },
        })
    return {"work_id": "issue-308", "ops": ops}


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from migration_records import RECORDS

    out = pathlib.Path(__file__).with_name("migration-delta.json")
    delta = build(RECORDS)
    out.write_text(json.dumps(delta, indent=2, ensure_ascii=True) + "\n", encoding="utf-8", newline="\n")
    unknown_eps = sum(
        1 for op in delta["ops"]
        if any(v["statement"].startswith(UNKNOWN_MARK) for v in op["agent_supplied"].values())
    )
    unknown_fields = sum(
        1 for op in delta["ops"] for v in op["agent_supplied"].values()
        if v["statement"].startswith(UNKNOWN_MARK)
    )
    print(f"episodes: {len(delta['ops'])}")
    print(f"episodes carrying at least one UNKNOWN field: {unknown_eps}")
    print(f"UNKNOWN fields in total: {unknown_fields}")
    print(f"wrote {out}")
