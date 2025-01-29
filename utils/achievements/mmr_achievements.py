"""Достижения за MMR"""
from datetime import datetime
from .base import Achievement, AchievementCategory, AchievementProgress

MMR_ACHIEVEMENTS = [
    # Базовые ранги
    Achievement(
        id='mmr_0',
        name='Начало пути',
        description='Калибровка MMR',
        emoji='🌱',
        category='MMR',
        progress_max=1
    ),
    Achievement(
        id='mmr_500',
        name='Новичок',
        description='Достичь 500 MMR',
        emoji='🎋',
        category='MMR'
    ),
    Achievement(
        id='mmr_1000',
        name='Ученик',
        description='Достичь 1000 MMR',
        emoji='🌿',
        category='MMR'
    ),
    
    # Средние ранги
    Achievement(
        id='mmr_2000',
        name='Боец',
        description='Достичь 2000 MMR',
        emoji='⚔️',
        category='MMR',
        progress_max=2000,
        requires='mmr_0'
    ),
    Achievement(
        id='mmr_3000',
        name='Воин',
        description='Достичь 3000 MMR',
        emoji='🗡️',
        category='MMR'
    ),
    Achievement(
        id='mmr_4000',
        name='Мастер',
        description='Достичь 4000 MMR',
        emoji='🏹',
        category='MMR'
    ),
    
    # Высокие ранги
    Achievement(
        id='mmr_5000',
        name='Элита',
        description='Достичь 5000 MMR',
        emoji='🎯',
        category='MMR'
    ),
    Achievement(
        id='mmr_6000',
        name='Чемпион',
        description='Достичь 6000 MMR',
        emoji='🏆',
        category='MMR'
    ),
    Achievement(
        id='mmr_7000',
        name='Гранд-мастер',
        description='Достичь 7000 MMR',
        emoji='👑',
        category='MMR'
    ),
    
    # Экстремальные ранги
    Achievement(
        id='mmr_8000',
        name='Легенда',
        description='Достичь 8000 MMR',
        emoji='⭐',
        category='MMR'
    ),
    Achievement(
        id='mmr_9000',
        name='Титан',
        description='Достичь 9000 MMR',
        emoji='🌟',
        category='MMR'
    ),
    Achievement(
        id='mmr_10000',
        name='Бессмертный',
        description='Достичь 10000 MMR',
        emoji='💫',
        category='MMR'
    ),
    
    # Достижения за прогресс
    Achievement(
        id='mmr_climb_100',
        name='Первый шаг',
        description='Поднять MMR на 100 за неделю',
        emoji='📈',
        category='MMR'
    ),
    Achievement(
        id='mmr_climb_500',
        name='Быстрый подъём',
        description='Поднять MMR на 500 за месяц',
        emoji='🚀',
        category='MMR'
    ),
    Achievement(
        id='mmr_climb_1000',
        name='Стремительный взлёт',
        description='Поднять MMR на 1000 за сезон',
        emoji='✨',
        category='MMR',
        progress_max=1000,
        hidden=True
    ),
    
    # Достижения за стабильность
    Achievement(
        id='mmr_stable_month',
        name='Стабильность',
        description='Удерживать MMR выше 5000 месяц',
        emoji='🛡️',
        category='MMR'
    ),
    Achievement(
        id='mmr_stable_season',
        name='Железная воля',
        description='Удерживать MMR выше 6000 сезон',
        emoji='🔱',
        category='MMR'
    ),
    Achievement(
        id='mmr_stable_year',
        name='Несокрушимый',
        description='Удерживать MMR выше 7000 год',
        emoji='💎',
        category='MMR'
    )
]

class MMRAchievements(AchievementCategory):
    def __init__(self):
        super().__init__('MMR', MMR_ACHIEVEMENTS)
    
    def check(self, stats, mmr_data=None):
        earned = []
        progress = AchievementProgress()
        
        if not mmr_data:
            return earned, progress
        
        # Получаем текущий MMR, используя get() для безопасности
        current_mmr = mmr_data.get('current_mmr', 0)
        if not current_mmr:
            current_mmr = mmr_data.get('mmr', 0)
        
        # Получаем историю MMR
        mmr_history = mmr_data.get('history', [])
        
        # Проверяем калибровку
        if current_mmr > 0:
            earned.append('mmr_0')
            progress.unlock('mmr_0', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Проверяем достижения за абсолютное значение MMR
        thresholds = [
            (500, 'mmr_500'),
            (1000, 'mmr_1000'),
            (2000, 'mmr_2000'),
            (3000, 'mmr_3000'),
            (4000, 'mmr_4000'),
            (5000, 'mmr_5000'),
            (6000, 'mmr_6000'),
            (7000, 'mmr_7000'),
            (8000, 'mmr_8000'),
            (9000, 'mmr_9000'),
            (10000, 'mmr_10000')
        ]
        
        for threshold, achievement_id in thresholds:
            # Обновляем прогресс
            progress.update(achievement_id, min(current_mmr, threshold))
            
            if current_mmr >= threshold:
                earned.append(achievement_id)
                progress.unlock(achievement_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # Проверяем прогресс MMR если есть история
        if mmr_history:
            # За неделю
            week_start_mmr = mmr_history[-7] if len(mmr_history) >= 7 else mmr_history[0]
            week_progress = current_mmr - week_start_mmr
            
            if week_progress >= 100:
                earned.append('mmr_climb_100')
                progress.unlock('mmr_climb_100', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # За месяц
            month_start_mmr = mmr_history[-30] if len(mmr_history) >= 30 else mmr_history[0]
            month_progress = current_mmr - month_start_mmr
            
            if month_progress >= 500:
                earned.append('mmr_climb_500')
                progress.unlock('mmr_climb_500', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # За сезон
            season_start_mmr = mmr_history[-90] if len(mmr_history) >= 90 else mmr_history[0]
            season_progress = current_mmr - season_start_mmr
            
            # Обновляем прогресс сезонного подъема
            progress.update('mmr_climb_1000', max(0, season_progress))
            
            if season_progress >= 1000:
                earned.append('mmr_climb_1000')
                progress.unlock('mmr_climb_1000', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        return earned, progress 