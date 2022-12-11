from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from telegram import markups, aux_funcs
from database.controllers import books_controller, message_controller
from config.bot_config import EPUB_FOLDER
import vars_global


class SendingState(StatesGroup):
    wait_send_text = State()
    wait_next_part = State()
    wait_prev_part = State()


class SetPost:
    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    def check_auth(decorated_func):
        """Auth decorator"""

        def inner(*args, **kwargs):
            decorated_func(*args, **kwargs)

        return inner

    @staticmethod
    async def add_book(call: types.CallbackQuery, state: FSMContext):
        """Add post content"""
        await state.finish()
        await call.message.answer(message_controller.db_read_messages().add_book_msg)
        await state.set_state(SendingState.wait_send_text.state)

    @staticmethod
    async def add_book_command(message: types.Message, state: FSMContext):
        """Add post content"""
        await state.finish()
        await message.answer(message_controller.db_read_messages().add_book_msg)
        await state.set_state(SendingState.wait_send_text.state)

    async def get_book_text(self, message: types.Message, state: FSMContext):
        if '.epub' not in message.document.file_name:
            await message.answer(message_controller.db_read_messages().book_format_err_msg)
            return
        filepath = f'{EPUB_FOLDER}{message.document.file_name}'
        await self.bot.download_file_by_id(message.document.file_id, filepath)
        user_id = message.chat.id
        books_part_text = aux_funcs.init_first_book(user_id, filepath)
        vars_global.update_schedule = [True, user_id]
        if books_part_text.get('new_book'):
            await message.answer(message_controller.db_read_messages().first_book_msg)
            keyboard = markups.get_next_part_button(user_id)
        else:
            await message.answer(message_controller.db_read_messages().same_book_msg)
            keyboard = markups.get_nav_menu(user_id)
        await message.answer(books_part_text.get('books_part_text'), reply_markup=keyboard)
        await state.finish()

    @staticmethod
    async def get_books_next_part(call: types.CallbackQuery):
        """Go to next book part"""
        user_id = call.message.chat.id
        books_part_text = aux_funcs.get_target_part_text(user_id, 'inc')
        if not books_part_text:
            await call.message.edit_text(message_controller.db_read_messages().reeding_complete_msg)
            return
        keyboard = markups.get_nav_menu(user_id)
        await call.message.answer(books_part_text, reply_markup=keyboard)

    @staticmethod
    async def get_books_prev_part(call: types.CallbackQuery):
        """Go to prev book part"""
        user_id = call.message.chat.id
        books_part_text = aux_funcs.get_target_part_text(user_id, 'dec')
        if not books_part_text:
            await call.message.edit_text(message_controller.db_read_messages().reeding_complete_msg)
            return
        book_name = books_controller.db_read_user_current_book(user_id)
        prev_page = aux_funcs.get_last_part_numb(user_id, book_name)
        keyboard = markups.get_nav_menu(user_id)
        if prev_page == 1:
            keyboard = markups.get_next_part_button(user_id)
        await call.message.answer(books_part_text, reply_markup=keyboard)

    def register_handlers(self, dp: Dispatcher):
        """Register handlers"""
        dp.register_callback_query_handler(self.add_book, text='start_app',
                                           state='*')
        dp.register_message_handler(self.add_book_command, commands="select",
                                    state='*')
        dp.register_message_handler(self.get_book_text, content_types='document',
                                    state=SendingState.wait_send_text)
        dp.register_callback_query_handler(self.get_books_next_part, text='next_part',
                                           state='*')
        dp.register_callback_query_handler(self.get_books_prev_part, text='prev_part',
                                           state='*')
