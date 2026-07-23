# Knowledge-base check exceptions

Every line here suppresses a check in `tools/check_kb_hygiene.py`. Each needs a
written reason, because **a suppressed check is a claim that the defect is not a
defect**, and that claim should be as reviewable as any other in this repository.

Format — the reason after the em dash is for humans, not the parser:

```
- <check>: <id> — <reason>
```

Valid check names: `orphans`, `empty-blocks`, `coverage`, `stale-pdf`, `stale-translation`, `agents-sync`, `kb-index`, `pii`. (This list is the human-facing mirror of `CHECK_NAMES` in `tools/check_kb_hygiene.py`; keep the two in step.)

Adding a line here is a normal part of a pull request when the exception is
genuine. Adding one to make CI green when the defect is real is the failure this
file is designed to make visible: the diff shows the suppression next to the
reason, so a reviewer can disagree with it.

---

## orphans

A PMID cited in the knowledge base with no source-excerpt block. Normally this
means the paper was never archived and the claim resting on it was never
verified — see `docs/LITERATURE-PIPELINE-SOP.md` §3c. The exceptions are
identifiers that are **not sources at all**:

- orphans: 17552367 — Not a source. A transcription error retained as evidence. This PMID resolves to Blumberg MS et al., "Sleep, development, and human health" (*Sleep* 2007) — a human sleep editorial that has nothing to do with this repository. It was written into an early draft in place of Baez 2007, whose correct PMID is 17451991. The wrong identifier and the paper it actually resolves to are kept in the reference-record section of `supportive-and-palliative-care.md` so the error stays documented rather than being quietly overwritten.
- orphans: 31896807 — Not a source. The same failure: this resolves to Netto GJ, "Editorial" (*Mod Pathol* 2020), and was written in place of Evangelista 2019, whose correct PMID is 31836868 (digits transposed). Retained on the same grounds.


### Owner-guide reference-list entries (60), a tracked debt rather than an acceptance

`guides/*.zh.md` entered verification on 2026-07-21, having been written before the
citation contract existed. Bringing them in exposed something the excerpt count hides:

**⚠️ The original wording of this note was wrong, and it is corrected here rather than
rewritten away.** It read: *"Their body prose carries no inline citations at all. Not one
`PMID` appears before `## 附录 B`."* The second sentence was true. The first did not follow
from it — **I grepped for the citation form I expected and reported the absence of that form
as the absence of attribution.** The guides do cite, by author and year: *Sfiligoi 2007*,
*Haney 2009*, *Goto 2022*, in tables and 依据 lines. A reader can trace those to the reference
list by name.

**Measured 2026-07-21: 58 of 951 substantive body lines carried author-year attribution — about
6%.** So the finding was directionally right and overstated in degree, which is exactly the
error class this repository keeps catching in its own checkers: testing for one representation
and concluding about the thing itself.

**Work done 2026-07-21.** 62 of 87 author-year mentions resolved uniquely to an archived record
(0 ambiguous) and now carry their PMID inline — safe because *the paper was already named in the
prose*, so no sentence-level attribution judgement was involved. `tools/attribution_candidates.py`
was written to propose the rest without deciding: it sorts figures into UNIQUE / AMBIGUOUS /
UNMATCHED and hands the judgement to a human, because a figure appearing in one abstract is not
proof the sentence is about that paper.

**What remains, measured rather than estimated:**

- **25 author-year mentions that do not resolve** to an archived record (Collette 2015, Kogan 2026,
  Tzannes 2007, May 1987 …). Either not archived, or the guide names a different author position.
- **~94% of body lines still carry no attribution.** Distinctive figures (3+ digits) across both
  guides: 198 UNIQUE candidates over 136 lines and 66 papers, plus 99 AMBIGUOUS and 53 UNMATCHED.
  Every UNIQUE one still needs a human to read the sentence.
- The 60 suppressions below remain accurate: these PMIDs appear only in the reference appendix and
  have no excerpt block.

**These suppressions are the marker for that debt, not its discharge.** The CKD guide was built
with inline attribution from its first draft so the debt does not grow.

**Progress 2026-07-21 (continued).** Two more standalone load-bearing figures got inline PMIDs after
sentence-level review — the cribriform-plate 121-vs-876-day prognostic split (Reczynska 2022, verified
in its excerpt block) and the chlorambucil 1317-day small-cell figure (Pope 2015), the latter now also
labelled 消化道小细胞型 so the guide's own "do not extrapolate to nasal lymphoma" warning is harder to
miss. The remaining figures were NOT auto-inserted: most repeat a study already named in the same
paragraph or table column (e.g. 536/172 days sit directly under "Haney 2009（PMID 19143934）"), and the
per-figure matcher's "unique" hits include coincidences — a cat's 200–300 mL blood volume matched a
nasal-disease PMID purely because 300 appears in its abstract. That is the co-occurrence-is-not-
attribution trap, and it is why the remainder stays human-reviewed rather than scripted.

One genuine defect surfaced and is now flagged inline rather than suppressed: the nasal guide's
"complete-remission survival 50–2520 days, median 296" (§2.1) appears in NO cited abstract and NO
excerpt block. Marked 出处待核 in the body — the large-spread conclusion it illustrates is corroborated
by other tables, but those two specific numbers are unverified until their full-text source is found.



- orphans: 3597844 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 8263850 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 8947869 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 9353558 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 11899035 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 15265480 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 15954547 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 16407483 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 16700173 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 17881744 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 18466247 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 19055574 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 19178669 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 21041334 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 22577051 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 24879661 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 24903757 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 25146662 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 26109275 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 26308738 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 26511103 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 27562979 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 28100766 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 29963947 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 30004120 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 30305106 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 30554552 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 30994392 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 31161850 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 31254440 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 31328872 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 31554586 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 32573314 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 32903608 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 32996835 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 33345405 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 33473067 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 33894870 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 34236002 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 34458024 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 35048412 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 35051110 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 35188319 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 35279897 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 35442117 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 35720767 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 36049238 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 37095139 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 37627457 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 38891700 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 39032511 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 39619931 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 39631747 — reference-list entry in feline-nasal-lymphoma-owner-guide.zh.md; see the note above.
- orphans: 40508984 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 40624957 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 40657883 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 40716042 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 41072475 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 41111634 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.
- orphans: 41742593 — reference-list entry in feline-lymphoma-all-types-owner-guide.zh.md; see the note above.

## empty-blocks

An excerpt block with no quoted source text. Prefer the in-file declaration —
an annotation containing the phrase `no source text available` — over an entry
here, because it keeps the reason next to the block a reader is looking at.

*(No entries. `27154944` is a Vet Rec letter with no abstract in the PubMed
record and declares itself in place.)*

## pii

Generic secret and PII findings that are intentional. Note that this repository's
**named-entity privacy screen is deliberately not part of the public checks** —
publishing that pattern list would leak precisely what it protects. Run it
locally before every commit.

*(No entries. The one e-mail address in the tree, required by the Unpaywall API,
is allow-listed in the script itself.)*

