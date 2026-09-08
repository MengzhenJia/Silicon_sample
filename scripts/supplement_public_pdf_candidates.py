#!/usr/bin/env python3
import csv
import html
import re
import shutil
import time
from pathlib import Path
from urllib.parse import urljoin

from download_all_literature import SESSION, PDF_DIR, MANIFEST, fetch_pdf, safe_name

SUPP = Path("literature_supplement")
SUPP_PAPERS = SUPP / "papers"

# Public/full-text locations found by exact-title web verification.
EXPLICIT = {
    9: [
        "https://papers.ssrn.com/sol3/Delivery.cfm/f0d88299-386e-4329-854e-52a014ef1706-MECA.pdf?abstractid=6790227&mirid=1",
    ],
    13: [
        "https://journals.sagepub.com/history/bc7b2953-fab6-498d-a727-b158e5f9abd3/27523543251365678.22854943.pdf",
    ],
    16: [
        "https://www.cell.com/action/showPdf?pii=S2666-6758%2826%2900277-8",
        "https://www.cell.com/the-innovation/pdf/S2666-6758(26)00277-8.pdf",
        "https://www.sciencedirect.com/science/article/pii/S2666675826002778/pdfft?isDTMRedir=true&download=true",
    ],
    17: [
        "https://www.techrxiv.org/doi/pdf/10.36227/techrxiv.173949768.84003950/v1",
    ],
    25: [
        "https://pubs.acs.org/doi/pdf/10.1021/acsmaterialslett.6c00224",
        "https://pubs.acs.org/doi/pdf/10.1021/acsmaterialslett.6c00224?download=1",
    ],
    42: [
        "https://www.cell.com/trends/cognitive-sciences/pdf/S1364-6613(23)00098-0.pdf",
        "https://www.cell.com/action/showPdf?pii=S1364-6613%2823%2900098-0",
    ],
    43: [
        "https://link.springer.com/content/pdf/10.1007/s10515-023-00409-6.pdf",
    ],
    56: [
        "https://arxiv.org/pdf/2504.11671.pdf",
    ],
    67: [
        "https://www.mdpi.com/2079-9292/12/12/2722/pdf",
        "https://mdpi-res.com/d_attachment/electronics/electronics-12-02722/article_deploy/electronics-12-02722-v2.pdf",
    ],
    77: [
        "https://cs.stanford.edu/~jure/pubs/medai-nature23.pdf",
    ],
    90: [
        "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/sdr.1773",
        "https://onlinelibrary.wiley.com/doi/pdf/10.1002/sdr.1773",
    ],
    91: [
        "https://osf.io/4esdp/download",
        "https://osf.io/download/4esdp/",
    ],
    109: [
        "https://www.mdpi.com/2076-3417/16/12/5870/pdf",
        "https://mdpi-res.com/d_attachment/applsci/applsci-16-05870/article_deploy/applsci-16-05870-v2.pdf",
    ],
    130: [
        "https://pubs.rsc.org/en/content/articlepdf/2026/dd/d6dd00269b",
    ],
    134: [
        "https://www.sciencedirect.com/science/article/pii/S0893608026000304/pdfft?isDTMRedir=true&download=true",
    ],
    140: [
        "https://link.springer.com/content/pdf/10.1007/s40647-026-00473-8.pdf",
    ],
    147: [
        "https://www.sciencedirect.com/science/article/pii/S0264275125007693/pdfft?isDTMRedir=true&download=true",
    ],
    157: [
        "https://www.nature.com/articles/s41586-023-06221-2.pdf",
    ],
    164: [
        "https://dl.acm.org/doi/pdf/10.1145/3715928.3737473",
    ],
    171: [
        "https://link.springer.com/content/pdf/10.1007/s11186-025-09606-6.pdf",
    ],
    176: [
        "https://www.china-simulation.com/EN/article/downloadArticleFile.do?attachType=PDF&id=3837",
    ],
    192: [
        "https://papers.ssrn.com/sol3/Delivery.cfm/5133034.pdf?abstractid=5133034&mirid=1",
    ],
    193: [
        "https://royalsocietypublishing.org/doi/pdf/10.1098/rsta.2024.0591",
    ],
    194: [
        "https://www.nature.com/articles/s41570-026-00847-2.pdf",
    ],
    205: [
        "https://www.nature.com/articles/s44159-023-00241-5.pdf",
    ],
}


def add_unique(out, url, source):
    if not url or not isinstance(url, str):
        return
    url = html.unescape(url.strip())
    if url.startswith("//"):
        url = "https:" + url
    if url.startswith("http") and all(u != url for u, _ in out):
        out.append((url, source))


def sage_public_version_candidates(doi):
    out = []
    pages = [
        f"https://journals.sagepub.com/doi/{doi}",
        f"https://journals.sagepub.com/doi/full/{doi}",
        f"https://journals.sagepub.com/doi/abs/{doi}",
    ]
    for page in pages:
        try:
            r = SESSION.get(page, timeout=35, allow_redirects=True)
            if r.status_code >= 400:
                continue
            text = r.text[:3_000_000]
            # SAGE exposes public article-version PDFs under /history/.../*.pdf.
            for m in re.finditer(r'''href=["']([^"']+(?:/history/[^"']+\.pdf|Version\d+\.pdf)[^"']*)["']''', text, flags=re.I):
                add_unique(out, urljoin(r.url, m.group(1)), "SAGE public article version")
            for m in re.finditer(r'''["'](https://journals\.sagepub\.com/history/[^"']+\.pdf)["']''', text, flags=re.I):
                add_unique(out, m.group(1), "SAGE public article version")
        except Exception:
            pass
    add_unique(out, f"https://journals.sagepub.com/doi/pdf/{doi}?download=true", "SAGE PDF endpoint")
    return out


def generic_candidates(original_url):
    out = []
    if "doi.org/" not in original_url:
        return out
    doi = original_url.split("doi.org/", 1)[1]
    dlow = doi.lower()
    if dlow.startswith("10.1177/"):
        out.extend(sage_public_version_candidates(doi))
    if dlow.startswith("10.1007/"):
        add_unique(out, f"https://link.springer.com/content/pdf/{doi}.pdf", "Springer public PDF endpoint")
    if dlow.startswith("10.3390/"):
        add_unique(out, f"https://www.mdpi.com/doi/pdf/{doi}", "MDPI public PDF endpoint")
    if dlow.startswith("10.1098/"):
        add_unique(out, f"https://royalsocietypublishing.org/doi/pdf/{doi}", "Royal Society public PDF endpoint")
    if dlow.startswith("10.1145/"):
        add_unique(out, f"https://dl.acm.org/doi/pdf/{doi}", "ACM PDF endpoint")
    if dlow.startswith("10.1002/"):
        add_unique(out, f"https://onlinelibrary.wiley.com/doi/pdfdirect/{doi}", "Wiley public PDF endpoint")
    if dlow.startswith("10.1038/"):
        slug = doi.split("/", 1)[1]
        add_unique(out, f"https://www.nature.com/articles/{slug}.pdf", "Nature PDF endpoint")
    return out


def main():
    SUPP_PAPERS.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8-sig")))
    recovered = []

    for row in rows:
        if row.get("status") == "downloaded":
            continue
        idx = int(row["index"])
        title = row["title"]
        dest = PDF_DIR / safe_name(idx, title)
        candidates = []
        for url in EXPLICIT.get(idx, []):
            add_unique(candidates, url, "exact-title public web source")
        for url, source in generic_candidates(row["original_url"]):
            add_unique(candidates, url, source)

        last = "no targeted public candidate"
        tried = 0
        for url, source in candidates:
            tried += 1
            ok, info, final_url = fetch_pdf(url, dest, accept_pdf=True)
            if ok:
                row["status"] = "downloaded"
                row["source"] = source
                row["resolved_pdf_url"] = final_url
                row["filename"] = dest.name
                row["bytes_or_error"] = info
                row["candidates_tried"] = str(int(row.get("candidates_tried") or 0) + tried)
                shutil.copy2(dest, SUPP_PAPERS / dest.name)
                recovered.append((idx, title, final_url, dest.name))
                print(f"[PUBLIC RECOVERED] {idx:03d} {title[:100]}", flush=True)
                break
            last = info
            time.sleep(0.2)
        else:
            row["bytes_or_error"] = last[:500]
            row["candidates_tried"] = str(int(row.get("candidates_tried") or 0) + tried)
            print(f"[STILL UNAVAILABLE] {idx:03d} {title[:100]}", flush=True)
        time.sleep(0.15)

    with MANIFEST.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    shutil.copy2(MANIFEST, SUPP / "download_manifest_final.csv")
    ok_count = sum(r.get("status") == "downloaded" for r in rows)
    failed = len(rows) - ok_count
    with (SUPP / "RECOVERED.txt").open("w", encoding="utf-8") as f:
        f.write(f"New PDFs recovered by exact-title public-web pass: {len(recovered)}\n")
        f.write(f"Total PDFs now available: {ok_count} / {len(rows)} unique links\n")
        f.write(f"Still without a directly accessible public PDF: {failed}\n\n")
        for idx, title, url, filename in recovered:
            f.write(f"{idx:03d}\t{title}\n    {filename}\n    {url}\n")
    print(f"SUPPLEMENT DONE new={len(recovered)} total_downloaded={ok_count} failed={failed}", flush=True)


if __name__ == "__main__":
    main()
