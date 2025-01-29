from datetime import datetime
from database.connection import get_db
from database.models import get_or_create_user
from typing import Dict, List, Tuple, Optional
from utils.achievements import ACHIEVEMENT_CATEGORIES, get_all_achievements
from utils.achievements.base import AchievementProgress

def save_achievement(telegram_nickname, achievement_type):
    """Сохраняет новое достижение пользователя"""
    with get_db() as db:
        user_id = get_or_create_user(telegram_nickname)
        
        # Проверяем, нет ли уже такого достижения
        existing = db.execute(
            '''SELECT id FROM achievements 
               WHERE user_id = ? AND achievement_type = ?''',
            (user_id, achievement_type)
        ).fetchone()
        
        if not existing:
            db.execute(
                '''INSERT INTO achievements (user_id, achievement_type)
                   VALUES (?, ?)''',
                (user_id, achievement_type)
            )
            db.commit()
            return True
        return False

def check_and_save_achievements(telegram_nickname):
    """Проверяет и сохраняет новые достижения"""
    with get_db() as db:
        user_id = get_or_create_user(telegram_nickname)
        
        # Получаем статистику пользователя
        stats = db.execute(
            '''SELECT COUNT(*) as total_games,
               SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins
               FROM matches WHERE user_id = ?''',
            (user_id,)
        ).fetchone()
        
        # Получаем статистику по героям
        hero_stats = db.execute(
            '''SELECT hero, COUNT(*) as games,
               SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins
               FROM matches 
               WHERE user_id = ?
               GROUP BY hero''',
            (user_id,)
        ).fetchall()
        
        # Получаем последние матчи для проверки серии
        recent_matches = db.execute(
            '''SELECT outcome
               FROM matches
               WHERE user_id = ?
               ORDER BY played_at DESC
               LIMIT 5''',
            (user_id,)
        ).fetchall()
        
        # Проверяем различные достижения
        if stats['wins'] > 0:
            save_achievement(telegram_nickname, "🏆 Первая победа")
        
        if stats['total_games'] >= 100:
            save_achievement(telegram_nickname, "💯 100 матчей")
        elif stats['total_games'] >= 50:
            save_achievement(telegram_nickname, "🎮 50 матчей")
        
        # Проверяем серию побед
        win_streak = 0
        for match in recent_matches:
            if match['outcome'] == 'win':
                win_streak += 1
            else:
                break
        
        if win_streak >= 5:
            save_achievement(telegram_nickname, f"🔥 Серия из {win_streak} побед")
        
        # Проверяем мастерство героев
        for hero in hero_stats:
            if hero['games'] >= 20:
                winrate = (hero['wins'] / hero['games'] * 100)
                if winrate > 60:
                    save_achievement(telegram_nickname, f"👑 Мастер {hero['hero']}")

def get_achievements(telegram_nickname):
    """Получает список достижений пользователя"""
    with get_db() as db:
        user_id = get_or_create_user(telegram_nickname)
        
        achievements = db.execute(
            '''SELECT achievement_type 
               FROM achievements 
               WHERE user_id = ?
               ORDER BY achieved_at DESC''',
            (user_id,)
        ).fetchall()
        
        return [achievement['achievement_type'] for achievement in achievements]

"""Сервис для работы с достижениями"""
class AchievementsService:
    def __init__(self):
        self.achievements = get_all_achievements()
        self.categories = ACHIEVEMENT_CATEGORIES
    
    def check_achievements(self, stats: Dict, mmr_data: Optional[Dict] = None) -> Tuple[List[str], Dict[str, AchievementProgress]]:
        """Проверяет все достижения и возвращает список полученных и их прогресс"""
        earned = []
        progress = {}
        
        for category in self.categories:
            category_earned, category_progress = category.check(stats, mmr_data)
            earned.extend(category_earned)
            progress[category.name] = category_progress
        
        # Проверяем зависимости
        final_earned = []
        for achievement_id in earned:
            achievement = self.achievements[achievement_id]
            if achievement.requires:
                if achievement.requires in earned:
                    final_earned.append(achievement_id)
            else:
                final_earned.append(achievement_id)
        
        return final_earned, progress
    
    def get_achievement_progress(self, achievement_id: str, progress: AchievementProgress) -> Optional[str]:
        """Возвращает отформатированный прогресс достижения"""
        achievement = self.achievements.get(achievement_id)
        if not achievement or not achievement.progress_max:
            return None
            
        current = progress.progress.get(achievement_id, 0)
        return achievement.format_progress(current)
    
    def get_unlocked_time(self, achievement_id: str, progress: AchievementProgress) -> Optional[str]:
        """Возвращает время получения достижения"""
        return progress.unlocked_at.get(achievement_id) 