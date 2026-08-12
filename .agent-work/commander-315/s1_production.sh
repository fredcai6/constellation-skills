#!/usr/bin/env bash
# Prove S1 through the REAL engine production path (main() -> base_dir=path.parent
# -> _check_condition -> _run_check_command), by applying the proposed fix to a
# COPY of the engine and driving a real commander spine's init precondition.
set -u
WT=/home/tommy/projects/constellation-skills-wt/epic-568-315
T=$(mktemp -d)

# --- build a main checkout + a linked worktree, exactly the real topology ---
git init -q "$T/main"
cd "$T/main" || exit 1
git config user.email t@t; git config user.name t
mkdir -p scripts
cp "$WT/scripts/verify_worktree_isolation.py" scripts/
echo x > f.txt; git add -A; git commit -qm init
git worktree add -q "$T/wt" -b wtbranch >/dev/null 2>&1

# --- a spine in the WORKTREE, with the shipped init.c0 precondition ---
mkdir -p "$T/wt/.agent-work/w1"
cat > "$T/wt/.agent-work/w1/spine.json" <<JSON
{"work_id":"w1","type":"gated","items":["init"],
 "tasks":{"init":{"id":"init","status":"pending","imperative":"isolation",
  "preconditions":[{"id":"c0","statement":"in the provisioned worktree",
    "check":{"kind":"command","command":"python scripts/verify_worktree_isolation.py --here $T/wt"},
    "satisfied":false}],
  "postconditions":[],"evidence":[]}},
 "triage_candidates":[],"blockers":[],"refusals":[]}
JSON

# --- engine A: unmodified. engine B: proposed fix (cwd = spine's enclosing repo root) ---
cp "$WT/scripts/checklist_engine.py" "$T/engine_before.py"
cp "$WT/scripts/checklist_engine.py" "$T/engine_after.py"
py - "$T/engine_after.py" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1]); s = p.read_text()
old = '''def _run_check_command(command: str) -> tuple[subprocess.CompletedProcess, str]:'''
new = '''def _repo_root_for(base_dir):
    if base_dir is None:
        return None
    d = Path(base_dir).resolve()
    while True:
        if (d / ".git").exists():
            return d
        if d == d.parent:
            return None
        d = d.parent


def _run_check_command(command: str, base_dir=None) -> tuple[subprocess.CompletedProcess, str]:'''
assert old in s
s = s.replace(old, new, 1)
old2 = 'proc = subprocess.run([shell, "-c", command], capture_output=True, text=True)'
new2 = 'proc = subprocess.run([shell, "-c", command], capture_output=True, text=True, cwd=_repo_root_for(base_dir))'
assert old2 in s
s = s.replace(old2, new2, 1)
old3 = 'proc, shell_marker = _run_check_command(chk["command"])'
new3 = 'proc, shell_marker = _run_check_command(chk["command"], base_dir)'
assert old3 in s
s = s.replace(old3, new3, 1)
p.write_text(s)
print("patched engine_after.py")
PY

echo
echo "topology: main=$T/main   worktree=$T/wt   spine=$T/wt/.agent-work/w1/spine.json"
echo "the gate asserts the agent is standing in $T/wt"
echo "the LAUNCHER will stand in $T/main -- the wrong place, which the gate exists to catch"
echo

for label in before after; do
  cp "$T/wt/.agent-work/w1/spine.json" "$T/spine_$label.json"
  # spine must sit inside the worktree for base_dir to resolve there
  cp "$T/spine_$label.json" "$T/wt/.agent-work/w1/spine.json"
  echo "--- engine_$label.py, launched from $T/main ---"
  ( cd "$T/main" && py "$T/engine_$label.py" --file "$T/wt/.agent-work/w1/spine.json" start init 2>&1 | tail -2 )
  echo
done

cd /
rm -rf "$T"
