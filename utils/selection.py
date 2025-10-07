import json
import os
from typing import Optional, Dict
from config.settings import SELECTED_TASKS_FILE, DATA_DIR


class SelectionManager:
    """Manage per-user selected task stored in a JSON file.

    Structure:
    {
        "<user_id>": {
            "task_id": 123,
            "subject": "математика",
            "name": "Задание 1",
        },
        ...
    }
    """

    def __init__(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        self.path = SELECTED_TASKS_FILE
        self._data: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
        except Exception:
            self._data = {}

    def _save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def set_selection(self, user_id: int, task: Dict):
        self._data[str(user_id)] = {
            "task_id": task.get("id"),
            "subject": task.get("subject"),
            "name": task.get("name"),
        }
        self._save()

    def get_selection(self, user_id: int) -> Optional[Dict]:
        return self._data.get(str(user_id))

    def clear_selection(self, user_id: int):
        if str(user_id) in self._data:
            del self._data[str(user_id)]
            self._save()


selection_manager = SelectionManager()
