from __future__ import annotations

from pathlib import Path
import logging
from typing import Any

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RAW_DATA_PATH = DATA_DIR / "raw" / "telco_churn.csv"
LEGACY_ENCODERS_PATH = PROCESSED_DIR / "label_encoders.pkl"
PREPROCESSOR_ARTIFACT_PATH = PROCESSED_DIR / "preprocessor.pkl"


class ChurnPreprocessor:
    """Shared preprocessing logic for both training and inference."""

    def __init__(self) -> None:
        self.label_encoders: dict[str, LabelEncoder] = {}
        self.feature_columns_: list[str] = []
        self.target_column_: str | None = None

    def clean_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()

        if "customerID" in df.columns:
            df = df.drop(columns=["customerID"])

        if "TotalCharges" in df.columns:
            df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0.0)

        logging.info("Data cleaning completed.")
        return df

    def feature_engineering(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        df = dataframe.copy()
        df["ChargePerTenure"] = df["MonthlyCharges"] / (df["tenure"] + 1)

        service_columns = [
            "PhoneService",
            "MultipleLines",
            "InternetService",
            "OnlineSecurity",
            "OnlineBackup",
            "DeviceProtection",
            "TechSupport",
            "StreamingTV",
            "StreamingMovies",
        ]
        existing_services = [column for column in service_columns if column in df.columns]
        df["TotalServicesUsed"] = df[existing_services].apply(
            lambda row: row.astype(str).str.contains("Yes", regex=False).sum(),
            axis=1,
        )

        bins = [0, 12, 24, 48, 60, float("inf")]
        labels = ["0-1y", "1-2y", "2-4y", "4-5y", "5y+"]
        df["TenureGroup"] = pd.cut(df["tenure"], bins=bins, labels=labels, include_lowest=True)

        logging.info("Feature engineering completed.")
        return df

    def create_features(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        return self.feature_engineering(dataframe)

    def _fit_label_encoder(self, values: pd.Series) -> LabelEncoder:
        encoder = LabelEncoder()
        encoder.fit(values.astype(str).fillna("nan"))
        return encoder

    def fit(self, dataframe: pd.DataFrame, target_column: str = "Churn") -> ChurnPreprocessor:
        df = dataframe.copy()
        self.target_column_ = target_column if target_column in df.columns else None

        categorical_columns = list(df.select_dtypes(include=["object", "category"]).columns)
        if self.target_column_ and self.target_column_ in categorical_columns:
            categorical_columns.remove(self.target_column_)

        if self.target_column_:
            self.label_encoders[self.target_column_] = self._fit_label_encoder(df[self.target_column_])

        for column in categorical_columns:
            self.label_encoders[column] = self._fit_label_encoder(df[column])

        features = df.drop(columns=[target_column]) if self.target_column_ else df
        self.feature_columns_ = features.columns.tolist()
        return self

    def _transform_with_encoder(self, series: pd.Series, encoder: LabelEncoder) -> pd.Series:
        mapping = {str(label): index for index, label in enumerate(encoder.classes_)}
        return series.astype(str).fillna("nan").map(lambda value: mapping.get(value, -1)).astype(int)

    def transform(self, dataframe: pd.DataFrame, include_target: bool = False) -> pd.DataFrame:
        df = dataframe.copy()
        for column, encoder in self.label_encoders.items():
            if column == self.target_column_ and not include_target:
                continue
            if column in df.columns:
                df[column] = self._transform_with_encoder(df[column], encoder)
        return df

    def fit_transform_training(
        self,
        dataframe: pd.DataFrame,
        target_column: str = "Churn",
    ) -> tuple[pd.DataFrame, pd.Series]:
        cleaned_df = self.clean_data(dataframe)
        featured_df = self.feature_engineering(cleaned_df)
        self.fit(featured_df, target_column=target_column)
        transformed_df = self.transform(featured_df, include_target=True)

        X = transformed_df.drop(columns=[target_column])
        y = transformed_df[target_column]
        self.feature_columns_ = X.columns.tolist()
        return X, y

    def transform_for_inference(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        cleaned_df = self.clean_data(dataframe)
        featured_df = self.feature_engineering(cleaned_df)
        transformed_df = self.transform(featured_df, include_target=False)

        for column in self.feature_columns_:
            if column not in transformed_df.columns:
                transformed_df[column] = 0

        return transformed_df[self.feature_columns_]

    def save(self, path: str | Path) -> None:
        joblib.dump(self, path)

    @classmethod
    def load(cls, path: str | Path) -> ChurnPreprocessor:
        artifact = joblib.load(path)
        if not isinstance(artifact, cls):
            raise TypeError(f"Unexpected preprocessor artifact type: {type(artifact)!r}")
        return artifact

    @classmethod
    def from_feature_names(cls, feature_names: list[str]) -> ChurnPreprocessor:
        instance = cls()
        instance.feature_columns_ = feature_names
        instance.target_column_ = "Churn"
        return instance

    @classmethod
    def from_legacy_artifacts(
        cls,
        feature_names: list[str],
        encoders_path: str | Path = LEGACY_ENCODERS_PATH,
    ) -> ChurnPreprocessor:
        raw_encoders: dict[str, Any] = joblib.load(encoders_path)
        instance = cls()
        instance.label_encoders = raw_encoders
        instance.feature_columns_ = feature_names
        instance.target_column_ = "Churn" if "Churn" in raw_encoders else None
        return instance


def run_preprocessing_pipeline() -> None:
    from data_ingestion import DataIngestor

    raw_df = DataIngestor(RAW_DATA_PATH).load_as_dataframe()
    preprocessor = ChurnPreprocessor()
    X, y = preprocessor.fit_transform_training(raw_df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    X_train.to_csv(PROCESSED_DIR / "X_train.csv", index=False)
    X_test.to_csv(PROCESSED_DIR / "X_test.csv", index=False)
    y_train.to_frame(name="Churn").to_csv(PROCESSED_DIR / "y_train.csv", index=False)
    y_test.to_frame(name="Churn").to_csv(PROCESSED_DIR / "y_test.csv", index=False)
    joblib.dump(preprocessor.label_encoders, LEGACY_ENCODERS_PATH)
    preprocessor.save(PREPROCESSOR_ARTIFACT_PATH)

    logging.info("Preprocessing artifacts saved to %s", PROCESSED_DIR)


if __name__ == "__main__":
    run_preprocessing_pipeline()
