"""Head-to-head: the map's curated container dependency edges vs the container
dependency graph derived purely from the SCIP index.

1. Parse index.md: container/component node yaml blocks (id -> path) and the
   Relationships yaml block (source/target/type).
2. From the SCIP index, for every occurrence of an internal (f1brainz) symbol,
   attribute the *referencing file* to a container and the *referenced symbol's
   module* to a container. Roll up to container->container edges.
3. Report: edges the map has that SCIP finds, edges SCIP finds that the map
   does not list, and edges the map lists that SCIP cannot see.
"""

import io, json, os, re, sys
from collections import Counter, defaultdict
from decode_scip import iter_fields, unpack_varints, s, classify_symbol, ROLE

INDEX = r"C:\Programs\f1Brainz\docs\architecture\index.md"
SCIP = sys.argv[1] if len(sys.argv) > 1 else "index.scip"

md = io.open(INDEX, encoding="utf-8").read()

# ---- 1. node yaml blocks ---------------------------------------------------
blocks = re.findall(r"```yaml\n(.*?)```", md, re.S)
nodes = {}
edges = []
for b in blocks:
    if b.lstrip().startswith("- source:"):
        for m in re.finditer(r"- source:\s*(\S+)\s*\n\s*target:\s*(\S+)\s*\n\s*type:\s*(\S+)", b):
            edges.append(m.groups())
        continue
    d = {}
    for line in b.splitlines():
        m = re.match(r"\s*(\w+):\s*(.*)", line)
        if m:
            d[m.group(1)] = m.group(2).strip().strip('"')
    if "id" in d:
        nodes[d["id"]] = d

containers = {i: n for i, n in nodes.items()
              if n.get("level") == "container" and n.get("path", "").startswith("src/")}
components = {i: n for i, n in nodes.items() if n.get("level") == "component"}

# path prefix -> container id
prefix = {}
for cid, n in containers.items():
    prefix[n["path"].rstrip("/").replace("/", ".")] = cid   # e.g. src.data


def container_of_module(mod):
    # mod like 'src.data.database._core'
    parts = mod.split(".")
    for k in range(len(parts), 0, -1):
        cand = ".".join(parts[:k])
        if cand in prefix:
            return prefix[cand]
    return None


# ---- 2. SCIP-derived container graph --------------------------------------
raw = open(SCIP, "rb").read()
docs = [v for fn, wt, v in iter_fields(raw) if fn == 2 and wt == 2]

scip_edges = Counter()
scip_edge_evidence = defaultdict(set)
for dbuf in docs:
    relpath, occs = None, []
    for fn, wt, val in iter_fields(dbuf):
        if fn == 1 and wt == 2:
            relpath = s(val)
        elif fn == 2 and wt == 2:
            occs.append(val)
    if not relpath:
        continue
    from_mod = relpath.replace("\\", "/")[:-3].replace("/", ".")
    src_c = container_of_module(from_mod)
    if not src_c:
        continue
    for obuf in occs:
        sym, roles = None, 0
        for fn, wt, val in iter_fields(obuf):
            if fn == 2 and wt == 2:
                sym = s(val)
            elif fn == 3 and wt == 0:
                roles = val
        if not sym or (roles & ROLE["Definition"]):
            continue
        if " f1brainz " not in sym:
            continue
        parts = sym.split(" ", 4)
        if len(parts) < 5:
            continue
        mod = parts[4].split("/")[0].strip("`")
        tgt_c = container_of_module(mod)
        if tgt_c and tgt_c != src_c:
            scip_edges[(src_c, tgt_c)] += 1
            if len(scip_edge_evidence[(src_c, tgt_c)]) < 3:
                scip_edge_evidence[(src_c, tgt_c)].add(relpath)

# ---- 3. compare -----------------------------------------------------------
map_pairs = set()
map_pairs_srconly = set()
for a, b, t in edges:
    map_pairs.add((a, b))
    if a in containers and b in containers:
        map_pairs_srconly.add((a, b))

scip_pairs = set(scip_edges)

both = map_pairs_srconly & scip_pairs
map_only = map_pairs_srconly - scip_pairs
scip_only = scip_pairs - map_pairs_srconly
non_src_targets = map_pairs - map_pairs_srconly

out = {
    "map_container_nodes": len(containers),
    "map_component_nodes": len(components),
    "map_total_yaml_nodes": len(nodes),
    "map_relationship_edges_total": len(edges),
    "map_edge_types": dict(Counter(t for _, _, t in edges)),
    "map_edges_between_two_src_containers": len(map_pairs_srconly),
    "map_edges_touching_external_or_non_src_node": len(non_src_targets),
    "scip_derived_container_edges": len(scip_pairs),
    "agreement_map_edge_confirmed_by_scip": len(both),
    "map_edges_scip_cannot_see": sorted(map_only),
    "scip_edges_absent_from_map": sorted(scip_only)[:40],
    "scip_edges_absent_from_map_count": len(scip_only),
    "confirmed_edges": sorted(both),
    "external_or_non_src_map_edges": sorted(non_src_targets),
    "top_scip_edges_by_occurrence": [[a, b, n] for (a, b), n in scip_edges.most_common(15)],
}
json.dump(out, open("edge_compare.json", "w", encoding="utf-8"), indent=2)
print(json.dumps(out, indent=2)[:7000])
