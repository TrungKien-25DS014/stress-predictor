import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from xgboost import XGBClassifier
import json
# ═══════════════════════════════════════════════════════════════
# 1. CẤU HÌNH ĐƯỜNG DẪN TỰ ĐỘNG
# ═══════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_PATH             = os.path.join(BASE_DIR, "data", "processed", "cleaned_data.csv")
MODEL_DIR             = os.path.join(BASE_DIR, "models")

OVERFITTING_THRESHOLD = 5.0   # % gap tối đa cho phép
RANDOM_STATE          = 42
N_SPLITS              = 5     # 5-fold CV


# ═══════════════════════════════════════════════════════════════
# 2. KHỞI TẠO MÔ HÌNH (ĐÃ TINH CHỈNH GIẢM OVERFIT)
# ═══════════════════════════════════════════════════════════════
def print_section(title: str):
    print(f"\n{'═' * 55}")
    print(f"  {title}")
    print(f"{'═' * 55}")

def get_random_forest():
    return RandomForestClassifier(
        n_estimators=300,
        max_depth=3,                # Giảm độ sâu cây
        min_samples_leaf=15,        # Tăng số mẫu tối thiểu ở node lá
        min_samples_split=20,       # Tăng số mẫu tối thiểu để chẻ nhánh
        max_features='log2',
        class_weight='balanced',
        random_state=RANDOM_STATE
    )

def get_xgboost():
    return XGBClassifier(
        n_estimators=500,           # Giảm số lượng cây xuống 500
        max_depth=2,                # Ép cây nông xuống tầng 2
        learning_rate=0.05,
        subsample=0.7,              # Lấy ngẫu nhiên 70% mẫu để train mỗi cây
        colsample_bytree=0.7,       # Lấy ngẫu nhiên 70% features
        reg_lambda=2.0,             # Tăng phạt L2 Regularization
        reg_alpha=1.0,              # Thêm phạt L1 Regularization
        min_child_weight=5,
        early_stopping_rounds=30,
        eval_metric='mlogloss',
        random_state=RANDOM_STATE,
        verbosity=0
    )


# ═══════════════════════════════════════════════════════════════
# 3. HÀM ĐÁNH GIÁ BẰNG 5-FOLD CROSS VALIDATION
# ═══════════════════════════════════════════════════════════════
def evaluate_5_fold(model_name, get_model_func, X, y):
    print_section(f"ĐÁNH GIÁ: {model_name} ({N_SPLITS}-FOLD CV)")
    
    skf = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    train_accs = []
    val_accs = []

    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model = get_model_func()

        if "XGB" in model_name:
            model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        else:
            model.fit(X_train, y_train)

        t_acc = accuracy_score(y_train, model.predict(X_train)) * 100
        v_acc = accuracy_score(y_val, model.predict(X_val)) * 100

        train_accs.append(t_acc)
        val_accs.append(v_acc)
        print(f"  │ Fold {fold}: Train Acc = {t_acc:.2f}% | Val Acc = {v_acc:.2f}%")

    mean_train = np.mean(train_accs)
    mean_val = np.mean(val_accs)
    gap = mean_train - mean_val

    print(f"  ├────────────────────────────────────────────")
    print(f"  │ Trung bình Train Acc: {mean_train:.2f}%")
    print(f"  │ Trung bình Val Acc  : {mean_val:.2f}%")
    print(f"  │ Overfitting Gap     : {gap:.2f}%  {'✔' if gap <= OVERFITTING_THRESHOLD else '✘ VƯỢT NGƯỠNG'}")
    print(f"  └────────────────────────────────────────────")

    return mean_val, gap


# ═══════════════════════════════════════════════════════════════
# 4. MAIN - CHẠY LUỒNG HUẤN LUYỆN
# ═══════════════════════════════════════════════════════════════
def train_and_benchmark():
    # ── ĐỌC DỮ LIỆU ──
    print_section("1. ĐỌC DỮ LIỆU")
    if not os.path.exists(DATA_PATH):
        print(f"  ❌ Lỗi: Không tìm thấy file dữ liệu tại {DATA_PATH}")
        return
        
    df = pd.read_csv(DATA_PATH)
    X = df.drop('stress_level', axis=1)
    y = df['stress_level']

    print(f"  Tổng số mẫu: {len(df)} | Số features: {df.shape[1] - 1}")

    # ── CHẠY 5-FOLD CV CHO TỪNG MODEL ──
    rf_val_acc, rf_gap = evaluate_5_fold("RANDOM FOREST", get_random_forest, X, y)
    xgb_val_acc, xgb_gap = evaluate_5_fold("XGBOOST", get_xgboost, X, y)

    # ── CHỌN MODEL & HUẤN LUYỆN FINAL ──
    print_section("2. CHỌN MODEL TỐT NHẤT & LƯU")
    candidates = [
        ("xgboost", get_xgboost, xgb_val_acc, xgb_gap, "stress_model_xgboost.pkl"),
        ("random_forest", get_random_forest, rf_val_acc, rf_gap, "stress_model_random_forest.pkl")
    ]

    valid = [c for c in candidates if c[3] <= OVERFITTING_THRESHOLD]
    if valid:
        best = max(valid, key=lambda c: c[2])
        print(f"  ✔ Tìm thấy model trong ngưỡng. Ưu tiên Validation Acc cao nhất.")
    else:
        best = min(candidates, key=lambda c: c[3])
        print(f"  ⚠ Tất cả đều vượt ngưỡng. Chọn model có Gap overfit nhỏ nhất.")

    name, get_model_func, best_val_acc, best_gap, filename = best
    print(f"\n  ★ MODEL ĐƯỢC CHỌN: {name.upper()}")

    # ── TRAIN TRÊN 100% DỮ LIỆU ──
    print("  Đang huấn luyện lại model được chọn trên TOÀN BỘ dữ liệu...")
    final_model = get_model_func()
    
    if "xgboost" in name:
        final_model = XGBClassifier(
            n_estimators=300, max_depth=2, learning_rate=0.05,
            subsample=0.7, colsample_bytree=0.7, reg_lambda=2.0, reg_alpha=1.0,
            eval_metric='mlogloss', random_state=RANDOM_STATE, verbosity=0
        )
        
    final_model.fit(X, y)
    print_section("3. ĐỘ QUAN TRỌNG CỦA CÁC ĐẶC TRƯNG (FEATURE IMPORTANCE)")
    
    # Lấy mức độ quan trọng và gán với tên cột
    importances = final_model.feature_importances_
    features = X.columns
    
    # Tạo bảng và sắp xếp giảm dần
    fi_df = pd.DataFrame({
        'Feature': features,
        'Importance (%)': importances * 100
    }).sort_values(by='Importance (%)', ascending=False)

    print("  Mức độ đóng góp của 20 biến vào kết quả dự đoán:\n")
    for index, row in fi_df.iterrows():
        # Định dạng in cho đẹp và thẳng hàng
        print(f"  ➤ {row['Feature']:<25} : {row['Importance (%)']:.2f}%")
        
    print(f"\n  💡 GỢI Ý GIẢM OVERFIT: Cân nhắc xóa các cột có Importance < 1.0% khỏi file 'cleaned_data.csv'.")
    
    # ── LƯU FILE .PKL MÔ HÌNH ──
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_path = os.path.join(MODEL_DIR, filename)

    joblib.dump(final_model, model_path)
    print(f"💾 LƯU MODEL TẠI: {model_path}")

    # CHÈN THÊM ĐOẠN NÀY ĐỂ LƯU JSON
    meta_info = {
        "model_name": name.upper(),
        "val_accuracy": round(best_val_acc, 2),
        "gap": round(best_gap, 2),
        "features": list(X.columns) # Lưu lại bản đồ các cột dữ liệu
    }
    json_path = model_path.replace(".pkl", "_meta.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(meta_info, f, indent=4, ensure_ascii=False)
    print(f"📄 LƯU METADATA TẠI: {json_path}")
    print(f"\n  💾 ĐÃ LƯU MODEL TẠI:")
    print(f"  ➤ {model_path}")

if __name__ == "__main__":
    train_and_benchmark()