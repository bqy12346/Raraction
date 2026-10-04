# 工作记录：对照 Challenge 05 的升级

日期：2026-10-04　分支：`boxuan/tryout`　状态：未提交

## 一句话总结

需求（[docs/05.pdf](../05.pdf)）要的是：帮患者组织负责人 Maria 走完一条完整的路径，从一个诊断出发，找到有证据支持的关联疾病、可复用的资产、可以联系的合作者，最后得到具体的下一步。原有仓库已经有一个覆盖 7,999 种单基因病的"生物学底座"图谱，但缺少人、资产、文献这几类节点，也还没有用到 AI。

这一轮选了 STXBP1 作为切片，把整条旅程打通：新增 6 个数据来源、一套合并与分析逻辑，以及一个旅程界面。OpenAI 的两个步骤代码已经写好，等 API Key 到位后运行。

## 文件

| 文件 | 内容 |
|---|---|
| [01-gap-analysis.md](01-gap-analysis.md) | 逐条对照 PDF 的检查表：做之前缺什么，现在补到了哪一步 |
| [02-design.md](02-design.md) | 思路：为什么选 STXBP1，OpenAI 承担什么角色，证据规则和判定规则 |
| [03-changes.md](03-changes.md) | 改动清单：新增和修改了哪些文件，每一步产出什么，怎么运行 |
| [04-issues-and-fixes.md](04-issues-and-fixes.md) | 过程中发现的问题和修正，大多是"看起来对、其实错"的情况 |
| [05-next-steps.md](05-next-steps.md) | 还没做的事、风险，以及运行 OpenAI 步骤的方法 |
| [06-ui-merge.md](06-ui-merge.md) | 把 journey 页面并入 cluster view、作为唯一界面的思路和改动 |

## 当前状态

| 部分 | 状态 |
|---|---|
| 数据：ClinVar、ClinicalTrials.gov、PubMed、NIH RePORTER、患者组织 | 已完成，并已运行 |
| 合并分析：机制、线索判定、网络重叠、缺口 | 已完成，并已运行 |
| 界面 [views/atlas_cluster_view.html](../../views/atlas_cluster_view.html) | 已完成：journey 功能已并入 cluster view，成为唯一界面；用无头 Chrome 截图检查过四种状态，没有控制台错误 |
| OpenAI Extract（读论文抽机制）和 Explain（通俗解释、提案） | 代码已写，**未运行**（缺 API Key） |
| 10× 时间线、演示视频脚本 | 未开始 |
