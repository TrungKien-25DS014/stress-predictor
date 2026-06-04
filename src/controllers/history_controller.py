from src.views.components.widgets import CustomMessageBox

class HistoryController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.current_user_id = None
        self.on_data_changed_callback = None
        # Kết nối sự kiện từ giao diện (khi người dùng bấm nút Xóa trên dòng)
        self._connect_signals()

    def _connect_signals(self):
        # Giả định View sẽ emit một signal kèm theo ID bản ghi khi nhấn nút xóa
        if hasattr(self.view, "delete_requested"):
            self.view.delete_requested.connect(self.handle_delete_record)

    def set_current_user(self, user_id: int):
        """Thiết lập user đang đăng nhập và tự động làm mới bảng lịch sử"""
        self.current_user_id = user_id
        self.refresh_history_view()

    def refresh_history_view(self):
        """Lấy toàn bộ dữ liệu thật từ Model, tính toán các nhóm yếu tố và yêu cầu View hiển thị"""
        if not self.current_user_id:
            return

        raw_records = self.model.get_all_user_history(self.current_user_id)
        
        # Cấu hình tính toán 5 nhóm yếu tố tương thích với DetailDialog
        factor_groups = [
            ["anxiety_level", "self_esteem", "mental_health_history", "depression"], # Tâm lý
            ["headache", "blood_pressure", "sleep_quality", "breathing_problem"],    # Thể chất
            ["noise_level", "living_conditions", "safety", "basic_needs"],           # Môi trường
            ["academic_performance", "study_load", "teacher_student_relationship", "future_career_concerns"], # Học tập
            ["social_support", "peer_pressure", "extracurricular_activities", "bullying"] # Xã hội
        ]
        
        key_max = {
            "anxiety_level": 21, "self_esteem": 30, "mental_health_history": 1, "depression": 27,
            "headache": 5, "blood_pressure": 3, "sleep_quality": 5, "breathing_problem": 5,
            "noise_level": 5, "living_conditions": 5, "safety": 5, "basic_needs": 5,
            "academic_performance": 5, "study_load": 5, "teacher_student_relationship": 5,
            "future_career_concerns": 5, "social_support": 3, "peer_pressure": 5,
            "extracurricular_activities": 5, "bullying": 5
        }

        processed_records = []
        for r in raw_records:
            # Quy đổi kết quả dự đoán (0,1,2) thành điểm phần trăm giống Dashboard (0-100)
            score = float(r['prediction_result']) * 50
            
            # Tính toán chỉ số phân bổ 5 nhóm để nạp trực tiếp vào đồ thị hình tròn của DetailDialog
            factors = []
            for group in factor_groups:
                s = sum(float(r.get(k, 0)) / (key_max.get(k, 1) or 1) for k in group)
                factors.append(max(s, 0.01))

            processed_records.append({
                "id": r["id"],
                "datetime": r["predicted_at"].strftime("%H:%M - %d/%m/%Y"),
                "anxiety_level": r["anxiety_level"],
                "sleep_hours": r["sleep_quality"], # Hiển thị mức chất lượng giấc ngủ
                "score": score,
                "factors": factors
            })
            
        # Gọi hàm hiển thị dữ liệu của class HistoryScreen (View)
        self.view.populate_table(processed_records)

    def handle_delete_record(self, prediction_id: int):
        """Xử lý logic khi nhận được yêu cầu xóa từ giao diện"""
        success, msg = self.model.delete_record(prediction_id)
        if success:
            CustomMessageBox.show_success(self.view, "Thành công", msg)
            self.refresh_history_view()
            
            # THÊM 2 DÒNG NÀY: Xóa xong thì alo cho Dashboard cập nhật luôn
            if self.on_data_changed_callback:
                self.on_data_changed_callback()
        else:
            CustomMessageBox.show_error(self.view, "Thất bại", msg)