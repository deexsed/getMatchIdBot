"""Базовые классы и функции для достижений"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    emoji: str
    category: str
    progress_max: Optional[int] = None  # Максимальное значение для прогресса
    hidden: bool = False  # Скрытые достижения
    requires: Optional[str] = None  # Зависимости от других достижений
    
    def format_progress(self, current: int) -> str:
        """Форматирует прогресс достижения"""
        if not self.progress_max:
            return ""
        return f" ({current}/{self.progress_max})"

class AchievementProgress:
    def __init__(self):
        self.progress: Dict[str, int] = {}  # Прогресс по каждому достижению
        self.unlocked_at: Dict[str, str] = {}  # Время получения достижения
    
    def update(self, achievement_id: str, value: int):
        """Обновляет прогресс достижения"""
        self.progress[achievement_id] = value
    
    def unlock(self, achievement_id: str, timestamp: str):
        """Отмечает достижение как полученное"""
        self.unlocked_at[achievement_id] = timestamp

class AchievementCategory:
    # Словарь с эмодзи для каждой категории
    CATEGORY_EMOJIS = {
        'Матчи': '🎮',
        'MMR': '📈',
        'Герои': '⚔️',
        'Винрейт': '🎯',
        'Особые': '✨'
    }

    def __init__(self, name, achievements):
        self.name = name
        self.emoji = self.CATEGORY_EMOJIS.get(name, '📋')  # Дефолтный эмодзи если категория не найдена
        self.achievements = achievements

    def check(self, stats: Dict[str, Any], mmr_data: Optional[Dict[str, Any]] = None) -> tuple[list[str], AchievementProgress]:
        """
        Проверяет достижения и возвращает список полученных достижений и их прогресс
        """
        return [], AchievementProgress()  # Базовая реализация всегда возвращает tuple

    def check_specific(self, stats: Dict[str, Any], mmr_data: Optional[Dict[str, Any]] = None) -> tuple[list[str], AchievementProgress]:
        """
        Проверяет достижения и возвращает список полученных достижений и их прогресс
        """
        return [], AchievementProgress()  # Реализация конкретного метода

    def check_alternative(self, stats: Dict[str, Any], mmr_data: Optional[Dict[str, Any]] = None) -> tuple[list[str], AchievementProgress]:
        """
        Проверяет достижения и возвращает список полученных достижений и их прогресс
        """
        return [], AchievementProgress()  # Реализация альтернативного метода

    def check_combined(self, stats: Dict[str, Any], mmr_data: Optional[Dict[str, Any]] = None) -> tuple[list[str], AchievementProgress]:
        """
        Проверяет достижения и возвращает список полученных достижений и их прогресс
        """
        return [], AchievementProgress()  # Реализация комбинированного метода 