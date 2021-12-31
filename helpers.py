import asyncio
from contextlib import suppress
from aiogram import types
from random import choice as random_choice
from typing import List

from db_helpers import get_random_word, check_count_words


class LearnProcess:
    current_word = None
    # translate from learning language
    answer_from = True
    process_messages = {
        "current_messages": [],
        "old_messages": []
    }

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.counter = 0

    def set_answer_from(self) -> None:
        self.answer_from = self.current_word["number_of_correct_answers_to"]\
                           > self.current_word["number_of_correct_answers_from"]

    def count(self) -> None:
        self.counter += 1

    async def delete_old_process_messages(self) -> None:
        process_messages = self.process_messages
        for message in process_messages["old_messages"]:
            await message.delete()

        self.process_messages["old_messages"] = process_messages["current_messages"]
        self.process_messages["current_messages"] = []

    async def set_new_current_word(self) -> None:
        self.current_word = await get_random_word(
            None, self.chat_id
        )

        self.set_answer_from()
        self.count()
        await self.delete_old_process_messages()

    def add_process_message(self, message):
        self.process_messages["current_messages"].append(message)


def read_help_text(file_name: str) -> str:
    with open(f"help_texts/{file_name}", "r", encoding="utf-8") as f:
        return f.read()


def parse_translates_from_str(text: str) -> List[str]:
    return text.strip().split(";")


def generate_message_for_check_translate(learn_process: LearnProcess) -> str:
    word = learn_process.current_word
    if learn_process.answer_from:
        return word["word"]
    else:
        return random_choice(word["translations"])


async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    await message.delete()


async def check_if_enough_words(chat_id: int) -> bool:
    count = check_count_words(chat_id)
    return count > 2
