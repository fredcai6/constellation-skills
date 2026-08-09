"""Restore CRLF working-tree line endings on files the Edit tool normalized to LF.

Every target in this gate was checked out CRLF (`.gitattributes` sets `* text=auto`, so the
blob is LF and the Windows checkout is CRLF). The editor writes LF, which git's own
normalization hides from `git diff` -- but leaving the working tree flipped is still a
whole-file byte change nobody asked for, so it is put back. Read/write in BINARY so nothing
else in the file can be reinterpreted."""
import sys
from pathlib import Path

for name in sys.argv[1:]:
    p = Path(name)
    data = p.read_bytes()
    fixed = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    if fixed != data:
        p.write_bytes(fixed)
        print(f"CRLF restored: {name}")
    else:
        print(f"already CRLF: {name}")
