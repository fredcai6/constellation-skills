"""Small helper: drive the issue-716 commander spine through the engine."""
import subprocess, sys

ENGINE = r"C:\Users\fredc\.claude\skills\constellation-commander\scripts\checklist_engine.py"
FILE = ".agent-work/issue-716/spine.json"
SESSION = "commander-issue-716"


def eng(*args):
    r = subprocess.run([sys.executable, ENGINE, "--file", FILE, *args, "--session-id", SESSION],
                       capture_output=True, text=True, encoding="utf-8")
    out = ((r.stdout or "") + (r.stderr or "")).strip()
    # drop the long RAIL preamble, keep the verdict lines
    lines = [ln for ln in out.splitlines() if ln.strip() and not ln.startswith("RAIL:")]
    print(f"[{r.returncode}] " + " | ".join(lines[-3:]))
    return r.returncode


if __name__ == "__main__":
    eng(*sys.argv[1:])
