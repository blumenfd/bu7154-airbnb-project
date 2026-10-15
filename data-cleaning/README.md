# Dublin Airbnb data cleaning

This folder contains a simple pandas workflow that prepares Airbnb listings for listing-level analysis.

## Run it

From the repository root:

```bash
python data-cleaning/clean_airbnb_data.py
```

The script reads:

```text
dublin-data/listings.csv
dublin-data/reviews.csv
```

It creates:

```text
data-cleaning/output/cleaned_listings.csv
data-cleaning/output/review_aggregation.csv
data-cleaning/output/cleaning_report.json
```

The original source files are not changed.

## Cleaning steps

1. Keep fields related to host, listing, price, location, availability, reviews, and booking performance.
2. Drop candidate fields with more than 50% missing values.
3. Convert `amenities` into `amenities_count`.
4. Combine host tenure fields into month counts.
5. Convert price and bathroom text into numeric fields.
6. Keep the full `description` text and create a separate `description_length` feature.
7. Aggregate reviews by `listing_id` before joining them to listings.
8. Compare total, last-30-day, last-12-month, and previous-calendar-year review counts with the listing file.

## Dropped columns

These five candidate columns are completely empty in the current data snapshot:

- `host_response_time`
- `host_response_rate`
- `host_acceptance_rate`
- `host_total_listings_count`
- `instant_bookable`

Other metadata and unrelated fields are excluded by the useful-feature selection.

`latitude` and `longitude` are also excluded from the cleaned listing table.

## Transformed columns

| Source column(s) | Output column |
|---|---|
| `description` | Kept as full text; `description_length` is added as a separate feature |
| `hosts_time_as_user_years`, `hosts_time_as_user_months` | `host_time_as_user_months_count` |
| `hosts_time_as_host_years`, `hosts_time_as_host_months` | `host_time_as_host_months_count` |
| `amenities` | `amenities_count` |
| `price` | `price_numeric` |
| `bathrooms_text` | `bathrooms_count` |
| `first_review`, `last_review` | `first_review_date`, `last_review_date` |
| `last_scraped` | `listing_last_scraped_date` |

The transformed source columns above are removed from the cleaned output after transformation. The original `description` text is retained.

The cleaned listing table does not include review audit fields such as `reviews_count_from_*`, difference columns, or match columns. Those checks remain in `cleaning_report.json` and `review_aggregation.csv` so the data can still be verified.

## `maximum_nights` check

The current source has 6,723 non-missing values. There are no zero or negative values. The distribution is concentrated at platform-style limits:

- 2,418 listings have `maximum_nights = 365`.
- 1,644 listings have `maximum_nights = 1125`.
- 42 listings have `maximum_nights = 999`.
- 43 listings have `maximum_nights = 730`.

The maximum value is 1,125. These values look like booking-policy caps rather than obvious data errors. For modeling, consider treating `maximum_nights` as a capped or grouped policy feature instead of using the raw highly skewed value. No change has been made yet.

## Review-count checks

The script uses each listing's `last_scraped` date as the reference date:

- `number_of_reviews`: all review rows
- `number_of_reviews_l30d`: reviews in the previous 30 days
- `number_of_reviews_ltm`: reviews in the previous 12 months
- `number_of_reviews_ly`: reviews in the previous calendar year

For each period, it calculates the difference from the listing file:

```python
cleaned["review_count_l30d_difference"] = (
    cleaned["reviews_count_l30d_from_reviews"]
    - cleaned["number_of_reviews_l30d"]
)
cleaned["review_count_l30d_matches"] = (
    cleaned["review_count_l30d_difference"].eq(0)
)
```

The script stops if any listing fails a check. The current snapshot has 6,748 exact matches for every period. The total review count is 389,071 in both files.

## Points to confirm

- Is the 50% missingness cutoff suitable?
- Should review scores and other review-derived fields be excluded from predictive models to avoid target leakage?
- Should a sentiment feature be added for `comments`? If so, which method and threshold should be used?
