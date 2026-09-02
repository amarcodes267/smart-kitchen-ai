from pathlib import Path

import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor

try:
    from .preprocessing import preprocess_data
except ImportError:
    # Support direct execution with ``python ml/train.py`` as documented.
    from preprocessing import preprocess_data


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = BASE_DIR / "ml" / "model.pkl"


# =========================================================
# TRAIN MODEL
# =========================================================

def train_model():

    print("\n===================================")
    print("      AI KITCHEN MODEL TRAINING")
    print("===================================\n")


    # -----------------------------------------------------
    # Load + preprocess dataset
    # -----------------------------------------------------

    print("Preparing training data...")

    X, y, feature_columns = preprocess_data()


    # -----------------------------------------------------
    # Check dataset
    # -----------------------------------------------------

    if len(X) < 10:

        raise ValueError(
            "Not enough training records."
        )


    print(
        f"\nTotal records: {len(X)}"
    )

    print(
        f"Total features: {len(feature_columns)}"
    )


    # -----------------------------------------------------
    # Train/Test Split
    # -----------------------------------------------------

    X_train, X_test, y_train, y_test = train_test_split(

        X,

        y,

        test_size=0.2,

        random_state=42
    )


    print(
        f"\nTraining records: {len(X_train)}"
    )

    print(
        f"Testing records: {len(X_test)}"
    )


    # -----------------------------------------------------
    # Create XGBoost Model
    # -----------------------------------------------------

    print("\nCreating XGBoost model...")


    model = XGBRegressor(

        n_estimators=100,

        max_depth=5,

        learning_rate=0.05,

        subsample=0.8,

        colsample_bytree=0.8,

        objective="reg:squarederror",

        eval_metric="mae",

        random_state=42,

        n_jobs=2
    )


    # -----------------------------------------------------
    # Train
    # -----------------------------------------------------

    print("Training model...\n")


    model.fit(

        X_train,

        y_train
    )


    print(
        "Model training completed."
    )


    # -----------------------------------------------------
    # Test Model
    # -----------------------------------------------------

    print("\nEvaluating model...")


    predictions = model.predict(
        X_test
    )


    mae = mean_absolute_error(

        y_test,

        predictions
    )


    print(
        f"Mean Absolute Error: {mae:.2f}"
    )


    # -----------------------------------------------------
    # Save Model
    # -----------------------------------------------------

    model_data = {

        "model": model,

        "features": feature_columns

    }


    joblib.dump(

        model_data,

        MODEL_PATH
    )


    print(
        "\n==================================="
    )

    print(
        "MODEL SAVED SUCCESSFULLY"
    )

    print(
        "==================================="
    )

    print(
        f"\nLocation:\n{MODEL_PATH}"
    )

    print(
        "\nFeatures stored:"
    )

    for feature in feature_columns:

        print(
            f" - {feature}"
        )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    train_model()
