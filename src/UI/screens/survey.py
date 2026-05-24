"""
src/UI/screens/survey.py
------------------------
Màn hình Khảo sát – Thu thập 20 yếu tố đầu vào cho mô hình dự đoán Stress.

Cấu trúc 5 Tab × 4 câu hỏi:
  Tab 1 – Học tập & Áp lực       (anxiety, academic_pressure, study_hours, teacher_relationship)
  Tab 2 – Giấc ngủ & Thể chất    (sleep_quality, sleep_hours, headache, blood_pressure)
  Tab 3 – Sức khoẻ tâm thần      (mental_health, depression, breathe_problem, noise_level)
  Tab 4 – Xã hội & Môi trường    (social_support, peer_pressure, extracurricular, bullying)
  Tab 5 – Sinh lý & Lối sống     (heart_rate, bmi, self_esteem, future_career)

Design: Clinical Light – nhất quán với custom_widgets.py
"""

from __future__ import annotations

from typing import Callable

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QTabWidget, QLabel, QSlider, QSpinBox, QDoubleSpinBox,
    QRadioButton, QButtonGroup, QFrame, QProgressBar,
    QSizePolicy, QFormLayout, QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor

from src.UI.components.custom_widgets import GoldButton, StyledCard

# ---------------------------------------------------------------------------
# Design Tokens
# ---------------------------------------------------------------------------
C = {
    "bg":            "#F8F9FA",
    "white":         "#FFFFFF",
    "accent":        "#007AFF",
    "accent_light":  "#E8F3FF",
    "accent_hover":  "#0062CC",
    "gold":          "#D4AF37",
    "text":          "#212529",
    "muted":         "#6C757D",
    "divider":       "#E9ECEF",
    "card_border":   "#DEE2E6",
    "success":       "#28A745",
    "warning":       "#FFC107",
    "danger":        "#DC3545",
}

TOTAL_QUESTIONS = 20

# ---------------------------------------------------------------------------
# 20 câu hỏi chia theo 5 Tab
# ---------------------------------------------------------------------------
SURVEY_TABS: list[dict] = [
    {
        "tab_label": "📚  Học tập",
        "tab_key":   "academics",
        "questions": [
            {
                "key":     "anxiety_level",
                "label":   "1. Mức độ lo âu khi chuẩn bị cho kỳ thi?",
                "hint":    "1 = Rất bình thản  ·  5 = Cực kỳ lo lắng",
                "widget":  "slider",
                "min": 1, "max": 5, "default": 3,
                "lo": "Bình thản", "hi": "Rất lo",
            },
            {
                "key":     "academic_pressure",
                "label":   "2. Áp lực học tập từ nhà trường / gia đình?",
                "hint":    "1 = Rất nhẹ  ·  5 = Cực kỳ nặng",
                "widget":  "slider",
                "min": 1, "max": 5, "default": 3,
                "lo": "Nhẹ", "hi": "Nặng",
            },
            {
                "key":     "study_hours",
                "label":   "3. Số giờ tự học mỗi ngày?",
                "hint":    "Trung bình trong tuần học",
                "widget":  "spinbox",
                "min": 0, "max": 20, "default": 4, "suffix": " giờ",
            },
            {
                "key":     "teacher_student_relationship",
                "label":   "4. Mối quan hệ với giảng viên / giáo viên?",
                "hint":    "Chất lượng hỗ trợ học thuật bạn nhận được",
                "widget":  "radio",
                "options": ["Rất tệ", "Tệ", "Bình thường", "Tốt", "Rất tốt"],
                "default": 2,
            },
        ],
    },
    {
        "tab_label": "😴  Giấc ngủ",
        "tab_key":   "sleep",
        "questions": [
            {
                "key":     "sleep_quality",
                "label":   "5. Chất lượng giấc ngủ gần đây?",
                "hint":    "1 = Rất tệ (mất ngủ, hay tỉnh)  ·  5 = Rất tốt (sâu giấc)",
                "widget":  "slider",
                "min": 1, "max": 5, "default": 3,
                "lo": "Rất tệ", "hi": "Rất tốt",
            },
            {
                "key":     "sleep_hours",
                "label":   "6. Số giờ ngủ trung bình mỗi đêm?",
                "hint":    "WHO khuyến nghị 7–9 giờ với sinh viên",
                "widget":  "spinbox",
                "min": 0, "max": 14, "default": 7, "suffix": " giờ",
            },
            {
                "key":     "headache",
                "label":   "7. Tần suất đau đầu trong tuần qua?",
                "hint":    "1 = Không đau đầu  ·  5 = Đau đầu mỗi ngày",
                "widget":  "slider",
                "min": 1, "max": 5, "default": 1,
                "lo": "Không", "hi": "Hàng ngày",
            },
            {
                "key":     "blood_pressure",
                "label":   "8. Huyết áp của bạn hiện tại?",
                "hint":    "Tự đánh giá hoặc kết quả đo gần nhất",
                "widget":  "radio",
                "options": ["Thấp", "Bình thường", "Cao"],
                "default": 1,
            },
        ],
    },
    {
        "tab_label": "🧠  Tâm thần",
        "tab_key":   "mental",
        "questions": [
            {
                "key":     "mental_health_history",
                "label":   "9. Bạn có tiền sử vấn đề sức khoẻ tâm thần?",
                "hint":    "Bao gồm rối loạn lo âu, trầm cảm, ADHD…",
                "widget":  "radio",
                "options": ["Không có", "Có"],
                "default": 0,
            },
            {
                "key":     "depression",
                "label":   "10. Mức độ cảm giác buồn bã / tuyệt vọng?",
                "hint":    "1 = Không có  ·  5 = Thường xuyên, kéo dài",
                "widget":  "slider",
                "min": 1, "max": 5, "default": 1,
                "lo": "Không có", "hi": "Thường xuyên",
            },
            {
                "key":     "breathing_problem",
                "label":   "11. Mức độ khó thở / tức ngực khi căng thẳng?",
                "hint":    "1 = Không bao giờ  ·  5 = Rất thường xuyên",
                "widget":  "slider",
                "min": 1, "max": 5, "default": 1,
                "lo": "Không", "hi": "Thường xuyên",
            },
            {
                "key":     "noise_level",
                "label":   "12. Môi trường học tập / sinh sống có ồn ào không?",
                "hint":    "1 = Rất yên tĩnh  ·  5 = Rất ồn ào",
                "widget":  "slider",
                "min": 1, "max": 5, "default": 2,
                "lo": "Yên tĩnh", "hi": "Rất ồn",
            },
        ],
    },
    {
        "tab_label": "🤝  Xã hội",
        "tab_key":   "social",
        "questions": [
            {
                "key":     "social_support",
                "label":   "13. Mức độ hỗ trợ xã hội bạn cảm nhận được?",
                "hint":    "Từ gia đình, bạn bè, thầy cô…",
                "widget":  "slider",
                "min": 1, "max": 5, "default": 3,
                "lo": "Cô đơn", "hi": "Rất được hỗ trợ",
            },
            {
                "key":     "peer_pressure",
                "label":   "14. Áp lực từ bạn bè / nhóm đồng lứa?",
                "hint":    "1 = Không có  ·  5 = Rất lớn",
                "widget":  "slider",
                "min": 1, "max": 5, "default": 2,
                "lo": "Không có", "hi": "Rất lớn",
            },
            {
                "key":     "extracurricular",
                "label":   "15. Số hoạt động ngoại khoá bạn tham gia?",
                "hint":    "CLB, thể thao, tình nguyện, part-time…",
                "widget":  "spinbox",
                "min": 0, "max": 10, "default": 1, "suffix": " hoạt động",
            },
            {
                "key":     "bullying",
                "label":   "16. Bạn có từng bị bắt nạt / quấy rối?",
                "hint":    "1 = Chưa bao giờ  ·  5 = Rất thường xuyên",
                "widget":  "slider",
                "min": 1, "max": 5, "default": 1,
                "lo": "Không", "hi": "Thường xuyên",
            },
        ],
    },
    {
        "tab_label": "💪  Sinh lý",
        "tab_key":   "physiology",
        "questions": [
            {
                "key":     "heart_rate",
                "label":   "17. Nhịp tim lúc nghỉ ngơi (bpm)?",
                "hint":    "Người khoẻ mạnh thường 60–100 bpm",
                "widget":  "spinbox",
                "min": 40, "max": 180, "default": 75, "suffix": " bpm",
            },
            {
                "key":     "bmi",
                "label":   "18. Chỉ số BMI của bạn?",
                "hint":    "BMI = cân nặng (kg) / chiều cao² (m²)",
                "widget":  "dspinbox",
                "min": 10.0, "max": 50.0, "default": 22.0,
                "step": 0.1, "decimals": 1, "suffix": " BMI",
            },
            {
                "key":     "self_esteem",
                "label":   "19. Mức độ tự tin / tự trọng của bạn?",
                "hint":    "1 = Rất thấp (tự ti)  ·  5 = Rất cao (tự tin)",
                "widget":  "slider",
                "min": 1, "max": 5, "default": 3,
                "lo": "Rất thấp", "hi": "Rất cao",
            },
            {
                "key":     "future_career_concerns",
                "label":   "20. Lo lắng về tương lai nghề nghiệp?",
                "hint":    "1 = Không lo  ·  5 = Lo lắng rất nhiều",
                "widget":  "slider",
                "min": 1, "max": 5, "default": 3,
                "lo": "Không lo", "hi": "Rất lo",
            },
        ],
    },
]


# ===========================================================================
# CSS helpers
# ===========================================================================

_SLIDER_CSS = f"""
    QSlider::groove:horizontal {{
        height: 6px;
        background: {C['divider']};
        border-radius: 3px;
    }}
    QSlider::sub-page:horizontal {{
        background: {C['accent']};
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {C['white']};
        border: 2px solid {C['accent']};
        width: 18px; height: 18px;
        margin: -6px 0;
        border-radius: 9px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {C['accent_light']};
    }}
"""

_SPINBOX_CSS = f"""
    QSpinBox, QDoubleSpinBox {{
        background: {C['white']};
        color: {C['text']};
        border: 1.5px solid {C['card_border']};
        border-radius: 8px;
        padding: 6px 10px;
        font-family: 'Segoe UI';
        font-size: 10pt;
        min-width: 110px;
    }}
    QSpinBox:focus, QDoubleSpinBox:focus {{
        border-color: {C['accent']};
    }}
    QSpinBox::up-button, QDoubleSpinBox::up-button {{
        border-left: 1px solid {C['divider']};
        border-bottom: 1px solid {C['divider']};
        border-top-right-radius: 7px;
        width: 22px;
    }}
    QSpinBox::down-button, QDoubleSpinBox::down-button {{
        border-left: 1px solid {C['divider']};
        border-bottom-right-radius: 7px;
        width: 22px;
    }}
"""

_RADIO_CSS = f"""
    QRadioButton {{
        color: {C['text']};
        background: transparent;
        spacing: 6px;
        font-family: 'Segoe UI';
        font-size: 9pt;
    }}
    QRadioButton::indicator {{
        width: 16px; height: 16px;
        border: 2px solid {C['card_border']};
        border-radius: 8px;
        background: {C['white']};
    }}
    QRadioButton::indicator:checked {{
        background: {C['accent']};
        border-color: {C['accent']};
    }}
    QRadioButton::indicator:hover {{
        border-color: {C['accent']};
    }}
"""

_TAB_CSS = f"""
    QTabWidget::pane {{
        border: 1px solid {C['divider']};
        border-radius: 10px;
        background: {C['white']};
        top: -1px;
    }}
    QTabBar::tab {{
        background: transparent;
        color: {C['muted']};
        font-family: 'Segoe UI';
        font-size: 9pt;
        padding: 9px 18px;
        border: 1px solid transparent;
        border-bottom: none;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background: {C['white']};
        color: {C['accent']};
        font-weight: 600;
        border-color: {C['divider']};
        border-bottom-color: {C['white']};
    }}
    QTabBar::tab:hover:!selected {{
        background: {C['accent_light']};
        color: {C['accent']};
    }}
"""

_PROGRESS_CSS = f"""
    QProgressBar {{
        background: {C['divider']};
        border: none;
        border-radius: 5px;
        height: 10px;
        text-align: center;
        font-size: 0pt;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(
            x1:0, y1:0, x2:1, y2:0,
            stop:0 {C['accent']}, stop:1 #34AADC
        );
        border-radius: 5px;
    }}
"""


# ===========================================================================
# QuestionCard – widget cho một câu hỏi
# ===========================================================================
class QuestionCard(QFrame):
    """
    Card bọc 1 câu hỏi khảo sát.

    Hỗ trợ widget: 'slider' · 'spinbox' · 'dspinbox' · 'radio'
    Signal first_touch(key) phát ra khi người dùng lần đầu tương tác.
    """

    first_touch = pyqtSignal(str)

    def __init__(self, q_def: dict, parent: QWidget | None = None):
        super().__init__(parent)
        self.q = q_def
        self._touched = False

        # Control references
        self.slider: QSlider | None = None
        self.spinbox: QSpinBox | None = None
        self.dspinbox: QDoubleSpinBox | None = None
        self.radio_group: QButtonGroup | None = None
        self._val_badge: QLabel | None = None

        self._build_ui()
        self._apply_card_style()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        # ── Question label ────────────────────────────────────────────
        q_lbl = QLabel(self.q["label"])
        q_lbl.setFont(QFont("Segoe UI Semibold", 10))
        q_lbl.setStyleSheet(f"color: {C['text']}; background: transparent;")
        q_lbl.setWordWrap(True)
        root.addWidget(q_lbl)

        # ── Hint ──────────────────────────────────────────────────────
        if hint := self.q.get("hint"):
            h_lbl = QLabel(hint)
            h_lbl.setFont(QFont("Segoe UI", 8))
            h_lbl.setStyleSheet(f"color: {C['muted']}; background: transparent;")
            root.addWidget(h_lbl)

        # ── Input widget ──────────────────────────────────────────────
        w = self.q["widget"]
        if w == "slider":
            root.addLayout(self._make_slider())
        elif w == "spinbox":
            root.addLayout(self._make_spinbox())
        elif w == "dspinbox":
            root.addLayout(self._make_dspinbox())
        elif w == "radio":
            root.addLayout(self._make_radio())

    # ------------------------------------------------------------------
    def _make_slider(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        lo = QLabel(self.q.get("lo", "Thấp"))
        lo.setFont(QFont("Segoe UI", 8))
        lo.setStyleSheet(f"color: {C['muted']}; background: transparent;")

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(self.q["min"], self.q["max"])
        self.slider.setValue(self.q.get("default", self.q["min"]))
        self.slider.setStyleSheet(_SLIDER_CSS)
        self.slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        hi = QLabel(self.q.get("hi", "Cao"))
        hi.setFont(QFont("Segoe UI", 8))
        hi.setStyleSheet(f"color: {C['muted']}; background: transparent;")

        # Value badge
        self._val_badge = QLabel(str(self.slider.value()))
        self._val_badge.setFixedSize(32, 24)
        self._val_badge.setAlignment(Qt.AlignCenter)
        self._val_badge.setFont(QFont("Segoe UI Semibold", 9))
        self._val_badge.setStyleSheet(f"""
            background: {C['accent']};
            color: {C['white']};
            border-radius: 6px;
        """)

        def _on_change(v: int):
            self._val_badge.setText(str(v))
            self._mark()

        self.slider.valueChanged.connect(_on_change)

        row.addWidget(lo)
        row.addWidget(self.slider, 1)
        row.addWidget(hi)
        row.addWidget(self._val_badge)
        return row

    # ------------------------------------------------------------------
    def _make_spinbox(self) -> QHBoxLayout:
        row = QHBoxLayout()
        self.spinbox = QSpinBox()
        self.spinbox.setRange(self.q["min"], self.q["max"])
        self.spinbox.setValue(self.q.get("default", 0))
        self.spinbox.setSuffix(self.q.get("suffix", ""))
        self.spinbox.setStyleSheet(_SPINBOX_CSS)
        self.spinbox.setFixedWidth(150)
        self.spinbox.valueChanged.connect(lambda _: self._mark())
        row.addWidget(self.spinbox)
        row.addStretch()
        return row

    # ------------------------------------------------------------------
    def _make_dspinbox(self) -> QHBoxLayout:
        row = QHBoxLayout()
        self.dspinbox = QDoubleSpinBox()
        self.dspinbox.setRange(self.q["min"], self.q["max"])
        self.dspinbox.setValue(self.q.get("default", 0.0))
        self.dspinbox.setSuffix(self.q.get("suffix", ""))
        self.dspinbox.setSingleStep(self.q.get("step", 0.1))
        self.dspinbox.setDecimals(self.q.get("decimals", 1))
        self.dspinbox.setStyleSheet(_SPINBOX_CSS)
        self.dspinbox.setFixedWidth(150)
        self.dspinbox.valueChanged.connect(lambda _: self._mark())
        row.addWidget(self.dspinbox)
        row.addStretch()
        return row

    # ------------------------------------------------------------------
    def _make_radio(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(16)
        self.radio_group = QButtonGroup(self)
        default_idx = self.q.get("default", 0)
        for i, text in enumerate(self.q["options"]):
            rb = QRadioButton(text)
            rb.setStyleSheet(_RADIO_CSS)
            if i == default_idx:
                rb.setChecked(True)
            self.radio_group.addButton(rb, i)
            rb.toggled.connect(lambda checked: self._mark() if checked else None)
            row.addWidget(rb)
        row.addStretch()
        return row

    # ------------------------------------------------------------------
    def _mark(self):
        if not self._touched:
            self._touched = True
            self.first_touch.emit(self.q["key"])

    # ------------------------------------------------------------------
    def get_value(self) -> float:
        w = self.q["widget"]
        if w == "slider"  and self.slider:
            return float(self.slider.value())
        if w == "spinbox" and self.spinbox:
            return float(self.spinbox.value())
        if w == "dspinbox" and self.dspinbox:
            return float(self.dspinbox.value())
        if w == "radio" and self.radio_group:
            return float(self.radio_group.checkedId())
        return 0.0

    # ------------------------------------------------------------------
    def reset(self):
        self._touched = False
        w = self.q["widget"]
        if w == "slider" and self.slider:
            self.slider.setValue(self.q.get("default", self.q["min"]))
        elif w == "spinbox" and self.spinbox:
            self.spinbox.setValue(self.q.get("default", 0))
        elif w == "dspinbox" and self.dspinbox:
            self.dspinbox.setValue(self.q.get("default", 0.0))
        elif w == "radio" and self.radio_group:
            btn = self.radio_group.button(self.q.get("default", 0))
            if btn:
                btn.setChecked(True)

    # ------------------------------------------------------------------
    def _apply_card_style(self):
        self.setObjectName("q_card")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(0, 0, 0, 18))
        shadow.setBlurRadius(14)
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        self.setStyleSheet("""
            QFrame#q_card {
                background: white;
                border: 1px solid #DEE2E6;
                border-radius: 12px;
            }
        """)


# ===========================================================================
# SurveyScreen
# ===========================================================================
class SurveyScreen(QWidget):
    """
    Màn hình Khảo sát chính.

    Signal:
      survey_submitted(list[float])  – phát ra khi người dùng bấm Submit,
                                       chứa mảng 20 giá trị float theo thứ tự
                                       định nghĩa trong SURVEY_TABS.
    """

    survey_submitted = pyqtSignal(list)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._cards: list[QuestionCard] = []
        self._touched_keys: set[str] = set()
        self._build_ui()
        self._apply_base_styles()
        self._refresh_footer()

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 20)
        root.setSpacing(16)

        # ── Page header ───────────────────────────────────────────────
        root.addLayout(self._make_header())

        # ── Tab widget ────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(_TAB_CSS)
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        for tab_def in SURVEY_TABS:
            tab_widget = self._make_tab(tab_def)
            self.tabs.addTab(tab_widget, tab_def["tab_label"])

        root.addWidget(self.tabs, 1)

        # ── Footer ────────────────────────────────────────────────────
        root.addWidget(self._make_footer())

    # ------------------------------------------------------------------
    def _make_header(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        icon = QLabel("📋")
        icon.setFont(QFont("Segoe UI", 18))
        icon.setStyleSheet("background: transparent;")

        title = QLabel("Bộ câu hỏi đánh giá mức độ Stress")
        title.setFont(QFont("Segoe UI Semibold", 13))
        title.setStyleSheet(f"color: {C['text']}; background: transparent;")

        sub = QLabel("Vui lòng hoàn thành tất cả 20 câu hỏi để nhận kết quả chính xác nhất.")
        sub.setFont(QFont("Segoe UI", 9))
        sub.setStyleSheet(f"color: {C['muted']}; background: transparent;")
        sub.setWordWrap(True)

        txt_col = QVBoxLayout()
        txt_col.setSpacing(2)
        txt_col.addWidget(title)
        txt_col.addWidget(sub)

        row.addWidget(icon)
        row.addLayout(txt_col, 1)
        return row

    # ------------------------------------------------------------------
    def _make_tab(self, tab_def: dict) -> QWidget:
        """Tạo 1 tab với QScrollArea bọc 4 QuestionCard."""
        outer = QWidget()
        outer.setStyleSheet(f"background: {C['white']};")

        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"background: {C['white']}; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setStyleSheet(f"background: {C['white']};")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Tab description badge
        desc = QLabel(f"Nhóm: {tab_def['tab_label'].split('  ')[-1]} — 4 câu hỏi")
        desc.setFont(QFont("Segoe UI", 8))
        desc.setStyleSheet(f"""
            background: {C['accent_light']};
            color: {C['accent']};
            border-radius: 6px;
            padding: 4px 10px;
        """)
        desc.setFixedHeight(26)
        layout.addWidget(desc)

        for q_def in tab_def["questions"]:
            card = QuestionCard(q_def)
            card.first_touch.connect(self._on_first_touch)
            self._cards.append(card)
            layout.addWidget(card)

        layout.addStretch()
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)
        return outer

    # ------------------------------------------------------------------
    def _make_footer(self) -> QFrame:
        footer = QFrame()
        footer.setObjectName("survey_footer")
        footer.setStyleSheet(f"""
            QFrame#survey_footer {{
                background: {C['white']};
                border: 1px solid {C['divider']};
                border-radius: 12px;
            }}
        """)

        fl = QVBoxLayout(footer)
        fl.setContentsMargins(20, 14, 20, 14)
        fl.setSpacing(10)

        # ── Progress row ──────────────────────────────────────────────
        prog_row = QHBoxLayout()
        prog_row.setSpacing(12)

        prog_icon = QLabel("📊")
        prog_icon.setFont(QFont("Segoe UI", 10))
        prog_icon.setStyleSheet("background: transparent;")

        prog_col = QVBoxLayout()
        prog_col.setSpacing(4)

        lbl_row = QHBoxLayout()
        prog_txt = QLabel("Tiến độ hoàn thành")
        prog_txt.setFont(QFont("Segoe UI", 9))
        prog_txt.setStyleSheet(f"color: {C['text']}; background: transparent;")

        self._prog_lbl = QLabel("0 / 20 câu")
        self._prog_lbl.setFont(QFont("Segoe UI Semibold", 9))
        self._prog_lbl.setStyleSheet(f"color: {C['accent']}; background: transparent;")

        lbl_row.addWidget(prog_txt)
        lbl_row.addStretch()
        lbl_row.addWidget(self._prog_lbl)

        self._prog_bar = QProgressBar()
        self._prog_bar.setRange(0, TOTAL_QUESTIONS)
        self._prog_bar.setValue(0)
        self._prog_bar.setFixedHeight(10)
        self._prog_bar.setStyleSheet(_PROGRESS_CSS)

        prog_col.addLayout(lbl_row)
        prog_col.addWidget(self._prog_bar)

        prog_row.addWidget(prog_icon)
        prog_row.addLayout(prog_col, 1)
        fl.addLayout(prog_row)

        # ── Submit button ─────────────────────────────────────────────
        self._submit_btn = GoldButton(
            "🔍  Gửi câu trả lời để phân tích  →",
            height=52,
        )
        self._submit_btn.setEnabled(False)
        self._submit_btn.clicked.connect(self._on_submit)
        fl.addWidget(self._submit_btn)

        # Hint text
        hint = QLabel("⚠  Hãy hoàn thành tất cả 20 câu hỏi trước khi gửi.")
        hint.setFont(QFont("Segoe UI", 8))
        hint.setStyleSheet(f"color: {C['muted']}; background: transparent;")
        hint.setAlignment(Qt.AlignCenter)
        self._hint_lbl = hint
        fl.addWidget(hint)

        return footer

    # ------------------------------------------------------------------
    # Slots & helpers
    # ------------------------------------------------------------------
    def _on_first_touch(self, key: str):
        self._touched_keys.add(key)
        self._refresh_footer()

    def _refresh_footer(self):
        n = len(self._touched_keys)
        self._prog_lbl.setText(f"{n} / {TOTAL_QUESTIONS} câu")
        self._prog_bar.setValue(n)
        ready = (n == TOTAL_QUESTIONS)
        self._submit_btn.setEnabled(ready)
        self._hint_lbl.setVisible(not ready)

    def _on_submit(self):
        payload = self.get_payload()
        print("[SurveyScreen] Payload:", payload)
        self.survey_submitted.emit(payload)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_payload(self) -> list[float]:
        """
        Trả về mảng 20 giá trị float theo thứ tự:
          [anxiety_level, academic_pressure, study_hours, teacher_student_relationship,
           sleep_quality, sleep_hours, headache, blood_pressure,
           mental_health_history, depression, breathing_problem, noise_level,
           social_support, peer_pressure, extracurricular, bullying,
           heart_rate, bmi, self_esteem, future_career_concerns]
        """
        return [card.get_value() for card in self._cards]

    def reset(self):
        """Reset toàn bộ câu hỏi về giá trị mặc định."""
        self._touched_keys.clear()
        for card in self._cards:
            card.reset()
        self._refresh_footer()

    # ------------------------------------------------------------------
    def _apply_base_styles(self):
        self.setStyleSheet(f"QWidget {{ background: {C['bg']}; }}")