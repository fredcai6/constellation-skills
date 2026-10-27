import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,readFile,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {Workflow,type Config} from '../src/workflow.js';
const source=process.env.CONSTELLATION_SOURCE??resolve('../../..');
const python=process.env.CONSTELLATION_PYTHON??'/home/tommy/.local/share/uv/python/cpython-3.12.13-linux-x86_64-gnu/bin/python';
async function fixture(t:any, opts:{block?:boolean,missing?:boolean,maxCalls?:number,instructions?:string,afterBlockError?:boolean}={}){
 const cwd=await mkdtemp(join(tmpdir(),'pi-workflow-'));t.after(()=>rm(cwd,{recursive:true,force:true}));
 const dir=join(cwd,'run');
 const config:Config={source,python,cwd,model:'anthropic/fake',maxCalls:opts.maxCalls??12,maxTurns:6,timeoutMs:1000};
 await Workflow.create(dir,'Write answer.txt with 42',config);
 const calls:any[]=[];
 const runtime={async prompt(o:any){calls.push(o);if(o.role==='commander'){
   const tool=o.tools[0];if(tool)await tool.execute(tool.name==='propose_plan'?{plan:'Write answer.txt containing 42; verify exact content.'}:{instructions:opts.instructions});
  }else if(!opts.missing){if(o.role==='implementer')await writeFile(join(cwd,'answer.txt'),'42');
   await o.tools[0].execute({verdict:o.role==='implementer'?'COMPLETE':opts.block?'BLOCK':'APPROVE',summary:o.role==='implementer'?'Wrote answer':'Checked answer',evidence:[`Read answer.txt: ${await readFile(join(cwd,'answer.txt'),'utf8')}`]});if(opts.afterBlockError&&o.role==='reviewer')throw Error('provider stopped after submitted BLOCK');}
  return {text:'done',sessionFile:join(dir,`${o.role}.jsonl`),usage:{input:1,output:1,cost:0.001}};
 }};
 return {w:new Workflow(dir,runtime),dir,cwd,calls};
}
test('Commander approval, separate crews, resume and final human acceptance use real engine',async t=>{
 const {w,dir,calls}=await fixture(t);
 await assert.rejects(w.approve('yes'),/propose a plan/);
 await w.chat('Plan the task');assert.equal((await w.status()).engine.active?.id,'plan');
 await w.approve('Approved');assert.equal((await w.status()).engine.active?.id,'implement');
 await w.chat('Execute');assert.equal((await w.status()).engine.active?.id,'review');
 await w.chat('Review');assert.equal((await w.status()).engine.active?.id,'accept');
 assert.deepEqual(calls.map(c=>c.role),['commander','commander','implementer','commander','reviewer']);
 assert.equal(calls[3].sessionFile,join(dir,'commander.jsonl'));
 const resumed=new Workflow(dir);assert.equal((await resumed.status()).engine.active?.id,'accept');
 await resumed.approve('Accepted after reviewing the evidence');assert.equal((await resumed.status()).engine.active,null);
 const status=await resumed.status();assert.equal(status.calls,5);assert.equal(status.cost,0.005);assert.equal(status.engine.lease_held,false);
});
test('Reviewer BLOCK cannot advance or receive human final acceptance',async t=>{
 const {w}=await fixture(t,{block:true});await w.chat('Plan');await w.approve('Approved');await w.chat('Implement');await w.chat('Review');
 assert.equal((await w.status()).engine.active?.id,'review');await assert.rejects(w.approve('accept'),/only available/);
});
test('Missing crew completion leaves parent gate open',async t=>{
 const {w}=await fixture(t,{missing:true});await w.chat('Plan');await w.approve('Approved');await assert.rejects(w.chat('Implement'),/without submitting/);
 assert.equal((await w.status()).engine.active?.id,'implement');
});
test('Call budget persists across resumes and stops before another runtime call',async t=>{
 const {w,calls}=await fixture(t,{maxCalls:1});await w.chat('Plan');await w.approve('Approved');await assert.rejects(w.chat('Implement'),/call limit/);assert.equal(calls.length,1);
});
test('Override requires authority, records reason, and leaves engine checks in charge',async t=>{
 const {w,dir}=await fixture(t);await assert.rejects(w.override('','why','waive',['plan','--cond','evidence']),/authority/);
 await w.override('human','Exercise explicit escape hatch','waive',['plan','--cond','evidence']);
 const saved=JSON.parse(await readFile(join(dir,'run.json'),'utf8'));assert.equal(saved.overrides.length,1);assert.equal(saved.overrides[0].authority,'human');
});
test('Concurrent controller mutations are refused',async t=>{
 const {w,dir}=await fixture(t);await writeFile(join(dir,'controller.lock'),'{}');await assert.rejects(w.chat('Plan'),/Another controller/);
});
test('Reviewer BLOCK can return to implementation and independent review',async t=>{
 const settings={block:true};const {w,calls}=await fixture(t,settings);await w.chat('Plan');await w.approve('Approved');await w.chat('Implement');await w.chat('Review');
 await w.repair('Address reviewer findings within the approved plan');assert.equal((await w.status()).engine.active?.id,'implement');
 settings.block=false;await w.chat('Repair');assert.match(calls.filter(c=>c.role==='implementer').at(-1).systemPrompt,/Reviewer findings to address:.*Checked answer/);assert.equal((await w.status()).engine.active?.id,'review');await w.chat('Review repaired work');assert.equal((await w.status()).engine.active?.id,'accept');
});
test('Completed child can recover parent integration without another model crew call',async t=>{
 const {Engine}=await import('../src/engine.js');const {w,dir,calls,cwd}=await fixture(t);await w.chat('Plan');await w.approve('Approved');
 const original=Engine.prototype.run;let crash=true;
 Engine.prototype.run=async function(verb,args=[]){if(crash&&this.options.file===join(dir,'spine.json')&&verb==='advance'&&args[0]==='implement'){crash=false;throw Error('simulated interruption before parent advance');}return original.call(this,verb,args);};
 try{await assert.rejects(w.chat('Implement'),/simulated interruption/);}finally{Engine.prototype.run=original;}
 const before=calls.filter(c=>c.role==='implementer').length;await w.chat('Recover implementation result');
 assert.equal(calls.filter(c=>c.role==='implementer').length,before);assert.equal((await w.status()).engine.active?.id,'review');
});
test('Explicit parent reopen requests fresh crew work rather than recycling prior result',async t=>{
 const {w,calls}=await fixture(t);await w.chat('Plan');await w.approve('Approved');await w.chat('Implement');
 await w.override('human','Reimplement with a corrected approach','reopen',['implement']);
 await w.chat('Implement again');assert.equal(calls.filter(c=>c.role==='implementer').length,2);
});
test('Refused reopen of an active review preserves reviewer findings and repair ability',async t=>{
 const {w}=await fixture(t,{block:true});await w.chat('Plan');await w.approve('Approved');await w.chat('Implement');await w.chat('Review');
 await assert.rejects(w.override('human','Retry review','reopen',['review']),/completed parent gate/);
 assert.equal((await w.status()).results.reviewer?.verdict,'BLOCK');await w.repair('Fix reviewer findings');assert.equal((await w.status()).engine.active?.id,'implement');
});

test('Directed override can start and close pending gates and releases the terminal lease',async t=>{
 const {w}=await fixture(t);
 await w.override('parent-agent','Authorize bounded fixture plan','waive',['plan','--cond','evidence']);
 await w.override('parent-agent','Begin directed fixture step','start',['plan']);
 await w.override('parent-agent','Proceed under parent direction','advance',['plan']);
 assert.equal((await w.status()).engine.active?.id,'implement');
 // A directed test can waive the execution evidence without inventing a crew result.
 for(const gate of ['implement','review','accept']){
  await w.override('parent-agent','Exercise explicit override lifecycle','waive',[gate,'--cond','evidence']);
  await w.override('parent-agent','Begin directed test step','start',[gate]);
  const transition=await w.override('parent-agent','Complete directed test step','advance',[gate]);
  if(gate==='accept')assert.equal(transition.state?.lease_held,false);
 }
 const status=await w.status();assert.equal(status.engine.active,null);assert.equal(status.engine.lease_held,false);
});

test('output-token budget updates persist and reach Commander and crew sessions',async t=>{
 const {w,dir,calls}=await fixture(t);
 await assert.rejects(w.chat('Plan',{maxOutputTokens:0}),/positive integer/);
 await w.chat('Plan',{maxOutputTokens:4096,maxTurns:20,timeoutMs:600000,maxCalls:12});await w.approve('Approved');await w.chat('Implement');
 assert.ok(calls.every(c=>c.maxOutputTokens===4096&&c.maxTurns===20&&c.timeoutMs===600000));
 assert.equal((await w.status()).maxCalls,12);
 assert.equal((await new Workflow(dir).status()).maxOutputTokens,4096);
});

test('Commander dispatch carries its bounded handoff to the crew',async t=>{
 const {w,calls}=await fixture(t,{instructions:'Verify PCI matching with canonical drm-pdev fixture data.'});
 await w.chat('Plan');await w.approve('Approved');await w.chat('Implement');
 assert.match(calls.find(c=>c.role==='implementer').systemPrompt,/Commander handoff: Verify PCI matching with canonical drm-pdev fixture data/);
});

test('submitted BLOCK survives an interrupted reviewer invocation and remains repairable',async t=>{
 const {w}=await fixture(t,{block:true,afterBlockError:true});await w.chat('Plan');await w.approve('Approved');await w.chat('Implement');await w.chat('Review');
 assert.equal((await w.status()).results.reviewer?.verdict,'BLOCK');assert.equal((await w.status()).engine.active?.id,'review');
 await w.repair('Address the recorded blocker');assert.equal((await w.status()).engine.active?.id,'implement');
});
