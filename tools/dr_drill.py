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

Leg 5 — full-text excerpts. The excerpts Leg 1 structurally cannot reach, checked
        against `pdftotext` output archived by fulltext_text.py. See SOP section 3l.

Self-test — corrupt a record in a scratch copy on purpose and assert Leg 1 fails.
        A detector never shown a fault has not been shown to work, so `--self-test`
        is not optional garnish; a PASS without it means little.

Each leg prints one machine-greppable verdict line. A leg that cannot run prints
SKIP; it never fabricates a PASS.

Usage:
  dr_drill.py leg1 [--archive DIR] [-v]
  dr_drill.py leg2 [--count N] [--batch N]
  dr_drill.py leg4 [--archive DIR] [-v]
  dr_drill.py leg5 [-v]
  dr_drill.py self-test [--archive DIR]
"""
from __future__ import annotations

import argparse
import functools
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
from pubmed_archive import archive_dir, KB, corpus_files, gate_record, GRADE_RAW  # noqa: E402

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


# Matches both provenance forms the knowledge base uses: PMC full text, and a
# publisher PDF supplied directly. The common substring is deliberate — a new
# source type should be recognised by adding words around this phrase, not by
# inventing a marker the checker has never heard of. (It was, once: excerpts
# marked "Publisher full text" were treated as abstract-sourced and failed
# verification, which is how this was found — and the first fix attempt failed
# too, because the new marker read "full text (PDF) retrieved and checked",
# interrupting the very phrase being matched. Keep the phrase CONTIGUOUS and put
# qualifiers outside it.)
#
# ⚠️ And it must be matched in every language the corpus is written in. The
# checker was English-only until 2026-07-21, while the owner guides — the only
# documents here a cat owner reads — are Chinese and mark the same provenance as
# 【已取 PMC 全文核对】. When the guides entered verification for the first time,
# five excerpts failed as "not in the abstract" when the full text had in fact
# been retrieved and checked; four of them appear verbatim in a knowledge-base
# block carrying the English marker and passing. Nothing was wrong with the
# documents. A monolingual checker on a multilingual corpus does not report that
# it cannot read half of it — it reports that half of it is wrong.
FULLTEXT_MARKERS = (
    "full text retrieved and checked",   # English: PMC or publisher PDF
    "全文核对",                            # Chinese: 【已取 PMC 全文核对】
)
FULLTEXT_MARKER = FULLTEXT_MARKERS[0]    # kept for the self-test's fault injection


def is_fulltext_marker(body: str) -> bool:
    return any(m in body for m in FULLTEXT_MARKERS)


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
    for f in corpus_files():
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
                if is_fulltext_marker(body):
                    origin = "fulltext"
                    continue
                # Source sentences are plain prose. A line carrying Markdown
                # emphasis or a warning glyph is this project's own annotation.
                if not body or "**" in body or any(
                        body.startswith(a) for a in ANNOTATION_MARKERS):
                    continue
                out.setdefault(current, []).append((f.name, body, origin))
    return out


def abstract_of(raw_xml: str) -> list[str]:
    """Every legitimate rendering of a record's abstract text.

    Structured abstracts carry several AbstractText nodes with their section
    names in a `Label` attribute. Readers render those inline ("RESULTS: ...")
    and an excerpt copied from such a view carries the prefix — so one join
    keeps the labels. But **the space between two nodes does not exist in the
    source at all**; it is introduced by whoever concatenates them. An excerpt
    that legitimately spans two sections therefore matches the unlabelled join
    and not the labelled one.

    Returning both is not a loosening of the check. No word, figure or
    punctuation mark can differ under either form; only the join between two
    adjacent nodes does, and that join is this function's own invention.

    Found 2026-07-21, when the owner guides entered verification for the first
    time: four excerpts failed purely because they quoted across a section
    boundary, e.g. "Retrospective study.  38 cats with lymphoma." — DESIGN and
    ANIMALS in the record, with the label injection landing between them.
    """
    art = ET.fromstring(raw_xml)
    labelled, plain = [], []
    for t in art.iter("AbstractText"):
        body = "".join(t.itertext())
        label = t.get("Label")
        labelled.append(f"{label}: {body}" if label else body)
        plain.append(body)
    for t in art.iter("ArticleTitle"):
        title = "".join(t.itertext())
        labelled.append(title)
        plain.append(title)
    forms = [" ".join(labelled)]
    if plain != labelled:
        forms.append(" ".join(plain))
    return forms


def load_archive(arc: Path) -> tuple[dict[str, str], dict[str, list[str]]]:
    """Returns (admissible payloads, rejected pmid -> reasons).

    The gate runs HERE, not as a separate audit, so that a record which fails it
    is never available to excerpt verification at all. A gate that only reports
    is a gate standing next to an open door.
    """
    recs: dict[str, str] = {}
    rejected: dict[str, list[str]] = {}
    for f in sorted((arc / "records").glob("*.json")):
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except Exception as exc:
            rejected[f.stem] = [f"unreadable record ({type(exc).__name__})"]
            continue
        problems = gate_record(rec)
        if problems:
            rejected[rec.get("pmid", f.stem)] = problems
        else:
            recs[rec["pmid"]] = rec["raw_xml"]
    return recs, rejected


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

    archive, rejected = load_archive(arc)

    missing_records: list[str] = []
    unmatched: list[tuple[str, str, str]] = []
    checked = skipped_fulltext = 0

    for pmid, items in sorted(excerpts.items()):
        raw = archive.get(pmid)
        if raw is None:
            missing_records.append(pmid)
            continue
        hays = [norm(form) for form in abstract_of(raw)]
        for src_file, sentence, origin in items:
            if origin == "fulltext":
                # Correctly absent from the abstract; out of this leg's reach.
                skipped_fulltext += 1
                continue
            checked += 1
            needle = norm(sentence)
            if not any(needle in hay for hay in hays):
                unmatched.append((pmid, src_file, sentence))

    if verbose:
        for pmid, src, sent in unmatched:
            print(f"  UNMATCHED {pmid} ({src}): {sent[:100]}"
                  f"{'...' if len(sent) > 100 else ''}")
        for pmid in missing_records:
            print(f"  NO-RECORD {pmid}")
        for pmid, reasons in rejected.items():
            print(f"  GATE-REJECTED {pmid}: {'; '.join(reasons)}")

    detail = (f"{len(excerpts)} PMIDs, {checked} abstract-sourced excerpts checked, "
              f"{len(unmatched)} unmatched, {len(missing_records)} records missing, "
              f"{skipped_fulltext} full-text excerpts deferred to leg5")
    if rejected:
        detail += f", {len(rejected)} records rejected by the grade gate"
    # Findings are keyed by (pmid, what-was-found). A gate rejection is a finding
    # too — and a stronger one than an excerpt mismatch, since it stops the record
    # before it can be read as evidence at all. The self-test compares these sets,
    # so it must see both kinds or it will report a regression when a fault is
    # merely caught earlier than it used to be.
    keys = {(p, s) for p, _f, s in unmatched}
    keys |= {(p, f"<gate-rejected: {r[0]}>") for p, r in rejected.items() if r}
    if missing_records or unmatched or rejected:
        return "FAIL", detail, keys
    return "PASS", detail, keys


def cmd_leg1(args) -> int:
    arc = archive_dir(args.archive)
    verdict, detail, _ = leg1(arc, args.verbose)
    print(f"DR_LEG1: {verdict} ({detail})")
    return 0 if verdict == "PASS" else 1


# --- Leg 5: the excerpts Leg 1 structurally cannot reach -------------------
#
# Leg 1 compares against the archived PubMed **abstract**, so an excerpt taken
# from a full text is correctly absent from it and has always been skipped: 82
# of 908 excerpts, measured 2026-07-27 — the fraction of the corpus standing
# outside the discipline the project is built on. This leg closes that for every
# paper whose PDF is held, by comparing against `pdftotext` output archived by
# `fulltext_text.py`.
#
# ⚠️ Extraction is lossy in ways that are NOT the excerpt's fault, and pretending
# otherwise would produce exactly the false accusation this project is built to
# avoid. Two repairs, both observed live on the first run:
#   * words hyphenated across a line break rejoin;
#   * some publisher PDFs carry a broken font map — Baez 2007 extracts every "="
#     as "¼" (24 occurrences) and drops "±" entirely.
# A repaired match is reported as REPAIRED, never silently as a clean match, so
# the count of papers needing repair stays visible rather than becoming folklore.

PDF_REPAIRS = ((("¼", "="),), )      # (from, to) pairs applied only on retry


def norm_pdf(s: str) -> str:
    """Leg 1's `norm`, plus the de-hyphenation a page layout forces."""
    return norm(re.sub(r"-\s*\n\s*", "", s))


def alnum_only(s: str) -> str:
    """Last resort: letters and digits. Punctuation, symbols and spacing survive
    extraction unreliably; a changed word or digit still fails this."""
    return re.sub(r"[^0-9a-zÀ-ɏ]+", "", norm(s))


EXCEPTIONS_DOC = Path(__file__).resolve().parent.parent / "docs" / "kb-exceptions.md"
LEG5_EXCEPTION = re.compile(r'^-\s*leg5:\s*(\d{7,8})\s+"([^"]+)"\s*—')


def leg5_exceptions() -> list[tuple[str, str]]:
    """(pmid, normalised excerpt prefix) pairs from docs/kb-exceptions.md.

    ⚠️ **Every entry here is a claim that the EXTRACTOR failed, never that the
    excerpt is exempt from being right.** The four originals are inline
    superscript reference numbers glued into the sentence ("hypertensive
    cats,7,20,57,66,67 including…"), a figure caption inserted mid-sentence, and
    a two-column passage that both pdftotext modes shred. Adding a tolerance for
    any of those would mean ignoring digits inside a sentence — in a corpus whose
    whole point is that the digits are right. So the artefact is named, per
    excerpt, and counted in its own bucket rather than folded into a pass.

    Keyed on PMID **plus a prefix**, so an exception can never quietly cover a
    second excerpt of the same paper.
    """
    if not EXCEPTIONS_DOC.exists():
        return []
    out = []
    for line in EXCEPTIONS_DOC.read_text(encoding="utf-8").splitlines():
        m = LEG5_EXCEPTION.match(line.strip())
        if m:
            out.append((m.group(1), norm(m.group(2))))
    return out


def leg5(verbose: bool = False) -> tuple[str, str, set]:
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import fulltext_text
    except Exception as exc:                                  # pragma: no cover
        return "SKIP", f"fulltext_text unavailable ({exc})", set()

    excerpts = excerpts_from_kb()
    exceptions = leg5_exceptions()
    exact = repaired = lossy = excepted = 0
    unreachable: set[str] = set()
    unmatched: list[tuple[str, str, str]] = []
    unused_exceptions = set(exceptions)

    for pmid, items in sorted(excerpts.items()):
        rows = [(f, s) for f, s, o in items if o == "fulltext"]
        if not rows:
            continue
        bodies = fulltext_text.load_texts(pmid)
        if not bodies:
            unreachable.add(pmid)
            continue
        hay = [norm_pdf(b) for b in bodies]
        forms = [functools.reduce(lambda t, kv: t.replace(*kv), pairs, b)
                 for b in bodies for pairs in PDF_REPAIRS]
        hay_repaired = [norm_pdf(f) for f in forms]
        # The repairs must reach the fallback too, or a document needing one is
        # denied both routes: NFKC expands "¼" to "1⁄4", so the stray digits
        # survive into the alphanumeric form and corrupt it there as well.
        hay_alnum = [alnum_only(t) for t in bodies + forms]
        for src_file, sentence in rows:
            needle = norm(sentence)
            if any(needle in h for h in hay):
                exact += 1
            elif any(needle in h for h in hay_repaired):
                repaired += 1
            elif any(alnum_only(sentence) in h for h in hay_alnum):
                lossy += 1
            else:
                hit = [e for e in exceptions
                       if e[0] == pmid and needle.startswith(e[1])]
                if hit:
                    excepted += 1
                    unused_exceptions.discard(hit[0])
                else:
                    unmatched.append((pmid, src_file, sentence))

    if verbose:
        for pmid, src, sent in unmatched:
            print(f"  UNMATCHED {pmid} ({src}): {sent[:110]}"
                  f"{'...' if len(sent) > 110 else ''}")
        for pmid in sorted(unreachable):
            print(f"  NO-FULLTEXT {pmid} (PDF not held; run fetch_fulltext.py)")

    # ⚠️ A stale exception is a dead hatch pointing the other way: it says a
    # problem is known when it no longer exists, and the next real one inherits
    # the excuse. Report it rather than letting the list rot silently.
    if verbose:
        for pmid, prefix in sorted(unused_exceptions):
            print(f"  STALE-EXCEPTION {pmid}: no longer matches anything — remove it")

    total = exact + repaired + lossy + excepted + len(unmatched)
    detail = (f"{total} full-text excerpts checked, {exact} exact, "
              f"{repaired} matched after repairing a known PDF font artefact, "
              f"{lossy} matched modulo lossy punctuation, "
              f"{excepted} excepted as extraction artefacts, "
              f"{len(unmatched)} unmatched; "
              f"{len(unreachable)} paper(s) still have no held PDF, "
              f"{len(unused_exceptions)} stale exception(s)")
    keys = {(p, s) for p, _f, s in unmatched}
    return ("FAIL" if unmatched else "PASS"), detail, keys


def cmd_leg5(args) -> int:
    verdict, detail, _ = leg5(args.verbose)
    print(f"DR_LEG5: {verdict} ({detail})")
    return 0 if verdict in ("PASS", "SKIP") else 1


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


def _hash_tree(records: Path) -> dict[str, str]:
    """sha256 of each record FILE as it sits on disk — not the stored hash field,
    which would be self-confirming. This is what proves bytes were reused rather
    than rewritten."""
    import hashlib
    return {f.name: hashlib.sha256(f.read_bytes()).hexdigest()
            for f in sorted(records.glob("*.json"))}


def _broken_records(records: Path) -> list[str]:
    """Records that do not parse or lack their payload — what a crash mid-write
    leaves behind, and what a resume must never silently accept as done."""
    bad = []
    for f in sorted(records.glob("*.json")):
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
            if not rec.get("raw_xml") or not rec.get("sha256"):
                bad.append(f.name)
        except Exception:
            bad.append(f.name)
    return bad


def cmd_leg2(args) -> int:
    """Leg 2 — crash resume.

    Kill a fetch mid-flight, re-dispatch the identical command, and assert it
    resumes from its checkpoint rather than starting over, reusing already-written
    records byte for byte.

    ⚠️ Controlled kill -9, never a real reboot: the node this pipeline targets has
    an unresolved crash history, so rebooting to test crash-recovery risks
    triggering the very fault, and the resume path exercised is identical.

    ⚠️ The crash window is made by increasing the number of round trips (small
    --batch), not by inserting delays. The sibling project's drill initially
    tested nothing because the work finished before the killer fired; padding with
    sleeps would only have measured the sleep.
    """
    import subprocess
    import time

    tool = Path(__file__).resolve().parent / "pubmed_archive.py"
    total = args.count

    with tempfile.TemporaryDirectory() as tmp:
        scratch = Path(tmp) / "arc"
        records = scratch / "records"
        cmd = [sys.executable, str(tool), "fetch", "--archive", str(scratch),
               "--batch", str(args.batch), "--limit", str(total)]

        # --- run 1: kill it mid-flight -------------------------------------
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.time() + args.timeout
        killed_at = None
        while time.time() < deadline:
            n = len(list(records.glob("*.json"))) if records.is_dir() else 0
            if n >= args.batch and n < total:      # at least one batch landed, not all
                proc.kill()
                killed_at = n
                break
            if proc.poll() is not None:            # finished before we could cut in
                break
            time.sleep(0.05)
        proc.wait()

        if killed_at is None:
            n = len(list(records.glob("*.json"))) if records.is_dir() else 0
            print(f"DR_LEG2: SKIP (no crash window: fetch reached {n}/{total} before "
                  f"it could be killed — lower --batch or raise --count)")
            return 0

        before = _hash_tree(records)
        broken_before = _broken_records(records)

        # --- run 2: identical command, must resume -------------------------
        # In --self-test the second run is deliberately given --force, which makes
        # it refetch everything. That is exactly the fault this leg exists to
        # catch, so the leg must FAIL on it; a leg that passes here detects
        # nothing. Leg 1 taught this lesson the hard way.
        cmd2 = cmd + (["--force"] if args.self_test else [])
        r2 = subprocess.run(cmd2, capture_output=True, text=True)
        stdout = r2.stdout.strip()
        m = re.search(r"(\d+) PMIDs requested, (\d+) to fetch", stdout)
        after = _hash_tree(records)
        broken_after = _broken_records(records)

        failures = []
        # (a) resumed rather than restarted
        if m:
            to_fetch = int(m.group(2))
            if to_fetch >= total:
                failures.append(f"restarted from zero ({to_fetch}/{total} to fetch)")
        else:
            failures.append("could not parse resume report from run 2")
        # (b) previously written records reused byte for byte
        rewritten = [k for k, v in before.items() if after.get(k) != v]
        if rewritten:
            failures.append(f"{len(rewritten)} record(s) rewritten, not reused: "
                            f"{', '.join(rewritten[:3])}")
        # (c) completed
        if len(after) != total:
            failures.append(f"incomplete after resume: {len(after)}/{total}")
        # (d) no corruption survived — a truncated record must not pass as done
        new_broken = set(broken_after) - set(broken_before)
        if broken_after:
            failures.append(f"{len(broken_after)} unreadable record(s) after resume: "
                            f"{', '.join(broken_after[:3])}")

        detail = (f"killed after {killed_at}/{total} records, resumed "
                  f"{to_fetch if m else '?'} remaining, {len(before)} carried over "
                  f"byte-identical, {len(after)}/{total} final")
        if broken_before:
            detail += f", {len(broken_before)} truncated by the kill"
        if args.self_test:
            if failures:
                print(f"DR_LEG2_SELFTEST: PASS (a non-resuming fetch was detected: "
                      f"{'; '.join(failures)})")
                return 0
            print(f"DR_LEG2_SELFTEST: FAIL (a forced full refetch went UNDETECTED — "
                  f"this leg proves nothing) [{detail}]", file=sys.stderr)
            return 1
        if failures:
            print(f"DR_LEG2: FAIL ({'; '.join(failures)}) [{detail}]", file=sys.stderr)
            return 1
        print(f"DR_LEG2: PASS ({detail})")
        return 0


FAKE_SUMMARY = ("This retrospective study of 250 cats found that most were "
                "euthanised at presentation, though some survived beyond a year.")


def _attacks(rec: dict) -> list[tuple[str, dict]]:
    """Ways a model-authored artefact could come to occupy a raw payload's place.

    Each returns a mutated record that MUST be refused. They escalate: the first
    is a careless substitution, the last is a deliberate forgery that satisfies
    every check except provenance and integrity. The point of the ladder is that
    no single check catches all of them.
    """
    import copy
    out = []

    # 1. Blunt substitution: prose dropped into the payload field.
    a = copy.deepcopy(rec); a["raw_xml"] = FAKE_SUMMARY
    out.append(("prose in place of payload", a))

    # 2. Same, but the hash is updated so integrity alone would pass.
    import hashlib
    b = copy.deepcopy(rec); b["raw_xml"] = FAKE_SUMMARY
    b["sha256"] = hashlib.sha256(FAKE_SUMMARY.encode()).hexdigest()
    out.append(("prose with a recomputed hash", b))

    # 3. Well-formed XML, but not a PubMed record — fabrication that parses.
    c = copy.deepcopy(rec)
    c["raw_xml"] = f"<Summary><Text>{FAKE_SUMMARY}</Text></Summary>"
    c["sha256"] = hashlib.sha256(c["raw_xml"].encode()).hexdigest()
    out.append(("well-formed XML that is not a PubmedArticle", c))

    # 4. A genuine record relabelled as another paper's — right bytes, wrong claim.
    d = copy.deepcopy(rec); d["pmid"] = "99999999"
    out.append(("payload attributed to the wrong PMID", d))

    # 5. Grade downgraded but content left alone: an honest hint that must still
    #    never reach the excerpt path.
    e = copy.deepcopy(rec); e["grade"] = "local_relevance_hint"
    out.append(("record self-declared as a local hint", e))

    # 6. Hint text merged into the payload — the boundary erased rather than crossed.
    f = copy.deepcopy(rec)
    f["local_relevance_note"] = FAKE_SUMMARY
    f["raw_xml"] = rec["raw_xml"].replace("<Abstract>", f"<Abstract>{FAKE_SUMMARY}", 1) \
        if "<Abstract>" in rec["raw_xml"] else rec["raw_xml"] + FAKE_SUMMARY
    f["sha256"] = hashlib.sha256(f["raw_xml"].encode()).hexdigest()
    out.append(("hint text merged into the payload", f))

    return out


def cmd_leg4(args) -> int:
    """Leg 4 — grade enforcement.

    Inject artefacts that a local model could plausibly have produced into the
    position a raw payload occupies, and assert every one is refused.

    This leg guards the project's core asset. `## 原文摘录` is trusted as evidence
    precisely because nothing but a fetched payload can reach it; if that stops
    being true, every downstream verification is checking a paraphrase while
    reporting that it checked a source.
    """
    arc = archive_dir(args.archive)
    records_dir = arc / "records"
    if not records_dir.is_dir():
        print(f"DR_LEG4: SKIP (no archive at {arc})")
        return 0

    # Use a record that Leg 1 actually verifies, so admission would be consequential.
    excerpts = excerpts_from_kb()
    sample = None
    for pmid in sorted(excerpts):
        f = records_dir / f"{pmid}.json"
        if f.exists():
            rec = json.loads(f.read_text(encoding="utf-8"))
            if not gate_record(rec):
                sample = rec
                break
    if sample is None:
        print("DR_LEG4: SKIP (no admissible record to build attacks from)")
        return 0

    # Control: the untouched record must pass, or the leg proves nothing by
    # rejecting everything.
    if gate_record(sample):
        print(f"DR_LEG4: FAIL (control record {sample['pmid']} was itself rejected)",
              file=sys.stderr)
        return 1

    admitted = []
    for name, mutated in _attacks(sample):
        problems = gate_record(mutated)
        if not problems:
            admitted.append(name)
        elif args.verbose:
            print(f"  refused [{name}]: {problems[0]}")

    total = len(_attacks(sample))
    if admitted:
        print(f"DR_LEG4: FAIL ({len(admitted)}/{total} forged artefacts ADMITTED as "
              f"verbatim source: {'; '.join(admitted)})", file=sys.stderr)
        return 1
    print(f"DR_LEG4: PASS (control admitted; {total}/{total} forged artefacts refused, "
          f"built from PMID {sample['pmid']})")
    return 0


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
    p3 = sub.add_parser("leg2")
    p3.add_argument("--count", type=int, default=24, help="records to fetch in the drill")
    p3.add_argument("--batch", type=int, default=4, help="records per request; smaller = wider crash window")
    p3.add_argument("--timeout", type=float, default=120.0)
    p3.add_argument("--self-test", action="store_true",
                    help="prove this leg detects a fetch that does NOT resume")
    p4 = sub.add_parser("leg4")
    p4.add_argument("--archive")
    p4.add_argument("-v", "--verbose", action="store_true")
    p4.set_defaults(fn=cmd_leg4)
    p5 = sub.add_parser("leg5")
    p5.add_argument("-v", "--verbose", action="store_true")
    p5.set_defaults(fn=cmd_leg5)
    p3.set_defaults(fn=cmd_leg2)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())


# ── Attribution cross-check ────────────────────────────────────────────────
# extract_source_excerpts.py assigns figures to citations BY SENTENCE, so a
# sentence carrying two citations files one paper's numbers under the other and
# reports them as unverified. Four such false positives were confirmed by hand
# on 2026-07-20 (85/2024, 123, 412, 27).
#
# ⚠️ This check only RAISES SUSPICION. Its first run flagged 14 candidates, of
# which most were coincidence: common values like 10, 21, 30 and 50 appear in
# many abstracts for unrelated reasons. Written up as a lesson in its own right —
# the checker committed the error class it exists to detect, treating
# co-occurrence as attribution. Confirm each hit against the body sentence before
# acting; never bulk-clear on its output.
def suspect_misattribution(kb_dir=None):
    import glob as _glob
    kb = Path(kb_dir) if kb_dir else None
    year = re.compile(r"^(19|20)\d\d$")
    out = []
    for f in (sorted(kb.glob("*.md")) if kb else corpus_files()):
        text = f.read_text(encoding="utf-8")
        if "## 原文摘录" not in text:
            continue
        blocks = re.split(r"\*\*PMID (\d+)\*\*", text.split("## 原文摘录", 1)[1])
        owner = {blocks[i]: blocks[i + 1] for i in range(1, len(blocks), 2)}
        for pmid, body in owner.items():
            g = re.search(r"The figures? `([^`]+)`", body)
            if not g:
                continue
            for n in (x.strip() for x in g.group(1).split(",")):
                if year.match(n) or len(n) > 7:
                    continue
                other = [p for p, b in owner.items()
                         if p != pmid and re.search(r"\b" + re.escape(n) + r"\b", b)]
                if other:
                    out.append((f.name, pmid, n, other))
    return out
