"""Live durability proof (issue #130) — REAL subprocesses, no claude, no pytest.

Uses the real run_skill_eval pipeline but swaps the agent launcher for one that
spawns a genuine long-sleeping python subprocess as the "subject", so we exercise
the real launch_agent deadline/kill/meta path and the real resume/orphan path
against actual OS processes.

  mode=run    : launch ONE subject via run_scenario (real sleeper), enforce timeout.
  mode=resume : re-invoke with resume=True, max_new_runs=0 -> adjudicate the orphan.
"""
import sys
from pathlib import Path

HERE = Path(r"C:/Programs/constellation-wt-129-131")
sys.path.insert(0, str(HERE / "scripts"))
import importlib.util
spec = importlib.util.spec_from_file_location("run_skill_eval", HERE / "scripts" / "run_skill_eval.py")
rse = importlib.util.module_from_spec(spec)
sys.modules["run_skill_eval"] = rse
spec.loader.exec_module(rse)


def sleeper_launch(argv, *, cwd, env, stdout_path, stderr_path, timeout):
    """Spawn a REAL long-sleeping python as the subject (ignoring the agent argv),
    driving it through the genuine launch_agent machinery so the deadline poll,
    tree-kill, heartbeat stamping, and pid recording all run for real."""
    real_argv = [sys.executable, "-c", "import time,sys; sys.stderr.write('subject up\\n'); time.sleep(3000)"]
    return rse.launch_agent(real_argv, cwd=cwd, env=env, stdout_path=stdout_path,
                            stderr_path=stderr_path, timeout=timeout)


def main():
    mode, temp_dir = sys.argv[1], sys.argv[2]
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
    scenario = rse.load_scenario(HERE / "evals" / "euler-1-multiples")
    scenario.timeout_seconds = timeout
    scenario.m = 1  # one completion target for the proof
    if mode == "run":
        v = rse.run_scenario(scenario, temp_root=Path(temp_dir), launch=sleeper_launch,
                             worktree=str(HERE), max_new_runs=1)
    else:  # resume: adjudicate the orphan, launch nothing new
        v = rse.run_scenario(scenario, temp_root=Path(temp_dir), launch=sleeper_launch,
                             resume=True, max_new_runs=0)
    print(f"VERDICT {v.status} completed={v.completed_count} fenced={v.fenced_count}")


if __name__ == "__main__":
    main()
