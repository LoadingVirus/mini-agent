#!/opt/homebrew/bin/python3.12
"""mini-agent v3 — 全新重写，干净无 bug"""

import http.server, json, urllib.request, urllib.parse, re, os, platform
from ddgs import DDGS

HOST, PORT = "localhost", 8765
OS_NAME = {"Darwin":"macOS","Windows":"Windows","Linux":"Linux"}.get(platform.system(),platform.system())
LM_STUDIO = "http://localhost:1234/v1"
DIR = os.path.dirname(os.path.abspath(__file__))
SESSIONS_FILE = os.path.join(DIR, "sessions.json")

def web_search(q):
    try:
        rs = list(DDGS().text(q, max_results=5))
        if not rs: return "无结果"
        lines = [f"[{i+1}] {r.get('title','')}\n   {r.get('body','')[:300]}\n   {r.get('href','')}" for i,r in enumerate(rs)]
        return "\n\n".join(lines)
    except Exception as e:
        return f"搜索出错: {e}"

def load_sessions():
    try:
        with open(SESSIONS_FILE) as f: return json.load(f)
    except: return {}

def save_sessions(d):
    with open(SESSIONS_FILE, "w") as f: json.dump(d, f, ensure_ascii=False, indent=2)

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Mini Harness</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:"Inter",-apple-system,BlinkMacSystemFont,sans-serif;background:#f5f5f7;color:#1d1d1f;height:100vh;display:flex;-webkit-font-smoothing:antialiased}
.sidebar{width:200px;flex-shrink:0;background:rgba(250,250,252,0.9);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-right:0.5px solid rgba(0,0,0,0.08);display:flex;flex-direction:column}
.sidebar-header{padding:12px 14px;display:flex;align-items:center;justify-content:space-between;border-bottom:0.5px solid rgba(0,0,0,0.06)}
.sidebar-header span{font-size:12px;font-weight:600;color:#86868b;letter-spacing:0.5px}
.sidebar-header button{width:24px;height:24px;border-radius:50%;border:none;background:#0071e3;color:#fff;font-size:16px;cursor:pointer;line-height:1}
.sidebar-header button:hover{background:#0077ed}
#sessions{flex:1;overflow-y:auto;padding:6px}
.sess{padding:8px 12px;border-radius:8px;cursor:pointer;font-size:13px;margin-bottom:1px;display:flex;align-items:center;justify-content:space-between;transition:background .1s}
.sess:hover{background:rgba(0,0,0,0.04)}
.sess.on{background:rgba(0,113,227,0.1);color:#0071e3;font-weight:500}
.sess .name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex:1}
.sess .x{display:none;font-size:11px;color:#86868b;margin-left:4px;padding:2px 4px;border-radius:4px}
.sess:hover .x{display:block}.sess .x:hover{background:rgba(255,59,48,0.1);color:#ff3b30}
.main{flex:1;display:flex;flex-direction:column;min-width:0}
.toolbar{background:rgba(255,255,255,0.85);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-bottom:0.5px solid rgba(0,0,0,0.08);padding:0 20px;height:48px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.toolbar h1{font-size:14px;font-weight:600}
.toolbar .right{display:flex;align-items:center;gap:12px;font-size:12px;color:#86868b}
.toolbar .dot{width:7px;height:7px;border-radius:50%;display:inline-block}
.toolbar .dot.g{background:#34c759}.toolbar .dot.r{background:#ff3b30}
#msgs{flex:1;overflow-y:auto;padding:20px}
.msg.u{color:#1d1d1f}.msg.a{color:#1d1d1f}.msg.p{color:#3634a3;font-size:13px}.msg.t{color:#6e6e73;font-size:12px}
.msg .head{font-size:11px;font-weight:600;color:#86868b;margin-bottom:2px}
#input-wrap{padding:12px 20px 16px;flex-shrink:0;background:rgba(250,250,252,0.85);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);border-top:0.5px solid rgba(0,0,0,0.08)}
#input-wrap .bar{max-width:900px;margin:0 auto;display:flex;gap:8px;align-items:flex-end;background:#fff;border-radius:20px;border:1px solid rgba(0,0,0,0.1);padding:3px 3px 3px 14px;transition:border-color .2s}
#input-wrap .bar:focus-within{border-color:#0071e3;box-shadow:0 0 0 3px rgba(0,113,227,0.1)}
#inp{flex:1;border:none;outline:none;font:14px "Inter",-apple-system,sans-serif;color:#1d1d1f;resize:none;min-height:22px;max-height:80px;padding:5px 0;background:transparent}
#inp::placeholder{color:#c7c7cc}
#inp:disabled{color:#86868b}
#btn{width:32px;height:32px;border-radius:50%;border:none;background:#0071e3;color:#fff;font-size:16px;cursor:pointer;flex-shrink:0;display:flex;align-items:center;justify-content:center;transition:opacity .15s}
#btn:hover{background:#0077ed}
#btn:disabled{opacity:0.35;cursor:not-allowed}
.dots{display:flex;gap:4px;padding:4px 0}.dots span{width:5px;height:5px;border-radius:50%;background:#c7c7cc;animation:b 1.4s infinite}.dots span:nth-child(2){animation-delay:.2s}.dots span:nth-child(3){animation-delay:.4s}@keyframes b{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-4px);opacity:1}}
.msg{padding:6px 20px;display:flex;flex-direction:column;max-width:900px}
.msg.u{align-items:flex-start}.msg.a{align-items:flex-start}
.bubble{max-width:80%;padding:10px 14px;border-radius:18px;font-size:14px;line-height:1.55;word-break:break-word}
.msg.u .bubble{background:#0071e3;color:#fff;border-bottom-left-radius:6px}
.msg.a .bubble{background:#e9e9eb;color:#1d1d1f;border-bottom-left-radius:6px;max-width:none;width:auto}
.msg.p{padding:4px 20px 4px 28px;font-size:13px;color:#5856d6;align-items:flex-start;border-left:3px solid #5856d6;margin:6px 0 6px 16px}
.msg.p .head{font-size:11px;font-weight:600;margin-bottom:4px;color:#3634a3}
.msg.t{padding:4px 20px;font-size:12px;color:#8e8e93;align-items:flex-start;font-style:italic}
.msg.t .head{font-weight:600;margin-bottom:2px}
/* Markdown 表格 */
.bubble table{border-collapse:collapse;margin:8px 0;width:100%;font-size:13px}
.bubble th,.bubble td{border:1px solid rgba(0,0,0,0.15);padding:6px 10px;text-align:left}
.bubble th{background:rgba(0,0,0,0.04);font-weight:600}
.msg.u .bubble th{background:rgba(255,255,255,0.15);border-color:rgba(255,255,255,0.3)}
.msg.u .bubble td{border-color:rgba(255,255,255,0.2)}
.bubble pre{background:rgba(0,0,0,0.05);padding:12px;border-radius:8px;overflow-x:auto;margin:8px 0;font-size:13px}
.msg.u .bubble pre{background:rgba(255,255,255,0.12)}
.bubble code{font-family:"SF Mono",Monaco,monospace;font-size:13px}
.bubble p{margin:4px 0}.bubble ul,.bubble ol{padding-left:20px;margin:4px 0}
::-webkit-scrollbar{width:5px}::-webkit-scrollbar-thumb{background:rgba(0,0,0,0.12);border-radius:3px}
</style>
</head>
<body>
<div class="sidebar">
<div class="sidebar-header"><span>会话</span><button onclick="newS()" title="新建">+</button></div>
<div id="sessions"></div>
</div>
<div class="main">
<div class="toolbar"><h1>Mini Harness <span style="font-size:11px;color:#0071e3;font-weight:400">v3</span></h1><div class="right"><span id="toks" style="white-space:nowrap;min-width:140px;text-align:right"></span><span class="dot r" id="dot"></span><span id="stat">⏳</span></div></div>
<div id="msgs"></div>
<div id="input-wrap"><div class="bar"><textarea id="inp" rows="1" placeholder="输入消息..." onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();send()}"></textarea><button id="btn" onclick="send()" disabled>↑</button></div></div>
</div>
<script>
// ============== STATE ==============
let SS={}, aid=null, toks=0, pending=null;
const SYS="你是运行在{OS}上的助手，可执行终端命令获取系统信息。需要实时信息时用 web_search 搜索。搜索结果足够时直接回答，不要再搜索！";

// ============== SESSIONS ==============
async function api(u,o){let r=await fetch(u,o);return o&&o.method==='POST'?r.json():r.json()}
async function loadS(){SS=await api('/api/sessions');if(!Object.keys(SS).length)await newS();else{aid=Object.keys(SS).sort().pop();renderS()}}
async function saveS(){await api('/api/sessions',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(SS)})}
async function newS(){let id='s'+Date.now();SS[id]={name:'新对话',h:[],ts:Date.now()};aid=id;await saveS();renderS();renderM()}
function switchS(id){aid=id;renderS();renderM()}
async function delS(id){if(Object.keys(SS).length<2)return;delete SS[id];if(aid===id)aid=Object.keys(SS).sort().pop();await saveS();renderS();renderM()}
function cur(){return SS[aid]}
function renderS(){
  let h='';for(let[k,v]of Object.entries(SS).sort((a,b)=>b[1].ts-a[1].ts)){
    h+=`<div class="sess${k===aid?' on':''}" onclick="switchS('${k}')"><span class="name" ondblclick="event.stopPropagation();renameS('${k}')">${v.name}</span><span class="x" onclick="event.stopPropagation();delS('${k}')">✕</span></div>`}
  document.getElementById('sessions').innerHTML=h
}
async function renameS(id){let n=prompt('名称:',SS[id].name);if(n){SS[id].name=n;await saveS();renderS()}}
function renderM(){
  let d=document.getElementById('msgs');d.innerHTML='';let s=cur();if(!s)return;
  for(let m of s.h){
    if(m.t==='s')continue; // 摘要不渲染
    if(m.t==='u')d.innerHTML+=`<div class="msg u"><div class="bubble">${md(m.c)}</div></div>`;
    else if(m.t==='p')d.innerHTML+=`<div class="msg p"><div class="head">📋 计划</div><div>${esc(m.c)}</div></div>`;
    else if(m.t==='x')d.innerHTML+=`<div class="msg t"><div class="head">🔍 ${esc(m.l)}</div><div>${esc(m.c)}</div></div>`;
    else d.innerHTML+=`<div class="msg a"><div class="bubble">${md(m.c)}</div></div>`;
  }
  d.scrollTop=d.scrollHeight
}
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function md(s){
  s=esc(s);
  // 代码块 ```...```
  s=s.replace(/```(\w*)\n([\s\S]*?)```/g,'<pre><code>$2</code></pre>');
  // 内联代码 `...`
  s=s.replace(/`([^`]+)`/g,'<code>$1</code>');
  // 粗体 **...**
  s=s.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>');
  // 斜体 *...*
  s=s.replace(/\*(.+?)\*/g,'<em>$1</em>');
  // Markdown 表格 |...|
  let lines=s.split('\n'),out=[],inTable=0,tableRows=[];
  for(let i=0;i<lines.length;i++){
    let l=lines[i].trim();
    if(l.startsWith('|')&&l.endsWith('|')){
      let cells=l.split('|').slice(1,-1).map(c=>c.trim());
      if(cells.every(c=>/^[-:]+$/.test(c))){inTable=2;continue} // 分隔行
      if(inTable===0)inTable=1;
      tableRows.push(cells);
    }else{
      if(inTable>0){out.push(tbl(tableRows,inTable===2));tableRows=[];inTable=0}
      // 无序列表
      if(/^[-*]\s/.test(l))out.push('<li>'+l.replace(/^[-*]\s/,'')+'</li>');
      // 有序列表
      else if(/^\d+\.\s/.test(l))out.push('<li>'+l.replace(/^\d+\.\s/,'')+'</li>');
      else if(l)out.push('<p>'+l+'</p>');
      else out.push('');
    }
  }
  if(inTable>0)out.push(tbl(tableRows,inTable===2));
  // 包裹连续 <li>
  let r=[],inUl=0;
  for(let p of out){
    if(p.startsWith('<li>')){if(!inUl){r.push('<ul>');inUl=1}r.push(p)}
    else{if(inUl){r.push('</ul>');inUl=0}r.push(p)}
  }
  if(inUl)r.push('</ul>');
  return r.join('');
}
function tbl(rows,hasHeader){
  let h='<table>',start=0;
  if(hasHeader){h+='<thead><tr>'+rows[0].map(c=>'<th>'+c+'</th>').join('')+'</tr></thead>';start=1}
  h+='<tbody>'+rows.slice(start).map(r=>'<tr>'+r.map(c=>'<td>'+c+'</td>').join('')+'</tr>').join('')+'</tbody></table>';
  return h;
}

// ============== UI HELPERS ==============
function add(t,c,l){c=c||'';if(t==='u')cur().h.push({t:'u',c});else if(t==='p')cur().h.push({t:'p',c});else if(t==='x')cur().h.push({t:'x',c,l:l||''});else cur().h.push({t:'a',c});renderM()}
function load(){let d=document.getElementById('msgs');d.innerHTML+='<div class="msg a"><div class="dots"><span></span><span></span><span></span></div></div>';d.scrollTop=d.scrollHeight}
function unload(){let d=document.getElementById('msgs');let r=d.lastElementChild;if(r&&r.querySelector('.dots'))r.remove()}

// ============== STATUS ==============
async function chk(){
  try{let r=await fetch('/api/health');r=await r.json();
    if(r.ok){document.getElementById('dot').className='dot g';document.getElementById('stat').textContent='已连接';document.getElementById('btn').disabled=false;document.getElementById('inp').disabled=false;return}
  }catch(e){}
  document.getElementById('dot').className='dot r';document.getElementById('stat').textContent='未连接';document.getElementById('btn').disabled=true;document.getElementById('inp').disabled=true
}

// ============== API ==============
async function search(q){let r=await fetch('/api/search?q='+encodeURIComponent(q));return await r.text()}
async function callLM(ms,tools){
  let body={model:'gemma',messages:ms,temperature:0.1};
  if(tools)body.tools=tools;
  let r=await fetch('/api/lm',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  if(!r.ok)throw new Error('LM Studio: '+r.status);
  let d=await r.json();
  if(d.usage){toks+=d.usage.total_tokens||(d.usage.prompt_tokens+d.usage.completion_tokens)||0;document.getElementById('toks').textContent='本次对话：'+toks+' token'}
  return d.choices[0].message
}
function mkTools(){return[{type:'function',function:{name:'web_search',description:'搜索互联网获取实时信息。',parameters:{type:'object',properties:{query:{type:'string',description:'搜索关键词'}},required:['query']}}},{type:'function',function:{name:'run_shell',description:'在{OS}上执行终端命令。危险命令（如rm、sudo等）弹窗确认。',parameters:{type:'object',properties:{command:{type:'string',description:'要执行的Shell命令'}},required:['command']}}}]}

// ============== CONTEXT ==============
function estTokens(ms){return Math.ceil(JSON.stringify(ms).length/2.5)}
function trimByBudget(ms,maxT){
  while(estTokens(ms)>maxT&&ms.length>2){
    // 从位置1开始找第一个user消息（跳过system），删除 user+assistant 对
    let found=-1;
    for(let i=1;i<ms.length-1;i++){if(ms[i].role==='user'){found=i;break}}
    if(found<0)break;
    ms.splice(found,2);
  }
  return ms;
}
async function maybeSummarize(){
  let ua=cur().h.filter(m=>m.t==='u'||m.t==='a');
  if(ua.length<=16)return;
  // 取前半部分做摘要
  let half=ua.slice(0,Math.floor(ua.length/2)).map(m=>m.t==='u'?'用户: '+m.c:'助手: '+m.c).join('\n');
  let sp='将以下对话压缩为一段简短摘要（100字以内），保留关键信息和结论：\n'+half.substring(0,3000);
  try{
    let r=await callLM([{role:'system',content:sp},{role:'user',content:'请生成摘要'}],null);
    if(r.content){
      // 删除被摘要的原始消息，插入摘要
      // 删前半 user+assistant，插入摘要
      let uaAll=cur().h.filter(m=>m.t==='u'||m.t==='a');
      let delCount=Math.floor(uaAll.length/2);
      let indices=[];
      for(let i=0;i<cur().h.length;i++){
        let m=cur().h[i];
        if((m.t==='u'||m.t==='a')&&indices.length<delCount){indices.push(i)}
      }
      // 从后往前删
      for(let i=indices.length-1;i>=0;i--){cur().h.splice(indices[i],1)}
      // 在开头插入摘要
      cur().h.unshift({t:'s',c:r.content});
      await saveS();
    }
  }catch(e){console.error('摘要失败:',e)}
}

// ============== AGENT ==============
async function plan(um){
  let m=await callLM([{role:'system',content:'你是运行在{OS}上的助手，具备以下能力。收到用户问题先理解，然后列出解决此问题需要的命令步骤。简练，不需编号。（1）需要实时信息时用 web_search 搜索。（2）可直接执行 Shell 命令获取系统信息。'},{role:'user',content:um}],null);
  let p=m.content?.trim();if(p)add('p',p);return p||'';
}
async function run(um){
  // 上下文管理：摘要检查
  await maybeSummarize();
  let p=await plan(um);
  let sy=SYS;if(p)sy+='\n\n【计划】\n'+p;
  let tools=mkTools(),ms=[{role:'system',content:sy}];
  // 收集历史：摘要 + 最近消息
  let allH=cur().h.filter(m=>m.t==='u'||m.t==='a'||m.t==='s');
  let summary=allH.filter(m=>m.t==='s').pop();
  if(summary)ms.push({role:'system',content:'【对话摘要】'+summary.c});
  let recent=allH.filter(m=>m.t!=='s').slice(-8).flatMap(m=>m.t==='u'?[{role:'user',content:m.c}]:[{role:'assistant',content:m.c}]);
  ms.push(...recent);ms.push({role:'user',content:um});
  // Token 预算控制
  ms=trimByBudget(ms,8000);
  let sc=0;
  for(let t=0;t<6;t++){
    if(sc>=2&&ms.filter(m=>m.role==='system'&&m.content.includes('必须回答')).length===0){
      ms.push({role:'system',content:'[系统] 你已搜索'+sc+'次。现在请直接基于结果回答，不要继续搜索。'});
    }
    let m=await callLM(ms,tools);
    if(m.tool_calls){
      ms.push({role:'assistant',content:'',tool_calls:m.tool_calls});
      for(let tc of m.tool_calls){
        let nm=tc.function.name,args=JSON.parse(tc.function.arguments),r='';
        if(nm==='web_search'){sc++;r=await search(args.query);add('x','搜索#'+sc,JSON.stringify(args)+' -> '+r.length+'字')}
        else if(nm==='run_shell'){
          let cmd=args.command||'';
          add('x','Shell',cmd);
          let chk=await(await fetch('/api/shell/check?cmd='+encodeURIComponent(cmd))).json();
          if(chk.dangerous){
            // 命中黑名单 → 弹窗确认
            if(confirm('⚠️ 风险指令!\n\n'+cmd+'\n\n风险: '+chk.reason+'\n\n确定执行?')){
              let resp=await fetch('/api/shell/exec',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({command:cmd,force:true})});
              r=await resp.text();
            }else{r='[已拒绝] 用户取消了风险命令'}
          }else{
            // 常规命令 → 直接执行
            let resp=await fetch('/api/shell/exec',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({command:cmd,force:true})});
            r=await resp.text();
          }
        }
        else r='未知工具:'+nm;
        ms.push({role:'tool',tool_call_id:tc.id,content:r.substring(0,2000)});
      }
    }else{
      add('a',m.content);await saveS();return m.content;
    }
  }
  // 兜底
  try{ms.push({role:'system',content:'现在请基于以上所有搜索结果直接回答。不要再搜索。'});let fm=await callLM(ms,null);add('a',fm.content);await saveS();return fm.content}catch(e){return '达到最大轮次'}
}

// ============== SEND ==============
async function send(){
  let t=document.getElementById('inp').value.trim();if(!t)return;
  // 如果正在处理中，加入等待队列
  if(document.getElementById('btn').disabled){
    if(pending){pending=null;document.getElementById('inp').value=t;document.getElementById('inp').style.color='';document.getElementById('inp').placeholder='输入消息...';return}
    pending=t;document.getElementById('inp').value='⏳ 等待上轮完成 (点击取消)';document.getElementById('inp').style.color='#86868b';
    return;
  }
  if(pending){t=pending;pending=null;document.getElementById('inp').style.color='';document.getElementById('inp').placeholder='输入消息...'}
  document.getElementById('inp').value='';document.getElementById('inp').style.height='auto';
  document.getElementById('btn').disabled=true;document.getElementById('inp').disabled=true;
  add('u',t);load();saveS().catch(()=>{});
  try{
    let r=await run(t);unload();
    if(cur().h.filter(m=>m.t==='u').length===1){cur().name=t.substring(0,16)+(t.length>16?'...':'');renderS()}
  }catch(e){unload();add('a','错误: '+e.message);chk()}
  document.getElementById('btn').disabled=false;document.getElementById('inp').disabled=false;document.getElementById('inp').focus();
  // 处理队列中的下一条
  if(pending){let next=pending;pending=null;document.getElementById('inp').value=next;send()}
}
document.getElementById('inp').addEventListener('click',function(){if(pending){pending=null;this.value='';this.style.color='';this.placeholder='输入消息...'}});
document.getElementById('inp').addEventListener('input',function(){this.style.height='auto';this.style.height=Math.min(this.scrollHeight,80)+'px'});

// ============== START ==============
(async()=>{
  document.getElementById('stat').textContent='启动中...';
  document.getElementById('toks').textContent='本次对话：0 token';
  try{await loadS()}catch(e){console.error('loadS:',e);document.getElementById('stat').textContent='会话加载失败'}
  document.getElementById('stat').textContent='检测中...';
  chk();setInterval(chk,10000);
})();
</script>
</body>
</html>"""

# ---- Shell 黑名单 ----
import re as _re
DANGEROUS_PATTERNS = [
    (_re.compile(r"rm\b"), "删除文件/目录"),
    (_re.compile(r"sudo\b"), "提权操作"),
    (_re.compile(r">\s*/dev/"), "写入块设备"),
    (_re.compile(r"mkfs\."), "格式化文件系统"),
    (_re.compile(r"dd\s+if="), "磁盘直接读写"),
    (_re.compile(r"chmod\s+(-R\s+)?777"), "开放所有权限"),
    (_re.compile(r":\(\)\s*\{"), "Fork 炸弹"),
    (_re.compile(r"\|\s*(ba)?sh\b"), "管道到 Shell"),
    (_re.compile(r"curl.*\|\s*(ba)?sh"), "curl 管道到 Shell"),
    (_re.compile(r"wget.*-O\s*-\s*\|"), "wget 管道到 Shell"),
    (_re.compile(r">\s*/etc/"), "修改系统配置"),
    (_re.compile(r"shutdown|reboot|halt"), "关机/重启"),
    (_re.compile(r"killall\s+-9"), "强制终止所有进程"),
]

def resolve_executable(cmd):
    """提取命令中的可执行文件并解析为全路径"""
    import shlex, shutil
    try:
        tokens = shlex.split(cmd)
        if not tokens: return None
        exe = tokens[0]
        if exe == "sudo" and len(tokens) > 1:
            exe = tokens[1]
        return shutil.which(exe)
    except Exception:
        return None

def check_dangerous(cmd):
    """返回 (is_dangerous, reason) — 同时检查原始命令和全路径"""
    # 1. 解析全路径，用全路径匹配黑名单（防 PATH 劫持）
    resolved = resolve_executable(cmd)
    if resolved:
        for pattern, reason in DANGEROUS_PATTERNS:
            if pattern.search(resolved) or pattern.search(cmd):
                return True, reason
    else:
        # 无法解析时回退到仅检查原始命令
        for pattern, reason in DANGEROUS_PATTERNS:
            if pattern.search(cmd):
                return True, reason
    # 2. 额外安全层：全路径不在系统目录 → 可疑
    if resolved and not resolved.startswith(("/bin/", "/usr/bin/", "/usr/sbin/", "/sbin/", "/opt/homebrew/")):
        # 但允许已知安全目录
        safe = False
        for prefix in ["/Library/Developer/CommandLineTools/", "/Applications/", os.path.expanduser("~/.homiclaw/")]:
            if resolved.startswith(prefix):
                safe = True
                break
        if not safe:
            return True, f"非系统路径: {resolved}"
    return False, None

def exec_shell(cmd):
    """执行 Shell 命令，返回 stdout+stderr，30s 超时"""
    import subprocess, shlex, os
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        out = r.stdout.strip()
        if r.stderr.strip():
            out += ("\n" if out else "") + r.stderr.strip()
        return out[:4000] if out else "(无输出)"
    except subprocess.TimeoutExpired:
        return "⏰ 命令超时 (30s)"
    except Exception as e:
        return f"❌ 执行失败: {e}"

class S(http.server.SimpleHTTPRequestHandler):
    def _proxy(self):
        n=int(self.headers.get("Content-Length",0));b=self.rfile.read(n) if n else b""
        try:
            r=urllib.request.Request(LM_STUDIO+"/chat/completions",data=b,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(r,timeout=120) as resp:
                d=resp.read();self.send_response(200);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(d)
        except Exception as e:
            self.send_response(502);self.send_header("Content-Type","application/json");self.end_headers()
            self.wfile.write(json.dumps({"error":str(e)}).encode())

    def _ok(self,code,d,ct=None):
        self.send_response(code);self.send_header("Content-Type",ct or "application/json");self.end_headers()
        self.wfile.write((d if isinstance(d,str) else json.dumps(d)).encode() if isinstance(d,str) else json.dumps(d).encode())

    def do_GET(self):
        if self.path.startswith("/api/search"):
            q=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("q",[""])[0]
            self._ok(200,web_search(q) if q else "搜索词为空","text/plain; charset=utf-8")
        elif self.path=="/api/sessions":self._ok(200,json.load(open(SESSIONS_FILE)) if os.path.exists(SESSIONS_FILE) else {})
        elif self.path=="/api/health":
            try:urllib.request.urlopen(LM_STUDIO+"/models",timeout=3);self._ok(200,{"ok":True})
            except:self._ok(503,{"ok":False})
        elif self.path.startswith("/api/shell/check"):
            q=urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("cmd",[""])[0]
            is_d,reason=check_dangerous(urllib.parse.unquote(q))
            self._ok(200,{"dangerous":is_d,"reason":reason or ""})
        else:
            self.send_response(200);self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Cache-Control","no-store");self.end_headers();self.wfile.write(HTML.replace("{OS}",OS_NAME).replace("{DIR}",DIR).replace("{PORT}",str(PORT)).encode())

    def do_POST(self):
        if self.path=="/api/sessions":
            n=int(self.headers.get("Content-Length",0));d=json.loads(self.rfile.read(n)) if n else {}
            with open(SESSIONS_FILE,"w") as f:json.dump(d,f,ensure_ascii=False,indent=2)
            self._ok(200,{"ok":True})
        elif self.path=="/api/lm":self._proxy()
        elif self.path=="/api/shell/exec":
            n=int(self.headers.get("Content-Length",0));d=json.loads(self.rfile.read(n).decode()) if n else {}
            cmd=d.get("command","");force=d.get("force",False)
            is_d,reason=check_dangerous(cmd)
            if is_d and not force:
                self._ok(403,{"error":"高危指令","reason":reason})
            else:
                self._ok(200,exec_shell(cmd),"text/plain; charset=utf-8")
        else:self.send_response(404);self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        for h,v in[("Access-Control-Allow-Origin","*"),("Access-Control-Allow-Methods","GET,POST,OPTIONS"),("Access-Control-Allow-Headers","Content-Type")]:
            self.send_header(h,v)
        self.end_headers()
    def log_message(self,*a):pass

if __name__=="__main__":
    print(f"\n  Mini Harness v3  →  http://{HOST}:{PORT}\n")
    http.server.HTTPServer((HOST,PORT),S).serve_forever()