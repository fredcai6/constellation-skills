"""Validation: does centrality predict what f1Brainz's curated map chose to name?

Ground truth = the identifiers that docs/architecture/{index.md,packets/*.md,
overlays/*.yml} actually mention. Compares hit-rate in the top-K central entities
against the base rate over all graph nodes (the random-draw baseline).
"""
import json
import re
import random
from pathlib import Path

X4 = Path(r"C:\Programs\constellation-skills\.claude\worktrees\explore-code-map\.agent-work\explore-code-map\evidence\x4")
DOCS = Path(r"C:\Programs\f1Brainz\docs\architecture")

IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def load_map_text():
    parts, files = [], []
    for p in [DOCS / "index.md"] + sorted((DOCS / "packets").glob("*.md")) + sorted((DOCS / "overlays").glob("*.yml")):
        parts.append(p.read_text(encoding="utf-8", errors="replace"))
        files.append(p.name)
    return "\n".join(parts), files


def extract_mentions(text):
    """Identifiers the map names. Only counts tokens inside backticks or inside a
    dotted path, so ordinary English prose cannot create a false hit."""
    code_spans = re.findall(r"`([^`]+)`", text)
    dotted = re.findall(r"\b(?:src\.)?[a-z_][a-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)+\b", text)
    tokens, paths = set(), set()
    for span in code_spans + dotted:
        for t in IDENT.findall(span):
            tokens.add(t)
        for m in re.finditer(r"[A-Za-z_][A-Za-z0-9_.]*", span):
            s = m.group(0).strip(".")
            if "." in s:
                paths.add(s)
                paths.add(s[4:] if s.startswith("src.") else "src." + s)
    return tokens, paths


def module_mentioned(module, tokens, paths):
    """True if the map names this module: full dotted path, or its file stem as a token."""
    if module in paths:
        return True
    stem = module.rsplit(".", 1)[-1]
    for p in paths:
        if p.endswith("." + stem) or p == module:
            return True
    return stem in tokens


def leaf_mentioned(qual, tokens):
    return qual.rsplit(".", 1)[-1] in tokens


def main():
    rows = json.loads((X4 / "centrality.json").read_text(encoding="utf-8"))
    mrows = json.loads((X4 / "centrality_modules.json").read_text(encoding="utf-8"))
    text, files = load_map_text()
    tokens, paths = extract_mentions(text)
    print(f"map files read: {len(files)}  chars={len(text)}  code-tokens={len(tokens)}  dotted-paths={len(paths)}")

    for r in rows:
        r["leaf_hit"] = leaf_mentioned(r["qual"], tokens)
        r["mod_hit"] = module_mentioned(r["module"], tokens, paths)
    for r in mrows:
        r["mod_hit"] = module_mentioned(r["module"], tokens, paths)

    n = len(rows)
    base_leaf = sum(r["leaf_hit"] for r in rows) / n
    base_mod = sum(r["mod_hit"] for r in rows) / n
    print(f"\nPOPULATION: {n} symbol nodes")
    print(f"  base rate, entity's own name named by the map : {base_leaf:.1%}")
    print(f"  base rate, entity's module named by the map   : {base_mod:.1%}")

    print("\n=== SYMBOL-LEVEL PageRank vs curated map ===")
    print(f"{'K':>5} {'own-name hits':>14} {'rate':>7} {'lift':>6} | {'module hits':>12} {'rate':>7} {'lift':>6}")
    for K in (10, 20, 30, 50, 100):
        top = rows[:K]
        lh = sum(r["leaf_hit"] for r in top); mh = sum(r["mod_hit"] for r in top)
        print(f"{K:>5} {lh:>14} {lh/K:>7.1%} {lh/K/base_leaf:>6.2f}x | {mh:>12} {mh/K:>7.1%} {mh/K/base_mod:>6.2f}x")

    ranked_auth = sorted(rows, key=lambda r: -r["authority"])
    print("\n=== SYMBOL-LEVEL HITS-authority vs curated map ===")
    for K in (10, 20, 30):
        top = ranked_auth[:K]
        lh = sum(r["leaf_hit"] for r in top)
        print(f"{K:>5} {lh:>14} {lh/K:>7.1%} {lh/K/base_leaf:>6.2f}x")

    ranked_deg = sorted(rows, key=lambda r: -r["in_degree"])
    print("\n=== SYMBOL-LEVEL raw in-degree (control) vs curated map ===")
    for K in (10, 20, 30):
        top = ranked_deg[:K]
        lh = sum(r["leaf_hit"] for r in top)
        print(f"{K:>5} {lh:>14} {lh/K:>7.1%} {lh/K/base_leaf:>6.2f}x")

    nm = len(mrows)
    base_m = sum(r["mod_hit"] for r in mrows) / nm
    print(f"\n=== MODULE-LEVEL PageRank vs curated map ===  population={nm}, base={base_m:.1%}")
    for K in (10, 20, 30, 50):
        top = mrows[:K]
        h = sum(r["mod_hit"] for r in top)
        print(f"{K:>5} {h:>3} hits {h/K:>7.1%} lift={h/K/base_m:>5.2f}x")

    # empirical random baseline, to sanity-check the analytic base rate
    random.seed(0)
    trials = [sum(r["leaf_hit"] for r in random.sample(rows, 30)) / 30 for _ in range(2000)]
    trials.sort()
    print(f"\nrandom 30-draw (symbol, own-name): mean={sum(trials)/len(trials):.1%} "
          f"p95={trials[int(.95*len(trials))]:.1%} max={trials[-1]:.1%}")
    mtrials = [sum(r["mod_hit"] for r in random.sample(mrows, 30)) / 30 for _ in range(2000)]
    mtrials.sort()
    print(f"random 30-draw (module): mean={sum(mtrials)/len(mtrials):.1%} p95={mtrials[int(.95*len(mtrials))]:.1%}")

    print("\n=== TOP 30 SYMBOLS, hit detail ===")
    for r in rows[:30]:
        print(f"{r['pr_rank']:3d} pr={r['pagerank']:.5f} own={'HIT ' if r['leaf_hit'] else '--- '} "
              f"mod={'HIT ' if r['mod_hit'] else '--- '} doc={'Y' if r['has_docstring'] else 'N'} "
              f"{r['module']}.{r['qual']}")

    json.dump(rows, open(X4 / "centrality_scored.json", "w", encoding="utf-8"), indent=1)
    json.dump(mrows, open(X4 / "centrality_modules_scored.json", "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
