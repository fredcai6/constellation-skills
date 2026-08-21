import ast
import re
import sys

PARENT_VALUE = "test-parent"

def patch_file(path, func_name="main", module_prefix="RC"):
    src = open(path, encoding="utf-8").read()
    lines = src.splitlines(keepends=True)
    tree = ast.parse(src)

    targets = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr != func_name:
            continue
        if not isinstance(func.value, ast.Name) or func.value.id != module_prefix:
            continue
        if not node.args:
            continue
        first = node.args[0]
        if not isinstance(first, ast.List):
            continue
        has_parent = any(
            isinstance(e, ast.Constant) and e.value == "--parent"
            for e in first.elts
        )
        if has_parent:
            continue
        if not first.elts:
            continue
        targets.append(first)

    if not targets:
        print(f"{path}: no unpatched {module_prefix}.{func_name}([...]) calls found")
        return 0

    targets.sort(key=lambda n: (n.end_lineno, n.end_col_offset), reverse=True)

    for lst in targets:
        close_line_idx = lst.end_lineno - 1
        close_line = lines[close_line_idx]
        close_col = lst.end_col_offset  # index right after ']'
        assert close_line[close_col - 1] == "]", (path, lst.lineno, repr(close_line))
        before_bracket = close_line[:close_col - 1]
        if before_bracket.strip() == "":
            # The `]` is alone (or with only leading whitespace) on this line
            # -- the multi-line-list case every real call site here uses.
            # Insert a NEW sibling element line above it, matching the
            # indentation of the line right before (the last real element,
            # which already ends in a trailing comma).
            prev_idx = close_line_idx - 1
            prev_line = lines[prev_idx]
            indent_match = re.match(r"[ \t]*", prev_line)
            indent = indent_match.group(0) if indent_match else "    "
            new_line = f'{indent}"--parent", "{PARENT_VALUE}",\n'
            lines.insert(close_line_idx, new_line)
        else:
            # Same-line case: there is element content right before `]` on
            # this line already (a trailing comma or the last element
            # itself) -- append ours right after it, before the bracket.
            trimmed = before_bracket.rstrip()
            needs_comma = not trimmed.endswith(",")
            sep = ", " if needs_comma else " "
            insertion = f'{sep}"--parent", "{PARENT_VALUE}"'
            lines[close_line_idx] = before_bracket + insertion + close_line[close_col - 1:]

    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(lines))
    print(f"{path}: patched {len(targets)} {module_prefix}.{func_name}([...]) call(s)")
    return len(targets)


if __name__ == "__main__":
    total = 0
    for p in sys.argv[1:]:
        total += patch_file(p)
    print(f"TOTAL patched: {total}")
