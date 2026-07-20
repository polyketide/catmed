#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Disaster-recovery drill for the literature archive. See
docs/LITERATURE-PIPELINE-SOP.md section 4a.

Governing idea, inherited from the sibling project: `runs != works` applied to
backups themselves. Prove the archive RESTORES, not merely that it was written.

Leg 1 — archive rebuild. Rebuild from the repository's committed PMID list alone
        and assert every source excerpt in the knowledge base still appears, word
        for word, in the re-fetched record. This tests the cache-not-truth split
        (SOP section 3) and the frozen-baseline invariant (section 4) at once.

Self-test — corrupt a record in a scratch copy on purpose and assert Leg 1 fails.
        A detector never shown a fault has not been shown to work, so `--self-test`
        is not optional garnish; a PASS without it means little.

Each leg prints one machine-greppable verdict line. A leg that cannot run prints
SKIP; it never fabricates a PASS.

Usage:
  dr_drill.py leg1 [--archive DIR] [-v]
  dr_drill.py self-test [--archive DIR]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pubmed_archive import archive_dir, KB  # noqa: E402

# Excerpt lines beginning with these are the author's own annotations, not source
# text, and are excluded from verification.
ANNOTATION_MARKERS = ("⚠️", "**", "The sentences below", "The prose in the body",
                      "Only sentences carrying")


def norm(s: str) -> str:
    """Normalise for comparison, and ONLY for comparison.

    The archive keeps bytes verbatim; this is the reader that has to bridge two
    representations of the same text. PubMed's XML carries entities and NFC/NFD
    variation, and a Markdown excerpt was copied out of an already-decoded view.
    Whitespace is collapsed because line wrapping differs between the two, not
    because whitespace is unimportant — U+00A0 and U+2009 survive in the archive
    and are only folded here, at compare time.
    """
    s = html.unescape(s)
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("‐", "-").replace("‑", "-").replace("‒", "-")
    s = s.replace("–", "-").replace("—", "-").replace("−", "-")
    s = s.replace("‘", "'").replace("’", "'")
    s = s.replace("“", '"').replace("”", '"')
    # Case-folded: a structured abstract's section label renders as "RESULTS" in
    # the XML attribute and "Results:" in most readers. That difference is
    # presentational. Content drift — a changed figure or word — survives this.
    return re.sub(r"\s+", " ", s).strip().casefold()


FULLTEXT_MARKER = "PMC full text retrieved and checked"


def excerpts_from_kb() -> dict[str, list[tuple[str, str, str]]]:
    """PMID -> [(source file, sentence, origin)] from every `## 原文摘录` section.

    `origin` is "abstract" or "fulltext". The knowledge base marks the boundary
    with 【PMC full text retrieved and checked】: excerpts after that marker were
    taken from the PMC full text, so they are *correctly* absent from the PubMed
    abstract and must not be counted as failures. Leg 1 can only verify the
    abstract-sourced ones; conflating the two would make it report either false
    failures or false confidence.
    """
    out: dict[str, list[tuple[str, str, str]]] = {}
    for f in sorted(KB.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        if "## 原文摘录" not in text:
            continue
        current = None
        origin = "abstract"
        for line in text.split("## 原文摘录", 1)[1].splitlines():
            stripped = line.strip()
            if stripped.startswith("---"):        # section break ends a PMID block
                current, origin = None, "abstract"
                continue
            m = re.match(r"\*\*PMID\s+(\d+)\*\*", stripped)
            if m:
                current, origin = m.group(1), "abstract"
                continue
            if current and line.startswith("> "):
                body = line[2:].strip()
                if FULLTEXT_MARKER in body:
                    origin = "fulltext"
                    continue
                # Source sentences are plain prose. A line carrying Markdown
                # emphasis or a warning glyph is this project's own annotation.
                if not body or "**" in body or any(
                        body.startswith(a) for a in ANNOTATION_MARKERS):
                    continue
                out.setdefault(current, []).append((f.name, body, origin))
    return out


def abstract_of(raw_xml: str) -> str:
    """All abstract text of a record, joined. Structured abstracts carry several
    AbstractText nodes; excerpts may span or sit inside any of them."""
    art = ET.fromstring(raw_xml)
    parts = []
    for t in art.iter("AbstractText"):
        label = t.get("Label")
        body = "".join(t.itertext())
        # Readers render the label inline ("RESULTS: ..."); the XML keeps it as
        # an attribute. Excerpts copied from a rendered view carry the prefix.
        parts.append(f"{label}: {body}" if label else body)
    for t in art.iter("ArticleTitle"):
        parts.append("".join(t.itertext()))
    return " ".join(parts)


def load_archive(arc: Path) -> dict[str, str]:
    recs = {}
    for f in (arc / "records").glob("*.json"):
        rec = json.loads(f.read_text(encoding="utf-8"))
        recs[rec["pmid"]] = rec["raw_xml"]
    return recs


def leg1(arc: Path, verbose: bool = False) -> tuple[str, str, set]:
    """Returns (verdict, detail, unmatched_keys).

    The third value lets the self-test prove that an injected fault changed the
    result, rather than merely observing that the run failed for reasons that
    were already there.
    """
    if not (arc / "records").is_dir():
        return "SKIP", f"no archive at {arc} — run pubmed_archive.py fetch", set()

    excerpts = excerpts_from_kb()
    if not excerpts:
        return "SKIP", "no source excerpts found in knowledge-base/", set()

    archive = load_archive(arc)

    missing_records: list[str] = []
    unmatched: list[tuple[str, str, str]] = []
    checked = skipped_fulltext = 0

    for pmid, items in sorted(excerpts.items()):
        raw = archive.get(pmid)
        if raw is None:
            missing_records.append(pmid)
            continue
        hay = norm(abstract_of(raw))
        for src_file, sentence, origin in items:
            if origin == "fulltext":
                # Correctly absent from the abstract; out of this leg's reach.
                skipped_fulltext += 1
                continue
            checked += 1
            if norm(sentence) not in hay:
                unmatched.append((pmid, src_file, sentence))

    if verbose:
        for pmid, src, sent in unmatched:
            print(f"  UNMATCHED {pmid} ({src}): {sent[:100]}"
                  f"{'...' if len(sent) > 100 else ''}")
        for pmid in missing_records:
            print(f"  NO-RECORD {pmid}")

    detail = (f"{len(excerpts)} PMIDs, {checked} abstract-sourced excerpts checked, "
              f"{len(unmatched)} unmatched, {len(missing_records)} records missing, "
              f"{skipped_fulltext} full-text excerpts not verifiable here")
    keys = {(p, s) for p, _f, s in unmatched}
    if missing_records or unmatched:
        return "FAIL", detail, keys
    return "PASS", detail, keys


def cmd_leg1(args) -> int:
    arc = archive_dir(args.archive)
    verdict, detail, _ = leg1(arc, args.verbose)
    print(f"DR_LEG1: {verdict} ({detail})")
    return 0 if verdict == "PASS" else 1


def cmd_self_test(args) -> int:
    """Prove Leg 1 detects an injected fault. Corrupts a scratch copy only.

    ⚠️ The obvious version of this test is wrong, and the first version here was:
    asserting only that the corrupted run returns FAIL passes trivially whenever
    the baseline already fails, which is exactly when a broken detector most
    needs catching. The test must show the injected fault produced a NEW finding.
    """
    arc = archive_dir(args.archive)
    if not (arc / "records").is_dir():
        print(f"DR_SELFTEST: SKIP (no archive at {arc})")
        return 0

    base_verdict, _base_detail, base_keys = leg1(arc)
    if base_verdict == "SKIP":
        print("DR_SELFTEST: SKIP (leg1 could not run on the real archive)")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / "arc"
        shutil.copytree(arc, scratch)

        # Target a PMID whose abstract-sourced excerpts currently all MATCH, so
        # any new failure is unambiguously ours.
        excerpts = excerpts_from_kb()
        target = None
        for pmid, items in sorted(excerpts.items()):
            if not (scratch / "records" / f"{pmid}.json").exists():
                continue
            abstract_items = [s for _f, s, o in items if o == "abstract"]
            if abstract_items and not any((pmid, s) in base_keys for s in abstract_items):
                target = pmid
                break
        if target is None:
            print("DR_SELFTEST: SKIP (no clean record available to corrupt)")
            return 0

        f = scratch / "records" / f"{target}.json"
        rec = json.loads(f.read_text(encoding="utf-8"))
        # Corrupt the text of an excerpt Leg 1 actually checks. Damaging an
        # arbitrary span is not enough: an earlier version mangled the opening
        # section of a structured abstract while every checked sentence sat in
        # RESULTS, so the injected fault was invisible and the test passed for
        # the wrong reason.
        victim = next(s for _fn, s, o in excerpts[target] if o == "abstract")
        words = victim.split()
        probe = " ".join(words[:6]) if len(words) >= 6 else victim
        if probe not in rec["raw_xml"]:
            print(f"DR_SELFTEST: SKIP (cannot locate excerpt text verbatim in "
                  f"PMID {target}; nothing to corrupt deterministically)")
            return 0
        rec["raw_xml"] = rec["raw_xml"].replace(probe, "CORRUPTED_BY_SELFTEST", 1)
        f.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")

        _v, detail, new_keys = leg1(scratch)
        introduced = {k for k in new_keys - base_keys if k[0] == target}
        if introduced:
            print(f"DR_SELFTEST: PASS (injected corruption in PMID {target} produced "
                  f"{len(introduced)} new unmatched excerpt(s); baseline had "
                  f"{len(base_keys)} unrelated)")
            return 0
        print(f"DR_SELFTEST: FAIL (corrupting PMID {target} produced NO new finding — "
              f"leg1 is not detecting this fault class; {detail})", file=sys.stderr)
        return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("leg1")
    p1.add_argument("--archive")
    p1.add_argument("-v", "--verbose", action="store_true")
    p1.set_defaults(fn=cmd_leg1)
    p2 = sub.add_parser("self-test")
    p2.add_argument("--archive")
    p2.set_defaults(fn=cmd_self_test)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
