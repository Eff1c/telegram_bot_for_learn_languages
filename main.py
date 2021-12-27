import logging

from aiogram import Bot, Dispatcher, executor, types
from decouple import config

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=config('BOT_TOKEN'))
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    with open("help.txt", "r", encoding="utf-8") as f:
        help_text = f.read()

    await message.reply(help_text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
