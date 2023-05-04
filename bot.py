import asyncio
import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from tgbot.config import load_config
from tgbot.handlers.admin import admin_router
from tgbot.handlers.other_messages import not_caught_router
from tgbot.handlers.user import user_router
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.middlewares.throttling import ThrottlingMiddleware
from tgbot.misc.mongostorage import MongoStorage
from tgbot.misc.set_bot_commands import set_default_commands
from tgbot.services import broadcaster

logger = logging.getLogger(__name__)
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)


async def on_startup(bot: Bot, admin_ids: list[int]):
    await broadcaster.broadcast(bot, admin_ids, "Бот запущен!")


def register_global_middlewares(dp: Dispatcher, config):
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))
    dp.message.middleware(ThrottlingMiddleware())
    dp.callback_query.middleware(CallbackAnswerMiddleware())


def register_logger():
    logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-6s [%(asctime)s]  %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S',
                        level=log_level)
    logger.info("Starting bot")


async def main():
    register_logger()

    config = load_config(".env")
    if config.tg_bot.use_mongo_storage:
        storage = MongoStorage(uri='mongodb://127.0.0.1:27017/',
                               database='FSM_states',
                               collection_states='states')
    else:
        storage = MemoryStorage()

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(storage=storage)

    for router in [
        admin_router,
        user_router,
        not_caught_router
    ]:
        dp.include_router(router)

    register_global_middlewares(dp, config)

    await set_default_commands(bot)

    await on_startup(bot, config.tg_bot.admin_ids)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Stopping bot")
