import logging

from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from decouple import config

# Configure logging
from helpers import read_help_text

logging.basicConfig(level=logging.INFO)

session = AiohttpSession()
bot = Bot(token=config('BOT_TOKEN'))
dp = Dispatcher(bot)


@dp.message(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    help_text = read_help_text("main_help.txt")

    await message.reply(help_text)


if __name__ == '__main__':
    dp.start_polling(bot, skip_updates=True)
