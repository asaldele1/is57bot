import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import BOT_TOKEN
from handlers import routers
from api import api_client
from utils import auth_manager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска бота"""
    # Проверка токена бота
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен! Проверьте файл .env")
        return

    # Создание бота и диспетчера
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    # Регистрация роутеров
    for router in routers:
        dp.include_router(router)

    # Загрузка данных авторизации
    logger.info("Загрузка данных авторизации...")
    await auth_manager.load_data()

    # Информация о запуске
    try:
        bot_info = await bot.get_me()
        logger.info(
            f"Бот запущен: @{bot_info.username} ({bot_info.first_name})"
        )
        logger.info(f"ID бота: {bot_info.id}")

        # Информация о разрешениях
        allowed_users = auth_manager.get_allowed_users()
        allowed_groups = auth_manager.get_allowed_groups()
        api_token = auth_manager.get_api_token()

        logger.info(f"Разрешенных пользователей: {len(allowed_users)}")
        logger.info(f"Разрешенных групп: {len(allowed_groups)}")
        logger.info(
            f"API токен: {'установлен' if api_token else 'не установлен'}"
        )

    except Exception as e:
        logger.error(f"Ошибка при получении информации о боте: {e}")
        return

    try:
        # Запуск поллинга
        logger.info("Запуск поллинга...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске поллинга: {e}")
    finally:
        # Закрытие ресурсов
        logger.info("Завершение работы бота...")
        await api_client.close()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
