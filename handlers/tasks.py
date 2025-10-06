from aiogram import Router, types
from aiogram.filters import Command
from utils import auth_required, auth_manager
from api import api_client
from config.settings import LEGAL_SYMBOLS, SUBJECTS
from utils.helpers import validate_name
import shlex

router = Router()


@router.message(Command("add_task"))
@auth_required()
async def cmd_add_task(message: types.Message):
    """Добавление нового задания"""
    try:
        args = shlex.split(message.text)[1:]
        if len(args) < 2:
            await message.answer(
                "❌ Использование: `/add_task <предмет> <название>`\n"
                f"Доступные предметы: {', '.join(SUBJECTS[:5])}...",
                parse_mode="Markdown",
            )
            return

        subject = args[0].lower()
        name = args[1].strip()

        # Проверка предмета
        if subject not in SUBJECTS:
            await message.answer(
                "❌ Неверный предмет. Используйте /subjects для просмотра списка."
            )
            return

        # Проверка имени
        if not validate_name(name, LEGAL_SYMBOLS):
            await message.answer(
                "❌ Название задания содержит недопустимые символы. "
                "Разрешены только буквы, цифры, пробелы и тире."
            )
            return

        # Проверка на дубликаты
        tasks = await api_client.get_tasks()
        for task in tasks:
            if task["name"] == name:
                await message.answer(
                    "❌ Задание с таким названием уже существует."
                )
                return

        # Добавление задания
        token = auth_manager.get_api_token()
        if not token:
            await message.answer(
                "❌ API токен не установлен. Обратитесь к администратору."
            )
            return

        success = await api_client.add_task(token, subject, name)
        if success:
            await message.answer(
                f"✅ Задание '{name}' по предмету '{subject}' добавлено!"
            )
        else:
            await message.answer(
                "❌ Ошибка при добавлении задания. Проверьте токен."
            )

    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении задания: {e}")


@router.message(Command("remove_task"))
@auth_required()
async def cmd_remove_task(message: types.Message):
    """Удаление задания"""
    try:
        args = shlex.split(message.text)[1:]
        if len(args) < 2:
            await message.answer(
                "❌ Использование: `/remove_task <предмет> <название>`",
                parse_mode="Markdown",
            )
            return

        subject = args[0].lower()
        name = args[1].strip()

        # Поиск задания
        tasks = await api_client.get_tasks()
        task = api_client.find_task_by_name_and_subject(tasks, name, subject)

        if not task:
            await message.answer("❌ Задание не найдено.")
            return

        # Удаление задания
        token = auth_manager.get_api_token()
        if not token:
            await message.answer(
                "❌ API токен не установлен. Обратитесь к администратору."
            )
            return

        success = await api_client.remove_task(token, task["id"])
        if success:
            await message.answer(f"✅ Задание '{name}' успешно удалено!")
        else:
            await message.answer(
                "❌ Ошибка при удалении задания. Проверьте токен."
            )

    except Exception as e:
        await message.answer(f"❌ Ошибка при удалении задания: {e}")


@router.message(Command("set_result"))
@auth_required()
async def cmd_set_result(message: types.Message):
    """Установка результата команды"""
    try:
        args = shlex.split(message.text)[1:]
        if len(args) < 4:
            await message.answer(
                "❌ Использование: `/set_result <команда> <предмет> <задание> <баллы>`",
                parse_mode="Markdown",
            )
            return

        team_name = args[0].strip()
        subject = args[1].lower()
        task_name = args[2].strip()
        points = int(args[3])

        # Получение данных
        teams = await api_client.get_teams()
        tasks = await api_client.get_tasks()

        # Поиск команды и задания
        team = api_client.find_team_by_name(teams, team_name)

        # Если точного совпадения нет — попробуем найти по префиксу (началу названия), нечувствительно к регистру
        if not team:
            lc = team_name.lower()
            prefix_matches = [t for t in teams if t.get(
                "name", "").lower().startswith(lc)]
            if len(prefix_matches) == 1:
                team = prefix_matches[0]
                team_name = team.get("name")
            elif len(prefix_matches) > 1:
                # Если несколько совпадений — попросим уточнить
                names = ", ".join(t.get("name") for t in prefix_matches[:10])
                await message.answer(
                    f"❌ Найдено несколько команд, начинающихся на '{team_name}': {names}. Пожалуйста, уточните название."
                )
                return
        task = api_client.find_task_by_name_and_subject(
            tasks, task_name, subject
        )

        if not team:
            await message.answer("❌ Команда не найдена.")
            return

        if not task:
            await message.answer("❌ Задание не найдено.")
            return

        # Установка результата
        token = auth_manager.get_api_token()
        if not token:
            await message.answer(
                "❌ API токен не установлен. Обратитесь к администратору."
            )
            return

        success = await api_client.set_result(
            token, team["id"], task["id"], points
        )
        if success:
            await message.answer(
                f"✅ Результат установлен!\n"
                f"Команда: {team_name}\n"
                f"Задание: {task_name} ({subject})\n"
                f"Баллы: {points}"
            )
        else:
            await message.answer(
                "❌ Ошибка при установке результата. Проверьте токен."
            )

    except ValueError:
        await message.answer("❌ Баллы должны быть числами.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при установке результата: {e}")
