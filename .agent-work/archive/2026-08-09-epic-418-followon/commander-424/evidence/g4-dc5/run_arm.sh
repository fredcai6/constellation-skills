#!/usr/bin/env bash
# Run ONE measurement arm for gate g4 (DC5), issue #424.
#
# Usage: run_arm.sh <cli|mcp> <arm-dir> <session-id>
#
# The two arms get a byte-identical spine and a task prompt that differs in
# exactly one paragraph -- the interface the agent reaches the engine through.
# Everything else (the goal, the rules, the stop condition) is shared text.
set -u

ARM="$1"; DIR="$(cd "$(dirname "$2")" && pwd)/$(basename "$2")"; SID="$3"
REPO="/home/tommy/projects/constellation-skills-wt/f-424"

SHARED="You are driving a checklist spine to completion. The spine file is ${DIR}/spine.json.

Drive it to DONE. Use session id '${SID}'. Claim the lease first, then work each gate in order,
doing exactly what that gate's imperative says, until the engine reports no open items. Release the
lease as your last action.

Rules:
- NEVER hand-edit spine.json or any checklist JSON. Every state change goes through the engine.
- Any file a gate tells you to create goes in ${DIR}/.
- When you are done, print DONE-ARM as your final line."

case "$ARM" in
  cli)
    IFACE="Reach the engine through its command-line interface, by running
'python3 ${REPO}/scripts/checklist_engine.py' with Bash. Work out the verbs and flags you need."
    TOOLS="Bash Write Read"
    ;;
  mcp)
    IFACE="Reach the engine through the MCP tools whose names begin with 'mcp__spine__'. Work out
which tool and which arguments you need. Do not shell out to the engine."
    TOOLS="mcp__spine__spine_status mcp__spine__spine_lease mcp__spine__spine_start mcp__spine__spine_advance mcp__spine__spine_evidence mcp__spine__spine_halt mcp__spine__spine_survey_result Write Read"
    ;;
  *) echo "unknown arm: $ARM" >&2; exit 2;;
esac

PROMPT="${SHARED}

${IFACE}"

cd "$REPO" || exit 1
export SPINE_FILE="${DIR}/spine.json"
export SPINE_ENGINE="${REPO}/scripts/checklist_engine.py"
export SPINE_SESSION="${SID}"

timeout 900 claude -p "$PROMPT" \
  --allowedTools $TOOLS \
  --permission-mode acceptEdits \
  --output-format stream-json --verbose \
  > "${DIR}/record.jsonl" 2> "${DIR}/record.err"
echo "EXIT=$? arm=${ARM} dir=${DIR}"
