import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# IS57 API Configuration
IS57_API_BASE_URL = "https://back.is57.ru"

# Bot Settings
# ID пользователя-администратора бота
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))
ALLOWED_USERS = []  # Список разрешенных пользователей (заполняется из файла)
ALLOWED_GROUPS = []  # Список разрешенных групп (заполняется из файла)

# Data Files
DATA_DIR = "data"
ALLOWED_USERS_FILE = os.path.join(DATA_DIR, "allowed_users.txt")
ALLOWED_GROUPS_FILE = os.path.join(DATA_DIR, "allowed_groups.txt")
API_TOKEN_FILE = os.path.join(DATA_DIR, "api_token.txt")
SELECTED_TASKS_FILE = os.path.join(DATA_DIR, "selected_tasks.json")

# IS57 API Data
SUBJECTS = [
    "биология",
    "география",
    "информатика",
    "история",
    "лингвистика",
    "литература",
    "математика",
    "мхк",
    "физика",
    "химия",
    "экономика",
    "игровая",
    "спортивная",
    "творческое задание",
    "английский язык",
]

BUILDINGS = [1, 3]

# Legal symbols for names (based on admin panel logic)
LEGAL_SYMBOLS = [" ", "-"]


def init_legal_symbols():
    """Инициализация разрешенных символов для имен команд и заданий"""
    symbols = LEGAL_SYMBOLS.copy()

    # Добавляем латинские буквы
    for i in range(ord("a"), ord("z") + 1):
        symbols.append(chr(i))
    for i in range(ord("A"), ord("Z") + 1):
        symbols.append(chr(i))

    # Добавляем цифры
    for i in range(ord("0"), ord("9") + 1):
        symbols.append(chr(i))

    # Добавляем кириллические буквы
    for i in range(ord("а"), ord("я") + 1):
        symbols.append(chr(i))
    for i in range(ord("А"), ord("Я") + 1):
        symbols.append(chr(i))

    return symbols


LEGAL_SYMBOLS = init_legal_symbols()
