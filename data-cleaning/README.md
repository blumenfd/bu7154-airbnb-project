# Dublin Airbnb data cleaning

This folder contains a small, reproducible pandas workflow for preparing the Dublin Inside Airbnb data for listing-level analysis.

## Run the cleaning workflow

From the repository root:

```bash
python data-cleaning/clean_airbnb_data.py
```

The script reads:

```text
dublin-data/listings.csv
dublin-data/reviews.csv
```

and writes:

```text
data-cleaning/output/cleaned_listings.csv
data-cleaning/output/review_aggregation.csv
data-cleaning/output/cleaning_report.json
```

## What the script does

1. Starts from a short list of fields related to booking performance.
2. Removes candidate fields with more than 50% missing values.
3. Converts `amenities` from JSON text into `amenities_count`.
4. Combines host tenure fields into:
   - `host_time_as_user_months_count`
   - `host_time_as_host_months_count`
5. Converts the currency-formatted `price` field into `price_numeric`.
6. Converts `bathrooms_text` into `bathrooms_count` where possible.
7. Creates `description_length` and `review_span_days`.
8. Aggregates `reviews.csv` to listing level before joining it to `listings.csv`.
9. Checks the aggregated review count against `listings.csv.number_of_reviews`.

The source fields used for derived features are removed from the cleaned output when the derived field is clearer. The original raw files remain unchanged.

## Review-count verification

The review aggregation is performed with this logic:

```python
review_summary = (
    reviews.groupby("listing_id", as_index=False)
    .agg(reviews_count_from_reviews=("id", "size"))
)

cleaned["review_count_difference"] = (
    cleaned["reviews_count_from_reviews"] - cleaned["number_of_reviews"]
)
cleaned["review_count_matches"] = cleaned["review_count_difference"].eq(0)
```

The script stops with an error if any listing does not reconcile. In the current Dublin snapshot, all 6,748 listings match and the total review count is 389,071 in both files.

## Assumptions to review

- The missingness cutoff is **50%**. A field is removed only when more than half of its values are missing.
- `host_listings_count` is retained because it is populated. `host_total_listings_count` is dropped because it is completely empty in this snapshot.
- `host_response_time`, `host_response_rate`, `host_acceptance_rate`, and `instant_bookable` are dropped because they are completely empty in this snapshot.
- Review-derived fields are retained for reconciliation and exploratory analysis. For a predictive model, consider whether review scores and text features are available before the booking outcome; otherwise they may cause target leakage.
- No sentiment score is created. A sentiment method and threshold should be agreed before adding a `positive_comment_share` feature.

## Suggested next decisions

Please suggest whether you want to:

1. change the 50% missingness cutoff;
2. keep or remove review scores and other review-derived predictors from the final modeling table;
3. add a sentiment feature for `comments`; or
4. keep any additional listing field that you consider important.
