# Releasing, and getting a citable DOI

Written 2026-07-21. Two audiences ask for this: an open-source application that
wants to know how the project is cited, and a veterinarian or researcher who
wants to reference it in a talk or a paper.

`CITATION.cff` already gives GitHub enough to show a **"Cite this repository"**
button on the repository page. A DOI adds the part that matters academically:
a **permanent, versioned archive** that keeps resolving even if the repository
moves or disappears.

---

## ⭐ First, decide whether you need a DOI at all — most of the time, not yet

**A DOI is optional, and minting one is worth deferring until the project is
stable.** This section exists because the DOI route is easy to treat as an
obvious next step after `CITATION.cff`, and it is not one. Reasons to wait:

1. **The `CITATION.cff` button already covers everyday citation, at zero risk.**
   It is committed, it works now, and GitHub renders a "Cite this repository"
   box from it. That is enough for most people who want to reference the project.
2. **This project's real citation anchor is elsewhere.** The value here is that
   every figure traces to a PubMed sentence — so the thing worth citing is the
   *underlying paper*, and `CITATION.cff` says exactly that. A DOI only anchors
   the integration layer, which is useful but rarely urgent.
3. **A DOI is a permanent snapshot, and this corpus still changes often.**
   Freezing a fast-moving tree gains little. Mint the first DOI when the project
   has settled, or when an application or a citing author specifically asks for
   one — not as a reflex.

The permanence below is not a defect: it is the whole point of a DOI (a citation
anchor a publisher cannot quietly retract). It is a reason to **time** the first
release well, not a reason to avoid Zenodo. When that time comes, the rest of
this document is the procedure.

⚠️ **Note on the public-repo baseline.** Making a GitHub repository public
already publishes irreversibly in practice — crawlers, forks and caches capture
what you push, and a force-push only rewrites your own copy. Zenodo adds one more
layer (you cannot rewrite even your copy), but it does not create the exposure
from nothing. The privacy screen matters at *every* public push, not only at a
release.

---

## ⚠️ Read this before minting anything

**A Zenodo deposit is permanent in a way a git commit is not.**

A bad commit can be rewritten, force-pushed, and effectively erased. A Zenodo
record is assigned a DOI, indexed, and mirrored; withdrawing one requires
contacting Zenodo and leaves a tombstone. There is no `git push --force`
equivalent.

This is §9a.1 of the SOP applied to releases: **rank verification by how far an
artifact travels and how badly it updates.** A release travels further and
updates worse than anything else this project produces.

**So the named-entity screen is not optional before a release — it is the last
moment it can still matter.** Run it, and run the public checks, on the exact
commit you are about to tag:

```bash
python3 tools/check_kb_hygiene.py     # 8 checks incl. PII, staleness, generated artifacts
python3 tools/test_tools.py           # unit tests for the checkers
python3 tools/pubmed_archive.py fetch # rebuild the archive from cited PMIDs
python3 tools/dr_drill.py leg1        # every excerpt vs its source
python3 tools/dr_drill.py self-test   # prove the checker can still fail
```

Then the local named-entity screen, which is deliberately not in this repository
and not in CI — publishing the pattern list would leak what it protects.

**Do not tag a commit whose CI has not gone green.** The release archives the
tree as it is, not as it will be after the follow-up fix.

---

## One-time setup

1. Sign in to **https://zenodo.org** with the GitHub account that owns the
   repository, and authorise the GitHub integration.
2. In Zenodo's GitHub settings, find `polyketide/catmed` and switch it **on**.
   Zenodo then listens for GitHub *Releases* on that repository.

⚠️ Zenodo's interface wording changes from time to time. The shape of the flow —
authorise, toggle the repository, then release — has been stable, but **do not
treat the exact labels above as verified**; they are from general knowledge, not
from having walked this account through it.

Nothing is archived until the first release, so the toggle alone is safe.

---

## Making a release

```bash
# 1. Confirm you are releasing what you think you are
git status --short          # must be empty
git log origin/main..HEAD   # must be empty
gh run list --limit 2       # both workflows green on this commit

# 2. Tag and push
git tag -a v0.1.0 -m "First citable release"
git push origin v0.1.0

# 3. Create the GitHub Release (this is what Zenodo reacts to)
gh release create v0.1.0 --title "catmed v0.1.0" --notes-file docs/release-notes-v0.1.0.md
```

Zenodo picks it up within a few minutes and mints **two** DOIs:

| DOI | Points at | Use it for |
|---|---|---|
| **Concept DOI** | always the newest version | the general "cite this project" case |
| **Version DOI** | this release, frozen | reproducing a specific claim |

**Cite the concept DOI in `CITATION.cff`**, so the reference does not go stale
with each release.

### Versioning

Use semantic-ish versions where the **minor** number moves when the corpus
gains or corrects material, and the **patch** number moves for tooling and
documentation. A reader who cites `v0.3.0` and later reads `v0.4.0` should be
able to tell that the evidence changed, not just the scripts.

---

## After the first DOI exists

1. Add it to `CITATION.cff`:

   ```yaml
   doi: 10.5281/zenodo.XXXXXXX      # the CONCEPT DOI, not the version DOI
   ```

2. Add the badge to `README.md`, next to the CI badge:

   ```markdown
   [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
   ```

3. Commit both. `CITATION.cff` is the file GitHub reads for the citation button,
   so the two must agree.

---

## ⚠️ What a DOI for this project does *not* mean

**It does not make the clinical figures citable through this project.** They
belong to the papers they came from, and `CITATION.cff` says so explicitly:

> If you are citing a specific clinical figure, cite the underlying paper (its
> PMID is given inline), not this project.

Cite catmed for the **integration, the verification method, or the recorded
gaps** — the things this project actually produced. Citing it for a survival
figure would put a layer between a reader and the evidence, which is the exact
distance this repository exists to remove.

---

## If the project is ever archived or abandoned

The DOI keeps resolving; that is its purpose. Two things worth doing before
walking away:

- Make a final release so the last verified state is the one preserved.
- Note in the README that the corpus is no longer maintained, **with a date**.
  Per SOP §9a, a status header decays faster than anything else in a document —
  and a knowledge base whose last check ran years ago is exactly the thing a
  reader needs told plainly.
