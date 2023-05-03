from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from tgbot.keyboards.reply import yes_no_keyboard, initial_payment_keyboard, budget_keyboard, initial_payment, budget
from tgbot.misc.states import QuestionsState

user_router = Router()


@user_router.message(CommandStart())
async def user_start(message: Message, state: FSMContext):
    await state.clear()
    text = (
        'Здравствуйте! Ответьте всего на 5 вопросов, чтобы мы могли понять, '
        'какие автомобили мы сможем Вам предложить\n\n'

        '1. Какие марки авто вы рассматриваете к покупке? (Напишите марки автомобилей которые вам нравятся)')
    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    await state.set_state(QuestionsState.Q1)


@user_router.message(QuestionsState.Q1, F.text)
async def process_answer1(message: Message, state: FSMContext):
    answer = message.text.strip()
    await message.answer(text='<b>2. Есть ли у Вас SSN? (ДА/НЕТ)\n'
                              '(Не переживайте - мы оформляем авто даже без SSN)</b>',
                         reply_markup=yes_no_keyboard)

    await state.set_state(QuestionsState.Q2)
    await state.update_data(car_brands=answer)


@user_router.message(QuestionsState.Q2, F.text)
async def process_answer2(message: Message, state: FSMContext):
    answer = message.text.strip().upper()
    if answer == 'ДА':
        using_ssn = True
    elif answer == 'НЕТ':
        using_ssn = False
    else:
        await message.answer('<b>Выберите "Да" или "Нет"</b>')
        return

    await state.set_state(QuestionsState.Q3)
    await state.update_data(using_ssn=using_ssn)
    await message.answer(text='<b>3. Будете ли Вы брать авто-кредит? (ДА/НЕТ)</b>',
                         reply_markup=yes_no_keyboard)


@user_router.message(QuestionsState.Q3, F.text)
async def process_answer3(message: Message, state: FSMContext):
    answer = message.text.strip().upper()
    if answer == 'ДА':
        credit = True
        await message.answer(text='<b>4. Какой будет первоначальный взнос?</b>',
                             reply_markup=initial_payment_keyboard())
        await state.set_state(QuestionsState.waiting_initial_payment)
    elif answer == 'НЕТ':
        credit = False
        await message.answer(text='<b>4. Какой бюджет закладываете на покупку?</b>',
                             reply_markup=budget_keyboard())
        await state.set_state(QuestionsState.waiting_budget)

    else:
        await message.answer('<b>Выберите "Да" или "Нет"</b>')
        return

    await state.update_data(credit=credit)


@user_router.message(QuestionsState.waiting_initial_payment, F.text.in_(initial_payment))
async def process_initial_payment(message: Message, state: FSMContext):
    answer = message.text.strip()
    await state.set_state(QuestionsState.waiting_phone)
    await state.update_data(initial_payment=answer)
    await message.answer('<b>5. Введите Ваш номер телефона</b>',
                         reply_markup=ReplyKeyboardRemove())


@user_router.message(QuestionsState.waiting_budget, F.text.in_(budget))
async def process_initial_payment(message: Message, state: FSMContext):
    answer = message.text.strip()
    await state.set_state(QuestionsState.waiting_phone)
    await state.update_data(budget=answer)
    await message.answer('<b>5. Введите Ваш номер телефона</b>',
                         reply_markup=ReplyKeyboardRemove())


@user_router.message(QuestionsState.waiting_phone, F.text.regexp(r'\d+', search=True))
async def process_phone_number(message: Message, state: FSMContext):
    user_id = message.from_user.id
    name = message.from_user.full_name
    phone = message.text.strip()

    data = await state.get_data()
    car_brands = data.get('car_brands')
    using_ssn = data.get('using_ssn')
    credit = data.get('credit')
    await state.clear()


@user_router.message(QuestionsState.waiting_phone)
async def process_wrong_phone_number(message: Message):
    await message.answer('<b>Вы ввели некорректный номер телефона. Он должен содержать в себе цифры.\n'
                         'Попробуйте снова.</b>')
