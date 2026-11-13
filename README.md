# rongguan-collocations

**「冗官」的搭配词研究：北宋士人如何诊断与医治官冗**

Collocation study of 冗官 ("superfluous offices") in Li Tao's *Xu Zizhi
tongjian changbian* (續資治通鑑長編, Northern Song chronicle, 960–1127).

研究问题：① "冗官"周边的词是否在统计意义上是真正的强搭配词（Fisher
精确检验 + FDR 校正；logDice）；② 北宋士人把官冗归因于什么（恩荫、入仕
无定数、磨勘不黜陟、机构叠构）；③ 朝廷实际采用了什么对策（庆历抑侥幸、
熙宁省官、元祐裁汰吏额）。

## 仓库结构

```
├── README.md                 本文件
├── proposal/                 项目计划书（中英文，docx + md）
├── changbian/                分析项目（自包含，可独立运行）
│   ├── download.py             维基文库 API 下载 513 卷 wikitext
│   ├── clean.py                清洗：模板处理、正文/李焘自注分离
│   ├── analyze.py              分词 + find_collocates（4 个运行）+ 密度表 + KWIC
│   ├── user_dict.txt           jieba 用户词典（冗词族 + 制度词）
│   ├── data/                   语料（正文 4,149,461 字；自注 730,404 字）
│   └── results/                搭配词 CSV ×4、关键词密度表、KWIC 检索行
├── make_overview.py          生成 冗官搭配词.html（结果总览页）
├── top10_passages.py         提取前十名搭配词的原文段落并注入总览页
├── 冗官搭配词.html            结果总览页（含 48 段原文检索行）
└── requirements.txt
```

## 复现步骤

```bash
pip install -r requirements.txt

cd changbian
python download.py     # 从中文维基文库下载 513 卷（约 1 分钟）
python clean.py        # 清洗并分离李焘自注
python analyze.py      # 4 个搭配运行 + 密度表 + KWIC（约 2 分钟）
cd ..

python make_overview.py     # 重建总览页
python top10_passages.py    # 注入前十名搭配词的原文段落
```

## 语料与权利

- 李焘《续资治通鉴长编》，中文维基文库"四庫全書本"
  （https://zh.wikisource.org/wiki/續資治通鑑長編_(四庫全書本)），
  公有领域（public domain）。
- 原书 520 卷，该本存 513 卷（卷 25、141、180、302、359、366、383 为
  传世本所缺）。正文共 4,149,461 字；李焘自注（12,955 条，730,404 字）
  已单独切分，不混入统计。
- "冗官"正文出现 31 次（自注 2 次）；族词：冗員 19、冗兵 34、冗費 40、
  冗食 26、濫官 8、濫賞 14。

## 方法摘要

- 分词：繁转简（OpenCC）→ jieba（**关闭 HMM**，文言文新词发现会凭空
  造词）→ 用户词典。四库本无标点，以卷为窗口单位（不跨卷）。
- 搭配：qhchina `find_collocates`，对称窗口 ±5 与 ±10；目标词 冗官 及
  合并目标 冗官＋冗員。
- 显著性：Fisher 精确检验（单侧 greater）+ Benjamini–Hochberg FDR 校正
  ——目标词仅 31 次，大样本近似不可靠。
- 强度：logDice（区分"罕见而紧密"与"高频而松散"）。

## 主要发现

- "冗官"的最强搭配几乎全部是处置动词：**去**（11–12 次共现，
  FDR 后 p < 10⁻⁶）居首，汰、裁、省、减紧随——该词在《长编》中首先
  是一个**等待裁除的对象**。
- 31 次中 14 次集中于卷 143（仁宗庆历三年九月）：范仲淹《答手诏条陈
  十事》"抑侥幸"条 + 富弼《冗官利害六事》——庆历新政前夜的核心文献。
- 原因词汇（奏荐、任子、磨勘、侥幸）与对策词汇（去、汰、裁、省、减）
  在数据上可分；"三冗"（冗官·冗兵·冗费）的词汇耦合在族词统计中
  已见雏形。

## 工具版本

Python 3.14 · jieba 0.42.1 · qhchina 0.2.7 · opencc-python-reimplemented
0.1.7 · pandas 3.0.6 · scipy 1.18.1
