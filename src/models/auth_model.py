import bcrypt
from src.database.db_manager import DatabaseConnection

class AuthModel:
    def __init__(self):
        # Gọi class kết nối DB của m
        self.db = DatabaseConnection()

    def login(self, email: str, raw_password: str) -> dict | None:
        """Kiểm tra đăng nhập. Trả về dict thông tin user nếu thành công, None nếu thất bại."""
        conn = self.db.get_connection()
        if not conn:
            return None
            
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT a.id as account_id, a.password, u.full_name 
                    FROM accounts a
                    JOIN users u ON a.id = u.account_id
                    WHERE a.email = %s
                """
                cursor.execute(sql, (email,))
                result = cursor.fetchone()

                if result:
                    hashed_password = result['password'].encode('utf-8')
                    if bcrypt.checkpw(raw_password.encode('utf-8'), hashed_password):
                        return {
                            "account_id": result['account_id'],
                            "full_name": result['full_name'],
                            "email": email
                        }
        except Exception as e:
            print(f"[DB Error - Login]: {e}")
        finally:
            conn.close()
            
        return None

    def check_email_exists(self, email: str) -> bool:
        """Kiểm tra email đã tồn tại trong hệ thống chưa."""
        conn = self.db.get_connection()
        if not conn:
            return True # Block đăng ký nếu lỗi DB
            
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM accounts WHERE email = %s", (email,))
                return cursor.fetchone() is not None
        except Exception as e:
            print(f"[DB Error - Check Email]: {e}")
            return True 
        finally:
            conn.close()

    def register(self, data: dict) -> tuple[bool, str]:
        """Đăng ký tài khoản mới. Trả về (Thành công?, Thông báo lỗi nếu có)."""
        if self.check_email_exists(data['email']):
            return False, "Email này đã được đăng ký!"

        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), salt).decode('utf-8')

        conn = self.db.get_connection()
        if not conn:
            return False, "Không thể kết nối đến cơ sở dữ liệu."

        try:
            with conn.cursor() as cursor:
                # 1. Insert vào accounts
                sql_account = "INSERT INTO accounts (email, password) VALUES (%s, %s)"
                cursor.execute(sql_account, (data['email'], hashed_password))
                account_id = cursor.lastrowid

                # 2. Insert vào users
                sql_user = """
                    INSERT INTO users (account_id, full_name, gender, birthday, phone)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql_user, (
                    account_id, 
                    data['full_name'], 
                    data['gender'], 
                    data['dob'], 
                    data['phone']
                ))
            
            conn.commit()
            return True, "Đăng ký thành công!"
            
        except Exception as e:
            conn.rollback()
            print(f"[DB Error - Register]: {e}")
            return False, "Lỗi hệ thống khi đăng ký. Vui lòng thử lại!"
        finally:
            conn.close()

    def update_password(self, email: str, new_password: str) -> bool:
        """Cập nhật mật khẩu mới (khi quên MK)."""
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
        
        conn = self.db.get_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cursor:
                sql = "UPDATE accounts SET password = %s WHERE email = %s"
                cursor.execute(sql, (hashed_password, email))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"[DB Error - Update Pwd]: {e}")
            return False
        finally:
            conn.close()