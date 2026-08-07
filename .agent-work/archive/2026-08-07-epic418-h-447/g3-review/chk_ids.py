import json, subprocess, sys
paths = ['skills/commander/templates/COMMANDER_SPINE.template.json',
         'skills/admiral/templates/ADMIRAL_SPINE.template.json']
def ids(d):
    out={}
    for tid,t in d['tasks'].items():
        out[tid]={'pre':[c['id'] for c in t.get('preconditions',[])],
                  'post':[c['id'] for c in t.get('postconditions',[])]}
    return out
rc=0
for p in paths:
    old=json.loads(subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,encoding='utf-8').stdout)
    new=json.load(open(p,encoding='utf-8'))
    a,b=ids(old),ids(new)
    print('===',p)
    if list(old['tasks'])!=list(new['tasks']):
        print('  TASK LIST CHANGED:',list(old['tasks']),'->',list(new['tasks'])); rc=1
    if old.get('items')!=new.get('items'):
        print('  ITEMS CHANGED:',old.get('items'),'->',new.get('items')); rc=1
    for tid in a:
        if a[tid]!=b.get(tid):
            print('  DIFF',tid,'OLD',a[tid],'NEW',b.get(tid))
    print('  full old post map:',{k:v['post'] for k,v in a.items()})
    print('  full new post map:',{k:v['post'] for k,v in b.items()})
sys.exit(rc)
