# app/handlers/__init__.py

from aiogram import Router

# Import all sub-routers
from .start import start_router
from .setup import setup_router
from .inspect_menu import inspect_menu_router
from .tools import tools_router
from .main_menu import main_menu_router
from .settings import settings_menu_router

router = Router()

# Include sub-routers
router.include_router(settings_menu_router)
router.include_router(start_router)
router.include_router(setup_router)
router.include_router(main_menu_router)
router.include_router(inspect_menu_router)
router.include_router(tools_router)
