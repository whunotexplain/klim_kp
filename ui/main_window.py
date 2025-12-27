from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from .widgets import StyledButton, FilterSpinBox


class MainWindowUI(QWidget):
    """Пользовательский интерфейс главного окна"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок
        title = QLabel("АВТОМАТИЗАЦИЯ ПРИЁМА РЕЗЮМЕ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            font-size: 32px; font-weight: bold; color: white; padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c0392b, stop:1 #e74c3c);
            border-radius: 16px; border: 3px solid #e74c3c;
        """)
        main_layout.addWidget(title)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_load = StyledButton("ЗАГРУЗИТЬ РЕЗЮМЕ (.docx)", "#e74c3c")
        self.btn_analyze = StyledButton("АНАЛИЗ И СОРТИРОВКА", "#c0392b")
        
        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_analyze)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # Средняя часть
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(40)

        # ФИЛЬТРЫ
        filter_box = self.create_filter_box()
        mid_layout.addWidget(filter_box)

        # КАНДИДАТЫ
        cand_box = self.create_candidate_box()
        mid_layout.addWidget(cand_box)

        mid_layout.addStretch()
        main_layout.addLayout(mid_layout)

        # РЕЗУЛЬТАТЫ АНАЛИЗА
        res_box = self.create_result_box()
        main_layout.addWidget(res_box, stretch=1)

        # Глобальные стили
        self.setStyleSheet("""
            QWidget { background: black; color: white; }
            QCheckBox { color: white; font-size: 15px; }
            QCheckBox::indicator { width: 18px; height: 18px; border: 2px solid #e74c3c; border-radius: 4px; }
            QCheckBox::indicator:checked { background: #e74c3c; }
            QLabel { color: #ddd; }
        """)
    
    def create_filter_box(self):
        """Создание панели фильтров"""
        filter_box = QGroupBox("ФИЛЬТРЫ")
        filter_box.setFixedSize(620, 440)
        filter_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 18px;
                color: #e74c3c;
                border: 3px solid #e74c3c;
                border-radius: 16px;
                background: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                color: white;
            }
        """)

        grid = QGridLayout()
        grid.setContentsMargins(30, 30, 30, 30)
        grid.setVerticalSpacing(18)
        grid.setHorizontalSpacing(20)

        # Категории
        self.chk_suitable = QCheckBox("Подходит")
        self.chk_not = QCheckBox("Не подходит")
        grid.addWidget(self.chk_suitable, 0, 0)
        grid.addWidget(self.chk_not, 0, 1)

        # Метки
        grid.addWidget(QLabel("Возраст от:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        grid.addWidget(QLabel("до:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        grid.addWidget(QLabel("Стаж от:"), 3, 0, Qt.AlignmentFlag.AlignRight)
        grid.addWidget(QLabel("до:"), 4, 0, Qt.AlignmentFlag.AlignRight)
        grid.addWidget(QLabel("ЗП от:"), 5, 0, Qt.AlignmentFlag.AlignRight)
        grid.addWidget(QLabel("до:"), 6, 0, Qt.AlignmentFlag.AlignRight)

        # SpinBox'ы
        self.age_from = FilterSpinBox(); self.age_from.setRange(0, 100); self.age_from.setValue(0)
        self.age_to = FilterSpinBox(); self.age_to.setRange(0, 100); self.age_to.setValue(0)
        self.exp_from = FilterSpinBox(); self.exp_from.setRange(0, 50); self.exp_from.setValue(0)
        self.exp_to = FilterSpinBox(); self.exp_to.setRange(0, 50); self.exp_to.setValue(0)
        self.sal_from = FilterSpinBox(); self.sal_from.setRange(0, 999999); self.sal_from.setValue(0)
        self.sal_to = FilterSpinBox(); self.sal_to.setRange(0, 999999); self.sal_to.setValue(0)

        grid.addWidget(self.age_from, 1, 1)
        grid.addWidget(self.age_to, 2, 1)
        grid.addWidget(self.exp_from, 3, 1)
        grid.addWidget(self.exp_to, 4, 1)
        grid.addWidget(self.sal_from, 5, 1)
        grid.addWidget(self.sal_to, 6, 1)

        # Образование
        edu_title = QLabel("Образование")
        edu_title.setStyleSheet("color:#e74c3c; font-weight:bold; font-size:16px; margin-top:10px;")
        grid.addWidget(edu_title, 0, 3, 1, 2, Qt.AlignmentFlag.AlignCenter)

        self.edu_checkboxes = {}
        row = 1
        edu_levels = self.parent_app.parser.edu_levels if hasattr(self.parent_app, 'parser') else {
            "Послевузовское образование": 4,
            "Высшее образование": 3,
            "Среднее профессиональное образование": 2,
            "Среднее общее образование": 1
        }
        
        for name in edu_levels:
            chk = QCheckBox(name)
            chk.setStyleSheet("color:white; font-size:14px;")
            grid.addWidget(chk, row, 3, 1, 2)
            self.edu_checkboxes[name] = chk
            row += 1

        filter_box.setLayout(grid)
        return filter_box
    
    def create_candidate_box(self):
        """Создание панели кандидатов"""
        cand_box = QGroupBox("КАНДИДАТЫ")
        cand_box.setFixedSize(380, 440)
        cand_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 18px;
                color: #e74c3c;
                border: 3px solid #e74c3c;
                border-radius: 16px;
                background: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                color: white;
            }
        """)
        
        c_layout = QVBoxLayout()
        c_layout.setContentsMargins(20, 35, 20, 20)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            background:#111;
            color:white;
            border-radius:12px;
            font-size:15px;
            QListWidget::item {
                padding:12px;
                background:#222;
                margin:3px;
                border-radius:8px;
            }
            QListWidget::item:selected {
                background:#e74c3c;
                color:white;
            }
        """)
        c_layout.addWidget(self.file_list)
        cand_box.setLayout(c_layout)
        
        return cand_box
    
    def create_result_box(self):
        """Создание панели результатов"""
        res_box = QGroupBox("РЕЗУЛЬТАТЫ АНАЛИЗА")
        res_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 18px;
                color: #e74c3c;
                border: 3px solid #e74c3c;
                border-radius: 16px;
                background: #1a1a1a;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px;
                color: white;
            }
        """)
        
        res_layout = QVBoxLayout()
        res_layout.setContentsMargins(20, 20, 20, 20)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setStyleSheet("""
            background:#111;
            color:white;
            border-radius:14px;
            padding:20px;
            font-size:16px;
        """)
        self.result_display.setHtml("""
            <div style='text-align:center;color:#bbb;font-size:20px;margin-top:100px;'>
                Загрузите резюме и примените фильтры
            </div>
        """)
        res_layout.addWidget(self.result_display)
        res_box.setLayout(res_layout)
        
        return res_box
    
    def update_candidate_list(self, candidates):
        """Обновление списка кандидатов"""
        self.file_list.clear()
        for candidate in candidates.values():
            self.file_list.addItem(candidate.fio)