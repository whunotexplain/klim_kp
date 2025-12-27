import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from runner import ResumeSorterApp

def main():
    """Основная функция запуска приложения"""
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    
    window = ResumeSorterApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()