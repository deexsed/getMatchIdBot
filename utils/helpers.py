"""
Вспомогательные функции
"""
def get_user_nickname(user):
    """Получает никнейм пользователя"""
    return f"@{user.username}" if user.username else user.first_name

def calculate_streak(matches, nickname):
    """Подсчитывает текущую серию побед/поражений"""
    if not matches:
        return 0, 'none'
    
    streak = 0
    streak_type = matches[0]['outcome']
    
    for match in matches:
        if match['outcome'] == streak_type:
            streak += 1
        else:
            break
    
    return streak, streak_type 