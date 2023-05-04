import asyncio

from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto

from tgbot.config import Config
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import chat_link_keyboard

admin_router = Router()
admin_router.message.filter(AdminFilter(), F.chat.type == "private")

mediagroups = {}


@admin_router.message(Command(commands='post'))
async def new_post(message: Message, state: FSMContext):
    await message.answer('<b>Отправьте пост, который хотите отправить в группу</b>')
    await state.set_state('waiting_group_post')


@admin_router.message(StateFilter('waiting_group_post'), F.photo[-1].file_id.as_("photo_id"),
                      F.media_group_id.as_("album_id"))
async def collect_and_send_mediagroup(message: Message, bot: Bot, config: Config, photo_id: str, album_id: int,
                                      state: FSMContext, ):
    await state.clear()

    text = message.html_text
    if album_id in mediagroups:
        mediagroups[album_id]['album'].append(photo_id)
        if text:
            mediagroups[album_id]['text'] = text

        return

    mediagroups[album_id] = {'album': [photo_id]}
    if text:
        mediagroups[album_id]['text'] = text
    await asyncio.sleep(2)

    text = mediagroups[album_id].get('text')
    new_album = [InputMediaPhoto(media=file_id) for file_id in mediagroups[album_id]['album']]

    if new_album:
        new_album[-1].caption = text
        chat_id = config.tg_bot.chat_id
        await bot.send_media_group(chat_id=chat_id,
                                   media=new_album)
    del mediagroups[album_id]


@admin_router.message(StateFilter('waiting_group_post'))
async def waiting_group_post(message: Message, state: FSMContext, config: Config):
    await state.clear()

    chat_id = config.tg_bot.chat_id

    await message.copy_to(chat_id=chat_id,
                          reply_markup=chat_link_keyboard)

# @admin_router.message(Command(commands='create_spreadsheet'))
# async def create_spreadsheet_admin(message: Message, config: Config):
#     google_client_manager = config.misc.google_client_manager
#     google_client = await google_client_manager.authorize()
#     async_spreadsheet = await create_spreadsheet(google_client, spreadsheet_name='Название т1')
#     await add_worksheet(async_spreadsheet, 'Новый лист (рабочий)')
#     await share_spreadsheet(async_spreadsheet, email='timka22771@gmail.com')
#     url = async_spreadsheet.ss.url
#
#     await message.answer(f'Ваш файл находится тут: {url}')
