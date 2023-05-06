from datetime import datetime

import pytz as pytz
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from tgbot.config import Config
from tgbot.misc.states import QuestionsState
from tgbot.services.google_sheets import write_to_sheet

user_router = Router()
user_router.message.filter(F.chat.type == "private")
user_router.callback_query.filter(F.message.chat.type == 'private')


@user_router.message(CommandStart(), flags={'throttling_key': 'default'})
async def user_start(message: Message, state: FSMContext):
    await state.clear()
    text = '<b>Какой у Вас вопрос?</b>'
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(QuestionsState.Q1)


@user_router.message(QuestionsState.Q1, F.text)
async def process_answer1(message: Message, state: FSMContext):
    question = message.text.strip()
    if len(question) > 200:
        await message.answer('<b>Вопрос должен быть не длиннее 200 символов!</b>')
        return

    await message.answer(text='<b>Напишите свой номер телефона. Когда я буду в офисе - позвоню Вам.</b>')
    await state.set_state(QuestionsState.Q2)
    await state.update_data(question=question)


@user_router.message(QuestionsState.Q2, F.text.regexp(r'\d+', search=True))
async def process_phone_number(message: Message, state: FSMContext, config: Config):
    username = message.from_user.username if message.from_user.username else '-'
    phone = message.text.strip()

    if len(phone) > 21:
        await message.answer('<b>Номер телефона должен быть не длиннее 21 символа</b>')
        return

    data = await state.get_data()
    question = data.get('question')

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
        await write_to_sheet(worksheet, date, time, username, phone, question)
    except Exception as e:
        print(e)
    else:
        await message.answer(
            '<b>Ваша заявка была принята.</b>\n'
            'Я Денис - Ваш личный менеджер, позвоню Вам в ближайшее время и скину всю информацию по Вашему запросу.')
    finally:
        await state.clear()


@user_router.message(QuestionsState.Q2)
async def process_wrong_phone_number(message: Message):
    await message.answer('<b>Вы ввели некорректный номер телефона. Он должен содержать в себе цифры.\n'
                         'Попробуйте снова.</b>')
