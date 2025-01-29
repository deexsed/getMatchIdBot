import logging
from telegram import Update
from telegram.ext import CallbackContext
from utils.decorators import handle_errors
from services.stats_service import get_user_mmr, ensure_user_mmr

logger = logging.getLogger(__name__)

@handle_errors
async def mmr_command(update: Update, context: CallbackContext) -> None:
    """Показывает текущий MMR пользователя"""
    nickname = f"@{update.message.from_user.username}" if update.message.from_user.username else update.message.from_user.first_name
    
    try:
        ensure_user_mmr(nickname)  # Убеждаемся, что запись существует
        mmr_data = get_user_mmr(nickname)
        current_mmr = mmr_data.get('current_mmr', 0)
        
        if current_mmr > 0:
            await update.message.reply_text(f"Ваш текущий MMR: {current_mmr}")
        else:
            await update.message.reply_text("MMR еще не установлен. Используйте /setmmr <значение> чтобы установить MMR.")
    except Exception as e:
        logger.error(f"Error in mmr_command: {e}")
        await update.message.reply_text("Произошла ошибка при получении MMR. Попробуйте позже.") 