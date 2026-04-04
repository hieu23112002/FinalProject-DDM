import pandas as pd
import logging
import os
import mlflow
import mlflow.sklearn
import lightgbm as lgb
from sklearn.metrics import recall_score, f1_score, accuracy_score
import joblib

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChurnModelTrainer:
    """
    Huấn luyện mô hình, lưu vết thí nghiệm với MLflow và tạo giải thích SHAP.
    """
    def __init__(self, experiment_name: str = "Churn_Prediction_Production"):
        mlflow.set_experiment(experiment_name)

    def load_training_data(self):
        """Nạp dữ liệu từ thư mục processed."""
        X_train = pd.read_csv("data/processed/X_train.csv")
        y_train = pd.read_csv("data/processed/y_train.csv").values.ravel()
        return X_train, y_train

    def train_model(self, X_train, y_train):
        """Huấn luyện mô hình LightGBM và lưu Log vào MLflow."""
        with mlflow.start_run(run_name="LGBM_Production_Final"):
            model_parameters = {
                "n_estimators": 200,
                "learning_rate": 0.05,
                "class_weight": "balanced",
                "random_state": 42
            }
            
            # Khởi tạo và huấn luyện
            classifier = lgb.LGBMClassifier(**model_parameters, verbose=-1)
            classifier.fit(X_train, y_train)
            
            # Ghi nhận tham số và mô hình vào MLflow
            mlflow.log_params(model_parameters)
            mlflow.sklearn.log_model(classifier, "model")
            
            # Lưu model + tên cột (API sẽ tạo TreeExplainer lúc chạy — tránh pickle SHAP lỗi giữa Python versions)
            os.makedirs("models", exist_ok=True)
            joblib.dump(classifier, "models/best_model.pkl")
            joblib.dump(X_train.columns.tolist(), "models/feature_names.pkl")
            
            logging.info("Huấn luyện thành công. Đã lưu model và tên đặc trưng.")
            return classifier

if __name__ == "__main__":
    trainer = ChurnModelTrainer()
    try:
        X_train_data, y_train_data = trainer.load_training_data()
        trainer.train_model(X_train_data, y_train_data)
        logging.info("Giai đoạn 2: Huấn luyện mô hình hoàn tất.")
    except Exception as error:
        logging.error(f"Lỗi trong Giai đoạn 2: {error}")