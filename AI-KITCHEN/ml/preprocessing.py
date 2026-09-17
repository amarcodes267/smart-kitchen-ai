from pathlib import Path
import pandas as pd

try:
    from .feature_config import get_feature_columns
except ImportError:
    from feature_config import get_feature_columns


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"

DAILY_SALES_PATH = RAW_DATA_DIR / "kitchen_sales_daily.csv"
LEGACY_TRAIN_PATH = RAW_DATA_DIR / "kitchen_data.csv"
PROCESSED_OUTPUT_PATH = PROCESSED_DATA_DIR / "training_data.csv"


# =========================================================
# LOAD TRAINING DATA
# =========================================================

def load_training_data():
    if DAILY_SALES_PATH.exists():
        print(f"Loading daily kitchen sales dataset from: {DAILY_SALES_PATH}")
        df = pd.read_csv(DAILY_SALES_PATH)
        print(f"Loaded {len(df)} records.")
        return df
    elif LEGACY_TRAIN_PATH.exists():
        print(f"Loading legacy food demand dataset from: {LEGACY_TRAIN_PATH}")
        df = pd.read_csv(LEGACY_TRAIN_PATH)
        print(f"Loaded {len(df)} records.")
        return df
    else:
        raise FileNotFoundError(f"No training data found in {RAW_DATA_DIR}")


# =========================================================
# FEATURE ENGINEERING
# =========================================================

def create_features(df):
    df = df.copy()

    # Time-series daily kitchen sales format
    if "date" in df.columns and "quantity_sold" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        sort_cols = [c for c in ["kitchen_id", "menu_item_id", "date"] if c in df.columns]
        if not sort_cols:
            sort_cols = ["date"]
        df = df.sort_values(sort_cols)

        df["day_of_week"] = df["date"].dt.dayofweek
        df["month"] = df["date"].dt.month

        if "kitchen_id" in df.columns and "menu_item_id" in df.columns:
            df["previous_sales"] = df.groupby(["kitchen_id", "menu_item_id"])["quantity_sold"].shift(1)
            df["rolling_7_day_avg"] = df.groupby(["kitchen_id", "menu_item_id"])["quantity_sold"].transform(
                lambda s: s.rolling(window=7, min_periods=1).mean()
            )
        else:
            df["previous_sales"] = df["quantity_sold"].shift(1)
            df["rolling_7_day_avg"] = df["quantity_sold"].rolling(window=7, min_periods=1).mean()

        df = df.dropna(subset=["previous_sales", "rolling_7_day_avg", "quantity_sold"])

        feature_columns = get_feature_columns()
        X = df[feature_columns]
        y = df["quantity_sold"]

        # Preserve date for chronological train/test split
        X_with_date = X.copy()
        X_with_date["date"] = df["date"]

        PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        export_df = X.copy()
        export_df["quantity_sold"] = y
        export_df["date"] = df["date"]
        export_df.to_csv(PROCESSED_OUTPUT_PATH, index=False)

        return X_with_date, y, feature_columns

    # Legacy Kaggle Food Delivery format
    df["price_difference"] = df["checkout_price"] - df["base_price"]
    df["discount_percentage"] = 0.0
    mask = df["base_price"] != 0
    df.loc[mask, "discount_percentage"] = (
        (df.loc[mask, "base_price"] - df.loc[mask, "checkout_price"])
        / df.loc[mask, "base_price"] * 100
    )
    df["promotion_score"] = df.get("emailer_for_promotion", 0) + df.get("homepage_featured", 0)
    df["week_mod_4"] = df["week"] % 4

    legacy_features = [
        "week", "center_id", "meal_id", "checkout_price", "base_price",
        "emailer_for_promotion", "homepage_featured", "price_difference",
        "discount_percentage", "promotion_score", "week_mod_4"
    ]
    X = df[legacy_features]
    y = df["num_orders"]
    return X, y, legacy_features


# =========================================================
# COMPLETE PREPROCESSING PIPELINE
# =========================================================

def preprocess_data():
    print("\n==============================")
    print("PREPROCESSING FOOD DEMAND DATA")
    print("==============================\n")

    df = load_training_data()
    X, y, feature_columns = create_features(df)

    print("\nFeatures created:")
    for feature in feature_columns:
        print(f" - {feature}")

    print(f"\nFeature shape: {X.shape}")
    print(f"Target shape: {y.shape}")

    return X, y, feature_columns


if __name__ == "__main__":
    X, y, features = preprocess_data()
    print("\nPreprocessing completed successfully.")
    print("\nFirst 5 feature rows:")
    print(X.head())
    print("\nFirst 5 target values:")
    print(y.head())