from .basic import router as basic_router
from .admin import router as admin_router
from .tasks import router as tasks_router

# Список всех роутеров для регистрации в main.py
routers = [basic_router, admin_router, tasks_router]

__all__ = ["routers"]
