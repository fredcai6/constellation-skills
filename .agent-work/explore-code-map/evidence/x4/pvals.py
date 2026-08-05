import json, random
from pathlib import Path
X4 = Path(r"C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\evidence\x4")
rows = json.loads((X4/"centrality_scored.json").read_text(encoding="utf-8"))
def is_private(r): return any(p.startswith("_") and not p.startswith("__") for p in r["qual"].split("."))
pub=[r for r in rows if not is_private(r)]
random.seed(7); N=20000
def pval(pool, key, K):
    top=sorted(pool,key=key)[:K]; obs=sum(r["leaf_hit"] for r in top)
    draws=[sum(r["leaf_hit"] for r in random.sample(pool,K)) for _ in range(N)]
    p=sum(1 for d in draws if d>=obs)/N
    return obs, obs/K, p
print(f"{'signal':28} {'pool':7} {'K':>3} {'hits':>5} {'rate':>7} {'p(>=obs)':>9}")
for name,pool,key in [("PageRank",rows,lambda r:-r["pagerank"]),
                      ("PageRank",pub,lambda r:-r["pagerank"]),
                      ("in-degree",pub,lambda r:-r["in_degree"]),
                      ("in-weight (call count)",pub,lambda r:-r["in_weight"]),
                      ("HITS authority",rows,lambda r:-r["authority"])]:
    lbl="public" if pool is pub else "all"
    for K in (10,20,30):
        o,rate,p=pval(pool,key,K)
        star=" *" if p<0.05 else ""
        print(f"{name:28} {lbl:7} {K:>3} {o:>5} {rate:>7.1%} {p:>9.4f}{star}")
