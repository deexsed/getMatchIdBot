"""
Основной модуль приложения
"""
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.error import NetworkError, RetryAfter
import httpx
import asyncio

import config
from database.connection import init_db
from handlers.base import start_command, cancel_command, error_handler
from handlers.matches import (
    new_game, handle_message, handle_hero_selection,
    handle_match_outcome, handle_restart, last_matches
)
from handlers.stats import stats_handler, period_stats_handler, handle_period_stats, mmr_command, set_mmr_command
from handlers.predictions import hero_prediction_handler, handle_hero_prediction
from handlers.achievements import achievements_handler, achievement_button_handler
from utils.bot_commands import DEFAULT_COMMANDS
from utils.hero_import import import_heroes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application):
    """Выполняется после инициализации бота"""
    await application.bot.delete_my_commands()  # Удаляем старые команды
    await application.bot.set_my_commands(DEFAULT_COMMANDS)  # Устанавливаем новые
    logger.info("Обновление базы героев...")
    await import_heroes()  # Обновляем героев при каждом запуске бота
    logger.info("База героев успешно обновлена")

def main():
    # Инициализируем базу данных
    init_db()
    logger.info("База данных инициализирована")
    
    # Добавляем настройки для повторных попыток подключения
    defaults = {
        'connect_timeout': 30.0,
        'read_timeout': 30.0,
        'write_timeout': 30.0,
        'pool_timeout': 30.0,
        'connect_retry_attempts': 5,
        'connect_retry_delay': 1.0
    }
    
    while True:
        try:
            application = (
                ApplicationBuilder()
                .token(config.TG_BOT_TOKEN)
                .post_init(post_init)
                .connection_pool_size(8)
                .pool_timeout(30.0)
                .read_timeout(30.0)
                .write_timeout(30.0)
                .connect_timeout(30.0)
                .build()
            )
            
            # Добавляем обработчики
            application.add_error_handler(error_handler)
            
            # Основные команды
            application.add_handler(CommandHandler('start', start_command))
            application.add_handler(CommandHandler('stats', stats_handler))
            application.add_handler(CommandHandler('period', period_stats_handler))
            application.add_handler(CommandHandler('predict', hero_prediction_handler))
            application.add_handler(CommandHandler('achievements', achievements_handler))
            application.add_handler(CommandHandler('last', last_matches))
            application.add_handler(CommandHandler('cancel', cancel_command))
            
            # Обработчики сообщений и callback'ов
            application.add_handler(CommandHandler('newgame', new_game))
            application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            application.add_handler(CallbackQueryHandler(handle_hero_selection, pattern='^(hero:|page:|search|cancel_search)'))
            application.add_handler(CallbackQueryHandler(handle_match_outcome, pattern='^(win|lose)$'))
            application.add_handler(CallbackQueryHandler(handle_restart, pattern='^restart$'))
            application.add_handler(CallbackQueryHandler(handle_period_stats, pattern='^stats_'))
            application.add_handler(CallbackQueryHandler(handle_hero_prediction, pattern='^predict_'))
            
            # Добавляем обработчики MMR
            application.add_handler(CommandHandler('mmr', mmr_command))
            application.add_handler(CommandHandler('setmmr', set_mmr_command))
            
            # Добавляем обработчик достижений
            application.add_handler(CallbackQueryHandler(achievement_button_handler, pattern='^ach_'))
            
            # Запускаем бота
            logger.info("Запуск бота...")
            application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,
                timeout=30
            )
            
        except (NetworkError, httpx.ReadError, httpx.ConnectError) as e:
            logger.error(f"Ошибка подключения: {e}")
            logger.info("Повторная попытка через 5 секунд...")
            asyncio.sleep(5)
            continue
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            break

if __name__ == '__main__':
    main() 