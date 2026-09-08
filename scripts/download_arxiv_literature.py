#!/usr/bin/env python3
import csv
import hashlib
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "downloaded_literature"
PDF_DIR = OUT_DIR / "pdfs"
MANIFEST = OUT_DIR / "manifest.csv"
FAILED = OUT_DIR / "failed.csv"
USER_AGENT = "Mozilla/5.0 (compatible; SiliconSampleLiteratureDownloader/1.0; +https://github.com/MengzhenJia/Silicon_sample)"
MAX_WORKERS = 4


def collect_records():
    records = {}
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    for csv_path in csv_files:
        with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                arxiv_id = (row.get("arxiv_id") or "").strip()
                arxiv_url = (row.get("arxiv_url") or "").strip()
                if not arxiv_id and arxiv_url:
                    m = re.search(r"arxiv\.org/(?:abs|pdf)/([^?#/]+)", arxiv_url)
                    if m:
                        arxiv_id = m.group(1).removesuffix(".pdf")
                if not arxiv_id:
                    continue
                records.setdefault(arxiv_id, {
                    "arxiv_id": arxiv_id,
                    "title": (row.get("title") or "").strip(),
                    "year": (row.get("year") or row.get("v1_year") or "").strip(),
                    "category": (row.get("category") or row.get("reason") or "").strip(),
                    "scope": (row.get("scope") or "").strip(),
                    "source_csv": csv_path.name,
                    "arxiv_url": arxiv_url or f"https://arxiv.org/abs/{arxiv_id}",
                })
    return [records[k] for k in sorted(records)], csv_files


def download_one(rec):
    arxiv_id = rec["arxiv_id"]
    target = PDF_DIR / f"{arxiv_id}.pdf"
    urls = [
        f"https://arxiv.org/pdf/{arxiv_id}.pdf",
        f"https://export.arxiv.org/pdf/{arxiv_id}.pdf",
    ]
    last_error = ""
    for attempt in range(1, 4):
        for url in urls:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/pdf"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = resp.read()
                    content_type = (resp.headers.get("Content-Type") or "").lower()
                if not data.startswith(b"%PDF-"):
                    raise ValueError(f"response is not PDF; content-type={content_type}; bytes={len(data)}")
                target.write_bytes(data)
                return {
                    **rec,
                    "pdf_url": url,
                    "local_file": f"pdfs/{target.name}",
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "status": "ok",
                    "error": "",
                }
            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"
        time.sleep(min(12, 2 ** attempt))
    return {
        **rec,
        "pdf_url": urls[0],
        "local_file": "",
        "bytes": "",
        "sha256": "",
        "status": "failed",
        "error": last_error,
    }


def write_csv(path, rows):
    fields = [
        "arxiv_id", "year", "title", "category", "scope", "source_csv", "arxiv_url",
        "pdf_url", "local_file", "bytes", "sha256", "status", "error"
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    records, csv_files = collect_records()
    total = len(records)
    print(f"Found {total} unique arXiv records across {len(csv_files)} CSV files.", flush=True)
    results_by_id = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        future_map = {pool.submit(download_one, rec): rec for rec in records}
        completed = 0
        for future in as_completed(future_map):
            result = future.result()
            completed += 1
            results_by_id[result["arxiv_id"]] = result
            print(f"[{completed}/{total}] {result['arxiv_id']} -> {result['status']} {result.get('bytes','')} {result.get('error','')}", flush=True)
    results = [results_by_id[r["arxiv_id"]] for r in records]
    write_csv(MANIFEST, results)
    failures = [r for r in results if r["status"] != "ok"]
    write_csv(FAILED, failures)
    ok = total - len(failures)
    print(f"Completed: {ok}/{total} PDFs downloaded; failures={len(failures)}", flush=True)
    if failures:
        print("FAILED_IDS=" + ",".join(r["arxiv_id"] for r in failures), flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
