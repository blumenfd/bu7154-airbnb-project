---
title: "Airbnb Group Assessment：原始要求与老师视频说明｜Original Requirements and Lecturer Briefing"
course_code: BU7154
type: assignment-guide
updated: 2026-10-12
source:
  - "Airbnb Project brief/airbnb project brief.pdf, pages 1-3"
  - "../Submission Requirements.txt"
  - "../Rubric for Project Report.docx"
  - "../Team Agreement Template.docx"
  - "../Mandatory Files (attach with your report)/assignment cover sheet.docx"
  - "../Mandatory Files (attach with your report)/TCD MSc Submission template - AI declaration.doc"
  - "../../recordings/transcripts/Airbnb_Project_Brief.txt"
  - "../../recordings/transcripts/Airbnb_Project_Brief.json, approximately 12 minutes 20 seconds"
---

# Airbnb Group Assessment：原始要求与老师视频说明

本作业要求小组以 data analysts 的身份，为 Airbnb host-support team 分析房源成功预订的相关因素，并检验既有跨城市研究的发现是否适用于 Dublin。由于没有真实 booking 数据，使用房源收到的 **customer review count** 作为代理指标。小组需要自行定义具体研究目标，完成数据处理、变量构造、模型选择、结果解释和业务建议。

**EN.** Define your own project goals, aggregate guest reviews to listing level, investigate predictors of review counts as a proxy for successful bookings, relate the findings to prior research, and make evidence-based recommendations for a host-support or platform team.

本页根据原始 PDF、Group Assessment 提交说明、rubric、声明模板和老师视频转录重新整理。数据分析 notebook、小组会议计划及此前课程笔记不作为作业要求的依据。正文分别注明 **PDF 要求**、**视频补充** 和 **整理说明**；未解决的原文冲突保留在第 10 节。

## 1. Sources and transcript quality｜原始来源与转录质量

| 标记 | 原始材料 | 用途 |
|---|---|---|
| PDF | [Airbnb project brief](<./Airbnb Project brief/airbnb project brief.pdf>)，共 3 页 | 商业问题、数据、变量表、模型要求 |
| Submission | [Submission Requirements](<../Submission Requirements.txt>) | 三项交付物、字数、视频、命名、截止时间 |
| Rubric | [Rubric for Project Report](<../Rubric for Project Report.docx>) | 报告章节、评分权重、引用和附录要求 |
| Video | [English transcript](<../../recordings/transcripts/Airbnb_Project_Brief.txt>)；[timestamp JSON](<../../recordings/transcripts/Airbnb_Project_Brief.json>) | 老师对 PDF 的逐节讲解与建议 |
| Templates | [Team Agreement](<../Team Agreement Template.docx>)；[assignment cover sheet](<../Mandatory Files (attach with your report)/assignment cover sheet.docx>)；[AI declaration](<../Mandatory Files (attach with your report)/TCD MSc Submission template - AI declaration.doc>) | 协作约定、署名和 AI 使用说明 |

视频录制文件名对应 **19 August 2026**；JSON 记录长度约 **739.99 秒，即 12:20**。现有转录由本地 Cohere Transcribe / MLX 4-bit 生成，文字总体连贯，但有统计模型和专有名词错听。例如 “positive and negative binomial” 及 “Limited Power” 不能直接作为模型名称；本页用 PDF 第 3 页及视频较清楚的后文核对为 **Poisson / Negative Binomial**。论文题名、作者、年份和研究城市数以 PDF 的参考文献与书面叙述为准；时间段仅是近似定位。

## 2. Business question and research goals｜商业问题与研究目标

**PDF 第 1 页，§1-2；Video 0:00-2:32。**

> A host-support team at Airbnb wants to understand what are the significant predictors of successful bookings at a listing and whether the predictors identified by past research conducted across different cities, also hold in Dublin.

研究对象是 **一个 listing**，结果变量是该房源的评论数量。老师在视频 **4:07-5:45** 解释：并非所有住客都会留下评论，因此从 reviews 推断 bookings 是一个需要说明的假设。

Rubric 要求 **“Students must define their own project goals.”** 小组应把宽泛问题收敛为自己的研究目标，并解释研究如何帮助商业团队做决策。可以围绕哪些房源/房东特征与评论数量有关，以及这些关系是否与既有研究或第二城市一致来制定问题；原文没有规定必须采用某一句统一 research question。

**整理说明：** 结果变量不是实际入住人数、真实订单或 calendar 中不可用天数。报告需要交代 review count 的代理性质，避免把相关关系直接写成某个因素造成了更多预订。

## 3. Research background｜文献背景与比较对象

**PDF 第 1 页，§2；第 3 页 References；Video 1:32-5:45。**

PDF 用以下研究构建背景：

- **Biswas, Sengupta and Chatterjee (2020)**：研究 peer-to-peer home-sharing 平台评论数量的决定因素，使用 clustering 和 count regression。Brief 将其描述为覆盖 **10 个城市**。
- **Sengupta et al. (2021)**：研究成功 Airbnb bookings 的 predictors，使用 hurdle models。Brief 将其描述为覆盖 **22 个城市，包括 Dublin**。
- **Zhang, Yan and Zhang (2018)**：研究 guests' perceived trust towards Airbnb hosts，列在原始参考文献中。

这些是 **brief 对论文的概述**，不能替代阅读论文原文。Literature Review 应有聚焦、深度和批判性，并说明研究问题如何定位在文献中。老师在视频 **2:32-3:03** 说明 brief 的变量是 guideline，可以从文献中选择更多有意义的变量。

第二城市的文字存在冲突，见第 10 节。PDF 第 2 页的扩展段落建议从 Sengupta et al. 的 22-city sample 中选择城市，举例 **Amsterdam、Barcelona、Copenhagen**，比较该城市、Dublin 和论文中的跨城市结果表。视频 **9:34-10:35** 也把第二城市作为 stronger submission 的建议。

原始 brief 没有指定 Edinburgh；若使用它，应说明选城理由，并在论文原文中核对它是否属于推荐的研究样本，不能仅凭本页假定。

## 4. Data collection, aggregation and joining｜数据获取、汇总与连接

**PDF 第 1-2 页，§3；Video 5:45-10:35。**

### Source tables｜原文指定的表

从 [Inside Airbnb — Get the Data](https://insideairbnb.com/get-the-data/) 获取：

| 文件 | 原文中的观察单位与内容 |
|---|---|
| `listings.csv` | 每个 listing 一行，包含房东、价格、amenity 等属性 |
| `reviews.csv` | 每条 individual guest review 一行，字段包含 `listing_id`、`id`、`date`、`reviewer_id`、`reviewer_name`、`comments` |

**PDF 第 2 页明确要求**直接引用 [官方 Inside Airbnb Data Dictionary](https://docs.google.com/spreadsheets/d/1iWCNJcSutYqpULSQHlNyGInUvHg2BoUGoNRIGa6Szc4/edit?usp=sharing)，报告所用版本；不要仅凭列名猜测含义。视频 **6:52-7:54** 强调 schema 会随时间变化。

`calendar.csv` 没有被本次原始 Airbnb brief 或这段视频列为必需数据表。它可以服务于自行定义的扩展问题，但不能代替 listings/reviews 的核心分析。

### Processing order｜原文要求的处理顺序

1. 读取 listings 和 reviews，记录各自原始行数。
2. 按 `reviews.listing_id` **先汇总到每个房源一行**，构造评论数、平均评论长度等房源级指标。
3. 使用 `listings.id = reviews.listing_id` 连接。
4. 以本次 listings 的当前房源为参照；视频 **8:24-9:00** 要求忽略无法对应当前房源的历史评论。
5. 将汇总的 comment count 与 listings 中 `number_of_reviews` 交叉核对。
6. 保留并报告零评论房源，确认最终分析单位为一个 listing。

其中“保留零评论房源”是对老师“报告零评论比例”要求的实现说明：通常用 listings 为主表左连接，未匹配评论的房源计数为 0，不能让 inner join 把它们全部移除。

### Reporting dates, counts and version｜报告日期、数量和版本

PDF 第 2 页明确列出：

- **Download date**：下载日期。
- **Row count of each raw file**：每个原始文件的行数。
- **Row count after aggregation and joining**：汇总与连接后剩余的行数。
- 使用的数据字典版本。

下载日期与 snapshot label、`last_scraped` 是不同概念，报告时应区分。原文强调季度更新会改变数据和结果，应报告本次实际数据，不沿用旧年度样本数量。

### Approximate sample size｜大致样本范围

原文建议最终 **listing-level** 数据约 **5,000-50,000 行**，不是 review-level 行数。若选择更大的第二城市，PDF 第 2 页要求 subsample listings，使其留在这一范围内；视频同样强调每个城市的房源级样本规模。

这是原文给出的近似范围与计算可行性考虑，不能将“在此范围内”本身当成模型必然稳定的证据。

## 5. Variable definitions｜PDF 原始变量表

**PDF 第 2-3 页，§4。** 下表保留原文的字段与工程任务。视频允许根据文献扩展变量，但不能因此忽略书面变量表中已经明确列出的内容。

| 原始字段 / 来源 | PDF 中的定义与处理 |
|---|---|
| `host_is_superhost` / listings | Superhost status |
| `host_response_time` / listings | Host responsiveness |
| `host_total_listings_count` / listings | Total listings owned by the host |
| `accommodates` / listings | Accommodation capacity |
| `amenities` / listings | JSON 字段，**解析并计数，得到 amenities 数量** |
| `price` / listings | Nightly price |
| `review_scores_rating`、`review_scores_communication`、`review_scores_cleanliness` / listings | Guest review scores |
| `instant_bookable` / listings | Booking policy |
| `comments`，按 `listing_id` 聚合 / reviews | **Comment count**，与 `number_of_reviews` 核对；**average comment length**；**share of comments with positive sentiment** |
| `first_review`、`last_review` / listings | 构造第一条与最近一条评论之间的 **spread in days** |
| `number_of_reviews` / listings | Y：successful bookings 的代理计数 |

这份表特别要求注意三个工程任务：

1. **Amenities count**：先解析 JSON，再数列表中的设施条目。
2. **Review text features**：在 review level 处理 comments，再按房源汇总平均长度和正向情感比例。
3. **Review date spread**：计算首末评论日期之差，单位是天。

**整理说明：** 原文没有规定评论长度按 words 还是 characters，没有指定 sentiment 工具、语言处理、分类阈值，也没有规定零评论房源的平均文字长度/情感比例如何编码。实施时需要自行定义并报告，不能把这些选择写成老师规定。

`first_review` 与 `last_review` 的跨度是 **观察到的评论时间跨度**，不能自动解释为 listing age。它确实列在 PDF 的变量表中；若认为它或评分/评论文字与累计评论数存在时间关系或内生性问题，应讨论分析设计和局限，而不是声称老师禁止使用这些变量。

`host_total_listings_count` 是 PDF 写出的字段。若实际数据只能使用 `calculated_host_listings_count`，必须核对两个字段的定义和范围，并说明替代理由，不能静默当作同一个变量。对全空、缺失或不再提供的字段也应记录可用性与处理理由。

### Additional suggestions in the video｜视频补充的变量方向

**Video 2:32-4:40。**

老师还提及 description length、description 的 positive sentiment、host profile photo、host membership duration、exact location、neighbourhood、与周边或类似房源的 **price difference**、facilities、flexible/strict cancellation，以及 value-for-money 等。它们是文献和选题方向，是否能使用需根据实际字段与定义核对，不代表每个新下载批次都会提供。

Description sentiment 与 guest-comment sentiment 来自不同文本，不能混写；PDF 明确列出的正向情感比例针对 **comments**。

## 6. Modelling requirements｜模型与论证要求

**PDF 第 3 页，§5-6；Video 10:35-12:10。**

### Primary approach｜主要方法

以 `number_of_reviews` 为 count outcome，使用 **Poisson 或 Negative Binomial regression**。原文是“or”，没有要求每组必须同时提交两套模型；比较两者可以帮助论证，但属于实施选择。

PDF 明确要求报告：

- **Proportion of listings with zero reviews**。
- **Variance-to-mean ratio**。
- 用这些实际数据证据说明选择 Poisson 或 Negative Binomial 的理由。

PDF §6 特别强调：不要只背诵“计数就用某模型”的一般规则，应检查本次数据的 dispersion。

**整理说明：** 方差/均值比可以描述原始结果变量的离散程度，但不能独自证明包含 covariates 后的 Poisson 模型一定过度离散。后续拟合诊断应与这项书面要求一起完成。论文使用 hurdle models，并不等于本作业规定必须使用 hurdle model；视频也接受合适的其他 count regression。

### Acceptable alternative｜允许的替代方法

可对 `log(1 + number_of_reviews)` 拟合 linear regression。PDF 要求以 count variable 的 **skewness** 解释为什么做 log transformation，并明确写出这是相对于文献中的 Poisson / Negative Binomial 方法的 **simplification**。

### Rigour｜方法严谨性

原文重点包括 review aggregation、joining、amenities JSON parsing，以及根据实际 dispersion 选择模型。Rubric 还要求解释所用技术的优点、局限，以及它如何对应研究问题。只生成模型输出、缺少方法论证和结果解释，不足以满足评分要求。

## 7. Report structure and marking rubric｜报告结构与评分

**来源：Rubric 第 1-2 页。**

学生需要自行定义 project goals；最终报告按以下结构写作：

| 章节 / 评分维度 | 权重 | Rubric 的重点 |
|---|---:|---|
| Executive Summary | 5% | 概括目标、背景、方法、发现和 managerial implications / recommendations |
| Project Goals | 5% | 明确研究目标、简述 approach，以及对商业决策的贡献 |
| Literature Review | 10% | 文献要当前、聚焦且有深度，组织有逻辑、批判性阅读，并定位研究问题 |
| Methodology | 25% | 清楚描述数据、工具、技术；解释选择理由、优缺点，以及与研究问题的匹配 |
| Discussion of Findings | 25% | 展示回答问题所需的结果与适当可视化；理解指标并结合项目背景解释 |
| Recommendations | 25% | 提出 e-business / digital marketing / platform team 可应用的具体决策，且与结果直接关联 |
| Housekeeping | 5% | 逻辑连贯、排版、文字、引用与拼写 |

另外必须有 **References，HARVARD Style**，以及 **Appendices**。

附录中的 **GitHub repository link 是必需项**，其他补充图表等内容可选。Rubric 明确写：**代码不放在附录，代码通过 GitHub 提交，链接贴在附录。**

报告字数为 **4,000 words ±10%**，即约 **3,600-4,400 words**；不包括 title page、cover files、tables、figure captions、references 和 appendices。Sample Report 是 illustrative only，报告结构以 rubric 为准。

## 8. Submission requirements｜交付物与截止时间

**来源：Submission Requirements.txt。**

从 Amazon / Airbnb 两个 brief 中选一个题目。开始项目工作前需签署 Team Agreement。

| 交付物 | 原始提交说明 |
|---|---|
| Code / evidence of code execution | 使用 GitHub；可以使用任意标准软件运行模型 |
| Video presentation + slides | **Maximum 15 minutes**；配套 slides 支持完整展示。可用 Zoom、MS Teams 或标准录屏工具；提供链接，或上传 College OneDrive。Business casual attire 可接受 |
| Final report | 按 rubric 结构，4,000 words ±10%；代码放 GitHub，不放报告正文 |

提交说明允许将 coding、data cleaning 等证据作为附录；这类补充材料 **不要加进 PPT**。视频讲 methodology 时可口头说明处理步骤，不要求把具体证据逐项展示在屏幕上。

所有提交文件和资源应使用 **group number** 命名，包括 GitHub repository、slides、视频链接/文件、appendix 和 cover files。原例：`BU7154 Group 01 code` / `BU7154 Group 01 report`。

**Deadline：15 December 2026，9 PM Dublin Time。**

### Mandatory cover files and AI statement｜必交声明与封面

需提交两份 cover files：

1. Assignment cover sheet。
2. Generative AI declaration。

AI declaration 要选择：

- **Option A**：未使用 ChatGPT 或其他 generative AI。
- **Option B**：使用了 generative AI。

若选 B，Rubric 和声明模板要求说明在哪些章节/部分使用了 AI、如何帮助学习，以及如何遵循伦理规范；说明长度约 **300-600 words**，放在 appendix。所有人仍需提交 AI declaration；300-600 字使用说明仅对 Option B 要求。

Assignment cover sheet 包含 group number、学生姓名和 contribution。模板注明，小组成员贡献不均等时才需要注明个人贡献百分比。

Team Agreement 模板涉及 informal communication、meetings、decision making、sanctions 和签名，体现集体参与与责任。这里没有从模板推定小组已经签署。

## 9. Lecturer video guide｜视频按主题定位

以下时间来自现有 JSON segments，边界近似：

| 时间 | 主题 |
|---|---|
| 0:00-2:32 | BU7154 选题介绍、host-support 场景、Dublin 与既有跨城研究 |
| 2:32-4:40 | 从文献选择变量；房东、描述、价格、容量、政策及 guest evaluations |
| 4:40-5:45 | 评论数作为 booking proxy 的假设；第二篇论文 |
| 5:45-7:54 | Inside Airbnb 数据、listings/reviews 粒度、data dictionary 与版本 |
| 7:54-9:34 | 先聚合 reviews 再连接；排除无当前房源对应的评论；样本规模 |
| 9:34-10:35 | 第二城市比较、优先考虑论文涉及的城市、变量表 |
| 10:35-11:37 | Poisson / Negative Binomial、计数结果与零评论比例 |
| 11:37-12:20 | log(1 + reviews) 线性回归替代方案、清洗与连接的严谨性 |

视频主要讲分析任务，没有完整讲解交付物、评分 rubric、字数和截止时间；这些信息来自独立的 Group Assessment 材料。

## 10. Ambiguities and interpretation boundaries｜原文冲突与解释边界

| 事项 | 原始证据 | 本页如何处理 |
|---|---|---|
| 第二城市是否必需 | PDF 第 1 页写 “For Dublin and another city”；第 2 页却把第二城市称作 stronger submission 的扩展；视频 9:34-10:35 也采用扩展措辞 | 书面要求存在内部冲突，不能一概写成必需或完全可选。若只做 Dublin 需向老师确认；做两城则兼顾两处表述 |
| 第二城市是否必须来自论文样本 | PDF 扩展段落建议从 Sengupta et al. 的 22-city sample 中选择；视频说这样更便于比较 | 按原文记录该建议。PDF 没有指定 Edinburgh，也没有在这里核实它是否属于论文样本 |
| 是否必须使用每个变量 | PDF 有明确变量表；视频 2:32-3:03 又说明 guideline 且允许扩展 | 完整记录表中工程任务；对不可用字段或不采用的变量给出理由。不把所有字段强制塞进一个模型，也不忽略表中任务 |
| 评分、评论文字和首末评论跨度 | PDF §4 明确包含这些变量 | 不能把此前分析中的谨慎建议写成老师禁用规则。它们与结果变量的关系、零评论缺失及解释限制应在 methodology 中说明 |
| 模型是否必须 Poisson 和 NB 都跑 | PDF 和视频清楚的模型说明是 Poisson **or** Negative Binomial，且允许 log-linear 替代 | 不把两套模型或 hurdle model 写成统一硬性提交要求 |
| 视频时长 | Submission 明确 maximum 15 minutes；原始 PDF 和此视频转录没有写 10 分钟提交上限 | 本页按原始 Submission 写 15 分钟；如 Blackboard 有更晚通知，再核对更新。现有材料未提供可验证的更新顺序 |
| “live data” 与季度批次 | 老师说 pull live data，但同时要求使用 Inside Airbnb 的季度数据并报告下载日期与行数 | 使用本次实际下载批次，记录来源和版本；不把公开季度快照误解为必须自行实时抓取 Airbnb |

## 11. Assignment checklist｜按原始要求自查

下面是交付前检查清单，不表示这些工作已经完成。

- [ ] 自行定义 project goals，并说明对 host-support / platform 决策的价值。
- [ ] 阅读相关论文，将研究问题、变量和方法放进文献背景。
- [ ] 记录数据来源、download date、raw row counts、post-aggregation/join row counts 和 dictionary version。
- [ ] 先聚合 reviews，再连接 listings；核对 comment count 和 `number_of_reviews`，报告零评论比例。
- [ ] 处理 PDF 的 amenities count、平均评论长度、正向评论比例与首末评论跨度等任务；记录变量不可用或调整理由。
- [ ] 报告 variance-to-mean ratio，并基于本次数据论证 count model；若用 log-linear，解释偏度和简化性质。
- [ ] 将模型指标、可视化和结果解释与研究目标联系起来。
- [ ] 如做第二城市，比较其结果、Dublin 和文献发现，并记录比较范围与数据差异。
- [ ] 提出与结果直接相连、业务团队能应用的 recommendations。
- [ ] 完成 rubric 指定章节、Harvard references、GitHub link 附录和适用的 AI-use statement。
- [ ] 提交 report、slides/video、GitHub code/evidence、两份 cover files；按 group number 命名，核对 deadline。

## References｜原始 brief 的参考文献

以下条目按 PDF 第 3 页整理：

Biswas, B., Sengupta, P. and Chatterjee, D. (2020) ‘Examining the determinants of the count of customer reviews in peer-to-peer home-sharing platforms using clustering and count regression techniques’, *Decision Support Systems*, 135, 113324. [Provided paper](<./Airbnb Project brief/1-s2.0-S0167923620300798-main.pdf>).

Sengupta, P., Biswas, B., Kumar, A., Shankar, R. and Gupta, S. (2021) ‘Examining the predictors of successful Airbnb bookings with Hurdle models: Evidence from Europe, Australia, USA and Asia-Pacific cities’, *Journal of Business Research*, 137, pp. 538-554. [Provided paper](<./Airbnb Project brief/1-s2.0-S0148296321005968-main.pdf>).

Zhang, L., Yan, Q. and Zhang, L. (2018) ‘A computational framework for understanding antecedents of guests' perceived trust towards hosts on Airbnb’, *Decision Support Systems*, 115, pp. 105-116.
