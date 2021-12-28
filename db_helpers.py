from typing import List, Tuple

from decouple import config
from pymongo import MongoClient, errors

client = MongoClient(config("MONGODB_URL"))

db = client.learn_english

words_column = db.words


def add_word(
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


def update_number_of_correct_answers(word: str, chat_id: int, field: str, increase: bool):
    query = {
        "word": word,
        "chat_id": chat_id
    }
    quantity = 1 if increase else -1

    words_column.update(
        query,
        {
            "$inc": {field: quantity}
        }
    )


def check_translation(word_dict: dict, chat_id: int, input_: str, answer_from: bool) -> bool:
    respond = False

    # if translate from learning language
    if answer_from:
        field = "number_of_correct_answers_from"
        if input_ in word_dict["translation"]:
            update_number_of_correct_answers(
                word_dict["word"], chat_id, field, True
            )
            respond = True

        elif word_dict[field] > 0:
            update_number_of_correct_answers(
                word_dict["word"], chat_id, field, False
            )

    # if translate to learning language
    else:
        field = "number_of_correct_answers_to"
        if input_ == word_dict["word"]:
            update_number_of_correct_answers(
                word_dict["word"], chat_id, field, True
            )
            respond = True

        elif word_dict[field] > 0:
            update_number_of_correct_answers(
                word_dict["word"], chat_id, field, False
            )

    return respond


def get_random_word(current_word: str, chat_id: int) -> dict:
    return words_column.aggregate(
        [{
            "$sample": {"size": 1}
        }]
    ).next()

