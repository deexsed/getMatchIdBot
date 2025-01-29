"""
Обработчики для статистики
"""
import logging
from telegram import Update
from telegram.ext import CallbackContext
from services.stats_service import get_user_stats, get_period_stats, get_user_mmr, update_user_mmr
from utils.messages import get_stats_text
from utils.keyboards import get_period_stats_keyboard
from utils.decorators import handle_errors
from utils.rank_utils import get_rank_info

logger = logging.getLogger(__name__)

@handle_errors
async def stats_handler(update: Update, context: CallbackContext) -> None:
    """Показывает статистику пользователя"""
    nickname = f"@{update.message.from_user.username}" if update.message.from_user.username else update.message.from_user.first_name
    
    stats_data = get_user_stats(nickname)
    
    if stats_data['total_games'] == 0:
        await update.message.reply_text('У вас пока нет записанных матчей.')
        return
        
    stats_text = get_stats_text(stats_data)
    await update.message.reply_text(stats_text, parse_mode='Markdown')

@handle_errors
async def period_stats_handler(update: Update, context: CallbackContext) -> None:
    """Показывает статистику за определенный период"""
    keyboard = get_period_stats_keyboard()
    await update.message.reply_text('Выберите период:', reply_markup=keyboard)

@handle_errors
async def handle_period_stats(update: Update, context: CallbackContext) -> None:
    """Обработчик выбора периода статистики"""
    query = update.callback_query
    await query.answer()
    
    nickname = f"@{query.from_user.username}" if query.from_user.username else query.from_user.first_name
    period = query.data.split('_')[1]
    
    period_days = {
        '24h': 1,
        'week': 7,
        'month': 30
    }[period]
    
    stats = get_period_stats(nickname, period_days)
    
    if stats['total_games'] == 0:
        await query.message.reply_text(f'Нет матчей за выбранный период.')
        return
    
    period_text = {
        '24h': "за последние 24 часа",
        'week': "за последнюю неделю",
        'month': "за последний месяц"
    }[period]
    
    stats_text = get_stats_text(stats)
    await query.message.reply_text(stats_text, parse_mode='Markdown')

@handle_errors
async def mmr_command(update: Update, context: CallbackContext) -> None:
    """Показывает текущий MMR и ранг"""
    nickname = f"@{update.message.from_user.username}" if update.message.from_user.username else update.message.from_user.first_name
    
    mmr_data = get_user_mmr(nickname)
    if not mmr_data or mmr_data['current_mmr'] is None:
        await update.message.reply_text(
            'MMR не установлен. Используйте команду /setmmr <число> для установки MMR.'
        )
        return
    
    rank_info = get_rank_info(mmr_data['current_mmr'])
    if not rank_info:
        await update.message.reply_text('Ошибка при определении ранга.')
        return
    
    medal_progress_bar = generate_progress_bar(rank_info['medal_progress'])
    rank_progress_bar = generate_progress_bar(rank_info['next_rank_progress'])
    
    text = (
        f"🎮 *Ваш текущий MMR:* {mmr_data['current_mmr']}\n"
        f"🏆 *Ранг:* {rank_info['emoji']} {rank_info['rank']} [{rank_info['medal']}]\n\n"
    )
    
    # Прогресс до следующей медали
    text += (
        f"*Прогресс до {rank_info['rank']} [{rank_info['medal'] + 1 if rank_info['medal'] < 5 else 1}]:*\n"
        f"{medal_progress_bar} {rank_info['medal_progress']:.1f}%\n"
        f"• Осталось набрать: {rank_info['mmr_to_next_medal']} MMR\n\n"
    )
    
    # Прогресс до следующего ранга
    if rank_info['rank'] != 'Immortal':
        text += (
            f"*Прогресс до {rank_info['next_rank']}:*\n"
            f"{rank_progress_bar} {rank_info['next_rank_progress']:.1f}%\n"
            f"• Осталось набрать: {rank_info['mmr_to_next_rank']} MMR\n"
            f"• Диапазон текущего ранга: {rank_info['current_mmr_range'][0]}-{rank_info['current_mmr_range'][1]} MMR\n"
        )
    
    text += f"\n💫 Последнее обновление: {mmr_data['history']}"
    
    await update.message.reply_text(text, parse_mode='Markdown')

def generate_progress_bar(percentage, length=10):
    """Генерирует прогресс-бар"""
    filled = int(percentage / 100 * length)
    return '▰' * filled + '▱' * (length - filled)

@handle_errors
async def set_mmr_command(update: Update, context: CallbackContext) -> None:
    """Устанавливает MMR пользователя"""
    if not context.args:
        await update.message.reply_text(
            'Пожалуйста, укажите MMR. Пример: /setmmr 3000'
        )
        return
    
    try:
        mmr = int(context.args[0])
        if mmr < 0 or mmr > 12000:  # Разумные ограничения
            await update.message.reply_text('MMR должен быть между 0 и 12000.')
            return
        
        nickname = f"@{update.message.from_user.username}" if update.message.from_user.username else update.message.from_user.first_name
        update_user_mmr(nickname, mmr)
        
        rank_info = get_rank_info(mmr)
        
        await update.message.reply_text(
            f"✅ MMR успешно обновлен!\n"
            f"🎮 *Текущий MMR:* {mmr}\n"
            f"🏆 *Ваш ранг:* {rank_info['emoji']} {rank_info['rank']} [{rank_info['medal']}]",
            parse_mode='Markdown'
        )
        
    except ValueError:
        await update.message.reply_text(
            'Пожалуйста, введите корректное число. Пример: /setmmr 3000'
        ) 