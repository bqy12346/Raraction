/* UI localization only: publication titles, abstracts and evidence stay verbatim. */
'use strict';
(() => {
  const zh = {
    'Audience':'身份',
    // First-visit intro (intro.js).
    "Who's exploring today?":'请选择你的身份', 'Patient & family':'患者与家属', 'I, or someone I love, lives with a rare disease.':'我或我爱的人正在面对罕见病。',
    'Expert':'专家', 'I research, treat or develop therapies for rare diseases.':'我从事罕见病的研究、诊疗或疗法开发。', 'You can change this anytime in the top right.':'之后可随时在右上角更改。',
    'Toggle legend size':'切换图例大小',
    'Refresh papers & studies':'刷新论文与研究', 'AI tools':'AI 工具',
    // Connection details & source evidence (graph detail panel; curated starter text and live-graph templates).
    'collapsed':'折叠路径', 'symptom':'症状', 'Seizure':'癫痫发作', 'Hypotonia':'肌张力低下', 'Global developmental delay':'全面发育迟缓', 'Developmental delay':'发育迟缓',
    'STXBP1-related disorder':'STXBP1 相关疾病', 'SLC6A1-related disorder':'SLC6A1 相关疾病',
    'Reduced GABA reuptake':'GABA 再摄取减少', 'Reduced synaptic vesicle release':'突触囊泡释放减少',
    'associated with gene':'关联基因', 'has reported phenotype':'有报告的表型', 'has patient community':'有患者社群', 'represented in registry':'已纳入登记项目',
    'candidate shared research':'候选共同研究', 'discussed in publication':'在论文中讨论', 'named in study':'在研究中列名', 'loss of function affects':'功能丧失影响',
    'listed study collaborator':'列名的研究合作方', 'sponsored by':'申办方', 'authored by':'作者', 'same mechanism not established':'未确立相同机制',
    'identity search candidate':'身份检索候选', 'returned by literature search':'文献检索结果', 'returned by study search':'研究检索结果',
    'automatically annotated mention':'自动标注的提及', 'listed study contact':'列名的研究联系人', 'path through hidden nodes':'经过隐藏节点的关联路径',
    'Visit source ↗':'查看来源 ↗', 'Open source ↗':'打开来源 ↗',
    'Sources for the selected connection. Copies of one paper count as one source.':'所选联系的来源。同一篇论文的多个副本只计为一个来源。',
    'Sources for the selected node’s visible connections. Copies of one paper count as one source.':'所选节点当前可见联系的来源。同一篇论文的多个副本只计为一个来源。',
    'Curator assessment of directness and source coverage; not a clinical probability.':'整理者对关系直接程度和来源覆盖情况的评估，不是临床概率。',
    'Single source lineage; no independent corroboration established':'只有单一来源谱系，尚无独立佐证',
    'Research hypothesis; requires expert validation':'研究假设，需要专家验证',
    'Counterevidence or limitation must be reviewed':'需要审查反面证据或局限',
    'No traceable supporting source':'没有可追溯的支持来源', 'Missing or incomplete provenance':'来源记录缺失或不完整',
    'Search or annotation candidate; requires source and identity review':'检索或标注候选，需要核对来源与身份',
    'Provenance and consistency checks, not validation of scientific truth.':'这是来源与一致性检查，不是对科学结论的验证。',
    'Curated mechanism / research layer; not a validated disease taxonomy':'人工整理的机制/研究分层，不是经过验证的疾病分类',
    'Degree / (visible node count - 1), using observed edges only. Measures map connectivity, not medical importance.':'度 /（可见节点数 − 1），只计算有记录的边。衡量的是图谱连接程度，不代表医学重要性。',
    'No results posted in the downloaded record. Registration is not proof of benefit.':'下载的记录中没有发布结果。登记注册不代表有益处。',
    'Results posted in the downloaded record. Registration is not proof of benefit.':'下载的记录中已发布结果。登记注册不代表有益处。',
    'A developmental disorder affecting communication between brain cells.':'一种影响脑细胞之间信息传递的发育障碍。',
    'A neurodevelopmental disorder affecting GABA transport.':'一种影响 GABA 转运的神经发育障碍。',
    'Local stable disease identifier. Myoclonic-atonic epilepsy is broader than SLC6A1-NDD and is deliberately not used as an equivalent MONDO identity.':'本地稳定疾病标识符。肌阵挛-失张力癫痫的范围比 SLC6A1-NDD 更广，因此刻意不把它当作等同的 MONDO 身份。',
    'STXBP1 supports vesicle docking and fusion; loss of function impairs neurotransmitter release.':'STXBP1 参与囊泡停靠与融合；功能丧失会削弱神经递质释放。',
    'SLC6A1 encodes GAT-1, which transports GABA into neurons and glia.':'SLC6A1 编码 GAT-1，负责把 GABA 转运进神经元和胶质细胞。',
    'Simons Searchlight links the STXBP1 community to this foundation.':'Simons Searchlight 将 STXBP1 社群与该基金会联系起来。',
    'Simons Searchlight includes STXBP1 research participation.':'Simons Searchlight 包含 STXBP1 的研究参与项目。',
    'SLC6A1 Connect describes participation in Simons Searchlight.':'SLC6A1 Connect 介绍了参与 Simons Searchlight 的方式。',
    'GeneReviews lists SLC6A1 Connect as a disease-specific organization.':'GeneReviews 将 SLC6A1 Connect 列为针对该疾病的组织。',
    'Different synaptic processes and overlapping observations suggest comparing registry measures, without assuming a common treatment.':'两者涉及不同的突触过程，但临床观察有重叠，提示可以比较登记库的测量指标，但不预设存在共同的治疗方法。',
    'Both affect neural communication, but the cited sources describe different molecular functions.':'两者都影响神经信息传递，但所引来源描述的是不同的分子功能。',
    'The study registry names this patient organization as a collaborator.':'研究登记记录将该患者组织列为合作方。',
    'Listed lead sponsor in the study registry.':'研究登记记录中列出的主要申办方。',
    'Named author on this publication; potential research contact subject to expertise and identity checks.':'该论文的署名作者；可作为潜在研究联系人，但需核实其专业领域和身份。',
    'Gene-level summary. Do not assume every variant has the same effect.':'这是基因层面的概括，不要假设每种变异的效应都相同。',
    'The full molecular pathology remains incompletely understood; variant-specific interpretation is needed.':'完整的分子病理机制尚未完全阐明，需要针对具体变异进行解读。',
    'A reported feature is not universal or diagnostic. Broad symptoms alone do not establish a shared mechanism.':'有报告的特征并非人人都有，也不能用于诊断。仅凭宽泛的症状不能确立共同机制。',
    'Vesicle release and GABA reuptake are different molecular mechanisms. Reuse is a proposal, not a validated cross-disease intervention.':'囊泡释放和 GABA 再摄取是不同的分子机制。复用只是一项提议，不是经过验证的跨疾病干预。',
    'Shared seizures and broad pathway language cannot justify treating these as the same mechanism.':'共同的癫痫发作和宽泛的通路描述，不足以把两者视为同一机制。',
    'Publication relevance is not confirmation of a specific mechanism or therapy.':'论文相关并不等于证实了某种具体机制或疗法。',
    'This person is listed as an author in the indexed publication.':'此人是该收录论文的署名作者。',
    'The registry lists this person as a study contact or official.':'登记记录将此人列为研究联系人或负责人。',
    'Listed lead study sponsor.':'列出的主要研究申办方。',
    'The reviewed directory links this disease or gene query to this community.':'经审核的名录将此疾病或基因检索与该社群关联。',
    'The identity service returned this term for the search; it is not asserted equivalent to the selected disease.':'身份检索服务为此次搜索返回了这个术语；并不表示它与所选疾病等同。',
    'Subtype and broad symptom matches require explicit identity review.':'亚型和宽泛症状的匹配需要明确的身份审核。',
    'Retrieval is not confirmation of a mechanistic relationship. This may be background or tangential evidence.':'被检索到不代表证实了机制关系，它可能只是背景或间接证据。',
    'Directory coverage is limited. Confirm current services and suitability with the organization.':'名录覆盖范围有限。请向该组织确认当前服务及是否适合。',
    'Automated entity normalization can be wrong. A mention is not a causal, therapeutic, or shared-mechanism claim.':'自动实体标准化可能出错。被提及不代表因果、治疗或共同机制的结论。',
    'Automatically annotated entity mention; biological meaning needs source review.':'自动标注的实体提及，其生物学含义需要核对来源。',
    'Publication-scoped identity and affiliation contact. Not disambiguated; current role and contact information must be verified.':'以论文为范围的身份和单位联系方式。尚未消歧，需核实当前职务和联系方式。',
    'Lead sponsor in the retrieved study record. The registry is a source link, not the institution website.':'检索到的研究记录中的主要申办方。登记记录只是来源链接，不是该机构的官网。',
    'Identity is unresolved or ambiguous. Choose an ontology candidate before interpreting disease-specific evidence.':'身份尚未解析或存在歧义。解读疾病特定证据之前，请先选择一个本体候选。',
    'Confidence in the stated metadata relationship only; not in disease causation, efficacy, or clinical applicability.':'可信度只针对所述的元数据关系，不涉及疾病因果、疗效或临床适用性。',
    'Live record type; not a validated biological mechanism cluster.':'实时记录类型，不是经过验证的生物学机制分组。',
    'Resolved by exact label or synonym.':'通过精确名称或同义词解析。',
    'The search took too long. Please try again.':'搜索时间过长，请重试。', 'Cross-origin requests are not allowed':'不允许跨站请求',
    'Live research map. Literature retrieval and automated mentions do not establish biological causation.':'实时研究图谱。文献检索和自动标注的提及不能确立生物学因果关系。',
    'Search result label and synonyms':'检索结果名称与同义词', 'Retrieved title, abstract and author list':'检索到的标题、摘要和作者列表',
    'Study search, conditions, status and eligibility':'研究检索：疾病、状态和入组条件', 'BioC annotations and character offsets':'BioC 标注及字符位置',
    'Reviewed community directory; exact disease/gene match':'经审核的社群名录；疾病/基因精确匹配', 'Author list':'作者列表',
    'Selected identity is not in the retrieved candidates':'所选身份不在检索到的候选中',
    // AI chat.
    'Ask your own question':'提出你自己的问题', 'Answers use only the sources in this map and show which ones they rely on.':'回答只使用当前图谱中的资料，并注明依据的来源。',
    'Ask about this condition, the research, or what to ask your care team…':'可以问这种疾病、相关研究，或者该向医护团队问些什么…',
    'Not medical advice. For decisions about your care, talk to your care team.':'这不是医疗建议。涉及治疗和照护的决定，请咨询你的医护团队。',
    'The AI assistant is not available on this server yet (no AI provider is configured).':'此服务器尚未启用 AI 助手（还没有配置 AI 服务）。',
    'The AI assistant is not available: no live AI provider is configured on this server.':'AI 助手暂不可用：此服务器还没有配置实时 AI 服务。',
    'What does this condition involve?':'这种疾病是怎么回事？', 'Which research or registries could I take part in?':'有哪些研究或登记项目可以参与？',
    'What should I ask my care team?':'我应该问医护团队哪些问题？', 'New conversation':'新对话', 'Sources':'来源', 'Send':'发送',
    'Ask a question':'提问', 'Conversation':'对话',
    // Sources & coverage dialog (text comes from atlas/graph.py coverage()).
    'Data sources':'数据来源', 'Baseline':'基线', 'Proposed':'设想目标', 'days':'天', 'Assumptions':'前提假设', 'How to validate':'验证方式',
    'Live disease, gene and symptom search across MONDO, HPO, NCBI Gene, PubMed, Europe PMC and ClinicalTrials.gov, with on-demand graphs. Curated STXBP1/SLC6A1 is a starter slice; no claim of complete coverage or validated biology for every rare disease.':'跨 MONDO、HPO、NCBI Gene、PubMed、Europe PMC 和 ClinicalTrials.gov 实时检索疾病、基因和症状，并按需生成图谱。人工整理的 STXBP1/SLC6A1 只是入门示例；不声称覆盖全部罕见病，也不声称每种罕见病的生物学机制都已验证。',
    'GeneReviews / verified community sites':'GeneReviews / 经核实的社区网站', 'OpenAlex / NIH RePORTER / model databases':'OpenAlex / NIH RePORTER / 模型数据库',
    'snapshot + live lookup':'快照 + 实时查询', 'live adapters + paper snapshot':'实时接口 + 论文快照', 'live adapter + snapshot':'实时接口 + 快照',
    'live entity annotation':'实时实体标注', 'curated cited links':'人工整理的引用链接', 'mapping unavailable in snapshot':'快照中暂无映射', 'next integration':'下一步接入',
    'Stable terms and synonyms. Human-native terms only; no automatic equivalence mapping.':'稳定的术语与同义词。仅使用人类原生术语；不做自动等价映射。',
    'Gene identity and indexed publications; abstracts are candidates, not confirmed graph claims.':'基因身份与已索引的文献；摘要只是候选信息，不是已确认的图谱结论。',
    'Paper metadata, abstracts, preprint labels; PubMed records share a source lineage.':'论文元数据、摘要和预印本标记；与 PubMed 记录同源。',
    'Paper-to-gene, disease and variant mentions with offsets. Automated mentions are candidates, not causal relations.':'论文中提及的基因、疾病和变异（含文本位置）。自动识别的提及只是候选，不代表因果关系。',
    'Study scope, status, eligibility, collaborators. Registry listing is not evidence of efficacy.':'研究范围、状态、入组条件和合作方。登记在册不代表有疗效证据。',
    'Mechanism summaries and existing registries. Full text is linked, not redistributed.':'机制综述与现有登记库。全文只提供链接，不做转载。',
    'No pathway membership was invented when mapping requests failed.':'映射请求失败时，不会凭空生成通路归属。',
    'No patient-specific variants or variant-effect claims imported in this demo.':'本演示未导入任何患者特定变异或变异效应结论。',
    'No author disambiguation, grants, or model availability asserted.':'不对作者消歧、资助信息或模型可用性作任何断言。',
    'Variant-specific effects and counterevidence require expert full-text review.':'变异的具体效应及反面证据需要专家审阅全文。',
    'No validated cross-disease treatment recommendation.':'不提供经验证的跨疾病治疗建议。',
    'Registry access and measure comparability have not been confirmed.':'登记库的访问权限和测量指标的可比性尚未确认。',
    'No patient records are collected.':'不收集任何患者记录。',
    'Reach a decision on reusing registry measures for a joint natural-history proposal.':'就是否在联合自然史研究提案中复用登记库测量指标作出决定。',
    'Illustrative planning hypothesis; not measured impact.':'示意性的规划假设，并非实测效果。',
    'Existing registry team responds within a week.':'现有登记库团队在一周内回复。',
    'Consent and data access permit comparison.':'知情同意和数据访问权限允许进行比较。',
    'A clinician and both patient groups review the proposal.':'一名临床医生和两个患者组织共同审阅提案。',
    'No new registry or ethics approval is needed for the initial feasibility decision.':'初步可行性决策无需新建登记库，也无需新的伦理审批。',
    'Measure actual time to a documented reuse decision against comparable prior efforts.':'对照以往可比的工作，测量实际作出有记录的复用决策所用的时间。',
    'Search & annotation candidates':'检索与标注候选',
    'RESEARCH MAP':'研究图谱',
    'Biological mechanisms, shared phenotypes, and research infrastructure.':'生物学机制、共有表型与研究基础设施。',
    'Shared phenotypes':'共有表型',
    'Synaptic vesicle release':'突触囊泡释放',
    'Research infrastructure':'研究基础设施',
    'Scientific literature':'科学文献',
    'Genetic variants':'遗传变异',
    'Path through hidden nodes':'经过隐藏节点的关联路径',
    'This line summarizes an existing path, not a direct relationship.':'这条线汇总了已有的关联路径，并不表示直接关系。',
    'About this community':'社群简介来源',
    'About this community — official website':'社群简介 — 官方网站',
    'A parent-led foundation supporting families affected by STXBP1-related disorders. It funds research and helps families understand the condition and get involved.':'由家长发起的基金会，为受 STXBP1 相关疾病影响的家庭提供支持，资助研究，并帮助家庭了解疾病和参与相关活动。',
    'Supports families affected by SLC6A1-related disorders and funds research into new treatments. Offers guidance after diagnosis and connections to specialists and research opportunities.':'支持受 SLC6A1 相关疾病影响的家庭，资助新疗法研究，提供确诊后的指导，并帮助家庭联系专科医生和了解研究参与机会。',
    'An international research program connecting families with rare genetic neurodevelopmental disorders and scientists. Collects medical histories, surveys and optional blood samples to support research.':'连接罕见遗传性神经发育障碍家庭与科学家的国际研究项目，通过收集病史、问卷和自愿提供的血液样本支持研究。',
    'Supports U.S. patients with Gaucher disease and their families through education, patient services and financial assistance. Helps families find specialists and connect with others.':'为美国戈谢病患者及家庭提供科普、患者服务和经济援助，帮助家庭寻找专科医生并与其他家庭建立联系。',
    'Provides education and support for people with Fabry disease and their families. Offers family events, assistance programs and a directory of Fabry specialists.':'为法布雷病患者及家庭提供科普与支持，包括家庭活动、援助项目和专科医生名录。',
    'Connects Fabry patient organizations around the world. Shares information and supports collaboration to improve the lives of people affected by Fabry disease.':'连接世界各地的法布雷病患者组织，通过信息分享与合作，帮助改善患者的生活。',
    'Offers education, advocacy and a supportive community for people affected by Fabry disease. Provides resources, programs and events for patients and families.':'为受法布雷病影响的人群提供科普、权益倡导和社群支持，为患者及家庭提供资源、项目和交流活动。',
    'RARE DISEASE ATLAS':'罕见病知识图谱', 'Sources & coverage ↗':'来源与覆盖范围 ↗',
    'Rare, but never alone.':'罕见，但从不孤单。',
    'Open the example map':'打开示例图谱', 'Scroll to zoom · Drag to pan · Select to inspect':'滚轮缩放 · 拖动平移 · 点击查看',
    'Patient organization leader':'患者组织负责人', 'Search the atlas':'搜索知识图谱',
    'FIND YOUR NEXT CONNECTION':'发现新的研究联系', 'Where could your research go next?':'下一步研究可以走向哪里？',
    'Search a disease, gene, or symptom':'搜索疾病、基因或症状', 'Search a disease, gene, or symptom…':'搜索疾病、基因或症状…',
    'Explore':'探索', 'Try':'试试', ', or': '，或', 'seizures':'癫痫发作', 'low muscle tone':'肌张力低下',
    'Loading the evidence map…':'正在加载证据图谱…', 'YOUR RESEARCH MAP':'你的研究图谱',
    'Research connections':'研究联系', 'Start with what is known. Explore what could be shared.':'从已有知识出发，探索可以共享的资源。',
    'Evidence confidence':'证据可信度', 'Moderate & high':'中等及高', 'High only':'仅高可信度', 'All confidence levels':'全部可信度',
    'Show research hypotheses':'显示研究假设', 'Confidence is a curator assessment of the evidence, not a probability of benefit.':'可信度是对证据的整理评估，并非获益概率。',
    'Documented relationship':'有记录的关系', 'Proposed connection':'提出的联系', 'Limitation / counterexample':'局限 / 反例',
    'Node size reflects connections in this map. Select a line to see why it exists.':'节点大小反映图中联系数量。选择连线查看依据。',
    'A focused first chapter':'首个示例图谱', 'Reviewed 4 October 2026':'核查日期：2026年10月4日',
    'Research network':'研究网络', 'Map view':'图谱视图', 'Network':'网络图', 'Related papers':'相关论文',
    'Reset graph view':'重置图谱视图', 'Fit map ⊞':'适配图谱 ⊞', 'CONNECTED BY EVIDENCE':'以证据连接',
    'Interactive evidence graph':'交互式证据图谱', 'Loading…':'正在加载…', 'Click a node or a connection':'点击节点或连线',
    'Follow the published evidence':'追踪已发表证据', 'Reading leads are separated from confirmed claims.':'阅读线索与已确认结论分别展示。',
    'Search public sources ↗':'搜索公开来源 ↗', 'From connections to a next step':'从研究联系走向下一步',
    'Filter evidence → check sources → review a research proposal':'筛选证据 → 核查来源 → 审核研究建议',
    'Review evidence':'审核证据', 'Review evidence →':'审核证据 →', 'Refresh papers & studies for the review':'审核前刷新论文与研究记录',
    'Agent review':'智能体审核', '(checking configuration)':'（正在检查配置）', '(not configured)':'（未配置）',
    'Details':'详情', 'Connection':'联系', 'Evidence':'证据', 'Next steps':'下一步',
    'One disease is a starting point. Evidence shows the way forward.':'一种疾病是起点，证据指引前进方向。',
    'Research navigation · expert review required for clinical decisions':'研究导航 · 临床决策需专家审核',
    'KNOW WHAT THIS MAP CAN TELL YOU':'了解图谱的能力与局限', 'Close sources and coverage':'关闭来源与覆盖范围',
    'Sources, scope & missing evidence':'来源、范围与缺失证据', 'Filtering the evidence…':'正在筛选证据…',
    'Live research graph':'实时研究图谱', 'FOLLOW THE SOURCE':'追踪来源', 'Evidence you can inspect':'可查阅的证据',
    'Open source':'打开来源', 'WHY THIS CONNECTION EXISTS':'这条联系的依据', 'Relationship':'关系', 'Evidence checks':'证据检查',
    'Inspect supporting sources →':'查阅支持来源 →', 'Explore either end':'探索两端节点', 'Stable identifier':'稳定标识符',
    'Visit source':'访问来源', 'Study evidence':'研究证据', 'View registry eligibility criteria':'查看登记的入选标准',
    'Connections in this map':'图谱中的联系', 'Existing assets':'已有资源', 'Explore connections':'探索联系',
    'Find a next research step →':'寻找下一步研究方向 →', 'A PLAN FOR MARIA':'Maria 的行动计划',
    'What can we do this week?':'本周可以做什么？', 'Review the filtered evidence to find reusable assets, partners, and questions that still need expert review.':'审核筛选后的证据，寻找可复用资源、合作伙伴和待专家确认的问题。',
    'A connection worth discussing':'值得讨论的联系', 'Agent critical review':'智能体批判性审核',
    'Download sourced proposal ↓':'下载附来源的研究建议 ↓', 'What still needs validation':'仍需验证的内容',
    'indexed reading lead':'已索引的阅读线索', 'Read publication':'阅读论文', 'View graph connection':'查看图谱联系',
    'Inspect paper':'查阅论文', 'Read retrieved abstract':'阅读检索到的摘要', 'Inspect study':'查阅研究',
    'Personal eligibility has not been assessed. Registration does not prove efficacy.':'尚未评估个人参与资格。研究登记不代表疗效已被证明。',
    'No records excluded.':'没有排除记录。', 'Searching public databases and assembling a live graph…':'正在搜索公开数据库并构建实时图谱…',
    'Live graph ready. Search relationships and automated mentions still need scientific review.':'实时图谱已生成。检索关系和自动识别的提及仍需科学审核。',
    'Identity is unresolved or ambiguous. This graph is search context, not a confirmed diagnosis. Choose a term to refine it:':'身份尚未明确或存在歧义。此图是检索上下文，并非确诊结果。请选择术语细化：',
    'No identity was resolved. The graph shows available search records; confirm the disease, gene, or symptom name before interpreting it.':'未明确识别实体。图谱显示可检索记录；解读前请确认疾病、基因或症状名称。',
    'Live graph unavailable; previous map remains visible.':'实时图谱暂不可用，仍显示上一张图谱。',
    'Searching trusted sources…':'正在搜索可信来源…', 'Reviewing…':'正在审核…', 'Filtering evidence…':'正在筛选证据…',
    'Retrieving bounded paper and study candidates…':'正在检索限定数量的论文与研究候选记录…',
    'Checking provenance and visible limitations…':'正在检查来源与已知局限…',
    'Agent is reviewing the filtered evidence…':'智能体正在审核筛选后的证据…',
    'Agent is challenging the draft and checking citations…':'智能体正在质疑草稿并检查引用…',
    'Review complete.':'审核完成。', 'Review queued…':'审核已排队…',
    'Review saved for the previous map. Run a review for the current search.':'审核结果已保存到上一张图谱，请对当前检索重新审核。',
    'Source checks and agent critical review complete. Human validation is still needed.':'来源检查与智能体审核已完成，仍需人工验证。',
    'Evidence checks complete. No model review was run.':'证据检查已完成，未运行模型审核。',
    'Agent review is available when selected.':'勾选后可使用智能体审核。', 'Evidence checks are available. Agent review is not configured.':'证据检查可用，智能体审核尚未配置。',
    'Known gaps':'已知缺口', 'The 10× planning hypothesis':'十倍提速的规划假设',
    'Diseases':'疾病', 'Genes':'基因', 'Phenotypes':'表型', 'Studies':'研究', 'Publications':'论文', 'Investigators':'研究人员', 'Variants':'变异', 'Search context':'检索上下文',
    'Vesicle release':'囊泡释放', 'GABA reuptake':'GABA 再摄取', 'Shared observations':'共同观察', 'Shared infrastructure':'共享基础设施', 'Published evidence':'已发表证据',
    'observed':'有记录', 'inferred':'推断', 'disputed':'有争议', 'hypothesis':'假设', 'documented':'有记录', 'conflicting':'相互冲突', 'unknown':'未知', 'unreviewed candidate':'待审核候选', 'preprint':'预印本',
    'disease':'疾病', 'gene':'基因', 'phenotype':'表型', 'paper':'论文', 'study':'研究', 'researcher':'研究人员', 'variant':'变异', 'search':'检索', 'institution':'机构', 'asset':'资源', 'mechanism':'机制', 'organization':'组织',
    'high confidence':'高可信度', 'moderate confidence':'中等可信度', 'low confidence':'低可信度'
  };
  Object.assign(zh, {'About confidence':'关于证据可信度', 'About node size':'关于节点大小', 'Node area is proportional to documented connections in this map. Select a line to see why it exists.':'节点面积代表此图中有记录的关联数量。选择连线可查看关联依据。'});
  const records = new WeakMap();
  Object.assign(zh, {
    'YOU DO NOT HAVE TO NAVIGATE THIS ALONE':'你不必独自面对',
    'Find support and people who understand.':'找到支持，也找到理解你的人。',
    'More options':'更多选项', 'More for researchers':'研究者可查看更多',
    'Graph & technical details':'图谱与专业细节',
    'Connection details & source evidence':'关联详情与来源证据',
    'Understand the papers and what comes next':'读懂论文，了解下一步',
    'Paper summaries, feasibility and risks — with sources':'论文总结、可行性与风险提醒，附来源引用',
    'Summarize papers & review feasibility':'总结论文并分析可行性',
    'PAPERS, FEASIBILITY & RISKS':'论文、可行性与风险',
    'What the evidence means for you':'这些证据对你意味着什么',
    'What the papers say & risks to consider':'论文结论与需要注意的风险',
    'Feasibility & next steps':'可行性与下一步'
  });
  Object.assign(zh, {
    'START WITH PEOPLE':'先找到同行的人',
    'Jump to the AI guide':'跳转到 AI 解读',
    'Find a community. Start a conversation.':'找到相关社群，开始交流。',
    'Existing support networks and research contacts connected to your search.':'与你的搜索相关的已有支持社群和研究联系人。',
    'Communities':'患者社群', 'Researchers & institutions':'研究人员与机构',
    'Indirect connections':'间接关联', 'Leads without direct contact':'暂无直接联系方式的线索',
    'Ranking criteria':'排序依据', 'Photos & logos':'图片与标识',
    'Communities to connect with':'可以联系的患者社群',
    'Researchers & institutions to reach out to':'可以进一步联系的研究人员与机构',
    'How results are ranked & coverage':'排序方法与覆盖范围',
    'Explore the evidence graph & research details':'查看证据图谱和研究细节',
    'Optional':'可选', 'Enlarge graph workspace':'放大图谱工作区', 'Restore workspace size':'恢复工作区大小',
    'Show papers, genes & mechanisms':'显示论文、基因和机制',
    'Website / source record':'网站／来源记录', 'Contact page / study contact':'联系页面／研究联系信息',
    'Sources & connection':'来源与关联', 'View in graph':'在图谱中查看',
    'OUTREACH RANK':'联系线索评分', 'Search connection':'搜索关联', 'Source support':'来源支持',
    'Contact route':'联系渠道', 'Profile details':'资料完整度'
  });
  Object.assign(zh, {
    'Symptoms in common':'共同症状',
    'How nerve cells send signals':'神经细胞如何发送信号',
    'How nerve cells clear signals':'神经细胞如何清除信号',
    'Patient registries & research resources':'患者登记与研究资源',
    'Published research':'已发表的研究', 'Symptoms & traits':'症状与特征',
    'Researchers':'研究人员', 'Genetic changes':'基因变异', 'Your search':'你的搜索',
    'Understand your condition & treatment research with AI ↓':'用 AI 了解疾病与治疗研究 ↓',
    'Understand your condition and possible treatments':'了解疾病与可能的治疗方向',
    'An AI guide for patients and families — explained simply, with sources':'面向患者及家属的 AI 指南：通俗解释，附原始来源',
    'Help me understand':'帮我读懂', 'Find out more':'查看更多', 'View details':'查看详情',
    'Photo unavailable':'暂无照片', 'Logo unavailable':'暂无机构标识',
    'Close researcher list':'关闭研究者列表',
    'Related through shared research or resources; may focus on a different condition.':'通过共同研究或资源找到，关注的疾病可能不同。',
    'The sources link this person or organization to your search.':'来源资料显示此人或机构与你的搜索有关。',
    'Use the listed contact details to ask about their work or support.':'可通过所列联系方式咨询研究或支持服务。',
    'Contact details are not listed. Visit the source or official website to find them.':'暂无联系方式，可前往来源页面或官方网站查找。',
    'Public organization profile / contact source':'机构公开资料 / 联系方式来源',
    'Review again to generate a report for the selected audience and language.':'请重新审阅，以生成适合所选身份和语言的报告。'
  });
  let language;
  try { language = localStorage.getItem('raraction-language'); } catch {}
  const browser = navigator.language;
  if (!['en','zh-CN','zh-Hant','de'].includes(language)) language = /^zh-(TW|HK|MO|Hant)/i.test(browser) ? 'zh-Hant' : browser.startsWith('zh') ? 'zh-CN' : browser.startsWith('de') ? 'de' : 'en';
  const select = document.createElement('select');
  select.id = 'language'; select.setAttribute('aria-label', 'Language / 语言 / 語言 / Sprache');
  select.innerHTML = '<option value="en">English</option><option value="zh-CN">简体中文</option><option value="zh-Hant">繁體中文</option><option value="de">Deutsch</option>';
  document.querySelector('.header-right').prepend(select);
  // Helpers for templated detail-panel text: look terms up in the dictionary, keep unknown ones verbatim.
  const lookup = value => locales[language].dict[value] || locales[language].dict[value.toLowerCase()];
  const term = value => lookup(value) || value;
  const trialStatus = {'recruiting':'招募中', 'not yet recruiting':'尚未开始招募', 'active not recruiting':'进行中（已停止招募）', 'completed':'已完成',
    'enrolling by invitation':'受邀入组', 'suspended':'已暂停', 'terminated':'已终止', 'withdrawn':'已撤回', 'unknown':'状态未知'};
  const studyStatus = value => locales[language].trialStatus[value.toLowerCase().replace(/_/g, ' ')] || value;
  // Simplified Chinese lives in this file; other languages (i18n-zh-hant.js, i18n-de.js) register {title, dict, trialStatus, rules} on window.asteriskLocales.
  const locales = {'zh-CN': {title: 'Asterisk · 罕见病知识图谱', dict: zh, trialStatus}, ...window.asteriskLocales};
  function translate(text) {
    const trimmed = text.trim();
    const locale = locales[language];
    let value = lookup(trimmed);
    if (!value) {
      const rules = locale.rules ? (locale.compiled ||= locale.rules(term, studyStatus)) : [
        [/^(\d+) nodes · (\d+) connections$/, '$1 个节点 · $2 条联系'],
        [/^(\d+) documented · (\d+) proposed$/, '$1 条有记录 · $2 条假设'],
        [/^\((.+) available\)$/, '（$1 已配置）'],
        [/^SELECTED (.+)$/, (_, kind) => '选中' + (zh[kind.toLowerCase()] || kind)],
        [/^Retrieved (\d{4}-\d{2}-\d{2})$/, '检索日期：$1'],
        [/^Reviewed (\d{4}-\d{2}-\d{2})$/, '审核日期：$1'],
        [/^(\d+) graph edges excluded by current filters\.$/, '当前筛选条件排除了 $1 条图谱联系。'],
        [/^Live graph for "(.+)" across public disease, phenotype, gene, literature and study databases\. Results are bounded; completeness and rarity classification are not guaranteed\.$/, '“$1”的实时图谱，覆盖公共疾病、表型、基因、文献和研究数据库。结果数量有上限；不保证完整性，也不保证罕见病分类准确。'],
        [/^Building live evidence map for (.+)…$/, '正在为 $1 构建实时证据图谱…'],
        [/^(\d+) documented connections?$/, '$1 条有记录的联系'],
        [/^Degree centrality: (\d+) \/ 100\. This measures map connectivity, not medical importance\.$/, '度中心性：$1 / 100。它衡量的是在图谱中的连接程度，不代表医学重要性。'],
        [/^(\d+) registry connections?$/, '$1 个登记项目联系'],
        [/^(\d+) cited sources? · (\d+) source lineages?$/, '$1 个引用来源 · $2 个来源谱系'],
        [/^Source date: (\S+) · Reviewed: (\S+)$/, '来源日期：$1 · 审核日期：$2'],
        [/^Reviewed: (\S+)$/, '审核日期：$1'],
        [/^Source lineage: (.+)$/, '来源谱系：$1'],
        [/^([A-Z][A-Z_ ]+)\. Last updated (\S+)\. Refresh the study record before discussing participation\.$/, (_, status, date) => studyStatus(status) + '。最后更新：' + date + '。讨论是否参与之前，请先刷新研究记录。'],
        [/^Registry listing establishes study scope, not efficacy or personal eligibility\. Snapshot status: (.+)\.$/, (_, status) => '登记记录只说明研究范围，不代表疗效或个人入组资格。快照状态：' + studyStatus(status) + '。'],
        [/^Search relevance, biological applicability, and personal eligibility require review\. Status: (.+)\.$/, (_, status) => '检索相关性、生物学适用性和个人入组资格都需要审核。状态：' + studyStatus(status) + '。'],
        [/^(.+) have been reported in affected individuals\.$/, (_, feature) => '受影响者中有' + term(feature) + '的报告。'],
        [/^Pathogenic (\S+) variants are associated with this disorder\.$/, '致病性 $1 变异与该疾病相关。'],
        [/^This indexed publication discusses (\S+)\. It is a reading lead; claims require full-text assessment\.$/, '这篇收录论文讨论了 $1。它只是阅读线索，其中的结论需要阅读全文评估。'],
        [/^The registered study includes (\S+) in its condition and arm descriptions\.$/, '这项登记研究在其疾病和分组描述中包含 $1。'],
        [/^This publication was returned for "(.+)"\. Read its abstract to assess relevance\.$/, '检索“$1”时返回了这篇论文。请阅读摘要判断相关性。'],
        [/^This study was returned for "(.+)"; listed conditions: (.*)\.$/, '检索“$1”时返回了这项研究；列出的疾病：$2。'],
        [/^PubTator annotated "(.+)" in this publication\.$/, 'PubTator 在这篇论文中标注了“$1”。'],
        [/^(.+) · (observed|inferred|disputed|collapsed)$/, (_, relation, status) => term(relation) + ' · ' + term(status)],
        [/^Exact directory term match: (.+)$/, '名录精确匹配：$1'],
        [/^Search query: (.+)$/, '检索词：$1'],
        [/^Public identity lookup · (.+)$/, '公共身份查询 · $1'],
        // Last: lines that join several known phrases with " · " (e.g. assessment flags) translate part by part.
        [/^Searching public databases for “(.+)”… This usually takes 10–30 seconds\.$/, '正在公共数据库中检索“$1”…通常需要 10–30 秒。'],
        [/^Search failed: (.+)$/, (_, reason) => '搜索失败：' + term(reason)],
        [/^The server returned an unexpected response \(HTTP (\d+)\)\.$/, '服务器返回了意外的响应（HTTP $1）。'],
        [/^(\d+) sourced leads?$/, '$1 条有来源的线索'],
        [/^Phone: (.+)$/, '电话：$1'],
        [/^(.+) ↗$/, (_, label) => term(label) + ' ↗'],
        [/^.+ · .+$/, line => line.split(' · ').map(term).join(' · ')]
      ];
      for (const [pattern, replacement] of rules) if (pattern.test(trimmed)) { value = trimmed.replace(pattern, replacement); break; }
    }
    return value ? text.replace(trimmed, value) : text;
  }
  function apply(root = document.body) {
    observer.disconnect();
    document.documentElement.lang = language;
    select.value = language;
    document.title = locales[language]?.title || 'Asterisk · Rare Disease Atlas';
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.parentElement.closest('script,style,#language,.locale-note,.glass-select,.chat-text')) continue;
      let record = records.get(node);
      if (!record || node.nodeValue !== record.rendered) record = {original: node.nodeValue};
      record.rendered = language !== 'en' ? translate(record.original) : record.original;
      node.nodeValue = record.rendered; records.set(node, record);
    }
    for (const element of document.querySelectorAll('[placeholder],[title],[aria-label]')) {
      if (element === select) continue;
      for (const attribute of ['placeholder','title','aria-label']) {
        if (!element.hasAttribute(attribute)) continue;
        const key = 'locale' + attribute.replaceAll('-', '');
        if (!(key in element.dataset)) element.dataset[key] = element.getAttribute(attribute);
        element.setAttribute(attribute, language !== 'en' ? translate(element.dataset[key]) : element.dataset[key]);
      }
    }
    observer.observe(document.body, {childList: true, subtree: true, characterData: true});
  }
  const observer = new MutationObserver(() => apply());
  select.addEventListener('change', () => {
    language = select.value;
    try { localStorage.setItem('raraction-language', language); } catch {}
    apply();
  });
  apply();
})();
