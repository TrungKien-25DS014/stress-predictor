"""
src/UI/screens/login.py
------------------------
Màn hình Đăng nhập – Vaultek Stress Tracker
Design System : Clinical Light
Layout        : 2 cột  [Brand Panel 45%] | [Form Panel 55%]
Window        : Windowed (1100×700), frame hệ điều hành gốc

Signal:
  login_success(display_name: str)  →  main.py mở MainWindow
"""

from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QLineEdit, QCheckBox,
    QPushButton, QMessageBox, QGraphicsDropShadowEffect,
    QApplication, QSizePolicy, QSpacerItem,
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QRect, QSize,
)
from PyQt5.QtGui import QFont, QColor, QPainter, QLinearGradient, QPen

from src.UI.components.custom_widgets import GlowLineEdit, GoldButton

# ---------------------------------------------------------------------------
# Mock credentials
# ---------------------------------------------------------------------------
_MOCK_USERS: dict[str, dict] = {
    "kienphan":  {"password": "kien123", "display_name": "Phan Trung Kiên"},
    "baonguyen": {"password": "bao123",  "display_name": "Nguyễn Hữu Bảo"},
    "admin":     {"password": "admin",   "display_name": "Quản trị viên"},
}

# ---------------------------------------------------------------------------
# Design Tokens
# ---------------------------------------------------------------------------
C = {
    "bg":             "#F0F4F8",
    "white":          "#FFFFFF",
    "accent":         "#007AFF",
    "accent_dark":    "#0055CC",
    "accent_light":   "#E8F3FF",
    "accent_hover":   "#0062CC",
    "gold":           "#D4AF37",
    "text":           "#1A2233",
    "muted":          "#6C757D",
    "divider":        "#E2E8F0",
    "danger":         "#DC3545",
    "success":        "#28A745",
    # Brand panel gradient stops
    "brand_top":      "#0A2463",
    "brand_mid":      "#1565C0",
    "brand_bot":      "#0D47A1",
}


# ===========================================================================
# BrandPanel – cột trái gradient xanh đậm
# ===========================================================================
class BrandPanel(QWidget):
    """Panel trái full-height với gradient xanh, logo và taglines."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._build_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        grad = QLinearGradient(0, 0, 0, self.height())
        grad.setColorAt(0.0,  QColor(C["brand_top"]))
        grad.setColorAt(0.5,  QColor(C["brand_mid"]))
        grad.setColorAt(1.0,  QColor(C["brand_bot"]))
        painter.fillRect(self.rect(), grad)

        # Vòng tròn trang trí
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 12))
        painter.drawEllipse(-80, -80, 320, 320)
        painter.setBrush(QColor(255, 255, 255, 8))
        painter.drawEllipse(self.width() - 180, self.height() - 200, 360, 360)
        painter.setBrush(QColor(255, 255, 255, 6))
        painter.drawEllipse(60, self.height() // 2 - 40, 160, 160)

        # Đường kẻ mỏng trang trí dưới cùng
        pen = QPen(QColor(255, 255, 255, 25))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(24, self.height() - 68, self.width() - 24, self.height() - 68)

        painter.end()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 52, 48, 40)
        layout.setSpacing(0)

        # ── Logo + App name ───────────────────────────────────────────
        logo_row = QHBoxLayout()
        logo_row.setAlignment(Qt.AlignLeft)

        logo_box = QFrame()
        logo_box.setFixedSize(44, 44)
        logo_box.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.15);
                border: 1.5px solid rgba(255,255,255,0.28);
                border-radius: 12px;
            }
        """)
        logo_lbl = QLabel("◆")
        logo_lbl.setFont(QFont("Segoe UI", 16, QFont.Bold))
        logo_lbl.setAlignment(Qt.AlignCenter)
        logo_lbl.setStyleSheet("color: white; background: transparent;")
        ll = QVBoxLayout(logo_box)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.addWidget(logo_lbl)

        app_name = QLabel("VAULTEX")
        app_name.setFont(QFont("Segoe UI Black", 16))
        app_name.setStyleSheet("color: white; letter-spacing: 4px; background: transparent;")

        logo_row.addWidget(logo_box)
        logo_row.addSpacing(14)
        logo_row.addWidget(app_name)
        layout.addLayout(logo_row)

        layout.addStretch(2)

        # ── Hero headline ─────────────────────────────────────────────
        headline = QLabel("Hiểu rõ bản thân.\nKiểm soát\nStress của bạn.")
        headline.setFont(QFont("Segoe UI Black", 27))
        headline.setStyleSheet("color: white; background: transparent;")
        headline.setWordWrap(True)
        layout.addWidget(headline)

        layout.addSpacing(16)

        # Thanh accent màu vàng
        accent_bar = QFrame()
        accent_bar.setFixedSize(48, 3)
        accent_bar.setStyleSheet("background: rgba(212,175,55,0.85); border: none; border-radius: 2px;")
        layout.addWidget(accent_bar)

        layout.addSpacing(18)

        # ── Tagline ───────────────────────────────────────────────────
        tagline = QLabel(
            "Ứng dụng phân tích sức khoẻ tâm lý dành riêng\n"
            "cho sinh viên — dựa trên dữ liệu khoa học."
        )
        tagline.setFont(QFont("Segoe UI", 10))
        tagline.setStyleSheet("color: rgba(255,255,255,0.68); background: transparent;")
        tagline.setWordWrap(True)
        layout.addWidget(tagline)

        layout.addSpacing(36)

        # ── 3 feature pills ───────────────────────────────────────────
        for icon, text in [
            ("📊", "Phân tích 20 yếu tố sức khoẻ"),
            ("🤖", "Dự đoán bằng AI / ML"),
            ("📅", "Theo dõi lịch sử theo thời gian"),
        ]:
            layout.addWidget(self._make_pill(icon, text))
            layout.addSpacing(10)

        layout.addStretch(3)

        # ── Footer ────────────────────────────────────────────────────
        footer_row = QHBoxLayout()
        ver = QLabel("Stress Predictor  v1.0")
        ver.setFont(QFont("Segoe UI", 8))
        ver.setStyleSheet("color: rgba(255,255,255,0.32); background: transparent;")
        edition = QLabel("Clinical Light")
        edition.setFont(QFont("Segoe UI", 8))
        edition.setStyleSheet("color: rgba(255,255,255,0.32); background: transparent;")
        footer_row.addWidget(ver)
        footer_row.addStretch()
        footer_row.addWidget(edition)
        layout.addLayout(footer_row)

    def _make_pill(self, icon: str, text: str) -> QFrame:
        pill = QFrame()
        pill.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.09);
                border: 1px solid rgba(255,255,255,0.17);
                border-radius: 10px;
            }
        """)
        row = QHBoxLayout(pill)
        row.setContentsMargins(16, 11, 16, 11)
        row.setSpacing(12)

        ico = QLabel(icon)
        ico.setFont(QFont("Segoe UI", 14))
        ico.setStyleSheet("background: transparent;")

        txt = QLabel(text)
        txt.setFont(QFont("Segoe UI", 9))
        txt.setStyleSheet("color: rgba(255,255,255,0.82); background: transparent;")

        row.addWidget(ico)
        row.addWidget(txt)
        row.addStretch()
        return pill


# ===========================================================================
# FormPanel – cột phải trắng chứa form đăng nhập
# ===========================================================================
class FormPanel(QWidget):
    """Panel phải màu trắng với window controls và form login."""

    login_success = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._shake_anim: QPropertyAnimation | None = None
        self.setStyleSheet(f"background: {C['white']};")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Vùng form chính
        scroll_area = QWidget()
        scroll_area.setStyleSheet("background: transparent;")
        scroll_layout = QVBoxLayout(scroll_area)
        scroll_layout.setAlignment(Qt.AlignVCenter)
        scroll_layout.setContentsMargins(72, 0, 72, 0)
        scroll_layout.setSpacing(0)

        self._form_widget = QWidget()
        self._form_widget.setStyleSheet("background: transparent;")
        self._form_widget.setObjectName("form_shake_target")
        form_layout = QVBoxLayout(self._form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(0)

        form_layout.addLayout(self._make_header())
        form_layout.addSpacing(32)
        form_layout.addLayout(self._make_form_fields())
        form_layout.addSpacing(14)
        form_layout.addLayout(self._make_options_row())
        form_layout.addSpacing(28)
        form_layout.addWidget(self._make_login_btn())
        form_layout.addSpacing(22)
        form_layout.addWidget(self._make_divider_line())
        form_layout.addSpacing(20)
        form_layout.addLayout(self._make_footer_links())

        scroll_layout.addStretch(1)
        scroll_layout.addWidget(self._form_widget)
        scroll_layout.addStretch(1)

        outer.addWidget(scroll_area, 1)

        # Thanh trạng thái bảo mật dưới cùng
        outer.addWidget(self._make_bottom_bar())

    # ------------------------------------------------------------------
    def _make_bottom_bar(self) -> QWidget:
        """Thanh footer hiển thị bảo mật và phiên bản."""
        bar = QWidget()
        bar.setFixedHeight(38)
        bar.setStyleSheet(f"""
            background: {C['bg']};
            border-top: 1px solid {C['divider']};
        """)
        row = QHBoxLayout(bar)
        row.setContentsMargins(20, 0, 20, 0)

        lock_lbl = QLabel("🔒  Kết nối được mã hoá  ·  SSL/TLS")
        lock_lbl.setFont(QFont("Segoe UI", 8))
        lock_lbl.setStyleSheet(f"color: {C['muted']}; background: transparent;")

        version_lbl = QLabel("v1.0.0")
        version_lbl.setFont(QFont("Segoe UI", 8))
        version_lbl.setStyleSheet(f"color: {C['muted']}; background: transparent;")

        row.addWidget(lock_lbl)
        row.addStretch()
        row.addWidget(version_lbl)
        return bar

    # ------------------------------------------------------------------
    def _make_header(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)

        welcome = QLabel("Chào mừng trở lại 👋")
        welcome.setFont(QFont("Segoe UI", 11))
        welcome.setStyleSheet(f"color: {C['accent']}; background: transparent;")

        title = QLabel("Đăng nhập vào\nVaultex Stress Tracker")
        title.setFont(QFont("Segoe UI Black", 22))
        title.setStyleSheet(f"color: {C['text']}; background: transparent; line-height: 1.2;")

        sub = QLabel("Nhập thông tin tài khoản để tiếp tục theo dõi\nsức khoẻ tâm lý của bạn.")
        sub.setFont(QFont("Segoe UI", 9))
        sub.setStyleSheet(f"color: {C['muted']}; background: transparent;")

        col.addWidget(welcome)
        col.addSpacing(8)
        col.addWidget(title)
        col.addSpacing(10)
        col.addWidget(sub)
        return col

    # ------------------------------------------------------------------
    def _make_form_fields(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(18)

        # ── Username ──────────────────────────────────────────────────
        col.addWidget(self._field_label("Tên tài khoản / Email"))
        self._username_input = GlowLineEdit("Nhập tên tài khoản…")
        self._username_input.setFixedHeight(50)
        self._username_input.returnPressed.connect(self._on_login)
        col.addWidget(self._username_input)

        # ── Password ──────────────────────────────────────────────────
        col.addWidget(self._field_label("Mật khẩu"))

        pwd_frame = QFrame()
        pwd_frame.setStyleSheet("background: transparent; border: none;")
        pwd_row = QHBoxLayout(pwd_frame)
        pwd_row.setContentsMargins(0, 0, 0, 0)
        pwd_row.setSpacing(0)

        self._password_input = GlowLineEdit("Nhập mật khẩu…")
        self._password_input.setFixedHeight(50)
        self._password_input.setEchoMode(QLineEdit.Password)
        self._password_input.returnPressed.connect(self._on_login)

        self._eye_btn = QPushButton("👁")
        self._eye_btn.setFixedSize(48, 50)
        self._eye_btn.setCursor(Qt.PointingHandCursor)
        self._eye_btn.setCheckable(True)
        self._eye_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; border: none;
                font-size: 14pt; color: {C['muted']};
            }}
            QPushButton:hover {{ color: {C['accent']}; }}
        """)
        self._eye_btn.toggled.connect(self._toggle_pwd)

        pwd_row.addWidget(self._password_input, 1)
        pwd_row.addWidget(self._eye_btn)
        col.addWidget(pwd_frame)

        # ── Error banner ──────────────────────────────────────────────
        self._error_lbl = QLabel("")
        self._error_lbl.setFont(QFont("Segoe UI", 9))
        self._error_lbl.setAlignment(Qt.AlignCenter)
        self._error_lbl.setStyleSheet(f"""
            color: {C['danger']};
            background: #FFF0F0;
            border: 1px solid #F5C6CB;
            border-radius: 8px;
            padding: 8px 12px;
        """)
        self._error_lbl.setVisible(False)
        col.addWidget(self._error_lbl)

        return col

    # ------------------------------------------------------------------
    def _make_options_row(self) -> QHBoxLayout:
        row = QHBoxLayout()

        self._remember_cb = QCheckBox("Ghi nhớ tôi")
        self._remember_cb.setFont(QFont("Segoe UI", 9))
        self._remember_cb.setStyleSheet(f"""
            QCheckBox {{
                color: {C['muted']}; spacing: 7px; background: transparent;
            }}
            QCheckBox::indicator {{
                width: 17px; height: 17px;
                border: 1.5px solid {C['divider']};
                border-radius: 4px;
                background: {C['white']};
            }}
            QCheckBox::indicator:checked {{
                background: {C['accent']}; border-color: {C['accent']};
            }}
        """)

        forgot_btn = QPushButton("Quên mật khẩu?")
        forgot_btn.setFont(QFont("Segoe UI", 9))
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C['accent']};
                border: none; text-decoration: underline;
            }}
            QPushButton:hover {{ color: {C['accent_dark']}; }}
        """)
        forgot_btn.clicked.connect(self._on_forgot)

        row.addWidget(self._remember_cb)
        row.addStretch()
        row.addWidget(forgot_btn)
        return row

    # ------------------------------------------------------------------
    def _make_login_btn(self) -> GoldButton:
        self._login_btn = GoldButton("ĐĂNG NHẬP", height=54)
        self._login_btn.setFont(QFont("Segoe UI Black", 11))
        self._login_btn.clicked.connect(self._on_login)
        return self._login_btn

    # ------------------------------------------------------------------
    def _make_divider_line(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        for i in range(2):
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet(f"background: {C['divider']}; border: none;")
            line.setFixedHeight(1)
            row.addWidget(line, 1)
            if i == 0:
                mid = QLabel("hoặc")
                mid.setFont(QFont("Segoe UI", 8))
                mid.setStyleSheet(f"color: {C['muted']}; background: transparent;")
                row.addWidget(mid)

        return container

    # ------------------------------------------------------------------
    def _make_footer_links(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignCenter)
        row.setSpacing(4)

        hint = QLabel("Chưa có tài khoản?")
        hint.setFont(QFont("Segoe UI", 9))
        hint.setStyleSheet(f"color: {C['muted']}; background: transparent;")

        reg_btn = QPushButton("Đăng ký ngay →")
        reg_btn.setFont(QFont("Segoe UI Semibold", 9))
        reg_btn.setCursor(Qt.PointingHandCursor)
        reg_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: {C['accent']};
                border: none; font-weight: 600;
            }}
            QPushButton:hover {{ color: {C['accent_dark']}; }}
        """)
        reg_btn.clicked.connect(self._on_register)

        row.addWidget(hint)
        row.addWidget(reg_btn)
        return row

    # ------------------------------------------------------------------
    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI Semibold", 9))
        lbl.setStyleSheet(f"color: {C['text']}; background: transparent;")
        return lbl

    # ------------------------------------------------------------------
    # Sự kiện
    # ------------------------------------------------------------------
    def _on_login(self):
        username = self._username_input.text().strip()
        password = self._password_input.text()

        if not username:
            self._show_error("⚠  Vui lòng nhập tên tài khoản.")
            self._username_input.setFocus()
            self._shake()
            return
        if not password:
            self._show_error("⚠  Vui lòng nhập mật khẩu.")
            self._password_input.setFocus()
            self._shake()
            return

        user = _MOCK_USERS.get(username.lower())
        if user is None or user["password"] != password:
            self._show_error("⚠  Tên tài khoản hoặc mật khẩu không đúng.")
            self._password_input.clear()
            self._password_input.setFocus()
            self._shake()
            return

        self._hide_error()
        if self._remember_cb.isChecked():
            print(f"[LoginScreen] Ghi nhớ: {username}")
        print(f"[LoginScreen] Thành công → {user['display_name']}")
        self.login_success.emit(user["display_name"])

    def _on_forgot(self):
        QMessageBox.information(
            self, "Quên mật khẩu",
            "Vui lòng liên hệ quản trị viên.\n📧  support@vaultex.edu.vn",
        )

    def _on_register(self):
        QMessageBox.information(
            self, "Đăng ký tài khoản",
            "Tính năng đang phát triển.\nLiên hệ nhà trường để nhận tài khoản.",
        )

    def _toggle_pwd(self, checked: bool):
        mode = QLineEdit.Normal if checked else QLineEdit.Password
        self._password_input.setEchoMode(mode)
        self._eye_btn.setText("🙈" if checked else "👁")

    def _show_error(self, msg: str):
        self._error_lbl.setText(msg)
        self._error_lbl.setVisible(True)

    def _hide_error(self):
        self._error_lbl.setVisible(False)

    def _shake(self):
        """Rung form khi đăng nhập thất bại."""
        if self._shake_anim and self._shake_anim.state() == QPropertyAnimation.Running:
            return
        target = self._form_widget
        r = target.geometry()
        self._shake_anim = QPropertyAnimation(target, b"geometry")
        self._shake_anim.setDuration(350)
        kv = [
            (0.00, r.x()),
            (0.15, r.x() - 12),
            (0.30, r.x() + 10),
            (0.45, r.x() - 8),
            (0.60, r.x() + 6),
            (0.75, r.x() - 4),
            (0.90, r.x() + 2),
            (1.00, r.x()),
        ]
        for t, x in kv:
            self._shake_anim.setKeyValueAt(t, QRect(x, r.y(), r.width(), r.height()))
        self._shake_anim.start()


# ===========================================================================
# LoginScreen – cửa sổ full screen ghép 2 panel
# ===========================================================================
class LoginScreen(QWidget):
    """
    Cửa sổ đăng nhập – windowed 1100×700, frame Windows gốc.

    Bố cục ngang:
      ┌───────────────────┬──────────────────────┐
      │   BrandPanel 45%  │    FormPanel  55%    │
      │  (gradient xanh)  │    (trắng + form)    │
      └───────────────────┴──────────────────────┘

    Signal:
      login_success(display_name: str)
    """

    login_success = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_window()
        self._build_ui()

    # ------------------------------------------------------------------
    def _init_window(self):
        self.setWindowTitle("Đăng nhập – Vaultek Stress Tracker")
        # Dùng frame hệ điều hành gốc (có nút minimize/maximize/close của Windows)
        self.setFixedSize(1100, 700)

        # Căn giữa màn hình
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width()  - 1100) // 2,
            (screen.height() - 700)  // 2,
        )

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Cột trái – Brand
        self._brand = BrandPanel()
        root.addWidget(self._brand, 45)

        # Đường kẻ phân cách
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background: {C['divider']}; border: none;")
        root.addWidget(sep)

        # Cột phải – Form
        self._form = FormPanel()
        self._form.login_success.connect(self.login_success)
        root.addWidget(self._form, 55)

    # ------------------------------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()
        super().keyPressEvent(event)