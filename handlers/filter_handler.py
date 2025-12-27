"""
Обработчик фильтрации кандидатов.
"""

import os
from typing import List, Dict, Any
from database import db


class FilterHandler:
    """Обработчик фильтрации кандидатов"""
    
    def __init__(self, app):
        self.app = app
        self.edu_levels = {
            "Послевузовское образование": 4,
            "Высшее образование": 3,
            "Среднее профессиональное образование": 2,
            "Среднее общее образование": 1
        }
    
    def apply_filters(self) -> str:
        """Применение фильтров и возврат HTML результата"""
        if not self.app.candidates:
            return self._get_error_html("Сначала загрузите резюме!")
        
        # Получаем настройки фильтров из UI
        show_s = self.app.ui.chk_suitable.isChecked()
        show_n = self.app.ui.chk_not.isChecked()
        
        if not (show_s or show_n):
            return self._get_error_html("Выберите хотя бы одну категорию")
        
        # Параметры фильтрации
        filters = self._get_filter_params()
        
        # Применяем фильтры
        if db.conn:
            filtered_candidates = self._filter_from_database(filters)
        else:
            filtered_candidates = self._filter_in_memory(filters)
        
        return self._format_results(filtered_candidates)
    
    def _get_filter_params(self) -> Dict[str, Any]:
        """Получение параметров фильтрации из UI"""
        return {
            'show_suitable': self.app.ui.chk_suitable.isChecked(),
            'show_not_suitable': self.app.ui.chk_not.isChecked(),
            'age_from': self.app.ui.age_from.value() or 0,
            'age_to': self.app.ui.age_to.value() or 200,
            'exp_from': self.app.ui.exp_from.value() or 0,
            'exp_to': self.app.ui.exp_to.value() or 100,
            'sal_from': self.app.ui.sal_from.value() or 0,
            'sal_to': self.app.ui.sal_to.value() or 9999999,
            'education_levels': self._get_selected_education()
        }
    
    def _get_selected_education(self):
        """Получение выбранных уровней образования"""
        selected = set()
        for name, chk in self.app.ui.edu_checkboxes.items():
            if chk.isChecked():
                selected.add(self.edu_levels[name])
        return selected
    
    def _filter_from_database(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Фильтрация кандидатов из БД"""
        try:
            # Строим SQL запрос с фильтрами
            sql = "SELECT * FROM candidates WHERE 1=1"
            params = []
            
            # Фильтр по статусу
            if filters['show_suitable'] and not filters['show_not_suitable']:
                sql += " AND status = %s"
                params.append("Подходит")
            elif filters['show_not_suitable'] and not filters['show_suitable']:
                sql += " AND status = %s"
                params.append("Не подходит")
            
            # Фильтр по возрасту
            if filters['age_from'] > 0:
                sql += " AND age >= %s"
                params.append(filters['age_from'])
            if filters['age_to'] < 200:
                sql += " AND age <= %s"
                params.append(filters['age_to'])
            
            # Фильтр по опыту
            if filters['exp_from'] > 0:
                sql += " AND experience >= %s"
                params.append(filters['exp_from'])
            if filters['exp_to'] < 100:
                sql += " AND experience <= %s"
                params.append(filters['exp_to'])
            
            # Фильтр по зарплате
            if filters['sal_from'] > 0:
                sql += " AND salary >= %s"
                params.append(filters['sal_from'])
            if filters['sal_to'] < 9999999:
                sql += " AND salary <= %s"
                params.append(filters['sal_to'])
            
            # Фильтр по образованию
            if filters['education_levels']:
                placeholders = ', '.join(['%s'] * len(filters['education_levels']))
                sql += f" AND education IN ({placeholders})"
                params.extend(filters['education_levels'])
            
            sql += " ORDER BY created_at DESC"
            
            # Выполняем запрос
            results = db.fetch_all(sql, tuple(params))
            return results
            
        except Exception as e:
            print(f"Ошибка фильтрации из БД: {e}")
            return []
    
    def _filter_in_memory(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Фильтрация кандидатов в памяти"""
        filtered = []
        
        for candidate in self.app.candidates.values():
            # Фильтр по статусу
            if candidate.original_category == "Подходит" and not filters['show_suitable']:
                continue
            if candidate.original_category == "Не подходит" and not filters['show_not_suitable']:
                continue
            
            # Фильтр по возрасту
            if not (filters['age_from'] <= candidate.age <= filters['age_to']):
                continue
            
            # Фильтр по опыту
            if not (filters['exp_from'] <= candidate.experience <= filters['exp_to']):
                continue
            
            # Фильтр по зарплате
            if candidate.salary and not (filters['sal_from'] <= candidate.salary <= filters['sal_to']):
                continue
            
            # Фильтр по образованию
            if filters['education_levels'] and candidate.education not in filters['education_levels']:
                continue
            
            # Преобразуем кандидата в словарь для единообразия
            filtered.append({
                'fio': candidate.fio,
                'age': candidate.age,
                'experience': candidate.experience,
                'education': candidate.education,
                'salary': candidate.salary,
                'about': candidate.about,
                'status': candidate.original_category,
                'category_color': candidate.category_color
            })
        
        return filtered
    
    def _format_results(self, candidates: List[Dict[str, Any]]) -> str:
        """Форматирование результатов в HTML"""
        if not candidates:
            return self._get_error_html("Нет подходящих кандидатов")
        
        cards = []
        for candidate in candidates:
            color = candidate['category_color']
            about = candidate['about'] or "—"
            edu_str = self._edu_level_str(candidate['education'])
            
            cards.append(f"""
            <div style="background:#111;padding:22px;margin:15px 0;border-radius:16px;
                        border-left:8px solid {color};box-shadow:0 6px 16px rgba(231,76,60,0.4);">
                <h3 style="margin:0;color:#e74c3c;font-size:24px;">{candidate['fio']}</h3>
                <p style="margin:8px 0 0;color:{color};font-size:18px;font-weight:bold;">{candidate['status']}</p>
                <p style="margin:10px 0;color:#ddd;">
                    Возраст: <b>{candidate['age']}</b>  |  Стаж: <b>{candidate['experience']} лет</b>  |
                    Образование: <b>{edu_str}</b>  |  ЗП: <b>{candidate['salary'] or '—'}</b>
                </p>
                <p style="margin:10px 0 0;color:#aaa;font-style:italic;">О себе: {about}</p>
            </div>
            """)
        
        return "".join(cards)
    
    def _edu_level_str(self, level: int) -> str:
        """Текстовое представление уровня образования"""
        for name, value in self.edu_levels.items():
            if value == level:
                return name
        return "—"
    
    def _get_error_html(self, message: str) -> str:
        """HTML для сообщения об ошибке"""
        return f"""
        <div style='text-align:center;color:#e74c3c;font-size:22px;margin-top:100px;'>
            {message}
        </div>
        """
    
    def sort_files(self):
        """Сортировка файлов по категориям"""
        for candidate in self.app.candidates.values():
            folder = os.path.join(self.app.sorted_dir, candidate.original_category)
            os.makedirs(folder, exist_ok=True)
            
            new_path = os.path.join(folder, candidate.filename)
            if os.path.exists(candidate.source_file) and not os.path.exists(new_path):
                os.replace(candidate.source_file, new_path)
                # Обновляем путь в данных кандидата
                candidate.source_file = new_path