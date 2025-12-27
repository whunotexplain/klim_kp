import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import os


class Database:
    def __init__(self):
        # Инициализация атрибутов ДО попытки подключения
        self._processed_files = {}  # Для отслеживания обработанных файлов
        
        try:
            self.conn = psycopg2.connect(
                host='localhost', 
                port='5432', 
                dbname='resume_db',
                user='postgres', 
                password='12345',
                cursor_factory=RealDictCursor,
                client_encoding='UTF-8'  # Явно указываем кодировку
            )
            print("✓ Database connected successfully")
            self.create_tables()
        except Exception as e:
            print(f"✗ Database connection error: {e}")
            print("Приложение будет работать без базы данных")
            self.conn = None
    
    def is_file_processed(self, file_path):
        """Проверяет, был ли файл уже обработан"""
        # Простая реализация - всегда возвращаем False для тестирования
        return False
    
    def mark_file_as_processed(self, file_path):
        """Отмечает файл как обработанный"""
        self._processed_files[file_path] = True
    
    def create_tables(self):
        """Создание таблиц в базе данных"""
        if not self.conn:
            print("Нет подключения к базе данных")
            return
        
        try:
            with self.conn.cursor() as cur:
                # Таблица кандидатов
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS candidates (
                        id SERIAL PRIMARY KEY,
                        filename VARCHAR(255) NOT NULL UNIQUE,
                        fio VARCHAR(255) NOT NULL,
                        age INTEGER DEFAULT 0,
                        experience INTEGER DEFAULT 0,
                        education INTEGER DEFAULT 0,
                        salary INTEGER DEFAULT 0,
                        about TEXT,
                        status VARCHAR(50) DEFAULT 'На рассмотрении',
                        category_color VARCHAR(20) DEFAULT '#7f8c8d',
                        source_file VARCHAR(500),
                        position VARCHAR(100) DEFAULT '',  -- ДОБАВЛЕН СТОЛБЕЦ
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Таблица логов обработки
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS processing_logs (
                        id SERIAL PRIMARY KEY,
                        filename VARCHAR(255),
                        operation VARCHAR(50),
                        status VARCHAR(50),
                        message TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Индексы
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_candidates_fio 
                    ON candidates(fio)
                """)
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_candidates_status 
                    ON candidates(status)
                """)
                
                # Проверяем и добавляем столбец position, если его нет
                try:
                    cur.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'candidates' 
                        AND column_name = 'position'
                    """)
                    if not cur.fetchone():
                        print("Добавляем столбец 'position' в таблицу 'candidates'...")
                        cur.execute("ALTER TABLE candidates ADD COLUMN position VARCHAR(100) DEFAULT ''")
                except Exception as e:
                    print(f"Ошибка проверки столбца position: {e}")
                
                self.conn.commit()
                print("✓ Таблицы базы данных созданы")
                
        except Exception as e:
            print(f"Ошибка создания таблиц: {e}")
            if self.conn:
                self.conn.rollback()
    
    def execute(self, query, params=None):
        """Выполнение SQL запроса"""
        if not self.conn:
            print("Нет подключения к базе данных")
            return None
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                if query.strip().upper().startswith('SELECT'):
                    return cur.fetchall()
                self.conn.commit()
                return cur.rowcount
        except Exception as e:
            print(f"Ошибка запроса: {e}")
            if self.conn:
                self.conn.rollback()
            return None
    
    def fetch_all(self, query, params=None):
        """Получение всех результатов"""
        if not self.conn:
            return []
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params or ())
                return cur.fetchall()
        except Exception as e:
            print(f"Ошибка получения данных: {e}")
            return []
    
    def insert(self, table, data):
        """Вставка данных в таблицу"""
        if not self.conn:
            return None
        
        try:
            # Убираем 'position' из данных, если его нет в таблице candidates
            if table == 'candidates' and 'position' in data:
                # Проверяем, есть ли столбец position
                with self.conn.cursor() as check_cur:
                    check_cur.execute("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'candidates' 
                        AND column_name = 'position'
                    """)
                    if not check_cur.fetchone():
                        # Если столбца нет, удаляем его из данных
                        del data['position']
            
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
            
            with self.conn.cursor() as cur:
                cur.execute(query, tuple(data.values()))
                result = cur.fetchone()
                self.conn.commit()
                return result['id'] if result else None
        except Exception as e:
            print(f"Ошибка вставки данных: {e}")
            print(f"Таблица: {table}, Данные: {data}")  # Для отладки
            if self.conn:
                self.conn.rollback()
            return None
    
    def close(self):
        """Закрытие соединения"""
        if self.conn:
            self.conn.close()


# Создаем глобальный экземпляр БД
db = Database()