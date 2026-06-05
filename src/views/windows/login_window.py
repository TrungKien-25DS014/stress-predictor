from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QLineEdit, QCheckBox,
    QPushButton, QGraphicsDropShadowEffect,
    QApplication, QSizePolicy, QStackedWidget,
    QDateEdit, QComboBox
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QDate
)
from PyQt5.QtGui import QFont, QColor, QPainter, QLinearGradient, QPen

# Import từ thư mục project của bạn
from src.views.components.widgets import GlowLineEdit, GoldButton
from src.core.config import C

# Style chung cho nút Vàng Ánh Kim (Metallic Gold Gradient) - Lấy từ config
GOLD_BTN_STYLE = f"""
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                    stop:0 {C['btn_gold_edge']}, stop:0.5 {C['btn_gold_mid']}, stop:1 {C['btn_gold_edge']});
        color: {C['text_primary']};
        border-radius: 16px; 
        font-weight: bold;
        font-size: 15px;
        border: 1px solid {C['btn_gold_border']};
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                    stop:0 {C['btn_gold_h_edge']}, stop:0.5 {C['btn_gold_h_mid']}, stop:1 {C['btn_gold_h_edge']});
    }}
    QPushButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                    stop:0 {C['btn_gold_p_edge']}, stop:0.5 {C['btn_gold_p_mid']}, stop:1 {C['btn_gold_p_edge']});
    }}
"""

# =====================================================================
# CỘT TRÁI: BRAND PANEL
# =====================================================================
class BrandPanel(QWidget):
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

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 12))
        painter.drawEllipse(-80, -80, 320, 320)
        painter.setBrush(QColor(255, 255, 255, 8))
        painter.drawEllipse(self.width() - 180, self.height() - 200, 360, 360)
        painter.setBrush(QColor(255, 255, 255, 6))
        painter.drawEllipse(60, self.height() // 2 - 40, 160, 160)

        pen = QPen(QColor(255, 255, 255, 25))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawLine(24, self.height() - 68, self.width() - 24, self.height() - 68)
        painter.end()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(48, 52, 48, 40)
        layout.setSpacing(0)

        logo_row = QHBoxLayout()
        logo_row.setAlignment(Qt.AlignLeft)
        logo_box = QFrame()
        logo_box.setFixedSize(44, 44)
        logo_box.setStyleSheet("QFrame { background: rgba(255,255,255,0.15); border: none; border-radius: 12px; }")
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

        headline = QLabel("Hiểu rõ bản thân.\nKiểm soát\nStress của bạn.")
        headline.setFont(QFont("Segoe UI Black", 27))
        headline.setStyleSheet("color: white; background: transparent;")
        headline.setWordWrap(True)
        layout.addWidget(headline)
        layout.addSpacing(16)

        accent_bar = QFrame()
        accent_bar.setFixedSize(48, 3)
        accent_bar.setStyleSheet("background: rgba(212,175,55,0.85); border: none; border-radius: 2px;")
        layout.addWidget(accent_bar)
        layout.addSpacing(18)

        tagline = QLabel("Ứng dụng phân tích sức khoẻ tâm lý dành riêng\ncho sinh viên — dựa trên dữ liệu khoa học.")
        tagline.setFont(QFont("Segoe UI", 10))
        tagline.setStyleSheet("color: rgba(255,255,255,0.68); background: transparent;")
        tagline.setWordWrap(True)
        layout.addWidget(tagline)
        layout.addSpacing(36)

        for icon, text in [
            ("📊", "Phân tích 20 yếu tố sức khoẻ"),
            ("🤖", "Dự đoán bằng AI / ML"),
            ("📅", "Theo dõi lịch sử theo thời gian"),
        ]:
            layout.addWidget(self._make_pill(icon, text))
            layout.addSpacing(10)

        layout.addStretch(3)

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
        pill.setStyleSheet("QFrame { background: rgba(255,255,255,0.09); border: none; border-radius: 10px; }")
        row = QHBoxLayout(pill)
        row.setContentsMargins(16, 11, 16, 11)
        row.setSpacing(12)
        ico = QLabel(icon)
        ico.setFont(QFont("Segoe UI", 14))
        ico.setStyleSheet("background: transparent;")
        txt = QLabel(text)
        txt.setFont(QFont("Segoe UI", 9))
        txt.setStyleSheet("color: rgba(255,255,255,0.9); background: transparent; font-weight: 500;")
        row.addWidget(ico); row.addWidget(txt); row.addStretch()
        return pill

# =====================================================================
# HÀM TẠO PANE TRẮNG NỔI CHUNG
# =====================================================================
def create_floating_card(parent_widget: QWidget, width: int = 480) -> tuple[QVBoxLayout, QFrame]:
    parent_widget.setStyleSheet(f"background: {C['bg']};") 
    
    main_layout = QVBoxLayout(parent_widget)
    main_layout.setAlignment(Qt.AlignCenter)
    
    card = QFrame()
    card.setFixedWidth(width)
    card.setObjectName("FloatingCard")
    
    card.setStyleSheet(f"""
        #FloatingCard {{
            background: {C['white']};
            border-radius: 24px;  
            border: 1px solid {C['divider']};
        }}
        QLineEdit, QDateEdit, QComboBox {{
            background: {C['input_bg']};
            border: 1.2px solid {C['input_border']}; 
            border-radius: 16px; 
            padding: 10px 18px;   
            color: {C['text']};        
            font-size: 14px;
        }}
        QLineEdit:focus, QDateEdit:focus, QComboBox:focus {{
            border: 1.5px solid {C['accent']};
            background: {C['white']}; 
        }}
        QLineEdit::placeholder {{
            color: {C['muted']};   
        }}
        QDateEdit::drop-down, QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 30px;
            border-left-width: 0px;
        }}
        QDateEdit::down-arrow, QComboBox::down-arrow {{
            width: 14px;
            height: 14px;
        }}
    """)
    
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(30)
    shadow.setColor(QColor(0, 0, 0, 12))
    shadow.setOffset(0, 10)
    card.setGraphicsEffect(shadow)
    
    card_layout = QVBoxLayout(card)
    main_layout.addWidget(card)
    
    return card_layout, card

# =====================================================================
# CỘT PHẢI: CLASS 1 - ĐĂNG NHẬP
# =====================================================================
class LoginPanel(QWidget):
    login_requested = pyqtSignal(str, str)
    go_to_register = pyqtSignal()
    go_to_forgot_password = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        card_layout, _ = create_floating_card(self, width=460)
        card_layout.setContentsMargins(40, 45, 40, 40)
        
        card_layout.addLayout(self._make_header())
        card_layout.addSpacing(32)
        card_layout.addLayout(self._make_form_fields())
        card_layout.addSpacing(14)
        card_layout.addLayout(self._make_options_row())
        card_layout.addSpacing(28)
        card_layout.addWidget(self._make_login_btn())
        card_layout.addSpacing(25)
        card_layout.addWidget(self._make_divider_line())
        card_layout.addSpacing(25)
        card_layout.addLayout(self._make_footer_links())

    def _make_header(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(6)
        welcome = QLabel("Chào mừng trở lại 👋")
        welcome.setFont(QFont("Segoe UI", 11))
        welcome.setStyleSheet(f"color: {C['accent']}; background: transparent;")
        title = QLabel("Đăng nhập vào\nVaultex Tracker")
        title.setFont(QFont("Segoe UI Black", 22))
        title.setStyleSheet(f"color: {C['text']}; background: transparent;")
        sub = QLabel("Nhập thông tin tài khoản để tiếp tục.")
        sub.setFont(QFont("Segoe UI", 9))
        sub.setStyleSheet(f"color: {C['muted']}; background: transparent;")
        col.addWidget(welcome); col.addWidget(title); col.addWidget(sub)
        return col

    def _make_form_fields(self) -> QVBoxLayout:
        col = QVBoxLayout()
        col.setSpacing(10)
        
        col.addWidget(self._field_label("Tên tài khoản / Email"))
        self._username_input = QLineEdit() 
        self._username_input.setPlaceholderText("Nhập tên tài khoản…")
        self._username_input.setFixedHeight(49) 
        col.addWidget(self._username_input)
        
        col.addSpacing(6)

        col.addWidget(self._field_label("Mật khẩu"))
        self._password_input = QLineEdit()
        self._password_input.setPlaceholderText("Nhập mật khẩu…")
        self._password_input.setFixedHeight(49) 
        self._password_input.setEchoMode(QLineEdit.Password)
        col.addWidget(self._password_input)
        
        self._error_lbl = QLabel("")
        self._error_lbl.setStyleSheet(f"color: {C['danger']}; background: transparent;")
        self._error_lbl.setVisible(False)
        col.addWidget(self._error_lbl)
        
        return col

    def _make_options_row(self) -> QHBoxLayout:
        row = QHBoxLayout()
        self._remember_cb = QCheckBox("Ghi nhớ tôi")
        self._remember_cb.setStyleSheet(f"color: {C['text']}; background: transparent;")
        
        forgot_btn = QPushButton("Quên mật khẩu?")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.setStyleSheet(f"color: {C['accent']}; background: transparent; border: none; text-decoration: underline;")
        forgot_btn.clicked.connect(self.go_to_forgot_password.emit)
        
        row.addWidget(self._remember_cb); row.addStretch(); row.addWidget(forgot_btn)
        return row

    def _make_login_btn(self) -> GoldButton:
        self._login_btn = GoldButton("ĐĂNG NHẬP", height=53) 
        self._login_btn.setStyleSheet(GOLD_BTN_STYLE)
        self._login_btn.clicked.connect(self._on_login)
        return self._login_btn

    def _make_divider_line(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        row = QHBoxLayout(container)
        row.setContentsMargins(0, 0, 0, 0)
        line = QFrame(); line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background: {C['divider']}; border: none;")
        line.setFixedHeight(1)
        row.addWidget(line)
        return container

    def _make_footer_links(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignCenter)
        hint = QLabel("Chưa có tài khoản?")
        hint.setStyleSheet(f"color: {C['text']}; background: transparent;")
        reg_btn = QPushButton("Đăng ký ngay →")
        reg_btn.setCursor(Qt.PointingHandCursor)
        reg_btn.setStyleSheet(f"color: {C['accent']}; background: transparent; border: none; font-weight: bold;")
        reg_btn.clicked.connect(self.go_to_register.emit)
        row.addWidget(hint); row.addWidget(reg_btn)
        return row

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI Semibold", 9))
        lbl.setStyleSheet(f"color: {C['text']}; background: transparent;")
        return lbl

    def _on_login(self):
        username = self._username_input.text().strip()
        password = self._password_input.text()
        
        if not username or not password:
            self._error_lbl.setText("⚠ Vui lòng nhập đầy đủ tài khoản và mật khẩu.")
            self._error_lbl.setVisible(True)
            return
            
        self._error_lbl.setVisible(False)
        self.login_requested.emit(username, password) 

    def show_error(self, message: str):
        self._error_lbl.setText(message)
        self._error_lbl.setVisible(True)


# =====================================================================
# CỘT PHẢI: CLASS 2 - ĐĂNG KÝ
# =====================================================================
class RegisterPanel(QWidget):
    go_back = pyqtSignal()
    register_requested = pyqtSignal(dict) 

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        card_layout, _ = create_floating_card(self, width=540)
        card_layout.setContentsMargins(40, 30, 40, 30)
        card_layout.setSpacing(8)
        
        title = QLabel("Tạo tài khoản")
        title.setFont(QFont("Segoe UI Black", 18))
        title.setStyleSheet(f"color: {C['text']}; background: transparent;")
        card_layout.addWidget(title)
        
        card_layout.addWidget(self._make_section_header("1", "THÔNG TIN TÀI KHOẢN"))
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("e.g. sinhvien@vku.udn.vn")
        self.email_input.setFixedHeight(45) 
        card_layout.addWidget(self._field_label("Địa chỉ Email"))
        card_layout.addWidget(self.email_input)
        
        pwd_container = QWidget()
        pwd_container.setStyleSheet(".QWidget { background: transparent; }")
        pwd_row = QHBoxLayout(pwd_container)
        pwd_row.setContentsMargins(0, 0, 0, 0)
        
        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("Tối thiểu 6 ký tự")
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.pwd_input.setFixedHeight(45) 
        
        self.confirm_pwd_input = QLineEdit()
        self.confirm_pwd_input.setPlaceholderText("Nhập lại mật khẩu")
        self.confirm_pwd_input.setEchoMode(QLineEdit.Password)
        self.confirm_pwd_input.setFixedHeight(45) 
        
        pwd_col1 = QVBoxLayout(); pwd_col1.addWidget(self._field_label("Mật khẩu")); pwd_col1.addWidget(self.pwd_input)
        pwd_col2 = QVBoxLayout(); pwd_col2.addWidget(self._field_label("Xác nhận mật khẩu")); pwd_col2.addWidget(self.confirm_pwd_input)
        pwd_row.addLayout(pwd_col1); pwd_row.addLayout(pwd_col2)
        card_layout.addWidget(pwd_container)
        
        card_layout.addSpacing(5)
        card_layout.addWidget(self._make_section_header("2", "THÔNG TIN CÁ NHÂN"))
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nhập họ và tên đầy đủ")
        self.name_input.setFixedHeight(45) 
        card_layout.addWidget(self._field_label("Họ và Tên"))
        card_layout.addWidget(self.name_input)
        
        details_container = QWidget()
        details_container.setStyleSheet(".QWidget { background: transparent; }")
        details_row = QHBoxLayout(details_container)
        details_row.setContentsMargins(0, 0, 0, 0)
        
        self.dob_input = QDateEdit()
        self.dob_input.setCalendarPopup(True) 
        self.dob_input.setDate(QDate(2000, 1, 1))
        self.dob_input.setDisplayFormat("dd/MM/yyyy")
        self.dob_input.setFixedHeight(45) 
        
        self.gender_input = QComboBox()
        self.gender_input.addItems(["Nam", "Nữ", "Khác"])
        self.gender_input.setFixedHeight(45) 
        
        dob_col = QVBoxLayout(); dob_col.addWidget(self._field_label("Ngày sinh")); dob_col.addWidget(self.dob_input)
        gen_col = QVBoxLayout(); gen_col.addWidget(self._field_label("Giới tính")); gen_col.addWidget(self.gender_input)
        details_row.addLayout(dob_col); details_row.addLayout(gen_col)
        card_layout.addWidget(details_container)
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("e.g. 0901234567")
        self.phone_input.setFixedHeight(45) 
        card_layout.addWidget(self._field_label("Số điện thoại"))
        card_layout.addWidget(self.phone_input)
        
        card_layout.addSpacing(15)
        self.reg_btn = GoldButton("HOÀN TẤT ĐĂNG KÝ →", height=51) 
        self.reg_btn.setStyleSheet(GOLD_BTN_STYLE)
        self.reg_btn.clicked.connect(self._on_register)
        card_layout.addWidget(self.reg_btn)
        
        back_btn = QPushButton("← Trở về Đăng nhập")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet(f"QPushButton {{ color: {C['muted']}; background: transparent; border: none; text-decoration: underline; padding-top: 5px;}} QPushButton:hover {{ color: {C['accent']}; }}")
        back_btn.clicked.connect(self.go_back.emit)
        card_layout.addWidget(back_btn, alignment=Qt.AlignCenter)

    def _make_section_header(self, step: str, title: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 10, 0, 0)
        lbl_step = QLabel(step)
        lbl_step.setFixedSize(22, 22)
        lbl_step.setAlignment(Qt.AlignCenter)
        lbl_step.setStyleSheet(f"background: {C['brand_top']}; color: white; border-radius: 11px; font-weight: bold;")
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_title.setStyleSheet(f"color: {C['brand_top']}; background: transparent;")
        lay.addWidget(lbl_step); lay.addWidget(lbl_title); lay.addStretch()
        return w

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI Semibold", 8))
        lbl.setStyleSheet(f"color: {C['text']}; background: transparent;")
        return lbl

    def _on_register(self):
        data = {
            "email": self.email_input.text().strip(),
            "password": self.pwd_input.text(),
            "confirm_password": self.confirm_pwd_input.text(),
            "full_name": self.name_input.text().strip(),
            "dob": self.dob_input.date().toString("yyyy-MM-dd"),
            "gender": self.gender_input.currentText(),
            "phone": self.phone_input.text().strip()
        }
        self.register_requested.emit(data)


# =====================================================================
# CỘT PHẢI: CLASS 3 - QUÊN MẬT KHẨU
# =====================================================================
class ForgotPasswordPanel(QWidget):
    go_back = pyqtSignal()
    send_otp_requested = pyqtSignal(str)
    update_pwd_requested = pyqtSignal(str, str, str,str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        card_layout, _ = create_floating_card(self, width=500)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(10)
        
        title = QLabel("Quên Mật Khẩu")
        title.setFont(QFont("Segoe UI Black", 18))
        title.setStyleSheet(f"color: {C['text']}; background: transparent;")
        card_layout.addWidget(title)
        
        card_layout.addWidget(self._make_section_header("1", "EMAIL TÀI KHOẢN"))
        
        email_container = QWidget()
        email_container.setStyleSheet(".QWidget { background: transparent; }")
        email_row = QHBoxLayout(email_container)
        email_row.setContentsMargins(0, 0, 0, 0)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Nhập email đã đăng ký")
        self.email_input.setFixedHeight(45) 
        self.otp_btn = QPushButton("Gửi OTP")
        self.otp_btn.setFixedSize(100, 45) 
        self.otp_btn.setCursor(Qt.PointingHandCursor)
        self.otp_btn.setStyleSheet(f"background: {C['accent']}; color: white; border-radius: 16px; font-weight: bold;")
        self.otp_btn.clicked.connect(self._on_send_otp)
        email_row.addWidget(self.email_input); email_row.addWidget(self.otp_btn)
        
        card_layout.addWidget(self._field_label("Địa chỉ Email"))
        card_layout.addWidget(email_container)
        
        card_layout.addWidget(self._make_section_header("2", "XÁC THỰC MÃ"))
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("Nhập mã OTP 6 số")
        self.otp_input.setFixedHeight(45) 
        card_layout.addWidget(self._field_label("Mã OTP"))
        card_layout.addWidget(self.otp_input)
        
        card_layout.addWidget(self._make_section_header("3", "MẬT KHẨU MỚI"))
        
        pwd_container = QWidget()
        pwd_container.setStyleSheet(".QWidget { background: transparent; }")
        pwd_row = QHBoxLayout(pwd_container)
        pwd_row.setContentsMargins(0, 0, 0, 0)
        
        self.new_pwd = QLineEdit()
        self.new_pwd.setPlaceholderText("Tối thiểu 6 ký tự")
        self.new_pwd.setEchoMode(QLineEdit.Password)
        self.new_pwd.setFixedHeight(45) 
        
        self.conf_pwd = QLineEdit()
        self.conf_pwd.setPlaceholderText("Nhập lại mật khẩu mới")
        self.conf_pwd.setEchoMode(QLineEdit.Password)
        self.conf_pwd.setFixedHeight(45) 
        pwd_col1 = QVBoxLayout(); pwd_col1.addWidget(self._field_label("Mật khẩu mới")); pwd_col1.addWidget(self.new_pwd)
        pwd_col2 = QVBoxLayout(); pwd_col2.addWidget(self._field_label("Xác nhận mật khẩu")); pwd_col2.addWidget(self.conf_pwd)
        pwd_row.addLayout(pwd_col1); pwd_row.addLayout(pwd_col2)
        card_layout.addWidget(pwd_container)
        
        card_layout.addSpacing(15)
        self.update_btn = GoldButton("CẬP NHẬT MẬT KHẨU →", height=51) 
        self.update_btn.setStyleSheet(GOLD_BTN_STYLE)
        self.update_btn.clicked.connect(self._on_update_pwd)
        card_layout.addWidget(self.update_btn)
        
        back_btn = QPushButton("← Trở về Đăng nhập")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet(f"QPushButton {{ color: {C['muted']}; background: transparent; border: none; text-decoration: underline; padding-top: 10px;}} QPushButton:hover {{ color: {C['accent']}; }}")
        back_btn.clicked.connect(self.go_back.emit)
        card_layout.addWidget(back_btn, alignment=Qt.AlignCenter)

    def _make_section_header(self, step: str, title: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 10, 0, 0)
        lbl_step = QLabel(step)
        lbl_step.setFixedSize(22, 22)
        lbl_step.setAlignment(Qt.AlignCenter)
        lbl_step.setStyleSheet(f"background: {C['brand_top']}; color: white; border-radius: 11px; font-weight: bold;")
        lbl_title = QLabel(title)
        lbl_title.setFont(QFont("Segoe UI", 9, QFont.Bold))
        lbl_title.setStyleSheet(f"color: {C['brand_top']}; background: transparent;")
        lay.addWidget(lbl_step); lay.addWidget(lbl_title); lay.addStretch()
        return w

    def _field_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI Semibold", 8))
        lbl.setStyleSheet(f"color: {C['text']}; background: transparent;")
        return lbl

    def _on_send_otp(self):
        email = self.email_input.text().strip()
        if email:
            if email:
                self.otp_btn.setText("Đang gửi...")
                self.otp_btn.setEnabled(False)
                QApplication.processEvents()

                self.send_otp_requested.emit(email)

                self.otp_btn.setText("Gửi OTP")
                self.otp_btn.setEnabled(True)

    def _on_update_pwd(self):
        email = self.email_input.text().strip()
        otp = self.otp_input.text().strip()
        pwd = self.new_pwd.text()
        conf_pwd = self.conf_pwd.text()
    
        self.update_pwd_requested.emit(email, otp, pwd, conf_pwd)

# =====================================================================
# CỬA SỔ CHÍNH QUẢN LÝ
# =====================================================================
class LoginScreen(QWidget):
    login_requested = pyqtSignal(str, str)
    register_requested = pyqtSignal(dict)
    send_otp_requested = pyqtSignal(str)
    update_pwd_requested = pyqtSignal(str, str, str, str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._init_window()
        self._build_ui()

    def _init_window(self):
        self.setWindowTitle("Xác thực – Vaultex Tracker")
        self.setFixedSize(1100, 700)
        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width() - 1100) // 2, (screen.height() - 700) // 2)

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._brand = BrandPanel()
        root.addWidget(self._brand, 45)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background: {C['bg']};")
        
        self._login_panel = LoginPanel()
        self._register_panel = RegisterPanel()
        self._forgot_panel = ForgotPasswordPanel()

        self._stack.addWidget(self._login_panel)      
        self._stack.addWidget(self._register_panel)   
        self._stack.addWidget(self._forgot_panel)     

        self._login_panel.go_to_register.connect(lambda: self._stack.setCurrentIndex(1))
        self._login_panel.go_to_forgot_password.connect(lambda: self._stack.setCurrentIndex(2))
        self._register_panel.go_back.connect(lambda: self._stack.setCurrentIndex(0))
        self._forgot_panel.go_back.connect(lambda: self._stack.setCurrentIndex(0))

        self._login_panel.login_requested.connect(self.login_requested)
        self._register_panel.register_requested.connect(self.register_requested)
        self._forgot_panel.send_otp_requested.connect(self.send_otp_requested)
        self._forgot_panel.update_pwd_requested.connect(self.update_pwd_requested)

        root.addWidget(self._stack, 55)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()
        super().keyPressEvent(event)