from random import choice as random_choice
from typing import List

from db_helpers import get_random_word


class LearnProcess:
    current_word = None
    # translate from learning language
    answer_from = True

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.counter = 0

    async def set_new_current_word(self) -> None:
        self.current_word = await get_random_word(
            None, self.chat_id
        )
        self.set_answer_from()

    def set_answer_from(self) -> None:
        self.answer_from = self.current_word["number_of_correct_answers_to"]\
                           > self.current_word["number_of_correct_answers_from"]

    def count(self) -> None:
        self.counter += 1


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
