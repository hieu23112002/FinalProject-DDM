import pandas as pd
import os
import requests
import logging

# Cấu hình logging để theo dõi quá trình thực thi
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataIngestor:
    """
    Lớp này chịu trách nhiệm tải dữ liệu từ nguồn bên ngoài và lưu trữ cục bộ.
    """
    def __init__(self, raw_data_path: str):
        self.raw_data_path = raw_data_path
        self.dataset_url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
        
        # Tạo thư mục nếu chưa tồn tại
        os.makedirs(os.path.dirname(self.raw_data_path), exist_ok=True)

    def download_data(self):
        """Tải dữ liệu từ URL về máy cục bộ."""
        try:
            logging.info(f"Đang tải dữ liệu từ: {self.dataset_url}")
            response = requests.get(self.dataset_url)
            response.raise_for_status()
            
            with open(self.raw_data_path, 'wb') as file:
                file.write(response.content)
            logging.info(f"Tải dữ liệu thành công và lưu tại: {self.raw_data_path}")
        except Exception as error:
            logging.error(f"Lỗi khi tải dữ liệu: {error}")
            raise

    def load_as_dataframe(self) -> pd.DataFrame:
        """Đọc dữ liệu đã tải thành Pandas DataFrame."""
        if not os.path.exists(self.raw_data_path):
            self.download_data()
        
        dataframe = pd.read_csv(self.raw_data_path)
        logging.info(f"Dữ liệu đã được nạp với kích thước: {dataframe.shape}")
        return dataframe

if __name__ == "__main__":
    # Điểm thực thi chính để kiểm tra script
    RAW_PATH = "data/raw/telco_churn.csv"
    ingestor = DataIngestor(RAW_PATH)
    data = ingestor.load_as_dataframe()
    print(data.head())