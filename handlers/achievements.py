"""
Обработчики для достижений
"""
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from services.stats_service import get_user_stats, get_user_mmr
from utils.achievements import check_achievements, format_achievements_page, get_achievements_keyboard, get_categories_keyboard, ACHIEVEMENT_CATEGORIES
from utils.decorators import handle_errors

logger = logging.getLogger(__name__)

@handle_errors
async def achievements_handler(update: Update, context: CallbackContext) -> None:
    """Показывает категории достижений"""
    nickname = f"@{update.message.from_user.username}" if update.message.from_user.username else update.message.from_user.first_name
    
    # Очищаем предыдущие данные о достижениях
    context.user_data.pop('achievements_page', None)
    context.user_data.pop('achievements_category', None)
    context.user_data.pop('show_all_achievements', None)
    
    # Показываем список категорий
    keyboard = get_categories_keyboard()
    await update.message.reply_text(
        "Выберите категорию достижений:",
        reply_markup=keyboard
    )

@handle_errors
async def achievement_button_handler(update: Update, context: CallbackContext) -> None:
    """Обработчик кнопок достижений"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    current_page = int(context.user_data.get('achievements_page', 1))
    show_all = context.user_data.get('show_all_achievements', False)
    category = context.user_data.get('achievements_category', 'all')
    
    if data == 'ach_categories':
        # Возврат к списку категорий
        keyboard = get_categories_keyboard()
        await query.message.edit_text(
            "Выберите категорию достижений:",
            reply_markup=keyboard
        )
        context.user_data.pop('achievements_page', None)
        context.user_data.pop('achievements_category', None)
        return
    
    elif data.startswith('ach_cat_'):
        # Выбор категории
        category = data.replace('ach_cat_', '')
        # Преобразуем обратно в оригинальное имя категории если это не 'all'
        if category != 'all':
            for cat in ACHIEVEMENT_CATEGORIES:
                if str(cat.name).replace(' ', '_').lower() == category:
                    category = cat.name
                    break
        context.user_data['achievements_category'] = category
        current_page = 1
    
    elif data.startswith('ach_page_'):
        # Навигация по страницам
        current_page = int(data.split('_')[-1])
        context.user_data['achievements_page'] = current_page
    
    elif data == 'ach_toggle_mode':
        # Переключение режима отображения
        show_all = not show_all
        context.user_data['show_all_achievements'] = show_all
    
    # Получаем достижения
    nickname = f"@{query.from_user.username}" if query.from_user.username else query.from_user.first_name
    stats = get_user_stats(nickname)
    mmr_data = get_user_mmr(nickname)
    earned_achievements = check_achievements(stats, mmr_data)
    
    # Обновляем сообщение
    achievements_text, total_pages = format_achievements_page(
        earned_achievements,
        page=current_page,
        show_locked=show_all,
        category=category
    )
    keyboard = get_achievements_keyboard(
        current_page,
        total_pages,
        show_all=show_all,
        category=category
    )
    
    await query.message.edit_text(
        achievements_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    ) 