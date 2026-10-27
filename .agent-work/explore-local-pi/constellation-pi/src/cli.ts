#!/usr/bin/env node
import { parseArgs } from 'node:util';
import { resolve, join } from 'node:path';
import { mkdir } from 'node:fs/promises';
import { Workflow } from './workflow.js';
const help=`constellation-pi — Pi Commander with Constellation engine gates

new --task TEXT --cwd REPO --source CONSTELLATION --python PYTHON [--id NAME]
chat --run RUN_DIRECTORY --message TEXT
status --run RUN_DIRECTORY
repair --run RUN_DIRECTORY --reason TEXT
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
 const {values,positionals}=parseArgs({args:argv,allowPositionals:true,options:Object.fromEntries(['task','cwd','source','python','id','run','message','reason','authority','model','max-calls','max-turns','timeout-ms','max-output-tokens'].map(k=>[k,{type:'string' as const}]))});
 const need=(key:string)=>{const value=values[key];if(typeof value!=='string'||!value.trim())throw Error(`--${key} is required`);return value;};
 if(command==='new'){
  const cwd=resolve(need('cwd')),base=join(cwd,'.constellation-pi');await mkdir(base,{recursive:true});
  const id=values.id??new Date().toISOString().replace(/[:.]/g,'-');
  if(!/^[a-zA-Z0-9_-]+$/.test(id))throw Error('--id must contain letters, numbers, underscores or hyphens');
  const dir=join(base,id);
  const w=await Workflow.create(dir,need('task'),{cwd,source:resolve(need('source')),python:need('python'),model:values.model??'anthropic/claude-haiku-4-5',maxCalls:Number(values['max-calls']??12),maxTurns:Number(values['max-turns']??6),timeoutMs:Number(values['timeout-ms']??120000),maxOutputTokens:Number(values['max-output-tokens']??1024)});
  console.log(JSON.stringify({run:dir,...await w.status()},null,2));return;
 }
 const w=new Workflow(resolve(need('run')));
 const result=command==='status'?await w.status():command==='chat'?await w.chat(need('message'),Object.fromEntries([['max-output-tokens','maxOutputTokens'],['max-turns','maxTurns'],['timeout-ms','timeoutMs'],['max-calls','maxCalls']].filter(([flag])=>values[flag]!==undefined).map(([flag,key])=>[key,Number(values[flag])]))):command==='approve'?await w.approve(need('reason')):command==='repair'?await w.repair(need('reason')):command==='override'?await w.override(need('authority'),need('reason'),positionals[0]??'',positionals.slice(1)):undefined;
 if(result===undefined)throw Error(`Unknown command: ${command}`);
 console.log(JSON.stringify(result,null,2));
}
main().catch(error=>{console.error(error instanceof Error?error.message:String(error));process.exitCode=1;});
