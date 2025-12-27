# ui/registration_ui.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QGridLayout, QComboBox,
    QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class RegistrationUI(QWidget):
    """UI компонент для регистрации"""
    
    # Сигналы
    register_requested = pyqtSignal(dict)  # данные пользователя
    show_auth_requested = pyqtSignal()     # переход к авторизации
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle('HR System - Регистрация')
        self.setFixedSize(500, 550)
        
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        
        title_label = QLabel('Регистрация нового пользователя')
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet('color: #333; margin-bottom: 10px;')
        main_layout.addWidget(title_label)
        
        
        personal_group = QGroupBox("Личная информация")
        personal_group.setStyleSheet('''
            QGroupBox {
                font-weight: bold;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        ''')
        personal_layout = QGridLayout()
        personal_layout.setVerticalSpacing(15)
        personal_layout.setHorizontalSpacing(10)
        
        
        fullname_label = QLabel('Полное имя:')
        fullname_label.setStyleSheet('font-weight: bold; color: #555;')
        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText('Иванов Иван Иванович')
        self.fullname_input.setMinimumHeight(35)
        personal_layout.addWidget(fullname_label, 0, 0)
        personal_layout.addWidget(self.fullname_input, 0, 1)
        
        
        email_label = QLabel('Email:')
        email_label.setStyleSheet('font-weight: bold; color: #555;')
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText('example@company.com')
        self.email_input.setMinimumHeight(35)
        personal_layout.addWidget(email_label, 1, 0)
        personal_layout.addWidget(self.email_input, 1, 1)
        
        
        phone_label = QLabel('Телефон:')
        phone_label.setStyleSheet('font-weight: bold; color: #555;')
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('+7 (999) 123-45-67')
        self.phone_input.setMinimumHeight(35)
        personal_layout.addWidget(phone_label, 2, 0)
        personal_layout.addWidget(self.phone_input, 2, 1)
        
        personal_group.setLayout(personal_layout)
        main_layout.addWidget(personal_group)
        
        
        credentials_group = QGroupBox("Учетные данные")
        credentials_group.setStyleSheet(personal_group.styleSheet())
        credentials_layout = QGridLayout()
        credentials_layout.setVerticalSpacing(15)
        credentials_layout.setHorizontalSpacing(10)
        
        
        password_label = QLabel('Пароль:')
        password_label.setStyleSheet('font-weight: bold; color: #555;')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Не менее 8 символов')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(35)
        credentials_layout.addWidget(password_label, 0, 0)
        credentials_layout.addWidget(self.password_input, 0, 1)
        
        
        confirm_password_label = QLabel('Подтверждение:')
        confirm_password_label.setStyleSheet('font-weight: bold; color: #555;')
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText('Повторите пароль')
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setMinimumHeight(35)
        credentials_layout.addWidget(confirm_password_label, 1, 0)
        credentials_layout.addWidget(self.confirm_password_input, 1, 1)
        
        
        role_label = QLabel('Роль:')
        role_label.setStyleSheet('font-weight: bold; color: #555;')
        self.role_combo = QComboBox()
        self.role_combo.addItems(['hr', 'manager', 'admin'])
        self.role_combo.setCurrentText('hr')
        self.role_combo.setMinimumHeight(35)
        self.role_combo.setStyleSheet('''
            QComboBox {
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        ''')
        credentials_layout.addWidget(role_label, 2, 0)
        credentials_layout.addWidget(self.role_combo, 2, 1)
        
        
        for input_field in [self.fullname_input, self.email_input, self.phone_input,
                          self.password_input, self.confirm_password_input]:
            input_field.setStyleSheet('''
                QLineEdit {
                    padding: 5px 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border: 1px solid #2196F3;
                }
            ''')
        
        credentials_group.setLayout(credentials_layout)
        main_layout.addWidget(credentials_group)
        
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        
        self.register_button = QPushButton('Зарегистрироваться')
        self.register_button.setMinimumHeight(45)
        self.register_button.clicked.connect(self.on_register_clicked)
        self.register_button.setStyleSheet('''
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                font-size: 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        ''')
        
        
        self.cancel_button = QPushButton('Отмена')
        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.cancel_button.setStyleSheet('''
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                font-size: 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #c62828;
            }
        ''')
        
        buttons_layout.addWidget(self.register_button)
        buttons_layout.addWidget(self.cancel_button)
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
    
    def on_register_clicked(self):
        """Обработчик клика по кнопке регистрации"""
        user_data = {
            'full_name': self.fullname_input.text().strip(),
            'email': self.email_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'password': self.password_input.text(),
            'confirm_password': self.confirm_password_input.text(),
            'role': self.role_combo.currentText()
        }
        self.register_requested.emit(user_data)
    
    def on_cancel_clicked(self):
        """Обработчик клика по кнопке отмены"""
        self.show_auth_requested.emit()
    
    def clear_fields(self):
        """Очистка всех полей"""
        self.fullname_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()
        self.role_combo.setCurrentText('hr')
    
    def set_loading(self, loading: bool):
        """Установка состояния загрузки"""
        self.register_button.setEnabled(not loading)
        self.cancel_button.setEnabled(not loading)
        self.register_button.setText('Регистрация...' if loading else 'Зарегистрироваться')