import re, json, csv, io
from pathlib import Path
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader
from docx import Document

UA='IntelligentResearchCopilot/1.0 (+local research agent)'

def clean_text(text):
    text=re.sub(r'\s+',' ',text or '').strip()
    return text[:120000]

async def fetch_url(url):
    p=urlparse(url)
    if p.scheme not in ('http','https'): raise ValueError('Only http/https URLs are allowed.')
    if not p.hostname: raise ValueError('Invalid URL.')
    async with httpx.AsyncClient(timeout=20,follow_redirects=True,headers={'User-Agent':UA}) as client:
        r=await client.get(url)
        r.raise_for_status()
        ctype=r.headers.get('content-type','')
        if 'text/html' in ctype:
            soup=BeautifulSoup(r.text,'html.parser')
            for x in soup(['script','style','noscript','svg']): x.decompose()
            title=soup.title.get_text(' ',strip=True) if soup.title else p.hostname
            text=clean_text(soup.get_text(' ',strip=True))
        else:
            title=p.hostname; text=clean_text(r.text)
        return {'url':str(r.url),'title':title,'domain':p.hostname,'content':text,'snippet':text[:500],'source_type':'web'}

def parse_file(path:Path):
    ext=path.suffix.lower()
    if ext=='.pdf':
        reader=PdfReader(str(path)); text='\n'.join((p.extract_text() or '') for p in reader.pages)
    elif ext=='.docx': text='\n'.join(p.text for p in Document(str(path)).paragraphs)
    elif ext in ('.txt','.md','.log','.json','.csv'):
        text=path.read_text(encoding='utf-8',errors='ignore')
        if ext=='.json':
            try:text=json.dumps(json.loads(text),indent=2)
            except:pass
    else: raise ValueError('Unsupported file type. Use PDF, DOCX, TXT, MD, CSV, JSON or LOG.')
    return {'url':'file://'+str(path),'title':path.name,'domain':'local-file','content':clean_text(text),'snippet':clean_text(text)[:500],'source_type':'file'}
