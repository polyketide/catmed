#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch open-access full texts where that is possible, and say plainly where it is not.

Abstracts answer most questions; some need the full text (see the ⚠️ markers in
knowledge-base/*.md). Obtaining those was manual. This automates the part that
can be automated legitimately and — as importantly — reports the part that
cannot, so the remaining work is a short list rather than a guess.

**Only open-access articles are downloaded.** Licence status comes from Unpaywall,
not from assumption, and is recorded alongside the file. Paywalled articles are
never scraped or circumvented; they are listed for the operator to obtain through
their own institutional access.

Reality of what works, measured 2026-07-20 — publisher hostility to automated
requests has nothing to do with licence:
  J-Stage, Frontiers          → download fine
  MDPI, PMC, Wiley, SAGE      → 403 or JS interstitial, even for gold OA

So a `gold` status is necessary but not sufficient. The tool tries, and does not
pretend a failure was a licence problem when it was a bot check.

Usage:
  fetch_fulltext.py <PMID> [PMID ...] [--out DIR]
  fetch_fulltext.py --needed [--out DIR]     # every PMID the knowledge base flags
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pubmed_archive import KB, archive_dir, trimmed_view  # noqa: E402

EMAIL = "wamphetamine@gmail.com"          # Unpaywall requires a contact address
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
YEAR = re.compile(r"^(19|20)\d\d$")


# The wording the open-flag template emits. A note that *resolves* a flag quotes
# the same figures in the same backticks, so matching on the figures alone makes
# the work list re-report every gap that has already been closed — measured
# 2026-07-27, when all 3 remaining "unblocked" PMIDs turned out to be this.
OPEN_FLAG = "retrieve the full text and verify before citing"


def needed_pmids() -> dict[str, str]:
    """PMIDs the knowledge base has flagged as citing figures absent from the
    abstract. These are exactly the cases where a full text would settle
    something, so they are the sensible default work list.

    **A resolution note is not a flag.** Only lines carrying the open-flag
    wording count; `FALSE POSITIVE resolved`/`ATTRIBUTION CORRECTED`/`FLAG
    CLOSED` notes quote the same figures and must not re-enter the work list."""
    out: dict[str, str] = {}
    for f in sorted(KB.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        if "## 原文摘录" not in text:
            continue
        current = None
        for line in text.split("## 原文摘录", 1)[1].splitlines():
            m = re.match(r"\*\*PMID\s+(\d+)\*\*", line.strip())
            if m:
                current = m.group(1)
                continue
            if OPEN_FLAG not in line:
                continue
            g = re.search(r"The figures? `([^`]+)`", line)
            if g and current:
                real = [x.strip() for x in g.group(1).split(",")
                        if not YEAR.match(x.strip()) and len(x.strip()) < 8]
                if real:
                    out[current] = ",".join(real)
    return out


def oa_info(doi: str) -> tuple[str, list[str]]:
    """(status, candidate PDF urls) from Unpaywall. Never guesses a licence."""
    url = f"https://api.unpaywall.org/v2/{doi}?email={EMAIL}"
    with urllib.request.urlopen(url, timeout=25) as r:
        d = json.load(r)
    if not d.get("is_oa"):
        return d.get("oa_status", "closed"), []
    urls, seen = [], set()
    for loc in ([d.get("best_oa_location")] + (d.get("oa_locations") or [])):
        if not loc:
            continue
        u = loc.get("url_for_pdf") or loc.get("url")
        if u and u not in seen:
            seen.add(u)
            urls.append(u)
    return d.get("oa_status", "?"), urls


def try_download(urls: list[str], dest: Path) -> tuple[bool, str]:
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={
                "User-Agent": UA, "Accept": "application/pdf,*/*"})
            with urllib.request.urlopen(req, timeout=90) as r:
                data = r.read()
        except Exception as exc:
            continue
        if data[:4] == b"%PDF":
            dest.write_bytes(data)
            return True, u
    return False, "no candidate returned a PDF (bot check or interstitial)"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pmids", nargs="*")
    ap.add_argument("--needed", action="store_true",
                    help="use every PMID the knowledge base flags as needing full text")
    ap.add_argument("--out", default="~/.catmed-archive/fulltext")
    args = ap.parse_args()

    flagged = needed_pmids()
    targets = args.pmids or (sorted(flagged) if args.needed else [])
    if not targets:
        sys.exit("give PMIDs, or --needed")

    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    arc = archive_dir(None) / "records"

    got, manual = [], []
    for pmid in targets:
        f = arc / f"{pmid}.json"
        if not f.exists():
            manual.append((pmid, "not archived — fetch metadata first", ""))
            continue
        doi = trimmed_view(json.loads(f.read_text(encoding="utf-8"))["raw_xml"])["doi"]
        if not doi:
            manual.append((pmid, "no DOI in record", ""))
            continue
        dest = out / f"{pmid}.pdf"
        if dest.exists():
            got.append((pmid, "already held", str(dest)))
            continue
        try:
            status, urls = oa_info(doi)
        except Exception as exc:
            manual.append((pmid, f"Unpaywall error ({type(exc).__name__})", ""))
            continue
        if not urls:
            manual.append((pmid, f"{status} — needs institutional access",
                           f"https://doi.org/{doi}"))
            continue
        ok, detail = try_download(urls, dest)
        (got if ok else manual).append(
            (pmid, f"{status} — {'downloaded' if ok else detail}",
             detail if ok else urls[0]))
        time.sleep(0.5)

    print(f"\n=== downloaded: {len(got)} ===")
    for p, why, where in got:
        note = f" [{flagged[p]}]" if p in flagged else ""
        print(f"  {p}{note}  {why}")
    print(f"\n=== needs manual retrieval: {len(manual)} ===")
    for p, why, where in manual:
        note = f" [{flagged[p]}]" if p in flagged else ""
        print(f"  {p}{note}  {why}")
        if where:
            print(f"      {where}")
    if manual:
        print("\nThese require the operator's own institutional access. Do not attempt")
        print("to circumvent access controls; hand the list over instead.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
