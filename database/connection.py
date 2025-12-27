import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
import os


class Database:
    def __init__(self):
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
            if self.conn:
                self.conn.rollback()
            return None
    
    def close(self):
        """Закрытие соединения"""
        if self.conn:
            self.conn.close()


# Создаем глобальный экземпляр БД
db = Database()