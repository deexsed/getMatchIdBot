"""
Утилиты для работы с рангами
"""

RANKS = {
    'Herald': (0, 720),
    'Guardian': (720, 1460),
    'Crusader': (1460, 2200),
    'Archon': (2200, 3000),
    'Legend': (3000, 3800),
    'Ancient': (3800, 4620),
    'Divine': (4620, 5420),
    'Immortal': (5420, 100000)
}

RANK_EMOJIS = {
    'Herald': '🔰',
    'Guardian': '🛡️',
    'Crusader': '⚔️',
    'Archon': '🏹',
    'Legend': '👑',
    'Ancient': '🏺',
    'Divine': '✨',
    'Immortal': '⚡'
}

def get_rank_info(mmr):
    """Получает информацию о ранге по MMR"""
    if mmr is None:
        return None
        
    for rank, (min_mmr, max_mmr) in RANKS.items():
        if min_mmr <= mmr < max_mmr:
            # Определяем медаль (1-5)
            rank_range = max_mmr - min_mmr
            progress = mmr - min_mmr
            
            # Вычисляем медаль (1-5)
            medal = min(5, max(1, int((progress / rank_range) * 5) + 1))
            
            # Процент до следующей медали
            medal_size = rank_range / 5  # Делим на 5 вместо 7
            medal_progress = ((progress % medal_size) / medal_size) * 100
            
            # Процент до следующего ранга
            next_rank_progress = (progress / rank_range) * 100
            
            # Определяем следующий ранг
            ranks = list(RANKS.keys())
            current_rank_index = ranks.index(rank)
            next_rank = ranks[current_rank_index + 1] if rank != 'Immortal' else None
            
            return {
                'rank': rank,
                'medal': medal,
                'medal_progress': medal_progress,
                'emoji': RANK_EMOJIS[rank],
                'next_rank': next_rank,
                'next_rank_progress': next_rank_progress,
                'mmr_to_next_medal': int(medal_size - (progress % medal_size)),
                'mmr_to_next_rank': max_mmr - mmr if rank != 'Immortal' else 0,
                'current_mmr_range': (min_mmr, max_mmr),
                'total_rank_mmr': rank_range
            }
    return None 