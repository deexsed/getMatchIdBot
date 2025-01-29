from datetime import datetime
from database.connection import get_db
from database.models import get_or_create_user
from services.achievements_service import check_and_save_achievements

def save_match(telegram_nickname, match_id, hero, outcome):
    """Сохраняет матч и обновляет статистику героя"""
    with get_db() as db:
        user_id = get_or_create_user(telegram_nickname)
        
        # Получаем текущую статистику героя
        hero_stat = db.execute(
            '''SELECT games, wins FROM hero_stats 
               WHERE user_id = ? AND hero = ?''',
            (user_id, hero)
        ).fetchone()
        
        if hero_stat:
            games = hero_stat['games'] + 1
            wins = hero_stat['wins'] + (1 if outcome == 'win' else 0)
        else:
            games = 1
            wins = 1 if outcome == 'win' else 0
        
        hero_winrate = (wins / games) * 100
        
        # Сохраняем матч
        db.execute(
            '''INSERT INTO matches 
               (user_id, match_id, hero, outcome, hero_winrate, played_at) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, match_id, hero, outcome, hero_winrate, datetime.now())
        )
        
        # Обновляем статистику героя
        db.execute(
            '''INSERT OR REPLACE INTO hero_stats 
               (user_id, hero, games, wins, last_played)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)''',
            (user_id, hero, games, wins)
        )
        
        db.commit()

        # Проверяем и сохраняем достижения после каждого матча
        check_and_save_achievements(telegram_nickname)
        
        return hero_winrate 