"""
Обработчик загрузки и парсинга резюме.
"""

import os
import shutil
from typing import Dict, List, Optional

from database import db, Candidate, ResumeParser


class ResumeHandler:
    """Обработчик резюме с сохранением в БД"""
    
    def __init__(self, app):
        self.app = app
        self.parser = ResumeParser()
        
        # Расширенный список ключевых слов для классификации
        self.keywords = [
            "python", "sql", "django", "flask", "fastapi",
            "html", "css", "javascript", "java", "c++", "c#",
            "hr", "менеджер", "аналитик", "разработчик", "программист",
            "тестировщик", "дизайнер", "маркетолог", "продавец",
            "опыт работы", "образование", "университет", "курсы",
            "коммуникабельность", "ответственность", "целеустремленность"
        ]
        
        # Создаем необходимые директории
        self.resume_dir = "resumes"
        self.sorted_dir = os.path.join(self.resume_dir, "sorted")
        os.makedirs(self.resume_dir, exist_ok=True)
        os.makedirs(self.sorted_dir, exist_ok=True)
    
    def load_resume(self) -> List[str]:
        """Загрузка резюме через диалог выбора файлов"""
        from PyQt6.QtWidgets import QFileDialog
        
        files, _ = QFileDialog.getOpenFileNames(
            self.app, "Выберите резюме", "", "Word Files (*.docx)"
        )
        
        if not files:
            return []
        
        added = []
        for file in files:
            filename = os.path.basename(file)
            
            # Проверяем, не загружали ли уже этот файл
            if db.is_file_processed(file):
                print(f"Файл уже обработан: {filename}")
                continue
            
            # Копируем файл в рабочую директорию
            dest = os.path.join(self.resume_dir, filename)
            if not os.path.exists(dest):
                shutil.copy2(file, dest)
            
            # Парсим резюме
            candidate = self.parser.parse_resume(dest)
            if not candidate:
                print(f"Ошибка парсинга файла: {filename}")
                continue
            
            # Устанавливаем дополнительные поля
            candidate.filename = filename
            candidate.source_file = dest
            
            # Классифицируем
            text = self.parser.extract_text_from_word(dest)
            
            # ДЕБАГ: Выводим текст для анализа
            print(f"\n=== АНАЛИЗ ФАЙЛА: {filename} ===")
            print(f"Текст (первые 300 символов): {text[:300]}...")
            
            # Ищем ключевые слова (в нижнем регистре)
            text_lower = text.lower()
            cnt = 0
            found_keywords = []
            
            for kw in self.keywords:
                if kw.lower() in text_lower:
                    cnt += 1
                    found_keywords.append(kw)
            
            print(f"Найдено ключевых слов: {cnt}")
            print(f"Найденные слова: {found_keywords}")
            
            # Более мягкая классификация: достаточно 1 ключевого слова
            if cnt >= 1:  # ИЗМЕНЕНО: было cnt >= 2, стало cnt >= 1
                candidate.original_category = "Подходит"
                candidate.category_color = "#2ecc71"  # Зеленый для "Подходит"
                print(f"Категория: ПОДХОДИТ (найдено {cnt} ключевых слов)")
            else:
                candidate.original_category = "Не подходит"
                candidate.category_color = "#e74c3c"  # Красный для "Не подходит"
                print(f"Категория: НЕ ПОДХОДИТ (найдено {cnt} ключевых слов)")
            
            # Сохраняем в БД
            candidate_id = self._save_to_database(candidate)
            if candidate_id:
                added.append(filename)
                self.app.candidates[filename] = candidate
                db.mark_file_as_processed(file)  # Отмечаем как обработанный
                print(f"Файл успешно добавлен: {filename}")
            else:
                print(f"Ошибка сохранения в БД: {filename}")
        
        return added
    
    def _save_to_database(self, candidate: Candidate) -> Optional[int]:
        """Сохранение кандидата в базу данных"""
        try:
            # Преобразуем в словарь для БД (БЕЗ position)
            candidate_data = {
                'filename': candidate.filename,
                'fio': candidate.fio,
                'age': candidate.age,
                'experience': candidate.experience,
                'education': candidate.education,
                'salary': candidate.salary,
                'about': candidate.about,
                'status': candidate.original_category,
                'category_color': candidate.category_color,
                'source_file': candidate.source_file
            }
            
            # Сохраняем в БД
            candidate_id = db.insert('candidates', candidate_data)
            return candidate_id
            
        except Exception as e:
            print(f"Ошибка сохранения в БД: {e}")
            return None
    
    def get_all_candidates(self) -> Dict[str, Candidate]:
        """Получение всех кандидатов из БД"""
        if not db.conn:
            return self.app.candidates
        
        try:
            results = db.fetch_all("SELECT * FROM candidates ORDER BY created_at DESC")
            
            candidates = {}
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
                candidates[row['filename']] = candidate
            
            return candidates
            
        except Exception as e:
            print(f"Ошибка загрузки кандидатов из БД: {e}")
            return self.app.candidates