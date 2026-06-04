from __future__ import annotations

import datetime
from typing import Any

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QSizePolicy,
    QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush

from src.views.components.widgets import MetricCard
from src.views.components.charts import CanvasChart


# ============================================================================
# DashboardScreen
# ============================================================================
class DashboardScreen(QWidget):

    _CARD_ACCENTS: list[str] = ["#4A90D9", "#7B61FF", "#F59E0B", "#EF4444"]

    _STRESS_LEVELS: dict[tuple[int, int], tuple[str, str]] = {
        (0,  40):  ("Thấp",       "#22C55E"),
        (40, 65):  ("Trung bình", "#F59E0B"),
        (65, 85):  ("Cao",        "#EF4444"),
        (85, 101): ("Rất cao",    "#9B1C1C"),
    }

    _HEALTH_TIPS: list[str] = [
        "💧 Uống đủ 2 lít nước mỗi ngày giúp não hoạt động tốt hơn.",
        "🏃 Đi bộ 20 phút giúp giảm cortisol (hormone stress) hiệu quả.",
        "🧘 Thở 4-7-8: hít 4 giây, nín 7 giây, thở ra 8 giây.",
        "😴 Ngủ đủ 7–8 tiếng giúp phục hồi hệ thần kinh.",
        "🥦 Bổ sung rau xanh và omega-3 hỗ trợ chức năng não.",
        "📵 Nghỉ màn hình 10 phút mỗi giờ để mắt và não nghỉ ngơi.",
        "🎵 Nghe nhạc nhẹ 15 phút trước khi ngủ giúp giảm căng thẳng.",
    ]

    _TABLE_HEADERS: list[str] = ["Ngày / Giờ", "Điểm số", "Đánh giá"]

    # =========================================================================
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("DashboardScreen")
        self._build_ui()
        self._apply_style()

    # =========================================================================
    # PUBLIC API
    # =========================================================================
    def update_metrics(
        self,
        total_tests: int,
        monthly_tests: int,
        avg_stress: float,
        latest_stress: float,
    ) -> None:
        """Cập nhật 4 MetricCard ở hàng trên cùng."""
        self._card_total.set_value(str(total_tests))
        self._card_monthly.set_value(str(monthly_tests))
        self._card_avg.set_value(f"{avg_stress:.1f}")
        self._card_latest.set_value(f"{latest_stress:.1f}")

    def update_dashboard_data(
        self,
        summary_dict: dict[str, Any],
        chart_data: dict[str, list],
        history_list: list[dict[str, Any]],
    ) -> None:
        """
        Cập nhật toàn bộ dashboard từ dữ liệu database – một lần gọi duy nhất.

        Args:
            summary_dict:
                {
                    "total_tests":   int,
                    "monthly_tests": int,
                    "avg_stress":    float,   # 0–100
                    "latest_stress": float,
                }
            chart_data:
                {
                    "dates":  list[datetime.date | datetime.datetime],
                    "scores": list[float],    # 0–100
                }
            history_list:  list of
                {
                    "datetime": str,    # "2024-05-20 14:32"
                    "score":    float,
                }
        """
        self.update_metrics(
            total_tests   = summary_dict.get("total_tests",   0),
            monthly_tests = summary_dict.get("monthly_tests", 0),
            avg_stress    = float(summary_dict.get("avg_stress",    0.0)),
            latest_stress = float(summary_dict.get("latest_stress", 0.0)),
        )
        self._chart.plot(
            dates  = chart_data.get("dates",  []),
            scores = chart_data.get("scores", []),
        )
        self._populate_history_table(history_list)

    # =========================================================================
    # PRIVATE – BUILD UI
    # =========================================================================
    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 24)
        root.setSpacing(18)

        root.addWidget(self._build_top_bar())            # ① tiêu đề
        root.addWidget(self._build_analytics_row())      # ② 4 MetricCard
        root.addWidget(self._build_middle_panel(), 1)    # ③ chart full-width
        root.addWidget(self._build_bottom_panel(), 1)    # ④ table

    # ── ① Top bar ─────────────────────────────────────────────────────────────
    def _build_top_bar(self) -> QLabel:
        lbl = QLabel("Dashboard")
        lbl.setObjectName("PageTitle")
        f = QFont("Segoe UI", 20)
        f.setWeight(QFont.DemiBold)
        lbl.setFont(f)
        lbl.setContentsMargins(0, 0, 0, 4)
        return lbl

    # ── ② Analytics row – 4 × MetricCard ─────────────────────────────────────
    def _build_analytics_row(self) -> QWidget:
        wrap = QWidget()
        wrap.setObjectName("AnalyticsRow")
        row = QHBoxLayout(wrap)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)

        specs = [
            ("Tổng số lần test",     "–", self._CARD_ACCENTS[0]),
            ("Test trong tháng",     "–", self._CARD_ACCENTS[1]),
            ("Độ stress trung bình", "–", self._CARD_ACCENTS[2]),
            ("Độ stress gần nhất",   "–", self._CARD_ACCENTS[3]),
        ]
        cards: list[MetricCard] = []
        for title, value, accent in specs:
            card = MetricCard(title=title, value=value, accent_color=accent)
            card.setMinimumHeight(120)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            row.addWidget(card)
            cards.append(card)

        # Giữ tham chiếu để update_metrics() có thể gọi set_value()
        self._card_total, self._card_monthly, \
            self._card_avg, self._card_latest = cards
        return wrap

    # ── ③ Middle panel – CanvasChart full-width ──────────────────────────────
    def _build_middle_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("SectionPanel")
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(16, 16, 16, 16)
        vbox.setSpacing(8)
        vbox.addWidget(self._build_chart_side())
        return panel

    def _build_chart_side(self) -> QWidget:
        """Trái: tiêu đề + CanvasChart (tái sử dụng từ canvas_chart.py)."""
        box = QWidget()
        box.setObjectName("ChartBox")
        vbox = QVBoxLayout(box)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(8)

        lbl = QLabel("📈  Xu hướng stress theo thời gian")
        lbl.setObjectName("SectionTitle")
        vbox.addWidget(lbl)

        self._chart = CanvasChart()     # ← tái sử dụng CanvasChart
        vbox.addWidget(self._chart)
        return box

    # ── ④ Bottom panel – QTableWidget nhật ký ────────────────────────────────
    def _build_bottom_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("SectionPanel")
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(16, 14, 16, 14)
        vbox.setSpacing(10)

        lbl = QLabel("📋  Nhật ký kiểm tra gần đây")
        lbl.setObjectName("SectionTitle")
        vbox.addWidget(lbl)

        self._history_table = self._build_history_table()
        vbox.addWidget(self._history_table)
        return panel

    def _build_history_table(self) -> QTableWidget:
        tbl = QTableWidget(0, len(self._TABLE_HEADERS))
        tbl.setHorizontalHeaderLabels(self._TABLE_HEADERS)
        tbl.setObjectName("HistoryTable")
        tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)
        tbl.setShowGrid(False)                   # ← bảng phẳng, ẩn gridlines
        tbl.setAlternatingRowColors(True)
        tbl.verticalHeader().setVisible(False)   # ẩn cột số thứ tự
        tbl.setFocusPolicy(Qt.NoFocus)

        hh = tbl.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Stretch)           # Ngày/Giờ
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Điểm số
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Đánh giá
        hh.setHighlightSections(False)
        tbl.verticalHeader().setDefaultSectionSize(40)
        return tbl

    # =========================================================================
    # PRIVATE – DATA POPULATION
    # =========================================================================
    def _populate_history_table(self, history_list: list[dict[str, Any]]) -> None:
        """Xoá rồi điền lại toàn bộ bảng nhật ký."""
        self._history_table.setRowCount(0)

        for i, rec in enumerate(history_list):
            self._history_table.insertRow(i)
            score = float(rec.get("score", 0.0))
            level_label, badge_color = self._stress_level(score)

            c0 = QTableWidgetItem(str(rec.get("datetime", "–")))
            c0.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)

            c1 = QTableWidgetItem(f"{score:.1f}")
            c1.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
            c1.setFont(QFont("Segoe UI", 10, QFont.Bold))

            c2 = QTableWidgetItem(f"  {level_label}  ")
            c2.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
            c2.setForeground(QBrush(QColor(badge_color)))
            c2.setFont(QFont("Segoe UI", 10, QFont.Bold))

            for col, item in enumerate((c0, c1, c2)):
                self._history_table.setItem(i, col, item)

    # =========================================================================
    # PRIVATE – HELPERS
    # =========================================================================
    def _stress_level(self, score: float) -> tuple[str, str]:
        """Trả về (nhãn, màu hex) tương ứng với mức điểm stress."""
        for (lo, hi), (label, color) in self._STRESS_LEVELS.items():
            if lo <= score < hi:
                return label, color
        return "Không xác định", "#9CA3AF"

    # =========================================================================
    # STYLESHEET TOÀN CỤC
    # =========================================================================
    def _apply_style(self) -> None:
        self.setStyleSheet("""
            DashboardScreen { background-color: #F3F6FB; }

            QLabel#PageTitle {
                color: #1A1D2E;
            }

            QFrame#SectionPanel {
                background-color : #FFFFFF;
                border-radius    : 12px;
                border           : 1px solid #E8EDF2;
            }

            QLabel#SectionTitle {
                color       : #374151;
                font-family : "Segoe UI";
                font-size   : 13px;
                font-weight : 600;
            }

            QLabel#TipLabel {
                background-color : #EFF6FF;
                border-left      : 3px solid #4A90D9;
                border-radius    : 6px;
                padding          : 10px 12px;
                color            : #1E40AF;
                font-family      : "Segoe UI";
                font-size        : 12px;
            }

            QTableWidget#HistoryTable {
                background-color           : #FFFFFF;
                alternate-background-color : #F8FAFC;
                border      : none;
                outline     : none;
                font-family : "Segoe UI";
                font-size   : 12px;
                color       : #374151;
            }
            QTableWidget#HistoryTable::item          { padding:0 12px; border:none; }
            QTableWidget#HistoryTable::item:selected { background:#EFF6FF; color:#1A1D2E; }

            QHeaderView::section {
                background-color : #F8FAFC;
                color            : #6B7280;
                font-family      : "Segoe UI";
                font-size        : 11px;
                font-weight      : 600;
                padding          : 8px 12px;
                border           : none;
                border-bottom    : 2px solid #E8EDF2;
            }

            QScrollBar:vertical           { background:transparent; width:6px; margin:0; }
            QScrollBar::handle:vertical   { background:#D1D9E6; border-radius:3px; min-height:20px; }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical { height:0; }
        """)