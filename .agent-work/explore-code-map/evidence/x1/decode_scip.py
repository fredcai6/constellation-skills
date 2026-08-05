"""Minimal pure-Python SCIP protobuf decoder.

No protoc, no protobuf runtime. Parses only the fields we need, straight off
the wire format, using the SCIP schema (sourcegraph/scip scip.proto).

Index          { 1: Metadata, 2: repeated Document, 3: repeated SymbolInformation }
Metadata       { 1: version, 2: ToolInfo, 3: project_root, 4: text_document_encoding }
Document       { 1: relative_path, 2: repeated Occurrence, 3: repeated SymbolInformation,
                 4: language, 5: text }
Occurrence     { 1: repeated int32 range, 2: symbol, 3: symbol_roles, 5: syntax_kind,
                 7: repeated int32 enclosing_range }
SymbolInformation { 1: symbol, 3: repeated documentation, 4: repeated Relationship,
                 5: kind, 6: display_name, 8: enclosing_symbol }

Usage:  python decode_scip.py index.scip
"""

import sys
import json
import os
from collections import Counter, defaultdict


# ---------------------------------------------------------------- wire format

def read_varint(buf, i):
    result = 0
    shift = 0
    while True:
        b = buf[i]
        i += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            return result, i
        shift += 7


def iter_fields(buf, start=0, end=None):
    """Yield (field_number, wire_type, value) where value is bytes for wt=2,
    int for wt=0."""
    if end is None:
        end = len(buf)
    i = start
    while i < end:
        key, i = read_varint(buf, i)
        fn, wt = key >> 3, key & 7
        if wt == 0:
            val, i = read_varint(buf, i)
            yield fn, wt, val
        elif wt == 2:
            ln, i = read_varint(buf, i)
            yield fn, wt, buf[i:i + ln]
            i += ln
        elif wt == 5:
            yield fn, wt, buf[i:i + 4]
            i += 4
        elif wt == 1:
            yield fn, wt, buf[i:i + 8]
            i += 8
        else:
            raise ValueError("unsupported wire type %d at %d" % (wt, i))


def unpack_varints(b):
    out, i = [], 0
    while i < len(b):
        v, i = read_varint(b, i)
        out.append(v)
    return out


def s(b):
    return b.decode("utf-8", "replace")


# ---------------------------------------------------------------- SCIP enums

# scip.proto SymbolRole bitmask
ROLE = {
    "Definition": 0x1,
    "Import": 0x2,
    "WriteAccess": 0x4,
    "ReadAccess": 0x8,
    "Generated": 0x10,
    "Test": 0x20,
    "ForwardDefinition": 0x40,
}


# ------------------------------------------------ SCIP symbol-string grammar
# <scheme> ' ' <manager> ' ' <name> ' ' <version> ' ' <descriptor>+
# descriptor suffixes: foo/ Namespace | foo# Type | foo. Term | foo(). Method
#                      [foo] TypeParameter | (foo) Parameter | foo: Meta
# locals are the whole symbol: "local <n>"

def classify_symbol(sym):
    """Return (kind, last_descriptor) derived from the SCIP symbol string alone."""
    if sym.startswith("local "):
        return "local", sym
    # descriptors begin after the 4 space-separated header fields
    parts = sym.split(" ", 4)
    if len(parts) < 5:
        return "malformed", sym
    desc = parts[4]
    if not desc:
        return "package", ""
    d = desc.rstrip()
    if d.endswith(")."):
        return "method", d
    if d.endswith("."):
        return "term", d
    if d.endswith("#"):
        return "type", d
    if d.endswith("/"):
        return "namespace", d
    if d.endswith("]"):
        return "typeparam", d
    if d.endswith(")"):
        return "parameter", d
    if d.endswith(":"):
        return "meta", d
    return "other", d


def is_local_project(sym, project_name):
    # scip-python emits "scip-python python <project> <version> <descriptors>"
    return (" %s " % project_name) in sym[:120]


# ---------------------------------------------------------------- main parse

def main(path, project_name="f1brainz"):
    raw = open(path, "rb").read()
    print("index bytes: %d" % len(raw))

    docs = []
    external = 0
    metadata = {}

    for fn, wt, val in iter_fields(raw):
        if fn == 1 and wt == 2:
            for mfn, mwt, mval in iter_fields(val):
                if mfn == 3:
                    metadata["project_root"] = s(mval)
                elif mfn == 2:
                    for tfn, twt, tval in iter_fields(mval):
                        if tfn == 1:
                            metadata["tool"] = s(tval)
                        elif tfn == 2:
                            metadata["tool_version"] = s(tval)
        elif fn == 2 and wt == 2:
            docs.append(val)
        elif fn == 3 and wt == 2:
            external += 1

    print("metadata: %s" % metadata)
    print("documents: %d   external_symbols: %d" % (len(docs), external))

    # -------------------------------------------------------------- tallies
    sym_kind = Counter()              # kind of every *defined* symbol
    sym_kind_all = Counter()          # kind of every symbol mentioned in occurrences
    role_counts = Counter()
    docstring_present = Counter()     # kind -> count with non-empty documentation
    docstring_absent = Counter()
    per_doc = []
    defs_by_symbol = {}               # symbol -> (relpath, kind, display_name, has_doc)
    occ_role_by_kind = defaultdict(Counter)
    # read/write edges: (enclosing definition symbol) -> accessed symbol
    edge_rows = []
    local_symbols = set()
    relationship_count = 0
    enclosing_symbol_count = 0
    signature_doc_count = 0

    samples = defaultdict(list)

    for dbuf in docs:
        relpath = None
        occurrences = []
        symbols = []
        for fn, wt, val in iter_fields(dbuf):
            if fn == 1 and wt == 2:
                relpath = s(val)
            elif fn == 2 and wt == 2:
                occurrences.append(val)
            elif fn == 3 and wt == 2:
                symbols.append(val)

        n_def = 0
        # ---- SymbolInformation (the "definition table" for this file)
        for sbuf in symbols:
            sym = None
            doc_lines = []
            kind_enum = None
            display = None
            enclosing = None
            for fn, wt, val in iter_fields(sbuf):
                if fn == 1 and wt == 2:
                    sym = s(val)
                elif fn == 3 and wt == 2:
                    doc_lines.append(s(val))
                elif fn == 4 and wt == 2:
                    relationship_count += 1
                elif fn == 5 and wt == 0:
                    kind_enum = val
                elif fn == 6 and wt == 2:
                    display = s(val)
                elif fn == 7 and wt == 2:
                    signature_doc_count += 1
                elif fn == 8 and wt == 2:
                    enclosing = s(val)
                    enclosing_symbol_count += 1
            if sym is None:
                continue
            kind, desc = classify_symbol(sym)
            sym_kind[kind] += 1
            n_def += 1
            # documentation[0] for scip-python is usually the signature/type;
            # a real docstring shows up as an extra entry or a ```...``` block.
            has_doc = _has_real_docstring(doc_lines)
            if has_doc:
                docstring_present[kind] += 1
            else:
                docstring_absent[kind] += 1
            defs_by_symbol[sym] = (relpath, kind, display, has_doc)
            if len(samples[kind]) < 6:
                samples[kind].append({
                    "file": relpath, "symbol": sym, "kind_enum": kind_enum,
                    "display_name": display, "enclosing_symbol": enclosing,
                    "documentation": doc_lines[:4],
                })

        # ---- Occurrences (the reference/read/write edges)
        n_occ = 0
        for obuf in occurrences:
            sym = None
            roles = 0
            rng = None
            enclosing_rng = None
            for fn, wt, val in iter_fields(obuf):
                if fn == 1:
                    rng = unpack_varints(val) if wt == 2 else [val]
                elif fn == 2 and wt == 2:
                    sym = s(val)
                elif fn == 3 and wt == 0:
                    roles = val
                elif fn == 7:
                    enclosing_rng = unpack_varints(val) if wt == 2 else [val]
            if sym is None:
                continue
            n_occ += 1
            kind, _ = classify_symbol(sym)
            sym_kind_all[kind] += 1
            if kind == "local":
                local_symbols.add((relpath, sym))
            for name, bit in ROLE.items():
                if roles & bit:
                    role_counts[name] += 1
                    occ_role_by_kind[kind][name] += 1
            if roles & (ROLE["ReadAccess"] | ROLE["WriteAccess"]):
                edge_rows.append({
                    "file": relpath,
                    "symbol": sym,
                    "kind": kind,
                    "role": ("write" if roles & ROLE["WriteAccess"] else "read"),
                    "line": rng[0] if rng else None,
                    "has_enclosing_range": enclosing_rng is not None,
                })
            if roles == 0:
                role_counts["<no role: plain reference>"] += 1

        per_doc.append((relpath, n_def, n_occ))

    out = {
        "metadata": metadata,
        "documents": len(docs),
        "external_symbols": external,
        "defined_symbols_by_kind": dict(sym_kind.most_common()),
        "occurrence_symbols_by_kind": dict(sym_kind_all.most_common()),
        "occurrence_roles": dict(role_counts.most_common()),
        "roles_by_symbol_kind": {k: dict(v) for k, v in occ_role_by_kind.items()},
        "docstring_present_by_kind": dict(docstring_present.most_common()),
        "docstring_absent_by_kind": dict(docstring_absent.most_common()),
        "relationship_fields": relationship_count,
        "enclosing_symbol_fields": enclosing_symbol_count,
        "signature_documentation_fields": signature_doc_count,
        "distinct_local_symbols": len(local_symbols),
        "read_write_occurrences": len(edge_rows),
        "samples": {k: v for k, v in samples.items()},
        "top_files_by_defs": sorted(per_doc, key=lambda r: -r[1])[:15],
    }

    outdir = os.path.dirname(os.path.abspath(path))
    with open(os.path.join(outdir, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    with open(os.path.join(outdir, "edges.jsonl"), "w", encoding="utf-8") as f:
        for r in edge_rows:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(outdir, "defs.jsonl"), "w", encoding="utf-8") as f:
        for sym, (rp, kind, disp, hd) in defs_by_symbol.items():
            f.write(json.dumps({"symbol": sym, "file": rp, "kind": kind,
                                "display_name": disp, "has_docstring": hd}) + "\n")

    print(json.dumps({k: v for k, v in out.items() if k != "samples"}, indent=2)[:6000])
    print("\nwrote summary.json, edges.jsonl, defs.jsonl to %s" % outdir)


def _has_real_docstring(doc_lines):
    """scip-python puts the rendered signature in documentation[0] as a
    ```python ...``` fence. A prose docstring appears as additional text
    beyond that fence."""
    if not doc_lines:
        return False
    joined = "\n".join(doc_lines)
    # strip fenced code blocks; whatever prose remains is the docstring
    parts = joined.split("```")
    prose = "".join(parts[i] for i in range(0, len(parts), 2))
    return len(prose.strip()) > 0


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "index.scip")
