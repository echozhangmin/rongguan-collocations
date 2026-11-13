"""Build a polished self-contained HTML overview of the 冗官 collocation
results from the 續資治通鑑長編 project (target 冗官 and pooled 冗官+冗員,
windows ±5 / ±10).

Reads the CSVs produced by changbian/analyze.py and writes
冗官搭配词.html. No external dependencies: one file, inline CSS.
Run from the repository root: python3 make_overview.py
"""
import pathlib

import pandas as pd

ROOT = pathlib.Path(__file__).parent
C = ROOT / "changbian" / "results"
OUT = ROOT / "冗官搭配词.html"

VERBS = {"减", "除", "去", "省", "汰", "裁", "废", "增", "罢"}
KEYN = {"四色", "良吏", "滥官", "冗官"}
CAUSAL = {"奏荐", "任子", "磨勘", "侥幸", "员多阙少"}

RUNS = [
    (C / "collocates_w5.csv", "冗官 · 窗口 ±5"),
    (C / "collocates_w10.csv", "冗官 · 窗口 ±10"),
    (C / "collocates_pooled_w5.csv", "冗官＋冗員（合并）· 窗口 ±5"),
    (C / "collocates_pooled_w10.csv", "冗官＋冗員（合并）· 窗口 ±10"),
]


def stars(p):
    if pd.isna(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def fmt_p(p):
    if pd.isna(p):
        return "—"
    if p == 0:
        return "≈0"
    if p < 0.0001:
        return f"{p:.1e}".replace("e-0", "×10⁻").replace("e-", "×10⁻")
    return f"{p:.4f}"


def chips(df, n=6):
    top = df.sort_values("p_value").head(n)
    out = []
    for _, r in top.iterrows():
        cls = "chip verb" if r["collocate"] in VERBS else "chip"
        out.append(
            f'<span class="{cls}">{r["collocate"]}<i>×{int(r["obs_local"])}</i></span>'
        )
    return "".join(out)


def table(df, by, n=12):
    d = (df.sort_values("p_value") if by == "p"
         else df.sort_values("log_dice", ascending=False)).head(n)
    rows = []
    for _, r in d.iterrows():
        c = str(r["collocate"])
        cls = ""
        if c in VERBS:
            cls = ' class="verb"'
        elif c in CAUSAL:
            cls = ' class="causal"'
        elif c in KEYN:
            cls = ' class="keyn"'
        w = min(100.0, float(r["log_dice"]) / 12 * 100)
        rows.append(
            f"<tr{cls}><td>{c}</td>"
            f"<td>{int(r['obs_local'])}</td>"
            f"<td>{r['exp_local']:.3g}</td>"
            f"<td>{int(r['obs_global'])}</td>"
            f"<td>{fmt_p(r['p_value'])} {stars(r['p_value'])}</td>"
            f"<td>{fmt_p(r['adjusted_p_value'])} {stars(r['adjusted_p_value'])}</td>"
            f"<td class='ld'><span class='bar' style='width:{w:.0f}%'></span>"
            f"<b>{r['log_dice']:.2f}</b></td></tr>"
        )
    head = ("<tr><th>搭配词</th><th>共现</th><th>期望</th><th>全局频次</th>"
            "<th>p 值</th><th>FDR 后 p</th><th>logDice</th></tr>")
    return f"<table>{head}{''.join(rows)}</table>"


def main():
    sections = []
    for path, label in RUNS:
        df = pd.read_csv(path)
        anchor = label.replace("（", "").replace("）", "").replace(" ", "")
        sections.append(f"""
<section id="{anchor}">
  <h3>{label}</h3>
  <p class="chips">{chips(df)}</p>
  <div class="two">
    <div><h4>按显著性（p 值，前 12）</h4>{table(df, "p")}</div>
    <div><h4>按强度（logDice，前 12）</h4>{table(df, "d")}</div>
  </div>
  <p class="n">该运行共 {len(df)} 个搭配词</p>
</section>""")

    nav = "".join(
        f'<a href="#{l.replace("（","").replace("）","").replace(" ","")}">'
        f'{l.split("·")[0].strip()} · {l.split("·")[-1].strip()}</a>'
        for _, l in RUNS
    )

    html = f"""<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8">
<title>「冗官」搭配词 · 续资治通鉴长编</title>
<style>
  :root {{ --ink:#2b2620; --paper:#f7f4ee; --card:#fffdf8; --line:#e3dccd;
          --red:#8b2e2e; --gold:#a9802f; --blue:#3d5a73; --soft:#8a8071; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--paper); color:var(--ink);
         font-family:"Songti SC","Noto Serif SC","STSong",serif; }}
  .page {{ max-width:1080px; margin:0 auto; padding:48px 32px 80px; }}
  header {{ text-align:center; border-bottom:3px double var(--line);
            padding-bottom:28px; margin-bottom:8px; }}
  h1 {{ font-size:30px; letter-spacing:2px; margin:0 0 10px; }}
  h1 .node {{ color:var(--red); }}
  .sub {{ color:var(--soft); font-size:14px; letter-spacing:1px; }}
  .cards {{ display:flex; gap:16px; margin:26px 0 10px; flex-wrap:wrap; }}
  .card {{ flex:1 1 320px; background:var(--card); border:1px solid var(--line);
          border-radius:10px; padding:16px 20px; }}
  .card h2 {{ font-size:17px; margin:0 0 8px; letter-spacing:1px; }}
  .card .big {{ font-size:30px; color:var(--red); font-weight:700; }}
  .card p {{ margin:6px 0; font-size:13.5px; color:#55503f; }}
  nav {{ text-align:center; margin:18px 0 34px; }}
  nav a {{ display:inline-block; margin:3px 8px; padding:5px 14px; font-size:14px;
          color:var(--ink); background:var(--card); border:1px solid var(--line);
          border-radius:999px; text-decoration:none; letter-spacing:1px; }}
  nav a:hover {{ border-color:var(--red); color:var(--red); }}
  section {{ background:var(--card); border:1px solid var(--line);
            border-radius:10px; padding:24px 28px; margin:22px 0; }}
  h3 {{ margin:0 0 6px; font-size:20px; letter-spacing:1.5px; }}
  h3 .sep {{ color:var(--red); margin:0 8px; }}
  .chips {{ margin:8px 0 16px; }}
  .chip {{ display:inline-block; padding:3px 12px; margin:2px 4px; font-size:14px;
          background:#efe9db; border-radius:999px; letter-spacing:1px; }}
  .chip.verb {{ background:#f6e3df; color:var(--red); font-weight:600; }}
  .chip i {{ font-style:normal; font-size:12px; color:var(--soft);
            margin-left:4px; }}
  .two {{ display:flex; gap:20px; flex-wrap:wrap; }}
  .two > div {{ flex:1 1 420px; }}
  h4 {{ font-size:15px; color:#55503f; margin:10px 0 6px; letter-spacing:1px; }}
  table {{ border-collapse:collapse; width:100%; font-size:13px;
          font-family:"PingFang SC","Hiragino Sans GB",sans-serif;
          font-variant-numeric:tabular-nums; }}
  th {{ text-align:left; background:#efe9db; padding:6px 8px; font-weight:600;
       border-bottom:2px solid var(--line); white-space:nowrap; }}
  td {{ padding:5px 8px; border-bottom:1px solid #eee7d8; }}
  tr:hover td {{ background:#faf6ec; }}
  tr.verb td:first-child {{ color:var(--red); font-weight:700; }}
  tr.keyn td:first-child {{ color:var(--gold); font-weight:700; }}
  tr.causal td:first-child {{ color:var(--blue); font-weight:700; }}
  .ld {{ position:relative; }}
  .bar {{ position:absolute; left:0; top:6px; bottom:6px; background:#e5d9bd;
         border-radius:3px; z-index:0; }}
  .ld b {{ position:relative; z-index:1; padding-left:6px; }}
  .n {{ color:var(--soft); font-size:12.5px; margin:10px 0 0; }}
  .read {{ background:#fbf7ee; border:1px solid var(--line); border-radius:10px;
          padding:22px 28px; margin:30px 0; }}
  .read h3 {{ font-size:18px; }}
  .read li {{ margin:7px 0; line-height:1.75; font-size:15px; }}
  .note {{ color:var(--soft); font-size:12.5px; line-height:1.8; margin-top:30px;
          border-top:1px solid var(--line); padding-top:14px; }}
  em {{ color:var(--red); font-style:normal; font-weight:600; }}
  i.c {{ color:var(--blue); font-style:normal; font-weight:600; }}
</style></head><body><div class="page">
<header>
  <h1>《續資治通鑑長編》中「<span class="node">冗官</span>」的搭配词</h1>
  <p class="sub">李焘 · 四库本 513 卷正文 · 对称窗口 ±5 与 ±10 词元<br>
  Fisher 精确检验（单侧，BH 校正）＝显著性 · logDice＝强度 · jieba＋用户词典（繁转简，关闭 HMM）</p>
</header>
<div class="cards">
  <div class="card"><h2>语料与目标词</h2>
    <p>正文 4,149,461 字（李焘自注 730,404 字另计，不混入统计）</p>
    <p><span class="big">31</span> 次出现（另有自注 2 次）</p>
    <p>族词：冗員 19 · 冗兵 34 · 冗費 40 · 冗食 26 · 濫官 8 · 濫賞 14</p></div>
  <div class="card"><h2>搭配画像（验证后）</h2>
    <p>顶部搭配：<em>去</em>、汰、裁、省、减 —— 全部通过 FDR 校正</p>
    <p>"处方动词"群与"原因名词"群（<i class="c">奏荐、任子、磨勘、侥幸</i>）在数据上可分</p>
    <p>"四色""良吏"出自富弼卷 143《冗官利害六事》</p></div>
</div>
<nav>{nav}</nav>
{''.join(sections)}
<div class="read">
  <h3>诊断与处方：数据怎么说</h3>
  <ol>
    <li><em>"处方"动词主导</em>：两窗口下"去"（11–12 次共现，p&lt;10⁻¹²）遥居首位，汰、裁、省、减紧随其后——《长编》中"冗官"首先是一个<em>等待裁除的对象</em>，搭配词汇几乎全是处置动词。</li>
    <li><em>原因侧证据</em>：范仲淹卷 143"复更每岁奏荐，积成冗官"；富弼"今天下官有定员，而入仕之人无定数，既不黜陟，冒滥者多"。全书记词密度：磨勘 858 次（291 卷）、侥幸 287 次、任子 45 次——因果词汇的体量远大于目标词本身。</li>
    <li><em>议论的周期性</em>：31 次中 14 次集中于卷 143（仁宗庆历三年九月，范仲淹十事＋富弼六事）；其余覆盖淳化（卷 32）、治平（161/166/167）、熙宁（254/262）、元祐（355/361/376/386）、徽宗朝（402/413）——庆历、熙宁、元祐三个改革周期的议论均可见。</li>
    <li><em>精读入口</em>：卷 143 → 卷 140（庆历三年三月）→ 卷 262（熙宁"诏减将作监冗官十六员"）→ 卷 32（淳化"省冗官"）。</li>
  </ol>
</div>
<p class="note">共现＝目标词居中窗口内出现次数；期望＝按列联表独立性计算的期望值；全局频次＝全书词元数；p 值＝Fisher 精确检验（单侧 greater），FDR 后 p＝Benjamini-Hochberg 校正；logDice≤14（越高越强）。
红色＝处置动词（处方），蓝色＝原因名词（诊断），金色＝关键名词。四库本无标点，以卷为分词单位，窗口不跨卷。生成：changbian/analyze.py · 本页 make_overview.py。</p>
</div></body></html>"""
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT} ({len(html)} chars)")


if __name__ == "__main__":
    main()
