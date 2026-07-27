# catmed v0.1.0 — first citable release

An evidence-integration knowledge base for feline medicine, where every figure
traces to a verbatim published sentence and a machine re-checks that on every
commit.

**Verified at this tag** (from an empty archive, as CI runs it):

- **229 papers, 823 verbatim source excerpts, 0 unmatched** against the archived
  PubMed records — `dr_drill.py leg1`. A further **82** excerpts come from full
  text rather than abstracts; those are reported as *not verifiable here* rather
  than counted as passing.
- The verifier's own self-test passes: a deliberately corrupted record is caught
- **10/10** structural hygiene checks, **71/71** unit tests
- Named-entity privacy screen clean

> These figures were re-measured on the tagged commit. An earlier draft of this
> file carried the numbers from three weeks before it (180 / 677, 8 checks,
> 56 tests) — a status header describing a tree that no longer existed, which is
> the decay SOP §9a is about.

## What is in it

**Owner-facing guides** (Chinese, Markdown + PDF) — the product:

- 🚨 Emergency triage — *do I go to the vet now?*, ordered by danger, no diagnosis assumed
- Chronic kidney disease — every figure carries an inline PMID
- Feline lymphoma (all anatomical types)
- Nasal lymphoma

**Analysis notes for clinicians** (English plus some 中文, with verbatim excerpts
and explicit gaps): **21 files**, spanning the older-cat disease triad
(CKD × hyperthyroidism × hypertension), cardiac disease, emergency red-flags,
supportive and palliative care, assisted feeding, acid suppression, transfusion
compatibility, and an oncology cluster covering treatment currency, COP vs CHOP,
drug toxicity, neutropenia management, response assessment, what a negative PARR
means, and the validity of the markers used to judge response. Topic selection is
itself sourced, from a survey of what cats actually present with and die of.
Five files are in Chinese, including the owner-vernacular lexicon and the
practice-context note; the full language matrix remains deferred.

**Two agents.** A restricted owner-triage agent whose safety property is its
tool list — it can read the knowledge base or decline, and cannot search the
web — and an unrestricted research agent. Both exported as platform-neutral
prompts for non-Claude hosts, with a stated host requirement.

**The tooling, which is the part worth reusing.** A citation-integrity pipeline
that rebuilds its literature archive from scratch on every commit, verifies each
quoted sentence byte-for-byte, and corrupts a record on purpose to prove the
checker can still fail. Plus ten structural checks — orphaned citations, empty
excerpt blocks, coverage drift, stale PDFs, stale translations, agent-export
drift, index drift, generic PII, documentation cross-references, and a search
log that requires a **negative** claim ("no feline evidence exists") to carry a
recorded search rather than an assumption.

## What it is not

It does not diagnose, does not prescribe, and does not replace a veterinarian.
It is built to help someone ask their vet a better question, and to state plainly
where the evidence runs out.

**Cite a clinical figure through its own paper** — the PMID is inline — not
through this project. Cite catmed for the integration, the verification method,
or the recorded gaps.

## Known and deferred

- Coverage was seeded by one cat's illness and is being rebalanced toward what
  cats most commonly present with; several common conditions are not yet covered
- The two lymphoma guides carry partial inline attribution; the debt is tracked
  in `docs/kb-exceptions.md`
- English and Japanese versions are deferred with the translation contract
  already settled — see `docs/LITERATURE-PIPELINE-SOP.md` §11

Full methodology and every defect that shaped it:
`docs/LITERATURE-PIPELINE-SOP.md`. Published site:
https://polyketide.github.io/catmed/
