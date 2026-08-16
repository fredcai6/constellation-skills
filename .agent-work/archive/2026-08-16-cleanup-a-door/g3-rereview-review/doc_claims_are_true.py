"""The three reworked doc references: are their CLAIMS true of the code that runs?

CREW_CONTEXT.md: "assert against behaviour, never against text that describes it."
Confirming the prose changed is worthless -- the blocker was prose that contradicted
the code, so the check is whether the NEW prose matches the code. Each claim is
checked against the AST or the live import, never against another string.
"""

import ast
import importlib.util
import sys
from pathlib import Path

SERVER = Path("scripts/mcp_spine_server.py")
tree = ast.parse(SERVER.read_text(encoding="utf-8"))
funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
failures = []


def check(label, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {label}{(' -- ' + detail) if detail else ''}")
    if not ok:
        failures.append(label)


# --- Claim 1: _log_rejection appends to `_rejectionlog()`, not the deleted REJECTIONLOG.
check("_rejectionlog() exists as a function", "_rejectionlog" in funcs)
check("REJECTIONLOG is gone as an identifier",
      not any(isinstance(n, ast.Name) and n.id == "REJECTIONLOG" for n in ast.walk(tree)))
lr = funcs["_log_rejection"]
calls = {n.func.id for n in ast.walk(lr) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
check("_log_rejection actually calls _rejectionlog()", "_rejectionlog" in calls,
      f"calls={sorted(calls)}")
check("_log_rejection's docstring names _rejectionlog()",
      "_rejectionlog()" in (ast.get_docstring(lr) or ""))

# --- Claim 2: _primary_checkout_for_lifecycle reads NO environment at all.
pc = funcs["_primary_checkout_for_lifecycle"]
env_reads = [
    n for n in ast.walk(pc)
    if (isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
        and n.value.id == "os" and n.attr == "environ")
    or (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr in {"getenv"})
]
check("_primary_checkout_for_lifecycle contains ZERO os.environ / getenv reads",
      not env_reads, f"found={len(env_reads)}")
names = {n.id for n in ast.walk(pc) if isinstance(n, ast.Name)}
check("...and it does reference the SPINE global (bound-spine branch)", "SPINE" in names)
src = ast.get_source_segment(SERVER.read_text(encoding="utf-8"), pc) or ""
check("...and falls back to THIS SCRIPT's own location (__file__)", "__file__" in src)

# --- Claim 3: the README cites a test that exists under that name.
CITED = "test_mcp_json_spine_file_is_overridable_and_any_default_loads"
readme = Path("examples/mcp-interactive-demo/README.md").read_text(encoding="utf-8")
check("README cites the new test name", CITED in readme)
check("README no longer cites the deleted test name",
      "test_mcp_json_referenced_spine_file_exists_and_loads" not in readme)
test_tree = ast.parse(Path("tests/test_mcp_spine_server.py").read_text(encoding="utf-8"))
test_names = {n.name for n in ast.walk(test_tree) if isinstance(n, ast.FunctionDef)}
check("the cited test genuinely exists in tests/test_mcp_spine_server.py", CITED in test_names)

# --- Claim 3b: README's tense fix -- .mcp.json's default really is empty now.
mcp = Path(".mcp.json").read_text(encoding="utf-8")
check(".mcp.json's SPINE_FILE default really is empty (README's 'pointed at' is correct)",
      '"${SPINE_FILE:-}"' in mcp, "found: " + next(
          (l.strip() for l in mcp.splitlines() if "SPINE_FILE" in l), "<none>"))

print(f"\nRESULT: {len(failures)} failed claim(s)" + (f" -> {failures}" if failures else ""))
sys.exit(1 if failures else 0)
