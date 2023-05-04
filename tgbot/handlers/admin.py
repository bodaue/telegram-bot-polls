from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from tgbot.config import Config
from tgbot.filters.admin import AdminFilter
from tgbot.services.google_sheets import create_spreadsheet, add_worksheet, share_spreadsheet

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(Command(commands='create_spreadsheet'))
async def create_spreadsheet_admin(message: Message, config: Config):
    google_client_manager = config.misc.google_client_manager
    google_client = await google_client_manager.authorize()
    async_spreadsheet = await create_spreadsheet(google_client, spreadsheet_name='Название т1')
    await add_worksheet(async_spreadsheet, 'Новый лист (рабочий)')
    await share_spreadsheet(async_spreadsheet, email='timka22771@gmail.com')
    url = async_spreadsheet.ss.url

    await message.answer(f'Ваш файл находится тут: {url}')
