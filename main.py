import sys
from PyQt5.QtWidgets import QApplication

# Import View
from src.UI.login import LoginScreen
from src.UI.main_window import MainWindow

# Import Model & Controller
from src.models.auth_model import AuthModel
from src.controllers.auth_controller import AuthController

def launch_main_window(user_info, login_window):
    """Callback kích hoạt sau khi đăng nhập thành công"""
    # Tạo và hiển thị màn hình chính
    global main_window
    main_window = MainWindow()
    
    # Pass tên user vào hàm set_user của MainWindow (như m đã code trong file main_window.py)
    main_window.set_user(user_info['full_name'])
    
    main_window.show()
    
    # Đóng màn hình đăng nhập
    login_window.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 1. Khởi tạo View, Model
    login_view = LoginScreen()
    auth_model = AuthModel()
    
    # 2. Khởi tạo Controller, nhét View, Model và hàm callback chuyển trang vào
    # Dùng lambda để truyền reference của login_view vào hàm launch
    auth_controller = AuthController(
        login_view=login_view, 
        auth_model=auth_model, 
        app_navigator=lambda user_info: launch_main_window(user_info, login_view)
    )
    
    # 3. Hiển thị UI Đăng nhập
    login_view.show()
    
    sys.exit(app.exec_())