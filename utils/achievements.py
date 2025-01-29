"""
Система достижений
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from . import ACHIEVEMENT_CATEGORIES, get_all_achievements

def get_categories_keyboard():
    """Создает клавиатуру для выбора категории достижений"""
    keyboard = []
    
    # Добавляем кнопку для просмотра всех достижений
    keyboard.append([InlineKeyboardButton("📋 Все достижения", callback_data="ach_cat_all")])
    
    # Добавляем кнопки для каждой категории
    for category in ACHIEVEMENT_CATEGORIES:
        keyboard.append([
            InlineKeyboardButton(
                f"{category.name}",
                callback_data=f"ach_cat_{category.name}"
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

def format_achievements_page(earned, page=1, show_locked=False, category=None):
    """Форматирует одну страницу достижений"""
    ITEMS_PER_PAGE = 8
    
    # Формируем плоский список достижений
    all_achievements = []
    earned_set = set(earned)
    
    if category == 'all':
        categories = ACHIEVEMENT_CATEGORIES
    else:
        categories = [cat for cat in ACHIEVEMENT_CATEGORIES if cat.name == category]
    
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
        text += f" - {category}"
    text += ":*\n\n"
    
    for item_type, *data in page_items:
        if item_type == 'category':
            text += f"\n*{data[0]}:*\n"
        else:
            achievement, is_earned = data
            if is_earned:
                text += (
                    f"{achievement.emoji} *{achievement.name}*\n"
                    f"└ {achievement.description}\n"
                )
            else:
                text += (
                    f"🔒 _{achievement.name}_\n"
                    f"└ {achievement.description}\n"
                )
    
    text += f"\n✨ Получено {len(earned)} из {len(get_all_achievements())} достижений"
    
    return text, total_pages 