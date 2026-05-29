import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

def train_model():
    print("1. Đang đọc dữ liệu đã làm sạch...")
    df = pd.read_csv("data/processed/cleaned_data.csv")
    
    X = df.drop('stress_level', axis=1)
    y = df['stress_level']
    
    print("2. Đang chia tập dữ liệu Train/Test...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("3. Đang dùng GridSearchCV quét thông số tối ưu cho XGBoost (sẽ mất khoảng 1-2 phút)...")
    # Tạo mô hình gốc
    xgb = XGBClassifier(random_state=42, eval_metric='mlogloss')
    
    # Đưa ra các lựa chọn để máy tự thử nghiệm
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2]
    }
    
    # Cho máy tự quét (cv=3 nghĩa là nó sẽ kiểm tra chéo 3 lần cho chắc ăn)
    grid_search = GridSearchCV(estimator=xgb, param_grid=param_grid, cv=3, scoring='accuracy', n_jobs=-1)
    grid_search.fit(X_train, y_train)
    
    # Lấy ra bộ thông số xịn nhất mà máy tìm được
    best_model = grid_search.best_estimator_
    print(f" => Bộ thông số xịn nhất máy tìm được là: {grid_search.best_params_}")
    
    print("\n4. Test trình độ AI với bộ thông số mới...")
    predictions = best_model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    print(f" => ĐỘ CHÍNH XÁC CUỐI CÙNG (XGBoost + GridSearch): {acc * 100:.2f}%\n")
    
    os.makedirs("models", exist_ok=True)
    model_path = "models/stress_model.pkl"
    joblib.dump(best_model, model_path)
    print("Đã lưu model XGBoost Siêu Cấp thành công!")

if __name__ == "__main__":
    train_model()