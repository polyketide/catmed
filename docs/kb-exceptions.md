# Knowledge-base check exceptions

Every line here suppresses a check in `tools/check_kb_hygiene.py`. Each needs a
written reason, because **a suppressed check is a claim that the defect is not a
defect**, and that claim should be as reviewable as any other in this repository.

Format — the reason after the em dash is for humans, not the parser:

```
- <check>: <id> — <reason>
```

Valid check names: `orphans`, `empty-blocks`, `pii`.

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
