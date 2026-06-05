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

    # Màu đặc trưng cho Chart & Dashboard
    "chart_blue":   "#4A90D9",
    "chart_purple": "#7B61FF",
    "chart_green":  "#22C55E",
    "chart_amber":  "#F59E0B",
    "chart_red":    "#EF4444",
    "chart_darkred":"#9B1C1C",
    
    # Màu nền phụ cho Dashboard
    "dash_bg":      "#F3F6FB",
    "table_alt":    "#F8FAFC",
    "scroll_handle":"#D1D9E6",

    # Màu đặc trưng cho Detail Dialog (Gradients & Tags)
    "detail_low_a":     "#1DB954",
    "detail_low_b":     "#0A8D3F",
    "detail_low_bg":    "#E6F9EE",
    "detail_low_txt":   "#0A6B2E",
    
    "detail_mid_a":     "#F59E0B",
    "detail_mid_b":     "#D97706",
    "detail_mid_bg":    "#FFFBEA",
    "detail_mid_txt":   "#7D5C00",
    
    "detail_high_a":    "#EF4444",
    "detail_high_b":    "#B91C1C",
    "detail_high_bg":   "#FEE2E2",
    "detail_high_txt":  "#7F1D1D",
    
    # Màu cho 5 yếu tố stress (Donut Chart)
    "factor_psy":       "#8B5CF6", # Tâm lý
    "factor_phy":       "#EF4444", # Thể chất
    "factor_env":       "#06B6D4", # Môi trường
    "factor_edu":       "#F59E0B", # Học tập
    "factor_soc":       "#10B981", # Xã hội

    # Màu đặc trưng cho History (Tags & Stats)
    "hist_low_fg":      "#16A34A",
    "hist_low_bg":      "#F0FDF4",
    
    "hist_mid_fg":      "#F59E0B",
    "hist_mid_bg":      "#EFF6FF",
    
    "hist_high_fg":     "#DC2626",
    "hist_high_bg":     "#FEF2F2",
    
    "hist_avg_fg":      "#B8860B",
    "hist_avg_bg":      "#FFFBEB",
    
    "hist_all_fg":      "#6B7280",
    "hist_all_bg":      "#F3F4F6",
    
    "hist_table_alt":   "#F8FAFC",
    "hist_header":      "#F1F5F9",

    # Màu Gradient cho Gold Button (Login/Register)
    "btn_gold_edge":    "#C89B3C",
    "btn_gold_mid":     "#F7DA83",
    "btn_gold_h_edge":  "#D9AF4E",  # Hover edge
    "btn_gold_h_mid":   "#FCE69C",  # Hover mid
    "btn_gold_p_edge":  "#B08226",  # Pressed edge
    "btn_gold_p_mid":   "#E0C161",  # Pressed mid
    "btn_gold_border":  "#B8862D",  

    # Màu cho các nút phụ trong Result Dialog
    "btn_retry_bg":     "#F3F4F6",
    "btn_retry_fg":     "#374151",
    "btn_retry_border": "#D1D5DB",
    "btn_retry_hover":  "#E5E7EB",
    
    "btn_pdf_bg":       "#EFF6FF",
    "btn_pdf_fg":       "#1D4ED8",
    "btn_pdf_border":   "#93C5FD",
    "btn_pdf_hover":    "#DBEAFE",
    "btn_pdf_pressed":  "#BFDBFE",
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
