"""Clean the Dublin Inside Airbnb listing and review files.

Run from the repository root with:

    python data-cleaning/clean_airbnb_data.py

The script writes compact listing-level outputs and a JSON validation report to
``data-cleaning/output``.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "dublin-data"
OUTPUT_DIR = ROOT / "data-cleaning" / "output"
MISSINGNESS_THRESHOLD = 0.50

# These are the listing fields that are relevant to booking performance.
# Columns with more than 50% missing values are removed from this candidate set.
USEFUL_LISTING_COLUMNS = [
    "id",
    "description",
    "host_id",
    "hosts_time_as_user_years",
    "hosts_time_as_user_months",
    "hosts_time_as_host_years",
    "hosts_time_as_host_months",
    "host_response_time",
    "host_response_rate",
    "host_acceptance_rate",
    "host_is_superhost",
    "host_listings_count",
    "host_total_listings_count",
    "host_has_profile_pic",
    "host_identity_verified",
    "neighbourhood_cleansed",
    "latitude",
    "longitude",
    "property_type",
    "room_type",
    "accommodates",
    "bathrooms_text",
    "bedrooms",
    "beds",
    "amenities",
    "price",
    "minimum_nights",
    "maximum_nights",
    "has_availability",
    "availability_30",
    "availability_60",
    "availability_90",
    "availability_365",
    "number_of_reviews",
    "first_review",
    "last_review",
    "review_scores_rating",
    "review_scores_cleanliness",
    "review_scores_communication",
    "review_scores_value",
    "instant_bookable",
]

# Raw columns replaced by clearer derived features below.
TRANSFORMED_SOURCE_COLUMNS = {
    "description",
    "hosts_time_as_user_years",
    "hosts_time_as_user_months",
    "hosts_time_as_host_years",
    "hosts_time_as_host_months",
    "amenities",
    "price",
    "bathrooms_text",
    "first_review",
    "last_review",
}


def parse_amenities(value: object) -> int:
    """Return the number of amenities in the source JSON-like value."""
    if pd.isna(value) or str(value).strip() in {"", "[]"}:
        return 0
    text = str(value)
    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        try:
            parsed = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            return 0
    return len(parsed) if isinstance(parsed, list) else 0


def parse_price(value: object) -> float:
    """Convert currency-formatted nightly prices to numbers."""
    if pd.isna(value):
        return np.nan
    cleaned = re.sub(r"[^0-9.\-]", "", str(value))
    return float(cleaned) if cleaned else np.nan


def parse_bathrooms(value: object) -> float:
    """Extract a numeric bathroom count from values such as '1.5 baths'."""
    if pd.isna(value):
        return np.nan
    text = str(value).lower()
    if "half" in text and not re.search(r"\d", text):
        return 0.5
    match = re.search(r"\d+(?:\.\d+)?", text)
    return float(match.group()) if match else np.nan


def months_from_years_and_months(years: pd.Series, months: pd.Series) -> pd.Series:
    """Combine separate tenure fields into one month count."""
    years_numeric = pd.to_numeric(years, errors="coerce")
    months_numeric = pd.to_numeric(months, errors="coerce")
    return years_numeric * 12 + months_numeric


def review_summary(reviews: pd.DataFrame, listing_ids: pd.Series) -> pd.DataFrame:
    """Aggregate review rows and include zero-review listings for reconciliation."""
    grouped = (
        reviews.assign(
            comment_length=reviews["comments"].fillna("").astype(str).str.len(),
            review_date=pd.to_datetime(reviews["date"], errors="coerce"),
        )
        .groupby("listing_id", as_index=False)
        .agg(
            reviews_count_from_reviews=("id", "size"),
            average_comment_length=("comment_length", "mean"),
            review_first_date_from_reviews=("review_date", "min"),
            review_last_date_from_reviews=("review_date", "max"),
        )
    )
    all_ids = pd.DataFrame({"listing_id": listing_ids.astype("int64")})
    result = all_ids.merge(grouped, on="listing_id", how="left")
    result["reviews_count_from_reviews"] = (
        result["reviews_count_from_reviews"].fillna(0).astype("int64")
    )
    return result


def clean_listings(
    listings: pd.DataFrame,
    review_agg: pd.DataFrame,
    raw_review_rows: int,
) -> tuple[pd.DataFrame, dict]:
    """Select, transform, and reconcile listing-level fields."""
    available = [column for column in USEFUL_LISTING_COLUMNS if column in listings.columns]
    missing_share = listings[available].isna().mean().sort_values(ascending=False)
    retained = [column for column in available if missing_share[column] <= MISSINGNESS_THRESHOLD]
    dropped = {
        column: round(float(missing_share[column]), 4)
        for column in available
        if column not in retained
    }

    cleaned = listings[retained].copy().rename(columns={"id": "listing_id"})

    # Derive compact, model-ready fields from the source columns.
    cleaned["description_length"] = listings["description"].fillna("").astype(str).str.len()
    cleaned["host_time_as_user_months_count"] = months_from_years_and_months(
        listings["hosts_time_as_user_years"], listings["hosts_time_as_user_months"]
    )
    cleaned["host_time_as_host_months_count"] = months_from_years_and_months(
        listings["hosts_time_as_host_years"], listings["hosts_time_as_host_months"]
    )
    cleaned["amenities_count"] = listings["amenities"].map(parse_amenities).astype("int64")
    cleaned["price_numeric"] = listings["price"].map(parse_price)
    cleaned["bathrooms_count"] = listings["bathrooms_text"].map(parse_bathrooms)

    first_review = pd.to_datetime(listings["first_review"], errors="coerce")
    last_review = pd.to_datetime(listings["last_review"], errors="coerce")
    cleaned["first_review_date"] = first_review.dt.strftime("%Y-%m-%d")
    cleaned["last_review_date"] = last_review.dt.strftime("%Y-%m-%d")
    cleaned["review_span_days"] = (last_review - first_review).dt.days

    cleaned = cleaned.drop(
        columns=[column for column in TRANSFORMED_SOURCE_COLUMNS if column in cleaned.columns],
        errors="ignore",
    )

    cleaned = cleaned.merge(review_agg, on="listing_id", how="left", validate="one_to_one")
    cleaned["review_count_difference"] = (
        cleaned["reviews_count_from_reviews"] - cleaned["number_of_reviews"]
    )
    cleaned["review_count_matches"] = cleaned["review_count_difference"].eq(0)

    output_order = [
        "listing_id",
        "number_of_reviews",
        "reviews_count_from_reviews",
        "review_count_difference",
        "review_count_matches",
        "average_comment_length",
        "review_first_date_from_reviews",
        "review_last_date_from_reviews",
        "description_length",
        "amenities_count",
        "price_numeric",
        "bathrooms_count",
        "host_time_as_user_months_count",
        "host_time_as_host_months_count",
        "host_id",
        "host_is_superhost",
        "host_listings_count",
        "host_has_profile_pic",
        "host_identity_verified",
        "neighbourhood_cleansed",
        "latitude",
        "longitude",
        "property_type",
        "room_type",
        "accommodates",
        "bedrooms",
        "beds",
        "minimum_nights",
        "maximum_nights",
        "has_availability",
        "availability_30",
        "availability_60",
        "availability_90",
        "availability_365",
        "first_review_date",
        "last_review_date",
        "review_span_days",
        "review_scores_rating",
        "review_scores_cleanliness",
        "review_scores_communication",
        "review_scores_value",
    ]
    output_order = [column for column in output_order if column in cleaned.columns]
    cleaned = cleaned[output_order]

    comparison = cleaned["review_count_difference"]
    report = {
        "missingness_threshold": MISSINGNESS_THRESHOLD,
        "raw_listing_rows": int(len(listings)),
        "raw_review_rows": int(raw_review_rows),
        "cleaned_listing_rows": int(len(cleaned)),
        "candidate_listing_columns": available,
        "retained_listing_columns": retained,
        "dropped_listing_columns_by_missing_share": dropped,
        "review_count_total_from_reviews": int(cleaned["reviews_count_from_reviews"].sum()),
        "review_count_total_from_listings": int(cleaned["number_of_reviews"].sum()),
        "review_count_exact_matches": int(cleaned["review_count_matches"].sum()),
        "review_count_match_rate": float(cleaned["review_count_matches"].mean()),
        "review_count_difference_min": int(comparison.min()),
        "review_count_difference_max": int(comparison.max()),
    }
    return cleaned, report


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    listings = pd.read_csv(RAW_DIR / "listings.csv")
    reviews = pd.read_csv(RAW_DIR / "reviews.csv")

    aggregated_reviews = review_summary(reviews, listings["id"])
    cleaned, report = clean_listings(listings, aggregated_reviews, raw_review_rows=len(reviews))

    if report["review_count_match_rate"] != 1.0:
        raise ValueError("Review counts do not reconcile for every listing.")
    if report["review_count_total_from_reviews"] != report["review_count_total_from_listings"]:
        raise ValueError("Total review counts do not reconcile.")

    cleaned.to_csv(OUTPUT_DIR / "cleaned_listings.csv", index=False)
    aggregated_reviews.to_csv(OUTPUT_DIR / "review_aggregation.csv", index=False)
    (OUTPUT_DIR / "cleaning_report.json").write_text(
        json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8"
    )

    print(f"Wrote {len(cleaned):,} cleaned listings to {OUTPUT_DIR / 'cleaned_listings.csv'}")
    print(f"Review count match rate: {report['review_count_match_rate']:.2%}")
    print("Dropped mostly-empty columns:")
    for column, share in report["dropped_listing_columns_by_missing_share"].items():
        print(f"  - {column}: {share:.1%} missing")


if __name__ == "__main__":
    main()
