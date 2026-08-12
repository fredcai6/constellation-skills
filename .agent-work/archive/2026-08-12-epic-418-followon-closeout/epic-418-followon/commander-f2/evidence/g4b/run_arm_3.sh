#!/usr/bin/env bash
set -u
REPO="/home/tommy/projects/constellation-skills-wt/f2-mcp-adoption"
DIR="${REPO}/.agent-work/epic-418-followon/commander-f2/evidence/g4b"
SPINE="${DIR}/.agent-work/g4b-acceptance-3/spine.json"
SID="g4b-acceptance-3"
PROMPT="Load the constellation-workbench skill and work under it.

You are a TOP-LEVEL dispatched agent driving YOUR OWN spine. This process's spine binding is
${SPINE} -- you own it; it is not a parent's.

Drive that spine to DONE. Use session id '${SID}'. Claim the lease first, then work each gate in
order, doing exactly what its imperative says, until the engine reports no open items. Release the
lease as your last action.

Rules:
- NEVER hand-edit spine.json. Every state change goes through the engine.
- When you are done, print DONE-ARM as your final line."
cd "$REPO" || exit 1
export SPINE_FILE="${SPINE}"
export SPINE_ENGINE="${REPO}/scripts/checklist_engine.py"
export SPINE_SESSION="${SID}"
timeout 900 claude -p "$PROMPT" \
  --allowedTools mcp__spine__spine_status mcp__spine__spine_lease mcp__spine__spine_start \
                 mcp__spine__spine_advance mcp__spine__spine_evidence mcp__spine__spine_halt \
                 mcp__spine__spine_survey_result Bash Write Read Glob Grep \
  --permission-mode acceptEdits --output-format stream-json --verbose \
  > "${DIR}/arm-mcp-3/record.jsonl" 2> "${DIR}/arm-mcp-3/record.err"
echo "DISPATCH_EXIT=$?"
