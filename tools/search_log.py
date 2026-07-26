#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Record what was searched, what was rejected, and why — so a negative claim has evidence.

    search_log.py add < entry.json     # append one entry (JSON on stdin)
    search_log.py verify               # schema + archive consistency
    search_log.py negatives            # KB claims of "nothing found" vs backing entries
    search_log.py show [--query TEXT]  # read the log back

WHY THIS EXISTS. The pipeline is careful about positives: every excerpt is
byte-checked against an archived record, and Leg 1 fails if one drifts. It has
been careless about **negatives**. A file saying *"no feline study addressing
this was located"* is a research claim, often a load-bearing one — it is the
difference between "we chose not to state a dose" and "no dose exists" — and
until this log, it rested on nothing an outside reader could check.

Measured 2026-07-27: **16 such claims across the knowledge base, none of them
verifiable.** Meanwhile 285 archived records against 283 cited PMIDs — i.e. the
archive holds essentially only what got cited. **Papers read and rejected during
a search left no trace at all**, so the same ground gets re-searched, and nobody
can audit the judgement that discarded them.

This also closes a standing gap against the operator's own conduct rule: *what
was learned — including the honest conclusion that a search found nothing —
must be recorded traceably.*

WHAT IT DELIBERATELY DOES NOT DO.

  * It does not write itself. The **reason** a paper was rejected is a judgement,
    and only the agent that read the abstract can supply it. An auto-logger would
    capture queries and lose the only part that matters.
  * It does not gate on negative claims. Matching prose to log entries by keyword
    is a heuristic; `negatives` therefore **reports** and leaves the judgement to
    a human, rather than turning a fuzzy match into a green light.
  * It distinguishes **contemporaneous** entries from **reconstructed** ones and
    never lets the second masquerade as the first — a log written from memory
    after the fact is weaker evidence, and pretending otherwise would reproduce
    the failure this whole repository exists to prevent.
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LOG = REPO / "docs" / "search-log.jsonl"
KB = REPO / "knowledge-base"

REQUIRED = ("ts", "q", "db", "hits", "kept", "rejected", "recorded")
RECORDED_VALUES = ("contemporaneous", "reconstructed")

# Phrases by which the knowledge base asserts that a search came up empty. These
# are the claims this log exists to support.
NEGATIVE_CLAIM = re.compile(
    r"no (?:feline|veterinary|comparative|head-to-head|such)[^.。\n]{0,80}"
    r"(?:locat\w*|found|exist\w*)"
    r"|(?:was|were|is|are) not located"
    r"|located no [a-z]+"
    r"|no study (?:was )?locat\w*"
    r"|未(?:能)?(?:找到|检索到|定位)"
    r"|没有找到",
    re.I)


def entries():
    if not LOG.exists():
        return []
    out = []
    for i, line in enumerate(LOG.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            out.append((i, json.loads(line)))
        except json.JSONDecodeError as e:
            sys.exit(f"{LOG.name}:{i}: not valid JSON ({e})")
    return out


def archived_pmids():
    """PMIDs present in the archive, so `kept` can be checked for consistency."""
    sys.path.insert(0, str(REPO / "tools"))
    try:
        import pubmed_archive as pa
        d = pa.archive_dir(None) / "records"
        return {p.stem for p in d.glob("*.json")} if d.is_dir() else set()
    except SystemExit:
        return set()          # no archive configured; verify degrades, not fails


def cmd_add(args):
    raw = sys.stdin.read().strip()
    if not raw:
        sys.exit("nothing on stdin; pipe one JSON object")
    try:
        e = json.loads(raw)
    except json.JSONDecodeError as exc:
        sys.exit(f"stdin is not valid JSON: {exc}")
    missing = [k for k in REQUIRED if k not in e]
    if missing:
        sys.exit(f"missing required field(s): {', '.join(missing)}")
    if e["recorded"] not in RECORDED_VALUES:
        sys.exit(f"`recorded` must be one of {RECORDED_VALUES}")
    for r in e.get("rejected", []):
        if not isinstance(r, dict) or not r.get("why"):
            sys.exit("every rejected entry needs a `why` — a PMID with no reason "
                     "records that you looked, not what you concluded")
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"appended to {LOG.relative_to(REPO)} ({len(entries())} entries)")
    return 0


def cmd_verify(args):
    rows = entries()
    if not rows:
        print("SEARCH_LOG: empty (no entries yet)")
        return 0
    arc = archived_pmids()
    problems = []
    for ln, e in rows:
        for k in REQUIRED:
            if k not in e:
                problems.append(f"line {ln}: missing `{k}`")
        if e.get("recorded") not in RECORDED_VALUES:
            problems.append(f"line {ln}: `recorded` = {e.get('recorded')!r}")
        for r in e.get("rejected", []):
            if not r.get("why"):
                problems.append(f"line {ln}: rejected {r.get('pmid')} has no reason")
        if arc:
            for p in e.get("kept", []):
                if p not in arc:
                    problems.append(f"line {ln}: kept {p} is not in the archive")
    if problems:
        print(f"SEARCH_LOG: FAIL ({len(problems)})")
        for p in problems:
            print(f"  {p}")
        return 1
    recon = sum(1 for _, e in rows if e["recorded"] == "reconstructed")
    print(f"SEARCH_LOG: PASS ({len(rows)} entries, {recon} reconstructed, "
          f"{sum(len(e.get('rejected', [])) for _, e in rows)} rejections recorded)")
    return 0


def cmd_negatives(args):
    """Every 'nothing was found' claim in the KB, and whether anything backs it.

    Matching is by keyword overlap and is **deliberately advisory**. A green tick
    here means a plausibly related search was logged, never that the claim is
    proven; the judgement stays with the reader."""
    rows = entries()
    logged = [(e.get("claim", ""), e.get("q", "")) for _, e in rows]
    print("知识库中的『未找到』类断言 —— 以及是否有检索记录支撑\n"
          "  ⚠️ 匹配为关键词启发式，仅供人工判断；打勾不等于已证实。\n")
    total = backed = 0
    for f in sorted(KB.glob("*.md")):
        hits = []
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if NEGATIVE_CLAIM.search(line):
                hits.append((i, line.strip()))
        if not hits:
            continue
        print(f"  {f.name}")
        for ln, line in hits:
            total += 1
            key = f.stem.replace("-", " ")
            ok = any(f.name in c or key.split()[0] in (c + q).lower()
                     for c, q in logged)
            backed += bool(ok)
            mark = "✅ 有记录" if ok else "❌ 无记录"
            snippet = re.sub(r"\s+", " ", line)[:96]
            print(f"    {mark}  L{ln}: {snippet}")
    print(f"\n  {total} 条断言，{backed} 条有相关检索记录，{total - backed} 条仍悬空。")
    return 0


def cmd_show(args):
    for _, e in entries():
        if args.query and args.query.lower() not in json.dumps(e, ensure_ascii=False).lower():
            continue
        print(f"[{e['ts']}] ({e['recorded']}) {e['db']}: {e['q']}")
        print(f"    hits={e['hits']} kept={e.get('kept') or '—'}")
        for r in e.get("rejected", []):
            print(f"    ✗ {r.get('pmid')}: {r['why']}")
        if e.get("claim"):
            print(f"    → backs: {e['claim']}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("add", help="append one JSON entry from stdin")
    sub.add_parser("verify", help="schema and archive consistency")
    sub.add_parser("negatives", help="KB 'nothing found' claims vs log")
    s = sub.add_parser("show", help="read the log back")
    s.add_argument("--query")
    args = ap.parse_args()
    return {"add": cmd_add, "verify": cmd_verify,
            "negatives": cmd_negatives, "show": cmd_show}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
