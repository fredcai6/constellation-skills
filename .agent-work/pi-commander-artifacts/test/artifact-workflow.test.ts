import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile, writeFile, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { Workflow } from '../src/workflow.js';
import { parseHandoff } from '../src/invocation.js';
import { Engine } from '../src/engine.js';
import { COMMANDER_PROMPT } from '../src/artifacts.js';
const source=process.env.CONSTELLATION_SOURCE!;
const python=process.env.CONSTELLATION_PYTHON!;
function document(parts:Record<string,string>) { return Object.entries(parts).map(([name,value])=>`## ${name}\n${value}\n`).join('\n'); }
async function fixture(t:any){
 const cwd=await mkdtemp(join(tmpdir(),'pi-artifact-workflow-'));t.after(()=>rm(cwd,{recursive:true,force:true}));
 const dir=join(cwd,'run'),input=join(cwd,'task.md');await writeFile(input,'Write answer.txt containing 42. Preserve unrelated files. Verify exact bytes.');
 await Workflow.createFromArtifact(dir,input,{cwd,source,python,model:'anthropic/fake',maxCalls:40,maxTurns:8,timeoutMs:1000,maxOutputTokens:4096});
 const calls:any[]=[],handoffCounts={implementer:0,reviewer:0};let block=false,errorAfterBlock=false,missing=false,wrongGate=false;
 const runtime={async prompt(o:any){
  calls.push(o);const sessionFile=o.sessionFile??join(dir,`${o.role}.jsonl`);await o.onSessionAllocated?.(sessionFile);
  if(o.role==='commander'){
   const contextPath=/Read invocation context at (.*?)\. SHA256:/.exec(o.prompt)![1];
   const context=JSON.parse(await readFile(contextPath,'utf8'));const phase=context.engine.active.id;
   if(phase==='plan')await o.tools.find((t:any)=>t.name==='propose_plan').execute({plan:'Implement answer.txt; independently read and assert its bytes. Preserve scope.'});
   if(phase==='implement'||phase==='review'){
    const role=phase==='implement'?'implementer':'reviewer';
    let input=context.crewInvocations[role]?.input.path;
    if(!input){
     const round=++handoffCounts[role],result=join(cwd,`${role}-${round}-result.md`);
     const common={Gate:'g1','Close Criteria':'answer.txt contains exactly 42','Allowed Scope':'answer.txt and named result only','Stop Conditions':'Missing authority or evidence','Result Artifact':result,'Return Format':role==='implementer'?'IMPLEMENTER_RESULT':'REVIEW_RESULT'};
     const body=role==='implementer'?document({...common,Task:`Implement the task at ${context.task.path}. Plan: ${context.plan.path}. Prior findings: ${context.repairFindings?.artifact?.path??'none'}`,'Protected Intent':'Preserve unrelated files','Test Mode':'test-after allowed','Required Evidence':'assert exact bytes','Verification Commands':'read answer.txt',Authority:'Human plan approval recorded by engine'}):document({...common,'Task Statement':`Review task ${context.task.path} and plan ${context.plan.path}`,'How to Inspect the Diff':'read answer.txt','Constraints the Implementation Must Respect':'Preserve unrelated files','Evidence Produced':context.results.implementer.artifact.path});
     input=(await o.tools.find((t:any)=>t.name==='write_handoff').execute({content:body})).input.path;
    }
    await o.tools.find((t:any)=>t.name==='dispatch_crew').execute({input});
   }
  }else if(!missing){
   const path=/Execute the handoff snapshot at (.*?)\. Original location:/.exec(o.prompt)![1];
   const handoff=parseHandoff(await readFile(path,'utf8'),o.role);
   const common={'Assigned gate':wrongGate?'wrong':handoff.gate,'Workflow Feedback':'Checked handoff and references; no additional gaps','Return status':'complete'};
   if(o.role==='implementer')await writeFile(join(cwd,'answer.txt'),'42');
   await writeFile(handoff.result,document(o.role==='implementer'?{...common,'Completed slice':'Wrote answer',Scope:'answer.txt','Test mode':'test-after satisfied',Evidence:'read answer.txt: 42','Stop conditions hit':'none'}:{...common,Result:block?'BLOCK':'APPROVE','Handoff compliance':'Checked task and plan','Scope drift':'none','Evidence verdict':'independently read answer.txt',Blockers:block?'Fixture blocker':'none'}));
   await o.tools[0].execute({});
   if(errorAfterBlock&&o.role==='reviewer')throw Object.assign(Error('provider failed after BLOCK'),{partial:{sessionFile,usage:{input:1,output:1,cost:0.001}}});
  }
  return {text:'Narrative must not be copied to another agent or receipt',sessionFile,usage:{input:1,output:1,cost:0.001}};
 }};
 return {w:new Workflow(dir,runtime),dir,cwd,input,calls,block:(v:boolean)=>block=v,errorAfterBlock:(v:boolean)=>errorAfterBlock=v,missing:(v:boolean)=>missing=v,wrongGate:(v:boolean)=>wrongGate=v};
}
async function approvePlan(f:Awaited<ReturnType<typeof fixture>>){await f.w.chat('Propose plan');await f.w.approve('Human approves this fixture plan');}
test('artifact Commander completes separate crew delivery gates and waits for actual human acceptance',async t=>{
 const f=await fixture(t);await assert.rejects(f.w.approve('approve'),/propose a plan/);
 const plan=await f.w.chat('Plan');assert.ok(!('text' in plan));assert.ok(!JSON.stringify(plan).includes('Narrative'));
 await f.w.approve('Human approved');await f.w.chat('Implement');await f.w.chat('Review');
 const status=await f.w.status();assert.equal(status.engine.active?.id,'accept');assert.equal(status.results.reviewer?.verdict,'APPROVE');assert.ok(status.results.implementer?.artifact?.sha256);
 assert.equal(f.calls.find(c=>c.role==='implementer').systemPrompt.includes('Write answer'),false);
 const commanders=f.calls.filter(c=>c.role==='commander');assert.ok(commanders.every(c=>c.systemPrompt===COMMANDER_PROMPT));
 assert.notEqual(f.calls.find(c=>c.role==='implementer').sessionDir,f.calls.find(c=>c.role==='reviewer').sessionDir);
 assert.equal(status.calls,5);assert.equal(status.cost,0.005);
 const dispatch=commanders[1].tools.find((t:any)=>t.name==='dispatch_crew');assert.deepEqual(Object.keys(dispatch.parameters.properties),['input']);
 await f.w.approve('Human accepts reviewed fixture');assert.equal((await f.w.status()).engine.active,null);assert.equal((await f.w.status()).engine.lease_held,false);
});
test('review BLOCK repairs using preserved result reference, new round files and same role sessions',async t=>{
 const f=await fixture(t);await approvePlan(f);await f.w.chat('Implement');f.block(true);await f.w.chat('Review');
 assert.equal((await f.w.status()).engine.active?.id,'review');await assert.rejects(f.w.approve('accept'),/only available/);
 const first=(await f.w.status()).results.reviewer!.artifact!.path;
 await f.w.repair('Address findings in result artifact');f.block(false);await f.w.chat('Repair');await f.w.chat('Review again');
 const next=(await f.w.status()).results.reviewer!.artifact!.path;assert.notEqual(first,next);assert.match(await readFile(first,'utf8'),/BLOCK/);assert.match(await readFile(next,'utf8'),/APPROVE/);
 const implementers=f.calls.filter(c=>c.role==='implementer'),reviewers=f.calls.filter(c=>c.role==='reviewer');assert.equal(implementers[1].sessionFile,implementers[0].sessionFile??join(f.dir,'implementer.jsonl'));assert.equal(reviewers[1].sessionFile,join(f.dir,'reviewer.jsonl'));
 const metadata=JSON.parse(await readFile(join(f.dir,'run.json'),'utf8'));assert.equal(metadata.artifacts.history.length,4);assert.equal(metadata.repairFindings.artifact.path,first);
});
test('missing or wrong result cannot advance; retry resumes the same handoff and session',async t=>{
 const f=await fixture(t);await approvePlan(f);f.missing(true);await f.w.chat('Implement');assert.equal((await f.w.status()).engine.active?.id,'implement');
 f.missing(false);f.wrongGate(true);await f.w.chat('Retry');f.wrongGate(false);await f.w.chat('Retry again');
 assert.equal((await f.w.status()).engine.active?.id,'review');const meta=JSON.parse(await readFile(join(f.dir,'run.json'),'utf8'));assert.equal(meta.artifacts.history.length,1);
});
test('changed approved plan or task refuses further work before a model call',async t=>{
 const f=await fixture(t);await approvePlan(f);const status=await f.w.status(),plan=status.plan as {path:string};await writeFile(plan.path,'Different plan');
 const n=f.calls.length;await assert.rejects(f.w.chat('Implement'),/Artifact changed/);assert.equal(f.calls.length,n);
});
test('parent integration crash reuses delivered artifact without dispatching crew again',async t=>{
 const f=await fixture(t);await approvePlan(f);const original=Engine.prototype.run;let fail=true;
 Engine.prototype.run=async function(verb,args=[]){if(fail&&this.options.file===join(f.dir,'spine.json')&&verb==='advance'&&args[0]==='implement'){fail=false;throw Error('parent advance interrupted');}return original.call(this,verb,args);};
 try{await assert.rejects(f.w.chat('Implement'),/parent advance interrupted/);}finally{Engine.prototype.run=original;}
 await f.w.chat('Recover');assert.equal(f.calls.filter(c=>c.role==='implementer').length,1);assert.equal((await f.w.status()).engine.active?.id,'review');
});
test('BLOCK survives provider error; repair retires unfinished invocation without claiming success',async t=>{
 const f=await fixture(t);await approvePlan(f);await f.w.chat('Implement');f.block(true);f.errorAfterBlock(true);await f.w.chat('Review');
 assert.equal((await f.w.status()).results.reviewer?.verdict,'BLOCK');
 const meta=JSON.parse(await readFile(join(f.dir,'run.json'),'utf8')),binding=meta.artifacts.bindings.reviewer;
 await f.w.repair('Repair recorded blocker after provider failure');
 const retired=JSON.parse(await readFile(join(binding.dir,'invocation.json'),'utf8'));assert.ok(retired.abandoned);assert.equal(retired.completed,undefined);
 const engine=new Engine({source,python,cwd:f.cwd,file:join(binding.dir,'spine.json'),sessionId:retired.id});const state=await engine.state();assert.equal(state.active?.status,'blocked');assert.equal(state.lease_held,false);
});
test('provider error after APPROVE cannot advance review or manufacture a repair verdict',async t=>{
 const f=await fixture(t);await approvePlan(f);await f.w.chat('Implement');f.errorAfterBlock(true);
 await f.w.chat('Review');assert.equal((await f.w.status()).engine.active?.id,'review');assert.equal((await f.w.status()).results.reviewer,undefined);
 await assert.rejects(f.w.repair('Cannot treat errored approval as blocker'),/after a reviewer BLOCK/);
 f.errorAfterBlock(false);await f.w.chat('Resume review');assert.equal((await f.w.status()).engine.active?.id,'accept');
});
test('original task edits refuse work and resumed limits reach existing crew invocation',async t=>{
 const f=await fixture(t);await approvePlan(f);f.missing(true);await f.w.chat('Implement');f.missing(false);
 await f.w.chat('Resume with larger response budget',{maxOutputTokens:8192,maxTurns:12});
 const crews=f.calls.filter(c=>c.role==='implementer');assert.equal(crews[1].maxOutputTokens,8192);assert.equal(crews[1].maxTurns,12);
 await writeFile(f.input,'Changed scope');const before=f.calls.length;await assert.rejects(f.w.chat('Review'),/Artifact changed/);assert.equal(f.calls.length,before);
});
test('Markdown evidence code fences do not introduce handoff metadata sections',()=>{
 const text=document({Gate:'g1',Task:'Implement task','Protected Intent':'Preserve scope','Test Mode':'test-after','Close Criteria':'Exact bytes','Allowed Scope':'answer.txt','Required Evidence':'Read bytes','Verification Commands':'```sh\nprintf "## Gate\\nnot-metadata"\n## Gate\n```',Authority:'Explicit fixture authority','Stop Conditions':'Missing evidence','Return Format':'IMPLEMENTER_RESULT','Result Artifact':'result.md'});
 assert.equal(parseHandoff(text).gate,'g1');
});
test('generated handoff includes exact output contract and authorized restart preserves old round',async t=>{
 const f=await fixture(t);await approvePlan(f);f.missing(true);await f.w.chat('Implement');
 const meta=JSON.parse(await readFile(join(f.dir,'run.json'),'utf8')),first=meta.artifacts.bindings.implementer;
 const text=await readFile(first.input.path,'utf8');assert.match(text,/## Output Contract/);assert.match(text,/complete \| partial \| blocked \| out-of-scope \| failed/);assert.match(text,/second-level Markdown headings/);
 await assert.rejects(f.w.restartCrew('implementer','','Fix handoff'),/directing authority/);
 await f.w.restartCrew('implementer','supervising-agent','Replace incomplete output contract within approved scope');
 const retired=JSON.parse(await readFile(join(first.dir,'invocation.json'),'utf8'));assert.ok(retired.abandoned);assert.equal(retired.completed,undefined);
 f.missing(false);await f.w.chat('Resume active step');const next=JSON.parse(await readFile(join(f.dir,'run.json'),'utf8'));assert.equal(next.artifacts.history.length,2);assert.equal(next.overrides.at(-1).authority,'supervising-agent');assert.equal((await f.w.status()).engine.active?.id,'review');
});
