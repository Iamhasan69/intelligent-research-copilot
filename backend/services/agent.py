import json, re
from urllib.parse import urlparse
from . import db
from .providers import generate, extract_json, ProviderError
from .scanner import fetch_url

PLANNER='''You are the planning module of an AI research agent. Convert the user's research request into a concrete, auditable workflow. Return JSON only with keys: objective, subquestions (array), search_queries (array), source_types (array), deliverables (array), verification_rules (array). Keep it practical and specific. Do not invent facts.'''

async def plan(query, provider,key,model):
    r=await generate(provider,key,model,PLANNER+'\nUSER REQUEST:\n'+query)
    p=extract_json(r['text'])
    if not p:p={'objective':query,'subquestions':[query],'search_queries':[query],'source_types':['official websites','reputable reporting','primary documents'],'deliverables':['evidence-backed report','structured dataset','source list'],'verification_rules':['prefer primary sources','flag conflicts','never invent missing fields']}
    return p

def host_allowed(url):
    h=(urlparse(url).hostname or '').lower()
    blocked=('localhost','127.','0.0.0.0','::1','169.254.','10.','192.168.','172.16.','172.17.','172.18.','172.19.','172.2','172.30.','172.31.')
    return bool(h) and not any(h.startswith(x) for x in blocked)

async def run_research(rid,query,provider,key,model,urls=None,files=None):
    db.add_event(rid,'PLAN','Building research plan')
    p=await plan(query,provider,key,model)
    db.add_event(rid,'PLAN','Plan created',json.dumps(p))
    sources=[]
    # Explicit URLs/files are first-class evidence.
    for u in urls or []:
        if not host_allowed(u):
            db.add_event(rid,'COLLECT',f'Skipped unsafe URL: {u}')
            continue
        try:
            s=await fetch_url(u); sid=db.add_source(rid,**s); s['id']=sid; sources.append(s); db.add_event(rid,'COLLECT',f'Read {u}')
        except Exception as e: db.add_event(rid,'COLLECT',f'URL failed: {u}',str(e))
    for f in files or []:
        sid=db.add_source(rid,**f); f['id']=sid; sources.append(f); db.add_event(rid,'COLLECT',f'Indexed file {f["title"]}')
    # Discovery is delegated to provider grounding/browser search.
    discovery_prompt=f'''Research task: {query}\nPlan: {json.dumps(p)}\nFind authoritative and diverse public sources. Prefer official documents, company/government pages, standards, research papers and reputable reporting. Provide a concise evidence-oriented synthesis. Include URLs in the answer when possible. Clearly distinguish facts, claims and uncertainty.'''
    db.add_event(rid,'DISCOVER','Searching public sources')
    web=await generate(provider,key,model,discovery_prompt,use_web=True)
    for c in web.get('citations',[]):
        if c.get('url') and host_allowed(c['url']) and not any(x.get('url')==c['url'] for x in sources):
            try:
                s=await fetch_url(c['url']); s['title']=c.get('title') or s['title']; sid=db.add_source(rid,**s); s['id']=sid; sources.append(s)
            except: pass
    db.add_event(rid,'COLLECT',f'Collected {len(sources)} evidence sources')
    # Keep context bounded but source traceability preserved in DB.
    context=[]
    for i,s in enumerate(sources):
        context.append(f'''SOURCE {i+1} [ID {s["id"]}]\nTITLE: {s.get("title")}\nURL: {s.get("url")}\nCONTENT:\n{s.get("content","")[:12000]}''')
    context_text='\n\n'.join(context)
    synthesis=f'''You are the synthesis and verification engine of a research copilot. User request: {query}\nPlan: {json.dumps(p)}\n\nEVIDENCE SOURCES:\n{context_text}\n\nReturn JSON only with keys: report_markdown, dataset (array of objects), entities (array of {{name,type,description}}), relationships (array of {{source,target,type}}), evidence (array of {{source_id,claim,quote,confidence}}), conflicts (array of {{topic,positions,reason}}), limitations (array).\nRules: Every factual dataset value must be traceable to a source_id when possible. Never fabricate. If a field is unknown use null. Confidence is 0..1. Quotes must be short excerpts, not long passages. Deduplicate entities. Explicitly flag conflicts and stale/uncertain evidence.''' 
    db.add_event(rid,'PROCESS','Verifying, deduplicating and synthesizing evidence')
    final=await generate(provider,key,model,synthesis)
    result=extract_json(final['text'])
    if not result:
        result={'report_markdown':final['text'],'dataset':[],'entities':[],'relationships':[],'evidence':[],'conflicts':[],'limitations':['Model did not return structured JSON.'],}
    for ev in result.get('evidence',[]):
        try: db.add_evidence(rid,int(ev.get('source_id')),ev.get('claim',''),ev.get('quote',''),float(ev.get('confidence',0.5)))
        except: pass
    db.update_research(rid,status='completed',report=result.get('report_markdown',''),dataset_json=json.dumps(result.get('dataset',[])),graph_json=json.dumps({'entities':result.get('entities',[]),'relationships':result.get('relationships',[]),'conflicts':result.get('conflicts',[]),'limitations':result.get('limitations',[])}))
    db.add_event(rid,'DELIVER','Research completed',f'{len(sources)} sources')
    return db.get_research(rid)
