# arXiv 系统检索方案：硅基样本与 LLM 人类模拟（2023–2026）

## 1. 研究目标

建立一个可审计、可更新的高召回文献库，覆盖 2023-01-01 至 2026-09-08 首次提交到 arXiv、以大语言模型模拟人类个体、群体、受访者或社会过程为核心对象的研究。

本项目不把“silicon sampling”当成唯一关键词。相关研究使用 synthetic respondents、human surrogate、digital twin、persona simulation、generative agents、user simulation、social simulation 等不同术语，只使用单一关键词会产生系统性漏检。

## 2. 时间口径

年份统一按照 arXiv **v1 首次提交日期**，不按照会议/期刊发表年份。这样可以避免同一预印本在正式发表后被跨年重复计算。

主时间窗：

- start: 2023-01-01
- end: 2026-09-08

重要但 v1 早于 2023 年的奠基论文记录在 `data/foundational_pre2023.csv`，不进入主清单计数。

## 3. 纳入规则

### 3.1 Primary：核心范围

至少满足以下一条：

1. **硅基/合成受访者**：LLM 被用作 survey respondent、synthetic respondent、virtual respondent、silicon sample、public-opinion proxy；
2. **个体人类模拟**：LLM 模拟真人、特定 persona、人口群体、人的认知、心理、偏好、决策、行为或日常活动；
3. **数字孪生/代理人**：LLM 被构造成 human surrogate、digital twin、digital representative 或行为代理；
4. **社会模拟**：LLM agents 用于模拟意见动力学、社会网络、组织行为、政治行为、经济活动、城市行为、群体互动或其他社会过程；
5. **有效性与方法研究**：研究专门检验以上模拟的 fidelity、reliability、bias、heterogeneity、validation、causal inference、robustness、statistical inference，或系统综述该领域。

### 3.2 Extended：扩展边界

与模拟人高度相关，但主要目标偏向：

- fictional/established role-playing；
- recommender-system user simulator；
- consumer/shopping simulation；
- game/negotiation agent；
- education、healthcare 等领域中的模拟角色。

保留这些记录用于保证召回率，但在以“硅基样本作为社会科学方法”为主题的综述中可以筛除。

## 4. 排除规则

排除以下研究：

- 一般 autonomous agent、tool use、software engineering agent，但不模拟人或社会过程；
- 纯 LLM-as-judge / evaluator；
- 一般 bias、alignment、value 研究，但没有把 LLM 当人类代理或没有直接检验模拟真实性；
- 纯 synthetic text/data generation，且生成对象不是人类受访者、行为或社会过程；
- 非 arXiv 资料（可以在检索日志中作为交叉核验来源，但不计入主清单）。

## 5. 查询词族

### A. Silicon / survey sampling

- `"silicon sampling"`
- `"silicon sample"`
- `"synthetic respondent"`
- `"synthetic survey respondent"`
- `"virtual survey respondent"`
- `"survey response" AND ("large language model" OR LLM)`
- `"public opinion" AND ("large language model" OR LLM)`
- `"synthetic participants" AND ("large language model" OR LLM)`

### B. Human proxy / digital twin / persona

- `"human surrogate" AND ("large language model" OR LLM)`
- `"human proxy" AND ("large language model" OR LLM)`
- `"digital twin" AND ("large language model" OR LLM)`
- `"digital representative" AND ("large language model" OR LLM)`
- `"persona simulation" AND ("large language model" OR LLM)`
- `"persona-conditioned" AND (survey OR behavior)`

### C. Human behavior / cognition

- `"simulate human behavior"`
- `"human behavior simulation" AND (LLM OR "large language model")`
- `"human cognition" AND (LLM OR "large language model")`
- `"cognitive model" AND "large language model"`
- `"human preferences" AND "large language model"`
- `"human-like" AND simulation AND (LLM OR "large language model")`

### D. Social simulation

- `"social simulation" AND (LLM OR "large language model")`
- `"generative agents" AND (human OR social)`
- `"opinion dynamics" AND (LLM OR "large language model")`
- `"social network simulation" AND (LLM OR "large language model")`
- `"public opinion simulation" AND (LLM OR "large language model")`
- `"agent-based" AND simulation AND "large language model"`

### E. Application terms used to catch boundary papers

- `"user simulator" AND (LLM OR "large language model")`
- `"user simulation" AND (LLM OR "large language model")`
- `"consumer simulation" AND (LLM OR "large language model")`
- `"customer simulation" AND (LLM OR "large language model")`
- `"student simulation" AND (LLM OR "large language model")`
- `"economic agents" AND "large language model"`

## 6. 多源交叉核验

关键词检索之外，使用下列“种子地图”反查漏检：

1. *From Individual to Society: A Survey on Social Simulation Driven by Large Language Model-based Agents* (`2412.03563`) 及其 FudanDISC/SocialAgent 配套列表；
2. Persdre/awesome-llm-human-simulation（持续维护的人类模拟专题清单）；
3. CaroHaensch/public_opinion_llms（public opinion / survey 专题清单）；
4. 新近方法论文和综述的参考文献与 related-work 线索；
5. 对 2025–2026 年新术语（digital twins、human surrogate、synthetic users、human simulation validation）单独补检。

## 7. 去重与年份规范化

- 将 `arxiv_id` 规范为不带 `v1/v2/...` 的 canonical ID；
- canonical ID 相同只保留一条；
- 用 arXiv `published`（v1）确定首次年份；
- 标题大小写或后续版本更名不产生新的文献记录；
- 正式发表版本与 arXiv 版本对应时，主键仍为 canonical arXiv ID。

## 8. 人工筛选顺序

每条候选按照以下顺序判断：

1. 标题是否直接指向 human/survey/user/social simulation；
2. 摘要中的研究对象是否为人的态度、行为、认知、选择或社会过程；
3. LLM 是否真正承担“被模拟的人/行动者”角色，而不只是研究工具；
4. 若主要贡献是模拟真实性、偏差或推断有效性，仍归入 primary；
5. 若更接近角色扮演/工程用户模拟，归入 extended；
6. 无法满足以上条件则排除。

## 9. 完整性的含义

这里的“尽量不遗漏”实现为：**高召回查询词族 + 多个专题清单交叉核验 + canonical ID 去重 + 明确边界 + 可重复更新脚本**。

任何开放、持续增长的 arXiv 主题都无法用有限关键词数学证明“绝对零遗漏”。因此，本仓库不把一次性清单包装成封闭全集；相反，保存搜索式、日期、筛选规则和自动候选生成脚本，使新增或遗漏条目可以被审计并补入。

## 10. 更新工作流

```bash
python scripts/update_arxiv_search.py \
  --start 2023-01-01 \
  --end 2026-09-08 \
  --output data/generated_candidates.csv
```

随后：

1. 将 `generated_candidates.csv` 与四个 curated 年份 CSV 按 `arxiv_id` 比较；
2. 对新增候选阅读标题/摘要；
3. 标注 `primary` / `extended` / excluded；
4. 写入对应年份文件；
5. 更新 `docs/search_log_YYYY-MM-DD.md` 和 README 计数。
