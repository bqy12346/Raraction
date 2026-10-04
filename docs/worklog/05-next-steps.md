# 05 待办与下一步

## 马上要做：运行 OpenAI 步骤

1. 在仓库根目录新建 `.env`（已被 git 忽略），写入：

   ```
   OPENAI_API_KEY=sk-...
   # 可选，默认 gpt-5
   OPENAI_MODEL=gpt-5
   ```

2. 依次运行：

   ```
   python3 pipeline/extract_claims.py   # 约 226 次调用，每篇有摘要的论文一次
   python3 pipeline/build_slice.py
   python3 pipeline/explain.py          # 约 25 次调用：12 条线索，加上第一圈疾病的缺口说明
   python3 pipeline/build_slice.py && python3 pipeline/build_view.py
   ```

3. 检查输出：
   - `extract_claims.py` 会打印被丢弃的论断数量和原因（引用对不上原文、基因不对、疾病 ID 不在列表里）。如果"引用对不上"的比例很高，就需要调整提示词。
   - 人工抽查 20 条抽取结果：引用是否支持结论，置信度是否合理。
   - 重点看 STXBP1：预计有功能丧失（单倍剂量不足）的论断，也可能有显性负效应的论断，这两类会互相标为矛盾。
   - 重点看 GLS：预计白内障这种病会被识别为功能获得，从而出现第一个真正的反例。
   - 打开 `views/journey.html#d=MONDO:0012812&lead=MONDO:0032900&p=maria`，查看解释、下一步和提案草稿。

这两个脚本只验证过语法和数据流，**还没有真正调用过 API**，第一次运行可能需要调试。

## 计划中还没做的（P1）

| 项 | 对应 PDF | 想法 |
|---|---|---|
| 10× 时间线 | Think Bigger | 选"启动共享自然史研究"作为里程碑。对比单个社区从零建注册库的时间线，和借助现有资源（ESCO、STARR、Simons Searchlight、RARE-X）的时间线，写清楚每个假设 |
| 1 分钟演示脚本 | What to Submit | 用网址锚点串起来：搜 STXBP1 → VAMP2 线索 → 证据 → Simons Searchlight → 下一步；再演示一个没有路径的疾病（如 PPFIA3）的诚实缺口 |
| 整个图谱的细粒度聚类 | Module 3 | 用 Reactome 中间层，或在邻居图上做社区发现，解决溶酶体病被拆散的问题 |
| 扩到更多切片 | Module 1 | 管道只依赖 `slice.py` 里的种子疾病；患者组织候选清单需要按新切片重新搜索 |

## 以后再做（P2）

- 合并为单文件 SQLite 或 DuckDB，加全文检索。
- 部署：页面是静态的，任何静态托管都可以。只有在需要对任意路径实时生成解释时，才需要后端。

## 风险和局限

- **患者组织不全**：候选清单靠人工搜索，NORD 和 Orphanet 的组织目录没有开放接口。CPLX1、GAD1、GLS、SLC32A1、PPFIA3、TSPOAP1 目前没有找到组织，界面会如实显示为缺口。
- **研究者匹配**：按姓名和单位词匹配，仍可能误合并或误拆分。界面标注了"identity not verified"。
- **论文只读摘要**：全文里的证据读不到；摘要的结论可能比正文更强。
- **NIH RePORTER 只覆盖美国联邦资助**：欧洲的资助（如 ESCO 背后的资金）看不到。
- **ClinVar 变异谱推断很粗糙**：30% 截断型这个阈值是经验值，只作为"仅提示"使用。
- **时效性**：所有数据的检索日期是 2026-10-04。临床试验状态和组织网页会变化，重新运行抓取脚本即可更新。
