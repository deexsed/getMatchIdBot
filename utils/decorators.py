"""
Декораторы для обработки ошибок и логирования
"""
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def handle_errors(func):
    """Декоратор для обработки ошибок в хендлерах"""
    @wraps(func)
    async def wrapper(update, context, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка в {func.__name__}: {e}")
            if update.effective_message:
                await update.effective_message.reply_text(
                    "Произошла ошибка. Попробуйте еще раз или обратитесь к администратору."
                )
    return wrapper 