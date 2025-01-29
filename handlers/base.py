"""
Базовые обработчики команд
"""
import logging
from telegram import Update
from telegram.ext import CallbackContext
from utils.decorators import handle_errors
from utils.bot_commands import DEFAULT_COMMANDS

logger = logging.getLogger(__name__)

@handle_errors
async def start_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /start"""
    commands_text = "\n".join([
        f"/{cmd.command} - {cmd.description}" for cmd in DEFAULT_COMMANDS
    ])
    
    welcome_text = (
        "👋 Добро пожаловать в DotaStatsBot!\n\n"
        "🤖 Я помогу вам отслеживать статистику ваших матчей в Dota 2.\n\n"
        "*Доступные команды:*\n"
        f"{commands_text}\n\n"
        "📝 Чтобы начать, используйте /newgame для записи нового матча или "
        "/stats для просмотра вашей статистики.\n\n"
        "👨‍💻 *Автор:* @deexsed"
    )
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown'
    )

@handle_errors
async def cancel_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /cancel"""
    context.user_data.clear()
    await update.message.reply_text(
        'Ввод отменен. Используйте /start для начала нового ввода.'
    )

@handle_errors
async def error_handler(update: Update, context: CallbackContext) -> None:
    """Глобальный обработчик ошибок"""
    error = context.error
    logger.error(f"Произошла ошибка: {error}")
    
    if update and update.effective_message:
        try:
            if context.user_data and context.user_data.get('waiting_for_match_id'):
                await update.effective_message.reply_text(
                    "Введите ID матча:"
                )
            else:
                await update.effective_message.reply_text(
                    "Произошла ошибка. Используйте /start для начала нового ввода."
                )
                if context.user_data:
                    context.user_data.clear()
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения об ошибке: {e}")
    else:
        logger.error("Не удалось отправить сообщение об ошибке: update или effective_message отсутствует") 