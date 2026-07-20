#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Structural checks on the knowledge base that need no network and no archive.

`dr_drill.py leg1` proves that every excerpt matches its source. It cannot prove
that a claim *has* an excerpt, because a claim with no excerpt block produces
nothing for it to check. Every defect below was found by hand during one session
in July 2026, each after a green Leg 1, and each is the same shape: **the checker
was silent, not failing.** A silent checker reads as coverage.

  orphans       A PMID cited in body prose or an index line with no excerpt block.
                Until 2026-07-20 the archive's rebuild input scanned only the
                excerpt section, so these papers were never fetched, never
                checked, and never reported. 38 of 119 (32%) were in this state.
                One of them cost a wrong flag, a wrong conclusion, and a wasted
                retrieval request to the operator.

  empty-blocks  An excerpt block with a header and nothing but annotation lines.
                It increments Leg 1's PMID count and not its excerpt count: a
                verified-looking paper that verifies nothing. Five existed; four
                had body claims resting on them.

  pii           Generic secret/PII scan — absolute home paths, private-range IP
                addresses, unexpected e-mail addresses. **Deliberately generic.**
                This repository also screens for named private entities (a
                clinic, a patient, people), and those patterns are NOT in this
                file and must never be: publishing the redline list would leak
                exactly what it exists to protect. Run that screen locally.

Exceptions live in docs/kb-exceptions.md, each with a written reason, so that
suppressing a check is a reviewable edit rather than an invisible one.

Usage:
  check_kb_hygiene.py [orphans|empty-blocks|pii|all]     # default: all
Exit code 1 if any check fails. Standard library only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KB = REPO / "knowledge-base"
EXCEPTIONS = REPO / "docs" / "kb-exceptions.md"

EXCERPT_HEADING = "## 原文摘录"
NO_SOURCE_MARKER = "no source text available"

# The maintainer's contact address, required by the Unpaywall API and
# deliberately public. Any OTHER address in the tree is a finding.
ALLOWED_EMAILS = {"wamphetamine@gmail.com"}

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PRIVATE_IP_RE = re.compile(r"\b(?:10\.\d{1,3}|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b")
HOME_PATH_RE = re.compile(r"(?:/Users/|/home/)[a-zA-Z0-9_.-]+/")

SCAN_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".txt", ".sh"}
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules"}


def load_exceptions() -> dict[str, set[str]]:
    """Parse docs/kb-exceptions.md. Lines look like:

        - orphans: 17552367 — a wrong PMID retained as evidence of the typo

    The reason after the em dash is for humans; this only needs check and id."""
    out: dict[str, set[str]] = {"orphans": set(), "empty-blocks": set(), "pii": set()}
    if not EXCEPTIONS.exists():
        return out
    for line in EXCEPTIONS.read_text(encoding="utf-8").splitlines():
        m = re.match(r"-\s*(orphans|empty-blocks|pii):\s*(\S+)", line.strip())
        if m:
            out[m.group(1)].add(m.group(2))
    return out


def kb_files() -> list[Path]:
    return sorted(KB.glob("*.md"))


def split_sections(text: str) -> tuple[str, str]:
    """(everything before the excerpt heading, everything after)."""
    head, _, tail = text.partition(EXCERPT_HEADING)
    return head, tail


def cited_pmids(head: str) -> set[str]:
    """Both citation forms the knowledge base actually uses: `PMID 12345678` in
    prose, and `(12345678, descriptor)` in the per-topic index lines."""
    return set(re.findall(r"PMID\s+(\d+)", head)) | set(re.findall(r"\((\d{7,8}),", head))


def excerpt_blocks(tail: str) -> list[tuple[str, list[str]]]:
    """[(pmid, [quoted lines]), ...] for each block in the excerpt section."""
    out = []
    for m in re.finditer(r"\*\*PMID (\d+)\*\*[^\n]*\n((?:> [^\n]*\n)*)", tail):
        out.append((m.group(1), m.group(2).splitlines()))
    return out


def check_orphans(exc: set[str]) -> list[str]:
    """Repo-wide, not per-file, and the distinction matters.

    Files cross-cite each other, so a paper excerpted in one file is legitimate
    evidence for a claim in another — Leg 1 verifies the excerpt wherever it
    lives. A per-file rule flags those as orphans and is wrong: the first
    version of this function did exactly that and reported PMID 31836868 and
    38825481 as unverified when both were excerpted and passing all along.
    That is the same false-positive shape this repository has been bitten by
    repeatedly (see the SOP's attribution sections) — a checker mistaking
    "not here" for "nowhere"."""
    have: set[str] = set()
    cited: dict[str, str] = {}          # pmid -> first file citing it
    for f in kb_files():
        head, tail = split_sections(f.read_text(encoding="utf-8"))
        have |= {p for p, _ in excerpt_blocks(tail)}
        for pmid in cited_pmids(head):
            cited.setdefault(pmid, f.name)
    problems = []
    for pmid in sorted(cited, key=int):
        if pmid not in have and pmid not in exc:
            problems.append(
                f"{cited[pmid]}: PMID {pmid} is cited but has no excerpt block "
                f"anywhere in the knowledge base. Fetch it "
                f"(tools/pubmed_archive.py fetch) and quote the sentences the "
                f"claim rests on, or add it to docs/kb-exceptions.md with a reason.")
    return problems


def check_empty_blocks(exc: set[str]) -> list[str]:
    problems = []
    for f in kb_files():
        _, tail = split_sections(f.read_text(encoding="utf-8"))
        for pmid, lines in excerpt_blocks(tail):
            quoted = [l for l in lines if l.startswith("> ") and not l.startswith("> ⚠️")]
            if quoted or pmid in exc:
                continue
            if any(NO_SOURCE_MARKER in l.lower() for l in lines):
                continue          # explicitly declared: nothing rests on it
            problems.append(
                f"{f.name}: PMID {pmid} has an excerpt block with no source text. "
                f"It counts as a checked paper and verifies nothing. Quote at "
                f"least one sentence, or state why none exists using the phrase "
                f"'{NO_SOURCE_MARKER}'.")
    return problems


def scannable_files() -> list[Path]:
    """Only files git actually tracks.

    What matters for a public repository is what gets published, not what
    happens to sit in the working tree. Local, git-ignored files legitimately
    contain absolute paths (`.claude/settings.local.json` does), and flagging
    them trains contributors to ignore the check. If git is unavailable, fall
    back to walking the tree — noisier, but never quieter."""
    import subprocess
    try:
        out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO, check=True,
                             capture_output=True, text=True).stdout
        return [REPO / p for p in out.split("\0") if p]
    except (OSError, subprocess.CalledProcessError):
        return [p for p in REPO.rglob("*")
                if not any(part in SKIP_DIRS for part in p.parts)]


def check_pii() -> list[str]:
    problems = []
    for path in sorted(scannable_files()):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        rel = path.relative_to(REPO)
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for addr in EMAIL_RE.findall(line):
                # Author contact addresses inside verbatim source excerpts are
                # part of the quoted record, not a leak from this repository.
                if addr in ALLOWED_EMAILS or line.lstrip().startswith(">"):
                    continue
                problems.append(f"{rel}:{n}: unexpected e-mail address {addr!r}")
            if PRIVATE_IP_RE.search(line):
                problems.append(f"{rel}:{n}: private-range IP address")
            if HOME_PATH_RE.search(line):
                problems.append(f"{rel}:{n}: absolute home path — use a relative "
                                f"path or ~ so the tree is portable")
    return problems


CHECKS = {
    "orphans": lambda e: check_orphans(e["orphans"]),
    "empty-blocks": lambda e: check_empty_blocks(e["empty-blocks"]),
    "pii": lambda e: check_pii(),
}


def main() -> int:
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which not in CHECKS and which != "all":
        sys.exit(f"unknown check {which!r}; expected one of {', '.join(CHECKS)} or 'all'")
    exc = load_exceptions()
    names = list(CHECKS) if which == "all" else [which]

    failed = False
    for name in names:
        problems = CHECKS[name](exc)
        if problems:
            failed = True
            print(f"\nKB_HYGIENE {name}: FAIL ({len(problems)})")
            for p in problems:
                print(f"  {p}")
        else:
            print(f"KB_HYGIENE {name}: PASS")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
