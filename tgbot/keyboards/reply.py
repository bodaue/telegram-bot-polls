from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

yes_no_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Да'),
            KeyboardButton(text='Нет')
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите ответ')

initial_payment = ['2.000-5.000$',
                   'от 5.000$',
                   'от 10.000$',
                   'более 10.000$']

budget = ['до 10.000$',
          'до 20.000$',
          'до 30.000$',
          'более 30.000$']


def initial_payment_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for amount in initial_payment:
        builder.add(KeyboardButton(text=amount))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True,
                             one_time_keyboard=True)


def budget_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for amount in budget:
        builder.add(KeyboardButton(text=amount))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True,
                             one_time_keyboard=True)
