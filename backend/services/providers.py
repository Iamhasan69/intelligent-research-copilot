import json, os, re
import httpx

GEMINI_MODELS=['gemini-3.8-flash','gemini-3.7-flash','gemini-3.6-flash','gemini-2.5-flash','gemini-2.5-pro']
GROQ_MODELS=['openai/gpt-oss-120b','openai/gpt-oss-20b','groq/compound','groq/compound-mini','qwen/qwen3.8-27b','llama-3.3-70b-versatile','llama-3.1-8b-instant']

class ProviderError(Exception): pass

async def verify(provider,key,model):
    if not key or len(key.strip())<10: raise ProviderError('API key is empty or too short.')
    if provider=='gemini':
        url=f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
        body={'contents':[{'parts':[{'text':'Reply with exactly: CONNECTION_OK'}]}]}
        async with httpx.AsyncClient(timeout=30) as c:r=await c.post(url,params={'key':key.strip()},json=body)
        if r.status_code>=400: raise ProviderError(f'Gemini HTTP {r.status_code}: {extract_error(r)}')
        return {'ok':True,'message':'Gemini connection verified','model':model}
    if provider=='groq':
        url='https://api.groq.com/openai/v1/chat/completions'
        body={'model':model,'messages':[{'role':'user','content':'Reply with exactly: CONNECTION_OK'}],'max_tokens':8}
        async with httpx.AsyncClient(timeout=30) as c:r=await c.post(url,headers={'Authorization':f'Bearer {key.strip()}','Content-Type':'application/json'},json=body)
        if r.status_code>=400: raise ProviderError(f'Groq HTTP {r.status_code}: {extract_error(r)}')
        return {'ok':True,'message':'Groq connection verified','model':model}
    raise ProviderError('Unsupported provider.')

def extract_error(r):
    try:
        d=r.json(); return d.get('error',{}).get('message') or d.get('message') or str(d)
    except:return r.text[:600]

async def generate(provider,key,model,prompt,use_web=False):
    if provider=='gemini': return await gemini_generate(key,model,prompt,use_web)
    if provider=='groq': return await groq_generate(key,model,prompt,use_web)
    raise ProviderError('Unsupported provider.')

async def gemini_generate(key,model,prompt,use_web=False):
    url=f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    body={'contents':[{'parts':[{'text':prompt}]}], 'generationConfig':{'temperature':0.2}}
    if use_web: body['tools']=[{'google_search':{}}]
    async with httpx.AsyncClient(timeout=120) as c:r=await c.post(url,params={'key':key},json=body)
    if r.status_code>=400: raise ProviderError(f'Gemini HTTP {r.status_code}: {extract_error(r)}')
    d=r.json(); text=''.join(p.get('text','') for c in d.get('candidates',[]) for p in c.get('content',{}).get('parts',[]) if p.get('text'))
    citations=[]
    for c in d.get('candidates',[]):
        gm=c.get('groundingMetadata',{})
        for ch in gm.get('groundingChunks',[]):
            web=ch.get('web',{}); 
            if web.get('uri'): citations.append({'url':web['uri'],'title':web.get('title','')})
    return {'text':text,'citations':citations,'raw':d}

async def groq_generate(key,model,prompt,use_web=False):
    if use_web and model in ('openai/gpt-oss-120b','openai/gpt-oss-20b'):
        url='https://api.groq.com/openai/v1/responses'
        body={'model':model,'input':prompt,'tools':[{'type':'browser_search'}]}
        async with httpx.AsyncClient(timeout=120) as c:r=await c.post(url,headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},json=body)
        if r.status_code>=400: raise ProviderError(f'Groq HTTP {r.status_code}: {extract_error(r)}')
        d=r.json(); text=d.get('output_text','')
        if not text:
            parts=[]
            for item in d.get('output',[]):
                for x in item.get('content',[]) if isinstance(item,dict) else []:
                    if isinstance(x,dict) and x.get('text'):parts.append(x['text'])
            text=''.join(parts)
        cites=[]
        def walk(x):
            if isinstance(x,dict):
                if x.get('url'): cites.append({'url':x['url'],'title':x.get('title','')})
                for v in x.values():walk(v)
            elif isinstance(x,list):
                for v in x:walk(v)
        walk(d)
        return {'text':text,'citations':cites,'raw':d}
    url='https://api.groq.com/openai/v1/chat/completions'
    body={'model':model,'messages':[{'role':'user','content':prompt}],'temperature':0.2,'max_tokens':6000}
    async with httpx.AsyncClient(timeout=120) as c:r=await c.post(url,headers={'Authorization':f'Bearer {key}','Content-Type':'application/json'},json=body)
    if r.status_code>=400: raise ProviderError(f'Groq HTTP {r.status_code}: {extract_error(r)}')
    d=r.json(); return {'text':d['choices'][0]['message']['content'],'citations':[],'raw':d}

def extract_json(text):
    text=text.strip()
    text=re.sub(r'^```(?:json)?\s*','',text,flags=re.I); text=re.sub(r'\s*```$','',text)
    try:return json.loads(text)
    except: pass
    m=re.search(r'\{.*\}',text,re.S)
    if m:
        try:return json.loads(m.group(0))
        except:pass
    m=re.search(r'\[.*\]',text,re.S)
    if m:
        try:return json.loads(m.group(0))
        except:pass
    return None
