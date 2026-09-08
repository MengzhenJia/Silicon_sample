# 文献地图：从硅基样本到 LLM 人类与社会模拟

本文件不是新的纳入清单，而是对 `data/` 中 curated arXiv 记录的研究路线整理。需要精确文献全集时，以四个年份 CSV 为准。

## 1. 硅基样本、调查受访者与公共舆论

这是与社会科学“硅基样本”最直接相关的路线。核心问题从“LLM 能否生成像人的回答”逐渐转向“能否保持真实人群的分布、组内异质性和条件差异”。

### 2023：群体意见和调查响应成为可检验对象

代表文献：

- `2303.17548` — *Whose Opinions Do Language Models Reflect?*
- `2303.16779` — *Language Models Trained on Media Diets Can Predict Public Opinion*
- `2305.09620` — *AI-Augmented Surveys*
- `2306.07951` — *Questioning the Survey Responses of Large Language Models*
- `2306.16388` — *Towards Measuring the Representation of Subjective Global Opinions in Language Models*
- `2307.04781` — *Demonstrations of the Potential of AI-based Political Issue Polling*
- `2310.17888` — *Large Language Models as Subpopulation Representative Models: A Review*
- `2311.04076` — *Do LLMs Exhibit Human-like Response Biases?*

边界外但方法史上极重要：`2209.06899` *Out of One, Many*。它正式发表于 2023 年，但 arXiv v1 属于 2022 年，因此单列于 `foundational_pre2023.csv`。

### 2024：从 persona prompting 转向随机硅基抽样与分布有效性

代表文献：

- `2402.18144` — *Random Silicon Sampling*
- `2405.06058` — *Large Language Models Show Human-like Social Desirability Biases in Survey Responses*
- `2406.09464` — *GPT-ology, Computational Models, Silicon Sampling*
- `2407.11409` — *Representation Bias in Political Sample Simulations with Large Language Models*
- `2411.05403` — *Benchmarking Distributional Alignment of Large Language Models for Survey Research*
- `2412.03162` — *LLM-Mirror: A Generated-Persona Approach for Survey Pre-Testing*

### 2025：研究重点明显转向可靠性、代表性和不确定性

代表文献：

- `2501.06834` — *Large Language Models Model Non-WEIRD Populations with Some Success*
- `2501.08579` — *LLM-based Human Simulations Have Not Yet Been Reliable*
- `2502.17773` — *How Many Human Survey Respondents is a Large Language Model Worth?*
- `2504.08954` — *Should You Use LLMs to Simulate Opinions? Quality Checks for Synthetic Survey Research*
- `2505.21997` — *Leveraging Interview-Informed LLMs to Model Survey Responses*
- `2507.02919` — *ChatGPT is not A Man but Das Man*
- `2509.06337` — *Large Language Models as Virtual Survey Respondents*
- `2512.22725` — *Mitigating Social Desirability Bias in Random Silicon Sampling*

### 2026：从“能否替代”进一步转向条件有效性和跨调查迁移

代表文献：

- `2602.06302` — *Do LLMs Track Public Opinion?*
- `2602.13862` — *Measuring Self-Rating Bias in LLM-Generated Survey Data*
- `2602.18462` — *Assessing the Reliability of Persona-Conditioned LLMs as Synthetic Survey Respondents*
- `2606.04592` — *Synthetic Personalities*
- `2606.30085` — *Not-quite-human tastes: the stylized omnivorousness of LLM survey surrogates*
- `2607.03091` — *Silicon Sampling via Cross-Survey Transfer*
- `2607.26348` — *When Synthetic Users Fail*
- `2608.14079` — *The Conditional Superiority of Fast Silicon Sampling*

## 2. 从人口属性到个体 persona 与数字孪生

第二条路线关心：模型模拟的到底是“某类人”，还是可以逼近“这个具体的人”。这一路线与个体化硅基样本、生命经历/RAG、digital twin 最直接相关。

关键节点：

- `2306.03917` — *Turning Large Language Models into Cognitive Models*
- `2406.17232` — *Beyond Demographics: Aligning Role-playing LLM-based Agents Using Human Belief Networks*
- `2410.20268` — *Centaur: a Foundation Model of Human Cognition*
- `2411.10109` — *Generative Agent Simulations of 1,000 People*
- `2502.12109` — *Generative Personality Simulation via Theory-Informed Structured Interview*
- `2502.14642` — *How Far are LLMs from Being Our Digital Twins?*
- `2509.19088` — *Digital Twins as Funhouse Mirrors: Five Key Distortions*
- `2601.06111` — *LLM-Powered Social Digital Twins*
- `2608.20344` — *Beyond Raw Transcripts: Structured Persona Extraction for LLM-Based Digital Twins*

对“硅基样本”研究而言，这条路线提供了一个重要区分：**群体条件化的代表性**与**个体层面的可识别性/可预测性**不是同一个标准。

## 3. 生成式行动者与社会模拟

第三条路线把 LLM 从单个受访者扩展为可以互动的社会行动者，以观察宏观社会现象是否从微观语言行动中涌现。

### 2023：生成式行动者框架形成

- `2304.03442` — *Generative Agents: Interactive Simulacra of Human Behavior*
- `2307.14984` — *S3: Social-network Simulation System with Large Language Model-Empowered Agents*
- `2308.03313` — *Quantifying the Impact of Large Language Models on Collective Opinion Dynamics*
- `2309.11456` — *Generative Agent-Based Modeling*
- `2310.10436` — *EconAgent*
- `2311.09618` — *Simulating Opinion Dynamics with Networks of LLM-based Agents*
- `2312.03664` — *Concordia: A Library for Generative Social Simulation*

### 2024：规模化与领域化

- `2403.08251` — *Emergence of Social Norms in Generative Agent Societies*
- `2407.11190` — *In Silico Sociology*
- `2408.00818` — *Y Social: an LLM-powered Social Media Digital Twin*
- `2409.19338` — *Decoding Echo Chambers*
- `2410.04360` — *GenSim*
- `2410.20746` — *ElectionSim*
- `2411.11581` — *OASIS: Open Agent Social Interaction Simulations with One Million Agents*
- `2412.03563` — *From Individual to Society: A Survey on Social Simulation Driven by Large Language Model-based Agents*

### 2025–2026：超大规模社会系统与真实性审计

- `2502.08691` — *AgentSociety*
- `2504.10157` — *SocioVerse*
- `2506.21805` — *CitySim*
- `2603.00113` — *AI Agents Alone Are Not (Yet) Sufficient for Social Simulation*
- `2604.18011` — *Topology-Aware LLM-Driven Social Simulation*
- `2605.00197` — *The Silicon Society Cookbook*
- `2605.18890` — *Stop Drawing Scientific Claims from LLM Social Simulations Without Robustness Audits*
- `2605.27419` — *APS: Bias-Controlled Adaptive Prototype Simulation for Population-Scale LLM Agents*
- `2607.02464` — *Will Scaling Improve Social Simulation with LLMs?*
- `2608.16897` — *CityReal*

## 4. 有效性、偏差与因果/统计推断

这是整个领域中必须和“性能提升”区分开的路线。它追问：即使聚合结果相似，能否据此把模型当成人？

主要问题包括：

- **分布压缩/异质性不足**：模型能否复现同一人口群体内部的差异；
- **身份扁平化**：人口属性提示是否把复杂身份压成刻板类别；
- **社会赞许偏差**：模型调查响应是否出现系统性的 desirability 偏移；
- **模型依赖性**：结论是否依赖 prompt、temperature、model family、版本；
- **个体真实性**：聚合拟合是否掩盖个体层面的错误；
- **因果有效性**：模拟的 treatment effect 能否外推到真人；
- **统计推断**：把 synthetic respondents 当独立样本是否造成虚假精度。

代表文献：

- `2312.15524` — *The Challenge of Using LLMs to Simulate Human Behavior: A Causal Inference Perspective*
- `2402.01908` — *Large Language Models Should Not Replace Human Participants Because They Can Misportray and Flatten Identity Groups*
- `2403.05020` — *The Misleading Success of Simulating Social Interactions With LLMs*
- `2405.07248` — *Limited Ability of LLMs to Simulate Human Psychological Behaviours*
- `2412.05093` — *Sense and Sensitivity*
- `2509.13397` — *The Threat of Analytic Flexibility in LLM-Based Synthetic Data*
- `2510.21180` — *Social Simulations with Large Language Models Risk Utopian Illusion*
- `2602.15785` — *This Human Study Did Not Involve Human Subjects*
- `2604.15329` — *Evaluating LLMs as Human Surrogates in Controlled Experiments*
- `2605.18890` — *Stop Drawing Scientific Claims from LLM Social Simulations Without Robustness Audits*
- `2606.13629` — *Valid Inference with Synthetic Data via Task Exchangeability*

## 5. 用户、消费者和领域行为模拟

这部分在狭义“社会科学硅基样本”综述里可以作为 extended 或应用分支，但方法上非常重要，因为它们往往拥有真实行为日志作为 ground truth。

主要方向：

- recommender user simulation；
- conversational user simulation；
- customer / shopping behavior；
- education / virtual students；
- healthcare / counseling agents；
- market and economic behavior。

这类文献对验证“模型是否能模拟人的连续行为链”尤其有价值，因为其评价标准通常不是单题问卷相似，而是多轮行动、序列选择和长期状态变化。

## 6. 对硅基样本研究最关键的四个方法问题

从整个文献库看，后续研究可以围绕四个互相区分的标准组织：

1. **Marginal fidelity**：总体分布是否像真人；
2. **Conditional fidelity**：不同人口群体/情境的条件分布是否像真人；
3. **Individual fidelity**：同一个人的答案、行为或跨题结构能否被复现；
4. **Process fidelity**：模型内部或跨时互动产生结果的过程是否与要解释的人类机制具有足够对应关系。

把这四层分开，可以避免用总体均值/相关性很好就推断“模型已经模拟了人”。

## 7. 与本仓库筛选字段的对应

若只研究“硅基样本作为社会科学调查替代/补充方法”，优先使用：

- `survey_opinion`
- `survey_validation`
- `synthetic_participants`
- `digital_twins`
- `methods_validation`
- `methods_review`

若研究更广义“LLM 模拟社会行动者”，再加入：

- `human_behavior`
- `cognition`
- `social_simulation`
- `political_simulation`
- `economic_behavior`
- `economic_simulation`
- `user_simulation`
- `consumer_simulation`
