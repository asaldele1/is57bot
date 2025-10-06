from aiogram import Router, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from api import api_client
from utils import (
    auth_required,
    format_team_info,
    format_task_info,
    split_long_message,
)
from config.settings import SUBJECTS, BUILDINGS

router = Router()


@router.message(Command("start"))
@auth_required()
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    welcome_text = """
🤖 Добро пожаловать в IS57 Bot!

Этот бот предоставляет доступ к API is57.ru для управления командами, \
заданиями и результатами.

📋 *Основные команды:*
/help - Показать все доступные команды
/teams - Получить список команд
/tasks - Получить список заданий
/results - Показать таблицу результатов

Для получения полного списка команд используйте /help
"""
    await message.answer(welcome_text, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("help"))
@auth_required()
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
*Основные правила:*
 • Названия команд указываются в следующем формате: "10В Гении".
 • При вводе результатов можно указывать только начало названия команды, \
например "10В" будет отсылать к команде "10В Гении".
 • Если в названии команды или задания есть пробелы, используйте кавычки, \
например: `/add\\_team 1 "Команда А"` или \
`/add\\_task математика "Линейная алгебра"`.


📋 *Доступные команды:*

*🔍 Просмотр данных:*
/teams - Получить список всех команд
/tasks - Получить список всех заданий
/results - Показать таблицу результатов

*👥 Команды для работы с командами:*
/add\\_team <здание - 1 или 3> <название> - Добавить новую команду
/remove\\_team <название> - Удалить команду

*📝 Команды для работы с заданиями:*
/add\\_task <предмет> <название> - Добавить новое задание
/remove\\_task <предмет> <название> - Удалить задание

*📊 Управление результатами:*
/set\\_result <команда> <предмет> <задание> <баллы> - Установить результат

*📚 Справочная информация:*
/subjects - Список доступных предметов
/buildings - Список доступных зданий

*Пример использования:*
`/add\\_team 1 "10В Гении"`
`/add\\_task математика "Линейная алгебра"`
`/set\\_result 10В математика "Линейная алгебра" 85`
"""

    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("teams"))
@auth_required()
async def cmd_teams(message: types.Message):
    """Обработчик команды /teams"""
    try:
        teams = await api_client.get_teams()

        if not teams:
            await message.answer("📭 Список команд пуст.")
            return

        # Сортировка как в админке
        teams.sort(key=lambda x: x["building"], reverse=True)

        teams_text = "👥 *Список команд:*\n\n"
        for team in teams:
            teams_text += format_team_info(team) + "\n"

        parts = split_long_message(teams_text)
        for part in parts:
            await message.answer(part, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        await message.answer(f"❌ Ошибка при получении списка команд: {e}")


@router.message(Command("tasks"))
@auth_required()
async def cmd_tasks(message: types.Message):
    """Обработчик команды /tasks"""
    try:
        tasks = await api_client.get_tasks()

        if not tasks:
            await message.answer("📭 Список заданий пуст.")
            return

        # Сортировка как в админке
        tasks.sort(key=lambda x: x["subject"])

        tasks_text = "📝 *Список заданий:*\n\n"
        for task in tasks:
            tasks_text += format_task_info(task) + "\n"

        parts = split_long_message(tasks_text)
        for part in parts:
            await message.answer(part, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        await message.answer(f"❌ Ошибка при получении списка заданий: {e}")


@router.message(Command("subjects"))
@auth_required()
async def cmd_subjects(message: types.Message):
    """Обработчик команды /subjects"""
    subjects_text = "📚 *Доступные предметы:*\n\n"
    for i, subject in enumerate(SUBJECTS, 1):
        subjects_text += f"{i}. {subject}\n"

    await message.answer(subjects_text, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("buildings"))
@auth_required()
async def cmd_buildings(message: types.Message):
    """Обработчик команды /buildings"""
    buildings_text = "🏢 *Доступные здания:*\n\n"
    for building in BUILDINGS:
        buildings_text += f"• Здание {building}\n"

    await message.answer(buildings_text, parse_mode=ParseMode.MARKDOWN)


@router.message(Command("results"))
@auth_required()
async def cmd_results(message: types.Message):
    """Обработчик команды /results"""
    try:
        # Получение всех данных
        teams = await api_client.get_teams()
        tasks = await api_client.get_tasks()
        results = await api_client.get_results()

        if not teams or not tasks:
            await message.answer("❌ Нет данных для отображения результатов.")
            return

        # Сортировка
        teams.sort(key=lambda x: x["building"], reverse=True)
        tasks.sort(key=lambda x: x["subject"])

        # Создание простого списка результатов
        results_text = "📊 *Результаты команд:*"
        for team in teams:
            results_text += (
                f"\n🏢 *{team['name']} (здание {team['building']}):*\n"
            )
            team_total = 0

            for task in tasks:
                result = api_client.get_team_result(
                    results, team["id"], task["id"]
                )
                if result > 0:
                    results_text += f"  • {task['subject']}: "
                    results_text += f"{task['name']} - {result} баллов\n"
                    team_total += result

            results_text += f"  *Итого: {team_total} баллов*\n"

        if not results_text.strip():
            await message.answer("📭 Нет результатов для отображения.")
        else:
            parts = split_long_message(results_text)
            for part in parts:
                await message.answer(part, parse_mode=ParseMode.MARKDOWN)

    except Exception as e:
        await message.answer(f"❌ Ошибка при получении результатов: {e}")
