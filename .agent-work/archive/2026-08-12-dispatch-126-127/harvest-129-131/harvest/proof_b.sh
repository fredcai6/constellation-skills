#!/bin/bash
# PROOF B: deadline/reaping survives RUNNER DEATH (issue #130).
# Launch a runner with a long timeout, kill the runner mid-flight (simulating the
# harness reap), then --resume to adjudicate the orphan the dead runner left.
set -u
DIR="C:/Users/fredc/AppData/Local/Temp/constellation-live-b"
DRV="C:/Users/fredc/AppData/Local/Temp/claude/C--Programs-constellation-skills/eb0613e9-f73d-465e-a396-6c96e3cb6ac6/scratchpad/live_kill_test.py"
rm -rf "$DIR"; mkdir -p "$DIR"
cd /c/Programs/constellation-wt-129-131

echo "STEP1: launch runner (long timeout) in background"
py "$DRV" run "$DIR" 3000 > "$DIR/runner.log" 2>&1 &
DRIVER=$!
echo "runner driver pid=$DRIVER"

echo "STEP2: wait for the subject to spawn (subject_pid recorded in meta)"
for i in $(seq 1 60); do
  if [ -f "$DIR/run-0/meta.json" ] && python -c "import json,sys; sys.exit(0 if json.load(open('$DIR/run-0/meta.json')).get('subject_pid') else 1)" 2>/dev/null; then
    echo "subject spawned after ${i}s"; break
  fi
  sleep 1
done
echo "--- meta after spawn ---"; cat "$DIR/run-0/meta.json"
SUB=$(python -c "import json;print(json.load(open('$DIR/run-0/meta.json'))['subject_pid'])")

echo "STEP3: KILL the runner driver (simulate harness reap of the background task)"
kill -9 "$DRIVER" 2>/dev/null; wait "$DRIVER" 2>/dev/null
sleep 2
echo "--- meta after runner death (should still be 'launched' — runner never finalized) ---"; cat "$DIR/run-0/meta.json"
# reap the orphaned subject the dead runner left (external reaper uses recorded pid)
taskkill //PID "$SUB" //T //F >/dev/null 2>&1 && echo "external reaper tree-killed orphaned subject pid=$SUB" || echo "subject pid=$SUB already gone"

echo "STEP4: --resume adjudicates the orphan (deadline/verdict enforced OUTSIDE the dead runner)"
py "$DRV" resume "$DIR" 2>&1 | tail -2
echo "--- meta after resume adjudication ---"; cat "$DIR/run-0/meta.json"
echo "PROOF_B_DONE"
