"""
src/ui/screens/survey.py
------------------------
Màn hình Khảo sát – Thu thập 20 yếu tố đầu vào cho mô hình dự đoán Stress.

Cấu trúc 5 Tab x 4 câu hỏi / tab:
  Tab 0 – Tâm lý & Cảm xúc
  Tab 1 – Sinh lý & Sức khỏe
  Tab 2 – Môi trường & Điều kiện
  Tab 3 – Học thuật & Tương lai
  Tab 4 – Hành vi & Xã hội

API Contract output – list[float], 20 phần tử, thứ tự chuẩn:
  [anxiety, self_esteem, mental_health_history, depression,
   headache, blood_pressure, sleep_quality, breathing_problem,
   noise_level, living_conditions, safety, basic_needs,
   academic_performance, study_load, teacher_student_relationship, future_career,
   social_support, peer_pressure, extracurricular, bullying]

Cải tiến v2:
  - set[str] đếm câu đã chạm (tránh đếm trùng khi slider thay đổi nhiều lần)
  - Progress bar đổi màu theo 3 ngưỡng: xám / vàng->xanh / xanh lá
  - Submit button disabled khi chưa đủ 20 câu + tooltip hướng dẫn
  - reset() public để MainWindow có thể tái sử dụng form
"""

from __future__ import annotations
from typing import Callable

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QTabWidget, QLabel, QSlider, QSpinBox, QRadioButton,
    QButtonGroup, QFrame, QProgressBar, QPushButton, QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

# ---------------------------------------------------------------------------
# Design Tokens – Clinical Light
# ---------------------------------------------------------------------------
C = {
    "bg":           "#F8F9FA",
    "white":        "#FFFFFF",
    "accent":       "#007AFF",
    "accent_light": "#E8F3FF",
    "accent_hover": "#0062CC",
    "text":         "#212529",
    "muted":        "#6C757D",
    "divider":      "#E9ECEF",
    "card_border":  "#DEE2E6",
    "success":      "#28A745",
    "warning":      "#FFC107",
}

TOTAL_QUESTIONS = 20  # 5 tabs x 4 câu


# ---------------------------------------------------------------------------
# Định nghĩa 20 câu hỏi (thứ tự == API Contract)
# ---------------------------------------------------------------------------
TABS_DEF: list[dict] = [
    {
        "title": "🧠  Tâm lý & Cảm xúc",
        "questions": [
            {
                "key": "anxiety",
                "label": "1.  Mức độ lo lắng / căng thẳng tâm lý hiện tại của bạn?",
                "widget": "slider", "min": 1, "max": 5, "default": 3,
            },
            {
                "key": "self_esteem",
                "label": "2.  Bạn đánh giá mức độ tự tin vào bản thân như thế nào?",
                "widget": "slider", "min": 1, "max": 5, "default": 3,
            },
            {
                "key": "mental_health_history",
                "label": "3.  Bạn có tiền sử vấn đề sức khỏe tâm thần không?",
                "widget": "radio",
                "options": ["Không có", "Nhẹ / đã ổn định", "Đang điều trị"],
                "default": 0,
            },
            {
                "key": "depression",
                "label": "4.  Mức độ cảm giác chán nản / trầm cảm trong 2 tuần qua?",
                "widget": "slider", "min": 1, "max": 5, "default": 2,
            },
        ],
    },
    {
        "title": "❤️  Sinh lý & Sức khỏe",
        "questions": [
            {
                "key": "headache",
                "label": "5.  Tần suất đau đầu trong tuần qua (số lần / tuần)?",
                "widget": "spinbox", "min": 0, "max": 14, "suffix": " lần/tuần", "default": 1,
            },
            {
                "key": "blood_pressure",
                "label": "6.  Huyết áp của bạn ở mức nào?",
                "widget": "radio",
                "options": ["Thấp  (< 90/60)", "Bình thường", "Cao  (> 130/80)"],
                "default": 1,
            },
            {
                "key": "sleep_quality",
                "label": "7.  Số giờ ngủ trung bình mỗi đêm?",
                "widget": "spinbox", "min": 2, "max": 12, "suffix": " giờ/đêm", "default": 7,
            },
            {
                "key": "breathing_problem",
                "label": "8.  Mức độ khó thở / tức ngực bạn trải qua?",
                "widget": "slider", "min": 1, "max": 5, "default": 1,
            },
        ],
    },
    {
        "title": "🏠  Môi trường & Điều kiện",
        "questions": [
            {
                "key": "noise_level",
                "label": "9.  Mức độ ồn ào / xao nhãng trong môi trường học tập / sống?",
                "widget": "slider", "min": 1, "max": 5, "default": 3,
            },
            {
                "key": "living_conditions",
                "label": "10. Điều kiện nơi ở / học tập của bạn hiện tại?",
                "widget": "radio",
                "options": ["Kém", "Trung bình", "Tốt", "Rất tốt"],
                "default": 2,
            },
            {
                "key": "safety",
                "label": "11. Bạn cảm thấy an toàn trong môi trường học / sinh sống?",
                "widget": "slider", "min": 1, "max": 5, "default": 4,
            },
            {
                "key": "basic_needs",
                "label": "12. Nhu cầu cơ bản (ăn, uống, ngủ) được đáp ứng ở mức nào?",
                "widget": "slider", "min": 1, "max": 5, "default": 4,
            },
        ],
    },
    {
        "title": "🎓  Học thuật & Tương lai",
        "questions": [
            {
                "key": "academic_performance",
                "label": "13. Bạn tự đánh giá kết quả học tập hiện tại của mình?",
                "widget": "slider", "min": 1, "max": 5, "default": 3,
            },
            {
                "key": "study_load",
                "label": "14. Số giờ học / ôn tập trung bình mỗi ngày?",
                "widget": "spinbox", "min": 0, "max": 16, "suffix": " giờ/ngày", "default": 4,
            },
            {
                "key": "teacher_student_relationship",
                "label": "15. Mối quan hệ với giảng viên / giáo viên của bạn?",
                "widget": "slider", "min": 1, "max": 5, "default": 3,
            },
            {
                "key": "future_career",
                "label": "16. Mức độ lo lắng về định hướng nghề nghiệp tương lai?",
                "widget": "slider", "min": 1, "max": 5, "default": 3,
            },
        ],
    },
    {
        "title": "🤝  Hành vi & Xã hội",
        "questions": [
            {
                "key": "social_support",
                "label": "17. Mức độ hỗ trợ từ gia đình / bạn bè bạn nhận được?",
                "widget": "slider", "min": 1, "max": 5, "default": 3,
            },
            {
                "key": "peer_pressure",
                "label": "18. Áp lực từ bạn bè / đồng lứa mà bạn cảm nhận?",
                "widget": "slider", "min": 1, "max": 5, "default": 2,
            },
            {
                "key": "extracurricular",
                "label": "19. Số lượng hoạt động ngoại khoá / câu lạc bộ bạn tham gia?",
                "widget": "spinbox", "min": 0, "max": 10, "suffix": " hoạt động", "default": 1,
            },
            {
                "key": "bullying",
                "label": "20. Bạn có từng bị bắt nạt / phân biệt đối xử không?",
                "widget": "radio",
                "options": ["Chưa bao giờ", "Hiếm khi", "Đôi khi", "Thường xuyên"],
                "default": 0,
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# CSS constants (module-level – tránh tạo lại mỗi lần __init__)
# ---------------------------------------------------------------------------
_SLIDER_CSS = (
    "QSlider::groove:horizontal {"
    f"height:6px; background:{C['divider']}; border-radius:3px;"
    "}"
    "QSlider::sub-page:horizontal {"
    f"background:{C['accent']}; border-radius:3px;"
    "}"
    "QSlider::handle:horizontal {"
    f"background:{C['white']}; border:2px solid {C['accent']};"
    "width:18px; height:18px; margin:-6px 0; border-radius:9px;"
    "}"
    "QSlider::handle:horizontal:hover {"
    f"background:{C['accent_light']};"
    "}"
)

_SPINBOX_CSS = (
    "QSpinBox {"
    f"background:{C['white']}; color:{C['text']};"
    f"border:1.5px solid {C['card_border']};"
    "border-radius:8px; padding:6px 10px;"
    "}"
    f"QSpinBox:focus {{ border-color:{C['accent']}; }}"
    "QSpinBox::up-button, QSpinBox::down-button {"
    f"width:22px; background:{C['bg']}; border:none; border-radius:4px;"
    "}"
    "QSpinBox::up-button:hover, QSpinBox::down-button:hover {"
    f"background:{C['accent_light']};"
    "}"
)

_RADIO_CSS = (
    f"QRadioButton {{ color:{C['text']}; background:transparent; spacing:6px; }}"
    "QRadioButton::indicator {"
    "width:16px; height:16px;"
    f"border:2px solid {C['card_border']}; border-radius:8px;"
    f"background:{C['white']};"
    "}"
    "QRadioButton::indicator:checked {"
    f"background:{C['accent']}; border-color:{C['accent']};"
    "}"
    f"QRadioButton::indicator:hover {{ border-color:{C['accent']}; }}"
)

_SUBMIT_DISABLED_CSS = (
    "QPushButton {"
    f"background:{C['card_border']}; color:{C['muted']};"
    "border:none; border-radius:12px;"
    "font-family:'Segoe UI Semibold'; font-size:11pt;"
    "}"
)

_SUBMIT_ENABLED_CSS = (
    "QPushButton {"
    "background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
    f"stop:0 {C['accent']},stop:1 #34AADC);"
    f"color:{C['white']}; border:none; border-radius:12px;"
    "font-family:'Segoe UI Semibold'; font-size:11pt; letter-spacing:0.3px;"
    "}"
    "QPushButton:hover {"
    "background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
    f"stop:0 {C['accent_hover']},stop:1 {C['accent']});"
    "}"
    "QPushButton:pressed { padding-top:2px; }"
)


# ===========================================================================
# QuestionCard – widget bọc một câu hỏi đơn lẻ
# ===========================================================================
class QuestionCard(QFrame):
    """
    Card hiển thị một câu hỏi.
    Signal first_touch(key) phát đúng một lần khi người dùng tương tác
    lần đầu – SurveyScreen dùng để tính tiến độ.
    """
    first_touch = pyqtSignal(str)   # payload = key của câu hỏi

    def __init__(self, q_def: dict, parent: QWidget | None = None):
        super().__init__(parent)
        self.q            = q_def
        self._touched     = False

        # Tham chiếu widget nhập liệu (dùng cho get_value / reset)
        self.slider      : QSlider      | None = None
        self.spinbox     : QSpinBox     | None = None
        self.radio_group : QButtonGroup | None = None
        self._val_lbl    : QLabel       | None = None   # live value badge (slider)

        self._build_ui()
        self._apply_card_style()

    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(10)

        lbl = QLabel(self.q["label"])
        lbl.setFont(QFont("Segoe UI", 10))
        lbl.setStyleSheet("color:%s; background:transparent;" % C["text"])
        lbl.setWordWrap(True)
        root.addWidget(lbl)

        w = self.q["widget"]
        if   w == "slider":  root.addLayout(self._make_slider())
        elif w == "spinbox": root.addLayout(self._make_spinbox())
        elif w == "radio":   root.addLayout(self._make_radio())

    # ── Slider ────────────────────────────────────────────────────────
    def _make_slider(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        lo = QLabel("Thấp")
        lo.setFont(QFont("Segoe UI", 8))
        lo.setStyleSheet("color:%s; background:transparent;" % C["muted"])

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(self.q["min"], self.q["max"])
        self.slider.setValue(self.q.get("default", self.q["min"]))
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.slider.setStyleSheet(_SLIDER_CSS)

        self._val_lbl = QLabel(str(self.slider.value()))
        self._val_lbl.setFont(QFont("Segoe UI Semibold", 10))
        self._val_lbl.setFixedWidth(32)
        self._val_lbl.setAlignment(Qt.AlignCenter)
        self._val_lbl.setStyleSheet(
            "color:%s; background:%s; border-radius:6px; padding:1px 4px;"
            % (C["accent"], C["accent_light"])
        )

        hi = QLabel("Cao")
        hi.setFont(QFont("Segoe UI", 8))
        hi.setStyleSheet("color:%s; background:transparent;" % C["muted"])

        def _on_change(v: int):
            self._val_lbl.setText(str(v))
            self._mark()

        self.slider.valueChanged.connect(_on_change)

        row.addWidget(lo)
        row.addWidget(self.slider, stretch=1)
        row.addWidget(hi)
        row.addWidget(self._val_lbl)
        return row

    # ── SpinBox ───────────────────────────────────────────────────────
    def _make_spinbox(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(12)

        self.spinbox = QSpinBox()
        self.spinbox.setRange(self.q["min"], self.q["max"])
        self.spinbox.setValue(self.q.get("default", self.q["min"]))
        self.spinbox.setSuffix(self.q.get("suffix", ""))
        self.spinbox.setFont(QFont("Segoe UI", 11))
        self.spinbox.setFixedWidth(170)
        self.spinbox.setStyleSheet(_SPINBOX_CSS)
        self.spinbox.valueChanged.connect(lambda _v: self._mark())

        hint = QLabel(
            "(từ %d → %d%s)" % (self.q["min"], self.q["max"], self.q.get("suffix", ""))
        )
        hint.setFont(QFont("Segoe UI", 8))
        hint.setStyleSheet("color:%s; background:transparent;" % C["muted"])

        row.addWidget(self.spinbox)
        row.addWidget(hint)
        row.addStretch()
        return row

    # ── Radio ─────────────────────────────────────────────────────────
    def _make_radio(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(16)
        self.radio_group = QButtonGroup(self)
        default_idx = self.q.get("default", 0)

        for i, text in enumerate(self.q["options"]):
            rb = QRadioButton(text)
            rb.setFont(QFont("Segoe UI", 9))
            rb.setStyleSheet(_RADIO_CSS)
            if i == default_idx:
                rb.setChecked(True)
            self.radio_group.addButton(rb, i)
            # toggled fires for both check and uncheck; only count checks
            rb.toggled.connect(lambda checked, _=None: self._mark() if checked else None)
            row.addWidget(rb)

        row.addStretch()
        return row

    # ── State helpers ─────────────────────────────────────────────────
    def _mark(self):
        """Phát signal first_touch đúng một lần."""
        if not self._touched:
            self._touched = True
            self.first_touch.emit(self.q["key"])

    # ── Public API ────────────────────────────────────────────────────
    def get_value(self) -> float:
        """Trả về giá trị hiện tại dưới dạng float."""
        w = self.q["widget"]
        if w == "slider":  return float(self.slider.value())
        if w == "spinbox": return float(self.spinbox.value())
        if w == "radio":   return float(self.radio_group.checkedId() + 1)
        return 0.0

    def reset(self):
        """Khôi phục về giá trị mặc định và xoá trạng thái touched."""
        self._touched = False
        w    = self.q["widget"]
        dflt = self.q.get("default", self.q.get("min", 0))

        if w == "slider":
            self.slider.blockSignals(True)
            self.slider.setValue(dflt)
            self.slider.blockSignals(False)
            self._val_lbl.setText(str(dflt))

        elif w == "spinbox":
            self.spinbox.blockSignals(True)
            self.spinbox.setValue(dflt)
            self.spinbox.blockSignals(False)

        elif w == "radio":
            btn = self.radio_group.button(dflt)
            if btn:
                btn.blockSignals(True)
                btn.setChecked(True)
                btn.blockSignals(False)

    # ── Style ─────────────────────────────────────────────────────────
    def _apply_card_style(self):
        self.setObjectName("q_card")
        self.setStyleSheet(
            "QFrame#q_card {"
            "background:%s; border:1.5px solid %s; border-radius:12px;"
            "}"
            "QFrame#q_card:hover { border-color:%s; }"
            % (C["white"], C["card_border"], C["accent"])
        )


# ===========================================================================
# _build_tab – tạo nội dung một Tab (QScrollArea + 4 QuestionCard)
# ===========================================================================
def _build_tab(
    tab_def: dict,
    cards_out: list,
    on_first_touch: Callable[[str], None],
) -> QWidget:
    """
    Trả về QWidget dùng làm nội dung Tab.
    4 QuestionCard được append vào cards_out theo đúng thứ tự API Contract.
    """
    wrapper = QWidget()
    wrapper.setStyleSheet("background:%s;" % C["bg"])
    wl = QVBoxLayout(wrapper)
    wl.setContentsMargins(0, 0, 0, 0)

    # QScrollArea – chống tràn màn hình
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QFrame.NoFrame)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setStyleSheet(
        "QScrollArea { background:%s; border:none; }"
        "QScrollBar:vertical { background:%s; width:6px; border-radius:3px; margin:0; }"
        "QScrollBar::handle:vertical { background:%s; border-radius:3px; min-height:24px; }"
        "QScrollBar::handle:vertical:hover { background:%s; }"
        "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }"
        % (C["bg"], C["bg"], C["card_border"], C["accent"])
    )

    inner = QWidget()
    inner.setStyleSheet("background:%s;" % C["bg"])
    il = QVBoxLayout(inner)
    il.setContentsMargins(24, 20, 24, 20)
    il.setSpacing(14)

    for q_def in tab_def["questions"]:
        card = QuestionCard(q_def)
        card.first_touch.connect(on_first_touch)
        il.addWidget(card)
        cards_out.append(card)

    il.addStretch()
    scroll.setWidget(inner)
    wl.addWidget(scroll)
    return wrapper


# ===========================================================================
# SurveyScreen – màn hình chính
# ===========================================================================
class SurveyScreen(QWidget):
    """
    Màn hình Khảo sát hoàn chỉnh.

    Signals
    -------
    survey_submitted(list[float])
        Phát sau khi người dùng nhấn nút Gửi.
        Payload: mảng 20 float theo đúng thứ tự API Contract.
    """
    survey_submitted = pyqtSignal(list)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # list[QuestionCard] – 20 phần tử, thứ tự == API Contract
        self._cards: list[QuestionCard] = []

        # set[str] – key các câu đã được người dùng chạm ít nhất 1 lần
        # Dùng set để tránh đếm trùng (slider valueChanged có thể fire nhiều lần)
        self._touched_keys: set[str] = set()

        self._build_ui()
        self._apply_base_styles()
        self._refresh_footer()   # khởi tạo trạng thái ban đầu

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._make_header())

        self.tabs = QTabWidget()
        self.tabs.setObjectName("survey_tabs")
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        for tab_def in TABS_DEF:
            content = _build_tab(tab_def, self._cards, self._on_first_touch)
            self.tabs.addTab(content, tab_def["title"])

        root.addWidget(self.tabs, stretch=1)
        root.addWidget(self._make_footer())

    # ------------------------------------------------------------------
    def _make_header(self) -> QFrame:
        h = QFrame()
        h.setObjectName("survey_header")
        hl = QVBoxLayout(h)
        hl.setContentsMargins(28, 22, 28, 16)
        hl.setSpacing(5)

        title = QLabel("📋  Bộ câu hỏi đánh giá mức độ Stress")
        title.setFont(QFont("Segoe UI Semibold", 14))
        title.setStyleSheet("color:%s; background:transparent;" % C["text"])

        sub = QLabel(
            "Trả lời trung thực cả %d câu để nhận kết quả phân tích "
            "chính xác nhất.  Dự kiến hoàn thành trong 3 phút." % TOTAL_QUESTIONS
        )
        sub.setFont(QFont("Segoe UI", 9))
        sub.setStyleSheet("color:%s; background:transparent;" % C["muted"])
        sub.setWordWrap(True)

        hl.addWidget(title)
        hl.addWidget(sub)
        return h

    # ------------------------------------------------------------------
    def _make_footer(self) -> QFrame:
        f = QFrame()
        f.setObjectName("survey_footer")
        fl = QVBoxLayout(f)
        fl.setContentsMargins(28, 14, 28, 20)
        fl.setSpacing(12)

        # ── Progress row ──────────────────────────────────────────────
        pr = QHBoxLayout()
        pr.setSpacing(14)

        self._prog_lbl = QLabel("0 / %d câu đã trả lời" % TOTAL_QUESTIONS)
        self._prog_lbl.setFont(QFont("Segoe UI", 9))
        self._prog_lbl.setStyleSheet("color:%s;" % C["muted"])
        self._prog_lbl.setFixedWidth(185)

        self._prog_bar = QProgressBar()
        self._prog_bar.setRange(0, TOTAL_QUESTIONS)
        self._prog_bar.setValue(0)
        self._prog_bar.setTextVisible(False)
        self._prog_bar.setFixedHeight(8)
        self._prog_bar.setObjectName("prog_bar")

        self._pct_lbl = QLabel("0%")
        self._pct_lbl.setFont(QFont("Segoe UI Semibold", 9))
        self._pct_lbl.setFixedWidth(36)
        self._pct_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._pct_lbl.setStyleSheet("color:%s;" % C["muted"])

        pr.addWidget(self._prog_lbl)
        pr.addWidget(self._prog_bar, stretch=1)
        pr.addWidget(self._pct_lbl)
        fl.addLayout(pr)

        # ── Submit button ─────────────────────────────────────────────
        self._submit_btn = QPushButton("  🔍  Gửi câu trả lời để phân tích  →")
        self._submit_btn.setFont(QFont("Segoe UI Semibold", 11))
        self._submit_btn.setFixedHeight(52)
        self._submit_btn.setCursor(Qt.PointingHandCursor)
        self._submit_btn.setObjectName("submit_btn")
        self._submit_btn.setEnabled(False)
        self._submit_btn.setToolTip(
            "Hãy trả lời đủ %d câu hỏi trước khi gửi." % TOTAL_QUESTIONS
        )
        self._submit_btn.clicked.connect(self._on_submit)
        fl.addWidget(self._submit_btn)

        return f

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def _on_first_touch(self, key: str):
        """Nhận signal first_touch từ QuestionCard – cập nhật tiến độ."""
        self._touched_keys.add(key)
        self._refresh_footer()

    def _refresh_footer(self):
        """Cập nhật progress bar, nhãn % và trạng thái Submit."""
        n   = len(self._touched_keys)
        pct = int(n / TOTAL_QUESTIONS * 100)

        self._prog_bar.setValue(n)
        self._prog_lbl.setText("%d / %d câu đã trả lời" % (n, TOTAL_QUESTIONS))
        self._pct_lbl.setText("%d%%" % pct)

        # Màu progress bar theo 3 ngưỡng tiến độ
        if n == TOTAL_QUESTIONS:
            chunk = (
                "background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                "stop:0 %s,stop:1 #20C997);" % C["success"]
            )
            self._pct_lbl.setStyleSheet("color:%s;" % C["success"])
        elif pct >= 66:
            chunk = (
                "background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                "stop:0 %s,stop:1 #34C759);" % C["accent"]
            )
            self._pct_lbl.setStyleSheet("color:%s;" % C["accent"])
        elif pct >= 33:
            chunk = (
                "background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
                "stop:0 %s,stop:1 %s);" % (C["warning"], C["accent"])
            )
            self._pct_lbl.setStyleSheet("color:%s;" % C["warning"])
        else:
            chunk = "background:%s;" % C["card_border"]
            self._pct_lbl.setStyleSheet("color:%s;" % C["muted"])

        self._prog_bar.setStyleSheet(
            "QProgressBar { background:%s; border-radius:4px; border:none; }"
            "QProgressBar::chunk { %s border-radius:4px; }"
            % (C["divider"], chunk)
        )

        # Enable / disable Submit
        ready = (n == TOTAL_QUESTIONS)
        self._submit_btn.setEnabled(ready)
        if ready:
            self._submit_btn.setToolTip("Nhấn để gửi và xem kết quả phân tích.")
            self._submit_btn.setStyleSheet(_SUBMIT_ENABLED_CSS)
        else:
            self._submit_btn.setToolTip(
                "Còn %d câu chưa được trả lời." % (TOTAL_QUESTIONS - n)
            )
            self._submit_btn.setStyleSheet(_SUBMIT_DISABLED_CSS)

    # ------------------------------------------------------------------
    def _on_submit(self):
        """Thu thập 20 giá trị → đóng gói API Contract → phát signal."""
        payload = self.get_payload()

        # Debug log – xoá khi tích hợp module AI
        print("\n" + "=" * 56)
        print("  [SurveyScreen] API Contract payload (20 features)")
        print("=" * 56)
        keys = [q["key"] for tab in TABS_DEF for q in tab["questions"]]
        for k, v in zip(keys, payload):
            print("  %-44s= %s" % (k, v))
        print("=" * 56 + "\n")

        self.survey_submitted.emit(payload)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def get_payload(self) -> list[float]:
        """
        Trả về mảng 20 float theo đúng thứ tự API Contract.
        Có thể gọi bất cứ lúc nào (unit test, tích hợp bên ngoài).
        """
        return [card.get_value() for card in self._cards]

    def reset(self):
        """Đặt lại toàn bộ form về giá trị mặc định."""
        self._touched_keys.clear()
        for card in self._cards:
            card.reset()
        self._refresh_footer()

    # ------------------------------------------------------------------
    # Base styles
    # ------------------------------------------------------------------
    def _apply_base_styles(self):
        self.setStyleSheet(
            "QWidget { background:%s; }"
            "QFrame#survey_header { background:%s; border-bottom:1px solid %s; }"
            "QFrame#survey_footer { background:%s; border-top:1px solid %s; }"
            "QTabWidget#survey_tabs::pane { border:none; background:%s; }"
            "QTabWidget#survey_tabs > QTabBar::tab {"
            "  background:%s; color:%s; font-family:'Segoe UI'; font-size:9pt;"
            "  padding:10px 16px; border:none;"
            "  border-bottom:3px solid transparent; min-width:130px;"
            "}"
            "QTabWidget#survey_tabs > QTabBar::tab:selected {"
            "  color:%s; background:%s;"
            "  border-bottom:3px solid %s; font-weight:600;"
            "}"
            "QTabWidget#survey_tabs > QTabBar::tab:hover:!selected {"
            "  color:%s; background:%s;"
            "}"
            % (
                C["bg"],
                C["white"], C["divider"],
                C["white"], C["divider"],
                C["bg"],
                C["bg"], C["muted"],
                C["accent"], C["white"], C["accent"],
                C["text"], C["accent_light"],
            )
        )