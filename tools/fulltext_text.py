#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract the TEXT layer of held full-text PDFs, so full-text excerpts can be verified.

    fulltext_text.py extract [--force]   # pdftotext every held PDF into the archive
    fulltext_text.py status              # what is extracted, what needs OCR

WHY THIS EXISTS. Leg 1 compares every excerpt against an archived record, and
that record is the PubMed **abstract**. An excerpt taken from a full text is
correctly absent from the abstract, so Leg 1 has always had to skip it: measured
2026-07-27, **82 of 908 excerpts were marked "not verifiable here"** — the exact
fraction of the knowledge base standing outside the discipline the project is
built on. Reading more full texts makes that number grow, not shrink, unless the
full text is archived too. This closes that.

Adopted from the sibling project's `docs/GPU-LITERATURE-READING-SOP.md`, whose
reading rules bind any model or frontend:

  * **Text-first.** A text-bearing PDF is read via `pdftotext` and the TEXT is
    what gets read — never PDF-image vision tokens. Here it is also what gets
    archived, so the comparison is against bytes rather than against a view.
  * **Scanned → OCR, not guessed.** Under 200 characters means there is no text
    layer. Such a file is reported for OCR and **never** silently treated as an
    empty document, which would make every excerpt "unverifiable" and read as
    though nothing were wrong.
  * **Provenance is recorded, not assumed.** Each extraction stores WHO produced
    it and WHEN, alongside the SHA-256 of the PDF it came from — so a re-download
    that changes the file cannot leave a stale extraction looking current.

WHAT IT DELIBERATELY DOES NOT DO. It does not put the text, or the PDF, in the
repository. Both live in the archive outside it (SOP §3): the PDFs are third-party
copyrighted articles and the repository is public.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import sys
from datetime import datetime, timezone
from pathlib import Path

MIN_CHARS = 200          # below this there is no text layer — OCR, do not guess

# ⚠️ Column ordering is a heuristic and NEITHER mode is right for every paper, so
# both are extracted and an excerpt may match either. Measured 2026-07-27: the
# default mode shreds a two-column JVIM perspective by interleaving the columns
# line by line — "…which is sup-  emphases. EQUATOR, an excellent resource…" —
# turning 10 correctly transcribed excerpts into 10 apparent failures. `-raw`
# follows the content stream and reads that paper correctly; it is not a
# universal improvement, which is exactly why the choice is not made here.
MODES = {"flow": (), "raw": ("-raw",)}
FULLTEXT = Path(os.path.expanduser("~/.catmed-archive/fulltext"))
TEXTDIR = Path(os.path.expanduser("~/.catmed-archive/fulltext-txt"))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()


def sidecar(pmid: str) -> Path:
    return TEXTDIR / f"{pmid}.json"


def extract_one(pdf: Path, force: bool = False) -> tuple[str, str]:
    """(state, detail); state in {'ok','ocr','stale-ok','skip','error'}."""
    pmid = pdf.stem
    txt, meta = TEXTDIR / f"{pmid}.txt", sidecar(pmid)
    digest = sha256(pdf)
    if txt.exists() and meta.exists() and not force:
        try:
            prev = json.loads(meta.read_text(encoding="utf-8"))
        except Exception:
            prev = {}
        if prev.get("pdf_sha256") == digest:
            return "skip", "already extracted, PDF unchanged"
        return "stale-ok", "PDF changed since extraction — re-extracting"
    bodies = {}
    for mode, flags in MODES.items():
        try:
            out = subprocess.run(["pdftotext", "-q", *flags, str(pdf), "-"],
                                 capture_output=True, timeout=180)
        except FileNotFoundError:
            return "error", "pdftotext not installed (brew install poppler)"
        except subprocess.TimeoutExpired:
            return "error", f"pdftotext timed out in {mode} mode"
        bodies[mode] = out.stdout.decode("utf-8", errors="replace")
    body = bodies["flow"]
    if len(body.strip()) < MIN_CHARS:
        return "ocr", f"no text layer ({len(body.strip())} chars) — needs OCR"
    TEXTDIR.mkdir(parents=True, exist_ok=True)
    txt.write_text(body, encoding="utf-8")
    (TEXTDIR / f"{pmid}.raw.txt").write_text(bodies["raw"], encoding="utf-8")
    meta.write_text(json.dumps({
        "pmid": pmid,
        "pdf_sha256": digest,
        "chars": {k: len(v) for k, v in bodies.items()},
        "extracted_by": "pdftotext",
        "modes": {k: " ".join(v) or "(default)" for k, v in MODES.items()},
        "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return "ok", f"{len(body)} chars"


def jats_text(xml_bytes: bytes) -> str:
    """Readable text from a JATS article, in document order.

    Element-by-element rather than a bare itertext() over the root: the latter
    also sweeps up <front> metadata — journal titles, affiliations, funding —
    which would put strings in the extracted text that are not in the article's
    prose. An excerpt check comparing against that is comparing against the
    wrong bytes.

    <sec> boundaries become blank lines so paragraphs stay separable, and
    <title> keeps its heading on its own line. Tables and figure graphics are
    skipped: their captions are kept, their contents are not text.

    <supplementary-material> is skipped too, and that one was found by testing
    rather than by reading the spec. Its boilerplate — "Supplemental material,
    sj-docx-N-… for <title> by <authors> in <journal>" — sits inside <body>, not
    <front>, so restricting the walk to the body does not exclude it. Left in,
    it puts the journal name and the full author list into what is supposed to
    be article prose, and an excerpt check would then be comparing against
    strings the authors never wrote in the text.
    """
    root = ET.fromstring(xml_bytes)
    body = root.find(".//body")
    if body is None:
        return ""
    supp = {id(d) for s in body.iter("supplementary-material") for d in s.iter()}
    parts: list[str] = []
    for el in body.iter():
        if id(el) in supp:
            continue
        if el.tag in ("table", "graphic", "inline-formula", "disp-formula"):
            continue
        if el.tag in ("title", "p", "label"):
            chunk = " ".join("".join(el.itertext()).split())
            if chunk:
                parts.append(chunk + ("\n" if el.tag == "title" else ""))
    return "\n\n".join(parts).strip() + "\n"


def extract_one_xml(xml: Path, force: bool = False) -> tuple[str, str]:
    """(state, detail) for a JATS full text, mirroring extract_one for PDFs.

    Same discipline as the PDF path, for the same reason: a short result is
    reported, never written as though the document were empty. An empty <body>
    is what a metadata-only JATS stub looks like, and treating it as an
    extracted document would mark every excerpt from that paper unverifiable
    while the run still reported success.
    """
    pmid = xml.stem
    txt, meta = TEXTDIR / f"{pmid}.txt", sidecar(pmid)
    digest = sha256(xml)
    if txt.exists() and meta.exists() and not force:
        try:
            prev = json.loads(meta.read_text(encoding="utf-8"))
        except Exception:
            prev = {}
        if prev.get("source_sha256") == digest or prev.get("pdf_sha256") == digest:
            return "skip", "already extracted, source unchanged"
        return "stale-ok", "source changed since extraction — re-extracting"
    try:
        body = jats_text(xml.read_bytes())
    except ET.ParseError as exc:
        return "error", f"not parseable as XML ({exc})"
    if len(body.strip()) < MIN_CHARS:
        return "short", (f"JATS body yielded {len(body.strip())} chars — "
                         f"metadata-only stub, not written")
    TEXTDIR.mkdir(parents=True, exist_ok=True)
    txt.write_text(body, encoding="utf-8")
    meta.write_text(json.dumps({
        "pmid": pmid,
        "source_sha256": digest,
        "source_suffix": ".xml",
        "chars": {"jats": len(body)},
        "extracted_by": "jats-xml",
        "extracted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return "ok", f"{len(body)} chars"


def load_text(pmid: str) -> str | None:
    """The default-mode text for one PMID, or None."""
    p = TEXTDIR / f"{pmid}.txt"
    return p.read_text(encoding="utf-8") if p.exists() else None


def load_texts(pmid: str) -> list[str]:
    """Every extracted rendering of one PDF. Leg 5 accepts a match in any of
    them: a column-order difference is the extractor's artefact, not drift, and
    no word or digit can differ between renderings of the same page."""
    out = []
    for name in (f"{pmid}.txt", f"{pmid}.raw.txt"):
        p = TEXTDIR / name
        if p.exists():
            out.append(p.read_text(encoding="utf-8"))
    return out


def cmd_extract(args) -> int:
    if not FULLTEXT.is_dir():
        sys.exit(f"no full-text directory at {FULLTEXT}")
    counts: dict[str, int] = {}
    ocr: list[str] = []
    for pdf in sorted(FULLTEXT.glob("*.pdf")):
        state, detail = extract_one(pdf, args.force)
        counts[state] = counts.get(state, 0) + 1
        if state == "ocr":
            ocr.append(f"{pdf.stem}: {detail}")
        if state == "error":
            print(f"  ERROR {pdf.stem}: {detail}")
    # JATS full texts arrive from Europe PMC alongside the PDFs. Globbing only
    # *.pdf here would skip them in silence: `status` would report nothing
    # outstanding while the text sat unextracted and its excerpts stayed
    # unverifiable.
    for xml in sorted(FULLTEXT.glob("*.xml")):
        if (FULLTEXT / f"{xml.stem}.pdf").exists():
            continue          # PDF already handled this PMID
        state, detail = extract_one_xml(xml, args.force)
        counts[state] = counts.get(state, 0) + 1
        if state in ("error", "short"):
            print(f"  {state.upper()} {xml.stem}: {detail}")
    print("FULLTEXT_TEXT: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    if ocr:
        print(f"\n{len(ocr)} PDF(s) have no text layer and were NOT extracted:")
        for line in ocr:
            print(f"  {line}")
        print("These need OCR. They are not treated as empty documents.")
    return 0


def cmd_status(args) -> int:
    pdfs = {p.stem for p in FULLTEXT.glob("*.pdf")} if FULLTEXT.is_dir() else set()
    xmls = ({p.stem for p in FULLTEXT.glob("*.xml")} - pdfs) if FULLTEXT.is_dir() else set()
    held = pdfs | xmls
    txts = {p.stem for p in TEXTDIR.glob("*.txt")
            if not p.name.endswith(".raw.txt")} if TEXTDIR.is_dir() else set()
    print(f"PDFs held      : {len(pdfs)}")
    print(f"JATS XML held  : {len(xmls)}")
    print(f"text extracted : {len(txts)}")
    missing = sorted(held - txts)
    if missing:
        print(f"not extracted  : {len(missing)} -> {', '.join(missing[:10])}"
              f"{' …' if len(missing) > 10 else ''}")
    stale = []
    for pmid in sorted(held & txts):
        try:
            meta = json.loads(sidecar(pmid).read_text(encoding="utf-8"))
        except Exception:
            stale.append(pmid)
            continue
        src = FULLTEXT / f"{pmid}.pdf"
        if not src.exists():
            src = FULLTEXT / f"{pmid}.xml"
        recorded = meta.get("source_sha256") or meta.get("pdf_sha256")
        if not src.exists() or recorded != sha256(src):
            stale.append(pmid)
    print(f"stale (source changed since extraction): {len(stale)}"
          + (f" -> {', '.join(stale)}" if stale else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract", help="pdftotext every held PDF into the archive")
    e.add_argument("--force", action="store_true", help="re-extract even if current")
    sub.add_parser("status", help="what is extracted, what needs OCR")
    args = ap.parse_args()
    return {"extract": cmd_extract, "status": cmd_status}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
