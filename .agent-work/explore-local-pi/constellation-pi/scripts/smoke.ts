import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { PiRuntime } from '../src/pi-runtime.js';
const dir=await mkdtemp(join(tmpdir(),'constellation-pi-smoke-'));
try {
 if(!process.env.ANTHROPIC_API_KEY)throw Error('ANTHROPIC_API_KEY is not loaded');
 const result=await new PiRuntime().prompt({role:'commander',cwd:dir,sessionDir:join(dir,'sessions'),model:'anthropic/claude-haiku-4-5',systemPrompt:'You are testing a local Pi session connection. Reply with exactly OK. Do not call tools.',prompt:'Connection check.',tools:[],maxTurns:1,maxOutputTokens:32,timeoutMs:30000});
 if(result.text.trim()!=='OK')throw Error('Connection returned an unexpected response');
 console.log(JSON.stringify({ok:true,model:'anthropic/claude-haiku-4-5',...result.usage}));
} catch(error:any) {console.error(JSON.stringify({ok:false,error:error.message,usage:error.partial?.usage}));process.exitCode=1;}
finally {await rm(dir,{recursive:true,force:true});}
