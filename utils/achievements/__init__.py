"""Система достижений"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from .match_achievements import MatchAchievements
from .mmr_achievements import MMRAchievements
from .hero_achievements import HeroAchievements
from .winrate_achievements import WinrateAchievements
from .special_achievements import SpecialAchievements

logger = logging.getLogger(__name__)

ACHIEVEMENT_CATEGORIES = [
    MatchAchievements(),
    MMRAchievements(),
    HeroAchievements(),
    WinrateAchievements(),
    SpecialAchievements()
]

def get_all_achievements():
    """Возвращает словарь всех достижений"""
    achievements = {}
    for category in ACHIEVEMENT_CATEGORIES:
        for achievement in category.achievements:
            achievements[achievement.id] = achievement
    return achievements

def check_achievements(stats, mmr_data=None):
    """Проверяет все достижения"""
    earned = set()
    for category in ACHIEVEMENT_CATEGORIES:
        try:
            category_result = category.check(stats, mmr_data)
            # Проверяем, что результат это tuple с двумя элементами
            if isinstance(category_result, tuple) and len(category_result) == 2:
                category_earned, _ = category_result
            else:
                # Если формат неправильный, используем пустой список
                category_earned = []
            earned.update(category_earned)
        except Exception as e:
            logger.error(f"Error checking achievements for category {category.name}: {e}")
            continue
    return list(earned)

def get_categories_keyboard():
    """Создает клавиатуру для выбора категории достижений"""
    keyboard = []
    
    # Добавляем кнопку для просмотра всех достижений
    keyboard.append([InlineKeyboardButton("📋 Все достижения", callback_data="ach_cat_all")])
    
    # Добавляем кнопки для каждой категории
    for category in ACHIEVEMENT_CATEGORIES:
        # Преобразуем имя категории в безопасный формат для callback_data
        safe_category_name = str(category.name).replace(' ', '_').lower()
        keyboard.append([
            InlineKeyboardButton(
                f"{category.emoji} {category.name}",
                callback_data=f"ach_cat_{safe_category_name}"
            )
        ])
    
    return InlineKeyboardMarkup(keyboard)

def get_achievements_keyboard(page, total_pages, show_all=False, category=None):
    """Создает клавиатуру для навигации по достижениям"""
    keyboard = []
    
    # Кнопки навигации
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton("◀️", callback_data=f"ach_page_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="ignore"))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton("▶️", callback_data=f"ach_page_{page+1}"))
    keyboard.append(nav_buttons)
    
    # Кнопки управления
    control_buttons = []
    
    # Кнопка переключения режима отображения
    mode_text = "Скрыть заблокированные" if show_all else "Показать все"
    control_buttons.append(InlineKeyboardButton(mode_text, callback_data="ach_toggle_mode"))
    
    # Кнопка возврата к категориям
    control_buttons.append(InlineKeyboardButton("↩️ К категориям", callback_data="ach_categories"))
    
    keyboard.append(control_buttons)
    
    return InlineKeyboardMarkup(keyboard)

def format_achievements_page(earned, page=1, show_locked=False, category=None, progress=None):
    """Форматирует одну страницу достижений"""
    ITEMS_PER_PAGE = 8
    
    # Преобразуем earned в множество, если это еще не множество
    earned_set = set(earned) if not isinstance(earned, set) else earned
    
    # Формируем плоский список достижений
    all_achievements = []
    
    if category == 'all':
        categories = ACHIEVEMENT_CATEGORIES
    else:
        safe_category = str(category).replace(' ', '_').lower() if category else None
        categories = [cat for cat in ACHIEVEMENT_CATEGORIES 
                     if str(cat.name).replace(' ', '_').lower() == safe_category]
    
    for cat in categories:
        all_achievements.append(('category', cat.name))
        for achievement in cat.achievements:
            is_earned = achievement.id in earned_set
            if is_earned or show_locked:
                all_achievements.append(('achievement', achievement, is_earned))
    
    # Вычисляем общее количество страниц
    total_pages = (len(all_achievements) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    page = min(max(1, page), total_pages)
    
    # Получаем элементы для текущей страницы
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    page_items = all_achievements[start_idx:end_idx]
    
    # Формируем текст
    text = "🏆 *Достижения"
    if category and category != 'all':
        # Находим эмодзи категории
        category_emoji = next((cat.emoji for cat in ACHIEVEMENT_CATEGORIES if cat.name == category), '📋')
        text += f" - {category_emoji} {category}"
    text += ":*\n\n"
    
    for item_type, *data in page_items:
        if item_type == 'category':
            category_emoji = next((cat.emoji for cat in ACHIEVEMENT_CATEGORIES if cat.name == data[0]), '📋')
            text += f"\n*{category_emoji} {data[0]}:*\n"
        else:
            achievement, is_earned = data
            if is_earned:
                # Добавляем время получения
                unlock_time = ""
                if progress and achievement.id in progress.unlocked_at:
                    timestamp = progress.unlocked_at[achievement.id]
                    unlock_time = f" (получено {timestamp})"
                
                text += (
                    f"{achievement.emoji} *{achievement.name}*{unlock_time}\n"
                    f"└ {achievement.description}\n"
                )
            elif not achievement.hidden or show_locked:
                # Добавляем прогресс
                progress_text = ""
                if progress and achievement.id in progress.progress:
                    current = progress.progress[achievement.id]
                    progress_text = achievement.format_progress(current)
                
                text += (
                    f"🔒 _{achievement.name}_{progress_text}\n"
                    f"└ {achievement.description}\n"
                )
    
    text += f"\n✨ Получено {len(earned)} из {len(get_all_achievements())} достижений"
    
    return text, total_pages 