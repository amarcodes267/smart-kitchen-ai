from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

try:
    from .preprocessing import preprocess_data
except ImportError:
    # Support direct execution with ``python ml/train.py``
    from preprocessing import preprocess_data


# =========================================================
# PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_PATH = BASE_DIR / "ml" / "model.pkl"
NATIVE_MODEL_PATH = BASE_DIR / "ml" / "model.json"


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

    if len(X) < 10:
        raise ValueError("Not enough training records.")

    print(f"\nTotal records: {len(X)}")
    print(f"Total features: {len(feature_columns)}")

    # -----------------------------------------------------
    # Chronological Temporal Split (Prevents Lookahead Leakage)
    # -----------------------------------------------------
    if "date" in X.columns:
        print("\nApplying chronological temporal split (80% train / 20% test)...")
        cutoff_date = X["date"].quantile(0.8)
        print(f"Cutoff date: {cutoff_date.date()}")

        train_mask = X["date"] <= cutoff_date
        test_mask = X["date"] > cutoff_date

        X_train = X.loc[train_mask, feature_columns]
        X_test = X.loc[test_mask, feature_columns]
        y_train = y[train_mask]
        y_test = y[test_mask]
    else:
        print("\nApplying sequential chronological split (80% train / 20% test)...")
        split_idx = int(len(X) * 0.8)
        feature_df = X[feature_columns] if all(c in X.columns for c in feature_columns) else X
        X_train = feature_df.iloc[:split_idx]
        X_test = feature_df.iloc[split_idx:]
        y_train = y.iloc[:split_idx]
        y_test = y.iloc[split_idx:]

    print(f"Training records: {len(X_train)}")
    print(f"Testing records:  {len(X_test)}")

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
    model.fit(X_train, y_train)
    print("Model training completed.")

    # -----------------------------------------------------
    # Evaluate Model
    # -----------------------------------------------------
    print("\nEvaluating model...")

    pred_train = model.predict(X_train)
    pred_test = model.predict(X_test)

    train_mae = mean_absolute_error(y_train, pred_train)
    train_rmse = np.sqrt(mean_squared_error(y_train, pred_train))
    train_r2 = r2_score(y_train, pred_train)

    test_mae = mean_absolute_error(y_test, pred_test)
    test_mse = mean_squared_error(y_test, pred_test)
    test_rmse = np.sqrt(test_mse)
    test_r2 = r2_score(y_test, pred_test)

    print("\n--- TRAIN METRICS ---")
    print(f"MAE:  {train_mae:.4f}")
    print(f"RMSE: {train_rmse:.4f}")
    print(f"R²:   {train_r2:.4f}")

    print("\n--- TEST METRICS (Unseen Temporal Horizon) ---")
    print(f"MAE:  {test_mae:.4f}")
    print(f"MSE:  {test_mse:.4f}")
    print(f"RMSE: {test_rmse:.4f}")
    print(f"R²:   {test_r2:.4f}")

    # -----------------------------------------------------
    # Save Model
    # -----------------------------------------------------
    model_data = {
        "model": model,
        "features": feature_columns,
        "metrics": {
            "test_mae": float(test_mae),
            "test_rmse": float(test_rmse),
            "test_r2": float(test_r2)
        }
    }

    joblib.dump(model_data, MODEL_PATH)

    try:
        model.save_model(str(NATIVE_MODEL_PATH))
        print(f"\nNative XGBoost JSON model saved to: {NATIVE_MODEL_PATH}")
    except Exception as e:
        print(f"Could not export native JSON format: {e}")

    print("\n===================================")
    print("      MODEL SAVED SUCCESSFULLY")
    print("===================================")
    print(f"Location: {MODEL_PATH}")
    print("\nFeatures stored:")
    for feature in feature_columns:
        print(f" - {feature}")

    return model_data


if __name__ == "__main__":
    train_model()
