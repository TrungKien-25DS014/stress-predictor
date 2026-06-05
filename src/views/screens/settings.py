from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QComboBox,
    QSizePolicy, QSpacerItem,
    QDateEdit,
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPaintEvent,
    QBrush, QPen,
)

from src.core.config import C
from src.views.components.widgets import GlowLineEdit, GoldButton, CustomMessageBox
from src.core.config import C, CURRENT_THEME
_RADIUS_CARD = 12

def _make_card(parent: QWidget | None = None) -> QFrame:
    '''Tạo một thẻ QFrame cơ bản làm container với nền trắng và viền chuẩn.'''
    card = QFrame(parent)
    card.setObjectName("settings_card")
    card.setStyleSheet(f"""
        QFrame#settings_card {{
            background-color : {C['white']};
            border           : 1px solid {C['card_border']};
            border-radius    : {_RADIUS_CARD}px;
        }}
    """)
    return card

def _make_section_title(text: str, emoji: str = "") -> QLabel:
    '''Tạo tiêu đề chính cho từng khu vực cài đặt.'''
    prefix = f"{emoji}  " if emoji else ""
    lbl = QLabel(f"{prefix}{text}")
    lbl.setFont(QFont("Segoe UI Semibold", 11))
    lbl.setStyleSheet(f"color: {C['text_primary']}; background: transparent;")
    return lbl

def _make_subsection_label(text: str) -> QLabel:
    '''Tạo nhãn phụ cho các phần tử con trong cài đặt.'''
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI Semibold", 9))
    lbl.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")
    return lbl

def _make_field_label(text: str) -> QLabel:
    '''Tạo nhãn chỉ định thông tin cho các trường nhập liệu.'''
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI Semibold", 9))
    lbl.setStyleSheet(f"color: {C['text_primary']}; background: transparent;")
    return lbl

def _make_divider_line() -> QFrame:
    '''Tạo đường kẻ ngang để phân chia nội dung.'''
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFixedHeight(1)
    line.setStyleSheet(f"background-color: {C['divider']}; border: none;")
    return line

def _field_col(label_text: str, widget: QWidget) -> QVBoxLayout:
    '''Tạo layout cột bao gồm nhãn và widget nhập liệu bên dưới.'''
    col = QVBoxLayout()
    col.setContentsMargins(0, 0, 0, 0)
    col.setSpacing(4)
    col.addWidget(_make_field_label(label_text))
    col.addWidget(widget)
    return col


class AvatarWidget(QWidget):
    '''
    Widget hiển thị ảnh đại diện dạng chữ cái đầu (Avatar).
    Tự động vẽ thành hình tròn với màu accent mặc định.
    '''
    def __init__(self, initials: str = "U", size: int = 80,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self._initials = initials.upper()[:2]
        self._size = size
        self.setFixedSize(size, size)

    def paintEvent(self, event: QPaintEvent):
        '''Vẽ ảnh đại diện tròn khi widget được yêu cầu cập nhật.'''
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(QColor(C['accent'])))
        p.setPen(QPen(QColor(C['accent_dark']), 2))
        p.drawEllipse(1, 1, self._size - 2, self._size - 2)
        font = QFont("Segoe UI Semibold", int(self._size * 0.28))
        p.setFont(font)
        p.setPen(QPen(QColor(C['white'])))
        p.drawText(self.rect(), Qt.AlignCenter, self._initials)
        p.end()


class SettingsScreen(QWidget):
    '''
    Giao diện màn hình Cài Đặt (Settings).
    Quản lý thông tin cá nhân, cấu hình mật khẩu và giao diện hiển thị.
    '''
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("SettingsScreen")
        self._build_ui()
        self._apply_page_style()

    def _build_ui(self):
        '''Xây dựng toàn bộ layout và thành phần giao diện.'''
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._scroll_area = QScrollArea()
        self._scroll_area.setObjectName("settings_scroll")
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll_area.setFrameShape(QFrame.NoFrame)
        self._scroll_area.setStyleSheet(f"""
            QScrollArea#settings_scroll {{
                background-color: {C['bg_main']};
                border: none;
            }}
            QScrollBar:vertical {{
                background: {C['bg_main']}; width: 8px; border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {C['card_border']}; border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {C['text_muted']}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

        self._scroll_content = QWidget()
        self._scroll_content.setObjectName("scroll_content")
        self._scroll_content.setStyleSheet(f"background-color: {C['bg_main']};")

        self._main_layout = QVBoxLayout(self._scroll_content)
        self._main_layout.setContentsMargins(20, 20, 20, 20)
        self._main_layout.setSpacing(20)

        self._build_page_header()
        self._build_profile_card()
        self._build_security_card()
        self._build_interface_card()
        self._build_bottom_actions()

        self._main_layout.addSpacerItem(QSpacerItem(0, 12, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self._scroll_area.setWidget(self._scroll_content)
        root.addWidget(self._scroll_area)

    def _build_page_header(self):
        '''Tạo tiêu đề lớn ở đầu trang Cài đặt.'''
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(12)

        icon_badge = QLabel("⚙️")
        icon_badge.setFont(QFont("Segoe UI", 18))
        icon_badge.setFixedSize(44, 44)
        icon_badge.setAlignment(Qt.AlignCenter)
        icon_badge.setStyleSheet(f"""
            background-color: {C['accent_light']};
            border-radius: 10px;
            border: 1px solid {C['accent']};
        """)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(2)

        page_title = QLabel("Cài đặt")
        page_title.setFont(QFont("Segoe UI Semibold", 15))
        page_title.setStyleSheet(f"color: {C['text_primary']}; background: transparent;")

        page_sub = QLabel("Quản lý thông tin cá nhân, bảo mật và giao diện của bạn.")
        page_sub.setFont(QFont("Segoe UI", 9))
        page_sub.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        header_row.addWidget(icon_badge)
        header_row.addLayout(title_col)
        header_row.addStretch()
        self._main_layout.addLayout(header_row)

    def _build_profile_card(self):
        '''Xây dựng thẻ thông tin cá nhân gồm Avatar và thông tin liên hệ.'''
        card = _make_card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(16)

        card_layout.addWidget(_make_section_title("Thông tin cá nhân", "👤"))
        card_layout.addWidget(_make_divider_line())

        avatar_row = QHBoxLayout()
        avatar_row.setContentsMargins(0, 4, 0, 4)
        avatar_row.setSpacing(20)

        avatar_col = QVBoxLayout()
        avatar_col.setContentsMargins(0, 0, 0, 0)
        avatar_col.setSpacing(8)
        avatar_col.setAlignment(Qt.AlignHCenter)

        self._avatar_widget = AvatarWidget(initials="U", size=80)
        avatar_col.addWidget(self._avatar_widget, alignment=Qt.AlignHCenter)

        self._btn_change_avatar = QPushButton("🖼  Thay đổi ảnh đại diện")
        self._btn_change_avatar.setFont(QFont("Segoe UI", 9))
        self._btn_change_avatar.setCursor(Qt.PointingHandCursor)
        self._btn_change_avatar.setFixedHeight(32)
        self._btn_change_avatar.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {C['accent']};
                border: 1px solid {C['accent']};
                border-radius: 6px;
                padding: 0px 12px;
            }}
            QPushButton:hover {{ background-color: {C['accent_light']}; }}
        """)
        self._btn_change_avatar.clicked.connect(self._on_change_avatar)
        avatar_col.addWidget(self._btn_change_avatar, alignment=Qt.AlignHCenter)

        hint_lbl = QLabel("JPG, PNG – tối đa 2MB")
        hint_lbl.setFont(QFont("Segoe UI", 8))
        hint_lbl.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")
        hint_lbl.setAlignment(Qt.AlignHCenter)
        avatar_col.addWidget(hint_lbl)
        avatar_row.addLayout(avatar_col)

        vline = QFrame()
        vline.setFrameShape(QFrame.VLine)
        vline.setFixedWidth(1)
        vline.setStyleSheet(f"background-color: {C['divider']}; border: none;")
        avatar_row.addWidget(vline)

        form_col = QVBoxLayout()
        form_col.setContentsMargins(4, 0, 0, 0)
        form_col.setSpacing(12)

        self._input_name = GlowLineEdit("Nhập họ và tên...")
        form_col.addLayout(_field_col("Họ và tên", self._input_name))

        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(16)

        self._input_email = GlowLineEdit("Địa chỉ email...")
        self._input_phone = GlowLineEdit("Nhập số điện thoại...")

        row2.addLayout(_field_col("Email (Không thể thay đổi)", self._input_email))
        row2.addLayout(_field_col("Số điện thoại", self._input_phone))
        form_col.addLayout(row2)

        row3 = QHBoxLayout()
        row3.setContentsMargins(0, 0, 0, 0)
        row3.setSpacing(16)

        self._combo_gender = QComboBox()
        self._combo_gender.addItems(["Nam", "Nữ", "Khác", "Không muốn tiết lộ"])
        self._combo_gender.setFixedHeight(36)
        self._combo_gender.setCursor(Qt.PointingHandCursor)
        self._combo_gender.setStyleSheet(f"""
            QComboBox {{
                background-color : {C['white']};
                border           : 1.5px solid {C['card_border']};
                border-radius    : 8px;
                padding          : 0px 12px;
                color            : {C['text_primary']};
            }}
            QComboBox:focus {{
                border-color     : {C['accent']};
                background-color : {C['accent_light']};
            }}
            QComboBox::drop-down {{ border: none; width: 28px; }}
            QComboBox::down-arrow {{ image: none; width: 0; }}
        """)

        self._date_dob = QDateEdit()
        self._date_dob.setCalendarPopup(True)
        self._date_dob.setDisplayFormat("dd/MM/yyyy")
        self._date_dob.setFixedHeight(36)
        self._date_dob.setCursor(Qt.PointingHandCursor)
        self._date_dob.setStyleSheet(f"""
            QDateEdit {{
                background-color : {C['white']};
                border           : 1.5px solid {C['card_border']};
                border-radius    : 8px;
                padding          : 0px 12px;
                color            : {C['text_primary']};
            }}
            QDateEdit:focus {{
                border-color     : {C['accent']};
                background-color : {C['accent_light']};
            }}
            QDateEdit::drop-down {{ border: none; width: 28px; }}
            QDateEdit::down-arrow {{ image: none; }}
        """)

        row3.addLayout(_field_col("Giới tính", self._combo_gender))
        row3.addLayout(_field_col("Ngày sinh", self._date_dob))
        form_col.addLayout(row3)

        form_col.addStretch()
        avatar_row.addLayout(form_col, stretch=1)
        card_layout.addLayout(avatar_row)
        self._main_layout.addWidget(card)

    def _build_security_card(self):
        '''Xây dựng thẻ bảo mật, quản lý tính năng đổi mật khẩu an toàn.'''
        self._security_card = _make_card()
        card_layout = QVBoxLayout(self._security_card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(16)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(12)

        header_row.addWidget(_make_section_title("Bảo mật", "🔒"))
        header_row.addStretch()

        self._btn_toggle_pw = QPushButton("🔑  Đổi mật khẩu")
        self._btn_toggle_pw.setFont(QFont("Segoe UI Semibold", 9))
        self._btn_toggle_pw.setCursor(Qt.PointingHandCursor)
        self._btn_toggle_pw.setFixedHeight(34)
        self._btn_toggle_pw.setMinimumWidth(140)
        self._btn_toggle_pw.setCheckable(True)
        self._btn_toggle_pw.setChecked(False)
        self._btn_toggle_pw.setStyleSheet(f"""
            QPushButton {{
                background-color : transparent;
                color            : {C['accent']};
                border           : 1.5px solid {C['accent']};
                border-radius    : 8px;
                padding          : 0px 14px;
            }}
            QPushButton:hover {{ background-color: {C['accent_light']}; }}
            QPushButton:checked {{ background-color: {C['accent']}; color: {C['white']}; border-color: {C['accent']}; }}
        """)
        self._btn_toggle_pw.toggled.connect(self._on_toggle_password_form)
        header_row.addWidget(self._btn_toggle_pw)
        card_layout.addLayout(header_row)

        self._pw_form_widget = QWidget()
        self._pw_form_widget.setStyleSheet("background: transparent;")
        pw_layout = QVBoxLayout(self._pw_form_widget)
        pw_layout.setContentsMargins(0, 0, 0, 0)
        pw_layout.setSpacing(12)

        pw_layout.addWidget(_make_divider_line())

        self._input_cur_pw = GlowLineEdit("Nhập mật khẩu hiện tại...")
        self._input_cur_pw.setEchoMode(self._input_cur_pw.Password)
        pw_layout.addLayout(_field_col("Mật khẩu hiện tại", self._input_cur_pw))

        new_pw_row = QHBoxLayout()
        new_pw_row.setContentsMargins(0, 0, 0, 0)
        new_pw_row.setSpacing(16)

        self._input_new_pw = GlowLineEdit("Nhập mật khẩu mới...")
        self._input_new_pw.setEchoMode(self._input_new_pw.Password)

        self._input_confirm_pw = GlowLineEdit("Nhập lại mật khẩu mới...")
        self._input_confirm_pw.setEchoMode(self._input_confirm_pw.Password)

        new_pw_row.addLayout(_field_col("Mật khẩu mới", self._input_new_pw))
        new_pw_row.addLayout(_field_col("Xác nhận mật khẩu mới", self._input_confirm_pw))
        pw_layout.addLayout(new_pw_row)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 4, 0, 0)
        self._btn_change_pw = QPushButton("✔  Xác nhận đổi mật khẩu")
        self._btn_change_pw.setFont(QFont("Segoe UI Semibold", 10))
        self._btn_change_pw.setCursor(Qt.PointingHandCursor)
        self._btn_change_pw.setFixedHeight(40)
        self._btn_change_pw.setMinimumWidth(200)
        self._btn_change_pw.setStyleSheet(f"""
            QPushButton {{
                background-color : {C['accent']};
                color            : {C['white']};
                border           : none;
                border-radius    : 8px;
                padding          : 0px 20px;
            }}
            QPushButton:hover {{ background-color: {C['accent_hover']}; }}
        """)
        btn_row.addStretch()
        btn_row.addWidget(self._btn_change_pw)
        pw_layout.addLayout(btn_row)

        self._pw_form_widget.setVisible(False)
        card_layout.addWidget(self._pw_form_widget)

        self._main_layout.addWidget(self._security_card)

    def _build_interface_card(self):
        '''Xây dựng thẻ cấu hình giao diện, cho phép chuyển đổi chế độ sáng / tối.'''
        card = _make_card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(16)

        card_layout.addWidget(_make_section_title("Cấu hình giao diện", "🎨"))
        card_layout.addWidget(_make_divider_line())
        card_layout.addWidget(_make_subsection_label("Chế độ hiển thị"))

        radio_row = QHBoxLayout()
        radio_row.setContentsMargins(0, 4, 0, 4)
        radio_row.setSpacing(24)

        self._radio_group = QButtonGroup(self)

        _radio_style = lambda accent: f"""
            QRadioButton {{ color: {C['text_primary']}; background: transparent; spacing: 8px; }}
            QRadioButton::indicator {{
                width: 18px; height: 18px; border-radius: 9px;
                border: 2px solid {C['card_border']}; background: {C['white']};
            }}
            QRadioButton::indicator:checked {{ background: {accent}; border-color: {accent}; }}
        """

        self._radio_light = QRadioButton("☀️   Giao diện sáng  (Clinical Light)")
        self._radio_light.setFont(QFont("Segoe UI", 10))
        self._radio_light.setChecked(True)
        self._radio_light.setCursor(Qt.PointingHandCursor)
        self._radio_light.setStyleSheet(_radio_style(C['accent']))
        self._radio_group.addButton(self._radio_light, 0)

        self._radio_dark = QRadioButton("🌙   Giao diện tối  (Dark Mode)")
        self._radio_dark.setFont(QFont("Segoe UI", 10))
        self._radio_dark.setCursor(Qt.PointingHandCursor)
        self._radio_dark.setStyleSheet(_radio_style(C['text_muted']))
        self._radio_group.addButton(self._radio_dark, 1)

        from src.core.config import CURRENT_THEME
        if CURRENT_THEME == "dark":
            self._radio_dark.setChecked(True)
        else:
            self._radio_light.setChecked(True)

        radio_row.addWidget(self._radio_light)
        radio_row.addWidget(self._radio_dark)
        radio_row.addStretch()
        card_layout.addLayout(radio_row)

        note_frame = QFrame()
        note_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {C.get('warning_bg', '#FFF9E6')};
                border: 1px solid {C['warning']};
                border-radius: 8px;
            }}
        """)
        note_layout = QHBoxLayout(note_frame)
        note_layout.setContentsMargins(12, 8, 12, 8)
        note_layout.setSpacing(8)

        note_icon = QLabel("💡")
        note_icon.setFont(QFont("Segoe UI", 10))
        note_icon.setStyleSheet("background: transparent;")

        note_text = QLabel("Chức năng Dark Mode hiện đang được phát triển. Thay đổi sẽ được áp dụng khi khởi động lại ứng dụng.")
        note_text.setFont(QFont("Segoe UI", 8))
        note_text.setWordWrap(True)
        note_text.setStyleSheet(f"color: {C.get('warning_text', '#856404')}; background: transparent;")

        note_layout.addWidget(note_icon, alignment=Qt.AlignTop)
        note_layout.addWidget(note_text, 1)
        card_layout.addWidget(note_frame)

        self._main_layout.addWidget(card)

    def _build_bottom_actions(self):
        '''Tạo dải nút hành động (Xóa form, Lưu cài đặt) ở dưới cùng.'''
        actions_row = QHBoxLayout()
        actions_row.setContentsMargins(0, 4, 0, 0)
        actions_row.setSpacing(12)

        self._btn_reset = QPushButton("↺  Xóa form")
        self._btn_reset.setFont(QFont("Segoe UI", 10))
        self._btn_reset.setCursor(Qt.PointingHandCursor)
        self._btn_reset.setFixedHeight(44)
        self._btn_reset.setMinimumWidth(160)
        self._btn_reset.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {C['text_muted']};
                border: 1.5px solid {C['card_border']};
                border-radius: 8px;
            }}
            QPushButton:hover {{ 
                background-color: {C.get('btn_outline_bg', '#F1F3F5')}; 
                color: {C['text_primary']}; 
                border-color: {C.get('btn_outline_border', '#ADB5BD')}; 
            }}
        """)
        self._btn_reset.clicked.connect(self._on_reset)

        self._btn_save = GoldButton(text="💾  Lưu cài đặt", width=160, height=44)

        actions_row.addStretch()
        actions_row.addWidget(self._btn_reset)
        actions_row.addWidget(self._btn_save)
        self._main_layout.addLayout(actions_row)

    def _apply_page_style(self):
        '''Đồng bộ màu nền chủ đạo cho toàn trang Cài đặt.'''
        self.setStyleSheet(f"QWidget#SettingsScreen {{ background-color: {C['bg_main']}; }}")

    def _on_toggle_password_form(self, checked: bool):
        '''Xử lý trạng thái hiển thị của khung nhập mật khẩu.'''
        self._pw_form_widget.setVisible(checked)
        self._btn_toggle_pw.setText("✕  Đóng" if checked else "🔑  Đổi mật khẩu")
        if not checked:
            self._input_cur_pw.clear()
            self._input_new_pw.clear()
            self._input_confirm_pw.clear()

    def _on_reset(self):
        '''Làm mới toàn bộ thông tin đang chỉnh sửa trên các khung nhập liệu.'''
        self._input_name.clear()
        self._input_phone.clear()
        self._combo_gender.setCurrentIndex(0)

    def _on_change_avatar(self):
        '''Kích hoạt chức năng đổi ảnh đại diện (Hiện tại đang phát triển).'''
        CustomMessageBox.show_warning(self, "Thông báo", "Chức năng tải ảnh đại diện đang được phát triển.")

    def _show_warning(self, message: str):
        '''Hiển thị hộp thoại cảnh báo.'''
        CustomMessageBox.show_warning(self, "Cảnh báo", message)

    def load_profile(self, name: str, email: str = "", phone: str = "", gender: str = "Nam", dob: QDate = None):
        '''Nạp thông tin người dùng thực tế vào các khung nhập liệu.'''
        self._input_name.setText(name)
        self._input_email.setText(email)
        self._input_phone.setText(phone)
        
        idx = self._combo_gender.findText(gender)
        if idx >= 0:
            self._combo_gender.setCurrentIndex(idx)
        
        if dob:
            self._date_dob.setDate(dob)
            
        initials = "".join(w[0] for w in name.split() if w)[:2].upper() if name else "U"
        self._avatar_widget._initials = initials
        self._avatar_widget.update()

    def get_settings_data(self) -> dict:
        '''Đóng gói các thay đổi của người dùng trả về dạng từ điển để xử lý lưu.'''
        return {
            "name":   self._input_name.text().strip(),
            "phone":  self._input_phone.text().strip(),
            "gender": self._combo_gender.currentText(),
            "dob":    self._date_dob.date().toString("yyyy-MM-dd"),
            "theme":  "light" if self._radio_group.checkedId() == 0 else "dark",
        }