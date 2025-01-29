"""
Модуль для импорта героев из OpenDota API
"""
import logging
import httpx
from database.connection import get_db

logger = logging.getLogger(__name__)

OPENDOTA_API_URL = "https://api.opendota.com/api/heroes"

async def import_heroes():
    """Импортирует героев из OpenDota API в базу данных"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OPENDOTA_API_URL)
            response.raise_for_status()
            heroes = response.json()

            with get_db() as db:
                # Очищаем таблицу героев перед обновлением
                db.execute('DELETE FROM heroes')
                
                # Добавляем новых героев
                for hero in heroes:
                    roles = ','.join(hero.get('roles', []))
                    role_levels = ','.join(map(str, hero.get('role_levels', [])))
                    
                    db.execute('''
                        INSERT INTO heroes (
                            id, name, localized_name, primary_attr, attack_type,
                            roles, base_str, base_agi, base_int, str_gain,
                            agi_gain, int_gain, base_health, base_mana,
                            base_armor, base_attack_min, base_attack_max,
                            base_movement_speed, role_levels, complexity
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        hero['id'],
                        hero['name'].replace('npc_dota_hero_', ''),
                        hero['localized_name'],
                        hero['primary_attr'],
                        hero.get('attack_type'),
                        roles,
                        hero.get('base_str'),
                        hero.get('base_agi'),
                        hero.get('base_int'),
                        hero.get('str_gain'),
                        hero.get('agi_gain'),
                        hero.get('int_gain'),
                        hero.get('base_health', 200),
                        hero.get('base_mana', 50),
                        hero.get('base_armor', 0),
                        hero.get('base_attack_min', 0),
                        hero.get('base_attack_max', 0),
                        hero.get('move_speed', 300),
                        role_levels,
                        hero.get('complexity', 1)
                    ))
                
                db.commit()
                logger.info(f"Успешно импортировано {len(heroes)} героев")
                
    except httpx.RequestError as e:
        logger.error(f"Ошибка при запросе к API: {e}")
        raise
    except Exception as e:
        logger.error(f"Ошибка при импорте героев: {e}")
        raise 