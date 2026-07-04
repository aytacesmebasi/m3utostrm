import sys
import logging
import os
from PyQt6.QtWidgets import QApplication

# Ensure log directory exists
base_dir = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(base_dir, "log")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "app.log")

# Set up global logging before importing modules that use it
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    app = QApplication(sys.argv)
    
    # Imports must be done after QApplication is created due to qfluentwidgets
    from ui.main_window import MainWindow
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
