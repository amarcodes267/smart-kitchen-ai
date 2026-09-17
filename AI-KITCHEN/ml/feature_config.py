"""
Feature configuration for the ML pipeline.
Exports the ordered list of feature columns used by preprocessing and the model.
"""

FEATURE_COLUMNS = [
    "day_of_week",
    "month",
    "previous_sales",
    "rolling_7_day_avg",
]

LEGACY_FEATURE_COLUMNS = [
    "week",
    "center_id",
    "meal_id",
    "checkout_price",
    "base_price",
    "emailer_for_promotion",
    "homepage_featured",
    "price_difference",
    "discount_percentage",
    "promotion_score",
    "week_mod_4",
]


def get_feature_columns():
    return FEATURE_COLUMNS


def get_legacy_feature_columns():
    return LEGACY_FEATURE_COLUMNS
