<!--
Thanks for contributing. Delete any section that does not apply — a typo fix
does not need an evidence checklist.

Issues and PRs in English, 中文 or 日本語 are all fine.
-->

## What this changes

<!-- One or two sentences. -->

## Evidence

<!-- Only for changes that add or alter a claim. -->

- PMIDs added or affected:
- Which excerpt supports the change:

**Checklist for a claim change** (see CONTRIBUTING.md):

- [ ] Every new `> ` excerpt line is copied and pasted from the source, not retyped or tidied
- [ ] The species is labelled if the paper is not feline
- [ ] If the sentence cites more than one paper, it is clear which numbers came from which
- [ ] A negative result is written as "not shown to help" unless the study actually showed harm or equivalence
- [ ] No figure was deleted without first searching the other PMIDs in the same paragraph and reference list for it

## Checks

- [ ] `python3 tools/check_kb_hygiene.py` passes
- [ ] `python3 tools/dr_drill.py leg1` passes
- [ ] Any suppression added to `docs/kb-exceptions.md` carries a written reason

## Privacy

- [ ] No patient, owner, clinic or veterinarian names; no case numbers; no raw reports
- [ ] Any real-case material was de-identified **before** it reached the working tree

<!--
If this touches the triage path (emergency-triage-red-flags.md, or the triage
section of .claude/agents/medical.md), please say so explicitly — that is where
an error can cause real harm, and it gets a slower review.
-->
