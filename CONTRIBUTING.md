# Contributing to catmed

Issues and pull requests are welcome in **English, 中文, or 日本語** — write in
whichever you think most precisely. Source excerpts are never translated (see
below), so a multilingual reviewer pool is an asset here rather than a friction.

---

## Before anything else: what this project is, and what it refuses to be

catmed is an **evidence-integration** project. Its value is not that it knows
more veterinary medicine than a veterinarian — it does not. Its value is that
it holds evidence that is scattered across papers, notices when two sources
disagree, and makes every number traceable to the sentence a human author
actually wrote.

It **does not diagnose, does not prescribe, and does not replace a
veterinarian.** Contributions that move it toward "tell the owner what is wrong
with their cat" will be declined regardless of quality. The reason is not
timidity: an unexamined animal cannot be diagnosed from text, and a confident
output is precisely what would cause an owner to delay care.

A useful heuristic for a proposed change: **does it help someone ask their vet a
better question, or does it substitute for asking?** The first is in scope.

---

## The one non-negotiable rule: the citation contract

Body prose is interpretation. **Source excerpts are evidence, and they are
byte-exact.**

Every knowledge-base file ends with a `## 原文摘录（source excerpts）` section.
For each cited paper it carries the verbatim sentences that hold the
load-bearing figures, **in the original language, untranslated, unedited**.

```
**PMID 29393723** · Teng KT 2018
> In total, 2609 cats met the selection criteria from 4020 cats screened.
> ⚠️ Anything beginning with this marker is your own annotation, not the source.
```

A line beginning `> ` that is not an annotation must be a **byte-exact substring
of the archived PubMed record**. CI checks all of them on every pull request.

### What "byte-exact" rules out

Each of these has actually happened in this repository:

- **No synonyms inside quotation marks.** A file quoted a source as saying
  decompression "generally improves sensation"; the source says *"usually"*. The
  meaning was unchanged and it was still a defect.
- **No tidying.** Do not fix the source's typos, normalise its spacing, convert
  its hyphens or quotes, or merge two of its sentences. One archived record
  prints a confidence interval as `95% CI 11.5-1.76` — a lower bound above its
  upper bound. It is quoted exactly like that, with an annotation saying the
  published value is malformed. **Flag it; never silently correct it.**
- **No translation of excerpts.** Translate in the body if you like. The excerpt
  is the thing a future reader checks the translation against, so it has to
  survive intact.
- **Non-breaking and thin spaces are real.** U+00A0 and U+2009 appear in PubMed
  abstracts. Copy and paste; do not retype.

### Why this is worth the inconvenience

A knowledge base written in one language about literature written in another has
a silent failure mode: figures survive translation, but *what the authors said*
exists only as one person's rendering. Drift between that rendering and the
source is invisible, because there is nothing left to compare against.

---

## Adding or changing a claim

1. **Find the paper and get its PMID.**
2. **Fetch it into the local archive.** The archive lives outside the repository
   at `~/.catmed-archive` by design — it is a cache, never a source of truth,
   and everything needed to rebuild it is version-controlled.
   ```bash
   python3 tools/pubmed_archive.py fetch
   ```
   This scans the whole knowledge base for citations, so once your claim cites
   `PMID nnnnnnnn`, the fetch picks it up.
3. **Write the body claim**, with the citation inline.
4. **Add the excerpt block**, copying the sentences that carry your figures.
5. **Run the checks** (below). Fix anything they report.
6. **Open a pull request** describing what changed and what evidence supports it.

### Rules that come from specific mistakes

- **One sentence, one paper's numbers.** A body sentence citing two or three
  papers is where attribution goes wrong. Twelve confirmed misattributions in
  this repository all arose this way — figures filed under whichever PMID was
  nearest. If a sentence carries numbers from two sources, say which is which.
- **"Not in this source" is not "not in any source".** A verification pass once
  deleted three real figures as unverifiable after checking only the paper they
  were misfiled under. They belonged to another paper in the same reference
  list. **Before deleting a figure, search every PMID in the surrounding
  paragraph and reference list for it.** A checker that can only confirm or
  delete converts every filing error into a data loss.
- **Label the species, every time.** This is a knowledge base about cats that
  cites canine, human, rodent and in-vitro work constantly, and cross-species
  extrapolation must be visible in the text rather than inferable from the
  title. `⚠️ Canine data. Cited as extrapolation, not as a feline measurement.`
- **"Not shown to help" ≠ "shown not to help".** Underpowered negative results
  are common in veterinary literature. Write which one you have.
- **An absence needs a documented search.** Claiming that no feline evidence
  exists for something is a claim. Record what you searched and where, so the
  next person can extend it instead of repeating it.

---

## Running the checks locally

Standard library only — Python 3.9+, nothing to install.

```bash
python3 tools/check_kb_hygiene.py    # structure: orphaned citations, empty blocks, PII
python3 tools/pubmed_archive.py fetch    # rebuild the archive from cited PMIDs
python3 tools/pubmed_archive.py verify   # re-hash every archived record
python3 tools/dr_drill.py leg1           # every excerpt against its source
python3 tools/dr_drill.py self-test      # prove the checker can still fail
```

CI runs all of these, starting from **no archive at all** and rebuilding it from
the PMIDs your branch cites. That is deliberate: it tests the claim that the
archive is a disposable cache, and it checks your excerpts against what PubMed
serves today, so an upstream record revision shows up as a failure rather than
as silent drift.

If CI fails on `Rebuild the archive`, that is a PubMed outage, not your change —
re-run the job.

### If a check is wrong

It happens; several of these checkers have produced false positives, and one of
them committed the exact error it was written to detect. Suppress it in
`docs/kb-exceptions.md` **with a written reason**, in the same pull request. The
diff then shows the suppression next to its justification, and a reviewer can
disagree with it. Silently loosening a check is the thing to avoid.

---

## Privacy

This repository originated in one cat's illness, and the clinical records behind
it belong to real people and a real clinic.

**Never commit:** patient names, owner names, clinic or veterinarian names,
case or accession numbers, raw imaging or laboratory reports, or anything that
identifies an individual animal or practice.

The maintainer runs a named-entity screen before every commit. **That pattern
list is deliberately not in this repository and not in CI** — publishing the
list of terms would leak exactly what it protects. The public checks cover
generic cases only: absolute home paths, private-range IP addresses, unexpected
e-mail addresses.

If you are contributing material drawn from a real case, **de-identify it before
it reaches your working tree**, not before you commit. Git remembers.

---

## What would help most

Roughly in order of usefulness:

- **Conditions that send cats to vets, not the ones this repository started
  with.** Coverage today is shaped by a single lymphoma case: oncology, upper
  airway, palliative care, hypertension, hyperthyroid × CKD. Chronic kidney
  disease, dental disease, urinary obstruction, and diabetes are more common and
  barely covered. CKD in particular is full of decisions an owner has to make
  with contradictory evidence — exactly what this project is for.
- **Corrections.** If a number here is wrong, misattributed, or overstated, that
  is the most valuable issue you can file. Say which excerpt contradicts it.
- **Veterinary review of the triage path.** `knowledge-base/emergency-triage-
  red-flags.md` and the triage section of `.claude/agents/medical.md` are where
  a mistake could cause real harm — a missing red flag, or wording an owner
  could read as permission to wait. Clinical review is welcome and wanted.
- **Translation of owner-facing guides.** `guides/` is currently Chinese only.
- **Reuse of the citation harness elsewhere.** `tools/` is not
  veterinary-specific. If it is useful for another evidence-based project, say
  so in an issue — hardening it for a second consumer would improve it here.

## What will be declined

- Content without verbatim source excerpts.
- Dosing recommendations, or anything phrased as an instruction to treat.
- Probability estimates for an animal nobody has examined.
- Advice that could be read as a reason to delay veterinary care.
- LLM-generated summaries of papers not read. This project's entire premise is
  that the excerpt is the evidence; a plausible paraphrase of an abstract is
  precisely the failure mode it exists to prevent.

---

## Licence

MIT. By contributing you agree your contributions are licensed under it.
