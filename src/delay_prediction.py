import os

import pandas as pd
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = "data/raw/o2c_orders.csv"
MODEL_DIR = "models"
REPORT_DIR = "reports"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_FILE)

print("=" * 70)
print("O2C DELAY PREDICTION")
print("=" * 70)

print(f"\nDataset size: {df.shape}")


# ============================================================
# FEATURES
# ============================================================

feature_columns = [
    "customer_type",
    "warehouse",
    "shipping_method",
    "product_category",
    "order_value",
    "manual_approval",
    "rework"
]

target = "delayed"


X = df[feature_columns].copy()
y = df[target].copy()


# ============================================================
# FEATURE TYPES
# ============================================================

categorical_features = [
    "customer_type",
    "warehouse",
    "shipping_method",
    "product_category"
]

numeric_features = [
    "order_value",
    "manual_approval",
    "rework"
]


# ============================================================
# PREPROCESSING
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
            categorical_features
        )
    ],
    remainder="passthrough"
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print(f"\nTraining samples: {len(X_train)}")
print(f"Testing samples : {len(X_test)}")


# ============================================================
# MODELS
# ============================================================

models = {

    "Logistic Regression":
        LogisticRegression(
            max_iter=1000
        ),

    "Random Forest":
        RandomForestClassifier(
            n_estimators=300,
            max_depth=10,
            random_state=42,
            class_weight="balanced"
        )
}


results = []


# ============================================================
# TRAIN + EVALUATE
# ============================================================

for model_name, model in models.items():

    print("\n" + "=" * 70)
    print(model_name)
    print("=" * 70)

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    pipeline.fit(
        X_train,
        y_train
    )

    y_pred = pipeline.predict(X_test)

    y_probability = pipeline.predict_proba(
        X_test
    )[:, 1]

    accuracy = accuracy_score(
        y_test,
        y_pred
    )

    precision = precision_score(
        y_test,
        y_pred
    )

    recall = recall_score(
        y_test,
        y_pred
    )

    f1 = f1_score(
        y_test,
        y_pred
    )

    roc_auc = roc_auc_score(
        y_test,
        y_probability
    )

    print(f"\nAccuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            y_pred
        )
    )

    print("Confusion Matrix:")
    print(
        confusion_matrix(
            y_test,
            y_pred
        )
    )

    results.append({
        "model": model_name,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc
    })

    # Save best-performing pipeline later
    if model_name == "Random Forest":

        import joblib

        joblib.dump(
            pipeline,
            f"{MODEL_DIR}/delay_prediction_model.pkl"
        )


# ============================================================
# MODEL COMPARISON
# ============================================================

results_df = pd.DataFrame(results)

print("\n" + "=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results_df
    .round(4)
    .to_string(index=False)
)


results_df.to_csv(
    f"{REPORT_DIR}/model_comparison.csv",
    index=False
)


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

print("\n" + "=" * 70)
print("RANDOM FOREST FEATURE IMPORTANCE")
print("=" * 70)


rf_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "model",
            RandomForestClassifier(
                n_estimators=300,
                max_depth=10,
                random_state=42,
                class_weight="balanced"
            )
        )
    ]
)


rf_pipeline.fit(
    X_train,
    y_train
)


model = rf_pipeline.named_steps["model"]

preprocessor_fitted = (
    rf_pipeline
    .named_steps["preprocessor"]
)

feature_names = (
    preprocessor_fitted
    .get_feature_names_out()
)

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": model.feature_importances_
})


importance_df = importance_df.sort_values(
    "importance",
    ascending=False
)


print(
    importance_df
    .head(15)
    .to_string(index=False)
)


importance_df.to_csv(
    f"{REPORT_DIR}/feature_importance.csv",
    index=False
)


# ============================================================
# FEATURE IMPORTANCE PLOT
# ============================================================

top_features = (
    importance_df
    .head(10)
    .sort_values("importance")
)


plt.figure(
    figsize=(10, 6)
)

plt.barh(
    top_features["feature"],
    top_features["importance"]
)

plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title(
    "Top Features for O2C Delay Prediction"
)

plt.tight_layout()

plt.savefig(
    f"{REPORT_DIR}/feature_importance.png",
    dpi=200
)

plt.close()


# ============================================================
# FINAL
# ============================================================

print("\n" + "=" * 70)
print("DELAY PREDICTION COMPLETE")
print("=" * 70)

print("\nSaved:")
print("models/delay_prediction_model.pkl")
print("reports/model_comparison.csv")
print("reports/feature_importance.csv")
print("reports/feature_importance.png")