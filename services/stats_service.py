"""
Сервис для работы со статистикой
"""
import pandas as pd
from datetime import datetime, timedelta
from database.connection import get_db
from database.models import get_or_create_user
import logging

logger = logging.getLogger(__name__)

def get_best_worst_heroes(nickname, min_games=3):
    """Возвращает лучших и худших героев"""
    with get_db() as db:
        user_id = get_or_create_user(nickname)
        
        hero_stats = db.execute('''
            SELECT hero,
                   COUNT(*) as games,
                   SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins
            FROM matches
            WHERE user_id = ?
            GROUP BY hero
            HAVING COUNT(*) >= ?
        ''', (user_id, min_games)).fetchall()
        
        hero_stats = [{
            'hero': h['hero'],
            'games': h['games'],
            'winrate': (h['wins'] / h['games'] * 100)
        } for h in hero_stats]
        
        sorted_heroes = sorted(hero_stats, key=lambda x: x['winrate'], reverse=True)
        best = sorted_heroes[:3]
        worst = sorted_heroes[-3:]
        
        return best, worst

def get_period_stats(nickname, days):
    """Получает статистику за период"""
    with get_db() as db:
        user_id = get_or_create_user(nickname)
        period_start = datetime.now() - timedelta(days=days)
        
        # Получаем общую статистику
        stats = db.execute('''
            SELECT COUNT(*) as total_games,
                   SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as total_wins
            FROM matches
            WHERE user_id = ? AND played_at >= ?
        ''', (user_id, period_start)).fetchone()
        
        # Получаем статистику по героям
        heroes = db.execute('''
            SELECT hero,
                   COUNT(*) as games,
                   SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins
            FROM matches
            WHERE user_id = ? AND played_at >= ?
            GROUP BY hero
            ORDER BY games DESC
        ''', (user_id, period_start)).fetchall()
        
        return {
            'total_games': stats['total_games'],
            'total_wins': stats['total_wins'],
            'heroes': [{
                'hero': h['hero'],
                'games': h['games'],
                'wins': h['wins'],
                'winrate': (h['wins'] / h['games'] * 100) if h['games'] > 0 else 0
            } for h in heroes]
        }

def get_user_stats(telegram_nickname):
    """Получает статистику пользователя"""
    with get_db() as db:
        user_id = get_or_create_user(telegram_nickname)
        
        stats = db.execute(
            '''SELECT COUNT(*) as total_games,
               SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins
               FROM matches WHERE user_id = ?''',
            (user_id,)
        ).fetchone()
        
        heroes = db.execute(
            '''SELECT hero, games, wins
               FROM hero_stats
               WHERE user_id = ?
               ORDER BY games DESC''',
            (user_id,)
        ).fetchall()
        
        return {
            'total_games': stats['total_games'],
            'total_wins': stats['wins'],
            'heroes': [{
                'hero': h['hero'],
                'games': h['games'],
                'wins': h['wins'],
                'winrate': (h['wins'] / h['games'] * 100) if h['games'] > 0 else 0
            } for h in heroes]
        }

def get_last_matches(telegram_nickname, limit=5):
    """Получает последние матчи пользователя"""
    with get_db() as db:
        user_id = get_or_create_user(telegram_nickname)
        matches = db.execute(
            '''SELECT played_at, hero, outcome, match_id, hero_winrate
               FROM matches
               WHERE user_id = ?
               ORDER BY played_at DESC
               LIMIT ?''',
            (user_id, limit)
        ).fetchall()
        return matches

def update_user_mmr(telegram_nickname, mmr):
    """Обновляет MMR пользователя"""
    with get_db() as db:
        user_id = get_or_create_user(telegram_nickname)
        
        # Обновляем текущий MMR
        db.execute('''
            UPDATE users 
            SET mmr = ?, last_mmr_update = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (mmr, user_id))
        
        # Добавляем запись в историю
        db.execute('''
            INSERT INTO mmr_history (user_id, mmr)
            VALUES (?, ?)
        ''', (user_id, mmr))
        
        db.commit()

def get_user_mmr(nickname):
    """Получает MMR пользователя"""
    with get_db() as db:
        try:
            user_id = get_or_create_user(nickname)
            
            # Получаем MMR напрямую как число
            result = db.execute(
                'SELECT mmr FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            
            # Проверяем результат
            if result is None:
                return {'current_mmr': 0, 'history': []}
            
            # Получаем значение MMR
            try:
                current_mmr = result[0] if result[0] is not None else 0
            except (IndexError, TypeError):
                current_mmr = 0
            
            # Получаем историю MMR
            history = db.execute('''
                SELECT mmr 
                FROM mmr_history 
                WHERE user_id = ? 
                ORDER BY recorded_at DESC 
                LIMIT 90
            ''', (user_id,)).fetchall()
            
            # Преобразуем историю в список чисел
            history_values = []
            for row in history:
                try:
                    mmr = row[0] if row[0] is not None else 0
                    history_values.append(mmr)
                except (IndexError, TypeError):
                    continue
            
            return {
                'current_mmr': current_mmr,
                'history': history_values
            }
            
        except Exception as e:
            logger.error(f"Error getting MMR for user {nickname}: {e}")
            return {
                'current_mmr': 0,
                'history': []
            }

def get_mmr_history(telegram_nickname, limit=10):
    """Получает историю изменений MMR"""
    with get_db() as db:
        user_id = get_or_create_user(telegram_nickname)
        history = db.execute('''
            SELECT mmr, recorded_at
            FROM mmr_history
            WHERE user_id = ?
            ORDER BY recorded_at DESC
            LIMIT ?
        ''', (user_id, limit)).fetchall()
        return history

def ensure_user_mmr(nickname):
    """Убеждаемся, что у пользователя есть запись MMR"""
    with get_db() as db:
        try:
            user_id = get_or_create_user(nickname)
            
            # Проверяем существование записи
            result = db.execute(
                'SELECT mmr FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            
            # Если записи нет или MMR равен NULL, устанавливаем 0
            if result is None or result[0] is None:
                db.execute(
                    'UPDATE users SET mmr = 0, last_mmr_update = CURRENT_TIMESTAMP WHERE id = ?',
                    (user_id,)
                )
                db.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"Error ensuring MMR for user {nickname}: {e}")
            return False 