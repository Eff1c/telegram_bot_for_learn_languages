import asyncio
import logging

from aiogram import Bot, Dispatcher, types, Router
from decouple import config

from helpers import read_help_text

logging.basicConfig(level=logging.INFO)

main_router = Router()


@main_router.message(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    help_text = read_help_text("main_help.txt")

    await message.reply(help_text)


async def main():
    bot = Bot(token=config('BOT_TOKEN'), parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(main_router)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    asyncio.run(main())
