import os
import smtplib
import random
import glob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from PyQt5.QtWidgets import QMessageBox

# Import Views
from src.views.windows.main_window import MainWindow
from src.views.windows.login_window import LoginScreen
from src.views.windows.result_dialog import ResultDialog, _FEATURE_ORDER
from src.views.components.widgets import CustomMessageBox

# Import Models & Controllers
from src.models.stress_model import StressModel
from src.models.auth_model import AuthModel
from src.models.history_model import HistoryModel
from src.controllers.history_controller import HistoryController

class MainApplicationController:
    def __init__(self):
        # 1. Khởi tạo Models
        models_dir = os.path.join(os.getcwd(), "models")
        pkl_files = glob.glob(os.path.join(models_dir, "*.pkl"))
        model_filepath = pkl_files[0] if pkl_files else os.path.join(models_dir, "stress_model_random_forest.pkl")
            
        self.stress_model = StressModel(model_path=model_filepath)
        self.auth_model = AuthModel()
        self.history_model = HistoryModel()

        self.current_user_id = None
        self.current_user_name = ""

        # 2. Khởi tạo Views
        self.login_window = LoginScreen()
        self.main_window = MainWindow()

        # 3. Khởi tạo Controller cho Lịch Sử
        self.history_controller = HistoryController(
            model=self.history_model,
            view=self.main_window.get_screen("history")
        )
        self.history_controller.on_data_changed_callback = self.refresh_dashboard_data

        # 4. Kết nối sự kiện
        self._connect_auth_signals()
        self._connect_app_signals()

    def _connect_auth_signals(self):
        self.login_window.login_requested.connect(self.handle_login)
        self.login_window.register_requested.connect(self.handle_register)
        self.login_window.send_otp_requested.connect(self.handle_send_otp)
        self.login_window.update_pwd_requested.connect(self.handle_update_pwd)

    def start(self):
        self.login_window.show()

    def handle_login(self, email, password):
        user = self.auth_model.login(email, password)
        if user:
            self.current_user_id = user["id"]
            self.current_user_name = user["full_name"]
            
            self.main_window.set_user(self.current_user_name)
            
            # Đồng bộ User ID cho Lịch sử NGAY LẬP TỨC khi đăng nhập
            self.history_controller.set_current_user(self.current_user_id)
            self.refresh_dashboard_data()

            self.login_window.hide()
            self.main_window.show()
        else:
            QMessageBox.warning(self.login_window, "Thất bại", "Email hoặc mật khẩu không chính xác.")

    def handle_register(self, data: dict):
        if data['password'] != data['confirm_password']:
            QMessageBox.warning(self.login_window, "Lỗi", "Mật khẩu xác nhận không khớp.")
            return

        success, msg = self.auth_model.register(data)
        if success:
            QMessageBox.information(self.login_window, "Thành công", msg)
            self.login_window._stack.setCurrentIndex(0)
        else:
            QMessageBox.warning(self.login_window, "Lỗi", msg)

    def handle_send_otp(self, email):
        if not self.auth_model.check_email_exists(email):
            CustomMessageBox.show_warning(self.login_window, "Lỗi", "Email này không tồn tại trong hệ thống!")
            return
            
        otp = str(random.randint(100000, 999999))
        if not hasattr(self, 'otp_storage'):
            self.otp_storage = {}
        self.otp_storage[email] = otp
        
        try:
            smtp_email = os.getenv("SMTP_EMAIL", "email_cua_ban@gmail.com") 
            smtp_password = os.getenv("SMTP_PASSWORD", "matkhauungdung") 
            
            msg = MIMEMultipart()
            msg['From'] = f"Vaultex Stress Predictor <{smtp_email}>"
            msg['To'] = email
            msg['Subject'] = "Mã xác thực Khôi phục Mật khẩu"
            body = f"Xin chào,\n\nMã OTP khôi phục mật khẩu của bạn là: {otp}\n\nVui lòng không chia sẻ mã này."
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)
            server.quit()
            
            CustomMessageBox.show_success(self.login_window, "Thành công", f"Đã gửi mã OTP đến {email}!")
        except Exception as e:
            print(f"Lỗi SMTP: {e}")
            CustomMessageBox.show_error(self.login_window, "Lỗi", "Không thể gửi email lúc này. Vui lòng kiểm tra cấu hình.")

    def handle_update_pwd(self, email, otp, pwd, conf_pwd):
        email = email.strip()
        otp = otp.strip()
        
        if not hasattr(self, 'otp_storage') or email not in self.otp_storage:
            CustomMessageBox.show_warning(self.login_window, "Từ chối", "Bạn chưa yêu cầu mã OTP cho email này!")
            return
        if self.otp_storage[email] != otp:
            CustomMessageBox.show_error(self.login_window, "Sai OTP", "Mã OTP không chính xác!")
            return
        if pwd != conf_pwd:
            CustomMessageBox.show_warning(self.login_window, "Lỗi", "Mật khẩu xác nhận không khớp.")
            return
        if len(pwd) < 6:
            CustomMessageBox.show_warning(self.login_window, "Lỗi", "Mật khẩu mới phải có ít nhất 6 ký tự.")
            return

        success = self.auth_model.update_password(email, pwd)
        if success:
            CustomMessageBox.show_success(self.login_window, "Thành công", "Đổi mật khẩu thành công! Hãy đăng nhập lại.")
            del self.otp_storage[email] 
            self.login_window._stack.setCurrentIndex(0)
        else:
            CustomMessageBox.show_error(self.login_window, "Lỗi", "Hệ thống lỗi khi lưu mật khẩu mới.")

    def _connect_app_signals(self):
        survey_screen = self.main_window.get_screen("survey")
        if survey_screen:
            survey_screen.survey_submitted.connect(self.handle_survey_submission)

        # ĐÃ SỬA LỖI RACE CONDITION TẠI ĐÂY: Lắng nghe sự kiện chuyển trang thực sự thay vì nút bấm
        self.main_window.stack.currentChanged.connect(self.handle_tab_changed)

    def handle_tab_changed(self, current_idx):
        # Index 0 là Dashboard, Index 2 là Trang Lịch Sử
        if current_idx == 0: 
            self.refresh_dashboard_data()
        elif current_idx == 2:
            self.history_controller.refresh_history_view()

    def refresh_dashboard_data(self):
        dashboard_screen = self.main_window.get_screen("dashboard")
        if not dashboard_screen or not self.current_user_id: 
            return

        metrics = self.stress_model.get_dashboard_metrics(self.current_user_id)
        if metrics:
            dashboard_screen.update_dashboard_data(
                summary_dict=metrics.get("summary_dict", {}),
                chart_data=metrics.get("chart_data", {}),
                history_list=metrics.get("history_list", [])
            )

    def handle_survey_submission(self, payload_dict: dict):
        if not self.current_user_id: 
            return
            
        try:
            raw_result = self.stress_model.process_new_survey(self.current_user_id, payload_dict)
            feature_list = [payload_dict.get(key, 0.0) for key in _FEATURE_ORDER]
            self.show_result_dialog(int(raw_result), feature_list)
            
            # Cập nhật data cho cả 2 trang ngay sau khi nộp bài
            self.refresh_dashboard_data()
            self.history_controller.refresh_history_view()
        except Exception as e:
            print(f"Lỗi khi xử lý khảo sát: {e}")

    def show_result_dialog(self, level: int, feature_list: list):
        dialog = ResultDialog(level=level, payload=feature_list, parent=self.main_window)
        action = dialog.exec_()
        
        if action == ResultDialog.Rejected:
            survey_screen = self.main_window.get_screen("survey")
            if survey_screen: 
                survey_screen.reset()
        elif action == ResultDialog.Accepted:
            self.main_window._navigate_to(0)