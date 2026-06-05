import os
import json
from PyQt5.QtGui import QFont

# 1. CƠ CHẾ ĐỌC / GHI THEME
THEME_FILE = "app_theme.json"
CURRENT_THEME = "light"

# Đọc theme hiện tại nếu file tồn tại
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


# =====================================================================
# 2. BỘ MÀU GIAO DIỆN SÁNG (LIGHT MODE)
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
# 3. BỘ MÀU TỐI (DARK MODE)
# =====================================================================
DARK_COLORS = LIGHT_COLORS.copy()
DARK_COLORS.update({
    "bg_main":      "#121212",   
    "bg_sidebar":   "#1E1E1E",   
    "bg_panel":     "#1E1E1E",   
    "white":        "#1E1E1E",    # Thẻ nền trắng giờ chuyển thành xám đen
    "bg":           "#121212",
    "text_primary": "#E0E0E0",    # Chữ đen thành chữ trắng xám
    "text_muted":   "#8B949E",   
    "text":         "#E0E0E0",
    "muted":        "#8B949E",
    "divider":      "#2C2C2C",    
    "card_border":  "#333333",
    
    "accent_light": "#1A2B4C",    # Highlight màu xanh hạ tone tối
    "input_bg":     "#2A2A2A", 
    "input_border": "#3A3A3A",
    "dash_bg":      "#121212", 
    "table_alt":    "#242424", 
    "scroll_handle":"#4A4A4A",
    
    "success_bg":   "#173320",
    "warning_bg":   "#3A2D0D",
    "warning_text": "#FFC107",
    "danger_bg":    "#3B1C1E",
    
    "hist_low_bg": "#173320", "hist_mid_bg": "#1A2B4C", "hist_high_bg": "#3B1C1E",
    "hist_avg_bg": "#3A2D0D", "hist_all_bg": "#2A2A2A", "hist_table_alt": "#242424", "hist_header": "#2A2A2A",
    
    "btn_outline_bg":       "#2A2A2A",
    "btn_outline_border":   "#4A4A4A",
    "btn_retry_bg":         "#2A2A2A",
    "btn_retry_fg":         "#E0E0E0",
    "btn_retry_border":     "#4A4A4A",
    "btn_retry_hover":      "#333333",
})

# Xác định bộ màu đang được nạp
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