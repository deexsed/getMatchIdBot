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