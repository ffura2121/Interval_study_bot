from aiogram.fsm.state import StatesGroup, State

#============ Клас для створення теми ============
#============ async def create_new_theme ============

class CreateTheme(StatesGroup):
    waiting_name = State()

#============ Клас для тем ============
#============ process_theme_name ============

class Theme():

    def __init__(self, name):
        self.name = name
        self.dict_words = {}


#============ Список з об'єктами Theme ============
#============ Довелось винести бо був циклічний імопрт і не працювала kb ============
list_themes = []