"""
src/ui/main_window.py
---------------------
Cửa sổ chính của ứng dụng Student Stress Predictor.
Design System: Clinical Light
Author  : Senior PyQt5 Engineer
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QStackedWidget, QLabel, QPushButton, QFrame,
    QSizePolicy, QCalendarWidget, QScrollArea,
)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

from src.UI.screens.survey import SurveyScreen
# ---------------------------------------------------------------------------
# Design Tokens – Clinical Light
# ---------------------------------------------------------------------------
COLORS = {
    "bg_main":      "#F8F9FA",   # Nền tổng thể
    "bg_sidebar":   "#FFFFFF",   # Nền sidebar
    "bg_panel":     "#FFFFFF",   # Nền panel phụ
    "text_primary": "#212529",   # Chữ chủ đạo
    "text_muted":   "#6C757D",   # Chữ phụ / caption
    "accent":       "#007AFF",   # Xanh Y tế – brand color
    "accent_light": "#E8F3FF",   # Nền nhấn nhẹ khi hover
    "accent_hover": "#0062CC",   # Xanh đậm hơn khi hover
    "divider":      "#E9ECEF",   # Đường kẻ phân cách
    "success":      "#28A745",   # Xanh lá – trạng thái bình thường
    "warning":      "#FFC107",   # Vàng – cảnh báo
    "danger":       "#DC3545",   # Đỏ – nguy hiểm
    "white":        "#FFFFFF",
}

FONTS = {
    "brand":    QFont("Segoe UI Semibold", 14),
    "nav":      QFont("Segoe UI",          10),
    "heading":  QFont("Segoe UI Semibold", 13),
    "body":     QFont("Segoe UI",           9),
    "caption":  QFont("Segoe UI",           8),
    "greeting": QFont("Segoe UI Semibold", 11),
}


# ===========================================================================
# ──  PLACEHOLDER SCREENS  (sẽ được implement ở các file riêng)
# ===========================================================================

class DashboardScreen(QWidget):
    """Màn hình Tổng quan (Dashboard)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        lbl = QLabel("📊  Dashboard Screen\n(Placeholder – sẽ được implement tại screens/dashboard.py)")
        lbl.setFont(FONTS["body"])
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"color: {COLORS['text_muted']};")
        layout.addWidget(lbl)




class HistoryScreen(QWidget):
    """Màn hình Lịch sử (History)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        lbl = QLabel("📅  History Screen\n(Placeholder – sẽ được implement tại screens/history.py)")
        lbl.setFont(FONTS["body"])
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"color: {COLORS['text_muted']};")
        layout.addWidget(lbl)


class SettingsScreen(QWidget):
    """Màn hình Cài đặt (Settings)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        lbl = QLabel("⚙️  Settings Screen\n(Placeholder – sẽ được implement tại screens/settings.py)")
        lbl.setFont(FONTS["body"])
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet(f"color: {COLORS['text_muted']};")
        layout.addWidget(lbl)


# ===========================================================================
# ──  SIDEBAR  (tỷ lệ 2)
# ===========================================================================

class Sidebar(QFrame):
    """
    Panel điều hướng bên trái.
    Chứa: logo / brand, danh sách nút nav, footer nhỏ.
    """

    # Mapping nhãn → (emoji, index trong QStackedWidget)
    NAV_ITEMS = [
        ("🏠", "Tổng quan",  0),
        ("📝", "Khảo sát",   1),
        ("📅", "Lịch sử",    2),
        ("⚙️", "Cài đặt",   3),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.nav_buttons: list[QPushButton] = []
        self._active_index = 0
        self._build_ui()
        self._apply_styles()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Logo / Brand ────────────────────────────────────────────
        brand_frame = QFrame()
        brand_frame.setObjectName("brand_frame")
        brand_layout = QHBoxLayout(brand_frame)
        brand_layout.setContentsMargins(20, 20, 20, 18)

        dot = QLabel("◆")
        dot.setFont(QFont("Segoe UI", 14, QFont.Bold))
        dot.setStyleSheet(f"color: {COLORS['accent']};")

        name = QLabel("VAULTEX")
        name.setFont(QFont("Segoe UI Black", 13))
        name.setStyleSheet(f"color: {COLORS['accent']}; letter-spacing: 2px;")

        brand_layout.addWidget(dot)
        brand_layout.addWidget(name)
        brand_layout.addStretch()
        root.addWidget(brand_frame)

        # ── Divider ─────────────────────────────────────────────────
        root.addWidget(self._make_divider())

        # ── Section label ────────────────────────────────────────────
        section_lbl = QLabel("DANH MỤC")
        section_lbl.setFont(QFont("Segoe UI", 7, QFont.Bold))
        section_lbl.setStyleSheet(
            f"color: {COLORS['text_muted']}; letter-spacing: 1.5px; "
            "padding: 14px 20px 6px 20px;"
        )
        root.addWidget(section_lbl)

        # ── Navigation buttons ───────────────────────────────────────
        nav_frame = QFrame()
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(10, 4, 10, 4)
        nav_layout.setSpacing(2)

        for icon, label, idx in self.NAV_ITEMS:
            btn = self._make_nav_button(icon, label, idx)
            nav_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        nav_layout.addStretch()
        root.addWidget(nav_frame)

        root.addStretch()

        # ── Footer ───────────────────────────────────────────────────
        footer = QLabel("Stress Predictor  v1.0")
        footer.setFont(FONTS["caption"])
        footer.setStyleSheet(
            f"color: {COLORS['text_muted']}; padding: 12px 20px;"
        )
        footer.setAlignment(Qt.AlignCenter)
        root.addWidget(footer)

        # Đặt active mặc định cho nút đầu tiên
        self._set_active(0)

    # ------------------------------------------------------------------
    def _make_nav_button(self, icon: str, label: str, index: int) -> QPushButton:
        btn = QPushButton(f"  {icon}  {label}")
        btn.setFont(FONTS["nav"])
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("nav_index", index)
        btn.setCheckable(False)
        btn.setObjectName("nav_btn")
        return btn

    # ------------------------------------------------------------------
    def _make_divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {COLORS['divider']}; margin: 0 16px;")
        return line

    # ------------------------------------------------------------------
    def _apply_styles(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_sidebar']};
                border-right: 1px solid {COLORS['divider']};
            }}
            QPushButton#nav_btn {{
                background-color: transparent;
                color: {COLORS['text_muted']};
                border: none;
                border-radius: 8px;
                text-align: left;
                padding-left: 10px;
            }}
            QPushButton#nav_btn:hover {{
                background-color: {COLORS['accent_light']};
                color: {COLORS['accent']};
            }}
        """)

    # ------------------------------------------------------------------
    def _set_active(self, active_idx: int):
        """Cập nhật trạng thái active cho nút tương ứng."""
        self._active_index = active_idx
        for btn in self.nav_buttons:
            idx = btn.property("nav_index")
            if idx == active_idx:
                btn.setStyleSheet(f"""
                    background-color: {COLORS['accent_light']};
                    color: {COLORS['accent']};
                    border: none;
                    border-radius: 8px;
                    font-weight: 600;
                    text-align: left;
                    padding-left: 10px;
                """)
            else:
                btn.setStyleSheet("")   # Reset về stylesheet cha


# ===========================================================================
# ──  RIGHT PANEL  (tỷ lệ 2)
# ===========================================================================

class RightPanel(QFrame):
    """
    Panel thông tin nhanh bên phải.
    Chứa: lời chào người dùng + lịch trình (QCalendarWidget).
    """

    def __init__(self, user_name: str = "Nguyễn Hữu Bảo", parent=None):
        super().__init__(parent)
        self.user_name = user_name
        self._build_ui()
        self._apply_styles()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 20, 16, 20)
        root.setSpacing(16)

        # ── Greeting card ────────────────────────────────────────────
        greeting_card = QFrame()
        greeting_card.setObjectName("greeting_card")
        gc_layout = QVBoxLayout(greeting_card)
        gc_layout.setContentsMargins(14, 12, 14, 12)
        gc_layout.setSpacing(4)

        hello_lbl = QLabel(f"👋  Xin chào,")
        hello_lbl.setFont(FONTS["body"])
        hello_lbl.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")

        name_lbl = QLabel(self.user_name)
        name_lbl.setFont(QFont("Segoe UI Semibold", 12))
        name_lbl.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        name_lbl.setWordWrap(True)

        status_row = QHBoxLayout()
        dot = QLabel("●")
        dot.setFont(QFont("Segoe UI", 8))
        dot.setStyleSheet(f"color: {COLORS['success']}; background: transparent;")
        status_txt = QLabel("Đang hoạt động")
        status_txt.setFont(FONTS["caption"])
        status_txt.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")
        status_row.addWidget(dot)
        status_row.addWidget(status_txt)
        status_row.addStretch()

        gc_layout.addWidget(hello_lbl)
        gc_layout.addWidget(name_lbl)
        gc_layout.addLayout(status_row)
        root.addWidget(greeting_card)

        # ── Section: Lịch trình ─────────────────────────────────────
        sched_lbl = QLabel("Lịch trình")
        sched_lbl.setFont(QFont("Segoe UI Semibold", 10))
        sched_lbl.setStyleSheet(f"color: {COLORS['text_primary']};")
        root.addWidget(sched_lbl)

        # Calendar widget
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setNavigationBarVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.ISOWeekNumbers)
        self.calendar.setFixedHeight(220)
        self.calendar.setStyleSheet(f"""
            QCalendarWidget QWidget {{
                alternate-background-color: {COLORS['bg_main']};
                background-color: {COLORS['white']};
                color: {COLORS['text_primary']};
                font-family: 'Segoe UI';
                font-size: 9pt;
            }}
            QCalendarWidget QAbstractItemView:enabled {{
                color: {COLORS['text_primary']};
                selection-background-color: {COLORS['accent']};
                selection-color: {COLORS['white']};
            }}
            QCalendarWidget QAbstractItemView:disabled {{
                color: {COLORS['text_muted']};
            }}
            QCalendarWidget QToolButton {{
                color: {COLORS['text_primary']};
                background-color: transparent;
                border: none;
                font-family: 'Segoe UI';
                font-size: 9pt;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: {COLORS['accent_light']};
                border-radius: 4px;
                color: {COLORS['accent']};
            }}
            QCalendarWidget #qt_calendar_navigationbar {{
                background-color: {COLORS['white']};
                padding: 4px;
            }}
            QCalendarWidget QSpinBox {{
                color: {COLORS['text_primary']};
                background-color: {COLORS['white']};
                border: 1px solid {COLORS['divider']};
                border-radius: 4px;
            }}
        """)
        root.addWidget(self.calendar)

        # ── Quick stress tip ─────────────────────────────────────────
        tip_card = QFrame()
        tip_card.setObjectName("tip_card")
        tip_layout = QVBoxLayout(tip_card)
        tip_layout.setContentsMargins(12, 10, 12, 10)
        tip_layout.setSpacing(4)

        tip_title = QLabel("💡  Mẹo hôm nay")
        tip_title.setFont(QFont("Segoe UI Semibold", 9))
        tip_title.setStyleSheet(f"color: {COLORS['accent']}; background: transparent;")

        tip_body = QLabel(
            "Hãy dành 5 phút hít thở sâu trước khi bắt đầu bài kiểm tra."
        )
        tip_body.setFont(FONTS["caption"])
        tip_body.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent;")
        tip_body.setWordWrap(True)

        tip_layout.addWidget(tip_title)
        tip_layout.addWidget(tip_body)
        root.addWidget(tip_card)

        root.addStretch()

    # ------------------------------------------------------------------
    def _apply_styles(self):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_panel']};
                border-left: 1px solid {COLORS['divider']};
            }}
            QFrame#greeting_card {{
                background-color: {COLORS['accent_light']};
                border: 1px solid {COLORS['divider']};
                border-radius: 10px;
            }}
            QFrame#tip_card {{
                background-color: {COLORS['bg_main']};
                border: 1px solid {COLORS['divider']};
                border-radius: 10px;
            }}
        """)


# ===========================================================================
# ──  MAIN WINDOW
# ===========================================================================

class MainWindow(QMainWindow):
    """
    Cửa sổ chính của ứng dụng.

    Bố cục tỷ lệ 2 : 6 : 2
    ┌──────────┬──────────────────────┬──────────┐
    │ Sidebar  │    Main Content      │  Right   │
    │  (2/10)  │  QStackedWidget(6/10)│  Panel   │
    │          │                      │  (2/10)  │
    └──────────┴──────────────────────┴──────────┘
    """

    DEFAULT_WIDTH  = 1200
    DEFAULT_HEIGHT = 750
    MIN_WIDTH      = 900
    MIN_HEIGHT     = 600

    def __init__(self):
        super().__init__()
        self._init_window()
        self._build_layout()
        self._connect_navigation()
        self._apply_global_styles()

    # ------------------------------------------------------------------
    # 1. Khởi tạo cửa sổ
    # ------------------------------------------------------------------
    def _init_window(self):
        self.setWindowTitle("Stress Predictor Dashboard")
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)

        # Màu nền tổng thể
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(COLORS["bg_main"]))
        self.setPalette(palette)

    # ------------------------------------------------------------------
    # 2. Xây dựng bố cục chính
    # ------------------------------------------------------------------
    def _build_layout(self):
        # Widget gốc
        central = QWidget()
        central.setObjectName("central_widget")
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar (tỷ lệ 2) ────────────────────────────────────────
        self.sidebar = Sidebar()
        self.sidebar.setObjectName("sidebar")

        # ── QStackedWidget – Main Content (tỷ lệ 6) ─────────────────
        self.stack = QStackedWidget()
        self.stack.setObjectName("main_stack")

        # Đăng ký các màn hình theo đúng thứ tự index
        self._screens: dict[str, QWidget] = {
            "dashboard": DashboardScreen(self),   # index 0
            "survey":    SurveyScreen(self),      # index 1
            "history":   HistoryScreen(self),     # index 2
            "settings":  SettingsScreen(self),    # index 3
        }
        for screen in self._screens.values():
            self.stack.addWidget(screen)

        self.stack.setCurrentIndex(0)

        # ── Right Panel (tỷ lệ 2) ────────────────────────────────────
        self.right_panel = RightPanel(user_name="Nguyễn Hữu Bảo")
        self.right_panel.setObjectName("right_panel")

        # ── Thêm vào layout với tỷ lệ 2:6:2 ─────────────────────────
        main_layout.addWidget(self.sidebar,     stretch=2)
        main_layout.addWidget(self.stack,       stretch=6)
        main_layout.addWidget(self.right_panel, stretch=2)

    # ------------------------------------------------------------------
    # 3. Kết nối điều hướng
    # ------------------------------------------------------------------
    def _connect_navigation(self):
        """
        Kết nối mỗi nút nav trong Sidebar với phương thức chuyển trang.
        Sử dụng lambda để truyền đúng index vào slot.
        """
        for btn in self.sidebar.nav_buttons:
            idx = btn.property("nav_index")
            # Dùng default argument để tránh vấn đề closure trong vòng lặp
            btn.clicked.connect(
                lambda checked, i=idx: self._navigate_to(i)
            )

    # ------------------------------------------------------------------
    def _navigate_to(self, index: int):
        """
        Chuyển màn hình tại QStackedWidget và cập nhật trạng thái
        active trên Sidebar.

        Args:
            index (int): Index của màn hình cần chuyển đến.
        """
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)
            self.sidebar._set_active(index)

    # ------------------------------------------------------------------
    # 4. Truy cập màn hình theo tên (helper công khai)
    # ------------------------------------------------------------------
    def get_screen(self, name: str) -> QWidget | None:
        """
        Trả về widget màn hình theo tên.

        Args:
            name: 'dashboard' | 'survey' | 'history' | 'settings'

        Returns:
            QWidget hoặc None nếu tên không hợp lệ.
        """
        return self._screens.get(name)

    # ------------------------------------------------------------------
    # 5. Style toàn cục
    # ------------------------------------------------------------------
    def _apply_global_styles(self):
        self.setStyleSheet(f"""
            QWidget#central_widget {{
                background-color: {COLORS['bg_main']};
            }}
            QStackedWidget#main_stack {{
                background-color: {COLORS['bg_main']};
                border: none;
            }}
        """)
    # ===================================================================
# RUN APPLICATION
# ===================================================================

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())