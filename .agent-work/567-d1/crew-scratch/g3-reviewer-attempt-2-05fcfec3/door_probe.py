"""Fresh-process probe: does the live door emit the fragment the specs QUOTE?

The quote is read OUT OF THE SPECS (tomllib), never typed here, so this compares
the shipped text against the door rather than against a copy I retyped.
Usage: door_probe.py <repo-root> <path-to-mcp_spine_server.py> <tag>
"""
import json, os, pathlib, re, subprocess, sys, tomllib

ROOT = pathlib.Path(sys.argv[1]).resolve()
DOOR = pathlib.Path(sys.argv[2]).resolve()
TAG  = sys.argv[3]
WORK = ROOT / ".agent-work/567-d1/crew-scratch/g3-reviewer-attempt-2-05fcfec3/door-probe"
WORK.mkdir(parents=True, exist_ok=True)

def spine(name, work_id):
    p = WORK / (name + ".json")
    p.write_text(json.dumps({
        "work_id": work_id, "type": "gated", "items": ["g1"],
        "tasks": {"g1": {"id":"g1","title":"t","imperative":"do","preconditions":[],
                          "postconditions":[],"constraints":[],"directives":None,
                          "child_checklist":None,"status":"pending","status_detail":{},
                          "result":None,"finding":None,"evidence":[],"rework_count":0}},
        "consolidation": None, "triage_candidates": [], "blockers": [],
    }, indent=2))
    return p

A = spine("probe-a-" + TAG, "567-d1-g3r2" + TAG + "-a")
B = spine("probe-b-" + TAG, "567-d1-g3r2" + TAG + "-b")

def call(env, calls):
    script = (
        "import json, sys, importlib.util\n"
        "spec = importlib.util.spec_from_file_location('door', r'" + str(DOOR) + "')\n"
        "m = importlib.util.module_from_spec(spec); sys.modules['door']=m; spec.loader.exec_module(m)\n"
        "out=[]\n"
        "for name, args in " + repr(calls) + ":\n"
        "    try:\n"
        "        fn = m.call_lifecycle_tool if name in getattr(m,'LIFECYCLE_TOOL_NAMES',set()) else m.call_tool\n        out.append({'tool':name,'ok':True,'result':str(fn(name,args))})\n"
        "    except Exception as e:\n"
        "        out.append({'tool':name,'ok':False,'result':type(e).__name__+': '+str(e)})\n"
        "print('@@JSON@@'+json.dumps(out))\n"
    )
    e = dict(os.environ); e.pop("SPINE_FILE", None); e.pop("SPINE_SESSION", None)
    e.update(env)
    r = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, cwd=ROOT, env=e)
    tail = [l for l in r.stdout.splitlines() if l.startswith("@@JSON@@")]
    if not tail:
        return [{"tool":"<launch>","ok":False,"result":(r.stdout+r.stderr)[-3000:]}]
    return json.loads(tail[0][len("@@JSON@@"):])

frags = {}
for p in ["specs/implementer.spine.toml", "specs/reviewer.spine.toml"]:
    d = tomllib.load(open(ROOT/p, "rb"))
    q = re.findall(r'"([^"]*one door drives one spine[^"]*)"', d["gate"][0]["imperative"])
    assert len(q) == 1, (p, q)
    frags[p] = [s.strip() for s in q[0].split("...")]
print("QUOTE HALVES extracted from the specs:")
for k,v in frags.items(): print("  ", k, "->", v)
print("DOOR UNDER TEST:", DOOR)

print("\n=== CASE 1 bound-then-rebind (own lease held) -> expect REFUSED ===")
r1 = call({"SPINE_FILE": str(A), "SPINE_SESSION": "constellation/567-d1-g3r2" + TAG + "-a"},
          [("spine_lease", {"action":"claim","claimed_by":"reviewer"}),
           ("spine_bind",  {"spine_file": str(B)}),
           ("spine_status", {})])
for r in r1: print("  " + r["tool"] + ": ok=" + str(r["ok"]) + "\n    " + r["result"][:700].replace(chr(10), chr(10)+"    "))
refusal = r1[1]["result"]

print("\n=== CASE 2 released-then-rebind (POSITIVE CONTROL) -> expect SUCCESS ===")
r2 = call({"SPINE_FILE": str(A), "SPINE_SESSION": "constellation/567-d1-g3r2" + TAG + "-a"},
          [("spine_lease", {"action":"claim","claimed_by":"reviewer"}),
           ("spine_lease", {"action":"release"}),
           ("spine_bind",  {"spine_file": str(B)})])
for r in r2: print("  " + r["tool"] + ": ok=" + str(r["ok"]) + "\n    " + r["result"][:300].replace(chr(10), chr(10)+"    "))

print("\n=== CASE 3 unbound-then-bind -> status REFUSED, bind SUCCESS ===")
r3 = call({}, [("spine_status", {}), ("spine_bind", {"spine_file": str(B)})])
for r in r3: print("  " + r["tool"] + ": ok=" + str(r["ok"]) + "\n    " + r["result"][:400].replace(chr(10), chr(10)+"    "))

print("\n=== VERBATIM: each half of the specs quote vs the LIVE refusal ===")
allok = True
for p, halves in frags.items():
    for h in halves:
        hit = h in refusal; allok &= hit
        print("  " + p + ": " + repr(h) + " present=" + str(hit))
print("VERBATIM_OK=" + str(allok))
