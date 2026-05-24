"""
src/ui/components/custom_widgets.py
------------------------------------
Bộ widget tùy biến theo phong cách Clinical Light.

Gồm 3 thành phần:
  - GlowLineEdit    : Ô nhập liệu có hiệu ứng glow khi focus
  - GoldButton      : Nút bấm vàng gold với hover + press animation
  - BackgroundWidget: Widget nền ảnh tự động scale theo cửa sổ

Author : Senior PyQt5 Engineer
"""

from __future__ import annotations

from PyQt5.QtWidgets import (
    QLineEdit, QPushButton, QWidget,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPixmap,
    QPaintEvent, QFocusEvent, QResizeEvent,
)

# ---------------------------------------------------------------------------
# Design Tokens
# ---------------------------------------------------------------------------
_ACCENT        = "#007AFF"
_ACCENT_HOVER  = "#0062CC"
_BORDER_IDLE   = "#CED4DA"
_BORDER_FOCUS  = "#007AFF"
_GOLD          = "#D4AF37"
_GOLD_HOVER    = "#B8960C"
_GOLD_PRESSED  = "#9A7D0A"
_WHITE         = "#FFFFFF"
_TEXT_DARK     = "#212529"
_TEXT_MUTED    = "#6C757D"
_RADIUS        = 8


# ===========================================================================
# 1. GlowLineEdit
# ===========================================================================
class GlowLineEdit(QLineEdit):
    """
    Ô nhập liệu với hiệu ứng viền phát sáng khi được focus.

    Trạng thái:
      - Idle   : viền xám nhạt (#CED4DA), không có shadow
      - Focus  : viền xanh (#007AFF) + QGraphicsDropShadowEffect màu xanh

    Tham số khởi tạo:
      placeholder (str) : Placeholder text hiển thị khi rỗng
      parent            : Widget cha
    """

    def __init__(self, placeholder: str = "", parent: QWidget | None = None):
        super().__init__(parent)

        if placeholder:
            self.setPlaceholderText(placeholder)

        self.setFont(QFont("Segoe UI", 10))
        self.setFixedHeight(42)

        # Tạo shadow effect – ban đầu tắt (blurRadius = 0)
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setColor(QColor(_ACCENT))
        self._shadow.setBlurRadius(0)
        self._shadow.setOffset(0, 0)
        self.setGraphicsEffect(self._shadow)

        self._apply_idle_style()

    # ── Style helpers ──────────────────────────────────────────────────
    def _apply_idle_style(self):
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color : {_WHITE};
                color            : {_TEXT_DARK};
                border           : 1.5px solid {_BORDER_IDLE};
                border-radius    : {_RADIUS}px;
                padding          : 0px 12px;
                font-family      : 'Segoe UI';
                font-size        : 10pt;
            }}
            QLineEdit:disabled {{
                background-color : #F8F9FA;
                color            : {_TEXT_MUTED};
            }}
        """)

    def _apply_focus_style(self):
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color : {_WHITE};
                color            : {_TEXT_DARK};
                border           : 1.5px solid {_BORDER_FOCUS};
                border-radius    : {_RADIUS}px;
                padding          : 0px 12px;
                font-family      : 'Segoe UI';
                font-size        : 10pt;
            }}
        """)

    # ── Event overrides ────────────────────────────────────────────────
    def focusInEvent(self, event: QFocusEvent):
        """Kích hoạt glow khi người dùng click vào ô."""
        super().focusInEvent(event)
        self._apply_focus_style()
        self._shadow.setBlurRadius(18)
        self._shadow.setColor(QColor(0, 122, 255, 160))   # #007AFF với alpha 160

    def focusOutEvent(self, event: QFocusEvent):
        """Tắt glow khi người dùng click ra ngoài."""
        super().focusOutEvent(event)
        self._apply_idle_style()
        self._shadow.setBlurRadius(0)


# ===========================================================================
# 2. GoldButton
# ===========================================================================
class GoldButton(QPushButton):
    """
    Nút bấm phong cách vàng gold.

    Trạng thái:
      - Normal  : nền #D4AF37, chữ trắng
      - Hover   : nền đậm hơn #B8960C
      - Pressed : nền tối hơn #9A7D0A + lún nhẹ (padding-top tăng 2px)
      - Disabled: nền xám, chữ muted

    Tham số khởi tạo:
      text   (str)  : Nhãn nút
      width  (int)  : Chiều rộng cố định (0 = tự động)
      height (int)  : Chiều cao cố định (mặc định 44px)
      parent        : Widget cha
    """

    def __init__(
        self,
        text: str = "Button",
        width: int = 0,
        height: int = 44,
        parent: QWidget | None = None,
    ):
        super().__init__(text, parent)

        self.setFont(QFont("Segoe UI Semibold", 10))
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(height)

        if width > 0:
            self.setFixedWidth(width)

        # Drop shadow nhẹ để tạo chiều sâu
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(212, 175, 55, 80))   # gold với alpha 80
        shadow.setBlurRadius(12)
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

        self._apply_style()

    # ── Style ──────────────────────────────────────────────────────────
    def _apply_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color : {_GOLD};
                color            : {_WHITE};
                border           : none;
                border-radius    : {_RADIUS}px;
                padding          : 0px 20px;
                font-family      : 'Segoe UI Semibold';
                font-size        : 10pt;
                letter-spacing   : 0.3px;
            }}

            /* ── Hover: làm tối nền ── */
            QPushButton:hover {{
                background-color : {_GOLD_HOVER};
            }}

            /* ── Pressed: tối hơn nữa + lún nhẹ ── */
            QPushButton:pressed {{
                background-color : {_GOLD_PRESSED};
                padding-top      : 2px;
            }}

            /* ── Disabled ── */
            QPushButton:disabled {{
                background-color : #E9ECEF;
                color            : {_TEXT_MUTED};
            }}
        """)

    # ── Convenience: đổi nhãn và tự resize ────────────────────────────
    def set_label(self, text: str):
        self.setText(text)


# ===========================================================================
# 3. BackgroundWidget
# ===========================================================================
class BackgroundWidget(QWidget):
    """
    Widget hiển thị ảnh nền tự động scale theo kích thước cửa sổ.

    Ảnh được vẽ lại trong paintEvent mỗi khi widget thay đổi kích thước,
    đảm bảo luôn lấp đầy toàn bộ diện tích mà không méo (AspectRatioMode
    có thể tuỳ chỉnh qua thuộc tính scale_mode).

    Tham số khởi tạo:
      image_path (str)         : Đường dẫn tuyệt đối / tương đối tới file ảnh
      scale_mode               : Qt.KeepAspectRatioByExpanding (mặc định)
                                 hoặc Qt.IgnoreAspectRatio / Qt.KeepAspectRatio
      overlay_opacity (float)  : 0.0–1.0, độ mờ của lớp phủ trắng chồng lên
                                 ảnh để nội dung bên trên dễ đọc hơn (mặc định 0)
      parent                   : Widget cha
    """

    def __init__(
        self,
        image_path: str = "",
        scale_mode: Qt.AspectRatioMode = Qt.KeepAspectRatioByExpanding,
        overlay_opacity: float = 0.0,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self._pixmap          : QPixmap | None = None
        self._scaled_cache    : QPixmap | None = None   # cache tránh scale lại liên tục
        self._last_size                        = None   # kích thước lần scale trước
        self.scale_mode       = scale_mode
        self.overlay_opacity  = max(0.0, min(1.0, overlay_opacity))

        if image_path:
            self.set_image(image_path)

    # ── Public API ─────────────────────────────────────────────────────
    def set_image(self, image_path: str):
        """
        Tải và hiển thị ảnh nền mới.
        Có thể gọi lại bất cứ lúc nào để đổi ảnh nền runtime.
        """
        px = QPixmap(image_path)
        if px.isNull():
            # Ảnh không tồn tại hoặc không đọc được – giữ nền trong suốt
            self._pixmap       = None
            self._scaled_cache = None
        else:
            self._pixmap       = px
            self._scaled_cache = None   # Xoá cache để vẽ lại
        self.update()

    def set_overlay_opacity(self, value: float):
        """Điều chỉnh độ mờ của lớp phủ (0.0 = trong suốt, 1.0 = trắng hoàn toàn)."""
        self.overlay_opacity = max(0.0, min(1.0, value))
        self.update()

    # ── Event overrides ────────────────────────────────────────────────
    def paintEvent(self, event: QPaintEvent):
        """
        Vẽ ảnh nền scale khớp widget, sau đó vẽ lớp phủ mờ nếu cần.
        Được gọi tự động mỗi khi widget cần redraw (bao gồm cả resize).
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        if self._pixmap is not None:
            # Chỉ scale lại khi kích thước thực sự thay đổi (cache tối ưu CPU)
            current_size = rect.size()
            if current_size != self._last_size or self._scaled_cache is None:
                self._scaled_cache = self._pixmap.scaled(
                    current_size,
                    self.scale_mode,
                    Qt.SmoothTransformation,
                )
                self._last_size = current_size

            # Canh giữa ảnh trong trường hợp KeepAspectRatio có viền trống
            img_w = self._scaled_cache.width()
            img_h = self._scaled_cache.height()
            x_offset = (rect.width()  - img_w) // 2
            y_offset = (rect.height() - img_h) // 2
            painter.drawPixmap(x_offset, y_offset, self._scaled_cache)

        else:
            # Không có ảnh – tô nền trắng mặc định
            painter.fillRect(rect, QColor("#F8F9FA"))

        # Lớp phủ bán trong suốt để tăng độ tương phản cho nội dung bên trên
        if self.overlay_opacity > 0.0:
            overlay_color = QColor(255, 255, 255, int(self.overlay_opacity * 255))
            painter.fillRect(rect, overlay_color)

        painter.end()

    def resizeEvent(self, event: QResizeEvent):
        """Xoá cache khi widget bị resize để paintEvent scale lại."""
        self._scaled_cache = None
        super().resizeEvent(event)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout

    app = QApplication(sys.argv)

    window = QWidget()
    window.resize(500, 300)

    layout = QVBoxLayout(window)

    input_box = GlowLineEdit("Nhập gì đó...")
    btn = GoldButton("Submit")

    layout.addWidget(input_box)
    layout.addWidget(btn)

    window.show()
    sys.exit(app.exec_())

# ===========================================================================
# 4. StyledCard
# ===========================================================================
class StyledCard(QWidget):
    """
    Card container tái sử dụng theo phong cách Clinical Light.

    Các biến thể (variant):
      - 'default'  : Nền trắng, viền xám nhạt, bo góc 12px
      - 'accent'   : Nền xanh nhạt (#E8F3FF), viền xanh brand
      - 'success'  : Nền xanh lá nhạt, viền #28A745
      - 'warning'  : Nền vàng nhạt, viền #FFC107
      - 'danger'   : Nền đỏ nhạt, viền #DC3545

    Tham số khởi tạo:
      variant  (str)   : Một trong 5 biến thể trên (mặc định 'default')
      padding  (int)   : Padding nội dung bên trong card (mặc định 16px)
      radius   (int)   : Border-radius (mặc định 12px)
      shadow   (bool)  : Thêm drop-shadow nhẹ hay không (mặc định True)
      parent           : Widget cha

    Cách dùng:
      card = StyledCard(variant='accent')
      card.body_layout.addWidget(QLabel("Nội dung"))
    """

    _VARIANTS = {
        "default": {
            "bg":     "#FFFFFF",
            "border": "#DEE2E6",
            "shadow": QColor(0, 0, 0, 25),
        },
        "accent": {
            "bg":     "#E8F3FF",
            "border": "#007AFF",
            "shadow": QColor(0, 122, 255, 40),
        },
        "success": {
            "bg":     "#E9F7EF",
            "border": "#28A745",
            "shadow": QColor(40, 167, 69, 40),
        },
        "warning": {
            "bg":     "#FFF9E6",
            "border": "#FFC107",
            "shadow": QColor(255, 193, 7, 50),
        },
        "danger": {
            "bg":     "#FDECEA",
            "border": "#DC3545",
            "shadow": QColor(220, 53, 69, 40),
        },
    }

    def __init__(
        self,
        variant: str = "default",
        padding: int = 16,
        radius: int = 12,
        shadow: bool = True,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        v = self._VARIANTS.get(variant, self._VARIANTS["default"])

        if shadow:
            fx = QGraphicsDropShadowEffect(self)
            fx.setColor(v["shadow"])
            fx.setBlurRadius(16)
            fx.setOffset(0, 3)
            self.setGraphicsEffect(fx)

        self.setStyleSheet(f"""
            StyledCard {{
                background-color : {v['bg']};
                border           : 1px solid {v['border']};
                border-radius    : {radius}px;
            }}
        """)

        # Layout body – người dùng addWidget vào đây
        self.body_layout = QVBoxLayout(self)
        self.body_layout.setContentsMargins(padding, padding, padding, padding)
        self.body_layout.setSpacing(8)


# ===========================================================================
# 5. PrimaryButton
# ===========================================================================
class PrimaryButton(QPushButton):
    """
    Nút bấm chủ đạo (Primary) theo màu accent xanh brand.

    Trạng thái:
      - Normal   : nền #007AFF, chữ trắng
      - Hover    : nền #0062CC
      - Pressed  : nền #004FA3 + padding-top +2px
      - Disabled : nền xám nhạt, chữ muted

    Biến thể (variant):
      - 'solid'   (mặc định) : nền đặc xanh
      - 'outline'            : nền trong suốt, viền xanh, chữ xanh
      - 'ghost'              : không viền, chữ xanh, hover nhẹ

    Tham số khởi tạo:
      text     (str)   : Nhãn nút
      variant  (str)   : 'solid' | 'outline' | 'ghost'
      width    (int)   : Chiều rộng cố định (0 = tự động)
      height   (int)   : Chiều cao (mặc định 44px)
      parent           : Widget cha
    """

    _CSS: dict[str, str] = {
        "solid": f"""
            QPushButton {{
                background-color : {_ACCENT};
                color            : {_WHITE};
                border           : none;
                border-radius    : {_RADIUS}px;
                padding          : 0px 20px;
                font-family      : 'Segoe UI Semibold';
                font-size        : 10pt;
                letter-spacing   : 0.3px;
            }}
            QPushButton:hover    {{ background-color: {_ACCENT_HOVER}; }}
            QPushButton:pressed  {{ background-color: #004FA3; padding-top: 2px; }}
            QPushButton:disabled {{ background-color: #E9ECEF; color: {_TEXT_MUTED}; }}
        """,
        "outline": f"""
            QPushButton {{
                background-color : transparent;
                color            : {_ACCENT};
                border           : 1.5px solid {_ACCENT};
                border-radius    : {_RADIUS}px;
                padding          : 0px 20px;
                font-family      : 'Segoe UI Semibold';
                font-size        : 10pt;
            }}
            QPushButton:hover    {{ background-color: #E8F3FF; }}
            QPushButton:pressed  {{ background-color: #D0E8FF; padding-top: 2px; }}
            QPushButton:disabled {{ border-color: #CED4DA; color: {_TEXT_MUTED}; }}
        """,
        "ghost": f"""
            QPushButton {{
                background-color : transparent;
                color            : {_ACCENT};
                border           : none;
                border-radius    : {_RADIUS}px;
                padding          : 0px 16px;
                font-family      : 'Segoe UI';
                font-size        : 10pt;
            }}
            QPushButton:hover    {{ background-color: #E8F3FF; }}
            QPushButton:pressed  {{ background-color: #D0E8FF; padding-top: 2px; }}
            QPushButton:disabled {{ color: {_TEXT_MUTED}; }}
        """,
    }

    def __init__(
        self,
        text: str = "Button",
        variant: str = "solid",
        width: int = 0,
        height: int = 44,
        parent: QWidget | None = None,
    ):
        super().__init__(text, parent)

        self.setFont(QFont("Segoe UI Semibold", 10))
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(height)
        if width > 0:
            self.setFixedWidth(width)

        css = self._CSS.get(variant, self._CSS["solid"])
        self.setStyleSheet(css)

        if variant == "solid":
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setColor(QColor(0, 122, 255, 70))
            shadow.setBlurRadius(12)
            shadow.setOffset(0, 3)
            self.setGraphicsEffect(shadow)


# ===========================================================================
# 6. StyledInput  (wrapper GlowLineEdit với label + error message)
# ===========================================================================
class StyledInput(QWidget):
    """
    Input field đầy đủ: Label tiêu đề + GlowLineEdit + thông báo lỗi.

    Tham số khởi tạo:
      label        (str)  : Nhãn hiển thị phía trên input
      placeholder  (str)  : Placeholder bên trong input
      required     (bool) : Hiện dấu * đỏ nếu True
      parent               : Widget cha

    API công khai:
      .text()              → str   : Lấy nội dung nhập
      .set_error(msg)               : Hiển thị thông báo lỗi màu đỏ
      .clear_error()                : Xoá thông báo lỗi
      .input                        : Truy cập GlowLineEdit bên trong
    """

    def __init__(
        self,
        label: str = "",
        placeholder: str = "",
        required: bool = False,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(4)

        # ── Label row ──────────────────────────────────────────────────
        if label:
            lbl_row = QHBoxLayout()
            lbl_row.setContentsMargins(0, 0, 0, 0)
            lbl_row.setSpacing(2)

            lbl = QLabel(label)
            lbl.setFont(QFont("Segoe UI Semibold", 9))
            lbl.setStyleSheet(f"color: {_TEXT_DARK};")
            lbl_row.addWidget(lbl)

            if required:
                req = QLabel("*")
                req.setFont(QFont("Segoe UI", 9, QFont.Bold))
                req.setStyleSheet("color: #DC3545;")
                lbl_row.addWidget(req)

            lbl_row.addStretch()
            root.addLayout(lbl_row)

        # ── GlowLineEdit ───────────────────────────────────────────────
        self.input = GlowLineEdit(placeholder)
        root.addWidget(self.input)

        # ── Error label (ẩn mặc định) ──────────────────────────────────
        self._error_lbl = QLabel("")
        self._error_lbl.setFont(QFont("Segoe UI", 8))
        self._error_lbl.setStyleSheet("color: #DC3545;")
        self._error_lbl.setVisible(False)
        root.addWidget(self._error_lbl)

    # ── Public API ─────────────────────────────────────────────────────
    def text(self) -> str:
        return self.input.text()

    def set_error(self, message: str):
        self._error_lbl.setText(f"⚠  {message}")
        self._error_lbl.setVisible(True)
        self.input.setStyleSheet(f"""
            QLineEdit {{
                background-color : {_WHITE};
                color            : {_TEXT_DARK};
                border           : 1.5px solid #DC3545;
                border-radius    : {_RADIUS}px;
                padding          : 0px 12px;
                font-family      : 'Segoe UI';
                font-size        : 10pt;
            }}
        """)

    def clear_error(self):
        self._error_lbl.setVisible(False)
        self.input._apply_idle_style()


# ===========================================================================
# 7. StyledSlider  (Slider với label, min/max labels và giá trị hiện tại)
# ===========================================================================
class StyledSlider(QWidget):
    """
    Slider tái sử dụng đầy đủ tiêu chuẩn Clinical Light.

    Gồm:
      - Label tiêu đề
      - QSlider ngang với accent color
      - Nhãn min / max hai bên
      - Badge hiển thị giá trị hiện tại

    Tham số khởi tạo:
      label      (str)   : Tiêu đề slider
      min_val    (int)   : Giá trị nhỏ nhất (mặc định 0)
      max_val    (int)   : Giá trị lớn nhất (mặc định 10)
      default    (int)   : Giá trị ban đầu
      min_label  (str)   : Nhãn cạnh trái (mặc định "Thấp")
      max_label  (str)   : Nhãn cạnh phải (mặc định "Cao")
      parent             : Widget cha

    Signal:
      valueChanged(int)  : Phát mỗi khi giá trị thay đổi

    API công khai:
      .value()  → int    : Lấy giá trị hiện tại
      .setValue(int)     : Đặt giá trị lập trình
    """

    from PyQt5.QtCore import pyqtSignal as _sig
    valueChanged = _sig(int)

    def __init__(
        self,
        label: str = "",
        min_val: int = 0,
        max_val: int = 10,
        default: int | None = None,
        min_label: str = "Thấp",
        max_label: str = "Cao",
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        # ── Title row ──────────────────────────────────────────────────
        if label:
            title_row = QHBoxLayout()
            title_row.setContentsMargins(0, 0, 0, 0)

            title_lbl = QLabel(label)
            title_lbl.setFont(QFont("Segoe UI Semibold", 9))
            title_lbl.setStyleSheet(f"color: {_TEXT_DARK};")

            self._badge = QLabel()
            self._badge.setFont(QFont("Segoe UI Semibold", 9))
            self._badge.setAlignment(Qt.AlignCenter)
            self._badge.setFixedSize(36, 22)
            self._badge.setStyleSheet(f"""
                background-color: {_ACCENT};
                color: {_WHITE};
                border-radius: 6px;
            """)

            title_row.addWidget(title_lbl)
            title_row.addStretch()
            title_row.addWidget(self._badge)
            root.addLayout(title_row)
        else:
            self._badge = QLabel()

        # ── Slider row ─────────────────────────────────────────────────
        slider_row = QHBoxLayout()
        slider_row.setContentsMargins(0, 0, 0, 0)
        slider_row.setSpacing(8)

        lo_lbl = QLabel(min_label)
        lo_lbl.setFont(QFont("Segoe UI", 8))
        lo_lbl.setStyleSheet(f"color: {_TEXT_MUTED};")

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(min_val, max_val)
        init_val = default if default is not None else min_val
        self._slider.setValue(init_val)
        self._slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                height      : 6px;
                background  : #E9ECEF;
                border-radius: 3px;
            }}
            QSlider::sub-page:horizontal {{
                background  : {_ACCENT};
                border-radius: 3px;
            }}
            QSlider::handle:horizontal {{
                background  : {_WHITE};
                border      : 2px solid {_ACCENT};
                width        : 18px;
                height       : 18px;
                margin       : -6px 0;
                border-radius: 9px;
            }}
            QSlider::handle:horizontal:hover {{
                background: #E8F3FF;
            }}
        """)

        hi_lbl = QLabel(max_label)
        hi_lbl.setFont(QFont("Segoe UI", 8))
        hi_lbl.setStyleSheet(f"color: {_TEXT_MUTED};")

        slider_row.addWidget(lo_lbl)
        slider_row.addWidget(self._slider, 1)
        slider_row.addWidget(hi_lbl)
        root.addLayout(slider_row)

        # ── Connect ────────────────────────────────────────────────────
        self._slider.valueChanged.connect(self._on_change)
        self._on_change(init_val)   # Khởi tạo badge

    # ── Slots ──────────────────────────────────────────────────────────
    def _on_change(self, v: int):
        self._badge.setText(str(v))
        self.valueChanged.emit(v)

    # ── Public API ─────────────────────────────────────────────────────
    def value(self) -> int:
        return self._slider.value()

    def setValue(self, v: int):
        self._slider.setValue(v)