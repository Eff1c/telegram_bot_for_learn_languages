from typing import List

from decouple import config
from pymongo import MongoClient, errors

client = MongoClient(config("MONGODB_URL"))

db = client.learn_english

words_column = db.words


def add_word(
    word: str,
    translation: List[str],
    number_of_correct_answers_from: int = 0,
    number_of_correct_answers_to: int = 0
) -> str:
    try:
        words_column.insert_one(
            {
                "word": word,
                "translation": translation,
                "number_of_correct_answers_from": number_of_correct_answers_from,
                "number_of_correct_answers_to": number_of_correct_answers_to
            }
        )
        return "Successful!"
    except errors.DuplicateKeyError:
        return "Not unique word!"


def update_number_of_correct_answers(word: str, field: str, increase: bool):
    query = {"word": word}
    quantity = 1 if increase else -1

    words_column.update(
        query,
        {
            "$inc": {field: quantity}
        }
    )


def check_translation(word_dict: dict, input_: str, answer_from: bool) -> bool:
    respond = False

    # if translate from learning language
    if answer_from:
        field = "number_of_correct_answers_from"
        if input_ in word_dict["translation"]:
            update_number_of_correct_answers(
                word_dict["word"], field, True
            )
            respond = True

        elif word_dict[field] > 0:
            update_number_of_correct_answers(
                word_dict["word"], field, False
            )

    # if translate to learning language
    else:
        field = "number_of_correct_answers_to"
        if input_ == word_dict["word"]:
            update_number_of_correct_answers(
                word_dict["word"], field, True
            )
            respond = True

        elif word_dict[field] > 0:
            update_number_of_correct_answers(
                word_dict["word"], field, False
            )

    return respond


def get_random_word(current_word: str) -> dict:
    return words_column.aggregate(
        [{
            "$sample": {"size": 1}
        }]
    ).next()

