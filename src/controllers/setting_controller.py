from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDate
from src.models.setting_model import SettingModel
from src.views.components.widgets import CustomMessageBox
from src.core import config
class SettingController:
    def __init__(self, model: SettingModel, view):
        self.model = model
        self.view = view
        self.current_user_id = None
        
        self.view._btn_save.clicked.connect(self.handle_save_profile)
        self.view._btn_change_pw.clicked.connect(self.handle_change_password)
        
        # Khóa ô email không cho sửa (vì email dính tới bảng accounts và xác thực)
        self.view._input_email.setReadOnly(True)
        self.view._input_email.setStyleSheet(self.view._input_email.styleSheet() + "background-color: #F8F9FA; color: #6C757D;")

    def set_current_user(self, user_id: int):
        self.current_user_id = user_id
        self.load_profile_data()
        
    def load_profile_data(self):
        if not self.current_user_id: return
        data = self.model.get_user_profile(self.current_user_id)
        
        if data:
            # Parse ngày sinh từ DB (chuỗi 'yyyy-MM-dd') sang QDate
            dob_qdate = QDate.fromString(str(data['birthday']), "yyyy-MM-dd") if data['birthday'] else QDate(2000, 1, 1)
            
            self.view.load_profile(
                name=data['full_name'],
                email=data['email'],
                phone=data['phone'] or "",
                gender=data['gender'] or "Nam",
                dob=dob_qdate
            )

    def handle_save_profile(self):
        if not self.current_user_id: return
        data = self.view.get_settings_data() 
        success = self.model.update_user_profile(self.current_user_id, data)
        new_theme = data.get("theme", "light")
        theme_changed = (new_theme != config.CURRENT_THEME)
        
        if theme_changed:
            config.save_theme_config(new_theme)
            config.CURRENT_THEME = new_theme
        if success:
            msg = "Đã cập nhật thông tin cá nhân!"
            if theme_changed:
                msg += "\n\nVui lòng khởi động lại ứng dụng để áp dụng giao diện mới."
            CustomMessageBox.show_success(self.view, "Thành công", msg)
        else:
            CustomMessageBox.show_error(self.view, "Lỗi", "Không thể cập nhật thông tin. Vui lòng thử lại.")
            
    def handle_change_password(self):
        if not self.current_user_id: return
        
        cur_pw = self.view._input_cur_pw.text().strip()
        new_pw = self.view._input_new_pw.text().strip()
        confirm_pw = self.view._input_confirm_pw.text().strip()
        
        # Validate cơ bản
        if not cur_pw:
            self.view._show_warning("Vui lòng nhập mật khẩu hiện tại.")
            return
        if not new_pw or len(new_pw) < 6:
            self.view._show_warning("Mật khẩu mới phải có ít nhất 6 ký tự.")
            return
        if new_pw != confirm_pw:
            self.view._show_warning("Mật khẩu xác nhận không khớp.")
            return
            
        # Gọi xuống Model
        # Gọi xuống Model
        success, msg = self.model.update_password(self.current_user_id, cur_pw, new_pw)
        if success:
            CustomMessageBox.show_success(self.view, "Thành công", msg)
            self.view._btn_toggle_pw.setChecked(False) # Đóng form đổi mật khẩu lại
        else:
            CustomMessageBox.show_error(self.view, "Lỗi", msg)