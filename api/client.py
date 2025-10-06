import aiohttp
import logging
from typing import Optional, List, Dict
from config.settings import IS57_API_BASE_URL

logger = logging.getLogger(__name__)


class IS57APIClient:
    """Клиент для работы с API is57.ru"""

    def __init__(self):
        self.base_url = IS57_API_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получение или создание HTTP сессии"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """Закрытие HTTP сессии"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _make_request(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Выполнение HTTP запроса к API"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}{endpoint}"

            async with session.get(url, params=params) as response:
                if response.status == 200:
                    if response.content_type == "application/json":
                        return await response.json()
                    else:
                        text = await response.text()
                        if text == "invalid token":
                            return {"error": "invalid token"}
                        return {"result": text}
                else:
                    logger.error(f"API request failed: {response.status}")
                    return None

        except Exception as e:
            logger.error(f"API request error: {e}")
            return None

    async def get_teams(self) -> List[Dict]:
        """Получение списка команд"""
        result = await self._make_request("/teams")
        return result if result else []

    async def get_tasks(self) -> List[Dict]:
        """Получение списка заданий"""
        result = await self._make_request("/tasks")
        return result if result else []

    async def get_results(self) -> Dict:
        """Получение результатов команд"""
        result = await self._make_request("/results")
        return result if result else {}

    async def add_team(self, token: str, building: int, name: str) -> bool:
        """Добавление новой команды"""
        params = {"token": token, "building": building, "name": name}
        result = await self._make_request("/teams/add", params)
        return result is not None and result.get("error") != "invalid token"

    async def remove_team(self, token: str, team_id: int) -> bool:
        """Удаление команды"""
        params = {"token": token, "id": team_id}
        result = await self._make_request("/teams/del", params)
        return result is not None and result.get("error") != "invalid token"

    async def add_task(self, token: str, subject: str, name: str) -> bool:
        """Добавление нового задания"""
        params = {"token": token, "subject": subject, "name": name}
        result = await self._make_request("/tasks/add", params)
        return result is not None and result.get("error") != "invalid token"

    async def remove_task(self, token: str, task_id: int) -> bool:
        """Удаление задания"""
        params = {"token": token, "id": task_id}
        result = await self._make_request("/tasks/del", params)
        return result is not None and result.get("error") != "invalid token"

    async def set_result(
        self, token: str, team_id: int, task_id: int, value: int
    ) -> bool:
        """Установка результата команды для задания"""
        params = {
            "token": token,
            "team_id": team_id,
            "task_id": task_id,
            "value": value,
        }
        result = await self._make_request("/results/set", params)
        return result is not None and result.get("error") != "invalid token"

    async def set_date(self, token: str, value: str) -> bool:
        """Установка даты"""
        params = {"token": token, "value": value}
        result = await self._make_request("/date/set", params)
        return result is not None and result.get("error") != "invalid token"

    def find_team_by_name(
        self, teams: List[Dict], name: str
    ) -> Optional[Dict]:
        """Поиск команды по имени и зданию"""
        for team in teams:
            if team.get("name") == name:
                return team
        return None

    def find_task_by_name_and_subject(
        self, tasks: List[Dict], name: str, subject: str
    ) -> Optional[Dict]:
        """Поиск задания по имени и предмету"""
        for task in tasks:
            if task.get("name") == name and task.get("subject") == subject:
                return task
        return None

    def get_team_result(
        self, results: Dict, team_id: int, task_id: int
    ) -> int:
        """Получение результата команды для конкретного задания"""
        if str(team_id) in results:
            team_results = results[str(team_id)].get("results", [])
            for result in team_results:
                if result.get("taskInfo", {}).get("id") == task_id:
                    return result.get("result", 0)
        return 0


# Глобальный экземпляр API клиента
api_client = IS57APIClient()
