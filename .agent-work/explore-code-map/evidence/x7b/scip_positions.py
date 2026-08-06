"""Extract per-occurrence positions from index.scip for the x7b slice.

x1's edges.jsonl keeps only the start line, which is not enough to join an AST
name node to a SCIP occurrence. This re-decodes index.scip and keeps the full
range plus roles, restricted to the slice files.

Output: scip_occ.jsonl -- one line per occurrence in a slice file:
  {"file","line","c0","c1","symbol","roles","norm","origin"}
line/c0 are 0-based, exactly as SCIP emits them.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
X1 = os.path.join(os.path.dirname(HERE), "x1")
sys.path.insert(0, X1)

from decode_scip import iter_fields, unpack_varints, s  # noqa: E402

INDEX = os.path.join(X1, "index.scip")
PROJECT = "f1brainz"


def normalize(sym):
    """SCIP symbol string -> (norm, origin).

    origin: 'internal' | 'external' | 'local' | 'meta'
    norm for internal:  'src.utils.config:Config.load_config'
                        'src.utils.config:'   (the module itself)
    """
    if sym.startswith("local "):
        return sym, "local"
    parts = sym.split(" ", 4)
    if len(parts) < 5:
        return sym, "external"
    scheme, mgr, name, ver, desc = parts
    internal = (name == PROJECT)
    if not desc:
        return name, "external"
    # descriptor string: `src.utils.config`/Config#load_config().
    # split module prefix from member path
    if desc.startswith("`"):
        end = desc.find("`/", 1)
        if end == -1:
            mod = desc.strip("`/")
            rest = ""
        else:
            mod = desc[1:end]
            rest = desc[end + 2:]
    else:
        # src/__init__:  or  src/__version__.
        slash = desc.find("/")
        if slash == -1:
            mod, rest = desc, ""
        else:
            mod, rest = desc[:slash].replace("/", "."), desc[slash + 1:]
    members = []
    cur = ""
    for ch in rest:
        if ch in "#/":
            members.append(cur)
            cur = ""
        elif ch == ".":
            if cur:
                members.append(cur)
            cur = ""
        elif ch == "(":
            continue
        elif ch == ")":
            continue
        elif ch == ":":
            cur = cur  # meta marker (module __init__)
        else:
            cur += ch
    if cur:
        members.append(cur)
    # `mod`/__init__:  is the module itself (meta descriptor). A method named
    # __init__ is NOT -- keep it there.
    if desc.rstrip().endswith(":"):
        members = [m for m in members if m and m != "__init__"]
    else:
        members = [m for m in members if m]
    # scip-python quirk: an ANNOTATED module-level variable gets a doubled
    # descriptor -- `src.utils.constants`/F1_CALENDARS.F1_CALENDARS.
    # Unannotated ones do not. Collapse it so the comparison is fair.
    if len(members) == 2 and members[0] == members[1]:
        members = members[:1]
    norm = mod + ":" + ".".join(members)
    # scip-python files third-party symbols under the PROJECT name -- e.g.
    # `scip-python python f1brainz excursion-x1 `pandas.core.frame`/DataFrame#`.
    # Project membership is therefore decided by the module path, not the
    # package field.
    in_src = (mod == "src" or mod.startswith("src."))
    return norm, ("internal" if (internal and in_src) else "external")


def main(slice_files_path, out_path):
    want = set()
    with open(slice_files_path, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                want.add(ln.replace("/", "\\").lower())

    raw = open(INDEX, "rb").read()
    rows = []
    seen_files = set()
    for fn, wt, val in iter_fields(raw):
        if fn != 2 or wt != 2:
            continue
        relpath = None
        occs = []
        for dfn, dwt, dval in iter_fields(val):
            if dfn == 1 and dwt == 2:
                relpath = s(dval)
            elif dfn == 2 and dwt == 2:
                occs.append(dval)
        if relpath is None:
            continue
        key = relpath.replace("/", "\\").lower()
        if key not in want:
            continue
        seen_files.add(key)
        for obuf in occs:
            sym, roles, rng = None, 0, None
            for ofn, owt, oval in iter_fields(obuf):
                if ofn == 1:
                    rng = unpack_varints(oval) if owt == 2 else [oval]
                elif ofn == 2 and owt == 2:
                    sym = s(oval)
                elif ofn == 3 and owt == 0:
                    roles = oval
            if sym is None or not rng:
                continue
            if len(rng) == 3:
                line, c0, c1 = rng[0], rng[1], rng[2]
            elif len(rng) == 4:
                line, c0, c1 = rng[0], rng[1], rng[3]
            else:
                continue
            norm, origin = normalize(sym)
            rows.append({"file": relpath, "line": line, "c0": c0, "c1": c1,
                         "symbol": sym, "roles": roles,
                         "norm": norm, "origin": origin})
    with open(out_path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    missing = want - seen_files
    print("slice files wanted: %d  found in index: %d  missing: %d"
          % (len(want), len(seen_files), len(missing)))
    if missing:
        for m in sorted(missing)[:20]:
            print("  MISSING:", m)
    print("occurrences written: %d -> %s" % (len(rows), out_path))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
