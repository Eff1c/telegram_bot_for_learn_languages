from aiogram import Router, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from db_helpers import check_translation
from helpers import generate_message_for_check_translate, LearnProcess

router_learn = Router()


class FormLearn(StatesGroup):
    learn_process = State()
    translate = State()


@router_learn.message(commands={"stop_learn"})
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer(
        "Ви молодець! Продовжимо пізніше 😉",
        reply_markup=ReplyKeyboardRemove(),
    )


@router_learn.message(commands={'start_learn'})
async def start_learn(message: types.Message, state: FSMContext) -> None:
    new_learn_process = LearnProcess(message.chat.id)
    await new_learn_process.set_new_current_word()

    await state.update_data(learn_process=new_learn_process)
    await state.set_state(FormLearn.translate)

    await message.answer(
        "Розпочинаємо процес навчання ✍️",
        reply_markup=ReplyKeyboardRemove(),
    )

    # send message with word for check translate
    process_message = await message.answer(
        generate_message_for_check_translate(new_learn_process),
        reply_markup=ReplyKeyboardRemove(),
    )

    new_learn_process.add_process_message(process_message)


@router_learn.message(state=FormLearn.translate)
async def check_translate(message: types.Message, state: FSMContext) -> None:
    translate = message.text
    state_data = await state.get_data()
    learn_process = state_data["learn_process"]
    learn_process.add_process_message(message)
    current_word = learn_process.current_word
    # we do not set a translation to state and loop the process
    await state.set_state(FormLearn.translate)

    successful = await check_translation(
        current_word,
        message.chat.id,
        translate,
        learn_process.answer_from
    )

    not_successful_response = f'Неправильна відповідь 🚫\n{current_word["word"]} - {" ".join(current_word["translations"])}'
    text = 'Правильна відповідь ✅' if successful else not_successful_response

    process_message = await message.answer(
        text,
        reply_markup=ReplyKeyboardRemove(),
    )
    learn_process.add_process_message(process_message)
    await learn_process.set_new_current_word()

    # send message with word for check translate
    process_message = await message.answer(
        generate_message_for_check_translate(learn_process),
        reply_markup=ReplyKeyboardRemove(),
    )
    learn_process.add_process_message(process_message)
