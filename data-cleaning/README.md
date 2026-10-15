# Airbnb data cleaning

This folder contains a pandas workflow for preparing Dublin, Copenhagen, and Edinburgh Inside Airbnb data for listing-level analysis.

## Run the workflow

Run from the repository root:

```bash
python data-cleaning/clean_airbnb_data.py --city dublin
python data-cleaning/clean_airbnb_data.py --city copenhagen
python data-cleaning/clean_airbnb_data.py --city edinburgh
```

To process all three cities:

```bash
python data-cleaning/clean_airbnb_data.py --all
```

The script accepts both `.csv` and `.csv.gz` input files. It does not change the raw data.

### Input data

| City | Source folder | Snapshot |
|---|---|---|
| Dublin | `dublin-data/` | Existing project data |
| Copenhagen | `copenhagen-data/` | 25 September 2026 |
| Edinburgh | `edinburgh-data/` | 19 September 2026 |

Each city folder contains `listings` and `reviews` files. The downloaded city folders also contain `source_metadata.json` with the source URLs.

### Output data

Dublin outputs are written to `data-cleaning/output/`. Copenhagen and Edinburgh outputs are written to their own subfolders:

```text
data-cleaning/output/
data-cleaning/output/copenhagen/
data-cleaning/output/edinburgh/
```

Each output folder contains:

```text
cleaned_listings.csv
review_aggregation.csv
cleaning_report.json
```

## Cleaning steps

1. Keep fields related to hosts, listings, price, location, availability, reviews, and booking performance.
2. Drop candidate fields with more than 50% missing values.
3. Convert `amenities` into `amenities_count`.
4. Combine host tenure fields into month counts.
5. Convert price and bathroom text into numeric fields.
6. Keep the full `description` text and create `description_length`.
7. Add `maximum_nights_bucket` and `allows_long_stays` while retaining raw `maximum_nights`.
8. Aggregate reviews by `listing_id` before joining them to listings.
9. Compare total, last-30-day, last-12-month, and previous-calendar-year review counts with the listing file.

## Dropped columns

These candidate columns are completely empty in the current snapshots:

- `host_response_time`
- `host_response_rate`
- `host_acceptance_rate`
- `host_total_listings_count`
- `instant_bookable`

`latitude` and `longitude` are retained because location may be useful for spatial analysis and neighbourhood comparisons. Other metadata and unrelated fields are excluded by the useful-feature selection.

## Transformed columns

| Source column(s) | Output column |
|---|---|
| `description` | Kept as full text; `description_length` is added |
| `hosts_time_as_user_years`, `hosts_time_as_user_months` | `host_time_as_user_months_count` |
| `hosts_time_as_host_years`, `hosts_time_as_host_months` | `host_time_as_host_months_count` |
| `amenities` | `amenities_count` |
| `price` | `price_numeric` |
| `bathrooms_text` | `bathrooms_count` |
| `maximum_nights` | Raw value plus `maximum_nights_bucket` and `allows_long_stays` |
| `first_review`, `last_review` | `first_review_date`, `last_review_date` |
| `last_scraped` | `listing_last_scraped_date` |

The cleaned listing table does not include review audit fields such as `reviews_count_from_*`, difference columns, or match columns. Those checks remain in `cleaning_report.json` and `review_aggregation.csv`.

## Review-count checks

The script uses each listing's `last_scraped` date as the reference date:

- `number_of_reviews`: all review rows
- `number_of_reviews_l30d`: reviews in the previous 30 days
- `number_of_reviews_ltm`: reviews in the previous 12 months
- `number_of_reviews_ly`: reviews in the previous calendar year

For each period, it compares the count calculated from `reviews.csv` with the value in `listings.csv`. The script stops if any listing fails a check.

Current results:

| City | Listings | Reviews | Match rate for all four checks |
|---|---:|---:|---:|
| Dublin | 6,748 | 389,071 | 100% |
| Copenhagen | 22,845 | 495,775 | 100% |
| Edinburgh | 6,342 | 714,112 | 100% |

## Modeling notes

- Use the `maximum_nights_bucket` or `allows_long_stays` feature instead of relying only on raw `maximum_nights`.
- Review scores and review-derived fields may cause target leakage if they were recorded after the booking outcome. Consider this before predictive modeling.
- The raw `description` is retained for text analysis. If no text analysis is planned, `description_length` may be enough.
- No sentiment feature is created because a sentiment method and threshold have not been selected.
