from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from telegram import markups
from database.controllers import message_controller
from config import bot_config


class EditState(StatesGroup):
    wait_edit_text = State()


class AdminPanel:
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    async def edit_bot_messages(call: types.CallbackQuery, state: FSMContext):
        """Add post content"""
        await state.finish()
        keyboard = markups.get_bot_messages_menu()
        await call.message.answer('Выбери текст для редактирования', reply_markup=keyboard)

    @staticmethod
    async def edit_greeting_msg(call: types.CallbackQuery, state: FSMContext):
        await call.message.answer('Введи новый текст сообщения:')
        await state.update_data(target_msg=call.data)
        await state.set_state(EditState.wait_edit_text.state)

    @staticmethod
    async def edit_book_add_msg(call: types.CallbackQuery, state: FSMContext):
        await call.message.answer('Введи новый текст сообщения:')
        await state.update_data(target_msg=call.data)
        await state.set_state(EditState.wait_edit_text.state)

    @staticmethod
    async def edit_book_format_err_msg(call: types.CallbackQuery, state: FSMContext):
        await call.message.answer('Введи новый текст сообщения:')
        await state.update_data(target_msg=call.data)
        await state.set_state(EditState.wait_edit_text.state)

    @staticmethod
    async def edit_first_book_msg(call: types.CallbackQuery, state: FSMContext):
        await call.message.answer('Введи новый текст сообщения:')
        await state.update_data(target_msg=call.data)
        await state.set_state(EditState.wait_edit_text.state)

    @staticmethod
    async def edit_same_book_msg(call: types.CallbackQuery, state: FSMContext):
        await call.message.answer('Введи новый текст сообщения:')
        await state.update_data(target_msg=call.data)
        await state.set_state(EditState.wait_edit_text.state)

    @staticmethod
    async def edit_reeding_complete_msg(call: types.CallbackQuery, state: FSMContext):
        await call.message.answer('Введи новый текст сообщения:')
        await state.update_data(target_msg=call.data)
        await state.set_state(EditState.wait_edit_text.state)

    @staticmethod
    async def accept_edit_text(message: types.Message, state: FSMContext):
        user_data = await state.get_data()
        target_msg = user_data.get('target_msg')
        messages = message_controller.db_read_messages()
        if target_msg == 'GREETING_MSG':
            message_controller.db_update_message_table({'greeting_msg': message.text})
            bot_config.GREETING_MSG = messages.greeting_msg

        elif target_msg == 'ADD_BOOK_MSG':
            message_controller.db_update_message_table({'add_book_msg': message.text})
            bot_config.ADD_BOOK_MSG = messages.add_book_msg

        elif target_msg == 'BOOK_FORMAT_ERR_MSG':
            message_controller.db_update_message_table({'book_format_err_msg': message.text})
            bot_config.BOOK_FORMAT_ERR_MSG = messages.book_format_err_msg

        elif target_msg == 'FIRST_BOOK_MSG':
            message_controller.db_update_message_table({'first_book_msg': message.text})
            bot_config.FIRST_BOOK_MSG = messages.first_book_msg

        elif target_msg == 'SAME_BOOK_MSG':
            message_controller.db_update_message_table({'same_book_msg': message.text})
            bot_config.SAME_BOOK_MSG = messages.same_book_msg

        elif target_msg == 'REEDING_COMPLETE_MSG':
            message_controller.db_update_message_table({'reeding_complete_msg': message.text})
            bot_config.REEDING_COMPLETE_MSG = messages.reeding_complete_msg

        await message.answer('👌 Новый текст для выбранного сообщения успещно принят')

    def register_handlers(self, dp: Dispatcher):
        """Register handlers"""
        dp.register_callback_query_handler(self.edit_bot_messages, text='edit_bot_messages', state='*')
        dp.register_callback_query_handler(self.edit_greeting_msg, text='GREETING_MSG', state='*')
        dp.register_callback_query_handler(self.edit_book_add_msg, text='ADD_BOOK_MSG')
        dp.register_callback_query_handler(self.edit_book_format_err_msg, text='BOOK_FORMAT_ERR_MSG')
        dp.register_callback_query_handler(self.edit_first_book_msg, text='FIRST_BOOK_MSG')
        dp.register_callback_query_handler(self.edit_same_book_msg, text='SAME_BOOK_MSG')
        dp.register_callback_query_handler(self.edit_reeding_complete_msg, text='REEDING_COMPLETE_MSG')
        dp.register_message_handler(self.accept_edit_text, content_types='text', state=EditState.wait_edit_text)
