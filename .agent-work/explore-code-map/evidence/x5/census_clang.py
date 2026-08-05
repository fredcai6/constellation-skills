"""Clang-AST census of superCoolSpaceSim's C++ sources.

Purpose: produce the structural baseline (containers / transformers) that a
scip-clang run on Linux should be compared against, using the SAME compilation
database scip-clang would consume. Uses the libclang 18.1.1 Windows DLL bundled
in the PyPI `libclang` wheel -- no clang binary on this machine.

Reads:  evidence/x5/build/compile_commands.json
Writes: evidence/x5/census.json, evidence/x5/census_errors.txt
"""
import json
import os
import shlex
import sys
import time
from collections import Counter, defaultdict

EV = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(EV, "pylib"))

import clang.cindex as ci  # noqa: E402

ci.Config.set_library_file(os.path.join(EV, "pylib", "clang", "native", "libclang.dll"))

REPO_SRC = "c:\\programs\\supercoolspacesim\\src"

MINGW_INCLUDES = [
    "C:/msys64/ucrt64/include/c++/14.2.0",
    "C:/msys64/ucrt64/include/c++/14.2.0/x86_64-w64-mingw32",
    "C:/msys64/ucrt64/include/c++/14.2.0/backward",
    "C:/msys64/ucrt64/lib/gcc/x86_64-w64-mingw32/14.2.0/include",
    "C:/msys64/ucrt64/include",
    "C:/msys64/ucrt64/lib/gcc/x86_64-w64-mingw32/14.2.0/include-fixed",
]


def in_repo(cursor):
    loc = cursor.location
    if loc is None or loc.file is None:
        return False
    return os.path.abspath(loc.file.name).lower().startswith(REPO_SRC)


def tu_args(entry):
    """Turn a compile_commands entry into libclang arguments."""
    raw = shlex.split(entry["command"].replace("\\", "/"), posix=True)
    args, skip = [], False
    for i, a in enumerate(raw):
        if skip:
            skip = False
            continue
        if i == 0:  # the compiler itself
            continue
        if a in ("-o", "-c"):
            skip = True
            continue
        if a.endswith((".cpp", ".cc", ".c")):
            continue
        args.append(a)
    args += ["--target=x86_64-w64-windows-gnu", "-fsyntax-only"]
    for inc in MINGW_INCLUDES:
        args += ["-isystem", inc]
    return args


TRANSFORMER_KINDS = {
    ci.CursorKind.FUNCTION_DECL: "free function",
    ci.CursorKind.CXX_METHOD: "method",
    ci.CursorKind.CONSTRUCTOR: "constructor",
    ci.CursorKind.DESTRUCTOR: "destructor",
    ci.CursorKind.FUNCTION_TEMPLATE: "function template",
    ci.CursorKind.CONVERSION_FUNCTION: "conversion operator",
}
CONTAINER_KINDS = {
    ci.CursorKind.FIELD_DECL: "class field",
    ci.CursorKind.PARM_DECL: "parameter",
    ci.CursorKind.VAR_DECL: "variable",
    ci.CursorKind.ENUM_CONSTANT_DECL: "enum constant",
}
TYPE_KINDS = {
    ci.CursorKind.CLASS_DECL: "class",
    ci.CursorKind.STRUCT_DECL: "struct",
    ci.CursorKind.CLASS_TEMPLATE: "class template",
    ci.CursorKind.ENUM_DECL: "enum",
    ci.CursorKind.NAMESPACE: "namespace",
    ci.CursorKind.TYPEDEF_DECL: "typedef",
    ci.CursorKind.TYPE_ALIAS_DECL: "type alias",
}


def main():
    with open(os.path.join(EV, "build", "compile_commands.json")) as f:
        cdb = json.load(f)
    cdb = [e for e in cdb if "supercoolspacesim" in e["file"].lower()]

    index = ci.Index.create()
    seen = {}                       # USR -> kind label
    local_vars = set()              # (file, line, col) of function-local VAR_DECLs
    files_touched = set()
    calls = set()                   # (caller USR, callee USR)
    member_refs = 0
    errors = []
    parsed = parse_fail = 0
    t0 = time.time()

    for n, entry in enumerate(cdb, 1):
        args = tu_args(entry)
        src = entry["file"]
        try:
            tu = index.parse(src, args=args,
                             options=ci.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)
        except Exception as exc:  # noqa: BLE001
            parse_fail += 1
            errors.append(f"{src}: PARSE THREW {exc}")
            continue
        parsed += 1
        sev = [d for d in tu.diagnostics if d.severity >= 3]
        if sev:
            errors.append(f"{src}: {len(sev)} errors; first: {sev[0].spelling}")

        def walk(cursor, enclosing_fn=None):
            nonlocal member_refs
            k = cursor.kind
            if in_repo(cursor):
                files_touched.add(os.path.abspath(cursor.location.file.name).lower())
                usr = cursor.get_usr()
                if k in TRANSFORMER_KINDS:
                    if cursor.is_definition() and usr:
                        seen[usr] = TRANSFORMER_KINDS[k]
                    enclosing_fn = usr or enclosing_fn
                elif k in TYPE_KINDS:
                    if usr and (cursor.is_definition() or k == ci.CursorKind.NAMESPACE):
                        seen.setdefault(usr, TYPE_KINDS[k])
                elif k in CONTAINER_KINDS:
                    label = CONTAINER_KINDS[k]
                    if k == ci.CursorKind.VAR_DECL:
                        sk = cursor.semantic_parent.kind if cursor.semantic_parent else None
                        if sk in TRANSFORMER_KINDS:
                            loc = cursor.location
                            local_vars.add((loc.file.name.lower(), loc.line, loc.column))
                            label = None
                        else:
                            label = "module/class-level state"
                    if label and usr:
                        seen.setdefault(usr, label)
                elif k == ci.CursorKind.CALL_EXPR:
                    ref = cursor.referenced
                    if ref is not None and enclosing_fn:
                        ru = ref.get_usr()
                        if ru:
                            calls.add((enclosing_fn, ru))
                elif k == ci.CursorKind.MEMBER_REF_EXPR:
                    member_refs += 1
            for ch in cursor.get_children():
                walk(ch, enclosing_fn)

        sys.setrecursionlimit(20000)
        walk(tu.cursor)
        if n % 20 == 0:
            print(f"  [{n}/{len(cdb)}] {time.time()-t0:.0f}s", flush=True)

    counts = Counter(seen.values())
    transformers = sum(v for k, v in counts.items() if k in set(TRANSFORMER_KINDS.values()))
    named_containers = sum(v for k, v in counts.items()
                           if k in {"class field", "parameter",
                                    "module/class-level state", "enum constant"})

    out = {
        "compile_db_entries_total": 110,
        "compile_db_entries_in_repo": len(cdb),
        "tus_parsed": parsed,
        "tus_parse_threw": parse_fail,
        "tus_with_errors": len(errors),
        "wall_seconds": round(time.time() - t0, 1),
        "distinct_repo_files_touched": len(files_touched),
        "by_kind": dict(sorted(counts.items(), key=lambda x: -x[1])),
        "transformers_total": transformers,
        "named_containers_total": named_containers,
        "function_local_variables": len(local_vars),
        "distinct_caller_callee_pairs": len(calls),
        "member_ref_expressions": member_refs,
    }
    with open(os.path.join(EV, "census.json"), "w") as f:
        json.dump(out, f, indent=2)
    with open(os.path.join(EV, "census_errors.txt"), "w") as f:
        f.write("\n".join(errors))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
