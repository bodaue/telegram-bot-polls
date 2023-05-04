from aiogram import Router, F

not_caught_router = Router()

not_caught_router.message.filter(F.chat.type == "private")
not_caught_router.callback_query.filter(F.message.chat.type == 'private')

#
# @not_caught_router.message()
# async def not_caught_messages(message: Message):
#     await message.answer('Для заполнения опроса отправьте команду: <b>/start</b>')
