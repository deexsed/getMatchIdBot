"""
Сервис для работы с героями
"""
from database.connection import get_db
from database.models import get_or_create_user
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_all_heroes():
    """Получает список всех героев из базы данных"""
    with get_db() as db:
        heroes = db.execute('SELECT name, localized_name FROM heroes ORDER BY localized_name').fetchall()
        return [{'name': hero['name'], 'localized_name': hero['localized_name']} for hero in heroes]

def get_hero_by_name(name):
    """Получает информацию о герое по имени"""
    with get_db() as db:
        return db.execute('SELECT * FROM heroes WHERE name = ?', (name,)).fetchone()

def get_heroes_by_attribute(attr):
    """Получает список героев по основному атрибуту"""
    with get_db() as db:
        heroes = db.execute(
            'SELECT name FROM heroes WHERE primary_attr = ? ORDER BY name',
            (attr,)
        ).fetchall()
        return [hero['name'] for hero in heroes]

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
        
        # Инициализируем метрики производительности
        performance_metrics = {
            'consistency': 0,  # Стабильность результатов (1-5)
            'trend_score': 0,  # Оценка тренда (1-5)
            'experience': 0,   # Опыт на герое (1-5)
            'recent_performance': 0  # Недавние результаты (1-5)
        }
        
        # Обновленная оценка стабильности (1-5)
        winrate_variance = abs(recent_winrate - total_winrate)
        recent_games = len(recent_matches)
        
        if recent_games >= 5:
            if winrate_variance <= 5:
                if total_winrate >= 55:
                    performance_metrics['consistency'] = 5  # Отличная стабильность с высоким винрейтом
                elif total_winrate >= 50:
                    performance_metrics['consistency'] = 4  # Хорошая стабильность
                elif total_winrate >= 45:
                    performance_metrics['consistency'] = 3  # Средняя стабильность
                else:
                    performance_metrics['consistency'] = 2  # Стабильно низкие результаты
            elif winrate_variance <= 10:
                performance_metrics['consistency'] = 3
            elif winrate_variance <= 15:
                performance_metrics['consistency'] = 2
            else:
                performance_metrics['consistency'] = 1
            
            # Учитываем текущую серию
            if current_streak >= 3 and streak_type == 'lose':
                performance_metrics['consistency'] = max(1, performance_metrics['consistency'] - 2)
        else:
            performance_metrics['consistency'] = 1
            
        # Улучшенная оценка тренда (1-5)
        if total_games >= 5:
            if recent_winrate > total_winrate + 20:
                performance_metrics['trend_score'] = 5  # Значительный рост
                trend = 'растущий'
            elif recent_winrate > total_winrate + 10:
                performance_metrics['trend_score'] = 4  # Умеренный рост
                trend = 'растущий'
            elif recent_winrate > total_winrate + 5:
                performance_metrics['trend_score'] = 3  # Небольшой рост
                trend = 'растущий'
            elif recent_winrate < total_winrate - 15:
                performance_metrics['trend_score'] = 1  # Сильное падение
                trend = 'падающий'
            elif recent_winrate < total_winrate - 5:
                performance_metrics['trend_score'] = 2  # Умеренное падение
                trend = 'падающий'
            else:
                performance_metrics['trend_score'] = 3  # Стабильный тренд
                trend = 'стабильный'
        else:
            performance_metrics['trend_score'] = 3
            trend = 'недостаточно данных'
            
        # Более точная оценка опыта (1-5)
        if total_games >= 50:
            performance_metrics['experience'] = 5  # Эксперт
        elif total_games >= 30:
            performance_metrics['experience'] = 4  # Опытный
        elif total_games >= 20:
            performance_metrics['experience'] = 3  # Уверенный
        elif total_games >= 10:
            performance_metrics['experience'] = 2  # Начинающий
        else:
            performance_metrics['experience'] = 1  # Новичок
            
        # Улучшенная оценка недавних результатов (1-5)
        if month_stats['games'] >= 5:
            if month_winrate >= 70:
                performance_metrics['recent_performance'] = 5  # Превосходно
            elif month_winrate >= 60:
                performance_metrics['recent_performance'] = 4  # Очень хорошо
            elif month_winrate >= 50:
                performance_metrics['recent_performance'] = 3  # Хорошо
            elif month_winrate >= 40:
                performance_metrics['recent_performance'] = 2  # Удовлетворительно
            else:
                performance_metrics['recent_performance'] = 1  # Плохо
        else:
            performance_metrics['recent_performance'] = 1
        
        # Обновленное определение уровня комфорта
        total_score = sum(performance_metrics.values())
        max_score = 20  # Максимально возможный счет (4 метрики по 5 баллов)
        
        if total_games < 5:
            comfort_level = 'недостаточно игр'
        elif total_score >= max_score * 0.8:  # 16+ баллов
            comfort_level = 'высокий'
        elif total_score >= max_score * 0.6:  # 12+ баллов
            comfort_level = 'хороший'
        elif total_score >= max_score * 0.4:  # 8+ баллов
            comfort_level = 'средний'
        else:
            comfort_level = 'низкий'
        
        # Обновленный анализ сильных и слабых сторон
        strengths = []
        weaknesses = []
        
        # Анализ стабильности только при достаточном количестве игр
        if recent_games >= 5:
            if performance_metrics['consistency'] == 5:
                strengths.append("Отличная стабильность")
            elif performance_metrics['consistency'] == 4:
                strengths.append("Хорошая стабильность")
            elif performance_metrics['consistency'] == 3:
                strengths.append("Средняя стабильность")
            elif performance_metrics['consistency'] == 2:
                weaknesses.append("Стабильно низкие результаты")
        
        # Анализ винрейта с учетом опыта
        if total_games >= 10:
            if total_winrate >= 65:
                strengths.append("Исключительный винрейт")
            elif total_winrate >= 55:
                strengths.append("Хороший винрейт")
            elif total_winrate < 45:
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

# Константы для пагинации
HEROES_PER_PAGE = 21  # Кратно 3 для трех столбцов

def get_max_pages():
    """Получает максимальное количество страниц"""
    heroes_count = len(get_all_heroes())
    return (heroes_count + HEROES_PER_PAGE - 1) // HEROES_PER_PAGE 