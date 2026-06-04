import sys
from PyQt5.QtWidgets import QApplication
from src.controllers.app_controller import MainApplicationController

def main():
    app = QApplication(sys.argv)
    
    # Khởi tạo Controller và chạy app
    controller = MainApplicationController()
    controller.start()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()