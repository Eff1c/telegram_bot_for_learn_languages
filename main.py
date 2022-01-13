import asyncio

from aiogram import Bot, Dispatcher, types, Router
from decouple import config

from config import create_logger
from helpers import read_help_text, before_run
from ddl_word import router_ddl_word
from learn_word import router_learn

main_router = Router()

logger = create_logger(__name__)


@main_router.message(commands=['start', 'help'])
async def help_handler(message: types.Message):
    help_text = read_help_text("main_help.txt")

    await message.reply(help_text)


async def main():
    logger.debug("Bot creating...")
    bot = Bot(token=config('BOT_TOKEN'), parse_mode="HTML")
    logger.debug("Bot created")
    dp = Dispatcher()
    dp.include_router(main_router)
    dp.include_router(router_ddl_word)
    dp.include_router(router_learn)
    logger.debug("All routers created")

    logger.debug("Actions before run...")
    before_run()

    logger.debug("Start polling...")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
