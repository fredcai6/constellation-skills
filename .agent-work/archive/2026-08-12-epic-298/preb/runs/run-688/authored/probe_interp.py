"""Which interpreter can actually run this plan's verification commands?"""
import importlib.util as u
import subprocess
import sys

CANDIDATES = [
    sys.executable,
    r"C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe",
]
CODE = (
    "import sys,importlib.util as u;"
    "print(sys.executable);"
    "print('  scipy', bool(u.find_spec('scipy')), "
    "'| radon', bool(u.find_spec('radon')), "
    "'| pytest', bool(u.find_spec('pytest')), "
    "'| pandas', bool(u.find_spec('pandas')))"
)
for exe in CANDIDATES:
    try:
        r = subprocess.run([exe, "-c", CODE], capture_output=True, text=True, timeout=90)
        print((r.stdout or r.stderr).strip())
    except Exception as exc:
        print(f"{exe}: {type(exc).__name__}: {exc}")
_ = u
