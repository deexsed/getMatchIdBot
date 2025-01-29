"""
Команды бота
"""
from telegram import BotCommand

DEFAULT_COMMANDS = [
    BotCommand('start', 'Начать работу с ботом'),
    BotCommand('newgame', 'Записать новый матч'),
    BotCommand('stats', 'Показать общую статистику'),
    BotCommand('period', 'Статистика за период'),
    BotCommand('predict', 'Анализ героя'),
    BotCommand('last', 'Последние матчи'),
    BotCommand('mmr', 'Показать текущий MMR и ранг'),
    BotCommand('setmmr', 'Установить MMR (например: /setmmr 3000)'),
    BotCommand('achievements', 'Показать достижения'),
    BotCommand('cancel', 'Отменить текущее действие')
] 