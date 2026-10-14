---
title: "Airbnb 小组项目简介（简体中文）"
course_code: BU7154
type: assignment-guide-translation
source: "airbnb project brief.pdf"
---

# Airbnb 小组项目简介

本文是英文项目简介的简化中文版本，保留原任务的核心要求、数据字段、建模方法和参考文献。字段名、模型名和数据源链接保留英文，方便在代码和报告中使用。

## 1. 商业问题

Airbnb 的房东支持团队希望了解：

1. 哪些因素能够显著预测一个房源是否取得较好的预订表现？
2. 过去在多个城市研究中发现的预测因素，是否同样适用于 Dublin？

Airbnb 不公开真实的预订数据，因此本项目使用房源收到的**住客评论数量**作为成功预订数量的代理指标。评论数量并不等于实际订单数，报告需要说明这一限制。

## 2. 数据要求

从 [Inside Airbnb – Get the Data](https://insideairbnb.com/get-the-data/) 下载 **Dublin** 和另一个城市的数据。原始项目简介要求使用以下两个文件：

| 文件 | 内容 |
|---|---|
| `listings.csv` | 每行代表一个房源，包含房东、价格和设施等属性 |
| `reviews.csv` | 每行代表一条住客评论，包含 `listing_id`、`id`、`date`、`reviewer_id`、`reviewer_name` 和 `comments` |

字段含义和数据类型必须直接参考并引用官方 [Inside Airbnb Data Dictionary](https://docs.google.com/spreadsheets/d/1iWCNJcSutYqpULSQHlNyGInUvHg2BoUGoNRIGa6Szc4/edit?usp=sharing)。数据字典会随年份变化，报告应注明所使用的版本。

### 数据处理顺序

1. 记录两个原始文件的下载日期和行数。
2. 在评论层面处理 `reviews.csv`，按 `listing_id` 汇总为每个房源一行。
3. 至少构造评论数量、平均评论长度等房源级指标。
4. 使用 `listings.csv.id = reviews.csv.listing_id` 连接两个表。
5. 报告聚合和连接后的行数，并确认最终分析单位是 listing。
6. 将最终房源级数据控制在约 **5,000–50,000 行**。如果第二个城市的数据量较大，可以抽样其房源。

评论文件必须先聚合再连接，不能直接把评论级数据与房源表连接后当作分析数据。季度更新会改变数据行数和分析结果，因此不能直接套用往年样本数量。

### 可选的第二城市比较

更完整的项目可以选择 Sengupta et al. (2021) 研究过的第二个城市，例如 Amsterdam、Barcelona 或 Copenhagen，并比较：

- Dublin 与第二城市的结果；
- 两个城市与已发表的跨城市研究结果。

## 3. 变量定义

| 字段及来源 | 含义或处理方式 |
|---|---|
| `host_is_superhost`（`listings.csv`） | 是否为 Superhost |
| `host_response_time`（`listings.csv`） | 房东响应速度 |
| `host_total_listings_count`（`listings.csv`） | 房东拥有的房源总数 |
| `accommodates`（`listings.csv`） | 房源可接待人数 |
| `amenities`（`listings.csv`） | JSON 字段；解析后计算设施数量 |
| `price`（`listings.csv`） | 每晚价格 |
| `review_scores_rating`、`review_scores_communication`、`review_scores_cleanliness`（`listings.csv`） | 住客评分 |
| `instant_bookable`（`listings.csv`） | 是否支持即时预订 |
| `comments`（`reviews.csv`，按 `listing_id` 汇总） | 评论数量、平均评论长度、正向情感评论比例；评论数量要与 `number_of_reviews` 核对 |
| `first_review`、`last_review`（`listings.csv`） | 计算第一条评论到最近一条评论的天数差 |
| `number_of_reviews`（`listings.csv`） | 因变量；作为成功预订数量的代理指标 |

评论文本特征应先在评论层面计算，再汇总到房源层面。`amenities` 也必须先解析 JSON，不能把原始字符串直接当作设施数量。

## 4. 建模要求

### 首选方法：计数回归

将 `number_of_reviews` 作为计数型结果变量，使用：

- **Poisson regression**，或
- **Negative Binomial regression**。

报告必须包含：

- 零评论房源的比例；
- 结果变量的方差与均值之比（variance-to-mean ratio）；
- 根据实际离散程度解释为什么选择 Poisson 或 Negative Binomial。

不能只引用“计数数据通常使用某个模型”的一般规则，必须用本次下载数据的证据支持模型选择。

### 可接受的替代方法

也可以对 `log(1 + number_of_reviews)` 使用线性回归，但必须：

1. 根据评论数量的偏度解释为什么需要对数变换；
2. 明确说明这相对于文献常用的 Poisson / Negative Binomial 方法是一种简化。

## 5. 方法严谨性

项目重点不只是生成模型输出，还包括：

- 正确地把评论级数据汇总到房源级；
- 正确解析 `amenities` JSON 字段；
- 解释模型选择及其适用条件；
- 说明数据处理、模型和研究问题之间的关系；
- 讨论方法的优点、局限，以及评论数量作为预订代理指标的限制。

两个数据文件都会定期更新。不同小组使用的下载批次可能不同，因此样本量和结果不一定相同；报告应记录自己的下载日期、数据字典版本和实际行数。

## 6. 研究背景

项目简介引用了以下研究，报告应阅读并正确引用原文：

- Biswas, B., Sengupta, P. & Chatterjee, D. (2020). *Examining the determinants of the count of customer reviews in peer-to-peer home-sharing platforms using clustering and count regression techniques*. Decision Support Systems, 135, 113324.
- Sengupta, P., Biswas, B., Kumar, A., Shankar, R. & Gupta, S. (2021). *Examining the predictors of successful Airbnb bookings with Hurdle models: Evidence from Europe, Australia, USA and Asia-Pacific cities*. Journal of Business Research, 137, 538–554.
- Zhang, L., Yan, Q. & Zhang, L. (2018). *A computational framework for understanding antecedents of guests' perceived trust towards hosts on Airbnb*. Decision Support Systems, 115, 105–116.

还可以查阅 Tourism Management、Annals of Tourism Research 和 International Journal of Hospitality Management 等旅游与酒店管理期刊中的相关研究。

## 7. 完成检查清单

- [ ] 下载 Dublin 和第二城市的 `listings.csv`、`reviews.csv`。
- [ ] 记录下载日期、原始行数和数据字典版本。
- [ ] 先按 `listing_id` 汇总评论，再与 `listings.csv` 连接。
- [ ] 解析 `amenities` 并计算设施数量。
- [ ] 核对评论数量与 `number_of_reviews`。
- [ ] 报告零评论比例和方差与均值之比。
- [ ] 选择并解释 Poisson、Negative Binomial 或经说明的对数线性替代模型。
- [ ] 结合文献、Dublin 结果和业务场景提出建议。
- [ ] 在报告中引用官方数据字典和学术文献。
