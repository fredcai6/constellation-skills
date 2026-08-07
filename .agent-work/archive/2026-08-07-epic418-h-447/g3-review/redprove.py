import hashlib, subprocess, sys, os
P = 'skills/commander/templates/COMMANDER_SPINE.template.json'
BK = '.agent-work/epic418-h-447/g3-review/COMMANDER_SPINE.backup.bin'
orig = open(P,'rb').read()
open(BK,'wb').write(orig)
h0 = hashlib.sha256(orig).hexdigest()
print('ORIG sha256', h0, 'bytes', len(orig))

OLD = b'verify_episode_captured.py <work-id> --store-root episodes --phase feedback"}'
NEW = b'verify_episode_NOSUCHSCRIPT.py <work-id> --store-root episodes --phase feedback"}'
assert orig.count(OLD) == 1, f'MUTATION ANCHOR COUNT = {orig.count(OLD)} (expected 1) -- aborting'
mut = orig.replace(OLD, NEW)
assert mut != orig, 'mutation did not apply'
print('MUTATION APPLIED: feedback.c1 command now names verify_episode_NOSUCHSCRIPT.py')
try:
    open(P,'wb').write(mut)
    assert open(P,'rb').read() == mut, 'mutated bytes did not land'
    env = dict(os.environ, FORCE_COLOR='0', NO_COLOR='1')
    r = subprocess.run([sys.executable,'-m','pytest',
        'tests/test_install_constellation.py::InstallConstellationTests::test_every_spine_command_names_an_installed_script',
        '-q'], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    print('--- RED RUN EXIT =', r.returncode, '---')
    print(r.stdout[-2500:])
finally:
    open(P,'wb').write(orig)
    back = open(P,'rb').read()
    h1 = hashlib.sha256(back).hexdigest()
    print('RESTORED sha256', h1, 'bytes', len(back))
    print('BYTE-IDENTICAL RESTORE:', h1 == h0 and back == orig)
