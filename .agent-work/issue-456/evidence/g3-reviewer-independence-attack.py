"""Reviewer-authored independence attack on checks.entity_symbol_join (gate g3).

Independent of the implementer's own mutations (EXTRACTOR_RENAME_MUTATION,
SOURCE_SCAN_FLATTEN_MUTATION in tests/test_code_map.py). Different anchors,
different substitutions, run against the REAL corpus (this repository) rather
than the synthetic `_make_mixed_repo` fixture, via scratch --artifacts/--out so
the committed map/ tree and .code-map/ are never touched.

Three runs, each into its own scratch dir:
  CONTROL  - unmutated copy of scripts/code_map, real corpus. Must be exit 0.
  SIDE A   - extract.py: child_sym returns the bare name, dropping the whole
             enclosing chain (module prefix included). This is the literal
             "flattens an enclosing chain" mutation the review handoff names.
  SIDE B   - checks.py: SourceScan._walk stops treating ClassDef as a
             qualifying scope, so a method's source-derived qualified name
             drops its class prefix specifically (methods only, not the
             implementer's whole-tree flatten).

Each run asserts the substitution's anchor occurred exactly once (so a defect
in this harness fails loudly rather than passing vacuously), and reports the
check's own exit code and entity-symbol-join failure count.
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
CODE_MAP = ROOT / "scripts" / "code_map"


class HarnessError(AssertionError):
    pass


def mutated_copy(tmpdir, module, old, new):
    dest = pathlib.Path(tmpdir) / "scripts" / "code_map"
    shutil.copytree(CODE_MAP, dest, ignore=shutil.ignore_patterns("__pycache__"))
    original = (CODE_MAP / module).read_text(encoding="utf-8")
    if original.count(old) != 1:
        raise HarnessError(
            f"anchor occurs {original.count(old)} time(s) in {module}, expected 1: {old!r}")
    text = original.replace(old, new, 1)
    if text == original:
        raise HarnessError("substitution did not change the text")
    (dest / module).write_text(text, encoding="utf-8", newline="\n")
    return pathlib.Path(tmpdir)


def unmutated_copy(tmpdir):
    dest = pathlib.Path(tmpdir) / "scripts" / "code_map"
    shutil.copytree(CODE_MAP, dest, ignore=shutil.ignore_patterns("__pycache__"))
    return pathlib.Path(tmpdir)


def run(host, scratch, *args):
    import os
    env = dict(os.environ)
    env.pop("FORCE_COLOR", None)
    env.pop("PYTHONIOENCODING", None)
    return subprocess.run(
        [sys.executable, "-m", "scripts.code_map", *args,
         "--root", str(ROOT),
         "--artifacts", str(pathlib.Path(scratch) / "artifacts"),
         "--out", str(pathlib.Path(scratch) / "out")],
        cwd=str(host), capture_output=True, text=True, env=env)


def build_and_check(host, scratch, label):
    b = run(host, scratch, "build")
    if b.returncode != 0:
        print(f"{label}: BUILD FAILED exit={b.returncode}\n{b.stdout[-2000:]}\n{b.stderr[-2000:]}")
        return None
    c = run(host, scratch, "check")
    print(f"--- {label} --- check exit={c.returncode}")
    for line in c.stdout.splitlines():
        if "entity-symbol-join" in line or line.startswith("passed") or line.startswith("FAILED"):
            print("   " + line)
    # print a few of the entity-symbol-join failure lines specifically
    lines = c.stdout.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("FAIL entity-symbol-join"):
            for extra in lines[i:i + 4]:
                print("   " + extra)
            break
    return c


def main():
    results = {}

    with tempfile.TemporaryDirectory(prefix="g3rev-ctl-") as tmp:
        scratch = tempfile.mkdtemp(prefix="g3rev-ctl-out-")
        try:
            host = unmutated_copy(tmp)
            results["CONTROL"] = build_and_check(host, scratch, "CONTROL (unmutated, real corpus)")
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    with tempfile.TemporaryDirectory(prefix="g3rev-a-") as tmp:
        scratch = tempfile.mkdtemp(prefix="g3rev-a-out-")
        try:
            host = mutated_copy(
                tmp, "extract.py",
                '        return base + name if base.endswith(":") else base + "." + name\n',
                '        return self.mod + ":" + name\n')
            results["SIDE_A_extractor_chain_flatten"] = build_and_check(
                host, scratch, "SIDE A: extract.child_sym flattens the enclosing chain "
                               "(every definition reads as module-level, module prefix kept)")
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    with tempfile.TemporaryDirectory(prefix="g3rev-b-") as tmp:
        scratch = tempfile.mkdtemp(prefix="g3rev-b-out-")
        try:
            host = mutated_copy(
                tmp, "checks.py",
                "            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):\n",
                "            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):\n")
            results["SIDE_B_sourcescan_class_blind"] = build_and_check(
                host, scratch, "SIDE B: checks.SourceScan stops qualifying by ClassDef")
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    print("\n=== SUMMARY ===")
    for label, proc in results.items():
        if proc is None:
            print(f"{label}: BUILD FAILED (see above)")
        else:
            print(f"{label}: check exit={proc.returncode}")


if __name__ == "__main__":
    main()
