# 03 改动清单

所有改动都还没有提交。原有的图谱文件（`data/atlas/`、`views/atlas_cluster_view.html`、`views/demo_graph.html`）没有改动。

## 修改的文件

| 文件 | 改动 |
|---|---|
| [README.md](../../README.md) | 开头改为两层结构（图谱 + 切片），删掉了过时的分支名 `yuzhu`；新增"The STXBP1 slice"一节，包括架构图、证据规则、数据量、复现步骤；补充已知局限和数据来源；更新"Not built yet" |
| [.gitignore](../../.gitignore) | 忽略 `data/slice/cache/*`（原始 API 响应约 150 MB），但保留 `data/slice/cache/openai/`（模型回答要提交）。同时修了一个 bug：原文件末尾没有换行，追加内容时粘到了 `data/raw/` 那一行，已拆开 |

## 新增：管道脚本 [pipeline/](../../pipeline/)

全部只用 Python 标准库，按顺序运行。

| 步骤 | 脚本 | 做什么 | 产出 |
|---|---|---|---|
| 公共 | [common.py](../../pipeline/common.py) | 带缓存的 HTTP 请求（不缓存出错的响应）、TSV 读写、和图谱一致的 14 列边格式、按姓名生成研究者 ID、OpenAI structured outputs 调用（从 `.env` 读 Key） | — |
| 0 | [slice.py](../../pipeline/slice.py) | 从图谱里取出切片；从 EBI OLS 拿 MONDO 同义词 | `slice.json`、`parts/atlas_*` |
| 1 | [fetch_clinvar.py](../../pipeline/fetch_clinvar.py) | 通过 E-utilities 拿致病和可能致病变异；结果太大时自动拆小批次；按变异谱推断机制 | `parts/clinvar_*` |
| 2 | [fetch_trials.py](../../pipeline/fetch_trials.py) | ClinicalTrials.gov API v2；按结构化字段判断资产类型（注册库、自然史研究、干预试验） | `parts/trials_*` |
| 3 | [fetch_pubmed.py](../../pipeline/fetch_pubmed.py) | 每个基因约 30 篇和机制相关的论文，限定神经领域；保留第一作者和最后作者 | `parts/pubmed_*`、`parts/pubmed_abstracts.json` |
| 4 | [fetch_reporter.py](../../pipeline/fetch_reporter.py) | NIH RePORTER，2021 年以后的资助项目，按核心项目号合并多个财年 | `parts/reporter_*` |
| 5 | [fetch_orgs.py](../../pipeline/fetch_orgs.py) | 抓取患者组织的原网页，逐句核实候选关联 | `parts/orgs_*` |
| 6 | [extract_claims.py](../../pipeline/extract_claims.py) | **OpenAI**：从摘要抽取机制论断和资产，逐字校验引用，标出相互矛盾的论断 | `parts/extract_*`（未运行） |
| 7 | [build_slice.py](../../pipeline/build_slice.py) | 合并所有来源；机制、社区、桥梁、线索、反例、缺口 | `nodes.tsv`、`edges.tsv`、`slice_view.json` |
| 8 | [explain.py](../../pipeline/explain.py) | **OpenAI**：给每条线索写解释和提案，给每个缺口写下一步问题，校验引用的边编号 | `explanations.json`（未运行） |
| 9 | [build_view.py](../../pipeline/build_view.py) | 把数据嵌进界面模板，生成单个 HTML 文件 | `views/journey.html` |

运行方法：

```
python3 pipeline/slice.py
python3 pipeline/fetch_clinvar.py
python3 pipeline/fetch_trials.py
python3 pipeline/fetch_pubmed.py
python3 pipeline/fetch_reporter.py
python3 pipeline/fetch_orgs.py
python3 pipeline/extract_claims.py   # 需要 OPENAI_API_KEY（放在仓库根目录的 .env 里）
python3 pipeline/build_slice.py
python3 pipeline/explain.py          # 需要 OPENAI_API_KEY
python3 pipeline/build_slice.py && python3 pipeline/build_view.py
```

没有 Key 时，跳过两个 OpenAI 步骤，界面照常生成，只是机制停留在"仅提示"，解释部分显示按规则生成的文字。

## 新增：数据 [data/slice/](../../data/slice/)

| 文件 | 内容 |
|---|---|
| `slice.json` | 切片定义：12 个基因、42 种疾病、同义词 |
| `patient_orgs_seed.tsv` | 人工搜索得到的患者组织候选清单（31 行，29 行通过核实） |
| `parts/<来源>_{nodes,edges}.tsv` | 每个来源各自的节点和边 |
| `nodes.tsv`、`edges.tsv` | 合并后的切片图谱，列格式和 `data/atlas/` 一致 |
| `slice_view.json` | 界面所需的数据（0.77 MB） |
| `cache/` | 原始响应缓存。只有 `cache/openai/` 会被提交 |

合并后的数据量：

| | 数量 |
|---|---|
| 节点 | 2,788：疾病 42、基因 12、症状 569、通路 37、变异 1,263、研究 23、组织 90、研究者 440、论文 230、资助项目 54、资助方 14、干预 12、机制 2 |
| 边 | 4,509：observed 4,448，inferred 61 |
| 桥梁 | 研究者 11、组织 2、研究 3、资助方 3 |

## 新增：界面

| 文件 | 内容 |
|---|---|
| [views/src/journey.template.html](../../views/src/journey.template.html) | 界面模板，`__DATA__` 是数据占位符 |
| [views/journey.html](../../views/journey.html) | 生成好的单文件页面（0.81 MB），直接在浏览器打开 |

主要功能：

- 全局搜索：疾病、同义词、基因、症状、患者组织、通路、研究、药物
- 四个角色视图：Maria、Devon、Priya、Dr. Osei
- 邻居地图：按判定结果着色，虚线表示推断的关联
- 线索详情：证据链（每个箭头都可以点开）、两边的机制对比、判定理由、可复用的东西、下一步
- 证据侧栏：来源链接、日期、证据类型、置信度、原文引用、矛盾证据
- 网址锚点：例如 `journey.html#d=MONDO:0012812&lead=MONDO:0032900&p=maria`
- 深色模式，窄屏时变为单栏

## 新增：文档

| 文件 | 内容 |
|---|---|
| `docs/05.pdf` | 需求文件（用户提供） |
| `docs/worklog/` | 本工作记录 |
