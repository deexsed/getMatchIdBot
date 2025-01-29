"""
Обработчики для матчей
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.hero_service import get_all_heroes, get_user_heroes, HEROES_PER_PAGE
from services.stats_service import get_last_matches
from services.match_service import save_match
from utils.keyboards import (
    get_hero_selection_keyboard,
    get_match_outcome_keyboard,
    get_restart_keyboard
)
from utils.decorators import handle_errors
import json

logger = logging.getLogger(__name__)

@handle_errors
async def new_game(update: Update, context: CallbackContext) -> None:
    """Начинает процесс записи нового матча"""
    context.user_data.clear()
    await update.message.reply_text('Введите ID матча:')
    context.user_data['waiting_for_match_id'] = True

@handle_errors
async def handle_message(update: Update, context: CallbackContext) -> None:
    """Обработчик текстовых сообщений"""
    if context.user_data.get('waiting_for_search'):
        search_query = update.message.text.strip()
        context.user_data['waiting_for_search'] = False
        await send_hero_selection(update, context, search_query=search_query)
        return
        
    if context.user_data.get('waiting_for_match_id'):
        await handle_match_id(update, context)

@handle_errors
async def handle_match_id(update: Update, context: CallbackContext) -> None:
    """Обработка введенного ID матча"""
    nickname = f"@{update.message.from_user.username}" if update.message.from_user.username else update.message.from_user.first_name
    match_id = update.message.text.strip()
    
    if not match_id.isdigit():
        await update.message.reply_text('ID матча должен содержать только цифры.')
        return
        
    if not (8 <= len(match_id) <= 16):
        await update.message.reply_text('ID матча должен быть длиной от 8 до 16 цифр.')
        return

    context.user_data['match_id'] = match_id
    context.user_data['nickname'] = nickname
    context.user_data['waiting_for_match_id'] = False
    
    await send_hero_selection(update, context)

@handle_errors
async def send_hero_selection(update: Update, context: CallbackContext, page: int = 1, search_query: str = None) -> None:
    """Отправляет страницу с героями"""
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
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "Выберите героя:"
    if not search_query:
        text += f"\nСтраница {page} из {max_pages}"
    elif not heroes_to_show:
        text = "По вашему запросу ничего не найдено. Попробуйте другой запрос."
    
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

@handle_errors
async def handle_hero_selection(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    
    data = query.data
    heroes = get_all_heroes()
    hero_names = [hero['name'] for hero in heroes]
    
    if data.startswith("page:"):
        page = int(data.split(":")[1])
        await send_hero_selection(update, context, page=page)
        return
    
    if data == "search":
        await query.message.reply_text(
            "Введите часть имени героя для поиска:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Отмена", callback_data="cancel_search")
            ]])
        )
        context.user_data['waiting_for_search'] = True
        return
    
    if data == "cancel_search":
        context.user_data['waiting_for_search'] = False
        await send_hero_selection(update, context)
        return
    
    if data.startswith("hero:"):
        hero_name = data.split(":")[1]
        if hero_name not in hero_names:
            return

        match_id = context.user_data.get('match_id')
        nickname = context.user_data.get('nickname')

        if match_id is None or nickname is None:
            await start(update, context)
            return

        context.user_data['hero_name'] = hero_name
        await send_match_outcome_selection(query.message)

async def send_match_outcome_selection(message) -> None:
    keyboard = [
        [InlineKeyboardButton("Победа", callback_data='win')],
        [InlineKeyboardButton("Поражение", callback_data='lose')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text('Выберите исход матча:', reply_markup=reply_markup)

async def handle_match_outcome(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data not in ['win', 'lose']:
        return

    match_outcome = query.data
    match_id = context.user_data.get('match_id')
    nickname = context.user_data.get('nickname')
    hero_name = context.user_data.get('hero_name')

    if match_id is None or nickname is None or hero_name is None:
        await start(update, context)
        return

    try:
        save_match(nickname, match_id, hero_name, match_outcome)
        await query.message.reply_text('Данные сохранены!')
        await send_restart_button(query.message)
    except Exception as e:
        logger.error(f"Ошибка при сохранении: {e}")
        await query.message.reply_text(
            'Произошла ошибка при сохранении данных. '
            'Пожалуйста, попробуйте еще раз или обратитесь к администратору.'
        )
    finally:
        context.user_data.clear()

async def send_restart_button(message) -> None:
    """Отправляет кнопку для записи нового матча"""
    keyboard = [[InlineKeyboardButton("Записать новый матч", callback_data='restart')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await message.reply_text('Хотите записать новый матч?', reply_markup=reply_markup)

async def handle_restart(update: Update, context: CallbackContext) -> None:
    """Обработчик кнопки 'Записать новый матч'"""
    query = update.callback_query
    await query.answer()

    # Очищаем данные предыдущего ввода
    context.user_data.clear()
    
    # Используем query.message вместо создания нового Update
    await query.message.reply_text('Введите ID матча:')
    context.user_data['waiting_for_match_id'] = True

async def last_matches(update: Update, context: CallbackContext) -> None:
    """Показывает последние матчи пользователя"""
    nickname = f"@{update.message.from_user.username}" if update.message.from_user.username else update.message.from_user.first_name
    
    try:
        matches = get_last_matches(nickname)
        
        if not matches:
            await update.message.reply_text('У вас пока нет записанных матчей.')
            return
            
        matches_text = "🎮 Ваши последние матчи:\n\n"
        for match in matches:
            outcome_emoji = "✅" if match['outcome'] == 'win' else "❌"
            matches_text += (
                f"{match['played_at']}\n"
                f"Герой: {match['hero']}\n"
                f"Исход: {outcome_emoji}\n"
                f"ID матча: {match['match_id']}\n\n"
            )
            
        await update.message.reply_text(matches_text)
        
    except Exception as e:
        logger.error(f"Ошибка при получении матчей: {e}")
        await update.message.reply_text('Произошла ошибка при получении матчей.') 