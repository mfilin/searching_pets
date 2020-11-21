from aiogram.dispatcher.filters.state import State, StatesGroup

class Form(StatesGroup):
    START = State()

    CHOOSING = State()
    ADDING = State()
    DELETING = State()
    RESULT = State()

