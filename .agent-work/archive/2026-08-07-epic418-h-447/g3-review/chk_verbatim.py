import json
SENT = "An episode is a record, not a rule: write what you observed, and do NOT write a rule for a future agent to follow \u2014 a rule to follow belongs in docs/agents/* and is a human's call."
for name,p in [('commander','skills/commander/templates/COMMANDER_SPINE.template.json'),
               ('admiral','skills/admiral/templates/ADMIRAL_SPINE.template.json')]:
    d=json.load(open(p,encoding='utf-8'))
    step = 'feedback' if name=='commander' else 'closeout'
    imp = d['tasks'][step]['imperative']
    print(name, step, 'VERBATIM PRESENT:', SENT in imp)
    if SENT not in imp:
        i=imp.find('An episode is a record')
        print('  actual:', repr(imp[i:i+220]))
