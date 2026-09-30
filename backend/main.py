import os, json, asyncio, csv, io, time
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from .services import db
from .services.providers import verify, ProviderError, GEMINI_MODELS, GROQ_MODELS
from .services.scanner import parse_file
from .services.agent import run_research

load_dotenv(Path(__file__).resolve().parents[1]/'.env')
db.init_db()
app=FastAPI(title='Intelligent Research Copilot',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])
UPLOAD=Path(__file__).resolve().parents[1]/'data'/'uploads'; UPLOAD.mkdir(parents=True,exist_ok=True)

class ProviderIn(BaseModel): provider:str; model:str; api_key:str
class ResearchIn(BaseModel):
    query:str=Field(min_length=5,max_length=12000)
    provider:str='gemini'; model:str='gemini-3.8-flash'
    urls:list[str]=[]
    file_ids:list[int]=[]
    file_context:list[dict]=[]

@app.get('/api/health')
def health(): return {'ok':True,'service':'Intelligent Research Copilot','version':'1.0.0'}

@app.get('/api/providers')
def providers():
    return {'gemini':GEMINI_MODELS,'groq':GROQ_MODELS,'saved':db.get_settings()}

@app.post('/api/providers/verify')
async def provider_verify(x:ProviderIn):
    try:
        out=await verify(x.provider,x.api_key,x.model); db.save_settings(x.provider,x.model,x.api_key,1); return out
    except ProviderError as e: raise HTTPException(status_code=400,detail=str(e))

@app.post('/api/providers/disconnect')
def disconnect(x:dict):
    db.save_settings(x.get('provider'),x.get('model',''),'',0); return {'ok':True}

@app.post('/api/files')
async def upload(files:list[UploadFile]=File(...)):
    out=[]
    allowed={'.pdf','.docx','.txt','.md','.csv','.json','.log'}
    for f in files:
        ext=Path(f.filename or '').suffix.lower()
        if ext not in allowed: raise HTTPException(400,f'Unsupported file: {f.filename}')
        data=await f.read()
        if len(data)>20*1024*1024: raise HTTPException(400,f'File too large: {f.filename}')
        path=UPLOAD/f'{int(time.time()*1000)}_{Path(f.filename).name}'
        path.write_bytes(data)
        parsed=parse_file(path)
        # Store a source row detached from a research; research copies it by id below.
        out.append({'file_id':str(path),'name':f.filename,'parsed':parsed})
    return out

@app.get('/api/researches')
def researches(): return db.list_researches()

@app.get('/api/researches/{rid}')
def research(rid:int):
    r=db.get_research(rid)
    if not r: raise HTTPException(404,'Research not found')
    return r

@app.post('/api/researches')
async def create(x:ResearchIn, background_tasks:BackgroundTasks):
    key=db.get_key(x.provider)
    if not key: raise HTTPException(400,f'No connected {x.provider} API key. Open Settings and Verify & Connect.')
    rid=db.create_research(x.query,x.provider,x.model)
    background_tasks.add_task(_run,rid,x,key)
    return {'id':rid,'status':'planning'}

async def _run(rid,x,key):
    try:
        files=[]
        for fid in x.file_ids:
            # reserved for future persistent upload IDs; current upload endpoint returns parsed file payload.
            pass
        await run_research(rid,x.query,x.provider,key,x.model,x.urls,x.file_context)
    except Exception as e:
        db.update_research(rid,status='failed',report=f'Agent failed: {e}')
        db.add_event(rid,'ERROR','Research failed',str(e))

@app.get('/api/researches/{rid}/export.json')
def export_json(rid:int):
    r=db.get_research(rid)
    if not r: raise HTTPException(404)
    return JSONResponse(r)

@app.get('/api/researches/{rid}/export.csv')
def export_csv(rid:int):
    r=db.get_research(rid)
    if not r: raise HTTPException(404)
    rows=r['dataset']; keys=sorted({k for row in rows for k in row.keys()}) if rows else ['data']
    s=io.StringIO(); w=csv.DictWriter(s,fieldnames=keys); w.writeheader();
    for row in rows:w.writerow({k:row.get(k) for k in keys})
    return StreamingResponse(iter([s.getvalue()]),media_type='text/csv',headers={'Content-Disposition':f'attachment; filename=research-{rid}.csv'})

@app.get('/api/researches/{rid}/export.md')
def export_md(rid:int):
    r=db.get_research(rid)
    if not r: raise HTTPException(404)
    md=f'# {r["title"]}\n\n## Query\n{r["query"]}\n\n{r.get("report","")}\n\n## Sources\n' + '\n'.join(f'- [{s.get("title")}]({s.get("url")})' for s in r['sources'])
    return PlainTextResponse(md,headers={'Content-Disposition':f'attachment; filename=research-{rid}.md'})

from fastapi.staticfiles import StaticFiles
app.mount('/', StaticFiles(directory=Path(__file__).resolve().parents[1]/'frontend', html=True), name='frontend')
