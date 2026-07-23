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

  coverage      A knowledge-base file the agent definition does not name, or a
                file it names that does not exist. The agent's scope boundary
                lists what it may advise from; a hardcoded list drifts the moment
                an entry is added, and it drifts silently in the dangerous
                direction — verified material sitting unused, or believed
                coverage that was renamed away.

  pii           Generic secret/PII scan — absolute home paths, private-range IP
                addresses, unexpected e-mail addresses. **Deliberately generic.**
                This repository also screens for named private entities (a
                clinic, a patient, people), and those patterns are NOT in this
                file and must never be: publishing the redline list would leak
                exactly what it exists to protect. Run that screen locally.

Exceptions live in docs/kb-exceptions.md, each with a written reason, so that
suppressing a check is a reviewable edit rather than an invisible one.

Usage:
  check_kb_hygiene.py [orphans|empty-blocks|coverage|pii|all]   # default: all
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


# Every check name. load_exceptions() derives its accepted keys from this, so a
# new check cannot ship with a suppression hatch that silently does nothing.
CHECK_NAMES = ("orphans", "empty-blocks", "coverage", "stale-pdf",
               "stale-translation", "agents-sync", "kb-index", "pii",
               "docs-xref")


def load_exceptions() -> dict[str, set[str]]:
    """Parse docs/kb-exceptions.md. Lines look like:

        - orphans: 17552367 — a wrong PMID retained as evidence of the typo

    The reason after the em dash is for humans; this only needs check and id.

    ⚠️ **Keys are derived from CHECK_NAMES, never hand-listed, and this function
    is the reason that rule exists.** Both the key dict and the regex were once
    typed out by hand, and every check added after that shipped with a
    suppression hatch that silently did nothing: a `- stale-pdf: ...` line
    parsed to nothing at all, while the check's own failure message instructed
    the user to write exactly that. CI would have stayed red with no legitimate
    way to accept a finding, and the refusal would have looked like the tool
    being right.

    That was reported as fixed on 2026-07-21 and **was not** — the edit did not
    apply, the claim went into a commit message unverified, and three further
    checks (`agents-sync`, `kb-index`, `stale-translation`) inherited the same
    dead hatch. Caught by testing the suppression path of a new check rather
    than only its detection path. **Test the escape hatch, not just the alarm.**
    """
    out: dict[str, set[str]] = {name: set() for name in CHECK_NAMES}
    if not EXCEPTIONS.exists():
        return out
    for line in EXCEPTIONS.read_text(encoding="utf-8").splitlines():
        m = re.match(r"-\s*([a-z][a-z-]*):\s*(\S+)", line.strip())
        if m and m.group(1) in out:
            out[m.group(1)].add(m.group(2))
    return out


def kb_files() -> list[Path]:
    """Knowledge base AND owner guides -- see pubmed_archive.corpus_files()."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from pubmed_archive import corpus_files
    return corpus_files()


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


def check_pii(exc: set[str] | None = None) -> list[str]:
    problems = []
    for path in sorted(scannable_files()):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        rel = path.relative_to(REPO)
        if str(rel) in (exc or set()):
            continue
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


AGENT = REPO / ".claude" / "agents" / "medical.md"


def check_coverage(exc: set[str]) -> list[str]:
    """The agent's scope boundary names the files it may advise from. A hardcoded
    list drifts the moment someone adds a knowledge-base entry — and it drifts
    silently in the dangerous direction: a file exists, the agent does not know
    it may use it, so verified material sits unused; or a file is renamed and the
    agent believes it has coverage it no longer has.

    The list in the agent is explicitly a snapshot with the directory declared
    authoritative, which limits the damage. This check keeps the snapshot true."""
    if not AGENT.exists():
        return []
    text = AGENT.read_text(encoding="utf-8")
    listed = set(re.findall(r"`([a-z0-9-]+\.md)`", text))
    # README.md is the generated clinician index, not a knowledge file. It names
    # no condition and carries no excerpts, so requiring the agent to list it as
    # a covered topic would be asking the agent to claim coverage of an index.
    # Excluded: the generated index (names no condition), and `*.zh.md`
    # translations (the same topic in another language, already declared by the
    # English file). Requiring the agent to list a translation separately would
    # make it claim two coverages for one subject.
    actual = {f.name for f in sorted(KB.glob("*.md"))
              if f.name != "README.md" and not f.name.endswith(".zh.md")}
    problems = []
    for name in sorted(actual - listed):
        if name in exc:
            continue
        problems.append(
            f".claude/agents/medical.md: knowledge-base/{name} exists but is not "
            f"named anywhere in the agent definition. Add it to the Scope boundary "
            f"table, or the agent will decline questions it actually has verified "
            f"material for.")
    for name in sorted(listed - actual):
        if name.startswith(("feline-", "chronic-", "emergency-", "supportive-",
                            "antineoplastic-", "targeted-", "hyperthyroidism-",
                            "upper-airway-", "evidence-")) and name not in exc:
            problems.append(
                f".claude/agents/medical.md references knowledge-base/{name}, "
                f"which does not exist. The agent believes it has coverage it "
                f"does not have.")
    return problems


def last_commit(path: Path) -> int | None:
    """Git commit time of a path, or None if never committed.

    Deliberately git, not the filesystem: a fresh clone rewrites every mtime, so
    an mtime comparison would pass vacuously everywhere except the machine the
    files were last edited on — the opposite of what a check is for."""
    import subprocess
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(path.relative_to(REPO))],
            cwd=REPO, check=True, capture_output=True, text=True).stdout.strip()
        return int(out) if out else None
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None


TRANSLATION = re.compile(r"^(?P<stem>.+)\.(?P<lang>[a-z]{2}(?:-[A-Z]{2})?)\.md$")


def translation_pairs() -> list[tuple[Path, Path, str]]:
    """[(original, translation, lang)] for files that are genuinely translations.

    A `*.zh.md` file is only a translation when `*.md` also exists. The four
    owner guides are Chinese ORIGINALS with no English counterpart, and treating
    them as translations of a non-existent source would fire on every commit —
    a check that cries wolf is a check people learn to ignore."""
    out = []
    for d in ("knowledge-base", "guides"):
        for f in sorted((REPO / d).glob("*.*.md")):
            m = TRANSLATION.match(f.name)
            if not m:
                continue
            orig = f.with_name(m.group("stem") + ".md")
            if orig.exists():
                out.append((orig, f, m.group("lang")))
    return out


def check_stale_translation(exc: set[str]) -> list[str]:
    """A translation older than the original it renders.

    Added 2026-07-21 BEFORE the second language rather than after, on the
    reasoning in `docs/LITERATURE-PIPELINE-SOP.md` §11: this is cheap to add at
    two languages and a matrix-wide retrofit at three.

    **What goes stale is the prose, and only the prose.** The `## 原文摘录`
    section is byte-identical across languages and Leg 1 already checks every
    copy of it — so a stale translation never carries a wrong quotation. It
    carries something subtler: an interpretation the English original has since
    corrected. This repository has already corrected a mechanism claim that
    contradicted its own source, and withdrawn a figure that turned out to be
    unattributable. A translation frozen before either of those would still be
    stating them, in a language whose readers cannot compare against the
    original — which is exactly the audience with no way to notice.

    Same family as `stale-pdf`: a derived artifact that does not update itself."""
    problems = []
    for orig, trans, lang in translation_pairs():
        if trans.name in exc:
            continue
        t_o, t_t = last_commit(orig), last_commit(trans)
        if t_o is None or t_t is None:
            continue                      # uncommitted; nothing to compare yet
        if t_o > t_t:
            mins = (t_o - t_t) // 60
            problems.append(
                f"{trans.name} is {mins} min older than {orig.name}. The prose "
                f"may now state something the original has corrected, and its "
                f"readers are the ones who cannot check against the original. "
                f"Re-translate the changed sections (excerpts stay byte-identical "
                f"— never re-translate those), or add it to docs/kb-exceptions.md "
                f"with a reason.")
    return problems


def check_stale_pdf(exc: set[str]) -> list[str]:
    """A committed PDF older than the Markdown it renders.

    **The PDF is the only artifact here that leaves the reader's control.** An
    owner downloads it, prints it, forwards it to another owner — and unlike the
    site, it never updates. Yet it was the one product with no verification at
    all: the corpus checks read Markdown, and CI never looked at a PDF.

    Found 2026-07-21 by reading the repository as a stranger would. Both lymphoma
    PDFs were roughly a day behind their sources, and the gap was not cosmetic —
    the sources had since gained 62 inline PMIDs and, more seriously, an 出处待核
    flag on a survival figure that could not be traced to any source. **The stale
    PDFs still presented that figure as authoritative.** The most-forwarded
    artifact was the least trustworthy one.

    Compares git commit times, not filesystem mtimes: a fresh clone rewrites
    every mtime, so mtime would make this check pass vacuously everywhere except
    the maintainer's own machine — which is the opposite of what a check is for.
    """
    problems = []
    for md in sorted((REPO / "guides").glob("*.md")):
        pdf = md.with_suffix(".pdf")
        if not pdf.exists() or md.name in exc:
            continue
        t_md, t_pdf = last_commit(md), last_commit(pdf)
        if t_md is None or t_pdf is None:
            continue                      # uncommitted; nothing to compare yet
        if t_md > t_pdf:
            mins = (t_md - t_pdf) // 60
            problems.append(
                f"{pdf.name} is {mins} min older than {md.name}. The PDF is what "
                f"readers download and forward, and it does not update itself. "
                f"Rebuild it (tools/render_markdown.py + headless Chrome, see "
                f"CONTRIBUTING.md) or add it to docs/kb-exceptions.md with a reason.")
    return problems


def _run_generator(script: str, label: str) -> list[str]:
    """Run a generator's --check mode and surface its complaint verbatim."""
    import subprocess
    try:
        r = subprocess.run([sys.executable, str(REPO / "tools" / script), "--check"],
                           cwd=REPO, capture_output=True, text=True)
    except OSError as exc_:
        return [f"could not run {script} ({exc_})"]
    if r.returncode == 0:
        return []
    return [l for l in (r.stdout + r.stderr).splitlines() if l.strip()]


def check_kb_index(exc: set[str]) -> list[str]:
    """knowledge-base/README.md drifted from the corpus it indexes.

    It is the entry point a clinician meets first, and it states each file's
    paper and excerpt counts. A stale index misreports the size of the evidence
    base to exactly the readers most likely to check."""
    return _run_generator("build_kb_index.py", "kb-index")


def check_agents_sync(exc: set[str]) -> list[str]:
    """Portable agent prompts drifted from their Claude source.

    `agents/*.prompt.md` are generated from `.claude/agents/`. Two copies of a
    prompt always drift, and a drifted OWNER-FACING prompt is the dangerous
    kind: a non-Claude host would be running an older set of safety rules while
    the repository shows the newer ones."""
    import subprocess
    try:
        r = subprocess.run([sys.executable, str(REPO / "tools" / "export_agents.py"),
                            "--check"], cwd=REPO, capture_output=True, text=True)
    except OSError as exc_:
        return [f"could not run export_agents.py ({exc_})"]
    if r.returncode == 0:
        return []
    return [line for line in (r.stdout + r.stderr).splitlines() if line.strip()]


# A markdown filename referenced from docs/. Explicit paths (`knowledge-base/x.md`)
# must resolve at that path; a bare `x.md` in backticks may live in any of the
# directories a doc legitimately points into. Bare names require the backticks —
# an unquoted "foo.md" in prose is too ambiguous to treat as a file reference.
DOC_XREF_DIRS = ("", "docs", "knowledge-base", "guides", ".claude/agents")
DOC_XREF_PATH_RE = re.compile(
    r"`?((?:knowledge-base|guides|docs|\.claude/agents)/[A-Za-z0-9._-]+\.md)`?")
DOC_XREF_BARE_RE = re.compile(r"`([A-Za-z0-9._-]+\.md)`")


def check_docs_xref(exc: set[str]) -> list[str]:
    """A markdown file named in docs/ that resolves to nothing on disk.

    docs/ sits OUTSIDE corpus_files(), so no other check here verifies that a
    `knowledge-base/foo.md` pointer in the SOP still names a real file. When a
    knowledge-base entry is renamed or removed, the prose pointing at it goes
    stale silently — precisely the cross-reference rot §7a warns about, in the
    one directory the corpus checks never reach. This closes it: an explicit
    path must resolve at that path; a bare `name.md` must exist in one of the
    directories a doc plausibly references. A reference that is intentionally
    forward-looking goes in docs/kb-exceptions.md as `- docs-xref: name`."""
    problems = []
    docs_dir = REPO / "docs"
    if not docs_dir.is_dir():
        return problems
    for f in sorted(docs_dir.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        refs: dict[str, str] = {}                  # ref -> kind (first wins)
        for m in DOC_XREF_PATH_RE.finditer(text):
            refs.setdefault(m.group(1), "path")
        for m in DOC_XREF_BARE_RE.finditer(text):
            refs.setdefault(m.group(1), "bare")
        for ref, kind in sorted(refs.items()):
            if ref in exc:
                continue
            if kind == "path":
                ok = (REPO / ref).is_file()
            else:
                ok = any((REPO / d / ref).is_file() for d in DOC_XREF_DIRS)
            if not ok:
                problems.append(
                    f"{f.name}: references `{ref}`, which resolves to no file. "
                    f"Point it at the current name, or record it in "
                    f"docs/kb-exceptions.md as '- docs-xref: {ref}' with a reason.")
    return problems


CHECKS = {
    "orphans": lambda e: check_orphans(e["orphans"]),
    "empty-blocks": lambda e: check_empty_blocks(e["empty-blocks"]),
    "coverage": lambda e: check_coverage(e.get("coverage", set())),
    "stale-pdf": lambda e: check_stale_pdf(e.get("stale-pdf", set())),
    "stale-translation": lambda e: check_stale_translation(e.get("stale-translation", set())),
    "agents-sync": lambda e: check_agents_sync(e.get("agents-sync", set())),
    "kb-index": lambda e: check_kb_index(e.get("kb-index", set())),
    "pii": lambda e: check_pii(e.get("pii", set())),
    "docs-xref": lambda e: check_docs_xref(e.get("docs-xref", set())),
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
