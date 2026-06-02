"""
main.py – Entry point của ứng dụng Stress Predictor
=====================================================

Luồng khởi chạy:
  ┌─────────────┐   login_success(display_name)   ┌──────────────┐
  │ LoginScreen │ ──────────────────────────────→  │  MainWindow  │
  │ (borderless)│                                  │  (full app)  │
  └─────────────┘                                  └──────────────┘

Trách nhiệm của main.py:
  1. Tạo QApplication với font & style mặc định
  2. Hiển thị LoginScreen
  3. Khi login_success phát → ẩn login, mở MainWindow với tên người dùng
  4. Giữ tham chiếu các cửa sổ để tránh garbage-collected
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from src.UI.screens.login import LoginScreen
from src.UI.main_window import MainWindow


class App:
    """
    Điều phối vòng đời ứng dụng.

    Tách logic khỏi hàm main() để:
      - Tránh closure / nonlocal phức tạp
      - Giữ tham chiếu cửa sổ an toàn (không bị GC thu hồi)
      - Dễ mở rộng sau này (logout, restart session…)
    """

    def __init__(self, q_app: QApplication):
        self._q_app     = q_app
        self._login_win: LoginScreen | None = None
        self._main_win:  MainWindow  | None = None

    # ------------------------------------------------------------------
    def run(self):
        """Khởi động ứng dụng – hiển thị LoginScreen và vào event loop."""
        self._show_login()
        sys.exit(self._q_app.exec_())

    # ------------------------------------------------------------------
    def _show_login(self):
        """Tạo và hiển thị cửa sổ đăng nhập."""
        self._login_win = LoginScreen()
        self._login_win.login_success.connect(self._on_login_success)
        self._login_win.show()

    # ------------------------------------------------------------------
    def _on_login_success(self, display_name: str):
        """
        Slot nhận signal login_success(display_name) từ LoginScreen.

        Thứ tự thực hiện:
          1. Ẩn LoginScreen (không destroy ngay để tránh crash trên macOS)
          2. Tạo MainWindow
          3. Truyền tên người dùng vào MainWindow qua set_user()
          4. Hiển thị MainWindow
          5. Đóng hẳn LoginScreen
        """
        # 1. Ẩn login trước để UX mượt
        if self._login_win:
            self._login_win.hide()

        # 2 & 3. Tạo MainWindow rồi set tên – đúng thứ tự
        self._main_win = MainWindow()
        self._main_win.set_user(display_name)

        # 4. Hiển thị
        self._main_win.show()

        # 5. Đóng hẳn LoginScreen sau khi MainWindow đã render
        if self._login_win:
            self._login_win.close()
            self._login_win = None


# ===========================================================================
# Entry point
# ===========================================================================
def main():
    app = QApplication(sys.argv)

    # Font mặc định toàn ứng dụng
    app.setFont(QFont("Segoe UI", 10))

    # Tắt ? trên title bar mặc định của Windows
    app.setStyle("Fusion")

    App(app).run()


if __name__ == "__main__":
    main()