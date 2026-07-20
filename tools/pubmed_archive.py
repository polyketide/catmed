#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch PubMed records into a raw, verifiable archive kept OUTSIDE the repository.

The archive is a cache, never a source of truth: everything needed to rebuild it
(the PMID list) lives in the knowledge base, under version control. See
docs/LITERATURE-PIPELINE-SOP.md sections 3 and 3b.

Each record stores the payload exactly as PubMed returned it, plus a SHA-256 of
those bytes and the provenance of the fetch. Nothing here interprets, summarises
or reformats a source; that is deliberate, and the excerpt-verification step in
dr_drill.py depends on it.

Usage:
  pubmed_archive.py fetch [--pmids FILE] [--archive DIR] [--force]
  pubmed_archive.py measure [--archive DIR]     # token cost, raw vs trimmed
  pubmed_archive.py verify [--archive DIR]      # re-hash every record

Archive location resolution order: --archive, $CATMED_ARCHIVE, ~/.catmed-archive
Standard library only, matching the rest of tools/.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

TOOL_VERSION = "1"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
BATCH = 20            # PubMed is fine with more, but keep batches reviewable
SLEEP = 0.4           # stay under the 3 req/s courtesy limit without an API key
UA = "catmed-literature-pipeline/%s (+https://github.com/polyketide/catmed)" % TOOL_VERSION

REPO = Path(__file__).resolve().parent.parent
KB = REPO / "knowledge-base"


# ---------------------------------------------------------------- archive path

def archive_dir(explicit: str | None) -> Path:
    """Resolve the archive location. Never inside the repo — it is a public repo
    and these are third-party API payloads."""
    p = Path(explicit or os.environ.get("CATMED_ARCHIVE") or "~/.catmed-archive")
    p = p.expanduser().resolve()
    if REPO == p or REPO in p.parents:
        sys.exit("refusing to write the archive inside the repository: %s" % p)
    return p


# ------------------------------------------------------------ knowledge base IO

def pmids_from_kb() -> dict[str, list[str]]:
    """Every PMID cited in a source-excerpt section, mapped to the files citing it.

    This is the rebuild input. If a PMID reaches the archive without appearing
    here, the cache-not-truth split has been broken.
    """
    out: dict[str, list[str]] = {}
    for f in sorted(KB.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        if "## 原文摘录" not in text:
            continue
        excerpts = text.split("## 原文摘录", 1)[1]
        for pmid in re.findall(r"\*\*PMID\s+(\d+)\*\*", excerpts):
            out.setdefault(pmid, []).append(f.name)
    return out


# ------------------------------------------------------------------- fetching

def fetch_batch(pmids: list[str]) -> str:
    """Return the raw XML for a batch, exactly as PubMed sent it."""
    qs = urllib.parse.urlencode(
        {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}
    )
    req = urllib.request.Request(EFETCH + "?" + qs, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def split_records(xml_text: str) -> dict[str, str]:
    """Split a multi-record response into per-PMID XML fragments, preserving the
    original bytes of each fragment rather than re-serialising the tree."""
    out: dict[str, str] = {}
    root = ET.fromstring(xml_text)
    for art in root.iter("PubmedArticle"):
        pid = art.findtext(".//PMID")
        if pid:
            # tostring on the parsed element is a re-serialisation; acceptable
            # only because we hash and verify THIS representation consistently.
            out[pid] = ET.tostring(art, encoding="unicode")
    return out


def cmd_fetch(args) -> int:
    arc = archive_dir(args.archive)
    (arc / "records").mkdir(parents=True, exist_ok=True)

    if args.pmids:
        wanted = [l.strip() for l in Path(args.pmids).read_text().splitlines() if l.strip()]
        origin = {p: ["(file)"] for p in wanted}
    else:
        origin = pmids_from_kb()
        wanted = sorted(origin)

    todo = [p for p in wanted
            if args.force or not (arc / "records" / f"{p}.json").exists()]
    print(f"{len(wanted)} PMIDs requested, {len(todo)} to fetch "
          f"({len(wanted)-len(todo)} already archived)")

    ok = failed = 0
    for i in range(0, len(todo), BATCH):
        batch = todo[i:i + BATCH]
        try:
            xml_text = fetch_batch(batch)
            records = split_records(xml_text)
        except Exception as exc:                      # never fabricate a substitute
            print(f"  FETCH-ERROR batch {i//BATCH+1}: {exc}", file=sys.stderr)
            failed += len(batch)
            continue

        for pmid in batch:
            frag = records.get(pmid)
            if frag is None:
                # A requested PMID that PubMed did not return is a real finding,
                # not a blank to be filled in.
                print(f"  NOT-RETURNED {pmid}", file=sys.stderr)
                failed += 1
                continue
            raw = frag.encode("utf-8")
            rec = {
                "pmid": pmid,
                "raw_xml": frag,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "source": "pubmed efetch",
                "tool_version": TOOL_VERSION,
                "cited_by": origin.get(pmid, []),
            }
            (arc / "records" / f"{pmid}.json").write_text(
                json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8"
            )
            ok += 1
        time.sleep(SLEEP)

    print(f"archived {ok}, failed {failed} → {arc/'records'}")
    return 1 if failed else 0


# ------------------------------------------------------------------- measuring

def approx_tokens(s: str) -> int:
    """Rough token count. Deliberately crude — this measures a RATIO between two
    representations of the same text, where a constant factor cancels out."""
    return max(1, len(s) // 4)


def trimmed_view(frag: str) -> dict:
    """The fields the agent actually needs, which is what a local pipeline would
    hand over. Everything else in a PubMed record is overhead for this purpose."""
    art = ET.fromstring(frag)
    abstract = " ".join(
        (t.text or "") for t in art.iter("AbstractText")
    ).strip()
    authors = []
    for a in art.iter("Author"):
        ln, fn = a.findtext("LastName"), a.findtext("Initials")
        if ln:
            authors.append(f"{ln} {fn}" if fn else ln)
    return {
        "pmid": art.findtext(".//PMID"),
        "title": (art.findtext(".//ArticleTitle") or "").strip(),
        "journal": art.findtext(".//ISOAbbreviation"),
        "year": art.findtext(".//PubDate/Year"),
        "volume": art.findtext(".//Volume"),
        "issue": art.findtext(".//Issue"),
        "pages": art.findtext(".//MedlinePgn"),
        "doi": next((i.text for i in art.iter("ArticleId")
                     if i.get("IdType") == "doi"), None),
        "language": art.findtext(".//Language"),
        "authors": authors[:3] + (["et al."] if len(authors) > 3 else []),
        "abstract": abstract,
    }


# The legal notice the MCP tool prepends to every response is counted, on the
# principle that a measurement of overhead should include the overhead.
LEGAL_NOTICE_CHARS = 1750   # measured from the bio-research PubMed MCP response
MCP_BATCH = 8               # typical batch size used in practice this session


def mcp_like_view(frag: str) -> dict:
    """Reconstruct what the PubMed MCP tool actually hands the agent, so the
    comparison is against the real baseline rather than against raw XML.

    Field set observed from live responses this session: identifiers, title,
    abstract, journal object, authors WITH affiliations, publication_date,
    keywords, mesh_terms, article_types, language, citation.
    """
    art = ET.fromstring(frag)
    view = trimmed_view(frag)
    authors = []
    for a in art.iter("Author"):
        ln = a.findtext("LastName")
        if not ln:
            continue
        authors.append({
            "last_name": ln,
            "fore_name": a.findtext("ForeName"),
            "initials": a.findtext("Initials"),
            "affiliations": [af.text for af in a.iter("Affiliation") if af.text],
        })
    return {
        "identifiers": {"pmid": view["pmid"], "doi": view["doi"]},
        "title": view["title"],
        "abstract": view["abstract"],
        "journal": {"title": art.findtext(".//Journal/Title"),
                    "iso_abbreviation": view["journal"]},
        "authors": authors,
        "publication_date": {"year": view["year"]},
        "keywords": [k.text for k in art.iter("Keyword") if k.text],
        "mesh_terms": [m.text for m in art.iter("DescriptorName") if m.text],
        "article_types": [p.text for p in art.iter("PublicationType") if p.text],
        "language": view["language"],
        "citation": {"volume": view["volume"], "issue": view["issue"],
                     "pages": view["pages"]},
    }


def cmd_measure(args) -> int:
    arc = archive_dir(args.archive)
    files = sorted((arc / "records").glob("*.json"))
    if not files:
        sys.exit("archive empty — run `fetch` first: %s" % arc)

    raw_t = mcp_t = trim_t = 0
    fails = 0
    for f in files:
        rec = json.loads(f.read_text(encoding="utf-8"))
        raw_t += approx_tokens(rec["raw_xml"])
        try:
            mcp_t += approx_tokens(
                json.dumps(mcp_like_view(rec["raw_xml"]), ensure_ascii=False))
            trim_t += approx_tokens(
                json.dumps(trimmed_view(rec["raw_xml"]), ensure_ascii=False))
        except Exception as exc:
            print(f"  VIEW-ERROR {rec['pmid']}: {exc}", file=sys.stderr)
            fails += 1

    n = len(files)
    notice_t = approx_tokens("x" * LEGAL_NOTICE_CHARS) * ((n + MCP_BATCH - 1) // MCP_BATCH)
    mcp_total = mcp_t + notice_t

    print(f"records                      : {n}")
    print(f"raw XML (what PubMed sends)  : ~{raw_t:,} tokens  ({raw_t//n:,}/rec)")
    print(f"MCP-equivalent payload       : ~{mcp_t:,} tokens  ({mcp_t//n:,}/rec)")
    print(f"  + repeated legal notice    : ~{notice_t:,} tokens  "
          f"({(n+MCP_BATCH-1)//MCP_BATCH} calls x ~{approx_tokens('x'*LEGAL_NOTICE_CHARS)})")
    print(f"  = current baseline         : ~{mcp_total:,} tokens")
    print(f"trimmed view (pipeline out)  : ~{trim_t:,} tokens  ({trim_t//n:,}/rec)")
    if trim_t:
        print()
        print(f"SAVING vs current baseline   : {mcp_total/trim_t:.1f}x  "
              f"({100*(1-trim_t/mcp_total):.0f}% of tokens removed)")
        print(f"  (vs raw XML, for reference : {raw_t/trim_t:.1f}x)")
    if fails:
        print(f"view failures                : {fails}  (excluded from totals)")
    print("\n⚠️  ~4 chars/token approximation; ratios are meaningful, absolute")
    print("    totals are not. The MCP-equivalent view is RECONSTRUCTED from the")
    print("    same XML to match the field set observed in live responses — it is")
    print("    a faithful model of the baseline, not a recording of one.")
    print("    Excluded from the baseline (so the saving is understated): search")
    print("    results, whose query_translation echo is pure overhead, and any")
    print("    record fetched but never cited.")
    return 0


# -------------------------------------------------------------------- verifying

def cmd_verify(args) -> int:
    arc = archive_dir(args.archive)
    files = sorted((arc / "records").glob("*.json"))
    if not files:
        sys.exit("archive empty: %s" % arc)
    bad = 0
    for f in files:
        rec = json.loads(f.read_text(encoding="utf-8"))
        actual = hashlib.sha256(rec["raw_xml"].encode("utf-8")).hexdigest()
        if actual != rec["sha256"]:
            print(f"  HASH-MISMATCH {rec['pmid']}: stored {rec['sha256'][:12]} "
                  f"actual {actual[:12]}", file=sys.stderr)
            bad += 1
    print(f"verified {len(files)} records, {bad} corrupted")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("fetch", cmd_fetch), ("measure", cmd_measure), ("verify", cmd_verify)):
        p = sub.add_parser(name)
        p.add_argument("--archive")
        if name == "fetch":
            p.add_argument("--pmids", help="file of PMIDs; default = scan knowledge-base/")
            p.add_argument("--force", action="store_true", help="re-fetch existing records")
        p.set_defaults(fn=fn)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
