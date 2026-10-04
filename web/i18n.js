/* UI localization only: publication titles, abstracts and evidence stay verbatim. */
'use strict';
(() => {
  const zh = {
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
    'For patients, families and advocates like Maria: understand the condition, what research has found, and how far possible treatments have progressed. Explore what may be feasible, what is still uncertain, and questions to discuss with your care team — with links to the sources.':'帮助 Maria 这样的患者、家属及患者组织代表了解疾病、研究发现，以及潜在治疗目前进展到哪一步。解释哪些方向可能可行、哪些仍不确定，并整理可与医疗团队讨论的问题，附来源链接。',
    'Related through shared research or resources; may focus on a different condition.':'通过共同研究或资源找到，关注的疾病可能不同。',
    'The sources link this person or organization to your search.':'来源资料显示此人或机构与你的搜索有关。',
    'Use the listed contact details to ask about their work or support.':'可通过所列联系方式咨询研究或支持服务。',
    'Contact details are not listed. Visit the source or official website to find them.':'暂无联系方式，可前往来源页面或官方网站查找。'
  });
  let language;
  try { language = localStorage.getItem('raraction-language'); } catch {}
  if (!['en','zh-CN'].includes(language)) language = navigator.language.startsWith('zh') ? 'zh-CN' : 'en';
  const select = document.createElement('select');
  select.id = 'language'; select.setAttribute('aria-label', 'Language / 语言');
  select.innerHTML = '<option value="en">English</option><option value="zh-CN">简体中文</option>';
  document.querySelector('.header-right').prepend(select);
  function translate(text) {
    const trimmed = text.trim();
    let value = zh[trimmed] || zh[trimmed.toLowerCase()];
    if (!value) {
      const rules = [
        [/^(\d+) nodes · (\d+) connections$/, '$1 个节点 · $2 条联系'],
        [/^(\d+) documented · (\d+) proposed$/, '$1 条有记录 · $2 条假设'],
        [/^\((.+) available\)$/, '（$1 已配置）'],
        [/^SELECTED (.+)$/, (_, kind) => '选中' + (zh[kind.toLowerCase()] || kind)],
        [/^Retrieved (\d{4}-\d{2}-\d{2})$/, '检索日期：$1'],
        [/^Building live evidence map for (.+)…$/, '正在为 $1 构建实时证据图谱…']
      ];
      for (const [pattern, replacement] of rules) if (pattern.test(trimmed)) { value = trimmed.replace(pattern, replacement); break; }
    }
    return value ? text.replace(trimmed, value) : text;
  }
  function apply(root = document.body) {
    observer.disconnect();
    document.documentElement.lang = language;
    select.value = language;
    document.title = language === 'zh-CN' ? 'Raraction · 罕见病知识图谱' : 'Raraction · Rare Disease Atlas';
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.parentElement.closest('script,style,#language,.locale-note')) continue;
      let record = records.get(node);
      if (!record || node.nodeValue !== record.rendered) record = {original: node.nodeValue};
      record.rendered = language === 'zh-CN' ? translate(record.original) : record.original;
      node.nodeValue = record.rendered; records.set(node, record);
    }
    for (const element of document.querySelectorAll('[placeholder],[title],[aria-label]')) {
      if (element === select) continue;
      for (const attribute of ['placeholder','title','aria-label']) {
        if (!element.hasAttribute(attribute)) continue;
        const key = 'locale' + attribute.replaceAll('-', '');
        if (!(key in element.dataset)) element.dataset[key] = element.getAttribute(attribute);
        element.setAttribute(attribute, language === 'zh-CN' ? translate(element.dataset[key]) : element.dataset[key]);
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
