from __future__ import annotations

from pathlib import Path
import logging

import pandas as pd
import requests


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATASET_URL = (
    "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/"
    "Telco-Customer-Churn.csv"
)


class DataIngestor:
    """Download and load the raw churn dataset."""

    def __init__(self, raw_data_path: str | Path, dataset_url: str = DEFAULT_DATASET_URL) -> None:
        self.raw_data_path = Path(raw_data_path)
        if not self.raw_data_path.is_absolute():
            self.raw_data_path = PROJECT_ROOT / self.raw_data_path

        self.dataset_url = dataset_url
        self.raw_data_path.parent.mkdir(parents=True, exist_ok=True)

    def download_data(self, timeout_seconds: int = 30) -> None:
        logging.info("Downloading dataset from %s", self.dataset_url)
        try:
            response = requests.get(self.dataset_url, timeout=timeout_seconds)
            response.raise_for_status()
            self.raw_data_path.write_bytes(response.content)
        except requests.RequestException as error:
            logging.error("Dataset download failed: %s", error)
            raise

        logging.info("Dataset saved to %s", self.raw_data_path)

    def load_as_dataframe(self) -> pd.DataFrame:
        if not self.raw_data_path.exists():
            self.download_data()

        dataframe = pd.read_csv(self.raw_data_path)
        logging.info("Loaded raw dataset with shape %s", dataframe.shape)
        return dataframe


if __name__ == "__main__":
    data = DataIngestor("data/raw/telco_churn.csv").load_as_dataframe()
    print(data.head())
