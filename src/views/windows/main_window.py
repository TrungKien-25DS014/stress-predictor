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
from src.views.components.widgets import MetricCard
from src.views.screens.survey import SurveyScreen
from src.views.screens.dashboard import DashboardScreen
from src.views.screens.history import HistoryScreen
from src.views.screens.settings import SettingsScreen
from src.core.config import C, FONTS 

# ===========================================================================
# ──  SIDEBAR  (tỷ lệ 2)
# ===========================================================================

class Sidebar(QFrame):
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

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        brand_frame = QFrame()
        brand_frame.setObjectName("brand_frame")
        brand_layout = QHBoxLayout(brand_frame)
        brand_layout.setContentsMargins(20, 20, 20, 18)

        dot = QLabel("◆")
        dot.setFont(QFont("Segoe UI", 14, QFont.Bold))
        dot.setStyleSheet(f"color: {C['accent']};")

        name = QLabel("VAULTEX")
        name.setFont(QFont("Segoe UI Black", 13))
        name.setStyleSheet(f"color: {C['accent']}; letter-spacing: 2px;")

        brand_layout.addWidget(dot)
        brand_layout.addWidget(name)
        brand_layout.addStretch()
        root.addWidget(brand_frame)

        root.addWidget(self._make_divider())

        section_lbl = QLabel("DANH MỤC")
        section_lbl.setFont(QFont("Segoe UI", 7, QFont.Bold))
        section_lbl.setStyleSheet(
            f"color: {C['text_muted']}; letter-spacing: 1.5px; "
            "padding: 14px 20px 6px 20px;"
        )
        root.addWidget(section_lbl)

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

        footer = QLabel("Stress Predictor  v1.0")
        footer.setFont(FONTS["caption"])
        footer.setStyleSheet(f"color: {C['text_muted']}; padding: 12px 20px;")
        footer.setAlignment(Qt.AlignCenter)
        root.addWidget(footer)

        self._set_active(0)

    def _make_nav_button(self, icon: str, label: str, index: int) -> QPushButton:
        btn = QPushButton(f"  {icon}  {label}")
        btn.setFont(FONTS["nav"])
        btn.setFixedHeight(40)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("nav_index", index)
        btn.setCheckable(False)
        btn.setObjectName("nav_btn")
        return btn

    def _make_divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {C['divider']}; margin: 0 16px;")
        return line

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QFrame {{ background-color: {C['bg_sidebar']}; border-right: 1px solid {C['divider']}; }}
            QPushButton#nav_btn {{ background-color: transparent; color: {C['text_muted']}; border: none; border-radius: 8px; text-align: left; padding-left: 10px; }}
            QPushButton#nav_btn:hover {{ background-color: {C['accent_light']}; color: {C['accent']}; }}
        """)

    def _set_active(self, active_idx: int):
        self._active_index = active_idx
        for btn in self.nav_buttons:
            idx = btn.property("nav_index")
            if idx == active_idx:
                btn.setStyleSheet(f"""
                    background-color: {C['accent_light']}; color: {C['accent']};
                    border: none; border-radius: 8px; font-weight: 600;
                    text-align: left; padding-left: 10px;
                """)
            else:
                btn.setStyleSheet("")


# ===========================================================================
# ──  RIGHT PANEL  (tỷ lệ 2)
# ===========================================================================

class RightPanel(QFrame):
    def __init__(self, user_name: str = "Nguyễn Hữu Bảo", parent=None):
        super().__init__(parent)
        self.user_name = user_name
        self._build_ui()
        self._apply_styles()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 20, 16, 20)
        root.setSpacing(16)

        greeting_card = QFrame()
        greeting_card.setObjectName("greeting_card")
        gc_layout = QVBoxLayout(greeting_card)
        gc_layout.setContentsMargins(14, 12, 14, 12)
        gc_layout.setSpacing(4)

        hello_lbl = QLabel(f"👋  Xin chào,")
        hello_lbl.setFont(FONTS["body"])
        hello_lbl.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")

        name_lbl = QLabel(self.user_name)
        name_lbl.setObjectName("greeting_name_lbl")
        name_lbl.setFont(QFont("Segoe UI Semibold", 12))
        name_lbl.setStyleSheet(f"color: {C['text_primary']}; background: transparent;")
        name_lbl.setWordWrap(True)

        status_row = QHBoxLayout()
        dot = QLabel("●")
        dot.setFont(QFont("Segoe UI", 8))
        dot.setStyleSheet(f"color: {C['success']}; background: transparent;")
        status_txt = QLabel("Đang hoạt động")
        status_txt.setFont(FONTS["caption"])
        status_txt.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")
        status_row.addWidget(dot)
        status_row.addWidget(status_txt)
        status_row.addStretch()

        gc_layout.addWidget(hello_lbl)
        gc_layout.addWidget(name_lbl)
        gc_layout.addLayout(status_row)
        root.addWidget(greeting_card)

        sched_lbl = QLabel("Lịch trình")
        sched_lbl.setFont(QFont("Segoe UI Semibold", 10))
        sched_lbl.setStyleSheet(f"color: {C['text_primary']};")
        root.addWidget(sched_lbl)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(False)
        self.calendar.setNavigationBarVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.ISOWeekNumbers)
        self.calendar.setFixedHeight(220)
        self.calendar.setStyleSheet(f"""
            QCalendarWidget QWidget {{
                alternate-background-color: {C['bg_main']}; background-color: {C['white']};
                color: {C['text_primary']}; font-family: 'Segoe UI'; font-size: 9pt;
            }}
            QCalendarWidget QAbstractItemView:enabled {{ color: {C['text_primary']}; selection-background-color: {C['accent']}; selection-color: {C['white']}; }}
            QCalendarWidget QAbstractItemView:disabled {{ color: {C['text_muted']}; }}
            QCalendarWidget QToolButton {{ color: {C['text_primary']}; background-color: transparent; border: none; font-family: 'Segoe UI'; font-size: 9pt; }}
            QCalendarWidget QToolButton:hover {{ background-color: {C['accent_light']}; border-radius: 4px; color: {C['accent']}; }}
            QCalendarWidget #qt_calendar_navigationbar {{ background-color: {C['white']}; padding: 4px; }}
            QCalendarWidget QSpinBox {{ color: {C['text_primary']}; background-color: {C['white']}; border: 1px solid {C['divider']}; border-radius: 4px; }}
        """)
        root.addWidget(self.calendar)

        tip_card = QFrame()
        tip_card.setObjectName("tip_card")
        tip_layout = QVBoxLayout(tip_card)
        tip_layout.setContentsMargins(12, 10, 12, 10)
        tip_layout.setSpacing(4)

        tip_title = QLabel("💡  Mẹo hôm nay")
        tip_title.setFont(QFont("Segoe UI Semibold", 9))
        tip_title.setStyleSheet(f"color: {C['accent']}; background: transparent;")

        tip_body = QLabel("Hãy dành 5 phút hít thở sâu trước khi bắt đầu bài kiểm tra.")
        tip_body.setFont(FONTS["caption"])
        tip_body.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")
        tip_body.setWordWrap(True)

        tip_layout.addWidget(tip_title)
        tip_layout.addWidget(tip_body)
        root.addWidget(tip_card)

        know_lbl = QLabel("🧠  Bạn có biết?")
        know_lbl.setFont(QFont("Segoe UI Semibold", 10))
        know_lbl.setStyleSheet(f"color: {C['text_primary']};")
        root.addWidget(know_lbl)

        facts = [
            ("😰", "Stress kéo dài làm giảm khả năng ghi nhớ và tập trung."),
            ("🫀", "Cortisol cao liên tục ảnh hưởng đến tim mạch và hệ miễn dịch."),
            ("🌿", "Thiên nhiên và cây xanh giúp giảm stress hiệu quả trong 5 phút."),
        ]
        for emoji, text in facts:
            row = QFrame()
            row.setObjectName("fact_row")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(10, 8, 10, 8)
            rl.setSpacing(8)

            e_lbl = QLabel(emoji)
            e_lbl.setFont(QFont("Segoe UI", 11))
            e_lbl.setStyleSheet("background: transparent; border: none;")
            e_lbl.setFixedWidth(22)
            e_lbl.setAlignment(Qt.AlignTop)

            t_lbl = QLabel(text)
            t_lbl.setFont(FONTS["caption"])
            t_lbl.setWordWrap(True)
            t_lbl.setStyleSheet(f"color: {C['text_muted']}; background: transparent; border: none;")

            rl.addWidget(e_lbl)
            rl.addWidget(t_lbl, 1)
            root.addWidget(row)

        root.addStretch()

    def set_user(self, display_name: str):
        self.user_name = display_name
        from PyQt5.QtWidgets import QLabel
        lbl = self.findChild(QLabel, "greeting_name_lbl")
        if lbl:
            lbl.setText(display_name)

    def _apply_styles(self):
        self.setStyleSheet(f"""
            QFrame {{ background-color: {C['bg_panel']}; border-left: 1px solid {C['divider']}; }}
            QFrame#greeting_card {{ background-color: {C['accent_light']}; border: 1px solid {C['divider']}; border-radius: 10px; }}
            QFrame#tip_card {{ background-color: {C['bg_main']}; border: 1px solid {C['divider']}; border-radius: 10px; }}
            QFrame#fact_row {{ background-color: {C['white']}; border: 1px solid {C['divider']}; border-radius: 8px; }}
        """)

# ===========================================================================
# ──  MAIN WINDOW
# ===========================================================================

class MainWindow(QMainWindow):
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

    def _init_window(self):
        self.setWindowTitle("Stress Predictor Dashboard")
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(C["bg_main"]))
        self.setPalette(palette)

    def _build_layout(self):
        central = QWidget()
        central.setObjectName("central_widget")
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.sidebar.setObjectName("sidebar")

        self.stack = QStackedWidget()
        self.stack.setObjectName("main_stack")

        self._screens: dict[str, QWidget] = {
            "dashboard": DashboardScreen(self),
            "survey":    SurveyScreen(self),
            "history":   HistoryScreen(self),
            "settings":  SettingsScreen(self),
        }
        for screen in self._screens.values():
            self.stack.addWidget(screen)

        self.stack.setCurrentIndex(0)

        self.right_panel = RightPanel(user_name="Nguyễn Hữu Bảo")
        self.right_panel.setObjectName("right_panel")

        self.sidebar.setMinimumWidth(200) 
        self.sidebar.setMaximumWidth(16777215) 
        self.right_panel.setMinimumWidth(200)
        self.right_panel.setMaximumWidth(16777215)
        self.stack.setMinimumWidth(400)

        main_layout.addWidget(self.sidebar, stretch=2)
        main_layout.addWidget(self.stack, stretch=6)
        main_layout.addWidget(self.right_panel, stretch=2)

    def _connect_navigation(self):
        for btn in self.sidebar.nav_buttons:
            idx = btn.property("nav_index")
            btn.clicked.connect(lambda checked, i=idx: self._navigate_to(i))

    def _navigate_to(self, index: int):
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)
            self.sidebar._set_active(index)

    def get_screen(self, name: str) -> QWidget | None:
        return self._screens.get(name)

    def _apply_global_styles(self):
        self.setStyleSheet(f"""
            QWidget#central_widget {{ background-color: {C['bg_main']}; }}
            QStackedWidget#main_stack {{ background-color: {C['bg_main']}; border: none; }}
        """)

    def set_user(self, display_name: str):
        self.setWindowTitle(f"Stress Predictor – {display_name}")
        self.right_panel.set_user(display_name)

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())