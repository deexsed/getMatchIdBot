"""Особые достижения"""
from datetime import datetime, timedelta
from .base import Achievement, AchievementCategory, AchievementProgress

SPECIAL_ACHIEVEMENTS = [
    # Временные достижения
    Achievement(
        id='early_bird',
        name='Ранняя пташка',
        description='Выиграть 5 игр до 9 утра',
        emoji='🌅',
        category='Особые'
    ),
    Achievement(
        id='night_owl',
        name='Ночная сова',
        description='Выиграть 5 игр после 23:00',
        emoji='🦉',
        category='Особые'
    ),
    Achievement(
        id='lunch_break',
        name='Обеденный перерыв',
        description='Выиграть 10 игр в обеденное время (12:00-14:00)',
        emoji='🍽️',
        category='Особые'
    ),
    
    # Сезонные достижения
    Achievement(
        id='summer_grinder',
        name='Летний гринд',
        description='Сыграть 100 игр летом',
        emoji='☀️',
        category='Особые'
    ),
    Achievement(
        id='winter_warrior',
        name='Зимний воин',
        description='Сыграть 100 игр зимой',
        emoji='❄️',
        category='Особые'
    ),
    Achievement(
        id='new_year_spirit',
        name='Новогодний дух',
        description='Сыграть в новогоднюю ночь',
        emoji='🎄',
        category='Особые'
    ),
    
    # Достижения за серии
    Achievement(
        id='comeback_master',
        name='Мастер камбэков',
        description='Выиграть после серии из 7+ поражений',
        emoji='🔄',
        category='Особые'
    ),
    Achievement(
        id='perfect_week',
        name='Идеальная неделя',
        description='Выиграть все игры за неделю (мин. 10 игр)',
        emoji='✨',
        category='Особые'
    ),
    Achievement(
        id='weekend_marathon',
        name='Марафонец выходных',
        description='Сыграть 20 игр за выходные',
        emoji='🏃',
        category='Особые'
    ),
    
    # Социальные достижения
    Achievement(
        id='party_player',
        name='Командный игрок',
        description='Сыграть 50 игр в группе',
        emoji='👥',
        category='Особые'
    ),
    Achievement(
        id='duo_master',
        name='Мастер дуо',
        description='Выиграть 20 игр с одним тиммейтом',
        emoji='🤝',
        category='Особые'
    ),
    Achievement(
        id='team_spirit',
        name='Командный дух',
        description='Выиграть 10 игр в полной группе',
        emoji='🎭',
        category='Особые'
    ),
    
    # Редкие достижения
    Achievement(
        id='holiday_warrior',
        name='Праздничный воин',
        description='Играть в каждый праздник месяца',
        emoji='🎉',
        category='Особые'
    ),
    Achievement(
        id='dedication',
        name='Преданность',
        description='Играть каждый день месяца',
        emoji='📅',
        category='Особые'
    ),
    Achievement(
        id='all_day_grinder',
        name='Круглосуточный игрок',
        description='Сыграть в каждый час суток',
        emoji='🕐',
        category='Особые'
    )
]

class SpecialAchievements(AchievementCategory):
    def __init__(self):
        super().__init__('Особые', SPECIAL_ACHIEVEMENTS)
    
    def check(self, stats, mmr_data=None):
        earned = []
        progress = AchievementProgress()
        
        if not stats:
            return earned, progress  # Всегда возвращаем tuple
        
        matches = stats.get('matches', [])
        
        if not matches:
            return earned, progress
        
        # Счетчики для временных достижений
        early_wins = 0
        night_wins = 0
        lunch_wins = 0
        hours_played = set()
        
        # Счетчики для сезонных достижений
        summer_games = 0
        winter_games = 0
        new_year_played = False
        
        # Счетчики для серий
        lose_streak = 0
        weekly_games = {}
        weekend_games = 0
        
        # Счетчики для социальных достижений
        party_games = 0
        duo_games = {}
        full_team_wins = 0
        
        # Счетчики для редких достижений
        daily_games = {}
        holidays = set()  # Здесь можно добавить список праздников
        
        for match in matches:
            if not match.get('played_at'):
                continue
                
            try:
                match_time = datetime.strptime(match['played_at'], '%Y-%m-%d %H:%M:%S')
                hour = match_time.hour
                date = match_time.date()
                month = match_time.month
                
                # Проверяем временные достижения
                hours_played.add(hour)
                if match.get('outcome') == 'win':
                    if 5 <= hour < 9:
                        early_wins += 1
                    elif 23 <= hour or hour < 5:
                        night_wins += 1
                    elif 12 <= hour < 14:
                        lunch_wins += 1
                
                # Проверяем сезонные достижения
                if 6 <= month <= 8:  # Лето
                    summer_games += 1
                elif month in [12, 1, 2]:  # Зима
                    winter_games += 1
                
                # Проверяем новогоднюю ночь
                if month == 12 and date.day == 31:
                    if 22 <= hour or hour < 2:
                        new_year_played = True
                
                # Проверяем серии
                if match.get('outcome') == 'lose':
                    lose_streak += 1
                else:
                    if lose_streak >= 7:
                        earned.append('comeback_master')
                    lose_streak = 0
                
                # Группируем игры по неделям и выходным
                week_num = date.isocalendar()[1]
                if week_num not in weekly_games:
                    weekly_games[week_num] = {'total': 0, 'wins': 0}
                weekly_games[week_num]['total'] += 1
                if match.get('outcome') == 'win':
                    weekly_games[week_num]['wins'] += 1
                
                if date.weekday() >= 5:  # Выходные
                    weekend_games += 1
                
                # Проверяем социальные достижения
                party_size = len(match.get('party', []))
                if party_size > 1:
                    party_games += 1
                    if party_size == 5:
                        if match.get('outcome') == 'win':
                            full_team_wins += 1
                    
                    # Считаем игры с каждым тиммейтом
                    for teammate in match.get('party', []):
                        if teammate != stats.get('player_id'):
                            duo_games[teammate] = duo_games.get(teammate, 0) + 1
                
                # Собираем статистику по дням
                if date not in daily_games:
                    daily_games[date] = True
                
            except (ValueError, TypeError):
                continue
        
        # Проверяем достижения
        if early_wins >= 5:
            earned.append('early_bird')
        if night_wins >= 5:
            earned.append('night_owl')
        if lunch_wins >= 10:
            earned.append('lunch_break')
        
        if summer_games >= 100:
            earned.append('summer_grinder')
        if winter_games >= 100:
            earned.append('winter_warrior')
        if new_year_played:
            earned.append('new_year_spirit')
        
        # Проверяем недельные достижения
        for week_stats in weekly_games.values():
            if week_stats['total'] >= 10 and week_stats['total'] == week_stats['wins']:
                earned.append('perfect_week')
        
        if weekend_games >= 20:
            earned.append('weekend_marathon')
        
        if party_games >= 50:
            earned.append('party_player')
        if any(games >= 20 for games in duo_games.values()):
            earned.append('duo_master')
        if full_team_wins >= 10:
            earned.append('team_spirit')
        
        # Проверяем редкие достижения
        if len(hours_played) == 24:
            earned.append('all_day_grinder')
        
        # Проверяем ежедневные игры
        days_in_month = max(daily_games.keys()).day if daily_games else 0
        if days_in_month >= 28:  # Учитываем разное количество дней в месяцах
            earned.append('dedication')
        
        return earned, progress 