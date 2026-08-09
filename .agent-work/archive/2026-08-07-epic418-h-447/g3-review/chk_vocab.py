import json,re,sys
paths = {'commander':'skills/commander/templates/COMMANDER_SPINE.template.json',
         'admiral':'skills/admiral/templates/ADMIRAL_SPINE.template.json'}
BAD = ['lesson','LESSON','ripe','apply-or-defer','bank_reason','dormanc','disposition',
       'playbook','AGENT_FEEDBACK','graduate','apply_lessons_delta','verify_lessons_applied',
       'verify_agent_feedback','lessons-auditor','inbox']
for name,p in paths.items():
    raw=open(p,encoding='utf-8').read()
    print('===',name)
    for b in BAD:
        hits=[m.start() for m in re.finditer(re.escape(b),raw)]
        if hits:
            for h in hits:
                print(f'  HIT {b!r} @{h}: ...{raw[max(0,h-160):h+160]}...')
    if not any(re.search(re.escape(b),raw) for b in BAD):
        print('  clean of all retired vocabulary')
