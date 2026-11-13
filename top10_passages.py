"""Extract source-text passages (KWIC with juan and date) for the top-10
collocates of 冗官 in the Changbian, and add a passage section to
冗官搭配词.html.

The Siku edition is unpunctuated, so "sentences" are rendered as fixed
character windows around each co-occurrence. For each top-10 collocate
(by p-value, window ±5 run) every 冗官-window co-occurrence is listed.
Output: results/top10_passages.txt + updated HTML section.
"""
import json
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
DATA = HERE / "changbian" / "data"
RESULTS = HERE / "changbian" / "results"
HTML = HERE / "冗官搭配词.html"

TARGET = "冗官"


def era_of(juan_text):
    head = juan_text[:50]
    m = re.search(r"(仁宗|英宗|神宗|哲宗|徽宗|欽宗)([^月]{1,10}月)", head)
    if m:
        return m.group(1) + m.group(2)
    m = re.search(r"([^月]{2,12}月)", head)
    return m.group(1) if m else juan_text[:10]


def find_all(text, pat):
    return [m.start() for m in re.finditer(f"(?={re.escape(pat)})", text)]


def main():
    main_lines = (DATA / "changbian_main.txt").read_text(
        encoding="utf-8").split("\n")
    manifest = json.loads((DATA / "manifest.json").read_text())

    # tokenise each juan the same way analyze.py does, and locate target
    # and collocate token positions, then map back to character offsets
    import jieba
    from opencc import OpenCC
    t2s = OpenCC("t2s")
    jieba.load_userdict(str(HERE / "changbian" / "user_dict.txt"))
    NOT_WORD = re.compile(r"[，、；：「」『』《》〈〉！？（）()〔〕\[\]—…·／/\s□]")

    df = pd.read_csv(RESULTS / "collocates_w5.csv")
    top10 = df.sort_values("p_value").head(10)["collocate"].tolist()

    # positions of target tokens per juan, in simplified text
    juan_data = []  # (juan, era, simp_text, offsets) offsets: char->token idx
    for juan, text in zip(manifest, main_lines):
        simp = t2s.convert(text)
        if TARGET not in simp:
            continue
        toks = []
        tok_of_char = [None] * (len(simp) + 1)  # char index -> token idx
        pos = 0
        for ti, t in enumerate(jieba.cut(simp, HMM=False)):
            toks.append(t)
            for k in range(len(t)):
                tok_of_char[pos + k] = ti
            pos += len(t)
        # note: jieba tokens include punctuation; NOT_WORD filtered later
        juan_data.append((juan, era_of(text), simp, toks, tok_of_char))

    entries = []  # (collocate, juan, era, passage)
    for coll in top10:
        for juan, era, simp, toks, tok_of_char in juan_data:
            # token indices of target and collocate
            t_idx = [i for i, t in enumerate(toks) if t == TARGET]
            if not t_idx:
                continue
            c_idx = [i for i, t in enumerate(toks) if t == coll]
            if not c_idx:
                continue
            # token positions are contiguous, so window check by index
            for ci in c_idx:
                for ti in t_idx:
                    d = ci - ti
                    if 0 < abs(d) <= 5 and not NOT_WORD.search(coll):
                        # character position of the collocate token start
                        chpos = None
                        # find char pos by scanning token lengths
                        # (only compute when needed)
                        pos = 0
                        for i, t in enumerate(toks):
                            if i == ci:
                                chpos = pos
                                break
                            pos += len(t)
                        s = max(0, chpos - 40)
                        e = min(len(simp), chpos + len(coll) + 40)
                        pre = simp[s:chpos]
                        node = simp[chpos:chpos + len(coll)]
                        post = simp[chpos + len(coll):e]
                        mark = (f'{pre}【{node}】{post}')
                        entries.append((coll, juan, era, mark))
                        break  # one passage per collocate occurrence

    # dedupe by (coll, juan, passage)
    seen, lines_out = set(), []
    for coll, juan, era, mark in entries:
        key = (coll, juan, mark)
        if key in seen:
            continue
        seen.add(key)
        lines_out.append(f"〔{coll}〕卷{juan}（{era}）…{mark}…")

    (RESULTS / "top10_passages.txt").write_text(
        "\n".join(lines_out) + "\n", encoding="utf-8")
    print(f"{len(lines_out)} passages for top-10 collocates")

    # ---- HTML section ----
    by_coll = {}
    for coll, juan, era, mark in lines_out and [] or []:
        pass
    import collections
    by_coll = collections.OrderedDict()
    for coll in top10:
        by_coll[coll] = [l for l in lines_out if l.startswith(f"〔{coll}〕")]
    sec = ['<div class="read" id="passages"><h3>前十名搭配词的原文本</h3>'
           '<p class="n" style="margin-top:0">按 p 值排序的前十名搭配词，'
           '每词列出其与「冗官」共现的全部原文段落（四库本无标点，'
           '以【】标出搭配词，前后各约 40 字；标明卷次与年月）。</p>']
    for coll, ls in by_coll.items():
        if not ls:
            sec.append(f'<h4>〔{coll}〕</h4><p class="n">（无共现段落）</p>')
            continue
        sec.append(f'<h4>〔{coll}〕· {len(ls)} 段</h4><ul class="kwic">')
        for l in ls:
            body = l.split("〕", 1)[1]
            sec.append(f"<li>{body}</li>")
        sec.append("</ul>")
    sec.append("</div>")

    html = HTML.read_text(encoding="utf-8")
    # insert before the footer note
    anchor = '<p class="note">'
    html = html.replace(anchor, "".join(sec) + "\n" + anchor, 1)
    # add CSS for kwic list
    css_anchor = "  em {{ color:var(--red); font-style:normal; font-weight:600; }}"
    kwic_css = """
  .kwic {{ list-style:none; padding-left:0; margin:6px 0 18px; }}
  .kwic li {{ font-size:13.5px; line-height:1.9; margin:4px 0;
             padding:6px 10px; background:#faf6ec; border-radius:6px;
             border-left:3px solid var(--line); text-align:justify; }}
  .kwic li b {{ color:var(--red); }}
  h4 {{ font-size:15px; color:#55503f; margin:14px 0 6px; letter-spacing:1px; }}"""
    html = html.replace(css_anchor, css_anchor + kwic_css, 1)
    HTML.write_text(html, encoding="utf-8")
    print(f"updated {HTML}")


if __name__ == "__main__":
    main()
