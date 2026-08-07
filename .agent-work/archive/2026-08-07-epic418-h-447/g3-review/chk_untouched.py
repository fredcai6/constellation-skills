import json,subprocess
def load(rev,p):
    if rev=='HEAD':
        return json.loads(subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,encoding='utf-8').stdout)
    return json.load(open(p,encoding='utf-8'))
C='skills/commander/templates/COMMANDER_SPINE.template.json'
A='skills/admiral/templates/ADMIRAL_SPINE.template.json'
oc,nc=load('HEAD',C),load('wt',C)
oa,na=load('HEAD',A),load('wt',A)

def cond(d,t,cid):
    for c in d['tasks'][t]['postconditions']:
        if c['id']==cid: return c
    return None
print('--- commander archive.c4 IDENTICAL:', cond(oc,'archive','c4')==cond(nc,'archive','c4'))
print('    deny_globs:', json.dumps(cond(nc,'archive','c4')['check']['policy']['deny_globs']))
for cid in ['c2','c2b','c3']:
    print(f'--- commander archive.{cid} IDENTICAL:', cond(oc,'archive',cid)==cond(nc,'archive',cid))
for cid in ['c3','c4','c5']:
    print(f'--- admiral closeout.{cid} IDENTICAL:', cond(oa,'closeout',cid)==cond(na,'closeout',cid))
# every OTHER task untouched?
for lbl,o,n in [('commander',oc,nc),('admiral',oa,na)]:
    changed=[t for t in o['tasks'] if o['tasks'][t]!=n['tasks'][t]]
    print(f'--- {lbl}: tasks differing from HEAD = {changed}')
# tail byte identity of untouched imperative sentences
oi,ni=oc['tasks']['archive']['imperative'],nc['tasks']['archive']['imperative']
anchor='Push the branch to remote.'
print('--- commander archive tail (from "Push the branch") IDENTICAL:',
      oi[oi.index(anchor):]==ni[ni.index(anchor):] if anchor in oi and anchor in ni else 'ANCHOR MISSING')
oi2,ni2=oa['closeout']['imperative'] if False else oa['tasks']['closeout']['imperative'], na['tasks']['closeout']['imperative']
a2='3) Hand the epic'
print('--- admiral closeout steps 3/4/5 IDENTICAL:', oi2[oi2.index(a2):]==ni2[ni2.index(a2):])
print('--- commander archive: work-area move instructed:', 'Move .agent-work/<work-id>/ to .agent-work/archive/<date>-<work-id>/' in ni)
print('--- commander archive: retired trailing clause gone:', 'leaving the unified AGENT_FEEDBACK.md' not in ni)
