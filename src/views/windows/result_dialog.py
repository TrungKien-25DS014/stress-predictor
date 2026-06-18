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
            import os, re, math, datetime as dt

            # ── Font setup ────────────────────────────────────────────────
            BASE_FONT = "Helvetica"
            BOLD_FONT = "Helvetica-Bold"
            _here = os.path.dirname(os.path.abspath(__file__))
            _font_candidates = [
                (os.path.join(_here, "fonts", "DejaVuSans.ttf"),    os.path.join(_here, "fonts", "DejaVuSans-Bold.ttf"),    "DejaVuSans",  "DejaVuSans-Bold"),
                (os.path.join(_here, "DejaVuSans.ttf"),             os.path.join(_here, "DejaVuSans-Bold.ttf"),             "DejaVuSans",  "DejaVuSans-Bold"),
                ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "DejaVuSans",  "DejaVuSans-Bold"),
                ("C:/Windows/Fonts/arial.ttf",                       "C:/Windows/Fonts/arialbd.ttf",                        "Arial",       "Arial-Bold"),
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
            cfg        = self._cfg
            level_names = {0: "Thấp", 1: "Trung bình", 2: "Cao"}
            level_hex  = {
                0: C["detail_low_a"],
                1: C["detail_mid_a"],
                2: C["detail_high_a"],
            }
            lv_hex     = level_hex[self._level]
            lv_color   = colors.HexColor(lv_hex)
            lv_light   = colors.HexColor(cfg["tag_bg"])

            GRAY_DARK  = colors.HexColor(C['text_primary'])
            GRAY_MID   = colors.HexColor(C['text_muted'])
            GRAY_LINE  = colors.HexColor(C['divider'])
            BG_STRIPE  = colors.HexColor(C['bg_main'])
            WHITE      = colors.white

            now_str   = dt.datetime.now().strftime("%d/%m/%Y %H:%M")
            PAGE_W, PAGE_H = A4
            CONTENT_W = PAGE_W - 4*cm    # left+right margins 2cm each

            # ── Paragraph styles ──────────────────────────────────────────
            sty_footer = ParagraphStyle(
                "sty_footer", fontName=BASE_FONT, fontSize=8,
                textColor=GRAY_MID, alignment=1,
            )
            sty_body = ParagraphStyle(
                "sty_body", fontName=BASE_FONT, fontSize=9.5,
                textColor=GRAY_DARK, leading=14,
            )
            sty_body_bold = ParagraphStyle(
                "sty_body_bold", fontName=BOLD_FONT, fontSize=9.5,
                textColor=GRAY_DARK, leading=14,
            )
            sty_muted = ParagraphStyle(
                "sty_muted", fontName=BASE_FONT, fontSize=9,
                textColor=GRAY_MID, leading=13,
            )

            # ── Custom Flowables ──────────────────────────────────────────

            class TitleBanner(Flowable):
                """Top title banner."""
                def __init__(self, width, bold_font, base_font):
                    super().__init__()
                    self.width  = width
                    self._bf    = bold_font
                    self._nf    = base_font
                    self.height = 56

                def draw(self):
                    c = self.canv
                    c.setFillColorRGB(0.07, 0.26, 0.13)
                    c.roundRect(0, 0, self.width, self.height, 8, fill=1, stroke=0)
                    c.setFillColor(colors.white)
                    c.setFont(self._bf, 17)
                    c.drawCentredString(self.width / 2, self.height - 26, "BÁO CÁO ĐÁNH GIÁ STRESS")
                    c.setFillColorRGB(0.65, 0.86, 0.65)
                    c.setFont(self._nf, 8)
                    c.drawCentredString(self.width / 2, self.height - 40, "STRESS ASSESSMENT REPORT")

            class InfoBar(Flowable):
                """Green info strip: name / date / report id / confidence."""
                def __init__(self, name, date_str, report_id, confidence, width, base_font, bold_font):
                    super().__init__()
                    self._fields = [
                        ("Họ và tên",           name),
                        ("Ngày đánh giá",        date_str),
                        ("Mã báo cáo",           report_id),
                        ("Độ tin cậy dữ liệu",   confidence),
                    ]
                    self.width  = width
                    self._nf    = base_font
                    self._bf    = bold_font
                    self.height = 40

                def draw(self):
                    c = self.canv
                    c.setFillColorRGB(0.18, 0.49, 0.20)
                    c.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=0)
                    col_w = self.width / len(self._fields)
                    for i, (lbl, val) in enumerate(self._fields):
                        x = i * col_w + col_w / 2
                        c.setFillColorRGB(0.78, 0.90, 0.78)
                        c.setFont(self._nf, 6.5)
                        c.drawCentredString(x, self.height - 13, lbl)
                        c.setFillColor(colors.white)
                        c.setFont(self._bf, 8.5)
                        c.drawCentredString(x, self.height - 24, val)
                    c.setStrokeColorRGB(0.50, 0.78, 0.50)
                    c.setLineWidth(0.5)
                    for i in range(1, len(self._fields)):
                        x = i * col_w
                        c.line(x, 5, x, self.height - 5)

            class SectionHeading(Flowable):
                """Coloured left-accent bar + bold title."""
                def __init__(self, number, text, accent_color, width, bold_font):
                    super().__init__()
                    self._num    = number
                    self._text   = text
                    self._accent = accent_color
                    self.width   = width
                    self._bf     = bold_font
                    self.height  = 22

                def draw(self):
                    c = self.canv
                    c.setFillColor(self._accent)
                    c.roundRect(0, 3, 4, 16, 2, fill=1, stroke=0)
                    c.setFillColorRGB(
                        self._accent.red, self._accent.green, self._accent.blue, 0.07,
                    )
                    c.roundRect(8, 1, self.width - 8, 20, 4, fill=1, stroke=0)
                    c.setFillColor(colors.HexColor(C['text_primary']))
                    c.setFont(self._bf, 10)
                    c.drawString(16, 7, f"{self._num}. {self._text}")

            class ScoreCards(Flowable):
                """3-column summary cards: score / level / status."""
                def __init__(self, pct, level_label, status, status_desc, width, base_font, bold_font, lv_color):
                    super().__init__()
                    self._pct         = pct
                    self._level       = level_label
                    self._status      = status
                    self._status_desc = status_desc
                    self.width        = width
                    self._nf          = base_font
                    self._bf          = bold_font
                    self._lvc         = lv_color
                    self.height       = 78

                def draw(self):
                    c     = self.canv
                    col_w = self.width / 3
                    pad   = 5
                    cards = [
                        ("STRESS SCORE",   f"{self._pct}%",  "Chỉ số stress",    self._lvc),
                        ("MỨC ĐỘ STRESS",  self._level,      "Mức độ hiện tại",  self._lvc),
                        ("TRẠNG THÁI",     self._status,     self._status_desc,  self._lvc),
                    ]
                    for i, (title, main, sub, col) in enumerate(cards):
                        x = i * col_w + pad
                        w = col_w - pad * 2
                        c.setFillColor(colors.white)
                        c.setStrokeColorRGB(0.88, 0.88, 0.88)
                        c.setLineWidth(0.8)
                        c.roundRect(x, 0, w, self.height, 7, fill=1, stroke=1)
                        c.setFillColorRGB(col.red, col.green, col.blue, 0.12)
                        c.circle(x + 18, self.height - 18, 10, fill=1, stroke=0)
                        c.setFillColor(col)
                        c.setFont(self._bf, 7)
                        c.drawCentredString(x + 18, self.height - 22, "●")
                        c.setFillColor(colors.HexColor(C['text_muted']))
                        c.setFont(self._nf, 6.5)
                        c.drawString(x + 32, self.height - 14, title)
                        c.setFillColor(colors.HexColor(C['text_primary']))
                        font_sz = 18 if len(main) <= 4 else 13
                        c.setFont(self._bf, font_sz)
                        c.drawString(x + 10, self.height - 46, main)
                        # sub label
                        c.setFillColor(colors.HexColor(C['text_muted']))
                        c.setFont(self._nf, 8)
                        c.drawString(x + 10, self.height - 60, sub)

            class DonutScaleRow(Flowable):
                """Donut gauge (left) + detail table (center) + scale legend (right)."""
                def __init__(self, pct, threshold, level_label, lv_color, cfg, width, base_font, bold_font):
                    super().__init__()
                    self._pct       = pct
                    self._threshold = threshold
                    self._level     = level_label
                    self._lvc       = lv_color
                    self._cfg       = cfg
                    self.width      = width
                    self._nf        = base_font
                    self._bf        = bold_font
                    self.height     = 130

                def draw(self):
                    c     = self.canv
                    donut_w = self.width * 0.26
                    table_w = self.width * 0.36
                    scale_w = self.width - donut_w - table_w - 8

                    # ── Donut ────────────────────────────────────────────
                    cx = donut_w / 2
                    cy = self.height / 2
                    r  = 42

                    c.setFillColor(colors.white)
                    c.setStrokeColorRGB(0.88, 0.88, 0.88)
                    c.setLineWidth(11)
                    c.circle(cx, cy, r, fill=0, stroke=1)

                    c.saveState()
                    c.setStrokeColor(self._lvc)
                    c.setLineWidth(11)
                    c.setLineCap(1)
                    span  = self._pct / 100 * 360
                    steps = max(int(span * 2), 4)
                    p = c.beginPath()
                    for i in range(steps + 1):
                        angle = math.radians(90 - span * i / steps)
                        px = cx + r * math.cos(angle)
                        py = cy + r * math.sin(angle)
                        if i == 0:
                            p.moveTo(px, py)
                        else:
                            p.lineTo(px, py)
                    c.drawPath(p, fill=0, stroke=1)
                    c.restoreState()

                    c.setFillColor(self._lvc)
                    c.setFont(self._bf, 16)
                    c.drawCentredString(cx, cy + 2, f"{self._pct}%")
                    c.setFillColor(colors.HexColor(C['text_muted']))
                    c.setFont(self._nf, 7)
                    c.drawCentredString(cx, cy - 12, "Stress Score")

                    # ── Detail table ─────────────────────────────────────
                    tx = donut_w + 6
                    rows = [
                        ("Chỉ số stress",      f"{self._pct}%",   False, colors.HexColor(C['text_primary'])),
                        ("Mức độ",             self._level,        True,  self._lvc),
                        ("Ngưỡng tham chiếu",  self._threshold,   False, colors.HexColor(C['text_primary'])),
                        ("Trạng thái",         "Bình thường",      True,  colors.HexColor(C['text_primary'])),
                    ]
                    row_h = 22
                    for i, (lbl, val, bold, val_col) in enumerate(rows):
                        y  = self.height - 24 - i * row_h
                        bg = (0.97, 0.97, 0.97) if i % 2 == 0 else (1.0, 1.0, 1.0)
                        c.setFillColorRGB(*bg)
                        c.rect(tx, y - 4, table_w, row_h, fill=1, stroke=0)
                        c.setFillColor(colors.HexColor(C['text_muted']))
                        c.setFont(self._nf, 8)
                        c.drawString(tx + 6, y + 4, lbl)
                        c.setFillColor(val_col)
                        c.setFont(self._bf if bold else self._nf, 8)
                        c.drawRightString(tx + table_w - 6, y + 4, val)

                    tip_y = self.height - 24 - len(rows) * row_h - 14
                    c.setFillColorRGB(self._lvc.red, self._lvc.green, self._lvc.blue, 0.10)
                    c.roundRect(tx, tip_y - 5, table_w, 18, 4, fill=1, stroke=0)
                    c.setFillColor(self._lvc)
                    c.setFont(self._nf, 7)
                    c.drawString(tx + 6, tip_y + 1, "Chỉ số ở mức thấp – trạng thái tinh thần ổn định.")

                    # ── Scale legend ─────────────────────────────────────
                    sx = donut_w + table_w + 14
                    c.setFillColor(colors.HexColor(C['text_primary']))
                    c.setFont(self._bf, 7)
                    c.drawString(sx, self.height - 14, "THANG ĐÁNH GIÁ MỨC ĐỘ STRESS")

                    scale_items = [
                        ("0 – 35%",    "THẤP",       colors.HexColor("#2E7D32"), colors.HexColor("#E8F5E9"), "Bình thường"),
                        ("36 – 65%",   "TRUNG BÌNH", colors.HexColor("#F57C00"), colors.HexColor("#FFF3E0"), "Cần chú ý"),
                        ("66 – 100%",  "CAO",        colors.HexColor("#C62828"), colors.HexColor("#FFEBEE"), "Nguy cơ cao"),
                    ]
                    for j, (rng, lbl, col, bg, sub) in enumerate(scale_items):
                        sy = self.height - 36 - j * 30
                        c.setFillColor(bg)
                        c.roundRect(sx, sy - 8, scale_w - 4, 26, 4, fill=1, stroke=0)
                        c.setFillColor(col)
                        c.circle(sx + 9, sy + 4, 6, fill=1, stroke=0)
                        c.setFillColor(col)
                        c.setFont(self._bf, 7.5)
                        c.drawString(sx + 20, sy + 6, rng)
                        c.setFont(self._bf, 8.5)
                        c.drawString(sx + 20, sy - 2, lbl)
                        c.setFillColor(colors.HexColor(C['text_muted']))
                        c.setFont(self._nf, 6.5)
                        c.drawRightString(sx + scale_w - 6, sy + 2, sub)

            class FactorBarChart(Flowable):
                """Horizontal bar chart for 5 stress factor groups."""
                def __init__(self, groups, sizes, width, base_font, bold_font, lv_color):
                    super().__init__()
                    self._groups  = groups
                    self._sizes   = sizes
                    self.width    = width
                    self._nf      = base_font
                    self._bf      = bold_font
                    self._lvc     = lv_color
                    self.height   = len(groups) * 24 + 32

                def draw(self):
                    c     = self.canv
                    total = sum(self._sizes) or 1
                    bar_x = 70
                    bar_w = self.width * 0.58
                    row_h = 24

                    c.setFillColor(colors.HexColor(C['text_muted']))
                    c.setFont(self._nf, 6)
                    for pct in [0, 20, 40, 60, 80, 100]:
                        x = bar_x + bar_w * pct / 100
                        c.drawCentredString(x, self.height - 12, f"{pct}%")
                        c.setStrokeColorRGB(0.88, 0.88, 0.88)
                        c.setLineWidth(0.3)
                        c.line(x, self.height - 16, x, 28)

                    for i, (grp, size) in enumerate(zip(self._groups, self._sizes)):
                        pct   = size / total * 100
                        y     = self.height - 30 - i * row_h
                        col   = colors.HexColor(grp["color"])

                        if i % 2 == 0:
                            c.setFillColorRGB(0.97, 0.97, 0.97)
                            c.rect(0, y - 4, self.width, row_h, fill=1, stroke=0)

                        c.setFillColor(col)
                        c.circle(7, y + 4, 5, fill=1, stroke=0)
                        c.setFillColor(colors.HexColor(C['text_primary']))
                        c.setFont(self._nf, 8.5)
                        c.drawString(15, y + 1, grp["name"])

                        c.setFillColorRGB(0.88, 0.88, 0.88)
                        c.roundRect(bar_x, y + 2, bar_w, 11, 4, fill=1, stroke=0)

                        filled = bar_w * pct / 100
                        c.setFillColor(col)
                        if filled > 0:
                            c.roundRect(bar_x, y + 2, filled, 11, 4, fill=1, stroke=0)

                        c.setFillColor(col)
                        c.setFont(self._bf, 8.5)
                        c.drawString(bar_x + bar_w + 5, y + 2, f"{pct:.1f}%")

                    c.setFillColorRGB(self._lvc.red, self._lvc.green, self._lvc.blue, 0.10)
                    c.roundRect(0, 0, self.width, 20, 4, fill=1, stroke=0)
                    c.setFillColor(self._lvc)
                    c.circle(9, 10, 4, fill=1, stroke=0)
                    c.setFillColor(colors.HexColor(C['text_primary']))
                    c.setFont(self._nf, 7.5)
                    c.drawString(18, 6, "Thể chất và Môi trường tác động nhiều nhất đến mức stress hiện tại.")

            class InsightCard(Flowable):
                """Checkmark insight row."""
                def __init__(self, text, lv_color, width, base_font, bold_font):
                    super().__init__()
                    self._text  = text
                    self._lvc   = lv_color
                    self.width  = width
                    self._nf    = base_font
                    self._bf    = bold_font
                    self.height = 20

                def draw(self):
                    c = self.canv
                    c.setFillColor(self._lvc)
                    c.circle(8, 8, 6, fill=1, stroke=0)
                    c.setFillColor(colors.white)
                    c.setFont(self._bf, 7)
                    c.drawCentredString(8, 5, "v")
                    c.setFillColor(colors.HexColor(C['text_primary']))
                    c.setFont(self._nf, 8.5)
                    c.drawString(20, 5, self._text[:98])

            class RecCard(Flowable):
                """Numbered recommendation row."""
                def __init__(self, number, text, lv_color, width, base_font, bold_font):
                    super().__init__()
                    self._num  = number
                    self._text = text
                    self._lvc  = lv_color
                    self.width = width
                    self._nf   = base_font
                    self._bf   = bold_font
                    self.height = 20

                def draw(self):
                    c = self.canv
                    c.setFillColor(self._lvc)
                    c.circle(8, 8, 7, fill=1, stroke=0)
                    c.setFillColor(colors.white)
                    c.setFont(self._bf, 8)
                    c.drawCentredString(8, 5, str(self._num))
                    c.setFillColor(colors.HexColor(C['text_primary']))
                    c.setFont(self._nf, 8.5)
                    c.drawString(20, 5, self._text[:98])

            # ── Assemble story (1 page) ───────────────────────────────────
            level_label = level_names.get(self._level, "Không xác định")
            bar_pct     = cfg["bar_pct"]
            story       = []

            GAP = 0.22*cm   # tight spacing to fit 1 page

            # ── Header ────────────────────────────────────────────────────
            story.append(TitleBanner(CONTENT_W, BOLD_FONT, BASE_FONT))
            story.append(Spacer(1, 3))
            story.append(InfoBar(
                "Nguyễn Văn A", now_str,
                f"STR-{dt.datetime.now().strftime('%Y%m%d')}-001", "92%",
                CONTENT_W, BASE_FONT, BOLD_FONT,
            ))
            story.append(Spacer(1, GAP))

            # ── Section 1: Tóm tắt kết quả ───────────────────────────────
            story.append(SectionHeading("1", "TÓM TẮT KẾT QUẢ", lv_color, CONTENT_W, BOLD_FONT))
            story.append(Spacer(1, 4))
            story.append(ScoreCards(
                bar_pct, level_label,
                "Bình thường", "Chưa phát hiện nguy cơ stress",
                CONTENT_W, BASE_FONT, BOLD_FONT, lv_color,
            ))
            story.append(Spacer(1, 4))
            story.append(DonutScaleRow(
                bar_pct, "0 – 35%", level_label, lv_color, cfg,
                CONTENT_W, BASE_FONT, BOLD_FONT,
            ))
            story.append(Spacer(1, GAP))

            # ── Sections 2 & 3 side by side: Phân bố + Nhận xét ─────────
            half_w = (CONTENT_W - 0.4*cm) / 2

            clean_tips = []
            for tip in cfg["tips"]:
                clean = re.sub(r'[^\x00-\x7F\u00C0-\u024F\u1E00-\u1EFF\u2013\u2014\u0300-\u036F ]', '', tip).strip()
                clean_tips.append(clean or tip)

            level_vn = level_label
            insights_text = [
                f"Chỉ số stress tổng thể của bạn đang ở mức {level_vn}.",
                "Hai yếu tố tác động nhiều nhất là Thể chất (24.7%) và Môi trường (24.2%).",
                "Yếu tố Tâm lý hiện không phải nguyên nhân chính.",
                "Chưa phát hiện nguy cơ stress kéo dài.",
            ]

            left_col = [SectionHeading("2", "PHÂN BỐ YẾU TỐ STRESS", lv_color, half_w, BOLD_FONT), Spacer(1, 4),
                        FactorBarChart(FACTOR_GROUPS, self._factor_sizes, half_w, BASE_FONT, BOLD_FONT, lv_color)]

            right_col = [SectionHeading("3", "NHẬN XÉT CHUYÊN SÂU", lv_color, half_w, BOLD_FONT), Spacer(1, 6)]
            for txt in insights_text:
                right_col.append(InsightCard(txt, lv_color, half_w, BASE_FONT, BOLD_FONT))
                right_col.append(Spacer(1, 4))

            two_col = Table(
                [[left_col, right_col]],
                colWidths=[half_w, half_w],
                hAlign="LEFT",
            )
            two_col.setStyle(TableStyle([
                ("VALIGN",       (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING",   (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
            ]))
            story.append(two_col)
            story.append(Spacer(1, GAP))

            # ── Section 4: Khuyến nghị cá nhân hóa (full width) ──────────
            rec_items = [SectionHeading("4", "KHUYẾN NGHỊ CÁ NHÂN HÓA", lv_color, CONTENT_W, BOLD_FONT), Spacer(1, 5)]
            # 2-column layout for recommendations
            mid = math.ceil(len(clean_tips) / 2)
            left_recs  = clean_tips[:mid]
            right_recs = clean_tips[mid:]
            rec_left  = []
            rec_right = []
            for i, tip in enumerate(left_recs, 1):
                rec_left.append(RecCard(i, tip, lv_color, half_w, BASE_FONT, BOLD_FONT))
                rec_left.append(Spacer(1, 4))
            for i, tip in enumerate(right_recs, mid + 1):
                rec_right.append(RecCard(i, tip, lv_color, half_w, BASE_FONT, BOLD_FONT))
                rec_right.append(Spacer(1, 4))

            rec_table = Table(
                [[rec_left, rec_right]],
                colWidths=[half_w, half_w],
                hAlign="LEFT",
            )
            rec_table.setStyle(TableStyle([
                ("VALIGN",       (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING",   (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
            ]))
            rec_items.append(rec_table)
            story.extend(rec_items)

            # ── Footer ────────────────────────────────────────────────────
            story.append(Spacer(1, GAP))
            story.append(HRFlowable(width="100%", thickness=0.5, color=GRAY_LINE, spaceAfter=4))
            footer_row = Table(
                [[
                    Paragraph(
                        "Báo cáo được tạo tự động từ hệ thống Stress Predictor v1.0  ·  "
                        "Không thay thế tư vấn hoặc chẩn đoán của chuyên gia y tế.",
                        ParagraphStyle("fl", fontName=BASE_FONT, fontSize=7, textColor=GRAY_MID, leading=10),
                    ),
                    Paragraph(
                        "www.stresspredictor.com  |  Hotline: 1900 1234",
                        ParagraphStyle("fr", fontName=BASE_FONT, fontSize=7, textColor=GRAY_MID, leading=10, alignment=2),
                    ),
                ]],
                colWidths=[CONTENT_W * 0.65, CONTENT_W * 0.35],
            )
            footer_row.setStyle(TableStyle([
                ("LEFTPADDING",  (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING",   (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
                ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(footer_row)

            # ── Build ─────────────────────────────────────────────────────
            doc = SimpleDocTemplate(
                path, pagesize=A4,
                leftMargin=1.8*cm, rightMargin=1.8*cm,
                topMargin=1.0*cm, bottomMargin=1.0*cm,
            )
            doc.build(story)

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