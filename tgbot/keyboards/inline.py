from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

yes_no_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='Да', callback_data='yes'),
        InlineKeyboardButton(text='Нет', callback_data='no')
    ]
])

initial_payments = ['2.000-5.000',
                    'от 5.000',
                    'от 10.000',
                    'более 10.000']

budgets = ['до 10.000',
           'до 20.000',
           'до 30.000',
           'более 30.000']


def initial_payment_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for amount in initial_payments:
        builder.add(InlineKeyboardButton(text=amount,
                                         callback_data=f'initial_payment:{amount}'))
    builder.adjust(2)
    return builder.as_markup()


def budget_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for amount in budgets:
        builder.add(InlineKeyboardButton(text=amount,
                                         callback_data=f'budget:{amount}'))
    builder.adjust(2)
    return builder.as_markup()
