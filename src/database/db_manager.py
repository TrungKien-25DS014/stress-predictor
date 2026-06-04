import os
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

load_dotenv()

class DatabaseConnection:
    def __init__(self):
        # Thiết lập cấu hình từ .env
        self.config = {
            'host': os.getenv('DB_HOST', '127.0.0.1'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'stress_prediction_db'),
            'charset': 'utf8mb4',
            'cursorclass': DictCursor
        }

    def get_connection(self):
        """Mở và trả về một kết nối MySQL mới."""
        try:
            return pymysql.connect(**self.config)
        except pymysql.MySQLError as e:
            print(f"Lỗi kết nối cơ sở dữ liệu: {e}")
            return None