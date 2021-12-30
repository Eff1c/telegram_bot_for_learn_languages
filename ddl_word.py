from aiogram import Router, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from helpers import read_help_text, parse_translates_from_str, delete_message
from db_helpers import add_word as add_word_to_db

router_ddl_word = Router()


class FormAddWord(StatesGroup):
    word = State()
    translates = State()


@router_ddl_word.message(commands={"cancel"})
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


@router_ddl_word.message(commands={'add'})
async def add_word(message: types.Message, state: FSMContext) -> None:
    """
    Add word for learning
    """
    await state.set_state(FormAddWord.word)

    answer = await message.answer(
        "Введіть слово яке хочете вивчити",
        reply_markup=ReplyKeyboardRemove(),
    )

    await delete_message(message, 25)
    await delete_message(answer, 25)


@router_ddl_word.message(state=FormAddWord.word)
async def process_word(message: types.Message, state: FSMContext) -> None:
    await state.update_data(word=message.text)
    await state.set_state(FormAddWord.translates)

    help_text = read_help_text("add_translations_help.txt")

    answer = await message.answer(help_text)

    await delete_message(message, 20)
    await delete_message(answer, 20)


@router_ddl_word.message(state=FormAddWord.translates)
async def process_gender(message: types.Message, state: FSMContext) -> None:
    data = await state.update_data(
        translates=parse_translates_from_str(message.text)
    )
    await state.clear()

    successful, response = await add_word_to_db(
        data['word'], data['translates'], message.chat.id
    )

    text = 'Чудово, ви додали нове слово 😊' if successful else f'Помилка: {response}'

    answer = await message.answer(
        text,
        reply_markup=ReplyKeyboardRemove(),
    )

    await delete_message(message, 15)
    await delete_message(answer, 15)
