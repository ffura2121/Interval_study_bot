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

#============ Клас для додавання слів ============
#============ async def add_word ============

class AddWord(StatesGroup):
    word = State()
    translate = State()

#============ Клас для повторення слів ============
#============ async def process_remind_word ============

class RemindWord(StatesGroup):
    waiting_answer = State()
    

#============ Список з об'єктами Theme ============
#============ Довелось винести бо був циклічний імопрт і не працювала kb ============
list_themes = [Theme("IT")]