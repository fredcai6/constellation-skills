import ast
import re
import sys

PARENT_VALUE = "test-parent"

def patch_file(path):
    src = open(path, encoding="utf-8").read()
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)

    calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name != "CrewSpec":
                continue
            has_parent = any(kw.arg == "parent" for kw in node.keywords)
            if has_parent:
                continue
            calls.append(node)

    if not calls:
        print(f"{path}: no unpatched CrewSpec(...) calls found")
        return 0

    # Sort by position descending so earlier edits don't shift later offsets.
    calls.sort(key=lambda n: (n.end_lineno, n.end_col_offset), reverse=True)

    for node in calls:
        close_line_idx = node.end_lineno - 1
        close_line = lines[close_line_idx]
        stripped = close_line.strip()
        if stripped == ")" or stripped == "):":
            # Closing paren on its own line -- insert a new sibling kwarg line
            # above it, matching the indentation of the line right before it
            # (the last real kwarg line), which is the multi-line-call case
            # every actual call site in this repo uses.
            prev_idx = close_line_idx - 1
            prev_line = lines[prev_idx]
            indent_match = re.match(r"[ \t]*", prev_line)
            indent = indent_match.group(0) if indent_match else "    "
            new_line = f'{indent}parent="{PARENT_VALUE}",\n'
            lines.insert(close_line_idx, new_line)
        else:
            # Single-line or unusual shape -- insert inline right before ')'.
            close_col = node.end_col_offset
            assert close_line[close_col - 1] == ")", (path, node.lineno, repr(close_line))
            insertion = f'parent="{PARENT_VALUE}", '
            lines[close_line_idx] = (
                close_line[:close_col - 1] + insertion + close_line[close_col - 1:]
            )

    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(lines))
    print(f"{path}: patched {len(calls)} CrewSpec(...) call(s)")
    return len(calls)


if __name__ == "__main__":
    total = 0
    for p in sys.argv[1:]:
        total += patch_file(p)
    print(f"TOTAL patched: {total}")
