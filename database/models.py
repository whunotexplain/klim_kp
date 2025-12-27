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
        self.current_date = current_date or datetime(2025, 11, 13)
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
            return "\n".join(p.text for p in doc.paragraphs).lower()
        except:
            return "Ошибка чтения"
    
    def parse_resume(self, filepath):
        """Парсинг резюме из файла"""
        text = self.extract_text_from_word(filepath)
        if "ошибка" in text.lower():
            return None
        
        data = {
            'fio': self._extract_fio(text),
            'age': self._extract_age(text),
            'experience': self._extract_experience(text),
            'education': self._extract_education(text),
            'salary': self._extract_salary(text),
            'about': self._extract_about_section(text),
        }
        
        return Candidate(data)
    
    def _extract_fio(self, text):
        m = re.search(r'фио[:\s]*([^:\n]+)', text, re.IGNORECASE)
        if m: return m.group(1).strip().title()
        for line in text.split('\n')[:6]:
            if re.match(r'^[А-ЯЁ]{2,}\s+[А-ЯЁ]+\s+[А-ЯЁ]+', line.strip(), re.I):
                return line.strip().title()
        return "ФИО не указано"
    
    def _extract_age(self, text):
        m = re.search(r'(\d{4})\s*(год\s*рождения|д\.р\.?)', text)
        if m: return self.current_date.year - int(m.group(1))
        m = re.search(r'возраст[а]?:\s*(\d+)', text)
        if m: return int(m.group(1))
        return 0
    
    def _extract_experience(self, text):
        m = re.search(r'(стаж|опыт\s*работы)[\s:]*(\d+)', text)
        return int(m.group(2)) if m else 0
    
    def _extract_education(self, text):
        if re.search(r'ph\.?d|доктор', text): return 4
        if re.search(r'магистр|master', text): return 3
        if re.search(r'бакалавр|bachelor', text): return 2
        if re.search(r'среднее|колледж', text): return 1
        return 0
    
    def _extract_salary(self, text):
        m = re.search(r'(зарплат[аы]|salary)[\s:]*(\d+)', text)
        return int(m.group(2)) if m else 0
    
    def _extract_about_section(self, text):
        for pat in [r'о\s*себе[:\s]*([^.?!]{20,})', r'личные\s*качества[:\s]*([^.?!]{20,})']:
            m = re.search(pat, text, re.I | re.S)
            if m: return m.group(1).strip()[:300] + ("..." if len(m.group(1)) > 300 else "")
        return ""