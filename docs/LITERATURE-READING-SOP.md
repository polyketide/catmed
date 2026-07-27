# Reading a paper — the veterinary version

Adapted 2026-07-27 from the sibling research agent's reading rules: `docs/GPU-LITERATURE-READING-SOP.md` and the *Reading SOP (hard rule — always)* section of that project's own CLAUDE.md. Those govern an enzyme-research agent whose reader is a local model on a GPU node and whose output is a Chinese digest. **This project's reader is the agent itself, its output is a byte-exact excerpt, and its readers are cat owners and their clinicians.** That changes enough to warrant its own document rather than a pointer.

`LITERATURE-PIPELINE-SOP.md` governs the *pipeline* — archive, verification, hygiene. This governs the *read*.

---

## 0. What carried over unchanged, and what did not

| | Research agent | Here |
|---|---|---|
| Who reads | a local model on the GPU node (zero-token triage) | **the agent itself** — there is no node, and no zero-token tier |
| Output of a read | a Chinese digest in a strict library | **verbatim excerpts** in `## 原文摘录`, verified by Leg 1/Leg 5 |
| Honesty ceiling | *"the local 14B is a FILTER, not deep understanding"* | **the abstract is the filter; the full text is the source** — and no digest, summary or paraphrase is admissible at all |
| Egress guard | unpublished drafts never leave the trust domain | the **repository is public** — PDFs and extracted text never enter it |
| Scanned PDFs | local node OCR, never a cloud OCR | **no OCR capability exists here** — see §3 |

**Carried over verbatim in substance: text-first, scanned-is-not-empty, flag-not-invent, provenance recorded.** Those four are why this document is short.

---

## 1. When the full text is required, not optional

Read the full text whenever the paper is doing any of the following in the knowledge base:

- **carrying a number that a decision leans on** — a survival figure, a dose, a complication rate, a predictive value;
- **being cited for something the abstract does not state** — the abstract is a summary written to persuade, and its omissions are not random;
- **standing alone as the evidence for a claim** — a single-source claim gets the full text or it gets a caveat saying it did not;
- **contradicting another paper**, or contradicting itself between abstract and results (this project has found both).

The abstract is sufficient only for orientation and for excerpts that genuinely live in it.

---

## 2. How to read it — text-first

```bash
python3 tools/fetch_fulltext.py <PMID> ...   # licence looked up, never assumed
python3 tools/fulltext_text.py extract       # pdftotext -> archive, with SHA-256
python3 tools/dr_drill.py leg5               # every full-text excerpt vs that text
```

1. **Extract the text and read the TEXT.** Never render a text-bearing PDF as page images to summarise it — that spends vision tokens on what `pdftotext` gives cheaply, and it reads a *picture* of the sentence rather than the sentence.
2. **The extracted text is archived**, so a later run can check the excerpt. This is the addition over the research agent's version: there, a read produces a digest nobody re-verifies; here, an unverifiable excerpt is inadmissible (§6).
3. **A page-fetching tool's output is not a source.** It returns a model's summary of a page, not the page — see the pipeline SOP's *"a web page is not a source"*.

---

## 3. ⛔ Scanned PDFs: this project cannot read them, and says so

The research agent routes a scan to a **local** OCR on its node and forbids cloud OCR outright. **This project has neither.** So when `pdftotext` returns under 200 characters:

- the file is **reported as needing OCR and not extracted**;
- it is **never treated as an empty document** — that would make every excerpt from it "unverifiable" while the run reads as though nothing were wrong;
- ⛔ **and it is not sent to a cloud OCR service to work around the gap.** The research agent's reason was trust-domain (unpublished pages). The reason here is the same discipline in a different coat: a capability this project does not have is recorded as absent, not simulated.

**Current status: 0 of 45 held PDFs lack a text layer.** The rule exists before the case that needs it.

---

## 4. ⭐ The veterinary part: four things to fix before reading a single result

This is what the research version has no equivalent of, and it is the whole reason for a separate document. **In this field the most dangerous error is not a misquoted number — it is a correctly quoted number attached to the wrong animal.**

1. **⭐ Species, first and always.** Before recording any figure, establish whether it is feline, canine, or human. Whole guidelines transfer badly: VCOG's response criteria state they are *"intended only for use in dogs"*, and a project entry exists solely because a mirtazapine or G-CSF finding is species-specific. **A figure whose species is not recorded is not usable**, and every extrapolation is labelled as one, fused to the finding rather than appended.
2. **N, and what N is made of.** Seven cats and eleven cats is a randomised comparison; 2609 cats is a primary-practice cohort. Referral populations are not general populations. Record the number *and* the setting, because the sentence that omits the setting is the one that gets over-read.
3. **Design and date.** Prospective vs retrospective, randomised vs case series, single-centre, and the year. **A protocol matching a textbook is proof of copying, not of currency** (§3 of the pipeline SOP's currency entry).
4. **Funding and authorship.** A manufacturer among the authors does not invalidate a result; omitting it while quoting the result does. This is how the CK-586 entry was written.

---

## 5. What must be taken from a full text that an abstract will never give

- **⚠️ The parenthetical.** A P value, a confidence interval, an n. **Never truncate a quotation before a statistic** — one excerpt in this repository read *"…returned to a value comparable with that of the control group by 12 weeks of treatment."* where the source ends `(P = 0.06)`. Cutting there turns a trend into a demonstrated result.
- **The limitations paragraph.** Abstracts almost never carry it, and it is frequently the most decision-relevant text in the paper — the Baez entry's "subjective, single investigator, never tested for inter-observer reproducibility" comes from there.
- **The completeness of adverse-event reporting, as a finding in its own right.** When a paper says its harm data were *"too inconsistent to report"*, that sentence is the result. A protocol cannot be called safe on data that were never assembled.
- **Whether the abstract and the results section agree.** They have disagreed here before. If they do, quote both and say so.
- **Subgroup collapse.** A figure that holds overall and vanishes in the subgroup that matters — body weight predicting survival until only lymphoma cats are considered — is a finding the abstract will present as the opposite.

---

## 6. The output of a read is an excerpt, not a summary

⛔ **No digest, paraphrase, or translation of a source sentence may enter the knowledge base.** The research agent's local model produces a Chinese digest and that is appropriate there, because a digest is triage and the library records who produced it. Here the excerpt *is* the evidence a clinician will check, so:

- excerpts are **verbatim and untranslated**, in the source's own language;
- the body prose is clearly the project's interpretation, and says so at the top of every block;
- **a number this project computed is not a quoted figure** — `7/26` is the source, `27%` is arithmetic;
- provenance is marked in-block (`【Publisher full text retrieved and checked <date>】`) so Leg 1 knows not to look for it in the abstract.

---

## 7. Verification is not optional, and it is what makes deep reading safe

**A full-text excerpt is admissible only if its source text is archived** — otherwise it is an unverifiable quotation wearing the formatting of a verified one, which is worse than no quotation because the block advertises byte-exactness.

Leg 5's verdict line counts its tolerances separately (`exact` / `repaired` / `lossy` / `excepted`) so they can never collapse into "fine", and reports how many papers it still cannot see **and how many of its own exceptions have gone stale**.

⭐ **Expect most failures to be the extractor, not the excerpt — and do not let that expectation soften the check.** Of 21 mismatches across two runs, **19 were extraction artefacts** and **2 were genuine transcription errors** invisible to any abstract-level check: a dropped word (`lifestyle of` for `lifestyle typical of`) and a dropped `p` twice (`(< 0.0001)` for `(p < 0.0001)`). The artefact classes seen so far:

| Artefact | Handling |
|---|---|
| word hyphenated across a line break | tolerated in the matcher |
| a font map rendering every `=` as `¼`, dropping `±` | repaired on retry, **counted** |
| two columns interleaved line by line | both `pdftotext` modes extracted, either may match |
| **inline superscript reference numbers** (`hypertensive cats,7,20,57,66,67 including…`) | ⛔ **named per excerpt in `kb-exceptions.md`, never tolerated** |
| a figure caption or running footer injected mid-sentence | same |

⛔ **The last two are not given a matcher tolerance on purpose**: tolerating them means ignoring digits inside a sentence, in a corpus whose entire premise is that the digits are right. An artefact gets named, with its PMID and the excerpt prefix, so it can never quietly cover a second excerpt of the same paper. ⚠️ **Extraction is lossy in ways that are not the excerpt's fault** — de-hyphenation, and at least one publisher font map that renders every `=` as `¼` — so a mismatch is a prompt to look, and the tolerances are regression-tested against a real dropped word and a real changed digit.

---

## 8. ⚠️ Held for reading is not cleared for sharing

Open-access status and licence are looked up per paper, never assumed, and **no access control is ever circumvented**. Two distinctions the research agent never had to make, because it was not handing files to anyone:

- **Free to read ≠ redistributable.** A `bronze` paper opens in a browser and grants no re-distribution licence. Only CC/public-domain files are ever passed on; the rest are shared as links.
- **A watermark is licence evidence.** Three extracted texts here carry `Brought to you by University of Tokyo | Unauthenticated`, and all three have no licence. Reading them is fine. Forwarding them is not.

---

## 9. Where this sits

- `LITERATURE-PIPELINE-SOP.md` §3l — the standing instruction and the incident that produced it.
- `LITERATURE-PIPELINE-SOP.md` §3h — a dose is written only when a record states it verbatim.
- `LITERATURE-PIPELINE-SOP.md` §7a — choosing what to read next, and treating a lead as a lead.
- `tools/fetch_fulltext.py`, `tools/fulltext_text.py`, `tools/dr_drill.py leg5` — the automation. Use it; do not hand-roll the steps it already performs.
