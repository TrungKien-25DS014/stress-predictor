import joblib
import pandas as pd
from datetime import datetime
from src.database.db_manager import DatabaseConnection # Đảm bảo đường dẫn đúng

class StressModel:
    """
    Lớp Model xử lý AI Prediction và tương tác với Database.
    Tuyệt đối không chứa code liên quan đến giao diện (PyQt5) ở đây.
    """
    def __init__(self, model_path="models/stress_model_random_forest.pkl"):
        self.db = DatabaseConnection()
        self.ai_model = self._load_ai_model(model_path)

    def _load_ai_model(self, path):
        try:
            return joblib.load(path)
        except Exception as e:
            print(f"Lỗi load AI model: {e}")
            return None

    def process_new_survey(self, user_id: int, payload: dict) -> float:
        """Thực hiện dự đoán AI và lưu thẳng vào Database."""
        if not self.ai_model:
            raise ValueError("AI Model chưa được tải.")

        # 1. Dự đoán bằng AI
        df = pd.DataFrame([payload])
        result = float(self.ai_model.predict(df)[0])

        # 2. Lưu kết quả vào Database
        conn = self.db.get_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    sql = """
                        INSERT INTO predictions 
                        (user_id, anxiety_level, self_esteem, mental_health_history, depression, 
                        headache, blood_pressure, sleep_quality, breathing_problem, noise_level, 
                        living_conditions, safety, basic_needs, academic_performance, study_load, 
                        teacher_student_relationship, future_career_concerns, social_support, 
                        peer_pressure, extracurricular_activities, bullying, prediction_result) 
                        VALUES 
                        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    # Map dữ liệu từ dictionary payload vào SQL
                    values = (
                        user_id,
                        payload.get("anxiety_level", 0), payload.get("self_esteem", 0),
                        payload.get("mental_health_history", 0), payload.get("depression", 0),
                        payload.get("headache", 0), payload.get("blood_pressure", 0),
                        payload.get("sleep_quality", 0), payload.get("breathing_problem", 0),
                        payload.get("noise_level", 0), payload.get("living_conditions", 0),
                        payload.get("safety", 0), payload.get("basic_needs", 0),
                        payload.get("academic_performance", 0), payload.get("study_load", 0),
                        payload.get("teacher_student_relationship", 0), payload.get("future_career_concerns", 0),
                        payload.get("social_support", 0), payload.get("peer_pressure", 0),
                        payload.get("extracurricular_activities", 0), payload.get("bullying", 0),
                        str(result)
                    )
                    cursor.execute(sql, values)
                conn.commit()
            except Exception as e:
                print(f"Lỗi Insert DB: {e}")
            finally:
                conn.close()
                
        return result

    # src/models/prediction_model.py

    def get_dashboard_metrics(self, user_id: int) -> dict:
        """[DASHBOARD] Lấy dữ liệu lịch sử TRONG 30 NGÀY GẦN NHẤT từ DB"""
        conn = self.db.get_connection()
        if not conn:
            return {}
            
        try:
            with conn.cursor() as cursor:
                # Dùng DATE_SUB(NOW(), INTERVAL 30 DAY) để lọc chuẩn 30 ngày trong MySQL
                sql = """
                    SELECT * FROM predictions 
                    WHERE user_id = %s AND predicted_at >= DATE_SUB(NOW(), INTERVAL 30 DAY) 
                    ORDER BY predicted_at ASC
                """
                cursor.execute(sql, (user_id,))
                records = cursor.fetchall()
                
                if not records:
                    return {}

                total_tests = len(records) # Tổng số lần test trong 30 ngày
                current_month = datetime.now().month
                monthly_tests = sum(1 for r in records if r['predicted_at'].month == current_month)
                
                scores = [float(r['prediction_result']) * 50 for r in records] 
                avg_stress = sum(scores) / len(scores) if scores else 0
                latest_stress = scores[-1] if scores else 0

                history_list = []
                for idx, r in enumerate(reversed(records)): 
                    history_list.append({
                        "datetime": r['predicted_at'].strftime("%Y-%m-%d %H:%M"),
                        "score": scores[-(idx+1)]
                    })

                return {
                    "summary_dict": {
                        "total_tests": total_tests, "monthly_tests": monthly_tests,
                        "avg_stress": avg_stress, "latest_stress": latest_stress,
                    },
                    "chart_data": {
                        "dates": [r['predicted_at'] for r in records],
                        "scores": scores
                    },
                    "history_list": history_list
                }
        finally:
            conn.close()

    def get_all_history(self, user_id: int) -> list[dict]:
        """[HISTORY PAGE] Hàm chuẩn bị sẵn để lấy TOÀN BỘ lịch sử (Không giới hạn ngày)"""
        conn = self.db.get_connection()
        if not conn:
            return []
        try:
            with conn.cursor() as cursor:
                # Lấy hết sạch sành sanh không lọc ngày tháng gì cả
                sql = "SELECT * FROM predictions WHERE user_id = %s ORDER BY predicted_at DESC"
                cursor.execute(sql, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Lỗi lấy toàn bộ lịch sử: {e}")
            return []
        finally:
            conn.close()