from __future__ import annotations

import math
from typing import Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QWidget, QSizePolicy, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
)
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer,
    QSequentialAnimationGroup, QParallelAnimationGroup,
    pyqtSignal, QRect, QPoint,
)
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QPainterPath,
    QLinearGradient, QConicalGradient, QRadialGradient,
)
from src.views.components.widgets import CustomMessageBox
from src.core.config import C  # Gọi chung file Config

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    _MPL_OK = True
except ImportError:
    _MPL_OK = False

# ---------------------------------------------------------------------------
# Thứ tự features (khớp SurveyScreen.get_payload)
# ---------------------------------------------------------------------------
_FEATURE_ORDER = [
    "anxiety_level", "self_esteem", "mental_health_history", "depression",
    "headache", "blood_pressure", "sleep_quality", "breathing_problem",
    "noise_level", "living_conditions", "safety", "basic_needs",
    "academic_performance", "study_load", "teacher_student_relationship",
    "future_career_concerns", "social_support", "peer_pressure",
    "extracurricular_activities", "bullying",
]

# ---------------------------------------------------------------------------
# 3 mức độ stress (class 0, 1, 2) - Lấy màu từ config
# ---------------------------------------------------------------------------
STRESS_LEVELS = {
    0: {
        "label":       "Thấp",
        "sublabel":    "Mức độ stress của bạn nằm trong ngưỡng bình thường",
        "emoji":       "😌",
        "gradient_a":  C["detail_low_a"],
        "gradient_b":  C["detail_low_b"],
        "ring_color":  C["detail_low_a"],
        "tag_bg":      C["detail_low_bg"],
        "tag_text":    C["detail_low_txt"],
        "bar_pct":     28,
        "tips": [
            "🧘 Duy trì thói quen ngủ đủ 7–8 giờ mỗi đêm",
            "🏃 Tập thể dục nhẹ 30 phút mỗi ngày",
            "🤝 Giữ kết nối xã hội với bạn bè và gia đình",
        ],
    },
    1: {
        "label":       "Trung bình",
        "sublabel":    "Bạn đang chịu một mức áp lực đáng chú ý",
        "emoji":       "😐",
        "gradient_a":  C["detail_mid_a"],
        "gradient_b":  C["detail_mid_b"],
        "ring_color":  C["detail_mid_a"],
        "tag_bg":      C["detail_mid_bg"],
        "tag_text":    C["detail_mid_txt"],
        "bar_pct":     58,
        "tips": [
            "🌬️ Thực hành hít thở sâu 4-7-8 mỗi buổi sáng",
            "📋 Lập danh sách ưu tiên để giảm tải công việc",
            "🎯 Dành 30 phút/ngày cho sở thích cá nhân",
            "💬 Chia sẻ lo lắng cùng người thân tin cậy",
        ],
    },
    2: {
        "label":       "Cao",
        "sublabel":    "Mức stress của bạn cần được quan tâm nghiêm túc",
        "emoji":       "😰",
        "gradient_a":  C["detail_high_a"],
        "gradient_b":  C["detail_high_b"],
        "ring_color":  C["detail_high_a"],
        "tag_bg":      C["detail_high_bg"],
        "tag_text":    C["detail_high_txt"],
        "bar_pct":     88,
        "tips": [
            "🏥 Liên hệ chuyên gia tâm lý hoặc cố vấn học tập",
            "📵 Giới hạn mạng xã hội — tối đa 30 phút/ngày",
            "🧘 Thiền định hoặc yoga 15–20 phút mỗi sáng",
            "📓 Viết nhật ký cảm xúc để nhận biết nguồn gốc stress",
            "☎️ Đường dây hỗ trợ: 1800 599 920 (miễn phí 24/7)",
        ],
    },
}

# ---------------------------------------------------------------------------
# 5 nhóm yếu tố cho Radar / Pie
# ---------------------------------------------------------------------------
FACTOR_GROUPS = [
    {"name": "Tâm lý",    "keys": ["anxiety_level","self_esteem","mental_health_history","depression"], "color": C["factor_psy"]},
    {"name": "Thể chất",  "keys": ["headache","blood_pressure","sleep_quality","breathing_problem"],    "color": C["factor_phy"]},
    {"name": "Môi trường","keys": ["noise_level","living_conditions","safety","basic_needs"],           "color": C["factor_env"]},
    {"name": "Học tập",   "keys": ["academic_performance","study_load","teacher_student_relationship","future_career_concerns"], "color": C["factor_edu"]},
    {"name": "Xã hội",    "keys": ["social_support","peer_pressure","extracurricular_activities","bullying"], "color": C["factor_soc"]},
]

_KEY_MAX = {
    "anxiety_level":21,"self_esteem":30,"mental_health_history":1,"depression":27,
    "headache":5,"blood_pressure":3,"sleep_quality":5,"breathing_problem":5,
    "noise_level":5,"living_conditions":5,"safety":5,"basic_needs":5,
    "academic_performance":5,"study_load":5,"teacher_student_relationship":5,
    "future_career_concerns":5,"social_support":3,"peer_pressure":5,
    "extracurricular_activities":5,"bullying":5,
}

# ===========================================================================
# Arc Ring Widget
# ===========================================================================
class ArcRingWidget(QWidget):
    def __init__(self, color: str, pct: int, parent=None):
        super().__init__(parent)
        self._color   = QColor(color)
        self._target  = max(0, min(100, pct))
        self._current = 0
        self.setMinimumSize(200, 110)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self._steps = 0
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._tick)
        QTimer.singleShot(300, self._timer.start)

    def _tick(self):
        self._steps += 1
        t = min(self._steps / 50, 1.0)
        ease = 1.0 - (1.0 - t) ** 3
        self._current = int(self._target * ease)
        self.update()
        if self._steps >= 50:
            self._current = self._target
            self._timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        size  = min(w, h * 2) - 20
        cx    = w / 2
        cy    = h - 4
        ro    = size / 2

        pen_bg = QPen(QColor(C["divider"]), 14, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(pen_bg)
        painter.drawArc(int(cx - ro), int(cy - ro), int(ro * 2), int(ro * 2), 0 * 16, 180 * 16)

        if self._current > 0:
            span_deg = int(self._current / 100 * 180)
            pen_fg = QPen(self._color, 14, Qt.SolidLine, Qt.RoundCap)
            painter.setPen(pen_fg)
            painter.drawArc(int(cx - ro), int(cy - ro), int(ro * 2), int(ro * 2), 0 * 16, span_deg * 16)

        painter.setPen(self._color)
        painter.setFont(QFont("Segoe UI Black", 26))
        painter.drawText(QRect(int(cx - 50), int(cy - 48), 100, 50), Qt.AlignCenter, f"{self._current}%")
        painter.end()


# ===========================================================================
# Donut Chart Widget
# ===========================================================================
class DonutWidget(QWidget):
    def __init__(self, sizes, colors, labels, parent=None):
        super().__init__(parent)
        self._sizes  = sizes
        self._colors = colors
        self._labels = labels
        self.setMinimumSize(180, 180)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        if _MPL_OK:
            self._setup_mpl()

    def _setup_mpl(self):
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        import matplotlib
        matplotlib.rcParams['font.family'] = 'DejaVu Sans'
        self._fig = Figure(figsize=(3, 3), dpi=90, facecolor="none")
        self._canvas = FigureCanvas(self._fig)
        self._canvas.setParent(self)
        self._canvas.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0,0,0,0)
        lay.addWidget(self._canvas)
        self._draw()

    def _draw(self):
        self._fig.clear()
        ax = self._fig.add_subplot(111)
        ax.pie(self._sizes, colors=self._colors, startangle=90, wedgeprops=dict(linewidth=2.5, edgecolor="white", width=0.45))
        ax.axis("equal")
        self._fig.tight_layout(pad=0.2)
        self._canvas.draw()

    def paintEvent(self, event):
        if _MPL_OK:
            super().paintEvent(event)
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rc   = self.rect()
        side = min(rc.width(), rc.height()) - 16
        cx, cy = rc.width() / 2.0, rc.height() / 2.0
        ro = side / 2.0
        total = sum(self._sizes) or 1
        angle = 90.0
        for size, color_hex in zip(self._sizes, self._colors):
            span = size / total * 360.0
            path = QPainterPath()
            path.moveTo(cx, cy)
            path.arcTo(cx-ro, cy-ro, ro*2, ro*2, angle, -span)
            path.closeSubpath()
            painter.setBrush(QBrush(QColor(color_hex)))
            painter.setPen(QPen(Qt.white, 2.5))
            painter.drawPath(path)
            angle -= span
        ri = ro * 0.55
        painter.setBrush(QBrush(QColor(C["white"])))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(int(cx-ri), int(cy-ri), int(ri*2), int(ri*2))
        painter.end()


# ===========================================================================
# ResultDialog
# ===========================================================================
class ResultDialog(QDialog):
    def __init__(self, level: int, payload: list[float], parent=None):
        super().__init__(parent, Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        self._level   = max(0, min(2, int(level)))
        self._payload = list(payload) if payload else [0.0] * 20
        self._cfg     = STRESS_LEVELS[self._level]

        self._factor_sizes  = self._compute_factors()
        self._drag_pos: Optional[QPoint] = None

        self._build_ui()
        self.resize(720, 600)

    def _compute_factors(self):
        if len(self._payload) != 20:
            return [1.0] * len(FACTOR_GROUPS)
        feat = dict(zip(_FEATURE_ORDER, self._payload))
        sizes = []
        for grp in FACTOR_GROUPS:
            s = sum(feat.get(k, 0) / (_KEY_MAX.get(k, 1) or 1) for k in grp["keys"])
            sizes.append(max(s, 0.01))
        return sizes

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        self._card = QFrame()
        self._card.setObjectName("result_card")
        self._card.setStyleSheet(f"""
            QFrame#result_card {{
                background: {C['white']}; border-radius: 20px; border: 1.5px solid {C['card_border']};
            }}
        """)
        outer.addWidget(self._card)

        card_lay = QVBoxLayout(self._card)
        card_lay.setContentsMargins(0, 0, 0, 0)
        card_lay.setSpacing(0)

        card_lay.addWidget(self._make_header())

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(28, 20, 28, 20)
        body_lay.setSpacing(24)

        body_lay.addLayout(self._make_left_col(), stretch=5)
        body_lay.addWidget(self._make_right_col(), stretch=4)

        card_lay.addWidget(body, 1)
        card_lay.addWidget(self._make_footer())

    def _make_header(self) -> QWidget:
        cfg = self._cfg
        header = QWidget()
        header.setFixedHeight(110)
        header.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {cfg['gradient_a']}, stop:1 {cfg['gradient_b']});
            border-top-left-radius: 20px; border-top-right-radius: 20px;
        """)

        lay = QHBoxLayout(header)
        lay.setContentsMargins(28, 16, 20, 16)
        lay.setSpacing(14)

        emoji_frame = QFrame()
        emoji_frame.setFixedSize(64, 64)
        emoji_frame.setStyleSheet("QFrame { background: rgba(255,255,255,0.22); border-radius: 32px; }")
        ef_lay = QVBoxLayout(emoji_frame)
        ef_lay.setContentsMargins(0,0,0,0)
        emoji_lbl = QLabel(cfg["emoji"])
        emoji_lbl.setFont(QFont("Segoe UI Emoji", 28))
        emoji_lbl.setAlignment(Qt.AlignCenter)
        emoji_lbl.setStyleSheet("background: transparent; color: white;")
        ef_lay.addWidget(emoji_lbl)

        txt_col = QVBoxLayout()
        txt_col.setSpacing(2)

        tag = QLabel(f"  Mức độ stress: {cfg['label']}  ")
        tag.setFont(QFont("Segoe UI Semibold", 9))
        tag.setStyleSheet("background: rgba(255,255,255,0.28); color: white; border-radius: 10px; padding: 2px 0px;")
        tag.setFixedHeight(22)
        tag.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        tag.setMaximumWidth(200)

        title_lbl = QLabel("Kết quả phân tích Stress")
        title_lbl.setFont(QFont("Segoe UI Black", 16))
        title_lbl.setStyleSheet("color: white; background: transparent;")

        sub_lbl = QLabel(cfg["sublabel"])
        sub_lbl.setFont(QFont("Segoe UI", 9))
        sub_lbl.setStyleSheet("color: rgba(255,255,255,0.85); background: transparent;")

        txt_col.addWidget(tag)
        txt_col.addWidget(title_lbl)
        txt_col.addWidget(sub_lbl)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(34, 34)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFont(QFont("Segoe UI", 11))
        close_btn.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.20); color: white; border-radius: 17px; border: none; }
            QPushButton:hover { background: rgba(255,255,255,0.38); }
            QPushButton:pressed { background: rgba(0,0,0,0.15); }
        """)
        close_btn.clicked.connect(self.accept)

        lay.addWidget(emoji_frame)
        lay.addLayout(txt_col, 1)
        lay.addWidget(close_btn, alignment=Qt.AlignTop)
        return header

    def _make_left_col(self) -> QVBoxLayout:
        cfg = self._cfg
        col = QVBoxLayout()
        col.setSpacing(16)

        arc_card = self._card_frame()
        ac_lay = QVBoxLayout(arc_card)
        ac_lay.setContentsMargins(20, 16, 20, 12)
        ac_lay.setSpacing(6)

        arc_title = QLabel("Chỉ số stress tổng thể")
        arc_title.setFont(QFont("Segoe UI Semibold", 9))
        arc_title.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")
        arc_title.setAlignment(Qt.AlignCenter)

        arc = ArcRingWidget(color=cfg["ring_color"], pct=cfg["bar_pct"])
        arc.setFixedHeight(108)

        ac_lay.addWidget(arc_title)
        ac_lay.addWidget(arc)
        col.addWidget(arc_card)
        col.addWidget(self._make_scale_bar())
        col.addWidget(self._make_tips_card(), 1)
        return col

    def _make_scale_bar(self) -> QFrame:
        card = self._card_frame()
        lay  = QVBoxLayout(card)
        lay.setContentsMargins(18, 12, 18, 12)
        lay.setSpacing(8)

        lbl = QLabel("Thang đo 3 mức độ")
        lbl.setFont(QFont("Segoe UI Semibold", 9))
        lbl.setStyleSheet(f"color: {C['text_primary']}; background: transparent;")
        lay.addWidget(lbl)

        levels_data = [
            (0, "Thấp",        C["detail_low_a"], self._level == 0),
            (1, "Trung bình",  C["detail_mid_a"], self._level == 1),
            (2, "Cao",         C["detail_high_a"], self._level == 2),
        ]

        bar_row = QHBoxLayout()
        bar_row.setSpacing(4)
        for lvl_id, lvl_name, color, active in levels_data:
            seg = QFrame()
            seg.setFixedHeight(8)
            seg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            seg.setStyleSheet(f"background: {color if active else C['divider']}; border-radius: 4px;")
            bar_row.addWidget(seg)
        lay.addLayout(bar_row)

        label_row = QHBoxLayout()
        label_row.setSpacing(4)
        for lvl_id, lvl_name, color, active in levels_data:
            lbl2 = QLabel(f"{'▶ ' if active else ''}{lvl_name}")
            lbl2.setFont(QFont("Segoe UI Semibold" if active else "Segoe UI", 8))
            lbl2.setStyleSheet(f"color: {color if active else C['text_muted']}; background: transparent;")
            lbl2.setAlignment(Qt.AlignCenter)
            label_row.addWidget(lbl2)
        lay.addLayout(label_row)
        return card

    def _make_tips_card(self) -> QFrame:
        cfg = self._cfg
        card = self._card_frame()
        card.setStyleSheet(f"QFrame {{ background: {cfg['tag_bg']}; border: none; border-radius: 14px; }}")
        lay  = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        header = QHBoxLayout()
        icon_lbl = QLabel("💡")
        icon_lbl.setFont(QFont("Segoe UI Emoji", 13))
        icon_lbl.setStyleSheet("background: transparent;")
        tip_title = QLabel("Gợi ý cải thiện")
        tip_title.setFont(QFont("Segoe UI Semibold", 10))
        tip_title.setStyleSheet(f"color: {C['text_primary']}; background: transparent;")
        header.addWidget(icon_lbl)
        header.addWidget(tip_title, 1)
        lay.addLayout(header)

        for tip in cfg["tips"]:
            row = QHBoxLayout()
            row.setSpacing(8)
            tip_lbl = QLabel(tip)
            tip_lbl.setFont(QFont("Segoe UI", 9))
            tip_lbl.setWordWrap(True)
            tip_lbl.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")
            lay.addWidget(tip_lbl)
        lay.addStretch()
        return card

    def _make_right_col(self) -> QFrame:
        card = self._card_frame()
        lay  = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(12)

        chart_title = QLabel("📊  Phân bổ yếu tố stress")
        chart_title.setFont(QFont("Segoe UI Semibold", 10))
        chart_title.setStyleSheet(f"color: {C['text_primary']}; background: transparent;")
        lay.addWidget(chart_title)

        sizes  = self._factor_sizes
        colors = [g["color"] for g in FACTOR_GROUPS]
        labels = [g["name"]  for g in FACTOR_GROUPS]

        donut = DonutWidget(sizes, colors, labels)
        donut.setMinimumHeight(175)
        lay.addWidget(donut, 1)

        total = sum(sizes) or 1
        for grp, size in zip(FACTOR_GROUPS, sizes):
            pct = size / total * 100
            row = QHBoxLayout()
            row.setSpacing(8)

            dot = QLabel("●")
            dot.setFont(QFont("Segoe UI", 11))
            dot.setFixedWidth(14)
            dot.setStyleSheet(f"color: {grp['color']}; background: transparent;")

            name_lbl = QLabel(f"{grp['name']}")
            name_lbl.setFont(QFont("Segoe UI", 8))
            name_lbl.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")

            pct_lbl = QLabel(f"{pct:.1f}%")
            pct_lbl.setFont(QFont("Segoe UI Semibold", 8))
            pct_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            pct_lbl.setStyleSheet(f"color: {grp['color']}; background: transparent;")

            bar_frame = QFrame()
            bar_frame.setFixedHeight(4)
            bar_frame.setStyleSheet(f"background: {grp['color']}; border-radius: 2px;")
            bar_frame.setFixedWidth(max(8, int(pct * 0.8)))

            row.addWidget(dot)
            row.addWidget(name_lbl, 1)
            row.addWidget(bar_frame)
            row.addWidget(pct_lbl)
            lay.addLayout(row)
        return card

    def _make_footer(self) -> QFrame:
        cfg = self._cfg
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background: {C['bg_main']}; border-top: 1px solid {C['divider']};
                border-bottom-left-radius: 20px; border-bottom-right-radius: 20px;
            }}
        """)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(24, 14, 24, 14)
        fl.setSpacing(12)

        retry_btn = QPushButton("🔄  Khảo sát lại")
        retry_btn.setFixedHeight(44)
        retry_btn.setFont(QFont("Segoe UI Semibold", 9))
        retry_btn.setCursor(Qt.PointingHandCursor)
        retry_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        retry_btn.setStyleSheet(f"""
            QPushButton {{ background: {C['btn_retry_bg']}; color: {C['btn_retry_fg']}; border: 1.5px solid {C['btn_retry_border']}; border-radius: 10px; }}
            QPushButton:hover {{ background: {C['btn_retry_hover']}; }}
            QPushButton:pressed {{ background: {C['btn_retry_border']}; }}
        """)
        retry_btn.clicked.connect(self.reject)

        pdf_btn = QPushButton("📄  Xuất PDF")
        pdf_btn.setFixedHeight(44)
        pdf_btn.setFont(QFont("Segoe UI Semibold", 9))
        pdf_btn.setCursor(Qt.PointingHandCursor)
        pdf_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        pdf_btn.setStyleSheet(f"""
            QPushButton {{ background: {C['btn_pdf_bg']}; color: {C['btn_pdf_fg']}; border: 1.5px solid {C['btn_pdf_border']}; border-radius: 10px; }}
            QPushButton:hover {{ background: {C['btn_pdf_hover']}; }}
            QPushButton:pressed {{ background: {C['btn_pdf_pressed']}; }}
        """)
        pdf_btn.clicked.connect(self._export_pdf)

        close_btn = QPushButton("✅  Hoàn tất")
        close_btn.setFixedHeight(44)
        close_btn.setFont(QFont("Segoe UI Semibold", 9))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {cfg['gradient_a']}, stop:1 {cfg['gradient_b']});
                color: {C['white']}; border: none; border-radius: 10px;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
            QPushButton:pressed {{ background: {cfg['gradient_b']}; }}
        """)
        close_btn.clicked.connect(self.accept)

        fl.addWidget(retry_btn, 1)
        fl.addWidget(pdf_btn, 1)
        fl.addWidget(close_btn, 1)
        return footer

    def _export_pdf(self):
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        import datetime

        default_name = f"stress_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Lưu báo cáo PDF", default_name, "PDF Files (*.pdf)")
        if not path:
            return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            import os
            import re

            cfg = self._cfg
            level_names = {0: "Thấp", 1: "Trung bình", 2: "Cao"}
            level_colors = {
                0: colors.HexColor(C["detail_low_a"]),
                1: colors.HexColor(C["detail_mid_a"]),
                2: colors.HexColor(C["detail_high_a"]),
            }
            lv_color = level_colors[self._level]

            BASE_FONT = "Helvetica"
            BOLD_FONT = "Helvetica-Bold"

            _here = os.path.dirname(os.path.abspath(__file__))
            _font_candidates = [
                (os.path.join(_here, "fonts", "DejaVuSans.ttf"), os.path.join(_here, "fonts", "DejaVuSans-Bold.ttf"), "DejaVuSans", "DejaVuSans-Bold"),
                (os.path.join(_here, "DejaVuSans.ttf"), os.path.join(_here, "DejaVuSans-Bold.ttf"), "DejaVuSans", "DejaVuSans-Bold"),
                ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans", "DejaVuSans-Bold"),
                ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf", "Arial", "Arial-Bold"),
                (os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts/DejaVuSans.ttf"), os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts/DejaVuSans-Bold.ttf"), "DejaVuSans", "DejaVuSans-Bold"),
            ]
            for reg_path, bold_path, reg_name, bold_name in _font_candidates:
                if os.path.exists(reg_path) and os.path.exists(bold_path):
                    try:
                        pdfmetrics.registerFont(TTFont(reg_name, reg_path))
                        pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                        BASE_FONT = reg_name
                        BOLD_FONT = bold_name
                        break
                    except Exception:
                        continue

            styles = getSampleStyleSheet()
            style_title = ParagraphStyle("title", fontName=BOLD_FONT, fontSize=18, textColor=colors.HexColor(C['text_primary']), spaceAfter=4)
            style_sub = ParagraphStyle("sub", fontName=BASE_FONT, fontSize=10, textColor=colors.HexColor(C['text_muted']), spaceAfter=12)
            style_section = ParagraphStyle("section", fontName=BOLD_FONT, fontSize=12, textColor=colors.HexColor(C['text_primary']), spaceBefore=14, spaceAfter=6)
            style_body = ParagraphStyle("body", fontName=BASE_FONT, fontSize=10, textColor=colors.HexColor(C['text_primary']), spaceAfter=4, leading=15)
            style_tip = ParagraphStyle("tip", fontName=BASE_FONT, fontSize=9.5, textColor=colors.HexColor(C['text_muted']), spaceAfter=5, leftIndent=12, leading=14)

            import datetime as dt
            now_str = dt.datetime.now().strftime("%d/%m/%Y %H:%M")

            story = []
            story.append(Paragraph("Báo cáo phân tích Stress", style_title))
            story.append(Paragraph(f"Thời gian: {now_str}", style_sub))
            story.append(HRFlowable(width="100%", thickness=1.5, color=lv_color, spaceAfter=12))

            story.append(Paragraph("Kết quả dự đoán", style_section))

            level_label = level_names.get(self._level, "Không xác định")
            bar_pct     = cfg["bar_pct"]
            table_data = [
                ["Mức độ stress:", level_label],
                ["Chỉ số:", f"{bar_pct}%"],
                ["Mô tả:", cfg["sublabel"]],
            ]
            t = Table(table_data, colWidths=[4*cm, 12*cm])
            t.setStyle(TableStyle([
                ("FONTNAME",  (0,0), (0,-1), BOLD_FONT),
                ("FONTNAME",  (1,0), (1,-1), BASE_FONT),
                ("FONTSIZE",  (0,0), (-1,-1), 10),
                ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor(C['text_primary'])),
                ("TEXTCOLOR", (1,0), (1,0), lv_color),
                ("FONTNAME",  (1,0), (1,0), BOLD_FONT),
                ("FONTSIZE",  (1,0), (1,0), 12),
                ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor(C['bg_main']), colors.white]),
                ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor(C['divider'])),
                ("TOPPADDING",    (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                ("LEFTPADDING",   (0,0), (-1,-1), 10),
            ]))
            story.append(t)
            story.append(Spacer(1, 0.4*cm))

            story.append(Paragraph("Phân bổ yếu tố stress", style_section))
            total = sum(self._factor_sizes) or 1
            factor_rows = [["Nhóm yếu tố", "Tỉ lệ (%)"]]
            for grp, size in zip(FACTOR_GROUPS, self._factor_sizes):
                pct_val = size / total * 100
                factor_rows.append([grp["name"], f"{pct_val:.1f}%"])

            ft = Table(factor_rows, colWidths=[9*cm, 7*cm])
            ft.setStyle(TableStyle([
                ("FONTNAME",  (0,0), (-1,0),  BOLD_FONT),
                ("FONTNAME",  (0,1), (-1,-1), BASE_FONT),
                ("FONTSIZE",  (0,0), (-1,-1), 10),
                ("BACKGROUND",(0,0), (-1,0),  colors.HexColor(C['divider'])),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor(C['bg_main'])]),
                ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor(C['divider'])),
                ("TOPPADDING",    (0,0), (-1,-1), 6),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
                ("LEFTPADDING",   (0,0), (-1,-1), 10),
                ("ALIGN", (1,0), (1,-1), "CENTER"),
            ]))
            story.append(ft)
            story.append(Spacer(1, 0.4*cm))

            story.append(Paragraph("Gợi ý cải thiện", style_section))
            for tip in cfg["tips"]:
                clean = re.sub(r'[𐀀-]', '', tip).strip()
                clean = clean or tip
                story.append(Paragraph(f"• {clean}", style_tip))

            story.append(Spacer(1, 0.5*cm))
            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor(C['divider'])))
            story.append(Paragraph(
                "Báo cáo được tạo từ hệ thống Stress Predictor · Không thay thế tư vấn y tế chuyên nghiệp.",
                ParagraphStyle("footer", fontName=BASE_FONT, fontSize=8, textColor=colors.HexColor(C['text_muted']), spaceAfter=0)
            ))

            doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
            doc.build(story)

            CustomMessageBox.show_success(self, "Xuất PDF thành công", f"Đã lưu báo cáo tại:\n{path}")

        except ImportError:
            CustomMessageBox.show_warning(self, "Thiếu thư viện", "Cần cài đặt ReportLab để xuất PDF:\n\npip install reportlab")
            
        except Exception as e:
            CustomMessageBox.show_error(self, "Lỗi xuất PDF", f"Không thể tạo file PDF:\n{str(e)}")

    @staticmethod
    def _card_frame() -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background: {C['white']}; border: none; border-radius: 14px; }}")
        return card

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def showEvent(self, event):
        super().showEvent(event)
        if self.parent():
            parent_rect = self.parent().frameGeometry()
            self.move(
                parent_rect.center().x() - self.width() // 2,
                parent_rect.center().y() - self.height() // 2,
            )

ResultScreen = ResultDialog