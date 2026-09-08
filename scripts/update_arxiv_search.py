#!/usr/bin/env python3
"""Generate high-recall arXiv candidates for LLM-based human simulation.

This script does NOT automatically decide inclusion. It searches multiple query
families, normalizes canonical arXiv IDs, deduplicates candidates, and writes a
CSV for manual screening against the curated yearly files in ../data/.

Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import csv
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from pathlib import Path

API_URL = "https://export.arxiv.org/api/query"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_ID_RE = re.compile(r"(?:abs/|pdf/)?(\d{4}\.\d{4,5})(?:v\d+)?")

QUERY_FAMILIES = {
    "silicon_sampling": 'all:"silicon sampling"',
    "silicon_sample": 'all:"silicon sample"',
    "synthetic_respondent": 'all:"synthetic respondent"',
    "synthetic_survey_respondent": 'all:"synthetic survey respondent"',
    "virtual_survey_respondent": 'all:"virtual survey respondent"',
    "synthetic_participant": 'all:"synthetic participant" AND (all:"large language model" OR all:LLM)',
    "survey_response": 'all:"survey response" AND (all:"large language model" OR all:LLM)',
    "public_opinion": 'all:"public opinion" AND (all:"large language model" OR all:LLM)',
    "human_surrogate": 'all:"human surrogate" AND (all:"large language model" OR all:LLM)',
    "human_proxy": 'all:"human proxy" AND (all:"large language model" OR all:LLM)',
    "digital_twin": 'all:"digital twin" AND (all:"large language model" OR all:LLM)',
    "digital_representative": 'all:"digital representative" AND (all:"large language model" OR all:LLM)',
    "persona_simulation": 'all:"persona simulation" AND (all:"large language model" OR all:LLM)',
    "human_behavior_simulation": 'all:"human behavior simulation" AND (all:"large language model" OR all:LLM)',
    "simulate_human_behavior": 'all:"simulate human behavior" AND (all:"large language model" OR all:LLM)',
    "human_cognition": 'all:"human cognition" AND (all:"large language model" OR all:LLM)',
    "cognitive_model": 'all:"cognitive model" AND all:"large language model"',
    "human_preferences": 'all:"human preferences" AND all:"large language model"',
    "social_simulation": 'all:"social simulation" AND (all:"large language model" OR all:LLM)',
    "generative_agents": 'all:"generative agents" AND (all:human OR all:social)',
    "opinion_dynamics": 'all:"opinion dynamics" AND (all:"large language model" OR all:LLM)',
    "social_network_simulation": 'all:"social network simulation" AND (all:"large language model" OR all:LLM)',
    "population_simulation": 'all:"population simulation" AND (all:"large language model" OR all:LLM)',
    "agent_based_social": 'all:"agent-based" AND all:simulation AND all:"large language model"',
    "user_simulator": 'all:"user simulator" AND (all:"large language model" OR all:LLM)',
    "user_simulation": 'all:"user simulation" AND (all:"large language model" OR all:LLM)',
    "consumer_simulation": 'all:"consumer simulation" AND (all:"large language model" OR all:LLM)',
    "customer_simulation": 'all:"customer simulation" AND (all:"large language model" OR all:LLM)',
    "student_simulation": 'all:"student simulation" AND (all:"large language model" OR all:LLM)',
    "economic_agents": 'all:"economic agents" AND all:"large language model"',
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2023-01-01", help="inclusive YYYY-MM-DD")
    parser.add_argument("--end", default=datetime.now().date().isoformat(), help="inclusive YYYY-MM-DD")
    parser.add_argument("--output", default="data/generated_candidates.csv")
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--max-per-query", type=int, default=2000)
    parser.add_argument("--sleep", type=float, default=3.0, help="seconds between API requests")
    return parser.parse_args()


def iso_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d")


def arxiv_date_filter(start: str, end: str) -> str:
    start_token = start.replace("-", "") + "0000"
    end_token = end.replace("-", "") + "2359"
    return f"submittedDate:[{start_token} TO {end_token}]"


def canonical_arxiv_id(url_or_id: str) -> str:
    match = ARXIV_ID_RE.search(url_or_id)
    return match.group(1) if match else url_or_id.strip()


def clean_text(text: str | None) -> str:
    return " ".join((text or "").split())


def fetch_feed(search_query: str, start: int, max_results: int) -> ET.Element:
    params = {
        "search_query": search_query,
        "start": str(start),
        "max_results": str(max_results),
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = API_URL + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "SiliconSampleLiterature/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return ET.fromstring(response.read())


def parse_entry(entry: ET.Element) -> dict[str, str]:
    raw_id = clean_text(entry.findtext("atom:id", namespaces=ATOM_NS))
    arxiv_id = canonical_arxiv_id(raw_id)
    authors = [
        clean_text(author.findtext("atom:name", namespaces=ATOM_NS))
        for author in entry.findall("atom:author", ATOM_NS)
    ]
    categories = [node.attrib.get("term", "") for node in entry.findall("atom:category", ATOM_NS)]
    published = clean_text(entry.findtext("atom:published", namespaces=ATOM_NS))
    updated = clean_text(entry.findtext("atom:updated", namespaces=ATOM_NS))
    return {
        "arxiv_id": arxiv_id,
        "title": clean_text(entry.findtext("atom:title", namespaces=ATOM_NS)),
        "authors": "; ".join(authors),
        "published": published,
        "updated": updated,
        "summary": clean_text(entry.findtext("atom:summary", namespaces=ATOM_NS)),
        "categories": "; ".join(categories),
        "arxiv_url": f"https://arxiv.org/abs/{arxiv_id}",
    }


def query_all(label: str, query: str, date_filter: str, args: argparse.Namespace) -> list[dict[str, str]]:
    combined = f"({query}) AND {date_filter}"
    rows: list[dict[str, str]] = []
    offset = 0

    while offset < args.max_per_query:
        size = min(args.batch_size, args.max_per_query - offset)
        feed = fetch_feed(combined, offset, size)
        entries = feed.findall("atom:entry", ATOM_NS)
        if not entries:
            break
        for entry in entries:
            row = parse_entry(entry)
            row["matched_query"] = label
            rows.append(row)
        offset += len(entries)
        if len(entries) < size:
            break
        time.sleep(args.sleep)

    return rows


def main() -> None:
    args = parse_args()
    start_dt = iso_date(args.start)
    end_dt = iso_date(args.end)
    if end_dt < start_dt:
        raise ValueError("--end must be on or after --start")

    date_filter = arxiv_date_filter(args.start, args.end)
    by_id: dict[str, dict[str, str]] = {}
    matched_queries: defaultdict[str, set[str]] = defaultdict(set)

    for index, (label, query) in enumerate(QUERY_FAMILIES.items(), start=1):
        print(f"[{index}/{len(QUERY_FAMILIES)}] {label}: {query}")
        rows = query_all(label, query, date_filter, args)
        print(f"  returned: {len(rows)}")
        for row in rows:
            arxiv_id = row["arxiv_id"]
            matched_queries[arxiv_id].add(label)
            by_id.setdefault(arxiv_id, row)
        time.sleep(args.sleep)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "arxiv_id",
        "title",
        "authors",
        "published",
        "updated",
        "categories",
        "matched_queries",
        "arxiv_url",
        "summary",
    ]

    def sort_key(row: dict[str, str]) -> tuple[str, str]:
        return (row.get("published", ""), row.get("arxiv_id", ""))

    rows_out = []
    for arxiv_id, row in by_id.items():
        item = dict(row)
        item["matched_queries"] = "; ".join(sorted(matched_queries[arxiv_id]))
        rows_out.append(item)

    rows_out.sort(key=sort_key)

    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Unique candidates: {len(rows_out)}")
    print(f"Written to: {output}")
    print("Manual screening is still required; this is a high-recall candidate generator, not an automatic inclusion classifier.")


if __name__ == "__main__":
    main()
