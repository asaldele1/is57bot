from aiogram import Router, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from utils import auth_required, auth_manager
from api import api_client
from config.settings import LEGAL_SYMBOLS, SUBJECTS
from utils.helpers import validate_name
from utils.selection import selection_manager
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
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        subject = args[0].lower()
        name = args[1].strip()

        # Проверка предмета
        if subject not in SUBJECTS:
            await message.answer("❌ Неверный предмет. Используйте /subjects.")
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
            if task["name"] == name and task["subject"] == subject:
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
                parse_mode=ParseMode.MARKDOWN,
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


@router.message(Command("choose_task"))
@auth_required()
async def cmd_choose_task(message: types.Message):
    """Выбрать задание для последующего использования в /set_result"""
    try:
        args = shlex.split(message.text)[1:]
        if len(args) < 2:
            await message.answer(
                "❌ Использование: `/choose_task <предмет> <название>`",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        subject = args[0].lower()
        name = args[1].strip()

        tasks = await api_client.get_tasks()
        task = api_client.find_task_by_name_and_subject(tasks, name, subject)

        if not task:
            await message.answer("❌ Задание не найдено.")
            return

        selection_manager.set_selection(message.from_user.id, task)
        await message.answer(
            "✅ Вы выбрали задание: "
            f"{task['name']} ({task['subject']}). "
            "Теперь можно использовать `/set_result <команда> <баллы>`",
            parse_mode=ParseMode.MARKDOWN
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка при выборе задания: {e}")


@router.message(Command("clear_choice"))
@auth_required()
async def cmd_clear_choice(message: types.Message):
    """Очистить выбранное задание пользователя"""
    try:
        selection_manager.clear_selection(message.from_user.id)
        await message.answer("✅ Выбор задания очищен.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при очистке выбора: {e}")


@router.message(Command("s"))
@router.message(Command("set_result"))
@auth_required()
async def cmd_set_result(message: types.Message):
    """Установка результата команды"""
    try:
        args = shlex.split(message.text)[1:]
        # expected usages:
        # /set_result <team> <subject> <task> <points>
        # /set_result <team> <points>  (uses user's selected task)
        if len(args) < 2:
            await message.answer(
                "❌ Использование: `/set_result <команда> <предмет> <задание> "
                "<баллы>`\n"
                "или: `/set_result <команда> <баллы>` если вы ранее выбрали "
                "задание через /choose_task",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        team_name = args[0].strip()

        # Если передано только 2 аргумента — предполагаем, что второй это баллы
        if len(args) == 2:
            # попробуем получить выбранное задание пользователя
            sel = selection_manager.get_selection(message.from_user.id)
            if not sel:
                await message.answer(
                    "❌ Вы не указали предмет/задание и не выбрали задание."
                    " Используйте: `/set_result <команда> <предмет> <задание>`"
                    " или выберите задание через /choose_task",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return

            subject = sel.get("subject")
            task_name = sel.get("name")
            try:
                points = int(args[1])
            except ValueError:
                await message.answer("❌ Баллы должны быть числами.")
                return
        else:
            subject = args[1].lower()
            task_name = args[2].strip()
            try:
                points = int(args[3])
            except (IndexError, ValueError):
                await message.answer("❌ Баллы должны быть числами.")
                return

        # Получение данных
        teams = await api_client.get_teams()
        tasks = await api_client.get_tasks()

        # Поиск команды и задания
        team = api_client.find_team_by_name(teams, team_name)

        # Если точного совпадения нет — попробуем найти по префиксу
        # (началу названия), нечувствительно к регистру
        if not team:
            lc = team_name.lower()
            prefix_matches = [
                t for t in teams if t.get("name", "").lower().startswith(lc)
            ]
            if len(prefix_matches) == 1:
                team = prefix_matches[0]
                team_name = team.get("name")
            elif len(prefix_matches) > 1:
                # Если несколько совпадений — попросим уточнить
                names = ", ".join(t.get("name") for t in prefix_matches[:10])
                await message.answer(
                    "❌ Найдено несколько команд, начинающихся на '"
                    f"{team_name}': {names}. Пожалуйста, уточните название."
                )
                return
        task = api_client.find_task_by_name_and_subject(
            tasks, task_name, subject
        )

        # Если задание не найдено — сообщим об этом
        if not task:
            await message.answer("❌ Задание не найдено.")
            return

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
