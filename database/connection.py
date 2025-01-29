"""
Модуль для работы с подключением к базе данных
"""
import sqlite3
import logging
import os

logger = logging.getLogger(__name__)

DATABASE_PATH = 'data/dota_stats.db'

def get_db():
    """Создает подключение к базе данных"""
    try:
        db = sqlite3.connect(DATABASE_PATH)
        db.row_factory = sqlite3.Row
        return db
    except sqlite3.Error as e:
        logger.error(f"Ошибка при подключении к БД: {e}")
        raise

def init_db():
    """Инициализирует базу данных"""
    if not os.path.exists('data'):
        os.makedirs('data')
        
    with get_db() as db:
        try:
            # Создаем таблицу пользователей
            db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_nickname TEXT UNIQUE NOT NULL,
                    mmr INTEGER DEFAULT NULL,
                    last_mmr_update TIMESTAMP DEFAULT NULL
                )
            ''')
            
            # Создаем таблицу матчей
            db.execute('''
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    match_id TEXT NOT NULL,
                    hero TEXT NOT NULL,
                    outcome TEXT CHECK(outcome IN ('win', 'lose')) NOT NULL,
                    hero_winrate REAL,
                    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE (user_id, match_id)
                )
            ''')
            
            # Создаем таблицу статистики героев
            db.execute('''
                CREATE TABLE IF NOT EXISTS hero_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    hero TEXT NOT NULL,
                    games INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE (user_id, hero)
                )
            ''')
            
            # Создаем таблицу достижений
            db.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    achievement_type TEXT NOT NULL,
                    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE (user_id, achievement_type)
                )
            ''')
            
            # Создаем таблицу истории MMR
            db.execute('''
                CREATE TABLE IF NOT EXISTS mmr_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    mmr INTEGER NOT NULL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Пытаемся добавить колонки в таблицу users, если их еще нет
            try:
                db.execute('ALTER TABLE users ADD COLUMN mmr INTEGER DEFAULT NULL')
            except sqlite3.OperationalError:
                pass  # Колонка уже существует
                
            try:
                db.execute('ALTER TABLE users ADD COLUMN last_mmr_update TIMESTAMP DEFAULT NULL')
            except sqlite3.OperationalError:
                pass  # Колонка уже существует
            
            db.commit()
            logger.info("База данных успешно инициализирована")
            
        except sqlite3.Error as e:
            logger.error(f"Ошибка при инициализации БД: {e}")
            raise 