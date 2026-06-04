# src/models/history_model.py
from src.database.db_manager import DatabaseConnection

class HistoryModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_user_history(self, user_id: int) -> list[dict]:
        """Truy vấn toàn bộ lịch sử kiểm tra của một người dùng, sắp xếp mới nhất lên đầu"""
        conn = self.db.get_connection()
        if not conn:
            return []
            
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT id, anxiety_level, self_esteem, mental_health_history, depression, 
                           headache, blood_pressure, sleep_quality, breathing_problem, noise_level, 
                           living_conditions, safety, basic_needs, academic_performance, study_load, 
                           teacher_student_relationship, future_career_concerns, social_support, 
                           peer_pressure, extracurricular_activities, bullying, prediction_result, 
                           predicted_at 
                    FROM predictions 
                    WHERE user_id = %s 
                    ORDER BY predicted_at DESC
                """
                cursor.execute(sql, (user_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"[DB Error - Get All History]: {e}")
            return []
        finally:
            conn.close()

    def delete_record(self, prediction_id: int) -> tuple[bool, str]:
        """Xóa một bản ghi lịch sử dựa trên ID"""
        conn = self.db.get_connection()
        if not conn:
            return False, "Không thể kết nối cơ sở dữ liệu."
            
        try:
            with conn.cursor() as cursor:
                sql = "DELETE FROM predictions WHERE id = %s"
                cursor.execute(sql, (prediction_id,))
            conn.commit()
            return True, "Đã xóa bản ghi lịch sử thành công!"
        except Exception as e:
            conn.rollback()
            print(f"[DB Error - Delete Record]: {e}")
            return False, "Lỗi hệ thống, không thể xóa bản ghi."
        finally:
            conn.close()