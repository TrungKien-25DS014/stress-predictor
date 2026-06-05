from __future__ import annotations

from typing import Any, Optional

from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QColor, QFont, QBrush, QPainter, QPen, QLinearGradient
from PyQt5.QtWidgets import (
    QDialog, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget,
)

from src.core.config import C

_FONT = "Segoe UI"

DETAIL_CONFIG: dict[str, dict] = {
    "Thấp": {
        "gradient_a": C["detail_low_a"],
        "gradient_b": C["detail_low_b"],
        "ring_color": C["detail_low_a"],
        "tag_bg":     C["detail_low_bg"],
        "tag_text":   C["detail_low_txt"],
        "bar_pct":    20,
        "emoji":      "😌",
        "sublabel":   "Mức độ stress của bạn nằm trong ngưỡng kiểm soát tốt",
        "tips": [
            "🧘 Duy trì thói quen ngủ đủ 7–8 giờ mỗi đêm",
            "🏃 Tập thể dục nhẹ 30 phút mỗi ngày",
            "🤝 Giữ kết nối xã hội với bạn bè và gia đình",
        ],
    },
    "Bình thường": {
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
    "Cao": {
        "gradient_a": C["detail_high_a"],
        "gradient_b": C["detail_high_b"],
        "ring_color": C["detail_high_a"],
        "tag_bg":     C["detail_high_bg"],
        "tag_text":   C["detail_high_txt"],
        "bar_pct":    85,
        "emoji":      "😰",
        "sublabel":   "Mức stress của bạn cần được quan tâm nghiêm túc",
        "tips": [
            "🏥 Liên hệ chuyên gia tâm lý hoặc cố vấn học tập",
            "📵 Giới hạn mạng xã hội — tối đa 30 phút/ngày",
            "🧘 Thiền định hoặc yoga 15–20 phút mỗi sáng",
            "📓 Viết nhật ký cảm xúc để nhận biết nguồn gốc stress",
            "☎️ Đường dây hỗ trợ: 1800 599 920 (miễn phí 24/7)",
        ],
    },
}

FACTOR_GROUPS: list[dict] = [
    {"name": "Tâm lý",     "color": C["factor_psy"]},
    {"name": "Thể chất",   "color": C["factor_phy"]},
    {"name": "Môi trường", "color": C["factor_env"]},
    {"name": "Học tập",    "color": C["factor_edu"]},
    {"name": "Xã hội",     "color": C["factor_soc"]},
]

_SCALE_LEVELS = [
    ("Thấp",        C["detail_low_a"]),
    ("Bình thường", C["detail_mid_a"]),
    ("Cao",         C["detail_high_a"]),
]


class ArcRingWidget(QWidget):
    '''
    Widget biểu đồ dạng vòng cung (Arc) với hiệu ứng chuyển động (Animation).
    Trực quan hóa mức độ stress tổng quát dưới dạng phần trăm (%).
    '''
    def __init__(self, color: str, pct: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._color   = QColor(color)
        self._target  = max(0, min(100, pct))
        self._current = 0
        self.setMinimumSize(180, 130)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(16)

    def _tick(self) -> None:
        '''Xử lý bước lặp animation chạy thông số % từ 0 đến ngưỡng chỉ định.'''
        if self._current < self._target:
            self._current = min(self._current + 3, self._target)
            self.update()

    def paintEvent(self, _) -> None:
        '''Tạo hình nền xám nhạt và đường vòng cung dải màu tương ứng.'''
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        arc_h = h - 30
        side  = min(w, arc_h * 2) - 20
        r     = side // 2
        cx    = w // 2
        cy    = arc_h

        p.setPen(QPen(QColor(C['divider']), 12, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(cx - r, cy - r, 2 * r, 2 * r, 0 * 16, 180 * 16)

        sweep = int(self._current / 100 * 180)
        grad  = QLinearGradient(cx - r, cy, cx + r, cy)
        grad.setColorAt(0, self._color.lighter(120))
        grad.setColorAt(1, self._color)
        p.setPen(QPen(grad, 12, Qt.SolidLine, Qt.RoundCap))
        p.drawArc(cx - r, cy - r, 2 * r, 2 * r, 180 * 16, -sweep * 16)

        p.setPen(QPen(self._color))
        p.setFont(QFont(_FONT, 15, QFont.Bold))
        p.drawText(cx - 35, cy + 6, 70, 24, Qt.AlignCenter, f"{self._current}%")
        p.end()


class DonutMiniWidget(QWidget):
    '''
    Widget biểu đồ bánh quy (Donut) tối giản, không sử dụng Matplotlib 
    để đảm bảo hiệu năng, chuyên dùng phân tích tỷ trọng yếu tố.
    '''
    def __init__(
        self,
        sizes: list[float],
        colors: list[str],
        labels: list[str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._sizes  = sizes
        self._colors = [QColor(c) for c in colors]
        self._labels = labels
        self.setMinimumSize(160, 160)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def paintEvent(self, _) -> None:
        '''Dựng hình chiếc bánh bằng các lớp cung theo tỷ trọng và khoét lỗ trung tâm.'''
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h   = self.width(), self.height()
        side   = min(w, h) - 20
        x = (w - side) // 2
        y = (h - side) // 2

        total = sum(self._sizes) or 1
        angle = 90 * 16
        for size, color in zip(self._sizes, self._colors):
            span = int(size / total * 360 * 16)
            p.setBrush(QBrush(color))
            p.setPen(Qt.NoPen)
            p.drawPie(x, y, side, side, angle, span)
            angle += span

        hole = int(side * 0.52)
        p.setBrush(QBrush(QColor(C['white'])))
        p.drawEllipse((w - hole) // 2, (h - hole) // 2, hole, hole)
        p.end()


class DetailDialog(QDialog):
    '''
    Hộp thoại chi tiết báo cáo lịch sử. 
    Trực quan hóa cấu trúc điểm phân bổ 5 mặt sức khỏe ở quá khứ.
    '''
    def __init__(
        self,
        record: dict[str, Any],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent, Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        self._rec        = record
        self._level_name = record.get("level", "Bình thường")
        self._cfg        = DETAIL_CONFIG.get(self._level_name, DETAIL_CONFIG["Bình thường"])
        self._factors    = record.get("factors", [1.0] * 5)
        self._drag_pos: Optional[QPoint] = None

        self._build_ui()
        self.resize(720, 620)

    def _build_ui(self) -> None:
        '''Khởi tạo thiết kế hộp thoại chi tiết gồm 3 mảng: Header, thân và Footer.'''
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        card = QFrame()
        card.setObjectName("detail_card")
        card.setStyleSheet(f"""
            QFrame#detail_card {{
                background    : {C['white']};
                border-radius : 20px;
                border        : 1.5px solid {C['card_border']};
            }}
        """)
        outer.addWidget(card)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(self._make_header())

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        body_lay = QHBoxLayout(body)
        body_lay.setContentsMargins(24, 18, 24, 18)
        body_lay.setSpacing(20)
        body_lay.addLayout(self._make_left_col(), stretch=5)
        body_lay.addWidget(self._make_right_col(), stretch=4)
        lay.addWidget(body, 1)

        lay.addWidget(self._make_footer())

    def _make_header(self) -> QWidget:
        '''Chứa thông tin tóm tắt và đánh giá cấp độ nổi bật qua background dải màu (gradient).'''
        cfg = self._cfg
        rec = self._rec

        header = QWidget()
        header.setFixedHeight(110)
        header.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {cfg['gradient_a']}, stop:1 {cfg['gradient_b']}
            );
            border-top-left-radius : 20px;
            border-top-right-radius: 20px;
        """)

        lay = QHBoxLayout(header)
        lay.setContentsMargins(24, 14, 18, 14)
        lay.setSpacing(14)

        badge = QFrame()
        badge.setFixedSize(62, 62)
        badge.setStyleSheet(f"QFrame {{ background: {C.get('glass_light', 'rgba(255,255,255,0.22)')}; border-radius: 31px; }}")
        bl = QVBoxLayout(badge)
        bl.setContentsMargins(0, 0, 0, 0)
        el = QLabel(cfg["emoji"])
        el.setFont(QFont("Segoe UI Emoji", 26))
        el.setAlignment(Qt.AlignCenter)
        el.setStyleSheet("background: transparent; color: white;")
        bl.addWidget(el)

        txt = QVBoxLayout()
        txt.setSpacing(2)

        tag_lbl = QLabel(f"  Đánh giá: {self._level_name}  ")
        tag_lbl.setFont(QFont(_FONT + " Semibold", 8))
        tag_lbl.setStyleSheet(f"background: {C.get('glass_mid', 'rgba(255,255,255,0.28)')}; color: white; border-radius: 10px; padding: 2px 0;")
        tag_lbl.setFixedHeight(22)
        tag_lbl.setMaximumWidth(180)

        title_lbl = QLabel("Báo cáo chi tiết Stress")
        title_lbl.setFont(QFont(_FONT, 15, QFont.Black))
        title_lbl.setStyleSheet("color: white; background: transparent;")

        date_lbl = QLabel(f"🗓  {rec.get('datetime', '—')}")
        date_lbl.setFont(QFont(_FONT, 9))
        date_lbl.setStyleSheet(f"color: {C.get('glass_high', 'rgba(255,255,255,0.85)')}; background: transparent;")

        txt.addWidget(tag_lbl)
        txt.addWidget(title_lbl)
        txt.addWidget(date_lbl)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(34, 34)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setFont(QFont(_FONT, 11))
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: {C.get('glass_dark', 'rgba(255,255,255,0.20)')};
                color: white; border-radius: 17px; border: none;
            }}
            QPushButton:hover {{ background: {C.get('glass_hover', 'rgba(255,255,255,0.38)')}; }}
        """)
        close_btn.clicked.connect(self.accept)

        lay.addWidget(badge)
        lay.addLayout(txt, 1)
        lay.addWidget(close_btn, alignment=Qt.AlignTop)
        return header

    def _make_left_col(self) -> QVBoxLayout:
        '''Cột bên trái tích hợp thẻ hiển thị % stress tổng hợp, khung thang mức độ và phần gợi ý.'''
        cfg = self._cfg
        col = QVBoxLayout()
        col.setSpacing(14)

        arc_card = self._card()
        ac_lay = QVBoxLayout(arc_card)
        ac_lay.setContentsMargins(18, 14, 18, 10)
        ac_lay.setSpacing(4)

        arc_title = QLabel("Chỉ số stress tổng thể")
        arc_title.setFont(QFont(_FONT + " Semibold", 9))
        arc_title.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")
        arc_title.setAlignment(Qt.AlignCenter)

        arc = ArcRingWidget(color=cfg["ring_color"], pct=cfg["bar_pct"])
        arc.setFixedHeight(130)

        ac_lay.addWidget(arc_title)
        ac_lay.addWidget(arc)
        col.addWidget(arc_card)

        scale = self._card()
        sc_lay = QVBoxLayout(scale)
        sc_lay.setContentsMargins(16, 12, 16, 12)
        sc_lay.setSpacing(6)

        sc_title = QLabel("Thang đo 3 mức độ")
        sc_title.setFont(QFont(_FONT + " Semibold", 9))
        sc_title.setStyleSheet(f"color: {C['text_primary']}; background: transparent;")
        sc_lay.addWidget(sc_title)

        bar_row = QHBoxLayout()
        bar_row.setSpacing(4)
        lbl_row = QHBoxLayout()
        lbl_row.setSpacing(4)

        for name, color in _SCALE_LEVELS:
            active = (name == self._level_name)

            seg = QFrame()
            seg.setFixedHeight(8)
            seg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            bg_color = color if active else C['divider']
            seg.setStyleSheet(f"background: {bg_color}; border-radius: 4px;")
            bar_row.addWidget(seg)

            lbl2 = QLabel(f"{'▶ ' if active else ''}{name}")
            lbl2.setFont(QFont(_FONT + (" Semibold" if active else ""), 8))
            text_color = color if active else C['text_muted']
            lbl2.setStyleSheet(f"color: {text_color}; background: transparent;")
            lbl2.setAlignment(Qt.AlignCenter)
            lbl_row.addWidget(lbl2)

        sc_lay.addLayout(bar_row)
        sc_lay.addLayout(lbl_row)
        col.addWidget(scale)

        tips_card = QFrame()
        tips_card.setStyleSheet(f"QFrame {{ background: {cfg['tag_bg']}; border: none; border-radius: 14px; }}")
        t_lay = QVBoxLayout(tips_card)
        t_lay.setContentsMargins(16, 12, 16, 12)
        t_lay.setSpacing(8)

        h_row = QHBoxLayout()
        h_row.setSpacing(8)
        ico = QLabel("💡")
        ico.setFont(QFont("Segoe UI Emoji", 12))
        ico.setStyleSheet("background: transparent;")
        ttl = QLabel("Gợi ý cải thiện")
        ttl.setFont(QFont(_FONT + " Semibold", 10))
        ttl.setStyleSheet(f"color: {C['text_primary']}; background: transparent;")
        h_row.addWidget(ico)
        h_row.addWidget(ttl, 1)
        t_lay.addLayout(h_row)

        for tip in cfg["tips"]:
            tl = QLabel(tip)
            tl.setFont(QFont(_FONT, 9))
            tl.setWordWrap(True)
            tl.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")
            t_lay.addWidget(tl)

        t_lay.addStretch()
        col.addWidget(tips_card, 1)
        return col

    def _make_right_col(self) -> QFrame:
        '''Khu vực chứa thống kê Donut, các nhóm yếu tố tác động và điểm chi tiết.'''
        rec  = self._rec
        card = self._card()
        lay  = QVBoxLayout(card)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(12)

        rt = QLabel("📊  Phân bổ yếu tố stress")
        rt.setFont(QFont(_FONT + " Semibold", 10))
        rt.setStyleSheet(f"color: {C['text_primary']}; background: transparent;")
        lay.addWidget(rt)

        sizes  = self._factors
        colors = [g["color"] for g in FACTOR_GROUPS]
        labels = [g["name"]  for g in FACTOR_GROUPS]
        donut  = DonutMiniWidget(sizes, colors, labels)
        donut.setMinimumHeight(160)
        lay.addWidget(donut, 1)

        total = sum(sizes) or 1
        for grp, size in zip(FACTOR_GROUPS, sizes):
            pct = size / total * 100
            row = QHBoxLayout()
            row.setSpacing(8)

            dot = QLabel("●")
            dot.setFont(QFont(_FONT, 11))
            dot.setFixedWidth(14)
            dot.setStyleSheet(f"color: {grp['color']}; background: transparent;")

            nm = QLabel(grp["name"])
            nm.setFont(QFont(_FONT, 8))
            nm.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")

            pct_lbl = QLabel(f"{pct:.1f}%")
            pct_lbl.setFont(QFont(_FONT + " Semibold", 8))
            pct_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            pct_lbl.setStyleSheet(f"color: {grp['color']}; background: transparent;")

            mini_bar = QFrame()
            mini_bar.setFixedHeight(4)
            mini_bar.setFixedWidth(max(8, int(pct * 0.8)))
            mini_bar.setStyleSheet(f"background: {grp['color']}; border-radius: 2px;")

            row.addWidget(dot)
            row.addWidget(nm, 1)
            row.addWidget(mini_bar)
            row.addWidget(pct_lbl)
            lay.addLayout(row)

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {C['divider']}; border: none;")
        lay.addWidget(div)

        info_data = [
            ("Điểm stress", str(rec.get("score", "—"))),
            ("Mức lo âu",   f"{rec.get('anxiety_level', '—')} / 21"),
            ("Giờ ngủ",     f"{rec.get('sleep_hours', '—')} giờ"),
        ]
        for label, value in info_data:
            irow = QHBoxLayout()
            il = QLabel(label)
            il.setFont(QFont(_FONT, 9))
            il.setStyleSheet(f"color: {C['text_muted']}; background: transparent;")
            iv = QLabel(value)
            iv.setFont(QFont(_FONT + " Semibold", 9))
            iv.setStyleSheet(f"color: {C['text_primary']}; background: transparent;")
            iv.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            irow.addWidget(il, 1)
            irow.addWidget(iv)
            lay.addLayout(irow)

        return card

    def _make_footer(self) -> QFrame:
        '''Dải chứa nút thao tác thoát hộp thoại, nằm ở cuối giao diện.'''
        cfg = self._cfg
        footer = QFrame()
        footer.setStyleSheet(f"""
            QFrame {{
                background              : {C['bg_main']};
                border-top              : 1px solid {C['divider']};
                border-bottom-left-radius : 20px;
                border-bottom-right-radius: 20px;
            }}
        """)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(24, 14, 24, 14)

        close_btn = QPushButton("✅  Đóng báo cáo")
        close_btn.setFixedHeight(44)
        close_btn.setFont(QFont(_FONT + " Semibold", 9))
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 {cfg['gradient_a']}, stop:1 {cfg['gradient_b']});
                color: {C['white']}; border: none; border-radius: 10px;
            }}
            QPushButton:hover   {{ opacity: 0.9; }}
            QPushButton:pressed {{ background: {cfg['gradient_b']}; }}
        """)
        close_btn.clicked.connect(self.accept)
        fl.addWidget(close_btn)
        return footer

    @staticmethod
    def _card() -> QFrame:
        '''Trả về khung giao diện với đường viền bo nhẹ phổ quát.'''
        c = QFrame()
        c.setStyleSheet(f"QFrame {{ background: {C['white']}; border: none; border-radius: 14px; }}")
        return c

    def mousePressEvent(self, e) -> None:
        '''Cho phép bắt đầu di chuyển khung báo cáo từ bất kỳ vị trí trống nào.'''
        if e.button() == Qt.LeftButton:
            self._drag_pos = e.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e) -> None:
        '''Cập nhật liên tục tọa độ thả cửa sổ.'''
        if e.buttons() == Qt.LeftButton and self._drag_pos:
            self.move(e.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, e) -> None:
        '''Giải phóng con trỏ khi hoàn tất.'''
        self._drag_pos = None

    def showEvent(self, e) -> None:
        '''Canh giữa hộp thoại ngay khi vừa hiển thị.'''
        super().showEvent(e)
        if self.parent():
            pr = self.parent().frameGeometry()
            self.move(
                pr.center().x() - self.width()  // 2,
                pr.center().y() - self.height() // 2,
            )