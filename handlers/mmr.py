"""
Обработчики для работы с MMR
"""
import logging
from telegram import Update
from telegram.ext import CallbackContext
from database.models import get_or_create_user, get_user_mmr, update_user_mmr
from utils.decorators import handle_errors

logger = logging.getLogger(__name__)

def get_rank_by_mmr(mmr):
    """Возвращает ранг и подранг на основе MMR"""
    if mmr is None:
        return "Не установлен", None
        
    # Определяем основной ранг
    if mmr >= 5420:
        rank = "Immortal"
        subrank = None  # У Immortal нет подранга
    elif mmr >= 4620:
        rank = "Divine"
        subrank = (mmr - 4620) // 270 + 1  # Каждые ~270 MMR
    elif mmr >= 3850:
        rank = "Ancient"
        subrank = (mmr - 3850) // 260 + 1
    elif mmr >= 3080:
        rank = "Legend"
        subrank = (mmr - 3080) // 260 + 1
    elif mmr >= 2310:
        rank = "Archon"
        subrank = (mmr - 2310) // 260 + 1
    elif mmr >= 1540:
        rank = "Crusader"
        subrank = (mmr - 1540) // 260 + 1
    elif mmr >= 770:
        rank = "Guardian"
        subrank = (mmr - 770) // 260 + 1
    else:
        rank = "Herald"
        subrank = (mmr // 260) + 1
    
    # Ограничиваем подранг от 1 до 5
    if subrank is not None:
        subrank = max(1, min(5, subrank))
    
    return rank, subrank

def get_rank_emoji(rank):
    """Возвращает эмодзи для ранга"""
    rank_emojis = {
        "Immortal": "🔱",
        "Divine": "⚜️",
        "Ancient": "🏅",
        "Legend": "🎖️",
        "Archon": "🏆",
        "Crusader": "🛡️",
        "Guardian": "🔰",
        "Herald": "⭐",
        "Не установлен": "❓"
    }
    return rank_emojis.get(rank, "❓")

def format_rank(rank, subrank):
    """Форматирует ранг с подрангом"""
    if rank == "Не установлен":
        return rank
    elif rank == "Immortal":
        return rank
    else:
        return f"{rank} {subrank}"

@handle_errors
async def mmr_command(update: Update, context: CallbackContext) -> None:
    """Показывает текущий MMR пользователя"""
    nickname = f"@{update.message.from_user.username}" if update.message.from_user.username else update.message.from_user.first_name
    user_id = get_or_create_user(nickname)
    mmr_data = get_user_mmr(user_id)
    
    mmr = mmr_data['mmr'] if mmr_data else None
    rank, subrank = get_rank_by_mmr(mmr)
    rank_emoji = get_rank_emoji(rank)
    
    if mmr is None:
        message = (
            "❗ MMR не установлен\n"
            "Используйте команду /setmmr чтобы установить свой MMR"
        )
    else:
        formatted_rank = format_rank(rank, subrank)
        message = (
            f"🎮 Текущий MMR: {mmr}\n"
            f"{rank_emoji} Ранг: {formatted_rank}"
        )
        
        # Добавляем информацию о прогрессе до следующего ранга
        if rank != "Immortal":
            next_rank_mmr = {
                "Herald": 770,
                "Guardian": 1540,
                "Crusader": 2310,
                "Archon": 3080,
                "Legend": 3850,
                "Ancient": 4620,
                "Divine": 5420
            }
            
            current_rank_mmr = next_rank_mmr.get(rank, 0)
            next_rank = list(next_rank_mmr.keys())[list(next_rank_mmr.keys()).index(rank) + 1]
            next_rank_required = next_rank_mmr[next_rank]
            
            mmr_needed = next_rank_required - mmr
            progress = ((mmr - current_rank_mmr) / (next_rank_required - current_rank_mmr)) * 100
            
            message += f"\n\nПрогресс до {next_rank}:\n"
            progress_bar = "█" * int(progress / 10) + "▁" * (10 - int(progress / 10))
            message += f"{progress_bar} {progress:.1f}%\n"
            message += f"• Осталось набрать: {mmr_needed} MMR"
    
    await update.message.reply_text(message)

@handle_errors
async def set_mmr_command(update: Update, context: CallbackContext) -> None:
    """Устанавливает MMR пользователя"""
    if not context.args:
        await update.message.reply_text(
            "Пожалуйста, укажите значение MMR.\n"
            "Пример: /setmmr 2000"
        )
        return
    
    try:
        mmr = int(context.args[0])
        if mmr < 0 or mmr > 12000:  # Проверка на разумные пределы
            raise ValueError
    except ValueError:
        await update.message.reply_text("Пожалуйста, укажите корректное значение MMR (0-12000)")
        return
    
    nickname = f"@{update.message.from_user.username}" if update.message.from_user.username else update.message.from_user.first_name
    user_id = get_or_create_user(nickname)
    update_user_mmr(user_id, mmr)
    
    rank, subrank = get_rank_by_mmr(mmr)
    rank_emoji = get_rank_emoji(rank)
    
    await update.message.reply_text(
        f"✅ MMR успешно обновлен!\n"
        f"🎮 Текущий MMR: {mmr}\n"
        f"{rank_emoji} Ранг: {format_rank(rank, subrank)}"
    ) 