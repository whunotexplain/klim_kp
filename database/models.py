from datetime import datetime
import re
from docx import Document


class Candidate:
    """Модель кандидата"""
    def __init__(self, data=None):
        data = data or {}
        self.filename = data.get('filename', '')
        self.fio = data.get('fio', 'ФИО не указано')
        self.age = data.get('age', 0)
        self.experience = data.get('experience', 0)
        self.education = data.get('education', 0)
        self.salary = data.get('salary', 0)
        self.about = data.get('about', '')
        self.source_file = data.get('source_file', '')
        self.original_category = data.get('original_category', 'Не подходит')
        self.category_color = data.get('category_color', '#888')


class ResumeParser:
    """Парсер резюме"""
    
    def __init__(self, current_date=None):
        self.current_date = current_date or datetime.now()
        self.edu_levels = {
            "Послевузовское образование": 4,
            "Высшее образование": 3,
            "Среднее профессиональное образование": 2,
            "Среднее общее образование": 1
        }
    
    def extract_text_from_word(self, path):
        """Извлечение текста из DOCX"""
        try:
            doc = Document(path)
            text = "\n".join(p.text for p in doc.paragraphs)
            return text.lower()  # Возвращаем в нижнем регистре
        except Exception as e:
            print(f"Ошибка чтения файла {path}: {e}")
            return ""
    
    def parse_resume(self, filepath):
        """Парсинг резюме из файла"""
        text = self.extract_text_from_word(filepath)
        if not text:
            print(f"Пустой текст файла: {filepath}")
            return None
        
        data = {
            'fio': self._extract_fio(text),
            'age': self._extract_age(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text),
            'salary': self._extract_salary(text),
            'about': self._extract_about_section(text),
        }
        
        # Отладочная информация
        print(f"\n=== ПАРСИНГ РЕЗЮМЕ: {filepath} ===")
        print(f"  ФИО: {data['fio']}")
        print(f"  Возраст: {data['age']}")
        print(f"  Опыт: {data['experience']}")
        print(f"  Образование (уровень): {data['education']}")
        print(f"  ЗП: {data['salary']}")
        print(f"  О себе: {data['about'][:100]}...")
        
        return Candidate(data)
    
    def _extract_fio(self, text):
        m = re.search(r'фио[:\s]*([^:\n]+)', text, re.IGNORECASE)
        if m: 
            fio = m.group(1).strip().title()
            print(f"    Найден ФИО через шаблон 'фио': {fio}")
            return fio
        
        # Ищем ФИО в первых строках
        for line in text.split('\n')[:6]:
            line = line.strip()
            if re.match(r'^[А-ЯЁ]{2,}\s+[А-ЯЁ]+\s+[А-ЯЁ]+', line, re.I):
                fio = line.title()
                print(f"    Найден ФИО в строке: {fio}")
                return fio
        
        print("    ФИО не найден, используем 'ФИО не указано'")
        return "ФИО не указано"
    
    def _extract_age(self, text):
        m = re.search(r'(\d{4})\s*(год\s*рождения|д\.р\.?)', text)
        if m: 
            age = self.current_date.year - int(m.group(1))
            print(f"    Найден год рождения: {m.group(1)}, возраст: {age}")
            return age
        
        m = re.search(r'возраст[а]?:\s*(\d+)', text)
        if m: 
            age = int(m.group(1))
            print(f"    Найден возраст: {age}")
            return age
        
        print("    Возраст не найден, используем 0")
        return 0
    
    def _extract_experience(self, text):
        m = re.search(r'(стаж|опыт\s*работы)[\s:]*(\d+)', text)
        if m: 
            exp = int(m.group(2))
            print(f"    Найден опыт работы: {exp} лет")
            return exp
        
        print("    Опыт работы не найден, используем 0")
        return 0
    
    def _extract_education(self, text):
        if re.search(r'ph\.?d|доктор', text): 
            print("    Образование: PhD/Доктор (уровень 4)")
            return 4
        if re.search(r'магистр|master', text): 
            print("    Образование: Магистр (уровень 3)")
            return 3
        if re.search(r'бакалавр|bachelor', text): 
            print("    Образование: Бакалавр (уровень 2)")
            return 2
        if re.search(r'среднее|колледж', text): 
            print("    Образование: Среднее (уровень 1)")
            return 1
        
        print("    Образование не распознано, используем 0")
        return 0
    
    def _extract_salary(self, text):
        m = re.search(r'(зарплат[аы]|salary)[\s:]*(\d+)', text)
        if m: 
            salary = int(m.group(2))
            print(f"    Найдена зарплата: {salary}")
            return salary
        
        print("    Зарплата не найдена, используем 0")
        return 0
    
    def _extract_about_section(self, text):
        for pat in [r'о\s*себе[:\s]*([^.?!]{20,})', r'личные\s*качества[:\s]*([^.?!]{20,})']:
            m = re.search(pat, text, re.I | re.S)
            if m: 
                about = m.group(1).strip()[:300] + ("..." if len(m.group(1)) > 300 else "")
                print(f"    Найдено 'о себе': {about[:100]}...")
                return about
        
        print("    Раздел 'о себе' не найден")
        return ""