#!/usr/bin/env bash
# g4b acceptance arm. Adapted from F's archived run_arm.sh (the harness that
# worked), with ONE deliberate change: Bash is ALLOWED.
#
# F's mcp arm withheld Bash, which made "zero CLI engine invocations" true by
# construction and therefore unmeasurable. Adoption is a claim about what an
# agent CHOOSES when both doors are open, so this arm opens both and measures
# which one it used. A measure that cannot lose is not a measure.
set -u
REPO="/home/tommy/projects/constellation-skills-wt/f2-mcp-adoption"
DIR="${REPO}/.agent-work/epic-418-followon/commander-f2/evidence/g4b"
SPINE="${DIR}/.agent-work/g4b-acceptance/spine.json"
SID="g4b-acceptance"

PROMPT="You are a Constellation IMPLEMENTER. Load the constellation-implementer skill and work under it.

Drive the implementer plan at ${SPINE} to DONE. Use session id '${SID}'. Claim the lease first,
then work each gate in order, doing exactly what that gate's imperative says, until the engine
reports no open items. Release the lease as your last action.

Rules:
- NEVER hand-edit spine.json or any checklist JSON. Every state change goes through the engine.
- Any file a gate tells you to create goes where the gate says.
- When you are done, print DONE-ARM as your final line."

cd "$REPO" || exit 1
export SPINE_FILE="${SPINE}"
export SPINE_ENGINE="${REPO}/scripts/checklist_engine.py"
export SPINE_SESSION="${SID}"

timeout 900 claude -p "$PROMPT" \
  --allowedTools mcp__spine__spine_status mcp__spine__spine_lease mcp__spine__spine_start \
                 mcp__spine__spine_advance mcp__spine__spine_evidence mcp__spine__spine_halt \
                 mcp__spine__spine_survey_result Bash Write Read Glob Grep \
  --permission-mode acceptEdits \
  --output-format stream-json --verbose \
  > "${DIR}/arm-mcp/record.jsonl" 2> "${DIR}/arm-mcp/record.err"
echo "DISPATCH_EXIT=$?"
