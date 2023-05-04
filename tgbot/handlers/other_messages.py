from aiogram import Router
from aiogram.types import Message

not_caught_router = Router()


@not_caught_router.message()
async def not_caught_messages(message: Message):
    await message.answer('Для заполнения опроса отправьте команду: <b>/start</b>')
