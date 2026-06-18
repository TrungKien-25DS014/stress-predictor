from __future__ import annotations

import math
from typing import Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QWidget, QSizePolicy, QGraphicsDropShadowEffect,
)
from PyQt5.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal, QRect, QPoint,
)
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QPainterPath,
)
from src.views.components.widgets import CustomMessageBox
from src.core.config import C

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    _MPL_OK = True
except ImportError:
    _MPL_OK = False

_FEATURE_ORDER = [
    "anxiety_level", "self_esteem", "mental_health_history", "depression",
    "headache", "blood_pressure", "sleep_quality", "breathing_problem",
    "noise_level", "living_conditions", "safety", "basic_needs",
    "academic_performance", "study_load", "teacher_student_relationship",
    "future_career_concerns", "social_support", "peer_pressure",
    "extracurricular_activities", "bullying",
]

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

class ArcRingWidget(QWidget):
    '''
    Thành phần vẽ đồ thị cung tròn hiển thị tổng thể mức stress.
    Hỗ trợ hiệu ứng lướt (easing) mượt mà lúc ban đầu.
    '''
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
        '''Cập nhật tiến trình đồ họa sau mỗi khung hình nhỏ.'''
        self._steps += 1
        t = min(self._steps / 50, 1.0)
        ease = 1.0 - (1.0 - t) ** 3
        self._current = int(self._target * ease)
        self.update()
        if self._steps >= 50:
            self._current = self._target
            self._timer.stop()

    def paintEvent(self, event):
        '''Mã nền tảng vẽ hình vòng cung tỉ lệ %.'''
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


class DonutWidget(QWidget):
    '''
    Thành phần vẽ bánh (Donut) tự nhận diện môi trường cài đặt Matplotlib
    hoặc dự phòng dùng QPainter Native.
    '''
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
        '''Tích hợp matplotlib nâng cao thay thế PyQt Native khi thư viện khả dụng.'''
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
        '''Thực hiện trích xuất dữ liệu và vẽ thông qua FigureCanvas.'''
        self._fig.clear()
        ax = self._fig.add_subplot(111)
        ax.pie(self._sizes, colors=self._colors, startangle=90, wedgeprops=dict(linewidth=2.5, edgecolor="white", width=0.45))
        ax.axis("equal")
        self._fig.tight_layout(pad=0.2)
        self._canvas.draw()

    def paintEvent(self, event):
        '''Mã vẽ dự phòng với chuẩn QPainter (khi thiếu Matplotlib).'''
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


class ResultDialog(QDialog):
    '''
    Cửa sổ hiển thị ngay tức thì đánh giá dự đoán của mô hình AI.
    Cung cấp gợi ý và khả năng kết xuất báo cáo chuẩn PDF.
    '''
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
        '''Chuẩn hóa lại dữ liệu đầu vào thành tỷ trọng 5 khía cạnh sức khỏe.'''
        if len(self._payload) != 20:
            return [1.0] * len(FACTOR_GROUPS)
        feat = dict(zip(_FEATURE_ORDER, self._payload))
        sizes = []
        for grp in FACTOR_GROUPS:
            s = sum(feat.get(k, 0) / (_KEY_MAX.get(k, 1) or 1) for k in grp["keys"])
            sizes.append(max(s, 0.01))
        return sizes

    def _build_ui(self):
        '''Đóng gói các khối giao diện lại thành chỉnh thể hoàn chỉnh.'''
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
        '''Biểu diễn thông tin chủ đạo dạng Gradient nổi bật đánh giá cốt lõi.'''
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
        emoji_frame.setStyleSheet(f"QFrame {{ background: {C.get('glass_light', 'rgba(255,255,255,0.22)')}; border-radius: 32px; }}")
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
        tag.setStyleSheet(f"background: {C.get('glass_mid', 'rgba(255,255,255,0.28)')}; color: white; border-radius: 10px; padding: 2px 0px;")
        tag.setFixedHeight(22)
        tag.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        tag.setMaximumWidth(200)

        title_lbl = QLabel("Kết quả phân tích Stress")
        title_lbl.setFont(QFont("Segoe UI Black", 16))
        title_lbl.setStyleSheet("color: white; background: transparent;")

        sub_lbl = QLabel(cfg["sublabel"])
        sub_lbl.setFont(QFont("Segoe UI", 9))
        sub_lbl.setStyleSheet(f"color: {C.get('glass_high', 'rgba(255,255,255,0.85)')}; background: transparent;")

        txt_col.addWidget(tag)
        txt_col.addWidget(title_lbl)
        txt_col.addWidget(sub_lbl)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(34, 34)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFont(QFont("Segoe UI", 11))
        close_btn.setStyleSheet(f"""
            QPushButton {{ background: {C.get('glass_dark', 'rgba(255,255,255,0.20)')}; color: white; border-radius: 17px; border: none; }}
            QPushButton:hover {{ background: {C.get('glass_hover', 'rgba(255,255,255,0.38)')}; }}
            QPushButton:pressed {{ background: {C.get('glass_pressed', 'rgba(0,0,0,0.15)')}; }}
        """)
        close_btn.clicked.connect(self.accept)

        lay.addWidget(emoji_frame)
        lay.addLayout(txt_col, 1)
        lay.addWidget(close_btn, alignment=Qt.AlignTop)
        return header

    def _make_left_col(self) -> QVBoxLayout:
        '''Dựng phần thông tin cốt lõi kèm biểu đồ vòng cung và thước đo.'''
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
        '''Render thang đo hiển thị tương quan 3 mức chỉ số Low-Mid-High.'''
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
        '''Khu vực khuyên dùng và các thủ thuật y tế tương đối.'''
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
        '''Dựng phần thể hiện tỷ trọng tương đối giữa 5 yếu tố cốt cán.'''
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
        '''Dải công cụ cuối bao gồm xuất PDF và quay lại ban đầu.'''
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
            QPushButton {{ background: {C.get('btn_retry_bg', '#F3F4F6')}; color: {C.get('btn_retry_fg', '#374151')}; border: 1.5px solid {C.get('btn_retry_border', '#D1D5DB')}; border-radius: 10px; }}
            QPushButton:hover {{ background: {C.get('btn_retry_hover', '#E5E7EB')}; }}
            QPushButton:pressed {{ background: {C.get('btn_retry_border', '#D1D5DB')}; }}
        """)
        retry_btn.clicked.connect(self.reject)

        pdf_btn = QPushButton("📄  Xuất PDF")
        pdf_btn.setFixedHeight(44)
        pdf_btn.setFont(QFont("Segoe UI Semibold", 9))
        pdf_btn.setCursor(Qt.PointingHandCursor)
        pdf_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        pdf_btn.setStyleSheet(f"""
            QPushButton {{ background: {C.get('btn_pdf_bg', '#EFF6FF')}; color: {C.get('btn_pdf_fg', '#1D4ED8')}; border: 1.5px solid {C.get('btn_pdf_border', '#93C5FD')}; border-radius: 10px; }}
            QPushButton:hover {{ background: {C.get('btn_pdf_hover', '#DBEAFE')}; }}
            QPushButton:pressed {{ background: {C.get('btn_pdf_pressed', '#BFDBFE')}; }}
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
        '''Kết xuất toàn bộ phân tích sang định dạng PDF thông qua ReportLab.'''
        from PyQt5.QtWidgets import QFileDialog
        import datetime

        default_name = f"stress_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "Lưu báo cáo PDF", default_name, "PDF Files (*.pdf)")
        if not path:
            return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm, mm
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                HRFlowable, KeepTogether,
            )
            from reportlab.platypus.flowables import Flowable
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.graphics.shapes import Drawing, Rect, String, Line
            from reportlab.graphics import renderPDF
            import os, re, datetime as dt

            # ── Font setup ────────────────────────────────────────────────
            BASE_FONT = "Helvetica"
            BOLD_FONT = "Helvetica-Bold"
            _here = os.path.dirname(os.path.abspath(__file__))
            _font_candidates = [
                (os.path.join(_here, "fonts", "DejaVuSans.ttf"),   os.path.join(_here, "fonts", "DejaVuSans-Bold.ttf"),   "DejaVuSans",  "DejaVuSans-Bold"),
                (os.path.join(_here, "DejaVuSans.ttf"),            os.path.join(_here, "DejaVuSans-Bold.ttf"),            "DejaVuSans",  "DejaVuSans-Bold"),
                ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","DejaVuSans",  "DejaVuSans-Bold"),
                ("C:/Windows/Fonts/arial.ttf",                      "C:/Windows/Fonts/arialbd.ttf",                        "Arial",       "Arial-Bold"),
            ]
            for reg_path, bold_path, reg_name, bold_name in _font_candidates:
                if os.path.exists(reg_path) and os.path.exists(bold_path):
                    try:
                        pdfmetrics.registerFont(TTFont(reg_name, reg_path))
                        pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                        BASE_FONT, BOLD_FONT = reg_name, bold_name
                        break
                    except Exception:
                        continue

            # ── Color palette ─────────────────────────────────────────────
            cfg = self._cfg
            level_names = {0: "Thấp", 1: "Trung bình", 2: "Cao"}
            level_hex = {
                0: C["detail_low_a"],
                1: C["detail_mid_a"],
                2: C["detail_high_a"],
            }
            lv_hex   = level_hex[self._level]
            lv_color = colors.HexColor(lv_hex)
            lv_light = colors.HexColor(cfg["tag_bg"])

            GRAY_DARK  = colors.HexColor(C['text_primary'])
            GRAY_MID   = colors.HexColor(C['text_muted'])
            GRAY_LINE  = colors.HexColor(C['divider'])
            BG_STRIPE  = colors.HexColor(C['bg_main'])
            WHITE      = colors.white

            now_str = dt.datetime.now().strftime("%d/%m/%Y %H:%M")
            PAGE_W, PAGE_H = A4
            CONTENT_W = PAGE_W - 4*cm   # margins 2cm each side

            # ── Paragraph styles ──────────────────────────────────────────
            sty_title = ParagraphStyle(
                "sty_title", fontName=BOLD_FONT, fontSize=22,
                textColor=WHITE, spaceAfter=2, leading=26,
            )
            sty_sub_header = ParagraphStyle(
                "sty_sub_header", fontName=BASE_FONT, fontSize=10,
                textColor=colors.HexColor("#FFFFFF99"), spaceAfter=0,
            )
            sty_section = ParagraphStyle(
                "sty_section", fontName=BOLD_FONT, fontSize=12,
                textColor=GRAY_DARK, spaceBefore=6, spaceAfter=8,
                borderPad=0,
            )
            sty_body = ParagraphStyle(
                "sty_body", fontName=BASE_FONT, fontSize=10,
                textColor=GRAY_DARK, leading=15,
            )
            sty_tip = ParagraphStyle(
                "sty_tip", fontName=BASE_FONT, fontSize=9.5,
                textColor=GRAY_MID, spaceAfter=6, leftIndent=8, leading=15,
            )
            sty_footer = ParagraphStyle(
                "sty_footer", fontName=BASE_FONT, fontSize=8,
                textColor=GRAY_MID, alignment=1,
            )

            # ── Custom Flowables ──────────────────────────────────────────

            class GradientHeader(Flowable):
                """Full-width coloured header banner with title + timestamp."""
                def __init__(self, color_hex_a, color_hex_b, level_label, bar_pct, now_str, width, base_font, bold_font):
                    super().__init__()
                    self._ca   = colors.HexColor(color_hex_a)
                    self._cb   = colors.HexColor(color_hex_b)
                    self._lvl  = level_label
                    self._pct  = bar_pct
                    self._now  = now_str
                    self.width = width
                    self._bf   = bold_font
                    self._nf   = base_font
                    self.height = 110

                def draw(self):
                    c = self.canv
                    # gradient via layered rects (reportlab has no native linear gradient)
                    steps = 30
                    for i in range(steps):
                        t  = i / steps
                        r  = self._ca.red   + t * (self._cb.red   - self._ca.red)
                        g  = self._ca.green + t * (self._cb.green - self._ca.green)
                        b  = self._ca.blue  + t * (self._cb.blue  - self._ca.blue)
                        x0 = self.width * i / steps
                        x1 = self.width * (i+1) / steps
                        c.setFillColorRGB(r, g, b)
                        c.rect(x0, 0, x1-x0+0.5, self.height, fill=1, stroke=0)

                    # Decorative circle top-right
                    c.setFillColorRGB(1, 1, 1, 0.08)
                    c.circle(self.width - 20, self.height - 10, 80, fill=1, stroke=0)
                    c.circle(self.width + 10, 20, 50, fill=1, stroke=0)

                    # Title text
                    c.setFillColor(colors.white)
                    c.setFont(self._bf, 20)
                    c.drawString(22, self.height - 36, "BÁO CÁO PHÂN TÍCH STRESS")

                    # Level badge — width is computed from the rendered text
                    # itself so longer labels (e.g. "Trung bình") never spill
                    # outside their pill background
                    lvl_text = f"Mức độ stress: {self._lvl}"
                    c.setFont(self._bf, 10)
                    badge_w = c.stringWidth(lvl_text, self._bf, 10) + 28
                    c.setFillColorRGB(1, 1, 1, 0.22)
                    c.roundRect(22, self.height - 72, badge_w, 24, 12, fill=1, stroke=0)
                    c.setFillColor(colors.white)
                    c.drawCentredString(22 + badge_w/2, self.height - 63, lvl_text)

                    # Score badge — same dynamic-width treatment
                    sc_text = f"Chỉ số: {self._pct}%"
                    c.setFont(self._bf, 11)
                    sc_w  = c.stringWidth(sc_text, self._bf, 11) + 28
                    sc_x = 22 + badge_w + 10
                    c.setFillColorRGB(1, 1, 1, 0.22)
                    c.roundRect(sc_x, self.height - 72, sc_w, 24, 12, fill=1, stroke=0)
                    c.setFillColor(colors.white)
                    c.drawCentredString(sc_x + sc_w/2, self.height - 63, sc_text)

                    # Horizontal score bar — anchored a fixed gap below the
                    # badge row so it never collides with the timestamp below it
                    bar_h  = 7
                    bar_y  = (self.height - 72) - 8 - bar_h
                    bar_w  = self.width - 44
                    c.setFillColorRGB(1, 1, 1, 0.25)
                    c.roundRect(22, bar_y, bar_w, bar_h, 3, fill=1, stroke=0)
                    filled = bar_w * min(self._pct, 100) / 100
                    c.setFillColorRGB(1, 1, 1, 0.90)
                    c.roundRect(22, bar_y, filled, bar_h, 3, fill=1, stroke=0)

                    # Timestamp — anchored below the bar (instead of a fixed
                    # y=12 that used to sit underneath the bar)
                    c.setFillColorRGB(1, 1, 1, 0.65)
                    c.setFont(self._nf, 8.5)
                    c.drawString(22, bar_y - 13, f"Thời gian tạo: {self._now}")

            class SectionHeading(Flowable):
                """Coloured left-accent bar + bold title."""
                def __init__(self, text, accent_color, width, bold_font):
                    super().__init__()
                    self._text   = text
                    self._accent = accent_color
                    self.width   = width
                    self._bf     = bold_font
                    self.height  = 26

                def draw(self):
                    c = self.canv
                    # accent bar
                    c.setFillColor(self._accent)
                    c.roundRect(0, 4, 4, 18, 2, fill=1, stroke=0)
                    # light background
                    c.setFillColorRGB(
                        self._accent.red, self._accent.green, self._accent.blue, 0.07
                    )
                    c.roundRect(8, 2, self.width - 8, 22, 4, fill=1, stroke=0)
                    # text
                    c.setFillColor(colors.HexColor(C['text_primary']))
                    c.setFont(self._bf, 11)
                    c.drawString(18, 9, self._text)

            class HorizontalBarChart(Flowable):
                """Horizontal bar chart for factor distribution."""
                def __init__(self, groups, sizes, width, base_font, bold_font):
                    super().__init__()
                    self._groups = groups
                    self._sizes  = sizes
                    self.width   = width
                    self._nf     = base_font
                    self._bf     = bold_font
                    self.height  = len(groups) * 32 + 8

                def draw(self):
                    c     = self.canv
                    total = sum(self._sizes) or 1
                    bar_x = 90
                    bar_w = self.width - bar_x - 55
                    row_h = 32
                    n     = len(self._groups)

                    for i, (grp, size) in enumerate(zip(self._groups, self._sizes)):
                        pct   = size / total * 100
                        y     = self.height - (i + 1) * row_h + 4
                        color = colors.HexColor(grp["color"])

                        # row background alternating
                        if i % 2 == 0:
                            c.setFillColorRGB(0.97, 0.97, 0.97)
                            c.rect(0, y - 2, self.width, row_h - 2, fill=1, stroke=0)

                        # label
                        c.setFillColor(colors.HexColor(C['text_primary']))
                        c.setFont(self._nf, 9)
                        c.drawString(6, y + 8, grp["name"])

                        # track
                        c.setFillColorRGB(0.88, 0.88, 0.88)
                        c.roundRect(bar_x, y + 6, bar_w, 12, 6, fill=1, stroke=0)

                        # fill
                        filled = bar_w * pct / 100
                        c.setFillColor(color)
                        if filled > 0:
                            c.roundRect(bar_x, y + 6, filled, 12, 6, fill=1, stroke=0)

                        # pct label
                        c.setFillColor(color)
                        c.setFont(self._bf, 9)
                        c.drawString(bar_x + bar_w + 6, y + 7, f"{pct:.1f}%")

            class ScoreGauge(Flowable):
                """Arc gauge showing the stress score."""
                def __init__(self, pct, color_hex, width, base_font, bold_font):
                    super().__init__()
                    self._pct   = pct
                    self._color = colors.HexColor(color_hex)
                    self.width  = width
                    self._nf    = base_font
                    self._bf    = bold_font
                    # The arc is drawn within a bounding box that reaches
                    # cy + 2*r = 12 + 120 = 132 (plus a few pt for the 10pt
                    # stroke width). The previous value of 90 was smaller than
                    # the actual drawn content, so the gauge bled upward into
                    # whatever flowable was placed above it on the page.
                    self.height = 140

                def draw(self):
                    import math
                    c  = self.canv
                    cx = self.width / 2
                    cy = 12
                    r  = 60
                    # background arc
                    c.setStrokeColorRGB(0.88, 0.88, 0.88)
                    c.setLineWidth(10)
                    c.arc(cx-r, cy, cx+r, cy+r*2, 0, 180)
                    # colored arc
                    span = self._pct / 100 * 180
                    c.setStrokeColor(self._color)
                    c.setLineWidth(10)
                    c.arc(cx-r, cy, cx+r, cy+r*2, 0, span)
                    # percentage text
                    c.setFillColor(self._color)
                    c.setFont(self._bf, 22)
                    c.drawCentredString(cx, cy + r - 14, f"{self._pct}%")
                    c.setFillColor(colors.HexColor(C['text_muted']))
                    c.setFont(self._nf, 8)
                    c.drawCentredString(cx, cy + r - 26, "Chỉ số stress")

            class TipBox(Flowable):
                """Styled tip card with coloured left border."""
                def __init__(self, text, accent_color, width, base_font):
                    super().__init__()
                    self._text   = text
                    self._accent = accent_color
                    self.width   = width
                    self._nf     = base_font
                    self.height  = 28

                def draw(self):
                    c = self.canv
                    # light bg
                    c.setFillColorRGB(
                        self._accent.red, self._accent.green, self._accent.blue, 0.06
                    )
                    c.roundRect(0, 0, self.width, self.height - 4, 5, fill=1, stroke=0)
                    # accent left border
                    c.setFillColor(self._accent)
                    c.rect(0, 0, 3, self.height - 4, fill=1, stroke=0)
                    # text
                    c.setFillColor(colors.HexColor(C['text_primary']))
                    c.setFont(self._nf, 9.5)
                    # clip long text
                    max_w = self.width - 18
                    c.drawString(12, 8, self._text[:90])

            # ── Build story ───────────────────────────────────────────────
            level_label = level_names.get(self._level, "Không xác định")
            bar_pct     = cfg["bar_pct"]
            story       = []

            # 1. Header banner
            story.append(GradientHeader(
                cfg["gradient_a"], cfg["gradient_b"],
                level_label, bar_pct, now_str,
                CONTENT_W, BASE_FONT, BOLD_FONT,
            ))
            story.append(Spacer(1, 0.35*cm))

            # 2. Summary row (gauge + prediction table side-by-side)
            gauge_w = 5.5*cm
            table_w = CONTENT_W - gauge_w - 0.4*cm

            level_label_vn = level_label
            pred_data = [
                [Paragraph(f"<b>Mức độ stress</b>", ParagraphStyle("ph", fontName=BOLD_FONT, fontSize=10, textColor=GRAY_DARK)),
                 Paragraph(f"<b>{level_label_vn}</b>", ParagraphStyle("phv", fontName=BOLD_FONT, fontSize=12, textColor=lv_color))],
                [Paragraph("Chỉ số", ParagraphStyle("ph2", fontName=BASE_FONT, fontSize=10, textColor=GRAY_MID)),
                 Paragraph(f"{bar_pct}%", ParagraphStyle("phv2", fontName=BOLD_FONT, fontSize=10, textColor=GRAY_DARK))],
                [Paragraph("Mô tả", ParagraphStyle("ph3", fontName=BASE_FONT, fontSize=10, textColor=GRAY_MID)),
                 Paragraph(cfg["sublabel"], ParagraphStyle("phv3", fontName=BASE_FONT, fontSize=10, textColor=GRAY_DARK, leading=14))],
            ]

            pred_t = Table(pred_data, colWidths=[3.5*cm, table_w - 3.5*cm])
            pred_t.setStyle(TableStyle([
                ("FONTSIZE",       (0,0), (-1,-1), 10),
                ("ROWBACKGROUNDS", (0,0), (-1,-1), [BG_STRIPE, WHITE]),
                ("LINEBELOW",      (0,0), (-1,-2), 0.4, GRAY_LINE),
                ("TOPPADDING",     (0,0), (-1,-1), 8),
                ("BOTTOMPADDING",  (0,0), (-1,-1), 8),
                ("LEFTPADDING",    (0,0), (-1,-1), 10),
                ("RIGHTPADDING",   (0,0), (-1,-1), 8),
                ("VALIGN",         (0,0), (-1,-1), "MIDDLE"),
                ("ROUNDEDCORNERS", [6]),
            ]))

            summary_t = Table(
                [[ScoreGauge(bar_pct, lv_hex, gauge_w, BASE_FONT, BOLD_FONT), pred_t]],
                colWidths=[gauge_w, table_w],
            )
            summary_t.setStyle(TableStyle([
                ("VALIGN",       (0,0), (-1,-1), "MIDDLE"),
                ("LEFTPADDING",  (0,0), (0,-1), 0),
                ("RIGHTPADDING", (0,0), (0,-1), 10),
                ("TOPPADDING",   (0,0), (-1,-1), 0),
                ("BOTTOMPADDING",(0,0), (-1,-1), 0),
            ]))
            story.append(KeepTogether([
                SectionHeading("Kết quả dự đoán", lv_color, CONTENT_W, BOLD_FONT),
                Spacer(1, 0.25*cm),
                summary_t,
            ]))
            story.append(Spacer(1, 0.35*cm))

            # 3. Factor distribution (horizontal bar chart)
            story.append(KeepTogether([
                SectionHeading("Phân bố yếu tố stress", lv_color, CONTENT_W, BOLD_FONT),
                Spacer(1, 0.25*cm),
                HorizontalBarChart(FACTOR_GROUPS, self._factor_sizes, CONTENT_W, BASE_FONT, BOLD_FONT),
            ]))
            story.append(Spacer(1, 0.35*cm))

            # 4. Tips
            clean_tips = []
            for tip in cfg["tips"]:
                clean = re.sub(r'[^\x00-\x7F\u00C0-\u024F\u1E00-\u1EFF\u2013\u2014 ]', '', tip).strip()
                clean_tips.append(clean or tip)

            tip_blocks = [
                SectionHeading("Gợi ý cải thiện", lv_color, CONTENT_W, BOLD_FONT),
                Spacer(1, 0.3*cm),
            ]
            for tip in clean_tips:
                tip_blocks.append(TipBox(tip, lv_color, CONTENT_W, BASE_FONT))
                tip_blocks.append(Spacer(1, 0.15*cm))
            story.append(KeepTogether(tip_blocks))

            story.append(Spacer(1, 0.4*cm))
            story.append(HRFlowable(width="100%", thickness=0.8, color=GRAY_LINE, spaceAfter=8))
            story.append(Paragraph(
                "Báo cáo được tạo từ hệ thống Stress Predictor  ·  Không thay thế tư vấn y tế chuyên nghiệp.",
                sty_footer,
            ))

            # ── Page template with subtle page number ─────────────────────
            def on_page(canvas, doc):
                canvas.saveState()
                canvas.setFillColor(GRAY_MID)
                canvas.setFont(BASE_FONT, 8)
                canvas.drawCentredString(PAGE_W / 2, 0.55*cm, f"Trang {doc.page}")
                canvas.restoreState()

            doc = SimpleDocTemplate(
                path, pagesize=A4,
                leftMargin=2*cm, rightMargin=2*cm,
                topMargin=1.1*cm, bottomMargin=1.3*cm,
            )
            doc.build(story, onFirstPage=on_page, onLaterPages=on_page)

            CustomMessageBox.show_success(self, "Xuất PDF thành công", f"Đã lưu báo cáo tại: {path}")

        except ImportError:
            CustomMessageBox.show_warning(self, "Thiếu thư viện", "Cần cài đặt ReportLab để xuất PDF: pip install reportlab")
        except Exception as e:
            CustomMessageBox.show_error(self, "Lỗi xuất PDF", f"Không thể tạo file PDF: {str(e)}")

    @staticmethod
    def _card_frame() -> QFrame:
        '''Chuyên xây dựng khung QFrame nền trắng bo góc chuẩn mực.'''
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background: {C['white']}; border: none; border-radius: 14px; }}")
        return card

    def mousePressEvent(self, event):
        '''Gắn tọa độ chuột lên thuộc tính nhằm hỗ trợ hiệu ứng Drag tùy biến.'''
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        '''Dịch chuyển bản đồ tọa độ của toàn Form qua các tính toán từ trỏ chuột.'''
        if event.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        '''Tẩy trắng tọa độ chuột khi thả ra.'''
        self._drag_pos = None

    def showEvent(self, event):
        '''Kiểm tra vị trí và canh giữa Widget so với Cha của nó.'''
        super().showEvent(event)
        if self.parent():
            parent_rect = self.parent().frameGeometry()
            self.move(
                parent_rect.center().x() - self.width() // 2,
                parent_rect.center().y() - self.height() // 2,
            )

ResultScreen = ResultDialog