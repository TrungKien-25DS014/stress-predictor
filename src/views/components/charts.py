import datetime
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Import cấu hình màu chung
from src.core.config import C

class CanvasChart(FigureCanvas):
    """
    Widget biểu đồ Matplotlib nhúng trực tiếp vào layout PyQt5.

    Vẽ đường xu hướng stress theo thời gian với:
      • Đường chính màu gradient xanh-tím.
      • Vùng fill phía dưới đường (alpha thấp).
      • Các điểm dữ liệu highlight bằng scatter.
      • Đường ngưỡng trung bình (dashed).
    """

    # Đồng bộ hoàn toàn màu sắc với palette chung từ config.py
    _LINE_COLOR   = C["chart_blue"]
    _FILL_COLOR   = C["chart_blue"]
    _AVG_COLOR    = C["chart_amber"]
    _POINT_COLOR  = C["chart_purple"]
    _BG_COLOR     = C["white"]
    _GRID_COLOR   = C["divider"]
    _TEXT_COLOR   = C["text_muted"]

    def __init__(self, parent: QWidget | None = None) -> None:
        self._fig = Figure(figsize=(6, 3.5), dpi=96, facecolor=self._BG_COLOR)
        super().__init__(self._fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(220)

        self._ax = self._fig.add_subplot(111)
        self._configure_axes()
        self._draw_empty_state()

    # ── Public API ──────────────────────────────────────────────────────────
    def plot(self, dates: list[datetime.date], scores: list[float]) -> None:
        """
        Vẽ lại toàn bộ biểu đồ với dữ liệu mới.

        Args:
            dates:  Danh sách datetime.date hoặc datetime.datetime.
            scores: Điểm stress tương ứng (0–100).
        """
        self._ax.cla()
        self._configure_axes()

        if not dates or not scores:
            self._draw_empty_state()
            self.draw()
            return

        # Đảm bảo cùng độ dài
        n = min(len(dates), len(scores))
        dates, scores = dates[:n], scores[:n]

        # Chuyển date → số để matplotlib xử lý
        x = mdates.date2num(dates)
        y = scores

        avg = sum(scores) / len(scores)

        # ── Vùng fill ───────────────────────────────────────────────────────
        self._ax.fill_between(
            x, y, alpha=0.12,
            color=self._FILL_COLOR, linewidth=0,
        )

        # ── Đường chính ─────────────────────────────────────────────────────
        self._ax.plot(
            x, y,
            color=self._LINE_COLOR, linewidth=2.2,
            solid_capstyle="round", solid_joinstyle="round",
            zorder=3,
        )

        # ── Điểm dữ liệu ────────────────────────────────────────────────────
        self._ax.scatter(
            x, y,
            color=self._POINT_COLOR, s=42, zorder=4,
            edgecolors="white", linewidths=1.5,
        )

        # ── Đường trung bình (dashed) ────────────────────────────────────────
        self._ax.axhline(
            avg, linestyle="--", linewidth=1.2,
            color=self._AVG_COLOR, alpha=0.8,
            label=f"Trung bình: {avg:.1f}",
        )
        self._ax.legend(
            loc="upper right", fontsize=9,
            frameon=True, framealpha=0.9,
            edgecolor=self._GRID_COLOR,
        )

        # ── Trục X: định dạng ngày ───────────────────────────────────────────
        self._ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        self._ax.xaxis_date()
        self._fig.autofmt_xdate(rotation=30, ha="right")

        # ── Trục Y: giới hạn ────────────────────────────────────────────────
        self._ax.set_ylim(0, 105)
        self._ax.set_yticks(range(0, 101, 20))

        self._fig.tight_layout(pad=1.6)
        self.draw()

    # ── Private ─────────────────────────────────────────────────────────────
    def _configure_axes(self) -> None:
        ax = self._ax
        ax.set_facecolor(self._BG_COLOR)
        ax.tick_params(colors=self._TEXT_COLOR, labelsize=9)
        ax.set_ylabel("Điểm stress", fontsize=10, color=self._TEXT_COLOR, labelpad=8)
        ax.set_xlabel("Ngày", fontsize=10, color=self._TEXT_COLOR, labelpad=6)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        for spine in ("left", "bottom"):
            ax.spines[spine].set_color(self._GRID_COLOR)
        ax.yaxis.grid(True, color=self._GRID_COLOR, linewidth=0.8, linestyle="--")
        ax.set_axisbelow(True)
        self._fig.patch.set_facecolor(self._BG_COLOR)

    def _draw_empty_state(self) -> None:
        self._ax.text(
            0.5, 0.5,
            "Chưa có dữ liệu biểu đồ",
            ha="center", va="center",
            transform=self._ax.transAxes,
            color=self._TEXT_COLOR, fontsize=12,
        )
        self.draw()