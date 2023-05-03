from aiogram.fsm.state import StatesGroup, State


class QuestionsState(StatesGroup):
    Q1 = State()
    Q2 = State()

    Q3 = State()
    waiting_initial_payment = State()
    waiting_budget = State()

    waiting_phone = State()