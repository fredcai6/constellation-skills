"""r9: did the rework break anything the previous review passed?"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(".").resolve() / "tests"))
import test_cli_retirement_guard as G

print("=== the four vacuity floors")
for label, got, floor in [("INSTRUCTION_FILES (skills/)", len(G.INSTRUCTION_FILES), 60),
                          ("SPEC_FILES (specs/)", len(G.SPEC_FILES), 1),
                          ("OVERLAY_FILES (overlay)", len(G.OVERLAY_FILES), 60),
                          ("GUARD_TEXTS", len(G.GUARD_TEXTS), 1800)]:
    print(f"  {label:30} {got:5}  floor {floor:5}  {'OK' if got >= floor else 'BELOW FLOOR'}")

print("\n=== exception list: is there ANY per-file exclusion construct?")
src = pathlib.Path("tests/test_cli_retirement_guard.py").read_text()
import re as _re
print("  _walk_dir body filters on:", _re.search(r"if p\.is_file\(\)[^\n]*", src).group(0).strip())
print("  any EXCLUDE/SKIP/ALLOW/IGNORE list?:",
      _re.findall(r"^\s*(EXCLU\w+|SKIP\w*|ALLOW\w*|IGNORE\w*|EXEMPT\w*)\s*=", src, _re.M) or "NONE")
print("  exception list length: 0")

print("\n=== both pre-ruled survivors, out by the WALK RULE alone")
for s in ["docs/superpowers/plans/2026-06-27-delegated-autonomous-commander.md",
          "scripts/init_work_area.py"]:
    print(f"  {s}: in GUARDED_FILES = {s in G.GUARDED_FILES}   (file exists: {pathlib.Path(s).exists()})")
    print(f"      named in any code path? {'no -- docstring prose only' if src.count(s) and 'GUARDED' not in src.split(s)[0][-200:] else '?'}"
          f"  (occurrences in file: {src.count(s)}, all inside the module docstring: {src.index(s) < src.index('from __future__')})")

print("\n=== PROSE_ONLY / COMMAND_SHAPED discriminations still hold")
T = G.TestTheInvocationPredicateItself()
for m in ["test_catches_every_command_shape", "test_leaves_a_bare_component_mention_alone",
          "test_the_clause_pattern_reads_every_measured_surface_form"]:
    try: getattr(T, m)(); print(f"  {m}: PASS")
    except AssertionError as e: print(f"  {m}: FAIL -> {e}")
print(f"  PROSE_ONLY entries: {len(T.PROSE_ONLY)} (incl. the write-a-skill archetype cell), "
      f"COMMAND_SHAPED: {len(T.COMMAND_SHAPED)}")

print("\n=== overlay scope rule: is a live run's own artifacts reachable?")
overlay_root = (G.ROOT / G.OVERLAY_DIR).resolve()
run_dir = (G.ROOT / ".agent-work/567-d1").resolve()
print(f"  overlay root: {overlay_root}")
print(f"  is .agent-work/567-d1 an ANCESTOR-descendant of the overlay root? "
      f"{overlay_root in run_dir.parents or run_dir in overlay_root.parents}")
strays = [p for p in G.GUARDED_FILES if p.startswith(".agent-work/") and not p.startswith(G.OVERLAY_DIR + "/")]
print(f"  strays under .agent-work/ outside the overlay: {len(strays)}")
print(f"  symlinks escaping the overlay: "
      f"{[str(p) for p in overlay_root.rglob('*') if p.is_symlink()] or 'NONE'}")

print("\n=== lane-D2 fenced files: is the .baseline/constellation-workbench subtree clean of all four?")
pats = [("placeholder", G.ENGINE_PLACEHOLDER_RE), ("fallback", G.CLI_FALLBACK_RE),
        ("invocation", G.ENGINE_INVOCATION_RE), ("standin", G.ENGINE_STANDIN_COMMAND_RE)]
sub = [(p, w, t, wf) for (p, w, t, wf) in G.GUARD_TEXTS
       if p.startswith(".agent-work/templates/.baseline/constellation-workbench/")]
files = sorted({p for p, _, _, _ in sub})
hits = {lbl: sum(len(pat.findall(t)) for _, _, t, _ in sub) for lbl, pat in pats}
print(f"  {len(files)} files, {len(sub)} texts, matches: {hits}")
