from aiogram.fsm.state import State, StatesGroup


class SetupStates(StatesGroup):
    language = State()
    currency = State()
    game = State()


class SetupItemToInspect(StatesGroup):
    item_name = State()


class InspectState(StatesGroup):
    waiting_for_item = State()


class SetupItemToFloatCheck(StatesGroup):
    rungame_url = State()
