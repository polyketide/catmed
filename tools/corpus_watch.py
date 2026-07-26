#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Watch a private owner-community corpus for things the knowledge base should know.

Three questions, three subcommands:

    corpus_watch.py divergence   # where does community practice conflict with verified evidence?
    corpus_watch.py unknown      # what shorthand appears often and is covered nowhere?
    corpus_watch.py topics       # what are people asking about, vs what do we cover?

WHY THIS EXISTS. Two research instruments are recorded in the SOP (§7a): corpus
frequency analysis, and single deep questions. Both were run by hand, once. A
hand-run analysis is a snapshot that silently expires — vocabulary drifts, new
drugs arrive, and practice changes. This makes the recurring part rerunnable.

WHAT IT DELIBERATELY DOES NOT DO.

  * It does not decide anything is wrong. `divergence` reports occurrences of
    divergences ALREADY established against verified sources, each pointing at
    the knowledge-base file holding the evidence. It cannot discover a new
    clinical error, and any output claiming otherwise would be this project's
    cardinal sin (SOP §12) wearing a script's clothes.
  * It does not judge clinicians. The corpus cannot separate access, cost, local
    convention, case mix or commercial pressure (SOP §7a). Counting a pattern is
    not explaining it.
  * It does not write corpus content anywhere. The corpus lives OUTSIDE the
    repository and stays there; only counts and term candidates reach stdout.
    This is the same cache-not-truth split the archive uses, for a stronger
    reason: the archive holds published papers, this holds people's private
    conversations about a dying animal.

CORPUS LOCATION resolves as: --corpus, then $CATMED_CORPUS. There is no default
and none should be added: a default path invites someone to drop the corpus in
the repo and commit it.
"""
import argparse
import collections
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KB = REPO / "knowledge-base"
GUIDES = REPO / "guides"
LEXICON = KB / "owner-vernacular-lexicon.zh.md"


# --------------------------------------------------------------- corpus access

def corpus_path(explicit):
    """Resolve the corpus location, refusing anything inside the repository.

    The refusal is the point. A private support-group export inside a public
    repo is one `git add -A` away from being published, and no amount of care
    downstream undoes that. Mirrors pubmed_archive.archive_dir()."""
    raw = explicit or os.environ.get("CATMED_CORPUS")
    if not raw:
        sys.exit("no corpus given: pass --corpus PATH or set $CATMED_CORPUS "
                 "(no default exists, deliberately — see the module docstring)")
    p = Path(raw).expanduser().resolve()
    if not p.exists():
        sys.exit(f"corpus not found: {p}")
    if REPO == p or REPO in p.parents:
        sys.exit(f"refusing to read a corpus stored inside the repository: {p}\n"
                 "Move it outside the repo; it must never be committable.")
    return p


def corpus_text(path):
    """All text from the corpus, whether it is one file or a directory."""
    files = sorted(path.glob("**/*.md")) if path.is_dir() else [path]
    if not files:
        sys.exit(f"no .md files found in {path}")
    return "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in files)


def kb_text():
    """Everything the knowledge base and guides say, for coverage tests."""
    parts = []
    for d in (KB, GUIDES):
        if d.is_dir():
            parts += [f.read_text(encoding="utf-8", errors="replace") for f in d.glob("*.md")]
    return "\n".join(parts)


# ------------------------------------------------------- 1. divergence registry
#
# Each entry: a practice observable in owner communities, the evidence that
# bears on it, and the file holding that evidence verbatim. Every `note` here
# must be traceable to an excerpt in `kb` — this table is a router, never a
# source. Adding a row without landing the evidence first inverts the pipeline.

DIVERGENCES = [
    {
        "key": "human-gcsf-repeat",
        "pattern": r"升白|瑞白|惠尔血|免力健",
        "note": "反复注射人用 G-CSF 可诱导与自身 G-CSF 交叉反应的中和抗体，反而致中性粒细胞减少。",
        "kb": "gcsf-and-chemotherapy-neutropenia.md",
    },
    {
        "key": "transfusion-untyped",
        "pattern": r"输血|供血|配血",
        "note": "猫可能死于首次输血；AB 同型为必要非充分（Mik），首次输血前亦须交叉配血。",
        "kb": "blood-types-and-transfusion-compatibility.md",
    },
    {
        "key": "esa-without-classifying",
        "pattern": r"\bepo\b|\bdpo\b|促红|补血|生血",
        "note": "先按网织红细胞分类并过严重度门槛；达贝泊汀的猫证据来自肾性贫血，不外推至肿瘤相关贫血。",
        "kb": "supportive-and-palliative-care.md",
    },
    {
        "key": "iron-in-inflammatory-anaemia",
        "pattern": r"补血|铁剂|肝精|阿胶|生血宁",
        "note": "非处方补血制剂无支持证据；含铁者在炎症性贫血（肿瘤患者最常见）中基本无效且有已记载危害。",
        "kb": "supportive-and-palliative-care.md",
    },
    {
        "key": "force-feeding-over-tube",
        "pattern": r"强饲|灌食|硬喂",
        "note": "2022 ISFM 共识：因照护者顾虑而拖延放置饲管，可能拖慢恢复；并发症亦真实，两侧都要说。",
        "kb": "assisted-feeding-and-feeding-tubes.md",
    },
    {
        "key": "response-called-on-one-lesion",
        "pattern": r"不应答|无效|没效果|压不住|耐药",
        "note": "VCOG 判据自陈仅用于狗且不评估结外病灶；单一时点单一结外病灶是最弱的判定配置。",
        "kb": "response-assessment-and-drug-resistance.md",
    },
    {
        "key": "doxorubicin-assumed-better",
        "pattern": r"多柔|阿霉素|chop",
        "note": "猫的多柔比星单药疗效弱且靶器官是肾；“狗的标准”不构成关于猫的论证。",
        "kb": "does-doxorubicin-help-cats-cop-vs-chop.md",
    },
    {
        "key": "cure-rate-folklore",
        "pattern": r"结疗率|治愈率|能好的.{0,4}[几百]|1%",
        "note": "流传的“约 1%”与已核实数据不符（低级别 CR 76%、小细胞 ORR 85.7%、高级别 66%）。",
        "kb": "does-doxorubicin-help-cats-cop-vs-chop.md",
    },
]


def cmd_divergence(args):
    text = corpus_text(corpus_path(args.corpus))
    print("语料中出现的『已知分歧点』——这是路由，不是判断\n"
          "  每一条都指向持有逐字证据的知识库文件；本工具不认定任何做法是错的。\n")
    rows = []
    for d in DIVERGENCES:
        n = len(re.findall(d["pattern"], text, re.I))
        if n:
            rows.append((n, d))
    if not rows:
        print("  （无命中）")
        return 0
    for n, d in sorted(rows, key=lambda r: -r[0]):
        exists = (KB / d["kb"]).exists()
        mark = " " if exists else "  ⚠️ 指向的文件不存在！"
        print(f"  {n:5d}  {d['key']}")
        print(f"         {d['note']}")
        print(f"         → knowledge-base/{d['kb']}{mark}")
    print(f"\n  {len(rows)} 个分歧点被触及。频次高低不代表严重程度，只代表被谈论得多。")
    return 0


# ------------------------------------------------------- 2. unknown-term monitor

# Very common Chinese words that carry no clinical meaning here. Kept short on
# purpose: over-filtering hides real terms, and the output is explicitly a
# candidate list for a human, not a finding.
STOP = set("""
现在 这个 那个 什么 怎么 可以 就是 我们 你们 他们 自己 时候 因为 所以 但是 如果
今天 明天 昨天 一个 没有 还是 这样 那样 知道 觉得 应该 可能 已经 一直 真的 谢谢
不是 这边 那边 问题 情况 医生 医院 宝宝 宝贝 姐妹 大家 群里 感谢 辛苦 麻烦 不好
""".split())


EXPORT_NOISE = {"图片", "图片消息", "表情包", "链接", "视频", "语音", "文件", "转账", "撤回"}

# Cities are identifying in a small community — a city plus a cat's disease can
# single out one member. Filtered for the same reason display names are.
CITIES = set("""
北京 上海 广州 深圳 南京 杭州 成都 天津 武汉 长沙 苏州 厦门 重庆 西安 青岛 大连
沈阳 济南 合肥 福州 南宁 昆明 贵阳 郑州 无锡 宁波 南昌 南充 石家庄 哈尔滨 长春
东莞 佛山 惠州 珠海 汕头 温州 常州 徐州 扬州 烟台 潍坊 唐山 洛阳 襄阳 蚌埠 江阴
东京 大阪 悉尼 墨尔本 纽约 美国 日本 澳洲 加拿大 多伦多 温哥华 西班牙 丹麦 捷克
""".split())


def speaker_fragments(text):
    """Every CJK fragment appearing in a sender name, to be excluded from output.

    ⚠️ ADDED AFTER THE FIRST REAL RUN, WHICH FAILED THIS PROJECT'S OWN RULE.
    The unknown-term monitor is careful never to write corpus content into the
    repository — and then printed group members' display names, a cat's name and
    the group's own name straight to stdout, ranked by frequency. Output is a
    publication surface too (SOP §9a.4): anyone pasting that list into an issue
    would have leaked exactly what the corpus rules exist to protect.

    Display names are recoverable because the export marks them: `## DATE TIME
    NAME`. Every 2-4 character window of every sender name is excluded, since
    the term extractor works on windows, not on whole names."""
    frags = set()
    for m in re.finditer(r"^##\s+\d{4}\S*\s+\d{2}:\d{2}:\d{2}\s+(.+?)\s*$", text, re.M):
        name = re.sub(r"\\(.)", r"\1", m.group(1))
        cjk = re.findall(r"[一-鿿]+", name)
        for run in cjk:
            for size in (2, 3, 4):
                for i in range(len(run) - size + 1):
                    frags.add(run[i:i + size])
    return frags


def cmd_unknown(args):
    text = corpus_text(corpus_path(args.corpus))
    known = (LEXICON.read_text(encoding="utf-8") if LEXICON.exists() else "") + kb_text()
    excluded = speaker_fragments(text) | EXPORT_NOISE | CITIES

    cand = collections.Counter()
    # 2-4 character CJK runs — the shape most drug names and clinical terms take.
    for m in re.finditer(r"[一-鿿]{2,4}", text):
        t = m.group(0)
        if t not in STOP:
            cand[t] += 1
    # Protocol-style abbreviations: one CJK char + digits (门1, 洛2, 培3 ...)
    for m in re.finditer(r"([一-鿿])\d{1,2}(?![\d一-鿿])", text):
        cand["%s+数字" % m.group(1)] += 1

    missing = [(n, t) for t, n in cand.items()
               if n >= args.min_count
               and t.replace("+数字", "") not in known
               and t not in excluded]
    missing.sort(key=lambda r: -r[0])

    print("语料中高频、但术语表与知识库均未覆盖的写法\n"
          "  ⚠️ 这是**候选清单，含噪声**（日常词会混入），需要人来判断。\n"
          f"  已排除 {len(excluded)} 个发言人名片段、城市名与导出工具产物——输出本身也是发布面。\n"
          "  ⚠️ 中文无 NER 则无法完全分离人名与术语：**残留人名仍会出现**，\n"
          "     故本清单只供人当场判读，**不得原样复制、粘贴或提交**。\n"
          "  用途：发现语言漂移与新药新写法。绝不可据此自动扩充术语表。\n")
    if not missing:
        print("  （无候选）")
        return 0
    for n, t in missing[:args.top]:
        print(f"  {n:5d}  {t}")
    print(f"\n  共 {len(missing)} 个候选（阈值 ≥{args.min_count} 次），上列前 {min(args.top, len(missing))} 个。")
    return 0


# ---------------------------------------------------------- 3. topic vs coverage

TOPICS = [
    ("化疗方案与轮次", r"cop|chop|cmop|方案|几次|疗程|结疗|减药|停药|间隔|周期|换方案"),
    ("医院与医生选择", r"医院|医生|大夫|挂号|转诊|哪家|会诊|专家"),
    ("副作用与处理", r"副作用|反应|不良|掉毛|口炎|溃疡|指标高|伤肝|保肝|护肾"),
    ("费用与药品获取", r"多少钱|价格|费用|贵|哪买|代购|药店|渠道|断货|出药"),
    ("具体药物用法剂量", r"剂量|mg|吃几|怎么吃|一次几|多久吃|空腹|饭前|饭后|掰|半粒|用量"),
    ("检查与诊断", r"穿刺|活检|病理|免疫组化|超声|b超|ct|核磁|片子|报告|确诊|分型|复查"),
    ("血常规骨髓抑制", r"血常规|白细胞|中性粒|粒细胞|血小板|贫血|血值|抽血|骨髓抑制|升白|网织"),
    ("食欲呕吐腹泻", r"食欲|不吃|厌食|呕吐|吐了|拉稀|腹泻|软便|强饲|管饲|营养|体重"),
    ("预后与生存期", r"能活|多久|生存|预后|活多久|晚期|转移|扩散|复发|恶化"),
    ("临终与安乐", r"安乐|喵星|临终|痛苦|放弃|最后"),
]

QUESTION = re.compile(r"[?？]|怎么办|怎么样|如何|要不要|能不能|可以吗|有没有|是不是|多少|为什么|请问|求助")


def cmd_topics(args):
    text = corpus_text(corpus_path(args.corpus))
    kb = kb_text()
    lines = [l for l in text.splitlines() if l.strip() and QUESTION.search(l)]
    print(f"疑问句式行 {len(lines)} 条 —— 提问主题分布 vs 知识库覆盖\n")
    if not lines:
        print("  （无）")
        return 0
    joined = "\n".join(lines)
    rows = []
    for name, pat in TOPICS:
        n = len(re.findall(pat, joined, re.I))
        # Coverage proxy: does any KB/guide text mention this topic's terms at all?
        covered = len(re.findall(pat, kb, re.I))
        rows.append((n, name, covered))
    for n, name, covered in sorted(rows, key=lambda r: -r[0]):
        pct = n / len(lines) * 100
        flag = "✅" if covered >= 20 else ("⚠️ 覆盖薄" if covered else "❌ 无覆盖")
        print(f"  {n:5d}  {pct:5.1f}%  {name:<12} {flag} (KB 命中 {covered})")
    print("\n  ⚠️ 『KB 命中』只是词面覆盖的粗代理，不等于实质覆盖——低分值得人工确认，"
          "高分不保证答得好。\n  ⛔ 医院选择与药品渠道属于应当拒答的范围，其频次高不代表应当去覆盖。")
    return 0


# ------------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--corpus", help="corpus file or directory, OUTSIDE the repo "
                                     "(or set $CATMED_CORPUS)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("divergence", help="known divergences occurring in the corpus")
    u = sub.add_parser("unknown", help="frequent shorthand covered nowhere")
    u.add_argument("--min-count", type=int, default=8)
    u.add_argument("--top", type=int, default=40)
    sub.add_parser("topics", help="question topics vs knowledge-base coverage")
    args = ap.parse_args()
    return {"divergence": cmd_divergence, "unknown": cmd_unknown,
            "topics": cmd_topics}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
