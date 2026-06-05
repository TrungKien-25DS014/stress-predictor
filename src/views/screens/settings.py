"""
src/views/screens/settings.py
------------------------------
Màn hình Cài đặt (Settings) – phong cách Clinical Light.

Gồm 3 phân khu:
  1. Thông tin cá nhân  (Profile Settings) – bao gồm giới tính, ngày sinh
  2. Bảo mật           (Đổi mật khẩu – ẩn/hiện theo nút toggle)
  3. Giao diện hiển thị (Interface Settings)

Author : Senior PyQt5 Engineer
"""

from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QScrollArea, QFrame, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QComboBox,
    QMessageBox, QSizePolicy, QSpacerItem,
    QDateEdit,
)
from PyQt5.QtCore import Qt, QSize, QDate
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPaintEvent,
    QBrush, QPen,
)

from src.views.components.widgets import GlowLineEdit, GoldButton
from src.core.config import COLORS, FONTS

# ---------------------------------------------------------------------------
# Design Tokens
# ---------------------------------------------------------------------------
_BG_PAGE      = "#F8F9FA"
_BG_CARD      = "#FFFFFF"
_BORDER_CARD  = "#E5E5E5"
_ACCENT       = "#007AFF"
_ACCENT_LIGHT = "#E8F3FF"
_GOLD         = "#D4AF37"
_TEXT_PRIMARY = "#1A2233"
_TEXT_MUTED   = "#6C757D"
_RADIUS_CARD  = 12
_DIVIDER      = "#E2E8F0"
_WARN_BG      = "#FFF9E6"
_WARN_BORDER  = "#FFC107"


# ===========================================================================
# Helpers
# ===========================================================================
def _make_card(parent: QWidget | None = None) -> QFrame:
    card = QFrame(parent)
    card.setObjectName("settings_card")
    card.setStyleSheet(f"""
        QFrame#settings_card {{
            background-color : {_BG_CARD};
            border           : 1px solid {_BORDER_CARD};
            border-radius    : {_RADIUS_CARD}px;
        }}
    """)
    return card


def _make_section_title(text: str, emoji: str = "") -> QLabel:
    prefix = f"{emoji}  " if emoji else ""
    lbl = QLabel(f"{prefix}{text}")
    lbl.setFont(QFont("Segoe UI Semibold", 11))
    lbl.setStyleSheet(f"color: {_TEXT_PRIMARY}; background: transparent;")
    return lbl


def _make_subsection_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI Semibold", 9))
    lbl.setStyleSheet(f"color: {_TEXT_MUTED}; background: transparent;")
    return lbl


def _make_field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setFont(QFont("Segoe UI Semibold", 9))
    lbl.setStyleSheet(f"color: {_TEXT_PRIMARY}; background: transparent;")
    return lbl


def _make_divider_line() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFixedHeight(1)
    line.setStyleSheet(f"background-color: {_DIVIDER}; border: none;")
    return line


def _field_col(label_text: str, widget: QWidget) -> QVBoxLayout:
    """Trả về QVBoxLayout gồm label + widget."""
    col = QVBoxLayout()
    col.setContentsMargins(0, 0, 0, 0)
    col.setSpacing(4)
    col.addWidget(_make_field_label(label_text))
    col.addWidget(widget)
    return col


# ===========================================================================
# AvatarWidget
# ===========================================================================
class AvatarWidget(QWidget):
    def __init__(self, initials: str = "NB", size: int = 80,
                 parent: QWidget | None = None):
        super().__init__(parent)
        self._initials = initials.upper()[:2]
        self._size = size
        self.setFixedSize(size, size)

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(QBrush(QColor(_ACCENT)))
        p.setPen(QPen(QColor("#0055CC"), 2))
        p.drawEllipse(1, 1, self._size - 2, self._size - 2)
        font = QFont("Segoe UI Semibold", int(self._size * 0.28))
        p.setFont(font)
        p.setPen(QPen(QColor("#FFFFFF")))
        p.drawText(self.rect(), Qt.AlignCenter, self._initials)
        p.end()


# ===========================================================================
# SettingsScreen
# ===========================================================================
class SettingsScreen(QWidget):

    _MOCK_NAME  = "Nguyễn Hữu Bảo"
    _MOCK_EMAIL = "bao.nguyen@example.com"
    _MOCK_PHONE = "0912 345 678"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("SettingsScreen")
        self._build_ui()
        self._apply_page_style()

    # =========================================================================
    # BUILD UI
    # =========================================================================
    def _build_ui(self):
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
                background-color: {_BG_PAGE};
                border: none;
            }}
            QScrollBar:vertical {{
                background: {_BG_PAGE}; width: 8px; border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: #CED4DA; border-radius: 4px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {_TEXT_MUTED}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

        self._scroll_content = QWidget()
        self._scroll_content.setObjectName("scroll_content")
        self._scroll_content.setStyleSheet(f"background-color: {_BG_PAGE};")

        self._main_layout = QVBoxLayout(self._scroll_content)
        self._main_layout.setContentsMargins(20, 20, 20, 20)
        self._main_layout.setSpacing(20)

        self._build_page_header()
        self._build_profile_card()
        self._build_security_card()
        self._build_interface_card()
        self._build_bottom_actions()

        self._main_layout.addSpacerItem(
            QSpacerItem(0, 12, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
        self._scroll_area.setWidget(self._scroll_content)
        root.addWidget(self._scroll_area)

    # ── 0. Page Header ────────────────────────────────────────────────
    def _build_page_header(self):
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(12)

        icon_badge = QLabel("⚙️")
        icon_badge.setFont(QFont("Segoe UI", 18))
        icon_badge.setFixedSize(44, 44)
        icon_badge.setAlignment(Qt.AlignCenter)
        icon_badge.setStyleSheet(f"""
            background-color: {_ACCENT_LIGHT};
            border-radius: 10px;
            border: 1px solid {_ACCENT};
        """)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(2)

        page_title = QLabel("Cài đặt")
        page_title.setFont(QFont("Segoe UI Semibold", 15))
        page_title.setStyleSheet(f"color: {_TEXT_PRIMARY}; background: transparent;")

        page_sub = QLabel("Quản lý thông tin cá nhân, bảo mật và giao diện của bạn.")
        page_sub.setFont(QFont("Segoe UI", 9))
        page_sub.setStyleSheet(f"color: {_TEXT_MUTED}; background: transparent;")

        title_col.addWidget(page_title)
        title_col.addWidget(page_sub)

        header_row.addWidget(icon_badge)
        header_row.addLayout(title_col)
        header_row.addStretch()
        self._main_layout.addLayout(header_row)

    # ── 1. Profile Card ───────────────────────────────────────────────
    def _build_profile_card(self):
        card = _make_card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(16)

        card_layout.addWidget(_make_section_title("Thông tin cá nhân", "👤"))
        card_layout.addWidget(_make_divider_line())

        # ── Avatar row ─────────────────────────────────────────────────
        avatar_row = QHBoxLayout()
        avatar_row.setContentsMargins(0, 4, 0, 4)
        avatar_row.setSpacing(20)

        avatar_col = QVBoxLayout()
        avatar_col.setContentsMargins(0, 0, 0, 0)
        avatar_col.setSpacing(8)
        avatar_col.setAlignment(Qt.AlignHCenter)

        initials = "".join(w[0] for w in self._MOCK_NAME.split() if w)[:2].upper()
        self._avatar_widget = AvatarWidget(initials=initials, size=80)
        avatar_col.addWidget(self._avatar_widget, alignment=Qt.AlignHCenter)

        self._btn_change_avatar = QPushButton("🖼  Thay đổi ảnh đại diện")
        self._btn_change_avatar.setFont(QFont("Segoe UI", 9))
        self._btn_change_avatar.setCursor(Qt.PointingHandCursor)
        self._btn_change_avatar.setFixedHeight(32)
        self._btn_change_avatar.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {_ACCENT};
                border: 1px solid {_ACCENT};
                border-radius: 6px;
                padding: 0px 12px;
            }}
            QPushButton:hover {{ background-color: {_ACCENT_LIGHT}; }}
            QPushButton:pressed {{ background-color: #D0E8FF; padding-top: 1px; }}
        """)
        self._btn_change_avatar.clicked.connect(self._on_change_avatar)
        avatar_col.addWidget(self._btn_change_avatar, alignment=Qt.AlignHCenter)

        hint_lbl = QLabel("JPG, PNG – tối đa 2MB")
        hint_lbl.setFont(QFont("Segoe UI", 8))
        hint_lbl.setStyleSheet(f"color: {_TEXT_MUTED}; background: transparent;")
        hint_lbl.setAlignment(Qt.AlignHCenter)
        avatar_col.addWidget(hint_lbl)
        avatar_row.addLayout(avatar_col)

        vline = QFrame()
        vline.setFrameShape(QFrame.VLine)
        vline.setFixedWidth(1)
        vline.setStyleSheet(f"background-color: {_DIVIDER}; border: none;")
        avatar_row.addWidget(vline)

        # ── Form cột phải ──────────────────────────────────────────────
        form_col = QVBoxLayout()
        form_col.setContentsMargins(4, 0, 0, 0)
        form_col.setSpacing(12)

        # Hàng 1: Họ và tên (full width)
        self._input_name = GlowLineEdit("Nhập họ và tên...")
        self._input_name.setText(self._MOCK_NAME)
        form_col.addLayout(_field_col("Họ và tên", self._input_name))

        # Hàng 2: Email + Số điện thoại
        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(16)

        self._input_email = GlowLineEdit("Nhập địa chỉ email...")
        self._input_email.setText(self._MOCK_EMAIL)

        self._input_phone = GlowLineEdit("Nhập số điện thoại...")
        self._input_phone.setText(self._MOCK_PHONE)

        row2.addLayout(_field_col("Email", self._input_email))
        row2.addLayout(_field_col("Số điện thoại", self._input_phone))
        form_col.addLayout(row2)

        # Hàng 3: Giới tính + Ngày sinh
        row3 = QHBoxLayout()
        row3.setContentsMargins(0, 0, 0, 0)
        row3.setSpacing(16)

        # Giới tính – QComboBox
        self._combo_gender = QComboBox()
        self._combo_gender.addItems(["Nam", "Nữ", "Khác", "Không muốn tiết lộ"])
        self._combo_gender.setCurrentIndex(0)
        self._combo_gender.setFixedHeight(36)
        self._combo_gender.setCursor(Qt.PointingHandCursor)
        self._combo_gender.setStyleSheet(f"""
            QComboBox {{
                background-color : #FFFFFF;
                border           : 1.5px solid {_BORDER_CARD};
                border-radius    : 8px;
                padding          : 0px 12px;
                color            : {_TEXT_PRIMARY};
                font-family      : 'Segoe UI';
                font-size        : 10pt;
            }}
            QComboBox:hover {{
                border-color: {_ACCENT};
            }}
            QComboBox:focus {{
                border-color     : {_ACCENT};
                background-color : {_ACCENT_LIGHT};
            }}
            QComboBox::drop-down {{
                border: none;
                width : 28px;
            }}
            QComboBox::down-arrow {{
                image : none;
                width : 0;
            }}
            QComboBox QAbstractItemView {{
                background-color : #FFFFFF;
                border           : 1px solid {_BORDER_CARD};
                border-radius    : 6px;
                selection-background-color: {_ACCENT_LIGHT};
                selection-color  : {_ACCENT};
                color            : {_TEXT_PRIMARY};
                font-family      : 'Segoe UI';
                font-size        : 10pt;
                padding          : 4px;
            }}
        """)

        # Ngày sinh – QDateEdit
        self._date_dob = QDateEdit()
        self._date_dob.setDate(QDate(2003, 1, 15))
        self._date_dob.setCalendarPopup(True)
        self._date_dob.setDisplayFormat("dd/MM/yyyy")
        self._date_dob.setFixedHeight(36)
        self._date_dob.setCursor(Qt.PointingHandCursor)
        self._date_dob.setStyleSheet(f"""
            QDateEdit {{
                background-color : #FFFFFF;
                border           : 1.5px solid {_BORDER_CARD};
                border-radius    : 8px;
                padding          : 0px 12px;
                color            : {_TEXT_PRIMARY};
                font-family      : 'Segoe UI';
                font-size        : 10pt;
            }}
            QDateEdit:hover  {{ border-color: {_ACCENT}; }}
            QDateEdit:focus  {{
                border-color     : {_ACCENT};
                background-color : {_ACCENT_LIGHT};
            }}
            QDateEdit::drop-down {{
                border     : none;
                width      : 28px;
            }}
            QDateEdit::down-arrow {{
                image : none;
            }}
        """)

        row3.addLayout(_field_col("Giới tính", self._combo_gender))
        row3.addLayout(_field_col("Ngày sinh", self._date_dob))
        form_col.addLayout(row3)

        form_col.addStretch()
        avatar_row.addLayout(form_col, stretch=1)
        card_layout.addLayout(avatar_row)
        self._main_layout.addWidget(card)

    # ── 2. Security Card ──────────────────────────────────────────────
    def _build_security_card(self):
        """Card bảo mật: chỉ hiện nút toggle, form ẩn mặc định."""
        self._security_card = _make_card()
        card_layout = QVBoxLayout(self._security_card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(16)

        # ── Header row: tiêu đề + nút toggle ──────────────────────────
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
                color            : {_ACCENT};
                border           : 1.5px solid {_ACCENT};
                border-radius    : 8px;
                padding          : 0px 14px;
                font-family      : 'Segoe UI Semibold';
                font-size        : 9pt;
            }}
            QPushButton:hover {{
                background-color : {_ACCENT_LIGHT};
            }}
            QPushButton:checked {{
                background-color : {_ACCENT};
                color            : #FFFFFF;
                border-color     : {_ACCENT};
            }}
            QPushButton:checked:hover {{
                background-color : #0062CC;
            }}
        """)
        self._btn_toggle_pw.toggled.connect(self._on_toggle_password_form)
        header_row.addWidget(self._btn_toggle_pw)
        card_layout.addLayout(header_row)

        # ── Form đổi mật khẩu (ẩn mặc định) ──────────────────────────
        self._pw_form_widget = QWidget()
        self._pw_form_widget.setStyleSheet("background: transparent;")
        pw_layout = QVBoxLayout(self._pw_form_widget)
        pw_layout.setContentsMargins(0, 0, 0, 0)
        pw_layout.setSpacing(12)

        pw_layout.addWidget(_make_divider_line())

        # Mật khẩu hiện tại
        self._input_cur_pw = GlowLineEdit("Nhập mật khẩu hiện tại...")
        self._input_cur_pw.setEchoMode(self._input_cur_pw.Password)
        pw_layout.addLayout(_field_col("Mật khẩu hiện tại", self._input_cur_pw))

        # Mật khẩu mới + Xác nhận (cạnh nhau)
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

        # Nút xác nhận đổi mật khẩu
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 4, 0, 0)
        self._btn_change_pw = QPushButton("✔  Xác nhận đổi mật khẩu")
        self._btn_change_pw.setFont(QFont("Segoe UI Semibold", 10))
        self._btn_change_pw.setCursor(Qt.PointingHandCursor)
        self._btn_change_pw.setFixedHeight(40)
        self._btn_change_pw.setMinimumWidth(200)
        self._btn_change_pw.setStyleSheet(f"""
            QPushButton {{
                background-color : {_ACCENT};
                color            : #FFFFFF;
                border           : none;
                border-radius    : 8px;
                padding          : 0px 20px;
                font-family      : 'Segoe UI Semibold';
                font-size        : 10pt;
            }}
            QPushButton:hover   {{ background-color: #0062CC; }}
            QPushButton:pressed {{ background-color: #004FA3; padding-top: 2px; }}
        """)
        self._btn_change_pw.clicked.connect(self._on_change_password)
        btn_row.addStretch()
        btn_row.addWidget(self._btn_change_pw)
        pw_layout.addLayout(btn_row)

        # Ẩn form mặc định
        self._pw_form_widget.setVisible(False)
        card_layout.addWidget(self._pw_form_widget)

        self._main_layout.addWidget(self._security_card)

    # ── 3. Interface Card ─────────────────────────────────────────────
    def _build_interface_card(self):
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
            QRadioButton {{
                color: {_TEXT_PRIMARY}; background: transparent; spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: 18px; height: 18px; border-radius: 9px;
                border: 2px solid {_BORDER_CARD}; background: #FFFFFF;
            }}
            QRadioButton::indicator:checked {{
                background: {accent}; border-color: {accent};
            }}
            QRadioButton:hover {{ color: {accent}; }}
        """

        self._radio_light = QRadioButton("☀️   Giao diện sáng  (Clinical Light)")
        self._radio_light.setFont(QFont("Segoe UI", 10))
        self._radio_light.setChecked(True)
        self._radio_light.setCursor(Qt.PointingHandCursor)
        self._radio_light.setStyleSheet(_radio_style(_ACCENT))
        self._radio_group.addButton(self._radio_light, 0)

        self._radio_dark = QRadioButton("🌙   Giao diện tối  (Dark Mode)")
        self._radio_dark.setFont(QFont("Segoe UI", 10))
        self._radio_dark.setCursor(Qt.PointingHandCursor)
        self._radio_dark.setStyleSheet(_radio_style("#6C757D"))
        self._radio_group.addButton(self._radio_dark, 1)

        radio_row.addWidget(self._radio_light)
        radio_row.addWidget(self._radio_dark)
        radio_row.addStretch()
        card_layout.addLayout(radio_row)

        note_frame = QFrame()
        note_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {_WARN_BG};
                border: 1px solid {_WARN_BORDER};
                border-radius: 8px;
            }}
        """)
        note_layout = QHBoxLayout(note_frame)
        note_layout.setContentsMargins(12, 8, 12, 8)
        note_layout.setSpacing(8)

        note_icon = QLabel("💡")
        note_icon.setFont(QFont("Segoe UI", 10))
        note_icon.setStyleSheet("background: transparent;")

        note_text = QLabel(
            "Chức năng Dark Mode hiện đang được phát triển. "
            "Thay đổi sẽ được áp dụng khi khởi động lại ứng dụng."
        )
        note_text.setFont(QFont("Segoe UI", 8))
        note_text.setWordWrap(True)
        note_text.setStyleSheet("color: #856404; background: transparent;")

        note_layout.addWidget(note_icon, alignment=Qt.AlignTop)
        note_layout.addWidget(note_text, 1)
        card_layout.addWidget(note_frame)

        self._main_layout.addWidget(card)

    # ── 4. Bottom Actions ─────────────────────────────────────────────
    def _build_bottom_actions(self):
        actions_row = QHBoxLayout()
        actions_row.setContentsMargins(0, 4, 0, 0)
        actions_row.setSpacing(12)

        self._btn_reset = QPushButton("↺  Đặt lại mặc định")
        self._btn_reset.setFont(QFont("Segoe UI", 10))
        self._btn_reset.setCursor(Qt.PointingHandCursor)
        self._btn_reset.setFixedHeight(44)
        self._btn_reset.setMinimumWidth(160)
        self._btn_reset.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {_TEXT_MUTED};
                border: 1.5px solid {_BORDER_CARD};
                border-radius: 8px;
                padding: 0px 18px;
                font-family: 'Segoe UI'; font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: #F1F3F5;
                color: {_TEXT_PRIMARY};
                border-color: #ADB5BD;
            }}
            QPushButton:pressed {{ background-color: #DEE2E6; padding-top: 2px; }}
        """)
        self._btn_reset.clicked.connect(self._on_reset)

        self._btn_save = GoldButton(text="💾  Lưu cài đặt", width=160, height=44)
        self._btn_save.clicked.connect(self._on_save)

        actions_row.addStretch()
        actions_row.addWidget(self._btn_reset)
        actions_row.addWidget(self._btn_save)
        self._main_layout.addLayout(actions_row)

    # =========================================================================
    # STYLE
    # =========================================================================
    def _apply_page_style(self):
        self.setStyleSheet(f"QWidget#SettingsScreen {{ background-color: {_BG_PAGE}; }}")

    # =========================================================================
    # SLOTS
    # =========================================================================
    def _on_toggle_password_form(self, checked: bool):
        """Hiển thị / ẩn form đổi mật khẩu."""
        self._pw_form_widget.setVisible(checked)
        self._btn_toggle_pw.setText(
            "✕  Đóng" if checked else "🔑  Đổi mật khẩu"
        )
        # Xóa nội dung khi đóng
        if not checked:
            self._input_cur_pw.clear()
            self._input_new_pw.clear()
            self._input_confirm_pw.clear()

    def _on_change_avatar(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Thay đổi ảnh đại diện")
        msg.setText(
            "Chức năng tải ảnh đại diện đang được phát triển.\n"
            "Tính năng này sẽ hỗ trợ định dạng JPG, PNG (tối đa 2MB)."
        )
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet(self._msg_style(_ACCENT))
        msg.exec_()

    def _on_change_password(self):
        cur_pw     = self._input_cur_pw.text().strip()
        new_pw     = self._input_new_pw.text().strip()
        confirm_pw = self._input_confirm_pw.text().strip()

        if not cur_pw:
            self._show_warning("Vui lòng nhập mật khẩu hiện tại.")
            return
        if not new_pw:
            self._show_warning("Vui lòng nhập mật khẩu mới.")
            return
        if new_pw != confirm_pw:
            self._show_warning("Mật khẩu mới và xác nhận mật khẩu không khớp.")
            return
        if len(new_pw) < 6:
            self._show_warning("Mật khẩu mới phải có ít nhất 6 ký tự.")
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("✅  Đổi mật khẩu thành công")
        msg.setText("<b>Mật khẩu của bạn đã được cập nhật thành công!</b>")
        msg.setInformativeText(
            "<i style='color:#6C757D;'>(Mock – chưa lưu vào cơ sở dữ liệu)</i>"
        )
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet(self._msg_style(_ACCENT))
        msg.exec_()

        # Đóng form sau khi đổi thành công
        self._btn_toggle_pw.setChecked(False)

    def _show_warning(self, message: str):
        msg = QMessageBox(self)
        msg.setWindowTitle("⚠️  Lỗi nhập liệu")
        msg.setText(message)
        msg.setIcon(QMessageBox.Warning)
        msg.setStyleSheet(self._msg_style(_ACCENT))
        msg.exec_()

    def _msg_style(self, btn_color: str) -> str:
        return f"""
            QMessageBox {{ background-color: #FFFFFF; }}
            QLabel {{
                color: {_TEXT_PRIMARY}; font-family: 'Segoe UI';
                font-size: 10pt; min-width: 260px;
            }}
            QPushButton {{
                background-color: {btn_color}; color: #FFFFFF;
                border: none; border-radius: 6px; padding: 6px 18px;
                font-family: 'Segoe UI Semibold'; font-size: 10pt; min-width: 80px;
            }}
            QPushButton:hover {{ background-color: #0062CC; }}
        """

    def _on_reset(self):
        reply = QMessageBox.question(
            self, "Xác nhận đặt lại",
            "Bạn có chắc muốn đặt lại toàn bộ cài đặt về mặc định không?\n"
            "Thao tác này không thể hoàn tác.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self._input_name.setText(self._MOCK_NAME)
            self._input_email.setText(self._MOCK_EMAIL)
            self._input_phone.setText(self._MOCK_PHONE)
            self._combo_gender.setCurrentIndex(0)
            self._date_dob.setDate(QDate(2003, 1, 15))
            self._radio_light.setChecked(True)
            self._btn_toggle_pw.setChecked(False)

    def _on_save(self):
        name       = self._input_name.text().strip()
        email      = self._input_email.text().strip()
        phone      = self._input_phone.text().strip()
        gender     = self._combo_gender.currentText()
        dob        = self._date_dob.date().toString("dd/MM/yyyy")
        theme_name = "Clinical Light" if self._radio_group.checkedId() == 0 else "Dark Mode"

        print(
            f"[SettingsScreen] Lưu cài đặt (Mock):\n"
            f"  Tên        : {name}\n"
            f"  Email      : {email}\n"
            f"  ĐT         : {phone}\n"
            f"  Giới tính  : {gender}\n"
            f"  Ngày sinh  : {dob}\n"
            f"  Giao diện  : {theme_name}"
        )

        msg = QMessageBox(self)
        msg.setWindowTitle("✅  Lưu cài đặt thành công")
        msg.setText(
            "<b>Đã cập nhật các thay đổi thành công!</b><br><br>"
            "<i style='color:#6C757D;'>(Mock – chưa lưu vào cơ sở dữ liệu)</i>"
        )
        msg.setInformativeText(
            f"👤  Tên: <b>{name}</b><br>"
            f"📧  Email: <b>{email}</b><br>"
            f"📱  Điện thoại: <b>{phone}</b><br>"
            f"⚧  Giới tính: <b>{gender}</b><br>"
            f"🎂  Ngày sinh: <b>{dob}</b><br>"
            f"🎨  Giao diện: <b>{theme_name}</b>"
        )
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet(f"""
            QMessageBox {{ background-color: #FFFFFF; border: 1px solid {_BORDER_CARD}; }}
            QLabel {{
                color: {_TEXT_PRIMARY}; font-family: 'Segoe UI';
                font-size: 10pt; min-width: 320px;
            }}
            QPushButton {{
                background-color: {_GOLD}; color: #FFFFFF;
                border: none; border-radius: 6px; padding: 6px 20px;
                font-family: 'Segoe UI Semibold'; font-size: 10pt;
                min-width: 90px; min-height: 24px;
            }}
            QPushButton:hover   {{ background-color: #B8960C; }}
            QPushButton:pressed {{ padding-top: 2px; }}
        """)
        msg.exec_()

    # =========================================================================
    # PUBLIC API
    # =========================================================================
    def load_profile(self, name: str, email: str = "", phone: str = "",
                     gender: str = "Nam", dob: QDate = None):
        self._input_name.setText(name)
        self._input_email.setText(email)
        self._input_phone.setText(phone)
        idx = self._combo_gender.findText(gender)
        if idx >= 0:
            self._combo_gender.setCurrentIndex(idx)
        if dob:
            self._date_dob.setDate(dob)
        initials = "".join(w[0] for w in name.split() if w)[:2].upper()
        self._avatar_widget._initials = initials
        self._avatar_widget.update()

    def get_settings_data(self) -> dict:
        return {
            "name":   self._input_name.text().strip(),
            "email":  self._input_email.text().strip(),
            "phone":  self._input_phone.text().strip(),
            "gender": self._combo_gender.currentText(),
            "dob":    self._date_dob.date().toString("yyyy-MM-dd"),
            "theme":  "light" if self._radio_group.checkedId() == 0 else "dark",
        }


# ===========================================================================
# Standalone Test
# ===========================================================================
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    win = QWidget()
    win.setWindowTitle("Settings Screen – Clinical Light Preview")
    win.resize(860, 750)
    win.setStyleSheet(f"background-color: {_BG_PAGE};")

    layout = QVBoxLayout(win)
    layout.setContentsMargins(0, 0, 0, 0)

    screen = SettingsScreen()
    layout.addWidget(screen)

    win.show()
    sys.exit(app.exec_())