# Project Proposal (draft)

## Author(s)

*(Your name here; up to 3 group members)*

## Tentative title

**Collocates of 冗官 in the *Xu Zizhi tongjian changbian*: How Northern Song Literati Diagnosed and Treated Official Redundancy**

## Research questions

1. **Methodological question.** Are the words that appear around 冗官 ("superfluous offices") *genuinely strong collocates* in the statistical sense — co-occurring significantly more often than chance expectation (Fisher's exact test with FDR correction), and with sufficient strength of association (logDice)? Which are merely accidental neighbours of high-frequency function words?
2. **Question of causes.** Starting from the validated collocates and concordance lines, what did Northern Song literati themselves attribute official redundancy to — hereditary privilege (恩蔭/任子), unrestricted entry into officialdom, routine promotion without demotion (磨勘), and layered bureaucratic structures — and how is this causal vocabulary distributed across the data?
3. **Question of remedies.** What measures did the court actually adopt — curbing privilege and enforcing evaluation (慶曆), consolidating offices and agencies (熙寧/元豐), cutting clerk quotas (元祐) — and are the "remedy" and "cause" vocabularies separable in the collocational profile?

## Data

**Source.** Li Tao's *Xu Zizhi tongjian changbian* (續資治通鑑長編), the Siku quanshu edition on Chinese Wikisource, public domain, downloaded in full via the MediaWiki API. The original work runs to 520 juan; this edition preserves 513 (the seven missing juan are lost in the transmitted edition itself).

**Scale.** Main text ≈ 4,149,461 characters (≈ 1.5 million tokens across 129,982 segmentation units); Li Tao's critical notes, ≈ 730,404 characters, were separated out and tagged, and are excluded from the statistics. The target word 冗官 appears 31 times in the main text (twice in the notes); cluster terms: 冗員 ×19, 冗兵 ×34, 冗費 ×40, 冗食 ×26, 濫官 ×8, 濫賞 ×14.

**Digitization effort.** Already complete. The Wikisource text is a pre-existing digital transcription, so no OCR was needed; the full pipeline — download of all 513 juan, cleaning (stripping wikitext templates, extracting reign-date headers, separating Li Tao's notes), and segmentation (traditional→simplified conversion, jieba with HMM disabled, a user dictionary securing the 冗-cluster and institutional terms) — is fully scripted and runs in a few hours of machine time. Residual issues: some 8,000 missing characters in the Siku transcription (marked □) and the absence of punctuation (the juan is the window unit); both are documented in the README.

**Is it enough data?** For collocation analysis, 31 occurrences of the target is a small sample, but three things make it workable. First, Fisher's exact test was chosen over large-sample approximations precisely for small counts. Second, the cluster terms (冗員， 濫官， etc.) and the pooled target (冗官＋冗員) provide cross-validation; pilot runs show a stable profile. Third, all 31 occurrences can be read closely one by one, so statistics and close reading can discipline each other — here the small N is not a defect but a methodological feature. If expansion is needed, the *Song huiyao jigao*, "Zhiguan" section, can serve as a comparison corpus.

## Methods

Collocation analysis (the course method), supported by KWIC concordances and a keyword-density table as a close-reading map:

- **Tools and parameters.** qhchina `find_collocates`; symmetric windows of ±5 and ±10 tokens (contrasting two definitions of "nearby" is itself part of the analysis); target 冗官, plus the pooled target 冗官＋冗員.
- **Significance.** Fisher's exact test (one-sided, greater) with Benjamini–Hochberg FDR correction — exact inference is chosen precisely because the count is small (31).
- **Strength.** logDice, set against significance to distinguish rare-but-tight from frequent-but-loose collocates (Evert 2008).
- **Preprocessing.** Traditional→simplified conversion (OpenCC); jieba segmentation with HMM disabled (its new-word discovery coins non-words in classical prose), with a user dictionary securing the 冗-cluster, proper names, and institutional terms (差遣， 磨勘， 任子， 僥倖， etc.); every occurrence window checked by eye.
- **From statistics to history.** The validated collocates are used in three groups: action verbs (去， 汰， 裁， 省， 減 — "remove, weed out, cut, trim, reduce") mark the *prescriptions*; causal nouns (奏薦， 任子， 磨勘， 僥倖) mark the *diagnoses*; the density table locates the juan where the debate concentrates (14 of 31 hits in juan 143: Fan Zhongyan's ten-point memorial and Fu Bi's six-point case for cutting 冗官)， and KWIC lines support close reading with citations.

**Pilot results** (complete and reproducible): 去 (11–12 co-occurrences, FDR-adjusted p < 10⁻⁶) ranks first, followed by 汰， 裁， 省， 減 (all survive correction); 四色 ("four categories" of unfit officials) and 良吏 enter the top ranks by logDice — the collocational profile of 冗官 in the *Changbian* is almost entirely made of "prescription verbs," and cause vocabulary and remedy vocabulary are separable in the data.

## Preliminary references

- Evert, Stefan. "Corpora and Collocations." In *Corpus Linguistics: An International Handbook*, edited by Anke Lüdeling and Merja Kytö. Mouton de Gruyter, 2008. (collocation measures)
- Chaffee, John W. *The Thorny Gates of Learning in Sung China: A Social History of Examinations.* Cambridge University Press, 1995. (examinations and hereditary privilege)
- Deng, Xiaonan. 鄧小南， *Zuzong zhi fa: Bei Song qianqi zhengzhi shulüe* (The way of the ancestors: A sketch of early Northern Song politics). Sanlian Shudian, 2006. (checks, balances, and institutional inertia)
- Miao, Shumei. 苗書梅， *Songdai guanyuan xuanren he guanli zhidu* (The selection and management of Song officials). Henan University Press, 1996. (quan-reduo-que-shao — more candidates than posts)
- Wang, Shengduo. 汪聖鐸， *Liang Song caizheng shi* (A fiscal history of the two Songs). Zhonghua Shuju, 1995. (the fiscal frame of the "three redundancies")
- Pei, Rucheng, and Xu, Peizao. 裴汝誠、許沛藻， *Xu Zizhi tongjian changbian kaolüe* (A study of the Changbian's textual history). Shanghai Guji Chubanshe, 1985.
