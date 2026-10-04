# 最近一次 Git push 之后的改动

本说明依据本地 Git push 记录及 `git diff origin/yiyu` 整理，记录最终实现。

- 分支：`yiyu`
- 对比基线：`d9ca468`（提交信息：`web`）
- 最近一次 push：2026-10-04 12:09:50，Europe/Zurich（UTC+02:00）
- 范围：该提交之后的当前工作区改动，包括已暂存和未暂存的内容。

## 1. 分类筛选与隐藏节点的关联路径

修复隐藏 Publications 等分类后，仍勾选的 Diseases、Genes 等节点失去关联或被一起隐藏的问题。

- 取消勾选某一分类时，该分类的节点隐藏，包括属于该分类的搜索中心。
- 其他仍勾选的分类继续显示，不再因为中间节点被隐藏而删除下游节点。
- 经过隐藏节点的已有路径折叠为虚线；点击后可查看路径中的原始关系、说明和来源。
- 折叠路径只是显示方式，不表示新增的直接关系，也不修改后台证据图谱。
- 保留直接连线，额外折叠路径只用于连接尚未连通的部分，优先选择连接搜索中心的路径，避免共享论文生成大量重复虚线。
- 同一搜索中心刷新图谱时保留分类勾选状态；切换到不同搜索中心时重新初始化分类。
- 缺少分类的节点按 `Other` 处理，避免绕过筛选。
- 图上总节点数和总连线数显示当前可见数量；左侧分类数量仍表示后台返回图谱中的分类总数。

## 2. 节点选择与悬浮状态

修复点击节点后整张图被重建、悬浮淡化状态残留，导致节点看起来消失的问题。

- 点击节点或连线只更新选中样式和详情，不重建 SVG。
- 筛选等操作需要重绘时，清除残留的悬浮高亮状态。
- 拖动、连线位置更新及邻域高亮使用当前可见连线，包括折叠路径。
- 从社群或研究人员详情进入图谱时，先更新图谱显示，再选中目标节点。

## 3. 图谱可读性

- 最小节点半径调整为 6 个 SVG 单位，使连接较少的节点也能显示分类颜色。
- 节点大小仍随原始有记录的连接数量变化，但不再严格按面积比例缩小到难以辨认。
- 折叠路径采用更细、更淡的虚线，降低连线对节点和文字的遮挡。
- 悬浮时保留其他节点的颜色，只淡化无关连线和节点标签。
- 新增“经过隐藏节点的关联路径”图例。

## 4. 研究术语与中文翻译

侧栏标题改为 `Research network`，说明改为 `Biological mechanisms, shared phenotypes, and research infrastructure.`。

| 原文案 | 新文案 | 中文 |
| --- | --- | --- |
| Symptoms in common | Shared phenotypes | 共有表型 |
| How nerve cells send signals | Synaptic vesicle release | 突触囊泡释放 |
| How nerve cells clear signals | GABA reuptake | GABA 再摄取 |
| Patient registries & research resources | Research infrastructure | 研究基础设施 |
| Published research | Scientific literature | 科学文献 |
| Symptoms & traits | Phenotypes | 表型 |
| Genetic changes | Genetic variants | 遗传变异 |
| Your search | Search context | 检索上下文 |

新增路径说明和候选图例的中文翻译。

## 5. 研究假设开关

修复取消 `Show research hypotheses` 后，疾病和基因的检索、自动标注候选也被过滤掉的问题。

- 区分研究假设与两类元数据候选：`identity_search_candidate`、`automatically_annotated_mention`。
- 只有同时具有 `metadata_only` 标记和上述关系类型的候选保留；其他推断关系仍受研究假设开关控制。
- 候选保留 `inferred` 状态，并提示需要核对来源与身份，不将其升级为已确认的生物学关系。
- 候选使用独立点线样式及 `Search & annotation candidates` 图例，不计入界面中的研究假设数量。
- 来源完整性和可信度过滤仍然生效，因此关闭假设开关不意味着保留所有低可信度或缺少来源的节点。

## 6. 修改文件

| 文件 | 改动 |
| --- | --- |
| `atlas/graph.py` | 区分元数据候选与研究假设，调整过滤和核验提示 |
| `web/app.js` | 可见图谱、折叠路径、路径详情、筛选状态、选择交互、节点大小及计数 |
| `web/styles.css` | 节点颜色可见性、折叠路径与候选连线样式 |
| `web/index.html` | 侧栏正式文案与新增图例 |
| `web/i18n.js` | 新增中英文术语与说明映射 |
| `scripts/check_people_ui.py` | 增加筛选、选择、折叠路径、虚线数量和颜色的浏览器回归检查 |
| `tests/test_live_graph.py` | 增加关闭研究假设后仍保留元数据候选的测试 |

## 7. 已完成的验证

后端相关测试共 27 项通过：

```powershell
python -m unittest tests.test_live_graph.LiveGraphTests tests.test_atlas.EvidenceTests tests.test_leads
```

图谱交互和视觉调整完成后，浏览器回归脚本通过，覆盖分类状态保留、节点点击不重建、隐藏分类后路径可查看、重新勾选恢复、节点颜色和最小尺寸，以及原有中英文和响应式检查。该轮浏览器检查在最后一次研究假设过滤及候选图例调整之前完成；最后一次过滤调整已由上述后端测试验证。

浏览器脚本默认访问本地 8017 端口，可在两个终端中运行：

```powershell
python -m atlas.server --port 8017
```

```powershell
python scripts/check_people_ui.py
```

脚本需要本地 Chrome 和 `websocket` Python 模块。上述回归使用本地数据和测试构造的图谱，不代表对所有在线检索结果的逐项核验。

## 8. 生效与范围说明

- `atlas/graph.py` 的变更需要重启 Python 服务；前端修改需要刷新页面。
- 社群官网简介、来源链接以及悬浮详情中的简介已经包含在基线 `d9ca468` 中，不属于这次 push 之后的新增改动。
- 研究人员与机构的官网联系方式抓取没有在本次改动中新增。
- 工作区另有 `data/people-ui-profile/` 下的浏览器缓存、日志等变化，它们来自浏览器验证，不属于产品功能改动。
- 本次仅整理变更文档，没有执行新的 commit 或 push。
