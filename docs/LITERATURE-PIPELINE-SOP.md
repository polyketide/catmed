# Literature Pipeline SOP — offloading retrieval to a local node

> Status: **design agreed 2026-07-20, not yet built.** Nothing here has been run. Treat every section as a specification to implement and verify, not as a description of working behaviour.
> Companion document: `.claude/agents/medical.md` §C, which states the rules binding the agent's own behaviour. This file covers engineering and operations.
>
> **Provenance of what follows.** Directly verified by reading the files: the hardware ceiling and model tiers, the existence of the sibling project's reading loop and its still-growing library index, and the presence of its node SOPs. **Reported by a survey subagent and not independently confirmed**: the internal structure of that reading loop (its stage breakdown, deduplication strategy, retry behaviour, and offline-digest mode) and the contents of the sibling project's error-handling SOPs. Those informed the patterns below and are believed accurate, but per this project's own rule that a report is a source rather than a fact, **read the originals before depending on any specific detail.**

## 1. Why

Fetching literature is the largest token cost in this project and needs almost no intelligence. Searching PubMed, pulling metadata, matching by PMID, dropping duplicates, and discarding noise fields are API and string operations. Meanwhile the work that actually requires judgement — which paper is load-bearing, which sentence may be quoted, whether a cited figure exists in the source — is a small fraction of the tokens.

Splitting these puts each on the right substrate. It also introduces heterogeneity into a project that is otherwise entirely Claude-authored: the knowledge base, the SOP, and the self-checks all come from the same model, which is a correlated set of eyes.

**Measured 2026-07-20** over the knowledge base's full citation set (63 PMIDs), via `tools/pubmed_archive.py measure`:

| Representation | ~tokens | per record |
|---|---|---|
| Raw XML as PubMed sends it | 262,693 | 4,169 |
| **MCP-equivalent payload + repeated legal notice = current baseline** | **57,590** | 858 |
| Trimmed view the pipeline would hand over | **29,563** | 469 |

**Saving against the real baseline: 1.9×, i.e. 49% of tokens removed.** An earlier draft of this file claimed 8.9×; that figure used raw XML as the baseline, which is not what the agent ever receives. The honest number is the smaller one.

### The discarded-candidate saving: measured, and mostly unavailable

An earlier draft of this section guessed that the unmeasured half — candidates fetched and thrown away — would be the larger prize, on the theory that filtering them out before they reach the agent is where local screening earns its keep. **Measured 2026-07-20 via `tools/screen.py`, that guess was wrong in the way that matters.**

Replaying ten real searches produced a 136-candidate pool, of which 12 are cited by the knowledge base:

| Mode | Compression | Recall of cited papers |
|---|---|---|
| Field trimming only (lossless) | **1.8×** | **100%** |
| Plus content screening | 2.9× | **66.7%** |

**Content screening is rejected.** The extra 20 percentage points of compression cost four load-bearing sources, and the loss is silent — nothing downstream can notice a paper it was never shown. Among the discarded: the review that carries the entire lily section, dropped for "no quantitative signal" while supplying the two sentences that section rests on ("As little as 2 leaves or part of a single flower have resulted in deaths"; "Prognosis is excellent if fluid diuresis is started before anuric renal failure has developed").

**The defect is the premise, not the thresholds.** Those rules encode *useful means quantitative*. This knowledge base's most load-bearing citations are frequently qualitative boundary statements — a dose that kills, a window in which prognosis is excellent — with no percentage, no p-value, nothing a pattern can match. The species rule fails the same way on the human-medicine literature cited deliberately in §3. Retuning the patterns would only change *which* load-bearing papers vanish.

**What survives is the lossless part, and it replicates.** Field trimming measures 1.8× on this candidate pool and 1.9× on the cited set — two independent measurements agreeing. That is the real, bankable saving: strip `query_translation` echoes, repeated legal notices, affiliations, MeSH terms and keywords, and discard no paper at all.

⚠️ 100% recall here is on the pool these queries produced. It is not proof the trimming is safe on queries it has not seen — only that dropping *nothing* cannot lose anything, which is the point.

## 2. The division of labour

| Stage | Where | Why |
|---|---|---|
| Query construction | Local, escalate when unclear | Mechanical for known red flags; a genuinely new question is worth a Claude call |
| PubMed search, metadata fetch | **Local** | Pure API work |
| Deduplicate, index by PMID | **Local** | Dictionary lookup |
| Skip what is already archived or cited | **Local** | Identity matching, not a judgement about content — lossless by construction |
| Drop noise fields | **Local** | `query_translation` (PubMed's expanded query string) and the repeated legal notice are pure overhead |
| ~~Relevance filtering by content~~ | **Nowhere** | **Measured and rejected** — 66.7% recall (§1). Dropping papers on quantitative or species signals discards load-bearing sources, silently. |
| **Select the load-bearing paper** | **Claude** | Judgement |
| **Choose the sentence to excerpt** | **Claude** | This is the project's core asset |
| **Verify figures against source** | **Claude** | The check that catches transposed PMIDs and phantom numbers |
| **Detect internal contradictions** | **Claude** | e.g. abstract vs results section |
| Write interpretation | **Claude** | — |

**The invariant**: the local side moves bytes, the Claude side makes claims. A local model may rank a paper as promising; it may never produce a sentence that ends up inside `## 原文摘录`.

**The line inside that invariant, learned by measurement**: the local side may decide by **identity**, never by **content**. Skipping a PMID already in the archive cannot lose a paper — the paper is already held. Deciding a paper looks irrelevant can, and the loss leaves no trace, because nothing downstream can miss what it was never shown. So ranking is permitted and truncation is not: **whatever the local side ranks, it hands over complete.** The moment a local score decides what the agent sees rather than what it sees first, content filtering has been reintroduced under another name.

## 3. Where the archive lives — and why that makes DR mandatory

**Decided 2026-07-20: the raw API archive lives outside the repository.** Committing API dumps would bloat a public repo with material that is neither reviewable nor ours to redistribute.

But leaving git means leaving git's protection, and that has one consequence that shapes everything else:

> **The archive must be a cache, never a source of truth.** Whatever is required to rebuild it from scratch — the PMID list, the queries that produced it, the fetch parameters — **stays in the repository, version-controlled.** The archive holds bytes that can be re-fetched; the repo holds the instructions for re-fetching them.

If that split holds, total loss of the archive costs time and API calls, not knowledge, and disaster recovery reduces to "re-run the fetch". If it does not hold — if some PMID exists only in the uncommitted archive — then a disk failure silently deletes part of the evidence base and nothing will announce it.

**Therefore the recoverability of the archive is a property that must be tested, not assumed.** That is §4a.

## 3b. Storage contract

The pipeline writes a raw archive that Claude reads directly. Requirements:

- **Raw API payload stored verbatim**, one record per PMID, unmodified. No re-encoding, no whitespace normalisation — U+00A0 and U+2009 appear in real PubMed abstracts and must survive.
- **Content hash per record**, so a later verification pass can prove the archive was not rewritten between fetch and use.
- **Any local-model output stored in a separate field**, clearly named as a hint (e.g. `local_relevance_note`), never merged into the payload. If a future reader cannot tell at a glance which bytes came from PubMed and which from a 14B model, the format is wrong.
- **Fetch provenance**: timestamp, query used, tool version.

## 4. Frozen-baseline regression (the self-check)

Adapted from the sibling project's flywheel rule for a domain with no ground-truth oracle: *lock a benchmark that never participates in training; only a run that does not degrade it counts as an improvement; if it degrades, stop, alert, and keep the old artefact.*

Here the frozen baseline is **a subset of already-verified knowledge-base entries**. The pipeline must be able to re-derive, for each entry in that set, the same PMIDs and the same verbatim excerpt text. If it cannot, the pipeline has drifted and must halt rather than continue producing.

This is what makes the loop safe to leave running: it has a way to detect its own corruption that does not depend on anyone reading its output.

## 4a. Disaster-recovery drill

Modelled on the sibling project's DR drill, whose governing idea is `runs ≠ works` applied to backups themselves: **prove the backup restores, not merely that it was written.** Two rules from it carry over unchanged:

- **Each leg reports independently.** A leg that cannot run is `SKIP`, never a fabricated `PASS`.
- **Emit one machine-greppable verdict line per leg**, so the drill can be automated and its flatline detected.

### The legs

**Status 2026-07-20: Legs 1, 2 and 4 are implemented in `tools/dr_drill.py`; all five checks pass.** Leg 3 is deliberately not built as a separate leg — its content (hash integrity, deliberate corruption, detection proof) is already enforced by the grade gate in `pubmed_archive.py` and exercised by Leg 1's self-test and Leg 4. A separate leg would restate rather than add.

Leg 4 required building the mechanism it tests: the grade contract existed on paper but nothing enforced it. `gate_record()` now runs inside the archive loader, so a record failing it is never available to excerpt verification at all — a gate that only reports is a gate standing beside an open door. Applying it retroactively rejected all 63 existing records for carrying no explicit grade, which is the correct answer: an artefact that does not declare what it is should not be trusted as evidence. They were re-fetched.

Leg 2 found a real defect on its first run — `--limit` was applied after the already-archived filter, so a resumed run fetched a *different* subset instead of completing the intended one, ending with more records than requested. Fixed, and the reason is recorded in the code. The archive now also writes atomically (temp file + `rename`), because a crash mid-write would otherwise leave a truncated record that a later resume skips as already done; the drill did not happen to hit that window, which is precisely why it should not be left to luck.

**Leg 1 — Archive rebuild (the one that matters most).** Point the pipeline at an empty scratch archive and rebuild from the repository's committed PMID list alone. Assert every PMID resolves, and that the re-fetched payloads reproduce the verbatim excerpts currently in the knowledge base **byte-for-byte**. This simultaneously tests the §3 cache-not-truth split and the frozen-baseline invariant. If a PMID cannot be rebuilt because it exists only in the archive, that is the exact failure this design is meant to prevent — a `FAIL`, not a warning.

**Leg 2 — Crash resume.** Kill the fetch process mid-run, re-dispatch the identical command, and assert it **resumes from its checkpoint rather than recomputing from zero**, and that already-fetched records are reused byte-identically rather than re-written.

⚠️ Use a **controlled `kill -9`, not a real reboot.** The sibling project reasoned this out and the reasoning applies here with more force: that node has a history of unresolved crashes, so rebooting to test crash-recovery risks triggering the very fault, and the resume path exercised is the same either way.

⚠️ **Design the crash window deliberately.** The sibling drill initially failed to test anything because the workload finished before the killer could fire — the run has to be slow enough that the kill lands mid-flight. Their fix was to enlarge the work items rather than to shorten the delay.

**Leg 3 — Integrity detection.** Corrupt one archived record on purpose — flip a byte, truncate a payload, or edit a stored abstract — and assert the checksum pass reports it. **This is the leg that tests the tester.** Per the standing rule that a detector must be proven against a known state, an integrity checker that has never been shown corruption has not been shown to work; "no problems found" from such a checker means nothing.

**Leg 4 — Grade enforcement.** Inject a local-model summary into the position where a raw payload belongs, and assert the pipeline refuses it. The `## 原文摘录` section is this project's core asset; the guard preventing a paraphrase from reaching it must be tested adversarially, not trusted.

### What building the legs taught, beyond the legs themselves

These generalise past this pipeline; a later drill or checker should be held to them.

**A detector must be shown a fault — and must also be shown a non-fault.** The existing rule (prove it catches what it exists to catch) has a twin that is easier to forget: prove it *admits* the clean case. A leg that rejects everything passes the first test and is worthless. Leg 4 therefore asserts an untouched control record is admitted before it asserts six forgeries are refused. Both halves are load-bearing: one rules out false negatives, the other false positives.

**A stronger defence and a regression can look identical from the test's seat.** After the grade gate went in, Leg 1's self-test failed — not because anything broke, but because a corrupted payload was now stopped at the gate rather than surfacing later as an excerpt mismatch. The fault was caught *earlier*, and the test only knew how to look *later*. Read that failure wrongly and the obvious "fix" is to weaken the gate. **When a test starts failing right after a defence is added, establish which of the two moved before changing either.** The durable form: findings are keyed by what was found, and an earlier-layer rejection counts as a finding rather than as silence.

**Put the gate on the path, not beside it.** `gate_record()` runs inside the archive loader, so a record that fails it is never available to excerpt verification at all. Had it been a separate audit command, every consumer would have been free to skip it, and one eventually would. A gate that only reports is a gate standing beside an open door.

**Layer the checks, because no single one survives a determined forgery.** Schema alone admits well-formed fabrication. Identity alone admits a genuine record relabelled as another paper. A self-declared grade is only a claim. The six attack shapes Leg 4 uses are worth reusing as a checklist whenever a new artefact type gains admission to the excerpt path: prose substituted for payload; the same with the hash recomputed; well-formed XML that is not the expected document type; a genuine payload attributed to the wrong identifier; a record self-declaring a lower grade; and hint text merged into the payload — that last one erasing the boundary rather than crossing it.

**Retroactive enforcement should reject, not grandfather.** Applying the gate to 63 already-fetched records rejected all of them for declaring no grade. Re-fetching was cheap; an exemption would have been permanent. An artefact that does not say what it is should not be read as evidence, including one that predates the rule.

### Traps this environment has already produced

Both were hit today, while merely *checking whether the node was free*. Both would have produced a confident wrong answer:

- **`nvidia-smi` is absent from the non-interactive `PATH` on this WSL2 node**, so a naive remote busy-check returns `command not found`. A detector that treats "command failed" as "nothing is running" will report the node idle **exactly when it cannot see**. Any busy-check must distinguish *measured idle* from *failed to measure*, and must fail loudly on the latter.
- **The notes described a hardware/model configuration that did not match the machine** — two 14B models that were never installed. Written infrastructure facts decay silently. Re-measure before depending on them; that is why §6 now carries a measurement date.

## 5. Operational rules, and the incidents behind them

Carried over from the sibling project's own failure log. Each of these cost real time there.

- **`runs ≠ works`.** A process that exits 0 has not thereby done anything. Verify the artefact, not the exit code.
- **Every automated task needs a monotonically increasing output counter, and a flatline is an alarm.** Three cycles producing nothing is a failure report, not a quiet success. The concrete case here: `rebuild_references.py` completing with zero records updated looks identical to "nothing needed updating" and to "the fetch silently broke".
- **Never swallow an error, and never `2>/dev/null`.** An unrecorded error is a lie told to whoever reads the log next. Every failure is recorded, including — especially — empty model returns.
- **Distinguish the two failure classes; they get opposite handling.**
  - *Retrieval failure* (a search or fetch errors out): **do not retry blindly, and never fabricate a substitute.** Record the failure, skip that query, and let the gap be visible.
  - *Model empty-return* (the local model produces nothing): **retry with a counter, then give up loudly.** An empty return is indistinguishable from "no relevant literature", which is why it must never be allowed to pass as a result.
- **Measure the failure *rate* before tuning.** A badly quantised local model returned empty on ~75% of requests; two days went into tuning input length, which the log later described as "chasing a coin-flip". Establish whether a fault is deterministic or probabilistic *first*.
- **A detector must be proven against a known state.** Do not trust "no problems found" from a checker that has never been shown a problem it should catch.
- **Normalise notation before reporting a mismatch.** Two false-positive classes have already been observed in numeric cross-checking: sources writing `38 per cent` where the body writes `38%`, and sources spelling numerals in words (`Eighty`, `One hundred seventeen`) where the body uses digits. Both are expected — excerpts keep the source's own wording, as they must. A checker that flags them produces noise, and **a checker producing noise is a checker nobody reads**, which fails in the same direction as one that reports nothing. Note that `extract_source_excerpts.py` has the mirror image of this blind spot, documented in its own output: it *misses* figures the source spells out.
- **Every incident must leave behind the check that would have caught it.** Recording a fix without adding the detector is not finishing. And a root cause that has not been demonstrated with a probe is a hypothesis — write it as one.

## 5a. Account for every input; label every output by grade

Two patterns worth copying exactly, both from the sibling project's reading loop.

**Nothing is dropped silently.** Every input item must end in exactly one recorded state — accepted, already-seen, or unusable-with-a-stated-reason. If a cap is hit, the overflow is reported rather than truncated away. A pipeline that quietly discards is indistinguishable from one that found nothing, and the failure only surfaces much later, as a gap nobody can explain.

**Output carries its own grade, visibly.** When the full path is unavailable — no API budget, model down, node busy — the sibling pipeline still produces something, but stamps it `[extractive digest — NOT a deep-read]`: sentences pulled mechanically by code, with nothing generated. Copy this. For catmed the grades are roughly:

| Grade | What it means | May it enter `## 原文摘录`? |
|---|---|---|
| Raw API payload | Bytes as PubMed returned them | **Yes** — this is the only thing that may |
| Extractive selection | Sentences cut from the payload by code, unmodified | Only after Claude confirms the selection |
| Local relevance hint | A local model's opinion about a paper | **Never** |

The point is not the taxonomy; it is that an artefact must never be able to travel without its grade attached. Downgrading silently is how a routing hint ends up looking like evidence.
- **Yield to real compute.** The node is shared with other long-running work. Back off rather than compete.
- **Detect node-busy via `nvidia-smi` utilisation, not `pgrep -f`** — a `pgrep` pattern can match the checking process itself and report busy forever.
- **Stage scripts with `ssh 'cat >'` and a quoted heredoc, not `rsync`.** `rsync` was observed returning `rc=0` while silently failing to deliver a file.
- **The node has an unresolved recurring BSOD (0x9F).** Any loop must be resumable from a checkpoint and must assume it can die mid-run.

## 6. Node facts

⚠️ **Host addresses, usernames, and keys do not belong in this repository — it is public.** They live in the operator's local environment and in the sibling project's private notes. Read them from there at run time; do not transcribe them here, and do not let them reach a commit, a log file, or an error message that gets committed.

What is safe to record, because it constrains design rather than granting access. **Measured on the node 2026-07-20, not taken from notes** — the sibling project's memory files described a planned configuration that does not match what is installed:

- Hardware: RTX 3080 Laptop, 16 GB. At the time of measurement: **utilisation 0%, but 5.5 GB of VRAM already resident** — that is the local model server holding a loaded model, not a competing job. Usable headroom is therefore ~10.8 GB, not 16.
- **Installed models are a 9B and a 7B. There is no 14B on the node.** The notes claimed two 14B tiers; they were never installed. Any design assuming 14B capability is designing against a machine that does not exist.
- **The resident 9B is a known-bad build.** The sibling project's log records it returning empty on roughly 75% of requests for digest-style prompts, with two days lost tuning input length before the cause was found. Its stated fix was "a non-broken model later" — that replacement has not happened. Its context window is also only 4096 tokens.
- Access is over a private mesh network; the two machines use **different SSH usernames**, which has caused a real misconfiguration before. Confirm both before assuming either.
- The node runs **WSL2**. `nvidia-smi` is not on the default non-interactive `PATH`; it lives under the WSL library directory and must be added explicitly.
- A difficulty router already exists in the sibling project (`compute-node/runs/local-router/`), classifying tasks 1–5 and escalating only the hardest. Read it before writing anything new.

> **Why this does not break the design — and is in fact the argument for it.** A pipeline that asked the local model to summarise or judge would have walked straight into a 75%-empty failure rate on a 4096-token context. This one asks it to move bytes and, at most, apply a crude filter that degrades gracefully to keyword matching. **The architecture is deliberately insensitive to local model quality, because no judgement was delegated to it.** Treat any local model output as optional; the pipeline must remain correct with the model switched off entirely.

## 7. Isolation from the sibling project

catmed builds its **own** pipeline rather than extending the sibling's `reading_loop.py`. This is deliberate:

- catmed is a **public** repository with privacy redlines; the sibling's `state/` tree contains unrelated research material. Shared state would eventually leak one into the other.
- The two have different verbatim requirements. The sibling extracts structured facts; catmed extracts **quotable sentences**, where a single normalised space is a defect.
- Coupling would make catmed's citation discipline depend on a codebase that does not share it.

Borrow the patterns and the scar tissue. Do not share the code or the state directory.

## 7a. Choosing what to research next

Established 2026-07-20, after a survey of documented gaps in feline medicine.

**Separate the data gap from the integration gap, and only take the second.** "Nobody has run this study" is not addressable here — no amount of retrieval creates evidence. "The evidence exists but sits in two literatures nobody reads together" is exactly addressable. Before starting a topic, say which kind it is; if it is the first, the honest output is a recorded absence, not a file.

**Prefer topics where two specialties each hold half.** The strongest entries this project has produced come from that shape — an abstract contradicting its own results section, an imaging report and a histology report read blind to each other, hyperthyroidism and kidney disease masking one another across endocrine and renal clinics. The value is in the join, which is where nobody is standing.

**A stated need beats an inferred one.** The profession publishes its own diagnoses of what is missing (`evidence-to-practice-gap.md`). Building against a documented request is defensible in a way that building against a guess is not.

**Prefer gaps the knowledge base itself flagged.** Each file ends with what it could not close. Those are pre-scoped, already justified, and immune to the charge of picking convenient topics.

**Order by how often the question is faced, not by how interesting it is.** This repository grew from one rare tumour, which was right for its origin and wrong as a plan: the commonest chronic diseases of older cats had no entry at all until deliberately addressed.

### ⚠️ Read the whole abstract before writing from it

`screen.py show` prints a full record; a shell pipeline that truncates the display does not truncate the source, but it does truncate what the writer sees. Writing the hypertension entry from a display-clipped abstract produced two defects in one pass: figures cited in the body whose sentences never reached the excerpt block, and — worse — a claim in the body that the unread remainder **contradicted**. The entry had argued fundic examination was the easier alternative to a blood pressure cuff; the same abstract went on to report that 73.1% of practitioners struggle to interpret ocular findings.

**Before writing a section, confirm the abstract was read to its end.** The numeric cross-check catches the first defect (a figure with no excerpt) but is blind to the second: nothing flags a conclusion the source refutes in a sentence you never saw.

### ⚠️ A web page is not a source

Page-fetching tools return a *model's summary* of a page, not the page. Its wording is not the author's wording, and its figures have passed through a paraphrase. **Nothing obtained that way may enter `## 原文摘录` or be quoted as verbatim.** Use web search to find out *what to look for*; then retrieve the record properly and quote from that. When a figure exists only in a full text that was read through such a tool, cite nothing and record that the check was not performed — as `evidence-to-practice-gap.md` §2 does.

## 8. Before building — open questions

1. ~~Is the node free?~~ **Resolved 2026-07-20 by measurement**: compute idle (0% utilisation), ~10.8 GB VRAM headroom, no competing job. Re-check before each run — and per §4a, distinguish *measured idle* from *failed to measure*.
2. ~~Where does the archive live?~~ **Resolved: outside the repository**, with the rebuild inputs committed inside it (§3).
3. ~~Measure the token cost.~~ **Done 2026-07-20.** 1.9× on the cited set, 1.8× on a candidate pool — and the discarded-candidate saving I expected to be larger turned out to be mostly unavailable, because taking it costs recall (§1). The bankable figure is ~1.8–1.9×, from lossless field trimming.
4. Decide whether the local model is used at all in v1. Given that the installed 9B is a known-bad build with a 4096-token context, the honest default is **build the pipeline with no local model**, prove the deterministic path end to end, and add a model only if a measured need survives that. A pipeline that works with the model switched off is the one worth having anyway (§6).
