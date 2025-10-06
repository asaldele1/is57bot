import logging
from functools import wraps
from aiogram import types
from utils.auth import auth_manager

logger = logging.getLogger(__name__)


def auth_required(admin_only: bool = False):
    """
    Декоратор для проверки авторизации пользователя

    Args:
        admin_only: Если True, разрешает доступ только админу
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(message: types.Message, *args, **kwargs):
            user_id = message.from_user.id
            chat_id = message.chat.id

            # Проверка только для админа
            if admin_only:
                if not auth_manager.is_admin(user_id):
                    await message.reply(
                        "❌ Эта команда доступна только администратору бота."
                    )
                    return
            # Обычная проверка авторизации
            elif not auth_manager.can_use_bot(user_id, chat_id):
                await message.reply(
                    "❌ У вас нет доступа к этому боту. "
                    "Обратитесь к администратору для получения разрешения."
                )
                return

            return await func(message, *args, **kwargs)

        return wrapper

    return decorator


def format_team_info(team: dict) -> str:
    """Форматирование информации о команде"""
    return f"🏢 {team['name']} (здание {team['building']}) - ID: {team['id']}"


def format_task_info(task: dict) -> str:
    """Форматирование информации о задании"""
    return f"📝 {task['name']} ({task['subject']}) - ID: {task['id']}"


def format_results_table(teams: list, tasks: list, results: dict) -> str:
    """Форматирование таблицы результатов для отправки в Telegram"""
    if not teams or not tasks:
        return "❌ Нет данных для отображения таблицы результатов."

    # Заголовок таблицы
    table = "📊 *Таблица результатов*\n"

    # Сортировка команд и заданий как в админке
    teams_sorted = sorted(teams, key=lambda x: x["building"], reverse=True)
    tasks_sorted = sorted(tasks, key=lambda x: x["subject"])

    # Создание таблицы
    # Заголовок с названиями команд
    table += "| Задание | "
    for team in teams_sorted:
        table += f"{team['name'][:8]} | "
    table += "\n"

    # Разделитель
    table += "|" + "-" * 10 + "|"
    for _ in teams_sorted:
        table += "-" * 10 + "|"
    table += "\n"

    # Строки с результатами
    for task in tasks_sorted:
        task_name = f"{task['name'][:8]}"
        table += f"| {task_name} | "

        for team in teams_sorted:
            result = get_team_task_result(results, team["id"], task["id"])
            result_str = str(result) if result > 0 else " "
            table += f"{result_str:>8} | "
        table += "\n"

    return f"```\n{table}\n```"


def get_team_task_result(results: dict, team_id: int, task_id: int) -> int:
    """Получение результата команды для задания"""
    if str(team_id) in results:
        team_results = results[str(team_id)].get("results", [])
        for result in team_results:
            if result.get("taskInfo", {}).get("id") == task_id:
                return result.get("result", 0)
    return 0


def validate_name(name: str, legal_symbols: list) -> bool:
    """Проверка имени на соответствие разрешенным символам"""
    name = name.strip()
    if not name:
        return False

    for char in name:
        if char not in legal_symbols:
            return False

    return True


def split_long_message(text: str, max_length: int = 4000) -> list:
    """Разделение длинного сообщения на части"""
    if len(text) <= max_length:
        return [text]

    parts = []
    current_part = ""

    for line in text.split("\n"):
        if len(current_part + line + "\n") <= max_length:
            current_part += line + "\n"
        else:
            if current_part:
                parts.append(current_part.rstrip())
                current_part = line + "\n"
            else:
                # Если даже одна строка слишком длинная
                parts.append(line[:max_length])
                current_part = (
                    line[max_length:] + "\n" if len(line) > max_length else ""
                )

    if current_part:
        parts.append(current_part.rstrip())

    return parts
