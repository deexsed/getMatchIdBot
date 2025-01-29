"""
Модели и функции для работы с базой данных
"""
from database.connection import get_db

def get_or_create_user(telegram_nickname):
    """Получает или создает пользователя"""
    with get_db() as db:
        # Проверяем существование пользователя
        user = db.execute(
            'SELECT id FROM users WHERE telegram_nickname = ?',
            (telegram_nickname,)
        ).fetchone()
        
        if user:
            return user['id']
            
        # Создаем нового пользователя
        cursor = db.execute(
            'INSERT INTO users (telegram_nickname) VALUES (?)',
            (telegram_nickname,)
        )
        db.commit()
        return cursor.lastrowid 

def get_user_mmr(user_id):
    """Получает MMR пользователя"""
    with get_db() as db:
        result = db.execute(
            'SELECT mmr FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        return result if result else None

def update_user_mmr(user_id, mmr):
    """Обновляет MMR пользователя"""
    with get_db() as db:
        db.execute(
            'UPDATE users SET mmr = ? WHERE id = ?',
            (mmr, user_id)
        )
        db.commit() 