"""
Главный файл запуска приложения.
"""

import sys
import os
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Сначала импортируем базу данных
from database.connection import db
print("База данных:", "подключена" if db.conn else "не подключена")

# Теперь импортируем UI
try:
    from ui.main_window import MainWindowUI
    print("UI модуль загружен")
except ImportError as e:
    print(f"Ошибка загрузки UI: {e}")
    QMessageBox.critical(None, "Ошибка", f"Не удалось загрузить интерфейс: {e}")
    sys.exit(1)

# Импортируем обработчики
try:
    from handlers.resume_handler import ResumeHandler
    from handlers.filter_handler import FilterHandler
    print("Обработчики загружены")
except ImportError as e:
    print(f"Ошибка загрузки обработчиков: {e}")
    QMessageBox.critical(None, "Ошибка", f"Не удалось загрузить обработчики: {e}")
    sys.exit(1)


class ResumeSorterApp(QMainWindow):
    """Главный класс приложения"""
    
    def __init__(self):
        super().__init__()
        print("Инициализация приложения...")
        
        self.setWindowTitle("HR Resume Sorter")
        self.setGeometry(100, 100, 1350, 900)
        
        # Настройки приложения
        self.keywords_suitable = ["python", "sql", "django", "flask", "hr", "менеджер", "аналитик"]
        self.resume_dir = "resumes"
        self.sorted_dir = os.path.join(self.resume_dir, "sorted")
        
        # Создаем директории
        os.makedirs(self.resume_dir, exist_ok=True)
        os.makedirs(self.sorted_dir, exist_ok=True)
        print(f"Директории созданы: {self.resume_dir}, {self.sorted_dir}")
        
        # Данные кандидатов
        self.candidates = {}
        
        try:
            # Инициализация UI
            print("Создание интерфейса...")
            self.ui = MainWindowUI(self)
            self.setCentralWidget(self.ui)
            print("Интерфейс создан")
            
            # Инициализация обработчиков
            print("Инициализация обработчиков...")
            self.resume_handler = ResumeHandler(self)
            self.filter_handler = FilterHandler(self)
            print("Обработчики инициализированы")
            
            # Подключение сигналов
            print("Подключение сигналов...")
            self.ui.btn_load.clicked.connect(self.load_resume)
            self.ui.btn_analyze.clicked.connect(self.analyze_and_sort)
            print("Сигналы подключены")
            
            # Загружаем кандидатов из БД если есть
            self.load_candidates_from_db()
            
            print("✓ Приложение инициализировано успешно")
            
        except Exception as e:
            print(f"✗ Ошибка инициализации приложения: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка инициализации", str(e))
    
    def load_candidates_from_db(self):
        """Загрузка кандидатов из базы данных"""
        if not db.conn:
            print("БД не подключена, пропускаем загрузку кандидатов")
            return
        
        try:
            from database.models import Candidate
            
            results = db.fetch_all("SELECT * FROM candidates ORDER BY created_at DESC")
            if results:
                print(f"Загружено {len(results)} кандидатов из БД")
                for row in results:
                    candidate = Candidate({
                        'filename': row['filename'],
                        'fio': row['fio'],
                        'age': row['age'],
                        'experience': row['experience'],
                        'education': row['education'],
                        'salary': row['salary'],
                        'about': row['about'],
                        'source_file': row['source_file'],
                        'original_category': row['status'],
                        'category_color': row['category_color']
                    })
                    self.candidates[row['filename']] = candidate
                
                # Обновляем список в UI
                self.ui.update_candidate_list(self.candidates)
            else:
                print("В базе данных пока нет кандидатов")
                
        except Exception as e:
            print(f"Ошибка загрузки кандидатов из БД: {e}")
    
    def load_resume(self):
        """Загрузка резюме"""
        print("Загрузка резюме...")
        try:
            added = self.resume_handler.load_resume()
            if added:
                print(f"Добавлено {len(added)} резюме")
                self.ui.update_candidate_list(self.candidates)
            else:
                print("Резюме не добавлены")
        except Exception as e:
            print(f"Ошибка загрузки резюме: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить резюме: {e}")
    
    def analyze_and_sort(self):
        """Анализ и сортировка"""
        print("Анализ и сортировка...")
        try:
            html_result = self.filter_handler.apply_filters()
            self.ui.result_display.setHtml(html_result)
            self.filter_handler.sort_files()
            print("Анализ завершен")
        except Exception as e:
            print(f"Ошибка анализа: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка при анализе: {e}")


def main():
    """Основная функция запуска"""
    print("=" * 50)
    print("Запуск HR Resume Sorter")
    print("=" * 50)
    
    try:
        app = QApplication(sys.argv)
        app.setFont(QFont("Segoe UI", 10))
        
        print("Создание главного окна...")
        window = ResumeSorterApp()
        
        print("Показать окно...")
        window.show()
        
        print("✓ Приложение запущено успешно")
        print("=" * 50)
        
        return app.exec()
        
    except Exception as e:
        print(f"✗ Критическая ошибка запуска: {e}")
        import traceback
        traceback.print_exc()
        QMessageBox.critical(None, "Критическая ошибка", str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())