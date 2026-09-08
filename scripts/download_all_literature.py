#!/usr/bin/env python3
import csv
import html
import json
import re
import sys
import time
from pathlib import Path
from urllib.parse import quote, unquote, urljoin, urlparse

import requests

INPUT = Path("literature/generative_social_science_ai_for_science_2023_2026.csv")
OUT = Path("literature_downloads")
PDF_DIR = OUT / "papers"
MANIFEST = OUT / "download_manifest.csv"
SUMMARY = OUT / "README.txt"
UA = "Mozilla/5.0 (compatible; AcademicLiteratureDownloader/1.0; +https://github.com/MengzhenJia/Silicon_sample)"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": UA})


def parse_rows(path: Path):
    lines = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    rows = []
    seen = set()
    for line_no, line in enumerate(lines[1:], 2):
        if ",http" not in line:
            continue
        title, url = line.rsplit(",", 1)
        title = title.strip().strip('"').replace('""', '"')
        url = url.strip()
        if not url.startswith("http"):
            continue
        if url in seen:
            continue
        seen.add(url)
        rows.append({"line": line_no, "title": title, "url": url})
    return rows


def safe_name(i, title):
    s = re.sub(r"[^A-Za-z0-9._ -]+", "_", title)
    s = re.sub(r"\s+", " ", s).strip(" ._")
    if not s:
        s = "paper"
    return f"{i:03d}_{s[:140]}.pdf"


def request_json(url, timeout=30):
    r = SESSION.get(url, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    return r.json()


def add_candidate(cands, url, source):
    if not url or not isinstance(url, str):
        return
    url = html.unescape(url.strip())
    if url.startswith("//"):
        url = "https:" + url
    if not url.startswith("http"):
        return
    if all(existing[0] != url for existing in cands):
        cands.append((url, source))


def arxiv_candidates(url):
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([^?#]+)", url)
    if not m:
        return []
    arxiv_id = m.group(1)
    arxiv_id = re.sub(r"\.pdf$", "", arxiv_id)
    return [(f"https://arxiv.org/pdf/{arxiv_id}.pdf", "arXiv")]


def doi_candidates(doi_url):
    doi = unquote(urlparse(doi_url).path.lstrip("/"))
    cands = []

    # DOI content negotiation sometimes returns a PDF directly.
    add_candidate(cands, doi_url, "DOI resolver")

    # Crossref often exposes publisher PDF links.
    try:
        data = request_json(f"https://api.crossref.org/works/{quote(doi, safe='')}")
        msg = data.get("message", {})
        for link in msg.get("link", []) or []:
            u = link.get("URL")
            ctype = (link.get("content-type") or "").lower()
            if "pdf" in ctype or (u and ".pdf" in u.lower()):
                add_candidate(cands, u, "Crossref")
    except Exception:
        pass

    # OpenAlex exposes legal OA repository/publisher locations.
    try:
        data = request_json(f"https://api.openalex.org/works/https://doi.org/{quote(doi, safe='/()')}")
        for key in ("best_oa_location", "primary_location"):
            loc = data.get(key) or {}
            add_candidate(cands, loc.get("pdf_url"), f"OpenAlex {key}")
        for loc in data.get("locations", []) or []:
            add_candidate(cands, (loc or {}).get("pdf_url"), "OpenAlex location")
    except Exception:
        pass

    # Semantic Scholar can expose an OA PDF when other metadata sources do not.
    try:
        data = request_json(
            "https://api.semanticscholar.org/graph/v1/paper/DOI:"
            + quote(doi, safe="")
            + "?fields=title,openAccessPdf"
        )
        oa = data.get("openAccessPdf") or {}
        add_candidate(cands, oa.get("url"), "Semantic Scholar OA")
    except Exception:
        pass

    return doi, cands


def extract_pdf_meta(landing_url):
    out = []
    try:
        r = SESSION.get(landing_url, timeout=35, allow_redirects=True)
        ctype = (r.headers.get("content-type") or "").lower()
        if "application/pdf" in ctype or r.content[:5] == b"%PDF-":
            add_candidate(out, r.url, "publisher direct")
            return out
        text = r.text[:2_000_000]
        patterns = [
            r'<meta[^>]+name=["\']citation_pdf_url["\'][^>]+content=["\']([^"\']+)',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']citation_pdf_url["\']',
            r'<meta[^>]+name=["\']pdf_url["\'][^>]+content=["\']([^"\']+)',
            r'<meta[^>]+property=["\']og:pdf["\'][^>]+content=["\']([^"\']+)',
        ]
        for pat in patterns:
            for m in re.finditer(pat, text, flags=re.I):
                add_candidate(out, urljoin(r.url, m.group(1)), "publisher metadata")
    except Exception:
        pass
    return out


def fetch_pdf(url, dest, accept_pdf=False):
    headers = {}
    if accept_pdf:
        headers["Accept"] = "application/pdf,application/octet-stream;q=0.9,*/*;q=0.1"
    tmp = dest.with_suffix(dest.suffix + ".part")
    try:
        with SESSION.get(url, headers=headers, timeout=(20, 90), allow_redirects=True, stream=True) as r:
            if r.status_code >= 400:
                return False, f"HTTP {r.status_code}", r.url
            ctype = (r.headers.get("content-type") or "").lower()
            first = b""
            size = 0
            with tmp.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    if not chunk:
                        continue
                    if not first:
                        first = chunk[:8]
                    f.write(chunk)
                    size += len(chunk)
                    if size > 150 * 1024 * 1024:
                        raise RuntimeError("file exceeds 150 MB")
            is_pdf = first.startswith(b"%PDF-") or "application/pdf" in ctype
            if not is_pdf:
                tmp.unlink(missing_ok=True)
                return False, f"not PDF ({ctype or 'unknown content-type'})", r.url
            tmp.replace(dest)
            return True, str(size), r.url
    except Exception as e:
        tmp.unlink(missing_ok=True)
        return False, f"{type(e).__name__}: {e}", url


def main():
    OUT.mkdir(exist_ok=True)
    PDF_DIR.mkdir(exist_ok=True)
    rows = parse_rows(INPUT)
    results = []
    ok_count = 0

    print(f"Unique literature links: {len(rows)}", flush=True)

    for i, row in enumerate(rows, 1):
        title, url = row["title"], row["url"]
        dest = PDF_DIR / safe_name(i, title)
        status = "failed"
        source = ""
        resolved = ""
        detail = ""
        candidates = []

        if "arxiv.org" in url:
            candidates.extend(arxiv_candidates(url))
        elif "doi.org" in url:
            doi, doi_cands = doi_candidates(url)
            candidates.extend(doi_cands)
            # Inspect the DOI landing page for citation_pdf_url metadata.
            candidates.extend(extract_pdf_meta(url))
        else:
            add_candidate(candidates, url, "original URL")

        tried = []
        for cand, cand_source in candidates:
            if cand in tried:
                continue
            tried.append(cand)
            accept_pdf = cand == url and "doi.org" in url
            success, info, final_url = fetch_pdf(cand, dest, accept_pdf=accept_pdf)
            if success:
                status = "downloaded"
                source = cand_source
                resolved = final_url
                detail = info
                ok_count += 1
                break
            detail = info
            time.sleep(0.15)

        if status != "downloaded":
            detail = (detail or "no public PDF candidate found")[:500]

        results.append({
            "index": i,
            "title": title,
            "original_url": url,
            "status": status,
            "source": source,
            "resolved_pdf_url": resolved,
            "filename": dest.name if status == "downloaded" else "",
            "bytes_or_error": detail,
            "candidates_tried": len(tried),
        })
        print(f"[{i:03d}/{len(rows)}] {status:10s} {title[:80]}", flush=True)
        time.sleep(0.25)

    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        w.writeheader()
        w.writerows(results)

    failed = len(rows) - ok_count
    SUMMARY.write_text(
        "Bulk literature download\n"
        "========================\n"
        f"Unique links in source table: {len(rows)}\n"
        f"PDFs downloaded: {ok_count}\n"
        f"Not directly downloadable as public PDFs: {failed}\n\n"
        "The downloader uses arXiv and publicly exposed/open-access PDF locations from DOI publishers, Crossref, OpenAlex, and Semantic Scholar. It does not bypass authentication or paywalls. See download_manifest.csv for per-paper status.\n",
        encoding="utf-8",
    )
    print(f"DONE downloaded={ok_count} failed={failed}", flush=True)


if __name__ == "__main__":
    main()
