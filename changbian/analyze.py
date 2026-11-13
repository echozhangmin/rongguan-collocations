"""Collocations of 冗官 in the Xu Zizhi Tongjian Changbian (續資治通鑑長編).

Corpus: the Wikisource 四庫全書本 transcription, 513 extant juan,
unpunctuated. Li Tao's own notes were cleaned out into a separate file,
so this analysis covers the main text only.

Same method as the 資治通鑑 project (assignment 1, qhchina):
t2s -> jieba (HMM off, user dictionary) -> windows of ±5 and ±10 tokens.
Because the edition has no punctuation, a juan is one tokenisation unit
(max_sentence_length=None); windows never cross juan boundaries.

Four runs, one CSV each:
  collocates_w5.csv / collocates_w10.csv        target 冗官
  collocates_pooled_w5.csv / _w10.csv          target 冗官+冗员 pooled
Also writes:
  results/keyword_density.csv   keyword x juan counts (reading guide)
  results/kwic_rongguan.txt     character-based concordance of the
                                冗-term family, with juan + era + note tag
  results/compare.html          side-by-side top lists of the four runs
"""
import json
import re
from pathlib import Path

import jieba
import pandas as pd
from opencc import OpenCC
from qhchina.analytics.collocations import find_collocates

HERE = Path(__file__).parent
DATA = HERE / "data"
OUTDIR = HERE / "results"

WINDOWS = [5, 10]
COLLOCATE_COLS = ["collocate", "obs_local", "exp_local", "obs_global",
                  "p_value", "adjusted_p_value", "log_likelihood", "log_dice"]

# the 冗-family and the institutional vocabulary around office reform
DENSITY_TERMS = ["冗官", "冗員", "冗兵", "冗費", "冗食", "濫官", "濫賞",
                 "省官", "任子", "僥倖", "磨勘"]
KWIC_TERMS = ["冗官", "冗員", "冗食", "濫官", "濫賞"]

NOT_WORD = re.compile(r"[，、；：「」『』《》〈〉！？（）()〔〕\[\]—…·／/\s□]")


def load():
    main = (DATA / "changbian_main.txt").read_text(encoding="utf-8").split("\n")
    notes = (DATA / "changbian_notes.txt").read_text(encoding="utf-8").split("\n")
    notes = [n for n in notes if n]
    manifest = json.loads((DATA / "manifest.json").read_text())
    return main, notes, manifest


def era_of(juan_text):
    """Opening date, e.g. 仁宗嘉祐六年閏八月, from the juan header."""
    head = juan_text[:50]
    m = re.search(r"(仁宗|英宗|神宗|哲宗|徽宗|欽宗)([^月]{1,10}月)", head)
    if m:
        return m.group(1) + m.group(2)
    m = re.search(r"([^月]{2,12}月)", head)
    if m:
        return m.group(1)
    return juan_text[:10]


def build_sentences(main):
    """Restartable list of tokenized juan (simplified, punctuation-free)."""
    t2s = OpenCC("t2s")
    jieba.load_userdict(str(HERE / "user_dict.txt"))
    sentences = []
    for juan_text in main:
        toks = [t for t in jieba.cut(t2s.convert(juan_text), HMM=False)
                if not NOT_WORD.search(t)]
        sentences.append(toks)
    return sentences


def run(sentences, horizon, target):
    df = find_collocates(
        sentences,
        target,
        method="window",
        horizon=horizon,
        pooled=(target != "冗官"),
        measures=["log_likelihood", "log_dice"],
        correction="fdr_bh",
        max_sentence_length=None,
    )
    return df.sort_values("p_value")


def keyword_density(main, manifest):
    rows = []
    for juan, text in zip(manifest, main):
        row = {"卷": juan, "年代": era_of(text)}
        for t in DENSITY_TERMS:
            row[t] = text.count(t)
        row["命中合计"] = sum(row[t] for t in DENSITY_TERMS)
        rows.append(row)
    return pd.DataFrame(rows)


def kwic_file(main, notes, manifest):
    out = []
    for term in KWIC_TERMS:
        out.append(f"◆◇◆ {term} ◆◇◆")
        n = 0
        for juan, text in zip(manifest, main):
            for m in re.finditer(term, text):
                n += 1
                s, e = max(0, m.start() - 45), m.end() + 45
                ctx = text[s:e]
                out.append(f"卷{juan}（{era_of(text)}） …{ctx}…")
        for line in notes:
            juan, _, ntext = line.partition("\t")
            for m in re.finditer(term, ntext):
                n += 1
                s, e = max(0, m.start() - 45), m.end() + 45
                out.append(f"{juan}〔李焘自注〕 …{ntext[s:e]}…")
        out.append(f"〔{term}：正文+注 共 {n} 次〕\n")
        if n == 0:
            out.pop(-2)  # drop the empty header
    (OUTDIR / "kwic_rongguan.txt").write_text(
        "\n".join(out) + "\n", encoding="utf-8")


def save_html(runs):
    blocks = []
    for (h, label), df in runs.items():
        blocks.append(f"<h2>{label}，窗口 ±{h}</h2>")
        for title, d in (
            ("按 p 值（显著性，Fisher 精确检验）",
             df.sort_values("p_value")),
            ("按 logDice（强度）",
             df.sort_values("log_dice", ascending=False)),
        ):
            top = d.head(20)[COLLOCATE_COLS]
            blocks.append(f"<h3>{title}（前 20）</h3>")
            blocks.append(top.to_html(index=False, border=1))
    body = "\n".join(blocks)
    html = (
        "<html><head><meta charset='utf-8'>"
        "<title>長編 冗官 搭配词比较</title></head>"
        f"<body><h1>《續資治通鑑長編》中「冗官」的搭配词</h1>"
        f"<p>语料：维基文库四库本 513 卷（无标点，正文，不含李焘自注）；"
        f"目标词：冗官；另附 冗官+冗员 合并目标。"
        f"分词：jieba + 用户词典（繁转简、关闭 HMM、卷为单位、窗口不跨卷）。</p>"
        f"{body}</body></html>"
    )
    (OUTDIR / "compare.html").write_text(html, encoding="utf-8")


def main():
    OUTDIR.mkdir(exist_ok=True)
    main, notes, manifest = load()
    sentences = build_sentences(main)
    n_tokens = sum(len(s) for s in sentences)
    print(f"juan: {len(sentences)}, tokens: {n_tokens}")

    dens = keyword_density(main, manifest)
    dens.to_csv(OUTDIR / "keyword_density.csv",
                index=False, encoding="utf-8-sig")
    top = dens[dens["命中合计"] > 0].sort_values("命中合计", ascending=False)
    print("\n=== keyword totals (main text) ===")
    print(dens[DENSITY_TERMS].sum().to_string())
    print("\n=== densest juan ===")
    print(top.head(15)[["卷", "年代", "冗官", "命中合计"]].to_string(index=False))

    kwic_file(main, notes, manifest)

    runs = {}
    for h in WINDOWS:
        df = run(sentences, h, "冗官")
        df.to_csv(OUTDIR / f"collocates_w{h}.csv",
                  index=False, encoding="utf-8-sig")
        runs[(h, "冗官")] = df
        print(f"\n=== 冗官, window ±{h}: {len(df)} collocates ===")
        print("Top by p_value:")
        print(df.sort_values("p_value").head(12)[COLLOCATE_COLS]
              .to_string(index=False))
    for h in WINDOWS:
        df = run(sentences, h, ["冗官", "冗员"])
        df.to_csv(OUTDIR / f"collocates_pooled_w{h}.csv",
                  index=False, encoding="utf-8-sig")
        runs[(h, "冗官＋冗员（合并）")] = df
        print(f"\n=== pooled 冗官+冗员, window ±{h}: {len(df)} ===")
        print(df.sort_values("p_value").head(12)[COLLOCATE_COLS]
              .to_string(index=False))
    save_html(runs)
    print(f"\nwrote {OUTDIR}/compare.html")


if __name__ == "__main__":
    main()
