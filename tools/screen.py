#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Measure what a deterministic local screen would save — and what it would cost.

docs/LITERATURE-PIPELINE-SOP.md section 1 measures only records that survived
selection and were cited. The larger, unmeasured cost is the candidates fetched
and discarded: the screen's whole purpose is keeping those away from the agent.

This replays real searches, applies a screen that uses no language model at all,
and reports two numbers. Only one of them is about tokens.

  compression — how much candidate payload the screen removes
  RECALL      — how many papers the knowledge base actually cites would have
                survived the screen

Recall is the one that decides whether this is viable. A screen that saves 90% of
tokens while discarding a load-bearing paper is worse than no screen, because the
loss is silent: the agent never learns what it was not shown.

Usage:
  screen.py measure [--queries FILE] [--retmax N]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pubmed_archive import (UA, approx_tokens, mcp_like_view, pmids_from_kb,  # noqa: E402
                            split_records, trimmed_view)

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
SLEEP = 0.4

# The searches actually run while building the emergency-triage and supportive-care
# files. Kept verbatim so the replay measures real retrieval rather than a
# retrospectively tidied version of it.
DEFAULT_QUERIES = [
    "urethral obstruction[Title] AND cats[Title]",
    "arterial thromboembolism[Title] AND cats[Title]",
    "permethrin[Title] AND cats[Title]",
    "(lily[Title] OR Lilium[Title]) AND cats",
    "hepatic lipidosis[Title] AND cats",
    "respiratory distress[Title] AND cats[Title]",
    "symptom checker[Title] AND (triage OR advice OR urgency)",
    "thickened liquids[Title] AND (aspiration OR pneumonia OR dysphagia)",
    "megaesophagus[All Fields] AND dogs AND (feeding OR upright OR posture)",
    "dysphagia[Title] AND (cats[Title] OR feline[Title])",
]

SPECIES = re.compile(r"\b(cat|cats|feline|felis|kitten)\b", re.I)
CROSS_SPECIES = re.compile(r"\b(dog|dogs|canine|human|patient|patients|people)\b", re.I)
QUANT = re.compile(r"\d+\s*%|\bP\s*[=<]|\b\d+/\d+\b|\bCI\b|hazard ratio|"
                   r"median\b|sensitivity|specificity|survival|incidence", re.I)


def esearch(term: str, retmax: int) -> list[str]:
    qs = urllib.parse.urlencode({"db": "pubmed", "term": term,
                                 "retmax": retmax, "retmode": "json"})
    req = urllib.request.Request(ESEARCH + "?" + qs, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())["esearchresult"].get("idlist", [])


def efetch(pmids: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for i in range(0, len(pmids), 20):
        qs = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(pmids[i:i + 20]),
                                     "retmode": "xml"})
        req = urllib.request.Request(EFETCH + "?" + qs, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            out.update(split_records(r.read().decode("utf-8")))
        time.sleep(SLEEP)
    return out


def screen_none(frag: str) -> tuple[bool, str]:
    """The lossless option: drop no papers, only trim fields.

    Kept as a first-class mode because the measurement below showed content
    screening losing load-bearing sources, and a saving that cannot lose a paper
    is worth more than a larger one that can.
    """
    return True, "no content screening"


def screen(frag: str) -> tuple[bool, str]:
    """Content screening — MEASURED AND REJECTED. Not the default; kept so the
    negative result stays reproducible.

    Measured 2026-07-20 over a 136-candidate replay of real searches: 2.9x
    compression at **66.7% recall**. It discarded four sources the knowledge base
    depends on, including the review that carries the entire lily section ("As
    little as 2 leaves or part of a single flower have resulted in deaths").

    The defect is in the premise, not the thresholds. These rules encode "useful
    means quantitative", and this knowledge base's most load-bearing citations are
    often qualitative boundary statements — a dose that kills, a window in which
    prognosis is excellent — carrying no percentage, no p-value, nothing a regex
    can see. The species rule fails the same way on the human-medicine literature
    the project cites deliberately.

    Tuning the patterns would not fix this; it would move which load-bearing
    papers get dropped.
    """
    view = trimmed_view(frag)
    text = f"{view['title']} {view['abstract']}"

    if not view["abstract"].strip():
        # No abstract: nothing to screen ON. Keep — a letter or comment may still
        # be the thing that matters, and this is exactly where a confident filter
        # would start doing damage.
        return True, "no abstract to screen on"
    if not (SPECIES.search(text) or CROSS_SPECIES.search(text)):
        return False, "no species term"
    if not QUANT.search(text):
        return False, "no quantitative signal"
    return True, "kept"


def cmd_survey(args) -> int:
    """Stage 1 of real use: title-level triage.

    Prints one line per candidate — no abstracts. This is where the token saving
    actually lands in practice: a survey of 40 candidates costs less than pulling
    three full records, and the agent still chooses which to open. Nothing is
    dropped; the full list is always printed (see SOP section 2 on ranking versus
    truncation).
    """
    cited = set(pmids_from_kb())
    pool, seen = [], set()
    for q in args.query:
        try:
            ids = esearch(q, args.retmax)
        except Exception as exc:
            print(f"  SEARCH-ERROR {q!r}: {exc}", file=sys.stderr)
            continue
        new = [p for p in ids if p not in seen]
        seen.update(new)
        pool.extend(new)
        time.sleep(SLEEP)
    if not pool:
        sys.exit("no candidates")
    records = efetch(pool)
    for pmid in pool:
        frag = records.get(pmid)
        if frag is None:
            print(f"  {pmid}  (not returned by efetch)")
            continue
        v = trimmed_view(frag)
        mark = "*" if pmid in cited else " "     # already in the knowledge base
        has_abs = "A" if v["abstract"].strip() else "-"
        print(f"{mark}{has_abs} {pmid}  {(v['year'] or '????'):>4}  "
              f"{(v['journal'] or '?')[:28]:28s}  {v['title'][:88]}")
    print("")
    print(f"{len(pool)} candidates  (* = already cited here, A = has abstract)")
    return 0


def cmd_show(args) -> int:
    """Stage 2: full trimmed view for the handful worth opening."""
    records = efetch(args.pmids)
    for pmid in args.pmids:
        frag = records.get(pmid)
        if frag is None:
            print(f"--- {pmid}: NOT RETURNED ---")
            continue
        print(json.dumps(trimmed_view(frag), ensure_ascii=False, indent=1))
        print()
    return 0


def cmd_measure(args) -> int:
    queries = ([l.strip() for l in Path(args.queries).read_text().splitlines() if l.strip()]
               if args.queries else DEFAULT_QUERIES)
    cited = set(pmids_from_kb())

    pool: list[str] = []
    seen: set[str] = set()
    for q in queries:
        try:
            ids = esearch(q, args.retmax)
        except Exception as exc:
            print(f"  SEARCH-ERROR {q!r}: {exc}", file=sys.stderr)
            continue
        new = [p for p in ids if p not in seen]
        seen.update(new)
        pool.extend(new)
        print(f"  {len(ids):3d} hits ({len(new):3d} new)  {q}")
        time.sleep(SLEEP)

    if not pool:
        sys.exit("no candidates retrieved")

    print(f"\nfetching {len(pool)} candidate records...")
    records = efetch(pool)

    kept, dropped = [], []
    for pmid in pool:
        frag = records.get(pmid)
        if frag is None:
            continue
        ok, reason = (screen if args.content_screen else screen_none)(frag)
        (kept if ok else dropped).append((pmid, reason))

    def toks(items, view):
        return sum(approx_tokens(json.dumps(view(records[p]), ensure_ascii=False))
                   for p, _ in items if p in records)

    baseline = toks(kept + dropped, mcp_like_view)
    after = toks(kept, trimmed_view)

    # --- the number that decides viability ---------------------------------
    cited_in_pool = {p for p, _ in kept + dropped} & cited
    cited_kept = {p for p, _ in kept} & cited
    cited_dropped = sorted(cited_in_pool - cited_kept)

    print(f"\ncandidates retrieved        : {len(kept) + len(dropped)}")
    print(f"  kept by screen            : {len(kept)}")
    print(f"  dropped by screen         : {len(dropped)}")
    print(f"\nbaseline (all candidates,")
    print(f"  MCP-equivalent)           : ~{baseline:,} tokens")
    print(f"after screen (trimmed)      : ~{after:,} tokens")
    if after:
        print(f"compression                 : {baseline/after:.1f}x "
              f"({100*(1-after/baseline):.0f}% removed)")

    print(f"\n--- RECALL (the deciding number) ---")
    print(f"knowledge-base PMIDs in pool: {len(cited_in_pool)}")
    print(f"  survived the screen       : {len(cited_kept)}")
    print(f"  WRONGLY DROPPED           : {len(cited_dropped)}")
    if cited_in_pool:
        rec = 100 * len(cited_kept) / len(cited_in_pool)
        print(f"  recall                    : {rec:.1f}%")
    for p in cited_dropped:
        reason = next(r for q, r in dropped if q == p)
        title = trimmed_view(records[p])["title"][:70]
        print(f"    ✗ {p}  [{reason}]  {title}")

    if cited_dropped:
        print("\n⚠️  Recall is below 100%. A paper the knowledge base relies on would")
        print("    not have reached the agent. Compression is irrelevant until this")
        print("    is zero: the loss is silent — nothing downstream can notice a")
        print("    paper it was never shown.")
        return 1
    print("\n✅ Recall 100% on this pool: every cited paper survived the screen.")
    print("   Note this is the pool these queries produced; it is not proof the")
    print("   screen is safe on queries it has not seen.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    ps = sub.add_parser("survey")
    ps.add_argument("query", nargs="+")
    ps.add_argument("--retmax", type=int, default=20)
    ps.set_defaults(fn=cmd_survey)
    ph = sub.add_parser("show")
    ph.add_argument("pmids", nargs="+")
    ph.set_defaults(fn=cmd_show)
    p = sub.add_parser("measure")
    p.add_argument("--queries", help="file of one query per line")
    p.add_argument("--retmax", type=int, default=15)
    p.add_argument("--content-screen", action="store_true",
                   help="ALSO drop papers by content heuristics. Measured at 66.7%% "
                        "recall — retained only to reproduce that result.")
    p.set_defaults(fn=cmd_measure)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
