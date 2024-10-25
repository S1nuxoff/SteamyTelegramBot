# app/handlers/__init__.py

from aiogram import Router
from app.middlewares.last_activity import LastActivityMiddleware

from .start import start_router
from app.handlers.menus.setup_menu import setup_router
from app.handlers.menus.inspect_menu import inspect_menu_router
from app.handlers.tools.inspect_item_tools import inspect_item_tools_router
from app.handlers.menus.main_menu import main_menu_router
from app.handlers.menus.settings_menu import settings_menu_router
from app.handlers.tools.main_tools import main_tools_router

router = Router()

router.message.middleware(LastActivityMiddleware())
router.callback_query.middleware(LastActivityMiddleware())

# Include sub-routers
router.include_router(main_tools_router)
router.include_router(settings_menu_router)
router.include_router(start_router)
router.include_router(setup_router)
router.include_router(main_menu_router)
router.include_router(inspect_menu_router)
router.include_router(inspect_item_tools_router)
