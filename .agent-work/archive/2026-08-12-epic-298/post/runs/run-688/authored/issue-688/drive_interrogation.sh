#!/bin/sh
E="C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py"
F=".agent-work/issue-688/interrogation.json"
py "$E" --file "$F" claim --session-id interr-688 --claimed-by interrogator --worktree . 2>&1 | tail -1
for q in i0-context q1 q2 q3 q4 q5 q6 q7 q8 q9 q10 q11 zc-consolidate; do
  py "$E" --file "$F" start "$q" --session-id interr-688 >/dev/null 2>&1
  py "$E" --file "$F" advance "$q" --session-id interr-688 \
    --why "resolved and recorded in .agent-work/issue-688/INTERROGATION_RECORD.json; verify_interrogation.py exit 0" 2>&1 | tail -1
done
