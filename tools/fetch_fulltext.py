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

Resolution order (2026-07-30):
  1. Europe PMC JATS XML   open access only; EPMC enforces the licence itself,
                           returning 404 for anything else. Structured, and not
                           subject to the interstitials above. Tried first.
  2. Unpaywall PDF links   licence status from Unpaywall, never assumed.
  3. reported for manual retrieval, with the reason separated: not open access,
     versus open access but blocked by a bot check, versus genuinely absent.

Deliberately absent: Sci-Hub, LibGen, and any CAPTCHA or bot-detection
circumvention. They would fetch more papers. They also make this tool something
that cannot be run at an institution, and the corpus is meant to be checkable by
the people it is written for.

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
import urllib.error
import urllib.parse
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


EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"


def epmc_info(pmid: str) -> dict:
    """Europe PMC's view of one article. Returns {} when it knows nothing.

    Two facts are reported separately and must not be conflated:

      inEPMC        a full text exists in Europe PMC
      isOpenAccess  we are licensed to take it

    They diverge often. A PubMed/PMC full-text call can hand back an empty body
    for an article whose full text is plainly on the web, because those calls
    serve the open-access subset; the empty field is a licence statement wearing
    the costume of an absence. Keeping the two apart is what lets this tool say
    "exists, not ours to take — use institutional access" instead of the much
    less useful "not found".
    """
    url = (f"{EPMC}/search?query=EXT_ID:{urllib.parse.quote(pmid)}"
           f"&format=json&resultType=core")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=25) as r:
        results = json.load(r).get("resultList", {}).get("result", [])
    if not results:
        return {}
    a = results[0]
    return {
        "pmcid": a.get("pmcid") or "",
        "in_epmc": a.get("inEPMC") == "Y",
        "is_oa": a.get("isOpenAccess") == "Y",
    }


def epmc_fulltext(pmcid: str, dest: Path) -> tuple[bool, str]:
    """Fetch the structured JATS full text. Europe PMC enforces the licence
    itself — open access returns the document, anything else returns 404 — so
    this path cannot be used to reach past a paywall.

    That makes a bare 404 ambiguous between "not open access" and "no such
    article", which is why callers must consult epmc_info() first rather than
    inferring absence from the status code.

    XML rather than PDF on purpose: it is the machine-readable form, and it
    arrives without the bot checks and JS interstitials that block publisher
    PDF links even for gold OA.
    """
    url = f"{EPMC}/{pmcid}/fullTextXML"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
    except urllib.error.HTTPError as exc:
        return False, f"Europe PMC returned HTTP {exc.code}"
    except Exception as exc:
        return False, f"Europe PMC error ({type(exc).__name__})"
    if b"<article" not in body[:4000]:
        return False, "Europe PMC response was not JATS XML"
    dest.write_bytes(body)
    return True, str(dest)


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
        xml_dest = out / f"{pmid}.xml"
        if dest.exists() or xml_dest.exists():
            held = dest if dest.exists() else xml_dest
            got.append((pmid, "already held", str(held)))
            continue

        # Europe PMC first: it serves structured JATS and is not behind the bot
        # checks that block publisher PDF links even for gold OA. A failure here
        # is not fatal — the Unpaywall path below still runs.
        try:
            epmc = epmc_info(pmid)
        except Exception:
            epmc = {}
        if epmc.get("is_oa") and epmc.get("pmcid"):
            ok, detail = epmc_fulltext(epmc["pmcid"], xml_dest)
            if ok:
                got.append((pmid, "open access — Europe PMC JATS XML", detail))
                time.sleep(0.5)
                continue

        try:
            status, urls = oa_info(doi)
        except Exception as exc:
            manual.append((pmid, f"Unpaywall error ({type(exc).__name__})", ""))
            continue
        if not urls and epmc.get("in_epmc") and not epmc.get("is_oa"):
            # The distinction worth reporting: a full text demonstrably exists,
            # and we are simply not licensed to take it. Saying "not found" here
            # would send the operator looking for something that is right there.
            manual.append((pmid,
                           f"{status} — full text exists in Europe PMC "
                           f"({epmc['pmcid']}) but is not open access; "
                           f"use institutional access",
                           f"https://europepmc.org/article/MED/{pmid}"))
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
