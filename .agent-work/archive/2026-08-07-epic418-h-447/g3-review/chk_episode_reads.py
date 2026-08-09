import json,re
for name,p in [('commander','skills/commander/templates/COMMANDER_SPINE.template.json'),
               ('admiral','skills/admiral/templates/ADMIRAL_SPINE.template.json')]:
    d=json.load(open(p,encoding='utf-8'))
    print('='*20,name)
    for tid,t in d['tasks'].items():
        blobs=[('imperative',t.get('imperative') or '')]
        for c in t.get('preconditions',[])+t.get('postconditions',[]):
            blobs.append((tid+'.'+c['id']+'.statement', c.get('statement') or ''))
            ch=c.get('check')
            if ch: blobs.append((tid+'.'+c['id']+'.check', json.dumps(ch)))
        for label,txt in blobs:
            if re.search(r'episode', txt, re.I):
                for m in re.finditer(r'[^.]*episode[^.]*\.', txt, re.I):
                    print(f'  [{tid}/{label}] {m.group(0).strip()}')
