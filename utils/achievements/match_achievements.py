"""Достижения за количество матчей"""
from datetime import datetime
from .base import Achievement, AchievementCategory, AchievementProgress

MATCH_ACHIEVEMENTS = [
    # Начальные достижения
    Achievement(
        id='first_match',
        name='Первые шаги',
        description='Записать первый матч',
        emoji='👶',
        category='Матчи',
        progress_max=1
    ),
    Achievement(
        id='ten_matches',
        name='Начинающий',
        description='Сыграть 10 матчей',
        emoji='🎮',
        category='Матчи',
        progress_max=10,
        requires='first_match'
    ),
    Achievement(
        id='fifty_matches',
        name='Любитель',
        description='Сыграть 50 матчей',
        emoji='🎲',
        category='Матчи',
        progress_max=50,
        requires='ten_matches'
    ),
    Achievement(
        id='hundred_matches',
        name='Ветеран',
        description='Сыграть 100 матчей',
        emoji='🏆',
        category='Матчи'
    ),
    
    # Продвинутые достижения
    Achievement(
        id='five_hundred_matches',
        name='Опытный боец',
        description='Сыграть 500 матчей',
        emoji='🎯',
        category='Матчи'
    ),
    Achievement(
        id='thousand_matches',
        name='Мастер',
        description='Сыграть 1000 матчей',
        emoji='💫',
        category='Матчи'
    ),
    Achievement(
        id='two_thousand_matches',
        name='Элита',
        description='Сыграть 2000 матчей',
        emoji='🌟',
        category='Матчи'
    ),
    
    # Экспертные достижения
    Achievement(
        id='five_thousand_matches',
        name='Легенда',
        description='Сыграть 5000 матчей',
        emoji='👑',
        category='Матчи'
    ),
    Achievement(
        id='ten_thousand_matches',
        name='Бессмертный',
        description='Сыграть 10000 матчей',
        emoji='⚡',
        category='Матчи'
    ),
    Achievement(
        id='fifteen_thousand_matches',
        name='Ноулайфер',
        description='Сыграть 15000 матчей',
        emoji='🔱',
        category='Матчи'
    ),
    
    # Достижения за серии
    Achievement(
        id='daily_player',
        name='Ежедневный игрок',
        description='Сыграть 3 игры за день',
        emoji='📅',
        category='Матчи',
        progress_max=3
    ),
    Achievement(
        id='weekend_warrior',
        name='Воин выходного дня',
        description='Сыграть 10 игр за выходные',
        emoji='🎪',
        category='Матчи',
        progress_max=10,
        requires='daily_player'
    ),
    Achievement(
        id='marathon_runner',
        name='Марафонец',
        description='Сыграть 20 игр за день',
        emoji='🏃',
        category='Матчи',
        progress_max=20,
        requires='weekend_warrior',
        hidden=True  # Скрытое достижение
    ),
    
    # Достижения за постоянство
    Achievement(
        id='weekly_dedication',
        name='Недельная преданность',
        description='Играть каждый день недели',
        emoji='📊',
        category='Матчи'
    ),
    Achievement(
        id='monthly_master',
        name='Мастер месяца',
        description='Сыграть 100 игр за месяц',
        emoji='📈',
        category='Матчи'
    ),
    Achievement(
        id='seasonal_veteran',
        name='Ветеран сезона',
        description='Сыграть 300 игр за сезон',
        emoji='🌟',
        category='Матчи'
    ),
    
    # Особые достижения за матчи
    Achievement(
        id='morning_person',
        name='Ранняя пташка',
        description='Сыграть 10 игр до 9 утра',
        emoji='🌅',
        category='Матчи'
    ),
    Achievement(
        id='night_owl',
        name='Ночная сова',
        description='Сыграть 10 игр после 23:00',
        emoji='🌙',
        category='Матчи'
    ),
    Achievement(
        id='prime_time_player',
        name='Прайм-тайм игрок',
        description='Сыграть 50 игр в прайм-тайм (19:00-23:00)',
        emoji='⭐',
        category='Матчи'
    )
]

class MatchAchievements(AchievementCategory):
    def __init__(self):
        super().__init__('Матчи', MATCH_ACHIEVEMENTS)
    
    def check(self, stats, mmr_data=None):
        earned = []
        progress = AchievementProgress()
        
        if not stats:
            return earned, progress  # Всегда возвращаем tuple
        
        total_games = stats.get('total_games', 0)
        
        # Проверяем достижения за количество игр
        thresholds = [
            (1, 'first_match'),
            (10, 'ten_matches'),
            (50, 'fifty_matches'),
            (100, 'hundred_matches'),
            (500, 'five_hundred_matches'),
            (1000, 'thousand_matches'),
            (2000, 'two_thousand_matches'),
            (5000, 'five_thousand_matches'),
            (10000, 'ten_thousand_matches'),
            (15000, 'fifteen_thousand_matches')
        ]
        
        # Обновляем прогресс для всех достижений
        for threshold, achievement_id in thresholds:
            current = min(total_games, threshold)
            progress.update(achievement_id, current)
            if total_games >= threshold:
                earned.append(achievement_id)
                progress.unlock(achievement_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Проверяем достижения за игры в определенное время
        morning_games = 0
        night_games = 0
        prime_time_games = 0
        daily_games = {}
        
        for match in stats.get('matches', []):
            if not match.get('played_at'):
                continue
                
            try:
                match_time = datetime.strptime(match['played_at'], '%Y-%m-%d %H:%M:%S')
                hour = match_time.hour
                date = match_time.date()
                
                # Считаем игры в разное время суток
                if 5 <= hour < 9:
                    morning_games += 1
                elif 23 <= hour or hour < 5:
                    night_games += 1
                elif 19 <= hour < 23:
                    prime_time_games += 1
                
                # Считаем игры за день
                daily_games[date] = daily_games.get(date, 0) + 1
                
                # Обновляем прогресс ежедневных достижений
                progress.update('daily_player', daily_games[date])
                
                if daily_games[date] >= 3:
                    earned.append('daily_player')
                    progress.unlock('daily_player', match['played_at'])
                
                if daily_games[date] >= 20:
                    earned.append('marathon_runner')
                    progress.unlock('marathon_runner', match['played_at'])
                
                # Проверяем выходные
                if date.weekday() >= 5:  # Суббота и воскресенье
                    weekend_games = sum(1 for d, count in daily_games.items() 
                                     if d.weekday() >= 5)
                    progress.update('weekend_warrior', weekend_games)
                    if weekend_games >= 10:
                        earned.append('weekend_warrior')
                        progress.unlock('weekend_warrior', match['played_at'])
                
            except (ValueError, TypeError):
                continue
        
        # Проверяем время
        if morning_games >= 10:
            earned.append('morning_person')
            progress.unlock('morning_person', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if night_games >= 10:
            earned.append('night_owl')
            progress.unlock('night_owl', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if prime_time_games >= 50:
            earned.append('prime_time_player')
            progress.unlock('prime_time_player', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Проверяем месячные достижения
        month_games = sum(daily_games.values())
        if month_games >= 100:
            earned.append('monthly_master')
            progress.unlock('monthly_master', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if month_games >= 300:
            earned.append('seasonal_veteran')
            progress.unlock('seasonal_veteran', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        return earned, progress 