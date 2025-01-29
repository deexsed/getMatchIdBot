"""Достижения за героев"""
import logging
from datetime import datetime
from .base import Achievement, AchievementCategory, AchievementProgress

logger = logging.getLogger(__name__)

HERO_ACHIEVEMENTS = [
    # Базовые достижения
    Achievement(
        id='hero_first',
        name='Первый герой',
        description='Сыграть первую игру на герое',
        emoji='👶',
        category='Герои',
        progress_max=1
    ),
    Achievement(
        id='hero_ten',
        name='Коллекционер',
        description='Сыграть на 10 разных героях',
        emoji='📚',
        category='Герои',
        progress_max=10,
        requires='hero_first'
    ),
    Achievement(
        id='hero_twenty',
        name='Искатель приключений',
        description='Сыграть на 20 разных героях',
        emoji='🎭',
        category='Герои',
        progress_max=20,
        requires='hero_ten'
    ),
    
    # Мастерство героев
    Achievement(
        id='hero_mastery_10',
        name='Начинающий мастер',
        description='Сыграть 10 игр на одном герое',
        emoji='🎯',
        category='Герои',
        progress_max=10,
        requires='hero_first'
    ),
    Achievement(
        id='hero_mastery_50',
        name='Опытный мастер',
        description='Сыграть 50 игр на одном герое',
        emoji='⚔️',
        category='Герои',
        progress_max=50,
        requires='hero_mastery_10'
    ),
    Achievement(
        id='hero_mastery_100',
        name='Эксперт героя',
        description='Сыграть 100 игр на одном герое',
        emoji='👑',
        category='Герои',
        progress_max=100,
        requires='hero_mastery_50'
    ),
    
    # Винрейт на героях
    Achievement(
        id='hero_winrate_60',
        name='Талант',
        description='Достичь 60% винрейта на герое (мин. 20 игр)',
        emoji='🌟',
        category='Герои',
        progress_max=60,
        requires='hero_mastery_10'
    ),
    Achievement(
        id='hero_winrate_70',
        name='Виртуоз',
        description='Достичь 70% винрейта на герое (мин. 30 игр)',
        emoji='💫',
        category='Герои',
        progress_max=70,
        requires='hero_winrate_60'
    ),
    Achievement(
        id='hero_winrate_80',
        name='Легенда героя',
        description='Достичь 80% винрейта на герое (мин. 40 игр)',
        emoji='⭐',
        category='Герои',
        progress_max=80,
        requires='hero_winrate_70',
        hidden=True
    ),
    
    # Серии побед
    Achievement(
        id='hero_streak_5',
        name='Победная серия',
        description='Выиграть 5 игр подряд на одном герое',
        emoji='🔥',
        category='Герои',
        progress_max=5
    ),
    Achievement(
        id='hero_streak_10',
        name='Непобедимый',
        description='Выиграть 10 игр подряд на одном герое',
        emoji='⚡',
        category='Герои',
        progress_max=10,
        requires='hero_streak_5'
    ),
    Achievement(
        id='hero_streak_15',
        name='Доминатор',
        description='Выиграть 15 игр подряд на одном герое',
        emoji='🔱',
        category='Герои',
        progress_max=15,
        requires='hero_streak_10',
        hidden=True
    ),
    
    # Разнообразие
    Achievement(
        id='hero_roles_all',
        name='Универсал',
        description='Сыграть на героях всех ролей',
        emoji='🎭',
        category='Герои',
        progress_max=5,
        requires='hero_ten'
    ),
    Achievement(
        id='hero_attributes_all',
        name='Мастер стихий',
        description='Сыграть на героях всех атрибутов',
        emoji='🌈',
        category='Герои',
        progress_max=3,
        requires='hero_ten'
    ),
    Achievement(
        id='hero_complexity_3',
        name='Сложный путь',
        description='Выиграть 10 игр на героях со сложностью 3',
        emoji='💎',
        category='Герои',
        progress_max=10,
        requires='hero_twenty',
        hidden=True
    )
]

class HeroAchievements(AchievementCategory):
    def __init__(self):
        super().__init__('Герои', HERO_ACHIEVEMENTS)
    
    def check(self, stats, mmr_data=None):
        earned = []
        progress = AchievementProgress()
        heroes = stats.get('heroes', [])
        
        if not heroes:
            return earned, progress  # Всегда возвращаем tuple
        
        try:
            # Безопасное получение ID героя
            def get_hero_id(hero_data):
                try:
                    hero = hero_data.get('hero')
                    if isinstance(hero, (list, dict)):
                        return f"hero_{hash(str(sorted(hero.items()) if isinstance(hero, dict) else hero))}"
                    return f"hero_{hero}"
                except Exception as e:
                    logger.error(f"Error getting hero ID: {e}, hero_data: {hero_data}")
                    return "unknown_hero"
            
            # Логируем структуру данных для отладки
            logger.debug(f"First hero data: {heroes[0] if heroes else None}")
            
            # Проверяем базовые достижения
            unique_heroes = set()
            for hero in heroes:
                try:
                    hero_id = get_hero_id(hero)
                    unique_heroes.add(hero_id)
                except Exception as e:
                    logger.error(f"Error processing hero: {e}, hero: {hero}")
            
            unique_count = len(unique_heroes)
            logger.debug(f"Unique heroes count: {unique_count}")
            
            progress.update('hero_first', min(unique_count, 1))
            progress.update('hero_ten', min(unique_count, 10))
            progress.update('hero_twenty', min(unique_count, 20))
            
            if unique_count >= 1:
                earned.append('hero_first')
                progress.unlock('hero_first', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if unique_count >= 10:
                earned.append('hero_ten')
                progress.unlock('hero_ten', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if unique_count >= 20:
                earned.append('hero_twenty')
                progress.unlock('hero_twenty', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Группируем статистику по героям
            hero_stats = {}
            for match in heroes:
                try:
                    hero_id = get_hero_id(match)
                    if hero_id not in hero_stats:
                        hero_stats[hero_id] = {
                            'games': 0,
                            'wins': 0,
                            'current_streak': 0,
                            'info': {}
                        }
                    
                    # Безопасное получение информации о герое
                    hero_info = match.get('hero_info', {})
                    if isinstance(hero_info, dict):
                        hero_stats[hero_id]['info'] = {
                            'role': str(hero_info.get('role', '')),
                            'attribute': str(hero_info.get('attribute', '')),
                            'complexity': int(hero_info.get('complexity', 0))
                        }
                    
                    hero_stats[hero_id]['games'] += 1
                    if match.get('outcome') == 'win':
                        hero_stats[hero_id]['wins'] += 1
                        hero_stats[hero_id]['current_streak'] += 1
                    else:
                        hero_stats[hero_id]['current_streak'] = 0
                except Exception as e:
                    logger.error(f"Error processing match: {e}, match: {match}")
            
            # Проверяем мастерство героев
            for hero_id, hero_data in hero_stats.items():
                games = hero_data['games']
                wins = hero_data['wins']
                streak = hero_data['current_streak']
                
                # Обновляем прогресс мастерства
                progress.update(f'hero_mastery_{hero_id}', min(games, 100))
                
                if games >= 10:
                    earned.append('hero_mastery_10')
                    progress.unlock('hero_mastery_10', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                if games >= 50:
                    earned.append('hero_mastery_50')
                    progress.unlock('hero_mastery_50', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                if games >= 100:
                    earned.append('hero_mastery_100')
                    progress.unlock('hero_mastery_100', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                
                # Проверяем винрейт
                if games >= 20:
                    winrate = (wins / games) * 100
                    progress.update(f'hero_winrate_{hero_id}', min(int(winrate), 80))
                    
                    if winrate >= 60:
                        earned.append('hero_winrate_60')
                        progress.unlock('hero_winrate_60', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    if games >= 30 and winrate >= 70:
                        earned.append('hero_winrate_70')
                        progress.unlock('hero_winrate_70', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    if games >= 40 and winrate >= 80:
                        earned.append('hero_winrate_80')
                        progress.unlock('hero_winrate_80', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                
                # Проверяем серии побед
                progress.update(f'hero_streak_{hero_id}', min(streak, 15))
                
                if streak >= 5:
                    earned.append('hero_streak_5')
                    progress.unlock('hero_streak_5', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                if streak >= 10:
                    earned.append('hero_streak_10')
                    progress.unlock('hero_streak_10', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                if streak >= 15:
                    earned.append('hero_streak_15')
                    progress.unlock('hero_streak_15', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Проверяем разнообразие
            roles = set()
            attributes = set()
            complex_hero_wins = 0
            
            for hero_data in hero_stats.values():
                hero_info = hero_data['info']
                role = hero_info.get('role', '')
                attribute = hero_info.get('attribute', '')
                
                if role and role != 'None':
                    roles.add(role)
                if attribute and attribute != 'None':
                    attributes.add(attribute)
                
                if hero_info.get('complexity', 0) == 3:
                    complex_hero_wins += hero_data['wins']
            
            # Обновляем прогресс разнообразия
            progress.update('hero_roles_all', len(roles))
            progress.update('hero_attributes_all', len(attributes))
            progress.update('hero_complexity_3', min(complex_hero_wins, 10))
            
            if len(roles) >= 5:
                earned.append('hero_roles_all')
                progress.unlock('hero_roles_all', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if len(attributes) >= 3:
                earned.append('hero_attributes_all')
                progress.unlock('hero_attributes_all', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            if complex_hero_wins >= 10:
                earned.append('hero_complexity_3')
                progress.unlock('hero_complexity_3', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
        except Exception as e:
            logger.error(f"Error checking hero achievements: {e}")
            return earned, progress  # Возвращаем tuple даже при ошибке
        
        return earned, progress  # Убедимся что возвращаем tuple 