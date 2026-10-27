#!/usr/bin/env node
import { parseArgs } from 'node:util';
import { resolve, join } from 'node:path';
import { mkdir } from 'node:fs/promises';
import { Workflow } from './workflow.js';
import { ArtifactInvocation } from './invocation.js';
import { createHash } from 'node:crypto';
import { usageReport } from './telemetry.js';
const help=`constellation-pi — Pi Commander with Constellation engine gates

invoke --role implementer|reviewer --input HANDOFF.md --cwd REPO --source CONSTELLATION --python PYTHON [--id NAME]
invoke --run RUN_DIRECTORY [--recover-interrupted yes]
invoke-status --run RUN_DIRECTORY
usage --run RUN_DIRECTORY

new --input TASK_FILE --cwd REPO --source CONSTELLATION --python PYTHON [--id NAME]
new --task TEXT --cwd REPO --source CONSTELLATION --python PYTHON [--id NAME]
chat --run RUN_DIRECTORY --message TEXT
status --run RUN_DIRECTORY
repair --run RUN_DIRECTORY --reason TEXT
restart-crew --run RUN_DIRECTORY --role implementer|reviewer --authority PRINCIPAL --reason TEXT
approve --run RUN_DIRECTORY --reason TEXT
override --run RUN_DIRECTORY --authority human|PRINCIPAL --reason TEXT -- VERB ARGS...

new prints its run directory. Approve is an explicit human operation.
Set ANTHROPIC_API_KEY in your environment; credentials are never copied to runs.
Options: --model anthropic/claude-haiku-4-5 --max-calls 12 --max-turns 6 --timeout-ms 120000 --max-output-tokens 1024
For code-writing tasks, set --max-output-tokens 4096 on new or chat; the value persists.
Commander path: plan → implement → review → accept.
This version does not execute the entire installed Commander skill or publish changes.
`;
async function main(){
 const [command,...argv]=process.argv.slice(2);
 if(!command||command==='help'||command==='--help'){console.log(help);return;}
 const {values,positionals}=parseArgs({args:argv,allowPositionals:true,options:Object.fromEntries(['input','role','recover-interrupted','task','cwd','source','python','id','run','message','reason','authority','model','max-calls','max-turns','timeout-ms','max-output-tokens'].map(k=>[k,{type:'string' as const}]))});
 const need=(key:string)=>{const value=values[key];if(typeof value!=='string'||!value.trim())throw Error(`--${key} is required`);return value;};
 if(command==='usage') { console.log(JSON.stringify(await usageReport(resolve(need('run'))),null,2)); return; }
 if(command==='invoke-status') { console.log(JSON.stringify(await new ArtifactInvocation(resolve(need('run'))).status(),null,2)); return; }
 if(command==='invoke') {
  if(values.message||values.task||values.reason)throw Error('Invocation assignments belong in the input artifact, not commentary');
  if(values['recover-interrupted']!==undefined&&values['recover-interrupted']!=='yes')throw Error('--recover-interrupted must be yes');
  let invocation:ArtifactInvocation;
  if(values.run) {
   if(['input','role','cwd','source','python','model','id','max-calls','max-turns','timeout-ms','max-output-tokens'].some(key=>values[key]!==undefined))throw Error('Resume uses the recorded input and configuration');
   invocation=new ArtifactInvocation(resolve(values.run));
  } else {
   if(!['implementer','reviewer'].includes(need('role')))throw Error('Artifact invocation supports implementer or reviewer');
   const cwd=resolve(need('cwd')),input=resolve(cwd,need('input')),base=join(cwd,'.constellation-pi');
   const id=values.id??`invoke-${createHash('sha256').update(input).digest('hex').slice(0,16)}`;
   if(!/^[a-zA-Z0-9_-]+$/.test(id))throw Error('Invalid invocation id');
   await mkdir(base,{recursive:true});
   invocation=await ArtifactInvocation.create(join(base,id),input,{cwd,source:resolve(need('source')),python:need('python'),model:values.model??'anthropic/claude-sonnet-4-6',maxCalls:Number(values['max-calls']??3),maxTurns:Number(values['max-turns']??20),timeoutMs:Number(values['timeout-ms']??600000),maxOutputTokens:Number(values['max-output-tokens']??8192)},need('role') as 'implementer'|'reviewer');
  }
  const receipt=await invocation.run(values['recover-interrupted']==='yes');
  console.log(JSON.stringify(receipt,null,2));if(receipt.status!=='complete')process.exitCode=1;return;
 }
 if(command==='new'){
  const cwd=resolve(need('cwd')),base=join(cwd,'.constellation-pi');await mkdir(base,{recursive:true});
  const id=values.id??new Date().toISOString().replace(/[:.]/g,'-');
  if(!/^[a-zA-Z0-9_-]+$/.test(id))throw Error('--id must contain letters, numbers, underscores or hyphens');
  const dir=join(base,id);
  if(values.input&&values.task)throw Error('Use --input for an artifact run or --task for a legacy run, not both');
  const artifact=!!values.input;
  const config={cwd,source:resolve(need('source')),python:need('python'),model:values.model??(artifact?'anthropic/claude-sonnet-4-6':'anthropic/claude-haiku-4-5'),maxCalls:Number(values['max-calls']??12),maxTurns:Number(values['max-turns']??(artifact?20:6)),timeoutMs:Number(values['timeout-ms']??(artifact?600000:120000)),maxOutputTokens:Number(values['max-output-tokens']??(artifact?8192:1024))};
  const w=artifact?await Workflow.createFromArtifact(dir,need('input'),config):await Workflow.create(dir,need('task'),config);
  console.log(JSON.stringify({run:dir,...await w.status()},null,2));return;
 }
 const w=new Workflow(resolve(need('run')));
 const result=command==='restart-crew'?await w.restartCrew(need('role') as 'implementer'|'reviewer',need('authority'),need('reason')):command==='status'?await w.status():command==='chat'?await w.chat(need('message'),Object.fromEntries([['max-output-tokens','maxOutputTokens'],['max-turns','maxTurns'],['timeout-ms','timeoutMs'],['max-calls','maxCalls']].filter(([flag])=>values[flag]!==undefined).map(([flag,key])=>[key,Number(values[flag])]))):command==='approve'?await w.approve(need('reason')):command==='repair'?await w.repair(need('reason')):command==='override'?await w.override(need('authority'),need('reason'),positionals[0]??'',positionals.slice(1)):undefined;
 if(result===undefined)throw Error(`Unknown command: ${command}`);
 console.log(JSON.stringify(result,null,2));
}
main().catch(error=>{console.error(error instanceof Error?error.message:String(error));process.exitCode=1;});
