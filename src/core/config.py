import os
import json
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QObject, pyqtSignal

# =====================================================================
# 1. THEME SIGNAL — dùng để notify toàn app khi theme thay đổi
# =====================================================================
class _ThemeSignalBus(QObject):
    theme_changed = pyqtSignal(str)   # emits "light" or "dark"

theme_bus = _ThemeSignalBus()


# =====================================================================
# 2. CƠ CHẾ ĐỌC / GHI THEME
# =====================================================================
THEME_FILE = "app_theme.json"
CURRENT_THEME = "light"

if os.path.exists(THEME_FILE):
    try:
        with open(THEME_FILE, "r") as f:
            CURRENT_THEME = json.load(f).get("theme", "light")
    except Exception:
        pass


def save_theme_config(theme_name: str):
    """Lưu lựa chọn giao diện của người dùng vào file cục bộ"""
    with open(THEME_FILE, "w") as f:
        json.dump({"theme": theme_name}, f)


def apply_theme(theme_name: str):
    """
    Áp dụng theme mới ngay lập tức:
    - Cập nhật CURRENT_THEME, C, C toàn cục
    - Lưu vào file
    - Phát signal để các widget tự refresh
    """
    global CURRENT_THEME, COLORS, C
    CURRENT_THEME = theme_name
    COLORS = LIGHT_COLORS if theme_name == "light" else DARK_COLORS
    C = COLORS
    save_theme_config(theme_name)
    theme_bus.theme_changed.emit(theme_name)


# =====================================================================
# 3. BỘ MÀU GIAO DIỆN SÁNG (LIGHT MODE)
# =====================================================================
LIGHT_COLORS = {
    "bg_main":      "#F8F9FA",
    "bg_sidebar":   "#FFFFFF",
    "bg_panel":     "#FFFFFF",
    "white":        "#FFFFFF",
    "bg":           "#F8F9FA",
    "text_primary": "#1A2233",
    "text_muted":   "#6C757D",
    "text":         "#1A2233",
    "muted":        "#6C757D",
    "divider":      "#E2E8F0",
    "card_border":  "#DEE2E6",

    "accent":       "#007AFF",
    "accent_light": "#E8F3FF",
    "accent_hover": "#0062CC",
    "accent_dark":  "#0055CC",
    "accent_pressed": "#004FA3",
    "accent_light_pressed": "#D0E8FF",

    "success":      "#28A745",
    "warning":      "#FFC107",
    "danger":       "#DC3545",
    "success_bg":   "#E9F7EF",
    "warning_bg":   "#FFF9E6",
    "warning_text": "#856404",
    "danger_bg":    "#FDECEA",

    "btn_outline_bg":       "#F1F3F5",
    "btn_outline_border":   "#ADB5BD",
    "progress_gradient_end":"#34AADC",

    "brand_top":    "#0A2463", "brand_mid": "#1565C0", "brand_bot": "#0D47A1", "gold": "#D4AF37",
    "input_bg":     "#F7F6F2", "input_border": "#E5E2DA",

    "chart_blue":   "#4A90D9", "chart_purple": "#7B61FF", "chart_green": "#22C55E",
    "chart_amber":  "#F59E0B", "chart_red":    "#EF4444", "chart_darkred":"#9B1C1C",

    "dash_bg":      "#F3F6FB", "table_alt":    "#F8FAFC", "scroll_handle":"#D1D9E6",

    "detail_low_a": "#1DB954", "detail_low_b": "#0A8D3F", "detail_low_bg": "#E6F9EE", "detail_low_txt": "#0A6B2E",
    "detail_mid_a": "#F59E0B", "detail_mid_b": "#D97706", "detail_mid_bg": "#FFFBEA", "detail_mid_txt": "#7D5C00",
    "detail_high_a": "#EF4444", "detail_high_b": "#B91C1C", "detail_high_bg": "#FEE2E2", "detail_high_txt": "#7F1D1D",

    "factor_psy": "#8B5CF6", "factor_phy": "#EF4444", "factor_env": "#06B6D4", "factor_edu": "#F59E0B", "factor_soc": "#10B981",

    "hist_low_fg": "#16A34A", "hist_low_bg": "#F0FDF4", "hist_mid_fg": "#F59E0B", "hist_mid_bg": "#EFF6FF",
    "hist_high_fg": "#DC2626", "hist_high_bg": "#FEF2F2", "hist_avg_fg": "#B8860B", "hist_avg_bg": "#FFFBEB",
    "hist_all_fg": "#6B7280", "hist_all_bg": "#F3F4F6", "hist_table_alt": "#F8FAFC", "hist_header": "#F1F5F9",

    "btn_gold_edge": "#C89B3C", "btn_gold_mid": "#F7DA83", "btn_gold_h_edge": "#D9AF4E",
    "btn_gold_h_mid": "#FCE69C", "btn_gold_p_edge": "#B08226", "btn_gold_p_mid": "#E0C161", "btn_gold_border": "#B8862D",

    "btn_retry_bg": "#F3F4F6", "btn_retry_fg": "#374151", "btn_retry_border": "#D1D5DB", "btn_retry_hover": "#E5E7EB",
    "btn_pdf_bg": "#EFF6FF", "btn_pdf_fg": "#1D4ED8", "btn_pdf_border": "#93C5FD", "btn_pdf_hover": "#DBEAFE", "btn_pdf_pressed": "#BFDBFE",

    "glass_light": "rgba(255,255,255,0.22)", "glass_mid": "rgba(255,255,255,0.28)",
    "glass_high": "rgba(255,255,255,0.85)", "glass_dark": "rgba(255,255,255,0.20)",
    "glass_hover": "rgba(255,255,255,0.38)", "glass_pressed": "rgba(0,0,0,0.15)", "glass_full": "rgba(255,255,255,0.9)",
}


# =====================================================================
# 4. BỘ MÀU TỐI (DARK MODE)
# =====================================================================
DARK_COLORS = LIGHT_COLORS.copy()
DARK_COLORS.update({
    # ── Nền chính ── xám xanh trung tính, không quá tối đen
    "bg_main":      "#1C1F2E",   # nền page chính
    "bg_sidebar":   "#13151F",   # sidebar tối hơn 1 bậc
    "bg_panel":     "#13151F",   # panel phải
    "white":        "#242736",   # thay thế #FFFFFF → card/input bg
    "bg":           "#1C1F2E",

    # ── Chữ ── đủ sáng, không chói
    "text_primary": "#E8EDF5",   # chữ chính — gần trắng, hơi xanh lạnh
    "text_muted":   "#9BA5BB",   # chữ phụ — xám xanh rõ ràng
    "text":         "#E8EDF5",
    "muted":        "#9BA5BB",

    # ── Đường kẻ & viền ── nhìn thấy rõ nhưng không lấn át
    "divider":      "#2E3347",
    "card_border":  "#383D54",

    # ── Accent xanh dương ── sáng hơn, saturate hơn
    "accent":               "#5B9FFF",   # xanh sáng chính
    "accent_light":         "#1E2D50",   # nền accent nhạt (badge, bg hover)
    "accent_hover":         "#74AFFF",   # hover sáng hơn
    "accent_dark":          "#4A8FEF",
    "accent_pressed":       "#3A7FDF",
    "accent_light_pressed": "#172440",

    # ── Trạng thái ── nền đủ tương phản, chữ đủ sáng
    "success":      "#3DD68C",   # xanh lá sáng hơn
    "warning":      "#FFD166",   # vàng ấm
    "danger":       "#FF6B6B",   # đỏ san hô

    "success_bg":   "#1A3628",
    "warning_bg":   "#312508",
    "warning_text": "#FFD166",
    "danger_bg":    "#3A1A1A",

    # ── Input ──
    "input_bg":     "#2A2E42",
    "input_border": "#454B66",

    # ── Dashboard / bảng ──
    "dash_bg":      "#1C1F2E",
    "table_alt":    "#222538",
    "scroll_handle":"#454B66",

    # ── History badges ── nền đủ sáng để chữ màu đọc được
    "hist_low_fg":    "#3DD68C", "hist_low_bg":  "#1A3628",
    "hist_mid_fg":    "#FFD166", "hist_mid_bg":  "#312508",
    "hist_high_fg":   "#FF6B6B", "hist_high_bg": "#3A1A1A",
    "hist_avg_fg":    "#FFD166", "hist_avg_bg":  "#312508",
    "hist_all_fg":    "#9BA5BB", "hist_all_bg":  "#2A2E42",
    "hist_table_alt": "#222538",
    "hist_header":    "#2A2E42",

    # ── Buttons outline / retry ──
    "btn_outline_bg":     "#2A2E42",
    "btn_outline_border": "#454B66",
    "btn_retry_bg":       "#2A2E42",
    "btn_retry_fg":       "#E8EDF5",
    "btn_retry_border":   "#454B66",
    "btn_retry_hover":    "#333854",

    # ── Detail level cards ──
    "detail_low_bg":  "#1A3628", "detail_low_txt":  "#3DD68C",
    "detail_mid_bg":  "#312508", "detail_mid_txt":  "#FFD166",
    "detail_high_bg": "#3A1A1A", "detail_high_txt": "#FF8080",

    # ── Charts ── màu sáng hơn trên nền tối
    "chart_blue":    "#5B9FFF",
    "chart_purple":  "#A78BFA",
    "chart_green":   "#3DD68C",
    "chart_amber":   "#FFD166",
    "chart_red":     "#FF6B6B",
    "chart_darkred": "#FF4444",

    # ── Glass effects ──
    "glass_light":   "rgba(255,255,255,0.06)",
    "glass_mid":     "rgba(255,255,255,0.10)",
    "glass_high":    "rgba(255,255,255,0.18)",
    "glass_dark":    "rgba(0,0,0,0.30)",
    "glass_hover":   "rgba(255,255,255,0.14)",
    "glass_pressed": "rgba(0,0,0,0.40)",
    "glass_full":    "rgba(30,33,50,0.95)",

    # ── Factor colors (giữ nguyên, đã đủ sáng) ──
    "factor_psy": "#A78BFA",
    "factor_phy": "#FF6B6B",
    "factor_env": "#22D3EE",
    "factor_edu": "#FFD166",
    "factor_soc": "#3DD68C",

    # ── PDF button ──
    "btn_pdf_bg":      "#1E2D50",
    "btn_pdf_fg":      "#74AFFF",
    "btn_pdf_border":  "#3A5A9A",
    "btn_pdf_hover":   "#253660",
    "btn_pdf_pressed": "#1A2848",

    # ── Progress bar ──
    "progress_gradient_end": "#5B9FFF",
})


# =====================================================================
# 5. KHỞI TẠO BỘ MÀU ĐANG DÙNG
# =====================================================================
COLORS = LIGHT_COLORS if CURRENT_THEME == "light" else DARK_COLORS
C = COLORS


FONTS = {
    "brand":    QFont("Segoe UI Semibold", 14),
    "nav":      QFont("Segoe UI",          10),
    "heading":  QFont("Segoe UI Semibold", 13),
    "body":     QFont("Segoe UI",           9),
    "caption":  QFont("Segoe UI",           8),
    "greeting": QFont("Segoe UI Semibold", 11),
}