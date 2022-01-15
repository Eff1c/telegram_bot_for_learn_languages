from aiogram import Router, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from config import create_logger
from helpers import read_help_text, parse_translates_from_str, delete_message
from db_helpers import add_word as add_word_to_db, delete_word as db_delete_word

router_ddl_word = Router()

logger = create_logger(__name__)


class FormAddWord(StatesGroup):
    word = State()
    translates = State()


class FormDeleteWord(StatesGroup):
    word = State()


@router_ddl_word.message(commands={"cancel"})
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    logger.debug("run cancel_handler")
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
    logger.debug("run add_word")
    await state.set_state(FormAddWord.word)

    answer = await message.answer(
        "Введіть слово яке хочете вивчити",
        reply_markup=ReplyKeyboardRemove(),
    )

    await delete_message(message, 25)
    await delete_message(answer, 25)


@router_ddl_word.message(state=FormAddWord.word)
async def process_word(message: types.Message, state: FSMContext) -> None:
    logger.debug("run process_word")
    await state.update_data(word=message.text.lower())
    await state.set_state(FormAddWord.translates)

    help_text = read_help_text("add_translations_help.txt")

    answer = await message.answer(help_text)

    await delete_message(message, 20)
    await delete_message(answer, 20)


@router_ddl_word.message(state=FormAddWord.translates)
async def process_translates(message: types.Message, state: FSMContext) -> None:
    logger.debug("run process_translates")
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


@router_ddl_word.message(commands={'remove', 'delete'})
async def delete_word(message: types.Message, state: FSMContext) -> None:
    logger.debug("run delete_word")
    await state.set_state(FormDeleteWord.word)

    answer = await message.answer(
        "Введіть слово яке хочете видалити",
        reply_markup=ReplyKeyboardRemove(),
    )

    await delete_message(message, 20)
    await delete_message(answer, 20)


@router_ddl_word.message(state=FormDeleteWord.word)
async def delete_word_finish(message: types.Message, state: FSMContext) -> None:
    await state.clear()
    logger.debug("run delete_word_finish")
    successful, response = await db_delete_word(
        message.text.lower(), message.chat.id
    )

    text = 'Слово видалено успішно ✅' if successful else f'Помилка: {response}'

    answer = await message.answer(
        text,
        reply_markup=ReplyKeyboardRemove(),
    )

    await delete_message(message, 20)
    await delete_message(answer, 20)
