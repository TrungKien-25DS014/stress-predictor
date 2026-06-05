from __future__ import annotations
from PyQt5.QtWidgets import (
    QLineEdit, QPushButton, QWidget, QSlider,
    QGraphicsDropShadowEffect, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QRadioButton, QButtonGroup, QSizePolicy, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPainter, QPixmap, QPaintEvent, QFocusEvent, QResizeEvent

from src.core.config import C

# Độ bo góc mặc định áp dụng cho hệ thống điều khiển
DEFAULT_RADIUS = 8

class GlowLineEdit(QLineEdit):
    '''
    Ô nhập liệu thông minh tích hợp hiệu ứng viền phát sáng khi kích hoạt.
    Trạng thái:
      - Bình thường: Viền xám nhạt tinh tế, không bóng đổ.
      - Tập trung (Focus): Viền đổi màu accent và hiển thị hiệu ứng phát sáng nhẹ.
    '''

    def __init__(self, placeholder: str = "", parent: QWidget | None = None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)

        self.setFont(QFont("Segoe UI", 10))
        self.setFixedHeight(42)

        # Cấu hình hiệu ứng phát sáng mặc định ẩn
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setColor(QColor(C["accent"]))
        self._shadow.setBlurRadius(0)
        self._shadow.setOffset(0, 0)
        self.setGraphicsEffect(self._shadow)

        self._apply_idle_style()

    def _apply_idle_style(self):
        '''Thiết lập giao diện mặc định khi không hoạt động'''
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color : {C['white']};
                color            : {C['text_primary']};
                border           : 1.5px solid {C['card_border']};
                border-radius    : {DEFAULT_RADIUS}px;
                padding          : 0px 12px;
                font-family      : 'Segoe UI';
                font-size        : 10pt;
            }}
            QLineEdit:disabled {{
                background-color : {C['bg_main']};
                color            : {C['text_muted']};
            }}
        """)

    def _apply_focus_style(self):
        '''Thiết lập giao diện nổi bật khi người dùng chọn vào ô'''
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color : {C['white']};
                color            : {C['text_primary']};
                border           : 1.5px solid {C['accent']};
                border-radius    : {DEFAULT_RADIUS}px;
                padding          : 0px 12px;
                font-family      : 'Segoe UI';
                font-size        : 10pt;
            }}
        """)

    def focusInEvent(self, event: QFocusEvent):
        '''Kích hoạt hiệu ứng phát sáng khi ô nhập liệu nhận focus'''
        super().focusInEvent(event)
        self._apply_focus_style()
        self._shadow.setBlurRadius(18)
        self._shadow.setColor(QColor(0, 122, 255, 160))

    def focusOutEvent(self, event: QFocusEvent):
        '''Tắt hiệu ứng phát sáng khi ô nhập liệu mất focus'''
        super().focusOutEvent(event)
        self._apply_idle_style()
        self._shadow.setBlurRadius(0)


class GoldButton(QPushButton):
    '''
    Nút bấm mang phong cách vàng ánh kim cao cấp.
    Thích hợp dùng cho các hành động quan trọng bậc nhất hoặc tạo điểm nhấn thương hiệu.
    '''

    def __init__(self, text: str = "Button", width: int = 0, height: int = 44, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setFont(QFont("Segoe UI Semibold", 10))
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(height)

        if width > 0:
            self.setFixedWidth(width)

        # Hiệu ứng đổ bóng mờ tạo chiều sâu cho nút
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(212, 175, 55, 80))
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        self._apply_style()

    def _apply_style(self):
        '''Cấu hình bảng style sheet đồng bộ màu gold từ config'''
        self.setStyleSheet(f"""
            QPushButton {{
                background-color : {C['gold']};
                color            : {C['white']};
                border           : none;
                border-radius    : {DEFAULT_RADIUS}px;
                padding          : 0px 20px;
                font-family      : 'Segoe UI Semibold';
                font-size        : 10pt;
                letter-spacing   : 0.3px;
            }}
            QPushButton:hover {{
                background-color : {C['btn_gold_h_edge']};
            }}
            QPushButton:pressed {{
                background-color : {C['btn_gold_p_edge']};
                padding-top      : 2px;
            }}
            QPushButton:disabled {{
                background-color : {C['divider']};
                color            : {C['text_muted']};
            }}
        """)

    def set_label(self, text: str):
        '''Hỗ trợ thay đổi tiêu đề động'''
        self.setText(text)


class BackgroundWidget(QWidget):
    '''
    Widget xử lý hình nền động, có khả năng tự động co giãn tối ưu 
    theo độ phân giải hiển thị thực tế của cửa sổ ứng dụng.
    '''

    def __init__(self, image_path: str = "", scale_mode: Qt.AspectRatioMode = Qt.KeepAspectRatioByExpanding, overlay_opacity: float = 0.0, parent: QWidget | None = None):
        super().__init__(parent)
        self._pixmap = None
        self._scaled_cache = None
        self._last_size = None
        self.scale_mode = scale_mode
        self.overlay_opacity = max(0.0, min(1.0, overlay_opacity))

        if image_path:
            self.set_image(image_path)

    def set_image(self, image_path: str):
        '''Cập nhật hình nền mới cho giao diện'''
        px = QPixmap(image_path)
        if px.isNull():
            self._pixmap = None
            self._scaled_cache = None
        else:
            self._pixmap = px
            self._scaled_cache = None
        self.update()

    def set_overlay_opacity(self, value: float):
        '''Điều chỉnh độ hiển thị của lớp phủ mịn phía trên ảnh nền'''
        self.overlay_opacity = max(0.0, min(1.0, value))
        self.update()

    def paintEvent(self, event: QPaintEvent):
        '''Vẽ ảnh nền cùng lớp bao phủ dựa trên bộ đệm cache để tối ưu hiệu năng CPU'''
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        if self._pixmap is not None:
            current_size = rect.size()
            if current_size != self._last_size or self._scaled_cache is None:
                self._scaled_cache = self._pixmap.scaled(current_size, self.scale_mode, Qt.SmoothTransformation)
                self._last_size = current_size

            x_offset = (rect.width() - self._scaled_cache.width()) // 2
            y_offset = (rect.height() - self._scaled_cache.height()) // 2
            painter.drawPixmap(x_offset, y_offset, self._scaled_cache)
        else:
            painter.fillRect(rect, QColor(C["bg_main"]))

        if self.overlay_opacity > 0.0:
            overlay_color = QColor(255, 255, 255, int(self.overlay_opacity * 255))
            painter.fillRect(rect, overlay_color)

        painter.end()

    def resizeEvent(self, event: QResizeEvent):
        '''Giải phóng bộ nhớ cache hình ảnh cũ khi kích thước khung thay đổi'''
        self._scaled_cache = None
        super().resizeEvent(event)


class StyledCard(QWidget):
    '''
    Khung chứa dữ liệu thông tin (Card) được chuẩn hóa theo hệ thống Clinical Light.
    Hỗ trợ 5 trạng thái thiết kế trực quan thông qua thuộc tính 'variant'.
    '''

    def __init__(self, variant: str = "default", padding: int = 16, radius: int = 12, shadow: bool = True, parent: QWidget | None = None):
        super().__init__(parent)

        variants_config = {
            "default": {"bg": C["white"], "border": C["card_border"], "shadow": QColor(0, 0, 0, 25)},
            "accent":  {"bg": C["accent_light"], "border": C["accent"], "shadow": QColor(0, 122, 255, 40)},
            "success": {"bg": C.get("success_bg", "#E9F7EF"), "border": C["success"], "shadow": QColor(40, 167, 69, 40)},
            "warning": {"bg": C.get("warning_bg", "#FFF9E6"), "border": C["warning"], "shadow": QColor(255, 193, 7, 50)},
            "danger":  {"bg": C.get("danger_bg", "#FDECEA"), "border": C["danger"], "shadow": QColor(220, 53, 69, 40)}
        }

        cfg = variants_config.get(variant, variants_config["default"])

        if shadow:
            fx = QGraphicsDropShadowEffect(self)
            fx.setColor(cfg["shadow"])
            fx.setBlurRadius(16)
            fx.setOffset(0, 3)
            self.setGraphicsEffect(fx)

        self.setStyleSheet(f"""
            StyledCard {{
                background-color : {cfg['bg']};
                border           : 1px solid {cfg['border']};
                border-radius    : {radius}px;
            }}
        """)

        self.body_layout = QVBoxLayout(self)
        self.body_layout.setContentsMargins(padding, padding, padding, padding)
        self.body_layout.setSpacing(8)


class PrimaryButton(QPushButton):
    '''
    Nút bấm chủ đạo mang màu sắc thương hiệu xanh y tế.
    Hỗ trợ các dạng thức: Solid (nền đặc), Outline (khung viền) và Ghost (trong suốt).
    '''

    def __init__(self, text: str = "Button", variant: str = "solid", width: int = 0, height: int = 44, parent: QWidget | None = None):
        super().__init__(text, parent)
        self.setFont(QFont("Segoe UI Semibold", 10))
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(height)
        if width > 0:
            self.setFixedWidth(width)

        css_templates = {
            "solid": f"""
                QPushButton {{
                    background-color : {C['accent']};
                    color            : {C['white']};
                    border           : none;
                    border-radius    : {DEFAULT_RADIUS}px;
                    padding          : 0px 20px;
                    font-family      : 'Segoe UI Semibold';
                    font-size        : 10pt;
                    letter-spacing   : 0.3px;
                }}
                QPushButton:hover {{ background-color: {C['accent_hover']}; }}
                QPushButton:pressed {{ background-color: {C.get('accent_pressed', '#004FA3')}; padding-top: 2px; }}
                QPushButton:disabled {{ background-color: {C['divider']}; color: {C['text_muted']}; }}
            """,
            "outline": f"""
                QPushButton {{
                    background-color : transparent;
                    color            : {C['accent']};
                    border           : 1.5px solid {C['accent']};
                    border-radius    : {DEFAULT_RADIUS}px;
                    padding          : 0px 20px;
                    font-family      : 'Segoe UI Semibold';
                    font-size        : 10pt;
                }}
                QPushButton:hover {{ background-color: {C['accent_light']}; }}
                QPushButton:pressed {{ background-color: {C.get('accent_light_pressed', '#D0E8FF')}; padding-top: 2px; }}
                QPushButton:disabled {{ border-color: {C['card_border']}; color: {C['text_muted']}; }}
            """,
            "ghost": f"""
                QPushButton {{
                    background-color : transparent;
                    color            : {C['accent']};
                    border           : none;
                    border-radius    : {DEFAULT_RADIUS}px;
                    padding          : 0px 16px;
                    font-family      : 'Segoe UI';
                    font-size        : 10pt;
                }}
                QPushButton:hover {{ background-color: {C['accent_light']}; }}
                QPushButton:pressed {{ background-color: {C.get('accent_light_pressed', '#D0E8FF')}; padding-top: 2px; }}
                QPushButton:disabled {{ color: {C['text_muted']}; }}
            """
        }

        self.setStyleSheet(css_templates.get(variant, css_templates["solid"]))

        if variant == "solid":
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setColor(QColor(0, 122, 255, 70))
            shadow.setBlurRadius(12)
            shadow.setOffset(0, 3)
            self.setGraphicsEffect(shadow)


class StyledInput(QWidget):
    '''
    Thành phần nhập liệu hoàn chỉnh bao gồm Label tiêu đề, ô nhập phát sáng 
    và khu vực cảnh báo thông tin lỗi trực quan.
    '''

    def __init__(self, label: str = "", placeholder: str = "", required: bool = False, parent: QWidget | None = None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        if label:
            lbl_row = QHBoxLayout()
            lbl_row.setContentsMargins(0, 0, 0, 0)
            lbl_row.setSpacing(2)

            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI Semibold", 9))
            lbl.setStyleSheet(f"color: {C['text_primary']};")
            lbl_row.addWidget(lbl)

            if required:
                req = QLabel("*")
                req.setFont(QFont("Segoe UI", 9, QFont.Bold))
                req.setStyleSheet(f"color: {C['danger']};")
                lbl_row.addWidget(req)

            lbl_row.addStretch()
            root.addLayout(lbl_row)

        self.input = GlowLineEdit(placeholder)
        root.addWidget(self.input)

        self._error_lbl = QLabel("")
        self._error_lbl.setFont(QFont("Segoe UI", 8))
        self._error_lbl.setStyleSheet(f"color: {C['danger']};")
        self._error_lbl.setVisible(False)
        root.addWidget(self._error_lbl)

    def text(self) -> str:
        '''Lấy chuỗi văn bản người dùng nhập hiện tại'''
        return self.input.text()

    def set_error(self, message: str):
        '''Bật hiển thị trạng thái lỗi cùng thông điệp cảnh báo'''
        self._error_lbl.setText(f"⚠  {message}")
        self._error_lbl.setVisible(True)
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background-color : {C['white']};
                color            : {C['text_primary']};
                border           : 1.5px solid {C['danger']};
                border-radius    : {DEFAULT_RADIUS}px;
                padding          : 0px 12px;
                font-family      : 'Segoe UI';
                font-size        : 10pt;
            }}
        """)

    def clear_error(self):
        '''Khôi phục lại giao diện bình thường, xóa cảnh báo lỗi'''
        self._error_lbl.setVisible(False)
        self.input._apply_idle_style()


class StyledSlider(QWidget):
    '''
    Thanh trượt lựa chọn thông số nâng cao tích hợp nhãn mô tả, 
    giới hạn cận biên (Thấp/Cao) và Badge số hiển thị kết quả thời gian thực.
    '''
    from PyQt5.QtCore import pyqtSignal as _sig
    valueChanged = _sig(int)

    def __init__(self, label: str = "", min_val: int = 0, max_val: int = 10, default: int | None = None, min_label: str = "Thấp", max_label: str = "Cao", parent: QWidget | None = None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        if label:
            title_row = QHBoxLayout()
            title_row.setContentsMargins(0, 0, 0, 0)

            title_lbl = QLabel(label)
            title_lbl.setFont(QFont("Segoe UI Semibold", 9))
            title_lbl.setStyleSheet(f"color: {C['text_primary']};")

            self._badge = QLabel()
            self._badge.setFont(QFont("Segoe UI Semibold", 9))
            self._badge.setAlignment(Qt.AlignCenter)
            self._badge.setFixedSize(36, 22)
            self._badge.setStyleSheet(f"""
                background-color: {C['accent']};
                color: {C['white']};
                border-radius: 6px;
            """)

            title_row.addWidget(title_lbl)
            title_row.addStretch()
            title_row.addWidget(self._badge)
            root.addLayout(title_row)
        else:
            self._badge = QLabel()

        slider_row = QHBoxLayout()
        slider_row.setContentsMargins(0, 0, 0, 0)
        slider_row.setSpacing(8)

        lo_lbl = QLabel(min_label)
        lo_lbl.setFont(QFont("Segoe UI", 8))
        lo_lbl.setStyleSheet(f"color: {C['text_muted']};")

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(min_val, max_val)
        init_val = default if default is not None else min_val
        self._slider.setValue(init_val)
        self._slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height      : 6px;
                background  : {C['divider']};
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background  : {C['accent']};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background  : {C['white']};
                border      : 2px solid {C['accent']};
                width        : 18px;
                height       : 18px;
                margin       : -6px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background: {C['accent_light']};
            }}
        """)

        hi_lbl = QLabel(max_label)
        hi_lbl.setFont(QFont("Segoe UI", 8))
        hi_lbl.setStyleSheet(f"color: {C['text_muted']};")

        slider_row.addWidget(lo_lbl)
        slider_row.addWidget(self._slider, 1)
        slider_row.addWidget(hi_lbl)
        root.addLayout(slider_row)

        self._slider.valueChanged.connect(self._on_change)
        self._on_change(init_val)

    def _on_change(self, v: int):
        '''Cập nhật dữ liệu hiển thị lên badge khi giá trị thanh đổi'''
        self._badge.setText(str(v))
        self.valueChanged.emit(v)

    def value(self) -> int:
        '''Lấy giá trị hiện tại của thanh trượt'''
        return self._slider.value()

    def setValue(self, v: int):
        '''Thiết lập giá trị lập trình cho thanh trượt'''
        self._slider.setValue(v)


class MetricCard(QFrame):
    '''Thẻ biểu diễn chỉ số đơn lẻ kèm thanh Accent chỉ định màu sắc ở đỉnh khung.'''

    def __init__(self, title: str, value: str = "–", accent_color: str = "#4A90D9", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._title = title
        self._value = value
        self._accent_color = accent_color
        self._build_ui()
        self._apply_style()

    def set_value(self, value: str) -> None:
        '''Cập nhật nội dung giá trị đo lường'''
        self._value_label.setText(value)

    def set_title(self, title: str) -> None:
        '''Cập nhật chuỗi tiêu đề của thẻ'''
        self._title_label.setText(title)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        self._accent_bar = QFrame()
        self._accent_bar.setFixedHeight(4)
        self._accent_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._title_label = QLabel(self._title)
        self._title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._title_label.setWordWrap(True)

        self._value_label = QLabel(self._value)
        self._value_label.setAlignment(Qt.AlignLeft | Qt.AlignBottom)

        layout.addWidget(self._accent_bar)
        layout.addWidget(self._title_label)
        layout.addStretch()
        layout.addWidget(self._value_label)

    def _apply_style(self) -> None:
        self._accent_bar.setStyleSheet(f"background-color: {self._accent_color}; border-radius: 2px;")
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: {C['white']};
                border-radius: 12px;
                border: 1px solid {C['divider']};
            }}
            MetricCard:hover {{
                border: 1px solid {self._accent_color};
            }}
        """)
        
        title_font = QFont("Segoe UI", 11)
        self._title_label.setFont(title_font)
        self._title_label.setStyleSheet(f"color: {C['text_muted']};")

        value_font = QFont("Segoe UI", 28, QFont.Bold)
        self._value_label.setFont(value_font)
        self._value_label.setStyleSheet(f"color: {C['text_primary']};")


class CustomMessageBox(QDialog):
    '''
    Hộp thoại thông báo Frameless tùy biến toàn diện, độc lập hoàn toàn 
    với giao diện mặc định nhàm chán của hệ điều hành.
    '''
    
    def __init__(self, msg_type: str, title: str, text: str, parent: QWidget | None = None):
        super().__init__(parent, Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        self.msg_type = msg_type
        self.title_text = title
        self.msg_text = text
        self._drag_pos = None

        self._build_ui()
        self.setMinimumWidth(400)
        self.setMaximumWidth(480)

    def _build_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {C['white']};
                border-radius: 16px;
                border: 1px solid {C['card_border']};
            }}
        """)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 5)
        card.setGraphicsEffect(shadow)

        outer_layout.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 20)
        card_layout.setSpacing(20)

        body_layout = QHBoxLayout()
        body_layout.setSpacing(16)

        icon_lbl = QLabel()
        icon_lbl.setFont(QFont("Segoe UI Emoji", 32))
        icon_lbl.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        icon_lbl.setStyleSheet("background: transparent; border: none;")

        btn_bg = C["accent"]
        btn_hover = C["accent_hover"]
        btn_text = "Đóng"

        if self.msg_type == "success":
            icon_lbl.setText("✅")
            btn_bg = C["success"]
            btn_hover = "#218838"
        elif self.msg_type == "warning":
            icon_lbl.setText("⚠️")
            btn_bg = C["warning"]
            btn_hover = "#D97706"
        elif self.msg_type == "error":
            icon_lbl.setText("❌")
            btn_bg = C["danger"]
            btn_hover = "#C82333"
        elif self.msg_type == "question":
            icon_lbl.setText("❓")
            btn_text = "Đồng ý"

        body_layout.addWidget(icon_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(6)
        
        title_lbl = QLabel(self.title_text)
        title_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_lbl.setStyleSheet(f"color: {C['text_primary']}; background: transparent; border: none;")
        
        msg_lbl = QLabel(self.msg_text)
        msg_lbl.setFont(QFont("Segoe UI", 10))
        msg_lbl.setStyleSheet(f"color: {C['text_muted']}; background: transparent; border: none;")
        msg_lbl.setWordWrap(True)

        text_col.addWidget(title_lbl)
        text_col.addWidget(msg_lbl)
        text_col.addStretch()

        body_layout.addLayout(text_col, 1)
        card_layout.addLayout(body_layout)

        footer_layout = QHBoxLayout()
        footer_layout.addStretch()

        if self.msg_type == "question":
            cancel_btn = QPushButton("Hủy bỏ")
            cancel_btn.setCursor(Qt.PointingHandCursor)
            cancel_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {C['bg_main']}; color: {C['text_muted']};
                    border: 1px solid {C['card_border']}; border-radius: 8px;
                    padding: 8px 20px; font-family: 'Segoe UI Semibold'; font-size: 10pt;
                }}
                QPushButton:hover {{ background-color: {C.get('btn_outline_bg', '#F1F3F5')}; color: {C['text_primary']}; }}
            """)
            cancel_btn.clicked.connect(self.reject)
            footer_layout.addWidget(cancel_btn)

        ok_btn = QPushButton(btn_text)
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_bg}; color: {C['white']};
                border: none; border-radius: 8px;
                padding: 8px 24px; font-family: 'Segoe UI Semibold'; font-size: 10pt;
            }}
            QPushButton:hover {{ background-color: {btn_hover}; }}
            QPushButton:pressed {{ padding-top: 2px; }}
        """)
        ok_btn.clicked.connect(self.accept)
        footer_layout.addWidget(ok_btn)

        card_layout.addLayout(footer_layout)

    def mousePressEvent(self, event):
        '''Ghi nhận điểm nhấn chuột đầu tiên hỗ trợ tính năng kéo di chuyển cửa sổ'''
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        '''Di chuyển cửa sổ theo tọa độ kéo chuột thực tế'''
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        '''Hủy trạng thái kéo cửa sổ khi buông chuột'''
        self._drag_pos = None

    @staticmethod
    def show_success(parent, title: str, text: str):
        CustomMessageBox("success", title, text, parent).exec_()

    @staticmethod
    def show_warning(parent, title: str, text: str):
        CustomMessageBox("warning", title, text, parent).exec_()

    @staticmethod
    def show_error(parent, title: str, text: str):
        CustomMessageBox("error", title, text, parent).exec_()
        
    @staticmethod
    def show_question(parent, title: str, text: str) -> bool:
        return CustomMessageBox("question", title, text, parent).exec_() == QDialog.Accepted