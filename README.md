# Silicon Sample / LLM Human Simulation Literature

本仓库系统整理 **2023-01-01 至 2026-09-08** 首次提交到 arXiv、且与“硅基样本 / 使用大语言模型模拟人类”直接相关的研究，并保存检索与筛选过程以便复核和持续更新。

## 当前版本

- 截止日期：**2026-09-08**
- 当前人工纳入：**206 条 arXiv 记录**
- `primary`（核心范围）：**169 条**
- `extended`（扩展边界）：**37 条**
- 年份分布：
  - 2023：40 条（30 primary + 10 extended）
  - 2024：69 条（55 primary + 14 extended）
  - 2025：58 条（47 primary + 11 extended）
  - 2026：39 条（37 primary + 2 extended，截至 2026-09-08）

> “所有文献”在这里按可复现的操作性定义处理：尽可能高召回地覆盖目标概念的不同命名，并通过综述、专题清单、arXiv 定向检索和引用链交叉核验。任何有限关键词集合都无法数学上证明绝对零遗漏，因此本仓库同时保存检索式、边界规则和更新脚本，使遗漏可以被发现并补入。

## 收录范围

### Primary

论文的主要贡献至少满足一项：

1. **硅基/合成受访者**：synthetic respondents、silicon sampling、virtual respondents、synthetic samples、LLM survey simulation、public-opinion simulation；
2. **个体模拟**：LLM 作为特定真人、人口群体、persona、human proxy、digital twin，模拟人的态度、选择、心理、认知或行为；
3. **社会模拟**：LLM agents 用于模拟社会互动、意见动力学、社会网络、组织、政治、经济、城市或其他人类群体过程；
4. **方法与有效性**：专门检验上述模拟的 fidelity、reliability、bias、heterogeneity、validation、inference、robustness，或系统综述该领域。

### Extended

与“模拟人”紧密相关，但研究目标更偏角色扮演、用户/消费者模拟、推荐系统、博弈或领域应用；保留用于防止因定义过窄漏检。论文综述若只关心社会科学中的硅基样本，可优先筛选 `scope=primary`。

### 排除

- 仅把 LLM 当一般自主 agent、工具调用器、程序员或 LLM-as-judge，且不以人类行为/社会过程为模拟对象；
- 仅讨论通用 bias/alignment，但没有评估 LLM 作为人的代理或模拟器；
- 非 arXiv 记录不计入主清单；重要但 v1 在 2023 年以前的奠基论文单独记录在边界文件中。

## 年份口径

以 **arXiv v1 首次提交年份**为准，而不是期刊/会议正式发表年份。例如 *Out of One, Many: Using Language Models to Simulate Human Samples* 虽在 2023 年正式发表，但 arXiv v1 为 `2209.06899`，因此不计入 2023–2026 主清单，而放入边界文献。

## 文件结构

```text
README.md
├─ data/
│  ├─ arxiv_llm_human_simulation_2023.csv
│  ├─ arxiv_llm_human_simulation_2024.csv
│  ├─ arxiv_llm_human_simulation_2025.csv
│  ├─ arxiv_llm_human_simulation_2026.csv
│  └─ foundational_pre2023.csv
├─ docs/
│  ├─ search_protocol.md
│  ├─ search_log_2026-09-08.md
│  └─ literature_map.md
└─ scripts/
   └─ update_arxiv_search.py
```

## 数据字段

- `arxiv_id`：去掉版本号后的 canonical arXiv ID
- `year`：由 v1 arXiv ID / 首次提交日期确定
- `title`：论文标题
- `category`：本项目的主题分类
- `scope`：`primary` 或 `extended`
- `arxiv_url`：arXiv abstract 页面

## 检索策略

不是只搜 `silicon sample`，而是同时覆盖：

- `silicon sampling`, `silicon sample`, `synthetic respondent`, `virtual survey respondent`
- `human surrogate`, `human proxy`, `digital twin`, `persona simulation`
- `simulate human behavior`, `human behavior simulation`, `human cognition`
- `survey response`, `public opinion`, `synthetic survey`
- `social simulation`, `generative agents`, `opinion dynamics`, `social network simulation`
- `user simulator`, `consumer simulation`, `student simulation`, `economic agents`

再以领域综述和持续维护的专题列表做引用链/漏检核验。详细过程见 [`docs/search_protocol.md`](docs/search_protocol.md) 和 [`docs/search_log_2026-09-08.md`](docs/search_log_2026-09-08.md)。

## 主要交叉核验入口

- arXiv: *From Individual to Society: A Survey on Social Simulation Driven by Large Language Model-based Agents* (`2412.03563`)
- FudanDISC/SocialAgent：该综述维护的 social-agent 文献表
- Persdre/awesome-llm-human-simulation：截至 2026-08 持续维护的人类模拟专题清单
- CaroHaensch/public_opinion_llms：LLM public-opinion / survey research 专题清单
- 2025–2026 arXiv 定向检索：silicon sampling、synthetic respondents、human surrogate、digital twin、human/social simulation 等

## 使用建议

若用于“硅基样本”博士论文综述，建议先筛：

```text
scope == primary
category in {
  survey_opinion,
  survey_validation,
  synthetic_participants,
  digital_twins,
  methods_validation,
  methods_review
}
```

若讨论“使用大模型模拟社会行动者”的完整谱系，再加入 `human_behavior`、`cognition`、`social_simulation`、`economic_behavior`、`political_simulation`、`user_simulation` 等类别。
