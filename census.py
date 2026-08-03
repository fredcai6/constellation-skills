"""exc-8 census: segment the Commander's always-loaded surface into paragraph
units and score a classification.

Method (stated so it is reproducible):
  * Sources are the ORIGINAL files at `main`, not this worktree's edited copies.
  * A "unit" is a markdown block: a run of consecutive non-blank lines. A
    heading line is its own unit and is counted; table rows collapse into the
    single table unit they belong to; fenced code is kept whole.
  * Each unit gets exactly one class, assigned by hand in CLASSES below:
      S = step-specific     -> relocatable to a named gate; cite the gate
      A = always-needed     -> spine-use trigger / role identity / project focus
      R = reference-on-demand -> consulted at need, not carried in context
  * Shares are reported over words and bytes of unit text.

Usage:
  python census.py segment            # print numbered units to classify
  python census.py report             # print the classified census
"""
import collections
import pathlib
import re
import subprocess
import sys

SOURCES = [
    "skills/commander/SKILL.md",
    "skills/commander/references/commander-core.md",
    "skills/commander/references/crew-dispatch.md",
]

ROOT = pathlib.Path(__file__).parent


def units():
    """Yield (source, index, text) for every paragraph unit, read from `main`."""
    out = []
    for src in SOURCES:
        text = subprocess.run(
            ["git", "show", f"main:{src}"],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True,
        ).stdout
        # strip YAML frontmatter (metadata, not prose)
        text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)
        blocks, buf, in_fence = [], [], False
        for line in text.splitlines():
            if line.strip().startswith("```"):
                in_fence = not in_fence
            if not line.strip() and not in_fence:
                if buf:
                    blocks.append("\n".join(buf))
                    buf = []
            else:
                buf.append(line)
        if buf:
            blocks.append("\n".join(buf))
        # A block that is a top-level LIST is split per item: its items are
        # separately-relocatable instructions (the "Start here" 1-5 list and the
        # delegated-mode bullets each span several destination steps). Tables
        # (lines starting `|`) and fenced code stay whole.
        split = []
        for b in blocks:
            lines = b.splitlines()
            is_table = all(l.lstrip().startswith("|") for l in lines if l.strip())
            has_items = any(re.match(r"^(\d+\.|[-*])\s", l) for l in lines)
            if is_table or not has_items or "```" in b:
                split.append(b)
                continue
            cur = []
            for l in lines:
                if re.match(r"^(\d+\.|[-*])\s", l) and cur:
                    split.append("\n".join(cur))
                    cur = [l]
                else:
                    cur.append(l)
            if cur:
                split.append("\n".join(cur))
        for i, b in enumerate(split, 1):
            out.append((src, i, b))
    return out


# ---------------------------------------------------------------------------
# Hand classification. Key is "<file-short>:<unit index>".
#   S:<gate>  step-specific, relocatable to that spine step
#   A         always-needed
#   R         reference-on-demand
# ---------------------------------------------------------------------------
CLASSES = {
    # ---- SKILL.md — the literally always-loaded file ----
    "SKILL:1": "A", "SKILL:2": "A", "SKILL:3": "A",
    "SKILL:4": "A", "SKILL:5": "A", "SKILL:6": "A",

    # ---- commander-core.md ----
    "CORE:1": "A",            # H1
    "CORE:2": "A",            # mode-neutral framing + principal binding
    "CORE:3": "R",            # "Contents" heading
    **{f"CORE:{i}": "R" for i in range(4, 15)},   # TOC entries
    "CORE:15": "A",           # "Role" heading
    "CORE:16": "A",           # role identity, rigor scaffold, force decisions
    "CORE:17": "A",           # you own the run; drive every step through the engine
    "CORE:18": "A",           # "Start here" heading
    "CORE:19": "A",           # BOOTSTRAP: fires before any engine call exists
    "CORE:20": "A",           # BOOTSTRAP: instantiate spine + claim lease
    "CORE:21": "A",           # THE spine-use trigger: ask `current` at every step
    "CORE:22": "S:execute",   # deliverables come out of the spine
    "CORE:23": "S:execute",   # solution is the MIDDLE; closeout ordering
    "CORE:24": "S:execute",   # dispatching a crew is not a reason to end your turn
    "CORE:25": "A",           # work the engine never saw did not happen
    "CORE:26": "R", "CORE:27": "R", "CORE:28": "R",   # checklists-you-own + table
    "CORE:29": "S:execute",   # execute.json never hand-edited; amend/reopen
    "CORE:30": "R",           # "How it works" heading
    "CORE:31": "A",           # drive the spine one step at a time
    "CORE:32": "R",           # step/where-it-runs table (duplicates the spine)
    "CORE:33": "S:understand",  # shaped-design intake
    "CORE:34": "S:understand",  # feasibility probe
    "CORE:35": "S:understand",  # prototyper escape hatch
    "CORE:36": "S:execute", "CORE:37": "S:execute",
    "CORE:38": "S:execute",   # gN-implement  <-- THE TRACER
    "CORE:39": "S:execute", "CORE:40": "S:execute",
    "CORE:41": "S:execute", "CORE:42": "S:execute",
    "CORE:43": "S:plan",      # crew gate vs reasoning gate (authored at plan)
    "CORE:44": "S:plan",      # doc-only gates pre-author invariant chain
    "CORE:45": "S:execute",   # closeout checks are postconditions; waive
    "CORE:46": "S:execute",   # pick model tier
    "CORE:47": "R",           # pointer to crew-dispatch.md
    "CORE:48": "A", "CORE:49": "A",     # Repo / project focus
    "CORE:50": "A", "CORE:51": "A",     # human checkpoints (spans 4 steps)
    "CORE:52": "A", "CORE:53": "A", "CORE:54": "A",   # Modes framing
    "CORE:55": "S:understand",  # delegated understand
    "CORE:56": "A",           # four user-decision checkpoints (spans 4 steps)
    "CORE:57": "A",           # reach-up, any step
    "CORE:58": "A",           # trip vs query, any step
    "CORE:59": "A",           # interactive runs unchanged
    "CORE:60": "S:plan",      # "Decision candidates" heading
    "CORE:61": "A",           # candidates span plan/execute/reconcile
    "CORE:62": "A",           # fixedness tier spans plan/reconcile/downstream
    "CORE:63": "S:plan", "CORE:64": "S:plan", "CORE:65": "S:plan",
    "CORE:66": "S:plan",
    "CORE:67": "A",           # SendMessage rule spans plan critics + execute crews
    "CORE:68": "S:plan", "CORE:69": "S:plan", "CORE:70": "S:plan",
    "CORE:71": "S:plan",
    "CORE:72": "A", "CORE:73": "A",     # architecture bookend spans the run
    "CORE:74": "S:reconcile",
    "CORE:75": "R", "CORE:76": "R",     # templates pointers

    # ---- crew-dispatch.md — pointer-loaded, not carried by default ----
    "DISPATCH:1": "R", "DISPATCH:2": "R",
    "DISPATCH:3": "S:execute", "DISPATCH:4": "S:execute", "DISPATCH:5": "S:execute",
    "DISPATCH:6": "R", "DISPATCH:7": "R", "DISPATCH:8": "R", "DISPATCH:9": "R",
    "DISPATCH:10": "S:execute",
    "DISPATCH:11": "R",
    "DISPATCH:12": "S:execute", "DISPATCH:13": "S:execute",
    "DISPATCH:14": "S:execute", "DISPATCH:15": "S:execute",
}

SHORT = {
    "skills/commander/SKILL.md": "SKILL",
    "skills/commander/references/commander-core.md": "CORE",
    "skills/commander/references/crew-dispatch.md": "DISPATCH",
}


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "report"
    us = units()

    if mode == "segment":
        for src, i, b in us:
            key = f"{SHORT[src]}:{i}"
            first = b.splitlines()[0][:110]
            print(f"{key:14} w={len(b.split()):4} b={len(b.encode()):5} | {first}")
        print(f"\nTOTAL UNITS: {len(us)}")
        return 0

    # report
    missing = [f"{SHORT[s]}:{i}" for s, i, _ in us if f"{SHORT[s]}:{i}" not in CLASSES]
    if missing:
        print("UNCLASSIFIED UNITS (census incomplete):", missing)
        return 1

    per_file = collections.defaultdict(lambda: collections.Counter())
    tot = collections.Counter()
    words = collections.Counter()
    byts = collections.Counter()
    gates = collections.Counter()
    for src, i, b in us:
        cls = CLASSES[f"{SHORT[src]}:{i}"]
        head = cls[0]
        per_file[SHORT[src]][head] += 1
        tot[head] += 1
        words[head] += len(b.split())
        byts[head] += len(b.encode())
        if head == "S":
            gates[cls.split(":", 1)[1]] += len(b.split())

    W, B, U = sum(words.values()), sum(byts.values()), sum(tot.values())
    print(f"CENSUS — Commander always-loaded surface ({len(SOURCES)} files, {U} units, "
          f"{W} words, {B} bytes)\n")
    label = {"S": "step-specific (relocatable)", "A": "always-needed",
             "R": "reference-on-demand"}
    print(f"{'class':<30}{'units':>7}{'unit%':>8}{'words':>8}{'word%':>8}{'bytes':>8}{'byte%':>8}")
    for k in ("S", "A", "R"):
        print(f"{label[k]:<30}{tot[k]:>7}{100*tot[k]/U:>7.1f}%{words[k]:>8}"
              f"{100*words[k]/W:>7.1f}%{byts[k]:>8}{100*byts[k]/B:>7.1f}%")
    print(f"{'TOTAL':<30}{U:>7}{100:>7.1f}%{W:>8}{100:>7.1f}%{B:>8}{100:>7.1f}%")

    print("\nPer file (unit counts):")
    for f in ("SKILL", "CORE", "DISPATCH"):
        c = per_file[f]
        n = sum(c.values())
        print(f"  {f:<10} units={n:<4} S={c['S']:<4} A={c['A']:<4} R={c['R']:<4}")

    print("\nStep-specific words by destination gate:")
    for g, w in gates.most_common():
        print(f"  {g:<12} {w:>5} words  ({100*w/W:.1f}% of surface)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
