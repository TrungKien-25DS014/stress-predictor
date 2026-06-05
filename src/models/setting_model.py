import bcrypt
from src.database.db_manager import DatabaseConnection

class SettingModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_user_profile(self, user_id: int) -> dict | None:
        """Lấy thông tin profile từ DB."""
        conn = self.db.get_connection()
        if not conn: return None
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT u.full_name, a.email, u.phone, u.gender, u.birthday 
                    FROM users u 
                    JOIN accounts a ON u.account_id = a.id 
                    WHERE u.id = %s
                """
                cursor.execute(sql, (user_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"[DB Error - Get Profile]: {e}")
            return None
        finally:
            conn.close()

    def update_user_profile(self, user_id: int, data: dict) -> bool:
        """Cập nhật thông tin cá nhân (không đổi email để đảm bảo tính toàn vẹn account)."""
        conn = self.db.get_connection()
        if not conn: return False
        try:
            with conn.cursor() as cursor:
                sql = """
                    UPDATE users 
                    SET full_name = %s, phone = %s, gender = %s, birthday = %s 
                    WHERE id = %s
                """
                cursor.execute(sql, (data['name'], data['phone'], data['gender'], data['dob'], user_id))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[DB Error - Update Profile]: {e}")
            return False
        finally:
            conn.close()

    def update_password(self, user_id: int, current_pwd: str, new_pwd: str) -> tuple[bool, str]:
        """Kiểm tra mật khẩu cũ và đổi mật khẩu mới."""
        conn = self.db.get_connection()
        if not conn: return False, "Lỗi kết nối cơ sở dữ liệu."
        try:
            with conn.cursor() as cursor:
                # 1. Lấy thông tin account hiện tại
                sql_get = "SELECT a.id, a.password FROM accounts a JOIN users u ON a.id = u.account_id WHERE u.id = %s"
                cursor.execute(sql_get, (user_id,))
                result = cursor.fetchone()
                
                if not result:
                    return False, "Không tìm thấy tài khoản."
                    
                # 2. Xác thực mật khẩu cũ
                hashed_password = result['password'].encode('utf-8')
                if not bcrypt.checkpw(current_pwd.encode('utf-8'), hashed_password):
                    return False, "Mật khẩu hiện tại không chính xác."
                    
                # 3. Mã hóa & cập nhật mật khẩu mới
                salt = bcrypt.gensalt()
                new_hashed = bcrypt.hashpw(new_pwd.encode('utf-8'), salt).decode('utf-8')
                sql_update = "UPDATE accounts SET password = %s WHERE id = %s"
                cursor.execute(sql_update, (new_hashed, result['id']))
                
            conn.commit()
            return True, "Cập nhật mật khẩu thành công!"
        except Exception as e:
            conn.rollback()
            print(f"[DB Error - Update Pwd Settings]: {e}")
            return False, "Lỗi hệ thống khi cập nhật mật khẩu."
        finally:
            conn.close()