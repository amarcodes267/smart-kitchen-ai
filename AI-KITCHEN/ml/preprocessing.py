from pathlib import Path

import pandas as pd


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data" / "raw"

TRAIN_PATH = DATA_DIR / "kitchen_data.csv"


# =========================================================
# LOAD TRAINING DATA
# =========================================================

def load_training_data():

    print("Loading food demand dataset...")

    if not TRAIN_PATH.exists():

        raise FileNotFoundError(
            f"train.csv not found at: {TRAIN_PATH}"
        )

    df = pd.read_csv(TRAIN_PATH)

    print(
        f"Loaded {len(df)} records."
    )

    return df


# =========================================================
# BASIC CLEANING
# =========================================================

def clean_data(df):

    df = df.copy()

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Convert numeric columns
    numeric_columns = [
        "week",
        "center_id",
        "meal_id",
        "checkout_price",
        "base_price",
        "emailer_for_promotion",
        "homepage_featured",
        "num_orders"
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )


    # Remove rows where target is missing
    if "num_orders" in df.columns:

        df = df.dropna(
            subset=["num_orders"]
        )


    # Fill missing values
    for column in numeric_columns:

        if column in df.columns:

            df[column] = df[column].fillna(0)


    print(
        f"After cleaning: {len(df)} records."
    )

    return df


# =========================================================
# FEATURE ENGINEERING
# =========================================================

def create_features(df):

    df = df.copy()


    # -----------------------------------------------------
    # Price Difference
    # -----------------------------------------------------

    df["price_difference"] = (
        df["checkout_price"]
        - df["base_price"]
    )


    # -----------------------------------------------------
    # Discount Percentage
    # -----------------------------------------------------

    df["discount_percentage"] = 0.0

    mask = df["base_price"] != 0

    df.loc[mask, "discount_percentage"] = (

        (
            df.loc[mask, "base_price"]
            - df.loc[mask, "checkout_price"]
        )
        /
        df.loc[mask, "base_price"]
        * 100

    )


    # -----------------------------------------------------
    # Promotion Score
    # -----------------------------------------------------

    df["promotion_score"] = (

        df["emailer_for_promotion"]
        +
        df["homepage_featured"]

    )


    # -----------------------------------------------------
    # Week Information
    # -----------------------------------------------------

    df["week_mod_4"] = (
        df["week"] % 4
    )


    # -----------------------------------------------------
    # Select Features
    # -----------------------------------------------------

    feature_columns = [

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

        "week_mod_4"

    ]


    X = df[feature_columns]

    y = df["num_orders"]


    return X, y, feature_columns


# =========================================================
# COMPLETE PREPROCESSING PIPELINE
# =========================================================

def preprocess_data():

    print("\n==============================")
    print("PREPROCESSING FOOD DATA")
    print("==============================\n")


    # Load
    df = load_training_data()


    # Clean
    df = clean_data(df)


    # Create features
    X, y, feature_columns = create_features(
        df
    )


    print("\nFeatures created:")

    for feature in feature_columns:

        print(
            f" - {feature}"
        )


    print(
        f"\nFeature shape: {X.shape}"
    )

    print(
        f"Target shape: {y.shape}"
    )


    return X, y, feature_columns


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    X, y, features = preprocess_data()

    print("\nPreprocessing completed successfully.")

    print("\nFirst 5 feature rows:")

    print(
        X.head()
    )

    print("\nFirst 5 target values:")

    print(
        y.head()
    )