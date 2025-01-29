"""
Модуль для хранения клавиатур бота
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from services.hero_service import get_all_heroes, get_heroes_by_attribute, HEROES_PER_PAGE

def get_match_outcome_keyboard():
    """Клавиатура для выбора исхода матча"""
    keyboard = [
        [InlineKeyboardButton("Победа", callback_data='win')],
        [InlineKeyboardButton("Поражение", callback_data='lose')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_restart_keyboard():
    """Клавиатура для записи нового матча"""
    keyboard = [[InlineKeyboardButton("Записать новый матч", callback_data='restart')]]
    return InlineKeyboardMarkup(keyboard)

def get_period_stats_keyboard():
    """Клавиатура для выбора периода статистики"""
    keyboard = [
        [InlineKeyboardButton("За 24 часа", callback_data='stats_24h')],
        [InlineKeyboardButton("За неделю", callback_data='stats_week')],
        [InlineKeyboardButton("За месяц", callback_data='stats_month')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_hero_selection_keyboard(page=1, search_query=None):
    """Создает клавиатуру выбора героя"""
    keyboard = []
    heroes = get_all_heroes()
    
    # Добавляем кнопку поиска в начале
    keyboard.append([InlineKeyboardButton("🔍 Поиск", callback_data="search")])
    
    if search_query:
        filtered_heroes = [
            hero for hero in heroes 
            if search_query.lower() in hero['localized_name'].lower()
        ]
        heroes_to_show = filtered_heroes
    else:
        start_idx = (page - 1) * HEROES_PER_PAGE
        end_idx = start_idx + HEROES_PER_PAGE
        heroes_to_show = heroes[start_idx:end_idx]

    # Добавляем кнопки героев по три в ряд
    for i in range(0, len(heroes_to_show), 3):
        row = []
        for j in range(3):
            if i + j < len(heroes_to_show):
                hero = heroes_to_show[i + j]
                row.append(InlineKeyboardButton(
                    hero['localized_name'], 
                    callback_data=f"hero:{hero['name']}"
                ))
        keyboard.append(row)
    
    # Добавляем навигационные кнопки
    if not search_query:
        nav_buttons = []
        max_pages = (len(heroes) + HEROES_PER_PAGE - 1) // HEROES_PER_PAGE
        
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"page:{page-1}"))
        if page < max_pages:
            nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"page:{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(keyboard) 