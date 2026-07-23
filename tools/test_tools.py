#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for the three tools that shipped without a safety net.

`dr_drill.py` has had a self-test since it was written: it corrupts a record on
purpose and asserts the checker notices. The other tools had nothing, and two of
them have already shipped real defects into the repository:

  * `check_kb_hygiene.check_orphans()` was originally PER-FILE. It reported
    PMID 31836868 and 38825481 as unverified while both were excerpted in a
    neighbouring file and passing Leg 1 all along — a checker mistaking
    "not here" for "nowhere".
  * `attribution_candidates` treats co-occurrence as attribution. Its first run
    produced 654 "unique" matches dominated by coincidences on values like 50
    and 100 appearing in some unrelated abstract.

Both of those shapes are encoded below as regression tests and say so in their
docstrings, so a future reader knows they are history rather than hypothesis.

Everything here builds its own synthetic Markdown in a temporary directory. It
does NOT read the real corpus: those files change every session, and a test that
读 them fails for reasons that have nothing to do with the code under test. It
needs no network and no PubMed archive.

Usage:
  python3 tools/test_tools.py [-v]
Standard library only (unittest). No pytest, no new dependencies.
"""
from __future__ import annotations

import contextlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import attribution_candidates as attrib   # noqa: E402
import build_site                          # noqa: E402
import check_kb_hygiene as hygiene         # noqa: E402


# --------------------------------------------------------------- test scaffolding
#
# NOTE ON GLOBAL PATHS — deliberately worked around, not refactored away.
# `check_kb_hygiene` resolves its inputs through module globals: `kb_files()`
# delegates to `pubmed_archive.corpus_files()` (the real knowledge-base and
# guides directories) and `load_exceptions()` reads the module constant
# `EXCEPTIONS`. Neither takes an argument, so the only way to point them at a
# fixture is to rebind the module attribute for the duration of a test. That is
# what `_patched()` does. The alternative — threading a path parameter through
# the tool — would change tool behaviour, which these tests exist to protect.

@contextlib.contextmanager
def _patched(module, **attrs):
    """Temporarily rebind module attributes; restore them whatever happens."""
    old = {k: getattr(module, k) for k in attrs}
    for k, v in attrs.items():
        setattr(module, k, v)
    try:
        yield
    finally:
        for k, v in old.items():
            setattr(module, k, v)


class Fixture(unittest.TestCase):
    """Base class giving each test a private temporary directory."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def write(self, name: str, text: str) -> Path:
        p = self.dir / name
        p.write_text(text, encoding="utf-8")
        return p


# =============================================================================
# check_kb_hygiene.py — citation extraction
# =============================================================================

class TestCitedPmids(Fixture):

    def test_prose_form(self):
        """Catches a regex that stops recognising `PMID 12345678` in body prose."""
        self.assertEqual(hygiene.cited_pmids("The median was 12 months (PMID 28245741)."),
                         {"28245741"})

    def test_index_form(self):
        """Catches loss of the `(12345678, descriptor)` per-topic index form."""
        line = "- 高血压视网膜病变 (33512084, prevalence study)"
        self.assertEqual(hygiene.cited_pmids(line), {"33512084"})

    def test_both_forms_together(self):
        """Catches an extractor that finds one citation form and stops.

        This is the same failure the repository documented in kb-exceptions.md:
        grepping for the citation form you expect, then reporting the absence of
        that form as the absence of attribution."""
        text = ("Prose cites PMID 28245741 directly.\n"
                "- index line (33512084, cohort)\n")
        self.assertEqual(hygiene.cited_pmids(text), {"28245741", "33512084"})

    def test_index_form_ignores_short_numbers(self):
        """Catches a widened index regex swallowing ordinary parenthesised numbers.

        `(21, 2)` in a table cell is not a citation; only 7-8 digit ids are."""
        self.assertEqual(hygiene.cited_pmids("survival (21, 2) and (123456, x)"), set())

    def test_no_citations_is_empty(self):
        """Catches an extractor that invents citations from bare digits."""
        self.assertEqual(hygiene.cited_pmids("225 cats, 58.6% abnormal fundus."), set())


class TestExcerptBlocks(Fixture):

    def test_parses_pmid_and_quoted_lines(self):
        """Catches a block parser that loses the PMID or drops quoted lines."""
        tail = ("\n\n**PMID 28245741** · Taylor SS 2017\n"
                "> First quoted sentence.\n"
                "> Second quoted sentence.\n")
        self.assertEqual(hygiene.excerpt_blocks(tail),
                         [("28245741", ["> First quoted sentence.",
                                        "> Second quoted sentence."])])

    def test_stops_at_the_next_block(self):
        """Catches a greedy parser that merges two records' excerpts into one."""
        tail = ("**PMID 111111** · A 2020\n> quote A\n"
                "\n"
                "**PMID 222222** · B 2021\n> quote B\n")
        blocks = hygiene.excerpt_blocks(tail)
        self.assertEqual([p for p, _ in blocks], ["111111", "222222"])
        self.assertEqual(blocks[0][1], ["> quote A"])
        self.assertEqual(blocks[1][1], ["> quote B"])

    def test_stops_at_a_non_quote_line(self):
        """Catches a parser that absorbs ordinary prose as if it were quoted source."""
        tail = ("**PMID 333333** · C 2022\n> quote C\n"
                "This paragraph is commentary, not source text.\n")
        self.assertEqual(hygiene.excerpt_blocks(tail), [("333333", ["> quote C"])])

    def test_split_sections_divides_head_from_excerpts(self):
        """Catches a split that leaks excerpt text into the 'cited' half.

        If it did, every excerpted PMID would look 'cited' and orphan detection
        would go permanently silent."""
        head, tail = hygiene.split_sections(
            "# Doc\nBody cites PMID 111111.\n\n## 原文摘录\n\n**PMID 222222**\n> q\n")
        self.assertIn("PMID 111111", head)
        self.assertNotIn("222222", head)
        self.assertIn("222222", tail)


# =============================================================================
# check_kb_hygiene.py — orphan detection (repo-wide)
# =============================================================================

class TestOrphans(Fixture):

    def _files(self, *pairs):
        return [self.write(n, t) for n, t in pairs]

    def test_cross_file_excerpt_is_not_an_orphan(self):
        """REGRESSION (real bug, July 2026): orphan detection must be REPO-WIDE.

        The first version of check_orphans() was per-file and reported
        PMID 31836868 and 38825481 as unverified when both were excerpted in a
        neighbouring file and had been passing Leg 1 all along. Files legitimately
        cross-cite; Leg 1 verifies an excerpt wherever it lives. If this test ever
        fails, the checker has gone back to mistaking 'not here' for 'nowhere'."""
        files = self._files(
            ("claims.md", "# Claims\nSurvival rests on PMID 31836868.\n"),
            ("sources.md", "# Sources\n\n## 原文摘录\n\n"
                           "**PMID 31836868** · Evangelista 2019\n"
                           "> A quoted sentence from the abstract.\n"),
        )
        with _patched(hygiene, kb_files=lambda: files):
            self.assertEqual(hygiene.check_orphans(set()), [])

    def test_pmid_excerpted_nowhere_is_reported(self):
        """Catches the opposite failure: a repo-wide check that never fails.

        Companion to the regression test above — a checker made silent to stop
        false positives is worse than the false positives."""
        files = self._files(
            ("claims.md", "# Claims\nA claim rests on PMID 99999999.\n"),
            ("sources.md", "# Sources\n\n## 原文摘录\n\n"
                           "**PMID 31836868** · Evangelista 2019\n> quoted.\n"),
        )
        with _patched(hygiene, kb_files=lambda: files):
            problems = hygiene.check_orphans(set())
        self.assertEqual(len(problems), 1)
        self.assertIn("99999999", problems[0])
        self.assertIn("claims.md", problems[0])

    def test_index_line_citation_counts_as_a_citation(self):
        """Catches orphans going unreported when the only citation is an index line."""
        files = self._files(
            ("index.md", "# Index\n- topic (99999999, cohort)\n"),
        )
        with _patched(hygiene, kb_files=lambda: files):
            problems = hygiene.check_orphans(set())
        self.assertEqual(len(problems), 1)
        self.assertIn("99999999", problems[0])

    def test_exception_suppresses_the_report(self):
        """Catches an exceptions set that is parsed but never consulted.

        docs/kb-exceptions.md is the repository's only reviewable way to say
        'this identifier is not a source'; if it stopped working, contributors
        would silence checks some other, invisible way."""
        files = self._files(("claims.md", "# Claims\nSee PMID 17552367.\n"))
        with _patched(hygiene, kb_files=lambda: files):
            self.assertEqual(hygiene.check_orphans({"17552367"}), [])

    def test_citation_inside_the_excerpt_section_is_not_a_citation(self):
        """Catches a check that treats quoted source text as if it were a claim.

        Excerpts routinely mention other PMIDs; those are part of the quoted
        record, not this repository citing them."""
        files = self._files(
            ("doc.md", "# Doc\n\n## 原文摘录\n\n"
                       "**PMID 31836868** · E 2019\n"
                       "> The authors compare with PMID 99999999 in their discussion.\n"),
        )
        with _patched(hygiene, kb_files=lambda: files):
            self.assertEqual(hygiene.check_orphans(set()), [])


# =============================================================================
# check_kb_hygiene.py — empty excerpt blocks
# =============================================================================

class TestEmptyBlocks(Fixture):

    def _check(self, text, exc=frozenset()):
        f = self.write("doc.md", text)
        with _patched(hygiene, kb_files=lambda: [f]):
            return hygiene.check_empty_blocks(set(exc))

    def test_annotation_only_block_is_flagged(self):
        """Catches the 'verified-looking paper that verifies nothing' defect.

        A block holding only `> ⚠️` annotation increments Leg 1's PMID count and
        not its excerpt count. Five existed; four had body claims resting on them."""
        problems = self._check("# Doc\n\n## 原文摘录\n\n"
                               "**PMID 28245741** · Taylor 2017\n"
                               "> ⚠️ Abstract could not be retrieved.\n")
        self.assertEqual(len(problems), 1)
        self.assertIn("28245741", problems[0])

    def test_declared_missing_source_is_accepted(self):
        """Catches loss of the documented escape hatch for records with no abstract.

        The phrase 'no source text available' is a written declaration that
        nothing rests on the block; it must keep suppressing the finding."""
        self.assertEqual(
            self._check("# Doc\n\n## 原文摘录\n\n"
                        "**PMID 28245741** · Taylor 2017\n"
                        "> ⚠️ no source text available for this record.\n"),
            [])

    def test_declared_missing_source_is_case_insensitive(self):
        """Catches a case-sensitive marker match rejecting 'No source text available'."""
        self.assertEqual(
            self._check("# Doc\n\n## 原文摘录\n\n"
                        "**PMID 28245741** · Taylor 2017\n"
                        "> ⚠️ No Source Text Available — abstract-less record.\n"),
            [])

    def test_block_with_real_quotes_is_not_flagged(self):
        """Catches a false positive that would flag every properly excerpted paper."""
        self.assertEqual(
            self._check("# Doc\n\n## 原文摘录\n\n"
                        "**PMID 28245741** · Taylor 2017\n"
                        "> ⚠️ Partial record.\n"
                        "> A genuinely quoted sentence from the abstract.\n"),
            [])

    def test_exception_suppresses_the_report(self):
        """Catches empty-block exceptions being parsed but ignored."""
        self.assertEqual(
            self._check("# Doc\n\n## 原文摘录\n\n"
                        "**PMID 28245741** · Taylor 2017\n"
                        "> ⚠️ Abstract could not be retrieved.\n",
                        exc={"28245741"}),
            [])


# =============================================================================
# check_kb_hygiene.py — exceptions file
# =============================================================================

class TestLoadExceptions(Fixture):

    def _load(self, text):
        f = self.write("kb-exceptions.md", text)
        with _patched(hygiene, EXCEPTIONS=f):
            return hygiene.load_exceptions()

    def test_parses_the_documented_line_format(self):
        """Catches a parser change that silently drops every exception.

        Exceptions would stop suppressing anything and CI would go red for
        defects that were reviewed and accepted."""
        exc = self._load(
            "# Knowledge-base check exceptions\n\n"
            "## orphans\n\n"
            "- orphans: 17552367 — Not a source. A transcription error kept as evidence.\n"
            "- empty-blocks: 28245741 — abstract-less record, nothing rests on it\n")
        self.assertEqual(exc["orphans"], {"17552367"})
        self.assertEqual(exc["empty-blocks"], {"28245741"})
        self.assertEqual(exc["coverage"], set())
        self.assertEqual(exc["pii"], set())

    def test_prose_and_headings_are_not_parsed_as_exceptions(self):
        """Catches an over-eager parser turning documentation into suppressions.

        kb-exceptions.md is mostly prose explaining each entry; a parser that
        matched loosely could suppress checks nobody asked to suppress."""
        exc = self._load(
            "Valid check names: `orphans`, `empty-blocks`, `pii`.\n"
            "Normally this means the paper was never archived (orphans: see SOP).\n"
            "- orphans: 17552367 — real entry\n")
        self.assertEqual(exc["orphans"], {"17552367"})

    def test_missing_file_yields_empty_sets_not_a_crash(self):
        """Catches a checker that dies on a repo with no exceptions file yet."""
        with _patched(hygiene, EXCEPTIONS=self.dir / "does-not-exist.md"):
            exc = hygiene.load_exceptions()
        # Derived, not hard-coded: a literal set here would have to be edited
        # every time a check is added, and the version that was hard-coded is
        # what let four checks ship with dead suppression hatches.
        self.assertEqual(set(exc), set(hygiene.CHECK_NAMES))
        self.assertTrue(all(v == set() for v in exc.values()))

    def test_stale_pdf_exception_actually_suppresses(self):
        """REGRESSION, fixed 2026-07-21. This test previously asserted the
        OPPOSITE — it documented that a `- stale-pdf:` line parsed to nothing
        while check_stale_pdf's own failure message instructed users to write
        exactly that. The hatch is now real; the assertion is inverted to keep
        it that way."""
        exc = self._load("- stale-pdf: feline-ckd-owner-guide.zh.md — rebuilt next release\n")
        self.assertEqual(exc["stale-pdf"], {"feline-ckd-owner-guide.zh.md"})


# =============================================================================
# attribution_candidates.py — body extraction
# =============================================================================

class TestBodyOf(Fixture):

    def test_strips_appendix_b(self):
        """Catches reference-appendix figures leaking into the review list.

        Every reference line contains a year, a volume and a page range; if the
        appendix survived, the candidate list would be mostly bibliography."""
        body = attrib.body_of("Prose says 68%.\n\n## 附录 B 参考文献\n\n1. Foo 2019;21:455-461.\n")
        self.assertIn("68%", body)
        self.assertNotIn("455", body)

    def test_strips_references_heading(self):
        """Catches `## 参考文献` no longer terminating the body."""
        body = attrib.body_of("Prose says 68%.\n\n## 参考文献\n\n1. Bar 2020;12:33-40.\n")
        self.assertNotIn("33-40", body)

    def test_strips_excerpt_section(self):
        """Catches quoted source text being mined for figures to attribute.

        Excerpts are verbatim source; their numbers already belong to a known
        PMID and must never enter the attribution queue."""
        body = attrib.body_of("Prose says 68%.\n\n## 原文摘录\n\n**PMID 1** \n> 225 cats.\n")
        self.assertNotIn("225", body)

    def test_earliest_heading_wins_regardless_of_order(self):
        """Catches a splitter that only honours whichever heading it checks first."""
        md = "Body 68%.\n\n## 原文摘录\n> 225 cats.\n\n## 参考文献\n1. Foo 2019;21:455.\n"
        body = attrib.body_of(md)
        self.assertNotIn("225", body)
        self.assertNotIn("455", body)

    def test_document_without_any_stop_heading_is_kept_whole(self):
        """Catches a splitter that truncates documents having no appendix."""
        md = "# Guide\n\nProse says 68% and 12.5 months.\n"
        self.assertEqual(attrib.body_of(md), md)


# =============================================================================
# attribution_candidates.py — figure extraction
# =============================================================================

class TestFiguresIn(Fixture):

    def figs(self, text, min_len=2):
        return [f for _, f, _ in attrib.figures_in(text, min_len)]

    def test_skips_fenced_code_blocks(self):
        """Catches the ASCII survival-range diagram flooding the candidate list.

        The guides contain fenced diagrams full of numbers that are layout, not
        claims; each one would arrive as a figure a human must adjudicate."""
        text = ("Median survival was 12 months.\n"
                "```\n"
                "0----30----60----90 days\n"
                "```\n"
                "Remission rate 68%.\n")
        self.assertEqual(self.figs(text), ["12", "68%"])

    def test_code_fence_toggles_back_off(self):
        """Catches a one-way fence flag that discards the entire rest of the file."""
        text = "```\n99\n```\nAfter the fence: 68%.\n```\n77\n```\nEnd: 45.\n"
        self.assertEqual(self.figs(text), ["68%", "45"])

    def test_skips_bare_years(self):
        """REGRESSION-ADJACENT (real bug, July 2026): years are not figures.

        The first run produced 654 'unique' matches dominated by coincidences.
        Years are the worst offenders — every abstract carries several, so a
        year in prose matches almost any record and manufactures attributions."""
        self.assertEqual(self.figs("Sfiligoi 2007 and Goto 2022 reported 68%."), ["68%"])

    def test_year_boundaries_1990_and_2035(self):
        """Catches a narrowed year filter letting 1990s and 2030s dates through."""
        self.assertEqual(self.figs("In 1990, in 2035, in 1899, in 2101."),
                         ["1899", "2101"])

    def test_year_shaped_quantities_are_dropped_even_when_not_years(self):
        """DOCUMENTS A DEFECT, does not endorse it — see the report for this suite.

        YEARISH is tested against the figure with `%` already stripped, so the
        year filter also eats genuine quantities whose digits happen to fall in
        1990-2035: a cohort of `2000` cats, a dose of `2000` mg, an implausible
        `2020%`. These vanish from the review queue silently, which is the
        quieter half of the same judgement the tool is meant to hand to a human.

        If this test starts failing, the defect was fixed: delete the test."""
        self.assertEqual(self.figs("An implausible 2020% increase."), [])
        self.assertEqual(self.figs("A cohort of 2000 cats received 1995 mg."), [])
        # Just outside the window, the same quantities survive — so the loss is
        # a property of the value's digits, not of anything about the sentence.
        self.assertEqual(self.figs("A cohort of 2100 cats."), ["2100"])

    def test_min_len_threshold_is_respected(self):
        """Catches single digits (list markers, chapter numbers) returning as figures."""
        text = "Stage 3 disease, 12 months, 12.5 weeks.\n"
        self.assertEqual(self.figs(text, min_len=2), ["12", "12.5"])
        self.assertEqual(self.figs(text, min_len=3), ["12.5"])

    def test_min_len_counts_digits_across_the_decimal_point(self):
        """Pins that `8.5` counts as two digits, not three.

        The threshold measures digits of precision, not character width, so a
        one-decimal value needs min_len 2 to survive. Catches a change that
        starts counting the separator and silently raises the threshold."""
        self.assertEqual(self.figs("Median 8.5 weeks.", min_len=2), ["8.5"])
        self.assertEqual(self.figs("Median 8.5 weeks.", min_len=3), [])

    def test_min_len_counts_digits_not_punctuation(self):
        """Catches a threshold that counts separators, so `1,825` looks 5 digits long."""
        self.assertEqual(self.figs("A cohort of 1,825 cats.", min_len=4), ["1,825"])
        self.assertEqual(self.figs("A cohort of 1,825 cats.", min_len=5), [])

    def test_keeps_decimals_and_percentages_intact(self):
        """Catches a tokeniser that splits 58.6% into 58 and 6, destroying the match."""
        self.assertEqual(self.figs("Prevalence was 58.6% overall."), ["58.6%"])

    def test_skips_table_rules_and_warning_lines(self):
        """Catches Markdown table separators and ⚠️ annotations entering the queue."""
        text = "|---|---:|---|\n> ⚠️ 出处待核 12 个月\nBody figure 68%.\n"
        self.assertEqual(self.figs(text), ["68%"])

    def test_line_numbers_are_one_based_and_real(self):
        """Catches off-by-one line numbers, which make a review list unusable."""
        text = "line one\nline two has 68%\n"
        self.assertEqual(attrib.figures_in(text, 2)[0][0], 2)

    def test_inline_pmids_are_returned_as_figures(self):
        """DOCUMENTS A DEFECT, does not endorse it — see the report for this suite.

        The July 2026 retrofit added 62 inline `PMID nnnnnnnn` citations to the
        guides. figures_in() has no PMID exclusion, so each one now returns as
        an 8-digit 'figure' needing attribution — the tool generating review work
        out of the citations it exists to add. They land in UNMATCHED (a PMID is
        not printed inside its own abstract), so it is noise rather than a false
        attribution, but it is noise proportional to progress.

        If this test starts failing, the defect was fixed: delete the test."""
        self.assertIn("17451991", self.figs("依据 PMID 17451991，中位生存期 12 个月。"))


# =============================================================================
# build_site.py
# =============================================================================

class TestFirstHeading(Fixture):

    def test_returns_the_first_h1(self):
        """Catches every site page falling back to its filename as a title."""
        self.assertEqual(build_site.first_heading("# 猫慢性肾病（CKD）\n\nBody.\n", "fb"),
                         "猫慢性肾病（CKD）")

    def test_ignores_h2_and_deeper(self):
        """Catches a section heading being promoted to the page title."""
        self.assertEqual(build_site.first_heading("## 第 0 章\n\n# Real Title\n", "fb"),
                         "Real Title")

    def test_falls_back_when_there_is_no_heading(self):
        """Catches a crash (or an empty <title>) on a document with no `# ` line."""
        self.assertEqual(build_site.first_heading("No heading at all.\n", "fallback"),
                         "fallback")

    def test_takes_the_first_of_several(self):
        """Catches a last-match search retitling pages with a trailing heading."""
        self.assertEqual(build_site.first_heading("# First\n\n# Second\n", "fb"), "First")

    def test_strips_trailing_whitespace(self):
        """Catches ragged <title> text from Markdown written with trailing spaces."""
        self.assertEqual(build_site.first_heading("#   Padded Title   \n", "fb"),
                         "Padded Title")


class TestPage(Fixture):

    def test_every_page_carries_the_disclaimer(self):
        """SAFETY: a page without the disclaimer is a defect, not a cosmetic miss.

        Readers arrive from search engines in the middle of a document, so a
        warning that exists only on the index is not a warning. This asserts the
        full block, including the emergency instruction to contact a vet first."""
        out = build_site.page("T", "<p>body</p>")
        self.assertIn(build_site.DISCLAIMER, out)
        self.assertIn("这不是医疗建议", out)
        self.assertIn("请立刻联系兽医", out)

    def test_index_page_also_carries_the_disclaimer(self):
        """SAFETY: `nav=False` must drop the navbar only, never the warning."""
        out = build_site.page("catmed", "<p>index</p>", nav=False)
        self.assertIn(build_site.DISCLAIMER, out)
        self.assertNotIn('class="sitenav"', out)

    def test_viewport_meta_tag_is_present(self):
        """Catches a desktop-width page on a phone, which is how owners arrive.

        Without it the mobile stylesheet at max-width 640px never engages and the
        tables and DOI lists overflow sideways."""
        out = build_site.page("T", "<p>body</p>")
        self.assertIn('<meta name="viewport" content="width=device-width,initial-scale=1"/>',
                      out)

    def test_charset_and_language_are_declared(self):
        """Catches mojibake: these pages are Chinese and must declare utf-8."""
        out = build_site.page("T", "<p>body</p>")
        self.assertIn('<meta charset="utf-8"/>', out)
        self.assertIn('<html lang="zh-CN">', out)

    def test_title_is_html_escaped(self):
        """Catches a Markdown heading containing `<` or `&` breaking the document."""
        out = build_site.page("A & B <script>", "<p>body</p>")
        self.assertIn("<title>A &amp; B &lt;script&gt;</title>", out)
        self.assertNotIn("<title>A & B <script>", out)

    def test_body_html_is_passed_through_unescaped(self):
        """Catches the rendered Markdown being escaped into visible tag soup."""
        self.assertIn("<h1>Rendered</h1>", build_site.page("T", "<h1>Rendered</h1>"))

    def test_navbar_present_by_default(self):
        """Catches content pages losing their route back to the index."""
        self.assertIn('href="index.html"', build_site.page("T", "<p>body</p>"))


class TranslationPairs(unittest.TestCase):
    """stale-translation: pairing logic and, critically, the suppression path."""

    def test_zh_without_english_original_is_not_a_translation(self):
        """Catches firing on the four owner guides, which are Chinese ORIGINALS.
        A check that cries wolf on every commit is one people learn to ignore."""
        names = [p.name for p in Path(hygiene.REPO, "guides").glob("*.zh.md")]
        self.assertTrue(names, "expected Chinese owner guides to exist")
        pairs = {t.name for _, t, _ in hygiene.translation_pairs()}
        for n in names:
            if not Path(hygiene.REPO, "guides", n[:-6] + ".md").exists():
                self.assertNotIn(n, pairs,
                                 f"{n} has no English original and must not be paired")

    def test_pairs_require_the_original_to_exist(self):
        """Every reported pair must have both halves on disk."""
        for orig, trans, lang in hygiene.translation_pairs():
            self.assertTrue(orig.exists() and trans.exists())
            self.assertEqual(len(lang.split("-")[0]), 2)

    def test_every_check_name_has_a_working_exception_key(self):
        """REGRESSION, 2026-07-21. load_exceptions() hand-listed its keys, so
        stale-pdf / agents-sync / kb-index / stale-translation all shipped with
        a suppression hatch that parsed to nothing while their own failure
        messages told users to write exactly that line. Reported fixed once
        before it actually was. Test the escape hatch, not just the alarm."""
        parsed = hygiene.load_exceptions()
        for name in hygiene.CHECK_NAMES:
            self.assertIn(name, parsed,
                          f"{name} has no exception key; its documented "
                          f"suppression would silently do nothing")

    def test_exception_line_for_a_new_check_actually_parses(self):
        """The end-to-end escape hatch, not just the key's presence."""
        with tempfile.TemporaryDirectory() as d:
            f = Path(d, "exc.md")
            f.write_text("- stale-translation: foo.zh.md — because\n"
                         "- not-a-real-check: bar — ignored\n", encoding="utf-8")
            orig = hygiene.EXCEPTIONS
            try:
                hygiene.EXCEPTIONS = f
                got = hygiene.load_exceptions()
            finally:
                hygiene.EXCEPTIONS = orig
            self.assertEqual(got["stale-translation"], {"foo.zh.md"})
            self.assertNotIn("not-a-real-check", got)


class TestDocsXref(Fixture):
    """docs-xref: a filename referenced in docs/ that resolves to nothing.

    Guards the one directory outside the corpus against pointing at a renamed or
    deleted knowledge-base entry — the cross-reference rot no other check reaches."""

    def _repo(self):
        (self.dir / "docs").mkdir()
        (self.dir / "knowledge-base").mkdir()
        return _patched(hygiene, REPO=self.dir)

    def test_valid_path_reference_passes(self):
        """A `knowledge-base/x.md` pointer whose target exists must not fire."""
        with self._repo():
            (self.dir / "knowledge-base" / "real.md").write_text("x", encoding="utf-8")
            (self.dir / "docs" / "sop.md").write_text(
                "See `knowledge-base/real.md` for the evidence.", encoding="utf-8")
            self.assertEqual(hygiene.check_docs_xref(set()), [])

    def test_missing_path_reference_is_flagged(self):
        """The whole reason the check exists: a renamed/deleted KB entry still
        pointed at from docs/. If this starts passing on a real deletion, the
        check has regressed."""
        with self._repo():
            (self.dir / "docs" / "sop.md").write_text(
                "See `knowledge-base/gone.md`.", encoding="utf-8")
            problems = hygiene.check_docs_xref(set())
            self.assertEqual(len(problems), 1)
            self.assertIn("gone.md", problems[0])

    def test_bare_name_resolved_in_a_search_dir_passes(self):
        """A bare `README.md` that exists at the repo root is not stale — the
        check must not treat every backticked *.md as a knowledge-base file."""
        with self._repo():
            (self.dir / "README.md").write_text("x", encoding="utf-8")
            (self.dir / "docs" / "pitch.md").write_text(
                "See `README.md`.", encoding="utf-8")
            self.assertEqual(hygiene.check_docs_xref(set()), [])

    def test_bare_name_existing_nowhere_is_flagged(self):
        with self._repo():
            (self.dir / "docs" / "sop.md").write_text(
                "See `nowhere.md`.", encoding="utf-8")
            problems = hygiene.check_docs_xref(set())
            self.assertEqual(len(problems), 1)
            self.assertIn("nowhere.md", problems[0])

    def test_unbackticked_filename_is_not_treated_as_a_reference(self):
        """False-positive boundary: prose mentioning a bare foo.md with no
        backticks is not a file reference and must not be flagged."""
        with self._repo():
            (self.dir / "docs" / "sop.md").write_text(
                "A file named foo.md is described but not linked.", encoding="utf-8")
            self.assertEqual(hygiene.check_docs_xref(set()), [])

    def test_exception_suppresses_the_report(self):
        """A forward-looking reference recorded in kb-exceptions.md is accepted."""
        with self._repo():
            (self.dir / "docs" / "sop.md").write_text(
                "See `knowledge-base/planned.md`.", encoding="utf-8")
            self.assertEqual(
                hygiene.check_docs_xref({"knowledge-base/planned.md"}), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
