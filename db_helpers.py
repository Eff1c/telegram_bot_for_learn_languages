from typing import List, Tuple, Optional

from decouple import config
from pymongo import MongoClient, errors

MONGODB_URL = f'mongodb://{config("MONGODB_HOST")}:{config("MONGODB_PORT")}/'

client = MongoClient(MONGODB_URL)

db = client.learn_english

words_column = db.words


def first_run() -> None:
    words_column.create_index([("word", "text")], unique=True)


async def add_word(
    word: str,
    translations: List[str],
    chat_id,
    number_of_correct_answers_from: int = 0,
    number_of_correct_answers_to: int = 0
) -> Tuple[bool, str]:
    """
    Function for add a new word to the database
    :param word: word (str) for learning
    :param translations: arrays translations
    :param chat_id: chat_id for unique words for each chat
    :param number_of_correct_answers_from: `optional` point correct answers from learning languages
    :param number_of_correct_answers_to: `optional`
    :return: successful (bool) and response (str)
    """
    try:
        words_column.insert_one(
            {
                "word": word,
                "translations": translations,
                "chat_id": chat_id,
                "number_of_correct_answers_from": number_of_correct_answers_from,
                "number_of_correct_answers_to": number_of_correct_answers_to
            }
        )
        return True, "Successful!"
    except errors.DuplicateKeyError:
        return False, "Not unique word!"


async def update_number_of_correct_answers(word: str, chat_id: int, field: str, increase: bool):
    query = {
        "word": word,
        "chat_id": chat_id
    }
    quantity = 1 if increase else -1

    words_column.update_one(
        query,
        {
            "$inc": {field: quantity}
        }
    )


async def check_translation(word_dict: dict, chat_id: int, input_: str, answer_from: bool) -> bool:
    # if translate from learning language
    if answer_from:
        field_counter = "number_of_correct_answers_from"
        correct_answer = input_ in word_dict["translations"]

    # if translate to learning language
    else:
        field_counter = "number_of_correct_answers_to"
        correct_answer = input_ == word_dict["word"]

    # check > 0 because the counter must not be less than 0
    if correct_answer or word_dict[field_counter] > 0:
        await update_number_of_correct_answers(
            word_dict["word"], chat_id, field_counter, correct_answer
        )

    return correct_answer


async def get_random_word(current_word: Optional[str], chat_id: int) -> dict:
    random_word = words_column.aggregate(
        [
            {
                "$match": {
                    "chat_id": chat_id,
                    "word": {"$ne": current_word},
                    "number_of_correct_answers_from": {"$lt": 10},
                    "number_of_correct_answers_to": {"$lt": 10},
                }
            },
            {
                "$sample": {
                    "size": 1
                }
            }
        ]
    ).next()

    return random_word


async def delete_word(word: str, chat_id: int) -> Tuple[bool, str]:
    response = words_column.delete_one(
        {
            "word": word,
            "chat_id": chat_id,
        }
    )
    if response.deleted_count != 0:
        return True, "Successful!"
    else:
        return False, "Word not found!"


async def get_count_words(chat_id: int) -> int:
    return words_column.count_documents(
        {
            "chat_id": chat_id,
        }
    )
