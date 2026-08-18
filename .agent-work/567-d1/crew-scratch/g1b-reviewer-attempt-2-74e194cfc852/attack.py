"""r11: attack the widened verb arm. Plausible regrowth a future agent restoring
this doctrine would actually write."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(".").resolve() / "tests"))
import test_cli_retirement_guard as G
P = [("placeholder", G.ENGINE_PLACEHOLDER_RE), ("fallback", G.CLI_FALLBACK_RE),
     ("invocation", G.ENGINE_INVOCATION_RE), ("standin", G.ENGINE_STANDIN_COMMAND_RE)]

CASES = [
 # --- the rework's own new surface: `resume`
 ("resume, the pinned blocker",            "Second path: <cli> resume g1 --reason 'unblocked'."),
 ("resume, other dialect",                 "If blocked: {{engine}} resume g1 --reason 'unblocked'"),
 ("resume, env var form",                  "Then `$ENGINE resume g1 --reason 'unblocked'`"),
 ("resume, windows form",                  "%ENGINE% resume g1 --reason 'unblocked'"),
 ("resume, single brace",                  "fallback: {engine} resume g1"),
 # --- separator attacks on the widened arm
 ("tab separator",                         "Second path: <cli>\tresume g1 --reason 'x'."),
 ("double space",                          "Second path: <cli>  resume g1."),
 ("colon AFTER the stand-in",              "Second path: <cli>: resume g1 --reason 'x'."),
 ("NBSP separator (U+00A0)",               "Second path: <cli> resume g1."),
 ("narrow no-break space (U+202F)",        "Second path: <cli> resume g1."),
 ("em space (U+2003)",                     "Second path: <cli> resume g1."),
 ("quote between",                         'Second path: "<cli>" resume g1.'),
 ("backslash line continuation",           "Second path: <cli> \\\n  resume g1."),
 ("verb on the NEXT line (declared limit)","Second path: <cli>\nresume g1 --reason 'x'."),
 ("code span (declared limit)",            "Second path: `<cli>` resume g1."),
 # --- case / morphology
 ("capitalized verb",                      "Second path: <cli> Resume g1 --reason 'x'."),
 ("uppercase verb",                        "Second path: <cli> RESUME g1."),
 ("verb with trailing punctuation",        "Second path: <cli> resume, then heartbeat."),
 # --- dialect attacks (the upheld residual)
 ("[engine] bracket dialect",              "Second path: [engine] resume g1 --reason 'x'."),
 ("__ENGINE__ dunder dialect",             "Second path: __ENGINE__ resume g1."),
 ("$(engine) command substitution",        "Second path: $(engine) resume g1."),
 ("<<engine>> double angle",               "Second path: <<engine>> resume g1."),
 ("@engine sigil",                         "Second path: @engine resume g1."),
 ("(engine) parens",                       "Second path: (engine) resume g1."),
 # --- no-stand-in shapes (declared limit: hands over no program name)
 ("word-introduced, no stand-in",          "run the engine with resume g1 --reason 'x'"),
 ("bare program word",                     "engine resume g1 --reason 'unblocked'"),
 # --- honest text the widened arm might now red-light (false-alarm probes)
 ("HONEST: <work-id> resume prose",        "the `<work-id>` resume is written by the engine"),
 ("HONEST: bare <run> resume",             "after a crash the <run> resume picks up where it stopped"),
 ("HONEST: <gate> record",                 "the `<gate>` record names its own postconditions"),
 ("HONEST: <skill-dir> release notes",     "see <skill-dir> release notes for the change"),
 ("HONEST: <id> current state",            "the <id> current state is read from the journal"),
 ("HONEST: prohibition quoting it",        "NEVER write `<engine> claim` into a template"),
]
w = max(len(n) for n, _ in CASES)
for name, s in CASES:
    hits = [lbl for lbl, p in P if p.search(s)]
    mark = "CAUGHT" if hits else "MISS  "
    print(f"{mark} {name:<{w}} by {','.join(hits) or '-'}")
print()
caught = sum(1 for n, s in CASES if any(p.search(s) for _, p in P))
print(f"{caught}/{len(CASES)} caught")
