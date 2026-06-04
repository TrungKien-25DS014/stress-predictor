from __future__ import annotations

from typing import Any

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QBrush
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSizePolicy,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QSpacerItem,
    QLineEdit, QMessageBox
)

# ---------------------------------------------------------------------------
# Import nội bộ (Cấu hình UI & Widgets)
# ---------------------------------------------------------------------------
try:
    from src.views.components.widgets import GlowLineEdit, GoldButton
    from src.core.config import COLORS, FONTS
    from src.views.screens.detail_dialog import DetailDialog
except ImportError:
    try:
        from detail_dialog import DetailDialog
    except ImportError:
        DetailDialog = None  
    GlowLineEdit = None
    GoldButton   = None
    COLORS = {
        "bg_main":      "#F8F9FA", "bg_panel":     "#FFFFFF", "white":        "#FFFFFF",
        "text_primary": "#1A2233", "text_muted":   "#6C757D", "accent":       "#007AFF",
        "accent_light": "#E8F3FF", "divider":      "#E2E8F0", "card_border":  "#DEE2E6",
        "gold":         "#D4AF37", "danger":       "#DC3545", "warning":      "#FFC107",
        "success":      "#28A745",
    }
    FONTS = {}

# ---------------------------------------------------------------------------
# Design Constants
# ---------------------------------------------------------------------------
_FONT_FAMILY = "Segoe UI"
_ROW_HEIGHT  = 52
_PAGE_SIZE   = 8
_RADIUS      = 12

_LEVEL_CONFIG: dict[str, tuple[str, str, str]] = {
    "Thấp"       : ("#16A34A", "#F0FDF4", "😌"),
    "Bình thường": ("#F59E0B", "#EFF6FF", "😐"),
    "Cao"        : ("#DC2626", "#FEF2F2", "😰"),
}

_COLUMNS: list[str] = ["STT", "Ngày / Giờ", "Mức lo âu", "Chất lượng ngủ", "Điểm Stress", "Đánh giá", "Thao tác"]


class _PageBtn(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(36)
        self.setMinimumWidth(110)
        self.setCursor(Qt.PointingHandCursor)
        self.setFont(QFont(_FONT_FAMILY, 9))
        self._style()

    def _style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['accent_light']}; color: {COLORS['accent']};
                border: 1px solid {COLORS['divider']}; border-radius: 8px;
                padding: 0 16px; font-weight: 600;
            }}
            QPushButton:hover {{ background: {COLORS['accent']}; color: #FFFFFF; }}
            QPushButton:disabled {{ background: {COLORS['bg_main']}; color: {COLORS['text_muted']}; border: 1px solid {COLORS['divider']}; }}
        """)


class HistoryScreen(QWidget):
    """Màn hình Lịch sử (View trong MVC) - Chỉ hiển thị dữ liệu và phát tín hiệu"""
    
    # Signal báo cho Controller biết người dùng muốn xóa bản ghi nào
    delete_requested = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("HistoryScreen")

        # Dữ liệu nội bộ (được cấp phát từ Controller)
        self._all_records:      list[dict[str, Any]] = []
        self._filtered_records: list[dict[str, Any]] = []
        self._current_page = 1
        self._total_pages  = 1

        self._build_ui()
        self._apply_style()

    # ── Public API (Được gọi từ Controller) ─────────────────────────────────
    def populate_table(self, records: list[dict[str, Any]]) -> None:
        """Nhận dữ liệu thật từ DB thông qua Controller và hiển thị"""
        processed = []
        for r in records:
            score = float(r.get("score", 0))
            level = self._score_to_level(score)
            processed.append({
                "id":            r.get("id", 0),
                "datetime":      r.get("datetime", "—"),
                "anxiety_level": r.get("anxiety_level", 0),
                "sleep_hours":   r.get("sleep_hours", 0),
                "score":         score,
                "level":         level,
                "factors":       r.get("factors", [1.0] * 5),
            })
            
        self._all_records      = processed
        self._filtered_records = processed[:]
        self._current_page     = 1
        
        # Cập nhật số liệu trên 3 thẻ thống kê động
        total = len(processed)
        n_cao = sum(1 for r in processed if r["level"] == "Cao")
        n_avg_s = sum(r["score"] for r in processed) / total if total else 0
        
        self._stat_total_lbl.setText(str(total))
        self._stat_high_lbl.setText(str(n_cao))
        self._stat_avg_lbl.setText(f"{n_avg_s:.1f}")

        self._update_total_pages()
        self._render_page()

    # ── Build UI ────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 22, 24, 16)
        root.setSpacing(16)

        root.addWidget(self._build_header())
        root.addWidget(self._build_stats_bar())

        card = QFrame()
        card.setObjectName("history_card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(0)

        cl.addWidget(self._build_toolbar())

        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setFixedHeight(1)
        div.setStyleSheet(f"background: {COLORS['divider']}; border: none;")
        cl.addWidget(div)

        self._table = self._build_table()
        cl.addWidget(self._table)

        root.addWidget(card, stretch=1)
        root.addWidget(self._build_pagination_bar())

    def _build_header(self) -> QWidget:
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        title_col = QVBoxLayout()
        title = QLabel("Lịch sử kiểm tra sức khỏe")
        title.setFont(QFont(_FONT_FAMILY, 17, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        sub = QLabel("Theo dõi toàn bộ nhật ký đánh giá mức độ stress của bạn")
        sub.setFont(QFont(_FONT_FAMILY, 9))
        sub.setStyleSheet(f"color: {COLORS['text_muted']};")
        title_col.addWidget(title)
        title_col.addWidget(sub)
        lay.addLayout(title_col, 1)
        return w

    def _build_stats_bar(self) -> QWidget:
        w = QWidget()
        w.setObjectName("stats_bar_container")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        self._stat_total_lbl = QLabel("0")
        self._stat_high_lbl = QLabel("0")
        self._stat_avg_lbl = QLabel("0.0")

        stats = [
            ("Tổng lần kiểm tra", self._stat_total_lbl, "#007AFF", "#E8F3FF", "stat_blue"),
            ("Mức Nguy Cơ Cao",   self._stat_high_lbl,  "#DC2626", "#FEF2F2", "stat_red"),
            ("Điểm Stress Trung Bình", self._stat_avg_lbl,   "#B8860B", "#FFFBEB", "stat_gold"),
        ]
        
        for label, val_lbl, fg, bg, obj_name in stats:
            card = QWidget()
            card.setObjectName(obj_name)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            card.setFixedHeight(72)
            card.setStyleSheet(f"QWidget#{obj_name} {{ background-color: {bg}; border: none; border-radius: 12px; }}")

            cl = QVBoxLayout(card)
            cl.setContentsMargins(18, 10, 18, 10)
            cl.setSpacing(1)

            val_lbl.setFont(QFont(_FONT_FAMILY, 20, QFont.Bold))
            val_lbl.setStyleSheet(f"color: {fg}; background: transparent; border: none;")

            name_lbl = QLabel(label)
            name_lbl.setFont(QFont(_FONT_FAMILY, 8))
            name_lbl.setStyleSheet(f"color: {fg}AA; background: transparent; border: none;")

            cl.addWidget(val_lbl)
            cl.addWidget(name_lbl)
            lay.addWidget(card)
        return w

    def _build_toolbar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("history_toolbar")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(10)

        self._search_box = QLineEdit(bar)
        self._search_box.setPlaceholderText("Tìm theo ngày hoặc mức đánh giá...")
        self._search_box.setFixedHeight(40)
        self._search_box.setMinimumWidth(260)
        self._search_box.setFont(QFont(_FONT_FAMILY, 10))
        self._search_box.setStyleSheet(f"QLineEdit {{ background: #FFFFFF; border: 1.5px solid {COLORS['divider']}; border-radius: 8px; padding: 0 12px; }}")
        self._search_box.textChanged.connect(self._on_search_changed)

        self._filter_btns: dict[str, QPushButton] = {}
        filter_frame = QWidget()
        ff_lay = QHBoxLayout(filter_frame)
        ff_lay.setContentsMargins(0, 0, 0, 0)
        ff_lay.setSpacing(6)

        filter_defs = [("Tất cả", "#6B7280", "#F3F4F6"), ("Thấp", "#16A34A", "#F0FDF4"), ("Bình thường", "#F59E0B", "#EFF6FF"), ("Cao", "#DC2626", "#FEF2F2")]
        for label, fg, bg in filter_defs:
            btn = QPushButton(label)
            btn.setFixedHeight(36)
            btn.setMinimumWidth(80)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setProperty("filter_label", label)
            btn.setProperty("fg", fg)
            btn.setProperty("bg", bg)
            self._set_filter_btn_style(btn, active=(label == "Tất cả"))
            btn.clicked.connect(lambda checked, l=label: self._on_filter_clicked(l))
            self._filter_btns[label] = btn
            ff_lay.addWidget(btn)

        self._active_filter = "Tất cả"
        self._record_count_label = QLabel()
        self._record_count_label.setFont(QFont(_FONT_FAMILY, 8))
        self._record_count_label.setStyleSheet(f"color: {COLORS['text_muted']};")

        lay.addWidget(self._search_box)
        lay.addWidget(filter_frame)
        lay.addSpacerItem(QSpacerItem(8, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))
        lay.addWidget(self._record_count_label)
        return bar

    @staticmethod
    def _set_filter_btn_style(btn: QPushButton, active: bool):
        fg = btn.property("fg")
        bg = btn.property("bg")
        if active:
            btn.setStyleSheet(f"QPushButton {{ background: {fg}; color: #FFFFFF; border: none; border-radius: 8px; padding: 0 12px; font-weight: 600; }}")
        else:
            btn.setStyleSheet(f"QPushButton {{ background: {bg}; color: {fg}; border: none; border-radius: 8px; padding: 0 12px; }} QPushButton:hover {{ background: {fg}22; }}")

    def _build_table(self) -> QTableWidget:
        tbl = QTableWidget()
        tbl.setObjectName("history_table")
        tbl.setColumnCount(len(_COLUMNS))
        tbl.setHorizontalHeaderLabels(_COLUMNS)
        tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        tbl.setSelectionBehavior(QAbstractItemView.SelectRows)
        tbl.setSelectionMode(QAbstractItemView.SingleSelection)
        tbl.setShowGrid(False)
        tbl.setAlternatingRowColors(True)
        tbl.verticalHeader().setVisible(False)
        tbl.setFocusPolicy(Qt.NoFocus)
        tbl.verticalHeader().setDefaultSectionSize(_ROW_HEIGHT)

        h = tbl.horizontalHeader()
        h.setSectionResizeMode(QHeaderView.Stretch)
        h.setHighlightSections(False)
        h.setFixedHeight(46)
        
        # Thiết lập độ rộng các cột cố định
        h.setSectionResizeMode(0, QHeaderView.Fixed); tbl.setColumnWidth(0, 50)
        h.setSectionResizeMode(5, QHeaderView.Fixed); tbl.setColumnWidth(5, 120)
        h.setSectionResizeMode(6, QHeaderView.Fixed); tbl.setColumnWidth(6, 170) # Nới rộng để chứa 2 nút (Chi tiết & Xóa)
        return tbl

    def _build_pagination_bar(self) -> QWidget:
        bar = QWidget()
        lay = QHBoxLayout(bar)
        self._prev_btn = _PageBtn("◀  Trước")
        self._prev_btn.clicked.connect(self._go_prev_page)
        self._page_label = QLabel("Trang 1 / 1")
        self._page_label.setFont(QFont(_FONT_FAMILY, 9))
        self._page_label.setMinimumWidth(100)
        self._page_label.setAlignment(Qt.AlignCenter)
        self._next_btn = _PageBtn("Sau  ▶")
        self._next_btn.clicked.connect(self._go_next_page)

        lay.addStretch()
        lay.addWidget(self._prev_btn)
        lay.addWidget(self._page_label)
        lay.addWidget(self._next_btn)
        lay.addStretch()
        return bar

    # ── Logic Xử Lý Phân Trang & Lọc ─────────────────────────────────────────
    def _update_total_pages(self):
        n = len(self._filtered_records)
        self._total_pages = max(1, (n + _PAGE_SIZE - 1) // _PAGE_SIZE)

    def _render_page(self):
        start = (self._current_page - 1) * _PAGE_SIZE
        page_records = self._filtered_records[start: start + _PAGE_SIZE]
        self._table.setRowCount(len(page_records))

        for row_idx, rec in enumerate(page_records):
            abs_idx = start + row_idx + 1
            level   = str(rec.get("level", "—"))
            
            cells = [
                str(abs_idx), 
                str(rec.get("datetime", "—")), 
                f"{rec.get('anxiety_level', '—')} / 21", 
                f"{rec.get('sleep_hours', '—')} / 5", 
                f"{rec.get('score', '—')}%", 
                level
            ]

            for col_idx, value in enumerate(cells):
                item = QTableWidgetItem(value)
                if col_idx == 0:
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                    item.setForeground(QBrush(QColor(COLORS["text_muted"])))
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

                if col_idx == 5:
                    cfg = _LEVEL_CONFIG.get(value)
                    if cfg:
                        fg, bg, _ = cfg
                        item.setForeground(QBrush(QColor(fg)))
                        item.setBackground(QBrush(QColor(bg)))
                        item.setFont(QFont(_FONT_FAMILY, 9, QFont.Bold))
                    item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
                self._table.setItem(row_idx, col_idx, item)

            # Cột Thao Tác (Có cả nút Chi Tiết và Nút Xóa)
            action_widget = QWidget()
            action_lay = QHBoxLayout(action_widget)
            action_lay.setContentsMargins(6, 6, 6, 6)
            action_lay.setSpacing(6)
            
            # Nút Chi tiết
            detail_btn = QPushButton("🔍 Chi tiết")
            detail_btn.setFixedHeight(32)
            detail_btn.setCursor(Qt.PointingHandCursor)
            level_cfg = _LEVEL_CONFIG.get(level, ("#6B7280", "#F3F4F6", ""))
            fg_c, bg_c, _ = level_cfg
            detail_btn.setStyleSheet(f"QPushButton {{ background: {bg_c}; color: {fg_c}; border: none; border-radius: 8px; font-weight: 600; padding: 0 8px;}} QPushButton:hover {{ background: {fg_c}; color: #FFFFFF; }}")
            detail_btn.clicked.connect(lambda checked, r=rec: self._open_detail(r))
            
            # Nút Xóa
            del_btn = QPushButton("🗑️")
            del_btn.setFixedHeight(32)
            del_btn.setFixedWidth(36)
            del_btn.setCursor(Qt.PointingHandCursor)
            del_btn.setStyleSheet(f"QPushButton {{ background: #FEE2E2; color: #DC2626; border: none; border-radius: 8px; font-weight: 600; }} QPushButton:hover {{ background: #DC2626; color: #FFFFFF; }}")
            del_btn.clicked.connect(lambda checked, r_id=rec["id"]: self._confirm_delete(r_id))
            
            action_lay.addWidget(detail_btn)
            action_lay.addWidget(del_btn)
            
            self._table.setCellWidget(row_idx, 6, action_widget)

        self._page_label.setText(f"Trang {self._current_page} / {self._total_pages}")
        self._prev_btn.setEnabled(self._current_page > 1)
        self._next_btn.setEnabled(self._current_page < self._total_pages)

        total = len(self._filtered_records)
        extra = f" (lọc từ {len(self._all_records)})" if total != len(self._all_records) else ""
        self._record_count_label.setText(f"{total} bản ghi{extra}")

    def _open_detail(self, record: dict[str, Any]):
        if DetailDialog:
            dlg = DetailDialog(record, parent=self)
            dlg.exec_()
            
    def _confirm_delete(self, record_id: int):
        reply = QMessageBox.question(
            self, 'Xác nhận xóa', 
            'Bạn có chắc chắn muốn xóa bản ghi đánh giá này khỏi lịch sử không?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Phát tín hiệu ra cho HistoryController bắt và xử lý xóa Database
            self.delete_requested.emit(record_id)

    # ── Lọc & Tìm Kiếm ──────────────────────────────────────────────────────
    def _on_filter_clicked(self, label: str):
        self._active_filter = label
        for btn_label, btn in self._filter_btns.items():
            self._set_filter_btn_style(btn, active=(btn_label == label))
        self._apply_filter()

    def _on_search_changed(self, keyword: str):
        self._apply_filter()

    def _apply_filter(self):
        kw = self._search_box.text().strip().lower()
        lvl_filter = self._active_filter

        result = self._all_records[:]
        if lvl_filter != "Tất cả":
            result = [r for r in result if r.get("level") == lvl_filter]
        if kw:
            result = [r for r in result if kw in str(r.get("datetime", "")).lower() or kw in str(r.get("level", "")).lower()]

        self._filtered_records = result
        self._current_page     = 1
        self._update_total_pages()
        self._render_page()

    def _go_prev_page(self):
        if self._current_page > 1:
            self._current_page -= 1
            self._render_page()

    def _go_next_page(self):
        if self._current_page < self._total_pages:
            self._current_page += 1
            self._render_page()

    @staticmethod
    def _score_to_level(score: float) -> str:
        if score < 34: return "Thấp"
        if score < 67: return "Bình thường"
        return "Cao"

    # ── CSS Tùy Chỉnh ────────────────────────────────────────────────────────
    def _apply_style(self):
        self.setStyleSheet(f"""
            HistoryScreen {{ background-color: {COLORS['bg_main']}; }}
            QFrame#history_card {{ background-color: {COLORS['white']}; border: 1px solid {COLORS['card_border']}; border-radius: {_RADIUS}px; }}
            QTableWidget#history_table {{ background-color: {COLORS['white']}; alternate-background-color: #F8FAFC; border: none; outline: 0; }}
            QTableWidget#history_table::item {{ border-bottom: 1px solid {COLORS['divider']}; padding-left: 10px; }}
            QHeaderView::section {{ background-color: #F1F5F9; color: {COLORS['text_muted']}; font-weight: 600; padding-left: 10px; border: none; border-bottom: 2px solid {COLORS['divider']}; }}
        """)