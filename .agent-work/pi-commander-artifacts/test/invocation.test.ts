import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { ArtifactInvocation, parseHandoff, IMPLEMENTER_PROMPT } from '../src/invocation.js';
import { Engine } from '../src/engine.js';
const source = process.env.CONSTELLATION_SOURCE!;
const python = process.env.CONSTELLATION_PYTHON!;
export function handoff(result = 'result.md') {
 return '# Implementer Handoff\n' + Object.entries({ Gate: 'g1', Task: 'Write answer.txt with 42.', 'Protected Intent': 'No unrelated changes', 'Test Mode': 'test-after allowed', 'Close Criteria': 'Exact answer', 'Allowed Scope': 'answer.txt and result.md', 'Required Evidence': 'Read answer.txt', 'Verification Commands': 'cat answer.txt', Authority: 'Human requested task', 'Stop Conditions': 'Missing authority', 'Return Format': 'Existing IMPLEMENTER_RESULT template', 'Result Artifact': '`'+result+'`' }).map(([k,v])=>`\n## ${k}\n${v}\n`).join('');
}
function result(status='complete',gate='g1') { return Object.entries({ 'Assigned gate':gate, 'Completed slice':'Wrote answer', Scope:'answer.txt', 'Test mode':'test-after satisfied', Evidence:'Read answer.txt: 42', 'Stop conditions hit':'none', 'Workflow Feedback':'No gaps after checking assignment', 'Return status':status }).map(([k,v])=>`## ${k}\n${v}\n`).join('\n'); }
async function fixture(t:any) {
 const cwd=await mkdtemp(join(tmpdir(),'pi-artifact-'));t.after(()=>rm(cwd,{recursive:true,force:true}));
 const input=join(cwd,'handoff.md'),dir=join(cwd,'invocation');await writeFile(input,handoff());
 await ArtifactInvocation.create(dir,input,{cwd,source,python,model:'anthropic/fake',maxCalls:3,maxTurns:6,timeoutMs:1000,maxOutputTokens:4096});
 let mode='complete';let calls:any[]=[];
 const runtime={async prompt(o:any){calls.push(o);await o.onSessionAllocated(join(dir,'session.jsonl'));
  if(mode!=='missing') {if(mode!=='stale')await writeFile(join(cwd,'result.md'),result(mode==='partial'?'partial':'complete',mode==='wrong-gate'?'g2':'g1'));await o.tools[0].execute({});}
  if(mode==='error-after-submit')throw Object.assign(Error('provider failed after delivery'),{partial:{sessionFile:join(dir,'session.jsonl'),usage:{input:4,output:2,cost:0.01}}});
  return {sessionFile:join(dir,'session.jsonl'),text:'Extra commentary must never enter receipt',usage:{input:4,output:2,cost:0.01}};
 }};
 return {cwd,dir,input,calls,run:new ArtifactInvocation(dir,runtime),mode:(v:string)=>mode=v,engine:new Engine({cwd,source,python,file:join(dir,'spine.json'),sessionId:JSON.parse(await readFile(join(dir,'invocation.json'),'utf8')).id})};
}
test('existing Markdown delivery and explicit result field share one contract',()=>{
 const h=handoff();assert.equal(parseHandoff(h).result,'result.md');
 assert.equal(parseHandoff(h.replace(/## Result Artifact[\s\S]*/, 'Delivery. Write the full `IMPLEMENTER_RESULT` to `result.md` before ending.')).result,'result.md');
 assert.throws(()=>parseHandoff(h.replace('## Task','## Missing')),/Incomplete/);
 assert.throws(()=>parseHandoff(h+'\n## Delivery\nWrite the full `IMPLEMENTER_RESULT` to `other.md`'),/Conflicting/);
 assert.throws(()=>parseHandoff(handoff('<work-id>/result.md')),/concrete/);
});
test('artifact flows through real engine; receipt has no duplicated narrative and completed rerun costs nothing',async t=>{
 const f=await fixture(t);const receipt=await f.run.run();assert.equal(receipt.status,'complete');assert.equal(receipt.estimatedCostUsd,0.01);
 assert.ok(!JSON.stringify(receipt).includes('Extra commentary'));
 assert.equal(f.calls[0].systemPrompt,IMPLEMENTER_PROMPT);assert.ok(!IMPLEMENTER_PROMPT.includes('Write answer'));
 assert.match(f.calls[0].prompt,/input.md/);assert.ok(!f.calls[0].prompt.includes('Write answer'));
 assert.equal((await f.engine.state()).active,null);assert.equal((await f.engine.state()).lease_held,false);
 await f.run.run();assert.equal(f.calls.length,1);
});
for(const mode of ['missing','wrong-gate','partial','error-after-submit'])test(`${mode} cannot complete and resume reuses session`,async t=>{
 const f=await fixture(t);f.mode(mode);const receipt=await f.run.run();assert.notEqual(receipt.status,'complete');assert.ok((await f.engine.state()).active);
 f.mode('complete');await new Promise(r=>setTimeout(r,5));assert.equal((await f.run.run()).status,'complete');assert.equal(f.calls[1].sessionFile,f.calls[0]?join(f.dir,'session.jsonl'):null);
 assert.equal(f.calls[0].systemPrompt,f.calls[1].systemPrompt);
});
test('modified input refuses resume before another model call',async t=>{
 const f=await fixture(t);f.mode('missing');await f.run.run();await writeFile(f.input,handoff()+'\nChanged task');await assert.rejects(f.run.run(),/Input changed/);assert.equal(f.calls.length,1);
});
test('stale existing output and concurrent controller are refused',async t=>{
 const f=await fixture(t);await writeFile(join(f.cwd,'result.md'),result());await assert.rejects(ArtifactInvocation.create(join(f.cwd,'other'),f.input,{cwd:f.cwd,source,python,model:'fake',maxCalls:1,maxTurns:1,timeoutMs:1000}),/already exists/);
 await writeFile(join(f.dir,'controller.lock'),'{}');await assert.rejects(f.run.run(),/already has a controller/);assert.equal(f.calls.length,0);
});
test('engine integration interruption recovers verified result without paid retry',async t=>{
 const f=await fixture(t),original=Engine.prototype.run;let fail=true;
 Engine.prototype.run=async function(verb,args=[]){if(fail&&this.options.file===join(f.dir,'spine.json')&&verb==='advance'){fail=false;throw Error('interrupted integration');}return original.call(this,verb,args);};
 try{assert.equal((await f.run.run()).status,'verified');}finally{Engine.prototype.run=original;}
 assert.equal((await f.run.run()).status,'complete');assert.equal(f.calls.length,1);
});

test('resume refuses stale prior output without a fresh delivery',async t=>{
 const f=await fixture(t);f.mode('error-after-submit');await f.run.run();f.mode('stale');
 const receipt=await f.run.run();assert.equal(receipt.status,'error');assert.match(receipt.attempts.at(-1)!.error!,/stale/);assert.ok((await f.engine.state()).active);
});
test('interrupted attempt requires explicit recovery and retains session',async t=>{
 const f=await fixture(t);f.mode('missing');await f.run.run();
 const path=join(f.dir,'invocation.json'),manifest=JSON.parse(await readFile(path,'utf8'));manifest.attempts[0].outcome='running';delete manifest.attempts[0].usage;await writeFile(path,JSON.stringify(manifest));
 await assert.rejects(f.run.run(),/explicitly recover/);f.mode('complete');
 const receipt=await f.run.run(true);assert.equal(receipt.status,'complete');assert.equal(receipt.costIncomplete,true);assert.equal(receipt.attempts[0].outcome,'interrupted');assert.equal(f.calls[1].sessionFile,join(f.dir,'session.jsonl'));
});
test('failure after terminal advance recovers lease release without model retry',async t=>{
 const f=await fixture(t),original=Engine.prototype.run;let fail=true;
 Engine.prototype.run=async function(verb,args=[]){if(fail&&this.options.file===join(f.dir,'spine.json')&&verb==='release'){fail=false;throw Error('release interrupted');}return original.call(this,verb,args);};
 try{assert.equal((await f.run.run()).status,'verified');}finally{Engine.prototype.run=original;}
 assert.equal((await f.run.run()).status,'complete');assert.equal(f.calls.length,1);assert.equal((await f.engine.state()).lease_held,false);
});
