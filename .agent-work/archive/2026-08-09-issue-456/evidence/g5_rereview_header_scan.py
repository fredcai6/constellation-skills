import pathlib
import re

POSITION = re.compile(r"\.py:\d+")
total = 0
hits = 0
for page in pathlib.Path("map").rglob("*.md"):
    total += 1
    text = page.read_text(encoding="utf-8")
    lines = text.splitlines()
    header_region = "\n".join(lines[:2])
    if POSITION.search(header_region):
        hits += 1
        print("HIT:", page)

print(f"pages scanned: {total}, headers carrying a .py:<line>: {hits}")
