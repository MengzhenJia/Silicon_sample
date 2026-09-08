#!/usr/bin/env python3
import csv
import difflib
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

from download_all_literature import SESSION, OUT, PDF_DIR, MANIFEST, SUMMARY, fetch_pdf, safe_name


def norm_title(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def similarity(a, b):
    return difflib.SequenceMatcher(None, norm_title(a), norm_title(b)).ratio()


def request_json(url, timeout=30):
    r = SESSION.get(url, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    return r.json()


def add(cands, url, source):
    if not url or not isinstance(url, str) or not url.startswith("http"):
        return
    if all(u != url for u, _ in cands):
        cands.append((url, source))


def openalex_title_candidates(title):
    cands = []
    try:
        data = request_json("https://api.openalex.org/works?search=" + quote(title) + "&per-page=10")
        for work in data.get("results", []) or []:
            wt = work.get("title") or ""
            if similarity(title, wt) < 0.90:
                continue
            for key in ("best_oa_location", "primary_location"):
                loc = work.get(key) or {}
                add(cands, loc.get("pdf_url"), f"OpenAlex title {key}")
            for loc in work.get("locations", []) or []:
                add(cands, (loc or {}).get("pdf_url"), "OpenAlex title location")
    except Exception:
        pass
    return cands


def semantic_scholar_title_candidates(title):
    cands = []
    try:
        url = "https://api.semanticscholar.org/graph/v1/paper/search?query=" + quote(title) + "&limit=10&fields=title,openAccessPdf,externalIds"
        data = request_json(url)
        for paper in data.get("data", []) or []:
            pt = paper.get("title") or ""
            if similarity(title, pt) < 0.90:
                continue
            oa = paper.get("openAccessPdf") or {}
            add(cands, oa.get("url"), "Semantic Scholar title OA")
    except Exception:
        pass
    return cands


def arxiv_title_candidates(title):
    cands = []
    try:
        words = [w for w in re.findall(r"[A-Za-z0-9]+", title) if len(w) > 2][:12]
        if not words:
            return cands
        q = " ".join(words)
        url = "https://export.arxiv.org/api/query?search_query=all:" + quote(q) + "&start=0&max_results=10"
        r = SESSION.get(url, timeout=35)
        r.raise_for_status()
        root = ET.fromstring(r.text)
        ns = {"a": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("a:entry", ns):
            et = " ".join((entry.findtext("a:title", default="", namespaces=ns) or "").split())
            if similarity(title, et) < 0.92:
                continue
            eid = (entry.findtext("a:id", default="", namespaces=ns) or "").strip()
            m = re.search(r"arxiv\.org/abs/(.+)$", eid)
            if m:
                add(cands, f"https://arxiv.org/pdf/{m.group(1)}.pdf", "arXiv title match")
    except Exception:
        pass
    return cands


def europe_pmc_candidates(original_url):
    cands = []
    if "doi.org" not in original_url:
        return cands
    doi = original_url.split("doi.org/", 1)[1]
    try:
        data = request_json("https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:" + quote(doi) + "&format=json")
        for row in (data.get("resultList") or {}).get("result", []) or []:
            pmcid = row.get("pmcid")
            if pmcid:
                add(cands, f"https://europepmc.org/articles/{pmcid}?pdf=render", "Europe PMC")
    except Exception:
        pass
    return cands


def main():
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8-sig")))
    retried = 0
    recovered = 0

    for row in rows:
        if row.get("status") == "downloaded":
            continue
        retried += 1
        idx = int(row["index"])
        title = row["title"]
        original_url = row["original_url"]
        dest = PDF_DIR / safe_name(idx, title)
        cands = []
        cands.extend(openalex_title_candidates(title))
        cands.extend(semantic_scholar_title_candidates(title))
        cands.extend(arxiv_title_candidates(title))
        cands.extend(europe_pmc_candidates(original_url))

        tried = 0
        last = "no fallback candidate"
        for url, source in cands:
            tried += 1
            ok, info, final_url = fetch_pdf(url, dest, accept_pdf=False)
            if ok:
                row["status"] = "downloaded"
                row["source"] = source
                row["resolved_pdf_url"] = final_url
                row["filename"] = dest.name
                row["bytes_or_error"] = info
                row["candidates_tried"] = str(int(row.get("candidates_tried") or 0) + tried)
                recovered += 1
                print(f"[RECOVERED] {idx:03d} {title[:90]}", flush=True)
                break
            last = info
            time.sleep(0.15)
        else:
            row["bytes_or_error"] = last[:500]
            row["candidates_tried"] = str(int(row.get("candidates_tried") or 0) + tried)
            print(f"[STILL FAILED] {idx:03d} {title[:90]}", flush=True)
        time.sleep(0.2)

    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    ok_count = sum(r.get("status") == "downloaded" for r in rows)
    failed = len(rows) - ok_count
    SUMMARY.write_text(
        "Bulk literature download\n"
        "========================\n"
        f"Unique links in source table: {len(rows)}\n"
        f"PDFs downloaded: {ok_count}\n"
        f"Not directly downloadable as public PDFs: {failed}\n"
        f"Recovered by title/repository fallback: {recovered} of {retried} retried\n\n"
        "Sources attempted include arXiv, DOI publishers, Crossref, OpenAlex, Semantic Scholar, Europe PMC, and title-matched public repositories. The process does not bypass authentication or paywalls. See download_manifest.csv for per-paper status.\n",
        encoding="utf-8",
    )
    print(f"RETRY DONE recovered={recovered} total_downloaded={ok_count} failed={failed}", flush=True)


if __name__ == "__main__":
    main()
