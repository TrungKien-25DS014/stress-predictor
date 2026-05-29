import joblib
import pandas as pd

def predict_stress(user_input_dict):
    """
    Hàm này nhận dữ liệu từ giao diện, đưa vào AI và trả về kết quả dự đoán.
    """
    try:
        model = joblib.load("models/stress_model.pkl")
        df = pd.DataFrame([user_input_dict])
        result = model.predict(df)[0]
        return result
        
    except Exception as e:
        print(f"Lỗi khi dự đoán: {e}")
        return None