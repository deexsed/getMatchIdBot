"""Достижения за винрейт"""
from datetime import datetime
from .base import Achievement, AchievementCategory, AchievementProgress

WINRATE_ACHIEVEMENTS = [
    # Базовые достижения
    Achievement(
        id='first_win',
        name='Первая победа',
        description='Выиграть первую игру',
        emoji='🎉',
        category='Винрейт',
        progress_max=1
    ),
    Achievement(
        id='win_streak_3',
        name='Победная серия',
        description='Выиграть 3 игры подряд',
        emoji='🔥',
        category='Винрейт',
        progress_max=3,
        requires='first_win'
    ),
    Achievement(
        id='win_streak_5',
        name='Доминация',
        description='Выиграть 5 игр подряд',
        emoji='⚡',
        category='Винрейт',
        progress_max=5,
        requires='win_streak_3'
    ),
    
    # Достижения за винрейт
    Achievement(
        id='winrate_55',
        name='Стабильность',
        description='Достичь 55% винрейта (мин. 100 игр)',
        emoji='📈',
        category='Винрейт',
        progress_max=55,
        requires='first_win'
    ),
    Achievement(
        id='winrate_60',
        name='Мастерство',
        description='Достичь 60% винрейта (мин. 200 игр)',
        emoji='🌟',
        category='Винрейт',
        progress_max=60,
        requires='winrate_55'
    ),
    Achievement(
        id='winrate_65',
        name='Превосходство',
        description='Достичь 65% винрейта (мин. 300 игр)',
        emoji='💫',
        category='Винрейт',
        progress_max=65,
        requires='winrate_60',
        hidden=True
    ),
    
    # Достижения за количество побед
    Achievement(
        id='wins_50',
        name='Начинающий победитель',
        description='Одержать 50 побед',
        emoji='🎮',
        category='Винрейт',
        progress_max=50,
        requires='first_win'
    ),
    Achievement(
        id='wins_100',
        name='Опытный победитель',
        description='Одержать 100 побед',
        emoji='🎯',
        category='Винрейт',
        progress_max=100,
        requires='wins_50'
    ),
    Achievement(
        id='wins_500',
        name='Мастер побед',
        description='Одержать 500 побед',
        emoji='👑',
        category='Винрейт',
        progress_max=500,
        requires='wins_100'
    ),
    
    # Особые достижения
    Achievement(
        id='perfect_day',
        name='Идеальный день',
        description='Выиграть все игры за день (мин. 5 игр)',
        emoji='🌞',
        category='Винрейт',
        progress_max=5,
        hidden=True
    ),
    Achievement(
        id='comeback_king',
        name='Король камбэков',
        description='Выиграть после серии из 5 поражений',
        emoji='👑',
        category='Винрейт',
        progress_max=5,
        hidden=True
    ),
    Achievement(
        id='weekend_warrior',
        name='Воин выходных',
        description='Выиграть 10 игр за выходные',
        emoji='🎪',
        category='Винрейт',
        progress_max=10,
        requires='wins_50'
    )
]

class WinrateAchievements(AchievementCategory):
    def __init__(self):
        super().__init__('Винрейт', WINRATE_ACHIEVEMENTS)
    
    def check(self, stats, mmr_data=None):
        earned = []
        progress = AchievementProgress()
        
        if not stats:
            return earned, progress  # Всегда возвращаем tuple
        
        total_games = stats.get('total_games', 0)
        total_wins = stats.get('total_wins', 0)
        
        if total_games == 0:
            return earned, progress
        
        # Проверяем базовые достижения
        progress.update('first_win', min(total_wins, 1))
        if total_wins > 0:
            earned.append('first_win')
            progress.unlock('first_win', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Проверяем достижения за количество побед
        progress.update('wins_50', min(total_wins, 50))
        progress.update('wins_100', min(total_wins, 100))
        progress.update('wins_500', min(total_wins, 500))
        
        if total_wins >= 50:
            earned.append('wins_50')
            progress.unlock('wins_50', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if total_wins >= 100:
            earned.append('wins_100')
            progress.unlock('wins_100', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if total_wins >= 500:
            earned.append('wins_500')
            progress.unlock('wins_500', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Проверяем достижения за винрейт
        winrate = (total_wins / total_games) * 100
        progress.update('winrate_55', min(int(winrate), 55))
        progress.update('winrate_60', min(int(winrate), 60))
        progress.update('winrate_65', min(int(winrate), 65))
        
        if total_games >= 100 and winrate >= 55:
            earned.append('winrate_55')
            progress.unlock('winrate_55', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if total_games >= 200 and winrate >= 60:
            earned.append('winrate_60')
            progress.unlock('winrate_60', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if total_games >= 300 and winrate >= 65:
            earned.append('winrate_65')
            progress.unlock('winrate_65', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Проверяем серии и особые достижения
        current_streak = 0
        max_streak = 0
        lose_streak = 0
        daily_games = {}
        weekend_wins = 0
        
        for match in stats.get('matches', []):
            if not match.get('played_at'):
                continue
                
            try:
                match_time = datetime.strptime(match['played_at'], '%Y-%m-%d %H:%M:%S')
                date = match_time.date()
                
                # Проверяем серии побед
                if match.get('outcome') == 'win':
                    current_streak += 1
                    max_streak = max(max_streak, current_streak)
                    lose_streak = 0
                    
                    # Считаем победы в выходные
                    if match_time.weekday() >= 5:  # Суббота и воскресенье
                        weekend_wins += 1
                        progress.update('weekend_warrior', min(weekend_wins, 10))
                else:
                    current_streak = 0
                    lose_streak += 1
                    progress.update('comeback_king', min(lose_streak, 5))
                    
                    if lose_streak >= 5 and match.get('outcome') == 'win':
                        earned.append('comeback_king')
                        progress.unlock('comeback_king', match['played_at'])
                
                # Группируем игры по дням
                if date not in daily_games:
                    daily_games[date] = {'total': 0, 'wins': 0}
                daily_games[date]['total'] += 1
                if match.get('outcome') == 'win':
                    daily_games[date]['wins'] += 1
                
                # Проверяем идеальный день
                if daily_games[date]['total'] >= 5:
                    progress.update('perfect_day', daily_games[date]['wins'])
                    if daily_games[date]['total'] == daily_games[date]['wins']:
                        earned.append('perfect_day')
                        progress.unlock('perfect_day', match['played_at'])
                
            except (ValueError, TypeError):
                continue
        
        # Проверяем серии побед
        progress.update('win_streak_3', min(max_streak, 3))
        progress.update('win_streak_5', min(max_streak, 5))
        
        if max_streak >= 3:
            earned.append('win_streak_3')
            progress.unlock('win_streak_3', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        if max_streak >= 5:
            earned.append('win_streak_5')
            progress.unlock('win_streak_5', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Проверяем достижения выходных
        if weekend_wins >= 10:
            earned.append('weekend_warrior')
            progress.unlock('weekend_warrior', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        return earned, progress 