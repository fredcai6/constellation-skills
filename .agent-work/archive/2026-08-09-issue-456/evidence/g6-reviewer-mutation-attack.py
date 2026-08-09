"""g6 review, question 3: attack span_hash's reformatting immunity with
mutations the crew did NOT choose. Predict before running; each pair is
(name, prediction, source_a, source_b)."""
import ast
import sys
sys.path.insert(0, ".")
from scripts.code_map import extract


def h(src):
    node = ast.parse(src).body[0]
    return extract.span_hash(node)


CASES = [
    ("quote-style",
     "predict NO flag -- ast.dump encodes the string VALUE, not the quote character",
     "def f(x):\n    return 'hello'\n",
     "def f(x):\n    return \"hello\"\n"),

    ("backslash-continuation",
     "predict NO flag -- line continuation is lexical, not part of the AST",
     "def f(x):\n    return x + 1\n",
     "def f(x):\n    return x + \\\n        1\n"),

    ("paren-wrap",
     "predict NO flag -- parenthesized wrapping across lines is lexical only",
     "def f(x):\n    return (x + 1)\n",
     "def f(x):\n    return (\n        x + 1\n    )\n"),

    ("default-arg-value",
     "predict FLAG -- a changed default value is a real semantic/AST change",
     "def f(x=1):\n    return x\n",
     "def f(x=2):\n    return x\n"),

    ("statement-reorder",
     "predict FLAG -- ast.dump encodes body list order, which changes",
     "def f(x):\n    a = 1\n    b = 2\n    return a + b\n",
     "def f(x):\n    b = 2\n    a = 1\n    return a + b\n"),

    ("add-type-annotation",
     "predict FLAG -- an annotation adds/changes an AST node (arg.annotation)",
     "def f(x):\n    return x\n",
     "def f(x: int):\n    return x\n"),

    ("int-literal-to-equiv-expr",
     "predict FLAG -- Constant(2) vs BinOp(1+1) differ in AST even though the runtime value is equal",
     "def f(x):\n    return x + 2\n",
     "def f(x):\n    return x + (1 + 1)\n"),

    ("for-loop-to-comprehension",
     "predict FLAG -- For-statement vs ListComp-expression are very different AST shapes",
     "def f(xs):\n    out = []\n    for x in xs:\n        out.append(x)\n    return out\n",
     "def f(xs):\n    out = [x for x in xs]\n    return out\n"),
]

print(f"{'case':30s} {'predicted':6s} {'actual':6s} {'match':5s}")
mismatches = []
for name, note, a, b in CASES:
    predicted_flag = "FLAG" in note.split("--")[0]
    ha, hb = h(a), h(b)
    actual_flag = ha != hb
    match = predicted_flag == actual_flag
    print(f"{name:30s} {str(predicted_flag):6s} {str(actual_flag):6s} {str(match):5s}  {note}")
    if not match:
        mismatches.append(name)

print()
print("mismatches:", mismatches if mismatches else "none -- every prediction matched observed behavior")
