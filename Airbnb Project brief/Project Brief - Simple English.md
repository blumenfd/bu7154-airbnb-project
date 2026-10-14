---
title: "Airbnb Project Brief (Simple English)"
course_code: BU7154
type: assignment-guide
source: "airbnb project brief.pdf"
---

# Airbnb Project Brief

This document is a simplified, structured version of the English project brief. Keep the original field names, model names, and links in your code and report.

## 1. Business question

An Airbnb host-support team wants to know:

- Which listing characteristics are significant predictors of successful bookings?
- Do findings from research across several cities also apply to Dublin?

Airbnb does not publish booking data. Use a listing's **number of guest reviews** as a proxy for successful bookings, and explain this limitation in the report.

## 2. Data

Download data from [Inside Airbnb – Get the Data](https://insideairbnb.com/get-the-data/) for Dublin and a comparison city. Use these files:

| File | Unit of observation | Main content |
|---|---|---|
| `listings.csv` | One row per listing | Host, price, capacity, amenities, and other listing attributes |
| `reviews.csv` | One row per guest review | `listing_id`, `id`, `date`, reviewer fields, and `comments` |

Use and cite the official [Inside Airbnb Data Dictionary](https://docs.google.com/spreadsheets/d/1iWCNJcSutYqpULSQHlNyGInUvHg2BoUGoNRIGa6Szc4/edit?usp=sharing). Record the dictionary version because the schema changes over time.

### Required data workflow

1. Record the download date and raw row count for each file.
2. Aggregate `reviews.csv` to one row per `listing_id` before joining it to `listings.csv`.
3. Create listing-level review measures, including review count and average comment length.
4. Join with `listings.csv` using `listings.id = reviews.listing_id`.
5. Report the row count after aggregation and joining.
6. Keep the final listing-level dataset at approximately 5,000–50,000 rows. Subsample a larger comparison city if needed.

Do not treat review-level rows as listing-level observations. Quarterly data refreshes can change the row counts and results, so report the actual values from your download.

### Comparison city

A stronger project can compare Dublin with a second city from Sengupta et al. (2021), such as Amsterdam, Barcelona, or Copenhagen. Discuss both the city comparison and the relationship to the published cross-city findings.

## 3. Variables

| Field | Use in the analysis |
|---|---|
| `host_is_superhost` | Superhost status |
| `host_response_time` | Host responsiveness |
| `host_total_listings_count` | Number of listings owned by the host |
| `accommodates` | Accommodation capacity |
| `amenities` | Parse the JSON field and count the amenities |
| `price` | Nightly price |
| `review_scores_rating` | Overall guest rating |
| `review_scores_communication` | Communication rating |
| `review_scores_cleanliness` | Cleanliness rating |
| `instant_bookable` | Booking policy |
| `comments` | Aggregate by listing to create comment count, average comment length, and the share of positive comments |
| `first_review`, `last_review` | Calculate the number of days between the first and most recent review |
| `number_of_reviews` | Dependent variable and proxy for successful bookings |

Calculate text features at review level first, then aggregate them to listing level. Check the aggregated comment count against `number_of_reviews`.

## 4. Modelling

### Primary approach

Treat `number_of_reviews` as a count outcome and fit either:

- Poisson regression; or
- Negative Binomial regression.

The report must include:

- the proportion of listings with zero reviews;
- the variance-to-mean ratio; and
- a data-based explanation for the selected count model.

Do not justify the model only with a general rule about count data. Use the dispersion observed in this dataset.

### Acceptable alternative

You may fit a linear regression using `log(1 + number_of_reviews)`. If you do so, explain the skewness that motivates the transformation and state that this is a simplification of the Poisson / Negative Binomial approach used in the literature.

## 5. Required interpretation

The project should explain:

- how reviews were aggregated and joined;
- how the `amenities` JSON field was parsed;
- why the chosen model fits the observed data;
- the strengths and limitations of the method; and
- why review count is only a proxy for bookings.

The report should connect the findings to the research literature and turn them into practical recommendations for Airbnb's host-support or platform team.

## 6. Key references

- Biswas, B., Sengupta, P. & Chatterjee, D. (2020). *Examining the determinants of the count of customer reviews in peer-to-peer home-sharing platforms using clustering and count regression techniques*. Decision Support Systems, 135, 113324.
- Sengupta, P., Biswas, B., Kumar, A., Shankar, R. & Gupta, S. (2021). *Examining the predictors of successful Airbnb bookings with Hurdle models: Evidence from Europe, Australia, USA and Asia-Pacific cities*. Journal of Business Research, 137, 538–554.
- Zhang, L., Yan, Q. & Zhang, L. (2018). *A computational framework for understanding antecedents of guests' perceived trust towards hosts on Airbnb*. Decision Support Systems, 115, 105–116.

You may also use relevant articles from *Tourism Management*, *Annals of Tourism Research*, and the *International Journal of Hospitality Management*.

## 7. Completion checklist

- [ ] Download Dublin and comparison-city `listings.csv` and `reviews.csv`.
- [ ] Record download dates, raw row counts, and the data dictionary version.
- [ ] Aggregate reviews by `listing_id` before joining.
- [ ] Parse `amenities` and count the amenities.
- [ ] Check aggregated review counts against `number_of_reviews`.
- [ ] Report zero-review listings and the variance-to-mean ratio.
- [ ] Fit and justify Poisson, Negative Binomial, or the stated log-linear alternative.
- [ ] Compare findings with prior research and make evidence-based recommendations.
