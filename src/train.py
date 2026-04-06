from __future__ import annotations

from pathlib import Path
import logging

import joblib
import lightgbm as lgb
import mlflow
import mlflow.sklearn
import pandas as pd

from preprocessing import (
    LEGACY_ENCODERS_PATH,
    PREPROCESSOR_ARTIFACT_PATH,
    PROCESSED_DIR,
    ChurnPreprocessor,
)


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"


class ChurnModelTrainer:
    """Train and persist the churn classification model."""

    def __init__(self, experiment_name: str = "Churn_Prediction_Production") -> None:
        mlflow.set_experiment(experiment_name)

    def load_training_data(self) -> tuple[pd.DataFrame, pd.Series]:
        X_train = pd.read_csv(PROCESSED_DIR / "X_train.csv")
        y_train = pd.read_csv(PROCESSED_DIR / "y_train.csv").iloc[:, 0]
        return X_train, y_train

    def load_preprocessor(self, feature_names: list[str]) -> ChurnPreprocessor:
        if PREPROCESSOR_ARTIFACT_PATH.exists():
            return ChurnPreprocessor.load(PREPROCESSOR_ARTIFACT_PATH)
        if LEGACY_ENCODERS_PATH.exists():
            return ChurnPreprocessor.from_legacy_artifacts(feature_names, LEGACY_ENCODERS_PATH)
        return ChurnPreprocessor.from_feature_names(feature_names)

    def train_model(self, X_train: pd.DataFrame, y_train: pd.Series) -> lgb.LGBMClassifier:
        with mlflow.start_run(run_name="LGBM_Production_Final"):
            model_parameters = {
                "n_estimators": 200,
                "learning_rate": 0.05,
                "class_weight": "balanced",
                "random_state": 42,
            }

            classifier = lgb.LGBMClassifier(**model_parameters, verbose=-1)
            classifier.fit(X_train, y_train)

            mlflow.log_params(model_parameters)
            mlflow.sklearn.log_model(classifier, "model")

            MODELS_DIR.mkdir(parents=True, exist_ok=True)
            feature_names = X_train.columns.tolist()
            preprocessor = self.load_preprocessor(feature_names)
            preprocessor.feature_columns_ = feature_names

            joblib.dump(classifier, MODELS_DIR / "best_model.pkl")
            joblib.dump(feature_names, MODELS_DIR / "feature_names.pkl")
            preprocessor.save(MODELS_DIR / "preprocessor.pkl")

            logging.info("Training completed and model artifacts saved to %s", MODELS_DIR)
            return classifier


if __name__ == "__main__":
    trainer = ChurnModelTrainer()
    try:
        X_train_data, y_train_data = trainer.load_training_data()
        trainer.train_model(X_train_data, y_train_data)
        logging.info("Model training pipeline finished.")
    except Exception as error:
        logging.error("Training failed: %s", error)
