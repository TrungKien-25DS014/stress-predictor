import os
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt5.QtWidgets import QMessageBox

class AuthController:
    def __init__(self, login_view, auth_model, app_navigator):
        self.view = login_view
        self.model = auth_model
        self.app_navigator = app_navigator # Callback để chuyển sang MainWindow
        
        # Lưu tạm OTP trong RAM: { "email": "123456" }
        self.otp_storage = {}
        
        self.SMTP_EMAIL = os.getenv("SMTP_EMAIL") 
        self.SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

        self._connect_signals()

    def _connect_signals(self):
        self.view.login_requested.connect(self.handle_login)
        self.view.register_requested.connect(self.handle_register)
        self.view.send_otp_requested.connect(self.handle_send_otp)
        self.view.update_pwd_requested.connect(self.handle_update_pwd)

    def handle_login(self, email, password):
        user_info = self.model.login(email, password)
        if user_info:
            print(f"[Login Success] Welcome, {user_info['full_name']}")
            # Gọi hàm chuyển màn hình ở main.py
            self.app_navigator(user_info)
        else:
            self.view._login_panel.show_error("⚠ Email hoặc mật khẩu không chính xác.")

    def handle_register(self, data):
        # Validate cơ bản
        if data['password'] != data['confirm_password']:
            QMessageBox.warning(self.view, "Lỗi", "Mật khẩu xác nhận không khớp!")
            return
            
        if len(data['password']) < 6:
            QMessageBox.warning(self.view, "Lỗi", "Mật khẩu phải có ít nhất 6 ký tự.")
            return
            
        if not data['email'] or not data['full_name']:
            QMessageBox.warning(self.view, "Lỗi", "Vui lòng nhập đủ Email và Họ tên.")
            return

        success, msg = self.model.register(data)
        if success:
            QMessageBox.information(self.view, "Thành công", msg)
            self.view._stack.setCurrentIndex(0) # Quay về form login
        else:
            QMessageBox.warning(self.view, "Lỗi đăng ký", msg)

    def handle_send_otp(self, email):
        if not self.model.check_email_exists(email):
            QMessageBox.warning(self.view, "Lỗi", "Email này không tồn tại trong hệ thống!")
            return
            
        # Tạo mã 6 số ngẫu nhiên
        otp = str(random.randint(100000, 999999))
        self.otp_storage[email] = otp
        
        # Gửi email thực tế
        try:
            msg = MIMEMultipart()
            msg['From'] = f"Vaultex Stress Predictor <{self.SMTP_EMAIL}>"
            msg['To'] = email
            msg['Subject'] = "Mã xác thực Khôi phục Mật khẩu"
            
            body = f"Xin chào,\n\nMã OTP khôi phục mật khẩu của bạn là: {otp}\n\nVui lòng không chia sẻ mã này cho bất kỳ ai."
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.SMTP_EMAIL, self.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            QMessageBox.information(self.view, "Thành công", f"Đã gửi mã OTP đến {email}!\nVui lòng kiểm tra hộp thư.")
        except Exception as e:
            print(f"[SMTP Error]: {e}")
            QMessageBox.critical(self.view, "Lỗi", "Không thể gửi email lúc này. Vui lòng kiểm tra lại kết nối mạng.")

    # Sửa lại định nghĩa hàm (khoảng dòng 62)
    def handle_update_pwd(self, email, otp, new_pwd, conf_pwd):
      if email not in self.otp_storage or self.otp_storage[email] != otp:
        QMessageBox.warning(self.view, "Lỗi", "Mã OTP không hợp lệ hoặc đã hết hạn!")
        return
        
    # BỔ SUNG KIỂM TRA TRÙNG KHỚP
      if new_pwd != conf_pwd:
        QMessageBox.warning(self.view, "Lỗi", "Mật khẩu xác nhận không khớp!")
        return
        
      if len(new_pwd) < 6:
        QMessageBox.warning(self.view, "Lỗi", "Mật khẩu mới phải có ít nhất 6 ký tự.")
        return
        
      if self.model.update_password(email, new_pwd):
        QMessageBox.information(self.view, "Thành công", "Đổi mật khẩu thành công! Hãy đăng nhập lại.")
        del self.otp_storage[email] 
        self.view._stack.setCurrentIndex(0) 
      else:
        QMessageBox.warning(self.view, "Lỗi", "Có lỗi xảy ra, vui lòng thử lại sau.")