<!-- Read by Codex, Cursor, Zed, Aider, Continue and other agentic coding tools.
     Claude Code additionally reads .claude/agents/. Keep this file tool-neutral. -->

# AGENTS.md — working in this repository

**catmed** is an evidence-integration project about feline medicine. Its single
distinguishing property is that **every figure traces to a verbatim published
sentence, and a machine re-checks that on every commit.**

If you are an agent making changes here, the rules below are not style
preferences. Most of them exist because something specific went wrong.

---

## The one non-negotiable rule

Body prose is interpretation. **Source excerpts are evidence, and they are
byte-exact.**

Every corpus file ends with a `## 原文摘录（source excerpts）` section:

```
**PMID 29393723** · Teng KT 2018
> In total, 2609 cats met the selection criteria from 4020 cats screened.
> ⚠️ A line starting with this marker is annotation, not source text.
```

A `> ` line that is not an annotation **must be a byte-exact substring of the
archived PubMed record.** Do not fix the source's typos, normalise its spacing,
convert its hyphens or quotes, translate it, or merge two of its sentences.
One archived record prints a confidence interval as `95% CI 11.5-1.76` — bounds
inverted. It is quoted exactly like that, with an annotation saying so.

**Copy and paste. Do not retype.** U+00A0 and U+2009 occur in real abstracts.

---

## Before you commit — run these

Standard library only, Python 3.9+, nothing to install:

```bash
python3 tools/check_kb_hygiene.py     # structure, staleness, PII
python3 tools/pubmed_archive.py fetch # rebuild the archive from cited PMIDs
python3 tools/dr_drill.py leg1        # every excerpt vs its source
python3 tools/dr_drill.py self-test   # prove the checker can still fail
python3 tools/test_tools.py           # unit tests for the checkers themselves
python3 tools/export_agents.py --check # portable prompts still in sync
python3 tools/build_kb_index.py --check # clinician index still matches the corpus
```

The literature archive lives **outside** the repository at `~/.catmed-archive`.
It is a cache, never a source of truth; everything needed to rebuild it is
version-controlled. If a check reports no archive, run the `fetch` line.

CI runs all of this from an **empty archive**, so it also proves the cache is
disposable and checks excerpts against what PubMed serves *today*.

---

## Rules that come from specific mistakes

- **One sentence, one paper's numbers.** A sentence citing two or three papers
  is where attribution goes wrong — twelve confirmed misattributions here all
  arose that way. If a sentence carries numbers from two sources, say which is
  which.
- **"Not in this source" ≠ "not in any source".** A verification pass once
  *deleted three real figures* as unsourced after checking only the paper they
  were misfiled under; they belonged to another paper in the same reference
  list. Before deleting a figure, search every PMID in the surrounding paragraph
  and reference list for it.
- **Label the species.** This is a knowledge base about cats that cites canine,
  human, rodent and in-vitro work constantly. Extrapolation must be visible in
  the text.
- **"Not shown to help" ≠ "shown not to help".** Underpowered negative results
  are common in veterinary literature. Write which one you have.
- **An absence needs a documented search.** Claiming no feline evidence exists
  is itself a claim. Record what you searched.
- **When you find nothing, check you searched every form it takes.** Three
  separate defects here were "grep for the representation I expected, conclude
  the thing is absent" — a monolingual checker reporting Chinese markers as
  unverified, a per-file rule calling cross-file citations orphans, and a claim
  that the guides had no inline citations when 6% of lines did.
- **Generated, never typed.** Reference lists, portable prompts and the site are
  produced by scripts from verified sources. Three of seven hand-typed reference
  entries were once wrong.
- **Re-translate when you edit an original.** `stale-translation` pairs
  `<name>.<lang>.md` with `<name>.md` by commit time. Excerpts stay
  byte-identical — never re-translate those; only the prose goes stale.
- **Rebuild the PDF when you edit a guide.** `check_kb_hygiene.py stale-pdf`
  enforces it. The PDF is the artifact owners download and forward, and it does
  not update itself.

---

## Scope — what will be declined

- Content without verbatim source excerpts
- Dosing recommendations, or anything phrased as an instruction to treat
- Probability estimates for an animal nobody has examined
- Anything readable as a reason to delay veterinary care
- LLM-generated summaries of papers nobody read

A useful test for a change: **does it help someone ask their vet a better
question, or does it substitute for asking?** Only the first is in scope.

---

## Privacy

This repository originated in one cat's illness; the records behind it belong to
real people and a real clinic.

**Never commit** patient, owner, clinic or veterinarian names, case numbers, raw
reports, or anything identifying an individual animal or practice. **Never print
an absolute filesystem path in agent output** — it leaks the operator's account
name into every screenshot.

The maintainer runs a named-entity screen locally before each commit. That
pattern list is deliberately **not** in this repository and not in CI: publishing
it would leak exactly what it protects. Public checks cover generic cases only.

---

## Using the agent definitions on a non-Claude platform

`.claude/agents/` is the source of truth. `agents/*.prompt.md` are generated
platform-neutral exports — run `tools/export_agents.py` after editing, and
`--check` verifies they have not drifted.

**⛔ Read the host requirement at the top of `agents/cat-owner-triage.prompt.md`
before deploying it.** Its safety property is the *tool restriction*
(`Read, Grep, Glob` — no web, no shell), not the prose. The same rule written as
prose failed twice on the same test. A platform that cannot restrict tools must
not present that prompt to cat owners.

---

## Where things are

| Path | What |
|---|---|
| `guides/` | owner-facing, Chinese, Markdown + PDF — **the product** |
| `knowledge-base/` | analysis notes, English, with verbatim excerpts |
| `docs/LITERATURE-PIPELINE-SOP.md` | every defect found, and the rule it produced |
| `docs/kb-exceptions.md` | suppressed checks, each with a written reason |
| `tools/` | archive, checkers, site builder, agent export |
| `.claude/agents/` | agent definitions (source of truth) |
| `agents/` | generated portable prompts |
| `knowledge-base/README.md` | generated index for clinicians — start here if you are a vet |
| `.github/ISSUE_TEMPLATE/` | challenge a figure · clinical review · propose coverage |

Published site: **https://polyketide.github.io/catmed/**
