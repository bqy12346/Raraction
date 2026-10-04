# 06 界面合并：cluster view 作为唯一界面

日期：2026-10-04

## 决定

| 问题 | 选择 |
|---|---|
| 最终界面用哪个 | [views/atlas_cluster_view.html](../../views/atlas_cluster_view.html)：覆盖全部 7,999 种疾病，布局最接近 PDF 第 4 页的示意图 |
| 切片以外的疾病怎么办 | 丰富数据（患者组织、研究、研究者、线索判定）先只覆盖 STXBP1 切片的 42 种疾病；其他疾病只显示图谱数据，并明确写出"尚未覆盖" |
| 原来的 journey 页面 | 删除，功能并入 cluster view，只保留一个入口 |

## 合并方式

三栏布局保持不变，下方新增一个全宽的旅程区域。这对应 PDF 里"先看摘要，点击再看细节"（Progressive reveal）的原则。

| 位置 | 内容 |
|---|---|
| 顶部 | 全局搜索 |
| 左栏 | 机制聚类列表；底部新增 "Viewing as" 角色切换，位置与 PDF 示意图一致 |
| 中间 | 邻居地图。颜色仍代表机制聚类；切片内的邻居多了一圈外环，颜色代表线索判定 |
| 右栏 | 所选疾病的摘要。切片内的疾病：机制显示确认级别和证据，"Key investigators"和"Patient groups"显示真实数量（原来是 "not loaded yet"），并有一个 "Explore connections →" 按钮；邻居列表加上判定标签 |
| 下方旅程区 | 按角色显示：Maria 看线索列表和详情、现有社区、网络重叠、缺口、反例；Devon 看患者社区；Priya 看按机制排序的表格；Dr. Osei 看跨基因的研究者。切片外的疾病显示"尚未覆盖"说明，并列出开放数据库里也缺的信息 |
| 侧栏 | 证据详情、节点详情、症状对应的疾病列表 |

## 搜索范围

| 内容 | 范围 | 数据来源 |
|---|---|---|
| 疾病名、基因 | 全图谱 | `atlas_view.json` |
| 症状 | 全图谱，10,291 个 HPO 症状 | `build_view.py` 从 `data/atlas/edges.tsv.gz` 生成症状索引 |
| 疾病同义词 | 切片 | MONDO 同义词（来自 EBI OLS），已提交的图谱文件里没有同义词 |
| 患者组织、通路、研究、药物 | 切片 | `slice_view.json` |

Priya 的视图分两部分：全图谱部分按 Orphanet 标注的功能方向，统计各机制聚类里的疾病数；切片部分列出基因的证据、患者组织、研究、资助和研究者。

## 改动的文件

| 文件 | 改动 |
|---|---|
| `views/src/atlas.template.html` | 新增。合并后的界面模板，包含三个数据占位符 |
| `pipeline/build_view.py` | 改写。读取图谱数据、切片数据，生成症状索引，写出 `views/atlas_cluster_view.html` |
| `views/atlas_cluster_view.html` | 由脚本重新生成，4.07 MB。原来的数据是手工嵌进页面的，没有生成步骤 |
| `views/journey.html`、`views/src/journey.template.html` | 删除 |
| `pipeline/build_slice.py` | 研究者桥梁的单位匹配更严格（见下） |
| `README.md`、`docs/worklog/*` | 更新对界面的描述 |

## 检查

用无头 Chrome 渲染了四种状态，截图检查，控制台没有错误：

1. 种子疾病，Maria 视图
2. STXBP1 ↔ VAMP2 线索详情
3. Gaucher 病（切片外）
4. Priya 视图

## 这一轮发现并修正的问题

### 右栏太长，旅程区被推到很下面

- **现象**：右栏的邻居列表有 10 项，每项都带分数和共享通路，高度超过 1,400 像素。点开的线索详情、切片外说明、Priya 的表格都被推到第一屏之外。
- **修正**：邻居列表固定最大高度 460 像素，内部滚动。

### 研究者"同一单位"的依据太弱

- **现象**：Dora Steel 只靠 "neurosciences" 一个词就被认定为同一单位，Manju Kurian 只靠 "child"。这些词在很多机构名里都会出现。
- **修正**：学科词（neuroscience、genetics、epilepsy 等）、国家名和虚词（from、with）不再作为单位依据。界面显示的"共同单位"改为两两重合的并集，与判定逻辑一致。
- **结果**：桥梁研究者从 11 位变为 10 位，每位都有具体的地名或机构名作为依据，例如 Glasgow、Queen Square、Austin/Florey、Kiel、Cambridge、Amsterdam、Northwestern、Yale。

## 还没做的

- 切片外的疾病要有完整旅程，需要用新的种子疾病重新运行整个管道（`pipeline/slice.py`），并重新搜索、核实患者组织。
- OpenAI 步骤运行后，重新执行 `build_slice.py` 和 `build_view.py`，解释和提案就会出现在线索详情里。
