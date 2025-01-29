"""
Обработчики для прогнозов
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.hero_service import get_user_heroes, get_hero_prediction
from utils.messages import get_hero_prediction_text
from utils.decorators import handle_errors

logger = logging.getLogger(__name__)

@handle_errors
async def hero_prediction_handler(update: Update, context: CallbackContext) -> None:
    """Команда для получения прогноза по герою"""
    nickname = f"@{update.message.from_user.username}" if update.message.from_user.username else update.message.from_user.first_name
    
    user_heroes = get_user_heroes(nickname)
    
    if not user_heroes:
        await update.message.reply_text('У вас пока нет записанных матчей.')
        return
    
    keyboard = []
    row = []
    
    for i, hero in enumerate(user_heroes, 1):
        row.append(InlineKeyboardButton(hero, callback_data=f'predict_{hero}'))
        if i % 3 == 0:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        'Выберите героя для анализа:\n'
        f'(Доступно героев: {len(user_heroes)})', 
        reply_markup=reply_markup
    )

@handle_errors
async def handle_hero_prediction(update: Update, context: CallbackContext) -> None:
    """Обработчик выбора героя для прогноза"""
    query = update.callback_query
    await query.answer()
    
    hero = query.data.split('_')[1]
    nickname = f"@{query.from_user.username}" if query.from_user.username else query.from_user.first_name
    
    prediction = get_hero_prediction(nickname, hero)
    prediction_text = get_hero_prediction_text(hero, prediction)
    await query.message.reply_text(prediction_text, parse_mode='Markdown') 