from aiogram import Router, types
from aiogram.filters import Command
from utils import auth_required, auth_manager
from api import api_client
from config.settings import LEGAL_SYMBOLS, BUILDINGS
from utils.helpers import validate_name
import shlex

router = Router()


@router.message(Command("set_token"))
@auth_required(admin_only=True)
async def cmd_set_token(message: types.Message):
    """Установка API токена (только для админа)"""
    try:
        args = message.text.split()[1:]
        if not args:
            await message.answer(
                "❌ Укажите токен: `/set_token <токен>`", parse_mode="Markdown"
            )
            return

        token = args[0]
        await auth_manager.save_api_token(token)
        await message.answer("✅ API токен успешно сохранен!")

    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении токена: {e}")


@router.message(Command("add_user"))
@auth_required(admin_only=True)
async def cmd_add_user(message: types.Message):
    """Добавление разрешенного пользователя (только для админа)"""
    try:
        args = message.text.split()[1:]
        if not args:
            await message.answer(
                "❌ Укажите ID пользователя: `/add_user <user_id>`",
                parse_mode="Markdown",
            )
            return

        user_id = int(args[0])
        await auth_manager.add_user(user_id)
        await message.answer(
            f"✅ Пользователь {user_id} добавлен в разрешенные!"
        )

    except ValueError:
        await message.answer("❌ ID пользователя должен быть числом.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении пользователя: {e}")


@router.message(Command("remove_user"))
@auth_required(admin_only=True)
async def cmd_remove_user(message: types.Message):
    """Удаление пользователя из разрешенных (только для админа)"""
    try:
        args = message.text.split()[1:]
        if not args:
            await message.answer(
                "❌ Укажите ID пользователя: `/remove_user <user_id>`",
                parse_mode="Markdown",
            )
            return

        user_id = int(args[0])
        await auth_manager.remove_user(user_id)
        await message.answer(
            f"✅ Пользователь {user_id} удален из разрешенных!"
        )

    except ValueError:
        await message.answer("❌ ID пользователя должен быть числом.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при удалении пользователя: {e}")


@router.message(Command("add_group"))
@auth_required(admin_only=True)
async def cmd_add_group(message: types.Message):
    """Добавление группы в разрешенные (только для админа)"""
    try:
        chat_id = message.chat.id
        if chat_id > 0:
            await message.answer("❌ Эта команда работает только в группах.")
            return

        await auth_manager.add_group(chat_id)
        await message.answer("✅ Эта группа добавлена в разрешенные!")

    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении группы: {e}")


@router.message(Command("remove_group"))
@auth_required(admin_only=True)
async def cmd_remove_group(message: types.Message):
    """Удаление группы из разрешенных (только для админа)"""
    try:
        chat_id = message.chat.id
        if chat_id > 0:
            await message.answer("❌ Эта команда работает только в группах.")
            return

        await auth_manager.remove_group(chat_id)
        await message.answer("✅ Эта группа удалена из разрешенных!")

    except Exception as e:
        await message.answer(f"❌ Ошибка при удалении группы: {e}")


@router.message(Command("status"))
@auth_required(admin_only=True)
async def cmd_status(message: types.Message):
    """Показать статус бота (только для админа)"""
    try:
        allowed_users = auth_manager.get_allowed_users()
        allowed_groups = auth_manager.get_allowed_groups()
        api_token = auth_manager.get_api_token()

        status_text = f"""
🤖 **Статус бота:**

**API токен:** {'✅ Установлен' if api_token else '❌ Не установлен'}

**Разрешенные пользователи:** {len(allowed_users)}
{', '.join(str(uid) for uid in allowed_users[:10]) if allowed_users else 'Нет'}

**Разрешенные группы:** {len(allowed_groups)}
{', '.join(str(gid) for gid in allowed_groups[:10]) if allowed_groups else 'Нет'}

**Администратор:** {message.from_user.id}
"""

        await message.answer(status_text, parse_mode="Markdown")

    except Exception as e:
        await message.answer(f"❌ Ошибка при получении статуса: {e}")


@router.message(Command("add_team"))
@auth_required()
async def cmd_add_team(message: types.Message):
    """Добавление новой команды"""
    try:
        args = shlex.split(message.text)[1:]
        if len(args) < 2:
            await message.answer(
                "❌ Использование: `/add_team <здание> <название>`\n"
                f"Доступные здания: {', '.join(map(str, BUILDINGS))}",
                parse_mode="Markdown",
            )
            return

        building = int(args[0])
        name = args[1].strip()

        # Проверка здания
        if building not in BUILDINGS:
            await message.answer(
                f"❌ Неверный здание. Доступные: {', '.join(map(str, BUILDINGS))}"
            )
            return

        # Проверка имени
        if not validate_name(name, LEGAL_SYMBOLS):
            await message.answer(
                "❌ Название команды содержит недопустимые символы. "
                "Разрешены только буквы, цифры, пробелы и тире."
            )
            return

        # Проверка на дубликаты
        teams = await api_client.get_teams()
        for team in teams:
            if team["name"] == name:
                await message.answer(
                    "❌ Команда с таким названием уже существует."
                )
                return

        # Добавление команды
        token = auth_manager.get_api_token()
        if not token:
            await message.answer(
                "❌ API токен не установлен. Обратитесь к администратору."
            )
            return

        success = await api_client.add_team(token, building, name)
        if success:
            await message.answer(
                f"✅ Команда '{name}' (здание {building}) успешно добавлена!"
            )
        else:
            await message.answer(
                "❌ Ошибка при добавлении команды. Проверьте токен."
            )

    except ValueError:
        await message.answer("❌ Номер здания должен быть числом.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении команды: {e}")


@router.message(Command("remove_team"))
@auth_required()
async def cmd_remove_team(message: types.Message):
    """Удаление команды"""
    try:
        args = shlex.split(message.text)[1:]
        if len(args) < 1:
            await message.answer(
                "❌ Использование: `/remove_team <название>`",
                parse_mode="Markdown",
            )
            return

        name = args[0].strip()

        # Поиск команды
        teams = await api_client.get_teams()
        team = api_client.find_team_by_name(teams, name)

        if not team:
            await message.answer("❌ Команда не найдена.")
            return

        # Удаление команды
        token = auth_manager.get_api_token()
        if not token:
            await message.answer(
                "❌ API токен не установлен. Обратитесь к администратору."
            )
            return

        success = await api_client.remove_team(token, team["id"])
        if success:
            await message.answer(f"✅ Команда '{name}' успешно удалена!")
        else:
            await message.answer(
                "❌ Ошибка при удалении команды. Проверьте токен."
            )

    except ValueError:
        await message.answer("❌ Номер здания должен быть числом.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при удалении команды: {e}")
