# catmed

**Owner-facing feline medicine guides where every figure traces to a published sentence — plus the verified knowledge base behind them, and the tooling that proves the citations on every commit.**

[![citation integrity](https://github.com/polyketide/catmed/actions/workflows/citation-integrity.yml/badge.svg)](https://github.com/polyketide/catmed/actions/workflows/citation-integrity.yml)
[![licence: MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

[English](#english) · [日本語](#日本語) · [中文](#中文) · [Contributing](CONTRIBUTING.md) · [项目简介](docs/PROJECT-PITCH.md)

> **Every figure in this repository is checked against PubMed on every commit.**
> CI starts with no literature archive at all, rebuilds it from the PMIDs the corpus
> cites, and requires each quoted sentence to be a byte-exact substring of the
> record — then corrupts one on purpose to prove the checker can still fail.
> Currently **229 papers, 823 verbatim excerpts checked, 0 unmatched** across the
> knowledge base and the owner guides alike. (A further 82 excerpts come from full
> text rather than abstracts and are marked as not verifiable in CI, rather than
> counted as passing.)
> Contributions welcome in English, 中文 or 日本語 — see [CONTRIBUTING.md](CONTRIBUTING.md).

**Read it here → https://polyketide.github.io/catmed/** (中文，手机可读). The guides are the product. The agents are how they get made.

> ⚠️ **Not medical advice.** Everything here is literature-referenced material for discussing options with a licensed veterinarian. It does not diagnose, prescribe, or replace your vet.
> ⚠️ **医療アドバイスではありません。** 本リポジトリの内容は、獣医師と選択肢を検討するための文献参照資料です。診断・処方・獣医師の代替にはなりません。
> ⚠️ **不是医疗建议。** 所有内容是供你与执业兽医共同审阅的循证参考，不下诊断、不开处方、不能替代兽医。

```
guides/                    # THE PRODUCT — owner-facing, Chinese, Markdown + PDF
  ├── feline-emergency-owner-guide.zh.{md,pdf}          # start here: is this an emergency?
  ├── feline-ckd-owner-guide.zh.{md,pdf}                # every figure carries an inline PMID
  ├── feline-lymphoma-all-types-owner-guide.zh.{md,pdf}
  └── feline-nasal-lymphoma-owner-guide.zh.{md,pdf}

knowledge-base/            # 21 analysis files, English + some 中文, each with verbatim excerpts
  ├── README.md / README.zh.md   # ← GENERATED clinician index. Start here if you are a vet.
  └── …                          # topics listed below

.claude/agents/            # agent definitions (source of truth)
  ├── medical.md                 # research agent: full tools, unrestricted topics
  └── cat-owner-triage.md        # owner-facing: `tools: Read, Grep, Glob` — CANNOT search
                                 #   literature, must answer from the KB or decline
agents/                    # generated platform-neutral exports of the above
docs/                      # engineering SOPs — the methodology record
  ├── LITERATURE-PIPELINE-SOP.md # every defect found, and the rule it produced
  ├── kb-exceptions.md           # suppressed checks, each with a written reason
  ├── RELEASING.md · PROJECT-PITCH.md · release-notes-v0.1.0.md
tools/                     # standard library only, Python 3.9+, nothing to install
  ├── pubmed_archive.py          # fetch / verify the raw record archive
  ├── dr_drill.py                # every excerpt vs its source, + a self-test that must fail
  ├── check_kb_hygiene.py        # 10 structural checks (orphans, staleness, PII, xrefs…)
  ├── search_log.py              # record what was searched and rejected, so a NEGATIVE claim has evidence
  ├── corpus_watch.py            # watch a private owner-community corpus for coverage gaps
  ├── build_kb_index.py          # regenerate the clinician index
  ├── build_site.py              # static site
  ├── export_agents.py           # regenerate the portable agent prompts
  ├── rebuild_references.py · extract_source_excerpts.py · attribution_candidates.py
  ├── fetch_fulltext.py · screen.py · render_markdown.py
  ├── lab_reference_plot.py      # labs vs reference range; ships with no data
  └── test_tools.py              # unit tests for the checkers themselves
.github/                   # CI, plus issue templates: challenge a figure · clinical review · propose coverage
```

---

## What is covered

The knowledge base began as feline oncology and is no longer only that — coverage
follows what cats actually present with, which is itself a sourced question
(`feline-disease-frequency.md`). **The generated index at
[`knowledge-base/README.md`](knowledge-base/README.md) is the authoritative list**;
this is the shape of it:

| | Files |
|---|---|
| **Oncology** | lymphoma treatment currency · does doxorubicin help cats (COP vs CHOP) · antineoplastic drug toxicity · targeted & immunotherapy evidence · G-CSF and chemotherapy neutropenia · response assessment & drug resistance · treatment-related harm and the trade-off · PARR clonality: what a negative means · upper-airway response-marker validity · oncology literature survey |
| **Common chronic disease** | chronic kidney disease · hyperthyroidism × kidney disease (EN + 中文) · feline hypertension · HCM emerging therapy |
| **Acute & supportive** | emergency triage red flags · supportive and palliative care · assisted feeding and feeding tubes · acid suppression (omeprazole) · blood types and transfusion compatibility |
| **How the field and owners actually work** | feline disease frequency · evidence-to-practice gap · working with a specialist (中文) · owner vernacular lexicon (中文) · Chinese practice context (中文) |

---

## What this actually is, and what it is not

**The product is the documents. The agents are production tooling.**

That is worth stating plainly because the repository layout suggests otherwise, and because the obvious reading of "a medical AI agent" is wrong here in a way that matters.

Nothing valuable in this project came from a chat exchange. It came from slow, adversarial, verified passes over literature — finding twelve misattributed figures, catching a verification pass that had *deleted three real findings* as unsourced, discovering that the checker was monolingual while half the corpus is Chinese, and discovering that the most rigorously verified material was the least read while the only material with readers had no verification at all. **None of that is a thing you can ask a chatbot for.** It is what a pipeline produces when it is run against itself repeatedly.

So the layers are:

| Layer | Who it is for | Where |
|---|---|---|
| **Owner guides** | cat owners, no medical background | [the site](https://polyketide.github.io/catmed/), and `guides/` |
| **Knowledge base** | vets, researchers | `knowledge-base/` — with verbatim excerpts and explicit gaps |
| **Agents** | maintainer, contributors | `.claude/agents/` — how the above gets made and checked |

### The owner-facing agent is deliberately crippled, and this is the most important design decision here

`cat-owner-triage.md` declares `tools: Read, Grep, Glob`. It cannot search PubMed, cannot browse, cannot run commands. It answers from the knowledge base or it declines.

**This replaced a rule that did not work.** The same restriction was first written into the `medical` agent as prose — a dedicated section, then promoted to a rule explicitly outranking every other rule in the file. It was tested both times with one question about a diabetic cat, a condition the knowledge base does not cover. **Both times the agent searched PubMed live and answered in full.** On the second attempt it wrote *"this project has no diabetes file"* and then answered anyway.

It was not malfunctioning. The rest of the definition asks — correctly — for thoroughness toward a frightened owner, and no sentence outranks that pull in practice. So the restriction moved out of the prose and into the tool list, where compliance is not a judgement call.

**The general form of that lesson runs through this whole repository: a constraint enforced by the thing it constrains is not a constraint.** The citation discipline became real when CI enforced it rather than the maintainer remembering. The scope limit became real when the capability was removed rather than requested. See `docs/LITERATURE-PIPELINE-SOP.md` §3f.

**Why cripple it at all?** Because a model that answers fluently about any feline disease is indistinguishable, to the owner reading it, from one that answers correctly — and this project's single distinguishing property is that it says where the evidence runs out. Sounding limited is the feature.

---

## What CI enforces

Everything below runs on every push, from an **empty archive** — which also proves
the local cache is disposable and checks the excerpts against what PubMed serves
*today*, not what it served when they were written.

```bash
python3 tools/test_tools.py             # unit tests for the checkers themselves
python3 tools/build_kb_index.py --check # the clinician index still matches the corpus
python3 tools/export_agents.py --check  # portable agent prompts have not drifted
python3 tools/check_kb_hygiene.py       # 10 checks: orphan citations, empty blocks,
                                        #   coverage, stale PDF, stale translation,
                                        #   agent sync, index, PII, doc xrefs, search log
python3 tools/pubmed_archive.py fetch   # rebuild the archive from the cited PMIDs
python3 tools/pubmed_archive.py verify  # archive integrity
python3 tools/dr_drill.py leg1          # every excerpt vs its source
python3 tools/dr_drill.py self-test     # corrupt one on purpose — the checker MUST fail
```

The last line is the one that matters: **a check that has never been observed to
fail is not evidence of anything.**

Two rules worth stealing even if you take nothing else:

- **Generated, never typed.** Reference lists, the clinician index, the portable prompts and the site are produced by scripts from verified sources. Three of seven hand-typed reference entries were once wrong.
- **A negative claim needs a documented search.** "No feline evidence exists for X" is itself a claim. `search_log.py` records what was searched and rejected, so an absence has evidence behind it rather than an assumption.

---

## English

### What this is

**A set of owner-facing feline medicine guides in which every figure traces back to a published sentence, plus the knowledge base and tooling that keep that true.**

It began around feline oncology and now covers much of what cats actually present with — kidney disease, hyperthyroidism, hypertension, cardiac disease, emergency triage, supportive care — with each topic chosen from sourced disease-frequency data rather than intuition.

Two Claude Code sub-agents are included as production tooling: a research agent for cross-species evidence work (given a veterinary question it goes looking for the corresponding human-medicine evidence, and vice versa, while flagging the limits of any extrapolation), and a deliberately tool-restricted owner-facing agent that must answer from the knowledge base or decline.

Their value is not that they "know more medicine." It is a set of disciplines that stop them from making things up.

### The citation discipline

This is the part worth stealing even if you never use the agents.

**Literature is recorded in its original language, verbatim — the content, not just the title.**

A knowledge base written in one language about literature written in another has a silent failure mode: the figures survive translation, but *what the authors actually said* exists only as the author's rendering. That rendering cannot be quoted, cannot be checked, and drift between it and the source is invisible — there is nothing to compare against.

So every document here carries a **source excerpts** section: for each cited paper, the verbatim sentences that carry the load-bearing figures, untranslated. The prose is interpretation; the excerpt is evidence.

The tooling enforces it:

| Script | What it does |
|---|---|
| `rebuild_references.py` | Regenerates each reference entry from the PubMed record keyed by PMID, rather than editing it. Title, ISO journal abbreviation, volume/issue/pages, DOI verbatim. Author commentary is demoted to a trailing note so it can never be mistaken for part of the title. |
| `extract_source_excerpts.py` | Pulls the source sentences carrying each cited figure, and **reports figures the document cites that do not appear in the source** — those may come from full text the abstract omits, or may be wrong, but either way must not pass as verified. |
| `search_log.py` | Records what was searched and what was rejected, so that a **negative** claim ("no feline study exists") carries evidence rather than an assumption. |
| `render_markdown.py` | Standard-library Markdown → print-ready HTML with GitHub-compatible anchors, for PDF via headless Chrome. No toolchain to install. |

**What this actually caught**, on a corpus that is now ~229 papers:

- A **PMID pointing at an unrelated dental-informatics paper**, used as the source for a rescue-chemotherapy protocol. Every figure attached to it was correct; only the identifier was wrong. Nothing short of returning to the source would have surfaced this.
- A **percentage attributed to the wrong clinical sign** — a cough frequency recorded as a dysphonia frequency, shifting a reported range by half.
- A **response-rate range that did not exist in the cited paper at all**.
- Wrong years, wrong author initials, a wrong first author, and truncated titles throughout.
- One paper whose **abstract contradicts its own results section** on whether a covariate affected survival.
- Two PMIDs transcribed from memory rather than from a tool result — one off by a single digit — caught only because adding the verbatim excerpts forced a return to the source.

The point is not that these were careless mistakes. It is that reading carefully does not catch them, and returning to the source does.

### Reusing the agents

Drop `.claude/agents/medical.md` into any project's `.claude/agents/`. It expects the bio-research MCP servers (PubMed, ClinicalTrials, ChEMBL, Consensus) and loads them on demand. Platform-neutral exports for other agentic tools live in `agents/`.

⛔ **Before deploying `cat-owner-triage`, read the host requirement at the top of `agents/cat-owner-triage.prompt.md`.** Its safety property is the *tool restriction*, not the prose — the same rule written as prose failed twice on the same test. A platform that cannot restrict tools must not present that prompt to cat owners.

The agents' own rules are in those files. In brief: search rather than recall for anything numeric; label every claim as verified / inferred / extrapolated / unknown; trace which premises came from the user versus which the agent filled in itself; never prescribe; treat emergency recognition as outranking diagnostic completeness.

---

## 日本語

### これは何か

**すべての数値が公表論文の一文まで遡れる、猫の飼い主向け医療ガイド**と、それを支える検証済みナレッジベース、および引用の正確性を毎コミット機械的に保証するツール群です。

出発点は猫の腫瘍学でしたが、現在は猫が実際に罹る疾患の多く — 腎臓病・甲状腺機能亢進症・高血圧・心疾患・救急トリアージ・支持療法 — を扱います。扱う topic は勘ではなく、**出典のある疾患頻度データ**から選ばれています。

制作ツールとして Claude Code サブエージェントを 2 つ同梱しています。獣医学 × 人医学を横断する調査用エージェント（獣医学の問いには対応する人医学のエビデンスを探しに行き、逆方向も同様に行い、種を跨いだ外挿の限界を必ず明示する）と、**意図的にツールを制限した**飼い主向けエージェント（ナレッジベースから答えるか、答えられないと述べるかのいずれかしかできない）です。

これらの価値は「医学に詳しいこと」ではなく、**自らの捏造を防ぐ規律**にあります。

### 引用の規律

エージェントを使わない場合でも、この部分だけは持ち帰る価値があります。

**文献は原語のまま、逐語的に記録する — タイトルだけでなく「内容」を。**

ある言語で書かれたナレッジベースが別言語の文献を扱うとき、静かな失敗様式が生じます。数値は翻訳を生き延びますが、**著者が実際に何と述べたか**は執筆者の訳文としてしか残りません。訳文は引用できず、検証もできず、原文との乖離は不可視です（比較対象が存在しないため）。

そこで本リポジトリの全文書には **原文抜粋（source excerpts）** の節があります。引用した各論文について、結論を担う文を未翻訳のまま逐語収録しています。本文の記述は解釈であり、抜粋が証拠です。

ツールがこれを機械的に強制します：

| スクリプト | 機能 |
|---|---|
| `rebuild_references.py` | 参考文献項目を編集するのではなく、PMID を鍵に PubMed レコードから**再生成**。タイトル・ISO 誌名略記・巻号頁・DOI を逐語採録。執筆者の注記は末尾に降格し、タイトルの一部と誤認されない位置に置く。 |
| `extract_source_excerpts.py` | 引用された各数値を担う原文の文を抽出し、さらに**本文が引用しているが原文に存在しない数値を報告**する。全文にのみ記載がある場合も、誤りである場合もあるが、いずれにせよ「検証済み」として通してはならない。 |
| `search_log.py` | 何を検索し何を棄却したかを記録する。これにより「猫での報告は存在しない」という**否定的主張**が、思い込みではなく証拠を伴う。 |
| `render_markdown.py` | 標準ライブラリのみで Markdown → 印刷用 HTML（GitHub 互換アンカー付き）。headless Chrome で PDF 化。追加インストール不要。 |

**現在約 229 件の文献からなるコーパスに適用して、実際に検出されたもの：**

- 救援化学療法プロトコルの出典として記載されていた **PMID が、無関係な歯科情報学の論文を指していた**。付随する数値はすべて正しく、識別子のみが誤り。原文に戻る以外に発見手段はなかった。
- **臨床徴候の取り違え** — 咳嗽の頻度を発声障害の頻度として記録しており、報告範囲が半分ずれていた。
- **引用先論文に存在しない奏効率の範囲**。
- 発行年・著者イニシャル・筆頭著者の誤り、およびタイトルの切り詰めが多数。
- **抄録と結果セクションが互いに矛盾している**論文が 1 件（ある共変量が生存に影響したか否かについて）。
- ツールの出力ではなく**記憶から転記された PMID が 2 件**（うち 1 件は 1 桁違い）。逐語抜粋を追加する作業が原文への回帰を強制したことでのみ発覚した。

これらが不注意による誤りだという話ではありません。**注意深く読んでも発見できず、原文に戻れば発見できる**という点が要点です。

### エージェントの再利用

`.claude/agents/medical.md` を任意のプロジェクトの `.claude/agents/` に置くだけで動作します。bio-research 系 MCP サーバ（PubMed / ClinicalTrials / ChEMBL / Consensus）を必要時に読み込みます。他の agentic ツール向けの汎用エクスポートは `agents/` にあります。

⛔ **`cat-owner-triage` を配備する前に、`agents/cat-owner-triage.prompt.md` 冒頭のホスト要件を必ず読んでください。** その安全性は散文ではなく**ツール制限**によって担保されています（同じ規則を散文で書いた場合、同一のテストで 2 回とも失敗しました）。ツールを制限できないプラットフォームで、このプロンプトを飼い主に提示してはなりません。

規律の詳細は各ファイル内に記載。要約すると：数値に関わる事項は記憶ではなく検索で確認する／全主張を【検証済】【推論】【外挿】【不明】に分類する／どの前提が利用者由来でどれが自らの補完かを追跡する／処方は行わない／診断の完全性より救急認識を優先する。

---

## 中文

### 这是什么

**一套给猫主人看的医疗指南，其中每一个数字都能回溯到某篇论文里的某一句原文**；外加支撑它的知识库，以及每次提交都机械核对引用的工具链。

起点是猫的肿瘤学，现在已经覆盖猫真正会得的大部分病——肾病、甲亢、高血压、心脏病、急诊分诊、支持照护。选题不是凭感觉，而是依据**有出处的疾病频率数据**（`feline-disease-frequency.md`）。

作为制作工具，附带两个 Claude Code 子代理：一个**跨兽医与人医**的研究代理（遇到兽医问题会主动去找对应的人医证据，反之亦然，并强制标注跨物种外推的局限），以及一个**被刻意限制工具**的主人面向代理——它只能从知识库回答，否则就说自己答不了。

它们的特点不在"更懂医学"，而在**一套防止自己胡说的纪律**。

### 引用纪律

即使你不用这两个 agent，这部分也值得拿走。

**文献按原语言逐字记录——记的是「内容」，不只是标题。**

用一种语言写、引用另一种语言文献的知识库有一个静默的失败模式：数字能活过翻译，但**作者到底说了什么**只剩下转述。转述无法被引用、无法被核对，而它与原文之间的漂移是**不可见**的——因为没有可比对的对象。

所以本仓库每份文档都带 **原文摘录（source excerpts）** 一节：对每篇引用的论文，逐字收录承载结论的句子，不翻译。正文是**解读**，摘录才是**证据**。

工具把这条纪律机械化：

| 脚本 | 作用 |
|---|---|
| `rebuild_references.py` | 参考文献条目不是"修改"而是按 PMID 从 PubMed 记录**重建**。标题、ISO 期刊缩写、卷期页、DOI 逐字采录。作者注解降级到末尾，永远不会被误认为标题的一部分。 |
| `extract_source_excerpts.py` | 抽取承载每个引用数字的原文句子，并**报告正文引用了但原文中不存在的数字**——它们可能出自摘要不含的全文，也可能有误，但无论如何都不该以"已核实"的面目通过。 |
| `search_log.py` | 记录检索了什么、排除了什么，让**否定式结论**（"猫身上没有这方面研究"）也带着证据，而不是一个假设。 |
| `render_markdown.py` | 纯标准库 Markdown → 印刷级 HTML（GitHub 兼容锚点），配 headless Chrome 出 PDF。零依赖安装。 |

**在目前约 229 篇文献的语料上实际抓到的：**

- 一个**指向无关牙科信息学论文的 PMID**，却被当作救援化疗方案的出处。挂在它名下的数据**全部正确**，只有编号错了。不回原文永远发现不了。
- 一处**临床征象张冠李戴**——把咳嗽的发生率记成了发声障碍的发生率，导致报告区间整体偏移一半。
- 一个**在被引论文中根本不存在**的应答率区间。
- 若干错误的年份、作者缩写、第一作者，以及大量被截短的标题。
- 一篇论文的**摘要与其自身结果部分互相矛盾**（关于某协变量是否影响生存）。
- 两个**凭记忆转写、而非从工具结果复制的 PMID**（其中一个只差一位数）——只因为补写逐字摘录强制回到原文，才被发现。

要点不是"这些是粗心造成的错误"，而是：**认真读发现不了，回原文才能发现。**

### 复用这两个 agent

把 `.claude/agents/medical.md` 放进任意项目的 `.claude/agents/` 即可。它按需加载 bio-research 系列 MCP 工具（PubMed / ClinicalTrials / ChEMBL / Consensus）。给其他 agentic 工具用的通用版导出在 `agents/`。

⛔ **部署 `cat-owner-triage` 之前，务必先读 `agents/cat-owner-triage.prompt.md` 顶部的宿主要求。** 它的安全性来自**工具限制**而不是文字——同一条规则写成文字时，在同一个测试上**失败了两次**。无法限制工具的平台，不得把该提示词提供给猫主人。

具体纪律写在各自文件里。简述：涉及数值一律检索而非凭记忆；每条结论标注【已查证】【推断】【外推】【未知】；追溯哪些前提来自用户、哪些是自己填的；不开处方；急症识别优先于诊断完美。

---

## License

MIT. See [LICENSE](LICENSE).

Literature quoted in this repository belongs to its respective publishers; excerpts are limited to the sentences needed to verify a specific claim, each attributed with PMID and DOI.
