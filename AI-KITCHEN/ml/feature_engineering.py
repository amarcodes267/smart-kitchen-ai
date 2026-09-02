import pandas as pd


def add_time_features(df):
    """
    Add useful time-based features.
    """

    df = df.copy()

    # Week of year
    if "week" in df.columns:
        df["week"] = pd.to_numeric(
            df["week"],
            errors="coerce"
        ).fillna(0)

        # Short-term cycle
        df["week_mod_4"] = df["week"] % 4

        # Longer-term cycle
        df["week_mod_12"] = df["week"] % 12

    return df


def add_price_features(df):
    """
    Create features related to food pricing.
    """

    df = df.copy()

    if (
        "checkout_price" in df.columns
        and "base_price" in df.columns
    ):

        df["price_difference"] = (
            df["checkout_price"]
            - df["base_price"]
        )

        df["discount_percentage"] = 0.0

        mask = df["base_price"] != 0

        df.loc[
            mask,
            "discount_percentage"
        ] = (
            (
                df.loc[
                    mask,
                    "base_price"
                ]
                -
                df.loc[
                    mask,
                    "checkout_price"
                ]
            )
            /
            df.loc[
                mask,
                "base_price"
            ]
            * 100
        )

    return df


def add_promotion_features(df):
    """
    Combine promotion-related columns.
    """

    df = df.copy()

    email_promotion = df.get(
        "emailer_for_promotion",
        0
    )

    homepage_featured = df.get(
        "homepage_featured",
        0
    )

    df["promotion_score"] = (
        email_promotion
        +
        homepage_featured
    )

    return df


def create_features(df):
    """
    Complete feature engineering pipeline.
    """

    df = df.copy()

    # Time features
    df = add_time_features(df)

    # Price features
    df = add_price_features(df)

    # Promotion features
    df = add_promotion_features(df)

    return df


if __name__ == "__main__":

    print(
        "Feature engineering module loaded successfully."
    )
