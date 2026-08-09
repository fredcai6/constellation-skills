"""Reviewer-built decoy probe. Independent of the implementer's tests."""
import importlib.util, sys, tempfile
from pathlib import Path

SCRIPT = Path(r"C:/Programs/constellation-skills-wt/epic418-w5-gates/scripts/verify_iterative_role_artifacts.py")
spec = importlib.util.spec_from_file_location("vira", SCRIPT)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def old_name_test(p: Path) -> bool:
    return p.name.startswith("constellation-")

fails = []
with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)

    # --- A real skills root, marked by the installer's CORPUS.json ---
    root = tmp / "skills"; root.mkdir()
    (root / "CORPUS.json").write_text("{}", encoding="utf-8", newline="\n")

    # --- DECOY 1: named constellation-*, NO SKILL.md, inside a real skills root ---
    d1 = root / "constellation-decoy"; d1.mkdir()
    print(f"decoy1 {d1}: exists={d1.is_dir()} has_SKILL_md={(d1/'SKILL.md').is_file()} "
          f"parent_is_skills_root={m._is_skills_root(d1.parent)} old_name_test={old_name_test(d1)}")
    r = m._is_installed_bundle(d1)
    print(f"  _is_installed_bundle(decoy1) = {r}   (must be False)")
    if r: fails.append("decoy1 (constellation-* with no SKILL.md in a marked root) ACCEPTED")
    if not old_name_test(d1): fails.append("decoy1 is not even a name-test positive; decoy invalid")
    if not m._is_skills_root(d1.parent): fails.append("decoy1 parent is not a skills root; clause 2 not exercised")

    # --- DECOY 2: same, but the root is a skills root by clause 2 (a real sibling bundle) ---
    root2 = tmp / "skills2"; root2.mkdir()
    sib = root2 / "constellation-real"; sib.mkdir()
    (sib / "SKILL.md").write_text("# real", encoding="utf-8", newline="\n")
    d2 = root2 / "constellation-decoy2"; d2.mkdir()
    print(f"decoy2 {d2}: has_SKILL_md={(d2/'SKILL.md').is_file()} "
          f"parent_is_skills_root={m._is_skills_root(d2.parent)} (no CORPUS.json: "
          f"{not (root2/'CORPUS.json').exists()}) old_name_test={old_name_test(d2)}")
    r2 = m._is_installed_bundle(d2)
    print(f"  _is_installed_bundle(decoy2) = {r2}   (must be False)")
    if r2: fails.append("decoy2 ACCEPTED")

    # --- DECOY 3: has SKILL.md but parent is NOT a skills root (lone dir) ---
    lone = tmp / "lonely" / "constellation-lonely"; lone.mkdir(parents=True)
    (lone / "SKILL.md").write_text("# lonely", encoding="utf-8", newline="\n")
    r3 = m._is_installed_bundle(lone)
    print(f"decoy3 {lone}: has_SKILL_md=True parent_is_skills_root={m._is_skills_root(lone.parent)} "
          f"old_name_test={old_name_test(lone)}")
    print(f"  _is_installed_bundle(decoy3) = {r3}   (must be False)")
    if r3: fails.append("decoy3 (SKILL.md but parent not a skills root) ACCEPTED")

    # --- POSITIVE CONTROL: a real bundle must still be ACCEPTED (guard can say yes) ---
    good = root / "constellation-good"; good.mkdir()
    (good / "SKILL.md").write_text("# good", encoding="utf-8", newline="\n")
    rg = m._is_installed_bundle(good)
    print(f"positive-control {good}: _is_installed_bundle = {rg}   (must be True)")
    if not rg: fails.append("positive control REJECTED -- guard cannot say yes; check-that-cannot-pass")

    # --- NAME-FREE ACCEPT: accepted bundle whose name is NOT constellation-* ---
    odd = root / "totally-unrelated-name"; odd.mkdir()
    (odd / "SKILL.md").write_text("# odd", encoding="utf-8", newline="\n")
    ro = m._is_installed_bundle(odd)
    print(f"name-free accept {odd}: old_name_test={old_name_test(odd)} _is_installed_bundle = {ro}   (must be True)")
    if not ro: fails.append("name-free bundle rejected -- predicate still consults the name")

print()
print("FAILURES:", fails if fails else "none")
sys.exit(1 if fails else 0)
