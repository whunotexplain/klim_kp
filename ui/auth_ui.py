# ui/auth_ui.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class AuthUI(QWidget):
    """UI компонент для авторизации"""
    
    # Сигналы
    login_requested = pyqtSignal(str, str)  # email, password
    show_registration_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle('HR System - Авторизация')
        self.setFixedSize(400, 300)
        
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        
        title_label = QLabel('Вход в систему')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet('margin-bottom: 30px; color: #333;')
        main_layout.addWidget(title_label)
        
        
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(10)
        
        
        email_label = QLabel('Email:')
        email_label.setStyleSheet('font-weight: bold; color: #555;')
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('Введите ваш email')
        self.email_input.setMinimumHeight(35)
        self.email_input.setStyleSheet('''
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
        ''')
        form_layout.addWidget(email_label, 0, 0)
        form_layout.addWidget(self.email_input, 0, 1)
        
        
        password_label = QLabel('Пароль:')
        password_label.setStyleSheet('font-weight: bold; color: #555;')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Введите пароль')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        self.password_input.setStyleSheet('''
            QLineEdit {
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
        ''')
        form_layout.addWidget(password_label, 1, 0)
        form_layout.addWidget(self.password_input, 1, 1)
        
        main_layout.addLayout(form_layout)
        
        
        self.login_button = QPushButton('Войти')
        self.login_button.setMinimumHeight(40)
        self.login_button.clicked.connect(self.on_login_clicked)
        self.login_button.setStyleSheet('''
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                font-size: 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        ''')
        main_layout.addWidget(self.login_button)
        
        
        register_layout = QHBoxLayout()
        register_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        register_layout.setSpacing(5)
        
        register_label = QLabel('Нет аккаунта?')
        register_label.setStyleSheet('color: #666;')
        
        self.register_button = QPushButton('Зарегистрироваться')
        self.register_button.setStyleSheet('''
            QPushButton {
                border: none;
                color: #2196F3;
                font-weight: bold;
                background: transparent;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #1976D2;
            }
        ''')
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.clicked.connect(self.on_register_clicked)
        
        register_layout.addWidget(register_label)
        register_layout.addWidget(self.register_button)
        main_layout.addLayout(register_layout)
        
        self.setLayout(main_layout)
    
    def on_login_clicked(self):
        """Обработчик клика по кнопке входа"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        self.login_requested.emit(email, password)
    
    def on_register_clicked(self):
        """Обработчик клика по кнопке регистрации"""
        self.show_registration_requested.emit()
    
    def clear_fields(self):
        """Очистка полей ввода"""
        self.email_input.clear()
        self.password_input.clear()
    
    def set_loading(self, loading: bool):
        """Установка состояния загрузки"""
        self.login_button.setEnabled(not loading)
        self.login_button.setText('Вход...' if loading else 'Войти')