import os
from typing import List, Set
from config.settings import (
    ADMIN_USER_ID,
    ALLOWED_USERS_FILE,
    ALLOWED_GROUPS_FILE,
    API_TOKEN_FILE,
    DATA_DIR,
)


class AuthManager:
    """Менеджер авторизации для управления доступом к боту"""

    def __init__(self):
        self.allowed_users: Set[int] = set()
        self.allowed_groups: Set[int] = set()
        self.api_token: str = ""
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Создание директории для данных если она не существует"""
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

    async def load_data(self):
        """Загрузка данных авторизации из файлов"""
        await self._load_allowed_users()
        await self._load_allowed_groups()
        await self._load_api_token()

    async def _load_allowed_users(self):
        """Загрузка списка разрешенных пользователей"""
        try:
            if os.path.exists(ALLOWED_USERS_FILE):
                with open(ALLOWED_USERS_FILE, "r") as f:
                    user_ids = f.read().strip().split("\n")
                    self.allowed_users = {
                        int(uid) for uid in user_ids if uid.strip()
                    }
        except Exception as e:
            print(f"Ошибка загрузки разрешенных пользователей: {e}")

    async def _load_allowed_groups(self):
        """Загрузка списка разрешенных групп"""
        try:
            if os.path.exists(ALLOWED_GROUPS_FILE):
                with open(ALLOWED_GROUPS_FILE, "r") as f:
                    group_ids = f.read().strip().split("\n")
                    self.allowed_groups = {
                        int(gid) for gid in group_ids if gid.strip()
                    }
        except Exception as e:
            print(f"Ошибка загрузки разрешенных групп: {e}")

    async def _load_api_token(self):
        """Загрузка API токена"""
        try:
            if os.path.exists(API_TOKEN_FILE):
                with open(API_TOKEN_FILE, "r") as f:
                    self.api_token = f.read().strip()
        except Exception as e:
            print(f"Ошибка загрузки API токена: {e}")

    async def save_allowed_users(self):
        """Сохранение списка разрешенных пользователей"""
        try:
            with open(ALLOWED_USERS_FILE, "w") as f:
                f.write("\n".join(str(uid) for uid in self.allowed_users))
        except Exception as e:
            print(f"Ошибка сохранения разрешенных пользователей: {e}")

    async def save_allowed_groups(self):
        """Сохранение списка разрешенных групп"""
        try:
            with open(ALLOWED_GROUPS_FILE, "w") as f:
                f.write("\n".join(str(gid) for gid in self.allowed_groups))
        except Exception as e:
            print(f"Ошибка сохранения разрешенных групп: {e}")

    async def save_api_token(self, token: str):
        """Сохранение API токена"""
        try:
            self.api_token = token
            with open(API_TOKEN_FILE, "w") as f:
                f.write(token)
        except Exception as e:
            print(f"Ошибка сохранения API токена: {e}")

    def is_admin(self, user_id: int) -> bool:
        """Проверка является ли пользователь администратором"""
        return user_id == ADMIN_USER_ID

    def is_user_allowed(self, user_id: int) -> bool:
        """Проверка разрешен ли пользователь"""
        return self.is_admin(user_id) or user_id in self.allowed_users

    def is_group_allowed(self, chat_id: int) -> bool:
        """Проверка разрешена ли группа"""
        return chat_id in self.allowed_groups

    def can_use_bot(self, user_id: int, chat_id: int) -> bool:
        """Проверка может ли пользователь использовать бота в данном чате"""
        # Админ может использовать везде
        if self.is_admin(user_id):
            return True

        # В приватном чате - проверяем только пользователя
        if chat_id > 0:
            return self.is_user_allowed(user_id)

        # В группе - проверяем и пользователя и группу
        return self.is_group_allowed(chat_id)

    async def add_user(self, user_id: int):
        """Добавление пользователя в разрешенные"""
        self.allowed_users.add(user_id)
        await self.save_allowed_users()

    async def remove_user(self, user_id: int):
        """Удаление пользователя из разрешенных"""
        self.allowed_users.discard(user_id)
        await self.save_allowed_users()

    async def add_group(self, chat_id: int):
        """Добавление группы в разрешенные"""
        self.allowed_groups.add(chat_id)
        await self.save_allowed_groups()

    async def remove_group(self, chat_id: int):
        """Удаление группы из разрешенных"""
        self.allowed_groups.discard(chat_id)
        await self.save_allowed_groups()

    def get_api_token(self) -> str:
        """Получение API токена"""
        return self.api_token

    def get_allowed_users(self) -> List[int]:
        """Получение списка разрешенных пользователей"""
        return list(self.allowed_users)

    def get_allowed_groups(self) -> List[int]:
        """Получение списка разрешенных групп"""
        return list(self.allowed_groups)


auth_manager = AuthManager()
