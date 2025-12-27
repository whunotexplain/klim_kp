from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt


class StyledButton(QPushButton):
    """Стилизованная кнопка"""
    
    def __init__(self, text, color="#e74c3c", parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(60)
        self.setStyleSheet(self._get_style(color))
    
    def _get_style(self, color):
        light_color = self._lighten(color, 40)
        return f"""
            QPushButton {{
                background: {color};
                color: white;
                font-weight: bold;
                font-size: 18px;
                padding: 16px 40px;
                border-radius: 12px;
                border: 3px solid white;
            }}
            QPushButton:hover {{
                background: {light_color};
            }}
        """
    
    def _lighten(self, c, a=40):
        c = c.lstrip('#')
        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        return f"#{min(255, r+a):02x}{min(255, g+a):02x}{min(255, b+a):02x}"


class FilterSpinBox(QSpinBox):
    """Стилизованный SpinBox для фильтров"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QSpinBox {
                background:#222;
                color:white;
                border:2px solid #e74c3c;
                border-radius:8px;
                padding:8px;
                min-width:120px;
                font-size:14px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width:20px;
            }
        """)
        self.setSpecialValueText(" ")