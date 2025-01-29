"""
Текстовые сообщения бота
"""
def get_hero_prediction_text(hero, prediction):
    """Формирует текст анализа героя"""
    if prediction['status'] == 'недостаточно данных':
        return (
            f"❗ *Анализ героя {hero}:*\n"
            f"{prediction['message']}\n"
            f"Сыграно игр: {prediction['games']}"
        )

    trend_emoji = {
        'растущий': '📈',
        'падающий': '📉',
        'стабильный': '➡️'
    }
    
    comfort_emoji = {
        'высокий': '🟢',
        'хороший': '🟦',
        'средний': '🟡',
        'перспективный': '⭐',
        'низкий': '🔴'
    }
    
    # Формируем основной текст
    text = (
        f"🎯 *Анализ героя {hero}:*\n\n"
        f"*Общая статистика:*\n"
        f"• Всего игр: {prediction['games']}\n"
        f"• Общий винрейт: {prediction['winrate']:.1f}%\n"
        f"• Недавний винрейт: {prediction['recent_winrate']:.1f}%\n"
        f"• За месяц: {prediction['month_games']} игр, {prediction['month_winrate']:.1f}%\n\n"
        f"*Оценка показателей:*\n"
        f"• Стабильность: {'⭐' * prediction['performance_metrics']['consistency']}\n"
        f"• Тренд: {'⭐' * prediction['performance_metrics']['trend_score']}\n"
        f"• Опыт: {'⭐' * prediction['performance_metrics']['experience']}\n"
        f"• Текущая форма: {'⭐' * prediction['performance_metrics']['recent_performance']}\n"
        f"• Общая оценка: {prediction['total_score']}/20\n\n"
    )
    
    # Добавляем информацию о серии
    if prediction['current_streak'] >= 2:
        streak_type = "побед" if prediction['streak_type'] == 'win' else "поражений"
        text += f"*Текущая серия {streak_type}:* {prediction['current_streak']}\n"
    if prediction['best_streak'] >= 3:
        text += f"*Лучшая серия побед:* {prediction['best_streak']}\n"
    text += "\n"
    
    # Добавляем тренд и уровень комфорта
    text += (
        f"*Тренд:* {trend_emoji[prediction['trend']]} {prediction['trend']}\n"
        f"*Уровень комфорта:* {comfort_emoji[prediction['comfort_level']]} {prediction['comfort_level']}\n\n"
    )
    
    # Добавляем сильные и слабые стороны
    if prediction['strengths']:
        text += "*Сильные стороны:*\n"
        for strength in prediction['strengths']:
            text += f"✅ {strength}\n"
        text += "\n"
    
    if prediction['weaknesses']:
        text += "*Слабые стороны:*\n"
        for weakness in prediction['weaknesses']:
            text += f"❌ {weakness}\n"
        text += "\n"
    
    # Добавляем статистику по периодам
    if prediction.get('period_stats'):
        text += "*Статистика по периодам:*\n"
        period_names = {
            'week': 'За неделю',
            'month': 'За месяц',
            'quarter': 'За квартал'
        }
        for period, stats in prediction['period_stats'].items():
            text += f"• {period_names[period]}: {stats['games']} игр, {stats['winrate']:.1f}% винрейт\n"
        text += "\n"

    # Добавляем лучшее время для игры
    if prediction.get('best_time'):
        text += f"*Лучшее время для игры:* {prediction['best_time']} ({prediction['best_time_winrate']:.1f}% винрейт)\n\n"

    # Улучшаем рекомендации
    recommendations = {
        'высокий': {
            'text': (
                "Отличный выбор! У вас хорошо получается играть на этом герое. "
                "Продолжайте совершенствовать свое мастерство."
            ),
            'tips': [
                "Попробуйте новые сборки и тактики",
                "Поделитесь опытом с другими игроками",
                "Изучите продвинутые механики героя"
            ]
        },
        'хороший': {
            'text': (
                "Вы уверенно играете на этом герое. "
                "Есть потенциал для дальнейшего роста."
            ),
            'tips': [
                "Обратите внимание на тайминги способностей",
                "Изучите сложные комбинации",
                "Поэкспериментируйте с разными стилями игры"
            ]
        },
        'перспективный': {
            'text': (
                "Многообещающие результаты! Стоит продолжать играть на этом герое "
                "и набираться опыта."
            ),
            'tips': [
                "Сосредоточьтесь на базовых механиках",
                "Изучите популярные сборки",
                "Посмотрите гайды по герою"
            ]
        },
        'средний': {
            'text': (
                "У вас есть хороший потенциал на этом герое. "
                "Попробуйте проанализировать успешные игры и понять, что работает лучше всего."
            ),
            'tips': [
                "Определите свои сильные стороны",
                "Работайте над слабыми местами",
                "Изучите контрпики и синергии"
            ]
        },
        'низкий': {
            'text': (
                "Возможно, стоит пересмотреть свой подход к игре на этом герое. "
                "Попробуйте изучить новые тактики или посмотреть реплеи успешных игроков."
            ),
            'tips': [
                "Начните с базовых механик",
                "Посмотрите обучающие видео",
                "Тренируйтесь в безопасных условиях"
            ]
        }
    }

    rec = recommendations[prediction['comfort_level']]
    text += f"📝 *Рекомендация:* {rec['text']}\n\n"
    text += "*Советы по улучшению:*\n"
    for tip in rec['tips']:
        text += f"• {tip}\n"
    text += "\n"

    return text

def get_stats_text(stats_data):
    """Формирует текст статистики"""
    total_games = stats_data['total_games']
    wins = stats_data['total_wins']
    losses = total_games - wins
    winrate = (wins / total_games) * 100
    
    # Основная статистика
    stats_text = (
        f"📊 *Общая статистика:*\n"
        f"• Всего игр: {total_games}\n"
        f"• Победы/Поражения: {wins}W/{losses}L\n"
        f"• Винрейт: {winrate:.1f}%\n"
    )
    
    # Добавляем тренд
    if total_games >= 10:
        recent_games = min(10, total_games)
        recent_text = f"\n📈 *Последние {recent_games} игр:*\n"
        recent_wins = sum(1 for hero in stats_data['heroes'][:recent_games] if hero['wins'] > 0)
        recent_winrate = (recent_wins / recent_games) * 100
        trend = "↗️" if recent_winrate > winrate else "↘️" if recent_winrate < winrate else "➡️"
        
        recent_text += (
            f"• Винрейт: {recent_winrate:.1f}% {trend}\n"
            f"• Результат: {recent_wins}W/{recent_games - recent_wins}L\n"
        )
        stats_text += recent_text
    
    # Лучшие герои
    if stats_data['heroes']:
        stats_text += "\n🏆 *Лучшие герои:*\n"
        # Сортируем героев по винрейту (минимум 3 игры)
        best_heroes = [h for h in stats_data['heroes'] if h['games'] >= 3]
        best_heroes.sort(key=lambda x: (x['winrate'], x['games']), reverse=True)
        
        for hero in best_heroes[:3]:
            winrate_emoji = "🟢" if hero['winrate'] >= 60 else "🟡" if hero['winrate'] >= 50 else "🔴"
            stats_text += (
                f"• {hero['hero']}: {winrate_emoji} "
                f"{hero['winrate']:.1f}% ({hero['wins']}W/{hero['games'] - hero['wins']}L)\n"
            )
    
    # Наиболее играемые герои
    if stats_data['heroes']:
        stats_text += "\n👾 *Самые играемые герои:*\n"
        most_played = sorted(stats_data['heroes'], key=lambda x: x['games'], reverse=True)
        
        for hero in most_played[:3]:
            games_emoji = "🌟" if hero['games'] >= 20 else "⭐" if hero['games'] >= 10 else "✨"
            stats_text += (
                f"• {hero['hero']}: {games_emoji} "
                f"{hero['games']} игр ({hero['winrate']:.1f}%)\n"
            )
    
    # Текущая серия
    current_streak = 0
    streak_type = None
    for hero in stats_data['heroes']:
        if hero['wins'] > 0:
            if streak_type is None or streak_type == 'win':
                streak_type = 'win'
                current_streak += 1
        else:
            if streak_type is None or streak_type == 'lose':
                streak_type = 'lose'
                current_streak += 1
            else:
                break
    
    if current_streak >= 2:
        streak_emoji = "🔥" if streak_type == 'win' else "❄️"
        streak_text = "побед" if streak_type == 'win' else "поражений"
        stats_text += f"\n{streak_emoji} *Текущая серия {streak_text}:* {current_streak}\n"
    
    return stats_text

def get_matches_text(matches):
    """Формирует текст последних матчей"""
    matches_text = "🎮 Ваши последние матчи:\n\n"
    for match in matches:
        outcome_emoji = "✅" if match['outcome'] == 'win' else "❌"
        matches_text += (
            f"{match['played_at']}\n"
            f"Герой: {match['hero']}\n"
            f"Исход: {outcome_emoji}\n"
            f"ID матча: {match['match_id']}\n\n"
        )
    return matches_text

def format_hero_prediction(data):
    """Форматирует предсказание для героя"""
    if data['status'] == 'недостаточно данных':
        return f"⚠️ {data['message']}\nСыграно игр: {data['games']}"
    
    # Эмодзи для оценок
    star_emojis = {
        1: "⭐",
        2: "⭐⭐",
        3: "⭐⭐⭐",
        4: "⭐⭐⭐⭐",
        5: "⭐⭐⭐⭐⭐"
    }
    
    metrics = data['performance_metrics']
    max_score = 20  # Максимально возможный счет (4 метрики по 5 баллов)
    
    message = [
        f"🎯 Анализ героя {data['hero_name']}:",
        "",
        "Общая статистика:",
        f"• Всего игр: {data['games']}",
        f"• Общий винрейт: {data['winrate']:.1f}%",
        f"• Недавний винрейт: {data['recent_winrate']:.1f}%",
        f"• За месяц: {data['month_games']} игр, {data['month_winrate']:.1f}%",
        "",
        "Оценка показателей:",
        f"• Стабильность: {star_emojis[metrics['consistency']]}",
        f"• Тренд: {star_emojis[metrics['trend_score']]}",
        f"• Опыт: {star_emojis[metrics['experience']]}",
        f"• Текущая форма: {star_emojis[metrics['recent_performance']]}",
        f"• Общая оценка: {data['total_score']}/{max_score}"
    ]
    
    # ... остальной код без изменений ... 