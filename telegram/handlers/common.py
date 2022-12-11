from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from telegram import markups
from database.controllers import books_controller, message_controller
from app_types import User
import datetime
from config.bot_config import ADMIN_ID


async def start_command(message: types.Message, state: FSMContext):
    if message.chat.type != 'private':  # start only in private messages
        return
    await state.finish()
    message_controller.db_init_message_table()  # init messages for bot
    user_object = User(telegram_id=message.chat.id,
                       telegram_username=message.chat.username,
                       telegram_first_name=message.chat.first_name,
                       telegram_last_name=message.chat.last_name,
                       privilege='user',
                       registration_timestamp=str(datetime.datetime.now()),
                       current_book='None')
    books_controller.db_write_users(user_object)
    keyboard = markups.get_start_menu()
    if message.chat.id == ADMIN_ID:
        keyboard = markups.show_bot_messages_menu()
    await message.answer(message_controller.db_read_messages().greeting_msg, reply_markup=keyboard)


def register_handlers(dp: Dispatcher):
    """Register message handlers"""
    dp.register_message_handler(start_command, commands="start", state='*')
