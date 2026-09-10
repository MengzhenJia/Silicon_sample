#!/usr/bin/env python3
import csv, json, os, re, sys, time, unicodedata
from pathlib import Path
from urllib.parse import quote, urljoin, urlparse, parse_qs
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup

CURRENT = Path("literature/GENERATIVESS_list.csv")
OLD = Path("literature/generative_social_science_ai_for_science_2023_2026.csv")
OUTROOT = Path("downloaded_missing")
OUTDIR = OUTROOT / "papers"
OUTDIR.mkdir(parents=True, exist_ok=True)

FAILED_OLD = [
  "A survey of social network simulation in the LLM era: From classical models to Generative Agents",
  "Agentic AI for Sustainable Development: Leveraging Large Language Model-Enhanced Agent-Based Modeling for Complex Policy Strategies",
  "AI for science: Progress, challenges, and perspectives",
  "AI for Science: Opportunities, Challenges, and Future Directions",
  "AI mirrors experimental science to unlock new research",
  "AI-Generated Hypotheses and the Emergence of Autonomous Scientific Discovery",
  "Balancing Large Language Model Alignment and Algorithmic Fidelity in Social Science Research",
  "Can AI language models replace human participants?",
  "Can AI serve as a substitute for human subjects in software engineering research?",
  "Computational Basis of Large Language Models’ Decision Making in Social Simulation",
  "Correcting the Measurement Errors of AI-Assisted Labeling in Image Analysis Using Design-Based Supervised Learning",
  "Emergent cooperation and strategy adaptation in multi-agent systems: An extended coevolutionary theory with LLMs",
  "Foundation models for generalist medical artificial intelligence",
  "From Codebooks to Promptbooks: Extracting Information from Text with Generative Large Language Models",
  "Generative AI and simulation modeling: What do we need to know?",
  "Generative AI Meets Open-Ended Survey Responses: Research Participant Use of AI and Homogenization",
  "Integrating Generative Artificial Intelligence into Social Science Research: Measurement, Prompting, and Simulation",
  "Large Language Model-Driven Multi-Agent Simulation of Online Firestorms",
  "Machine Bias. How Do Generative Language Models Answer Opinion Polls?",
  "Navigating the path to autonomy: real-world lessons from an air-free self-driving laboratory",
  "On scientific foundation models: Rigorous definitions, key applications, and a comprehensive survey",
  "Piercing a Methodological Bubble: Large Language Models and the Social Sciences",
  "Quantifying Narrative Similarity Across Languages",
  "Real world community oriented high-definition social simulation: Combining reinforcement learning and large language models",
  "Scientific discovery in the age of artificial intelligence",
  "Simulating Human Decision-Making in Ultimatum Games using Large Language Models",
  "Simulating theory and society: large language models and generative artificial intelligence as new tools for sociological theorizing",
  "Social Cognition Simulation with Large Language Model-driven Agents",
  "The Mixed Subjects Design: Treating Large Language Models as Potentially Informative Observations",
  "The need for verification in artificial intelligence-driven scientific discovery",
  "The past, present and future of self-driving laboratories",
  "Using large language models in psychology"
]

UA = "Mozilla/5.0 (compatible; GenerativeSocialScienceLiteratureDownloader/2.0; +https://github.com/MengzhenJia/Silicon_sample)"
HEADERS = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.9,*/*;q=0.8"}
TIMEOUT = 22
MAX_BYTES = 80 * 1024 * 1024

def norm_title(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def clean_filename(title, idx):
    s = unicodedata.normalize("NFKC", title or "paper")
    s = re.sub(r'[\\/:*?"<>|\r\n\t]+', "_", s)
    s = re.sub(r"\s+", " ", s).strip(" ._")[:180].rstrip(" ._")
    return f"{idx:03d}_{s}.pdf"

def extract_doi(link):
    m = re.search(r'(?:doi\.org/)?(10\.\d{4,9}/[^\s?#]+)', link or "", re.I)
    return m.group(1).rstrip(".,;)").lower() if m else None

def extract_arxiv(link):
    if not link: return None
    for p in [r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?',
              r'10\.48550/arxiv\.(\d{4}\.\d{4,5})(?:v\d+)?']:
        m = re.search(p, link, re.I)
        if m: return m.group(1)
    return None

def add(cands, url, source):
    if not url: return
    url = str(url).replace("&amp;", "&").strip()
    if url.startswith("//"): url = "https:" + url
    if url.startswith(("http://","https://")) and all(u != url for u,_ in cands):
        cands.append((url, source))

def get_json(url, params=None):
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        if r.ok: return r.json()
    except Exception:
        pass
    return None

def openalex_candidates(title, doi, cands):
    try:
        work = None
        if doi:
            work = get_json(f"https://api.openalex.org/works/https://doi.org/{quote(doi, safe='')}")
        if work:
            locs = [work.get("best_oa_location"), work.get("primary_location")] + (work.get("locations") or [])
            for loc in locs:
                if isinstance(loc, dict): add(cands, loc.get("pdf_url"), "OpenAlex")
        if not any("OpenAlex" in s for _,s in cands):
            data = get_json("https://api.openalex.org/works", {"search": title, "per-page": 5})
            if data:
                target = norm_title(title)
                scored = [(SequenceMatcher(None, target, norm_title(w.get("title",""))).ratio(), w)
                          for w in data.get("results",[])]
                for score,w in sorted(scored, reverse=True, key=lambda x:x[0]):
                    if score < 0.76: continue
                    locs = [w.get("best_oa_location"), w.get("primary_location")] + (w.get("locations") or [])
                    for loc in locs:
                        if isinstance(loc, dict): add(cands, loc.get("pdf_url"), f"OpenAlex-title-{score:.2f}")
                    if score >= 0.90: break
    except Exception:
        pass

def crossref_candidates(doi, cands):
    if not doi: return
    try:
        data = get_json(f"https://api.crossref.org/works/{quote(doi, safe='')}")
        if not data: return
        for x in (data.get("message",{}).get("link") or []):
            if not isinstance(x,dict): continue
            url=x.get("URL"); ct=(x.get("content-type") or "").lower()
            if url and ("pdf" in ct or ".pdf" in url.lower()):
                add(cands,url,"Crossref")
    except Exception:
        pass

def semantic_candidate(doi,cands):
    if not doi: return
    try:
        data=get_json(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{quote(doi, safe='')}",
                      {"fields":"title,openAccessPdf"})
        if data:
            add(cands,(data.get("openAccessPdf") or {}).get("url"),"SemanticScholar")
    except Exception:
        pass

def html_candidates(page_url,cands):
    try:
        r=requests.get(page_url,headers=HEADERS,timeout=TIMEOUT,allow_redirects=True)
        if not r.ok or "html" not in (r.headers.get("content-type") or "").lower(): return
        soup=BeautifulSoup(r.text[:2_000_000],"html.parser")
        for key in ["citation_pdf_url","eprints.document_url"]:
            tag=soup.find("meta",attrs={"name":re.compile(f"^{re.escape(key)}$",re.I)})
            if tag: add(cands,urljoin(r.url,tag.get("content")),"HTML-meta")
        for a in soup.find_all("a",href=True):
            href=a["href"]; h=href.lower(); txt=a.get_text(" ",strip=True).lower()
            if ".pdf" in h or "/pdf" in h or txt in {"pdf","download pdf","full text pdf"}:
                add(cands,urljoin(r.url,href),"HTML-link")
                if len(cands)>=18: break
    except Exception:
        pass

def build_candidates(title,link):
    c=[]
    arx=extract_arxiv(link); doi=extract_doi(link)
    if arx:
        add(c,f"https://arxiv.org/pdf/{arx}","arXiv")
        add(c,f"https://export.arxiv.org/pdf/{arx}","arXiv-export")
    low=(link or "").lower()
    if "openreview.net" in low:
        q=parse_qs(urlparse(link).query)
        if q.get("id"): add(c,f"https://openreview.net/pdf?id={q['id'][0]}","OpenReview")
    if doi:
        d=doi
        if d.startswith("10.18653/v1/"):
            slug=d.split("10.18653/v1/",1)[1]
            add(c,f"https://aclanthology.org/{slug}.pdf","ACL-Anthology")
        if d.startswith(("10.31235/osf.io/","10.31234/osf.io/")):
            osfid=d.split("osf.io/",1)[1].split("_")[0]
            add(c,f"https://osf.io/{osfid}/download","OSF")
        if d.startswith("10.3386/w"):
            w=d.split("10.3386/",1)[1]
            add(c,f"https://www.nber.org/system/files/working_papers/{w}/{w}.pdf","NBER")
        if d.startswith(("10.1038/","10.1057/")):
            add(c,f"https://www.nature.com/articles/{d.split('/',1)[1]}.pdf","Nature")
        if d.startswith("10.1371/journal.pone."):
            add(c,f"https://journals.plos.org/plosone/article/file?id={d}&type=printable","PLOS")
        if d.startswith("10.1145/"): add(c,f"https://dl.acm.org/doi/pdf/{d}","ACM")
        if d.startswith("10.1111/"): add(c,f"https://onlinelibrary.wiley.com/doi/pdfdirect/{d}","Wiley")
        crossref_candidates(d,c)
        openalex_candidates(title,d,c)
        if len(c)<3: semantic_candidate(d,c)
    else:
        openalex_candidates(title,None,c)
    if len(c)<3:
        html_candidates(link,c)
    return c

def try_download(url,dst):
    try:
        with requests.get(url,headers=HEADERS,timeout=TIMEOUT,stream=True,allow_redirects=True) as r:
            if r.status_code!=200: return False,f"HTTP {r.status_code}"
            ct=(r.headers.get("content-type") or "").lower()
            data=bytearray()
            for chunk in r.iter_content(256*1024):
                if chunk:
                    data.extend(chunk)
                    if len(data)>MAX_BYTES: return False,"too large"
            if not bytes(data[:5])==b"%PDF":
                return False,f"not PDF ({ct or 'unknown'}; {len(data)} bytes)"
            dst.write_bytes(data)
            return True,str(len(data))
    except Exception as e:
        return False,f"{type(e).__name__}: {str(e)[:160]}"

def load_missing():
    current=list(csv.DictReader(CURRENT.open(encoding="utf-8-sig")))
    old=list(csv.DictReader(OLD.open(encoding="utf-8-sig")))
    old_norm={norm_title(r["Title"]) for r in old}
    failed_norm={norm_title(x) for x in FAILED_OLD}
    missing=[]
    for r in current:
        n=norm_title(r["Title"])
        if n not in old_norm or n in failed_norm:
            missing.append(r)
    return missing

rows=load_missing()
with (OUTROOT/"missing_input.csv").open("w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["Title","Link"]); w.writeheader(); w.writerows(rows)
print(f"MISSING_COUNT={len(rows)}",flush=True)

def process(item):
    idx,row=item
    title=row["Title"].strip(); link=row["Link"].strip()
    fn=clean_filename(title,idx); dst=OUTDIR/fn
    cands=build_candidates(title,link)
    errs=[]
    for url,src in cands[:18]:
        ok,msg=try_download(url,dst)
        if ok:
            return {"index":idx,"title":title,"original_url":link,"status":"downloaded",
                    "source":src,"resolved_pdf_url":url,"filename":fn,
                    "bytes_or_error":msg,"candidates_tried":len(errs)+1}
        errs.append(f"{src}: {msg}")
    return {"index":idx,"title":title,"original_url":link,"status":"failed",
            "source":"","resolved_pdf_url":"","filename":"",
            "bytes_or_error":" | ".join(errs[-10:])[:3000] if errs else "no candidate PDF URL",
            "candidates_tried":len(cands[:18])}

results=[]
with ThreadPoolExecutor(max_workers=8) as ex:
    futs={ex.submit(process,(i,r)):i for i,r in enumerate(rows,1)}
    for fut in as_completed(futs):
        res=fut.result(); results.append(res)
        print(f"[{len(results)}/{len(rows)}] {res['status'].upper()} {res['title'][:100]}",flush=True)

results.sort(key=lambda r:r["index"])
fields=["index","title","original_url","status","source","resolved_pdf_url","filename","bytes_or_error","candidates_tried"]
for path, subset in [
    (OUTROOT/"download_results.csv", results),
    (OUTROOT/"failed_downloads.csv", [r for r in results if r["status"]=="failed"]),
    (OUTROOT/"downloaded_manifest.csv", [r for r in results if r["status"]=="downloaded"]),
]:
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(subset)

ok=sum(r["status"]=="downloaded" for r in results)
print(f"SUMMARY downloaded={ok} failed={len(results)-ok} total={len(results)}",flush=True)
print('FAILED_LIST_BEGIN', flush=True)
for r in results:
    if r['status'] == 'failed':
        reason = str(r['bytes_or_error']).replace('\n',' ').replace('|',';')
        print(f"FAILED|{r['title']}|{r['original_url']}|{reason}", flush=True)
print('FAILED_LIST_END', flush=True)
