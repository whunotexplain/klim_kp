import sys
import os
import re
from datetime import datetime
# from docx import Document
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class ResumeSorterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HR Resume Sorter")
        self.setGeometry(100, 100, 1350, 900)

        self.keywords_suitable = ["python", "sql", "django", "flask", "hr", "менеджер", "аналитик"]
        self.resume_dir = "resumes"
        self.sorted_dir = os.path.join(self.resume_dir, "sorted")
        os.makedirs(self.resume_dir, exist_ok=True)
        os.makedirs(self.sorted_dir, exist_ok=True)

        self.current_date = datetime(2025, 11, 13)
        self.candidates = {}
        self.edu_levels = {
            "Послевузовское образование": 4,
            "Высшее образование": 3,
            "Среднее профессиональное образование": 2,
            "Среднее общее образование": 1
        }

        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
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
        self.btn_load = QPushButton("ЗАГРУЗИТЬ РЕЗЮМЕ (.docx)")
        self.btn_load.setFixedHeight(60)
        self.btn_load.setStyleSheet(self.btn_style("#e74c3c"))
        self.btn_load.clicked.connect(self.load_resume)

        self.btn_analyze = QPushButton("АНАЛИЗ И СОРТИРОВКА")
        self.btn_analyze.setFixedHeight(60)
        self.btn_analyze.setStyleSheet(self.btn_style("#c0392b"))
        self.btn_analyze.clicked.connect(self.analyze_and_sort)

        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_analyze)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # Средняя часть
        mid_layout = QHBoxLayout()
        mid_layout.setSpacing(40)

        #ФИЛЬТРЫ
        filter_box = QGroupBox("ФИЛЬТРЫ")
        filter_box.setFixedSize(620, 440)
        filter_box.setStyleSheet("""
            QGroupBox { font-weight: bold; font-size: 18px; color: #e74c3c;
                        border: 3px solid #e74c3c; border-radius: 16px; background: #1a1a1a; }
            QGroupBox::title { subcontrol-origin: margin; left: 20px; padding: 0 10px; color: white; }
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
        spin_style = """
            QSpinBox { background:#222; color:white; border:2px solid #e74c3c; border-radius:8px; 
                        padding:8px; min-width:120px; font-size:14px; }
            QSpinBox::up-button, QSpinBox::down-button { width:20px; }
        """

        self.age_from = QSpinBox(); self.age_from.setRange(0,100); self.age_from.setValue(0); self.age_from.setSpecialValueText(" ")
        self.age_to   = QSpinBox(); self.age_to.setRange(0,100);   self.age_to.setValue(0);   self.age_to.setSpecialValueText(" ")
        self.exp_from = QSpinBox(); self.exp_from.setRange(0,50);  self.exp_from.setValue(0); self.exp_from.setSpecialValueText(" ")
        self.exp_to   = QSpinBox(); self.exp_to.setRange(0,50);    self.exp_to.setValue(0);   self.exp_to.setSpecialValueText(" ")
        self.sal_from = QSpinBox(); self.sal_from.setRange(0,999999); self.sal_from.setValue(0); self.sal_from.setSpecialValueText(" ")
        self.sal_to   = QSpinBox(); self.sal_to.setRange(0,999999);   self.sal_to.setValue(0);   self.sal_to.setSpecialValueText(" ")

        for w in [self.age_from, self.age_to, self.exp_from, self.exp_to, self.sal_from, self.sal_to]:
            w.setStyleSheet(spin_style)

        grid.addWidget(self.age_from, 1, 1)
        grid.addWidget(self.age_to,   2, 1)
        grid.addWidget(self.exp_from, 3, 1)
        grid.addWidget(self.exp_to,   4, 1)
        grid.addWidget(self.sal_from, 5, 1)
        grid.addWidget(self.sal_to,   6, 1)

        # Образование
        edu_title = QLabel("Образование")
        edu_title.setStyleSheet("color:#e74c3c; font-weight:bold; font-size:16px; margin-top:10px;")
        grid.addWidget(edu_title, 0, 3, 1, 2, Qt.AlignCenter)

        self.edu_checkboxes = {}
        row = 1
        for name in self.edu_levels:
            chk = QCheckBox(name)
            chk.setStyleSheet("color:white; font-size:14px;")
            grid.addWidget(chk, row, 3, 1, 2)
            self.edu_checkboxes[name] = chk
            row += 1

        filter_box.setLayout(grid)
        mid_layout.addWidget(filter_box)

        # КАНДИДАТЫ
        cand_box = QGroupBox("КАНДИДАТЫ")
        cand_box.setFixedSize(380, 440)
        cand_box.setStyleSheet("""
            QGroupBox { font-weight: bold; font-size: 18px; color: #e74c3c;
                        border: 3px solid #e74c3c; border-radius: 16px; background: #1a1a1a; }
            QGroupBox::title { subcontrol-origin: margin; left: 20px; padding: 0 10px; color: white; }
        """)
        c_layout = QVBoxLayout()
        c_layout.setContentsMargins(20, 35, 20, 20)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            background:#111; color:white; border-radius:12px; font-size:15px;
            QListWidget::item { padding:12px; background:#222; margin:3px; border-radius:8px; }
            QListWidget::item:selected { background:#e74c3c; color:white; }
        """)
        c_layout.addWidget(self.file_list)
        cand_box.setLayout(c_layout)
        mid_layout.addWidget(cand_box)

        mid_layout.addStretch()
        main_layout.addLayout(mid_layout)

        res_box = QGroupBox("РЕЗУЛЬТАТЫ АНАЛИЗА")
        res_box.setStyleSheet("""
            QGroupBox { font-weight: bold; font-size: 18px; color: #e74c3c;
                        border: 3px solid #e74c3c; border-radius: 16px; background: #1a1a1a; }
            QGroupBox::title { subcontrol-origin: margin; left: 20px; padding: 0 10px; color: white; }
        """)
        res_layout = QVBoxLayout()
        res_layout.setContentsMargins(20, 20, 20, 20)

        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        self.result_display.setStyleSheet("background:#111; color:white; border-radius:14px; padding:20px; font-size:16px;")
        self.result_display.setHtml("<div style='text-align:center;color:#bbb;font-size:20px;margin-top:100px;'>Загрузите резюме и примените фильтры</div>")
        res_layout.addWidget(self.result_display)
        res_box.setLayout(res_layout)
        main_layout.addWidget(res_box, stretch=1)

        # Глобальные стили
        self.setStyleSheet("""
            QWidget { background: black; color: white; }
            QCheckBox { color: white; font-size: 15px; }
            QCheckBox::indicator { width: 18px; height: 18px; border: 2px solid #e74c3c; border-radius: 4px; }
            QCheckBox::indicator:checked { background: #e74c3c; }
            QLabel { color: #ddd; }
        """)

    def btn_style(self, color):
        return f"""
            QPushButton {{ background: {color}; color: white; font-weight: bold; font-size: 18px;
                          padding: 16px 40px; border-radius: 12px; border: 3px solid white; }}
            QPushButton:hover {{ background: {self.lighten(color, 40)}; }}
        """

    def lighten(self, c, a=40):
        c = c.lstrip('#')
        r, g, b = int(c[0:2],16), int(c[2:4],16), int(c[4:6],16)
        return f"#{min(255,r+a):02x}{min(255,g+a):02x}{min(255,b+a):02x}"

    # === ВСЕ МЕТОДЫ РАБОТАЮТ ===
    def load_resume(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите резюме", "", "Word Files (*.docx)")
        if not files: return
        added = []
        for file in files:
            fn = os.path.basename(file)
            if fn in self.candidates: continue
            dest = os.path.join(self.resume_dir, fn)
            if not os.path.exists(dest):
                with open(file, 'rb') as s, open(dest, 'wb') as d: d.write(s.read())
            text = self.extract_text_from_word(dest)
            if "ошибка" not in text.lower():
                data = self.extract_candidate_data(text)
                data['source_file'] = dest
                data['original_category'] = self.classify_resume(text)[0]
                self.candidates[fn] = data
                added.append(fn)
        if added:
            self.update_candidate_list(self.candidates)

    def extract_text_from_word(self, path):
        try:
            doc = Document(path)
            return "\n".join(p.text for p in doc.paragraphs).lower()
        except:
            return "Ошибка чтения"

    def extract_candidate_data(self, text):
        return {
            'fio': self.extract_fio(text),
            'age': self.extract_age(text),
            'experience': self.extract_experience(text),
            'education': self.extract_education(text),
            'salary': self.extract_salary(text),
            'about': self.extract_about_section(text),
        }

    def extract_fio(self, text):
        m = re.search(r'фио[:\s]*([^:\n]+)', text, re.IGNORECASE)
        if m: return m.group(1).strip().title()
        for line in text.split('\n')[:6]:
            if re.match(r'^[А-ЯЁ]{2,}\s+[А-ЯЁ]+\s+[А-ЯЁ]+', line.strip(), re.I):
                return line.strip().title()
        return "ФИО не указано"

    def extract_age(self, text):
        m = re.search(r'(\d{4})\s*(год\s*рождения|д\.р\.?)', text)
        if m: return self.current_date.year - int(m.group(1))
        m = re.search(r'возраст[а]?:\s*(\d+)', text)
        if m: return int(m.group(1))
        return 0

    def extract_experience(self, text):
        m = re.search(r'(стаж|опыт\s*работы)[\s:]*(\d+)', text)
        return int(m.group(2)) if m else 0

    def extract_education(self, text):
        if re.search(r'ph\.?d|доктор', text): return 4
        if re.search(r'магистр|master', text): return 3
        if re.search(r'бакалавр|bachelor', text): return 2
        if re.search(r'среднее|колледж', text): return 1
        return 0

    def extract_salary(self, text):
        m = re.search(r'(зарплат[аы]|salary)[\s:]*(\d+)', text)
        return int(m.group(2)) if m else 0

    def extract_about_section(self, text):
        for pat in [r'о\s*себе[:\s]*([^.?!]{20,})', r'личные\s*качества[:\s]*([^.?!]{20,})']:
            m = re.search(pat, text, re.I | re.S)
            if m: return m.group(1).strip()[:300] + ("..." if len(m.group(1)) > 300 else "")
        return ""

    def classify_resume(self, text):
        cnt = sum(1 for kw in self.keywords_suitable if kw in text)
        return ("Подходит", "#e74c3c") if cnt >= 2 else ("Не подходит", "#888")

    def analyze_and_sort(self):
        if not self.candidates:
            self.result_display.setHtml("<div style='text-align:center;color:#e74c3c;font-size:22px;margin-top:100px;'>Сначала загрузите резюме!</div>")
            return
        if not (self.chk_suitable.isChecked() and not self.chk_not.isChecked()):
            self.result_display.setHtml("<div style='text-align:center;color:#e74c3c;font-size:22px;margin-top:100px;'>Выберите хотя бы одну категорию</div>")
            return

        show_s = self.chk_suitable.isChecked()
        show_n = self.chk_not.isChecked()

        af = self.age_from.value() or 0
        at = self.age_to.value() or 200
        ef = self.exp_from.value() or 0
        et = self.exp_to.value() or 100
        sf = self.sal_from.value() or 0
        st = self.sal_to.value() or 9999999
        edu = {v for k, v in self.edu_levels.items() if self.edu_checkboxes[k].isChecked()}

        cards = []
        for fn, d in self.candidates.items():
            if d['original_category'] == "Подходит" and not show_s: continue
            if d['original_category'] == "Не подходит" and not show_n: continue
            if not (af <= d['age'] <= at): continue
            if not (ef <= d['experience'] <= et): continue
            if d['salary'] and not (sf <= d['salary'] <= st): continue
            if edu and d['education'] not in edu: continue

            color = "#e74c3c" if d['original_category'] == "Подходит" else "#888"
            about = d['about'] or "—"
            cards.append(f"""
            <div style="background:#111;padding:22px;margin:15px 0;border-radius:16px;
                        border-left:8px solid {color};box-shadow:0 6px 16px rgba(231,76,60,0.4);">
                <h3 style="margin:0;color:#e74c3c;font-size:24px;">{d['fio']}</h3>
                <p style="margin:8px 0 0;color:{color};font-size:18px;font-weight:bold;">{d['original_category']}</p>
                <p style="margin:10px 0;color:#ddd;">
                    Возраст: <b>{d['age']}</b>  |  Стаж: <b>{d['experience']} лет</b>  |
                    Образование: <b>{self.edu_level_str(d['education'])}</b>  |  ЗП: <b>{d['salary'] or '—'}</b>
                </p>
                <p style="margin:10px 0 0;color:#aaa;font-style:italic;">О себе: {about}</p>
            </div>
            """)

        self.result_display.setHtml("".join(cards) if cards else
            "<div style='text-align:center;color:#e74c3c;font-size:22px;margin-top:100px;'>Нет подходящих кандидатов</div>")

        # Сортировка файлов
        for fn, d in self.candidates.items():
            folder = os.path.join(self.sorted_dir, d['original_category'])
            os.makedirs(folder, exist_ok=True)
            new_path = os.path.join(folder, fn)
            if not os.path.exists(new_path):
                os.replace(d['source_file'], new_path)

    def edu_level_str(self, level):
        return {v: k for k, v in self.edu_levels.items()}.get(level, "—")

    def update_candidate_list(self, cands):
        self.file_list.clear()
        for _, data in cands.items():
            self.file_list.addItem(data['fio'])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    win = ResumeSorterApp()
    win.show()
    sys.exit(app.exec_())