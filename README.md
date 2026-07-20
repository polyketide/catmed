# catmed

**An evidence-first sub-agent for veterinary × human medical analysis, a cited feline-medicine knowledge base, and the tooling that keeps its citations honest.**

[![citation integrity](https://github.com/polyketide/catmed/actions/workflows/citation-integrity.yml/badge.svg)](https://github.com/polyketide/catmed/actions/workflows/citation-integrity.yml)
[![licence: MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

[English](#english) · [日本語](#日本語) · [中文](#中文) · [Contributing](CONTRIBUTING.md)

> **Every figure in this repository is checked against PubMed on every commit.**
> CI starts with no literature archive at all, rebuilds it from the PMIDs the
> knowledge base cites, and requires each quoted sentence to be a byte-exact
> substring of the record — then corrupts one on purpose to prove the checker
> can still fail. Currently **180 papers, 623 verbatim excerpts, 0 unmatched** — knowledge base and owner guides alike.
> Contributions welcome in English, 中文 or 日本語 — see [CONTRIBUTING.md](CONTRIBUTING.md).

> ⚠️ **Not medical advice.** Everything here is literature-referenced material for discussing options with a licensed veterinarian. It does not diagnose, prescribe, or replace your vet.
> ⚠️ **医療アドバイスではありません。** 本リポジトリの内容は、獣医師と選択肢を検討するための文献参照資料です。診断・処方・獣医師の代替にはなりません。
> ⚠️ **不是医疗建议。** 所有内容是供你与执业兽医共同审阅的循证参考，不下诊断、不开处方、不能替代兽医。

```
.claude/agents/medical.md              # the sub-agent definition
knowledge-base/                        # analysis-facing notes (English, with verbatim source excerpts)
  ├── feline-disease-frequency.md        # what cats present with and die of — decides what gets written next
  ├── chronic-kidney-disease.md
  ├── hyperthyroidism-and-kidney-disease.md
  ├── feline-hypertension.md
  ├── emergency-triage-red-flags.md
  ├── supportive-and-palliative-care.md
  ├── evidence-to-practice-gap.md
  ├── antineoplastic-drug-toxicity.md
  ├── targeted-and-immunotherapy-evidence.md
  ├── feline-oncology-literature-survey.md
  └── upper-airway-response-marker-validity.md
guides/                                # owner-facing guides, Markdown + PDF (Chinese)
  ├── feline-ckd-owner-guide.zh.{md,pdf}         # every figure carries an inline PMID
  ├── feline-lymphoma-all-types-owner-guide.zh.{md,pdf}
  └── feline-nasal-lymphoma-owner-guide.zh.{md,pdf}
docs/                                  # engineering SOPs
  └── LITERATURE-PIPELINE-SOP.md       # offloading literature retrieval to a local node (design, not yet built)
tools/                                 # citation-integrity and rendering scripts
  ├── rebuild_references.py
  ├── fetch_fulltext.py
  ├── extract_source_excerpts.py
  └── render_markdown.py
```

---

## English

### What this is

A Claude Code sub-agent for cross-species evidence-based analysis: given a veterinary question it goes looking for the corresponding human-medicine evidence (mechanism, pharmacology, dosing principles) and vice versa, while flagging the limits of any cross-species extrapolation.

Its value is not that it "knows more medicine." It is a set of disciplines that stop it from making things up.

### The citation discipline

This is the part worth stealing even if you never use the agent.

**Literature is recorded in its original language, verbatim — the content, not just the title.**

A knowledge base written in one language about literature written in another has a silent failure mode: the figures survive translation, but *what the authors actually said* exists only as the author's rendering. That rendering cannot be quoted, cannot be checked, and drift between it and the source is invisible — there is nothing to compare against.

So every document here carries a **source excerpts** section: for each cited paper, the verbatim sentences that carry the load-bearing figures, untranslated. The prose is interpretation; the excerpt is evidence.

The tooling enforces it:

| Script | What it does |
|---|---|
| `rebuild_references.py` | Regenerates each reference entry from the PubMed record keyed by PMID, rather than editing it. Title, ISO journal abbreviation, volume/issue/pages, DOI verbatim. Author commentary is demoted to a trailing note so it can never be mistaken for part of the title. |
| `extract_source_excerpts.py` | Pulls the source sentences carrying each cited figure, and **reports figures the document cites that do not appear in the source** — those may come from full text the abstract omits, or may be wrong, but either way must not pass as verified. |
| `render_markdown.py` | Standard-library Markdown → print-ready HTML with GitHub-compatible anchors, for PDF via headless Chrome. No toolchain to install. |

**What this actually caught**, on a corpus of ~150 references:

- A **PMID pointing at an unrelated dental-informatics paper**, used as the source for a rescue-chemotherapy protocol. Every figure attached to it was correct; only the identifier was wrong. Nothing short of returning to the source would have surfaced this.
- A **percentage attributed to the wrong clinical sign** — a cough frequency recorded as a dysphonia frequency, shifting a reported range by half.
- A **response-rate range that did not exist in the cited paper at all**.
- Wrong years, wrong author initials, a wrong first author, and truncated titles throughout.
- One paper whose **abstract contradicts its own results section** on whether a covariate affected survival.

The point is not that these were careless mistakes. It is that reading carefully does not catch them, and returning to the source does.

### Reusing the agent

Drop `.claude/agents/medical.md` into any project's `.claude/agents/`. It expects the [bio-research MCP servers](https://github.com/anthropics/claude-code) (PubMed, ClinicalTrials, ChEMBL, Consensus) and loads them on demand.

The agent's own rules are in that file. In brief: search rather than recall for anything numeric; label every claim as verified / inferred / extrapolated / unknown; trace which premises came from the user versus which it filled in itself; never prescribe; treat emergency recognition as outranking diagnostic completeness.

---

## 日本語

### これは何か

獣医学 × 人医学を横断してエビデンスを検証する Claude Code サブエージェントと、出典付きの猫腫瘍学ナレッジベース、そして引用の正確性を担保するツール群です。

獣医学の問いに対しては対応する人医学のエビデンス（機序・薬理・用量原則）を探しに行き、逆方向も同様に行います。その際、種を跨いだ外挿の限界を必ず明示します。

このエージェントの価値は「医学に詳しいこと」ではなく、**自らの捏造を防ぐ規律**にあります。

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
| `render_markdown.py` | 標準ライブラリのみで Markdown → 印刷用 HTML（GitHub 互換アンカー付き）。headless Chrome で PDF 化。追加インストール不要。 |

**約 150 件の参考文献に適用して実際に検出されたもの：**

- 救援化学療法プロトコルの出典として記載されていた **PMID が、無関係な歯科情報学の論文を指していた**。付随する数値はすべて正しく、識別子のみが誤り。原文に戻る以外に発見手段はなかった。
- **臨床徴候の取り違え** — 咳嗽の頻度を発声障害の頻度として記録しており、報告範囲が半分ずれていた。
- **引用先論文に存在しない奏効率の範囲**。
- 発行年・著者イニシャル・筆頭著者の誤り、およびタイトルの切り詰めが多数。
- **抄録と結果セクションが互いに矛盾している**論文が 1 件（ある共変量が生存に影響したか否かについて）。

これらが不注意による誤りだという話ではありません。**注意深く読んでも発見できず、原文に戻れば発見できる**という点が要点です。

### エージェントの再利用

`.claude/agents/medical.md` を任意のプロジェクトの `.claude/agents/` に置くだけで動作します。bio-research 系 MCP サーバ（PubMed / ClinicalTrials / ChEMBL / Consensus）を必要時に読み込みます。

規律の詳細は同ファイル内に記載。要約すると：数値に関わる事項は記憶ではなく検索で確認する／全主張を【検証済】【推論】【外挿】【不明】に分類する／どの前提が利用者由来でどれが自らの補完かを追跡する／処方は行わない／診断の完全性より救急認識を優先する。

---

## 中文

### 这是什么

一个**跨兽医与人医的循证分析** Claude Code 子代理，附带一套带原文出处的猫肿瘤知识库，以及保证引用可核对的工具。

遇到兽医问题会主动去找对应的人医证据（机制、药理、剂量原则），反之亦然，并强制标注跨物种外推的局限。

它的特点不在"更懂医学"，而在**一套防止自己胡说的纪律**。

### 引用纪律

即使你不用这个 agent，这部分也值得拿走。

**文献按原语言逐字记录——记的是「内容」，不只是标题。**

用一种语言写、引用另一种语言文献的知识库有一个静默的失败模式：数字能活过翻译，但**作者到底说了什么**只剩下转述。转述无法被引用、无法被核对，而它与原文之间的漂移是**不可见**的——因为没有可比对的对象。

所以本仓库每份文档都带 **原文摘录（source excerpts）** 一节：对每篇引用的论文，逐字收录承载结论的句子，不翻译。正文是**解读**，摘录才是**证据**。

工具把这条纪律机械化：

| 脚本 | 作用 |
|---|---|
| `rebuild_references.py` | 参考文献条目不是"修改"而是按 PMID 从 PubMed 记录**重建**。标题、ISO 期刊缩写、卷期页、DOI 逐字采录。作者注解降级到末尾，永远不会被误认为标题的一部分。 |
| `extract_source_excerpts.py` | 抽取承载每个引用数字的原文句子，并**报告正文引用了但原文中不存在的数字**——它们可能出自摘要不含的全文，也可能有误，但无论如何都不该以"已核实"的面目通过。 |
| `render_markdown.py` | 纯标准库 Markdown → 印刷级 HTML（GitHub 兼容锚点），配 headless Chrome 出 PDF。零依赖安装。 |

**在约 150 条参考文献上实际抓到的：**

- 一个**指向无关牙科信息学论文的 PMID**，却被当作救援化疗方案的出处。挂在它名下的数据**全部正确**，只有编号错了。不回原文永远发现不了。
- 一处**临床征象张冠李戴**——把咳嗽的发生率记成了发声障碍的发生率，导致报告区间整体偏移一半。
- 一个**在被引论文中根本不存在**的应答率区间。
- 若干错误的年份、作者缩写、第一作者，以及大量被截短的标题。
- 一篇论文的**摘要与其自身结果部分互相矛盾**（关于某协变量是否影响生存）。

要点不是"这些是粗心造成的错误"，而是：**认真读发现不了，回原文才能发现。**

### 复用这个 agent

把 `.claude/agents/medical.md` 放进任意项目的 `.claude/agents/` 即可。它按需加载 bio-research 系列 MCP 工具（PubMed / ClinicalTrials / ChEMBL / Consensus）。

具体纪律写在该文件里。简述：涉及数值一律检索而非凭记忆；每条结论标注【已查证】【推断】【外推】【未知】；追溯哪些前提来自用户、哪些是自己填的；不开处方；急症识别优先于诊断完美。

---

## License

MIT. See [LICENSE](LICENSE).

Literature quoted in this repository belongs to its respective publishers; excerpts are limited to the sentences needed to verify a specific claim, each attributed with PMID and DOI.
