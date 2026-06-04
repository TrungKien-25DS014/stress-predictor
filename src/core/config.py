"""
src/core/config.py
------------------
Chứa các cài đặt cốt lõi, biến môi trường và Constants (Màu sắc, Font)
dùng chung cho toàn bộ ứng dụng Clinical Light.
"""

from PyQt5.QtGui import QFont

COLORS = {
    # Nền (Backgrounds)
    "bg_main":      "#F8F9FA",   
    "bg_sidebar":   "#FFFFFF",   
    "bg_panel":     "#FFFFFF",   
    "white":        "#FFFFFF",
    "bg":           "#F8F9FA",
    
    # Chữ (Text)
    "text_primary": "#1A2233",   
    "text_muted":   "#6C757D",   
    "text":         "#1A2233",
    "muted":        "#6C757D",
    
    # Viền (Borders & Dividers)
    "divider":      "#E2E8F0",   
    "card_border":  "#DEE2E6",
    
    # Màu Brand (Xanh Y tế)
    "accent":       "#007AFF",   
    "accent_light": "#E8F3FF",   
    "accent_hover": "#0062CC",   
    "accent_dark":  "#0055CC",
    
    # Trạng thái (Status/Feedback)
    "success":      "#28A745",   
    "warning":      "#FFC107",   
    "danger":       "#DC3545",   
    
    # Gradient Brand & Gold
    "brand_top":    "#0A2463",
    "brand_mid":    "#1565C0",
    "brand_bot":    "#0D47A1",
    "gold":         "#D4AF37",
    
    # Input login
    "input_bg":     "#F7F6F2",
    "input_border": "#E5E2DA",
}

C = COLORS 

FONTS = {
    "brand":    QFont("Segoe UI Semibold", 14),
    "nav":      QFont("Segoe UI",          10),
    "heading":  QFont("Segoe UI Semibold", 13),
    "body":     QFont("Segoe UI",           9),
    "caption":  QFont("Segoe UI",           8),
    "greeting": QFont("Segoe UI Semibold", 11),
}