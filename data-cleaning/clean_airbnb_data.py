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
    "last_scraped",
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
    "number_of_reviews_ltm",
    "number_of_reviews_l30d",
    "number_of_reviews_ly",
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
    "hosts_time_as_user_years",
    "hosts_time_as_user_months",
    "hosts_time_as_host_years",
    "hosts_time_as_host_months",
    "amenities",
    "price",
    "bathrooms_text",
    "first_review",
    "last_review",
    "last_scraped",
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


def review_summary(
    reviews: pd.DataFrame,
    listings: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate total and time-window review counts by listing."""
    listing_dates = listings[["id", "last_scraped"]].rename(
        columns={"id": "listing_id", "last_scraped": "listing_last_scraped"}
    )
    dated_reviews = reviews.assign(
        comment_length=reviews["comments"].fillna("").astype(str).str.len(),
        review_date=pd.to_datetime(reviews["date"], errors="coerce"),
    ).merge(listing_dates, on="listing_id", how="left", validate="many_to_one")
    dated_reviews["listing_last_scraped"] = pd.to_datetime(
        dated_reviews["listing_last_scraped"], errors="coerce"
    )
    dated_reviews["within_last_30_days"] = (
        dated_reviews["review_date"].ge(
            dated_reviews["listing_last_scraped"] - pd.Timedelta(days=30)
        )
        & dated_reviews["review_date"].le(dated_reviews["listing_last_scraped"])
    )
    dated_reviews["within_last_12_months"] = (
        dated_reviews["review_date"].ge(
            dated_reviews["listing_last_scraped"] - pd.DateOffset(years=1)
        )
        & dated_reviews["review_date"].le(dated_reviews["listing_last_scraped"])
    )
    dated_reviews["within_previous_calendar_year"] = dated_reviews["review_date"].dt.year.eq(
        dated_reviews["listing_last_scraped"].dt.year - 1
    )
    grouped = dated_reviews.groupby("listing_id", as_index=False).agg(
        reviews_count_from_reviews=("id", "size"),
        reviews_count_l30d_from_reviews=("within_last_30_days", "sum"),
        reviews_count_ltm_from_reviews=("within_last_12_months", "sum"),
        reviews_count_ly_from_reviews=("within_previous_calendar_year", "sum"),
        average_comment_length=("comment_length", "mean"),
        review_first_date_from_reviews=("review_date", "min"),
        review_last_date_from_reviews=("review_date", "max"),
    )
    all_ids = pd.DataFrame({"listing_id": listings["id"].astype("int64")})
    result = all_ids.merge(grouped, on="listing_id", how="left")
    count_columns = [
        "reviews_count_from_reviews",
        "reviews_count_l30d_from_reviews",
        "reviews_count_ltm_from_reviews",
        "reviews_count_ly_from_reviews",
    ]
    result[count_columns] = result[count_columns].fillna(0).astype("int64")
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
    cleaned["listing_last_scraped_date"] = pd.to_datetime(
        listings["last_scraped"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")
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
    review_checks = {
        "review_count": ("reviews_count_from_reviews", "number_of_reviews"),
        "review_count_l30d": (
            "reviews_count_l30d_from_reviews",
            "number_of_reviews_l30d",
        ),
        "review_count_ltm": (
            "reviews_count_ltm_from_reviews",
            "number_of_reviews_ltm",
        ),
        "review_count_ly": (
            "reviews_count_ly_from_reviews",
            "number_of_reviews_ly",
        ),
    }
    for prefix, (from_reviews, from_listings) in review_checks.items():
        cleaned[f"{prefix}_difference"] = cleaned[from_reviews] - cleaned[from_listings]
        cleaned[f"{prefix}_matches"] = cleaned[f"{prefix}_difference"].eq(0)

    # Keep audit fields in memory for validation, but leave them out of the
    # cleaned listing table returned to downstream analysis.
    audit = cleaned.copy()

    output_order = [
        "listing_id",
        "listing_last_scraped_date",
        "description",
        "description_length",
        "number_of_reviews",
        "number_of_reviews_l30d",
        "number_of_reviews_ltm",
        "number_of_reviews_ly",
        "average_comment_length",
        "review_first_date_from_reviews",
        "review_last_date_from_reviews",
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

    comparison = audit["review_count_difference"]
    report = {
        "missingness_threshold": MISSINGNESS_THRESHOLD,
        "raw_listing_rows": int(len(listings)),
        "raw_review_rows": int(raw_review_rows),
        "cleaned_listing_rows": int(len(cleaned)),
        "candidate_listing_columns": available,
        "retained_listing_columns": retained,
        "dropped_listing_columns_by_missing_share": dropped,
        "review_windows": {
            "total": {
                "definition": "All review rows for each listing",
                "source_column": "number_of_reviews",
                "reviews_count_column": "reviews_count_from_reviews",
            },
            "last_30_days": {
                "definition": "Review date from last_scraped minus 30 days through last_scraped",
                "source_column": "number_of_reviews_l30d",
                "reviews_count_column": "reviews_count_l30d_from_reviews",
            },
            "last_12_months": {
                "definition": "Review date from last_scraped minus 12 months through last_scraped",
                "source_column": "number_of_reviews_ltm",
                "reviews_count_column": "reviews_count_ltm_from_reviews",
            },
            "previous_calendar_year": {
                "definition": "Review date in the calendar year before last_scraped",
                "source_column": "number_of_reviews_ly",
                "reviews_count_column": "reviews_count_ly_from_reviews",
            },
        },
        "review_count_checks": {
            "total": {
                "exact_matches": int(audit["review_count_matches"].sum()),
                "match_rate": float(audit["review_count_matches"].mean()),
                "difference_min": int(comparison.min()),
                "difference_max": int(comparison.max()),
                "total_from_reviews": int(audit["reviews_count_from_reviews"].sum()),
                "total_from_listings": int(cleaned["number_of_reviews"].sum()),
            },
            "last_30_days": {
                "exact_matches": int(audit["review_count_l30d_matches"].sum()),
                "match_rate": float(audit["review_count_l30d_matches"].mean()),
                "difference_min": int(audit["review_count_l30d_difference"].min()),
                "difference_max": int(audit["review_count_l30d_difference"].max()),
            },
            "last_12_months": {
                "exact_matches": int(audit["review_count_ltm_matches"].sum()),
                "match_rate": float(audit["review_count_ltm_matches"].mean()),
                "difference_min": int(audit["review_count_ltm_difference"].min()),
                "difference_max": int(audit["review_count_ltm_difference"].max()),
            },
            "previous_calendar_year": {
                "exact_matches": int(audit["review_count_ly_matches"].sum()),
                "match_rate": float(audit["review_count_ly_matches"].mean()),
                "difference_min": int(audit["review_count_ly_difference"].min()),
                "difference_max": int(audit["review_count_ly_difference"].max()),
            },
        },
    }
    return cleaned, report


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    listings = pd.read_csv(RAW_DIR / "listings.csv")
    reviews = pd.read_csv(RAW_DIR / "reviews.csv")

    aggregated_reviews = review_summary(reviews, listings)
    cleaned, report = clean_listings(listings, aggregated_reviews, raw_review_rows=len(reviews))

    if any(
        check["match_rate"] != 1.0
        for check in report["review_count_checks"].values()
    ):
        raise ValueError("One or more review-count windows do not reconcile.")
    if (
        report["review_count_checks"]["total"]["total_from_reviews"]
        != report["review_count_checks"]["total"]["total_from_listings"]
    ):
        raise ValueError("Total review counts do not reconcile.")

    cleaned.to_csv(OUTPUT_DIR / "cleaned_listings.csv", index=False)
    aggregated_reviews.to_csv(OUTPUT_DIR / "review_aggregation.csv", index=False)
    (OUTPUT_DIR / "cleaning_report.json").write_text(
        json.dumps(report, indent=2, default=str) + "\n", encoding="utf-8"
    )

    print(f"Wrote {len(cleaned):,} cleaned listings to {OUTPUT_DIR / 'cleaned_listings.csv'}")
    print("Review count match rates:")
    for window, check in report["review_count_checks"].items():
        print(f"  - {window}: {check['match_rate']:.2%}")
    print("Dropped mostly-empty columns:")
    for column, share in report["dropped_listing_columns_by_missing_share"].items():
        print(f"  - {column}: {share:.1%} missing")


if __name__ == "__main__":
    main()
