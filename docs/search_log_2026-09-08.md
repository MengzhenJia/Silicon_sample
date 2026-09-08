# 检索执行日志 — 2026-09-08

## 任务

系统搜集 arXiv 上 2023–2026 年与“硅基样本”和“使用大模型模拟人类”相关的研究，并将清单、边界与检索过程保存在本仓库。

检索截止：**2026-09-08**。

## Step 1：确认仓库与写权限

目标仓库：`MengzhenJia/Silicon_sample`

确认仓库存在、默认分支为 `main`，当前连接具有写权限。仓库开始执行本任务时为空，因此本次建立了 README、按年文献表、检索协议、执行日志、主题地图与更新脚本。

## Step 2：确定“所有文献”的操作性边界

发现仅以 `silicon sampling` / `silicon sample` 为关键词会漏掉大量同一研究问题下的文献。因此把目标概念展开为五组：

1. silicon / synthetic / virtual survey respondents；
2. human surrogate / human proxy / digital twin / persona simulation；
3. human behavior / cognition / preference simulation；
4. generative-agent / social / opinion-dynamics / population simulation；
5. user / consumer / customer / student / economic-agent simulation。

同时建立 `primary` 与 `extended` 两层范围，详见 `search_protocol.md`。

## Step 3：用领域综述建立第一批种子文献

首先使用：

- `2412.03563` — *From Individual to Society: A Survey on Social Simulation Driven by Large Language Model-based Agents*

该综述及其配套资源将相关工作区分为 individual simulation、scenario simulation、society simulation。由此确认不能只围绕 survey 或 silicon sampling 搜索。

随后检查其 FudanDISC/SocialAgent 配套文献表，重点提取：

- demographics / persona / human behavior；
- public opinion survey；
- general economic simulation；
- individual and organizational behavior；
- social platform / opinion dynamics；
- recommendation environments。

## Step 4：公共舆论与调查研究专项反查

交叉检查 `CaroHaensch/public_opinion_llms`，补充并核对了 survey/public-opinion 路线中的关键 arXiv 记录，包括：

- `2303.17548` Whose Opinions Do Language Models Reflect?
- `2303.16779` Language Models Trained on Media Diets Can Predict Public Opinion
- `2305.09620` AI-Augmented Surveys
- `2305.14929` Aligning Language Models to User Opinions
- `2306.07951` Questioning the Survey Responses of Large Language Models
- `2306.16388` Towards Measuring the Representation of Subjective Global Opinions in Language Models
- `2307.04781` Demonstrations of the Potential of AI-based Political Issue Polling
- `2310.17888` Large Language Models as Subpopulation Representative Models: A Review
- `2311.04076` Do LLMs Exhibit Human-like Response Biases?
- `2402.18144` Random Silicon Sampling

这一步主要防止遗漏那些标题中没有 `simulate human` 但实际上直接把 LLM 当作调查受访者/群体代表模型的文献。

## Step 5：2025–2026 新文献专项反查

检查持续维护至 2026-08 的 `Persdre/awesome-llm-human-simulation`，补入并核查下列快速增长的路线：

- synthetic survey respondents / human surrogates；
- digital twins；
- reliability / fidelity / robustness audits；
- population-scale social simulation；
- user/customer simulation；
- cognition and human memory simulation。

尤其对 2026 年逐项检查，因为当前年度尚未结束，不能依赖旧综述覆盖。

## Step 6：定向关键词补检

在上述种子清单之外，再以以下词族定向搜索 arXiv/网页索引中的 arXiv 页面：

### Survey / silicon

- `silicon sampling`
- `silicon sample`
- `synthetic respondent`
- `synthetic survey respondent`
- `virtual survey respondent`
- `LLM survey responses`
- `LLM public opinion`

### Human proxy / individual simulation

- `LLM human surrogate`
- `LLM human proxy`
- `LLM digital twin human`
- `LLM persona simulation`
- `LLM simulate human behavior`
- `LLM human cognition`

### Society / agents

- `LLM social simulation`
- `LLM opinion dynamics`
- `LLM social network simulation`
- `generative agents human behavior`
- `LLM population simulation`

### Applied boundary searches

- `LLM user simulator`
- `LLM consumer simulation`
- `LLM customer simulation`
- `LLM student simulation`
- `LLM simulated economic agents`

## Step 7：处理年份边界

统一按照 arXiv v1 首次提交年份。

因此以下高度相关的奠基文献虽然常在 2023 年及之后的综述中出现，但 **不计入 2023–2026 主表**：

- `2208.04024` Social Simulacra
- `2208.10264` Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies
- `2209.06899` Out of One, Many: Using Language Models to Simulate Human Samples
- `2209.07065` CommunityLM

它们单独保存于 `data/foundational_pre2023.csv`。

## Step 8：去重与筛选

以不含版本号的 canonical arXiv ID 作为唯一主键。对候选记录执行：

1. 去除 `v1/v2/...`；
2. 合并标题变体和正式发表版本重复；
3. 阅读标题与摘要判定研究对象；
4. 标注 `primary` / `extended`；
5. 排除纯 autonomous-agent、LLM-as-judge、一般 bias/alignment 和与人类模拟无关的 synthetic-data 论文。

## Step 9：当前结果

截至 2026-09-08，本轮整理得到：

| 年份 | Primary | Extended | 合计 |
|---|---:|---:|---:|
| 2023 | 30 | 10 | 40 |
| 2024 | 55 | 14 | 69 |
| 2025 | 47 | 11 | 58 |
| 2026 | 37 | 2 | 39 |
| **总计** | **169** | **37** | **206** |

主表文件：

- `data/arxiv_llm_human_simulation_2023.csv`
- `data/arxiv_llm_human_simulation_2024.csv`
- `data/arxiv_llm_human_simulation_2025.csv`
- `data/arxiv_llm_human_simulation_2026.csv`

## Step 10：质量控制

本轮采用以下交叉核验逻辑：

- 综述 → 配套文献表 → 专项 survey/public-opinion 文献表；
- 关键词检索 → 反查是否已在专题清单出现；
- 2026 新文献 → 单独按最新术语补检；
- arXiv ID → canonical 去重；
- 正式发表年份 → 不用于主年份归档。

另外，给仓库加入 `scripts/update_arxiv_search.py`，以后可以直接重新跑查询词族生成候选表，再与人工 curated 清单做差集。

## 已知边界

1. arXiv 是持续更新的开放库，2026 年之后仍会有新增记录；本轮截止于 2026-09-08。
2. 一些高度相关研究只出现在 SocArXiv、SSRN、期刊或会议网站，没有可确认的 arXiv 版本；因任务明确要求 arXiv，未计入主表。
3. “模拟人类”的概念边界可宽可窄，所以保留 `primary/extended` 两层，避免用一个主观阈值偷偷删掉边界论文。
4. 无法从有限关键词数学证明绝对零遗漏；本项目用多源交叉核验和可重复脚本把“尽量不漏”转化为可审计过程。

## 下一次更新建议

更新时先运行自动候选脚本，再重点查：

- `synthetic respondent / synthetic participant`
- `human surrogate / digital twin`
- `silicon sampling`
- `social simulation / opinion dynamics`
- 最近 90 天的 2026 新 arXiv 记录

对脚本新发现但不在 curated CSV 中的 ID 逐条人工筛选，再更新计数与日志。
