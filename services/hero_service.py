from database.connection import get_db
from database.models import get_or_create_user
import json
import logging
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_hero_prediction(telegram_nickname, hero):
    """Получает расширенный анализ героя"""
    with get_db() as db:
        user_id = get_or_create_user(telegram_nickname)
        
        # Общая статистика героя
        stats = db.execute('''
            SELECT games, wins
            FROM hero_stats
            WHERE user_id = ? AND hero = ?
        ''', (user_id, hero)).fetchone()
        
        if not stats or stats['games'] < 3:
            return {
                'status': 'недостаточно данных',
                'games': stats['games'] if stats else 0,
                'message': 'Недостаточно игр для анализа (нужно минимум 3)'
            }
        
        # Последние 10 матчей
        recent_matches = db.execute('''
            SELECT outcome, played_at
            FROM matches
            WHERE user_id = ? AND hero = ?
            ORDER BY played_at DESC LIMIT 10
        ''', (user_id, hero)).fetchall()
        
        # Статистика за последний месяц
        month_ago = datetime.now() - timedelta(days=30)
        month_stats = db.execute('''
            SELECT COUNT(*) as games,
                   SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins
            FROM matches
            WHERE user_id = ? AND hero = ? AND played_at >= ?
        ''', (user_id, hero, month_ago)).fetchone()
        
        # Текущая серия побед/поражений
        current_streak = 0
        streak_type = recent_matches[0]['outcome'] if recent_matches else None
        for match in recent_matches:
            if match['outcome'] == streak_type:
                current_streak += 1
            else:
                break
        
        # Лучшая серия побед
        best_streak = 0
        current_best = 0
        for match in recent_matches:
            if match['outcome'] == 'win':
                current_best += 1
                best_streak = max(best_streak, current_best)
            else:
                current_best = 0
        
        # Основные показатели
        total_games = stats['games']
        total_wins = stats['wins']
        total_winrate = (total_wins / total_games * 100)
        
        recent_wins = len([m for m in recent_matches if m['outcome'] == 'win'])
        recent_winrate = (recent_wins / len(recent_matches) * 100)
        
        month_winrate = (month_stats['wins'] / month_stats['games'] * 100) if month_stats['games'] > 0 else 0
        
        # Определяем тренд
        trend = 'стабильный'
        if recent_winrate > total_winrate + 10:
            trend = 'растущий'
        elif recent_winrate < total_winrate - 10:
            trend = 'падающий'
        
        # Рассчитываем различные показатели для оценки
        performance_metrics = {
            'consistency': 0,  # Стабильность результатов
            'trend_score': 0,  # Оценка тренда
            'experience': 0,   # Опыт на герое
            'recent_performance': 0  # Недавние результаты
        }
        
        # Оценка стабильности (на основе разброса винрейта)
        winrate_variance = abs(recent_winrate - total_winrate)
        if winrate_variance <= 5:
            performance_metrics['consistency'] = 3  # Высокая стабильность
        elif winrate_variance <= 15:
            performance_metrics['consistency'] = 2  # Средняя стабильность
        else:
            performance_metrics['consistency'] = 1  # Низкая стабильность
            
        # Оценка тренда
        if trend == 'растущий':
            performance_metrics['trend_score'] = 3
        elif trend == 'стабильный':
            performance_metrics['trend_score'] = 2
        else:
            performance_metrics['trend_score'] = 1
            
        # Оценка опыта
        if total_games >= 30:
            performance_metrics['experience'] = 3
        elif total_games >= 15:
            performance_metrics['experience'] = 2
        else:
            performance_metrics['experience'] = 1
            
        # Оценка недавних результатов
        if month_stats['games'] >= 5:
            if month_winrate >= 60:
                performance_metrics['recent_performance'] = 3
            elif month_winrate >= 50:
                performance_metrics['recent_performance'] = 2
            else:
                performance_metrics['recent_performance'] = 1
        
        # Общая оценка производительности (максимум 12 баллов)
        total_score = sum(performance_metrics.values())
        
        # Определяем уровень комфорта на основе комплексной оценки
        comfort_level = 'средний'  # По умолчанию средний
        
        if total_score >= 10 and total_winrate >= 55:
            comfort_level = 'высокий'
        elif total_score >= 8 and total_winrate >= 50:
            comfort_level = 'хороший'
        elif total_games < 10 and total_winrate >= 60:
            comfort_level = 'перспективный'
        elif total_score <= 6 and total_games >= 10:
            comfort_level = 'низкий'
        
        # Определяем сильные и слабые стороны
        strengths = []
        weaknesses = []
        
        # Анализ стабильности
        if performance_metrics['consistency'] == 3:
            strengths.append("Стабильные результаты")
        elif performance_metrics['consistency'] == 1:
            weaknesses.append("Нестабильные результаты")
        
        # Анализ винрейта с учетом опыта
        if total_winrate >= 70:
            strengths.append("Исключительный винрейт")
        elif total_winrate >= 60:
            strengths.append("Высокий винрейт")
        elif total_winrate < 45 and total_games >= 10:
            weaknesses.append("Низкий винрейт")
        
        # Анализ серий с контекстом
        if best_streak >= 5:
            strengths.append(f"Впечатляющая серия побед: {best_streak}")
        elif best_streak >= 3:
            strengths.append(f"Хорошая серия побед: {best_streak}")
        
        if current_streak >= 3:
            if streak_type == 'win':
                strengths.append(f"Текущая серия побед: {current_streak}")
            else:
                weaknesses.append(f"Текущая серия поражений: {current_streak}")
        
        # Анализ недавних результатов с учетом количества игр
        if month_stats['games'] >= 5:
            if month_winrate >= 65:
                strengths.append("Отличные результаты в последнее время")
            elif month_winrate >= 55:
                strengths.append("Стабильные результаты в последнее время")
            elif month_winrate < 45:
                weaknesses.append("Слабые результаты в последнее время")
        
        # Анализ опыта и его эффективности
        if total_games >= 30:
            if total_winrate >= 55:
                strengths.append("Большой успешный опыт игры на герое")
            else:
                strengths.append("Большой опыт игры на герое")
        elif total_games <= 5:
            if total_winrate >= 60:
                strengths.append("Многообещающие первые результаты")
            elif total_winrate < 50:
                weaknesses.append("Недостаточно опыта")
        
        # Анализ тренда с контекстом
        if trend == 'растущий' and total_games >= 10:
            strengths.append("Стабильное улучшение результатов")
        elif trend == 'падающий' and total_games >= 10:
            weaknesses.append("Ухудшение результатов")

        # Добавим анализ динамики по периодам
        periods = {
            'week': datetime.now() - timedelta(days=7),
            'month': datetime.now() - timedelta(days=30),
            'quarter': datetime.now() - timedelta(days=90)
        }
        
        period_stats = {}
        for period_name, period_start in periods.items():
            stats = db.execute('''
                SELECT COUNT(*) as games,
                       SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins
                FROM matches
                WHERE user_id = ? AND hero = ? AND played_at >= ?
            ''', (user_id, hero, period_start)).fetchone()
            
            if stats['games'] > 0:
                period_stats[period_name] = {
                    'games': stats['games'],
                    'winrate': (stats['wins'] / stats['games'] * 100)
                }

        # Анализ времени суток
        time_stats = db.execute('''
            SELECT 
                CASE 
                    WHEN strftime('%H', played_at) BETWEEN '06' AND '11' THEN 'утро'
                    WHEN strftime('%H', played_at) BETWEEN '12' AND '17' THEN 'день'
                    WHEN strftime('%H', played_at) BETWEEN '18' AND '23' THEN 'вечер'
                    ELSE 'ночь'
                END as time_of_day,
                COUNT(*) as games,
                SUM(CASE WHEN outcome = 'win' THEN 1 ELSE 0 END) as wins
            FROM matches
            WHERE user_id = ? AND hero = ?
            GROUP BY time_of_day
            HAVING games >= 3
        ''', (user_id, hero)).fetchall()

        best_time = None
        best_time_winrate = 0
        for time in time_stats:
            winrate = (time['wins'] / time['games'] * 100)
            if winrate > best_time_winrate:
                best_time_winrate = winrate
                best_time = time['time_of_day']

        return {
            'status': 'успешно',
            'games': total_games,
            'winrate': total_winrate,
            'recent_winrate': recent_winrate,
            'month_games': month_stats['games'],
            'month_winrate': month_winrate,
            'current_streak': current_streak,
            'streak_type': streak_type,
            'best_streak': best_streak,
            'trend': trend,
            'comfort_level': comfort_level,
            'performance_metrics': performance_metrics,
            'total_score': total_score,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'period_stats': period_stats,
            'best_time': best_time,
            'best_time_winrate': best_time_winrate if best_time else 0
        }

def get_user_heroes(telegram_nickname):
    """Получает список героев пользователя"""
    with get_db() as db:
        user_id = get_or_create_user(telegram_nickname)
        heroes = db.execute(
            'SELECT DISTINCT hero FROM matches WHERE user_id = ? ORDER BY hero',
            (user_id,)
        ).fetchall()
        return [h['hero'] for h in heroes]

def load_heroes(filename='data/heroes.json'):
    """Загружает список героев из JSON файла"""
    try:
        # Получаем абсолютный путь к файлу относительно корня проекта
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, filename)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data['heroes']
    except FileNotFoundError:
        logger.error(f"Ошибка: Файл {filename} не найден")
        return []
    except json.JSONDecodeError:
        logger.error(f"Ошибка: Файл {filename} содержит некорректный JSON")
        return []
    except KeyError:
        logger.error(f"Ошибка: В файле {filename} отсутствует ключ 'heroes'")
        return []

# Загружаем список героев при импорте модуля
HEROES = load_heroes()
HEROES_PER_PAGE = 21  # Кратно 3 для трех столбцов
MAX_PAGES = len(HEROES) // HEROES_PER_PAGE + (1 if len(HEROES) % HEROES_PER_PAGE > 0 else 0) 