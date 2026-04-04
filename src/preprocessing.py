import pandas as pd
import numpy as np
import logging
import os
import sys
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChurnPreprocessor:
    """
    Lớp này thực hiện làm sạch dữ liệu và tạo các đặc trưng (Feature Engineering).
    """
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()

    def clean_data(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Làm sạch dữ liệu cơ bản."""
        df = dataframe.copy()
        
        # Loại bỏ ID khách hàng vì không có giá trị dự báo
        if 'customerID' in df.columns:
            df.drop('customerID', axis=1, inplace=True)

        # Chuyển đổi TotalCharges sang kiểu số (xử lý các khoảng trắng lỗi)
        df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
        
        # Điền giá trị thiếu của TotalCharges bằng 0 (thường là khách hàng mới chưa có hóa đơn)
        df['TotalCharges'] = df['TotalCharges'].fillna(0)
        
        logging.info("Hoàn thành làm sạch dữ liệu: Xử lý TotalCharges và loại bỏ ID.")
        return df

    def feature_engineering(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Tạo các đặc trưng mới để tăng độ chính xác của Model."""
        df = dataframe.copy()
        
        # 1. Tỷ lệ cước phí hàng tháng trên thời gian gắn bó
        # (Để tránh chia cho 0, cộng thêm 1 vào tenure)
        df['ChargePerTenure'] = df['MonthlyCharges'] / (df['tenure'] + 1)
        
        # 2. Tổng số lượng dịch vụ khách hàng đang sử dụng
        service_columns = ['PhoneService', 'MultipleLines', 'InternetService', 
                           'OnlineSecurity', 'OnlineBackup', 'DeviceProtection', 
                           'TechSupport', 'StreamingTV', 'StreamingMovies']
        
        # Kiểm tra xem các cột có tồn tại không trước khi xử lý
        existing_services = [col for col in service_columns if col in df.columns]
        df['TotalServicesUsed'] = df[existing_services].apply(
            lambda x: x.astype(str).str.contains('Yes').sum(), axis=1
        )
        
        # 3. Phân loại khách hàng theo thời gian gắn bó (Tenure Group)
        bins = [0, 12, 24, 48, 60, 100]
        labels = ['0-1y', '1-2y', '2-4y', '4-5y', '5y+']
        df['TenureGroup'] = pd.cut(df['tenure'], bins=bins, labels=labels)
        
        logging.info("Hoàn thành Feature Engineering: Đã tạo ChargePerTenure, TotalServicesUsed, TenureGroup.")
        return df

    def encode_and_split(self, dataframe: pd.DataFrame, target_column: str = 'Churn'):
        """Mã hóa các biến phân loại và chia tập dữ liệu Train/Test."""
        df = dataframe.copy()
        
        # Mã hóa cột mục tiêu (Target)
        if target_column in df.columns:
            le = LabelEncoder()
            df[target_column] = le.fit_transform(df[target_column].astype(str))
            self.label_encoders[target_column] = le

        # Mã hóa các cột categorical khác
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            self.label_encoders[col] = le

        # Chia dữ liệu
        X = df.drop(target_column, axis=1)
        y = df[target_column]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        logging.info(f"Dữ liệu đã được chia: Train={X_train.shape}, Test={X_test.shape}")
        return X_train, X_test, y_train, y_test

    def create_features(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Alias cho API; cùng logic với feature_engineering."""
        return self.feature_engineering(dataframe)

if __name__ == "__main__":
    # Đảm bảo thư mục src nằm trong sys.path để có thể import data_ingestion
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
        
    try:
        from data_ingestion import DataIngestor
        
        # Cấu hình đường dẫn (chạy từ thư mục gốc dự án)
        RAW_DATA_PATH = "data/raw/telco_churn.csv"
        PROCESSED_DIR = "data/processed"
        
        # 1. Ingestion: Tải dữ liệu
        ingestor = DataIngestor(RAW_DATA_PATH)
        raw_df = ingestor.load_as_dataframe()
        
        # 2. Preprocessing: Làm sạch và Feature Engineering
        preprocessor = ChurnPreprocessor()
        cleaned_df = preprocessor.clean_data(raw_df)
        featured_df = preprocessor.feature_engineering(cleaned_df)
        
        # 3. Split: Chia dữ liệu
        X_train, X_test, y_train, y_test = preprocessor.encode_and_split(featured_df)
        
        # 4. Save: Lưu kết quả
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        X_train.to_csv(f"{PROCESSED_DIR}/X_train.csv", index=False)
        X_test.to_csv(f"{PROCESSED_DIR}/X_test.csv", index=False)
        y_train.to_csv(f"{PROCESSED_DIR}/y_train.csv", index=False)
        y_test.to_csv(f"{PROCESSED_DIR}/y_test.csv", index=False)
        
        logging.info("--- TEST GIAI ĐOẠN 1 THÀNH CÔNG ---")
        logging.info(f"File đã lưu tại: {PROCESSED_DIR}")
        
    except ImportError as e:
        logging.error(f"Lỗi Import: Không tìm thấy file data_ingestion.py. Hãy đảm bảo bạn đang chạy từ root. Chi tiết: {e}")
    except Exception as e:
        logging.error(f"Lỗi không xác định: {e}")