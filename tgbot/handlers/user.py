from datetime import datetime

import pytz as pytz
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from tgbot.config import Config
from tgbot.keyboards.inline import yes_no_keyboard, initial_payment_keyboard, budget_keyboard
from tgbot.misc.states import QuestionsState
from tgbot.services.google_sheets import write_to_sheet

user_router = Router()
user_router.message.filter(F.chat.type == "private")
user_router.callback_query.filter(F.message.chat.type == 'private')


@user_router.message(CommandStart(), flags={'throttling_key': 'default'})
async def user_start(message: Message, state: FSMContext):
    await state.clear()
    text = (
        '<code>Здравствуйте! Ответьте всего на 5 вопросов, чтобы мы могли понять, '
        'какие автомобили мы сможем Вам предложить</code>\n\n'

        '1. Какие марки авто Вы рассматриваете к покупке?\n'
        '<code>Напишите марки автомобилей, которые Вам нравятся</code>')
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(QuestionsState.Q1)


@user_router.message(QuestionsState.Q1, F.text)
async def process_answer1(message: Message, state: FSMContext):
    answer = message.text.strip()
    if len(answer) > 100:
        await message.answer('<b>Текст должен быть не длиннее 100 символов!</b>')
        return
    await message.answer(text='<b>2. Есть ли у Вас SSN?</b>\n'
                              '<code>Не переживайте - мы оформляем авто даже без SSN</code>',
                         reply_markup=yes_no_keyboard)

    await state.set_state(QuestionsState.Q2)
    await state.update_data(car_brands=answer)


@user_router.callback_query(QuestionsState.Q2, F.data.in_(['yes', 'no']))
async def process_answer2(call: CallbackQuery, state: FSMContext):
    data = call.data
    if data == 'yes':
        using_ssn = True
    elif data == 'no':
        using_ssn = False
    else:
        await call.answer('<b>Выберите "Да" или "Нет"</b>')
        return

    await state.set_state(QuestionsState.Q3)
    await state.update_data(using_ssn=using_ssn)
    await call.message.edit_text(text='<b>3. Будете ли Вы брать авто-кредит?</b>',
                                 reply_markup=yes_no_keyboard)


@user_router.callback_query(QuestionsState.Q3, F.data.in_(['yes', 'no']))
async def process_answer3(call: CallbackQuery, state: FSMContext):
    data = call.data
    if data == 'yes''':
        credit = True
        await call.message.edit_text(text='<b>4. Какой будет первоначальный взнос?</b>',
                                     reply_markup=initial_payment_keyboard())
        await state.set_state(QuestionsState.waiting_initial_payment)
    elif data == 'no':
        credit = False
        await call.message.edit_text(text='<b>4. Какой бюджет закладываете на покупку?</b>',
                                     reply_markup=budget_keyboard())
        await state.set_state(QuestionsState.waiting_budget)

    else:
        await call.answer('<b>Выберите "Да" или "Нет"</b>')
        return
    # await call.message.delete_reply_markup()
    await state.update_data(credit=credit)


@user_router.callback_query(QuestionsState.waiting_initial_payment, F.data.startswith('initial_payment:'))
async def process_initial_payment(call: CallbackQuery, state: FSMContext):
    data = call.data.split(':')
    answer = data[1]
    await state.set_state(QuestionsState.waiting_phone)
    await state.update_data(initial_payment=answer)
    await call.message.edit_text('<b>5. ВВЕДИТЕ ВАШ НОМЕР ТЕЛЕФОНА</b>\n'
                                 '<code>Мы скинем по SMS наш сайт, доступные вам варианты и'
                                 ' назначим Вам личного менеджера</code>')


@user_router.callback_query(QuestionsState.waiting_budget, F.data.startswith('budget:'))
async def process_initial_payment(call: CallbackQuery, state: FSMContext):
    data = call.data.split(':')
    answer = data[1]

    await state.set_state(QuestionsState.waiting_phone)
    await state.update_data(budget=answer)
    await call.message.edit_text('<b>5. ВВЕДИТЕ ВАШ НОМЕР ТЕЛЕФОНА</b>\n'
                                 '<code>Мы скинем по SMS наш сайт, доступные вам варианты и'
                                 ' назначим Вам личного менеджера</code>')


@user_router.message(QuestionsState.waiting_phone, F.text.regexp(r'\d+', search=True))
async def process_phone_number(message: Message, state: FSMContext, config: Config):
    username = message.from_user.username if message.from_user.username else '-'
    phone = message.text.strip()

    if len(phone) > 21:
        await message.answer('<b>Номер телефона должен быть не длиннее 21 символа</b>')
        return

    data = await state.get_data()
    car_brands = data.get('car_brands')
    using_ssn = data.get('using_ssn')
    using_ssn = 'Есть' if using_ssn else 'Нет'
    credit = data.get('credit')
    credit = 'В кредит' if credit else 'Наличными'
    initial_payment = data.get('initial_payment', '-')
    budget = data.get('budget', '-')

    tz = pytz.timezone('America/Los_Angeles')
    date_time = datetime.now(tz=tz)
    date = date_time.date().strftime('%d.%m.%Y')
    time = date_time.time().strftime('%H:%M')

    try:
        google_client_manager = config.misc.google_client_manager
        google_client = await google_client_manager.authorize()
        sheet_key = config.misc.google_sheet_key
        spreadsheet = await google_client.open_by_key(sheet_key)
        worksheet = await spreadsheet.worksheet('Prime')
        await write_to_sheet(worksheet, date, time, username, phone, car_brands, using_ssn, credit, initial_payment,
                             budget)
    except Exception as e:
        print(e)
    else:
        await message.answer(
            '<b>Ваша заявка была принята.</b>\n'
            'Я Денис - Ваш личный менеджер, позвоню Вам в ближайшее время и скину всю информацию по Вашему запросу.')
    finally:
        await state.clear()


@user_router.message(QuestionsState.waiting_phone)
async def process_wrong_phone_number(message: Message):
    await message.answer('<b>Вы ввели некорректный номер телефона. Он должен содержать в себе цифры.\n'
                         'Попробуйте снова.</b>')
